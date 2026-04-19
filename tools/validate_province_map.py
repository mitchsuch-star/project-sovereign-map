"""Map Readiness Section 4.3: offline color-map validator for commissioned art.

Plan reference: ``docs/SCALE_READINESS_PLAN.md`` Section 4.3.

Runtime checks (size match, lookup color presence at >=1 pixel) are already
enforced by Section 4.2 in ``map_renderer_base.gd::_load_map_images()``. This
tool covers the offline acceptance checks that the runtime cannot do well:

    1. Registry sentinel collision -- no province ``lookup_color`` equals
       the registry's ``no_province_color``.
    2. Registry duplicate colors -- no two provinces share a ``lookup_color``.
    3. Image dimension match -- visual + lookup PNGs agree on size.
    4. Province minimum coverage -- every declared province occupies at least
       ``min_coverage_pixels`` pixels in the lookup image (default 50).
    5. Tiny pixel islands -- any color with ``1 <= count < tiny_island_threshold``
       pixels is reported as a likely export artifact / anti-alias bleed
       (default threshold 5).
    6. Unmapped colors -- any non-sentinel color in the lookup image that is
       not declared in the registry is reported with pixel count and a
       sample ``(x, y)`` coordinate.

The runtime loader fails on the FIRST unmapped pixel; this tool collects ALL
failures so a commissioned-art delivery produces one acceptance report
instead of an iterative debug loop.

Usage::

    .venv\\Scripts\\python.exe -m tools.validate_province_map \\
        --registry godot-client/project-sovereign/assets/maps/europe.json \\
        --visual   godot-client/project-sovereign/assets/maps/europe_visual.png \\
        --lookup   godot-client/project-sovereign/assets/maps/europe_lookup.png

If only ``--registry`` is supplied, only the registry checks (#1, #2) run.
This is the cheapest acceptance gate and works before any PNG exists.

Add ``--json`` to emit a structured report on stdout for CI parsing. The
human-readable report is suppressed in JSON mode.

Exit codes::

    0   all checks passed (no errors; warnings allowed unless --strict)
    1   one or more error-severity failures
    2   bad input (missing files, malformed registry, unsupported PNG)
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

DEFAULT_MIN_COVERAGE_PIXELS = 50
DEFAULT_TINY_ISLAND_THRESHOLD = 5

ERROR = "error"
WARNING = "warning"


@dataclass
class ValidationFailure:
    """Single validator finding.

    ``code`` is a stable machine-readable identifier. ``message`` is the
    human-readable line printed in non-JSON mode. ``detail`` carries
    structured fields the CI report and downstream tools can key off.
    """

    code: str
    severity: str
    message: str
    detail: dict = field(default_factory=dict)


@dataclass
class ValidationReport:
    failures: list[ValidationFailure] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationFailure]:
        return [f for f in self.failures if f.severity == ERROR]

    @property
    def warnings(self) -> list[ValidationFailure]:
        return [f for f in self.failures if f.severity == WARNING]

    def extend(self, more: Iterable[ValidationFailure]) -> None:
        self.failures.extend(more)

    def to_dict(self) -> dict:
        return {
            "ok": not self.errors,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "failures": [asdict(f) for f in self.failures],
        }


# ---------------------------------------------------------------------------
# PNG decoding (minimal pure-Python: 8-bit RGB / RGBA, all 5 filter types).
# ---------------------------------------------------------------------------


class PNGDecodeError(Exception):
    pass


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _unfilter_scanlines(raw: bytes, width: int, height: int, bpp: int) -> bytearray:
    """Reverse the per-scanline PNG filter (types 0..4) and return raw pixels."""
    stride = width * bpp
    out = bytearray(stride * height)
    cursor = 0
    prev_row_start = -stride  # sentinel "no previous row"
    for y in range(height):
        if cursor >= len(raw):
            raise PNGDecodeError("Truncated PNG IDAT stream")
        filter_type = raw[cursor]
        cursor += 1
        row_start = y * stride
        for x in range(stride):
            byte = raw[cursor + x]
            left = out[row_start + x - bpp] if x >= bpp else 0
            up = out[prev_row_start + x] if prev_row_start >= 0 else 0
            up_left = out[prev_row_start + x - bpp] if (prev_row_start >= 0 and x >= bpp) else 0
            if filter_type == 0:
                value = byte
            elif filter_type == 1:
                value = (byte + left) & 0xFF
            elif filter_type == 2:
                value = (byte + up) & 0xFF
            elif filter_type == 3:
                value = (byte + ((left + up) >> 1)) & 0xFF
            elif filter_type == 4:
                value = (byte + _paeth(left, up, up_left)) & 0xFF
            else:
                raise PNGDecodeError(f"Unsupported PNG filter type {filter_type} on row {y}")
            out[row_start + x] = value
        cursor += stride
        prev_row_start = row_start
    return out


def read_png_pixels(path: Path) -> tuple[int, int, list[list[tuple[int, int, int]]]]:
    """Decode an 8-bit RGB or RGBA PNG into (width, height, rows of (r, g, b)).

    Alpha is dropped if present; only the RGB triple is used for color-map
    lookups. Raises :class:`PNGDecodeError` for unsupported formats.
    """
    blob = path.read_bytes()
    if not blob.startswith(PNG_SIGNATURE):
        raise PNGDecodeError(f"{path.name} is not a PNG file (missing signature)")

    cursor = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = None
    idat = bytearray()
    while cursor < len(blob):
        if cursor + 8 > len(blob):
            raise PNGDecodeError(f"{path.name}: truncated chunk header")
        length = struct.unpack(">I", blob[cursor:cursor + 4])[0]
        cursor += 4
        chunk_type = blob[cursor:cursor + 4]
        cursor += 4
        payload = blob[cursor:cursor + length]
        cursor += length
        cursor += 4  # skip CRC; trust the file
        if chunk_type == b"IHDR":
            (
                width,
                height,
                bit_depth,
                color_type,
                compression,
                filter_method,
                interlace,
            ) = struct.unpack(">IIBBBBB", payload)
            if compression != 0 or filter_method != 0:
                raise PNGDecodeError(
                    f"{path.name}: unsupported compression/filter "
                    f"({compression}/{filter_method}); expected 0/0"
                )
            if interlace != 0:
                raise PNGDecodeError(
                    f"{path.name}: interlaced PNGs are not supported by the validator"
                )
            if bit_depth != 8 or color_type not in (2, 6):
                raise PNGDecodeError(
                    f"{path.name}: unsupported bit_depth/color_type "
                    f"({bit_depth}/{color_type}); expected 8-bit RGB (2) or RGBA (6)"
                )
        elif chunk_type == b"IDAT":
            idat.extend(payload)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or color_type is None:
        raise PNGDecodeError(f"{path.name}: missing IHDR chunk")
    if not idat:
        raise PNGDecodeError(f"{path.name}: missing IDAT chunk")

    bpp = 3 if color_type == 2 else 4
    raw = zlib.decompress(bytes(idat))
    expected_len = (1 + width * bpp) * height
    if len(raw) != expected_len:
        raise PNGDecodeError(
            f"{path.name}: decompressed length {len(raw)} != expected {expected_len}"
        )

    pixel_bytes = _unfilter_scanlines(raw, width, height, bpp)
    rows: list[list[tuple[int, int, int]]] = []
    stride = width * bpp
    for y in range(height):
        row_start = y * stride
        row: list[tuple[int, int, int]] = []
        for x in range(width):
            base = row_start + x * bpp
            row.append((pixel_bytes[base], pixel_bytes[base + 1], pixel_bytes[base + 2]))
        rows.append(row)
    return width, height, rows


# ---------------------------------------------------------------------------
# Registry validation.
# ---------------------------------------------------------------------------


def _color_key(rgb: tuple[int, int, int]) -> str:
    return f"{rgb[0]},{rgb[1]},{rgb[2]}"


def _coerce_rgb(value, label: str) -> tuple[int, int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{label} must be a 3-element [r, g, b] list")
    r, g, b = value
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in (r, g, b)):
        raise ValueError(f"{label} channels must be ints in [0, 255]")
    return (int(r), int(g), int(b))


def load_registry(path: Path) -> dict:
    """Load and shallowly validate the province registry JSON.

    Raises :class:`ValueError` for structural problems so the CLI can exit
    with code 2 before running any color logic.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if "regions" not in raw or not isinstance(raw["regions"], dict):
        raise ValueError("registry missing 'regions' dict")
    if "no_province_color" not in raw:
        raise ValueError("registry missing 'no_province_color'")
    _coerce_rgb(raw["no_province_color"], "no_province_color")
    for name, entry in raw["regions"].items():
        if "lookup_color" not in entry:
            raise ValueError(f"region {name!r} missing 'lookup_color'")
        _coerce_rgb(entry["lookup_color"], f"region {name!r} lookup_color")
    return raw


def validate_registry(province_data: dict) -> list[ValidationFailure]:
    """Registry-only checks: sentinel collision + duplicate lookup colors."""
    findings: list[ValidationFailure] = []
    sentinel = tuple(province_data["no_province_color"])
    seen: dict[tuple[int, int, int], list[str]] = {}
    for name, entry in province_data["regions"].items():
        rgb = tuple(entry["lookup_color"])
        if rgb == sentinel:
            findings.append(
                ValidationFailure(
                    code="SENTINEL_COLLISION",
                    severity=ERROR,
                    message=(
                        f"Province {name!r} uses lookup_color {_color_key(rgb)} which "
                        f"equals no_province_color -- the runtime loader will reject "
                        f"this region."
                    ),
                    detail={"region": name, "color": list(rgb)},
                )
            )
        seen.setdefault(rgb, []).append(name)
    for rgb, names in seen.items():
        if len(names) > 1:
            findings.append(
                ValidationFailure(
                    code="DUPLICATE_LOOKUP_COLOR",
                    severity=ERROR,
                    message=(
                        f"Lookup color {_color_key(rgb)} is shared by "
                        f"{len(names)} regions: {sorted(names)}"
                    ),
                    detail={"color": list(rgb), "regions": sorted(names)},
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Image validation.
# ---------------------------------------------------------------------------


def _count_colors(
    rows: list[list[tuple[int, int, int]]],
) -> tuple[dict[tuple[int, int, int], int], dict[tuple[int, int, int], tuple[int, int]]]:
    """Return (counts, first_seen_xy) keyed by RGB triple."""
    counts: dict[tuple[int, int, int], int] = {}
    first_seen: dict[tuple[int, int, int], tuple[int, int]] = {}
    for y, row in enumerate(rows):
        for x, pixel in enumerate(row):
            counts[pixel] = counts.get(pixel, 0) + 1
            if pixel not in first_seen:
                first_seen[pixel] = (x, y)
    return counts, first_seen


def validate_images(
    visual_path: Path,
    lookup_path: Path,
    province_data: dict,
    *,
    min_coverage_pixels: int = DEFAULT_MIN_COVERAGE_PIXELS,
    tiny_island_threshold: int = DEFAULT_TINY_ISLAND_THRESHOLD,
) -> list[ValidationFailure]:
    """Image-side checks: dimensions, coverage, tiny islands, unmapped colors."""
    findings: list[ValidationFailure] = []
    visual_width, visual_height, _ = read_png_pixels(visual_path)
    lookup_width, lookup_height, lookup_rows = read_png_pixels(lookup_path)
    if (visual_width, visual_height) != (lookup_width, lookup_height):
        findings.append(
            ValidationFailure(
                code="SIZE_MISMATCH",
                severity=ERROR,
                message=(
                    f"Visual {visual_width}x{visual_height} != lookup "
                    f"{lookup_width}x{lookup_height}"
                ),
                detail={
                    "visual": [visual_width, visual_height],
                    "lookup": [lookup_width, lookup_height],
                },
            )
        )
        # Continue: coverage / unmapped checks still produce useful output
        # against the lookup image even when the visual is wrong.

    sentinel = tuple(province_data["no_province_color"])
    color_to_region: dict[tuple[int, int, int], str] = {
        tuple(entry["lookup_color"]): name
        for name, entry in province_data["regions"].items()
    }
    counts, first_seen = _count_colors(lookup_rows)

    # Province coverage: missing entirely vs. insufficient pixels.
    for color, region in color_to_region.items():
        pixel_count = counts.get(color, 0)
        if pixel_count == 0:
            findings.append(
                ValidationFailure(
                    code="MISSING_PROVINCE",
                    severity=ERROR,
                    message=(
                        f"Province {region!r} (color {_color_key(color)}) does not "
                        f"appear in the lookup image."
                    ),
                    detail={"region": region, "color": list(color), "pixel_count": 0},
                )
            )
        elif pixel_count < min_coverage_pixels:
            findings.append(
                ValidationFailure(
                    code="INSUFFICIENT_COVERAGE",
                    severity=ERROR,
                    message=(
                        f"Province {region!r} (color {_color_key(color)}) covers only "
                        f"{pixel_count} pixel(s) (minimum: {min_coverage_pixels})."
                    ),
                    detail={
                        "region": region,
                        "color": list(color),
                        "pixel_count": pixel_count,
                        "min_required": min_coverage_pixels,
                    },
                )
            )

    # Unmapped colors and tiny islands across the whole lookup.
    for color, count in counts.items():
        if color == sentinel:
            continue
        sample = first_seen[color]
        if color not in color_to_region:
            findings.append(
                ValidationFailure(
                    code="UNMAPPED_COLOR",
                    severity=ERROR,
                    message=(
                        f"Lookup contains undeclared color {_color_key(color)} "
                        f"({count} pixel(s); first seen at {sample[0]},{sample[1]})."
                    ),
                    detail={
                        "color": list(color),
                        "pixel_count": count,
                        "sample_xy": list(sample),
                    },
                )
            )
        if 0 < count < tiny_island_threshold:
            findings.append(
                ValidationFailure(
                    code="TINY_ISLAND",
                    severity=WARNING,
                    message=(
                        f"Color {_color_key(color)} appears as {count} pixel(s) at "
                        f"{sample[0]},{sample[1]} -- likely export artifact / "
                        f"anti-alias bleed."
                    ),
                    detail={
                        "color": list(color),
                        "pixel_count": count,
                        "sample_xy": list(sample),
                        "region": color_to_region.get(color),
                    },
                )
            )

    return findings


def validate_all(
    registry_path: Path,
    visual_path: Path | None,
    lookup_path: Path | None,
    *,
    min_coverage_pixels: int = DEFAULT_MIN_COVERAGE_PIXELS,
    tiny_island_threshold: int = DEFAULT_TINY_ISLAND_THRESHOLD,
) -> ValidationReport:
    """Run all applicable checks and return an aggregated report."""
    report = ValidationReport()
    province_data = load_registry(registry_path)
    report.extend(validate_registry(province_data))
    if visual_path is not None and lookup_path is not None:
        report.extend(
            validate_images(
                visual_path,
                lookup_path,
                province_data,
                min_coverage_pixels=min_coverage_pixels,
                tiny_island_threshold=tiny_island_threshold,
            )
        )
    return report


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _format_report(report: ValidationReport) -> str:
    lines: list[str] = []
    if not report.failures:
        lines.append("PASS: no findings.")
        return "\n".join(lines)
    for failure in report.failures:
        lines.append(f"[{failure.severity.upper()}] {failure.code}: {failure.message}")
    lines.append("")
    lines.append(
        f"Summary: {len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )
    return "\n".join(lines)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="validate_province_map",
        description="Map Readiness Section 4.3 offline color-map validator.",
    )
    parser.add_argument(
        "--registry",
        required=True,
        type=Path,
        help="Path to the province registry JSON (e.g. session8_placeholder_provinces.json).",
    )
    parser.add_argument(
        "--visual",
        type=Path,
        default=None,
        help="Path to the visual map PNG. Optional; if omitted, only registry checks run.",
    )
    parser.add_argument(
        "--lookup",
        type=Path,
        default=None,
        help="Path to the lookup color-map PNG. Required if --visual is given.",
    )
    parser.add_argument(
        "--min-coverage-pixels",
        type=int,
        default=DEFAULT_MIN_COVERAGE_PIXELS,
        help=f"Minimum pixels per declared province (default: {DEFAULT_MIN_COVERAGE_PIXELS}).",
    )
    parser.add_argument(
        "--tiny-island-threshold",
        type=int,
        default=DEFAULT_TINY_ISLAND_THRESHOLD,
        help=(
            f"Pixel-count threshold below which a color is reported as a tiny island "
            f"warning (default: {DEFAULT_TINY_ISLAND_THRESHOLD})."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable JSON report on stdout (suppresses human output).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors when computing the exit code.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])

    if (args.visual is None) != (args.lookup is None):
        print(
            "ERROR: --visual and --lookup must be provided together (or both omitted).",
            file=sys.stderr,
        )
        return 2

    if not args.registry.exists():
        print(f"ERROR: registry not found: {args.registry}", file=sys.stderr)
        return 2
    if args.visual is not None and not args.visual.exists():
        print(f"ERROR: visual PNG not found: {args.visual}", file=sys.stderr)
        return 2
    if args.lookup is not None and not args.lookup.exists():
        print(f"ERROR: lookup PNG not found: {args.lookup}", file=sys.stderr)
        return 2

    try:
        report = validate_all(
            args.registry,
            args.visual,
            args.lookup,
            min_coverage_pixels=args.min_coverage_pixels,
            tiny_island_threshold=args.tiny_island_threshold,
        )
    except (ValueError, PNGDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(_format_report(report))

    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

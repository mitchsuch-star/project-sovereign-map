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
    5. Tiny pixel islands -- each connected lookup-color island smaller than
       ``tiny_island_threshold`` pixels is reported as a likely export artifact
       / anti-alias bleed (default threshold 5).
    6. Unmapped colors -- any non-sentinel color in the lookup image that is
       not declared in the registry is reported with pixel count and a
       sample ``(x, y)`` coordinate.
    7. Adjacency unknown target (Slice 1) -- an ``adjacent`` edge points at a
       province not in the registry.
    8. Adjacency self-loop (Slice 1) -- a province lists itself as adjacent.
    9. Adjacency asymmetry (Slice 1) -- A lists B but B does not list A back.
    10. Isolated province (Slice 1, warning) -- a province with no land
        adjacency (islands, until sea links are hand-authored in Slice 2).

    The adjacency checks (7-10) run only when at least one region declares an
    ``adjacent`` list, so legacy registries without adjacency stay clean.

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
    2   bad input (missing files, malformed registry, empty registry,
        unsupported PNG)
"""
from __future__ import annotations

import argparse
from array import array
import json
import re
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


def _rgb_to_int(rgb: tuple[int, int, int]) -> int:
    return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]


def _int_to_rgb(color: int) -> tuple[int, int, int]:
    return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)


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


def _parse_png_structure(
    path: Path,
    *,
    collect_idat: bool,
) -> tuple[int, int, int, bytearray]:
    """Parse PNG structure, validating the supported validator subset."""
    blob = path.read_bytes()
    if not blob.startswith(PNG_SIGNATURE):
        raise PNGDecodeError(f"{path.name} is not a PNG file (missing signature)")

    cursor = len(PNG_SIGNATURE)
    width = height = color_type = None
    saw_ihdr = False
    saw_idat = False
    saw_iend = False
    idat = bytearray()
    while cursor < len(blob):
        if cursor + 8 > len(blob):
            raise PNGDecodeError(f"{path.name}: truncated chunk header")
        try:
            length = struct.unpack(">I", blob[cursor:cursor + 4])[0]
        except struct.error as exc:
            raise PNGDecodeError(f"{path.name}: malformed chunk length") from exc
        cursor += 4
        chunk_type = blob[cursor:cursor + 4]
        cursor += 4
        if cursor + length + 4 > len(blob):
            chunk_label = chunk_type.decode("ascii", errors="replace")
            raise PNGDecodeError(f"{path.name}: truncated {chunk_label} chunk payload")
        payload = blob[cursor:cursor + length]
        cursor += length
        cursor += 4  # skip CRC; trust the file
        if chunk_type == b"IHDR":
            if saw_ihdr:
                raise PNGDecodeError(f"{path.name}: multiple IHDR chunks are not supported")
            if length != 13:
                raise PNGDecodeError(f"{path.name}: IHDR payload must be 13 bytes (got {length})")
            try:
                (
                    width,
                    height,
                    bit_depth,
                    color_type,
                    compression,
                    filter_method,
                    interlace,
                ) = struct.unpack(">IIBBBBB", payload)
            except struct.error as exc:
                raise PNGDecodeError(f"{path.name}: malformed IHDR chunk") from exc
            saw_ihdr = True
            if width <= 0 or height <= 0:
                raise PNGDecodeError(f"{path.name}: PNG width/height must be > 0")
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
            if not saw_ihdr:
                raise PNGDecodeError(f"{path.name}: IDAT chunk appears before IHDR")
            saw_idat = True
            if collect_idat:
                idat.extend(payload)
        elif chunk_type == b"IEND":
            saw_iend = True
            break

    if not saw_ihdr or width is None or height is None or color_type is None:
        raise PNGDecodeError(f"{path.name}: missing IHDR chunk")
    if not saw_idat:
        raise PNGDecodeError(f"{path.name}: missing IDAT chunk")
    if not saw_iend:
        raise PNGDecodeError(f"{path.name}: missing IEND chunk")
    return width, height, color_type, idat


def read_png_size(path: Path) -> tuple[int, int]:
    """Read PNG dimensions without decoding the image payload."""
    width, height, _color_type, _idat = _parse_png_structure(path, collect_idat=False)
    return width, height


def read_png_rgb_bytes(path: Path) -> tuple[int, int, bytearray]:
    """Decode an 8-bit RGB/RGBA PNG into a flat RGB bytearray."""
    width, height, color_type, idat = _parse_png_structure(path, collect_idat=True)
    try:
        raw = zlib.decompress(bytes(idat))
    except zlib.error as exc:
        raise PNGDecodeError(f"{path.name}: failed to decompress IDAT stream ({exc})") from exc

    bpp = 3 if color_type == 2 else 4
    expected_len = (1 + width * bpp) * height
    if len(raw) != expected_len:
        raise PNGDecodeError(
            f"{path.name}: decompressed length {len(raw)} != expected {expected_len}"
        )

    pixel_bytes = _unfilter_scanlines(raw, width, height, bpp)
    if color_type == 2:
        return width, height, pixel_bytes

    rgb_bytes = bytearray(width * height * 3)
    read_cursor = 0
    write_cursor = 0
    for _ in range(width * height):
        rgb_bytes[write_cursor] = pixel_bytes[read_cursor]
        rgb_bytes[write_cursor + 1] = pixel_bytes[read_cursor + 1]
        rgb_bytes[write_cursor + 2] = pixel_bytes[read_cursor + 2]
        read_cursor += 4
        write_cursor += 3
    return width, height, rgb_bytes


def read_png_pixels(path: Path) -> tuple[int, int, list[list[tuple[int, int, int]]]]:
    """Decode an 8-bit RGB or RGBA PNG into (width, height, rows of (r, g, b)).

    Alpha is dropped if present; only the RGB triple is used for color-map
    lookups. Raises :class:`PNGDecodeError` for unsupported formats.
    """
    width, height, rgb_bytes = read_png_rgb_bytes(path)
    rows: list[list[tuple[int, int, int]]] = []
    stride = width * 3
    for y in range(height):
        row_start = y * stride
        row: list[tuple[int, int, int]] = []
        for x in range(width):
            base = row_start + x * 3
            row.append((rgb_bytes[base], rgb_bytes[base + 1], rgb_bytes[base + 2]))
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
    if not raw["regions"]:
        raise ValueError("registry 'regions' must not be empty")
    _coerce_rgb(raw["no_province_color"], "no_province_color")
    for name, entry in raw["regions"].items():
        if not isinstance(entry, dict):
            raise ValueError(f"region {name!r} must be an object")
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
# Adjacency validation (Slice 1).
# ---------------------------------------------------------------------------


def validate_adjacency(province_data: dict) -> list[ValidationFailure]:
    """Registry-side adjacency-graph checks (Slice 1, hardened in Slice 2).

    Runs only when at least one region declares an ``adjacent`` list, so legacy
    registries without adjacency stay clean:

      - ``ADJACENCY_UNKNOWN_TARGET`` (error): an edge points at a province not
        in the registry.
      - ``ADJACENCY_SELF_LOOP`` (error): a province lists itself as adjacent.
      - ``ADJACENCY_ASYMMETRY`` (error): A lists B but B does not list A.
      - ``ISOLATED_PROVINCE`` (warning): a province has no adjacency -- expected
        for islands until sea links are hand-authored (Slice 2).
      - ``DUPLICATE_ADJACENCY_ENTRY`` (warning, Slice-2 M5): a province lists the
        same neighbour twice.

    Slice-2 M4 -- omitted vs. empty ``adjacent``: a region whose ``adjacent``
    key is *absent* is treated as "not yet authored" and is exempt from the
    isolation warning and from being demanded as an asymmetry back-edge, so a
    mid-slice partial hand-edit does not produce a confusing error burst. Only
    an *explicit* empty list (``"adjacent": []``) is reported as isolated.
    """
    regions = province_data["regions"]
    if not any("adjacent" in entry for entry in regions.values()):
        return []

    findings: list[ValidationFailure] = []
    names = set(regions)
    authored = {name for name, entry in regions.items() if "adjacent" in entry}
    adj: dict[str, list[str]] = {
        name: list(entry.get("adjacent") or []) for name, entry in regions.items()
    }

    for name in sorted(adj):
        seen_targets: set[str] = set()
        for target in adj[name]:
            if target in seen_targets:
                findings.append(
                    ValidationFailure(
                        code="DUPLICATE_ADJACENCY_ENTRY",
                        severity=WARNING,
                        message=(
                            f"Province {name!r} lists {target!r} more than once."
                        ),
                        detail={"region": name, "target": target},
                    )
                )
                continue
            seen_targets.add(target)
            if target == name:
                findings.append(
                    ValidationFailure(
                        code="ADJACENCY_SELF_LOOP",
                        severity=ERROR,
                        message=f"Province {name!r} lists itself as adjacent.",
                        detail={"region": name},
                    )
                )
            elif target not in names:
                findings.append(
                    ValidationFailure(
                        code="ADJACENCY_UNKNOWN_TARGET",
                        severity=ERROR,
                        message=(
                            f"Province {name!r} lists adjacency to unknown "
                            f"province {target!r}."
                        ),
                        detail={"region": name, "target": target},
                    )
                )

    for name in sorted(adj):
        for target in set(adj[name]):
            if target == name or target not in names:
                continue
            # M4: only demand a back-edge from an *authored* neighbour.
            if target in authored and name not in adj.get(target, []):
                findings.append(
                    ValidationFailure(
                        code="ADJACENCY_ASYMMETRY",
                        severity=ERROR,
                        message=(
                            f"Province {name!r} lists {target!r} but {target!r} "
                            f"does not list {name!r} back."
                        ),
                        detail={"from": name, "to": target},
                    )
                )

    for name in sorted(authored):
        if not adj[name]:
            findings.append(
                ValidationFailure(
                    code="ISOLATED_PROVINCE",
                    severity=WARNING,
                    message=(
                        f"Province {name!r} has no adjacency -- island or "
                        f"awaiting Slice-2 sea links."
                    ),
                    detail={"region": name},
                )
            )

    return findings


# ---------------------------------------------------------------------------
# Gameplay-field validation (Slice 2).
# ---------------------------------------------------------------------------

# Mirror of backend.models.region.VALID_TERRAINS / VALID_REGION_TYPES. Kept
# inline so this tool stays stdlib-only and importable without the backend.
VALID_TERRAINS = {"plains", "forest", "urban", "mountains", "hills", "river_crossing"}
VALID_REGION_TYPES = {"city", "town", "rural", "capital", "major_city"}
_PLACEHOLDER_NAME = re.compile(r"^Region_\d+$")


def validate_gameplay_fields(province_data: dict) -> list[ValidationFailure]:
    """Slice-2 registry data checks for the authored gameplay fields.

    Runs only when at least one region declares ``starting_controller`` -- so
    the Slice-1 / placeholder registries (render fields only) stay clean.

      - ``MISSING_GAMEPLAY_FIELD`` (error): a required authored field is absent.
      - ``PLACEHOLDER_NAME`` (error): a province still carries its ``Region_NNN``
        placeholder name.
      - ``DUPLICATE_PROVINCE_NAME`` (error): two provinces share a ``name``.
      - ``INVALID_TERRAIN`` / ``INVALID_REGION_TYPE`` (error): value outside the
        canonical set.
      - ``NATION_MISSING_CAPITAL`` / ``NATION_MULTIPLE_CAPITALS`` (error): every
        nation that owns provinces must have exactly one ``is_capital`` province.
      - ``INLAND_SEA_EDGE`` (error, G3): a non-coastal province is an endpoint of
        a hand-authored ``sea_links`` crossing.
    """
    regions = province_data["regions"]
    if not any("starting_controller" in entry for entry in regions.values()):
        return []

    findings: list[ValidationFailure] = []
    required = ("name", "starting_controller", "terrain", "region_type",
                "is_coastal", "is_capital")
    seen_names: dict[str, str] = {}
    capitals: dict[str, list[str]] = {}
    owners: set[str] = set()

    for name in sorted(regions):
        entry = regions[name]
        for field_name in required:
            if field_name not in entry:
                findings.append(
                    ValidationFailure(
                        code="MISSING_GAMEPLAY_FIELD",
                        severity=ERROR,
                        message=f"Province {name!r} is missing '{field_name}'.",
                        detail={"region": name, "field": field_name},
                    )
                )
        prov_name = entry.get("name")
        if isinstance(prov_name, str):
            if _PLACEHOLDER_NAME.match(prov_name):
                findings.append(
                    ValidationFailure(
                        code="PLACEHOLDER_NAME",
                        severity=ERROR,
                        message=f"Province {name!r} still has placeholder name {prov_name!r}.",
                        detail={"region": name, "name": prov_name},
                    )
                )
            elif prov_name in seen_names:
                findings.append(
                    ValidationFailure(
                        code="DUPLICATE_PROVINCE_NAME",
                        severity=ERROR,
                        message=(
                            f"Province name {prov_name!r} is shared by "
                            f"{seen_names[prov_name]!r} and {name!r}."
                        ),
                        detail={"name": prov_name,
                                "regions": [seen_names[prov_name], name]},
                    )
                )
            else:
                seen_names[prov_name] = name
        terrain = entry.get("terrain")
        if terrain is not None and terrain not in VALID_TERRAINS:
            findings.append(
                ValidationFailure(
                    code="INVALID_TERRAIN",
                    severity=ERROR,
                    message=f"Province {name!r} has invalid terrain {terrain!r}.",
                    detail={"region": name, "terrain": terrain},
                )
            )
        rtype = entry.get("region_type")
        if rtype is not None and rtype not in VALID_REGION_TYPES:
            findings.append(
                ValidationFailure(
                    code="INVALID_REGION_TYPE",
                    severity=ERROR,
                    message=f"Province {name!r} has invalid region_type {rtype!r}.",
                    detail={"region": name, "region_type": rtype},
                )
            )
        controller = entry.get("starting_controller")
        if controller:
            owners.add(controller)
            if entry.get("is_capital"):
                capitals.setdefault(controller, []).append(name)

    for nation in sorted(owners):
        caps = capitals.get(nation, [])
        if not caps:
            findings.append(
                ValidationFailure(
                    code="NATION_MISSING_CAPITAL",
                    severity=ERROR,
                    message=f"Nation {nation!r} owns provinces but has no capital.",
                    detail={"nation": nation},
                )
            )
        elif len(caps) > 1:
            findings.append(
                ValidationFailure(
                    code="NATION_MULTIPLE_CAPITALS",
                    severity=ERROR,
                    message=(
                        f"Nation {nation!r} has {len(caps)} capitals: {sorted(caps)}."
                    ),
                    detail={"nation": nation, "regions": sorted(caps)},
                )
            )

    # G3: sea-link endpoints must be coastal.
    for pair in province_data.get("sea_links", []):
        for idx in pair:
            key = f"Region_{idx:03d}" if isinstance(idx, int) else idx
            entry = regions.get(key)
            if entry is not None and entry.get("is_coastal") is False:
                findings.append(
                    ValidationFailure(
                        code="INLAND_SEA_EDGE",
                        severity=ERROR,
                        message=(
                            f"Province {key!r} is not coastal but is a sea-link "
                            f"endpoint {pair}."
                        ),
                        detail={"region": key, "sea_link": list(pair)},
                    )
                )

    return findings


# ---------------------------------------------------------------------------
# Image validation.
# ---------------------------------------------------------------------------


def _count_color_keys(
    rgb_bytes: bytearray,
    width: int,
) -> tuple[dict[int, int], dict[int, tuple[int, int]], array]:
    """Return (counts, first_seen_xy, flat color-key array) keyed by RGB int."""
    counts: dict[int, int] = {}
    first_seen: dict[int, tuple[int, int]] = {}
    color_keys = array("I")
    append_color_key = color_keys.append
    x = 0
    y = 0
    for base in range(0, len(rgb_bytes), 3):
        color_key = (
            (rgb_bytes[base] << 16)
            | (rgb_bytes[base + 1] << 8)
            | rgb_bytes[base + 2]
        )
        append_color_key(color_key)
        counts[color_key] = counts.get(color_key, 0) + 1
        if color_key not in first_seen:
            first_seen[color_key] = (x, y)
        x += 1
        if x == width:
            x = 0
            y += 1
    return counts, first_seen, color_keys


def _find_tiny_islands(
    color_keys: array,
    width: int,
    height: int,
    *,
    tiny_island_threshold: int,
    sentinel_key: int,
    color_to_region: dict[int, str],
) -> list[ValidationFailure]:
    """Return one warning per connected color island smaller than the threshold."""
    if tiny_island_threshold <= 1:
        return []

    def _find_label(label: int, parent: list[int]) -> int:
        while parent[label] != label:
            parent[label] = parent[parent[label]]
            label = parent[label]
        return label

    def _union_labels(left: int, right: int, parent: list[int], size: list[int]) -> int:
        left_root = _find_label(left, parent)
        right_root = _find_label(right, parent)
        if left_root == right_root:
            return left_root
        if left_root > right_root:
            left_root, right_root = right_root, left_root
        parent[right_root] = left_root
        size[left_root] += size[right_root]
        return left_root

    findings: list[ValidationFailure] = []
    parent: list[int] = []
    size: list[int] = []
    samples: list[tuple[int, int]] = []
    colors: list[int] = []
    previous_runs: list[tuple[int, int, int, int]] = []
    next_label = 0

    for y in range(height):
        row_start = y * width
        current_runs: list[tuple[int, int, int, int]] = []
        x = 0
        while x < width:
            color_key = color_keys[row_start + x]
            run_start = x
            x += 1
            while x < width and color_keys[row_start + x] == color_key:
                x += 1
            run_end = x - 1
            if color_key == sentinel_key:
                continue

            label = next_label
            next_label += 1
            parent.append(label)
            size.append(run_end - run_start + 1)
            samples.append((run_start, y))
            colors.append(color_key)

            for prev_start, prev_end, prev_color, prev_label in previous_runs:
                if prev_color != color_key:
                    continue
                if prev_end < run_start - 1 or prev_start > run_end + 1:
                    continue
                label = _union_labels(label, prev_label, parent, size)

            current_runs.append(
                (run_start, run_end, color_key, _find_label(label, parent))
            )
        previous_runs = current_runs

    for label, color_key in enumerate(colors):
        root = _find_label(label, parent)
        if root != label:
            continue
        island_size = size[root]
        if island_size < tiny_island_threshold:
            rgb = _int_to_rgb(color_key)
            sample = samples[root]
            findings.append(
                ValidationFailure(
                    code="TINY_ISLAND",
                    severity=WARNING,
                    message=(
                        f"Color {_color_key(rgb)} has a tiny island of {island_size} pixel(s) "
                        f"at {sample[0]},{sample[1]} -- likely export artifact / anti-alias bleed."
                    ),
                    detail={
                        "color": list(rgb),
                        "pixel_count": island_size,
                        "sample_xy": list(sample),
                        "region": color_to_region.get(color_key),
                    },
                )
            )

    return findings


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
    visual_width, visual_height = read_png_size(visual_path)
    lookup_width, lookup_height, lookup_rgb_bytes = read_png_rgb_bytes(lookup_path)
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
    sentinel_key = _rgb_to_int(sentinel)
    color_to_region: dict[int, str] = {
        _rgb_to_int(tuple(entry["lookup_color"])): name
        for name, entry in province_data["regions"].items()
    }
    counts, first_seen, color_keys = _count_color_keys(lookup_rgb_bytes, lookup_width)

    # Province coverage: missing entirely vs. insufficient pixels.
    for color_key, region in color_to_region.items():
        pixel_count = counts.get(color_key, 0)
        rgb = _int_to_rgb(color_key)
        if pixel_count == 0:
            findings.append(
                ValidationFailure(
                    code="MISSING_PROVINCE",
                    severity=ERROR,
                    message=(
                        f"Province {region!r} (color {_color_key(rgb)}) does not "
                        f"appear in the lookup image."
                    ),
                    detail={"region": region, "color": list(rgb), "pixel_count": 0},
                )
            )
        elif pixel_count < min_coverage_pixels:
            findings.append(
                ValidationFailure(
                    code="INSUFFICIENT_COVERAGE",
                    severity=ERROR,
                    message=(
                        f"Province {region!r} (color {_color_key(rgb)}) covers only "
                        f"{pixel_count} pixel(s) (minimum: {min_coverage_pixels})."
                    ),
                    detail={
                        "region": region,
                        "color": list(rgb),
                        "pixel_count": pixel_count,
                        "min_required": min_coverage_pixels,
                    },
                )
            )

    # Unmapped colors and tiny islands across the whole lookup.
    for color_key, count in counts.items():
        if color_key == sentinel_key:
            continue
        sample = first_seen[color_key]
        if color_key not in color_to_region:
            rgb = _int_to_rgb(color_key)
            findings.append(
                ValidationFailure(
                    code="UNMAPPED_COLOR",
                    severity=ERROR,
                    message=(
                        f"Lookup contains undeclared color {_color_key(rgb)} "
                        f"({count} pixel(s); first seen at {sample[0]},{sample[1]})."
                    ),
                    detail={
                        "color": list(rgb),
                        "pixel_count": count,
                        "sample_xy": list(sample),
                    },
                )
            )

    findings.extend(
        _find_tiny_islands(
            color_keys,
            lookup_width,
            lookup_height,
            tiny_island_threshold=tiny_island_threshold,
            sentinel_key=sentinel_key,
            color_to_region=color_to_region,
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
    report.extend(validate_adjacency(province_data))
    report.extend(validate_gameplay_fields(province_data))
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

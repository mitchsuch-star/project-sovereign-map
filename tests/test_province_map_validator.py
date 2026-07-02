"""Tests for the Map Readiness Section 4.3 offline color-map validator.

These tests pin the validator's behavioral contract:
  - Registry-only checks (sentinel collision, duplicate colors)
  - Image-side checks (size mismatch, missing province, insufficient
    coverage, tiny islands, unmapped colors, all-clear baseline)
  - CLI exit codes (0 / 1 / 2)
  - JSON output mode

Plan reference: docs/SCALE_READINESS_PLAN.md Section 4.3.

The live Europe registry (europe.json) is also pinned: it must always pass
the registry-only checks so the validator stays trustworthy as a regression
gate for the shipped map data.
"""
from __future__ import annotations

import io
import json
import struct
import zlib
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import pytest

from tools import validate_province_map as vpm


REPO_ROOT = Path(__file__).resolve().parents[1]
LIVE_REGISTRY = (
    REPO_ROOT
    / "godot-client"
    / "project-sovereign"
    / "assets"
    / "maps"
    / "europe.json"
)
TMP_ROOT = REPO_ROOT / ".pytest_tmp_local_run"


# ---------------------------------------------------------------------------
# Fixture helpers: minimal RGBA PNG writer matching test_map_bitmap_contract.py
# (filter type 0). The validator's decoder also handles RGB and filters 1-4.
# ---------------------------------------------------------------------------


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(chunk_type: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + chunk_type
        + payload
        + struct.pack(">I", zlib.crc32(chunk_type + payload) & 0xFFFFFFFF)
    )


def _build_png_payload(
    *,
    width: int,
    height: int,
    raw: bytes,
    color_type: int,
    split_idat: bool = False,
) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    compressed = zlib.compress(raw)
    if split_idat and len(compressed) > 2:
        midpoint = len(compressed) // 2
        idat = _chunk(b"IDAT", compressed[:midpoint]) + _chunk(b"IDAT", compressed[midpoint:])
    else:
        idat = _chunk(b"IDAT", compressed)
    return PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + idat + _chunk(b"IEND", b"")


def _write_rgba_png(
    path: Path,
    rows: list[list[tuple[int, int, int]]],
    *,
    alpha_fn=None,
    split_idat: bool = False,
) -> None:
    """Write a minimal 8-bit RGBA PNG with filter type 0 (no prediction)."""
    height = len(rows)
    width = len(rows[0]) if rows else 0
    assert width > 0 and height > 0
    raw = bytearray()
    for y, row in enumerate(rows):
        raw.append(0)  # filter type
        for x, (r, g, b) in enumerate(row):
            alpha = 255 if alpha_fn is None else alpha_fn(x, y, r, g, b)
            raw.extend((r, g, b, alpha))
    payload = _build_png_payload(
        width=width,
        height=height,
        raw=bytes(raw),
        color_type=6,
        split_idat=split_idat,
    )
    path.write_bytes(payload)


def _write_rgb_png(
    path: Path,
    rows: list[list[tuple[int, int, int]]],
    *,
    split_idat: bool = False,
) -> None:
    """Write a minimal 8-bit RGB PNG (color_type 2)."""
    height = len(rows)
    width = len(rows[0]) if rows else 0
    assert width > 0 and height > 0
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for r, g, b in row:
            raw.extend((r, g, b))
    payload = _build_png_payload(
        width=width,
        height=height,
        raw=bytes(raw),
        color_type=2,
        split_idat=split_idat,
    )
    path.write_bytes(payload)


def _make_registry(
    regions: dict[str, tuple[int, int, int]],
    sentinel: tuple[int, int, int] = (0, 0, 0),
) -> dict:
    return {
        "version": 2,
        "schema_version": 2,
        "no_province_color": list(sentinel),
        "regions": {
            name: {
                "province_id": name.lower(),
                "lookup_color": list(color),
                "anchor": [0, 0],
            }
            for name, color in regions.items()
        },
    }


def _write_registry(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _failure_codes(failures) -> list[str]:
    return [f.code for f in failures]


# ---------------------------------------------------------------------------
# Registry-only checks.
# ---------------------------------------------------------------------------


def test_live_registry_passes_registry_only_checks():
    """The shipped Europe registry must always pass the cheap acceptance gate."""
    province_data = vpm.load_registry(LIVE_REGISTRY)
    assert vpm.validate_registry(province_data) == []


def test_registry_sentinel_collision_is_error():
    data = _make_registry(
        {"Paris": (179, 68, 55), "Belgium": (0, 0, 0)},
        sentinel=(0, 0, 0),
    )
    findings = vpm.validate_registry(data)
    assert _failure_codes(findings) == ["SENTINEL_COLLISION"]
    assert findings[0].severity == vpm.ERROR
    assert findings[0].detail["region"] == "Belgium"
    assert findings[0].detail["color"] == [0, 0, 0]


def test_registry_duplicate_colors_is_error():
    data = _make_registry(
        {
            "Paris": (179, 68, 55),
            "Lyon": (179, 68, 55),
            "Berlin": (74, 102, 47),
        }
    )
    findings = vpm.validate_registry(data)
    assert _failure_codes(findings) == ["DUPLICATE_LOOKUP_COLOR"]
    assert sorted(findings[0].detail["regions"]) == ["Lyon", "Paris"]


def test_registry_loader_rejects_missing_fields(tmp_path):
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps({"regions": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="no_province_color"):
        vpm.load_registry(bad_path)


def test_registry_loader_rejects_malformed_lookup_color(tmp_path):
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(
        json.dumps(
            {
                "no_province_color": [0, 0, 0],
                "regions": {"Paris": {"lookup_color": [300, 0, 0]}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="channels must be ints"):
        vpm.load_registry(bad_path)


def test_registry_loader_rejects_empty_regions(tmp_path):
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(
        json.dumps({"no_province_color": [0, 0, 0], "regions": {}}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="must not be empty"):
        vpm.load_registry(bad_path)


# ---------------------------------------------------------------------------
# Adjacency checks (Slice 1).
# ---------------------------------------------------------------------------


def _registry_with_adjacency(adjacency: dict[str, list[str]]) -> dict:
    """Build a registry whose regions carry the given adjacency lists."""
    colors = {
        "Paris": (179, 68, 55),
        "Belgium": (198, 97, 34),
        "Berlin": (74, 102, 47),
        "Sicily": (55, 88, 179),
    }
    data = _make_registry({n: colors[n] for n in adjacency})
    for name, neighbors in adjacency.items():
        data["regions"][name]["adjacent"] = list(neighbors)
    return data


def test_adjacency_symmetric_graph_passes():
    data = _registry_with_adjacency({"Paris": ["Belgium"], "Belgium": ["Paris"]})
    assert vpm.validate_adjacency(data) == []


def test_adjacency_skipped_when_no_region_declares_it():
    """A registry without any 'adjacent' field is not adjacency-checked."""
    data = _make_registry({"Paris": (179, 68, 55), "Belgium": (198, 97, 34)})
    assert vpm.validate_adjacency(data) == []


def test_live_registry_passes_adjacency_checks():
    """The shipped Europe registry's authored adjacency graph stays clean."""
    province_data = vpm.load_registry(LIVE_REGISTRY)
    assert vpm.validate_adjacency(province_data) == []


def test_adjacency_unknown_target_is_error():
    data = _registry_with_adjacency({"Paris": ["Atlantis"], "Belgium": ["Paris"]})
    findings = vpm.validate_adjacency(data)
    unknown = [f for f in findings if f.code == "ADJACENCY_UNKNOWN_TARGET"]
    assert len(unknown) == 1
    assert unknown[0].severity == vpm.ERROR
    assert unknown[0].detail == {"region": "Paris", "target": "Atlantis"}


def test_adjacency_asymmetry_is_error():
    # Paris lists Belgium; Belgium does not list Paris back.
    data = _registry_with_adjacency({"Paris": ["Belgium"], "Belgium": []})
    findings = vpm.validate_adjacency(data)
    asym = [f for f in findings if f.code == "ADJACENCY_ASYMMETRY"]
    assert len(asym) == 1
    assert asym[0].severity == vpm.ERROR
    assert asym[0].detail == {"from": "Paris", "to": "Belgium"}


def test_adjacency_self_loop_is_error():
    # A province listing itself is a self-loop error, not an unknown target,
    # and must not also fire an asymmetry finding for the self-edge.
    data = _registry_with_adjacency({"Paris": ["Paris"], "Belgium": []})
    findings = vpm.validate_adjacency(data)
    loops = [f for f in findings if f.code == "ADJACENCY_SELF_LOOP"]
    assert len(loops) == 1
    assert loops[0].severity == vpm.ERROR
    assert loops[0].detail == {"region": "Paris"}
    assert not [f for f in findings if f.code == "ADJACENCY_UNKNOWN_TARGET"]
    assert not [f for f in findings if f.code == "ADJACENCY_ASYMMETRY"]


def test_adjacency_isolated_province_is_warning():
    # Belgium has no land edges: a warning (island / awaiting sea links), not
    # an error; Paris<->Berlin stay symmetric and clean.
    data = _registry_with_adjacency(
        {"Paris": ["Berlin"], "Berlin": ["Paris"], "Belgium": []}
    )
    findings = vpm.validate_adjacency(data)
    assert [f.code for f in findings if f.severity == vpm.ERROR] == []
    isolated = [f for f in findings if f.code == "ISOLATED_PROVINCE"]
    assert len(isolated) == 1
    assert isolated[0].severity == vpm.WARNING
    assert isolated[0].detail == {"region": "Belgium"}


def test_validate_all_runs_adjacency_checks(tmp_path):
    """validate_all wires the adjacency pass in alongside the registry checks."""
    data = _registry_with_adjacency({"Paris": ["Atlantis"], "Belgium": ["Paris"]})
    registry = _write_registry(tmp_path, data)
    report = vpm.validate_all(registry, None, None)
    assert "ADJACENCY_UNKNOWN_TARGET" in _failure_codes(report.failures)


# ---------------------------------------------------------------------------
# Image-side checks.
# ---------------------------------------------------------------------------


def test_image_validation_passes_clean_baseline(tmp_path):
    """A lookup with two declared colors at >= min_coverage and a sentinel
    background must produce zero findings."""
    paris = (179, 68, 55)
    belgium = (198, 97, 34)
    sentinel = (0, 0, 0)
    data = _make_registry({"Paris": paris, "Belgium": belgium}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    rows = []
    # 10x10 = 100 pixels: 50 Paris, 50 Belgium, no sentinel pixels
    for y in range(10):
        row = []
        for x in range(10):
            row.append(paris if x < 5 else belgium)
        rows.append(row)
    _write_rgba_png(visual, rows)
    _write_rgba_png(lookup, rows)

    findings = vpm.validate_images(visual, lookup, data)
    assert findings == []


def test_image_validation_flags_size_mismatch(tmp_path):
    paris = (179, 68, 55)
    sentinel = (0, 0, 0)
    data = _make_registry({"Paris": paris}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    _write_rgba_png(visual, [[paris] * 4 for _ in range(4)])
    _write_rgba_png(lookup, [[paris] * 5 for _ in range(5)])

    findings = vpm.validate_images(visual, lookup, data, min_coverage_pixels=1)
    codes = _failure_codes(findings)
    assert "SIZE_MISMATCH" in codes
    size_finding = next(f for f in findings if f.code == "SIZE_MISMATCH")
    assert size_finding.detail == {"visual": [4, 4], "lookup": [5, 5]}


def test_image_validation_flags_missing_province(tmp_path):
    paris = (179, 68, 55)
    belgium = (198, 97, 34)
    sentinel = (0, 0, 0)
    data = _make_registry({"Paris": paris, "Belgium": belgium}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    rows = [[paris] * 10 for _ in range(10)]
    _write_rgba_png(visual, rows)
    _write_rgba_png(lookup, rows)  # Belgium absent entirely

    findings = vpm.validate_images(visual, lookup, data, min_coverage_pixels=1)
    missing = [f for f in findings if f.code == "MISSING_PROVINCE"]
    assert len(missing) == 1
    assert missing[0].detail["region"] == "Belgium"
    assert missing[0].detail["pixel_count"] == 0


def test_image_validation_flags_insufficient_coverage(tmp_path):
    paris = (179, 68, 55)
    belgium = (198, 97, 34)
    sentinel = (0, 0, 0)
    data = _make_registry({"Paris": paris, "Belgium": belgium}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    rows = [[paris] * 10 for _ in range(10)]
    # Drop just 10 Belgium pixels, well below the default 50 minimum.
    for y in range(2):
        for x in range(5):
            rows[y][x] = belgium
    _write_rgba_png(visual, rows)
    _write_rgba_png(lookup, rows)

    findings = vpm.validate_images(visual, lookup, data, tiny_island_threshold=2)
    coverage_findings = [f for f in findings if f.code == "INSUFFICIENT_COVERAGE"]
    assert len(coverage_findings) == 1
    assert coverage_findings[0].detail["region"] == "Belgium"
    assert coverage_findings[0].detail["pixel_count"] == 10
    assert coverage_findings[0].detail["min_required"] == 50


def test_image_validation_flags_tiny_islands_as_warning(tmp_path):
    """A 3-pixel splash of an undeclared color must produce both an
    UNMAPPED_COLOR error and a TINY_ISLAND warning at the same coords."""
    paris = (179, 68, 55)
    sentinel = (0, 0, 0)
    splash = (1, 2, 3)
    data = _make_registry({"Paris": paris}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    rows = [[paris] * 10 for _ in range(10)]
    rows[3][4] = splash
    rows[3][5] = splash
    rows[4][4] = splash
    _write_rgba_png(visual, rows)
    _write_rgba_png(lookup, rows)

    findings = vpm.validate_images(visual, lookup, data, min_coverage_pixels=10)

    tiny = [f for f in findings if f.code == "TINY_ISLAND"]
    assert len(tiny) == 1
    assert tiny[0].severity == vpm.WARNING
    assert tiny[0].detail["color"] == [1, 2, 3]
    assert tiny[0].detail["pixel_count"] == 3
    assert tiny[0].detail["sample_xy"] == [4, 3]
    assert tiny[0].detail["region"] is None  # not mapped to a province

    unmapped = [f for f in findings if f.code == "UNMAPPED_COLOR"]
    assert len(unmapped) == 1
    assert unmapped[0].detail["pixel_count"] == 3
    assert unmapped[0].detail["sample_xy"] == [4, 3]


def test_image_validation_flags_disconnected_repeated_tiny_islands(tmp_path):
    """Repeated 1-pixel specks of the same undeclared color must still be
    flagged as tiny islands even when their aggregate color count exceeds the
    threshold."""
    paris = (179, 68, 55)
    sentinel = (0, 0, 0)
    splash = (1, 2, 3)
    data = _make_registry({"Paris": paris}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    rows = [[paris] * 10 for _ in range(10)]
    for x, y in ((0, 0), (2, 0), (4, 0), (6, 0), (8, 0), (0, 2)):
        rows[y][x] = splash
    _write_rgba_png(visual, rows)
    _write_rgba_png(lookup, rows)

    findings = vpm.validate_images(visual, lookup, data, min_coverage_pixels=1)

    unmapped = [f for f in findings if f.code == "UNMAPPED_COLOR"]
    assert len(unmapped) == 1
    assert unmapped[0].detail["pixel_count"] == 6

    tiny = [f for f in findings if f.code == "TINY_ISLAND"]
    assert len(tiny) == 6
    assert all(f.detail["pixel_count"] == 1 for f in tiny)
    assert {tuple(f.detail["sample_xy"]) for f in tiny} == {
        (0, 0),
        (2, 0),
        (4, 0),
        (6, 0),
        (8, 0),
        (0, 2),
    }


def test_image_validation_flags_unmapped_color_with_high_pixel_count(tmp_path):
    """A high-pixel-count unmapped color must produce an UNMAPPED_COLOR
    error WITHOUT a tiny-island warning."""
    paris = (179, 68, 55)
    sentinel = (0, 0, 0)
    splash = (1, 2, 3)
    data = _make_registry({"Paris": paris}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    rows = [[splash] * 10 for _ in range(10)]
    # Give Paris enough coverage so it doesn't trigger a separate finding.
    for y in range(5):
        for x in range(10):
            rows[y][x] = paris
    _write_rgba_png(visual, rows)
    _write_rgba_png(lookup, rows)

    findings = vpm.validate_images(visual, lookup, data, min_coverage_pixels=10)
    unmapped = [f for f in findings if f.code == "UNMAPPED_COLOR"]
    tiny = [f for f in findings if f.code == "TINY_ISLAND"]
    assert len(unmapped) == 1
    assert unmapped[0].detail["pixel_count"] == 50
    assert tiny == []  # 50 pixels is above the tiny-island threshold


def test_image_validation_ignores_sentinel_pixels(tmp_path):
    """Sentinel (no_province_color) pixels never produce findings."""
    paris = (179, 68, 55)
    sentinel = (0, 0, 0)
    data = _make_registry({"Paris": paris}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    rows = [[sentinel] * 10 for _ in range(10)]
    for y in range(5):
        for x in range(10):
            rows[y][x] = paris
    _write_rgba_png(visual, rows)
    _write_rgba_png(lookup, rows)

    findings = vpm.validate_images(visual, lookup, data, min_coverage_pixels=10)
    assert findings == []


def test_image_validation_handles_rgb_png_input(tmp_path):
    """The decoder must accept 8-bit RGB PNGs (color_type 2), not just RGBA."""
    paris = (179, 68, 55)
    belgium = (198, 97, 34)
    sentinel = (0, 0, 0)
    data = _make_registry({"Paris": paris, "Belgium": belgium}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    rows = []
    for y in range(10):
        row = []
        for x in range(10):
            row.append(paris if x < 5 else belgium)
        rows.append(row)
    _write_rgb_png(visual, rows)
    _write_rgb_png(lookup, rows)

    findings = vpm.validate_images(visual, lookup, data)
    assert findings == []


def test_image_validation_drops_alpha_before_color_comparison(tmp_path):
    paris = (179, 68, 55)
    belgium = (198, 97, 34)
    sentinel = (0, 0, 0)
    data = _make_registry({"Paris": paris, "Belgium": belgium}, sentinel)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    rows = [[paris, belgium] * 5 for _ in range(10)]
    _write_rgba_png(visual, rows)
    _write_rgba_png(lookup, rows, alpha_fn=lambda x, _y, *_rgb: 0 if x % 2 == 0 else 255)

    findings = vpm.validate_images(visual, lookup, data, min_coverage_pixels=1)
    assert findings == []


# ---------------------------------------------------------------------------
# CLI: exit codes and JSON output mode.
# ---------------------------------------------------------------------------


def test_cli_exit_zero_on_clean_live_registry():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vpm.main(["--registry", str(LIVE_REGISTRY)])
    assert rc == 0
    assert "PASS" in buf.getvalue()


def test_cli_exit_one_on_validation_error(tmp_path):
    data = _make_registry({"Paris": (0, 0, 0), "Belgium": (1, 2, 3)}, sentinel=(0, 0, 0))
    registry = _write_registry(tmp_path, data)

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vpm.main(["--registry", str(registry)])
    assert rc == 1
    assert "SENTINEL_COLLISION" in buf.getvalue()
    assert "1 error(s)" in buf.getvalue()


def test_cli_exit_two_on_missing_registry(tmp_path):
    err_buf = io.StringIO()
    with redirect_stderr(err_buf):
        rc = vpm.main(["--registry", str(tmp_path / "does_not_exist.json")])
    assert rc == 2
    assert "registry not found" in err_buf.getvalue()


def test_cli_exit_two_on_visual_without_lookup(tmp_path):
    err_buf = io.StringIO()
    with redirect_stderr(err_buf):
        rc = vpm.main(
            [
                "--registry",
                str(LIVE_REGISTRY),
                "--visual",
                str(tmp_path / "ignored.png"),
            ]
        )
    assert rc == 2
    assert "must be provided together" in err_buf.getvalue()


def test_cli_exit_two_on_empty_registry(tmp_path):
    registry = _write_registry(
        tmp_path,
        {"no_province_color": [0, 0, 0], "regions": {}},
    )

    err_buf = io.StringIO()
    with redirect_stderr(err_buf):
        rc = vpm.main(["--registry", str(registry)])
    assert rc == 2
    assert "must not be empty" in err_buf.getvalue()


def test_cli_json_mode_emits_structured_report(tmp_path):
    data = _make_registry(
        {"Paris": (1, 1, 1), "Lyon": (1, 1, 1)},
        sentinel=(0, 0, 0),
    )
    registry = _write_registry(tmp_path, data)

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vpm.main(["--registry", str(registry), "--json"])
    assert rc == 1
    payload = json.loads(buf.getvalue())
    assert payload["ok"] is False
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 0
    assert payload["failures"][0]["code"] == "DUPLICATE_LOOKUP_COLOR"


def test_cli_strict_mode_promotes_warnings_to_failure_exit(tmp_path):
    """--strict should turn a warnings-only run into a non-zero exit."""
    paris = (179, 68, 55)
    sentinel = (0, 0, 0)
    splash = (1, 2, 3)

    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    # Start fully Paris-covered and inject a 1-pixel undeclared dot.
    rows = [[paris] * 10 for _ in range(10)]
    rows[0][0] = splash
    _write_rgba_png(visual, rows)
    _write_rgba_png(lookup, rows)

    # Map the splash color to a second declared province so it is not an
    # UNMAPPED_COLOR error. With min-coverage=1 it passes the coverage gate
    # but stays below the tiny-island threshold.
    splash_data = _make_registry({"Paris": paris, "Splash": splash}, sentinel)
    splash_registry = _write_registry(tmp_path, splash_data)

    # With min-coverage=1 and tiny-island=5, the 1-pixel splash province
    # passes coverage but stays a TINY_ISLAND warning.
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vpm.main(
            [
                "--registry",
                str(splash_registry),
                "--visual",
                str(visual),
                "--lookup",
                str(lookup),
                "--min-coverage-pixels",
                "1",
            ]
        )
    assert rc == 0  # warnings only, no --strict
    assert "TINY_ISLAND" in buf.getvalue()

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vpm.main(
            [
                "--registry",
                str(splash_registry),
                "--visual",
                str(visual),
                "--lookup",
                str(lookup),
                "--min-coverage-pixels",
                "1",
                "--strict",
            ]
        )
    assert rc == 1  # --strict promotes warnings


def test_cli_exit_two_on_malformed_png_stream(tmp_path):
    registry = _write_registry(tmp_path, _make_registry({"Paris": (179, 68, 55)}))
    visual = tmp_path / "visual.png"
    lookup = tmp_path / "lookup.png"
    _write_rgba_png(visual, [[(179, 68, 55)]])

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    lookup.write_bytes(
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", b"not-zlib")
        + _chunk(b"IEND", b"")
    )

    err_buf = io.StringIO()
    with redirect_stderr(err_buf):
        rc = vpm.main(
            [
                "--registry",
                str(registry),
                "--visual",
                str(visual),
                "--lookup",
                str(lookup),
            ]
        )
    assert rc == 2
    assert "failed to decompress IDAT stream" in err_buf.getvalue()


# ---------------------------------------------------------------------------
# PNG decoder coverage for all 5 filter types and unsupported formats.
# ---------------------------------------------------------------------------


def test_png_decoder_rejects_interlaced_png(tmp_path):
    path = tmp_path / "interlaced.png"
    ihdr = struct.pack(">IIBBBBB", 4, 4, 8, 6, 0, 0, 1)  # interlace=1
    blob = (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(b"\x00" + b"\x00" * 16 * 4))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(blob)
    with pytest.raises(vpm.PNGDecodeError, match="interlaced"):
        vpm.read_png_pixels(path)


def test_png_decoder_rejects_non_png_signature(tmp_path):
    path = tmp_path / "not_a_png.png"
    path.write_bytes(b"hello world")
    with pytest.raises(vpm.PNGDecodeError, match="not a PNG"):
        vpm.read_png_pixels(path)


def test_png_decoder_handles_multiple_idat_chunks(tmp_path):
    path = tmp_path / "multi_idat.png"
    rows = [
        [(1, 2, 3), (4, 5, 6)],
        [(7, 8, 9), (10, 11, 12)],
    ]
    _write_rgb_png(path, rows, split_idat=True)

    assert vpm.read_png_pixels(path) == (2, 2, rows)


def test_png_decoder_rejects_malformed_ihdr_payload(tmp_path):
    path = tmp_path / "bad_ihdr.png"
    path.write_bytes(
        PNG_SIGNATURE
        + _chunk(b"IHDR", b"abc")
        + _chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00"))
        + _chunk(b"IEND", b"")
    )

    with pytest.raises(vpm.PNGDecodeError, match="IHDR payload must be 13 bytes"):
        vpm.read_png_pixels(path)


def test_png_decoder_handles_all_five_filter_types(tmp_path):
    """A 5-row RGBA fixture exercising each scanline filter type round-trips
    cleanly through the decoder. Each row uses a distinct filter."""
    path = tmp_path / "filters.png"
    width, height = 4, 5
    bpp = 4

    rows_rgba: list[list[int]] = []
    for y in range(height):
        row: list[int] = []
        for x in range(width):
            row.extend([(x * 30 + y * 10) & 0xFF, (x * 17 + y * 23) & 0xFF, (x + y) & 0xFF, 255])
        rows_rgba.append(row)

    def _scanline_filter(filter_type: int, row: list[int], prev: list[int] | None) -> bytes:
        prev_bytes = prev if prev is not None else [0] * (width * bpp)
        out = bytearray()
        for x in range(width * bpp):
            left = row[x - bpp] if x >= bpp else 0
            up = prev_bytes[x]
            up_left = prev_bytes[x - bpp] if x >= bpp else 0
            byte = row[x]
            if filter_type == 0:
                value = byte
            elif filter_type == 1:
                value = (byte - left) & 0xFF
            elif filter_type == 2:
                value = (byte - up) & 0xFF
            elif filter_type == 3:
                value = (byte - ((left + up) >> 1)) & 0xFF
            elif filter_type == 4:
                value = (byte - vpm._paeth(left, up, up_left)) & 0xFF
            else:
                raise AssertionError("unreachable")
            out.append(value)
        return bytes(out)

    raw = bytearray()
    prev: list[int] | None = None
    for y, row in enumerate(rows_rgba):
        ftype = y  # 0..4 across the 5 rows
        raw.append(ftype)
        raw.extend(_scanline_filter(ftype, row, prev))
        prev = row

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    blob = (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw)))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(blob)

    w, h, decoded = vpm.read_png_pixels(path)
    assert (w, h) == (width, height)
    for y, decoded_row in enumerate(decoded):
        for x, pixel in enumerate(decoded_row):
            base = x * bpp
            assert pixel == (
                rows_rgba[y][base],
                rows_rgba[y][base + 1],
                rows_rgba[y][base + 2],
            ), f"mismatch at ({x},{y}) for filter type {y}"

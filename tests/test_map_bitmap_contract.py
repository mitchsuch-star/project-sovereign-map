"""Behavioral bitmap-contract tests for Map Readiness §4.2.

These tests do not execute GDScript; the repo has no Godot runtime harness in
pytest. Instead they exercise the bitmap asset contract directly with tiny PNG
fixtures so CI catches regressions that source-level greps miss.
"""

from __future__ import annotations

import json
import struct
import tempfile
import zlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVINCE_JSON = (
    REPO_ROOT
    / "godot-client"
    / "project-sovereign"
    / "assets"
    / "maps"
    / "session8_placeholder_provinces.json"
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
TMP_ROOT = REPO_ROOT / ".pytest_tmp_local_run"


def _load_province_definition() -> dict:
    return json.loads(PROVINCE_JSON.read_text(encoding="utf-8"))


def _color_to_key(rgb: tuple[int, int, int]) -> str:
    return f"{rgb[0]},{rgb[1]},{rgb[2]}"


def _rgba(rgb: tuple[int, int, int]) -> tuple[int, int, int, int]:
    return (rgb[0], rgb[1], rgb[2], 255)


def _chunk(chunk_type: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + chunk_type
        + payload
        + struct.pack(">I", zlib.crc32(chunk_type + payload) & 0xFFFFFFFF)
    )


def _write_rgba_png(path: Path, rows: list[list[tuple[int, int, int, int]]]) -> None:
    height = len(rows)
    width = len(rows[0]) if rows else 0
    assert width > 0 and height > 0
    assert all(len(row) == width for row in rows)

    raw = bytearray()
    for row in rows:
        raw.append(0)
        for pixel in row:
            raw.extend(pixel)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    payload = (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw)))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(payload)


def _read_rgba_png(path: Path) -> tuple[int, int, list[list[tuple[int, int, int, int]]]]:
    blob = path.read_bytes()
    assert blob.startswith(PNG_SIGNATURE)

    cursor = len(PNG_SIGNATURE)
    width = height = None
    idat = bytearray()
    while cursor < len(blob):
        length = struct.unpack(">I", blob[cursor:cursor + 4])[0]
        cursor += 4
        chunk_type = blob[cursor:cursor + 4]
        cursor += 4
        payload = blob[cursor:cursor + length]
        cursor += length
        cursor += 4  # crc
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB",
                payload,
            )
            assert (bit_depth, color_type, compression, filter_method, interlace) == (8, 6, 0, 0, 0)
        elif chunk_type == b"IDAT":
            idat.extend(payload)
        elif chunk_type == b"IEND":
            break

    assert width is not None and height is not None
    raw = zlib.decompress(bytes(idat))
    stride = 1 + width * 4
    rows: list[list[tuple[int, int, int, int]]] = []
    for y in range(height):
        row = raw[y * stride:(y + 1) * stride]
        assert row[0] == 0, "Only filter type 0 fixtures are supported"
        pixels = []
        for x in range(width):
            start = 1 + x * 4
            pixel = tuple(row[start:start + 4])
            assert len(pixel) == 4
            pixels.append(pixel)  # type: ignore[arg-type]
        rows.append(pixels)
    return width, height, rows


def _province_lookup(region_names: tuple[str, ...]) -> tuple[dict[str, str], dict]:
    province_data = _load_province_definition()
    lookup = {}
    for region_name in region_names:
        rgb = tuple(province_data["regions"][region_name]["lookup_color"])
        lookup[_color_to_key(rgb)] = region_name
    return lookup, province_data


def _load_bitmap_contract(
    visual_path: Path,
    lookup_path: Path,
    province_color_lookup: dict[str, str],
    no_province_rgb: tuple[int, int, int],
) -> tuple[bool, str | dict]:
    if not visual_path.exists():
        return False, f"missing visual:{visual_path.name}"
    if not lookup_path.exists():
        return False, f"missing lookup:{lookup_path.name}"

    visual_width, visual_height, _ = _read_rgba_png(visual_path)
    lookup_width, lookup_height, lookup_rows = _read_rgba_png(lookup_path)
    if (visual_width, visual_height) != (lookup_width, lookup_height):
        return False, "size mismatch"

    no_province_key = _color_to_key(no_province_rgb)
    seen = set()
    for y, row in enumerate(lookup_rows):
        for x, pixel in enumerate(row):
            pixel_key = _color_to_key(pixel[:3])
            if pixel_key == no_province_key:
                continue
            if pixel_key not in province_color_lookup:
                return False, f"unmapped color {pixel_key} at {x},{y}"
            seen.add(pixel_key)

    missing = set(province_color_lookup) - seen
    if missing:
        return False, f"missing colors {sorted(missing)}"

    return True, {
        "map_origin": (0, 0),
        "map_canvas_size": (visual_width, visual_height),
        "lookup_rows": lookup_rows,
    }


def _lookup_region_from_contract(
    contract: dict,
    province_color_lookup: dict[str, str],
    x: int,
    y: int,
) -> str:
    width, height = contract["map_canvas_size"]
    if x < 0 or y < 0 or x >= width or y >= height:
        return ""
    pixel = contract["lookup_rows"][y][x]
    return province_color_lookup.get(_color_to_key(pixel[:3]), "")


def test_fixture_bitmap_loader_rejects_missing_and_mismatched_files():
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=TMP_ROOT) as temp_dir:
        tmp_path = Path(temp_dir)
        lookup, province_data = _province_lookup(("Paris", "Belgium"))
        sentinel = tuple(province_data["no_province_color"])

        visual_path = tmp_path / "visual.png"
        lookup_path = tmp_path / "lookup.png"
        _write_rgba_png(lookup_path, [[_rgba(sentinel)]])

        ok, error = _load_bitmap_contract(visual_path, lookup_path, lookup, sentinel)
        assert not ok
        assert error == "missing visual:visual.png"

        _write_rgba_png(visual_path, [[_rgba((20, 20, 20))]])
        _write_rgba_png(
            lookup_path,
            [[_rgba(sentinel), _rgba(sentinel)]],
        )
        ok, error = _load_bitmap_contract(visual_path, lookup_path, lookup, sentinel)
        assert not ok
        assert error == "size mismatch"


def test_fixture_bitmap_loader_rejects_unknown_and_missing_lookup_colors():
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=TMP_ROOT) as temp_dir:
        tmp_path = Path(temp_dir)
        lookup, province_data = _province_lookup(("Paris", "Belgium"))
        sentinel = tuple(province_data["no_province_color"])
        paris = tuple(province_data["regions"]["Paris"]["lookup_color"])
        belgium = tuple(province_data["regions"]["Belgium"]["lookup_color"])

        visual_path = tmp_path / "visual.png"
        lookup_path = tmp_path / "lookup.png"
        _write_rgba_png(visual_path, [[_rgba((20, 20, 20)), _rgba((30, 30, 30))]])

        _write_rgba_png(
            lookup_path,
            [[_rgba(paris), _rgba((paris[0], paris[1], min(255, paris[2] + 1)))]],
        )
        ok, error = _load_bitmap_contract(visual_path, lookup_path, lookup, sentinel)
        assert not ok
        assert error == f"unmapped color {paris[0]},{paris[1]},{min(255, paris[2] + 1)} at 1,0"

        _write_rgba_png(
            lookup_path,
            [[_rgba(paris), _rgba(sentinel)]],
        )
        ok, error = _load_bitmap_contract(visual_path, lookup_path, lookup, sentinel)
        assert not ok
        assert error == f"missing colors ['{_color_to_key(belgium)}']"


def test_fixture_bitmap_lookup_round_trips_region_hits_with_zero_origin():
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=TMP_ROOT) as temp_dir:
        tmp_path = Path(temp_dir)
        lookup, province_data = _province_lookup(("Paris", "Belgium"))
        sentinel = tuple(province_data["no_province_color"])
        paris = tuple(province_data["regions"]["Paris"]["lookup_color"])
        belgium = tuple(province_data["regions"]["Belgium"]["lookup_color"])

        visual_path = tmp_path / "visual.png"
        lookup_path = tmp_path / "lookup.png"
        _write_rgba_png(
            visual_path,
            [
                [_rgba((20, 20, 20)), _rgba((30, 30, 30)), _rgba((40, 40, 40))],
                [_rgba((50, 50, 50)), _rgba((60, 60, 60)), _rgba((70, 70, 70))],
            ],
        )
        _write_rgba_png(
            lookup_path,
            [
                [_rgba(paris), _rgba(belgium), _rgba(sentinel)],
                [_rgba(sentinel), _rgba(belgium), _rgba(paris)],
            ],
        )

        ok, payload = _load_bitmap_contract(visual_path, lookup_path, lookup, sentinel)
        assert ok, payload
        contract = payload
        assert contract["map_origin"] == (0, 0)
        assert contract["map_canvas_size"] == (3, 2)
        assert _lookup_region_from_contract(contract, lookup, 0, 0) == "Paris"
        assert _lookup_region_from_contract(contract, lookup, 1, 0) == "Belgium"
        assert _lookup_region_from_contract(contract, lookup, 2, 0) == ""
        assert _lookup_region_from_contract(contract, lookup, 1, 1) == "Belgium"
        assert _lookup_region_from_contract(contract, lookup, 2, 1) == "Paris"
        assert _lookup_region_from_contract(contract, lookup, -1, 0) == ""
        assert _lookup_region_from_contract(contract, lookup, 3, 0) == ""

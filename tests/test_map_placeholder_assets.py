"""Guardrails for the Session 8 placeholder province-definition assets."""

import json
import re
from pathlib import Path

from backend.models.region import REGIONS_DATA


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map.gd"
PROVINCE_JSON = (
    REPO_ROOT
    / "godot-client"
    / "project-sovereign"
    / "assets"
    / "maps"
    / "session8_placeholder_provinces.json"
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_map_positions(source: str) -> dict[str, tuple[int, int]]:
    positions_match = re.search(
        r"const REGION_POSITIONS\s*=\s*\{(.*?)\}",
        source,
        re.DOTALL,
    )
    assert positions_match, "Could not find REGION_POSITIONS in map.gd"
    positions_block = positions_match.group(1)

    parsed: dict[str, tuple[int, int]] = {}
    for name, x_str, y_str in re.findall(
        r'"([^"]+)":\s*Vector2\(([-\d.]+),\s*([-\d.]+)\)',
        positions_block,
    ):
        parsed[name] = (int(float(x_str)), int(float(y_str)))
    return parsed


def test_placeholder_province_asset_is_referenced_from_map_script():
    source = _read_text(MAP_GD)
    assert "PLACEHOLDER_PROVINCE_DEFINITION_PATH" in source
    assert "session8_placeholder_provinces.json" in source
    assert "func _get_map_asset_definition_path() -> String:" in source


def test_placeholder_province_asset_covers_all_backend_regions():
    province_data = json.loads(PROVINCE_JSON.read_text(encoding="utf-8"))
    regions = province_data["regions"]
    assert set(regions) == set(REGIONS_DATA)


def test_placeholder_province_asset_anchors_match_map_positions():
    map_positions = _parse_map_positions(_read_text(MAP_GD))
    province_data = json.loads(PROVINCE_JSON.read_text(encoding="utf-8"))

    for region_name, position in map_positions.items():
        assert region_name in province_data["regions"], f"Missing province entry: {region_name}"
        anchor = tuple(province_data["regions"][region_name]["anchor"])
        assert anchor == position, f"Anchor mismatch for {region_name}: {anchor} != {position}"


def test_placeholder_province_lookup_colors_are_unique_and_non_sentinel():
    province_data = json.loads(PROVINCE_JSON.read_text(encoding="utf-8"))
    sentinel = tuple(province_data["no_province_color"])
    colors = [
        tuple(entry["lookup_color"])
        for entry in province_data["regions"].values()
    ]

    assert len(colors) == len(set(colors)), "Province lookup colors must be unique"
    assert all(color != sentinel for color in colors)

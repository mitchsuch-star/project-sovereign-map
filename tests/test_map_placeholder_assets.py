"""Guardrails for the Session 8 placeholder province-definition assets.

Schema v2 (Map Readiness Closure Pass §4.1) adds:
- Stable `province_id` per region
- Separate anchors for `unit_anchor`, `label_anchor`, `garrison_anchor`, `building_anchor`
- `wired` and `interactive` flags for runtime gating

Any change to this schema must update these tests plus the renderer seams in
`map_renderer_base.gd` that consume the new fields.
"""

import json
import re
from pathlib import Path

from backend.models.region import REGIONS_DATA


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map.gd"
MAP_RENDERER_BASE_GD = (
    REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map_renderer_base.gd"
)
PROVINCE_JSON = (
    REPO_ROOT
    / "godot-client"
    / "project-sovereign"
    / "assets"
    / "maps"
    / "session8_placeholder_provinces.json"
)

REQUIRED_ANCHOR_FIELDS = (
    "anchor",
    "unit_anchor",
    "label_anchor",
    "garrison_anchor",
    "building_anchor",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_province_definition() -> dict:
    return json.loads(PROVINCE_JSON.read_text(encoding="utf-8"))


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
    province_data = _load_province_definition()
    regions = province_data["regions"]
    assert set(regions) == set(REGIONS_DATA)


def test_placeholder_province_asset_anchors_match_map_positions():
    map_positions = _parse_map_positions(_read_text(MAP_GD))
    province_data = _load_province_definition()

    for region_name, position in map_positions.items():
        assert region_name in province_data["regions"], f"Missing province entry: {region_name}"
        anchor = tuple(province_data["regions"][region_name]["anchor"])
        assert anchor == position, f"Anchor mismatch for {region_name}: {anchor} != {position}"


def test_placeholder_province_lookup_colors_are_unique_and_non_sentinel():
    province_data = _load_province_definition()
    sentinel = tuple(province_data["no_province_color"])
    colors = [
        tuple(entry["lookup_color"])
        for entry in province_data["regions"].values()
    ]

    assert len(colors) == len(set(colors)), "Province lookup colors must be unique"
    assert all(color != sentinel for color in colors)


def test_placeholder_province_asset_declares_schema_version_2():
    province_data = _load_province_definition()
    # Both the legacy `version` key and the explicit `schema_version` key must
    # be at v2 so downstream readers can pin either one.
    assert province_data.get("version") == 2
    assert province_data.get("schema_version") == 2


def test_placeholder_province_entries_have_province_id():
    province_data = _load_province_definition()
    for region_name, entry in province_data["regions"].items():
        assert "province_id" in entry, f"Missing province_id on {region_name}"
        province_id = entry["province_id"]
        assert isinstance(province_id, str)
        assert province_id != ""
        # Current convention: province_id is snake_case derived from the display name.
        assert province_id == province_id.lower(), (
            f"province_id must be lowercase, got {province_id!r} on {region_name}"
        )
        assert " " not in province_id, (
            f"province_id must not contain spaces, got {province_id!r} on {region_name}"
        )


def test_placeholder_province_ids_are_unique():
    province_data = _load_province_definition()
    ids = [entry["province_id"] for entry in province_data["regions"].values()]
    assert len(ids) == len(set(ids)), "province_id values must be unique across regions"


def test_placeholder_province_entries_have_all_anchor_fields():
    province_data = _load_province_definition()
    for region_name, entry in province_data["regions"].items():
        for field in REQUIRED_ANCHOR_FIELDS:
            assert field in entry, f"Missing {field} on {region_name}"
            value = entry[field]
            assert isinstance(value, list) and len(value) == 2, (
                f"{field} on {region_name} must be a 2-element [x, y] list"
            )
            assert all(isinstance(v, (int, float)) for v in value), (
                f"{field} on {region_name} must be numeric"
            )


def test_placeholder_province_entries_have_wired_and_interactive_flags():
    province_data = _load_province_definition()
    for region_name, entry in province_data["regions"].items():
        assert "wired" in entry, f"Missing wired flag on {region_name}"
        assert "interactive" in entry, f"Missing interactive flag on {region_name}"
        assert isinstance(entry["wired"], bool), f"wired must be bool on {region_name}"
        assert isinstance(entry["interactive"], bool), (
            f"interactive must be bool on {region_name}"
        )


def test_placeholder_all_current_provinces_are_wired_and_interactive():
    """The 19-region placeholder has no unwired/non-interactive provinces yet.

    This test pins that invariant so a future author doesn't silently drop a
    gameplay region from the backend without updating the placeholder.
    """
    province_data = _load_province_definition()
    for region_name, entry in province_data["regions"].items():
        assert entry["wired"] is True, f"{region_name} must be wired for the current placeholder"
        assert entry["interactive"] is True, (
            f"{region_name} must be interactive for the current placeholder"
        )


def test_renderer_consumes_wired_and_interactive_flags():
    """The GDScript renderer must reference the new schema flags so the
    placeholder JSON plumbing actually affects runtime behavior.
    """
    source = _read_text(MAP_RENDERER_BASE_GD)
    # Parses the flags out of the province definition entries.
    assert '"wired"' in source, "Renderer must read wired flag from province data"
    assert '"interactive"' in source, "Renderer must read interactive flag from province data"
    # Hover/click path must gate on interactive.
    assert "interactive" in source and "_lookup_region_from_color_map" in source
    # update_all_regions must gate on wired so unwired provinces never populate
    # gameplay dicts.
    update_all_regions_match = re.search(
        r"func update_all_regions\(map_data: Dictionary\):(.*?)(?=\nfunc |\Z)",
        source,
        re.DOTALL,
    )
    assert update_all_regions_match, "Could not locate update_all_regions in renderer"
    assert "wired" in update_all_regions_match.group(1), (
        "update_all_regions must gate on wired flag"
    )


def test_renderer_consumes_new_anchor_fields():
    """Every new anchor field must be parsed by the renderer so commissioned
    art can drive per-feature placement once assets land.
    """
    source = _read_text(MAP_RENDERER_BASE_GD)
    for field in ("unit_anchor", "label_anchor", "garrison_anchor", "building_anchor"):
        assert f'"{field}"' in source, f"Renderer must read {field} from province data"
    assert '"province_id"' in source, "Renderer must read province_id from province data"


def test_placeholder_map_script_does_not_opt_into_bitmap_mode():
    """§4.2: the 19-region placeholder scene must NOT declare bitmap paths.

    The placeholder has no commissioned art — it relies on the circle-fallback
    path inside `_build_map_textures()`. If `map.gd` ever overrides
    `_get_map_visual_bitmap_path()` or `_get_map_lookup_bitmap_path()` to a
    non-empty value without shipping the actual PNGs, the loader will log a
    warning every load and silently keep running on circles — this test pins
    the "dev mode stays on circles" invariant.
    """
    source = _read_text(MAP_GD)
    assert "_get_map_visual_bitmap_path" not in source, (
        "Placeholder map.gd must not override _get_map_visual_bitmap_path — "
        "the base default (empty string) keeps circle fallback active."
    )
    assert "_get_map_lookup_bitmap_path" not in source, (
        "Placeholder map.gd must not override _get_map_lookup_bitmap_path — "
        "the base default (empty string) keeps circle fallback active."
    )

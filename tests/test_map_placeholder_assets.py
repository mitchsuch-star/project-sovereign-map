"""Guardrails for the Session 8 placeholder province-definition assets.

Schema v2 (Map Readiness Closure Pass §4.1) adds:
- Stable `province_id` per region
- Separate anchors for `unit_anchor`, `label_anchor`, `garrison_anchor`, `building_anchor`
- `wired` and `interactive` flags for runtime gating

Any change to this schema must update these tests plus the renderer seams in
`map_renderer_base.gd` that consume the new fields.

Slice 7 note: map.gd no longer loads this asset (the game map is the Europe
renderer — see tests/test_map_slice7_cutover.py), so the map.gd-tied pins that
used to live here are retired. The asset itself + its schema guards stay until
the Slice 9 cleanup pass retires the placeholder assets with owner rows.
"""

import json
import re
from pathlib import Path

from backend.models.region import REGIONS_DATA


REPO_ROOT = Path(__file__).resolve().parents[1]
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


def test_placeholder_province_asset_covers_all_backend_regions():
    province_data = _load_province_definition()
    regions = province_data["regions"]
    assert set(regions) == set(REGIONS_DATA)


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


def test_placeholder_province_entries_have_coastal_flags_matching_backend():
    province_data = _load_province_definition()
    for region_name, entry in province_data["regions"].items():
        assert "is_coastal" in entry, f"Missing is_coastal flag on {region_name}"
        assert isinstance(entry["is_coastal"], bool), (
            f"is_coastal must be bool on {region_name}"
        )
        assert entry["is_coastal"] is bool(
            REGIONS_DATA[region_name].get("is_coastal", False)
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


def test_every_backend_region_is_wired_in_registry():
    """Cross-file drift guard: every REGIONS_DATA region must be `wired: true`.

    `test_placeholder_province_asset_covers_all_backend_regions` already pins
    set equality between the backend roster and the registry keys, but a
    future author could silently flip `wired: false` on an entry that the
    backend AI, ledger, and dispatch still treat as a live gameplay region.
    The renderer §4.4 unwired-gate would then block clicks + grey-overlay a
    province that the rest of the game considers in-play — a silent
    desync. This test fails loudly if that ever happens.
    """
    province_data = _load_province_definition()
    regions = province_data["regions"]
    unwired = sorted(
        name
        for name in REGIONS_DATA
        if regions.get(name, {}).get("wired") is not True
    )
    assert not unwired, (
        "Every region in backend.models.region.REGIONS_DATA must have "
        "wired: true in session8_placeholder_provinces.json. "
        f"Unwired backend regions: {unwired}"
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


# The "dev mode stays on circles" pin (map.gd must not declare bitmap paths)
# retired with the Slice 7 cutover: the game map IS the bitmap Europe renderer
# now (map.gd -> europe_map.gd, which owns the bitmap-path overrides). The
# bitmap contract pins live in tests/test_map_slice7_cutover.py and
# tests/test_map_owner_fill.py.

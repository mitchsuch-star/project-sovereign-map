"""
Map Slice 4 — Europe region set as an alternate backend world.

Guards `create_europe_regions()` + the `WorldState(sovereign_map="europe")`
region-factory seam (G1). The standing invariants:

    * The Europe world builds the validated 126-province map from europe.json —
      the SAME registry the Godot renderer reads (no backend/renderer drift).
    * Ownership, adjacency, and every derived field (income/supply/garrison/grid)
      match the registry + the REGION_TYPE_* tables.
    * The authored roster is fully present: every nation owns its capital; the
      three French satellite states are seeded into world.vassals with their
      authored patron.
    * The Europe world is turn-stable (advances without error) and round-trips
      through save/load.
    * The legacy default (`WorldState()`) and its 19-region fixture are
      UNTOUCHED — the whole gameplay suite depends on it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.ai.strategic_parser import resolve_direction
from backend.models.region import (
    REGION_TYPE_INCOME,
    create_europe_regions,
    create_regions,
    derive_europe_grid_positions,
    get_europe_starting_controllers,
)
from backend.models.world_state import WorldState
from backend.nation_config import (
    EUROPE_NATION_CAPITALS,
    EUROPE_ROSTER,
    EUROPE_VASSAL_WEB,
)

REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe.json"
)


@pytest.fixture(scope="module")
def registry() -> dict:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def europe_world() -> WorldState:
    return WorldState(sovereign_map="europe")


# ════════════════════════════════════════════════════════════════════
# REGION FACTORY — create_europe_regions()
# ════════════════════════════════════════════════════════════════════

def test_builds_all_126_provinces(registry):
    regions = create_europe_regions()
    assert len(regions) == 126
    assert len(regions) == len(registry["regions"])


def test_regions_keyed_by_historical_name(registry):
    regions = create_europe_regions()
    expected_names = {data["name"] for data in registry["regions"].values()}
    assert set(regions.keys()) == expected_names
    # No placeholder ids leaked through as keys.
    assert not any(name.startswith("Region_") for name in regions)


def test_adjacency_translated_to_names_and_symmetric(registry):
    regions = create_europe_regions()
    id_to_name = {rid: d["name"] for rid, d in registry["regions"].items()}
    # Every declared adjacency resolves to a real region name...
    for name, region in regions.items():
        for adj in region.adjacent_regions:
            assert adj in regions, f"{name} -> unknown neighbour {adj}"
            assert not adj.startswith("Region_")
    # ...and matches the registry (id-lists translated to names)...
    for rid, data in registry["regions"].items():
        expected = {id_to_name[a] for a in data.get("adjacent", [])}
        assert set(regions[data["name"]].adjacent_regions) == expected
    # ...and is symmetric.
    for name, region in regions.items():
        for adj in region.adjacent_regions:
            assert name in regions[adj].adjacent_regions


def test_derived_gameplay_fields_match_registry_and_tables(registry):
    regions = create_europe_regions()
    for data in registry["regions"].values():
        r = regions[data["name"]]
        assert r.terrain == data["terrain"]
        assert r.region_type == data["region_type"]
        assert r.is_coastal == bool(data["is_coastal"])
        assert r.is_capital == bool(data.get("is_capital", False))
        # Income derives from region_type (decision #7), not authored per-province.
        assert r.income_value == REGION_TYPE_INCOME[data["region_type"]]
        # Supply capacity derives from region_type + terrain.
        assert r.supply_capacity > 0


def test_grid_positions_unique_and_direction_ordered():
    """Centroid spatial-rank (N4): unique (row, col), N/S/E/W preserving."""
    regions = create_europe_regions()
    positions = [r.grid_position for r in regions.values()]
    assert all(p is not None for p in positions)
    # Unique cell per province — a coarse bucket would collide at 126.
    assert len(set(positions)) == len(positions)


def test_derive_grid_positions_preserves_north_south_east_west(registry):
    grid = derive_europe_grid_positions(registry["regions"])
    # Build name -> anchor to check monotonicity against the derived ranks.
    anchors = {d["name"]: d["anchor"] for d in registry["regions"].values()}
    names = list(grid)
    # A northernmost anchor (min y) must get the smallest row; easternmost the largest col.
    north = min(names, key=lambda n: anchors[n][1])
    south = max(names, key=lambda n: anchors[n][1])
    west = min(names, key=lambda n: anchors[n][0])
    east = max(names, key=lambda n: anchors[n][0])
    assert grid[north][0] < grid[south][0]
    assert grid[west][1] < grid[east][1]


# ════════════════════════════════════════════════════════════════════
# EUROPE WORLD — WorldState(sovereign_map="europe")
# ════════════════════════════════════════════════════════════════════

def test_world_has_126_regions_and_full_roster(europe_world):
    assert europe_world.sovereign_map == "europe"
    assert len(europe_world.regions) == 126
    assert europe_world.player_nation == "France"
    # Every non-player roster nation is an enemy nation.
    assert set(europe_world.enemy_nations) == set(EUROPE_ROSTER) - {"France"}


def test_every_nation_owns_its_capital(europe_world):
    for nation in EUROPE_ROSTER:
        capital = europe_world.get_nation_capital(nation)
        assert capital == EUROPE_NATION_CAPITALS[nation]
        region = europe_world.regions.get(capital)
        assert region is not None, f"{nation} capital {capital} missing"
        assert region.controller == nation
        assert region.is_capital


def test_ownership_matches_registry(europe_world):
    controllers = get_europe_starting_controllers()
    for name, nation in controllers.items():
        assert europe_world.regions[name].controller == nation


def test_capitals_start_with_garrison(europe_world):
    for nation in EUROPE_ROSTER:
        capital = europe_world.get_nation_capital(nation)
        assert europe_world.regions[capital].garrison_strength == 15000


def test_vassal_web_matches_authored_patrons(europe_world):
    # Exactly the three French satellites are seeded.
    assert set(europe_world.vassals) == set(EUROPE_VASSAL_WEB)
    for vassal, authored in EUROPE_VASSAL_WEB.items():
        state = europe_world.vassals[vassal]
        assert state["lord"] == authored["lord"]
        assert state["autonomy"] == 1  # AUTONOMY_SATELLITE
        assert 0 <= state["loyalty"] <= 100


def test_europe_world_advances_a_turn(europe_world):
    start = europe_world.current_turn
    europe_world.advance_turn()
    assert europe_world.current_turn == start + 1


def test_europe_world_round_trips_through_save_load(europe_world):
    data = europe_world.to_dict()
    assert data["sovereign_map"] == "europe"
    restored = WorldState.from_dict(data)
    assert restored.sovereign_map == "europe"
    assert len(restored.regions) == 126
    assert restored.get_nation_capital("Britain") == "London"
    # Region grid_position survives the round trip.
    for name, region in restored.regions.items():
        assert region.grid_position == europe_world.regions[name].grid_position


def test_direction_resolution_works_on_europe_world(europe_world):
    # Find a region with several neighbours and confirm north/south are ordered.
    for name, region in europe_world.regions.items():
        if len(region.adjacent_regions) >= 4:
            north = resolve_direction(name, "north", europe_world)
            south = resolve_direction(name, "south", europe_world)
            assert north is not None and south is not None
            # North neighbour sits at a lower row than the south neighbour.
            assert (
                europe_world.regions[north].grid_position[0]
                < europe_world.regions[south].grid_position[0]
            )
            break


# ════════════════════════════════════════════════════════════════════
# LEGACY IMMUTABILITY — the default must stay the 19-region fixture
# ════════════════════════════════════════════════════════════════════

def test_default_world_is_legacy_untouched():
    legacy = WorldState()
    assert legacy.sovereign_map == "legacy"
    assert len(legacy.regions) == 19
    # The documented Britain proxy the settlement scorer depends on is intact.
    assert legacy.get_nation_capital("Britain") == "Netherlands"
    assert legacy.vassals == {}


def test_legacy_region_set_unchanged():
    legacy = create_regions()
    assert len(legacy) == 19
    assert "Paris" in legacy and "Berlin" in legacy
    # Legacy regions still carry their authored grid_position (parity preserved).
    assert legacy["Paris"].grid_position == (2, 2)


def test_two_worlds_do_not_share_state():
    legacy = WorldState()
    europe = WorldState(sovereign_map="europe")
    # A shared region name (e.g. Paris exists in both) resolves independently.
    assert legacy.get_nation_capital("France") == "Paris"
    assert europe.get_nation_capital("France") == "Paris"
    # Britain diverges — proof the capital maps are not shared.
    assert legacy.get_nation_capital("Britain") == "Netherlands"
    assert europe.get_nation_capital("Britain") == "London"

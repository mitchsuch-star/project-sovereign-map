"""
Verify `/map_topology` exposes the static map topology the Godot frontend needs (§3.2).

This endpoint replaces the hardcoded REGION_CONNECTIONS dict in map.gd. The
backend is the single source of truth for adjacency; the Godot client fetches
this payload on game start instead of maintaining a parallel copy.

Map Slice 5 (backend cutover): the game's map is the 126-province Europe world
built from europe.json, so the endpoint serves the ACTIVE world's graph — the
Europe registry on the default bootstrap, the legacy 19-region set under the
SOVEREIGN_MAP=legacy rollback flag. These are map-contract tests: they assert
properties of "the game's map", which is now Europe.

See docs/SCALE_READINESS_PLAN.md §3.2 + docs/MAP_IMPLEMENTATION_PLAN.md Slice 5.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as main_module
from backend.main import app
from backend.models.region import NATION_CAPITALS, REGIONS_DATA
from backend.nation_config import EUROPE_NATION_CAPITALS

REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe.json"
)

client = TestClient(app)


@pytest.fixture(scope="module")
def registry() -> dict:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def europe_game(monkeypatch):
    """The default game bootstrap — a fresh Europe world as the active state."""
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    return main_module._reset_world_state()


@pytest.fixture
def legacy_game(monkeypatch):
    """The rollback bootstrap (SOVEREIGN_MAP=legacy) as the active state."""
    monkeypatch.setenv("SOVEREIGN_MAP", "legacy")
    yield main_module._reset_world_state()
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    main_module._reset_world_state()


def test_map_topology_returns_success(europe_game):
    resp = client.get("/map_topology")
    assert resp.status_code == 200
    assert resp.json().get("success") is True


def test_map_topology_exposes_all_126_provinces(europe_game, registry):
    resp = client.get("/map_topology").json()
    expected_names = {data["name"] for data in registry["regions"].values()}
    assert len(resp["regions"]) == 126
    assert set(resp["regions"].keys()) == expected_names


def test_map_topology_adjacencies_match_registry(europe_game, registry):
    """The served adjacency is the europe.json graph, id-lists translated to names."""
    resp = client.get("/map_topology").json()
    id_to_name = {rid: d["name"] for rid, d in registry["regions"].items()}
    for data in registry["regions"].values():
        expected = sorted(id_to_name[a] for a in data.get("adjacent", []))
        assert sorted(resp["regions"][data["name"]]["adjacent"]) == expected, (
            f"Adjacency mismatch for {data['name']}"
        )


def test_map_topology_adjacency_is_bilateral_in_payload(europe_game):
    """Serialized topology preserves the bilateral-adjacency invariant."""
    regions = client.get("/map_topology").json()["regions"]
    for name, entry in regions.items():
        for neighbor in entry["adjacent"]:
            assert neighbor in regions, f"{name} lists unknown neighbor {neighbor}"
            assert name in regions[neighbor]["adjacent"], (
                f"{name} claims {neighbor} as neighbor but {neighbor} does not reciprocate"
            )


def test_map_topology_exposes_static_fields(europe_game, registry):
    regions = client.get("/map_topology").json()["regions"]
    for data in registry["regions"].values():
        entry = regions[data["name"]]
        assert entry["terrain"] == data["terrain"]
        assert entry["region_type"] == data["region_type"]
        assert entry["is_capital"] == bool(data.get("is_capital", False))
        assert entry["starting_controller"] == data["starting_controller"]


def test_map_topology_exposes_europe_nation_capitals(europe_game):
    resp = client.get("/map_topology").json()
    assert resp["nation_capitals"] == dict(EUROPE_NATION_CAPITALS)
    # The cutover retires the legacy Britain->Netherlands proxy at the API layer.
    assert resp["nation_capitals"]["Britain"] == "London"


def test_map_topology_grid_position_is_json_serializable_list(europe_game):
    """grid_position is a tuple in Python but must serialize as a JSON array,
    and every Europe province carries a unique spatial-rank cell (N4)."""
    regions = client.get("/map_topology").json()["regions"]
    seen = set()
    for name, entry in regions.items():
        grid = entry["grid_position"]
        assert isinstance(grid, list), f"{name} grid_position did not serialize to a list"
        assert len(grid) == 2
        assert all(isinstance(v, int) for v in grid)
        seen.add(tuple(grid))
    assert len(seen) == len(regions), "grid_position cells must be unique per province"


# ════════════════════════════════════════════════════════════════════
# G1 ROLLBACK — SOVEREIGN_MAP=legacy serves the 19-region topology
# ════════════════════════════════════════════════════════════════════

def test_map_topology_rollback_serves_legacy_19(legacy_game):
    resp = client.get("/map_topology").json()
    assert resp["success"] is True
    assert set(resp["regions"].keys()) == set(REGIONS_DATA.keys())
    assert resp["nation_capitals"] == dict(NATION_CAPITALS)
    for name, data in REGIONS_DATA.items():
        assert sorted(resp["regions"][name]["adjacent"]) == sorted(data["adjacent"])
        assert resp["regions"][name]["grid_position"] == list(data["grid_position"])

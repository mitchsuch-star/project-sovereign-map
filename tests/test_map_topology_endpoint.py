"""
Verify `/map_topology` exposes the static map topology the Godot frontend needs (§3.2).

This endpoint replaces the hardcoded REGION_CONNECTIONS dict in map.gd. The
backend is the single source of truth for adjacency; the Godot client fetches
this payload on game start instead of maintaining a parallel copy.

See docs/SCALE_READINESS_PLAN.md §3.2.
"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.models.region import NATION_CAPITALS, REGIONS_DATA


client = TestClient(app)


def test_map_topology_returns_success():
    resp = client.get("/map_topology")
    assert resp.status_code == 200
    assert resp.json().get("success") is True


def test_map_topology_exposes_all_regions():
    resp = client.get("/map_topology").json()
    assert set(resp["regions"].keys()) == set(REGIONS_DATA.keys())


def test_map_topology_adjacencies_match_backend():
    resp = client.get("/map_topology").json()
    for name, data in REGIONS_DATA.items():
        assert sorted(resp["regions"][name]["adjacent"]) == sorted(data["adjacent"]), (
            f"Adjacency mismatch for {name}"
        )


def test_map_topology_adjacency_is_bilateral_in_payload():
    """Serialized topology preserves the bilateral-adjacency invariant."""
    regions = client.get("/map_topology").json()["regions"]
    for name, entry in regions.items():
        for neighbor in entry["adjacent"]:
            assert neighbor in regions, f"{name} lists unknown neighbor {neighbor}"
            assert name in regions[neighbor]["adjacent"], (
                f"{name} claims {neighbor} as neighbor but {neighbor} does not reciprocate"
            )


def test_map_topology_exposes_static_fields():
    regions = client.get("/map_topology").json()["regions"]
    for name, data in REGIONS_DATA.items():
        entry = regions[name]
        assert entry["terrain"] == data["terrain"]
        assert entry["region_type"] == data["region_type"]
        assert entry["is_capital"] == bool(data.get("is_capital", False))
        assert entry["starting_controller"] == data["starting_controller"]
        assert entry["grid_position"] == list(data["grid_position"])


def test_map_topology_exposes_nation_capitals():
    resp = client.get("/map_topology").json()
    assert resp["nation_capitals"] == dict(NATION_CAPITALS)


def test_map_topology_grid_position_is_json_serializable_list():
    """grid_position is a tuple in Python but must serialize as a JSON array."""
    regions = client.get("/map_topology").json()["regions"]
    for name, entry in regions.items():
        assert isinstance(entry["grid_position"], list), (
            f"{name} grid_position did not serialize to a list"
        )
        assert len(entry["grid_position"]) == 2

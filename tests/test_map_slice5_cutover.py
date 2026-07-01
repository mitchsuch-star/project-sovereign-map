"""
Map Slice 5 — backend game cutover to the 126-province Europe world.

Guards the cutover contract from docs/MAP_IMPLEMENTATION_PLAN.md Slice 5:

    * The game bootstrap (module-load `world`, `_reset_world_state`, /new_game)
      builds the Europe world by default via the SOVEREIGN_MAP flag.
    * (G1) Rollback drill: SOVEREIGN_MAP=legacy restores the 19-region game
      without a code change; flipping back restores Europe.
    * (G2) Legacy-fixture immutability: `create_regions()` still returns the
      EXACT 19-region fixture (names, owners, adjacency) the ~275-file
      gameplay suite depends on — pinned as a frozen snapshot.
    * (DEF-2) Pre-cutover saves fail gracefully (guard lives in save_manager;
      the load-path case is in tests/test_save_load.py).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import backend.main as main_module
from backend.models.region import NATION_CAPITALS, create_regions
from backend.nation_config import EUROPE_ROSTER

client = TestClient(main_module.app)


@pytest.fixture(autouse=True)
def _isolated_save_dir(tmp_path, monkeypatch):
    """Keep /new_game autosaves out of the real saves/ directory."""
    import backend.save_manager as save_manager
    monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")


@pytest.fixture
def default_bootstrap(monkeypatch):
    """Fresh default bootstrap (SOVEREIGN_MAP unset) with post-test restore."""
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    yield main_module._reset_world_state()
    main_module._reset_world_state()


# ════════════════════════════════════════════════════════════════════
# THE CUTOVER — the game bootstrap builds Europe
# ════════════════════════════════════════════════════════════════════

def test_bootstrap_flag_defaults_to_europe(monkeypatch):
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    assert main_module._resolve_sovereign_map() == "europe"


def test_bootstrap_flag_rejects_unknown_values(monkeypatch):
    monkeypatch.setenv("SOVEREIGN_MAP", "atlantis")
    assert main_module._resolve_sovereign_map() == "europe"
    monkeypatch.setenv("SOVEREIGN_MAP", " Legacy ")
    assert main_module._resolve_sovereign_map() == "legacy"


def test_reset_world_state_builds_europe_by_default(default_bootstrap):
    world = default_bootstrap
    assert world.sovereign_map == "europe"
    assert len(world.regions) == 126
    assert world.player_nation == "France"
    assert set(world.enemy_nations) == set(EUROPE_ROSTER) - {"France"}
    assert world.get_nation_capital("Britain") == "London"


def test_new_game_endpoint_builds_europe_world(default_bootstrap):
    response = client.post("/new_game")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["new_game"] is True
    assert data["game_state"]["turn"] == 1

    world = main_module.world
    assert world.sovereign_map == "europe"
    assert len(world.regions) == 126
    assert main_module.game_state["world"] is world


def test_new_game_serves_europe_topology_end_to_end(default_bootstrap):
    """The curl-verifiable contract: /new_game then /map_topology is Europe."""
    assert client.post("/new_game").json()["success"] is True
    topo = client.get("/map_topology").json()
    assert topo["success"] is True
    assert len(topo["regions"]) == 126
    assert topo["nation_capitals"]["Britain"] == "London"


# ════════════════════════════════════════════════════════════════════
# (G1) ROLLBACK DRILL — a flag flip, no code change
# ════════════════════════════════════════════════════════════════════

def test_rollback_drill_flag_flip_restores_legacy_then_europe(monkeypatch):
    # Flip to legacy: the 19-region game comes back exactly.
    monkeypatch.setenv("SOVEREIGN_MAP", "legacy")
    world = main_module._reset_world_state()
    assert world.sovereign_map == "legacy"
    assert len(world.regions) == 19
    assert world.get_nation_capital("Britain") == "Netherlands"
    assert world.get_marshal("Ney") is not None  # legacy armies present

    # /new_game honors the live flag too.
    assert client.post("/new_game").json()["success"] is True
    assert main_module.world.sovereign_map == "legacy"
    assert len(main_module.world.regions) == 19

    # Flip back: Europe returns.
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    world = main_module._reset_world_state()
    assert world.sovereign_map == "europe"
    assert len(world.regions) == 126


# ════════════════════════════════════════════════════════════════════
# (G2) LEGACY-FIXTURE IMMUTABILITY — frozen snapshot of the 19 regions
# ════════════════════════════════════════════════════════════════════

# The exact fixture the gameplay suite depends on. A failing diff here means
# an edit perturbed the legacy map — revert it or consciously re-pin (which
# requires auditing the ~275 test files that reference these names).
LEGACY_FIXTURE_SNAPSHOT = {
    "Bavaria": ("Austria", ["Rhineland", "Saxony", "Tyrol", "Vienna"]),
    "Belgium": ("France", ["Netherlands", "Normandy", "Paris", "Rhineland", "Waterloo"]),
    "Berlin": ("Prussia", ["Bohemia", "Hanover", "Saxony"]),
    "Bohemia": ("Austria", ["Berlin", "Dresden", "Saxony", "Vienna"]),
    "Bordeaux": ("France", ["Brittany", "Lyon", "Marseille", "Paris"]),
    "Brittany": ("France", ["Bordeaux", "Normandy"]),
    "Dresden": ("Saxony", ["Bohemia", "Saxony"]),
    "Hanover": ("Britain", ["Berlin", "Netherlands", "Saxony", "Waterloo"]),
    "Lyon": ("France", ["Bordeaux", "Marseille", "Milan", "Paris", "Rhineland"]),
    "Marseille": ("France", ["Bordeaux", "Lyon", "Milan"]),
    "Milan": ("France", ["Lyon", "Marseille", "Tyrol", "Vienna"]),
    "Netherlands": ("Britain", ["Belgium", "Hanover", "Waterloo"]),
    "Normandy": ("France", ["Belgium", "Brittany", "Paris"]),
    "Paris": ("France", ["Belgium", "Bordeaux", "Lyon", "Normandy"]),
    "Rhineland": ("Prussia", ["Bavaria", "Belgium", "Lyon", "Saxony"]),
    "Saxony": ("Saxony", ["Bavaria", "Berlin", "Bohemia", "Dresden", "Hanover", "Rhineland"]),
    "Tyrol": ("Austria", ["Bavaria", "Milan", "Vienna"]),
    "Vienna": ("Austria", ["Bavaria", "Bohemia", "Milan", "Tyrol"]),
    "Waterloo": ("Britain", ["Belgium", "Hanover", "Netherlands"]),
}

LEGACY_NATION_CAPITALS_SNAPSHOT = {
    "France": "Paris",
    "Britain": "Netherlands",
    "Prussia": "Berlin",
    "Austria": "Vienna",
    "Saxony": "Dresden",
}


def test_legacy_fixture_names_unchanged():
    regions = create_regions()
    assert set(regions.keys()) == set(LEGACY_FIXTURE_SNAPSHOT.keys())


def test_legacy_fixture_owners_unchanged():
    regions = create_regions()
    from backend.models.region import get_starting_controllers
    controllers = get_starting_controllers()
    for name, (owner, _adjacent) in LEGACY_FIXTURE_SNAPSHOT.items():
        assert controllers[name] == owner, f"{name} owner changed"
        assert name in regions


def test_legacy_fixture_adjacency_unchanged():
    regions = create_regions()
    for name, (_owner, adjacent) in LEGACY_FIXTURE_SNAPSHOT.items():
        assert sorted(regions[name].adjacent_regions) == adjacent, (
            f"{name} adjacency changed"
        )


def test_legacy_nation_capitals_unchanged():
    """The Britain->Netherlands proxy (settlement_scoring.py contract) is intact."""
    assert dict(NATION_CAPITALS) == LEGACY_NATION_CAPITALS_SNAPSHOT


# ════════════════════════════════════════════════════════════════════
# WORLD-SCOPED STARTING-CONTROLLER READS — Europe cutover regressions
# ════════════════════════════════════════════════════════════════════

def test_capture_threat_reads_the_world_starting_map():
    """capture_region's R16 threat check must consult the WORLD's starting
    map, not the legacy module global: France recapturing its own Europe
    starting province ("Berry" — a Europe-only name absent from the legacy
    19) accrues NO threat, while capturing foreign territory still does."""
    from backend.models.world_state import WorldState

    world = WorldState(sovereign_map="europe")
    baseline = int(getattr(world, "threat_level", 0))

    # Recapture of own 1805 starting territory: no threat.
    world.regions["Berry"].controller = "Prussia"
    world.capture_region("Berry", "France")
    assert int(world.threat_level) == baseline, (
        "Recapturing France's own starting province must not add threat"
    )

    # Conquest of foreign starting territory: +2 threat.
    world.capture_region("Silesia", "France")
    assert int(world.threat_level) == baseline + 2

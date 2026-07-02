"""
1805 Loader + Constants pre-slice (Map Implementation Plan, approved decision #8).

Guards the eight pre-slice items that must land BEFORE `europe_1805.json` can
be authored (docs/MAP_IMPLEMENTATION_PLAN.md §"LOADER + CONSTANTS PRE-SLICE"):

    1. World-scoped scenario runtime validation — `sovereign_map: "europe"`
       validates against EUROPE_NATION_CAPITALS + the Europe diplomat cast;
       the legacy Venice/Milan rejection contract is untouched.
    2. `regions: "europe"` hook — a Europe scenario omitting `regions` gets
       the validated 126-province world injected (and NO legacy marshals).
    3. Europe-scoped `from_dict` fallbacks — omitted keys keep the WORLD'S
       OWN construction-time surfaces (incl. the 3 seeded satellite vassals).
    4. `/new_game` scenario delivery via the SOVEREIGN_SCENARIO env hook.
    5. 20-nation Europe manpower pools (EUROPE_MANPOWER_POOLS).
    6. Europe `max_turns` 40 → 60 (legacy stays 40).
    7. World-scoped capital reads — Vienna's capture must move war score.
    8. NATION_HONOR_BIAS for the 15 new nations (Russia explicitly neutral),
       Austria AP 3→4, fatter Russian treasury.

Plus the `starting_wars` loader contract: scenario wars seed through the live
`ensure_war_instance_for_pair` machinery (one shared coalition instance),
never hand-authored `war_instance` JSON.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import backend.main as main_module
from backend.models.world_state import DEFAULT_MANPOWER_POOLS, WorldState
from backend.modding.validator import validate_scenario
from backend.nation_config import (
    EUROPE_BASE_ACTIONS,
    EUROPE_MANPOWER_POOLS,
    EUROPE_NATION_GOLD,
    EUROPE_ROSTER,
    NATION_HONOR_BIAS,
    validate_scenario_runtime_support,
)

client = TestClient(main_module.app)

LEGACY_ROSTER = {"France", "Britain", "Prussia", "Austria", "Saxony"}
SATELLITES = {"Holland", "KingdomOfItaly", "Switzerland"}


@pytest.fixture(autouse=True)
def _isolated_save_dir(tmp_path, monkeypatch):
    """Keep /new_game autosaves out of the real saves/ directory."""
    import backend.save_manager as save_manager
    monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")


def _write_scenario(tmp_path, payload, name="scenario.json"):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _minimal_europe_scenario(**extra):
    payload = {"sovereign_map": "europe", "player_nation": "France"}
    payload.update(extra)
    return payload


# ════════════════════════════════════════════════════════════════════
# Item 1 — world-scoped scenario runtime validation
# ════════════════════════════════════════════════════════════════════

def test_europe_scenario_validates_clean():
    errors = validate_scenario_runtime_support(
        _minimal_europe_scenario(nation_gold={"Russia": 1500, "Ottoman": 600})
    )
    assert errors == []


def test_europe_scenario_rejects_unknown_nation():
    errors = validate_scenario_runtime_support(
        _minimal_europe_scenario(nation_gold={"Venice": 100})
    )
    assert any("Venice: missing capital mapping" in e for e in errors)
    assert any("Venice: missing diplomat config" in e for e in errors)


def test_legacy_scenario_contract_unchanged():
    """Europe-only nations still hard-reject on the LEGACY path (no sovereign_map)."""
    errors = validate_scenario_runtime_support({"nation_gold": {"Russia": 1000}})
    assert any("Russia: missing capital mapping" in e for e in errors)
    assert any("Russia: missing diplomat config" in e for e in errors)


def test_europe_capital_in_regions_check_is_europe_scoped():
    """With explicit regions, the capital check reads EUROPE capitals."""
    payload = _minimal_europe_scenario(
        regions={"Paris": {"controller": "France"}},
        nation_gold={"Britain": 2000},
    )
    errors = validate_scenario_runtime_support(payload)
    # Britain's EUROPE capital is London (not the legacy Netherlands proxy)
    assert any("Britain: capital 'London' missing from scenario regions" in e for e in errors)


# ════════════════════════════════════════════════════════════════════
# Item 2 — regions:"europe" hook (and no legacy-marshal injection)
# ════════════════════════════════════════════════════════════════════

def test_minimal_europe_scenario_loads_126_province_world(tmp_path):
    world = WorldState.from_scenario(_write_scenario(tmp_path, _minimal_europe_scenario()))
    assert world.sovereign_map == "europe"
    assert len(world.regions) == 126
    assert world.get_nation_capital("Britain") == "London"


def test_minimal_europe_scenario_starts_army_less(tmp_path):
    world = WorldState.from_scenario(_write_scenario(tmp_path, _minimal_europe_scenario()))
    assert world.marshals == {}


def test_minimal_legacy_scenario_keeps_legacy_defaults(tmp_path):
    """The pinned legacy contract: omitted regions/marshals inject the 19-region fixture."""
    world = WorldState.from_scenario(_write_scenario(tmp_path, {"player_nation": "France"}))
    assert world.sovereign_map == "legacy"
    assert len(world.regions) == 19
    assert "Paris" in world.regions
    assert len(world.marshals) > 0


def test_invalid_europe_scenario_raises(tmp_path):
    path = _write_scenario(tmp_path, _minimal_europe_scenario(nation_gold={"Venice": 1}))
    with pytest.raises(ValueError, match="Invalid scenario"):
        WorldState.from_scenario(path)


# ════════════════════════════════════════════════════════════════════
# Item 3 — Europe-scoped from_dict fallbacks
# ════════════════════════════════════════════════════════════════════

@pytest.fixture
def europe_dict_without_roster_keys():
    data = WorldState(sovereign_map="europe").to_dict()
    for key in ("enemy_nations", "nation_actions", "nation_authority", "diplomats",
                "vassals", "nation_gold", "manpower_pools", "max_turns"):
        data.pop(key, None)
    return data


def test_from_dict_omitted_keys_keep_europe_surfaces(europe_dict_without_roster_keys):
    world = WorldState.from_dict(europe_dict_without_roster_keys)
    assert set(world.enemy_nations) == set(EUROPE_ROSTER) - {"France"}
    assert world.nation_actions["Austria"] == 4
    assert world.nation_authority["Russia"] == 60
    assert len(world.diplomats) == 20 and "Ottoman" in world.diplomats
    assert world.nation_gold["Russia"] == 1500
    assert world.max_turns == 60
    assert set(world.manpower_pools) == set(EUROPE_ROSTER)


def test_from_dict_omitted_vassals_keep_satellites(europe_dict_without_roster_keys):
    world = WorldState.from_dict(europe_dict_without_roster_keys)
    assert set(world.vassals) == SATELLITES
    assert all(world.vassals[v]["lord"] == "France" for v in SATELLITES)


def test_from_dict_explicit_empty_vassals_still_wipes():
    """An EXPLICIT empty dict is authored data (all satellites released)."""
    data = WorldState(sovereign_map="europe").to_dict()
    data["vassals"] = {}
    world = WorldState.from_dict(data)
    assert world.vassals == {}


def test_from_dict_legacy_fallbacks_unchanged():
    """The minimal-legacy-dict contract holds (test_serialization pins 40/1200)."""
    world = WorldState.from_dict({"player_nation": "Prussia"})
    assert world.max_turns == 40
    assert set(world.manpower_pools) == LEGACY_ROSTER
    assert set(world.diplomats) == LEGACY_ROSTER
    assert world.vassals == {}


def test_from_dict_omitted_starting_regions_derive_from_loaded_regions():
    """Omitted nation_starting_regions derive from loaded control (not {})."""
    data = WorldState(sovereign_map="europe").to_dict()
    data.pop("nation_starting_regions", None)
    world = WorldState.from_dict(data)
    assert world.nation_starting_regions, "must not be empty"
    assert "Paris" in world.nation_starting_regions["France"]


# ════════════════════════════════════════════════════════════════════
# Item 4 — SOVEREIGN_SCENARIO bootstrap delivery
# ════════════════════════════════════════════════════════════════════

@pytest.fixture
def restore_bootstrap(monkeypatch):
    """Restore the suite's bare-world module state after bootstrap tests.

    Slice 7 made the 1805 scenario the SHIPPED no-env default, so teardown
    pins the "none" sentinel (the suite-wide conftest default) rather than
    delenv — a delenv reset would boot the full 1805 scenario here.
    """
    yield
    monkeypatch.setenv("SOVEREIGN_SCENARIO", "none")
    main_module._reset_world_state()


def test_sovereign_scenario_env_drives_reset(tmp_path, monkeypatch, restore_bootstrap):
    path = _write_scenario(tmp_path, _minimal_europe_scenario(current_turn=3))
    monkeypatch.setenv("SOVEREIGN_SCENARIO", path)
    world = main_module._reset_world_state()
    assert world.sovereign_map == "europe"
    assert len(world.regions) == 126
    assert world.current_turn == 3
    assert main_module.world is world


def test_new_game_endpoint_honors_sovereign_scenario(tmp_path, monkeypatch, restore_bootstrap):
    path = _write_scenario(tmp_path, _minimal_europe_scenario(current_turn=5))
    monkeypatch.setenv("SOVEREIGN_SCENARIO", path)
    response = client.post("/new_game")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("success", True)
    assert main_module.world.current_turn == 5
    assert len(main_module.world.regions) == 126


def test_sovereign_scenario_missing_file_fails_loudly(monkeypatch, restore_bootstrap):
    monkeypatch.setenv("SOVEREIGN_SCENARIO", r"C:\nonexistent\europe_1805.json")
    with pytest.raises(FileNotFoundError):
        main_module._reset_world_state()


def test_unset_sovereign_scenario_builds_default_world(monkeypatch, restore_bootstrap):
    """Slice 7 default-boot flip: the unset-env default IS the 1805 scenario
    (the full pin suite lives in tests/test_map_slice7_cutover.py; the
    "none" sentinel restores the bare army-less world)."""
    monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    world = main_module._reset_world_state()
    assert world.sovereign_map == "europe"
    assert len(world.regions) == 126
    assert world.current_turn == 1
    assert world.get_marshal("Ney") is not None, (
        "the shipped default boot carries the authored 1805 armies"
    )

    monkeypatch.setenv("SOVEREIGN_SCENARIO", "none")
    bare = main_module._reset_world_state()
    assert len(bare.regions) == 126
    assert not bare.marshals, "the none sentinel opts out to the bare Europe world"


# ════════════════════════════════════════════════════════════════════
# Item 5 — 20-nation Europe manpower pools
# ════════════════════════════════════════════════════════════════════

def test_europe_world_has_pools_for_all_20_nations():
    world = WorldState(sovereign_map="europe")
    assert set(world.manpower_pools) == set(EUROPE_ROSTER)


def test_europe_pools_carry_all_three_types_as_ints():
    for nation, pools in EUROPE_MANPOWER_POOLS.items():
        for pool_type in ("infantry", "cavalry", "artillery"):
            assert pool_type in pools, f"{nation} missing {pool_type} pool"
            assert isinstance(pools[pool_type], int)
            assert pools[pool_type] > 0


def test_legacy_pools_untouched():
    assert set(DEFAULT_MANPOWER_POOLS) == LEGACY_ROSTER
    assert DEFAULT_MANPOWER_POOLS["France"]["infantry"] == 80000
    world = WorldState()
    assert set(world.manpower_pools) == LEGACY_ROSTER


def test_europe_save_pool_backfill_is_world_scoped():
    """A Europe save missing one nation's pools refills from the EUROPE table."""
    data = WorldState(sovereign_map="europe").to_dict()
    data["manpower_pools"].pop("Ottoman")
    world = WorldState.from_dict(data)
    assert world.manpower_pools["Ottoman"] == EUROPE_MANPOWER_POOLS["Ottoman"]


# ════════════════════════════════════════════════════════════════════
# Item 6 — Europe max_turns 60
# ════════════════════════════════════════════════════════════════════

def test_europe_world_gets_60_turns_legacy_keeps_40():
    assert WorldState(sovereign_map="europe").max_turns == 60
    assert WorldState().max_turns == 40


def test_europe_save_without_max_turns_key_restores_60():
    data = WorldState(sovereign_map="europe").to_dict()
    data.pop("max_turns", None)
    assert WorldState.from_dict(data).max_turns == 60


# ════════════════════════════════════════════════════════════════════
# Item 7 — world-scoped capital reads
# ════════════════════════════════════════════════════════════════════

def test_vienna_capture_moves_europe_war_score():
    """The spec's named acceptance: Vienna's capture must move war score."""
    from backend.game_logic.diplomacy import calculate_war_score

    world = WorldState(sovereign_map="europe")
    world.diplomatic_states["Austria|France"] = "WAR"
    before = calculate_war_score("France", "Austria", world, return_components=True)
    world.regions["Vienna"].controller = "France"
    after = calculate_war_score("France", "Austria", world, return_components=True)
    assert before["capital"] == 0
    assert after["capital"] == 20


def test_london_capture_moves_europe_war_score():
    """Britain retires the Netherlands proxy — real London must count."""
    from backend.game_logic.diplomacy import calculate_war_score

    world = WorldState(sovereign_map="europe")
    world.diplomatic_states["Britain|France"] = "WAR"
    world.regions["London"].controller = "France"
    components = calculate_war_score("France", "Britain", world, return_components=True)
    assert components["capital"] == 20


def test_europe_capture_classifies_enemy_capital():
    """war_contribution capital classification reads the world's capital map."""
    from backend.game_logic.settlement_helpers import ensure_war_instance_for_pair
    from backend.game_logic.war_contribution import _classify_capture_occupation_kind

    world = WorldState(sovereign_map="europe")
    world.diplomatic_states["Austria|France"] = "WAR"
    result = ensure_war_instance_for_pair(
        world, "France", "Austria",
        entry_path="test_preslice", root_episode_id="test_preslice", reason="test",
    )
    assert result.get("ok")
    kind = _classify_capture_occupation_kind(
        world,
        region="Vienna",
        actor_nation="France",
        from_controller="Austria",
        war_id=result["war_id"],
    )
    assert kind == "enemy_capital_captured"


def test_europe_war_objective_targets_real_capital():
    """declare_war-family objective targeting must see Europe capitals."""
    from backend.game_logic.diplomacy import get_available_war_objectives

    world = WorldState(sovereign_map="europe")
    objectives = get_available_war_objectives(world, "France", "Russia")
    conquest = next(o for o in objectives if o["type"] == "conquest")
    assert "Vilna" in conquest["description"]


def test_europe_satellite_capital_resolves_for_vassal_mechanics():
    world = WorldState(sovereign_map="europe")
    assert world.get_nation_capital("Holland") == "Amsterdam"
    assert world.get_nation_capital("KingdomOfItaly") == "Milan"


# ════════════════════════════════════════════════════════════════════
# Item 8 — constants: honor bias, Austria AP, Russian treasury
# ════════════════════════════════════════════════════════════════════

def test_honor_bias_covers_every_europe_roster_nation():
    """The 15 new nations are authored; the legacy five keep prior values."""
    new_nations = set(EUROPE_ROSTER) - LEGACY_ROSTER
    for nation in new_nations:
        assert nation in NATION_HONOR_BIAS, f"{nation} missing honor bias"


def test_honor_bias_russia_is_explicit_neutral():
    """DG-4 spec-closure fixtures pin Russia-breaker deltas at bias 1.0."""
    assert NATION_HONOR_BIAS["Russia"] == 1.0


def test_honor_bias_legacy_values_unchanged():
    assert NATION_HONOR_BIAS["Prussia"] == 1.15
    assert NATION_HONOR_BIAS["Spain"] == 0.85
    assert "France" not in NATION_HONOR_BIAS
    assert "Britain" not in NATION_HONOR_BIAS
    assert "Austria" not in NATION_HONOR_BIAS
    assert "Saxony" not in NATION_HONOR_BIAS


def test_honor_bias_values_in_sane_band():
    for nation, bias in NATION_HONOR_BIAS.items():
        assert 0.5 <= bias <= 1.5, f"{nation}: {bias} outside sane band"


def test_austria_action_budget_raised_to_4():
    assert EUROPE_BASE_ACTIONS["Austria"] == 4
    assert WorldState(sovereign_map="europe").nation_actions["Austria"] == 4


def test_russian_treasury_fattened():
    assert EUROPE_NATION_GOLD["Russia"] == 1500
    assert WorldState(sovereign_map="europe").nation_gold["Russia"] == 1500


# ════════════════════════════════════════════════════════════════════
# starting_wars — the loader war-seeding contract
# ════════════════════════════════════════════════════════════════════

COALITION_WARS = [
    {"attacker": "France", "defender": "Britain"},
    {"attacker": "France", "defender": "Austria"},
    {"attacker": "France", "defender": "Russia"},
]


def test_starting_wars_seed_one_shared_coalition_instance(tmp_path):
    path = _write_scenario(tmp_path, _minimal_europe_scenario(starting_wars=COALITION_WARS))
    world = WorldState.from_scenario(path)
    assert len(world.war_instances) == 1
    instance = next(iter(world.war_instances.values()))
    assert instance["attacker_leader"] == "France"
    assert instance["defender_leader"] == "Britain"  # first entry fixes leaders
    assert sorted(instance["defenders"]) == ["Austria", "Britain", "Russia"]


def test_starting_wars_set_states_and_start_turns(tmp_path):
    path = _write_scenario(tmp_path, _minimal_europe_scenario(starting_wars=COALITION_WARS))
    world = WorldState.from_scenario(path)
    for pair in ("Britain|France", "Austria|France", "France|Russia"):
        assert world.diplomatic_states[pair] == "WAR"
        assert world.war_start_turns[pair] == 1


def test_starting_wars_world_advances_turn_cleanly(tmp_path):
    path = _write_scenario(tmp_path, _minimal_europe_scenario(starting_wars=COALITION_WARS))
    world = WorldState.from_scenario(path)
    world.advance_turn()
    assert world.current_turn == 2


def test_starting_wars_validator_rejects_self_war():
    result = validate_scenario(
        _minimal_europe_scenario(starting_wars=[{"attacker": "France", "defender": "France"}])
    )
    assert not result.is_valid
    assert any("attacker and defender are both" in e.message for e in result.errors)


def test_starting_wars_validator_rejects_malformed_entries():
    result = validate_scenario(
        _minimal_europe_scenario(starting_wars=[{"attacker": "France"}, "Britain"])
    )
    assert not result.is_valid
    paths = {e.path for e in result.errors}
    assert "starting_wars[0].defender" in paths
    assert "starting_wars[1]" in paths


def test_starting_wars_nations_are_runtime_validated():
    errors = validate_scenario_runtime_support(
        _minimal_europe_scenario(starting_wars=[{"attacker": "France", "defender": "Venice"}])
    )
    assert any("Venice: missing capital mapping" in e for e in errors)

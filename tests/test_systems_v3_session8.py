"""
Systems Audit V3 — Session 8 Tests
Save/Load, Modding & Campaign Log

14 bugs fixed across persistence, modding validation, and campaign logging.
"""

import json
import pytest
from pathlib import Path

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.save_manager import save_game, load_game
from backend.modding.validator import (
    validate_region,
    VALID_NATIONS,
)
from backend.campaign_log import (
    CAMPAIGN_LOG_TYPES,
    CATEGORY_MAP,
    format_event_oneliner,
)


# ============================================================================
# HELPERS
# ============================================================================

def _make_world() -> WorldState:
    """Create a minimal world for testing."""
    return WorldState(player_nation="France")


def _save_and_load(world: WorldState, tmp_path: Path) -> WorldState:
    """Save a world state to disk and load it back."""
    filepath = tmp_path / "test_save.json"
    result = save_game(world, "Test", filepath=filepath)
    assert result["success"], result["message"]
    load_result = load_game(filepath)
    assert load_result["success"], load_result["message"]
    return load_result["world"]


# ============================================================================
# 2B-1: Transient state clearing on load
# ============================================================================

class TestTransientStateClearingOnLoad:
    """Verify all per-turn transient fields are cleared after save/load."""

    def test_objection_popups_survive_load(self, tmp_path):
        """WO-23 (Aug 21, 2026) — CONSCIOUSLY FLIPPED, for the same reason
        `test_attacks_this_turn_survives_load` below was flipped in Aug
        2026, and the same reason `diplomatic_trust_applied` was carved out
        of the load-side wipe then.

        `objection_popups_this_turn` is not decoration: it is the ONLY live
        limiter on the objection trust channel (max one MODERATE+ objection
        popup per marshal per turn). `from_dict` restored it and `load_game`
        immediately discarded it, so a mid-turn save/load refreshed every
        marshal's budget. The trigger is trust-INDEPENDENT — the
        relationship-SUPPORT check reads personality and relationship only —
        so nothing self-limits the loop as trust climbs, and three of the
        four non-literal French marshals sit on authored -2 pairs at the
        1805 boot. The real turn boundary (`_advance_turn_internal`) still
        clears it, which is where a per-TURN budget is supposed to reset.
        """
        world = _make_world()
        world.objection_popups_this_turn = {"Ney", "Davout"}
        loaded = _save_and_load(world, tmp_path)
        assert loaded.objection_popups_this_turn == {"Ney", "Davout"}

    def test_mild_concerns_cleared_on_load(self, tmp_path):
        world = _make_world()
        world.mild_concerns_this_turn = [{"marshal": "Ney", "concern": "test"}]
        loaded = _save_and_load(world, tmp_path)
        assert loaded.mild_concerns_this_turn == []

    def test_gold_spent_cleared_on_load(self, tmp_path):
        world = _make_world()
        world.gold_spent_this_turn = {"Ney": 50}
        loaded = _save_and_load(world, tmp_path)
        assert loaded.gold_spent_this_turn == {}

    def test_attacks_this_turn_survives_load(self, tmp_path):
        """Aug 2026 health-check audit re-point: attacks_this_turn is
        serialized under an explicit 'PER-TURN TRACKING (for mid-turn
        saves)' contract in to_dict — it is the SOLE input to the flanking
        bonus, so the old load-side clear silently cost the player the
        pincer bonus on any mid-turn save/load. The real turn boundary
        (reset_attack_tracking in advance_turn) still clears it."""
        world = _make_world()
        world.attacks_this_turn = {"Saxony": [{"attacker": "Ney", "defender": "Blucher"}]}
        loaded = _save_and_load(world, tmp_path)
        assert loaded.attacks_this_turn == {
            "Saxony": [{"attacker": "Ney", "defender": "Blucher"}]}


# ============================================================================
# 2C-1: Terrain validation
# ============================================================================

class TestTerrainValidation:
    """Validator must check terrain against VALID_TERRAINS."""

    def test_valid_terrain_passes(self):
        data = {"name": "TestRegion", "adjacent_regions": ["Other"], "terrain": "forest"}
        result = validate_region(data)
        terrain_errors = [e for e in result.errors if "terrain" in e.path]
        assert len(terrain_errors) == 0

    def test_invalid_terrain_fails(self):
        data = {"name": "TestRegion", "adjacent_regions": ["Other"], "terrain": "swamp"}
        result = validate_region(data)
        terrain_errors = [e for e in result.errors if "terrain" in e.path]
        assert len(terrain_errors) == 1
        assert "swamp" in terrain_errors[0].message


# ============================================================================
# 2C-2: Region type validation
# ============================================================================

class TestRegionTypeValidation:
    """Validator must check region_type against VALID_REGION_TYPES."""

    def test_valid_region_type_passes(self):
        data = {"name": "TestRegion", "adjacent_regions": ["Other"], "region_type": "capital"}
        result = validate_region(data)
        type_errors = [e for e in result.errors if "region_type" in e.path]
        assert len(type_errors) == 0

    def test_invalid_region_type_fails(self):
        data = {"name": "TestRegion", "adjacent_regions": ["Other"], "region_type": "hamlet"}
        result = validate_region(data)
        type_errors = [e for e in result.errors if "region_type" in e.path]
        assert len(type_errors) == 1
        assert "hamlet" in type_errors[0].message


# ============================================================================
# 2C-3: Saxony in VALID_NATIONS
# ============================================================================

class TestSaxonyValidNation:
    """Saxony must be in the modding validator's VALID_NATIONS set."""

    def test_saxony_in_valid_nations(self):
        assert "Saxony" in VALID_NATIONS


# ============================================================================
# 2C-4: Scenario validation before from_dict
# ============================================================================

class TestScenarioValidation:
    """from_scenario() must reject invalid scenario data."""

    def test_invalid_scenario_raises_valueerror(self, tmp_path):
        bad_scenario = {
            "player_nation": "France",
            "marshals": {
                "BadMarshal": {
                    # Missing required 'name', 'location', 'strength'
                }
            },
            "regions": {},
        }
        # from_scenario takes a file path, so write the bad data to a file
        filepath = tmp_path / "bad_scenario.json"
        filepath.write_text(json.dumps(bad_scenario), encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid scenario"):
            WorldState.from_scenario(str(filepath))


# ============================================================================
# 2D-1: Event log rolling cap
# ============================================================================

class TestEventLogCap:
    """Event log must be capped to prevent unbounded growth."""

    def test_event_log_capped_at_max(self):
        world = _make_world()
        for i in range(600):
            world.log_event({"type": "test", "index": i})
        assert len(world.event_log) == WorldState.MAX_EVENT_LOG_SIZE

    def test_old_events_removed_first(self):
        world = _make_world()
        for i in range(600):
            world.log_event({"type": "test", "index": i})
        # Oldest events (index 0-99) should be gone, newest should remain
        indices = [e["index"] for e in world.event_log]
        assert 0 not in indices
        assert 599 in indices


# ============================================================================
# 2B-2: Morale default mismatch
# ============================================================================

class TestMoraleDefault:
    """from_dict() morale default must match __init__ default (100)."""

    def test_from_dict_morale_default_matches_init(self):
        data = {
            "name": "TestMarshal",
            "location": "Paris",
            "strength": 10000,
        }
        marshal = Marshal.from_dict(data)
        fresh = Marshal("Fresh", "Paris", 10000, personality="balanced")
        assert marshal.morale == fresh.morale == 100


# ============================================================================
# 2C-5: Strength int cast
# ============================================================================

class TestStrengthIntCast:
    """from_dict() must cast strength to int (Godot float safety)."""

    def test_from_dict_strength_cast_to_int(self):
        data = {
            "name": "TestMarshal",
            "location": "Paris",
            "strength": 15000.0,  # Float from JSON
        }
        marshal = Marshal.from_dict(data)
        assert isinstance(marshal.strength, int)
        assert marshal.strength == 15000


# ============================================================================
# 2B-3, 2B-4: Treaty deepcopy isolation
# ============================================================================

class TestTreatyDeepCopy:
    """to_dict() must deepcopy treaties to prevent mutation leakage."""

    def test_active_treaties_deepcopy_isolation(self):
        world = _make_world()
        world.active_treaties["France-Prussia"] = {
            "type": "NON_AGGRESSION",
            "clauses": [{"type": "territory", "region": "Saxony"}]
        }
        state_dict = world.to_dict()
        # Mutate the serialized copy
        state_dict["active_treaties"]["France-Prussia"]["clauses"].append({"type": "gold"})
        # Original must be unaffected
        assert len(world.active_treaties["France-Prussia"]["clauses"]) == 1

    def test_previous_treaties_deepcopy_isolation(self):
        world = _make_world()
        world.previous_treaties["France-Prussia"] = [
            {"type": "ALLIANCE", "clauses": [{"type": "military"}]}
        ]
        state_dict = world.to_dict()
        # Mutate the serialized copy
        state_dict["previous_treaties"]["France-Prussia"][0]["clauses"].append({"type": "gold"})
        # Original must be unaffected
        assert len(world.previous_treaties["France-Prussia"][0]["clauses"]) == 1


# ============================================================================
# 2D-2: Battle report stripped from event log
# ============================================================================

class TestBattleReportStripped:
    """battle_report should not be stored in event log events."""

    def test_event_log_has_no_battle_report(self):
        from backend.game_logic.combat import CombatResolver
        combat = CombatResolver()
        attacker = Marshal("Ney", "Saxony", 10000, personality="aggressive", nation="France")
        defender = Marshal("Blucher", "Saxony", 8000, personality="aggressive", nation="Prussia")
        result = combat.resolve_battle(attacker, defender)
        event = result.get("log_battle_event", {})
        assert "battle_report" not in event


# ============================================================================
# 2D-3, 2D-4, 2D-5: Campaign log missing event types
# ============================================================================

class TestCampaignLogTypes:
    """New event types must be in whitelist, category map, and have formatters."""

    def test_nation_eliminated_in_whitelist(self):
        assert "nation_eliminated" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP["nation_eliminated"] == "diplomacy"
        line = format_event_oneliner({"type": "nation_eliminated", "nation": "Prussia"})
        assert "Prussia" in line

    def test_vassal_auto_join_war_in_whitelist(self):
        assert "vassal_auto_join_war" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP["vassal_auto_join_war"] == "diplomacy"
        line = format_event_oneliner({"type": "vassal_auto_join_war", "vassal": "Saxony", "overlord": "France"})
        assert "Saxony" in line

    def test_coalition_member_left_in_whitelist(self):
        assert "coalition_member_left" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP["coalition_member_left"] == "diplomacy"
        line = format_event_oneliner({"type": "coalition_member_left", "nation": "Austria"})
        assert "Austria" in line

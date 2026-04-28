"""WPS-A: War Objectives + Ticking Score tests.

Spec: `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` §6-§7, §12, §14-§15.
Plan: `docs/PEACE_DEALS_UMBRELLA_SPEC.md` §5.

Covers (~23 tests):
  1-3.   Objective creation: conquest/subjugation/forced_alliance shape
  4.     Defense auto-assignment on war declaration
  5.     Liberation objective shape (vassal_nations field)
  6.     Subjugation power cap: unavailable when target > 50%
  7.     Ticking — conquest: +2/turn while holding target capital
  8.     Ticking — defense: +1/turn per enemy-held region
  9.     Ticking — cap at 25
  10.    Ticking — no gain when target not held
  11.    Ticking — armistice pause
  12.    War score — ticking as 5th component
  13.    War score — bidirectional (both sides)
  14.    War score — total still capped at ±100
  15.    Ticking survives battle_score decay
  16.    Objective cleanup: war end adds concluded_turn
  17.    Objective cleanup: old records purged after 10 turns
  18.    Serialization roundtrip
  19.    War Purpose popup: declare_war without objective triggers dialogue
  20.    War Purpose selection: proceeds to declaration
  21.    War Purpose back out: cancels
  22.    Set war purpose on defensive war
  23.    Set war purpose — already set blocks
  24.    Campaign log events
  25.    Settlement tier mapping
"""
from __future__ import annotations

import pytest

from backend.campaign_log import (
    CAMPAIGN_LOG_TYPES, CATEGORY_MAP, format_event_oneliner, filter_campaign_log,
)
from backend.ai.llm_client import LLMClient
from backend.game_logic.coalition import form_coalition
from backend.game_logic.diplomacy import (
    OBJECTIVE_TYPES, TICKING_RATES, TICKING_CAP,
    SETTLEMENT_TIERS, SETTLEMENT_TIER_DISPLAY, OBJECTIVE_TYPE_DISPLAY,
    calculate_national_power,
    create_war_objective,
    get_available_war_objectives,
    get_settlement_tier,
    accumulate_war_objective_ticking,
    _conclude_war_objectives,
    _cleanup_old_war_objectives,
    calculate_war_score,
    process_diplomacy_turn,
    declare_war,
    set_diplomatic_state,
)
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _war_world(*, aggressor="France", target="Prussia") -> WorldState:
    """Create a world at WAR between aggressor and target."""
    world = WorldState(player_nation="France")
    set_diplomatic_state(world, aggressor, target, "WAR", "test")
    return world


def _diplo_key(world, a, b):
    return world._make_diplo_key(a, b)


# ════════════════════════════════════════════════════════════════════════════
# 1-3. OBJECTIVE CREATION (RECORD SHAPE)
# ════════════════════════════════════════════════════════════════════════════

class TestObjectiveCreation:

    def test_conquest_record_shape(self):
        obj = create_war_objective("conquest", "France", "Prussia", ["Berlin"], 5)
        assert obj["type"] == "conquest"
        assert obj["declaring_nation"] == "France"
        assert obj["target_nation"] == "Prussia"
        assert obj["target_regions"] == ["Berlin"]
        assert obj["accumulated_ticking"] == 0
        assert obj["created_turn"] == 5
        assert obj["ticking_active"] is False
        assert obj["objective_met_turn"] is None
        assert "vassal_nations" not in obj

    def test_subjugation_record_shape(self):
        obj = create_war_objective("subjugation", "France", "Saxony", ["Dresden"], 3)
        assert obj["type"] == "subjugation"
        assert obj["accumulated_ticking"] == 0

    def test_forced_alliance_record_shape(self):
        obj = create_war_objective("forced_alliance", "France", "Prussia", ["Berlin"], 1)
        assert obj["type"] == "forced_alliance"
        assert obj["ticking_active"] is False


# ════════════════════════════════════════════════════════════════════════════
# 4. DEFENSE AUTO-ASSIGNMENT
# ════════════════════════════════════════════════════════════════════════════

class TestDefenseAutoAssignment:

    def test_defender_gets_defense_objective(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Prussia", "PEACE", "test")
        result = declare_war(world, "France", "Prussia", war_objective="conquest")
        assert result["success"], result.get("message")
        dk = _diplo_key(world, "France", "Prussia")
        assert dk in world.war_objectives
        defender_obj = world.war_objectives[dk].get("Prussia")
        assert defender_obj is not None
        assert defender_obj["type"] == "defense"
        assert defender_obj["declaring_nation"] == "Prussia"
        assert defender_obj["target_nation"] == "France"

    def test_ai_ai_war_defaults_to_conquest_objective(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "Prussia", "Austria", "PEACE", "test")
        result = declare_war(world, "Prussia", "Austria")
        assert result["success"], result.get("message")
        dk = _diplo_key(world, "Prussia", "Austria")
        assert world.war_objectives[dk]["Prussia"]["type"] == "conquest"


# ════════════════════════════════════════════════════════════════════════════
# 5. LIBERATION OBJECTIVE SHAPE
# ════════════════════════════════════════════════════════════════════════════

class TestLiberationObjective:

    def test_liberation_has_vassal_nations(self):
        obj = create_war_objective(
            "liberation", "Prussia", "France", ["Paris"],
            current_turn=2, vassal_nations=["Saxony"],
        )
        assert obj["type"] == "liberation"
        assert obj["vassal_nations"] == ["Saxony"]

    def test_coalition_member_gets_liberation_objective(self):
        world = WorldState(player_nation="France")
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 50}
        from backend.models.region import NATION_CAPITALS
        saxony_cap = NATION_CAPITALS.get("Saxony")
        if saxony_cap and saxony_cap in world.regions:
            world.regions[saxony_cap].controller = "France"
        result = form_coalition(["Austria"], world)
        assert result["success"], result.get("message")
        dk = _diplo_key(world, "France", "Austria")
        assert world.war_objectives[dk]["Austria"]["type"] == "liberation"
        assert world.war_objectives[dk]["Austria"]["vassal_nations"] == ["Saxony"]


# ════════════════════════════════════════════════════════════════════════════
# 6. SUBJUGATION POWER CAP
# ════════════════════════════════════════════════════════════════════════════

class TestSubjugationPowerCap:

    def test_subjugation_unavailable_when_target_too_powerful(self):
        world = WorldState(player_nation="France")
        objectives = get_available_war_objectives(world, "France", "Prussia")
        subj = next(o for o in objectives if o["type"] == "subjugation")
        france_power = calculate_national_power("France", world)
        prussia_power = calculate_national_power("Prussia", world)
        if prussia_power > france_power // 2:
            assert subj["available"] is False
            assert subj["reason"] is not None
        else:
            assert subj["available"] is True

    def test_conquest_always_available(self):
        world = WorldState(player_nation="France")
        objectives = get_available_war_objectives(world, "France", "Prussia")
        conquest = next(o for o in objectives if o["type"] == "conquest")
        assert conquest["available"] is True

    def test_forced_alliance_always_available(self):
        world = WorldState(player_nation="France")
        objectives = get_available_war_objectives(world, "France", "Prussia")
        fa = next(o for o in objectives if o["type"] == "forced_alliance")
        assert fa["available"] is True


# ════════════════════════════════════════════════════════════════════════════
# 7-8. TICKING ACCUMULATION
# ════════════════════════════════════════════════════════════════════════════

class TestTickingAccumulation:

    def test_conquest_ticking_when_holding_capital(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        from backend.models.region import NATION_CAPITALS
        target_cap = NATION_CAPITALS.get("Prussia")
        if target_cap and target_cap in world.regions:
            world.regions[target_cap].controller = "France"
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia",
                                           [target_cap] if target_cap else [], 1),
        }
        events = accumulate_war_objective_ticking(world)
        obj = world.war_objectives[dk]["France"]
        if target_cap and target_cap in world.regions:
            assert obj["accumulated_ticking"] == 2
            assert obj["ticking_active"] is True
            assert len(events) == 1
            assert events[0]["type"] == "war_objective_ticking_started"

    def test_defense_ticking_when_enemy_holds_regions(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        starting = list(world.nation_starting_regions.get("Prussia", []))
        if not starting:
            pytest.skip("No starting regions for Prussia")
        world.regions[starting[0]].controller = "France"
        world.war_objectives[dk] = {
            "Prussia": create_war_objective("defense", "Prussia", "France",
                                            starting, 1),
        }
        events = accumulate_war_objective_ticking(world)
        obj = world.war_objectives[dk]["Prussia"]
        assert obj["accumulated_ticking"] >= 1
        assert obj["ticking_active"] is True

    def test_subjugation_ticking_rate_is_three(self):
        world = _war_world(target="Austria")
        dk = _diplo_key(world, "France", "Austria")
        from backend.models.region import NATION_CAPITALS
        target_cap = NATION_CAPITALS.get("Austria")
        if target_cap and target_cap in world.regions:
            world.regions[target_cap].controller = "France"
        world.war_objectives[dk] = {
            "France": create_war_objective(
                "subjugation", "France", "Austria",
                [target_cap] if target_cap else [], 1,
            ),
        }
        accumulate_war_objective_ticking(world)
        assert world.war_objectives[dk]["France"]["accumulated_ticking"] == 3

    def test_liberation_ticking_when_france_holds_vassal_capital(self):
        world = _war_world(aggressor="Austria", target="France")
        dk = _diplo_key(world, "Austria", "France")
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 50}
        from backend.models.region import NATION_CAPITALS
        saxony_cap = NATION_CAPITALS.get("Saxony")
        if saxony_cap and saxony_cap in world.regions:
            world.regions[saxony_cap].controller = "France"
        world.war_objectives[dk] = {
            "Austria": create_war_objective(
                "liberation", "Austria", "France",
                [saxony_cap] if saxony_cap else [],
                current_turn=1, vassal_nations=["Saxony"],
            ),
        }
        accumulate_war_objective_ticking(world)
        assert world.war_objectives[dk]["Austria"]["accumulated_ticking"] == 1


# ════════════════════════════════════════════════════════════════════════════
# 9. TICKING CAP AT 25
# ════════════════════════════════════════════════════════════════════════════

class TestTickingCap:

    def test_ticking_caps_at_25(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        from backend.models.region import NATION_CAPITALS
        target_cap = NATION_CAPITALS.get("Prussia")
        if target_cap and target_cap in world.regions:
            world.regions[target_cap].controller = "France"
        obj = create_war_objective("conquest", "France", "Prussia",
                                   [target_cap] if target_cap else [], 1)
        obj["accumulated_ticking"] = 24
        world.war_objectives[dk] = {"France": obj}
        accumulate_war_objective_ticking(world)
        assert world.war_objectives[dk]["France"]["accumulated_ticking"] <= TICKING_CAP

    def test_objective_met_turn_set_when_cap_reached(self):
        world = _war_world()
        world.current_turn = 7
        dk = _diplo_key(world, "France", "Prussia")
        from backend.models.region import NATION_CAPITALS
        target_cap = NATION_CAPITALS.get("Prussia")
        if target_cap and target_cap in world.regions:
            world.regions[target_cap].controller = "France"
        obj = create_war_objective(
            "conquest", "France", "Prussia",
            [target_cap] if target_cap else [], 1,
        )
        obj["accumulated_ticking"] = 24
        world.war_objectives[dk] = {"France": obj}
        accumulate_war_objective_ticking(world)
        assert world.war_objectives[dk]["France"]["accumulated_ticking"] == TICKING_CAP
        assert world.war_objectives[dk]["France"]["objective_met_turn"] == 7


# ════════════════════════════════════════════════════════════════════════════
# 10. TICKING — NO GAIN WHEN NOT HOLDING
# ════════════════════════════════════════════════════════════════════════════

class TestTickingNoGain:

    def test_no_ticking_when_not_holding_target(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        from backend.models.region import NATION_CAPITALS
        target_cap = NATION_CAPITALS.get("Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia",
                                           [target_cap] if target_cap else [], 1),
        }
        events = accumulate_war_objective_ticking(world)
        obj = world.war_objectives[dk]["France"]
        assert obj["accumulated_ticking"] == 0
        assert obj["ticking_active"] is False
        assert len(events) == 0


# ════════════════════════════════════════════════════════════════════════════
# 11. TICKING — ARMISTICE PAUSE
# ════════════════════════════════════════════════════════════════════════════

class TestTickingArmisticePause:

    def test_no_ticking_during_armistice(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        from backend.models.region import NATION_CAPITALS
        target_cap = NATION_CAPITALS.get("Prussia")
        if target_cap and target_cap in world.regions:
            world.regions[target_cap].controller = "France"
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia",
                                           [target_cap] if target_cap else [], 1),
        }
        set_diplomatic_state(world, "France", "Prussia", "ARMISTICE", "peace")
        events = accumulate_war_objective_ticking(world)
        obj = world.war_objectives[dk]["France"]
        assert obj["accumulated_ticking"] == 0
        assert len(events) == 0


# ════════════════════════════════════════════════════════════════════════════
# 12-14. WAR SCORE INTEGRATION
# ════════════════════════════════════════════════════════════════════════════

class TestWarScoreIntegration:

    def test_ticking_appears_as_5th_component(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia", ["Berlin"], 1),
        }
        world.war_objectives[dk]["France"]["accumulated_ticking"] = 10
        components = calculate_war_score("France", "Prussia", world, return_components=True)
        assert "ticking" in components
        assert components["ticking"] == 10

    def test_bidirectional_ticking(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia", ["Berlin"], 1),
            "Prussia": create_war_objective("defense", "Prussia", "France", ["Paris"], 1),
        }
        world.war_objectives[dk]["France"]["accumulated_ticking"] = 15
        world.war_objectives[dk]["Prussia"]["accumulated_ticking"] = 5
        components = calculate_war_score("France", "Prussia", world, return_components=True)
        assert components["ticking"] == 10  # 15 - 5

    def test_war_score_total_capped(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia", ["Berlin"], 1),
        }
        world.war_objectives[dk]["France"]["accumulated_ticking"] = 25
        from backend.models.region import NATION_CAPITALS
        target_cap = NATION_CAPITALS.get("Prussia")
        if target_cap and target_cap in world.regions:
            world.regions[target_cap].controller = "France"
        starting = list(world.nation_starting_regions.get("Prussia", []))
        for r in starting:
            if r in world.regions:
                world.regions[r].controller = "France"
        components = calculate_war_score("France", "Prussia", world, return_components=True)
        assert -100 <= components["total"] <= 100

    def test_process_turn_stores_post_ticking_war_score(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Austria", "PEACE", "test")
        result = declare_war(world, "France", "Austria", war_objective="conquest")
        assert result["success"], result.get("message")
        dk = _diplo_key(world, "France", "Austria")
        from backend.models.region import NATION_CAPITALS
        target_cap = NATION_CAPITALS.get("Austria")
        if target_cap and target_cap in world.regions:
            world.regions[target_cap].controller = "France"
        process_diplomacy_turn(world)
        assert world.war_objectives[dk]["France"]["accumulated_ticking"] == 2
        assert world.war_scores[dk] == calculate_war_score("Austria", "France", world)

    def test_territory_score_does_not_scan_all_regions(self):
        class NoFullRegionScanDict(dict):
            def values(self):
                raise AssertionError("calculate_war_score must not scan all regions")

        world = _war_world()
        world.regions["Berlin"].controller = "France"
        world.regions = NoFullRegionScanDict(world.regions)

        components = calculate_war_score("France", "Prussia", world, return_components=True)

        assert components["territory"] > 0


# ════════════════════════════════════════════════════════════════════════════
# 15. TICKING SURVIVES BATTLE SCORE DECAY
# ════════════════════════════════════════════════════════════════════════════

class TestTickingNoDecay:

    def test_ticking_preserved_after_decay(self):
        from backend.game_logic.diplomacy import apply_war_score_decay
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia", ["Berlin"], 1),
        }
        world.war_objectives[dk]["France"]["accumulated_ticking"] = 12
        apply_war_score_decay(world)
        assert world.war_objectives[dk]["France"]["accumulated_ticking"] == 12


# ════════════════════════════════════════════════════════════════════════════
# 16. OBJECTIVE CLEANUP — WAR END
# ════════════════════════════════════════════════════════════════════════════

class TestObjectiveCleanup:

    def test_war_end_concludes_objectives(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia", ["Berlin"], 1),
            "Prussia": create_war_objective("defense", "Prussia", "France", ["Paris"], 1),
        }
        world.current_turn = 10
        _conclude_war_objectives(world, dk)
        assert world.war_objectives[dk]["France"]["concluded_turn"] == 10
        assert world.war_objectives[dk]["Prussia"]["concluded_turn"] == 10

    def test_armistice_pauses_without_concluding_objective(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Austria", "PEACE", "test")
        result = declare_war(world, "France", "Austria", war_objective="conquest")
        assert result["success"], result.get("message")
        dk = _diplo_key(world, "France", "Austria")
        world._ratify_treaty({
            "type": "armistice",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "clauses": [],
            "sweeteners": [],
            "demands": [],
        })
        assert world.get_diplomatic_state("France", "Austria") == "ARMISTICE"
        assert world.war_objectives[dk]["France"].get("concluded_turn") is None

    def test_armistice_to_peace_concludes_objective(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Austria", "PEACE", "test")
        result = declare_war(world, "France", "Austria", war_objective="conquest")
        assert result["success"], result.get("message")
        dk = _diplo_key(world, "France", "Austria")
        world._ratify_treaty({
            "type": "armistice",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "clauses": [],
            "sweeteners": [],
            "demands": [],
        })
        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "clauses": [],
            "sweeteners": [],
            "demands": [],
        })
        assert world.get_diplomatic_state("France", "Austria") == "PEACE"
        assert world.war_objectives[dk]["France"]["concluded_turn"] == world.current_turn


# ════════════════════════════════════════════════════════════════════════════
# 17. OBJECTIVE CLEANUP — OLD RECORDS PURGED
# ════════════════════════════════════════════════════════════════════════════

class TestObjectiveOldCleanup:

    def test_concluded_objectives_purged_after_10_turns(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia", ["Berlin"], 1),
        }
        world.war_objectives[dk]["France"]["concluded_turn"] = 5
        world.current_turn = 20
        _cleanup_old_war_objectives(world)
        assert dk not in world.war_objectives

    def test_recent_concluded_objectives_kept(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia", ["Berlin"], 1),
        }
        world.war_objectives[dk]["France"]["concluded_turn"] = 15
        world.current_turn = 20
        _cleanup_old_war_objectives(world)
        assert dk in world.war_objectives


# ════════════════════════════════════════════════════════════════════════════
# 18. SERIALIZATION ROUNDTRIP
# ════════════════════════════════════════════════════════════════════════════

class TestSerialization:

    def test_war_objectives_roundtrip(self):
        world = _war_world()
        dk = _diplo_key(world, "France", "Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia", ["Berlin"], 3),
            "Prussia": create_war_objective("defense", "Prussia", "France", ["Paris"], 3),
        }
        world.war_objectives[dk]["France"]["accumulated_ticking"] = 8
        data = world.to_dict()
        assert "war_objectives" in data
        restored = WorldState.from_dict(data)
        rdk = restored._make_diplo_key("France", "Prussia")
        assert rdk in restored.war_objectives
        assert restored.war_objectives[rdk]["France"]["accumulated_ticking"] == 8
        assert restored.war_objectives[rdk]["France"]["type"] == "conquest"
        assert restored.war_objectives[rdk]["Prussia"]["type"] == "defense"


# ════════════════════════════════════════════════════════════════════════════
# 19-21. WAR PURPOSE POPUP
# ════════════════════════════════════════════════════════════════════════════

class TestWarPurposePopup:

    def test_declare_war_without_objective_triggers_popup(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Prussia", "PEACE", "test")
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        exec_ = DiplomaticExecutor.__new__(DiplomaticExecutor)
        result = exec_._execute_diplomatic_declare_war(
            {"target_nation": "Prussia"}, world
        )
        assert result.get("awaiting_diplomatic_response") is True
        assert result.get("war_purpose_popup") is not None
        popup = result["war_purpose_popup"]
        assert popup["target_nation"] == "Prussia"
        assert len(popup["objectives"]) >= 2
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue["type"] == "war_purpose_selection"

    def test_declare_war_with_objective_proceeds(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Prussia", "PEACE", "test")
        result = declare_war(world, "France", "Prussia", war_objective="conquest")
        assert result["success"], result.get("message")
        dk = _diplo_key(world, "France", "Prussia")
        assert dk in world.war_objectives
        assert world.war_objectives[dk]["France"]["type"] == "conquest"

    def test_back_out_cancels(self):
        """Selecting 'Back Out' / reconsider pops the dialogue without war."""
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Prussia", "PEACE", "test")
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        exec_ = DiplomaticExecutor.__new__(DiplomaticExecutor)
        exec_._execute_diplomatic_declare_war(
            {"target_nation": "Prussia"}, world
        )
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        result = exec_._process_dialogue_choice(
            "reconsider", {"action": "reconsider"}, dialogue, world,
        )
        assert result["success"]
        state = world.get_diplomatic_state("France", "Prussia")
        assert state != "WAR"

    def test_confirm_set_war_purpose_dialogue_handler(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Austria", "PEACE", "test")
        result = declare_war(world, "Austria", "France")
        assert result["success"], result.get("message")
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        exec_ = DiplomaticExecutor.__new__(DiplomaticExecutor)
        prompt = exec_._set_war_purpose_inner("Austria", None, world)
        assert prompt.get("awaiting_diplomatic_response") is True
        dialogue = world.pending_diplomatic_dialogue
        selected = {
            "action": "confirm_set_war_purpose",
            "target_nation": "Austria",
            "objective_type": "conquest",
        }
        result = exec_._process_dialogue_choice(
            "confirm_set_war_purpose", selected, dialogue, world,
        )
        assert result["success"], result.get("message")
        dk = _diplo_key(world, "France", "Austria")
        assert world.war_objectives[dk]["France"]["type"] == "conquest"

    def test_player_attack_into_peace_war_stages_war_purpose(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Austria", "PEACE", "test")
        ney = world.get_marshal("Ney")
        schwarzenberg = world.get_marshal("Schwarzenberg")
        assert ney is not None
        assert schwarzenberg is not None
        schwarzenberg.location = ney.location
        dp_before = world.diplomatic_points

        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "attack", "marshal": "Ney", "target": "Schwarzenberg"}},
            {"world": world},
        )

        assert result.get("awaiting_diplomatic_response") is True
        assert result.get("war_purpose_popup") is not None
        assert world.get_diplomatic_state("France", "Austria") == "PEACE"
        assert world.diplomatic_points == dp_before


# ════════════════════════════════════════════════════════════════════════════
# 22-23. SET WAR PURPOSE (DEFENSIVE WARS)
# ════════════════════════════════════════════════════════════════════════════

class TestSetWarPurpose:

    def test_set_war_purpose_on_defensive_war(self):
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Prussia", "PEACE", "test")
        declare_war(world, "Prussia", "France")
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        exec_ = DiplomaticExecutor.__new__(DiplomaticExecutor)
        result = exec_._set_war_purpose_inner("Prussia", "conquest", world)
        assert result["success"]
        dk = _diplo_key(world, "France", "Prussia")
        assert world.war_objectives[dk]["France"]["type"] == "conquest"

    def test_set_war_purpose_already_set_blocked(self):
        """Cannot change a non-defense objective mid-war."""
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Prussia", "WAR", "test")
        dk = _diplo_key(world, "France", "Prussia")
        world.war_objectives[dk] = {
            "France": create_war_objective("conquest", "France", "Prussia", ["Berlin"], 1),
        }
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        exec_ = DiplomaticExecutor.__new__(DiplomaticExecutor)
        result = exec_._set_war_purpose_inner("Prussia", "subjugation", world)
        assert result["success"] is False
        assert "already set" in result["message"]

    def test_parser_extracts_set_war_purpose(self):
        client = LLMClient(use_real_api=False)
        parsed = client.parse_command_structured(
            "Talleyrand, set war purpose conquest against Austria"
        )
        command = parsed.diplomatic_data
        assert parsed.action == "set_war_purpose"
        assert command["target_nation"] == "Austria"
        assert command["objective_type"] == "conquest"


# ════════════════════════════════════════════════════════════════════════════
# 24. CAMPAIGN LOG EVENTS
# ════════════════════════════════════════════════════════════════════════════

class TestCampaignLogEvents:

    def test_war_objective_declared_in_log_types(self):
        assert "war_objective_declared" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP.get("war_objective_declared") == "diplomacy"

    def test_war_objective_ticking_started_in_log_types(self):
        assert "war_objective_ticking_started" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP.get("war_objective_ticking_started") == "diplomacy"

    def test_format_declared_oneliner(self):
        event = {
            "type": "war_objective_declared",
            "declaring_nation": "France",
            "target_nation": "Prussia",
            "objective_type": "conquest",
            "turn": 5,
        }
        line = format_event_oneliner(event)
        assert line is not None
        assert "France" in line
        assert "Prussia" in line

    def test_format_ticking_oneliner(self):
        event = {
            "type": "war_objective_ticking_started",
            "declaring_nation": "France",
            "target_nation": "Prussia",
            "objective_type": "conquest",
            "target_region": "Berlin",
            "rate": 2,
            "turn": 6,
        }
        line = format_event_oneliner(event)
        assert line is not None
        assert "France" in line

    def test_war_objective_events_survive_campaign_log_filter(self):
        world = WorldState(player_nation="France")
        events = [
            {
                "type": "war_objective_declared",
                "declaring_nation": "France",
                "target_nation": "Austria",
                "objective_type": "conquest",
                "turn": 2,
            },
            {
                "type": "war_objective_ticking_started",
                "declaring_nation": "Austria",
                "target_nation": "France",
                "objective_type": "defense",
                "target_region": "Paris",
                "rate": 1,
                "turn": 3,
            },
        ]
        filtered = filter_campaign_log(events, world)
        assert [event["type"] for event in filtered] == [
            "war_objective_declared",
            "war_objective_ticking_started",
        ]


# ════════════════════════════════════════════════════════════════════════════
# 25. SETTLEMENT TIER MAPPING
# ════════════════════════════════════════════════════════════════════════════

class TestSettlementTiers:

    def test_white_peace(self):
        assert get_settlement_tier(0) == "white_peace"
        assert get_settlement_tier(19) == "white_peace"

    def test_favorable_terms(self):
        assert get_settlement_tier(20) == "favorable_terms"
        assert get_settlement_tier(39) == "favorable_terms"

    def test_dictated_terms(self):
        assert get_settlement_tier(40) == "dictated_terms"
        assert get_settlement_tier(59) == "dictated_terms"

    def test_harsh_peace(self):
        assert get_settlement_tier(60) == "harsh_peace"
        assert get_settlement_tier(79) == "harsh_peace"

    def test_total_victory(self):
        assert get_settlement_tier(80) == "total_victory"
        assert get_settlement_tier(100) == "total_victory"

    def test_negative_scores_use_absolute(self):
        assert get_settlement_tier(-50) == "dictated_terms"
        assert get_settlement_tier(-90) == "total_victory"

    def test_all_tiers_have_display(self):
        for _, tier in SETTLEMENT_TIERS:
            assert tier in SETTLEMENT_TIER_DISPLAY

    def test_all_objective_types_have_display(self):
        for otype in OBJECTIVE_TYPES:
            assert otype in OBJECTIVE_TYPE_DISPLAY

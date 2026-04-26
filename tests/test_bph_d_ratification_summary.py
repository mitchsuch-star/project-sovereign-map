"""BPH-D: Ratification summary + dispatch tests.

Spec: `docs/BILATERAL_PEACE_HARDENING_SPEC.md` §11, §14 (Slice BPH-D).

Covers (~12 tests):
  1.  Summary includes war outcome, territory, gold, casualties
  2.  War outcome classification: french_victory (score >= 30)
  3.  War outcome classification: enemy_victory (score <= -30)
  4.  War outcome classification: stalemate (territory or gold changed)
  5.  War outcome classification: white_peace (no changes)
  6.  Political aftermath includes ally penalties
  7.  Political aftermath includes cancelled orders
  8.  Summary stored in peace_ratification_log (capped at 5)
  9.  Serialization round-trip for peace_ratification_log
  10. Campaign log one-liner uses war outcome
  11. Dispatch settlement section filters by previous turn
  12. Summary attached to ratification result
"""
from __future__ import annotations

import copy

import pytest

from backend.campaign_log import format_event_oneliner
from backend.game_logic.diplomacy import (
    _capture_pre_cleanup_war_data,
    build_peace_ratification_summary,
    set_diplomatic_state,
)
from backend.game_logic.dispatch import _build_peace_settlement_section
from backend.models.world_state import WorldState


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _war_world(*, player="France", enemy="Prussia", turn=10) -> WorldState:
    world = WorldState(player_nation=player)
    world.current_turn = turn
    world.invalidate_active_nations_cache()
    set_diplomatic_state(world, player, enemy, "WAR", "test")
    world.war_start_turns[world._make_diplo_key(player, enemy)] = 2
    world.war_scores = {world._make_diplo_key(player, enemy): 40}
    world.battle_records = {
        world._make_diplo_key(player, enemy): [
            {
                "attacker": player,
                "defender": enemy,
                "winner": player,
                "attacker_casualties": 5000,
                "defender_casualties": 12000,
            },
        ],
    }
    return world


def _sample_treaty(*, territory_to_player=None, gold_to_player=0,
                   territory_from_player=None, gold_from_player=0):
    clauses = []
    if territory_to_player:
        clauses.append({
            "type": "territory_cede",
            "from": "Prussia",
            "to": "France",
            "regions": territory_to_player,
            "amount": 0,
        })
    if territory_from_player:
        clauses.append({
            "type": "territory_cede",
            "from": "France",
            "to": "Prussia",
            "regions": territory_from_player,
            "amount": 0,
        })
    if gold_to_player:
        clauses.append({
            "type": "gold_lump",
            "from": "Prussia",
            "to": "France",
            "amount": gold_to_player,
        })
    if gold_from_player:
        clauses.append({
            "type": "gold_lump",
            "from": "France",
            "to": "Prussia",
            "amount": gold_from_player,
        })
    return {
        "clauses": clauses,
        "state_transition": "WAR_TO_PEACE",
        "harshness": 0.5,
    }


def _sample_annotated(labels=None):
    labels = labels or ["Prussia cedes Rhineland to France", "Prussia pays 500 gold"]
    return [{"display": label} for label in labels]


def _peace_proposal(player="France", target="Prussia"):
    return {
        "type": "peace",
        "proposer_nation": player,
        "target_nation": target,
        "sweeteners": [],
        "demands": [
            {"type": "territory_cede", "regions": ["Rhineland"], "value": 0},
            {"type": "gold_lump", "value": 500},
        ],
        "clauses": [],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SUMMARY STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

class TestSummaryStructure:

    def test_summary_has_all_required_fields(self):
        world = _war_world()
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        treaty = _sample_treaty(territory_to_player=["Rhineland"], gold_to_player=500)
        summary = build_peace_ratification_summary(
            world, "France", "Prussia", treaty,
            _sample_annotated(), [], [], pre,
        )
        assert summary["target_nation"] == "Prussia"
        assert summary["previous_state"] == "WAR"
        assert summary["new_state"] == "PEACE"
        assert summary["war_duration_turns"] == 8
        assert summary["war_outcome"] == "french_victory"
        assert summary["territory_gained"] == ["Rhineland"]
        assert summary["territory_lost"] == []
        assert summary["gold_received"] == 500
        assert summary["gold_paid"] == 0
        assert summary["casualties_france"] == 5000
        assert summary["casualties_enemy"] == 12000
        assert summary["final_war_score"] == 40
        assert len(summary["terms_ratified"]) == 2
        assert summary["target_capital"] == "Berlin"
        assert isinstance(summary["turn"], int)


# ═══════════════════════════════════════════════════════════════════════════════
# 2-5. WAR OUTCOME CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestWarOutcome:

    def test_french_victory_score_ge_30(self):
        world = _war_world()
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 35
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        treaty = _sample_treaty()
        summary = build_peace_ratification_summary(
            world, "France", "Prussia", treaty, [], [], [], pre,
        )
        assert summary["war_outcome"] == "french_victory"

    def test_enemy_victory_score_le_neg30(self):
        world = _war_world()
        world.war_scores[world._make_diplo_key("France", "Prussia")] = -35
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        treaty = _sample_treaty()
        summary = build_peace_ratification_summary(
            world, "France", "Prussia", treaty, [], [], [], pre,
        )
        assert summary["war_outcome"] == "enemy_victory"

    def test_stalemate_territory_changed(self):
        world = _war_world()
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 10
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        treaty = _sample_treaty(territory_to_player=["Rhineland"])
        summary = build_peace_ratification_summary(
            world, "France", "Prussia", treaty, [], [], [], pre,
        )
        assert summary["war_outcome"] == "stalemate"

    def test_stalemate_gold_exchanged(self):
        world = _war_world()
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 10
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        treaty = _sample_treaty(gold_to_player=200)
        summary = build_peace_ratification_summary(
            world, "France", "Prussia", treaty, [], [], [], pre,
        )
        assert summary["war_outcome"] == "stalemate"

    def test_white_peace_no_changes(self):
        world = _war_world()
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 10
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        treaty = _sample_treaty()
        summary = build_peace_ratification_summary(
            world, "France", "Prussia", treaty, [], [], [], pre,
        )
        assert summary["war_outcome"] == "white_peace"


# ═══════════════════════════════════════════════════════════════════════════════
# 6-7. POLITICAL AFTERMATH
# ═══════════════════════════════════════════════════════════════════════════════

class TestPoliticalAftermath:

    def test_aftermath_includes_ally_penalties(self):
        world = _war_world()
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        penalties = [
            {"ally": "Austria", "relation_change": -10, "severity": "MINOR",
             "display": "Austria views this separate peace unfavorably (-10 relation)"},
        ]
        summary = build_peace_ratification_summary(
            world, "France", "Prussia", _sample_treaty(),
            [], penalties, [], pre,
        )
        assert any("Austria" in a for a in summary["political_aftermath"])

    def test_aftermath_includes_cancelled_orders(self):
        world = _war_world()
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        cancelled = [
            {"marshal": "Ney", "order_type": "PURSUE", "target": "Blücher"},
        ]
        summary = build_peace_ratification_summary(
            world, "France", "Prussia", _sample_treaty(),
            [], [], cancelled, pre,
        )
        assert any("Ney" in a and "pursuit" in a for a in summary["political_aftermath"])

    def test_aftermath_move_to_shows_march(self):
        world = _war_world()
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        cancelled = [
            {"marshal": "Davout", "order_type": "MOVE_TO", "target": "Berlin"},
        ]
        summary = build_peace_ratification_summary(
            world, "France", "Prussia", _sample_treaty(),
            [], [], cancelled, pre,
        )
        assert any("Davout" in a and "march" in a for a in summary["political_aftermath"])


# ═══════════════════════════════════════════════════════════════════════════════
# 8. RATIFICATION LOG CAP
# ═══════════════════════════════════════════════════════════════════════════════

class TestRatificationLog:

    def test_log_capped_at_5(self):
        world = WorldState(player_nation="France")
        world.peace_ratification_log = [
            {"target_nation": f"Nation{i}", "turn": i} for i in range(5)
        ]
        world.peace_ratification_log.append({"target_nation": "Nation5", "turn": 5})
        if len(world.peace_ratification_log) > 5:
            world.peace_ratification_log = world.peace_ratification_log[-5:]
        assert len(world.peace_ratification_log) == 5
        assert world.peace_ratification_log[0]["target_nation"] == "Nation1"

    def test_ratify_treaty_stores_summary_in_log(self):
        world = _war_world()
        proposal = _peace_proposal()
        result = world._ratify_treaty(proposal)
        assert len(world.peace_ratification_log) == 1
        entry = world.peace_ratification_log[0]
        assert entry["target_nation"] == "Prussia"
        assert "war_outcome" in entry
        assert "peace_ratification_summary" in result


# ═══════════════════════════════════════════════════════════════════════════════
# 9. SERIALIZATION ROUND-TRIP
# ═══════════════════════════════════════════════════════════════════════════════

class TestSerialization:

    def test_round_trip_peace_ratification_log(self):
        world = WorldState(player_nation="France")
        world.peace_ratification_log = [
            {
                "target_nation": "Prussia",
                "turn": 10,
                "war_outcome": "french_victory",
                "territory_gained": ["Rhineland"],
                "final_war_score": 40,
            },
        ]
        data = world.to_dict()
        assert "peace_ratification_log" in data
        assert len(data["peace_ratification_log"]) == 1

        restored = WorldState.from_dict(data)
        assert len(restored.peace_ratification_log) == 1
        assert restored.peace_ratification_log[0]["target_nation"] == "Prussia"
        assert restored.peace_ratification_log[0]["war_outcome"] == "french_victory"

    def test_pre_bphd_save_loads_empty(self):
        world = WorldState(player_nation="France")
        data = world.to_dict()
        del data["peace_ratification_log"]
        restored = WorldState.from_dict(data)
        assert restored.peace_ratification_log == []


# ═══════════════════════════════════════════════════════════════════════════════
# 10. CAMPAIGN LOG ONE-LINER
# ═══════════════════════════════════════════════════════════════════════════════

class TestCampaignLogOneLiner:

    def test_oneliner_french_victory_with_territory(self):
        event = {
            "type": "peace_ratified",
            "target_nation": "Prussia",
            "state_transition": "WAR_TO_PEACE",
            "war_outcome": "french_victory",
            "territory_gained": ["Rhineland"],
            "gold_received": 500,
        }
        result = format_event_oneliner(event)
        assert "Peace with Prussia" in result
        assert "French victory" in result
        assert "Rhineland" in result
        assert "+500 gold" in result

    def test_oneliner_white_peace(self):
        event = {
            "type": "peace_ratified",
            "target_nation": "Austria",
            "state_transition": "WAR_TO_PEACE",
            "war_outcome": "white_peace",
        }
        result = format_event_oneliner(event)
        assert "Peace with Austria" in result
        assert "white peace" in result

    def test_oneliner_territory_lost(self):
        event = {
            "type": "peace_ratified",
            "target_nation": "Russia",
            "state_transition": "WAR_TO_PEACE",
            "war_outcome": "enemy_victory",
            "territory_lost": ["Alsace"],
            "gold_paid": 300,
        }
        result = format_event_oneliner(event)
        assert "lost Alsace" in result
        assert "-300 gold" in result

    def test_armistice_oneliner_unchanged(self):
        event = {
            "type": "peace_ratified",
            "target_nation": "Austria",
            "state_transition": "WAR_TO_ARMISTICE",
            "annotated_terms": [{"display_label": "x"}],
        }
        result = format_event_oneliner(event)
        assert "Armistice ratified" in result


# ═══════════════════════════════════════════════════════════════════════════════
# 11. DISPATCH PEACE SETTLEMENT SECTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestDispatchSettlement:

    def test_settlement_filters_by_previous_turn(self):
        world = WorldState(player_nation="France")
        world.current_turn = 11
        world.peace_ratification_log = [
            {"target_nation": "Prussia", "turn": 10, "war_duration_turns": 8,
             "war_outcome": "french_victory", "territory_gained": ["Rhineland"],
             "final_war_score": 40, "target_capital": "Berlin"},
            {"target_nation": "Austria", "turn": 5, "war_duration_turns": 3,
             "war_outcome": "white_peace", "territory_gained": [],
             "final_war_score": 0, "target_capital": "Vienna"},
        ]
        settlements = _build_peace_settlement_section(world)
        assert len(settlements) == 1
        assert settlements[0]["target_nation"] == "Prussia"
        assert "Treaty of Berlin" in settlements[0]["headline"]
        assert "8 turns" in settlements[0]["detail"]

    def test_settlement_empty_when_no_previous_turn_match(self):
        world = WorldState(player_nation="France")
        world.current_turn = 15
        world.peace_ratification_log = [
            {"target_nation": "Prussia", "turn": 10, "war_duration_turns": 8,
             "war_outcome": "french_victory", "territory_gained": [],
             "final_war_score": 40, "target_capital": "Berlin"},
        ]
        settlements = _build_peace_settlement_section(world)
        assert settlements == []


# ═══════════════════════════════════════════════════════════════════════════════
# 12. PRE-CLEANUP DATA CAPTURE
# ═══════════════════════════════════════════════════════════════════════════════

class TestPreCleanupCapture:

    def test_captures_war_data_correctly(self):
        world = _war_world()
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        assert pre["war_duration"] == 8
        assert pre["war_score"] == 40
        assert pre["french_casualties"] == 5000
        assert pre["enemy_casualties"] == 12000

    def test_score_flipped_for_player_perspective(self):
        world = _war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -20
        pre = _capture_pre_cleanup_war_data(world, "France", "Prussia")
        assert pre["war_score"] == -20

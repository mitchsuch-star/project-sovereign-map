"""BPH-B: Peace preview panel + war context snapshot tests.

Spec: `docs/BILATERAL_PEACE_HARDENING_SPEC.md` §8, §12.1, §16 (Slice BPH-B).
Plan: `docs/PEACE_DEALS_UMBRELLA_SPEC.md` §5.

Covers (~20 tests):
  1-5.   Snapshot field correctness (all required fields populated, int types)
  6-7.   War score components match calculate_war_score
  8-9.   Battle stats aggregation (won/lost/casualties from records)
  10-11. Regions held computation
  12.    War duration from war_start_turns
  13.    War score trend (rising/falling/stagnant)
  14-15. Acceptance preview (score, outcome, largest factors)
  16.    Harshness label classification
  17.    Annotated terms carried on snapshot
  18.    Armistice-specific fields (remaining turns, cooldown)
  19.    Peace-class routing — only WAR/ARMISTICE triggers enrichment
  20.    Non-peace actions do NOT get snapshots
  21.    Forward-compat — .get() tolerates unknown keys
"""
from __future__ import annotations

import pytest

from backend.game_logic.diplomacy import (
    PEACE_CLASS_ACTIONS,
    build_war_context_snapshot,
    calculate_war_score,
    get_diplomatic_preview,
    get_harshness_label,
    get_war_score_for,
    set_diplomatic_state,
)
from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
from backend.models.world_state import WorldState


# ═══════════════════════════════════════════════════════════��════════════════
# HELPERS
# ══════���════════════════════════════════════════════════���════════════════════

def _war_world(*, player="France", enemy="Prussia", turn=5) -> WorldState:
    """Create a WorldState with an active war between player and enemy."""
    world = WorldState(player_nation=player)
    world.current_turn = turn
    set_diplomatic_state(world, player, enemy, "WAR", "test")
    world.war_start_turns[world._make_diplo_key(player, enemy)] = 1
    return world


def _add_battle_record(world, player, enemy, *, winner, attacker=None,
                       attacker_cas=500, defender_cas=300, turn=None):
    """Add a battle record between player and enemy."""
    diplo_key = world._make_diplo_key(player, enemy)
    if diplo_key not in world.battle_records:
        world.battle_records[diplo_key] = []
    if attacker is None:
        attacker = player
    defender = enemy if attacker == player else player
    world.battle_records[diplo_key].append({
        "turn": turn if turn is not None else world.current_turn,
        "winner": winner,
        "attacker": attacker,
        "defender": defender,
        "attacker_casualties": attacker_cas,
        "defender_casualties": defender_cas,
    })


def _add_decisive_battle(world, player, enemy, *, winner, turn=None):
    diplo_key = world._make_diplo_key(player, enemy)
    if diplo_key not in world.decisive_battles:
        world.decisive_battles[diplo_key] = []
    world.decisive_battles[diplo_key].append({
        "turn": turn if turn is not None else world.current_turn,
        "winner": winner,
    })


def _sample_terms():
    return {
        "type": "peace",
        "sweeteners": [{"type": "gold_per_turn", "value": 100}],
        "demands": [{"type": "gold_lump", "value": 500}],
        "clauses": ["open_borders"],
    }


# ═════════════���═════════════════════════��════════════════════════════���═══════
# 1-5. SNAPSHOT FIELD CORRECTNESS
# ══════════════════════════════════���═════════════════════════════════��═══════

class TestSnapshotFields:

    def test_snapshot_has_all_required_fields(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        required = [
            "target_nation", "current_state", "proposed_state",
            "war_score", "war_score_components", "war_score_trend",
            "war_duration_turns", "battles_fought", "battles_won", "battles_lost",
            "decisive_victories", "decisive_defeats",
            "french_casualties_total", "enemy_casualties_total",
            "regions_held_by_france", "regions_held_by_enemy",
            "france_relation", "acceptance_preview",
            "harshness", "harshness_label", "proposal_terms", "annotated_terms",
            "fallout_warnings", "commitment_conflicts",
        ]
        for field in required:
            assert field in snapshot, f"Missing field: {field}"

    def test_snapshot_values_are_int_safe(self):
        world = _war_world()
        _add_battle_record(world, "France", "Prussia", winner="France")
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        int_fields = [
            "war_score", "war_duration_turns", "battles_fought",
            "battles_won", "battles_lost", "decisive_victories",
            "decisive_defeats", "french_casualties_total",
            "enemy_casualties_total", "france_relation",
        ]
        for field in int_fields:
            assert isinstance(snapshot[field], int), f"{field} is {type(snapshot[field])}"

    def test_snapshot_target_nation(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["target_nation"] == "Prussia"

    def test_snapshot_current_state_war(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["current_state"] == "WAR"

    def test_snapshot_proposed_state_peace(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["proposed_state"] == "PEACE"

    def test_snapshot_proposed_state_armistice(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "armistice_winning")
        assert snapshot["proposed_state"] == "ARMISTICE"


# ═══════���══════════════════════════��═══════════════════════��═════════════════
# 6-7. WAR SCORE COMPONENTS
# ═════════��═════════════════════════���════════════════════════════════════════

class TestWarScoreComponents:

    def test_components_match_calculate_war_score(self):
        world = _war_world()
        _add_battle_record(world, "France", "Prussia", winner="France")
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        expected = calculate_war_score("France", "Prussia", world, return_components=True)
        assert snapshot["war_score"] == expected["total"]
        assert snapshot["war_score_components"]["territory"] == expected["territory"]
        assert snapshot["war_score_components"]["battle"] == expected["battles"]
        assert snapshot["war_score_components"]["decisive_battle"] == expected["decisive"]
        assert snapshot["war_score_components"]["capital"] == expected["capital"]

    def test_war_score_components_all_int(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        for key, val in snapshot["war_score_components"].items():
            assert isinstance(val, int), f"Component {key} is {type(val)}"


# ══��══════════════════════════════════════════════════════════════════���══════
# 8-9. BATTLE STATS AGGREGATION
# ��══════════════════��════════════════════════════════════════════════════════

class TestBattleStats:

    def test_battles_won_lost_count(self):
        world = _war_world()
        _add_battle_record(world, "France", "Prussia", winner="France")
        _add_battle_record(world, "France", "Prussia", winner="France")
        _add_battle_record(world, "France", "Prussia", winner="Prussia")
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["battles_won"] == 2
        assert snapshot["battles_lost"] == 1
        assert snapshot["battles_fought"] == 3

    def test_casualties_aggregation(self):
        world = _war_world()
        _add_battle_record(world, "France", "Prussia", winner="France",
                           attacker="France", attacker_cas=1000, defender_cas=2000)
        _add_battle_record(world, "France", "Prussia", winner="Prussia",
                           attacker="Prussia", attacker_cas=800, defender_cas=1500)
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["french_casualties_total"] == 1000 + 1500
        assert snapshot["enemy_casualties_total"] == 2000 + 800


# ══════════════════════════════════════════════════════════════════��═════════
# 10-11. REGIONS HELD
# ═══════════════════════════════════��═════════════════════════════════���══════

class TestRegionsHeld:

    def test_regions_held_by_france(self):
        world = _war_world()
        prussian_starting = world.nation_starting_regions.get("Prussia", [])
        if prussian_starting:
            target_region = prussian_starting[0]
            world.regions[target_region].controller = "France"
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        if prussian_starting:
            assert target_region in snapshot["regions_held_by_france"]

    def test_regions_held_by_enemy(self):
        world = _war_world()
        french_starting = world.nation_starting_regions.get("France", [])
        if french_starting:
            target_region = french_starting[0]
            world.regions[target_region].controller = "Prussia"
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        if french_starting:
            assert target_region in snapshot["regions_held_by_enemy"]


# ═══════════════════════════════��══════════════════════��═════════════════════
# 12. WAR DURATION
# ══════════════════════════════��═════════════════════════════════════════════

class TestWarDuration:

    def test_war_duration_calculation(self):
        world = _war_world(turn=10)
        dk = world._make_diplo_key("France", "Prussia")
        world.war_start_turns[dk] = 3
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["war_duration_turns"] == 7


# ════════════��════════════════════════���══════════════════════════════════════
# 13. WAR SCORE TREND
# ═══════════════════════════════════════════════════════════════���════════════

class TestWarScoreTrend:

    def test_trend_rising(self):
        world = _war_world()
        dk = world._make_diplo_key("France", "Prussia")
        world.previous_war_scores[dk] = -10
        world.war_scores[dk] = 5
        _add_battle_record(world, "France", "Prussia", winner="France")
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["war_score_trend"] == "rising"

    def test_trend_stagnant_no_change(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["war_score_trend"] == "stagnant"

    def test_trend_uses_three_turn_history_when_available(self):
        world = _war_world()
        dk = world._make_diplo_key("France", "Prussia")
        world.war_score_history[dk] = [12, 8, 4]
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["war_score_trend"] == "falling"


# ═══════════════════════════════════════════════════��════════════════════��═══
# 14-15. ACCEPTANCE PREVIEW
# ═════════════════════════════════════════��══════════════════════════════════

class TestAcceptancePreview:

    def test_acceptance_preview_structure(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace", terms=_sample_terms())
        ap = snapshot["acceptance_preview"]
        assert "score" in ap
        assert "outcome" in ap
        assert "largest_positive" in ap
        assert "largest_negative" in ap
        assert isinstance(ap["score"], int)

    def test_acceptance_outcome_is_string(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace", terms=_sample_terms())
        assert snapshot["acceptance_preview"]["outcome"] in ("ACCEPT", "COUNTER", "REJECT")

    def test_counter_offer_outcome_is_normalized_for_preview(self):
        world = _war_world(turn=5)
        dk = world._make_diplo_key("France", "Prussia")
        world.war_start_turns[dk] = 1
        terms = {"type": "peace", "sweeteners": [], "demands": [], "clauses": []}
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace", terms=terms)
        assert snapshot["acceptance_preview"]["outcome"] == "COUNTER"


# ════════��═════════════════════════════════════════════════════��═════════════
# 16. HARSHNESS LABEL
# ════════════════════════════════════��════════════════════════════════��══════

class TestHarshnessLabel:

    @pytest.mark.parametrize("harshness,expected", [
        (0.0, "generous"),
        (0.05, "generous"),
        (0.10, "balanced"),
        (0.20, "balanced"),
        (0.25, "harsh"),
        (0.45, "harsh"),
        (0.50, "punitive"),
        (1.0, "punitive"),
    ])
    def test_harshness_label_thresholds(self, harshness, expected):
        assert get_harshness_label(harshness) == expected

    def test_snapshot_harshness_label_present(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace", terms=_sample_terms())
        assert snapshot["harshness_label"] in ("generous", "balanced", "harsh", "punitive")


# ════════════════════════════════════════��═══════════════════════════════════
# 17. ANNOTATED TERMS ON SNAPSHOT
# ═��══════════════════════════════════════════════════════════════════════════

class TestAnnotatedTerms:

    def test_annotated_terms_carried_on_snapshot(self):
        world = _war_world()
        terms = _sample_terms()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace", terms=terms)
        annotated = snapshot["annotated_terms"]
        assert isinstance(annotated, list)
        assert len(annotated) >= 2
        for t in annotated:
            assert "clause_type" in t
            assert "display_label" in t
            assert "term_direction" in t

    def test_proposal_terms_are_carried_exactly_on_snapshot(self):
        world = _war_world()
        terms = _sample_terms()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace", terms=terms)
        assert snapshot["proposal_terms"] == terms

    def test_confirmation_dialogue_snapshot_uses_execute_option_terms(self):
        world = _war_world()
        terms = _sample_terms()
        dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "options": [{"action": "execute_proposal", "terms": terms}],
            "context": {"proposal_type": "peace"},
        }
        enriched = _enrich_proposal_summary(dialogue, "Prussia", "peace", world)
        assert enriched["war_context_snapshot"]["proposal_terms"] == terms


# ══════════════════════════════════════��═════════════════════════════════════
# 18. ARMISTICE-SPECIFIC FIELDS
# ═════════════════════��══════════════════════════════��═══════════════════════

class TestArmisticeFields:

    def test_armistice_remaining_turns(self):
        world = _war_world()
        set_diplomatic_state(world, "France", "Prussia", "ARMISTICE", "ceasefire")
        dk = world._make_diplo_key("France", "Prussia")
        world.armistice_turns[dk] = 2
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace")
        assert "armistice_remaining_turns" in snapshot
        assert snapshot["armistice_remaining_turns"] == 3  # 5 - 2

    def test_armistice_cooldown_flag(self):
        world = _war_world()
        set_diplomatic_state(world, "France", "Prussia", "ARMISTICE", "ceasefire")
        dk = world._make_diplo_key("France", "Prussia")
        world.armistice_cooldowns[dk] = 3
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace")
        assert snapshot["armistice_cooldown_active"] is True

    def test_war_state_has_no_armistice_fields(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace")
        assert "armistice_remaining_turns" not in snapshot


# ══════════��════════════════════��══════════════════════════════════════���═════
# 19-20. PEACE-CLASS ROUTING IN PREVIEW ENDPOINT
# ════��═══════════════════════════════════════════════════════════���═══════════

class TestPeaceClassRouting:

    def test_war_state_includes_war_context_snapshots(self):
        world = _war_world()
        preview = get_diplomatic_preview(world, "Prussia")
        has_peace_action = any(
            a["action"] in PEACE_CLASS_ACTIONS and a.get("available")
            for a in preview.get("actions", [])
        )
        if has_peace_action:
            assert "war_context_snapshots" in preview
            snapshots = preview["war_context_snapshots"]
            assert isinstance(snapshots, dict)
            for key in snapshots:
                assert key in PEACE_CLASS_ACTIONS
                assert "proposal_terms" in snapshots[key]
                assert "annotated_terms" in snapshots[key]

    def test_non_war_state_has_no_snapshots(self):
        world = WorldState(player_nation="France")
        dk = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[dk] = "PEACE"
        preview = get_diplomatic_preview(world, "Prussia")
        assert "war_context_snapshots" not in preview

    def test_peace_class_actions_constant(self):
        assert "propose_armistice" in PEACE_CLASS_ACTIONS
        assert "propose_peace" in PEACE_CLASS_ACTIONS
        assert "propose_alliance" not in PEACE_CLASS_ACTIONS


# ════���══════════════════════��════════════════════════════════���═══════════════
# 21. FORWARD COMPATIBILITY
# ═════��═════════════════════���═════════════════════════════════���══════════════

class TestForwardCompatibility:

    def test_wpsd_fields_present_in_snapshot(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace")
        assert snapshot.get("war_objective") is None
        assert snapshot["settlement_tier"] == "white_peace"
        assert snapshot["tier_mismatch_warnings"] == []

    def test_fallout_and_conflicts_empty_for_now(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace")
        assert snapshot["fallout_warnings"] == []
        assert snapshot["commitment_conflicts"] == []

    def test_war_score_history_serializes_for_trend_preview(self):
        world = _war_world()
        dk = world._make_diplo_key("France", "Prussia")
        world.war_score_history[dk] = [1, 4, 7]
        restored = WorldState.from_dict(world.to_dict())
        assert restored.war_score_history[dk] == [1, 4, 7]


# ══���══════════════════════════��══════════════════════════════════════════════
# DECISIVE BATTLE STATS
# ═════════════════════════════════��══════════════════════════════��═══════════

class TestDecisiveBattles:

    def test_decisive_victories_and_defeats(self):
        world = _war_world()
        _add_decisive_battle(world, "France", "Prussia", winner="France")
        _add_decisive_battle(world, "France", "Prussia", winner="Prussia")
        _add_decisive_battle(world, "France", "Prussia", winner="France")
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["decisive_victories"] == 2
        assert snapshot["decisive_defeats"] == 1

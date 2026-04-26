"""BPH-C: Fallout preview + commitment conflicts tests.

Spec: `docs/BILATERAL_PEACE_HARDENING_SPEC.md` §9, §10, §16 (Slice BPH-C).

Covers (~20 tests):
  1-3.   Ally fallout detection (ally at war with target triggers warning)
  4-5.   Severity bands (MINOR / MAJOR / SEVERE)
  6-7.   Harshness scaling (generous peace doubles penalty)
  8.     No ally = no fallout warnings
  9.     Ally at peace with target = no warning
  10.    Penalty application on ratification
  11.    Penalty isolation (only allies still at war with target)
  12-13. Paradox conflict detection
  14.    Bloc-opposition conflict detection
  15.    No paradox when ally not at war with target
  16.    Strategic order cancellation preview (PURSUE)
  17.    Strategic order cancellation preview (MOVE_TO region)
  18.    No cancellation when no matching orders
  19.    Full snapshot integration (fallout + conflicts populated)
  20.    Warning priority order in snapshot
  21.    Overflow cap (>3 warnings)
"""
from __future__ import annotations

import pytest

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.diplomacy import (
    _compute_separate_peace_penalty,
    _get_order_cancellation_preview,
    apply_separate_peace_penalties,
    build_war_context_snapshot,
    get_peace_commitment_conflicts,
    get_separate_peace_fallout_warnings,
    set_diplomatic_state,
)
from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════���═══════════════════════════════════════════════════��═════════════════════

def _war_world(*, player="France", enemy="Prussia", turn=10,
               extra_nations=None) -> WorldState:
    """Create a WorldState with an active war between player and enemy."""
    world = WorldState(player_nation=player)
    world.current_turn = turn
    if extra_nations:
        existing = set(getattr(world, 'enemy_nations', []))
        existing.update(extra_nations)
        world.enemy_nations = list(existing)
    world.invalidate_active_nations_cache()
    set_diplomatic_state(world, player, enemy, "WAR", "test")
    world.war_start_turns[world._make_diplo_key(player, enemy)] = 1
    return world


def _add_ally_at_war(world, player, ally, enemy, *, ally_war_start=1,
                     ally_state="ALLIANCE", casualties=0, battles=None):
    """Add an allied nation that is also at war with the same enemy."""
    set_diplomatic_state(world, player, ally, ally_state, "test_alliance")
    set_diplomatic_state(world, ally, enemy, "WAR", "test_war")
    target_key = world._make_diplo_key(ally, enemy)
    world.war_start_turns[target_key] = ally_war_start
    if casualties > 0 or battles:
        if not hasattr(world, 'battle_records'):
            world.battle_records = {}
        records = battles or [{
            "attacker": ally,
            "defender": enemy,
            "winner": ally,
            "attacker_casualties": casualties,
            "defender_casualties": 0,
        }]
        world.battle_records[target_key] = records


def _make_marshal_with_order(world, name, nation, location, *,
                             order_type="PURSUE", target_type="marshal",
                             target_name="Blucher"):
    """Create a marshal with a strategic order for testing cancellation preview."""
    from backend.models.marshal import Marshal
    m = Marshal(name=name, location=location, strength=10000,
                personality="aggressive", nation=nation)

    class _FakeOrder:
        def __init__(self, cmd, ttype, tname):
            self.command_type = cmd
            self.target_type = ttype
            self.target = tname

    m.strategic_order = _FakeOrder(order_type, target_type, target_name)
    world.marshals[name] = m
    return m


# ══════��═══════════════════���════════════════════════════════════════════════════
# TEST: Ally Fallout Detection
# ═══════════════════════════════════════════════���═══════════════════════════════

class TestAllyFalloutDetection:
    def test_ally_at_war_triggers_warning(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        warnings = get_separate_peace_fallout_warnings(world, "France", "Prussia", 0.4)
        assert len(warnings) == 1
        assert warnings[0]["ally"] == "Austria"
        assert warnings[0]["warning_type"] == "separate_peace_ally"
        assert "Austria" in warnings[0]["display"]

    def test_multiple_allies_at_war(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        _add_ally_at_war(world, "France", "Britain", "Prussia", ally_state="DEFENSIVE_ALLIANCE")
        warnings = get_separate_peace_fallout_warnings(world, "France", "Prussia", 0.4)
        allies = {w["ally"] for w in warnings}
        assert allies == {"Austria", "Britain"}

    def test_defensive_alliance_triggers_warning(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia",
                         ally_state="DEFENSIVE_ALLIANCE")
        warnings = get_separate_peace_fallout_warnings(world, "France", "Prussia", 0.4)
        assert len(warnings) == 1

    def test_no_ally_no_warnings(self):
        world = _war_world()
        warnings = get_separate_peace_fallout_warnings(world, "France", "Prussia", 0.4)
        assert warnings == []

    def test_ally_at_peace_with_target_no_warning(self):
        world = _war_world()
        set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "test")
        # Austria NOT at war with Prussia
        warnings = get_separate_peace_fallout_warnings(world, "France", "Prussia", 0.4)
        assert warnings == []


# ═══��═══════════════════════════════════════════════════════════════════════════
# TEST: Severity Bands
# ═══════════════════════════���═══════════════════════════════════════════════════

class TestSeverityBands:
    def test_minor_ally_winning(self):
        """Ally winning (war_score > 20) → MINOR, -5 relation."""
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        dk = world._make_diplo_key("Austria", "Prussia")
        if not hasattr(world, 'war_scores'):
            world.war_scores = {}
        world.war_scores[dk] = 30
        warnings = get_separate_peace_fallout_warnings(world, "France", "Prussia", 0.4)
        assert len(warnings) == 1
        assert warnings[0]["severity"] == "MINOR"
        assert warnings[0]["predicted_relation_change"] == -5

    def test_major_ally_losing(self):
        """Ally losing or neutral (war_score ≤ 20) → MAJOR, -10 relation."""
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        warnings = get_separate_peace_fallout_warnings(world, "France", "Prussia", 0.4)
        assert len(warnings) == 1
        assert warnings[0]["severity"] == "MAJOR"
        assert warnings[0]["predicted_relation_change"] == -10

    def test_severe_long_costly_war(self):
        """Ally in 5+ turn war with >5000 casualties → SEVERE, -15 relation."""
        world = _war_world(turn=10)
        _add_ally_at_war(world, "France", "Austria", "Prussia",
                         ally_war_start=1, casualties=6000)
        warnings = get_separate_peace_fallout_warnings(world, "France", "Prussia", 0.4)
        assert len(warnings) == 1
        assert warnings[0]["severity"] == "SEVERE"
        assert warnings[0]["predicted_relation_change"] == -15


# ═════════════════════════════════════════════════════════��═════════════════════
# TEST: Harshness Scaling
# ══════════════════════════��══════════════════════════��═════════════════════════

class TestHarshnessScaling:
    def test_generous_peace_doubles_penalty(self):
        """Harshness < 0.2 doubles the base penalty."""
        penalty = _compute_separate_peace_penalty(
            ally_war_score=0, ally_war_turns=3,
            ally_casualties=0, harshness=0.1,
        )
        assert penalty == -20  # -10 base doubled

    def test_harsh_peace_no_doubling(self):
        """Harshness >= 0.2 does not double."""
        penalty = _compute_separate_peace_penalty(
            ally_war_score=0, ally_war_turns=3,
            ally_casualties=0, harshness=0.5,
        )
        assert penalty == -10

    def test_generous_severe_penalty(self):
        """Generous peace with severe conditions: -15 * 2 = -30."""
        penalty = _compute_separate_peace_penalty(
            ally_war_score=-10, ally_war_turns=8,
            ally_casualties=10000, harshness=0.1,
        )
        assert penalty == -30


# ═══════════════════════════���════════════════════════════════��══════════════════
# TEST: Penalty Application on Ratification
# ════════════════════════════════════════���══════════════════════════════════════

class TestPenaltyApplication:
    def test_penalty_applied_to_relation(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        ally_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[ally_key] = 50
        applied = apply_separate_peace_penalties(world, "France", "Prussia", 0.4)
        assert len(applied) == 1
        assert applied[0]["ally"] == "Austria"
        assert world.nation_relations[ally_key] == 40  # 50 + (-10)

    def test_penalty_isolation_only_affected_allies(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        set_diplomatic_state(world, "France", "Britain", "ALLIANCE", "test")
        # Britain NOT at war with Prussia → should be unaffected
        britain_key = world._make_diplo_key("France", "Britain")
        world.nation_relations[britain_key] = 50
        apply_separate_peace_penalties(world, "France", "Prussia", 0.4)
        assert world.nation_relations[britain_key] == 50  # unchanged


# ═══════════���════════════════════════════════════════════���══════════════════════
# TEST: Commitment Conflict Detection
# ═══════════════════���═══════════════════════════════════════════════════════════

class TestCommitmentConflicts:
    def test_paradox_detected(self):
        """Allied with Austria, Austria at war with Prussia → paradox."""
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        conflicts = get_peace_commitment_conflicts(world, "France", "Prussia", [])
        paradox = [c for c in conflicts if c["conflict_type"] == "paradox"]
        assert len(paradox) == 1
        assert paradox[0]["affected_entity"] == "Austria"
        assert paradox[0]["severity"] == "HARD_STOP"

    def test_paradox_blocks_player_send_before_dp_spend(self):
        """HARD_STOP paradox conflicts block proposal send instead of only warning."""
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        world.diplomatic_points = 10
        terms = {"type": "peace", "sweeteners": [], "demands": [], "clauses": []}
        world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "options": [{"label": "Send", "action": "execute_proposal", "terms": terms}],
            "context": {},
            "turn_created": int(world.current_turn),
            "blocking": False,
        })

        result = DiplomaticExecutor(None).handle_diplomatic_dialogue_response(
            "send", {"world": world},
        )

        assert result["success"] is False
        assert "diplomatic contradiction" in result["message"]
        assert world.proposal_in_transit is None
        assert world.diplomatic_points == 10

    def test_no_paradox_when_ally_not_at_war(self):
        """Allied with Austria, Austria NOT at war with Prussia → no paradox."""
        world = _war_world()
        set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "test")
        conflicts = get_peace_commitment_conflicts(world, "France", "Prussia", [])
        paradox = [c for c in conflicts if c["conflict_type"] == "paradox"]
        assert len(paradox) == 0

    def test_bloc_opposition_detected(self):
        """Proposer in bloc, target outside bloc → INFO warning."""
        world = _war_world()
        from unittest.mock import patch
        with patch("backend.game_logic.coalition._identify_max_bloc_share",
                   return_value=("France", 0.45)):
            with patch.object(world, "get_bloc_members", return_value=["France", "Saxony"]):
                conflicts = get_peace_commitment_conflicts(
                    world, "France", "Prussia", [],
                )
        bloc = [c for c in conflicts if c["conflict_type"] == "bloc_opposition"]
        assert len(bloc) == 1
        assert bloc[0]["severity"] == "INFO"
        assert "Prussia" in bloc[0]["display"]

    def test_no_bloc_opposition_when_target_in_bloc(self):
        """Both in the same bloc → no opposition warning."""
        from unittest.mock import patch
        world = _war_world()
        with patch("backend.game_logic.coalition._identify_max_bloc_share",
                   return_value=("France", 0.50)):
            with patch.object(world, "get_bloc_members",
                              return_value=["France", "Prussia"]):
                conflicts = get_peace_commitment_conflicts(
                    world, "France", "Prussia", [],
                )
        bloc = [c for c in conflicts if c["conflict_type"] == "bloc_opposition"]
        assert len(bloc) == 0


# ════════��══════════════════════════════════════════════════════════════════════
# TEST: Strategic Order Cancellation Preview
# ═══════════════════════════════════════════════════════════════��═══════════════

class TestOrderCancellationPreview:
    def test_pursue_order_detected(self):
        world = _war_world()
        _make_marshal_with_order(world, "Ney", "France", "Berlin",
                                 order_type="PURSUE", target_type="marshal",
                                 target_name="Blucher")
        from backend.models.marshal import Marshal
        enemy_m = Marshal(name="Blucher", location="Brandenburg", strength=8000,
                          personality="aggressive", nation="Prussia")
        world.marshals["Blucher"] = enemy_m

        result = _get_order_cancellation_preview(world, "France", "Prussia")
        assert result is not None
        assert result["warning_type"] == "order_cancellation"
        assert len(result["orders"]) == 1
        assert "pursuit" in result["display"].lower()

    def test_move_to_region_detected(self):
        world = _war_world()
        if not hasattr(world, 'nation_starting_regions'):
            world.nation_starting_regions = {}
        world.nation_starting_regions["Prussia"] = ["Brandenburg", "Berlin"]
        _make_marshal_with_order(world, "Davout", "France", "Rhineland",
                                 order_type="MOVE_TO", target_type="region",
                                 target_name="Brandenburg")
        result = _get_order_cancellation_preview(world, "France", "Prussia")
        assert result is not None
        assert "Davout's march on Brandenburg" in result["display"]

    def test_move_to_region_preview_matches_cleanup(self):
        """Region MOVE_TO orders shown in preview are actually cancelled on peace."""
        world = _war_world()
        marshal = next(m for m in world.marshals.values() if m.nation == "France")
        target_region = world.get_nation_regions("Prussia")[0]
        marshal.strategic_order = StrategicOrder(
            command_type="MOVE_TO",
            target=target_region,
            target_type="region",
            started_turn=int(world.current_turn),
            original_command="march on target",
        )

        result = _get_order_cancellation_preview(world, "France", "Prussia")
        assert result is not None
        assert result["orders"][0]["target"] == target_region

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
        })
        assert marshal.strategic_order is None

    def test_no_cancellation_no_matching_orders(self):
        world = _war_world()
        result = _get_order_cancellation_preview(world, "France", "Prussia")
        assert result is None


# ═══════���══════════════════��═════════════════════════════���══════════════════════
# TEST: Full Snapshot Integration
# ═══════════════���══════════════════════════════════���════════════════════════════

class TestSnapshotIntegration:
    def test_snapshot_populates_fallout_warnings(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert len(snapshot["fallout_warnings"]) >= 1
        w = snapshot["fallout_warnings"][0]
        assert w["ally"] == "Austria"
        assert "display" in w

    def test_snapshot_populates_commitment_conflicts(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        paradox = [c for c in snapshot["commitment_conflicts"]
                   if c["conflict_type"] == "paradox"]
        assert len(paradox) == 1

    def test_snapshot_empty_when_no_allies_or_conflicts(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        assert snapshot["fallout_warnings"] == []
        assert snapshot["commitment_conflicts"] == []

    def test_armistice_snapshot_has_no_relation_fallout(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        snapshot = build_war_context_snapshot(world, "France", "Prussia", "armistice")
        fallout_types = {w.get("warning_type") for w in snapshot["fallout_warnings"]}
        assert "separate_peace_ally" not in fallout_types

    def test_order_cancellation_appears_in_fallout(self):
        world = _war_world()
        _make_marshal_with_order(world, "Ney", "France", "Berlin",
                                 order_type="PURSUE", target_type="marshal",
                                 target_name="Blucher")
        from backend.models.marshal import Marshal
        enemy = Marshal(name="Blucher", location="Brandenburg", strength=8000,
                        personality="aggressive", nation="Prussia")
        world.marshals["Blucher"] = enemy

        snapshot = build_war_context_snapshot(world, "France", "Prussia", "peace")
        order_warnings = [w for w in snapshot["fallout_warnings"]
                          if w.get("warning_type") == "order_cancellation"]
        assert len(order_warnings) == 1


class TestRatificationEdgeCases:
    def test_war_to_armistice_does_not_apply_separate_peace_penalty(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        ally_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[ally_key] = 50

        world._ratify_treaty({
            "type": "armistice",
            "proposer_nation": "France",
            "target_nation": "Prussia",
        })

        assert world.get_diplomatic_state("France", "Prussia") == "ARMISTICE"
        assert world.nation_relations[ally_key] == 50

    def test_accepting_incoming_ai_peace_penalizes_france_allies(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        ally_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[ally_key] = 50
        dialogue = {
            "type": "incoming_proposal",
            "context": {
                "source_nation": "Prussia",
                "proposal": {
                    "type": "peace",
                    "proposer_nation": "Prussia",
                    "target_nation": "France",
                },
            },
        }
        world.dialogue_manager.replace(dialogue)

        result = DiplomaticExecutor(None)._handle_accept_ai_proposal(dialogue, world)

        assert result["success"] is True
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE"
        assert world.nation_relations[ally_key] == 30

    def test_incoming_ai_peace_preview_uses_france_fallout_orientation(self):
        world = _war_world()
        _add_ally_at_war(world, "France", "Austria", "Prussia")
        popup = build_pending_envoy_popup_from_terms(
            world,
            nation="Prussia",
            terms={
                "type": "peace",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
        )

        fallout = popup["war_context_snapshot"]["fallout_warnings"]
        assert any(w.get("ally") == "Austria" for w in fallout)


class TestGodotWarningPriority:
    def test_peace_preview_sorts_consequences_before_overflow_cap(self):
        from pathlib import Path

        source = Path(
            "godot-client/project-sovereign/scripts/proposal_confirm_popup.gd",
        ).read_text()

        assert "consequence_items.sort_custom" in source
        assert 'sev == "HARD_STOP"' in source

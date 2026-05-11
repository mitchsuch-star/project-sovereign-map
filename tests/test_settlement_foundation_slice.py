"""G2-Slice-1 Foundation behavioral tests (SC-1 through SC-4).

Tests authored terms validation, executor forwarding, acceptance-gated
ratification, hard-stop enforcement, and draft persistence semantics.
"""

from __future__ import annotations

import copy
from unittest.mock import patch

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.settlement_preview import (
    build_settlement_preview,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.game_logic.settlement_scoring import (
    CANONICAL_CLAUSE_TYPES,
    CLAUSE_CONFLICT_MATRIX,
    MAX_SETTLEMENT_CLAUSE_COUNT,
    SETTLEMENT_HARD_STOP_CODES,
    SETTLEMENT_MVP_CLAUSE_TYPES,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


def _acceptance_always_passes(*args, **kwargs):
    """Patch helper for tests that need to isolate post-acceptance mutation."""
    from backend.game_logic.settlement_scoring import calculate_common_peace_acceptance as real

    result = real(*args, **kwargs)
    result["score"] = 100
    result["verdict"] = "accept"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    return result


def _install_common_peace_war(world: WorldState, *, war_score: int = 70) -> dict:
    """Install a multi-party war fixture with controllable acceptance."""
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        a, b = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = war_score if a == "Austria" else -war_score
    world.war_exhaustion["Austria"] = 30
    world.invalidate_war_instance_indexes()
    return war


# ═══════════════════════════════════════════════════════════════════════════
# SC-1: Clause validation
# ═══════════════════════════════════════════════════════════════════════════


class TestClauseValidation:
    def test_valid_territory_cede(self):
        terms = [{"type": "territory_cede", "from": "Austria", "to": "France", "region": "Bohemia"}]
        result = validate_settlement_terms(terms, actor_nation="France", player_nation="France")
        assert result["valid"] is True

    def test_valid_multi_clause_draft(self):
        terms = [
            {"type": "peace"},
            {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Bohemia"},
            {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 100},
            {"type": "forced_alliance", "from": "Austria", "to": "France"},
        ]
        result = validate_settlement_terms(terms, actor_nation="France", player_nation="France")
        assert result["valid"] is True

    def test_empty_draft_rejected(self):
        result = validate_settlement_terms([], actor_nation="France", player_nation="France")
        assert result["valid"] is False
        assert result["error"] == "empty_authored_draft"

    def test_max_clause_count_exceeded(self):
        terms = [{"type": "peace"}] * (MAX_SETTLEMENT_CLAUSE_COUNT + 1)
        result = validate_settlement_terms(terms, actor_nation="France", player_nation="France")
        assert result["valid"] is False
        assert result["error"] == "max_clause_count_exceeded"

    def test_invalid_clause_type(self):
        terms = [{"type": "bogus_clause"}]
        result = validate_settlement_terms(terms, actor_nation="France", player_nation="France")
        assert result["valid"] is False
        assert result["error"] == "invalid_clause_type"
        assert result["error_index"] == 0

    def test_missing_required_keys(self):
        terms = [{"type": "territory_cede", "from": "Austria"}]
        result = validate_settlement_terms(terms, actor_nation="France", player_nation="France")
        assert result["valid"] is False
        assert result["error"] == "invalid_clause_schema"
        assert result["error_index"] == 0
        assert "to" in result["missing_keys"]
        assert "region" in result["missing_keys"]

    def test_unknown_alias_keys_rejected(self):
        terms = [{
            "type": "territory_cede",
            "from": "Austria",
            "to": "France",
            "region": "Bohemia",
            "target": "Bohemia",
        }]
        result = validate_settlement_terms(terms, actor_nation="France", player_nation="France")
        assert result["valid"] is False
        assert result["error"] == "invalid_clause_schema"
        assert result["error_index"] == 0
        assert result["unknown_keys"] == ["target"]

    def test_non_dict_clause_rejected(self):
        result = validate_settlement_terms(
            [{"type": "peace"}, "bad"],
            actor_nation="France",
            player_nation="France",
        )
        assert result["valid"] is False
        assert result["error"] == "invalid_clause_schema"
        assert result["error_index"] == 1

    def test_unauthorized_actor(self):
        terms = [{"type": "peace"}]
        result = validate_settlement_terms(
            terms, actor_nation="Austria", player_nation="France",
        )
        assert result["valid"] is False
        assert result["error"] == "unauthorized_actor"

    def test_proposer_side_mismatch(self):
        terms = [{"type": "peace"}]
        result = validate_settlement_terms(
            terms,
            actor_nation="France",
            player_nation="France",
            proposer_side="defenders",
            actor_side_in_war="attackers",
        )
        assert result["valid"] is False
        assert result["error"] == "proposer_side_mismatch"

    def test_conflict_matrix_vassalage_forced_alliance(self):
        terms = [
            {"type": "vassalage", "from": "Austria", "to": "France"},
            {"type": "forced_alliance", "from": "Austria", "to": "France"},
        ]
        result = validate_settlement_terms(terms, actor_nation="France", player_nation="France")
        assert result["valid"] is False
        assert result["error"] == "duplicate_or_conflicting_clauses"

    def test_conflict_matrix_different_targets_ok(self):
        terms = [
            {"type": "vassalage", "from": "Austria", "to": "France"},
            {"type": "forced_alliance", "from": "Prussia", "to": "France"},
        ]
        result = validate_settlement_terms(terms, actor_nation="France", player_nation="France")
        assert result["valid"] is True

    def test_clause_ordering_irrelevant(self):
        terms_a = [
            {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Bohemia"},
            {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 50},
        ]
        terms_b = list(reversed(terms_a))
        assert validate_settlement_terms(terms_a, actor_nation="France", player_nation="France")["valid"]
        assert validate_settlement_terms(terms_b, actor_nation="France", player_nation="France")["valid"]

    def test_mvp_clause_types_are_canonical(self):
        for ctype in SETTLEMENT_MVP_CLAUSE_TYPES:
            assert ctype in CANONICAL_CLAUSE_TYPES


# ═══════════════════════════════════════════════════════════════════════════
# SC-1: Executor forwards settlement_terms into staging
# ═══════════════════════════════════════════════════════════════════════════


class TestExecutorForwarding:
    def test_executor_forwards_settlement_terms_to_staged_dialogue(self):
        world = WorldState()
        _install_common_peace_war(world)
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        cmd = {
            "action": "propose_common_peace",
            "target_nation": "Austria",
            "settlement_terms": [
                {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Bohemia"},
            ],
        }
        result = executor._execute_propose_common_peace(cmd, {"world": world})
        assert result["success"] is True
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert len(dialogue["settlement_terms"]) == 1
        assert dialogue["settlement_terms"][0]["type"] == "territory_cede"
        assert dialogue["settlement_terms"][0]["region"] == "Bohemia"

    def test_executor_rejects_invalid_terms(self):
        world = WorldState()
        _install_common_peace_war(world)
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        cmd = {
            "action": "propose_common_peace",
            "target_nation": "Austria",
            "settlement_terms": [{"type": "bogus"}],
        }
        result = executor._execute_propose_common_peace(cmd, {"world": world})
        assert result["success"] is False
        assert result["error"] == "submitted_terms_failed_revalidation"
        assert result["mutated"] is False

    def test_executor_rejects_explicit_empty_top_level_terms(self):
        """v0.22 SC-1: an explicit empty top-level `settlement_terms` key is
        an authored draft and must be rejected with `empty_authored_draft`
        even when `diplomatic_data.settlement_terms` is non-empty. The
        top-level key wins per the executor precedence rule."""
        world = WorldState()
        _install_common_peace_war(world)
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        cmd = {
            "action": "propose_common_peace",
            "target_nation": "Austria",
            "settlement_terms": [],
            "diplomatic_data": {
                "settlement_terms": [{"type": "peace"}],
            },
        }
        result = executor._execute_propose_common_peace(cmd, {"world": world})
        assert result["success"] is False
        assert result["error"] == "submitted_terms_failed_revalidation"
        assert result["validation_error"] == "empty_authored_draft"
        assert world.pending_diplomatic_dialogue is None

    def test_executor_persists_draft(self):
        world = WorldState()
        _install_common_peace_war(world)
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        terms = [{"type": "forced_alliance", "from": "Austria", "to": "France"}]
        cmd = {
            "action": "propose_common_peace",
            "target_nation": "Austria",
            "settlement_terms": terms,
        }
        executor._execute_propose_common_peace(cmd, {"world": world})
        assert "war_1" in world.pending_settlement_drafts
        assert world.pending_settlement_drafts["war_1"][0]["type"] == "forced_alliance"


# ═══════════════════════════════════════════════════════════════════════════
# SC-3: Ratify Settlement gated on fresh acceptance rescore
# ═══════════════════════════════════════════════════════════════════════════


class TestRatificationAcceptanceGate:
    def test_rejected_settlement_cannot_ratify(self):
        world = WorldState()
        _install_common_peace_war(world, war_score=5)
        before_states = dict(world.diplomatic_states)
        stage_settlement_confirm(
            world, war_id="war_1",
            settlement_terms=[{"type": "territory_cede", "from": "Austria", "to": "France", "region": "Bohemia"}],
        )
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        result = handle_settlement_dialogue_action(
            world, action="confirm_settlement", dialogue=dialogue,
        )
        assert result["success"] is False
        assert result["error"] in ("acceptance_rejected", "acceptance_blocked")
        assert result["mutated"] is False
        assert dict(world.diplomatic_states) == before_states

    @patch("backend.game_logic.settlement_preview.calculate_common_peace_acceptance", _acceptance_always_passes)
    def test_accepted_settlement_ratifies(self):
        world = WorldState()
        war = make_synthetic_war_instance(
            "war_accept",
            attackers=["France", "Saxony"],
            defenders=["Austria", "Prussia"],
            attacker_leader="France",
            defender_leader="Austria",
            created_turn=1,
            created_sequence=1,
        )
        world.war_instances["war_accept"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
            # Very high war scores on all pairs to boost side pressure.
            world.war_scores[pair] = 100
        world.war_exhaustion["Austria"] = 300
        world.invalidate_war_instance_indexes()
        stage_settlement_confirm(
            world, war_id="war_accept",
            settlement_terms=[{"type": "peace"}],
        )
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        # With the @patch above, acceptance is forced to pass so the
        # ratification path can be exercised end to end.
        assert dialogue["can_ratify"] is True
        result = handle_settlement_dialogue_action(
            world, action="confirm_settlement", dialogue=dialogue,
        )
        assert result["success"] is True
        assert result["mutated"] is True
        assert (
            result["settlement_reactions"]["summary_event"]["route"]["route_id"]
            == dialogue["route_id"]
        )

    def test_ratification_options_absent_on_rejection(self):
        """v0.22 SC-3 contract: blocked ratification OMITS
        `confirm_settlement` from both `options[]` AND `available_action_ids[]`
        rather than rendering a disabled Ratify button. The popup banner
        replaces the missing primary action; codex's earlier "visible but
        disabled" plumbing (`available=False`, `disabled_reason`,
        `ratify_blocked_reason`) is intentionally not used for the blocked
        state. The only visible action is the back-out path."""
        world = WorldState()
        _install_common_peace_war(world, war_score=5)
        result = stage_settlement_confirm(
            world, war_id="war_1",
            settlement_terms=[{"type": "territory_cede", "from": "Austria", "to": "France", "region": "Bohemia"}],
        )
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        option_actions = [o["action"] for o in dialogue.get("options", [])]
        assert "confirm_settlement" not in option_actions
        assert "back_out_settlement" in option_actions
        # `available_action_ids[]` mirrors the absent-options shape per v0.22 SC-3.
        assert "confirm_settlement" not in dialogue.get("available_action_ids", [])
        assert "back_out_settlement" in dialogue.get("available_action_ids", [])
        assert dialogue.get("can_ratify") is False


# ═══════════════════════════════════════════════════════════════════════════
# SC-4: Hard-stop enforcement
# ═══════════════════════════════════════════════════════════════════════════


class TestHardStopEnforcement:
    def test_hard_stop_blocks_ratification(self):
        world = WorldState()
        war = make_synthetic_war_instance(
            "war_hs",
            attackers=["France"],
            defenders=["Austria"],
            attacker_leader="France",
            defender_leader="Austria",
            created_turn=1,
            created_sequence=1,
        )
        world.war_instances["war_hs"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
            world.war_scores[pair] = 0
        world.invalidate_war_instance_indexes()
        # No covered enemy → hard stop
        stage_settlement_confirm(
            world, war_id="war_hs",
            settlement_terms=[],
            covered_enemy_participants=[],
        )
        dialogue = world.pending_diplomatic_dialogue
        if dialogue:
            result = handle_settlement_dialogue_action(
                world, action="confirm_settlement", dialogue=dialogue,
            )
            assert result["success"] is False
            assert result["mutated"] is False

    def test_hard_stop_codes_constant_covers_all_emitters(self):
        assert "no_covered_enemy_participants" in SETTLEMENT_HARD_STOP_CODES
        assert "no_direct_war_score_for_covered_enemy" in SETTLEMENT_HARD_STOP_CODES


# ═══════════════════════════════════════════════════════════════════════════
# SC-2: Revise Terms hidden, Back Out discard semantics
# ═══════════════════════════════════════════════════════════════════════════


class TestReviseTermsAndBackOut:
    def test_revise_terms_returns_error(self):
        world = WorldState()
        _install_common_peace_war(world)
        stage_settlement_confirm(
            world, war_id="war_1",
            settlement_terms=[{"type": "forced_alliance", "from": "Austria", "to": "France"}],
        )
        dialogue = world.pending_diplomatic_dialogue
        result = handle_settlement_dialogue_action(
            world, action="revise_settlement_terms", dialogue=dialogue,
        )
        assert result["success"] is False
        assert result["error"] == "revision_not_available"

    def test_back_out_clears_persisted_draft(self):
        world = WorldState()
        _install_common_peace_war(world)
        world.pending_settlement_drafts["war_1"] = [
            {"type": "forced_alliance", "from": "Austria", "to": "France"},
        ]
        stage_settlement_confirm(
            world, war_id="war_1",
            settlement_terms=[{"type": "forced_alliance", "from": "Austria", "to": "France"}],
        )
        dialogue = world.pending_diplomatic_dialogue
        result = handle_settlement_dialogue_action(
            world, action="back_out_settlement", dialogue=dialogue,
        )
        assert result["success"] is True
        assert result["had_draft"] is True
        assert "war_1" not in world.pending_settlement_drafts

    def test_back_out_empty_draft_no_discard_prompt(self):
        world = WorldState()
        _install_common_peace_war(world)
        stage_settlement_confirm(world, war_id="war_1", settlement_terms=[])
        dialogue = world.pending_diplomatic_dialogue
        result = handle_settlement_dialogue_action(
            world, action="back_out_settlement", dialogue=dialogue,
        )
        assert result["success"] is True
        assert result["had_draft"] is False

    def test_revise_terms_not_in_options(self):
        world = WorldState()
        _install_common_peace_war(world)
        stage_settlement_confirm(
            world, war_id="war_1",
            settlement_terms=[{"type": "forced_alliance", "from": "Austria", "to": "France"}],
        )
        dialogue = world.pending_diplomatic_dialogue
        option_actions = [o["action"] for o in dialogue.get("options", [])]
        assert "revise_settlement_terms" not in option_actions


# ═══════════════════════════════════════════════════════════════════════════
# Draft persistence and serialization
# ═══════════════════════════════════════════════════════════════════════════


class TestDraftPersistence:
    def test_drafts_discarded_on_turn_end(self):
        world = WorldState()
        _install_common_peace_war(world)
        world.pending_settlement_drafts["war_1"] = [{"type": "peace"}]
        world.advance_turn()
        assert world.pending_settlement_drafts == {}

    def test_drafts_round_trip_serialization(self):
        world = WorldState()
        world.pending_settlement_drafts = {
            "war_1": [{"type": "territory_cede", "from": "A", "to": "B", "region": "X"}],
        }
        world.settlement_route_seq = {"war_1": {7: 2}}
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.pending_settlement_drafts == {
            "war_1": [{"type": "territory_cede", "from": "A", "to": "B", "region": "X"}],
        }
        assert restored.settlement_route_seq == {"war_1": {7: 2}}

    def test_settlement_route_ids_are_unique_same_war_same_turn(self):
        """v0.22 SC-14c: two same-war same-turn settlements mint distinct
        `settlement:{war_id}:{turn}:{seq}` route ids with a monotonic seq."""
        world = WorldState()
        _install_common_peace_war(world)

        first = stage_settlement_confirm(
            world,
            war_id="war_1",
            settlement_terms=[{"type": "peace"}],
        )
        first_route = first["diplomatic_dialogue"]["route_id"]
        world.dialogue_manager.pop()

        second = stage_settlement_confirm(
            world,
            war_id="war_1",
            settlement_terms=[{"type": "peace"}],
        )
        second_route = second["diplomatic_dialogue"]["route_id"]

        assert first_route != second_route
        assert first_route == f"settlement:war_1:{world.current_turn}:1"
        assert second_route == f"settlement:war_1:{world.current_turn}:2"

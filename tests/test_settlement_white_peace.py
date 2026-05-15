"""G2-Slice-W1 White Peace Affordance behavior tests.

SETTLEMENT_UI_CLEANUP_SPEC v0.28 §"White Peace Affordance" introduces
`propose_white_peace` as a distinct labeled action and an editor empty-
Ratify gate. These tests pin the contract:

- Editor-staged empty drafts (caller_kind="player_editor", white_peace=False)
  omit `confirm_settlement` from `options[]` and `available_action_ids[]`
  regardless of acceptance verdict.
- Authoring a first clause re-enables Ratify when acceptance allows.
- The wizard surfaces `propose_white_peace` alongside Open Settlement.
- The wizard CTA stages `settlement_confirm` with white_peace=True,
  empty draft, and a labeled heading.
- A blocked white-peace acceptance verdict hides Ratify and shows the
  blocked-ratification banner.
- White-peace ratification emits `settlement_summary` with
  `white_peace=True` on the event payload.
- The typed `propose common peace with X` command path remains
  debug/parser-only and does not stage through the labeled CTA surface.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from backend.ai.validation import VALID_ACTIONS
from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.diplomacy import get_available_diplomatic_actions
from backend.game_logic.settlement_preview import (
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    handle_settlement_dialogue_action,
    ratify_settlement_confirm,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


def _install_common_peace_war(world: WorldState, *, war_score: int = 70) -> dict:
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
        a, _b = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = war_score if a == "Austria" else -war_score
    world.war_exhaustion["Austria"] = 30
    world.invalidate_war_instance_indexes()
    return war


def _acceptance_accepts(*args, **kwargs):
    from backend.game_logic.settlement_scoring import calculate_common_peace_acceptance as real
    result = real(*args, **kwargs)
    result["score"] = 100
    result["verdict"] = "accept"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    result["side_pressure_score"] = 70
    return result


def _acceptance_rejects(*args, **kwargs):
    from backend.game_logic.settlement_scoring import calculate_common_peace_acceptance as real
    result = real(*args, **kwargs)
    result["score"] = 12
    result["verdict"] = "reject"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Empty-Ratify gate
# ═══════════════════════════════════════════════════════════════════════════


class TestEmptyRatifyGate:
    def test_open_settlement_editor_blocks_ratify_when_settlement_terms_is_empty(self):
        """Editor-staged empty drafts omit `confirm_settlement` from
        `options[]` AND `available_action_ids[]` even when the scorer
        would otherwise accept."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[],
                caller_kind="player_editor",
                white_peace=False,
            )
        # Either the preview path refuses to mint Ratify, or staging
        # blocks the dialogue. Both shapes are acceptable per spec.
        dialogue = (result.get("diplomatic_dialogue")
                    or world.pending_diplomatic_dialogue)
        if dialogue is None:
            # Hard refusal upstream is also acceptable.
            assert result.get("success") is False
            return
        assert "confirm_settlement" not in dialogue.get(
            "available_action_ids", []
        ), "editor empty-draft must not advertise confirm_settlement"
        option_actions = [
            o.get("action") for o in dialogue.get("options", []) or []
        ]
        assert "confirm_settlement" not in option_actions
        terms_rows = (
            dialogue.get("review_sections", {})
            .get("sections", {})
            .get("terms", {})
            .get("rows", [])
        )
        assert terms_rows == []
        assert dialogue["acceptance_display"]["band"] == "blocked"
        assert dialogue["acceptance_display"]["total"] is None
        assert dialogue["ratify_blocked_reason"] == "No settlement terms have been authored."
        assert "no settlement terms authored" in dialogue["talleyrand_text"]
        assert "no single dominant pressure" not in dialogue["talleyrand_text"]
        assert "author_gold_indemnity_terms" in dialogue["available_action_ids"]
        assert "author_gold_per_turn_terms" in dialogue["available_action_ids"]

    def test_empty_first_open_can_author_gold_per_turn_demand(self):
        """The first Open Settlement screen must offer a real authoring
        path, not only pair-substitute escape hatches."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[],
                selected_target_nation="Austria",
                caller_kind="player_editor",
                white_peace=False,
            )
            dialogue = staged["diplomatic_dialogue"]
            result = handle_settlement_dialogue_action(
                world,
                action="author_gold_per_turn_terms",
                dialogue=dialogue,
            )

        assert result["success"] is True
        assert result["mutated"] is False
        refreshed = result["diplomatic_dialogue"]
        assert refreshed["settlement_terms"] == [
            {"type": "peace"},
            {
                "type": "gold_per_turn",
                "from": "Austria",
                "to": "France",
                "amount": 50,
                "turns": 3,
            },
        ]
        labels = [
            row.get("display_label", "")
            for row in refreshed["review_sections"]["sections"]["terms"].get("rows", [])
        ]
        assert "End hostilities (no material change)" in labels
        assert any(
            "50 gold/turn from Austria to France (3 turns)" in label
            for label in labels
        )

    def test_open_settlement_editor_enables_ratify_after_first_clause_authored(self):
        """Authoring at least one material clause re-enables Ratify if
        acceptance allows."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[
                    {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Bohemia"},
                ],
                caller_kind="player_editor",
                white_peace=False,
            )
        assert result.get("success") is True
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert "confirm_settlement" in dialogue.get("available_action_ids", [])
        option_actions = [
            o.get("action") for o in dialogue.get("options", []) or []
        ]
        assert "confirm_settlement" in option_actions

    def test_ratification_refuses_empty_editor_draft(self):
        """Defense-in-depth: even if the dialogue somehow exposes
        `confirm_settlement`, `ratify_settlement_confirm` refuses to
        mutate an empty editor draft with white_peace=False."""
        world = WorldState()
        _install_common_peace_war(world)
        # Manually build a malformed dialogue that violates the
        # editor empty-Ratify gate.
        dialogue = {
            "war_id": "war_1",
            "proposer_side": "attackers",
            "accepting_side": "defenders",
            "covered_enemy_participants": ["Austria", "Prussia"],
            "settlement_terms": [],
            "caller_kind": "player_editor",
            "white_peace": False,
            "settlement_preview": {"acceptance": {}},
            "staged_leaders": {
                "attackers": "France", "defenders": "Austria",
            },
            "route_id": "settlement:war_1:0:1",
        }
        result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is False
        assert result["mutated"] is False
        assert result["error"] == "empty_editor_draft_ratification"


# ═══════════════════════════════════════════════════════════════════════════
# Wizard CTA surfacing
# ═══════════════════════════════════════════════════════════════════════════


class TestWizardCTA:
    def test_propose_white_peace_action_visible_on_wizard_when_war_active(self):
        world = WorldState()
        _install_common_peace_war(world)
        actions = get_available_diplomatic_actions(world, "Austria")
        action_ids = [a.get("action") for a in actions]
        assert "propose_white_peace" in action_ids
        # Same eligibility as Open Settlement.
        wp = next(a for a in actions if a.get("action") == "propose_white_peace")
        os_action = next(a for a in actions if a.get("action") == "open_settlement")
        assert wp.get("available") == os_action.get("available")
        assert wp.get("war_id") == os_action.get("war_id")

    def test_propose_white_peace_in_valid_actions(self):
        assert "propose_white_peace" in VALID_ACTIONS


# ═══════════════════════════════════════════════════════════════════════════
# Wizard CTA → executor stages settlement_confirm with white_peace=True
# ═══════════════════════════════════════════════════════════════════════════


class TestProposeWhitePeaceExecution:
    def test_propose_white_peace_popup_uses_empty_draft_and_labeled_copy(self):
        world = WorldState()
        _install_common_peace_war(world)
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = executor._execute_propose_white_peace(
                {"action": "propose_white_peace", "target_nation": "Austria"},
                {"world": world},
            )
        assert result.get("success") is True
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue.get("white_peace") is True
        assert dialogue.get("settlement_terms") == []
        # Heading text identifies this as a white peace, not generic settlement.
        heading = dialogue.get("talleyrand_text", "")
        assert "white peace" in heading.lower() or "no terms" in heading.lower(), (
            f"unexpected white-peace heading: {heading!r}"
        )
        # Ratify must be available since the gate exempts white-peace.
        assert "confirm_settlement" in dialogue.get("available_action_ids", [])

    def test_propose_white_peace_acceptance_rejection_hides_ratify_and_shows_blocked_banner(self):
        world = WorldState()
        _install_common_peace_war(world)
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_rejects,
        ):
            result = executor._execute_propose_white_peace(
                {"action": "propose_white_peace", "target_nation": "Austria"},
                {"world": world},
            )
        assert result.get("success") is True
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue.get("white_peace") is True
        # Ratify must be absent because acceptance rejects.
        assert "confirm_settlement" not in dialogue.get("available_action_ids", [])
        option_actions = [
            o.get("action") for o in dialogue.get("options", []) or []
        ]
        assert "confirm_settlement" not in option_actions
        # Blocked banner copy is present (white-peace variant or fallback).
        heading = dialogue.get("talleyrand_text", "")
        lowered = heading.lower()
        assert (
            "cannot be ratified" in lowered
            or "blocked" in lowered
            or "white peace" in lowered
        ), f"unexpected blocked white-peace heading: {heading!r}"


class TestRatifyEmitsWhitePeaceEvent:
    def test_propose_white_peace_ratify_emits_settlement_summary_with_white_peace_true(self):
        world = WorldState()
        _install_common_peace_war(world)
        # Force acceptance through so ratification mutates and emits.
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            executor._execute_propose_white_peace(
                {"action": "propose_white_peace", "target_nation": "Austria"},
                {"world": world},
            )
            dialogue = world.pending_diplomatic_dialogue
            assert dialogue is not None
            assert dialogue.get("white_peace") is True
            result = ratify_settlement_confirm(world, dialogue)
        assert result.get("success") is True
        assert result.get("mutated") is True
        summary = (
            result.get("settlement_reactions", {}).get("summary_event") or {}
        )
        assert summary.get("white_peace") is True, (
            "settlement_summary event must carry white_peace=true after a "
            "labeled white-peace ratification"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Typed-command path does not surface
# ═══════════════════════════════════════════════════════════════════════════


class TestTypedCommandPath:
    def test_typed_propose_common_peace_does_not_route_through_player_facing_surfaces(self):
        """The typed `propose common peace with X` command remains in the
        parser keyword table as a debug/parser-only entry. The player
        surface for a white peace is the wizard CTA `propose_white_peace`,
        not the typed common-peace command. This test pins that
        `propose_white_peace` is NOT in the parser's keyword table for
        natural-language common-peace phrases."""
        from backend.ai.llm_client import LLMClient

        # The free-text `propose white peace with Austria` should not
        # auto-classify to `propose_white_peace`. `propose_white_peace`
        # ships only via the wizard's structured action field; the
        # parser keyword table must not give it a typed-command path.
        client = LLMClient(use_real_api=False)
        result = client.parse_command(
            "propose white peace with Austria",
            game_state={
                "valid_marshals": [],
                "valid_regions": [],
                "valid_targets": ["Austria"],
                "player_nation": "France",
                "current_turn": 1,
                "actions_remaining": 1,
                "max_actions_per_turn": 1,
            },
        )
        # parse_command may return ParseResult or dict; normalize.
        action_str = ""
        if hasattr(result, "action"):
            action_str = str(getattr(result, "action", "") or "")
        elif isinstance(result, dict):
            action_str = str(result.get("action") or "")
        assert action_str != "propose_white_peace", (
            "typed `propose white peace with X` must not auto-parse to "
            "propose_white_peace; wizard CTA is the only player surface"
        )


# ═══════════════════════════════════════════════════════════════════════════
# settlement_confirm dialogue fields
# ═══════════════════════════════════════════════════════════════════════════


class TestSettlementConfirmDialogueFields:
    def test_dialogue_carries_caller_kind_and_white_peace_flag(self):
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            preview = build_settlement_preview(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[],
            )
            dialogue = build_settlement_confirm_dialogue(
                world, preview,
                selected_target_nation="Austria",
                caller_kind="player_editor",
                white_peace=True,
            )
        assert dialogue.get("caller_kind") == "player_editor"
        assert dialogue.get("white_peace") is True
        # Empty-draft + white_peace=True exempts the editor empty-Ratify gate.
        assert "confirm_settlement" in dialogue.get("available_action_ids", [])

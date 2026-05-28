"""SC-5R-2 Godot settlement editor + draft round-trip + active-vs-archived
routing + incoming-offer label/copy alignment.

DWL-SET-SC5R-2 lands the player-facing surface that consumes the
SC-5R-1 EDIT payload contract: the Godot `settlement_editor_popup`
scene/script renders clause add/edit/remove controls, a covered-enemy
picker, and a `Submit for Review` button that POSTs the structured
`propose_common_peace` body the backend expects. `Back Out` keeps the
scoped draft alive so the player can re-open Settlement and pick up
where they left off. War-detail re-open of an active war routes back
to the live review surface; a war that is no longer active in the
HUD cache routes to the Diplomatic Ledger Treaties tab instead.

The audit repair acceptance checklist also requires that incoming
settlement offer action labels match behavior: `accept_settlement_offer`
opens a staged review (not an immediate ratification), so the label
must read `Review Settlement Offer` rather than `Accept Settlement`.

This test bundle pins all four surfaces. It does not run a Godot scene
graph (the headless harness is covered by `tools/godot_parse_report.json`);
it inspects backend payloads + Godot source so the player-facing
contract is enforceable from the Python suite.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.settlement_preview import (
    build_incoming_settlement_offer_popup,
    compute_settlement_draft_key,
    load_scoped_settlement_draft,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


GODOT_ROOT = Path(__file__).resolve().parent.parent / "godot-client" / "project-sovereign"
EDITOR_SCRIPT = GODOT_ROOT / "scripts" / "settlement_editor_popup.gd"
EDITOR_SCENE = GODOT_ROOT / "scenes" / "settlement_editor_popup.tscn"
MAIN_SCRIPT = GODOT_ROOT / "scripts" / "main.gd"
POPUP_SCRIPT = GODOT_ROOT / "scripts" / "proposal_confirm_popup.gd"


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
    from backend.game_logic.settlement_scoring import (
        calculate_common_peace_acceptance as real,
    )
    result = real(*args, **kwargs)
    result["score"] = 100
    result["verdict"] = "accept"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    result["side_pressure_score"] = 70
    return result


def _gold_indemnity_clause(amount: int = 200) -> dict:
    return {
        "type": "gold_indemnity",
        "from": "Austria",
        "to": "France",
        "amount": amount,
    }


# ═══════════════════════════════════════════════════════════════════════════
# A. Godot editor scene + script presence and structural pins
# ═══════════════════════════════════════════════════════════════════════════


class TestGodotEditorPopupSource:
    def test_settlement_editor_popup_script_exists(self):
        """SC-5R-2 ships a dedicated editor script (`settlement_editor_popup.gd`)."""
        assert EDITOR_SCRIPT.exists(), (
            f"Missing Godot editor script at {EDITOR_SCRIPT}"
        )

    def test_settlement_editor_popup_scene_exists(self):
        """SC-5R-2 ships a dedicated editor scene (`settlement_editor_popup.tscn`)."""
        assert EDITOR_SCENE.exists(), (
            f"Missing Godot editor scene at {EDITOR_SCENE}"
        )

    def test_editor_script_exposes_show_editor_entry_point(self):
        """`show_editor(data)` is the canonical mount entry point."""
        source = EDITOR_SCRIPT.read_text(encoding="utf-8")
        assert "func show_editor(data: Dictionary)" in source

    def test_editor_script_exposes_submit_and_back_out_signals(self):
        """The editor emits `submit_requested` + `back_out_requested`
        so main.gd can forward them through the structured POST or
        treat Back Out as a draft-preserving no-op."""
        source = EDITOR_SCRIPT.read_text(encoding="utf-8")
        assert "signal submit_requested(payload: Dictionary)" in source
        assert "signal back_out_requested(payload: Dictionary)" in source

    def test_editor_scene_renders_submit_for_review_action_label(self):
        """SC-25 vocabulary scan: editor uses `Submit for Review`, not bare `Submit`."""
        scene_source = EDITOR_SCENE.read_text(encoding="utf-8")
        assert "Submit for Review" in scene_source
        # Bare "Submit" appears nowhere as a button label.
        assert 'text = "Submit"' not in scene_source

    def test_editor_scene_renders_back_out_action_label(self):
        """Editor action rail exposes `Back Out` per spec line 590."""
        scene_source = EDITOR_SCENE.read_text(encoding="utf-8")
        assert "Back Out" in scene_source

    def test_editor_script_reads_clause_control_schema_for_picker_contents(self):
        """`clause_control_schema` is the backend source of truth for picker
        contents per spec line 554; the editor must consume it."""
        source = EDITOR_SCRIPT.read_text(encoding="utf-8")
        assert "clause_control_schema" in source

    def test_editor_script_reads_available_clause_types(self):
        """`available_clause_types[]` gates Add Clause picker contents."""
        source = EDITOR_SCRIPT.read_text(encoding="utf-8")
        assert "available_clause_types" in source

    def test_editor_script_reads_editor_route_payload(self):
        """The editor consumes the SC-5R-1 `editor_route` payload (war_id,
        selected_target_nation, covered_enemy_participants, draft_key,
        staged_settlement_terms)."""
        source = EDITOR_SCRIPT.read_text(encoding="utf-8")
        for field in [
            "editor_route",
            "draft_key",
            "selected_target_nation",
            "covered_enemy_participants",
            "staged_settlement_terms",
        ]:
            assert field in source, f"editor script must consume {field}"

    def test_editor_script_emits_propose_common_peace_payload_with_player_editor_caller_kind(
        self,
    ):
        """Submit for Review POST body uses `action=propose_common_peace`
        and `caller_kind=player_editor`."""
        source = EDITOR_SCRIPT.read_text(encoding="utf-8")
        assert '"action": "propose_common_peace"' in source
        assert '"caller_kind": "player_editor"' in source

    def test_editor_scene_layer_is_above_proposal_confirm_popup(self):
        """The editor (layer 112) must render above the proposal_confirm
        popup (layer 110) that launched it."""
        scene_source = EDITOR_SCENE.read_text(encoding="utf-8")
        assert "layer = 112" in scene_source

    def test_editor_scene_includes_clause_picker_and_submit_controls(self):
        """The scene defines the AddClause selector, ClauseList, and
        SubmitForReview button so the script can populate them at runtime."""
        scene_source = EDITOR_SCENE.read_text(encoding="utf-8")
        for node in [
            "AddClauseTypeSelector",
            "AddClauseButton",
            "ClauseList",
            "SubmitForReviewButton",
            "BackOutButton",
            "CoveredEnemiesContainer",
        ]:
            assert node in scene_source, f"scene must declare node {node}"


# ═══════════════════════════════════════════════════════════════════════════
# B. main.gd wires editor open + Submit + Back Out flow
# ═══════════════════════════════════════════════════════════════════════════


class TestMainGdWiringForEditor:
    def test_main_registers_settlement_editor_popup_with_dialog_manager(self):
        """`main.gd::_ready` registers the editor with dialog_manager so
        it participates in the modal taxonomy."""
        source = MAIN_SCRIPT.read_text(encoding="utf-8")
        assert (
            'dialog_manager.register("settlement_editor", "res://scenes/settlement_editor_popup.tscn")'
            in source
        )

    def test_main_connects_editor_submit_and_back_out_signals(self):
        """`submit_requested` -> _on_settlement_editor_submit;
        `back_out_requested` -> _on_settlement_editor_back_out."""
        source = MAIN_SCRIPT.read_text(encoding="utf-8")
        assert "submit_requested.connect(_on_settlement_editor_submit)" in source
        assert "back_out_requested.connect(_on_settlement_editor_back_out)" in source

    def test_main_intercepts_revise_terms_when_can_edit_terms_true(self):
        """When the player clicks `Revise Terms` on a settlement_confirm
        REVIEW dialogue with `can_edit_terms=true` and an `editor_route`,
        main.gd opens the editor LOCALLY instead of round-tripping a
        dialogue response (which would just re-stage the same REVIEW
        per SC-2 today)."""
        source = MAIN_SCRIPT.read_text(encoding="utf-8")
        assert 'if action == "revise_settlement_terms":' in source
        assert 'settlement_editor_popup.show_editor(data)' in source

    def test_main_submit_handler_posts_propose_common_peace_via_structured_command(self):
        """Submit pushes through `send_structured_command` with the
        editor's structured payload so the backend re-runs SC-1 POST
        preview validation."""
        source = MAIN_SCRIPT.read_text(encoding="utf-8")
        assert "func _on_settlement_editor_submit(payload: Dictionary)" in source
        assert "api_client.send_structured_command(command, payload, _on_command_result)" in source

    def test_main_back_out_handler_preserves_draft(self):
        """Back Out is a no-op for the scoped draft store; the editor
        emits a status line and re-enables input. The backend keeps
        the draft alive under its `draft_key`."""
        source = MAIN_SCRIPT.read_text(encoding="utf-8")
        assert "func _on_settlement_editor_back_out(payload: Dictionary)" in source
        assert "Settlement draft kept for war" in source


# ═══════════════════════════════════════════════════════════════════════════
# C. Backend draft round-trip via scoped draft_key
# ═══════════════════════════════════════════════════════════════════════════


class TestBackendDraftRoundTrip:
    def test_propose_common_peace_restores_scoped_draft_when_no_terms_passed(self):
        """SC-5R-2 round-trip: a scoped draft saved on Submit is
        restored on a subsequent `propose_common_peace` open without
        explicit `settlement_terms`. The restored draft populates the
        staged settlement_confirm REVIEW seeded with the prior clauses."""
        world = WorldState()
        _install_common_peace_war(world)
        # Save a scoped draft via the canonical helper.
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=[{"type": "peace"}, _gold_indemnity_clause(150)],
        )
        executor = DiplomaticExecutor(None)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = executor._execute_propose_common_peace(
                {
                    "action": "propose_common_peace",
                    "target_nation": "Austria",
                    "war_id": "war_1",
                    "selected_target_nation": "Austria",
                    "covered_enemy_participants": ["Austria", "Prussia"],
                },
                {"world": world},
            )
        assert result.get("success"), result
        assert result.get("draft_restored_from_scope") is True
        staged = result.get("diplomatic_dialogue") or {}
        terms = staged.get("settlement_terms") or []
        # Compare by clause type to avoid display-only field drift.
        types = [str(t.get("type", "")) for t in terms]
        assert "peace" in types
        assert "gold_indemnity" in types

    def test_propose_common_peace_with_explicit_terms_does_not_restore_scope(self):
        """When the caller explicitly passes `settlement_terms`, the
        scoped store is NOT consulted; the explicit terms win."""
        world = WorldState()
        _install_common_peace_war(world)
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=[{"type": "peace"}],
        )
        executor = DiplomaticExecutor(None)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = executor._execute_propose_common_peace(
                {
                    "action": "propose_common_peace",
                    "target_nation": "Austria",
                    "war_id": "war_1",
                    "selected_target_nation": "Austria",
                    "covered_enemy_participants": ["Austria", "Prussia"],
                    "settlement_terms": [
                        {"type": "peace"},
                        _gold_indemnity_clause(250),
                    ],
                },
                {"world": world},
            )
        assert result.get("success"), result
        assert result.get("draft_restored_from_scope") is not True
        staged = result.get("diplomatic_dialogue") or {}
        terms = staged.get("settlement_terms") or []
        # Explicit terms preserved verbatim; scoped draft was [{"type": "peace"}] only.
        amounts = [int(t.get("amount", 0)) for t in terms if t.get("type") == "gold_indemnity"]
        assert 250 in amounts

    def test_propose_common_peace_no_scoped_draft_starts_empty(self):
        """When no scoped draft exists, the propose path stages an
        empty draft (white-peace baseline), not a restored draft."""
        world = WorldState()
        _install_common_peace_war(world)
        executor = DiplomaticExecutor(None)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = executor._execute_propose_common_peace(
                {
                    "action": "propose_common_peace",
                    "target_nation": "Austria",
                    "war_id": "war_1",
                    "selected_target_nation": "Austria",
                    "covered_enemy_participants": ["Austria", "Prussia"],
                },
                {"world": world},
            )
        assert result.get("draft_restored_from_scope") is not True

    def test_scoped_draft_key_for_different_target_does_not_collide(self):
        """SC-5R-1 contract: drafts for the same war but different
        selected_target_nation are stored under different draft_keys
        and do not restore into each other."""
        world = WorldState()
        _install_common_peace_war(world)
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
            settlement_terms=[_gold_indemnity_clause(150)],
        )
        # A different selected target's scoped store starts empty.
        restored = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Prussia",
            covered_enemy_participants=["Prussia"],
        )
        assert restored is None or restored == []


# ═══════════════════════════════════════════════════════════════════════════
# D. Active-vs-archived settlement review routing
# ═══════════════════════════════════════════════════════════════════════════


class TestActiveVsArchivedRouting:
    def test_main_war_settlement_clicked_routes_archived_war_to_history(self):
        """SC-5R-2: when the cached war list does NOT contain an active
        row for the clicked war_id, main.gd routes to the Diplomatic
        Ledger settlement history surface instead of POSTing a stale
        propose_common_peace."""
        source = MAIN_SCRIPT.read_text(encoding="utf-8")
        assert "_is_war_archived_in_cache" in source
        assert '"surface": "settlement_history"' in source
        # Routes the existing recovery_route helper so the existing
        # settlement_history wiring stays single-source.
        assert "_route_settlement_recovery_route" in source

    def test_main_war_settlement_clicked_continues_to_post_for_active_war(self):
        """Active wars still POST `propose_common_peace` so the live
        review surface mounts. The structured payload includes war_id,
        target_nation, and the propose_common_peace action."""
        source = MAIN_SCRIPT.read_text(encoding="utf-8")
        assert '"action": "propose_common_peace"' in source

    def test_active_vs_archived_routing_guard_runs_before_post(self):
        """The archive check must run BEFORE the POST so a stale click
        does not waste a backend round trip. The early return uses
        `_route_settlement_recovery_route` for the ledger handoff."""
        source = MAIN_SCRIPT.read_text(encoding="utf-8")
        idx_archived = source.find("if _is_war_archived_in_cache(war_id):")
        idx_post = source.find('"action": "propose_common_peace"', idx_archived)
        assert idx_archived != -1
        assert idx_post > idx_archived, (
            "Archive-route check must precede propose_common_peace POST"
        )


# ═══════════════════════════════════════════════════════════════════════════
# E. Incoming-offer action labels match behavior
# ═══════════════════════════════════════════════════════════════════════════


class TestIncomingOfferLabelsMatchBehavior:
    def _make_offer(self, world: WorldState) -> dict:
        return {
            "type": "incoming_settlement_offer",
            "offer_id": "settlement_offer:war_1:2:1",
            "war_id": "war_1",
            "proposer_nation": "Austria",
            "proposer_side": "defenders",
            "accepting_side": "attackers",
            "covered_enemy_participants": ["Austria"],
            "settlement_terms": [
                {"type": "peace"},
                _gold_indemnity_clause(150),
            ],
            "turn_created": 2,
        }

    def test_review_settlement_offer_label_replaces_accept_settlement(self):
        """SC-5R-2: `accept_settlement_offer` stages a settlement_confirm
        REVIEW; the action label must read as a review action, not an
        immediate ratification."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        labels = {opt.get("action"): opt.get("label") for opt in popup.get("options", [])}
        assert labels.get("accept_settlement_offer") == "Review Settlement Offer"

    def test_reject_offer_label_replaces_reject_settlement(self):
        """`Reject Offer` reads correctly because the action only
        removes the pending offer; it does not reject a settlement
        that has been ratified."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        labels = {opt.get("action"): opt.get("label") for opt in popup.get("options", [])}
        assert labels.get("reject_settlement_offer") == "Reject Offer"

    def test_review_settlement_offer_description_promises_review_not_ratification(
        self,
    ):
        """The description must not promise immediate ratification —
        the backend handler stages a fresh settlement_confirm review,
        and the player still has to ratify on the next popup."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        accept_opt = next(
            opt for opt in popup["options"] if opt.get("action") == "accept_settlement_offer"
        )
        description = str(accept_opt.get("description", "")).lower()
        # Must promise a review path, not a one-click ratify.
        assert "review" in description
        # Must NOT claim it ratifies.
        assert "ratif" not in description or "still requires a final confirm" in description.lower() or "still requires" in description

    def test_request_revision_label_preserved(self):
        """`Request Revision` label / description stayed correct after
        the SC-5R-2 label fix — this regression pin proves the rewrite
        did not accidentally collateral-damage the counter-editor path."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        labels = {opt.get("action"): opt.get("label") for opt in popup.get("options", [])}
        assert labels.get("request_settlement_revision") == "Request Revision"

    def test_all_three_offer_actions_remain_available_after_label_rewrite(self):
        """The label rewrite is copy-only; all three actions remain
        available and route through the same handler."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        actions = {opt.get("action") for opt in popup.get("options", [])}
        assert actions == {
            "accept_settlement_offer",
            "request_settlement_revision",
            "reject_settlement_offer",
        }


# ═══════════════════════════════════════════════════════════════════════════
# F. Editor mount conditions match the SC-5R-1 EDIT payload contract
# ═══════════════════════════════════════════════════════════════════════════


class TestEditorMountGatesMatchBackendContract:
    def test_editor_mount_intercept_gated_on_can_edit_terms_true(self):
        """main.gd refuses to mount the editor when `can_edit_terms=false`,
        so AI-staged offers + legacy/typed callers fall through to the
        regular dialogue response path (the same path SC-5R-1 still
        owns)."""
        source = MAIN_SCRIPT.read_text(encoding="utf-8")
        # The intercept asserts can_edit_terms AND a non-empty editor_route.
        intercept = source.split('if action == "revise_settlement_terms":', 1)[1].split(
            "func", 1
        )[0]
        assert "can_edit_terms" in intercept
        assert "editor_route" in intercept

    def test_proposal_confirm_popup_still_renders_settlement_review_when_editor_absent(
        self,
    ):
        """The editor is additive. The existing settlement_confirm
        review render in `proposal_confirm_popup.gd` is unchanged
        when the editor is not mounted."""
        source = POPUP_SCRIPT.read_text(encoding="utf-8")
        assert "_build_settlement_content" in source

    def test_can_edit_terms_propagates_to_editor_mount_payload(self):
        """Backend payload carries can_edit_terms / editor_route /
        available_clause_types / clause_control_schema so the Godot
        editor can mount without an extra round trip."""
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
                settlement_terms=[{"type": "peace"}, _gold_indemnity_clause()],
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
        dialogue = staged["diplomatic_dialogue"]
        assert dialogue["can_edit_terms"] is True
        assert isinstance(dialogue.get("editor_route"), dict)
        assert dialogue["editor_route"].get("surface") == "settlement_editor"
        assert dialogue["editor_route"].get("draft_key") == compute_settlement_draft_key(
            "war_1", "Austria", ["Austria", "Prussia"]
        )
        # The editor_route payload carries the staged terms verbatim so
        # the editor can mount without a second POST preview.
        staged_terms = dialogue["editor_route"].get("staged_settlement_terms") or []
        types = [str(t.get("type", "")) for t in staged_terms]
        assert "gold_indemnity" in types

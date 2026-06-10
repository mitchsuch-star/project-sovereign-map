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

This test bundle pins the audited SC-5R-2 surfaces. It does not run a Godot scene
graph (the headless harness is covered by `tools/godot_parse_report.json`);
it inspects backend payloads + Godot source so the player-facing
contract is enforceable from the Python suite.
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.settlement_preview import (
    build_incoming_settlement_offer_popup,
    compute_settlement_draft_key,
    handle_incoming_settlement_offer_action,
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


def _read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _function_body(path: Path, function_name: str) -> str:
    source = _read_source(path)
    marker = f"func {function_name}"
    start = source.find(marker)
    assert start != -1, f"{path} missing {marker}"
    next_func = re.search(r"\nfunc\s+\w+", source[start + 1:])
    end = len(source) if next_func is None else start + 1 + next_func.start()
    return source[start:end]


def _return_lines(function_body: str) -> list[str]:
    lines = []
    for line in function_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("return "):
            lines.append(stripped)
    return lines


def _scene_node_block(scene_source: str, node_name: str) -> str:
    match = re.search(
        rf'(?ms)^\[node name="{re.escape(node_name)}" [^\]]+\]\n(.*?)(?=^\[node |\Z)',
        scene_source,
    )
    assert match, f"scene missing node {node_name}"
    return match.group(1)


def _scene_node_text(scene_source: str, node_name: str) -> str:
    block = _scene_node_block(scene_source, node_name)
    match = re.search(r'(?m)^text = "([^"]*)"', block)
    assert match, f"node {node_name} missing text property"
    return match.group(1)


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
        body = _function_body(EDITOR_SCRIPT, "show_editor")
        assert body.startswith("func show_editor(data: Dictionary) -> bool")

    def test_editor_script_exposes_submit_and_back_out_signals(self):
        """The editor emits the SC-5R-2 action signals
        so main.gd can forward them through the structured POST or
        dialogue response endpoint without synthesizing commands."""
        source = _read_source(EDITOR_SCRIPT)
        signals = set(re.findall(r"(?m)^signal\s+([^(]+\([^)]*\))", source))
        assert "submit_requested(payload: Dictionary)" in signals
        assert "back_out_requested(payload: Dictionary)" in signals
        assert "concession_baseline_requested(payload: Dictionary)" in signals

    def test_editor_scene_renders_submit_for_review_action_label(self):
        """SC-25 vocabulary scan: editor uses `Submit for Review`, not bare `Submit`."""
        scene_source = _read_source(EDITOR_SCENE)
        assert _scene_node_text(scene_source, "SubmitForReviewButton") == "Submit for Review"
        # Bare "Submit" appears nowhere as a button label.
        assert 'text = "Submit"' not in scene_source

    def test_editor_scene_renders_back_out_action_label(self):
        """Editor action rail exposes `Back Out` per spec line 590."""
        scene_source = _read_source(EDITOR_SCENE)
        assert _scene_node_text(scene_source, "BackOutButton") == "Back Out"

    def test_editor_script_reads_clause_control_schema_for_picker_contents(self):
        """`clause_control_schema` is the backend source of truth for picker
        contents per spec line 554; the editor must consume it."""
        body = _function_body(EDITOR_SCRIPT, "_render_clause_editor_fields")
        assert 'clause_control_schema.get(ttype, {})' in body
        assert 'schema.get("fields", {})' in body

    def test_editor_script_reads_available_clause_types(self):
        """`available_clause_types[]` gates Add Clause picker contents."""
        body = _function_body(EDITOR_SCRIPT, "_populate_add_clause_selector")
        assert "for ttype in available_clause_types:" in body
        assert "add_clause_selector.set_item_metadata(idx, str(ttype))" in body

    def test_editor_script_reads_editor_route_payload(self):
        """The editor consumes the SC-5R-1 `editor_route` payload (war_id,
        selected_target_nation, covered_enemy_participants, draft_key,
        staged_settlement_terms)."""
        show_body = _function_body(EDITOR_SCRIPT, "show_editor")
        submit_body = _function_body(EDITOR_SCRIPT, "_on_submit_pressed")
        for field in [
            "editor_route",
            "covered_enemy_participants",
            "staged_settlement_terms",
        ]:
            assert field in show_body, f"show_editor must consume {field}"
        for field in ["draft_key", "selected_target_nation"]:
            assert field in submit_body, f"submit payload must echo {field}"

    def test_editor_script_emits_propose_common_peace_payload_with_player_editor_caller_kind(
        self,
    ):
        """Submit for Review POST body uses `action=propose_common_peace`
        and `caller_kind=player_editor`."""
        body = _function_body(EDITOR_SCRIPT, "_on_submit_pressed")
        for key in [
            '"action": "propose_common_peace"',
            '"war_id"',
            '"selected_target_nation"',
            '"covered_enemy_participants"',
            '"settlement_terms"',
            '"draft_key"',
            '"caller_kind": "player_editor"',
        ]:
            assert key in body

    def test_editor_renders_concession_baseline_button_inside_edit_surface(self):
        """The EDIT surface renders the concession baseline button but
        asks the backend to revalidate the baseline at click time."""
        source = _read_source(EDITOR_SCRIPT)
        assert "Generate concession baseline (Talleyrand)" in source
        assert "concession_baseline_visible" in source
        assert "func _on_apply_concession_baseline_pressed()" in source
        apply_body = _function_body(EDITOR_SCRIPT, "_on_apply_concession_baseline_pressed")
        assert "concession_baseline_requested.emit(payload)" in apply_body
        assert "settlement_terms = terms" not in apply_body
        payload_body = _function_body(EDITOR_SCRIPT, "_baseline_request_payload")
        assert '"action": "re_author_with_concessions"' in payload_body
        assert '"caller_kind": "player_editor"' in payload_body

    def test_editor_inline_submit_errors_render_in_status_panel(self):
        """Backend submit errors remount as inline editor status text."""
        show_body = _function_body(EDITOR_SCRIPT, "show_editor")
        status_body = _function_body(EDITOR_SCRIPT, "_render_status")
        assert 'data.get("editor_inline_error", "")' in show_body
        assert "inline_error_text" in status_body
        assert "COLOR_RED" in status_body

    def test_editor_scene_layer_is_above_proposal_confirm_popup(self):
        """The editor (layer 112) must render above the proposal_confirm
        popup (layer 110) that launched it."""
        scene_source = _read_source(EDITOR_SCENE)
        assert "layer = 112" in _scene_node_block(scene_source, "SettlementEditorPopup")

    def test_editor_scene_includes_clause_picker_and_submit_controls(self):
        """The scene defines the AddClause selector, ClauseList, and
        SubmitForReview button so the script can populate them at runtime."""
        scene_source = _read_source(EDITOR_SCENE)
        declared_nodes = set(re.findall(r'(?m)^\[node name="([^"]+)" ', scene_source))
        for node in [
            "AddClauseTypeSelector",
            "AddClauseButton",
            "ClauseList",
            "SubmitForReviewButton",
            "BackOutButton",
            "CoveredEnemiesContainer",
        ]:
            assert node in declared_nodes, f"scene must declare node {node}"


# ═══════════════════════════════════════════════════════════════════════════
# B. main.gd wires editor open + Submit + Back Out flow
# ═══════════════════════════════════════════════════════════════════════════


class TestMainGdWiringForEditor:
    def test_main_registers_settlement_editor_popup_with_dialog_manager(self):
        """`main.gd::_ready` registers the editor with dialog_manager so
        it participates in the modal taxonomy."""
        ready_body = _function_body(MAIN_SCRIPT, "_ready")
        assert (
            'dialog_manager.register("settlement_editor", "res://scenes/settlement_editor_popup.tscn")'
            in ready_body
        )

    def test_main_connects_editor_submit_and_back_out_signals(self):
        """Editor signals are wired to the main response handlers."""
        ready_body = _function_body(MAIN_SCRIPT, "_ready")
        assert "submit_requested.connect(_on_settlement_editor_submit)" in ready_body
        assert "back_out_requested.connect(_on_settlement_editor_back_out)" in ready_body
        assert (
            "concession_baseline_requested.connect(_on_settlement_editor_concession_baseline_requested)"
            in ready_body
        )

    def test_main_intercepts_revise_terms_when_can_edit_terms_true(self):
        """When the player clicks `Revise Terms` on a settlement_confirm
        REVIEW dialogue with `can_edit_terms=true` and an `editor_route`,
        main.gd opens the editor LOCALLY instead of round-tripping a
        dialogue response (which would just re-stage the same REVIEW
        per SC-2 today)."""
        body = _function_body(MAIN_SCRIPT, "_on_proposal_confirm_choice")
        revise_block = body.split('if action == "revise_settlement_terms":', 1)[1].split(
            "# Send the raw action", 1,
        )[0]
        fallback_block = body.split("# Send the raw action", 1)[1]
        assert (
            'dtype == "settlement_confirm" and can_edit and editor_route_data is Dictionary '
            "and editor_route_data.size() > 0"
        ) in revise_block
        assert "settlement_editor_popup.show_editor(data)" in revise_block
        assert "api_client.send_dialogue_response(choice_index, _on_command_result)" in fallback_block
        assert body.index("settlement_editor_popup.show_editor(data)") < body.index(
            "api_client.send_dialogue_response(choice_index, _on_command_result)"
        )

    def test_main_submit_handler_posts_propose_common_peace_via_structured_command(self):
        """Submit pushes through `send_structured_command` with the
        editor's structured payload so the backend re-runs SC-1 POST
        preview validation."""
        body = _function_body(MAIN_SCRIPT, "_on_settlement_editor_submit")
        assert body.startswith("func _on_settlement_editor_submit(payload: Dictionary)")
        assert "_remember_settlement_editor_payload(payload)" in body
        assert "api_client.send_structured_command(command, payload, _on_command_result)" in body

    def test_main_routes_initial_open_editor_mount_before_review_popup(self):
        """Initial Open Settlement / Request Revision responses carry
        `open_editor_on_mount=true`; main.gd must mount EDIT before the
        generic settlement_confirm REVIEW popup route can consume the response."""
        configure_body = _function_body(MAIN_SCRIPT, "_configure_response_routes")
        assert '"id": "settlement_editor"' in configure_body
        assert configure_body.index('"id": "settlement_editor"') < configure_body.index(
            '"id": "proposal_confirm"',
        )
        matcher = _function_body(MAIN_SCRIPT, "_response_has_settlement_editor_route")
        router = _function_body(MAIN_SCRIPT, "_route_settlement_editor_response")
        assert 'response.get("open_editor_on_mount", false)' in matcher
        assert "_dialogue_can_open_settlement_editor" in matcher
        assert "settlement_editor_popup.show_editor(dialogue)" in router

    def test_main_remounts_editor_inline_on_submit_validation_errors(self):
        """Submit-time editor errors stay inside the editor surface."""
        body = _function_body(MAIN_SCRIPT, "_maybe_remount_settlement_editor_after_error")
        for code in [
            "empty_authored_draft",
            "submitted_terms_failed_revalidation",
            "same_war_merge_conflict",
            "concession_baseline_unavailable",
        ]:
            assert code in body
        assert "_remount_settlement_editor_with_error" in body

    def test_main_concession_baseline_button_uses_dialogue_response_revalidation(self):
        """The editor baseline button uses the real dialogue action path
        so backend click-time revalidation stays authoritative."""
        body = _function_body(MAIN_SCRIPT, "_on_settlement_editor_concession_baseline_requested")
        assert "_settlement_dialogue_option_index(" in body
        assert '"re_author_with_concessions"' in body
        assert "_settlement_editor_pending_baseline_apply = true" in body
        assert "api_client.send_dialogue_response(choice_index, _on_command_result)" in body
        continuation = _function_body(MAIN_SCRIPT, "_maybe_continue_settlement_editor_baseline")
        assert 'response.get("requires_replace_confirm", false)' in continuation
        assert "api_client.send_dialogue_response(1, _on_command_result)" in continuation

    def test_main_back_out_handler_preserves_draft(self):
        """Back Out closes the editor and pops the staged settlement_confirm
        hard-stop on the backend via the non-destructive
        `suspend_settlement_editor` dialogue action, so the next command is
        not held by the executor hard-stop gate. It must NOT send the
        discard close (`back_out_settlement`) and must not call a scoped
        discard helper — the backend keeps the draft alive under its
        `draft_key`."""
        body = _function_body(MAIN_SCRIPT, "_on_settlement_editor_back_out")
        assert body.startswith("func _on_settlement_editor_back_out(payload: Dictionary)")
        assert "Settlement draft kept for war" in body
        assert "discard_scoped_settlement_draft" not in body
        assert "back_out_settlement" not in body
        # The fix: pop the staged hard-stop without discarding the draft.
        assert 'send_dialogue_response("suspend_settlement_editor"' in body


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

    def test_propose_common_peace_no_scoped_draft_lands_fresh_propose(self):
        """Re-front Slice 1: with no scoped draft, opening a settlement lands
        the conversational PROPOSE surface with a freshly generated baseline —
        NOT a restored draft and NOT the old blank EDIT form."""
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
        assert result.get("propose_on_mount") is True
        assert result.get("open_editor_on_mount") is not True
        staged = result.get("diplomatic_dialogue") or {}
        assert staged.get("dialogue_mode") == "PROPOSE"
        # The PROPOSE surface always carries the per-court acceptance block.
        assert staged.get("per_court_acceptance")

    def test_propose_common_peace_submit_for_review_does_not_reopen_editor(self):
        """Submit for Review returns REVIEW; it must not auto-mount EDIT again."""
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
                    "settlement_terms": [{"type": "peace"}, _gold_indemnity_clause(275)],
                },
                {"world": world},
            )
        assert result.get("success"), result
        assert result.get("open_editor_on_mount") is not True

    def test_scoped_draft_restore_is_war_scoped_with_target_preference(self):
        """PF-2 (Gate-4 pre-flight D4) supersedes the SC-5R-1 isolation pin:
        the real reopen route cannot reconstruct the suspend-time scope (it
        sends no covered list and always targets the war's defender leader),
        so same-war lookups fall back — exact key, then (war, target)
        prefix, then war-wide most-recent. A settlement is ONE multi-court
        table per war (SC-26), so war-scoped restore matches the player's
        "draft kept" mental model. Cross-WAR isolation still holds."""
        world = WorldState()
        _install_common_peace_war(world)
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
            settlement_terms=[_gold_indemnity_clause(150)],
        )
        # Same war, different target: the war-wide fallback restores the
        # kept draft instead of silently regenerating a baseline (D4).
        restored = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Prussia",
            covered_enemy_participants=["Prussia"],
        )
        assert restored == [_gold_indemnity_clause(150)]
        # Cross-war isolation holds: nothing bleeds across war ids.
        assert load_scoped_settlement_draft(
            world,
            war_id="war_2",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
        ) is None
        # Target preference: when the asked-for target has its own draft,
        # it wins over another court's more recent save.
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Prussia",
            covered_enemy_participants=["Prussia"],
            settlement_terms=[_gold_indemnity_clause(75)],
        )
        restored_austria = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=[],
        )
        assert restored_austria == [_gold_indemnity_clause(150)]

    def test_suspend_settlement_editor_choice_pops_hardstop_and_keeps_draft(self):
        """SC-5R-2 follow-up bug fix: the editor Back Out sends the string
        choice `suspend_settlement_editor`. The dialogue resolver routes it
        to the settlement handler even though it is absent from the REVIEW
        options[] surface; the handler pops the staged settlement_confirm
        hard-stop (so ordinary commands are no longer held) while PRESERVING
        the scoped draft for same-turn reopen. This is the distinguishing
        behavior from `back_out_settlement`, which discards."""
        world = WorldState()
        _install_common_peace_war(world)
        terms = [{"type": "peace"}, _gold_indemnity_clause(150)]
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=terms,
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
        # The staged settlement_confirm is a hard-stop that would hold
        # ordinary commands at the executor gate.
        assert world.dialogue_manager.is_hard_stop() is True
        executor = DiplomaticExecutor(None)
        result = executor.handle_diplomatic_dialogue_response(
            "suspend_settlement_editor", {"world": world},
        )
        assert result.get("success") is True
        assert result.get("action") == "suspend_settlement_editor"
        assert result.get("mutated") is False
        # Bug fix: the hard-stop is popped so the next command is not held.
        assert world.dialogue_manager.is_hard_stop() is False
        # Scoped draft preserved verbatim for same-turn reopen.
        assert (
            load_scoped_settlement_draft(
                world,
                war_id="war_1",
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
            )
            == terms
        )


# ═══════════════════════════════════════════════════════════════════════════
# D. Active-vs-archived settlement review routing
# ═══════════════════════════════════════════════════════════════════════════


class TestActiveVsArchivedRouting:
    def test_main_war_settlement_clicked_routes_archived_war_to_history(self):
        """SC-5R-2: when the cached war list does NOT contain an active
        row for the clicked war_id, main.gd routes to the Diplomatic
        Ledger settlement history surface instead of POSTing a stale
        propose_common_peace."""
        click_body = _function_body(MAIN_SCRIPT, "_on_war_settlement_clicked")
        helper_body = _function_body(MAIN_SCRIPT, "_is_war_archived_in_cache")
        process_body = _function_body(MAIN_SCRIPT, "_process_active_wars")
        assert "_seen_war_ids[cached_war_id] = true" in process_body
        assert "return bool(_seen_war_ids.get(war_id, false))" in helper_body
        assert '"surface": "settlement_history"' in click_body
        # Routes the existing recovery_route helper so the existing
        # settlement_history wiring stays single-source.
        assert "_route_settlement_recovery_route" in click_body
        assert _return_lines(helper_body)[-1] != "return false"

    def test_main_war_settlement_clicked_continues_to_post_for_active_war(self):
        """Active wars still POST `propose_common_peace` so the live
        review surface mounts. The structured payload includes war_id,
        target_nation, and the propose_common_peace action."""
        click_body = _function_body(MAIN_SCRIPT, "_on_war_settlement_clicked")
        helper_body = _function_body(MAIN_SCRIPT, "_is_war_archived_in_cache")
        assert 'if str(w.get("war_instance_id", w.get("war_id", ""))) == war_id:' in helper_body
        assert '"action": "propose_common_peace"' in click_body

    def test_active_vs_archived_routing_guard_runs_before_post(self):
        """The archive check must run BEFORE the POST so a stale click
        does not waste a backend round trip. The early return uses
        `_route_settlement_recovery_route` for the ledger handoff."""
        click_body = _function_body(MAIN_SCRIPT, "_on_war_settlement_clicked")
        idx_archived = click_body.find("if _is_war_archived_in_cache(war_id):")
        idx_post = click_body.find('"action": "propose_common_peace"', idx_archived)
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

    def test_request_revision_response_mounts_editor_directly(self):
        """Request Revision is an explicit counter-editor action, so the
        backend asks Godot to mount EDIT immediately."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = handle_incoming_settlement_offer_action(
                world,
                action="request_settlement_revision",
                dialogue=offer,
            )
        assert result.get("success"), result
        assert result.get("open_editor_on_mount") is True
        staged = result.get("diplomatic_dialogue") or {}
        assert staged.get("can_edit_terms") is True
        assert staged.get("editor_route", {}).get("surface") == "settlement_editor"


# ═══════════════════════════════════════════════════════════════════════════
# F. Editor mount conditions match the SC-5R-1 EDIT payload contract
# ═══════════════════════════════════════════════════════════════════════════


class TestEditorMountGatesMatchBackendContract:
    def test_editor_mount_intercept_gated_on_can_edit_terms_true(self):
        """main.gd refuses to mount the editor when `can_edit_terms=false`,
        so AI-staged offers + legacy/typed callers fall through to the
        regular dialogue response path (the same path SC-5R-1 still
        owns)."""
        source = _read_source(MAIN_SCRIPT)
        # The intercept asserts can_edit_terms AND a non-empty editor_route.
        intercept = source.split('if action == "revise_settlement_terms":', 1)[1].split(
            "func", 1
        )[0]
        assert "can_edit_terms" in intercept
        assert "editor_route" in intercept
        assert "editor_route_data.size() > 0" in intercept

    def test_editor_show_editor_self_gates_on_backend_edit_contract(self):
        """The popup entry point refuses to mount unless the payload itself
        carries `can_edit_terms=true` and a non-empty editor_route. This
        protects non-main callers from handing AI/system/debug reviews to
        the editor."""
        body = _function_body(EDITOR_SCRIPT, "show_editor")
        gate_prefix = body.split("current_data = data.duplicate(true)", 1)[0]
        assert 'data.get("can_edit_terms", false)' in gate_prefix
        assert "return false" in gate_prefix
        assert "editor_route_data.size() == 0" in gate_prefix
        assert body.rstrip().endswith("return true")

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

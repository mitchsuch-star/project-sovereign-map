import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def gdscript_function_body(source: str, function_name: str) -> str:
    match = re.search(rf"^func {re.escape(function_name)}\([^\n]*\).*$", source, re.MULTILINE)
    assert match is not None, f"missing GDScript function {function_name}"
    start = match.end()
    next_func = re.search(r"^func [A-Za-z0-9_]+\(", source[start:], re.MULTILINE)
    end = start + next_func.start() if next_func else len(source)
    return source[start:end]


def gdscript_body_without_docstrings(body: str) -> str:
    return re.sub(r'"""[\s\S]*?"""', "", body)


def test_diplomacy_wizard_maps_open_settlement_without_cost_label() -> None:
    source = read_repo_file(
        "godot-client/project-sovereign/scripts/diplomacy_wizard.gd"
    )

    assert '"open_settlement"' in source
    assert 'return "propose common peace with " + nation' in source
    assert "disabled_reason_display" in source
    assert 'if dp_cost > 0:' in source
    assert 'if gold_cost > 0:' in source


def test_settlement_confirm_uses_review_payload_and_humanized_fields() -> None:
    """SC-5 / G2-Slice-4 inversion: the popup match arm now keys only on
    `settlement_confirm` while incoming offers are deferred-and-hidden;
    the legacy combined `"settlement_confirm", "incoming_settlement_offer"`
    arm is intentionally absent."""
    source = read_repo_file(
        "godot-client/project-sovereign/scripts/proposal_confirm_popup.gd"
    )

    # Combined arm removed by SC-5; lone `"settlement_confirm":` arm remains.
    assert '"settlement_confirm", "incoming_settlement_offer"' not in source
    assert '"settlement_confirm":' in source
    assert "review_sections" in source
    assert "covered_enemy_display_chips" in source
    assert "standing_display" in source
    assert "display_label" in source
    assert "code_display" in source
    assert "band_display" in source
    assert "Will %s accept this settlement?" in source
    assert "Settlement payload incomplete" in source
    assert 'data.get("actions"' not in source


def test_war_detail_and_notifications_preserve_settlement_route_ids() -> None:
    war_detail = read_repo_file(
        "godot-client/project-sovereign/scripts/war_detail_popup.gd"
    )
    notifications = read_repo_file(
        "godot-client/project-sovereign/scripts/notification_bar.gd"
    )
    main = read_repo_file("godot-client/project-sovereign/scripts/main.gd")

    assert "signal settlement_clicked(war_id: String, target_nation: String)" in war_detail
    assert "Open Whole-War Settlement" in war_detail
    assert 'war_data.get("settlement_available", false)' in war_detail
    assert "_shared_coalition_war_id" in war_detail
    assert "notification_review_requested(review_target: String, route_id: String, war_id: String)" in notifications
    assert "_on_notification_review_requested(review_target: String, route_id: String = \"\", war_id: String = \"\")" in main
    assert "send_structured_command" in main
    assert '"war_id": war_id' in main
    assert 'open_diplomatic_ledger_review("ledger_settlements", route_id, war_id)' in main


def test_war_status_and_ledger_do_not_depend_on_raw_settlement_labels() -> None:
    war_status = read_repo_file("backend/game_logic/war_status.py")
    panel = read_repo_file(
        "godot-client/project-sovereign/scripts/war_status_panel.gd"
    )
    ledger = read_repo_file(
        "godot-client/project-sovereign/scripts/diplomatic_ledger.gd"
    )

    assert '"standing_status_display"' in war_status
    assert "standing_status_display" in panel
    assert "display_label" in ledger
    assert "standing_display" in ledger
    assert "code_display" in ledger
    assert "band_display" in ledger
    assert "_humanize_label" in ledger


def test_backend_confirm_payload_carries_review_and_reopen_contract() -> None:
    preview = read_repo_file("backend/game_logic/settlement_preview.py")
    main = read_repo_file("backend/main.py")

    assert "build_settlement_review" in preview
    assert '"review_sections"' in preview
    assert '"Ratify Settlement"' in preview
    assert '"available_action_ids"' in preview
    assert '"actions": ["confirm_settlement"' not in preview
    assert '"reopen_target"' in preview
    assert '"review_route"' in preview
    assert '"settlement_result_feedback"' in preview
    assert '"error_display"' in preview
    assert '"disabled_reason_display"' in preview
    assert '"settlement_result_feedback"' in main


def test_backend_humanization_and_incoming_offer_contracts_are_pinned() -> None:
    display_names = read_repo_file("backend/display_names.py")
    preview = read_repo_file("backend/game_logic/settlement_preview.py")
    executor = read_repo_file("backend/commands/diplomatic_executor.py")
    helper = read_repo_file("backend/game_logic/settlement_helpers.py")

    assert "SETTLEMENT_DISABLED_REASON_DISPLAY" in display_names
    assert "ACCEPTANCE_COMPONENT_DISPLAY" in display_names
    assert "acceptance_band_phrase" in display_names
    assert "SIDE_LABEL_DISPLAY" in display_names
    assert "side_label_display" in display_names
    assert "unknown_settlement_action" in display_names
    assert "unknown_settlement_offer_action" in display_names
    assert "handle_incoming_settlement_offer_action" in preview
    assert "accept_settlement_offer" in executor
    assert "request_settlement_revision" in executor
    assert "requested_war_id" in helper
    assert "war_state_changed_since_open" in helper


def test_route_id_uses_event_format_consistently() -> None:
    """G2-Slice-3 SC-14c inversion: settlement route ids use the
    `settlement:{war_id}:{turn}:{seq}` namespace, minted from
    `mint_settlement_route_id(...)`. The reaction event consumes the
    staged value verbatim instead of recomputing."""
    preview = read_repo_file("backend/game_logic/settlement_preview.py")
    reactions = read_repo_file("backend/game_logic/settlement_reactions.py")

    # Legacy `settlement_summary:` prefix must remain absent.
    assert 'f"settlement_summary:{war_id}' not in preview
    # Legacy `{war_id}:{turn}` route id literal MUST NOT regress.
    assert 'f"{war_id}:{int(getattr(world, \'current_turn\', 0) or 0)}"' \
        not in preview
    assert 'f"{war_id}:{turn}"' not in reactions
    # New SC-14c surface: route id minting + namespace constant.
    assert "mint_settlement_route_id" in preview
    assert 'SETTLEMENT_ROUTE_NAMESPACE = "settlement"' in preview
    # Reaction emitters consume the staged route id and only fall back to
    # `mint_settlement_route_id` when no staged id was supplied.
    assert "staged_route_id" in reactions
    assert "mint_settlement_route_id" in reactions


def test_settlement_review_emits_uncovered_chips_and_side_labels() -> None:
    """Live preview path stamps `side_label` and `is_beneficiary` so the
    confirm popup never falls back to raw `attackers`/`defenders` enums."""
    presentation = read_repo_file(
        "backend/game_logic/settlement_presentation.py"
    )

    assert "side_label_display" in presentation
    assert '"side_label": side_label_display(side)' in presentation
    assert "uncovered_enemy_display_chips" in presentation
    assert "_beneficiaries_from_terms" in presentation
    assert '"is_beneficiary": nation in beneficiaries' in presentation


def test_main_gd_handles_must_reopen_and_auto_opens_ledger() -> None:
    """Settlement-result feedback should programmatically open the
    ledger, not just point at it; reopen_target must drive a real reopen."""
    main = read_repo_file("godot-client/project-sovereign/scripts/main.gd")

    assert "must_reopen" in main
    assert "reopen_target" in main
    assert "Reopening settlement review for" in main
    assert "did not provide a valid target" in main
    assert "Opening diplomatic ledger to settlement" in main
    # The wizard's structured-command signal is wired so open_settlement
    # forwards war_id to the backend.
    assert "_on_wizard_structured_command_selected" in main
    assert "structured_command_selected" in main


def test_settlement_dialogue_actions_never_fallback_to_command_synthesis() -> None:
    """Settlement popup choices must stay on the dialogue endpoint.

    The old generic fallback builds a natural-language command string,
    which can drop Revise Terms into the imperial command box instead of
    reopening the settlement popup flow.
    """
    main = read_repo_file("godot-client/project-sovereign/scripts/main.gd")
    handler = gdscript_function_body(main, "_on_proposal_confirm_choice")

    assert "SETTLEMENT_DIALOGUE_ACTIONS" in main
    assert "if action in SETTLEMENT_DIALOGUE_ACTIONS:" in handler
    assert "proposal_confirm_popup.show_dialogue(data)" in handler
    assert handler.index("if action in SETTLEMENT_DIALOGUE_ACTIONS:") < handler.index(
        'var command = "Talleyrand, %s the %s proposal"'
    )


def test_backend_hides_common_settlement_for_one_to_one_wizard_paths() -> None:
    display_names = read_repo_file("backend/display_names.py")
    preview = read_repo_file("backend/game_logic/settlement_preview.py")
    diplomacy = read_repo_file("backend/game_logic/diplomacy.py")

    assert "one_to_one_war" in display_names
    assert "is_common_settlement_worth_showing" in preview
    assert 'settlement_disabled_reason_display("one_to_one_war")' in diplomacy


def test_war_detail_refresh_honors_war_instance_id() -> None:
    war_detail = read_repo_file(
        "godot-client/project-sovereign/scripts/war_detail_popup.gd"
    )

    # Refresh must match war_instance_id when known so multi-war
    # disambiguation does not silently swap to a sibling war.
    assert "_current_war_id != \"\"" in war_detail
    assert "war_instance_id" in war_detail


def test_diplomacy_wizard_open_settlement_forwards_war_id() -> None:
    wizard = read_repo_file(
        "godot-client/project-sovereign/scripts/diplomacy_wizard.gd"
    )

    assert "structured_command_selected" in wizard
    assert "_structured_payload_for_action" in wizard
    assert '"action": "propose_common_peace"' in wizard


def test_diplomacy_wizard_structured_payload_helper_has_no_stray_command_emit() -> None:
    """Catch invalid unreachable GDScript left inside the helper body.

    Godot still parses unreachable statements, so an out-of-scope
    `command_selected.emit(command)` here breaks the wizard before the
    Open Settlement button can route its structured war_id.
    """
    wizard = read_repo_file(
        "godot-client/project-sovereign/scripts/diplomacy_wizard.gd"
    )
    body = gdscript_body_without_docstrings(
        gdscript_function_body(wizard, "_structured_payload_for_action")
    )

    assert "command_selected.emit" not in body
    assert re.search(r"\bcommand\b", body) is None


def test_acceptance_color_uses_band_code_only() -> None:
    """Color logic must compare the raw enum band_code, never the
    humanized `band` string — otherwise a wording change silently
    swaps the colour."""
    popup = read_repo_file(
        "godot-client/project-sovereign/scripts/proposal_confirm_popup.gd"
    )

    # The new color block uses if/elif on band_code; the regression
    # would re-introduce `band == "Near acceptable"`.
    assert 'band_code == "near_acceptable"' in popup
    assert 'band == "Near acceptable"' not in popup


def test_diplomatic_ledger_top_components_use_humanized_keys() -> None:
    """Inline acceptance section must read `component_display` and
    `value_display`, never the missing `name`/raw `value`."""
    ledger = read_repo_file(
        "godot-client/project-sovereign/scripts/diplomatic_ledger.gd"
    )

    assert "component_display" in ledger
    assert "value_display" in ledger

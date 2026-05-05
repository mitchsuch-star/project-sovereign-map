from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_diplomacy_wizard_maps_open_settlement_without_cost_label() -> None:
    source = read_repo_file(
        "godot-client/project-sovereign/scripts/diplomacy_wizard.gd"
    )

    assert '"open_settlement"' in source
    assert 'return "propose common peace with " + nation' in source
    assert 'if dp_cost > 0:' in source
    assert 'if gold_cost > 0:' in source


def test_settlement_confirm_uses_review_payload_and_humanized_fields() -> None:
    source = read_repo_file(
        "godot-client/project-sovereign/scripts/proposal_confirm_popup.gd"
    )

    assert '"settlement_confirm", "incoming_settlement_offer"' in source
    assert "review_sections" in source
    assert "covered_enemy_display_chips" in source
    assert "standing_display" in source
    assert "display_label" in source
    assert "code_display" in source
    assert "band_display" in source


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
    assert "_shared_coalition_war_id" in war_detail
    assert "notification_review_requested(review_target: String, route_id: String, war_id: String)" in notifications
    assert "_on_notification_review_requested(review_target: String, _route_id: String = \"\", _war_id: String = \"\")" in main


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
    assert '"reopen_target"' in preview
    assert '"settlement_result_feedback"' in preview
    assert '"error_display"' in preview
    assert '"settlement_result_feedback"' in main

"""G2-Slice-G2e same-war scope replace-confirm tests."""

from __future__ import annotations

import copy
import pathlib

from backend.game_logic.diplomatic_templates import resolve_settlement_voice_line
from backend.game_logic.settlement_preview import (
    compute_settlement_draft_key,
    handle_settlement_dialogue_action,
    load_scoped_settlement_draft,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _install_war(world: WorldState) -> dict:
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
        world.diplomatic_states[pair] = "WAR"
    world.invalidate_war_instance_indexes()
    return war


def _austrian_terms() -> list[dict]:
    return [
        {
            "type": "gold_indemnity",
            "from": "Austria",
            "to": "France",
            "amount": 200,
            "turns": 0,
        },
    ]


def _prussian_terms() -> list[dict]:
    return [
        {
            "type": "gold_indemnity",
            "from": "Prussia",
            "to": "France",
            "amount": 300,
            "turns": 0,
        },
    ]


def _stage_austria_then_prussia(world: WorldState) -> tuple[dict, dict]:
    first = stage_settlement_confirm(
        world,
        war_id="war_1",
        selected_target_nation="Austria",
        covered_enemy_participants=["Austria"],
        settlement_terms=_austrian_terms(),
    )
    assert first["success"] is True
    current_dialogue = copy.deepcopy(world.pending_diplomatic_dialogue)

    second = stage_settlement_confirm(
        world,
        war_id="war_1",
        selected_target_nation="Prussia",
        covered_enemy_participants=["Prussia"],
        settlement_terms=_prussian_terms(),
    )
    assert second["success"] is True
    return current_dialogue, second["diplomatic_dialogue"]


def test_same_war_different_scope_restage_returns_scope_replace_confirm():
    world = WorldState()
    _install_war(world)

    current_dialogue, chooser = _stage_austria_then_prussia(world)

    assert chooser["type"] == "settlement_scope_replace_confirm"
    assert chooser["dialogue_type"] == "settlement_scope_replace_confirm"
    assert world.pending_diplomatic_dialogue["type"] == "settlement_scope_replace_confirm"
    assert chooser["current_draft_key"] == current_dialogue["draft_key"]
    assert chooser["incoming_draft_key"] == compute_settlement_draft_key(
        "war_1", "Prussia", ["Prussia"],
    )
    assert chooser["current_scope"]["covered_enemy_participants"] == ["Austria"]
    assert chooser["incoming_scope"]["covered_enemy_participants"] == ["Prussia"]
    assert [opt["action"] for opt in chooser["options"]] == [
        "replace_current_scope_draft",
        "keep_current_scope_draft",
    ]
    assert chooser["outer_cancel_action"] == "keep_current_scope_draft"


def test_scope_replace_confirm_accept_replace_clears_existing_draft():
    world = WorldState()
    _install_war(world)
    current_dialogue, chooser = _stage_austria_then_prussia(world)
    old_key = current_dialogue["draft_key"]
    world.pending_settlement_drafts_by_key[old_key] = _austrian_terms()

    result = handle_settlement_dialogue_action(
        world,
        action="replace_current_scope_draft",
        dialogue=chooser,
    )

    assert result["success"] is True
    assert result["scope_replaced"] is True
    assert result["cleared_draft_key"] == old_key
    assert old_key not in world.pending_settlement_drafts_by_key
    assert world.pending_diplomatic_dialogue["type"] == "settlement_confirm"
    assert world.pending_diplomatic_dialogue["selected_target_nation"] == "Prussia"
    assert world.pending_diplomatic_dialogue["covered_enemy_participants"] == ["Prussia"]
    assert world.pending_diplomatic_dialogue["draft_key"] == result["draft_key"]
    assert any(
        term.get("from") == "Prussia" and term.get("amount") == 300
        for term in world.pending_diplomatic_dialogue["settlement_terms"]
    )
    assert not any(
        term.get("from") == "Austria"
        for term in world.pending_diplomatic_dialogue["settlement_terms"]
    )


def test_scope_replace_confirm_accept_keep_is_no_op_restoring_prior_popup():
    world = WorldState()
    _install_war(world)
    current_dialogue, chooser = _stage_austria_then_prussia(world)

    result = handle_settlement_dialogue_action(
        world,
        action="keep_current_scope_draft",
        dialogue=chooser,
    )

    assert result["success"] is True
    assert result["scope_replaced"] is False
    assert world.pending_diplomatic_dialogue["type"] == "settlement_confirm"
    assert world.pending_diplomatic_dialogue["draft_key"] == current_dialogue["draft_key"]
    assert world.pending_diplomatic_dialogue["selected_target_nation"] == "Austria"
    assert world.pending_diplomatic_dialogue["covered_enemy_participants"] == ["Austria"]
    assert world.pending_diplomatic_dialogue["settlement_terms"] == _austrian_terms()


def test_scope_replace_confirm_outer_cancel_treated_as_keep():
    world = WorldState()
    _install_war(world)
    current_dialogue, chooser = _stage_austria_then_prussia(world)

    result = handle_settlement_dialogue_action(
        world,
        action="back_out_settlement",
        dialogue=chooser,
    )

    assert result["success"] is True
    assert result["scope_replaced"] is False
    assert world.pending_diplomatic_dialogue["type"] == "settlement_confirm"
    assert world.pending_diplomatic_dialogue["draft_key"] == current_dialogue["draft_key"]
    assert world.pending_diplomatic_dialogue["selected_target_nation"] == "Austria"


def test_scope_replace_confirm_click_time_revalidation_handles_scope_flip():
    world = WorldState()
    _install_war(world)
    current_dialogue, chooser = _stage_austria_then_prussia(world)
    flipped = copy.deepcopy(chooser)
    flipped["incoming_request"]["selected_target_nation"] = "Austria"
    flipped["incoming_request"]["covered_enemy_participants"] = ["Austria"]

    result = handle_settlement_dialogue_action(
        world,
        action="replace_current_scope_draft",
        dialogue=flipped,
    )

    assert result["success"] is True
    assert result["scope_replaced"] is False
    assert result["scope_revalidation"] == "same_scope_no_replace"
    assert world.pending_diplomatic_dialogue["type"] == "settlement_confirm"
    assert world.pending_diplomatic_dialogue["draft_key"] == current_dialogue["draft_key"]
    assert world.pending_diplomatic_dialogue["selected_target_nation"] == "Austria"


def test_scope_replace_confirm_voice_and_godot_popup_variant_are_wired():
    voice = resolve_settlement_voice_line(
        "settlement_scope_replace_confirm_talleyrand",
        war_label="War of the Coalition",
        current_scope="Austria",
        incoming_scope="Prussia",
    )
    assert "Austria" in voice
    assert "Prussia" in voice
    assert "replace" in voice.lower()

    main_gd = (
        REPO_ROOT / "godot-client/project-sovereign/scripts/main.gd"
    ).read_text(encoding="utf-8")
    popup_gd = (
        REPO_ROOT / "godot-client/project-sovereign/scripts/proposal_confirm_popup.gd"
    ).read_text(encoding="utf-8")
    assert '"settlement_scope_replace_confirm"' in main_gd
    assert '"replace_current_scope_draft"' in main_gd
    assert '"keep_current_scope_draft"' in main_gd
    assert '"settlement_scope_replace_confirm":' in popup_gd
    assert "func _build_settlement_scope_replace_content" in popup_gd

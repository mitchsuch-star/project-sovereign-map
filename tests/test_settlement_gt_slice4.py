"""GT-Slice-4 — retire the freeform settlement editor (absence + routing).

`docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` §5 (complete removal/re-point
inventory) + §9 GT-Slice-4. The guided per-court rows (GT-Slices 1-3) are
the deep authoring tier; this slice deletes the SC-5R editor and re-points
every editor producer at the guided PROPOSE surface. Pinned here:

- ABSENCE: the editor scene/script are gone; main.gd carries no editor
  wiring; settlement_preview.py carries no identity-picker schema; the
  /command CommandRequest carries no settlement submit-blob fields.
- ROUTING: every §5 re-point lands guided PROPOSE — the blocked-REVIEW
  re-author replacement arm, and (covered in their home files) the
  re_author direct arm, incoming-offer counter-authoring, and the
  same-war single-source-of-truth refresh.
- VERIFY-DEAD: the old editor structured POST body is stripped at the
  Pydantic boundary — it can no longer stage a submitted blob as REVIEW.
- COPY: the PF-1 budget-bound carry hint points at the court row's
  territory offer, not the retired 'Adjust terms'.
- The V4 self-liberation validator rejection survives the deletion of the
  slice-0 picker tests (the validator, not the picker, is the authority).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.game_logic.settlement_preview import (
    _settlement_propose_carry_hint,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance
from tests.test_settlement_sc5r2_godot_editor import (
    _acceptance_accepts,
    _gold_indemnity_clause,
    _install_common_peace_war,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_ROOT = REPO_ROOT / "godot-client" / "project-sovereign"


# ===========================================================================
# Fixtures
# ===========================================================================


def _install_losing_war(world: WorldState, *, war_score_against_france: int = 70) -> dict:
    """France (proposer) losing badly: side_pressure_score <= -20 so the
    concession baseline is visible."""
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
        world.war_scores[pair] = (
            war_score_against_france
            if a in ("Austria", "Prussia")
            else -war_score_against_france
        )
    world.invalidate_war_instance_indexes()
    return war


# ===========================================================================
# 1. Absence — the editor and its contract are gone everywhere
# ===========================================================================


def test_settlement_editor_scene_and_script_are_deleted():
    assert not (GODOT_ROOT / "scenes" / "settlement_editor_popup.tscn").exists()
    assert not (GODOT_ROOT / "scripts" / "settlement_editor_popup.gd").exists()


def test_main_gd_carries_no_settlement_editor_wiring():
    main_gd = (GODOT_ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
    for retired in (
        "settlement_editor_popup",
        "open_editor_on_mount",
        "_maybe_remount_settlement_editor_after_error",
        "_remember_settlement_editor_payload",
        "_on_settlement_editor_submit",
        'if action == "adjust_terms":',
        'if action == "revise_settlement_terms":',
        "editor_route",
        "can_edit_terms",
    ):
        assert retired not in main_gd, retired
    # The non-destructive PROPOSE Back Out action id is the one intentional
    # survivor of the editor's naming.
    assert '"suspend_settlement_editor"' in main_gd


def test_settlement_preview_carries_no_identity_picker_schema():
    import backend.game_logic.settlement_preview as sp

    for retired_symbol in (
        "_build_clause_control_schema_for_review",
        "_clause_fields_for_review",
        "_nation_control_options",
        "_side_partitioned_options",
        "_region_control_options",
        "_build_settlement_editor_route",
        "merge_same_war_settlement_drafts",
        "SETTLEMENT_EDITOR_SOURCES",
    ):
        assert not hasattr(sp, retired_symbol), retired_symbol
    # The eligibility + candidate-generation helpers the guided suggestions
    # reuse are KEPT (spec §5: removal is the schema build, not these).
    for kept_symbol in (
        "evaluate_vassalage_eligibility",
        "evaluate_subjugation_eligibility",
        "evaluate_liberation_eligibility",
    ):
        assert hasattr(sp, kept_symbol), kept_symbol


def test_command_request_carries_no_settlement_submit_fields():
    from backend.main import CommandRequest

    fields = set(CommandRequest.model_fields)
    for retired_field in (
        "settlement_terms",
        "selected_target_nation",
        "covered_enemy_participants",
    ):
        assert retired_field not in fields, retired_field
    # PF-2 reopen + wizard transports stay.
    assert "target_nation" in fields
    assert "war_id" in fields


def test_staged_dialogue_never_carries_editor_contract_keys():
    world = WorldState()
    _install_common_peace_war(world)
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_acceptance_accepts,
    ):
        for mode in ("PROPOSE", "REVIEW"):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[{"type": "peace"}, _gold_indemnity_clause()],
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
                dialogue_mode=mode,
            )
            dialogue = staged["diplomatic_dialogue"]
            for retired_key in (
                "can_edit_terms",
                "available_clause_types",
                "clause_control_schema",
                "editor_route",
            ):
                assert retired_key not in dialogue, (mode, retired_key)
            world.dialogue_manager.pop()


# ===========================================================================
# 2. Routing — the §5 re-points land guided PROPOSE
# ===========================================================================


def test_apply_concession_baseline_replacement_stages_guided_propose_not_editor():
    """§5 re-point: the blocked-REVIEW replacement arm re-stages the guided
    PROPOSE surface seeded with Talleyrand's concession baseline — no editor
    mount flag, ever."""
    world = WorldState()
    world.nation_gold = {
        "France": 5000,
        "Austria": 3000,
        "Prussia": 3000,
        "Saxony": 1000,
    }
    _install_losing_war(world)
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        settlement_terms=[{"type": "peace"}],
        selected_target_nation="Austria",
        covered_enemy_participants=["Austria", "Prussia"],
        caller_kind="player_editor",
        dialogue_mode="REVIEW",
    )
    assert staged.get("success"), staged
    review_dialogue = staged["diplomatic_dialogue"]

    result = handle_settlement_dialogue_action(
        world,
        action="apply_concession_baseline_replacement",
        dialogue=review_dialogue,
    )
    assert result.get("success"), result
    assert "open_editor_on_mount" not in result
    refreshed = result.get("diplomatic_dialogue") or {}
    assert refreshed.get("dialogue_mode") == "PROPOSE"
    # Seeded from the baseline: material concessions beyond the peace floor.
    assert any(
        t.get("type") != "peace" for t in (refreshed.get("settlement_terms") or [])
    )


# ===========================================================================
# 3. Verify-dead — the old editor POST body cannot stage a submitted blob
# ===========================================================================


@pytest.fixture()
def _http_client_with_war():
    import backend.main as main_module
    from backend.commands.parser import CommandParser

    world = WorldState()
    _install_common_peace_war(world)
    main_module._set_active_world(world)
    original_parser = main_module.parser
    main_module.parser = CommandParser(use_real_llm=False)
    try:
        yield TestClient(main_module.app), world
    finally:
        main_module.parser = original_parser


def test_old_editor_submit_body_is_stripped_and_lands_guided_propose(
    _http_client_with_war,
):
    """Verify-dead regression: the retired editor's structured POST body is
    stripped at the Pydantic boundary. The submitted blob can never stage as
    REVIEW; opening a settlement always lands the guided PROPOSE surface and
    the blob's marker clause (gold 4321) never appears."""
    client, _world = _http_client_with_war
    body = {
        "command": "propose common peace with Austria",
        "action": "propose_common_peace",
        "war_id": "war_1",
        "selected_target_nation": "Austria",
        "covered_enemy_participants": ["Austria", "Prussia"],
        "settlement_terms": [{"type": "peace"}, _gold_indemnity_clause(4321)],
        "caller_kind": "player_editor",
    }
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_acceptance_accepts,
    ):
        response = client.post("/command", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True, data
    dialogue = data.get("diplomatic_dialogue") or {}
    assert dialogue.get("dialogue_mode") == "PROPOSE"
    amounts = [
        int(t.get("amount", 0))
        for t in (dialogue.get("settlement_terms") or [])
        if t.get("type") == "gold_indemnity"
    ]
    assert 4321 not in amounts, amounts


# ===========================================================================
# 4. Copy — the carry hint points at the court row, not 'Adjust terms'
# ===========================================================================


def test_budget_bound_carry_hint_copy_points_at_row_territory_offer():
    hint = _settlement_propose_carry_hint(
        ["Austria"],
        [{"nation": "Austria", "total": 30, "hard_stops": []}],
        budget_bound_constraint={"budget_bound": True},
    )
    assert "add a territory offer on the court's row" in hint
    assert "Adjust terms" not in hint


# ===========================================================================
# 5. Validator authority survives the picker deletion (slice-0 transplant)
# ===========================================================================


def test_tampered_self_referential_liberation_rejected_by_validator():
    """France-liberates-France stays dead without the picker: a tampered
    self-referential liberation clause is rejected pre-stage by the
    validator (V4 — France is not a vassal of anyone)."""
    world = WorldState()
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
    world.invalidate_war_instance_indexes()
    world.vassals["Bavaria"] = {"lord": "France", "lord_nation": "France"}

    result = validate_settlement_terms(
        [
            {
                "type": "liberation",
                "vassal_nation": "France",
                "lord_nation": "France",
                "liberator": "France",
            }
        ],
        world=world,
        war_instance=war,
    )
    assert result["valid"] is False
    assert result["error"] == "liberation_target_not_vassal"

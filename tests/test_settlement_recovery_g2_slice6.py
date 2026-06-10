"""G2-Slice-6 settlement recovery and smoke-fixture evidence tests."""

from __future__ import annotations

from backend.game_logic.settlement_preview import (
    evaluate_war_detail_actionability,
    handle_settlement_dialogue_action,
    load_scoped_settlement_draft,
    record_reopen_attempt,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.models.world_state import (
    SMOKE_START_ENV,
    SMOKE_START_SETTLEMENT_LOSING,
    SMOKE_START_SETTLEMENT_MULTIWAR_AMBIGUITY,
    SMOKE_START_SETTLEMENT_REJECTED,
    WorldState,
)
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


def _install_rejected_war(world: WorldState) -> dict:
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
        a, _ = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 70 if a != "France" else -70
    world.war_exhaustion["Austria"] = 5
    world.invalidate_war_instance_indexes()
    return war


def test_war_detail_actionability_helper_schema_matches_canonical_keys():
    world = WorldState()
    _install_rejected_war(world)

    result = evaluate_war_detail_actionability(
        world,
        war_id="war_1",
        selected_target_nation="Austria",
        covered_enemy_participants=["Austria", "Prussia"],
        source_route_id="settlement:war_1:1:1",
    )

    assert result["actionable"] is True
    assert result["refusal_code"] == ""
    assert result["peace_seeking_controls"] == ["negotiate_peace"]
    assert result["recovery_route"] == {
        "surface": "war_detail",
        "target": "war_detail",
        "war_id": "war_1",
        "selected_target_nation": "Austria",
        "target_nation": "Austria",
        "nation": "Austria",
        "covered_enemy_participants": ["Austria", "Prussia"],
        "source_route_id": "settlement:war_1:1:1",
        "reason": "blocked_settlement_recovery",
    }


def test_war_detail_actionability_negative_hides_open_war_detail_recovery():
    world = WorldState()
    _install_rejected_war(world)

    missing = evaluate_war_detail_actionability(
        world, war_id="war_1", selected_target_nation="",
    )
    assert missing["actionable"] is False
    assert missing["refusal_code"] == "selected_pair_missing"
    assert "recovery_route" not in missing

    world.diplomatic_states["Austria|France"] = "PEACE"
    resolved = evaluate_war_detail_actionability(
        world, war_id="war_1", selected_target_nation="Austria",
    )
    assert resolved["actionable"] is False
    assert resolved["refusal_code"] == "pair_not_at_war"


def test_blocked_settlement_recovery_affordance_schema():
    world = WorldState()
    _install_rejected_war(world)

    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria", "Prussia"],
        selected_target_nation="Austria",
    )

    assert staged["success"] is True
    dialogue = staged["diplomatic_dialogue"]
    assert dialogue["can_ratify"] is False
    actions = [option["action"] for option in dialogue["options"]]
    assert "confirm_settlement" not in actions
    assert "open_war_detail" in actions
    assert "propose_peace" not in actions
    assert "propose_armistice" not in actions
    assert dialogue["war_detail_actionability"]["actionable"] is True
    assert dialogue["recovery_route"]["surface"] == "war_detail"


def test_open_war_detail_recovery_preserves_non_empty_draft_without_discard_prompt():
    world = WorldState()
    _install_rejected_war(world)
    terms = [{"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 100}]
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        settlement_terms=terms,
        covered_enemy_participants=["Austria"],
        selected_target_nation="Austria",
    )
    dialogue = staged["diplomatic_dialogue"]

    result = handle_settlement_dialogue_action(
        world, action="open_war_detail", dialogue=dialogue,
    )

    assert result["success"] is True
    assert result["draft_preserved"] is True
    assert result["recovery_route"]["surface"] == "war_detail"
    assert world.pending_diplomatic_dialogue is None
    # CH-3: the preserved draft lives in the scoped store.
    assert load_scoped_settlement_draft(
        world,
        war_id="war_1",
        selected_target_nation="Austria",
        covered_enemy_participants=["Austria"],
    ) == terms
    assert "had_draft" not in result


def test_sc14b_attempt_4_runs_actionability_probe_and_falls_back_when_dead():
    from backend.game_logic.settlement_routes import _safe_reopen_response

    world = WorldState()
    _install_rejected_war(world)
    for _ in range(3):
        record_reopen_attempt(world, war_id="war_1")

    live_payload = _safe_reopen_response(
        world,
        war_id="war_1",
        dialogue={
            "selected_target_nation": "Austria",
            "covered_enemy_participants": ["Austria"],
            "route_id": "settlement:war_1:1:1",
        },
    )
    assert live_payload["must_reopen"] is False
    assert live_payload["error"] == "reopen_attempt_cap_exceeded"
    assert live_payload["recovery_route"]["surface"] == "war_detail"
    assert live_payload["war_detail_actionability"]["actionable"] is True

    world.diplomatic_states["Austria|France"] = "PEACE"
    dead_payload = _safe_reopen_response(
        world,
        war_id="war_1",
        dialogue={
            "selected_target_nation": "Austria",
            "covered_enemy_participants": ["Austria"],
        },
    )
    assert dead_payload["must_reopen"] is False
    assert dead_payload["war_detail_actionability"]["actionable"] is False
    assert "recovery_route" not in dead_payload
    assert "terminal_recovery_copy" in dead_payload


def test_draft_discard_notice_clear_flag_is_persisted_at_render_time():
    world = WorldState()
    save_scoped_settlement_draft(
        world,
        war_id="war_1",
        selected_target_nation="Austria",
        covered_enemy_participants=["Austria"],
        settlement_terms=[{"type": "peace"}],
    )

    world.advance_turn()

    assert world.pending_settlement_drafts_by_key == {}
    assert len(world.pending_settlement_draft_notices) == 1
    saved_before_render = world.to_dict()
    drained = world.drain_settlement_draft_notices()
    assert drained[0]["war_id"] == "war_1"
    assert world.pending_settlement_draft_notices == []
    saved_after_render = world.to_dict()

    assert saved_before_render["pending_settlement_draft_notices"]
    assert saved_after_render["pending_settlement_draft_notices"] == []
    restored = WorldState.from_dict(saved_before_render)
    assert restored.pending_settlement_draft_notices[0]["war_id"] == "war_1"


def test_smoke_start_rejected_fixture_opens_blocked_recovery(monkeypatch):
    monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_REJECTED)

    world = WorldState()
    result = stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        selected_target_nation="Britain",
    )

    assert world.settlement_smoke_fixture["name"] == SMOKE_START_SETTLEMENT_REJECTED
    dialogue = result["diplomatic_dialogue"]
    assert dialogue["can_ratify"] is False
    assert "confirm_settlement" not in dialogue["available_action_ids"]
    assert "open_war_detail" in dialogue["available_action_ids"]


def test_smoke_start_losing_fixture_has_concession_baseline_inputs(monkeypatch):
    monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_LOSING)

    world = WorldState()

    assert world.settlement_smoke_fixture["name"] == SMOKE_START_SETTLEMENT_LOSING
    assert world.settlement_smoke_fixture["concession_region"] == "Waterloo"
    assert world.nation_gold["France"] >= 1500
    assert world.regions["Waterloo"].controller == "France"


def test_smoke_start_multiwar_ambiguity_fixture_has_multiple_war_instances(monkeypatch):
    monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_MULTIWAR_AMBIGUITY)

    world = WorldState()

    assert world.settlement_smoke_fixture["name"] == SMOKE_START_SETTLEMENT_MULTIWAR_AMBIGUITY
    assert len(world.war_instances) >= 2
    assert len(world.settlement_smoke_fixture["war_ids"]) == len(world.war_instances)

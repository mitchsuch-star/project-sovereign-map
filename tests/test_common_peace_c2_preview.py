"""Slice C2 settlement preview/dialogue contract tests."""

from __future__ import annotations

import copy

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.diplomacy import get_available_diplomatic_actions
from backend.game_logic.settlement_preview import (
    build_settlement_preview,
    evaluate_open_settlement_eligibility,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


def _install_common_peace_war(world: WorldState) -> dict:
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
        world.war_scores[pair] = 70 if a == "Austria" else -70
    world.war_exhaustion["Austria"] = 30
    world.invalidate_war_instance_indexes()
    return war


def test_open_settlement_eligibility_available_for_side_leader():
    world = WorldState()
    _install_common_peace_war(world)

    result = evaluate_open_settlement_eligibility(world, war_id="war_1")

    assert result["available"] is True
    assert result["proposer_side"] == "attackers"
    assert result["accepting_side"] == "defenders"
    assert result["coverable_enemy_participants"] == ["Austria", "Prussia"]


def test_open_settlement_eligibility_rejects_non_leader():
    world = WorldState()
    _install_common_peace_war(world)

    result = evaluate_open_settlement_eligibility(
        world, war_id="war_1", actor_nation="Saxony",
    )

    assert result["available"] is False
    assert result["error"] == "not_side_leader"


def test_open_settlement_action_appears_with_spec_greyout_reason():
    world = WorldState()
    _install_common_peace_war(world)

    actions = get_available_diplomatic_actions(world, "Austria")

    action = next(a for a in actions if a["action"] == "open_settlement")
    assert action["available"] is True
    assert action["dp_cost"] == 0
    assert action["war_id"] == "war_1"


def test_settlement_preview_is_no_mutation_and_exposes_acceptance():
    world = WorldState()
    _install_common_peace_war(world)
    before_states = dict(world.diplomatic_states)
    before_instances = copy.deepcopy(world.war_instances)

    result = build_settlement_preview(
        world,
        war_id="war_1",
        settlement_terms=[
            {
                "type": "territory_cede",
                "from": "Austria",
                "to": "France",
                "regions": ["Bohemia"],
            },
        ],
    )

    assert result["success"] is True
    assert result["mode"] == "settlement"
    assert result["mutated"] is False
    assert "acceptance_components" in result["settlement_preview"]
    assert dict(world.diplomatic_states) == before_states
    assert world.war_instances == before_instances


def test_stage_settlement_confirm_creates_hard_stop_without_mutation():
    world = WorldState()
    _install_common_peace_war(world)
    before_states = dict(world.diplomatic_states)

    result = stage_settlement_confirm(
        world,
        war_id="war_1",
        settlement_terms=[{"type": "forced_alliance", "from": "Austria", "to": "France"}],
    )

    dialogue = world.pending_diplomatic_dialogue
    assert result["success"] is True
    assert dialogue["type"] == "settlement_confirm"
    assert world.dialogue_manager.is_hard_stop() is True
    assert "available_action_ids" in dialogue
    assert "back_out_settlement" in dialogue["available_action_ids"]
    assert "actions" not in dialogue
    # Options are gated by acceptance; at minimum Back Out is present.
    assert any(o["action"] == "back_out_settlement" for o in dialogue["options"])
    assert "review_sections" in dialogue
    assert dict(world.diplomatic_states) == before_states


def test_stage_settlement_confirm_preempts_without_dropping_existing_dialogue():
    world = WorldState()
    _install_common_peace_war(world)
    existing = {
        "type": "incoming_proposal",
        "from": "Austria",
        "target_nation": "Austria",
        "options": [{"label": "Acknowledge", "action": "dismiss"}],
        "blocking": False,
        "turn_created": world.current_turn,
    }
    world.dialogue_manager.replace(existing)

    result = stage_settlement_confirm(world, war_id="war_1", settlement_terms=[])

    assert result["success"] is True
    assert world.pending_diplomatic_dialogue["type"] == "settlement_confirm"
    assert world.dialogue_manager.pop()["type"] == "settlement_confirm"
    assert world.pending_diplomatic_dialogue["type"] == "incoming_proposal"


def test_settlement_back_out_and_revise_do_not_mutate():
    world = WorldState()
    _install_common_peace_war(world)
    before_states = dict(world.diplomatic_states)
    executor = DiplomaticExecutor.__new__(DiplomaticExecutor)

    stage_settlement_confirm(world, war_id="war_1", settlement_terms=[])
    back_out = executor.handle_diplomatic_dialogue_response(
        "back out", {"world": world},
    )

    assert back_out["success"] is True
    assert back_out["mutated"] is False
    assert world.pending_diplomatic_dialogue is None
    assert dict(world.diplomatic_states) == before_states

    from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
    stage_settlement_confirm(world, war_id="war_1", settlement_terms=[])
    dialogue = world.pending_diplomatic_dialogue
    revise = handle_settlement_dialogue_action(
        world, action="revise_settlement_terms", dialogue=dialogue,
    )

    # SC-2: Revise Terms is now hidden/blocked until real editor exists.
    assert revise["success"] is False
    assert revise["error"] == "revision_not_available"
    assert revise["mutated"] is False
    assert dict(world.diplomatic_states) == before_states


def test_settlement_confirm_revalidation_blocks_changed_pair_without_mutation():
    from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
    world = WorldState()
    war = _install_common_peace_war(world)
    before_states = dict(world.diplomatic_states)

    # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 empty-Ratify gate
    # short-circuits before pair revalidation, so author a minimum
    # legitimate peace package and probe the pair-changed guard.
    stage_settlement_confirm(
        world, war_id="war_1", settlement_terms=[{"type": "peace"}],
    )
    dialogue = world.pending_diplomatic_dialogue
    pair = war["active_diplo_keys"][0]
    war["active_diplo_keys"].remove(pair)
    war["resolved_diplo_keys"].append(pair)
    war["diplo_key_meta"][pair]["pair_status"] = "resolved"

    # Call handler directly to bypass options gate (SC-3 may hide ratify).
    result = handle_settlement_dialogue_action(
        world, action="confirm_settlement", dialogue=dialogue,
    )

    assert result["success"] is False
    assert result["error"] == "active_pair_changed"
    assert result["mutated"] is False
    assert dict(world.diplomatic_states) == before_states

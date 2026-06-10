"""G2-Slice-G2b ally settlement petition behavior tests."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.game_logic.diplomacy import create_war_objective, set_diplomatic_state
from backend.game_logic.settlement_preview import (
    ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
    build_ally_settlement_petition_popup,
    build_settlement_preview,
    handle_ally_settlement_petition_action,
    handle_incoming_settlement_offer_action,
    queue_ally_settlement_petitions_for_player_action,
    stage_settlement_confirm,
)
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# CH-1 stable-seam note: the scorer is patched at
# backend.game_logic.settlement_scoring.calculate_common_peace_acceptance,
# so wrap-the-real side effects must capture the real function at import
# time (a lazy import inside the side effect would fetch the mock).
from backend.game_logic.settlement_scoring import (
    calculate_common_peace_acceptance as _REAL_COMMON_PEACE_ACCEPTANCE,
)


def _install_war(
    world: WorldState,
    war_id: str,
    *,
    attackers: tuple[str, ...],
    defenders: tuple[str, ...],
    attacker_leader: str,
    defender_leader: str,
) -> Mapping[str, object]:
    war = make_synthetic_war_instance(
        war_id,
        attackers=list(attackers),
        defenders=list(defenders),
        attacker_leader=attacker_leader,
        defender_leader=defender_leader,
        created_turn=int(world.current_turn),
    )
    world.war_instances[war_id] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 70
    world.invalidate_war_instance_indexes()
    return war


def _seed_request_open_world() -> WorldState:
    world = WorldState()
    world.current_turn = 5
    _install_war(
        world,
        "war_1",
        attackers=("France",),
        defenders=("Austria", "Britain"),
        attacker_leader="France",
        defender_leader="Austria",
    )
    _install_war(
        world,
        "war_2",
        attackers=("Saxony",),
        defenders=("Prussia",),
        attacker_leader="Saxony",
        defender_leader="Prussia",
    )
    set_diplomatic_state(world, "France", "Saxony", "ALLIANCE", "test")
    key = world._make_diplo_key("Saxony", "Prussia")
    world.war_objectives[key] = {
        "Saxony": create_war_objective(
            "conquest",
            "Saxony",
            "Prussia",
            ["Berlin"],
            world.current_turn,
        )
    }
    return world


def _seed_warn_sellout_world() -> WorldState:
    world = WorldState()
    world.current_turn = 5
    _install_war(
        world,
        "war_1",
        attackers=("France", "Saxony"),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    set_diplomatic_state(world, "France", "Saxony", "ALLIANCE", "test")
    key = world._make_diplo_key("Saxony", "Austria")
    world.war_objectives[key] = {
        "Saxony": create_war_objective(
            "conquest",
            "Saxony",
            "Austria",
            ["Vienna"],
            world.current_turn,
        )
    }
    return world


def _all_dialogues(world: WorldState) -> list[Mapping[str, object]]:
    dm = world.dialogue_manager
    items = []
    current = dm.peek()
    if isinstance(current, Mapping):
        items.append(current)
    items.extend(d for d in dm.iter_queue() if isinstance(d, Mapping))
    return items


def _ally_petitions(world: WorldState) -> list[Mapping[str, object]]:
    return [
        d
        for d in _all_dialogues(world)
        if d.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
    ]


def _acceptance_accepts(*args, **kwargs):
    real = _REAL_COMMON_PEACE_ACCEPTANCE
    result = real(*args, **kwargs)
    result["score"] = 100
    result["verdict"] = "accept"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    result["side_pressure_score"] = 70
    return result


def _sellout_terms() -> list[dict[str, object]]:
    return [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 50},
    ]


def _player_facing_source_text() -> str:
    chunks: list[str] = []
    for root in (REPO_ROOT / "backend", REPO_ROOT / "godot-client"):
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".gd"}:
                continue
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


@pytest.fixture()
def fastapi_client():
    from backend import main as backend_main

    backend_main.game_state["world"] = WorldState()
    backend_main.game_state["debug_mode"] = False
    return TestClient(backend_main.app), backend_main


def test_ally_petition_request_open_settlement_fires_on_solicited_trigger():
    world = _seed_request_open_world()

    result = stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        selected_target_nation="Austria",
    )

    assert result["success"] is True
    assert world.dialogue_manager.peek()["type"] == "settlement_confirm"
    petitions = _ally_petitions(world)
    assert len(petitions) == 1
    assert petitions[0]["petition_type"] == "request_open_settlement"
    assert petitions[0]["trigger_action"] == "open_settlement"
    assert result["ally_settlement_petitions"][0]["ally_nation"] == "Saxony"


def test_ally_petition_request_open_settlement_mailbox_payload_routes_through_popup(
    fastapi_client,
):
    client, backend_main = fastapi_client
    world = _seed_request_open_world()
    backend_main.game_state["world"] = world
    queued = queue_ally_settlement_petitions_for_player_action(
        world,
        trigger_action="open_settlement",
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        settlement_terms=[],
    )

    assert len(queued) == 1
    assert DialogueManager.PERSISTENT_MAILBOX_TYPES >= {"ally_settlement_petition"}
    mailbox = client.get("/mailbox").json()
    assert mailbox["count"] == 1
    assert mailbox["items"][0]["item_type"] == "ally_settlement_petition"
    assert mailbox["items"][0]["source_nation"] == "Saxony"

    pending = client.get("/pending_envoy").json()
    assert pending["has_pending"] is True
    assert pending["dialogue_type"] == "ally_settlement_petition"
    popup = pending["diplomatic_dialogue"]
    assert popup["type"] == "ally_settlement_petition"
    assert popup["petition_type"] == "request_open_settlement"
    assert "acknowledge_ally_settlement_petition" in popup["available_action_ids"]

    activated = client.post(
        "/mailbox/activate",
        json={"mailbox_id": mailbox["items"][0]["mailbox_id"]},
    ).json()
    assert activated["success"] is True
    assert activated["diplomatic_dialogue"]["type"] == "ally_settlement_petition"
    handled = handle_ally_settlement_petition_action(
        world,
        action="acknowledge_ally_settlement_petition",
        dialogue=world.dialogue_manager.peek(),
    )
    assert handled["success"] is True
    assert world.dialogue_manager.get_mailbox_count() == 0


def test_ally_petition_request_open_settlement_does_not_block_player_ratification():
    world = _seed_request_open_world()

    result = stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        selected_target_nation="Austria",
    )

    assert result["success"] is True
    assert "ally_settlement_petition" not in DialogueManager.HARD_STOP_TYPES
    assert world.dialogue_manager.peek()["type"] == "settlement_confirm"
    assert _ally_petitions(world)[0]["blocking"] is False


def test_ally_petition_warn_against_sellout_fires_on_settlement_excluding_ally():
    world = _seed_warn_sellout_world()

    with patch(
        "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
        side_effect=_acceptance_accepts,
    ):
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            selected_target_nation="Austria",
            settlement_terms=_sellout_terms(),
        )

    assert result["success"] is True
    petitions = _ally_petitions(world)
    assert len(petitions) == 1
    assert petitions[0]["petition_type"] == "warn_against_sellout"
    assert petitions[0]["claim_region"] == "Vienna"
    assert petitions[0]["target_enemy"] == "Austria"


def test_ally_petition_warn_against_sellout_does_not_block_ratification():
    world = _seed_warn_sellout_world()

    with patch(
        "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
        side_effect=_acceptance_accepts,
    ):
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            selected_target_nation="Austria",
            settlement_terms=_sellout_terms(),
        )

    dialogue = result["diplomatic_dialogue"]
    assert dialogue["type"] == "settlement_confirm"
    assert "confirm_settlement" in dialogue["available_action_ids"]
    assert world.dialogue_manager.peek()["type"] == "settlement_confirm"
    assert _ally_petitions(world)[0]["blocking"] is False


def test_ally_petition_warn_against_sellout_renders_named_ally_voice_not_generic_chancery():
    world = _seed_warn_sellout_world()

    with patch(
        "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
        side_effect=_acceptance_accepts,
    ):
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            selected_target_nation="Austria",
            settlement_terms=_sellout_terms(),
        )

    petition = _ally_petitions(world)[0]
    popup = build_ally_settlement_petition_popup(petition)
    assert "Einsiedel" in popup["ally_voice"]
    assert "chancery" not in popup["ally_voice"].lower()
    inline = result["diplomatic_dialogue"]["ally_petitions"][0]
    assert "Einsiedel" in inline["ally_voice"]

    godot_popup = (
        REPO_ROOT
        / "godot-client"
        / "project-sovereign"
        / "scripts"
        / "proposal_confirm_popup.gd"
    ).read_text(encoding="utf-8")
    assert '"ally_settlement_petition":' in godot_popup
    assert "_build_ally_settlement_petition_content" in godot_popup


def test_ally_petition_warn_against_sellout_fires_on_rejected_incoming_offer():
    world = _seed_warn_sellout_world()
    offer = {
        "type": "incoming_settlement_offer",
        "dialogue_type": "incoming_settlement_offer",
        "offer_id": "settlement_offer:war_1:5:1",
        "war_id": "war_1",
        "proposer_nation": "Austria",
        "covered_enemy_participants": ["Austria"],
        "settlement_terms": _sellout_terms(),
        "turn_created": world.current_turn,
        "blocking": False,
    }
    world.dialogue_manager.push(dict(offer))

    result = handle_incoming_settlement_offer_action(
        world,
        action="reject_settlement_offer",
        dialogue=offer,
    )

    assert result["success"] is True
    petitions = _ally_petitions(world)
    assert len(petitions) == 1
    assert petitions[0]["petition_type"] == "warn_against_sellout"
    assert petitions[0]["trigger_action"] == "reject_settlement_offer"
    assert (
        result["ally_settlement_petitions"][0]["petition_key"]
        == petitions[0]["petition_key"]
    )


def test_ally_petition_request_consultation_removed_from_player_facing_scope():
    assert "request_consultation" not in _player_facing_source_text()


def test_ally_petition_request_redress_after_settlement_removed_from_player_facing_scope():
    assert "request_redress_after_settlement" not in _player_facing_source_text()


def test_ally_petitions_fire_only_in_response_to_named_player_actions():
    world = _seed_request_open_world()

    not_solicited = queue_ally_settlement_petitions_for_player_action(
        world,
        trigger_action="layout_tolerance",
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        settlement_terms=[],
    )
    assert not_solicited == []
    assert _ally_petitions(world) == []

    solicited = queue_ally_settlement_petitions_for_player_action(
        world,
        trigger_action="open_settlement",
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        settlement_terms=[],
    )
    assert len(solicited) == 1
    assert solicited[0]["petition_type"] in {
        "request_open_settlement",
        "warn_against_sellout",
    }


def test_ally_petitions_do_not_fire_on_pure_cooldown_without_player_trigger():
    world = _seed_request_open_world()
    world.current_turn += 4

    preview = build_settlement_preview(
        world,
        war_id="war_1",
        actor_nation="France",
    )
    assert preview["success"] is True
    assert _ally_petitions(world) == []

    cooldown = queue_ally_settlement_petitions_for_player_action(
        world,
        trigger_action="cooldown",
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        settlement_terms=[],
    )
    assert cooldown == []
    assert _ally_petitions(world) == []


def test_petition_request_reward_or_restoration_absent_until_slice_h_lands():
    assert "request_reward_or_restoration" not in _player_facing_source_text()


def test_petition_demand_bargain_honor_absent_until_slice_h_lands():
    assert "demand_bargain_honor" not in _player_facing_source_text()

"""Regression coverage for PL-29 restart flow."""

import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.models.world_state import WorldState
from backend.save_manager import AUTOSAVE_FILENAME, autosave, save_game


@pytest.fixture
def restart_client():
    """Provide a TestClient with an isolated save directory and fresh world."""
    save_dir = Path("saves") / "__restart_flow_tmp__"
    if save_dir.exists():
        shutil.rmtree(save_dir)
    save_dir.mkdir(parents=True)
    with patch("backend.save_manager.SAVE_DIR", save_dir):
        import backend.main as main_module

        main_module._reset_world_state()
        with TestClient(main_module.app) as client:
            yield client, main_module, save_dir
        main_module._reset_world_state()
    if save_dir.exists():
        shutil.rmtree(save_dir)


def test_new_game_resets_active_world_and_returns_fresh_state(restart_client):
    client, main_module, _save_dir = restart_client
    baseline = WorldState(player_nation="France")

    main_module.world.current_turn = 9
    main_module.world.actions_remaining = 0
    main_module.world.nation_gold["France"] = 321
    main_module.world.get_marshal("Ney").strength = 1234
    main_module.world.eliminated_nations_notified.add("Prussia")
    main_module.world.dialogue_manager.push({
        "type": "incoming_proposal",
        "turn_created": 9,
    })

    response = client.post("/new_game")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["new_game"] is True
    assert data["autosave_success"] is True
    assert data["game_state"]["turn"] == 1

    assert main_module.game_state["world"] is main_module.world
    assert main_module.world.current_turn == 1
    assert main_module.world.actions_remaining == baseline.actions_remaining
    assert main_module.world.nation_gold["France"] == baseline.nation_gold["France"]
    assert main_module.world.get_marshal("Ney").strength == baseline.get_marshal("Ney").strength
    assert main_module.world.dialogue_manager.get_mailbox_count() == 0
    assert main_module.world.pending_diplomatic_dialogue is None
    assert main_module.world.eliminated_nations_notified == set()


def test_new_game_overwrites_autosave_but_preserves_manual_saves(restart_client):
    client, main_module, save_dir = restart_client

    main_module.world.current_turn = 7
    manual_path = save_dir / "manual_keep.json"
    save_game(main_module.world, save_name="Manual Keep", filepath=manual_path)
    autosave(main_module.world)

    with open(save_dir / AUTOSAVE_FILENAME, "r", encoding="utf-8") as handle:
        assert json.load(handle)["metadata"]["turn"] == 7

    response = client.post("/new_game")
    assert response.status_code == 200
    assert response.json()["autosave_success"] is True

    assert manual_path.exists()
    with open(manual_path, "r", encoding="utf-8") as handle:
        assert json.load(handle)["metadata"]["turn"] == 7

    with open(save_dir / AUTOSAVE_FILENAME, "r", encoding="utf-8") as handle:
        assert json.load(handle)["metadata"]["turn"] == 1


def test_load_autosave_after_new_game_uses_fresh_campaign_state(restart_client):
    client, main_module, save_dir = restart_client
    baseline = WorldState(player_nation="France")

    main_module.world.current_turn = 8
    main_module.world.nation_gold["France"] = 222
    autosave(main_module.world)

    with open(save_dir / AUTOSAVE_FILENAME, "r", encoding="utf-8") as handle:
        assert json.load(handle)["metadata"]["turn"] == 8

    new_game_response = client.post("/new_game")
    assert new_game_response.status_code == 200
    assert new_game_response.json()["autosave_success"] is True

    load_response = client.post("/load", json={"filename": AUTOSAVE_FILENAME})
    assert load_response.status_code == 200

    data = load_response.json()
    assert data["success"] is True
    assert data["game_state"]["turn"] == 1
    assert main_module.world.current_turn == 1
    assert main_module.world.nation_gold["France"] == baseline.nation_gold["France"]


def test_new_game_preserves_non_france_player_nation(restart_client):
    client, main_module, _save_dir = restart_client

    main_module._reset_world_state(player_nation="Prussia")
    assert main_module.world.player_nation == "Prussia"

    response = client.post("/new_game")
    assert response.status_code == 200
    assert response.json()["success"] is True

    assert main_module.world.player_nation == "Prussia"
    assert "France" in main_module.world.enemy_nations
    assert "Prussia" not in main_module.world.enemy_nations
    assert "France" in main_module.world.nation_actions
    assert "Prussia" not in main_module.world.nation_actions

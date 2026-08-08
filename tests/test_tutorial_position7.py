"""POSITION 7 — the /new_game scenario handshake + WorldState.scenario_name
+ the School of War client structural pins.

Backend half (T-A*): the allowlisted scenario request, the display-only
scenario identity field, and their serialization.
Structural half (T-G*, T-B1): added in slice S2 alongside the overlay.
"""

import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def handshake_client(monkeypatch):
    """TestClient with an isolated save dir and a fresh default world.

    Modeled on tests/test_restart_flow.py (the TestClient world-swap trap:
    /new_game rebinds BOTH module globals; assert against main_module.world).
    Runs on the conftest default (SOVEREIGN_SCENARIO=none → bare Europe flag
    world) so the DEFAULT arm is the suite's own baseline boot.
    """
    save_dir = Path("saves") / "__tutorial_handshake_tmp__"
    if save_dir.exists():
        shutil.rmtree(save_dir)
    save_dir.mkdir(parents=True)
    with patch("backend.save_manager.SAVE_DIR", save_dir):
        import backend.main as main_module

        main_module._reset_world_state()
        with TestClient(main_module.app) as client:
            yield client, main_module
        main_module._reset_world_state()
    if save_dir.exists():
        shutil.rmtree(save_dir)


class TestNewGameScenarioParam:
    def test_default_new_game_unchanged(self, handshake_client):
        """T-A1: {} body and NO body both take today's path — a bare/default
        world with scenario_name ''."""
        client, main_module = handshake_client
        for body in ({}, None):
            response = client.post("/new_game", json=body) if body is not None \
                else client.post("/new_game")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["new_game"] is True
            assert data["game_state"]["scenario_name"] == ""
            assert main_module.world.scenario_name == ""

    def test_tutorial_boot_and_revert(self, handshake_client):
        """T-A2: the named scenario boots The Danube Lesson; a following
        default new_game reverts — no latch leak."""
        client, main_module = handshake_client
        response = client.post("/new_game", json={"scenario": "tutorial"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["game_state"]["scenario_name"] == "tutorial"
        assert main_module.world.scenario_name == "tutorial"
        assert main_module.world.get_marshal("Senarmont") is not None
        assert main_module.world.is_at_war("France", "Austria")
        assert main_module.game_state["world"] is main_module.world

        response = client.post("/new_game", json={})
        assert response.json()["game_state"]["scenario_name"] == ""
        assert main_module.world.get_marshal("Senarmont") is None

    def test_unknown_and_hostile_names_refused_world_not_swapped(self, handshake_client):
        """T-A3: unknown names fail loudly naming the allowlist; a raw path
        is never resolved; the running world is untouched."""
        client, main_module = handshake_client
        main_module.world.current_turn = 7
        world_before = main_module.world
        for name in ("europe_1805", "../../saves/x.json", "none",
                     "TUTORIAL", "tutorial "):
            response = client.post("/new_game", json={"scenario": name})
            assert response.status_code == 200
            data = response.json()
            if name.strip() == "tutorial":
                continue  # "tutorial " strips to a valid name — not this arm
            assert data["success"] is False, name
            assert "tutorial" in data["message"], name
            assert main_module.world is world_before, name
            assert main_module.world.current_turn == 7, name

    def test_trailing_space_strips_to_valid(self, handshake_client):
        """The one whitespace nicety: 'tutorial ' strips to the allowlist
        name rather than failing."""
        client, main_module = handshake_client
        response = client.post("/new_game", json={"scenario": "tutorial "})
        assert response.json()["success"] is True
        assert main_module.world.scenario_name == "tutorial"

    def test_allowlist_file_contract(self):
        """T-A4: the allowlist path exists on disk and carries the client
        contract id."""
        import backend.main as main_module
        path = main_module.SCENARIO_ALLOWLIST["tutorial"]
        assert Path(path).exists()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert data["scenario_name"] == "tutorial"

    def test_never_combine_with_smoke_preset(self, handshake_client, monkeypatch):
        """T-A5: an explicit scenario + a smoke preset stays the documented
        never-combine pair — loud failure, world preserved."""
        client, main_module = handshake_client
        monkeypatch.setenv("SOVEREIGN_SMOKE_START", "settlement_losing")
        world_before = main_module.world
        response = client.post("/new_game", json={"scenario": "tutorial"})
        data = response.json()
        assert data["success"] is False
        assert "never combine" in data["message"]
        assert main_module.world is world_before


class TestScenarioNameSerialization:
    def test_default_and_roundtrip(self):
        """T-A6: '' by default; survives to_dict/from_dict; a pre-field save
        (popped key) reads ''."""
        w = WorldState(player_nation="France")
        assert w.scenario_name == ""
        w.scenario_name = "tutorial"
        data = w.to_dict()
        assert data["scenario_name"] == "tutorial"
        restored = WorldState.from_dict(data)
        assert restored.scenario_name == "tutorial"
        data.pop("scenario_name")
        assert WorldState.from_dict(data).scenario_name == ""

    def test_none_value_reads_empty(self):
        w = WorldState(player_nation="France")
        data = w.to_dict()
        data["scenario_name"] = None
        assert WorldState.from_dict(data).scenario_name == ""

    def test_game_state_summaries_carry_it(self):
        """T-A7: both summary variants surface the field — it rides every
        response via build_base_response and the /test payload."""
        w = WorldState(player_nation="France")
        w.scenario_name = "tutorial"
        assert w.get_game_state_summary()["scenario_name"] == "tutorial"
        assert w.get_filtered_game_state_summary()["scenario_name"] == "tutorial"

    def test_test_endpoint_carries_it(self, handshake_client):
        client, main_module = handshake_client
        client.post("/new_game", json={"scenario": "tutorial"})
        response = client.get("/test")
        assert response.json()["game_state"]["scenario_name"] == "tutorial"

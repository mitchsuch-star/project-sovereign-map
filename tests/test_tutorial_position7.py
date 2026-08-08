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


# ═══════════════════════════════════════════════════════════════════════════
# The School of War — client structural pins (T-G*) + the suggest-command
# guarantee (T-B1). The .gd files are asserted as text, mirroring
# tests/test_main_menu_and_ux_pass.py.
# ═══════════════════════════════════════════════════════════════════════════

GODOT = REPO / "godot-client" / "project-sovereign"


def _read(rel: str) -> str:
    return (GODOT / rel).read_text(encoding="utf-8")


def _func_body(source: str, func_name: str) -> str:
    """Slice one function's body out of a .gd file (to the next top-level
    func) — the _on_continue_saves_listed slicing idiom."""
    start = source.index(f"func {func_name}")
    end = source.find("\nfunc ", start + 1)
    return source[start:end] if end != -1 else source[start:]


class TestClientStructuralPins:
    def test_g1_consume_arms_old_and_new(self):
        """T-G1: the NEW tutorial arm exists AND the position-6 pinned
        new_game literal survives byte-for-byte."""
        gd = _read("scripts/main.gd")
        assert '"new_game":\n\t\t\t_on_pause_new_game_requested()' in gd
        assert '"tutorial":\n\t\t\t_on_tutorial_boot_requested()' in gd

    def test_g2_nonmodal_registration_and_observe_only(self):
        """T-G2: registered NON-modal (load-bearing — modal would block
        ESC/hotkeys/war HUD); observed on BOTH response paths; NEVER a
        response-routes entry (the documented end-turn-tail soft-lock)."""
        gd = _read("scripts/main.gd")
        assert 'tutorial_overlay = dialog_manager.register("tutorial_overlay", ' \
               '"res://scenes/tutorial_overlay.tscn", false)' in gd
        assert gd.count("tutorial_overlay.observe(") >= 2
        routes = _func_body(gd, "_configure_response_routes")
        assert "tutorial" not in routes

    def test_g3_observe_before_routing(self):
        """T-G3: inside _on_command_result the observe sits AHEAD of
        _route_response_ui so early-returning routes still reach the tutor."""
        body = _func_body(_read("scripts/main.gd"), "_on_command_result")
        assert body.index("tutorial_overlay.observe(") \
            < body.index("_route_response_ui(")

    def test_g4_menu_pins(self):
        menu = _read("scripts/main_menu.gd")
        assert '_add_menu_button("tutorial"' in menu
        assert '_launch("tutorial")' in menu
        assert '"begin", "return", "tutorial":' in menu
        assert '"tutorial"' in _read("scripts/menu_boot.gd")

    def test_g5_api_client_signature(self):
        api = _read("scripts/api_client.gd")
        assert 'func new_game(callback: Callable, scenario: String = "")' in api
        assert '"scenario"' in api

    def test_g6_overlay_hygiene(self):
        """T-G6: no timers of any kind; the overlay can never SEND a command
        (fills only, via the suggest signal); layer 90 under the modal band;
        hidden until armed; the layer index + the UiSettings latch exist."""
        overlay = _read("scripts/tutorial_overlay.gd")
        assert "get_tree().create_timer" not in overlay
        assert "send_command" not in overlay
        assert "suggest:" in overlay
        assert "signal suggest_command" in overlay
        scene = _read("scenes/tutorial_overlay.tscn")
        assert "layer = 90" in scene
        assert "visible = false" in scene
        assert "90: tutorial_overlay" in _read("scripts/dialog_manager.gd")
        settings = _read("scripts/ui_settings.gd")
        assert "static func get_tutorial_done" in settings
        assert "static func set_tutorial_done" in settings

    def test_g8_parse_harness_covers_the_new_files(self):
        harness = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert "res://scripts/tutorial_overlay.gd" in harness
        assert "res://scenes/tutorial_overlay.tscn" in harness


class TestSuggestCommandsParse:
    def test_b1_every_suggest_mock_parses_to_its_action(self):
        """T-B1: every chip the tutor offers is guaranteed to parse — each
        (suggest, suggest_action) pair from the step table is mock-parsed
        against the tutorial world's own roster. Edit the two fields
        together; an unparseable chip is a dead button."""
        import re

        from backend.commands.parser import CommandParser

        overlay = _read("scripts/tutorial_overlay.gd")
        suggests = re.findall(r'"suggest":\s*"([^"]*)"', overlay)
        actions = re.findall(r'"suggest_action":\s*"([^"]*)"', overlay)
        assert len(suggests) == len(actions)
        assert len(suggests) >= 10, "the step table lost its suggests"
        pairs = [(s, a) for s, a in zip(suggests, actions) if s != ""]
        assert pairs, "no non-empty suggests found"

        world = WorldState.from_scenario(
            str((REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "tutorial_1805.json")))
        parser = CommandParser(use_real_llm=False)
        for suggest, expected_action in pairs:
            assert expected_action != "", suggest
            result = parser.parse(suggest, world=world)
            assert result.get("success"), (suggest, result.get("error"))
            got = result["command"]["action"]
            assert got == expected_action, (suggest, got, expected_action)

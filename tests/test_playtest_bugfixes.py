"""
Playtest bugfix tests — 4 fixes from creative playtesting.

Fix 1: Game-over enforcement + capital-loss defeat removed
Fix 2: Empty command rejection
Fix 3: ParseResult includes requested_type/diplomatic_data/cheat_type/cheat_args from LLM
Fix 4: War declaration on treaty ally shows warning
"""
import pytest
from fastapi.testclient import TestClient
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def client():
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def fresh_world():
    import backend.main as main_module
    main_module.world = WorldState()
    main_module.game_state = {"world": main_module.world}
    return main_module.world


def _make_world():
    world = WorldState()
    world.current_turn = 5
    return world


def _make_game_state(world=None):
    if world is None:
        world = _make_world()
    return {"world": world}


# ═══════════════════════════════════════════════════════════════════════════
# FIX 1: GAME-OVER ENFORCEMENT + CAPITAL-LOSS DEFEAT REMOVED
# ═══════════════════════════════════════════════════════════════════════════

class TestCapitalLossNotDefeat:
    """Capital loss no longer ends the game (land can be ceded via treaties)."""

    def test_capital_loss_does_not_end_game(self):
        """Losing your capital should NOT trigger defeat."""
        from backend.game_logic.turn_manager import TurnManager
        world = _make_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        # Give player at least one marshal with strength
        ney = world.marshals.get("Ney")
        assert ney is not None
        ney.strength = 15000

        # Ensure Paris is NOT controlled by the player (enemy took it)
        paris_region = world.regions.get("Ile-de-France")
        if paris_region:
            paris_region.controller = "Prussia"

        tm = TurnManager(world, executor)
        result = tm._check_victory_conditions()

        # Should NOT be game over (capital loss removed as defeat condition)
        if result:
            assert result.get("result") != "defeat" or "Capital" not in result.get("reason", "")

    def test_all_marshals_destroyed_still_defeats(self):
        """All marshals destroyed should still end the game."""
        from backend.game_logic.turn_manager import TurnManager
        world = _make_world()
        executor = CommandExecutor()

        # Set all player marshals to 0 strength
        for m in world.get_player_marshals():
            m.strength = 0

        tm = TurnManager(world, executor)
        result = tm._check_victory_conditions()
        assert result is not None
        assert result["game_over"] is True
        assert result["result"] == "defeat"
        assert "destroyed" in result["reason"].lower()


class TestGameOverBlocksCommands:
    """After game over, action endpoints should be blocked."""

    def test_game_over_blocks_commands(self, client, fresh_world):
        """POST /command should be rejected when game_over=True."""
        fresh_world.game_over = True
        fresh_world.victory = "defeat"

        response = client.post("/command", json={"command": "Ney, attack Wellington"})
        data = response.json()
        assert data["success"] is False
        assert "war is over" in data["message"].lower()
        assert data["game_over"] is True

    def test_game_over_blocks_cancel_order(self, client, fresh_world):
        """POST /cancel_order should be rejected when game_over=True."""
        fresh_world.game_over = True
        fresh_world.victory = "victory"

        response = client.post("/cancel_order", json={"marshal": "Ney"})
        data = response.json()
        assert data["success"] is False
        assert data["game_over"] is True


class TestAIDiplomacySkippedAfterGameOver:
    """AI diplomatic phase should not run after game over."""

    def test_ai_diplomacy_skipped_after_game_over(self):
        from backend.game_logic.turn_manager import TurnManager
        world = _make_world()
        world.game_over = True
        executor = CommandExecutor()

        tm = TurnManager(world, executor)
        result = tm._process_ai_diplomatic_phase()
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════
# FIX 2: EMPTY COMMAND REJECTION
# ═══════════════════════════════════════════════════════════════════════════

class TestEmptyCommandRejected:
    """Empty or whitespace-only commands should be rejected cleanly."""

    def test_empty_command_rejected(self, client, fresh_world):
        response = client.post("/command", json={"command": ""})
        data = response.json()
        assert data["success"] is False
        assert "no command" in data["message"].lower()

    def test_whitespace_command_rejected(self, client, fresh_world):
        response = client.post("/command", json={"command": "   "})
        data = response.json()
        assert data["success"] is False
        assert "no command" in data["message"].lower()


# ═══════════════════════════════════════════════════════════════════════════
# FIX 3: PARSERESULT INCLUDES MISSING FIELDS FROM LLM
# ═══════════════════════════════════════════════════════════════════════════

class TestParseResultIncludesFields:
    """json_to_parse_result should map all ParseResult fields from LLM JSON."""

    def test_parse_result_includes_requested_type(self):
        from backend.ai.providers import json_to_parse_result
        json_data = {
            "matched": True,
            "action": "recruit",
            "requested_type": "cavalry",
            "diplomatic_data": {"target_nation": "Prussia", "action": "diplomatic_proposal"},
            "cheat_type": "add_troops",
            "cheat_args": ["Ney", "5000"],
        }
        result = json_to_parse_result(json_data, "anthropic", "recruit cavalry")
        assert result.requested_type == "cavalry"
        assert result.diplomatic_data["target_nation"] == "Prussia"
        assert result.cheat_type == "add_troops"
        assert result.cheat_args == ["Ney", "5000"]

    def test_parse_result_missing_fields_default(self):
        """Missing optional fields should default gracefully."""
        from backend.ai.providers import json_to_parse_result
        json_data = {"matched": True, "action": "attack"}
        result = json_to_parse_result(json_data, "anthropic", "attack")
        assert result.requested_type is None
        assert result.diplomatic_data is None
        assert result.cheat_type is None
        assert result.cheat_args == []


# ═══════════════════════════════════════════════════════════════════════════
# FIX 4: WAR DECLARATION ON TREATY ALLY SHOWS WARNING
# ═══════════════════════════════════════════════════════════════════════════

class TestWarOnTreatyAlly:
    """Declaring war on a nation with an active treaty should show a warning."""

    def test_war_on_treaty_ally_shows_warning(self):
        """If we have a treaty with a nation, war declaration should warn first."""
        world = _make_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        target = "Prussia"
        player = world.player_nation  # France

        # Set up a treaty
        diplo_key = world._make_diplo_key(player, target)
        world.active_treaties[diplo_key] = {
            "type": "non_aggression",
            "nations": [player, target],
            "turn_created": 1,
        }
        # Make sure we're not at war
        world.diplomatic_states[diplo_key] = "NON_AGGRESSION"
        # Give enough DP
        world.diplomatic_points = 5

        diplomatic_data = {"target_nation": target, "action": "diplomatic_declare_war"}
        result = executor._execute_diplomatic_declare_war(diplomatic_data, world)

        # Should show a warning dialogue, not immediately declare war
        assert result.get("success") is True
        assert result.get("diplomatic_dialogue") is not None
        assert result.get("awaiting_diplomatic_response") is True
        assert "treaty" in result["message"].lower() or "oath" in result["message"].lower()
        # War should NOT be declared yet
        assert world.diplomatic_states[diplo_key] != "WAR"

    def test_war_on_non_treaty_nation_no_warning(self):
        """No treaty = no special warning (existing threat objection may still fire)."""
        world = _make_world()
        executor = CommandExecutor()

        target = "Prussia"
        player = world.player_nation

        diplo_key = world._make_diplo_key(player, target)
        # Ensure no treaty exists
        world.active_treaties.pop(diplo_key, None)
        # Set neutral state, low threat
        world.diplomatic_states[diplo_key] = "PEACE"
        world.threat_level = 10
        world.diplomatic_points = 5

        diplomatic_data = {"target_nation": target, "action": "diplomatic_declare_war"}
        result = executor._execute_diplomatic_declare_war(diplomatic_data, world)

        # Should succeed directly (no treaty warning)
        assert result.get("success") is True
        # War should be declared
        assert world.diplomatic_states[diplo_key] == "WAR"

    def test_force_declare_war_completes(self):
        """After confirming treaty warning, war should be declared via force_declare_war."""
        world = _make_world()
        executor = CommandExecutor()

        target = "Austria"
        player = world.player_nation
        diplo_key = world._make_diplo_key(player, target)

        # Set up alliance treaty
        world.active_treaties[diplo_key] = {
            "type": "alliance",
            "nations": [player, target],
            "turn_created": 1,
        }
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.diplomatic_points = 5

        # Simulate the pending dialogue that the treaty warning creates
        world.dialogue_manager.replace({
            "type": "force_declare_war_confirmation",
            "target_nation": target,
            "message": "Treaty warning...",
            "options": [
                {"label": "Proceed", "action": "force_declare_war", "target_nation": target},
                {"label": "Reconsider", "action": "reconsider"},
            ],
            "turn_created": int(world.current_turn),
            "blocking": True,
        })

        # Player chooses "proceed" (force_declare_war)
        selected = {"action": "force_declare_war", "target_nation": target}
        dialogue = world.pending_diplomatic_dialogue
        result = executor._process_dialogue_choice("force_declare_war", selected, dialogue, world)

        assert result.get("success") is True
        # War should now be declared
        assert world.diplomatic_states[diplo_key] == "WAR"
        # DP should be deducted (1 for war declaration)
        assert world.diplomatic_points == 4
        # Dialogue should be cleared
        assert world.pending_diplomatic_dialogue is None

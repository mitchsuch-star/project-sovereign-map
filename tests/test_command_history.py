"""
Tests for Phase 5 Command History System.

Tests cover:
1. Adding commands to history
2. Sliding window limit (50 commands)
3. Getting recent commands
4. Getting command history for LLM prompt
"""

import pytest
from backend.models.world_state import WorldState


class TestCommandHistory:
    """Test CommandHistory on WorldState."""

    def setup_method(self):
        self.world = WorldState()

    def test_history_starts_empty(self):
        """Command history should be empty on initialization."""
        assert len(self.world.command_history) == 0
        print("Command history starts empty")

    def test_add_command(self):
        """Adding a command should increase history length."""
        self.world.add_to_command_history({
            "raw_input": "Ney attack",
            "marshal": "Ney",
            "action": "attack",
            "turn": 1
        })
        assert len(self.world.command_history) == 1
        assert self.world.command_history[0]["raw_input"] == "Ney attack"
        print("Command added successfully")

    def test_add_multiple_commands(self):
        """Adding multiple commands should preserve order."""
        for i in range(5):
            self.world.add_to_command_history({
                "raw_input": f"command {i}",
                "marshal": "Ney",
                "action": "attack",
                "turn": i
            })

        assert len(self.world.command_history) == 5
        assert self.world.command_history[0]["raw_input"] == "command 0"
        assert self.world.command_history[4]["raw_input"] == "command 4"
        print("Multiple commands preserved in order")

    def test_sliding_window_limit(self):
        """History should be limited to 50 commands (sliding window)."""
        for i in range(60):
            self.world.add_to_command_history({
                "raw_input": f"command {i}",
                "marshal": "Ney",
                "action": "attack",
                "turn": i
            })

        assert len(self.world.command_history) == 50
        # First 10 should be dropped, so first remaining is "command 10"
        assert self.world.command_history[0]["raw_input"] == "command 10"
        assert self.world.command_history[49]["raw_input"] == "command 59"
        print("Sliding window maintains 50 commands")

    def test_get_recent_commands_default(self):
        """get_recent_commands() should return last 5 by default."""
        for i in range(10):
            self.world.add_to_command_history({
                "raw_input": f"command {i}",
                "marshal": "Ney",
                "action": "attack",
                "turn": i
            })

        recent = self.world.get_recent_commands()
        assert len(recent) == 5
        assert recent[0]["raw_input"] == "command 5"
        assert recent[4]["raw_input"] == "command 9"
        print("get_recent_commands returns last 5 by default")

    def test_get_recent_commands_custom_count(self):
        """get_recent_commands(n) should return last n commands."""
        for i in range(10):
            self.world.add_to_command_history({
                "raw_input": f"command {i}",
                "marshal": "Ney",
                "action": "attack",
                "turn": i
            })

        recent = self.world.get_recent_commands(3)
        assert len(recent) == 3
        assert recent[0]["raw_input"] == "command 7"
        assert recent[2]["raw_input"] == "command 9"
        print("get_recent_commands(3) returns last 3")

    def test_get_recent_commands_fewer_than_requested(self):
        """get_recent_commands should handle fewer commands than requested."""
        for i in range(3):
            self.world.add_to_command_history({
                "raw_input": f"command {i}",
                "marshal": "Ney",
                "action": "attack",
                "turn": i
            })

        # Request 5 but only 3 exist
        recent = self.world.get_recent_commands(5)
        assert len(recent) == 3
        print("get_recent_commands handles fewer than requested")

    def test_get_command_history_for_prompt(self):
        """get_command_history_for_prompt() should return raw_input strings."""
        for i in range(3):
            self.world.add_to_command_history({
                "raw_input": f"Ney attack for glory {i}",
                "marshal": "Ney",
                "action": "attack",
                "turn": i
            })

        prompt_history = self.world.get_command_history_for_prompt()
        assert len(prompt_history) == 3
        assert all(isinstance(s, str) for s in prompt_history)
        assert prompt_history[0] == "Ney attack for glory 0"
        assert prompt_history[2] == "Ney attack for glory 2"
        print("get_command_history_for_prompt returns strings")

    def test_get_command_history_for_prompt_limits_to_5(self):
        """get_command_history_for_prompt() should only return last 5."""
        for i in range(10):
            self.world.add_to_command_history({
                "raw_input": f"command {i}",
                "marshal": "Ney",
                "action": "attack",
                "turn": i
            })

        prompt_history = self.world.get_command_history_for_prompt()
        assert len(prompt_history) == 5
        assert prompt_history[0] == "command 5"
        assert prompt_history[4] == "command 9"
        print("get_command_history_for_prompt limits to last 5")

    def test_get_command_history_for_prompt_empty(self):
        """get_command_history_for_prompt() should handle empty history."""
        prompt_history = self.world.get_command_history_for_prompt()
        assert len(prompt_history) == 0
        assert prompt_history == []
        print("get_command_history_for_prompt handles empty history")

    def test_command_structure_preserved(self):
        """Command structure should be fully preserved in history."""
        command = {
            "raw_input": "Ney, charge Wellington for glory!",
            "marshal": "Ney",
            "action": "attack",
            "turn": 5
        }
        self.world.add_to_command_history(command)

        stored = self.world.command_history[0]
        assert stored["raw_input"] == command["raw_input"]
        assert stored["marshal"] == command["marshal"]
        assert stored["action"] == command["action"]
        assert stored["turn"] == command["turn"]
        print("Command structure fully preserved")

    def test_none_marshal_handled(self):
        """Commands with None marshal should be stored correctly."""
        self.world.add_to_command_history({
            "raw_input": "attack the enemy",
            "marshal": None,
            "action": "attack",
            "turn": 1
        })

        assert len(self.world.command_history) == 1
        assert self.world.command_history[0]["marshal"] is None
        print("None marshal handled correctly")


class TestCommandHistoryIntegration:
    """Integration tests for command history with prompt builder."""

    def setup_method(self):
        self.world = WorldState()

    def test_history_isolated_between_worlds(self):
        """Each WorldState should have its own command history."""
        world1 = WorldState()
        world2 = WorldState()

        world1.add_to_command_history({
            "raw_input": "command for world 1",
            "marshal": "Ney",
            "action": "attack",
            "turn": 1
        })

        assert len(world1.command_history) == 1
        assert len(world2.command_history) == 0
        print("Command histories are isolated between worlds")

    def test_sliding_window_fifo(self):
        """Sliding window should use FIFO (first-in-first-out)."""
        # Fill to capacity
        for i in range(50):
            self.world.add_to_command_history({
                "raw_input": f"old command {i}",
                "marshal": "Ney",
                "action": "attack",
                "turn": i
            })

        # Add one more
        self.world.add_to_command_history({
            "raw_input": "new command",
            "marshal": "Davout",
            "action": "defend",
            "turn": 50
        })

        # Oldest (command 0) should be gone, newest should be present
        assert len(self.world.command_history) == 50
        assert self.world.command_history[0]["raw_input"] == "old command 1"
        assert self.world.command_history[49]["raw_input"] == "new command"
        print("FIFO behavior confirmed")

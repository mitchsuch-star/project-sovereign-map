"""
Test suite for bug fixes:
- BUG 1: Paris-Waterloo adjacency
- BUG 2: Failed commands consuming actions
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor


class TestParisWaterlooAdjacency:
    """Test that Paris and Waterloo are properly adjacent."""

    def test_paris_waterloo_bidirectional_adjacency(self):
        """Paris and Waterloo should be adjacent in both directions."""
        world = WorldState(player_nation="France")

        paris = world.get_region("Paris")
        waterloo = world.get_region("Waterloo")

        # Check bidirectional adjacency
        assert paris.is_adjacent_to("Waterloo"), "Paris should be adjacent to Waterloo"
        assert waterloo.is_adjacent_to("Paris"), "Waterloo should be adjacent to Paris"

    def test_paris_waterloo_distance(self):
        """Distance between Paris and Waterloo should be 1."""
        world = WorldState(player_nation="France")

        distance = world.get_distance("Paris", "Waterloo")
        assert distance == 1, f"Paris-Waterloo distance should be 1, got {distance}"

    def test_attack_paris_to_waterloo_in_range(self):
        """Attacking from Paris to Waterloo should be in range."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # Place Davout in Paris
        davout = world.get_marshal("Davout")
        davout.location = "Paris"

        # Wellington is at Waterloo
        wellington = world.get_enemy_by_name("Wellington")
        assert wellington.location == "Waterloo", "Wellington should be at Waterloo"

        # Attack should succeed (in range)
        game_state = {"world": world}
        command = {
            "marshal": "Davout",
            "action": "attack",
            "target": "Wellington",
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Should NOT get "not in range" error
        assert result.get("success", False) or "cannot reach" not in result.get("message", "").lower(), \
            f"Attack should not fail due to range. Message: {result.get('message')}"


class TestActionConsumption:
    """Test that failed commands don't consume actions."""

    def test_failed_attack_does_not_consume_action(self):
        """Failed attack (out of range) should NOT consume action."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # Place Davout in Paris
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        davout.movement_range = 1  # Infantry

        # Record initial actions
        initial_actions = world.actions_remaining

        # Try to attack Vienna (too far away)
        game_state = {"world": world}
        command = {
            "marshal": "Davout",
            "action": "attack",
            "target": "Vienna",
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Attack should fail
        assert result.get("success", False) == False, "Attack should fail (out of range)"

        # Actions should NOT be consumed
        assert world.actions_remaining == initial_actions, \
            f"Failed attack should not consume action. Before: {initial_actions}, After: {world.actions_remaining}"

    def test_successful_attack_does_consume_action(self):
        """Successful attack should consume action."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # Place Davout in Paris
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        davout.movement_range = 1  # Infantry

        # Place an enemy in adjacent region
        wellington = world.get_enemy_by_name("Wellington")
        wellington.location = "Belgium"  # Adjacent to Paris

        # Record initial actions
        initial_actions = world.actions_remaining

        # Attack Wellington directly (by name)
        game_state = {"world": world}
        command = {
            "command": {"marshal": "Davout", "action": "attack", "target": "Wellington"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Attack should execute (success depends on combat outcome)
        # If attack executed, action should be consumed regardless of victory
        if result.get("success", False):
            assert world.actions_remaining == initial_actions - 1, \
                f"Executed attack should consume action. Before: {initial_actions}, After: {world.actions_remaining}"
        else:
            # If attack failed validation, action should NOT be consumed
            assert world.actions_remaining == initial_actions, \
                f"Failed attack should not consume action. Message: {result.get('message')}"

    def test_failed_move_does_not_consume_action(self):
        """Failed move (invalid destination) should NOT consume action."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # Place Ney in Belgium
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"

        # Record initial actions
        initial_actions = world.actions_remaining

        # Try to move to invalid/non-adjacent region
        game_state = {"world": world}
        command = {
            "marshal": "Ney",
            "action": "move",
            "target": "Vienna",  # Not adjacent to Belgium
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Move should fail
        assert result.get("success", False) == False, "Move should fail (not adjacent)"

        # Actions should NOT be consumed
        assert world.actions_remaining == initial_actions, \
            f"Failed move should not consume action. Before: {initial_actions}, After: {world.actions_remaining}"

    def test_successful_move_does_consume_action(self):
        """Successful move should consume action."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # Place Ney in Belgium
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"

        # Move Blucher away from Netherlands so we can move there
        blucher = world.get_marshal("Blucher")
        blucher.location = "Rhineland"

        # Record initial actions
        initial_actions = world.actions_remaining

        # Move to adjacent region (now empty of enemies)
        game_state = {"world": world}
        command = {
            "command": {"marshal": "Ney", "action": "move", "target": "Netherlands"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Move should succeed
        assert result.get("success", False) == True, f"Move should succeed. Message: {result.get('message')}"

        # Actions should be consumed
        assert world.actions_remaining == initial_actions - 1, \
            f"Successful move should consume action. Before: {initial_actions}, After: {world.actions_remaining}"

    def test_invalid_target_does_not_consume_action(self):
        """Attack with invalid target should NOT consume action."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # Place Davout in Paris
        davout = world.get_marshal("Davout")
        davout.location = "Paris"

        # Record initial actions
        initial_actions = world.actions_remaining

        # Try to attack non-existent target
        game_state = {"world": world}
        command = {
            "marshal": "Davout",
            "action": "attack",
            "target": "InvalidTarget",
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Attack should fail
        assert result.get("success", False) == False, "Attack should fail (invalid target)"

        # Actions should NOT be consumed
        assert world.actions_remaining == initial_actions, \
            f"Failed attack should not consume action. Before: {initial_actions}, After: {world.actions_remaining}"


class TestActionConsumptionIntegration:
    """Integration tests for action consumption across multiple commands."""

    def test_multiple_failed_commands_preserve_actions(self):
        """Multiple failed commands should not drain action pool."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        davout.movement_range = 1

        initial_actions = world.actions_remaining
        game_state = {"world": world}

        # Try 3 invalid commands
        for target in ["Vienna", "Milan", "Bavaria"]:  # All too far
            command = {
                "marshal": "Davout",
                "action": "attack",
                "target": target,
                "type": "specific"
            }
            result = executor.execute(command, game_state)
            assert result.get("success", False) == False, f"Attack {target} should fail"

        # Actions should still be unchanged
        assert world.actions_remaining == initial_actions, \
            "Multiple failed commands should not consume actions"


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v"])

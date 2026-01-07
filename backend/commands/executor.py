"""
Command Executor for Project Sovereign
Executes parsed commands against game state
"""

from typing import Dict, List
from backend.models.world_state import WorldState


class CommandExecutor:
    """
    Executes validated commands and returns results.
    Handles smart command routing based on game state.
    """

    def __init__(self):
        print("Command Executor initialized")

    def execute(self, parsed_command: Dict, game_state: Dict) -> Dict:
        """
        Execute a command against the current game state.

        Args:
            parsed_command: Output from CommandParser
            game_state: Current world state

        Returns:
            Execution result:
            {
                "success": True/False,
                "events": [...],  # What happened
                "message": "...",  # Player feedback
                "new_state": {...}  # Updated game state
            }
        """
        command = parsed_command.get("command", {})
        command_type = command.get("type", "specific")
        action = command.get("action")
        if action == "reinforce":
            return self._execute_reinforce(command, game_state)
        elif action == "recruit":
            return self._execute_recruit(command, game_state)

        # Route to appropriate handler
        if command_type == "specific":
            return self._execute_specific(command, game_state)
        elif command_type == "general_attack":
            return self._execute_general_attack(command, game_state)
        elif command_type == "auto_assign_attack":
            return self._execute_auto_assign_attack(command, game_state)
        elif command_type == "general_retreat":
            return self._execute_general_retreat(command, game_state)
        elif command_type == "general_defensive":
            return self._execute_general_defensive(command, game_state)
        else:
            return {
                "success": False,
                "message": f"Unknown command type: {command_type}"
            }

    def _execute_specific(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute command directed at specific marshal.
        Example: "Ney, attack Wellington"
        """
        # TODO: Implement in Week 1, Day 4-5
        marshal = command["marshal"]
        action = command["action"]
        target = command.get("target")

        return {
            "success": True,
            "events": [{
                "type": "specific_order",
                "marshal": marshal,
                "action": action,
                "target": target
            }],
            "message": f"{marshal} will {action}" + (f" {target}" if target else ""),
            "new_state": game_state  # No changes yet (stub)
        }

    def _execute_general_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute "attack" with no target specified.
        Finds nearest enemy and attacks.
        """
        # TODO: Implement proximity checking
        # For now, return placeholder
        return {
            "success": False,
            "message": "Cannot execute general attack order yet - need to implement proximity system",
            "suggestion": "Try: 'Ney, attack Wellington' for now"
        }

    def _execute_auto_assign_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute "attack [target]" with no marshal.
        Finds closest marshal to target.
        """
        target = command.get("target")

        # TODO: Implement proximity checking
        # For now, return placeholder
        return {
            "success": False,
            "message": f"Cannot auto-assign marshal to attack {target} yet - need proximity system",
            "suggestion": f"Try: 'Ney, attack {target}' for now"
        }

    def _execute_general_retreat(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute "retreat" - all forces retreat.
        """
        # TODO: Get all marshals from game_state
        # For now, placeholder
        return {
            "success": True,
            "events": [{
                "type": "general_retreat",
                "all_marshals": True
            }],
            "message": "All forces ordered to retreat!",
            "new_state": game_state  # No changes yet (stub)
        }

    def _execute_general_defensive(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute "defend" - all forces go defensive.
        """
        return {
            "success": True,
            "events": [{
                "type": "general_defensive",
                "all_marshals": True
            }],
            "message": "All forces ordered to defensive positions!",
            "new_state": game_state  # No changes yet (stub)
        }
    def _execute_recruit(self, command: Dict, game_state: Dict) -> Dict:
        """
        Recruit new troops - assigns to marshal closest to recruitment location.
        Now uses REAL proximity calculation!

        Examples:
        - "Ney, recruit" → +10,000 to Ney at his current location
        - "Recruit in Belgium" → +10,000 to marshal closest to Belgium
        - "Recruit" → +10,000 to marshal closest to capital

        Cost: 200 gold per recruitment
        Effect: +10,000 strength to determined marshal
        """
        marshal_specified = command.get("marshal")
        location_specified = command.get("target")

        # Get world state
        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Check if player has enough gold
        if world.gold < 200:
            return {
                "success": False,
                "message": f"Insufficient gold! Need 200 gold, have {world.gold} gold",
                "suggestion": "Wait for more income or conquer more regions"
            }

        # Determine which marshal gets the troops
        if marshal_specified:
            # Marshal named directly
            marshal = world.get_marshal(marshal_specified)
            if not marshal:
                return {
                    "success": False,
                    "message": f"Marshal {marshal_specified} not found"
                }

            recipient = marshal.name
            recruitment_location = marshal.location
            message = f"{marshal.name} recruits 10,000 troops at {marshal.location}"

        elif location_specified:
            # Location specified - find nearest marshal
            result = world.find_nearest_marshal_to_region(location_specified)

            if not result:
                return {
                    "success": False,
                    "message": f"No marshals available to recruit in {location_specified}"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = location_specified
            message = f"{marshal.name} recruits 10,000 troops for {location_specified} ({distance} regions away)"

        else:
            # Neither specified - find marshal nearest to capital
            result = world.find_nearest_marshal_to_region("Paris")

            if not result:
                return {
                    "success": False,
                    "message": "No marshals available for recruitment"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = "Paris"
            message = f"{marshal.name} recruits 10,000 troops (nearest to capital)"

        # Execute recruitment
        marshal = world.get_marshal(recipient)
        marshal.add_troops(10000)
        world.gold -= 200

        return {
            "success": True,
            "message": f"{message} - Cost: 200 gold",
            "events": [{
                "type": "recruit",
                "marshal": recipient,
                "location": recruitment_location,
                "troops_added": 10000,
                "gold_cost": 200,
                "new_strength": marshal.strength,
                "description": f"+10,000 troops for {recipient}"
            }],
            "new_state": game_state
        }


    def _execute_reinforce(self, command: Dict, game_state: Dict) -> Dict:
        """
        Reinforce another marshal - move to support them.
        Now uses REAL world state for validation!

        Example: "Davout, reinforce Ney"
        """
        marshal_name = command.get("marshal")
        target_name = command.get("target")

        # Get world state
        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Get marshals
        marshal = world.get_marshal(marshal_name)
        target_marshal = world.get_marshal(target_name)

        if not marshal:
            return {
                "success": False,
                "message": f"Marshal {marshal_name} not found"
            }

        if not target_marshal:
            return {
                "success": False,
                "message": f"Target marshal {target_name} not found"
            }

        # Calculate distance
        distance = world.get_distance(marshal.location, target_marshal.location)

        if distance == 0:
            return {
                "success": True,
                "message": f"{marshal.name} is already with {target_marshal.name} at {marshal.location}",
                "events": [{
                    "type": "reinforce",
                    "marshal": marshal.name,
                    "target": target_marshal.name,
                    "already_together": True
                }],
                "new_state": game_state
            }

        # Move marshal to target's location
        marshal.move_to(target_marshal.location)

        return {
            "success": True,
            "message": f"{marshal.name} moves to reinforce {target_marshal.name} at {target_marshal.location} ({distance} regions)",
            "events": [{
                "type": "reinforce",
                "marshal": marshal.name,
                "target": target_marshal.name,
                "from_location": marshal.location,
                "to_location": target_marshal.location,
                "distance": distance
            }],
            "new_state": game_state
        }
    def calculate_turn_income(self, game_state: Dict) -> Dict:
        """
        Calculate income for the current turn.
        Now uses REAL world state!

        Args:
            game_state: Dictionary containing "world" key with WorldState instance

        Returns:
            Income breakdown dictionary
        """
        # Get world state instance
        world: WorldState = game_state.get("world")

        if not world:
            # Fallback if no world state provided (shouldn't happen)
            return {
                "income": 0,
                "breakdown": {"error": "No world state provided"},
                "message": "Error: No world state"
            }

        # Use real calculation from world state
        return world.calculate_turn_income()


# Test code
if __name__ == "__main__":
    """
    Test the executor with mock game state.
    """
    print("=" * 60)
    print("COMMAND EXECUTOR TEST")
    print("=" * 60)

    executor = CommandExecutor()

    # Mock game state (simplified)
    mock_state = {
        "marshals": {
            "Ney": {"location": "Belgium", "strength": 72000},
            "Davout": {"location": "Paris", "strength": 48000},
            "Grouchy": {"location": "Wavre", "strength": 33000}
        },
        "enemies": {
            "Wellington": {"location": "Waterloo", "strength": 68000},
            "Blucher": {"location": "Wavre", "strength": 50000}
        }
    }



    # Test commands
    test_commands = [
        {
            "success": True,
            "command": {
                "marshal": "Ney",
                "action": "attack",
                "target": "Wellington",
                "type": "specific"
            }
        },
        {
            "success": True,
            "command": {
                "marshal": "Ney",
                "action": "retreat",
                "target": None,
                "type": "general_retreat"
            }
        }
    ]

    print("\nExecuting test commands:\n")
    for parsed_cmd in test_commands:
        print(f"Command: {parsed_cmd['command']}")
        result = executor.execute(parsed_cmd, mock_state)
        print(f"Result: {result['message']}")
        print()

    print("=" * 60)
    print("EXECUTOR STUB READY")
    print("Will implement full logic in Week 1, Day 4-5")
    print("=" * 60)

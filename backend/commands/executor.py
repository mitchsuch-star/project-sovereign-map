from typing import Dict, List


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


def calculate_turn_income(self, game_state: Dict) -> Dict:
    """
    Calculate automatic income for this turn.
    Called at start of each turn (not a player command).

    Formula: (regions_controlled × 100) + capital_bonus

    TODO (Week 1 Day 2 - when building world_state.py):
    - Get list of regions player controls
    - Count them
    - Check if Paris is controlled (capital bonus +200)
    - Return income amount

    Example:
    - Control 3 regions: 300 gold/turn
    - Control 3 regions + Paris: 500 gold/turn
    - Control 8 regions + Paris: 1,000 gold/turn
    """
    # Placeholder - real implementation in world_state.py
    regions_controlled = game_state.get("regions_controlled", 3)  # Default: 3
    controlled_region_list = game_state.get("controlled_regions", ["Paris", "Belgium", "Rhine"])
    has_capital = "Paris" in controlled_region_list

    base_income = regions_controlled * 100
    capital_bonus = 200 if has_capital else 0
    total_income = base_income + capital_bonus

    return {
        "income": total_income,
        "breakdown": {
            "regions": regions_controlled,
            "base_income": base_income,
            "capital_bonus": capital_bonus,
            "total": total_income
        },
        "message": f"Turn income: {total_income} gold ({regions_controlled} regions)"
    }
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


    def _execute_recruit(self, command: Dict, game_state: Dict) -> Dict:
        """
        Recruit new troops - assigns to marshal closest to recruitment location.

        Examples:
        - "Ney, recruit" → +10,000 to Ney at his current location
        - "Recruit in Belgium" → +10,000 to marshal closest to Belgium
        - "Recruit" → +10,000 to marshal closest to capital

        Cost: 200 gold per recruitment
        Effect: +10,000 strength to determined marshal

        Design: NO garrison system for MVP.
        Troops always assigned to nearest marshal to recruitment location.
        This maintains high-level abstraction (no free-floating troops).

        TODO (Week 1 Day 4-5):
        - Check player has enough gold (need gold >= 200)
        - Deduct 200 gold from treasury
        - Find marshal closest to recruitment location
        - Add 10,000 to that marshal's strength
        """
        marshal_specified = command.get("marshal")
        location_specified = command.get("target")

        # Determine which marshal gets the troops
        if marshal_specified:
            # Clear case: marshal named directly
            recipient = marshal_specified
            recruitment_location = "current position"
            message = f"{marshal_specified} recruits 10,000 troops at their position"
            assignment_method = "specified"

        elif location_specified:
            # Location specified - find marshal closest to that location
            # TODO (Week 1 Day 4): Implement proximity system
            # For now, stub response
            recipient = "nearest_marshal"  # Placeholder
            recruitment_location = location_specified
            message = f"Recruiting 10,000 troops in {location_specified} - assigning to nearest marshal"
            assignment_method = "proximity_to_location"

        else:
            # Neither specified - default to capital region
            # Find marshal closest to capital
            # TODO (Week 1 Day 4): Find marshal nearest to Paris
            recipient = "nearest_to_capital"  # Placeholder
            recruitment_location = "Paris"
            message = f"Recruiting 10,000 troops - assigning to marshal nearest capital"
            assignment_method = "default_capital"

        return {
            "success": True,
            "message": f"{message} - Cost: 200 gold",
            "events": [{
                "type": "recruit",
                "marshal": recipient,
                "location": recruitment_location,
                "troops_added": 10000,
                "gold_cost": 200,
                "assignment_method": assignment_method,
                "description": f"+10,000 troops for {recipient} (closest to {recruitment_location})"
            }],
            "new_state": game_state  # TODO: Deduct gold, add troops to marshal
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

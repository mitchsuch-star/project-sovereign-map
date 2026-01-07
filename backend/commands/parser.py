"""
Command Parser for Project Sovereign
Converts natural language commands into validated, executable orders
"""

from typing import Dict, List, Optional
from backend.ai.llm_client import LLMClient


class CommandParser:
    """
    Parses player commands and validates them against game state.
    Uses LLM client to interpret natural language.
    """

    def __init__(self, use_real_llm: bool = False):
        """
        Initialize the parser with an LLM client.

        Args:
            use_real_llm: If True, use real Claude API. If False, use mock.
        """
        self.llm = LLMClient(use_real_api=use_real_llm)

        # Valid marshals (will expand this later)
        self.valid_marshals = ["Ney", "Davout", "Grouchy", "Murat"]

        # Valid actions
        self.valid_actions = [
            "attack", "defend", "retreat", "move", "scout",
            "reinforce", "recruit"
        ]

        print(f"Command Parser initialized with {'REAL' if use_real_llm else 'MOCK'} LLM")

    def parse(self, command_text: str, game_state: Optional[Dict] = None) -> Dict:
        """
        Parse a command from the player.

        Args:
            command_text: Natural language command
            game_state: Current game state (for validation)

        Returns:
            Parsed and validated command - ALWAYS returns a Dict
        """
        try:
            # Step 1: Use LLM to parse natural language
            llm_result = self.llm.parse_command(command_text, game_state)

            # Step 2: Validate the parsed command
            validation_result = self._validate_command(llm_result, game_state)

            # Step 3: Return complete result
            if validation_result.get("valid"):
                # Classify command type
                command_type = self._classify_command(llm_result, command_text)

                result = {
                    "success": True,
                    "command": {
                        "marshal": llm_result.get("marshal"),  # Can be None for general orders
                        "action": llm_result["action"],
                        "target": llm_result.get("target"),
                        "confidence": llm_result.get("confidence", 0.9),
                        "type": command_type
                    },
                    "raw_input": command_text
                }

                # Add warning if present
                if validation_result.get("warning"):
                    result["warning"] = validation_result["warning"]
                return result
            else:
                return {
                    "success": False,
                    "error": validation_result.get("error", "Unknown validation error"),
                    "suggestion": validation_result.get("suggestion"),
                    "raw_input": command_text
                }
        except Exception as e:
            # Safety net - should never happen but prevents crashes
            return {
                "success": False,
                "error": f"Parser error: {str(e)}",
                "raw_input": command_text
            }

    def _validate_command(self, parsed_command: Dict, game_state: Optional[Dict]) -> Dict:
        """
        Validate that the parsed command makes sense.
        Now handles None marshal (for general orders).
        """
        marshal = parsed_command.get("marshal")
        action = parsed_command.get("action")

        # Validation 1: Check action is valid
        if action not in self.valid_actions:
            return {
                "valid": False,
                "error": f"Unknown action: {action}",
                "suggestion": f"Valid actions: {', '.join(self.valid_actions)}"
            }

        # Validation 2: Marshal can be None for general orders - that's OK!
        # Only validate if a marshal was specified
        warning = None
        if marshal is not None and marshal not in self.valid_marshals:
            warning = f"Note: '{marshal}' is not a standard marshal. Standard marshals: {', '.join(self.valid_marshals)}"

        # Validation 3: Attack with no marshal and no target is ambiguous
        # (Let this through - executor will handle "find nearest enemy")
        # if action == "attack" and not parsed_command.get("target") and marshal is None:
        #     return {
        #         "valid": False,
        #         "error": "Attack command needs either a target or a marshal",
        #         "suggestion": "Try: 'attack Wellington' or 'Ney, attack'"
        #     }

        # All validations passed
        return {
            "valid": True,
            "warning": warning
        }

    def _classify_command(self, parsed_command: Dict, raw_input: str) -> str:
        """
        Classify the type of command.

        Args:
            parsed_command: The parsed command dict from LLM
            raw_input: The original command text

        Returns:
            Command type string
        """
        action = parsed_command.get("action", "")
        target = parsed_command.get("target")

        # Check if marshal name was actually mentioned in the command
        raw_lower = raw_input.lower()
        marshal_mentioned = any(name in raw_lower for name in ["ney", "davout", "grouchy", "marshal"])

        # If no specific marshal mentioned, it's a general order
        if not marshal_mentioned:
            if action == "attack":
                if not target:
                    return "general_attack"  # "attack" alone
                else:
                    return "auto_assign_attack"  # "attack Wellington" - find closest marshal
            elif action == "retreat":
                return "general_retreat"  # All forces retreat
            elif action == "defend":
                return "general_defensive"  # All forces defend

        # Default: directed at specific marshal
        return "specific"
    def parse_multiple(self, command_text: str, game_state: Optional[Dict] = None) -> List[Dict]:
        """
        Parse commands that mention multiple marshals.

        Example: "Ney and Davout, attack Wellington"

        Returns list of individual commands.
        """
        # Simple implementation: check if "and" is in command
        if " and " in command_text.lower():
            # Split into individual commands
            # This is simplified - real version would be smarter
            parts = command_text.lower().split(" and ")

            results = []
            for part in parts:
                # Parse each part
                result = self.parse(part.strip(), game_state)
                results.append(result)

            return results
        else:
            # Single command
            return [self.parse(command_text, game_state)]

    def get_help(self) -> str:
        """
        Return help text for players.
        """
        return f"""
COMMAND HELP:

Valid Marshals:
{chr(10).join(f'  • {m}' for m in self.valid_marshals)}

Valid Actions:
{chr(10).join(f'  • {a}' for a in self.valid_actions)}

Example Commands:
  • "Ney, attack Wellington"
  • "Marshal Davout, defend the ridge"
  • "Grouchy, scout the area"
  • "Retreat to Paris"
  • "Ney and Davout, attack"

Tips:
  • You can be casual: "attack!" works
  • Commands are case-insensitive
  • Multiple marshals: Use "and" between names
"""


# Test code
if __name__ == "__main__":
    """
    Test the command parser with various inputs.
    """
    print("=" * 60)
    print("COMMAND PARSER TEST")
    print("=" * 60)

    # Create parser in mock mode
    parser = CommandParser(use_real_llm=False)

    print("\n" + "=" * 60)
    print("TEST 1: Valid Commands")
    print("=" * 60)

    valid_commands = [
        "Ney, attack Wellington",
        "Marshal Davout, defend",
        "Grouchy, scout the area",
        "Retreat!",
    ]

    for cmd in valid_commands:
        print(f"\nCommand: '{cmd}'")
        result = parser.parse(cmd)
        if result["success"]:
            print(f"✓ SUCCESS: {result['command']}")
        else:
            print(f"✗ FAILED: {result['error']}")

    print("\n" + "=" * 60)
    print("TEST 2: Invalid Commands (Should Fail)")
    print("=" * 60)

    invalid_commands = [
        "Murat, attack Wellington",  # Invalid marshal
        "Ney, dance",  # Invalid action
        "attack",  # Attack without target
    ]

    for cmd in invalid_commands:
        print(f"\nCommand: '{cmd}'")
        result = parser.parse(cmd)
        if result["success"]:
            print(f"✓ SUCCESS: {result['command']}")
        else:
            print(f"✗ FAILED (expected): {result['error']}")
            if result.get("suggestion"):
                print(f"  Suggestion: {result['suggestion']}")

    print("\n" + "=" * 60)
    print("TEST 3: Multiple Marshals")
    print("=" * 60)

    multi_command = "Ney and Davout, attack Wellington"
    print(f"\nCommand: '{multi_command}'")
    results = parser.parse_multiple(multi_command)

    for i, result in enumerate(results, 1):
        print(f"\n  Command {i}:")
        if result["success"]:
            print(f"  ✓ {result['command']}")
        else:
            print(f"  ✗ {result['error']}")
    print("\n" + "=" * 60)
    print("TEST 5: General Orders (No Marshal Specified)")
    print("=" * 60)

    general_commands = [
        ("attack", "Should find nearest enemy"),
        ("attack Wellington", "Should assign closest marshal to Wellington"),
        ("retreat", "Should retreat all forces"),
        ("defend", "Should put all forces on defensive"),
    ]

    for cmd, description in general_commands:
        print(f"\nCommand: '{cmd}'")
        print(f"Expected: {description}")
        result = parser.parse(cmd)
        if result["success"]:
            cmd_type = result["command"].get("type", "unknown")
            print(f"✓ Type: {cmd_type}")
            print(f"  Command: {result['command']}")
        else:
            print(f"✗ FAILED: {result['error']}")
    print("\n" + "=" * 60)
    print("TEST 4: Help Text")
    print("=" * 60)
    print(parser.get_help())

    print("=" * 60)
    print("ALL TESTS COMPLETE!")
    print("=" * 60)


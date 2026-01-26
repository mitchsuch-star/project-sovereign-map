"""
Command Parser for Project Sovereign
Converts natural language commands into validated, executable orders
"""

from typing import Dict, List, Optional
from backend.ai.llm_client import LLMClient
from backend.utils.fuzzy_matcher import FuzzyMatcher


class CommandParser:
    """
    Parses player commands and validates them against game state.
    Uses LLM client to interpret natural language.
    """

    def __init__(self, use_real_llm: bool = None):
        """
        Initialize the parser with an LLM client.

        Args:
            use_real_llm: If True, use real Claude API. If False, use mock.
                         If None (default), read from LLM_MODE environment variable.
        """
        # Pass None to let LLMClient read from environment
        self.llm = LLMClient(use_real_api=use_real_llm)
        self.fuzzy_matcher = FuzzyMatcher()

        # Valid marshals (will expand this later)
        self.valid_marshals = ["Ney", "Davout", "Grouchy", "Murat"]

        # Valid actions
        # NOTE: When adding new actions, update ALL of these locations:
        # 1. executor.py: Add _execute_* method
        # 2. executor.py: Update help_text in _execute_help()
        # 3. executor.py: Add to objection_actions if personality can object
        # 4. llm_client.py: Add keyword detection for mock parser
        # 5. personality.py: Add triggers if marshals can object to it
        # 6. CLAUDE.md: Update Disobedience System documentation
        self.valid_actions = [
            "attack", "defend", "retreat", "move", "scout",
            "reinforce", "recruit", "help", "end_turn",
            # Tactical state actions (Phase 2.6)
            "drill", "fortify", "unfortify",
            # Stance system (Phase 2.7)
            "stance_change",
            # Hold/Wait actions
            "hold",  # Alias for defend - same mechanics
            "wait",  # Free action (0 cost) - pass turn for this marshal
            # Debug commands (Phase 2.8)
            "debug",  # For testing abilities: /debug counter_punch Davout
            # Cavalry recklessness (Phase 3)
            "charge",    # Glorious Charge - available at recklessness >= 1
            "restrain",  # Restrain marshal - normal attack instead of charge
        ]

        # Valid stances for stance_change command (Phase 2.7)
        self.valid_stances = ["neutral", "defensive", "aggressive"]

        # Known regions for fuzzy matching
        self.known_regions = [
            "Paris", "Belgium", "Netherlands", "Waterloo", "Rhine",
            "Bavaria", "Vienna", "Lyon", "Milan", "Marseille",
            "Geneva", "Brittany", "Bordeaux"
        ]

        # Known enemy marshals
        self.known_enemies = ["Wellington", "Blucher"]

        # Show actual mode from LLMClient (which reads from env if use_real_llm=None)
        mode = self.llm.provider_name.upper()
        key_source = self.llm.key_source
        print(f"Command Parser initialized: mode={mode}, key_source={key_source}")

    def _apply_fuzzy_matching(self, llm_result: Dict, command_text: str) -> tuple:
        """
        Apply fuzzy matching to correct typos in marshal and target names.

        Args:
            llm_result: The result from LLM parsing
            command_text: Original command text

        Returns:
            Tuple of (updated llm_result, error_dict or None)
            error_dict is set if an invalid marshal name was detected
        """
        # Fuzzy match marshal name if LLM extracted one
        if llm_result.get("marshal"):
            marshal_result = self.fuzzy_matcher.match_with_context(
                llm_result["marshal"],
                self.valid_marshals
            )
            if marshal_result["action"] in ["exact", "auto_correct"]:
                llm_result["marshal"] = marshal_result["match"]
            elif marshal_result["action"] == "suggest":
                # Medium confidence match - suggest to user
                return (llm_result, {
                    "error": f"Did you mean '{marshal_result['match']}'? ('{llm_result['marshal']}' not found)",
                    "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(self.valid_marshals)}"
                })
            else:  # action == "error"
                # No good match - return error with suggestions
                suggestions = marshal_result.get("suggestions", self.valid_marshals[:3])
                return (llm_result, {
                    "error": f"Marshal '{llm_result['marshal']}' not found",
                    "suggestion": f"Available marshals: {', '.join(suggestions)}"
                })
        # If marshal is None, try to extract from command text with fuzzy matching
        elif not llm_result.get("marshal"):
            # BUG-002 FIX: Skip fuzzy marshal matching for meta/help commands
            # Actions that don't require a marshal (meta commands + pending charge responses)
            meta_actions = ["help", "end_turn", "status", "unknown", "debug", "charge", "restrain"]
            if llm_result.get("action") in meta_actions:
                return (llm_result, None)  # Don't try to find a marshal

            words = command_text.split()
            for word in words:
                # Skip very short words, common words, and action keywords
                # BUG-002 FIX: Added help, wait, hold, retreat, fortify, drill, etc.
                skip_words = [
                    "to", "the", "at", "in", "on", "and", "or",
                    "attack", "defend", "move", "scout", "retreat",
                    "help", "wait", "hold", "fortify", "drill", "recruit",
                    "reinforce", "unfortify", "stance", "aggressive", "defensive", "neutral",
                    "go", "take", "be", "switch", "adopt", "return",  # Stance command verbs
                    "debug", "/debug", "set_location", "set_retreat", "set_recovery",  # Debug commands
                    "set_strength", "set_morale", "set_fortified", "ai_turn", "ai_state",
                    "charge", "restrain", "glorious",  # Cavalry recklessness commands
                ]
                if len(word) < 2 or word.lower() in skip_words:
                    continue

                marshal_result = self.fuzzy_matcher.match_with_context(
                    word,
                    self.valid_marshals
                )
                if marshal_result["action"] in ["exact", "auto_correct"]:
                    llm_result["marshal"] = marshal_result["match"]
                    break
                elif marshal_result["action"] == "suggest":
                    # Found a word that looks like a marshal but medium confidence
                    # Suggest to user instead of auto-assigning
                    return (llm_result, {
                        "error": f"Did you mean '{marshal_result['match']}'? ('{word}' not found)",
                        "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(self.valid_marshals)}"
                    })
                elif marshal_result["action"] == "error":
                    # Word doesn't match any marshal well. Check if it's a valid target.
                    # If it's not a target either, it's probably a bad marshal name.
                    all_targets = self.known_regions + self.known_enemies
                    target_check = self.fuzzy_matcher.match_with_context(word, all_targets)

                    # If this word also doesn't match any target, it's likely a bad marshal attempt
                    if target_check["action"] == "error":
                        suggestions = marshal_result.get("suggestions", self.valid_marshals[:3])
                        return (llm_result, {
                            "error": f"Marshal '{word}' not found",
                            "suggestion": f"Available marshals: {', '.join(suggestions)}"
                        })
                    # Otherwise, skip this word - it might be a target, not a marshal

        # Fuzzy match target name
        if llm_result.get("target"):
            # Try matching against regions first
            target_result = self.fuzzy_matcher.match_with_context(
                llm_result["target"],
                self.known_regions
            )

            # If no good region match, try enemies
            if target_result["action"] == "error":
                target_result = self.fuzzy_matcher.match_with_context(
                    llm_result["target"],
                    self.known_enemies
                )

            # Apply correction if found
            if target_result["action"] in ["exact", "auto_correct"]:
                llm_result["target"] = target_result["match"]

        # If target is still None, try to extract it from command text
        elif not llm_result.get("target"):
            # Build skip list: common words + action words + marshal name
            skip_words = [
                "to", "the", "at", "in", "on", "and", "or", "a", "an",
                # Action words - don't match these to targets
                "attack", "defend", "move", "scout", "retreat", "recruit",
                "reinforce", "help", "wait", "hold", "fortify", "drill",
                "unfortify", "stance", "aggressive", "defensive", "neutral",
                "charge", "restrain", "glorious",  # Cavalry recklessness commands
            ]
            # Also skip the marshal name if identified
            if llm_result.get("marshal"):
                skip_words.append(llm_result["marshal"].lower())

            # Extract potential target words from command (words after action)
            words = command_text.split()
            for word in words:
                # Skip common/action words and marshal name
                if word.lower() in skip_words:
                    continue
                # Skip very short words (likely not valid targets)
                if len(word) < 3:
                    continue

                # Try matching against all targets
                all_targets = self.known_regions + self.known_enemies
                target_result = self.fuzzy_matcher.match_with_context(
                    word,
                    all_targets
                )

                if target_result["action"] in ["exact", "auto_correct"]:
                    llm_result["target"] = target_result["match"]
                    break

        return (llm_result, None)

    def parse(self, command_text: str, game_state: Optional[Dict] = None) -> Dict:
        """
        Parse a command from the player.

        Args:
            command_text: Natural language command
            game_state: Current game state (for validation)

        Returns:
            Dict with the following structure on success:
            {
                "success": True,
                "command": {
                    "marshal": str | None,
                    "action": str,
                    "target": str | None,
                    "confidence": float,
                    "type": str | None,
                    "target_stance": str | None  # For stance_change
                },
                "raw_input": str,
                # Phase 5 - REQUIRED by main.py for feedback generation:
                "strategic_score": int,  # 0-100, from LLM or default 10
                "ambiguity": int,        # 0-100, from LLM or default 5
                "mode": str,             # "mock" or "live"
                "warning": str | None    # Optional validation warning
            }

            On failure:
            {
                "success": False,
                "error": str,
                "suggestion": str | None,
                "raw_input": str
            }

        IMPORTANT: main.py reads strategic_score, ambiguity, and mode from
        the TOP LEVEL of this return dict for feedback generation. If these
        fields are missing, feedback will silently fail to generate.
        """
        try:
            # Step 1: Use LLM to parse natural language
            llm_result = self.llm.parse_command(command_text, game_state)

            # Step 2: Apply fuzzy matching to correct typos
            llm_result, fuzzy_error = self._apply_fuzzy_matching(llm_result, command_text)

            # If fuzzy matching found an invalid marshal/target, return error immediately
            if fuzzy_error:
                return {
                    "success": False,
                    "error": fuzzy_error["error"],
                    "suggestion": fuzzy_error.get("suggestion"),
                    "raw_input": command_text
                }

            # Step 3: Validate the parsed command
            validation_result = self._validate_command(llm_result, game_state)

            # Step 4: Return complete result
            if validation_result.get("valid"):
                # Classify command type
                command_type = self._classify_command(llm_result, command_text)

                command_dict = {
                    "marshal": llm_result.get("marshal"),  # Can be None for general orders
                    "action": llm_result["action"],
                    "target": llm_result.get("target"),
                    "confidence": llm_result.get("confidence", 0.9),
                    "type": command_type
                }

                # BUG-005 FIX: Preserve target_stance for stance_change action
                if llm_result["action"] == "stance_change" and llm_result.get("target_stance"):
                    command_dict["target_stance"] = llm_result["target_stance"]

                result = {
                    "success": True,
                    "command": command_dict,
                    "raw_input": command_text,
                    # Phase 5: Include scores for feedback generation
                    "strategic_score": llm_result.get("strategic_score", 10),
                    "ambiguity": llm_result.get("ambiguity", 5),
                    "mode": llm_result.get("mode", "mock"),
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
            parsed_command: The parsed command dict from LLM (AFTER fuzzy matching)
            raw_input: The original command text

        Returns:
            Command type string
        """
        action = parsed_command.get("action", "")
        target = parsed_command.get("target")
        marshal = parsed_command.get("marshal")

        # If a marshal is set (after fuzzy matching), it's a specific order
        if marshal is not None:
            return "specific"

        # No marshal specified - classify as general order based on action
        if action == "attack":
            if not target:
                return "general_attack"  # "attack" alone - find nearest enemy
            else:
                return "auto_assign_attack"  # "attack Wellington" - find closest marshal to target
        elif action == "retreat":
            return "general_retreat"  # All forces retreat
        elif action == "defend":
            return "general_defensive"  # All forces defend

        # Default fallback
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


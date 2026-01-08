"""
LLM Client for Project Sovereign
Handles both mock (free, instant) and real (Claude API) command parsing
"""

import os
import re
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMClient:
    """
    Dual-mode LLM client:
    - Mock mode: Simple keyword matching (free, instant, offline)
    - Real mode: Claude API (costs money, requires internet)
    """

    def __init__(self, use_real_api: bool = False):
        """
        Initialize the LLM client.

        Args:
            use_real_api: If True, use real Claude API. If False, use mock.
        """
        self.use_real_api = use_real_api
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if use_real_api and not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        print(f"LLM Client initialized in {'REAL' if use_real_api else 'MOCK'} mode")

    def parse_command(self, command_text: str, game_state: Optional[Dict] = None) -> Dict:
        """
        Parse a natural language command into structured data.

        Args:
            command_text: The command from the player (e.g., "Ney, attack Wellington")
            game_state: Current game state (optional, for context)

        Returns:
            Dict with parsed command structure:
            {
                "marshal": "Ney",
                "action": "attack",
                "target": "Wellington",
                "confidence": 0.95
            }
        """
        if self.use_real_api:
            return self._parse_with_claude(command_text, game_state)
        else:
            return self._parse_with_mock(command_text)

    def _parse_with_mock(self, command_text: str) -> Dict:
        """
        Mock parser using simple keyword matching.
        Fast, free, deterministic - perfect for development!
        """
        command_lower = command_text.lower()

        # Extract marshal name - find the FIRST mentioned marshal
        marshal = None  # Start with None for general orders

        # Known marshals with their search patterns
        known_marshals = [
            ("ney", "Ney"),
            ("davout", "Davout"),
            ("grouchy", "Grouchy"),
            ("murat", "Murat"),
            ("soult", "Soult"),
            ("lannes", "Lannes"),
        ]

        # Find which marshal appears FIRST in the command
        first_position = len(command_lower) + 1
        for pattern, name in known_marshals:
            pos = command_lower.find(pattern)
            if pos != -1 and pos < first_position:
                first_position = pos
                marshal = name

        # Also check for "Marshal [Name]" pattern
        match = re.search(r'marshal\s+([A-Z][a-z]+)', command_text)
        if match:
            match_pos = command_lower.find("marshal")
            if match_pos != -1 and match_pos < first_position:
                marshal = match.group(1)

        # If still None, that's OK - means general order

        # Extract action (ALWAYS set a value)
        action = "unknown"  # Default
        if "attack" in command_lower:
            action = "attack"
        elif "defend" in command_lower or "hold" in command_lower:
            action = "defend"
        elif "retreat" in command_lower or "fall back" in command_lower:
            action = "retreat"
        elif "move" in command_lower or "march" in command_lower:
            action = "move"
        elif "scout" in command_lower or "reconnaissance" in command_lower:
            action = "scout"
        elif "reinforce" in command_lower or "support" in command_lower:
            action = "reinforce"
        elif "recruit" in command_lower or "raise" in command_lower or "conscript" in command_lower:
            action = "recruit"

        # Extract target (can be None)
        target = None

        # Enemy commanders
        if "wellington" in command_lower:
            target = "Wellington"
        elif "blucher" in command_lower or "blücher" in command_lower:
            target = "Blucher"
        elif "prussian" in command_lower:
            target = "Prussians"
        elif "british" in command_lower:
            target = "British"

        # Regions
        elif "belgium" in command_lower:
            target = "Belgium"
        elif "waterloo" in command_lower:
            target = "Waterloo"
        elif "paris" in command_lower:
            target = "Paris"
        elif "lyon" in command_lower:
            target = "Lyon"
        elif "brittany" in command_lower:
            target = "Brittany"
        elif "bordeaux" in command_lower:
            target = "Bordeaux"
        elif "rhine" in command_lower:
            target = "Rhine"
        elif "bavaria" in command_lower:
            target = "Bavaria"
        elif "vienna" in command_lower:
            target = "Vienna"
        elif "milan" in command_lower:
            target = "Milan"
        elif "marseille" in command_lower:
            target = "Marseille"
        elif "geneva" in command_lower:
            target = "Geneva"
        elif "netherlands" in command_lower:
            target = "Netherlands"

        # For reinforce commands, check for friendly marshal names as targets
        # Find the SECOND marshal mentioned (the one being reinforced)
        if target is None and action == "reinforce":
            second_marshal = None
            second_position = len(command_lower) + 1

            for pattern, name in known_marshals:
                pos = command_lower.find(pattern)
                if pos != -1 and name != marshal:  # Not the commanding marshal
                    if second_marshal is None or pos < second_position:
                        # Find this marshal's position (should be after the first)
                        second_position = pos
                        second_marshal = name

            if second_marshal:
                target = second_marshal

        # Return parsed command
        return {
            "marshal": marshal,
            "action": action,
            "target": target,
            "confidence": 0.9,
            "raw_command": command_text,
            "mode": "mock"
        }

    def _parse_with_claude(self, command_text: str, game_state: Optional[Dict] = None) -> Dict:
        """
        Real Claude API parsing.
        Will implement this in Day 5-7 once mock works!
        """
        # TODO: Implement Claude API call
        # For now, just use mock
        print("Real API not implemented yet - using mock")
        return self._parse_with_mock(command_text)


# Test function
if __name__ == "__main__":
    """
    Quick test to verify the client works.
    Run this file directly: python backend/ai/llm_client.py
    """
    print("=" * 50)
    print("LLM CLIENT TEST")
    print("=" * 50)

    # Create mock client
    client = LLMClient(use_real_api=False)

    # Test commands
    test_commands = [
        "Ney, attack Wellington",
        "Marshal Davout, defend the ridge",
        "Grouchy, pursue the Prussians",
        "Attack!",
        "Move to Belgium",
    ]

    print("\nTesting command parsing:\n")
    for cmd in test_commands:
        print(f"Command: '{cmd}'")
        result = client.parse_command(cmd)
        print(f"Parsed:  {result}")
        print()

    print("=" * 50)
    print("TEST COMPLETE!")
    print("=" * 50)
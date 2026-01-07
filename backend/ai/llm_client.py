
"""
LLM Client for Project Sovereign
Handles both mock (free, instant) and real (Claude API) command parsing
"""

import os
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

        # Extract marshal name
        marshal = None  # Start with None for general orders

        # Check for known marshals first
        if "ney" in command_lower:
            marshal = "Ney"
        elif "davout" in command_lower:
            marshal = "Davout"
        elif "grouchy" in command_lower:
            marshal = "Grouchy"
        elif "murat" in command_lower:
            marshal = "Murat"
        elif "soult" in command_lower:
            marshal = "Soult"
        elif "lannes" in command_lower:
            marshal = "Lannes"
        elif "marshal" in command_lower:
            # Look for "Marshal [Name]"
            import re
            match = re.search(r'marshal\s+([A-Z][a-z]+)', command_text)
            if match:
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
        elif "scout" in command_lower or "reconnaissance" in command_lower:
            action = "scout"
        elif "reinforce" in command_lower or "support" in command_lower:
            action = "reinforce"
        elif "recruit" in command_lower or "raise" in command_lower or "conscript" in command_lower:
            action = "recruit"

        # Extract target (can be None)
        target = None
        if "wellington" in command_lower:
            target = "Wellington"
        elif "blucher" in command_lower or "blücher" in command_lower:
            target = "Blucher"
        elif "prussian" in command_lower:
            target = "Prussians"
        elif "british" in command_lower:
            target = "British"
        elif "belgium" in command_lower:
            target = "Belgium"
        elif "waterloo" in command_lower:
            target = "Waterloo"
        elif "paris" in command_lower:
            target = "Paris"
        # For reinforce commands, check for friendly marshal names as targets
        if target is None and action == "reinforce":
            # Check for marshal names that aren't the commanding marshal
            if "ney" in command_lower and marshal != "Ney":
                target = "Ney"
            elif "davout" in command_lower and marshal != "Davout":
                target = "Davout"
            elif "grouchy" in command_lower and marshal != "Grouchy":
                target = "Grouchy"
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


## 🧪 TEST IT!

### Run the Test
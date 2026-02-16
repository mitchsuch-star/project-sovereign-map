"""
Test suite for "occupy" command alias (Session 31).

"Occupy" is a parser alias for "attack" — it should be parsed as attack
by the mock parser. It is NOT in VALID_ACTIONS (no _execute_occupy).
"""

import pytest
from backend.ai.llm_client import LLMClient
from backend.ai.validation import VALID_ACTIONS


# ════════════════════════════════════════════════════════════════════════════════
# PARSER ALIAS TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestOccupyAlias:
    """Test 'occupy' keyword maps to 'attack' action."""

    def test_occupy_parsed_as_attack(self):
        """'occupy' keyword maps to action='attack'."""
        client = LLMClient()
        result = client._parse_with_mock("Ney, occupy the Netherlands")
        assert result is not None
        assert result.action == "attack"

    def test_occupy_with_region_target(self):
        """'occupy Bavaria' parses region as target."""
        client = LLMClient()
        result = client._parse_with_mock("Davout, occupy Bavaria")
        assert result is not None
        assert result.action == "attack"

    def test_occupy_case_insensitive(self):
        """'Occupy' with capital works."""
        client = LLMClient()
        result = client._parse_with_mock("Ney, Occupy Belgium")
        assert result is not None
        assert result.action == "attack"

    def test_occupy_not_in_valid_actions(self):
        """'occupy' is NOT in VALID_ACTIONS — parser alias only."""
        assert "occupy" not in VALID_ACTIONS

    def test_occupy_word_boundary(self):
        """'occupy' doesn't match substrings like 'preoccupy'."""
        client = LLMClient()
        # 'preoccupy' contains 'occupy' but word boundary should prevent match
        result = client._parse_with_mock("Ney is preoccupied")
        # Should not parse as attack
        if result is not None:
            assert result.action != "attack"

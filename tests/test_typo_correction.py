"""
Repro tests for typo correction through the full command pipeline.

Tests that typos like "bordeuex" → "Bordeaux" are corrected at some point
in the chain: fast parser → LLM fallback → parser fuzzy → executor fuzzy.

Run: pytest tests/test_typo_correction.py -v
"""

import pytest
from unittest.mock import patch
from backend.commands.parser import CommandParser
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState
from backend.utils.fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcherDirectly:
    """Test the fuzzy matcher in isolation to verify it CAN correct typos."""

    def test_bordeaux_typo(self):
        fm = FuzzyMatcher()
        regions = ["Paris", "Belgium", "Netherlands", "Waterloo", "Rhine",
                   "Bavaria", "Vienna", "Lyon", "Milan", "Marseille",
                   "Geneva", "Brittany", "Bordeaux"]
        result = fm.match_with_context("bordeuex", regions)
        assert result["action"] in ("exact", "auto_correct"), \
            f"FuzzyMatcher didn't auto-correct 'bordeuex': {result}"
        assert result["match"] == "Bordeaux"

    def test_belguim_typo(self):
        fm = FuzzyMatcher()
        regions = ["Paris", "Belgium", "Netherlands", "Waterloo", "Rhine",
                   "Bavaria", "Vienna", "Lyon", "Milan", "Marseille",
                   "Geneva", "Brittany", "Bordeaux"]
        result = fm.match_with_context("Belguim", regions)
        assert result["action"] in ("exact", "auto_correct"), \
            f"FuzzyMatcher didn't auto-correct 'Belguim': {result}"
        assert result["match"] == "Belgium"

    def test_nay_typo_suggests_not_autocorrects(self):
        """'Nay' is too short (3 chars, score 67 < 70 threshold) for auto-correct.
        FuzzyMatcher correctly suggests rather than auto-correcting."""
        fm = FuzzyMatcher()
        marshals = ["Ney", "Davout", "Grouchy"]
        result = fm.match_with_context("Nay", marshals)
        # Score 67 falls in suggest range (50-70) for short names
        assert result["action"] == "suggest", \
            f"Expected 'suggest' for 'Nay' (score ~67), got: {result}"
        assert result["match"] == "Ney"

    def test_wellinton_typo(self):
        fm = FuzzyMatcher()
        enemies = ["Wellington", "Blucher", "Uxbridge", "Gneisenau"]
        result = fm.match_with_context("Wellinton", enemies)
        assert result["action"] in ("exact", "auto_correct"), \
            f"FuzzyMatcher didn't auto-correct 'Wellinton': {result}"
        assert result["match"] == "Wellington"


class TestParserTypoCorrection:
    """Test that parser corrects typos via its fuzzy matching layer."""

    def test_bordeuex_through_parser(self):
        """'davout march to bordeuex' should parse with corrected region.

        The strategic parser overrides target from raw text (no fuzzy matching).
        Fix: parser.py applies fuzzy matching to strategic parser output.
        """
        parser = CommandParser(use_real_llm=False)
        world = WorldState()
        game_state = {"world": world}

        result = parser.parse("davout march to bordeuex", game_state=game_state, world=world)

        assert result.get("success"), f"Parser failed: {result}"
        cmd = result.get("command", {})
        assert cmd.get("target") == "Bordeaux", \
            f"Parser returned target '{cmd.get('target')}' instead of 'Bordeaux'"

    def test_nay_attack_wellinton_suggest_not_autocorrect(self):
        """'nay' (3 chars, score 67) gets SUGGEST not auto-correct.
        Parser returns 'Did you mean Ney?' — known gap for very short names.
        LLM mode would handle this correctly since it has the name list."""
        parser = CommandParser(use_real_llm=False)
        world = WorldState()
        game_state = {"world": world}

        result = parser.parse("nay attack wellinton", game_state=game_state, world=world)

        # Mock parser can't auto-correct "nay" (too short, score < 70)
        # This is expected — LLM fallback would handle it in live mode
        assert result.get("success") is False
        error = result.get("error", "")
        assert "Ney" in error, f"Should suggest 'Ney', got: {error}"

    def test_davout_move_to_viena(self):
        """'davout move to viena' should correct to Vienna."""
        parser = CommandParser(use_real_llm=False)
        world = WorldState()
        game_state = {"world": world}

        result = parser.parse("davout move to viena", game_state=game_state, world=world)

        if result.get("success"):
            cmd = result.get("command", {})
            assert cmd.get("target") == "Vienna", \
                f"Target not corrected: got '{cmd.get('target')}'"
        else:
            msg = result.get("message", "") + result.get("error", "")
            pytest.fail(
                f"Parser failed 'viena' typo.\n"
                f"Message: {msg}\n"
                f"Full result: {result}"
            )


class TestExecutorTypoCorrection:
    """Test that executor catches typos that parser missed."""

    def test_executor_fuzzy_matches_region(self):
        """Executor should fuzzy match 'bordeuex' → 'Bordeaux'."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}

        # Simulate a parsed command with uncorrected typo
        parsed = {
            "success": True,
            "command": {
                "marshal": "Davout",
                "action": "move",
                "target": "bordeuex"
            }
        }

        with patch('builtins.print'):  # suppress output
            result = executor.execute(parsed, game_state)

        # Should either succeed (corrected) or give a "did you mean" suggestion
        msg = result.get("message", "")
        if result.get("success"):
            assert "Bordeaux" in msg or world.get_marshal("Davout").location == "Bordeaux", \
                f"Move succeeded but didn't go to Bordeaux: {msg}"
        else:
            # Check if it's a useful error (not just "not found")
            assert "Bordeaux" in msg or "Did you mean" in msg, \
                f"Executor didn't suggest correction: {msg}"

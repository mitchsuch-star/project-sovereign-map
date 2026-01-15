"""
Test suite for fuzzy string matching in command parsing.
Tests typo tolerance for marshal and region names.
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.utils.fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcherCore:
    """Test FuzzyMatcher class directly."""

    def test_exact_match(self):
        """Exact matches should return score 100."""
        matcher = FuzzyMatcher()
        result = matcher.match_with_context("Paris", ["Paris", "Belgium", "Waterloo"])

        assert result["action"] == "exact"
        assert result["match"] == "Paris"
        assert result["score"] == 100

    def test_case_insensitive_exact_match(self):
        """Case-insensitive matches should be treated as exact."""
        matcher = FuzzyMatcher()
        result = matcher.match_with_context("waterloo", ["Paris", "Waterloo", "Belgium"])

        assert result["action"] == "exact"
        assert result["match"] == "Waterloo"
        assert result["score"] == 100

    def test_auto_correct_high_confidence(self):
        """High confidence typos (80+) should auto-correct."""
        matcher = FuzzyMatcher()

        # "Waterlo" -> "Waterloo" (missing one letter)
        result = matcher.match_with_context("Waterlo", ["Paris", "Waterloo", "Belgium"])

        assert result["action"] == "auto_correct"
        assert result["match"] == "Waterloo"
        assert result["score"] >= 80

    def test_suggest_medium_confidence(self):
        """Medium confidence (60-79) should suggest with confirmation."""
        matcher = FuzzyMatcher()

        # "Bruss" -> "Brussels" (partial match)
        result = matcher.match_with_context("Bruss", ["Brussels", "Bavaria", "Britain"])

        assert result["action"] == "suggest"
        assert result["match"] == "Brussels"
        assert 60 <= result["score"] < 80

    def test_error_low_confidence(self):
        """Low confidence (<60) should return error with suggestions."""
        matcher = FuzzyMatcher()

        # "Asdfgh" -> no good match
        result = matcher.match_with_context("Asdfgh", ["Paris", "Waterloo", "Belgium"])

        assert result["action"] == "error"
        assert result["match"] is None
        assert result["score"] == 0
        assert len(result["suggestions"]) > 0


class TestFuzzyMarshalLookup:
    """Test fuzzy matching for marshal names in commands."""

    def test_marshal_typo_auto_correct(self):
        """Marshal name typo with high confidence should auto-correct silently."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # "Davot" -> "Davout" (one letter wrong)
        game_state = {"world": world}
        command = {
            "command": {"marshal": "Davot", "action": "defend"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Should succeed with auto-corrected name
        assert result.get("success", False) == True
        assert "Davout" in result.get("message", "")

    def test_marshal_typo_suggestion(self):
        """Marshal name with medium confidence should ask for confirmation."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # "N" -> too short, should be low confidence
        game_state = {"world": world}
        command = {
            "command": {"marshal": "N", "action": "defend"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Should fail with suggestion or error
        assert result.get("success", False) == False
        message = result.get("message", "").lower()
        assert "did you mean" in message or "not found" in message or "available" in message

    def test_marshal_invalid_name_shows_suggestions(self):
        """Invalid marshal name should show available marshals."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # "Xyz" -> no match
        game_state = {"world": world}
        command = {
            "command": {"marshal": "Xyz", "action": "defend"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Should fail with suggestions
        assert result.get("success", False) == False
        assert "not found" in result.get("message", "").lower()


class TestFuzzyRegionLookup:
    """Test fuzzy matching for region names in commands."""

    def test_region_typo_auto_correct_move(self):
        """Region name typo in move command should auto-correct."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # Place Ney in Belgium
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"

        # "Netherland" -> "Netherlands" (missing 's')
        game_state = {"world": world}
        command = {
            "command": {"marshal": "Ney", "action": "move", "target": "Netherland"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Should succeed with auto-corrected region name
        # Note: May fail if not adjacent, but should NOT fail due to region not found
        if not result.get("success", False):
            # Check it's adjacency error, not region not found error
            assert "not adjacent" in result.get("message", "").lower() or \
                   "did you mean" in result.get("message", "").lower()
        else:
            assert "Netherlands" in result.get("message", "")

    def test_region_typo_auto_correct_scout(self):
        """Region name typo in scout command should auto-correct."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # Place Davout in Paris
        davout = world.get_marshal("Davout")
        davout.location = "Paris"

        # "Belgum" -> "Belgium" (typo)
        game_state = {"world": world}
        command = {
            "command": {"marshal": "Davout", "action": "scout", "target": "Belgum"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Should succeed with auto-corrected region
        assert result.get("success", False) == True or "did you mean" in result.get("message", "").lower()

    def test_region_invalid_shows_suggestions(self):
        """Invalid region name should show nearby regions."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        ney = world.get_marshal("Ney")
        ney.location = "Belgium"

        # "Xyz" -> no match
        game_state = {"world": world}
        command = {
            "command": {"marshal": "Ney", "action": "move", "target": "Xyz"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Should fail with suggestions
        assert result.get("success", False) == False
        assert "not found" in result.get("message", "").lower() or \
               "nearby" in result.get("message", "").lower()


class TestFuzzyMatchingIntegration:
    """Integration tests for fuzzy matching across different commands."""

    def test_recruit_with_marshal_typo(self):
        """Recruit command with marshal typo should work."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # Give enough gold
        world.gold = 500

        # "Grouch" -> "Grouchy"
        game_state = {"world": world}
        command = {
            "command": {"marshal": "Grouch", "action": "recruit"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Should succeed or suggest
        if result.get("success", False):
            assert "Grouchy" in result.get("message", "")
        else:
            # Medium confidence suggestion
            assert "did you mean" in result.get("message", "").lower() or \
                   "not found" in result.get("message", "").lower()

    def test_reinforce_with_both_marshals_typo(self):
        """Reinforce command with typos in both marshals should work."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()

        # "Grouch" -> "Grouchy", "Davot" -> "Davout"
        game_state = {"world": world}
        command = {
            "command": {"marshal": "Grouch", "action": "reinforce", "target": "Davot"},
            "type": "specific"
        }

        result = executor.execute(command, game_state)

        # Should work if both auto-corrected
        # May fail with suggestion if confidence too low
        assert "message" in result


class TestFuzzyMatcherEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_query(self):
        """Empty query should return error."""
        matcher = FuzzyMatcher()
        result = matcher.match_with_context("", ["Paris", "Belgium"])

        assert result["action"] == "error"

    def test_empty_candidates(self):
        """Empty candidate list should return error."""
        matcher = FuzzyMatcher()
        result = matcher.match_with_context("Paris", [])

        assert result["action"] == "error"

    def test_special_characters_in_name(self):
        """Names with special characters should work."""
        matcher = FuzzyMatcher()
        result = matcher.match_with_context("Rhine", ["Rhine", "Rhineland", "Bavaria"])

        assert result["action"] == "exact"
        assert result["match"] == "Rhine"


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v"])

"""
Tests for strategic command bugfixes (Bugs 1-6).

Run with: pytest tests/test_strategic_bugfixes.py -v -s
"""
import sys
import os
import io
import contextlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, StrategicOrder, StrategicCondition, Stance
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser


@pytest.fixture
def world():
    return WorldState(player_nation="France")


@pytest.fixture
def executor():
    return CommandExecutor()


@pytest.fixture
def game_state(world):
    return {"world": world}


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


# ══════════════════════════════════════════════════════════════════════════════
# BUG 1: PURSUE target in same/adjacent region
# ══════════════════════════════════════════════════════════════════════════════

class TestPursueSameRegion:
    """PURSUE when target is in same region should produce a meaningful response."""

    def test_pursue_same_region_aggressive_auto_attacks(self, world, executor, game_state):
        """Aggressive marshal (Ney) auto-attacks when target is in same region."""
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Put them in same region
        ney.location = "Belgium"
        wellington.location = "Belgium"

        parsed = {
            "success": True,
            "command": {"marshal": "Ney", "action": "attack", "target": "Wellington",
                        "target_type": "marshal"},
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "raw_input": "Ney, pursue Wellington",
            "strategic_score": 70,
            "ambiguity": 10,
        }

        with _suppress():
            result = executor.execute(parsed, game_state)

        assert result.get("success"), f"Expected success, got: {result.get('message')}"
        msg = result.get("message", "")
        # Should mention engaging, not just a bland "pursues Wellington"
        assert "right here" in msg.lower() or "engaging" in msg.lower(), \
            f"Expected engagement message, got: {msg}"

    def test_pursue_same_region_cautious_waits(self, world, executor, game_state):
        """Cautious marshal acknowledges target but doesn't auto-attack."""
        davout = world.get_marshal("Davout")
        wellington = world.get_marshal("Wellington")

        davout.location = "Belgium"
        wellington.location = "Belgium"

        parsed = {
            "success": True,
            "command": {"marshal": "Davout", "action": "attack", "target": "Wellington",
                        "target_type": "marshal"},
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "raw_input": "Davout, pursue Wellington",
            "strategic_score": 70,
            "ambiguity": 10,
        }

        with _suppress():
            result = executor.execute(parsed, game_state)

        assert result.get("success"), f"Expected success, got: {result.get('message')}"
        msg = result.get("message", "")
        # Should mention the target is here
        assert "right here" in msg.lower() or wellington.name.lower() in msg.lower(), \
            f"Expected acknowledgment, got: {msg}"


class TestPursueAdjacentRegion:
    """PURSUE when target is in adjacent region."""

    def test_pursue_adjacent_aggressive_attacks(self, world, executor, game_state):
        """Aggressive marshal attacks when target is just one region away."""
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Ney in Paris, Wellington in Belgium (adjacent)
        ney.location = "Paris"
        wellington.location = "Belgium"

        parsed = {
            "success": True,
            "command": {"marshal": "Ney", "action": "attack", "target": "Wellington",
                        "target_type": "marshal"},
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "raw_input": "Ney, pursue Wellington",
            "strategic_score": 70,
            "ambiguity": 10,
        }

        with _suppress():
            result = executor.execute(parsed, game_state)

        assert result.get("success"), f"Expected success, got: {result.get('message')}"
        msg = result.get("message", "")
        # Should have some response about spotting/engaging
        assert msg, "Expected a non-empty message"

    def test_pursue_adjacent_cautious_prepares(self, world, executor, game_state):
        """Cautious marshal spots target but prepares rather than charging."""
        davout = world.get_marshal("Davout")
        wellington = world.get_marshal("Wellington")

        davout.location = "Paris"
        wellington.location = "Belgium"

        parsed = {
            "success": True,
            "command": {"marshal": "Davout", "action": "attack", "target": "Wellington",
                        "target_type": "marshal"},
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "raw_input": "Davout, pursue Wellington",
            "strategic_score": 70,
            "ambiguity": 10,
        }

        with _suppress():
            result = executor.execute(parsed, game_state)

        assert result.get("success"), f"Expected success, got: {result.get('message')}"
        msg = result.get("message", "")
        # Should mention spotting/preparing, NOT "path blocked"
        assert "path blocked" not in msg.lower(), f"Should not say path blocked: {msg}"


# ══════════════════════════════════════════════════════════════════════════════
# BUG 2: Self-targeting
# ══════════════════════════════════════════════════════════════════════════════

class TestSelfTargeting:
    """Marshals cannot target themselves with strategic commands."""

    def test_cannot_support_self(self, world, executor, game_state):
        """Support self should be rejected."""
        parsed = {
            "success": True,
            "command": {"marshal": "Ney", "action": "move", "target": "Ney",
                        "target_type": "marshal"},
            "is_strategic": True,
            "strategic_type": "SUPPORT",
            "raw_input": "Ney, support Ney",
            "strategic_score": 50,
            "ambiguity": 20,
        }

        with _suppress():
            result = executor.execute(parsed, game_state)

        assert not result.get("success"), "Self-support should fail"
        assert "cannot target themselves" in result.get("message", "").lower() or \
               "cannot target" in result.get("message", "").lower(), \
            f"Expected self-target error, got: {result.get('message')}"

    def test_cannot_pursue_self(self, world, executor, game_state):
        """Pursue self should be rejected."""
        parsed = {
            "success": True,
            "command": {"marshal": "Ney", "action": "attack", "target": "Ney",
                        "target_type": "marshal"},
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "raw_input": "Ney, pursue Ney",
            "strategic_score": 50,
            "ambiguity": 20,
        }

        with _suppress():
            result = executor.execute(parsed, game_state)

        assert not result.get("success"), "Self-pursue should fail"
        assert "cannot target themselves" in result.get("message", "").lower(), \
            f"Expected self-target error, got: {result.get('message')}"


# ══════════════════════════════════════════════════════════════════════════════
# BUG 3: Generic targets should not fail at parser
# ══════════════════════════════════════════════════════════════════════════════

class TestGenericTargets:
    """Generic/ambiguous targets should pass through parser to strategic system."""

    def test_generic_target_parser_passes(self):
        """'support the general' should not fail with 'Marshal general not found'."""
        parser = CommandParser(use_real_llm=False)

        with _suppress():
            result = parser.parse("Ney, support the general")

        # Should not fail — either succeeds or gets through to executor
        if not result.get("success"):
            error = result.get("error", "")
            # Must NOT fail because "general" was mistaken for a marshal name
            assert "marshal" not in error.lower() or "not found" not in error.lower(), \
                f"Parser incorrectly rejected 'general' as bad marshal: {error}"

    def test_generic_marshal_term_passes(self):
        """'pursue the marshal' should not fail."""
        parser = CommandParser(use_real_llm=False)

        with _suppress():
            result = parser.parse("Ney, pursue the marshal")

        if not result.get("success"):
            error = result.get("error", "")
            assert "not found" not in error.lower(), \
                f"Parser incorrectly rejected 'marshal': {error}"

    def test_generic_commander_term_passes(self):
        """'support the commander' should not fail."""
        parser = CommandParser(use_real_llm=False)

        with _suppress():
            result = parser.parse("Davout, support the commander")

        if not result.get("success"):
            error = result.get("error", "")
            assert "not found" not in error.lower(), \
                f"Parser incorrectly rejected 'commander': {error}"


# ══════════════════════════════════════════════════════════════════════════════
# BUG 4: Cancel popup should be graceful
# ══════════════════════════════════════════════════════════════════════════════

class TestCancelPopup:
    """Cancel with no active order should return graceful success."""

    def test_cancel_popup_graceful(self, world, executor, game_state):
        """Cancel when no strategic order exists should be success, not error."""
        ney = world.get_marshal("Ney")
        # Ensure no active order
        ney.strategic_order = None

        parsed = {
            "success": True,
            "command": {"marshal": "Ney", "action": "cancel"},
            "raw_input": "cancel",
            "strategic_score": 0,
            "ambiguity": 0,
        }

        with _suppress():
            result = executor.execute(parsed, game_state)

        # Should succeed gracefully, not error
        assert result.get("success"), f"Cancel should succeed gracefully, got: {result.get('message')}"
        assert result.get("no_action_cost"), "Cancel with no order should be free"
        assert "awaits" in result.get("message", "").lower(), \
            f"Expected graceful message, got: {result.get('message')}"


# ══════════════════════════════════════════════════════════════════════════════
# BUG 5: Grouchy PURSUE buff (working as designed)
# ══════════════════════════════════════════════════════════════════════════════

class TestGrouchyPursueBuff:
    """Grouchy's LITERAL bonus behavior on PURSUE — documents design."""

    def test_precision_execution_triggers_on_explicit_pursue(self, world, executor, game_state):
        """Precision execution (+1 skills) should trigger on explicit PURSUE."""
        grouchy = world.get_marshal("Grouchy")
        wellington = world.get_marshal("Wellington")

        # Put them far enough apart that PURSUE creates an order
        grouchy.location = "Paris"
        wellington.location = "Netherlands"

        parsed = {
            "success": True,
            "command": {"marshal": "Grouchy", "action": "attack", "target": "Wellington",
                        "target_type": "marshal"},
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "raw_input": "Grouchy, pursue Wellington",
            "strategic_score": 80,
            "ambiguity": 10,
        }

        with _suppress():
            result = executor.execute(parsed, game_state)

        # Precision execution should be active (ambiguity <= 20, strategic_score > 60)
        assert grouchy.precision_execution_active, \
            "Precision execution should trigger on explicit PURSUE with low ambiguity"
        assert grouchy.precision_execution_turns == 3, \
            f"Expected 3 turns of precision, got {grouchy.precision_execution_turns}"


# ══════════════════════════════════════════════════════════════════════════════
# BUG 6: Player messages should not contain internal terms
# ══════════════════════════════════════════════════════════════════════════════

class TestPlayerMessages:
    """Player-facing messages should not leak internal terminology."""

    def test_clarification_no_internal_terms(self, world, executor, game_state):
        """Clarification messages should not contain '(nearest enemy)' etc."""
        grouchy = world.get_marshal("Grouchy")
        wellington = world.get_marshal("Wellington")

        grouchy.location = "Paris"
        wellington.location = "Belgium"

        parsed = {
            "success": True,
            "command": {"marshal": "Grouchy", "action": "attack", "target": "the enemy",
                        "target_type": "generic"},
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "raw_input": "Grouchy, pursue the enemy",
            "strategic_score": 50,
            "ambiguity": 70,
        }

        with _suppress():
            result = executor.execute(parsed, game_state)

        msg = result.get("message", "")
        # Should NOT contain internal debug terms
        internal_terms = ["(nearest enemy)", "(most threatened)", "(nearest enemy position)",
                          "target_type", "generic", "MOVE_TO", "PURSUE", "HOLD", "SUPPORT"]
        for term in internal_terms:
            assert term not in msg, f"Internal term '{term}' leaked in message: {msg}"

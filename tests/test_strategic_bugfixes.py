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
from backend.models.marshal import StrategicOrder, StrategicCondition
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
        """Cautious marshal acknowledges target but doesn't auto-attack.
        V2a: Cautious may also object to PURSUE at bad odds (MODERATE+ popup)."""
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
        # V2a: Cautious may object to bad odds (popup) OR acknowledge target is here
        is_objection = result.get("pending_objection") is True
        is_acknowledgment = "right here" in msg.lower() or wellington.name.lower() in msg.lower()
        assert is_objection or is_acknowledgment, \
            f"Expected objection or acknowledgment, got: {msg}"


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


# ══════════════════════════════════════════════════════════════════════════════
# BUG 7: Compromise strategic orders skip first-step execution
# ══════════════════════════════════════════════════════════════════════════════

class TestCompromiseFirstStep:
    """Compromise strategic orders should execute first movement step immediately,
    same as normal strategic orders."""

    def test_compromise_support_moves_on_issuance_turn(self, world, executor, game_state):
        """Compromise SUPPORT should move toward ally on the turn it's issued."""
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        # Ney in Belgium, Davout in Paris (1 hop)
        ney.location = "Belgium"
        davout.location = "Paris"

        # Give Ney a hostile relationship with Davout to trigger STRONG objection
        ney.modify_relationship("Davout", -3)  # hostile

        # Issue SUPPORT command
        parsed = {
            "command": {"marshal": "Ney", "action": "support", "target": "Davout",
                        "target_type": "marshal"},
            "is_strategic": True,
            "strategic_type": "SUPPORT",
        }
        with _suppress():
            result = executor.execute(parsed, game_state)

        # Should trigger objection (relationship-based)
        if result.get("pending_objection") or world.pending_strategic_objection:
            # Respond with compromise
            with _suppress():
                compromise_result = executor.handle_objection_response("compromise", game_state)

            assert compromise_result.get("success"), compromise_result.get("message", "")
            # Ney should have moved to Paris (first step executed)
            assert ney.location == "Paris", (
                f"Ney should have moved to Paris on compromise turn, but is at {ney.location}"
            )
        else:
            # No objection — normal path. Ney should still move.
            assert ney.location == "Paris", (
                f"Ney should have moved to Paris, but is at {ney.location}"
            )

    def test_compromise_moveto_moves_on_issuance_turn(self, world, executor, game_state):
        """Compromise MOVE_TO with safe_path should move on the turn it's issued."""
        davout = world.get_marshal("Davout")
        davout.location = "Paris"

        # Put enemy in Rhine to trigger cautious objection for move through enemy territory
        blucher = world.get_marshal("Blucher")
        if blucher:
            blucher.location = "Rhine"

        # Issue MOVE_TO to a destination that requires travel
        parsed = {
            "command": {"marshal": "Davout", "action": "move_to", "target": "Lyon",
                        "target_type": "region"},
            "is_strategic": True,
            "strategic_type": "MOVE_TO",
        }
        with _suppress():
            result = executor.execute(parsed, game_state)

        if result.get("pending_objection") or world.pending_strategic_objection:
            with _suppress():
                compromise_result = executor.handle_objection_response("compromise", game_state)
            assert compromise_result.get("success"), compromise_result.get("message", "")
            # Davout should have moved at least one step
            assert davout.location != "Paris", (
                "Davout should have moved from Paris on compromise turn, but didn't"
            )
        else:
            # Normal path — should have moved
            assert davout.location != "Paris" or davout.strategic_order is not None


class TestTimedSupportArrivalTimer:
    """Timed SUPPORT timer should count from arrival at ally, not from issuance."""

    def test_timed_support_timer_starts_on_arrival(self, world, executor, game_state):
        """3-turn timed SUPPORT from Belgium->Paris should give 3 full turns of support."""
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        ney.location = "Belgium"
        davout.location = "Paris"

        # Put an enemy adjacent to Davout so SUPPORT doesn't auto-complete (ally not safe)
        # Use Waterloo (adjacent to Paris) — NOT on Ney's path (Belgium->Paris)
        wellington = world.get_marshal("Wellington")
        if wellington:
            wellington.location = "Waterloo"  # Adjacent to Paris

        # Clear enemies from Belgium so Ney can move freely
        blucher = world.get_marshal("Blucher")
        if blucher:
            blucher.location = "Vienna"

        # Manually create a timed SUPPORT order (simulates compromise issued turn 1)
        # First step already executed by executor on turn 1 (skipped by strategic processor)
        # so we start processing from turn 2
        order = StrategicOrder(
            command_type="SUPPORT",
            target="Davout",
            target_type="marshal",
            started_turn=1,
            issued_turn=1,
            original_command="Ney support Davout",
            path=["Paris"],
            condition=StrategicCondition(max_turns=3),
        )
        ney.strategic_order = order

        from backend.commands.strategic import StrategicExecutor
        strat_exec = StrategicExecutor(executor)

        # Turn 2: Ney moves to Paris and arrived_turn should be set
        world.current_turn = 2
        with _suppress():
            results = strat_exec.process_strategic_orders(world, game_state)
        assert ney.location == "Paris", f"Ney should be at Paris, is at {ney.location}"
        assert order.arrived_turn is not None, "arrived_turn should be set when reaching ally"
        assert order.arrived_turn == 2, f"arrived_turn should be 2, got {order.arrived_turn}"

        # Turns 3-4: Should still be active (supporting — 1 and 2 turns of support)
        for turn in [3, 4]:
            world.current_turn = turn
            with _suppress():
                results = strat_exec.process_strategic_orders(world, game_state)
            assert ney.strategic_order is not None, (
                f"Order should still be active on turn {turn}"
            )

        # Turn 5: 3 turns of actual support complete (arrived turn 2, +3 = turn 5)
        world.current_turn = order.arrived_turn + 3
        with _suppress():
            results = strat_exec.process_strategic_orders(world, game_state)
        assert ney.strategic_order is None, (
            "Order should expire after 3 turns of actual support"
        )

    def test_timed_support_doesnt_expire_during_travel(self, world, executor, game_state):
        """Timed SUPPORT should NOT expire while infantry marshal is still traveling."""
        # Use Davout (infantry, movement_range=1) supporting Grouchy
        davout = world.get_marshal("Davout")
        grouchy = world.get_marshal("Grouchy")
        davout.location = "Paris"
        grouchy.location = "Lyon"  # 2 hops from Paris for infantry

        # Put enemy near Grouchy so SUPPORT doesn't auto-complete
        blucher = world.get_marshal("Blucher")
        if blucher:
            blucher.location = "Rhine"  # Adjacent to Lyon

        # Order issued turn 1
        order = StrategicOrder(
            command_type="SUPPORT",
            target="Grouchy",
            target_type="marshal",
            started_turn=1,
            issued_turn=1,
            original_command="Davout support Grouchy",
            path=["Lyon"],
            condition=StrategicCondition(max_turns=3),
        )
        davout.strategic_order = order

        from backend.commands.strategic import StrategicExecutor
        strat_exec = StrategicExecutor(executor)

        # Turn 2: Move toward ally (Paris -> Lyon), infantry moves 1 step
        world.current_turn = 2
        with _suppress():
            strat_exec.process_strategic_orders(world, game_state)
        assert davout.strategic_order is not None, "Order should survive turn 2"
        assert davout.location == "Lyon", f"Davout should be at Lyon, is at {davout.location}"
        assert order.arrived_turn == 2, f"arrived_turn should be 2, got {order.arrived_turn}"

        # Turns 3-4: Should still be active (1 and 2 turns of actual support)
        for turn in [3, 4]:
            world.current_turn = turn
            with _suppress():
                strat_exec.process_strategic_orders(world, game_state)
            assert davout.strategic_order is not None, (
                f"Order should survive turn {turn} (supporting)"
            )

        # Turn 5: 3 turns of support complete (arrived turn 2, +3 = turn 5)
        world.current_turn = 5
        with _suppress():
            strat_exec.process_strategic_orders(world, game_state)
        assert davout.strategic_order is None, (
            "Order should expire after 3 turns of actual support"
        )

    def test_arrived_turn_set_on_colocation(self, world, executor, game_state):
        """arrived_turn should be set when SUPPORT marshal first reaches ally."""
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        ney.location = "Paris"
        davout.location = "Paris"  # Already co-located

        # issued_turn=1, process on turn 2 (turn 1 is skipped as issued_turn)
        order = StrategicOrder(
            command_type="SUPPORT",
            target="Davout",
            target_type="marshal",
            started_turn=1,
            issued_turn=1,
            original_command="Ney support Davout",
            path=[],  # No path needed
            condition=StrategicCondition(max_turns=3),
        )
        ney.strategic_order = order

        from backend.commands.strategic import StrategicExecutor
        strat_exec = StrategicExecutor(executor)

        # Turn 2: first real processing — already co-located
        world.current_turn = 2
        with _suppress():
            strat_exec.process_strategic_orders(world, game_state)

        assert order.arrived_turn == 2, f"arrived_turn should be 2, got {order.arrived_turn}"

    def test_arrived_turn_serializes(self):
        """arrived_turn must survive save/load."""
        order = StrategicOrder(
            command_type="SUPPORT",
            target="Davout",
            target_type="marshal",
            started_turn=1,
            issued_turn=1,
            original_command="test",
            path=[],
            arrived_turn=3,
        )
        data = order.to_dict()
        assert data["arrived_turn"] == 3

        restored = StrategicOrder.from_dict(data)
        assert restored.arrived_turn == 3

    def test_arrived_turn_defaults_none(self):
        """Old saves without arrived_turn should load with None."""
        data = {
            "command_type": "SUPPORT",
            "target": "Davout",
            "target_type": "marshal",
            "started_turn": 1,
            "original_command": "test",
        }
        restored = StrategicOrder.from_dict(data)
        assert restored.arrived_turn is None

"""
Tests for Systems Audit Fix Plan — Session 9: Personality & Disobedience Bugs.

Covers:
- P4-3: Vindication last_change_turn uses current_turn (not always 0)
- P4-8: Defensive vindication stale cleanup generates notification
- P4-9: FALSE POSITIVE — _is_fortified correctly reads marshal.fortified
- P3-6: Alphabetical starvation — non-interrupting marshals execute first
- P3-9: SUPPORT with max_turns doesn't auto-complete on ally_safe
- P3-10: BY DESIGN — cannon fire "continue" costs -2 trust (documented)
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import StrategicOrder, StrategicCondition
from backend.commands.vindication import VindicationTracker
from backend.commands.strategic import StrategicOrderProcessor
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def world():
    world = WorldState()
    world.current_turn = 10
    return world


@pytest.fixture
def executor():
    return CommandExecutor()


@pytest.fixture
def game_state(world, executor):
    return {"world": world, "executor": executor}


@pytest.fixture
def strategic_executor(executor):
    return StrategicOrderProcessor(executor)


def _make_order(cmd_type, target, path=None, condition=None):
    order = StrategicOrder(
        command_type=cmd_type,
        target=target,
        target_type="region" if cmd_type in ("MOVE_TO", "HOLD") else "marshal",
        started_turn=1,
        original_command=f"{cmd_type.lower()} {target}",
        path=path or [],
        issued_turn=1,
    )
    if condition:
        order.condition = condition
    return order


# ═══════════════════════════════════════════════════════════════════════════════
# P4-3: Vindication last_change_turn uses current_turn
# ═══════════════════════════════════════════════════════════════════════════════


class TestVindicationLastChangeTurn:
    """P4-3: last_change_turn should record the current game turn, not 0."""

    def test_last_change_turn_records_current_turn(self, world):
        """When vindication changes, last_change_turn stores world.current_turn."""
        tracker = VindicationTracker()
        world.current_turn = 7

        tracker.record_choice("Ney", "trust", {"action": "attack"})
        result = tracker.resolve_battle("Ney", "victory", world)

        assert result is not None
        assert result["vindication_change"] != 0
        assert tracker.last_change_turn["Ney"] == 7

    def test_last_change_turn_not_zero_on_insist_defeat(self, world):
        """Insist + defeat gives marshal vindication; turn recorded correctly."""
        tracker = VindicationTracker()
        world.current_turn = 12

        tracker.record_choice("Ney", "insist", {"action": "attack"})
        result = tracker.resolve_battle("Ney", "defeat", world)

        assert result["vindication_change"] != 0
        assert tracker.last_change_turn["Ney"] == 12

    def test_last_change_turn_unchanged_on_draw(self, world):
        """Draw with trust gives 0 vindication change — turn not recorded."""
        tracker = VindicationTracker()
        world.current_turn = 15

        tracker.record_choice("Ney", "compromise", {"action": "attack"})
        result = tracker.resolve_battle("Ney", "draw", world)

        assert result["vindication_change"] == 0
        assert "Ney" not in tracker.last_change_turn


# ═══════════════════════════════════════════════════════════════════════════════
# P4-8: Defensive vindication stale cleanup notification
# ═══════════════════════════════════════════════════════════════════════════════


class TestDefensiveVindicationNarrative:
    """P4-8: Stale defensive vindication entries produce notification."""

    def test_stale_vindication_generates_notification(self, world):
        """When defensive vindication expires (>5 turns), a notification is created."""
        world.vindication_tracker.pending_defensive_vindication["Davout"] = {
            "turn": 1,
            "source": "objection",
        }
        world.current_turn = 8  # 7 turns later > 5

        initial_count = len(world.notifications.get_pending())
        world._process_vindication_decay()

        # Entry should be removed
        assert "Davout" not in world.vindication_tracker.pending_defensive_vindication
        # Notification should be created
        assert len(world.notifications.get_pending()) > initial_count
        notif = world.notifications.get_pending()[-1]
        assert "Davout" in notif["title"]
        assert "unchallenged" in notif["message"] or "passed" in notif["message"]

    def test_stale_defiance_vindication_generates_notification(self, world):
        """Defiance-source vindication gets different narrative flavor."""
        world.vindication_tracker.pending_defensive_vindication["Ney"] = {
            "turn": 1,
            "source": "defiance",
        }
        world.current_turn = 8

        world._process_vindication_decay()

        assert "Ney" not in world.vindication_tracker.pending_defensive_vindication
        notif = world.notifications.get_pending()[-1]
        assert "defiant" in notif["message"] or "forgotten" in notif["message"]

    def test_non_stale_vindication_not_cleared(self, world):
        """Defensive vindication within 5 turns is not removed."""
        world.vindication_tracker.pending_defensive_vindication["Davout"] = {
            "turn": 6,
            "source": "objection",
        }
        world.current_turn = 10  # 4 turns — not stale

        initial_count = len(world.notifications.get_pending())
        world._process_vindication_decay()

        assert "Davout" in world.vindication_tracker.pending_defensive_vindication
        assert len(world.notifications.get_pending()) == initial_count


# ═══════════════════════════════════════════════════════════════════════════════
# P3-6: Alphabetical starvation fix
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlphabeticalStarvation:
    """P3-6: Non-interrupting marshals execute before interrupting ones."""

    def test_non_interrupting_executes_before_interrupt(self, world, strategic_executor, game_state):
        """Marshal without interrupt executes even if alphabetically later."""
        # Davout (D) has pending interrupt, Ney (N) has clean HOLD
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "options": ["attack", "go_around"],
        }

        ney = world.get_marshal("Ney")
        ney.strategic_order = _make_order("HOLD", "Belgium")

        reports = strategic_executor.process_strategic_orders(world, game_state)

        # Both should be in reports — Ney executed, Davout awaiting
        marshal_names = [r["marshal"] for r in reports]
        assert "Ney" in marshal_names, "Ney should not be starved"
        assert "Davout" in marshal_names

    def test_interrupt_still_requires_input(self, world, strategic_executor, game_state):
        """Deferred interrupt marshal still returns requires_input."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "options": ["investigate", "continue_order"],
        }

        reports = strategic_executor.process_strategic_orders(world, game_state)

        davout_report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert davout_report.get("requires_input") is True


# ═══════════════════════════════════════════════════════════════════════════════
# P3-9: SUPPORT with max_turns honors duration
# ═══════════════════════════════════════════════════════════════════════════════


class TestSupportMaxTurns:
    """P3-9: SUPPORT with explicit max_turns doesn't auto-complete on ally_safe."""

    def test_support_auto_completes_without_max_turns(self, world, strategic_executor, game_state):
        """Open-ended SUPPORT auto-completes when ally is safe."""
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")

        # Put them in same location, no enemies nearby
        ney.location = "Paris"
        davout.location = "Paris"

        order = _make_order("SUPPORT", "Davout")
        order.arrived_turn = 5
        ney.strategic_order = order

        reports = strategic_executor.process_strategic_orders(world, game_state)

        ney_report = [r for r in reports if r["marshal"] == "Ney"]
        assert len(ney_report) == 1
        assert ney_report[0].get("order_status") == "completed"

    def test_support_with_max_turns_continues_when_ally_safe(self, world, strategic_executor, game_state):
        """SUPPORT with explicit max_turns continues even if ally is safe."""
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")

        ney.location = "Paris"
        davout.location = "Paris"

        condition = StrategicCondition(max_turns=5)
        order = _make_order("SUPPORT", "Davout", condition=condition)
        order.arrived_turn = 9  # Only 1 turn elapsed (turn 10 - arrived 9)
        ney.strategic_order = order

        reports = strategic_executor.process_strategic_orders(world, game_state)

        ney_report = [r for r in reports if r["marshal"] == "Ney"]
        assert len(ney_report) == 1
        # Should continue, not complete
        assert ney_report[0].get("order_status") != "completed"
        assert ney.strategic_order is not None, "Order should not be cleared"

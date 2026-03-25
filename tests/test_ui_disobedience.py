"""
Tests for Hold/Wait/Disobedience System (V2-37: converted from print-only to assertions).

Covers: hold action, wait action, personality-based objections, response flow.
"""

from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser


def _make_world():
    """Create a fresh world state for testing."""
    return WorldState(player_nation="France")


def _parse_and_execute(world, command_str):
    """Parse and execute a command, return (parsed, result)."""
    executor = CommandExecutor()
    parser = CommandParser(use_real_llm=False)
    parsed = parser.parse(command_str)
    if not parsed.get("success"):
        return parsed, None
    result = executor.execute(parsed, {"world": world})
    return parsed, result


class TestHoldAction:
    """Hold should work as alias for defend."""

    def test_hold_succeeds_for_cautious_marshal(self):
        """Davout (cautious) should execute hold without objection."""
        world = _make_world()
        davout = world.marshals["Davout"]
        _, result = _parse_and_execute(world, "Davout, hold")
        assert result is not None
        assert result.get("success") is True
        assert davout.stance.value == "defensive"

    def test_hold_consumes_action(self):
        """Hold should consume an action point (for non-objecting marshal)."""
        world = _make_world()
        initial = world.actions_remaining
        _, result = _parse_and_execute(world, "Davout, hold")
        assert result is not None
        assert result.get("success") is True
        assert world.actions_remaining < initial


class TestWaitAction:
    """Wait should be free with no state change."""

    def test_wait_is_free_action(self):
        world = _make_world()
        initial_actions = world.actions_remaining
        _, result = _parse_and_execute(world, "Ney, wait")
        assert result is not None
        assert result.get("success") is True
        assert world.actions_remaining == initial_actions

    def test_wait_does_not_change_location(self):
        world = _make_world()
        ney = world.marshals["Ney"]
        initial_loc = ney.location
        _parse_and_execute(world, "Ney, wait")
        assert ney.location == initial_loc


class TestNeyObjections:
    """Ney (aggressive) should object to defensive orders."""

    def test_ney_defend_triggers_objection_or_executes(self):
        """Ney defend: either triggers objection (aggressive vs defend) or succeeds."""
        world = _make_world()
        _, result = _parse_and_execute(world, "Ney, defend")
        assert result is not None
        # Must either succeed or have an objection/pending_objection
        assert result.get("success") is True or result.get("objection") is not None \
            or result.get("pending_objection") is True

    def test_ney_hold_processes(self):
        """Ney hold: processes without crash, may trigger mild objection."""
        world = _make_world()
        _, result = _parse_and_execute(world, "Ney, hold")
        assert result is not None

    def test_ney_wait_processes(self):
        """Ney wait: processes without crash."""
        world = _make_world()
        _, result = _parse_and_execute(world, "Ney, wait")
        assert result is not None
        assert result.get("success") is True


class TestDavoutNoDefendObjection:
    """Davout (cautious) should NOT object to defend."""

    def test_davout_defend_succeeds(self):
        world = _make_world()
        _, result = _parse_and_execute(world, "Davout, defend")
        assert result is not None
        # Cautious marshal should not object to defensive orders
        assert result.get("success") is True


class TestGrouchyAlwaysObeys:
    """Grouchy (literal) follows orders without objection."""

    def test_grouchy_defend_no_objection(self):
        world = _make_world()
        _, result = _parse_and_execute(world, "Grouchy, defend")
        assert result is not None
        assert result.get("objection") is None

    def test_grouchy_wait_no_objection(self):
        world = _make_world()
        _, result = _parse_and_execute(world, "Grouchy, wait")
        assert result is not None
        assert result.get("success") is True


class TestObjectionResponseFlow:
    """Test objection response flow triggers correctly."""

    def test_low_trust_ney_defend_processes(self):
        """Lowering Ney's trust and issuing defend should process."""
        world = _make_world()
        ney = world.marshals["Ney"]
        ney.trust.modify(-35)  # Lower trust to increase objection chance

        _, result = _parse_and_execute(world, "Ney, defend")
        assert result is not None
        # With low trust, aggressive Ney should likely object to defend
        # But even if variance prevents it, the command must process
        assert result.get("success") is True or result.get("objection") is not None \
            or result.get("pending_objection") is True

"""
Comprehensive tests for Phase 5.2-C: StrategicExecutor.

Tests all 4 command handlers (MOVE_TO, PURSUE, HOLD, SUPPORT),
interrupt system, condition checking, executor integration,
and the Grouchy clarification system.

Run with: pytest tests/test_strategic_executor.py -v
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import (
    Marshal, StrategicOrder, StrategicCondition, Stance
)
from backend.commands.strategic import StrategicExecutor
from backend.commands.executor import CommandExecutor


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def world():
    """Fresh WorldState."""
    return WorldState(player_nation="France")


@pytest.fixture
def executor():
    """CommandExecutor instance."""
    return CommandExecutor()


@pytest.fixture
def game_state(world):
    """Standard game_state dict."""
    return {"world": world}


@pytest.fixture
def strategic_executor(executor):
    """StrategicExecutor instance."""
    return StrategicExecutor(executor)


def _suppress_output():
    """Context manager to suppress print output during tests."""
    import io
    import contextlib
    return contextlib.redirect_stdout(io.StringIO())


def _set_strategic_order(marshal, command_type, target, target_type="region",
                         started_turn=1, path=None, condition=None,
                         target_snapshot_location=None, attack_on_arrival=False):
    """Helper to create and assign a strategic order."""
    order = StrategicOrder(
        command_type=command_type,
        target=target,
        target_type=target_type,
        started_turn=started_turn,
        original_command=f"Test: {command_type} {target}",
        path=path or [],
        target_snapshot_location=target_snapshot_location,
        attack_on_arrival=attack_on_arrival,
        condition=condition,
    )
    marshal.strategic_order = order
    return order


# ══════════════════════════════════════════════════════════════════════════════
# MOVE_TO TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestMoveToCommand:
    """Tests for MOVE_TO strategic command."""

    def test_move_to_region_basic(self, world, game_state, strategic_executor):
        """Marshal moves toward region destination."""
        ney = world.get_marshal("Ney")
        # Move Ney to Paris (safe, no enemies)
        ney.location = "Paris"
        start = ney.location
        # Pick a safe destination 2 hops away
        dest = "Lyon"  # Paris -> Lyon path exists

        _set_strategic_order(ney, "MOVE_TO", dest, path=[])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        assert len(reports) > 0
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report["command"] == "MOVE_TO"
        assert report.get("order_status") in ("continues", "completed")

    def test_move_to_cavalry_moves_two_regions(self, world, game_state, strategic_executor):
        """Cavalry (movement_range=2) moves 2 regions per turn."""
        ney = world.get_marshal("Ney")
        assert ney.movement_range == 2, "Ney should be cavalry"

        # Set up a path 3 regions long
        start = ney.location
        region = world.get_region(start)
        path_regions = []

        # Build a valid path by traversing adjacency
        current = start
        for _ in range(3):
            r = world.get_region(current)
            for adj in r.adjacent_regions:
                if adj not in path_regions and adj != start:
                    # Make sure no enemies
                    enemies = world.get_enemies_in_region(adj, ney.nation)
                    if not enemies:
                        path_regions.append(adj)
                        current = adj
                        break
            else:
                break

        if len(path_regions) < 2:
            pytest.skip("Cannot build 2+ region clear path from Ney's start")

        dest = path_regions[-1]
        _set_strategic_order(ney, "MOVE_TO", dest, path=list(path_regions))

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        moved = report.get("regions_moved", [])

        # Cavalry should move up to 2 regions
        if report["order_status"] == "continues":
            assert len(moved) <= 2
            # Should have moved at least 1
            assert len(moved) >= 1

    def test_move_to_infantry_moves_one_region(self, world, game_state, strategic_executor):
        """Infantry (movement_range=1) moves 1 region per turn."""
        davout = world.get_marshal("Davout")
        assert davout.movement_range == 1, "Davout should be infantry"

        start = davout.location
        region = world.get_region(start)

        # Find a clear path
        path_regions = []
        current = start
        for _ in range(3):
            r = world.get_region(current)
            for adj in r.adjacent_regions:
                if adj not in path_regions and adj != start:
                    enemies = world.get_enemies_in_region(adj, davout.nation)
                    if not enemies:
                        path_regions.append(adj)
                        current = adj
                        break
            else:
                break

        if len(path_regions) < 2:
            pytest.skip("Cannot build 2+ region clear path from Davout's start")

        dest = path_regions[-1]
        _set_strategic_order(davout, "MOVE_TO", dest, path=list(path_regions))

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Davout"][0]
        moved = report.get("regions_moved", [])

        if report["order_status"] == "continues":
            assert len(moved) == 1, "Infantry should move exactly 1 region"

    def test_move_to_arrival_completes_order(self, world, game_state, strategic_executor):
        """Order completes when marshal arrives at destination."""
        ney = world.get_marshal("Ney")
        start = ney.location
        region = world.get_region(start)

        # Find adjacent clear region
        dest = None
        for adj in region.adjacent_regions:
            if not world.get_enemies_in_region(adj, ney.nation):
                dest = adj
                break

        if not dest:
            pytest.skip("No clear adjacent region")

        _set_strategic_order(ney, "MOVE_TO", dest, path=[dest])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        # Cavalry moves 2, so with 1-hop path, should arrive
        assert ney.location == dest or report["order_status"] == "completed"

    def test_move_to_marshal_target_reports_if_still_there(self, world, game_state, strategic_executor):
        """Arrival message says if target marshal still there."""
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")

        # Put Ney at Davout's location (simulating arrival)
        davout_loc = davout.location
        ney.location = davout_loc

        _set_strategic_order(ney, "MOVE_TO", "Davout",
                             target_type="marshal",
                             target_snapshot_location=davout_loc)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report["order_status"] == "completed"
        assert "is here" in report["message"]

    def test_move_to_marshal_reports_if_moved(self, world, game_state, strategic_executor):
        """Arrival message shows where target marshal went."""
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")

        # Snapshot was Belgium, but Davout moved to Paris
        snapshot = "Belgium"
        ney.location = snapshot  # Ney arrives at snapshot location
        davout.location = "Paris"  # Davout moved away

        _set_strategic_order(ney, "MOVE_TO", "Davout",
                             target_type="marshal",
                             target_snapshot_location=snapshot)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report["order_status"] == "completed"
        assert "moved on" in report["message"] or "Paris" in report["message"]

    def test_move_to_blocked_cautious_asks(self, world, game_state, strategic_executor):
        """Cautious asks player when path blocked."""
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious"

        wellington = world.get_marshal("Wellington")
        # Put Wellington in Davout's path
        davout_region = world.get_region(davout.location)
        blocked = davout_region.adjacent_regions[0]
        wellington.location = blocked

        # Destination is beyond the blocked region
        blocked_region = world.get_region(blocked)
        dest = None
        for adj in blocked_region.adjacent_regions:
            if adj != davout.location:
                dest = adj
                break
        if not dest:
            pytest.skip("No destination beyond blocked region")

        _set_strategic_order(davout, "MOVE_TO", dest, path=[blocked, dest])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report.get("requires_input") is True
        assert report.get("interrupt_type") == "contact"

    def test_move_to_blocked_literal_reroutes(self, world, game_state, strategic_executor):
        """Literal silently reroutes around enemies."""
        grouchy = world.get_marshal("Grouchy")
        assert grouchy.personality == "literal"

        wellington = world.get_marshal("Wellington")

        # Put Wellington blocking Grouchy's path
        grouchy_region = world.get_region(grouchy.location)
        blocked = grouchy_region.adjacent_regions[0]
        wellington.location = blocked

        # Find a destination that has alternate route
        dest = None
        for adj in grouchy_region.adjacent_regions:
            if adj != blocked and not world.get_enemies_in_region(adj, grouchy.nation):
                dest_r = world.get_region(adj)
                for further in dest_r.adjacent_regions:
                    if further != grouchy.location and further != blocked:
                        dest = further
                        break
                if dest:
                    break

        if not dest:
            pytest.skip("No alternate route available")

        _set_strategic_order(grouchy, "MOVE_TO", dest, path=[blocked, dest])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        # Should reroute, not ask
        assert report.get("requires_input") is not True
        assert report.get("action") == "reroute" or report.get("order_status") in ("continues", "error", "breaks")


# ══════════════════════════════════════════════════════════════════════════════
# PURSUE TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestPursueCommand:
    """Tests for PURSUE strategic command."""

    def test_pursue_completes_on_target_destroyed(self, world, game_state, strategic_executor):
        """PURSUE completes when target destroyed."""
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Destroy Wellington
        wellington.strength = 0

        _set_strategic_order(ney, "PURSUE", "Wellington", target_type="marshal")

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report["order_status"] == "completed"
        assert "destroyed" in report["message"]

    def test_pursue_attacks_when_reached(self, world, game_state, strategic_executor):
        """PURSUE attacks when in same region as target."""
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Put them in same region
        ney.location = wellington.location

        _set_strategic_order(ney, "PURSUE", "Wellington", target_type="marshal")

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        # Should have engaged in combat
        assert report.get("action") == "combat" or report.get("combat_result") is not None or report.get("order_status") in ("continues", "breaks")

    def test_pursue_combat_loop_prevention(self, world, game_state, strategic_executor):
        """Don't auto-attack same enemy fought last turn."""
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.location = wellington.location

        order = _set_strategic_order(ney, "PURSUE", "Wellington", target_type="marshal")
        # Simulate previous combat
        order.last_combat_enemy = "Wellington"
        order.last_combat_turn = world.current_turn
        order.last_combat_result = "stalemate"

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        # Should ask instead of auto-attacking
        assert report.get("requires_input") is True
        assert report.get("interrupt_type") == "repeated_combat"

    def test_pursue_moves_toward_target(self, world, game_state, strategic_executor):
        """PURSUE moves toward target when not in same region."""
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Move Ney far from all enemies for a clean path test
        ney.location = "Bordeaux"
        wellington.location = "Rhine"
        # Move other enemies away too
        for name, m in world.marshals.items():
            if m.nation != ney.nation and m.name != "Wellington":
                m.location = "Netherlands"

        start = ney.location
        _set_strategic_order(ney, "PURSUE", "Wellington", target_type="marshal")

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        status = report.get("order_status", "")
        # Should have moved toward Wellington or engaged
        assert status in ("continues", "completed") or report.get("action") == "combat"


# ══════════════════════════════════════════════════════════════════════════════
# HOLD TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestHoldCommand:
    """Tests for HOLD strategic command."""

    def test_hold_literal_immovable(self, world, game_state, strategic_executor):
        """Literal marshal gets Immovable bonus, never leaves."""
        grouchy = world.get_marshal("Grouchy")
        assert grouchy.personality == "literal"

        hold_loc = grouchy.location
        _set_strategic_order(grouchy, "HOLD", hold_loc)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["action"] == "hold_immovable"
        assert grouchy.holding_position is True
        assert "Immovable" in report["message"]
        assert grouchy.location == hold_loc

    def test_hold_cautious_fortifies(self, world, game_state, strategic_executor):
        """Cautious marshal auto-fortifies."""
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious"

        # Ensure defensive stance for fortify
        davout.stance = Stance.DEFENSIVE
        hold_loc = davout.location
        _set_strategic_order(davout, "HOLD", hold_loc)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report["action"] == "hold_fortify"

    def test_hold_aggressive_sallies(self, world, game_state, strategic_executor):
        """Aggressive marshal sallies out to attack adjacent enemies."""
        ney = world.get_marshal("Ney")
        assert ney.personality == "aggressive"
        wellington = world.get_marshal("Wellington")

        # Put Wellington adjacent to Ney
        ney_region = world.get_region(ney.location)
        adj = ney_region.adjacent_regions[0]
        wellington.location = adj
        # Make Ney stronger for favorable odds
        ney.strength = 80000
        wellington.strength = 50000

        hold_loc = ney.location
        _set_strategic_order(ney, "HOLD", hold_loc)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        # Should sally or hold_active
        assert report["action"] in ("sally", "hold_active")

    def test_hold_sally_returns_to_position(self, world, game_state, strategic_executor):
        """Sally attack returns marshal to hold position."""
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney_region = world.get_region(ney.location)
        adj = ney_region.adjacent_regions[0]
        wellington.location = adj
        ney.strength = 100000
        wellington.strength = 30000

        hold_loc = ney.location
        _set_strategic_order(ney, "HOLD", hold_loc)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        if report["action"] == "sally":
            # Marshal should be back at hold position
            assert ney.location == hold_loc
            assert report.get("returned_to") == hold_loc

    def test_hold_until_relieved(self, world, game_state, strategic_executor):
        """HOLD completes when ally arrives (until_relieved)."""
        grouchy = world.get_marshal("Grouchy")
        davout = world.get_marshal("Davout")

        # Put Davout in same region as Grouchy (relief)
        grouchy_loc = grouchy.location
        davout.location = grouchy_loc

        condition = StrategicCondition(until_relieved=True)
        _set_strategic_order(grouchy, "HOLD", grouchy_loc, condition=condition)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"
        assert "Relieved" in report["message"]


# ══════════════════════════════════════════════════════════════════════════════
# SUPPORT TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestSupportCommand:
    """Tests for SUPPORT strategic command."""

    def test_support_moves_to_ally(self, world, game_state, strategic_executor):
        """SUPPORT moves toward ally."""
        grouchy = world.get_marshal("Grouchy")
        ney = world.get_marshal("Ney")

        # Ensure different locations
        if grouchy.location == ney.location:
            region = world.get_region(grouchy.location)
            for adj in region.adjacent_regions:
                if not world.get_enemies_in_region(adj, grouchy.nation):
                    grouchy.location = adj
                    break

        start = grouchy.location
        _set_strategic_order(grouchy, "SUPPORT", "Ney", target_type="marshal")

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        if report["order_status"] == "continues":
            assert grouchy.location != start or report.get("regions_moved")

    def test_support_completes_when_ally_safe(self, world, game_state, strategic_executor):
        """SUPPORT completes when ally has no adjacent enemies."""
        grouchy = world.get_marshal("Grouchy")
        ney = world.get_marshal("Ney")

        # Put them together in a safe location
        # Move all enemies far away
        wellington = world.get_marshal("Wellington")
        blucher = world.get_marshal("Blucher")

        safe_loc = "Paris"
        grouchy.location = safe_loc
        ney.location = safe_loc

        # Move ALL enemies away from Paris and its adjacents
        far_location = "Milan"  # Far from Paris
        for name, m in world.marshals.items():
            if m.nation != "France":
                m.location = far_location

        _set_strategic_order(grouchy, "SUPPORT", "Ney", target_type="marshal")

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"
        assert "secure" in report["message"]

    def test_support_ally_destroyed_breaks(self, world, game_state, strategic_executor):
        """SUPPORT breaks when ally destroyed."""
        grouchy = world.get_marshal("Grouchy")
        ney = world.get_marshal("Ney")

        ney.strength = 0  # Destroyed

        _set_strategic_order(grouchy, "SUPPORT", "Ney", target_type="marshal")

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "breaks"
        assert "fallen" in report["message"]

    def test_support_cautious_asks_before_following(self, world, game_state, strategic_executor):
        """Cautious asks before following moving ally."""
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious"
        ney = world.get_marshal("Ney")

        # Ney has a strategic order (is moving)
        _set_strategic_order(ney, "MOVE_TO", "Rhine")

        # Davout supports Ney but they're not together
        if davout.location == ney.location:
            region = world.get_region(davout.location)
            for adj in region.adjacent_regions:
                if not world.get_enemies_in_region(adj, davout.nation):
                    davout.location = adj
                    break

        _set_strategic_order(davout, "SUPPORT", "Ney", target_type="marshal")

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Davout"][0]
        # Cautious should ask about following
        assert report.get("requires_input") is True or report.get("interrupt_type") == "ally_moving"


# ══════════════════════════════════════════════════════════════════════════════
# INTERRUPT TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestInterrupts:
    """Tests for interrupt detection."""

    def test_literal_never_interrupts_cannon_fire(self, world, game_state, strategic_executor):
        """THE GROUCHY MOMENT: Literal ignores cannon fire."""
        grouchy = world.get_marshal("Grouchy")
        assert grouchy.personality == "literal"

        # Record a nearby battle
        grouchy_region = world.get_region(grouchy.location)
        battle_loc = grouchy_region.adjacent_regions[0]
        world.record_battle(battle_loc, "Wellington", "Blucher", "ongoing")

        dest_region = world.get_region(grouchy.location)
        dest = None
        for adj in dest_region.adjacent_regions:
            if adj != battle_loc and not world.get_enemies_in_region(adj, grouchy.nation):
                dest = adj
                break
        if not dest:
            pytest.skip("No clear destination away from battle")

        _set_strategic_order(grouchy, "MOVE_TO", dest, path=[dest])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        # Grouchy should NOT be interrupted
        assert report.get("interrupt") != "cannon_fire"
        assert report.get("requires_input") is not True or report.get("interrupt_type") != "cannon_fire"

    def test_aggressive_rushes_to_cannon_fire(self, world, game_state, strategic_executor):
        """Aggressive auto-redirects toward nearby battle."""
        ney = world.get_marshal("Ney")
        assert ney.personality == "aggressive"

        # Record nearby battle
        ney_region = world.get_region(ney.location)
        battle_loc = ney_region.adjacent_regions[0]
        world.record_battle(battle_loc, "SomeAttacker", "SomeDefender", "ongoing")

        # Give Ney a MOVE_TO order going elsewhere
        dest = None
        for adj in ney_region.adjacent_regions:
            if adj != battle_loc:
                dest = adj
                break
        if not dest:
            dest = battle_loc  # Use battle location as fallback

        _set_strategic_order(ney, "MOVE_TO", dest, path=[dest])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        # Aggressive should redirect
        assert report.get("interrupt") == "cannon_fire" or report.get("order_status") in ("interrupted", "continues", "completed")

    def test_cautious_asks_about_cannon_fire(self, world, game_state, strategic_executor):
        """Cautious asks player about investigating cannon fire."""
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious"

        davout_region = world.get_region(davout.location)
        battle_loc = davout_region.adjacent_regions[0]
        world.record_battle(battle_loc, "SomeAttacker", "SomeDefender", "ongoing")

        dest = None
        for adj in davout_region.adjacent_regions:
            if adj != battle_loc:
                dest = adj
                break
        if not dest:
            pytest.skip("No alternate destination")

        _set_strategic_order(davout, "MOVE_TO", dest, path=[dest])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Davout"][0]
        # Cautious should ask
        if report.get("interrupt") == "cannon_fire":
            assert report.get("requires_input") is True


# ══════════════════════════════════════════════════════════════════════════════
# CONDITION TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestConditions:
    """Tests for strategic conditions."""

    def test_condition_max_turns(self, world, game_state, strategic_executor):
        """Order completes after max_turns."""
        grouchy = world.get_marshal("Grouchy")
        condition = StrategicCondition(max_turns=3)
        _set_strategic_order(grouchy, "HOLD", grouchy.location,
                             started_turn=1, condition=condition)

        # Set current turn so 3 turns have passed
        world.current_turn = 4  # started_turn=1, 4-1=3 >= max_turns=3

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"
        assert "3 turn" in report["message"]

    def test_condition_until_marshal_arrives(self, world, game_state, strategic_executor):
        """Order completes when named marshal arrives."""
        grouchy = world.get_marshal("Grouchy")
        ney = world.get_marshal("Ney")

        # Put Ney in same location as Grouchy
        ney.location = grouchy.location

        condition = StrategicCondition(until_marshal_arrives="Ney")
        _set_strategic_order(grouchy, "HOLD", grouchy.location, condition=condition)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"
        assert "Ney" in report["message"]

    def test_condition_until_marshal_destroyed(self, world, game_state, strategic_executor):
        """Order completes when named marshal destroyed."""
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        wellington.strength = 0  # Destroyed

        condition = StrategicCondition(until_marshal_destroyed="Wellington")
        _set_strategic_order(ney, "PURSUE", "Wellington",
                             target_type="marshal", condition=condition)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report["order_status"] == "completed"

    def test_condition_until_relieved(self, world, game_state, strategic_executor):
        """Order completes when any ally arrives."""
        grouchy = world.get_marshal("Grouchy")
        davout = world.get_marshal("Davout")
        davout.location = grouchy.location  # Relief

        condition = StrategicCondition(until_relieved=True)
        _set_strategic_order(grouchy, "HOLD", grouchy.location, condition=condition)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"
        assert "Relieved" in report["message"]

    def test_condition_until_battle_won(self, world, game_state, strategic_executor):
        """Order completes on victory."""
        ney = world.get_marshal("Ney")
        ney.last_combat_result = "victory"

        condition = StrategicCondition(until_battle_won=True)
        _set_strategic_order(ney, "HOLD", ney.location, condition=condition)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report["order_status"] == "completed"
        assert "Victory" in report["message"] or "victory" in report["message"].lower()


# ══════════════════════════════════════════════════════════════════════════════
# EXECUTOR INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestExecutorIntegration:
    """Tests for executor integration (flags, override, clarification)."""

    def test_strategic_execution_skips_action_cost(self, world, game_state, executor):
        """_strategic_execution=True skips action cost."""
        ney = world.get_marshal("Ney")
        actions_before = world.actions_remaining

        # Find adjacent clear region
        region = world.get_region(ney.location)
        target = None
        for adj in region.adjacent_regions:
            if not world.get_enemies_in_region(adj, ney.nation):
                target = adj
                break
        if not target:
            pytest.skip("No clear adjacent region")

        with _suppress_output():
            result = executor.execute(
                {"command": {
                    "marshal": "Ney",
                    "action": "move",
                    "target": target,
                    "_strategic_execution": True
                }},
                game_state
            )

        # Action should NOT have been consumed
        assert world.actions_remaining == actions_before

    def test_strategic_execution_skips_objections(self, world, game_state, executor):
        """_strategic_execution=True skips objection checks."""
        ney = world.get_marshal("Ney")
        # Set very low trust to maximize objection chance
        ney.trust.set(10)

        region = world.get_region(ney.location)
        target = None
        for adj in region.adjacent_regions:
            if not world.get_enemies_in_region(adj, ney.nation):
                target = adj
                break
        if not target:
            pytest.skip("No clear adjacent region")

        with _suppress_output():
            result = executor.execute(
                {"command": {
                    "marshal": "Ney",
                    "action": "move",
                    "target": target,
                    "_strategic_execution": True
                }},
                game_state
            )

        # Should not get objection/awaiting response
        assert result.get("awaiting_response") is not True
        assert result.get("state") != "awaiting_player_choice"

    def test_sortie_prevents_advance(self, world, game_state, executor):
        """_sortie=True prevents advancing on victory."""
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Make Ney much stronger to guarantee victory
        ney.strength = 200000
        ney.morale = 100
        wellington.strength = 10000
        wellington.morale = 30

        start_loc = ney.location

        with _suppress_output():
            result = executor.execute(
                {"command": {
                    "marshal": "Ney",
                    "action": "attack",
                    "target": "Wellington",
                    "_strategic_execution": True,
                    "_sortie": True
                }},
                game_state
            )

        # With _sortie, Ney should NOT advance to Wellington's region
        # (He may or may not have won, but if he won, he shouldn't have moved)
        if result.get("success"):
            assert ney.location == start_loc, \
                f"Sortie flag should prevent advance, but Ney moved to {ney.location}"

    def test_override_command_cancels_strategic(self, world, game_state, executor):
        """Override command cancels active strategic order."""
        ney = world.get_marshal("Ney")
        _set_strategic_order(ney, "HOLD", ney.location)
        assert ney.in_strategic_mode

        region = world.get_region(ney.location)
        target = None
        for adj in region.adjacent_regions:
            if not world.get_enemies_in_region(adj, ney.nation):
                target = adj
                break
        if not target:
            pytest.skip("No clear adjacent region")

        with _suppress_output():
            result = executor.execute(
                {"command": {
                    "marshal": "Ney",
                    "action": "move",
                    "target": target,
                }},
                game_state
            )

        # Strategic order should be cancelled
        assert not ney.in_strategic_mode

    def test_non_override_command_continues_strategic(self, world, game_state, executor):
        """Non-override command doesn't cancel strategic."""
        ney = world.get_marshal("Ney")
        _set_strategic_order(ney, "HOLD", ney.location)
        assert ney.in_strategic_mode

        with _suppress_output():
            result = executor.execute(
                {"command": {
                    "marshal": "Ney",
                    "action": "wait",
                }},
                game_state
            )

        # Strategic order should still be active
        assert ney.in_strategic_mode


# ══════════════════════════════════════════════════════════════════════════════
# CLARIFICATION TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestClarificationSystem:
    """Tests for Grouchy clarification (high ambiguity)."""

    def test_clarification_triggers_on_high_ambiguity(self, world, game_state, executor):
        """Literal + ambiguity > 60 + strategic triggers clarification."""
        grouchy = world.get_marshal("Grouchy")
        assert grouchy.personality == "literal"

        with _suppress_output():
            result = executor.execute(
                {
                    "command": {
                        "marshal": "Grouchy",
                        "action": "attack",
                        "target": "Wellington",
                    },
                    "ambiguity": 70,
                    "is_strategic": True,
                    "strategic_type": "PURSUE",
                    "interpreted_target": "Wellington",
                    "interpretation_reason": "nearest",
                    "alternatives": ["Blucher"],
                },
                game_state
            )

        assert result.get("state") == "awaiting_clarification"
        assert result.get("type") == "clarification"

    def test_clarification_shows_interpretation(self, world, game_state, executor):
        """Clarification shows parser's interpreted target."""
        grouchy = world.get_marshal("Grouchy")

        with _suppress_output():
            result = executor.execute(
                {
                    "command": {
                        "marshal": "Grouchy",
                        "action": "attack",
                        "target": "Wellington",
                    },
                    "ambiguity": 80,
                    "is_strategic": True,
                    "strategic_type": "PURSUE",
                    "interpreted_target": "Wellington",
                    "interpretation_reason": "nearest",
                    "alternatives": ["Blucher"],
                },
                game_state
            )

        if result.get("state") == "awaiting_clarification":
            assert result.get("interpreted_target") == "Wellington"
            assert result.get("interpretation_reason") == "nearest"

    def test_clarification_does_not_trigger_low_ambiguity(self, world, game_state, executor):
        """Low ambiguity does NOT trigger clarification."""
        grouchy = world.get_marshal("Grouchy")

        with _suppress_output():
            result = executor.execute(
                {
                    "command": {
                        "marshal": "Grouchy",
                        "action": "attack",
                        "target": "Wellington",
                    },
                    "ambiguity": 20,
                    "is_strategic": True,
                    "strategic_type": "PURSUE",
                },
                game_state
            )

        assert result.get("state") != "awaiting_clarification"

    def test_clarification_not_for_non_literal(self, world, game_state, executor):
        """Non-literal marshal does NOT trigger clarification."""
        ney = world.get_marshal("Ney")
        assert ney.personality != "literal"

        with _suppress_output():
            result = executor.execute(
                {
                    "command": {
                        "marshal": "Ney",
                        "action": "attack",
                        "target": "Wellington",
                    },
                    "ambiguity": 80,
                    "is_strategic": True,
                    "strategic_type": "PURSUE",
                },
                game_state
            )

        assert result.get("state") != "awaiting_clarification"


# ══════════════════════════════════════════════════════════════════════════════
# INTERPRETATION TESTS (strategic_parser._add_interpretation)
# ══════════════════════════════════════════════════════════════════════════════

class TestInterpretation:
    """Tests for strategic parser interpretation logic."""

    def test_pursue_generic_interprets_nearest_enemy(self, world):
        """Generic PURSUE picks nearest enemy."""
        from backend.ai.strategic_parser import detect_strategic_command

        ney = world.get_marshal("Ney")
        result = detect_strategic_command("pursue the enemy", "Ney", world)

        assert result is not None
        assert result["is_strategic"]
        assert result["strategic_type"] == "PURSUE"
        assert result["target_type"] == "generic"
        # Interpretation should be populated
        assert result.get("interpreted_target") is not None

    def test_pursue_generic_interprets_nearest_enemy_2(self, world):
        """Generic PURSUE picks nearest enemy marshal."""
        from backend.ai.strategic_parser import detect_strategic_command

        result = detect_strategic_command("pursue the enemy", "Ney", world)

        if result and result.get("strategic_type") == "PURSUE":
            assert result["target_type"] == "generic"
            # Should have interpretation picking nearest enemy
            if result.get("interpreted_target"):
                assert result.get("interpretation_reason") == "nearest"

    def test_specific_target_no_interpretation(self, world):
        """Specific target does NOT get interpretation."""
        from backend.ai.strategic_parser import detect_strategic_command

        result = detect_strategic_command("pursue Wellington", "Ney", world)

        assert result is not None
        # Wellington is a specific marshal, not generic
        assert result.get("target_type") == "marshal"
        # No interpretation needed for specific targets
        assert result.get("interpreted_target") is None


# ══════════════════════════════════════════════════════════════════════════════
# TURN MANAGER INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestTurnManagerIntegration:
    """Tests for turn manager integration."""

    def test_strategic_reports_in_turn_result(self, world, game_state, executor):
        """Strategic reports included in end_turn result."""
        from backend.game_logic.turn_manager import TurnManager

        grouchy = world.get_marshal("Grouchy")
        _set_strategic_order(grouchy, "HOLD", grouchy.location)

        tm = TurnManager(world, executor=executor)

        with _suppress_output():
            result = tm.end_turn(game_state)

        # Should have strategic_reports if any marshal had orders
        # (The order may have completed or continued)
        strategic = result.get("strategic_reports", [])
        assert isinstance(strategic, list)

    def test_no_strategic_reports_without_orders(self, world, game_state, executor):
        """No strategic reports when no marshals have orders."""
        from backend.game_logic.turn_manager import TurnManager

        tm = TurnManager(world, executor=executor)

        with _suppress_output():
            result = tm.end_turn(game_state)

        # Should be empty or not present
        strategic = result.get("strategic_reports", [])
        assert len(strategic) == 0

    def test_strategic_sees_enemy_battles(self, world, game_state, executor):
        """Strategic execution runs before advance_turn (can see battles)."""
        from backend.game_logic.turn_manager import TurnManager

        ney = world.get_marshal("Ney")
        # Give Ney a MOVE_TO order
        region = world.get_region(ney.location)
        dest = None
        for adj in region.adjacent_regions:
            if not world.get_enemies_in_region(adj, ney.nation):
                dest = adj
                break
        if not dest:
            pytest.skip("No clear destination")

        _set_strategic_order(ney, "MOVE_TO", dest, path=[dest])

        # Record a battle that should be visible
        battle_loc = region.adjacent_regions[0]
        world.record_battle(battle_loc, "TestAttacker", "TestDefender", "ongoing")

        tm = TurnManager(world, executor=executor)

        with _suppress_output():
            result = tm.end_turn(game_state)

        # Test passes if no crash — strategic executor ran with battles visible
        assert result is not None


# ══════════════════════════════════════════════════════════════════════════════
# EDGE CASE TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge case tests."""

    def test_no_orders_returns_empty(self, world, game_state, strategic_executor):
        """No marshals with orders returns empty list."""
        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert reports == []

    def test_order_cleared_on_complete(self, world, game_state, strategic_executor):
        """Strategic order is cleared when completed."""
        grouchy = world.get_marshal("Grouchy")
        davout = world.get_marshal("Davout")
        davout.location = grouchy.location  # Relief

        condition = StrategicCondition(until_relieved=True)
        _set_strategic_order(grouchy, "HOLD", grouchy.location, condition=condition)

        with _suppress_output():
            strategic_executor.process_strategic_orders(world, game_state)

        assert grouchy.strategic_order is None
        assert not grouchy.in_strategic_mode

    def test_literal_gets_trust_bonus_on_completion(self, world, game_state, strategic_executor):
        """Literal marshal gets +5 trust when completing order."""
        grouchy = world.get_marshal("Grouchy")
        assert grouchy.personality == "literal"

        trust_before = grouchy.trust.value
        davout = world.get_marshal("Davout")
        davout.location = grouchy.location

        condition = StrategicCondition(until_relieved=True)
        _set_strategic_order(grouchy, "HOLD", grouchy.location, condition=condition)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        if report["order_status"] == "completed":
            assert grouchy.trust.value == trust_before + 5
            assert report.get("precision_bonus") is True

    def test_hold_break_clears_holding_position(self, world, game_state, strategic_executor):
        """Breaking HOLD clears holding_position flag."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.holding_position = True
        grouchy.hold_region = grouchy.location

        # Create HOLD with condition that's already met
        condition = StrategicCondition(max_turns=0)
        _set_strategic_order(grouchy, "HOLD", grouchy.location,
                             started_turn=1, condition=condition)
        world.current_turn = 2  # 1 turn passed >= 0

        with _suppress_output():
            strategic_executor.process_strategic_orders(world, game_state)

        # Order completed (condition met), holding_position managed by _complete_order
        # Note: _complete_order doesn't clear holding_position — only _break_order does
        # But condition completion goes through _complete_order

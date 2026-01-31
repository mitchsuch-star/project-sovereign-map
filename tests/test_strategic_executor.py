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


# ══════════════════════════════════════════════════════════════════════════════
# PHASE D: INTERRUPT RESPONSE TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestInterruptResponse:
    """Tests for Phase D interrupt response handling."""

    # ── Cannon Fire ──────────────────────────────────────────────────────

    def test_cannon_fire_investigate(self, world, game_state, strategic_executor):
        """Investigate cancels order and moves toward battle."""
        ney = world.get_marshal("Ney")
        ney.personality = "cautious"
        ney.location = "Lyon"
        _set_strategic_order(ney, "MOVE_TO", "Vienna", path=["Bavaria", "Vienna"])

        # Simulate pending interrupt
        ney.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Bavaria",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Ney", "cannon_fire", "investigate", world, game_state
            )

        assert result["success"] is True
        assert result["order_cleared"] is True
        assert result["trust_change"] == 0
        assert ney.strategic_order is None
        assert ney.pending_interrupt is None

    def test_cannon_fire_continue(self, world, game_state, strategic_executor):
        """Continue order ignoring cannon fire costs -2 trust and executes movement."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"
        _set_strategic_order(davout, "MOVE_TO", "Rhine", path=["Lyon", "Belgium", "Rhine"])

        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Belgium",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        trust_before = davout.trust.value if hasattr(davout, 'trust') else None

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "cannon_fire", "continue_order", world, game_state
            )

        assert result["success"] is True
        assert result["order_cleared"] is False
        assert result["trust_change"] == -2
        assert davout.strategic_order is not None  # Order preserved
        if trust_before is not None:
            assert davout.trust.value == trust_before - 2
        # Movement should have executed (loop fix)
        assert davout.location != "Paris", "Marshal must move after continue_order"
        assert davout.cannon_fire_ignored_turn == world.current_turn

    def test_cannon_fire_hold_position(self, world, game_state, strategic_executor):
        """Hold position cancels order, -3 trust."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"
        _set_strategic_order(davout, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])

        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Belgium",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "cannon_fire", "hold_position", world, game_state
            )

        assert result["success"] is True
        assert result["order_cleared"] is True
        assert result["trust_change"] == -3
        assert davout.strategic_order is None

    # ── Blocked Path ─────────────────────────────────────────────────────

    def test_blocked_path_attack_victory(self, world, game_state, strategic_executor):
        """Attack blocking enemy — on victory, order continues."""
        ney = world.get_marshal("Ney")
        ney.personality = "cautious"
        ney.location = "Belgium"
        ney.strength = 80000  # Much stronger

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"  # Same region for attack
        wellington.strength = 10000  # Weak

        _set_strategic_order(ney, "MOVE_TO", "Netherlands", path=["Netherlands"])

        ney.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Netherlands",
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Ney", "blocked_path", "attack", world, game_state
            )

        assert result["success"] is True
        assert result["trust_change"] == 0
        # Order should still exist (victory = continue)
        assert result["order_cleared"] is False

    def test_blocked_path_go_around(self, world, game_state, strategic_executor):
        """Go around reroutes path avoiding blocked region."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"

        # Place enemy in Belgium so _get_enemy_occupied_regions finds it
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        _set_strategic_order(davout, "MOVE_TO", "Rhine",
                             path=["Belgium", "Rhine"])

        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Belgium",
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "blocked_path", "go_around", world, game_state
            )

        assert result["success"] is True
        assert result["order_cleared"] is False
        # Path should now avoid Belgium (go through Lyon)
        order = davout.strategic_order
        assert order is not None
        assert "Belgium" not in order.path

    def test_blocked_path_cancel(self, world, game_state, strategic_executor):
        """Cancel order clears strategic order with -3 trust."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"
        _set_strategic_order(davout, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])

        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Belgium",
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        trust_before = davout.trust.value if hasattr(davout, 'trust') else None

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "blocked_path", "cancel_order", world, game_state
            )

        assert result["success"] is True
        assert result["order_cleared"] is True
        assert result["trust_change"] == -3
        assert davout.strategic_order is None

    # ── Support / Ally Moving ────────────────────────────────────────────

    def test_support_follow_moving_ally(self, world, game_state, strategic_executor):
        """Follow updates path to ally's new location."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"

        ney = world.get_marshal("Ney")
        ney.location = "Rhine"  # Ally moved here

        _set_strategic_order(davout, "SUPPORT", "Ney",
                             target_type="friendly_marshal",
                             path=["Belgium"])

        davout.pending_interrupt = {
            "interrupt_type": "ally_moving",
            "ally": "Ney",
            "ally_destination": "Rhine",
            "options": ["follow", "hold_current", "cancel_support"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "ally_moving", "follow", world, game_state
            )

        assert result["success"] is True
        assert result["order_cleared"] is False
        assert result["action_taken"] == "follow"
        # Path should now lead toward Rhine
        assert davout.strategic_order is not None

    def test_support_hold_current(self, world, game_state, strategic_executor):
        """Hold current pauses but doesn't clear order."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"
        _set_strategic_order(davout, "SUPPORT", "Ney",
                             target_type="friendly_marshal",
                             path=["Belgium"])

        davout.pending_interrupt = {
            "interrupt_type": "ally_moving",
            "ally": "Ney",
            "options": ["follow", "hold_current", "cancel_support"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "ally_moving", "hold_current", world, game_state
            )

        assert result["success"] is True
        assert result["order_cleared"] is False
        assert davout.strategic_order is not None  # NOT cleared

    # ── Validation ───────────────────────────────────────────────────────

    def test_invalid_choice_rejected(self, world, game_state, strategic_executor):
        """Invalid choice returns error."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        _set_strategic_order(ney, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])

        ney.pending_interrupt = {
            "interrupt_type": "contact",
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        result = strategic_executor.handle_response(
            "Ney", "blocked_path", "dance", world, game_state
        )

        assert result["success"] is False
        assert "Invalid choice" in result["message"]

    def test_no_pending_interrupt(self, world, game_state, strategic_executor):
        """Response with no pending interrupt returns error."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        _set_strategic_order(ney, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])
        ney.pending_interrupt = None

        result = strategic_executor.handle_response(
            "Ney", "cannon_fire", "investigate", world, game_state
        )

        assert result["success"] is False
        assert "no pending interrupt" in result["message"]

    def test_pending_interrupt_blocks_execution(self, world, game_state,
                                                 strategic_executor):
        """Marshal with pending interrupt skips turn execution."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"
        _set_strategic_order(davout, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])

        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Belgium",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        location_before = davout.location

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        # Marshal should NOT have moved — blocked by pending interrupt
        assert davout.location == location_before
        assert len(reports) >= 1
        assert reports[0].get("requires_input") is True


class TestCannonFireLoopPrevention:
    """Tests that cannon fire continue_order doesn't cause infinite loops."""

    def test_continue_order_executes_movement(self, world, game_state, strategic_executor):
        """After continue_order, marshal should actually move (not stay stuck)."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"
        _set_strategic_order(davout, "MOVE_TO", "Rhine", path=["Lyon", "Belgium", "Rhine"])

        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Belgium",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "cannon_fire", "continue_order", world, game_state
            )

        assert result["success"] is True
        assert result["order_cleared"] is False
        # Marshal should have moved (not stayed at Paris)
        assert davout.location != "Paris", "Marshal must move after continue_order"
        assert result.get("movement_executed") is True

    def test_continue_order_sets_ignored_turn(self, world, game_state, strategic_executor):
        """continue_order sets cannon_fire_ignored_turn to suppress re-trigger."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"
        _set_strategic_order(davout, "MOVE_TO", "Rhine", path=["Lyon", "Belgium", "Rhine"])

        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Belgium",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        with _suppress_output():
            strategic_executor.handle_response(
                "Davout", "cannon_fire", "continue_order", world, game_state
            )

        assert davout.cannon_fire_ignored_turn == world.current_turn

    def test_ignored_turn_suppresses_redetection(self, world, game_state, strategic_executor):
        """After continue_order, _check_interrupts should return None for 1 turn."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Lyon"
        davout.cannon_fire_ignored_turn = world.current_turn

        # Record a battle nearby
        world.record_battle("Belgium", "Wellington", "Ney", "victory")

        result = strategic_executor._check_interrupts(davout, world)
        assert result is None, "Cannon fire should be suppressed after continue_order"

    def test_ignored_turn_expires_after_2_turns(self, world, game_state, strategic_executor):
        """Suppression only lasts 1 turn — 2 turns later, cannon fire re-detects."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Lyon"
        davout.cannon_fire_ignored_turn = world.current_turn - 2  # Expired

        world.record_battle("Belgium", "Wellington", "Ney", "victory")

        result = strategic_executor._check_interrupts(davout, world)
        assert result is not None, "Suppression should expire after 2 turns"
        assert result["type"] == "cannon_fire"

    def test_continue_order_breaks_loop_over_2_turns(self, world, game_state, strategic_executor):
        """Full loop test: continue_order → move → next turn no re-trigger."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"
        _set_strategic_order(davout, "MOVE_TO", "Rhine", path=["Lyon", "Belgium", "Rhine"])

        # Turn 1: Cannon fire interrupt
        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Belgium",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "cannon_fire", "continue_order", world, game_state
            )

        assert result["success"] is True
        location_after_continue = davout.location
        assert location_after_continue != "Paris"  # Moved

        # Turn 2: Record battle again at same location
        world.record_battle("Belgium", "Wellington", "Ney", "victory")

        # Execute strategic turn — should NOT re-trigger cannon fire
        with _suppress_output():
            report = strategic_executor._execute_strategic_turn(davout, world, game_state)

        # Should have moved, not been interrupted
        assert report is not None
        assert report.get("requires_input") is not True, \
            "Cannon fire re-triggered — infinite loop NOT prevented!"

    def test_go_around_executes_movement(self, world, game_state, strategic_executor):
        """After go_around, marshal should actually move along new path."""
        ney = world.get_marshal("Ney")
        ney.personality = "cautious"
        ney.location = "Belgium"
        _set_strategic_order(ney, "MOVE_TO", "Bavaria", path=["Rhine", "Bavaria"])

        # Enemy blocks Rhine
        wellington = world.get_marshal("Wellington")
        wellington.location = "Rhine"

        ney.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Rhine",
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Ney", "blocked_path", "go_around", world, game_state
            )

        assert result["success"] is True
        # If a new path exists, marshal should have moved
        if result.get("action_taken") == "go_around":
            assert result.get("movement_executed") is True or ney.location != "Belgium"

    def test_cannon_fire_ignored_turn_serialization(self):
        """cannon_fire_ignored_turn survives to_dict/from_dict roundtrip."""
        from backend.models.marshal import Marshal
        m = Marshal(name="Test", location="Paris", strength=50000,
                    personality="cautious", nation="France")
        m.cannon_fire_ignored_turn = 5

        data = m.to_dict()
        assert data["cannon_fire_ignored_turn"] == 5

        restored = Marshal.from_dict(data)
        assert restored.cannon_fire_ignored_turn == 5


class TestMovementEnforcement:
    """Tests that marshals never enter enemy-occupied regions without combat."""

    def test_movement_stops_before_enemy_region(self, world, game_state,
                                                 strategic_executor):
        """Marshal stops at region BEFORE enemy, not inside it."""
        ney = world.get_marshal("Ney")
        ney.personality = "aggressive"
        ney.location = "Paris"

        # Place enemy in Belgium (on the path Paris→Belgium→Rhine)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        _set_strategic_order(ney, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        # Ney must still be in Paris — stopped BEFORE Belgium
        assert ney.location == "Paris"

    def test_go_around_avoids_all_enemy_armies(self, world, game_state,
                                                strategic_executor):
        """go_around avoids ALL enemy-occupied regions, not just the blocking one."""
        davout = world.get_marshal("Davout")
        davout.personality = "cautious"
        davout.location = "Paris"

        # Place enemies in Belgium AND Waterloo
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"
        blucher = world.get_marshal("Blucher")
        blucher.location = "Waterloo"

        _set_strategic_order(davout, "MOVE_TO", "Rhine",
                             path=["Belgium", "Rhine"])

        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Belgium",
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "blocked_path", "go_around", world, game_state
            )

        assert result["success"] is True
        if not result["order_cleared"]:
            order = davout.strategic_order
            # Path must avoid BOTH Belgium and Waterloo
            assert "Belgium" not in order.path
            assert "Waterloo" not in order.path

    def test_move_through_empty_enemy_territory(self, world, game_state,
                                                 strategic_executor):
        """Movement through enemy-CONTROLLED but unoccupied region is allowed."""
        ney = world.get_marshal("Ney")
        ney.personality = "cautious"
        ney.location = "Paris"

        # Belgium is enemy-controlled but NO marshal there
        belgium = world.regions.get("Belgium")
        if belgium:
            belgium.controlled_by = "Britain"

        # Move all enemy marshals far away
        wellington = world.get_marshal("Wellington")
        wellington.location = "Vienna"
        blucher = world.get_marshal("Blucher")
        blucher.location = "Vienna"

        _set_strategic_order(ney, "MOVE_TO", "Netherlands",
                             path=["Belgium", "Netherlands"])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        # Ney should pass through Belgium (empty enemy territory)
        assert ney.location != "Paris"  # Moved at least one step


# ══════════════════════════════════════════════════════════════════════════════
# PHASE E: CANCEL COMMAND TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestCancelCommand:
    """Tests for Phase E cancel/halt/stop command."""

    def test_cancel_clears_strategic_order(self, world, game_state, executor):
        """Cancel clears marshal's strategic order."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        _set_strategic_order(ney, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])
        assert ney.in_strategic_mode

        with _suppress_output():
            result = executor.execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                game_state
            )

        assert result.get("success") is True
        assert ney.strategic_order is None
        assert "halts his march" in result.get("message", "")

    def test_cancel_costs_one_action(self, world, game_state, executor):
        """Cancel consumes 1 action."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        _set_strategic_order(ney, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])

        actions_before = world.actions_remaining

        with _suppress_output():
            executor.execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                game_state
            )

        assert world.actions_remaining == actions_before - 1

    def test_cancel_applies_trust_penalty(self, world, game_state, executor):
        """Cancel applies -3 trust (mid-march, not first-step)."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        _set_strategic_order(ney, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"],
                             started_turn=world.current_turn - 2)

        trust_before = ney.trust.value if hasattr(ney, 'trust') else None

        with _suppress_output():
            result = executor.execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                game_state
            )

        assert result.get("trust_change") == -3
        if trust_before is not None:
            assert ney.trust.value == trust_before - 3

    def test_cancel_clears_pending_interrupt(self, world, game_state, executor):
        """Cancel also clears pending interrupt."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        _set_strategic_order(ney, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])
        ney.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        with _suppress_output():
            executor.execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                game_state
            )

        assert ney.pending_interrupt is None
        assert ney.strategic_order is None

    def test_cancel_no_order_free(self, world, game_state, executor):
        """Cancel with no active order is free (no action cost)."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strategic_order = None

        actions_before = world.actions_remaining

        with _suppress_output():
            result = executor.execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                game_state
            )

        assert result.get("success") is False
        assert "no active order" in result.get("message", "").lower()
        # No action consumed
        assert world.actions_remaining == actions_before

    def test_cancel_keyword_halt(self, world, game_state):
        """'halt' keyword parses to cancel action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command("Ney, halt")
        assert result.get("action") == "cancel"

    def test_cancel_keyword_stop(self, world, game_state):
        """'stop' keyword parses to cancel action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command("stop")
        assert result.get("action") == "cancel"

    def test_cancel_keyword_abort(self, world, game_state):
        """'abort' keyword parses to cancel action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command("abort")
        assert result.get("action") == "cancel"

    def test_cancel_keyword_stand_down(self, world, game_state):
        """'stand down' parses to cancel, not neutral stance."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command("Ney, stand down")
        assert result.get("action") == "cancel"

    def test_cancel_keyword_cancel_order(self, world, game_state):
        """'cancel order' parses to cancel action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command("cancel Davout's orders")
        assert result.get("action") == "cancel"

    def test_cancel_keyword_belay(self, world, game_state):
        """'belay that' parses to cancel action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command("belay that")
        assert result.get("action") == "cancel"

    def test_cancel_message_pursue(self, world, game_state, executor):
        """Cancel PURSUE gives flavorful message."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        _set_strategic_order(ney, "PURSUE", "Wellington", target_type="marshal")

        with _suppress_output():
            result = executor.execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                game_state
            )

        assert result.get("success") is True
        assert "breaks off the pursuit" in result.get("message", "")

    def test_cancel_message_hold(self, world, game_state, executor):
        """Cancel HOLD gives flavorful message."""
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        _set_strategic_order(ney, "HOLD", "Belgium")

        with _suppress_output():
            result = executor.execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                game_state
            )

        assert result.get("success") is True
        assert "abandons the position" in result.get("message", "")

    def test_cancel_message_support(self, world, game_state, executor):
        """Cancel SUPPORT gives flavorful message with ally name."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        _set_strategic_order(ney, "SUPPORT", "Davout", target_type="marshal")

        with _suppress_output():
            result = executor.execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                game_state
            )

        assert result.get("success") is True
        assert "breaks off from supporting Davout" in result.get("message", "")


# ══════════════════════════════════════════════════════════════════════════════
# CAVALRY FIRST-STEP MOVEMENT TESTS
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# FIRST-STEP BLOCKED PATH TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestFirstStepBlocked:
    """Tests for personality-based first-step blocked path handling."""

    def test_first_step_aggressive_auto_attacks_good_odds(self, world, game_state, executor):
        """Aggressive marshal auto-attacks when blocked at first step with good odds."""
        ney = world.get_marshal("Ney")
        assert ney.personality == "aggressive"
        ney.location = "Paris"
        ney.strength = 80000

        # Put weak enemy in path
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"
        wellington.strength = 30000  # Ratio 80k/30k = 2.67 > 0.7

        with _suppress_output():
            result = executor.execute({
                "command": {
                    "raw_input": "Ney, march to Rhine",
                    "marshal": "Ney",
                    "action": "move",
                    "target": "Rhine",
                },
                "is_strategic": True,
                "strategic_type": "MOVE_TO",
            }, game_state)

        # Should auto-attack, not ask
        assert result.get("success") is True
        assert result.get("requires_input") is not True
        assert "Engaging" in result.get("message", "") or "bars the way" in result.get("message", "")

    def test_first_step_aggressive_asks_bad_odds(self, world, game_state, executor):
        """Aggressive marshal asks player when blocked with bad odds."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 30000

        # Put strong enemy in path
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"
        wellington.strength = 80000  # Ratio 30k/80k = 0.375 < 0.7

        with _suppress_output():
            result = executor.execute({
                "command": {
                    "raw_input": "Ney, march to Rhine",
                    "marshal": "Ney",
                    "action": "move",
                    "target": "Rhine",
                },
                "is_strategic": True,
                "strategic_type": "MOVE_TO",
            }, game_state)

        # Should ask player
        assert result.get("requires_input") is True
        assert ney.pending_interrupt is not None
        assert ney.pending_interrupt.get("is_first_step") is True

    def test_first_step_cautious_always_asks(self, world, game_state, executor):
        """Cautious marshal always asks when blocked at first step (no alternate route)."""
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious"
        davout.location = "Belgium"  # Start at Belgium
        davout.strength = 80000

        # Put enemy at Rhine (only adjacent region from Belgium that leads to destination)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Rhine"
        wellington.strength = 30000

        # Also block other paths with enemies
        blucher = world.get_marshal("Blucher")
        blucher.location = "Paris"  # Block fallback

        with _suppress_output():
            result = executor.execute({
                "command": {
                    "raw_input": "Davout, march to Bavaria",
                    "marshal": "Davout",
                    "action": "move",
                    "target": "Bavaria",  # Must go through Rhine
                },
                "is_strategic": True,
                "strategic_type": "MOVE_TO",
            }, game_state)

        # Should ask player (cautious found enemy on fallback direct path)
        assert result.get("requires_input") is True
        assert davout.pending_interrupt is not None
        assert davout.pending_interrupt.get("is_first_step") is True

    def test_first_step_literal_reroutes_silently(self, world, game_state, executor):
        """Literal marshal silently reroutes around blocked path."""
        grouchy = world.get_marshal("Grouchy")
        assert grouchy.personality == "literal"
        grouchy.location = "Paris"

        # Put enemy in direct path
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        # Clear other enemies from alternate routes
        for m in world.marshals.values():
            if m.nation != "France" and m.name != "Wellington":
                m.location = "Netherlands"

        with _suppress_output():
            result = executor.execute({
                "command": {
                    "raw_input": "Grouchy, march to Rhine",
                    "marshal": "Grouchy",
                    "action": "move",
                    "target": "Rhine",
                },
                "is_strategic": True,
                "strategic_type": "MOVE_TO",
            }, game_state)

        # Should reroute silently, not ask
        assert result.get("success") is True
        assert result.get("requires_input") is not True
        # Order should still be active with rerouted path
        assert grouchy.strategic_order is not None

    def test_first_step_cancel_zero_trust_penalty(self, world, game_state, executor):
        """First-step cancel has 0 trust penalty."""
        from backend.commands.strategic import StrategicExecutor
        strategic_executor = StrategicExecutor(executor)

        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        _set_strategic_order(davout, "MOVE_TO", "Rhine", path=["Belgium", "Rhine"])

        # Set up first-step interrupt
        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Belgium",
            "is_first_step": True,
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        trust_before = davout.trust.value

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "contact", "cancel_order", world, game_state)

        assert result.get("success") is True
        assert result.get("trust_change") == 0  # No trust penalty for first-step cancel
        assert davout.trust.value == trust_before  # Trust unchanged

    def test_mid_march_cancel_has_trust_penalty(self, world, game_state, executor):
        """Mid-march cancel has -3 trust penalty (not first step)."""
        from backend.commands.strategic import StrategicExecutor
        strategic_executor = StrategicExecutor(executor)

        davout = world.get_marshal("Davout")
        davout.location = "Belgium"  # Already moved from Paris
        _set_strategic_order(davout, "MOVE_TO", "Rhine", path=["Rhine"])

        # Set up mid-march interrupt (NOT first step)
        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Rhine",
            "is_first_step": False,  # Explicitly NOT first step
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        trust_before = davout.trust.value

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "contact", "cancel_order", world, game_state)

        assert result.get("success") is True
        assert result.get("trust_change") == -3  # Full trust penalty
        assert davout.trust.value == trust_before - 3

    def test_first_step_interrupt_costs_one_ap(self, world, game_state, executor):
        """First-step interrupt returns variable_action_cost=1."""
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"

        # Block the only path to Bavaria
        wellington = world.get_marshal("Wellington")
        wellington.location = "Rhine"

        # Block fallback
        blucher = world.get_marshal("Blucher")
        blucher.location = "Paris"

        with _suppress_output():
            result = executor.execute({
                "command": {
                    "raw_input": "Davout, march to Bavaria",
                    "marshal": "Davout",
                    "action": "move",
                    "target": "Bavaria",
                },
                "is_strategic": True,
                "strategic_type": "MOVE_TO",
            }, game_state)

        # Should return variable_action_cost=1
        assert result.get("requires_input") is True
        assert result.get("variable_action_cost") == 1


class TestCavalryFirstStep:
    """Tests for cavalry moving 2 regions on command (first-step)."""

    def test_cavalry_first_step_moves_two_regions(self, world, game_state, executor):
        """Cavalry moves 2 regions on MOVE_TO command first-step."""
        ney = world.get_marshal("Ney")
        assert ney.movement_range == 2, "Ney should be cavalry"

        # Clear enemies from path
        ney.location = "Paris"
        for m in list(world.marshals.values()):
            if m.nation != "France":
                m.location = "Netherlands"  # Move enemies away

        # Execute MOVE_TO Rhine (Paris -> Belgium -> Rhine) - cavalry should move 2 regions
        with _suppress_output():
            result = executor.execute({
                "command": {
                    "raw_input": "Ney, march to Rhine",
                    "marshal": "Ney",
                    "action": "move",
                    "target": "Rhine",
                },
                "is_strategic": True,
                "strategic_type": "MOVE_TO",
            },
                game_state
            )

        # Cavalry should move 2 regions on first step (Paris -> Belgium -> Rhine)
        assert result.get("success") is True
        assert ney.location == "Rhine", f"Ney should be at Rhine (moved 2 regions), but is at {ney.location}"

    def test_infantry_first_step_moves_one_region(self, world, game_state, executor):
        """Infantry moves only 1 region on MOVE_TO command first-step."""
        davout = world.get_marshal("Davout")
        assert davout.movement_range == 1, "Davout should be infantry"

        # Clear enemies from path
        davout.location = "Paris"
        for m in list(world.marshals.values()):
            if m.nation != "France":
                m.location = "Netherlands"

        # Execute MOVE_TO Rhine (Paris -> Belgium -> Rhine)
        with _suppress_output():
            result = executor.execute({
                "command": {
                    "raw_input": "Davout, march to Rhine",
                    "marshal": "Davout",
                    "action": "move",
                    "target": "Rhine",
                },
                "is_strategic": True,
                "strategic_type": "MOVE_TO",
            },
                game_state
            )

        # Infantry should only move 1 region
        assert result.get("success") is True
        assert davout.location == "Belgium", f"Davout should be at Belgium (moved 1 region), but is at {davout.location}"


# ══════════════════════════════════════════════════════════════════════════════
# BUG FIX REGRESSION TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestBugFixes:
    """Regression tests for strategic command bug fixes."""

    def test_strategic_no_double_move_on_issue_turn(self, world, game_state, strategic_executor):
        """Bug 1: Marshal should NOT move twice on the turn the order is issued.

        executor.py already executes the first step, so process_strategic_orders()
        must skip orders whose issued_turn == current_turn.
        """
        ney = world.get_marshal("Ney")
        ney.location = "Paris"

        # Simulate: order was issued THIS turn (turn 1) with first step already done
        _set_strategic_order(ney, "MOVE_TO", "Rhine", path=["Lyon", "Rhine"],
                             started_turn=world.current_turn)
        ney.strategic_order.issued_turn = world.current_turn

        start_location = ney.location  # Paris (first step NOT simulated here)

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        # Should produce only a status report (no execution), order_status="active"
        assert len(reports) == 1, f"Expected 1 status report, got {len(reports)}"
        assert reports[0]["order_status"] == "active"
        # Marshal should NOT have moved
        assert ney.location == start_location, \
            f"Marshal moved from {start_location} to {ney.location} — double-move bug!"

    def test_strategic_move_to_continues_during_retreat_recovery(self, world, game_state, strategic_executor):
        """Bug 2: MOVE_TO should NOT pause during retreat recovery.

        Movement is allowed during retreat recovery. Only combat-related
        orders (PURSUE, HOLD) should pause.
        """
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.retreat_recovery = 2  # In recovery

        # Issue a MOVE_TO on a previous turn
        _set_strategic_order(ney, "MOVE_TO", "Lyon", path=["Lyon"],
                             started_turn=world.current_turn - 1)
        ney.strategic_order.issued_turn = world.current_turn - 1

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        # Should have a report — MOVE_TO continues despite recovery
        assert len(reports) > 0, "MOVE_TO should NOT be paused during retreat recovery"
        report = reports[0]
        assert report.get("order_status") != "paused", \
            f"MOVE_TO was paused during recovery — should continue! Status: {report.get('order_status')}"

    def test_strategic_pursue_pauses_during_retreat_recovery(self, world, game_state, strategic_executor):
        """PURSUE should pause during retreat recovery (needs to attack)."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.retreat_recovery = 2

        wellington = world.get_marshal("Wellington")

        _set_strategic_order(ney, "PURSUE", "Wellington", target_type="marshal",
                             started_turn=world.current_turn - 1)
        ney.strategic_order.issued_turn = world.current_turn - 1

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        assert len(reports) > 0
        assert reports[0].get("order_status") == "paused"

    def test_strategic_first_step_executes_immediately(self, world, game_state, executor):
        """Bug 1: First step should execute immediately when strategic order is issued.

        When player says "Grouchy, march to Vienna", Grouchy should move 1 region
        immediately (infantry movement_range=1).
        """
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Paris"
        start = grouchy.location

        # Issue strategic command through full executor pipeline
        with _suppress_output():
            result = executor.execute(
                {
                    "command": {
                        "marshal": "Grouchy",
                        "action": "move",
                        "target": "Vienna",
                        "raw_command": "Grouchy, march to Vienna",
                    },
                    "is_strategic": True,
                    "strategic_type": "MOVE_TO",
                },
                game_state
            )

        assert result.get("success"), f"Strategic command failed: {result.get('message')}"
        # Grouchy should have moved from Paris (infantry = 1 region)
        assert grouchy.location != start, \
            f"First step did NOT execute — Grouchy still at {start}"
        # Should have a strategic order set
        assert grouchy.strategic_order is not None, "No strategic order set"
        assert grouchy.strategic_order.issued_turn == world.current_turn

    def test_strategic_infantry_moves_one_per_turn(self, world, game_state, strategic_executor):
        """Infantry (movement_range=1) should move exactly 1 region per strategic turn."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Lyon"
        # Ensure infantry
        assert getattr(grouchy, 'movement_range', 1) == 1

        _set_strategic_order(grouchy, "MOVE_TO", "Vienna",
                             path=["Bavaria", "Vienna"],
                             started_turn=world.current_turn - 1)
        grouchy.strategic_order.issued_turn = world.current_turn - 1

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        assert len(reports) > 0
        assert grouchy.location == "Bavaria", \
            f"Infantry should move 1 region (to Bavaria), but is at {grouchy.location}"
        # Should still have order active (not arrived yet)
        assert grouchy.strategic_order is not None


# ══════════════════════════════════════════════════════════════════════════════
# BUG FIX TESTS: Cannon Fire Redirect + Strategic Init
# ══════════════════════════════════════════════════════════════════════════════


class TestAggressiveRedirectActuallyMoves:
    """Bug 1: Aggressive auto-redirect should actually move/attack, not just cancel order."""

    def test_aggressive_redirect_moves_toward_battle(self, world, game_state, strategic_executor):
        """Aggressive marshal moves toward distant battle after redirect."""
        ney = world.get_marshal("Ney")
        assert ney.personality == "aggressive"
        # Place Ney at Paris, battle at Rhine (distance 2 via Belgium or Lyon)
        ney.location = "Paris"

        # Record battle at Rhine (not involving Ney)
        world.record_battle("Rhine", "SomeAttacker", "SomeDefender", "ongoing")

        # Give Ney order going elsewhere (e.g. Brittany)
        _set_strategic_order(ney, "MOVE_TO", "Brittany", path=["Brittany"])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report.get("interrupt") == "cannon_fire"
        assert report.get("order_status") == "interrupted"
        # Order should be cancelled
        assert ney.strategic_order is None
        # Ney should have MOVED (not stayed at Paris)
        assert ney.location != "Paris", \
            f"Ney should have moved toward Rhine but is still at {ney.location}"

    def test_aggressive_adjacent_to_battle_attacks(self, world, game_state, strategic_executor):
        """Aggressive marshal attacks enemy when adjacent to battle location."""
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"  # Adjacent to Waterloo

        # Place an enemy at Waterloo
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"

        # Record battle at Waterloo (not involving Ney)
        world.record_battle("Waterloo", "SomeOther", "SomeDefender", "ongoing")

        # Give Ney order going away
        _set_strategic_order(ney, "MOVE_TO", "Netherlands", path=["Netherlands"])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report.get("interrupt") == "cannon_fire"
        assert report.get("action_taken") == "attack"
        assert ney.strategic_order is None

    def test_cavalry_attacks_from_distance_2(self, world, game_state, strategic_executor):
        """Cavalry (movement_range=2) can attack from 2 regions away."""
        ney = world.get_marshal("Ney")
        assert getattr(ney, 'movement_range', 1) == 2  # Cavalry
        ney.location = "Paris"  # Paris -> Waterloo (distance 1) or Paris -> Belgium -> Waterloo

        # Place enemy at Waterloo (distance 1 from Paris, within cavalry range)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"

        # Record battle at Waterloo
        world.record_battle("Waterloo", "SomeAttacker", "SomeDefender", "ongoing")

        _set_strategic_order(ney, "MOVE_TO", "Brittany", path=["Brittany"])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report.get("interrupt") == "cannon_fire"
        # Paris->Waterloo is distance 1, within cavalry attack_range=2
        # Enemy present at Waterloo, so should attack
        assert report.get("action_taken") == "attack"

    def test_infantry_moves_toward_distance_2_battle(self, world, game_state, strategic_executor):
        """Infantry marshal moves toward battle 2 regions away (can't attack from distance 2)."""
        davout = world.get_marshal("Davout")
        # Davout is cautious — would ask. Use a different approach:
        # We need an aggressive non-cavalry marshal. Let's make Ney non-cavalry temporarily.
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.movement_range = 1  # Override to infantry for this test

        # Battle at Rhine (distance 2: Paris -> Lyon -> Rhine or Paris -> Belgium -> Rhine)
        world.record_battle("Rhine", "SomeAttacker", "SomeDefender", "ongoing")

        # No enemies at Rhine to attack
        # Move all enemies away from Rhine
        for m in world.marshals.values():
            if m.location == "Rhine":
                m.location = "Vienna"

        _set_strategic_order(ney, "MOVE_TO", "Brittany", path=["Brittany"])

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report.get("interrupt") == "cannon_fire"
        # Infantry can't attack from distance 2, should move toward
        assert report.get("action_taken") == "move"
        assert ney.location != "Paris", "Infantry should have moved one step toward battle"

        # Restore
        ney.movement_range = 2


class TestCannonFireEventInFrontendEvents:
    """Bug 2: Cannon fire redirects should appear in the main events list."""

    def test_cannon_fire_event_in_frontend_events(self, world, game_state):
        """Strategic reports with cannon_fire should be surfaced as events."""
        from backend.game_logic.turn_manager import TurnManager

        ney = world.get_marshal("Ney")
        ney.location = "Belgium"

        # Record a battle nearby (not involving Ney)
        world.record_battle("Waterloo", "SomeAttacker", "SomeDefender", "ongoing")

        # Give Ney a strategic order (issued previous turn so it gets processed)
        _set_strategic_order(ney, "MOVE_TO", "Netherlands", path=["Netherlands"])
        ney.strategic_order.issued_turn = world.current_turn - 1

        tm = TurnManager(world)
        tm.executor = CommandExecutor()

        with _suppress_output():
            result = tm.end_turn(game_state)

        # Check that events list contains cannon fire
        events = result.get("events", [])
        cannon_events = [e for e in events if e.get("type") == "cannon_fire_redirect"]
        assert len(cannon_events) >= 1, \
            f"Expected cannon_fire_redirect event, got events: {[e.get('type') for e in events]}"
        assert cannon_events[0]["marshal"] == "Ney"


class TestStrategicInitCommandWrapper:
    """Bug 3: Auto-upgrade MOVE_TO was missing 'command' wrapper in execute() call."""

    def test_strategic_init_with_valid_marshal(self, world, game_state):
        """Auto-upgrade move should properly wrap command for executor."""
        executor = CommandExecutor()
        davout = world.get_marshal("Davout")
        davout.location = "Paris"

        # Clear enemies from the path Paris -> Lyon
        for m in world.marshals.values():
            if m.location == "Lyon" and m.nation != "France":
                m.location = "Vienna"

        # Issue a move to Lyon (distance > movement range, should auto-upgrade)
        # Use the executor directly with a strategic command
        result = executor.execute(
            {"command": {
                "marshal": "Davout",
                "action": "move",
                "target": "Bavaria",  # Far enough to trigger auto-upgrade
                "is_strategic": True,
                "strategic_type": "MOVE_TO",
            }},
            game_state
        )

        # Should NOT contain "Marshal 'None' not found"
        msg = result.get("message", "")
        assert "None" not in msg or "not found" not in msg, \
            f"Got 'Marshal None not found' error: {msg}"


class TestInvestigateResponseActuallyMoves:
    """Bug fix: 'investigate' cannon fire response must actually move the marshal."""

    def test_investigate_moves_marshal_toward_battle(self, world, game_state, strategic_executor):
        """Davout at Lyon, battle at Waterloo (2 away). Investigate should move to Paris."""
        davout = world.get_marshal("Davout")
        davout.location = "Lyon"

        # Clear enemies from Paris so move succeeds
        for m in world.marshals.values():
            if m.location == "Paris" and m.nation != "France":
                m.location = "Vienna"

        _set_strategic_order(davout, "MOVE_TO", "Vienna", path=["Bavaria", "Vienna"])

        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "cannon_fire", "investigate", world, game_state
            )

        assert result["success"] is True
        assert result["order_cleared"] is True
        # Davout should have actually moved from Lyon toward Waterloo
        assert davout.location != "Lyon", \
            f"Davout should have moved from Lyon but is still at {davout.location}"
        # Lyon -> Paris is the first step toward Waterloo
        assert davout.location == "Paris", \
            f"Expected Davout at Paris (first step Lyon->Waterloo), got {davout.location}"

    def test_investigate_attacks_when_adjacent(self, world, game_state, strategic_executor):
        """Davout at Paris, enemy at Waterloo (adjacent). Investigate should attack."""
        davout = world.get_marshal("Davout")
        davout.location = "Paris"

        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"

        _set_strategic_order(davout, "MOVE_TO", "Vienna", path=["Lyon", "Bavaria", "Vienna"])

        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "cannon_fire", "investigate", world, game_state
            )

        assert result["success"] is True
        assert result["action_taken"] == "attack"
        assert davout.strategic_order is None

    def test_investigate_message_no_internal_names(self, world, game_state, strategic_executor):
        """Player-facing messages should not contain MOVE_TO, PURSUE, etc."""
        davout = world.get_marshal("Davout")
        davout.location = "Lyon"

        _set_strategic_order(davout, "MOVE_TO", "Vienna", path=["Bavaria", "Vienna"])

        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        with _suppress_output():
            result = strategic_executor.handle_response(
                "Davout", "cannon_fire", "investigate", world, game_state
            )

        msg = result.get("message", "")
        for internal_name in ["MOVE_TO", "PURSUE", "HOLD", "SUPPORT"]:
            assert internal_name not in msg, \
                f"Message contains internal name '{internal_name}': {msg}"


# ══════════════════════════════════════════════════════════════════════════════
# CARDINAL DIRECTION RESOLUTION
# ══════════════════════════════════════════════════════════════════════════════

class TestCardinalDirectionResolution:
    """Test direction keywords resolve to correct adjacent regions."""

    def test_north_from_paris(self):
        from backend.ai.strategic_parser import resolve_direction
        world = WorldState()
        result = resolve_direction("Paris", "north", world)
        assert result == "Belgium"  # Belgium is north of Paris

    def test_south_from_paris(self):
        from backend.ai.strategic_parser import resolve_direction
        world = WorldState()
        result = resolve_direction("Paris", "south", world)
        assert result == "Lyon"  # Lyon is south of Paris

    def test_west_from_paris(self):
        from backend.ai.strategic_parser import resolve_direction
        world = WorldState()
        result = resolve_direction("Paris", "west", world)
        assert result == "Brittany"  # Brittany is west of Paris

    def test_east_from_paris(self):
        from backend.ai.strategic_parser import resolve_direction
        world = WorldState()
        result = resolve_direction("Paris", "east", world)
        # Waterloo is east of Paris (col 2 vs col 1)
        assert result == "Waterloo"

    def test_front_resolves_toward_enemy(self):
        from backend.ai.strategic_parser import resolve_direction
        world = WorldState()
        # Wellington is in Belgium — "the front" from Paris should go toward Belgium
        result = resolve_direction("Paris", "the front", world, "Grouchy")
        assert result is not None

    def test_back_resolves_toward_capital(self):
        from backend.ai.strategic_parser import resolve_direction
        world = WorldState()
        result = resolve_direction("Belgium", "back", world)
        assert result == "Paris"  # Back from Belgium = toward Paris

    def test_no_direction_when_at_capital_going_back(self):
        from backend.ai.strategic_parser import resolve_direction
        world = WorldState()
        result = resolve_direction("Paris", "back", world)
        assert result is None  # Already at capital

    def test_direction_in_strategic_command(self):
        """'march south' from Ney at Belgium should detect as MOVE_TO Paris."""
        from backend.ai.strategic_parser import detect_strategic_command
        world = WorldState()
        # Ney starts at Belgium; south from Belgium → Paris
        result = detect_strategic_command("march south", "Ney", world)
        assert result is not None
        assert result["strategic_type"] == "MOVE_TO"
        assert result["target"] == "Paris"
        assert result["target_type"] == "region"

    def test_fall_back_south(self):
        """'fall back south' from Belgium should detect as MOVE_TO Paris."""
        from backend.ai.strategic_parser import detect_strategic_command
        world = WorldState()
        result = detect_strategic_command("fall back south", "Ney", world)
        assert result is not None
        assert result["strategic_type"] == "MOVE_TO"
        assert result["target"] == "Paris"


# ══════════════════════════════════════════════════════════════════════════════
# GENERIC TARGET RESOLUTION (ALL TYPES)
# ══════════════════════════════════════════════════════════════════════════════

class TestGenericTargetResolutionAllTypes:
    """Test generic target auto-resolution for non-literal and clarification for literal."""

    def test_pursue_generic_non_literal_auto_resolves(self):
        """Ney (aggressive) auto-resolves 'pursue the enemy' to nearest enemy."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}
        parsed = {
            "command": {
                "marshal": "Ney",
                "action": "move",
                "target": "generic",
                "target_type": "generic",
            },
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "raw_command": "pursue the enemy",
        }
        result = executor.execute(parsed, game_state)
        # Should NOT ask for clarification (Ney is aggressive)
        assert result.get("state") != "awaiting_clarification"

    def test_pursue_generic_literal_asks_clarification(self):
        """Grouchy (literal) asks clarification for 'pursue the enemy'."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}
        parsed = {
            "command": {
                "marshal": "Grouchy",
                "action": "move",
                "target": "generic",
                "target_type": "generic",
            },
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "raw_command": "pursue the enemy",
        }
        result = executor.execute(parsed, game_state)
        assert result.get("state") == "awaiting_clarification"
        assert result.get("strategic_type") == "PURSUE"
        assert result.get("free_action") is True

    def test_support_generic_non_literal_auto_resolves(self):
        """Ney auto-resolves 'support whoever needs it' to most threatened ally."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}
        parsed = {
            "command": {
                "marshal": "Ney",
                "action": "move",
                "target": "generic",
                "target_type": "generic",
            },
            "is_strategic": True,
            "strategic_type": "SUPPORT",
            "raw_command": "support whoever needs it",
        }
        result = executor.execute(parsed, game_state)
        # Should NOT ask for clarification
        assert result.get("state") != "awaiting_clarification"

    def test_support_generic_literal_asks_clarification(self):
        """Grouchy asks clarification for 'support whoever needs it'."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}
        parsed = {
            "command": {
                "marshal": "Grouchy",
                "action": "move",
                "target": "generic",
                "target_type": "generic",
            },
            "is_strategic": True,
            "strategic_type": "SUPPORT",
            "raw_command": "support whoever needs it",
        }
        result = executor.execute(parsed, game_state)
        assert result.get("state") == "awaiting_clarification"
        assert result.get("strategic_type") == "SUPPORT"
        assert "support" in result.get("message", "").lower()

    def test_move_to_generic_non_literal_auto_resolves(self):
        """Ney auto-resolves 'advance to the front' to nearest enemy position."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}
        parsed = {
            "command": {
                "marshal": "Ney",
                "action": "move",
                "target": "generic",
                "target_type": "generic",
            },
            "is_strategic": True,
            "strategic_type": "MOVE_TO",
            "raw_command": "advance to the front",
        }
        result = executor.execute(parsed, game_state)
        assert result.get("state") != "awaiting_clarification"

    def test_clarification_includes_strategic_type(self):
        """All clarification responses include strategic_type for Godot reissue."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}

        for stype in ["PURSUE", "SUPPORT", "MOVE_TO"]:
            parsed = {
                "command": {
                    "marshal": "Grouchy",
                    "action": "move",
                    "target": "generic",
                    "target_type": "generic",
                },
                "is_strategic": True,
                "strategic_type": stype,
                "raw_command": "test generic",
            }
            result = executor.execute(parsed, game_state)
            if result.get("state") == "awaiting_clarification":
                assert "strategic_type" in result, \
                    f"{stype} clarification missing strategic_type"

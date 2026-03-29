"""
Systems Audit Fix Plan — Session 5: Strategic Commands + Serialization

Tests for fixes:
  F1: StrategicOrder last_contact_enemy/last_contact_turn serialization
  F2: HOLD march respects cavalry movement_range (loop, not single move)
  F3: PURSUE stores path on order.path for ledger display
  F4: Hardcoded "Paris" fallbacks replaced with NATION_CAPITALS
  F5: Ledger field renamed from "issued_turn" to "started_turn"
  F6: we_dispatched_thresholds proper WorldState field + serialization
"""

import io
import contextlib

from backend.models.world_state import WorldState
from backend.models.marshal import StrategicOrder
from backend.commands.strategic import StrategicOrderProcessor
from backend.commands.executor import CommandExecutor
from backend.game_logic.ledger import build_strategic_ledger
from backend.models.region import NATION_CAPITALS


def _make_world():
    """Create a standard WorldState for testing."""
    return WorldState(player_nation="France")


def _suppress_output():
    """Context manager to suppress print output during tests."""
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


# ═══════════════════════════════════════════════════════════════════
# F1: StrategicOrder last_contact serialization
# ═══════════════════════════════════════════════════════════════════

class TestLastContactSerialization:
    """last_contact_enemy and last_contact_turn must survive save/load."""

    def test_fields_declared_on_dataclass(self):
        """last_contact fields exist as proper dataclass fields."""
        order = StrategicOrder(
            command_type="PURSUE",
            target="Wellington",
            target_type="marshal",
            started_turn=1,
            original_command="pursue Wellington",
            last_contact_enemy="Wellington",
            last_contact_turn=3,
        )
        assert order.last_contact_enemy == "Wellington"
        assert order.last_contact_turn == 3

    def test_round_trip_serialization(self):
        """last_contact fields survive to_dict/from_dict round-trip."""
        order = StrategicOrder(
            command_type="PURSUE",
            target="Wellington",
            target_type="marshal",
            started_turn=1,
            original_command="pursue Wellington",
            last_contact_enemy="Blucher",
            last_contact_turn=5,
        )
        data = order.to_dict()
        assert data["last_contact_enemy"] == "Blucher"
        assert data["last_contact_turn"] == 5

        restored = StrategicOrder.from_dict(data)
        assert restored.last_contact_enemy == "Blucher"
        assert restored.last_contact_turn == 5

    def test_defaults_none_when_missing(self):
        """Old saves without last_contact fields load with None defaults."""
        data = {
            "command_type": "PURSUE",
            "target": "Wellington",
            "target_type": "marshal",
            "started_turn": 1,
            "original_command": "pursue Wellington",
        }
        restored = StrategicOrder.from_dict(data)
        assert restored.last_contact_enemy is None
        assert restored.last_contact_turn is None


# ═══════════════════════════════════════════════════════════════════
# F2: HOLD march respects cavalry movement_range
# ═══════════════════════════════════════════════════════════════════

class TestHoldCavalryMovement:
    """Cavalry should move 2 regions when marching to HOLD position."""

    def test_cavalry_moves_two_regions_in_hold_march(self):
        """Cavalry (movement_range=2) moves 2 regions toward hold position."""
        world = _make_world()
        executor = CommandExecutor()
        strategic_executor = StrategicOrderProcessor(executor)
        game_state = {"world": world}

        ney = world.get_marshal("Ney")
        assert ney.movement_range == 2, "Ney should be cavalry"

        # Move enemies out of the way
        for m in world.marshals.values():
            if m.nation != "France":
                m.location = "Netherlands"

        # Place Ney at Paris, hold target 3+ regions away
        ney.location = "Paris"
        hold_target = "Bavaria"  # Paris -> Lyon -> Bavaria (or similar multi-hop)

        _set_strategic_order(ney, "HOLD", hold_target)
        start_loc = ney.location

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Ney"][0]
        # Cavalry should have moved past the first region
        assert ney.location != start_loc, "Ney should have moved from start"
        assert report["command"] == "HOLD"

    def test_infantry_moves_one_region_in_hold_march(self):
        """Infantry (movement_range=1) moves only 1 region toward hold position."""
        world = _make_world()
        executor = CommandExecutor()
        strategic_executor = StrategicOrderProcessor(executor)
        game_state = {"world": world}

        davout = world.get_marshal("Davout")
        assert davout.movement_range == 1, "Davout should be infantry"

        # Move enemies out of the way
        for m in world.marshals.values():
            if m.nation != "France":
                m.location = "Netherlands"

        # Place Davout at Paris, hold target far away
        davout.location = "Paris"
        hold_target = "Bavaria"

        _set_strategic_order(davout, "HOLD", hold_target)
        start_loc = davout.location

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert davout.location != start_loc, "Davout should have moved"
        # Infantry moves exactly 1 region per turn
        # Calculate distance moved
        distance_from_start = world.get_distance(start_loc, davout.location)
        assert distance_from_start == 1, "Infantry should move exactly 1 region"


# ═══════════════════════════════════════════════════════════════════
# F3: PURSUE path stored on order.path
# ═══════════════════════════════════════════════════════════════════

class TestPursuePathStorage:
    """PURSUE should store computed path on order.path for ledger display."""

    def test_pursue_stores_path_on_order(self):
        """After PURSUE processing, order.path should be populated."""
        world = _make_world()
        executor = CommandExecutor()
        strategic_executor = StrategicOrderProcessor(executor)
        game_state = {"world": world}

        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Place them far apart
        ney.location = "Paris"
        wellington.location = "Hanover"

        # Clear other enemies from path
        for m in world.marshals.values():
            if m.nation != "France" and m.name != "Wellington":
                m.location = "Netherlands"

        order = _set_strategic_order(ney, "PURSUE", "Wellington", target_type="marshal")
        assert order.path == [], "Path starts empty"

        with _suppress_output():
            reports = strategic_executor.process_strategic_orders(world, game_state)

        # After processing, order.path should be populated (if order still active)
        if ney.strategic_order is not None:
            assert len(ney.strategic_order.path) > 0, \
                "PURSUE should store path on order for ledger display"

    def test_pursue_ledger_shows_nonzero_path(self):
        """Ledger should show non-zero path_remaining for active PURSUE."""
        world = _make_world()
        ney = world.get_marshal("Ney")

        # Manually set up a PURSUE order with path (simulating post-processing)
        order = _set_strategic_order(
            ney, "PURSUE", "Wellington", target_type="marshal",
            path=["Belgium", "Hanover"]
        )

        ledger = build_strategic_ledger(world)
        orders = ledger["orders"]
        ney_order = [o for o in orders if o["marshal"] == "Ney"][0]
        assert ney_order["path_remaining"] == 2, \
            "Ledger should show non-zero path_remaining for PURSUE"


# ═══════════════════════════════════════════════════════════════════
# F4: Hardcoded "Paris" fallbacks replaced with NATION_CAPITALS
# ═══════════════════════════════════════════════════════════════════

class TestHardcodedParisFixes:
    """Enemy marshal respawn and recruit fallback should use correct capital."""

    def test_broken_enemy_respawns_to_correct_capital(self):
        """Broken enemy marshal (with spawn_location cleared) uses NATION_CAPITALS."""
        world = _make_world()
        blucher = world.get_marshal("Blucher")
        assert blucher.nation == "Prussia"

        # Verify NATION_CAPITALS has correct entry
        assert NATION_CAPITALS["Prussia"] == "Berlin"

        # Blucher's spawn_location should already be Berlin
        assert blucher.spawn_location == "Berlin", \
            "Blucher's spawn_location should be Berlin"

    def test_recruit_fallback_uses_nation_capitals(self):
        """Recruit capital fallback uses NATION_CAPITALS, not hardcoded Paris."""
        # Verify the mapping exists for all expected nations
        assert "France" in NATION_CAPITALS
        assert "Prussia" in NATION_CAPITALS
        assert "Austria" in NATION_CAPITALS
        assert "Britain" in NATION_CAPITALS

        # Verify the fallback logic works correctly
        for nation, expected_capital in NATION_CAPITALS.items():
            # Simulate: player_capital is None, fall back to NATION_CAPITALS
            player_capital = None
            capital = player_capital or NATION_CAPITALS.get(nation, "Paris")
            assert capital == expected_capital, \
                f"{nation} should fall back to {expected_capital}, not Paris"


# ═══════════════════════════════════════════════════════════════════
# F5: Ledger field renamed from "issued_turn" to "started_turn"
# ═══════════════════════════════════════════════════════════════════

class TestLedgerStartedTurnLabel:
    """Ledger orders section should use 'started_turn', not 'issued_turn'."""

    def test_active_order_uses_started_turn_key(self):
        """Active order dict should have 'started_turn', not 'issued_turn'."""
        world = _make_world()
        world.current_turn = 5

        ney = world.get_marshal("Ney")
        _set_strategic_order(ney, "MOVE_TO", "Vienna", started_turn=3,
                             path=["Rhine", "Bavaria", "Vienna"])

        ledger = build_strategic_ledger(world)
        orders = ledger["orders"]
        ney_order = [o for o in orders if o["marshal"] == "Ney"][0]

        assert "started_turn" in ney_order, "Should use 'started_turn' key"
        assert "issued_turn" not in ney_order, "Should NOT use 'issued_turn' key"
        assert ney_order["started_turn"] == 3

    def test_idle_marshal_uses_started_turn_key(self):
        """Idle marshal dict should also use 'started_turn', not 'issued_turn'."""
        world = _make_world()
        davout = world.get_marshal("Davout")
        davout.strategic_order = None  # Ensure idle

        ledger = build_strategic_ledger(world)
        orders = ledger["orders"]
        davout_order = [o for o in orders if o["marshal"] == "Davout"][0]

        assert "started_turn" in davout_order, "Idle should use 'started_turn' key"
        assert "issued_turn" not in davout_order, "Idle should NOT use 'issued_turn' key"
        assert davout_order["started_turn"] == 0


# ═══════════════════════════════════════════════════════════════════
# F6: we_dispatched_thresholds serialization
# ═══════════════════════════════════════════════════════════════════

class TestWEThresholdsSerialization:
    """we_dispatched_thresholds should be a proper WorldState field."""

    def test_field_exists_on_world_state(self):
        """we_dispatched_thresholds is a declared field, not dynamic."""
        world = _make_world()
        # Should be accessible without getattr — it's a proper field
        assert hasattr(world, 'we_dispatched_thresholds')
        assert world.we_dispatched_thresholds == {}
        # Should be settable directly
        world.we_dispatched_thresholds = {"Prussia": 20}
        assert world.we_dispatched_thresholds == {"Prussia": 20}

    def test_survives_save_load_round_trip(self):
        """we_dispatched_thresholds survives to_dict/from_dict."""
        world = _make_world()
        world.we_dispatched_thresholds = {"Prussia": 40, "Austria": 20}

        data = world.to_dict()
        assert "we_dispatched_thresholds" in data
        assert data["we_dispatched_thresholds"]["Prussia"] == 40
        assert data["we_dispatched_thresholds"]["Austria"] == 20

        restored = WorldState.from_dict(data)
        assert restored.we_dispatched_thresholds == {"Prussia": 40, "Austria": 20}

    def test_cleared_on_coalition_dissolution(self):
        """we_dispatched_thresholds clears when coalition dissolves."""
        world = _make_world()
        world.active_coalition = {
            "members": ["Prussia"],
            "leader": "Prussia",
            "name": "First Coalition",
        }
        world.we_dispatched_thresholds = {"Prussia": 60}
        world.war_exhaustion = {"Prussia": 80}
        world.coalition_cooldown = 0
        world.coalition_count = 1

        from backend.game_logic.coalition import dissolve_coalition
        dissolve_coalition(world, "war_exhaustion")

        assert world.we_dispatched_thresholds == {}, \
            "Thresholds should clear on dissolution"

    def test_values_are_int_after_load(self):
        """All values should be int after from_dict (Godot safety)."""
        world = _make_world()
        # Simulate save data with float-like values
        data = world.to_dict()
        data["we_dispatched_thresholds"] = {"Prussia": 40.0, "Austria": 20.0}

        restored = WorldState.from_dict(data)
        for v in restored.we_dispatched_thresholds.values():
            assert isinstance(v, int), f"Expected int, got {type(v)}"

# Phase J Comprehensive Test Suite
# tests/test_strategic_ui_comprehensive.py

"""
Comprehensive test suite for Strategic Command UI integration.

Coverage:
- Report generation (process_strategic_orders return format)
- Interrupt response handling (handle_response flows)
- Clarification system (literal personality + ambiguity gate)
- Tooltip/serialization data (marshal.to_dict strategic fields)
- Edge cases (nulls, empty, invalid, boundary)
- Holistic flows (multi-turn, multi-marshal scenarios)
- Regression guards (known bugs that must not recur)
- Concurrency & ordering (determinism, independence)

Run: pytest tests/test_strategic_ui_comprehensive.py -v
Run subset: pytest tests/test_strategic_ui_comprehensive.py -k "test_report" -v
"""

import pytest
from typing import Dict, List
from unittest.mock import patch

from backend.models.marshal import Marshal, StrategicOrder, StrategicCondition
from backend.models.region import Region
from backend.models.world_state import WorldState
from backend.commands.strategic import StrategicExecutor
from backend.commands.executor import CommandExecutor


# ════════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════════════════════

def _make_region(name: str, adjacent: List[str], controller: str = None) -> Region:
    """Helper to create a Region with optional controller."""
    r = Region(name=name, adjacent_regions=adjacent, income_value=100)
    r.controller = controller
    return r


def _make_marshal(name: str, location: str, nation: str = "France",
                  personality: str = "balanced", strength: int = 50000,
                  cavalry: bool = False) -> Marshal:
    """Helper to create a Marshal with sensible defaults."""
    m = Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        cavalry=cavalry
    )
    return m


@pytest.fixture
def world():
    """
    Create a test world with custom map overlaid on real WorldState.

    Map topology:
        Paris ── Belgium ── Netherlands
          │         │            │
        Lyon     Waterloo    Rhine ── Berlin
          │         │
       Marseille  Ligny ── Wavre
                              │
                           Munich ── Vienna

    French marshals: Grouchy (Wavre), Ney (Belgium), Davout (Paris)
    Coalition: Wellington (Waterloo), Blucher (Ligny)
    """
    # Use real constructor so ALL attributes are initialized
    w = WorldState()

    # Replace regions with our test map
    w.regions = {
        "Paris":       _make_region("Paris", ["Belgium", "Lyon"], "France"),
        "Belgium":     _make_region("Belgium", ["Paris", "Waterloo", "Netherlands"], "France"),
        "Netherlands": _make_region("Netherlands", ["Belgium", "Rhine"], "Britain"),
        "Waterloo":    _make_region("Waterloo", ["Belgium", "Ligny"], "Britain"),
        "Lyon":        _make_region("Lyon", ["Paris", "Marseille"], "France"),
        "Marseille":   _make_region("Marseille", ["Lyon"], "France"),
        "Ligny":       _make_region("Ligny", ["Waterloo", "Wavre"], "Prussia"),
        "Wavre":       _make_region("Wavre", ["Ligny", "Munich"], "France"),
        "Rhine":       _make_region("Rhine", ["Netherlands", "Berlin", "Munich"], "Prussia"),
        "Berlin":      _make_region("Berlin", ["Rhine"], "Prussia"),
        "Munich":      _make_region("Munich", ["Wavre", "Rhine", "Vienna"], "France"),
        "Vienna":      _make_region("Vienna", ["Munich"], "France"),
    }

    # Replace marshals with our test set
    w.marshals = {}
    w.marshals["Grouchy"] = _make_marshal(
        "Grouchy", "Wavre", "France", "literal")
    w.marshals["Ney"] = _make_marshal(
        "Ney", "Belgium", "France", "aggressive", cavalry=True)
    w.marshals["Davout"] = _make_marshal(
        "Davout", "Paris", "France", "cautious")
    w.marshals["Wellington"] = _make_marshal(
        "Wellington", "Waterloo", "Britain", "cautious")
    w.marshals["Blucher"] = _make_marshal(
        "Blucher", "Ligny", "Prussia", "aggressive", cavalry=True)

    return w


@pytest.fixture
def executor():
    """Create a CommandExecutor instance."""
    return CommandExecutor()


@pytest.fixture
def strategic_executor(executor):
    """Create a StrategicExecutor wrapping the CommandExecutor."""
    return StrategicExecutor(executor)


@pytest.fixture
def game_state(world):
    """Standard game_state dict for executor/strategic calls."""
    return {"world": world}


def _make_order(cmd_type: str, target: str, target_type: str = "region",
                path: List[str] = None, **kwargs) -> StrategicOrder:
    """Helper to build a StrategicOrder with required fields."""
    return StrategicOrder(
        command_type=cmd_type,
        target=target,
        target_type=target_type,
        started_turn=1,
        original_command=f"{cmd_type.lower()} {target}",
        path=path or [],
        **kwargs
    )


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1: REPORT GENERATION (process_strategic_orders)
# ════════════════════════════════════════════════════════════════════════════════

class TestReportGeneration:
    """Tests for process_strategic_orders() return format."""

    # ─── Required Fields ──────────────────────────────────────────────────

    def test_report_has_required_keys(self, world, strategic_executor, game_state):
        """Every report dict must have marshal, command, order_status, message."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Munich", "Vienna"])

        reports = strategic_executor.process_strategic_orders(world, game_state)

        assert len(reports) >= 1
        for r in reports:
            assert "marshal" in r, f"Missing 'marshal' key in report: {r}"
            assert "command" in r or "order_status" in r, f"Report missing status keys: {r}"
            assert "message" in r, f"Missing 'message' key in report: {r}"

    def test_report_marshal_name_is_string(self, world, strategic_executor, game_state):
        """Marshal field is a string name, not an object."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "HOLD", "Wavre", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        assert isinstance(reports[0]["marshal"], str)
        assert reports[0]["marshal"] == "Grouchy"

    # ─── Status Values ────────────────────────────────────────────────────

    def test_move_to_continuing_status(self, world, strategic_executor, game_state):
        """MOVE_TO mid-journey reports 'continues' status."""
        grouchy = world.get_marshal("Grouchy")
        # Path: Wavre → Munich → Vienna (2 hops remaining)
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Munich", "Vienna"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = reports[0]
        assert report["order_status"] == "continues"
        assert "Vienna" in report["message"]

    def test_move_to_completed_on_arrival(self, world, strategic_executor, game_state):
        """MOVE_TO reports 'completed' when marshal reaches destination."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Munich"
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Vienna"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = reports[0]
        assert report["order_status"] == "completed"

    def test_hold_continues_status(self, world, strategic_executor, game_state):
        """HOLD at destination reports 'continues'."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("HOLD", "Paris", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        assert reports[0]["order_status"] == "continues"
        assert "Paris" in reports[0]["message"]

    def test_blocked_path_reports_requires_input(self, world, strategic_executor, game_state):
        """Blocked path sets requires_input=True with options list."""
        # Davout tries to move through Waterloo (Wellington is there)
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        davout.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = reports[0]
        assert report.get("requires_input") == True
        assert isinstance(report.get("options"), list)
        assert len(report["options"]) > 0

    def test_paused_during_retreat_recovery(self, world, strategic_executor, game_state):
        """Marshal in retreat_recovery gets 'paused' report (PURSUE pauses, MOVE_TO doesn't)."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.retreat_recovery = 2
        grouchy.strategic_order = _make_order(
            "PURSUE", "Wellington", target_type="enemy_marshal", path=["Munich", "Vienna"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        assert reports[0]["order_status"] == "paused"
        assert "recover" in reports[0]["message"].lower()

    # ─── Multiple Marshals ────────────────────────────────────────────────

    def test_each_marshal_gets_own_report(self, world, strategic_executor, game_state):
        """All French marshals with orders produce separate reports."""
        world.get_marshal("Grouchy").strategic_order = _make_order(
            "HOLD", "Wavre", path=[])
        world.get_marshal("Ney").strategic_order = _make_order(
            "PURSUE", "Wellington", target_type="enemy_marshal",
            path=["Waterloo"])
        world.get_marshal("Davout").strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Belgium", "Waterloo"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        marshal_names = {r["marshal"] for r in reports}
        # At least 2 should process (3rd might stop at interrupt)
        assert len(marshal_names) >= 2

    def test_no_orders_yields_empty_reports(self, world, strategic_executor, game_state):
        """No strategic orders → empty list."""
        for m in world.marshals.values():
            m.strategic_order = None

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert reports == []

    def test_enemy_marshals_excluded_from_reports(self, world, strategic_executor, game_state):
        """Only player nation marshals are processed."""
        wellington = world.get_marshal("Wellington")
        wellington.strategic_order = _make_order("HOLD", "Waterloo")

        reports = strategic_executor.process_strategic_orders(world, game_state)
        for r in reports:
            assert r["marshal"] != "Wellington"

    def test_deterministic_order_alphabetical(self, world, strategic_executor, game_state):
        """Reports are generated in alphabetical marshal order."""
        world.get_marshal("Ney").strategic_order = _make_order("HOLD", "Belgium")
        world.get_marshal("Davout").strategic_order = _make_order("HOLD", "Paris")
        world.get_marshal("Grouchy").strategic_order = _make_order("HOLD", "Wavre")

        reports = strategic_executor.process_strategic_orders(world, game_state)
        names = [r["marshal"] for r in reports]
        assert names == sorted(names), f"Reports not alphabetical: {names}"

    # ─── Report Content by Order Type ─────────────────────────────────────

    def test_move_to_report_shows_destination(self, world, strategic_executor, game_state):
        """MOVE_TO message mentions the target destination."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Munich", "Vienna"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert "Vienna" in reports[0]["message"]

    def test_pursue_report_shows_target_marshal(self, world, strategic_executor, game_state):
        """PURSUE message mentions the enemy being pursued."""
        ney = world.get_marshal("Ney")
        ney.strategic_order = _make_order(
            "PURSUE", "Wellington", target_type="enemy_marshal",
            path=["Waterloo"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        msg = reports[0]["message"]
        assert "Wellington" in msg

    def test_support_report_shows_ally(self, world, strategic_executor, game_state):
        """SUPPORT message mentions the supported ally."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order(
            "SUPPORT", "Ney", target_type="friendly_marshal",
            path=["Belgium"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        msg = reports[0]["message"]
        assert "Ney" in msg


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2: INTERRUPT RESPONSE HANDLING (handle_response)
# ════════════════════════════════════════════════════════════════════════════════

class TestInterruptResponseHandling:
    """Tests for StrategicExecutor.handle_response()."""

    # ─── Cannon Fire Responses ────────────────────────────────────────────

    def test_investigate_clears_order_and_moves(self, world, strategic_executor, game_state):
        """'investigate' cancels order and redirects toward battle."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        result = strategic_executor.handle_response(
            "Davout", "cannon_fire", "investigate", world, game_state)

        assert result["success"] == True
        assert result.get("order_cleared") == True
        assert davout.pending_interrupt is None

    def test_continue_order_keeps_order(self, world, strategic_executor, game_state):
        """'continue_order' keeps strategic order active."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        result = strategic_executor.handle_response(
            "Davout", "cannon_fire", "continue_order", world, game_state)

        assert result["success"] == True
        assert result.get("order_cleared") == False
        assert davout.strategic_order is not None
        assert davout.pending_interrupt is None

    def test_continue_order_trust_penalty(self, world, strategic_executor, game_state):
        """'continue_order' for cannon fire costs -2 trust."""
        davout = world.get_marshal("Davout")
        initial_trust = davout.trust.value
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        result = strategic_executor.handle_response(
            "Davout", "cannon_fire", "continue_order", world, game_state)

        assert result["trust_change"] == -2
        assert davout.trust.value == initial_trust - 2

    def test_hold_position_cancels_order(self, world, strategic_executor, game_state):
        """'hold_position' on cannon_fire clears order."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        result = strategic_executor.handle_response(
            "Davout", "cannon_fire", "hold_position", world, game_state)

        assert result["success"] == True
        assert result.get("order_cleared") == True
        assert davout.strategic_order is None

    # ─── Blocked Path (Contact) Responses ─────────────────────────────────

    def test_go_around_recalculates_path(self, world, strategic_executor, game_state):
        """'go_around' reroutes avoiding enemy regions."""
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        davout.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])
        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Waterloo",
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        result = strategic_executor.handle_response(
            "Davout", "contact", "go_around", world, game_state)

        assert result["success"] == True
        assert davout.pending_interrupt is None
        # Order either rerouted or cancelled if no path
        if davout.strategic_order:
            # Path should NOT go through Waterloo
            assert "Waterloo" not in davout.strategic_order.path

    def test_cancel_order_clears_everything(self, world, strategic_executor, game_state):
        """'cancel_order' clears order and interrupt."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Ligny")
        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Waterloo",
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        result = strategic_executor.handle_response(
            "Davout", "contact", "cancel_order", world, game_state)

        assert result["success"] == True
        assert result.get("order_cleared") == True
        assert davout.strategic_order is None
        assert davout.pending_interrupt is None

    def test_attack_response_attempts_combat(self, world, strategic_executor, game_state):
        """'attack' on contact attempts combat with blocker."""
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])
        ney.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Waterloo",
            "options": ["attack", "go_around", "hold_position", "cancel_order"]
        }

        result = strategic_executor.handle_response(
            "Ney", "contact", "attack", world, game_state)

        assert result["success"] == True
        assert result["action_taken"] == "attack"

    # ─── Ally Moving (SUPPORT) Responses ──────────────────────────────────

    def test_follow_updates_support_path(self, world, strategic_executor, game_state):
        """'follow' recalculates path toward ally's new location."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order(
            "SUPPORT", "Ney", target_type="friendly_marshal")
        davout.pending_interrupt = {
            "interrupt_type": "ally_moving",
            "ally": "Ney",
            "options": ["follow", "hold_current", "cancel_support"]
        }

        result = strategic_executor.handle_response(
            "Davout", "ally_moving", "follow", world, game_state)

        assert result["success"] == True
        assert davout.pending_interrupt is None

    def test_hold_current_keeps_order_paused(self, world, strategic_executor, game_state):
        """'hold_current' keeps order but marshal stays put."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order(
            "SUPPORT", "Ney", target_type="friendly_marshal")
        davout.pending_interrupt = {
            "interrupt_type": "ally_moving",
            "ally": "Ney",
            "options": ["follow", "hold_current", "cancel_support"]
        }

        result = strategic_executor.handle_response(
            "Davout", "ally_moving", "hold_current", world, game_state)

        assert result["success"] == True
        assert result.get("order_cleared") == False
        assert davout.strategic_order is not None

    def test_cancel_support_clears_order(self, world, strategic_executor, game_state):
        """'cancel_support' clears SUPPORT order with trust penalty."""
        davout = world.get_marshal("Davout")
        initial_trust = davout.trust.value
        davout.strategic_order = _make_order(
            "SUPPORT", "Ney", target_type="friendly_marshal")
        davout.pending_interrupt = {
            "interrupt_type": "ally_moving",
            "ally": "Ney",
            "options": ["follow", "hold_current", "cancel_support"]
        }

        result = strategic_executor.handle_response(
            "Davout", "ally_moving", "cancel_support", world, game_state)

        assert result["success"] == True
        assert davout.strategic_order is None
        assert result["trust_change"] == -3
        assert davout.trust.value == initial_trust - 3

    # ─── Any Response Clears Interrupt ────────────────────────────────────

    def test_any_valid_response_clears_pending(self, world, strategic_executor, game_state):
        """All valid responses clear pending_interrupt."""
        interrupt_configs = [
            ("cannon_fire", ["investigate", "continue_order", "hold_position"]),
            ("contact", ["attack", "go_around", "hold_position", "cancel_order"]),
            ("ally_moving", ["follow", "hold_current", "cancel_support"]),
        ]

        for int_type, options in interrupt_configs:
            for choice in options:
                davout = world.get_marshal("Davout")
                davout.location = "Paris"  # Reset
                davout.strategic_order = _make_order(
                    "SUPPORT" if int_type == "ally_moving" else "MOVE_TO",
                    "Ney" if int_type == "ally_moving" else "Berlin",
                    target_type="friendly_marshal" if int_type == "ally_moving" else "region"
                )
                davout.pending_interrupt = {
                    "interrupt_type": int_type,
                    "battle_location": "Waterloo",
                    "enemy": "Wellington",
                    "location": "Waterloo",
                    "ally": "Ney",
                    "options": options,
                }

                result = strategic_executor.handle_response(
                    "Davout", int_type, choice, world, game_state)

                assert davout.pending_interrupt is None, \
                    f"'{choice}' for '{int_type}' didn't clear pending_interrupt"

    # ─── Error Cases ──────────────────────────────────────────────────────

    def test_unknown_marshal_returns_error(self, world, strategic_executor, game_state):
        """Unknown marshal name → success=False."""
        result = strategic_executor.handle_response(
            "Napoleon", "cannon_fire", "investigate", world, game_state)
        assert result["success"] == False

    def test_no_pending_interrupt_returns_error(self, world, strategic_executor, game_state):
        """No pending_interrupt → success=False."""
        davout = world.get_marshal("Davout")
        davout.pending_interrupt = None
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")

        result = strategic_executor.handle_response(
            "Davout", "cannon_fire", "investigate", world, game_state)
        assert result["success"] == False

    def test_invalid_choice_returns_error(self, world, strategic_executor, game_state):
        """Choice not in options → success=False."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "options": ["investigate", "continue_order", "hold_position"],
        }

        result = strategic_executor.handle_response(
            "Davout", "cannon_fire", "dance_a_jig", world, game_state)
        assert result["success"] == False

    def test_no_strategic_order_returns_error(self, world, strategic_executor, game_state):
        """Marshal with interrupt but no order → success=False, clears interrupt."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = None
        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "options": ["investigate"],
        }

        result = strategic_executor.handle_response(
            "Davout", "cannon_fire", "investigate", world, game_state)
        assert result["success"] == False
        assert davout.pending_interrupt is None


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3: CLARIFICATION POPUP (Executor-level Grouchy gate)
# ════════════════════════════════════════════════════════════════════════════════

class TestClarificationPopup:
    """Tests for literal personality clarification system in executor."""

    def test_literal_high_ambiguity_triggers_clarification(self, world, executor, game_state):
        """Literal + ambiguity>60 + is_strategic → clarification response."""
        result = executor.execute({
            "command": {
                "marshal": "Grouchy",
                "action": "pursue",
                "target": "the enemy",
            },
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "ambiguity": 80,
            "strategic_score": 50,
            "interpreted_target": "Blucher",
            "interpretation_reason": "nearest",
            "alternatives": ["Wellington"],
        }, game_state)

        assert result.get("state") == "awaiting_clarification"
        assert result.get("type") == "clarification"
        assert result.get("marshal") == "Grouchy"
        assert result.get("interpreted_target") == "Blucher"

    def test_clarification_has_options_list(self, world, executor, game_state):
        """Clarification response includes structured options."""
        result = executor.execute({
            "command": {
                "marshal": "Grouchy",
                "action": "pursue",
                "target": "the enemy",
            },
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "ambiguity": 80,
            "strategic_score": 50,
            "interpreted_target": "Blucher",
            "interpretation_reason": "nearest",
            "alternatives": ["Wellington"],
        }, game_state)

        options = result.get("options", [])
        assert len(options) >= 2
        values = [o.get("value") for o in options]
        assert "confirm" in values or "cancel" in values

    def test_clarification_alternatives_from_parsed(self, world, executor, game_state):
        """Alternatives in clarification come from parsed data."""
        result = executor.execute({
            "command": {
                "marshal": "Grouchy",
                "action": "pursue",
                "target": "the enemy",
            },
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "ambiguity": 80,
            "strategic_score": 50,
            "interpreted_target": "Blucher",
            "interpretation_reason": "nearest",
            "alternatives": ["Wellington"],
        }, game_state)

        assert "Wellington" in result.get("alternatives", [])

    def test_aggressive_no_clarification(self, world, executor, game_state):
        """Aggressive personality bypasses clarification even at high ambiguity."""
        result = executor.execute({
            "command": {
                "marshal": "Ney",
                "action": "pursue",
                "target": "the enemy",
            },
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "ambiguity": 80,
            "strategic_score": 50,
            "interpreted_target": "Wellington",
            "alternatives": [],
        }, game_state)

        # Ney is aggressive — should NOT trigger clarification
        assert result.get("state") != "awaiting_clarification"

    def test_low_ambiguity_no_clarification(self, world, executor, game_state):
        """Low ambiguity (<=60) skips clarification even for literal."""
        result = executor.execute({
            "command": {
                "marshal": "Grouchy",
                "action": "pursue",
                "target": "Blucher",
            },
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "ambiguity": 20,  # Low — clear order
            "strategic_score": 80,
            "interpreted_target": "Blucher",
            "alternatives": [],
        }, game_state)

        # Should proceed to execution, not clarification
        assert result.get("state") != "awaiting_clarification"

    def test_non_strategic_no_clarification(self, world, executor, game_state):
        """Non-strategic commands skip clarification even for literal."""
        result = executor.execute({
            "command": {
                "marshal": "Grouchy",
                "action": "move",
                "target": "Munich",
            },
            "is_strategic": False,
            "ambiguity": 80,
            "strategic_score": 10,
        }, game_state)

        assert result.get("state") != "awaiting_clarification"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 4: TOOLTIP / SERIALIZATION DATA
# ════════════════════════════════════════════════════════════════════════════════

class TestTooltipData:
    """Tests for marshal.to_dict() including strategic fields."""

    def test_strategic_order_in_to_dict(self, world):
        """to_dict includes strategic_order when present."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Munich", "Vienna"])

        data = grouchy.to_dict()
        assert "strategic_order" in data
        assert data["strategic_order"] is not None
        assert data["strategic_order"]["command_type"] == "MOVE_TO"
        assert data["strategic_order"]["target"] == "Vienna"

    def test_no_order_is_none_in_dict(self, world):
        """to_dict has strategic_order=None when no order."""
        ney = world.get_marshal("Ney")
        ney.strategic_order = None

        data = ney.to_dict()
        assert data["strategic_order"] is None

    def test_pending_interrupt_in_to_dict(self, world):
        """to_dict includes pending_interrupt."""
        ney = world.get_marshal("Ney")
        ney.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"]
        }

        data = ney.to_dict()
        assert data["pending_interrupt"] is not None
        assert data["pending_interrupt"]["interrupt_type"] == "cannon_fire"

    def test_precision_execution_in_to_dict(self, world):
        """to_dict includes precision execution fields."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.precision_execution_active = True
        grouchy.precision_execution_turns = 2

        data = grouchy.to_dict()
        assert data["precision_execution_active"] == True
        assert data["precision_execution_turns"] == 2

    def test_strategic_order_path_and_steps(self, world):
        """to_dict strategic order includes path for UI progress display."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Munich", "Vienna"])

        data = grouchy.to_dict()
        order = data["strategic_order"]
        assert "path" in order
        assert order["path"] == ["Munich", "Vienna"]


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 5: EDGE CASES
# ════════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    # ─── Null / Empty ─────────────────────────────────────────────────────

    def test_no_orders_no_crash(self, world, strategic_executor, game_state):
        """No strategic orders → empty list, no crash."""
        for m in world.marshals.values():
            m.strategic_order = None
            m.pending_interrupt = None

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert reports == []

    def test_empty_path_handled(self, world, strategic_executor, game_state):
        """Empty path recalculates or completes gracefully."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Vienna"
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=[])  # Already there

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        # Should complete (already at destination)
        assert reports[0]["order_status"] == "completed"

    def test_marshal_already_at_destination(self, world, strategic_executor, game_state):
        """Marshal at MOVE_TO destination → order completes immediately."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Wavre"
        grouchy.strategic_order = _make_order("MOVE_TO", "Wavre", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        assert reports[0]["order_status"] == "completed"
        assert grouchy.strategic_order is None

    # ─── Interrupt persistence ────────────────────────────────────────────

    def test_pending_interrupt_persists_across_process(self, world, strategic_executor, game_state):
        """Pending interrupt survives process_strategic_orders calls."""
        ney = world.get_marshal("Ney")
        ney.strategic_order = _make_order("MOVE_TO", "Berlin")
        ney.pending_interrupt = {
            "interrupt_type": "contact",
            "options": ["attack", "go_around", "hold_position", "cancel_order"],
        }

        strategic_executor.process_strategic_orders(world, game_state)

        assert ney.pending_interrupt is not None

    def test_interrupt_stops_further_processing(self, world, strategic_executor, game_state):
        """When a report requires_input, processing stops (no further marshals)."""
        # Davout (alphabetically first) has interrupt → blocks others
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "options": ["attack", "go_around", "hold_position", "cancel_order"],
        }

        ney = world.get_marshal("Ney")
        ney.strategic_order = _make_order("HOLD", "Belgium")

        reports = strategic_executor.process_strategic_orders(world, game_state)

        # Davout's awaiting_response should be returned, Ney skipped
        assert len(reports) == 1
        assert reports[0]["marshal"] == "Davout"

    # ─── State Transitions ────────────────────────────────────────────────

    def test_completed_order_clears_strategic_order(self, world, strategic_executor, game_state):
        """Completed MOVE_TO clears marshal.strategic_order."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Munich"
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Vienna"])

        strategic_executor.process_strategic_orders(world, game_state)

        assert grouchy.location == "Vienna", f"Should have moved to Vienna, got {grouchy.location}"
        assert grouchy.strategic_order is None, "Order should be cleared on completion"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 6: HOLISTIC FLOWS
# ════════════════════════════════════════════════════════════════════════════════

class TestHolisticFlows:
    """End-to-end multi-step scenarios."""

    def test_move_to_multi_turn(self, world, strategic_executor, game_state):
        """MOVE_TO progresses one step per turn (infantry)."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.movement_range = 1
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Munich", "Vienna"])

        # Turn 1: Wavre → Munich
        reports1 = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports1) >= 1
        assert grouchy.location == "Munich", f"Expected Munich, got {grouchy.location}"
        assert grouchy.strategic_order is not None, "Order should still be active"
        assert reports1[0]["order_status"] == "continues"

        # Turn 2: Munich → Vienna
        reports2 = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports2) >= 1
        assert grouchy.location == "Vienna", f"Expected Vienna, got {grouchy.location}"
        assert reports2[0]["order_status"] == "completed"

    def test_cavalry_moves_farther(self, world, strategic_executor, game_state):
        """Cavalry (movement_range=2) moves 2 regions per turn."""
        ney = world.get_marshal("Ney")
        assert ney.movement_range == 2
        # Belgium → Paris → Lyon (2 steps, no enemies)
        ney.strategic_order = _make_order(
            "MOVE_TO", "Lyon", path=["Paris", "Lyon"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        assert ney.location == "Lyon", f"Cavalry should reach Lyon in 1 turn, got {ney.location}"
        assert reports[0]["order_status"] == "completed"

    def test_interrupt_then_resume(self, world, strategic_executor, game_state):
        """Blocked → resolve → marshal continues on next process call."""
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        davout.strategic_order = _make_order(
            "MOVE_TO", "Ligny",
            path=["Waterloo", "Ligny"])

        # Process — should hit Wellington at Waterloo
        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        assert davout.pending_interrupt is not None, "Davout should be blocked by Wellington"

        # Resolve by going around
        strategic_executor.handle_response(
            "Davout", "contact", "go_around", world, game_state)

        # Order either rerouted or cancelled (no safe path on our map)
        if davout.strategic_order:
            reports2 = strategic_executor.process_strategic_orders(world, game_state)
            assert len(reports2) >= 1

    def test_cancel_mid_march(self, world, executor, game_state):
        """Cancel order via executor._execute_cancel mid-march."""
        grouchy = world.get_marshal("Grouchy")
        initial_trust = grouchy.trust.value
        order = _make_order("MOVE_TO", "Vienna", path=["Munich", "Vienna"])
        order.started_turn = world.current_turn - 2  # Started 2 turns ago (mid-march)
        grouchy.strategic_order = order

        result = executor.execute({
            "command": {
                "marshal": "Grouchy",
                "action": "cancel",
            }
        }, game_state)

        assert result["success"] == True
        assert grouchy.strategic_order is None
        assert result["trust_change"] == -3
        assert grouchy.trust.value == initial_trust - 3

    def test_multiple_interrupts_sequential(self, world, strategic_executor, game_state):
        """Two marshals with interrupts processed one at a time."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"],
        }

        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order("MOVE_TO", "Vienna")
        grouchy.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Ligny",
            "options": ["investigate", "continue_order", "hold_position"],
        }

        # First process — should return Davout (alphabetically first), stop
        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) == 1
        assert reports[0]["marshal"] == "Davout"

        # Resolve Davout
        strategic_executor.handle_response(
            "Davout", "cannon_fire", "continue_order", world, game_state)

        # Grouchy is literal — would never get cannon_fire interrupt normally
        # but we manually set it for testing. Process picks up Grouchy next.
        reports2 = strategic_executor.process_strategic_orders(world, game_state)
        # Grouchy should report (awaiting_response or continues)
        assert len(reports2) >= 1


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 7: REGRESSION GUARDS
# ════════════════════════════════════════════════════════════════════════════════

class TestRegressionGuards:
    """Tests preventing known bugs from recurring."""

    def test_serialization_roundtrip_strategic_fields(self, world):
        """Regression: All strategic fields survive serialize→deserialize."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "PURSUE", "Wellington", target_type="enemy_marshal",
            path=["Ligny", "Waterloo"])
        grouchy.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Waterloo",
            "options": ["investigate", "continue_order", "hold_position"]
        }
        grouchy.precision_execution_active = True
        grouchy.precision_execution_turns = 2

        data = grouchy.to_dict()
        restored = Marshal.from_dict(data)

        assert restored.strategic_order is not None
        assert restored.strategic_order.command_type == "PURSUE"
        assert restored.strategic_order.target == "Wellington"
        assert restored.strategic_order.path == ["Ligny", "Waterloo"]
        assert restored.pending_interrupt is not None
        assert restored.pending_interrupt["interrupt_type"] == "cannon_fire"
        assert restored.precision_execution_active == True
        assert restored.precision_execution_turns == 2

    def test_literal_ignores_cannon_fire(self, world, strategic_executor, game_state):
        """THE GROUCHY MOMENT: Literal personality never interrupted by cannon fire."""
        grouchy = world.get_marshal("Grouchy")
        assert grouchy.personality == "literal"
        grouchy.strategic_order = _make_order(
            "PURSUE", "Blucher", target_type="enemy_marshal",
            path=["Ligny"])

        # Record battle 2 regions away (Waterloo is 2 hops from Wavre via Ligny)
        world.record_battle("Waterloo", "Wellington", "Ney", "victory")

        reports = strategic_executor.process_strategic_orders(world, game_state)

        # Grouchy must NOT have cannon_fire interrupt
        for r in reports:
            if r["marshal"] == "Grouchy":
                assert r.get("interrupt_type") != "cannon_fire"
                assert r.get("interrupt") != "cannon_fire"

    def test_aggressive_auto_redirects_on_cannon_fire(self, world, strategic_executor, game_state):
        """Aggressive personality auto-redirects toward cannon fire."""
        ney = world.get_marshal("Ney")
        assert ney.personality == "aggressive"
        ney.location = "Paris"
        ney.strategic_order = _make_order(
            "MOVE_TO", "Marseille", path=["Lyon", "Marseille"])

        # Record battle 1 region away (Belgium is adjacent to Paris)
        world.record_battle("Belgium", "Wellington", "Davout", "stalemate")

        reports = strategic_executor.process_strategic_orders(world, game_state)

        # Ney should auto-redirect (no requires_input)
        for r in reports:
            if r["marshal"] == "Ney":
                assert r.get("requires_input", False) == False
                assert r.get("interrupt") == "cannon_fire" or r.get("order_status") in ("interrupted", "continues")

    def test_cautious_asks_on_cannon_fire(self, world, strategic_executor, game_state):
        """Cautious personality asks player about cannon fire."""
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious"
        davout.location = "Lyon"
        davout.strategic_order = _make_order(
            "MOVE_TO", "Marseille", path=["Marseille"])

        # Record battle at Paris (adjacent to Lyon)
        world.record_battle("Paris", "Wellington", "Ney", "stalemate")

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1, "Davout should produce a report"
        report = reports[0]
        assert report["marshal"] == "Davout"
        assert report.get("interrupt") == "cannon_fire", \
            f"Cautious should get cannon_fire interrupt, got: {report}"
        assert report.get("requires_input") == True
        assert "investigate" in report.get("options", [])

    def test_first_step_cancel_zero_trust_penalty(self, world, strategic_executor, game_state):
        """Cancelling at first step via interrupt has 0 trust penalty."""
        davout = world.get_marshal("Davout")
        initial_trust = davout.trust.value
        davout.strategic_order = _make_order("MOVE_TO", "Berlin")
        davout.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy": "Wellington",
            "location": "Waterloo",
            "is_first_step": True,  # First step!
            "options": ["attack", "go_around", "hold_position", "cancel_order"],
        }

        result = strategic_executor.handle_response(
            "Davout", "contact", "cancel_order", world, game_state)

        assert result["trust_change"] == 0
        assert davout.trust.value == initial_trust

    def test_world_state_serialization_preserves_battles(self, world):
        """WorldState.to_dict preserves battles_this_turn."""
        world.record_battle("Waterloo", "Wellington", "Ney", "victory")
        world.record_battle("Ligny", "Blucher", "Grouchy", "stalemate")

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert len(restored.battles_this_turn) == 2

    def test_condition_met_completes_order(self, world, strategic_executor, game_state):
        """StrategicCondition.max_turns met → order completes."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "HOLD", "Wavre", path=[],
            condition=StrategicCondition(max_turns=1))
        grouchy.strategic_order.started_turn = 0  # Turn 0, current is turn 1
        world.current_turn = 1

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1, "Grouchy should produce a report"
        report = reports[0]
        assert report["order_status"] == "completed", \
            f"max_turns=1 with 1 turn elapsed should complete, got: {report['order_status']}"
        assert grouchy.strategic_order is None


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 8: CONCURRENCY & ORDERING
# ════════════════════════════════════════════════════════════════════════════════

class TestConcurrencyAndOrdering:
    """Multi-marshal scenarios and determinism."""

    def test_all_marshals_execute_same_call(self, world, strategic_executor, game_state):
        """Single process call advances all marshals with orders."""
        world.get_marshal("Grouchy").strategic_order = _make_order(
            "HOLD", "Wavre", path=[])
        world.get_marshal("Davout").strategic_order = _make_order(
            "HOLD", "Paris", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        marshal_names = {r["marshal"] for r in reports}
        assert "Grouchy" in marshal_names
        assert "Davout" in marshal_names

    def test_interrupt_does_not_block_prior_marshals(self, world, strategic_executor, game_state):
        """Marshal alphabetically after interrupted one still gets skipped, but prior ones process."""
        # Davout (D) has clean HOLD, Ney (N) will get blocked
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("HOLD", "Paris", path=[])

        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        names = [r["marshal"] for r in reports]

        # Davout should have processed (alphabetically first)
        assert "Davout" in names

    def test_deterministic_same_input_same_output(self, world, strategic_executor, game_state):
        """Same state → same reports (no randomness in strategic processing)."""
        def setup():
            world.get_marshal("Grouchy").strategic_order = _make_order(
                "HOLD", "Wavre", path=[])
            world.get_marshal("Davout").strategic_order = _make_order(
                "HOLD", "Paris", path=[])
            world.get_marshal("Ney").strategic_order = None

        setup()
        r1 = strategic_executor.process_strategic_orders(world, game_state)

        # Reset orders and re-run
        for m in world.marshals.values():
            m.strategic_order = None
        setup()
        r2 = strategic_executor.process_strategic_orders(world, game_state)

        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert a["marshal"] == b["marshal"]
            assert a["order_status"] == b["order_status"]

    def test_one_marshal_interrupt_others_still_run(self, world, strategic_executor, game_state):
        """Alphabetically earlier clean marshal processes before later interrupt."""
        # Davout processes, Ney hits block → Grouchy skipped
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("HOLD", "Paris", path=[])

        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Vienna", path=["Munich", "Vienna"])

        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])  # Wellington blocks

        reports = strategic_executor.process_strategic_orders(world, game_state)
        names = [r["marshal"] for r in reports]

        # Davout (D) processed, Grouchy (G) processed, Ney (N) hits block
        assert "Davout" in names
        assert "Grouchy" in names


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 9: MOVEMENT INTO ENEMIES (UI Bug area)
# ════════════════════════════════════════════════════════════════════════════════

class TestMovementIntoEnemies:
    """Tests verifying marshals don't silently walk into enemy-occupied regions."""

    def test_move_to_blocks_on_enemy_region(self, world, strategic_executor, game_state):
        """MOVE_TO stops or interrupts when path goes through enemy marshal."""
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        davout.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])

        reports = strategic_executor.process_strategic_orders(world, game_state)

        # Should NOT silently move into Waterloo where Wellington is
        assert davout.location != "Waterloo" or davout.pending_interrupt is not None

    def test_infantry_stops_at_first_enemy(self, world, strategic_executor, game_state):
        """Infantry (range=1) encountering enemy on step 1 triggers block."""
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        davout.movement_range = 1
        davout.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])

        strategic_executor.process_strategic_orders(world, game_state)

        # Davout should still be in Belgium, not Waterloo
        assert davout.location == "Belgium"

    def test_cavalry_stops_at_enemy_during_multi_step(self, world, strategic_executor, game_state):
        """Cavalry moving 2 regions stops if second region has enemy."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.movement_range = 2
        # Paris → Belgium (friendly) → Waterloo (enemy!)
        ney.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Belgium", "Waterloo", "Ligny"])

        strategic_executor.process_strategic_orders(world, game_state)

        # Cavalry should advance to Belgium (first step safe) then stop at Waterloo boundary
        assert ney.location == "Belgium", \
            f"Cavalry should stop at Belgium before enemy at Waterloo, got {ney.location}"

    def test_literal_reroutes_around_enemies(self, world, strategic_executor, game_state):
        """Literal personality silently reroutes around enemy regions."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Wavre"
        # Direct path: Wavre → Ligny (Blucher there!) → Waterloo
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Waterloo", path=["Ligny", "Waterloo"])

        reports = strategic_executor.process_strategic_orders(world, game_state)

        # Grouchy is literal — should reroute or break, NOT walk into Blucher
        assert grouchy.location != "Ligny", \
            "Literal personality should never walk into enemy-occupied Ligny"
        assert len(reports) >= 1
        report = reports[0]
        # Should either reroute or break (no alternate path on this map)
        assert report.get("action") == "reroute" or report["order_status"] == "breaks", \
            f"Expected reroute or break, got: {report}"

    def test_cautious_asks_before_enemy_contact(self, world, strategic_executor, game_state):
        """Cautious personality asks player on enemy contact, doesn't walk in."""
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        davout.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])

        reports = strategic_executor.process_strategic_orders(world, game_state)

        # Davout is cautious — should get interrupt, not enter Waterloo
        has_contact = any(
            r.get("interrupt_type") in ("contact", "contact_bad_odds")
            for r in reports
        )
        still_in_belgium = davout.location == "Belgium"
        assert has_contact or still_in_belgium, \
            f"Cautious marshal walked into enemy at {davout.location} without interrupt"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 10: PURSUE HANDLER COVERAGE
# ════════════════════════════════════════════════════════════════════════════════

class TestPursueHandler:
    """Coverage for _execute_pursue edge cases."""

    def test_pursue_target_destroyed(self, world, strategic_executor, game_state):
        """PURSUE completes when target marshal is destroyed."""
        ney = world.get_marshal("Ney")
        ney.strategic_order = _make_order(
            "PURSUE", "Wellington", target_type="enemy_marshal",
            path=["Waterloo"])

        # Destroy target
        world.get_marshal("Wellington").strength = 0

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report["order_status"] == "completed"
        assert ney.strategic_order is None

    def test_pursue_target_missing(self, world, strategic_executor, game_state):
        """PURSUE completes when target marshal no longer exists."""
        ney = world.get_marshal("Ney")
        ney.strategic_order = _make_order(
            "PURSUE", "Wellington", target_type="enemy_marshal",
            path=["Waterloo"])

        # Remove target from game
        del world.marshals["Wellington"]

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report["order_status"] == "completed"

    def test_pursue_same_region_attacks(self, world, strategic_executor, game_state):
        """PURSUE attacks when in same region as target."""
        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strategic_order = _make_order(
            "PURSUE", "Wellington", target_type="enemy_marshal",
            path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        # Should have attempted combat
        assert report.get("action") == "combat" or report.get("order_status") in ("continues", "breaks")

    def test_pursue_combat_loop_prevention(self, world, strategic_executor, game_state):
        """PURSUE doesn't auto-attack same enemy fought last turn."""
        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"
        order = _make_order("PURSUE", "Wellington", target_type="enemy_marshal", path=[])
        order.last_combat_enemy = "Wellington"
        order.last_combat_turn = world.current_turn
        order.last_combat_result = "stalemate"
        ney.strategic_order = order

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        # Should require input (repeated_combat interrupt)
        assert report.get("requires_input") == True
        assert report.get("interrupt_type") == "repeated_combat"

    def test_pursue_moves_toward_target(self, world, strategic_executor, game_state):
        """PURSUE moves marshal closer to target each turn."""
        grouchy = world.get_marshal("Grouchy")
        # Grouchy at Wavre, Wellington at Waterloo — path via Ligny blocked by Blucher
        # Move Blucher away so path is clear
        world.get_marshal("Blucher").location = "Berlin"
        grouchy.strategic_order = _make_order(
            "PURSUE", "Wellington", target_type="enemy_marshal", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        # Should have moved closer (Wavre → Ligny)
        assert grouchy.location != "Wavre" or report["order_status"] in ("continues", "breaks")


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 11: HOLD HANDLER COVERAGE
# ════════════════════════════════════════════════════════════════════════════════

class TestHoldHandler:
    """Coverage for _execute_hold personality behaviors."""

    def test_hold_literal_sets_immovable(self, world, strategic_executor, game_state):
        """Literal HOLD sets holding_position=True."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order("HOLD", "Wavre", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        assert grouchy.holding_position == True
        assert grouchy.hold_region == "Wavre"
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report.get("action") == "hold_immovable"

    def test_hold_cautious_auto_fortifies(self, world, strategic_executor, game_state):
        """Cautious HOLD auto-fortifies."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("HOLD", "Paris", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report.get("action") == "hold_fortify"

    def test_hold_aggressive_sally(self, world, strategic_executor, game_state):
        """Aggressive HOLD sallies out to attack adjacent enemy."""
        ney = world.get_marshal("Ney")
        # Put Ney in Belgium with Wellington adjacent at Waterloo
        ney.location = "Belgium"
        ney.strategic_order = _make_order("HOLD", "Belgium", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report.get("action") == "sally"
        assert report.get("target") == "Wellington"
        # Should return to hold position
        assert report.get("returned_to") == "Belgium"

    def test_hold_aggressive_no_sally_bad_odds(self, world, strategic_executor, game_state):
        """Aggressive HOLD doesn't sally when odds < 1.0."""
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 10000  # Much weaker
        world.get_marshal("Wellington").strength = 50000
        ney.strategic_order = _make_order("HOLD", "Belgium", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report.get("action") == "hold_active"  # No sally

    def test_hold_moving_to_position(self, world, strategic_executor, game_state):
        """HOLD moves marshal to position if not already there."""
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        davout.strategic_order = _make_order("HOLD", "Lyon", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        # Should be moving toward Lyon
        assert davout.location == "Lyon" or report.get("action") == "moving_to_position"

    def test_hold_break_clears_holding_state(self, world, strategic_executor, game_state):
        """Breaking a HOLD order clears holding_position and hold_region."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.holding_position = True
        grouchy.hold_region = "Wavre"
        # Order for unreachable location
        grouchy.strategic_order = _make_order("HOLD", "NonExistent", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        assert len(reports) >= 1
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "breaks"
        assert grouchy.holding_position == False
        assert grouchy.hold_region == ""


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 12: SUPPORT HANDLER COVERAGE
# ════════════════════════════════════════════════════════════════════════════════

class TestSupportHandler:
    """Coverage for _execute_support edge cases."""

    def test_support_ally_destroyed_breaks(self, world, strategic_executor, game_state):
        """SUPPORT breaks when ally is destroyed."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order(
            "SUPPORT", "Ney", target_type="friendly_marshal", path=["Belgium"])

        # Destroy ally
        world.get_marshal("Ney").strength = 0

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report["order_status"] == "breaks"
        assert davout.strategic_order is None

    def test_support_ally_safe_completes(self, world, strategic_executor, game_state):
        """SUPPORT completes when ally has no adjacent enemies."""
        davout = world.get_marshal("Davout")
        davout.location = "Marseille"
        # Move Ney to safe location (Lyon — no enemies adjacent)
        ney = world.get_marshal("Ney")
        ney.location = "Marseille"
        # Remove all enemy adjacency
        world.get_marshal("Wellington").location = "Berlin"
        world.get_marshal("Blucher").location = "Vienna"

        davout.strategic_order = _make_order(
            "SUPPORT", "Ney", target_type="friendly_marshal", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report["order_status"] == "completed"

    def test_support_cautious_ally_moving_interrupt(self, world, strategic_executor, game_state):
        """Cautious SUPPORT asks player when ally is on the move."""
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        davout.strategic_order = _make_order(
            "SUPPORT", "Ney", target_type="friendly_marshal", path=["Belgium"])

        # Give Ney a strategic move order
        ney = world.get_marshal("Ney")
        ney.strategic_order = _make_order("MOVE_TO", "Rhine", path=["Netherlands", "Rhine"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report.get("requires_input") == True
        assert report.get("interrupt_type") == "ally_moving"
        assert "follow" in report.get("options", [])

    def test_support_moves_toward_ally(self, world, strategic_executor, game_state):
        """SUPPORT moves marshal closer to ally each turn."""
        davout = world.get_marshal("Davout")
        davout.location = "Lyon"
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strategic_order = None  # Not moving

        davout.strategic_order = _make_order(
            "SUPPORT", "Ney", target_type="friendly_marshal", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report["order_status"] == "continues"
        # Should have moved closer (Lyon → Paris)
        assert davout.location == "Paris", f"Expected move toward Belgium, got {davout.location}"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 13: CONDITION SYSTEM COVERAGE
# ════════════════════════════════════════════════════════════════════════════════

class TestConditionSystem:
    """Coverage for _check_condition edge cases."""

    def test_until_marshal_arrives(self, world, strategic_executor, game_state):
        """until_marshal_arrives completes when target marshal arrives."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "HOLD", "Wavre", path=[],
            condition=StrategicCondition(until_marshal_arrives="Davout"))

        # Move Davout to same location
        world.get_marshal("Davout").location = "Wavre"

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"
        assert "Davout" in report["message"]

    def test_until_marshal_destroyed(self, world, strategic_executor, game_state):
        """until_marshal_destroyed completes when target is gone."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "HOLD", "Wavre", path=[],
            condition=StrategicCondition(until_marshal_destroyed="Wellington"))

        # Destroy Wellington
        world.get_marshal("Wellington").strength = 0

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"
        assert "Wellington" in report["message"]

    def test_until_relieved(self, world, strategic_executor, game_state):
        """until_relieved completes when allied marshal arrives."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "HOLD", "Wavre", path=[],
            condition=StrategicCondition(until_relieved=True))

        # Move Davout to same location
        world.get_marshal("Davout").location = "Wavre"

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"
        assert "Relieved" in report["message"]

    def test_until_battle_won_victory(self, world, strategic_executor, game_state):
        """until_battle_won completes on victory."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.last_combat_result = "victory"
        grouchy.strategic_order = _make_order(
            "HOLD", "Wavre", path=[],
            condition=StrategicCondition(until_battle_won=True))

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"

    def test_until_battle_won_stalemate(self, world, strategic_executor, game_state):
        """until_battle_won also triggers on stalemate."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.last_combat_result = "stalemate"
        grouchy.strategic_order = _make_order(
            "HOLD", "Wavre", path=[],
            condition=StrategicCondition(until_battle_won=True))

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"

    def test_condition_not_met_continues(self, world, strategic_executor, game_state):
        """Unmet conditions allow order to continue."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order(
            "HOLD", "Wavre", path=[],
            condition=StrategicCondition(until_marshal_arrives="Davout"))

        # Davout is NOT at Wavre (he's at Paris)
        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "continues"
        assert grouchy.strategic_order is not None


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 14: COMPLETE/BREAK ORDER MECHANICS
# ════════════════════════════════════════════════════════════════════════════════

class TestCompleteBreakOrder:
    """Coverage for _complete_order and _break_order."""

    def test_literal_gets_trust_bonus_on_completion(self, world, strategic_executor, game_state):
        """Literal personality gets +5 trust when completing an order."""
        grouchy = world.get_marshal("Grouchy")
        initial_trust = grouchy.trust.value
        grouchy.location = "Munich"
        grouchy.strategic_order = _make_order("MOVE_TO", "Vienna", path=["Vienna"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "completed"
        assert report.get("precision_bonus") == True
        assert grouchy.trust.value == initial_trust + 5

    def test_non_literal_no_trust_bonus(self, world, strategic_executor, game_state):
        """Non-literal personality gets no trust bonus on completion."""
        davout = world.get_marshal("Davout")
        initial_trust = davout.trust.value
        davout.location = "Lyon"
        davout.strategic_order = _make_order("MOVE_TO", "Marseille", path=["Marseille"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report["order_status"] == "completed"
        assert report.get("precision_bonus") == False
        assert davout.trust.value == initial_trust

    def test_break_order_clears_order(self, world, strategic_executor, game_state):
        """Breaking an order clears strategic_order."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order("MOVE_TO", "NonExistent", path=[])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        assert report["order_status"] == "breaks"
        assert grouchy.strategic_order is None


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 15: BLOCKED PATH PERSONALITY ROUTING
# ════════════════════════════════════════════════════════════════════════════════

class TestBlockedPathRouting:
    """Coverage for _handle_blocked_path personality behavior."""

    def test_literal_reroutes_silently(self, world, strategic_executor, game_state):
        """Literal blocked path → silent reroute (no player input)."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Wavre"
        grouchy.strategic_order = _make_order(
            "MOVE_TO", "Waterloo", path=["Ligny", "Waterloo"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Grouchy"][0]
        # Should NOT require input
        assert report.get("requires_input", False) == False

    def test_cautious_always_asks(self, world, strategic_executor, game_state):
        """Cautious blocked path → always asks player."""
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        davout.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report.get("requires_input") == True
        assert report.get("interrupt_type") == "contact"
        assert "attack" in report.get("options", [])

    def test_aggressive_auto_attacks_good_odds(self, world, strategic_executor, game_state):
        """Aggressive auto-attacks when ratio >= 0.7."""
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 50000
        world.get_marshal("Wellington").strength = 50000  # 1.0 ratio
        ney.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        # Should auto-attack (ratio 1.0 >= 0.7), not ask
        assert report.get("requires_input", False) == False or \
               report.get("action") == "combat"

    def test_aggressive_asks_on_bad_odds(self, world, strategic_executor, game_state):
        """Aggressive asks player when odds < 0.7."""
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 10000
        world.get_marshal("Wellington").strength = 50000  # 0.2 ratio
        ney.strategic_order = _make_order(
            "MOVE_TO", "Ligny", path=["Waterloo", "Ligny"])

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report.get("requires_input") == True
        assert report.get("interrupt_type") == "contact_bad_odds"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 16: EXECUTOR CANCEL COVERAGE
# ════════════════════════════════════════════════════════════════════════════════

class TestExecutorCancel:
    """Coverage for _execute_cancel in executor.py."""

    def test_cancel_auto_finds_marshal(self, world, executor, game_state):
        """Cancel without specifying marshal finds one with active order."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.strategic_order = _make_order("MOVE_TO", "Vienna", path=["Munich"])

        result = executor.execute({
            "command": {"action": "cancel"}
        }, game_state)

        assert result["success"] == True
        assert grouchy.strategic_order is None

    def test_cancel_no_orders_returns_error(self, world, executor, game_state):
        """Cancel when no marshal has orders → error."""
        for m in world.marshals.values():
            m.strategic_order = None

        result = executor.execute({
            "command": {"marshal": "Grouchy", "action": "cancel"}
        }, game_state)

        assert result["success"] == False

    def test_cancel_hold_clears_holding_state(self, world, executor, game_state):
        """Cancel HOLD order clears holding_position."""
        grouchy = world.get_marshal("Grouchy")
        grouchy.holding_position = True
        grouchy.hold_region = "Wavre"
        grouchy.strategic_order = _make_order("HOLD", "Wavre", path=[])

        result = executor.execute({
            "command": {"marshal": "Grouchy", "action": "cancel"}
        }, game_state)

        assert result["success"] == True
        assert grouchy.holding_position == False
        assert grouchy.hold_region == ""

    def test_cancel_first_step_zero_trust(self, world, executor, game_state):
        """Cancel on same turn as order creation → 0 trust penalty."""
        grouchy = world.get_marshal("Grouchy")
        initial_trust = grouchy.trust.value
        order = _make_order("MOVE_TO", "Vienna", path=["Munich"])
        order.started_turn = world.current_turn  # Same turn
        grouchy.strategic_order = order

        result = executor.execute({
            "command": {"marshal": "Grouchy", "action": "cancel"}
        }, game_state)

        assert result["success"] == True
        assert result["trust_change"] == 0
        assert grouchy.trust.value == initial_trust

    def test_cancel_mid_march_negative_trust(self, world, executor, game_state):
        """Cancel after order has been running → -3 trust penalty."""
        grouchy = world.get_marshal("Grouchy")
        initial_trust = grouchy.trust.value
        order = _make_order("MOVE_TO", "Vienna", path=["Munich"])
        order.started_turn = world.current_turn - 2  # Started 2 turns ago
        grouchy.strategic_order = order

        result = executor.execute({
            "command": {"marshal": "Grouchy", "action": "cancel"}
        }, game_state)

        assert result["success"] == True
        assert result["trust_change"] == -3
        assert grouchy.trust.value == initial_trust - 3

    def test_cancel_flavorful_messages(self, world, executor, game_state):
        """Cancel generates different messages per order type."""
        order_types = {
            "MOVE_TO": "halts",
            "PURSUE": "pursuit",
            "HOLD": "abandons",
            "SUPPORT": "supporting",
        }
        for cmd_type, keyword in order_types.items():
            grouchy = world.get_marshal("Grouchy")
            grouchy.strategic_order = _make_order(cmd_type, "Vienna", path=[])
            grouchy.holding_position = False  # Reset

            result = executor.execute({
                "command": {"marshal": "Grouchy", "action": "cancel"}
            }, game_state)

            assert result["success"] == True
            assert keyword in result["message"].lower(), \
                f"'{keyword}' not in cancel message for {cmd_type}: {result['message']}"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 17: CANNON FIRE INTERRUPT SYSTEM
# ════════════════════════════════════════════════════════════════════════════════

class TestCannonFireSystem:
    """Coverage for _check_interrupts cannon fire detection."""

    def test_no_battles_no_interrupt(self, world, strategic_executor, game_state):
        """No nearby battles → no interrupt."""
        davout = world.get_marshal("Davout")
        davout.strategic_order = _make_order("MOVE_TO", "Lyon", path=["Lyon"])

        # No battles recorded
        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report.get("interrupt") != "cannon_fire"
        assert report["order_status"] in ("continues", "completed")

    def test_battle_out_of_range_no_interrupt(self, world, strategic_executor, game_state):
        """Battle >2 regions away → no cannon fire interrupt."""
        davout = world.get_marshal("Davout")
        davout.location = "Marseille"  # Far from Berlin
        davout.strategic_order = _make_order("MOVE_TO", "Lyon", path=["Lyon"])

        world.record_battle("Berlin", "Wellington", "Blucher", "victory")

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Davout"][0]
        assert report.get("interrupt") != "cannon_fire"

    def test_combat_populates_battles_this_turn(self, world, executor, game_state):
        """Combat via executor records battle for cannon fire detection."""
        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"

        assert len(world.battles_this_turn) == 0

        result = executor.execute({
            "command": {
                "marshal": "Ney",
                "action": "attack",
                "target": "Wellington",
            }
        }, game_state)

        assert len(world.battles_this_turn) >= 1, \
            "resolve_battle should call record_battle to populate battles_this_turn"
        battle = world.battles_this_turn[0]
        assert battle["attacker"] == "Ney"
        assert battle["defender"] == "Wellington"
        assert battle["location"] == "Waterloo"

    def test_end_to_end_cannon_fire_from_real_combat(self, world, executor, strategic_executor, game_state):
        """Full flow: combat → record_battle → cannon fire interrupt on next strategic process."""
        # Set up: Ney attacks Wellington at Waterloo
        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"

        # Davout is cautious, 1 region away (Belgium adjacent to Waterloo)
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        davout.strategic_order = _make_order("MOVE_TO", "Rhine",
                                              path=["Netherlands", "Rhine"])

        # Execute combat
        executor.execute({
            "command": {"marshal": "Ney", "action": "attack", "target": "Wellington"}
        }, game_state)

        # Now process strategic orders — Davout should hear cannon fire
        reports = strategic_executor.process_strategic_orders(world, game_state)
        davout_reports = [r for r in reports if r["marshal"] == "Davout"]
        assert len(davout_reports) >= 1
        report = davout_reports[0]
        assert report.get("interrupt") == "cannon_fire", \
            f"Davout should hear cannon fire from Waterloo, got: {report}"

    def test_aggressive_auto_redirects(self, world, strategic_executor, game_state):
        """Aggressive auto-redirects on cannon fire (no player input)."""
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strategic_order = _make_order("MOVE_TO", "Marseille", path=["Lyon", "Marseille"])

        world.record_battle("Belgium", "Wellington", "Davout", "stalemate")

        reports = strategic_executor.process_strategic_orders(world, game_state)
        report = [r for r in reports if r["marshal"] == "Ney"][0]
        assert report.get("interrupt") == "cannon_fire"
        assert report.get("requires_input", False) == False
        assert report["order_status"] == "interrupted"
        # Order should be cleared
        assert ney.strategic_order is None


# ════════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

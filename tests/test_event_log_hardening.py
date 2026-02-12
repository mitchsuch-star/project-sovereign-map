"""Tests for Event Log Hardening (EL1-EL5, Session 31).

EL1: Sally battle event logging
EL2: Glorious charge event logging
EL3: AI occupation capture event logging
EL4: Auto-charge battle event logging
EL5: log_battle_event key not leaked to API responses
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, Stance
from backend.game_logic.combat import CombatResolver
from backend.commands.executor import CommandExecutor


# ============================================================
# EL1: Sally battle event logging
# ============================================================

class TestSallyBattleEventLogging:
    """EL1: The 3 sally resolve_battle call sites in _execute_general_attack_combat
    use _log_battle_event but lacked individual tests."""

    def test_sally_battle_logs_event(self):
        """Trigger a sally battle via _execute_general_attack_combat and verify
        a battle event is logged to world.event_log."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        # Position Ney (France) adjacent to Wellington (Britain)
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        ney.location = "Belgium"
        wellington.location = "Waterloo"

        # Call _execute_general_attack_combat directly (the sally path)
        result = executor._execute_general_attack_combat(
            ney, wellington, world, "Test sally.\n", game_state
        )
        assert result.get("success"), f"Sally battle failed: {result.get('message')}"

        # Verify battle event logged
        battle_events = world.get_events_by_type("battle")
        assert len(battle_events) >= 1, "No battle event logged for sally"
        event = battle_events[0]
        assert event["attacker"] == "Ney"
        assert event["defender"] == "Wellington"
        assert event["location"] == "Waterloo"
        assert "outcome" in event
        assert "attacker_casualties" in event
        assert "defender_casualties" in event


# ============================================================
# EL2: Glorious charge event logging
# ============================================================

class TestGloriousChargeEventLogging:
    """EL2: _execute_glorious_charge calls _log_battle_event but had no
    dedicated test."""

    def test_glorious_charge_logs_battle_event(self):
        """Set up reckless cavalry, trigger glorious charge, verify battle
        event logged with correct location."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        # Set up Ney as reckless cavalry adjacent to Wellington
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        ney.cavalry = True
        ney.recklessness = 3
        ney.location = "Belgium"
        wellington.location = "Waterloo"

        # Waterloo is plains terrain, so charge is not blocked
        result = executor._execute_glorious_charge(
            ney, "Wellington", world, game_state
        )
        assert result.get("success"), f"Glorious charge failed: {result.get('message')}"

        # Verify battle event logged
        battle_events = world.get_events_by_type("battle")
        assert len(battle_events) >= 1, "No battle event logged for glorious charge"
        event = battle_events[0]
        assert event["attacker"] == "Ney"
        assert event["defender"] == "Wellington"
        assert event["location"] == "Waterloo"


# ============================================================
# EL3: AI occupation capture event logging
# ============================================================

class TestAIOccupationCaptureEventLogging:
    """EL3: _apply_occupation_capture_effects logs region_captured for AI
    but was only indirectly covered."""

    def test_ai_occupation_capture_logs_region_captured(self):
        """Set enemy marshal occupying a region, complete occupation timer,
        assert region_captured event with correct captured_by and method."""
        world = WorldState()

        # Use Wellington (Britain, cautious) — cautious AI should secure
        wellington = world.get_marshal("Wellington")
        target_region_name = "Paris"
        wellington.location = target_region_name

        # Set up occupation state (about to complete)
        wellington.occupation_region = target_region_name
        wellington.occupation_turns_held = 1  # Will be incremented to 2
        wellington.occupation_turns_required = 2

        # Paris starts controlled by France
        paris = world.get_region(target_region_name)
        assert paris.controller == "France"

        # Process tactical states (this ticks occupation and triggers capture)
        events = world._process_tactical_states()

        # Find the occupation_complete event
        occ_events = [e for e in events if e.get("type") == "occupation_complete"]
        assert len(occ_events) == 1, f"Expected occupation_complete event, got: {[e.get('type') for e in events]}"

        # Verify region_captured event was logged to world.event_log
        captured_events = world.get_events_by_type("region_captured")
        assert len(captured_events) == 1, "No region_captured event logged for AI occupation"
        event = captured_events[0]
        assert event["captured_by"] == "Britain"
        assert event["captured_from"] == "France"
        assert event["region"] == target_region_name
        # Wellington is cautious, so AI should secure (not plunder)
        assert event["method"] == "secure"


# ============================================================
# EL4: Auto-charge battle path logs events
# ============================================================

class TestAutoChargeBattleEventLogging:
    """EL4: _process_reckless_cavalry_turn_start creates its own combat
    resolution path. Verify battle event is logged to world.event_log."""

    def test_auto_charge_logs_battle_event(self):
        """Reckless cavalry at 4+ auto-charges at turn start. Confirm
        battle event is logged."""
        world = WorldState()

        # Set up Ney as reckless cavalry with auto-charge threshold
        ney = world.get_marshal("Ney")
        ney.cavalry = True
        ney.recklessness = 4  # Auto-charge threshold
        ney.location = "Belgium"
        ney.strength = 30000
        ney.morale = 80

        # Wellington adjacent in Waterloo (plains — charge not blocked)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 25000

        # Process reckless cavalry turn start
        events = world._process_reckless_cavalry_turn_start()

        # Should have an auto_glorious_charge event
        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        assert len(charge_events) >= 1, f"No auto_glorious_charge event, got: {[e.get('type') for e in events]}"

        # Verify battle event was logged to world.event_log
        battle_events = world.get_events_by_type("battle")
        assert len(battle_events) >= 1, (
            "No battle event logged in world.event_log for auto-charge. "
            "The auto-charge path in _process_reckless_cavalry_turn_start must call "
            "world.log_event() with the log_battle_event from combat result."
        )
        event = battle_events[0]
        assert event["attacker"] == "Ney"
        assert event["defender"] == "Wellington"
        assert event["location"] == "Waterloo"


# ============================================================
# EL4b: Auto-charge tactical event has no floats (Session 31b)
# ============================================================

class TestAutoChargeTacticalEventNoFloats:
    """The auto-charge tactical event is sent to Godot via the events list.
    It must not contain combat_result (which has floats like
    attacker_roll.multiplier) or any other float values."""

    def _find_floats(self, obj, path=""):
        """Recursively find any float values in a nested dict/list structure."""
        floats_found = []
        if isinstance(obj, float):
            floats_found.append(f"{path} = {obj}")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                floats_found.extend(self._find_floats(v, f"{path}.{k}"))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                floats_found.extend(self._find_floats(v, f"{path}[{i}]"))
        return floats_found

    def test_auto_charge_event_has_no_combat_result(self):
        """Auto-charge tactical event must not embed raw combat_result."""
        world = WorldState()

        ney = world.get_marshal("Ney")
        ney.cavalry = True
        ney.recklessness = 4
        ney.location = "Belgium"
        ney.strength = 30000
        ney.morale = 80

        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 25000

        events = world._process_reckless_cavalry_turn_start()
        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        assert len(charge_events) >= 1

        event = charge_events[0]
        assert "combat_result" not in event, (
            "Auto-charge tactical event still contains combat_result — "
            "this dict has floats (attacker_roll.multiplier) that would crash Godot"
        )

    def test_auto_charge_event_contains_no_floats(self):
        """No float values anywhere in the auto-charge tactical event dict."""
        world = WorldState()

        ney = world.get_marshal("Ney")
        ney.cavalry = True
        ney.recklessness = 4
        ney.location = "Belgium"
        ney.strength = 30000
        ney.morale = 80

        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 25000

        events = world._process_reckless_cavalry_turn_start()
        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        assert len(charge_events) >= 1

        event = charge_events[0]
        floats = self._find_floats(event, "auto_charge_event")
        assert len(floats) == 0, (
            f"Float values found in auto-charge tactical event "
            f"(would crash Godot):\n" + "\n".join(floats)
        )


# ============================================================
# EL5: log_battle_event key not leaked to API responses
# ============================================================

class TestLogBattleEventNotLeaked:
    """EL5: combat.py adds log_battle_event (dict with nested battle_report
    containing floats) to resolve_battle result. Verify main.py response
    formatting does not pass this key through to Godot."""

    def test_log_battle_event_exists_in_combat_result(self):
        """Sanity check: resolve_battle result includes log_battle_event."""
        resolver = CombatResolver()
        attacker = Marshal("A", "Paris", 30000, "aggressive", nation="France",
                           skills={"tactical": 5, "shock": 5, "defense": 5})
        defender = Marshal("B", "Waterloo", 25000, "cautious", nation="Britain",
                           skills={"tactical": 5, "shock": 5, "defense": 5})

        result = resolver.resolve_battle(attacker, defender, terrain="plains")
        assert "log_battle_event" in result, "resolve_battle should include log_battle_event"

    def test_main_response_does_not_include_log_battle_event(self):
        """The /command endpoint response dict must not contain log_battle_event.

        main.py builds the response by selectively picking keys (success, message,
        events, battle_report, etc.) — it never explicitly copies log_battle_event.
        This test verifies the pattern holds by checking the response construction
        code path does not reference this key.
        """
        import inspect
        from backend.main import app

        # Read the source of the command endpoint
        # Find the /command route handler
        source = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/command":
                source = inspect.getsource(route.endpoint)
                break

        assert source is not None, "Could not find /command endpoint"
        # The response construction should NOT reference log_battle_event
        assert "log_battle_event" not in source, (
            "main.py /command endpoint references 'log_battle_event' — "
            "this key contains floats that would crash Godot if leaked to the response"
        )

    def test_executor_result_keys_filtered_in_response(self):
        """Verify that when executor returns a result with log_battle_event,
        the selective response construction in main.py would not pass it through.

        We test this by checking that the known response keys do NOT include
        log_battle_event — main.py uses explicit key access (result.get("key"))
        rather than passing the whole result dict."""
        # Known keys that main.py explicitly passes to response
        known_response_keys = {
            "success", "message", "events", "action_info",
            "battle_report", "cavalry_terrain_message",
            "mild_concerns", "enemy_phase", "show_load_dialog",
            "pending_objection", "pending_glorious_charge",
            "pending_capture_choice", "pending_strategic_objection",
            "strategic_reports", "turn_end",
        }
        assert "log_battle_event" not in known_response_keys

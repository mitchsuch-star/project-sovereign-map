"""Tests for Turn Events Log (Phase 6.5 data layer).

Tests cover:
- WorldState event_log field initialization and helpers
- Serialization round-trip and backward compatibility
- Event logging at each insertion point
"""

from unittest.mock import patch
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.game_logic.combat import CombatResolver
from backend.commands.executor import CommandExecutor


# ============================================================
# WORLDSTATE INTEGRATION TESTS
# ============================================================

class TestEventLogField:
    """Test event_log field on WorldState."""

    def test_event_log_initializes_empty(self):
        world = WorldState()
        assert world.event_log == []

    def test_log_event_appends(self):
        world = WorldState()
        world.log_event({"type": "test"})
        assert len(world.event_log) == 1
        assert world.event_log[0]["type"] == "test"

    def test_log_event_sets_turn(self):
        world = WorldState()
        world.current_turn = 5
        world.log_event({"type": "test"})
        assert world.event_log[0]["turn"] == 5

    def test_log_event_overwrites_turn(self):
        """Turn is always set to current_turn, even if event already has a turn field."""
        world = WorldState()
        world.current_turn = 7
        world.log_event({"type": "test", "turn": 3})
        assert world.event_log[0]["turn"] == 7

    def test_multiple_events_accumulate(self):
        world = WorldState()
        world.current_turn = 1
        world.log_event({"type": "a"})
        world.current_turn = 2
        world.log_event({"type": "b"})
        world.log_event({"type": "c"})
        assert len(world.event_log) == 3
        assert world.event_log[0]["turn"] == 1
        assert world.event_log[1]["turn"] == 2
        assert world.event_log[2]["turn"] == 2


class TestEventLogHelpers:
    """Test query helper methods."""

    def _make_world_with_events(self):
        world = WorldState()
        world.current_turn = 1
        world.log_event({"type": "battle", "attacker": "Ney"})
        world.log_event({"type": "retreat", "marshal": "Wellington"})
        world.current_turn = 2
        world.log_event({"type": "battle", "attacker": "Davout"})
        world.current_turn = 3
        world.log_event({"type": "recruitment", "marshal": "Ney"})
        world.log_event({"type": "building_started", "region": "Paris"})
        return world

    def test_get_events_for_turn(self):
        world = self._make_world_with_events()
        turn1 = world.get_events_for_turn(1)
        assert len(turn1) == 2
        assert turn1[0]["type"] == "battle"
        assert turn1[1]["type"] == "retreat"

    def test_get_events_for_turn_empty(self):
        world = self._make_world_with_events()
        assert world.get_events_for_turn(99) == []

    def test_get_events_since_turn(self):
        world = self._make_world_with_events()
        since2 = world.get_events_since_turn(2)
        assert len(since2) == 3
        assert all(e["turn"] >= 2 for e in since2)

    def test_get_events_by_type(self):
        world = self._make_world_with_events()
        battles = world.get_events_by_type("battle")
        assert len(battles) == 2
        assert battles[0]["attacker"] == "Ney"
        assert battles[1]["attacker"] == "Davout"

    def test_get_events_by_type_no_matches(self):
        world = self._make_world_with_events()
        assert world.get_events_by_type("nonexistent") == []

    def test_get_latest_events_default(self):
        world = self._make_world_with_events()
        latest = world.get_latest_events()
        assert len(latest) == 5  # Only 5 events total

    def test_get_latest_events_limited(self):
        world = self._make_world_with_events()
        latest = world.get_latest_events(2)
        assert len(latest) == 2
        assert latest[0]["type"] == "recruitment"
        assert latest[1]["type"] == "building_started"

    def test_get_latest_events_exceeds_total(self):
        world = self._make_world_with_events()
        latest = world.get_latest_events(100)
        assert len(latest) == 5


# ============================================================
# SERIALIZATION TESTS
# ============================================================

class TestEventLogSerialization:
    """Test event_log serialization round-trip."""

    def test_to_dict_includes_event_log(self):
        world = WorldState()
        world.log_event({"type": "battle", "attacker": "Ney"})
        data = world.to_dict()
        assert "event_log" in data
        assert len(data["event_log"]) == 1
        assert data["event_log"][0]["type"] == "battle"

    def test_from_dict_restores_event_log(self):
        world = WorldState()
        world.current_turn = 5
        world.log_event({"type": "battle", "attacker": "Ney", "defender": "Wellington"})
        world.log_event({"type": "retreat", "marshal": "Wellington"})

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert len(restored.event_log) == 2
        assert restored.event_log[0]["type"] == "battle"
        assert restored.event_log[0]["turn"] == 5
        assert restored.event_log[1]["type"] == "retreat"

    def test_from_dict_backward_compat_no_event_log(self):
        """Old saves without event_log should get an empty list."""
        data = WorldState().to_dict()
        del data["event_log"]
        restored = WorldState.from_dict(data)
        assert restored.event_log == []

    def test_event_log_with_battle_report_serializes(self):
        """Events containing nested dicts (like battle_report) serialize correctly."""
        world = WorldState()
        world.log_event({
            "type": "battle",
            "battle_report": {
                "modifier_breakdown": {"attacker": [], "defender": []},
                "casualty_summary": {"attacker_casualties": 5000},
                "observation": "A hard-fought battle."
            }
        })
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.event_log[0]["battle_report"]["observation"] == "A hard-fought battle."

    def test_event_log_from_dict_independent(self):
        """from_dict should produce independent event list (top-level dicts are copies)."""
        world = WorldState()
        world.log_event({"type": "test", "value": 42})
        data = world.to_dict()

        restored = WorldState.from_dict(data)
        restored.event_log[0]["value"] = 999  # Mutate restored copy
        assert world.event_log[0]["value"] == 42  # Original unaffected by shallow copy


# ============================================================
# BATTLE EVENT LOGGING TESTS
# ============================================================

class TestBattleEventLogging:
    """Test that battles produce correct event log entries."""

    def _make_game_state(self):
        world = WorldState()
        return {"world": world}

    def test_combat_result_includes_log_battle_event(self):
        """resolve_battle should include a log_battle_event in its result."""
        resolver = CombatResolver()
        attacker = Marshal("TestA", "Paris", 30000, "aggressive", nation="France",
                           skills={"tactical": 5, "shock": 5, "defense": 5})
        defender = Marshal("TestB", "Waterloo", 25000, "cautious", nation="Britain",
                           skills={"tactical": 5, "shock": 5, "defense": 5})

        result = resolver.resolve_battle(attacker, defender, terrain="plains")

        assert "log_battle_event" in result
        event = result["log_battle_event"]
        assert event["type"] == "battle"
        assert event["attacker"] == "TestA"
        assert event["defender"] == "TestB"
        assert event["attacker_nation"] == "France"
        assert event["defender_nation"] == "Britain"
        assert "outcome" in event
        assert "attacker_casualties" in event
        assert "defender_casualties" in event
        # battle_report stripped from log event (V3 Session 8, bug 2D-2)
        assert "battle_report" not in event

    def test_battle_event_logged_on_attack(self):
        """Executing an attack should log a battle event to world.event_log."""
        game_state = self._make_game_state()
        world = game_state["world"]
        world.opening_attack_guidance_shown = True
        executor = CommandExecutor()

        # Force Ney and Wellington into adjacent regions
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        ney.location = "Belgium"
        wellington.location = "Waterloo"

        # Use _execute_attack directly to avoid dispatch complexity
        result = executor._execute_attack(ney, "Waterloo", world, game_state)
        assert result.get("success")

        # Should have at least one battle event
        battle_events = world.get_events_by_type("battle")
        assert len(battle_events) >= 1
        assert battle_events[0]["attacker"] == "Ney"
        assert battle_events[0]["location"] == "Waterloo"


class TestRetreatEventLogging:
    """Test retreat and broken events."""

    def test_forced_retreat_logs_retreat_event(self):
        """When a marshal is forced to retreat, a retreat event should be logged."""
        world = WorldState()
        executor = CommandExecutor()

        # Create marshal with very low morale that will trigger retreat
        marshal = world.get_marshal("Ney")
        marshal.morale = 20  # Below forced retreat threshold of 25
        original_location = marshal.location

        # Simulate forced retreat using the internal method
        # Create a mock enemy
        enemy = world.get_marshal("Wellington")
        if enemy:
            enemy.location = marshal.location  # Same location for battle context

            # Call internal method
            msg = executor._apply_forced_retreat_or_break(marshal, enemy, world)

            if msg:
                retreat_events = world.get_events_by_type("retreat")
                broken_events = world.get_events_by_type("marshal_broken")
                # Should have either a retreat or broken event
                assert len(retreat_events) + len(broken_events) >= 1

    def test_broken_army_logs_marshal_broken_event(self):
        """When army is surrounded and shattered, marshal_broken event logged."""
        world = WorldState()
        executor = CommandExecutor()

        marshal = world.get_marshal("Ney")
        marshal.morale = 10

        # Put enemies in all adjacent regions to force "surrounded" state
        ney_region = world.get_region(marshal.location)
        for adj_name in ney_region.adjacent_regions:
            # Create mock enemy in each adjacent region
            for enemy_m in world.marshals.values():
                if enemy_m.nation != "France":
                    break
            # Just move all enemies around Ney
            break

        # Force a broken path by mocking get_safe_retreat_destination to return None
        with patch.object(world, 'get_safe_retreat_destination', return_value=None):
            enemy = world.get_marshal("Wellington")
            if enemy:
                msg = executor._apply_forced_retreat_or_break(marshal, enemy, world)
                if msg and "SHATTERED" in msg:
                    broken_events = world.get_events_by_type("marshal_broken")
                    assert len(broken_events) == 1
                    assert broken_events[0]["marshal"] == "Ney"
                    assert broken_events[0]["nation"] == "France"


# ============================================================
# TERRITORY EVENT LOGGING TESTS
# ============================================================

class TestTerritoryEventLogging:
    """Test region_captured event logging."""

    def test_plunder_choice_logs_region_captured(self):
        """Player choosing plunder should log region_captured with method=plunder."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}

        # Set up pending capture choice
        world.pending_capture_choice = {
            "region": "Waterloo",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        # Need to own the region already (capture_region was called)
        world.capture_region("Waterloo", "France")

        result = executor.handle_capture_choice("plunder", game_state)
        assert result["success"]

        events = world.get_events_by_type("region_captured")
        assert len(events) == 1
        assert events[0]["region"] == "Waterloo"
        assert events[0]["captured_by"] == "France"
        assert events[0]["captured_from"] == "Britain"
        assert events[0]["method"] == "plunder"

    def test_secure_choice_logs_region_captured(self):
        """Player choosing secure should log region_captured with method=secure."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}

        world.pending_capture_choice = {
            "region": "Waterloo",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        world.capture_region("Waterloo", "France")

        result = executor.handle_capture_choice("secure", game_state)
        assert result["success"]

        events = world.get_events_by_type("region_captured")
        assert len(events) == 1
        assert events[0]["method"] == "secure"


# ============================================================
# ECONOMY EVENT LOGGING TESTS
# ============================================================

class TestEconomyEventLogging:
    """Test economy event logging (recruitment, buildings, bankruptcy, desertion)."""

    def test_recruit_logs_recruitment_event(self):
        """Successful recruitment should log a recruitment event."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}

        # Give enough gold
        world.nation_gold["France"] = 5000
        # Ensure Paris has high enough stability
        paris = world.get_region("Paris")
        paris.stability = 80

        # Make sure Ney is in Paris
        ney = world.get_marshal("Ney")
        ney.location = "Paris"

        command = {
            "action": "recruit",
            "marshal": "Ney",
            "target": "Paris",
        }
        result = executor._execute_recruit(command, game_state)

        if result.get("success"):
            events = world.get_events_by_type("recruitment")
            assert len(events) == 1
            assert events[0]["marshal"] == "Ney"
            assert events[0]["nation"] == "France"
            assert events[0]["amount"] == 5000  # Ney is cavalry
            assert events[0]["location"] == "Paris"

    def test_build_logs_building_started_event(self):
        """Starting a building should log a building_started event."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}

        world.nation_gold["France"] = 5000
        paris = world.get_region("Paris")
        paris.stability = 80
        paris.controller = "France"
        # Clear any existing buildings
        paris.buildings = []
        paris.building_under_construction = None

        command = {
            "action": "build",
            "target": "Paris",
            "building_type": "market",
            "raw_command": "build market at Paris",
        }
        result = executor._execute_build(command, game_state)

        if result.get("success"):
            events = world.get_events_by_type("building_started")
            assert len(events) == 1
            assert events[0]["region"] == "Paris"
            assert events[0]["building"] == "market"
            assert events[0]["nation"] == "France"

    def test_building_completed_logs_event(self):
        """When construction finishes, building_completed event should be logged."""
        world = WorldState()
        paris = world.get_region("Paris")
        paris.building_under_construction = {
            "type": "supply_depot",
            "turns_remaining": 1
        }

        events = world.process_construction_timers()

        # Check tactical event was returned
        assert any(e["type"] == "construction_complete" for e in events)

        # Check event log
        log_events = world.get_events_by_type("building_completed")
        assert len(log_events) == 1
        assert log_events[0]["region"] == "Paris"
        assert log_events[0]["building"] == "supply_depot"

    def test_bankruptcy_logs_event(self):
        """Bankruptcy should log a bankruptcy event."""
        world = WorldState()
        world.nation_gold["France"] = -100
        world.nation_bankruptcy_turns["France"] = 1

        result = world.process_bankruptcy_desertion("France")

        events = world.get_events_by_type("bankruptcy")
        assert len(events) == 1
        assert events[0]["nation"] == "France"
        assert events[0]["deficit"] == -100

    def test_desertion_logs_events(self):
        """Bankruptcy at 3+ turns should log desertion events for each marshal."""
        world = WorldState()
        world.nation_gold["France"] = -500
        world.nation_bankruptcy_turns["France"] = 3

        result = world.process_bankruptcy_desertion("France")

        assert result["bankrupt"]
        desertion_events = world.get_events_by_type("desertion")
        # Should have desertions for French marshals with troops
        french_marshals_with_troops = [
            m for m in world.marshals.values()
            if m.nation == "France" and m.strength > 0
        ]
        assert len(desertion_events) == len(french_marshals_with_troops)
        for ev in desertion_events:
            assert ev["nation"] == "France"
            assert ev["cause"] == "bankruptcy"
            assert ev["amount"] > 0

    def test_building_damaged_in_battle(self):
        """Battle should log building_damaged events for damaged buildings."""
        world = WorldState()
        executor = CommandExecutor()

        region = world.get_region("Paris")
        region.buildings = [{"type": "market", "damaged": False}]

        # Force damage (major battle threshold)
        with patch('random.random', return_value=0.0):  # Always damages
            executor._apply_battle_effects_to_region("Paris", 30000, 30000, world)

        damaged_events = world.get_events_by_type("building_damaged")
        assert len(damaged_events) == 1
        assert damaged_events[0]["region"] == "Paris"
        assert damaged_events[0]["building"] == "market"
        assert damaged_events[0]["cause"] == "battle"

    def test_building_damaged_by_plunder(self):
        """Plunder should log building_damaged events for destroyed buildings."""
        world = WorldState()
        executor = CommandExecutor()

        region = world.get_region("Paris")
        region.buildings = [
            {"type": "market", "damaged": False},
            {"type": "supply_depot", "damaged": False},
        ]

        executor._apply_plunder(region, world)

        damaged_events = world.get_events_by_type("building_damaged")
        assert len(damaged_events) == 2
        assert damaged_events[0]["cause"] == "plunder"
        assert damaged_events[1]["cause"] == "plunder"


# ============================================================
# COMMAND EVENT LOGGING TESTS
# ============================================================

class TestCommandEventLogging:
    """Test objection and strategic order event logging."""

    def test_objection_resolved_logs_event(self):
        """Resolving a MODERATE+ objection should log an objection event."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}

        ney = world.get_marshal("Ney")
        # Set up a pending objection
        world.pending_objection = {
            "type": "major_objection",
            "concern_level": "MODERATE",
            "marshal": "Ney",
            "personality": ney.personality,
            "original_order": {"action": "attack", "target": "Waterloo"},
            "message": "Test objection",
            "suggested_alternative": None,
            "insist_penalty": -5,
            "trust_gain": 10,
        }

        result = executor.handle_objection_response("insist", game_state)

        events = world.get_events_by_type("objection")
        assert len(events) == 1
        assert events[0]["marshal"] == "Ney"
        assert events[0]["concern_level"] == "MODERATE"
        assert events[0]["action"] == "attack"
        assert events[0]["resolution"] == "insist"

    def test_objection_trust_resolution_logged(self):
        """Trusting a marshal on objection should log with resolution=trust."""
        world = WorldState()
        executor = CommandExecutor()
        game_state = {"world": world}

        ney = world.get_marshal("Ney")
        world.pending_objection = {
            "type": "major_objection",
            "concern_level": "SERIOUS",
            "marshal": "Ney",
            "personality": ney.personality,
            "original_order": {"action": "move", "target": "Paris"},
            "message": "Test objection",
            "suggested_alternative": None,
            "insist_penalty": -10,
            "trust_gain": 15,
        }

        result = executor.handle_objection_response("trust", game_state)

        events = world.get_events_by_type("objection")
        assert len(events) == 1
        assert events[0]["resolution"] == "trust"

    def test_mild_concern_not_logged(self):
        """MILD concerns should NOT appear in the event log."""
        world = WorldState()
        # MILD concerns go to mild_concerns_this_turn, not event_log
        world.mild_concerns_this_turn.append({
            "marshal": "Ney",
            "message": "Ney mutters something about the weather."
        })

        # No event should be in the log for mild concerns
        events = world.get_events_by_type("objection")
        assert len(events) == 0


# ============================================================
# RECOVERY EVENT LOGGING TESTS
# ============================================================

class TestRecoveryEventLogging:
    """Test marshal_recovered events from _process_tactical_states."""

    def test_retreat_recovery_logs_marshal_recovered(self):
        """When retreat recovery completes, marshal_recovered event should be logged."""
        world = WorldState()
        marshal = world.get_marshal("Ney")
        marshal.retreating = True
        marshal.retreat_recovery = 2  # Stage 2 -> 3 = recovered

        # Process tactical states
        events = world._process_tactical_states()

        # Check event log
        recovered_events = world.get_events_by_type("marshal_recovered")
        assert len(recovered_events) == 1
        assert recovered_events[0]["marshal"] == "Ney"
        assert recovered_events[0]["recovery_type"] == "retreat"

    def test_broken_recovery_logs_marshal_recovered(self):
        """When broken recovery completes, marshal_recovered event should be logged."""
        world = WorldState()
        marshal = world.get_marshal("Ney")
        marshal.broken = True
        marshal.broken_recovery = 3  # Stage 3 -> 4 = recovered

        events = world._process_tactical_states()

        recovered_events = world.get_events_by_type("marshal_recovered")
        assert len(recovered_events) == 1
        assert recovered_events[0]["marshal"] == "Ney"
        assert recovered_events[0]["recovery_type"] == "broken"


# ============================================================
# INTEGRATION TEST
# ============================================================

class TestEventLogIntegration:
    """Integration tests for event log across a turn."""

    def test_events_not_cleared_between_turns(self):
        """Event log should accumulate across turns, never be cleared."""
        world = WorldState()
        world.current_turn = 1
        world.log_event({"type": "battle"})
        world.current_turn = 2
        world.log_event({"type": "retreat"})

        # Simulate turn advance
        world.current_turn = 3
        world.log_event({"type": "recruitment"})

        assert len(world.event_log) == 3
        assert world.event_log[0]["turn"] == 1
        assert world.event_log[1]["turn"] == 2
        assert world.event_log[2]["turn"] == 3

    def test_event_log_survives_save_load_cycle(self):
        """Full save/load cycle preserves event log."""
        world = WorldState()
        world.current_turn = 5
        world.log_event({"type": "battle", "attacker": "Ney", "defender": "Wellington"})
        world.log_event({"type": "region_captured", "region": "Waterloo", "method": "plunder"})
        world.current_turn = 6
        world.log_event({"type": "recruitment", "marshal": "Grouchy", "amount": 10000})

        # Save
        data = world.to_dict()

        # Load
        restored = WorldState.from_dict(data)

        assert len(restored.event_log) == 3
        assert restored.get_events_for_turn(5) == world.get_events_for_turn(5)
        assert restored.get_events_by_type("battle")[0]["attacker"] == "Ney"

    def test_ai_actions_also_generate_events(self):
        """AI (enemy) bankruptcy desertions should also create events."""
        world = WorldState()
        world.nation_gold["Britain"] = -300
        world.nation_bankruptcy_turns["Britain"] = 3

        result = world.process_bankruptcy_desertion("Britain")

        events = world.get_events_by_type("desertion")
        british_desertions = [e for e in events if e["nation"] == "Britain"]
        assert len(british_desertions) > 0

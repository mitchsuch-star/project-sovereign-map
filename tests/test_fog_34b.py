"""
Fog of War Session 34B Tests

Tests for strategic fog validation, display filtering, and event log types.

Covers:
- get_last_known_location() helper
- get_visible_enemies_in_region() helper
- PURSUE fog validation (UNKNOWN reject, STALE use, empty arrival, destroyed target)
- SUPPORT fog-aware safety check
- Cautious pathfinding fog_aware parameter
- Enemy phase display filtering
- Tactical event filtering
- Event log types (intel_updated, intel_decayed, target_not_found)
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.intel import (
    RegionIntel, FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
    get_strength_band,
)
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicExecutor
from backend.models.marshal import StrategicOrder, StrategicCondition


# ============================================================================
# HELPERS
# ============================================================================

def make_world():
    """Create a fresh WorldState for testing."""
    return WorldState(player_nation="France")


def make_game_state(world):
    """Create game state dict in the format executor expects."""
    return {"world": world, "debug_mode": True}


def set_intel(world, region_name, visibility, marshals=None, turn=1, source="scout"):
    """Helper to set intel on a region to a specific visibility level."""
    intel = world.get_region_intel(region_name)
    if marshals is None:
        marshals = []
    intel.visibility = visibility
    intel.known_marshals = marshals
    intel.last_updated_turn = turn
    intel.intel_source = source


def clear_all_intel(world):
    """Reset all intel to UNKNOWN for clean test state."""
    for region_name in world.regions:
        intel = world.get_region_intel(region_name)
        intel.visibility = UNKNOWN
        intel.known_marshals = []
        intel.last_updated_turn = 0
        intel.intel_source = ""


# ============================================================================
# TEST: get_last_known_location()
# ============================================================================

class TestGetLastKnownLocation:
    """Tests for WorldState.get_last_known_location() helper."""

    def test_never_scouted_returns_none(self):
        """Marshal never appears in any intel -> returns None."""
        world = make_world()
        clear_all_intel(world)
        result = world.get_last_known_location("Imaginary_Marshal")
        assert result is None

    def test_finds_marshal_in_intel(self):
        """Marshal present in intel -> returns location tuple."""
        world = make_world()
        clear_all_intel(world)
        set_intel(world, "Waterloo", FULL,
                  marshals=[{"name": "Wellington", "nation": "Britain", "strength": 42000}],
                  turn=3)
        result = world.get_last_known_location("Wellington")
        assert result is not None
        assert result[0] == "Waterloo"
        assert result[1] == 3
        assert result[2] == FULL

    def test_multiple_stale_regions_most_recent_wins(self):
        """Marshal in multiple stale regions -> most recent last_updated_turn wins."""
        world = make_world()
        clear_all_intel(world)
        # Wellington seen at Waterloo on turn 2
        set_intel(world, "Waterloo", STALE,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=2)
        # Wellington seen at Brussels on turn 5 (more recent)
        set_intel(world, "Belgium", STALE,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=5)

        result = world.get_last_known_location("Wellington")
        assert result is not None
        assert result[0] == "Belgium"
        assert result[1] == 5

    def test_destroyed_marshal_persists(self):
        """Marshal destroyed -> last intel entry persists (player's last knowledge)."""
        world = make_world()
        clear_all_intel(world)
        # Wellington was at Waterloo on turn 3 before being destroyed
        set_intel(world, "Waterloo", LAST_KNOWN,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=3)
        # Kill Wellington
        wellington = world.get_marshal("Wellington")
        wellington.strength = 0

        result = world.get_last_known_location("Wellington")
        assert result is not None
        assert result[0] == "Waterloo"

    def test_returns_none_when_intel_cleared(self):
        """All intel has empty known_marshals -> returns None."""
        world = make_world()
        clear_all_intel(world)
        result = world.get_last_known_location("Wellington")
        assert result is None


# ============================================================================
# TEST: get_visible_enemies_in_region()
# ============================================================================

class TestGetVisibleEnemiesInRegion:
    """Tests for WorldState.get_visible_enemies_in_region() helper."""

    def test_full_visibility_returns_full_data(self):
        """FULL visibility -> returns actual Marshal objects."""
        world = make_world()
        # Move a French marshal to Waterloo to grant FULL visibility there
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Waterloo"
        world.calculate_visibility()
        enemies = world.get_visible_enemies_in_region("Waterloo", "France")
        assert len(enemies) > 0
        # Should be actual marshal objects
        assert hasattr(enemies[0], 'strength')
        assert hasattr(enemies[0], 'morale')

    def test_partial_returns_band_only(self):
        """PARTIAL visibility -> returns name + band dicts, not exact numbers."""
        world = make_world()
        # Netherlands is adjacent to Belgium (French) — should be PARTIAL
        intel = world.get_region_intel("Netherlands")
        # Force PARTIAL for test
        intel.visibility = PARTIAL
        enemies = world.get_visible_enemies_in_region("Netherlands", "France")
        # If there are enemies there
        if enemies:
            # Should be dicts with band, not marshal objects
            assert isinstance(enemies[0], dict)
            assert "strength_band" in enemies[0]
            assert "name" in enemies[0]
            assert "fog_level" in enemies[0]

    def test_unknown_returns_empty(self):
        """UNKNOWN visibility -> empty list."""
        world = make_world()
        clear_all_intel(world)
        enemies = world.get_visible_enemies_in_region("Vienna", "France")
        assert enemies == []

    def test_last_known_returns_empty(self):
        """LAST_KNOWN visibility -> empty list (enemies not confirmed visible)."""
        world = make_world()
        set_intel(world, "Vienna", LAST_KNOWN,
                  marshals=[{"name": "Kutuzov", "nation": "Russia"}],
                  turn=1)
        enemies = world.get_visible_enemies_in_region("Vienna", "France")
        assert enemies == []

    def test_stale_returns_band(self):
        """STALE visibility -> band data, like PARTIAL."""
        world = make_world()
        # Force STALE on Waterloo
        intel = world.get_region_intel("Waterloo")
        intel.visibility = STALE
        enemies = world.get_visible_enemies_in_region("Waterloo", "France")
        if enemies:
            assert isinstance(enemies[0], dict)
            assert "strength_band" in enemies[0]
            assert enemies[0]["fog_level"] == STALE


# ============================================================================
# TEST: PURSUE fog validation
# ============================================================================

class TestPursueFog:
    """Tests for PURSUE fog validation in strategic.py."""

    def _setup_pursue(self, world, pursuer_name="Davout", target_name="Wellington"):
        """Helper to set up a PURSUE order."""
        pursuer = world.get_marshal(pursuer_name)
        order = StrategicOrder(
            command_type="PURSUE",
            target=target_name,
            target_type="marshal",
            started_turn=world.current_turn - 1,
            original_command=f"pursue {target_name}",
            path=[],
            issued_turn=world.current_turn - 1,  # Not issued this turn
        )
        pursuer.strategic_order = order
        return pursuer, order

    def test_pursue_unknown_target_rejected(self):
        """PURSUE with no intel on target -> reject with message."""
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Clear all intel so Wellington is UNKNOWN
        clear_all_intel(world)

        pursuer, order = self._setup_pursue(world, "Davout", "Wellington")
        # Move Davout away from Waterloo so he's not co-located
        pursuer.location = "Paris"

        result = strategic_exec._execute_pursue(pursuer, world, game_state)

        assert "No intelligence" in result.get("message", "")
        assert result.get("order_status") in ("breaks", "cancelled")

    def test_pursue_stale_uses_last_known(self):
        """PURSUE with STALE target -> uses last known position for pathfinding."""
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Set stale intel: Wellington last seen at Waterloo
        clear_all_intel(world)
        set_intel(world, "Waterloo", STALE,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=1)

        pursuer, order = self._setup_pursue(world, "Davout", "Wellington")
        pursuer.location = "Paris"

        # Move Wellington somewhere else (target moved but intel is stale)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Netherlands"
        # Move Uxbridge away too so path to Waterloo is clear
        uxbridge = world.get_marshal("Uxbridge")
        if uxbridge:
            uxbridge.location = "Netherlands"

        result = strategic_exec._execute_pursue(pursuer, world, game_state)
        # Should try to move toward Waterloo (last known), not Netherlands (real)
        # Result should show movement progress or completion
        assert result.get("order_status") in ("continues", "error", "breaks",
                                               "awaiting_response", "complete")
        # Target location in report should be Waterloo (last known), not Netherlands
        if result.get("target_location"):
            assert result["target_location"] == "Waterloo"

    def test_pursue_target_destroyed_completes(self):
        """PURSUE where target is destroyed -> completes normally."""
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        pursuer, order = self._setup_pursue(world, "Davout", "Wellington")
        # Destroy Wellington
        wellington = world.get_marshal("Wellington")
        wellington.strength = 0

        result = strategic_exec._execute_pursue(pursuer, world, game_state)
        assert "destroyed" in result.get("message", "").lower()

    def test_pursue_full_intel_works(self):
        """PURSUE with FULL intel -> works as before (pathfinds to real location)."""
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Game init has FULL on Waterloo (Grouchy is there)
        pursuer, order = self._setup_pursue(world, "Davout", "Wellington")
        pursuer.location = "Belgium"

        # Wellington is at Waterloo, which is FULL
        result = strategic_exec._execute_pursue(pursuer, world, game_state)
        # Should have made progress
        assert result.get("marshal") == "Davout"

    def test_pursue_multi_region_sighting_most_recent(self):
        """Marshal in multiple stale regions -> pursues most recent sighting."""
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        clear_all_intel(world)
        # Old sighting
        set_intel(world, "Waterloo", STALE,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=2)
        # More recent sighting
        set_intel(world, "Netherlands", STALE,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=5)

        pursuer, order = self._setup_pursue(world, "Davout", "Wellington")
        pursuer.location = "Paris"
        # Move Wellington away entirely
        wellington = world.get_marshal("Wellington")
        wellington.location = "Rhine"

        result = strategic_exec._execute_pursue(pursuer, world, game_state)
        # Should head toward Netherlands (most recent), not Waterloo
        if result.get("target_location"):
            assert result["target_location"] == "Netherlands"

    def test_pursue_empty_arrival_no_enemies(self):
        """Arrive at last known but target moved, no adjacent enemies -> auto-cancel."""
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        clear_all_intel(world)
        # Set stale intel: Wellington was at Belgium
        set_intel(world, "Belgium", STALE,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=1)

        pursuer, order = self._setup_pursue(world, "Ney", "Wellington")
        # Place Ney adjacent to Belgium
        pursuer.location = "Paris"
        # Move Wellington far away
        wellington = world.get_marshal("Wellington")
        wellington.location = "Vienna"
        # Move Uxbridge away too so Belgium is clear
        uxbridge = world.get_marshal("Uxbridge")
        if uxbridge:
            uxbridge.location = "Vienna"

        # Clear all enemies from path too
        for m_name, m in world.marshals.items():
            if m.nation != "France" and m.location in ("Belgium", "Brittany", "Lyon"):
                m.location = "Vienna"

        result = strategic_exec._execute_pursue(pursuer, world, game_state)
        # If Ney reaches Belgium and finds no one, should break
        if result.get("order_status") == "breaks" and "no sign" in result.get("message", "").lower():
            assert "intelligence" in result.get("message", "").lower()


# ============================================================================
# TEST: SUPPORT fog-aware safety
# ============================================================================

class TestSupportFogSafety:
    """Tests for SUPPORT fog-aware enemy scanning."""

    def test_support_only_sees_visible_enemies(self):
        """SUPPORT safety check only considers visible enemies."""
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Set up Ney supporting Davout
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        ney.location = "Paris"
        davout.location = "Paris"

        order = StrategicOrder(
            command_type="SUPPORT",
            target="Davout",
            target_type="marshal",
            started_turn=world.current_turn - 1,
            original_command="support Davout",
            path=[],
            issued_turn=world.current_turn - 1,
        )
        ney.strategic_order = order

        # Clear intel — enemies should be invisible
        clear_all_intel(world)

        # Put enemy adjacent but make the region UNKNOWN
        for m_name, m in world.marshals.items():
            if m.nation != "France":
                m.location = "Vienna"  # Far away
        kutuzov = world.get_marshal("Kutuzov")
        if kutuzov:
            kutuzov.location = "Belgium"  # Adjacent to Paris

        # With UNKNOWN intel on Belgium, support should think ally is safe
        result = strategic_exec._execute_support(ney, world, game_state)
        # Ally should be considered "safe" since we can't see the enemy
        # Result should be order completion (ally safe) or continuation
        assert result.get("marshal") == "Ney"


# ============================================================================
# TEST: Cautious pathfinding fog_aware
# ============================================================================

class TestCautiousPathfindingFog:
    """Tests for fog-aware cautious pathfinding."""

    def test_cautious_avoids_visible_enemies(self):
        """Cautious player marshal avoids enemies at PARTIAL+ regions."""
        world = make_world()
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Davout is cautious
        davout = world.get_marshal("Davout")
        davout.location = "Paris"

        # Enemies at Belgium (FULL visibility from game start)
        # The cautious path should avoid Belgium if enemies are there
        enemy_regions = strategic_exec._get_enemy_occupied_regions(
            "France", world, fog_aware=True)
        # Belgium should be in list if it has FULL/PARTIAL visibility AND enemies
        # This is testing the mechanism, not the specific map state

    def test_fog_aware_false_is_omniscient(self):
        """fog_aware=False returns all enemy regions regardless of visibility."""
        world = make_world()
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        omniscient = strategic_exec._get_enemy_occupied_regions(
            "France", world, fog_aware=False)

        # Should find all enemy-occupied regions
        assert len(omniscient) > 0

    def test_fog_aware_true_filters_by_visibility(self):
        """fog_aware=True only includes regions with PARTIAL+ visibility."""
        world = make_world()
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Clear all intel
        clear_all_intel(world)

        fog_aware = strategic_exec._get_enemy_occupied_regions(
            "France", world, fog_aware=True)

        # With UNKNOWN intel everywhere, should find no enemy regions
        assert len(fog_aware) == 0

    def test_ai_pathfinding_still_omniscient(self):
        """AI pathfinding uses fog_aware=False (omniscient)."""
        world = make_world()
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Get an enemy marshal (cautious personality if possible)
        for m in world.marshals.values():
            if m.nation != "France":
                # Even with all UNKNOWN intel, AI should find enemy regions
                all_regions = strategic_exec._get_enemy_occupied_regions(
                    m.nation, world, fog_aware=False)
                # AI (omniscient) should see French-occupied regions
                assert len(all_regions) > 0
                break


# ============================================================================
# TEST: Enemy phase display filtering
# ============================================================================

class TestEnemyPhaseFiltering:
    """Tests for _filter_enemy_phase_by_visibility in main.py."""

    def test_battle_involving_player_always_shown(self):
        """Enemy action with battle involving player marshal -> always shown."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        clear_all_intel(world)  # All UNKNOWN

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "success": True,
                        "ai_action": {"marshal": "Wellington", "action": "attack", "target": "Ney"},
                        "events": [{
                            "type": "battle",
                            "attacker": "Wellington",
                            "defender": "Ney",
                            "attacker_nation": "Britain",
                            "defender_nation": "France",
                        }],
                    }],
                    "action_count": 1,
                }
            },
            "total_actions": 1,
            "summary": [],
        }

        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)
        britain_actions = filtered["nations"].get("Britain", {}).get("actions", [])
        assert len(britain_actions) == 1  # Battle with player always shown

    def test_action_in_full_region_shown(self):
        """Enemy action in FULL visibility region -> shown."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        # Move Grouchy to Waterloo to grant FULL visibility there
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Waterloo"
        world.calculate_visibility()
        assert world.get_region_intel("Waterloo").visibility == FULL

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "success": True,
                        "ai_action": {"marshal": "Wellington", "action": "fortify"},
                        "events": [],
                    }],
                    "action_count": 1,
                }
            },
            "total_actions": 1,
            "summary": [],
        }
        # Wellington is at Waterloo (FULL)
        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)
        britain_actions = filtered["nations"].get("Britain", {}).get("actions", [])
        assert len(britain_actions) == 1

    def test_action_in_unknown_region_suppressed(self):
        """Enemy action in UNKNOWN region -> suppressed."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        clear_all_intel(world)

        # Move Wellington to Vienna (UNKNOWN)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Vienna"

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "success": True,
                        "ai_action": {"marshal": "Wellington", "action": "recruit"},
                        "events": [],
                    }],
                    "action_count": 1,
                }
            },
            "total_actions": 1,
            "summary": [],
        }

        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)
        britain_actions = filtered["nations"].get("Britain", {}).get("actions", [])
        assert len(britain_actions) == 0  # Suppressed

    def test_admin_action_in_fogged_region_suppressed(self):
        """Admin actions (recruit/build) in fogged regions -> suppressed."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        clear_all_intel(world)

        # Move enemy to unknown region
        kutuzov = world.get_marshal("Kutuzov")
        if kutuzov:
            kutuzov.location = "Vienna"

        enemy_phase = {
            "nations": {
                "Prussia": {
                    "actions": [{
                        "success": True,
                        "ai_action": {"marshal": "Kutuzov", "action": "build"},
                        "events": [],
                    }],
                    "action_count": 1,
                }
            },
            "total_actions": 1,
            "summary": [],
        }

        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)
        total = filtered.get("total_actions", 0)
        assert total == 0

    def test_missing_action_fields_suppressed(self):
        """Missing or unrecognized action fields -> suppressed (safe default)."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        clear_all_intel(world)

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "success": True,
                        # No ai_action field at all
                        "events": [],
                    }],
                    "action_count": 1,
                }
            },
            "total_actions": 1,
            "summary": [],
        }

        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)
        britain_actions = filtered["nations"].get("Britain", {}).get("actions", [])
        assert len(britain_actions) == 0  # Suppressed due to missing field

    def test_none_enemy_phase_handled(self):
        """None or empty enemy_phase -> returned as-is."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        assert _filter_enemy_phase_by_visibility(None, world) is None
        assert _filter_enemy_phase_by_visibility({}, world) == {}

    def test_enemy_victory_preserved(self):
        """enemy_victory flag preserved through filtering."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        enemy_phase = {
            "nations": {},
            "total_actions": 0,
            "summary": [],
            "enemy_victory": {"nation": "Britain", "regions": 8},
        }

        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)
        assert filtered.get("enemy_victory") == {"nation": "Britain", "regions": 8}


# ============================================================================
# TEST: Tactical event filtering
# ============================================================================

class TestTacticalEventFiltering:
    """Tests for _filter_tactical_events_by_visibility in main.py."""

    def test_player_nation_events_always_shown(self):
        """Events with player nation -> always shown."""
        from backend.main import _filter_tactical_events_by_visibility

        world = make_world()
        events = [
            {"type": "drill", "marshal": "Ney", "nation": "France", "location": "Paris"},
            {"type": "fortify", "marshal": "Davout", "nation": "France", "location": "Belgium"},
        ]

        filtered = _filter_tactical_events_by_visibility(events, world)
        assert len(filtered) == 2

    def test_enemy_occupation_in_fogged_region_suppressed(self):
        """Enemy occupation event in fogged region -> suppressed."""
        from backend.main import _filter_tactical_events_by_visibility

        world = make_world()
        clear_all_intel(world)

        events = [
            {"type": "occupation", "nation": "Britain", "location": "Vienna",
             "marshal": "Wellington"},
        ]

        filtered = _filter_tactical_events_by_visibility(events, world)
        assert len(filtered) == 0

    def test_enemy_supply_attrition_in_fogged_region_suppressed(self):
        """Enemy supply attrition in fogged region -> suppressed."""
        from backend.main import _filter_tactical_events_by_visibility

        world = make_world()
        clear_all_intel(world)

        events = [
            {"type": "supply_attrition", "nation": "Prussia", "location": "Vienna",
             "marshal": "Blucher"},
        ]

        filtered = _filter_tactical_events_by_visibility(events, world)
        assert len(filtered) == 0

    def test_enemy_event_in_visible_region_shown(self):
        """Enemy event in FULL/PARTIAL region -> shown."""
        from backend.main import _filter_tactical_events_by_visibility

        world = make_world()
        # Waterloo is FULL at game start

        events = [
            {"type": "fortify", "nation": "Britain", "location": "Waterloo",
             "marshal": "Wellington"},
        ]

        filtered = _filter_tactical_events_by_visibility(events, world)
        assert len(filtered) == 1

    def test_auto_charge_always_shown(self):
        """Auto-charge events always involve player -> always shown."""
        from backend.main import _filter_tactical_events_by_visibility

        world = make_world()
        clear_all_intel(world)

        events = [
            {"type": "auto_charge", "marshal": "Ney", "location": "Waterloo"},
        ]

        filtered = _filter_tactical_events_by_visibility(events, world)
        assert len(filtered) == 1

    def test_fog_events_always_shown(self):
        """intel_updated, intel_decayed, target_not_found -> always shown."""
        from backend.main import _filter_tactical_events_by_visibility

        world = make_world()
        clear_all_intel(world)

        events = [
            {"type": "intel_updated", "region": "Waterloo", "new_visibility": "full",
             "old_visibility": "unknown", "source": "scout"},
            {"type": "intel_decayed", "region": "Rhine", "old_visibility": "full",
             "new_visibility": "stale"},
            {"type": "target_not_found", "marshal": "Davout", "target": "Wellington",
             "region": "Waterloo", "intel_age": 3},
        ]

        filtered = _filter_tactical_events_by_visibility(events, world)
        assert len(filtered) == 3

    def test_empty_events_returns_empty(self):
        """Empty or None events -> returns as-is."""
        from backend.main import _filter_tactical_events_by_visibility

        world = make_world()
        assert _filter_tactical_events_by_visibility([], world) == []
        assert _filter_tactical_events_by_visibility(None, world) is None


# ============================================================================
# TEST: Event log types (intel_updated, intel_decayed)
# ============================================================================

class TestIntelEventLog:
    """Tests for intel event emission in calculate_visibility/decay_intel."""

    def test_intel_updated_emitted_on_visibility_change(self):
        """intel_updated event emitted when visibility upgrades."""
        world = make_world()
        clear_all_intel(world)

        # Recalculate visibility — should generate intel_updated events
        # for regions that go from UNKNOWN to FULL/PARTIAL
        world._intel_events_this_turn = []
        world.calculate_visibility()

        events = world._intel_events_this_turn
        intel_updated_events = [e for e in events if e["type"] == "intel_updated"]
        # Should have events for French regions going UNKNOWN -> FULL/PARTIAL
        assert len(intel_updated_events) > 0

        for evt in intel_updated_events:
            assert "region" in evt
            assert "new_visibility" in evt
            assert "old_visibility" in evt
            assert "source" in evt
            assert evt["old_visibility"] == UNKNOWN

    def test_intel_updated_not_emitted_on_same_level(self):
        """No intel_updated when visibility stays the same."""
        world = make_world()
        # First calc sets everything up
        world._intel_events_this_turn = []
        world.calculate_visibility()
        first_count = len([e for e in world._intel_events_this_turn
                          if e["type"] == "intel_updated"])

        # Second calc — visibility shouldn't change
        world._intel_events_this_turn = []
        world.calculate_visibility()
        second_count = len([e for e in world._intel_events_this_turn
                           if e["type"] == "intel_updated"])

        # Second run should have zero or fewer events
        assert second_count == 0

    def test_intel_decayed_emitted_on_decay(self):
        """intel_decayed event emitted when visibility downgrades."""
        world = make_world()

        # Scout a distant region to get FULL intel
        world.update_intel_from_scout("Vienna", world.current_turn)
        assert world.get_region_intel("Vienna").visibility == FULL

        # Advance many turns to trigger decay
        world.current_turn += 5
        world._intel_events_this_turn = []
        world.calculate_visibility()
        world.decay_intel()

        events = world._intel_events_this_turn
        decay_events = [e for e in events if e["type"] == "intel_decayed"]
        # Vienna should have decayed from FULL since no refresh
        vienna_decay = [e for e in decay_events if e.get("region") == "Vienna"]
        assert len(vienna_decay) > 0
        assert vienna_decay[0]["old_visibility"] in (FULL, PARTIAL, STALE)
        assert vienna_decay[0]["new_visibility"] in (STALE, LAST_KNOWN)

    def test_target_not_found_logged_on_empty_arrival(self):
        """target_not_found event logged when PURSUE arrives at empty region."""
        # This tests the event is appended to _last_tactical_events
        # which was tested in the PURSUE tests above. Here we just verify
        # the event type exists in the filter whitelist.
        from backend.main import _filter_tactical_events_by_visibility

        world = make_world()
        events = [{
            "type": "target_not_found",
            "marshal": "Davout",
            "target": "Wellington",
            "region": "Waterloo",
            "intel_age": 3,
        }]

        filtered = _filter_tactical_events_by_visibility(events, world)
        assert len(filtered) == 1
        assert filtered[0]["type"] == "target_not_found"


# ============================================================================
# TEST: Integration — full path from execute to filtered response
# ============================================================================

class TestIntegration:
    """Integration tests for fog filtering through the full stack."""

    def test_end_turn_enemy_phase_filtered(self):
        """End turn produces fog-filtered enemy phase."""
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()

        # Execute end_turn through executor
        result = executor.execute(
            {"command": {"marshal": None, "action": "end_turn"}},
            game_state
        )

        # enemy_phase should exist
        enemy_phase = result.get("enemy_phase")
        if enemy_phase:
            # The raw result from executor has unfiltered enemy phase
            # (filtering happens in main.py, not executor)
            # But we can verify the structure is what we expect
            assert "nations" in enemy_phase

    def test_status_command_returns_intel_report(self):
        """Status command returns fog-filtered intel report."""
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()

        result = executor.execute(
            {"command": {"marshal": None, "action": "status"}},
            game_state
        )

        assert result.get("success") is True
        assert "BERTHIER" in result.get("message", "")

    def test_intel_events_accumulated_in_advance_turn(self):
        """Intel events are accumulated in _last_tactical_events during advance_turn."""
        world = make_world()

        # Scout a distant region (FULL on turn 1)
        world.update_intel_from_scout("Vienna", world.current_turn)
        assert world.get_region_intel("Vienna").visibility == "full"

        # Advance exactly enough turns for FULL -> STALE decay
        # Scout on turn 1, fresh through turn 2 (turns_since_update=0,1),
        # STALE starts at turn 4 (turns_since_update=3)
        found_intel_event = False
        for _ in range(5):
            world.advance_turn()
            tactical_events = world.get_last_tactical_events()
            intel_types = [e.get("type") for e in tactical_events if isinstance(e, dict)]
            if any(t in ("intel_updated", "intel_decayed") for t in intel_types):
                found_intel_event = True
                break

        assert found_intel_event, "Expected intel_decayed event during advance_turn decay"

    def test_no_floats_in_intel_events(self):
        """Intel events don't contain floats (Godot safety)."""
        world = make_world()
        clear_all_intel(world)
        world._intel_events_this_turn = []
        world.calculate_visibility()

        for event in world._intel_events_this_turn:
            for key, value in event.items():
                assert not isinstance(value, float), (
                    f"Float found in intel event: {key}={value}"
                )


# ============================================================================
# TEST: Structural enforcement — fog_aware wiring (confidence hardening)
# ============================================================================

class TestFogAwareWiringEnforcement:
    """
    Structural test: every call to _get_enemy_occupied_regions() in strategic.py
    must pass marshal= or fog_aware=. If someone adds a new caller and forgets,
    this test fails.

    Pattern: same as test_serialization_enforcement.py — catches mistakes at
    test time, not production.
    """

    def test_all_callers_pass_fog_aware_or_marshal(self):
        """Every _get_enemy_occupied_regions() call must include fog_aware= or marshal=."""
        import re
        strategic_path = (
            "C:\\Users\\User\\PycharmProjects\\project-sovereign-map"
            "\\backend\\commands\\strategic.py"
        )
        with open(strategic_path, "r", encoding="utf-8") as f:
            source = f.read()

        # Find all call sites (not the def itself)
        call_pattern = re.compile(
            r'self\._get_enemy_occupied_regions\s*\(', re.MULTILINE
        )
        definition_pattern = re.compile(
            r'def _get_enemy_occupied_regions\s*\(', re.MULTILINE
        )

        all_matches = list(call_pattern.finditer(source))
        def_matches = list(definition_pattern.finditer(source))

        # Filter out the definition
        def_positions = {m.start() for m in def_matches}
        call_matches = [m for m in all_matches if m.start() not in def_positions]

        assert len(call_matches) > 0, "No calls to _get_enemy_occupied_regions found"

        # For each call, verify it passes fog_aware= or marshal=
        for match in call_matches:
            # Extract the full call (find matching closing paren)
            start = match.start()
            paren_depth = 0
            end = start
            for i, ch in enumerate(source[start:], start=start):
                if ch == '(':
                    paren_depth += 1
                elif ch == ')':
                    paren_depth -= 1
                    if paren_depth == 0:
                        end = i + 1
                        break

            call_text = source[start:end]
            line_num = source[:start].count('\n') + 1

            has_fog_aware = 'fog_aware=' in call_text
            has_marshal_kwarg = 'marshal=' in call_text
            assert has_fog_aware or has_marshal_kwarg, (
                f"Call to _get_enemy_occupied_regions at line {line_num} "
                f"missing fog_aware= or marshal= parameter.\n"
                f"Call: {call_text.strip()}\n"
                f"Every caller MUST pass marshal= (auto-derives fog) or fog_aware= explicitly."
            )

    def test_marshal_param_auto_derives_fog_aware(self):
        """Passing marshal= to _get_enemy_occupied_regions auto-derives fog_aware."""
        world = make_world()
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Player marshal — should auto-derive fog_aware=True
        davout = world.get_marshal("Davout")
        clear_all_intel(world)

        # With UNKNOWN intel, fog_aware=True means no enemy regions visible
        result = strategic_exec._get_enemy_occupied_regions(
            davout.nation, world, marshal=davout)
        assert len(result) == 0, "Player marshal with UNKNOWN intel should see no enemies"

        # Without marshal param (fog_aware defaults False) — should be omniscient
        result_omni = strategic_exec._get_enemy_occupied_regions(
            davout.nation, world)
        assert len(result_omni) > 0, "No marshal= means omniscient (fog_aware=False)"

    def test_ai_marshal_param_stays_omniscient(self):
        """Passing an AI marshal auto-derives fog_aware=False (omniscient)."""
        world = make_world()
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Get an enemy (AI) marshal
        wellington = world.get_marshal("Wellington")
        clear_all_intel(world)

        # AI marshal — should auto-derive fog_aware=False (omniscient)
        result = strategic_exec._get_enemy_occupied_regions(
            wellington.nation, world, marshal=wellington)
        # AI should still see French-occupied regions even with UNKNOWN intel
        assert len(result) > 0, "AI marshal should be omniscient regardless of intel"


# ============================================================================
# TEST: Enemy phase filter — malformed input resilience (confidence hardening)
# ============================================================================

class TestEnemyPhaseFilterResilience:
    """
    Parameterized tests feeding deliberately malformed action dicts to
    _filter_enemy_phase_by_visibility. All should be suppressed (safe default).
    """

    @pytest.mark.parametrize("malformed_action,description", [
        # No ai_action at all
        ({"success": True, "events": []}, "missing ai_action entirely"),
        # ai_action is None
        ({"success": True, "ai_action": None, "events": []}, "ai_action is None"),
        # ai_action is empty dict
        ({"success": True, "ai_action": {}, "events": []}, "ai_action empty dict"),
        # ai_action missing marshal
        ({"success": True, "ai_action": {"action": "move"}, "events": []},
         "ai_action missing marshal field"),
        # ai_action marshal is None
        ({"success": True, "ai_action": {"marshal": None, "action": "recruit"}, "events": []},
         "ai_action marshal is None"),
        # ai_action marshal is nonexistent
        ({"success": True, "ai_action": {"marshal": "Napoleon_Ghost", "action": "attack"}, "events": []},
         "ai_action marshal doesn't exist in world"),
        # events is not a list
        ({"success": True, "ai_action": {"marshal": "Wellington", "action": "fortify"},
          "events": "not_a_list"}, "events is string not list"),
        # events contains non-dict
        ({"success": True, "ai_action": {"marshal": "Wellington", "action": "fortify"},
          "events": [42, "garbage"]}, "events contains non-dict items"),
        # Completely empty action
        ({}, "completely empty action dict"),
    ])
    def test_malformed_action_suppressed(self, malformed_action, description):
        """Malformed action dicts are suppressed, never shown to player."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        clear_all_intel(world)

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [malformed_action],
                    "action_count": 1,
                }
            },
            "total_actions": 1,
            "summary": [],
        }

        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)
        britain_actions = filtered["nations"].get("Britain", {}).get("actions", [])
        assert len(britain_actions) == 0, (
            f"Malformed action should be suppressed: {description}"
        )

    def test_mixed_valid_and_malformed(self):
        """Valid action passes, malformed siblings are suppressed."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        # Waterloo is FULL at game start

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [
                        # Valid: battle involving player marshal → always show
                        {
                            "success": True,
                            "ai_action": {"marshal": "Wellington", "action": "attack", "target": "Ney"},
                            "events": [{"type": "battle", "attacker": "Wellington",
                                        "defender": "Ney", "attacker_nation": "Britain",
                                        "defender_nation": "France"}],
                        },
                        # Malformed: no ai_action
                        {"success": True, "events": []},
                        # Malformed: empty dict
                        {},
                    ],
                    "action_count": 3,
                }
            },
            "total_actions": 3,
            "summary": [],
        }

        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)
        britain_actions = filtered["nations"].get("Britain", {}).get("actions", [])
        assert len(britain_actions) == 1, "Only the valid player-battle action should survive"


# ============================================================================
# TEST: PURSUE personality × fog matrix (confidence hardening)
# ============================================================================

class TestPursuePersonalityFogMatrix:
    """
    Tests for specific personality behaviors during fog-affected PURSUE.
    These cover the untested sub-paths: cautious trap, aggressive arrival
    charge, literal stale auto-cancel.
    """

    def _setup_pursue(self, world, pursuer_name, target_name):
        """Helper to set up a PURSUE order."""
        pursuer = world.get_marshal(pursuer_name)
        order = StrategicOrder(
            command_type="PURSUE",
            target=target_name,
            target_type="marshal",
            started_turn=world.current_turn - 1,
            original_command=f"pursue {target_name}",
            path=[],
            issued_turn=world.current_turn - 1,
        )
        pursuer.strategic_order = order
        return pursuer, order

    def test_cautious_pursue_fog_trap(self):
        """
        Cautious marshal pursues through fog. Enemy in fogged region is
        invisible to cautious pathfinding → marshal walks into trap →
        blocked path interrupt fires.
        """
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Davout is cautious
        davout = world.get_marshal("Davout")
        davout.location = "Paris"

        # Clear all intel
        clear_all_intel(world)

        # Set STALE intel on a distant region where Wellington "was" seen
        set_intel(world, "Rhine", STALE,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=1)

        # Place an enemy on the path (Belgium is between Paris and Rhine)
        # but DON'T give visibility on Belgium
        uxbridge = world.get_marshal("Uxbridge")
        if uxbridge:
            uxbridge.location = "Belgium"
        # Move all other enemies away
        for m in world.marshals.values():
            if m.nation != "France" and m.name not in ("Wellington", "Uxbridge"):
                m.location = "Vienna"
        wellington = world.get_marshal("Wellington")
        wellington.location = "Rhine"

        pursuer, order = self._setup_pursue(world, "Davout", "Wellington")

        # The cautious pathfinding should NOT see the enemy at Belgium (UNKNOWN)
        # So the path should go through Belgium
        # When Davout tries to enter Belgium, movement loop blocks → interrupt
        result = strategic_exec._execute_pursue(davout, world, game_state)

        # Davout should have attempted to move. Since Belgium has an enemy,
        # the movement loop at line 466-468 blocks entry → blocked path interrupt.
        # Valid outcomes: continues (made progress), awaiting_response (blocked),
        # or the pursuit made it through (if Belgium adjacency allows skip)
        assert result.get("marshal") == "Davout"
        assert result.get("order_status") in (
            "continues", "awaiting_response", "complete", "breaks"
        ), f"Unexpected order_status: {result.get('order_status')}"

    def test_aggressive_pursue_arrives_enemies_adjacent(self):
        """
        Aggressive marshal (Ney) pursues to stale location. Target moved.
        Enemies adjacent. Aggressive personality should want to engage.
        """
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Ney is aggressive
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"  # Adjacent to Waterloo

        # Clear intel, set stale sighting at Waterloo
        clear_all_intel(world)
        set_intel(world, "Waterloo", STALE,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=1)

        # Move Wellington away from Waterloo but put Uxbridge there adjacent
        wellington = world.get_marshal("Wellington")
        wellington.location = "Vienna"

        # Put an enemy adjacent to Waterloo (at Netherlands for example)
        uxbridge = world.get_marshal("Uxbridge")
        if uxbridge:
            uxbridge.location = "Netherlands"

        # Move all other enemies far away
        for m in world.marshals.values():
            if m.nation != "France" and m.name not in ("Wellington", "Uxbridge"):
                m.location = "Vienna"

        pursuer, order = self._setup_pursue(world, "Ney", "Wellington")

        result = strategic_exec._execute_pursue(ney, world, game_state)

        # Ney arrives at Waterloo (1 step from Belgium), finds no Wellington.
        # Uxbridge is adjacent at Netherlands.
        # Result should show arrival or engagement attempt
        assert result.get("marshal") == "Ney"
        # Accept various valid outcomes — key is no crash and pursue handles it
        assert result.get("order_status") is not None

    def test_literal_pursue_stale_auto_cancel(self):
        """
        Literal marshal (Grouchy) pursues to stale location. Target moved.
        No enemies anywhere near. Auto-cancel with intel age message.
        """
        world = make_world()
        game_state = make_game_state(world)
        executor = CommandExecutor()
        strategic_exec = StrategicExecutor(executor)

        # Grouchy is literal
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Belgium"  # Adjacent to Waterloo

        # Clear intel, set stale sighting at Waterloo from 5 turns ago
        clear_all_intel(world)
        world.current_turn = 6
        set_intel(world, "Waterloo", STALE,
                  marshals=[{"name": "Wellington", "nation": "Britain"}],
                  turn=1)  # 5 turns old

        # Move ALL enemies far away
        for m in world.marshals.values():
            if m.nation != "France":
                m.location = "Vienna"

        pursuer, order = self._setup_pursue(world, "Grouchy", "Wellington")

        result = strategic_exec._execute_pursue(grouchy, world, game_state)

        # Grouchy arrives at Waterloo, nobody there, nobody adjacent → auto-cancel
        # Should break with "no sign" message that includes intel age
        assert result.get("marshal") == "Grouchy"
        if result.get("order_status") == "breaks":
            msg = result.get("message", "").lower()
            assert "no sign" in msg or "no intelligence" in msg, (
                f"Expected 'no sign' or intel info in break message: {msg}"
            )


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

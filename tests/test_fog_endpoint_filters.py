"""
Test suite for fog of war endpoint filters

Tests _filter_enemy_phase_by_visibility and _filter_tactical_events_by_visibility
from main.py. These functions redact enemy actions that the player shouldn't see.

Coverage targets: main.py lines 100-252
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.intel import RegionIntel, FULL, PARTIAL, STALE, UNKNOWN


def _make_world_with_visibility(region_visibility=None):
    """Create a WorldState with specific region intel visibility levels."""
    world = WorldState()
    if region_visibility:
        for region_name, vis_level in region_visibility.items():
            intel = world.get_region_intel(region_name)
            intel.visibility = vis_level
            intel.last_turn_seen = world.current_turn
    return world


def _filter_enemy_phase(enemy_phase, world):
    """Import and call _filter_enemy_phase_by_visibility."""
    from backend.main import _filter_enemy_phase_by_visibility
    return _filter_enemy_phase_by_visibility(enemy_phase, world)


def _filter_tactical_events(events, world):
    """Import and call _filter_tactical_events_by_visibility."""
    from backend.main import _filter_tactical_events_by_visibility
    return _filter_tactical_events_by_visibility(events, world)


# ═══════════════════════════════════════════════════════════════
# ENEMY PHASE FILTER
# ═══════════════════════════════════════════════════════════════

class TestFilterEnemyPhase:
    """Test _filter_enemy_phase_by_visibility."""

    def test_empty_phase_passthrough(self):
        """Empty or None enemy phase should pass through unchanged."""
        world = WorldState()
        assert _filter_enemy_phase(None, world) is None
        assert _filter_enemy_phase({}, world) == {}

    def test_no_nations_passthrough(self):
        """Enemy phase without nations key should pass through."""
        world = WorldState()
        result = _filter_enemy_phase({"nations": {}}, world)
        assert result["nations"] == {}

    def test_battle_involving_player_always_shown(self):
        """Actions where player marshal is attacker/defender are always visible."""
        world = WorldState()
        player_nation = world.player_nation
        ney = world.get_marshal("Ney")

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "ai_action": {"marshal": "Wellington", "action": "attack", "target": "Ney"},
                        "events": [{
                            "type": "battle",
                            "attacker": "Wellington",
                            "defender": "Ney",
                            "attacker_nation": "Britain",
                            "defender_nation": player_nation,
                        }]
                    }]
                }
            }
        }

        result = _filter_enemy_phase(enemy_phase, world)
        assert len(result["nations"]["Britain"]["actions"]) == 1

    def test_action_in_full_visibility_shown(self):
        """Enemy actions in FULL visibility regions should be visible."""
        world = _make_world_with_visibility({"Waterloo": FULL})

        # Place Wellington in Waterloo (FULL visibility)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "ai_action": {"marshal": "Wellington", "action": "fortify"},
                        "events": []
                    }]
                }
            }
        }

        result = _filter_enemy_phase(enemy_phase, world)
        assert len(result["nations"].get("Britain", {}).get("actions", [])) == 1

    def test_action_in_fogged_region_suppressed(self):
        """Enemy actions in non-FULL visibility should be suppressed."""
        world = _make_world_with_visibility({"Bavaria": STALE})

        wellington = world.get_marshal("Wellington")
        wellington.location = "Bavaria"

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "ai_action": {"marshal": "Wellington", "action": "move"},
                        "events": []
                    }]
                }
            }
        }

        result = _filter_enemy_phase(enemy_phase, world)
        # Should be suppressed — nation may not even appear
        britain_actions = result["nations"].get("Britain", {}).get("actions", [])
        assert len(britain_actions) == 0

    def test_action_in_unknown_region_suppressed(self):
        """Enemy actions in UNKNOWN visibility should be suppressed."""
        world = _make_world_with_visibility({"Bavaria": UNKNOWN})

        wellington = world.get_marshal("Wellington")
        wellington.location = "Bavaria"

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "ai_action": {"marshal": "Wellington", "action": "fortify"},
                        "events": []
                    }]
                }
            }
        }

        result = _filter_enemy_phase(enemy_phase, world)
        britain_actions = result["nations"].get("Britain", {}).get("actions", [])
        assert len(britain_actions) == 0

    def test_mixed_visible_and_fogged_actions(self):
        """Only visible actions should survive filtering."""
        world = _make_world_with_visibility({
            "Waterloo": FULL,
            "Bavaria": STALE,
        })

        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        blucher = world.get_marshal("Blucher")
        blucher.location = "Bavaria"

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [
                        {
                            "ai_action": {"marshal": "Wellington", "action": "fortify"},
                            "events": []
                        },
                        {
                            "ai_action": {"marshal": "Blucher", "action": "move"},
                            "events": []
                        },
                    ]
                }
            }
        }

        result = _filter_enemy_phase(enemy_phase, world)
        actions = result["nations"].get("Britain", {}).get("actions", [])
        # Wellington visible, Blucher fogged
        assert len(actions) == 1

    def test_total_actions_updated(self):
        """total_actions in filtered result should match actual count."""
        world = _make_world_with_visibility({"Waterloo": FULL})
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "ai_action": {"marshal": "Wellington", "action": "fortify"},
                        "events": []
                    }]
                }
            },
            "total_actions": 5  # Original count
        }

        result = _filter_enemy_phase(enemy_phase, world)
        assert result["total_actions"] == len(
            result["nations"].get("Britain", {}).get("actions", [])
        )

    def test_enemy_victory_preserved(self):
        """enemy_victory flag should be preserved through filtering."""
        world = WorldState()
        enemy_phase = {
            "nations": {},
            "enemy_victory": {"winner": "Britain", "message": "You lose!"}
        }

        result = _filter_enemy_phase(enemy_phase, world)
        assert result.get("enemy_victory") == {"winner": "Britain", "message": "You lose!"}

    def test_player_marshal_name_match(self):
        """Battle where player marshal name appears in target should show."""
        world = WorldState()
        ney = world.get_marshal("Ney")

        enemy_phase = {
            "nations": {
                "Britain": {
                    "actions": [{
                        "ai_action": {"marshal": "Wellington", "action": "attack", "target": "Ney"},
                        "events": []
                    }]
                }
            }
        }

        result = _filter_enemy_phase(enemy_phase, world)
        actions = result["nations"].get("Britain", {}).get("actions", [])
        assert len(actions) == 1


# ═══════════════════════════════════════════════════════════════
# TACTICAL EVENTS FILTER
# ═══════════════════════════════════════════════════════════════

class TestFilterTacticalEvents:
    """Test _filter_tactical_events_by_visibility."""

    def test_empty_events_passthrough(self):
        """Empty or None events should pass through."""
        world = WorldState()
        assert _filter_tactical_events(None, world) is None
        assert _filter_tactical_events([], world) == []

    def test_player_nation_events_always_shown(self):
        """Events with player nation are always visible."""
        world = WorldState()
        events = [{"type": "supply_attrition", "nation": world.player_nation, "marshal": "Ney"}]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1

    def test_player_marshal_events_always_shown(self):
        """Events involving a player marshal (by name) are always visible."""
        world = WorldState()
        events = [{"type": "attrition", "marshal": "Davout"}]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1

    def test_auto_charge_always_shown(self):
        """Auto-charge events always shown (involve player)."""
        world = WorldState()
        events = [{"type": "auto_charge", "marshal": "Grouchy"}]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1

    def test_reckless_cavalry_always_shown(self):
        """Reckless cavalry events always shown."""
        world = WorldState()
        events = [{"type": "reckless_cavalry", "marshal": "Grouchy"}]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1

    def test_fog_events_always_shown(self):
        """Intel update/decay events always shown to player."""
        world = WorldState()
        for event_type in ("intel_updated", "intel_decayed", "target_not_found"):
            events = [{"type": event_type, "region": "Bavaria"}]
            result = _filter_tactical_events(events, world)
            assert len(result) == 1, f"{event_type} should always be shown"

    def test_enemy_event_in_visible_region_shown(self):
        """Enemy events in FULL/PARTIAL regions should be visible."""
        world = _make_world_with_visibility({"Waterloo": PARTIAL})

        events = [{
            "type": "fortify",
            "nation": "Britain",
            "marshal": "Wellington",
            "location": "Waterloo"
        }]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1

    def test_enemy_event_in_full_region_shown(self):
        """Enemy events in FULL visibility regions should be visible."""
        world = _make_world_with_visibility({"Waterloo": FULL})

        events = [{
            "type": "move",
            "nation": "Britain",
            "marshal": "Wellington",
            "location": "Waterloo"
        }]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1

    def test_enemy_event_in_fogged_region_suppressed(self):
        """Enemy events in STALE/UNKNOWN regions should be suppressed."""
        world = _make_world_with_visibility({"Bavaria": STALE})

        events = [{
            "type": "fortify",
            "nation": "Britain",
            "marshal": "Wellington",
            "location": "Bavaria"
        }]
        result = _filter_tactical_events(events, world)
        assert len(result) == 0

    def test_enemy_event_no_location_kept(self):
        """Enemy events without a location are kept (can't fog-filter without location)."""
        world = WorldState()

        events = [{
            "type": "unknown",
            "nation": "Britain",
            "marshal": "Wellington"
            # No location or region key — kept as safe default
        }]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1

    def test_non_dict_events_passthrough(self):
        """Non-dict events (strings, etc.) should pass through."""
        world = WorldState()
        events = ["some string event", {"type": "supply", "nation": world.player_nation}]
        result = _filter_tactical_events(events, world)
        assert len(result) == 2

    def test_region_key_also_checked(self):
        """Events with 'region' key (not 'location') should also be checked."""
        world = _make_world_with_visibility({"Waterloo": FULL})

        events = [{
            "type": "occupation",
            "nation": "Britain",
            "marshal": "Wellington",
            "region": "Waterloo"
        }]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1

    def test_enemy_attrition_with_nation_field_suppressed_in_fog(self):
        """Enemy attrition events with nation field should be suppressed in fogged regions."""
        world = _make_world_with_visibility({"Bavaria": STALE})
        events = [{
            "type": "supply_attrition",
            "marshal": "Wellington",
            "nation": "Britain",
            "region": "Bavaria",
            "losses": 1000,
            "message": "Supply shortage at Bavaria: Wellington loses 1,000 troops"
        }]
        result = _filter_tactical_events(events, world)
        assert len(result) == 0, "Enemy attrition in fogged region should be suppressed"

    def test_player_attrition_always_shown(self):
        """Player attrition events should always be shown regardless of visibility."""
        world = WorldState()
        events = [{
            "type": "supply_attrition",
            "marshal": "Ney",
            "nation": "France",
            "region": "Bavaria",
            "losses": 500,
            "message": "Supply shortage at Bavaria: Ney loses 500 troops"
        }]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1, "Player attrition should always be visible"

    def test_enemy_attrition_shown_at_full_visibility(self):
        """Enemy attrition in FULL visibility regions should be shown."""
        world = _make_world_with_visibility({"Bavaria": FULL})
        events = [{
            "type": "supply_attrition",
            "marshal": "Wellington",
            "nation": "Britain",
            "region": "Bavaria",
            "losses": 1000,
            "message": "Supply shortage at Bavaria: Wellington loses 1,000 troops"
        }]
        result = _filter_tactical_events(events, world)
        assert len(result) == 1, "Enemy attrition at FULL visibility should be shown"

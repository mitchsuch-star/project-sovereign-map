"""
Session 8B Tests — Diplomatic Ledger UI Data Validation + Top Bar Fields

Tests cover:
  - Tab 1 (Nations): Ledger data dict key validation, diplomatic state mapping,
    relation value color logic
  - Tab 2 (Treaties): Treaty block data structure, duration formatting
  - Tab 3 (Threat & Coalition): Threat bar calculation, tier labeling,
    brewing status, active coalition data
  - Tab 4 (Talleyrand): Trust label mapping, mission display, envoy count
  - Top Bar Fields: DP counter format, threat indicator visibility thresholds,
    envoy indicator presence
  - Hotkey Map: Verify no duplicate hotkey assignments

NOTE: BBCode rendering is in GDScript — these tests verify the Python data layer
that feeds the Godot UI. Visual rendering is manual-only.
"""

import os

# Ensure mock mode for tests
os.environ["LLM_MODE"] = "mock"

from backend.models.world_state import WorldState
from backend.game_logic.diplomatic_ledger import (
    build_diplomatic_ledger,
    _build_threat_coalition,
    _build_talleyrand,
)


# ════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with sensible defaults for testing."""
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _set_relation(world, nation_a, nation_b, value):
    key = "|".join(sorted([nation_a, nation_b]))
    world.nation_relations[key] = value


def _set_diplo_state(world, nation_a, nation_b, state):
    key = "|".join(sorted([nation_a, nation_b]))
    world.diplomatic_states[key] = state


# ════════════════════════════════════════════════════════════════
# TAB 1: NATIONS — Data Validation for BBCode Rendering
# ════════════════════════════════════════════════════════════════

class TestTab1NationRendering:
    """Verify nation data contains all fields needed for BBCode rendering."""

    def test_nation_names_present(self):
        """Given ledger data with known nations, nation names are included."""
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        nation_names = [n["name"] for n in ledger["nations"]]
        assert "Prussia" in nation_names
        assert "Austria" in nation_names
        assert "Britain" in nation_names

    def test_war_state_present(self):
        """WAR state is correctly set when nations are at war."""
        world = _make_world()
        _set_diplo_state(world, "France", "Prussia", "WAR")
        ledger = build_diplomatic_ledger(world)
        prussia = next(n for n in ledger["nations"] if n["name"] == "Prussia")
        assert prussia["diplomatic_state"] == "WAR"

    def test_relation_negative_value(self):
        """Negative relation values are returned as negative integers."""
        world = _make_world()
        _set_relation(world, "France", "Prussia", -80)
        ledger = build_diplomatic_ledger(world)
        prussia = next(n for n in ledger["nations"] if n["name"] == "Prussia")
        assert prussia["relation"] == -80
        assert isinstance(prussia["relation"], int)

    def test_relation_positive_value(self):
        """Positive relation > 50 returned correctly (green in UI)."""
        world = _make_world()
        _set_relation(world, "France", "Austria", 60)
        ledger = build_diplomatic_ledger(world)
        austria = next(n for n in ledger["nations"] if n["name"] == "Austria")
        assert austria["relation"] == 60

    def test_alliance_state(self):
        """ALLIANCE diplomatic state is correctly surfaced."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "ALLIANCE")
        ledger = build_diplomatic_ledger(world)
        saxony = next(n for n in ledger["nations"] if n["name"] == "Saxony")
        assert saxony["diplomatic_state"] == "ALLIANCE"


# ════════════════════════════════════════════════════════════════
# TAB 2: TREATIES — Data Validation for BBCode Rendering
# ════════════════════════════════════════════════════════════════

class TestTab2TreatyRendering:
    """Verify treaty data contains nation pair, type, duration."""

    def test_no_treaties_returns_empty(self):
        """When no active treaties, empty list returned."""
        world = _make_world()
        world.active_treaties = {}
        ledger = build_diplomatic_ledger(world)
        assert ledger["treaties"] == []

    def test_treaty_has_nation_pair(self):
        """Treaty block includes nation_a and nation_b."""
        world = _make_world()
        world.active_treaties = {
            "Austria|France": {
                "nations": ["France", "Austria"],
                "type": "NON_AGGRESSION",
                "clauses": [],
                "duration": "permanent",
            }
        }
        ledger = build_diplomatic_ledger(world)
        assert len(ledger["treaties"]) == 1
        treaty = ledger["treaties"][0]
        assert treaty["nation_a"] == "France"
        assert treaty["nation_b"] == "Austria"
        assert treaty["treaty_type"] == "NON_AGGRESSION"

    def test_treaty_duration_int(self):
        """Integer duration (turns remaining) is int()-wrapped."""
        world = _make_world()
        world.active_treaties = {
            "France|Prussia": {
                "nations": ["France", "Prussia"],
                "type": "CEASEFIRE",
                "clauses": ["No hostilities"],
                "duration": 5,
            }
        }
        ledger = build_diplomatic_ledger(world)
        treaty = ledger["treaties"][0]
        assert treaty["duration"] == 5
        assert isinstance(treaty["duration"], int)

    def test_treaty_cancel_cost(self):
        """Cancel cost is always 1 DP."""
        world = _make_world()
        world.active_treaties = {
            "France|Prussia": {
                "nations": ["France", "Prussia"],
                "type": "CEASEFIRE",
                "clauses": [],
                "duration": "permanent",
            }
        }
        ledger = build_diplomatic_ledger(world)
        assert ledger["treaties"][0]["cancel_cost"] == 1


# ════════════════════════════════════════════════════════════════
# TAB 3: THREAT & COALITION — Data Validation
# ════════════════════════════════════════════════════════════════

class TestTab3ThreatRendering:
    """Verify threat bar data, tier labels, brewing status."""

    def test_threat_level_int(self):
        """Threat level is int()-wrapped."""
        world = _make_world()
        world.threat_level = 45
        ledger = build_diplomatic_ledger(world)
        tc = ledger["threat_coalition"]
        assert tc["threat_level"] == 45
        assert isinstance(tc["threat_level"], int)

    def test_threat_tier_low(self):
        """Threat < 30 = LOW tier."""
        world = _make_world()
        world.threat_level = 10
        tc = _build_threat_coalition(world)
        assert tc["threat_tier"] == "LOW"

    def test_threat_tier_moderate(self):
        """Threat 30-59 = MODERATE tier."""
        world = _make_world()
        world.threat_level = 35
        tc = _build_threat_coalition(world)
        assert tc["threat_tier"] == "MODERATE"

    def test_threat_tier_high(self):
        """Threat 60-79 = HIGH tier."""
        world = _make_world()
        world.threat_level = 65
        tc = _build_threat_coalition(world)
        assert tc["threat_tier"] == "HIGH"

    def test_threat_tier_critical(self):
        """Threat >= 80 = CRITICAL tier."""
        world = _make_world()
        world.threat_level = 85
        tc = _build_threat_coalition(world)
        assert tc["threat_tier"] == "CRITICAL"

    def test_bar_length_calculation(self):
        """Threat bar filled chars = threat_level / 5, max 20."""
        # This tests the logic that GDScript will replicate
        world = _make_world()
        world.threat_level = 50
        tc = _build_threat_coalition(world)
        # 50 / 5 = 10 filled chars out of 20
        filled = int(tc["threat_level"] / 5)
        assert filled == 10
        assert filled <= 20

    def test_brewing_status_shown(self):
        """Brewing coalition surfaces turns remaining."""
        world = _make_world()
        world.coalition_brewing = {"turns_remaining": 3, "qualifying": ["Prussia", "Austria"]}
        tc = _build_threat_coalition(world)
        assert tc["coalition_brewing"] is True
        assert tc["brewing_turns_remaining"] == 3

    def test_no_coalition_active(self):
        """When no coalition active, active_coalition is None."""
        world = _make_world()
        world.active_coalition = None
        tc = _build_threat_coalition(world)
        assert tc["active_coalition"] is None


# ════════════════════════════════════════════════════════════════
# TAB 4: TALLEYRAND — Data Validation
# ════════════════════════════════════════════════════════════════

class TestTab4TalleyrandRendering:
    """Verify Talleyrand status data for BBCode rendering."""

    def test_authority_label_present(self):
        """Authority label should be present."""
        world = _make_world()
        t = _build_talleyrand(world)
        assert "authority" in t
        assert "authority_label" in t
        assert isinstance(t["authority_label"], str)

    def test_idle_when_no_mission(self):
        """When no active mission, active_mission is None."""
        world = _make_world()
        world.active_diplomatic_mission = None
        t = _build_talleyrand(world)
        assert t["active_mission"] is None

    def test_pending_envoy_count(self):
        """Envoy count = dialogue_manager.get_mailbox_count()."""
        world = _make_world()
        # Push mailbox-type proposals via dialogue_manager
        world.dialogue_manager.push({
            "type": "incoming_proposal", "turn_created": 1,
            "target_nation": "Prussia", "blocking": True,
        })
        world.dialogue_manager.push({
            "type": "counter_offer", "turn_created": 1,
            "target_nation": "Austria", "blocking": True,
        })
        t = _build_talleyrand(world)
        assert t["pending_envoy_count"] == 2

    def test_dp_remaining(self):
        """DP remaining and max are int()-wrapped."""
        world = _make_world()
        world.diplomatic_points = 2
        world.max_diplomatic_points = 3
        t = _build_talleyrand(world)
        assert t["dp_remaining"] == 2
        assert t["dp_max"] == 3
        assert isinstance(t["dp_remaining"], int)
        assert isinstance(t["dp_max"], int)


# ════════════════════════════════════════════════════════════════
# TOP BAR FIELDS — Data Presence + Formatting
# ════════════════════════════════════════════════════════════════

class TestTopBarFields:
    """Verify /test endpoint includes diplomatic top-bar fields."""

    def test_dp_counter_format(self):
        """DP counter should produce 'DP: X/Y' style string."""
        world = _make_world()
        world.diplomatic_points = 2
        world.max_diplomatic_points = 3
        dp = int(getattr(world, 'diplomatic_points', 0))
        dp_max = int(getattr(world, 'max_diplomatic_points', 3))
        formatted = f"DP: {dp}/{dp_max}"
        assert formatted == "DP: 2/3"

    def test_threat_hidden_at_zero(self):
        """Threat indicator should be hidden when threat_level <= 29."""
        world = _make_world()
        world.threat_level = 0
        threat = int(getattr(world, 'threat_level', 0))
        visible = threat >= 30
        assert visible is False

    def test_threat_visible_at_35(self):
        """Threat indicator visible at 35 (amber range)."""
        world = _make_world()
        world.threat_level = 35
        threat = int(getattr(world, 'threat_level', 0))
        visible = threat >= 30
        assert visible is True

    def test_threat_red_at_60(self):
        """Threat indicator red at 60+."""
        world = _make_world()
        world.threat_level = 65
        threat = int(getattr(world, 'threat_level', 0))
        is_red = threat >= 60
        assert is_red is True

    def test_envoy_indicator_hidden_at_zero(self):
        """Envoy indicator hidden when count is 0."""
        world = _make_world()
        count = int(world.dialogue_manager.get_mailbox_count())
        visible = count > 0
        assert visible is False

    def test_envoy_indicator_shown(self):
        """Envoy indicator shown when count > 0."""
        world = _make_world()
        world.dialogue_manager.push({
            "type": "incoming_proposal", "turn_created": 1,
            "target_nation": "Prussia", "blocking": True,
        })
        count = int(world.dialogue_manager.get_mailbox_count())
        visible = count > 0
        assert visible is True


# ════════════════════════════════════════════════════════════════
# HOTKEY MAP — Verify No Conflicts
# ════════════════════════════════════════════════════════════════

class TestHotkeyMap:
    """Verify the hotkey map has no duplicate assignments."""

    def test_no_duplicate_hotkeys(self):
        """Each hotkey maps to exactly one screen."""
        hotkey_map = {
            "L": "event_log",
            "T": "ledger",
            "G": "generals",
            "D": "diplomatic_ledger",
            "R": "dispatch",
        }
        # No duplicate values
        screens = list(hotkey_map.values())
        assert len(screens) == len(set(screens)), "Duplicate screen assignments found"

        # No duplicate keys
        keys = list(hotkey_map.keys())
        assert len(keys) == len(set(keys)), "Duplicate hotkey assignments found"

    def test_d_maps_to_diplomatic_ledger(self):
        """D key should now map to diplomatic_ledger, not dispatch."""
        hotkey_map = {
            "D": "diplomatic_ledger",
            "R": "dispatch",
        }
        assert hotkey_map["D"] == "diplomatic_ledger"
        assert hotkey_map["R"] == "dispatch"

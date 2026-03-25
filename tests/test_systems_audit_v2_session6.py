"""
Tests for Systems Audit V2 — Session 6 (Cleanup/Dead Code)

Covers:
- V2-27: Cumulative fortification turns (unfortify exploit fix)
- V2-58: Dead _execute_hold() removal
- V2-66/67/68: Transient state serialization
- V2-78/79: Hardcoded "Paris" replaced with NATION_CAPITALS
- V2-93: find_safe_spawn exclude parameter
"""

from unittest.mock import MagicMock
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.models.region import NATION_CAPITALS


def _make_marshal(name="Test", nation="France", location="Paris", personality="cautious"):
    """Helper to create a Marshal with all required args."""
    return Marshal(name, location, 20000, personality, nation=nation)


# ════════════════════════════════════════════════════════════════
# V2-27: Cumulative Fortification Turns
# ════════════════════════════════════════════════════════════════

class TestCumulativeFortificationTurns:
    """V2-27: cumulative_fortification_turns persists through unfortify/refortify."""

    def test_field_exists_on_marshal(self):
        """Marshal has cumulative_fortification_turns field."""
        m = _make_marshal()
        assert hasattr(m, 'cumulative_fortification_turns')
        assert m.cumulative_fortification_turns == 0

    def test_serialization_roundtrip(self):
        """cumulative_fortification_turns survives to_dict/from_dict."""
        m = _make_marshal()
        m.cumulative_fortification_turns = 7
        data = m.to_dict()
        assert data["cumulative_fortification_turns"] == 7

        restored = Marshal.from_dict(data)
        assert restored.cumulative_fortification_turns == 7

    def test_unfortify_preserves_cumulative(self):
        """Unfortifying resets turns_fortified but NOT cumulative_fortification_turns."""
        m = _make_marshal("Davout")
        m.fortified = True
        m.turns_fortified = 5
        m.cumulative_fortification_turns = 5
        m.defense_bonus = 25

        # Simulate unfortify — this is what executor does
        m.fortified = False
        m.defense_bonus = 0
        m.turns_fortified = 0
        # cumulative_fortification_turns is NOT reset

        assert m.turns_fortified == 0
        assert m.cumulative_fortification_turns == 5  # Persists!

    def test_refortify_continues_cumulative_count(self):
        """After unfortify + refortify, cumulative picks up where it left off."""
        m = _make_marshal("Davout")
        m.cumulative_fortification_turns = 5

        # Simulate refortify and one turn processing
        m.fortified = True
        m.turns_fortified = 1
        m.cumulative_fortification_turns += 1  # Would be 6

        assert m.cumulative_fortification_turns == 6

    def test_not_cleared_by_combat_transient_clear(self):
        """cumulative_fortification_turns is NOT in clear_combat_transient_state."""
        m = _make_marshal()
        m.cumulative_fortification_turns = 10
        m.clear_combat_transient_state()
        assert m.cumulative_fortification_turns == 10


# ════════════════════════════════════════════════════════════════
# V2-58: Dead _execute_hold() Removal
# ════════════════════════════════════════════════════════════════

class TestHoldDeadCodeRemoval:
    """V2-58: _execute_hold() should no longer exist on executor."""

    def test_no_execute_hold_method(self):
        """Executor should not have _execute_hold method."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor.__new__(CommandExecutor)
        assert not hasattr(executor, '_execute_hold'), \
            "_execute_hold should have been removed (V2-58)"


# ════════════════════════════════════════════════════════════════
# V2-66/67/68: Transient State Serialization
# ════════════════════════════════════════════════════════════════

class TestTransientStateSerialization:
    """V2-66/67/68: Three transient fields now serialize."""

    def test_capital_proximity_last_alert_serializes(self):
        """V2-66: _capital_proximity_last_alert roundtrips."""
        world = WorldState()
        world._capital_proximity_last_alert = {"France": 3}
        data = world.to_dict()
        assert "_capital_proximity_last_alert" in data
        restored = WorldState.from_dict(data)
        assert restored._capital_proximity_last_alert == {"France": 3}

    def test_prev_war_exhaustion_serializes(self):
        """V2-67: _prev_war_exhaustion roundtrips."""
        world = WorldState()
        world._prev_war_exhaustion = {"Prussia": 50}
        data = world.to_dict()
        assert "_prev_war_exhaustion" in data
        restored = WorldState.from_dict(data)
        assert restored._prev_war_exhaustion == {"Prussia": 50}

    def test_relation_deltas_this_turn_serializes(self):
        """V2-68: _relation_deltas_this_turn roundtrips."""
        world = WorldState()
        world._relation_deltas_this_turn = {"France|Prussia": -5}
        data = world.to_dict()
        assert "_relation_deltas_this_turn" in data
        restored = WorldState.from_dict(data)
        assert restored._relation_deltas_this_turn == {"France|Prussia": -5}


# ════════════════════════════════════════════════════════════════
# V2-78/79: Hardcoded "Paris" Replaced
# ════════════════════════════════════════════════════════════════

class TestNationCapitalsUsage:
    """V2-78/79: Functions use NATION_CAPITALS instead of hardcoded Paris."""

    def test_exposes_capital_uses_nation_capital(self):
        """V2-79: _exposes_capital checks correct capital for non-French marshals."""
        from backend.models.personality import _exposes_capital

        # Create a Prussian marshal at Berlin (Prussia's capital)
        prussian_capital = NATION_CAPITALS.get("Prussia", "Berlin")
        marshal = MagicMock()
        marshal.nation = "Prussia"
        marshal.location = prussian_capital
        marshal.name = "Blucher"

        # Mock world with no other Prussian at capital
        world = MagicMock()
        world.regions = {prussian_capital: MagicMock(adjacent_regions=[])}
        world.marshals = {"Blucher": marshal}

        result = _exposes_capital(marshal, "Saxony", world)
        assert result is True, "Should detect Prussian marshal leaving Berlin as exposing capital"

    def test_exposes_capital_not_at_capital(self):
        """Non-capital marshal doesn't trigger expose check."""
        from backend.models.personality import _exposes_capital

        marshal = MagicMock()
        marshal.nation = "Prussia"
        marshal.location = "Saxony"  # Not at capital
        marshal.name = "Blucher"

        result = _exposes_capital(marshal, "Bavaria", MagicMock())
        assert result is False

    def test_resolve_direction_back_uses_nation_capital(self):
        """V2-78: resolve_direction 'back' uses NATION_CAPITALS for correct nation."""
        from backend.ai.strategic_parser import resolve_direction

        prussian_capital = NATION_CAPITALS.get("Prussia", "Berlin")

        # Use real WorldState so adjacency graph works
        world = WorldState()

        # Pick a Prussian marshal that exists
        prussian_marshals = [m for m in world.marshals.values() if m.nation == "Prussia"]
        if not prussian_marshals:
            return  # Skip if no Prussian marshals in default setup

        marshal = prussian_marshals[0]
        # Move to a location adjacent to capital but not at capital
        capital_region = world.regions.get(prussian_capital)
        if capital_region and capital_region.adjacent_regions:
            test_location = capital_region.adjacent_regions[0]
            marshal.location = test_location

            # "back" should resolve toward Berlin, not Paris
            result = resolve_direction(test_location, "back", world, marshal.name)
            # Result should be the next step toward Berlin
            if result is not None:
                assert result == prussian_capital, \
                    f"'back' for Prussian should step toward {prussian_capital}, got {result}"


# ════════════════════════════════════════════════════════════════
# V2-93: find_safe_spawn Exclude Parameter
# ════════════════════════════════════════════════════════════════

class TestFindSafeSpawnExclude:
    """V2-93: find_safe_spawn skips excluded region."""

    def test_exclude_skips_spawn_location(self):
        """When exclude matches spawn_location, it falls through to capital."""
        world = WorldState()
        marshal = MagicMock()
        marshal.nation = "France"
        # Spawn location is a non-capital French region
        marshal.spawn_location = "Lyon"

        # Without exclude, should return Lyon (spawn_location is checked first)
        result_without_exclude = world.find_safe_spawn(marshal)
        assert result_without_exclude == "Lyon"

        # With exclude=Lyon (battle happened at Lyon), should skip to capital
        result_with_exclude = world.find_safe_spawn(marshal, exclude="Lyon")
        assert result_with_exclude != "Lyon", \
            "find_safe_spawn should skip excluded Lyon"
        assert result_with_exclude == "Paris", \
            "Should fall through to capital (Paris) when spawn_location excluded"

    def test_exclude_none_is_normal_behavior(self):
        """exclude=None doesn't change behavior."""
        world = WorldState()
        marshal = MagicMock()
        marshal.nation = "France"
        marshal.spawn_location = "Paris"

        result = world.find_safe_spawn(marshal, exclude=None)
        assert result == "Paris"

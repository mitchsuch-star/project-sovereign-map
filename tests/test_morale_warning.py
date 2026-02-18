"""
Test suite for morale warning on recruitment (Session 31).

When recruiting drops morale below thresholds, the result message
should include [WARNING] or [DANGER] labels.
"""

import pytest
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _setup():
    """Create a fresh world and executor for testing."""
    world = WorldState()
    game_state = {"world": world}
    executor = CommandExecutor()
    return world, game_state, executor


def _get_french_marshal_in_stable_region(world):
    """Find a French infantry marshal in a stable, French-controlled region.

    Prefers infantry marshals for consistent 10k recruit math in morale tests.
    """
    for m in world.marshals.values():
        if m.nation == "France" and not getattr(m, 'cavalry', False):
            region = world.regions.get(m.location)
            if region and region.controller == "France" and region.stability > 50:
                return m, region
    # Fallback to any French marshal
    for m in world.marshals.values():
        if m.nation == "France":
            region = world.regions.get(m.location)
            if region and region.controller == "France" and region.stability > 50:
                return m, region
    return None, None


# ════════════════════════════════════════════════════════════════════════════════
# MORALE WARNING TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestMoraleWarning:
    """Test morale warning/danger labels on recruitment."""

    def test_no_warning_when_morale_stays_high(self):
        """No warning when post-recruit morale is >= 40%."""
        world, gs, executor = _setup()
        marshal, region = _get_french_marshal_in_stable_region(world)
        assert marshal is not None, "Need a French marshal in stable region"

        # High morale — dilution won't drop below 40%
        marshal.morale = 80
        marshal.strength = 30000
        world.nation_gold["France"] = 5000

        result = executor._execute_recruit({"marshal": marshal.name}, gs)
        assert result["success"] is True
        assert "[WARNING]" not in result["message"]
        assert "[DANGER]" not in result["message"]

    def test_warning_when_morale_drops_below_40(self):
        """[WARNING] shown when post-recruit morale is between 25-39%."""
        world, gs, executor = _setup()
        marshal, region = _get_french_marshal_in_stable_region(world)
        assert marshal is not None

        # Set up so dilution lands between 25% and 39%
        # 5000 troops at 40% morale + 10000 recruits at 40% = 40% (no warning)
        # 5000 troops at 50% morale + 10000 recruits at 40% = 43% (no warning)
        # 5000 troops at 30% morale + 10000 recruits at 40% = 36% (WARNING)
        marshal.morale = 30
        marshal.strength = 5000
        world.nation_gold["France"] = 5000

        result = executor._execute_recruit({"marshal": marshal.name}, gs)
        assert result["success"] is True
        assert "[WARNING]" in result["message"]
        assert "[DANGER]" not in result["message"]

    def test_danger_when_morale_drops_below_25(self):
        """[DANGER] shown when post-recruit morale drops below 25%."""
        world, gs, executor = _setup()
        marshal, region = _get_french_marshal_in_stable_region(world)
        assert marshal is not None

        # Very low morale: 5000 troops at 10% + 10000 recruits at 40% = 30%
        # Need even lower: 1000 troops at 5% + 10000 recruits at 40% ~= 36% (still too high)
        # With no training ground, recruits are 40%. Hard to get below 25% since
        # recruits bring morale UP from very low values.
        # Use 20000 troops at 15% + 10000 recruits at 40% = (300000+400000)/30000 = 23%
        marshal.morale = 15
        marshal.strength = 20000
        world.nation_gold["France"] = 5000

        result = executor._execute_recruit({"marshal": marshal.name}, gs)
        assert result["success"] is True
        assert "[DANGER]" in result["message"]
        assert "[WARNING]" not in result["message"]  # DANGER takes priority

    def test_morale_shown_in_message(self):
        """Morale transition is shown in result message."""
        world, gs, executor = _setup()
        marshal, region = _get_french_marshal_in_stable_region(world)
        assert marshal is not None

        marshal.morale = 70
        marshal.strength = 20000
        world.nation_gold["France"] = 5000

        result = executor._execute_recruit({"marshal": marshal.name}, gs)
        assert result["success"] is True
        assert "Morale:" in result["message"]
        assert "->" in result["message"]

    def test_warning_not_triggered_at_exactly_40(self):
        """Morale of exactly 40% does not trigger warning."""
        world, gs, executor = _setup()
        marshal, region = _get_french_marshal_in_stable_region(world)
        assert marshal is not None

        # Need new_morale to land exactly at 40
        # old_strength * old_morale + 10000 * 40 = (old_strength + 10000) * 40
        # Any old_morale of 40 with any strength should land at 40
        marshal.morale = 40
        marshal.strength = 20000
        world.nation_gold["France"] = 5000

        result = executor._execute_recruit({"marshal": marshal.name}, gs)
        assert result["success"] is True
        assert "[WARNING]" not in result["message"]
        assert "[DANGER]" not in result["message"]

    def test_danger_not_triggered_at_exactly_25(self):
        """Morale of exactly 25% triggers WARNING not DANGER."""
        world, gs, executor = _setup()
        marshal, region = _get_french_marshal_in_stable_region(world)
        assert marshal is not None

        # Need new_morale to land at 25
        # (S * M + 10000 * 40) / (S + 10000) = 25
        # S * M + 400000 = 25S + 250000
        # S * M = 25S - 150000
        # M = 25 - 150000/S
        # For S=10000: M = 25 - 15 = 10
        marshal.morale = 10
        marshal.strength = 10000
        world.nation_gold["France"] = 5000

        result = executor._execute_recruit({"marshal": marshal.name}, gs)
        assert result["success"] is True
        # At exactly 25, < 25 is False, so [DANGER] not triggered but < 40 is True
        assert "[WARNING]" in result["message"]
        assert "[DANGER]" not in result["message"]

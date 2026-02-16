"""
Home Territory Supply Bonus Tests

Tests the 1.5x supply capacity bonus for marshals in their own nation's territory.
Covers: mixed nations same region, neutral regions, controller changes, edge cases.

Run with: pytest tests/test_home_territory_supply.py -v
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal


class TestHomeSupplyBonusBasic:
    """Test basic home territory supply bonus behavior."""

    def setup_method(self):
        self.world = WorldState()
        # Isolate test: move all marshals to their capitals so they don't interfere
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.location = "Paris"
                m.strength = 10000
            elif m.nation == "Britain":
                m.location = "London"
                m.strength = 10000
            else:
                m.location = "Berlin"
                m.strength = 10000

    def test_home_territory_no_attrition_under_15x_cap(self):
        """Marshal at home should use 1.5x capacity — no attrition if within that."""
        # Belgium: town, plains. Base capacity = 20000 * 1.0 = 20000
        # Home 1.5x = 30000
        belgium = self.world.get_region("Belgium")
        belgium.controller = "France"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 25000  # Over base 20k but under 1.5x = 30k

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 0, "Home marshal under 1.5x cap should take no attrition"

    def test_away_territory_attrition_above_base_cap(self):
        """Marshal in enemy territory should use base capacity — attrition above base."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"  # Enemy territory for France

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 25000  # Over base 20k

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) > 0, "Invading marshal over base cap should take attrition"

    def test_home_vs_away_differential(self):
        """Same region, same troop count — invader should take more attrition."""
        # Test invader
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 25000
        ney_original = ney.strength

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        invader_losses = sum(e["losses"] for e in ney_events)

        # Reset and test defender
        ney.strength = 25000
        belgium.controller = "France"

        events2 = self.world.process_supply_attrition()
        ney_events2 = [e for e in events2 if e.get("marshal") == "Ney"]
        defender_losses = sum(e["losses"] for e in ney_events2)

        assert invader_losses > defender_losses


class TestMixedNationsSameRegion:
    """Test supply attrition when multiple nations share a region."""

    def setup_method(self):
        self.world = WorldState()
        # Isolate: put everyone in their capitals
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.location = "Paris"
                m.strength = 5000
            elif m.nation == "Britain":
                m.location = "London"
                m.strength = 5000
            else:
                m.location = "Berlin"
                m.strength = 5000

    def test_invader_takes_more_attrition_than_defender(self):
        """In same region, defender gets 1.5x cap, invader gets base cap."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "France"

        # French defender
        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 15000

        # British invader
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 15000

        # Total = 30000, base cap = 20000, home cap = 30000
        # Ney (home): total 30000 <= home cap 30000 -> no attrition
        # Wellington (away): total 30000 > base cap 20000, excess = 50% -> 3% attrition
        events = self.world.process_supply_attrition()

        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        wellington_events = [e for e in events if e.get("marshal") == "Wellington"]

        assert len(ney_events) == 0, "Home defender under 1.5x cap should not suffer"
        assert len(wellington_events) > 0, "Invader over base cap should suffer"

    def test_both_nations_invading_neutral(self):
        """When both nations are in non-home territory, both use base cap."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Prussia"  # Neither France nor Britain

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 15000

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 15000

        # Total = 30000, base cap = 20000 for both
        # Both excess 50% -> 3% attrition each
        events = self.world.process_supply_attrition()

        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        wellington_events = [e for e in events if e.get("marshal") == "Wellington"]

        assert len(ney_events) > 0
        assert len(wellington_events) > 0


class TestSupplyAttritionTiers:
    """Test the three attrition tiers with home territory bonus."""

    def setup_method(self):
        self.world = WorldState()
        for m in self.world.marshals.values():
            m.location = "Paris"
            m.strength = 5000

    def test_tier1_1pct_attrition(self):
        """0-25% excess over capacity -> 1% attrition."""
        # Belgium base cap = 20000. We want 0-25% excess = 20001 to 25000
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"  # Away territory for French

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 24000  # 20% excess (4000/20000)

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 1
        # 1% of 24000 = 240
        assert ney_events[0]["losses"] == 240

    def test_tier2_3pct_attrition(self):
        """25-50% excess over capacity -> 3% attrition."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 28000  # 40% excess (8000/20000)

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 1
        # 3% of 28000 = 840
        assert ney_events[0]["losses"] == 840

    def test_tier3_5pct_attrition(self):
        """>50% excess over capacity -> 5% attrition."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 35000  # 75% excess (15000/20000)

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 1
        # 5% of 35000 = 1750
        assert ney_events[0]["losses"] == 1750

    def test_home_territory_shifts_tier_down(self):
        """Home territory bonus should shift excess calculation down a tier."""
        # Belgium base cap = 20000, home cap = 30000
        belgium = self.world.get_region("Belgium")
        belgium.controller = "France"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 35000  # Away: 75% excess -> tier 3 (5%)
        # Home: total 35000 vs cap 30000 = 16.7% excess -> tier 1 (1%)

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 1
        # 1% of 35000 = 350 (home territory), NOT 5% = 1750
        assert ney_events[0]["losses"] == 350

    def test_no_attrition_under_capacity(self):
        """Under capacity -> 0 attrition regardless of territory."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 15000  # Under 20k base cap

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 0


class TestSupplyEdgeCases:
    """Test edge cases in supply attrition."""

    def setup_method(self):
        self.world = WorldState()
        for m in self.world.marshals.values():
            m.location = "Paris"
            m.strength = 5000

    def test_zero_strength_marshal_no_attrition(self):
        """Marshal with 0 strength should not generate events."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 0

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 0

    def test_no_controller_region_skipped(self):
        """Regions with no controller should be skipped."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = None

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 50000

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 0

    def test_strength_never_goes_negative(self):
        """Marshal strength should never go below 0 after attrition."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 100  # Very small, 5% = 5

        # Need to make total exceed capacity
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 50000  # Push total over cap

        events = self.world.process_supply_attrition()
        assert ney.strength >= 0

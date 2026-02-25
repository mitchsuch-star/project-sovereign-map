"""
Home Territory Supply Bonus Tests

Tests the 1.5x supply capacity bonus for marshals in their own nation's territory.
Covers: mixed nations same region, neutral regions, controller changes, edge cases.

Run with: pytest tests/test_home_territory_supply.py -v
"""

from backend.models.world_state import WorldState


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
        # Belgium: town, plains. Base capacity = 25000 * 1.0 = 25000
        # Home 1.5x = 37500
        belgium = self.world.get_region("Belgium")
        belgium.controller = "France"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 30000  # Over base 25k but under 1.5x = 37500

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 0, "Home marshal under 1.5x cap should take no attrition"

    def test_away_territory_attrition_above_base_cap(self):
        """Marshal in enemy territory should use base capacity — attrition above base."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"  # Enemy territory for France

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 30000  # Over base 25k

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) > 0, "Invading marshal over base cap should take attrition"

    def test_home_vs_away_differential(self):
        """Same region, same troop count — invader should take more attrition."""
        # Test invader — need strength > base cap (25000) to trigger attrition
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 40000  # Over base 25k (away) and over home 37500 (home)

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        invader_losses = sum(e["losses"] for e in ney_events)

        # Reset and test defender
        ney.strength = 40000
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

        # Total = 30000, base cap = 25000, home cap = 37500
        # Ney (home): total 30000 <= home cap 37500 -> no attrition
        # Wellington (away): total 30000 > base cap 25000, excess_ratio = 0.2 -> continuous attrition
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

        # Total = 30000, base cap = 25000 for both
        # Both excess_ratio = 0.2 -> continuous attrition each
        events = self.world.process_supply_attrition()

        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        wellington_events = [e for e in events if e.get("marshal") == "Wellington"]

        assert len(ney_events) > 0
        assert len(wellington_events) > 0


class TestSupplyAttritionContinuous:
    """Test the continuous attrition formula with home territory bonus."""

    def setup_method(self):
        self.world = WorldState()
        for m in self.world.marshals.values():
            m.location = "Paris"
            m.strength = 5000

    def test_small_excess_continuous_attrition(self):
        """Small excess over capacity: continuous formula scales smoothly."""
        # Belgium base cap = 25000 (away territory for French)
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 30000  # excess_ratio = (30000-25000)/25000 = 0.2
        # attrition = min(0.03, 0.2 * 0.015) = 0.003
        # losses = int(30000 * 0.003) = 90

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 1
        assert ney_events[0]["losses"] == 90

    def test_moderate_excess_continuous_attrition(self):
        """Moderate excess: attrition scales proportionally."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 40000  # excess_ratio = (40000-25000)/25000 = 0.6
        # attrition = min(0.03, 0.6 * 0.015) = 0.009
        # losses = int(40000 * 0.009) = 360

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 1
        assert ney_events[0]["losses"] == 360

    def test_severe_excess_hits_attrition_cap(self):
        """Extreme excess hits the 3% attrition cap."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 80000  # excess_ratio = (80000-25000)/25000 = 2.2
        # attrition = min(0.03, 2.2 * 0.015) = 0.03 (capped)
        # losses = int(80000 * 0.03) = 2400

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 1
        assert ney_events[0]["losses"] == 2400

    def test_home_territory_reduces_attrition(self):
        """Home territory 1.5x bonus reduces attrition vs away territory."""
        # Belgium base cap = 25000, home cap = 37500
        belgium = self.world.get_region("Belgium")
        belgium.controller = "France"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 45000
        # Home: excess_ratio = (45000-37500)/37500 = 0.2
        # attrition = min(0.03, 0.2 * 0.015) = 0.003
        # losses = int(45000 * 0.003) = 135
        # (Away would be: excess_ratio = 0.8, attrition = 0.012, losses = 540)

        events = self.world.process_supply_attrition()
        ney_events = [e for e in events if e.get("marshal") == "Ney"]
        assert len(ney_events) == 1
        assert ney_events[0]["losses"] == 135

    def test_no_attrition_under_capacity(self):
        """Under capacity -> 0 attrition regardless of territory."""
        belgium = self.world.get_region("Belgium")
        belgium.controller = "Britain"

        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 20000  # Under 25k base cap

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

"""
Tests for Phase 6.2.F: Supply Limits, Movement Attrition, Contested Capture.

Covers:
- Supply capacity (region.py)
- Supply attrition (world_state.py)
- Movement attrition (executor.py)
- Contested city capture / occupation (executor.py, world_state.py, marshal.py)
"""

import pytest
from unittest.mock import patch

from backend.models.region import Region, SUPPLY_BY_TYPE
from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.combat import CombatResolver


# ============================================================================
# HELPERS
# ============================================================================

def fresh_world() -> WorldState:
    """Create a fresh WorldState for testing."""
    world = WorldState(player_nation="France")
    return world


def make_executor():
    """Create an executor with combat resolver."""
    return CommandExecutor()


def make_game_state(world):
    """Wrap world in game_state dict."""
    return {"world": world}


# ============================================================================
# SUPPLY CAPACITY TESTS
# ============================================================================

class TestSupplyCapacity:
    """Test Region.supply_capacity computed property."""

    def test_capital_supply_capacity(self):
        """Capital (urban terrain) should have highest base capacity."""
        world = fresh_world()
        paris = world.get_region("Paris")
        # capital = 50000 * urban 1.2 = 60000
        assert paris.supply_capacity == 60000

    def test_major_city_supply_capacity(self):
        """Major city supply capacity from type + terrain."""
        world = fresh_world()
        vienna = world.get_region("Vienna")
        # major_city = 40000 * urban 1.2 = 48000
        assert vienna.supply_capacity == 48000

    def test_city_supply_capacity(self):
        """City supply capacity."""
        world = fresh_world()
        milan = world.get_region("Milan")
        # city = 30000 * urban 1.2 = 36000
        assert milan.supply_capacity == 36000

    def test_town_supply_capacity(self):
        """Town supply capacity."""
        world = fresh_world()
        belgium = world.get_region("Belgium")
        # town = 20000 * plains 1.0 = 20000
        assert belgium.supply_capacity == 20000

    def test_rural_supply_capacity(self):
        """Rural supply capacity."""
        world = fresh_world()
        netherlands = world.get_region("Netherlands")
        # rural = 15000 * plains 1.0 = 15000
        assert netherlands.supply_capacity == 15000

    def test_mountains_reduce_supply(self):
        """Mountain terrain halves supply capacity."""
        world = fresh_world()
        geneva = world.get_region("Geneva")
        # town = 20000 * mountains 0.5 = 10000
        assert geneva.supply_capacity == 10000

    def test_supply_depot_adds_capacity(self):
        """Supply depot building adds 10,000 to base before terrain modifier."""
        world = fresh_world()
        paris = world.get_region("Paris")
        paris.buildings.append({"type": "supply_depot", "damaged": False})
        # capital (50000 + 10000 depot) * urban 1.2 = 72000
        assert paris.supply_capacity == 72000

    def test_damaged_supply_depot_no_bonus(self):
        """Damaged supply depot gives no capacity bonus."""
        world = fresh_world()
        paris = world.get_region("Paris")
        paris.buildings.append({"type": "supply_depot", "damaged": True})
        # capital 50000 * urban 1.2 = 60000 (no depot bonus)
        assert paris.supply_capacity == 60000

    def test_supply_capacity_not_serialized(self):
        """supply_capacity is computed, not in to_dict() output."""
        region = Region("Test", ["Paris"], terrain="plains", region_type="town")
        data = region.to_dict()
        assert "supply_capacity" not in data


# ============================================================================
# SUPPLY ATTRITION TESTS
# ============================================================================

class TestSupplyAttrition:
    """Test WorldState.process_supply_attrition()."""

    def test_under_capacity_no_losses(self):
        """No attrition when troops are under supply capacity."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        ney.strength = 15000  # Under Belgium's 20000 cap
        events = world.process_supply_attrition()
        supply_events = [e for e in events if e["marshal"] == "Ney"]
        assert len(supply_events) == 0

    def test_at_exact_capacity_no_losses(self):
        """No attrition when troops exactly at supply capacity."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        ney.strength = 20000  # Exactly at Belgium's 20000 cap
        events = world.process_supply_attrition()
        supply_events = [e for e in events if e["marshal"] == "Ney"]
        assert len(supply_events) == 0

    def test_slight_excess_1_percent(self):
        """0-25% excess: 1% attrition."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        # Belgium cap = 20000. 24000 = 20% excess (under 25%)
        ney.strength = 24000
        events = world.process_supply_attrition()
        supply_events = [e for e in events if e["marshal"] == "Ney"]
        assert len(supply_events) == 1
        assert supply_events[0]["losses"] == 240  # 24000 * 0.01

    def test_moderate_excess_3_percent(self):
        """25-50% excess: 3% attrition."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        # Belgium cap = 20000. 28000 = 40% excess (between 25-50%)
        ney.strength = 28000
        events = world.process_supply_attrition()
        supply_events = [e for e in events if e["marshal"] == "Ney"]
        assert len(supply_events) == 1
        assert supply_events[0]["losses"] == 840  # 28000 * 0.03

    def test_severe_excess_5_percent(self):
        """>50% excess: 5% attrition."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        # Belgium cap = 20000. 50000 = 150% excess
        ney.strength = 50000
        events = world.process_supply_attrition()
        supply_events = [e for e in events if e["marshal"] == "Ney"]
        assert len(supply_events) == 1
        assert supply_events[0]["losses"] == 2500  # 50000 * 0.05

    def test_multiple_marshals_combined(self):
        """Multiple marshals in same region count together for supply check."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        # Move both to Belgium (cap 20000)
        ney.strength = 15000
        davout.location = "Belgium"
        davout.strength = 15000
        # Total = 30000, cap = 20000, excess = 50% -> 3% attrition
        events = world.process_supply_attrition()
        belgium_events = [e for e in events if e["region"] == "Belgium"]
        assert len(belgium_events) == 2  # Both marshals affected
        assert belgium_events[0]["losses"] == 450  # 15000 * 0.03
        assert belgium_events[1]["losses"] == 450

    def test_supply_attrition_runs_during_turn(self):
        """Supply attrition runs during turn resolution."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        ney.strength = 50000  # Way over Belgium cap
        old_str = ney.strength
        world.advance_turn()
        # Should have lost troops to supply attrition
        assert ney.strength < old_str

    def test_no_controller_region_skipped(self):
        """Regions with no controller are skipped."""
        world = fresh_world()
        # Find a region with no controller
        for r in world.regions.values():
            r.controller = None
        events = world.process_supply_attrition()
        assert len(events) == 0


# ============================================================================
# MOVEMENT ATTRITION TESTS
# ============================================================================

class TestMovementAttrition:
    """Test movement attrition via _calculate_movement_attrition()."""

    def test_base_attrition_20k_army(self):
        """20k army: ~1% base loss on plains."""
        world = fresh_world()
        executor = make_executor()
        marshal = world.get_marshal("Grouchy")
        marshal.strength = 20000
        # Waterloo is hills terrain (1.2x movement cost)
        result = executor._calculate_movement_attrition(marshal, "Waterloo", world)
        # base = 0.01, size_penalty = 0 (20000 - 20000 = 0), rate = 0.01 * 1.2 = 0.012
        expected = int(20000 * 0.012)
        assert result["march_losses"] == expected
        assert result["harassment_losses"] == 0
        assert result["total_losses"] == expected

    def test_large_army_size_penalty(self):
        """50k army: base + size penalty."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 50000
        # Belgium is plains (1.0x)
        result = executor._calculate_movement_attrition(ney, "Belgium", world)
        # base = 0.01, size_penalty = min(0.02, (50000-20000)/500000) = 0.00006 → 0.06/1000
        # Actually: (30000)/500000 = 0.06, min(0.02, 0.06) = 0.02
        # rate = (0.01 + 0.02) * 1.0 = 0.03
        expected = int(50000 * 0.03)
        assert result["march_losses"] == expected

    def test_small_army_no_size_penalty(self):
        """10k army: no size penalty below 20k."""
        world = fresh_world()
        executor = make_executor()
        marshal = world.get_marshal("Grouchy")
        marshal.strength = 10000
        # Belgium is plains (1.0x)
        result = executor._calculate_movement_attrition(marshal, "Belgium", world)
        # base = 0.01, size_penalty = 0, rate = 0.01
        expected = int(10000 * 0.01)
        assert result["march_losses"] == expected

    def test_mountain_terrain_doubles(self):
        """Mountains have 2.0x movement cost, doubling attrition."""
        world = fresh_world()
        executor = make_executor()
        marshal = world.get_marshal("Grouchy")
        marshal.strength = 20000
        # Geneva is mountains (2.0x)
        result = executor._calculate_movement_attrition(marshal, "Geneva", world)
        expected = int(20000 * 0.01 * 2.0)
        assert result["march_losses"] == expected

    def test_retreat_half_rate(self):
        """Retreat: halved base rate (0.5% vs 1%)."""
        world = fresh_world()
        executor = make_executor()
        marshal = world.get_marshal("Grouchy")
        marshal.strength = 20000
        # Belgium is plains (1.0x)
        result = executor._calculate_movement_attrition(marshal, "Belgium", world, is_retreat=True)
        # base = 0.005, size_penalty = 0, rate = 0.005
        expected = int(20000 * 0.005)
        assert result["march_losses"] == expected

    def test_harassment_through_enemy_fortification(self):
        """Moving through enemy fortified region: +4% harassment."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        # Set Belgium as enemy with fortification
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.buildings.append({"type": "fortification", "damaged": False})
        result = executor._calculate_movement_attrition(ney, "Belgium", world)
        assert result["harassment_losses"] == int(20000 * 0.04)
        assert result["total_losses"] == result["march_losses"] + result["harassment_losses"]

    def test_no_harassment_friendly_fortification(self):
        """No harassment through own fortification."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        belgium = world.get_region("Belgium")
        belgium.controller = "France"
        belgium.buildings.append({"type": "fortification", "damaged": False})
        result = executor._calculate_movement_attrition(ney, "Belgium", world)
        assert result["harassment_losses"] == 0

    def test_no_harassment_damaged_enemy_fortification(self):
        """Damaged enemy fortification: no harassment."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.buildings.append({"type": "fortification", "damaged": True})
        result = executor._calculate_movement_attrition(ney, "Belgium", world)
        assert result["harassment_losses"] == 0

    def test_attrition_reduces_strength(self):
        """Attrition actually reduces marshal strength."""
        world = fresh_world()
        executor = make_executor()
        marshal = world.get_marshal("Grouchy")
        marshal.strength = 20000
        old_str = marshal.strength
        result = executor._calculate_movement_attrition(marshal, "Belgium", world)
        assert marshal.strength == old_str - result["total_losses"]

    def test_strength_cannot_go_below_zero(self):
        """Strength cannot go below 0 from attrition."""
        world = fresh_world()
        executor = make_executor()
        marshal = world.get_marshal("Grouchy")
        marshal.strength = 10  # Tiny army
        result = executor._calculate_movement_attrition(marshal, "Belgium", world)
        assert marshal.strength >= 0

    def test_move_command_applies_attrition(self):
        """Executing a move command applies attrition (message mentions losses)."""
        world = fresh_world()
        executor = make_executor()
        game_state = make_game_state(world)
        ney = world.get_marshal("Ney")
        ney.strength = 50000  # Large army for visible losses
        old_str = ney.strength
        result = executor.execute({
            "command": {
                "marshal": "Ney",
                "action": "move",
                "target": "Paris",
                "_strategic_execution": True,  # Skip AP cost
            }
        }, game_state)
        assert result["success"]
        assert ney.strength < old_str
        assert "lost to march" in result["message"]


# ============================================================================
# CONTESTED CAPTURE (OCCUPATION) TESTS
# ============================================================================

class TestContestedCapture:
    """Test the contested capture / fortification occupation system."""

    def test_unfortified_instant_capture(self):
        """Unfortified region: instant capture (existing behavior)."""
        world = fresh_world()
        executor = make_executor()
        game_state = make_game_state(world)

        # Set Belgium as enemy, no fortification
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        ney = world.get_marshal("Ney")
        ney.strength = 30000

        # Remove enemy marshals from Belgium
        for m_name in list(world.marshals.keys()):
            m = world.marshals[m_name]
            if m.location == "Belgium" and m.nation != "France":
                m.location = "Vienna"  # Move away

        capture_result = executor._attempt_region_capture(
            ney, "Belgium", world, game_state, had_garrison=False)
        assert capture_result["captured"] is True
        assert capture_result["occupation_started"] is False
        assert belgium.controller == "France"

    def test_fortified_empty_starts_1_turn_occupation(self):
        """Empty fortified region: occupation_turns_required = 1."""
        world = fresh_world()
        executor = make_executor()
        game_state = make_game_state(world)

        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.buildings.append({"type": "fortification", "damaged": False})
        ney = world.get_marshal("Ney")

        capture_result = executor._attempt_region_capture(
            ney, "Belgium", world, game_state, had_garrison=False)
        assert capture_result["captured"] is False
        assert capture_result["occupation_started"] is True
        assert capture_result["turns_required"] == 1
        assert ney.occupation_region == "Belgium"
        assert ney.occupation_turns_required == 1
        # Region NOT captured yet
        assert belgium.controller == "Britain"

    def test_fortified_garrisoned_starts_2_turn_occupation(self):
        """Garrisoned fortified region: occupation_turns_required = 2."""
        world = fresh_world()
        executor = make_executor()
        game_state = make_game_state(world)

        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.buildings.append({"type": "fortification", "damaged": False})
        ney = world.get_marshal("Ney")

        capture_result = executor._attempt_region_capture(
            ney, "Belgium", world, game_state, had_garrison=True)
        assert capture_result["captured"] is False
        assert capture_result["occupation_started"] is True
        assert capture_result["turns_required"] == 2
        assert ney.occupation_turns_required == 2

    def test_damaged_fortification_instant_capture(self):
        """Damaged fortification: instant capture (no holdout)."""
        world = fresh_world()
        executor = make_executor()
        game_state = make_game_state(world)

        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.buildings.append({"type": "fortification", "damaged": True})
        ney = world.get_marshal("Ney")

        capture_result = executor._attempt_region_capture(
            ney, "Belgium", world, game_state, had_garrison=False)
        assert capture_result["captured"] is True

    def test_occupation_completes_after_hold(self):
        """Occupation completes and triggers capture after required turns."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.occupation_region = "Belgium"
        ney.occupation_turns_held = 0
        ney.occupation_turns_required = 1
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"

        events = world._process_tactical_states()
        occ_events = [e for e in events if e["type"] == "occupation_complete"]
        assert len(occ_events) == 1
        assert "secured the fortress" in occ_events[0]["message"]
        assert ney.occupation_region is None
        assert belgium.controller == "France"

    def test_occupation_resets_on_leaving(self):
        """Occupation resets if marshal leaves the region."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"  # NOT Belgium
        ney.occupation_region = "Belgium"
        ney.occupation_turns_held = 0
        ney.occupation_turns_required = 2

        events = world._process_tactical_states()
        abandon_events = [e for e in events if e["type"] == "occupation_abandoned"]
        assert len(abandon_events) == 1
        assert ney.occupation_region is None
        assert ney.occupation_turns_held == 0

    def test_occupation_resets_on_forced_retreat(self):
        """Forced retreat clears occupation state."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.occupation_region = "Belgium"
        ney.occupation_turns_held = 1
        ney.occupation_turns_required = 2

        # Create an enemy to force retreat from
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        # Simulate forced retreat (calling the method directly)
        result = executor._apply_forced_retreat_or_break(ney, wellington, world)
        assert ney.occupation_region is None
        assert ney.occupation_turns_held == 0
        assert ney.occupation_turns_required == 0

    def test_marshal_blocked_during_occupation(self):
        """Marshal can't move/attack/drill during occupation."""
        world = fresh_world()
        executor = make_executor()
        game_state = make_game_state(world)
        ney = world.get_marshal("Ney")
        ney.occupation_region = "Belgium"
        ney.occupation_turns_held = 0
        ney.occupation_turns_required = 2

        # Try to move
        result = executor.execute({
            "command": {
                "marshal": "Ney",
                "action": "move",
                "target": "Paris",
            }
        }, game_state)
        assert result["success"] is False
        assert "securing the fortress" in result["message"]

        # Try to attack
        result = executor.execute({
            "command": {
                "marshal": "Ney",
                "action": "attack",
                "target": "Wellington",
            }
        }, game_state)
        assert result["success"] is False
        assert "securing the fortress" in result["message"]

    def test_marshal_can_wait_during_occupation(self):
        """Marshal can wait/end_turn during occupation."""
        world = fresh_world()
        executor = make_executor()
        game_state = make_game_state(world)
        ney = world.get_marshal("Ney")
        ney.occupation_region = "Belgium"

        # End turn should work
        result = executor.execute({
            "command": {
                "action": "end_turn",
            }
        }, game_state)
        assert result["success"]

    def test_ai_marshal_skipped_during_occupation(self):
        """AI marshal with occupation is skipped in evaluation."""
        from backend.ai.enemy_ai import EnemyAI
        world = fresh_world()
        ai = EnemyAI(make_executor())

        wellington = world.get_marshal("Wellington")
        wellington.occupation_region = "Belgium"

        action, priority = ai._evaluate_marshal(wellington, "Britain", world)
        assert action is None
        assert priority == 999

    def test_occupation_fields_serialize_roundtrip(self):
        """Occupation fields survive serialization roundtrip."""
        marshal = Marshal(
            name="Test", location="Belgium", strength=30000,
            personality="aggressive", nation="France"
        )
        marshal.occupation_region = "Belgium"
        marshal.occupation_turns_held = 1
        marshal.occupation_turns_required = 2

        data = marshal.to_dict()
        restored = Marshal.from_dict(data)
        assert restored.occupation_region == "Belgium"
        assert restored.occupation_turns_held == 1
        assert restored.occupation_turns_required == 2

    def test_occupation_continues_event(self):
        """Occupation in progress generates 'continues' event with turns left."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.occupation_region = "Belgium"
        ney.occupation_turns_held = 0
        ney.occupation_turns_required = 2

        events = world._process_tactical_states()
        continue_events = [e for e in events if e["type"] == "occupation_continues"]
        assert len(continue_events) == 1
        assert continue_events[0]["turns_left"] == 1

    def test_occupation_2_turns_completes_on_second(self):
        """2-turn occupation: continues on first tick, completes on second."""
        world = fresh_world()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.occupation_region = "Belgium"
        ney.occupation_turns_held = 0
        ney.occupation_turns_required = 2
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"

        # First tick: continues
        events1 = world._process_tactical_states()
        cont_events = [e for e in events1 if e["type"] == "occupation_continues"]
        assert len(cont_events) == 1
        assert ney.occupation_region == "Belgium"  # Still occupying
        assert belgium.controller == "Britain"  # Not captured yet

        # Second tick: completes
        events2 = world._process_tactical_states()
        complete_events = [e for e in events2 if e["type"] == "occupation_complete"]
        assert len(complete_events) == 1
        assert ney.occupation_region is None
        assert belgium.controller == "France"

    def test_broken_army_clears_occupation(self):
        """Broken army state clears occupation fields."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.occupation_region = "Belgium"
        ney.occupation_turns_held = 1
        ney.occupation_turns_required = 2
        ney.strength = 10000

        # Create enemy that will shatter ney
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"
        wellington.strength = 100000

        # Simulate army breaking (surrounded path)
        # Remove all possible retreats to force break
        for r in world.regions.values():
            r.adjacent_regions = []

        result = executor._apply_forced_retreat_or_break(ney, wellington, world)
        # Marshal should be broken, occupation cleared
        assert ney.occupation_region is None


# ============================================================================
# SERIALIZATION TESTS
# ============================================================================

class TestSerializationIntegration:
    """Make sure new fields don't break serialization."""

    def test_serialization_enforcement_passes(self):
        """The serialization enforcement test still passes."""
        # Import and run the enforcement test
        from tests.test_serialization_enforcement import (
            TestMarshalSerializationEnforcement,
            create_fully_populated_marshal
        )
        test = TestMarshalSerializationEnforcement()
        test.test_all_marshal_fields_serialized()
        test.test_marshal_roundtrip_preserves_all_fields()


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

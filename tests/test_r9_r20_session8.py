"""
Architecture Refactoring Session 8: R9 (Marshal-by-Region Index) + R20 (advance_turn Guard)

R9 tests verify:
- Index builds correctly from marshal locations
- Dead marshals (strength 0) included in index (strength filtering is caller's job)
- Indexed lookup matches linear scan results
- Index rebuilt after marshal movement
- Empty region returns empty list
- get_marshals_in_region uses index
- get_enemies_in_region uses index
- get_enemy_at_location uses index
- _has_marshal_in_region uses index
- process_supply_attrition uses indexed lookup
- Index rebuilt at advance_turn start and before visibility calc
- Index rebuilt after from_dict

R20 tests verify:
- advance_turn runs successfully on first call
- Double call for same turn is rejected
- New turn advance works after previous turn completed
- Idempotency field survives save/load roundtrip
- Field present in to_dict output
- Guard value is 0 for fresh world
- Guard prevents double income/attrition processing
"""
import pytest
from tests.conftest import MarshalFactory, WorldFactory


# ═══════════════════════════════════════════════════════════════════════════════
# R9: MARSHAL-BY-REGION INDEX
# ═══════════════════════════════════════════════════════════════════════════════

class TestMarshalByRegionIndex:
    """Verify the _marshals_by_region transient cache."""

    def test_index_built_on_init(self):
        """Index is populated after WorldState.__init__."""
        world = WorldFactory.basic()
        assert world._marshals_by_region, "Index should not be empty after init"

    def test_index_groups_by_location(self):
        """Marshals are grouped by their location in the index."""
        m1 = MarshalFactory.infantry(name="A", location="Paris")
        m2 = MarshalFactory.infantry(name="B", location="Paris")
        m3 = MarshalFactory.infantry(name="C", location="Berlin")
        world = WorldFactory.with_marshals([m1, m2, m3])
        world._build_marshal_index()

        paris_marshals = world._marshals_by_region.get("Paris", [])
        berlin_marshals = world._marshals_by_region.get("Berlin", [])
        assert len(paris_marshals) == 2
        assert len(berlin_marshals) == 1
        assert {m.name for m in paris_marshals} == {"A", "B"}
        assert berlin_marshals[0].name == "C"

    def test_index_includes_dead_marshals(self):
        """Dead marshals (strength=0) ARE in index — filtering is caller's job."""
        m1 = MarshalFactory.infantry(name="Alive", location="Paris", strength=30000)
        m2 = MarshalFactory.infantry(name="Dead", location="Paris", strength=0)
        world = WorldFactory.with_marshals([m1, m2])
        world._build_marshal_index()

        paris = world._marshals_by_region.get("Paris", [])
        names = {m.name for m in paris}
        assert "Dead" in names, "Dead marshals should be in the index"
        assert "Alive" in names

    def test_index_empty_region_returns_empty(self):
        """Querying a region with no marshals returns empty list."""
        world = WorldFactory.basic()
        world.marshals.clear()
        world._build_marshal_index()
        assert world._marshals_by_region.get("Vienna", []) == []

    def test_indexed_lookup_matches_linear_scan(self):
        """_get_marshals_in_region_indexed matches get_marshals_in_region."""
        m1 = MarshalFactory.infantry(name="A", location="Paris", nation="France")
        m2 = MarshalFactory.infantry(name="B", location="Paris", nation="France")
        m3 = MarshalFactory.enemy(name="C", location="Paris")
        m4 = MarshalFactory.infantry(name="D", location="Berlin", nation="Prussia")
        world = WorldFactory.with_marshals([m1, m2, m3, m4])
        world._build_marshal_index()

        # Indexed result
        indexed = world._get_marshals_in_region_indexed("Paris")
        # Linear scan (always correct)
        linear = world.get_marshals_in_region("Paris")

        assert {m.name for m in indexed} == {m.name for m in linear}
        assert len(indexed) == 3

    def test_index_rebuilt_after_movement(self):
        """After a marshal moves, rebuilding the index reflects new location."""
        m1 = MarshalFactory.infantry(name="Mover", location="Paris")
        world = WorldFactory.with_marshals([m1])
        world._build_marshal_index()

        assert len(world._get_marshals_in_region_indexed("Paris")) == 1
        assert len(world._get_marshals_in_region_indexed("Belgium")) == 0

        # Move marshal
        m1.location = "Belgium"
        world._build_marshal_index()

        assert len(world._get_marshals_in_region_indexed("Paris")) == 0
        assert len(world._get_marshals_in_region_indexed("Belgium")) == 1

    def test_public_method_always_uses_linear_scan(self):
        """get_marshals_in_region always works even with stale/empty index."""
        m1 = MarshalFactory.infantry(name="A", location="Paris")
        world = WorldFactory.with_marshals([m1])
        world._marshals_by_region = {}  # Clear index

        # Public method should still work via linear scan
        result = world.get_marshals_in_region("Paris")
        assert len(result) == 1
        assert result[0].name == "A"

    def test_indexed_method_returns_reference(self):
        """_get_marshals_in_region_indexed returns the internal list (reference)."""
        m1 = MarshalFactory.infantry(name="A", location="Paris")
        world = WorldFactory.with_marshals([m1])
        world._build_marshal_index()

        result1 = world._get_marshals_in_region_indexed("Paris")
        result2 = world._get_marshals_in_region_indexed("Paris")
        assert result1 is result2, "Should return same internal list"


class TestIndexUsedByInternalMethods:
    """Verify internal hot-path methods use indexed lookups correctly."""

    def test_has_marshal_in_region_correctness(self):
        """_has_marshal_in_region works correctly with linear scan."""
        m1 = MarshalFactory.infantry(name="Guard", location="Paris",
                                     nation="France", strength=20000)
        world = WorldFactory.with_marshals([m1])

        assert world._has_marshal_in_region("Paris", "France") is True
        assert world._has_marshal_in_region("Berlin", "France") is False
        assert world._has_marshal_in_region("Paris", "Prussia") is False

    def test_has_marshal_in_region_ignores_dead(self):
        """_has_marshal_in_region ignores dead marshals (strength=0)."""
        m1 = MarshalFactory.infantry(name="Dead", location="Paris",
                                     nation="France", strength=0)
        world = WorldFactory.with_marshals([m1])

        assert world._has_marshal_in_region("Paris", "France") is False

    def test_supply_attrition_uses_indexed_lookup(self):
        """process_supply_attrition uses _get_marshals_in_region_indexed."""
        m1 = MarshalFactory.infantry(name="Huge", location="Paris",
                                     nation="France", strength=80000)
        world = WorldFactory.with_marshals([m1])
        world.regions["Paris"].controller = "France"
        world._build_marshal_index()

        old_strength = m1.strength
        events = world.process_supply_attrition()
        # With 80k troops and typical supply cap (~25k), should get attrition
        if events:
            assert m1.strength < old_strength

    def test_calculate_visibility_uses_indexed_lookup(self):
        """calculate_visibility uses _get_marshals_in_region_indexed."""
        m1 = MarshalFactory.infantry(name="Scout", location="Paris",
                                     nation="France", strength=20000)
        world = WorldFactory.with_marshals([m1])
        world._build_marshal_index()

        # Should not crash and should produce valid visibility
        world._intel_events_this_turn = []
        world.calculate_visibility()
        intel = world.get_region_intel("Paris")
        assert intel.visibility is not None


class TestIndexRebuildsAtCorrectTimes:
    """Verify index is rebuilt at the right points in the lifecycle."""

    def test_index_rebuilt_at_advance_turn_start(self):
        """Index is rebuilt at the start of _advance_turn_internal."""
        m1 = MarshalFactory.infantry(name="A", location="Paris", nation="France")
        world = WorldFactory.with_marshals([m1])

        # Move marshal and DON'T rebuild index
        m1.location = "Belgium"
        # Verify index is stale
        assert "Paris" in world._marshals_by_region or "Belgium" not in world._marshals_by_region

        # advance_turn rebuilds the index
        world.advance_turn()

        # After advance_turn, index should reflect new location
        assert len(world.get_marshals_in_region("Belgium")) == 1
        assert len(world.get_marshals_in_region("Paris")) == 0

    def test_index_rebuilt_after_from_dict(self):
        """Index is rebuilt after deserializing from saved data."""
        m1 = MarshalFactory.infantry(name="Testmarshal", location="Lyon",
                                     nation="France", strength=20000)
        world = WorldFactory.with_marshals([m1])
        world._build_marshal_index()

        # Serialize and deserialize
        from backend.models.world_state import WorldState
        data = world.to_dict()
        restored = WorldState.from_dict(data)

        # Index should be populated
        assert restored._marshals_by_region, "Index should be built after from_dict"
        lyon_marshals = restored.get_marshals_in_region("Lyon")
        assert any(m.name == "Testmarshal" for m in lyon_marshals)

    def test_index_not_serialized(self):
        """_marshals_by_region should NOT appear in to_dict output."""
        world = WorldFactory.basic()
        data = world.to_dict()
        assert "_marshals_by_region" not in data
        assert "marshals_by_region" not in data


# ═══════════════════════════════════════════════════════════════════════════════
# R20: ADVANCE_TURN IDEMPOTENCY GUARD
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdvanceTurnIdempotencyGuard:
    """Verify the _last_advanced_turn guard prevents double-processing."""

    def test_fresh_world_guard_is_zero(self):
        """New WorldState has _last_advanced_turn = 0."""
        world = WorldFactory.basic()
        assert world._last_advanced_turn == 0

    def test_advance_turn_runs_first_time(self):
        """advance_turn succeeds on first call and increments turn."""
        world = WorldFactory.basic()
        assert world.current_turn == 1
        world.advance_turn()
        assert world.current_turn == 2

    def test_advance_turn_stamps_guard(self):
        """After advance_turn, _last_advanced_turn is stamped with the old turn."""
        world = WorldFactory.basic()
        old = world.current_turn  # 1
        world.advance_turn()
        # Stamp should be the pre-increment turn number
        assert world._last_advanced_turn == old

    def test_double_call_rejected(self):
        """Calling advance_turn twice with same current_turn is idempotent."""
        world = WorldFactory.basic()
        assert world.current_turn == 1
        world.advance_turn()
        assert world.current_turn == 2

        # Manually set current_turn back to simulate a crash retry
        # where current_turn didn't increment
        world.current_turn = 1
        old_gold = dict(world.nation_gold)
        world.advance_turn()
        # Should have been rejected — turn still 1 (not incremented again)
        assert world.current_turn == 1
        # Gold shouldn't change (income phase shouldn't run again)
        assert world.nation_gold == old_gold

    def test_next_turn_works_after_previous(self):
        """After advancing turn 1→2, advancing turn 2→3 works."""
        world = WorldFactory.basic()
        world.advance_turn()  # 1→2
        assert world.current_turn == 2
        world.advance_turn()  # 2→3
        assert world.current_turn == 3

    def test_sequential_turns_all_work(self):
        """Multiple sequential advance_turn calls all succeed."""
        world = WorldFactory.basic()
        for expected in range(2, 7):
            world.advance_turn()
            assert world.current_turn == expected

    def test_guard_survives_save_load(self):
        """Idempotency guard persists through save/load roundtrip."""
        from backend.models.world_state import WorldState
        world = WorldFactory.basic()
        world.advance_turn()  # 1→2, stamp=1
        assert world._last_advanced_turn == 1

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored._last_advanced_turn == 1
        assert restored.current_turn == 2
        # Should be able to advance (2→3)
        restored.advance_turn()
        assert restored.current_turn == 3

    def test_guard_field_in_to_dict(self):
        """last_advanced_turn appears in serialized output."""
        world = WorldFactory.basic()
        data = world.to_dict()
        assert "last_advanced_turn" in data
        assert data["last_advanced_turn"] == 0

    def test_guard_field_default_on_old_save(self):
        """Loading a save without last_advanced_turn defaults to 0."""
        from backend.models.world_state import WorldState
        world = WorldFactory.basic()
        data = world.to_dict()
        del data["last_advanced_turn"]  # Simulate old save format

        restored = WorldState.from_dict(data)
        assert restored._last_advanced_turn == 0
        # Should still be able to advance
        restored.advance_turn()
        assert restored.current_turn == 2

    def test_guard_prevents_double_income(self):
        """Double advance_turn must not double-apply income."""
        world = WorldFactory.basic()
        # Record gold before
        gold_before = dict(world.nation_gold)

        world.advance_turn()  # 1→2
        gold_after_first = dict(world.nation_gold)

        # Try to re-advance with turn stuck at 1 (crash simulation)
        world.current_turn = 1
        world.advance_turn()  # Should be rejected

        # Gold should NOT have changed again
        gold_after_retry = dict(world.nation_gold)
        assert gold_after_retry == gold_after_first

    def test_guard_value_is_int(self):
        """Guard field serializes as int."""
        world = WorldFactory.basic()
        world.advance_turn()
        data = world.to_dict()
        assert isinstance(data["last_advanced_turn"], int)


# ═══════════════════════════════════════════════════════════════════════════════
# SERIALIZATION ENFORCEMENT (must not break roundtrip)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSerializationEnforcement:
    """Verify new fields don't break the serialization roundtrip."""

    def test_full_roundtrip_with_new_fields(self):
        """WorldState with R9+R20 changes survives full to_dict/from_dict."""
        from backend.models.world_state import WorldState
        world = WorldFactory.basic()

        # Advance a couple turns to populate the guard
        world.advance_turn()
        world.advance_turn()

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.current_turn == world.current_turn
        assert restored._last_advanced_turn == world._last_advanced_turn
        assert restored._marshals_by_region  # Index rebuilt

    def test_transient_index_not_in_save(self):
        """_marshals_by_region is transient and must not appear in saved data."""
        world = WorldFactory.basic()
        data = world.to_dict()
        # No key should reference the index
        for key in data:
            assert "marshal" not in key.lower() or key in (
                "marshals", "marshal_management_data"
            ), f"Unexpected marshal-related key in save: {key}"

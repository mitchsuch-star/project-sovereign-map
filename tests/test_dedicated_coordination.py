"""
Tests for Dedicated Coordination Bonus (Phase 7, Session 59)

Tests co-location tracking, dedicated bonus Path A (2+ turns co-located)
and Path B (active SUPPORT order), integration with coordination pipeline,
self-balancing, and serialization round-trips.

Spec: docs/MULTI_MARSHAL_SPEC.md §4
Amendments: docs/PHASE7_SPEC_AMENDMENTS.md [A-D3, A-D7]
"""

import pytest
from backend.models.marshal import Marshal, StrategicOrder
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    """Create a marshal with sensible defaults for dedicated coordination tests."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        tactical_skill=7,
        skills=kw.pop("skills", {
            "tactical": 7, "shock": 7, "defense": 7,
            "logistics": 7, "administration": 7, "command": 7,
        }),
        cavalry=cavalry, artillery=artillery,
        spawn_location=kw.pop("spawn_location", location),
        **kw,
    )


def _make_world_with_marshals(marshal_list, current_turn=1):
    """Create a WorldState and replace marshals with the given list."""
    world = WorldState()
    world.marshals.clear()
    for m in marshal_list:
        world.marshals[m.name] = m
    world.current_turn = current_turn
    return world


def _executor():
    return CommandExecutor()


def _advance_co_location(world, n_turns=1):
    """Run co-location tracking for n_turns by calling _update_co_location_tracking and incrementing turn."""
    for _ in range(n_turns):
        world._update_co_location_tracking()
        world.current_turn += 1


# ════════════════════════════════════════════════════════════════════════════════
# CO-LOCATION TRACKING
# ════════════════════════════════════════════════════════════════════════════════

class TestCoLocationTracking:
    """Test that co-location counters start, persist, and reset correctly."""

    def test_co_location_tracking_starts_on_first_shared_turn(self):
        """Two marshals in same region → counter starts with current turn."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=3)

        world._update_co_location_tracking()

        assert a.co_location_turns == {"B": 3}
        assert b.co_location_turns == {"A": 3}

    def test_co_location_counter_persists_across_turns(self):
        """After 2 updates, start_turn stays at original value."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)

        _advance_co_location(world, 2)  # turn 1 → 2 → 3

        # Start turn was recorded as 1 (the first call), not overwritten
        assert a.co_location_turns == {"B": 1}
        assert b.co_location_turns == {"A": 1}

    def test_co_location_resets_on_separation(self):
        """Marshal moves away → counter deleted."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)

        world._update_co_location_tracking()
        assert "B" in a.co_location_turns

        # B moves away
        b.location = "Rhineland"
        world._update_co_location_tracking()

        assert a.co_location_turns == {}
        assert b.co_location_turns == {}

    def test_co_location_dead_marshal_cleared(self):
        """Dead marshal (strength 0) clears all co-location counters."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)

        world._update_co_location_tracking()
        assert "B" in a.co_location_turns

        a.strength = 0
        world._update_co_location_tracking()

        assert a.co_location_turns == {}

    def test_co_location_broken_marshal_not_tracked(self):
        """Broken ally not counted in allies_here."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)

        b.broken = True
        world._update_co_location_tracking()

        assert a.co_location_turns == {}
        assert b.co_location_turns == {}  # B is dead-like, cleared

    def test_co_location_different_nation_excluded(self):
        """Enemy marshals at same location don't count."""
        a = _make_marshal(name="A", location="Paris", nation="France")
        b = _make_marshal(name="B", location="Paris", nation="Prussia")
        world = _make_world_with_marshals([a, b], current_turn=1)

        world._update_co_location_tracking()

        assert a.co_location_turns == {}
        assert b.co_location_turns == {}

    def test_co_location_tracks_multiple_allies(self):
        """Marshal tracks counters for 2+ allies independently."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        c = _make_marshal(name="C", location="Paris")
        world = _make_world_with_marshals([a, b, c], current_turn=1)

        world._update_co_location_tracking()

        assert set(a.co_location_turns.keys()) == {"B", "C"}
        assert set(b.co_location_turns.keys()) == {"A", "C"}
        assert set(c.co_location_turns.keys()) == {"A", "B"}

    def test_co_location_mutual(self):
        """If A tracks B, B also tracks A (symmetric tracking)."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=5)

        world._update_co_location_tracking()

        assert a.co_location_turns["B"] == 5
        assert b.co_location_turns["A"] == 5


# ════════════════════════════════════════════════════════════════════════════════
# TIMING (A-D7)
# ════════════════════════════════════════════════════════════════════════════════

class TestCoLocationTiming:
    """Verify tracking timing relative to turn counter (A-D7)."""

    def test_tracking_runs_before_turn_increment(self):
        """New entries record start_turn = old current_turn value."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=5)

        # Simulate what advance_turn does: call tracking BEFORE increment
        world._update_co_location_tracking()
        assert a.co_location_turns["B"] == 5  # Old value, not 6

        world.current_turn = 6  # Then increment happens

    def test_threshold_fires_at_start_of_third_turn(self):
        """current_turn - start_turn >= 2 fires correctly after 2 full cycles."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)
        ex = _executor()

        # Turn 1: tracking starts (start_turn = 1)
        world._update_co_location_tracking()
        world.current_turn = 2

        # Turn 2: 2 - 1 = 1, not yet
        world._update_co_location_tracking()
        ex._calculate_coordination_context(a, world)
        assert getattr(a, '_display_dedicated_atk', 0.0) == 0.0
        world.current_turn = 3

        # Turn 3: 3 - 1 = 2, threshold met!
        world._update_co_location_tracking()
        ex._calculate_coordination_context(a, world)
        assert a._display_dedicated_atk == pytest.approx(0.05)


# ════════════════════════════════════════════════════════════════════════════════
# DEDICATED BONUS — PATH A (Co-Location Duration)
# ════════════════════════════════════════════════════════════════════════════════

class TestDedicatedBonusPathA:
    """Test Path A: 2+ turns of co-location earns +5%/+5%."""

    def test_no_dedicated_bonus_at_1_turn(self):
        """Co-located 1 turn → no dedicated bonus."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)
        ex = _executor()

        # Turn 1: tracking starts
        world._update_co_location_tracking()
        world.current_turn = 2

        # Turn 2: 2 - 1 = 1, not enough
        world._update_co_location_tracking()
        ex._calculate_coordination_context(a, world)
        assert getattr(a, '_display_dedicated_atk', 0.0) == 0.0
        assert getattr(a, '_display_dedicated_def', 0.0) == 0.0

    def test_dedicated_bonus_at_2_turns(self):
        """Co-located 2+ turns → +5%/+5%."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)
        ex = _executor()

        # Advance through 2 full cycles
        _advance_co_location(world, 2)  # now current_turn = 3

        ex._calculate_coordination_context(a, world)
        assert a._display_dedicated_atk == pytest.approx(0.05)
        assert a._display_dedicated_def == pytest.approx(0.05)

    def test_dedicated_bonus_at_3_plus_turns(self):
        """Still +5%/+5% after 3+ turns (doesn't scale up)."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)
        ex = _executor()

        _advance_co_location(world, 5)  # now current_turn = 6

        ex._calculate_coordination_context(a, world)
        assert a._display_dedicated_atk == pytest.approx(0.05)
        assert a._display_dedicated_def == pytest.approx(0.05)

    def test_dedicated_bonus_value_correct(self):
        """Exactly 0.05 atk and 0.05 def."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)
        ex = _executor()

        _advance_co_location(world, 2)
        ex._calculate_coordination_context(a, world)

        assert a._display_dedicated_atk == 0.05
        assert a._display_dedicated_def == 0.05


# ════════════════════════════════════════════════════════════════════════════════
# DEDICATED BONUS — PATH B (SUPPORT Order)
# ════════════════════════════════════════════════════════════════════════════════

class TestDedicatedBonusPathB:
    """Test Path B: SUPPORT order grants immediate dedicated bonus."""

    def test_support_order_grants_immediate_dedicated(self):
        """Ally has SUPPORT targeting this marshal → +5%/+5% immediately."""
        davout = _make_marshal(name="Davout", location="Paris")
        ney = _make_marshal(name="Ney", location="Paris")
        # Ney has SUPPORT order targeting Davout
        ney.strategic_order = StrategicOrder(
            command_type="SUPPORT",
            target="Davout",
            target_type="marshal",
            started_turn=1,
            original_command="Support Davout",
        )
        world = _make_world_with_marshals([davout, ney], current_turn=1)
        ex = _executor()

        # No co-location time needed — SUPPORT is immediate
        ex._calculate_coordination_context(davout, world)
        assert davout._display_dedicated_atk == pytest.approx(0.05)
        assert davout._display_dedicated_def == pytest.approx(0.05)

    def test_support_one_directional(self):
        """A-D3: SUPPORT Davout gives Davout bonus, NOT the supporter (Ney)."""
        davout = _make_marshal(name="Davout", location="Paris")
        ney = _make_marshal(name="Ney", location="Paris")
        ney.strategic_order = StrategicOrder(
            command_type="SUPPORT",
            target="Davout",
            target_type="marshal",
            started_turn=1,
            original_command="Support Davout",
        )
        world = _make_world_with_marshals([davout, ney], current_turn=1)
        ex = _executor()

        ex._calculate_coordination_context(davout, world)

        # Davout gets the dedicated bonus
        assert davout._display_dedicated_atk == pytest.approx(0.05)

        # Ney does NOT (one-directional, no co-location time either)
        assert getattr(ney, '_display_dedicated_atk', 0.0) == 0.0

    def test_mutual_support_both_get_bonus(self):
        """Both issue SUPPORT → both get dedicated bonus."""
        davout = _make_marshal(name="Davout", location="Paris")
        ney = _make_marshal(name="Ney", location="Paris")
        ney.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Davout",
            target_type="marshal", started_turn=1,
            original_command="Support Davout",
        )
        davout.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney",
            target_type="marshal", started_turn=1,
            original_command="Support Ney",
        )
        world = _make_world_with_marshals([davout, ney], current_turn=1)
        ex = _executor()

        ex._calculate_coordination_context(davout, world)

        assert davout._display_dedicated_atk == pytest.approx(0.05)
        assert ney._display_dedicated_atk == pytest.approx(0.05)

    def test_support_wrong_target_no_bonus(self):
        """Ally has SUPPORT targeting someone else → no dedicated bonus."""
        davout = _make_marshal(name="Davout", location="Paris")
        ney = _make_marshal(name="Ney", location="Paris")
        grouchy = _make_marshal(name="Grouchy", location="Rhineland", personality="literal")
        ney.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Grouchy",
            target_type="marshal", started_turn=1,
            original_command="Support Grouchy",
        )
        world = _make_world_with_marshals([davout, ney, grouchy], current_turn=1)
        ex = _executor()

        ex._calculate_coordination_context(davout, world)
        assert getattr(davout, '_display_dedicated_atk', 0.0) == 0.0


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH COORDINATION PIPELINE
# ════════════════════════════════════════════════════════════════════════════════

class TestDedicatedPipelineIntegration:
    """Test that dedicated bonus integrates with combined arms + per-ally coordination."""

    def test_dedicated_added_to_raw_sum(self):
        """Combined arms + coordination + dedicated all sum together."""
        # 2 unit types → CA: 10% atk, 5% def
        # Professional relationship → coord: 3% atk, 5% def per ally
        # Dedicated: 5% atk, 5% def
        a = _make_marshal(name="A", location="Paris")  # infantry
        b = _make_marshal(name="B", location="Paris", cavalry=True)  # cavalry
        a.set_relationship("B", 0)  # Professional
        world = _make_world_with_marshals([a, b], current_turn=1)
        ex = _executor()

        _advance_co_location(world, 2)  # earn dedicated

        ex._calculate_coordination_context(a, world)
        # Total atk: CA(0.10) + coord(0.03) + dedicated(0.05) = 0.18
        # Total def: CA(0.05) + coord(0.05) + dedicated(0.05) = 0.15
        assert a.total_coordination_attack_bonus == pytest.approx(0.18)
        assert a.total_coordination_defense_bonus == pytest.approx(0.15)

    def test_dedicated_included_in_hard_cap(self):
        """Dedicated pushes total over cap → capped at 25%atk/20%def."""
        # 3 unit types → CA: 15% atk, 10% def
        # Devoted (+2) ally → coord: 4.5% atk, 7.5% def per ally (2 allies = 9%, 15%)
        # Dedicated: 5% atk, 5% def
        # Raw atk = 15 + 9 + 5 = 29% → capped at 25%
        # Raw def = 10 + 15 + 5 = 30% → capped at 20%
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris", cavalry=True)
        c = _make_marshal(name="C", location="Paris", artillery=True)
        a.set_relationship("B", 2)  # Devoted
        a.set_relationship("C", 2)  # Devoted
        world = _make_world_with_marshals([a, b, c], current_turn=1)
        ex = _executor()

        _advance_co_location(world, 2)

        ex._calculate_coordination_context(a, world)
        assert a.total_coordination_attack_bonus == pytest.approx(0.25)  # capped
        assert a.total_coordination_defense_bonus == pytest.approx(0.20)  # capped

    def test_dedicated_display_field_set(self):
        """_display_dedicated_atk/def set correctly."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)
        ex = _executor()

        _advance_co_location(world, 2)
        ex._calculate_coordination_context(a, world)

        assert hasattr(a, '_display_dedicated_atk')
        assert hasattr(a, '_display_dedicated_def')
        assert a._display_dedicated_atk == pytest.approx(0.05)
        assert a._display_dedicated_def == pytest.approx(0.05)

    def test_dedicated_display_field_cleared_after_combat(self):
        """Cleared with other coordination fields."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        world = _make_world_with_marshals([a, b], current_turn=1)
        ex = _executor()

        _advance_co_location(world, 2)
        ex._calculate_coordination_context(a, world)
        assert a._display_dedicated_atk == pytest.approx(0.05)

        # Clear coordination fields (as combat would)
        ex._clear_coordination_fields({"Paris"}, world)

        assert getattr(a, '_display_dedicated_atk', 0.0) == 0.0
        assert getattr(a, '_display_dedicated_def', 0.0) == 0.0


# ════════════════════════════════════════════════════════════════════════════════
# SELF-BALANCING
# ════════════════════════════════════════════════════════════════════════════════

class TestDedicatedSelfBalancing:
    """Test interaction with relationship levels (I2) and solo marshals."""

    def test_hostile_co_location_gets_dedicated_not_coordination(self):
        """I2: Ney+Davout Hostile → +5% dedicated, 0% per-ally coordination."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris")
        a.set_relationship("B", -2)  # Hostile
        world = _make_world_with_marshals([a, b], current_turn=1)
        ex = _executor()

        _advance_co_location(world, 2)
        ex._calculate_coordination_context(a, world)

        # Per-ally coordination: 0% (Hostile scaling = 0.0)
        assert a._display_coordination_atk == pytest.approx(0.0)
        assert a._display_coordination_def == pytest.approx(0.0)
        # Dedicated: +5% (co-location doesn't care about relationship)
        assert a._display_dedicated_atk == pytest.approx(0.05)
        assert a._display_dedicated_def == pytest.approx(0.05)

    def test_solo_marshal_no_dedicated(self):
        """No allies → no dedicated bonus."""
        a = _make_marshal(name="A", location="Paris")
        world = _make_world_with_marshals([a], current_turn=1)
        ex = _executor()

        ex._calculate_coordination_context(a, world)
        assert getattr(a, '_display_dedicated_atk', 0.0) == 0.0
        assert getattr(a, '_display_dedicated_def', 0.0) == 0.0


# ════════════════════════════════════════════════════════════════════════════════
# SERIALIZATION
# ════════════════════════════════════════════════════════════════════════════════

class TestDedicatedSerialization:
    """Test that new persistent fields survive serialization round-trips."""

    def test_co_location_turns_serialization_roundtrip(self):
        """to_dict → from_dict preserves co_location_turns."""
        m = _make_marshal(name="TestMarshal")
        m.co_location_turns = {"Davout": 3, "Ney": 5}

        data = m.to_dict()
        restored = Marshal.from_dict(data)

        assert restored.co_location_turns == {"Davout": 3, "Ney": 5}

    def test_last_relationship_change_turn_serialization_roundtrip(self):
        """to_dict → from_dict preserves last_relationship_change_turn."""
        m = _make_marshal(name="TestMarshal")
        m.last_relationship_change_turn = {"Davout": 7}

        data = m.to_dict()
        restored = Marshal.from_dict(data)

        assert restored.last_relationship_change_turn == {"Davout": 7}

    def test_co_location_turns_default_empty_dict(self):
        """Missing key in save data → defaults to empty dict."""
        m = _make_marshal(name="TestMarshal")
        data = m.to_dict()
        del data["co_location_turns"]

        restored = Marshal.from_dict(data)
        assert restored.co_location_turns == {}

    def test_last_relationship_change_default_empty_dict(self):
        """Missing key in save data → defaults to empty dict."""
        m = _make_marshal(name="TestMarshal")
        data = m.to_dict()
        del data["last_relationship_change_turn"]

        restored = Marshal.from_dict(data)
        assert restored.last_relationship_change_turn == {}

    def test_serialization_enforcement_passes(self):
        """The enforcement test validates new fields are properly wired."""
        # This is a sanity check — the actual enforcement test is in
        # test_serialization_enforcement.py. We verify the fields exist
        # in to_dict output and from_dict restores them.
        m = _make_marshal(name="TestMarshal")
        m.co_location_turns = {"A": 1}
        m.last_relationship_change_turn = {"B": 2}

        data = m.to_dict()
        assert "co_location_turns" in data
        assert "last_relationship_change_turn" in data

        restored = Marshal.from_dict(data)
        assert restored.co_location_turns == {"A": 1}
        assert restored.last_relationship_change_turn == {"B": 2}


# ════════════════════════════════════════════════════════════════════════════════
# BOTH SIDES
# ════════════════════════════════════════════════════════════════════════════════

class TestDedicatedBothSides:
    """Test that attacker and defender each calculate their own dedicated status."""

    def test_attacker_dedicated_independent_of_defender(self):
        """Each side's dedicated bonus is independent."""
        # France: A + B co-located 2+ turns
        a = _make_marshal(name="A", location="Paris", nation="France")
        b = _make_marshal(name="B", location="Paris", nation="France")
        # Prussia: C alone
        c = _make_marshal(name="C", location="Paris", nation="Prussia")

        world = _make_world_with_marshals([a, b, c], current_turn=1)
        ex = _executor()

        _advance_co_location(world, 2)

        ex._calculate_coordination_context(a, world)
        ex._calculate_coordination_context(c, world)

        # A has dedicated bonus (ally B co-located 2+ turns)
        assert a._display_dedicated_atk == pytest.approx(0.05)
        # C has no allies → no dedicated
        assert getattr(c, '_display_dedicated_atk', 0.0) == 0.0

    def test_defender_can_have_dedicated_bonus(self):
        """Defender with 2-turn co-location gets +5%/+5%."""
        d1 = _make_marshal(name="D1", location="Rhineland", nation="Prussia")
        d2 = _make_marshal(name="D2", location="Rhineland", nation="Prussia")
        world = _make_world_with_marshals([d1, d2], current_turn=1)
        ex = _executor()

        _advance_co_location(world, 2)
        ex._calculate_coordination_context(d1, world)

        assert d1._display_dedicated_def == pytest.approx(0.05)

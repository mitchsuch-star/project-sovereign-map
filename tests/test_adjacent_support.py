"""
Tests for Adjacent Support Bonus (Phase 7, Session 60)

Adjacent marshals in neighbouring regions provide +2% attack per ally.
Attack-only (A-M2), not relationship-scaled, purely positional.
Fortified and HOLD marshals count (physically present).

Spec: docs/MULTI_MARSHAL_SPEC.md §5
Amendments: docs/PHASE7_SPEC_AMENDMENTS.md [M3, A-M2]
"""

import pytest
from backend.commands.executor import CommandExecutor
from tests.conftest import MarshalFactory, WorldFactory


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS (delegating to conftest factories)
# ════════════════════════════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    """Create a marshal via MarshalFactory."""
    if cavalry:
        return MarshalFactory.cavalry(name=name, location=location, strength=strength,
                                      personality=personality, nation=nation, **kw)
    if artillery:
        return MarshalFactory.artillery(name=name, location=location, strength=strength,
                                        personality=personality, nation=nation, **kw)
    return MarshalFactory.infantry(name=name, location=location, strength=strength,
                                   personality=personality, nation=nation, **kw)


# Map reference: Paris adjacent to [Normandy, Belgium, Lyon, Bordeaux]
# Belgium adjacent to [Paris, Normandy, Netherlands, Waterloo, Rhine]


# ════════════════════════════════════════════════════════════════════════════════
# ADJACENT COUNT
# ════════════════════════════════════════════════════════════════════════════════

class TestAdjacentCount:
    """Test that adjacent allies are counted correctly."""

    def test_one_adjacent_ally_gives_2_percent(self):
        """1 ally in adjacent region → +2% atk."""
        primary = _make_marshal(name="Ney", location="Paris")
        adjacent = _make_marshal(name="Davout", location="Belgium")  # adjacent to Paris
        world = WorldFactory.with_marshals([primary, adjacent])
        ex = CommandExecutor()

        ctx = ex._calculate_coordination_context(primary, world)

        assert ctx["adjacent_count"] == 1
        assert abs(ctx["adjacent_atk"] - 0.02) < 0.001
        assert primary._display_adjacent_atk == pytest.approx(0.02)

    def test_two_adjacent_allies_gives_4_percent(self):
        """2 allies in adjacent regions → +4% atk."""
        primary = _make_marshal(name="Ney", location="Paris")
        adj1 = _make_marshal(name="Davout", location="Belgium")
        adj2 = _make_marshal(name="Soult", location="Lyon")  # adjacent to Paris
        world = WorldFactory.with_marshals([primary, adj1, adj2])
        ex = CommandExecutor()

        ctx = ex._calculate_coordination_context(primary, world)

        assert ctx["adjacent_count"] == 2
        assert abs(ctx["adjacent_atk"] - 0.04) < 0.001

    def test_three_adjacent_allies_gives_6_percent(self):
        """3 allies in adjacent regions → +6% atk."""
        primary = _make_marshal(name="Ney", location="Paris")
        adj1 = _make_marshal(name="Davout", location="Belgium")
        adj2 = _make_marshal(name="Soult", location="Lyon")
        adj3 = _make_marshal(name="Lannes", location="Bordeaux")  # adjacent to Paris
        world = WorldFactory.with_marshals([primary, adj1, adj2, adj3])
        ex = CommandExecutor()

        ctx = ex._calculate_coordination_context(primary, world)

        assert ctx["adjacent_count"] == 3
        assert abs(ctx["adjacent_atk"] - 0.06) < 0.001

    def test_non_adjacent_ally_excluded(self):
        """Ally 2+ regions away → not counted."""
        primary = _make_marshal(name="Ney", location="Paris")
        # Netherlands is NOT adjacent to Paris (Paris→Belgium→Netherlands)
        far_ally = _make_marshal(name="Davout", location="Netherlands")
        world = WorldFactory.with_marshals([primary, far_ally])
        ex = CommandExecutor()

        ctx = ex._calculate_coordination_context(primary, world)

        assert ctx["adjacent_count"] == 0
        assert ctx["adjacent_atk"] == 0.0

    def test_same_region_ally_not_counted_as_adjacent(self):
        """Co-located ally is in coordination, not adjacent count."""
        primary = _make_marshal(name="Ney", location="Paris")
        colocated = _make_marshal(name="Davout", location="Paris")
        world = WorldFactory.with_marshals([primary, colocated])
        ex = CommandExecutor()

        ctx = ex._calculate_coordination_context(primary, world)

        # Same-region ally should NOT appear in adjacent count
        assert ctx["adjacent_count"] == 0
        assert "Davout" not in ctx.get("adjacent_names", [])


# ════════════════════════════════════════════════════════════════════════════════
# ELIGIBILITY
# ════════════════════════════════════════════════════════════════════════════════

class TestAdjacentEligibility:
    """Test that ineligible marshals are excluded from adjacent count."""

    def test_broken_ally_excluded_from_adjacent(self):
        """Broken marshal not counted."""
        primary = _make_marshal(name="Ney", location="Paris")
        broken = _make_marshal(name="Davout", location="Belgium")
        broken.broken = True
        world = WorldFactory.with_marshals([primary, broken])
        ex = CommandExecutor()

        count, names = ex._count_adjacent_allies("Paris", "France", world)

        assert count == 0
        assert names == []

    def test_retreating_ally_excluded_from_adjacent(self):
        """Retreated_this_turn excluded."""
        primary = _make_marshal(name="Ney", location="Paris")
        retreating = _make_marshal(name="Davout", location="Belgium")
        retreating.retreated_this_turn = True
        world = WorldFactory.with_marshals([primary, retreating])
        ex = CommandExecutor()

        count, names = ex._count_adjacent_allies("Paris", "France", world)

        assert count == 0

    def test_recovering_ally_excluded_from_adjacent(self):
        """Retreat_recovery > 0 excluded."""
        primary = _make_marshal(name="Ney", location="Paris")
        recovering = _make_marshal(name="Davout", location="Belgium")
        recovering.retreat_recovery = 1
        world = WorldFactory.with_marshals([primary, recovering])
        ex = CommandExecutor()

        count, names = ex._count_adjacent_allies("Paris", "France", world)

        assert count == 0

    def test_zero_strength_excluded_from_adjacent(self):
        """Dead ally excluded."""
        primary = _make_marshal(name="Ney", location="Paris")
        dead = _make_marshal(name="Davout", location="Belgium", strength=0)
        world = WorldFactory.with_marshals([primary, dead])
        ex = CommandExecutor()

        count, names = ex._count_adjacent_allies("Paris", "France", world)

        assert count == 0

    def test_enemy_nation_excluded_from_adjacent(self):
        """Different nation not counted."""
        primary = _make_marshal(name="Ney", location="Paris")
        enemy = _make_marshal(name="Wellington", location="Belgium", nation="Britain")
        world = WorldFactory.with_marshals([primary, enemy])
        ex = CommandExecutor()

        count, names = ex._count_adjacent_allies("Paris", "France", world)

        assert count == 0

    def test_fortified_ally_counts_as_adjacent(self):
        """Fortified marshal IS counted (physically present)."""
        primary = _make_marshal(name="Ney", location="Paris")
        fortified = _make_marshal(name="Davout", location="Belgium")
        fortified.fortified = True
        fortified.defense_bonus = 0.10
        world = WorldFactory.with_marshals([primary, fortified])
        ex = CommandExecutor()

        count, names = ex._count_adjacent_allies("Paris", "France", world)

        assert count == 1
        assert "Davout" in names

    def test_hold_ally_counts_as_adjacent(self):
        """HOLD marshal IS counted."""
        primary = _make_marshal(name="Ney", location="Paris")
        holding = _make_marshal(name="Davout", location="Belgium")
        holding.holding_position = True
        world = WorldFactory.with_marshals([primary, holding])
        ex = CommandExecutor()

        count, names = ex._count_adjacent_allies("Paris", "France", world)

        assert count == 1
        assert "Davout" in names


# ════════════════════════════════════════════════════════════════════════════════
# ATTACK-ONLY (A-M2)
# ════════════════════════════════════════════════════════════════════════════════

class TestAttackOnly:
    """Adjacent support is attack-only — no defense component (A-M2)."""

    def test_adjacent_support_is_attack_only(self):
        """Adjacent bonus adds to atk, NOT def."""
        primary = _make_marshal(name="Ney", location="Paris")
        adjacent = _make_marshal(name="Davout", location="Belgium")
        world = WorldFactory.with_marshals([primary, adjacent])
        ex = CommandExecutor()

        ex._calculate_coordination_context(primary, world)

        # Attack should include adjacent bonus
        assert primary.total_coordination_attack_bonus >= 0.02
        # Defense should NOT include adjacent bonus (only combined arms and coordination)
        # With no co-located allies, defense should be 0
        assert primary.total_coordination_defense_bonus == 0.0

    def test_defender_gets_no_adjacent_bonus(self):
        """Adjacent support is attack-only — defender's total_coordination_defense_bonus
        should not increase from adjacent allies being present."""
        defender = _make_marshal(name="Wellington", location="Paris", nation="Britain")
        adj_ally = _make_marshal(name="Blucher", location="Belgium", nation="Britain")
        world = WorldFactory.with_marshals([defender, adj_ally])
        ex = CommandExecutor()

        ex._calculate_coordination_context(defender, world)

        # Defender's defense bonus should be 0 (no same-region allies, no CA)
        assert defender.total_coordination_defense_bonus == 0.0
        # But attack bonus should include adjacent support
        assert defender._display_adjacent_atk == pytest.approx(0.02)


# ════════════════════════════════════════════════════════════════════════════════
# NOT RELATIONSHIP-SCALED
# ════════════════════════════════════════════════════════════════════════════════

class TestNotRelationshipScaled:
    """Adjacent support is purely positional — not affected by relationships."""

    def test_adjacent_not_scaled_by_relationship(self):
        """Hostile adjacent ally gives same +2% as Devoted."""
        primary = _make_marshal(name="Ney", location="Paris")
        hostile_adj = _make_marshal(name="Davout", location="Belgium")
        # Set hostile relationship — should not affect adjacent bonus
        primary.relationships = {"Davout": "Hostile"}
        world = WorldFactory.with_marshals([primary, hostile_adj])
        ex = CommandExecutor()

        count, names = ex._count_adjacent_allies("Paris", "France", world)

        assert count == 1
        assert abs(count * 0.02 - 0.02) < 0.001


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH PIPELINE
# ════════════════════════════════════════════════════════════════════════════════

class TestPipelineIntegration:
    """Test that adjacent bonus integrates correctly with the coordination pipeline."""

    def test_adjacent_added_to_coordination_sum(self):
        """CA + coordination + adjacent all sum correctly."""
        # Infantry + cavalry in Paris (2/3 CA = 10% atk / 5% def)
        inf = _make_marshal(name="Ney", location="Paris")
        cav = _make_marshal(name="Murat", location="Paris", cavalry=True)
        # Adjacent ally
        adj = _make_marshal(name="Davout", location="Belgium")
        world = WorldFactory.with_marshals([inf, cav, adj])
        ex = CommandExecutor()

        ex._calculate_coordination_context(inf, world)

        # CA = 10% atk, adjacent = 2% atk → at least 12% total atk
        assert inf.total_coordination_attack_bonus >= 0.12
        assert inf._display_combined_arms_atk == pytest.approx(0.10)
        assert inf._display_adjacent_atk == pytest.approx(0.02)

    def test_adjacent_included_in_hard_cap(self):
        """Total exceeds 25% atk → capped."""
        # 3/3 CA = 20% atk + 3 adjacent × 2% = 6% → 26% → capped to 25%
        inf = _make_marshal(name="Ney", location="Paris")
        cav = _make_marshal(name="Murat", location="Paris", cavalry=True)
        art = _make_marshal(name="Drouot", location="Paris", artillery=True)
        adj1 = _make_marshal(name="Davout", location="Belgium")
        adj2 = _make_marshal(name="Soult", location="Lyon")
        adj3 = _make_marshal(name="Lannes", location="Bordeaux")
        world = WorldFactory.with_marshals([inf, cav, art, adj1, adj2, adj3])
        ex = CommandExecutor()

        ex._calculate_coordination_context(inf, world)

        # 20% CA + 6% adjacent = 26% → capped to 25%
        assert inf.total_coordination_attack_bonus == pytest.approx(0.25)

    def test_adjacent_display_field_set(self):
        """_display_adjacent_atk set correctly on all eligible marshals."""
        m1 = _make_marshal(name="Ney", location="Paris")
        m2 = _make_marshal(name="Murat", location="Paris", cavalry=True)
        adj = _make_marshal(name="Davout", location="Belgium")
        world = WorldFactory.with_marshals([m1, m2, adj])
        ex = CommandExecutor()

        ex._calculate_coordination_context(m1, world)

        # Both marshals in Paris should have same adjacent display value
        assert m1._display_adjacent_atk == pytest.approx(0.02)
        assert m2._display_adjacent_atk == pytest.approx(0.02)

    def test_adjacent_cleared_after_combat(self):
        """Transient field cleared by _clear_coordination_fields."""
        m = _make_marshal(name="Ney", location="Paris")
        adj = _make_marshal(name="Davout", location="Belgium")
        world = WorldFactory.with_marshals([m, adj])
        ex = CommandExecutor()

        ex._calculate_coordination_context(m, world)
        assert m._display_adjacent_atk == pytest.approx(0.02)

        # Clear fields
        ex._clear_coordination_fields({"Paris"}, world)
        assert getattr(m, '_display_adjacent_atk', 0.0) == 0.0


# ════════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ════════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases for adjacent support bonus."""

    def test_no_adjacent_allies_zero_bonus(self):
        """Solo marshal with no adjacent allies → 0 bonus."""
        solo = _make_marshal(name="Ney", location="Paris")
        world = WorldFactory.with_marshals([solo])
        ex = CommandExecutor()

        ctx = ex._calculate_coordination_context(solo, world)

        assert ctx["adjacent_count"] == 0
        assert ctx["adjacent_atk"] == 0.0
        assert solo._display_adjacent_atk == 0.0

    def test_adjacent_same_for_all_region_marshals(self):
        """All marshals in battle region get same adjacent count (not relationship-dependent)."""
        m1 = _make_marshal(name="Ney", location="Paris")
        m2 = _make_marshal(name="Murat", location="Paris", cavalry=True)
        adj = _make_marshal(name="Davout", location="Belgium")
        world = WorldFactory.with_marshals([m1, m2, adj])
        ex = CommandExecutor()

        ex._calculate_coordination_context(m1, world)

        # Both marshals should have same adjacent bonus
        assert m1._display_adjacent_atk == m2._display_adjacent_atk

    def test_full_france_stack_with_adjacent(self):
        """3/3 CA + coordination + dedicated + 2 adjacent → verify cap."""
        # Build a big stack: 3 types in Paris + 2 adjacent
        inf = _make_marshal(name="Ney", location="Paris")
        cav = _make_marshal(name="Murat", location="Paris", cavalry=True)
        art = _make_marshal(name="Drouot", location="Paris", artillery=True)
        adj1 = _make_marshal(name="Davout", location="Belgium")
        adj2 = _make_marshal(name="Soult", location="Lyon")
        world = WorldFactory.with_marshals([inf, cav, art, adj1, adj2])
        ex = CommandExecutor()

        ex._calculate_coordination_context(inf, world)

        # CA = 20% atk + adjacent = 4% + per-ally coordination varies
        # Total should be capped at 25%
        assert inf.total_coordination_attack_bonus <= 0.25
        # Defense has no adjacent component, capped at 20%
        assert inf.total_coordination_defense_bonus <= 0.20

    def test_exclude_names_parameter(self):
        """exclude_names parameter removes specified marshals from count (for S61)."""
        primary = _make_marshal(name="Ney", location="Paris")
        adj1 = _make_marshal(name="Davout", location="Belgium")
        adj2 = _make_marshal(name="Soult", location="Lyon")
        world = WorldFactory.with_marshals([primary, adj1, adj2])
        ex = CommandExecutor()

        # Without exclusion: 2 adjacent
        count, names = ex._count_adjacent_allies("Paris", "France", world)
        assert count == 2

        # With exclusion: 1 adjacent
        count, names = ex._count_adjacent_allies("Paris", "France", world, exclude_names={"Davout"})
        assert count == 1
        assert "Davout" not in names
        assert "Soult" in names

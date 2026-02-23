"""
Tests for Combined Arms Detection (Phase 7, Session 57)

Tests multi-marshal coordination: combined arms unit type detection,
bonus calculation, transient field management, modifier integration,
combat display messages, and battle report snapshots.

Spec: docs/MULTI_MARSHAL_SPEC.md §2
Amendments: docs/PHASE7_SPEC_AMENDMENTS.md [S57]
"""

import pytest
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.combat import CombatResolver
from backend.game_logic.battle_report import (
    snapshot_attacker_modifiers, snapshot_defender_modifiers,
)


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    """Create a marshal with sensible defaults for coordination tests."""
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


def _make_world_with_marshals(marshal_list):
    """Create a WorldState and replace marshals with the given list."""
    world = WorldState()
    world.marshals.clear()
    for m in marshal_list:
        world.marshals[m.name] = m
    return world


def _executor():
    return CommandExecutor()


# ════════════════════════════════════════════════════════════════════════════════
# UNIT TYPE DETECTION
# ════════════════════════════════════════════════════════════════════════════════

class TestUnitTypeDetection:
    """Test _count_unit_types() correctly identifies unit type diversity."""

    def test_single_infantry_returns_1_type(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        world = _make_world_with_marshals([inf])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_single_cavalry_returns_1_type(self):
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        world = _make_world_with_marshals([cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_single_artillery_returns_1_type(self):
        art = _make_marshal(name="Art1", location="Paris", artillery=True)
        world = _make_world_with_marshals([art])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_infantry_and_cavalry_returns_2_types(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 2

    def test_infantry_and_artillery_returns_2_types(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        art = _make_marshal(name="Art1", location="Paris", artillery=True)
        world = _make_world_with_marshals([inf, art])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 2

    def test_cavalry_and_artillery_returns_2_types(self):
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        art = _make_marshal(name="Art1", location="Paris", artillery=True)
        world = _make_world_with_marshals([cav, art])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 2

    def test_all_three_types_returns_3(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        art = _make_marshal(name="Art1", location="Paris", artillery=True)
        world = _make_world_with_marshals([inf, cav, art])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 3

    def test_duplicate_infantry_still_1_type(self):
        inf1 = _make_marshal(name="Inf1", location="Paris")
        inf2 = _make_marshal(name="Inf2", location="Paris")
        world = _make_world_with_marshals([inf1, inf2])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_broken_marshal_excluded(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        cav.broken = True
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_retreating_marshal_excluded(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        cav.retreated_this_turn = True
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_recovering_marshal_excluded(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        cav.retreat_recovery = 2
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_zero_strength_excluded(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True, strength=0)
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_garrison_detachment_excluded(self):
        """Garrison detachments are a region property, not marshals — don't affect type count."""
        inf = _make_marshal(name="Inf1", location="Paris")
        world = _make_world_with_marshals([inf])
        # Set garrison on region (not a marshal)
        region = world.get_region("Paris")
        if region:
            region.garrison_detachment = True
            region.garrison_strength = 5000
        ex = _executor()
        # Still only 1 type — garrison doesn't add anything
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_fortified_marshal_counts(self):
        """Fortified marshals still contribute their unit type."""
        inf = _make_marshal(name="Inf1", location="Paris")
        inf.fortified = True
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 2

    def test_different_nation_excluded(self):
        inf = _make_marshal(name="Inf1", location="Paris", nation="France")
        cav = _make_marshal(name="Cav1", location="Paris", nation="Britain", cavalry=True)
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1

    def test_different_region_excluded(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Belgium", cavalry=True)
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 1


# ════════════════════════════════════════════════════════════════════════════════
# BONUS VALUES
# ════════════════════════════════════════════════════════════════════════════════

class TestBonusValues:
    """Test _get_combined_arms_bonus() returns correct (atk, def) pairs."""

    def test_1_type_gives_zero_bonus(self):
        ex = _executor()
        assert ex._get_combined_arms_bonus(1) == (0.0, 0.0)

    def test_2_types_gives_10_5_bonus(self):
        ex = _executor()
        assert ex._get_combined_arms_bonus(2) == (0.10, 0.05)

    def test_3_types_gives_20_10_bonus(self):
        ex = _executor()
        assert ex._get_combined_arms_bonus(3) == (0.20, 0.10)


# ════════════════════════════════════════════════════════════════════════════════
# COORDINATION CONTEXT
# ════════════════════════════════════════════════════════════════════════════════

class TestCoordinationContext:
    """Test _calculate_coordination_context() sets fields and returns data."""

    def test_coordination_context_sets_transient_fields(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        ctx = ex._calculate_coordination_context(inf, world)
        assert ctx["type_count"] == 2
        assert ctx["combined_arms_atk"] == 0.10
        assert ctx["combined_arms_def"] == 0.05
        # CA 10% + 1 ally at professional (3%) = 13% atk
        # CA 5% + 1 ally at professional (5%) = 10% def
        assert inf.total_coordination_attack_bonus == pytest.approx(0.13)
        assert inf.total_coordination_defense_bonus == pytest.approx(0.10)

    def test_coordination_context_sets_on_all_eligible(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        ex._calculate_coordination_context(inf, world)
        # Both marshals get CA + per-ally coordination (1 ally at professional)
        assert cav.total_coordination_attack_bonus == pytest.approx(0.13)
        assert cav.total_coordination_defense_bonus == pytest.approx(0.10)
        assert cav._display_combined_arms_atk == 0.10
        assert cav._display_combined_arms_def == 0.05

    def test_transient_fields_cleared_after_combat(self):
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        ex._calculate_coordination_context(inf, world)
        # Verify fields are set (CA 10% + 1 professional ally 3% = 13%)
        assert inf.total_coordination_attack_bonus == pytest.approx(0.13)
        # Now clear them
        ex._clear_coordination_fields({"Paris"}, world)
        assert inf.total_coordination_attack_bonus == 0.0
        assert inf.total_coordination_defense_bonus == 0.0
        assert cav.total_coordination_attack_bonus == 0.0
        assert cav.total_coordination_defense_bonus == 0.0

    def test_transient_fields_not_in_init(self):
        """Marshal() has no coordination fields by default (D5)."""
        m = _make_marshal(name="Test")
        assert not hasattr(m, 'total_coordination_attack_bonus')
        assert not hasattr(m, 'total_coordination_defense_bonus')
        assert not hasattr(m, '_display_combined_arms_atk')
        assert not hasattr(m, '_display_combined_arms_def')

    def test_transient_fields_not_serialized(self):
        """to_dict() does not include coordination transient fields."""
        m = _make_marshal(name="Test")
        # Set transient fields manually
        m.total_coordination_attack_bonus = 0.10
        m.total_coordination_defense_bonus = 0.05
        m._display_combined_arms_atk = 0.10
        m._display_combined_arms_def = 0.05
        d = m.to_dict()
        assert 'total_coordination_attack_bonus' not in d
        assert 'total_coordination_defense_bonus' not in d
        assert '_display_combined_arms_atk' not in d
        assert '_display_combined_arms_def' not in d


# ════════════════════════════════════════════════════════════════════════════════
# MODIFIER INTEGRATION
# ════════════════════════════════════════════════════════════════════════════════

class TestModifierIntegration:
    """Test that get_attack_modifier / get_defense_modifier include coordination."""

    def test_attack_modifier_includes_combined_arms(self):
        m = _make_marshal(name="Test")
        base = m.get_attack_modifier()
        # Now set coordination bonus
        m.total_coordination_attack_bonus = 0.10
        boosted = m.get_attack_modifier()
        assert boosted > base
        assert abs(boosted - base * 1.10) < 0.001

    def test_defense_modifier_includes_combined_arms(self):
        m = _make_marshal(name="Test")
        base = m.get_defense_modifier()
        # Now set coordination bonus
        m.total_coordination_defense_bonus = 0.05
        boosted = m.get_defense_modifier()
        assert boosted > base
        assert abs(boosted - base * 1.05) < 0.001

    def test_no_bonus_when_no_transient_field(self):
        """getattr default 0.0 means no bonus when field doesn't exist."""
        m = _make_marshal(name="Test")
        base_atk = m.get_attack_modifier()
        base_def = m.get_defense_modifier()
        # These should be exactly 1.0 for a neutral-stance, no-bonus marshal
        assert base_atk == pytest.approx(1.0, abs=0.001)
        assert base_def == pytest.approx(1.0, abs=0.001)

    def test_modifier_multiplies_correctly(self):
        """e.g., base 1.15 (aggressive stance) × 1.10 (combined arms) = 1.265"""
        from backend.models.marshal import Stance
        m = _make_marshal(name="Test", personality="aggressive")
        m.stance = Stance.AGGRESSIVE
        base = m.get_attack_modifier()
        # Aggressive stance gives about 1.15 × personality bonus
        m.total_coordination_attack_bonus = 0.10
        boosted = m.get_attack_modifier()
        assert abs(boosted - base * 1.10) < 0.01


# ════════════════════════════════════════════════════════════════════════════════
# BOTH SIDES INDEPENDENT
# ════════════════════════════════════════════════════════════════════════════════

class TestBothSidesIndependent:
    """Test that attacker and defender get independent combined arms calculations."""

    def test_attacker_gets_own_combined_arms(self):
        atk_inf = _make_marshal(name="AtkInf", location="Belgium")
        atk_cav = _make_marshal(name="AtkCav", location="Belgium", cavalry=True)
        defender = _make_marshal(name="Def", location="Belgium", nation="Britain")
        world = _make_world_with_marshals([atk_inf, atk_cav, defender])
        ex = _executor()
        ctx = ex._calculate_coordination_context(atk_inf, world)
        assert ctx["type_count"] == 2
        assert ctx["combined_arms_atk"] == 0.10

    def test_defender_gets_own_combined_arms(self):
        attacker = _make_marshal(name="Atk", location="Belgium")
        def_inf = _make_marshal(name="DefInf", location="Belgium", nation="Britain")
        def_cav = _make_marshal(name="DefCav", location="Belgium", nation="Britain", cavalry=True)
        world = _make_world_with_marshals([attacker, def_inf, def_cav])
        ex = _executor()
        ctx = ex._calculate_coordination_context(def_inf, world)
        assert ctx["type_count"] == 2
        assert ctx["combined_arms_def"] == 0.05

    def test_both_sides_in_same_battle(self):
        """Attacker 2 types, defender 1 type → different bonuses."""
        atk_inf = _make_marshal(name="AtkInf", location="Belgium")
        atk_cav = _make_marshal(name="AtkCav", location="Belgium", cavalry=True)
        defender = _make_marshal(name="Def", location="Belgium", nation="Britain")
        world = _make_world_with_marshals([atk_inf, atk_cav, defender])
        ex = _executor()
        atk_ctx = ex._calculate_coordination_context(atk_inf, world)
        def_ctx = ex._calculate_coordination_context(defender, world)
        assert atk_ctx["type_count"] == 2  # France: infantry + cavalry
        assert def_ctx["type_count"] == 1  # Britain: solo infantry
        assert atk_ctx["combined_arms_atk"] == 0.10
        assert def_ctx["combined_arms_atk"] == 0.0

    def test_france_3_types_vs_coalition_2_types(self):
        """France gets +20% atk, Coalition (e.g. Prussia at 2/3) gets +10% atk."""
        # France: all 3 types
        fr_inf = _make_marshal(name="FrInf", location="Belgium")
        fr_cav = _make_marshal(name="FrCav", location="Belgium", cavalry=True)
        fr_art = _make_marshal(name="FrArt", location="Belgium", artillery=True)
        # Prussia: 2 types (infantry + artillery)
        pr_inf = _make_marshal(name="PrInf", location="Belgium", nation="Prussia")
        pr_art = _make_marshal(name="PrArt", location="Belgium", nation="Prussia", artillery=True)
        world = _make_world_with_marshals([fr_inf, fr_cav, fr_art, pr_inf, pr_art])
        ex = _executor()
        fr_ctx = ex._calculate_coordination_context(fr_inf, world)
        pr_ctx = ex._calculate_coordination_context(pr_inf, world)
        assert fr_ctx["combined_arms_atk"] == 0.20
        assert fr_ctx["combined_arms_def"] == 0.10
        assert pr_ctx["combined_arms_atk"] == 0.10
        assert pr_ctx["combined_arms_def"] == 0.05


# ════════════════════════════════════════════════════════════════════════════════
# BATTLE REPORT SNAPSHOTS
# ════════════════════════════════════════════════════════════════════════════════

class TestBattleReportSnapshots:
    """Test that battle report snapshot functions capture coordination data."""

    def test_snapshot_captures_combined_arms_atk(self):
        attacker = _make_marshal(name="Atk")
        defender = _make_marshal(name="Def", nation="Britain")
        attacker._display_combined_arms_atk = 0.10
        attacker.total_coordination_attack_bonus = 0.10
        mods = snapshot_attacker_modifiers(
            attacker, defender, "plains", 0.0, 0, False
        )
        labels = [m["label"] for m in mods]
        assert "Combined arms" in labels
        ca_mod = next(m for m in mods if m["label"] == "Combined arms")
        assert ca_mod["value"] == 10
        assert ca_mod["type"] == "bonus"

    def test_snapshot_captures_combined_arms_def(self):
        attacker = _make_marshal(name="Atk")
        defender = _make_marshal(name="Def", nation="Britain")
        defender._display_combined_arms_def = 0.05
        defender.total_coordination_defense_bonus = 0.05
        mods = snapshot_defender_modifiers(
            defender, attacker, "plains", 0.0
        )
        labels = [m["label"] for m in mods]
        assert "Combined arms" in labels
        ca_mod = next(m for m in mods if m["label"] == "Combined arms")
        assert ca_mod["value"] == 5
        assert ca_mod["type"] == "bonus"

    def test_snapshot_captures_total_coordination(self):
        """When total differs from combined arms, both show up."""
        attacker = _make_marshal(name="Atk")
        defender = _make_marshal(name="Def", nation="Britain")
        # Simulate future state: combined arms + other coordination sources
        attacker._display_combined_arms_atk = 0.10
        attacker.total_coordination_attack_bonus = 0.20  # Total > CA → other sources
        mods = snapshot_attacker_modifiers(
            attacker, defender, "plains", 0.0, 0, False
        )
        labels = [m["label"] for m in mods]
        assert "Combined arms" in labels
        assert "Coordination (total)" in labels

    def test_snapshot_no_duplicate_when_total_equals_ca(self):
        """When total == combined arms, only show combined arms (no redundant total)."""
        attacker = _make_marshal(name="Atk")
        defender = _make_marshal(name="Def", nation="Britain")
        attacker._display_combined_arms_atk = 0.10
        attacker.total_coordination_attack_bonus = 0.10  # Same as CA
        mods = snapshot_attacker_modifiers(
            attacker, defender, "plains", 0.0, 0, False
        )
        labels = [m["label"] for m in mods]
        assert "Combined arms" in labels
        assert "Coordination (total)" not in labels


# ════════════════════════════════════════════════════════════════════════════════
# COMBAT DISPLAY
# ════════════════════════════════════════════════════════════════════════════════

class TestCombatDisplay:
    """Test combined arms messages appear in combat output."""

    def test_combined_arms_message_in_battle_output(self):
        """2+ types shows combined arms message in battle description."""
        attacker = _make_marshal(name="Atk", location="Paris", strength=30000)
        defender = _make_marshal(name="Def", location="Paris", strength=30000, nation="Britain")
        # Set combined arms transient fields (simulating coordination context)
        attacker._display_combined_arms_atk = 0.10
        defender._display_combined_arms_def = 0.0
        resolver = CombatResolver()
        result = resolver.resolve_battle(attacker, defender, terrain="plains")
        desc = result["description"]
        assert "combined arms" in desc.lower()
        assert "+10% attack" in desc

    def test_no_combined_arms_message_for_solo(self):
        """1 type (no combined arms) shows no combined arms message."""
        attacker = _make_marshal(name="Atk", location="Paris", strength=30000)
        defender = _make_marshal(name="Def", location="Paris", strength=30000, nation="Britain")
        # No transient fields set (default 0.0 via getattr)
        resolver = CombatResolver()
        result = resolver.resolve_battle(attacker, defender, terrain="plains")
        desc = result["description"]
        assert "combined arms" not in desc.lower()


# ════════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ════════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Test edge cases and cap verification."""

    def test_hard_cap_bites_with_combined_arms_and_coordination(self):
        """3/3 CA (20% atk) + 2 allies at professional (2×3% = 6%) = 26% → capped to 25%.
        Defense: 3/3 CA (10%) + 2 allies (2×5% = 10%) = 20% → exactly at cap."""
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        art = _make_marshal(name="Art1", location="Paris", artillery=True)
        world = _make_world_with_marshals([inf, cav, art])
        ex = _executor()
        ctx = ex._calculate_coordination_context(inf, world)
        # atk: CA 20% + 2 professional allies (6%) = 26% → capped at 25%
        assert ctx["capped_atk"] == pytest.approx(0.25)
        # def: CA 10% + 2 professional allies (10%) = 20% → exactly at cap
        assert ctx["capped_def"] == pytest.approx(0.20)

    def test_zero_type_count_returns_zero(self):
        """Empty region returns 0 types."""
        world = _make_world_with_marshals([])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 0

    def test_combined_arms_with_only_dead_marshals(self):
        """All marshals dead → 0 types."""
        inf = _make_marshal(name="Inf1", location="Paris", strength=0)
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True, strength=0)
        world = _make_world_with_marshals([inf, cav])
        ex = _executor()
        assert ex._count_unit_types("Paris", "France", world) == 0

    def test_eligible_marshals_list_in_context(self):
        """Context returns names of eligible marshals."""
        inf = _make_marshal(name="Davout", location="Paris")
        cav = _make_marshal(name="Ney", location="Paris", cavalry=True)
        dead = _make_marshal(name="Dead", location="Paris", strength=0)
        world = _make_world_with_marshals([inf, cav, dead])
        ex = _executor()
        ctx = ex._calculate_coordination_context(inf, world)
        assert "Davout" in ctx["eligible_marshals"]
        assert "Ney" in ctx["eligible_marshals"]
        assert "Dead" not in ctx["eligible_marshals"]

    def test_display_fields_set_correctly(self):
        """Display fields (_display_combined_arms_*) set to raw CA values."""
        inf = _make_marshal(name="Inf1", location="Paris")
        cav = _make_marshal(name="Cav1", location="Paris", cavalry=True)
        art = _make_marshal(name="Art1", location="Paris", artillery=True)
        world = _make_world_with_marshals([inf, cav, art])
        ex = _executor()
        ex._calculate_coordination_context(inf, world)
        assert inf._display_combined_arms_atk == 0.20
        assert inf._display_combined_arms_def == 0.10
        assert cav._display_combined_arms_atk == 0.20
        assert art._display_combined_arms_atk == 0.20

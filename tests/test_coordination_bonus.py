"""
Tests for Per-Ally Coordination Bonus (Phase 7, Session 58)

Tests relationship-scaled per-ally coordination bonuses:
- Each ally contributes +3% attack / +5% defense × relationship scaling
- Relationship scaling: Hostile(0.0) → Rival(0.5) → Professional(1.0) → Friendly(1.25) → Devoted(1.5)
- Fortification rule: fortified non-artillery gives defense only, fortified artillery gives both
- Hard cap: +25% attack / +20% defense (sum of ALL sources: combined arms + coordination)

Spec: docs/MULTI_MARSHAL_SPEC.md §3
Amendments: docs/PHASE7_SPEC_AMENDMENTS.md [A-C1, A-C3]
"""

import pytest
from backend.commands.executor import CommandExecutor
from backend.game_logic.battle_report import (
    snapshot_attacker_modifiers, snapshot_defender_modifiers,
)
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


# ════════════════════════════════════════════════════════════════════════════════
# RELATIONSHIP SCALING VALUES
# ════════════════════════════════════════════════════════════════════════════════

class TestRelationshipScaling:
    """Test that each relationship level produces correct coordination values."""

    def test_hostile_gives_zero_coordination(self):
        """Hostile (-2) → scale 0.0 → +0% atk, +0% def."""
        primary = _make_marshal(name="A", location="Paris")
        ally = _make_marshal(name="B", location="Paris", cavalry=True)
        primary.set_relationship("B", -2)
        world = WorldFactory.with_marshals([primary, ally])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        # CA: 2 types → 10% atk, 5% def. Coordination: 0% from hostile ally.
        assert primary._display_coordination_atk == pytest.approx(0.0)
        assert primary._display_coordination_def == pytest.approx(0.0)

    def test_rival_gives_half_coordination(self):
        """Rival (-1) → scale 0.5 → +1.5% atk, +2.5% def."""
        primary = _make_marshal(name="A", location="Paris")
        ally = _make_marshal(name="B", location="Paris", cavalry=True)
        primary.set_relationship("B", -1)
        world = WorldFactory.with_marshals([primary, ally])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.015)
        assert primary._display_coordination_def == pytest.approx(0.025)

    def test_professional_gives_full_coordination(self):
        """Professional (0) → scale 1.0 → +3% atk, +5% def."""
        primary = _make_marshal(name="A", location="Paris")
        ally = _make_marshal(name="B", location="Paris", cavalry=True)
        # Default relationship is 0 (professional)
        world = WorldFactory.with_marshals([primary, ally])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.03)
        assert primary._display_coordination_def == pytest.approx(0.05)

    def test_friendly_gives_125_coordination(self):
        """Friendly (+1) → scale 1.25 → +3.75% atk, +6.25% def."""
        primary = _make_marshal(name="A", location="Paris")
        ally = _make_marshal(name="B", location="Paris", cavalry=True)
        primary.set_relationship("B", 1)
        world = WorldFactory.with_marshals([primary, ally])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.0375)
        assert primary._display_coordination_def == pytest.approx(0.0625)

    def test_devoted_gives_150_coordination(self):
        """Devoted (+2) → scale 1.5 → +4.5% atk, +7.5% def."""
        primary = _make_marshal(name="A", location="Paris")
        ally = _make_marshal(name="B", location="Paris", cavalry=True)
        primary.set_relationship("B", 2)
        world = WorldFactory.with_marshals([primary, ally])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.045)
        assert primary._display_coordination_def == pytest.approx(0.075)


# ════════════════════════════════════════════════════════════════════════════════
# ASYMMETRIC RELATIONSHIPS
# ════════════════════════════════════════════════════════════════════════════════

class TestAsymmetricRelationships:
    """Test that each marshal gets their OWN coordination based on their relationships."""

    def test_ney_davout_both_hostile(self):
        """Ney→Davout Hostile (0%), Davout→Ney Hostile (0%) — both get 0 coordination."""
        ney = _make_marshal(name="Ney", location="Paris", cavalry=True)
        davout = _make_marshal(name="Davout", location="Paris")
        ney.set_relationship("Davout", -2)
        davout.set_relationship("Ney", -2)
        world = WorldFactory.with_marshals([ney, davout])
        ex = CommandExecutor()
        ex._calculate_coordination_context(ney, world)
        assert ney._display_coordination_atk == pytest.approx(0.0)
        assert davout._display_coordination_atk == pytest.approx(0.0)

    def test_asymmetric_relationship_different_bonuses(self):
        """A→B Friendly (+1), B→A Rival (-1) → different coordination totals."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris", cavalry=True)
        a.set_relationship("B", 1)   # A sees B as Friendly
        b.set_relationship("A", -1)  # B sees A as Rival
        world = WorldFactory.with_marshals([a, b])
        ex = CommandExecutor()
        ex._calculate_coordination_context(a, world)
        # A gets Friendly scaling: +3.75% atk from B
        assert a._display_coordination_atk == pytest.approx(0.0375)
        # B gets Rival scaling: +1.5% atk from A
        assert b._display_coordination_atk == pytest.approx(0.015)

    def test_each_marshal_gets_own_coordination(self):
        """3 marshals, each with unique relationships → each gets unique total."""
        a = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris", cavalry=True)
        c = _make_marshal(name="C", location="Paris", artillery=True)
        # A: Professional with B (0), Hostile with C (-2)
        a.set_relationship("B", 0)
        a.set_relationship("C", -2)
        # B: Friendly with A (+1), Devoted with C (+2)
        b.set_relationship("A", 1)
        b.set_relationship("C", 2)
        # C: Rival with A (-1), Professional with B (0)
        c.set_relationship("A", -1)
        c.set_relationship("B", 0)
        world = WorldFactory.with_marshals([a, b, c])
        ex = CommandExecutor()
        ex._calculate_coordination_context(a, world)
        # A: B(professional 3%) + C(hostile 0%) = 3%
        assert a._display_coordination_atk == pytest.approx(0.03)
        # B: A(friendly 3.75%) + C(devoted 4.5%) = 8.25%
        assert b._display_coordination_atk == pytest.approx(0.0825)
        # C: A(rival 1.5%) + B(professional 3%) = 4.5%
        assert c._display_coordination_atk == pytest.approx(0.045)


# ════════════════════════════════════════════════════════════════════════════════
# FORTIFICATION RULE
# ════════════════════════════════════════════════════════════════════════════════

class TestFortificationRule:
    """Test that fortified allies affect attack/defense coordination correctly."""

    def test_fortified_infantry_excluded_from_attack_coordination(self):
        """Fortified non-artillery ally gives 0 attack coordination."""
        primary = _make_marshal(name="A", location="Paris")
        fort_ally = _make_marshal(name="B", location="Paris", cavalry=True)
        fort_ally.fortified = True
        world = WorldFactory.with_marshals([primary, fort_ally])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.0)

    def test_fortified_infantry_contributes_defense_coordination(self):
        """Fortified non-artillery ally still gives full defense coordination."""
        primary = _make_marshal(name="A", location="Paris")
        fort_ally = _make_marshal(name="B", location="Paris", cavalry=True)
        fort_ally.fortified = True
        world = WorldFactory.with_marshals([primary, fort_ally])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_def == pytest.approx(0.05)

    def test_fortified_artillery_contributes_both(self):
        """Fortified artillery ally gives BOTH attack and defense coordination."""
        primary = _make_marshal(name="A", location="Paris")
        fort_art = _make_marshal(name="B", location="Paris", artillery=True)
        fort_art.fortified = True
        world = WorldFactory.with_marshals([primary, fort_art])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.03)
        assert primary._display_coordination_def == pytest.approx(0.05)

    def test_unfortified_contributes_both(self):
        """Normal (unfortified) ally gives both attack and defense coordination."""
        primary = _make_marshal(name="A", location="Paris")
        ally = _make_marshal(name="B", location="Paris", cavalry=True)
        world = WorldFactory.with_marshals([primary, ally])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.03)
        assert primary._display_coordination_def == pytest.approx(0.05)


# ════════════════════════════════════════════════════════════════════════════════
# MULTIPLE ALLIES STACKING
# ════════════════════════════════════════════════════════════════════════════════

class TestMultipleAlliesStacking:
    """Test that per-ally bonuses stack additively."""

    def test_two_professional_allies_stack(self):
        """2 × Professional (+3%) = +6% atk, 2 × (+5%) = +10% def."""
        primary = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris", cavalry=True)
        c = _make_marshal(name="C", location="Paris", artillery=True)
        world = WorldFactory.with_marshals([primary, b, c])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.06)
        assert primary._display_coordination_def == pytest.approx(0.10)

    def test_three_allies_mixed_relationships(self):
        """Hostile(0%) + Professional(3%) + Devoted(4.5%) = 7.5% atk."""
        primary = _make_marshal(name="A", location="Paris")
        b = _make_marshal(name="B", location="Paris", cavalry=True)
        c = _make_marshal(name="C", location="Paris", artillery=True)
        d = _make_marshal(name="D", location="Paris")
        primary.set_relationship("B", -2)  # Hostile → 0%
        primary.set_relationship("C", 0)   # Professional → 3%
        primary.set_relationship("D", 2)   # Devoted → 4.5%
        world = WorldFactory.with_marshals([primary, b, c, d])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.075)

    def test_solo_marshal_zero_coordination(self):
        """No allies = 0% coordination bonus."""
        solo = _make_marshal(name="Solo", location="Paris")
        world = WorldFactory.with_marshals([solo])
        ex = CommandExecutor()
        ex._calculate_coordination_context(solo, world)
        assert solo._display_coordination_atk == pytest.approx(0.0)
        assert solo._display_coordination_def == pytest.approx(0.0)


# ════════════════════════════════════════════════════════════════════════════════
# HARD CAP ENFORCEMENT
# ════════════════════════════════════════════════════════════════════════════════

class TestHardCapEnforcement:
    """Test that the +25% atk / +20% def hard cap is enforced."""

    def test_hard_cap_25_attack_enforced(self):
        """3/3 CA (20%) + 2 professional allies (6%) = 26% → capped at 25%."""
        inf = _make_marshal(name="Inf", location="Paris")
        cav = _make_marshal(name="Cav", location="Paris", cavalry=True)
        art = _make_marshal(name="Art", location="Paris", artillery=True)
        world = WorldFactory.with_marshals([inf, cav, art])
        ex = CommandExecutor()
        ex._calculate_coordination_context(inf, world)
        assert inf.total_coordination_attack_bonus == pytest.approx(0.25)

    def test_hard_cap_20_defense_enforced(self):
        """3/3 CA (10%) + 2 professional allies (10%) = 20% → exactly at cap.
        Add devoted relationship to push over: 10% + 12.5% = 22.5% → capped at 20%."""
        inf = _make_marshal(name="Inf", location="Paris")
        cav = _make_marshal(name="Cav", location="Paris", cavalry=True)
        art = _make_marshal(name="Art", location="Paris", artillery=True)
        inf.set_relationship("Cav", 2)  # Devoted → 7.5% def
        inf.set_relationship("Art", 2)  # Devoted → 7.5% def
        world = WorldFactory.with_marshals([inf, cav, art])
        ex = CommandExecutor()
        ex._calculate_coordination_context(inf, world)
        # CA 10% + Devoted×2 (15%) = 25% → capped at 20%
        assert inf.total_coordination_defense_bonus == pytest.approx(0.20)

    def test_cap_applies_after_sum(self):
        """Sum all sources first, THEN cap (not cap per-source)."""
        inf = _make_marshal(name="Inf", location="Paris")
        cav = _make_marshal(name="Cav", location="Paris", cavalry=True)
        art = _make_marshal(name="Art", location="Paris", artillery=True)
        world = WorldFactory.with_marshals([inf, cav, art])
        ex = CommandExecutor()
        ex._calculate_coordination_context(inf, world)
        # Raw atk = CA(20%) + coord(6%) = 26%. Cap 25%. Not CA(capped 20%) + coord(capped 6%) = 26%.
        assert inf.total_coordination_attack_bonus == pytest.approx(0.25)
        # Display fields show raw (uncapped) per-source
        assert inf._display_combined_arms_atk == pytest.approx(0.20)
        assert inf._display_coordination_atk == pytest.approx(0.06)

    def test_under_cap_not_reduced(self):
        """Values below cap pass through unchanged."""
        primary = _make_marshal(name="A", location="Paris")
        ally = _make_marshal(name="B", location="Paris", cavalry=True)
        world = WorldFactory.with_marshals([primary, ally])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        # CA(10%) + coord(3%) = 13% → under 25% cap
        assert primary.total_coordination_attack_bonus == pytest.approx(0.13)
        # CA(5%) + coord(5%) = 10% → under 20% cap
        assert primary.total_coordination_defense_bonus == pytest.approx(0.10)


# ════════════════════════════════════════════════════════════════════════════════
# COMBINED ARMS + COORDINATION INTEGRATION
# ════════════════════════════════════════════════════════════════════════════════

class TestCombinedArmsCoordinationIntegration:
    """Test combined arms and per-ally coordination sum correctly."""

    def test_combined_arms_and_coordination_sum(self):
        """2/3 CA (10%) + 1 Professional ally (3%) = 13% atk."""
        inf = _make_marshal(name="Inf", location="Paris")
        cav = _make_marshal(name="Cav", location="Paris", cavalry=True)
        world = WorldFactory.with_marshals([inf, cav])
        ex = CommandExecutor()
        ex._calculate_coordination_context(inf, world)
        assert inf.total_coordination_attack_bonus == pytest.approx(0.13)
        assert inf.total_coordination_defense_bonus == pytest.approx(0.10)

    def test_three_types_plus_devoted_ally(self):
        """3/3 CA (20%) + Devoted ally (4.5%) = 24.5% atk (under cap)."""
        inf = _make_marshal(name="Inf", location="Paris")
        cav = _make_marshal(name="Cav", location="Paris", cavalry=True)
        art = _make_marshal(name="Art", location="Paris", artillery=True)
        inf.set_relationship("Cav", 2)
        inf.set_relationship("Art", 2)
        world = WorldFactory.with_marshals([inf, cav, art])
        ex = CommandExecutor()
        ex._calculate_coordination_context(inf, world)
        # atk: CA(20%) + 2 Devoted (2 × 4.5% = 9%) = 29% → capped at 25%
        assert inf.total_coordination_attack_bonus == pytest.approx(0.25)

    def test_two_types_no_extra_coordination(self):
        """2/3 CA with hostile ally → only CA bonus applies."""
        inf = _make_marshal(name="Inf", location="Paris")
        cav = _make_marshal(name="Cav", location="Paris", cavalry=True)
        inf.set_relationship("Cav", -2)
        world = WorldFactory.with_marshals([inf, cav])
        ex = CommandExecutor()
        ex._calculate_coordination_context(inf, world)
        # CA(10%) + Hostile coord(0%) = 10%
        assert inf.total_coordination_attack_bonus == pytest.approx(0.10)
        assert inf._display_coordination_atk == pytest.approx(0.0)


# ════════════════════════════════════════════════════════════════════════════════
# BOTH SIDES INDEPENDENT
# ════════════════════════════════════════════════════════════════════════════════

class TestBothSidesIndependent:
    """Test that attacker and defender get independent coordination."""

    def test_attacker_coordination_independent_of_defender(self):
        """Attacker has 2 allies, defender has 0 → different coordination."""
        atk1 = _make_marshal(name="AtkInf", location="Belgium")
        atk2 = _make_marshal(name="AtkCav", location="Belgium", cavalry=True)
        atk3 = _make_marshal(name="AtkArt", location="Belgium", artillery=True)
        defender = _make_marshal(name="Def", location="Belgium", nation="Britain")
        world = WorldFactory.with_marshals([atk1, atk2, atk3, defender])
        ex = CommandExecutor()
        ex._calculate_coordination_context(atk1, world)
        ex._calculate_coordination_context(defender, world)
        # Attacker: 3/3 CA + 2 professional allies
        assert atk1.total_coordination_attack_bonus == pytest.approx(0.25)  # capped
        # Defender: solo → 0
        assert defender.total_coordination_attack_bonus == pytest.approx(0.0)

    def test_defender_coordination_uses_own_relationships(self):
        """Defender's coordination based on defender's relationship values."""
        attacker = _make_marshal(name="Atk", location="Belgium")
        def1 = _make_marshal(name="DefInf", location="Belgium", nation="Britain")
        def2 = _make_marshal(name="DefCav", location="Belgium", nation="Britain", cavalry=True)
        def1.set_relationship("DefCav", 2)  # Devoted
        world = WorldFactory.with_marshals([attacker, def1, def2])
        ex = CommandExecutor()
        ex._calculate_coordination_context(def1, world)
        # DefInf: 2/3 CA (10% atk, 5% def) + Devoted ally (4.5% atk, 7.5% def)
        assert def1._display_coordination_atk == pytest.approx(0.045)
        assert def1._display_coordination_def == pytest.approx(0.075)

    def test_battle_with_coordination_both_sides(self):
        """Full battle — both sides get correct independent bonuses."""
        atk_inf = _make_marshal(name="AtkInf", location="Belgium", strength=30000)
        atk_cav = _make_marshal(name="AtkCav", location="Belgium", strength=30000, cavalry=True)
        def_inf = _make_marshal(name="DefInf", location="Belgium", strength=30000, nation="Britain")
        def_cav = _make_marshal(name="DefCav", location="Belgium", strength=30000, nation="Britain", cavalry=True)
        world = WorldFactory.with_marshals([atk_inf, atk_cav, def_inf, def_cav])
        ex = CommandExecutor()
        ex._calculate_coordination_context(atk_inf, world)
        ex._calculate_coordination_context(def_inf, world)
        # Both sides: 2/3 CA + 1 professional ally
        assert atk_inf.total_coordination_attack_bonus == pytest.approx(0.13)
        assert def_inf.total_coordination_defense_bonus == pytest.approx(0.10)


# ════════════════════════════════════════════════════════════════════════════════
# MODIFIER INTEGRATION
# ════════════════════════════════════════════════════════════════════════════════

class TestModifierIntegration:
    """Test that get_attack_modifier / get_defense_modifier include coordination."""

    def test_attack_modifier_reflects_coordination_bonus(self):
        """Coordination bonus appears in get_attack_modifier."""
        m = _make_marshal(name="Test")
        base = m.get_attack_modifier()
        # Set combined coordination (CA + per-ally)
        m.total_coordination_attack_bonus = 0.13
        boosted = m.get_attack_modifier()
        assert abs(boosted - base * 1.13) < 0.001

    def test_defense_modifier_reflects_coordination_bonus(self):
        """Coordination bonus appears in get_defense_modifier."""
        m = _make_marshal(name="Test")
        base = m.get_defense_modifier()
        m.total_coordination_defense_bonus = 0.10
        boosted = m.get_defense_modifier()
        assert abs(boosted - base * 1.10) < 0.001

    def test_coordination_compounds_with_personality(self):
        """Aggressive stance × coordination → multiplicative stacking."""
        from backend.models.marshal import Stance
        m = _make_marshal(name="Test", personality="aggressive")
        m.stance = Stance.AGGRESSIVE
        base = m.get_attack_modifier()
        m.total_coordination_attack_bonus = 0.13
        boosted = m.get_attack_modifier()
        assert abs(boosted - base * 1.13) < 0.01


# ════════════════════════════════════════════════════════════════════════════════
# ELIGIBILITY FILTERS
# ════════════════════════════════════════════════════════════════════════════════

class TestEligibilityFilters:
    """Test that ineligible marshals are excluded from coordination."""

    def test_broken_ally_excluded_from_coordination(self):
        """Broken marshal not counted as ally."""
        primary = _make_marshal(name="A", location="Paris")
        broken = _make_marshal(name="B", location="Paris", cavalry=True)
        broken.broken = True
        world = WorldFactory.with_marshals([primary, broken])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.0)
        assert primary._display_coordination_def == pytest.approx(0.0)

    def test_retreating_ally_excluded(self):
        """Retreated marshal not counted as ally."""
        primary = _make_marshal(name="A", location="Paris")
        retreated = _make_marshal(name="B", location="Paris", cavalry=True)
        retreated.retreated_this_turn = True
        world = WorldFactory.with_marshals([primary, retreated])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.0)

    def test_recovering_ally_excluded(self):
        """Recovering marshal (retreat_recovery > 0) not counted as ally."""
        primary = _make_marshal(name="A", location="Paris")
        recovering = _make_marshal(name="B", location="Paris", cavalry=True)
        recovering.retreat_recovery = 2
        world = WorldFactory.with_marshals([primary, recovering])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.0)

    def test_zero_strength_ally_excluded(self):
        """Dead marshal (0 strength) not counted as ally."""
        primary = _make_marshal(name="A", location="Paris")
        dead = _make_marshal(name="B", location="Paris", cavalry=True, strength=0)
        world = WorldFactory.with_marshals([primary, dead])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.0)

    def test_enemy_nation_excluded(self):
        """Different nation not counted as ally."""
        primary = _make_marshal(name="A", location="Paris", nation="France")
        enemy = _make_marshal(name="B", location="Paris", nation="Britain", cavalry=True)
        world = WorldFactory.with_marshals([primary, enemy])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.0)

    def test_different_region_excluded(self):
        """Ally in different region not counted."""
        primary = _make_marshal(name="A", location="Paris")
        far = _make_marshal(name="B", location="Belgium", cavalry=True)
        world = WorldFactory.with_marshals([primary, far])
        ex = CommandExecutor()
        ex._calculate_coordination_context(primary, world)
        assert primary._display_coordination_atk == pytest.approx(0.0)


# ════════════════════════════════════════════════════════════════════════════════
# TRANSIENT FIELD MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════════

class TestTransientFieldManagement:
    """Test coordination display fields are set and cleared properly."""

    def test_coordination_display_fields_set(self):
        """_display_coordination_atk/def are set on each marshal."""
        inf = _make_marshal(name="Inf", location="Paris")
        cav = _make_marshal(name="Cav", location="Paris", cavalry=True)
        world = WorldFactory.with_marshals([inf, cav])
        ex = CommandExecutor()
        ex._calculate_coordination_context(inf, world)
        assert hasattr(inf, '_display_coordination_atk')
        assert hasattr(inf, '_display_coordination_def')
        assert hasattr(cav, '_display_coordination_atk')
        assert hasattr(cav, '_display_coordination_def')

    def test_coordination_fields_cleared_after_combat(self):
        """All coordination fields reset after _clear_coordination_fields."""
        inf = _make_marshal(name="Inf", location="Paris")
        cav = _make_marshal(name="Cav", location="Paris", cavalry=True)
        world = WorldFactory.with_marshals([inf, cav])
        ex = CommandExecutor()
        ex._calculate_coordination_context(inf, world)
        assert inf._display_coordination_atk > 0
        ex._clear_coordination_fields({"Paris"}, world)
        assert inf._display_coordination_atk == 0.0
        assert inf._display_coordination_def == 0.0
        assert cav._display_coordination_atk == 0.0
        assert cav._display_coordination_def == 0.0

    def test_coordination_fields_not_serialized(self):
        """to_dict() does not include coordination transient fields."""
        m = _make_marshal(name="Test")
        m._display_coordination_atk = 0.03
        m._display_coordination_def = 0.05
        d = m.to_dict()
        assert '_display_coordination_atk' not in d
        assert '_display_coordination_def' not in d


# ════════════════════════════════════════════════════════════════════════════════
# BATTLE REPORT SNAPSHOTS
# ════════════════════════════════════════════════════════════════════════════════

class TestBattleReportSnapshots:
    """Test that battle report captures coordination display fields."""

    def test_snapshot_shows_coordination_total_when_different_from_ca(self):
        """Coordination entries intentionally omitted from snapshots (conveyed via Berthier narrative)."""
        attacker = _make_marshal(name="Atk")
        defender = _make_marshal(name="Def", nation="Britain")
        attacker._display_combined_arms_atk = 0.10
        attacker.total_coordination_attack_bonus = 0.13  # CA + per-ally
        mods = snapshot_attacker_modifiers(
            attacker, defender, "plains", 0.0, 0, False
        )
        labels = [m["label"] for m in mods]
        assert "Combined arms" not in labels
        assert "Coordination (total)" not in labels

    def test_snapshot_defender_coordination_total(self):
        """Defender coordination entries intentionally omitted from snapshots (conveyed via Berthier narrative)."""
        attacker = _make_marshal(name="Atk")
        defender = _make_marshal(name="Def", nation="Britain")
        defender._display_combined_arms_def = 0.05
        defender.total_coordination_defense_bonus = 0.10  # CA + per-ally
        mods = snapshot_defender_modifiers(
            defender, attacker, "plains", 0.0
        )
        labels = [m["label"] for m in mods]
        assert "Combined arms" not in labels
        assert "Coordination (total)" not in labels


# ════════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ════════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Test I2 scenario and full France stack."""

    def test_ney_davout_hostile_gives_combined_arms_only(self):
        """I2 dark comedy: CA 10% + coordination 0% = 10%."""
        ney = _make_marshal(name="Ney", location="Paris", cavalry=True)
        davout = _make_marshal(name="Davout", location="Paris")
        ney.set_relationship("Davout", -2)
        davout.set_relationship("Ney", -2)
        world = WorldFactory.with_marshals([ney, davout])
        ex = CommandExecutor()
        ex._calculate_coordination_context(ney, world)
        # CA: 2 types → 10%. Coordination from Hostile: 0%.
        assert ney.total_coordination_attack_bonus == pytest.approx(0.10)
        assert davout.total_coordination_attack_bonus == pytest.approx(0.10)

    def test_france_full_stack_professional(self):
        """Ney+Davout+Drouot all Professional: 3/3 CA + 2 allies → capped."""
        ney = _make_marshal(name="Ney", location="Paris", cavalry=True)
        davout = _make_marshal(name="Davout", location="Paris")
        drouot = _make_marshal(name="Drouot", location="Paris", artillery=True)
        world = WorldFactory.with_marshals([ney, davout, drouot])
        ex = CommandExecutor()
        ex._calculate_coordination_context(ney, world)
        # Each: CA(20%) + 2 Professional allies (6%) = 26% → capped at 25%
        assert ney.total_coordination_attack_bonus == pytest.approx(0.25)
        assert davout.total_coordination_attack_bonus == pytest.approx(0.25)
        assert drouot.total_coordination_attack_bonus == pytest.approx(0.25)
        # Defense: CA(10%) + 2 Professional allies (10%) = 20% → at cap
        assert ney.total_coordination_defense_bonus == pytest.approx(0.20)

    def test_france_full_stack_devoted(self):
        """All Devoted: 3/3 CA (20%) + 2 Devoted (9%) = 29% → capped at 25% atk."""
        ney = _make_marshal(name="Ney", location="Paris", cavalry=True)
        davout = _make_marshal(name="Davout", location="Paris")
        drouot = _make_marshal(name="Drouot", location="Paris", artillery=True)
        ney.set_relationship("Davout", 2)
        ney.set_relationship("Drouot", 2)
        world = WorldFactory.with_marshals([ney, davout, drouot])
        ex = CommandExecutor()
        ex._calculate_coordination_context(ney, world)
        # atk: CA(20%) + 2 Devoted (2 × 4.5% = 9%) = 29% → capped at 25%
        assert ney.total_coordination_attack_bonus == pytest.approx(0.25)
        # def: CA(10%) + 2 Devoted (2 × 7.5% = 15%) = 25% → capped at 20%
        assert ney.total_coordination_defense_bonus == pytest.approx(0.20)

    def test_per_ally_method_directly(self):
        """Test _calculate_per_ally_coordination helper method directly."""
        primary = _make_marshal(name="A")
        ally1 = _make_marshal(name="B")
        ally2 = _make_marshal(name="C", cavalry=True)
        primary.set_relationship("B", 0)   # Professional
        primary.set_relationship("C", 1)   # Friendly
        ex = CommandExecutor()
        atk, defe = ex._calculate_per_ally_coordination(primary, [ally1, ally2])
        # Professional: 3% + Friendly: 3.75% = 6.75% atk
        assert atk == pytest.approx(0.0675)
        # Professional: 5% + Friendly: 6.25% = 11.25% def
        assert defe == pytest.approx(0.1125)

    def test_scaling_table_class_attribute(self):
        """Verify the scaling table is accessible and correct."""
        from backend.commands.combat_executor import CombatExecutor
        ex = CommandExecutor()
        # _RELATIONSHIP_SCALING moved to CombatExecutor in R10B
        assert ex._combat._RELATIONSHIP_SCALING == {-2: 0.0, -1: 0.50, 0: 1.0, 1: 1.25, 2: 1.50}

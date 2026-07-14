"""Combat Overhaul Phase 1 — CO-1 / CO-1b / CO-2 behaviour tests.

Owner: docs/COMBAT_OVERHAUL_SPEC.md §4 Phase 1. Verifies the PRODUCTION change
(not the sweep model): committed reinforcements add strength to the clash
(CO-1), that contribution expresses the reinforcer's personality and
relationship to the lead (CO-1b), and the muster odds band reflects the total
committed force (CO-2).

GR1: the reinforcer's attack modifier is READ (consume=False) — no one-time
bonus is spent scoring a reinforcer. GR5: committed strength is symmetric — a
reinforced defender is stronger by the same code path.
"""

import random
from types import SimpleNamespace

from backend.commands.combat_executor import CombatExecutor
from backend.commands.objection_v2 import (
    inferred_attack_effective_ratio, inferred_attack_odds_band)
from backend.game_logic.combat import CombatResolver
from backend.models.marshal import Marshal, Stance


def _mk(name, strength, personality="aggressive", nation="France", *,
        morale=100, defense_bonus=0.0, stance=None):
    m = Marshal(name, "TestField", int(strength), personality, nation)
    m.morale = morale
    m.defense_bonus = defense_bonus
    if stance is not None:
        m.stance = stance
    return m


def _executor():
    return CombatExecutor(SimpleNamespace(combat_resolver=CombatResolver()))


# ════════════════════════════════════════════════════════════════════════════
# CO-1b — committed contribution helper (personality + relationship scaling)
# ════════════════════════════════════════════════════════════════════════════

def test_solo_lead_contributes_zero():
    ce = _executor()
    lead = _mk("Napoleon", 40000)
    assert ce._committed_reinforcement_strength(lead, [lead], None) == 0.0


def test_contribution_scales_with_alpha_and_strength():
    ce = _executor()
    lead = _mk("Napoleon", 40000)
    reinf = _mk("Soult", 40000, "aggressive")
    got = ce._committed_reinforcement_strength(lead, [lead, reinf], None)
    expected = (CombatExecutor.COMMITTED_ALPHA * reinf.strength
                * reinf.get_combat_effectiveness()
                * reinf.get_attack_modifier(1.0, consume=False)
                * 1.0)  # neutral relationship
    assert abs(got - expected) < 1.0
    assert got > 0.0


def test_aggressive_reinforcer_contributes_more_than_cautious():
    ce = _executor()
    lead = _mk("Napoleon", 40000)
    agg = ce._committed_reinforcement_strength(
        lead, [lead, _mk("A", 40000, "aggressive")], None)
    cau = ce._committed_reinforcement_strength(
        lead, [lead, _mk("B", 40000, "cautious")], None)
    assert agg > cau > 0.0


def test_hostile_pair_contributes_zero():
    """A reinforcer the lead is (aggressively) jealous of withholds entirely."""
    ce = _executor()
    lead = _mk("Napoleon", 40000, "aggressive")
    reinf = _mk("Bernadotte", 40000, "aggressive")
    lead.jealous_of = "Bernadotte"
    assert ce._committed_reinforcement_strength(lead, [lead, reinf], None) == 0.0


def test_relationship_factor_scales_contribution():
    """Devoted (+2 → ×1.5) contributes more than neutral (0 → ×1.0)."""
    ce = _executor()
    lead = _mk("Napoleon", 40000)
    neutral = _mk("N", 40000, "aggressive")
    devoted = _mk("D", 40000, "aggressive")
    lead.relationships = {"D": 2, "N": 0}
    c_neutral = ce._committed_reinforcement_strength(lead, [lead, neutral], None)
    c_devoted = ce._committed_reinforcement_strength(lead, [lead, devoted], None)
    assert c_devoted > c_neutral > 0.0


def test_reinforcer_iron_resolve_not_consumed_when_scored():
    """GR1: scoring a reinforcer's contribution must not spend its one-time
    bonuses (consume=False)."""
    ce = _executor()
    lead = _mk("Napoleon", 40000)
    davout = _mk("Davout", 40000, "cautious")
    davout.ability = {"name": "Iron Resolve"}
    davout.iron_resolve_stacks = 3
    ce._committed_reinforcement_strength(lead, [lead, davout], None)
    assert davout.iron_resolve_stacks == 3


# ════════════════════════════════════════════════════════════════════════════
# CO-1 — additive committed strength changes resolution
# ════════════════════════════════════════════════════════════════════════════

def _defender_casualties_with_committed(committed):
    """Mean defender casualties over fixed seeds for a given committed value."""
    total = 0
    for s in range(200):
        random.seed(s)
        atk = _mk("Napoleon", 40000, "aggressive")
        deff = _mk("Mack", 40000, "cautious", "Austria", defense_bonus=0.15)
        pre = deff.strength
        CombatResolver().resolve_battle(
            atk, deff, terrain="plains", apply_casualties=True,
            committed_attacker=committed)
        total += pre - deff.strength
    return total / 200


def test_committed_attacker_increases_defender_casualties():
    """More committed attacker strength → the defender bleeds more."""
    base = _defender_casualties_with_committed(0.0)
    massed = _defender_casualties_with_committed(60000.0)
    assert massed > base * 1.2, (
        f"committed strength should raise defender casualties: {base:.0f} -> {massed:.0f}")


def test_committed_zero_is_byte_identical_to_no_argument():
    """Default committed=0.0 must not perturb any existing solo battle."""
    random.seed(123)
    a1 = _mk("Napoleon", 40000, "aggressive")
    d1 = _mk("Mack", 40000, "cautious", "Austria", defense_bonus=0.15)
    r1 = CombatResolver().resolve_battle(a1, d1, terrain="plains")
    random.seed(123)
    a2 = _mk("Napoleon", 40000, "aggressive")
    d2 = _mk("Mack", 40000, "cautious", "Austria", defense_bonus=0.15)
    r2 = CombatResolver().resolve_battle(a2, d2, terrain="plains",
                                         committed_attacker=0.0,
                                         committed_defender=0.0)
    assert r1["attacker"]["casualties"] == r2["attacker"]["casualties"]
    assert r1["defender"]["casualties"] == r2["defender"]["casualties"]
    assert r1["outcome"] == r2["outcome"]


def test_committed_defender_is_symmetric():
    """GR5: a reinforced defender takes fewer casualties (same code path)."""
    def mean_def_cas(committed_def):
        total = 0
        for s in range(200):
            random.seed(s)
            atk = _mk("Napoleon", 60000, "aggressive")
            deff = _mk("Mack", 40000, "cautious", "Austria")
            pre = deff.strength
            CombatResolver().resolve_battle(
                atk, deff, terrain="plains", apply_casualties=True,
                committed_defender=committed_def)
            total += pre - deff.strength
        return total / 200
    assert mean_def_cas(40000.0) < mean_def_cas(0.0)


# ════════════════════════════════════════════════════════════════════════════
# CO-2 — muster odds band reflects committed force
# ════════════════════════════════════════════════════════════════════════════

def test_odds_ratio_rises_with_committed():
    marshal = _mk("Ney", 30000)
    enemy = _mk("Mack", 40000, "cautious", "Austria")
    lead_only = inferred_attack_effective_ratio(marshal, enemy)
    committed = inferred_attack_effective_ratio(
        marshal, enemy, committed_attacker=30000.0)
    assert committed > lead_only


def test_odds_band_can_flip_favorable_with_committed():
    marshal = _mk("Ney", 30000)
    enemy = _mk("Mack", 40000, "cautious", "Austria")
    assert inferred_attack_odds_band(marshal, enemy) != "favorable"
    assert inferred_attack_odds_band(
        marshal, enemy, committed_attacker=30000.0) == "favorable"

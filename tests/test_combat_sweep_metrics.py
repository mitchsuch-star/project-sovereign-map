"""Combat Overhaul Sweep — Half A deterministic metric harness (Phase 0).

Owner: docs/COMBAT_OVERHAUL_SPEC.md §2.1 (P0-1). This is the "run sweeps to
raise problematic scores" measurement engine. It runs a headless Monte-Carlo
over FIXED seeds against the REAL combat resolution (combat.py), the REAL
battle-report / casualty-distribution code, and the REAL jealousy engine —
prints each metric AND asserts the Phase-0 BASELINE (current behaviour), so
that every later slice FLIPS its assertion as it moves the metric toward
target.

PHASE 0 CONTRACT — measurement only. NO balance change lives here or in any
production file for this slice. The two forward-looking knobs the combat
overhaul will tune are declared here at their *baseline* values and read by
the metrics, so a later phase flips a single constant + the paired assertion:

    COMMITTED_ALPHA        = 0.0     # CO-1  (Phase 1): reinforcements add NO
                                     #        strength today (combat.py:1018
                                     #        resolves on the LEAD only).
    AI_CORPS_REGEN_PER_TURN = 10000  # CO-4  (Phase 2): the uncapped enemy
                                     #        per-corps top-up observed live
                                     #        (Field Review: Mack +10,000 in
                                     #        one turn). CO-4 caps it to R.

Metric map (spec §2.1) — ✅ = at target after Phase 2 (July 13, 2026):

    ID   State after Phase 2            Target                       Fixed by
    M1   ✅ monotonic (0.82 @5 corps)   strictly non-decreasing      CO-1
    M1b  ✅ agg 41.4k > cau 36k > 0     aggressive > cautious > hostile CO-1b
    M2   ✅ 0.61 @2:1 / 1.00 @3:1       >=0.35 @2:1, >=0.65 @3:1     CO-3 (Phase 2)
    M3   ✅ net <= -2000 (capped regen) net <= -2000                 CO-4 (Phase 2)
    M4   ✅ 100% multi-marshal          100%                         CO-5
    M5   ✅ +0.24 (stance freed)        >= +18%                      CO-7 (Phase 2)
    M6   defender-favourable (GUARD)    stays defender-favourable    holds all phases
    M7   drama dormant (pending)        <= 8                         Phase 3

Determinism: `random.seed(s)` is set before every single `resolve_battle`
call (combat.py draws 2d6 + a ±10% variance from the module `random`), and
every trial builds FRESH marshals (resolution mutates strength/morale). Same
seeds → identical numbers on every run and machine.

Run it:  ".venv\\Scripts\\python.exe" -m pytest tests/test_combat_sweep_metrics.py -v -s
The `-s` shows the printed metric table; set SWEEP_OUT=<path> to also dump a
markdown table (used to author docs/audits/SWEEP_<n>_<date>.md).
"""

import os
import random
import statistics
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.commands.combat_executor import CombatExecutor
from backend.game_logic.battle_report import generate_battle_report
from backend.game_logic.combat import CombatResolver, FORCED_RETREAT_THRESHOLD
from backend.game_logic import jealousy as J
from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════════
# TUNING KNOBS (baseline values — see module docstring / spec §0.3)
# ════════════════════════════════════════════════════════════════════════════

# CO-1: committed reinforcements add strength to the clash. Phase 1 (LANDED
# July 13, 2026) set this to the sweep-tuned α — the SAME single-source value
# as combat_executor.CombatExecutor.COMMITTED_ALPHA — and flipped the M1/M1b
# assertions from "flat" to "monotonic / personality-expressed". This mirrors
# the production _committed_reinforcement_strength model (α · strength ·
# effectiveness · attack_modifier · relationship_factor).
COMMITTED_ALPHA = 0.6

# CO-4 (Phase 2, LANDED July 13, 2026): per-corps regeneration is now CAPPED
# SYMMETRICALLY. The Field Review saw Mack reinforce +10,000 in a single turn
# while the best assault removed ~5,000 — frontal attrition was literally
# unwinnable. CO-4 caps ANY corps reinforcing in the field (no friendly depot
# or capital) to R men/turn — one rule keyed on the recruit region's supply,
# identical for player and enemy (GR5) — the SAME single-source value as
# production economy_executor.AI_CORPS_REGEN_CAP (guarded below) — so M3 flips
# from "defender GAINS" to "net <= -2000".
AI_CORPS_REGEN_PER_TURN = 3000

# Monte-Carlo seed set. 400 trials is ample for stable win-rates and runs in a
# fraction of a second (each resolve is microseconds).
SEEDS = tuple(range(400))
N = len(SEEDS)


def test_committed_alpha_matches_production():
    """Single-source guard: the harness α must equal the production α so the
    modelled M1/M1b curve tracks what combat resolution actually does."""
    from backend.commands.combat_executor import CombatExecutor
    assert COMMITTED_ALPHA == CombatExecutor.COMMITTED_ALPHA, (
        "Harness COMMITTED_ALPHA drifted from production "
        f"CombatExecutor.COMMITTED_ALPHA ({COMMITTED_ALPHA} != "
        f"{CombatExecutor.COMMITTED_ALPHA})")


def test_regen_cap_matches_production():
    """CO-4 single-source guard: the harness regen knob must equal the
    production field-regen cap so M3 models the capped code path."""
    from backend.commands.economy_executor import AI_CORPS_REGEN_CAP
    assert AI_CORPS_REGEN_PER_TURN == AI_CORPS_REGEN_CAP, (
        "Harness AI_CORPS_REGEN_PER_TURN drifted from production "
        f"economy_executor.AI_CORPS_REGEN_CAP ({AI_CORPS_REGEN_PER_TURN} != "
        f"{AI_CORPS_REGEN_CAP})")


# ════════════════════════════════════════════════════════════════════════════
# CONSTRUCTION HELPERS (mirror the idiom in test_terrain_combat_integration.py)
# ════════════════════════════════════════════════════════════════════════════

def _mk(name, strength, personality="aggressive", nation="France", *,
        morale=100, defense_bonus=0.0, stance=None, cavalry=False,
        artillery=False, ability=None, iron_stacks=0):
    """Build a fresh marshal for a single combat trial.

    Nations default apart (France vs Austria) so resolve_battle never trips its
    same-nation safety warning. Location is irrelevant to resolution.
    """
    m = Marshal(name, "TestField", int(strength), personality, nation)
    m.morale = morale
    m.defense_bonus = defense_bonus
    m.cavalry = cavalry
    m.artillery = artillery
    if stance is not None:
        m.stance = stance
    if ability is not None:
        m.ability = ability
    if iron_stacks:
        m.iron_resolve_stacks = iron_stacks
    return m


# A "dug-in" defender the way the review's Mack sat in Swabia: fortified in the
# mountains. Used by M1/M3/M6 (the concentration, attrition, and anti-over-nerf
# scenarios). terrain "mountains" = +25% defence (region.py), fort = +30%.
_DUG_IN_TERRAIN = "mountains"
_DUG_IN_FORT = 0.30
_DUG_IN_STRENGTH = 40000


def _dug_in_defender(strength=_DUG_IN_STRENGTH):
    return _mk("Mack", strength, "cautious", "Austria",
               morale=100, defense_bonus=0.15)


def _resolve(attacker, defender, terrain="plains", fort=0.0):
    """One real combat resolution (mutates both marshals)."""
    return CombatResolver().resolve_battle(
        attacker, defender, terrain=terrain, fortification_bonus=fort)


# ════════════════════════════════════════════════════════════════════════════
# M1 — Concentration monotonicity
# ════════════════════════════════════════════════════════════════════════════

def _assault_win_rate(lead_strength, reinforcer_contributions):
    """P(attacker wins) for a lead + committed reinforcers vs a dug-in
    defender, over the fixed seed set.

    Committed effective strength = lead + Σ contribution. At baseline every
    contribution is 0 (COMMITTED_ALPHA = 0), so the number of corps is inert —
    exactly the pathology. Phase 1 (CO-1) makes contribution non-zero and the
    curve rises.
    """
    committed = int(lead_strength + sum(reinforcer_contributions))
    wins = 0
    for s in SEEDS:
        random.seed(s)
        atk = _mk("Napoleon", committed, "aggressive", "France")
        deff = _dug_in_defender()
        res = _resolve(atk, deff, terrain=_DUG_IN_TERRAIN, fort=_DUG_IN_FORT)
        if res["attacker_won"]:
            wins += 1
    return wins / N


def _contribution(reinforcer_strength, personality, rel_factor):
    """CO-1b committed contribution of one reinforcer (spec §0.3 G-1b):
    α · strength · effectiveness · attack_multiplier · rel_factor, where
    attack_multiplier is `get_attack_modifier` READ straight from the
    reinforcer (it already returns 1+delta, e.g. 1.15 — GR1, never recomputed).

    At baseline α = 0 → 0 for every personality/relationship (reinforcements
    inert). Phase 1 (CO-1b) sets α and the personalities separate; the exact
    curve is sweep-tuned there.
    """
    r = _mk("Reinf", reinforcer_strength, personality, "France")
    eff = r.get_combat_effectiveness()
    atk_mult = r.get_attack_modifier(1.0)
    return COMMITTED_ALPHA * reinforcer_strength * eff * atk_mult * rel_factor


def measure_m1():
    """Win-rate for 1..5 committed corps of equal size vs a fixed defender."""
    lead = 40000
    reinf = 40000
    rates = []
    for n_corps in range(1, 6):
        contribs = [_contribution(reinf, "aggressive", 1.0)
                    for _ in range(n_corps - 1)]
        rates.append(_assault_win_rate(lead, contribs))
    return rates


def measure_m1b():
    """Committed contribution of one reinforcer of equal size, by personality.

    hostile-pair uses the MC-3 hostile coordination factor (×0.0); aggressive
    and cautious use a neutral (×1.0) relationship so only personality varies.
    """
    reinf = 40000
    return {
        "aggressive": _contribution(reinf, "aggressive", 1.0),
        "cautious": _contribution(reinf, "cautious", 1.0),
        "hostile_pair": _contribution(reinf, "aggressive", 0.0),
    }


def test_m1_concentration_is_monotonic():
    rates = measure_m1()
    print("\n[M1] committed-corps win-rate (1..5):",
          [round(r, 4) for r in rates])
    # CO-1 (Phase 1): committed corps add strength, so P(win) is strictly
    # non-decreasing as the force is massed, and committing the whole force is
    # decisively better than the lead alone. (Against the DUG-IN defender used
    # here — mountains+fort — the outright-destruction win only becomes likely
    # at the top of the ramp; morale-driven routs that make 3 corps decisive
    # land in Phase 2 / metric M2.)
    for i in range(len(rates) - 1):
        assert rates[i + 1] >= rates[i] - 1e-9, (
            f"M1 expected non-decreasing win-rate; corps {i+1}->{i+2} "
            f"dropped {rates[i]:.4f}->{rates[i+1]:.4f}")
    assert rates[-1] - rates[0] >= 0.30, (
        "M1 expected massing the full committed force to be decisively better "
        f"than the lead alone; 5-corps gain over 1-corps was {rates[-1] - rates[0]:.4f}")


def test_m1b_personality_expressed_in_mass():
    contribs = measure_m1b()
    print("\n[M1b] reinforcer committed contribution by personality:",
          {k: round(v, 2) for k, v in contribs.items()})
    # CO-1b (Phase 1): a reinforcer's committed contribution expresses their
    # OWN personality (attack modifier) and their relationship to the lead —
    # aggressive pushes harder than cautious of equal size, and a hostile-pair
    # reinforcer contributes nothing (×0.0 MC-3 factor).
    assert contribs["aggressive"] > contribs["cautious"] > contribs["hostile_pair"], (
        "M1b expected aggressive > cautious > hostile-pair; got "
        f"{contribs}")
    assert contribs["hostile_pair"] == 0.0


# ════════════════════════════════════════════════════════════════════════════
# M2 — Numerical decisiveness (rout within 2 turns at 2:1 & 3:1)
# ════════════════════════════════════════════════════════════════════════════

def _rout_within_two_turns(ratio):
    """P(the defender is forced to retreat within 2 sustained attacks) when the
    attacker is maintained at `ratio`:1 over equal (plains) terrain.

    The attacker is refreshed to full each turn (a maintained superior force);
    the defender's morale/strength carry between the two turns — measuring pure
    numerical decisiveness, not attrition of the attacker.
    """
    def_str = 40000
    routs = 0
    for s in SEEDS:
        random.seed(s)
        deff = _mk("Mack", def_str, "cautious", "Austria", morale=100)
        routed = False
        for _turn in range(2):
            atk = _mk("Napoleon", int(def_str * ratio), "aggressive", "France",
                      morale=100)
            res = _resolve(atk, deff, terrain="plains")
            if res["defender"]["forced_retreat"] or deff.strength <= 0:
                routed = True
                break
        if routed:
            routs += 1
    return routs / N


def measure_m2():
    return {"2:1": _rout_within_two_turns(2.0),
            "3:1": _rout_within_two_turns(3.0)}


def test_m2_decisiveness_at_target():
    m2 = measure_m2()
    print("\n[M2] rout-within-2-turns  2:1={:.4f}  3:1={:.4f}".format(
        m2["2:1"], m2["3:1"]))
    # CO-3 (Phase 2, LANDED July 13, 2026): a heavily-outnumbered defender who
    # bleeds far more than he inflicts breaks faster — the lopsided-exchange
    # morale penalty carries him across FORCED_RETREAT_THRESHOLD within two
    # sustained assaults. Target: >=0.35 @2:1, >=0.65 @3:1.
    assert m2["2:1"] >= 0.35, f"M2 @2:1 expected >=0.35; got {m2['2:1']:.4f}"
    assert m2["3:1"] >= 0.65, f"M2 @3:1 expected >=0.65; got {m2['3:1']:.4f}"


# ════════════════════════════════════════════════════════════════════════════
# M3 — Attrition winnability (net defender Δstrength/turn incl. AI regen)
# ════════════════════════════════════════════════════════════════════════════

def _mean_defender_casualties_sustained():
    """Mean defender casualties in one turn of a sustained 2:1 assault on a
    dug-in defender (fresh defender per trial — the conservative, steady-state
    per-turn attrition the combat model produces)."""
    def_str = 40000
    losses = []
    for s in SEEDS:
        random.seed(s)
        deff = _dug_in_defender(def_str)
        pre = deff.strength
        atk = _mk("Napoleon", int(def_str * 2), "aggressive", "France",
                  morale=100)
        _resolve(atk, deff, terrain=_DUG_IN_TERRAIN, fort=_DUG_IN_FORT)
        losses.append(pre - deff.strength)
    return statistics.mean(losses)


def measure_m3():
    mean_cas = _mean_defender_casualties_sustained()
    # Net change to the defender's strength per turn = what the AI regenerates
    # minus what a sustained superior assault removes. Baseline: the uncapped
    # regen (AI_CORPS_REGEN_PER_TURN) out-paces combat attrition ⇒ the defender
    # GAINS ground under attack. The combat half is measured from real
    # resolution; the regen half is the documented live model (CO-4 replaces it
    # with the capped code path).
    net = AI_CORPS_REGEN_PER_TURN - mean_cas
    return {"mean_casualties": mean_cas, "net_delta": net}


def test_m3_attrition_winnable_at_target():
    m3 = measure_m3()
    print("\n[M3] sustained 2:1 - mean casualties/turn={:.0f}  "
          "net defender delta/turn={:+.0f}".format(
              m3["mean_casualties"], m3["net_delta"]))
    # CO-4 (Phase 2, LANDED July 13, 2026): the field-regen cap (R=3,000) is
    # out-paced by a sustained superior assault, so a besieged defender net-
    # loses ground turn over turn. Target: net <= -2000.
    assert m3["net_delta"] <= -2000, (
        "M3 expected the defender to net-lose ground under sustained assault "
        f"(<= -2000); net was {m3['net_delta']:+.0f}")


# ════════════════════════════════════════════════════════════════════════════
# M4 — Report consistency in multi-marshal battles
# ════════════════════════════════════════════════════════════════════════════

def _executor():
    """A CombatExecutor whose only used method here is _distribute_casualties
    (the real proportional-distribution code). It needs a parent exposing a
    combat_resolver; nothing else is touched."""
    parent = SimpleNamespace(combat_resolver=CombatResolver())
    return CombatExecutor(parent)


def measure_m4():
    """Fraction of multi-marshal battles where the report's attacker_remaining
    agrees with the downstream event's remaining.

    The two-truths bug (pre-CO-5): the battle report derived attacker_remaining
    from the LEAD-vs-lead casualties (battle_report → original − whole-corps
    casualties), while the executor set the event remaining to the lead's
    strength AFTER distributing the total casualties across all participants —
    so the two disagreed in every multi-marshal battle.

    CO-5 (Phase 1) exercised here: resolve deferred (apply_casualties=False, as
    the real coordinated path does), distribute the raw casualties across
    [lead, reinforcer], apply the lead's share, then call the SAME production
    reconciliation the executor calls (_reconcile_report_survivors). Afterward
    the report's attacker_remaining and the event's remaining are ONE canonical
    value (the lead's post-distribution strength) → 100%.
    """
    ce = _executor()
    consistent = 0
    for s in SEEDS:
        random.seed(s)
        lead_orig, reinf_orig = 30000, 20000
        lead = _mk("Ney", lead_orig, "aggressive", "France")
        reinf = _mk("Soult", reinf_orig, "aggressive", "France")
        deff = _mk("Mack", 40000, "cautious", "Austria", defense_bonus=0.15)

        # Real DEFERRED resolution (coordinated path) — report built here, no
        # marshal state mutated. CO-1: the reinforcer commits strength too,
        # via the production helper (world unused for a same-nation pair).
        committed = ce._committed_reinforcement_strength(lead, [lead, reinf], None)
        res = CombatResolver().resolve_battle(
            lead, deff, terrain="plains", apply_casualties=False,
            committed_attacker=committed)
        report = res["battle_report"]

        # Real distribution of the whole-corps raw casualties across the
        # participants, then apply the lead's share (as the executor does).
        shares = ce._distribute_casualties(
            res["attacker_raw_casualties"], [lead, reinf])
        lead.take_casualties(shares.get("Ney", 0))
        deff.take_casualties(res["defender_raw_casualties"])

        # CO-5: the production reconciliation — both surfaces now read the
        # lead's post-distribution strength.
        ce._reconcile_report_survivors(res, lead, deff)
        report_remaining = report["casualty_summary"]["attacker_remaining"]
        event_remaining = int(lead.strength)

        if event_remaining == report_remaining:
            consistent += 1
    return consistent / N


def test_m4_report_consistent_in_multimarshal():
    rate = measure_m4()
    print("\n[M4] multi-marshal report consistency: {:.1%}".format(rate))
    # CO-5 (Phase 1): the report and the event read ONE canonical survivor
    # count → consistent in every multi-marshal battle.
    assert rate == 1.0, (
        f"M4 expected 100% consistency after CO-5; got {rate:.1%}")


# ════════════════════════════════════════════════════════════════════════════
# M5 — Iron Resolve payoff (stance-trapped)
# ════════════════════════════════════════════════════════════════════════════

def measure_m5():
    """Net attack modifier of releasing a 3-stack Iron Resolve vs attacking
    normally with no stacks.

    Stacks only accrue while fortified, which forces the DEFENSIVE stance
    (−10% attack). Releasing from that trapped stance eats most of the +24%,
    so the net payoff over a plain attack is small. CO-7 frees the stance and
    the payoff rises to >= +18% (M5 target).
    """
    trapped = _mk("Davout", 40000, "cautious", "France",
                  stance=Stance.DEFENSIVE, defense_bonus=0.16,
                  ability={"name": "Iron Resolve"}, iron_stacks=3)
    mod_trapped = trapped.get_attack_modifier(1.0)

    normal = _mk("Davout", 40000, "cautious", "France", stance=Stance.NEUTRAL)
    mod_normal = normal.get_attack_modifier(1.0)

    return {"trapped": mod_trapped, "normal": mod_normal,
            "payoff": mod_trapped - mod_normal}


def test_m5_iron_resolve_payoff_at_target():
    m5 = measure_m5()
    print("\n[M5] iron-resolve payoff: trapped={:.3f} normal={:.3f} "
          "net={:+.3f}".format(m5["trapped"], m5["normal"], m5["payoff"]))
    # CO-7 (Phase 2, LANDED July 13, 2026): releasing the coil no longer
    # self-cancels against the fortify-mandated defensive stance — the +24%
    # lands in full. Target: payoff >= +0.18.
    assert m5["payoff"] >= 0.18, (
        f"M5 expected payoff >= +0.18 after CO-7; got {m5['payoff']:+.3f}")


# ════════════════════════════════════════════════════════════════════════════
# M6 — Defender still matters (anti-over-nerf GUARD — must hold every phase)
# ════════════════════════════════════════════════════════════════════════════

def measure_m6():
    """P(attacker wins) for a SOLO equal-strength assault into fort+mountains.
    Must stay defender-favourable (attacker win-rate < 0.5) across every phase
    — this is the guard that the decisiveness work does not trivialise
    defence."""
    wins = 0
    for s in SEEDS:
        random.seed(s)
        atk = _mk("Napoleon", 40000, "aggressive", "France", morale=100)
        deff = _mk("Mack", 40000, "cautious", "Austria", morale=100)
        res = _resolve(atk, deff, terrain="mountains", fort=0.30)
        if res["attacker_won"]:
            wins += 1
    return wins / N


def test_m6_defender_favourable_guard():
    rate = measure_m6()
    print("\n[M6] solo equal-strength into fort+mountains - "
          "attacker win-rate: {:.4f}".format(rate))
    # GUARD (holds every phase): defence remains meaningful.
    assert rate < 0.5, (
        f"M6 guard breached — attacker win-rate into fort+mountains was {rate:.4f} "
        "(defence should stay favourable)")


# ════════════════════════════════════════════════════════════════════════════
# M7 — Drama liveness (turns until a jealousy trigger fires)
# ════════════════════════════════════════════════════════════════════════════

_SCENARIO_PATH = (
    Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
    / "assets" / "maps" / "europe_1805.json"
)

_M7_NEVER = 999  # sentinel: no trigger fired within the scripted horizon


def _france_standing(world):
    return [m for m in world.marshals.values()
            if m.nation == world.player_nation and m.strength > 0
            and not getattr(m, "captured_by", "")]


# The review's WINNABLE concentration. After Phases 1-2 (additive committed
# strength + decisiveness) a marshal who MASSES his force grinds a dug-in
# defender down instead of stalemating forever — the ~3:1 concentration the
# review used to grind Mack 52k->21.7k. We model that as a decisive assault
# against a defender dug in at roughly a third of the committed force, so the
# attacker out-DAMAGES (the situation the triple lock actually starved: a
# player winning the attrition who earns no glory for it). The original Phase-0
# harness modeled a 1:1 assault where the attacker is out-BLED and simply
# loses every battle — zero glory is correct there (no laurels for losing), so
# it never reproduced the lock. This is the faithful post-Phase-2 regime.
_M7_ASSAULT_ENEMY_FRAC = 0.35


def measure_m7(horizon=8):
    """Turns until any France marshal develops a grievance, in an 8-turn
    massed-assault run at high authority — the reviewed play pattern, now
    winnable. Returns the first trigger turn, or _M7_NEVER.

    The triple lock (spec §3.2) is what kept this dormant BEFORE Phase 3:
    (1) the hard-fought out-damaging stalemate awarded ZERO glory, (2) any
    stray point decayed inside a 5-turn window, and (3) authority 100 raised
    every jealousy threshold by one. Phase 3 breaks all three — DR-1 scores the
    out-damaging grind, DR-2 lets it accrete (window 8), DR-3 exempts the
    hair-trigger rival from the winning-army dampening — so a grievance forms.
    """
    world = WorldState.from_dict(
        WorldState.from_scenario(str(_SCENARIO_PATH)).to_dict())
    world.authority_tracker.authority = 100  # winning army: dampening active
    roster = _france_standing(world)[:4]  # a handful of engaged marshals

    for turn in range(1, horizon + 1):
        world.current_turn = turn
        random.seed(10_000 + turn)
        for marshal in roster:
            # Each marshal commits a massed force (~3:1) against a fresh dug-in
            # enemy — he out-damages the grind but the fortified defender
            # resists a clean rout, exactly the review's Mack assault.
            enemy = _mk("EnemyCorps",
                        int((marshal.strength or 40000) * _M7_ASSAULT_ENEMY_FRAC),
                        "cautious", "Austria", morale=100, defense_bonus=0.15)
            pre_atk = marshal.strength
            pre_def = enemy.strength
            res = _resolve(marshal, enemy, terrain=_DUG_IN_TERRAIN,
                           fort=_DUG_IN_FORT)
            outcome = res["outcome"]
            atk_won = outcome in ("attacker_victory", "attacker_tactical_victory")
            def_won = outcome in ("defender_victory", "defender_tactical_victory")
            # Mark the marshal engaged so the literal-sidelining path (which
            # keys off idle HOLD while peers fight) does not spuriously fire —
            # everyone is fighting the frontal war, exactly as in the review.
            marshal.attacks_this_turn = 1
            marshal.in_combat_this_turn = True
            J.record_battle_glory(
                world, marshal, enemy, atk_won, def_won,
                res["attacker"]["casualties"], res["defender"]["casualties"],
                conquered=False, is_garrison=False,
                pre_attacker_strength=pre_atk, pre_defender_strength=pre_def)

        world._jealousy_processed_turn = None
        J.process_turn(world)

        if any(getattr(m, "jealous_of", None) for m in _france_standing(world)):
            return turn

    return _M7_NEVER


def test_m7_drama_comes_alive():
    first = measure_m7()
    shown = "never" if first == _M7_NEVER else f"turn {first}"
    print("\n[M7] first jealousy trigger over 8 turns: {}".format(shown))
    # PHASE 3: the triple lock is broken (DR-1 glory-from-attrition, DR-2 slow
    # decay, DR-3 authority-dampening rework), so a grievance forms within the
    # 8-turn horizon in the winnable massed-assault run. Target: M7 <= 8.
    assert 1 <= first <= 8, (
        f"M7 (Phase 3) expected a jealousy trigger within 8 turns; got "
        f"{'never' if first == _M7_NEVER else first}")


# ════════════════════════════════════════════════════════════════════════════
# SWEEP TABLE — prints (and optionally writes) the full Sweep-0 scoreboard
# ════════════════════════════════════════════════════════════════════════════

def test_zz_emit_sweep_table():
    """Assemble every metric into one table (visible with -s). If SWEEP_OUT is
    set, also write a markdown table for docs/audits/SWEEP_<n>_<date>.md."""
    m1 = measure_m1()
    m1b = measure_m1b()
    m2 = measure_m2()
    m3 = measure_m3()
    m4 = measure_m4()
    m5 = measure_m5()
    m6 = measure_m6()
    m7 = measure_m7()
    m7_shown = "never (>8)" if m7 == _M7_NEVER else f"turn {m7}"

    rows = [
        ("M1", "concentration win-rate 1->5 corps",
         " -> ".join(f"{r:.3f}" for r in m1), "strictly non-decreasing; 3 >> 1"),
        ("M1b", "reinforcer contribution agg/cau/hostile",
         f"{m1b['aggressive']:.1f}/{m1b['cautious']:.1f}/{m1b['hostile_pair']:.1f}",
         "aggressive > cautious > hostile"),
        ("M2", "rout <=2 turns  2:1 / 3:1",
         f"{m2['2:1']:.3f} / {m2['3:1']:.3f}", ">=0.35 @2:1, >=0.65 @3:1"),
        ("M3", "net defender delta-strength/turn (sustained 2:1)",
         f"{m3['net_delta']:+.0f}  (cas {m3['mean_casualties']:.0f} vs regen {AI_CORPS_REGEN_PER_TURN})",
         "<= -2000"),
        ("M4", "multi-marshal report consistency",
         f"{m4:.1%}", "100%"),
        ("M5", "iron-resolve 3-stack payoff",
         f"{m5['payoff']:+.3f}", ">= +0.18"),
        ("M6", "attacker win-rate into fort+mountains (GUARD)",
         f"{m6:.3f}", "< 0.5 (holds all phases)"),
        ("M7", "first jealousy trigger / 8-turn run",
         m7_shown, "<= 8"),
    ]

    header = f"\n{'='*78}\nSWEEP 0 - Combat Overhaul baseline (Half A, {N} seeds)\n{'='*78}"
    print(header)
    for mid, name, baseline, target in rows:
        print(f"  {mid:<4} {name:<44} = {baseline}")
        print(f"       {'':<44}   target: {target}")

    out = os.environ.get("SWEEP_OUT")
    if out:
        lines = ["| ID | Metric | Baseline (measured) | Target |",
                 "|----|--------|---------------------|--------|"]
        for mid, name, baseline, target in rows:
            lines.append(f"| {mid} | {name} | `{baseline}` | {target} |")
        Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\n[sweep] wrote markdown table -> {out}")

    # Sanity: the table assembled without error and M7 produced a value.
    assert m7 == _M7_NEVER or 1 <= m7 <= 8

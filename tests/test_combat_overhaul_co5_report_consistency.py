"""Combat Overhaul Phase 1 — CO-5 single-source survivor count.

Owner: docs/COMBAT_OVERHAUL_SPEC.md §4 Phase 1 (metric M4). The pre-CO-5 bug:
in a coordinated battle the battle report derived attacker_remaining from the
LEAD-vs-lead casualties while the event carried the lead's strength AFTER the
total casualties were distributed across all participants — the two surfaces
contradicted each other in every multi-marshal battle.

CO-5: after distribution the executor calls _reconcile_report_survivors so the
report's casualty_summary and the event read ONE canonical value (the primary's
actual post-battle strength). Solo battles are unaffected.
"""

import random
from types import SimpleNamespace

from backend.commands.combat_executor import CombatExecutor
from backend.game_logic.combat import CombatResolver
from backend.models.marshal import Marshal


def _mk(name, strength, personality="aggressive", nation="France", *,
        morale=100, defense_bonus=0.0):
    m = Marshal(name, "TestField", int(strength), personality, nation)
    m.morale = morale
    m.defense_bonus = defense_bonus
    return m


def _executor():
    return CombatExecutor(SimpleNamespace(combat_resolver=CombatResolver()))


def test_report_matches_event_after_distribution():
    """The report's attacker_remaining equals the lead's distributed strength
    (the value the event carries) in every multi-marshal battle."""
    ce = _executor()
    for s in range(200):
        random.seed(s)
        lead = _mk("Ney", 30000)
        reinf = _mk("Soult", 20000)
        deff = _mk("Mack", 40000, "cautious", "Austria", defense_bonus=0.15)

        committed = ce._committed_reinforcement_strength(lead, [lead, reinf], None)
        res = CombatResolver().resolve_battle(
            lead, deff, terrain="plains", apply_casualties=False,
            committed_attacker=committed)

        atk_shares = ce._distribute_casualties(
            res["attacker_raw_casualties"], [lead, reinf])
        def_shares = ce._distribute_casualties(
            res["defender_raw_casualties"], [deff])
        lead.take_casualties(atk_shares.get("Ney", 0))
        reinf.take_casualties(atk_shares.get("Soult", 0))
        deff.take_casualties(def_shares.get("Mack", 0))

        ce._reconcile_report_survivors(res, lead, deff)

        cs = res["battle_report"]["casualty_summary"]
        assert cs["attacker_remaining"] == int(lead.strength)
        assert cs["defender_remaining"] == int(deff.strength)
        # casualties reconcile with original − remaining on the same surface
        assert cs["attacker_casualties"] == cs["attacker_original"] - cs["attacker_remaining"]
        assert cs["defender_casualties"] == cs["defender_original"] - cs["defender_remaining"]


def test_reconcile_uses_only_lead_share_not_whole_corps():
    """The reconciled attacker_casualties reflect the LEAD's distributed share,
    not the whole-corps raw total (the two-truths fix)."""
    ce = _executor()
    random.seed(7)
    lead = _mk("Ney", 30000)
    reinf = _mk("Soult", 20000)
    deff = _mk("Mack", 40000, "cautious", "Austria", defense_bonus=0.15)
    res = CombatResolver().resolve_battle(
        lead, deff, terrain="plains", apply_casualties=False)

    raw = res["attacker_raw_casualties"]
    shares = ce._distribute_casualties(raw, [lead, reinf])
    lead_share = shares.get("Ney", 0)
    lead.take_casualties(lead_share)
    deff.take_casualties(res["defender_raw_casualties"])

    # Pre-reconcile: the report still carries the whole-corps raw total.
    assert res["battle_report"]["casualty_summary"]["attacker_casualties"] == raw

    ce._reconcile_report_survivors(res, lead, deff)
    cs = res["battle_report"]["casualty_summary"]
    assert cs["attacker_casualties"] == lead_share
    assert lead_share < raw  # the lead only absorbed its proportional share


def test_reconcile_is_safe_when_no_report():
    """Helper is a no-op on a result without a battle_report/casualty_summary."""
    ce = _executor()
    lead = _mk("Ney", 30000)
    deff = _mk("Mack", 40000, "cautious", "Austria")
    # Must not raise.
    ce._reconcile_report_survivors({}, lead, deff)
    ce._reconcile_report_survivors({"battle_report": {}}, lead, deff)


def test_solo_battle_report_unaffected():
    """A solo battle (apply_casualties=True) never touches the reconciler; its
    report already reads original − casualties for the sole combatant."""
    random.seed(42)
    atk = _mk("Napoleon", 40000)
    deff = _mk("Mack", 40000, "cautious", "Austria", defense_bonus=0.15)
    res = CombatResolver().resolve_battle(atk, deff, terrain="plains")
    cs = res["battle_report"]["casualty_summary"]
    assert cs["attacker_remaining"] == cs["attacker_original"] - cs["attacker_casualties"]
    assert cs["attacker_remaining"] == int(atk.strength)

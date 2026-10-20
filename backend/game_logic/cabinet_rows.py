"""The Cabinet's rows for the diplomatic acts that had only a typed road
(the user's rule, October 20, 2026: "diplomacy is never typed" — every
diplomatic and naval act has a UI control carrying everything it needs;
`docs/BUG_FIXES.md` §PC PC-X42 … ; rules `SYSTEMS_REFERENCE.md` §134.7).

Each row is built from the SAME gates its executor reads, so the button is
offered exactly where the order would act, and disabled with the
executor's own words where it would be refused (the CN-4 chip-honesty
rule). The war purpose's row lives with the war's articles
(`declared_goals.war_purpose_action`).

    amends_actions      Make Amends — clear a strike (200g + 1 DP) or, the
                        grievance variant, an abandoned alliance (400g + 2 DP)
                        — `diplomatic_executor._execute_make_amends`
    repudiate_actions   Repudiate the Bargain — one row per live war bargain
                        France promised this court, through the existing
                        confirmation (`_execute_repudiate_bargain`)
    recognition_actions Offer Gold for Recognition — the Congress's
                        sweetener, sums chosen on the row (PC-X46)
    subjugate_actions   Subjugate — the beaten court made a vassal by
                        conquest (PC-X47)

Beside them in `diplomacy.get_available_diplomatic_actions`: the bid's sums
(PC-X45), the treaty ladder's skip-ahead choices (PC-X48), the sponsor's
licence and sums (PC-X49), the autonomy jumps (PC-X50) — each a row's
`choices`, which the wizard renders as indented buttons.
"""
from __future__ import annotations

from typing import Any, Dict, List

AMENDS_STANDARD = "make_amends"
AMENDS_GRIEVANCE = "make_amends_grievance"


def _amends_costs() -> Dict[str, Dict[str, int]]:
    """The executor's own prices (one home: `DiplomaticExecutor`)."""
    from backend.commands.diplomatic_executor import DiplomaticExecutor as DE
    return {
        AMENDS_STANDARD: {"gold": int(DE._MAKE_AMENDS_GOLD_COST), "dp": int(DE._MAKE_AMENDS_DP_COST),
                          "reliability": int(DE._MAKE_AMENDS_RELIABILITY_REWARD),
                          "relation": int(DE._MAKE_AMENDS_RELATION_REWARD),
                          "cooldown": int(DE._MAKE_AMENDS_COOLDOWN_TURNS)},
        AMENDS_GRIEVANCE: {"gold": int(DE._MAKE_AMENDS_GRIEVANCE_GOLD_COST),
                           "dp": int(DE._MAKE_AMENDS_GRIEVANCE_DP_COST),
                           "reliability": int(DE._MAKE_AMENDS_GRIEVANCE_RELIABILITY_REWARD),
                           "relation": int(DE._MAKE_AMENDS_GRIEVANCE_RELATION_REWARD),
                           "cooldown": int(DE._MAKE_AMENDS_COOLDOWN_TURNS)},
    }


def amends_actions(world: Any, player: str, target: str) -> List[Dict[str, Any]]:
    """PC-X43: Make Amends on the wronged court's page — a row per variant
    the pair has something to repair with (a strike; an abandoned
    alliance's grievance), its refusal the executor's own words in the
    executor's own order (the state, the shared cooldown, the DP, the
    gold). No strike and no grievance — no row: nothing to repair."""
    from backend.display_names import AMENDS_REFUSAL_DISPLAY
    from backend.game_logic.diplomacy import (
        _NON_WAR_TREATY_STATES, _betrayal_key, _get_grievance_flags,
    )
    record = ((getattr(world, "betrayal_history", {}) or {})
              .get(_betrayal_key(player, target)) or {})
    has = {AMENDS_STANDARD: bool(record.get("strikes")),
           AMENDS_GRIEVANCE: bool(_get_grievance_flags(world, player, target))}
    if not any(has.values()):
        return []
    costs = _amends_costs()
    turn = int(getattr(world, "current_turn", 0) or 0)
    common = ""
    if world.get_diplomatic_state(player, target) not in _NON_WAR_TREATY_STATES:
        common = AMENDS_REFUSAL_DISPLAY["war_or_armistice"].format(nation=target)
    else:
        expiry = int((getattr(world, "reparations_cooldown", {}) or {})
                     .get(world._make_diplo_key(player, target), 0) or 0)
        if expiry > turn:
            since = max(0, costs[AMENDS_STANDARD]["cooldown"] - (expiry - turn))
            common = AMENDS_REFUSAL_DISPLAY["cooldown_active"].format(nation=target, turns_since=since)
    dp = int(getattr(world, "diplomatic_points", 0) or 0)
    gold = int((getattr(world, "nation_gold", {}) or {}).get(player, 0) or 0)
    rows: List[Dict[str, Any]] = []
    for action, label, what in (
            (AMENDS_STANDARD, "Make Amends", "clear one strike"),
            (AMENDS_GRIEVANCE, "Make Amends for the Abandoned Alliance", "clear one grievance")):
        if not has[action]:
            continue
        c = costs[action]
        why = common
        if not why and dp < c["dp"]:
            why = AMENDS_REFUSAL_DISPLAY["insufficient_dp"].format(
                nation=target, required=c["dp"], available=dp)
        if not why and gold < c["gold"]:
            why = AMENDS_REFUSAL_DISPLAY["insufficient_gold"].format(
                nation=target, required=c["gold"], available=gold)
        rows.append({
            "action": action, "display_name": label,
            "dp_cost": c["dp"], "gold_cost": c["gold"],
            "available": not why, "disabled_reason": why, "disabled_reason_display": why,
            "effect_text": (f"{what} — our word +{c['reliability']}, relations "
                            f"+{c['relation']}; then {c['cooldown']} turns before another"),
        })
    return rows


def repudiate_actions(world: Any, player: str, target: str) -> List[Dict[str, Any]]:
    """PC-X44: Repudiate the Bargain on the ally's page — one row for the
    live war bargain France promised this court (the claim it promised),
    through the executor's own confirmation with the breach's price."""
    from backend.game_logic.diplomacy import _get_live_bargains_by_promiser
    rows: List[Dict[str, Any]] = []
    for b in _get_live_bargains_by_promiser(world, player):
        if str(b.get("beneficiary") or "") != target:
            continue
        claim = str((b.get("claim_term") or {}).get("claim_region") or "the claim")
        rows.append({
            "action": "repudiate_bargain", "display_name": "Repudiate the Bargain",
            "dp_cost": 0, "available": True, "disabled_reason": "",
            "effect_text": (f"break our promise of {claim} — France takes the breach: a betrayal "
                            f"strike, our word marked (you confirm first)"),
            "bargain_id": str(b.get("id") or ""),
        })
        break
    return rows


RECOGNITION_SUMS = (500, 1000, 2000)


def recognition_actions(world: Any, player: str, target: str) -> List[Dict[str, Any]]:
    """PC-X46: the Congress's sweetener — gold laid before a great power at
    the table — on that court's page while the Congress sits, one choice
    per sum the Congress would take (`congress.sweetener_refusal`, the
    executor's own gate) and the chest can pay."""
    from backend.game_logic import congress as C
    if not C.sitting(world) or target not in C.great_powers(world):
        return []
    gold = int((getattr(world, "nation_gold", {}) or {}).get(player, 0) or 0)
    dp = int(getattr(world, "diplomatic_points", 0) or 0)
    choices = [{"label": f"Offer {amount:,} gold", "payload": {"amount": int(amount)}}
               for amount in RECOGNITION_SUMS
               if amount <= gold and not C.sweetener_refusal(world, target, amount)]
    # Open while ANY sum is takeable; else the smallest sum's own refusal.
    why = "" if choices else (C.sweetener_refusal(world, target, RECOGNITION_SUMS[0])
                              or f"The treasury holds {gold:,}g — not enough for a sweetener.")
    if not why and dp < int(C.SWEETENER_DP_COST):
        why = f"Insufficient DP (need {int(C.SWEETENER_DP_COST)})."
    return [{
        "action": "recognition_sweetener", "display_name": "Offer Gold for Recognition",
        "dp_cost": int(C.SWEETENER_DP_COST), "available": not why,
        "disabled_reason": why, "disabled_reason_display": why,
        "effect_text": (f"+{int(C.SWEETENER_PER_1000)} at the table per 1,000 gold, up to "
                        f"+{int(C.SWEETENER_CAP)} — the Congress sits"),
        "choices": choices,
    }]


def subjugate_actions(world: Any, player: str, target: str) -> List[Dict[str, Any]]:
    """PC-X47: the beaten court made a vassal by conquest — on its WAR page,
    for a court small enough to be vassalized at all (the power cap), shut
    in the executor's own words until it is beaten
    (`vassal.subjugation_refusal`); the peace table's vassalage clause is
    the other road."""
    if world.get_diplomatic_state(player, target) != "WAR":
        return []
    if target in (getattr(world, "vassals", {}) or {}):
        return []
    from backend.game_logic.diplomacy import check_vassalage_power_cap
    if not check_vassalage_power_cap(world, player, target).get("allowed"):
        return []
    from backend.game_logic.vassal import subjugation_refusal
    why = ""
    cooldown = int((getattr(world, "vassal_release_cooldowns", {}) or {}).get(target, 0) or 0)
    if cooldown > 0:
        why = f"Recently released — {cooldown} turns before she can be made a vassal again."
    if not why:
        why = subjugation_refusal(world, player, target) or ""
    return [{
        "action": "subjugate", "display_name": "Subjugate",
        "dp_cost": 0, "available": not why, "disabled_reason": why, "disabled_reason_display": why,
        "effect_text": "make her France's vassal by conquest — she must be beaten first",
    }]

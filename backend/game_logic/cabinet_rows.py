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
    bond_actions        PC-R7 (ii) part 3, the league's bond (Chaumont): Bind
                        <ally> to the War (one choice per shared enemy) and
                        Outbid <payer>'s Bond (the table with her alone, the
                        bid staged)
    lever_table_actions S14E-D7 / S14E-X34, the counsel's lever: Open
                        Settlement with <court> alone, the payment that
                        carries her staged (`gold_offer`, the counsel's own
                        `gold_to_carry`), and `lever_offer_opening_terms`,
                        the draft the open-settlement arm stages

Beside them in `diplomacy.get_available_diplomatic_actions`: the bid's sums
(PC-X45), the treaty ladder's skip-ahead choices (PC-X48), the sponsor's
licence and sums (PC-X49), the autonomy jumps (PC-X50) — each a row's
`choices`, which the wizard renders as indented buttons.
"""
from __future__ import annotations

from typing import Any, Dict, List

from backend.display_names import plural as _plural  # LV-9: the count and its noun

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


def amends_gold_refusal(world: Any, player: str, target: str, required: int) -> str:
    """S14E-X186 — why the reparations' gold is short, in the table's words;
    '' when the CHEST pays `required`.

    The ONE gate of Make Amends' gold: the executor (both variants), the
    Cabinet row and the quote's "would hold N after" read the same chest
    (`instruments.chest_of` — the treasury less the recurring settlement
    payments still owed, the figure the sweetener, the buy-off and the lever
    text name). With nothing owed the chest IS the treasury and the sentence is
    the one it was; where the two differ it says so (`FREE_OF_OBLIGATIONS`)."""
    from backend.display_names import AMENDS_REFUSAL_DISPLAY
    from backend.game_logic.instruments import FREE_OF_OBLIGATIONS, chest_of
    treasury, chest = chest_of(world, player)
    if chest >= int(required):
        return ""
    shown = f"{chest} gold{FREE_OF_OBLIGATIONS}" if chest < treasury else chest
    return AMENDS_REFUSAL_DISPLAY["insufficient_gold"].format(
        nation=target, required=required, available=shown)


def amends_price_words(variant: str = AMENDS_GRIEVANCE) -> str:
    """S14E-10: the price of a Make Amends variant as the executor charges it
    ("400g + 2 DP" for the grievance variant) — read from `_amends_costs`,
    never typed again, so every surface that STATES the cure before the
    click (the table's forecast, the chip, the dispatch) quotes the number
    the Cabinet's row and the executor spend."""
    cost = _amends_costs()[variant]
    return f"{cost['gold']}g + {cost['dp']} DP"


def oldest_grievance_type(world: Any, player: str, target: str) -> str:
    """The `grievance_type` of the flag Make Amends (grievance variant) would
    clear — the executor's own FIFO choice (`_remove_oldest_grievance_flag`:
    oldest turn, then episode id); "" when the pair holds none or the flag
    carries no type."""
    from backend.game_logic.diplomacy import _get_grievance_flags
    flags = _get_grievance_flags(world, player, target)
    if not flags:
        return ""
    oldest = min(flags, key=lambda f: (int(f.get("turn", 0) or 0), str(f.get("episode_id", ""))))
    return str(oldest.get("grievance_type") or "")


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
    rows: List[Dict[str, Any]] = []
    # S14E-10: the grievance row names the flag it would clear (the oldest,
    # the executor's FIFO) — a shut-out is not an "abandoned alliance".
    from backend.display_names import grievance_kind_display
    grievance_label = (grievance_kind_display(oldest_grievance_type(world, player, target))["amends"]
                       if has[AMENDS_GRIEVANCE] else "")
    for action, label, what in (
            (AMENDS_STANDARD, "Make Amends", "clear one strike"),
            (AMENDS_GRIEVANCE, grievance_label, "clear one grievance")):
        if not has[action]:
            continue
        c = costs[action]
        why = common
        if not why and dp < c["dp"]:
            why = AMENDS_REFUSAL_DISPLAY["insufficient_dp"].format(
                nation=target, required=c["dp"], available=dp)
        if not why:
            # S14E-X186: the executor's own gate (the chest), not the raw coffers
            why = amends_gold_refusal(world, player, target, c["gold"])
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
    # S14E-X191: ONE read of the executor's gate - `sweetener_refusal` checks
    # the points and then the gold on `instruments.chest_of` (S14E-X157), so
    # no raw-coffers filter stands beside it, no raw fallback sentence is left
    # to say another figure, and no points check follows it (it would be
    # unreachable: a sum is takeable only when the points are there).
    choices = [{"label": f"Offer {amount:,} gold", "payload": {"amount": int(amount)}}
               for amount in RECOGNITION_SUMS
               if not C.sweetener_refusal(world, target, amount)]
    # Open while ANY sum is takeable; else the smallest sum's own refusal (the
    # smallest sum takeable would be a choice, so a shut row always has one).
    why = "" if choices else (C.sweetener_refusal(world, target, RECOGNITION_SUMS[0]) or "")
    return [{
        "action": "recognition_sweetener", "display_name": "Offer Gold for Recognition",
        "dp_cost": int(C.SWEETENER_DP_COST), "available": not why,
        "disabled_reason": why, "disabled_reason_display": why,
        "effect_text": (f"+{int(C.SWEETENER_PER_1000)} at the table per 1,000 gold, up to "
                        f"+{int(C.SWEETENER_CAP)} — the Congress sits"),
        "choices": choices,
    }]


def bond_actions(world: Any, player: str, target: str,
                 actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """PC-R7 (ii) part 3 — the league's no-separate-peace bond (Chaumont), on
    the court's page, from the bond's own gate (`bond.mint_refusal`) and price:

    * **Bind <court> to the War** — on a co-belligerent's page: France pays
      her own subsidy a turn for the term, and the court makes no separate
      peace with the enemy we share; one choice per shared enemy the gate
      lets France bind her against (`diplomatic_executor._execute_bind_to_war`).
    * **Outbid <payer>'s Bond** — on a court at war with France that the
      league's paymaster binds: the bond's price named, and the table with
      her alone opened with France's bid staged (the gold that pays the
      bond's table price — `bond.bid_gold`), through Open Settlement's own
      gate (the row beside it). S14E-X127: shut, with the shortfall in words,
      where the chest (`bond.bid_funds`) cannot pay the bid."""
    from backend.game_logic import bond as B
    from backend.game_logic.instruments import INSTRUMENT_DP_COST
    from backend.display_names import display_nation as _dn
    rows: List[Dict[str, Any]] = []
    dp = int(getattr(world, "diplomatic_points", 0) or 0)
    shared = B.shared_enemies(world, player, target)
    if shared:
        amount = B.bond_amount(world, player)
        choices = [{"label": f"Against {_dn(enemy)} — no separate peace with {_dn(enemy)}",
                    "payload": {"enemy": enemy}}
                   for enemy in shared if not B.mint_refusal(world, player, target, enemy)]
        why = "" if choices else B.mint_refusal(world, player, target, shared[0])
        if dp < INSTRUMENT_DP_COST:
            why = f"Insufficient DP (need {int(INSTRUMENT_DP_COST)})."
        rows.append({
            "action": "bind_to_war", "display_name": f"Bind {_dn(target)} to the War ({amount}g/turn)",
            "dp_cost": int(INSTRUMENT_DP_COST), "available": not why,
            "disabled_reason": why, "disabled_reason_display": why,
            "effect_text": (f"France pays her {amount} gold a turn for {B.bond_term_turns()} turns; she "
                            f"makes no separate peace while France fights on — one inside the term "
                            f"is a broken bargain (Chaumont)"),
            "choices": choices if not why else [],
        })
    record = B.bond_on(world, target, player) if world.is_at_war(player, target) else None
    table = next((a for a in actions if a.get("action") == "open_settlement"), None)
    if record is not None and table is not None:
        payer = _dn(str(record.get("payer")))
        gold = B.bid_gold(world, record)
        # S14E-X127: the chest is the lever's (`bond.bid_funds`), the one the
        # price line quotes - a bid the chest cannot pay is neither offered
        # (no choice) nor left an open control: the row is shut with the
        # shortfall in words, and `bid_short_by` marks it as shut for gold
        # alone (the counsel's path to the row stays named,
        # `counsel._outbid_path`). The table's own refusal comes first.
        funds = B.bid_funds(world, player)
        short = max(0, int(gold) - int(funds))
        why = "" if table.get("available") else str(table.get("disabled_reason_display")
                                                     or table.get("disabled_reason") or "")
        shut_for_gold = bool(short) and not why
        if shut_for_gold:
            why = f"The treasury holds {int(funds):,} gold — the bid is {int(gold):,}, {short:,} short."
        choices = ([{"label": f"Open the table with {gold:,} gold to {_dn(target)} "
                              f"(+{B.table_price(world, record)})",
                     "payload": {"bond_bid": int(gold)}}] if not short else [])
        row = {
            "action": "outbid_bond", "display_name": f"Outbid {payer}'s Bond — {_dn(target)} alone at the table",
            "dp_cost": 0, "available": not why, "disabled_reason": why, "disabled_reason_display": why,
            "effect_text": B.price_line(world, target, player,
                                        war_instance=(getattr(world, "war_instances", {}) or {})
                                        .get(str(table.get("war_id") or "")) or {}),
            "war_id": str(table.get("war_id") or ""), "counsel_coverage": [target],
            "choices": choices if not why else [],
        }
        if shut_for_gold:
            row["bid_short_by"] = int(short)
        rows.append(row)
    return rows


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
        why = f"Recently released — {_plural(cooldown, 'turn')} before she can be made a vassal again."
    if not why:
        why = subjugation_refusal(world, player, target) or ""
    return [{
        "action": "subjugate", "display_name": "Subjugate",
        "dp_cost": 0, "available": not why, "disabled_reason": why, "disabled_reason_display": why,
        "effect_text": "make her France's vassal by conquest — she must be beaten first",
    }]


def _lever_headroom(world: Any, payer: str, terms: List[Dict[str, Any]]) -> int:
    """What `payer` can still fund at the table beside `terms` — the settlement
    validator's own budget (`compute_gold_payer_budgets`: the treasury, any
    income over the longest recurring line, less the payments already owed)
    less the gold `terms` already commit: the bound a guided gold line is
    refused above (`settlement_actions._gold_headroom_for_payer`) and a
    ratification is bounced above."""
    from backend.game_logic.settlement_validation import compute_gold_payer_budgets
    used = 0
    for term in terms:
        if (term.get("type") in ("gold_indemnity", "gold_lump", "gold_per_turn")
                and str(term.get("from") or "") == payer):
            amount = abs(int(term.get("amount", 0) or 0))
            used += (amount * max(0, int(term.get("turns", 0) or 0))
                     if term.get("type") == "gold_per_turn" else amount)
    return max(0, int(compute_gold_payer_budgets(world, terms, [payer]).get(payer, 0)) - used)


def _lever_funds(world: Any, payer: str) -> int:
    """What `payer` can fund as a lump at the table with nothing else staged."""
    return _lever_headroom(world, payer, [])


def lever_table_actions(world: Any, player: str, target: str,
                        actions: List[Dict[str, Any]],
                        roads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """S14E-D7 / S14E-X34 (S14f part 2) — the counsel's lever has a control.

    Where the court alone does not carry but a payment would, Talleyrand says
    so (`counsel._lever_sentence`): "A payment of 875 gold to Britain would
    carry the table with her alone. At the table: Open Settlement with Britain
    alone, then Offer gold to Britain, 875 or more …". The Cabinet carried no
    row for that road — the counsel stamps the alone coverage only on the road
    that CARRIES, and a lever is said only where the alone table does not — and
    the table's offer row, once reached, opened at its default (300), six
    presses of + short of the sum. This row IS the road: `open_settlement` over
    the court alone, its `gold_offer` the very `gold_to_carry` the sentence
    quotes, which the open-settlement arm stages
    (`lever_offer_opening_terms`) the way the Outbid row's `bond_bid` stages the
    bid. A table opened any other way keeps its default.

    Funded or not at all: a sum beyond what the treasury can fund at the table
    is named on the row (what the lever costs, what the chest can fund) and
    carries no `gold_offer` — an overdrawn line is neither promised nor staged.
    Where the court IS the whole table the one `open_settlement` row carries
    the sum in place; elsewhere the row follows the whole-table row it
    narrows, flagged `echo_display_only` (S14E-X128: typed, its echo would open
    the whole table). A pure read over the counsel's roads (display only,
    Golden Rule 6); the AI never reaches it (the wizard is the player's)."""
    alone = next((r for r in (roads or []) if r.get("road") == "table_alone"), None)
    if not alone or not alone.get("available") or alone.get("carries"):
        return actions
    try:
        gold = int(alone.get("gold_to_carry") or 0)
    except (TypeError, ValueError):
        return actions
    if gold <= 0:
        return actions
    tables = [a for a in actions if a.get("action") == "open_settlement" and a.get("available")]
    if not tables:
        return actions
    from backend.display_names import display_nation as _dn
    court = _dn(target)
    funds = _lever_funds(world, player)
    funded = gold <= funds
    note = (f"opens with {gold} gold to {court} staged — the sum that carries her" if funded
            else f"{gold} gold to {court} would carry her; the treasury can fund {funds}")

    def _stamp(row: Dict[str, Any]) -> None:
        row["counsel_coverage"] = [target]
        row["effect_text"] = note
        if funded:
            row["gold_offer"] = gold

    in_place = next((a for a in tables
                     if list(a.get("counsel_coverage") or a.get("addresses") or []) == [target]), None)
    if in_place is not None:
        _stamp(in_place)
        return actions
    whole = tables[0]
    row = {k: v for k, v in whole.items() if k != "counsel_first"}
    row["display_name"] = str(alone.get("label") or f"Open Settlement with {court} alone")
    row["addresses"] = [target]
    row["addresses_display"] = f"with {court} alone"
    # S14E-X128: the court alone out of a larger table - typed, its echo opens
    # the whole table, so the wizard keys it as display copy (funded or not).
    row["echo_display_only"] = True
    _stamp(row)
    out = list(actions)
    out.insert(out.index(whole) + 1, row)
    return out


def lever_offer_opening_terms(world: Any, *, war_id: str, payer: str, court: str,
                              amount: int, covered: List[str],
                              base_terms: Any = None) -> Any:
    """The draft the counsel's lever opens the table with (S14E-D7): the draft
    it would open with anyway — `base_terms`, the draft the player holds for
    the war (a Back Out round trip restores one, and the click still stages
    its payment on it), else `bond.bid_opening_terms`' own (the articles
    declared at the war, else the bare peace) — and the payment, a gold
    indemnity from `payer` to `court` of `amount`, stamped the player's own
    (the click authored it, as the Offer row's press does — the dial sweep
    keeps a line the player authored). The one payer-to-court gold line the
    draft held (a declared article, an earlier offer) yields to it. None where
    the treasury cannot fund it beside the draft's other gold: the table then
    opens as it would have, never on an overdrawn line."""
    amount = int(amount or 0)
    if amount <= 0:
        return None
    if base_terms:
        base = [dict(t) for t in base_terms if isinstance(t, dict)]
    else:
        from backend.game_logic.bond import bid_opening_terms
        base = bid_opening_terms(world, war_id=war_id, payer=payer, court=court,
                                 amount=amount, covered=covered)[:-1]
    kept = [t for t in base
            if not (t.get("type") == "gold_indemnity" and t.get("from") == payer
                    and t.get("to") == court)]
    if amount > _lever_headroom(world, payer, kept):
        return None
    return kept + [{"type": "gold_indemnity", "from": payer, "to": court,
                    "amount": amount, "authored_by": "player"}]

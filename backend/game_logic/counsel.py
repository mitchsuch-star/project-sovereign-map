"""Talleyrand's counsel — a reading, not a lookup (PC-R8, ruling K; the peace
report `docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §46, October 16, 2026;
rules `SYSTEMS_REFERENCE.md` §122).

The old counsel (`diplomacy._base_recommendation_and_mission`) picked the
best *available* `propose_*` row by `likelihood_score` and printed one fixed
sentence — it could name a road whose own button was refused (PC-F35) and
recommended the armistice because the paradox had shut the peace row
(PC-F43). This module replaces the wartime arms with ONE reading of the
live board:

1. **A reading, not a lookup** (`read_counsel`). Every road open on the
   court's page is dry-run by the game's own instruments and ranked: the
   bilateral send (`calculate_acceptance` with its components), the table
   with this court alone and the table whole (`build_settlement_preview`),
   a truce (`armistice_likelihood`), a mission (IQ-4's forecast, at peace)
   and a battle — only where the battle ledger is not full
   (`calculate_war_score(return_components=True)`). The best road's number,
   the one term that would flip the verdict and the trade the road costs
   are in the reading.
2. **Never a road its button refuses.** A road is ranked `available` only
   when its own gate opens it (`treaty.can_sign(at_send=True)`, the table's
   eligibility, the row's own `available`); a shut road is carried as shut
   with the gate's reason and never recommended.
3. **Varied, in his register** (`compose_counsel_line`). Lines are composed
   from authored pools keyed by situation — winning / losing / level, a
   league in being, a truce running, a clock near its end — in the Voice
   Bible's Talleyrand register (urbane, "Sire", arithmetic with manners,
   never enthusiastic, never a battlefield metaphor); every line carries its
   figures. A per-court memory of the last line sent (`world.talleyrand_
   counsel_memory`) forbids a repeat while the situation is unchanged.
4. **His own mind, honestly** (`talleyrand_preference`). The preference is
   derived from the stores his objection reads (the war's sign, the staged
   draft's harshness) and said beside the numbers, which stay the scorer's;
   the override note's running tally says how often he was right.
5. **One builder, every surface.** The wizard's recommendation, the
   feasibility card's verdict and the table's counsel read this one set.

Golden Rule 6: no LLM; every sentence is deterministic text from
deterministic numbers (`compose_counsel_line` is a pure function of the
reading dict and the memory it is handed), byte-for-byte under
`SOVEREIGN_SEED=historical`.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
from typing import Any, Dict, List, Mapping, Optional

from backend.errors import report

# The authored pools (ruling K item 3). Keys: (posture, case). `posture` is
# the war's sign from France's chair — "winning" / "losing" / "level";
# `case` is what the reading found — "carries" (the best road carries),
# "none" (no road carries), "truce" (a truce runs). Every template carries
# at least one figure. Placeholders are filled from the reading's slots
# (`_slots`); a missing slot renders "" and the sentence is trimmed.
COUNSEL_POOLS: Dict[tuple, List[str]] = {
    ("winning", "carries"): [
        "Sire, {best_label} carries today — {best_number} of {threshold}. {trade} {second}",
        "Permit me to observe, Sire, that the arithmetic favours one road: "
        "{best_label}, at {best_number} of {threshold}. {trade} {second}",
        "If I may, Sire — {best_label} would be signed this morning ({best_number} of {threshold}). "
        "{trade} I would not pay for what is already purchased. {second}",
        "One could, of course, wait; one need not. {best_label} reads {best_number} of {threshold} "
        "today, Sire. {trade} {second}",
    ],
    ("winning", "none"): [
        "Sire, no road carries this morning. The nearest is {best_label} at "
        "{best_number} of {threshold}; the weight against it is {flip_label} ({flip_value}). {lever}",
        "Permit me to observe, Sire, that every door is shut by arithmetic, not by "
        "malice: {best_label} reads {best_number} of {threshold}. "
        "{flip_label} is the term ({flip_value}). {lever}",
        "If I may, Sire — the court is beaten and not yet buyable. {best_label} "
        "stands at {best_number} of {threshold}; it wants {flip_label} "
        "({flip_value}). {lever}",
    ],
    ("losing", "carries"): [
        "Sire, we are not in a position to be choosy. {best_label} carries at "
        "{best_number} of {threshold}; {trade} I would take it before the price rises.",
        "Permit me to observe, Sire, that {best_label} would be accepted today "
        "({best_number} of {threshold}). {trade} A court that is winning does not stay generous.",
        "If I may, Sire — the ledger is against us, and {best_label} is the door "
        "still open: {best_number} of {threshold}. {trade}",
    ],
    ("losing", "none"): [
        "Sire, no road carries while the field reads {score}. {best_label} comes "
        "nearest at {best_number} of {threshold}; {flip_label} is what they want ({flip_value}). {lever}",
        "Permit me to observe, Sire, that they are not yet tired enough to talk: "
        "{best_label} reads {best_number} of {threshold}; it wants {flip_label} "
        "({flip_value}). {lever}",
        "If I may, Sire — a peace is bought with something, and we hold little: "
        "{best_label} at {best_number} of {threshold}, wanting {flip_label} ({flip_value}). {lever}",
    ],
    ("level", "carries"): [
        "Sire, the war is level and {best_label} carries regardless — {best_number} of {threshold}. "
        "{trade} {second}",
        "Permit me to observe, Sire, that neither side has bought the other, and yet "
        "{best_label} reads {best_number} of {threshold}. {trade} {second}",
        "If I may, Sire — a level ledger still signs: {best_label} at {best_number} of {threshold}. "
        "{trade} {second}",
    ],
    ("level", "none"): [
        "Sire, the field reads {score} and no road carries. {best_label} comes "
        "nearest at {best_number} of {threshold}; {flip_label} is the weight ({flip_value}). {lever}",
        "Permit me to observe, Sire, that a level war is the dearest kind to end: "
        "{best_label} reads {best_number} of {threshold}; it wants {flip_label} "
        "({flip_value}). {lever}",
        "If I may, Sire — the court sees no reason to sign at {score}: {best_label} "
        "stands at {best_number} of {threshold}; it wants {flip_label} ({flip_value}). {lever}",
    ],
    # PC-R2 / PC-F44 (S13e part 2): a truce KEEPS the ledger (ruling D) — the
    # lines say what it keeps ({keeps}), where it heads ({heading}: the
    # dictated peace, the courted peace, the collapse) and the cure priced
    # where it is in reach ({cure}), from the one wording (`truce_words`).
    ("winning", "truce"): [
        "Sire, the truce with {court} has {clock_turns} to run and {keeps} {heading} "
        "{cure} {best_label} reads {best_number} of {threshold}. {trade}",
        "Permit me to observe, Sire, that a truce is a clock, not a treaty: {clock} "
        "turns, relations {relation}, and {keeps} {heading} {cure} {best_label} reads "
        "{best_number} of {threshold}. {trade}",
        "If I may, Sire — {clock_turns} of quiet remain with {court}; {keeps} {heading} "
        "{cure} {best_label} reads {best_number} of {threshold}. {trade}",
    ],
    ("losing", "truce"): [
        "Sire, the truce with {court} buys us {clock_turns}, and {keeps} {heading} "
        "{cure} {best_label} reads {best_number} of {threshold}. {trade}",
        "Permit me to observe, Sire, that {clock_turns} is what we have bought with "
        "{court}; {keeps} {heading} {cure} {best_label} reads {best_number} of "
        "{threshold}. {trade}",
        "If I may, Sire — the clock with {court} reads {clock}; {keeps} {heading} {cure} "
        "{best_label} reads {best_number} of {threshold}. {trade}",
    ],
    ("level", "truce"): [
        "Sire, the truce with {court} has {clock_turns} to run; {keeps} {heading} {cure} "
        "{best_label} reads {best_number} of {threshold}. {trade}",
        "Permit me to observe, Sire, that {clock_turns} of truce remain with {court}, "
        "relations {relation}; {keeps} {heading} {cure} {best_label} reads "
        "{best_number} of {threshold}. {trade}",
        "If I may, Sire — a level war in truce: {clock_turns}, relations {relation}; "
        "{keeps} {heading} {cure} {best_label} reads {best_number} of {threshold}. {trade}",
    ],
}

# Ruling K item 4 — his own mind. Keyed by the preference the stores yield.
PREFERENCE_POOLS: Dict[str, List[str]] = {
    "moderate": [
        "For my part, Sire, I would take the white peace and not the province: a "
        "court stripped today sends its Revanche in four years.",
        "If you ask my own mind, Sire: the plain peace. A province taken from a "
        "beaten court is a war bought back at interest.",
    ],
    "firm": [
        "For my part, Sire, I would sign before the price rises; a losing hand does "
        "not improve by being held.",
        "If you ask my own mind, Sire: take what is offered. The court will not stay "
        "this generous.",
    ],
}

ROAD_LABELS = {
    "send_peace": "Propose Peace",
    "table_alone": "Open Settlement with {court} alone",
    "table_whole": "the whole table",
    "truce": "Propose Armistice",
    "mission": "Improve Relations",
    "battle": "a battle",
}

ROAD_ACTIONS = {
    "send_peace": "propose_peace",
    "truce": "propose_armistice",
    "table_alone": "open_settlement",
    "table_whole": "open_settlement",
    "mission": "mission_improve_relations",
    "battle": "",
}


# ═══════════════════════════════════════════════════════════════════════════
# The reading
# ═══════════════════════════════════════════════════════════════════════════

def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _flip_from_components(components: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """The largest negative component of a bilateral acceptance — the one
    term that would flip the verdict — labelled in the formula's own
    feedback words (`display_names.FEEDBACK_STRINGS`)."""
    from backend.display_names import FEEDBACK_STRINGS
    worst_key, worst_val = "", 0
    for key, val in (components or {}).items():
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            continue
        if key in ("composite_floor", "composite_floor_adjustment",
                   "grievance_flag_count_raw", "oathbreaker_turns_remaining",
                   "anti_renewal_turns_remaining"):
            continue
        if val < worst_val:
            worst_key, worst_val = key, val
    if not worst_key:
        return None
    label = (FEEDBACK_STRINGS.get(worst_key) or {}).get("negative") or worst_key.replace("_", " ")
    return {"component": worst_key, "value": int(round(worst_val)), "label": str(label)}


def _bilateral_road(world, player: str, court: str, ptype: str, road: str,
                    priced_terms: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """A bilateral dry run — the suggested terms of `ptype` scored by
    `calculate_acceptance`, gated by `treaty.can_sign(at_send=True)`.

    K item 6: `priced_terms` is the ONE draft the wizard open memoised
    (`get_diplomatic_preview`'s `_suggested_terms_for`) — the same terms
    the snapshot scores and the confirm pre-fills, so the figure the
    counsel quotes is the figure the send is judged on. Without it (a
    reading outside the wizard) the deterministic draft is priced."""
    from backend.game_logic.diplomacy import (
        ACCEPT_SCORE, armistice_variant_for, calculate_acceptance,
        diplomatic_price_quote, separate_peace_words,
    )
    from backend.game_logic.diplomatic_templates import generate_suggested_terms
    from backend.game_logic.treaty import can_sign
    variant = armistice_variant_for(world, player, court) if ptype == "armistice" else ptype
    draft = (dict(priced_terms) if priced_terms
             else _quiet(generate_suggested_terms, court, ptype, world, deterministic=True))
    proposal = {
        "type": variant, "proposer_nation": player, "target_nation": court,
        "sweeteners": list(draft.get("sweeteners") or []),
        "demands": list(draft.get("demands") or []),
        "clauses": list(draft.get("clauses") or []),
    }
    acceptance = _quiet(calculate_acceptance, proposal, world)
    score = int(acceptance.get("score", 0))
    verdict = can_sign(world, proposal, at_send=True)
    quote = diplomatic_price_quote(world, "armistice" if ptype == "armistice" else "peace", court)
    have = int(getattr(world, "diplomatic_points", 0) or 0)
    available = bool(verdict.ok) and have >= int(quote["cost"])
    shut = "" if verdict.ok else str(verdict.message or verdict.clause or "")
    if verdict.ok and have < int(quote["cost"]):
        shut = f"It costs {int(quote['cost'])} DP; you have {have}."
    out: Dict[str, Any] = {
        "road": road, "action": ROAD_ACTIONS[road],
        "label": ROAD_LABELS[road].format(court=_shown(world, court)),
        "available": available, "shut_reason": shut,
        "carries": score >= ACCEPT_SCORE, "score": score, "threshold": int(ACCEPT_SCORE),
        "number": f"{score}",
        "flip": _flip_from_components(acceptance.get("components") or {}),
        "price_dp": int(quote["cost"]), "have_dp": have,
        "outcome": str(acceptance.get("outcome") or ""),
    }
    if ptype == "peace":
        words = separate_peace_words(world, player, court)
        trade = f"It costs {int(quote['cost'])} DP."
        if words:
            trade = f"{trade} {words['display']}"
        # PC-F40: the plain peace (no demands) scored beside the drafted
        # one, so the counsel can say "a peace without demands would be
        # accepted (75)" where the draft's own demand is the obstacle.
        plain = dict(proposal, sweeteners=[], demands=[], clauses=[])
        plain_score = int(_quiet(calculate_acceptance, plain, world).get("score", 0))
        out["plain_score"] = plain_score
        out["drafted"] = bool(proposal["demands"] or proposal["sweeteners"] or proposal["clauses"])
        if out["drafted"] and plain_score != score:
            verdict_word = "accepted" if plain_score >= ACCEPT_SCORE else "refused"
            out["plain_sentence"] = (
                f"A peace without demands would be {verdict_word} ({plain_score}).")
            if plain_score >= ACCEPT_SCORE and score < ACCEPT_SCORE:
                out["carries_plain"] = True
        out["trade"] = trade
        out["separate_peace"] = words
    else:
        # PC-R2 / PC-F44: a truce KEEPS the ledger (ruling D) — the trade
        # is time, not the score; the one wording (`truce_words`) says what
        # it keeps, where it heads and what the cure costs.
        from backend.game_logic.diplomacy import truce_words
        words = truce_words(world, player, court)
        heading = {
            "dictated": "it would end in a dictated peace on the held line",
            "peace": "it would ripen into peace on the held line",
            "war": "the war would resume where it stood",
        }.get(str(words.get("exit") or "war"), "the war would resume where it stood")
        cure = f" {words['cure_line']}" if words.get("cure_line") else ""
        out["trade"] = (f"It costs {int(quote['cost'])} DP. A truce keeps the ledger "
                        f"({words['keeps']['war_score']:+d} stands, the war "
                        f"{int(words['keeps']['war_age'])} turns old) and titles nothing "
                        f"until it ends; {heading}.{cure}")
        out["truce_words"] = words
    return out


def _table_road(world, player: str, court: str, *, alone: bool,
                staged_terms: Optional[List[Mapping[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """The settlement table dry run — this court alone, or the table whole —
    through `build_settlement_preview` (the very table Open Settlement
    shows). None when the court sits on no settleable war instance."""
    from backend.game_logic.diplomacy import diplomatic_price_quote
    from backend.game_logic.settlement_helpers import (
        _find_active_war_instance_for_pair, _make_pair_key,
    )
    war_id = _find_active_war_instance_for_pair(world, _make_pair_key(player, court))
    if not war_id:
        return None
    from backend.game_logic.settlement_staging import build_settlement_preview
    try:
        # K item 6: the table road is priced on the terms it will OPEN with —
        # the staged draft, or the white peace (no terms) — never on a
        # baseline the player has not seen; the open road applies these.
        # PC-R7 (ii) part 2: with nothing staged, the road prices the
        # articles declared at the war FIRST (`declared_when_empty`) — the
        # draft the editor opens with; the white peace where none were.
        preview = _quiet(
            build_settlement_preview, world, war_id=war_id,
            settlement_terms=list(staged_terms or []), actor_nation=player,
            ignore_active_dialogue=True, declared_when_empty=True,
            covered_enemy_participants=([court] if alone else None))
    except Exception as exc:
        report(exc, "counsel._table_road: build_settlement_preview")
        return None
    road = "table_alone" if alone else "table_whole"
    # K item 6: a table priced with no terms is the WHITE PEACE road
    # (`propose_white_peace`, the only road that ratifies an empty package);
    # with a staged draft — or the declared articles — it is the editor.
    _body0 = (preview.get("settlement_preview") or {}) if preview.get("success") else {}
    declared = bool(_body0.get("declared_draft"))
    action = ROAD_ACTIONS[road] if (staged_terms or declared) else "propose_white_peace"
    out: Dict[str, Any] = {
        "road": road, "action": action, "war_id": str(war_id),
        "label": ROAD_LABELS[road].format(court=_shown(world, court)),
        "declared_draft": declared,
    }
    if not preview.get("success"):
        out.update({
            "available": False,
            "shut_reason": str(preview.get("disabled_reason_display")
                               or preview.get("reason") or "The table is not open."),
            "carries": False, "score": None, "threshold": 50, "number": "", "flip": None,
            "trade": "", "price_dp": 0,
        })
        return out
    body = preview.get("settlement_preview") or {}
    rows = [r for r in (body.get("per_court_acceptance") or []) if isinstance(r, Mapping)]
    covered = [str(n) for n in (body.get("covered_enemy_participants") or [])]
    out["priced_terms"] = [dict(t) for t in (body.get("settlement_terms") or []) if isinstance(t, Mapping)]
    out["baseline_generated"] = bool(body.get("baseline_generated"))
    # PC-R1 (v) item 5: the two Pressburgs — the counsel says which draft
    # this is ("Revanche stands" / "Revanche lapses"), from the one seam.
    out["revanche_line"] = str(body.get("revanche_line") or "")
    if alone and covered != [court]:
        # the court is not alone on this table (it is the only coverable
        # court, or the preview widened the set): the whole-table road says it
        return None if covered else out
    carries = bool((body.get("overall_acceptance") or {}).get("carries"))
    mine = next((r for r in rows if str(r.get("nation")) == court), None)
    lowest = min((r for r in rows if r.get("total") is not None),
                 key=lambda r: int(r["total"]), default=None)
    quote = diplomatic_price_quote(world, "peace", court)
    have = int(getattr(world, "diplomatic_points", 0) or 0)
    totals = {str(r.get("nation")): r.get("total") for r in rows}
    mean = int((body.get("acceptance") or {}).get("total") or 0)
    out.update({
        "available": have >= int(quote["cost"]),
        "shut_reason": ("" if have >= int(quote["cost"])
                        else f"It costs {int(quote['cost'])} DP; you have {have}."),
        "carries": carries,
        "score": (int(mine["total"]) if (mine and mine.get("total") is not None)
                  else (int(lowest["total"]) if lowest else None)),
        "threshold": int((mine or lowest or {}).get("threshold") or 50),
        "per_court": totals, "mean": mean, "covered": covered,
        "price_dp": int(quote["cost"]), "have_dp": have,
    })
    out["number"] = (f"{out['score']}" if out["score"] is not None else "")
    holdout = lowest if (lowest and not carries) else None
    out["flip"] = ({"component": str(holdout.get("top_blocker_component") or ""),
                    "value": int(holdout.get("total") or 0) - int(holdout.get("threshold") or 50),
                    "label": (f"{_shown(world, str(holdout.get('nation')))}'s consent "
                              f"({str(holdout.get('top_blocker_display') or 'her court').lower()})")}
                   if holdout else None)
    # the draft this road priced: the staged one, or the declared articles
    _priced = list(staged_terms or []) or (list(out["priced_terms"]) if declared else [])
    if alone:
        from backend.game_logic.diplomacy import separate_peace_words
        words = separate_peace_words(world, player, court, _priced)
        trade = f"It costs {int(quote['cost'])} DP."
        if declared:
            trade = f"{trade} {_declared_words(world, war_id, player, _priced)}"
        if words:
            trade = f"{trade} {words['display']}"
        out["trade"] = trade
        out["separate_peace"] = words
        # Ruling K item 1's lever: the payment that would carry this court
        # alone, by the scorer's own credit (CONCESSION_GOLD_DIVISOR a point,
        # capped at CONCESSION_GOLD_CAP) — or none.
        out["gold_to_carry"] = _gold_to_carry(world, war_id, player, court, mine, _priced)
        # PC-F61 (S13e part 3): what the table CARRIES from a beaten court at
        # its score — the tier's name promises only what the scorer carries.
        out["carry_ladder"] = _carry_ladder(world, war_id, player, court, mine)
        out["carry_line"] = _carry_line(world, court, out["carry_ladder"])
        if out["carry_line"]:
            out["trade"] = f"{out['trade']} {out['carry_line']}"
        # PC-F60: the four rates for gold against land, named.
        from backend.game_logic.settlement_scoring import gold_land_rate_note
        out["rates_note"] = gold_land_rate_note()
    else:
        parts = " · ".join(f"{_shown(world, n)} {t if t is not None else 'no score'}"
                           for n, t in totals.items())
        out["trade"] = (f"Every covered court must reach {out['threshold']}; the table "
                        f"reads their mean ({mean}) — {parts}.")
        if declared:
            out["trade"] = f"{_declared_words(world, war_id, player, _priced)} {out['trade']}"
    return out


def _declared_words(world, war_id: str, player: str, terms) -> str:
    """PC-R7 (ii) part 2: the road says it was priced on the declared articles."""
    from backend.game_logic.declared_goals import declared_in_package
    inst = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    side = (inst.get("side_by_nation") or {}).get(player)
    names = declared_in_package(world, terms, list(inst.get(side) or [player]) if side else [player])
    return (f"Priced on the articles declared at the war: {', '.join(names)}." if names
            else "Priced on the articles declared at the war.")


def _carry_ladder(world, war_id: str, player: str, court: str, row) -> List[Dict[str, Any]]:
    """PC-F61 (S13e part 3, October 16, 2026): three packages dry-run on the
    court ALONE by the per-court scorer — a province, two provinces, a
    province and 300 gold — each with its total and whether it carries, so
    the counsel can say what the court's score actually buys. Measured at a
    forced +80 on the Vienna-held board: a province carries (63), two do not
    (49), where "Total Victory" promised more. Only for a court France is
    BEATING (its pair from our chair positive) with a home province in our
    side's hands; [] otherwise."""
    if not row or row.get("total") is None:
        return []
    from backend.game_logic.diplomacy import get_war_score_for
    if int(get_war_score_for(world, player, court)) <= 0:
        return []
    war = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    side_by_nation = war.get("side_by_nation") or {}
    ours = {n for n, s in side_by_nation.items() if s == side_by_nation.get(player)}
    capital = world.get_nation_capital(court)
    held = []
    for name in (getattr(world, "nation_starting_regions", {}) or {}).get(court, []) or []:
        if name == capital:
            continue
        region = world.regions.get(name)
        if region is not None and getattr(region, "controller", None) in ours:
            held.append((int(getattr(region, "income_value", 0) or 0), str(name)))
    held.sort(reverse=True)
    provinces = [n for _, n in held[:2]]
    if not provinces:
        return []
    packages = [("a province", [{"type": "territory_cede", "from": court, "to": player,
                                 "region": provinces[0]}], provinces[:1])]
    if len(provinces) > 1:
        packages.append(("two provinces", [{"type": "territory_cede", "from": court, "to": player,
                                            "region": p} for p in provinces], provinces[:2]))
    packages.append(("a province and 300 gold",
                     [{"type": "territory_cede", "from": court, "to": player, "region": provinces[0]},
                      {"type": "gold_indemnity", "from": court, "to": player, "amount": 300}],
                     provinces[:1]))
    out: List[Dict[str, Any]] = []
    from backend.game_logic.settlement_staging import build_settlement_preview
    for label, terms, named in packages:
        try:
            preview = _quiet(build_settlement_preview, world, war_id=war_id,
                             settlement_terms=terms, actor_nation=player,
                             ignore_active_dialogue=True, covered_enemy_participants=[court])
        except Exception as exc:
            report(exc, "counsel._carry_ladder: build_settlement_preview")
            continue
        body = preview.get("settlement_preview") or {}
        rows = body.get("per_court_acceptance") or []
        mine = next((r for r in rows if str(r.get("nation")) == court), None)
        if mine is None or mine.get("total") is None:
            continue
        out.append({"label": label, "regions": list(named), "total": int(mine["total"]),
                    "threshold": int(mine.get("threshold") or 50),
                    "carries": bool((body.get("overall_acceptance") or {}).get("carries"))})
    return out


def _carry_line(world, court: str, ladder: List[Dict[str, Any]]) -> str:
    """PC-F61: "At her score the table carries from Austria a province (Tyrol,
    63 of 50); not two provinces (49)." — "" with no ladder."""
    if not ladder:
        return ""
    name = _shown(world, court)
    carries = [r for r in ladder if r["carries"]]
    refuses = [r for r in ladder if not r["carries"]]
    parts = []
    if carries:
        best = max(carries, key=lambda r: (len(r["regions"]), r["total"]))
        parts.append(f"At her score the table carries from {name} {best['label']} "
                     f"({', '.join(best['regions'])}, {best['total']} of {best['threshold']})")
    else:
        worst = min(ladder, key=lambda r: len(r["regions"]))
        parts.append(f"At her score the table carries no province from {name} "
                     f"({worst['label']} reads {worst['total']} of {worst['threshold']})")
    if refuses and carries:
        r = min(refuses, key=lambda r: r["total"])
        parts.append(f"not {r['label']} ({r['total']})")
    return "; ".join(parts) + "."


def _gold_to_carry(world, war_id: str, player: str, court: str, row, staged_terms) -> Optional[int]:
    """The smallest gold indemnity to `court` that carries the court alone,
    by the scorer's credit arithmetic — verified by one preview; None when
    no payment can (the credit is capped)."""
    if not row or row.get("total") is None:
        return None
    from backend.game_logic.settlement_scoring import (
        CONCESSION_GOLD_CAP, CONCESSION_GOLD_DIVISOR,
    )
    need = int(row.get("threshold") or 50) - int(row["total"])
    if need <= 0:
        return 0
    if need > CONCESSION_GOLD_CAP:
        return None
    amount = need * CONCESSION_GOLD_DIVISOR
    terms = [dict(t) for t in (staged_terms or []) if isinstance(t, Mapping)]
    terms = [t for t in terms if not (t.get("type") == "gold_indemnity"
                                      and t.get("from") == player and t.get("to") == court)]
    terms.append({"type": "gold_indemnity", "from": player, "to": court, "amount": int(amount)})
    try:
        from backend.game_logic.settlement_staging import build_settlement_preview
        preview = _quiet(build_settlement_preview, world, war_id=war_id,
                         settlement_terms=terms, actor_nation=player,
                         ignore_active_dialogue=True, covered_enemy_participants=[court])
    except Exception as exc:
        report(exc, "counsel._gold_to_carry: build_settlement_preview")
        return None
    body = preview.get("settlement_preview") or {}
    return int(amount) if (body.get("overall_acceptance") or {}).get("carries") else None


def _battle_road(world, player: str, court: str) -> Dict[str, Any]:
    """The battle — only a road while the battle ledger is not full."""
    from backend.game_logic.diplomacy import (
        BATTLE_SCORE_CAP, BATTLE_SCORE_PER_WIN, DECISIVE_SCORE_CAP, calculate_war_score,
    )
    comps = calculate_war_score(player, court, world, return_components=True)
    battles = int(comps.get("battles", 0))
    decisive = int(comps.get("decisive", 0))
    room = max(0, int(BATTLE_SCORE_CAP) - battles)
    full = room <= 0
    capital = _their_capital(world, court)
    out = {
        "road": "battle", "action": "", "label": ROAD_LABELS["battle"],
        "available": not full, "carries": False, "score": None, "threshold": 0,
        "number": f"{battles} of {BATTLE_SCORE_CAP}", "flip": None, "price_dp": 0,
        "battles": battles, "battle_cap": int(BATTLE_SCORE_CAP),
        "decisive": decisive, "decisive_cap": int(DECISIVE_SCORE_CAP),
        "per_win": int(BATTLE_SCORE_PER_WIN),
    }
    if full:
        out["shut_reason"] = (f"the battle score is full ({battles}/{BATTLE_SCORE_CAP}); "
                              f"only {capital or 'their capital'} or time moves this court")
        out["trade"] = out["shut_reason"]
    else:
        out["shut_reason"] = ""
        out["trade"] = (f"the battle ledger has room ({battles}/{BATTLE_SCORE_CAP}): "
                        f"a victory adds up to {BATTLE_SCORE_PER_WIN}")
    return out


def _their_capital(world, court: str) -> str:
    caps = getattr(world, "nation_capitals", None) or {}
    cap = caps.get(court)
    if isinstance(cap, dict):
        cap = cap.get("name") or cap.get("region")
    return str(cap or "")


def _shown(world, nation: str) -> str:
    from backend.game_logic.formations import formed_display_name
    return formed_display_name(world, nation)


def _posture(score_from_player: int) -> str:
    if score_from_player > 20:
        return "winning"
    if score_from_player < -20:
        return "losing"
    return "level"


def talleyrand_preference(world, court: str, reading_posture: str,
                          own_score: int, staged_terms=None) -> Dict[str, Any]:
    """Ruling K item 4: what Talleyrand himself would do, derived from the
    stores his pre-proposal objection reads (`diplomatic_defiance.
    evaluate_pre_proposal_objection`: the harshness of what is drafted, the
    war's sign) — never chance. 'moderate' when France is winning over a
    beaten court and a harsh draft is on the table or none yet (a province
    buys the Revanche, `emergent_designs`); 'firm' when France is losing;
    'none' otherwise. Display only (GR6)."""
    from backend.game_logic.diplomatic_templates import burden_on_nation
    terms = [t for t in (staged_terms or []) if isinstance(t, Mapping)]
    harshness = float(burden_on_nation(terms, court) or 0.0) if terms else 0.0
    kind = "none"
    why = ""
    if reading_posture == "winning" and own_score <= -50:
        kind = "moderate"
        why = ("a beaten great power stripped of a province swears its Revanche"
               if harshness > 0.7 else "the plain peace holds; the province would not")
    elif reading_posture == "losing":
        kind = "firm"
        why = "the court will not stay this generous"
    return {"kind": kind, "why": why, "harshness": round(harshness, 2)}


def override_tally(world) -> Dict[str, int]:
    """The running count of the Emperor's overrides judged right and wrong
    (`talleyrand_override_tally`, kept across the campaign — the history
    keeps only the last five)."""
    tally = getattr(world, "talleyrand_override_tally", None) or {}
    return {"good": int(tally.get("good", 0) or 0), "bad": int(tally.get("bad", 0) or 0)}


def read_counsel(world, court: str, *, staged_terms=None,
                 priced_terms: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Dict[str, Any]:
    """The reading of the live board for `court` — the ranked roads, the
    best one, the situation, his preference and the tally. A pure read.
    `priced_terms` ({"peace": terms, "armistice": terms}) is the wizard
    open's memo (K item 6) — the bilateral roads price those drafts."""
    from backend.game_logic.ai_diplomacy import court_own_readiness
    from backend.game_logic.diplomacy import (
        ARMISTICE_AUTO_PEACE_RELATION, live_war_score_for,
    )
    player = str(getattr(world, "player_nation", "France") or "France")
    state = world.get_diplomatic_state(player, court)
    key = world._make_diplo_key(player, court)
    score = int(live_war_score_for(world, player, court)) if state in ("WAR", "ARMISTICE") else 0
    posture = _posture(score)
    own = court_own_readiness(world, court, player)
    diplomat = (getattr(world, "diplomats", {}) or {}).get(court)
    statecraft = str(getattr(diplomat, "personality", "") or "")
    truce = state == "ARMISTICE"
    # the truce's clock is the turns REMAINING (the store counts elapsed)
    from backend.game_logic.diplomacy import ARMISTICE_DURATION as _DUR
    clock = (max(0, int(_DUR) - int((getattr(world, "armistice_turns", {}) or {}).get(key, 0) or 0))
             if truce else None)
    relation = int((getattr(world, "nation_relations", {}) or {}).get(key, 0) or 0)

    roads: List[Dict[str, Any]] = []
    priced = dict(priced_terms or {})
    if state in ("WAR", "ARMISTICE"):
        roads.append(_bilateral_road(world, player, court, "peace", "send_peace",
                                     priced_terms=priced.get("peace")))
        alone = _table_road(world, player, court, alone=True, staged_terms=staged_terms)
        whole = _table_road(world, player, court, alone=False, staged_terms=staged_terms)
        if alone:
            roads.append(alone)
        if whole and (not alone or whole.get("covered") != alone.get("covered")):
            roads.append(whole)
        if state == "WAR":
            roads.append(_bilateral_road(world, player, court, "armistice", "truce",
                                         priced_terms=priced.get("armistice")))
            roads.append(_battle_road(world, player, court))

    _KIND = {"send_peace": 0, "table_alone": 0, "table_whole": 0, "truce": 1,
             "mission": 2, "battle": 3}

    def _rank(r: Dict[str, Any]):
        # roads that carry AND are open first — a PEACE before a truce (a
        # truce strikes the ledger: the dearer trade), the higher number,
        # then the cheaper DP; then the open roads by number; shut roads last.
        open_ = bool(r.get("available"))
        carries = bool(r.get("carries"))
        sc = r.get("score")
        sc = int(sc) if sc is not None else -999
        return (not (open_ and carries), not open_, _KIND.get(str(r.get("road")), 9),
                -sc, int(r.get("price_dp", 0) or 0))

    ranked = sorted(roads, key=_rank)
    best = next((r for r in ranked if r.get("available") and r.get("carries")), None)
    nearest = next((r for r in ranked if r.get("available") and r.get("score") is not None), None)
    carrying = [r["road"] for r in ranked if r.get("available") and r.get("carries")]
    case = "truce" if truce else ("carries" if best else "none")
    reading = {
        "court": court, "court_display": _shown(world, court), "player": player,
        "state": state, "turn": int(getattr(world, "current_turn", 0) or 0),
        "score": int(score), "posture": posture, "case": case,
        "league": bool(own.get("in_league")), "truce": truce, "clock": clock,
        "thaw": int(ARMISTICE_AUTO_PEACE_RELATION), "relation": relation,
        # PC-R2 / PC-F44: the one wording of a running truce
        **(_truce_reading(world, player, court) if truce else {}),
        "statecraft": statecraft, "own": own,
        "roads": ranked, "best": best, "nearest": nearest, "carrying": carrying,
        "preference": talleyrand_preference(world, court, posture, int(own.get("score", 0)),
                                            staged_terms),
        "tally": override_tally(world),
        "dp": int(getattr(world, "diplomatic_points", 0) or 0),
    }
    return reading


# ═══════════════════════════════════════════════════════════════════════════
# The line — a pure function of the reading
# ═══════════════════════════════════════════════════════════════════════════

class _Slots(dict):
    def __missing__(self, key):
        return ""


def situation_key(reading: Mapping[str, Any]) -> str:
    best = reading.get("best") or reading.get("nearest") or {}
    return "|".join(str(x) for x in (
        reading.get("posture"), reading.get("case"), reading.get("league"),
        reading.get("truce"), reading.get("statecraft"), best.get("road"),
        (reading.get("preference") or {}).get("kind"),
    ))


def _truce_reading(world, player: str, court: str) -> Dict[str, Any]:
    """The running truce's words for the reading: `truce_keeps` ("the ledger
    stands: …" in the counsel's lowercase), `truce_heading` (where it heads)
    and `truce_cure` (the cure priced, or '')."""
    from backend.game_logic.diplomacy import truce_words
    words = truce_words(world, player, court)
    keeps = str(words.get("keeps_line") or "")
    keeps = (keeps[0].lower() + keeps[1:]) if keeps else ""
    heading = {
        "dictated": (f"It heads for a dictated peace on the held line — "
                     f"{words.get('loser') and _shown(world, words['loser'])} reads "
                     f"{int(words.get('keeps', {}).get('war_score', 0)) * -1:+d} with her hope dead."),
        "peace": (f"It ripens into peace on the held line: relations stand at "
                  f"{int(words.get('relation', 0)):+d} and will thaw to {int(words.get('projected', 0)):+d}."),
        "war": (f"It heads for the collapse: relations stand at {int(words.get('relation', 0)):+d} and "
                f"will thaw to {int(words.get('projected', 0)):+d}, short of the line; the war resumes "
                f"where it stood."),
    }.get(str(words.get("exit") or "war"), "")
    return {"truce_keeps": keeps, "truce_heading": heading,
            "truce_cure": str(words.get("cure_line") or ""), "truce_exit": str(words.get("exit") or "")}


def _second_sentence(reading: Mapping[str, Any]) -> str:
    """The second road worth a word: the whole table's mean where the
    court alone carries, the alone table where the send carries, or the
    truce's cost where it is the only other open road."""
    best = reading.get("best") or {}
    roads = reading.get("roads") or []
    by = {r.get("road"): r for r in roads}
    if best.get("road") == "table_alone" and by.get("table_whole"):
        w = by["table_whole"]
        if w.get("per_court"):
            parts = " · ".join(f"{n} {t if t is not None else 'no score'}"
                               for n, t in w["per_court"].items())
            return (f"The whole table reads their mean ({w.get('mean', 0)}) and asks "
                    f"each court for {w.get('threshold', 50)}: {parts}.")
    if best.get("road") == "send_peace" and by.get("table_alone"):
        a = by["table_alone"]
        if a.get("score") is not None:
            return (f"The table with {reading.get('court_display')} alone reads "
                    f"{a['number']}{' and carries too' if a.get('carries') else ''}.")
    battle = by.get("battle")
    if battle and battle.get("trade"):
        return f"As for the field, {battle['trade']}."
    return ""


def _lever_sentence(reading: Mapping[str, Any]) -> str:
    """What would carry: a payment the scorer credits, the court alone, or
    the field — from the roads' own dry-runs."""
    roads = reading.get("roads") or []
    by = {r.get("road"): r for r in roads}
    alone = by.get("table_alone")
    if alone and alone.get("available"):
        gold = alone.get("gold_to_carry")
        if gold:
            return (f"A payment of {int(gold)} gold to {reading.get('court_display')} "
                    f"would carry the table with her alone.")
        if alone.get("carries"):
            return f"The table with {reading.get('court_display')} alone carries ({alone['number']})."
    battle = by.get("battle")
    if battle:
        if battle.get("available"):
            return f"On the field, {battle['trade']}."
        return f"On the field, {battle['shut_reason']}."
    truce = by.get("truce")
    if truce and truce.get("available") and truce.get("carries"):
        return f"A truce would be accepted ({truce['number']}); {truce['trade']}"
    return ""


def _slots(reading: Mapping[str, Any]) -> _Slots:
    best = reading.get("best") or reading.get("nearest") or {}
    flip = best.get("flip") or {}
    s = _Slots(
        court=reading.get("court_display", ""),
        score=f"{int(reading.get('score', 0)):+d}",
        best_label=best.get("label", ""),
        best_number=best.get("number", ""),
        threshold=str(best.get("threshold", 50)),
        trade=best.get("trade", ""),
        flip_label=flip.get("label", "the court's consent"),
        flip_value=f"{int(flip.get('value', 0)):+d}" if flip else "",
        clock=str(reading.get("clock") if reading.get("clock") is not None else ""),
        # PC-X12: "1 turn", "4 turns" — the pools say {clock_turns}
        clock_turns=(f"{int(reading['clock'])} turn{'' if int(reading['clock']) == 1 else 's'}"
                     if reading.get("clock") is not None else ""),
        thaw=str(reading.get("thaw", -60)),
        relation=f"{int(reading.get('relation', 0)):+d}",
        second=_second_sentence(reading),
        lever=_lever_sentence(reading),
        keeps=str(reading.get("truce_keeps", "")),
        heading=str(reading.get("truce_heading", "")),
        cure=str(reading.get("truce_cure", "")),
    )
    return s


def _tidy(text: str) -> str:
    out = " ".join(text.split()).replace(" .", ".").replace(" ,", ",").strip()
    # a label that opens a sentence ("the whole table", "a battle") takes
    # its capital
    chars = list(out)
    for i in range(2, len(chars)):
        if chars[i - 2] in ".!?" and chars[i - 1] == " " and chars[i].islower():
            chars[i] = chars[i].upper()
    return "".join(chars)


def compose_counsel_line(reading: Mapping[str, Any], last: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """The line, a pure function of the reading and the court's memory
    (`last`: {"situation", "index", "line"} or None). Returns {"line",
    "situation", "index", "preference_line"}. The pool is picked by
    situation; the template by a stable hash of the situation and the
    reading's figures plus the turn, rotated past the remembered line while
    the situation is unchanged (ruling K item 3)."""
    posture = str(reading.get("posture") or "level")
    case = str(reading.get("case") or "none")
    pool = COUNSEL_POOLS.get((posture, case)) or COUNSEL_POOLS[("level", "none")]
    sit = situation_key(reading)
    best = reading.get("best") or reading.get("nearest") or {}
    figures = f"{reading.get('score')}|{best.get('score')}|{reading.get('turn')}"
    digest = hashlib.md5(f"{sit}|{figures}".encode("utf-8")).hexdigest()
    index = (int(digest, 16) + int(reading.get("turn") or 0)) % len(pool)
    if last and str(last.get("situation")) == sit and int(last.get("index", -1)) == index:
        index = (index + 1) % len(pool)
    line = _tidy(pool[index].format_map(_slots(reading)))
    if not best:
        line = _tidy(f"Sire, there is no road to read with {reading.get('court_display')} "
                     f"at {int(reading.get('score', 0)):+d}; the page offers nothing to dry-run.")
    pref = reading.get("preference") or {}
    pref_pool = PREFERENCE_POOLS.get(str(pref.get("kind") or ""))
    pref_line = ""
    if pref_pool:
        pi = (int(digest[-4:], 16) + int(reading.get("turn") or 0)) % len(pref_pool)
        pref_line = pref_pool[pi]
        tally = reading.get("tally") or {}
        good, bad = int(tally.get("good", 0)), int(tally.get("bad", 0))
        if good or bad:
            # "good" = the Emperor was right to overrule him, "bad" = he was
            # right — the dispatch note's own reading (`override_tally_sentence`).
            pref_line += (f" (Overruled, I have been right {_times(bad)} and wrong "
                          f"{_times(good)} this campaign.)")
    return {"line": line, "situation": sit, "index": index, "preference_line": pref_line}


def _times(n: int) -> str:
    return {0: "never", 1: "once", 2: "twice"}.get(int(n), f"{int(n)} times")


def priced_terms_for_confirm(world, court: str, proposal_type: str) -> Optional[Dict[str, Any]]:
    """K item 6: the draft the wizard open priced for (court, proposal type)
    THIS turn — read by `diplomatic_dialogue._enrich_proposal_summary`, so
    the confirm the player opens is pre-filled with the terms the counsel
    quoted. None when no wizard open priced one this turn (the typed road
    drafts afresh). Armistice variants share the "armistice" draft."""
    memory = getattr(world, "talleyrand_counsel_memory", None) or {}
    row = memory.get(court) if isinstance(memory, dict) else None
    if not isinstance(row, dict):
        return None
    if int(row.get("turn", -1)) != int(getattr(world, "current_turn", 0) or 0):
        return None
    kind = "armistice" if str(proposal_type).startswith("armistice") else str(proposal_type)
    terms = (row.get("priced_terms") or {}).get(kind)
    if not isinstance(terms, Mapping):
        return None
    import copy as _copy
    return _copy.deepcopy(dict(terms))


def roads_display(reading: Mapping[str, Any]) -> List[str]:
    """The ranked roads as short lines for the wizard (PC-F12: the hints
    reach the screen): 'Open Settlement with Austria alone — 50 of 50 ✓ (3 DP)'."""
    out: List[str] = []
    for r in reading.get("roads") or []:
        mark = "✓" if (r.get("available") and r.get("carries")) else ("✗" if r.get("available") else "—")
        number = r.get("number") or ""
        if r.get("road") == "battle":
            number = f"{r.get('battles', 0)} of {r.get('battle_cap', 0)}"
        elif number and r.get("threshold"):
            number = f"{number} of {r['threshold']}"
        price = f" ({int(r['price_dp'])} DP)" if r.get("price_dp") else ""
        line = f"{r.get('label')} — {number} {mark}{price}".replace("—  ", "— ")
        if not r.get("available") and r.get("shut_reason"):
            line = f"{r.get('label')} — shut: {r['shut_reason']}"
        out.append(_tidy(line))
    return out


def counsel_for_wizard(world, court: str, *, staged_terms=None, remember: bool = True,
                       priced_terms: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Dict[str, Any]:
    """Ruling K item 5 — the ONE builder: the reading, the line (rotated
    past the court's remembered line), the preference, the roads' display
    lines and the action the counsel names. `remember` writes the court's
    memory (`world.talleyrand_counsel_memory`) — the wizard open does, a
    dry-run does not. K item 6: `priced_terms` (the wizard's memo) is
    remembered beside the line, so the confirm the player opens next is
    pre-filled with the very draft the counsel priced."""
    reading = read_counsel(world, court, staged_terms=staged_terms, priced_terms=priced_terms)
    memory = getattr(world, "talleyrand_counsel_memory", None)
    if not isinstance(memory, dict):
        memory = {}
        world.talleyrand_counsel_memory = memory
    last = memory.get(court) if isinstance(memory.get(court), dict) else None
    composed = compose_counsel_line(reading, last)
    if remember:
        memory[court] = {"situation": composed["situation"], "index": int(composed["index"]),
                         "line": composed["line"], "turn": int(reading.get("turn") or 0),
                         # K item 6: the drafts the roads priced, by proposal type
                         "priced_terms": {str(k): dict(v) for k, v in (priced_terms or {}).items()
                                          if isinstance(v, Mapping)}}
    best = reading.get("best") or {}
    text = composed["line"]
    if composed.get("preference_line"):
        text = f"{text} {composed['preference_line']}"
    return {
        "line": text,
        "recommendation_line": composed["line"],
        "preference_line": composed.get("preference_line", ""),
        "situation": composed["situation"],
        "best_road": str(best.get("road") or ""),
        "best_action": str(best.get("action") or ""),
        "best_war_id": str(best.get("war_id") or ""),
        # K item 6: what the best road opens with — the coverage of a table
        # road (the court alone, or the whole table) and its priced terms.
        "best_coverage": (list(best.get("covered") or [])
                          if str(best.get("road") or "").startswith("table") else []),
        "best_terms": (list(best.get("priced_terms") or [])
                       if str(best.get("road") or "").startswith("table") else []),
        "carrying": list(reading.get("carrying") or []),
        "roads": [
            {k: v for k, v in r.items() if k not in ("separate_peace",)}
            for r in (reading.get("roads") or [])
        ],
        "roads_display": roads_display(reading),
        "preference": dict(reading.get("preference") or {}),
        "tally": dict(reading.get("tally") or {}),
        "own": dict(reading.get("own") or {}),
        "posture": reading.get("posture"), "case": reading.get("case"),
    }

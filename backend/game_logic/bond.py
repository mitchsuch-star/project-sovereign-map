"""The coalition's no-separate-peace bond — Chaumont, 1814 (PC-R7 (ii), part 3;
ruling J of the peace report, `docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §40 J,
§46 J; `docs/BUG_FIXES.md` §PC PC-R7; rules `SYSTEMS_REFERENCE.md` §135).

"The coalition's no-separate-peace bond is a priced, dated clause the
paymaster pays for (Chaumont), so the league's cohesion is a lever the loser
can bid for." This module is the ONE home of the bond: the rule, the price,
the reads, the mint, the AI's paymaster, the words.

**The record.** A D5 directed record (`instruments.grant_directed_sponsorship`)
of kind `"bond"` beside `"sponsorship"` and `"neutrality"`: the PAYER (the
league's paymaster — or France for her own co-belligerent, GR5) pays the
MEMBER a subsidy per turn for her commitment NOT to sign a separate peace
with the AIM (the common enemy) while the payer fights on, for a term. The
same record shape and the same per-turn pass (`instruments.process_instruments`
pays it on the Subsidies line, counts its term, and its renege arm brands a
separate peace inside the term `bargain_reneged` against the member — the
strongest grievance in the game). Dated (`started_turn` / `expiry_turn`),
serialized with the directed records (no new world field).

**The price — derived, never invented.** The stream is the payer's own
subsidy (`agendas.get_paymaster_subsidy_amount`, the figure
`coalition.projected_paymaster_subsidy` pays — 200 to 500 a turn by the
treasury's tier) for the directed record's own term
(`instruments.SPONSORSHIP_DEFAULT_TURNS`, 10). Each surface prices it as the
gold stream it is, at that surface's OWN gold rate (PC-F60: "four rates, each
surface its own"):

  * the bilateral — `strength`: the per-turn stream at the bilateral's
    gold-a-turn sweetener rate (`SWEETENER_VALUES["gold_per_turn"]`, 3 a 100):
    400 a turn reads 12 — the `coalition_bond` component of
    `calculate_acceptance`;
  * the table — `table_price`: the stream still owed (the amount × the turns
    left) at the table's gold rate (`CONCESSION_GOLD_DIVISOR` gold a point,
    capped at `CONCESSION_GOLD_CAP`) — what she forfeits by signing alone; the
    `coalition_bond` component of `calculate_common_peace_acceptance`;
  * the break-ranks read — the strength in the loyalty term's own units: the
    score lines read `strength / bilateral_war_score_weight()` deeper (the
    bilateral's score-to-points rate), the exhaustion line
    `strength × COALITION_LOYALTY_EASE_PER` deeper (§6a's `we // 10`).

**France bids against it** at the table and in the bilateral by what each
already prices: gold to the court (the table's concession credit, the
bilateral's sweetener) or the compensation clause (`territory_compensate`) —
priced, never a veto. The bid row and the counsel's words name the sum.

**A separate peace only.** A package that covers the payer too is the
league's common peace — the bond is honoured, priced at nothing; a truce
leaves the league intact and breaks nothing.

**GR5.** One mint (`mint_bond`), one gate (`mint_refusal`), read by the AI's
paymaster (`ai_paymaster_binds`, from `coalition.process_coalition_turn`
beside the war subsidy) and the player's Cabinet row ("Bind <ally> to the
War", `cabinet_rows.bond_actions`) alike.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional

from backend.errors import report

BOND_KIND = "bond"

# The AI paymaster binds at most this many members a turn (the narration
# budget the sponsor branch keeps — `AI_SPONSORSHIPS_PER_TURN`'s idiom).
AI_BONDS_PER_TURN = 1


# ═══════════════════════════════════════════════════════════════════════════
# The record and its price
# ═══════════════════════════════════════════════════════════════════════════

def bond_term_turns() -> int:
    """The directed record's own term (`instruments.SPONSORSHIP_DEFAULT_TURNS`)."""
    from backend.game_logic.instruments import SPONSORSHIP_DEFAULT_TURNS
    return int(SPONSORSHIP_DEFAULT_TURNS)


def bond_amount(world: Any, payer: str) -> int:
    """The stream a turn: the payer's own subsidy at its treasury's tier
    (`agendas.get_paymaster_subsidy_amount` — the paymaster's war subsidy)."""
    from backend.game_logic.agendas import get_paymaster_subsidy_amount
    return int(get_paymaster_subsidy_amount(world, payer))


def _turns_left(world: Any, record: Mapping[str, Any]) -> int:
    turn = int(getattr(world, "current_turn", 0) or 0)
    return int(record.get("turns_remaining",
                          max(0, int(record.get("expiry_turn", turn)) - turn)) or 0)


def strength(record: Optional[Mapping[str, Any]]) -> int:
    """What breaking the bond costs her in the bilateral's points: the stream
    a turn at the bilateral's gold-a-turn sweetener rate (400 a turn → 12)."""
    if not record:
        return 0
    from backend.game_logic.diplomacy import SWEETENER_VALUES
    rate = float(SWEETENER_VALUES.get("gold_per_turn", 0) or 0)
    return int(round(int(record.get("amount_per_turn", 0) or 0) * rate))


def table_price(world: Any, record: Optional[Mapping[str, Any]]) -> int:
    """What she forfeits at the table by signing alone: the stream still owed
    at the table's gold rate, capped where the table caps gold."""
    if not record:
        return 0
    from backend.game_logic.settlement_scoring import (
        CONCESSION_GOLD_CAP, CONCESSION_GOLD_DIVISOR,
    )
    owed = int(record.get("amount_per_turn", 0) or 0) * max(0, _turns_left(world, record))
    return int(min(CONCESSION_GOLD_CAP, owed // CONCESSION_GOLD_DIVISOR))


def bid_gold(world: Any, record: Optional[Mapping[str, Any]]) -> int:
    """The gold to the bonded court that pays the bond's table price, by the
    table's own credit (`CONCESSION_GOLD_DIVISOR` gold a point)."""
    from backend.game_logic.settlement_scoring import CONCESSION_GOLD_DIVISOR
    return int(table_price(world, record) * CONCESSION_GOLD_DIVISOR)


def _party_gone(world: Any, nation: str) -> bool:
    from backend.game_logic.instruments import _party_gone as gone
    return bool(gone(world, nation))


def live_bonds(world: Any) -> List[Dict[str, Any]]:
    """Every bond record whose term still runs (the pass prunes the rest)."""
    return [r for r in (getattr(world, "directed_sponsorships", None) or [])
            if r.get("kind") == BOND_KIND and _turns_left(world, r) > 0]


def bond_on(world: Any, member: str, enemy: str) -> Optional[Dict[str, Any]]:
    """The live bond binding `member` against `enemy` — its term running and
    its payer still fighting `enemy` (at war or in a truce: a truce keeps the
    league, as the renege arm reads it — a payer at peace has nothing left to
    be abandoned in) — the strongest where several stand. None otherwise."""
    if not member or not enemy:
        return None
    best: Optional[Dict[str, Any]] = None
    for record in live_bonds(world):
        if record.get("recipient") != member or record.get("aim") != enemy:
            continue
        payer = str(record.get("payer") or "")
        if (not payer or _party_gone(world, payer)
                or world.get_diplomatic_state(payer, enemy) not in ("WAR", "ARMISTICE")):
            continue
        if best is None or int(record.get("amount_per_turn", 0) or 0) > int(best.get("amount_per_turn", 0) or 0):
            best = record
    return best


# ═══════════════════════════════════════════════════════════════════════════
# What it binds — the break-ranks read, the table, the bilateral
# ═══════════════════════════════════════════════════════════════════════════

def depth_for_strength(points: int) -> Dict[str, int]:
    """A bond of `points` read in the loyalty term's own units: the score
    lines deeper by the bilateral's score-to-points rate, the exhaustion line
    deeper by §6a's ease rate (10 exhaustion a point)."""
    if points <= 0:
        return {"score": 0, "exhaustion": 0}
    from backend.game_logic.ai_diplomacy import COALITION_LOYALTY_EASE_PER
    from backend.game_logic.diplomacy import bilateral_war_score_weight
    weight = float(bilateral_war_score_weight()) or 1.0
    return {"score": int(round(points / weight)),
            "exhaustion": int(points * COALITION_LOYALTY_EASE_PER)}


def break_ranks_depth(world: Any, member: str, enemy: str) -> Dict[str, Any]:
    """How much deeper `member`'s break-ranks lines read while a bond binds
    her against `enemy`: `{"score", "exhaustion", "strength", "payer"}` —
    zeros without one. The series attribution holds it down
    (`--seam backend.game_logic.bond:break_ranks_depth=lambda *a, **k:
    {"score": 0, "exhaustion": 0, "strength": 0, "payer": ""}`)."""
    record = bond_on(world, member, enemy)
    if record is None:
        return {"score": 0, "exhaustion": 0, "strength": 0, "payer": ""}
    points = strength(record)
    return {**depth_for_strength(points), "strength": int(points),
            "payer": str(record.get("payer") or "")}


def table_component(world: Any, *, court: str, proposer_side_participants: Iterable[str],
                    covered: Iterable[str]) -> Dict[str, Any]:
    """The bond's price on `court`'s row at the table: −`table_price` when a
    live bond binds her against a court of the proposing side and her payer
    is NOT covered by this package (her separate peace — the payer fights
    on); 0 for the league's common peace, or with no bond."""
    out: Dict[str, Any] = {"score": 0, "payer": "", "aim": "", "amount": 0,
                           "turns_left": 0, "common_peace": False}
    covered_set = {str(n) for n in covered or () if n}
    for enemy in [str(n) for n in proposer_side_participants or () if n]:
        record = bond_on(world, court, enemy)
        if record is None:
            continue
        payer = str(record.get("payer") or "")
        out.update({"payer": payer, "aim": enemy,
                    "amount": int(record.get("amount_per_turn", 0) or 0),
                    "turns_left": _turns_left(world, record)})
        if payer in covered_set:
            out["common_peace"] = True
            return out
        out["score"] = -int(table_price(world, record))
        return out
    return out


def pair_bond(world: Any, a: str, b: str) -> Optional[Dict[str, Any]]:
    """PC-X61: the bond that binds either court of the pair against the other
    (`bond_on` both ways) — the truce's automatic exits read it: a bonded
    court's truce never ripens, nor is dictated, into her separate peace (the
    war resumes; a peace with her runs through the table, where the bond is
    priced). None without one. The series attribution holds it down
    (`--seam backend.game_logic.bond:pair_bond=lambda *a, **k: None`)."""
    return bond_on(world, a, b) or bond_on(world, b, a)


def holds_her_letter(world: Any, nation: str, enemy: str) -> bool:
    """PC-X65: a court the league's bond binds against `enemy` writes no
    separate letter of her own (P8's dictated harsh peace) — the league's
    letter is her road; her paymaster's own dictated letter is untouched (the
    payer is not bound). The series attribution holds it down
    (`--seam backend.game_logic.bond:holds_her_letter=lambda *a, **k: False`)."""
    return bond_on(world, nation, enemy) is not None


def letter_keeps_payers(world: Any, covered: Iterable[str], enemy: str) -> List[str]:
    """PC-X66: the paymasters a league letter keeps on it — the payer of a bond
    binding a covered court against `enemy` is never left its war while she
    signs (`ai_diplomacy.leave_a_winning_court_its_war`): Chaumont bound the
    allies to treat together. The series attribution holds it down
    (`--seam backend.game_logic.bond:letter_keeps_payers=lambda *a, **k: []`)."""
    out: List[str] = []
    for court in [str(n) for n in covered or () if n]:
        record = bond_on(world, court, enemy)
        if record is not None and str(record.get("payer") or "") not in out:
            out.append(str(record.get("payer") or ""))
    return out


def consent_held(world: Any, court: str, covered: Iterable[str], enemy: str) -> bool:
    """PC-X66: a bonded court's own readiness to sue is no consent to a letter
    that leaves her paymaster at war — she is scored on her row, where the bond
    prices her separate peace (`ai_diplomacy.letter_consenting_courts`). The
    series attribution holds it down
    (`--seam backend.game_logic.bond:consent_held=lambda *a, **k: False`)."""
    record = bond_on(world, court, enemy)
    return record is not None and str(record.get("payer") or "") not in {str(n) for n in covered or ()}


def hope_subsidy(world: Any, loser: str, victor: str) -> Optional[Dict[str, Any]]:
    """PC-X54: the bond is a subsidy flowing to her — the truce's hope term
    (`diplomacy.truce_hope_alive`) reads it beside the war subsidy:
    `{"payer", "amount", "bond": True}` while a bond binds `loser` against
    `victor`, else None. The series attribution holds it down
    (`--seam backend.game_logic.bond:hope_subsidy=lambda *a, **k: None`)."""
    record = bond_on(world, loser, victor)
    if record is None:
        return None
    return {"payer": str(record.get("payer") or ""),
            "amount": int(record.get("amount_per_turn") or 0), "bond": True}


def bilateral_component(world: Any, *, court: str, proposer: str) -> int:
    """The bond's price on `court`'s answer to `proposer`'s separate peace:
    −`strength` while a live bond binds her against `proposer`."""
    return -int(strength(bond_on(world, court, proposer)))


# ═══════════════════════════════════════════════════════════════════════════
# The mint — one gate, one function (GR5)
# ═══════════════════════════════════════════════════════════════════════════

def shared_enemies(world: Any, payer: str, member: str) -> List[str]:
    """The courts `payer` and `member` both fight (sorted; never each other)."""
    if not payer or not member or world.is_at_war(payer, member):
        return []
    theirs = set(world.get_nations_at_war_with(member) or [])
    return sorted(str(n) for n in (world.get_nations_at_war_with(payer) or [])
                  if n in theirs and n not in (payer, member) and not _party_gone(world, str(n)))


def _envoy_at_the_enemy(world: Any, member: str, enemy: str) -> bool:
    """A separate peace of hers is already on the enemy's desk — the
    player's mailbox (her settlement letter or her bilateral proposal)."""
    if enemy != getattr(world, "player_nation", "France"):
        return False
    try:
        from backend.game_logic.ai_diplomacy import _one_envoy_for_this_war
        if _one_envoy_for_this_war(world, member, enemy):
            return True
    except Exception as exc:
        report(exc, "bond._envoy_at_the_enemy: _one_envoy_for_this_war")
    dm = getattr(world, "dialogue_manager", None)
    if dm is None:
        return False
    try:
        letters = [dm.peek()] + list(dm.iter_queue())
    except Exception as exc:
        report(exc, "bond._envoy_at_the_enemy: dialogue_manager")
        return False
    for entry in letters:
        if not isinstance(entry, Mapping) or entry.get("type") != "incoming_proposal":
            continue
        context = entry.get("context") or {}
        kind = str((context.get("proposal") or {}).get("type") or "")
        if str(context.get("source_nation") or "") == member and kind == "peace":
            return True
    return False


def mint_refusal(world: Any, payer: str, member: str, enemy: str) -> str:
    """"" when `payer` may bind `member` against `enemy`; else the reason in
    words. ONE gate, read by the AI's paymaster and the player's row."""
    from backend.display_names import display_nation as _dn
    from backend.game_logic.coalition import (
        A_SUBSIDY_PAYS_A_COURT_THAT_FIGHTS, fields_an_army,
    )
    from backend.game_logic.instruments import SPONSOR_SUSTAIN_MULT
    if not payer or not member or not enemy:
        return "No court to bind."
    if member == payer:
        return "A court cannot bind itself."
    for court in (payer, member, enemy):
        if _party_gone(world, court):
            return f"{_dn(court)} has fallen."
    if member == enemy or payer == enemy:
        return "A court cannot be bound against itself."
    if not world.is_at_war(payer, enemy):
        return f"{_dn(payer)} is not at war with {_dn(enemy)}."
    if not world.is_at_war(member, enemy):
        return f"{_dn(member)} is not at war with {_dn(enemy)}."
    if world.is_at_war(payer, member):
        return f"{_dn(payer)} is at war with {_dn(member)}."
    lord = ((getattr(world, "vassals", {}) or {}).get(member) or {})
    if isinstance(lord, Mapping) and lord.get("lord") == payer:
        return f"{_dn(member)} is {_dn(payer)}'s vassal — she has no peace of her own to sell."
    if A_SUBSIDY_PAYS_A_COURT_THAT_FIGHTS and not fields_an_army(world, member):
        return f"{_dn(member)} has no army in the field — a bond pays a court that fights."
    for record in getattr(world, "directed_sponsorships", None) or []:
        if (record.get("kind") == BOND_KIND and record.get("payer") == payer
                and record.get("recipient") == member and record.get("aim") == enemy):
            return f"The bond with {_dn(member)} already stands."
    if _envoy_at_the_enemy(world, member, enemy):
        return f"{_dn(member)}'s envoy is already at {_dn(enemy)}'s court."
    amount = bond_amount(world, payer)
    chest = int((getattr(world, "nation_gold", {}) or {}).get(payer, 0) or 0)
    if chest < amount * SPONSOR_SUSTAIN_MULT:
        return (f"The treasury holds {chest:,} gold — it cannot sustain {amount} a turn "
                f"(four turns' cover, {amount * SPONSOR_SUSTAIN_MULT:,}).")
    return ""


def mint_bond(world: Any, *, payer: str, member: str, enemy: str) -> Dict[str, Any]:
    """Bind `member` to the war against `enemy` at `payer`'s subsidy for the
    term — the ONE mint, through the D5 directed record (GR5). Refused in the
    gate's words; on success `{"success", "record", "event", "message"}`."""
    why = mint_refusal(world, payer, member, enemy)
    if why:
        return {"success": False, "message": why}
    from backend.game_logic.instruments import grant_directed_sponsorship
    amount = bond_amount(world, payer)
    result = grant_directed_sponsorship(
        world, payer=payer, recipient=member, aim=enemy,
        amount_per_turn=amount, turns=bond_term_turns(), kind=BOND_KIND)
    if not result.get("success"):
        return result
    record = result["record"]
    result["message"] = minted_line(world, record)
    _announce(world, record)
    return result


def _announce(world: Any, record: Mapping[str, Any]) -> None:
    """The bond is the most consequential fact about why a court will not
    settle: when France is its aim (or its payer), the rail says so."""
    player = getattr(world, "player_nation", "France")
    if player not in (record.get("aim"), record.get("payer"), record.get("recipient")):
        return
    try:
        from backend.notifications import (
            DIPLOMATIC_PROPOSAL, NotificationPriority, create_notification,
        )
        world.notifications.add(create_notification(
            DIPLOMATIC_PROPOSAL, NotificationPriority.HIGH,
            title_line(world, record), minted_line(world, record),
            int(getattr(world, "current_turn", 0) or 0)))
    except Exception as exc:
        report(exc, "bond._announce")


def ai_paymaster_binds(world: Any) -> List[Dict[str, Any]]:
    """The league's paymaster binds a member — Chaumont. On a deck world (the
    `paymaster` design's court, `agendas.get_paymaster_nation`), while the
    league stands with two or more members at war with its target, the
    paymaster binds the member that would break ranks NOW (P1's own clause)
    and whom the bond's depth would hold — the court about to leave, where its
    gold can keep her — through the same mint the player's row calls. One a
    turn. Its DP from its own pool when it holds any (the sponsor branch's
    idiom). The series attribution holds it down
    (`--seam backend.game_logic.bond:ai_paymaster_binds=lambda w: []`)."""
    if not (getattr(world, "agendas", {}) or {}):
        return []
    coalition = getattr(world, "active_coalition", None) or {}
    if not coalition:
        return []
    from backend.game_logic.agendas import get_paymaster_nation
    payer = get_paymaster_nation(world)
    if not payer:
        return []
    target = str(coalition.get("target_nation") or getattr(world, "player_nation", "France"))
    members = [str(m) for m in (coalition.get("members") or []) if m]
    at_war = [m for m in members if world.is_at_war(m, target)]
    if len(at_war) < 2 or payer not in at_war:
        return []
    from backend.game_logic.ai_diplomacy import coalition_break_ranks_reason
    from backend.game_logic.diplomacy import get_war_score_for
    events: List[Dict[str, Any]] = []
    for member in at_war:
        if len(events) >= AI_BONDS_PER_TURN:
            break
        if member == payer or mint_refusal(world, payer, member, target):
            continue
        score = int(get_war_score_for(world, member, target))
        key = world._make_diplo_key(member, target)
        if coalition_break_ranks_reason(world, member, war_score=score, diplo_key=key) is None:
            continue  # loyal of her own accord — nothing to buy
        held = depth_for_strength(strength({"amount_per_turn": bond_amount(world, payer)}))
        if coalition_break_ranks_reason(world, member, war_score=score, diplo_key=key,
                                        depth=held) is not None:
            continue  # past even the bond's line — gold cannot hold her
        result = mint_bond(world, payer=payer, member=member, enemy=target)
        if not result.get("success"):
            continue
        nation_dp = getattr(world, "nation_dp", None)
        if isinstance(nation_dp, dict) and int(nation_dp.get(payer, 0) or 0) >= 1:
            nation_dp[payer] = int(nation_dp.get(payer, 0)) - 1
        events.append(dict(result["event"]))
    return events


# ═══════════════════════════════════════════════════════════════════════════
# The words
# ═══════════════════════════════════════════════════════════════════════════

def _shown(world: Any, nation: str) -> str:
    from backend.game_logic.formations import formed_display_name
    return formed_display_name(world, nation)


def title_line(world: Any, record: Mapping[str, Any]) -> str:
    return (f"{_shown(world, str(record.get('payer')))} binds "
            f"{_shown(world, str(record.get('recipient')))} to the war")


def minted_line(world: Any, record: Mapping[str, Any]) -> str:
    """"Britain binds Austria to the war against France: no separate peace for
    10 turns, 400 gold a turn. A separate peace inside the term is a broken
    bargain; her answer to one carries the bond (40 at the table, 12 in a
    bilateral peace).\""""
    payer = _shown(world, str(record.get("payer")))
    member = _shown(world, str(record.get("recipient")))
    aim = _shown(world, str(record.get("aim")))
    turns = _turns_left(world, record)
    return (f"{payer} binds {member} to the war against {aim}: no separate peace for "
            f"{turns} turn{'s' if turns != 1 else ''}, {int(record.get('amount_per_turn', 0))} "
            f"gold a turn. A separate peace inside the term is a broken bargain; "
            f"{member}'s answer to one carries the bond ({table_price(world, record)} at "
            f"the table, {strength(record)} in a bilateral peace).")


_LAPSE_WORDS = {
    "honoured": "the league's common peace honours it",
    "payer_at_peace": "{payer} left the war first",
    "subjugated": "{member} is the enemy's vassal now",
    "followed_her_lord": "{member} followed her lord out of the war",
}


def log_line(event_type: str, event: Mapping[str, Any]) -> str:
    """The campaign log's one-liner for a bond's event (the directed records'
    own event types, kind "bond") — "" for anything else."""
    from backend.display_names import display_nation as _dn
    payer = _dn(str(event.get("payer") or ""))
    member = _dn(str(event.get("recipient") or ""))
    aim = _dn(str(event.get("aim") or ""))
    if event_type == "sponsorship_granted":
        return (f"{payer} binds {member} to the war against {aim} — no separate peace for "
                f"{int(event.get('turns', 0) or 0)} turns ({int(event.get('amount', 0) or 0)}g/turn)")
    if event_type == "sponsorship_reneged":
        return (f"THE BROKEN BARGAIN: {_dn(str(event.get('breaker') or ''))} breaks the bond with "
                f"{_dn(str(event.get('victim') or ''))} — a separate peace with {aim} inside the term")
    if event_type == "sponsorship_expired":
        return f"The bond between {payer} and {member} runs its term"
    if event_type == "instrument_lapsed":
        why = _LAPSE_WORDS.get(str(event.get("reason") or ""), "")
        return (f"The bond between {payer} and {member} lapses"
                + (f" — {why.format(payer=payer, member=member)}" if why else ""))
    return ""


def binds_clause(world: Any, payer: str) -> str:
    """"binds Austria to the war (no separate peace; 400g a turn, 6 turns
    left)" for every live bond `payer` pays — "" with none. The paymaster's
    surfaces (the Diplomatic Ledger's subsidy panel, the state desk's
    coalition answer) say it beside the subsidy."""
    pieces = [f"{_shown(world, str(r.get('recipient')))} to the war against "
              f"{_shown(world, str(r.get('aim')))} ({int(r.get('amount_per_turn', 0))}g a turn, "
              f"{_turns_left(world, r)} turns left)"
              for r in live_bonds(world) if r.get("payer") == payer]
    if not pieces:
        return ""
    return "binds " + "; ".join(pieces) + " — no separate peace"


def compact_words(world: Any, record: Mapping[str, Any]) -> str:
    """The instruments line's piece (the Diplomatic Ledger's Compacts)."""
    turns = _turns_left(world, record)
    return (f"{_shown(world, str(record.get('payer')))} binds "
            f"{_shown(world, str(record.get('recipient')))} to the war against "
            f"{_shown(world, str(record.get('aim')))} — no separate peace "
            f"({int(record.get('amount_per_turn', 0))}g/turn, {turns} turn"
            f"{'s' if turns != 1 else ''} left, since turn {int(record.get('started_turn', 0))})")


def compensation_bid(world: Any, court: str, enemy: str,
                     war_instance: Optional[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
    """The compensation the enemy's side could offer `court` at the table
    (`compensation.paid_candidates` first, then the pointed form) with its
    credit — France's other bid against the bond. None without one."""
    if not war_instance:
        return None
    from backend.game_logic import compensation as CO
    side = (war_instance.get("side_by_nation") or {}).get(enemy)
    members = [str(n) for n in (war_instance.get(side) or [enemy]) if n] if side else [enemy]
    try:
        paid = CO.paid_candidates(world, compensated=court, payer_side_members=members,
                                  war_instance=war_instance)
        if paid:
            region, payer = paid[0]
            return {"region": region, "payer": payer, "form": "paid",
                    "credit": int(CO.table_credit({"region": region}))}
        pointed = CO.pointed_candidates(world, compensated=court, payer=enemy,
                                        war_instance=war_instance)
        if pointed:
            row = pointed[0]
            return {"region": row["region"], "payer": enemy, "form": "pointed",
                    "title": row["design_title"],
                    "credit": int(CO.table_credit({"region": row["region"],
                                                   "design": row["design"]}))}
    except Exception as exc:
        report(exc, "bond.compensation_bid")
    return None


def guided_suggestions(world: Any, *, court: str, war_id: str, draft_key: str,
                       proposer_side_participants: Iterable[str], proposer_leader: str,
                       covered: Iterable[str], treasury_remaining: int) -> List[Dict[str, Any]]:
    """France's bid against the bond at the table — one "Offers to <court>"
    row, "Outbid Britain's bond — 1,000 gold to Austria", where this package
    is her separate peace (the bond priced on her row); the sum is the bond's
    table price at the table's own gold credit, so the bid offsets it exactly
    (the compensation rows beside it are the other bid). Shut, in words, when
    the chest cannot pay. [] where no bond is priced."""
    comp = table_component(world, court=court, proposer_side_participants=proposer_side_participants,
                           covered=covered)
    if int(comp.get("score") or 0) >= 0:
        return []
    record = bond_on(world, court, str(comp.get("aim") or ""))
    if record is None:
        return []
    from backend.game_logic.settlement_staging import _guided_suggestion
    gold = bid_gold(world, record)
    payer = _shown(world, str(record.get("payer")))
    shown = _shown(world, court)
    available = int(treasury_remaining) >= gold
    return [_guided_suggestion(
        label=f"Outbid {payer}'s bond — {gold:,} gold to {shown}",
        group="offer", clause_type="gold_indemnity",
        reason_display=(f"{payer} pays her {int(record.get('amount_per_turn', 0))} a turn not to "
                        f"sign alone, Sire — match what she would forfeit, and the bond weighs "
                        f"nothing at this table."),
        court=court, war_id=war_id, draft_key=draft_key, params={"amount": int(gold)},
        available=available,
        disabled_reason_display=("" if available else
                                 f"The treasury has {int(treasury_remaining):,} gold left for "
                                 f"this table — the bid is {gold:,}."),
        terms_display=(f"+{table_price(world, record)} to {shown}'s answer — the bond's price "
                       f"({int(record.get('amount_per_turn', 0))}g a turn, "
                       f"{_turns_left(world, record)} turns left)"),
        bond_bid=True,
    )]


def bid_opening_terms(world: Any, *, war_id: str, payer: str, court: str, amount: int,
                      covered: Iterable[str]) -> List[Dict[str, Any]]:
    """The draft the Cabinet's "Outbid <payer>'s Bond" opens the table with:
    the draft it would open with anyway (the articles declared at the war —
    `declared_goals.declared_draft` — else the bare peace) and France's bid,
    a gold indemnity to the court of `amount`."""
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    side = str((instance.get("side_by_nation") or {}).get(payer) or "")
    terms: List[Dict[str, Any]] = []
    if side:
        try:
            from backend.game_logic.declared_goals import declared_draft
            terms = [dict(t) for t in declared_draft(world, war_instance=instance, proposer_side=side,
                                                      proposer_leader=payer, covered=list(covered))]
        except Exception as exc:
            report(exc, "bond.bid_opening_terms: declared_draft")
            terms = []
    if not terms:
        terms = [{"type": "peace"}]
    terms.append({"type": "gold_indemnity", "from": payer, "to": court, "amount": int(amount)})
    return terms


def price_line(world: Any, court: str, enemy: str, *,
               war_instance: Optional[Mapping[str, Any]] = None) -> str:
    """The bond's price and France's bid, said where a separate peace with
    `court` is priced — "Britain's bond costs her 40 at the table (12 in a
    bilateral peace); 1,000 gold to her pays it — or Franconia, Bavaria's
    (+35), most of it." — "" without one."""
    record = bond_on(world, court, enemy)
    if record is None:
        return ""
    payer = _shown(world, str(record.get("payer")))
    at_table = table_price(world, record)
    words = (f"{payer}'s bond costs her {at_table} at the table "
             f"({strength(record)} in a bilateral peace); "
             f"{bid_gold(world, record):,} gold to her pays it")
    comp = compensation_bid(world, court, enemy, war_instance)
    if comp:
        what = (f"{comp['region']}, {_shown(world, comp['payer'])}'s" if comp["form"] == "paid"
                else f"{comp['title']} ({comp['region']})")
        share = "which pays it" if int(comp["credit"]) >= at_table else "most of it"
        words += f" — or {what} (+{int(comp['credit'])}), {share}"
    return words + "."

"""AU-1 "the books and the figure" — the standing: ONE writer, ONE quote, and
the books of authority (`docs/AUTHORITY_CURRENCY_SPEC.md` §5.1–§5.2, §5.6,
§5.8; the rules `SYSTEMS_REFERENCE.md` §169).

The code name is `standing`; the player's word is "Authority". The store
keeps its name (`AuthorityTracker`, `backend/models/authority.py`) and this
module is the only door to it in production:

  * `move(world, lord, delta, cause, party="", **fmt)` — the one writer. The
    player's tracker books every move in its ring with a cause from
    `display_names.AUTHORITY_CAUSES` (in the creditor's voice) and fires the
    threshold events on every crossing; a court's figure is
    `world.nation_authority[lord]`, clamped, no ring (the courts' books are
    AU-4's). An AST census forbids a write outside the store and a cause
    census forbids an empty one (`tests/test_standing_books.py`).
  * `quote(world, lord, delta)` — the one quote: `reforms.authority_line`
    (pinned, untouched) + `ledger.charges_grip_clause` + the Presence clause
    when the aura would change. Every button and every apply read it.
  * `refusal(world, lord, delta)` — the purchases' floor: a price lands whole
    or the button is closed with its reason (§5.1 — never a clamp). Under
    the grip's 60 (the diplomatic point's line) a purchase refuses. Nothing
    in production calls it at AU-1; the pushes (AU-3a / AU-3b) do.
  * `spend` / `regrow` — the purchases and the lumps (AU-3a / AU-2b call
    them): a spend is the quote then the move; a regrowth stops at the
    ceiling 95 and keeps its cooldown keyed in the tracker's `held`.
  * `payload` — the chip's one key on every base response; `dent_clause` —
    the morning's "down 9 since yesterday: …" on the dispatch's line, stamped
    at build; `pop_event` — the threshold box the next response carries.
  * `ai_refusal` — the courts' floors (30, and three diplomatic points a
    turn), the reforms' own rule, extracted so the courts' Decree (AU-3a's
    `find_ai_edict`) and their laws read one gate.
  * `keeps_books()` — the series rig's seam (arm AUB: the writer passes the
    clamped figure through and books nothing); `courts_move()` — the courts'
    new sources and battle writes, PARKED (False) until AU-4 flips it on the
    user's word.

Nothing moves by waiting (§5.1): every move sits on an event. No per-turn
rule here scans the regions (Golden Rule 8).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

# §5.1 the band and the floors (in-band tunable; the shapes are §4's rulings)
PURCHASE_FLOOR = 60     # the grip after a purchase's price must stay at 60 or above
CEILING = 95            # new gains (`regrow`) stop at 95; the field, the Temple and Naples write through `move`
MOVES_SHOWN = 5         # the payload's tail — the chip's tooltip
COURT_DEFAULT = 60      # the courts' table boots at 60 (`nation_config`); a court missing from it reads 60


# ─────────────────────────────── the store ───────────────────────────────

def is_player(world, lord: str) -> bool:
    return bool(lord) and lord == getattr(world, "player_nation", None)


def tracker_of(world, lord: str):
    """The player's tracker, or None for a court. An empty `lord` names the
    world's own tracker (a bare game-state object in the vindication path)."""
    if not lord or is_player(world, lord):
        return getattr(world, "authority_tracker", None)
    return None


def standing_of(world, lord: str) -> int:
    tracker = tracker_of(world, lord)
    if tracker is not None:
        return int(getattr(tracker, "authority", 0) or 0)
    table = getattr(world, "nation_authority", None)
    if isinstance(table, dict):
        return int(table.get(lord, COURT_DEFAULT) or 0)
    return 0


def grip_of(world, lord: str) -> int:
    from backend.models.authority import get_imperial_grip
    try:
        return int(get_imperial_grip(world, lord))
    except Exception as exc:        # a bare fixture world with no capitals: the court figure stands in
        from backend.errors import report
        report(exc, "standing.grip_of: get_imperial_grip")
        return standing_of(world, lord)


def _aura_of_grip(grip: int) -> float:
    from backend.models.authority import AURA_GRIP_BROKEN, AURA_GRIP_FULL
    if grip >= AURA_GRIP_FULL:
        return 1.0
    if grip <= AURA_GRIP_BROKEN:
        return 0.0
    return (grip - AURA_GRIP_BROKEN) / (AURA_GRIP_FULL - AURA_GRIP_BROKEN)


def _standing_sovereign(world, lord: str):
    for m in (getattr(world, "marshals", {}) or {}).values():
        if (getattr(m, "nation", None) == lord and getattr(m, "is_sovereign", False)
                and not getattr(m, "captured_by", "") and int(getattr(m, "strength", 0) or 0) > 0):
            return m
    return None


def presence_of(world, lord: str, grip: Optional[int] = None) -> int:
    """The Presence as the field reads it (+10 % full … 0), −1 when no
    sovereign of the lord's stands under arms."""
    if _standing_sovereign(world, lord) is None:
        return -1
    g = grip_of(world, lord) if grip is None else int(grip)
    return int(round(10 * _aura_of_grip(g)))


def keeps_books() -> bool:
    """The series rig's seam (arm AUB): True = the books are open."""
    return True


# §5.4 the hits (AU-2a) — three named seams, no levers
def hits_armed() -> bool:
    """Arm AUP: the Chancellor's and the Host's floor clause (`bites_since`) and
    the Host's authority op (`since`) — down, the deck reads as before AU-2a."""
    return True


def claims_armed() -> bool:
    """Arm AUK: the Claims of the Army on the dotation tick."""
    return True


def breach_armed() -> bool:
    """Arm AUW: the word broken (a treaty breach's strikes) and Make Amends' repayment."""
    return True


def courts_move() -> bool:
    """§5.7: the courts' new sources and battle writes — PARKED until AU-4
    flips it on the user's word (the RE-6 pattern)."""
    return False


# ─────────────────────────────── the writer ───────────────────────────────

def move(world, lord: str, delta: int, cause: str, party: str = "", **fmt) -> int:
    """THE writer. Returns the delta applied (after the clamp). The player's
    tracker books the move with its cause and fires the threshold events;
    a court's table is clamped 0–100 with no ring."""
    from backend.display_names import authority_cause
    delta = int(delta)
    key = str(cause or "unattributed")
    tracker = tracker_of(world, lord)
    if tracker is not None:
        return int(tracker.move(delta, key, authority_cause(key, **fmt), str(party or ""),
                                turn=int(getattr(world, "current_turn", 0) or 0),
                                book=keeps_books()))
    if not lord or is_player(world, lord):
        return 0            # a player's world without a tracker (a bare fixture): nothing to write
    table = getattr(world, "nation_authority", None)
    if not isinstance(table, dict):
        return 0
    before = int(table.get(lord, COURT_DEFAULT) or 0)
    after = max(0, min(100, before + delta))
    table[lord] = after
    return after - before


# ─────────────────────────────── the quote ───────────────────────────────

def refusal(world, lord: str, delta: int) -> str:
    """§5.1: "" when a purchase of `delta` (negative) may land whole; else
    why — the grip after the price under PURCHASE_FLOOR, or no store. A gain
    is never refused here (`regrow` keeps its own ceiling)."""
    delta = int(delta)
    if delta >= 0:
        return ""
    if is_player(world, lord):
        if tracker_of(world, lord) is None:
            return "no standing to spend"
        before = standing_of(world, lord)
        grip_after = grip_of(world, lord) + delta
        if grip_after < PURCHASE_FLOOR:
            return (f"Authority {before} → {before + delta} would take the Emperor's grip under "
                    f"{PURCHASE_FLOOR} (to {grip_after}), the diplomatic point's line — refused")
        return ""
    return ai_refusal(world, lord, -delta)


def quote(world, lord: str, delta: int) -> Dict[str, Any]:
    """The one quote of a move of `delta`: {before, after, grip_before,
    grip_after, presence_before, presence_after, refusal, line}. The line is
    `reforms.authority_line` + the Charges' grip clause + the Presence clause
    when the aura would change; shown = applied by construction."""
    from backend.game_logic.reforms import authority_line
    delta = int(delta)
    before = standing_of(world, lord)
    after = max(0, min(100, before + delta))
    grip_before = grip_of(world, lord)
    grip_after = max(0, min(100, grip_before + (after - before)))
    line = authority_line(before, after).rstrip(".")
    presence_before = presence_after = -1
    if is_player(world, lord):
        from backend.game_logic.ledger import charges_grip_clause
        clause = str(charges_grip_clause(world, lord, before, after) or "").rstrip(".")
        if clause:
            line = f"{line}; {clause}"
        presence_before = presence_of(world, lord, grip_before)
        presence_after = presence_of(world, lord, grip_after)
        if presence_before >= 0 and presence_after != presence_before:
            line = f"{line}; the Presence +{presence_before}% → +{presence_after}%"
    return {"before": before, "after": after, "grip_before": grip_before, "grip_after": grip_after,
            "presence_before": presence_before, "presence_after": presence_after,
            "refusal": refusal(world, lord, delta), "line": line + "."}


def spend(world, lord: str, amount: int, cause: str, party: str = "", **fmt) -> Dict[str, Any]:
    """A purchase: the quote, then the move — or the refusal with nothing
    applied (the one price rule: it lands whole or the button is closed)."""
    price = -abs(int(amount))
    q = quote(world, lord, price)
    if q["refusal"]:
        return dict(q, applied=0)
    return dict(q, applied=move(world, lord, price, cause, party, **fmt))


def regrow(world, lord: str, amount: int, cause: str, key: str, every: int = 0,
           party: str = "", **fmt) -> int:
    """A lump of regrowth (the Te Deum, the Bulletin, the Return — AU-2b's
    callers): +amount up to CEILING, once per `every` turns per `key` (the
    cooldown kept in the tracker's `held`). Returns what was applied. A
    court's regrowth is parked behind `courts_move()`."""
    amount = abs(int(amount))
    if not amount:
        return 0
    tracker = tracker_of(world, lord)
    if tracker is None and not courts_move():
        return 0
    held = getattr(tracker, "held", None) if tracker is not None else None
    turn = int(getattr(world, "current_turn", 0) or 0)
    if every and isinstance(held, dict):
        last = held.get(f"last:{key}")
        if last is not None and turn - int(last) < int(every):
            return 0
    room = CEILING - standing_of(world, lord)
    if room <= 0:
        return 0
    applied = move(world, lord, min(amount, room), cause, party, **fmt)
    if applied and isinstance(held, dict):
        held[f"last:{key}"] = turn
    return applied


def ai_refusal(world, lord: str, price: int) -> str:
    """The courts' floors (`reforms.ai_purse_refusal`'s own rule, extracted):
    a price never takes a court under AI_AUTHORITY_FLOOR, nor leaves it fewer
    than AI_DIPLOMACY_FLOOR diplomatic points a turn. "" when it may pay."""
    from backend.game_logic.reforms import AI_AUTHORITY_FLOOR, AI_DIPLOMACY_FLOOR, _court_dp_after
    authority = standing_of(world, lord)
    after = authority - int(price)
    if after < AI_AUTHORITY_FLOOR:
        return f"authority {authority} → {after} is under {AI_AUTHORITY_FLOOR}"
    if _court_dp_after(world, lord, after) < AI_DIPLOMACY_FLOOR:
        return (f"authority {after} would leave fewer than "
                f"{AI_DIPLOMACY_FLOOR} diplomatic points a turn")
    return ""


# ─────────────────────────────── the figure ───────────────────────────────

def payload(world, lord: str) -> Dict[str, Any]:
    """The chip's one key on every base response: {value, label, grip,
    presence, moves[≤ MOVES_SHOWN, newest first]} — every number an int."""
    tracker = tracker_of(world, lord)
    value = standing_of(world, lord)
    label = str(tracker.get_authority_label()) if tracker is not None and hasattr(tracker, "get_authority_label") else ""
    grip = grip_of(world, lord)
    ring = list(getattr(tracker, "moves", None) or []) if tracker is not None else []
    moves = [{"turn": int(m.get("turn", 0) or 0), "delta": int(m.get("delta", 0) or 0),
              "cause": str(m.get("cause") or ""), "party": str(m.get("party") or "")}
             for m in reversed(ring[-MOVES_SHOWN:])]
    return {"value": int(value), "label": label, "grip": int(grip),
            "presence": int(presence_of(world, lord, grip)), "moves": moves}


def dent(world, lord: str) -> List[Dict[str, Any]]:
    """The moves since the last morning's stamp (`held["told"]`), oldest first."""
    tracker = tracker_of(world, lord)
    if tracker is None:
        return []
    told = int((getattr(tracker, "held", None) or {}).get("told", 0) or 0)
    return [dict(m) for m in (getattr(tracker, "moves", None) or []) if int(m.get("seq", 0) or 0) > told]


def dent_clause(world, lord: str, stamp: bool = True) -> str:
    """§5.6: the dent the morning it lands — "" on a quiet morning (the line
    byte-identical), else " — down 9 since yesterday: Ney honoured (−4), the
    field at Elchingen under your own hand (−5)", with the Presence's line
    when the aura's 85 was crossed. Stamped at build (`held["told"]`): the
    stored dispatch is frozen and a re-read serves the same text."""
    rows = dent(world, lord)
    if not rows:
        return ""
    tracker = tracker_of(world, lord)
    total = sum(int(r.get("delta", 0) or 0) for r in rows)
    parts = []
    for r in rows:
        d = int(r.get("delta", 0) or 0)
        parts.append(f"{r.get('cause') or 'unattributed'} ({'+' if d > 0 else '−'}{abs(d)})")
    word = "down" if total < 0 else "up" if total > 0 else "even"
    clause = (f" — {word} {abs(total)} since yesterday: " if total else " — even since yesterday: ") + ", ".join(parts)
    from backend.models.authority import AURA_GRIP_FULL
    grip_now = grip_of(world, lord)
    grip_before = grip_now - total
    if _standing_sovereign(world, lord) is not None:
        if grip_before >= AURA_GRIP_FULL > grip_now:
            clause += f"; the Presence falls below {AURA_GRIP_FULL}"
        elif grip_before < AURA_GRIP_FULL <= grip_now:
            clause += f"; the Presence returns at {AURA_GRIP_FULL}"
    if stamp and tracker is not None:
        held = getattr(tracker, "held", None)
        if isinstance(held, dict):
            held["told"] = int(held.get("seq", 0) or 0)
    return clause


# ─────────────────────────────── the hits (AU-2a) ───────────────────────────────

CLAIMS_TURN = 14          # the Claims of the Army: a claim fourteen turns unpaid (the Treasury crisis of January 1806)
CLAIMS_FLOOR = 80         # … never under 80 on the grip after the bill
CLAIMS_AMOUNT = 3         # −3 per marshal, once per claim
CLAIMS_RENTE_TURNS = 20   # … while the chest holds twenty turns of his rente
BREACH_STRIKE = 3         # the word broken: −3 per at-fault strike
BREACH_EPISODE_CAP = 6    # at most −6 an episode
AMENDS_REPAY = 2          # Make Amends repays +2 of the debt owed to that court


def claims_of_the_army(world, marshal, elapsed: int) -> int:
    """§5.4 the Claims of the Army, on the dotation tick: a marshal's claim at
    `elapsed == CLAIMS_TURN` exactly, while the chest holds CLAIMS_RENTE_TURNS of
    his rente (`dotation.get_rente_cost`), never under CLAIMS_FLOOR on the grip
    after, once per claim (the paid marks in `held["claims"]`, keyed by the
    claim's opening turn — a re-opened claim is a new claim); Berthier presents
    it on the morning's line. The player's marshals; a court's claims are the
    courts' books (AU-4). Returns the delta applied."""
    if not claims_armed() or int(elapsed) != CLAIMS_TURN:
        return 0
    lord = str(getattr(marshal, "nation", "") or "")
    tracker = tracker_of(world, lord) if is_player(world, lord) else None
    if tracker is None:
        return 0
    from backend.game_logic.dotation import compute_rente_face, get_rente_cost
    rente = int(get_rente_cost(compute_rente_face(marshal, world), world, lord))
    if rente <= 0:
        return 0
    chest = int((getattr(world, "nation_gold", {}) or {}).get(lord, 0) or 0)
    if chest < CLAIMS_RENTE_TURNS * rente:
        return 0
    key = f"{marshal.name}:{int(getattr(marshal, 'expectation_grace_turn', -1) or -1)}"
    paid = list(tracker.held.get("claims") or [])
    if key in paid:
        return 0
    if grip_of(world, lord) - CLAIMS_AMOUNT < CLAIMS_FLOOR:
        return 0
    before = standing_of(world, lord)
    applied = move(world, lord, -CLAIMS_AMOUNT, "claims", party=str(marshal.name), marshal=str(marshal.name))
    tracker.held["claims"] = paid + [key]
    if applied:
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "moment_receipt", {
            "line": (f"Berthier presents the claims of the army: {marshal.name}, fourteen turns "
                     f"unpaid while the chest could pay his rente — authority {before} → {before + applied}."),
            "register": "claims"}, "always")
    return applied


def breach(world, preview: Dict[str, Any]) -> int:
    """§5.4 the word broken: a treaty breach at the lord's fault costs
    BREACH_STRIKE per strike, at most BREACH_EPISODE_CAP an episode (the tally
    `held["breach:<episode>"]`); the debt owed to the injured court
    (`held["owed:<court>"]`) is what Make Amends repays. A court's breach is the
    courts' books (AU-4). Returns the delta applied."""
    if not breach_armed():
        return 0
    lord = str((preview or {}).get("fault_nation") or "")
    injured = str((preview or {}).get("injured_party") or "")
    tracker = tracker_of(world, lord) if lord and is_player(world, lord) else None
    if tracker is None or not injured:
        return 0
    key = f"breach:{str((preview or {}).get('episode_id') or '')}"
    taken = int(tracker.held.get(key, 0) or 0)
    strike = min(BREACH_STRIKE, BREACH_EPISODE_CAP - taken)
    if strike <= 0:
        return 0
    applied = move(world, lord, -strike, "breach", party=injured, court=injured)
    if applied:
        tracker.held[key] = taken - applied
        owed_key = f"owed:{injured}"
        tracker.held[owed_key] = int(tracker.held.get(owed_key, 0) or 0) - applied
    return applied


def amends(world, lord: str, court: str) -> int:
    """§5.4 Make Amends repays AMENDS_REPAY of the breach's dents owed to that
    court — a repayment, never a price (it cannot net positive); the ceiling 95
    is `regrow`'s. Returns the delta applied."""
    if not breach_armed():
        return 0
    tracker = tracker_of(world, lord)
    if tracker is None or not court:
        return 0
    owed_key = f"owed:{court}"
    owed = int(tracker.held.get(owed_key, 0) or 0)
    if owed <= 0:
        return 0
    applied = regrow(world, lord, min(AMENDS_REPAY, owed), "amends", f"amends:{court}",
                     party=court, court=court)
    if applied:
        left = owed - applied
        if left > 0:
            tracker.held[owed_key] = left
        else:
            tracker.held.pop(owed_key, None)
    return applied


def breach_confirm_clause(world, lord: str) -> str:
    """§5.4: the word broken, priced on the war-declaration confirm — the
    first strike's quote, the one every button reads; "" while the breach is
    held down (arm AUW)."""
    if not breach_armed():
        return ""
    return " And the court keeps its own count: " + quote(world, lord, -BREACH_STRIKE)["line"]


def _signed(n: int) -> str:
    return f"+{int(n)}" if int(n) > 0 else f"−{abs(int(n))}"


def insist_stake_line() -> str:
    """§5.4 the stakes told in figures: what insisting on an order risks and
    wins when its own battle is judged (`vindication.resolve_battle`'s figures),
    printed under the marshal's words on the objection dialog."""
    from backend.commands.vindication import (
        COMPROMISE_LOSS_AUTHORITY, COMPROMISE_LOSS_TRUST, COMPROMISE_WIN_AUTHORITY,
        INSIST_LOSS_AUTHORITY, INSIST_LOSS_TRUST, INSIST_WIN_AUTHORITY)
    return (f"If the field is lost under your insistence: trust {_signed(INSIST_LOSS_TRUST)}, "
            f"authority {_signed(INSIST_LOSS_AUTHORITY)}; won: authority {_signed(INSIST_WIN_AUTHORITY)}. "
            f"A compromise: authority {_signed(COMPROMISE_WIN_AUTHORITY)} won, "
            f"trust {_signed(COMPROMISE_LOSS_TRUST)} and authority {_signed(COMPROMISE_LOSS_AUTHORITY)} lost.")


def pop_event(world) -> Optional[Dict[str, Any]]:
    """The threshold box the next response carries (read, then cleared —
    Golden Rule 4); None when no line was crossed since the last response."""
    tracker = getattr(world, "authority_tracker", None)
    if tracker is None or not hasattr(tracker, "pop_event"):
        return None
    return tracker.pop_event()

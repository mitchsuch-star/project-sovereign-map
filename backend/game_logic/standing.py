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
    sources and battle writes, flipped up by the user's word at AU-4 ("Flip,
    flat grip", November 6, 2026; arm AUC holds them down).

Nothing moves by waiting (§5.1): every move sits on an event. No per-turn
rule here scans the regions (Golden Rule 8).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

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


def sources_armed() -> bool:
    """Arm AUS (AU-2b, §5.5): the lumps — the Te Deum, the Bulletin, the Return,
    the honour's payback, the ceremonies' op and the Show's Acts (`since:
    "AU-2b"`); down, the tree reads as before AU-2b."""
    return True


def letters_armed() -> bool:
    """Arm AUL (AU-2c, §5.4): the Bank's Panic and the Pope's Refusal — two
    affairs templates authored `since: "AU-2c"`, held WHOLE out of the deck
    (`moments.affairs_deck`) while this reads False. ARMED by the user's word
    at AU-2c's review ("Arm both", November 5, 2026 — RE's rule kept: both
    premises measured before the flip, §6.4.3); down, the deck reads as
    before AU-2c (arm AUL)."""
    return True


def buys_armed() -> bool:
    """Arm AUY (AU-3a, §5.3): the buys — the Decree on the three Edict letters
    (their `decree` answer, `since: "AU-3a"`), the Word on an objection (both
    roads), Honour him and By Decree on the marshals' cards; down, the tree
    reads as AU-2c's. The courts' Decree rides `courts_move()` with the
    courts' other writes (AU-14 — flipped up at AU-4)."""
    return True


def offices_armed() -> bool:
    """Arm AUO (AU-3b, §5.3): the crowns and offices bought in authority —
    "Endow them" on the Fontainebleau card and the Titles of the
    Confederation (the Princes' Dotations Act paid in titles, `act_titles`);
    down, the tree reads as AU-3a's."""
    return True


def proclamation_armed() -> bool:
    """Arm AUR (AU-3b, §5.3): the Proclamation — a fourth Edict letter priced
    in authority on the eve of battle, authored `since: "AU-3b"`. ARMED by the
    user's word at AU-3b's review ("Arm it", November 5, 2026 — RE's rule
    kept: re-premised by "Re-premise it first" and measured before the flip,
    §6.6.5); down, the deck reads as before the Proclamation (arm AUR)."""
    return True


def courts_move() -> bool:
    """Arm AUC (§5.7, AU-4): the courts' sources and battle writes — their
    fields, garrisons and charges (`courts_battle`, `courts_garrison`), their
    Te Deum and Bulletin, their Decree in authority (AU-14) — FLIPPED UP by
    the user's word at AU-4's review ("Flip, flat grip", November 6, 2026; the
    RE-6 pattern: built and measured parked at AU-4 part 1, §6.7, then flipped
    in its own commit with its re-measure, §6.8); down, the courts as AU-4
    part 1 left them (arm AUC)."""
    return True


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
           party: str = "", ceiling: int = CEILING, **fmt) -> int:
    """A lump of regrowth (the Te Deum, the Bulletin, the Return — AU-2b's
    callers): +amount up to `ceiling` (CEILING, or an Act's own `ceiling` —
    never above it), once per `every` turns per `key` (the cooldown kept in
    the tracker's `held`). Returns what was applied. A court's regrowth
    rides `courts_move()` (arm AUC)."""
    amount = abs(int(amount))
    if not amount:
        return 0
    tracker = tracker_of(world, lord)
    if tracker is None and not courts_move():
        return 0
    held = _cooldown_store(world)
    slot = _cooldown_key(world, lord, key)
    turn = int(getattr(world, "current_turn", 0) or 0)
    if every and isinstance(held, dict):
        last = held.get(slot)
        if last is not None and turn - int(last) < int(every):
            return 0
    room = min(int(ceiling), CEILING) - standing_of(world, lord)
    if room <= 0:
        return 0
    applied = move(world, lord, min(amount, room), cause, party, **fmt)
    if applied and isinstance(held, dict):
        held[slot] = turn
    return applied


def _cooldown_store(world) -> Optional[Dict[str, Any]]:
    """AU-4: the lumps' cooldowns live in the player's tracker's `held` — the
    player's keys as AU-2b wrote them, a court's under its own name — so a
    court's Te Deum keeps its twelve turns and its Bulletin its three without
    a new field on the world (`WorldState.to_dict` keeps its size)."""
    tracker = getattr(world, "authority_tracker", None)
    held = getattr(tracker, "held", None) if tracker is not None else None
    return held if isinstance(held, dict) else None


def _cooldown_key(world, lord: str, key: str) -> str:
    """`last:<key>` for the player (AU-2b's keys, unchanged); `last:<court>|<key>` for a court."""
    if not lord or is_player(world, lord):
        return f"last:{key}"
    return f"last:{lord}|{key}"


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


def breach_quote(world, lord: str) -> str:
    """§5.4: the first strike's quote ("Authority 100 → 97 — …"), the one
    every choice that breaks a treaty reads; "" while the breach is held down
    (arm AUW)."""
    if not breach_armed():
        return ""
    return quote(world, lord, -BREACH_STRIKE)["line"]


def breach_confirm_clause(world, lord: str) -> str:
    """§5.4: the word broken, priced on a breach's confirm — the war
    declaration's and, since AU-8, the manual break's."""
    line = breach_quote(world, lord)
    return " And the court keeps its own count: " + line if line else ""


def breach_paradox_clause(world, lord: str) -> str:
    """AU-8 (BUG_FIXES.md §AU): the alliance paradox breaks a treaty on either
    answer (the war on the attacker, or the defender's alliance set aside), so
    its message carries the one quote once."""
    line = breach_quote(world, lord)
    return "\n\nEither way, the court keeps its own count: " + line if line else ""


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


# ─────────────────────────────── the lumps (AU-2b) ───────────────────────────────
# §5.5: standing comes back by play, never by waiting — each lump through
# `regrow` (the ceiling 95, a keyed cooldown), a court's behind `courts_move()` (AU-4).

TE_DEUM_SCORE = 25        # a war ENDED with the lord's war score at +25 or better …
TE_DEUM_AMOUNT = 4        # … sings a Te Deum: +4, …
TE_DEUM_EVERY = 12        # … once per twelve turns per lord (a three-pair settlement pays once)
BULLETIN_AMOUNT = 4       # a laurel victory is read in every church: +4, …
BULLETIN_EVERY = 3        # … one bulletin per three turns, …
BULLETIN_WINDOW = 10      # … and the field's dents of the last ten turns …
BULLETIN_REPAY_MAX = 8    # … repaid +1 a point up to +8, each point once, never a price
LAUREL_RATIO = 2          # a laurel: France's dead at most half the enemy's (a flawless win counts)
RETURN_AFIELD = 8         # the Return: back on his own seat after eight turns away …
RETURN_MAX = 5            # … repays the Council's dents, up to 5
HONOUR_WINDOW = 8         # the honour pays back when the man honoured wins within eight turns …
HONOUR_REPAID = 2         # … +2, once per honour (the mark is AU-3a's to write)
# §4.1 reading 5: the field's dents — the defeats, the failed mediations, the
# stakes — and never a price (a letter, a law, a claim, a breach, an Act)
FIELD_DENT_KEYS = ("field_lost", "capital_lost", "own_hand_lost", "assault_repulsed",
                   "mediation_ignored", "reconciliation_failed", "insisted_lost", "compromise_lost",
                   "word_lost")
COUNCIL_LETTER = "chancellors_letters"   # the Council's dents: the Arch-Chancellor's Declines


def te_deum_on_peace(world, diplo_key: str) -> int:
    """§5.5 the Te Deum, read by `diplomacy.cleanup_war_end` when a war ENDS
    (never a truce), before the pair's war score is popped: the player's stored
    war score (`diplomacy.get_war_score_for`) at TE_DEUM_SCORE or better sings
    one — +TE_DEUM_AMOUNT through `regrow`, once per TE_DEUM_EVERY turns per
    lord — and Le Moniteur prints it (the campaign log's `te_deum`). A level
    peace sings nothing; a court's Te Deum rides `courts_move()`. Returns what was applied."""
    if not sources_armed():
        return 0
    parts = str(diplo_key or "").split("|")
    if len(parts) != 2:
        return 0
    from backend.game_logic.diplomacy import get_war_score_for
    applied = 0
    for lord, court in ((parts[0], parts[1]), (parts[1], parts[0])):
        if not is_player(world, lord) and not courts_move():
            continue
        score = int(get_war_score_for(world, lord, court))
        if score < TE_DEUM_SCORE:
            continue
        got = regrow(world, lord, TE_DEUM_AMOUNT, "te_deum", "te_deum", every=TE_DEUM_EVERY,
                     party=court, court=court)
        if got and hasattr(world, "log_event"):
            world.log_event({"type": "te_deum", "nation": lord, "court": court,
                             "war_score": score, "authority": int(got)})
        applied += got
    return applied


def laurel_victory(ours: int, theirs: int) -> bool:
    """§4.1 reading 5: a laurel victory — an engagement `jealousy.is_laurel`
    calls a battle (its size), in which France out-bled the enemy two to one
    (a flawless win counts). Never a garrison or a bombardment: the callers
    are the field's own (battle step 12, the auto-charge mirror)."""
    from backend.game_logic.jealousy import is_laurel
    ours, theirs = max(0, int(ours or 0)), max(0, int(theirs or 0))
    if not is_laurel(ours, theirs):
        return False
    return ours == 0 or theirs >= LAUREL_RATIO * ours


def bulletin(world, lord: str, battle: str, ours: int, theirs: int) -> Tuple[int, int]:
    """§5.5 the Bulletin of the Field: a laurel victory is read in every church
    — +BULLETIN_AMOUNT through `regrow`, one per BULLETIN_EVERY turns — and
    repays the field's dents of the last BULLETIN_WINDOW turns (`FIELD_DENT_KEYS`
    in the ring, oldest first), +1 a point up to BULLETIN_REPAY_MAX, each point
    once (`held["bulletin_paid"]`, {seq: points}), never a price. Nothing at
    the ceiling, nothing inside the cooldown. Returns (the bulletin, the repaid)."""
    if not sources_armed() or not laurel_victory(ours, theirs):
        return 0, 0
    tracker = tracker_of(world, lord) if is_player(world, lord) else None
    if tracker is None:
        if not lord or is_player(world, lord) or not courts_move():
            return 0, 0                  # a court's Bulletin rides the courts' flip (AU-4, arm AUC)
        # AU-4: a court's Bulletin is the base alone — it keeps no ring, so no
        # dent of the field's to repay (§6.7 reading 3)
        return regrow(world, lord, BULLETIN_AMOUNT, "bulletin", "bulletin", every=BULLETIN_EVERY,
                      battle=str(battle or "")), 0
    battle = str(battle or "")
    base = regrow(world, lord, BULLETIN_AMOUNT, "bulletin", "bulletin", every=BULLETIN_EVERY, battle=battle)
    if not base:
        return 0, 0
    turn = int(getattr(world, "current_turn", 0) or 0)
    ring = list(getattr(tracker, "moves", None) or [])
    seqs = {str(int(m.get("seq", 0) or 0)) for m in ring}
    paid = {k: int(v) for k, v in dict(tracker.held.get("bulletin_paid") or {}).items() if k in seqs}
    owed = []
    for m in ring:
        delta = int(m.get("delta", 0) or 0)
        if str(m.get("key") or "") not in FIELD_DENT_KEYS or delta >= 0:
            continue
        if turn - int(m.get("turn", 0) or 0) >= BULLETIN_WINDOW:
            continue
        seq = str(int(m.get("seq", 0) or 0))
        left = -delta - paid.get(seq, 0)
        if left > 0:
            owed.append((seq, left))
    want = min(BULLETIN_REPAY_MAX, sum(left for _seq, left in owed))
    repaid = regrow(world, lord, want, "bulletin_repaid", "bulletin_repaid", battle=battle) if want else 0
    budget = repaid
    for seq, left in owed:
        if budget <= 0:
            break
        take = min(left, budget)
        paid[seq] = paid.get(seq, 0) + take
        budget -= take
    if paid:
        tracker.held["bulletin_paid"] = paid
    else:
        tracker.held.pop("bulletin_paid", None)
    return base, repaid


def bulletin_line(base: int, repaid: int, battle: str) -> str:
    """The Bulletin's line on the battle report (the throne's channel,
    `pipeline_out['sovereign_prestige_msg']`); "" when none was issued."""
    if not base:
        return ""
    where = f"The field at {battle}" if battle else "The field"
    tail = f", and +{int(repaid)} of the field's dents repaid" if repaid else ""
    return (f"\n\n[The Bulletin of the Grande Armée] {where} is read in every church in "
            f"France. (Authority +{int(base)}{tail})")


# ─────────────────────────────── AU-4 the courts' field ───────────────────────────────

FIELD_WON = 5             # a field won against the odds, or a capital taken (AU-1's battle writes)
OWN_HAND_WON = 2          # … +2 when the sovereign led it in person (NP-2)
FIELD_LOST = 5            # a field lost with the numbers, or a capital lost by its defender (AU-19)
OWN_HAND_LOST = 5         # … −5 when the sovereign led it in person
GARRISON_STORMED = 5      # a garrison stormed against the odds; a capital stormed; …
ASSAULT_REPULSED = 5      # … an assault repulsed with the numbers


def capital_lost_by(world, lord: str, region_name: str, defender: bool, conquered: bool) -> bool:
    """AU-19 (BUG_FIXES.md §AU): a lost battle is a capital lost only for its
    defender, when the capital falls in it — a lost assault on a capital, or a
    lost field at one that holds, is a field (−5 only when the loser
    outnumbered). A named function, read by the player's battle step and the
    courts' field alike, so the front page's replay and the rig's arm AUF can
    hold the old rule down (a lost battle at any capital the lord did not
    control — 248 bookings on the measured runs, most of them its satellites')."""
    region = world.get_region(region_name) if hasattr(world, "get_region") else None
    return bool(defender and conquered and region is not None and getattr(region, "is_capital", False))


def courts_battle(world, battle: str, attacker_nation: str, defender_nation: str,
                  attacker_won: bool, defender_won: bool, pre_atk: int, pre_def: int,
                  conquered: bool = False, atk_lead=None, def_lead=None,
                  atk_cas: int = 0, def_cas: int = 0, lost_capitals: bool = True) -> int:
    """AU-4 (§5.7, the gate's Q6 "same rules"): a field's writes for each COURT
    in it — AI against AI included, the player's side never touched — the
    player's own rules: won, +5 when outnumbered or a capital taken, +2 under
    the sovereign's own hand, and the Bulletin on a laurel; lost, −5 when
    outnumbering or a capital lost by its defender (AU-19), −5 under the
    sovereign's own hand. `lost_capitals` False for the auto-charge mirror,
    whose player arm books no capital lost (each site's own rules). Behind
    `courts_move()` (arm AUC). Returns the total moved."""
    if not courts_move():
        return 0
    region = world.get_region(battle) if hasattr(world, "get_region") else None
    is_capital = bool(region is not None and getattr(region, "is_capital", False))
    moved = 0
    for side, lord, won, lost, ours, theirs, lead, own_cas, their_cas in (
            ("attacker", attacker_nation, attacker_won, defender_won, pre_atk, pre_def, atk_lead, atk_cas, def_cas),
            ("defender", defender_nation, defender_won, attacker_won, pre_def, pre_atk, def_lead, def_cas, atk_cas)):
        if not lord or is_player(world, lord):
            continue
        led = bool(lead is not None and getattr(lead, "is_sovereign", False)
                   and getattr(lead, "name", None) in (getattr(world, "marshals", {}) or {}))
        if won:
            taken = bool(side == "attacker" and conquered and is_capital)
            if int(ours or 0) < int(theirs or 0) or taken:
                moved += move(world, lord, FIELD_WON, "capital_taken" if taken else "field_won", battle=battle)
            if led:
                moved += move(world, lord, OWN_HAND_WON, "own_hand_won", battle=battle)
            moved += bulletin(world, lord, battle, int(own_cas or 0), int(their_cas or 0))[0]
        elif lost:
            fallen = bool(lost_capitals) and capital_lost_by(world, lord, battle, side == "defender", bool(conquered))
            if int(ours or 0) > int(theirs or 0) or fallen:
                moved += move(world, lord, -FIELD_LOST, "capital_lost" if fallen else "field_lost", battle=battle)
            if led:
                moved += move(world, lord, -OWN_HAND_LOST, "own_hand_lost", battle=battle)
    return moved


def courts_garrison(world, lord: str, region, pre_atk: int, garrison_effective: int, stormed: bool) -> int:
    """AU-4: a court's assault on a garrison, the attacker's side as the
    player's — stormed against the odds +5, a capital stormed +5; repulsed
    with the numbers −5. Behind `courts_move()` (arm AUC); the player's own
    writes stay in the garrison path. Returns the total moved."""
    if not courts_move() or not lord or is_player(world, lord):
        return 0
    name = str(getattr(region, "name", region) or "")
    moved = 0
    if stormed:
        if int(pre_atk or 0) < int(garrison_effective or 0):
            moved += move(world, lord, GARRISON_STORMED, "garrison_stormed", region=name)
        if getattr(region, "is_capital", False):
            moved += move(world, lord, GARRISON_STORMED, "capital_stormed", region=name)
    elif int(pre_atk or 0) > int(garrison_effective or 0):
        moved += move(world, lord, -ASSAULT_REPULSED, "assault_repulsed", region=name)
    return moved


def council_dent(world, lord: str, loss: int) -> None:
    """The Arch-Chancellor's Decline booked as the Council's dent
    (`held["council_owed"]`) — what the Return repays. A tally, not a ring
    scan: the ring keeps 24 moves, and eight turns of war can push it out."""
    if not sources_armed() or int(loss or 0) <= 0:
        return
    tracker = tracker_of(world, lord) if is_player(world, lord) else None
    if tracker is not None:
        tracker.held["council_owed"] = int(tracker.held.get("council_owed", 0) or 0) + int(loss)


def the_return(world, lord: str) -> int:
    """§5.5 the Return, read each morning: the lord's sovereign away from his
    own held capital (`diplomacy.sovereign_seat_bonus` 0) starts the clock
    (`held["away_since"]`); back on the seat after RETURN_AFIELD turns or more,
    the Council's dents (`held["council_owed"]`) are repaid, up to RETURN_MAX,
    through `regrow`; a short trip repays nothing. Returns what was applied."""
    if not sources_armed():
        return 0
    tracker = tracker_of(world, lord) if is_player(world, lord) else None
    if tracker is None:
        return 0
    from backend.game_logic.diplomacy import sovereign_seat_bonus
    turn = int(getattr(world, "current_turn", 0) or 0)
    held = tracker.held
    if not sovereign_seat_bonus(world, lord):
        held.setdefault("away_since", turn)
        return 0
    since = held.pop("away_since", None)
    owed = int(held.get("council_owed", 0) or 0)
    if since is None or turn - int(since) < RETURN_AFIELD or owed <= 0:
        return 0
    from backend.game_logic.affairs import seat_of
    applied = regrow(world, lord, min(RETURN_MAX, owed), "return", "return",
                     party="Cambacérès", capital=seat_of(world, lord))
    if applied:
        left = owed - applied
        if left > 0:
            held["council_owed"] = left
        else:
            held.pop("council_owed", None)
    return applied


def honour_repaid(world, lord: str, marshal: str) -> int:
    """§5.5 the honour pays back: the man honoured (AU-3a's mark,
    `held["honoured:<marshal>"]` = the turn of the honour) wins within
    HONOUR_WINDOW turns — +HONOUR_REPAID through `regrow`, once per honour (the
    mark popped; an expired mark popped unpaid). Inert until AU-3a writes it."""
    if not sources_armed() or not marshal:
        return 0
    tracker = tracker_of(world, lord) if is_player(world, lord) else None
    if tracker is None:
        return 0
    mark = tracker.held.pop(f"honoured:{marshal}", None)
    if mark is None:
        return 0
    if int(getattr(world, "current_turn", 0) or 0) - int(mark) > HONOUR_WINDOW:
        return 0
    return regrow(world, lord, HONOUR_REPAID, "honour_repaid", f"honour:{marshal}",
                  party=str(marshal), marshal=str(marshal))


# ─────────────────────────────── the buys (AU-3a) ───────────────────────────────
# §5.3: authority the Emperor spends on purpose — the Decree on the Edict
# letters, the Word on an objection, the honour and the decree on the
# marshals' cards. One price rule: a price lands whole or its button is closed
# with the reason (`refusal`, the grip's 60); each buy raises the next by one
# for the turn and the five after it, at most three (the recency rise).

PUSH_WINDOW = 6           # the recency rise: the buys of this turn and the five before it …
PUSH_RISE_MAX = 3         # … each +1 on the next price, at most +3
WORD_PRICES = {"DEVOTED": 2, "TRUSTING": 3, "WARY": 4, "HOSTILE": 5}   # by the marshal's trust tier
WORD_WINDOW = 3           # a field lost within three turns of the word given …
WORD_LOSS_TRUST = -5      # … costs his trust −5 …
WORD_LOSS_AUTHORITY = -3  # … and authority −3; won, nothing (never the insistence's +5)
HONOUR_PRICE = 4          # Honour him: his grievance ends, trust +2 …
HONOUR_TRUST = 2          # … and the colleague passed over loses as much
PAIR_DECREE_PRICE = 5     # By decree: the quarrelling pair rises a rung with no roll


def _push_turns(world, lord: str) -> List[int]:
    tracker = tracker_of(world, lord) if is_player(world, lord) else None
    held = getattr(tracker, "held", None) if tracker is not None else None
    if not isinstance(held, dict):
        return []
    turn = int(getattr(world, "current_turn", 0) or 0)
    return [int(t) for t in (held.get("pushes") or []) if 0 <= turn - int(t) < PUSH_WINDOW]


def push_price(world, lord: str, base: int) -> int:
    """A buy's price: its base plus one per buy of this turn and the five before
    it, at most PUSH_RISE_MAX (a court keeps no such count)."""
    return int(base) + min(PUSH_RISE_MAX, len(_push_turns(world, lord)))


def offer(world, lord: str, base: int) -> Dict[str, Any]:
    """What a buy's button shows: {price, before, after, line, refusal} — the
    quote at the recency price; `buy` reads the same price (shown = applied)."""
    price = push_price(world, lord, base)
    q = quote(world, lord, -price)
    return {"price": int(price), "before": int(q["before"]), "after": int(q["after"]),
            "line": q["line"], "refusal": q["refusal"]}


def buy(world, lord: str, base: int, cause: str, party: str = "", **fmt) -> Dict[str, Any]:
    """A buy: the recency price spent whole (`spend`: the quote, then the
    move) — or refused with nothing applied; a buy that lands books its turn,
    raising the next one's price."""
    price = push_price(world, lord, base)
    out = spend(world, lord, price, cause, party, **fmt)
    out["price"] = int(price)
    tracker = tracker_of(world, lord) if is_player(world, lord) else None
    if not out.get("refusal") and tracker is not None:
        tracker.held["pushes"] = _push_turns(world, lord) + [int(getattr(world, "current_turn", 0) or 0)]
    return out


def word_base(marshal) -> int:
    """The Word's base price by the objecting marshal's trust tier — a third
    of the insistence's trust penalty it replaces (§4.1 reading 2)."""
    from backend.commands.objection_v2 import get_trust_tier
    trust = getattr(marshal, "trust", None)
    value = int(getattr(trust, "value", trust if isinstance(trust, int) else 70) or 0)
    return int(WORD_PRICES.get(get_trust_tier(value).name, WORD_PRICES["TRUSTING"]))


def word_stake_line() -> str:
    """What the Word risks, in figures, beside the insistence's own stake line."""
    return (f"By your word: no trust or defiance; lost within {WORD_WINDOW} turns, trust "
            f"{_signed(WORD_LOSS_TRUST)} and authority {_signed(WORD_LOSS_AUTHORITY)}.")


def word_offer(world, marshal) -> Dict[str, Any]:
    """The Word on an objection's payload: {price, before, after, line,
    refusal, stake}; {} while the buys are held down (arm AUY)."""
    if not buys_armed() or marshal is None:
        return {}
    lord = str(getattr(world, "player_nation", "") or "")
    out = offer(world, lord, word_base(marshal))
    out["stake"] = word_stake_line()
    return out


def pop_event(world) -> Optional[Dict[str, Any]]:
    """The threshold box the next response carries (read, then cleared —
    Golden Rule 4); None when no line was crossed since the last response."""
    tracker = getattr(world, "authority_tracker", None)
    if tracker is None or not hasattr(tracker, "pop_event"):
        return None
    return tracker.pop_event()

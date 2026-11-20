"""Row IC, the second commit (IC-4) — THE DIRECTIVE: one order to several
marshals, shown as ONE list first and sent on one confirmation (November 19,
2026; `docs/SYSTEMS_REFERENCE.md` §230).

The user's ruling in Plan Mode: "One list for all" — a collective line
("Everyone, on Vienna"), a list of names ("Ney, Lannes and Murat, march to
Ulm"), a named army ("Army of Italy, hold") or a Ctrl-selected group is shown
as a list — each man's order, its price, whether he may object — before
anything is spent, and goes as one order and one Take-back unit.

THE LIST IS THE TRUTH
=====================
* `address` reads WHO a line is for from its own words — never from "no
  marshal was named" (a list's parse names its first man).
* `quote` is the list: one row a marshal. Each row is the reading
  `/parse_preview` gives that man's own line (`parse_preview.read_one` — one
  reader), so the list, the read-back and the price check cannot drift. Nothing
  is written and no die is cast.
* `give` carries the ticked rows out through the collective's own fan-out
  (`group_orders._run_members`: each line the ordinary parser and executor —
  Rule 5). The list is drawn afresh first: a ticked man who can no longer go,
  or a total that differs from the one the player saw, refuses the order and
  returns the fresh list. A man charged MORE than his row said puts the whole
  board back (`group_orders.Overcharge`).

The address kinds: ``everyone`` (the collective words), ``at`` (the corps at a
province), ``list`` (names) and ``army`` (a saved army). A group selected on
the map travels as a list with `click`: each man's order is the one his own
click would send (a move where the plain move takes it — row PW's rule).

`a_named_list_is_one_directive` is the seam: down, a list of names rides the
relay as it did (first man, the rest handed back).
"""
from __future__ import annotations

import random
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.display_names import humanize_entity_name
from backend.errors import report


def a_named_list_is_one_directive() -> bool:
    """The seam (row IC, ruling 1). One line to reverse: return False."""
    return True


# ── who the line is for ─────────────────────────────────────────────────────

def address(world, text: str) -> Optional[Dict[str, Any]]:
    """Who `text` addresses, read from its own words: ``{"kind", "names",
    "rest", …}`` — or None when it is an order to one man, or to nobody.

      army      {"army": <saved name>, "names": its men ours to order}
      list      {"names": the marshals of ours it names, in order}
      everyone  the collective words;  at  {"at": <province>}

    `rest` is the order's own words. PURE; an army's name is tried first (the
    bare word "army" already means every corps)."""
    text = str(text or "")
    if world is None or not text.strip():
        return None
    try:
        from backend.game_logic import armies
        hit = armies.address_of(world, text)
        if hit is not None:
            return {"kind": "army", "army": hit["army"], "rest": hit["rest"],
                    "names": armies.members(world, hit["army"])}
        if armies.read_order(world, text) is not None:
            # The army's own verbs ("Army of Italy, disband", "form the Army of …")
            # are the staff's bookkeeping, never an order to several — though
            # "army" alone is the collective word (the review).
            return None
        if a_named_list_is_one_directive():
            from backend.commands.parser import _split_collective_address, _split_second_name
            second = _split_second_name(text, {"world": world})
            if second and second.get("kind") == "address":
                names = [second["first"], second["second"]] + list(second.get("others") or [])
                first_text = str(second.get("first_text") or "")
                rest = first_text[len(str(second["first"])) + 1:].strip()
                if rest:
                    return {"kind": "list", "names": names, "rest": rest}
            # "Lannes and Murat, both of you move to Rhineland" / "Ney, Davout,
            # Soult: everyone converge on Swabia" — a list closed by a
            # collective word, the parser's own reading of it (the first man's
            # line, the others' behind a colon).
            both = _split_collective_address(text, {"world": world})
            if both:
                first_line, tail = both
                lead, _, rest = str(first_line).partition(", ")
                others = [n.strip() for n in str(tail).partition(":")[0].split(",") if n.strip()]
                if lead and others and rest.strip():
                    return {"kind": "list", "names": [lead] + others, "rest": rest.strip()}
        from backend.commands import group_orders as G
        head = G.collective_head(text, places=list(getattr(world, "regions", {}) or {}))
        if head is not None:
            return {"kind": "at" if head.get("at") else "everyone", "names": [],
                    "rest": str(head.get("rest") or ""), "at": str(head.get("at") or "")}
        if G.is_collective_cancel(text):
            return {"kind": "everyone", "names": [], "rest": "cancel", "at": ""}
    except Exception as exc:
        report(exc, "directive.address")
    return None


def _names(shown: List[str]) -> str:
    shown = [s for s in shown if s]
    if not shown:
        return ""
    if len(shown) == 1:
        return shown[0]
    return ", ".join(shown[:-1]) + " and " + shown[-1]


def _who(world, stash: Dict[str, Any]) -> str:
    """Who the order goes to, as the card's title and the read-back say it."""
    kind = stash.get("kind")
    if kind == "army" and stash.get("army_name"):
        return f"The {stash['army_name']}"
    if kind == "list":
        return _names([humanize_entity_name(n) for n in (stash.get("who") or [])])
    if kind == "at" and stash.get("at"):
        return f"The corps at {humanize_entity_name(stash['at'])}"
    return "Every corps"


def canonical_line(stash: Dict[str, Any]) -> str:
    """The line the client sends back with its ticks: the same address in
    words the built-in reader takes whole ("Ney, Lannes and Murat, march to
    Ulm"), so the second send never needs free wording read again."""
    rest = str(stash.get("rest") or "")
    kind = stash.get("kind")
    if kind == "army" and stash.get("army_name"):
        return f"{stash['army_name']}, {rest}"
    if kind == "list":
        return f"{_names([str(n) for n in (stash.get('who') or [])])}, {rest}"
    if stash.get("cancel"):
        return "everyone, cancel"
    if kind == "at" and stash.get("at"):
        return f"everyone at {stash['at']}, {rest}"
    return f"everyone, {rest}"


# ── the list ────────────────────────────────────────────────────────────────

_RIDERS = ("contact", "camp", "departs", "march_cost", "detour", "pay", "guard", "front", "terms")


def _row_from_reading(name: str, line: str, reading: Dict[str, Any]) -> Dict[str, Any]:
    """One row of the list from the read-back's own reading of that man's line."""
    shown = humanize_entity_name(name)
    row: Dict[str, Any] = {
        "marshal": name, "shown": shown, "line": line, "says": "", "ok": False,
        "ap": 0, "turns": 0, "objection": "none", "replaces": "", "notes": [],
        "why": "", "ticked": False, "covered": False,
    }
    parts = [p for p in (reading.get("parts") or []) if isinstance(p, dict)]
    head = next((str(p.get("text") or "") for p in parts if p.get("role") == "head"), "")
    if reading.get("kind") == "order" and reading.get("ok"):
        says = head
        for lead in (shown + " · ", shown + " "):
            if says.startswith(lead):
                says = says[len(lead):]
                break
        row.update(ok=True, says=says, ap=int(reading.get("ap", 0) or 0),
                   turns=int(reading.get("turns", 0) or 0),
                   objection="possible" if reading.get("objection") == "possible" else "none",
                   replaces=str(reading.get("replaces") or ""))
        notes = [str(p.get("text") or "") for p in parts
                 if p.get("role") in ("warn", "note") and str(p.get("text") or "")
                 and str(p.get("text")) != "he may object"
                 and not str(p.get("text")).startswith("replaces ")]
        # Row IC, Session 2 (IC-8): what his line TOOK (a condition, an
        # if-then) and what it did NOT take, as the read-back says them.
        notes += [str(p.get("text") or "") for p in parts
                  if p.get("role") == "taken" and str(p.get("text") or "")]
        notes += ["not taken: " + str(p.get("text") or "") for p in parts
                  if p.get("role") == "nottaken" and str(p.get("text") or "")]
        quote = reading.get("_quote")
        if isinstance(quote, dict):
            for key in _RIDERS:
                text = str(quote.get(key) or "").strip()
                if text and text not in notes:
                    notes.append(text)
        row["notes"] = notes
        return row
    why = str(reading.get("refusal") or "")
    if not why:
        why = next((str(p.get("text") or "") for p in parts if p.get("role") in ("bad", "head")), "")
    row["why"] = _plain_why(shown, why) or "the order cannot be given to him"
    return row


def _plain_why(shown: str, why: str) -> str:
    """A refusal as a row says it: the man's own name off its head (the row
    names him already) and "nothing spent" off its tail (the list spends
    nothing by its nature)."""
    why = str(why or "").strip()
    for _twice in range(2):     # "Soult — Soult already stands at …"
        for lead in (shown + " — ", shown + " - ", shown + ": ", shown + " "):
            if why.startswith(lead):
                why = why[len(lead):]
                break
    why = re.sub(r"\s*[—-]\s*nothing (?:was )?spent\.?$", "", why, flags=re.IGNORECASE)
    why = re.sub(r"\s*Nothing (?:was )?spent\.?$", "", why)
    return why.strip().rstrip(".")


_RECALLED = {"march": "his march", "pursue": "his pursuit", "hold": "his hold",
             "support": "his support", "follow": "his following"}


def _row_for_recall(world, name: str, marshal, line: str) -> Dict[str, Any]:
    """One row of "everyone stop": what the recall costs THIS man — the
    cancel's own price and the trust it costs him, read where the arrow's card
    reads them (`strategic.standing_order_road`) — or that he has no order to
    recall (the executor then only says he awaits orders, free)."""
    row = _row_from_reading(name, line, {})
    if getattr(marshal, "strategic_order", None) is None:
        row["why"] = "has no standing order to recall"
        return row
    info: Dict[str, Any] = {}
    try:
        from backend.commands.strategic import standing_order_road
        info = standing_order_road(world, marshal) or {}
    except Exception as exc:
        report(exc, "directive._row_for_recall: strategic.standing_order_road")
    price = int(info.get("cancel_ap", world.get_action_cost("cancel")) or 0)
    have = int(getattr(world, "actions_remaining", 0) or 0)
    if price > have:
        row["why"] = ("no military action left this turn" if have <= 0
                      else f"needs {price} action{'s' if price != 1 else ''} — {have} left")
        return row
    trust = int(info.get("cancel_trust", 0) or 0)
    what = _RECALLED.get(str(info.get("kind") or ""), "his standing order")
    row.update(ok=True, ap=price, why="", says=f"recall {what}",
               notes=([f"Costs him {-trust} trust — he is already on the road."] if trust < 0
                      else ["No trust lost — the order was given this turn."]))
    return row


def _row_from_click(name: str, quote: Dict[str, Any]) -> Dict[str, Any]:
    """One row from the click road's own quote (`order_quotes.march_quote(
    click=True)`): the move where the plain move takes it, else the march."""
    shown = humanize_entity_name(name)
    command = str(quote.get("command") or "")
    cut = command.find(", ")
    says = command[cut + 2:] if cut >= 0 else command
    kind = str(quote.get("kind") or "")
    turns = int(quote.get("turns", 0) or 0)
    if kind == "move":
        says += " — arrives now"
    row: Dict[str, Any] = {
        "marshal": name, "shown": shown, "line": command, "says": says, "ok": True,
        "ap": int(quote.get("ap", 0) or 0), "turns": turns,
        "objection": "possible" if quote.get("objection") == "possible" else "none",
        "replaces": str(quote.get("replaces") or ""), "notes": [],
        "why": "", "ticked": False, "covered": False,
    }
    ground = quote.get("ground") if isinstance(quote.get("ground"), dict) else {}
    said = str(ground.get("line") or "").strip()
    if said and ground.get("takes") is not True:
        row["notes"].append(said[:1].upper() + said[1:] + ".")
    for key in _RIDERS + ("note",):
        text = str(quote.get(key) or "").strip()
        if text and text not in row["notes"]:
            row["notes"].append(text)
    return row


def _staff_view(world, stash: Dict[str, Any], rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The Staff's single order, when the collective rides it: who it covers
    (the column the gate chose, less the men its own run would leave out or
    whose own order would be refused) and its one price — or None (no Staff
    order today)."""
    if not stash.get("army"):
        return None
    from backend.commands import group_orders as G
    from backend.commands.state_probe import VERBS, order_state_refusal
    verb = G._probe_verb(stash["action"], stash.get("strategic_type"), stash["rest"])
    can_go = {r["marshal"] for r in rows if r.get("ok")}
    covers: List[str] = []
    doubts: List[str] = []
    for name in stash.get("members") or []:
        marshal = world.get_marshal(name)
        if marshal is None or int(getattr(marshal, "strength", 0) or 0) <= 0:
            continue
        if name not in can_go:
            continue
        if verb in VERBS and order_state_refusal(world, marshal, verb):
            continue
        doubt = G._would_object(world, marshal, stash.get("strategic_type"),
                                parsed_target=stash.get("target"), rest=stash["rest"])
        if doubt and stash.get("band") == "heard":
            continue      # he refuses the Staff's word and answers in person
        if doubt:
            doubts.append(name)
        covers.append(name)
    if not covers:
        return None
    return {"ap": int(G.ARMY_ORDER_AP), "covers": covers, "carried": doubts,
            "reach": int(G.ARMY_COLUMN_REACH), "note": str(stash.get("note") or "")}


def _quote_locked(world, stash: Dict[str, Any], readers: Dict[str, Any]) -> Dict[str, Any]:
    """The list of `stash` (the caller holds `parse_preview.reading()`)."""
    from backend.commands import group_orders as G
    from backend.commands import parse_preview as pp
    rest = str(stash.get("rest") or "")
    strategic_type = stash.get("strategic_type")
    addressed = [str(n) for n in (stash.get("addressed") or stash.get("members") or [])]
    have = int(getattr(world, "actions_remaining", 0) or 0)
    rows: List[Dict[str, Any]] = []
    memo: dict = {}
    for name in addressed:
        marshal = world.get_marshal(name)
        line = f"{name}, {rest}"
        if (marshal is None or int(getattr(marshal, "strength", 0) or 0) <= 0
                or getattr(marshal, "captured_by", "")):
            row = _row_from_reading(name, line, {})
            row["why"] = "not in the field"
            rows.append(row)
            continue
        row = None
        if stash.get("cancel"):
            rows.append(_row_for_recall(world, name, marshal, line))
            continue
        if stash.get("click") and strategic_type == "MOVE_TO" and stash.get("target") \
                and world.get_region(str(stash["target"])) is not None:
            try:
                from backend.commands import order_quotes as Q
                cq = Q.march_quote(world, marshal, str(stash["target"]), memo=memo, click=True)
            except Exception as exc:
                report(exc, "directive._quote_locked: order_quotes.march_quote")
                cq = None
            if isinstance(cq, dict) and cq.get("ok") and not cq.get("already") and cq.get("command"):
                row = _row_from_click(name, cq)
        if row is None:
            try:
                reading = pp.read_one(world, line, **readers)
            except Exception as exc:
                report(exc, "directive._quote_locked: parse_preview.read_one")
                reading = {}
            row = _row_from_reading(name, line, reading)
        rows.append(row)

    staff = _staff_view(world, stash, rows)
    if staff is not None:
        covered = set(staff["covers"])
        for row in rows:
            row["covered"] = row["marshal"] in covered
            if row["covered"]:
                row["ticked"] = True
                if row["marshal"] in staff["carried"]:
                    row["notes"] = ["He has his doubts — the Staff's order carries him."] + row["notes"]
        total = int(staff["ap"])
    else:
        left = have
        total = 0
        for row in rows:
            if row["ok"] and int(row["ap"]) <= left:
                row["ticked"] = True
                left -= int(row["ap"])
                total += int(row["ap"])
    can_go = [r for r in rows if r["ok"] or r["covered"]]
    order = "recall their standing orders" if stash.get("cancel") else rest
    if stash.get("click") and strategic_type == "MOVE_TO" and stash.get("target"):
        # A group sent by a click takes each man's own click order — a move next
        # door, a march beyond — so the head says neither ("go to Lorraine"; the
        # rows say which). Pressed in the real client: "march to" stood over
        # rows that read "move to".
        order = f"go to {humanize_entity_name(str(stash['target']))}"
    out: Dict[str, Any] = {
        "kind": str(stash.get("kind") or "everyone"),
        "who": _who(world, stash),
        "army": str(stash.get("army_name") or ""),
        "order": order,
        "line": canonical_line(stash),
        "click": bool(stash.get("click")),
        "rows": rows,
        "total": int(total), "have": int(have),
        "staff": staff,
        "sendable": bool(can_go),
        "note": "",
    }
    if not can_go:
        reasons = {r["why"] for r in rows if r["why"]}
        out["note"] = (next(iter(reasons)) if len(reasons) == 1
                       else "No corps can take this order today.")
    return out


def quote(world, stash: Dict[str, Any], readers: Dict[str, Any]) -> Dict[str, Any]:
    """THE LIST of an order to several corps: ``{kind, who, order, line, rows,
    total, have, staff, sendable, …}`` — each row ``{marshal, shown, line,
    says, ok, ap, turns, objection, replaces, notes, why, ticked, covered}``.
    PURE: nothing is written and no die is cast (the readers are the
    read-back's own). `readers` are `parse_preview.read_one`'s keywords."""
    from backend.commands import parse_preview as pp
    with pp.reading():
        return _quote_locked(world, stash, readers)


def total_for(listing: Dict[str, Any], members: List[str]) -> int:
    """What giving the order to exactly `members` costs, by the list's own
    figures: the Staff's one price when its whole column and nobody else is
    ticked, else each man's own."""
    staff = listing.get("staff")
    if isinstance(staff, dict) and set(members) == set(staff.get("covers") or []):
        return int(staff.get("ap", 0) or 0)
    by_name = {r["marshal"]: r for r in (listing.get("rows") or [])}
    return int(sum(int((by_name.get(n) or {}).get("ap", 0) or 0) for n in members))


def stale(listing: Dict[str, Any], members: List[str], expect_ap: Optional[int]) -> str:
    """Why the list the player answered no longer holds — "" when it does: a
    ticked man must be a row that can go, the total must be the one he saw
    (when he said what he saw) and the actions in hand must pay it."""
    by_name = {r["marshal"]: r for r in (listing.get("rows") or [])}
    staff = listing.get("staff") if isinstance(listing.get("staff"), dict) else None
    rides_staff = staff is not None and set(members) == set(staff.get("covers") or [])
    for name in members:
        row = by_name.get(name)
        if row is None:
            return f"{humanize_entity_name(name)} is not among the men this order goes to."
        if not row.get("ok") and not (rides_staff and row.get("covered")):
            return f"{row['shown']} can no longer take this order — {row.get('why') or 'it would be refused'}."
    total = total_for(listing, members)
    if expect_ap is not None and int(expect_ap) != total:
        return (f"The price has changed since the list was drawn — it was {int(expect_ap)} "
                f"action{'s' if int(expect_ap) != 1 else ''} and is now {total}.")
    if total > int(listing.get("have", 0) or 0):
        return (f"This needs {total} action{'s' if total != 1 else ''} and "
                f"{int(listing.get('have', 0) or 0)} remain — untick a corps.")
    return ""


def narrow(stash: Dict[str, Any], listing: Dict[str, Any], members: List[str]) -> Dict[str, Any]:
    """The stash a give runs: the ticked men, in the order the list showed
    them; the Staff's order only when exactly its column is ticked (else each
    man at his own price); each man's quoted price for the charge check; and
    the men left out, with why, for the reply's rows."""
    order = [r["marshal"] for r in (listing.get("rows") or [])]
    ticked = [n for n in order if n in set(members)]
    staff = listing.get("staff") if isinstance(listing.get("staff"), dict) else None
    rides_staff = staff is not None and set(ticked) == set(staff.get("covers") or [])
    by_name = {r["marshal"]: r for r in (listing.get("rows") or [])}
    out = dict(stash)
    out["members"] = list(ticked)
    if out.get("kind") == "list":
        out["who"] = list(ticked)     # the reply's head names the men it went to
    out["lines"], out["events"] = [], []
    out["left_out"] = [(n, "not ticked") for n in order if n not in set(ticked)]
    if rides_staff:
        out["quoted"] = {n: 0 for n in ticked}     # the Staff's one price covers them
    else:
        out["army"], out["band"] = False, None
        out["note"] = ""
        out["quoted"] = {n: int((by_name.get(n) or {}).get("ap", 0) or 0) for n in ticked}
    return out


# ── the give, with its guard ────────────────────────────────────────────────

def give(world, game_state, parser, executor, llm_game_state, stash: Dict[str, Any],
         listing: Dict[str, Any], members: List[str]) -> Tuple[str, Dict[str, Any]]:
    """Carry the ticked rows out as ONE order — ``("done", result)`` — or put
    the board back as it stood when a man was charged more than his row said —
    ``("undone", {"marshal", "charged", "quoted"})``. The price the list showed
    is the most this can ever cost."""
    from backend.commands import group_orders as G
    run_stash = narrow(stash, listing, members)
    showed = total_for(listing, members)
    try:
        snapshot, dice = world.to_dict(), random.getstate()
    except Exception as exc:
        report(exc, "directive.give: the snapshot before the order")
        snapshot, dice = None, None
    try:
        result = G._carry_out(world, game_state, parser, executor, llm_game_state, run_stash)
        charged = int(((result or {}).get("action_info") or {}).get("cost", 0) or 0)
        if charged > showed:
            raise G.Overcharge("the order", charged, showed)
    except G.Overcharge as over:
        if snapshot is None:
            raise
        report(over, "directive.give: charged more than the list said — the board is put back",
               every=True)
        world._restore_from_snapshot(snapshot)
        random.setstate(dice)
        world.calculate_visibility()
        return "undone", {"marshal": over.marshal, "charged": over.charged, "quoted": over.quoted}
    return "done", result


# ── the read-back of a line to several ──────────────────────────────────────

def readback(world, text: str, out: Dict[str, Any], readers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """`/parse_preview`'s reading of a line addressed to several corps: the
    list it will open, in one row — who, how many can go, what it costs, and
    that Enter shows the list — or None when the line is no such order (the
    ordinary reading then speaks). Called INSIDE the read-back's lock."""
    from backend.commands import group_orders as G
    from backend.commands import parse_preview as pp
    if getattr(world, "game_over", False):
        return None
    found = address(world, text)
    if found is None:
        return None
    try:
        if pp._pending_question(world, text, readers.get("interrupt_reader")):
            return None      # a standing question takes the line: the ordinary reading says so
        parse_text = text
        if found["kind"] == "army":
            lead = next((n for n in found.get("names") or []), "")
            parse_text = f"{lead}, {found['rest']}" if lead else text
        parsed = pp.mock_parse(world, parse_text, readers["llm_state"], readers.get("epoch", 0))
        built = G.build(world, pp._preview_parser(),
                        pp._llm_state(world, readers["llm_state"], readers.get("epoch", 0)),
                        text, parsed, address=found)
    except Exception as exc:
        report(exc, "directive.readback: the build")
        return None
    if built is None or built[0] != "stash":
        if found["kind"] != "army":
            return None
        # An order to a named army that the fan-out does not take (an attack is
        # ONE battle): the read-back is its first man's own reading, and says
        # so — never the bare "Army of …" line the other readers cannot read.
        if built is not None:
            return pp._refusal_reading(out, str(built[1].get("message") or "").replace(
                ", Sire — nothing spent.", "").rstrip("."))
        one = pp.read_one(world, parse_text, **readers)
        for private in ("_quote", "_marches"):
            one.pop(private, None)
        one["line"] = out["line"]
        one["parts"] = list(one.get("parts") or []) + [pp._part(
            "note", f"one man’s order, not one for each corps of the {found['army']}")]
        return one
    listing = _quote_locked(world, built[1], readers)
    rows = listing["rows"]
    going = [r for r in rows if r["ok"] or r["covered"]]
    out.update(kind="order", action=str(built[1].get("action") or ""),
               strategic=bool(built[1].get("strategic_type")),
               ap=int(listing["total"]), ap_left=int(listing["have"]), pool="military",
               ok=bool(going), free=False)
    out["directive"] = True
    count = len(going)
    head = f"{listing['who']} · {listing['order']}"
    if not going:
        out.update(kind="refusal", ok=False, refusal=listing["note"] or "no corps can take this order")
        out["parts"] = [pp._part("bad", f"{head} — {out['refusal']}"), pp._part("cost", "free refusal")]
        return out
    full = sum(int(r["ap"]) for r in going) if listing.get("staff") is None else int(listing["total"])
    cost = f"{pp._cost_text(full, 'military', full == 0)} for the {int(listing['have'])} in hand"
    parts = [pp._part("head", f"{head} · {count} corps"), pp._part("cost", cost)]
    stay = len(rows) - count
    if stay:
        parts.append(pp._part("warn", f"{stay} will not go"))
    parts.append(pp._part("note", "Enter shows the list"))
    out["parts"] = parts
    return out

"""AO — THE ARMY ORDER: a collective address, the Staff's second power, the
authority gate (October 17, 2026; `docs/REFORMS_SPEC.md` §5a is the record).

THE THREE TIERS
===============
1. **Before the Staff — the fan-out.** "everyone fortify", "all marshals march
   to Swabia", "every corps follow Ney" goes to every corps of ours that can
   take it, IN TURN, each line an ordinary `/command` through the ordinary
   parser and executor (Rule 5: one road), each at its own price. The reply
   opens with the sum against the pool. A refused corps is named and skipped
   (nothing spent); the pool's edge stops the order and names who did not go;
   a marshal who OBJECTS asks you himself — the modal is the designed surface
   — and the rest of the order waits behind his question (`world._pending_
   group`, transient, never serialized, let go at the turn boundary like the
   relay) and goes on the moment he is answered.
2. **With the Staff — the army order.** Once the court's `actions` law (France's
   Grand Quartier Général) is in force, a collective MARCH / FOLLOW / PURSUE
   is ONE order at the standing price (`ARMY_ORDER_AP` = 2): every corps of
   the EMPEROR'S COLUMN — ours, in the field, within `ARMY_COLUMN_REACH`
   provinces of the sovereign — takes the order at once, free of its own
   price and, while the Emperor's authority holds, of its own objection
   (`_army_order` on the member command). A corps beyond the column, or one
   whose state refuses the order, is named and left to its own order.
   Tactical verbs (fortify, drill …) are each corps' own labour and stay on
   the fan-out whatever law is in force.
3. **The authority gate.** `AuthorityTracker` already turns at 70 / 50 / 30.
   At `ARMY_AUTHORITY_CARRIES` (70) and above the Staff's order carries every
   objection (the doubter is named, and marches). Between `ARMY_AUTHORITY_
   HEARD` (50) and 70 a marshal who WOULD object refuses the Staff's word and
   answers you in person — his corps stays, named. Below 50 there is no army
   order: the collective falls to the fan-out at each man's price, with the
   reason said. The per-corps road is always open, so a beaten Emperor loses
   tempo, never the army.

WHAT STAYS AS IT WAS
====================
"everyone retreat" is the general retreat (CRT-1 CQ-34's pin), "everyone
attack Mack" is one battle whose leader the game asks for (the muster seats
the rest), and a plain two-name address rides the relay (CQ-8). The
collective is read only when the ordinary road would ask "Which marshal?".
Nothing is held for a later turn (CR-7-8): the stash lives one question long.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from backend.errors import report

ARMY_ORDER_AP = 2
ARMY_COLUMN_REACH = 2
ARMY_AUTHORITY_CARRIES = 70
ARMY_AUTHORITY_HEARD = 50

# The collective head: the words that mean the army, with the order after them.
# S14E-X143: the words that mean the army are ONE pattern (the head below, and the
# collective cancel's two word orders - `is_collective_cancel`, read by the
# parser's cancel arm - build from it).
_COLLECTIVE_WHO = (
    r"everyone|everybody|every\s+(?:marshal|corps|general|commander|man)"
    r"|all(?:\s+of\s+(?:you|them))?(?:\s+(?:my|the|our))?(?:\s+(?:marshals|corps|generals|commanders|men|of\s+you))?"
    r"|(?:grande\s+)?arm[eé]e|army|marshals|generals")
_COLLECTIVE_PREFIX = r"(?:(?:the|my|our)\s+)?(?:whole\s+|entire\s+)?"
COLLECTIVE_HEAD_RE = re.compile(
    r"^\s*" + _COLLECTIVE_PREFIX +
    r"(?P<who>" + _COLLECTIVE_WHO + r")"
    r"\s*[,:]?\s+(?P<rest>[A-Za-z].*)$",
    re.IGNORECASE)

# S14E-X143: "everyone stop" / "stop everyone" / "all marshals cancel" - the
# whole line is a collective address and ONE of the four recall verbs, in
# either order. The mock parser reads the line as the cancel
# (`llm_client`); the collective road below recalls EVERY standing order.
_CANCEL_VERBS = r"(?:cancel|stop|abort|halt|belay|cease)"      # S14E-X177: + cease
# ... and the orders may be named: "cancel all orders", "everyone, cancel your marches".
_ORDERS_TAIL = (r"(?:\s+(?:(?:your|their|all|the|my)\s+)?(?:(?:standing|marching)\s+)?"
                r"(?:orders?|marches|marching(?:\s+orders)?|movements?))?")
_COLLECTIVE_CANCEL_RE = re.compile(
    r"^\s*(?:please\s+)?(?:"
    + _COLLECTIVE_PREFIX + r"(?:" + _COLLECTIVE_WHO + r")\s*,?\s+" + _CANCEL_VERBS + _ORDERS_TAIL +
    r"|" + _CANCEL_VERBS + r"\s+" + _COLLECTIVE_PREFIX + r"(?:" + _COLLECTIVE_WHO + r")(?:['’]s)?"
    + _ORDERS_TAIL +
    r")(?:\s+(?:please|now))?\s*[.!]*\s*$",
    re.IGNORECASE)


_COLLECTIVE_ADDRESS_ONLY_RE = re.compile(
    r"^\s*" + _COLLECTIVE_PREFIX + r"(?:" + _COLLECTIVE_WHO + r")\s*[,:]?\s*$", re.IGNORECASE)

# T0-C (CMDFEEL-5, GR-25): the army named AFTER the verb — "fortify everyone",
# "march everyone to Swabia", "Move everybody at Rhineland to Swabia" — asked
# "Which marshal shall carry out this order?" where "everyone fortify" fanned
# out. The object form takes only the words that mean PEOPLE (never the bare
# "all" / "all the", which is "take all the guns to Swabia"'s), optionally
# the corps standing somewhere, then the rest of the order (a destination).
_COLLECTIVE_OBJECT_WHO = (
    r"everyone|everybody|every\s+(?:marshal|corps|general|commander|man)"
    r"|all\s+of\s+(?:you|them)|all\s+(?:(?:my|the|our)\s+)?(?:marshals|corps|generals|commanders)"
    r"|(?:the\s+)?(?:whole\s+|entire\s+)?(?:(?:grande\s+)?arm[eé]e|army)")
# "… who is at Rhineland" / "… standing in Swabia" / "… at Rhineland": the
# corps that stand somewhere. The place is read against the board's own
# provinces by `collective_head` (longest first), so "East Prussia" holds.
_COLLECTIVE_AT_LEAD = (r"(?:(?:who|that)\s+(?:is|are|stand|stands)\s+|standing\s+|posted\s+"
                       r"|stationed\s+|camped\s+|now\s+)?(?:at|in)\s+")
COLLECTIVE_OBJECT_RE = re.compile(
    r"^\s*(?P<verb>[A-Za-z]+(?:\s+(?:up|down|out|back|on))?)\s+"
    r"(?:(?:the|my|our)\s+)?(?P<who>" + _COLLECTIVE_OBJECT_WHO + r")"
    r"(?P<tail>(?:\s+" + _COLLECTIVE_AT_LEAD + r"[A-Za-z][A-Za-z' -]*?)?"
    r"(?:\s+(?:to|towards?|into|on|upon|for|home)\b.*)?)\s*[.!]*\s*$",
    re.IGNORECASE)
_COLLECTIVE_AT_RE = re.compile(r"^\s*" + _COLLECTIVE_AT_LEAD + r"(?P<rest>[A-Za-z].*)$", re.IGNORECASE)


def _peel_place(rest: str, places) -> Tuple[Optional[str], str]:
    """``(place, the rest after it)`` when `rest` opens with "(who is) at <a
    province>", else ``(None, rest)``. `places` are the board's province names
    (longest first wins); without them a one-word place is read."""
    m = _COLLECTIVE_AT_RE.match(rest or "")
    if not m:
        return None, rest
    after = m.group("rest")
    low = after.lower()
    for name in sorted((places or []), key=len, reverse=True):
        key = str(name).lower()
        if low == key or low.startswith(key + " ") or low.startswith(key + ","):
            tail = after[len(key):].lstrip(" ,")
            return str(name), tail
    if not places:
        word, _, tail = after.partition(" ")
        return word.strip(",."), tail
    return None, rest


def is_collective_address(text: str) -> bool:
    """S14E-X177: the text is NOTHING BUT the words that mean the army
    ("everyone", "all marshals", "the army") - the head of a collective order
    with the order cut off. PURE."""
    return bool(_COLLECTIVE_ADDRESS_ONLY_RE.match(text or ""))


def is_collective_cancel(text: str) -> bool:
    """The whole line is "<the army> <cancel|stop|abort|halt|belay|cease>" or
    the verb first ("stop everyone"), the orders optionally named ("cancel all
    orders", "everyone, cancel your marches"). PURE."""
    return bool(_COLLECTIVE_CANCEL_RE.match(text or ""))

# The verbs a collective fans out on. An attack is ONE battle (the muster
# seats the rest), a retreat is the general retreat already, and the
# economy / meta / Cabinet verbs are nobody's corps.
GROUPABLE_ACTIONS = frozenset({
    "fortify", "unfortify", "drill", "defend", "hold", "move", "scout", "wait",
    "form_square", "garrison",
})
GROUPABLE_STRATEGIC = frozenset({"MOVE_TO", "SUPPORT", "HOLD", "PURSUE"})
# The groupable verbs the executor never prices (its `free_actions`).
_NEVER_PRICED = frozenset({"wait"})
ARMY_STRATEGIC = frozenset({"MOVE_TO", "SUPPORT", "PURSUE"})

_THIRD_PERSON = {
    "marches": "march", "moves": "move", "follows": "follow", "fortifies": "fortify",
    "holds": "hold", "drills": "drill", "scouts": "scout", "pursues": "pursue",
    "supports": "support", "advances": "advance", "withdraws": "withdraw",
    "digs": "dig", "entrenches": "entrench", "waits": "wait", "defends": "defend",
    "garrisons": "garrison", "chases": "chase", "goes": "go", "heads": "head",
}


def collective_head(text: str, places=None) -> Optional[Dict[str, str]]:
    """``{"who", "rest"}`` when the line addresses the army as a whole, with
    the order's words after the head normalised to the second person ("the
    army marches on Swabia" -> "march to Swabia").

    T0-C (CMDFEEL-5, GR-25): the army named after the verb ("fortify
    everyone", "march everyone to Swabia") reads the same, the verb put back
    at the head of `rest`; and the corps standing somewhere ("Move everybody
    at Rhineland to Swabia", "Everybody who is at Rhineland goes to Swabia")
    carry the place as ``"at"`` — the fan-out goes to the corps there alone.
    `places` are the board's province names, for a multi-word place."""
    at = None
    m = COLLECTIVE_HEAD_RE.match(text or "")
    if m:
        rest = m.group("rest").strip()
        at, rest = _peel_place(rest, places)
        if at is not None:
            rest = rest.strip()
            if not rest:
                return None
    else:
        m = COLLECTIVE_OBJECT_RE.match(text or "")
        if not m:
            return None
        tail = (m.group("tail") or "").strip()
        at, tail = _peel_place(tail, places)
        rest = (m.group("verb").strip() + (" " + tail.strip() if tail.strip() else "")).strip()
    rest = second_person(rest)
    head = {"who": m.group("who"), "rest": rest}
    if at is not None:
        head["at"] = at
    return head


def second_person(rest: str) -> str:
    """The order's words after an address, in the second person: "marches on
    Swabia" -> "march to Swabia" (the collective head's own normalising, said
    once — a list of names and a named army read the same; row IC)."""
    words = str(rest or "").split()
    if words:
        first = words[0].lower()
        if first in _THIRD_PERSON:
            words[0] = _THIRD_PERSON[first]
    rest = " ".join(words)
    return re.sub(r"^(march|move|advance|head)\s+(?:on|upon|for|towards?)\s+", r"\1 to ", rest, flags=re.I)


def question_pending(world) -> bool:
    """A question the player has not yet answered stands on the world."""
    if getattr(world, "pending_objection", None) or getattr(world, "pending_strategic_objection", None):
        return True
    for m in _field_marshals(world):
        if getattr(m, "pending_interrupt", None):
            return True
    try:
        from backend.commands.clarification import CLARIFICATION_DIALOGUE_TYPE
        top = world.dialogue_manager.peek()
        if top is not None and top.get("type") == CLARIFICATION_DIALOGUE_TYPE:
            return True
    except Exception as exc:
        report(exc, "group_orders.question_pending: dialogue_manager.peek")
    return False


def _field_marshals(world) -> List[Any]:
    """Our corps in the field — `get_field_marshals` (no administrative
    role, standing, not a prisoner), with men only."""
    try:
        field = list(world.get_field_marshals())
    except Exception as exc:
        report(exc, "group_orders._field_marshals: get_field_marshals")
        field = [m for m in world.get_player_marshals() if not getattr(m, "captured_by", "")]
    return [m for m in field
            if int(getattr(m, "strength", 0) or 0) > 0 and not getattr(m, "captured_by", "")]


def _sovereign(world):
    for m in _field_marshals(world):
        if getattr(m, "is_sovereign", False):
            return m
    return None


def authority_of(world, nation: Optional[str] = None) -> int:
    nation = nation or world.player_nation
    if nation == world.player_nation:
        tracker = getattr(world, "authority_tracker", None)
        return int(getattr(tracker, "authority", 100) if tracker is not None else 100)
    # AU-4 (BUG_FIXES.md §AU): a court reads the one reader — the table's own
    # figure, 60 for a court missing from it (`standing.COURT_DEFAULT`), never 75
    from backend.game_logic import standing
    return int(standing.standing_of(world, nation))


def army_order_available(world, nation: Optional[str] = None) -> bool:
    """The court's Staff (its one `actions` law) is in force — `REFORMS_SPEC.md` §5a."""
    from backend.game_logic.reforms import staff_actions
    return staff_actions(world, nation or world.player_nation) > 0


def _first_sentence(message: str, limit: int = 220) -> str:
    """The member's reply, in one sentence: the first line up to its first
    sentence end (the long replies — the standing order's doctrine, the
    supply warning — are his own; the roll-call keeps the headline)."""
    text = str(message or "").strip().split("\n")[0].strip()
    end = re.search(r"[.!?](?:\s|$)", text)
    if end and end.end() >= 24:
        text = text[:end.end()].strip()
    if len(text) > limit:
        text = text[:limit].rstrip() + "…"
    return text


def _probe_verb(action: str, strategic_type: Optional[str], rest: str) -> str:
    if strategic_type == "MOVE_TO":
        return "march"
    if strategic_type == "SUPPORT":
        return "follow" if re.match(r"\s*follow\b", rest or "", re.I) else "support"
    if strategic_type == "HOLD":
        return "hold"
    if strategic_type == "PURSUE":
        return "pursue"
    return action or ""


def _price(world, marshal, action: str, strategic_type: Optional[str]) -> int:
    if strategic_type:
        return int(marshal.strategic_order_ap(order_type=strategic_type))
    if action in _NEVER_PRICED:
        # Row IC (IC-D2, found by the directive's fuzz): the executor never
        # prices these (`executor.py`'s `free_actions`) — "everyone, wait" with
        # no action left said "the pool is spent" of an order that is free,
        # and its head counted an action a corps.
        return 0
    if action in ("fortify", "defend"):
        # Row IC (IC-D10, rule 10's sibling of S14G-X167, found by the war-table
        # walk): a fortify from NEUTRAL (a defend from AGGRESSIVE) costs two —
        # the stance first — and the head said one ("2 corps, 2 actions" of an
        # order that spent four), and the pool check let a man go whom the
        # executor then refused for want of the second action. The one source
        # the chips, the cards and the list read (`state_probe._cost`).
        from backend.commands.state_probe import _cost
        return int(_cost(world, marshal, action, None))
    try:
        return int(world.get_action_cost(action))
    except Exception as exc:
        report(exc, "group_orders._price: world.get_action_cost")
        return 1


def _leader_name(world, parsed: Dict) -> str:
    """The man the order names (a follow / support / pursuit) — he is not
    ordered to follow himself."""
    target = str((parsed.get("command") or {}).get("target") or "")
    if target and world.get_marshal(target) is not None:
        return target
    return ""


def _display(name: str) -> str:
    from backend.display_names import humanize_entity_name
    return humanize_entity_name(name)


# ───────────────────────────── the fan-out ──────────────────────────────

def _run_members(world, game_state, parser, executor, llm_game_state,
                 stash: Dict[str, Any]) -> Dict[str, Any]:
    """Carry the order to the members still waiting (in `stash["members"]`),
    each line through the ordinary road. Returns ``{"lines", "question",
    "events", "waiting", "spent"}``: `question` is the member result that
    asked, with the rest of the members left in the stash on the world;
    `spent` (ACH-1) sums the actions each member's own reply says it cost."""
    from backend.main import _result_carries_question
    from backend.commands.state_probe import order_state_refusal
    rest = stash["rest"]
    action = stash["action"]
    strategic_type = stash.get("strategic_type")
    army = bool(stash.get("army"))
    band = stash.get("band")
    lines: List[str] = []
    events: List[Any] = []
    spent = 0
    refused: List[Tuple[str, str]] = []   # UI6-X26: (corps, why) - the order was NOT taken
    members: List[str] = list(stash["members"])
    # Row IC (the directive): every member's outcome as a row — {marshal, sent,
    # line, why, ap} — for the reply's `group.rows` (the list is the truth:
    # what was shown is what is reported); `quoted` is each man's price as the
    # list showed it (a give alone carries it), checked as he is charged.
    rows: List[Dict[str, Any]] = []
    quoted: Dict[str, int] = stash.get("quoted") or {}
    named = stash.get("kind") in ("list", "army")

    def _not_sent(who: str, sent_line: str, why: str) -> None:
        rows.append({"marshal": who, "sent": False, "line": sent_line, "why": why, "ap": 0})

    while members:
        name = members[0]
        marshal = world.get_marshal(name)
        if marshal is None or int(getattr(marshal, "strength", 0) or 0) <= 0:
            members.pop(0)
            if named:
                # A man NAMED (a list, an army) who cannot take an order is
                # said; the collective words skip him in silence, as before.
                lines.append(f"{_display(name)} — not in the field.")
                refused.append((name, ""))
                _not_sent(name, "", "not in the field")
            continue
        verb = _probe_verb(action, strategic_type, rest)
        line = f"{name}, {rest}"
        own_price: Optional[int] = None
        if stash.get("click"):
            # A group sent by a click on a province: each man's own plain order,
            # as his single click sends it (`order_quotes.march_quote(click=True)`
            # — a move where the plain move takes it, else the march).
            clicked = click_line(world, marshal, strategic_type, stash.get("target"))
            if clicked is not None:
                line, verb, own_price = clicked
        if not army:
            if own_price is None and name in quoted:
                own_price = int(quoted[name])      # the price his row showed
            price = own_price if own_price is not None else _price(world, marshal, action, strategic_type)
            if int(getattr(world, "actions_remaining", 0) or 0) < price:
                break
        reason = order_state_refusal(world, marshal, verb) if verb in _probe_verbs() else ""
        if reason:
            members.pop(0)
            lines.append(f"{_display(name)} — {reason}.")
            refused.append((name, ""))
            _not_sent(name, line, reason)
            continue
        if army and band == "heard":
            # 50–69: a marshal who WOULD object refuses the Staff's word.
            doubt = _would_object(world, marshal, strategic_type, parsed_target=stash.get("target"), rest=rest)
            if doubt:
                members.pop(0)
                lines.append(f"{_display(name)} will not march on the Staff's word — "
                             f"he answers you in person; order him yourself.")
                refused.append((name, ""))
                _not_sent(name, line, "will not march on the Staff's word — order him yourself")
                continue
        members.pop(0)
        try:
            parsed = parser.parse(line, llm_game_state, world=world)
        except Exception as exc:
            report(exc, "group_orders._run_members: parser.parse")
            lines.append(f"{_display(name)} — the order could not be read for him.")
            refused.append((name, ""))
            _not_sent(name, line, "the order could not be read for him")
            continue
        if not parsed.get("success"):
            _why = _first_sentence(parsed.get('error') or parsed.get('message') or 'the order could not be read for him')
            lines.append(f"{_display(name)} — {_why}")
            refused.append((name, ""))
            _not_sent(name, line, _why)
            continue
        command = parsed.get("command") or {}
        if army:
            # Free of its own price and of the battery's objection (the
            # executor's `_army_order` arms); the standing order is created
            # as any typed one is — `_strategic_execution` is NOT set, that
            # flag is a per-turn STEP's and would skip the order's creation.
            command["_army_order"] = True
            parsed["command"] = command
        try:
            result = executor.execute(parsed, game_state)
        except Exception as exc:
            report(exc, "group_orders._run_members: executor.execute", every=True)
            lines.append(f"{_display(name)} — the order failed for him.")
            refused.append((name, ""))
            _not_sent(name, line, "the order failed for him")
            continue
        if isinstance(result, dict) and result.get("events"):
            events.extend(result.get("events") or [])
        cost = 0
        if isinstance(result, dict) and isinstance(result.get("action_info"), dict):
            cost = int(result["action_info"].get("cost") or 0)
            spent += cost
        if name in quoted and cost > int(quoted[name]):
            # The list is the truth: a man charged MORE than his row said is
            # never let stand — the give's caller puts the board back.
            raise Overcharge(name, cost, int(quoted[name]))
        if _result_carries_question(result):
            stash["members"] = members
            stash["lines"] = list(stash.get("lines", [])) + lines
            stash["events"] = list(stash.get("events", [])) + events
            # (the list's prices were for the board as it stood: the men who
            # wait go on a board the answer has changed, at their own price)
            stash.pop("quoted", None)
            world._pending_group = stash
            rows.append({"marshal": name, "sent": False, "line": line, "asked": True,
                         "why": "asks you first", "ap": int(cost)})
            for waiter in members:
                _not_sent(waiter, "", f"waits behind {_display(name)}'s question")
            return {"lines": lines, "question": result, "events": events, "waiting": members,
                    "asker": name, "spent": spent, "refused": refused, "rows": rows}
        said = _first_sentence(result.get("message", ""))
        if isinstance(result, dict) and result.get("success") is False:
            refused.append((name, said))
            _not_sent(name, line, said)
        else:
            rows.append({"marshal": name, "sent": True, "line": line, "why": "", "ap": int(cost)})
        if army and band == "carries" and _would_object(
                world, marshal, strategic_type, parsed_target=stash.get("target"), rest=rest):
            said += " (He had his doubts; the Staff's order carries.)"
        lines.append(_member_line(name, said))
    world._pending_group = None
    for waiter in members:
        _not_sent(waiter, "", "the actions were spent before him")
    return {"lines": lines, "question": None, "events": events, "waiting": members, "asker": "",
            "spent": spent, "refused": refused, "rows": rows}


class Overcharge(Exception):
    """Row IC (the directive): a member was charged more than the list said."""

    def __init__(self, marshal: str, charged: int, quoted: int):
        super().__init__(f"{marshal} was charged {charged} where the list said {quoted}")
        self.marshal, self.charged, self.quoted = marshal, int(charged), int(quoted)


def click_line(world, marshal, strategic_type: Optional[str], target) -> Optional[Tuple[str, str, int]]:
    """``(line, verb, price)`` for a corps of a group sent by a CLICK on a
    province: the order his own single click would send — the plain move
    where the move takes it, else the march (`order_quotes.march_quote(
    click=True)`, row PW's rule) — or None where the click road has nothing
    of its own to say (another order type, a place that is no province, an
    order the quote refuses: the typed line's own reading then speaks)."""
    if strategic_type != "MOVE_TO" or not target or world.get_region(str(target)) is None:
        return None
    try:
        from backend.commands import order_quotes as Q
        quote = Q.march_quote(world, marshal, str(target), click=True)
    except Exception as exc:
        report(exc, "group_orders.click_line: order_quotes.march_quote")
        return None
    if not quote.get("ok") or quote.get("already") or not quote.get("command"):
        return None
    verb = "move" if str(quote.get("kind") or "") == "move" else "march"
    return str(quote["command"]), verb, int(quote.get("ap", 0) or 0)


def _member_line(name: str, said: str) -> str:
    """S14G-X17 (Pre-Deploy S14h part 1, October 26, 2026): one member's line
    in a group's reply. A reply that already opens with his name ("Ney already
    stands at Vienna - nothing spent.", "Ney begins march to Frankfurt.", "Ney
    halts his march ...") is the line - the group's "Ney: " prefix printed the
    name twice ("Ney: Ney already stands at Vienna"). The refusal sentence is
    shared with the quote and the typed order (`own_province_march_refusal`),
    so the fix is here, at the group's formatting. A reply that does not open
    with his name keeps the prefix that says whose it is."""
    shown = _display(name)
    if not said:
        return f"{shown}: done."
    if re.match(re.escape(shown) + r"(?![A-Za-z])", said):
        return said
    return f"{shown}: {said}"


def _probe_verbs():
    from backend.commands.state_probe import VERBS
    return VERBS


def _would_object(world, marshal, strategic_type: Optional[str], *, parsed_target: str, rest: str) -> bool:
    """Would this marshal object to the order? The quote's pure read — the
    evaluators run under a saved random state, so no dice are spent."""
    try:
        from backend.commands import order_quotes as Q
        if strategic_type == "MOVE_TO" and parsed_target:
            return Q.march_quote(world, marshal, parsed_target).get("objection") == "possible"
        if strategic_type == "SUPPORT" and parsed_target:
            ally = world.get_marshal(parsed_target)
            if ally is not None:
                return Q.support_quote(world, marshal, ally).get("objection") == "possible"
        if strategic_type == "PURSUE" and parsed_target:
            foe = world.get_marshal(parsed_target)
            road = [foe.location] if foe is not None else []
            return Q._strategic_objection(world, marshal, "PURSUE", parsed_target, road) == "possible"
    except Exception as exc:
        report(exc, "group_orders._would_object")
    return False


def _column_detour_clause(world, stash: Dict[str, Any], names: List[str]) -> str:
    """S14E-X134: "3 of 5 corps take a long or foreign road — their cards say
    which" for the column the Staff's typed order commits, read through the
    cards' own readers (`order_quotes.column_detours`); '' when no corps detours."""
    try:
        from backend.commands import order_quotes as Q
        count = Q.column_detours(world, names, stash.get("strategic_type"),
                                 str(stash.get("target") or ""), memo={})
        return Q.detour_count_clause(count, len(names))
    except Exception as exc:
        report(exc, "group_orders._column_detour_clause")
        return ""


def _head_line(world, stash: Dict[str, Any], names: List[str], have: Optional[int] = None,
               quoted: Optional[Dict[str, int]] = None) -> str:
    rest = stash["rest"]
    if stash.get("click") and stash.get("strategic_type") == "MOVE_TO" and stash.get("target"):
        # Row IC: a group sent by a click — each man's own click order (a move
        # next door, a march beyond); the head says neither, as the list does.
        rest = f"go to {_display(str(stash['target']))}"
    n = len(names)
    if stash.get("army"):
        line = (f"The Grand Quartier Général carries the Emperor's order — {ARMY_ORDER_AP} actions, "
                f"the whole column: {n} corps within {ARMY_COLUMN_REACH} provinces of the Emperor, "
                f"'{rest}'.")
        # S14E-X134: the Staff's order skips the road ask (S14E-22's scope), so the
        # head says how many of the column take a long or foreign road - the quote's
        # own count (`order_quotes.detour_count_clause`), '' when none does.
        detour = _column_detour_clause(world, stash, names)
        if detour:
            line += " " + detour + "."
        if stash.get("note"):
            line += " " + stash["note"]
        return line
    total = 0
    if quoted is None:
        quoted = stash.get("quoted") or {}
    for name in names:
        m = world.get_marshal(name)
        if name in quoted:
            total += int(quoted[name])      # row IC: the price the list showed
        elif m is not None:
            total += _price(world, m, stash["action"], stash.get("strategic_type"))
    if have is None:
        have = int(getattr(world, "actions_remaining", 0) or 0)
    if stash.get("cancel"):
        # S14E-X143: the recall's own head - what it recalls and what it costs
        # (each corps' cancel is the ordinary one: the price is its own).
        if stash.get("kind") in ("list", "army"):
            return (f"The standing orders of {_whom(stash)} are recalled, corps by corps — "
                    f"{n} corps, {total} action{'s' if total != 1 else ''} for the {have} in hand.")
        return (f"Every standing order is recalled, corps by corps — {n} corps, "
                f"{total} action{'s' if total != 1 else ''} for the {have} in hand.")
    # T0-C (CMDFEEL-5): the corps at a named province, when the order named one.
    whom = _whom(stash)
    line = (f"The order goes to {whom}, corps by corps — {n} corps, {total} action"
            f"{'s' if total != 1 else ''} for the {have} in hand: '{rest}'.")
    if stash.get("note"):
        line += " " + stash["note"]
    return line


def _whom(stash: Dict[str, Any]) -> str:
    """Who the order goes to, in the head's words: the army (the collective
    words), the corps at a province, the men a list named ("Ney, Lannes and
    Murat"), or a named army ("the Army of Italy") — row IC."""
    kind = stash.get("kind")
    if kind == "army" and stash.get("army_name"):
        return f"the {stash['army_name']}"
    if kind == "list":
        shown = [_display(n) for n in (stash.get("who") or stash.get("members") or [])]
        if len(shown) <= 1:
            return shown[0] if shown else "the corps named"
        return ", ".join(shown[:-1]) + " and " + shown[-1]
    return f"the corps at {_display(stash['at'])}" if stash.get("at") else "the army"


def _waiting_line(waiting: List[str]) -> str:
    if not waiting:
        return ""
    shown = ", ".join(_display(n) for n in waiting)
    return (f"Nothing left for {shown} today — the pool is spent; they take the order "
            f"with tomorrow's actions, or name the corps that matter most.")


def _compose(stash: Dict[str, Any], run: Dict[str, Any], head: str, *, resumed: bool,
             with_question: bool = True) -> str:
    """The order's reply in words: the head, each man's line, then the
    question that stopped it and who waits behind it — or, `with_question`
    False (row IC), everything but the question's own words (`group.said`:
    the client says it before the question's window)."""
    parts: List[str] = []
    if not resumed:
        parts.append(head)
    parts.extend(run["lines"])
    q = run.get("question")
    if q is not None:
        asker = _display(run.get("asker") or "")
        msg = str(q.get("message") or "")
        if with_question:
            parts.append(msg)
        rest_names = run.get("waiting") or []
        if rest_names:
            parts.append(f"The order waits for {', '.join(_display(n) for n in rest_names)} "
                         f"behind {asker}'s question.")
    else:
        w = _waiting_line(run.get("waiting") or [])
        if w:
            parts.append(w)
    return "\n".join(p for p in parts if p)


# ───────────────────────────── the entry ────────────────────────────────

def try_collective(world, game_state, parser, executor, llm_game_state,
                   command_text: str, parsed: Dict) -> Optional[Dict[str, Any]]:
    """The collective road, or None when the line is not the army's or the
    ordinary road already serves it. Called by `main._command_ordinary_road`
    in place of the executor."""
    try:
        return _try_collective(world, game_state, parser, executor, llm_game_state, command_text, parsed)
    except Exception as exc:
        report(exc, "group_orders.try_collective", every=True)
        return None


def _try_collective(world, game_state, parser, executor, llm_game_state,
                    command_text: str, parsed: Dict) -> Optional[Dict[str, Any]]:
    built = build(world, parser, llm_game_state, command_text, parsed)
    if built is None:
        return None
    if built[0] == "result":
        return built[1]
    return _carry_out(world, game_state, parser, executor, llm_game_state, built[1])


# The orders a LIST of names keeps on today's road — one battle, the first man
# leads and the muster calls the others (`parser.SECOND_NAME_SUPPORT_ACTIONS`):
# his attack, charge, bombardment or pursuit is never fanned out to a list.
LIST_KEEPS_ONE_BATTLE = frozenset({"attack", "charge", "pursue", "bombard"})
# Row IC, Session 2 (IC-7): the verbs only a NAMED address fans out — a list
# of names, a named army, a group sent from the map. "Ney, Davout and Soult,
# fall back" is each man's own fall back, on the one list (the group face's
# "Fall back…"); "everyone retreat" stays the GENERAL retreat it always was
# (`GROUPABLE_ACTIONS` is untouched, so the collective road never sees it).
NAMED_ONLY = frozenset({"retreat"})


def build(world, parser, llm_game_state, command_text: str, parsed: Dict, *,
          address: Optional[Dict[str, Any]] = None, click: bool = False
          ) -> Optional[Tuple[str, Dict[str, Any]]]:
    """The order to several corps as the fan-out will run it — ``("stash",
    stash)`` — or the free answer that stands in its place — ``("result",
    result)`` — or None when the line is no order to several that the fan-out
    takes (the ordinary road then speaks).

    `address` is `directive.address`'s reading of who the line names (row IC):
    a LIST of names or a named ARMY is built from it (a list's parse names its
    first man, so "no marshal named" is no test of it); without one — and for
    the collective words — this is the collective road exactly as AO landed
    it. PURE: nothing is written to the world (the read-only quote calls it
    with the built-in reader)."""
    if (address or {}).get("kind") in ("list", "army"):
        return _build_named(world, parser, llm_game_state, command_text, parsed, address, click)
    command = (parsed or {}).get("command") or {}
    if command.get("marshal") or not parsed.get("success"):
        return None
    # S14E-X143: a collective address that parsed as the cancel recalls every
    # standing order (the verb may come first: "stop everyone").
    if (str(command.get("action") or "") == "cancel" and not parsed.get("is_strategic")
            and (is_collective_cancel(command_text) or collective_head(command_text) is not None)):
        stash = _collective_cancel(world, command_text)
        return ("stash", stash) if stash is not None else None
    head = collective_head(command_text, places=list(getattr(world, "regions", {}) or {}))
    if head is None:
        return None
    action = str(command.get("action") or "")
    strategic_type = parsed.get("strategic_type") if parsed.get("is_strategic") else None
    if strategic_type:
        if strategic_type not in GROUPABLE_STRATEGIC:
            return None
    elif action not in GROUPABLE_ACTIONS:
        return None
    field = _field_marshals(world)
    at = head.get("at")
    if at:
        # T0-C (CMDFEEL-5): the corps standing at the named province alone.
        field = [m for m in field
                 if str(getattr(m, "location", "") or "").lower() == str(at).lower()]
        if not field:
            return ("result", {
                "success": False,
                "message": f"No corps of ours stands at {_display(at)}, Sire — nothing spent.",
                "variable_action_cost": 0,
            })
    if not field:
        return None
    rest = head["rest"]
    # The probe: how the first man would read the line — the verb and the
    # target the whole order carries (the collective parse itself names no
    # marshal, so its target may be bare).
    probe = parser.parse(f"{field[0].name}, {rest}", llm_game_state, world=world)
    if not probe.get("success"):
        return None
    p_cmd = probe.get("command") or {}
    p_action = str(p_cmd.get("action") or action)
    p_type = probe.get("strategic_type") if probe.get("is_strategic") else None
    if p_type:
        if p_type not in GROUPABLE_STRATEGIC:
            return None
    elif p_action not in GROUPABLE_ACTIONS:
        return None
    target = str(p_cmd.get("target") or "")
    leader = _leader_name(world, probe) if p_type in ("SUPPORT", "PURSUE") else ""
    members = [m.name for m in field if m.name != leader]

    stash: Dict[str, Any] = {
        "rest": rest, "action": p_action, "strategic_type": p_type, "target": target,
        "members": members, "turn": int(getattr(world, "current_turn", 0) or 0),
        "army": False, "band": None, "note": "", "lines": [], "events": [],
        "raw": command_text, "at": at or "",
        # Row IC (the directive's list): every corps the words address, before
        # the Staff narrows `members` to its column.
        "kind": "at" if at else "everyone", "addressed": list(members),
    }
    army_refusal = ""
    if p_type in ARMY_STRATEGIC:
        army_refusal = _army_gate(world, stash, field, leader)
        if army_refusal:
            stash["note"] = army_refusal
    return ("stash", stash)


def _collective_cancel(world, command_text: str) -> Optional[Dict[str, Any]]:
    """S14E-X143: "everyone stop" recalls EVERY standing order, corps by corps,
    each as the ordinary `cancel` (one road, its own price, its own trust) -
    where the parsed cancel carried no name and recalled the FIRST corps with
    an order, at one action, in a reply that said only his. None when fewer
    than two corps hold an order: the ordinary road recalls that one (or
    says there is none) exactly as before. Returns the stash (row IC: the
    caller carries it out, or lists it first)."""
    standing = [m.name for m in world.get_player_marshals()
                if getattr(m, "strategic_order", None) is not None
                and int(getattr(m, "strength", 0) or 0) > 0]
    if len(standing) < 2:
        return None
    return {
        "rest": "cancel", "action": "cancel", "strategic_type": None, "target": "",
        "members": standing, "turn": int(getattr(world, "current_turn", 0) or 0),
        "army": False, "band": None, "note": "", "lines": [], "events": [],
        "raw": command_text, "cancel": True,
        "kind": "everyone", "addressed": list(standing),
    }


def _build_named(world, parser, llm_game_state, command_text: str, parsed: Dict,
                 address: Dict[str, Any], click: bool
                 ) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Row IC: the stash of an order to a LIST of names ("Ney, Lannes and
    Murat, march to Ulm") or to a named ARMY ("Army of Italy, hold") — the same
    fan-out the collective words take, to the men named. None where the order
    is not one the fan-out takes (an attack is one battle: the first man leads
    and the muster calls the others — the road it had). The Staff's single
    order is the collective's alone: the men named each go at their own price."""
    kind = str(address.get("kind") or "")
    names = [str(n) for n in (address.get("names") or [])]
    rest = second_person(str(address.get("rest") or "").strip())
    if not names or not rest:
        return None
    field = {m.name for m in _field_marshals(world)}
    lead = next((n for n in names if n in field), None)
    if lead is None:
        who = (f"The {address.get('army')}" if kind == "army" else "None of the men you named")
        tail = "has no corps" if kind == "army" else "stands"
        return ("result", {"success": False, "variable_action_cost": 0,
                           "message": f"{who} {tail} in the field to take an order, Sire — nothing spent."})
    # The probe: how the first man in the field reads the line (the parse the
    # command already made, where it is his).
    command = (parsed or {}).get("command") or {}
    probe = parsed if (parsed or {}).get("success") and command.get("marshal") == lead else None
    if probe is None:
        probe = parser.parse(f"{lead}, {rest}", llm_game_state, world=world)
    if not probe.get("success"):
        return None
    p_cmd = probe.get("command") or {}
    p_action = str(p_cmd.get("action") or "")
    p_type = probe.get("strategic_type") if probe.get("is_strategic") else None
    cancel = p_action == "cancel" and not p_type
    if kind == "list" and not click and (p_type == "PURSUE" or p_action in LIST_KEEPS_ONE_BATTLE):
        # (a group sent from the map or the desk — `click` — is each man's own
        # order by its nature: its pursuit fans out, as "everyone pursue Mack" does)
        return None
    if p_type:
        if p_type not in GROUPABLE_STRATEGIC:
            return None
    elif not cancel and p_action not in GROUPABLE_ACTIONS and p_action not in NAMED_ONLY:
        return None
    target = str(p_cmd.get("target") or "")
    leader = _leader_name(world, probe) if p_type in ("SUPPORT", "PURSUE") else ""
    members = [n for n in names if n != leader]
    if not members:
        return None
    stash: Dict[str, Any] = {
        "rest": "cancel" if cancel else rest, "action": p_action, "strategic_type": p_type,
        "target": target, "members": members,
        "turn": int(getattr(world, "current_turn", 0) or 0),
        "army": False, "band": None, "note": "", "lines": [], "events": [],
        "raw": command_text, "at": "",
        "kind": kind, "addressed": list(members), "who": list(members),
        "army_name": str(address.get("army") or ""), "click": bool(click),
    }
    if cancel:
        stash["cancel"] = True
    return ("stash", stash)


def _carry_out(world, game_state, parser, executor, llm_game_state,
               stash: Dict[str, Any]) -> Dict[str, Any]:
    """Head the order, run it corps by corps, and build the reply - the tail
    both the fan-out and the collective cancel share."""
    # UI6-X26 (Session UI-6, November 13, 2026): a quote is what the order
    # will cost. The head used to price EVERY corps ("8 corps, 14 actions for
    # the 4 in hand") for an order each corps then refused for want of
    # intelligence on the man named. The head is built AFTER the corps are
    # asked - from the corps that took the order, against the pool as it stood
    # - and the Staff's charge is spent only when some corps took it. When no
    # corps took it and they all gave ONE reason, that reason is the whole
    # answer, free (as the single order says it).
    have = int(getattr(world, "actions_remaining", 0) or 0)
    original = list(stash["members"])
    # Row IC: the prices the list showed, kept for the head (a question pops
    # them off the stash: the men who wait go on later at their own price).
    shown_prices = dict(stash.get("quoted") or {}) or None
    if shown_prices is None and not stash.get("army"):
        # IC-D10: each man's price as the order FINDS him, read before the run —
        # a fortify from NEUTRAL costs two, and once he has dug in he stands
        # DEFENSIVE, where the table says one (the head is built after the run).
        shown_prices = {}
        for name in original:
            marshal = world.get_marshal(name)
            if marshal is not None:
                shown_prices[name] = _price(world, marshal, stash["action"], stash.get("strategic_type"))
    run = _run_members(world, game_state, parser, executor, llm_game_state, stash)
    refused = list(run.get("refused") or [])
    refused_names = {n for n, _why in refused}
    took = [n for n in original if n not in refused_names]
    if not took and not stash.get("cancel"):
        reasons = {why for _n, why in refused}
        if len(reasons) == 1 and next(iter(reasons)):
            reason = next(iter(reasons))
            if stash.get("at"):
                # T0-C (CMDFEEL-5): the corps the order named by place are
                # still named — they all gave the one answer.
                reason += (f" Nothing spent — the corps at {_display(stash['at'])} "
                           f"({len(original)} corps: {', '.join(_display(n) for n in original)}) "
                           f"all answer alike.")
            else:
                reason += " Nothing spent."
            return {"success": False, "message": reason,
                    "variable_action_cost": 0, "group": {"army": stash["army"], "members": [],
                                                         "asked": False,
                                                         "rows": _rows_of(stash, run)}}
        head_line = ("No corps takes the order, Sire — nothing spent: "
                     f"'{stash['rest']}'.")
        head_spent = 0
    else:
        head_line = _head_line(world, stash, took if refused else original, have, quoted=shown_prices)
        head_spent = (world.spend_actions("strategic", ARMY_ORDER_AP)["action_cost"]
                      if stash["army"] else 0)
    stash["head"] = head_line
    message = _compose(stash, run, head_line, resumed=False)
    q = run.get("question")
    result: Dict[str, Any] = {"success": True, "message": message,
                              "group": {"army": stash["army"], "members": stash["members"],
                                        "asked": bool(q),
                                        # Row IC: every row of the order, as it went.
                                        "rows": _rows_of(stash, run)},
                              "events": run.get("events") or []}
    if q is not None:
        for key, value in q.items():
            if key in ("message", "new_state", "events"):
                continue
            result[key] = value
        # Row IC: who went and who waits, without the question's own words —
        # said by the client BEFORE the question's window (which carries only
        # the question); without it the rest of the order's result was lost.
        result["group"]["said"] = _compose(stash, run, head_line, resumed=False, with_question=False)
    # ACH-1: the whole order's price — the Staff's charge and every corps'
    # own reply — where it said 0 while the corps spent the pool.
    result["action_info"] = world.get_action_info(head_spent + int(run.get("spent") or 0))
    result["action_summary"] = world.get_action_summary()
    return result


def _rows_of(stash: Dict[str, Any], run: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Row IC: the reply's rows — each man the run reached (`{marshal, sent,
    line, why, ap}`), then the men the list held back with their reasons
    (`stash["left_out"]`: not ticked, beyond the Staff's reach). Every number
    an int (Golden Rule 2)."""
    rows = [dict(r, ap=int(r.get("ap", 0) or 0)) for r in (run.get("rows") or [])]
    seen = {r["marshal"] for r in rows}
    for name, why in (stash.get("left_out") or []):
        if name not in seen:
            rows.append({"marshal": str(name), "sent": False, "line": "", "why": str(why), "ap": 0})
    return rows


def _army_gate(world, stash: Dict[str, Any], field: List[Any], leader: str) -> str:
    """Decide the tier for a collective standing order: the army order (the
    stash is marked and its column chosen), or the reason it is not one —
    said at the head of the fan-out."""
    if not army_order_available(world):
        return ("With the Grand Quartier Général in force this would be one order at "
                f"{ARMY_ORDER_AP} actions (the Laws, under the ledger).")
    sovereign = _sovereign(world)
    if sovereign is None:
        return "The army has no Emperor at its head to follow — each corps takes its own order."
    authority = authority_of(world)
    if authority < ARMY_AUTHORITY_HEARD:
        return (f"The Staff's order would not carry — at authority {authority} the marshals "
                f"march only on your own word, one by one, each at his own price.")
    if int(getattr(world, "actions_remaining", 0) or 0) < ARMY_ORDER_AP:
        return (f"The army order needs {ARMY_ORDER_AP} actions and {int(world.actions_remaining)} "
                f"remain — each corps takes its own order instead.")
    column, beyond = [], []
    for m in field:
        if m.name == leader:
            continue
        try:
            dist = int(world.get_distance(m.location, sovereign.location))
        except Exception as exc:
            report(exc, "group_orders._army_gate: world.get_distance")
            dist = 999
        (column if dist <= ARMY_COLUMN_REACH else beyond).append(m.name)
    if not column:
        return "No corps stands within the Emperor's reach — each corps takes its own order."
    stash["army"] = True
    stash["band"] = "carries" if authority >= ARMY_AUTHORITY_CARRIES else "heard"
    stash["members"] = column
    stash["beyond"] = beyond
    note = ""
    if beyond:
        note = (f"Beyond the Emperor's reach, left to their own orders: "
                f"{', '.join(_display(n) for n in beyond)}.")
    if stash["band"] == "heard":
        note = (f"Authority {authority}: a marshal with doubts refuses the Staff's word "
                f"and answers you in person. " + note).strip()
    stash["note"] = note
    return ""


# ───────────────────────────── the resume ───────────────────────────────

def resume(world, game_state, parser, executor, llm_game_state) -> Optional[Dict[str, Any]]:
    """Carry a stashed order on once its member's question is answered —
    ``None`` when nothing waits, or a question still stands, or the stash is
    from another turn (let go)."""
    stash = getattr(world, "_pending_group", None)
    if not stash:
        return None
    if int(stash.get("turn", -1)) != int(getattr(world, "current_turn", 0) or 0):
        world._pending_group = None
        return None
    if question_pending(world):
        return None
    try:
        run = _run_members(world, game_state, parser, executor, llm_game_state, stash)
    except Exception as exc:
        report(exc, "group_orders.resume", every=True)
        world._pending_group = None
        return None
    text = _compose(stash, run, stash.get("head", ""), resumed=True)
    if text:
        text = "The order goes on.\n" + text
    out: Dict[str, Any] = {"message": text, "question": run.get("question"),
                           "events": run.get("events") or [],
                           "waiting": run.get("waiting") or [],
                           "spent": int(run.get("spent") or 0)}
    return out


_QUESTION_CARRY = (
    "state", "pending_objection", "objection", "choices", "alternative", "awaiting_response",
    "clarification", "clarification_kind", "clarification_registered", "options", "question",
    "pending_strategic_objection", "pending_interrupt", "requires_input", "interrupt",
    "pending_glorious_charge", "pending_capture_choice", "muster_preview", "massed_strength",
)


def attach(response: Dict[str, Any], cont: Optional[Dict[str, Any]], world) -> None:
    """Fold a resumed order into the reply that answered its member's
    question: the lines after the answer, and the next question's own keys
    when another member asked."""
    if not cont:
        return
    text = str(cont.get("message") or "")
    if text:
        base = str(response.get("message") or "")
        response["message"] = (base + "\n\n" + text) if base else text
    if cont.get("events"):
        response["events"] = list(response.get("events") or []) + list(cont["events"])
    q = cont.get("question")
    if isinstance(q, dict):
        for key in _QUESTION_CARRY:
            if q.get(key) is not None and key in q:
                response[key] = q[key]
    # ACH-1: the corps the answer released spent too — their price joins the
    # answer's own (the interrupt road's reply carries no `action_info` of
    # its own, so it is given one when they spent).
    spent = int(cont.get("spent") or 0)
    info = response.get("action_info")
    if isinstance(info, dict):
        info["cost"] = int(info.get("cost") or 0) + spent
        info["remaining"] = int(getattr(world, "actions_remaining", 0) or 0)
    elif spent:
        response["action_info"] = world.get_action_info(spent)
    response["action_summary"] = world.get_action_summary()


def merge_into_result(result: Dict[str, Any], cont: Optional[Dict[str, Any]], world) -> None:
    """The same fold for an executor RESULT on the /command road (a typed
    answer that went through the stages)."""
    if not cont or not isinstance(result, dict):
        return
    attach(result, cont, world)

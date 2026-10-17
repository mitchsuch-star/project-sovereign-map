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
from typing import Any, Dict, List, Optional

from backend.errors import report

ARMY_ORDER_AP = 2
ARMY_COLUMN_REACH = 2
ARMY_AUTHORITY_CARRIES = 70
ARMY_AUTHORITY_HEARD = 50

# The collective head: the words that mean the army, with the order after them.
COLLECTIVE_HEAD_RE = re.compile(
    r"^\s*(?:(?:the|my|our)\s+)?(?:whole\s+|entire\s+)?"
    r"(?P<who>everyone|everybody|every\s+(?:marshal|corps|general|commander|man)"
    r"|all(?:\s+of\s+(?:you|them))?(?:\s+(?:my|the|our))?(?:\s+(?:marshals|corps|generals|commanders|men|of\s+you))?"
    r"|(?:grande\s+)?arm[eé]e|army|marshals|generals)"
    r"\s*[,:]?\s+(?P<rest>[A-Za-z].*)$",
    re.IGNORECASE)

# The verbs a collective fans out on. An attack is ONE battle (the muster
# seats the rest), a retreat is the general retreat already, and the
# economy / meta / Cabinet verbs are nobody's corps.
GROUPABLE_ACTIONS = frozenset({
    "fortify", "unfortify", "drill", "defend", "hold", "move", "scout", "wait",
    "form_square", "garrison",
})
GROUPABLE_STRATEGIC = frozenset({"MOVE_TO", "SUPPORT", "HOLD", "PURSUE"})
ARMY_STRATEGIC = frozenset({"MOVE_TO", "SUPPORT", "PURSUE"})

_THIRD_PERSON = {
    "marches": "march", "moves": "move", "follows": "follow", "fortifies": "fortify",
    "holds": "hold", "drills": "drill", "scouts": "scout", "pursues": "pursue",
    "supports": "support", "advances": "advance", "withdraws": "withdraw",
    "digs": "dig", "entrenches": "entrench", "waits": "wait", "defends": "defend",
    "garrisons": "garrison", "chases": "chase", "goes": "go", "heads": "head",
}


def collective_head(text: str) -> Optional[Dict[str, str]]:
    """``{"who", "rest"}`` when the line addresses the army as a whole, with
    the order's words after the head normalised to the second person ("the
    army marches on Swabia" -> "march to Swabia")."""
    m = COLLECTIVE_HEAD_RE.match(text or "")
    if not m:
        return None
    rest = m.group("rest").strip()
    words = rest.split()
    if words:
        first = words[0].lower()
        if first in _THIRD_PERSON:
            words[0] = _THIRD_PERSON[first]
        rest = " ".join(words)
    rest = re.sub(r"^(march|move|advance|head)\s+(?:on|upon|for|towards?)\s+", r"\1 to ", rest, flags=re.I)
    return {"who": m.group("who"), "rest": rest}


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
    return int((getattr(world, "nation_authority", {}) or {}).get(nation, 75))


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
    "events", "waiting"}``: `question` is the member result that asked, with
    the rest of the members left in the stash on the world."""
    from backend.main import _result_carries_question
    from backend.commands.state_probe import order_state_refusal
    rest = stash["rest"]
    action = stash["action"]
    strategic_type = stash.get("strategic_type")
    army = bool(stash.get("army"))
    band = stash.get("band")
    lines: List[str] = []
    events: List[Any] = []
    members: List[str] = list(stash["members"])
    while members:
        name = members[0]
        marshal = world.get_marshal(name)
        if marshal is None or int(getattr(marshal, "strength", 0) or 0) <= 0:
            members.pop(0)
            continue
        verb = _probe_verb(action, strategic_type, rest)
        if not army:
            price = _price(world, marshal, action, strategic_type)
            if int(getattr(world, "actions_remaining", 0) or 0) < price:
                break
        reason = order_state_refusal(world, marshal, verb) if verb in _probe_verbs() else ""
        if reason:
            members.pop(0)
            lines.append(f"{_display(name)} — {reason}.")
            continue
        if army and band == "heard":
            # 50–69: a marshal who WOULD object refuses the Staff's word.
            doubt = _would_object(world, marshal, strategic_type, parsed_target=stash.get("target"), rest=rest)
            if doubt:
                members.pop(0)
                lines.append(f"{_display(name)} will not march on the Staff's word — "
                             f"he answers you in person; order him yourself.")
                continue
        members.pop(0)
        line = f"{name}, {rest}"
        try:
            parsed = parser.parse(line, llm_game_state, world=world)
        except Exception as exc:
            report(exc, "group_orders._run_members: parser.parse")
            lines.append(f"{_display(name)} — the order could not be read for him.")
            continue
        if not parsed.get("success"):
            lines.append(f"{_display(name)} — {_first_sentence(parsed.get('error') or parsed.get('message') or 'the order could not be read for him')}")
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
            continue
        if isinstance(result, dict) and result.get("events"):
            events.extend(result.get("events") or [])
        if _result_carries_question(result):
            stash["members"] = members
            stash["lines"] = list(stash.get("lines", [])) + lines
            stash["events"] = list(stash.get("events", [])) + events
            world._pending_group = stash
            return {"lines": lines, "question": result, "events": events, "waiting": members,
                    "asker": name}
        said = _first_sentence(result.get("message", ""))
        if army and band == "carries" and _would_object(
                world, marshal, strategic_type, parsed_target=stash.get("target"), rest=rest):
            said += " (He had his doubts; the Staff's order carries.)"
        lines.append(f"{_display(name)}: {said}" if said else f"{_display(name)}: done.")
    world._pending_group = None
    return {"lines": lines, "question": None, "events": events, "waiting": members, "asker": ""}


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


def _head_line(world, stash: Dict[str, Any], names: List[str]) -> str:
    rest = stash["rest"]
    n = len(names)
    if stash.get("army"):
        line = (f"The Grand Quartier Général carries the Emperor's order — {ARMY_ORDER_AP} actions, "
                f"the whole column: {n} corps within {ARMY_COLUMN_REACH} provinces of the Emperor, "
                f"'{rest}'.")
        if stash.get("note"):
            line += " " + stash["note"]
        return line
    total = 0
    for name in names:
        m = world.get_marshal(name)
        if m is not None:
            total += _price(world, m, stash["action"], stash.get("strategic_type"))
    have = int(getattr(world, "actions_remaining", 0) or 0)
    line = (f"The order goes to the army, corps by corps — {n} corps, {total} action"
            f"{'s' if total != 1 else ''} for the {have} in hand: '{rest}'.")
    if stash.get("note"):
        line += " " + stash["note"]
    return line


def _waiting_line(waiting: List[str]) -> str:
    if not waiting:
        return ""
    shown = ", ".join(_display(n) for n in waiting)
    return (f"Nothing left for {shown} today — the pool is spent; they take the order "
            f"with tomorrow's actions, or name the corps that matter most.")


def _compose(stash: Dict[str, Any], run: Dict[str, Any], head: str, *, resumed: bool) -> str:
    parts: List[str] = []
    if not resumed:
        parts.append(head)
    parts.extend(run["lines"])
    q = run.get("question")
    if q is not None:
        asker = _display(run.get("asker") or "")
        msg = str(q.get("message") or "")
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
    command = (parsed or {}).get("command") or {}
    if command.get("marshal") or not parsed.get("success"):
        return None
    head = collective_head(command_text)
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
        "raw": command_text,
    }
    army_refusal = ""
    if p_type in ARMY_STRATEGIC:
        army_refusal = _army_gate(world, stash, field, leader)
        if army_refusal:
            stash["note"] = army_refusal
    head_line = _head_line(world, stash, stash["members"])
    stash["head"] = head_line
    if stash["army"]:
        for _ in range(ARMY_ORDER_AP):
            world.use_action("strategic")
    run = _run_members(world, game_state, parser, executor, llm_game_state, stash)
    message = _compose(stash, run, head_line, resumed=False)
    q = run.get("question")
    result: Dict[str, Any] = {"success": True, "message": message,
                              "group": {"army": stash["army"], "members": stash["members"],
                                        "asked": bool(q)},
                              "events": run.get("events") or []}
    if q is not None:
        for key, value in q.items():
            if key in ("message", "new_state", "events"):
                continue
            result[key] = value
    result["action_info"] = {
        "cost": 0, "remaining": int(getattr(world, "actions_remaining", 0) or 0),
        "turn_advanced": False, "new_turn": None,
    }
    result["action_summary"] = world.get_action_summary()
    return result


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
                           "waiting": run.get("waiting") or []}
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
    info = response.get("action_info")
    if isinstance(info, dict):
        info["remaining"] = int(getattr(world, "actions_remaining", 0) or 0)
    response["action_summary"] = world.get_action_summary()


def merge_into_result(result: Dict[str, Any], cont: Optional[Dict[str, Any]], world) -> None:
    """The same fold for an executor RESULT on the /command road (a typed
    answer that went through the stages)."""
    if not cont or not isinstance(result, dict):
        return
    attach(result, cont, world)

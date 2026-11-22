"""The take-back (row PW part 3, November 19, 2026): the last order, taken back.

The player's word after his first playtest was a game that is not clunky; a
slipped click — the wrong general, the wrong province, the wrong purchase —
had no way back (the typed `undo` got Berthier's shrug). An order can be
taken back while taking it back would un-know nothing and un-roll nothing:

  * it was an ORDER that went through and changed the board (a question, a
    refusal and an answer to a dialogue are none);
  * no battle was fought and no province changed hands;
  * it raised no question (an objection, an interrupt, a capture choice, a
    dialogue, a popup);
  * it showed the player nothing new — the fog's ledger reads as it did
    everywhere but on his own soil;
  * it touched nothing outside the order's own books (`ORDER_KEYS` — a save
    key outside them moving is read as "more happened than an order");
  * the turn did not end, and nothing else has been done since.

Orders kept one after another stack (`MAX_KEPT`): a second take-back steps
back the order before, as an editor's undo does. An order that stands empties
the stack — nothing before it can be reached past it.

The snapshot is the world's own save dict (`WorldState.to_dict`, about 6 ms
on the 1805 board) and the restore is the turn's own
(`WorldState._restore_from_snapshot`, about 10 ms). The dice come back by
construction on a seeded campaign (WS-11: a stream is built from the seed,
the turn and `battles_this_turn`); the ambient `random` state is carried for
the historical seed. The slot lives in this module and never in the save: a
loaded game has nothing to take back, and a slot remembers the world it was
taken from.

`a_taken_order_can_be_taken_back` is the seam: down, nothing is offered and
the typed `undo` keeps Berthier's shrug.
"""
from __future__ import annotations

import json
import random
import re
import weakref
from typing import Any, Dict, List, Optional

from backend.errors import report


def a_taken_order_can_be_taken_back() -> bool:
    """The seam (row PW part 3). One line to reverse: return False."""
    return True


# The books an order writes: the day's two pools, the purse, the corps, the
# provinces' own works, the fog (own soil only — read apart), the two logs.
# A save key outside these moving means more happened than an order (a
# treaty, a letter, a court's answer, a battle's books), and it stands.
ORDER_KEYS = frozenset({
    "actions_remaining", "admin_actions_remaining",
    "command_history", "event_log",
    "gold", "gold_spent_this_turn", "nation_gold",
    "manpower_pools", "manpower_spent_this_turn",
    "marshals", "regions", "intel",
    "strategic_orders", "notifications",
    "last_order_of_the_day",
    # Row IC, directives: an army formed or disbanded and a war's goal set are
    # the player's own bookkeeping — an order's books, taken back with it.
    "armies", "war_goals",
    # Row IC (the sibling of "one order to several is one Take-back unit"): a
    # small concern a marshal VOICES as he takes an order (no popup, no answer
    # asked — the turn's list of them, read only as the turn ends) is that
    # order's own; before this the remark alone made the order stand. A
    # concern that asks a question is a question, and still stands.
    "mild_concerns_this_turn",
    # Row IC, Session 3b (IC3B-1, and Session 3's sibling): setting a man on
    # his own while a bold senior stands idle writes that senior's resentment
    # in the court's book of incidents (`precedence.note`, "passed_over") — the
    # order's own consequence, un-written with it. Before this the note alone
    # made the order stand ("More than the order itself followed from it"),
    # for one man and for an army's task alike, while the list promised "Take
    # back undoes it all". (A battle's entries in the book never reach here:
    # a battle stands by its own verdict.)
    "marshal_ledger",
})
# Asked or answered: nothing an order changes, and nothing to take back — the
# log of what was typed, the counsel's memory, and help's own bookkeeping (a
# hint or a lesson marked shown: "what if Ney attacks Mack" marks the muster
# hint, and a question must never close a kept order).
INERT_KEYS = frozenset({"command_history", "talleyrand_counsel_memory"})


def _inert(key: str) -> bool:
    return key in INERT_KEYS or key.endswith(("_shown", "_seen")) or "tutorial" in key \
        or "first_open" in key or "hint" in key


# A reply carrying any of these raised a question or fought a battle.
QUESTION_KEYS = (
    "pending_objection", "pending_interrupt", "requires_input", "awaiting_response",
    "pending_capture_choice", "capture_data", "diplomatic_dialogue", "ai_proposal",
    "clarification", "pending_clarification", "choices",
)
BATTLE_KEYS = ("battle_report", "battle_diorama", "combat_result", "battle_day",
               "glorious_charge", "enemy_phase", "game_over")

# The POSTs that leave a kept order kept: the command road itself, the
# take-back, and the ones that move nothing on the board (a save, a line of
# help marked read, a notice dismissed, a preview, the parser's setting).
KEEPING_POSTS = frozenset({"/command", "/undo", "/save", "/first_open", "/notifications/dismiss",
                           "/diplomatic_preview", "/config/llm"})

# The typed line that asks for it ("undo", "take that back", "oops").
_LINE_RX = re.compile(
    r"^\s*(?:please\s+)?(?:undo|un-do|oops|take\s+(?:that|it|this)\s+back"
    r"|take\s+back\s+(?:that|the\s+last|my\s+last)(?:\s+(?:order|move|command))?)"
    r"(?:\s+(?:that|it|this|that\s+order|that\s+move|the\s+last\s+order|my\s+last\s+order))?"
    r"\s*[.!]*\s*$", re.IGNORECASE)


def is_take_back_line(text: str) -> bool:
    return bool(_LINE_RX.match(str(text or "")))


# Why an order stands — the words the button's hover and the typed `undo` say.
WHY = {
    "nothing": "There is no order to take back.",
    "question": "That order raised a question; it stands.",
    "battle": "That order was fought out; a battle cannot be taken back.",
    "ground": "That order took or lost ground; it stands.",
    "fog": "That order showed you new ground; it stands.",
    "more": "More than the order itself followed from it; it stands.",
    "turn": "The turn has moved on.",
    "since": "Something else has been done since that order.",
    "refused": "That order was not carried out; there is nothing to take back.",
    "off": "Orders cannot be taken back in this game.",
}

# The kept orders, the newest last: each {"world", "turn", "snapshot", "rng",
# "words"}; and why the last order stands when none is kept.
MAX_KEPT = 12
_KEPT: List[Dict[str, Any]] = []
_WHY_NOT: str = "nothing"


def _same(a: Any, b: Any) -> bool:
    if a is b:
        return True
    try:
        return json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
    except (TypeError, ValueError) as exc:
        report(exc, "take_back._same: a save value that will not serialize")
        return False


def _changed_keys(before: Dict[str, Any], after: Dict[str, Any]) -> set:
    return {k for k in set(before) | set(after) if not _same(before.get(k), after.get(k))}


def _friendly_soil(world) -> set:
    """The provinces whose fog an order may freshen without showing anything
    new: the player's own and those of the courts fighting beside him (his
    clients and allies — their soil is already his to read)."""
    player = getattr(world, "player_nation", "")
    friends = {player}
    try:
        for nation, row in (getattr(world, "vassals", {}) or {}).items():
            if isinstance(row, dict) and str(row.get("lord") or "") == player:
                friends.add(nation)
    except Exception as exc:
        report(exc, "take_back._friendly_soil: the vassal rows")
    return {name for name, region in (getattr(world, "regions", {}) or {}).items()
            if getattr(region, "controller", None) in friends}


def _controllers(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    regions = snapshot.get("regions") or {}
    if isinstance(regions, dict):
        return {name: (row or {}).get("controller") for name, row in regions.items() if isinstance(row, dict)}
    return {}


def mark(world) -> Optional[Dict[str, Any]]:
    """Before a command runs: the board as it stands (None with the seam down
    or no world)."""
    if world is None or not a_taken_order_can_be_taken_back():
        return None
    try:
        return {
            "snapshot": world.to_dict(),
            "rng": random.getstate(),
            "turn": int(getattr(world, "current_turn", 0) or 0),
            "friendly": _friendly_soil(world),
        }
    except Exception as exc:
        report(exc, "take_back.mark: the snapshot before a command")
        return None


def _verdict(world, before: Dict[str, Any], response: Dict[str, Any]) -> str:
    """"" when the order just run can be taken back, "inert" when the command
    changed nothing an order changes, else the key of `WHY` that says why it
    stands."""
    # Row IC, the directive: a request that only ASKED for the list of an order
    # to several corps (`directive` on the reply, nothing carried out — no
    # `group`) is no order at all: the kept orders stay kept.
    if response.get("directive") and not response.get("group"):
        return "inert"
    snapshot = before["snapshot"]
    after = world.to_dict()
    changed = {key for key in _changed_keys(snapshot, after) if not _inert(key)}
    if not changed:
        return "inert"
    if int(getattr(world, "current_turn", 0) or 0) != int(before["turn"]):
        return "turn"
    if any(response.get(key) for key in QUESTION_KEYS):
        return "question"
    if any(response.get(key) for key in BATTLE_KEYS) or "battles_this_turn" in changed \
            or "battle_history" in changed or "active_battles" in changed:
        return "battle"
    if not response.get("success"):
        return "refused"
    if _controllers(snapshot) != _controllers(after):
        return "ground"
    old_intel, new_intel = snapshot.get("intel") or {}, after.get("intel") or {}
    for name in set(old_intel) | set(new_intel):
        if name in before["friendly"]:
            continue
        if not _same(old_intel.get(name), new_intel.get(name)):
            return "fog"
    if "intel_grants" in changed:
        return "fog"
    if not changed <= ORDER_KEYS:
        return "more"
    return ""


def settle(world, before: Optional[Dict[str, Any]], response: Dict[str, Any], words: str) -> None:
    """After a command's reply is built: keep the order for a take-back, say
    why it stands, or leave the slot as it was (a question changes nothing).
    Never raises — a take-back that cannot be judged is not offered."""
    global _WHY_NOT
    if before is None or world is None or not isinstance(response, dict):
        return
    try:
        verdict = _verdict(world, before, response)
    except Exception as exc:
        report(exc, "take_back.settle: the verdict on the order just run")
        verdict = "more"
    if verdict == "inert":
        _top(world)   # (a stale stack — another world, another turn — is dropped here)
        return
    if verdict == "":
        _top(world)
        _KEPT.append({"world": weakref.ref(world), "turn": int(before["turn"]),
                      "snapshot": before["snapshot"], "rng": before["rng"],
                      "words": " ".join(str(words or "").split())[:80]})
        del _KEPT[:-MAX_KEPT]
        _WHY_NOT = ""
        return
    _KEPT.clear()
    _WHY_NOT = verdict


def _top(world) -> Optional[Dict[str, Any]]:
    """The newest kept order of THIS world's present turn; a stack kept for
    another world or an earlier turn is dropped."""
    global _WHY_NOT
    if not _KEPT:
        return None
    slot = _KEPT[-1]
    if world is None or slot["world"]() is not world \
            or slot["turn"] != int(getattr(world, "current_turn", 0) or 0):
        _KEPT.clear()
        _WHY_NOT = "turn"
        return None
    return slot


def forget(why: str = "since") -> None:
    """Anything else that moves the board (a popup's answer, a letter, a
    load, a new game) empties the stack."""
    global _WHY_NOT
    if _KEPT or _WHY_NOT == "":
        _WHY_NOT = why if why in WHY else "since"
    _KEPT.clear()


def new_board() -> None:
    """A world swapped in (a new game, a load): nothing is kept, and nothing
    was refused — the hover reads "There is no order to take back."."""
    global _WHY_NOT
    _KEPT.clear()
    _WHY_NOT = "nothing"


def offer(world) -> Dict[str, Any]:
    """What a reply tells the client: {"available", "words", "why", "kept"}."""
    if not a_taken_order_can_be_taken_back():
        return {"available": False, "words": "", "why": WHY["off"], "kept": 0}
    slot = _top(world)
    if slot is not None:
        return {"available": True, "words": slot["words"], "why": "", "kept": len(_KEPT)}
    return {"available": False, "words": "", "kept": 0,
            "why": WHY.get(_WHY_NOT or "nothing", WHY["nothing"])}


def take_back(world) -> Dict[str, Any]:
    """Put the board back as it stood before the newest kept order. Returns
    {"ok", "message", "words"}; that order leaves the stack either way."""
    global _WHY_NOT
    slot = _top(world) if a_taken_order_can_be_taken_back() else None
    if slot is None:
        return {"ok": False, "message": offer(world)["why"], "words": ""}
    words = str(slot["words"])
    _KEPT.pop()
    try:
        world._restore_from_snapshot(slot["snapshot"])
        random.setstate(slot["rng"])
        world.calculate_visibility()
    except Exception as exc:
        report(exc, "take_back.take_back: the restore", every=True)
        _KEPT.clear()
        _WHY_NOT = "more"
        return {"ok": False, "message": "The order could not be taken back.", "words": words}
    if not _KEPT:
        _WHY_NOT = "nothing"
    said = f"Taken back: “{words}”. " if words else "Taken back. "
    return {"ok": True, "words": words,
            "message": said + "The board stands as it did before that order, and its actions are yours again."}

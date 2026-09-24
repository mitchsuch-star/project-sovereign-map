"""CR-7-3 — THE RELAY: nothing is dropped in silence, and the tail comes back.

WHY THIS MODULE EXISTS
======================
CR-7-1 stopped a compound order's tail from REPLACING its head. What was
left was silence in three places, measured on the shipped 1805 boot
(`docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md` §CR-7-3):

* a REFUSED head lost its tail without a word (`Ney, march to Karaman, then
  Davout, fortify` → "Cannot enter Karaman" and nothing about Davout);
* the note never re-surfaced after `insist` / `trust` / `compromise` —
  the production comment at the drop site claimed it would, and it did not
  on any of the three arms;
* the value `dropped_sequel` was computed to build one string and thrown
  away: eight producers, ZERO consumers in the backend or the client.

And the tail that WAS reported was reported with an invitation — "must
follow as its own command" — that the user's own note of September 22, 2026
names as the wrong instruction: *"fortify and attack is a contradiction."*

THE RULES (SYSTEMS_REFERENCE.md §4 Stage 2c)
--------------------------------------------
1. The tail rides EVERY arm — success, refused head, objection,
   clarification, interrupt — as `dropped_sequel`, with ONE sentence that
   says what became of it (`relay_note`) and a `relay_kind`.
2. A tail is HANDED BACK for the player's seal (`relay_command`, the client
   fills the command line with it — it never sends) only when sending it
   NOW is coherent: kind ``ready``.
3. It is NOT handed back — named, never filled — when sending it now would
   undo the head: kind ``contradiction`` (a fortified / squared / drilling /
   defensive marshal told to move, or a standing HOLD / SUPPORT that any
   override verb would end); or when it would take the marshal's next turn
   where he stands rather than where his march ends: kind ``moment`` (the
   dissent's binding mitigation — a five-hop march outlives the player's
   memory of its tail, so the note names the moment and the ETA).
4. A refused head CANCELS the tail, and the tail is never promoted to a new
   head: kind ``refused_head``. The player wrote it to follow something that
   did not happen.
5. While the head is a QUESTION (objection / clarification / interrupt) the
   tail waits behind it: kind ``question``. It is stashed on the world for
   exactly one command's life (`world._pending_relay` — transient, never
   serialized, cleared at the turn boundary and by the next `/command`) and
   re-judged against the LIVE state when the answer lands.
6. There is nothing to cancel and nothing is queued. A relayed tail is an
   ordinary new command that pays its own AP when sent. The cross-turn order
   queue is retired by contract (CR-7-8).

GR5: the AI never types a compound, so it never sees a relay; a stash can
only be created by the player's own `/command`.
"""

import math
from typing import Dict, Optional

from backend.display_names import plural as _plural  # LV-9 (row EP F2)

# executor.py's `strategic_override_actions` — a same-marshal tail in this set
# ENDS a live standing order (measured: it wipes the order even on a command
# refused at 0 AP; the wipe is the executor's, this module only NAMES it).
ORDER_ENDING_ACTIONS = frozenset({"attack", "move", "defend", "fortify", "drill", "retreat"})
# Tails that MOVE the corps, against a head that committed it to stand.
MOVING_ACTIONS = frozenset({"attack", "move", "charge", "pursue", "retreat"})
MOVING_STRATEGIC_TYPES = frozenset({"MOVE_TO", "PURSUE"})
STANDING_STRATEGIC_TYPES = frozenset({"HOLD", "SUPPORT"})

RELAY_KINDS = ("ready", "moment", "contradiction", "refused_head", "question")


def stash(world, relay: Dict, marshal_name: Optional[str], head_action: Optional[str]) -> None:
    """Rule 5: keep the tail for exactly one command's life."""
    world._pending_relay = {
        "tail": relay["dropped_sequel"],
        "marshal": marshal_name,
        "head_action": head_action,
        "turn": int(getattr(world, "current_turn", 0) or 0),
    }


def pop(world) -> Optional[Dict]:
    pending = getattr(world, "_pending_relay", None)
    world._pending_relay = None
    return pending


def _tail_reading(parser, tail: str, llm_game_state) -> Dict:
    """What the tail would be if sent now — the mock chain's own deterministic
    read (never the LLM), plus the strategic routing table's type."""
    action = None
    target = None
    marshal = None
    strategic_type = None
    try:
        parsed = parser.llm.fast_parse(tail, llm_game_state)
        action = parsed.action if parsed.action != "unknown" else None
        target = parsed.target
        marshal = parsed.marshals[0] if parsed.marshals else None
    except Exception:
        pass
    try:
        from backend.ai.strategic_parser import _detect_strategic_type
        strategic_type = _detect_strategic_type(tail.lower())
    except Exception:
        pass
    return {"action": action, "target": target, "marshal": marshal,
            "strategic_type": strategic_type}


def _standing_state(marshal) -> Optional[str]:
    """Why a MOVING tail would undo the head, from the marshal's LIVE state —
    what actually happened, not what was typed (an objection's `trust` may
    have executed something else entirely)."""
    if getattr(marshal, "fortified", False):
        return "attacking or marching abandons the works he has just raised"
    if getattr(marshal, "square_formation", False):
        return "any other order breaks the square he has just formed"
    if getattr(marshal, "drilling", False):
        return "it would end the drill before it pays"
    stance = getattr(marshal, "stance", None)
    if getattr(stance, "value", stance) == "defensive":
        return "he would give up the defensive stance he has just taken"
    return None


def _eta_turns(marshal, order) -> int:
    path = list(getattr(order, "path", None) or [])
    rng = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    return max(1, int(math.ceil(len(path) / rng))) if path else 1


def _readdress(tail: str, tail_marshal: Optional[str], marshal_name: Optional[str]) -> str:
    if tail_marshal or not marshal_name:
        return tail
    return f"{marshal_name}, {tail}"


def build_relay(world, parser, llm_game_state, *, tail: str,
                marshal_name: Optional[str], head_action: Optional[str],
                result: Dict, question: bool, answered: bool = False) -> Dict:
    """Judge one dropped tail against the head's outcome and the live board.

    Returns ``{"dropped_sequel", "relay_kind", "relay_command", "relay_note"}``.
    ``relay_command`` is a string only for kind ``ready``.
    """
    tail = (tail or "").strip()
    reading = _tail_reading(parser, tail, llm_game_state)
    tail_marshal = reading["marshal"]
    same_marshal = (tail_marshal is None) or (marshal_name is not None
                                              and tail_marshal == marshal_name)
    marshal = world.get_marshal(marshal_name) if (world is not None and marshal_name) else None
    who = marshal_name or "the marshal"
    relay: Dict = {"dropped_sequel": tail, "relay_command": None}

    def done(kind: str, note: str, command: Optional[str] = None) -> Dict:
        relay["relay_kind"] = kind
        relay["relay_note"] = note
        relay["relay_command"] = command
        # The STANDALONE sentence — for a surface with no parser lead
        # before it (a clarification, an answer route): it must name the
        # tail itself. `relay_note` stays the second half for the /command
        # path, where `parser.sequel_note` has already named the tail.
        relay["relay_line"] = (
            note if f'"{tail}"' in note
            else f'One order at a time, Sire — "{tail}" waits behind it. {note}')
        return relay

    lead = (f'One order at a time, Sire — "{tail}" was waiting behind the question. '
            if answered else "")

    # Rule 5 — the head is a question the player has not yet answered.
    if question and not answered:
        asker = marshal_name or "Berthier"
        return done("question",
                    f"It waits behind the question {asker} has put to you. "
                    f"Answer, and it returns to the line; another order, or "
                    f"the turn's end, lets it go.")

    # Rule 4 — the head did not go out.
    if not (isinstance(result, dict) and result.get("success")):
        return done("refused_head",
                    f'One order at a time, Sire — and the first did not go out, '
                    f'so "{tail}", written to follow it, is not relayed.')

    tail_moves = (reading["action"] in MOVING_ACTIONS
                  or reading["strategic_type"] in MOVING_STRATEGIC_TYPES)
    tail_ends_order = (reading["action"] in ORDER_ENDING_ACTIONS
                       or reading["strategic_type"] is not None)

    if marshal is not None and same_marshal:
        order = getattr(marshal, "strategic_order", None)
        # Rule 3 — the moment: a live march or pursuit outlives this turn.
        if order is not None and order.command_type in MOVING_STRATEGIC_TYPES:
            if order.command_type == "PURSUE":
                return done("moment",
                            f"{lead}Sent now it would take {who}'s next turn where he "
                            f"stands, not where he runs {order.target} down. Give "
                            f"it when he has him.")
            try:
                from backend.commands.strategic import resolve_order_destination
                dest = resolve_order_destination(world, marshal, order)
            except Exception:
                dest = getattr(order, "target", "his destination")
            eta = _eta_turns(marshal, order)
            return done("moment",
                        f"{lead}Sent now it would take {who}'s next turn where he "
                        f"stands, not at {dest} — he reaches it in ~{_plural(int(eta), 'turn')}. "
                        f"Give it when he arrives.")
        # Rule 3 — a standing hold or support that the tail would end.
        if (order is not None and order.command_type in STANDING_STRATEGIC_TYPES
                and tail_ends_order):
            what = ("his standing hold" if order.command_type == "HOLD"
                    else f"his support of {order.target}")
            return done("contradiction",
                        f"{lead}Sent now it would undo the first: it would end "
                        f"{what}. Give it when you mean him to leave it.")
        # Rule 3 — a corps committed to stand, told to move.
        if tail_moves:
            reason = _standing_state(marshal)
            if reason:
                return done("contradiction",
                            f"{lead}Sent now it would undo the first: {reason}. "
                            f"Give it when you mean him to move.")

    # Rule 2 — coherent; on the line for the seal.
    command = _readdress(tail, tail_marshal, marshal_name)
    return done("ready",
                f"{lead}It is on the line — send it when you are ready.",
                command)


def let_go_line(pending: Dict) -> str:
    """CR-7-9: the word said when a stashed tail is let go — by a command
    that neither answered the question nor re-typed the tail, or by the
    turn's end. Rule 5 promised it would WAIT; it now says for how long,
    and the drop is never mute."""
    tail = str((pending or {}).get("tail") or "").strip()
    return (f'Berthier: "The order that waited behind the question — "{tail}" — '
            f'is let go with it. Give it again when you mean it."')


def attach(response: Dict, relay: Optional[Dict]) -> None:
    """Stamp the relay keys onto a response (or an executor result that will
    become one). `relay_command` is present only for kind ``ready`` so the
    client's fill is impossible on any other kind."""
    if not relay:
        return
    response["dropped_sequel"] = relay["dropped_sequel"]
    response["relay_kind"] = relay["relay_kind"]
    response["relay_note"] = relay["relay_note"]
    if relay.get("relay_command"):
        response["relay_command"] = relay["relay_command"]
    else:
        response.pop("relay_command", None)


def append_note(response: Dict, relay: Optional[Dict], *, standalone: bool) -> None:
    """Put the relay's sentence where the player reads it. `standalone` is
    the answer routes and the clarifications (no parser warning precedes
    it, so the line names the tail itself); the /command path already
    carries `sequel_note`'s lead, so only the second half follows."""
    if not relay:
        return
    note = relay["relay_note"]
    message = (response.get("message") or "").rstrip()
    if standalone or relay["relay_kind"] == "refused_head":
        line = f"Berthier: \"{relay.get('relay_line') or note}\""
        response["message"] = f"{message}\n\n{line}".strip() if message else line
        return
    # The parser's own sentence ends `… waits behind it."` — the second half
    # is spliced inside the same quotation so the player reads ONE remark.
    lead = 'waits behind it."'
    if lead in message:
        response["message"] = message.replace(lead, f"waits behind it. {note}\"", 1)
    else:
        response["message"] = f"{message}\n\nBerthier: \"{note}\"".strip()

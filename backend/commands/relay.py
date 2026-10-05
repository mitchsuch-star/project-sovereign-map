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

from backend.display_names import order_target_display
import math
import re
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


def _eta_turns(marshal, order, current_turn=None) -> int:
    """CRT-4-X1 (SR-6a): the ONE clock, read before the tick (the relay
    judges a tail at issue time, so a just-issued march counts the skipped
    issuing tick). Lever down = ceil(len / range), one short on that march."""
    from backend.commands import strategic as _road
    path = list(getattr(order, "path", None) or [])
    rng = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    if _road.ONE_CLOCK and current_turn is not None and path:
        return max(1, int(_road.order_turns_remaining(
            order, int(current_turn), movement_range=rng, before_tick=True)))
    return max(1, int(math.ceil(len(path) / rng))) if path else 1


def _readdress(tail: str, tail_marshal: Optional[str], marshal_name: Optional[str]) -> str:
    if tail_marshal or not marshal_name:
        return tail
    return f"{marshal_name}, {tail}"


def build_relay(world, parser, llm_game_state, *, tail: str,
                marshal_name: Optional[str], head_action: Optional[str],
                result: Dict, question: bool, answered: bool = False,
                independent: bool = False) -> Dict:
    """Judge one dropped tail against the head's outcome and the live board.

    Returns ``{"dropped_sequel", "relay_kind", "relay_command", "relay_note"}``.
    ``relay_command`` is a string only for kind ``ready``.

    ``independent`` (CQ-8 / CQ-38, Score Finish Step 7 slice 5a): the tail is
    a second marshal's OWN order, parallel to the head rather than written to
    follow it ("grant Ney and Murat a rente", "Ney and Soult, fortify") — so
    the head's refusal does not cancel it (Rule 4 is the sequence's rule).
    """
    tail = (tail or "").strip()
    reading = _tail_reading(parser, tail, llm_game_state)
    tail_marshal = reading["marshal"]
    same_marshal = (tail_marshal is None) or (marshal_name is not None
                                              and tail_marshal == marshal_name)
    marshal = world.get_marshal(marshal_name) if (world is not None and marshal_name) else None
    who = marshal_name or "the marshal"
    # `tail_action` is read by the second-name rule (CQ-38's met rente); it
    # is never stamped on a response (`attach` copies named keys only).
    relay: Dict = {"dropped_sequel": tail, "relay_command": None,
                   "tail_action": reading["action"]}

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
    if not independent and not (isinstance(result, dict) and result.get("success")):
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
                            f"stands, not where he runs {order_target_display(order.target)} down. Give "
                            f"it when he has him.")
            try:
                from backend.commands.strategic import resolve_order_destination
                dest = resolve_order_destination(world, marshal, order)
            except Exception:
                dest = getattr(order, "target", "his destination")
            eta = _eta_turns(marshal, order,
                             int(getattr(world, "current_turn", 0) or 0))
            return done("moment",
                        f"{lead}Sent now it would take {who}'s next turn where he "
                        f"stands, not at {dest} — he reaches it in ~{_plural(int(eta), 'turn')}. "
                        f"Give it when he arrives.")
        # Rule 3 — a standing hold or support that the tail would end.
        if (order is not None and order.command_type in STANDING_STRATEGIC_TYPES
                and tail_ends_order):
            what = ("his standing hold" if order.command_type == "HOLD"
                    else f"his support of {order_target_display(order.target)}")
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


def second_name_relay_note(world, second: str, order: str, *,
                           spliced: bool = True) -> str:
    """CQ-8 / CQ-38 (Score Finish Step 7 slice 5a): the second man's own
    order, on the line for the seal — never sent by the game. Priced when it
    is his SUPPORT of the first (the order the muster names), from
    `Marshal.strategic_order_ap`, the executor's own source; the same order
    re-addressed is priced by the executor when sent, so no figure is quoted
    for it here (a quote that could differ from the bill is worse than none).

    ``spliced``: the parser's sentence ("<second>'s own waits behind it.")
    stands before it — the head went out. Otherwise (the head was refused and
    the parser's sentence was not printed) the note names him itself."""
    price = ""
    if re.search(r",\s*support\s+", order or "", flags=re.IGNORECASE):
        marshal = world.get_marshal(second) if world is not None else None
        if marshal is not None:
            try:
                ap = int(marshal.strategic_order_ap(order_type="SUPPORT"))
            except Exception:
                ap = 0
            if ap > 0:
                price = f" ({_plural(ap, 'action')} when sent)"
    if spliced:
        return (f'His order is "{order}"{price}: it is on the line — send it '
                f'when you are ready.')
    return (f'You named {second} too, Sire — his own order, "{order}"{price}, '
            f'is on the line; send it when you are ready.')


def second_name_refused_note(lead: str, second: str, order: str) -> str:
    """CQ-8: his SUPPORT of a first order that did not go out is not relayed
    — there is nothing yet for him to support."""
    return (f"{lead}'s order did not go out, Sire, so {second}'s — "
            f'"{order}" — is not relayed either.')


def muster_counts(result: Dict, name: str) -> bool:
    """CQ-8: the head's muster already counts this marshal as marching."""
    rows = ((result or {}).get("muster_preview") or {}).get("rows") or []
    return any(isinstance(r, dict) and r.get("marshal") == name and r.get("will_join")
               for r in rows)


def second_name_unneeded(world, second: str, tail_action: Optional[str],
                         result: Dict, lead: str) -> Optional[str]:
    """CQ-8 / CQ-38: the second man needs no order of his own — the muster
    already counts him as marching, or the rente the line would grant him
    changes nothing (`dotation.rente_would_change`, the one "is he met"
    source the executor refuses by). The clause said instead of a relay, so
    the line never holds an order the game would refuse. None otherwise."""
    if muster_counts(result, second):
        return f"{second} marches with {lead} already — the muster counts him."
    if tail_action == "grant_pension" and world is not None:
        marshal = world.get_marshal(second)
        if marshal is not None:
            try:
                from backend.game_logic.dotation import rente_would_change
                if not rente_would_change(marshal, world):
                    return f"{second}'s expectation is met already — he needs no rente."
            except Exception:
                return None
    return None


def second_name_others_clause(result: Dict, others) -> str:
    """CQ-8: every further marshal the line named — marching already, or
    needing his own order (one clause each; empty when none)."""
    bits = [(f"{o} marches already" if muster_counts(result, o)
             else f"{o} needs his own order") for o in (others or [])]
    return (" " + "; ".join(bits) + ".") if bits else ""


def splice_second_name(response: Dict, second: str, sentence: str) -> None:
    """Put a second-name sentence where the player reads it: in place of the
    parser's "<second>'s own waits behind it." when that was printed (the
    head went out), else as its own remark naming him."""
    waits = f"{second}'s own waits behind it."
    message = response.get("message") or ""
    if waits in message:
        response["message"] = message.replace(waits, sentence, 1)
    else:
        line = f"You named {second} too, Sire: {sentence}"
        response["message"] = f"{message}\n\nBerthier: \"{line}\"".strip()


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

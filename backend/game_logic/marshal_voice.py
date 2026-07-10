"""Marshal voice banks — W6-5 The Literal Doctrine.

The literal marshal's register in ONE place (voice ownership rule,
WAVE6_FUN_FACTOR_SPEC §14): order acknowledgments, completion reports,
and the no-march fidelity lines all quote or orbit the player's own words
(`StrategicOrder.original_command`, the rider-(d) substrate).

Everything here is deterministic (GR6): variants rotate by a stable key
(text length + turn), never RNG — identical inputs always produce the
same line.
"""

from typing import List

# ── Acknowledgment: the order is repeated back, verbatim ──
LITERAL_ACK: List[str] = [
    "\"{order}.\" It will be done exactly, Sire.",
    "\"{order}.\" No more and no less.",
    "\"{order}.\" Understood to the letter.",
]

# ── Completion: the order is quoted, the outcome stated, instruction awaited ──
LITERAL_COMPLETE: List[str] = [
    "The order was \"{order}\". {outcome} I await further instruction.",
    "\"{order}\" — executed as written. {outcome} Awaiting your next word.",
    "As ordered: \"{order}\". {outcome} {name} stands ready for instruction.",
]

# ── The no-march tell: he heard the guns and held to his letter ──
# Variant 0 preserves the shipped reinforcement non-arrival line verbatim
# (it was the audit's best line — "revealed the rule three battles late";
# now the muster preview reveals it BEFORE, and this bank keeps the voice).
LITERAL_NO_MARCH: List[str] = [
    "{name} continues to follow standing orders. "
    "The sound of cannon fire grows louder behind him.",
    "{name} holds to the letter of his orders — the guns do not move him.",
    "{name} does not stir. His written orders say nothing of this battle.",
]


def _pick(bank: List[str], key: int) -> str:
    return bank[key % len(bank)]


def _clean_order_text(order_text: str) -> str:
    """Strip trailing punctuation so the quote reads cleanly in-template."""
    return (order_text or "").strip().rstrip(".!").strip()


def literal_ack(order_text: str, turn: int) -> str:
    """Acknowledgment line at order creation — quotes the verbatim command."""
    order = _clean_order_text(order_text)
    return _pick(LITERAL_ACK, len(order) + int(turn)).format(order=order)


def literal_completion(order_text: str, outcome: str, name: str,
                       turn: int) -> str:
    """Completion report — quotes the order, states the outcome plainly."""
    order = _clean_order_text(order_text)
    outcome_text = (outcome or "Done.").strip()
    if outcome_text and not outcome_text.endswith("."):
        outcome_text += "."
    return _pick(LITERAL_COMPLETE, len(order) + int(turn)).format(
        order=order, outcome=outcome_text, name=name)


def literal_no_march(name: str, key: int = 0) -> str:
    """The fidelity tell when a literal marshal ignores nearby guns."""
    return _pick(LITERAL_NO_MARCH, int(key)).format(name=name)


# ════════════════════════════════════════════════════════════════════════
# W6-5 §7.2.4 — the fidelity beat: pure narration of a literal marshal
# holding to his letter while the world shifts around it. NOT an
# interrupt, no choice, no trust change. Cap 1 per marshal per turn.
# ════════════════════════════════════════════════════════════════════════

def emit_literal_fidelity_events(world) -> list:
    """Per-turn scan: literal marshals WITH an active order whose context
    materially changed this turn (bounded — marshals-with-orders only,
    GR8-safe). Logs a `literal_fidelity` event and returns dispatch-ready
    dicts (message + nation keys for the turn-events whitelist filter).
    """
    events = []
    window_start = world.current_turn - 1
    # This turn's battles + captures, one pass over the recent window.
    recent_battles = []
    recent_captures = set()
    for e in world.event_log:
        if e.get("turn", 0) < window_start:
            continue
        if e.get("type") == "battle":
            recent_battles.append(e)
        elif e.get("type") == "region_captured":
            recent_captures.add(e.get("region", ""))

    for marshal in world.marshals.values():
        if getattr(marshal, "personality", "") != "literal":
            continue
        order = getattr(marshal, "strategic_order", None)
        if order is None or marshal.strength <= 0:
            continue

        region = world.get_region(marshal.location)
        adjacent = set(region.adjacent_regions) if region else set()
        message = ""

        # (a) A battle involving his own nation raged NEXT DOOR and he
        #     did not move — the visible cost/virtue of the doctrine.
        if not getattr(marshal, "moved_this_turn", False):
            for b in recent_battles:
                if b.get("location") not in adjacent:
                    continue
                if marshal.nation not in (b.get("attacker_nation"),
                                          b.get("defender_nation")):
                    continue
                message = (
                    f"{marshal.name} holds at {marshal.location}, per your "
                    f"orders — the guns at {b.get('location')} did not "
                    f"move him."
                )
                break

        # (b) His PURSUE/SUPPORT quarry shifted to a different region.
        if (not message
                and order.command_type in ("PURSUE", "SUPPORT")
                and not getattr(marshal, "moved_this_turn", False)):
            quarry = world.marshals.get(order.target)
            snapshot = getattr(order, "target_snapshot_location", None)
            if (quarry is not None and snapshot
                    and quarry.location != snapshot):
                message = (
                    f"{marshal.name}'s quarry has shifted to "
                    f"{quarry.location}, Sire — he follows the letter of "
                    f"your order, not his instincts."
                )

        # (c) His MOVE_TO destination changed hands mid-march.
        if (not message and order.command_type == "MOVE_TO"
                and order.target in recent_captures):
            message = (
                f"{marshal.name} marches on {order.target} as ordered — "
                f"though its colours have changed hands."
            )

        if not message:
            continue

        event = {
            "type": "literal_fidelity",
            "marshal": marshal.name,
            "nation": marshal.nation,
            "location": marshal.location,
            "order_type": order.command_type,
            "message": message,
        }
        world.log_event(dict(event))
        events.append(event)

    return events

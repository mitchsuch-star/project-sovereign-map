"""Marshal voice banks — W6-5 The Literal Doctrine + Tier 1 (position 9).

The PLAYER marshal's register in ONE place (voice ownership rule,
WAVE6_FUN_FACTOR_SPEC §14 — enemy marshals stay owned by enemy_voice.py,
named diplomats by the Voice Bible). The literal third (W6-5): order
acknowledgments, completion reports, and the no-march fidelity lines all
quote or orbit the player's own words (`StrategicOrder.original_command`,
the rider-(d) substrate). MARSHAL VOICE TIER 1 (Aug 8, 2026 — ROADMAP
position 9) completes the trio on the proven enemy_voice.py pattern:
aggressive + cautious acknowledgment/completion banks at the same seams,
and post-battle lines for the player's own commander in all three
registers (`battle_report.marshal_voice`, the enemy_voice mirror).

Everything here is deterministic (GR6): variants rotate by a stable key
(text length + turn, or the region's serialized battle count), never RNG —
identical inputs always produce the same line. Zero LLM cost, mock-safe.
"""

from typing import Dict, List, Optional

from backend.display_names import humanize_entity_name

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


# ════════════════════════════════════════════════════════════════════════
# MARSHAL VOICE TIER 1 (position 9, Aug 8 2026) — the other two thirds.
#
# 1) POST-BATTLE VOICE: the player's own commander gets one line in his
#    register after a battle — the exact mirror of enemy_voice.py
#    (situations from the PLAYER commander's perspective, named marquee
#    overrides, deterministic rotation by the region's serialized battle
#    count). Rides `battle_report.marshal_voice`, display-only.
# 2) ACKNOWLEDGMENT + COMPLETION: aggressive and cautious marshals answer
#    a standing order in their own register at the same two seams the
#    literal already owns (strategic_executor ack, strategic completion).
#    The literal keeps his verbatim-quote doctrine — these banks return ""
#    for him so W6-5 ownership is undisturbed.
# ════════════════════════════════════════════════════════════════════════

# Situations, always from the PLAYER commander's perspective:
#   carried_the_field — he attacked and won
#   held_the_line     — he defended and held/won
#   lost_ground       — he lost the field (either side)
#   driven_back       — he was forced from the field
#   stalemate         — neither side yielded
OWN_VOICE_SITUATIONS = ("carried_the_field", "held_the_line", "lost_ground",
                        "driven_back", "stalemate")

_OWN_PERSONALITY_LINES: Dict[str, Dict[str, List[str]]] = {
    "aggressive": {
        "carried_the_field": [
            "The field is ours! Give me leave and I will take the next one "
            "before dusk.",
            "They broke like green wood, Sire. I want the pursuit.",
            "A hard charge settles most arguments. It settled this one.",
        ],
        "held_the_line": [
            "They came, they bled, they left. I would have preferred to "
            "follow them.",
            "We held — though my sword-arm calls it half a battle.",
            "Let them come again with more men. The result will travel "
            "faster.",
        ],
        "lost_ground": [
            "We were checked — it will not stand. Give the word and I "
            "return the favor.",
            "A borrowed field, Sire. I mean to collect with interest.",
            "They had the ground and the luck. Luck runs out.",
        ],
        "driven_back": [
            "We fell back with our teeth still in, Sire. They will feel "
            "them again.",
            "A withdrawal, not a defeat. My temper survives intact.",
            "Driven from a field. It is not a habit I intend to form.",
        ],
        "stalemate": [
            "Neither side yielded. Unfinished business sits badly with me.",
            "A drawn field insults both armies. Let me finish it.",
            "We traded blood for nothing. I want tomorrow.",
        ],
    },
    "cautious": {
        "carried_the_field": [
            "The field is ours and the army still stands whole — both "
            "matter, Sire.",
            "Victory, at an acceptable price. The pickets are already "
            "posted.",
            "We won because the ground was right. I chose it so.",
        ],
        "held_the_line": [
            "The position held, as prepared positions do.",
            "They paid for every yard and kept none. Sound arithmetic.",
            "We held. The butcher's bill is theirs, not ours.",
        ],
        "lost_ground": [
            "We lost the field but kept the army — the second is harder "
            "to replace.",
            "I yielded ground rather than men, and stand ready to be "
            "judged on it.",
            "A reverse, Sire. I have already chosen the next position.",
        ],
        "driven_back": [
            "We were driven, but in order — the corps is whole and still "
            "dangerous.",
            "I gave ground to save the army. Time will return the ground.",
            "A retreat conducted properly is a battle postponed.",
        ],
        "stalemate": [
            "No decision — which favors whoever husbands his men better. "
            "That is us.",
            "They gained nothing and paid for the privilege. I can "
            "continue this indefinitely.",
            "An indecisive field. I decline to waste men decorating it.",
        ],
    },
    "literal": {
        "carried_the_field": [
            "The objective is taken. Casualty returns follow within the "
            "hour.",
            "The field is ours, as ordered. Awaiting further instruction.",
            "Executed. Their dispositions were insufficient; mine were "
            "yours.",
        ],
        "held_the_line": [
            "The position was held. The line stands where you drew it.",
            "Orders were to hold. The order is fulfilled.",
            "The attack was received and repelled. Nothing was improvised.",
        ],
        "lost_ground": [
            "The position could not be held with the forces assigned. I "
            "await revised instructions.",
            "The field is lost. I record the reverse without ornament.",
            "The returns are attached, Sire. They speak plainly enough.",
        ],
        "driven_back": [
            "Withdrawal conducted in good order. The army is intact.",
            "The line was forced. I have re-formed as regulation "
            "prescribes.",
            "I retire in accordance with necessity, not inclination.",
        ],
        "stalemate": [
            "I have recorded the engagement as indecisive, which it was.",
            "Both lines remain where they stood. Nothing further to "
            "report.",
            "No decision was reached. The returns will say precisely that.",
        ],
    },
}

# Marquee player marshals override the personality default when a row
# exists for the situation (the enemy_voice named-row idiom).
_OWN_NAMED_LINES: Dict[str, Dict[str, List[str]]] = {
    "Ney": {
        "carried_the_field": [
            "They stood, Sire. Briefly.",
            "The bravest of the brave was first through their line — ask "
            "the line.",
        ],
        "held_the_line": [
            "They found me standing exactly where I said I would be.",
        ],
        "driven_back": [
            "I was the last man off that field, Sire. I always am.",
        ],
    },
    "Davout": {
        "carried_the_field": [
            "The Third Corps does not require luck, Sire. Merely orders.",
            "Precision carried it. It usually does.",
        ],
        "held_the_line": [
            "They mistook discipline for weakness. The error has been "
            "corrected.",
        ],
        "stalemate": [
            "Iron does not tire. We continue when you wish.",
        ],
    },
    "Murat": {
        "carried_the_field": [
            "Was it not magnificent? The plume went first through their "
            "line, Sire.",
            "Their squares were a suggestion. My cavalry declined it.",
        ],
        "driven_back": [
            "Even the finest horseman must sometimes ride the other way.",
        ],
    },
}


def derive_own_situation(outcome: str, own_was_attacker: bool,
                         own_forced_retreat: bool) -> Optional[str]:
    """Map a battle outcome to the PLAYER commander's situation key —
    the exact mirror of enemy_voice.derive_enemy_situation."""
    if own_forced_retreat:
        return "driven_back"
    if outcome == "stalemate":
        return "stalemate"
    attacker_won = "attacker" in outcome and "victory" in outcome
    defender_won = "defender" in outcome and "victory" in outcome
    if own_was_attacker:
        if attacker_won:
            return "carried_the_field"
        if defender_won:
            return "lost_ground"
    else:
        if defender_won:
            return "held_the_line"
        if attacker_won:
            return "lost_ground"
    return None  # mutual destruction — no one left to speak


def pick_marshal_voice(name: str, personality: str, situation: str,
                       rotation_key: int = 0) -> str:
    """One line in the player commander's register ("" when none applies).

    Named rows (Ney, Davout, Murat) override the personality default;
    rotation is deterministic by `rotation_key` (the region's battle
    count, the enemy_voice idiom)."""
    if situation not in OWN_VOICE_SITUATIONS:
        return ""
    bank = _OWN_NAMED_LINES.get(name, {}).get(situation)
    if not bank:
        bank = _OWN_PERSONALITY_LINES.get(personality, {}).get(situation)
    if not bank:
        bank = _OWN_PERSONALITY_LINES["cautious"].get(situation, [])
    if not bank:
        return ""
    line = bank[int(rotation_key) % len(bank)]
    return f"{humanize_entity_name(name)}: \"{line}\""


# ── Acknowledgment: the standing order is answered in register ──────────
# Keyed by order family; the literal keeps his verbatim-quote ack (W6-5),
# so these banks intentionally have no "literal" key. No {target}
# interpolation — the base message already names the order and target.
_ACK_LINES: Dict[str, Dict[str, List[str]]] = {
    "aggressive": {
        "MOVE_TO": [
            "\"At the double, Sire — the men will smell powder soon "
            "enough.\"",
            "\"Good. An army rots standing still.\"",
            "\"We march. Pity whatever slows us.\"",
        ],
        "PURSUE": [
            "\"He is already beaten — he merely has not been told. I "
            "will tell him.\"",
            "\"Run him to ground, then. My sabers are hungry.\"",
            "\"I will have him by the collar within the week.\"",
        ],
        "HOLD": [
            "\"Hold? Very well — but chain a hound and he strains the "
            "leash, Sire.\"",
            "\"I will hold. They had best not come close enough to "
            "tempt me.\"",
            "\"Standing guard while others win laurels. As you command.\"",
        ],
        "SUPPORT": [
            "\"He shall have my sabers the moment he needs them — and I "
            "shall have a share of the credit.\"",
            "\"I ride to the guns the instant they speak.\"",
            "\"Supporting, Sire — though I intend to arrive first.\"",
        ],
    },
    "cautious": {
        "MOVE_TO": [
            "\"We move deliberately — arrival is worth little if the "
            "army arrives broken.\"",
            "\"The roads will be scouted before each march, Sire.\"",
            "\"As ordered. I keep my flanks as I go.\"",
        ],
        "PURSUE": [
            "\"I will follow — at a distance that leaves him no chance "
            "to turn on us.\"",
            "\"Pursuit, then. I do not intend to be led into anything.\"",
            "\"He will be watched at every step. Patience closes traps.\"",
        ],
        "HOLD": [
            "\"A sound instruction. Ground held is ground the enemy "
            "pays for.\"",
            "\"I will make this position expensive.\"",
            "\"Good. Let them come to us.\"",
        ],
        "SUPPORT": [
            "\"I will keep within reach — a corps that arrives whole is "
            "worth two that arrive winded.\"",
            "\"As you order. I move when the need is real, not before.\"",
            "\"He will not stand alone while I am in range.\"",
        ],
    },
}


def personality_ack(personality: str, order_type: str, turn: int,
                    key_extra: int = 0) -> str:
    """Register line appended to a standing-order acknowledgment for
    aggressive/cautious marshals ("" for literal — his quote ack is the
    W6-5 doctrine — and for unknown personalities/order types)."""
    bank = _ACK_LINES.get(personality, {}).get(order_type)
    if not bank:
        return ""
    return _pick(bank, int(turn) + int(key_extra))


# ── The halt before a hopeless assault ─────────────────────────────────
# CA9 row 2: the W6-4 muster confirm now arms ONLY for a cautious marshal
# at unfavorable odds (`objection_v2.muster_gate_arms`), which turns a UI
# interlock into a character beat — so the modal speaks in HIS register
# instead of the staff's. Aggressive and literal marshals never reach this
# seam by construction, which is why there is no bank for them here: an
# aggressive man charges without asking, and a literal man is already
# marching. Do not add one without moving the gate record.
_MUSTER_HALT_LINES: List[str] = [
    "\"I will go if you order it, Sire — but look at the ground first. "
    "This is not a battle, it is an arithmetic problem.\"",
    "\"Before I commit the corps: the odds are against us, and I would "
    "rather be told twice than bury them once.\"",
    "\"I can attack, Sire. I cannot promise you an army afterwards. "
    "Say the word and it is done.\"",
]


def cautious_muster_halt(name: str, turn: int) -> str:
    """The cautious marshal's own words on the muster-confirm modal.

    Deterministic (GR6 — display only, rotated on the turn like every
    other voice bank) and spoken ONLY behind a True from
    `objection_v2.muster_gate_arms`.
    """
    return f"{name} halts before the order is carried out. " \
           f"{_pick(_MUSTER_HALT_LINES, int(turn))}"


# ── Completion: the order is done, reported in register ─────────────────
_COMPLETION_LINES: Dict[str, List[str]] = {
    "aggressive": [
        "\"Done — and I trust the next order has more fire in it.\"",
        "\"It is done. Point me at something that shoots back, Sire.\"",
        "\"Accomplished. The men want a battle, not another road.\"",
    ],
    "cautious": [
        "\"Done, and done properly — no stragglers, no surprises.\"",
        "\"Accomplished as ordered. The army is intact.\"",
        "\"It is done. I took the liberty of posting pickets.\"",
    ],
}


def personality_completion(personality: str, reason: str, name: str,
                           turn: int) -> str:
    """Completion report for aggressive/cautious marshals: the plain
    reason plus one register line. Returns the reason unchanged for
    literal (owned by literal_completion) and unknown personalities."""
    bank = _COMPLETION_LINES.get(personality)
    base = (reason or "").strip()
    if not bank:
        return base
    line = _pick(bank, len(base) + int(turn))
    return f"{base} {name}: {line}".strip()

"""FA-89 (slice 17, Sept 11 2026): the School of War's step, for the digest.

The lesson's progression lives ENTIRELY in `tutorial_overlay.gd` — its
`advance` predicates over cross-response latches the backend does not have
(`_saw_objection`, `_saw_capture`, `_last_infantry_pool`, the Kienmayer
kill). So no unattended run could ever assert that a beat FIRED, and the
archived `audit-tutorial` digest proved only that the scenario boots.

This module is a SECOND, APPROXIMATE source by construction and says so on
every payload: the step reported is the LATEST whose `turn_gate` the current
turn has reached — which is a floor on what the overlay shows (its catch-up
rule only ever moves the displayed step FORWARD of this). It is display-only
(GR6): nothing mechanical reads it, the overlay keeps deriving its own step,
and `STEPS` is drift-pinned against the overlay's own table by
`tests/test_fa_slice17_f_the_instrument_answers_2026_09_11.py`.
"""

from typing import Dict, List, Optional, Tuple

# (id, turn_gate, title) — mirrors `tutorial_overlay.gd` `const STEPS` in order.
STEPS: List[Tuple[str, int, str]] = [
    ("survey", 1, "I. The Situation"),
    ("first_move", 1, "II. The Army Marches"),
    ("first_end_turn", 1, "III. The Day Closes"),
    ("objection", 2, "IV. The Marshal's Temper"),
    ("objection_answer", 2, "V. Trust, Insist, Compromise"),
    ("bombardment", 2, "VI. The Guns Speak"),
    ("cabinet", 3, "VII. The Cabinet"),
    ("first_battle", 4, "VIII. First Blood"),
    ("marshalate", 5, "IX. The Marshalate"),
    ("strategic_order", 5, "X. Standing Orders"),
    ("capture", 6, "XI. Conquest"),
    ("capture_answer", 6, "XII. The Conqueror's Choice"),
    ("recruit_build", 7, "XIII. The Depots"),
    ("free_scout", 8, "XIV. The Fog"),
    ("free_stand", 9, "XV. The Counter-Blow"),
    ("naval", 10, "XVI. The Wooden Wall"),
    ("congress", 11, "XVII. The Congress of Paris"),
    ("laws", 12, "XVIII. The Laws of State"),
    ("free_books", 13, "XIX. The Instruments"),
    ("handoff", 14, "XX. The Lesson Ends"),
]

TUTORIAL_SCENARIO_NAME = "tutorial"

# S14d part 2 (`docs/TABLE_LESSON_SPEC.md` §4.2): the Table — the Peace of
# Pressburg, seven cards over three turns; mirrors
# `tutorial_table_steps.gd` `const STEPS` in order (drift-pinned by
# `tests/test_tutorial_table_scenario.py`).
TABLE_SCENARIO_NAME = "tutorial_table"
TABLE_STEPS: List[Tuple[str, int, str]] = [
    ("austerlitz", 1, "I. The Day After Austerlitz"),
    ("table", 1, "II. Every Court for Itself"),
    ("austria_alone", 1, "III. Austria Alone"),
    ("pressburg", 2, "IV. The Peace of Pressburg"),
    ("bavaria", 2, "V. The Kingdom of Bavaria"),
    ("first_stone", 3, "VI. The First Stone"),
    ("handoff", 3, "VII. The Lesson Ends"),
]

# S14d part 2 (`docs/TABLE_LESSON_SPEC.md` §4.4): the School's lessons — the
# ONE tuple `main.SCENARIO_ALLOWLIST` is derived from (the consumers cannot
# import `main`), with each lesson's scenario file and its step mirror. A
# second lesson adds its name here and nowhere else.
SCHOOL_SCENARIOS: Tuple[str, ...] = (TUTORIAL_SCENARIO_NAME, TABLE_SCENARIO_NAME)
SCENARIO_FILES: Dict[str, str] = {
    TUTORIAL_SCENARIO_NAME: "tutorial_1805.json",
    TABLE_SCENARIO_NAME: "tutorial_table_1805.json",
}
STEPS_BY_SCENARIO: Dict[str, List[Tuple[str, int, str]]] = {
    TUTORIAL_SCENARIO_NAME: STEPS,
    TABLE_SCENARIO_NAME: TABLE_STEPS,
}


def is_tutorial_world(world) -> bool:
    """The Danube Lesson's world alone (its own cards' pins)."""
    return str(getattr(world, "scenario_name", "") or "") == TUTORIAL_SCENARIO_NAME


def is_school_world(world) -> bool:
    """S14d part 2: the ONE predicate by which a School scenario switches a
    subsystem off wholesale — jealousy and glory, the dotation, the client
    petitions, the campaign autosave (TUT-F2/TUT-F5's doctrine: an untaught
    modal does not intrude on a lesson). World-scoped, never an input to a
    formula (GR5). Every school lesson, the Danube included."""
    return str(getattr(world, "scenario_name", "") or "") in SCHOOL_SCENARIOS


def tutorial_step_for(world) -> Optional[Dict]:
    """The display-only step payload, or None off a School scenario."""
    steps = STEPS_BY_SCENARIO.get(str(getattr(world, "scenario_name", "") or ""))
    if not steps:
        return None
    turn = int(getattr(world, "current_turn", 1) or 1)
    reached = [(i, s) for i, s in enumerate(steps, start=1) if s[1] <= turn]
    if not reached:
        index, (step_id, gate, title) = 1, steps[0]
    else:
        index, (step_id, gate, title) = reached[-1]
    return {
        "step": int(index),
        "id": step_id,
        "title": title,
        "turn_gate": int(gate),
        "turn": turn,
        # Stated on the payload, not only in this docstring.
        "approximate": True,
    }

"""FA-89 (slice 17, Sept 11 2026): the School of War's step, for the digest.

The lesson's progression lives ENTIRELY in `tutorial_overlay.gd` — fifteen
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
    ("first_battle", 4, "VII. First Blood"),
    ("strategic_order", 5, "VIII. Standing Orders"),
    ("capture", 6, "IX. Conquest"),
    ("capture_answer", 6, "X. The Conqueror's Choice"),
    ("recruit_build", 7, "XI. The Depots"),
    ("free_scout", 8, "XII. The Fog"),
    ("free_stand", 9, "XIII. The Counter-Blow"),
    ("free_books", 10, "XIV. The Instruments"),
    ("handoff", 12, "XV. The Lesson Ends"),
]

TUTORIAL_SCENARIO_NAME = "tutorial"


def is_tutorial_world(world) -> bool:
    return str(getattr(world, "scenario_name", "") or "") == TUTORIAL_SCENARIO_NAME


def tutorial_step_for(world) -> Optional[Dict]:
    """The display-only step payload, or None off the tutorial scenario."""
    if not is_tutorial_world(world):
        return None
    turn = int(getattr(world, "current_turn", 1) or 1)
    reached = [(i, s) for i, s in enumerate(STEPS, start=1) if s[1] <= turn]
    if not reached:
        index, (step_id, gate, title) = 1, STEPS[0]
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

"""Row FR, Session FR-2 — the weak-spot readers' twelve finds (November 23,
2026): the session's seams, held DOWN.

`docs/WEAK_SPOT_FINDS_SPEC.md` §4. Every fix of the session that can move the
board sits behind a named zero-argument FUNCTION in the module it gates
(`tools/playtest_driver.py --seam MODULE:NAME=EXPR`). This list is the session
OFF: with every row down the game is the commit before (8dd99217), and a board
recorded before the session replays under the rules it was recorded under
(`tests/_oct27_seams.py` folds these rows in). The series attribution brings
them up one by one (`tools/_fr2_series_arms.py`).

    BANK    WS-R4 — `feedback.a_courts_bonus_rides_its_own_act`: a court's
            attack is judged before it runs and spends its own bonus; the
            turn-end expiry covers every holder. Down: the bonus is set after
            the act and banked for the marshal's next attack, as before.

    SHELL   WS-R5 — `combat_executor.the_guns_kill_outright`: a corps a
            bombardment shells to nothing is destroyed at once at the field
            (cause "bombardment"). Down: the forced-retreat road routs it with
            0 men until the night's supply sweep, as before.

    SALVO   WS-R12 — `battle_scale.a_salvo_is_a_battle_only_at_scale`: a
            bombardment's salvo writes a won battle only past 5,000 dead
            (`CANNONADE_MIN_CASUALTIES`); its dead still count for the war.
            Down: a salvo past 1,000 dead writes a won battle, as before (the
            farm the rule measured).

    FLOOR   WS-R7 — `battle_scale.a_remnant_is_not_a_corps`: a corps under
            1,000 men (`COUNTED_CORPS_MIN_STRENGTH`) adds no arm to combined
            arms, no next-door bonus, no ally's coordination, no march to the
            guns, no overwatch and no flank. Down: every count reads
            `strength > 0` again, as before.

The display-only and refusal-only fixes (WS-R1, WS-R2, WS-R3, WS-R8 … WS-R11)
carry no seam by design: none moves a corps or a die. Their proof is arm 0.
"""
from __future__ import annotations

FR2_SEAMS_BY_ROW = {
    "BANK": ["backend.ai.feedback:a_courts_bonus_rides_its_own_act=False"],
    "SHELL": ["backend.commands.combat_executor:the_guns_kill_outright=False"],
    "FLOOR": ["backend.game_logic.battle_scale:a_remnant_is_not_a_corps=False"],
    "SALVO": ["backend.game_logic.battle_scale:a_salvo_is_a_battle_only_at_scale=False"],
}

FR2_SEAMS_DOWN = [spec for row in FR2_SEAMS_BY_ROW for spec in FR2_SEAMS_BY_ROW[row]]

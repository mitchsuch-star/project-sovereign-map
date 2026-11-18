"""Row OC — "the rulings built" (November 18, 2026): the session's seams, held
DOWN.

The November 17 rulings (`docs/audits/OPEN_CALLS_RULED_2026_11_17.md` §4–§5,
row BA's BA-6) homed four builds before Session H. Every rule sits behind a
named zero-argument FUNCTION in the module it gates (`tools/playtest_driver.py
--seam MODULE:NAME=EXPR`; no levers). This list is the session OFF: with every
row down the game is the commit before (`9c5228a5`), and a board recorded
before the session replays under the rules it was recorded under
(`tests/_oct27_seams.py` folds these rows in, as it folds BA-6's). The rows
stand in LADDER order — the measure's arms bring them up one by one
(`tools/_oc_measure.py`).

    LETTER    OC-3, BRIT-1 — `ai_diplomacy.a_strangled_britain_writes_without_contact`:
              the trade power whose ports the System closes (the first tier,
              0.40) and whose war exhaustion is past its break-ranks line (80)
              writes for an armistice without the fifteen-turn no-contact window.

    ARREARS   OC-2, GRD-20 — `world_state.a_deficit_every_third_turn_is_remembered`:
              the mercy's turn pays no arrears down (a solvent turn that follows
              a deficit wipes no mark), so a deficit one turn in three deserts.

    RESTLESS  OC-2, GRD-19 — `world_state.restlessness_is_priced_by_the_province`:
              the restless interior costs 75 a province, capped at the crown
              term (250); down, a flat 75 for any count.

    CURE      OC-1, GRD-29 — `affairs.a_cure_is_never_stranded_by_an_edict`: the
              courts' one authority floor keeps an unbought authority cure's price
              in hand (edicts, lesser laws, titles); the cure itself pays the
              plain floor.

    STAFF     OC-1, GRD-37 / 14 / 28 — `reforms.the_staff_is_saved_for_without_the_upkeep_reserve`:
              an AI court at war saves for its Staff at the price and the flat
              reserve, without the five turns of upkeep.

    SAVE      OC-1, the save's reach (rule 10's sibling of T0-G's GR-15, found by
              the slice's own trace) — `enemy_ai.a_saving_court_holds_its_gold`:
              a court saving for its Staff holds its discretionary gold (the
              dotation and pension, the commission, the fleet and yard, the
              buildings and repairs, the rebuild recruit, the arms); the urgent
              recruit and the substitutes still buy.

    USED      OC-1, GRD-15 — `reforms.a_law_buys_what_is_used`: the law rung buys
              only a law one of whose effects the court uses (it has drilled, it
              has recruited that arm, the pool is under its cap, the Staff
              stands for a cure; passive effects always).

    CHEAP     OC-1, GRD-21 — `enemy_ai.a_cheap_rung_keeps_a_turn_of_upkeep`: every
              price-only purchase rung of the admin chain keeps one turn of upkeep
              in hand (`ledger.one_turn_of_upkeep`).

OC-4 (GRD-34, golden rule 1) carries NO seam by design: a seam would keep the
second source of the recklessness arithmetic alive, the very residue removed.
Its proof is arm 0 — OC-4 is in it, and arm 0 must equal `9c5228a5` on every
surface.
"""
from __future__ import annotations

OC_SEAMS_BY_ROW = {
    "LETTER": ["backend.game_logic.ai_diplomacy:a_strangled_britain_writes_without_contact=False"],
    "ARREARS": ["backend.models.world_state:a_deficit_every_third_turn_is_remembered=False"],
    "RESTLESS": ["backend.models.world_state:restlessness_is_priced_by_the_province=False"],
    "CURE": ["backend.game_logic.affairs:a_cure_is_never_stranded_by_an_edict=False"],
    "STAFF": ["backend.game_logic.reforms:the_staff_is_saved_for_without_the_upkeep_reserve=False"],
    "SAVE": ["backend.ai.enemy_ai:a_saving_court_holds_its_gold=False"],
    "USED": ["backend.game_logic.reforms:a_law_buys_what_is_used=False"],
    "CHEAP": ["backend.ai.enemy_ai:a_cheap_rung_keeps_a_turn_of_upkeep=False"],
}

OC_SEAMS_DOWN = [spec for row in OC_SEAMS_BY_ROW for spec in OC_SEAMS_BY_ROW[row]]

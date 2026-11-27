"""Row FUN, Session FUN-2 — "conquest with a cost" (November 26, 2026): the
session's seams, held DOWN.

`docs/GAMEPLAY_REVIEW_2026_11_25.md` §1.3 and §5, `SYSTEMS_REFERENCE.md` §240.
Every rule of the session that can move the board sits behind a named
zero-argument FUNCTION in `backend/game_logic/fear.py` (`tools/playtest_driver.py
--seam MODULE:NAME=EXPR`). This list is the session OFF: with every row down the
game is the commit before (f3df82a4), and a board recorded before the session
replays under the rules it was recorded under (`tests/_oct27_seams.py` folds
these rows in). Every seam also reads `fear.armed(world)` — the 1805 campaign's
`fear` block arms the rules; the bare flag world, the tutorials and the legacy
map carry none.

    FEAR      `fear_chooses_the_league`: each capture by France's house adds to
              every court's fear (8 x nearness x stake, the capital x3), fear
              fades 2 a turn, and the player's league is chosen by fear (past 50,
              a border or a stake, never an ally) and needs three. Down: nothing
              is written, relations below -10 choose, two make a league.
    FRIENDS   `a_declaration_angers_the_targets_friends`: a declaration's -15
              (-7) falls on the target's allies, its house and its neighbours.
              Down: on every court.
    STAND     `the_afraid_join_a_standing_league`: a court that crosses the line
              while a league stands joins it at the turn's end. Down: a standing
              league enrols nobody new. INERT while FEAR is down.
    HOME      `fear_fades_a_member_home`: a member that joined by fear and falls
              under 25 leaves the league and takes France's peace readily (+25).
              Down: it stays. INERT while FEAR is down.
    RISE      `unheld_land_rises`: France's unheld Hostile conquests do not
              settle and rise after 4 turns. Down: +5 a turn, nothing rises.
    RECRUIT   `recruits_wait_for_settling`: a province adds to the cavalry and
              artillery regen only once Settling. Down: from the day it is held.
    MIRROR    `the_charge_takes_as_the_chokepoint_does` (FUN2-1): the reckless
              charge's capture sets stability 25, clears the garrison, adds the
              +2 alarm and France's fear. Down: the mirror as it was.

The order card's warning, the map mode, the ledger's block and the province
window's count carry no seam by design: they move no corps and no die.
"""
from __future__ import annotations

from backend.game_logic import fear as _fear

_M = "backend.game_logic.fear"

FUN2_SEAMS_BY_ROW = {
    "FEAR": [f"{_M}:fear_chooses_the_league=False"],
    "FRIENDS": [f"{_M}:a_declaration_angers_the_targets_friends=False"],
    "STAND": [f"{_M}:the_afraid_join_a_standing_league=False"],
    "HOME": [f"{_M}:fear_fades_a_member_home=False"],
    "RISE": [f"{_M}:unheld_land_rises=False"],
    "RECRUIT": [f"{_M}:recruits_wait_for_settling=False"],
    "MIRROR": [f"{_M}:the_charge_takes_as_the_chokepoint_does=False"],
}

FUN2_SHIPPED_UP = tuple(FUN2_SEAMS_BY_ROW)
FUN2_SHIPPED_DOWN: tuple = ()

FUN2_SEAMS_DOWN = [spec for row in FUN2_SEAMS_BY_ROW for spec in FUN2_SEAMS_BY_ROW[row]]

# (row, module, function) — read by `tests/test_fun2_conquest_with_a_cost.py`.
SEAMS = [(row, _fear, specs[0].split(":", 1)[1].split("=", 1)[0])
         for row, specs in FUN2_SEAMS_BY_ROW.items()]

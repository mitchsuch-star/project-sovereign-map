"""Row FUN, Session FUN-2b — "peace terms priced" (November 27, 2026): the
session's seams, held DOWN.

`docs/NEXT_SESSION_PROMPT.md`'s FUN-2b block, `SYSTEMS_REFERENCE.md` §241.
Every rule of the session that can move the board sits behind a named
zero-argument FUNCTION (`tools/playtest_driver.py --seam MODULE:NAME=EXPR`):
three in `backend/game_logic/land_price.py`, two in `fear.py`. This list is
the session OFF: with every row down the game is the commit before
(dfc8ae1d), and a board recorded before the session replays under the rules it
was recorded under (`tests/_oct27_seams.py` folds these rows in). WHOLE, OFFER,
FRIGHT and CALM also read `fear.armed(world)` (the 1805 campaign's `fear`
block); PRICE is a pure rule of the scorer and binds every world.

    PRICE   `the_tables_price_keeps_rising`: the table's land price never
            stops — the harshness penalty loses its -45 floor, a court's own
            losses their -25 floor. Down: the price stops at five provinces.
    WHOLE   `no_court_signs_away_every_province`: no package France's house
            signs takes every province a court holds, whatever the score.
            Down: the 90 war-score line.
    OFFER   `the_table_offers_only_what_the_war_buys`: the guided table's land
            (the opening draft, the "Take X" rows, the declared articles, the
            Harsher button) only where the court would still sign. Down:
            offers ignore the price.
    FRIGHT  `land_at_the_table_frightens`: land passing by treaty into France's
            house frightens as a capture does (never twice). Down: it frightens
            nobody.
    CALM    `land_handed_back_calms`: land France's house gives a court by
            treaty calms that court by what taking it added. Down: nothing
            calms, no ledger is kept.

The prices on the table's lines and rows, the court's "would give" line, the
legend and the fear line carry no seam by design: they move no corps and no
die (the greyed rows are OFFER's).
"""
from __future__ import annotations

from backend.game_logic import fear as _fear
from backend.game_logic import land_price as _land_price

_L = "backend.game_logic.land_price"
_F = "backend.game_logic.fear"

FUN2B_SEAMS_BY_ROW = {
    "PRICE": [f"{_L}:the_tables_price_keeps_rising=False"],
    "WHOLE": [f"{_L}:no_court_signs_away_every_province=False"],
    "OFFER": [f"{_L}:the_table_offers_only_what_the_war_buys=False"],
    "FRIGHT": [f"{_F}:land_at_the_table_frightens=False"],
    "CALM": [f"{_F}:land_handed_back_calms=False"],
}

FUN2B_SHIPPED_UP = tuple(FUN2B_SEAMS_BY_ROW)
FUN2B_SHIPPED_DOWN: tuple = ()

FUN2B_SEAMS_DOWN = [spec for row in FUN2B_SEAMS_BY_ROW for spec in FUN2B_SEAMS_BY_ROW[row]]

_MODULES = {_L: _land_price, _F: _fear}

# (row, module, function) — read by `tests/test_fun2b_peace_terms_priced.py`.
SEAMS = [(row, _MODULES[specs[0].split(":", 1)[0]],
          specs[0].split(":", 1)[1].split("=", 1)[0])
         for row, specs in FUN2B_SEAMS_BY_ROW.items()]

"""AU-1 "the books and the figure" — the standing's seams, held DOWN
(docs/AUTHORITY_CURRENCY_SPEC.md §5.8 "The instrument and the pins", §6 the
series column).

Every behavioural change row AU makes to the store sits behind a named
FUNCTION a series arm can replace (`tools/playtest_driver.py --seam
MODULE:NAME=EXPR`, the S13b idiom: the seam becomes `lambda *a, **k: EXPR`).
No levers — the code-health ratchet is at 231 of 231. The list is the row
OFF; `tools/_standing_series_arms.py` holds each seam down and up with its
reach COUNTED in the child, and arm 0 reproduces the prior record byte for
byte. At AU-1 the books change no figure (the clamp is the clamp; the ring,
the causes, the events and the dent are records and words), so every arm is
byte-identical to HEAD's `BASELINE_SERIES` — measured, not assumed.

    AUB  `standing.keeps_books`   — down: the writer passes the clamped figure
                                    through and books nothing (no ring row, no
                                    threshold event, no dent) — HEAD's store
    AUP  `standing.hits_armed`    — AU-2a: the Chancellor's and the Host's floor
                                    clause (`bites_since`) and the Host's authority
                                    op (`since`) — down: the deck reads as before
                                    AU-2a (the Chancellor `bites: true`, the Host's
                                    Decline unpriced in authority)
    AUK  `standing.claims_armed`  — AU-2a: the Claims of the Army on the dotation
                                    tick — down: no claim is billed
    AUW  `standing.breach_armed`  — AU-2a: the word broken (a breach's strikes) and
                                    Make Amends' repayment — down: no dent, no
                                    repayment, no quote on the confirm
    AUS  `standing.sources_armed` — AU-2b: the lumps — the Te Deum, the Bulletin,
                                    the Return, the honour's payback, the
                                    ceremonies' op and the Show's two Acts
                                    (`since: "AU-2b"`) — down: the tree before AU-2b
    AUL  `standing.letters_armed` — AU-2c: the Bank's Panic and the Pope's Refusal,
                                    two affairs templates authored `since: "AU-2c"`
                                    — down: held WHOLE out of the deck (the deck
                                    before AU-2c). Up since the user's "Arm both"
                                    (November 5, 2026); the rig's AUL+ arm, which
                                    measured them up while authored, is retired
    AUY  `standing.buys_armed`    — AU-3a: the buys — the Edict letters' third
                                    answer (Decree it, `since: "AU-3a"`), the Word
                                    on an objection, Honour him and By Decree on
                                    the marshals' cards — down: the tree before
                                    AU-3a (the courts' Decree is parked with the
                                    courts' flip, AU-14)
    AUO  `standing.offices_armed` — AU-3b: the crowns and offices — "Endow them"
                                    on the Fontainebleau card and the Titles of
                                    the Confederation (the Princes' Dotations Act
                                    paid in titles) — down: the tree before AU-3b
    AUR  `standing.proclamation_armed` — AU-3b: the Proclamation, an Edict
                                    letter authored `since: "AU-3b"` — down: held
                                    WHOLE out of the deck (the deck before the
                                    Proclamation). Up since the user's "Arm it"
                                    (November 5, 2026); the rig's AUR+ arm, which
                                    measured it up while authored, is retired

    AUC  `standing.courts_move`   — AU-4: the courts' sources and battle writes
                                    (their fields, garrisons and charges, their
                                    Te Deum and Bulletin, their Decree in
                                    authority) — down: the courts as AU-4 part 1
                                    left them. Up since the user's "Flip, flat
                                    grip" (November 6, 2026); the rig's AUC+
                                    arms, which measured them up while parked,
                                    are retired
    AUF  `standing.capital_lost_by` — AU-19 (AU-4's head): a capital lost only
                                    by its defender, when it falls — down: the
                                    old rule, a lost battle at any capital the
                                    lord did not control (the seam's lambda)
    (AU-5's grip seam, AUG, is gone with its decision: the flat 75 kept by the
    user's "Flip, flat grip" — its record `tools/_standing_courts_au4.json`.)
    AUD  `enemy_ai.orders_carry_their_purse` — AU-20 (found at the flip): an
                                    admin rung's `currency` rides its order
                                    into the executor's command, so a court's
                                    Decree at its floors is paid in authority —
                                    down: the key dropped as before the fix (the
                                    review's courts-up tree, AU-4 part 1's AUC+)

`hold_down(monkeypatch)` applies the same list in-process.
"""
from __future__ import annotations

import importlib

STANDING_SEAMS_BY_ROW = {
    "AUB": ["backend.game_logic.standing:keeps_books=False"],
    "AUP": ["backend.game_logic.standing:hits_armed=False"],
    "AUK": ["backend.game_logic.standing:claims_armed=False"],
    "AUW": ["backend.game_logic.standing:breach_armed=False"],
    "AUS": ["backend.game_logic.standing:sources_armed=False"],
    "AUL": ["backend.game_logic.standing:letters_armed=False"],
    "AUY": ["backend.game_logic.standing:buys_armed=False"],
    "AUO": ["backend.game_logic.standing:offices_armed=False"],
    "AUR": ["backend.game_logic.standing:proclamation_armed=False"],
    "AUC": ["backend.game_logic.standing:courts_move=False"],
    "AUD": ["backend.ai.enemy_ai:orders_carry_their_purse=False"],
    "AUF": ["backend.game_logic.standing:capital_lost_by=bool(getattr(a[0].get_region(a[2]), 'is_capital', False) and getattr(a[0].get_region(a[2]), 'controller', None) != a[1])"],
}
STANDING_SEAMS_DOWN = [spec for row in STANDING_SEAMS_BY_ROW for spec in STANDING_SEAMS_BY_ROW[row]]


def parse(spec: str):
    target, expr = str(spec).split("=", 1)
    module_name, attr = target.split(":", 1)
    return module_name, attr, expr.strip()


def hold_down(monkeypatch, specs=STANDING_SEAMS_DOWN) -> None:
    """Apply the list in-process through `monkeypatch` (a `pytest.MonkeyPatch`
    for a module-scoped fixture), the driver's own `_apply_seams` semantics."""
    for spec in specs:
        module_name, attr, expr = parse(spec)
        owner = importlib.import_module(module_name)
        *path, name = attr.split(".")
        for step in path:
            owner = getattr(owner, step)
        assert callable(getattr(owner, name)), spec
        monkeypatch.setattr(owner, name, eval("lambda *a, **k: " + expr, {}))

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

The later slices add their seams here as they land: AUP the Chancellor's
floor (AU-2a), AUK the Claims (AU-2a), AUW the breach (AU-2a), AUS the
sources (AU-2b), AUC the courts (AU-4).

`hold_down(monkeypatch)` applies the same list in-process.
"""
from __future__ import annotations

import importlib

STANDING_SEAMS_BY_ROW = {
    "AUB": ["backend.game_logic.standing:keeps_books=False"],
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

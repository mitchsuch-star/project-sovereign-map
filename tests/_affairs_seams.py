"""RE-1 "Affairs of State" — the engine's seams, held DOWN
(docs/RECURRING_EVENTS_SPEC.md §16 "The series and the seams").

Every behavioural change of the recurring-events engine sits behind a named
FUNCTION a series arm can replace (`tools/playtest_driver.py --seam
MODULE:NAME=EXPR`, the S13b idiom: the seam becomes `lambda *a, **k: EXPR`).
No levers. The list is the engine OFF; `tools/_affairs_series_arms.py` holds
each seam down and up with its reach COUNTED in the child, and arm 0
reproduces the prior record byte for byte. On the shipped tree (the deck
UNARMED until RE-3) every seam's reach is 0 and every arm is byte-identical.

    AF0  `affairs.deliver_due`          — down: no affair is ever delivered
    AFB  `moments.moment_rows`          — the moments' blindness to `#` rows
                                          (down: the tick sees every row)
    AFP  `affairs.pulse_first` / `affairs.pulse_gap`
                                        — the pulse (down: the authored values,
                                          no seeded draw)
    AFN  `affairs.write_receipt`        — the rows and notices (down: no
                                          dispatch line for a set-aside or a
                                          withdrawal)
    AFA  `affairs.resolve_courts`       — the courts' affairs (inert in v1)
    AFH  `naval._squadron_tick`         — RE-H: the squadron's voyage (down: no
                                          squadron drills or settles; the
                                          sailing's sail stay out)
    AFS  `affairs.settle_squadrons` +   — RE-H: the sailing and the settlement
         `naval.detach_squadron`          (down: the Accept detaches nothing
                                          and no fate reaches the row; the
                                          seam is `detach_squadron`, the
                                          setter `moments._apply_squadron`
                                          calls by name, because the OPS
                                          table binds the apply function at
                                          import)
    AFE  `affairs.ai_decrees`           — RE-6: the courts' Edicts (down: no
                                          court decrees an edict; the
                                          player's offers and the lifecycle
                                          stand)
    AFR  `moments.crown_asks_a_vassal`  — RE3-6 (S15's head, November 6, 2026,
                                          the user's "Ask him; loyalty pays"):
                                          the Crown of the Reich asks a
                                          subjugated Francis too (down: the
                                          clause before it — the named court
                                          not the owner's vassal — under which
                                          the Rhine road's Pressburg by
                                          subjugation left the letter
                                          unreachable)

`hold_down(monkeypatch)` applies the same list in-process.
"""
from __future__ import annotations

import importlib

AFFAIRS_SEAMS_BY_ROW = {
    "AF0": ["backend.game_logic.affairs:deliver_due=[]"],
    "AFB": ["backend.game_logic.moments:moment_rows={str(k): v for k, v in (a[0] or {}).items() if isinstance(v, dict)}"],
    "AFP": ["backend.game_logic.affairs:pulse_first=int(__import__('backend.game_logic.affairs').game_logic.affairs.pacing(a[0])['first'])",
            "backend.game_logic.affairs:pulse_gap=int(__import__('backend.game_logic.affairs').game_logic.affairs.pacing(a[0])['gap'])"],
    "AFN": ["backend.game_logic.affairs:write_receipt=None"],
    "AFA": ["backend.game_logic.affairs:resolve_courts=[]"],
    "AFH": ["backend.game_logic.naval:_squadron_tick=[]"],
    "AFS": ["backend.game_logic.affairs:settle_squadrons=[]",
            "backend.game_logic.naval:detach_squadron={}"],
    # RE-6: the courts' Edicts (down: no court decrees; the player's letters
    # and the lifecycle are untouched — `find_ai_edict` reads the seam)
    "AFE": ["backend.game_logic.affairs:ai_decrees=False"],
    # RE3-6 (S15's head): the Crown asks a vassal Francis too (down: the clause
    # before it — `_design_fulfilled` reads the seam)
    "AFR": ["backend.game_logic.moments:crown_asks_a_vassal=False"],
}
AFFAIRS_SEAMS_DOWN = [spec for row in AFFAIRS_SEAMS_BY_ROW for spec in AFFAIRS_SEAMS_BY_ROW[row]]


def parse(spec: str):
    target, expr = str(spec).split("=", 1)
    module_name, attr = target.split(":", 1)
    return module_name, attr, expr.strip()


def hold_down(monkeypatch, specs=AFFAIRS_SEAMS_DOWN) -> None:
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

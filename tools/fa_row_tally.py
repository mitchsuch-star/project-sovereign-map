#!/usr/bin/env python
"""How much of the Final Whole-Game Audit is left?

Derives the tally from the row tables themselves rather than from a
hand-maintained number in a heading — a count written down by hand is stale
the moment the next slice lands, which is the exact class of defect this
build has spent eleven slices closing.

    .venv/Scripts/python.exe tools/fa_row_tally.py            # the tally
    .venv/Scripts/python.exe tools/fa_row_tally.py --open     # + the open ids

Sources of truth:
  docs/BUG_FIXES.md         - FA-n (audit defects), FA-N (verification pass),
                              FA-R (review-round findings), FA-S* (found while
                              building)
  docs/DESIGN_REFINEMENT.md - FA-D (design tie-ins), FA-S*-D* (gates raised by
                              a review round)

A row's state is read off its STATUS cell, which is the last pipe-delimited
column. The vocabulary the build actually uses is:

    FIXED / CLOSED / LANDED / a leading tick   -> closed
    HALF FIXED                                 -> partial
    REFUTED / a leading cross                  -> refuted (disposed)
    DUPLICATE                                  -> disposed
    MOVED / a leading fast-forward             -> re-homed to a later slice
    anything else                              -> still open

FA-D rows carry a VERIFICATION verdict in that column rather than a status
(they are design questions, not defects), so they read as open by
construction; that is correct — a design tie-in is open until a gate rules on
it — but they are counted in their own family so the defect number is not
inflated by them.
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = (ROOT / "docs" / "BUG_FIXES.md",
           ROOT / "docs" / "DESIGN_REFINEMENT.md")

ROW = re.compile(r"^>?\s*\|\s*\*\*(FA-[A-Z]*\d+(?:-[A-Z]?\d+)?)\*\*\s*\|")

FAMILIES = {
    "audit defect (FA-n)": lambda r: (not r.startswith(("FA-N", "FA-R", "FA-D"))
                                      and "-D" not in r[3:]
                                      and not r.startswith("FA-S")),
    "verification pass (FA-N)": lambda r: r.startswith("FA-N"),
    "review-round finding (FA-R)": lambda r: r.startswith("FA-R"),
    "found while building (FA-S)": lambda r: (r.startswith("FA-S")
                                              and "-D" not in r[3:]),
    "design tie-in (FA-D)": lambda r: r.startswith("FA-D"),
    "gate from a round (FA-S*-D*)": lambda r: (r.startswith("FA-S")
                                               and "-D" in r[3:]),
}


def classify(cell: str) -> str:
    upper = cell.upper()
    if "HALF FIXED" in upper:
        return "partial"
    if ("**FIXED" in upper or "**CLOSED" in upper or "LANDED" in upper
            or "✅" in cell):
        return "closed"
    if "**REFUTED" in upper or "❌" in cell:
        return "refuted"
    if "DUPLICATE" in upper:
        return "duplicate"
    if "**MOVED" in upper or "⏩" in cell:
        return "moved"
    return "OPEN"


def family_of(row_id: str) -> str:
    for name, test in FAMILIES.items():
        if test(row_id):
            return name
    return "other"


def collect() -> dict[str, tuple[str, str]]:
    """{row id: (state, family)} — the FIRST definition of a row wins, since
    later mentions are cross-references in prose tables."""
    rows: dict[str, tuple[str, str]] = {}
    for path in SOURCES:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").split("\n"):
            match = ROW.match(line)
            if not match:
                continue
            row_id = match.group(1)
            if row_id in rows:
                continue
            cells = line.split(" | ")
            status = cells[-1] if len(cells) >= 3 else ""
            rows[row_id] = (classify(status), family_of(row_id))
    return rows


def sort_key(row_id: str):
    match = re.match(r"FA-([A-Z]*)(\d+)", row_id)
    order = {"": 0, "N": 1, "R": 2, "S": 3, "D": 4}.get(match.group(1), 5)
    return (order, int(match.group(2)), row_id)


def main() -> int:
    rows = collect()
    if not rows:
        print("no FA rows found - are the docs where this expects them?")
        return 1

    by_family: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter)
    for row_id, (state, family) in rows.items():
        by_family[family][state] += 1

    width = max(len(name) for name in by_family)
    print(f"{'family':{width}}  {'OPEN':>5} {'closed':>7} {'disposed':>9} "
          f"{'total':>6}")
    totals: collections.Counter = collections.Counter()
    for family in sorted(by_family):
        counts = by_family[family]
        disposed = sum(n for state, n in counts.items()
                       if state not in ("OPEN", "closed"))
        print(f"{family:{width}}  {counts['OPEN']:>5} {counts['closed']:>7} "
              f"{disposed:>9} {sum(counts.values()):>6}")
        totals.update(counts)
    disposed = sum(n for state, n in totals.items()
                   if state not in ("OPEN", "closed"))
    print(f"{'TOTAL':{width}}  {totals['OPEN']:>5} {totals['closed']:>7} "
          f"{disposed:>9} {sum(totals.values()):>6}")

    defects_open = sum(counts["OPEN"] for family, counts in by_family.items()
                       if not family.startswith(("design", "gate")))
    design_open = totals["OPEN"] - defects_open
    print()
    print(f"DEFECT rows still open: {defects_open}")
    print(f"DESIGN rows / gates still open: {design_open}")

    if "--open" in sys.argv:
        print()
        for family in sorted(by_family):
            ids = sorted((r for r, (s, f) in rows.items()
                          if s == "OPEN" and f == family), key=sort_key)
            if ids:
                print(f"{family}:")
                print("   " + " ".join(ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

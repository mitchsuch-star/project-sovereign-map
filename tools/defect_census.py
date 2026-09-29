#!/usr/bin/env python
"""Every open row in the defect and design ledgers, counted from the tables.

The Score Finish's census (docs/SCORE_FINISH_SPEC.md §1). It generalises
tools/fa_row_tally.py from the FA family to every row id in the two ledgers,
because "every open defect" needs a number read off the tables rather than a
number written into a heading (the Creative AAR section's heading still reads
"ALL OPEN" over rows the mandate has since fixed).

    .venv/Scripts/python.exe tools/defect_census.py              # the tally
    .venv/Scripts/python.exe tools/defect_census.py --open       # + open rows
    .venv/Scripts/python.exe tools/defect_census.py --json out.json

A row is a table line whose first cell starts with a row id (AAR-1, RS-12,
IQ7-X7, FA-S17-D2, UI-2d-1, IQ-2.1 ...), after any leading marks (a strike, a
tick, a warning sign). Its state, first rule that fires:

    closed    the id cell is struck (~~) or ticked; or a cell STARTS with a
              tick or an upper-case closing word (FIXED, CLOSED, LANDED, BUILT,
              RULED, DECIDED, TAKEN, RESOLVED); or the LAST cell carries one
    disposed  the same, with REFUTED, STRUCK, DUPLICATE, WITHDRAWN, RETIRED,
              DECLINED, NOT REPRODUCED, NOT TAKEN, CANONIZED, SUPERSEDED,
              ACCEPTED (a disposition, as in "ACCEPTED, not deferred")
    partial   HALF FIXED / PARTIAL
    closed    (by heading) the section heading claims the whole section closed
              ("ALL ... FIXED", "SECTION CLOSED", "ALL DISPOSED") and the row
              does not say ROUTED / OPEN / DEFERRED or name an Owner
    closed    (by table) the table has a "Fix" column and no owner or status
              column - a table of fixes applied - and the row does not say
              ROUTED / OPEN / DEFERRED or name an Owner
    OPEN      anything else

An id defined in several tables is closed if ANY of its rows is closed: a
landing record strikes the row it fixes, and an earlier summary table does not
always follow. --open marks with '*' an open row whose id shares a line with a
closing word somewhere else under docs/ (a landing record, STATUS, a spec) -
the rows most likely to be stale, which a person should read first.

The vocabulary is the build's own (upper-case status words, a tick, a struck
id), so the census is a reading aid with a stated rule, not a proof: the spec's
done-when asks a person to confirm every row it lists.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEDGERS = (("defect", DOCS / "BUG_FIXES.md"),
           ("design", DOCS / "DESIGN_REFINEMENT.md"))

CELL_SPLIT = re.compile(r"(?<!\\)\|")
SEPARATOR = re.compile(r"^:?-{3,}:?$")
ID_TOKEN = r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+[a-z]?){1,3}(?:\.\d+)?"
ID_CELL = re.compile(r"^[^A-Za-z0-9]*(?P<id>" + ID_TOKEN + r")(?![A-Za-z0-9])")
ANY_ID = re.compile(r"(?<![A-Za-z0-9-])(" + ID_TOKEN + r")(?![A-Za-z0-9])")
SEVERITY = re.compile(r"\bP([0-4])\b")

CLOSED = re.compile(r"\b(FIXED|CLOSED|LANDED|BUILT|RULED|DECIDED|TAKEN|"
                    r"RESOLVED)\b")
DISPOSED = re.compile(r"\b(REFUTED|STRUCK|DUPLICATE|WITHDRAWN|RETIRED|"
                      r"DECLINED|NOT REPRODUCED|NOT TAKEN|CANONIZED|"
                      r"SUPERSEDED|ACCEPTED|RE-HOMED)\b")
# SF-0 (September 29, 2026): a row that is closed for the half that landed
# and OPEN for the rest says so with these two words, and the marker wins
# over every other occurrence of the id (NPC-12: the seven surfaces landed,
# RS-26 owns the remainder).
OPEN_REMAINDER = re.compile(r"\bOPEN REMAINDER\b")
# SF-0: every live row carries ONE tag naming the step (or gate) that owns
# it and the pillar it is scored under — `⟨SF step=2 · SR-6a · pillar=narration⟩`.
# The pillar keys are SCORE_FINISH_SPEC.md §2's fourteen, plus `none` for a
# row no pillar reads (test hygiene, a harness defect, a modding example).
SF_TAG = re.compile(r"⟨SF\s+(?P<body>[^⟩]*)⟩")
PILLARS = ("ending", "diplomacy", "first_contact", "economy", "naval",
           "living_balance", "combat_legibility", "marshal_drama", "vassals",
           "ui_ux", "command", "narration", "ai_aliveness", "agendas", "none")
PARTIAL = re.compile(r"\b(HALF FIXED|PARTIAL)\b")
STILL_OPEN = re.compile(r"\b(ROUTED|OPEN|DEFERRED)\b|Owner:")
HEADING_CLOSED = re.compile(r"ALL\b[^()]{0,40}?\b(FIXED|CLOSED|DISPOSED)|"
                            r"SECTION CLOSED|Fixed Bug Archive")
TICK = "✅"
CROSS = "❌"
# A tick followed by a closing word, anywhere in a cell: the triage tables
# record "FILED - <tick> CLOSED by CX-R1" in the verdict column.
TICKED_CLOSE = re.compile(TICK + r"[\s*~]{0,4}(FIXED|CLOSED|LANDED|BUILT|"
                          r"RULED|DECIDED|TAKEN|RESOLVED)\b")


def _clean(text: str, width: int) -> str:
    text = re.sub(r"[*`~]", "", text)
    text = re.sub(r"<br>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= width else text[: width - 1] + "…"


def _split(body: str) -> list[str]:
    parts = CELL_SPLIT.split(body)[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [p.strip() for p in parts]


def _leads_with(cell: str, pattern: re.Pattern) -> bool:
    head = cell.lstrip("*~ >(")
    if head.startswith(TICK):
        return pattern is CLOSED
    return bool(pattern.match(head))


def classify(cells: list[str], heading_closed: bool,
             table_of_fixes: bool, status_cols: tuple[int, ...] = ()) -> str:
    first, last = cells[0], cells[-1]
    if OPEN_REMAINDER.search(" ".join(cells)):
        return "partial"
    if "~~" in first or TICK in first:
        return "closed"
    if CROSS in first:
        return "disposed"
    if any(PARTIAL.match(c.lstrip("*~ ")) for c in cells[1:]):
        return "partial"
    if any(_leads_with(c, CLOSED) for c in cells[1:]):
        return "closed"
    # A ticked closing word counts mid-cell only in a column the table names
    # as its verdict or status: in a finding cell it usually describes a
    # sibling's fix ("NPC-3's alias fix closed the full-name road").
    if any(TICKED_CLOSE.search(cells[i]) for i in status_cols
           if 0 < i < len(cells)):
        return "closed"
    if any(_leads_with(c, DISPOSED) for c in cells[1:]):
        return "disposed"
    if PARTIAL.search(last):
        return "partial"
    if TICK in last or CLOSED.search(last):
        return "closed"
    if CROSS in last or DISPOSED.search(last):
        return "disposed"
    row_text = " ".join(cells)
    if (heading_closed or table_of_fixes) and not STILL_OPEN.search(row_text):
        return "closed"
    return "OPEN"


def _parse_tag(body: str) -> dict:
    """`step=2 · SR-6a · pillar=narration` -> {"step", "slice", "pillar"}."""
    out = {"pillar": "", "step": "", "slice": ""}
    parts = [p.strip() for p in re.split(r"\s*[·|]\s*", body) if p.strip()]
    for part in parts:
        if part.startswith("pillar="):
            out["pillar"] = part[len("pillar="):].strip()
        elif part.startswith("step="):
            out["step"] = part[len("step="):].strip()
        else:
            out["slice"] = (out["slice"] + " " + part).strip()
    return out


def collect() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for ledger, path in LEDGERS:
        if not path.exists():
            continue
        section, heading_closed, heading_landed = "", False, False
        header: list[str] = []
        previous: list[str] = []
        for number, line in enumerate(
                path.read_text(encoding="utf-8").split("\n"), start=1):
            if line.startswith("## "):
                heading = line[3:]
                heading_closed = bool(HEADING_CLOSED.search(heading))
                heading_landed = "landed" in heading.lower()
                section = re.split(r" \(|\s+—\s+", heading, maxsplit=1)[0]
                section = _clean(section, 70)
                header, previous = [], []
                continue
            body = line.lstrip("> ").rstrip()
            if not body.startswith("|"):
                header, previous = [], []
                continue
            cells = _split(body)
            if cells and all(SEPARATOR.match(c) for c in cells if c):
                header = [c.lower().strip("* ") for c in previous]
                continue
            previous = cells
            if len(cells) < 2:
                continue
            match = ID_CELL.match(cells[0])
            if not match:
                continue
            row_id = match.group("id")
            # A "Fix" column is a fix APPLIED in a table of fixes, or in any
            # table under a "landed" heading ("fix - lever"); elsewhere a
            # "fix seam" / "fix / landing" column is a fix PROPOSED.
            table_of_fixes = ((any(h in ("fix", "fixed", "fix applied")
                                   for h in header)
                               or (heading_landed
                                   and any(h.startswith("fix")
                                           and "shape" not in h
                                           and "seam" not in h
                                           for h in header)))
                              and not any(("owner" in h or "status" in h
                                           or "shape" in h or "rout" in h)
                                          for h in header))
            status_cols = tuple(i for i, h in enumerate(header)
                                if "verdict" in h or "status" in h)
            state = classify(cells, heading_closed, table_of_fixes,
                             status_cols)
            sev_match = next((SEVERITY.search(c) for c in cells[1:3]
                              if SEVERITY.search(c) and len(c) < 40), None)
            finding = cells[2] if (len(cells) > 3 and len(cells[1]) < 40) \
                else cells[1]
            entry = rows.setdefault(row_id, {
                "id": row_id, "ledger": ledger, "section": section,
                "line": number, "state": state,
                "severity": f"P{sev_match.group(1)}" if sev_match else "",
                "finding": _clean(finding, 160),
                "owner": _clean(cells[-1], 200),
                "occurrences": 0,
                "pillar": "", "step": "", "slice": "",
            })
            entry["occurrences"] += 1
            row_text = " ".join(cells)
            if OPEN_REMAINDER.search(row_text):
                entry["open_remainder"] = True
            tag = SF_TAG.search(row_text)
            if tag and not entry["pillar"]:
                entry.update(_parse_tag(tag.group("body")))
            if entry.get("open_remainder"):
                entry["state"] = "partial"
            elif entry["state"] in ("OPEN", "partial") and state not in (
                    "OPEN", "partial"):
                entry["state"] = state
    return rows


def closed_elsewhere() -> set[str]:
    """Ids that share a line with a closing word anywhere under docs/."""
    found: set[str] = set()
    for path in sorted(DOCS.glob("*.md")):
        for line in path.read_text(encoding="utf-8").split("\n"):
            if TICK not in line and not CLOSED.search(line):
                continue
            found.update(ANY_ID.findall(line))
    return found


def by_pillar(open_rows: list[dict]) -> dict:
    """{pillar: {"open": n, "p1": [ids], "p2": n, "rows": [ids]}} plus
    "untagged": the open rows that carry no SF tag (SF-0's done-when is
    that this list is empty)."""
    table: dict[str, dict] = {}
    untagged: list[str] = []
    for entry in open_rows:
        pillar = entry.get("pillar") or ""
        if pillar not in PILLARS:
            untagged.append(entry["id"])
            continue
        bucket = table.setdefault(pillar, {"open": 0, "p1": [], "p2": 0,
                                           "rows": []})
        bucket["open"] += 1
        bucket["rows"].append(entry["id"])
        if entry["severity"] == "P1":
            bucket["p1"].append(entry["id"])
        elif entry["severity"] == "P2":
            bucket["p2"] += 1
    return {"pillars": dict(sorted(table.items())), "untagged": untagged}


def print_by_pillar(open_rows: list[dict]) -> None:
    view = by_pillar(open_rows)
    print(f"\n{'pillar':18} {'open':>5} {'P1':>4} {'P2':>4}  rows")
    for pillar, bucket in view["pillars"].items():
        rows = ", ".join(bucket["rows"])
        print(f"{pillar:18} {bucket['open']:>5} {len(bucket['p1']):>4} "
              f"{bucket['p2']:>4}  {rows}")
        for p1 in bucket["p1"]:
            print(f"{'':18} {'':>5} {'':>4} {'':>4}  P1 open: {p1}")
    if view["untagged"]:
        print(f"\nUNTAGGED open rows ({len(view['untagged'])}): "
              + ", ".join(view["untagged"]))
    else:
        print("\nevery open row carries an SF tag")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--open", action="store_true",
                        help="list every open row")
    parser.add_argument("--json", metavar="PATH",
                        help="write every row as JSON")
    parser.add_argument("--by-pillar", action="store_true",
                        help="the open rows grouped by the pillar their SF "
                             "tag names, with the P1s and the untagged")
    args = parser.parse_args()
    # The ledgers carry arrows and dashes a Windows console code page cannot
    # print; replace what it cannot show rather than die mid-list.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    rows = collect()
    if not rows:
        print("no rows found - are the ledgers where this expects them?")
        return 1

    counts: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter)
    for entry in rows.values():
        counts[entry["ledger"]][entry["state"]] += 1

    print(f"{'ledger':8} {'OPEN':>6} {'partial':>8} {'closed':>7} "
          f"{'disposed':>9} {'total':>6}")
    for ledger, _ in LEDGERS:
        c = counts[ledger]
        print(f"{ledger:8} {c['OPEN']:>6} {c['partial']:>8} {c['closed']:>7} "
              f"{c['disposed']:>9} {sum(c.values()):>6}")

    open_rows = [r for r in rows.values() if r["state"] in ("OPEN", "partial")]
    stale = closed_elsewhere()
    for entry in open_rows:
        entry["closing_word_elsewhere"] = entry["id"] in stale

    if args.open:
        for ledger, _ in LEDGERS:
            by_section: dict[str, list] = collections.defaultdict(list)
            for entry in open_rows:
                if entry["ledger"] == ledger:
                    by_section[entry["section"]].append(entry)
            if not by_section:
                continue
            print(f"\n=== {ledger} ledger: open rows by section "
                  "(* = a closing word names this id elsewhere) ===")
            for section, entries in by_section.items():
                print(f"\n## {section}")
                for e in sorted(entries, key=lambda r: r["line"]):
                    mark = "*" if e["closing_word_elsewhere"] else " "
                    sev = e["severity"] or "--"
                    print(f" {mark}{e['id']:<14} {sev:<3} {e['finding']}")

    if args.by_pillar:
        print_by_pillar(open_rows)

    if args.json:
        out = pathlib.Path(args.json)
        out.write_text(json.dumps(sorted(rows.values(),
                                         key=lambda r: (r["ledger"],
                                                        r["line"])),
                                  indent=1, ensure_ascii=False),
                       encoding="utf-8")
        print(f"\nwrote {len(rows)} rows to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

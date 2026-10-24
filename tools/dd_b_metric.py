"""DD-B's metric, read off the causes record and the roads' exported rows
(Pre-Deploy S14e, October 24, 2026 — the re-measure's instrument, written so
the first measure's `metric.json` is reproduced byte-for-byte from its
`causes.json` and the three roads' `rows.json`).

    .venv/Scripts/python.exe tools/dd_b_metric.py \
        --causes docs/audits/dd_b/causes_2026_10_24.json \
        --road conquest=docs/audits/dd_b/conquest_2026_10_24 \
        --road diplomacy=docs/audits/dd_b/diplomacy_2026_10_24 \
        --road sea=docs/audits/dd_b/sea_2026_10_24 \
        --out docs/audits/dd_b/metric_2026_10_24.json

How it is counted (DD-B's rule, `docs/audits/DD_B_FRESH_EYES_2026_10_14.md`
§3): each road counts each cause once, at its worst sighting on that road; the
total across the roads counts each cause once, at its worst sighting anywhere.
Severity is the players' own. A road's turns are the turns it played (20 when
the turn counter reached Turn 21). The done-when: under 5 rows per 10 turns
and 0 P1.

`--check` verifies that every player row of every road is a sighting of a
cause or struck with a reason, and that every cause's sightings name rows that
exist — the same pins `tests/test_dd_b_the_client_hands.py` holds on the
committed records.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SEV_RANK = {"P1": 0, "P2": 1, "P3": 2}
DONE_WHEN_PER_10 = 5.0


def _read(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _worst(sevs) -> str:
    return min(sevs, key=lambda s: SEV_RANK.get(s, 9))


def _turns(run_dir: pathlib.Path) -> int:
    rec = _read(run_dir / "run.json")
    n = rec.get("turn_number")
    return max(int(n) - 1, 0) if n else 0


def metric(causes: dict, roads: dict[str, pathlib.Path]) -> dict:
    per_road = {}
    for road, run_dir in roads.items():
        rows = _read(run_dir / "rows.json") if (run_dir / "rows.json").is_file() else []
        seen = []
        for c in causes["causes"]:
            here = [s["severity"] for s in c["sightings"] if s["road"] == road]
            if here:
                seen.append(_worst(here))
        turns = _turns(run_dir)
        by = {k: sum(1 for s in seen if s == k) for k in ("P1", "P2", "P3")}
        per_road[road] = {
            "turns": turns,
            "rows": len(seen),
            "by_severity": by,
            "per_10_turns": round(len(seen) * 10 / turns, 1) if turns else None,
            "player_rows_filed": len(rows),
            "player_rows_struck": sum(1 for s in causes.get("struck", []) if s["road"] == road),
        }
    turns = sum(r["turns"] for r in per_road.values())
    sevs = [_worst([s["severity"] for s in c["sightings"]]) for c in causes["causes"]]
    by = {k: sum(1 for s in sevs if s == k) for k in ("P1", "P2", "P3")}
    homes: dict[str, int] = {}
    for c in causes["causes"]:
        # The first measure's labels: a defect row's slice ("S13b"), a design
        # question alone ("DR" -> "DESIGN_REFINEMENT only"), and a defect row
        # with a design half ("S13b+DR" -> counted under its slice AND named).
        home = str(c.get("home") or "?")
        if home == "DR":
            labels = ["DESIGN_REFINEMENT only"]
        elif home.endswith("+DR"):
            labels = [home[:-3], f"{home[:-3]} with a design half"]
        else:
            labels = [home]
        for label in labels:
            homes[label] = homes.get(label, 0) + 1
    per10 = round(len(sevs) * 10 / turns, 1) if turns else None
    across = {
        "turns": turns,
        "rows": len(sevs),
        "by_severity": by,
        "per_10_turns": per10,
        "per_10_turns_by_severity": {k: (round(v * 10 / turns, 1) if turns else None) for k, v in by.items()},
        "homes": homes,
        "done_when": {"under_5_per_10": bool(turns) and per10 < DONE_WHEN_PER_10, "zero_p1": by["P1"] == 0},
    }
    return {"per_road": per_road, "across": across,
            "done_when_met": across["done_when"]["under_5_per_10"] and across["done_when"]["zero_p1"]}


def check(causes: dict, roads: dict[str, pathlib.Path]) -> list[str]:
    problems = []
    sighted = {(s["road"], s["row"]) for c in causes["causes"] for s in c["sightings"]}
    struck = {(s["road"], s["row"]) for s in causes.get("struck", [])}
    existing = set()
    for road, run_dir in roads.items():
        rows = _read(run_dir / "rows.json") if (run_dir / "rows.json").is_file() else []
        for r in rows:
            existing.add((road, r["id"]))
            if (road, r["id"]) not in sighted | struck:
                problems.append(f"{road} row {r['id']} is neither a sighting nor struck")
    for c in causes["causes"]:
        if not c["sightings"]:
            problems.append(f"{c['id']} has no sighting")
        for s in c["sightings"]:
            if (s["road"], s["row"]) not in existing:
                problems.append(f"{c['id']} cites {s['road']} row {s['row']}, which does not exist")
            if s.get("frame") and not (REPO / s["frame"]).is_file():
                problems.append(f"{c['id']} cites a frame that is not in the repository: {s['frame']}")
    ids = [c["id"] for c in causes["causes"]]
    for i in sorted(set(ids)):
        if ids.count(i) > 1:
            problems.append(f"{i} is filed twice")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--causes", required=True)
    ap.add_argument("--road", action="append", required=True, metavar="ROAD=DIR")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    causes = _read(pathlib.Path(args.causes))
    roads = {}
    for spec in args.road:
        road, _, d = spec.partition("=")
        roads[road] = (REPO / d) if not pathlib.Path(d).is_absolute() else pathlib.Path(d)
    if args.check:
        problems = check(causes, roads)
        for p in problems:
            print("✗", p)
        if problems:
            return 1
        print("✓ every row a sighting or struck; every sighting a row with its frame")
    m = metric(causes, roads)
    text = json.dumps(m, indent=1, ensure_ascii=False)
    if args.out:
        pathlib.Path(args.out).write_text(text + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    print(json.dumps({"per_road": {k: (v["rows"], v["per_10_turns"], v["by_severity"]) for k, v in m["per_road"].items()},
                      "across": (m["across"]["rows"], m["across"]["per_10_turns"], m["across"]["by_severity"]),
                      "done_when_met": m["done_when_met"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

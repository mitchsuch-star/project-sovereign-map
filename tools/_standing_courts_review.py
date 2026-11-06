"""AU-4 (docs/AUTHORITY_CURRENCY_SPEC.md §6.7, §4.1 reading 16) — the courts'
flip measured for the user's review before the word: the shipped tree (the
courts' writes PARKED, `standing.courts_move` down) against the courts forced
UP — with the flat grip, and with the grip reading their books (arm AUG) —
on the measured runs; and the series rig's end-state table on its arms.

Per run: the player's end, each great power's end and lowest (the trace's
`courts_end` and the courts' moves), the courts' moves by cause; per letter:
its arrivals on each tree; per rig arm: the end-state table (the courts'
authority, their DP term, their grip, the coalition leader) and the series'
first divergence. Seeded paths, not laws.

    .venv/Scripts/python.exe -X utf8 tools/_standing_courts_review.py

Writes tools/_standing_courts_au4.json (committed with the landing record).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RUN = ROOT / "tools" / "playtest_runs" / "au4_2026_11_05"
GREAT_POWERS = ("Austria", "Britain", "Prussia", "Russia", "Ottoman", "Spain")
TREES = ("shipped", "flat", "grip")


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {f"{r['family']}/{r['arm']}": r for r in record.get("rows") or [] if r.get("measured")}


def _arrivals(reach_record: Dict[str, Any]) -> Dict[str, int]:
    from tools._affairs_au2c_letters import reach_runs
    out: Counter = Counter()
    for _key, row in reach_runs(reach_record).items():
        for template, reach in (row.get("affairs_reach") or {}).items():
            out[template] += sum(1 for line in reach.get("occurrences") or [] if " arrived T" in line)
    return dict(sorted(out.items()))


def compose(args) -> Dict[str, Any]:
    standing = {"shipped": _rows(_load(Path(args.shipped_standing))),
                "flat": _rows(_load(Path(args.flat_standing))),
                "grip": _rows(_load(Path(args.grip_standing)))}
    reach = {"shipped": _load(Path(args.shipped_reach)), "flat": _load(Path(args.flat_reach)),
             "grip": _load(Path(args.grip_reach))}
    rig = _load(Path(args.rig))
    runs: Dict[str, Any] = {}
    ends = {t: defaultdict(list) for t in TREES}
    at_floor = {t: Counter() for t in TREES}
    court_moves = {t: Counter() for t in TREES}
    for key in sorted(standing["shipped"]):
        row = {"player_end": {}, "courts_end": {}}
        for tree in TREES:
            r = standing[tree].get(key)
            if r is None:
                continue
            row["player_end"][tree] = int(r.get("end", 0) or 0)
            courts = {c: int(v) for c, v in (r.get("courts_end") or {}).items() if c in GREAT_POWERS}
            row["courts_end"][tree] = courts
            for court, v in courts.items():
                ends[tree][court].append(v)
                if v <= 30:
                    at_floor[tree][court] += 1
            for label, entry in (r.get("by_cause") or {}).items():
                lord, _sep, cause = label.partition(":")
                if _sep and lord and not lord.endswith(".py"):   # "<court>:<cause>"; "<file>.py:<site>" is a keyless move of the player's
                    court_moves[tree][cause] += int(entry.get("n", 0) or 0)
        runs[key] = row
    moved = sorted(k for k, r in runs.items()
                   if len(set(r["player_end"].values())) > 1)
    return {
        "_what": ("AU-4: the courts' flip measured for the user's review — the shipped tree (the courts "
                  "parked) against the courts UP with the flat grip and with the grip reading their books; "
                  "per run the player's end and each great power's end; the courts' moves by cause; each "
                  "letter's arrivals; the series rig's end-state table (AUTHORITY_CURRENCY_SPEC.md §6.7). "
                  "Seeded paths, not laws."),
        "runs_measured": len(runs),
        "courts_mean_end": {t: {c: round(sum(v) / len(v), 1) for c, v in sorted(ends[t].items()) if v}
                            for t in TREES},
        "courts_at_or_under_30": {t: dict(sorted(at_floor[t].items())) for t in TREES},
        "court_moves_by_cause": {t: dict(sorted(court_moves[t].items())) for t in TREES},
        "letters": {t: _arrivals(reach[t]) for t in TREES},
        "player_end_moved": moved,
        "rig": {arm: {"first_divergence_vs_prior": row.get("first_divergence_vs_prior"),
                      "series": row.get("series"),
                      "end_state": (row.get("reach") or {}).get("end_state"),
                      "court_moves": (row.get("reach") or {}).get("courts")}
                for arm, row in (rig.get("arms") or {}).items()},
        "runs": runs,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shipped-standing", default=str(ROOT / "tools" / "_standing_final.json"))
    ap.add_argument("--flat-standing", default=str(RUN / "courts_flat" / "standing_courts_flat.json"))
    ap.add_argument("--grip-standing", default=str(RUN / "courts_grip" / "standing_courts_grip.json"))
    ap.add_argument("--shipped-reach", default=str(ROOT / "tools" / "_s14c_sweep_final.json"))
    ap.add_argument("--flat-reach", default=str(RUN / "courts_flat" / "reach_courts_flat.json"))
    ap.add_argument("--grip-reach", default=str(RUN / "courts_grip" / "reach_courts_grip.json"))
    ap.add_argument("--rig", default=str(ROOT / "tools" / "_standing_series_arms_final.json"))
    ap.add_argument("--out", default=str(ROOT / "tools" / "_standing_courts_au4.json"))
    args = ap.parse_args(argv)
    out = compose(args)
    Path(args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", args.out)
    print("courts' mean end:", json.dumps(out["courts_mean_end"]))
    print("at or under 30:", json.dumps(out["courts_at_or_under_30"]))
    print("court moves:", json.dumps(out["court_moves_by_cause"]))
    print("player's end moved on", len(out["player_end_moved"]), "runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

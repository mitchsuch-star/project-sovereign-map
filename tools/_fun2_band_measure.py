"""Row FUN, Session FUN-2 — "conquest with a cost" — the France band on the
COMMANDED arms (the brief's measure (c): reported, never gated). The deploy gate's
difficulty guard (DYNAMISM_SPEC.md §2: France holds 23–28 provinces at turn 40
on the commanded arms) through `tools/playtest_driver.py` (`score_run.ARMS`
CMD-H / CMD-A / CMD-M: commanded_full40.json, forty turns, the mock parser),
France's provinces on the last `ledger` row.
    arm 0    every row of `tests/_fun2_seams.py` held DOWN through the driver's
             own `--seam` — MUST reproduce row FR-2's standing reading
             (`tools/_fr2_band_2026_11_23.json` arm ALL: 28 / 28 / 26);
    arm ALL  the tree as shipped — reported (the band is a guard, not FUN-2's gate);
    +ROW     every FUN-2 row but that one held down (the row alone up).
    .venv/Scripts/python.exe tools/_fun2_band_measure.py [--arms 0,ALL] [--jobs 3]
        [--tree <frozen copy>]
THIS PARENT RUNS PLAIN (never `-X utf8`).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
STANDING = {"CMD-H": 28, "CMD-A": 28, "CMD-M": 26}


def _seams(tree: pathlib.Path) -> dict:
    """arm -> the seams held DOWN: "0" every row, "ALL" none, "+ROW" every row
    but that one (the row alone up — its own effect)."""
    if str(tree) not in sys.path:
        sys.path.insert(0, str(tree))
    from tests._fun2_seams import FUN2_SEAMS_BY_ROW, FUN2_SEAMS_DOWN
    arms = {"0": list(FUN2_SEAMS_DOWN), "ALL": []}
    for row in FUN2_SEAMS_BY_ROW:
        arms["+" + row] = [s for r, specs in FUN2_SEAMS_BY_ROW.items() if r != row for s in specs]
    return arms


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="0,ALL")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--only", default="", help="a comma list of CMD-H / CMD-A / CMD-M (default all)")
    ap.add_argument("--tree", default=str(ROOT))
    ap.add_argument("--out", default=str(ROOT / "tools" / "_fun2_band_2026_11_26.json"))
    args = ap.parse_args()
    tree = pathlib.Path(args.tree).resolve()
    arms = _seams(tree)
    from tools import score_run as SR
    run_dir = tree / "tools" / "playtest_runs" / "fun2_band"
    record = {"_note": ("Row FUN, Session FUN-2 — the France band on the commanded arms (the deploy "
                        "gate's difficulty guard, 23–28; FUN-2 reports it, never gates): score_run's "
                        "CMD-H / CMD-A / CMD-M per arm, France's provinces on the last ledger row. Arm 0 "
                        "holds every FUN-2 seam down and must read 28 / 28 / 26 (row FR-2's standing "
                        "reading); arm ALL is the shipped tree. Written by tools/_fun2_band_measure.py."),
              "band": list(BAND), "standing": STANDING, "arms": {}}
    names = [n.strip() for n in args.only.split(",") if n.strip()] or list(BAND_ARMS)
    jobs = [(arm, name) for arm in [a.strip() for a in args.arms.split(",") if a.strip()]
            for name in names]

    def _one(job):
        arm, name = job
        arms_dir = run_dir / arm
        arms_dir.mkdir(parents=True, exist_ok=True)
        seams = [flag for spec in arms[arm] for flag in ("--seam", spec)]
        print(f"[fun2] band {arm} {name} ...", flush=True)
        result = SR._run_driver(tree, arms_dir, name, list(SR.ARMS[name]["argv"]) + seams)
        if result["exit"] != 0:
            raise SystemExit(f"[fun2] band {arm} {name} failed: {result}")
        rows = [json.loads(line) for line in (arms_dir / name / "digest.jsonl")
                .read_text(encoding="utf-8").splitlines() if line.strip()]
        ledgers = [r for r in rows if r.get("kind") == "ledger"]
        return arm, name, int(ledgers[-1]["provinces"]), result.get("seconds")

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        for arm, name, provinces, seconds in pool.map(_one, jobs):
            record["arms"].setdefault(arm, {"seams": arms[arm]})[name] = provinces
            print(f"[fun2] band {arm} {name}: {provinces} ({seconds} s)", flush=True)
    for arm, row in record["arms"].items():
        measured = [n for n in BAND_ARMS if n in row]
        # the session's review: an arm with no band arm measured holds nothing (None)
        row["_holds"] = (all(BAND[0] <= int(row[n]) <= BAND[1] for n in measured)
                         if measured else None)
    pathlib.Path(args.out).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({a: {n: r.get(n) for n in BAND_ARMS} for a, r in record["arms"].items()}))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

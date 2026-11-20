"""Row IC, Session 2 — the France band on the COMMANDED arms, re-read
(INDEPENDENT_COMMAND_SPEC.md §13 "R-INERT"; November 20, 2026).

Session 2 gives every simple order a button, makes the typed line the road for
a task, and lets a standing order carry exact orders (if-thens). None of it
may move a campaign nobody typed a task into: the deploy gate's difficulty
guard (DYNAMISM_SPEC.md §2 — France holds 23–28 provinces at turn 40 on the
commanded arms) must read as it stood. ONE change of the session is meant to
reach the board by itself:

    GRD-33   a literal marshal's buff for a clear order no longer banks from
             turn to turn (`world_state._process_tactical_states`, behind the
             seam `meta_executor.the_literal_buff_expires_with_the_turn`).

    arm 0    that seam held DOWN through the driver's own `--seam` — MUST
             reproduce the standing band to the province
             (`_ic_band_2026_11_19.json`: 26 / 27 / 28);
    arm ALL  the shipped tree — what GRD-33 moves, if anything (Soult is
             France's only marshal who follows orders to the letter).

The reading is `tools/_ba1_band_measure.py`'s own: `score_run.ARMS` CMD-H /
CMD-A / CMD-M (commanded_full40.json, forty turns, the mock parser), France's
provinces on the last `ledger` row; and, per seed, whether a trust crisis came
up (the digest's `POPUP redemption` rows — the audience is untouched by this
session, so the count is a control). Run ALONE — no backend, test or deck edit
lands while it runs.

    .venv/Scripts/python.exe tools/_ic2_measure.py [--arms 0,ALL]
        [--stamp 2026_11_20] [--jobs 2]

THIS PARENT RUNS PLAIN (never `-X utf8`): the children print cp1252.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEAM = "backend.commands.meta_executor:the_literal_buff_expires_with_the_turn=False"
# arm -> the seams held DOWN
ARMS = {
    "0": [SEAM],
    "ALL": [],
}
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
STANDING = {"CMD-H": 26, "CMD-A": 27, "CMD-M": 28}      # _ic_band_2026_11_19.json


def measure(arms, jobs: int) -> dict:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools import score_run as SR

    run_dir = ROOT / "tools" / "playtest_runs" / "ic2_band"
    record = {"_note": ("Row IC, Session 2 (buttons for orders, the line for tasks, exact orders) — "
                        "the France band on the commanded arms (DYNAMISM_SPEC.md §2: the deploy "
                        "gate's difficulty guard, 23–28): score_run's CMD-H / CMD-A / CMD-M "
                        "(commanded_full40.json, forty turns, the mock parser) per arm — France's "
                        "provinces on the last ledger row, and the trust crises that came up. Arm 0 "
                        "holds GRD-33's seam down through the driver's --seam and must be the "
                        "standing band (26 / 27 / 28); arm ALL is the shipped tree. Written by "
                        "tools/_ic2_measure.py (a chain run ALONE)."),
              "band": list(BAND), "standing": dict(STANDING), "arms": {}}
    for arm in arms:
        arms_dir = run_dir / arm
        arms_dir.mkdir(parents=True, exist_ok=True)
        seams = [flag for spec in ARMS[arm] for flag in ("--seam", spec)]

        def _one(name, arms_dir=arms_dir, seams=seams, arm=arm):
            print(f"[ic2] band {arm} {name} ...", flush=True)
            result = SR._run_driver(ROOT, arms_dir, name, list(SR.ARMS[name]["argv"]) + seams)
            if result["exit"] != 0:
                raise SystemExit(f"[ic2] band {arm} {name} failed: {result}")
            rows = [json.loads(line) for line in (arms_dir / name / "digest.jsonl")
                    .read_text(encoding="utf-8").splitlines() if line.strip()]
            ledgers = [r for r in rows if r.get("kind") == "ledger"]
            turns = [r for r in rows if r.get("kind") == "turn"]
            digest = arms_dir / name / "digest.md"
            crises = (digest.read_text(encoding="utf-8", errors="replace").count("POPUP redemption")
                      if digest.is_file() else 0)
            return name, {"provinces": int(ledgers[-1]["provinces"]),
                          "turn": int(turns[-1]["turn"]) if turns else None,
                          "status": result["status"], "trust_crises": int(crises)}

        with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
            record["arms"][arm] = dict(pool.map(_one, BAND_ARMS))
        record["arms"][arm]["seams_down"] = list(ARMS[arm])
    if "0" in record["arms"]:
        record["arm_0_is_the_standing_band"] = all(
            record["arms"]["0"][name]["provinces"] == STANDING[name] for name in BAND_ARMS)
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--stamp", default="2026_11_20")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default="", help="the record's path (default: tools/_ic2_band_<stamp>.json)")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    record = measure(arms, args.jobs)
    out = pathlib.Path(args.out) if args.out else ROOT / "tools" / f"_ic2_band_{args.stamp}.json"
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[ic2] band written {out}: "
          + str({a: {n: v["provinces"] for n, v in r.items() if n in BAND_ARMS}
                 for a, r in record["arms"].items()}), flush=True)


if __name__ == "__main__":
    main()

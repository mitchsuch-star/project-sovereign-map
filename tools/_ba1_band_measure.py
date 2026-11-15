"""Row BA, BA-1 — the France band on the COMMANDED arms, re-read for WS-11
(BATTLE_DIORAMA_SPEC.md §15.10 "The measure"; November 14, 2026).

The deploy gate's difficulty guard (DYNAMISM_SPEC.md §2: France holds 23–28
provinces at turn 40 on the commanded arms) is read through
`tools/playtest_driver.py`, and the driver plays THROUGH the game server —
`/new_game` installs its world by `backend.main._set_active_world`, the door
that serves a campaign. So on `austerlitz` and `marengo` the commanded arms
are campaigns the server holds on a rolled seed, and since WS-11 their
battles draw the campaign's dice. `historical` (CMD-H) is the fixed table and
keeps the old dice.

    arm 0    WS-11's seam held DOWN through the driver's own `--seam` — MUST
             reproduce Session G5's shipped band to the province
             (`_g5_band_2026_11_11.json`: 26 / 26 / 25);
    arm ALL  the shipped tree.

The reading is `tools/_g5_measure.py::_band`'s own: `score_run.ARMS` CMD-H /
CMD-A / CMD-M (commanded_full40.json, forty turns, the mock parser), France's
provinces on the last `ledger` row. Run ALONE — no backend, test or deck edit
lands while it runs.

    .venv/Scripts/python.exe tools/_ba1_band_measure.py [--arms 0,ALL]
        [--stamp 2026_11_14] [--jobs 2]

THIS PARENT RUNS PLAIN (never `-X utf8`): the children print cp1252.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEAM = "backend.game_logic.campaign_variance:the_battle_dice_are_seeded=False"
# arm -> the seams held DOWN
ARMS = {
    "0": [SEAM],
    "ALL": [],
}
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")


def measure(arms, jobs: int) -> dict:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools import score_run as SR

    run_dir = ROOT / "tools" / "playtest_runs" / "ba1_band"
    record = {"_note": ("Row BA, BA-1 (the battle in acts) — the France band on the commanded arms "
                        "(DYNAMISM_SPEC.md §2: the deploy gate's difficulty guard, 23–28), re-read "
                        "for WS-11 (the battle's dice are the campaign's): score_run's CMD-H / CMD-A "
                        "/ CMD-M (commanded_full40.json, forty turns, the mock parser) per arm — "
                        "France's provinces on the last ledger row. Arm 0 holds WS-11's seam down "
                        "through the driver's --seam and is Session G5's band; arm ALL is the shipped "
                        "tree. Written by tools/_ba1_band_measure.py (a chain run ALONE)."),
              "band": list(BAND), "arms": {}}
    for arm in arms:
        arms_dir = run_dir / arm
        arms_dir.mkdir(parents=True, exist_ok=True)
        seams = [flag for spec in ARMS[arm] for flag in ("--seam", spec)]

        def _one(name, arms_dir=arms_dir, seams=seams, arm=arm):
            print(f"[ba1] band {arm} {name} ...", flush=True)
            result = SR._run_driver(ROOT, arms_dir, name, list(SR.ARMS[name]["argv"]) + seams)
            if result["exit"] != 0:
                raise SystemExit(f"[ba1] band {arm} {name} failed: {result}")
            rows = [json.loads(line) for line in (arms_dir / name / "digest.jsonl")
                    .read_text(encoding="utf-8").splitlines() if line.strip()]
            ledgers = [r for r in rows if r.get("kind") == "ledger"]
            turns = [r for r in rows if r.get("kind") == "turn"]
            return name, {"provinces": int(ledgers[-1]["provinces"]),
                          "turn": int(turns[-1]["turn"]) if turns else None,
                          "status": result["status"]}

        with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
            record["arms"][arm] = dict(pool.map(_one, BAND_ARMS))
        record["arms"][arm]["seams_down"] = list(ARMS[arm])
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--stamp", default="2026_11_14")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default="", help="the record's path (default: tools/_ba1_band_<stamp>.json)")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    record = measure(arms, args.jobs)
    out = pathlib.Path(args.out) if args.out else ROOT / "tools" / f"_ba1_band_{args.stamp}.json"
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[ba1] band written {out}: "
          + str({a: {n: v["provinces"] for n, v in r.items() if n in BAND_ARMS}
                 for a, r in record["arms"].items()}), flush=True)


if __name__ == "__main__":
    main()

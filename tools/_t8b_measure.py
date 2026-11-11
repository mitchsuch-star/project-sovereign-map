"""Session F — Tier 8, Crowns & Recognition's second half (DY-7): the
session's ONE measure sweep, three arms on the three gate surfaces
(DYNAMISM_SPEC.md §2b rule 2: one switch a rule, one sweep a session; §6
and the Tier-8 gate record §6a Q4; November 10, 2026).

    arm 0       every DY-7 seam down — MUST reproduce session E's records
                byte for byte (`_dy_signature_t8_2026_11_10.json`, and arm
                ALL of `_t8_chain_d_2026_11_10.json` on that record's keys);
    arm RECOG   the legitimists' condition alone (`crowns.the_legitimists_
                withhold`: the peace chokepoints write `recognized_by`, the
                Congress grants, the beats — no price);
    arm ALL     + the three prices (`crowns.an_unrecognized_crown_pays`) —
                the shipped tree.

Per arm it runs the three instruments session E used, each a chain of
children under `INK_IRON_SEAMS` (the AU-2c hook), sequentially and ALONE —
no backend, test or deck edit lands while it runs:

  * the ten ambient `SWEEP_SEEDS` x 40 turns (`tools/_t3_4_measure.py`) — a
    DY signature record and a census per arm (the census carries the
    recognitions beside the crowns erected);
  * the AI-France harness, the ten seeds x 40 turns
    (`tools/_t3_5_chain_d.py --arms … --arm-seams …`) — ONE record holding
    the three arms (`recognitions` beside `crowns`);
  * the France band on the COMMANDED arms (the deploy gate's difficulty
    guard, 23–28): `score_run.ARMS` CMD-H / CMD-A / CMD-M, forty turns
    through `tools/playtest_driver.py`, each arm through the driver's own
    `--seam`; France's provinces on the last ledger row, into ONE record.

THIS PARENT RUNS PLAIN (never `-X utf8`): the children print cp1252.

    .venv/Scripts/python.exe tools/_t8b_measure.py [--arms 0,RECOG,ALL]
        [--surfaces ambient,d,band] [--stamp 2026_11_10]
"""
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECOG = "backend.game_logic.crowns:the_legitimists_withhold=False"
PRICE = "backend.game_logic.crowns:an_unrecognized_crown_pays=False"
# arm -> (the seams held DOWN, the ambient records' label)
ARMS = {
    "0": ([RECOG, PRICE], "t8b_control"),
    "RECOG": ([PRICE], "t8b_recog"),
    "ALL": ([], "t8b"),
}


def _run(cmd, seams: str = "") -> None:
    env = dict(os.environ)
    env.pop("INK_IRON_SEAMS", None)
    if seams:
        env["INK_IRON_SEAMS"] = seams
    print("[t8b]", " ".join(str(c) for c in cmd), f"(seams down: {seams or 'none'})", flush=True)
    rc = subprocess.run([sys.executable, *map(str, cmd)], cwd=str(ROOT), env=env).returncode
    if rc != 0:
        raise SystemExit(f"[t8b] failed (rc {rc}): {cmd}")


BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")


def _band(arms, stamp: str) -> None:
    """The France band on the commanded arms: each arm's three driver runs
    side by side, France's provinces off the last `ledger` row."""
    import json
    from concurrent.futures import ThreadPoolExecutor

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools import score_run as SR

    run_dir = ROOT / "tools" / "playtest_runs" / "t8b_band"
    record = {"_note": ("Session F (Tier 8, Crowns & Recognition's second half, DY-7) — the France "
                        "band on the commanded arms (DYNAMISM_SPEC.md §2: the deploy gate's "
                        "difficulty guard, 23–28): score_run's CMD-H / CMD-A / CMD-M "
                        "(commanded_full40.json, forty turns, the mock parser) per arm — France's "
                        "provinces on the last ledger row; written by tools/_t8b_measure.py "
                        "--surfaces band (a chain run ALONE)."),
              "band": list(BAND), "arms": {}}
    for arm in arms:
        arms_dir = run_dir / arm
        arms_dir.mkdir(parents=True, exist_ok=True)
        seams = [flag for spec in ARMS[arm][0] for flag in ("--seam", spec)]

        def _one(name, arms_dir=arms_dir, seams=seams):
            print(f"[t8b] band {arm} {name} ...", flush=True)
            result = SR._run_driver(ROOT, arms_dir, name, list(SR.ARMS[name]["argv"]) + seams)
            if result["exit"] != 0:
                raise SystemExit(f"[t8b] band {arm} {name} failed: {result}")
            rows = [json.loads(line) for line in (arms_dir / name / "digest.jsonl")
                    .read_text(encoding="utf-8").splitlines() if line.strip()]
            ledgers = [r for r in rows if r.get("kind") == "ledger"]
            turns = [r for r in rows if r.get("kind") == "turn"]
            return name, {"provinces": int(ledgers[-1]["provinces"]),
                          "turn": int(turns[-1]["turn"]) if turns else None,
                          "status": result["status"]}

        with ThreadPoolExecutor(max_workers=3) as pool:
            record["arms"][arm] = dict(pool.map(_one, BAND_ARMS))
        record["arms"][arm]["seams_down"] = list(ARMS[arm][0])
    out = ROOT / "tools" / f"_t8b_band_{stamp}.json"
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[t8b] band written {out}: "
          + str({a: {n: v['provinces'] for n, v in r.items() if n in BAND_ARMS}
                 for a, r in record['arms'].items()}), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--surfaces", default="ambient,d,band")
    ap.add_argument("--stamp", default="2026_11_10")
    ap.add_argument("--turns", type=int, default=40)
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    surfaces = set(args.surfaces.split(","))
    tools = ROOT / "tools"
    if "ambient" in surfaces:
        for arm in arms:
            down, label = ARMS[arm]
            _run([tools / "_t3_4_measure.py", "--turns", args.turns,
                  "--label", label.replace("_", "-"),
                  "--out", tools / f"_dy_signature_{label}_{args.stamp}.json",
                  "--census", tools / f"_{label}_census_{args.stamp}.json"],
                 seams=";".join(down))
    if "d" in surfaces:
        cmd = [tools / "_t3_5_chain_d.py", "--turns", args.turns, "--arms", ",".join(arms),
               "--out", tools / f"_t8b_chain_d_{args.stamp}.json",
               "--run-dir", tools / "playtest_runs" / "t8b_chain_d"]
        for arm in arms:
            if ARMS[arm][0]:
                cmd += ["--arm-seams", f"{arm}={';'.join(ARMS[arm][0])}"]
        _run(cmd)
    if "band" in surfaces:
        _band(arms, args.stamp)
    print("[t8b] the sweep is written", flush=True)


if __name__ == "__main__":
    main()

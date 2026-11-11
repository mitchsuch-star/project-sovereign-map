"""Session D — Tier 6, the Awakening's second half (DY-5): the session's ONE
measure sweep, six arms on the three gate surfaces (DYNAMISM_SPEC.md §2b
rule 2: one switch a rule, one sweep a session; §5 and the Tier-6 gate
record §5a; November 10, 2026).

    arm 0           every DY-5 seam down — MUST reproduce session C's records
                    byte for byte (`_dy_signature_t6_2026_11_10.json`, and arm
                    ALL of `_t6_chain_d_2026_11_10.json` on that record's keys);
    arm LEVEE       the liberation levée alone (`awakening.the_levee_rises`:
                    infantry regen ×1.5 and the draft ×0.75 for a court at war
                    on contested home soil, its people awakened; the `levee`
                    beats);
    arm DIAL        + the client dial (`awakening.the_tiger_is_ridden`: an
                    awakened client's loyalty −2 at autonomy ≤ 1, +1 at ≥ 2;
                    a rebellion names the cause);
    arm REVANCHE    + a risen people's revanche (`awakening.
                    a_risen_people_swears_revanche`: the partition bar waived
                    at `risen`);
    arm LIBERATORS  + the liberators' friction (`awakening.
                    liberators_hold_together`: 1 a turn, not 2, while the
                    league frees an awakened people);
    arm ALL         + the third letter (`awakening.the_nation_writes`) — the
                    shipped tree.

Per arm it runs the three instruments session C used, each a chain of
children under `INK_IRON_SEAMS` (the AU-2c hook), sequentially and ALONE —
no backend, test or deck edit lands while it runs:

  * the ten ambient `SWEEP_SEEDS` x 40 turns (`tools/_t3_4_measure.py`) — a
    DY signature record and a census per arm (the census carries the
    peoples' beats, the levée's beats, the awakened rebellions, the risen
    revanches and the supply bill by nation);
  * the AI-France harness, the ten seeds x 40 turns
    (`tools/_t3_5_chain_d.py --arms … --arm-seams …`) — ONE record holding
    the six arms (`awakening_events`, `levee_events`, `supply_losses`,
    `france_captures`);
  * the France band on the COMMANDED arms (the deploy gate's difficulty
    guard, 23–28): `score_run.ARMS` CMD-H / CMD-A / CMD-M, forty turns
    through `tools/playtest_driver.py`, each arm through the driver's own
    `--seam`; France's provinces on the last ledger row, into ONE record.

THIS PARENT RUNS PLAIN (never `-X utf8`): the children print cp1252.

    .venv/Scripts/python.exe tools/_t6b_measure.py [--arms 0,LEVEE,DIAL,REVANCHE,LIBERATORS,ALL]
        [--surfaces ambient,d,band] [--stamp 2026_11_10]
"""
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEVEE = "backend.game_logic.awakening:the_levee_rises=False"
DIAL = "backend.game_logic.awakening:the_tiger_is_ridden=False"
REVANCHE = "backend.game_logic.awakening:a_risen_people_swears_revanche=False"
LIBERATORS = "backend.game_logic.awakening:liberators_hold_together=False"
ARMS_LETTER = "backend.game_logic.awakening:the_nation_writes=False"
# arm -> (the seams held DOWN, the ambient records' label)
ARMS = {
    "0": ([LEVEE, DIAL, REVANCHE, LIBERATORS, ARMS_LETTER], "t6b_control"),
    "LEVEE": ([DIAL, REVANCHE, LIBERATORS, ARMS_LETTER], "t6b_levee"),
    "DIAL": ([REVANCHE, LIBERATORS, ARMS_LETTER], "t6b_dial"),
    "REVANCHE": ([LIBERATORS, ARMS_LETTER], "t6b_revanche"),
    "LIBERATORS": ([ARMS_LETTER], "t6b_liberators"),
    "ALL": ([], "t6b"),
}


def _run(cmd, seams: str = "") -> None:
    env = dict(os.environ)
    env.pop("INK_IRON_SEAMS", None)
    if seams:
        env["INK_IRON_SEAMS"] = seams
    print("[t6b]", " ".join(str(c) for c in cmd), f"(seams down: {seams or 'none'})", flush=True)
    rc = subprocess.run([sys.executable, *map(str, cmd)], cwd=str(ROOT), env=env).returncode
    if rc != 0:
        raise SystemExit(f"[t6b] failed (rc {rc}): {cmd}")


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

    run_dir = ROOT / "tools" / "playtest_runs" / "t6b_band"
    record = {"_note": ("Session D (Tier 6, the Awakening's second half, DY-5) — the France band "
                        "on the commanded arms (DYNAMISM_SPEC.md §2: the deploy gate's difficulty "
                        "guard, 23–28): score_run's CMD-H / CMD-A / CMD-M (commanded_full40.json, "
                        "forty turns, the mock parser) per arm — France's provinces on the last "
                        "ledger row; written by tools/_t6b_measure.py --surfaces band (a "
                        "chain run ALONE)."),
              "band": list(BAND), "arms": {}}
    for arm in arms:
        arms_dir = run_dir / arm
        arms_dir.mkdir(parents=True, exist_ok=True)
        seams = [flag for spec in ARMS[arm][0] for flag in ("--seam", spec)]

        def _one(name, arms_dir=arms_dir, seams=seams):
            print(f"[t6b] band {arm} {name} ...", flush=True)
            result = SR._run_driver(ROOT, arms_dir, name, list(SR.ARMS[name]["argv"]) + seams)
            if result["exit"] != 0:
                raise SystemExit(f"[t6b] band {arm} {name} failed: {result}")
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
    out = ROOT / "tools" / f"_t6b_band_{stamp}.json"
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[t6b] band written {out}: "
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
               "--out", tools / f"_t6b_chain_d_{args.stamp}.json",
               "--run-dir", tools / "playtest_runs" / "t6b_chain_d"]
        for arm in arms:
            if ARMS[arm][0]:
                cmd += ["--arm-seams", f"{arm}={';'.join(ARMS[arm][0])}"]
        _run(cmd)
    if "band" in surfaces:
        _band(arms, args.stamp)
    print("[t6b] the sweep is written", flush=True)


if __name__ == "__main__":
    main()

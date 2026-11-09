"""T3-5 chain D — the AI-France sweep re-run, Tier 3's second gate surface
(the Tier-3 gate record AI_INTENT_SPEC.md §13.2 R6; DYNAMISM_SPEC.md §2
Tier 3; November 9, 2026).

Runs `tools/ai_france_sweep.py`'s child over the ten `SWEEP_SEEDS` x 40
turns TWICE on one tree — arm D0 with `the_conduct_binds_every_runner`
held down through `INK_IRON_SEAMS` (the conduct rule's player exemption as
T3-3 landed it) and arm D with it up (the AI-run France bound as every
court) — keeping the full digests in the gitignored `tools/playtest_runs/`
and writing ONE compact committed record: per arm and seed, France's
`captures_outside_aim` entry (the deploy gate's AI-France line, read from
the ONE instrument, `ai_v_sweep.derive_metrics`), the per-court map, the
ambient total, France's captures (turn, province, from) and the ending —
and, descriptively, France's captures in the November 6 review's AI-France
run (`docs/audits/playtest_digests/rev1106-ai-france/`), the march the
review named (Vienna, then Estonia). THIS PARENT RUNS PLAIN; the chain runs
ALONE.

Usage:
  .venv/Scripts/python.exe tools/_t3_5_chain_d.py --out FILE [--run-dir DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import ai_france_sweep as AF  # noqa: E402
from tools.ai_v_sweep import AMBIENT_K, SWEEP_SEEDS  # noqa: E402

SEAM_DOWN = "backend.game_logic.war_council:the_conduct_binds_every_runner=False"
NOV6 = ROOT / "docs" / "audits" / "playtest_digests" / "rev1106-ai-france"


def france_captures(digest: dict) -> list:
    out = []
    for row in digest.get("turns") or []:
        for event in row.get("events") or []:
            if (event.get("type") == "region_captured"
                    and event.get("captured_by") == "France"):
                out.append([int(row.get("turn", 0)), str(event.get("region") or ""),
                            str(event.get("captured_from") or "")])
    return out


def summarize(digest: dict) -> dict:
    derived = digest.get("derived") or {}
    by_court = dict(derived.get("captures_outside_aim_by_court") or {})
    series = digest.get("france_series") or []
    return {
        "france_outside_aim": int(by_court.get("France", 0) or 0),
        "captures_outside_aim": int(derived.get("captures_outside_aim", 0) or 0),
        "captures_outside_aim_by_court": by_court,
        "france_captures": france_captures(digest),
        "france_provinces_final": int((series[-1] if series else {}).get("provinces", 0) or 0),
        "ending": digest.get("ending"),
    }


def run_arm(arm: str, run_dir: pathlib.Path, turns: int) -> dict:
    out_dir = run_dir / arm
    out_dir.mkdir(parents=True, exist_ok=True)
    if arm == "D0":
        os.environ["INK_IRON_SEAMS"] = SEAM_DOWN
    else:
        os.environ.pop("INK_IRON_SEAMS", None)
    seeds = {}
    for seed in SWEEP_SEEDS:
        path = out_dir / f"{seed}.json"
        print(f"[chain-d] {arm} {seed}: {turns} turns ...", flush=True)
        rc = AF.spawn(seed, AMBIENT_K, turns, path)
        if rc != 0:
            raise SystemExit(f"[chain-d] {arm} {seed} failed (rc {rc})")
        seeds[seed] = summarize(json.loads(path.read_text(encoding="utf-8")))
    os.environ.pop("INK_IRON_SEAMS", None)
    return seeds


def nov6() -> dict:
    out = {}
    for seed in SWEEP_SEEDS:
        path = NOV6 / f"{seed}.json"
        if path.exists():
            out[seed] = france_captures(json.loads(path.read_text(encoding="utf-8")))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--out", required=True)
    ap.add_argument("--run-dir", default=str(ROOT / "tools" / "playtest_runs" / "t3_5_chain_d"))
    args = ap.parse_args()
    run_dir = pathlib.Path(args.run_dir)
    arms = {arm: run_arm(arm, run_dir, args.turns) for arm in ("D0", "D")}
    record = {
        "_note": ("T3-5 chain D — the AI-France sweep, Tier 3's second gate surface "
                  "(AI_INTENT_SPEC.md §13.2 R6): ten SWEEP_SEEDS x "
                  f"{args.turns} turns at K={AMBIENT_K}, arm D0 the conduct rule's "
                  "player exemption held (T3-3's reading), arm D the AI-run France "
                  "bound; written by tools/_t3_5_chain_d.py (a chain run ALONE); "
                  "pinned by tests/test_t3_5_the_tier_closes.py. The deploy gate's 0 "
                  "is the gate's to measure."),
        "turns": int(args.turns),
        "arms": arms,
        "totals": {arm: {"france_outside_aim": sum(s["france_outside_aim"] for s in seeds.values()),
                         "captures_outside_aim": sum(s["captures_outside_aim"] for s in seeds.values())}
                   for arm, seeds in arms.items()},
        "nov6_france_captures": nov6(),
    }
    pathlib.Path(args.out).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                                      encoding="utf-8")
    print(f"[chain-d] totals = {record['totals']}")
    print(f"[chain-d] written {args.out}")


if __name__ == "__main__":
    main()

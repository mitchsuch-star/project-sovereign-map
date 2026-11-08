"""T3-1 (Tier 3's head — the Tier-3 gate record AI_INTENT_SPEC.md §13.2
R2; DYNAMISM_SPEC.md §2 Tier 3; November 8, 2026): the march metric's
PRE-BUILD baseline — the tier's starting DEBT.

Runs the ten ambient `SWEEP_SEEDS` (40 turns, each child under
PYTHONHASHSEED=0 via `ai_v_sweep.spawn_run`; THIS PARENT RUNS PLAIN,
never `-X utf8`) and writes `tools/_t3_march_baseline_2026_11_08.json`:
per seed `captures_outside_aim` (the ambient total, player excluded)
and the full per-court map, plus the ambient grand total. The deploy
gate reads 0 here and on the AI-France sweep's France entry once
T3-2…T3-4 land; the baseline is measured TODAY, honestly nonzero, and
never re-run into this file (the kept-record idiom — a later chain
writes its own dated record).

Usage:
  .venv/Scripts/python.exe tools/_t3_march_baseline.py [--turns 40] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ai_v_sweep import (  # noqa: E402
    AMBIENT_K,
    SWEEP_SEEDS,
    _variance_signature,
    spawn_run,
)

OUT_DEFAULT = ROOT / "tools" / "_t3_march_baseline_2026_11_08.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args()

    seeds = {}
    for seed in SWEEP_SEEDS:
        print(f"[t3] {seed}: running {args.turns} ambient turns ...",
              flush=True)
        digest = spawn_run(seed, AMBIENT_K, args.turns)
        derived = digest["derived"]
        seeds[seed] = {
            "captures_outside_aim": int(derived["captures_outside_aim"]),
            "by_court": dict(derived["captures_outside_aim_by_court"]),
            # The full signature rides too: the compatibility pin strips
            # the new column and compares against the T2-6 record byte
            # for byte — the widening moved no world-line.
            "signature": _variance_signature(digest),
        }
    total = sum(entry["captures_outside_aim"] for entry in seeds.values())
    record = {
        "_note": ("T3-1 pre-build march-metric baseline (the Tier-3 gate "
                  "record AI_INTENT_SPEC.md 13.2 R2; DYNAMISM_SPEC.md "
                  f"Tier 3) — ten ambient SWEEP_SEEDS x {args.turns} turns "
                  f"at K={AMBIENT_K}; written by tools/_t3_march_baseline.py "
                  "(a chain run ALONE); pinned by "
                  "tests/test_t3_1_the_march_metric.py. The ambient totals "
                  "are the tier's starting DEBT; the deploy gate reads 0, "
                  "measured at the gate once T3-2..T3-4 land, never today."),
        "turns": int(args.turns),
        "ambient_base": int(AMBIENT_K),
        "ambient_total": int(total),
        "seeds": seeds,
    }
    out = pathlib.Path(args.out)
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"[t3] ambient captures_outside_aim total = {total}")
    print(f"[t3] written {out}")


if __name__ == "__main__":
    main()

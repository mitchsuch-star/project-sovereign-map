"""DY-0 (Tier 2's head — DYNAMISM_SPEC.md §7; the Tier-2 gate record
AI_INTENT_SPEC.md §3.8.2; November 8, 2026): the PRE-BUILD story-class
baseline.

Runs the ten ambient `SWEEP_SEEDS` (40 turns, the pin-16a idiom — each
child under PYTHONHASHSEED=0 via `ai_v_sweep.spawn_run`; THIS PARENT RUNS
PLAIN, never `-X utf8`) and writes `tools/_dy_signature_baseline.json`:
per seed the `_variance_signature` and the `story_class`, plus the
distinct-class COUNT — the floor the Concert's tiers must beat, measured
again at the deploy gate (≥ 4 of 10). The chain runs ALONE: no backend,
test or deck edit lands while it runs.

Usage:
  .venv/Scripts/python.exe tools/_dy0_baseline.py [--turns 40] [--out FILE]
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
    story_class,
    story_class_count,
)

OUT_DEFAULT = ROOT / "tools" / "_dy_signature_baseline.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args()

    seeds = {}
    for seed in SWEEP_SEEDS:
        print(f"[dy0] {seed}: running {args.turns} ambient turns ...",
              flush=True)
        digest = spawn_run(seed, AMBIENT_K, args.turns)
        cls = story_class(digest)
        seeds[seed] = {
            "signature": _variance_signature(digest),
            # The class serialized as its canonical pairs — the JSON copy
            # of the hashable tuple, order preserved.
            "story_class": [[key, list(map(list, values))
                             if values and isinstance(values[0], tuple)
                             else list(values)]
                            for key, values in cls],
        }
    classes = [json.dumps(seeds[s]["story_class"], sort_keys=True)
               for s in SWEEP_SEEDS]
    count = story_class_count(classes)
    record = {
        "_note": ("DY-0 pre-build story-class baseline (DYNAMISM_SPEC.md "
                  "§7; the gate record §3.8.2) — ten ambient SWEEP_SEEDS "
                  f"x {args.turns} turns at K={AMBIENT_K}; written by "
                  "tools/_dy0_baseline.py (a chain run ALONE); pinned by "
                  "tests/test_dy0_the_signature.py. The count is the "
                  "pre-band floor the Concert must beat; the deploy gate "
                  "re-measures (>= 4 of 10)."),
        "turns": int(args.turns),
        "ambient_base": int(AMBIENT_K),
        "story_class_count": int(count),
        "seeds": seeds,
    }
    out = pathlib.Path(args.out)
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"[dy0] story_class_count = {count} of {len(SWEEP_SEEDS)}")
    print(f"[dy0] written {out}")


if __name__ == "__main__":
    main()

"""T4-1 — the BASELINE_SERIES attribution for the Alarm of Europe (the Tier-4
gate record DYNAMISM_SPEC.md §3c G1/G2; November 9, 2026), each seam's
reach COUNTED in the child (an arm whose seam never bites cannot pass for a
byte-identical one). The prior is HEAD's `BASELINE_SERIES` (never the
working tree's), the S14k rig's rule.

Arms: `0` — both T4-1 seams down, the tree before the slice (must reproduce
the prior byte for byte); `WRITE` — the alarm's write alone held down;
`RUNG` — the guarantee rung alone held down; `ALL` — both seams up, the
shipped tree (the re-pin's value).

    .venv/Scripts/python.exe tools/_t4_1_series_arms.py [--arms 0,ALL] [--jobs 4]

Writes tools/_t4_1_series_arms_final.json (committed with the landing
record; a re-run writes its OWN record via --out).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"

ARMS = {
    "0": {"WRITE", "RUNG"},
    "WRITE": {"WRITE"},
    "RUNG": {"RUNG"},
    "ALL": set(),
}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
from backend.game_logic import alarm as AL
_write, _rung = AL.the_alarm_sounds, AL.an_alarmed_court_guarantees
def _counted_write():
    _c["write_reads"] += 1
    return False if "WRITE" in DOWN else _write()
def _counted_rung():
    _c["rung_reads"] += 1
    return False if "RUNG" in DOWN else _rung()
AL.the_alarm_sounds = _counted_write
AL.an_alarmed_court_guarantees = _counted_rung
_sound = AL.sound_the_alarm
def _counted_sound(*a, **k):
    out = _sound(*a, **k)
    if out:
        _c["alarms_written"] += 1
    return out
AL.sound_the_alarm = _counted_sound
_process = AL.process_alarm_guarantees
def _counted_process(world):
    out = _process(world)
    _c["guarantees_pledged"] += len(out)
    return out
AL.process_alarm_guarantees = _counted_process
_KEYS = ("write_reads", "rung_reads", "alarms_written", "guarantees_pledged")
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}}}}))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(down: set) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING",
              "PYTHONDONTWRITEBYTECODE", "INK_IRON_SEAMS"):
        env.pop(k, None)
    code = CHILD.format(down=sorted(down), runner=str(RUNNER))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, timeout=3600)
    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{stdout[-2000:]}\n{stderr[-3000:]}")
    lines = stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("REACH=")]
    payload["reach"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
    return payload


def first_divergence(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def prior_series() -> list:
    """HEAD's `BASELINE_SERIES` — the series before this slice, never the
    working tree's (the S14k rig's rule)."""
    rel = RUNNER.relative_to(ROOT).as_posix()
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                          capture_output=True, check=True).stdout.decode("utf-8")
    m = re.search(r"^BASELINE_SERIES = (\[[^\]]*\])", text, re.M)
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_t4_1_series_arms_final.json"))
    args = ap.parse_args()
    prior = prior_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior, "seams_down": {k: sorted(ARMS[k]) for k in names},
           "arms": {}}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a]), names)))
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        out["arms"][arm] = {"down": sorted(ARMS[arm]), "series": series,
                            "first_divergence_vs_prior": first_divergence(series, prior),
                            "reach": payload.get("reach")}
        print(f"arm {arm:>8}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {(payload.get('reach') or {}).get('counts')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

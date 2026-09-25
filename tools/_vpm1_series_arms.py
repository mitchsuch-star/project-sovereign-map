"""VP-M1 "The Fortunes of War" — the BASELINE_SERIES attribution.

GE-D1 (RULED September 25, 2026, during GE-V) gives every losing lead a
seeded wound-or-death roll on BOTH boards (GR5), so the 40-turn ambient
series MAY move — an AI marshal wounded at turn 9 fights a different turn
10. The plan's rule: one re-record, attributed by a flip experiment. Each
arm runs the ambient sim in its own hash-pinned subprocess
(`tests/test_ai_intent_threat_migration.py --emit-series`) with the lever
set IN THE CHILD before the sim boots (the slice-9 idiom), and COUNTS every
wound and every death the roll produced — so the cause of any movement is
measured, not asserted.

    .venv/Scripts/python.exe tools/_vpm1_series_arms.py [--arms all|0,1]

Arms:
    0  THE_GENERALS_ARE_MORTAL = False -> must reproduce the PRIOR recorded
       series byte-for-byte (the recorded list at the time of the run)
    1  THE_GENERALS_ARE_MORTAL = True  -> the shipped tree

Writes tools/_vpm1_series_arms.json (committed with the landing record).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"

ARMS = {0: False, 1: True}

CHILD = r"""
import sys, runpy, atexit
import backend.game_logic.fortunes_of_war as FW
FW.THE_GENERALS_ARE_MORTAL = {lever!r}
_counts = {{"wounded": 0, "killed": 0, "rolls": 0}}
_orig_wound, _orig_kill, _orig_roll = FW._wound, FW._kill, FW.roll
def _w(*a, **k):
    _counts["wounded"] += 1
    return _orig_wound(*a, **k)
def _k(*a, **k):
    _counts["killed"] += 1
    return _orig_kill(*a, **k)
def _r(*a, **k):
    _counts["rolls"] += 1
    return _orig_roll(*a, **k)
FW._wound, FW._kill, FW.roll = _w, _k, _r
atexit.register(lambda: print("FORTUNES=" + repr(_counts)))
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(lever: bool) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)
    code = CHILD.format(runner=str(RUNNER), lever=bool(lever))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("FORTUNES=")]
    payload["fortunes"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
    return payload


def first_divergence(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def recorded_series() -> list:
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_vpm1_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    print("recorded:", prior)
    results = {}
    for arm in wanted:
        payload = run_arm(ARMS[arm])
        results[arm] = payload
        print(f"arm {arm} (THE_GENERALS_ARE_MORTAL={ARMS[arm]}): {payload['series']}")
        print(f"   diverges from RECORDED at index {first_divergence(prior, payload['series'])}")
        print(f"   fortunes: {payload['fortunes']}")
        print(f"   provinces: {payload.get('provinces')}")
    Path(args.out).write_text(json.dumps({
        "recorded": prior,
        "arms": {str(k): v for k, v in results.items()},
        "levers": {str(k): {"THE_GENERALS_ARE_MORTAL": v} for k, v in ARMS.items()}},
        indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

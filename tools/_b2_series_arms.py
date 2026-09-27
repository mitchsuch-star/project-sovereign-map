"""PC15-10 B2 "The petition dies with its subject" — the BASELINE_SERIES
attribution (PETITION_POPUP_REVISIT_SPEC.md §7: "verify, do not assume, one
flip experiment per landed slice").

B2 is player-only by construction (the petition channel is the player's court;
F10 runs at load, which the ambient sim never does), so the series is expected
byte-identical on both arms. This script MEASURES it, and COUNTS what the
levers did on the ambient board — retirements by reason and supersedes — so
"byte-identical" carries its reason instead of being assumed.

    .venv/Scripts/python.exe tools/_b2_series_arms.py [--arms all|0,1]

Arms:
    0  B2 levers down (THE_PETITION_DIES_WITH_ITS_SUBJECT, THE_NEWER_WORD_SUPERSEDES)
    1  the shipped tree

Writes tools/_b2_series_arms.json (committed with the landing record).
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

ARMS = {
    0: {"subject": False, "supersede": False},
    1: {"subject": True, "supersede": True},
}

CHILD = r"""
import sys, runpy, atexit
import backend.game_logic.jealousy as J
J.THE_PETITION_DIES_WITH_ITS_SUBJECT = {subject!r}
J.THE_NEWER_WORD_SUPERSEDES = {supersede!r}
_counts = {{"retired": {{}}, "petitions_pushed": 0}}
_orig_rp = J.retire_petition
def _rp(world, petition, reason):
    _counts["retired"][reason] = _counts["retired"].get(reason, 0) + 1
    return _orig_rp(world, petition, reason)
J.retire_petition = _rp
_orig_push = J._push_petition
def _push(world, petition):
    out = _orig_push(world, petition)
    if out == J.PETITION_QUEUED and world.pending_marshal_petition is petition:
        _counts["petitions_pushed"] += 1
    return out
J._push_petition = _push
atexit.register(lambda: print("B2=" + repr(_counts)))
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(levers: dict) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)
    code = CHILD.format(runner=str(RUNNER), **levers)
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("B2=")]
    payload["b2"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
    return payload


def recorded_series() -> list:
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_b2_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    results = {}
    for arm in wanted:
        payload = run_arm(ARMS[arm])
        results[arm] = payload
        same = payload["series"] == prior
        print(f"arm {arm} {ARMS[arm]}: byte-identical to recorded = {same}")
        print(f"   counts: {payload['b2']}")
    Path(args.out).write_text(json.dumps({
        "recorded": prior,
        "arms": {str(k): v for k, v in results.items()},
        "levers": {str(k): v for k, v in ARMS.items()}},
        indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

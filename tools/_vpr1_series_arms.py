"""VP-R1 "The Road to Forty-Five" — the BASELINE_SERIES attribution.

Three levers landed in one slice (`docs/audits/VP_R1_PROBES_2026_09_25.md`):
(a) the muster preview names its odds — display only, cannot move a board;
(b) a raiding party holds no homeland (`movement_executor.
RAIDING_PARTY_HOLDS_NO_HOMELAND`) — read by the walk-in, the attack's
undefended exit, the landing and the AI's own capture rungs, so the 40-turn
ambient series MAY move; (c) the glory attack obeys the odds (`jealousy.
GLORY_ATTACK_OBEYS_THE_ODDS`) — read by the player processor and the AI's
P3.9 rung, so it MAY move. The plan's rule: one re-record, attributed by a
flip experiment. Each arm runs the ambient sim in its own hash-pinned
subprocess (`tests/test_ai_intent_threat_migration.py --emit-series`) with
the levers set IN THE CHILD before the sim boots (the slice-9 idiom), and
COUNTS what each lever did — raiding-party refusals, glory attacks held —
so the cause of any movement is measured, not asserted.

    .venv/Scripts/python.exe tools/_vpr1_series_arms.py [--arms all|0,1,2,3]

Arms:
    0  all three levers down  -> must reproduce the PRIOR recorded series
       byte-for-byte (the recorded list at the time of the run)
    1  (b) only
    2  (c) only
    3  the shipped tree ((a)+(b)+(c))

Writes tools/_vpr1_series_arms.json (committed with the landing record).
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
    0: {"a": False, "b": False, "c": False},
    1: {"a": False, "b": True, "c": False},
    2: {"a": False, "b": False, "c": True},
    3: {"a": True, "b": True, "c": True},
}

CHILD = r"""
import sys, runpy, atexit
import backend.commands.combat_executor as CE
import backend.commands.movement_executor as MV
import backend.game_logic.jealousy as J
CE.MUSTER_ROWS_NAME_THEIR_ODDS = {a!r}
MV.RAIDING_PARTY_HOLDS_NO_HOMELAND = {b!r}
J.GLORY_ATTACK_OBEYS_THE_ODDS = {c!r}
_counts = {{"raiding_refusals": 0, "raiding_checks": 0, "glory_held": 0, "glory_checks": 0}}
_orig_rp = MV.raiding_party_holds_no_ground
def _rp(*args, **kw):
    _counts["raiding_checks"] += 1
    out = _orig_rp(*args, **kw)
    if out:
        _counts["raiding_refusals"] += 1
    return out
MV.raiding_party_holds_no_ground = _rp
_orig_held = J.glory_attack_held_by_the_odds
def _held(*args, **kw):
    _counts["glory_checks"] += 1
    out = _orig_held(*args, **kw)
    if out is not None:
        _counts["glory_held"] += 1
    return out
J.glory_attack_held_by_the_odds = _held
atexit.register(lambda: print("VPR1=" + repr(_counts)))
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
                          capture_output=True, text=True, timeout=1200)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("VPR1=")]
    payload["vpr1"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_vpr1_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    print("recorded:", prior)
    results = {}
    for arm in wanted:
        payload = run_arm(ARMS[arm])
        results[arm] = payload
        print(f"arm {arm} {ARMS[arm]}: {payload['series']}")
        print(f"   diverges from RECORDED at index {first_divergence(prior, payload['series'])}")
        print(f"   counts: {payload['vpr1']}")
        print(f"   provinces: {payload.get('provinces')}")
    Path(args.out).write_text(json.dumps({
        "recorded": prior,
        "arms": {str(k): v for k, v in results.items()},
        "levers": {str(k): v for k, v in ARMS.items()}},
        indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

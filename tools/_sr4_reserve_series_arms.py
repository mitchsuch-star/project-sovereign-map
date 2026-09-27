"""The Chunk 4 reserve — the BASELINE_SERIES attribution.

Two reserve rows touch both boards (`docs/SCORE_MANDATE_PLAN.md` §2 Chunk 4,
the reserve; `docs/BUG_FIXES.md` AAR4-X1, AAR24-X2):
(a) AAR4-X1 — the captor no longer inherits the garrison: `capture_region`
    clears the loser's garrison at the ONE capture seam
    (`world_state.CAPTURE_CLEARS_THE_GARRISON`);
(b) AAR24-X2 — an assault honours the counter-punch the attack spent
    (`combat_executor.COUNTER_PUNCH_CREDITS_THE_ASSAULT`): the free action
    rides the garrison exit, as it rides the field and capture exits — which
    gives an AI cautious marshal back the action he was silently charged.
The other reserve rows are player-only or display-only (AAR24-X1's refusal
sits in the player's pre-objection battery — the AI's P4.25 has always kept
the rule; AAR24-X3 is the objection, which the AI never raises; AAR10-X1 and
AAR32-D1 are copy) and cannot move a board.

The plan's rule: one re-record, attributed by a flip experiment. Each arm
runs the ambient sim in its own hash-pinned subprocess (`tests/
test_ai_intent_threat_migration.py --emit-series`) with the levers set IN THE
CHILD before the sim boots (the slice-9 idiom), and COUNTS what each lever
did — garrisons a capture cleared (and the men in them), assaults launched on
a banked counter-punch and how many were credited — so the cause of any
movement is measured, not asserted.

    .venv/Scripts/python.exe tools/_sr4_reserve_series_arms.py [--arms all|0,1,2,3]

Arms:
    0  both down  -> must reproduce the PRIOR recorded series
    1  (a) only
    2  (b) only
    3  the shipped tree ((a)+(b))

Writes tools/_sr4_reserve_series_arms.json (committed with the landing record).
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
    0: {"a": False, "b": False},
    1: {"a": True, "b": False},
    2: {"a": False, "b": True},
    3: {"a": True, "b": True},
}

CHILD = r"""
import sys, runpy, atexit
import backend.models.world_state as WS
import backend.commands.combat_executor as CE
WS.CAPTURE_CLEARS_THE_GARRISON = {a!r}
CE.COUNTER_PUNCH_CREDITS_THE_ASSAULT = {b!r}
_counts = {{"captures": 0, "garrisons_cleared": 0, "men_cleared": 0,
           "assault_blows": 0, "assault_blows_credited": 0}}
_orig_cap = WS.WorldState.capture_region
def _cap(self, region_name, capturing_nation):
    region = self.get_region(region_name)
    before = int(getattr(region, "garrison_strength", 0) or 0) if region else 0
    held_by = getattr(region, "controller", None) if region else None
    out = _orig_cap(self, region_name, capturing_nation)
    _counts["captures"] += 1
    after = int(getattr(region, "garrison_strength", 0) or 0) if region else 0
    if held_by != capturing_nation and before > 0 and after == 0:
        _counts["garrisons_cleared"] += 1
        _counts["men_cleared"] += before
    return out
WS.WorldState.capture_region = _cap
_orig_atk = CE.CombatExecutor._execute_attack
def _atk(self, *a, **kw):
    marshal = a[0] if a else kw.get("marshal")
    banked = bool(marshal is not None and marshal.has_counter_punch())
    out = _orig_atk(self, *a, **kw)
    if banked and isinstance(out, dict) and any(
            isinstance(e, dict) and str(e.get("type", "")).startswith("garrison")
            for e in (out.get("events") or [])):
        _counts["assault_blows"] += 1
        if out.get("free_action"):
            _counts["assault_blows_credited"] += 1
    return out
CE.CombatExecutor._execute_attack = _atk
atexit.register(lambda: print("SR4R=" + repr(_counts)))
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
    counts = [ln for ln in lines if ln.startswith("SR4R=")]
    payload["sr4r"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sr4_reserve_series_arms.json"))
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
        print(f"   counts: {payload['sr4r']}")
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

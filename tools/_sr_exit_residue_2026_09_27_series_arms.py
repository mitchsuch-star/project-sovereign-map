"""The session exit of September 27, 2026 — its residue's BASELINE_SERIES
attribution.

SRX-10 (`combat_executor.A_SPENT_CORPS_DOES_NOT_SHARE_THE_FIELD`): the
muster's co-located arm reads the resolver's own exclusions — a corps broken,
retreated this turn or still recovering no longer "shares the field". The
defender's muster feeds `muster_odds`, which the glory gate reads on BOTH
boards (the AI's P3.9 glory-attack rung and the player's autonomous glory
attack), so the lever can move a decision. SRX-9 (the crisis card's title)
is display only and cannot.

The plan's rule: attributed by a flip experiment. Each arm runs the ambient
sim in its own hash-pinned subprocess (`tests/test_ai_intent_threat_
migration.py --emit-series`) with the lever set IN THE CHILD before the sim
boots, and COUNTS the lever's reach: the co-located spent corps the muster
read, and the glory-gate readings (with their unfavorable share).

    .venv/Scripts/python.exe tools/_sr_exit_residue_2026_09_27_series_arms.py

Arms: 0 the lever down (must reproduce the PRIOR recorded series); 1 the
shipped tree. Writes tools/_sr_exit_residue_2026_09_27_series_arms.json.
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"
ARMS = {0: {"a": False}, 1: {"a": True}}

CHILD = r"""
import sys, runpy, atexit
import backend.commands.combat_executor as CE
CE.A_SPENT_CORPS_DOES_NOT_SHARE_THE_FIELD = {a!r}
_counts = {{"muster_reason_calls": 0, "spent_colocated_reads": 0,
           "muster_odds_calls": 0, "muster_odds_unfavorable": 0}}
_orig_mr = CE.CombatExecutor._muster_reason
def _mr(self, candidate, primary, battle_region, nation, world):
    out = _orig_mr(self, candidate, primary, battle_region, nation, world)
    _counts["muster_reason_calls"] += 1
    if candidate.location == battle_region and (
            getattr(candidate, "broken", False)
            or getattr(candidate, "retreated_this_turn", False)
            or getattr(candidate, "retreat_recovery", 0) > 0):
        _counts["spent_colocated_reads"] += 1
    return out
CE.CombatExecutor._muster_reason = _mr
_orig_mo = CE.CombatExecutor.muster_odds
def _mo(self, marshal, enemy, world):
    out = _orig_mo(self, marshal, enemy, world)
    _counts["muster_odds_calls"] += 1
    if out.get("band") == "unfavorable":
        _counts["muster_odds_unfavorable"] += 1
    return out
CE.CombatExecutor.muster_odds = _mo
atexit.register(lambda: print("SRXR=" + repr(_counts)))
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
    counts = [ln for ln in lines if ln.startswith("SRXR=")]
    payload["srxr"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    prior = recorded_series()
    print("recorded:", prior)
    results = {}
    for arm, levers in ARMS.items():
        payload = run_arm(levers)
        results[arm] = payload
        print(f"arm {arm} {levers}: {payload['series']}")
        print(f"   diverges from RECORDED at index {first_divergence(prior, payload['series'])}")
        print(f"   counts: {payload['srxr']}")
        print(f"   provinces: {payload.get('provinces')}")
    out = ROOT / "tools" / "_sr_exit_residue_2026_09_27_series_arms.json"
    out.write_text(json.dumps({"recorded": prior,
                               "arms": {str(k): v for k, v in results.items()},
                               "levers": {str(k): v for k, v in ARMS.items()}},
                              indent=1), encoding="utf-8")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

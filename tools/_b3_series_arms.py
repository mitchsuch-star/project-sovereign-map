"""PC15-10 B3 "The crisis survives a new flow" — the BASELINE_SERIES
attribution (PETITION_POPUP_REVISIT_SPEC.md §7: one flip experiment per
landed slice).

B3 changes `DialogueManager.open_flow` (every caller is a player command) and
the stale-answer arm of the player's dialogue endpoint, and folds the sabotage
modal into one builder (the same dict). So the series is expected
byte-identical on both arms; this script MEASURES it and counts how often the
ambient board reaches the changed seams.

    .venv/Scripts/python.exe tools/_b3_series_arms.py [--arms all|0,1]

Arms:
    0  B3 levers down (HYBRIDS_SURVIVE_A_NEW_FLOW, THE_HYBRID_MODAL_RETURNS)
    1  the shipped tree

Writes tools/_b3_series_arms.json (committed with the landing record).
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
    0: {"hybrids": False, "modal": False},
    1: {"hybrids": True, "modal": True},
}

CHILD = r"""
import sys, runpy, atexit
import backend.models.dialogue_manager as DM
import backend.commands.diplomatic_executor as DX
DM.HYBRIDS_SURVIVE_A_NEW_FLOW = {hybrids!r}
DX.THE_HYBRID_MODAL_RETURNS = {modal!r}
_counts = {{"open_flow": 0, "open_flow_over_hybrid": 0, "reissue": 0}}
_orig_of = DM.DialogueManager.open_flow
def _of(self, dialogue):
    _counts["open_flow"] += 1
    prev = self._current
    if prev is not None and prev.get("type", "") in self.HYBRID_SOFT_STOP_TYPES:
        _counts["open_flow_over_hybrid"] += 1
    return _orig_of(self, dialogue)
DM.DialogueManager.open_flow = _of
_orig_re = DX._reissue_displaced_hybrid
def _re(*a, **kw):
    _counts["reissue"] += 1
    return _orig_re(*a, **kw)
DX._reissue_displaced_hybrid = _re
atexit.register(lambda: print("B3=" + repr(_counts)))
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
    counts = [ln for ln in lines if ln.startswith("B3=")]
    payload["b3"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
    return payload


def recorded_series() -> list:
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_b3_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    results = {}
    for arm in wanted:
        payload = run_arm(ARMS[arm])
        results[arm] = payload
        print(f"arm {arm} {ARMS[arm]}: byte-identical to recorded = {payload['series'] == prior}")
        print(f"   counts: {payload['b3']}")
    Path(args.out).write_text(json.dumps({
        "recorded": prior,
        "arms": {str(k): v for k, v in results.items()},
        "levers": {str(k): v for k, v in ARMS.items()}},
        indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

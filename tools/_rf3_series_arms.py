"""SR-5r RF-3 "The AI enacts" — the BASELINE_SERIES attribution
(REFORMS_SPEC.md §7 "Balance": "the series is re-recorded ONCE, with a
flip-arm attribution in the tools/_vpr1_series_arms.py pattern, counting
enactments and lapses per court").

    .venv/Scripts/python.exe tools/_rf3_series_arms.py [--arms all|0,1]

Arms:
    0  reforms.THE_AI_ENACTS down — no AI court enacts: must reproduce the
       recorded series byte for byte (nothing is in force at boot, and the
       passive France of the ambient board enacts nothing)
    1  the shipped rung

Writes tools/_rf3_series_arms.json (committed with the landing record).
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
    0: {"ai_enacts": False},
    1: {"ai_enacts": True},
}

CHILD = r"""
import sys, runpy, atexit
import backend.game_logic.reforms as R
R.THE_AI_ENACTS = {ai_enacts!r}
_log = {{"enacted": [], "lapsed": [], "repealed": []}}
_orig_enact = R.enact_law
def _enact(world, nation, row):
    out = _orig_enact(world, nation, row)
    _log["enacted"].append((int(world.current_turn), nation, str(row.get("id"))))
    return out
R.enact_law = _enact
_orig_lapse = R.process_law_lapses
def _lapses(world):
    before = {{(n, r.get("id")) for n in (world.reforms or {{}})
              for r in R.laws_in_force(world, n)}}
    out = _orig_lapse(world)
    after = {{(n, r.get("id")) for n in (world.reforms or {{}})
             for r in R.laws_in_force(world, n)}}
    for n, law in sorted(before - after):
        _log["lapsed"].append((int(world.current_turn), n, str(law)))
    return out
R.process_law_lapses = _lapses
atexit.register(lambda: print("RF3=" + repr(_log)))
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(levers: dict) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    code = CHILD.format(runner=str(RUNNER), **levers)
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=3600)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    log = [ln for ln in lines if ln.startswith("RF3=")]
    payload["rf3"] = ast.literal_eval(log[-1].split("=", 1)[1]) if log else None
    return payload


def recorded_series() -> list:
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_rf3_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    results = {}
    for arm in wanted:
        payload = run_arm(ARMS[arm])
        results[arm] = payload
        same = payload["series"] == prior
        diverge = next((i for i, (a, b) in enumerate(zip(payload["series"], prior)) if a != b), None)
        print(f"arm {arm} {ARMS[arm]}: byte-identical to recorded = {same}"
              + ("" if same else f" (first divergence at index {diverge})"))
        print(f"   enacted: {payload['rf3']['enacted'] if payload['rf3'] else None}")
        print(f"   lapsed:  {payload['rf3']['lapsed'] if payload['rf3'] else None}")
    Path(args.out).write_text(json.dumps({
        "recorded": prior,
        "arms": {str(k): v for k, v in results.items()},
        "levers": {str(k): v for k, v in ARMS.items()}},
        indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

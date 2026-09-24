"""F5 "Bohemia is not empty" — the BASELINE_SERIES attribution (plan D15).

Each arm runs the 40-turn ambient sim in its own hash-pinned subprocess
(`tests/test_ai_intent_threat_migration.py --emit-series`, the pin's own
runner) with the F5 levers set IN THE CHILD before the sim boots — the
slice-9 idiom (a test must never edit a production source file to flip a
lever).

    .venv/Scripts/python.exe tools/_f5_series_arms.py [--arms all|0,1,2,3]

Arms (levers: C = enemy_ai.ONE_WALK_IN_PER_CORPS_PER_TURN,
              L = enemy_ai.THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK):

    0  both DOWN      -> must reproduce the PRIOR series byte-for-byte
    1  C only         -> the walk-in cap alone
    2  L only         -> the literal strength check alone
    3  C + L          -> the NEW series (shipped)

Prints each arm's series and the first index at which it diverges from the
prior recorded series and from the shipped tree.
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
    0: dict(C=False, L=False),
    1: dict(C=True, L=False),
    2: dict(C=False, L=True),
    3: dict(C=True, L=True),
}

CHILD = r"""
import sys, runpy, importlib
import backend.ai.enemy_ai as EA
EA.ONE_WALK_IN_PER_CORPS_PER_TURN = {C}
EA.THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK = {L}
for _spec in {extra!r}:
    _mod, _attr = _spec.rsplit(".", 1)
    _name, _val = _attr.split("=", 1)
    setattr(importlib.import_module(_mod), _name, {{"True": True, "False": False}}.get(_val, _val))
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""

EXTRA: list = []


def run_arm(levers: dict) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)
    code = CHILD.format(runner=str(RUNNER), extra=list(EXTRA), **levers)
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    line = [ln for ln in proc.stdout.splitlines() if ln.startswith("PAYLOAD=")][-1]
    return json.loads(line[len("PAYLOAD="):])


def first_divergence(a: list[int], b: list[int]):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def recorded_series() -> list[int]:
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_f5_series_arms.json"))
    ap.add_argument("--set", action="append", default=[],
                    help="extra module.ATTR=True|False lever set in the child "
                         "(e.g. backend.game_logic.jealousy.THE_REOPENED_QUARREL_SAYS_SO=False)")
    args = ap.parse_args()
    EXTRA.extend(args.set)
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    print("recorded:", prior)
    results = {}
    for arm in wanted:
        payload = run_arm(ARMS[arm])
        results[arm] = payload
        series = payload["series"]
        print(f"arm {arm} {ARMS[arm]}: {series}")
        print(f"   diverges from RECORDED at index {first_divergence(prior, series)}")
        print(f"   provinces: {payload.get('provinces')}")
    if 3 in results:
        for arm, payload in results.items():
            print(f"arm {arm} vs shipped tree: diverges at index "
                  f"{first_divergence(results[3]['series'], payload['series'])}")
    Path(args.out).write_text(json.dumps({
        "recorded": prior,
        "arms": {str(k): v for k, v in results.items()},
        "levers": {str(k): v for k, v in ARMS.items()}}, indent=1),
        encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

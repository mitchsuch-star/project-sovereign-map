"""F4 "The fuse is longer" — the four-arm BASELINE_SERIES attribution (plan D15).

Each arm runs the 40-turn ambient sim in its own hash-pinned subprocess
(`tests/test_ai_intent_threat_migration.py --emit-series`, the pin's own
runner) with the F4 levers set IN THE CHILD before the sim boots — the slice-9
idiom (a test must never edit a production source file to flip a lever).

    .venv/Scripts/python.exe tools/_f4_series_arms.py [--arms all|0,1,...]

Arms (levers: R = dotation.EXPECTATION_RISES_ON_DEEDS, C =
dotation.EXPECTATION_RISE_COOLDOWN_ACTIVE, P =
jealousy.THE_COLLECTIVE_PETITION_WAITS, U = dotation.THE_UNMET_BLOCK_WAITS):

    0  all four DOWN          -> must reproduce the PRIOR series byte-for-byte
    1  R only                 -> the deed rule + first-turn floor alone
    2  R + C                  -> plus the cooldown
    3  R + C + P              -> plus the petition gate
    4  full tree (R+C+P+U)    -> the NEW series
    5  P only                 -> the petition gate alone (is it inert ambiently?)
    6  U only                 -> the dispatch gate alone (display-only by design)

Prints each arm's series and the first index at which it diverges from the
prior recorded series and from the full tree.
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
    0: dict(R=False, C=False, P=False, U=False),
    1: dict(R=True, C=False, P=False, U=False),
    2: dict(R=True, C=True, P=False, U=False),
    3: dict(R=True, C=True, P=True, U=False),
    4: dict(R=True, C=True, P=True, U=True),
    5: dict(R=False, C=False, P=True, U=False),
    6: dict(R=False, C=False, P=False, U=True),
}

CHILD = r"""
import sys, runpy
import backend.game_logic.dotation as D
import backend.game_logic.jealousy as J
D.EXPECTATION_RISES_ON_DEEDS = {R}
D.EXPECTATION_RISE_COOLDOWN_ACTIVE = {C}
J.THE_COLLECTIVE_PETITION_WAITS = {P}
D.THE_UNMET_BLOCK_WAITS = {U}
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(levers: dict) -> list[int]:
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
                          capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    line = [ln for ln in proc.stdout.splitlines() if ln.startswith("PAYLOAD=")][-1]
    return json.loads(line[len("PAYLOAD="):])["series"]


def first_divergence(a: list[int], b: list[int]):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def recorded_series() -> list[int]:
    """The series the committed pin file carries (a literal there)."""
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_f4_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    print("recorded:", prior)
    results = {}
    for arm in wanted:
        series = run_arm(ARMS[arm])
        results[arm] = series
        print(f"arm {arm} {ARMS[arm]}: {series}")
        print(f"   diverges from RECORDED at index {first_divergence(prior, series)}")
    if 4 in results:
        for arm, series in results.items():
            print(f"arm {arm} vs full tree: diverges at index {first_divergence(results[4], series)}")
    Path(args.out).write_text(json.dumps({"recorded": prior,
                                          "arms": {str(k): v for k, v in results.items()},
                                          "levers": {str(k): v for k, v in ARMS.items()}}, indent=1),
                              encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

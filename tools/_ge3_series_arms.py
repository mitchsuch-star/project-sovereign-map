"""GE-3 "The Congress of Paris" — the BASELINE_SERIES attribution (plan D15).

GE-3 is one of the three slices the plan allows ONE re-record, "with a
flip-experiment attribution — the pressure hooks are dormant with no
Congress, arm 0 byte-identical". Each arm runs the 40-turn ambient sim in
its own hash-pinned subprocess (`tests/test_ai_intent_threat_migration.py
--emit-series`, the pin's own runner) with the Congress levers set IN THE
CHILD before the sim boots (the slice-9 idiom — a test never edits a
production source file to flip a lever), and COUNTS every write the
Congress makes to `world.congress` (`congress._store`) — so dormancy is
measured, not asserted.

    .venv/Scripts/python.exe tools/_ge3_series_arms.py [--arms all|0,1,2]

Arms (every lever in backend/game_logic/congress.py):

    0  all DOWN   -> must reproduce the RECORDED series byte-for-byte
    1  SITS only  -> the summons/tick/surfaces with no pressure hooks
    2  all UP     -> the shipped tree

Writes tools/_ge3_series_arms.json (committed with the landing record).

What the arms can and cannot show (GE-3 review #68): the ambient 40-turn
board never reaches 50 titled provinces, never summons and never ratifies a
France–great-power peace, so arms 1 and 2 equal arm 0 BY CONSTRUCTION — they
measure DORMANCY (zero Congress writes, the series unmoved), not an
attribution of the live pressure hooks. Those are pinned by the driven arms
(`tests/test_congress_review_round.py::TestTheArmsDriven`) and the hook pins.
The shipped tree (arm 2) also carries the review round's one change outside
the Congress, `world_state.SIEGE_ENDS_WITH_THE_WAR` — the series is
byte-identical with it.
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

LEVERS = ("THE_CONGRESS_SITS", "THE_CONGRESS_HARDENS_REFUSERS",
          "THE_CONGRESS_LOWERS_THE_GATE", "LONDON_FUNDS_THE_REFUSERS",
          "THE_BILLS_COME_DUE", "THE_UNIVERSAL_MONARCHY")

ARMS = {
    0: {lever: False for lever in LEVERS},
    1: {lever: (lever == "THE_CONGRESS_SITS") for lever in LEVERS},
    2: {lever: True for lever in LEVERS},
}

CHILD = r"""
import sys, runpy, atexit
import backend.game_logic.congress as CG
for _name, _val in {levers!r}.items():
    setattr(CG, _name, _val)
_writes = [0]
_orig_store = CG._store
def _counting_store(world):
    _writes[0] += 1
    return _orig_store(world)
CG._store = _counting_store
atexit.register(lambda: print("CONGRESS_WRITES=" + str(_writes[0])))
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
    code = CHILD.format(runner=str(RUNNER), levers=dict(levers))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    writes = [ln for ln in lines if ln.startswith("CONGRESS_WRITES=")]
    payload["congress_writes"] = int(writes[-1].split("=", 1)[1]) if writes else None
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_ge3_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    print("recorded:", prior)
    results = {}
    for arm in wanted:
        payload = run_arm(ARMS[arm])
        results[arm] = payload
        print(f"arm {arm}: {payload['series']}")
        print(f"   diverges from RECORDED at index {first_divergence(prior, payload['series'])}")
        print(f"   congress writes: {payload['congress_writes']}")
        print(f"   provinces: {payload.get('provinces')}")
    Path(args.out).write_text(json.dumps({
        "recorded": prior,
        "arms": {str(k): v for k, v in results.items()},
        "levers": {str(k): v for k, v in ARMS.items()}}, indent=1),
        encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

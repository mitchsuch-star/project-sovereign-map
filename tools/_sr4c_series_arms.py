"""SR-4c "The drama's fuse" — the BASELINE_SERIES attribution.

Three mechanical levers landed in one slice (`docs/SCORE_MANDATE_PLAN.md` §2
Chunk 4 SR-4c; `backend/game_logic/jealousy.py`):
(a) THE_LAUREL_FLOOR — an engagement below `battle_scale.is_a_battle` size
    that was not a decisive exchange earns and costs no glory (both boards);
(b) THE_CROWN_WANTS_LAURELS — the crown needs CROWN_MIN_GLORY (both boards:
    the crown's +1 shock/defense/administration reaches combat);
(c) THE_AUDIENCE_WAITS — a player marshal who asked for an audience does not
    ask again for AUDIENCE_COOLDOWN_TURNS (player-only: the petition channel
    is the player's court).
Plus the copy lever THE_FIRES_SAY_WHY, which moves no board. The plan's rule:
one re-record, attributed by a flip experiment. Each arm runs the ambient sim
in its own hash-pinned subprocess (`tests/test_ai_intent_threat_migration.py
--emit-series`) with the levers set IN THE CHILD before the sim boots (the
slice-9 idiom), and COUNTS what each lever did, so the cause of any movement
is measured, not asserted.

    .venv/Scripts/python.exe tools/_sr4c_series_arms.py [--arms all|0,1,2,3,4]

Arms:
    0  all levers down  -> must reproduce the PRIOR recorded series
    1  (a) only
    2  (b) only
    3  (c) only
    4  the shipped tree ((a)+(b)+(c) + copy)

Writes tools/_sr4c_series_arms.json (committed with the landing record).
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
    0: {"a": False, "b": False, "c": False, "w": False},
    1: {"a": True, "b": False, "c": False, "w": False},
    2: {"a": False, "b": True, "c": False, "w": False},
    3: {"a": False, "b": False, "c": True, "w": False},
    4: {"a": True, "b": True, "c": True, "w": True},
}

CHILD = r"""
import sys, runpy, atexit
import backend.game_logic.jealousy as J
J.THE_LAUREL_FLOOR = {a!r}
J.THE_CROWN_WANTS_LAURELS = {b!r}
J.THE_AUDIENCE_WAITS = {c!r}
J.THE_FIRES_SAY_WHY = {w!r}
_counts = {{"glory_calls": 0, "sub_floor": 0,
           "crowns_below_floor": 0, "audience_waits": 0, "fires": 0}}
_orig_rbg = J.record_battle_glory
def _rbg(world, attacker, defender, aw, dw, ac, dc, *a, **kw):
    _counts["glory_calls"] += 1
    if not J.is_laurel(ac, dc):
        _counts["sub_floor"] += 1
    return _orig_rbg(world, attacker, defender, aw, dw, ac, dc, *a, **kw)
J.record_battle_glory = _rbg
_orig_rc = J.recompute_crowns
def _rc(world):
    out = _orig_rc(world)
    for nation in {{m.nation for m in world.marshals.values()}}:
        ladder = J.get_nation_ladder(world, nation)
        if ladder and 0 < ladder[0][1] < J.CROWN_MIN_GLORY and (
                len(ladder) == 1 or ladder[0][1] > ladder[1][1]):
            _counts["crowns_below_floor"] += 1
    return out
J.recompute_crowns = _rc
_orig_aw = J.audience_wait
def _aw(*a, **kw):
    out = _orig_aw(*a, **kw)
    if out > 0:
        _counts["audience_waits"] += 1
    return out
J.audience_wait = _aw
_orig_aj = J.apply_jealousy
def _aj(*a, **kw):
    _counts["fires"] += 1
    return _orig_aj(*a, **kw)
J.apply_jealousy = _aj
atexit.register(lambda: print("SR4C=" + repr(_counts)))
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
    counts = [ln for ln in lines if ln.startswith("SR4C=")]
    payload["sr4c"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sr4c_series_arms.json"))
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
        print(f"   counts: {payload['sr4c']}")
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

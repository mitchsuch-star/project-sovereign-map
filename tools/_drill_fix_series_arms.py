"""The AI drill fix (user-directed, Sept 27, 2026) — the BASELINE_SERIES
attribution, in the tools/_rf3_series_arms.py pattern: every lever set in the
child, each arm run on the recorded ambient board, and every drill an AI
court orders counted with the nearest corps at war with it.

    .venv/Scripts/python.exe tools/_drill_fix_series_arms.py [--arms all|0,1,...]

Arms (levers: H = enemy_ai.AI_DRILLS_TO_HEAL, R = AI_DRILL_READS_THE_REACH,
D = DRILL_IS_THE_DAYS_WORK, P = EVERY_DEFAULT_LEAVES_THE_DRILL,
C = combat.DRILL_PENALTY_READ_BEFORE_THE_CLEAR):
    0    every lever down — must reproduce the recorded series byte for byte
    1    the shipped fix, every lever up
    H/R/D/P/C  that lever alone

Writes tools/_drill_fix_series_arms.json.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"

LEVERS = ("H", "R", "D", "P", "C")
ARMS = {"0": "", "1": "HRDPC", "H": "H", "R": "R", "D": "D", "P": "P", "C": "C"}

CHILD = r"""
import sys, runpy, atexit
import backend.ai.enemy_ai as EA
import backend.game_logic.combat as CB
import backend.commands.tactical_executor as TE
import backend.models.world_state as WS
up = set({up!r})
EA.AI_DRILLS_TO_HEAL = "H" in up
EA.AI_DRILL_READS_THE_REACH = "R" in up
EA.DRILL_IS_THE_DAYS_WORK = "D" in up
EA.EVERY_DEFAULT_LEAVES_THE_DRILL = "P" in up
CB.DRILL_PENALTY_READ_BEFORE_THE_CLEAR = "C" in up
_log = {{"drills": [], "completed": [], "within_reach": 0}}
_orig = TE.TacticalExecutor._execute_drill
def _drill(self, command, game_state):
    world = game_state.get("world")
    m = world.get_marshal(command.get("marshal")) if world else None
    before = (m.nation, m.name, int(world.current_turn), int(getattr(m, "morale", 0) or 0)) if m else None
    threat = EA.drill_reach_threat(world, m) if m else None
    near = None
    if m:
        best = None
        for o in world.marshals.values():
            if o.nation == m.nation or int(o.strength or 0) <= 0 or getattr(o, "captured_by", ""):
                continue
            if not world.is_at_war(m.nation, o.nation):
                continue
            d = world.get_distance(m.location, o.location)
            if best is None or d < best[0]:
                best = (d, o.name, int(getattr(o, "movement_range", 1) or 1))
        near = best
    out = _orig(self, command, game_state)
    if m and out.get("success") and m.nation != world.player_nation:
        _log["drills"].append([*before, near, threat.name if threat else None])
        if threat is not None:
            _log["within_reach"] += 1
    return out
TE.TacticalExecutor._execute_drill = _drill
_orig_apply = WS.WorldState._apply_drill_morale
def _apply(self, marshal):
    gain = _orig_apply(self, marshal)
    if marshal.nation != self.player_nation:
        _log["completed"].append([marshal.nation, marshal.name, int(self.current_turn), int(gain)])
    return gain
WS.WorldState._apply_drill_morale = _apply
atexit.register(lambda: print("DRILLFIX=" + repr(_log)))
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(up: str) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    code = CHILD.format(runner=str(RUNNER), up=up)
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=3600)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    log = [ln for ln in lines if ln.startswith("DRILLFIX=")]
    payload["drillfix"] = ast.literal_eval(log[-1].split("=", 1)[1]) if log else None
    return payload


def recorded_series() -> list:
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_drill_fix_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else args.arms.split(",")
    prior = recorded_series()
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {arm: pool.submit(run_arm, ARMS[arm]) for arm in wanted}
        results = {arm: fut.result() for arm, fut in futures.items()}
    for arm in wanted:
        payload = results[arm]
        same = payload["series"] == prior
        diverge = next((i for i, (a, b) in enumerate(zip(payload["series"], prior)) if a != b), None)
        log = payload["drillfix"] or {}
        print(f"arm {arm} (up: {ARMS[arm] or '-'}): byte-identical to recorded = {same}"
              + ("" if same else f" (first divergence at index {diverge})"))
        print(f"   AI drills ordered: {len(log.get('drills', []))}, "
              f"within reach of a corps at war: {log.get('within_reach')}, "
              f"completed: {len(log.get('completed', []))}")
        for d in log.get("drills", []):
            print(f"      {d}")
    Path(args.out).write_text(json.dumps({
        "recorded": prior,
        "arms": results,
        "levers": ARMS}, indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

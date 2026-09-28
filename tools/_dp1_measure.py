"""SR-5r DP-1 "The bank" — what a fuller AI pool unlocks on the ambient board
(REFORMS_SPEC §9 "Measure before landing").

    .venv/Scripts/python.exe tools/_dp1_measure.py

Runs the 40-turn ambient board exactly as the BASELINE_SERIES runner does
(the 1805 scenario, the historical seed, the per-turn re-seed 10_000 + turn),
once with `diplomacy.DIPLOMATIC_POINTS_CARRY` down and once shipped, in
hash-pinned children. Every AI court's diplomatic-point pool is wrapped in a
dict that counts each SPEND (a write that lowers a court's pool — the four
AI sites §9 names) and records the pool each court holds at each refill.
Prints, per arm: spends per court, points spent, the mean refilled pool, and
the threat series. Writes tools/_dp1_measure.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHILD = r'''
import contextlib, io, json, random, sys
sys.path.insert(0, r"{root}")
import backend.game_logic.diplomacy as DG
DG.DIPLOMATIC_POINTS_CARRY = {carry!r}
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.turn_manager import TurnManager

spends = {{}}
points = {{}}
pools = {{}}

class Counted(dict):
    def __setitem__(self, key, value):
        before = int(self.get(key, 0) or 0)
        if int(value) < before and not _REFILL[0]:
            spends[key] = spends.get(key, 0) + 1
            points[key] = points.get(key, 0) + (before - int(value))
        super().__setitem__(key, value)

_REFILL = [False]
_orig_regen = DG._process_dp_regen
def _regen(world):
    _REFILL[0] = True
    try:
        _orig_regen(world)
    finally:
        _REFILL[0] = False
    for n, v in (world.nation_dp or {{}}).items():
        pools.setdefault(n, []).append(int(v))
DG._process_dp_regen = _regen

with contextlib.redirect_stdout(io.StringIO()):
    world = WorldState.from_scenario(r"{scenario}")
    world.nation_dp = Counted(getattr(world, "nation_dp", {{}}) or {{}})
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    gs = {{"world": world, "executor": executor}}
series = [int(world.threat_level)]
for turn in range(40):
    random.seed(10_000 + turn)
    with contextlib.redirect_stdout(io.StringIO()):
        tm.end_turn(gs)
    if not isinstance(world.nation_dp, Counted):
        world.nation_dp = Counted(world.nation_dp)
    series.append(int(world.threat_level))
print("DP1=" + json.dumps({{
    "spends": spends, "points": points,
    "mean_pool": {{n: round(sum(v) / len(v), 2) for n, v in pools.items() if v}},
    "series": series}}))
'''


def run(carry: bool) -> dict:
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT), SOVEREIGN_SEED="historical",
               LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    scenario = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
    code = CHILD.format(root=str(ROOT), carry=carry, scenario=str(scenario))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(proc.stdout[-2000:] + proc.stderr[-3000:])
    line = [ln for ln in proc.stdout.splitlines() if ln.startswith("DP1=")][-1]
    return json.loads(line[len("DP1="):])


def main() -> int:
    out = {"off": run(False), "on": run(True)}
    for arm, data in out.items():
        print(f"[{arm}] spends {data['spends']} (total {sum(data['spends'].values())})")
        print(f"[{arm}] points {data['points']} (total {sum(data['points'].values())})")
        print(f"[{arm}] mean pool {data['mean_pool']}")
    print("series identical:", out["off"]["series"] == out["on"]["series"])
    (ROOT / "tools" / "_dp1_measure.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

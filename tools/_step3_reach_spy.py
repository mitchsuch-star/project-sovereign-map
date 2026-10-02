"""Score Finish Step 3 — the ambient REACH spy (October 2, 2026).

Runs the 40-turn ambient series (the `test_ai_intent_threat_migration.py`
`--emit-series` runner, hash-pinned) with counters on every production
seam Step 3 touches, so "the ambient board never …" is a NUMBER before
and after each lever:

    rs3_field_win_over_standing_garrison   a field win whose target province
                                           keeps a garrison that still fights
    iq5r1_reinforced_distributions         casualty pools split over >1 corps
    xr3_in_place_captures                  undefended captures where the corps
                                           already stood on the province
    aard8_small_detachment_assaults        AI assaults on a detachment garrison
                                           under the surrender floor
    cq22_ai_drills_in_aggressive_stance    AI drill orders taken in AGGRESSIVE
    cq22_ai_drills                         AI drill orders taken, any stance

    python tools/_step3_reach_spy.py [--levers up|down]
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

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = {up!r}
LEVERS = {levers!r}
for mod_name, name in LEVERS:
    mod = importlib.import_module(mod_name)
    if hasattr(mod, name):
        setattr(mod, name, UP)
import backend.commands.combat_executor as CE
import backend.commands.tactical_executor as TE
import backend.game_logic.garrison_report as GR
from backend.models.marshal import Stance
_c = collections.Counter()

_o_dist = CE.CombatExecutor._distribute_casualties
def _dist(self, raw, participants):
    live = [p for p in participants if getattr(p, "strength", 0) > 0]
    if len(live) > 1:
        _c["iq5r1_reinforced_distributions"] += 1
    return _o_dist(self, raw, participants)
CE.CombatExecutor._distribute_casualties = _dist

_o_cap = CE.CombatExecutor._attempt_region_capture
def _cap(self, marshal, region_name, world, game_state, had_garrison=False, auto_secure=False):
    region = world.get_region(region_name)
    if region is not None and had_garrison and region.controller != marshal.nation \
            and GR.garrison_fights(region):
        _c["rs3_field_win_over_standing_garrison"] += 1
    return _o_cap(self, marshal, region_name, world, game_state,
                  had_garrison=had_garrison, auto_secure=auto_secure)
CE.CombatExecutor._attempt_region_capture = _cap

_o_gar = CE.CombatExecutor._resolve_garrison_combat
def _gar(self, marshal, target_region, world, game_state):
    if getattr(target_region, "garrison_detachment", False) and \
            int(getattr(target_region, "garrison_strength", 0) or 0) < 500 \
            and marshal.nation != world.player_nation:
        _c["aard8_small_detachment_assaults"] += 1
    return _o_gar(self, marshal, target_region, world, game_state)
CE.CombatExecutor._resolve_garrison_combat = _gar

_o_drill = TE.TacticalExecutor._execute_drill
def _drill(self, command, game_state):
    out = _o_drill(self, command, game_state)
    world = game_state.get("world")
    m = world.marshals.get(command.get("marshal")) if world else None
    if out.get("success") and m is not None and m.nation != world.player_nation:
        _c["cq22_ai_drills"] += 1
        if getattr(m, "stance", None) == Stance.AGGRESSIVE:
            _c["cq22_ai_drills_in_aggressive_stance"] += 1
    return out
TE.TacticalExecutor._execute_drill = _drill

_o_attr = None
try:
    import backend.commands.movement_executor as ME
    _o_attr = ME.MovementExecutor._calculate_movement_attrition
    def _attr(self, marshal, destination_region, world, is_retreat=False):
        if marshal.location == destination_region:
            _c["xr3_in_place_attrition_calls"] += 1
        return _o_attr(self, marshal, destination_region, world, is_retreat=is_retreat)
    ME.MovementExecutor._calculate_movement_attrition = _attr
except Exception as exc:
    _c["xr3_spy_error"] = 1
def _dump():
    print("STEP3=" + repr(dict(_c)))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""

LEVERS: list = []


def run(up: bool) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(k, None)
    code = CHILD.format(up=up, levers=LEVERS, runner=str(RUNNER))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(f"run failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("STEP3=")]
    payload["step3"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levers", default="up", choices=("up", "down"))
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    payload = run(args.levers == "up")
    print("series:", payload["series"])
    print("provinces:", payload.get("provinces"))
    print("counts:", payload.get("step3"))
    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

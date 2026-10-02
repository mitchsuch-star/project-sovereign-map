"""Score Finish Step 3 "Europe acts without France" — the BASELINE_SERIES
attribution (October 2, 2026). Step 3 MOVES the series by design: every
lever is set IN THE CHILD before the 40-turn ambient sim boots (the slice-9
idiom), one arm per named lever, and every seam's reach is COUNTED, so
each lever's share of the move is a number and arm 0 must reproduce the
recorded (pre-Step-3) series byte for byte.

    python tools/_step3_series_arms.py [--arms 0,A,B,C,D,E,F,G,ALL]

Arms:
    0    every Step 3 lever down -> must reproduce the recorded series
    A    RS-3   A_FIELD_WIN_HALTS_BEFORE_THE_WORKS alone
    B    AAR-D8 A_SMALL_GARRISON_SURRENDERS alone
    C    AAR-D8 AI_ATTACKS_OBEY_THE_MUSTER_GATE alone
    D    CQ-22  ONE_STANCE_RULE_FOR_DRILL alone
    E    IQ5-R1 BLEED_BY_THE_MEN_COMMITTED alone
    F    XR-3   AN_IN_PLACE_CAPTURE_MARCHES_NOWHERE alone
    G    SR-G7  THE_ARMED_PEACE alone
    H    SR-7c  DISPERSION_IS_NOT_PUNISHED alone
    I    SR-7a  A_HELD_CORPS_IS_NOT_IDLE alone (the dither guard)
    J    SF-LB-1 A_DESIGN_IS_ASKED_BEFORE_IT_IS_FOUGHT alone
    K    SF-LB-1 A_REFUSAL_HARDENS_THE_ASKER alone
    L    SF-LB-1 AN_ALLY_IS_NOT_COVETED alone
    M    SF-LB-1 A_CONTAIN_DESIGN_SLEEPS_IN_THE_ARMED_PEACE alone
    ALL  the shipped tree (every lever up) -> the series to record

Writes tools/_step3_series_arms_final.json (committed with the landing record).
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

LEVERS = {
    "A": ("backend.commands.combat_executor", "A_FIELD_WIN_HALTS_BEFORE_THE_WORKS"),
    "B": ("backend.game_logic.garrison_report", "A_SMALL_GARRISON_SURRENDERS"),
    "C": ("backend.ai.enemy_ai", "AI_ATTACKS_OBEY_THE_MUSTER_GATE"),
    "D": ("backend.commands.tactical_executor", "ONE_STANCE_RULE_FOR_DRILL"),
    "E": ("backend.commands.combat_executor", "BLEED_BY_THE_MEN_COMMITTED"),
    "F": ("backend.commands.combat_executor", "AN_IN_PLACE_CAPTURE_MARCHES_NOWHERE"),
    "G": ("backend.game_logic.coalition", "THE_ARMED_PEACE"),
    "H": ("backend.models.world_state", "DISPERSION_IS_NOT_PUNISHED"),
    "I": ("backend.ai.enemy_ai", "A_HELD_CORPS_IS_NOT_IDLE"),
    "J": ("backend.game_logic.ai_diplomacy", "A_DESIGN_IS_ASKED_BEFORE_IT_IS_FOUGHT"),
    "K": ("backend.game_logic.intent", "A_REFUSAL_HARDENS_THE_ASKER"),
    "L": ("backend.game_logic.agendas", "AN_ALLY_IS_NOT_COVETED"),
    "M": ("backend.game_logic.agendas", "A_CONTAIN_DESIGN_SLEEPS_IN_THE_ARMED_PEACE"),
}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = {up!r}
ALL = {all_levers!r}
for key, (mod_name, name) in ALL.items():
    mod = importlib.import_module(mod_name)
    setattr(mod, name, key in UP)
import backend.commands.combat_executor as CE
import backend.commands.tactical_executor as TE
import backend.game_logic.garrison_report as GR
import backend.game_logic.coalition as CO
import backend.ai.enemy_ai as EA
from backend.models.marshal import Stance
_c = collections.Counter()

_o_works = CE.works_halt_line
def _works(world, marshal, region):
    out = _o_works(world, marshal, region)
    if out:
        _c["A_works_halts"] += 1
    return out
CE.works_halt_line = _works

_o_surr = GR.detachment_surrenders
def _surr(region):
    out = _o_surr(region)
    if out:
        _c["B_surrenders_read"] += 1
    return out
GR.detachment_surrenders = _surr

_o_gar = CE.CombatExecutor._resolve_garrison_combat
def _gar(self, marshal, target_region, world, game_state):
    if getattr(target_region, "garrison_detachment", False) and \
            int(getattr(target_region, "garrison_strength", 0) or 0) < 500:
        _c["B_small_detachment_assaults"] += 1
    return _o_gar(self, marshal, target_region, world, game_state)
CE.CombatExecutor._resolve_garrison_combat = _gar

_o_find = EA.EnemyAI._find_attack_opportunity
def _find(self, marshal, nation, world):
    out = _o_find(self, marshal, nation, world)
    if out is None and self._get_effective_personality(marshal, world) == "cautious":
        _c["C_cautious_p4_none"] += 1
    return out
EA.EnemyAI._find_attack_opportunity = _find

_o_drill = TE.TacticalExecutor._execute_drill
def _drill(self, command, game_state):
    out = _o_drill(self, command, game_state)
    world = game_state.get("world")
    m = world.marshals.get(command.get("marshal")) if world else None
    if m is not None and m.nation != world.player_nation:
        _c["D_ai_drill_orders"] += 1
        if getattr(m, "stance", None) == Stance.AGGRESSIVE:
            _c["D_ai_drill_orders_aggressive"] += 1
            if out.get("success"):
                _c["D_ai_drills_in_aggressive_taken"] += 1
    return out
TE.TacticalExecutor._execute_drill = _drill

_o_dist = CE.CombatExecutor._distribute_casualties
def _dist(self, raw, participants, lead=None):
    live = [p for p in participants if getattr(p, "strength", 0) > 0]
    if len(live) > 1:
        _c["E_reinforced_splits"] += 1
    return _o_dist(self, raw, participants, lead=lead)
CE.CombatExecutor._distribute_casualties = _dist

from backend.models.marshal import Marshal as _M
_o_move = _M.move_to
def _move(self, new_location):
    if self.location == new_location:
        _c["F_in_place_moves"] += 1
    return _o_move(self, new_location)
_M.move_to = _move

_o_read = CO.armed_peace_reading
def _read(world):
    out = _o_read(world)
    if out.get("holds"):
        _c["G_armed_peace_holds_reads"] += 1
        if out.get("rise"):
            _c["G_armed_peace_rise_reads"] += 1
    return out
CO.armed_peace_reading = _read

_o_press = None
try:
    from backend.models.world_state import WorldState as _WS
    _o_press = _WS.crowding_press
    def _press(self, region, marshals_here):
        out = _o_press(self, region, marshals_here)
        if len(marshals_here) >= 3:
            _c["H_press_reads_3plus"] += 1
            if out[0] < len(marshals_here) or out[1] > 2:
                _c["H_press_relieved"] += 1
        return out
    _WS.crowding_press = _press
    _o_friendly = _WS.retreat_soil_is_friendly
    def _friendly(self, marshal_nation, controller):
        out = _o_friendly(self, marshal_nation, controller)
        if out and controller != marshal_nation:
            _c["H_retreat_ally_soil_friendly"] += 1
        return out
    _WS.retreat_soil_is_friendly = _friendly
except Exception:
    _c["H_spy_error"] = 1
import backend.game_logic.ai_diplomacy as AD
_o_eval = AD._evaluate_ai_ai_proposal
def _eval(a, b, world):
    out = _o_eval(a, b, world)
    if out and out.get("type") == "design_ask":
        _c["J_design_asks"] += 1
    return out
AD._evaluate_ai_ai_proposal = _eval
import backend.game_logic.agendas as AGD
_o_acq = AGD._acquire_active
def _acq(world, nation, regions):
    out = _o_acq(world, nation, regions)
    return out
AGD._acquire_active = _acq
_o_cont = AGD._contain_active
def _cont(world, nation, share_floor):
    out = _o_cont(world, nation, share_floor)
    if not out:
        _c["M_contain_inactive_reads"] += 1
    return out
AGD._contain_active = _cont
def _dump():
    print("STEP3=" + repr(dict(_c)))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(up: set) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(k, None)
    code = CHILD.format(up=sorted(up), all_levers=LEVERS, runner=str(RUNNER))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("STEP3=")]
    payload["step3"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--arms", default="0,A,B,C,D,E,F,G,H,I,J,K,L,M,ALL")
    ap.add_argument("--prior", default="", help="JSON list: the PRE-Step-3 series to compare against (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_step3_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    out = {"prior": prior, "levers": {k: f"{m}.{n}" for k, (m, n) in LEVERS.items()}, "arms": {}}
    for arm in [x.strip() for x in args.arms.split(",") if x.strip()]:
        up = set(LEVERS) if arm == "ALL" else (set() if arm == "0" else {arm})
        print(f"arm {arm} (up: {sorted(up) or 'none'}) ...", flush=True)
        payload = run_arm(up)
        series = payload["series"]
        div = first_divergence(series, prior)
        out["arms"][arm] = {
            "levers_up": sorted(up), "series": series,
            "first_divergence_vs_prior": div,
            "provinces": payload.get("provinces"),
            "step3": payload.get("step3"),
        }
        print(f"  divergence vs prior: {div}; counts: {payload.get('step3')}", flush=True)
        Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

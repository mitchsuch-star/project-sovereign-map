"""Score Finish Step 7 slice 10 ("the AI's own accounting", SF7-X33 + SF7-X34 + SF7-X35)
— the BASELINE_SERIES attribution (October 5, 2026).

Two levers, each set IN THE CHILD before the 40-turn ambient sim boots (the
slice-9 idiom of every series tool since WO slice 9):

    R = `combat_executor.CombatExecutor.A_REFUSED_RAID_LEAVES_THE_GARRISON`
        (SF7-X33: a raiding party's refused capture no longer empties the
        garrison it could not take);
    S = `enemy_ai.THE_STAGNATION_COUNTS_A_CAPTURE`
        (SF7-X34: an attack that took a province is an achievement to the
        stagnation tracker);
    P = `diplomacy.A_NEW_WAR_HAS_A_PURPOSE`
        (SF7-X35: a war opened by any road but a declaration gets the
        purpose a declaration would have given it).

Arm 0 (both down) must reproduce the recorded series byte for byte. The reach
is COUNTED in the child: every raid refusal the attack seam issues (and how
many found a garrison standing), and every stagnation reading the two rules
would have judged differently.

    python tools/_sf7_s10_series_arms.py [--arms 0,R,S,P,ALL] [--prior JSON]

Writes tools/_sf7_s10_series_arms_final.json (committed with the landing
record). Run with --prior <the pre-slice series> once BASELINE_SERIES is
re-recorded (the default reads the recorded constant).
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
    "R": ("backend.commands.combat_executor", "CombatExecutor.A_REFUSED_RAID_LEAVES_THE_GARRISON"),
    "S": ("backend.ai.enemy_ai", "THE_STAGNATION_COUNTS_A_CAPTURE"),
    "P": ("backend.game_logic.diplomacy", "A_NEW_WAR_HAS_A_PURPOSE"),
}
ARMS = {"0": set(), "R": {"R"}, "S": {"S"}, "P": {"P"}, "ALL": set(LEVERS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib, inspect
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, path) in ALL.items():
    obj = importlib.import_module(mod_name)
    parts = path.split(".")
    for p in parts[:-1]:
        obj = getattr(obj, p)
    setattr(obj, parts[-1], key in UP)
import backend.commands.movement_executor as MV
import backend.ai.enemy_ai as EA
_c = collections.Counter()
_o_refusal = MV.raiding_party_refusal
def _refusal(marshal, region_name):
    caller = inspect.stack()[1].filename.replace("\\", "/")
    if caller.endswith("combat_executor.py"):
        _c["raid_refused_at_the_attack|" + str(marshal.nation)] += 1
    return _o_refusal(marshal, region_name)
MV.raiding_party_refusal = _refusal
_o_ach = EA.attack_achieved_something
def _ach(events, marshal_name):
    here = bool(EA.THE_STAGNATION_COUNTS_A_CAPTURE)
    EA.THE_STAGNATION_COUNTS_A_CAPTURE = not here
    try:
        other = _o_ach(events, marshal_name)
    finally:
        EA.THE_STAGNATION_COUNTS_A_CAPTURE = here
    out = _o_ach(events, marshal_name)
    _c["stagnation_reads"] += 1
    if out != other:
        _c["stagnation_reading_differs|" + ("capture_counts" if out else "capture_ignored")] += 1
    return out
EA.attack_achieved_something = _ach
# The decision the counter feeds most directly: the P7.5 stagnation
# breaker (>= 2), counted where it is reached and where it fires (the
# cautious advance at >= 1 and the artillery override at >= 3 read the
# same counter; the board's provinces below show what all three moved).
_o_stag = EA.EnemyAI._get_stagnation_action
def _stag(self, marshal, nation, world, stagnation, personality):
    out = _o_stag(self, marshal, nation, world, stagnation, personality)
    _c['p75_reached|' + str(nation)] += 1
    if out:
        _c['p75_fired|' + str(nation)] += 1
    return out
EA.EnemyAI._get_stagnation_action = _stag
# SF7-X35: every purpose the LIVE war-entry seam assigns (the load
# migration never runs in this sim).
import backend.game_logic.diplomacy as DP
_o_purpose = DP.give_the_war_its_purpose
def _purpose(world, a, b):
    out = _o_purpose(world, a, b)
    if out:
        _c['war_given_a_purpose'] += 1
    return out
DP.give_the_war_its_purpose = _purpose
def _dump():
    print("REACH=" + repr(dict(_c)))
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
    counts = [ln for ln in lines if ln.startswith("REACH=")]
    payload["reach"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sf7_s10_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    out = {"prior": prior,
           "levers": {k: f"{m}.{n}" for k, (m, n) in LEVERS.items()},
           "arm_levers": {k: sorted(v) for k, v in ARMS.items()}, "arms": {}}
    for arm in [x.strip() for x in args.arms.split(",") if x.strip()]:
        up = ARMS[arm]
        print(f"arm {arm} (up: {sorted(up) or 'none'}) ...", flush=True)
        payload = run_arm(up)
        series = payload["series"]
        out["arms"][arm] = {
            "levers_up": sorted(up), "series": series,
            "first_divergence_vs_prior": first_divergence(series, prior),
            "provinces": payload.get("provinces"),
            "reach": payload.get("reach"),
        }
        print(f"   divergence vs prior: {out['arms'][arm]['first_divergence_vs_prior']}"
              f"   reach: {payload.get('reach')}", flush=True)
    if "ALL" in out["arms"]:
        for arm, rec in out["arms"].items():
            rec["first_divergence_vs_all"] = first_divergence(
                rec["series"], out["arms"]["ALL"]["series"])
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

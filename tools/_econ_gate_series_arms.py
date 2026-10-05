"""The economy gate (October 5, 2026 — `docs/audits/ECONOMY_GATE_2026_10_05.md`;
gate record `docs/SCORE_FINISH_SPEC.md` §6.8) — the BASELINE_SERIES attribution.

Every behaviour change the gate lands sits behind its own module-level lever,
each set IN THE CHILD before the 40-turn ambient sim boots (the WO slice 9
idiom every series tool since has used):

    T = coalition.A_TRUCE_BINDS_THE_LEAGUE              (EA-19: a truce partner does not qualify)
    S = coalition.A_STANDING_LEAGUE_IS_NOT_REOPENED     (EA-19 rider: copy only)
    N = coalition.A_LEAGUE_NEEDS_TWO_MEMBERS            (EA-19 rider: no one-court league)
    A = enemy_ai.THE_LEAGUE_AIMS_AT_ITS_ENEMY           (EAD-7: never at a fellow member)
    R = enemy_ai.THE_MARCH_READS_THE_LAWFUL_ROAD        (EAD-7: the lawful road)
    U = coalition.THE_LEAGUE_SAYS_WHO_HAS_NOT_MARCHED   (EAD-8: display only)
    P = world_state.CAMPAIGN_PAY_ON_FOREIGN_SOIL        (EAD-1: campaign pay)
    C = ledger.THE_CHARGES_NAME_THEIR_PRICE             (EAD-2: display only)
    E = coalition.THE_ARMY_LINE_IS_A_THIRD              (EAD-4: the army line at a third)
    M = enemy_ai.A_COURT_WITHOUT_A_GENERAL_MAY_COMMISSION (EA-7's recovery path)

Arm 0 (every lever down) must reproduce the recorded series byte for byte.
The reach is COUNTED in the child — for a lever whose arm is byte-identical,
the count says whether its code was reached at all.

    python tools/_econ_gate_series_arms.py [--arms 0,T,...,ALL] [--jobs 4] [--prior JSON]

Writes tools/_econ_gate_series_arms_final.json (committed with the landing
record). Run with --prior <the pre-gate series> once BASELINE_SERIES is
re-recorded (the default reads the recorded constant).
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

LEVERS = {
    "T": ("backend.game_logic.coalition", "A_TRUCE_BINDS_THE_LEAGUE"),
    "S": ("backend.game_logic.coalition", "A_STANDING_LEAGUE_IS_NOT_REOPENED"),
    "N": ("backend.game_logic.coalition", "A_LEAGUE_NEEDS_TWO_MEMBERS"),
    "A": ("backend.ai.enemy_ai", "THE_LEAGUE_AIMS_AT_ITS_ENEMY"),
    "R": ("backend.ai.enemy_ai", "THE_MARCH_READS_THE_LAWFUL_ROAD"),
    "U": ("backend.game_logic.coalition", "THE_LEAGUE_SAYS_WHO_HAS_NOT_MARCHED"),
    "P": ("backend.models.world_state", "CAMPAIGN_PAY_ON_FOREIGN_SOIL"),
    "C": ("backend.game_logic.ledger", "THE_CHARGES_NAME_THEIR_PRICE"),
    "E": ("backend.game_logic.coalition", "THE_ARMY_LINE_IS_A_THIRD"),
    "M": ("backend.ai.enemy_ai", "A_COURT_WITHOUT_A_GENERAL_MAY_COMMISSION"),
}
ARMS = {"0": set(), **{k: {k} for k in LEVERS}, "ALL": set(LEVERS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, path) in ALL.items():
    obj = importlib.import_module(mod_name)
    parts = path.split(".")
    for p in parts[:-1]:
        obj = getattr(obj, p)
    setattr(obj, parts[-1], key in UP)
import backend.game_logic.diplomacy as DP
import backend.game_logic.coalition as CO
import backend.models.world_state as WS
import backend.ai.enemy_ai as EA
_c = collections.Counter()
_seen = set()

# T: the truce gate refusing a court at the qualifying gate (forced on).
_o_q = CO.qualifies_for_coalition
def _q(nation, world, target=None, relation_shift=0):
    out = _o_q(nation, world, target=target, relation_shift=relation_shift)
    if out is False or out:
        tgt = target or world.player_nation
        if DP.declaration_cooldown_left(world, nation, tgt) > 0 and nation != tgt:
            key = ("truce", int(world.current_turn), nation, tgt)
            if key not in _seen:
                _seen.add(key)
                _c["truce_bound_court_turns|" + nation] += 1
    return out
CO.qualifies_for_coalition = _q

# N: a league whose declarations failed below two members.
_o_fc = CO.form_coalition
def _fc(qualifying, world, target=None):
    out = _o_fc(qualifying, world, target=target)
    msg = str((out or {{}}).get("message", ""))
    if "the declarations failed" in msg:
        _c["league_refused_below_two"] += 1
    if (out or {{}}).get("success"):
        _c["league_formed"] += 1
    return out
CO.form_coalition = _fc

# A / R: the march plan and the fellow filter, per decision.
_o_mp = EA.EnemyAI._march_plan
def _mp(self, world, nation, marshal, target_region):
    plan = _o_mp(self, world, nation, marshal, target_region)
    if len(plan) > 1:
        _c["march_has_a_lawful_road"] += 1
        lawful = EA.lawful_distances_to(world, nation, target_region, marshal.location)
        if lawful.get(marshal.location) != world.get_distance(marshal.location, target_region):
            _c["lawful_road_longer_than_straight|" + nation] += 1
    else:
        _c["march_plan_straight_only"] += 1
    return plan
EA.EnemyAI._march_plan = _mp
_o_lf = EA.league_fellows
def _lf(world, nation):
    out = _o_lf(world, nation)
    if out:
        _c["league_fellows_nonempty|" + nation] += 1
    return out
EA.league_fellows = _lf

# P: the campaign pay billed, per nation and turn.
_o_up = WS.WorldState.calculate_turn_upkeep
def _up(self, nation=None):
    out = _o_up(self, nation)
    pay = int(out.get("campaign_pay", 0) or 0)
    if pay:
        n = nation or self.player_nation
        key = ("pay", int(self.current_turn), n)
        if key not in _seen:
            _seen.add(key)
            _c["campaign_pay_turns|" + n] += 1
    return out
WS.WorldState.calculate_turn_upkeep = _up

# E: a court standing between a third and 0.40 of Europe's men at the tick.
_o_et = CO._establishment_threat
def _et(world, france):
    totals = CO._standing_strength_by_nation(world)
    europe = sum(totals.values())
    if europe >= CO.ESTABLISHMENT_MIN_EUROPE_STRENGTH:
        for n, s in totals.items():
            share = s / europe
            if CO.ESTABLISHMENT_THREAT_SHARE_THIRD < share <= CO.ESTABLISHMENT_THREAT_SHARE:
                _c["between_a_third_and_040|" + n] += 1
    return _o_et(world, france)
CO._establishment_threat = _et

# M: a court with no general commissioning one.
_o_co = EA.EnemyAI.execute_commission_only
def _co(self, nation, world, game_state):
    out = _o_co(self, nation, world, game_state)
    _c["marshal_less_court_turns|" + nation] += 1
    if out:
        _c["marshal_less_commission|" + nation] += 1
    return out
EA.EnemyAI.execute_commission_only = _co

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
    # Bytes, decoded leniently: the child prints in the console's code page
    # and the PAYLOAD / REACH lines are ASCII (json / repr), so a stray
    # em dash in the game's own prints never kills the reader.
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, timeout=3600)
    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{stdout[-2000:]}\n{stderr[-3000:]}")
    lines = stdout.splitlines()
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
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--prior", default="", help="JSON list: the pre-gate series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_econ_gate_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior,
           "levers": {k: f"{m}.{n}" for k, (m, n) in LEVERS.items()},
           "arm_levers": {k: sorted(ARMS[k]) for k in names}, "arms": {}}
    print(f"running {len(names)} arms, {args.jobs} at a time ...", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a]), names)))
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        out["arms"][arm] = {
            "levers_up": sorted(ARMS[arm]), "series": series,
            "first_divergence_vs_prior": first_divergence(series, prior),
            "provinces": payload.get("provinces"),
            "reach": payload.get("reach"),
        }
        print(f"arm {arm:>3}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}",
              flush=True)
    if "ALL" in out["arms"]:
        for arm, rec in out["arms"].items():
            rec["first_divergence_vs_all"] = first_divergence(
                rec["series"], out["arms"]["ALL"]["series"])
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

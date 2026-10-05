"""The economy audit (October 5, 2026 — `docs/audits/ECONOMY_AUDIT_2026_10_05.md`)
— the BASELINE_SERIES attribution.

Every behaviour change the audit lands sits behind its own module-level lever,
each set IN THE CHILD before the 40-turn ambient sim boots (the WO slice 9
idiom every series tool since has used):

    D = coalition.THE_LEAGUE_DECLARES_IN_ITS_OWN_RIGHT   (SFR-DR1: no offensive cascade)
    F = coalition.A_FAILED_DECLARATION_IS_NOT_A_MEMBER   (SFR-DR1 rider)
    S = coalition.A_SUBSIDY_PAYS_A_COURT_THAT_FIGHTS      (EA-12)
    B = instruments.THE_SUBSIDIES_ARE_ON_THE_BOOKS        (EA-1: AI Nets read the transfers)
    T = diplomacy.A_PEACE_EARNS_NO_TRADE                  (EA-3, N5)
    G = diplomacy.THE_DEAD_DO_NOT_TRADE                   (EA-3, N4)
    C = diplomacy.THE_SYSTEM_CHARGES_ONLY_THE_TRADE_EARNED (EA-4, N6)
    V = ledger.THE_VASSAL_PAYS_ON_ITS_OWN_BOOKS           (EA-5, N2)
    K = contingent.THE_SATELLITE_PAYS_ON_ITS_OWN_BILL     (EA-6, N3)
    W = war_council.THE_BEAT_READS_THE_MORNINGS_CHEST     (SFR-D23)
    A = world_state.ARREARS_ARE_REMEMBERED                (EA-8)
    M = world_state.A_MARKET_PAYS_ITS_OWN_KEEP            (EA-9)
    O = enemy_ai.THE_AI_BUILDS_NO_WATCHTOWERS             (EA-10)
    R = enemy_ai.THE_COURT_ARMS_WITH_ITS_PURSE            (EA-11)

Arm 0 (every lever down) must reproduce the recorded series byte for byte.
The reach is COUNTED in the child — for a lever whose arm is byte-identical,
the count says whether its code was reached at all.

    python tools/_econ_audit_series_arms.py [--arms 0,D,...,ALL] [--jobs 8] [--prior JSON]

Writes tools/_econ_audit_series_arms_final.json (committed with the landing
record). Run with --prior <the pre-audit series> once BASELINE_SERIES is
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
    "D": ("backend.game_logic.coalition", "THE_LEAGUE_DECLARES_IN_ITS_OWN_RIGHT"),
    "F": ("backend.game_logic.coalition", "A_FAILED_DECLARATION_IS_NOT_A_MEMBER"),
    "S": ("backend.game_logic.coalition", "A_SUBSIDY_PAYS_A_COURT_THAT_FIGHTS"),
    "B": ("backend.game_logic.instruments", "THE_SUBSIDIES_ARE_ON_THE_BOOKS"),
    "T": ("backend.game_logic.diplomacy", "A_PEACE_EARNS_NO_TRADE"),
    "G": ("backend.game_logic.diplomacy", "THE_DEAD_DO_NOT_TRADE"),
    "C": ("backend.game_logic.diplomacy", "THE_SYSTEM_CHARGES_ONLY_THE_TRADE_EARNED"),
    "V": ("backend.game_logic.ledger", "THE_VASSAL_PAYS_ON_ITS_OWN_BOOKS"),
    "K": ("backend.game_logic.contingent", "THE_SATELLITE_PAYS_ON_ITS_OWN_BILL"),
    "W": ("backend.game_logic.war_council", "THE_BEAT_READS_THE_MORNINGS_CHEST"),
    "A": ("backend.models.world_state", "ARREARS_ARE_REMEMBERED"),
    "M": ("backend.models.world_state", "A_MARKET_PAYS_ITS_OWN_KEEP"),
    "O": ("backend.ai.enemy_ai", "THE_AI_BUILDS_NO_WATCHTOWERS"),
    "R": ("backend.ai.enemy_ai", "THE_COURT_ARMS_WITH_ITS_PURSE"),
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
import backend.game_logic.instruments as IN
import backend.game_logic.contingent as CT
import backend.game_logic.war_council as WC
import backend.models.world_state as WS
import backend.ai.enemy_ai as EA
import backend.commands.economy_executor as EE
_c = collections.Counter()
_seen = set()

def _flip(mod, name, value, fn, *a):
    here = getattr(mod, name)
    setattr(mod, name, value)
    try:
        return fn(*a)
    finally:
        setattr(mod, name, here)

# D / F: the league's own declarations (form_coalition's calls only).
_o_dw = DP.declare_war
def _dw(world, attacker, target, *a, **kw):
    out = _o_dw(world, attacker, target, *a, **kw)
    if sys._getframe(1).f_code.co_name == "form_coalition":
        _c["league_declaration|" + str(attacker)] += 1
        if not (out or {{}}).get("success"):
            _c["league_declaration_failed|" + str(attacker)] += 1
    return out
DP.declare_war = _dw

# S: the paymaster's recipient, read both ways at the payment.
_o_bs = CO._process_british_subsidy
def _bs(world):
    a = _flip(CO, "A_SUBSIDY_PAYS_A_COURT_THAT_FIGHTS", True, CO.get_british_subsidy_recipient, world)
    b = _flip(CO, "A_SUBSIDY_PAYS_A_COURT_THAT_FIGHTS", False, CO.get_british_subsidy_recipient, world)
    if a != b:
        _c["paymaster_recipient_differs|" + str(b) + "->" + str(a)] += 1
    return _o_bs(world)
CO._process_british_subsidy = _bs

# B: the subsidies term on any Net read (forced on), per nation and turn.
_o_sub = IN.subsidies_for
def _sub(world, nation, applied):
    full = _flip(IN, "THE_SUBSIDIES_ARE_ON_THE_BOOKS", True, _o_sub, world, nation, applied)
    if full.get("net"):
        key = ("sub", int(world.current_turn), nation)
        if key not in _seen:
            _seen.add(key)
            _c["subsidy_term_nonzero_turns|" + nation] += 1
    return _o_sub(world, nation, applied)
IN.subsidies_for = _sub

# T / G: the trade the advance PAYS, read both ways.
_o_tb = DP.calculate_trade_breakdown
def _tb(world):
    out = _o_tb(world)
    try:
        payer = sys._getframe(2).f_code.co_name
    except ValueError:
        payer = ""
    if payer == "process_trade_income":
        for key, lever in (("T", "A_PEACE_EARNS_NO_TRADE"), ("G", "THE_DEAD_DO_NOT_TRADE")):
            other = _flip(DP, lever, not getattr(DP, lever), _o_tb, world)
            if other != out:
                _c["trade_paid_differs|" + key] += 1
    return out
DP.calculate_trade_breakdown = _tb

# C: turns the System has members at all.
_o_cs = DP.apply_continental_system
def _cs(world):
    if getattr(world, "continental_system_members", None):
        _c["cs_turns_with_members"] += 1
    return _o_cs(world)
DP.apply_continental_system = _cs

# K: a satellite's contingent on its own bill (forced on), per vassal and turn.
_o_cpb = CT.contingents_paid_by
def _cpb(world, vassal):
    full = _flip(CT, "THE_SATELLITE_PAYS_ON_ITS_OWN_BILL", True, _o_cpb, world, vassal)
    if full:
        key = ("cpb", int(world.current_turn), vassal)
        if key not in _seen:
            _seen.add(key)
            _c["contingent_billed_turns|" + vassal] += 1
    return _o_cpb(world, vassal)
CT.contingents_paid_by = _cpb

# W: the crisis beats the morning's chest prices.
_o_brew = WC._emit_crisis_brewing
def _brew(world, coveter, record, events):
    _c["crisis_brewing_beats"] += 1
    return _o_brew(world, coveter, record, events)
WC._emit_crisis_brewing = _brew

# A: the desertion reading, both ways.
_o_des = WS.WorldState.deserts_now
def _des(self, nation):
    out = _o_des(self, nation)
    other = _flip(WS, "ARREARS_ARE_REMEMBERED", not WS.ARREARS_ARE_REMEMBERED, _o_des, self, nation)
    if out != other:
        _c["desertion_reading_differs|" + nation] += 1
    if out:
        _c["desertion|" + nation] += 1
    return out
WS.WorldState.deserts_now = _des

# M / O: what stands at each turn's end — markets, towers.
_o_adv = WS.WorldState.advance_turn
def _adv(self, *a, **kw):
    out = _o_adv(self, *a, **kw)
    player = getattr(self, "player_nation", "France")
    for r in self.regions.values():
        for b in getattr(r, "buildings", []) or []:
            if b.get("type") == "market":
                _c["market_turns|" + ("player" if r.controller == player else "ai")] += 1
        if getattr(r, "watchtower", "none") not in ("none", None, ""):
            _c["watchtower_turns|" + ("player" if r.controller == player else "ai")] += 1
    return out
WS.WorldState.advance_turn = _adv

_o_wt = EE.EconomyExecutor._execute_build_watchtower
def _wt(self, command, game_state, region_name):
    out = _o_wt(self, command, game_state, region_name)
    if command.get("_acting_nation") and (out or {{}}).get("success"):
        _c["ai_watchtower_built"] += 1
    return out
EE.EconomyExecutor._execute_build_watchtower = _wt

# R: the arming rung's levies, per court.
_o_arm = EA.EnemyAI._court_arms_with_its_purse
def _arm(self, nation, world):
    out = _o_arm(self, nation, world)
    if out:
        _c["court_arms|" + nation] += 1
    return out
EA.EnemyAI._court_arms_with_its_purse = _arm

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
                          capture_output=True, text=True, timeout=3600)
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
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--prior", default="", help="JSON list: the pre-audit series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_econ_audit_series_arms_final.json"))
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

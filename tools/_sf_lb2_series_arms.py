"""SF-LB-2 "The Defenceless Prize" — the BASELINE_SERIES attribution
(October 3, 2026; SCORE_FINISH_SPEC.md §6.4).

The slice MOVES the series by design (Prussia takes Hanover — the gate
record says so), so the series is re-recorded ONCE from this script's ALL
arm, and every other arm says what moved it: every lever is set IN THE
CHILD before the 40-turn ambient sim boots (the slice-9 idiom), one arm
per lever, and every seam's reach is COUNTED — arm 0 must reproduce the
recorded (SR-7d) series byte for byte.

    python tools/_sf_lb2_series_arms.py [--arms 0,W,C,K,R,N,WC,WCK,WCKR,ALL]

Arms:
    0    every SF-LB-2 lever down -> must reproduce the recorded series
    W    intent.A_HOLDER_WITHOUT_AN_ARMY_IS_A_PRIZE alone (the +10)
    C    war_council.THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE alone
    K    ai_diplomacy.A_COURT_ASKS_BEFORE_IT_DEMANDS alone
    R    war_council.A_CRISIS_OPENS_ONLY_WHERE_IT_CAN_DECLARE alone
    N    combat_executor.A_PROVINCE_OUTRANKS_A_FRIENDLY_NAMESAKE alone
    WC   the two §6.4 clauses together, the ask arm down
    WCK  the §6.4 clauses + the ask arm, the opening guard down
    WCKR the four war-council/intent levers, the namesake fix down
    ALL  the shipped tree -> the series to record

Writes tools/_sf_lb2_series_arms_final.json (committed with the landing
record).
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
    "W": ("backend.game_logic.intent", "A_HOLDER_WITHOUT_AN_ARMY_IS_A_PRIZE"),
    "C": ("backend.game_logic.war_council", "THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE"),
    "K": ("backend.game_logic.ai_diplomacy", "A_COURT_ASKS_BEFORE_IT_DEMANDS"),
    "R": ("backend.game_logic.war_council", "A_CRISIS_OPENS_ONLY_WHERE_IT_CAN_DECLARE"),
    "N": ("backend.commands.combat_executor", "A_PROVINCE_OUTRANKS_A_FRIENDLY_NAMESAKE"),
}
ARMS = {
    "0": set(),
    "W": {"W"}, "C": {"C"}, "K": {"K"}, "R": {"R"}, "N": {"N"},
    "WC": {"W", "C"},
    "WCK": {"W", "C", "K"},
    "WCKR": {"W", "C", "K", "R"},
    "ALL": {"W", "C", "K", "R", "N"},
}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = {up!r}
ALL = {all_levers!r}
for key, (mod_name, name) in ALL.items():
    mod = importlib.import_module(mod_name)
    setattr(mod, name, key in UP)
import backend.game_logic.war_council as WC
import backend.game_logic.intent as IN
_c = collections.Counter()

_o_out = WC.holder_outmatched
def _out(world, asker, holder):
    out = _o_out(world, asker, holder)
    if out:
        _c["outmatched_reads|" + str(asker) + ">" + str(holder)] += 1
    return out
WC.holder_outmatched = _out

_o_rung = WC.crisis_rung_holds
def _rung(world, coveter, view):
    out = _o_rung(world, coveter, view)
    if out and view.price != "fight":
        _c["coerce_rung_holds|" + str(coveter)] += 1
    return out
WC.crisis_rung_holds = _rung

_o_proc = WC.process_war_council
def _proc(world):
    before = {{k: dict(v) for k, v in (getattr(world, "war_intents", {{}}) or {{}}).items()}}
    out = _o_proc(world)
    for k, v in (getattr(world, "war_intents", {{}}) or {{}}).items():
        if k not in before:
            _c["crisis_opened|" + str(k) + ">" + str(v.get("target")) + "@" + str(v.get("opened_at_price"))] += 1
    for e in out:
        if e.get("type") == "war_declaration" or (e.get("type") or "").endswith("declared"):
            _c["council_events|" + str(e.get("type"))] += 1
    return out
WC.process_war_council = _proc

def _dump():
    print("SFLB2=" + repr(dict(_c)))
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
    counts = [ln for ln in lines if ln.startswith("SFLB2=")]
    payload["sflb2"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--arms", default="0,W,C,K,R,N,WC,WCK,WCKR,ALL")
    ap.add_argument("--prior", default="", help="JSON list: the PRE-SF-LB-2 series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sf_lb2_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    out = {"prior": prior, "levers": {k: f"{m}.{n}" for k, (m, n) in LEVERS.items()},
           "arm_levers": {k: sorted(v) for k, v in ARMS.items()}, "arms": {}}
    for arm in [x.strip() for x in args.arms.split(",") if x.strip()]:
        up = ARMS[arm]
        print(f"arm {arm} (up: {sorted(up) or 'none'}) ...", flush=True)
        payload = run_arm(up)
        series = payload["series"]
        div = first_divergence(series, prior)
        out["arms"][arm] = {
            "levers_up": sorted(up), "series": series,
            "first_divergence_vs_prior": div,
            "provinces": payload.get("provinces"),
            "sflb2": payload.get("sflb2"),
        }
        print(f"  divergence vs prior: {div}; counts: {payload.get('sflb2')}", flush=True)
        Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

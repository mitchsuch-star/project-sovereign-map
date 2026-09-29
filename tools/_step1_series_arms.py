"""Score Finish Step 1 "The peace holds" — the BASELINE_SERIES attribution
(September 29, 2026). Every Step 1 lever is set IN THE CHILD before the
40-turn ambient sim boots (the slice-9 idiom), and each production seam the
step touched is COUNTED — so "the ambient board never …" is a number.

    python3 tools/_step1_series_arms.py [--arms all|0,1,...]

Levers:
    a  diplomacy.THE_CASCADE_KEEPS_A_FRESH_PEACE          (RS-1)
    b  settlement_ratify.THE_SETTLEMENT_WRITES_THE_PAIR_COOLDOWN (RS-1)
    c  game_end.A_CONGRESS_WAR_CONTESTS_NOT_BREAKS        (RS-2)
    d  congress.A_PEACE_THAT_KEEPS_THE_CAPITAL_RECOGNIZES (RS-D1)
    e  settlement_scoring.A_RETAINED_CAPITAL_IS_A_CAPITAL_LOST (RS-D1 rider)
    f  ai_diplomacy.NO_OFFER_THE_TABLE_REFUSES            (SF-V1)
    g  ai_diplomacy.THE_LETTER_COVERS_ONLY_THE_PAIRS_AT_WAR
       + THE_LETTER_IS_RATIFIABLE_WHEN_SENT               (SF-V5)
    h  congress.THE_SUMMONS_NAMES_THE_LOWERED_GATE + THE_ALARM_LINE_IS_A_FORECAST
       + THE_LEVERS_QUOTE_THEIR_TURNS                     (RS-10 / RS-16 / RS-D1 copy)

Arms:
    0  all levers down -> must reproduce the recorded series byte-for-byte
    1  the shipped tree (all up)
    2..9  one lever up at a time (a..h) — run when arm 1 diverges

Writes tools/_step1_series_arms.json (committed with the landing record).
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

KEYS = "abcdefgh"
ARMS = {0: {k: False for k in KEYS}, 1: {k: True for k in KEYS}}
for i, k in enumerate(KEYS):
    ARMS[2 + i] = {kk: (kk == k) for kk in KEYS}

CHILD = r"""
import sys, runpy, atexit, collections
import backend.game_logic.diplomacy as DP
import backend.game_logic.settlement_ratify as SR
import backend.game_logic.game_end as GE
import backend.game_logic.congress as CG
import backend.game_logic.settlement_scoring as SS
import backend.game_logic.ai_diplomacy as AD
DP.THE_CASCADE_KEEPS_A_FRESH_PEACE = {a!r}
SR.THE_SETTLEMENT_WRITES_THE_PAIR_COOLDOWN = {b!r}
GE.A_CONGRESS_WAR_CONTESTS_NOT_BREAKS = {c!r}
CG.A_PEACE_THAT_KEEPS_THE_CAPITAL_RECOGNIZES = {d!r}
SS.A_RETAINED_CAPITAL_IS_A_CAPITAL_LOST = {e!r}
AD.NO_OFFER_THE_TABLE_REFUSES = {f!r}
AD.THE_LETTER_COVERS_ONLY_THE_PAIRS_AT_WAR = {g!r}
AD.THE_LETTER_IS_RATIFIABLE_WHEN_SENT = {g!r}
CG.THE_SUMMONS_NAMES_THE_LOWERED_GATE = {h!r}
CG.THE_ALARM_LINE_IS_A_FORECAST = {h!r}
CG.THE_LEVERS_QUOTE_THEIR_TURNS = {h!r}
_c = {{"bar_calls": 0, "bar_hits": collections.Counter(), "floors_written": collections.Counter(),
       "breaks_calls": 0, "contested": collections.Counter(), "latch_calls": 0,
       "latched": collections.Counter(), "rider_calls": 0, "rider_true": 0,
       "deliver_calls": 0, "withheld": collections.Counter(), "emit_calls": 0,
       "emit_none": 0, "emit_dropped_courts": collections.Counter()}}
_o = DP.offensive_call_bar
def _bar(world, callee, target):
    _c["bar_calls"] += 1
    out = _o(world, callee, target)
    if out:
        _c["bar_hits"][f"{{callee}}->{{target}}: {{out}}"] += 1
    return out
DP.offensive_call_bar = _bar
_o2 = SR.write_settlement_peace_floors
def _floors(world, rows):
    out = _o2(world, rows)
    for p in out:
        _c["floors_written"][p] += 1
    return out
SR.write_settlement_peace_floors = _floors
_o3 = GE.break_signed_titles
def _brk(world, a, b, reason=""):
    _c["breaks_calls"] += 1
    before = {{r for r, rec in (world.province_title or {{}}).items() if isinstance(rec, dict) and rec.get("contested")}}
    out = _o3(world, a, b, reason)
    after = {{r for r, rec in (world.province_title or {{}}).items() if isinstance(rec, dict) and rec.get("contested")}}
    for r in after - before:
        _c["contested"][r] += 1
    return out
GE.break_signed_titles = _brk
_o4 = CG.note_ratification
def _latch(world, parties, war_ending, beaten=(), capital_kept=()):
    _c["latch_calls"] += 1
    out = _o4(world, parties, war_ending, beaten=beaten, capital_kept=capital_kept)
    for court, kind in (out or {{}}).items():
        _c["latched"][f"{{court}}:{{kind}}"] += 1
    return out
CG.note_ratification = _latch
_o5 = SS.capital_retained_by_proposer_bloc
def _rider(*a, **k):
    _c["rider_calls"] += 1
    out = _o5(*a, **k)
    if out:
        _c["rider_true"] += 1
    return out
SS.capital_retained_by_proposer_bloc = _rider
_o6 = AD.deliver_ai_proposal
def _deliver(proposal, world):
    _c["deliver_calls"] += 1
    out = _o6(proposal, world)
    if out is None:
        _c["withheld"][f"{{proposal.get('nation')}}:{{(proposal.get('terms') or {{}}).get('type') or proposal.get('proposal_type')}}"] += 1
    return out
AD.deliver_ai_proposal = _deliver
_o7 = AD._emit_settlement_offer_for_war
def _emit(world, war_id, war, **kw):
    _c["emit_calls"] += 1
    out = _o7(world, war_id, war, **kw)
    if out is None:
        _c["emit_none"] += 1
    return out
AD._emit_settlement_offer_for_war = _emit
def _dump():
    c = dict(_c)
    for k in ("bar_hits", "floors_written", "contested", "latched", "withheld", "emit_dropped_courts"):
        c[k] = dict(c[k])
    print("STEP1=" + repr(c))
atexit.register(_dump)
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
    counts = [ln for ln in lines if ln.startswith("STEP1=")]
    payload["step1"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--arms", default="0,1")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_step1_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    out_path = Path(args.out)
    out = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    out["recorded"] = prior
    out.setdefault("arms", {})
    for arm in wanted:
        levers = ARMS[arm]
        print(f"arm {arm} {levers} ...", flush=True)
        payload = run_arm(levers)
        series = payload["series"]
        div = first_divergence(series, prior)
        out["arms"][str(arm)] = {
            "levers": levers,
            "series": series,
            "first_divergence_vs_recorded": div,
            "provinces": payload.get("provinces"),
            "step1": payload.get("step1"),
        }
        print(f"  divergence vs recorded: {div}; counts: {payload.get('step1')}", flush=True)
        out_path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""SR-7d "The Doctrines" — the BASELINE_SERIES attribution (October 3, 2026).

The doctrines MOVE the series by design (D-R5: in force from turn 1), so the
series is re-recorded ONCE from this script's ALL arm, and every other arm
says what moved it: every lever is set IN THE CHILD before the 40-turn
ambient sim boots (the slice-9 idiom), one arm per lever, and every seam's
reach is COUNTED — arm 0 must reproduce the recorded (Step-3) series byte
for byte.

    python tools/_sr7d_series_arms.py [--arms 0,F,B,R,A,P,C,S,ALL]

Arms:
    0    every doctrine lever down -> must reproduce the recorded series
    F    DOCTRINES_ACTIVE + France's doctrine alone (the cures off)
    B    … Britain's alone
    R    … Russia's alone
    A    … Austria's alone
    P    … Prussia's alone
    C    every court + THE_CURES_HEAL (the save-for-the-Staff rung off)
    S    every court + the cures + reforms.THE_AI_SAVES_FOR_THE_STAFF
    ALL  the shipped tree (= S) -> the series to record

Writes tools/_sr7d_series_arms_final.json (committed with the landing record).
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
    "M": ("backend.game_logic.doctrines", "DOCTRINES_ACTIVE"),
    "F": ("backend.game_logic.doctrines", "FRANCE_DOCTRINE"),
    "B": ("backend.game_logic.doctrines", "BRITAIN_DOCTRINE"),
    "R": ("backend.game_logic.doctrines", "RUSSIA_DOCTRINE"),
    "A": ("backend.game_logic.doctrines", "AUSTRIA_DOCTRINE"),
    "P": ("backend.game_logic.doctrines", "PRUSSIA_DOCTRINE"),
    "C": ("backend.game_logic.doctrines", "THE_CURES_HEAL"),
    "S": ("backend.game_logic.reforms", "THE_AI_SAVES_FOR_THE_STAFF"),
}
COURTS = ("F", "B", "R", "A", "P")
ARMS = {
    "0": set(),
    "F": {"M", "F"}, "B": {"M", "B"}, "R": {"M", "R"}, "A": {"M", "A"}, "P": {"M", "P"},
    "C": {"M", *COURTS, "C"},
    "S": {"M", *COURTS, "C", "S"},
    "ALL": {"M", *COURTS, "C", "S"},
}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = {up!r}
ALL = {all_levers!r}
for key, (mod_name, name) in ALL.items():
    mod = importlib.import_module(mod_name)
    setattr(mod, name, key in UP)
import backend.game_logic.doctrines as DC
import backend.commands.combat_executor as CE
import backend.commands.economy_executor as EE
import backend.models.world_state as WS
import backend.game_logic.reforms as RF
_c = collections.Counter()

_o_shift = DC.arrival_bar_shift
def _shift(world, reinforcer, primary):
    out = _o_shift(world, reinforcer, primary)
    if out[0]:
        _c["arrival_shifts|" + str(getattr(reinforcer, "nation", "?"))] += 1
    return out
DC.arrival_bar_shift = _shift

_o_rec = DC.recruit_price_term
def _rec(world, nation):
    out = _o_rec(world, nation)
    if out:
        _c["recruit_terms|" + str(nation)] += 1
    return out
DC.recruit_price_term = _rec

_o_sup = DC.supply_factor
def _sup(world, nation, region, forecast=True, extra_damage=0.0):
    out = _o_sup(world, nation, region, forecast, extra_damage)
    if out[0] < 1.0:
        _c["supply_bites|" + str(nation) + ("|bill" if not forecast else "|forecast")] += 1
    return out
DC.supply_factor = _sup

_o_pen = DC.scaled_defeat_penalty
def _pen(marshal, base):
    out = _o_pen(marshal, base)
    if out[1] is not None:
        _c["defeat_scaled|" + str(getattr(marshal, "nation", "?"))] += 1
    return out
DC.scaled_defeat_penalty = _pen

_o_cured = DC.flaw_cured
def _cured(world, nation):
    out = _o_cured(world, nation)
    if out:
        _c["cured_reads|" + str(nation)] += 1
    return out
DC.flaw_cured = _cured

_o_find = RF.find_ai_enactment
def _find(world, nation, treasury, admin_ap):
    out = _o_find(world, nation, treasury, admin_ap)
    if out:
        _c["ai_enactments|" + str(nation) + "|" + str(out.get("target"))] += 1
    return out
RF.find_ai_enactment = _find

def _dump():
    print("SR7D=" + repr(dict(_c)))
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
    counts = [ln for ln in lines if ln.startswith("SR7D=")]
    payload["sr7d"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--arms", default="0,F,B,R,A,P,C,S,ALL")
    ap.add_argument("--prior", default="", help="JSON list: the PRE-SR-7d series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sr7d_series_arms_final.json"))
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
            "sr7d": payload.get("sr7d"),
        }
        print(f"  divergence vs prior: {div}; counts: {payload.get('sr7d')}", flush=True)
        Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

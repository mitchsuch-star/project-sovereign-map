"""SF-LB-2b "The Chest the Council Can Spend" — the BASELINE_SERIES
attribution (October 3, 2026; SCORE_FINISH_SPEC.md §6 row 14).

ONE lever: `war_council.THE_COUNCIL_SPENDS_THE_TURNS_INCOME`. The slice
MOVES the series by design (Prussia's crisis on Hanover opens on the
ladder's turn instead of the chest's — turn 5 on the historical seed, was
9 — and the war follows two turns sooner), so the series is re-recorded
ONCE from this script's ALL arm; arm 0 (the lever DOWN in the child before
the 40-turn ambient sim boots, the slice-9 idiom) must reproduce the
recorded SF-LB-2 series byte for byte, and the opening's reads are
COUNTED on both arms.

    python tools/_sf_lb2b_series_arms.py [--arms 0,ALL]

Writes tools/_sf_lb2b_series_arms_final.json (committed with the landing
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
    "F": ("backend.game_logic.war_council", "THE_COUNCIL_SPENDS_THE_TURNS_INCOME"),
}
ARMS = {
    "0": set(),
    "ALL": {"F"},
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

_o_block = WC._restraint_block_reason
def _block(world, coveter, target, forecast=False):
    out = _o_block(world, coveter, target, forecast=forecast)
    if forecast:
        _c["opening_reads|" + str(coveter) + ">" + str(target) + "|" + str(out)] += 1
    return out
WC._restraint_block_reason = _block

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
    print("SFLB2B=" + repr(dict(_c)))
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
    counts = [ln for ln in lines if ln.startswith("SFLB2B=")]
    payload["sflb2b"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--arms", default="0,ALL")
    ap.add_argument("--prior", default="", help="JSON list: the PRE-SF-LB-2b series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sf_lb2b_series_arms_final.json"))
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
            "sflb2b": payload.get("sflb2b"),
        }
        print(f"  divergence vs prior: {div}; counts: {payload.get('sflb2b')}", flush=True)
        Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

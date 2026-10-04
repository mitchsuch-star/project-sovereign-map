"""Score Finish Step 7 slice 3b (SF7-X2 + SF7-X3, October 4, 2026) — the
BASELINE_SERIES attribution.

Two levers, each set IN THE CHILD before the 40-turn ambient sim boots (the
slice-9 idiom; the source is never written):

    X2  combat_executor.AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL — the muster's
        expected figure weighs an arriving gun by his arrival roll (the AI's
        defender-muster price reads the same weight, `enemy_ai._muster_price`);
    X3  counsel.THE_BUILD_LINE_NEEDS_NO_CORPS — the counsel's build line
        (player-facing only: the AI reads no counsel).

The reach is COUNTED in the child: every `_expected_arrival_weight` call that
takes the changed branch (an artillery reinforcer off the field), by the
lead's nation, and every counsel build line served by the corps-free finder.

    python tools/_sf7_3b_series_arms.py [--arms 0,X2,X3,ALL] [--prior JSON]

Writes tools/_sf7_3b_series_arms_final.json.
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
    "X2": ("backend.commands.combat_executor", "AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL"),
    "X3": ("backend.ai.counsel", "THE_BUILD_LINE_NEEDS_NO_CORPS"),
}
ARMS = {"0": set(), "X2": {"X2"}, "X3": {"X3"}, "ALL": set(LEVERS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, name) in ALL.items():
    mod = importlib.import_module(mod_name)
    setattr(mod, name, key in UP)
import backend.commands.combat_executor as CE
import backend.ai.counsel as CO
_c = collections.Counter()
_o_w = CE.CombatExecutor._expected_arrival_weight
def _w(self, lead, reinforcer, world, battle_region):
    if (getattr(reinforcer, "artillery", False)
            and getattr(reinforcer, "location", None) != battle_region):
        _c["gun_weight|" + str(getattr(lead, "nation", ""))] += 1
    return _o_w(self, lead, reinforcer, world, battle_region)
CE.CombatExecutor._expected_arrival_weight = _w
_o_b = CO._build_terms
def _b(world, nation, limit=2):
    if CO._first_own_region_with_a_corps(world, nation) is None:
        _c["build_line_without_a_corps|" + str(nation)] += 1
    return _o_b(world, nation, limit=limit)
CO._build_terms = _b
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sf7_3b_series_arms_final.json"))
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
        print(f"   divergence vs prior: {out['arms'][arm]['first_divergence_vs_prior']}; "
              f"reach {out['arms'][arm]['reach']}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

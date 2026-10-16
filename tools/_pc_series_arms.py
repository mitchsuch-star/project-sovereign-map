"""The Peace Conundrum's conservative fixes (October 15, 2026 —
`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §4 A, `docs/BUG_FIXES.md` §PC) —
the BASELINE_SERIES attribution for the two that touch mechanics.

Each behaviour change that could reach the 40-turn ambient sim has ONE
function seam; an arm with a rule DOWN patches that seam IN THE CHILD before
the sim boots (the DD-B idiom — seams, never module levers):

    L = turn_manager.ai_phase_reads_the_field  (PC-F5: the AI's diplomatic phase
                                                 reads the war as the turn ends;
                                                 down -> the stored score of the
                                                 last advance, no recalculation)
    E = battle_scale.is_decisive_victory_exchange (PC-F6: a decisive is the
                                                 winner's only when the winner
                                                 inflicted the 2:1 exchange;
                                                 down -> the direction-blind
                                                 `is_decisive_exchange`)

PC-F1 (the paradox's words, the Congress lever's `at_send`) and PC-F3 (the
War Status rows' peace table) are display reads — the passive France never
opens a wizard, a counsel or the war panel in the sim; they have no seam.

Arm 0 (every lever down) must reproduce the recorded series byte for byte.
The reach is COUNTED in the child — for a lever whose arm is byte-identical,
the count says whether its code was reached at all.

    python tools/_pc_series_arms.py [--arms 0,L,E,ALL] [--jobs 4] [--prior JSON]

Writes tools/_pc_series_arms_final.json (committed with the landing
record).
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

# key: (module, seam, the shipped (pre-slice) answer when the rule is DOWN)
LEVERS = {
    "L": ("backend.game_logic.turn_manager", "ai_phase_reads_the_field", "None"),
    "E": ("backend.game_logic.battle_scale", "is_decisive_victory_exchange",
          "__import__('backend.game_logic.battle_scale', fromlist=['x'])"
          ".is_decisive_exchange(a[0], a[1])"),
}
ARMS = {"0": set(), **{k: {k} for k in LEVERS}, "ALL": set(LEVERS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, name, down) in ALL.items():
    if key not in UP:
        mod = importlib.import_module(mod_name)
        setattr(mod, name, eval("lambda *a, **k: " + down, {{"_orig": getattr(mod, name)}}))
import backend.game_logic.turn_manager as TMM
import backend.game_logic.battle_scale as BSM
import backend.game_logic.diplomacy as DP
_c = collections.Counter()

_o_field = TMM.ai_phase_reads_the_field
def _field(world):
    before = dict(getattr(world, "war_scores", {{}}) or {{}})
    out = _o_field(world)
    after = dict(getattr(world, "war_scores", {{}}) or {{}})
    moved = sum(1 for k in after if int(after.get(k, 0)) != int(before.get(k, 0)))
    _c["ai_phase_read|" + ("moved" if moved else "same")] += 1
    _c["ai_phase_pairs_moved"] += moved
    return out
TMM.ai_phase_reads_the_field = _field
_o_dec = BSM.is_decisive_victory_exchange
def _dec(winner_cas, loser_cas):
    out = _o_dec(winner_cas, loser_cas)
    if BSM.is_decisive_exchange(winner_cas, loser_cas):
        _c["decisive_exchange|" + ("winner_inflicted" if int(winner_cas) < int(loser_cas)
                                   else "winner_bled") + "|" + str(bool(out))] += 1
    return out
BSM.is_decisive_victory_exchange = _dec

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
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE"):
        env.pop(k, None)
    code = CHILD.format(up=sorted(up), all_levers=LEVERS, runner=str(RUNNER))
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
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior,
           "levers": {k: f"{m}.{n}" for k, (m, n, _d) in LEVERS.items()},
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

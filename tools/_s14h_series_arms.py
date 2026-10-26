"""S14h part 1 "the third measure's rows" (`docs/BUG_FIXES.md` §S14G, S14G-1 … 12;
`docs/DESIGN_REFINEMENT.md` §S14G D1, D2, D3, D6) — the BASELINE_SERIES
attribution for the part's backend seams that the AI's road can reach (Golden
Rule 5), each seam's reach COUNTED in the child (an arm whose seam never bites
cannot pass for a byte-identical one). Chained from
`tools/_s14f_p3_series_arms_final.json`'s arm "0" — the tree after the nine
rulings with nothing held down, which IS the standing BASELINE_SERIES (an arm's
name is the set of seams held DOWN; "0" is the shipped tree, "ALL" every seam
down).

    LB = a province whose home court is an ally or client of the capturer,
         retaken from an enemy, is a LIBERATION handed back at once (S14G-1 /
         S14G-D1, `world_state.liberates_ally_ground`) — down: '' (today's
         conquest). Reach: the calls, the liberations (a non-empty court).
    SL = a plain SUPPORT lapses on arrival for every supporter alike, whatever
         his name (S14G-3, `StrategicOrderProcessor._support_lapses_on_arrival`)
         — down: None (the alphabetical split). Reach: the calls, the lapses.
         The AI never walks `_execute_support` (pinned in row 3's tests), so
         0 calls is the expected reading.
    LK = only a great court's letter, an ultimatum or a war decision shuts the
         Cabinet (S14G-6 / S14G-D3, `DialogueManager.letter_locks_cabinet`) —
         down: True (every offer locks). Reach: the calls, the letters that do
         not lock. Player-only (no reader under backend/ai), so the count is
         the proof.
    GP = the guard map of the Ansbach trap read through ONE helper the march
         ask shares (S14G-11, `agendas.guarded_provinces_for`) — no "down":
         the refactor is byte-identical by construction (the trap reads the
         helper); the arm counts its reach and the provinces it names.

    python tools/_s14h_series_arms.py [--arms 0,LB,SL,LK,GP,ALL] [--jobs 3]

Writes tools/_s14h_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_s14f_p3_series_arms_final.json"
SEAMS = ("LB", "SL", "LK", "GP")
ARMS = {"0": set(), **{s: {s} for s in SEAMS}, "ALL": set(SEAMS)}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()

# LB — the liberation of an ally's ground (S14G-1 / D1)
from backend.models import world_state as WS
_lb = WS.liberates_ally_ground
def _counted_lb(world, region_name, capturer, *a, **k):
    _c["lb_calls"] += 1
    out = _lb(world, region_name, capturer, *a, **k)
    if out:
        _c["lb_liberations"] += 1
    return "" if "LB" in DOWN else out
WS.liberates_ally_ground = _counted_lb

# SL — the support lapses on arrival (S14G-3)
from backend.commands import strategic as ST
_sl = ST.StrategicOrderProcessor._support_lapses_on_arrival
def _counted_sl(self, *a, **k):
    _c["sl_calls"] += 1
    out = _sl(self, *a, **k)
    if out is not None:
        _c["sl_lapses"] += 1
    return None if "SL" in DOWN else out
ST.StrategicOrderProcessor._support_lapses_on_arrival = _counted_sl

# LK — which letters shut the Cabinet (S14G-6 / D3)
from backend.models import dialogue_manager as DM
_lk = DM.DialogueManager.letter_locks_cabinet
def _counted_lk(self, item, *a, **k):
    _c["lk_calls"] += 1
    out = _lk(self, item, *a, **k)
    if not out:
        _c["lk_open"] += 1
    return True if "LK" in DOWN else out
DM.DialogueManager.letter_locks_cabinet = _counted_lk

# GP — the guard map through one helper (S14G-11); counted only
try:
    from backend.game_logic import agendas as AG
    _gp = AG.guarded_provinces_for
    def _counted_gp(world, violator, *a, **k):
        _c["gp_calls"] += 1
        out = _gp(world, violator, *a, **k)
        if out:
            _c["gp_guarded"] += 1
        return out
    AG.guarded_provinces_for = _counted_gp
except AttributeError:
    _c["gp_absent"] += 1

_KEYS = ("lb_calls", "lb_liberations", "sl_calls", "sl_lapses", "lk_calls", "lk_open",
         "gp_calls", "gp_guarded", "gp_absent")
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}}}}))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(down: set) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE"):
        env.pop(k, None)
    code = CHILD.format(down=sorted(down), runner=str(RUNNER))
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_s14h_series_arms_final.json"))
    args = ap.parse_args()
    prior = list(json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))["arms"]["0"]["series"])
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior, "seams_down": {k: sorted(ARMS[k]) for k in names}, "arms": {}}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a]), names)))
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        out["arms"][arm] = {"down": sorted(ARMS[arm]), "series": series,
                            "first_divergence_vs_prior": first_divergence(series, prior),
                            "reach": payload.get("reach")}
        print(f"arm {arm:>4}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {(payload.get('reach') or {}).get('counts')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

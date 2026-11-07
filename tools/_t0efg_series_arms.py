"""T0-E / T0-F / T0-G — the BASELINE_SERIES attribution for the November 6,
2026 review's series-moving fixes, each one's reach COUNTED in the child (an
arm whose seam never bites cannot pass for a byte-identical one). The prior
is HEAD's `BASELINE_SERIES` (never the working tree's), the S14k rig's rule.

Arms: `0` — every seam down, the tree before the three slices (must
reproduce the prior byte for byte); one arm per seam, that fix alone held
down; `ALL` — every seam up, the shipped tree (the re-pin's value).

    .venv/Scripts/python.exe tools/_t0efg_series_arms.py [--arms 0,ALL] [--jobs 3]

Writes tools/_t0efg_series_arms_final.json (committed with the landing
record; a re-run writes its OWN record via --out).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"
sys.path.insert(0, str(ROOT))
from tests._t0efg_seams import T0EFG_SEAMS_BY_ROW  # noqa: E402

SEAMS = tuple(T0EFG_SEAMS_BY_ROW)
ARMS = {"0": set(SEAMS), **{s: {s} for s in SEAMS}, "ALL": set()}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
from backend.ai import enemy_ai as EA
from backend.game_logic import affairs as AF
from backend.game_logic import ai_diplomacy as AD
from backend.game_logic import coalition as CO
from backend.game_logic import reforms as RF
# T0-E: the three brake seams, each held down on its arm, reads counted
_p39, _stm, _dsp = EA.p39_reads_the_brakes, EA.storms_read_the_pair, EA.desperation_reads_the_brakes
def _counted_p39():
    _c["p39_reads"] += 1
    return False if "T0E-P39" in DOWN else _p39()
def _counted_stm():
    _c["storm_reads"] += 1
    return False if "T0E-STM" in DOWN else _stm()
def _counted_dsp():
    _c["desperation_reads"] += 1
    return False if "T0E-DSP" in DOWN else _dsp()
EA.p39_reads_the_brakes, EA.storms_read_the_pair, EA.desperation_reads_the_brakes = (
    _counted_p39, _counted_stm, _counted_dsp)
# T0-F: the brew gate (verdicts counted) and the failed-expiry rest
_brw = CO.brew_follows_formation
def _counted_brw():
    _c["brew_gate_reads"] += 1
    return False if "T0F-BRW" in DOWN else _brw()
CO.brew_follows_formation = _counted_brw
_could = CO.a_league_the_brew_could_form
def _counted_could(world, qualifying, target):
    out = _could(world, qualifying, target)
    _c["brews_passed" if out else "brews_held"] += 1
    return out
CO.a_league_the_brew_could_form = _counted_could
# T0-F: the refused ask's rest (stamps counted)
_ask = AD.a_refused_ask_rests
def _counted_ask():
    _c["ask_rest_reads"] += 1
    return False if "T0F-ASK" in DOWN else _ask()
AD.a_refused_ask_rests = _counted_ask
_rest = AD.rest_refused_pair
def _counted_rest(initiator, ptype, world, target):
    if ptype == "design_ask":
        _c["asks_rested"] += 1
    return _rest(initiator, ptype, world, target)
AD.rest_refused_pair = _counted_rest
# T0-G: the reachability guard (verdicts counted) and the edicts' hold
_rch = RF.the_staff_must_be_reachable
def _counted_rch():
    _c["reach_guard_reads"] += 1
    return False if "T0G-RCH" in DOWN else _rch()
RF.the_staff_must_be_reachable = _counted_rch
_reachable = RF.staff_is_reachable
def _counted_reachable(world, nation, staff):
    out = _reachable(world, nation, staff)
    _c["staff_reachable" if out else "staff_unreachable"] += 1
    return out
RF.staff_is_reachable = _counted_reachable
_eds = AF.edicts_respect_the_save
def _counted_eds():
    _c["edict_save_reads"] += 1
    return False if "T0G-EDS" in DOWN else _eds()
AF.edicts_respect_the_save = _counted_eds
_KEYS = ("p39_reads", "storm_reads", "desperation_reads",
         "brew_gate_reads", "brews_passed", "brews_held",
         "ask_rest_reads", "asks_rested",
         "reach_guard_reads", "staff_reachable", "staff_unreachable",
         "edict_save_reads")
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


def prior_series() -> list:
    """HEAD's `BASELINE_SERIES` — the series before this slice, never the
    working tree's (the S14k rig's rule)."""
    rel = RUNNER.relative_to(ROOT).as_posix()
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                          capture_output=True, check=True).stdout.decode("utf-8")
    m = re.search(r"^BASELINE_SERIES = (\[[^\]]*\])", text, re.M)
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_t0efg_series_arms_final.json"))
    args = ap.parse_args()
    prior = prior_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior, "seams_down": {k: sorted(ARMS[k]) for k in names},
           "arms": {}}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a]), names)))
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        out["arms"][arm] = {"down": sorted(ARMS[arm]), "series": series,
                            "first_divergence_vs_prior": first_divergence(series, prior),
                            "reach": payload.get("reach")}
        print(f"arm {arm:>8}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {(payload.get('reach') or {}).get('counts')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

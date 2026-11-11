"""Session D — the BASELINE_SERIES attribution for DY-5's five seams
(DYNAMISM_SPEC.md §5, the Tier-6 gate record §5a; November 10, 2026), an
arm per seam raised in the sweep's order, each seam's reach COUNTED in the
child (an arm whose seam never bites cannot pass for a byte-identical one).
The prior is HEAD's `BASELINE_SERIES` (never the working tree's), the S14k
rig's rule.

Arms: `0` — every DY-5 seam down, the tree session C left (must reproduce
the prior byte for byte); `LEVEE` — the levée alone; `DIAL` — + the client
dial; `REVANCHE` — + a risen people's revanche; `LIBERATORS` — + the
liberators' friction; `ALL` — every seam up, the shipped tree (the re-pin's
value, if the series moves).

    .venv/Scripts/python.exe tools/_t6b_series_arms.py [--arms 0,LEVEE,DIAL,REVANCHE,LIBERATORS,ALL] [--jobs 2]

Writes tools/_t6b_series_arms_final.json (committed with the landing record;
a re-run writes its OWN record via --out).
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

ARMS = {
    "0": {"LEVEE", "DIAL", "REVANCHE", "LIBERATORS", "ARMS"},
    "LEVEE": {"DIAL", "REVANCHE", "LIBERATORS", "ARMS"},
    "DIAL": {"REVANCHE", "LIBERATORS", "ARMS"},
    "REVANCHE": {"LIBERATORS", "ARMS"},
    "LIBERATORS": {"ARMS"},
    "ALL": set(),
}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
_beats = []
from backend.game_logic import awakening as AW
def _counted(module, name, key, down_key):
    seam = getattr(module, name)
    def _wrapped():
        _c[key] += 1
        return False if down_key in DOWN else seam()
    setattr(module, name, _wrapped)
_counted(AW, "the_levee_rises", "levee_seam_reads", "LEVEE")
_counted(AW, "the_tiger_is_ridden", "dial_seam_reads", "DIAL")
_counted(AW, "a_risen_people_swears_revanche", "revanche_seam_reads", "REVANCHE")
_counted(AW, "liberators_hold_together", "liberators_seam_reads", "LIBERATORS")
_counted(AW, "the_nation_writes", "arms_seam_reads", "ARMS")
_levee = AW.levee_terms
def _counted_levee(world, court):
    out = _levee(world, court)
    _c["levee_reads"] += 1
    if out[0] != 1.0:
        _c["levee_bites"] += 1
    return out
AW.levee_terms = _counted_levee
_dial = AW.client_dial
def _counted_dial(world, client, autonomy):
    out = _dial(world, client, autonomy)
    _c["dial_reads"] += 1
    if out[1]:
        _c["dial_bites"] += 1
    return out
AW.client_dial = _counted_dial
_risen = AW.risen_grievance
def _counted_risen(world, court):
    out = _risen(world, court)
    _c["revanche_reads"] += 1
    if out:
        _c["revanche_bites"] += 1
    return out
AW.risen_grievance = _counted_risen
_step = AW.coalition_friction_step
def _counted_step(world, target):
    out = _step(world, target)
    _c["friction_reads"] += 1
    if out < AW.FRICTION_STEP:
        _c["friction_eased"] += 1
    return out
AW.coalition_friction_step = _counted_step
_beat = AW._the_levee_beats
def _counted_beat(world, court, direction):
    out = _beat(world, court, direction)
    _c["levee_beats"] += 1
    _beats.append([int(world.current_turn), str(court), str(direction)])
    return out
AW._the_levee_beats = _counted_beat
_pred = AW.nation_in_arms
def _counted_pred(world, lord, params):
    out = _pred(world, lord, params)
    if out.get("holds"):
        _c["letters_nation_in_arms"] += 1
    return out
AW.nation_in_arms = _counted_pred
_KEYS = ("levee_seam_reads", "dial_seam_reads", "revanche_seam_reads", "liberators_seam_reads",
         "arms_seam_reads", "levee_reads", "levee_bites", "levee_beats", "dial_reads", "dial_bites",
         "revanche_reads", "revanche_bites", "friction_reads", "friction_eased",
         "letters_nation_in_arms")
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}},
                           "beats": _beats}}))
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
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING",
              "PYTHONDONTWRITEBYTECODE", "INK_IRON_SEAMS"):
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
    """HEAD's `BASELINE_SERIES` — the series before this session, never the
    working tree's (the S14k rig's rule)."""
    rel = RUNNER.relative_to(ROOT).as_posix()
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                          capture_output=True, check=True).stdout.decode("utf-8")
    m = re.search(r"^BASELINE_SERIES = (\[[^\]]*\])", text, re.M)
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_t6b_series_arms_final.json"))
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
        print(f"arm {arm:>10}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {(payload.get('reach') or {}).get('counts')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

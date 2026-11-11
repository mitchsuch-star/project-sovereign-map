"""Session G2 — the BASELINE_SERIES attribution for the four session-G2 seams
(DYNAMISM_SPEC.md §7b; November 11, 2026), an arm per seam raised in the
sweep's order, each seam's reach COUNTED in the child (an arm whose seam never
bites cannot pass for a byte-identical one). The prior is HEAD's
`BASELINE_SERIES` (never the working tree's), the S14k rig's rule.

Arms: `0` — the four seams down, the tree session G left (must reproduce the
prior byte for byte); `ASK` — a court at fight still asks; `LADDER` — + the
ladder outlasts the rest; `ALL` — + a backed design dares and the war names
the beaten, the shipped tree (the re-pin's value, if the series moves).

    .venv/Scripts/python.exe tools/_g2_series_arms.py [--arms 0,ASK,LADDER,ALL] [--jobs 2]

Writes tools/_g2_series_arms_final.json (committed with the landing record;
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
    "0": {"RECOG", "ASK", "LADDER", "BACKED"},
    "ASK": {"RECOG", "LADDER", "BACKED"},
    "LADDER": {"RECOG", "BACKED"},
    "ALL": set(),
}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
_beats = []
from backend.game_logic import ai_diplomacy as AD
from backend.game_logic import crowns as CR
from backend.game_logic import intent as IT
def _counted(module, name, key, down_key):
    seam = getattr(module, name)
    def _wrapped():
        _c[key] += 1
        return False if down_key in DOWN else seam()
    setattr(module, name, _wrapped)
_counted(AD, "a_court_at_fight_still_asks", "ask_seam_reads", "ASK")
_counted(AD, "the_ladder_outlasts_the_rest", "ladder_seam_reads", "LADDER")
_counted(IT, "a_backed_design_dares", "backed_seam_reads", "BACKED")
_counted(CR, "the_war_names_the_beaten", "recog_seam_reads", "RECOG")
_backing = IT.design_backing
def _counted_backing(world, nation, agenda, against):
    out = _backing(world, nation, agenda, against)
    if out:
        _c["backed_bites"] += 1
        _beats.append([int(world.current_turn), "backed", str(nation), str(against), str(out.get("payer"))])
    return out
IT.design_backing = _counted_backing
_ladder = AD.get_ladder_refusals
def _counted_ladder(world, proposer, recipient):
    out = _ladder(world, proposer, recipient)
    short = AD.get_refused_asks(world, proposer, recipient)
    _c["ladder_reads"] += 1
    if len(out) >= 2 and len(short) < 2:
        _c["ladder_bites"] += 1
        _beats.append([int(world.current_turn), "ladder", str(proposer), str(recipient)])
    return out
AD.get_ladder_refusals = _counted_ladder
_KEYS = ("ask_seam_reads", "ladder_seam_reads", "backed_seam_reads", "recog_seam_reads",
         "backed_bites", "ladder_reads", "ladder_bites")
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}},
                           "beats": _beats[:60]}}))
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_g2_series_arms_final.json"))
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

"""Session C — the BASELINE_SERIES attribution for Tier 6's three seams
(DYNAMISM_SPEC.md §5, the Tier-6 gate record §5a; November 10, 2026), an
arm per seam raised in the sweep's order, each seam's reach COUNTED in the
child (an arm whose seam never bites cannot pass for a byte-identical one).
The prior is HEAD's `BASELINE_SERIES` (never the working tree's), the S14k
rig's rule.

Arms: `0` — every Tier-6 seam down, the tree before the session (must
reproduce the prior byte for byte); `STIR` — the scalar alone; `ULCER` — +
the ulcer; `ALL` — every seam up, the shipped tree (the re-pin's value, if
the series moves).

    .venv/Scripts/python.exe tools/_t6_series_arms.py [--arms 0,STIR,ULCER,ALL] [--jobs 2]

Writes tools/_t6_series_arms_final.json (committed with the landing record;
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
    "0": {"STIR", "ULCER", "LETTERS"},
    "STIR": {"ULCER", "LETTERS"},
    "ULCER": {"LETTERS"},
    "ALL": set(),
}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
_moves = []
from backend.game_logic import awakening as AW
def _counted(module, name, key, down_key):
    seam = getattr(module, name)
    def _wrapped():
        _c[key] += 1
        return False if down_key in DOWN else seam()
    setattr(module, name, _wrapped)
_counted(AW, "the_people_stir", "stir_seam_reads", "STIR")
_counted(AW, "the_ulcer_bleeds", "ulcer_seam_reads", "ULCER")
_counted(AW, "the_people_write", "letters_seam_reads", "LETTERS")
_move = AW.move
def _counted_move(world, court, delta, cause, occupied_now=None):
    before = AW.level(world, court)
    out = _move(world, court, delta, cause, occupied_now=occupied_now)
    after = AW.level(world, court)
    if after != before:
        _c["moves"] += 1
        _c["raises" if after > before else "cools"] += 1
    if out:
        _c["beats"] += 1
        _moves.append([int(world.current_turn), "beat", str(court), str(out.get("phase")), str(cause)])
    return out
AW.move = _counted_move
_ulcer = AW.ulcer_factor
def _counted_ulcer(world, nation, region):
    out = _ulcer(world, nation, region)
    _c["ulcer_reads"] += 1
    if out < 1.0:
        _c["ulcer_bites"] += 1
    return out
AW.ulcer_factor = _counted_ulcer
for _name in ("people_stir", "people_risen"):
    _fn = getattr(AW, _name)
    def _counted_pred(world, lord, params, _fn=_fn, _name=_name):
        out = _fn(world, lord, params)
        if out.get("holds"):
            _c["letters_" + _name] += 1
        return out
    setattr(AW, _name, _counted_pred)
_KEYS = ("stir_seam_reads", "ulcer_seam_reads", "letters_seam_reads", "moves", "raises", "cools",
         "beats", "ulcer_reads", "ulcer_bites", "letters_people_stir", "letters_people_risen")
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}},
                           "moves": _moves}}))
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_t6_series_arms_final.json"))
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
        print(f"arm {arm:>5}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {(payload.get('reach') or {}).get('counts')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""S14c "Events and Historical Moments", part 1 (`docs/EVENTS_SPEC.md` §7, §9)
— the BASELINE_SERIES attribution for the part's backend seams, each one's
reach COUNTED in the child (an arm whose seam never bites cannot pass for a
byte-identical one). Chained from `tools/_vp1_series_arms_final.json`:

    M0 = the moments' tick (`moments.tick`) — down: inert. Reach: the ticks
         that found an ARMED store (part 1: 0 — the shipped boot authors no
         block), the letters delivered, the lapses applied, the receipts.
    X8 = the non-treaty registry (`treaty.non_treaty_kind`) — down: "" (every
         context dialogue judged as a treaty again). Reach: the reads that
         returned a registered kind (an ultimatum, an offered crown, a
         broker's ask) — the stamps a passive France never answers.
    X9 = the court-less lapse (`dialogue_manager._extract_lapse_info`'s
         fallback) — reach only: the lapse rows written with no nation.

Part 2 extends it (MW the window resolver, ML the lapse default, MK the
residence, MN the rows, MH the wizard exclusion, MR the receipt) when it arms
the deck.

    python tools/_s14c_series_arms.py [--arms 0,M0,X8,ALL] [--jobs 3]

Writes tools/_s14c_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_vp1_series_arms_final.json"
SEAMS = ("M0", "X8")
ARMS = {"0": set(), "M0": {"M0"}, "X8": {"X8"}, "ALL": set(SEAMS)}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
from backend.game_logic import moments as MO
from backend.game_logic import treaty as TR
from backend.models import dialogue_manager as DMOD
_tick = MO.tick
def _counted_tick(world):
    if MO.armed(world):
        _c["moments_armed_ticks"] += 1
    if "M0" in DOWN:
        return []
    out = _tick(world)
    _c["letters_delivered"] += len(out or [])
    return out
MO.tick = _counted_tick
_lapse = MO.lapse_default
def _counted_lapse(world, letter):
    out = _lapse(world, letter)
    if out:
        _c["moment_lapses"] += 1
    return out
MO.lapse_default = _counted_lapse
_crowd = MO._crowd_out
def _counted_crowd(world, e, turn):
    _c["moment_receipts"] += 1
    return _crowd(world, e, turn)
MO._crowd_out = _counted_crowd
_ntk = TR.non_treaty_kind
def _counted_ntk(letter):
    out = _ntk(letter)
    if out:
        _c["non_treaty_reads"] += 1
    return "" if "X8" in DOWN else out
TR.non_treaty_kind = _counted_ntk
_eli = DMOD.DialogueManager._extract_lapse_info
def _counted_eli(self, dialogue):
    out = _eli(self, dialogue)
    if not out.get("nation"):
        _c["courtless_lapses"] += 1
    return out
DMOD.DialogueManager._extract_lapse_info = _counted_eli
_KEYS = ("moments_armed_ticks", "letters_delivered", "moment_lapses", "moment_receipts",
         "non_treaty_reads", "courtless_lapses")
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
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_s14c_series_arms_final.json"))
    args = ap.parse_args()
    prior = list(json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))["arms"]["ALL"]["series"])
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

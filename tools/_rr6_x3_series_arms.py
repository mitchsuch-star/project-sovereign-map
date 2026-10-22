"""RR6-X3 "one sighting rule" (Pre-Deploy S14b's head, October 21, 2026) — the
BASELINE_SERIES attribution for the slice's backend changes.

Every change is the PLAYER's fog — where the player places an enemy marshal
(`intel_surfaces.last_seen`: in sight now, else the newest sighting), what the
enemy-phase dialog shows written into the player's store
(`intel_surfaces.record_shown_sightings`), and a STALE province read as out of
sight (`WorldState.get_visible_enemies_in_region`, RR6-X8). The enemy AI reads
none of it (GR5), and the passive France of the ambient sim orders nothing, so
the series should not move; the arms prove it, and count the reach — an arm
whose seam never bites cannot pass for a byte-identical one.

    R = the rule (down: the order reads the store alone; the dialog writes
        nothing)
    X = RR6-X8 (down: a STALE province's live occupants read as in sight)

    python tools/_rr6_x3_series_arms.py [--arms 0,R,X,ALL] [--jobs 2]

Writes tools/_rr6_x3_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_sf_rr6_series_arms_final.json"

ARMS = {"0": set(), "R": {"R"}, "X": {"X"}, "ALL": {"R", "X"}}

CHILD = r"""
import sys, runpy, atexit, collections
UP = set({up!r})
_c = collections.Counter()
from backend.game_logic import intel_surfaces as IS
from backend.models import world_state as WS
from backend.models.intel import FULL, PARTIAL, STALE, get_strength_band
_last_seen, _record = IS.last_seen, IS.record_shown_sightings
_in_sight = IS.in_sight
def _counted_in_sight(world, viewer, man):
    out = _in_sight(world, viewer, man)
    if out:
        _c["in_sight_true"] += 1
    return out
IS.in_sight = _counted_in_sight
def _counted_record(world, shown):
    n = _record(world, shown)
    _c["sightings_written"] += int(n or 0)
    return n
if "R" in UP:
    IS.record_shown_sightings = _counted_record
else:
    def _store_only(world, viewer, name):
        known = world.get_last_known_location(name) if name else None
        if not known:
            return None
        return {{"location": known[0], "intel_turn": known[1],
                 "visibility": known[2], "source": "snapshot"}}
    IS.last_seen = _store_only
    def _held(world, shown):
        _c["record_held_down"] += 1
        return 0
    IS.record_shown_sightings = _held
_shipped_region = WS.WorldState.get_visible_enemies_in_region
def _entry_rule(self, region_name, nation):
    intel = self.get_region_intel(region_name)
    if intel.visibility == STALE:
        _c["stale_region_read"] += 1
    if intel.visibility == FULL:
        return self.get_enemies_in_region(region_name, nation)
    if intel.visibility in (PARTIAL, STALE):
        return [{{"name": m.name, "nation": m.nation,
                  "strength_band": get_strength_band(m.strength),
                  "fog_level": intel.visibility}}
                for m in self.get_enemies_in_region(region_name, nation)]
    return []
if "X" not in UP:
    WS.WorldState.get_visible_enemies_in_region = _entry_rule
else:
    def _counted_region(self, region_name, nation):
        if self.get_region_intel(region_name).visibility == STALE:
            _c["stale_region_read"] += 1
        return _shipped_region(self, region_name, nation)
    WS.WorldState.get_visible_enemies_in_region = _counted_region
def _dump():
    print("REACH=" + repr({{"counts": dict(_c)}}))
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
    code = CHILD.format(up=sorted(up), runner=str(RUNNER))
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
    """SF-RR6's final ALL series — the BASELINE_SERIES this slice found."""
    rec = json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))
    return list(rec["arms"]["ALL"]["series"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_rr6_x3_series_arms_final.json"))
    args = ap.parse_args()
    prior = recorded_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior,
           "levers": {"R": "intel_surfaces.last_seen + record_shown_sightings",
                      "X": "WorldState.get_visible_enemies_in_region (STALE)"},
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
        print(f"arm {arm:>4}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {payload.get('reach', {}).get('counts') if payload.get('reach') else None}",
              flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

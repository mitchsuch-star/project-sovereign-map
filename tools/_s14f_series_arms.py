"""S14f part 1 "the re-measure's rows" (`docs/BUG_FIXES.md` §S14E; the rulings
`docs/DESIGN_REFINEMENT.md` §S14E) — the BASELINE_SERIES attribution for the
part's backend seams, each seam's reach COUNTED in the child (an arm whose
seam never bites cannot pass for a byte-identical one). Chained from
`tools/_s14d_series_arms_final.json` (S14d part 1's ALL; S14e changed nothing).

    FS = the typed first step asks (S14E-1 / D1, `StrategicExecutor.
         _typed_first_step_asks`) — down: False (the legacy auto-attack).
         Reach: the asks built (`_first_step_contact_ask`) and the predicate's
         calls. A passive France types nothing, so 0 is the expectation.
    GT = the war title's ground floor (S14E-D4, `war_title._ground_rung`) —
         down: the rung returns its input (no floor). Reach: the calls, and
         how many rows the floor dropped.
    LG = the legitimacy tier reads the court's own slice (S14E-D2,
         `settlement_scoring.court_slice_of_package`) — down: the whole
         package. Reach: the calls.
    SO = the bilateral peace's shut-out reaction (S14E-D3, `settlement_
         reactions.shut_out_carried_allies`) — down: no reaction.
         Reach: the calls and the allies hit.
    CA = a corps that cannot arrive is not present in the player's muster
         (S14E-12, `CombatExecutor._reachable_joiners`) — down: every
         will-join corps kept (the old muster). Reach: the calls, and the
         corps dropped. The glory gate (`muster_odds`) reads it for France's
         own autonomous attacks, so a passive France can reach it.

    python tools/_s14f_series_arms.py [--arms 0,FS,GT,LG,SO,CA,ALL] [--jobs 3]

Writes tools/_s14f_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_s14d_series_arms_final.json"
SEAMS = ("FS", "GT", "LG", "SO", "CA")
ARMS = {"0": set(), **{s: {s} for s in SEAMS}, "ALL": set(SEAMS)}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()

# FS — the typed first step asks
from backend.commands import strategic_executor as SE
_asks = SE.StrategicExecutor._typed_first_step_asks
def _counted_asks(marshal, order, enemy, world):
    _c["fs_predicate_calls"] += 1
    out = _asks(marshal, order, enemy, world)
    if out:
        _c["fs_would_ask"] += 1
    return False if "FS" in DOWN else out
SE.StrategicExecutor._typed_first_step_asks = staticmethod(_counted_asks)
_ask_builder = SE.StrategicExecutor._first_step_contact_ask
def _counted_ask_builder(self, *a, **k):
    _c["fs_asks_built"] += 1
    return _ask_builder(self, *a, **k)
SE.StrategicExecutor._first_step_contact_ask = _counted_ask_builder

# GT — the ground floor
from backend.game_logic import war_title as WT
_rung = WT._ground_rung
def _counted_rung(world, ground):
    _c["gt_calls"] += 1
    out = _rung(world, ground)
    if len(out) != len(ground or []):
        _c["gt_rows_dropped"] += len(ground or []) - len(out)
    return list(ground or []) if "GT" in DOWN else out
WT._ground_rung = _counted_rung

# LG — the court's own slice
try:
    from backend.game_logic import settlement_scoring as SS
    _slice = getattr(SS, "court_slice_of_package", None)
except Exception:
    SS, _slice = None, None
if _slice is not None:
    def _counted_slice(package, court, *a, **k):
        _c["lg_calls"] += 1
        out = _slice(package, court, *a, **k)
        return package if "LG" in DOWN else out
    SS.court_slice_of_package = _counted_slice

# SO — the bilateral shut-out reaction
try:
    from backend.game_logic import settlement_reactions as SR
    _bilateral = getattr(SR, "shut_out_carried_allies", None)
except Exception:
    SR, _bilateral = None, None
if _bilateral is not None:
    def _counted_bilateral(*a, **k):
        _c["so_calls"] += 1
        if "SO" in DOWN:
            return []
        out = _bilateral(*a, **k)
        try:
            _c["so_allies_hit"] += len(out or [])
        except TypeError:
            pass
        return out
    SR.shut_out_carried_allies = _counted_bilateral

# CA — a corps that cannot arrive is not present
from backend.commands import combat_executor as CE
_reach = CE.CombatExecutor._reachable_joiners
def _counted_reach(self, lead, joiners, world, battle_region, active=None):
    _c["ca_calls"] += 1
    out = _reach(self, lead, joiners, world, battle_region, active)
    try:
        _c["ca_dropped"] += max(0, len(list(joiners)) - len(out))
    except TypeError:
        pass
    return list(joiners) if "CA" in DOWN else out
CE.CombatExecutor._reachable_joiners = _counted_reach

_KEYS = ("fs_predicate_calls", "fs_would_ask", "fs_asks_built", "gt_calls", "gt_rows_dropped",
         "lg_calls", "so_calls", "so_allies_hit", "ca_calls", "ca_dropped")
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}},
                           "seams_present": {{"LG": _slice is not None, "SO": _bilateral is not None}}}}))
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_s14f_series_arms_final.json"))
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

"""S14f part 2 "the re-measure's rows" (`docs/BUG_FIXES.md` §S14E; the rulings
`docs/DESIGN_REFINEMENT.md` §S14E D5 … D11) — the BASELINE_SERIES attribution
for the part's backend seams, each seam's reach COUNTED in the child (an arm
whose seam never bites cannot pass for a byte-identical one). Chained from
`tools/_s14f_series_arms_final.json` (part 1's ALL).

    HS = the harshness penalty reads the court's own slice (S14E-D5,
         `settlement_scoring.harshness_terms_for`) — down: the whole package.
         Reach: the calls, and how many calls the slice was smaller on.
    SR = the proposer-side pass reaches only the allies whose pair the table
         resolves (S14E-D8, `settlement_reactions.table_resolves_ally`) —
         down: always True (F81's old reach). Reach: the calls, the False
         verdicts.
    MM = the muster's mean re-seated on the exact per-outcome expectation
         (S14E-D11, `CombatExecutor._muster_mean_exact`) — down: None (the
         one-stamp mean). Reach: the calls, the re-seated figures.
    LB = the hegemon's last battle read from the world's store as well as
         the roster (S14E-35 and X118/X129 — every field battle stamps the
         store through `_stamp_battle_clock`; `coalition.last_battle_turn_of`)
         — down: the roster alone (`roster_last_battle_turn`), which nulls
         every store stamp at once. Reach: the calls, the reads where the
         store won, the stamps written.
    CP (counted, never down — the old predicates are gone): the clause-to-
         court predicates read `clause_parties` (S14E-X25). Reach: the calls,
         the clauses whose verdict differs from the old `from`/`to` read.

    python tools/_s14f_p2_series_arms.py [--arms 0,HS,SR,MM,LB,ALL] [--jobs 3]

Writes tools/_s14f_p2_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_s14f_series_arms_final.json"
SEAMS = ("HS", "SR", "MM", "LB")
ARMS = {"0": set(), **{s: {s} for s in SEAMS}, "ALL": set(SEAMS)}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()

# HS — the harshness penalty on the court's slice
from backend.game_logic import settlement_scoring as SS
_hs = SS.harshness_terms_for
def _counted_hs(package, court, *a, **k):
    _c["hs_calls"] += 1
    out = _hs(package, court, *a, **k)
    try:
        if len(out) < len(list(package)):
            _c["hs_slice_smaller"] += 1
    except TypeError:
        pass
    return list(SS._iter_terms(package)) if "HS" in DOWN else out
SS.harshness_terms_for = _counted_hs

# SR — the pass reaches only the allies whose pair the table resolves
from backend.game_logic import settlement_reactions as SRX
_sr = SRX.table_resolves_ally
def _counted_sr(*a, **k):
    _c["sr_calls"] += 1
    out = _sr(*a, **k)
    if not out:
        _c["sr_false"] += 1
    return True if "SR" in DOWN else out
SRX.table_resolves_ally = _counted_sr

# MM — the muster's mean re-seated
from backend.commands import combat_executor as CE
_mm = CE.CombatExecutor._muster_mean_exact
def _counted_mm(self, outcome_set):
    _c["mm_calls"] += 1
    out = _mm(self, outcome_set)
    if out is not None:
        _c["mm_reseated"] += 1
    return None if "MM" in DOWN else out
CE.CombatExecutor._muster_mean_exact = _counted_mm

# LB — the hegemon's last battle from the store as well as the roster
from backend.game_logic import coalition as CO
_lb = CO.last_battle_turn_of
_roster = CO.roster_last_battle_turn
def _counted_lb(world, hegemon, *a, **k):
    _c["lb_calls"] += 1
    out = _lb(world, hegemon, *a, **k)
    ros = _roster(world, hegemon, *a, **k)
    if out != ros:
        _c["lb_store_won"] += 1
    return ros if "LB" in DOWN else out
CO.last_battle_turn_of = _counted_lb
_sb = CE.CombatExecutor._stamp_battle_clock
def _counted_sb(world, attacker_nation, defender_nation, *a, **k):
    _c["sb_calls"] += 1
    return _sb(world, attacker_nation, defender_nation, *a, **k)
CE.CombatExecutor._stamp_battle_clock = staticmethod(_counted_sb)

# CP — counted only
from backend.game_logic import settlement_validation as SV
from backend.game_logic import settlement_actions as SA
def _old_touch(clause, court):
    try:
        return court in (clause.get("from"), clause.get("to"))
    except AttributeError:
        return False
_cv = SV._clause_touches_court
def _counted_cv(clause, court):
    _c["cp_calls"] += 1
    out = _cv(clause, court)
    if bool(out) != bool(_old_touch(clause, court)):
        _c["cp_differs"] += 1
    return out
SV._clause_touches_court = _counted_cv
_ca = SA.clause_names_court
def _counted_ca(clause, court):
    _c["cp_calls"] += 1
    out = _ca(clause, court)
    if bool(out) != bool(_old_touch(clause, court)):
        _c["cp_differs"] += 1
    return out
SA.clause_names_court = _counted_ca

_KEYS = ("hs_calls", "hs_slice_smaller", "sr_calls", "sr_false", "mm_calls", "mm_reseated",
         "lb_calls", "lb_store_won", "sb_calls", "cp_calls", "cp_differs")
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_s14f_p2_series_arms_final.json"))
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

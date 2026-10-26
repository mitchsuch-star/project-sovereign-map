"""S14f p3 "the nine rulings" (`docs/DESIGN_REFINEMENT.md` §S14E D12 … D20;
the rows `docs/BUG_FIXES.md` §S14E) — the BASELINE_SERIES attribution for the
rulings' backend seams that the AI's path walks (Golden Rule 5), each seam's
reach COUNTED in the child (an arm whose seam never bites cannot pass for a
byte-identical one). Chained from `tools/_s14f_p2_series_arms_final.json`
(part 2's ALL).

    DM = the DEFENDER's committed term and the band's ratio re-seated on the
         exact per-outcome expectation (S14E-D12, `CombatExecutor.
         _defender_mean_exact` and `_muster_ratio_exact`) — down: None for
         both (the one-stamp mean, the single ratio). Reach: the calls, the
         re-seated figures; the AI's muster price reads the first.
    DG = an AI court's downgrade through the ONE `execute_downgrade`
         (S14E-D13, `ai_diplomacy._ai_ai_downgrade`) — down: the old pair-only
         body (the state write, the booked pair hit, nothing else). Reach: the
         calls.
    WS = the stored pair war scores recomputed at the stamp sites (S14E-D14,
         `diplomacy.recalculate_pair_war_score`) — down: a no-op (the morning's
         score until End Turn). Reach: the calls, the stores moved.
    FA = a fleet action restarts Europe's fuse (S14E-D16, `naval.
         _stamp_fleet_action_clock`) — down: a no-op. Reach: the calls (0 on a
         run with no fleet action, recorded as such).
    CH = the AI buys off on its chest less the payments owed (S14E-D19 /
         X190, `war_council._ai_buyoff_funds`) — down: the raw treasury.
         Reach: the calls, the reads where the chest was smaller.
    DR = a drawn battle is contact for the AI's peace gate and the shut-out
         tier (S14E-D20, `diplomacy.pair_has_fought`, `diplomacy.
         ally_dead_in_pair`) — down: the winner-only records. Reach: the
         calls, the verdicts that differ.
    A  = an AI lead's own ATTACKER mean exact too (S14E-X215 — D11's
         player-only gate lifted; the seam is D11's `CombatExecutor.
         _muster_mean_exact`) — down: None (the one-stamp mean for every
         lead). Reach: the calls, the re-seated figures.
    PD = the AI prices the man who will stand (S14E-X216, `enemy_ai.
         priced_defender`) — down: the named target. Reach: the calls, the
         covered targets.
    DC = a drawn battle credits the war-contribution buckets on blood
         (S14E-D21 / X244, `war_contribution.accrue_drawn_contribution`) —
         down: a no-op. Reach: the calls.
    DX = a drawn battle accrues war exhaustion on each side's own dead
         (S14E-D22 / X245, `coalition.add_war_exhaustion_from_draw`) —
         down: a no-op. Reach: the calls.

    python tools/_s14f_p3_series_arms.py [--arms 0,DM,DG,WS,FA,CH,DR,A,PD,DC,DX,ALL] [--jobs 3]

Writes tools/_s14f_p3_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_s14f_p2_series_arms_final.json"
SEAMS = ("DM", "DG", "WS", "FA", "CH", "DR", "A", "PD", "DC", "DX")
ARMS = {"0": set(), **{s: {s} for s in SEAMS}, "ALL": set(SEAMS)}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()

# DM — the defender's mean and the band's ratio, exact
from backend.commands import combat_executor as CE
_dm = CE.CombatExecutor._defender_mean_exact
def _counted_dm(self, outcome_set):
    _c["dm_calls"] += 1
    out = _dm(self, outcome_set)
    if out is not None:
        _c["dm_reseated"] += 1
    return None if "DM" in DOWN else out
CE.CombatExecutor._defender_mean_exact = _counted_dm
_mr = CE.CombatExecutor._muster_ratio_exact
def _counted_mr(self, *a, **k):
    _c["mr_calls"] += 1
    out = _mr(self, *a, **k)
    if out is not None:
        _c["mr_reseated"] += 1
    return None if "DM" in DOWN else out
CE.CombatExecutor._muster_ratio_exact = _counted_mr

# A — an AI lead's own attacker mean exact (X215; D11's seam)
_am = CE.CombatExecutor._muster_mean_exact
def _counted_am(self, outcome_set):
    _c["a_calls"] += 1
    out = _am(self, outcome_set)
    if out is not None:
        _c["a_reseated"] += 1
    return None if "A" in DOWN else out
CE.CombatExecutor._muster_mean_exact = _counted_am

# PD — the AI prices the man who will stand (X216)
from backend.ai import enemy_ai as EA
_pd = EA.priced_defender
def _counted_pd(world, target, *a, **k):
    _c["pd_calls"] += 1
    out = _pd(world, target, *a, **k)
    if out is not target:
        _c["pd_covered"] += 1
    return target if "PD" in DOWN else out
EA.priced_defender = _counted_pd

# DC — a draw credits the war-contribution buckets (D21)
from backend.game_logic import war_contribution as WCN
_dc = WCN.accrue_drawn_contribution
def _counted_dc(*a, **k):
    _c["dc_calls"] += 1
    return None if "DC" in DOWN else _dc(*a, **k)
WCN.accrue_drawn_contribution = _counted_dc

# DX — a draw accrues war exhaustion (D22)
from backend.game_logic import coalition as CO
_dx = CO.add_war_exhaustion_from_draw
def _counted_dx(*a, **k):
    _c["dx_calls"] += 1
    return None if "DX" in DOWN else _dx(*a, **k)
CO.add_war_exhaustion_from_draw = _counted_dx

# DG — the AI's downgrade through the one executor
from backend.game_logic import ai_diplomacy as AD
_dg = AD._ai_ai_downgrade
def _old_ai_ai_downgrade(world, stronger, weaker, state, new_state):
    from backend.game_logic.diplomacy import DOWNGRADE_PENALTIES, set_diplomatic_state
    from backend.game_logic.diplomatic_dialogue import modify_relation_booked
    set_diplomatic_state(world, stronger, weaker, new_state, "ai_ai_downgrade")
    rel_hit = DOWNGRADE_PENALTIES.get((state, new_state), {{}}).get("relation_target", -10)
    modify_relation_booked(world, stronger, weaker, rel_hit, "downgrade", stronger, weaker)
    return {{"success": True, "new_state": new_state}}
def _counted_dg(world, stronger, weaker, state, new_state, *a, **k):
    _c["dg_calls"] += 1
    if "DG" in DOWN:
        return _old_ai_ai_downgrade(world, stronger, weaker, state, new_state)
    return _dg(world, stronger, weaker, state, new_state, *a, **k)
AD._ai_ai_downgrade = _counted_dg

# WS — the stored pair score recomputed at the stamp sites
from backend.game_logic import diplomacy as DP
_ws = DP.recalculate_pair_war_score
def _counted_ws(world, a, b, *x, **k):
    _c["ws_calls"] += 1
    if "WS" in DOWN:
        return None
    key = world._make_diplo_key(a, b)
    before = (getattr(world, "war_scores", {{}}) or {{}}).get(key)
    out = _ws(world, a, b, *x, **k)
    after = (getattr(world, "war_scores", {{}}) or {{}}).get(key)
    if before != after:
        _c["ws_moved"] += 1
    return out
DP.recalculate_pair_war_score = _counted_ws

# FA — a fleet action stamps the clock
from backend.game_logic import naval as NV
_fa = NV._stamp_fleet_action_clock
def _counted_fa(world, attacker, defender, *a, **k):
    _c["fa_calls"] += 1
    return None if "FA" in DOWN else _fa(world, attacker, defender, *a, **k)
NV._stamp_fleet_action_clock = _counted_fa

# CH — the AI's buy-off on the chest
from backend.game_logic import war_council as WC
_ch = WC._ai_buyoff_funds
def _counted_ch(world, target, *a, **k):
    _c["ch_calls"] += 1
    raw = int((getattr(world, "nation_gold", {{}}) or {{}}).get(target, 0) or 0)
    out = _ch(world, target, *a, **k)
    if int(out) != raw:
        _c["ch_differs"] += 1
    return raw if "CH" in DOWN else out
WC._ai_buyoff_funds = _counted_ch

# DR — a drawn battle is contact
_hf = DP.pair_has_fought
def _counted_hf(world, key, *a, **k):
    _c["dr_calls"] += 1
    records = bool((getattr(world, "battle_records", {{}}) or {{}}).get(key))
    out = _hf(world, key, *a, **k)
    if bool(out) != records:
        _c["dr_differs"] += 1
    return records if "DR" in DOWN else out
DP.pair_has_fought = _counted_hf
_ad = DP.ally_dead_in_pair
def _counted_ad(world, key, nation, *a, **k):
    _c["dr_calls"] += 1
    out = _ad(world, key, nation, *a, **k)
    drawn = int((DP.drawn_battle_dead(world, key) or {{}}).get(nation, 0) or 0)
    if drawn:
        _c["dr_differs"] += 1
    return (int(out) - drawn) if "DR" in DOWN else out
DP.ally_dead_in_pair = _counted_ad

_KEYS = ("dm_calls", "dm_reseated", "mr_calls", "mr_reseated", "a_calls", "a_reseated",
         "pd_calls", "pd_covered", "dc_calls", "dx_calls", "dg_calls", "ws_calls", "ws_moved",
         "fa_calls", "ch_calls", "ch_differs", "dr_calls", "dr_differs")
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_s14f_p3_series_arms_final.json"))
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

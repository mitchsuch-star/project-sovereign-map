"""S14h part 2 "the third measure's P3s" (`docs/BUG_FIXES.md` §S14G, S14G-13 … 33;
`docs/DESIGN_REFINEMENT.md` §S14G D4, D5) — the BASELINE_SERIES attribution for
the part's backend seams that the AI's road can reach (Golden Rule 5), each
seam's reach COUNTED in the child (an arm whose seam never bites cannot pass
for a byte-identical one). Chained from `tools/_s14h_series_arms_final.json`'s
arm "0" — part 1's shipped tree, which IS the standing BASELINE_SERIES (an
arm's name is the set of seams held DOWN; "0" is the shipped tree, "ALL" every
seam down).

    FS = a tie between roads of equal length and terrain goes to own or allied
         soil (S14G-33, `WorldState.foreign_soil_edge_cost`) — down: 0.0 for
         every province (push order decides, today's roads). Reach: the calls,
         the foreign edges priced. The AI's columns read it too (S14G-X159,
         `plot_route` passes the mover) and the BFS tie key (X33.5).
    GS = an AI counter's second gold sweetener of the same shape is folded into
         one line carrying the sum (S14G-23, `ai_diplomacy.add_counter_gold_
         sweetener`) — down: append a second line (today's two). Reach: the
         calls, the merges.
    MG = the armistice's projected relation counts the player's running
         courtship (S14G-24, `diplomacy.armistice_mission_gain`) — down: 0
         (the natural thaw alone). Reach: the calls, the non-zero gains (0 on
         the passive run: no AI court has a mission).
    SS = the sovereign does not sail — the verb refuses him and the AI's
         expedition rung passes him over (S14G-X85, `naval.sovereign_stays`)
         — down: False (no gate, no filter). Reach: the calls, the sovereigns
         met (0 on the shipped board: no AI court authors one).
    CO = the evacuation corridor is granted only after a WAR or ARMISTICE
         pair's treaty (S14G-21, `withdrawal.corridor_applies`) — down: True
         for every ratified treaty (today's nation-wide corridor). Reach: the
         calls, the refusals.
    RS = the player's attack refreshes sight after its retreat and advance
         (S14G-20, `CombatExecutor._refresh_sight_after_attack`, player-only
         by its guard) — down: a no-op. Reach: the calls, the player's.
    SP = a treaty's corridor serves the corps the PAIR strands, not every
         stranded corps of the nation (S14G-X100, `withdrawal.stranded_by_
         pair`) — down: True for every corps (today's nation-wide set).
         Reach: the calls, the exclusions (the AI's corps too).

    python tools/_s14h_p2_series_arms.py [--arms 0,FS,GS,MG,SS,CO,RS,SP,ALL] [--jobs 3]

Writes tools/_s14h_p2_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_s14h_series_arms_final.json"
SEAMS = ("FS", "GS", "MG", "SS", "CO", "RS", "SP")
ARMS = {"0": set(), **{s: {s} for s in SEAMS}, "ALL": set(SEAMS)}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()

# FS — ties go to own soil (S14G-33)
from backend.models import world_state as WS
_fs = WS.WorldState.foreign_soil_edge_cost
def _counted_fs(self, mover_nation, region_name, *a, **k):
    _c["fs_calls"] += 1
    out = _fs(self, mover_nation, region_name, *a, **k)
    if out:
        _c["fs_foreign"] += 1
    return 0.0 if "FS" in DOWN else out
WS.WorldState.foreign_soil_edge_cost = _counted_fs

# GS — one gold line per shape on an AI counter (S14G-23)
from backend.game_logic import ai_diplomacy as AD
_gs = AD.add_counter_gold_sweetener
def _old_add(terms, sweetener):
    terms.setdefault("sweeteners", []).append(sweetener)
    return terms
def _counted_gs(terms, sweetener, *a, **k):
    _c["gs_calls"] += 1
    before = len((terms or {{}}).get("sweeteners", []) or [])
    if "GS" in DOWN:
        return _old_add(terms, sweetener)
    out = _gs(terms, sweetener, *a, **k)
    after = len((out or {{}}).get("sweeteners", []) or [])
    if after == before:
        _c["gs_merged"] += 1
    return out
AD.add_counter_gold_sweetener = _counted_gs

# MG — the courtship in the truce's projection (S14G-24)
from backend.game_logic import diplomacy as DP
_mg = DP.armistice_mission_gain
def _counted_mg(*a, **k):
    _c["mg_calls"] += 1
    out = _mg(*a, **k)
    if out:
        _c["mg_nonzero"] += 1
    return 0 if "MG" in DOWN else out
DP.armistice_mission_gain = _counted_mg

# SS — the sovereign does not sail (S14G-X85)
from backend.game_logic import naval as NV
_ss = NV.sovereign_stays
def _counted_ss(marshal, *a, **k):
    _c["ss_calls"] += 1
    out = _ss(marshal, *a, **k)
    if out:
        _c["ss_sovereigns"] += 1
    return False if "SS" in DOWN else out
NV.sovereign_stays = _counted_ss

# CO — the corridor only after a war's or truce's treaty (S14G-21)
from backend.game_logic import withdrawal as WD
_co = WD.corridor_applies
def _counted_co(*a, **k):
    _c["co_calls"] += 1
    out = _co(*a, **k)
    if not out:
        _c["co_refused"] += 1
    return True if "CO" in DOWN else out
WD.corridor_applies = _counted_co

# RS — the player's attack refreshes sight (S14G-20)
from backend.commands import combat_executor as CE
_rs = CE.CombatExecutor._refresh_sight_after_attack
def _counted_rs(self, ctx, *a, **k):
    _c["rs_calls"] += 1
    try:
        if getattr(ctx.marshal, "nation", None) == getattr(ctx.world, "player_nation", None):
            _c["rs_player"] += 1
    except Exception:
        pass
    return None if "RS" in DOWN else _rs(self, ctx, *a, **k)
CE.CombatExecutor._refresh_sight_after_attack = _counted_rs

# SP — the corridor scoped to the pair (S14G-X100)
_sp = WD.stranded_by_pair
def _counted_sp(*a, **k):
    _c["sp_calls"] += 1
    out = _sp(*a, **k)
    if not out:
        _c["sp_excluded"] += 1
    return True if "SP" in DOWN else out
WD.stranded_by_pair = _counted_sp

_KEYS = ("fs_calls", "fs_foreign", "gs_calls", "gs_merged", "mg_calls", "mg_nonzero",
         "ss_calls", "ss_sovereigns", "co_calls", "co_refused", "rs_calls", "rs_player",
         "sp_calls", "sp_excluded")
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_s14h_p2_series_arms_final.json"))
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

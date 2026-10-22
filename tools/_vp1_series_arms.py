"""VP-1 "The Emperor's Designs", S14b part 1 (`docs/VP1_DESIGNS_SPEC.md` §7, §9)
— the BASELINE_SERIES attribution for the part's backend seams, each one's
reach COUNTED in the child (an arm whose seam never bites cannot pass for a
byte-identical one):

    D  = the designs' store (`imperial_designs.tick`, `note_ratification`,
         `drift_suspended`, `order_decay`; S14b part 3: the stamp
         `stamp_decisive_peace` — reach `decisive_stamps` — and the Acts'
         `decree` — reach `acts_decreed`) — down: inert. Reach: the calls
         that found an ARMED store (part 1: 0, the shipped boot authored
         none; part 2 ships the block — 396 reads on the ambient series, 12
         with the seam down — and the ambient France never proclaims, so
         nothing moves).
    X1 = `emergent_designs.held_cessions_are_punitive` — down: False. Reach:
         the bilateral ratifier's held cessions handed to the punitive record.
    X2 = `game_end.note_armistice_exit` — down: `count_peace`. Reach: the
         signed armistice exits with the player a party.
    X3 = `game_end.receiver_in_bloc` — down: the literal `to == player`.
         Reach: the calls whose answer differs from the literal.
    X12 = `diplomacy.regen_dp_for` read by the counter's dry run before a
         court's purse is written — down: the old zero. Reach: the
         projections made.
    X13 = `diplomacy.seed_purse` (S14b part 2's head: the boot seed and a
         carved court's birth) — down: the empty purses. Reach: the purses
         seeded.

    python tools/_vp1_series_arms.py [--arms 0,D,X1,X2,X3,X12,X13,ALL] [--jobs 3]

Writes tools/_vp1_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_rr6_x3_series_arms_final.json"
SEAMS = ("D", "X1", "X2", "X3", "X12", "X13")
ARMS = {"0": set(), "D": {"D"}, "X1": {"X1"}, "X2": {"X2"}, "X3": {"X3"}, "X12": {"X12"}, "X13": {"X13"}, "ALL": set(SEAMS)}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
from backend.game_logic import imperial_designs as ID
from backend.game_logic import emergent_designs as ED
from backend.game_logic import game_end as GE
_armed = ID.armed
def _counted_armed(world):
    out = _armed(world)
    if out:
        _c["designs_armed_reads"] += 1
    return out
ID.armed = _counted_armed
if "D" in DOWN:
    ID.tick = lambda world, turn: []
    ID.note_ratification = lambda world, **k: None
    ID.drift_suspended = lambda world, nation: False
    ID.order_decay = lambda world, nation: 0
_sdp = ID.stamp_decisive_peace
def _counted_sdp(world, turn):
    if "D" in DOWN:
        return None
    rec = _sdp(world, turn)
    if rec is not None:
        _c["decisive_stamps"] += 1
    return rec
ID.stamp_decisive_peace = _counted_sdp
_dec = ID.decree
def _counted_dec(world, act_id):
    _c["acts_decreed"] += 1
    return _dec(world, act_id)
ID.decree = _counted_dec
_rpc = ED.record_punitive_cessions
def _counted_rpc(world, cessions, offsets=None):
    _c["punitive_pairs"] += sum(len(v or []) for v in (cessions or {{}}).values())
    return _rpc(world, cessions, offsets=offsets)
ED.record_punitive_cessions = _counted_rpc
if "X1" in DOWN:
    ED.held_cessions_are_punitive = lambda: False
_nae = GE.note_armistice_exit
def _counted_nae(world, a, b, **k):
    if getattr(world, "player_nation", "") in (a, b):
        _c["player_armistice_exits"] += 1
    if "X2" in DOWN:
        return GE.count_peace(world, a, b)
    return _nae(world, a, b, **k)
GE.note_armistice_exit = _counted_nae
_rib = GE.receiver_in_bloc
def _counted_rib(world, receiver, player):
    out = _rib(world, receiver, player)
    literal = bool(receiver) and receiver == player
    if out != literal:
        _c["bloc_reads_not_literal"] += 1
    return literal if "X3" in DOWN else out
GE.receiver_in_bloc = _counted_rib
from backend.game_logic import diplomacy as DI
_rdf = DI.regen_dp_for
_in_seed = [False]
def _counted_rdf(world, nation):
    if _in_seed[0]:                 # the boot seed's own reading (X13), never X12's
        return _rdf(world, nation)
    _c["dry_run_purse_projections"] += 1
    return -10 ** 6 if "X12" in DOWN else _rdf(world, nation)
DI.regen_dp_for = _counted_rdf
_sp = DI.seed_purse
def _counted_sp(world, nation):
    if "X13" in DOWN:
        return 0
    _in_seed[0] = True
    try:
        n = _sp(world, nation)
    finally:
        _in_seed[0] = False
    _c["boot_purses_seeded"] += n
    return n
DI.seed_purse = _counted_sp
_KEYS = ("designs_armed_reads", "punitive_pairs", "player_armistice_exits",
         "bloc_reads_not_literal", "dry_run_purse_projections", "boot_purses_seeded",
         "decisive_stamps", "acts_decreed")
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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_vp1_series_arms_final.json"))
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

"""Pre-Deploy S13b part 1 (October 14, 2026 — `docs/BUG_FIXES.md` §DD-B) —
the BASELINE_SERIES attribution for DD-B's fixes.

Every behaviour change that could reach the 40-turn ambient sim has ONE
function seam; an arm with a rule DOWN patches that seam IN THE CHILD before
the sim boots (the WO slice 9 idiom, with seams instead of module levers —
the code-health ratchet forbids a new lever):

    C = call_to_arms.asks_the_callee      (DDB-2 / DDB-D8: the letter, not the cascade; down -> False)
    T = contingent.truce_courts           (DDB-3 / DDB-D9: a truce keeps a contingent at its post; down -> [])
    R = contingent.takes_its_own_road     (DDB-X7: a released contingent takes its court's road; down -> False)
    X = diplomacy.bilateral_war_score_weight   (DDB-X5 / DW-2: x0.65; down -> 0.3)
    S = settlement_scoring._has_non_trivial_terms (DDB-6: proposer-paid terms skipped; down -> the shipped read)
    H = game_end.homeland_returns         (DDB-12: an ally's retaken homeland goes home; down -> no returns)
    A = diplomacy.war_age_acceptance_mod  (DDB-X11, part 2: the curve's maximum 65; down -> the -30 curve)
    F = ai_diplomacy._send_floor          (DDB-X11, part 2: the send filter re-read at x0.65; down -> 20)

DDB-1, DDB-4, DDB-5, DDB-7 … 11 and DDB-X8 / X10 are the player's own roads
(the passive France never proposes, counters or opens a table) or display
reads; they have no seam here. Nor do part 2's DDB-X9 / X12 (the letters'
status-quo lines: display, read when a letter is shown).

Arm 0 (every lever down) must reproduce the recorded series byte for byte.
The reach is COUNTED in the child — for a lever whose arm is byte-identical,
the count says whether its code was reached at all.

    python tools/_ddb_s13b_series_arms.py [--arms 0,C,T,R,ALL] [--jobs 4] [--prior JSON]

Writes tools/_ddb_s13b_series_arms_final.json (committed with the landing
record). Run with --prior <the pre-slice series> once BASELINE_SERIES is
re-recorded (the default reads the recorded constant).
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

# key: (module, seam, the shipped (pre-slice) answer when the rule is DOWN)
LEVERS = {
    "C": ("backend.game_logic.call_to_arms", "asks_the_callee", "False"),
    "T": ("backend.game_logic.contingent", "truce_courts", "[]"),
    "R": ("backend.game_logic.contingent", "takes_its_own_road", "False"),
    "X": ("backend.game_logic.diplomacy", "bilateral_war_score_weight", "0.3"),
    "S": ("backend.game_logic.settlement_scoring", "_has_non_trivial_terms",
          "_orig(a[0], ())"),
    "H": ("backend.game_logic.game_end", "homeland_returns", "(a[3], {})"),
    "A": ("backend.game_logic.diplomacy", "war_age_acceptance_mod",
          "(0 if (not k.get('extracts_value') or a[0] is None or max(0, int(a[0])) >= 8)"
          " else -int(round(30 * (8 - max(0, int(a[0]))) / 8)))"),
    "F": ("backend.game_logic.ai_diplomacy", "_send_floor", "20.0"),
}
ARMS = {"0": set(), **{k: {k} for k in LEVERS}, "ALL": set(LEVERS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, name, down) in ALL.items():
    if key not in UP:
        mod = importlib.import_module(mod_name)
        setattr(mod, name, eval("lambda *a, **k: " + down, {{"_orig": getattr(mod, name)}}))
import backend.game_logic.call_to_arms as CTA
import backend.game_logic.contingent as CG
import backend.game_logic.diplomacy as DP
_c = collections.Counter()

_o_post = CTA.post_call
def _post(world, **k):
    _c["call_posted|" + str(k.get("ally")) + "|" + str(k.get("target"))] += 1
    return _o_post(world, **k)
CTA.post_call = _post
_o_ref = CTA.refuse_call
def _ref(world, terms, how="refused"):
    out = _o_ref(world, terms, how=how)
    _c["call_" + str(out.get("status")) + "|" + how] += 1
    return out
CTA.refuse_call = _ref
_o_res = DP._resolve_offensive_call_path
def _res(world, **k):
    if k.get("callee") == getattr(world, "player_nation", "France"):
        _c["france_resolved_by_the_cascade|" + str(k.get("aggressor"))] += 1
    return _o_res(world, **k)
DP._resolve_offensive_call_path = _res
_o_truce = CG.truce_courts
def _truce(world, lord, vassal):
    out = _o_truce(world, lord, vassal)
    if out:
        _c["truce_shared|" + str(lord) + "|" + str(vassal)] += 1
    return out
CG.truce_courts = _truce
import backend.game_logic.game_end as GE
_o_home = GE.homeland_returns
def _home(world, holder_leader, ceder, kept):
    out = _o_home(world, holder_leader, ceder, kept)
    if out[1]:
        _c["homeland_returned|" + str(holder_leader) + "|" + str(ceder)] += 1
    return out
GE.homeland_returns = _home
_o_rel = CG.release_home
def _rel(world, marshal):
    out = _o_rel(world, marshal)
    _c["release_home|" + str(getattr(marshal, "name", "")) + "|" + ("beat" if out else "none")] += 1
    return out
CG.release_home = _rel
import backend.game_logic.ai_diplomacy as AID
_o_floor = AID._send_floor
def _floor(proposal, world, nation):
    out = _o_floor(proposal, world, nation)
    if out < 20:
        _c["send_floor_lowered|" + str(nation)] += 1
    return out
AID._send_floor = _floor
_o_age = DP.war_age_acceptance_mod
def _age(turns_at_war, *, extracts_value):
    out = _o_age(turns_at_war, extracts_value=extracts_value)
    if out:
        _c["war_age_charged|" + str(out)] += 1
    return out
DP.war_age_acceptance_mod = _age

def _dump():
    print("REACH=" + repr(dict(_c)))
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
    code = CHILD.format(up=sorted(up), all_levers=LEVERS, runner=str(RUNNER))
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
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_ddb_s13b_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior,
           "levers": {k: f"{m}.{n}" for k, (m, n, _d) in LEVERS.items()},
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
        print(f"arm {arm:>3}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}",
              flush=True)
    if "ALL" in out["arms"]:
        for arm, rec in out["arms"].items():
            rec["first_divergence_vs_all"] = first_divergence(
                rec["series"], out["arms"]["ALL"]["series"])
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

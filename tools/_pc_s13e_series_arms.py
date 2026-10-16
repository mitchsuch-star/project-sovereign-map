"""The peace rulings, part 1 (S13e part 1, October 16, 2026 —
`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §46, `docs/BUG_FIXES.md` §PC:
PC-R1, PC-R8, PC-F9, F50, F51) — the BASELINE_SERIES attribution for every
behaviour change that can reach the 40-turn ambient sim.

Each change has ONE function seam; an arm with a rule DOWN patches that seam
IN THE CHILD before the sim boots (the DD-B idiom — seams, never module
levers; the code-health ratchet caps the levers):

    C = settlement_ratify.carried_in_allies      (PC-R1 ii: the leader's peace is
                                                  common to its side; down -> [] —
                                                  no ally's pair is carried)
    Y = ai_diplomacy.coalition_loyalty_penalty   (PC-R1 iii: COALITION_SPEC §6a's
                                                  loyalty term on the bilateral;
                                                  down -> 0)
    H = ai_diplomacy.honest_peace_never_silent   (PC-F9: P1's honest peace below
                                                  the split is force-sent;
                                                  down -> the send filter rules)
    W = ai_diplomacy.leave_a_winning_court_its_war (PC-F50: the leader's letter
                                                  never covers a court winning
                                                  its own pair; down -> every
                                                  court at war is covered)
    G = settlement_scoring.side_gold_credit_share (PC-F50: gold credits the payee
                                                  in full, the side at 0.5;
                                                  down -> 1.0, every court in full)
    R = settlement_helpers.reseat_leaders_after_exit (PC-F51: a side whose leader
                                                  left by a separate peace
                                                  re-seats it; down -> never)

PC-R1 (i) (the HARD_STOP a WARNING) and (iv) (the words), PC-R8 (the counsel)
and the client rows are reads the passive France of the sim never makes —
they have no seam. Arm 0 (every rule down) must reproduce the recorded
series byte for byte. The reach is COUNTED in the child — for a rule whose
arm is byte-identical, the count says whether its code was reached at all.

    python tools/_pc_s13e_series_arms.py [--arms 0,C,Y,H,W,G,R,ALL] [--jobs 4] [--prior JSON]

Writes tools/_pc_s13e_series_arms_final.json (committed with the landing
record).
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

# key: (module, seam, the shipped (pre-slice) answer when the rule is DOWN —
# an expression over the call's positional args `a`)
LEVERS = {
    "C": ("backend.game_logic.settlement_ratify", "carried_in_allies", "[]"),
    "Y": ("backend.game_logic.ai_diplomacy", "coalition_loyalty_penalty", "0"),
    "H": ("backend.game_logic.ai_diplomacy", "honest_peace_never_silent", "None"),
    "W": ("backend.game_logic.ai_diplomacy", "leave_a_winning_court_its_war", "list(a[2])"),
    "G": ("backend.game_logic.settlement_scoring", "side_gold_credit_share", "1.0"),
    "R": ("backend.game_logic.settlement_helpers", "reseat_leaders_after_exit", "[]"),
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
import backend.game_logic.settlement_ratify as SRM
import backend.game_logic.ai_diplomacy as AIM
import backend.game_logic.settlement_scoring as SCM
import backend.game_logic.settlement_helpers as SHM
_c = collections.Counter()

def _count(mod, name, key, measure):
    orig = getattr(mod, name)
    def wrapped(*a, **k):
        out = orig(*a, **k)
        _c[key + "|" + measure(a, k, out)] += 1
        return out
    setattr(mod, name, wrapped)

_count(SRM, "carried_in_allies", "carry_in", lambda a, k, out: "carried" if out else "none")
_count(AIM, "coalition_loyalty_penalty", "loyalty", lambda a, k, out: "charged" if out else "zero")
_count(AIM, "honest_peace_never_silent", "honest_peace", lambda a, k, out: "forced")
_count(AIM, "leave_a_winning_court_its_war", "coverage",
       lambda a, k, out: "narrowed" if len(out) < len(list(a[2])) else "whole")
_count(SCM, "side_gold_credit_share", "gold_share", lambda a, k, out: str(out))
_count(SHM, "reseat_leaders_after_exit", "reseat", lambda a, k, out: "reseated" if out else "kept")

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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_s13e_series_arms_final.json"))
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

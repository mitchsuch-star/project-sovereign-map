"""PC-R7 (ii) part 3 (Pre-Deploy S14 part 3, October 20, 2026 — the league's
no-separate-peace bond, Chaumont; `docs/audits/PEACE_CONUNDRUM_2026_10_15.md`
§46 J (ii), `docs/BUG_FIXES.md` §PC) — the BASELINE_SERIES attribution for
every change of the part that can reach the 40-turn ambient sim (the passive
France declares nothing, signs nothing and binds nobody, so only the AI's own
roads count).

Each change has ONE seam; an arm with a rule DOWN patches it IN THE CHILD
before the sim boots (the DD-B idiom — seams, never module levers):

    B = bond.ai_paymaster_binds    (the league's paymaster binds the member
                                    about to break ranks; down -> [], no bond
                                    is ever minted)
    D = bond.break_ranks_depth     (the bonded member's lines read deeper —
                                    P1's clause, the league gate's clock, the
                                    exhaustion forecast, the truce's spent line
                                    PC-X53, the AI pair exits PC-X55; down ->
                                    zeros, the stock lines)
    T = bond.table_component       (the bond's price on the court's row at the
                                    table; down -> 0)
    L = bond.bilateral_component   (the bond's price in the bilateral; down -> 0)
    S = bond.hope_subsidy          (PC-X54: the bond is a subsidy flowing to her
                                    — the truce's hope term; down -> None)
    X = bond.pair_bond             (PC-X61: the truce's automatic exits closed
                                    while a bond binds the pair; down -> None)
    P = bond.holds_her_letter      (PC-X65: a bonded member writes no separate
                                    P8 letter of her own; down -> False)
    K = bond.letter_keeps_payers   (PC-X66: the league letter keeps the payer
                                    of a covered court's bond; down -> [])
    C = bond.consent_held          (PC-X66: a bonded court's readiness is no
                                    consent to a letter leaving her payer at
                                    war; down -> False)

Everything else the part built is the player's own road (the Cabinet rows,
the bind verb, the bid's opening draft, the guided bid row, the counsel's
words) or reachable only through a bond. With B down no bond exists, so the
reads are inert: arm 0 (every rule down) must reproduce the prior byte for
byte, and so must every arm with B down; arm B alone is the bond's gold (its
stream and its renege arm) with every read of it down; ALL is the shipped
tree, attributed by its first divergence. The reach is COUNTED in the child (bonds minted, reneged, lapsed).

    python tools/_pc_s14p3_series_arms.py [--arms 0,B,D,T,L,S,X,P,K,C,ALL] [--jobs 3] [--prior JSON]

Writes tools/_pc_s14p3_series_arms_final.json (committed with the landing
record). The prior defaults to S14 part 2's ALL series
(tools/_pc_s14p2_series_arms_final.json), which equals the BASELINE_SERIES
the part found.
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
PRIOR_RECORD = ROOT / "tools" / "_pc_s14p2_series_arms_final.json"

_ZERO_DEPTH = '{"score": 0, "exhaustion": 0, "strength": 0, "payer": ""}'
_ZERO_TABLE = ('{"score": 0, "payer": "", "aim": "", "amount": 0, "turns_left": 0, '
               '"common_peace": False}')
# key: (module, seam, the shipped (pre-part) answer when the rule is DOWN)
LEVERS = {
    "B": ("backend.game_logic.bond", "ai_paymaster_binds", "[]"),
    "D": ("backend.game_logic.bond", "break_ranks_depth", _ZERO_DEPTH),
    "T": ("backend.game_logic.bond", "table_component", _ZERO_TABLE),
    "L": ("backend.game_logic.bond", "bilateral_component", "0"),
    "S": ("backend.game_logic.bond", "hope_subsidy", "None"),
    "X": ("backend.game_logic.bond", "pair_bond", "None"),
    "P": ("backend.game_logic.bond", "holds_her_letter", "False"),
    "K": ("backend.game_logic.bond", "letter_keeps_payers", "[]"),
    "C": ("backend.game_logic.bond", "consent_held", "False"),
}
DATA_LEVERS: dict = {}
ALL_KEYS = set(LEVERS) | set(DATA_LEVERS)
ARMS = {"0": set(), **{k: {k} for k in sorted(ALL_KEYS)}, "ALL": set(ALL_KEYS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
DATA = {data_levers!r}
for key, (mod_name, name, down) in ALL.items():
    if key not in UP:
        mod = importlib.import_module(mod_name)
        setattr(mod, name, eval("lambda *a, **k: " + down, {{"_orig": getattr(mod, name), "_mod": mod}}))
for key, stmts in DATA.items():
    if key not in UP:
        exec(stmts, {{}})
import backend.game_logic.bond as BD
import backend.game_logic.instruments as IN
_c = collections.Counter()
_mints = []

def _wrap_binds():
    orig = BD.ai_paymaster_binds
    def wrapped(world, *a, **k):
        out = orig(world, *a, **k)
        for ev in out or []:
            _mints.append((int(getattr(world, "current_turn", 0) or 0), ev.get("payer"), ev.get("recipient"),
                           int(ev.get("amount", 0) or 0)))
            _c["mint"] += 1
        return out
    BD.ai_paymaster_binds = wrapped
_wrap_binds()

def _wrap_pass():
    orig = IN.process_instruments
    def wrapped(world, *a, **k):
        out = orig(world, *a, **k)
        for ev in out or []:
            if ev.get("kind") == "bond" or ev.get("instrument") == "bond":
                _c[str(ev.get("type")) + "|" + str(ev.get("reason") or ev.get("breaker") or "")] += 1
        return out
    IN.process_instruments = wrapped
_wrap_pass()

def _dump():
    print("REACH=" + repr({{"counts": dict(_c), "mints": _mints}}))
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
    code = CHILD.format(up=sorted(up), all_levers=LEVERS, data_levers=DATA_LEVERS, runner=str(RUNNER))
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
    """S14 part 2's final ALL series — the prior this part is attributed
    against (it equals the runner's BASELINE_SERIES before this part)."""
    rec = json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))
    return list(rec["arms"]["ALL"]["series"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--prior", default="", help="JSON list: the pre-part series (default: S14 part 2's ALL)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_s14p3_series_arms_final.json"))
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
        print(f"arm {arm:>11}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}",
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

"""The peace rulings, part 2 (S13e part 2, October 16, 2026 —
`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §46 D and I, `docs/BUG_FIXES.md`
§PC: PC-R2, PC-R3, PC-X9) — the BASELINE_SERIES attribution for every
behaviour change that can reach the 40-turn ambient sim.

Each change has ONE function seam; an arm with a rule DOWN patches that seam
IN THE CHILD before the sim boots (the DD-B idiom — seams, never module
levers; the code-health ratchet caps the levers):

    L = diplomacy.truce_keeps_the_ledger     (PC-R2 D1-2: a truce keeps the pair's
                                              stores and the war's age; down -> the
                                              old pops at the truce)
    E = coalition.truce_holds_exhaustion     (PC-R2 / ruling H: a court whose only
                                              wars are truces holds its exhaustion;
                                              down -> the old -5 a turn)
    H = diplomacy.truce_hope_alive           (PC-R2 D4: the three-term hope read by
                                              the AI's ask and the expiry; down ->
                                              always alive: the old truce-above-the-
                                              split, never a dictated exit)
    T = ai_diplomacy.dictated_tier           (PC-R3 I1-2: the letter's tier from the
                                              court's leverage and the ratchet; down
                                              -> tier 0, the old one-lump letter)
    I = ai_diplomacy.war_priced_indemnity    (PC-R3 I3: the indemnity priced to the
                                              war; down -> the purse-scaled lump, no
                                              stream)

PC-R2's signed exits (`game_end.SIGNED_PEACE_REASONS`), PC-F69's floor,
PC-F82's broken truce and PC-X9's exhaustion pop are reads the sim can
reach only through the seams above or not at all (the passive France signs
no bilateral peace and breaks no truce) — they have no seam of their own.
Arm 0 (every rule down) must reproduce the recorded series byte for byte;
every other arm is attributed by its first divergence. The reach is COUNTED
in the child.

    python tools/_pc_s13e2_series_arms.py [--arms 0,L,E,H,T,I,ALL] [--jobs 3] [--prior JSON]

Writes tools/_pc_s13e2_series_arms_final.json (committed with the landing
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
# an expression over the call's positional args `a` and keyword args `k`;
# `_orig` is the live seam, `_mod` the module)
LEVERS = {
    "L": ("backend.game_logic.diplomacy", "truce_keeps_the_ledger", "False"),
    "E": ("backend.game_logic.coalition", "truce_holds_exhaustion", "False"),
    "H": ("backend.game_logic.diplomacy", "truce_hope_alive",
          "{'alive': True, 'members': [], 'subsidy': None, 'exhaustion': {}, "
          "'alive_terms': ['league'], 'dead_terms': []}"),
    "T": ("backend.game_logic.ai_diplomacy", "dictated_tier",
          "{'tier': 0, 'base': 0, 'ratchet': 0, 'capital_held': False, 'label': 'Reichenbach', "
          "'asks': '', 'next_tier': 1, 'next_label': 'Frankfurt', 'next_asks': ''}"),
    "I": ("backend.game_logic.ai_diplomacy", "war_priced_indemnity",
          "{'lump': int(_mod.purse_scaled_indemnity(a[0], a[1], a[3], a[4], "
          "*(a[5:6] or [k.get('gold_mult', 1.0)]))), 'stream': 0, 'turns': 0}"),
}
ARMS = {"0": set(), **{k: {k} for k in LEVERS}, "ALL": set(LEVERS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, name, down) in ALL.items():
    if key not in UP:
        mod = importlib.import_module(mod_name)
        setattr(mod, name, eval("lambda *a, **k: " + down, {{"_orig": getattr(mod, name), "_mod": mod}}))
import backend.game_logic.diplomacy as DM
import backend.game_logic.coalition as COM
import backend.game_logic.ai_diplomacy as AIM
_c = collections.Counter()

def _count(mod, name, key, measure):
    orig = getattr(mod, name)
    def wrapped(*a, **k):
        out = orig(*a, **k)
        _c[key + "|" + measure(a, k, out)] += 1
        return out
    setattr(mod, name, wrapped)

_count(DM, "truce_keeps_the_ledger", "ledger", lambda a, k, out: "kept" if out else "popped")
_count(COM, "truce_holds_exhaustion", "exhaustion", lambda a, k, out: "held" if out else "ticked")
_count(DM, "truce_hope_alive", "hope", lambda a, k, out: "alive" if out.get("alive") else "dead")
_count(AIM, "dictated_tier", "tier", lambda a, k, out: str(out.get("tier")))
_count(AIM, "war_priced_indemnity", "indemnity",
       lambda a, k, out: "war" if out.get("stream") or out.get("turns") else "purse")

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
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_s13e2_series_arms_final.json"))
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

"""PC-R7 (ii) part 1 (Pre-Deploy S14 part 1, October 20, 2026 —
`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §46 J (ii), `docs/BUG_FIXES.md`
§PC) — the BASELINE_SERIES attribution for every change of the part that can
reach the 40-turn ambient sim (the passive France signs nothing, so only the
AI's own roads count).

Each change has ONE seam; an arm with a rule DOWN patches it IN THE CHILD
before the sim boots (the DD-B idiom — seams, never module levers):

    P = compensation.letter_compensation_ask   (the beaten court's letter to the
                                                player asks its design pointed
                                                elsewhere; down -> None, the
                                                letter as it was)
    D = the desire profiles' 1805 names         (PC-X30: Austria covets Munich,
                                                Britain Brabant, the Dresden /
                                                Munich special bonuses; down ->
                                                the legacy names alone)

Everything else the part built is reachable only through a compensation
clause (the validator, both scorers' arms, both ratifiers' apply arm, the
punitive netting, the ally's reaction) — which only P writes for the AI — or
through the player's own roads (the guided rows, the hand-off and PC-X28, the
peace-table road's words PC-X29). Arm 0 (every rule down) must reproduce the
prior byte for byte; every other arm is attributed by its first divergence.
The reach is COUNTED in the child.

    python tools/_pc_s14_series_arms.py [--arms 0,P,D,ALL] [--jobs 3] [--prior JSON]

Writes tools/_pc_s14_series_arms_final.json (committed with the landing
record). The prior defaults to S13b part 4's ALL series
(tools/_ddb_s13b4_series_arms_final.json), which equals BASELINE_SERIES.
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
PRIOR_RECORD = ROOT / "tools" / "_ddb_s13b4_series_arms_final.json"

# key: (module, seam, the shipped (pre-part) answer when the rule is DOWN)
LEVERS = {
    "P": ("backend.game_logic.compensation", "letter_compensation_ask", "None"),
}
# data seams: key -> python statements run in the child when the rule is DOWN
DATA_LEVERS = {
    "D": (
        "import backend.game_logic.diplomatic_templates as _DT\n"
        "import backend.game_logic.diplomacy as _DI\n"
        "_DT.NATION_DESIRE_PROFILES['Austria']['covets_regions'].remove('Munich')\n"
        "_DT.NATION_DESIRE_PROFILES['Britain']['covets_regions'].remove('Brabant')\n"
        "_DI.SPECIAL_BONUSES['Prussia'].pop('territory_dresden')\n"
        "_DI.SPECIAL_BONUSES['Austria'].pop('territory_munich')\n"
    ),
}
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
import backend.game_logic.compensation as COM
import backend.game_logic.diplomacy as DIM
_c = collections.Counter()

def _count(mod, name, key, measure):
    orig = getattr(mod, name)
    def wrapped(*a, **k):
        out = orig(*a, **k)
        _c[key + "|" + measure(a, k, out)] += 1
        return out
    setattr(mod, name, wrapped)

_count(COM, "letter_compensation_ask", "ask", lambda a, k, out: "asked" if out else "no")
_count(COM, "apply_territory_compensate", "apply", lambda a, k, out: "applied" if out and out[0] else "dropped")
_count(DIM, "_has_bargain_strategic_interest", "bargain_interest",
       lambda a, k, out: ("new_name" if any(str(x) in ("Munich", "Brabant") for x in list(a) + list(k.values())) else "other")
       + ("_yes" if out else "_no"))

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
    """S13b part 4's final ALL series — the prior this part is attributed
    against (it equals the runner's BASELINE_SERIES)."""
    rec = json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))
    return list(rec["arms"]["ALL"]["series"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--prior", default="", help="JSON list: the pre-part series (default: S13b part 4's ALL)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_s14_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior,
           "levers": {**{k: f"{m}.{n}" for k, (m, n, _d) in LEVERS.items()},
                      **{k: "data: the desire profiles' 1805 names" for k in DATA_LEVERS}},
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

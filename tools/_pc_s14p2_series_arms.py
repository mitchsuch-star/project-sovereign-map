"""PC-R7 (ii) part 2 (Pre-Deploy S14 part 2, October 20, 2026 —
`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §46 J (ii), `docs/BUG_FIXES.md`
§PC) — the BASELINE_SERIES attribution for every change of the part that can
reach the 40-turn ambient sim (the passive France declares nothing and signs
nothing, so only the AI's own roads count).

Each change has ONE seam; an arm with a rule DOWN patches it IN THE CHILD
before the sim boots (the DD-B idiom — seams, never module levers):

    A = declared_goals.design_articles   (the AI's design war declares its
                                          design's provinces; down -> [], the
                                          declaration as it was)
    L = declared_goals.undeclared_terms  (the table's legitimacy read without
                                          the declared articles; down -> the
                                          terms unchanged)
    R = declared_goals.settle_at_peace   (each article settled at the peace, a
                                          dropped one refunding half; down -> [])
    O = declared_goals.declared_draft    (the table's opening draft on the
                                          declared articles; down -> [])
    M = declared_goals.objective_articles (PC-X37: the war's objective reads its
                                          declared articles as its aims;
                                          down -> [])
    P = declared_goals.declared_province_ask (PC-X40: a court's dictated letter
                                          asks the province it declared first;
                                          down -> "", its own pick)

Everything else the part built is the player's own road (the card's articles
step, the counsel's road, the guided rows, the bilateral warnings, the words)
or reachable only through an article — which only A writes for the AI. Arm 0
(every rule down) must reproduce the prior byte for byte; every other arm is
attributed by its first divergence. The reach is COUNTED in the child.

    python tools/_pc_s14p2_series_arms.py [--arms 0,A,L,M,O,P,R,ALL] [--jobs 3] [--prior JSON]

Writes tools/_pc_s14p2_series_arms_final.json (committed with the landing
record). The prior defaults to S14 part 1's ALL series
(tools/_pc_s14_series_arms_final.json), which equals BASELINE_SERIES.
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
PRIOR_RECORD = ROOT / "tools" / "_pc_s14_series_arms_final.json"

# key: (module, seam, the shipped (pre-part) answer when the rule is DOWN)
LEVERS = {
    "A": ("backend.game_logic.declared_goals", "design_articles", "[]"),
    "L": ("backend.game_logic.declared_goals", "undeclared_terms", "list(a[1] or [])"),
    "R": ("backend.game_logic.declared_goals", "settle_at_peace", "[]"),
    "O": ("backend.game_logic.declared_goals", "declared_draft", "[]"),
    "M": ("backend.game_logic.declared_goals", "objective_articles", "[]"),
    "P": ("backend.game_logic.declared_goals", "declared_province_ask", "''"),
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
import backend.game_logic.declared_goals as DG
_c = collections.Counter()

def _count(mod, name, key, measure):
    orig = getattr(mod, name)
    def wrapped(*a, **k):
        out = orig(*a, **k)
        _c[key + "|" + measure(a, k, out)] += 1
        return out
    setattr(mod, name, wrapped)

_count(DG, "design_articles", "design", lambda a, k, out: "declared" if out else "none")
_count(DG, "declare_articles", "declare", lambda a, k, out: "charged" if out.get("alarm") else "none")
_count(DG, "settle_at_peace", "settle", lambda a, k, out: ",".join(sorted({{r["settled"] for r in out}})) or "none")
_count(DG, "undeclared_terms", "legit", lambda a, k, out: "exempted" if len(out) != len(list(a[1] or [])) else "same")
_count(DG, "declared_draft", "draft", lambda a, k, out: "declared" if out else "none")
_count(DG, "objective_articles", "objective", lambda a, k, out: "articles" if out else "none")
_count(DG, "declared_province_ask", "letter", lambda a, k, out: "declared" if out else "none")

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
    """S14 part 1's final ALL series — the prior this part is attributed
    against (it equals the runner's BASELINE_SERIES)."""
    rec = json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))
    return list(rec["arms"]["ALL"]["series"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--prior", default="", help="JSON list: the pre-part series (default: S14 part 1's ALL)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_s14p2_series_arms_final.json"))
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

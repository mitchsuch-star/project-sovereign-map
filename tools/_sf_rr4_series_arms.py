"""SF-RR4 "war, truce and the standing order" (Score Finish residue 3, October 21,
2026; `docs/BUG_FIXES.md` §Score Finish Step 8 / §RR4, `docs/DESIGN_REFINEMENT.md`
EG-D3) — the BASELINE_SERIES attribution for every change of the slice that can
reach the 40-turn ambient sim (the passive France declares nothing and signs
nothing, so only the AI's own roads count).

Each change has ONE seam; an arm with a rule DOWN patches it IN THE CHILD before
the sim boots (the DD-B idiom — seams, never module levers). The bench is
authored content, so its two arms are DATA levers (the boot undone in the
child):

    B = the secondaries' bench (EG-D3: Spain's La Romana, Blake, Cuesta;
        Sweden's Toll, Adlercreutz; Bavaria's Wrede — `marshal_pool`; down ->
        the three courts' pools emptied at the boot, as before the slice)
    N = the contingents re-cast (Wrede and La Romana moved to their benches,
        so Bavaria's contingent is Raglovich's and Spain's Kindelan's; down ->
        the old Wrede / La Romana lists. With N down and B up a name sits both
        lists and the contingent falls back to "<Adjective> Contingent")
    R = reforms.ai_repeal_before_lapse (SFR-B14: a court whose law would
        lapse repeals one first; down -> None, the lapse rule alone)
    P = reforms.ai_holds_the_purse (RR4-X9: a court facing a lapse spends no
        gold this admin phase; down -> False)
    J = enemy_ai.ai_hop_backtracks (SFR-D35: no hop back onto ground stood on
        this phase at a non-urgent rung; down -> False)
    V = enemy_ai.ai_records_the_visit (SFR-D35: every successful order marks
        the province as visited; down -> the move and the retreat alone)
    H = movement_executor.harassment_losses (SFR-D31: only a court at war
        harasses a marching corps; down -> any other court's works)
    A = combat_executor.answering_defender (SFR-D6: the muster and its odds
        price the man the cover rule puts in the field — read by the glory
        hunt's gate on both boards; down -> the named target)
    O = combat_executor.holds_a_post (SFR-D5: a marshal on his HOLD's post
        does not reinforce; down -> the literal's flag alone)

ALL is the shipped tree, attributed by its first divergence against the prior
(the runner's BASELINE_SERIES at the slice's entry). The reach is COUNTED in the
child (commissions per court, the bench's men by name, repeals and lapses).

    python tools/_sf_rr4_series_arms.py [--arms 0,B,N,R,ALL] [--jobs 3] [--prior JSON]

Writes tools/_sf_rr4_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_pc_s14p3_series_arms_final.json"

# key: (module, seam, the pre-slice answer when the rule is DOWN)
_OLD_HARASSMENT = (
    "(0 if not (a[2] and a[2].controller and a[2].controller != a[1].nation) else "
    "(int(a[1].strength * 0.04) if a[2].has_building('fortification') else 0) + "
    "(int(a[1].strength * 0.02) if (a[2].garrison_detachment and a[2].garrison_strength > 0) else 0))")
LEVERS = {
    "R": ("backend.game_logic.reforms", "ai_repeal_before_lapse", "None"),
    "P": ("backend.game_logic.reforms", "ai_holds_the_purse", "False"),
    "J": ("backend.ai.enemy_ai", "ai_hop_backtracks", "False"),
    "V": ("backend.ai.enemy_ai", "ai_records_the_visit",
          "(a[0] or {}).get('action') in ('move', 'retreat')"),
    "H": ("backend.commands.movement_executor", "harassment_losses", _OLD_HARASSMENT),
    "A": ("backend.commands.combat_executor", "answering_defender", "a[1]"),
    "O": ("backend.commands.combat_executor", "holds_a_post",
          "bool(getattr(a[0], 'holding_position', False))"),
}

_OLD_CONTINGENTS = {
    "Bavaria": [{"name": "Wrede", "personality": "aggressive",
                 "skills": {"tactical": 6, "shock": 6, "defense": 5, "logistics": 5,
                            "administration": 5, "command": 6},
                 "tactical_skill": 6, "trust": {"value": 60}}],
    "Spain": [{"name": "La Romana", "personality": "cautious",
               "skills": {"tactical": 5, "shock": 5, "defense": 5, "logistics": 6,
                          "administration": 5, "command": 5},
               "tactical_skill": 5, "trust": {"value": 60}}],
}

# key: statements run in the child when the rule is DOWN (the boot undone)
DATA_LEVERS = {
    "B": (
        "import backend.models.world_state as _WS\n"
        "_fs = _WS.WorldState.from_scenario\n"
        "def _no_bench(*a, **k):\n"
        "    w = _fs(*a, **k)\n"
        "    for n in ('Spain', 'Sweden', 'Bavaria'):\n"
        "        w.marshal_pool.pop(n, None)\n"
        "    return w\n"
        "_WS.WorldState.from_scenario = staticmethod(_no_bench)\n"
    ),
    "N": (
        "import backend.models.world_state as _WS\n"
        "_fs2 = _WS.WorldState.from_scenario\n"
        f"_OLD = {_OLD_CONTINGENTS!r}\n"
        "def _old_contingents(*a, **k):\n"
        "    w = _fs2(*a, **k)\n"
        "    w.contingent_commanders.update({k2: [dict(c) for c in v] for k2, v in _OLD.items()})\n"
        "    return w\n"
        "_WS.WorldState.from_scenario = staticmethod(_old_contingents)\n"
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
import backend.game_logic.recruitment as RC
import backend.game_logic.reforms as RF
_c = collections.Counter()
_men = []

def _wrap_commission():
    orig = RC.commission_marshal
    def wrapped(world, nation, candidate, *a, **k):
        out = orig(world, nation, candidate, *a, **k)
        _c["commission|" + str(nation)] += 1
        _men.append((int(getattr(world, "current_turn", 0) or 0), nation, candidate.get("name")))
        return out
    RC.commission_marshal = wrapped
_wrap_commission()

def _count(mod, fn_name, tag, hit=lambda out, a: bool(out)):
    orig = getattr(mod, fn_name, None)
    if orig is None:
        return
    def wrapped(*a, **k):
        out = orig(*a, **k)
        if hit(out, a):
            _c[tag] += 1
        return out
    setattr(mod, fn_name, wrapped)

import backend.ai.enemy_ai as _EA
import backend.commands.movement_executor as _ME
import backend.commands.combat_executor as _CE
_count(RF, "ai_repeal_before_lapse", "repeal_rung")
_count(RF, "ai_holds_the_purse", "purse_held")
_count(RF, "repeal_law", "repealed", hit=lambda out, a: True)
_count(_EA, "ai_hop_backtracks", "backtrack_vetoed")
_count(_ME, "harassment_losses", "harassed")
_count(_CE, "answering_defender", "cover_priced", hit=lambda out, a: out is not a[1])
_count(_CE, "holds_a_post", "post_held")
_orig_lapses = RF.process_law_lapses
def _lapses(world, *a, **k):
    before = sum(1 for e in getattr(world, "event_log", []) or [] if e.get("type") == "law_lapsed")
    out = _orig_lapses(world, *a, **k)
    after = sum(1 for e in getattr(world, "event_log", []) or [] if e.get("type") == "law_lapsed")
    _c["lapsed"] += max(0, after - before)
    return out
RF.process_law_lapses = _lapses

def _dump():
    print("REACH=" + repr({{"counts": dict(_c), "commissions": _men}}))
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
    """S14 part 3's final ALL series — the BASELINE_SERIES this slice found."""
    rec = json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))
    return list(rec["arms"]["ALL"]["series"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: S14 part 3's ALL)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sf_rr4_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior,
           "levers": {**{k: f"{m}.{n}" for k, (m, n, _d) in LEVERS.items()},
                      **{k: "data (the boot undone in the child)" for k in DATA_LEVERS}},
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
        print(f"arm {arm:>4}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {payload.get('reach', {}).get('counts') if payload.get('reach') else None}",
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

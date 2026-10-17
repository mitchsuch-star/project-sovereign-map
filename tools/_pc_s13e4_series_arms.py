"""The peace rulings, part 4 (S13e part 4, October 17, 2026 —
`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §46 J (i) and the AI's memory
rows, `docs/BUG_FIXES.md` §PC) — the BASELINE_SERIES attribution for every
behaviour change that can reach the 40-turn ambient sim.

Each change has ONE function seam; an arm with a rule DOWN patches that seam
IN THE CHILD before the sim boots (the DD-B idiom — seams, never module
levers; the code-health ratchet caps the levers):

    L = settlement_third_party.sub_pair_loser_sues (PC-F28: a beaten sub-pair's
                                                    loser sues inside France's
                                                    instance; down -> None, the
                                                    exhausted exit alone)
    V = vassal.client_leads_its_own_war            (PC-F30: a client follows its
                                                    new lord out of the old lord's
                                                    wars; down -> the old exemption,
                                                    the OTHER court's lead spares
                                                    the pair too)
    C = emergent_designs.collect_cessions_from_clauses
                                                   (PC-F57: a carve counts toward the
                                                    punitive record; down -> the
                                                    carves dropped before the count)
    A = agendas._entry_achieved                    (PC-F74: achieved, never dormant;
                                                    down -> `_entry_satisfied`)
    H = game_end.ally_homeland_returns             (PC-F75: an ally's homeland
                                                    retaken from the ceder's ally goes
                                                    home; down -> {})
    S = diplomatic_templates.continental_system_lift_offered
                                                   (PC-F83: the System lifted drafted
                                                    for Britain; down -> never)
    J = diplomatic_templates.terms_jitter          (PC-F14: one seeded roll per draft;
                                                    down -> the global RNG)
    K = settlement_third_party.client_pair_is_the_lords_war
                                                   (PC-F29: a client's own war takes the
                                                    pair exits; down -> every client pair
                                                    untouchable)
    B = settlement_validation.bilateral_cession_carries
                                                   (PC-X21: the bilateral ratifier carries
                                                    an occupied-homeland cession to a third
                                                    court on the receiving side; down -> the
                                                    silent skip)

The title (PC-R7 i), F41, F72, F33, F11 and F45 are words — the ambient sim's
AI reads none of them. Arm 0 (every rule down) must reproduce part 3's final
series byte for byte; every other arm is attributed by its first divergence.
The reach is COUNTED in the child.

    python tools/_pc_s13e4_series_arms.py [--arms 0,L,V,C,A,H,S,J,K,B,ALL] [--jobs 3] [--prior JSON]

Writes tools/_pc_s13e4_series_arms_final.json (committed with the landing
record). The prior defaults to part 3's ALL series
(tools/_pc_s13e3_series_arms_final.json), which equals BASELINE_SERIES.
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
PRIOR_RECORD = ROOT / "tools" / "_pc_s13e3_series_arms_final.json"

# key: (module, seam, the shipped (pre-slice) answer when the rule is DOWN —
# an expression over the call's positional args `a` and keyword args `k`;
# `_orig` is the live seam, `_mod` the module)
LEVERS = {
    "L": ("backend.game_logic.settlement_third_party", "sub_pair_loser_sues", "None"),
    "V": ("backend.game_logic.vassal", "client_leads_its_own_war",
          "(str(a[0]) in {str((a[2] or {}).get('attacker_leader') or ''), str((a[2] or {}).get('defender_leader') or '')}"
          " or str(a[1]) in {str((a[2] or {}).get('attacker_leader') or ''), str((a[2] or {}).get('defender_leader') or '')})"),
    "C": ("backend.game_logic.emergent_designs", "collect_cessions_from_clauses",
          "_orig([c for c in (a[0] or []) if not (isinstance(c, dict) and c.get('type') == 'create_client')])"),
    "A": ("backend.game_logic.agendas", "_entry_achieved", "_mod._entry_satisfied(*a, **k)"),
    "H": ("backend.game_logic.game_end", "ally_homeland_returns", "{}"),
    "S": ("backend.game_logic.diplomatic_templates", "continental_system_lift_offered", "False"),
    "J": ("backend.game_logic.diplomatic_templates", "terms_jitter", "__import__('random').uniform(0.8, 1.2)"),
    "K": ("backend.game_logic.settlement_third_party", "client_pair_is_the_lords_war", "True"),
    "B": ("backend.game_logic.settlement_validation", "bilateral_cession_carries", "False"),
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
import backend.game_logic.settlement_third_party as TPM
import backend.game_logic.vassal as VM
import backend.game_logic.emergent_designs as EDM
import backend.game_logic.agendas as AGM
import backend.game_logic.game_end as GEM
import backend.game_logic.diplomatic_templates as DTM
_c = collections.Counter()

def _count(mod, name, key, measure):
    orig = getattr(mod, name)
    def wrapped(*a, **k):
        out = orig(*a, **k)
        _c[key + "|" + measure(a, k, out)] += 1
        return out
    setattr(mod, name, wrapped)

_count(TPM, "sub_pair_loser_sues", "loser_sues", lambda a, k, out: "sues" if out else "no")
_count(VM, "client_leads_its_own_war", "client_lead", lambda a, k, out: "own" if out else "follows")
_count(EDM, "collect_cessions_from_clauses", "carve", lambda a, k, out: "carve" if any(isinstance(c, dict) and c.get("type") == "create_client" for c in (a[0] or [])) else "cede")
_count(AGM, "_entry_achieved", "achieved", lambda a, k, out: "achieved" if out else ("dormant" if AGM._entry_satisfied(*a, **k) else "active"))
_count(GEM, "ally_homeland_returns", "ally_home", lambda a, k, out: "returned" if out else "none")
_count(DTM, "continental_system_lift_offered", "lift", lambda a, k, out: "offered" if out else "no")
_count(DTM, "terms_jitter", "jitter", lambda a, k, out: "rolled")
_count(TPM, "client_pair_is_the_lords_war", "client_pair", lambda a, k, out: "lords" if out else "own")
import backend.game_logic.settlement_validation as SVM
_count(SVM, "bilateral_cession_carries", "bilateral_cede", lambda a, k, out: "carried" if out else "dropped")

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
    """Part 3's final ALL series — the prior this part is attributed against
    (it equals the runner's BASELINE_SERIES, pinned by `TestTheSeriesPart3`)."""
    rec = json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))
    return list(rec["arms"]["ALL"]["series"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: part 3's ALL series)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_s13e4_series_arms_final.json"))
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

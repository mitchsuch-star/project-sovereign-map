"""The peace rulings, part 3 (S13e part 3, October 16, 2026 —
`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §46 E, H and G, `docs/BUG_FIXES.md`
§PC: PC-R4, PC-R5, PC-R6 and the F-rows that reach the AI) — the
BASELINE_SERIES attribution for every behaviour change that can reach the
40-turn ambient sim.

Each change has ONE function seam; an arm with a rule DOWN patches that seam
IN THE CHILD before the sim boots (the DD-B idiom — seams, never module
levers; the code-health ratchet caps the levers):

    B = settlement_scoring.court_own_pressure      (PC-R4 E2: the court's row on its OWN
                                                    pair; down -> the side mean)
    S = settlement_baseline.stake_floor_consults   (PC-R4 E3: a court under the 0.10 stake
                                                    floor is covered, not consulted; down ->
                                                    every court consulted = the veto)
    C = ai_diplomacy.letter_consenting_courts      (PC-R4 E5: the letter dry-run as the
                                                    player's; down -> consent by fiat)
    W = ai_diplomacy.letter_writer_and_score       (PC-R4 E5 + F63: the writer by contribution
                                                    on its own pair; down -> the leader on the
                                                    side's stored sum)
    X = coalition.exhaustion_clock_terms           (PC-R5 H: occupation / subsidy / finance;
                                                    down -> the bare +8)
    P = ai_diplomacy.p2_league_gate                (PC-F20: a loyal member sends no stalemate
                                                    truce alone; down -> ungated)
    K = diplomacy.battle_score_from_records        (PC-R6 G: decay then cap; down -> cap then
                                                    decay)
    D = diplomacy.defense_ticking_gain             (PC-R6 G: the shield down with the capital
                                                    held, a ticking that falls; down -> the
                                                    add-only count)
    F = diplomacy.acceptance_reads_the_field       (PC-F71: the bilateral reads the field where
                                                    it moved this turn; down -> the stored score)
    N = naval.posture_blockade_answered            (PC-F64: a strangled denier's posture books
                                                    nothing; down -> the wash)
    T = settlement_third_party.silent_band_white_peace
                                                   (PC-F31: the loser past its threshold, the
                                                    winner under 20 — the white peace carries;
                                                    down -> nothing sent)
    J = settlement_helpers.newcomer_joins_the_war  (PC-F66: a bare declaration folds only beside
                                                    a co-belligerent; down -> always folds)

F77 (the league holding the capital), F58 (the gate's leader), F79 / F80 (the
Congress), F26 / F27 / F38 / F39 / F42 / F55 / F60 / F61 / F68 / F84 are reads
the ambient sim reaches only through the seams above or not at all (the passive
France summons no Congress, authors no table and sends no bilateral peace).
Arm 0 (every rule down) must reproduce part 2's final series byte for byte;
every other arm is attributed by its first divergence. The reach is COUNTED
in the child.

    python tools/_pc_s13e3_series_arms.py [--arms 0,B,S,C,W,X,P,K,D,F,N,T,J,ALL] [--jobs 3] [--prior JSON]

Writes tools/_pc_s13e3_series_arms_final.json (committed with the landing
record). The prior defaults to part 2's ALL series
(tools/_pc_s13e2_series_arms_final.json), which equals BASELINE_SERIES.
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
PRIOR_RECORD = ROOT / "tools" / "_pc_s13e2_series_arms_final.json"

# key: (module, seam, the shipped (pre-slice) answer when the rule is DOWN —
# an expression over the call's positional args `a` and keyword args `k`;
# `_orig` is the live seam, `_mod` the module)
LEVERS = {
    "B": ("backend.game_logic.settlement_scoring", "court_own_pressure", "int(a[0])"),
    "S": ("backend.game_logic.settlement_baseline", "stake_floor_consults",
          "{'consulted': True, 'share': None, 'reason': 'floor_down', 'burdened': False}"),
    "C": ("backend.game_logic.ai_diplomacy", "letter_consenting_courts", "list(a[2])"),
    "W": ("backend.game_logic.ai_diplomacy", "letter_writer_and_score",
          "(str(k.get('leader') or (k.get('covered') or [''])[0]), "
          "int(__import__('backend.game_logic.diplomacy', fromlist=['x']).sum_stored_side_score("
          "a[0], k['player'], list(k['covered']))) if len(k.get('covered') or []) > 1 else "
          "int(__import__('backend.game_logic.diplomacy', fromlist=['x']).get_war_score_for("
          "a[0], k['player'], str(k.get('leader') or k['covered'][0]))))"),
    "X": ("backend.game_logic.coalition", "exhaustion_clock_terms",
          "{'occupation': 0, 'subsidy': 0, 'finance': 0, 'held': [], 'subsidy_role': ''}"),
    "P": ("backend.game_logic.ai_diplomacy", "p2_league_gate", "False"),
    "K": ("backend.game_logic.diplomacy", "battle_score_from_records",
          "_mod._decay_battle_score(max(-_mod.BATTLE_SCORE_CAP, min(_mod.BATTLE_SCORE_CAP, "
          "sum(_mod.BATTLE_SCORE_PER_WIN if r.get('winner') == a[1] else "
          "(-_mod.BATTLE_SCORE_PER_WIN if r.get('winner') == a[2] else 0) for r in a[0]))), a[0], a[3])"),
    "D": ("backend.game_logic.diplomacy", "defense_ticking_gain",
          "sum(1 for r in a[3].get('target_regions', []) if r in a[0].regions and "
          "((a[0].regions[r].controller == a[2]) if a[2] is not None else (a[0].regions[r].controller != a[1])))"),
    "F": ("backend.game_logic.diplomacy", "acceptance_reads_the_field", "False"),
    "N": ("backend.game_logic.naval", "posture_blockade_answered", "False"),
    "T": ("backend.game_logic.settlement_third_party", "silent_band_white_peace", "False"),
    "J": ("backend.game_logic.settlement_helpers", "newcomer_joins_the_war", "True"),
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
import backend.game_logic.settlement_scoring as SCM
import backend.game_logic.settlement_baseline as SBM
import backend.game_logic.naval as NVM
import backend.game_logic.settlement_third_party as TPM
import backend.game_logic.settlement_helpers as SHM
_c = collections.Counter()

def _count(mod, name, key, measure):
    orig = getattr(mod, name)
    def wrapped(*a, **k):
        out = orig(*a, **k)
        _c[key + "|" + measure(a, k, out)] += 1
        return out
    setattr(mod, name, wrapped)

_count(SCM, "court_own_pressure", "own_pressure", lambda a, k, out: "own" if (a[1] is not None and out != a[0]) else "side")
_count(SBM, "stake_floor_consults", "floor", lambda a, k, out: "consulted" if out.get("consulted") else "covered")
_count(AIM, "letter_consenting_courts", "consent", lambda a, k, out: "all" if sorted(out) == sorted(a[2]) else "own")
_count(AIM, "letter_writer_and_score", "writer", lambda a, k, out: "leader" if out[0] == k.get("leader") else "contribution")
_count(COM, "exhaustion_clock_terms", "exhaustion", lambda a, k, out: "named" if any(out.get(x) for x in ("occupation", "subsidy", "finance")) else "bare")
_count(AIM, "p2_league_gate", "p2_gate", lambda a, k, out: "held" if out else "open")
_count(DM, "battle_score_from_records", "battle", lambda a, k, out: "decay_then_cap" if a[0] else "empty")
_count(DM, "defense_ticking_gain", "shield", lambda a, k, out: "down" if out == 0 and any(a[0].regions[r].controller == a[2] for r in a[3].get("target_regions", []) if r in a[0].regions) else ("fall" if out < 0 else "tick"))
_count(DM, "acceptance_reads_the_field", "field", lambda a, k, out: "live" if out else "stored")
_count(NVM, "posture_blockade_answered", "blockade", lambda a, k, out: "answered" if out else "booked")
_count(TPM, "silent_band_white_peace", "band", lambda a, k, out: "white" if out else "no")
_count(SHM, "newcomer_joins_the_war", "fold", lambda a, k, out: "joins" if out else "own_war")

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
    """Part 2's final ALL series — the prior this part is attributed against
    (it equals the runner's BASELINE_SERIES, pinned by `TestTheSeriesPart2`)."""
    rec = json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))
    return list(rec["arms"]["ALL"]["series"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: part 2's ALL series)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_s13e3_series_arms_final.json"))
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

"""GE-3 "The Congress of Paris" — the BASELINE_SERIES dormancy proof (plan D15),
re-built on SEAMS by DDB-X4 (Pre-Deploy S14 part 4, October 20, 2026).

The first cut (September 25, 2026) flipped module booleans —
`THE_CONGRESS_SITS` and kin — which `congress.py` stopped defining when the
levers were folded into the shipped rules, so its arms flipped nothing and
"dormant" was asserted, not measured (`docs/BUG_FIXES.md` §DD-B DDB-X4). The
arms now hold LIVE functions down IN THE CHILD before the sim boots (the DD-B
idiom: `tools/_pc_s14p3_series_arms.py` — seams, never module levers, and a
test never edits a production source file), and COUNT what the Congress does:
every write to `world.congress` (`congress._store`) and every time a new
rule of S14 part 4 bites (the hold names a reason, the signing spends, a
bond deepens a sue line).

Each seam, its old lever, and the shipped answer it reads when DOWN:

    S = congress.process_end_of_turn  (THE_CONGRESS_SITS: the sitting's tick,
                                       E1 and the proclamation; down -> [])
    H = congress.refusal_weight       (THE_CONGRESS_HARDENS_REFUSERS: a
                                       refuser's want; down -> 0)
    R = congress.revanche_weight      (… its Revanche design; down -> 0)
    G = congress.coalition_gate       (THE_CONGRESS_LOWERS_THE_GATE: two
                                       refusers lower the gate; down -> None)
    Q = congress.refuser_qualifies    (… a refuser joins at any relation;
                                       down -> False)
    P = congress.spared_from_coalition(… an answering court is spared;
                                       down -> "")
    L = congress._london_pays         (LONDON_FUNDS_THE_REFUSERS; down -> None)
    D = congress.peace_dividend       (THE_BILLS_COME_DUE: the rentes ×1.5;
                                       down -> 1.0)
    K = congress.petition_stakes      (… a client petition's stakes ×2;
                                       down -> 1)
    U = congress.grudge_contributions (… a dissolution's grudge; down -> [])
    E = congress.no_great_power_stands(THE_UNIVERSAL_MONARCHY; down -> False)
    W = congress.league_waits_on_paris(SF-RR7, the hold: no new league declares
                                       while the Congress sits; down -> "")
    T = congress.the_signing_spends   (SF-RR7, the signing spends the alarm to
                                       the watch and dismisses the brew;
                                       down -> {})
    Y = congress.sue_line             (PC-X69, the bond deepens the sue line;
                                       down -> the stock −40)

The ambient 40-turn board never reaches 45 titled provinces, never summons,
never ratifies a France–great-power peace and never meets E1, so every arm
must reproduce the recorded series byte for byte and count ZERO Congress
writes and ZERO bites of the new rules — that is the dormancy proof (the hold
is READ every coalition turn, `hold_reads`, so the seam is live, and never
bites). The live
hooks are pinned by the driven arms (`tests/test_congress_review_round.py::
TestTheArmsDriven`, `tests/test_vp2_the_imperial_peaces_morning.py`).

    .venv/Scripts/python.exe tools/_ge3_series_arms.py [--arms 0,S,W,T,Y,ALL] [--jobs 3]

Writes tools/_ge3_series_arms.json (committed with the landing record).
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

_CG = "backend.game_logic.congress"
_STOCK_SUE = ('{"score": _mod.sue_score(a[0]), "base": _mod.sue_score(a[0]), '
              '"depth": 0, "payer": ""}')
# key: (module, seam, the answer when the rule is DOWN)
LEVERS = {
    "S": (_CG, "process_end_of_turn", "[]"),
    "H": (_CG, "refusal_weight", "0"),
    "R": (_CG, "revanche_weight", "0"),
    "G": (_CG, "coalition_gate", "None"),
    "Q": (_CG, "refuser_qualifies", "False"),
    "P": (_CG, "spared_from_coalition", '""'),
    "L": (_CG, "_london_pays", "None"),
    "D": (_CG, "peace_dividend", "1.0"),
    "K": (_CG, "petition_stakes", "1"),
    "U": (_CG, "grudge_contributions", "[]"),
    "E": (_CG, "no_great_power_stands", "False"),
    "W": (_CG, "league_waits_on_paris", '""'),
    "T": (_CG, "the_signing_spends", "{}"),
    "Y": (_CG, "sue_line", _STOCK_SUE),
}
ALL_KEYS = set(LEVERS)
ARMS = {"0": set(), **{k: {k} for k in sorted(ALL_KEYS)}, "ALL": set(ALL_KEYS)}
DEFAULT_ARMS = "0,S,W,T,Y,ALL"

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, name, down) in ALL.items():
    if key not in UP:
        mod = importlib.import_module(mod_name)
        setattr(mod, name, eval("lambda *a, **k: " + down, {{"_orig": getattr(mod, name), "_mod": mod}}))
import backend.game_logic.congress as CG
_c = collections.Counter()
_orig_store = CG._store
def _counting_store(world):
    _c["congress_writes"] += 1
    return _orig_store(world)
CG._store = _counting_store
_orig_wait = CG.league_waits_on_paris
def _counting_wait(*a, **k):
    out = _orig_wait(*a, **k)
    _c["hold_reads"] += 1
    if out:
        _c["hold_bites"] += 1
    return out
CG.league_waits_on_paris = _counting_wait
_orig_spend = CG.the_signing_spends
def _counting_spend(*a, **k):
    _c["signings"] += 1
    return _orig_spend(*a, **k)
CG.the_signing_spends = _counting_spend
_orig_line = CG.sue_line
def _counting_line(*a, **k):
    out = _orig_line(*a, **k)
    if int((out or {{}}).get("depth", 0) or 0):
        _c["bonded_sue_lines"] += 1
    return out
CG.sue_line = _counting_line
atexit.register(lambda: print("REACH=" + repr(dict(_c))))
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
    reach = [ln for ln in lines if ln.startswith("REACH=")]
    payload["reach"] = ast.literal_eval(reach[-1].split("=", 1)[1]) if reach else None
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
    ap.add_argument("--arms", default=DEFAULT_ARMS)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_ge3_series_arms.json"))
    args = ap.parse_args()
    prior = recorded_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"recorded": prior,
           "levers": {k: f"{m}.{n}" for k, (m, n, _d) in LEVERS.items()},
           "arm_levers": {k: sorted(ARMS[k]) for k in names}, "arms": {}}
    print("recorded:", prior, flush=True)
    print(f"running {len(names)} arms, {args.jobs} at a time ...", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a]), names)))
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        reach = payload.get("reach") or {}
        out["arms"][arm] = {
            "levers_up": sorted(ARMS[arm]), "series": series,
            "first_divergence_vs_recorded": first_divergence(series, prior),
            "congress_writes": int(reach.get("congress_writes", 0) or 0),
            "reach": reach, "provinces": payload.get("provinces"),
        }
        print(f"arm {arm:>4}: divergence vs recorded "
              f"{out['arms'][arm]['first_divergence_vs_recorded']} · reach {reach}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

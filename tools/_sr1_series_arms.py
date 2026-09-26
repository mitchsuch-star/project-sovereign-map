"""Score Mandate Chunk 1 — the BASELINE_SERIES attribution for SR-1a and
SR-1b (the two Chunk-1 slices that touch the diplomatic state machine).

SR-1a `game_end.STATUS_QUO_IS_A_CESSION`: the retention pass runs at the
ONE diplomatic-state setter on every SIGNED road out of WAR/ARMISTICE, so
the 40-turn ambient board MAY write titles at its AI-AI peaces. A title is
display substrate the AI never reads — except through `reconciled_regions`,
which a retained title is EXCLUDED from by design.

SR-1b `diplomacy.THE_CLIENTS_WAR_IS_THE_LORDS_WAR`: a lord's peace or truce
carries its clients' pairs with the same court, on the four treaty roads.
France's clients (Holland, the Kingdom of Italy, Switzerland) are the only
satellites on the boot, and the passive France signs nothing — but an AI
lord could exist mid-run (a treaty vassalage), so the cascade MAY fire.

The plan's rule (§0-7): byte-identity is measured, never assumed. Each arm
runs the ambient sim in its own hash-pinned subprocess with the levers set
IN THE CHILD before the sim boots (the slice-9 idiom) and COUNTS what each
pass did — retention entries by reason and pair; client pairs moved by
reason — so "the ambient board never …" is a number, not a sentence.

    .venv/Scripts/python.exe tools/_sr1_series_arms.py [--arms all|0,1,2,3,4,5]

SR-1d `ai_diplomacy.THE_LEAGUE_TREATS_WHEN_SPENT` (PR-D1b): the league's
settlement OFFER is gated on P1's break-ranks clause. The passive France
answers no offer, so a later offer changes nothing it does — but the
producer's cooldown writes move, and the spy counts the gate's refusals.

Arms:
    0  all levers down -> must reproduce the recorded series byte-for-byte
    1  SR-1a only
    2  SR-1b only
    3  SR-1a + SR-1b
    4  SR-1d only
    5  the shipped tree (all three)

Writes tools/_sr1_series_arms.json (committed with the landing record).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"

ARMS = {
    0: {"a": False, "b": False, "c": False},
    1: {"a": True, "b": False, "c": False},
    2: {"a": False, "b": True, "c": False},
    3: {"a": True, "b": True, "c": False},
    4: {"a": False, "b": False, "c": True},
    5: {"a": True, "b": True, "c": True},
}

CHILD = r"""
import sys, runpy, atexit, collections
import backend.game_logic.game_end as GE
import backend.game_logic.diplomacy as DP
import backend.game_logic.ai_diplomacy as AD
GE.STATUS_QUO_IS_A_CESSION = {a!r}
DP.THE_CLIENTS_WAR_IS_THE_LORDS_WAR = {b!r}
AD.THE_LEAGUE_TREATS_WHEN_SPENT = {c!r}
_counts = {{"sq_calls": 0, "sq_entries": 0, "sq_titled": 0,
            "sq_by_reason": collections.Counter(), "sq_pairs": collections.Counter(),
            "follow_calls": 0, "follow_moved": 0,
            "follow_by_reason": collections.Counter(), "follow_pairs": collections.Counter(),
            "gate_calls": 0, "gate_refusals": 0, "gate_by_turn": collections.Counter()}}
_orig_gate = AD.league_offer_gate
def _gate(world, war, **kw):
    _counts["gate_calls"] += 1
    out = _orig_gate(world, war, **kw)
    if out is not None:
        _counts["gate_refusals"] += 1
        _counts["gate_by_turn"][int(getattr(world, "current_turn", 0))] += 1
    return out
AD.league_offer_gate = _gate
_orig_sq = GE.title_status_quo_retentions
def _sq(world, a, b, old_state, new_state, reason):
    _counts["sq_calls"] += 1
    out = _orig_sq(world, a, b, old_state, new_state, reason)
    for e in out:
        _counts["sq_entries"] += 1
        n = sum(len(r) for r in (e.get("titled") or {{}}).values())
        _counts["sq_titled"] += n
        _counts["sq_by_reason"][str(reason)] += n
        _counts["sq_pairs"][str(e.get("pair"))] += n
    return out
GE.title_status_quo_retentions = _sq
_orig_follow = DP.follow_the_lord
def _follow(world, a, b, new_state, reason, **kw):
    _counts["follow_calls"] += 1
    out = _orig_follow(world, a, b, new_state, reason, **kw)
    for row in out:
        _counts["follow_moved"] += 1
        _counts["follow_by_reason"][str(reason)] += 1
        _counts["follow_pairs"][str(row.get("pair"))] += 1
    return out
DP.follow_the_lord = _follow
def _dump():
    c = dict(_counts)
    for k in ("sq_by_reason", "sq_pairs", "follow_by_reason", "follow_pairs", "gate_by_turn"):
        c[k] = dict(c[k])
    print("SR1=" + repr(c))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(levers: dict) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)
    code = CHILD.format(runner=str(RUNNER), **levers)
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=1200)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("SR1=")]
    payload["sr1"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
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
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sr1_series_arms.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else [int(x) for x in args.arms.split(",")]
    prior = recorded_series()
    out = {"recorded": prior, "arms": {}}
    for arm in wanted:
        levers = ARMS[arm]
        print(f"arm {arm} {levers} ...", flush=True)
        payload = run_arm(levers)
        series = payload["series"]
        div = first_divergence(series, prior)
        out["arms"][str(arm)] = {
            "levers": levers,
            "series": series,
            "first_divergence_vs_recorded": div,
            "provinces": payload.get("provinces"),
            "sr1": payload.get("sr1"),
        }
        print(f"  divergence vs recorded: {div}; counts: {payload.get('sr1')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

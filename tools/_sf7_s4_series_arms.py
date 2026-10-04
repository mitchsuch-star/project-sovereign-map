"""Score Finish Step 7 slice 4 (the Tilsit clause, SCORE_FINISH_SPEC §6.6,
October 4, 2026) — the BASELINE_SERIES attribution.

The clause is the player's (no AI writes it, §6.6 item 3), so the two levers
that could reach the ambient board are set IN THE CHILD before the 40-turn
ambient sim boots (the slice-9 idiom; the source is never written):

    EXIT  diplomacy.A_MEMBER_AT_WAR_LEAVES_THE_SYSTEM — a member that goes to
          war with the System's lord leaves it, at the WAR transition;
    X5    settlement_actions.THE_PLAIN_ALLIANCE_KEEPS_NO_SYSTEM — the plain
          "Force X into alliance" link writes its choice (player-only).

The reach is COUNTED in the child: every membership write
(`join_continental_system`), every exit (`leave_continental_system`), every
WAR transition that found a member to remove, and the System's member count
each time the income phase applies it.

    python tools/_sf7_s4_series_arms.py [--arms 0,EXIT,X5,ALL] [--prior JSON]

Writes tools/_sf7_s4_series_arms_final.json.
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

LEVERS = {
    "EXIT": ("backend.game_logic.diplomacy", "A_MEMBER_AT_WAR_LEAVES_THE_SYSTEM"),
    "X5": ("backend.game_logic.settlement_actions", "THE_PLAIN_ALLIANCE_KEEPS_NO_SYSTEM"),
}
ARMS = {"0": set(), "EXIT": {"EXIT"}, "X5": {"X5"}, "ALL": set(LEVERS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, name) in ALL.items():
    mod = importlib.import_module(mod_name)
    setattr(mod, name, key in UP)
import backend.game_logic.diplomacy as D
_c = collections.Counter()
_o_j = D.join_continental_system
def _j(world, nation, imposer, reason=""):
    joined = _o_j(world, nation, imposer, reason=reason)
    _c["join|" + str(nation) + "|" + ("joined" if joined else "already")] += 1
    return joined
D.join_continental_system = _j
_o_l = D.leave_continental_system
def _l(world, nation, reason=""):
    left = _o_l(world, nation, reason=reason)
    if left:
        _c["leave|" + str(nation)] += 1
    return left
D.leave_continental_system = _l
_o_a = D.apply_continental_system
def _a(world):
    _c["applied_with_members|" + str(len(getattr(world, "continental_system_members", []) or []))] += 1
    return _o_a(world)
D.apply_continental_system = _a
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
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(k, None)
    code = CHILD.format(up=sorted(up), all_levers=LEVERS, runner=str(RUNNER))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
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
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sf7_s4_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    out = {"prior": prior,
           "levers": {k: f"{m}.{n}" for k, (m, n) in LEVERS.items()},
           "arm_levers": {k: sorted(v) for k, v in ARMS.items()}, "arms": {}}
    for arm in [x.strip() for x in args.arms.split(",") if x.strip()]:
        up = ARMS[arm]
        print(f"arm {arm} (up: {sorted(up) or 'none'}) ...", flush=True)
        payload = run_arm(up)
        series = payload["series"]
        out["arms"][arm] = {
            "levers_up": sorted(up), "series": series,
            "first_divergence_vs_prior": first_divergence(series, prior),
            "provinces": payload.get("provinces"),
            "reach": payload.get("reach"),
        }
        print(f"   divergence vs prior: {out['arms'][arm]['first_divergence_vs_prior']}; "
              f"reach {out['arms'][arm]['reach']}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

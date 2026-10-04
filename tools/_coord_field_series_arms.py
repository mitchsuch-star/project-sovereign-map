"""§6 row 16's build (SF-CL-1-D1, "the coordination is read on the field") —
the BASELINE_SERIES attribution (Score Finish Step 7, October 4, 2026).

The slice MOVES combat by design: an attack from next door now reads the lead's
coordination context in the BATTLE province, where the corps that answer him
stand — so the AI's own attacks (the same resolver, GR5) earn the coordination
the player's do. The series is re-recorded ONCE from this script's ALL arm; arm
0 (the lever DOWN in the child before the 40-turn ambient sim boots, the
slice-9 idiom) must reproduce the recorded series byte for byte. Two levers:
F (the resolver's field read and the preview's lockstep) and G (the glory gate's
`muster_odds` reading under the preview's own priced context). The reach is
COUNTED in the child: every resolver read whose field is not the lead's own
province, every one of those with a stamped bonus, and every gate read with the
band the OTHER gate reading would have weighed.

    python tools/_coord_field_series_arms.py [--arms 0,ALL] [--prior JSON] [--shadow]

`--shadow` adds the SAME-BOARD reading: arm 0's 40 turns (the lever down, the
recorded trajectory), and at every resolver read with a field next door the
lever-up reading is taken too, in a shadow whose transient fields are restored
before the real (lever-down) read — so each battle the slice changes is
measured on the board where it happened, before the trajectories part. The
shadow consumes no RNG; its series must equal arm 0's (checked).

Writes tools/_coord_field_series_arms_final.json (committed with the landing
record). Run with --prior <the pre-slice series> once BASELINE_SERIES is
re-recorded (the default reads the recorded constant).
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
    "F": ("backend.commands.combat_executor", "THE_COORDINATION_IS_READ_ON_THE_FIELD"),
    "G": ("backend.commands.combat_executor", "THE_GATE_READS_THE_PREVIEWS_CONTEXT"),
}
ARMS = {"0": set(), "F": {"F"}, "G": {"G"}, "ALL": set(LEVERS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, name) in ALL.items():
    mod = importlib.import_module(mod_name)
    setattr(mod, name, key in UP)
import backend.commands.combat_executor as CE
_c = collections.Counter()
_o_ctx = CE.CombatExecutor._calculate_coordination_context
def _ctx(self, primary, world, *a, **k):
    field = k.get("field")
    # the RESOLVER's reads only (it alone passes reinforcement_results): the
    # gate's other reading below prices the preview's context, which reads a
    # field too, and must not be counted as a battle
    counted = (field and field != primary.location
               and k.get("reinforcement_results") is not None)
    if counted:
        _c["field_read|" + str(primary.nation)] += 1
    out = _o_ctx(self, primary, world, *a, **k)
    if counted:
        bonus = float(getattr(primary, "total_coordination_attack_bonus", 0.0) or 0.0)
        if bonus > 0:
            _c["field_bonus|" + str(primary.nation)] += 1
    return out
CE.CombatExecutor._calculate_coordination_context = _ctx
# The gate's half: every `muster_odds` read (the glory gate, both boards),
# with the OTHER reading of the gate taken beside it (both are pure) — how
# often the band the gate weighed would have differed.
_o_odds = CE.CombatExecutor.muster_odds
def _odds(self, marshal, enemy, world):
    here = bool(CE.THE_GATE_READS_THE_PREVIEWS_CONTEXT)
    CE.THE_GATE_READS_THE_PREVIEWS_CONTEXT = not here
    try:
        other = _o_odds(self, marshal, enemy, world)["band"]
    finally:
        CE.THE_GATE_READS_THE_PREVIEWS_CONTEXT = here
    out = _o_odds(self, marshal, enemy, world)
    _c["gate_read|" + str(marshal.nation)] += 1
    if out["band"] != other:
        _c["gate_band_differs|" + str(marshal.nation)] += 1
        _c["gate_band|" + out["band"] + "<-" + other] += 1
    return out
CE.CombatExecutor.muster_odds = _odds
def _dump():
    print("REACH=" + repr(dict(_c)))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


SHADOW_CHILD = r"""
import sys, runpy, atexit, json
import backend.commands.combat_executor as CE
from backend.models.marshal import Marshal
CE.THE_COORDINATION_IS_READ_ON_THE_FIELD = False
CE.THE_GATE_READS_THE_PREVIEWS_CONTEXT = False
_rows = []
_o_ctx = CE.CombatExecutor._calculate_coordination_context
def _bonus(m):
    return float(getattr(m, "total_coordination_attack_bonus", 0.0) or 0.0)
def _ctx(self, primary, world, *a, **k):
    field = k.get("field")
    resolver = k.get("reinforcement_results") is not None
    if not (field and field != primary.location and resolver):
        return _o_ctx(self, primary, world, *a, **k)
    fields = tuple(Marshal.COORDINATION_TRANSIENT_FIELDS) + ("sovereign_presence",)
    touched = [m for m in world.marshals.values() if m.nation == primary.nation]
    saved = {m.name: {f: (hasattr(m, f), getattr(m, f, None)) for f in fields}
             for m in touched}
    arrivals = [m for m in touched if m.location == field and m.name != primary.name]
    CE.THE_COORDINATION_IS_READ_ON_THE_FIELD = True
    try:
        _o_ctx(self, primary, world, *a, **k)
        new_lead = _bonus(primary)
        new_arr = [_bonus(m) for m in arrivals]
    finally:
        CE.THE_COORDINATION_IS_READ_ON_THE_FIELD = False
        for m in touched:
            for f, (had, value) in saved[m.name].items():
                if had:
                    setattr(m, f, value)
                elif hasattr(m, f):
                    delattr(m, f)
    out = _o_ctx(self, primary, world, *a, **k)
    _rows.append({"turn": int(world.current_turn), "nation": str(primary.nation),
                  "lead": str(primary.name), "field": str(field),
                  "lead_old": round(_bonus(primary), 4), "lead_new": round(new_lead, 4),
                  "arrivals": len(arrivals),
                  "arrivals_old": [round(_bonus(m), 4) for m in arrivals],
                  "arrivals_new": [round(x, 4) for x in new_arr]})
    return out
CE.CombatExecutor._calculate_coordination_context = _ctx
def _dump():
    print("SHADOW=" + json.dumps(_rows))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_shadow() -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(k, None)
    code = SHADOW_CHILD.replace("{runner}", str(RUNNER))  # the child holds braces
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(f"shadow failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    rows = json.loads([ln for ln in lines if ln.startswith("SHADOW=")][-1][len("SHADOW="):])
    by = {}
    for r in rows:
        b = by.setdefault(r["nation"], {"reads": 0, "lead_up": 0, "lead_down": 0,
                                        "lead_same": 0, "lead_delta_sum": 0.0,
                                        "arrival_reads": 0, "arrival_delta_sum": 0.0})
        b["reads"] += 1
        d = r["lead_new"] - r["lead_old"]
        b["lead_delta_sum"] += d
        b["lead_up" if d > 1e-9 else ("lead_down" if d < -1e-9 else "lead_same")] += 1
        for o, n in zip(r["arrivals_old"], r["arrivals_new"]):
            b["arrival_reads"] += 1
            b["arrival_delta_sum"] += n - o
    for b in by.values():
        b["lead_delta_mean"] = round(b.pop("lead_delta_sum") / max(1, b["reads"]), 4)
        b["arrival_delta_mean"] = round(
            b.pop("arrival_delta_sum") / max(1, b["arrival_reads"]), 4)
    return {"series": payload["series"], "provinces": payload.get("provinces"),
            "by_nation": by, "rows": rows}


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
    ap.add_argument("--out", default=str(ROOT / "tools" / "_coord_field_series_arms_final.json"))
    ap.add_argument("--shadow", action="store_true",
                    help="add the same-board reading (arm 0's battles, both readings)")
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
        print(f"   divergence vs prior: {out['arms'][arm]['first_divergence_vs_prior']}",
              flush=True)
    if "ALL" in out["arms"]:
        for arm, rec in out["arms"].items():
            rec["first_divergence_vs_all"] = first_divergence(
                rec["series"], out["arms"]["ALL"]["series"])
    if args.shadow:
        print("shadow (arm 0's board, both readings) ...", flush=True)
        shadow = run_shadow()
        shadow["series_equals_arm_0"] = (
            shadow["series"] == out["arms"].get("0", {}).get("series", prior))
        out["shadow"] = shadow
        print(f"   shadow series == arm 0: {shadow['series_equals_arm_0']}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

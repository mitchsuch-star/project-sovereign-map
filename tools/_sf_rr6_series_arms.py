"""SF-RR6 "the instrument reads what the player sees" (Score Finish residue 5,
October 21, 2026; `docs/BUG_FIXES.md` §Score Finish Step 8 / §The Economy Gate
EG-X4) — the BASELINE_SERIES attribution for the slice's ONE backend change.

Everything else the slice changed is the instrument (the driver's records,
the readers, the DL script, checklist v1.2) and cannot reach the 40-turn
ambient sim. The backend change is EG-X4's: a scout's or a battle's FULL view
expires after FRESH_TURNS instead of standing for good while a PARTIAL read
keeps it "refreshed" — the player's fog, read by the player's surfaces and
by the player's own PURSUE routing (`strategic.py` plots a pursuit to the
store's last sighting). The passive France of the ambient sim orders nothing,
so the series should not move; the arms prove it, and count the reach.

    X = world_state.scouted_view_expired (EG-X4; down -> False, the frozen
        FULL view as before)

An arm with the rule DOWN patches the seam IN THE CHILD before the sim boots
(the DD-B idiom — seams, never module levers). The reach is COUNTED in the
child (views expired), so an arm whose lever never bites cannot pass for a
byte-identical one.

    python tools/_sf_rr6_series_arms.py [--arms 0,ALL] [--jobs 2] [--prior JSON]

Writes tools/_sf_rr6_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_sf_rr4_series_arms_final.json"

# key: (module, seam, the pre-slice answer when the rule is DOWN)
LEVERS = {
    "X": ("backend.models.world_state", "scouted_view_expired", "False"),
}
ARMS = {"0": set(), "ALL": set(LEVERS)}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
_c = collections.Counter()
import backend.models.world_state as _WS
_shipped = _WS.scouted_view_expired
def _counted(*a, **k):
    out = _shipped(*a, **k)
    if out:
        _c["view_expired"] += 1
    return out
_WS.scouted_view_expired = _counted
for key, (mod_name, name, down) in ALL.items():
    if key not in UP:
        mod = importlib.import_module(mod_name)
        _real = getattr(mod, name)
        def _down(*a, _real=_real, **k):
            if _real(*a, **k):
                _c["view_expired_held_down"] += 1
            return eval(down)
        setattr(mod, name, _down)
def _dump():
    print("REACH=" + repr({{"counts": dict(_c)}}))
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
    """SF-RR4's final ALL series — the BASELINE_SERIES this slice found."""
    rec = json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))
    return list(rec["arms"]["ALL"]["series"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: SF-RR4's ALL)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sf_rr6_series_arms_final.json"))
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

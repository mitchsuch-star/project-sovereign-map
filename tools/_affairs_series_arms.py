"""RE-1 "Affairs of State" (`docs/RECURRING_EVENTS_SPEC.md` §16 "The series and
the seams") — the BASELINE_SERIES attribution for the engine's seams, each
one's reach COUNTED in the child (an arm whose seam never bites cannot pass
for a byte-identical one). The prior is HEAD's `BASELINE_SERIES` (never the
working tree's), the S14k rig's rule.

    AF0 = `affairs.deliver_due` — down: no affair is delivered. Reach: the
          affairs' armed ticks, the occurrences delivered.
    AFB = `moments.moment_rows` — down: the moments' tick sees every row.
          Reach: the `#` rows the blindness dropped.
    AFP = the pulse (`affairs.pulse_first` / `pulse_gap`) — down: the authored
          values. Reach: the draws made.
    AFN = `affairs.write_receipt` — down: no dispatch line. Reach: the lines.
    AFA = `affairs.resolve_courts` — inert in v1; reach: its calls on an
          armed world.

On the shipped tree the deck is UNARMED (RE-1), so every reach reads 0 and
every arm reproduces the prior byte for byte; RE-3 arms the deck and this
rig attributes what moves.

    .venv/Scripts/python.exe tools/_affairs_series_arms.py [--arms 0,AF0,AFB,AFP,AFN,AFA,ALL] [--jobs 4]

Writes tools/_affairs_series_arms_final.json (committed with the landing record).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"
sys.path.insert(0, str(ROOT))
from tests._affairs_seams import AFFAIRS_SEAMS_BY_ROW  # noqa: E402

SEAMS = tuple(AFFAIRS_SEAMS_BY_ROW)
ARMS = {"0": set(SEAMS), **{s: {s} for s in SEAMS}, "ALL": set()}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
from backend.game_logic import affairs as AF
from backend.game_logic import moments as MO
_deliver = AF.deliver_due
def _counted_deliver(world, delivered=None):
    if AF.armed(world):
        _c["affairs_armed_ticks"] += 1
    if "AF0" in DOWN:
        return []
    out = _deliver(world, delivered)
    _c["affairs_delivered"] += len(out or [])
    return out
AF.deliver_due = _counted_deliver
_rows = MO.moment_rows
def _counted_rows(state):
    out = _rows(state)
    dropped = sum(1 for k, v in (state or {{}}).items() if isinstance(v, dict)) - len(out)
    _c["blind_rows_dropped"] += max(0, dropped)
    if "AFB" in DOWN:
        return {{str(k): v for k, v in (state or {{}}).items() if isinstance(v, dict)}}
    return out
MO.moment_rows = _counted_rows
_first, _gap = AF.pulse_first, AF.pulse_gap
def _counted_first(world):
    _c["pulse_draws"] += 1
    if "AFP" in DOWN:
        return int(AF.pacing(world)["first"])
    return _first(world)
def _counted_gap(world, n):
    _c["pulse_draws"] += 1
    if "AFP" in DOWN:
        return int(AF.pacing(world)["gap"])
    return _gap(world, n)
AF.pulse_first, AF.pulse_gap = _counted_first, _counted_gap
_receipt = AF.write_receipt
def _counted_receipt(world, line):
    _c["affairs_receipts"] += 1
    if "AFN" in DOWN:
        return None
    return _receipt(world, line)
AF.write_receipt = _counted_receipt
_courts = AF.resolve_courts
def _counted_courts(world):
    _c["court_resolutions"] += 1
    if "AFA" in DOWN:
        return []
    return _courts(world)
AF.resolve_courts = _counted_courts
from backend.game_logic import naval as NV
_sqtick = NV._squadron_tick
def _counted_sqtick(world):
    _c["squadron_ticks"] += sum(1 for _n, r in NV.iter_fleet_records(world) if isinstance(r.get("squadron"), dict))
    if "AFH" in DOWN:
        return []
    out = _sqtick(world)
    _c["squadrons_returned"] += len(out or [])
    return out
NV._squadron_tick = _counted_sqtick
_detach = NV.detach_squadron
def _counted_detach(world, nation, ships, away, to, odds, tag, issued):
    _c["squadrons_sailed"] += 1
    if "AFS" in DOWN:
        return {{}}
    return _detach(world, nation, ships, away, to, odds, tag, issued)
NV.detach_squadron = _counted_detach
_settle = AF.settle_squadrons
def _counted_settle(world):
    if "AFS" in DOWN:
        return []
    out = _settle(world)
    _c["squadrons_settled"] += len(out or [])
    return out
AF.settle_squadrons = _counted_settle
_decrees = AF.ai_decrees
def _counted_decrees():
    _c["decree_reads"] += 1
    if "AFE" in DOWN:
        return False
    return _decrees()
AF.ai_decrees = _counted_decrees
_grant = AF.grant_edict
def _counted_grant(world, lord, e):
    _c["edicts_granted"] += 1
    return _grant(world, lord, e)
AF.grant_edict = _counted_grant
_KEYS = ("affairs_armed_ticks", "affairs_delivered", "blind_rows_dropped", "pulse_draws",
         "affairs_receipts", "court_resolutions", "squadron_ticks", "squadrons_sailed",
         "squadrons_returned", "squadrons_settled", "decree_reads", "edicts_granted")
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}}}}))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(down: set) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE"):
        env.pop(k, None)
    code = CHILD.format(down=sorted(down), runner=str(RUNNER))
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


def prior_series() -> list:
    """HEAD's `BASELINE_SERIES` — the series before this slice, never the
    working tree's (the S14k rig's rule)."""
    rel = RUNNER.relative_to(ROOT).as_posix()
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                          capture_output=True, check=True).stdout.decode("utf-8")
    m = re.search(r"^BASELINE_SERIES = (\[[^\]]*\])", text, re.M)
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_affairs_series_arms_final.json"))
    args = ap.parse_args()
    prior = prior_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior, "seams_down": {k: sorted(ARMS[k]) for k in names}, "arms": {}}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a]), names)))
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        out["arms"][arm] = {"down": sorted(ARMS[arm]), "series": series,
                            "first_divergence_vs_prior": first_divergence(series, prior),
                            "reach": payload.get("reach")}
        print(f"arm {arm:>4}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {(payload.get('reach') or {}).get('counts')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

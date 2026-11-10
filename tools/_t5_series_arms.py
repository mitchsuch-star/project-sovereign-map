"""Session B — the BASELINE_SERIES attribution for Tier 5's five seams
(DYNAMISM_SPEC.md §4, the Tier-5 gate record §4a; November 10, 2026), an
arm per seam raised in the sweep's order, each seam's reach COUNTED in the
child (an arm whose seam never bites cannot pass for a byte-identical one).
The prior is HEAD's `BASELINE_SERIES` (never the working tree's), the S14k
rig's rule.

Arms: `0` — every Tier-5 seam down, the tree before the session (must
reproduce the prior byte for byte); `Q` — DY-2 alone; `QC` — + DY-3; `BERN`
— + DY-1e; `GIFT` — + DY-1f; `ALL` — every seam up, the shipped tree (the
re-pin's value, if the series moves).

    .venv/Scripts/python.exe tools/_t5_series_arms.py [--arms 0,Q,QC,BERN,GIFT,ALL] [--jobs 2]

Writes tools/_t5_series_arms_final.json (committed with the landing record;
a re-run writes its OWN record via --out).
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

ARMS = {
    "0": {"Q", "C", "BERN", "GIFT", "SEAT"},
    "Q": {"C", "BERN", "GIFT", "SEAT"},
    "QC": {"BERN", "GIFT", "SEAT"},
    "BERN": {"GIFT", "SEAT"},
    "GIFT": {"SEAT"},
    "ALL": set(),
}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
_moves = []
from backend.game_logic import game_end as GE
from backend.game_logic import questions as QU
from backend.game_logic import settlement_third_party as TP
def _counted(module, name, key, down_key):
    seam = getattr(module, name)
    def _wrapped():
        _c[key] += 1
        return False if down_key in DOWN else seam()
    setattr(module, name, _wrapped)
_counted(QU, "the_questions_of_europe", "q_seam_reads", "Q")
_counted(QU, "the_congress_rules_a_question", "c_seam_reads", "C")
_counted(TP, "a_lord_signs_for_its_client", "bern_seam_reads", "BERN")
_counted(TP, "a_leader_signs_for_its_allies", "gift_seam_reads", "GIFT")
_counted(GE, "the_emperors_treaty_moves_a_seat", "seat_seam_reads", "SEAT")
_note = QU.note_capture
def _counted_note(world, region, holder, old):
    before = dict(QU.latch(world))
    out = _note(world, region, holder, old)
    after = QU.latch(world)
    if after != before:
        _c["latches"] += 1
        _moves.append([int(world.current_turn), "latch", str(region), str(holder)])
    if out:
        _c["turns"] += 1
        _moves.append([int(world.current_turn), "turns", str(out.get("question")), str(holder)])
    return out
QU.note_capture = _counted_note
_rules = QU.congress_rules
def _counted_rules(world):
    out = _rules(world)
    for row in out:
        _c["rulings"] += 1
        _moves.append([int(world.current_turn), "ruling", str(row.get("question")), str(row.get("court"))])
    return out
QU.congress_rules = _counted_rules
_refuge = TP.sign_at_the_last
def _counted_refuge(world, victim):
    out = _refuge(world, victim)
    if out and any(s != victim for s in (out.get("signed_by") or {{}}).values()):
        _c["lord_refuges"] += 1
        _moves.append([int(world.current_turn), "lord_refuge", str(victim), str(out.get("signed_by"))])
    return out
TP.sign_at_the_last = _counted_refuge
from backend.game_logic import war_council as WC
_side = WC.side_aim_cessions
def _counted_side(*a, **k):
    out = _side(*a, **k)
    if out:
        _c["ally_cessions"] += len(out)
        _moves.append([int(a[0].current_turn), "ally_cession", [c.get("region") for c in out], [c.get("to") for c in out]])
    return out
WC.side_aim_cessions = _counted_side
_seat = GE._seat_the_court
def _counted_seat(world, court, seat):
    out = _seat(world, court, seat)
    if out:
        _c["seats_moved"] += 1
        _moves.append([int(world.current_turn), "seat", str(court), str(seat)])
    return out
GE._seat_the_court = _counted_seat
_KEYS = ("q_seam_reads", "c_seam_reads", "bern_seam_reads", "gift_seam_reads", "seat_seam_reads",
         "latches", "turns", "rulings", "lord_refuges", "ally_cessions", "seats_moved")
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}},
                           "moves": _moves}}))
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
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING",
              "PYTHONDONTWRITEBYTECODE", "INK_IRON_SEAMS"):
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
    """HEAD's `BASELINE_SERIES` — the series before this session, never the
    working tree's (the S14k rig's rule)."""
    rel = RUNNER.relative_to(ROOT).as_posix()
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                          capture_output=True, check=True).stdout.decode("utf-8")
    m = re.search(r"^BASELINE_SERIES = (\[[^\]]*\])", text, re.M)
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_t5_series_arms_final.json"))
    args = ap.parse_args()
    prior = prior_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior, "seams_down": {k: sorted(ARMS[k]) for k in names},
           "arms": {}}
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

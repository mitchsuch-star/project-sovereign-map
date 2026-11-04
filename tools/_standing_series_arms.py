"""AU-1 "the books and the figure" (`docs/AUTHORITY_CURRENCY_SPEC.md` §5.8 "The
instrument and the pins") — the BASELINE_SERIES attribution for the
standing's seams, each one's reach COUNTED in the child (an arm whose seam
never bites cannot pass for a byte-identical one). The prior is HEAD's
`BASELINE_SERIES` (never the working tree's), the S14k rig's rule.

    AUB = `standing.keeps_books` — down: the writer passes the clamped figure
          through and books nothing (HEAD's store). Reach: the writer's
          calls, the rows booked, the threshold events queued.

At AU-1 the books change no figure: the clamp is the clamp, the ring and the
causes are records, the events and the dent are words. So every arm — 0
(every seam down), AUB, ALL (every seam up: the shipped tree) — reproduces
the prior byte for byte, with the reach showing the books DID open on the
ALL arm. The later slices add their arms (AUP, AUK, AUW, AUS, AUC) and
attribute what moves.

    .venv/Scripts/python.exe tools/_standing_series_arms.py [--arms 0,AUB,ALL] [--jobs 3]

Writes tools/_standing_series_arms_final.json (committed with the landing record).
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
from tests._standing_seams import STANDING_SEAMS_BY_ROW  # noqa: E402

SEAMS = tuple(STANDING_SEAMS_BY_ROW)
ARMS = {"0": set(SEAMS), **{s: {s} for s in SEAMS}, "ALL": set()}
# AU-2c: a seam DOWN by default (`standing.letters_armed`, the letters authored
# and not armed) is measured UP on its own arm — every other seam as shipped
ARMS["AUL+"] = set()
UP_ARMS = {"AUL+": {"AUL"}}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
from backend.game_logic import standing as ST
from backend.models import authority as AU
_keeps = ST.keeps_books
def _counted_keeps():
    _c["books_reads"] += 1
    if "AUB" in DOWN:
        return False
    return _keeps()
ST.keeps_books = _counted_keeps
_move = ST.move
def _counted_move(world, lord, delta, cause, party="", **fmt):
    _c["writer_calls"] += 1
    return _move(world, lord, delta, cause, party=party, **fmt)
ST.move = _counted_move
_tmove = AU.AuthorityTracker.move
def _counted_tmove(self, *a, **k):
    rows = len(self.moves)
    events = len((self.held or {{}}).get("events") or [])
    out = _tmove(self, *a, **k)
    _c["rows_booked"] += max(0, len(self.moves) - rows)
    _c["events_queued"] += max(0, len((self.held or {{}}).get("events") or []) - events)
    return out
AU.AuthorityTracker.move = _counted_tmove
# AU-2a the hits: the three seams, each held down on its arm, its reach counted
_hits, _claims, _breach = ST.hits_armed, ST.claims_armed, ST.breach_armed
def _counted_hits():
    _c["hits_reads"] += 1
    return False if "AUP" in DOWN else _hits()
def _counted_claims():
    _c["claims_reads"] += 1
    return False if "AUK" in DOWN else _claims()
def _counted_breach():
    _c["breach_reads"] += 1
    return False if "AUW" in DOWN else _breach()
ST.hits_armed, ST.claims_armed, ST.breach_armed = _counted_hits, _counted_claims, _counted_breach
_claim_fn, _breach_fn, _amends_fn = ST.claims_of_the_army, ST.breach, ST.amends
def _counted_claim(world, marshal, elapsed):
    out = _claim_fn(world, marshal, elapsed)
    if out:
        _c["claims_billed"] += 1
    return out
def _counted_breach_fn(world, preview):
    out = _breach_fn(world, preview)
    if out:
        _c["breaches_booked"] += 1
    return out
def _counted_amends(world, lord, court):
    out = _amends_fn(world, lord, court)
    if out:
        _c["amends_repaid"] += 1
    return out
ST.claims_of_the_army, ST.breach, ST.amends = _counted_claim, _counted_breach_fn, _counted_amends
from backend.game_logic import affairs as AF
_op_armed = AF.op_armed
def _counted_op_armed(op):
    out = _op_armed(op)
    row = (op or {{}}).get("since")
    if row == "AU-2a":
        _c["host_ops_planned" if out else "host_ops_held"] += 1
    elif row == "AU-2b":
        _c["au2b_content_armed" if out else "au2b_content_held"] += 1
    return out
AF.op_armed = _counted_op_armed
# AU-2b the lumps: the seam AUS, its reach counted
_sources = ST.sources_armed
def _counted_sources():
    _c["sources_reads"] += 1
    return False if "AUS" in DOWN else _sources()
ST.sources_armed = _counted_sources
_te, _bul, _ret, _hon, _regrow = ST.te_deum_on_peace, ST.bulletin, ST.the_return, ST.honour_repaid, ST.regrow
def _counted_te(world, key):
    out = _te(world, key)
    if out:
        _c["te_deums"] += 1
    return out
def _counted_bul(world, lord, battle, ours, theirs):
    base, repaid = _bul(world, lord, battle, ours, theirs)
    if base:
        _c["bulletins"] += 1
        _c["points_repaid"] += int(repaid)
    return base, repaid
def _counted_ret(world, lord):
    out = _ret(world, lord)
    if out:
        _c["returns"] += 1
    return out
def _counted_hon(world, lord, marshal):
    out = _hon(world, lord, marshal)
    if out:
        _c["paybacks"] += 1
    return out
def _counted_regrow(world, lord, amount, cause, key, *a, **k):
    out = _regrow(world, lord, amount, cause, key, *a, **k)
    if out and cause in ("ceremony", "act"):
        _c["ceremonies" if cause == "ceremony" else "acts_shown"] += 1
    return out
ST.te_deum_on_peace, ST.bulletin, ST.the_return, ST.honour_repaid, ST.regrow = (
    _counted_te, _counted_bul, _counted_ret, _counted_hon, _counted_regrow)
# AU-2c the Bank and the Pope: the seam AUL — DOWN by default (authored, not
# armed); the AUL+ arm forces it UP; its reach counted
UP = set({up!r})
_letters = ST.letters_armed
def _counted_letters():
    _c["letters_reads"] += 1
    if "AUL" in DOWN:
        return False
    return True if "AUL" in UP else _letters()
ST.letters_armed = _counted_letters
_deliver = AF._deliver
def _counted_deliver(world, cand, turn):
    out = _deliver(world, cand, turn)
    tid = str(((cand or {{}}).get("e") or {{}}).get("id") or "")
    if tid in ("the_bank", "the_popes_ports"):
        _c[tid + "_delivered"] += 1
    return out
AF._deliver = _counted_deliver
_KEYS = ("books_reads", "writer_calls", "rows_booked", "events_queued",
         "hits_reads", "claims_reads", "breach_reads", "claims_billed", "breaches_booked", "amends_repaid",
         "host_ops_planned", "host_ops_held",
         "sources_reads", "te_deums", "bulletins", "points_repaid", "returns", "paybacks",
         "ceremonies", "acts_shown", "au2b_content_armed", "au2b_content_held",
         "letters_reads", "the_bank_delivered", "the_popes_ports_delivered")
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}}}}))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(down: set, up: set = frozenset()) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE"):
        env.pop(k, None)
    code = CHILD.format(down=sorted(down), up=sorted(up), runner=str(RUNNER))
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
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_standing_series_arms_final.json"))
    args = ap.parse_args()
    prior = prior_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior, "seams_down": {k: sorted(ARMS[k]) for k in names},
           "seams_up": {k: sorted(UP_ARMS.get(k, ())) for k in names if UP_ARMS.get(k)}, "arms": {}}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a], UP_ARMS.get(a, frozenset())), names)))
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        out["arms"][arm] = {"down": sorted(ARMS[arm]), "up": sorted(UP_ARMS.get(arm, ())), "series": series,
                            "first_divergence_vs_prior": first_divergence(series, prior),
                            "reach": payload.get("reach")}
        print(f"arm {arm:>4}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {(payload.get('reach') or {}).get('counts')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""S14c "Events and Historical Moments", part 1 (`docs/EVENTS_SPEC.md` §7, §9)
— the BASELINE_SERIES attribution for the part's backend seams, each one's
reach COUNTED in the child (an arm whose seam never bites cannot pass for a
byte-identical one). Chained from `tools/_vp1_series_arms_final.json`:

    M0 = the moments' tick (`moments.tick`) — down: inert. Reach: the ticks
         that found an ARMED store (part 1: 0 — the shipped boot authors no
         block), the letters delivered, the lapses applied, the receipts.
    X8 = the non-treaty registry (`treaty.non_treaty_kind`) — down: "" (every
         context dialogue judged as a treaty again). Reach: the reads that
         returned a registered kind (an ultimatum, an offered crown, a
         broker's ask) — the stamps a passive France never answers.
    X9 = the court-less lapse (`dialogue_manager._extract_lapse_info`'s
         fallback) — reach only: the lapse rows written with no nation.

Part 2's second landing ARMS the deck (M1, M2, M4 in the shipped scenario)
and adds a seam per piece of a letter's reach (the record §7):

    MW = the window resolver (`campaign_variance.resolve_moment_turns`) —
         down: identity. Reach: windows resolved off their value (0 on the
         `historical` series).
    ML = the lapse default (`moments.lapse_default`) — down: the letter
         lapses with no decline applied. Reach: lapses applied.
    MK = the two-turn residence (`moments.keeps_open`) — down: never kept
         (a letter lapses after its first turn). Reach: the end-turn reads
         that kept a letter across an AI phase.
    MN = the rows (`moments._log`, the arrival's rail notice) — down: no log
         row, no notice. Reach: the rows written.
    MH = the wizard exclusion (`DialogueManager.has_current_turn_offers`'s
         moment arm) — down: a moment letter locks the wizard as a court's
         offer does. Reach: the reads whose answer the exclusion changed.
    MR = the crowd-out receipt (`moments._crowd_out`) — down: the letter
         passes silently, no decline, no receipt. Reach: crowd-outs.

Part 4 adds the due mark (S14C-X24):

    MD = the due mark (`moments._mark_due`) — down: a deferred letter is
         forgotten (the part-3 tick: a letter due and deferred whose premise
         fails before its last morning passes silently). Reach: the marks
         written.

    python tools/_s14c_series_arms.py [--arms 0,M0,X8,MW,ML,MK,MN,MH,MR,MD,ALL] [--jobs 3]

Writes tools/_s14c_series_arms_final.json (committed with the landing record).
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
PRIOR_RECORD = ROOT / "tools" / "_vp1_series_arms_final.json"  # the unarmed series (S14b part 3's ALL)
SEAMS = ("M0", "X8", "MW", "ML", "MK", "MN", "MH", "MR", "MD")
ARMS = {"0": set(), **{s: {s} for s in SEAMS}, "ALL": set(SEAMS)}

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
from backend.game_logic import moments as MO
from backend.game_logic import treaty as TR
from backend.models import dialogue_manager as DMOD
_tick = MO.tick
def _counted_tick(world):
    if MO.armed(world):
        _c["moments_armed_ticks"] += 1
    if "M0" in DOWN:
        return []
    out = _tick(world)
    _c["letters_delivered"] += len(out or [])
    return out
MO.tick = _counted_tick
_lapse = MO.lapse_default
def _counted_lapse(world, letter):
    if "ML" in DOWN and MO.is_moment_letter(letter):
        row = MO.status_row(world, MO.moment_id_of(letter))
        if row:
            row.update(status=MO.STATUS_LAPSED, answer=MO.ANSWER_DECLINE)
        _c["moment_lapses"] += 1
        return {{}}
    out = _lapse(world, letter)
    if out:
        _c["moment_lapses"] += 1
    return out
MO.lapse_default = _counted_lapse
_crowd = MO._crowd_out
def _counted_crowd(world, e, turn):
    _c["moment_receipts"] += 1
    if "MR" in DOWN:
        return MO._pass(world, e, MO.PASS_CROWDED, turn)
    return _crowd(world, e, turn)
MO._crowd_out = _counted_crowd
_mark = MO._mark_due
def _counted_mark(world, e, turn):
    _c["due_marks"] += 1
    if "MD" in DOWN:
        return None
    return _mark(world, e, turn)
MO._mark_due = _counted_mark
from backend.game_logic import campaign_variance as CV
_rmt = CV.resolve_moment_turns
def _counted_rmt(moments, seed, historical=None):
    before = [e.get("turn") for e in (moments.get("deck") or []) if isinstance(e, dict)]
    if "MW" in DOWN:
        for e in (moments.get("deck") or []):
            if isinstance(e, dict) and isinstance(e.get("turn"), dict):
                e["turn"] = int(e["turn"].get("value") or 0)
        return moments
    out = _rmt(moments, seed, historical=historical)
    after = [e.get("turn") for e in (moments.get("deck") or []) if isinstance(e, dict)]
    _c["windows_off_value"] += sum(1 for b, a in zip(before, after)
                                   if isinstance(b, dict) and a != b.get("value"))
    return out
CV.resolve_moment_turns = _counted_rmt
_keeps = MO.keeps_open
def _counted_keeps(dialogue, current_turn):
    out = _keeps(dialogue, current_turn)
    if out:
        _c["kept_across_a_phase"] += 1
    return False if "MK" in DOWN else out
MO.keeps_open = _counted_keeps
_log = MO._log
def _counted_log(world, phase, e, **fields):
    _c["moment_rows"] += 1
    if "MN" in DOWN:
        return None
    return _log(world, phase, e, **fields)
MO._log = _counted_log
_deliver = MO.deliver_letter
def _counted_deliver(world, e, turn):
    out = _deliver(world, e, turn)
    if "MN" in DOWN:
        MO._dismiss_notice(world, str(e.get("id")))
    return out
MO.deliver_letter = _counted_deliver
_hcto = DMOD.DialogueManager.has_current_turn_offers
def _counted_hcto(self):
    out = _hcto(self)
    if not out:
        items = [d for d in ([self._current] if self._current else []) + list(self._queue)]
        locks = any(d.get("type", "") in self.CURRENT_TURN_OFFER_TYPES for d in items)
        if locks:
            _c["wizard_reads_unlocked"] += 1
            if "MH" in DOWN:
                return True
    return out
DMOD.DialogueManager.has_current_turn_offers = _counted_hcto
_ntk = TR.non_treaty_kind
def _counted_ntk(letter):
    out = _ntk(letter)
    if out:
        _c["non_treaty_reads"] += 1
    return "" if "X8" in DOWN else out
TR.non_treaty_kind = _counted_ntk
_eli = DMOD.DialogueManager._extract_lapse_info
def _counted_eli(self, dialogue):
    out = _eli(self, dialogue)
    if not out.get("nation"):
        _c["courtless_lapses"] += 1
    return out
DMOD.DialogueManager._extract_lapse_info = _counted_eli
_KEYS = ("moments_armed_ticks", "letters_delivered", "moment_lapses", "moment_receipts",
         "non_treaty_reads", "courtless_lapses", "windows_off_value", "kept_across_a_phase",
         "moment_rows", "wizard_reads_unlocked", "due_marks")
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_s14c_series_arms_final.json"))
    args = ap.parse_args()
    prior = list(json.loads(PRIOR_RECORD.read_text(encoding="utf-8"))["arms"]["ALL"]["series"])
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

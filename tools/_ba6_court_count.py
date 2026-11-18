"""Row MC, BA-6 — the court count: how much happens at court in forty turns
of an AI-played France (`docs/MARSHALATE_SPEC.md` §8; the rule and its two
arms `tools/_ba6_court_rule_2026_11_17.json`).

Wraps the court's recorder (`precedence.record`, through which every bond and
the older writers' moves pass) and its title offers, confers, accounts and
claims with counters, then runs the AI-France harness's own `run_one`
(`tools/ai_france_sweep.py`: PYTHONHASHSEED=0 per child, the sweep's ten seeds,
ambient base 0). Each child also reads the French court's one-way views among
its marshals (the sovereign and captives out) at the boot and at the end.
A seam is held through `INK_IRON_SEAMS` (the harness applies it), so an arm
is the same run with one rule down. Descriptive: it gates nothing.

Usage:
  .venv/Scripts/python.exe tools/_ba6_court_count.py --all --out DIR
  INK_IRON_SEAMS="backend.game_logic.precedence:a_silence_is_remembered_when_pressed=False" \\
      .venv/Scripts/python.exe tools/_ba6_court_count.py --all --out DIR
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def child(seed: str, out: str, turns: int) -> None:
    from backend.game_logic import precedence as P
    from tools import ai_france_sweep as AF
    from tools import ai_v_sweep as base

    tally = collections.Counter()

    def side_of(world, name):
        m = world.marshals.get(name)
        return "France" if getattr(m, "nation", "") == "France" else "courts"

    orig_record = P.record

    def record(world, a, b, kind, place="", **kw):
        got = orig_record(world, a, b, kind, place, **kw)
        if got is not None:
            tally[f"{side_of(world, a)}:{kind}"] += 1
        return got

    P.record = record

    orig_earns = P.victory_earns

    def victory_earns(world, marshal, points, place, *, shadowed):
        before = getattr(marshal, "title_due", None) if marshal is not None else None
        orig_earns(world, marshal, points, place, shadowed=shadowed)
        after = getattr(marshal, "title_due", None) if marshal is not None else None
        if after is not None and after is not before:
            tally[f"{'France' if marshal.nation == 'France' else 'courts'}:title_offered"] += 1

    P.victory_earns = victory_earns

    orig_confer = P._confer

    def _confer(world, marshal, due, passed):
        tally[f"{'France' if marshal.nation == 'France' else 'courts'}:title_conferred"] += 1
        return orig_confer(world, marshal, due, passed)

    P._confer = _confer

    orig_queue = P._queue_account

    def _queue_account(world, lead, others, region):
        tally["France:account_queued"] += 1
        return orig_queue(world, lead, others, region)

    P._queue_account = _queue_account

    orig_claim = P._claim_card

    def _claim_card(world, marshal):
        tally["France:claim_card"] += 1
        return orig_claim(world, marshal)

    P._claim_card = _claim_card

    views = {}

    def court_views(world):
        court = [m for m in world.marshals.values()
                 if m.nation == "France" and not getattr(m, "is_sovereign", False)
                 and P.in_the_court(m) and not getattr(m, "captured_by", "")]
        names = {m.name for m in court}
        dist = collections.Counter(int(v) for m in court
                                   for other, v in (m.relationships or {}).items() if other in names)
        return {str(k): dist[k] for k in sorted(dist)}

    orig_boot, orig_final = base.RunCapture.capture_boot, base.RunCapture.capture_final

    def capture_boot(self):
        views["boot"] = court_views(self.world)
        return orig_boot(self)

    def capture_final(self):
        views["end"] = court_views(self.world)
        return orig_final(self)

    base.RunCapture.capture_boot = capture_boot
    base.RunCapture.capture_final = capture_final

    digest = AF.run_one(seed, 0, turns)
    Path(out).write_text(json.dumps({
        "seed": seed, "turns": turns, "france_battles": digest.get("france_battles", 0),
        "tally": dict(sorted(tally.items())), "views": views,
        "seams": os.environ.get("INK_IRON_SEAMS", ""),
    }, indent=1), encoding="utf-8")


def alive(end: dict) -> bool:
    """The rule's clause 3: at least one Devoted view and at least two Rival or worse."""
    end = {int(k): v for k, v in end.items()}
    return end.get(2, 0) >= 1 and sum(v for k, v in end.items() if k <= -1) >= 2


def parent(out_dir: str, turns: int, jobs: int) -> None:
    from tools.ai_v_sweep import SWEEP_SEEDS, child_env
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    def one(seed):
        args = [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "--seed", seed,
                "--turns", str(turns), "--out", str(out / f"court_{seed}.json")]
        p = subprocess.run(args, env=child_env(seed), cwd=str(ROOT), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=1800)
        return seed, p.returncode, p.stderr[-800:]

    with ThreadPoolExecutor(jobs) as pool:
        for seed, rc, err in pool.map(one, list(SWEEP_SEEDS)):
            print(seed, rc, "" if rc == 0 else err, flush=True)
    total, battles, live = collections.Counter(), 0, 0
    for f in sorted(out.glob("court_*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        total.update(r["tally"])
        battles += int(r.get("france_battles") or 0)
        live += alive(r["views"].get("end", {}))
    print("france battles", battles, "| alive seeds", live, "of", len(SWEEP_SEEDS))
    for k, v in sorted(total.items()):
        print(f"  {k:32s} {v}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    if a.all:
        parent(a.out, a.turns, a.jobs)
    else:
        child(a.seed, a.out, a.turns)

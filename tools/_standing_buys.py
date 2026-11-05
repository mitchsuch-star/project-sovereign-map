"""AU-3a "the three buys" (docs/AUTHORITY_CURRENCY_SPEC.md §5.3, the landing
record §6.5) — the buys arm: the nine commanded scripts played by a SPENDER,
the driver answering every buy it is offered where it is open — `--affair
decree` (the Edict letters' third answer), `--objection word` ("By my word"
where the objection offers it open, else trust), `--petition buy` (Honour him /
By decree where open, else the first enabled arm) — with the standing's and the
moments' traces. The shipped measure answers none of them (the default dials),
so this arm is where the buys are seen in play.

    .venv/Scripts/python.exe tools/_standing_buys.py run --out <dir> [--jobs 3]
    .venv/Scripts/python.exe tools/_standing_buys.py record --out <dir> \
        --shipped <the shipped measure's commanded/arms> --record tools/_standing_buys.json

Seeded paths, not laws: each run's buys are reported per run, never averaged.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BUY_CAUSES = ("edict_decreed", "word_given", "honoured", "by_decree")
STAKE_CAUSES = ("word_lost",)
# AU-2b's lumps — standing coming back by play (§5.5)
REGROWTH_CAUSES = ("bulletin", "bulletin_repaid", "te_deum", "return", "honour_repaid", "ceremony", "act",
                   "field_won", "own_hand_won", "capital_taken")
DIALS = ["--affair", "decree", "--petition", "buy", "--moments-trace", "--standing-trace"]


def _measure():
    spec = importlib.util.spec_from_file_location("_affairs_measure", ROOT / "tools" / "_affairs_measure.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _argv(base: list) -> list:
    """The arm's own argv with the spender's dials: its `--objection` (OP and
    FLD insist) becomes `word`; every other dial added."""
    argv = list(base)
    if "--objection" in argv:
        argv[argv.index("--objection") + 1] = "word"
    else:
        argv += ["--objection", "word"]
    return argv + DIALS


def cmd_run(args) -> int:
    am = _measure()
    arms = am._score_arms()
    out = Path(args.out).resolve() / "arms"
    jobs = [(name, _argv(arms[name]["argv"])) for name in am.COMMANDED]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(lambda j: am.run_arm(out, f"BUY-{j[0]}", j[1]), jobs))
    (Path(args.out) / "run.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    bad = [r for r in results if r["exit"] != 0]
    for r in results:
        print(f"  {r['arm']}: exit {r['exit']} {r['status']} {r['seconds']}s")
    return 1 if bad else 0


def _read_run(run_dir: Path) -> dict:
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    trace = meta.get("standing_trace") or {}
    moves = [m for m in (trace.get("moves") or []) if m.get("lord") == "France"]
    landed = Counter(str(m.get("key") or "") for m in moves if str(m.get("key") or "") in BUY_CAUSES)
    paid = Counter()
    for m in moves:
        if str(m.get("key") or "") in BUY_CAUSES:
            paid[str(m["key"])] += -int(m.get("delta", 0) or 0)
    answers = Counter()
    for line in (run_dir / "digest.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("kind") == "popup" and row.get("key") in ("objection", "marshal_petition", "marshal_audience"):
            answers[f"{row['key']}:{row.get('answer')}"] += 1
    decrees_answered = sum(1 for a in ((meta.get("moments_trace") or {}).get("applications") or [])
                           if a.get("kind") == "answer" and a.get("answer") == "decree")
    mornings = trace.get("mornings") or []
    after = [int(m.get("after", 0) or 0) for m in moves if str(m.get("key") or "") in BUY_CAUSES]
    crossed = any(str(m.get("key") or "") in BUY_CAUSES and int(m.get("before", 0) or 0) >= 85
                  > int(m.get("after", 0) or 0) for m in moves)
    regrowth = sum(int(m.get("delta", 0) or 0) for m in moves
                   if str(m.get("key") or "") in REGROWTH_CAUSES and int(m.get("delta", 0) or 0) > 0)
    return {"status": meta.get("status", ""), "turns": len(mornings),
            "buys": dict(sorted(landed.items())), "paid": dict(sorted(paid.items())),
            "lowest_after_a_buy": min(after) if after else None,
            "a_buy_crossed_85": bool(crossed), "regrowth": int(regrowth),
            "stakes": sum(-int(m.get("delta", 0) or 0) for m in moves if m.get("key") in STAKE_CAUSES),
            "decrees_answered": int(decrees_answered),
            "answers": dict(sorted(answers.items())),
            "start": trace.get("start"), "min": trace.get("min"), "end": trace.get("end"),
            "residual": trace.get("residual"),
            "pushes": sum(landed.values())}


def cmd_record(args) -> int:
    out = Path(args.out).resolve() / "arms"
    shipped = Path(args.shipped).resolve() if args.shipped else None
    runs = {}
    for run_dir in sorted(p for p in out.iterdir() if p.is_dir() and p.name.startswith("BUY-")):
        row = _read_run(run_dir)
        name = run_dir.name[len("BUY-"):]
        if shipped is not None and (shipped / name / "meta.json").is_file():
            base = (json.loads((shipped / name / "meta.json").read_text(encoding="utf-8"))
                    .get("standing_trace") or {})
            row["shipped_end"], row["shipped_min"] = base.get("end"), base.get("min")
        runs[name] = row
    totals = Counter()
    for row in runs.values():
        totals.update(row["buys"])
    record = {
        "_what": ("AU-3a the buys arm: the nine commanded scripts played by a spender "
                  "(`--affair decree --objection word --petition buy`), each buy counted by "
                  "its cause from the standing trace; `shipped_end` the same arm's end on the "
                  "shipped measure (the default dials buy nothing)"),
        "dials": DIALS + ["--objection", "word"],
        "runs": runs,
        "totals": dict(sorted(totals.items())),
        "runs_with_a_push": sorted(n for n, r in runs.items() if r["pushes"] > 0),
    }
    Path(args.record).write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.record}: {len(runs)} runs, totals {dict(totals)}, "
          f"{len(record['runs_with_a_push'])} with a push")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--jobs", type=int, default=3)
    c = sub.add_parser("record")
    c.add_argument("--out", required=True)
    c.add_argument("--shipped", default="")
    c.add_argument("--record", default=str(ROOT / "tools" / "_standing_buys.json"))
    args = ap.parse_args()
    return cmd_run(args) if args.cmd == "run" else cmd_record(args)


if __name__ == "__main__":
    sys.exit(main())

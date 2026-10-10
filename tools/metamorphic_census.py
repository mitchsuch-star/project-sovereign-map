"""DD-0 S3 — the metamorphic census (October 10, 2026; PRE_DEPLOY_PLAN.md
§3.0 instrument 2; rules SYSTEMS_REFERENCE.md §101).

Generates the metamorphic variants of the golden corpus's order rows
(`backend/ai/parser_metamorphic.py`), parses each beside its original on a
fresh board per world, and prints the failures by family and by the parse
trace's last stage — so the worklist is attributed before anyone opens a
file.

    .venv/Scripts/python.exe tools/metamorphic_census.py                      # the table
    .venv/Scripts/python.exe tools/metamorphic_census.py --family negation    # one family
    .venv/Scripts/python.exe tools/metamorphic_census.py --show <variant id>  # one variant's trace
    .venv/Scripts/python.exe tools/metamorphic_census.py --list               # every failure, one line each
    .venv/Scripts/python.exe tools/metamorphic_census.py --write-ledger       # rewrite the known-failures ledger

The ledger `tests/data/metamorphic_known_failures.json` is the ratchet the
pytest harness (`tests/test_dd0_metamorphic_corpus.py`) holds: no failure
outside it may land, and its count may only fall. Rewrite it ONLY when a
slice has fixed rows (the count must fall) or added a family (recorded in
the landing record) — never to hide a regression.

Exit code 0 always — the census is a measurement; its pins are the harness's.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

LEDGER = ROOT / "tests" / "data" / "metamorphic_known_failures.json"


def _env():
    os.environ["LLM_MODE"] = "mock"
    os.environ["SOVEREIGN_SCENARIO"] = "none"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", action="append", help="limit to a family (repeatable)")
    ap.add_argument("--show", help="print one variant's parse trace")
    ap.add_argument("--list", action="store_true", help="every failure, one line each")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--write-ledger", action="store_true")
    args = ap.parse_args()
    _env()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from backend.ai import parse_trace, parser_eval, parser_metamorphic as pm

    rows = parser_eval.load_corpus()["entries"]
    outcomes = pm.run(rows, families=args.family, limit=args.limit)
    if args.show:
        hit = [o for o in outcomes if o.variant.id == args.show]
        if not hit:
            print("no such variant id:", args.show)
            return 0
        o = hit[0]
        print(f"{o.variant.id}  [{o.variant.family} / {o.variant.relation}]  {o.variant.note}")
        print("original:", repr(o.variant.original))
        print("verdict: ", o.verdict or "HELD")
        print(parse_trace.fmt(o.trace, o.variant.utterance))
        return 0

    s = pm.summarize(outcomes)
    print(f"cases {s['cases']}  failed {s['failed']}  "
          f"(order rows {len({o.variant.row_id for o in outcomes})})")
    print("by family:")
    for fam, c in s["by_family"].items():
        print(f"   {fam:18} {c['failed']:5} / {c['cases']}")
    print("by last stage:")
    for st, n in s["by_last_stage"].items():
        print(f"   {n:5}  {st}")
    failures = [o for o in outcomes if o.verdict]
    if args.list:
        for o in failures:
            print(f"   {o.variant.id}  {o.variant.utterance!r}  -- {o.verdict}  [{o.last_stage}]")
    if args.write_ledger:
        LEDGER.write_text(json.dumps({
            "_note": ("DD-0 S3 the metamorphic corpus — the known failures the ratchet "
                      "holds (tests/test_dd0_metamorphic_corpus.py): no failure outside "
                      "this list may land, and the count may only fall. Each row is "
                      "S4's worklist, attributed by the parse trace's last stage. "
                      "Rewrite only via tools/metamorphic_census.py --write-ledger."),
            "count": len(failures),
            "failures": [{"id": o.variant.id, "family": o.variant.family,
                          "relation": o.variant.relation, "utterance": o.variant.utterance,
                          "original": o.variant.original, "why": o.verdict,
                          "last_stage": o.last_stage}
                         for o in failures],
        }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("ledger written:", LEDGER, len(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

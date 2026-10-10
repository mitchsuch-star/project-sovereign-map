"""SF-CMD-1 "The unrehearsed line" — the held-out census runner (October 3,
2026; SCORE_FINISH_SPEC.md §3 Step 4).

Runs a BLIND file of player sentences (written without seeing the corpus,
tests or docs — `tools/playtest_scripts/unrehearsed_2026_10_03.json`: 150
orders with their intended reading, 150 questions with the answer they need)
one line each on a FRESH 1805 boot board through the real `POST /command`,
and classifies every reply with the ONE judge the HOLD arm uses
(`tools/_score_probes.py`: SHRUG_RX / BOARD_GATE_RX / ASKED_RX / REFUSED_RX /
ACTION_WORDS — never a second):

    .venv/Scripts/python.exe tools/unrehearsed_census.py --blind tools/playtest_scripts/unrehearsed_2026_10_03.json --out X.json [--llm mock|anthropic]
    .venv/Scripts/python.exe tools/unrehearsed_census.py --reclassify X.json      (the judge re-read over a stored run)

Order classes:
  as_meant          executed and the reply names the intended action
  asked             the game asked before acting (which marshal, which
                    province, an objection to answer) — read, not yet done
  board_refusal     refused by the BOARD with its reason (no gold, no actions,
                    out of range, already so, not ours …) naming the man or
                    the state order — read right, refused honestly
  honest_refusal    the game could not read the line and said so, spending
                    nothing — the parser's worklist
  shrug             the generic cannot-parse reply — the parser's worklist
  misread           executed, and not what was meant — the dangerous class
  refused_as_meant  the line was MEANT to be refused (a marshal who does not
                    exist, a province that is not there, the wrong desk) and
                    was
  executed_when_refusal_meant  meant to be refused and ran — the worst class
Question classes: answered / shrug.

Exit code 0 always — the census is a measurement; its pins live in
tests/test_sf_cmd1_the_unrehearsed_census.py.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def _env(llm: str):
    os.environ.setdefault("INK_IRON_SAVE_DIR", tempfile.mkdtemp(prefix="unrehearsed_saves_"))
    os.environ["LLM_MODE"] = llm
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
        os.environ.pop(key, None)


_EXECUTED_RX = re.compile(
    r"moves? (to|from)|begins march|scouts |fortifies|recruits|Construction|MUSTER|⚔|takes? \d|lays? down|"
    r"has been|now holds|departs|Turn \d+ ended", re.I)


def classify_order(intended: dict, reply: dict) -> str:
    import _score_probes as judge
    msg = str(reply.get("message", "") or "")
    action = str(intended.get("action", "") or "")
    who = str(intended.get("marshal", "") or "")
    if action == "refuse":
        if (judge.REFUSED_RX.search(msg) or judge.BOARD_GATE_RX.search(msg)
                or judge.SHRUG_RX.search(msg) or judge.ASKED_RX.search(msg)):
            return "refused_as_meant"
        return "executed_when_refusal_meant"
    if judge.SHRUG_RX.search(msg):
        return "shrug"
    if judge.ASKED_RX.search(msg) and not _EXECUTED_RX.search(msg):
        return "asked"
    names_who = (who in ("state", "", "none")
                 or any(w.lower() in msg.lower() for w in who.replace(",", " ").split()))
    if judge.BOARD_GATE_RX.search(msg) and names_who:
        return "board_refusal"
    if judge.REFUSED_RX.search(msg):
        return "honest_refusal"
    if re.search(judge.ACTION_WORDS.get(action, action), msg, re.I):
        return "as_meant"
    return "misread" if reply.get("success") else "honest_refusal"


def classify_question(reply: dict) -> str:
    import _score_probes as judge
    msg = str(reply.get("message", "") or "")
    return "shrug" if (judge.SHRUG_RX.search(msg) or not msg.strip()) else "answered"


def totals(rows: list) -> dict:
    out: dict = {}
    for r in rows:
        out.setdefault(r["kind"], Counter())[r["class"]] += 1
    return {k: dict(v) for k, v in out.items()}


def reclassify(record: dict) -> dict:
    for r in record["rows"]:
        if r["kind"] == "order":
            r["class"] = classify_order(r.get("intended") or {}, r)
        else:
            r["class"] = classify_question(r)
    record["totals"] = totals(record["rows"])
    record["dangerous"] = [r["line"] for r in record["rows"]
                           if r["class"] in ("misread", "executed_when_refusal_meant")]
    return record


def run(blind: dict, llm: str, limit: int | None, trace: bool = False) -> dict:
    _env(llm)
    from fastapi.testclient import TestClient
    with contextlib.redirect_stdout(io.StringIO()):
        import backend.main as M
        client = TestClient(M.app)
    rows = []

    def fresh():
        with contextlib.redirect_stdout(io.StringIO()):
            M._reset_world_state()
            if llm == "mock":
                from backend.commands.parser import CommandParser
                M.parser = CommandParser(use_real_llm=False)

    def post(line):
        with contextlib.redirect_stdout(io.StringIO()):
            r = client.post("/command", json={"command": line, "trace": bool(trace)})
        return r.json()

    for o in blind.get("orders", [])[:limit]:
        fresh()
        t0 = time.time()
        reply = post(o["line"])
        row = {"kind": "order", "line": o["line"], "intended": o.get("intended"),
               "class": classify_order(o.get("intended") or {}, reply),
               "success": reply.get("success"), "parse_mode": reply.get("parse_mode"),
               "parse_confidence": reply.get("parse_confidence"),
               "message": str(reply.get("message", "") or "")[:300],
               "secs": round(time.time() - t0, 2)}
        # DD-0 S3: the parse trace rides each row (`--trace`), so a misread
        # or a shrug names the stage that read it wrong without a session.
        if trace and reply.get("parse_trace"):
            row["parse_trace"] = reply["parse_trace"]
        rows.append(row)
    for q in blind.get("questions", [])[:limit]:
        fresh()
        reply = post(q["line"])
        rows.append({"kind": "question", "line": q["line"], "intended": q.get("intended"),
                     "class": classify_question(reply),
                     "success": reply.get("success"), "parse_mode": reply.get("parse_mode"),
                     "parse_confidence": reply.get("parse_confidence"),
                     "message": str(reply.get("message", "") or "")[:300]})
    live = sum(1 for r in rows if r.get("parse_mode") not in (None, "mock"))
    record = {"blind": blind.get("name"), "llm": llm, "rows": rows, "live_parses": live}
    return reclassify(record)


def print_record(record: dict) -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(record["llm"], json.dumps(record["totals"], ensure_ascii=False), "live parses:", record["live_parses"])
    for cls in ("misread", "executed_when_refusal_meant", "shrug", "honest_refusal"):
        rows = [r for r in record["rows"] if r["class"] == cls]
        if rows:
            print(f"== {cls} ({len(rows)})")
            for r in rows:
                print(f"   [{r['kind']}] {r.get('parse_confidence')} {r['line'][:66]!r} -> {r['message'][:90]!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind")
    ap.add_argument("--out")
    ap.add_argument("--llm", default="mock", choices=("mock", "anthropic"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--reclassify", help="a stored run to re-read with the current judge (rewritten in place)")
    ap.add_argument("--trace", action="store_true",
                    help="DD-0 S3: store each order's parse trace on its row")
    args = ap.parse_args()
    if args.reclassify:
        path = Path(args.reclassify)
        record = reclassify(json.loads(path.read_text(encoding="utf-8")))
        path.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
        print_record(record)
        return 0
    blind = json.loads(Path(args.blind).read_text(encoding="utf-8"))
    record = run(blind, args.llm, args.limit, trace=args.trace)
    Path(args.out).write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    print_record(record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

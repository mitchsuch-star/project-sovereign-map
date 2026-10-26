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

DD-0 S4 part 4 (October 11, 2026) — THE RE-BASED INSTRUMENT (the user's
ruling, PRE_DEPLOY_PLAN.md §3.0): the done-when reads READ RIGHT BY HAND —
as_meant + asked + board_refusal + refused_as_meant — against ≥ 85 %, with
0 EXECUTED-OTHER-THAN-MEANT by hand; `as_meant` is printed beside it, never
in its place. The judge's `misread` / `executed_when_refusal_meant` are the
PROXIES: each must be read against its trace (the memos' method), and that
reading is a committed file beside the records:

    .venv/Scripts/python.exe tools/unrehearsed_census.py --reclassify X.json --by-hand X_by_hand.json

The hand file: {"rows": [{"line", "arm": keyless|keyed|both, "verdict",
"reply_starts", "note"}]} — verdicts `executed` (something other than what
was meant RAN — the dangerous class), `staged` (a chooser or dialogue opened
against what was meant; nothing ran), `disclosed` (ran, and SAID what it
changed), `asked`, `honest_refusal`, `wrong_desk` (the wrong desk answered,
nothing ran). `reply_starts` pins the reply the verdict was read against: a
re-read whose reply no longer starts so makes the verdict STALE and the row
unread, and an unread proxy row leaves `executed_other_than_meant` None —
the figure is never printed as 0 by default. The record gains `read_right`,
`executed_other_than_meant`, `by_hand` (line → verdict) and `by_hand_unread`.

Exit code 0 always — the census is a measurement; its pins live in
tests/test_sf_cmd1_the_unrehearsed_census.py and the blind-set pins.
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
    # DD-B's third measure (October 26, 2026): a repeat of an order already
    # standing is the board declining, free, and saying so.
    if judge.ALREADY_HELD_RX.search(msg) and names_who:
        return "board_refusal"
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


READ_RIGHT_CLASSES = ("as_meant", "asked", "board_refusal", "refused_as_meant")
PROXY_CLASSES = ("misread", "executed_when_refusal_meant")
# The rows a hand may read: the judge's two proxies, and an `honest_refusal`
# the judge could not place (the border law's "Cannot enter X — controlled
# by Hesse" is the BOARD's own refusal, read by a person as such).
HAND_READ_CLASSES = PROXY_CLASSES + ("honest_refusal",)
HAND_VERDICTS = ("executed", "staged", "disclosed", "asked", "honest_refusal", "wrong_desk", "board_refusal")
# The hand verdicts that are READ RIGHT (the ruling's four: the game asked
# before acting, or the board refused with its reason).
HAND_READ_RIGHT = ("asked", "board_refusal")


def read_right_of(record: dict) -> int:
    """The re-based done-when's numerator: the lines the game read RIGHT —
    executed as meant, asked before acting, refused by the board with its
    reason, or refused when a refusal was meant."""
    t = (record.get("totals") or {}).get("order") or {}
    return sum(int(t.get(k, 0)) for k in READ_RIGHT_CLASSES)


def load_by_hand(path) -> dict:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    for row in d.get("rows", []):
        if row.get("verdict") not in HAND_VERDICTS:
            raise ValueError(f"by-hand verdict {row.get('verdict')!r} for {row.get('line')!r} "
                             f"is not one of {HAND_VERDICTS}")
    return d


def apply_by_hand(record: dict, by_hand: dict | None) -> dict:
    """Read the judge's proxy rows by hand: each dangerous row takes the
    hand verdict filed for its line and arm, provided the reply still
    starts as the verdict was read against; otherwise it is unread."""
    arm = "keyed" if record.get("llm") == "anthropic" else "keyless"
    hand_rows = [h for h in (by_hand or {}).get("rows", [])
                 if h.get("arm", "both") in ("both", arm)]
    verdicts: dict = {}
    unread: list = []
    for r in record["rows"]:
        if r["kind"] != "order" or r["class"] not in HAND_READ_CLASSES:
            continue
        match = next((h for h in hand_rows if h["line"] == r["line"]), None)
        if match is None:
            # an honest refusal is the parser's unless a hand reads it as the board's
            if r["class"] in PROXY_CLASSES:
                unread.append(r["line"])
            continue
        starts = str(match.get("reply_starts") or "")
        if starts and not str(r.get("message") or "").startswith(starts):
            if r["class"] in PROXY_CLASSES:
                unread.append(r["line"])
            continue
        verdicts[r["line"]] = match["verdict"]
    record["read_right"] = read_right_of(record)
    record["by_hand"] = verdicts
    record["by_hand_unread"] = unread
    # the ruling's figure: the judge's four classes, plus every row a hand
    # read as asked or as the board's own refusal — and a line MEANT to be
    # refused that a hand read as refused (by the parser or the board) is
    # refused as meant.
    meant_refuse = {r["line"] for r in record["rows"]
                    if r["kind"] == "order" and str((r.get("intended") or {}).get("action") or "") == "refuse"}
    record["read_right_by_hand"] = record["read_right"] + sum(
        1 for line, v in verdicts.items()
        if v in HAND_READ_RIGHT or (v == "honest_refusal" and line in meant_refuse))
    record["executed_other_than_meant"] = (
        None if unread else sum(1 for v in verdicts.values() if v == "executed"))
    return record


def reclassify(record: dict, by_hand: dict | None = None) -> dict:
    for r in record["rows"]:
        if r["kind"] == "order":
            r["class"] = classify_order(r.get("intended") or {}, r)
        else:
            r["class"] = classify_question(r)
    record["totals"] = totals(record["rows"])
    record["dangerous"] = [r["line"] for r in record["rows"]
                           if r["class"] in PROXY_CLASSES]
    return apply_by_hand(record, by_hand)


def run(blind: dict, llm: str, limit: int | None, trace: bool = False,
        by_hand: dict | None = None) -> dict:
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
    return reclassify(record, by_hand)


def print_record(record: dict) -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(record["llm"], json.dumps(record["totals"], ensure_ascii=False), "live parses:", record["live_parses"])
    # DD-0 S4 part 4: the re-based instrument's two figures, `as_meant` beside.
    orders = sum((record["totals"].get("order") or {}).values())
    if orders:
        t = record["totals"]["order"]
        rr = record.get("read_right", read_right_of(record))
        rrh = record.get("read_right_by_hand", rr)
        eotm = record.get("executed_other_than_meant")
        unread = record.get("by_hand_unread") or []
        proxies = {k: int(t.get(k, 0)) for k in PROXY_CLASSES}
        print(f"read right BY HAND {rrh} / {orders} ({100.0 * rrh / orders:.1f} %) · the judge's four classes {rr} · "
              f"as meant {int(t.get('as_meant', 0))} / {orders} ({100.0 * int(t.get('as_meant', 0)) / orders:.1f} %)")
        print(f"executed other than meant (by hand): "
              f"{'UNREAD' if eotm is None else eotm} · the judge's proxies {proxies}"
              + (f" · unread by hand: {len(unread)}" if unread else ""))
        for line in unread:
            print(f"   unread: {line[:80]!r}")
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
    ap.add_argument("--by-hand", help="DD-0 S4 part 4: the hand reading of the judge's proxy rows "
                                      "(a committed JSON beside the record)")
    args = ap.parse_args()
    by_hand = load_by_hand(args.by_hand) if args.by_hand else None
    if args.reclassify:
        path = Path(args.reclassify)
        record = reclassify(json.loads(path.read_text(encoding="utf-8")), by_hand)
        path.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
        print_record(record)
        return 0
    blind = json.loads(Path(args.blind).read_text(encoding="utf-8"))
    record = run(blind, args.llm, args.limit, trace=args.trace, by_hand=by_hand)
    Path(args.out).write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    print_record(record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""T0-I (November 7, 2026) — the benchmark's own arms, measured.

Reads the slice's driver runs (Mode A, PYTHONHASHSEED=0, the mock parser)
and writes `tools/_t0i_benchmark_arms.json`, the committed record
`tests/test_t0i_the_benchmarks_arms.py` pins. Three blocks:

  shut   — GR-66: the re-staged sr5b_shut_out arm on the three benchmark
           seeds; per seed, the turn Britain sues (None where she cannot:
           on historical Spain destroys Paget outright at T7, no second
           corps lands inside the arm, and a court that has never fought
           France cannot sue her — the GR-18 ruling), the storm turn, and
           that NO attack_target clarification rewrote an order.
  sea    — the SF6-X2 re-stage: the yard raised, the commission taken,
           the landing quoted with its levers and RESOLVED at sea (an
           interception is an outcome, not a refusal), no SCRIPT
           PRECONDITION, and the two diversion quotes at odds =
           readiness − 25 (naval C1's own arithmetic).
  drama  — GR-2/GR-3: the provoke arm's counters — objections pressed,
           V2b defiances on the fixed line, the chest spent, the refusal
           rate against the open-loop control's 29-40%, and the trust
           cost (first/last MARSHALS row readings for the pressed men).

Usage:
  .venv/Scripts/python.exe tools/_t0i_benchmark_arms.py \
      --shut-h RUN --shut-a RUN --shut-m RUN --sea RUN --drama RUN
RUN names are directories under tools/playtest_runs/. Pure reads.
"""
from __future__ import annotations

import argparse
import io
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNS = ROOT / "tools" / "playtest_runs"
OUT = ROOT / "tools" / "_t0i_benchmark_arms.json"


def _md(name: str) -> str:
    return io.open(RUNS / name / "digest.md", encoding="utf-8").read()


def _meta(name: str) -> dict:
    return json.load(open(RUNS / name / "meta.json", encoding="utf-8"))


def _turn_of(md: str, needle: str):
    turn = None
    for line in md.splitlines():
        if line.startswith("## Turn"):
            turn = int(re.search(r"## Turn (\d+)", line).group(1))
        if needle in line:
            return turn
    return None


def read_shut(name: str) -> dict:
    md = _md(name)
    return {
        "britain_sues_turn": _turn_of(md, "Britain, armistice_losing"),
        "storm_turn": _turn_of(md, "Soult, attack Lisbon` → ✓"),
        "attack_target_rewrites": md.count("attack_target"),
        "completed": "finished: **completed**" in md,
    }


def read_sea(name: str) -> dict:
    md = _md(name)
    meta = _meta(name)
    quotes = [(int(o), int(r)) for o, r in re.findall(
        r"(\d+) times in 100 at her readiness \((\d+)\)", md)]
    return {
        "yard_turn": _turn_of(md, "Construction started: Naval Yard"),
        "commission_turn": _turn_of(md, "commission` → ✓")
        or _turn_of(md, "accepts his commission"),
        "landing_quoted_turn": _turn_of(md, "The expedition is drawn up"),
        # Oudinot's own throw only — Britain's Paget "puts 5,000 ashore"
        # every run and must not fake a resolution.
        "landing_resolved": bool(re.search(
            r"INTERCEPTED AT SEA: the British squadrons catch"
            r"|LANDING: Oudinot", md)),
        "diversion_quotes": quotes,
        "odds_are_readiness_minus_25": bool(quotes) and all(
            o == r - 25 for o, r in quotes),
        "resolved_throws": len(re.findall(
            "diversion draws|shattered in action|caught coming home", md)),
        "precondition_failed": bool(meta.get("script_preconditions_failed")),
        "completed": "finished: **completed**" in md,
    }


def read_drama(name: str) -> dict:
    md = _md(name)
    meta = _meta(name)
    counters = meta.get("counters") or {}
    rows = re.findall(r"^- MARSHALS (.+)$", md, re.M)

    def trust_of(row: str, who: str):
        m = re.search(re.escape(who) + r" trust (\d+)", row)
        return int(m.group(1)) if m else None

    pressed = ("Ney", "Lannes", "Murat", "Davout", "Bernadotte")
    spent = [int(s.replace(",", ""))
             for s in re.findall(r"SPENT ([0-9,]+)g", md)]
    cmds = int(counters.get("commands", 0) or 0)
    refused = int(counters.get("cmd_refused", 0) or 0)
    return {
        "objection_popups": md.count("POPUP objection"),
        "insists": md.count("→ insist"),
        # A V2b defiance fires the marshal_defied_order notification
        # (meta_executor's defiance block) — counted off the jsonl's dtype,
        # never prose ("defiance" also rides Portugal's agenda rail).
        "defiances": sum(
            1 for line in io.open(RUNS / name / "digest.jsonl",
                                  encoding="utf-8")
            if '"marshal_defied_order"' in line
            and '"kind": "rail"' in line),
        # The redemption arc (a pressed marshal at rock-bottom trust) —
        # under --redemption dismiss the Emperor refuses it and the man
        # stays in the line.
        "redemptions": md.count("POPUP redemption"),
        "gold_spent": sum(spent),
        "commands": cmds,
        "cmd_refused": refused,
        "refusal_rate_pct": round(100 * refused / cmds) if cmds else None,
        "ap_spent": counters.get("ap_spent"),
        "trust_first_turn": {w: trust_of(rows[0], w) for w in pressed} if rows else {},
        "trust_last_turn": {w: trust_of(rows[-1], w) for w in pressed} if rows else {},
        "completed": "finished: **completed**" in md,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shut-h", required=True)
    ap.add_argument("--shut-a", required=True)
    ap.add_argument("--shut-m", required=True)
    ap.add_argument("--sea", required=True)
    ap.add_argument("--drama", required=True)
    ap.add_argument("--rolls", default="",
                    help="the instrumented (chance, roll) table for the "
                         "drama line (a pass-through logger around "
                         "defiance.calculate_defiance_chance; the roll "
                         "peeked via getstate/setstate, never consumed)")
    args = ap.parse_args()
    record = {
        "_note": ("T0-I (November 7, 2026) — the benchmark's own arms, "
                  "measured on the re-staged scripts; written by "
                  "tools/_t0i_benchmark_arms.py; pinned by "
                  "tests/test_t0i_the_benchmarks_arms.py"),
        "shut": {
            "historical": read_shut(args.shut_h),
            "austerlitz": read_shut(args.shut_a),
            "marengo": read_shut(args.shut_m),
        },
        "sea": read_sea(args.sea),
        "drama": read_drama(args.drama),
    }
    if args.rolls:
        record["drama"]["defiance_pricing"] = json.load(
            open(args.rolls, encoding="utf-8"))
    OUT.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    print("written", OUT)
    print(json.dumps(record, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()

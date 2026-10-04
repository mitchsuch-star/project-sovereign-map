"""SF-NAV-1 "The strangulation, played" (Score Finish Step 6, October 4, 2026) —
the read-only probe over a driver run of `tools/playtest_scripts/sf_nav1_strangulation.json`.

Reads the saves the run wrote (`--save-at 1,2,…,N`) and its digest, and prints
one row per turn — the Continental System's closure against Britain (the
`congress._shut_out_reading` the Congress reads), whether SHUT OUT holds, the
British corps on the Continent (`congress.corps_on_the_continent`), Spain's
state with Britain, Britain's war exhaustion and the System's tier — then the
summary the record needs: the peak closure and its tier, every turn and the
longest run of turns the reading held, the turn Spain's war with Britain ended
(the exhausted-pair exit, `settlement_third_party.PAIR_EXIT_*`), the last turn a
British corps stood on the Continent, and Britain's envoys (when Britain sued,
at what war exhaustion and System tier — why Britain sues).

    PYTHONPATH=. .venv/Scripts/python.exe tools/sf_nav1_strangulation_probe.py \
        tools/playtest_runs/sf-nav1-historical [--json]

Read-only: each save is loaded into a fresh world; nothing is written.
"""
from __future__ import annotations

import contextlib
import glob
import io
import json
import os
import re
import sys

from backend.game_logic import naval
from backend.game_logic.congress import _shut_out_reading, corps_on_the_continent
from backend.models.world_state import WorldState

COURT = "Britain"
_ENVOY = re.compile(r"(?:POPUP diplomatic_dialogue:?|MAILBOX #\d+) Britain[ ,:].*?"
                    r"(armistice\w*|peace|settlement\w*|incoming_settlement_offer)", re.I)


def _turn_of(path: str) -> int:
    return int(re.search(r"_t(\d+)\.json$", path).group(1))


def _load(path: str) -> WorldState:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    state = data.get("world_state") or data.get("world") or data
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_dict(state)


def _envoys(run_dir: str):
    """Britain's envoys off the digest, by the turn header they ride under."""
    md = os.path.join(run_dir, "digest.md")
    out = []
    turn = 0
    if not os.path.exists(md):
        return out
    with open(md, encoding="utf-8") as fh:
        for line in fh:
            head = re.match(r"^## Turn (\d+)", line)
            if head:
                turn = int(head.group(1))
                continue
            m = _ENVOY.search(line)
            if m:
                # one envoy rides two lines (the mailbox row and the popup
                # that answers it) — read both as the same ask
                kind = m.group(1).lower()
                if kind.startswith("armistice"):
                    kind = "armistice"
                elif kind.startswith(("settlement", "incoming_settlement")):
                    kind = "settlement offer"
                out.append((turn, kind))
    seen, uniq = set(), []
    for row in out:
        if row not in seen:
            seen.add(row)
            uniq.append(row)
    return uniq


def probe(run_dir: str) -> dict:
    rows = []
    paths = sorted(glob.glob(os.path.join(run_dir, "saves", "*_t*.json")), key=_turn_of)
    for path in paths:
        world = _load(path)
        reading = _shut_out_reading(world, COURT)
        closure = naval.closure_against(world, COURT)
        rows.append({
            "turn": int(world.current_turn),
            "closed": int(reading.get("closed") or 0),
            "needed": int(reading.get("needed") or 0),
            "tier": int(naval.cs_closure_tier(closure)),
            "holds": bool(reading.get("holds")),
            "corps_abroad": list(corps_on_the_continent(world, COURT)),
            "spain_at_war": bool(world.is_at_war("Spain", COURT)),
            "france_at_war": bool(world.is_at_war(world.player_nation, COURT)),
            "britain_we": int((getattr(world, "war_exhaustion", {}) or {}).get(COURT, 0) or 0),
            "provinces": len(world.get_nation_regions(world.player_nation) or []),
            "titled": None,
        })
    holds = [r["turn"] for r in rows if r["holds"]]
    longest, run, prev = 0, 0, None
    for t in holds:
        run = run + 1 if prev is not None and t == prev + 1 else 1
        longest = max(longest, run)
        prev = t
    spain_exit = next((r["turn"] for i, r in enumerate(rows)
                       if i and rows[i - 1]["spain_at_war"] and not r["spain_at_war"]), None)
    corps_turns = [r["turn"] for r in rows if r["corps_abroad"]]
    by_turn = {r["turn"]: r for r in rows}
    envoys = [{"turn": t, "kind": k,
               "britain_we": (by_turn.get(t) or {}).get("britain_we"),
               "tier": (by_turn.get(t) or {}).get("tier"),
               "closed": (by_turn.get(t) or {}).get("closed")} for t, k in _envoys(run_dir)]
    return {
        "run": os.path.basename(run_dir.rstrip("/\\")),
        "rows": rows,
        "summary": {
            "peak_closed": max((r["closed"] for r in rows), default=0),
            "peak_tier": max((r["tier"] for r in rows), default=0),
            "holds_turns": holds,
            "longest_hold": longest,
            "spain_exit_turn": spain_exit,
            "last_corps_turn": max(corps_turns) if corps_turns else None,
            "britain_envoys": envoys,
        },
    }


def main(argv):
    as_json = "--json" in argv
    for run_dir in [a for a in argv if not a.startswith("--")]:
        result = probe(run_dir)
        if as_json:
            print(json.dumps(result, ensure_ascii=False))
            continue
        print(f"== {result['run']}")
        for r in result["rows"]:
            print(f"  t{r['turn']:>2}  {r['closed']:>2}/{r['needed']} tier {r['tier']}"
                  f"  {'SHUT OUT' if r['holds'] else '        '}  corps {r['corps_abroad'] or '-'}"
                  f"  Spain {'war' if r['spain_at_war'] else 'peace'}  WE {r['britain_we']}")
        s = result["summary"]
        print(f"  peak {s['peak_closed']} (tier {s['peak_tier']}) · held on {s['holds_turns']} "
              f"(longest {s['longest_hold']}) · Spain's exit t{s['spain_exit_turn']} · "
              f"last British corps t{s['last_corps_turn']}")
        for e in s["britain_envoys"]:
            print(f"  Britain {e['kind']} on t{e['turn']} at WE {e['britain_we']}, "
                  f"tier {e['tier']} ({e['closed']} ports)")


if __name__ == "__main__":
    main(sys.argv[1:])

"""SF-DC-1 (Score Finish Step 7 slice 6, October 4, 2026) — the volte door,
read turn by turn off a driver run's saves.

The research instrument behind §6 row 20 (`docs/SCORE_FINISH_SPEC.md`): for
every save a run wrote (`tools/playtest_driver.py --save-at 1,2,…,N`) it prints
the court's state with France, the relation, its war exhaustion, the homeland
provinces in foreign hands (and their holders' top overlords), any emergent
revanche in its deck (and its author), any punitive memory, and EVERY failing
clause of `emergent_designs.volte_face_failing_clauses` (exhaustive).

    PYTHONPATH=. .venv/Scripts/python.exe tools/_volte_door_probe.py <run_dir> [court]

Levers the run set must be set here too, or the clauses are read on a
different rule than the game played: `PROBE_LEVERS="module:NAME=0;module:NAME=1"`.
Read-only: each save is loaded into a fresh world; nothing is written.
"""
from __future__ import annotations

import contextlib
import glob
import importlib
import io
import json
import os
import re
import sys

from backend.game_logic import emergent_designs as ed
from backend.game_logic.settlement_reactions import get_settlement_memories
from backend.models.world_state import WorldState


def _load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    state = data.get("world_state") or data.get("world") or data
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_dict(state)


def main():
    for spec in filter(None, os.environ.get("PROBE_LEVERS", "").split(";")):
        mod, rest = spec.split(":")
        name, val = rest.split("=")
        setattr(importlib.import_module(mod), name, val == "1")
    run_dir = sys.argv[1]
    court = sys.argv[2] if len(sys.argv) > 2 else "Austria"
    saves = sorted(glob.glob(os.path.join(run_dir, "saves", "*_t*.json")),
                   key=lambda p: int(re.search(r"_t(\d+)\.json$", p).group(1)))
    for path in saves:
        loop = int(re.search(r"_t(\d+)\.json$", path).group(1))
        w = _load(path)
        state = w.get_diplomatic_state(court, "France")
        rel = int(w.nation_relations.get(w._make_diplo_key(court, "France"), 0) or 0)
        holders = []
        for r in ed._lost_homeland(w, court):
            c = getattr(w.regions.get(r), "controller", None)
            top = w._top_overlord(c) or c
            holders.append(f"{r}:{c}" + (f"->{top}" if top != c else ""))
        revanche = [(e.get("id"), e.get("author"), e.get("promoted_turn"))
                    for e in (w.agendas or {}).get(court) or []
                    if isinstance(e, dict) and e.get("emergent")]
        punitive = [(m.get("actor"), m.get("turn")) for m in get_settlement_memories(
            w, subject=court, memory_type=ed.PUNITIVE_MEMORY_TYPE)]
        fails = ed.volte_face_failing_clauses(w, court, "France", exhaustive=True)
        we = int((getattr(w, "war_exhaustion", {}) or {}).get(court, 0) or 0)
        print(f"loop {loop:2d} t{w.current_turn:2d} {state:12s} rel {rel:4d} WE {we:3d} "
              f"lost={holders} revanche={revanche} punitive={punitive} fails={fails}")


if __name__ == "__main__":
    main()

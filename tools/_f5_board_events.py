"""F5 — what authors the new ambient series' falls.

    .venv/Scripts/python.exe tools/_f5_board_events.py [--turns 40] [--cap 1] [--literal-check 1]

Runs the 40-turn ambient sim exactly as the series runner does (the same
scenario, seed and per-turn re-seed) and prints, per turn, the threat level
and every vassal / elimination / formation / design event the turn logged,
so a step in the alarm series can be named by the event that authored it.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["LLM_MODE"] = "mock"
os.environ["SOVEREIGN_SEED"] = "historical"
for _k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
    os.environ.pop(_k, None)

SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
WATCH = {"vassal_broke_free", "vassal_rebellion", "vassal_defection", "nation_eliminated",
         "design_promoted", "vassal_created", "vassal_transfer", "region_captured",
         "coalition_formed", "coalition_dissolved", "diplomatic_treaty_signed",
         "war_declared", "elimination"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--cap", type=int, default=1)
    ap.add_argument("--literal-check", dest="literal_check", type=int, default=1)
    args = ap.parse_args()
    from backend.ai import enemy_ai as EA
    EA.ONE_WALK_IN_PER_CORPS_PER_TURN = bool(args.cap)
    EA.THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK = bool(args.literal_check)
    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.world_state import WorldState

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO))
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
        game_state = {"world": world, "executor": executor}
    seen = 0
    prev = int(world.threat_level)
    print(f"turn 1 threat {prev}")
    for turn in range(args.turns):
        random.seed(10_000 + turn)
        with contextlib.redirect_stdout(io.StringIO()):
            tm.end_turn(game_state)
        cur = int(world.threat_level)
        new = world.event_log[seen:]
        seen = len(world.event_log)
        interesting = [e for e in new if e.get("type") in WATCH and
                       (e.get("type") != "region_captured" or e.get("captured_from") in ("France", "Bavaria")
                        or e.get("nation") == "Bavaria")]
        print(f"turn {int(world.current_turn)} threat {cur} (step {cur - prev}) "
              f"vassals={ {k: int(v.get('loyalty', 0)) for k, v in world.vassals.items() if v.get('lord') == 'France'} if hasattr(world, 'vassals') else '?'}")
        for e in interesting:
            keys = {k: e.get(k) for k in ("type", "nation", "vassal", "lord", "region", "captured_from",
                                           "marshal", "exit", "reason", "design", "target") if e.get(k) is not None}
            print("    ", keys)
        prev = cur
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

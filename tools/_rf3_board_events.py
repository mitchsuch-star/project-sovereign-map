"""SR-5r RF-3 — what authors the re-recorded ambient series' falls.

    .venv/Scripts/python.exe tools/_rf3_board_events.py [--turns 40] [--ai-enacts 1] [--cap 1]

Runs the 40-turn ambient sim exactly as the series runner does (the same
scenario, seed and per-turn re-seed) and prints, per turn, the threat level
and every vassal / elimination / design / law event the turn logged, so a step
in the alarm series can be named by the event that authored it. Events are
captured at `WorldState.log_event` itself (never by slicing `event_log`, whose
rolling cap evicts rows — the IQ-B trap). `--cap` sets the WO-9 courting cap
(the series runner ships it on).
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
         "design_promoted", "vassal_created", "vassal_transfer", "coalition_formed",
         "coalition_dissolved", "law_enacted", "law_lapsed", "law_repealed",
         "elimination"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--ai-enacts", dest="ai_enacts", type=int, default=1)
    ap.add_argument("--cap", type=int, default=1)
    args = ap.parse_args()
    from backend.game_logic import reforms as R
    from backend.game_logic import vassal as V
    R.THE_AI_ENACTS = bool(args.ai_enacts)
    V.COURTING_TARGET_CAP_ACTIVE = bool(args.cap)
    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.world_state import WorldState

    captured = []
    original = WorldState.log_event

    def _log(self, event):
        original(self, event)
        captured.append(dict(event))
    WorldState.log_event = _log

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO))
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
        game_state = {"world": world, "executor": executor}
    prev = int(world.threat_level)
    print(f"turn 1 threat {prev}")
    for turn in range(args.turns):
        random.seed(10_000 + turn)
        start = len(captured)
        with contextlib.redirect_stdout(io.StringIO()):
            tm.end_turn(game_state)
        cur = int(world.threat_level)
        france_vassals = {k: int(v.get("loyalty", 0)) for k, v in world.vassals.items()
                          if v.get("lord") == "France"}
        print(f"index {turn} turn {int(world.current_turn)} threat {cur} (step {cur - prev}) "
              f"vassals={france_vassals}")
        for e in captured[start:]:
            if e.get("type") not in WATCH:
                continue
            keys = {k: e.get(k) for k in ("type", "nation", "vassal", "lord", "exit",
                                           "reason", "design", "law", "target", "turn")
                    if e.get(k) is not None}
            print("    ", keys)
        prev = cur
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

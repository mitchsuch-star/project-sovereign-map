"""AU-3a the Mode C walk's crafted saves (`docs/AUTHORITY_CURRENCY_SPEC.md`
§5.3, §5.5, the landing record §6.5), the shape of `tools/re5_stage_saves.py`.

    .venv/Scripts/python.exe tools/au3a_stage_saves.py --chapter b --out <saves dir>/au3a_decree.json
    .venv/Scripts/python.exe tools/au3a_stage_saves.py --chapter d --out <saves dir>/au3a_te_deum.json

Chapter B (the Decree): the Remounts offer (an Edict) standing on the desk at
turn 7 with the Emperor's authority at 90 (the letter's third answer reads
"auth 90 -> 87 . 1 action . 8 turns"): the edicts pins' own Remounts board
(`tests/test_affairs_edicts.py::_remounts_board` — every corps home, the
chest at 5,000, the fleet under the Marine's bar, the dated moments passed,
the cavalry depots at 59 %), the look-ahead held at 0 so the production
`moments.tick` delivers the offer on the pulse's first morning (turn 7), the
letter made the current dialogue, the world saved by the save manager.

Chapter D (the Te Deum): France's pair with Austria stands in ARMISTICE on its
last turn (`armistice_turns` = ARMISTICE_DURATION - 1), the relation -20 (at or
over `ARMISTICE_AUTO_PEACE_RELATION`, so the truce ends in PEACE), the stored
war score +30 for France (the truce keeps the ledger; Te Deum needs +25), the
authority at 88 (under the ceiling 95). The walk's one end turn runs
`_process_armistice_expiration` -> `cleanup_war_end` -> `standing.te_deum_on_peace`
(+4, "the Te Deum for the peace with Austria"). The dated moments are passed so
no letter stands on the desk.

Each stager re-reads its save and plays the copy: chapter B checks the letter's
answers carry `decree_ai_proposal`; chapter D plays ONE real end turn
(`TurnManager.end_turn`) and checks the `te_deum` move landed — printed, never
written. A failed self-check exits 1.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("LLM_MODE", "mock")
for _k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
    os.environ.pop(_k, None)

REMOUNTS = "the_remounts#1"
DECREE_AUTHORITY = 90
TE_DEUM_AUTHORITY = 88


def test_module(name: str):
    """A test module imported by path for its STAGING helpers (`tests/` is not
    a package); its fixtures are never run here (the capture tool's idiom)."""
    path = ROOT / "tests" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_au3a_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stage_decree(out: Path) -> dict:
    A = test_module("test_affairs_engine")
    E = test_module("test_affairs_edicts")
    from backend.game_logic import affairs as AF
    from backend.game_logic import moments as MO
    from backend.models.world_state import WorldState
    from backend.save_manager import load_game, save_game

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(A.SCENARIO))
    E._remounts_board(world)
    world.authority_tracker.authority = int(DECREE_AUTHORITY)
    world.__dict__.pop("_affairs_memo", None)
    AF.LOOK_AHEAD = 0
    delivered = A._run(world, range(1, 8))
    if REMOUNTS not in delivered.get(7, []):
        raise SystemExit(f"the Remounts did not land on turn 7: {delivered}")
    letter = A._letter(world, REMOUNTS)
    if letter is None:
        raise SystemExit("the Remounts letter is not in the dialogue manager")
    A._make_current(world, letter)
    out.parent.mkdir(parents=True, exist_ok=True)
    result = save_game(world, "AU-3a - the Remounts standing, authority 90", filepath=out)
    if not result.get("success"):
        raise SystemExit(f"save failed: {result}")
    with contextlib.redirect_stdout(io.StringIO()):
        loaded = load_game(out)
    copy = loaded["world"]
    standing = A._letter(copy, REMOUNTS)
    # the letter's answers are planned at every read (seam 4), never stored:
    # read them the way the popup's passthrough does
    payload = MO.refresh_letter(copy, standing) if isinstance(standing, dict) else None
    answers = [str(a.get("action", "")) for a in ((payload or {}).get("answers") or []) if isinstance(a, dict)]
    row = MO.status_row(copy, REMOUNTS)
    check = {"row": {k: row.get(k) for k in ("status", "turn", "lord", "tier")},
             "letter_in_manager": standing is not None, "answers": answers,
             "button_decree": (payload or {}).get("button_decree"),
             "authority": int(copy.authority_tracker.authority),
             "gold": int(copy.nation_gold.get("France", 0))}
    ok = (row.get("status") == MO.STATUS_FIRED and standing is not None
          and "decree_ai_proposal" in answers and check["authority"] == DECREE_AUTHORITY)
    return {"save": str(out), "turn": int(world.current_turn), "standing": REMOUNTS,
            "delivered": {str(k): v for k, v in delivered.items()}, "self_check": check, "self_check_ok": ok}


def stage_te_deum(out: Path) -> dict:
    A = test_module("test_affairs_engine")
    from backend.commands.executor import CommandExecutor
    from backend.game_logic import diplomacy as D
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.world_state import WorldState
    from backend.save_manager import load_game, save_game

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(A.SCENARIO))
    A._no_moments(world)
    key = world._make_diplo_key("France", "Austria")
    before_state = world.diplomatic_states.get(key)
    world.diplomatic_states[key] = "ARMISTICE"
    world.nation_relations[key] = -20
    world.armistice_turns[key] = int(D.ARMISTICE_DURATION) - 1
    world.war_scores[key] = 30 if key.split("|")[0] == "France" else -30
    world.authority_tracker.authority = int(TE_DEUM_AUTHORITY)
    world.invalidate_active_nations_cache()
    world.__dict__.pop("_affairs_memo", None)
    out.parent.mkdir(parents=True, exist_ok=True)
    result = save_game(world, "AU-3a - the truce with Austria on its last turn, a Te Deum due", filepath=out)
    if not result.get("success"):
        raise SystemExit(f"save failed: {result}")

    # the self-check on a copy: ONE real end turn
    with contextlib.redirect_stdout(io.StringIO()):
        loaded = load_game(out)
        copy = loaded["world"]
        executor = CommandExecutor()
        tm = TurnManager(copy, executor=executor)
        random.seed(10_000 + int(copy.current_turn))
        tm.end_turn({"world": copy, "executor": executor})
    moves = [m for m in list(copy.authority_tracker.moves) if m.get("key") == "te_deum"]
    events = [e for e in copy.get_events_since_turn(0) if e.get("type") == "te_deum"]
    check = {"state_before": before_state, "state_after": copy.diplomatic_states.get(key),
             "te_deum_moves": [{k: m.get(k) for k in ("turn", "delta", "cause")} for m in moves],
             "te_deum_events": len(events), "authority_after": int(copy.authority_tracker.authority),
             "turn_after": int(copy.current_turn)}
    ok = bool(moves) and bool(events)
    return {"save": str(out), "turn": int(world.current_turn), "authority": TE_DEUM_AUTHORITY,
            "war_score": int(D.get_war_score_for(world, "France", "Austria")),
            "self_check": check, "self_check_ok": ok}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="the save file to write (inside the sandbox's save dir)")
    ap.add_argument("--chapter", default="b", choices=["b", "d"],
                    help="b: the Remounts standing with its Decree answer (authority 90); "
                         "d: the truce with Austria on its last turn, war score +30, authority 88 (the Te Deum)")
    args = ap.parse_args()
    summary = stage_decree(Path(args.out)) if args.chapter == "b" else stage_te_deum(Path(args.out))
    print(json.dumps(summary, indent=1, ensure_ascii=True))
    return 0 if summary["self_check_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

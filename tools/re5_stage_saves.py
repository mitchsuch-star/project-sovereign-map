"""RE-5 the close — the Mode C walk's crafted save (`docs/RECURRING_EVENTS_SPEC.md`
§16 "RE-5": the withdrawal seen; the record §26.1, chapter B).

A standing affair is withdrawn FREE when a dated moment arrives the same
morning (`affairs.withdraw_standing`). The walk cannot wait on the board for
that coincidence, so this stager builds the engine test's own board
(`tests/test_affairs_engine.py::test_a_moment_withdraws_a_standing_affair_free`):
the shipped boot, three corps quartered on Bavaria's soil (Swabia) so the
Host's Claims premises from the first morning, the chest at 5,000 so the
Staff's door stays shut, the look-ahead held at 0 so the letter lands on the
pulse's first morning (turn 7) one morning before the Bavarian Match (turn 8
— its date, Bavaria warm from the boot). The letter is made the current
dialogue and the world saved by `save_manager.save_game` into the sandbox's
save directory; the walk loads it by the client's own road (`POST /load`),
frames the standing letter, ends the turn, and the Match sets it aside.

    .venv/Scripts/python.exe tools/re5_stage_saves.py --chapter b --out <saves dir>/re5_withdrawal.json
    .venv/Scripts/python.exe tools/re5_stage_saves.py --chapter a --out <saves dir>/re5_chapter_a.json

The stager re-reads its save and ticks the next morning on the copy: the
Match arrives and the Host's row reads `withdrawn` — printed, never written.

Chapter A's save (RE5-2's finding): on the live historical board an Emperor
who gives no order is beaten in the field and his standing falls from 100
to 70 by turn 7, where the Marine's letter cannot bite (`bites: "floor"`:
the Decline must land above 71) — the walk met no letter in twenty turns.
The measured accept arms answered and fought, and their standing held. So
chapter A plays the shipped boot through the real turn flow
(`TurnManager.end_turn`, the series harness's per-turn seed) to turn 6 and
restores the standing to 100 — the one figure the idle board lost — then
saves; the walk loads it and the pulse's first morning (turn 7) delivers the
letter live. The self-check plays the copy one more turn: the letter stands.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("LLM_MODE", "mock")
for _k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
    os.environ.pop(_k, None)

HOST_OCCURRENCE = "the_host#1"
MOMENT = "bavarian_match"
SAVE_NAME = "RE-5 — the Host's letter standing, the Match due"


def test_module(name: str):
    """A test module imported by path for its STAGING helpers (`tests/` is not
    a package); its fixtures are never run here (the capture tool's idiom)."""
    path = ROOT / "tests" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_re5_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stage(out: Path, lapse: bool = False) -> dict:
    """Chapter B (the withdrawal): the Host's letter standing the morning
    before the Match. Chapter C (`lapse=True`): the same letter standing with
    every dated moment passed, so nothing sets it aside and it lapses on the
    morning after its answer-by turn — the walk leaves it unopened."""
    A = test_module("test_affairs_engine")
    from backend.game_logic import affairs as AF
    from backend.game_logic import moments as MO
    from backend.models.world_state import WorldState
    from backend.save_manager import load_game, save_game

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(A.SCENARIO))
    A._quarter(world, ("Ney", "Davout", "Lannes"))
    world.nation_gold["France"] = 5_000
    if lapse:
        A._no_moments(world)
    AF.LOOK_AHEAD = 0
    delivered = A._run(world, range(1, 8))
    if HOST_OCCURRENCE not in delivered.get(7, []):
        raise SystemExit(f"the Host's letter did not land on turn 7: {delivered}")
    letter = A._letter(world, HOST_OCCURRENCE)
    if letter is None:
        raise SystemExit("the Host's letter is not in the dialogue manager")
    A._make_current(world, letter)
    relation = A._rel(world, "Bavaria")
    if relation < 30:
        raise SystemExit(f"Bavaria is not warm enough for the Match (relation {relation})")
    out.parent.mkdir(parents=True, exist_ok=True)
    result = save_game(world, SAVE_NAME, filepath=out)
    if not result.get("success"):
        raise SystemExit(f"save failed: {result}")

    # the self-check on a copy: the next morning sets the letter aside (B),
    # or the letter stands through its answer-by turn and lapses after (C)
    with contextlib.redirect_stdout(io.StringIO()):
        loaded = load_game(out)
    copy = loaded["world"]
    if lapse:
        # the lapse is the turn flow's (the queue's answer-by gate), not the
        # moments tick's: play the copy through the real end turn, twice
        import random
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        statuses = []
        with contextlib.redirect_stdout(io.StringIO()):
            executor2 = CommandExecutor()
            tm2 = TurnManager(copy, executor=executor2)
            for i in range(2):
                random.seed(10_000 + 7 + i)
                tm2.end_turn({"world": copy, "executor": executor2})
                statuses.append((int(copy.current_turn), MO.status_row(copy, HOST_OCCURRENCE).get("status")))
        row = MO.status_row(copy, HOST_OCCURRENCE)
        check = {"after_each_end_turn": statuses,
                 "host_row": {k: row.get(k) for k in ("status", "turn", "lapsed_turn", "answer", "receipt")}}
        ok = statuses[0][1] == MO.STATUS_FIRED and row.get("status") == MO.STATUS_LAPSED
    else:
        A._at(copy, 8)
        arrived = A._tick(copy)
        row = MO.status_row(copy, HOST_OCCURRENCE)
        check = {"next_morning_delivers": list(arrived or []),
                 "host_row": {k: row.get(k) for k in ("status", "turn", "withdrawn_turn", "set_aside_for", "receipt")}}
        ok = MOMENT in check["next_morning_delivers"] and row.get("status") == MO.STATUS_WITHDRAWN
    summary = {"save": str(out), "turn": int(world.current_turn), "standing": HOST_OCCURRENCE,
               "bavaria_relation": relation, "delivered": {str(k): v for k, v in delivered.items()},
               "self_check": check, "self_check_ok": ok}
    return summary


def stage_chapter_a(out: Path, turns: int = 5, authority: int = 100) -> dict:
    """The live board to turn 6 through the real turn flow, the standing
    restored, saved; the copy's next morning must deliver the Marine's letter."""
    import random
    A = test_module("test_affairs_engine")
    from backend.commands.executor import CommandExecutor
    from backend.game_logic import moments as MO
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.world_state import WorldState
    from backend.save_manager import load_game, save_game

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(A.SCENARIO))
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
        gs = {"world": world, "executor": executor}
        for i in range(turns):
            random.seed(10_000 + i)
            tm.end_turn(gs)
    before = int(world.authority_tracker.authority)
    world.authority_tracker.authority = int(authority)
    world.__dict__.pop("_affairs_memo", None)
    out.parent.mkdir(parents=True, exist_ok=True)
    result = save_game(world, "RE-5 — the live board at turn 6, the standing held", filepath=out)
    if not result.get("success"):
        raise SystemExit(f"save failed: {result}")
    with contextlib.redirect_stdout(io.StringIO()):
        loaded = load_game(out)
        copy = loaded["world"]
        executor2 = CommandExecutor()
        tm2 = TurnManager(copy, executor=executor2)
        random.seed(10_000 + turns)
        tm2.end_turn({"world": copy, "executor": executor2})
    rows = {k: v.get("status") for k, v in MO._state(copy).items() if "#" in k}
    ok = any(k.startswith("santo_domingo#") and v == "fired" for k, v in rows.items())
    return {"save": str(out), "turn": int(world.current_turn), "standing_before": before, "standing": int(authority),
            "gold": int(world.nation_gold.get("France", 0)),
            "self_check": {"next_morning_rows": rows, "turn": int(copy.current_turn)}, "self_check_ok": ok}


def stage_offer(out: Path) -> dict:
    """The offer (an Edict) standing on turn 7: the edicts pins' own Remounts
    board — the boot with the dated moments passed, the chest at 5,000, the
    fleet under the Marine's bar (no Haiti letter), every corps at home (no
    campaign pay, so no Magazines), the cavalry depots at 59 % — the Remounts
    is the pulse's first pick. The letter made current and saved; the walk
    opens it from the desk and accepts."""
    A = test_module("test_affairs_engine")
    E = test_module("test_affairs_edicts")
    from backend.game_logic import affairs as AF
    from backend.game_logic import moments as MO
    from backend.models.world_state import WorldState
    from backend.save_manager import load_game, save_game

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(A.SCENARIO))
    E._remounts_board(world)
    AF.LOOK_AHEAD = 0
    delivered = A._run(world, range(1, 8))
    occ = "the_remounts#1"
    if occ not in delivered.get(7, []):
        raise SystemExit(f"the Remounts did not land on turn 7: {delivered}")
    letter = A._letter(world, occ)
    if letter is None:
        raise SystemExit("the Remounts letter is not in the dialogue manager")
    A._make_current(world, letter)
    out.parent.mkdir(parents=True, exist_ok=True)
    result = save_game(world, "RE-5 — the Remounts standing", filepath=out)
    if not result.get("success"):
        raise SystemExit(f"save failed: {result}")
    with contextlib.redirect_stdout(io.StringIO()):
        loaded = load_game(out)
    copy = loaded["world"]
    row = MO.status_row(copy, occ)
    standing = A._letter(copy, occ) is not None
    refusal = AF.edict_refusal(copy, "France", MO.entry(copy, "the_remounts"))
    check = {"row": {k: row.get(k) for k in ("status", "turn", "lord", "tier")}, "letter_in_manager": standing,
             "edict_refusal": refusal, "pool": int(copy.manpower_pools["France"]["cavalry"]),
             "gold": int(copy.nation_gold.get("France", 0))}
    ok = row.get("status") == MO.STATUS_FIRED and standing and refusal == ""
    return {"save": str(out), "turn": int(world.current_turn), "standing": occ,
            "delivered": {str(k): v for k, v in delivered.items()}, "self_check": check, "self_check_ok": ok}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="the save file to write (inside the sandbox's save dir)")
    ap.add_argument("--chapter", default="b", choices=["a", "b", "c", "d"],
                    help="b: the Host's letter standing before the Match (the withdrawal); "
                         "a: the live board at turn 6 with the standing held (the letter's arrival); "
                         "c: the Host's letter standing with every dated moment passed (the lapse); "
                         "d: the Remounts standing on turn 7 (the offer, the LAWS book, the quote)")
    args = ap.parse_args()
    if args.chapter == "a":
        summary = stage_chapter_a(Path(args.out))
    elif args.chapter == "d":
        summary = stage_offer(Path(args.out))
    else:
        summary = stage(Path(args.out), lapse=(args.chapter == "c"))
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0 if summary["self_check_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

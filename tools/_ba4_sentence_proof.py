"""Row BA, BA-4 (November 16, 2026) — the final tree is the measured one off
the served road.

After the measure's chain, things changed that no ambient or harness record
re-read: the key bar (`battle_day.KEY_BATTLE_MEN`, which exists only where a
campaign is served), the help's words, Murat's ability SENTENCE in the two
scenario files (§15.5.7 reversed "he must lead the killing blow") — and the
session's review (§15.21): the news of a battle abroad is told on every road
a field is lit on (an assault, a cannonade, a charge), where the chain
measured it on the main attack's road alone.

The keyed world probe of the final tree is read three ways against the
measured shipped arm's rows, forty ambient turns:

  as it is                 `marshals` (the sentence) and the keys of what the
                           player is TOLD — the review's news rows
  the old sentence back    the keys of what the player is told, alone
  ... and the review's     IDENTICAL, key for key: nothing else moved — no
  news left untold         key of the board

    PYTHONHASHSEED=0 .venv/Scripts/python.exe -X utf8 tools/_ba4_sentence_proof.py \
        --base <folder holding probe_X14_<seed>.json of the measured arm> \
        [--out tools/_ba4_final_tree_2026_11_16.json]

Read-only on the game; it writes its one record.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import pathlib
import random
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEEDS = ("jena", "marengo")
TURNS = 40
OLD = {
    "description": "When Murat personally breaks an enemy, his cavalry turns the rout into annihilation",
    "effect": ("+5,000 pursuit casualties when an enemy he defeats is forced to retreat "
               "(cavalry, leading the attack)"),
}


TOLD = ("event_log", "gazette_issues", "notifications", "pending_dispatch_events")


def rows_with(seed: str, turns: int, old_sentence: bool, untold: bool = False) -> list:
    """The probe's own loop on this tree (`tools/keyed_world_probe.py`), with
    Murat's old sentence put back on the booted world when asked — and, when
    `untold`, the review's news rows (an assault's, a cannonade's, a field
    battle's on a road other than the main attack's: each carries `kind` or
    `road`) written nowhere."""
    os.environ["SOVEREIGN_SEED"] = seed
    os.environ["LLM_MODE"] = "mock"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "INK_IRON_SEAMS"):
        os.environ.pop(key, None)
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    sink = io.StringIO()
    with redirect_stdout(sink), redirect_stderr(sink):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        from backend.models.world_state import WorldState
        from tools.keyed_world_probe import key_hashes
        world = WorldState.from_scenario(str(
            ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"))
        executor = CommandExecutor()
        manager = TurnManager(world, executor=executor)
        game_state = {"world": world, "executor": executor}
        if untold:
            from backend.game_logic import battle_news
            tell = battle_news._tell
            battle_news._tell = lambda w, event: (
                event if (event.get("kind") or event.get("road")) else tell(w, event))
    murat = world.marshals["Murat"]
    if murat.ability["description"] == OLD["description"]:
        raise SystemExit("the scenario still carries the old sentence: nothing to prove")
    if old_sentence:
        murat.ability.update(OLD)
    rows = []
    for turn in range(turns):
        sink = io.StringIO()
        with redirect_stdout(sink), redirect_stderr(sink):
            random.seed(10000 + turn)
            manager.end_turn(game_state)
            rows.append(key_hashes(world.to_dict()))
    return rows


def keys_differing(a: list, b: list) -> list:
    moved = set()
    for x, y in zip(a, b):
        moved |= {k for k in set(x) | set(y) if x.get(k) != y.get(k)}
    return sorted(moved)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="", help="the measured arm's probe_X14_<seed>.json files")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_ba4_final_tree_2026_11_16.json"))
    ap.add_argument("--child", default="", help="(internal) seed:old|new")
    ap.add_argument("--turns", type=int, default=TURNS)
    args = ap.parse_args()
    if args.child:
        seed, which = args.child.split(":")
        print("ROWS=" + json.dumps(rows_with(seed, args.turns, which != "new", which == "untold")))
        return 0
    base = pathlib.Path(args.base)
    record = {"_note": ("Row BA, BA-4 — the final tree against the measured shipped arm (the chain's X14) on "
                        "the keyed world probe, forty ambient turns: as it is; with Murat's OLD ability "
                        "sentence put back on the booted world; and with the review's news rows left untold "
                        "as well (an assault's, a cannonade's, a charge's — §15.21), which must be identical. "
                        "Written by tools/_ba4_sentence_proof.py."),
              "turns": args.turns, "told": list(TOLD), "seeds": {}}
    ok = True
    for seed in SEEDS:
        measured = json.loads((base / f"probe_X14_{seed}.json").read_text(encoding="utf-8"))["rows"]
        cell = {}
        for which in ("new", "old", "untold"):
            env = dict(os.environ, PYTHONHASHSEED="0")
            out = subprocess.run([sys.executable, "-X", "utf8", __file__, "--child", f"{seed}:{which}",
                                  "--turns", str(args.turns)],
                                 cwd=str(ROOT), env=env, capture_output=True, text=True, encoding="utf-8")
            line = next((ln for ln in out.stdout.splitlines() if ln.startswith("ROWS=")), None)
            if line is None:
                raise SystemExit(f"{seed} {which}: no rows\n{out.stdout[-800:]}\n{out.stderr[-800:]}")
            cell[which] = keys_differing(measured, json.loads(line[5:]))
        record["seeds"][seed] = {"as_it_is": cell["new"], "with_the_old_sentence": cell["old"],
                                 "and_the_reviews_news_untold": cell["untold"]}
        print(f"{seed}: keys differing from the measured arm — as it is {cell['new']}; "
              f"with the old sentence put back {cell['old'] or 'NONE'}; "
              f"and the review's news untold {cell['untold'] or 'NONE'}")
        ok &= (set(cell["new"]) <= {"marshals", *TOLD} and "marshals" in cell["new"]
               and set(cell["old"]) <= set(TOLD) and cell["untold"] == [])
    pathlib.Path(args.out).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("written", args.out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

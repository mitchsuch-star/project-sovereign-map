"""The keyed world probe — did a change move a game number?

N ambient turns of the 1805 campaign on a named seed, and after each one a hash
of every top-level key of `world.to_dict()`. Two trees that write the same rows
fought the same campaign, number for number; where they differ, the first turn
and the keys that differ say where to look.

It is the instrument behind "BA-2 moves no number" (row BA, session BA-2:
seeds jena and marengo, 30 turns, 212 keys a turn, identical to the commit
before — `docs/BATTLE_DIORAMA_SPEC.md` §15.12) and the one BA2-X2's fix is
measured with: the jena arm shows what the fix moves. Kept in the repository
by the session's review (November 15, 2026: BA2-X18); before it, the probe
lived in a scratch folder and the record could not be re-run.

    # one tree, one seed -> a JSON of rows (run it once per tree)
    PYTHONHASHSEED=0 python tools/keyed_world_probe.py run <tree root> <seed> <turns> <out.json>

    # two such files -> identical, or the first turn and the keys that differ
    python tools/keyed_world_probe.py compare <a.json> <b.json>

`<tree root>` is any checkout of the game: the working tree, or a copy made
with `git archive <commit> | tar -x -C <folder>` (the maps are tracked, so a
copy boots). PYTHONHASHSEED must be 0 for `run`: set iteration order is part
of what a campaign does. The turns are ambient — nobody commands France — and
the ambient random stream is seeded each turn (`random.seed(10000 + turn)`),
as the session's measures do. Display only: it plays a private campaign in
this process and writes one file.

Row BA, BA-4: `run` reads the measure's seam channel (`INK_IRON_SEAMS`,
`tools/_seams_env.py` — `MODULE:NAME=EXPR` specs separated by ";") and applies
it to the tree under test, so one tree can be read with a rule's seam held
down and the rows compared with the commit before. The specs applied are
written into the file (`seams`). Unset, nothing changes.
"""
import hashlib
import io
import json
import os
import random
import re
import sys
from contextlib import redirect_stderr, redirect_stdout

# a notification's id is a fresh uuid4 of the process, never from the seeded
# stream: masked, so that the key is compared by everything else in it
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def key_hashes(state: dict) -> dict:
    """One short hash per top-level key of a `world.to_dict()`."""
    return {key: hashlib.sha256(UUID.sub("UUID", json.dumps(
        state[key], sort_keys=True, default=str)).encode("utf-8")).hexdigest()[:16]
        for key in sorted(state)}


def run(root: str, seed: str, turns: int, out: str) -> int:
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise SystemExit("PYTHONHASHSEED must be 0 (set it in the environment, before Python starts)")
    root = os.path.abspath(root)
    os.environ["SOVEREIGN_SEED"] = seed
    os.environ["LLM_MODE"] = "mock"
    os.environ.pop("SOVEREIGN_SCENARIO", None)
    os.environ.pop("SOVEREIGN_MAP", None)
    os.chdir(root)
    sys.path.insert(0, root)

    sink = io.StringIO()
    with redirect_stdout(sink), redirect_stderr(sink):
        import backend
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(os.path.join(
            root, "godot-client", "project-sovereign", "assets", "maps", "europe_1805.json"))
        executor = CommandExecutor()
        turn_manager = TurnManager(world, executor=executor)
        game_state = {"world": world, "executor": executor}
    tree = os.path.dirname(os.path.abspath(backend.__file__))
    if os.path.dirname(tree) != root:
        raise SystemExit(f"the backend imported is {tree}, not the one under {root}")
    # BA-4: the seams the measure holds for this run, applied to THIS tree's
    # modules (a tree older than the channel has no `tools/_seams_env.py` and
    # is read as it stands — a spec asked of it is an error, never ignored).
    seams = []
    if os.environ.get("INK_IRON_SEAMS"):
        from tools._seams_env import apply_from_env
        seams = apply_from_env()

    rows, crashes = [], 0
    for turn in range(int(turns)):
        sink = io.StringIO()
        with redirect_stdout(sink), redirect_stderr(sink):
            random.seed(10000 + turn)
            turn_manager.end_turn(game_state)
            state = world.to_dict()
        # a court whose whole turn was lost to an exception prints this line (BA2-X2)
        crashes += sink.getvalue().count("turn crashed")
        rows.append(key_hashes(state))

    with open(out, "w", encoding="utf-8") as handle:
        json.dump({"tree": tree, "seed": seed, "turns": int(turns), "keys": len(rows[-1]) if rows else 0,
                   "crashes": crashes, "seams": list(seams), "rows": rows}, handle)
    print(f"{seed}: {turns} turns, {len(rows[-1]) if rows else 0} keys a turn, "
          f"{crashes} lost AI turn line(s), tree {tree}")
    return 0


def first_difference(a_rows: list, b_rows: list):
    """-> None when the two campaigns are the same, else (turn index from 1,
    the sorted keys that differ on that turn)."""
    for index, (a, b) in enumerate(zip(a_rows, b_rows), start=1):
        if a != b:
            return index, sorted(key for key in set(a) | set(b) if a.get(key) != b.get(key))
    if len(a_rows) != len(b_rows):
        return min(len(a_rows), len(b_rows)) + 1, ["(one campaign is longer)"]
    return None


def compare(a_path: str, b_path: str) -> int:
    with open(a_path, encoding="utf-8") as handle:
        a = json.load(handle)
    with open(b_path, encoding="utf-8") as handle:
        b = json.load(handle)
    if (a["seed"], a["turns"]) != (b["seed"], b["turns"]):
        raise SystemExit(f"not the same measure: {a['seed']} x {a['turns']} against {b['seed']} x {b['turns']}")
    found = first_difference(a["rows"], b["rows"])
    head = f"{a['seed']}, {a['turns']} turns, {a['keys']} keys a turn"
    if found is None:
        print(f"IDENTICAL — {head}; lost AI turn lines {a['crashes']} and {b['crashes']}")
        return 0
    turn, keys = found
    print(f"DIFFERENT — {head}: first at turn {turn}, {len(keys)} key(s): {', '.join(keys[:12])}"
          f"{' …' if len(keys) > 12 else ''}; lost AI turn lines {a['crashes']} and {b['crashes']}")
    return 1


def main(argv) -> int:
    if len(argv) == 6 and argv[1] == "run":
        return run(argv[2], argv[3], int(argv[4]), argv[5])
    if len(argv) == 4 and argv[1] == "compare":
        return compare(argv[2], argv[3])
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

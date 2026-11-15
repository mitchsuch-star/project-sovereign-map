"""Row BA, BA-2: each new claim of the walk, watched FAILING with its fix
switched off. One mutation of battle_acts.gd at a time, the walk run headless
on the scenes it bears on — at the scene's own speed for the claims read in a
showing's first instant — and the file put back whatever happens.

    python tools/ba2_switch_off.py [<repo root> [<case key> ...]]

It CHANGES A SOURCE FILE IN THE WORKING TREE while it runs. So (the review of
November 15, 2026 — BA2-X15):

* never run it while a commit's hook is running (the hook tests the working
  tree) or while another session edits battle_acts.gd;
* it refuses to start while its lock or its kept copy exists — another copy is
  running, or one was killed: the kept copy (`tools/.ba2_switch_off.kept`) is
  then the file as it was, byte for byte;
* every anchor is checked before anything is written; the file is read and put
  back as BYTES, so its line endings are its own; the walk has a time limit.
"""
import hashlib
import os
import pathlib
import subprocess
import sys

WALK_TIMEOUT_S = 1200

# key, name, [(old, new), ...], scenes, time scale, the words the failure must carry
CASES = [
    ("wall", "the wall is laid as it ended, and the opening does not stand it whole",
     [("""		host._transients.append(_wall)
		return
""", """		host._transients.append(_wall)
		_wall.show_the_end()
		return
"""), ("""	if _wall != null and is_instance_valid(_wall):
		_wall.stand_whole()
	for name in _works:
""", """	for name in _works:
""")], "assault_stormed", 1.0, "at the opening the wall already reads"),
    ("works", "the works are laid as they ended, and the opening does not rebuild them",
     [("""		bank.stand_as_built()
""", """		bank.stand_as_ended()
"""), ("""		(_works[name] as Rampart).stand_as_built()
""", """		pass
""")], "bombard_levels", 1.0, "the works stand at"),
    ("reserve", "the reserve's dead are on the table at the opening",
     [("""	for dead in _reserve_dead:
		if is_instance_valid(dead):
			(dead as Label).visible = false
""", """	for dead in _reserve_dead:
		if is_instance_valid(dead):
			pass
""")], "the_reserve", 1.0, "the reserve's dead are already told"),
    ("garrison", "the garrison keeps a portrait and a standard",
     [("""		if bool(c.get("garrison", false)):
			_dress_garrison(b)
""", """		if bool(c.get("garrison", false)):
			pass
""")], "assault_held", 8.0, "the garrison shows a portrait"),
    ("column", "a corps opens already in line",
     [("""		fig.position.x = float(fig.get_meta(&"ba_line_x")) * COLUMN_SQUEEZE
""", """		fig.position.x = float(fig.get_meta(&"ba_line_x"))
""")], "two_a_side", 1.0, "already stands in line"),
    ("wedge", "the order of battle is switched off",
     [("""const ORDER_OF_BATTLE := true
""", """const ORDER_OF_BATTLE := false
""")], "two_a_side", 8.0, "the table is laid as 'file'"),
    ("square", "a square is marked and not formed",
     [("""		_form_square(b, art)
""", """		pass
""")], "square_and_horse", 8.0, "is in square and stands in line"),
    ("standard", "the settled frame of a defeat leaves the victor's standard at home (BA2-X5)",
     [("""	_the_ground_is_as_it_ended()
	_the_victors_standard_stands_forward()
""", """	_the_ground_is_as_it_ended()
""")], "defeat_defending", 8.0, "'s standard stands at"),
    ("storm", "the stormers close up at once and the host's recoil stands them in line again",
     [("""	_close_up(b, AFTER_THE_RECOIL, 0.25)
""", """	_in_column(b)
""")], "assault_stormed", 8.0, "goes in standing in line"),
    ("ladders", "ladders are left against a wall that held",
     [("""		if fate != "stormed":
			_ladders = 0.0      # they fell back from it, or it opened its gates
""", """		if fate == "nothing":
			_ladders = 0.0      # they fell back from it, or it opened its gates
""")], "assault_held", 8.0, "ladders still stand against a wall that held"),
]


def _the_walk(root: pathlib.Path, scenes: str, speed: float) -> str:
    """The walk of one scene with the mutation in place -> everything it printed."""
    cmd = [str(root / ".venv/Scripts/python.exe"), str(root / "tools/ba1_acts_walk.py"),
           "--tag", "ba2_switch_off", "--only", scenes, "--headless", "--time-scale", str(speed)]
    try:
        out = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=WALK_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return f"the walk did not finish in {WALK_TIMEOUT_S} s"
    return (out.stdout or "") + (out.stderr or "")


def mutated(clean: bytes, swaps) -> bytes:
    """`clean` with each (old, new) put in once — in the file's own line
    endings. Raises ValueError when an anchor is not there exactly once."""
    text = clean.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    text = text.replace("\r\n", "\n")
    for old, new in swaps:
        found = text.count(old)
        if found != 1:
            raise ValueError(f"an anchor matches {found} times: {old[:60]!r}")
        text = text.replace(old, new)
    return text.replace("\n", eol).encode("utf-8")


def switch_off(root: pathlib.Path, only=(), walk=_the_walk, cases=None, say=print):
    """Run the cases -> [(name, caught)]. The file is put back, byte for byte,
    whatever happens short of the process being killed — and then the kept
    copy and the lock stay behind to say so."""
    root = pathlib.Path(root)
    acts = root / "godot-client/project-sovereign/scripts/battle_acts.gd"
    lock = root / "tools/.ba2_switch_off.lock"
    kept = root / "tools/.ba2_switch_off.kept"
    chosen = [case for case in (CASES if cases is None else cases) if not only or case[0] in only]
    if lock.exists() or kept.exists():
        raise SystemExit(
            f"refused: {lock.name} or {kept.name} exists in tools/ — another copy is running, or one "
            f"was killed. If none is running: {kept.name} is battle_acts.gd as it was; put it back "
            f"(or read `git diff` of battle_acts.gd), then delete both.")
    clean = acts.read_bytes()
    clean_sha = hashlib.sha256(clean).hexdigest()
    for _key, name, swaps, *_rest in chosen:          # every anchor, before anything is written
        try:
            mutated(clean, swaps)
        except ValueError as exc:
            raise SystemExit(f"refused, nothing written — '{name}': {exc}")
    with open(lock, "x", encoding="utf-8") as handle:  # "x": two copies cannot both pass here
        handle.write(str(os.getpid()))
    results = []
    try:
        kept.write_bytes(clean)
        for _key, name, swaps, scenes, speed, words in chosen:
            acts.write_bytes(mutated(clean, swaps))
            text = walk(root, scenes, speed)
            caught = words in text
            tail = [line for line in text.splitlines() if "claim(s) failed" in line]
            results.append((name, caught))
            say(("CAUGHT  " if caught else "MISSED  ") + name + " :: "
                + (tail[-1].strip().split(";")[0] if tail else "?"))
            if not caught:
                say("   ... " + "\n   ... ".join(text.splitlines()[-12:]))
    finally:
        acts.write_bytes(clean)
        back = hashlib.sha256(acts.read_bytes()).hexdigest() == clean_sha
        say(f"battle_acts.gd put back: {back}")
        if back:
            kept.unlink(missing_ok=True)
            lock.unlink(missing_ok=True)
    return results


def main(argv) -> int:
    root = pathlib.Path(argv[1]) if len(argv) > 1 else pathlib.Path(__file__).resolve().parents[1]
    results = switch_off(root, set(argv[2:]), say=lambda line: print(line, flush=True))
    print(sum(1 for _name, caught in results if caught), "of", len(results),
          "claims caught their fix switched off")
    return 0 if results and all(caught for _name, caught in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

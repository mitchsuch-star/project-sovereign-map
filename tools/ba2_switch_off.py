"""Row BA, BA-2: each new claim of the walk, watched FAILING with its fix
switched off. One mutation of battle_acts.gd at a time, the walk run headless
on the scenes it bears on — at the scene's own speed for the claims read in a
showing's first instant — and the file put back whatever happens."""
import hashlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1]
ONLY = set(sys.argv[2:])
ACTS = ROOT / "godot-client/project-sovereign/scripts/battle_acts.gd"
PY = ROOT / ".venv/Scripts/python.exe"
clean = ACTS.read_text(encoding="utf-8")
clean_sha = hashlib.sha256(clean.encode("utf-8")).hexdigest()

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

results = []
try:
    for key, name, swaps, scenes, speed, words in CASES:
        if ONLY and key not in ONLY:
            continue
        text_now = clean
        for old, new in swaps:
            assert text_now.count(old) == 1, (name, text_now.count(old), old[:50])
            text_now = text_now.replace(old, new)
        ACTS.write_text(text_now, encoding="utf-8", newline="\n")
        cmd = [str(PY), str(ROOT / "tools/ba1_acts_walk.py"), "--tag", "ba2_switch_off",
               "--only", scenes, "--headless", "--time-scale", str(speed)]
        out = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
        text = (out.stdout or "") + (out.stderr or "")
        caught = words in text
        tail = [line for line in text.splitlines() if "claim(s) failed" in line]
        results.append((name, caught))
        print(("CAUGHT  " if caught else "MISSED  ") + name + " :: "
              + (tail[-1].strip().split(";")[0] if tail else "?"), flush=True)
        if not caught:
            print("   ...", "\n   ... ".join(text.splitlines()[-12:]))
finally:
    ACTS.write_text(clean, encoding="utf-8", newline="\n")
    back = hashlib.sha256(ACTS.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    print("battle_acts.gd put back:", back == clean_sha)

print(sum(1 for _n, c in results if c), "of", len(results), "claims caught their fix switched off")

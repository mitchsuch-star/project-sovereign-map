# WO-D2/G1 slice 7 — one-off runtime check of the Cabinet matcher.
#
# The drift pin in tests/test_wo_slice7_cabinet_door.py re-executes the
# matcher's rules in PYTHON over the extracted lists. That catches list
# drift, but it cannot catch a GDScript SEMANTICS difference — `in` on a
# String, `text[i]` indexing, the boundary loop terminating — because the
# Python side never runs the shipped code. This does: it instantiates
# main.gd's script and calls the real predicates.
#
# Invoke headless (the GUI exe swallows stdout, so the verdict is written
# to a file — the project's standing one-off-check idiom):
#   Godot.exe --headless --quit --path godot-client/project-sovereign \
#     --script ../../tools/wo7_matcher_smoke.gd
extends SceneTree

# {sentence: expected_cabinet_family_verdict}
const CASES = {
	# claimed
	"declare war on prussia": true,
	"have talleyrand propose peace to austria": true,
	"should we declare war on prussia": true,
	"send the envoy to bavaria": true,
	"our minister will offer a truce to prussia": true,
	"declare war on prussia without delay": true,
	"make holland a puppet": true,
	"turn saxony into an autonomous state": true,
	"bought off prussia": true,
	"pay out bavaria": true,
	"court bavaria's favour": true,
	"invest in bavaria": true,
	"cede tyrol to bavaria": true,
	"guarantee saxony": true,
	"don't declare war on austria": true,
	# NOT claimed
	"ney, attack kienmayer": false,
	"soult, recruit troops": false,
	"grant ney a rente": false,
	"invest in defenses": false,
	"release the prisoners": false,
	"court martial that coward": false,
	"talleyrand, assess our situation": false,
	"make amends with prussia": false,
	"set war purpose against austria": false,
	"talleyrand, attack prussia": false,
	"economy": false,
	"murat, charge the guns": false,
}

# {text: {word: expected}} — the boundary helper, which is the newest and
# least obvious code in the matcher.
const WORD_CASES = [
	["court martial that coward", "court", true],
	["the courtier bowed", "court", false],
	["administer the province", "minister", false],
	["our minister will offer", "minister", true],
	["court bavaria's favour", "court", true],
]


func _init() -> void:
	var lines: Array[String] = []
	var failures := 0
	var main_script = load("res://scripts/main.gd")
	var m = main_script.new()

	for entry in WORD_CASES:
		var got = m._contains_word(entry[0], entry[1])
		var ok = got == entry[2]
		if not ok:
			failures += 1
		lines.append("%s _contains_word(%s, %s) = %s (want %s)" % [
			"PASS" if ok else "FAIL", entry[0], entry[1], got, entry[2]])

	for sentence in CASES:
		var want = CASES[sentence]
		# The full predicate minus the I/O: question guard, no-home guard,
		# then the family match — mirroring _redirect_diplomatic_command's
		# order without touching add_output/command_input.
		var got := false
		if not m._is_advisory_question(sentence):
			var homeless := false
			for keyword in m.DIPLO_NO_HOME_KEYWORDS:
				if keyword in sentence:
					homeless = true
					break
			if not homeless:
				got = m._matches_cabinet_family(sentence)
		var ok = got == want
		if not ok:
			failures += 1
		lines.append("%s %-46s claimed=%s (want %s)" % [
			"PASS" if ok else "FAIL", sentence, got, want])

	lines.append("")
	lines.append("FAILURES=%d of %d" % [
		failures, CASES.size() + WORD_CASES.size()])
	var f = FileAccess.open("res://../../tools/wo7_matcher_smoke.txt",
		FileAccess.WRITE)
	f.store_string("\n".join(lines))
	f.close()
	m.free()
	quit(1 if failures > 0 else 0)

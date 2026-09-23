extends SceneTree
# THE SCHOOL OF WAR, DRIVEN — headless (tests/test_tutorial_unbreakable_2026_09_23.py).
#
#   $env:TUT_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/tutorial_overlay_harness.gd
#
# The spec (written by the test):
#   {"responses": [<backend response dict>, ...],
#    "sent":      {"<index>": "<the line main.gd would note before that response>"},
#    "clicks":    {"<index>": ["skipstep:", "open:cabinet:Austria", ...]},
#    "out":       <abs path of the result JSON>}
#
# The REAL `tutorial_overlay.tscn` is instantiated. `responses[0]` arms the
# card through `on_world_swap()` (the /new_game payload); every later
# response goes through `observe()` exactly as main.gd hands them over — with
# `sent[i]` noted first (main.gd's `note_sent`) and `clicks[i]` pressed first
# through the card's own meta handler. After every response the step id, the
# badge, the body and the turn are recorded; the two signals the card emits
# (`suggest_command`, `open_cabinet`) are recorded as they fire.
#
# Why a driven pin and not a source census: the lesson's liveness is a
# property of the predicates run over REAL responses in order — a grep
# proves nothing about whether a card can wedge.
#
# Safety rails (IQ-10's): UiSettings is shimmed onto an in-memory ConfigFile
# before any scene loads, and the result JSON is written on every exit path.

const FRAME_LIMIT := 900

var _frames := 0
var _phase := "boot"
var _spec: Dictionary = {}
var _overlay = null
var _result: Dictionary = {"steps": [], "cabinet_opened": [], "suggested": []}


func _init():
	UiSettings._cfg = ConfigFile.new()
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames > FRAME_LIMIT:
		_result["error"] = "frame limit hit in phase " + _phase
		_finish()
		return
	match _phase:
		"boot":
			var path := OS.get_environment("TUT_SPEC")
			if path == "":
				_result["error"] = "TUT_SPEC not set"
				_finish()
				return
			var file := FileAccess.open(path, FileAccess.READ)
			if file == null:
				_result["error"] = "cannot open spec " + path
				_finish()
				return
			var parsed = JSON.parse_string(file.get_as_text())
			file.close()
			if typeof(parsed) != TYPE_DICTIONARY:
				_result["error"] = "spec is not a dictionary"
				_finish()
				return
			_spec = parsed
			var scene = load("res://scenes/tutorial_overlay.tscn")
			if scene == null:
				_result["error"] = "tutorial_overlay.tscn did not load"
				_finish()
				return
			_overlay = scene.instantiate()
			root.add_child(_overlay)
			_overlay.suggest_command.connect(func(cmd): _result["suggested"].append(str(cmd)))
			_overlay.open_cabinet.connect(func(nation): _result["cabinet_opened"].append(str(nation)))
			_phase = "drive"
		"drive":
			_drive()
			_finish()


func _drive() -> void:
	var responses: Array = _spec.get("responses", [])
	var sent: Dictionary = _spec.get("sent", {})
	var clicks: Dictionary = _spec.get("clicks", {})
	for i in responses.size():
		var key := str(i)
		if clicks.has(key):
			for meta in clicks[key]:
				_overlay._on_meta_clicked(str(meta))
		if sent.has(key):
			_overlay.note_sent(str(sent[key]))
		if i == 0:
			_overlay.on_world_swap(responses[i])
		else:
			_overlay.observe(responses[i])
		_record(i)


func _record(i: int) -> void:
	var index: int = _overlay._step_index
	var step: Dictionary = _overlay.STEPS[index] if index < _overlay.STEPS.size() else {}
	_result["steps"].append({
		"i": i,
		"index": index,
		"id": str(step.get("id", "")),
		"badge": str(_overlay._step_badge.text),
		"body": str(_overlay._body.text),
		"turn": int(_overlay._turn),
		"active": bool(_overlay._active),
		"done": bool(_overlay._done),
	})


func _finish() -> void:
	var out := str(_spec.get("out", OS.get_environment("TUT_OUT")))
	if out != "":
		var file := FileAccess.open(out, FileAccess.WRITE)
		if file != null:
			file.store_string(JSON.stringify(_result))
			file.close()
	quit()

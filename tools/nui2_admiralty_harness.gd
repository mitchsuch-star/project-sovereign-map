extends SceneTree
# NUI-2 "The Fleet Rides at Anchor" — the REAL Strategic Ledger
# (scenes/strategic_ledger.tscn) opened on THE ADMIRALTY book with captured
# `GET /ledger` responses, one board after another, and its rendered text
# read back. Nothing here decides what the tab shows; the pytest reads the
# record (tests/test_nui2_the_fleet_rides_at_anchor.py).
#
#   $env:NUI2_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script ../../tools/nui2_admiralty_harness.gd
#
# Spec: {"boards": [{"name": str, "ledger": <GET /ledger response>}, ...],
#        "out": <absolute result JSON path>}
# Result: {"boards": {name: {"text": parsed, "bbcode": raw}}, "error"?: str}
#
# The ledger is entered the way the game enters it: `open(api)` (which
# fetches and renders the current book) and then `_switch_tab(6)`, which
# re-renders THE ADMIRALTY from the cached payload. `open_to_tab` is NOT
# used: its tab is set AFTER the fetch, so against a stub that answers at
# once (this one) it would render the Forces book — the IQ-10 lesson that a
# synchronous stub is only faithful where the real road is synchronous too.
#
# Safety rails (IQ-10's): UiSettings shimmed in memory; the result JSON is
# written on every exit path; a hard frame cap.

const FRAME_LIMIT := 1500
const ADMIRALTY_TAB := 6

var _frames := 0
var _phase := "boot"
var _spec: Dictionary = {}
var _boards: Array = []
var _index := 0
var _wait := 0
var _ledger = null
var _api = null
var _result: Dictionary = {"boards": {}}


class ApiStub extends Node:
	var response: Dictionary = {}

	func get_ledger(cb: Callable) -> void:
		cb.call(response)

	# Click-only roads: never answered here (display needs none).
	func send_command(_c, _cb = null) -> void:
		pass

	func cancel_strategic_order(_m, _cb = null) -> void:
		pass


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
			var path := OS.get_environment("NUI2_SPEC")
			if path == "":
				_result["error"] = "NUI2_SPEC is not set"
				_finish()
				return
			var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
			if not (parsed is Dictionary):
				_result["error"] = "the spec at " + path + " is not a JSON object"
				_finish()
				return
			_spec = parsed
			_boards = _spec.get("boards", [])
			if not (_boards is Array) or _boards.is_empty():
				_result["error"] = "the spec names no boards"
				_finish()
				return
			_phase = "open"
		"open":
			if _index >= _boards.size():
				_finish()
				return
			var board = _boards[_index]
			var scene = load("res://scenes/strategic_ledger.tscn")
			_ledger = scene.instantiate()
			root.add_child(_ledger)
			_api = ApiStub.new()
			_api.response = board.get("ledger", {})
			root.add_child(_api)
			_wait = 3
			_phase = "enter"
		"enter":
			_wait -= 1
			if _wait > 0:
				return
			_ledger.open(_api)
			_ledger._switch_tab(ADMIRALTY_TAB)
			_wait = 4
			_phase = "record"
		"record":
			_wait -= 1
			if _wait > 0:
				return
			var board = _boards[_index]
			var content = _ledger.content_area
			_result["boards"][str(board.get("name", str(_index)))] = {
				"text": content.get_parsed_text(),
				"bbcode": content.text,
			}
			_ledger.queue_free()
			_api.queue_free()
			_ledger = null
			_api = null
			_index += 1
			_wait = 2
			_phase = "settle"
		"settle":
			_wait -= 1
			if _wait > 0:
				return
			_phase = "open"


func _finish():
	var out := str(_spec.get("out", ""))
	if out == "":
		out = OS.get_environment("NUI2_OUT")
	if out != "":
		var f := FileAccess.open(out, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_result))
			f.close()
	quit(0 if not _result.has("error") else 1)

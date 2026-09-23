extends SceneTree
# CX-R2 "The offer is reachable" — the command-line completer, DRIVEN.
#
#   $env:CXR2_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/cx_r2_completer_harness.gd
#
# The spec (written by tests/test_cx_r2_the_offer_is_reachable.py):
#   {"topology": <GET /map_topology>,
#    "boards": {<name>: {"game_state": <GET /test → game_state>,
#                        "prefixes": [<typed line>, ...]}},
#    "out": <abs path>}
# → {"offers": {<name>: {<prefix>: [<offered line>, ...]}}, ...}
#
# Boots the REAL `main.tscn` behind an API stub (CX-7's shape: the scene
# fetches on `_ready`, and a harness that waits for a live backend hangs),
# hands the REAL map node the real topology and the completer the real
# board, and records what `_build_completions` offers for each prefix. The
# pytest sends every offered line to POST /command and reads the effect —
# the memo's §2 scorer, run against the client itself rather than a Python
# copy of it.
#
# Safety rails (IQ-10's): UiSettings on an in-memory ConfigFile, no setter
# called; the result JSON is written on every exit path.

const HARD_FRAME_LIMIT := 900


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "cx-r2 stub"})

	func test_connection(cb = null): _answer("test_connection", cb)
	func get_map_topology(_cb = null): calls.append("get_map_topology")
	func get_ledger(cb = null): _answer("get_ledger", cb)
	func get_diplomatic_ledger(cb = null): _answer("get_diplomatic_ledger", cb)
	func get_marshal_overview(cb = null): _answer("get_marshal_overview", cb)
	func get_dispatch(cb = null): _answer("get_dispatch", cb)
	func get_gazette(cb = null): _answer("get_gazette", cb)
	func get_campaign_log(cb = null): _answer("get_campaign_log", cb)
	func get_mailbox(cb = null): _answer("get_mailbox", cb)
	func get_pending_envoy(cb = null): _answer("get_pending_envoy", cb)
	func send_command(_c, _cb = null): calls.append("send_command")
	func cancel_strategic_order(_m, _cb = null): calls.append("cancel_strategic_order")
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")


var _frames := 0
var _phase := "boot"
var _wait := 0
var _main = null
var _api = null
var _spec: Dictionary = {}
var _out: Dictionary = {}
var _fatal := ""


func _init():
	UiSettings._cfg = ConfigFile.new()
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames > HARD_FRAME_LIMIT:
		_fatal = "frame limit hit in phase %s" % _phase
		_finish()
		return
	if _wait > 0:
		_wait -= 1
		return
	match _phase:
		"boot":
			_boot()
		"run":
			_run()
		"done":
			_finish()


func _boot():
	var path := OS.get_environment("CXR2_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_fatal = "CXR2_SPEC missing or not a JSON object"
		_phase = "done"
		return
	_spec = parsed
	var packed: PackedScene = load("res://scenes/main.tscn")
	if packed == null:
		_fatal = "main.tscn did not load"
		_phase = "done"
		return
	_main = packed.instantiate()
	# swap the API before `_ready` can fetch
	_api = ApiStub.new()
	_api.name = "APIClient"
	var real = _main.get_node_or_null("APIClient")
	if real != null:
		_main.remove_child(real)
		real.queue_free()
	_main.add_child(_api)
	root.add_child(_main)
	if "api_client" in _main:
		_main.set("api_client", _api)
	_phase = "run"
	_wait = 30


func _run():
	var map_area = _main.get("map_area")
	if map_area == null or not map_area.has_method("set_region_topology"):
		_fatal = "the map node never resolved"
		_phase = "done"
		return
	map_area.set_region_topology(_spec.get("topology", {}))
	_out["topology_regions"] = map_area.get_region_topology().size()
	# One engine boot, several boards: each board's payload is handed to the
	# completer in turn, and every prefix is completed against it.
	var offers := {}
	var boards = _spec.get("boards", {})
	for board in boards.keys():
		var entry = boards[board]
		_main.set("_last_game_state", entry.get("game_state", {}))
		var mine := {}
		for prefix in entry.get("prefixes", []):
			mine[str(prefix)] = _main.call("_build_completions", str(prefix))
		offers[str(board)] = mine
	_out["offers"] = offers
	_phase = "done"


func _finish():
	if _fatal != "":
		_out["error"] = _fatal
	_out["frames"] = _frames
	var out := str(_spec.get("out", ""))
	if out != "":
		var f := FileAccess.open(out, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_out))
			f.close()
	quit(1 if _fatal != "" else 0)

# CX-7 slice 3 — the predictor, DRIVEN.
#
# The review round's sharpest procedural finding was that row CX pinned its
# own client half by READING THE SOURCE, on a stated belief that "there is no
# headless way to press Up in this project". There is: the same
# `Viewport.push_input(InputEventKey)` the row already used for Tab reaches
# `_on_command_input_gui_input`, and every key the completer binds is handled
# in that one function. This harness instantiates the REAL `main.tscn` and
# presses real keys at it.
#
# Built on IQ-10's proven shape (`tools/iq10_surface_screenshot.gd`): a
# `process_frame` tick with a hard frame limit, an in-memory `UiSettings`
# config so the player's file is never opened, and an API stub — the scene
# fetches on `_ready` and a harness that waits for a live backend is a
# harness that hangs.
#
#   Godot --headless --path godot-client/project-sovereign \
#         --script ../../tools/cx7_predictor_harness.gd
#
# Writes one JSON object to $CX7_OUT (default user://cx7_predictor.json) and
# prints it after a `[cx7]` marker. Read by `tests/test_cx7_predictor_driven.py`,
# which SKIPS when the engine is absent so the suite stays green without it.
extends SceneTree

const HARD_FRAME_LIMIT := 900


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "cx7 stub"})

	func test_connection(cb = null): _answer("test_connection", cb)
	# DELIBERATELY UNANSWERED. On the real client the topology request is
	# issued INSIDE `_on_connection_test` and its reply is 60+ frames away,
	# so `_initial_map_bootstrapped` is false for the whole of that handler.
	# A stub that answers synchronously flips the flag and hands the
	# handler the arm it takes in NO real boot — which made the first cut
	# of the CX3-R3 pin pass with the fix REVERTED. Recorded, not answered.
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
var _main: Node = null
var _input: LineEdit = null
var _row: RichTextLabel = null
var _api: ApiStub = null
var _out := {}
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
		"boot": _boot()
		"settle": _settle()
		"run": _run()
		"done": _finish()


func _boot():
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
	_phase = "settle"
	_wait = 30


func _settle():
	_input = _main.get("command_input")
	if _input == null:
		_fatal = "command_input never resolved"
		_phase = "done"
		return
	if "api_client" in _main:
		_main.set("api_client", _api)
	_row = _main.get("_suggestion_row")
	if _row == null:
		_main.call("_install_suggestion_row")
		_row = _main.get("_suggestion_row")
	if _row == null:
		_fatal = "the completion row was never installed"
		_phase = "done"
		return
	_phase = "run"


func _key(code: int) -> void:
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.pressed = true
	_input.grab_focus()
	_input.get_viewport().push_input(ev)


func _type(text: String) -> void:
	_input.grab_focus()
	_input.text = text
	_input.caret_column = text.length()
	_input.emit_signal("text_changed", text)


func _board() -> Dictionary:
	# CX-R2: the completer now draws each slot from the executor's answers on
	# the payload — a marshal's map entry (`tactical_state` gates), each
	# enemy's `at_war_with_player`, `passable_nations` — so the synthetic
	# board carries the shape the real payload has. The topology is left
	# unanswered (see `get_map_topology` above), so distances are unknown and
	# the pools come back alphabetically: the no-topology arm, exercised here.
	var gates := {
		"fortify_refusal": "", "unfortify_refusal": "not fortified",
		"drill_refusal": "", "defend_refusal": "", "garrison_refusal": "",
		"scout_range": 2, "move_open": ["Saxony", "Silesia"],
	}
	var corps := []
	for name in ["Ney", "Davout", "Soult", "Murat"]:
		corps.append({"name": name, "nation": "France", "tactical_state": gates})
	return {
		"player_nation": "France",
		"marshals": {"Ney": {"location": "Paris"}, "Davout": {"location": "Paris"},
			"Soult": {"location": "Paris"}, "Murat": {"location": "Paris"}},
		"enemies": {
			"Mack": {"location": "Swabia", "nation": "Austria", "at_war_with_player": true},
			"Brunswick": {"location": "Saxony", "nation": "Prussia", "at_war_with_player": true},
			"Deroy": {"location": "Silesia", "nation": "Bavaria", "at_war_with_player": true},
		},
		"passable_nations": ["Austria", "Bavaria", "France", "Prussia"],
		"map_data": {
			"Swabia": {"controller": "Austria", "marshals": []},
			"Silesia": {"controller": "Prussia", "marshals": []},
			"Saxony": {"controller": "Prussia", "marshals": []},
			"Paris": {"controller": "France", "marshals": corps},
		},
	}


func _offers() -> Array:
	var got = _main.get("_suggestions")
	return got if got is Array else []


func _run():
	# ── CX3-R8: the row's own font size, read off the LIVE node ────────
	_out["row_font_size"] = _row.get_theme_font_size("normal_font_size")
	_out["input_font_size"] = _input.get_theme_font_size("font_size")

	# ── CX3-R3: the boot handler must have REMEMBERED the board ────────
	# `_on_connection_test` ran on `_ready` against the stub, which answers
	# with no `game_state`; so this arm proves the SITE, not the payload —
	# the fix is that `_remember_game_state` is called for any response that
	# carries one, at the head of the block, rather than inside the
	# `_initial_map_bootstrapped` TRUE arm that is false on a fresh scene.
	_out["r3_bootstrapped_at_boot"] = _main.get("_initial_map_bootstrapped")
	_main.set("_last_game_state", {})      # the pre-boot state, explicitly
	_main.call("_on_connection_test", {"success": true, "game_state": _board()})
	# ... and the flag must STILL be false, or this arm took the other road
	_out["r3_bootstrapped_after"] = _main.get("_initial_map_bootstrapped")
	var remembered = _main.get("_last_game_state")
	_out["r3_remembered"] = (remembered is Dictionary
		and (remembered as Dictionary).size() > 0)
	_type("Ney, ")
	_out["r3_offers_after_boot"] = _offers().duplicate()

	# ── CX3-R1: every drawn offer must be reachable ────────────────────
	# An ADDRESSED verb slot, because that is where the list is longest —
	# three enemies on this board, and before CX3-R1 only the top one could
	# ever be placed on the line.
	_type("Ney, attack ")
	var drawn := _offers().duplicate()
	_out["r1_drawn"] = drawn.size()
	var reached := {}
	for _i in range(drawn.size() + 2):
		var idx = _main.get("_suggestion_index")
		if idx is int and idx >= 0 and idx < _offers().size():
			reached[str(_offers()[idx])] = true
		_key(KEY_DOWN)
	var missed := []
	for line in drawn:
		if not reached.has(str(line)):
			missed.append(str(line))
	_out["r1_unreachable"] = missed

	# ── CX3-R7: the completer wakes when a recalled line is EDITED ─────
	_main.call("_add_to_history", "Ney, attack Mack")
	_type("ney, a")
	_out["r7_before_up"] = _offers().size()
	_key(KEY_UP)
	_out["r7_line_after_up"] = _input.text
	_out["r7_during_walk"] = _offers().size()      # 0: the walk filled the line
	_type("Ney, attack Bru")                       # ... and now the player edits
	_out["r7_after_edit"] = _offers().duplicate()
	_out["r7_history_index"] = _main.get("history_index")

	# ── the completer never SENDS ──────────────────────────────────────
	_api.calls.clear()
	_type("ne")
	_key(KEY_TAB)
	_out["tab_filled"] = _input.text
	_out["tab_sent"] = ("send_command" in _api.calls)
	_phase = "done"


func _finish():
	if _fatal != "":
		_out["error"] = _fatal
	_out["frames"] = _frames
	var text := JSON.stringify(_out, "  ")
	var path := OS.get_environment("CX7_OUT")
	if path == "":
		path = "user://cx7_predictor.json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(text)
		f.close()
	print("[cx7] ", text)
	quit(1 if _fatal != "" else 0)

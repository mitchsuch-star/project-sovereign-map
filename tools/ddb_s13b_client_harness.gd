extends SceneTree
# Pre-Deploy S13b part 4 (October 19, 2026) — DD-B's client rows, DRIVEN:
# DDB-54 (Esc closes the topmost thing before it leaves the line), DDB-55 (the
# title caption changes at the crossfade's midpoint), DDB-56 (an ally's lost
# province reads as a loss), DDB-57 (a wheel notch is three lines; a tall
# reply opens at its first line, the window raised until the next command).
#
#   $env:DDB_SPEC = "<absolute path to a spec JSON>"   ({"out": <result path>})
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/ddb_s13b_client_harness.gd
#
# Boots the REAL main.tscn behind an API stub (tools/cc_client_harness.gd's,
# copied: a stub that never answers a fetch it was not asked to) and drives
# each scenario through the handler the live client uses — keys and the wheel
# through `root.push_input`. Pinned by `tests/test_ddb_s13b_the_client.py`.
# Safety rails (IQ-10's): UiSettings on an in-memory ConfigFile; the result
# JSON is written on every exit path.

const HARD_FRAME_LIMIT := 4000


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "ddb stub"})

	func test_connection(cb = null): _answer("test_connection", cb)
	func get_map_topology(_cb = null): calls.append("get_map_topology")
	func get_march_quotes(r, _cb = null): calls.append("march_quotes:" + str(r))
	func get_ledger(cb = null): _answer("get_ledger", cb)
	func get_diplomatic_ledger(cb = null): _answer("get_diplomatic_ledger", cb)
	func get_marshal_overview(cb = null): _answer("get_marshal_overview", cb)
	func get_dispatch(cb = null): _answer("get_dispatch", cb)
	func get_gazette(cb = null): _answer("get_gazette", cb)
	func get_campaign_log(cb = null): _answer("get_campaign_log", cb)
	func get_mailbox(_cb = null): calls.append("get_mailbox")
	func get_pending_envoy(cb = null): _answer("get_pending_envoy", cb)
	func get_pending_redemption(_cb = null): calls.append("get_pending_redemption")
	func get_campaign_end(_cb = null): calls.append("get_campaign_end")
	func list_saves(_cb = null): calls.append("list_saves")
	func load_game(_f, _cb = null): calls.append("load_game")
	func save_game(_f, _cb = null): calls.append("save_game")
	func new_game(_cb = null, _scenario = ""): calls.append("new_game")
	func set_llm_key(_k, _cb = null): calls.append("set_llm_key")
	var held_sends: Array = []
	func send_command(c, cb = null, r = false):
		calls.append("send:" + str(c) + ("|relayed" if r else ""))
		held_sends.append([str(c), cb])
	func answer_send(payload) -> String:
		if held_sends.is_empty():
			return ""
		var entry: Array = held_sends.pop_front()
		if entry[1] is Callable:
			(entry[1] as Callable).call(payload)
		return str(entry[0])
	func send_structured_command(c, _d = null, _cb = null): calls.append("send_structured:" + str(c))
	func send_dialogue_response(_c, _cb = null, _id = -1): calls.append("send_dialogue_response")
	func send_dialogue_response_with_params(_c, _p = null, _cb = null, _id = -1): calls.append("send_dialogue_response_with_params")
	func send_capture_choice_response(_c, _cb = null, _id = -1): calls.append("send_capture_choice_response")
	func send_strategic_response(_m, _t = null, _c = null, _cb = null): calls.append("send_strategic_response")
	func send_objection_response(_c, _cb = null): calls.append("send_objection_response")
	func send_marshal_petition_response(_c, _cb = null): calls.append("send_marshal_petition_response")
	func send_glorious_charge_response(_c, _cb = null): calls.append("send_glorious_charge_response")
	func send_diplomatic_objection_response(_c, _cb = null): calls.append("send_diplomatic_objection_response")
	func send_redemption_response(_c, _cb = null): calls.append("send_redemption_response")
	func activate_mailbox_item(_i, _cb = null): calls.append("activate_mailbox_item")
	func respond_to_mailbox_item(_i, _c = null, _cb = null): calls.append("respond_to_mailbox_item")
	func cancel_strategic_order(m, _cb = null): calls.append("cancel:" + str(m))
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")
	func get_march_reach(m, _cb = null): calls.append("march_reach:" + str(m))
	func get_order_quote(m, kind, target, _cb = null):
		calls.append("order_quote:%s|%s|%s" % [str(m), str(kind), str(target)])
	func get_group_quotes(_names, _dest, _cb = null): calls.append("group_quotes")


var _frames := 0
var _main = null
var _api = null
var _spec: Dictionary = {}
var _out: Dictionary = {}
var _fatal := ""
var _done := false


func _init():
	UiSettings._cfg = ConfigFile.new()
	process_frame.connect(_tick)
	_boot.call_deferred()


func _tick():
	_frames += 1
	if _frames > HARD_FRAME_LIMIT and not _done:
		_fatal = "frame limit hit"
		_finish()


func _boot():
	var path := OS.get_environment("DDB_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_fatal = "DDB_SPEC missing or not a JSON object"
		_finish()
		return
	_spec = parsed
	root.mode = Window.MODE_WINDOWED
	root.size = Vector2i(1600, 900)
	var packed: PackedScene = load("res://scenes/main.tscn")
	if packed == null:
		_fatal = "main.tscn did not load"
		_finish()
		return
	_main = packed.instantiate()
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
	_run.call_deferred()


func _wait(n: int) -> void:
	for _i in range(n):
		await process_frame


func _key(keycode: int) -> void:
	var ev := InputEventKey.new()
	ev.keycode = keycode
	ev.physical_keycode = keycode
	ev.pressed = true
	root.push_input(ev)
	var up := ev.duplicate()
	up.pressed = false
	root.push_input(up)


func _wheel(at: Vector2, down: bool) -> void:
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_WHEEL_DOWN if down else MOUSE_BUTTON_WHEEL_UP
	ev.pressed = true
	ev.factor = 1.0
	ev.position = at
	ev.global_position = at
	root.push_input(ev)
	var up := ev.duplicate()
	up.pressed = false
	root.push_input(up)


func _run() -> void:
	await _wait(60)
	await _ddb54()
	await _ddb57()
	_ddb56()
	await _ddb55()
	_finish()


# ── DDB-54: Esc closes the topmost thing before it leaves the line ─────────

func _ddb54() -> void:
	var line: LineEdit = _main.get("command_input")
	var top_bar = _main.get("top_bar")
	_main.call("set_input_enabled", true)
	top_bar.call("toggle_screen", "ledger")
	await _wait(4)
	_out["54_screen_open"] = bool(top_bar.call("is_screen_open"))
	line.grab_focus()
	line.text = "Ney, fortify"
	await _wait(2)
	_out["54_line_focused_before"] = line.has_focus()
	_key(KEY_ESCAPE)
	await _wait(4)
	_out["54_screen_open_after_first_esc"] = bool(top_bar.call("is_screen_open"))
	_out["54_line_focused_after_first_esc"] = line.has_focus()
	var pause = _main.get("pause_menu")
	_key(KEY_ESCAPE)
	await _wait(4)
	_out["54_line_focused_after_second_esc"] = line.has_focus()
	_out["54_pause_open_after_second_esc"] = bool(pause.visible) if pause != null else false
	line.text = ""


# ── DDB-57: the wheel and the tall reply ───────────────────────────────────

func _ddb57() -> void:
	var line: LineEdit = _main.get("command_input")
	var scroll: ScrollContainer = _main.get("output_scroll")
	_main.call("_apply_terminal_size", 420.0, 200.0)
	await _wait(6)
	var short_h: float = float(_main.get("_terminal_height"))
	_out["57_height_before"] = short_h
	# A reply taller than the window: forty lines.
	var lines := PackedStringArray()
	for i in range(40):
		lines.append("Line %d of the long reply, Sire." % (i + 1))
	_main.call("set_input_enabled", true)
	line.grab_focus()
	line.text = "help"
	_main.call("_execute_command")
	await _wait(2)
	_api.answer_send({"success": true, "message": "\n".join(lines)})
	await _wait(12)
	# (Read so the same scenario runs on a client without the fix — the
	# "before" reading: a missing field reads as false / -1.)
	_out["57_raised"] = _main.get("_reply_raised") == true
	_out["57_height_raised"] = float(_main.get("_terminal_height"))
	_out["57_scroll"] = int(scroll.scroll_vertical)
	_out["57_reply_top"] = int(_main.call("_reply_top_px")) if _main.has_method("_reply_top_px") else -1
	_out["57_scroll_max"] = int(scroll.get_v_scroll_bar().max_value)
	_out["57_view_h"] = float(scroll.size.y)
	# The wheel: one notch down moves three whole lines.
	var line_px: float = float(_main.call("_output_line_px")) if _main.has_method("_output_line_px") else -1.0
	_out["57_line_px"] = line_px
	var before := int(scroll.scroll_vertical)
	var rect: Rect2 = scroll.get_global_rect()
	_wheel(rect.get_center(), true)
	await _wait(3)
	_out["57_wheel_moved"] = int(scroll.scroll_vertical) - before
	# The next command puts the window back.
	_main.call("set_input_enabled", true)
	line.text = "status"
	_main.call("_execute_command")
	await _wait(6)
	_out["57_raised_after_next"] = _main.get("_reply_raised") == true
	_out["57_height_after_next"] = float(_main.get("_terminal_height"))
	_api.answer_send({"success": true, "message": "Short."})
	await _wait(8)
	_out["57_raised_for_a_short_reply"] = _main.get("_reply_raised") == true
	_out["57_scroll_at_end_for_a_short_reply"] = (
		int(scroll.scroll_vertical) >= int(scroll.get_v_scroll_bar().max_value - scroll.get_v_scroll_bar().page) - 2)
	# And a notch UP from the end of the log (the before-reading's own step:
	# the engine's page / 8, a fraction of one line in a 140 px window).
	var at_end := int(scroll.scroll_vertical)
	_wheel(scroll.get_global_rect().get_center(), false)
	await _wait(3)
	_out["57_wheel_up_moved"] = at_end - int(scroll.scroll_vertical)


# ── DDB-56: an ally's lost province reads as a loss ────────────────────────

func _ddb56() -> void:
	var packed: PackedScene = load("res://scenes/enemy_phase_dialog.tscn")
	var dialog = packed.instantiate()
	root.add_child(dialog)
	var error_hex := str(dialog.get("COLOR_ERROR"))
	var conquest_hex := str(Utils.COLOR_CONQUEST)
	var shapes := {
		"ally": {"captured_from": "Bavaria", "captured_from_alignment": "friend"},
		"ours": {"captured_from": "France", "captured_from_alignment": "player"},
		"foe": {"captured_from": "Austria", "captured_from_alignment": "foe"},
	}
	for key in shapes:
		var ev: Dictionary = {"type": "conquest", "region": "Munich"}
		ev.merge(shapes[key])
		var action := {"nation": "Austria", "ai_action": {"marshal": "Mack", "action": "move", "target": "Munich"},
			"events": [ev]}
		var text := str(dialog.call("_format_action", action))
		var colour := "other"
		if text.find("[color=#" + error_hex + "]") >= 0:
			colour = "error"
		elif text.find("[color=#" + conquest_hex + "]") >= 0:
			colour = "conquest"
		_out["56_" + key + "_colour"] = colour
		_out["56_" + key + "_text"] = text.substr(0, 400)
	dialog.queue_free()


# ── DDB-55: the caption at the crossfade's midpoint ────────────────────────

func _ddb55() -> void:
	var packed: PackedScene = load("res://scenes/main_menu.tscn")
	var menu = packed.instantiate()
	root.add_child(menu)
	await _wait(10)
	var caption: Label = menu.get("_caption")
	var first := str(caption.text)
	_out["55_first_caption"] = first
	menu.call("_advance_slide")
	await _wait(2)
	_out["55_caption_at_fade_start"] = str(caption.text)
	var fade: float = float(menu.get("FADE_SECONDS"))
	await create_timer(fade * 0.25).timeout
	_out["55_caption_at_quarter"] = str(caption.text)
	await create_timer(fade * 0.25 + 0.4).timeout
	_out["55_caption_past_midpoint"] = str(caption.text)
	menu.queue_free()


func _finish():
	if _done:
		return
	_done = true
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

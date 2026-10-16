extends SceneTree
# Row CC "Click & Command" — CC-0 "The line is the player's" and CC-1 "Click
# names into the line", DRIVEN.
#
#   $env:CC_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/cc_client_harness.gd
#
# The spec (written by tests/test_cc_click_and_command.py) carries the REAL
# boot board — `game_state` from GET /test and `topology` from GET
# /map_topology — plus the names the scenarios click ("out" is the result
# path). The harness boots the REAL `main.tscn` behind an API stub that
# records every command it is asked to send, hands the completer and the map
# the real board, and drives each scenario through the handler the live
# client uses — keys through `root.push_input`, so `_input`, the LineEdit and
# `_unhandled_input` all see them in the engine's own order.
#
# Safety rails (IQ-10's): UiSettings on an in-memory ConfigFile, no setter
# called; the result JSON is written on every exit path.

const HARD_FRAME_LIMIT := 900


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "cc stub"})

	func test_connection(cb = null): _answer("test_connection", cb)
	func get_map_topology(_cb = null): calls.append("get_map_topology")
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
	# The one the scenarios read: WHAT was sent, never answered (a sent
	# order stays "on the wire" until the scenario returns control itself).
	func send_command(c, _cb = null, r = false): calls.append("send:" + str(c) + ("|relayed" if r else ""))
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
	var path := OS.get_environment("CC_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_fatal = "CC_SPEC missing or not a JSON object"
		_phase = "done"
		return
	_spec = parsed
	var packed: PackedScene = load("res://scenes/main.tscn")
	if packed == null:
		_fatal = "main.tscn did not load"
		_phase = "done"
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
	_phase = "run"
	_wait = 60


# ── helpers ────────────────────────────────────────────────────────────────

func _line():
	return _main.get("command_input")


func _map():
	return _main.get("map_area")


func _panel():
	return _main.get("region_panel")


func _sends() -> Array:
	var out: Array = []
	for c in _api.calls:
		if str(c).begins_with("send:") or str(c).begins_with("send_structured:"):
			out.append(str(c))
	return out


func _fresh(text: String = "", caret: int = -1) -> void:
	"""A clean line: no offer, no parked draft, no latch, input open, `text`
	typed with the caret at `caret` (end when -1), the panel shut."""
	_main.set("_offered_command", "")
	_main.set("_parked_draft", "")
	_main.set("pending_relay_command", "")
	_main.set("_last_relay_fill", "")
	_main.set("_awaiting_end_turn_confirmation", false)
	_main.set("_chip_command_in_flight", false)
	_main.call("set_input_enabled", true)
	var panel = _panel()
	if panel != null and panel.visible:
		panel.close_panel()
	var line = _line()
	line.text = text
	line.caret_column = text.length() if caret < 0 else caret
	_main.call("_on_command_text_changed", line.text)
	var map = _map()
	if map != null:
		map.set("last_click_marshal", "")
		map.set("last_click_shift", false)
		map.set("last_click_ctrl", false)


func _key(keycode: int, unicode: int = 0) -> void:
	var ev := InputEventKey.new()
	ev.keycode = keycode
	ev.physical_keycode = keycode
	ev.unicode = unicode
	ev.pressed = true
	root.push_input(ev)
	var up := ev.duplicate()
	up.pressed = false
	root.push_input(up)


func _click(region: String, marshal: String = "", shift: bool = false) -> void:
	"""What `map_renderer_base` records on a left press, then the signal it
	emits — the province click as the live map delivers it."""
	var map = _map()
	map.set("last_click_marshal", marshal)
	map.set("last_click_shift", shift)
	map.set("last_click_ctrl", false)
	_main.call("_on_map_region_clicked", region)


func _panel_open_on(region: String) -> bool:
	var panel = _panel()
	return panel != null and panel.visible and str(panel.current_region()) == region


# ── the scenarios ──────────────────────────────────────────────────────────

func _run():
	var map = _map()
	if map != null and map.has_method("set_region_topology"):
		map.set_region_topology(_spec.get("topology", {}))
	var gs: Dictionary = _spec.get("game_state", {})
	_main.call("_reset_frontend_state_for_world_swap", true)
	_main.call("_update_map_from_game_state", gs)
	_main.set("_last_game_state", gs.duplicate(true))
	var own: String = str(_spec.get("own_marshal", "Ney"))        # shown name
	var second: String = str(_spec.get("second_marshal", "Soult"))
	var second_key: String = str(_spec.get("second_marshal_key", "Soult"))
	var enemy_key: String = str(_spec.get("enemy_key", "Mack"))
	var enemy_shown: String = str(_spec.get("enemy_shown", "Mack"))
	var far: String = str(_spec.get("province", "Moravia"))
	var spaced: String = str(_spec.get("spaced_province", "White Russia"))
	var line = _line()

	# ══ CC-0 ══════════════════════════════════════════════════════════════

	# s1 — a dispatch TODAY / tutor offer arrives over a draft.
	var draft := own + ", march to " + far.substr(0, 3)
	_fresh(draft)
	_main.call("_on_tutorial_suggest_command", second + ", fortify")
	_out["s1_line_kept"] = str(line.text)
	_out["s1_offered"] = str(_main.get("_offered_command"))
	_out["s1_row_head"] = str(_main.get("_suggestions")[0]) if (_main.get("_suggestions") as Array).size() > 0 else ""
	_main.call("_accept_suggestion")            # Tab takes the offer…
	_out["s1_line_after_tab"] = str(line.text)
	_out["s1_parked"] = str(_main.get("_parked_draft"))
	_out["s1_row_head_after_tab"] = str(_main.get("_suggestions")[0]) if (_main.get("_suggestions") as Array).size() > 0 else ""
	_main.call("_accept_suggestion")            # …and Tab again swaps back.
	_out["s1_line_after_swap"] = str(line.text)
	_out["s1_offered_after_swap"] = str(_main.get("_offered_command"))
	_out["s1_sends"] = _sends()

	# s2 — the parked draft comes back once the offered order has gone.
	_fresh(draft)
	_main.call("_on_tutorial_suggest_command", second + ", fortify")
	_main.call("_accept_suggestion")
	var before := _sends().size()
	_main.call("_execute_command")              # Enter sends the offer
	_out["s2_sent"] = _sends().slice(before)
	_out["s2_line_while_in_flight"] = str(line.text)
	_main.call("set_input_enabled", true)       # the reply returns control
	_out["s2_line_at_return"] = str(line.text)

	# s3 — type-through: a draft, a click on the map, then `e`.
	_fresh(own + ", march to ")
	_main.get_viewport().gui_release_focus()
	before = _sends().size()
	_key(KEY_E, 101)
	_out["s3_line"] = str(line.text)
	_out["s3_focused"] = bool(line.has_focus())
	_out["s3_sends"] = _sends().slice(before)
	# Control arm: an EMPTY line keeps the hotkey (the pin is sensitive).
	_fresh("")
	_main.get_viewport().gui_release_focus()
	before = _sends().size()
	_key(KEY_E, 101)
	_out["s3_control_sends"] = _sends().slice(before)
	_main.call("set_input_enabled", true)

	# s4 — the arrows still pan: focus does not move to the draft.
	_fresh(own + ", march to ")
	_main.get_viewport().gui_release_focus()
	_key(KEY_LEFT)
	_out["s4_focused_after_arrow"] = bool(line.has_focus())
	_out["s4_line"] = str(line.text)
	# …and Backspace edits the draft.
	_key(KEY_BACKSPACE)
	_out["s4_line_after_backspace"] = str(line.text)

	# s5 — the end-turn warning, a chip, then a bare Enter.
	_fresh("")
	_main.set("_awaiting_end_turn_confirmation", true)
	before = _sends().size()
	_main.call("_on_region_panel_command", second + ", drill")
	_main.set("_chip_command_in_flight", false)
	_main.call("set_input_enabled", true)      # the chip's reply returns
	line.text = ""
	_main.call("_execute_command")              # a bare Enter
	_out["s5_sends"] = _sends().slice(before)
	_out["s5_latch_after"] = bool(_main.get("_awaiting_end_turn_confirmation"))

	# s6 — a chip while a typed command is on the wire.
	_fresh("")
	_main.call("set_input_enabled", false)
	before = _sends().size()
	_main.call("_on_region_panel_command", second + ", drill")
	_out["s6_sends"] = _sends().slice(before)
	_out["s6_latch"] = bool(_main.get("_chip_command_in_flight"))

	# s7 — a relayed tail arriving over a draft waits beside it.
	_fresh(second + ", mar")
	_main.set("pending_relay_command", own + ", support " + second)
	_main.call("_fill_pending_relay")
	_out["s7_line"] = str(line.text)
	_out["s7_offered"] = str(_main.get("_offered_command"))
	_out["s7_last_relay_fill"] = str(_main.get("_last_relay_fill"))

	# s8 — CC-X10: an order sent with Enter, control returns, and the next
	# order's keys land (Godot 4.4's LineEdit left EDITING on submit and kept
	# focus, so `grab_focus()` re-armed nothing and the keys were dropped).
	_fresh("")
	line.grab_focus()
	_key(KEY_A, 97)
	_key(KEY_B, 98)
	_out["s8_typed_first"] = str(line.text)
	before = _sends().size()
	_key(KEY_ENTER)
	_out["s8_sent"] = _sends().slice(before)
	_main.call("set_input_enabled", true)       # the reply returns control
	_out["s8_editing_at_return"] = bool(line.is_editing()) if line.has_method("is_editing") else true
	_key(KEY_C, 99)
	_key(KEY_D, 100)
	_out["s8_line_after_return"] = str(line.text)
	# s8b — the safety net: a focused line that is NOT editing takes a key.
	if line.has_method("unedit"):
		line.unedit()
	_key(KEY_X, 120)
	_out["s8b_line"] = str(line.text)

	# ══ CC-1 ══════════════════════════════════════════════════════════════

	# c1 — the caret waits after `march to `: a province click writes it.
	_fresh(own + ", march to ")
	_click(far)
	_out["c1_line"] = str(line.text)
	_out["c1_panel_open"] = _panel_open_on(far)
	_out["c1_focused"] = bool(line.has_focus())

	# c2 — mid-word on a prefix of the clicked name: the prefix is replaced.
	_fresh(own + ", march to " + far.substr(0, 3))
	_click(far)
	_out["c2_line"] = str(line.text)

	# c3 — a two-word name, its prefix typed across the space.
	var cut := spaced.find(" ") + 3
	_fresh(own + ", march to " + spaced.substr(0, cut))
	_click(spaced)
	_out["c3_line"] = str(line.text)

	# c4 — no name slot: the click opens the panel as it always did.
	_fresh(own + ", ho")
	_click(far)
	_out["c4_line"] = str(line.text)
	_out["c4_panel_open"] = _panel_open_on(far)
	_panel().close_panel()

	# c5 — a piece clicked into `attack `: the man's shown name.
	_fresh(own + ", attack ")
	_click(far, enemy_key)
	_out["c5_line"] = str(line.text)

	# c6 — Shift on an empty line, an own piece: the order's addressee.
	_fresh("")
	_click(far, second_key, true)
	_out["c6_line"] = str(line.text)

	# c7 — Shift on an empty line, a province: its name.
	_fresh("")
	_click(far, "", true)
	_out["c7_line"] = str(line.text)

	# c8 — mid-line: the rest of the draft is untouched.
	var tail := "then attack " + enemy_shown
	var head := own + ", march to "
	_fresh(head + tail, head.length())
	_click(far)
	_out["c8_line"] = str(line.text)

	# c9 — a click on an offer is Tab: the line takes it and nothing is sent.
	_fresh(own.substr(0, 2))
	var offers: Array = (_main.get("_suggestions") as Array).duplicate()
	_out["c9_offers"] = offers
	before = _sends().size()
	_out["c9_clicked"] = str(offers[offers.size() - 1]) if offers.size() > 0 else ""
	if offers.size() > 0:
		_main.call("_on_suggestion_meta_clicked", "sugg:%d" % (offers.size() - 1))
	_out["c9_line"] = str(line.text)
	_out["c9_sends"] = _sends().slice(before)

	# c10 — the piece in FRONT wins the hover (and so the click).
	if map != null:
		var p: Vector2 = map.call("_get_map_mouse_position")
		map.set("marshal_hitboxes", [
			{"rect": Rect2(p - Vector2(10, 30), Vector2(20, 40)), "marshal": {"name": "Behind"}},
			{"rect": Rect2(p - Vector2(10, 10), Vector2(20, 40)), "marshal": {"name": "Front"}},
		])
		map.call("_refresh_hover_state")
		_out["c10_hovered"] = str((map.get("hovered_marshal") as Dictionary).get("name", ""))
		map.set("marshal_hitboxes", [])

	# c11 — the map answers the draft.
	_fresh(own + ", march to " + far)
	_out["c11_glow"] = str(map.get("selected_region")) if map != null else ""
	_fresh(second + ", ")
	_out["c11_glow_addressee"] = str(map.get("selected_region")) if map != null else ""
	_fresh("")
	_out["c11_glow_cleared"] = str(map.get("selected_region")) if map != null else ""

	_out["api_calls"] = _api.calls
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

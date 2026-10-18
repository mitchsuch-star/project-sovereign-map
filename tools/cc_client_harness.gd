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
	# CC-2: recorded, never answered — the scenario hands the panel the real
	# backend quotes itself, so it controls when (and for which province).
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
	# The one the scenarios read: WHAT was sent, never answered (a sent
	# order stays "on the wire" until the scenario returns control itself).
	# CC-5: its callback is HELD (oldest first) so a scenario may answer it
	# with the real backend's reply (`answer_send`); the earlier scenarios
	# never answer and are unchanged.
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
	# CC-5: the cancel's callback is held under "cancel:<marshal>".
	func cancel_strategic_order(m, cb = null):
		calls.append("cancel:" + str(m))
		held["cancel:" + str(m)] = cb
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")
	# CC-3: the selection's two read-only GETs — recorded, their callbacks
	# HELD until the scenario answers them with the real backend's payload
	# (`answer`), so the scenario controls when (and whether) each lands.
	var held := {}
	func get_march_reach(m, cb = null):
		var key := "march_reach:" + str(m)
		calls.append(key)
		held[key] = cb
	func get_order_quote(m, kind, target, cb = null):
		var key := "order_quote:%s|%s|%s" % [str(m), str(kind), str(target)]
		calls.append(key)
		held[key] = cb
	# CC-5: the group card's one GET, held under "group_quotes:<a,b,c>|<dest>".
	func get_group_quotes(names, dest, cb = null):
		var keys := PackedStringArray()
		for n in names:
			keys.append(str(n))
		var key := "group_quotes:%s|%s" % [",".join(keys), str(dest)]
		calls.append(key)
		held[key] = cb
	func answer(key: String, payload) -> bool:
		var cb = held.get(key, null)
		held.erase(key)
		if cb is Callable:
			cb.call(payload)
			return true
		return false


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
	if _frames > (HARD_FRAME_LIMIT * 4 if _spec.has("cc5") else HARD_FRAME_LIMIT):
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
		"cc3_view":
			# The live boot shows the map when /map_topology answers; the stub
			# never does (`_run` hands the map the topology itself).
			var map = _map()
			if map != null:
				map.visible = true
				map.call("fit_europe")
			_phase = "cc3_drag"
			_wait = 4
		"cc3_drag":
			_run_cc3_drag()
		"cc3_minimized":
			_restore_after_replies()
		"cc3_restored":
			_read_restored_terminal()
		"cc5_view":
			var map5 = _map()
			if map5 != null:
				map5.visible = true
				map5.call("fit_europe")
			_phase = "cc5_running"
			_run_cc5.call_deferred()
		"cc5_running":
			pass   # the coroutine moves the phase on when it is done
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
	if _main.has_method("_clear_order_selection"):
		_main.call("_clear_order_selection")   # CC-3: no corps selected
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
		map.set("last_click_fogged", "")


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


func _click(region: String, marshal: String = "", shift: bool = false, fogged: String = "") -> void:
	"""What `map_renderer_base` records on a left press, then the signal it
	emits — the province click as the live map delivers it."""
	var map = _map()
	map.set("last_click_marshal", marshal)
	map.set("last_click_shift", shift)
	map.set("last_click_ctrl", false)
	map.set("last_click_fogged", fogged)
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
	if bool(_spec.get("cc5_only", false)):
		# CC-5's own pins (`tests/test_cc5_the_war_table.py`): its scenarios
		# alone, on a real screen (headless the root is 64 px square).
		_out["api_calls"] = _api.calls
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1600, 900)
		_phase = "cc5_view"
		_wait = 6
		return
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

	# ══ CC-2 "March here" (only when the spec carries real quotes) ════════
	if _spec.has("march_quotes"):
		_run_march_here()

	_out["api_calls"] = _api.calls
	_phase = "done"
	# ══ CC-3 "Select, click, Enter" (only when the spec carries its board) ═
	if _spec.has("cc3"):
		_run_cc3()
		_out["api_calls"] = _api.calls
		# The drag is pushed as real mouse events, so the map needs a real
		# screen: headless, the root is 64 px square and the top bar covers
		# every piece. A 1600x900 window, then the whole theatre in view.
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1600, 900)
		_phase = "cc3_view"
		_wait = 6


func _calls_since(n: int, prefix: String) -> Array:
	var out: Array = []
	for i in range(n, _api.calls.size()):
		if str(_api.calls[i]).begins_with(prefix):
			out.append(str(_api.calls[i]))
	return out


func _run_march_here() -> void:
	var panel = _panel()
	var prov := str(_spec.get("quotes_province", ""))
	var payload: Dictionary = _spec.get("march_quotes", {})
	var other := str(_spec.get("refused_province", ""))
	var refused: Dictionary = _spec.get("refused_quotes", {})

	# p1 — a province click opens the panel, which asks for its quotes; the
	# quotes render as they came.
	_fresh("")
	var n: int = _api.calls.size()
	_click(prov)
	_out["p1_panel_open"] = _panel_open_on(prov)
	_out["p1_requested"] = _calls_since(n, "march_quotes:")
	panel.call("set_march_quotes", prov, payload)
	_out["p1_text"] = str(panel.content_area.text)

	# p2 — a stale answer (another province) never draws under this title.
	panel.call("set_march_quotes", other, refused)
	_out["p2_text_unchanged"] = str(panel.content_area.text) == str(_out["p1_text"])

	# p3 — a chip sends its quoted command through the chip road.
	var first := ""
	for q in payload.get("march", []):
		if q is Dictionary and bool(q.get("ok", false)):
			first = str(q.get("command", ""))
			break
	_out["p3_command"] = first
	var before := _sends().size()
	panel.call("_on_meta_clicked", "do:" + first)
	_out["p3_sent"] = _sends().slice(before)

	# p4 — the order's reply re-renders the panel, which asks again.
	_main.set("_chip_command_in_flight", false)
	_main.call("set_input_enabled", true)
	n = _api.calls.size()
	panel.call("refresh_if_open")
	_out["p4_requested_again"] = _calls_since(n, "march_quotes:")

	# p5 — "+N more…" opens every quote, the refused under their reason.
	panel.call("_on_meta_clicked", "toggle:march_more")
	_out["p5_text_more"] = str(panel.content_area.text)
	panel.call("_on_meta_clicked", "toggle:march_more")

	# p6 — a province no corps of ours can reach: the reasons ARE the answer.
	panel.close_panel()
	_click(other)
	panel.call("set_march_quotes", other, refused)
	_out["p6_text"] = str(panel.content_area.text)
	panel.close_panel()


# ══ CC-3 "Select, click, Enter" + drag ═════════════════════════════════════
# The spec's "cc3" block carries the REAL backend's answers for one corps of
# ours: his reach (GET /march_reach) and the exact quotes (GET /march_quotes?
# marshal=…) for a province, a refused province, an enemy and an ally. The
# stub HOLDS each GET until the scenario answers it, as the wire would.

func _card():
	return _main.get("order_card")


func _selected() -> String:
	return str(_main.get("_order_marshal"))


func _order() -> Dictionary:
	var map = _map()
	if map == null or not map.has_method("order_report"):
		return {}
	return map.call("order_report")


func _layer() -> Dictionary:
	var rep := _order()
	return rep.get("layer", {}) if rep.get("layer", {}) is Dictionary else {}


func _quote_key(cc3: Dictionary, kind: String, target: String) -> String:
	return "order_quote:%s|%s|%s" % [str(cc3["subject"]), kind, target]


func _select(cc3: Dictionary) -> void:
	"""Select the subject as the live client does — a plain click on his piece
	on an empty line — and answer his reach."""
	_fresh("")
	_click(str(cc3["subject_location"]), str(cc3["subject"]))
	_api.answer("march_reach:" + str(cc3["subject"]), cc3["reach"])


func _run_cc3() -> void:
	var cc3: Dictionary = _spec["cc3"]
	var subject := str(cc3["subject"])
	var home := str(cc3["subject_location"])
	var dest := str(cc3["dest"])
	var line = _line()
	var panel = _panel()
	var card = _card()
	# The board again: CC-1's c10 emptied the hit boxes the ring and the
	# drag stand on.
	_main.call("_update_map_from_game_state", (_spec.get("game_state", {}) as Dictionary).duplicate(true))

	# k1 — a plain click on a piece of ours on an EMPTY line selects him: the
	# ring, the strip, his reach asked for once; the panel stays shut.
	_fresh("")
	var n: int = _api.calls.size()
	_click(home, subject)
	_out["k1_selected"] = _selected()
	_out["k1_panel_open"] = bool(panel.visible)
	_out["k1_reach_asked"] = _calls_since(n, "march_reach:")
	_out["k1_ring"] = bool(_layer().get("ring", false))
	_out["k1_strip_loading"] = str(_main.call("order_strip_text"))
	_out["k1_tint_before"] = bool(_order().get("tint_visible", false))
	_api.answer("march_reach:" + subject, cc3["reach"])
	var bands: Dictionary = _order().get("bands", {})
	_out["k1_band_count"] = bands.size()
	_out["k1_band_dest"] = int(bands.get(dest, -1))
	_out["k1_band_far"] = int(bands.get(str(cc3.get("far_dest", "")), -1))
	_out["k1_tint"] = bool(_order().get("tint_visible", false))
	_out["k1_strip"] = str(_main.call("order_strip_text"))

	# k2 — the cursor over a province draws the reach's road at once; at rest
	# it fetches the exact quote — ONE GET, however long it rests.
	n = _api.calls.size()
	_main.call("_on_map_order_hover", dest, "")
	_out["k2_ghost_points"] = int(_layer().get("ghost_points", 0))
	_out["k2_ghost_label"] = str(_layer().get("ghost_label", ""))
	_main.call("_on_order_dwell_timeout")
	_main.call("_on_order_dwell_timeout")
	_out["k2_quote_asked"] = _calls_since(n, "order_quote:")
	_api.answer(_quote_key(cc3, "dest", dest), {"success": true, "quote": cc3["dest_quote"]})
	_out["k2_ghost_label_exact"] = str(_layer().get("ghost_label", ""))
	_out["k2_ghost_kind"] = str(_layer().get("ghost_kind", ""))

	# k3 — a click on the province opens the CARD on that quote, never the
	# panel; the quote in hand is not asked again.
	n = _api.calls.size()
	_click(dest)
	_out["k3_card_open"] = bool(card.visible)
	_out["k3_card_command"] = str(card.call("command"))
	_out["k3_panel_open"] = bool(panel.visible)
	_out["k3_asked_again"] = _calls_since(n, "order_quote:")
	_out["k3_modal"] = bool(_main.call("_is_modal_dialog_open"))

	# k4 — Enter on the card sends exactly its command — never the line,
	# never the armed end turn — and lets the selection go.
	_main.set("_awaiting_end_turn_confirmation", true)
	var before := _sends().size()
	_key(KEY_ENTER)
	_out["k4_sent"] = _sends().slice(before)
	_out["k4_card_open"] = bool(card.visible)
	_out["k4_selected"] = _selected()
	_out["k4_latch"] = bool(_main.get("_awaiting_end_turn_confirmation"))
	_out["k4_line"] = str(line.text)
	_out["k4_ring"] = bool(_layer().get("ring", false))
	_out["k4_tint"] = bool(_order().get("tint_visible", false))
	_out["k4_history_last"] = str((_main.get("command_history") as Array).back()) \
		if (_main.get("command_history") as Array).size() > 0 else ""
	_main.set("_chip_command_in_flight", false)
	_main.call("set_input_enabled", true)

	# k5 — Esc on the card shuts it, sends nothing and keeps him selected;
	# the next Esc lets him go — the line's own Esc, then the map's ladder
	# (which must not ALSO open the pause menu).
	_select(cc3)
	_click(dest)
	_api.answer(_quote_key(cc3, "dest", dest), {"success": true, "quote": cc3["dest_quote"]})
	before = _sends().size()
	_key(KEY_ESCAPE)
	_out["k5_card_open"] = bool(card.visible)
	_out["k5_sends"] = _sends().slice(before)
	_out["k5_selected_after_card_esc"] = _selected()
	_main.call("_clear_suggestions")
	line.grab_focus()
	_key(KEY_ESCAPE)
	_out["k5_selected_after_line_esc"] = _selected()
	_select(cc3)
	_main.get_viewport().gui_release_focus()
	var pause = _main.get("pause_menu")
	_key(KEY_ESCAPE)
	_out["k5_selected_after_map_esc"] = _selected()
	_out["k5_pause_open"] = bool(pause.visible) if pause != null else false
	if pause != null and pause.visible:
		pause.call("close_menu")

	# k5b — under the card every key is the card's: a bare E ends no turn.
	_select(cc3)
	_click(dest)
	_api.answer(_quote_key(cc3, "dest", dest), {"success": true, "quote": cc3["dest_quote"]})
	before = _sends().size()
	_main.get_viewport().gui_release_focus()
	_key(KEY_E, 101)
	_out["k5b_sends"] = _sends().slice(before)
	_out["k5b_card_open"] = bool(card.visible)
	_key(KEY_ESCAPE)

	# k6 — [Put in line] writes the quoted command on the line, sends nothing
	# and lets the selection go.
	_select(cc3)
	_click(dest)
	_api.answer(_quote_key(cc3, "dest", dest), {"success": true, "quote": cc3["dest_quote"]})
	before = _sends().size()
	card.call("_on_line")
	_out["k6_line"] = str(line.text)
	_out["k6_sends"] = _sends().slice(before)
	_out["k6_selected"] = _selected()
	_out["k6_card_open"] = bool(card.visible)

	# k7 — an enemy we see: the ATTACK quote (attack within his reach, march
	# and attack beyond it — the backend's word, not the client's).
	if cc3.has("enemy"):
		_select(cc3)
		n = _api.calls.size()
		_click(str(cc3["enemy_location"]), str(cc3["enemy"]))
		_out["k7_asked"] = _calls_since(n, "order_quote:")
		_api.answer(_quote_key(cc3, "enemy", str(cc3["enemy"])), {"success": true, "quote": cc3["enemy_quote"]})
		_out["k7_card_command"] = str(card.call("command"))
		_key(KEY_ESCAPE)

	# k7b — CC-X11: the enemy's FOG CHIP (partial sight names him — the
	# panel's ATTACK row offers him): the attack quote, not a march to his
	# province.
	if cc3.has("enemy"):
		_select(cc3)
		n = _api.calls.size()
		_click(str(cc3["enemy_location"]), "", false, str(cc3["enemy"]))
		_out["k7b_asked"] = _calls_since(n, "order_quote:")
		_api.answer(_quote_key(cc3, "enemy", str(cc3["enemy"])), {"success": true, "quote": cc3["enemy_quote"]})
		_out["k7b_card_command"] = str(card.call("command"))
		_key(KEY_ESCAPE)
		# The control arm: the same province clicked off the chip is a march.
		n = _api.calls.size()
		_click(str(cc3["enemy_location"]))
		_out["k7c_asked"] = _calls_since(n, "order_quote:")
		_key(KEY_ESCAPE)

	# k8 — a corps of ours: SUPPORT.
	if cc3.has("ally"):
		_select(cc3)
		n = _api.calls.size()
		_click(str(cc3["ally_location"]), str(cc3["ally"]))
		_out["k8_asked"] = _calls_since(n, "order_quote:")
		_api.answer(_quote_key(cc3, "ally", str(cc3["ally"])), {"success": true, "quote": cc3["ally_quote"]})
		_out["k8_card_command"] = str(card.call("command"))
		_key(KEY_ESCAPE)

	# k8b — a refused order: the card says why and Send is shut; its Enter
	# only closes the card.
	if cc3.has("refused_dest"):
		_select(cc3)
		_click(str(cc3["refused_dest"]))
		_api.answer(_quote_key(cc3, "dest", str(cc3["refused_dest"])),
			{"success": true, "quote": cc3["refused_quote"]})
		_out["k8b_sendable"] = bool(card.call("is_sendable"))
		var terms = card.get("terms_label")
		_out["k8b_terms"] = str(terms.get_parsed_text()) if terms != null else ""
		before = _sends().size()
		_key(KEY_ENTER)
		_out["k8b_sends"] = _sends().slice(before)
		_out["k8b_card_open"] = bool(card.visible)
		_out["k8b_selected"] = _selected()

	# k9 — nothing acts while a command is on the wire.
	_select(cc3)
	_main.call("set_input_enabled", false)
	n = _api.calls.size()
	_click(dest)
	_out["k9_card_open"] = bool(card.visible)
	_out["k9_asked"] = _calls_since(n, "order_quote:")
	_main.call("set_input_enabled", true)

	# k10 — a draft owns the clicks (CC-1): no selection; a typed draft lets
	# a selection go.
	_fresh(str(_spec.get("own_marshal", "Ney")) + ", ho")
	_click(home, subject)
	_out["k10_selected_with_draft"] = _selected()
	_out["k10_panel_with_draft"] = _panel_open_on(home)
	_select(cc3)
	line.text = "N"
	_main.call("_on_command_text_changed", line.text)
	_out["k10_selected_after_typing"] = _selected()
	# k10b — CC-X12: a line filled by CODE (a suggestion taken, the history
	# walked — no text_changed) and then a map click: the click is CC-1's
	# pen, not a card; the selection is let go.
	_select(cc3)
	line.text = str(_spec.get("own_marshal", "Ney")) + ", march to "
	line.caret_column = line.text.length()
	n = _api.calls.size()
	_click(dest)
	_out["k10b_selected"] = _selected()
	_out["k10b_card_open"] = bool(card.visible)
	_out["k10b_asked"] = _calls_since(n, "order_quote:")
	_out["k10b_line"] = str(line.text)

	# k11 — the clearing rules.
	var rules := {}
	_select(cc3)
	_main.call("_on_map_dismiss_requested")
	rules["right_click"] = _selected()
	_select(cc3)
	_click(home, subject)
	rules["click_him_again"] = _selected()
	var top = _main.get("top_bar")
	_select(cc3)
	if top != null:
		top.call("toggle_screen", "ledger")
		rules["screen"] = _selected()
		top.call("close_all_screens")
	_select(cc3)
	var other = _main.get("clarification_popup")
	if other != null:
		other.show()
		rules["modal"] = _selected()
		other.hide()
	_select(cc3)
	_main.call("_send_end_turn")
	rules["end_turn"] = _selected()
	_main.call("set_input_enabled", true)
	var gs: Dictionary = (_spec.get("game_state", {}) as Dictionary).duplicate(true)
	_select(cc3)
	var without: Dictionary = gs.duplicate(true)
	(without["marshals"] as Dictionary).erase(subject)
	_main.call("_update_map_from_game_state", without)
	rules["missing_from_board"] = _selected()
	_main.call("_update_map_from_game_state", gs)
	_select(cc3)
	n = _api.calls.size()
	_main.call("_update_map_from_game_state", gs)
	rules["standing_on_new_board"] = _selected()
	rules["reach_asked_again"] = _calls_since(n, "march_reach:").size()
	_api.answer("march_reach:" + subject, cc3["reach"])
	_main.call("_reset_frontend_state_for_world_swap", false)
	rules["world_swap"] = _selected()
	_main.call("_update_map_from_game_state", gs)
	_out["k11_rules"] = rules

	# k12 — the panel stays shut while he is selected.
	_fresh("")
	_click(dest)
	_out["k12_panel_first"] = _panel_open_on(dest)
	_click(home, subject)
	_out["k12_panel_after_select"] = bool(panel.visible)
	_click(dest)
	_out["k12_panel_after_click"] = bool(panel.visible)
	_out["k12_card_after_click"] = bool(card.visible)
	_key(KEY_ESCAPE)
	_fresh("")


func _push_motion(at: Vector2, held: bool) -> void:
	var ev := InputEventMouseMotion.new()
	ev.position = at
	ev.global_position = at
	ev.button_mask = MOUSE_BUTTON_MASK_LEFT if held else 0
	root.push_input(ev, true)


func _push_left(at: Vector2, pressed: bool) -> void:
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = pressed
	ev.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
	ev.position = at
	ev.global_position = at
	root.push_input(ev, true)


func _hover(at: Vector2, held: bool = false) -> void:
	# Twice: the map reads the control under the cursor as the GUI left it
	# after the PREVIOUS motion (the GUI updates its hover after `_input`).
	_push_motion(at, held)
	_push_motion(at, held)


func _uncovered(map, at: Vector2) -> bool:
	_hover(at)
	var over = root.gui_get_hovered_control()
	return over == map or (over != null and map.is_ancestor_of(over))


func _water_point(map) -> Vector2:
	"""A point of open water on screen, clear of every piece and panel."""
	var rect: Rect2 = map.get_global_rect()
	var y := rect.position.y + 60.0
	while y < rect.end.y - 20.0:
		var x := rect.position.x + 20.0
		while x < rect.end.x - 20.0:
			var p := Vector2(x, y)
			var world: Vector2 = map.call("_screen_to_map_position", p)
			if str(map.call("_lookup_region_from_color_map", world)) == "":
				var clear := true
				for hb in map.get("marshal_hitboxes") + map.get("fleet_hitboxes"):
					if (hb["rect"] as Rect2).grow(12.0).has_point(world):
						clear = false
						break
				if clear and _uncovered(map, p):
					return p
			x += 24.0
		y += 24.0
	return Vector2(-1, -1)


func _run_cc3_drag() -> void:
	var cc3: Dictionary = _spec["cc3"]
	var subject := str(cc3["subject"])
	var drag_dest := str(cc3["drag_dest"])
	var map = _map()
	var card = _card()
	_fresh("")
	_main.call("_minimize_terminal")   # the bottom-left is the map's again
	var water := _water_point(map)
	var piece: Vector2 = map.call("screen_point_of_marshal", subject)
	var dest_pt: Vector2 = map.call("screen_point_of_region", drag_dest)
	_out["d_water"] = [water.x, water.y]
	_out["d_piece"] = [piece.x, piece.y]
	_out["d_dest_pt"] = [dest_pt.x, dest_pt.y]
	var map_rect: Rect2 = map.get_global_rect()
	_out["d_view"] = [map_rect.position.x, map_rect.position.y, map_rect.size.x, map_rect.size.y]
	_out["d_piece_uncovered"] = _uncovered(map, piece)
	var over = root.gui_get_hovered_control()
	_out["d_over_piece"] = (str(over.get_path()) + ":" + over.get_class()
		+ ":filter=" + str(over.mouse_filter) + ":rect=" + str(over.get_global_rect())) if over != null else ""
	_out["d_hovered_piece"] = str((map.get("hovered_marshal") as Dictionary).get("name", ""))

	# d1 — pressed on his piece it waits; 5 px is still a click, 9 px a drag:
	# he is selected and his reach asked for; over a province the reach's road
	# is the ghost; released there, the card for that province.
	_fresh("")
	_hover(piece)
	var n: int = _api.calls.size()
	_push_left(piece, true)
	_out["d1_pending"] = bool(_order().get("drag_pending", false))
	_out["d1_selected_on_press"] = _selected()
	_push_motion(piece + Vector2(5, 0), true)
	_out["d1_dragging_at_5"] = bool(_order().get("dragging", false))
	_push_motion(piece + Vector2(9, 0), true)
	_out["d1_dragging_at_9"] = bool(_order().get("dragging", false))
	_out["d1_selected"] = _selected()
	_out["d1_reach_asked"] = _calls_since(n, "march_reach:")
	_api.answer("march_reach:" + subject, cc3["reach"])
	_hover(dest_pt, true)
	_out["d1_ghost_points"] = int(_layer().get("ghost_points", 0))
	_out["d1_ghost_kind"] = str(_layer().get("ghost_kind", ""))
	n = _api.calls.size()
	_push_left(dest_pt, false)
	_out["d1_asked"] = _calls_since(n, "order_quote:")
	_api.answer(_quote_key(cc3, "dest", drag_dest), {"success": true, "quote": cc3["drag_quote"]})
	_out["d1_card_open"] = bool(card.visible)
	_out["d1_card_command"] = str(card.call("command"))
	# The card stands clear of the road it confirms (and of the strip) — its
	# place is set on the answer (`set_avoid`), before this line runs.
	var card_rect: Rect2 = card.call("placed_rect")
	var road_rect: Rect2 = map.call("order_screen_rect")
	var view_rect := Rect2(Vector2.ZERO, Vector2(root.size))
	_out["d1_card_rect"] = [card_rect.position.x, card_rect.position.y, card_rect.size.x, card_rect.size.y]
	_out["d1_road_rect"] = [road_rect.position.x, road_rect.position.y, road_rect.size.x, road_rect.size.y]
	_out["d1_card_covers_road"] = card_rect.intersects(road_rect)
	_out["d1_card_on_screen"] = view_rect.encloses(card_rect)
	_key(KEY_ESCAPE)
	_out["d1_selected_after_card_esc"] = _selected()

	# d2 — released over open water: the gesture is let go.
	_fresh("")
	if water.x >= 0.0:
		_hover(piece)
		_push_left(piece, true)
		_push_motion(piece + Vector2(12, 0), true)
		_api.answer("march_reach:" + subject, cc3["reach"])
		_hover(water, true)
		_push_left(water, false)
		_out["d2_selected"] = _selected()
		_out["d2_card_open"] = bool(card.visible)
		_out["d2_dragging"] = bool(_order().get("dragging", false))

	# d3 — Esc mid-drag: the gesture is let go, and that Esc goes no further.
	_fresh("")
	_main.get_viewport().gui_release_focus()
	_hover(piece)
	_push_left(piece, true)
	_push_motion(piece + Vector2(12, 0), true)
	_out["d3_dragging"] = bool(_order().get("dragging", false))
	_key(KEY_ESCAPE)
	_out["d3_dragging_after"] = bool(_order().get("dragging", false))
	_out["d3_selected"] = _selected()
	var pause = _main.get("pause_menu")
	_out["d3_pause_open"] = bool(pause.visible) if pause != null else false
	if pause != null and pause.visible:
		pause.call("close_menu")
	_push_left(piece + Vector2(12, 0), false)
	_out["d3_card_open"] = bool(card.visible)

	# d4 — pressed and released where it stands: the click — he is selected.
	_fresh("")
	_hover(piece)
	_push_left(piece, true)
	_push_left(piece, false)
	_out["d4_selected"] = _selected()

	# d5 — with a draft on the line his piece does not drag: the press is
	# CC-1's pen (the name written where the caret waits).
	_fresh(str(_spec.get("own_marshal", "Ney")) + ", march to ")
	_hover(piece)
	_push_left(piece, true)
	_out["d5_pending"] = bool(_order().get("drag_pending", false))
	_push_left(piece, false)
	_out["d5_line"] = str(_line().text)
	_out["d5_selected"] = _selected()
	_fresh("")
	# CC-X13: orders given with the terminal minimized — the replies land in
	# a log no one can see (frames pass while it is hidden, as they do while
	# the backend answers); restored, it must stand on its newest line.
	var scroll = _main.get("output_scroll")
	scroll.scroll_vertical = 0
	for i in range(60):
		_main.call("add_output", "a reply written while the terminal was minimized — line %d" % i)
	_out["api_calls"] = _api.calls
	_phase = "cc3_minimized"
	_wait = 10


func _restore_after_replies() -> void:
	_main.call("_restore_terminal")
	_phase = "cc3_restored"
	_wait = 12


func _read_restored_terminal() -> void:
	var scroll = _main.get("output_scroll")
	var bar = scroll.get_v_scroll_bar()
	_out["x13_scroll"] = int(scroll.scroll_vertical)
	_out["x13_end"] = int(bar.max_value - bar.page)
	_out["x13_at_end"] = int(scroll.scroll_vertical) >= int(bar.max_value - bar.page) - 2
	_phase = "cc5_view" if _spec.has("cc5") else "done"
	_wait = 4


# ══ CC-5 "The war table" ═══════════════════════════════════════════════════
# The spec's "cc5" block carries a REAL board with standing orders of ours
# and busy corps, and the real backend's replies the scenarios answer the
# held requests with: the arrow card's cancel and the Orders tab's (POST
# /cancel_order, in sequence on one world), the group's quotes (GET
# /march_quotes?marshals=…) and its lines' own replies (POST /command).

func _wait_frames(n: int) -> void:
	for _i in range(n):
		await process_frame


func _arrow_rows() -> Array:
	var rows = _layer().get("arrows", [])
	return rows if rows is Array else []


func _arrow_keys() -> Array:
	var out: Array = []
	for a in _arrow_rows():
		out.append(str(a.get("marshal", "")))
	out.sort()
	return out


func _arrow_point(map, key: String) -> Vector2:
	"""A point on his arrow the map will take as the arrow's: on its drawn
	line (or badge), uncovered, with no piece or chip under it."""
	var layer = map.get("order_layer")
	for geo in layer.call("_arrow_geometry"):
		if str(geo["marshal"]) != key:
			continue
		var pts: PackedVector2Array = geo["pts"]
		var cands: Array = [(geo["badge"] as Rect2).get_center()]
		for k in range(pts.size() - 1):
			for f in [0.5, 0.35, 0.65, 0.8]:
				cands.append(pts[k].lerp(pts[k + 1], f))
		for c in cands:
			var at: Vector2 = c + layer.global_position
			if _uncovered(map, at) and (map.get("hovered_marshal") as Dictionary).is_empty() \
					and (map.get("hovered_fogged_force") as Dictionary).is_empty():
				return at
	return Vector2(-1, -1)


func _press_at(at: Vector2) -> void:
	_hover(at)
	_push_left(at, true)
	_push_left(at, false)


func _terminal_tail(chars: int = 900) -> String:
	var display = _main.get("output_display")
	var text: String = display.get_parsed_text() if display != null else ""
	return text.substr(maxi(0, text.length() - chars))


func _ctrl_click(region: String, marshal: String) -> void:
	var map = _map()
	map.set("last_click_marshal", marshal)
	map.set("last_click_shift", false)
	map.set("last_click_ctrl", true)
	map.set("last_click_fogged", "")
	_main.call("_on_map_region_clicked", region)


func _key_mod(keycode: int, unicode: int, alt: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = keycode
	ev.physical_keycode = keycode
	ev.unicode = unicode
	ev.alt_pressed = alt
	ev.pressed = true
	root.push_input(ev)
	var up := ev.duplicate()
	up.pressed = false
	root.push_input(up)


func _board(gs: Dictionary) -> void:
	_main.call("_update_map_from_game_state", gs.duplicate(true))
	_main.set("_last_game_state", gs.duplicate(true))


func _home_of(key: String) -> String:
	var gs: Dictionary = _main.get("_last_game_state")
	var row = (gs.get("marshals", {}) as Dictionary).get(key, {})
	return str(row.get("location", "")) if row is Dictionary else ""


func _gather(members: Array) -> void:
	"""Ctrl-click every member in turn, on an empty line."""
	_fresh("")
	for key in members:
		_ctrl_click(_home_of(str(key)), str(key))


func _group_send(cc5: Dictionary, run: Dictionary, tag: String) -> void:
	"""One group run: gather, click the province, answer the card's GET, press
	Enter, then answer each line as it is sent — the replies in `run`."""
	var members: Array = run["members"]
	var dest := str(run["dest"])
	var card = _card()
	# The run's board was read with the pool refilled: the client holds the
	# same pool.
	_main.set("actions_remaining", int(run.get("ap", 4)))
	_gather(members)
	_out[tag + "_group"] = (_main.get("_order_group") as Array).duplicate()
	_out[tag + "_rings"] = int(_layer().get("rings", 0))
	_out[tag + "_strip"] = str(_main.call("order_strip_text"))
	var n: int = _api.calls.size()
	_click(dest)
	_out[tag + "_card_mode"] = str(card.call("mode"))
	_out[tag + "_asked"] = _calls_since(n, "group_quotes:")
	var key := "group_quotes:%s|%s" % [",".join(PackedStringArray(members.map(func(k): return str(k)))), dest]
	_api.answer(key, run["quotes"])
	_out[tag + "_lines"] = card.call("group_lines")
	var terms = card.get("terms_label")
	_out[tag + "_terms"] = str(terms.get_parsed_text()) if terms != null else ""
	_out[tag + "_send_label"] = str((card.get("send_button") as Button).text)
	_main.set("_awaiting_end_turn_confirmation", true)
	var sent_before := _sends().size()
	_api.held_sends.clear()
	_key(KEY_ENTER)
	var trace: Array = []
	var replies: Array = run["replies"]
	for i in range(replies.size()):
		await _wait_frames(2)
		var on_wire: Array = []
		for h in _api.held_sends:
			on_wire.append(str(h[0]))
		trace.append({"on_wire": on_wire, "run": _main.call("group_run_report").duplicate(true)})
		if _api.held_sends.is_empty():
			break
		_api.answer_send(replies[i])
	await _wait_frames(3)
	_out[tag + "_trace"] = trace
	_out[tag + "_sent"] = _sends().slice(sent_before)
	_out[tag + "_left_on_wire"] = _api.held_sends.size()
	_out[tag + "_latch"] = bool(_main.get("_awaiting_end_turn_confirmation"))
	_out[tag + "_modal"] = bool(_main.call("_is_modal_dialog_open"))
	_out[tag + "_run_after"] = _main.call("group_run_report")
	_out[tag + "_tail"] = _terminal_tail(1400)
	# The arrows the run left standing — and whether any two badges print on
	# one spot (orders bound for one province step their badges apart).
	var layer = _map().get("order_layer")
	var badges: Array = []
	var dests: Array = []
	for geo in layer.call("_arrow_geometry"):
		badges.append(geo["badge"])
		dests.append(str(geo["marshal"]) + ":" + str((geo["arrow"] as Dictionary).get("label", "")))
	var overlap := false
	for i in range(badges.size()):
		for j in range(i + 1, badges.size()):
			if (badges[i] as Rect2).intersects(badges[j]):
				overlap = true
	_out[tag + "_arrow_labels"] = dests
	_out[tag + "_badges_overlap"] = overlap
	var dm = _main.get("dialog_manager")
	if dm != null and dm.has_method("hide_all"):
		dm.call("hide_all")
	_main.set("_chip_command_in_flight", false)
	_main.call("set_input_enabled", true)
	_api.held_sends.clear()


func _run_cc5() -> void:
	var cc5: Dictionary = _spec["cc5"]
	var map = _map()
	var card = _card()
	_board(cc5["board"])
	_main.set("actions_remaining", int(cc5.get("ap", 4)))
	_fresh("")
	_main.call("_minimize_terminal")   # the bottom-left is the map's again
	map.call("fit_europe")
	await _wait_frames(6)

	# w1 — every standing order of ours is an arrow; no enemy has one.
	_out["w1_arrows"] = _arrow_rows()
	_out["w1_arrow_keys"] = _arrow_keys()

	# w2 — a click on the march's arrow: the card's ARROW face; Enter is
	# Change — he is selected (his reach asked for).
	var march := str(cc5["march_subject"])
	var at := _arrow_point(map, march)
	_out["w2_point"] = [at.x, at.y]
	_hover(at)
	_out["w2_hover"] = str(_layer().get("arrow_hover", ""))
	var n: int = _api.calls.size()
	_push_left(at, true)
	_push_left(at, false)
	_out["w2_card_open"] = bool(card.visible)
	_out["w2_card_mode"] = str(card.call("mode"))
	_out["w2_card_marshal"] = str(card.call("standing_marshal"))
	_out["w2_title"] = str((card.get("title_label") as Label).text)
	_out["w2_headline"] = str((card.get("command_label") as Label).text)
	_out["w2_terms"] = str(card.get("terms_label").get_parsed_text())
	_out["w2_cancel_label"] = str((card.get("send_button") as Button).text)
	_out["w2_selected_before"] = _selected()
	var card_rect: Rect2 = card.call("placed_rect")
	var arrow_rect: Rect2 = map.call("order_arrow_screen_rect", march)
	_out["w2_card_covers_arrow"] = card_rect.intersects(arrow_rect)
	_key(KEY_ENTER)
	_out["w2_selected_after_enter"] = _selected()
	_out["w2_card_open_after_enter"] = bool(card.visible)
	_out["w2_reach_asked"] = _calls_since(n, "march_reach:")
	_out["w2_sends"] = _calls_since(n, "send:")
	_out["w2_cancels"] = _calls_since(n, "cancel:")
	_out["w2_arrows_dimmed"] = bool(_layer().get("arrows_dimmed", false))
	_key(KEY_ESCAPE)
	_out["w2_selected_after_esc"] = _selected()

	# w3 — [Cancel order] on the arrow card: ONE POST /cancel_order; the
	# reply's board takes the arrow away, the actions count follows, and the
	# armed end turn is retired (a send means the player moved on).
	_fresh("")
	_main.set("_awaiting_end_turn_confirmation", true)
	at = _arrow_point(map, march)
	n = _api.calls.size()
	_press_at(at)
	_out["w3_card_open"] = bool(card.visible)
	card.call("_on_send")
	_out["w3_cancels"] = _calls_since(n, "cancel:")
	_out["w3_sends"] = _calls_since(n, "send:")
	_out["w3_latch"] = bool(_main.get("_awaiting_end_turn_confirmation"))
	_out["w3_input_while_out"] = bool(_line().editable)
	_api.answer("cancel:" + march, cc5["cancel_reply"])
	await _wait_frames(3)
	_out["w3_arrow_keys"] = _arrow_keys()
	_out["w3_ap"] = int(_main.get("actions_remaining"))
	_out["w3_input_after"] = bool(_line().editable)
	_out["w3_tail"] = _terminal_tail(600)

	# w4 — CC-X15: the Orders tab's Cancel rides the same road.
	var ledger_subject := str(cc5["ledger_subject"])
	_fresh("")
	_main.set("_awaiting_end_turn_confirmation", true)
	var top = _main.get("top_bar")
	var ledger = top.get("screens").get("ledger") if top != null else null
	n = _api.calls.size()
	if ledger != null:
		ledger.call("_on_meta_clicked", "cancel:" + ledger_subject)
	_out["w4_cancels"] = _calls_since(n, "cancel:")
	_out["w4_latch"] = bool(_main.get("_awaiting_end_turn_confirmation"))
	_api.answer("cancel:" + ledger_subject, cc5["ledger_reply"])
	await _wait_frames(3)
	_out["w4_arrow_keys"] = _arrow_keys()
	_out["w4_ap"] = int(_main.get("actions_remaining"))

	# w5 — `.` walks the corps with nothing to do: the camera on each, and
	# (the line empty) he is selected; the busy are skipped; it wraps.
	_fresh("")
	# Zoomed in: at the whole-Europe fit the camera is clamped and cannot
	# turn to anyone.
	map.call("_set_camera_zoom_level", 1.6)
	await _wait_frames(3)
	_line().grab_focus()
	var idle: Array = cc5["idle"]
	var walk: Array = []
	var cams: Array = []
	for i in range(idle.size() + 1):
		_key(KEY_PERIOD, 46)
		walk.append(_selected())
		var feet: Dictionary = map.call("_order_piece_feet", _selected())
		var cam: Vector2 = (map.get("map_camera") as Camera2D).position
		cams.append(feet.get("feet", Vector2(-9999, -9999)).distance_to(cam) if not feet.is_empty() else -1.0)
	_out["w5_walk"] = walk
	_out["w5_cam_dist"] = cams
	_out["w5_line"] = str(_line().text)
	# …and with the line unfocused, the bare key.
	_main.get_viewport().gui_release_focus()
	_key(KEY_PERIOD, 46)
	_out["w5_unfocused"] = _selected()
	# Alt+`.` over a draft: the camera moves, nothing is selected, the draft
	# is untouched.
	var draft := "Ney, march to "
	_fresh(draft)
	_line().grab_focus()
	var cam0: Vector2 = (map.get("map_camera") as Camera2D).position
	_key_mod(KEY_PERIOD, 46, true)
	_out["w5_alt_selected"] = _selected()
	_out["w5_alt_line"] = str(_line().text)
	_out["w5_alt_camera_moved"] = (map.get("map_camera") as Camera2D).position.distance_to(cam0) > 1.0
	_fresh("")
	map.call("fit_europe")
	await _wait_frames(3)

	# w6 — the group: Ctrl-click gathers (and lets go of) our corps.
	var members: Array = cc5["toggle_members"]
	_gather(members)
	_out["w6_group"] = (_main.get("_order_group") as Array).duplicate()
	_out["w6_rings"] = int(_layer().get("rings", 0))
	_out["w6_strip"] = str(_main.call("order_strip_text"))
	_ctrl_click(_home_of(str(members[1])), str(members[1]))
	_out["w6_after_drop"] = (_main.get("_order_group") as Array).duplicate()
	_ctrl_click(_home_of(str(members[0])), str(members[0]))
	_out["w6_after_second_drop"] = (_main.get("_order_group") as Array).duplicate()
	_out["w6_selected_after_second_drop"] = _selected()
	_key(KEY_ESCAPE)
	_out["w6_after_esc"] = (_main.get("_order_group") as Array).duplicate()
	_out["w6_selected_after_esc"] = _selected()
	# w6b — Esc lets a whole group go: the line's Esc and the map's, one step
	# each (and never the pause menu with it).
	_gather(members)
	_main.call("_clear_suggestions")
	_line().grab_focus()
	_key(KEY_ESCAPE)
	_out["w6b_after_line_esc"] = (_main.get("_order_group") as Array).duplicate()
	_gather(members)
	_main.get_viewport().gui_release_focus()
	var pause = _main.get("pause_menu")
	_key(KEY_ESCAPE)
	_out["w6b_after_map_esc"] = (_main.get("_order_group") as Array).duplicate()
	_out["w6b_pause_open"] = bool(pause.visible) if pause != null else false
	if pause != null and pause.visible:
		pause.call("close_menu")

	# w7 / w8 / w9 — the group card and its Send: a real run that stops at a
	# question, a line refused on the wire, and a run that sends them all.
	for tag in ["w7", "w8", "w9"]:
		if cc5.has(tag):
			await _group_send(cc5, cc5[tag], tag)
	_board(cc5["board"])
	_fresh("")
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

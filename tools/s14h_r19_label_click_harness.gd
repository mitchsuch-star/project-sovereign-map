extends SceneTree
# S14G-19 (Pre-Deploy S14h part 2, October 26, 2026) - a map LABEL is a click
# target, DRIVEN.
#
#   $env:S14H_R19_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/s14h_r19_label_click_harness.gd
#
# The spec (written by tests/test_s14h_p2_row19.py) carries the REAL boot
# board with five corps of ours stacked on one province -- `game_state` from
# GET /test and `topology` from GET /map_topology -- plus the names to click
# ("out" is the result path). The harness boots the REAL `main.tscn` behind
# the CC harness's API stub, hands the map the board, lets the label layer
# lay the furniture out, then reads the VISIBLE label's screen centre and
# pushes a real mouse press and release there, through `root.push_input`
# (the engine's own order): the hover must name the label's man, and the
# click must select him -- not open the province under the text.
#
# Safety rails (the CC harness's): UiSettings on an in-memory ConfigFile; the
# result JSON is written on every exit path.

const HARD_FRAME_LIMIT := 1500


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
	UiSettings._persist = false   # Session UI-5: the harness flag — writes stay in memory, and the scripted day keeps its one End Turn
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
		"scenario":
			_phase = "scenario_running"
			_scenario.call_deferred()
		"scenario_running":
			pass   # the coroutine moves the phase on when it is done
		"done":
			_finish()


func _boot():
	var path := OS.get_environment("S14H_R19_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_fatal = "S14H_R19_SPEC missing or not a JSON object"
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


func _map():
	return _main.get("map_area")


func _run():
	var map = _map()
	if map != null and map.has_method("set_region_topology"):
		map.set_region_topology(_spec.get("topology", {}))
	var gs: Dictionary = _spec.get("game_state", {})
	_main.call("_reset_frontend_state_for_world_swap", true)
	_main.call("_update_map_from_game_state", gs.duplicate(true))
	_main.set("_last_game_state", gs.duplicate(true))
	# Headless the root is 64 px square: give the map a real screen.
	root.mode = Window.MODE_WINDOWED
	root.size = Vector2i(1600, 900)
	_phase = "scenario"
	_wait = 6


func _wait_frames(n: int) -> void:
	for _i in range(n):
		await process_frame


# ── input, as the CC harness pushes it ─────────────────────────────────────

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


func _hover(at: Vector2) -> void:
	# Twice: the map reads the control under the cursor as the GUI left it
	# after the PREVIOUS motion (the GUI updates its hover after `_input`).
	_push_motion(at, false)
	_push_motion(at, false)


func _uncovered(map, at: Vector2) -> bool:
	_hover(at)
	var over = root.gui_get_hovered_control()
	return over == map or (over != null and map.is_ancestor_of(over))


# ── the label under test ───────────────────────────────────────────────────

func _label_of_kind(kind: String, text: String):
	"""The VISIBLE furniture label of `kind` whose text is `text` ('' = any)."""
	var layer = _map().get("force_layer")
	for c in layer.get_children():
		if c is Label and c.has_meta("furniture_kind") \
				and str(c.get_meta("furniture_kind")) == kind \
				and c.visible and (text == "" or (c as Label).text == text):
			return c
	return null


func _label_world_rect(label: Label) -> Rect2:
	# Where the label layer measures a furniture item (map_label_layer.gd
	# `_item_world_rect`): its global position in the SubViewport canvas
	# (= world coords) and the larger of its size and its minimum size.
	var minimum := label.get_combined_minimum_size()
	var sz := Vector2(maxf(label.size.x, minimum.x), maxf(label.size.y, minimum.y))
	return Rect2(label.global_position, sz)


func _inside_any_piece(map, world_point: Vector2) -> bool:
	for hb in map.get("marshal_hitboxes"):
		if (hb["rect"] as Rect2).has_point(world_point):
			return true
	return false


func _fresh() -> void:
	"""An empty, open line and nothing selected - the state a plain click on a
	piece of ours selects him from (the CC harness's `_fresh`, cut down)."""
	_main.set("_offered_command", "")
	_main.set("_parked_draft", "")
	_main.set("pending_relay_command", "")
	_main.set("_awaiting_end_turn_confirmation", false)
	_main.set("_chip_command_in_flight", false)
	_main.call("set_input_enabled", true)
	_main.call("_clear_order_selection")
	var line = _main.get("command_input")
	line.text = ""
	_main.call("_on_command_text_changed", line.text)
	var map = _map()
	map.set("last_click_marshal", "")
	map.set("last_click_shift", false)
	map.set("last_click_ctrl", false)
	map.set("last_click_fogged", "")


func _click_point_of(map, label: Label) -> Dictionary:
	"""A point of the label's own text box that no piece covers and no panel
	sits over - the centre first (the brief's click), else the first clear
	sample. {} when the label has none."""
	var rect := _label_world_rect(label)
	for fy in [0.5, 0.3]:
		for fx in [0.5, 0.2, 0.8, 0.35, 0.65]:
			var world := rect.position + Vector2(rect.size.x * fx, rect.size.y * fy)
			var at: Vector2 = map.call("screen_point_of_world", world)
			if not Rect2(Vector2.ZERO, Vector2(root.size)).has_point(at):
				continue
			if _inside_any_piece(map, world):
				continue
			if not _uncovered(map, at):
				continue
			return {"world": world, "at": at, "centre": fx == 0.5 and fy == 0.5}
	return {}


func _read_label_click(tag: String, kind: String, text: String, expect_key: String) -> void:
	"""Hover the label's text, then press and release a real left click there:
	record what the map named and what the client selected."""
	var map = _map()
	_fresh()
	var label = _label_of_kind(kind, text)
	_out[tag + "_found"] = label != null
	_out[tag + "_expected"] = expect_key
	if label == null:
		return
	_out[tag + "_text"] = (label as Label).text
	var rect := _label_world_rect(label)
	_out[tag + "_rect"] = [rect.position.x, rect.position.y, rect.size.x, rect.size.y]
	var pick := _click_point_of(map, label)
	_out[tag + "_clear_point"] = not pick.is_empty()
	if pick.is_empty():
		return
	var at: Vector2 = pick["at"]
	_out[tag + "_centre"] = bool(pick["centre"])
	_out[tag + "_point"] = [at.x, at.y]
	_hover(at)
	_out[tag + "_hovered_marshal"] = str((map.get("hovered_marshal") as Dictionary).get("name", ""))
	_out[tag + "_hovered_region"] = str(map.get("hovered_region"))
	_push_left(at, true)
	_push_left(at, false)
	_out[tag + "_selected"] = str(_main.get("_order_marshal"))
	_out[tag + "_last_click_marshal"] = str(map.get("last_click_marshal"))
	var panel = _main.get("region_panel")
	_out[tag + "_panel_open"] = panel != null and panel.visible
	_fresh()


func _scenario() -> void:
	var map = _map()
	map.visible = true
	_main.call("_minimize_terminal")   # the bottom-left is the map's again
	map.call("fit_europe")
	# The furniture is laid out once the zoom settles (map_label_layer.gd).
	for _i in range(240):
		await process_frame
		if map.call("is_zoom_settled"):
			break
	await _wait_frames(12)
	var layer = map.get("map_label_layer")
	_out["layout_ran"] = layer != null and not (layer.get("_laid_out_key") as Array).is_empty()
	_out["label_hitboxes"] = (map.get("label_hitboxes") as Array).size()
	var stack: Dictionary = _spec.get("stack", {})
	_read_label_click("stack", "stack", str(stack.get("text", "")), str(stack.get("lead", "")))
	var name_spec: Dictionary = _spec.get("name", {})
	_read_label_click("name", "name", str(name_spec.get("text", "")), str(name_spec.get("key", "")))
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

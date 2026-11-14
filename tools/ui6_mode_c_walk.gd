extends SceneTree
# Session UI-6 - the Mode C walk (November 13, 2026) - modeled on
# tools/ui5_mode_c_walk.gd and tools/cc3_mode_c_walk.gd.
#
#   $env:SOVEREIGN_PORT   = "8006"        # a sandboxed backend listening there (never 8005)
#   $env:UI6_WALK_OUT     = "<abs dir>"   # frames + walk.json land here
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/ui6_mode_c_walk.gd
#
# The REAL main.tscn against a live sandboxed backend. Steps: boot, the marshal
# row, a card digit, a right-click order, the readback, the Generals'
# master-detail ("On the map"), the 2.0 slim bar and its log drawer. Each step
# records {step, did, saw, ok} in walk.json["results"] (and a frame row in
# walk.json["steps"]), tolerates failure, and the walk never aborts.

const WALL_LIMIT_MS := 900000
const OUT_DEFAULT := "res://../../docs/audits/ui6_mode_c_2026_11_13"

var _main = null
var _out: Dictionary = {"steps": [], "errors": [], "results": []}
var _dir := ""
var _t0 := 0
var _done := false
var _n := 0
var _subject := ""


func _init():
	UiSettings._cfg = ConfigFile.new()
	UiSettings._persist = false   # the harness flag: writes stay in memory
	# the player's defaults for the two UI-6 switches (a harness defaults them off)
	UiSettings._cfg.set_value("display", "readback", true)
	UiSettings._cfg.set_value("orders", "next_marshal_after_order", true)
	_t0 = Time.get_ticks_msec()
	process_frame.connect(_watchdog)
	_walk.call_deferred()


func _watchdog():
	if not _done and Time.get_ticks_msec() - _t0 > WALL_LIMIT_MS:
		_out["error"] = "wall-clock limit hit"
		_finish()


func _frames(n: int) -> void:
	for _i in range(n):
		await process_frame


func _secs(s: float) -> void:
	await create_timer(s).timeout
	await _frames(2)


func _api():
	return _main.get("api_client") if _main != null else null


func _api_idle() -> bool:
	var api = _api()
	if api == null:
		return true
	var queue = api.get("_request_queue")
	return not bool(api.get("_request_in_flight")) and (queue == null or queue.is_empty())


func _settle(limit_ms: int = 30000) -> void:
	var start := Time.get_ticks_msec()
	var calm := 0
	while Time.get_ticks_msec() - start < limit_ms:
		await process_frame
		calm = calm + 1 if _api_idle() else 0
		if calm >= 8:
			return


func _key(keycode: int, unicode: int = 0, shift: bool = false) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = keycode
		ev.physical_keycode = keycode
		ev.unicode = unicode
		ev.shift_pressed = shift
		ev.pressed = pressed
		root.push_input(ev)
	await _frames(4)


func _release_line() -> void:
	var line = _main.get("command_input")
	if line != null:
		line.release_focus()
	await _frames(3)


func _turn() -> int:
	return int(_main.get("current_turn")) if _main != null else 0


func _all_nodes(from: Node) -> Array:
	var out: Array = []
	var stack: Array = [from]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out


func _texts_under(from: Node, cap: int = 1600) -> String:
	if from == null:
		return ""
	var parts: Array = []
	for n in _all_nodes(from):
		if n is RichTextLabel and n.is_visible_in_tree():
			parts.append(n.get_parsed_text())
		elif n is Label and n.is_visible_in_tree() and str(n.text) != "":
			parts.append(str(n.text))
		elif n is Button and n.is_visible_in_tree() and str(n.text) != "":
			parts.append("[" + str(n.text) + "]")
	var s := "\n".join(parts)
	return s if s.length() <= cap else s.substr(0, cap) + " ..."


func _hold_window() -> void:
	if root.mode != Window.MODE_WINDOWED or root.size != Vector2i(1920, 1080):
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1920, 1080)
		root.position = Vector2i(5200, 20)
		await _frames(6)


func _press_text(scope: Node, first_line: String) -> bool:
	if scope == null:
		return false
	for b in _all_nodes(scope):
		if b is BaseButton and b.is_visible_in_tree() and not b.disabled and ("text" in b):
			var head := str(b.text).strip_edges().split("\n")[0].strip_edges()
			if head == first_line or head.begins_with(first_line):
				b.emit_signal("pressed")
				return true
	return false


func _clear_boot_overlays() -> void:
	for _i in range(6):
		var pressed := false
		var p = _main.get("incoming_proposal_popup")
		if p != null and p.visible:
			var dismiss = p.get("dismiss_btn")
			if dismiss != null and dismiss.visible and not dismiss.disabled:
				dismiss.emit_signal("pressed")
				pressed = true
		var ip = _main.get("interrupt_popup")
		if ip != null and ("visible" in ip) and bool(ip.visible):
			ip.visible = false
			pressed = true
		if not pressed:
			break
		await _frames(6)
		await _settle()


func _shot(name: String, note: String) -> void:
	await _hold_window()
	var park := InputEventMouseMotion.new()
	park.position = Vector2(-40, -40)
	park.global_position = park.position
	root.push_input(park, true)
	await _frames(4)
	_n += 1
	var img := root.get_texture().get_image()
	# jpg, as the runner's export globs *.jpg (the audits' frames are JPEGs)
	var file := "UI6_WALK_%02d_%s_2026_11_13.jpg" % [_n, name]
	var err := img.save_jpg(_dir.path_join(file), 0.88)
	_out["steps"].append({"step": name, "note": note, "frame": file, "saved": err == OK,
		"turn": _turn(), "ms": Time.get_ticks_msec() - _t0})


func _rec(step: String, did: String, saw: String, ok: bool, extra: Dictionary = {}) -> void:
	var row := {"step": step, "did": did, "saw": saw, "ok": ok}
	for k in extra:
		row[k] = extra[k]
	_out["results"].append(row)
	if not ok:
		_out["errors"].append({"turn": _turn(), "what": step + ": " + saw})


func _log_tail(chars: int = 500) -> String:
	var display = _main.get("output_display")
	var text: String = display.get_parsed_text() if display != null else ""
	return text.substr(maxi(0, text.length() - chars))


func _last_log_line() -> String:
	var lines := _log_tail(800).strip_edges().split("\n")
	for i in range(lines.size() - 1, -1, -1):
		if str(lines[i]).strip_edges() != "":
			return str(lines[i]).strip_edges()
	return ""


func _row_marshal_keys() -> Array:
	var row = _main.get("_marshal_row")
	if row != null and is_instance_valid(row) and row.has_method("shown_keys"):
		return row.call("shown_keys")
	return []


func _first_idle_key() -> String:
	var idle = _main.call("_idle_marshals") if _main.has_method("_idle_marshals") else []
	var shown := _row_marshal_keys()
	if idle is Array:
		for k in idle:
			if shown.has(k):
				return str(k)
		if not (idle as Array).is_empty():
			return str(idle[0])
	if not shown.is_empty():
		return str(shown[0])
	return ""


func _chip_for(key: String) -> Button:
	var row = _main.get("_marshal_row")
	if row == null or not is_instance_valid(row):
		return null
	for n in _all_nodes(row):
		if n is Button and n.is_visible_in_tree():
			# the chip's hover carries his name; fall back to the node name
			if str(n.name).findn(key) >= 0 or str(n.tooltip_text).findn(key) >= 0 \
					or str(n.text).findn(key) >= 0:
				return n
	return null


func _select_via_row(key: String) -> String:
	"""A click on his chip: push a real mouse click at its centre; else the
	row's own handler. Returns which road took it."""
	var chip := _chip_for(key)
	if chip != null:
		var at := chip.get_global_rect().get_center()
		for pressed in [true, false]:
			var ev := InputEventMouseButton.new()
			ev.button_index = MOUSE_BUTTON_LEFT
			ev.pressed = pressed
			ev.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
			ev.position = at
			ev.global_position = at
			root.push_input(ev, true)
			await _frames(2)
		await _frames(6)
		if str(_main.get("_order_marshal")) == key:
			return "chip click"
	_main.call("_on_marshal_chip_pressed", key)
	await _frames(8)
	return "row handler"


func _card() -> Node:
	return _main.get("_selection_card")


func _card_state() -> Dictionary:
	var card = _card()
	var out := {"visible": false, "marshal": "", "specs": 0, "lit": [], "title": ""}
	if card == null or not is_instance_valid(card):
		return out
	out["visible"] = bool(card.visible)
	out["marshal"] = str(card.call("current_marshal"))
	var specs = card.get("_specs")
	out["specs"] = (specs as Array).size() if specs is Array else 0
	var lit: Array = []
	for n in _all_nodes(card):
		if n is Button and str(n.name).begins_with("Slot") and not n.disabled:
			lit.append(int(str(n.name).substr(4)))
	lit.sort()
	out["lit"] = lit
	out["title"] = _texts_under(card, 160)
	return out


func _readback_text() -> String:
	var rb = _main.get("_readback_row")
	if rb == null or not is_instance_valid(rb):
		return "(no readback row)"
	if not rb.visible:
		return "(row hidden)"
	return rb.get_parsed_text()


func _read_line(step_name: String, text: String, tag: String) -> void:
	var input = _main.get("command_input")
	var saw := ""
	var ok := false
	if input == null or _main.get("_readback_row") == null:
		_rec(step_name, "typed '" + text + "'", "no command line or readback row", false)
		return
	input.grab_focus()
	input.text = text
	input.caret_column = text.length()
	_main.call("_readback_changed", text)   # what the line's text_changed does
	await _secs(0.8)
	await _settle(8000)
	await _secs(0.3)
	saw = _readback_text()
	ok = saw != "(row hidden)" and saw != "(no readback row)"
	_rec(step_name, "typed '" + text + "', waited ~0.8 s", saw, ok)
	await _shot(tag, "readback of '" + text + "'")


func _clear_line() -> void:
	var input = _main.get("command_input")
	if input != null:
		input.text = ""
		_main.call("_readback_changed", "")
	await _frames(6)


func _walk() -> void:
	var dir_env := OS.get_environment("UI6_WALK_OUT")
	_dir = dir_env if dir_env != "" else ProjectSettings.globalize_path(OUT_DEFAULT)
	DirAccess.make_dir_recursive_absolute(_dir)
	root.mode = Window.MODE_WINDOWED
	root.position = Vector2i(5200, 20)
	root.size = Vector2i(1920, 1080)
	await _frames(4)
	var packed: PackedScene = load("res://scenes/main.tscn")
	_main = packed.instantiate()
	root.add_child(_main)
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < 90000:
		await process_frame
		if bool(_main.get("_initial_map_bootstrapped")) and _main.get("command_input").editable:
			break
	await _settle()
	_out["backend"] = Utils.backend_url()
	_out["booted"] = bool(_main.get("_initial_map_bootstrapped"))
	await _frames(10)
	await _clear_boot_overlays()

	# 1 - boot
	var keys := _row_marshal_keys()
	_rec("boot", "booted the real main.tscn and cleared the boot overlays",
		"booted=%s turn=%d row chips=%s" % [str(_out["booted"]), _turn(), str(keys)],
		bool(_out["booted"]))
	await _shot("boot", "the war room after the backend's first board")

	# 2 - the marshal row
	_subject = _first_idle_key()
	if _subject == "":
		_rec("marshal_row", "looked for an idle marshal in the row", "none found", false)
		await _shot("marshal_row", "no marshal to select")
	else:
		var road := await _select_via_row(_subject)
		await _settle(15000)
		await _frames(10)
		var cs := _card_state()
		var sel := str(_main.get("_order_marshal"))
		var okc: bool = sel == _subject and bool(cs["visible"])
		_rec("marshal_row", "selected %s through the row (%s)" % [_subject, road],
			"selected=%s card visible=%s slots=%d lit=%s" % [sel, str(cs["visible"]), int(cs["specs"]), str(cs["lit"])],
			okc, {"card": cs})
		await _shot("marshal_row", "the selection card for " + _subject + ", its seven slots")

	# 3 - a digit
	var digit_slot := 0
	var cs3 := _card_state()
	for want in [3, 1, 2, 4, 5, 6]:
		if (cs3["lit"] as Array).has(want):
			digit_slot = want
			break
	var line = _main.get("command_input")
	if digit_slot == 0 or line == null:
		_rec("digit", "looked for a lit card slot", "none lit (card=%s)" % str(cs3), false)
		await _shot("digit", "no lit slot")
	else:
		await _release_line()
		if line.text != "":
			line.text = ""
		var before := _last_log_line()
		await _key(KEY_0 + digit_slot, 48 + digit_slot)
		await _settle(60000)
		await _frames(10)
		var after := _last_log_line()
		var live: bool = str(_main.get("_order_marshal")) != "" or after != before
		_rec("digit", "pushed digit %d with %s selected and the line empty" % [digit_slot, _subject],
			"log last line: '%s' (changed=%s) selected_now=%s ap=%s" % [after, str(after != before),
				str(_main.get("_order_marshal")), str(_main.get("actions_remaining"))],
			true, {"slot": digit_slot, "log_tail": _log_tail(500)})
		await _shot("digit", "slot %d by its digit; the reply in the log" % digit_slot)
		if not live:
			_out["errors"].append({"turn": _turn(), "what": "digit: neither a selection nor a new log line"})

	# 4 - right-click order
	var key4 := _first_idle_key()
	if key4 == "":
		key4 = _subject
	if key4 == "":
		_rec("right_click", "looked for a marshal", "none", false)
	else:
		if str(_main.get("_order_marshal")) != key4:
			await _release_line()
			await _select_via_row(key4)
		await _settle(15000)
		await _frames(8)
		var reach: Dictionary = _main.get("_order_reach") if _main.get("_order_reach") is Dictionary else {}
		var rows = reach.get("reach", {})
		var best := ""
		var best_t := 9999
		var loc := str((_main.call("_marshal_entry", key4) as Dictionary).get("location", ""))
		if rows is Dictionary:
			for region in rows:
				var t := int((rows[region] as Dictionary).get("turns", 99))
				if str(region) != loc and t < best_t:
					best_t = t
					best = str(region)
		var map = _main.get("map_area")
		if best == "" or map == null:
			_rec("right_click", "looked for a province in %s's reach" % key4,
				"none (reach keys=%d)" % (rows.size() if rows is Dictionary else 0), false)
			await _shot("right_click", "no province in reach")
		else:
			map.emit_signal("order_context_requested", best, "")
			await _frames(10)
			await _settle(15000)
			await _frames(10)
			var oc = _main.get("order_card")
			var open: bool = oc != null and oc.visible
			var title: String = str(oc.get("title_label").text) if open and oc.get("title_label") != null else ""
			var cmd: String = str(oc.call("command")) if open and oc.has_method("command") else ""
			_rec("right_click", "right-clicked %s next to %s (order_context_requested)" % [best, key4],
				"order card open=%s title='%s' command='%s'" % [str(open), title, cmd], open,
				{"province": best})
			await _shot("right_click_card", "the march card for " + best)
			if open:
				var sendb = oc.get("send_button")
				if sendb != null and not sendb.disabled and sendb.visible:
					sendb.emit_signal("pressed")
				elif oc.has_method("_on_send"):
					oc.call("_on_send")
				await _settle(60000)
				await _frames(10)
				var sent := _last_log_line()
				_rec("right_click_send", "pressed the card's send", "log last line: '%s'; card still open=%s" % [
					sent, str(oc.visible)], true, {"log_tail": _log_tail(500)})
				await _shot("right_click_sent", "the march sent; the reply in the log")
				if oc.visible and oc.has_method("close_card"):
					oc.call("close_card")
					await _frames(4)

	# 4b - a marshal's objection to the march stands as a modal: answered with
	# "Cancel the Order" (no AP, no trust spent), so the steps after it run
	# against an open line (the first walk's readback, Generals and Esc steps all
	# met Davout's Advice still open)
	if _press_text(root, "Cancel the Order"):
		await _settle(30000)
		await _frames(10)
		_rec("objection_answered", "answered the marshal's objection: Cancel the Order",
			"log last line: '%s'" % _last_log_line(), true)
		await _shot("objection_answered", "the objection answered; the line open again")

	# 5 - the readback
	await _release_line()
	if _main.has_method("_clear_order_selection"):
		_main.call("_clear_order_selection")
	await _frames(6)
	await _read_line("readback_ney", "Ney, attack Mack", "readback_ney")
	await _clear_line()
	await _read_line("readback_fog", "Kutuzov, retreat", "readback_fog")
	await _clear_line()
	await _read_line("readback_unknown", "Zorglub, retreat", "readback_unknown")
	await _clear_line()
	await _release_line()
	await _shot("readback_cleared", "the line cleared, the reading gone")

	# 6 - Generals
	await _release_line()
	await _key(KEY_G, 103)
	await _settle(15000)
	await _frames(12)
	var tb = _main.get("top_bar")
	var gen = tb.screens.get("generals", null) if tb != null else null
	var gopen: bool = gen != null and bool(gen.visible) and str(tb.get_active_screen()) == "generals"
	if not gopen and _main.has_method("_ui6_open_generals"):
		_main.call("_ui6_open_generals")
		await _settle(15000)
		await _frames(12)
		gopen = gen != null and bool(gen.visible)
	var roster = gen.get("_roster_names") if gen != null else null
	var nrows: int = (roster as Array).size() if roster is Array else -1
	_rec("generals_open", "pressed G", "generals visible=%s roster rows=%d" % [str(gopen), nrows],
		gopen and nrows != 0)
	await _shot("generals", "the master-detail roster")
	if gopen:
		var pick := _first_idle_key()
		if pick != "" and gen.has_method("select_marshal"):
			gen.call("select_marshal", pick)
			await _frames(10)
		await _release_line()
		if str(_main.get("_order_marshal")) != "":
			_main.call("_clear_order_selection")
			await _frames(4)
		var pressed := _press_text(gen, "On the map")
		await _frames(2)
		await _settle(10000)
		await _frames(12)
		var closed: bool = str(tb.get_active_screen()) != "generals"
		var selnow := str(_main.get("_order_marshal"))
		_rec("generals_on_the_map", "pressed 'On the map' for %s" % pick,
			"button found=%s screen closed=%s selected=%s" % [str(pressed), str(closed), selnow],
			pressed and closed and selnow != "")
		await _shot("generals_on_the_map", "the screen shut, he is selected on the map")
		if not closed:
			tb.toggle_screen("generals")
			await _frames(8)

	# 7 - the compact bar at Interface Scale 2.0
	var old_scale: float = UiSettings.get_ui_scale()
	await _release_line()
	if _main.has_method("_clear_order_selection"):
		_main.call("_clear_order_selection")
	_main.call("_apply_ui_scale", 2.0, false)   # the Settings slider's own road (+ UiSettings)
	UiSettings.set_ui_scale(2.0)
	await _frames(20)
	await _secs(0.5)
	var bar_on: bool = bool(_main.call("_ui5_bar_mode"))
	_rec("compact_bar", "set Interface Scale 2.0 (was %.2f)" % old_scale,
		"compact_view=%s slim bar mode=%s desk=%s" % [str(Utils.compact_view()), str(bar_on),
			str(_main.get("_desk_mode_now"))], bar_on)
	await _shot("bar_2_0", "Interface Scale 2.0: the slim bar")
	_main.call("_ui6_toggle_log")   # the bar's reply line / more menu's Open the log
	await _frames(14)
	var log_open: bool = bool(_main.get("_ui5_log_open"))
	_rec("compact_log_open", "toggled the log drawer open (reply-line road)",
		"log drawer open=%s" % str(log_open), log_open)
	await _shot("bar_log_open", "the log drawer open above the line")
	await _release_line()
	await _key(KEY_ESCAPE)
	await _frames(10)
	var log_after: bool = bool(_main.get("_ui5_log_open"))
	if log_after:
		_main.call("_ui5_close_log")   # note: Esc alone did not fold it
		await _frames(8)
	_rec("compact_log_esc", "pushed Esc", "drawer open after Esc=%s%s" % [str(log_after),
		" (closed by hand)" if log_after else ""], not log_after)
	await _shot("bar_log_closed", "the drawer folded")
	_main.call("_apply_ui_scale", old_scale, false)
	UiSettings.set_ui_scale(old_scale)
	await _frames(16)
	_rec("scale_restored", "restored Interface Scale", "scale=%.2f bar_mode=%s" % [
		root.content_scale_factor, str(_main.call("_ui5_bar_mode"))], absf(root.content_scale_factor - old_scale) < 0.01)
	await _shot("scale_restored", "the scale back")
	_finish()


func _finish():
	if _done:
		return
	_done = true
	_out["ms"] = Time.get_ticks_msec() - _t0
	_out["final_turn"] = _turn()
	var path := _dir.path_join("walk.json") if _dir != "" else ""
	if path != "":
		var f := FileAccess.open(path, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_out, "  "))
			f.close()
	quit(1 if _out.has("error") else 0)

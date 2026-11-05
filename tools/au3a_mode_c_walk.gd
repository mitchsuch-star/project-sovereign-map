extends SceneTree
# AU-3a the Mode C walk on 8007 (`docs/AUTHORITY_CURRENCY_SPEC.md` §5.3, §5.5,
# the landing record §6.5; November 5, 2026) — modeled on tools/re5_mode_c_walk.gd.
#
#   $env:SOVEREIGN_PORT       = "8007"        # a sandboxed backend listening there
#   $env:AU3A_WALK_OUT        = "<abs dir>"   # frames + walk.json land here
#   $env:AU3A_DECREE_SAVE     = "au3a_decree.json"    # chapter B's crafted save
#   $env:AU3A_TEDEUM_SAVE     = "au3a_te_deum.json"   # chapter D's crafted save
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/au3a_mode_c_walk.gd
#
# The REAL `main.tscn` with the REAL APIClient against a live sandboxed backend
# (never 8005 or 8006 — the player's ports). Every key is pushed into the
# viewport as an ENGINE event, every typed line goes down the command line's
# own road, every button is pressed by emitting its own `pressed` signal and
# every desk chip as the page's own `meta_clicked`; no operating-system input,
# the window parked off the desktop. Each step is recorded in walk.json.
#
#   Chapter A — the boot
#     chip            the top bar with the Authority chip: its text and tooltip
#   Chapter C — the Word (typed on the boot, before any save is loaded)
#     objection_word  `Ney, defend`: Ney objects; the dialog's five answers
#     word_given      "By My Word" pressed: the reply's lines and the chip
#   Chapter B — the Decree (crafted save: the Remounts standing, authority 90)
#     letter_decree   the letter from the desk, the third answer "Decree it"
#     decreed         the Decree pressed: the response lines and the chip
#   Chapter D — the Te Deum (crafted save: the truce with Austria on its last
#               turn, war score +30, authority 88)
#     te_deum_before  the board before the end turn (the chip at 88)
#     te_deum         the end turn: the Te Deum lands, the chip +4 and its tooltip
#     te_deum_dispatch  the morning's Dispatch lines
#     te_deum_gazette   the Gazette (Le Moniteur), when its screen opens

const WALL_LIMIT_MS := 1200000
const OUT_DEFAULT := "res://../../docs/audits/au3a_mode_c_2026_11_05"
const TEXT_CAP := 2400

var _main = null
var _out: Dictionary = {"steps": [], "turns": {}, "errors": []}
var _dir := ""
var _t0 := 0
var _done := false
var _n := 0


func _init():
	UiSettings._cfg = ConfigFile.new()
	_t0 = Time.get_ticks_msec()
	process_frame.connect(_watchdog)
	_walk.call_deferred()


func _watchdog():
	if not _done and Time.get_ticks_msec() - _t0 > WALL_LIMIT_MS:
		_out["error"] = "wall-clock limit hit"
		_finish()


# ── the engine's own roads ───────────────────────────────────────────────────

func _frames(n: int) -> void:
	for _i in range(n):
		await process_frame


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


func _key(keycode: int, unicode: int = 0) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = keycode
		ev.physical_keycode = keycode
		ev.unicode = unicode
		ev.pressed = pressed
		root.push_input(ev)
	await _frames(3)


func _type(line: String) -> void:
	var input = _main.get("command_input")
	input.text = line
	input.caret_column = line.length()
	_main.call("_execute_command")
	await _settle(90000)
	await _frames(6)


func _turn() -> int:
	return int(_main.get("current_turn")) if _main != null else 0


func _terminal_tail(chars: int = 1200) -> String:
	var display = _main.get("output_display")
	var text: String = display.get_parsed_text() if display != null else ""
	return text.substr(maxi(0, text.length() - chars))


func _cap(text: String) -> String:
	return text if text.length() <= TEXT_CAP else text.substr(0, TEXT_CAP) + " …"


func _all_nodes(from: Node) -> Array:
	var out: Array = []
	var stack: Array = [from]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out


func _texts_under(from: Node) -> String:
	var parts: Array = []
	for n in _all_nodes(from):
		if n is RichTextLabel and n.is_visible_in_tree():
			parts.append(n.get_parsed_text())
		elif n is Label and n.is_visible_in_tree() and str(n.text) != "":
			parts.append(str(n.text))
	return "\n".join(parts)


func _press_text(scope: Node, first_line: String) -> bool:
	# The capture harness's road: the button's own `pressed` — matched on the
	# first line of its text (the letter's buttons are two-line priced).
	for b in _all_nodes(scope):
		if b is BaseButton and b.is_visible_in_tree() and not b.disabled and ("text" in b):
			var head := str(b.text).strip_edges().split("\n")[0].strip_edges()
			if head == first_line:
				b.emit_signal("pressed")
				return true
	return false


func _hold_window() -> void:
	# A load's refit can hand the window to the desktop; every frame is taken
	# at the walk's one size, parked off the desktop.
	if root.mode != Window.MODE_WINDOWED or root.size != Vector2i(1920, 1080):
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1920, 1080)
		root.position = Vector2i(5200, 20)
		await _frames(6)


func _objection_open() -> bool:
	var od = _main.get("objection_dialog") if _main != null else null
	return od != null and ("visible" in od) and bool(od.visible)


func _clear_overlays() -> void:
	# What a player dismisses before reading a screen: the enemy phase's
	# report (its own Continue), the battle diorama, a court's envoy, the
	# envoys' panel, a marshal's interrupt. The letter popup, the objection
	# dialog and the screens are left as the scene has them.
	for _i in range(8):
		var pressed := false
		for n in _all_nodes(root):
			var scr = n.get_script() if n is Object and n.has_method("get_script") else null
			if scr == null or not str(scr.resource_path).ends_with("battle_diorama.gd"):
				continue
			if not (("visible" in n) and bool(n.visible)):
				continue
			if _press_text(n, "Close"):
				pass
			elif n.has_method("_skip_to_final"):
				n.call("_skip_to_final")
			else:
				var ev := InputEventMouseButton.new()
				ev.button_index = MOUSE_BUTTON_LEFT
				ev.pressed = true
				ev.position = Vector2(960, 540)
				ev.global_position = ev.position
				root.push_input(ev, true)
				ev = InputEventMouseButton.new()
				ev.button_index = MOUSE_BUTTON_LEFT
				ev.pressed = false
				ev.position = Vector2(960, 540)
				ev.global_position = ev.position
				root.push_input(ev, true)
			pressed = true
			break
		var mb = _mailbox()
		if mb != null and mb.visible:
			var btn = mb.get("close_btn")
			if btn != null:
				btn.emit_signal("pressed")
				pressed = true
			else:
				mb.visible = false
		var p = _popup()
		if p != null and p.visible:
			var data = p.get("current_data")
			var is_letter: bool = data is Dictionary and bool(data.get("is_moment", false))
			if not is_letter:
				var dismiss = p.get("dismiss_btn")
				if dismiss != null and not dismiss.disabled and dismiss.visible:
					dismiss.emit_signal("pressed")
					pressed = true
		var ep = _main.get("enemy_phase_dialog")
		if ep != null and ("visible" in ep) and bool(ep.visible):
			if _press_text(ep, "Continue"):
				pressed = true
			elif _press_text(root, "Continue"):
				pressed = true
			else:
				ep.visible = false
		var ip = _main.get("interrupt_popup")
		if ip != null and ("visible" in ip) and bool(ip.visible):
			var bc = ip.get("button_container")
			var taken := ""
			if bc != null:
				for c in bc.get_children():
					if c is BaseButton and not c.disabled and c.visible:
						taken = str(c.text)
						c.emit_signal("pressed")
						break
			if taken == "":
				ip.visible = false
			var overlays: Array = _out.get("overlays", [])
			overlays.append({"turn": _turn(), "kind": "interrupt", "marshal": str(ip.get("current_marshal")), "took": taken})
			_out["overlays"] = overlays
			pressed = true
		if not pressed:
			break
		await _frames(6)
		await _settle()


func _shot(name: String, note: String, extra: Dictionary = {}, clear: bool = true) -> void:
	if clear:
		await _clear_overlays()
	await _hold_window()
	var park := InputEventMouseMotion.new()
	park.position = Vector2(-40, -40)
	park.global_position = park.position
	root.push_input(park, true)
	await _frames(4)
	_n += 1
	var img := root.get_texture().get_image()
	var file := "AU3A_%02d_%s_2026_11_05.jpg" % [_n, name]
	var err := img.save_jpg(_dir.path_join(file), 0.86)
	var row := {"step": name, "note": note, "frame": file, "saved": err == OK, "turn": _turn(),
		"ms": Time.get_ticks_msec() - _t0}
	for k in extra:
		row[k] = extra[k]
	_out["steps"].append(row)


func _note_error(what: String) -> void:
	_out["errors"].append({"turn": _turn(), "what": what})


# ── the screens ──────────────────────────────────────────────────────────────

func _top_bar():
	return _main.get("top_bar")


func _dispatch():
	return _main.get("dispatch_view")


func _popup():
	return _main.get("incoming_proposal_popup")


func _mailbox():
	return _main.get("mailbox_panel")


func _chip() -> Dictionary:
	# the top bar's code-built AuthorityChip (AU-1): its text and tooltip
	var tb = _top_bar()
	var chip = tb.get("authority_chip") if tb != null else null
	if chip == null:
		return {"text": "", "tooltip": "", "present": false}
	return {"text": str(chip.text), "tooltip": str(chip.tooltip_text), "present": true,
		"visible": chip.is_visible_in_tree()}


func _open_dispatch() -> void:
	var dv = _dispatch()
	if dv != null and dv.visible:
		return
	await _key(KEY_R, 114)
	await _frames(6)
	dv = _dispatch()
	if dv != null and not dv.visible and _top_bar() != null:
		_top_bar().call("toggle_screen", "dispatch")
		await _frames(6)
	await _settle()
	await _frames(4)


func _close_dispatch() -> void:
	var dv = _dispatch()
	if dv != null and dv.visible:
		dv.call("close_view")
		await _frames(4)


func _close_modals() -> void:
	var mb = _mailbox()
	if mb != null and mb.visible:
		var btn = mb.get("close_btn")
		if btn != null:
			btn.emit_signal("pressed")
		else:
			mb.visible = false
		await _frames(6)
	await _close_dispatch()


func _dispatch_text() -> String:
	var dv = _dispatch()
	if dv == null:
		return ""
	var label = dv.get("content_label")
	return str(label.get_parsed_text()) if label != null else ""


func _open_correspondence() -> void:
	await _open_dispatch()
	var dv = _dispatch()
	if dv == null:
		return
	if bool(dv.call("has_correspondence")):
		if not _press_text(dv, str(dv.get("correspondence_button").text).strip_edges()):
			dv.call("open_correspondence")
	else:
		dv.call("open_correspondence")
	await _settle()
	await _frames(8)


func _correspondence_text() -> String:
	var dv = _dispatch()
	if dv == null:
		return ""
	var box = dv.get("corr_box")
	return _texts_under(box) if box != null else ""


func _corr() -> Dictionary:
	var dv = _dispatch()
	if dv == null:
		return {}
	var c = dv.get("_corr")
	return c if c is Dictionary else {}


func _desk_rows() -> Array:
	var out: Array = []
	for row in (_corr().get("standing", []) as Array):
		if row is Dictionary:
			out.append(row)
	return out


func _desk_chip() -> String:
	# The desk's "Read the letter ▸" chip of the first AFFAIR standing: the
	# page's own url `corr:read:<mailbox id>`.
	for row in _desk_rows():
		if str(row.get("register", "")) == "affair" and int(row.get("mailbox_id", 0) or 0) > 0:
			return "corr:read:%d" % int(row.get("mailbox_id"))
	return ""


func _read_letter_from_desk() -> bool:
	var dv = _dispatch()
	var box = dv.get("corr_box") if dv != null else null
	if box == null:
		return false
	var url := _desk_chip()
	if url == "":
		return false
	for n in _all_nodes(box):
		if n is RichTextLabel and str(n.text).contains(url):
			n.emit_signal("meta_clicked", url)
			break
	await _settle()
	await _frames(10)
	var p = _popup()
	return p != null and p.visible


func _letter_read() -> Dictionary:
	var p = _popup()
	if p == null or not p.visible:
		return {}
	var data: Dictionary = p.get("current_data") if p.get("current_data") is Dictionary else {}
	var counter = p.get("counter_btn")
	var answers: Array = []
	for a in (data.get("answers", []) as Array):
		if a is Dictionary:
			answers.append(str(a.get("action", "")))
	return {
		"title": str(data.get("title", data.get("header", ""))),
		"register": str(data.get("register", "")),
		"writer": str(data.get("writer", "")),
		"accept": str(p.get("accept_btn").text).replace("\n", " / "),
		"decline": str(p.get("reject_btn").text).replace("\n", " / "),
		"counter": str(counter.text).replace("\n", " / ") if counter != null else "",
		"counter_visible": counter != null and counter.visible,
		"counter_disabled": counter != null and counter.disabled,
		"counter_tooltip": str(counter.tooltip_text) if counter != null else "",
		"answers": answers,
		"button_decree": str(data.get("button_decree", "")),
		"counsel": str(data.get("counsel", "")),
		"body": _cap(str(p.get("content_label").get_parsed_text())),
	}


func _end_turn() -> void:
	await _close_dispatch()
	var before := _turn()
	await _type("end turn")
	await _settle(120000)
	await _frames(12)
	# The client's own gates ask for the order again (the peril warning, the
	# lapse warning); a player types it again, so does the walk (twice at most).
	for _i in range(2):
		if _turn() != before:
			break
		if _terminal_tail(600).contains("end turn again"):
			await _type("end turn")
			await _settle(120000)
			await _frames(12)
	await _clear_overlays()
	_out["turns"][str(_turn())] = Time.get_ticks_msec() - _t0


func _lines_with(text: String, needles: Array) -> Array:
	var out: Array = []
	for line in text.split("\n"):
		for nd in needles:
			if line.to_lower().contains(str(nd).to_lower()):
				out.append(line.strip_edges())
				break
	return out


func _load_save(name: String) -> bool:
	await _close_modals()
	_main.call("_on_load_save_selected", name)
	await _settle(90000)
	await _frames(20)
	await _hold_window()
	return true


# ── the walk ─────────────────────────────────────────────────────────────────

func _walk() -> void:
	var dir_env := OS.get_environment("AU3A_WALK_OUT")
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
	_out["boot_turn"] = _turn()
	await _frames(10)

	# ── Chapter A — the boot: the chip ──
	await _clear_overlays()
	var chip_boot := _chip()
	if not bool(chip_boot.get("present", false)):
		_note_error("no authority chip on the top bar")
	await _shot("chip", "the boot: the top bar with the Authority chip beside DP",
		{"chip_text": chip_boot.get("text", ""), "chip_tooltip": chip_boot.get("tooltip", ""),
		 "chip": chip_boot})

	# ── Chapter C — the Word (on the boot, authority 100) ──
	await _type("Ney, defend")
	await _frames(10)
	if _objection_open():
		var od = _main.get("objection_dialog")
		var wb = od.get("word_button")
		var buttons := {}
		for key in ["trust_button", "insist_button", "compromise_button", "word_button", "cancel_button"]:
			var b = od.get(key)
			if b != null:
				buttons[key] = {"text": str(b.text), "visible": b.is_visible_in_tree(),
					"disabled": b.disabled, "tooltip": str(b.tooltip_text)}
		var objection := {"marshal": str(od.get("current_marshal")),
			"stats": _texts_under(od.get("panel_container")) if od.get("panel_container") != null else "",
			"buttons": buttons, "chip": _chip(), "terminal": _cap(_terminal_tail(600))}
		_out["objection"] = objection
		await _shot("objection_word", "Ney objects: the dialog's five answers, 'By My Word' priced in authority",
			objection, false)
		if wb != null and wb.visible and not wb.disabled:
			wb.emit_signal("pressed")
			await _settle(90000)
			await _frames(30)
			var tail := _terminal_tail(1400)
			await _shot("word_given", "By My Word pressed: the order runs as given; the reply and the chip",
				{"reply_lines": _lines_with(tail, ["By your word", "Authority", "carries out"]),
				 "chip": _chip(), "terminal": _cap(tail)})
		else:
			_note_error("the WordButton is not pressable")
	else:
		_note_error("no objection dialog after `Ney, defend`: " + _cap(_terminal_tail(500)))

	# ── Chapter B — the Decree (crafted save) ──
	var save_b := OS.get_environment("AU3A_DECREE_SAVE")
	if save_b != "":
		await _load_save(save_b)
		_out["decree_loaded_turn"] = _turn()
		await _open_correspondence()
		var chip_before := _chip()
		if await _read_letter_from_desk():
			var letter := _letter_read()
			_out["decree_letter"] = letter
			letter["chip"] = chip_before
			await _shot("letter_decree", "the Remounts letter on the desk: the third answer, 'Decree it'", letter)
			var p = _popup()
			var counter = p.get("counter_btn") if p != null else null
			if counter != null and counter.visible and not counter.disabled:
				counter.emit_signal("pressed")
				await _settle(90000)
				await _frames(40)
				var tail_b := _terminal_tail(1400)
				await _shot("decreed", "Decree it pressed: the response lines and the chip",
					{"reply_lines": _lines_with(tail_b, ["decree", "Remounts", "Authority", "edict"]),
					 "chip_before": chip_before, "chip": _chip(), "terminal": _cap(tail_b)})
			else:
				_note_error("the Decree button is not pressable")
		else:
			_note_error("the Remounts letter did not open from the desk")

	# ── Chapter D — the Te Deum (crafted save) ──
	var save_d := OS.get_environment("AU3A_TEDEUM_SAVE")
	if save_d != "":
		await _load_save(save_d)
		_out["te_deum_loaded_turn"] = _turn()
		await _clear_overlays()
		var chip_pre := _chip()
		await _shot("te_deum_before", "the truce with Austria on its last turn: the chip before the end turn",
			{"chip": chip_pre})
		await _end_turn()
		var chip_after := _chip()
		var tail_d := _terminal_tail(1800)
		await _shot("te_deum", "the end turn: the truce ripens into peace; the Te Deum lands (+4)",
			{"chip_before": chip_pre, "chip": chip_after,
			 "tooltip_has_te_deum": str(chip_after.get("tooltip", "")).contains("Te Deum"),
			 "terminal_lines": _lines_with(tail_d, ["Te Deum", "peace", "Austria"]),
			 "terminal": _cap(tail_d)})
		await _open_dispatch()
		await _shot("te_deum_dispatch", "the morning's Dispatch after the peace",
			{"dispatch_lines": _lines_with(_dispatch_text(), ["Te Deum", "peace", "Austria", "authority"]),
			 "chip": _chip()})
		await _close_dispatch()
		var tb = _top_bar()
		var screens = tb.get("screens") if tb != null else null
		if screens is Dictionary and screens.has("gazette"):
			tb.call("toggle_screen", "gazette")
			await _settle()
			await _frames(10)
			var gz = screens.get("gazette")
			var gz_text := ""
			if gz != null and gz.get("content_label") != null:
				gz_text = str(gz.get("content_label").get_parsed_text())
			await _shot("te_deum_gazette", "Le Moniteur: the Te Deum's line",
				{"gazette_lines": _lines_with(gz_text, ["Te Deum", "Notre-Dame", "peace"]),
				 "gazette_open": gz != null and bool(gz.visible)})
			if gz != null and gz.visible:
				tb.call("toggle_screen", "gazette")
				await _frames(4)
		else:
			_out["gazette_note"] = "no gazette screen in top_bar.screens at the walk's time"
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

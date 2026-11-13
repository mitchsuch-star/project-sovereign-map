extends SceneTree
# Session UI-5 — the Mode C walk (`docs/UI_VISUAL_FOUNDATION_SPEC.md` §13; the
# plan's verification step 7; November 13, 2026) — modeled on
# tools/au3a_mode_c_walk.gd.
#
#   $env:SOVEREIGN_PORT   = "8006"        # a sandboxed backend listening there (never 8005)
#   $env:UI5_WALK_OUT     = "<abs dir>"   # frames + walk.json land here
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/ui5_mode_c_walk.gd
#
# The REAL `main.tscn` with the REAL APIClient against a live sandboxed backend.
# Every key is pushed into the viewport as an ENGINE event, the typed line goes
# down the command line's own road, every button is pressed by its own signal.
# The walk: the boot → an order typed → H (the HUD hidden) → ? / F10 (Help &
# Keys) → F5 (the quicksave toast) → F9 (the quickload's ask) → the save
# dialog → the Music Room → a letter → the war detail → Settings; a frame of
# each, recorded in walk.json.

const WALL_LIMIT_MS := 900000
const OUT_DEFAULT := "res://../../docs/audits/ui5_mode_c_2026_11_13"

var _main = null
var _out: Dictionary = {"steps": [], "errors": []}
var _dir := ""
var _t0 := 0
var _done := false
var _n := 0


func _init():
	UiSettings._cfg = ConfigFile.new()
	UiSettings._persist = false   # the harness flag: writes stay in memory
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


func _type(line_text: String) -> void:
	var input = _main.get("command_input")
	input.grab_focus()
	input.text = line_text
	input.caret_column = line_text.length()
	_main.call("_execute_command")
	await _settle(90000)
	await _frames(8)


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
	return s if s.length() <= cap else s.substr(0, cap) + " …"


func _hold_window() -> void:
	if root.mode != Window.MODE_WINDOWED or root.size != Vector2i(1920, 1080):
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1920, 1080)
		root.position = Vector2i(5200, 20)
		await _frames(6)


func _press_text(scope: Node, first_line: String) -> bool:
	for b in _all_nodes(scope):
		if b is BaseButton and b.is_visible_in_tree() and not b.disabled and ("text" in b):
			var head := str(b.text).strip_edges().split("\n")[0].strip_edges()
			if head == first_line or head.begins_with(first_line):
				b.emit_signal("pressed")
				return true
	return false


func _clear_boot_overlays() -> void:
	# What a player dismisses at the first view: a court's envoy popup, a
	# marshal's interrupt, the diorama. The screens are left as they are.
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


func _shot(name: String, note: String, extra: Dictionary = {}) -> void:
	await _hold_window()
	var park := InputEventMouseMotion.new()
	park.position = Vector2(-40, -40)
	park.global_position = park.position
	root.push_input(park, true)
	await _frames(4)
	_n += 1
	var img := root.get_texture().get_image()
	var file := "UI5_WALK_%02d_%s_2026_11_13.jpg" % [_n, name]
	var err := img.save_jpg(_dir.path_join(file), 0.88)
	var row := {"step": name, "note": note, "frame": file, "saved": err == OK, "turn": _turn(),
		"ms": Time.get_ticks_msec() - _t0}
	for k in extra:
		row[k] = extra[k]
	_out["steps"].append(row)


func _note_error(what: String) -> void:
	_out["errors"].append({"turn": _turn(), "what": what})


func _toasts_text() -> String:
	for n in _all_nodes(root):
		var scr = n.get_script() if n is Object and n.has_method("get_script") else null
		if scr != null and str(scr.resource_path).ends_with("toast_layer.gd"):
			return _texts_under(n, 400)
	return ""


func _walk() -> void:
	var dir_env := OS.get_environment("UI5_WALK_OUT")
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

	# 1 — the boot
	await _shot("boot", "the war room at its first view (1920 x 1080, the shipped 115 % type)")

	# 2 — an order typed down the command line's own road
	await _type("Soult, drill")
	var display = _main.get("output_display")
	var tail: String = display.get_parsed_text() if display != null else ""
	tail = tail.substr(maxi(0, tail.length() - 700))
	await _shot("order", "an order typed — 'Soult, drill' — and its reply in the log", {"log_tail": tail})

	# 3 — H hides every HUD panel but the top bar; H again brings them back
	await _release_line()
	await _key(KEY_H, 104)
	await _frames(6)
	await _shot("hud_hidden", "H — every HUD panel hidden but the top bar; the toast says how to bring them back",
		{"hud_hidden": bool(_main.get("_hud_hidden")), "toast": _toasts_text()})
	await _key(KEY_H, 104)
	await _frames(6)
	if bool(_main.get("_hud_hidden")):
		_note_error("H did not bring the HUD back")

	# 4 — Help & Keys (F10; `?` is the same door)
	await _release_line()
	await _key(KEY_F10)
	await _frames(8)
	var codex = _main.get("codex")
	var codex_open: bool = codex != null and bool(codex.call("is_open"))
	if not codex_open:
		_note_error("F10 did not open Help & Keys")
	await _shot("help_keys", "F10 — the Help & Keys book: the bindings, live", {"open": codex_open,
		"text": _texts_under(codex, 900) if codex_open else ""})
	if codex_open:
		await _key(KEY_ESCAPE)
		await _frames(6)
		if bool(codex.call("is_open")):
			codex.call("close")

	# 5 — F5 writes "Quicksave" (a toast says so)
	await _release_line()
	await _key(KEY_F5)
	await _settle(30000)
	await _frames(4)
	await _shot("quicksave", "F5 — the quicksave, and its toast", {"toast": _toasts_text()})

	# 6 — F9 asks before it loads
	await _key(KEY_F9)
	await _settle(15000)
	await _frames(8)
	await _shot("quickload_ask", "F9 — the quickload asks first (the confirm card)",
		{"pending": bool(_main.get("_ui5_quickload_pending"))})
	await _key(KEY_ESCAPE)
	await _frames(8)
	for n in _all_nodes(root):
		if n is BaseButton and n.is_visible_in_tree() and ("text" in n) and str(n.text).strip_edges() in ["Stay", "Cancel", "Keep playing"]:
			n.emit_signal("pressed")
			break
	await _frames(6)

	# 7 — the save dialog
	var sd = _main.get("save_dialog")
	if sd != null:
		sd.call("open", "Late September 1805 - France")
		await _settle(15000)
		await _frames(10)
		await _shot("save_dialog", "the save dialog — a named slot, the list with date, turn and nation",
			{"text": _texts_under(sd, 900)})
		sd.call("close")
		await _frames(6)
	else:
		_note_error("no save dialog")

	# 8 — the Music Room (Settings -> Sound)
	var pm = _main.get("pause_menu")
	if pm != null:
		pm.call("open_menu")
		await _frames(10)
		if not _press_text(pm, "Settings"):
			_note_error("no Settings button on the pause menu")
		await _frames(10)
		var sp = pm.get("_settings_panel")
		if sp != null:
			sp.call("_show_tab", 1)
			await _frames(6)
			sp.call("_on_music_room_toggled")
			await _frames(10)
			var room = sp.find_child("MusicRoom", true, false)
			if room != null:
				for n in _all_nodes(pm):
					if n is ScrollContainer and (n as ScrollContainer).is_ancestor_of(room):
						(n as ScrollContainer).ensure_control_visible(room)
						break
			await _frames(8)
			await _shot("music_room", "Settings → Sound: the levels, the switches, Now playing and the Music Room",
				{"text": _texts_under(sp, 900)})
			# 9 (frame 11) — Settings → Display, shot at the walk's end
		pm.call("hide")
		await _frames(6)
	else:
		_note_error("no pause menu")

	# 10 — a letter (the mailbox's first envoy, opened on the desk)
	var mb = _main.get("mailbox_panel")
	var letter_open := false
	if mb != null:
		# the top bar's Envoys road: main fetches GET /mailbox and shows the panel
		_main.call("_on_envoy_clicked")
		await _settle(15000)
		await _frames(10)
		for n in _all_nodes(mb):
			if n is BaseButton and n.is_visible_in_tree() and not n.disabled and ("text" in n):
				var t := str(n.text).strip_edges()
				if t.begins_with("Open") or t.begins_with("Read"):
					n.emit_signal("pressed")
					break
		await _settle(15000)
		await _frames(12)
		var popup = _main.get("incoming_proposal_popup")
		letter_open = popup != null and popup.visible
		if letter_open:
			await _shot("letter", "a court's letter from the mailbox: its picture, its terms, its answers",
				{"text": _texts_under(popup, 900)})
			var dismiss = popup.get("dismiss_btn")
			if dismiss != null and dismiss.visible and not dismiss.disabled:
				dismiss.emit_signal("pressed")
			await _frames(8)
		else:
			await _shot("mailbox", "the Envoys road at the boot (no court has written on this seed's first morning: the log says so; the letters are read in the rated frames)",
				{"text": _texts_under(mb, 900)})
		if mb.visible:
			var close_btn = mb.get("close_btn")
			if close_btn != null:
				close_btn.emit_signal("pressed")
			else:
				mb.visible = false
		await _frames(6)
	_out["letter_opened"] = letter_open

	# 11 — the war detail (the war panel's own card road)
	var wars: Array = _main.get("_cached_wars") if _main.get("_cached_wars") is Array else []
	var wsp = _main.get("war_status_panel")
	if not wars.is_empty() and wsp != null:
		var w: Dictionary = wars[0]
		wsp.emit_signal("card_clicked", str(w.get("opponent", "")), str(w.get("status", "war")),
			str(w.get("war_instance_id", w.get("war_id", ""))))
		await _settle(15000)
		await _frames(12)
		var wd = _main.get("war_detail_popup")
		var wd_open: bool = wd != null and bool(wd.visible)
		if not wd_open:
			_note_error("the war card did not open the war detail")
		await _shot("war_detail", "the war detail: its picture, the peace table, the score, behind its backdrop",
			{"open": wd_open, "text": _texts_under(wd, 900) if wd_open else ""})
		if wd_open:
			await _key(KEY_ESCAPE)
			await _frames(6)
			if wd.visible and wd.has_method("close_popup"):
				wd.call("close_popup")
			elif wd.visible:
				wd.visible = false
	else:
		_note_error("no war on the board for the war detail")

	# 12 — Settings (Display)
	if pm != null:
		pm.call("open_menu")
		await _frames(10)
		_press_text(pm, "Settings")
		await _frames(10)
		var sp2 = pm.get("_settings_panel")
		if sp2 != null:
			sp2.call("_show_tab", 0)
			await _frames(8)
		await _shot("settings", "Settings → Display: its titled cards (window, map & HUD, scale & type, accessibility)")
		pm.call("hide")
		await _frames(4)
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

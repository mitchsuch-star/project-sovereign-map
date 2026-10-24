# DD-B "The fresh-eyes campaign" — a player's hands on the real client
# (Pre-Deploy S13, Slice 1, October 14, 2026).
#
# The players of DD-B see exactly what a player sees and act only as a player
# can. This SceneTree script boots the game as it launches — the title screen,
# `main_menu.tscn`, whose real client talks to a sandboxed backend — in a
# 5120x1440 window parked past the desktop, at the Interface Scale a player at
# that screen gets (the menu derives it: `UiSettings.derive_ui_scale_for`
# gives 1.4), from a FIRST launch (an empty in-memory `UiSettings`, `_persist`
# false: the scale card, the parser hint and the tutor are not marked seen).
#
# Then it polls `<run>/inbox/NNNN.json` for one action at a time. For each it
# acts as a player would — through real input events (`push_input`) or the
# control's own road — settles (the API idle, then 20 frames, then 600 ms of
# real time: entrances animate in real time), and writes
#   <run>/frames/NNNN.png       the full frame
#   <run>/frames/NNNN_view.jpg  2560 wide, for reading
#   <run>/state/NNNN.json       what the frame shows (below)
# Frame 0000 is the boot (the title screen, the backend answered).
#
# The actions (`tools/dd_b_play.py act` writes them):
#   type <text>        the command line takes the text, key by key, and Enter
#   click <words>      the ONE visible control (a button, a chip, a [url] link)
#                      whose text holds the words, pressed by a real click at
#                      its centre (a link by its own meta_clicked road); an
#                      error when none or several match, naming them;
#                      `click#N <words>` picks the N-th (1-based)
#   click_at <x> <y>   a real click at logical px (the state's `factor` says
#                      how a view-JPEG pixel converts)
#   key <K>            Escape, Enter, T, Alt+T, F1, Ctrl+A …
#   scroll <x> <y> up|down <n>
#   look               no action, a fresh frame
#   quit               the last state, then the engine exits
#
# The state record: every visible text row with its rect and layer, grouped
# by surface (the CanvasLayer it stands on, or the war room's own pane); every
# visible button, chip and link with its text, rect and disabled state; the
# map's drawn place names and pieces with their screen rects; which screens,
# popups and the region panel are open; the focus; the command line's text;
# the command window's last 12 lines; every backend reply the action drew
# (`responses`; a typed line's own is `reply`).
#
# Rails: it refuses the player's 8005; UiSettings is in memory only; the
# window is parked past the desktop and takes no OS focus; an idle engine
# (no action for IDLE_QUIT_S) writes a last state and quits.
#
#   SOVEREIGN_PORT=<sandbox port> DD_B_RUN=<run dir> \
#   <godot> --audio-driver Dummy --windowed --resolution 5120x1440 \
#           --position 5200,20 --path godot-client/project-sovereign \
#           --script <abs>/tools/dd_b_client.gd
extends SceneTree

const MENU_SCENE := "res://scenes/main_menu.tscn"
const WINDOW := Vector2i(5120, 1440)
const PARKED := Vector2i(5200, 20)
const SETTLE_FRAMES := 20
const SETTLE_REAL_MS := 600
const IDLE_MS := 120000
const BOOT_MS := 120000
const SCENE_CHANGE_MS := 30000
const VIEW_WIDTH := 2560
const IDLE_QUIT_S := 2700.0
const TERMINAL_TAIL := 12
const MODAL_COVER := 0.95
const MAX_TEXT := 4000
# S14e (October 24, 2026): a control's text was cut at 120 characters, so a
# long chip (the Cabinet's instruments, after DDB-31 lengthened them) read as
# clipped in the record while the real chip wraps — half of a filed row was
# the instrument's own. The cap now holds the longest chip whole.
const MAX_CONTROL_TEXT := 600
const _SKIP_KEYS := ["message", "success", "game_state", "new_state"]

var _run_dir := ""
var _n := 0
var _responses: Array = []
var _hooked: Array = []
var _last_action_ms := 0
var _quitting := false
var _boot_scale := 0.0
var _derived_scale := 0.0
var _url_re := RegEx.create_from_string("(?s)\\[url(?:=([^\\]]*))?\\](.*?)\\[/url\\]")
var _tag_re := RegEx.create_from_string("\\[[^\\]]*\\]")
var _img_re := RegEx.create_from_string("(?s)\\[img[^\\]]*\\].*?\\[/img\\]")
var _ws_re := RegEx.create_from_string("\\s+")
var _sv_display_cache: Dictionary = {}


func _init():
	# A FIRST launch: nothing stored, nothing seen; nothing written to disk.
	UiSettings._cfg = ConfigFile.new()
	var settings_class: Variant = UiSettings
	settings_class.set("_persist", false)
	_run.call_deferred()


# ── the run ─────────────────────────────────────────────────────────────────

func _run() -> void:
	_run_dir = OS.get_environment("DD_B_RUN").replace("\\", "/")
	if _run_dir == "":
		push_error("[DD-B] DD_B_RUN is not set")
		quit(2)
		return
	for sub in ["inbox", "frames", "state"]:
		DirAccess.make_dir_recursive_absolute(_run_dir + "/" + sub)
	if Utils.backend_url().ends_with(":8005"):
		_write_json(_run_dir + "/state/0000.json",
				{"n": 0, "ok": false, "error": "refused: SOVEREIGN_PORT points at the player's 8005"})
		quit(1)
		return
	root.mode = Window.MODE_WINDOWED
	root.unfocusable = OS.get_environment("DD_B_FOCUSABLE") != "1"
	root.position = PARKED
	root.size = WINDOW
	await _frames(10)
	var menu: Node = (load(MENU_SCENE) as PackedScene).instantiate()
	root.add_child(menu)
	current_scene = menu
	# The menu answers once the war office does (its Begin is disabled until).
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < BOOT_MS:
		await process_frame
		if bool(menu.get("_backend_up")):
			break
	_boot_scale = root.content_scale_factor
	_derived_scale = UiSettings.derive_ui_scale_for(WINDOW.x, WINDOW.y,
			float(DisplayServer.screen_get_dpi(DisplayServer.window_get_current_screen())))
	await _settle()
	var rec := {"n": 0, "action": "boot", "ok": bool(menu.get("_backend_up")),
			"error": "" if bool(menu.get("_backend_up")) else "the menu never heard the war office",
			"note": "the title screen, a first launch"}
	_record(rec, 0)
	_n = 1
	_last_action_ms = Time.get_ticks_msec()
	while not _quitting:
		var path := "%s/inbox/%04d.json" % [_run_dir, _n]
		if FileAccess.file_exists(path):
			var req = _read_json(path)
			var action := str(req.get("action", "")) if req is Dictionary else ""
			await _do(action)
			_last_action_ms = Time.get_ticks_msec()
			_n += 1
		else:
			if Time.get_ticks_msec() - _last_action_ms > int(IDLE_QUIT_S * 1000.0):
				await _do("quit idle")
				break
			await create_timer(0.1).timeout


func _do(action: String) -> void:
	var t0 := Time.get_ticks_msec()
	_hook_api()
	_responses = []
	var tail_before := _terminal_text()
	var rec := {"n": _n, "action": action, "ok": true, "error": "", "note": ""}
	var words := action.strip_edges()
	var verb := words.get_slice(" ", 0).to_lower()
	var rest := words.substr(verb.length()).strip_edges()
	if verb == "type":
		await _act_type(rest, rec)
	elif verb == "click" or verb.begins_with("click#"):
		var pick := 0
		if verb.begins_with("click#"):
			pick = int(verb.substr(6))
		await _act_click_words(rest, pick, rec)
	elif verb == "click_at":
		var p := rest.split(" ", false)
		if p.size() != 2 or not p[0].is_valid_float() or not p[1].is_valid_float():
			_err(rec, "click_at wants two numbers: click_at <x> <y> (logical px)")
		else:
			await _act_click_at(Vector2(float(p[0]), float(p[1])), rec)
	elif verb == "key":
		await _act_key(rest, rec)
	elif verb == "scroll":
		await _act_scroll(rest, rec)
	elif verb == "look":
		rec["note"] = "a fresh frame"
	elif verb == "quit":
		_quitting = true
		rec["note"] = "the engine quits" + (" (idle)" if rest == "idle" else "")
	else:
		_err(rec, "unknown action %s — the actions: type, click, click#N, click_at, key, scroll, look" % verb)
	var t1 := Time.get_ticks_msec()
	if not _quitting:
		await _settle_after()
	var tail_after := _terminal_text()
	rec["terminal_new"] = _new_lines(tail_before, tail_after)
	rec["responses"] = _responses.duplicate()
	if verb == "type":
		rec["reply"] = _reply_of(_responses)
	rec["durations_ms"] = {"act": t1 - t0, "settle": Time.get_ticks_msec() - t1}
	_record(rec, _n)
	if _quitting:
		await _frames(2)
		quit(0)


# ── the actions ─────────────────────────────────────────────────────────────

func _act_type(text: String, rec: Dictionary) -> void:
	var main := _main()
	var input: LineEdit = main.get("command_input") if main != null else null
	if input == null or not input.is_visible_in_tree():
		_err(rec, "the command line is not on screen")
		return
	if not input.editable:
		_err(rec, "the command line is not taking orders now (it is disabled)")
		return
	if text == "":
		_err(rec, "type wants the words to type")
		return
	var how := []
	if not input.has_focus():
		# A click at the line's right end: the caret lands after any text.
		var r := input.get_global_rect()
		await _real_click(Vector2(r.end.x - 6.0, r.get_center().y))
		if not input.has_focus():
			input.grab_focus()
			how.append("focus by grab_focus (the click did not focus the line)")
	_restore_editing(rec)
	# Typed at the caret, as a player's keys land: a click into an unfocused
	# line put it at the end; a selection the player made (Ctrl+A) is
	# replaced by the first key.
	var base := input.text
	var at := input.caret_column
	if input.has_selection():
		at = input.get_selection_from_column()
		base = input.text.substr(0, at) + input.text.substr(input.get_selection_to_column())
	var expected := base.substr(0, at) + text + base.substr(at)
	var k := 0
	for ch in text:
		var ev := InputEventKey.new()
		ev.unicode = ch.unicode_at(0)
		ev.pressed = true
		root.push_input(ev, true)
		var up := ev.duplicate() as InputEventKey
		up.pressed = false
		root.push_input(up, true)
		k += 1
		if k % 8 == 0:
			await process_frame
	await _frames(2)
	if input.text != expected:
		# The keystrokes did not land as typed: the control's own road.
		input.text = expected
		input.caret_column = at + text.length()
		how.append("typed by the line's own road (the keystrokes did not land)")
	var sent_before := _sent("/command")
	await _push_key(KEY_ENTER, false, false, false, 0)
	await _frames(3)
	if input.text == expected and _sent("/command") == sent_before and input.is_visible_in_tree():
		input.text_submitted.emit(input.text)
		how.append("sent by the line's own road (Enter did not submit)")
	rec["typed"] = expected
	rec["note"] = "typed and Enter" + ("; " + "; ".join(how) if not how.is_empty() else "")


func _act_click_words(words: String, pick: int, rec: Dictionary) -> void:
	if words == "":
		_err(rec, "click wants the words on the control")
		return
	var want := _squash(words)
	var controls := _controls(true)
	var tiers := [[], [], []]
	for c in controls:
		var t := _squash(str(c["text"]))
		if t != "" and t == want:
			tiers[0].append(c)
		elif t != "" and t.find(want) >= 0:
			tiers[1].append(c)
		elif t == "" and _squash(str(c.get("tooltip", ""))).find(want) >= 0:
			tiers[2].append(c)
	var found: Array = []
	for tier in tiers:
		if not tier.is_empty():
			found = tier
			break
	if found.is_empty():
		_err(rec, "no visible control's text holds \"%s\"" % words)
		rec["candidates"] = []
		return
	if found.size() > 1 and pick == 0:
		_err(rec, "%d controls match \"%s\" — pick one with click#N" % [found.size(), words])
		rec["candidates"] = _describe(found)
		return
	if pick > found.size() or pick < 0:
		_err(rec, "click#%d: only %d controls match \"%s\"" % [pick, found.size(), words])
		rec["candidates"] = _describe(found)
		return
	var c: Dictionary = found[maxi(pick, 1) - 1]
	rec["pressed"] = _describe([c])[0]
	if bool(c.get("disabled", false)):
		# A player can click a disabled control: nothing happens. Say so.
		await _real_click(_centre(c))
		rec["note"] = "the control is disabled; the click did nothing" + \
				(" (its reason: %s)" % c["tooltip"] if str(c.get("tooltip", "")) != "" else "")
		return
	if str(c["kind"]) == "link":
		var rtl: RichTextLabel = c["_node"]
		rtl.meta_clicked.emit(c["meta_value"])
		rec["note"] = "pressed the link by its own road (meta_clicked)"
		return
	var node: Control = c["_node"]
	var hit := {"pressed": false}
	var on_pressed := func(): hit["pressed"] = true
	var on_input := func(ev):
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			hit["pressed"] = true
	if node is BaseButton:
		(node as BaseButton).pressed.connect(on_pressed)
		(node as BaseButton).button_down.connect(on_pressed)
	else:
		node.gui_input.connect(on_input)
	var at := _centre(c)
	var cover := _cover_at(at, node)
	await _real_click(at)
	if is_instance_valid(node):
		if node is BaseButton:
			if (node as BaseButton).pressed.is_connected(on_pressed):
				(node as BaseButton).pressed.disconnect(on_pressed)
			if (node as BaseButton).button_down.is_connected(on_pressed):
				(node as BaseButton).button_down.disconnect(on_pressed)
		elif node.gui_input.is_connected(on_input):
			node.gui_input.disconnect(on_input)
	if bool(hit["pressed"]) or not is_instance_valid(node):
		rec["note"] = "clicked at (%d, %d)" % [int(at.x), int(at.y)]
		return
	# The click did not reach it: record what took it, then press it by its
	# own road so the run goes on — the fallback is itself a finding.
	rec["click_taken_by"] = cover
	if node is BaseButton:
		var b := node as BaseButton
		if b.toggle_mode:
			b.button_pressed = not b.button_pressed
		b.pressed.emit()
	else:
		for pressed in [true, false]:
			var ev := InputEventMouseButton.new()
			ev.button_index = MOUSE_BUTTON_LEFT
			ev.pressed = pressed
			ev.position = node.size * 0.5
			ev.global_position = at
			node.gui_input.emit(ev)
	rec["note"] = "the click at (%d, %d) did not reach it (taken by %s); pressed by its own road" % [
			int(at.x), int(at.y), cover if cover != "" else "nothing"]


func _act_click_at(at: Vector2, rec: Dictionary) -> void:
	var view := root.get_visible_rect().size
	if at.x < 0 or at.y < 0 or at.x > view.x or at.y > view.y:
		_err(rec, "(%d, %d) is off the screen (%d x %d logical px)" % [int(at.x), int(at.y), int(view.x), int(view.y)])
		return
	var under := _cover_at(at, null)
	await _real_click(at)
	rec["note"] = "clicked at (%d, %d)%s" % [int(at.x), int(at.y), (" on " + under) if under != "" else ""]


func _act_key(spec: String, rec: Dictionary) -> void:
	if spec == "":
		_err(rec, "key wants a key: Escape, Enter, T, Alt+T, F1 …")
		return
	var parts := spec.split("+", false)
	var name := parts[parts.size() - 1].strip_edges()
	var alt := false
	var ctrl := false
	var shift := false
	for i in range(parts.size() - 1):
		var m := parts[i].strip_edges().to_lower()
		if m == "alt":
			alt = true
		elif m == "ctrl" or m == "control":
			ctrl = true
		elif m == "shift":
			shift = true
		else:
			_err(rec, "unknown modifier %s (Alt, Ctrl, Shift)" % parts[i])
			return
	var aliases := {"esc": "Escape", "return": "Enter", "del": "Delete", "pgup": "PageUp", "pgdn": "PageDown",
			"space": "Space", "tab": "Tab"}
	if aliases.has(name.to_lower()):
		name = aliases[name.to_lower()]
	var code := OS.find_keycode_from_string(name)
	if code == KEY_NONE:
		_err(rec, "unknown key %s" % name)
		return
	_restore_editing(rec)
	var uni := 0
	if name.length() == 1 and not ctrl and not alt:
		uni = (name.to_upper() if shift else name.to_lower()).unicode_at(0)
	elif name == "Space" and not ctrl and not alt:
		uni = 32
	await _push_key(code, alt, ctrl, shift, uni)
	rec["note"] = "pressed %s" % spec


func _act_scroll(spec: String, rec: Dictionary) -> void:
	var p := spec.split(" ", false)
	if p.size() < 3 or not p[0].is_valid_float() or not p[1].is_valid_float() \
			or not (p[2].to_lower() in ["up", "down"]):
		_err(rec, "scroll wants: scroll <x> <y> up|down <n>")
		return
	var at := Vector2(float(p[0]), float(p[1]))
	var n := int(p[3]) if p.size() > 3 and p[3].is_valid_int() else 3
	var button := MOUSE_BUTTON_WHEEL_UP if p[2].to_lower() == "up" else MOUSE_BUTTON_WHEEL_DOWN
	_motion(at)
	await _frames(2)
	for _i in range(clampi(n, 1, 50)):
		for pressed in [true, false]:
			var ev := InputEventMouseButton.new()
			ev.button_index = button
			ev.pressed = pressed
			ev.factor = 1.0
			ev.position = at
			ev.global_position = at
			root.push_input(ev, true)
		await _frames(2)
	rec["note"] = "scrolled %s %d at (%d, %d)" % [p[2].to_lower(), n, int(at.x), int(at.y)]


# ── input ───────────────────────────────────────────────────────────────────

func _restore_editing(rec: Dictionary) -> void:
	"""The parked window never holds the OS focus (it is unfocusable, so the
	player's own keys never reach it), and Godot 4.4's LineEdit does not
	start EDITING on `grab_focus` in a window without it: the client's
	focused command line would swallow every key. A player's window holds
	the focus, so their focused line edits; the harness gives the line that
	state before a key or a typed line (`edit()`), and says so."""
	var main := _main()
	var input: LineEdit = main.get("command_input") if main != null else null
	if input != null and input.has_focus() and input.editable and not input.is_editing():
		input.edit()
		rec["editing_restored"] = true


func _motion(at: Vector2) -> void:
	var ev := InputEventMouseMotion.new()
	ev.position = at
	ev.global_position = at
	root.push_input(ev, true)


func _real_click(at: Vector2) -> void:
	_motion(at)
	await _frames(3)
	for pressed in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = pressed
		ev.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
		ev.position = at
		ev.global_position = at
		root.push_input(ev, true)
		await _frames(2)


func _push_key(code: int, alt: bool, ctrl: bool, shift: bool, uni: int) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = code
		ev.physical_keycode = code
		ev.alt_pressed = alt
		ev.ctrl_pressed = ctrl
		ev.shift_pressed = shift
		ev.pressed = pressed
		if pressed:
			ev.unicode = uni
		root.push_input(ev, true)
		await _frames(2)


# ── settling ────────────────────────────────────────────────────────────────

func _main() -> Node:
	var cs: Node = current_scene
	if cs == null or not is_instance_valid(cs):
		return null
	return cs if cs.get("command_input") != null else null


func _api_idle() -> bool:
	var cs: Node = current_scene
	if cs == null or not is_instance_valid(cs):
		return false
	var api = cs.get("api_client")
	if api != null and is_instance_valid(api):
		if bool(api.get("_request_in_flight")):
			return false
		var queue = api.get("_request_queue")
		if queue is Array and not (queue as Array).is_empty():
			return false
	if cs.get("_http_mode") != null and str(cs.get("_http_mode")) != "":
		return false
	return true


func _settle() -> void:
	var start := Time.get_ticks_msec()
	var calm := 0
	while Time.get_ticks_msec() - start < IDLE_MS:
		await process_frame
		if _api_idle():
			calm += 1
			if calm >= SETTLE_FRAMES:
				break
		else:
			calm = 0
	await create_timer(SETTLE_REAL_MS / 1000.0).timeout


func _settle_after() -> void:
	"""Settle; a scene change in flight (the menu's fade to the war room, the
	pause menu's road back) is waited out, then the war room's boot."""
	await _settle()
	for _round in range(3):
		var cs: Node = current_scene
		var leaving: bool = cs != null and is_instance_valid(cs) and cs.get("_leaving") == true
		if leaving:
			var start := Time.get_ticks_msec()
			while Time.get_ticks_msec() - start < SCENE_CHANGE_MS:
				await process_frame
				if current_scene != cs:
					break
			await _frames(5)
		var main := _main()
		if main != null and not bool(main.get("_initial_map_bootstrapped")):
			var start2 := Time.get_ticks_msec()
			while Time.get_ticks_msec() - start2 < BOOT_MS:
				await process_frame
				if bool(main.get("_initial_map_bootstrapped")) and _api_idle():
					break
			await _settle()
			continue
		if leaving:
			await _settle()
			continue
		break


func _frames(n: int) -> void:
	for _i in range(n):
		await process_frame


# ── the backend's replies ───────────────────────────────────────────────────

func _hook_api() -> void:
	var cs: Node = current_scene
	if cs == null or not is_instance_valid(cs):
		return
	var api = cs.get("api_client")
	if api == null or not is_instance_valid(api) or _hooked.has(api):
		return
	if api.has_signal("response_received"):
		api.response_received.connect(_on_response)
		_hooked.append(api)


func _on_response(data) -> void:
	if not (data is Dictionary):
		return
	var d: Dictionary = data
	if not (d.has("message") or d.has("success")):
		return
	var keys: Array = []
	for k in d.keys():
		var v = d[k]
		if v != null and not (v is bool and v == false) and not _SKIP_KEYS.has(str(k)):
			keys.append(str(k))
	keys.sort()
	_responses.append({"success": d.get("success"), "message": str(d.get("message", "")).left(MAX_TEXT),
			"action": str(d.get("action", "")), "keys": keys.slice(0, 40)})


func _reply_of(responses: Array):
	for r in responses:
		if str(r.get("message", "")) != "":
			return r
	return null


func _sent(endpoint: String) -> int:
	var main := _main()
	var api = main.get("api_client") if main != null else null
	var counts = api.get("sent_counts") if api != null else null
	return int((counts as Dictionary).get(endpoint, 0)) if counts is Dictionary else -1


# ── the record ──────────────────────────────────────────────────────────────

func _record(rec: Dictionary, n: int) -> void:
	var t0 := Time.get_ticks_msec()
	var img := root.get_texture().get_image()
	var stem := "%s/frames/%04d" % [_run_dir, n]
	img.save_png(stem + ".png")
	var view_img := img.duplicate() as Image
	var vh := int(round(float(img.get_height()) * VIEW_WIDTH / float(img.get_width())))
	view_img.resize(VIEW_WIDTH, vh, Image.INTERPOLATE_LANCZOS)
	view_img.save_jpg(stem + "_view.jpg", 0.9)
	var logical := root.get_visible_rect().size
	var phys := float(img.get_width()) / maxf(logical.x, 1.0)
	rec["frame"] = "frames/%04d.png" % n
	rec["view"] = "frames/%04d_view.jpg" % n
	rec["factor"] = {"physical_per_logical": snappedf(phys, 0.0001),
			"logical_per_view_px": snappedf(float(img.get_width()) / VIEW_WIDTH / phys, 0.0001),
			"logical_size": [roundf(logical.x), roundf(logical.y)],
			"physical_size": [img.get_width(), img.get_height()],
			"view_size": [VIEW_WIDTH, vh]}
	rec["ui_scale"] = {"window": snappedf(root.content_scale_factor, 0.01),
			"derived_for_5120x1440": snappedf(_derived_scale, 0.01), "at_boot": snappedf(_boot_scale, 0.01)}
	rec.merge(_state(), true)
	rec["durations_ms"] = rec.get("durations_ms", {})
	rec["durations_ms"]["record"] = Time.get_ticks_msec() - t0
	_write_json("%s/state/%04d.json" % [_run_dir, n], rec)


func _state() -> Dictionary:
	var out := {}
	var cs: Node = current_scene
	out["scene"] = cs.scene_file_path.get_file().get_basename() if cs != null and is_instance_valid(cs) else ""
	var texts: Array = []
	var surfaces := {}
	var order: Array = []
	# The command window's log is recorded as its tail and its new lines.
	var main0 := _main()
	var log_node: Node = main0.get("output_display") if main0 != null else null
	for n in _all_nodes(root):
		if not (n is Control) or not _shown(n) or _inside_subviewport(n) or n == log_node:
			continue
		var ctrl := n as Control
		var vis := _visible_rect(ctrl)
		if vis.size.x < 1.0 or vis.size.y < 1.0:
			continue
		var t := ""
		if n is RichTextLabel:
			t = (n as RichTextLabel).get_parsed_text()
		elif n is Label:
			t = (n as Label).text
		elif n is LineEdit:
			t = (n as LineEdit).text
			if t == "" and (n as LineEdit).placeholder_text != "":
				t = "(" + (n as LineEdit).placeholder_text + ")"
		elif n is TextEdit:
			t = (n as TextEdit).text
		elif n is BaseButton:
			continue
		t = t.strip_edges()
		if t == "":
			continue
		var s := _surface_of(ctrl)
		if not surfaces.has(s["name"]):
			surfaces[s["name"]] = {"name": s["name"], "layer": s["layer"], "lines": [], "buttons": []}
			order.append(s["name"])
		var row := {"text": t.left(MAX_TEXT), "rect": _r(vis), "layer": s["layer"], "surface": s["name"]}
		if vis.size != ctrl.get_global_rect().size:
			row["clipped"] = true
		texts.append(row)
		surfaces[s["name"]]["lines"].append(row)
	var controls := _controls(false)
	var buttons: Array = _describe(controls)
	for b in buttons:
		var sname := str(b["surface"])
		if not surfaces.has(sname):
			surfaces[sname] = {"name": sname, "layer": b["layer"], "lines": [], "buttons": []}
			order.append(sname)
		surfaces[sname]["buttons"].append(b)
	# Where each scrolling pane stands (a surface's full text does not change
	# when the player scrolls it; its scroll does).
	for n in _all_nodes(root):
		if not (n is Control) or not _shown(n) or _inside_subviewport(n):
			continue
		var bar: VScrollBar = null
		if n is ScrollContainer:
			bar = (n as ScrollContainer).get_v_scroll_bar()
		elif n is RichTextLabel and (n as RichTextLabel).scroll_active and n != log_node:
			bar = (n as RichTextLabel).get_v_scroll_bar()
		if bar == null or bar.max_value - bar.page <= 1.0:
			continue
		var sc := _surface_of(n as Control)
		if surfaces.has(sc["name"]):
			if not surfaces[sc["name"]].has("scroll"):
				surfaces[sc["name"]]["scroll"] = []
			surfaces[sc["name"]]["scroll"].append([roundf(bar.value), roundf(bar.max_value - bar.page)])
	var floor_layer := _live_floor()
	var listed: Array = []
	for name in order:
		var sf: Dictionary = surfaces[name]
		var rows: Array = sf["lines"]
		rows.sort_custom(_reading_order)
		var lines: Array = []
		for r in rows:
			lines.append(r["text"])
		sf["lines"] = lines
		sf["above_floor"] = int(sf["layer"]) >= floor_layer
		listed.append(sf)
	listed.sort_custom(_by_layer_desc)
	out["surfaces"] = listed
	out["texts"] = texts
	out["buttons"] = buttons
	out["modal_floor"] = floor_layer
	out["map"] = _map_rows()
	out["open"] = _open_surfaces()
	var fo: Control = root.gui_get_focus_owner()
	out["focus"] = (str(fo.name) + " (" + fo.get_class() + ")") if fo != null else ""
	var main := _main()
	if main != null:
		var input: LineEdit = main.get("command_input")
		out["command_line"] = {"text": input.text, "editable": input.editable,
				"focused": input.has_focus(), "editing": input.is_editing(),
				"rect": _r(input.get_global_rect())} if input != null else {}
		out["window_has_focus"] = root.has_focus()
		var top = main.get("top_bar")
		if top != null and top.get("turn_label") != null:
			out["turn"] = str(top.turn_label.text)
		out["terminal_tail"] = _tail_lines(_terminal_text(), TERMINAL_TAIL)
	return out


func _reading_order(a: Dictionary, b: Dictionary) -> bool:
	var ay := float(a["rect"][1])
	var by := float(b["rect"][1])
	if absf(ay - by) > 4.0:
		return ay < by
	return float(a["rect"][0]) < float(b["rect"][0])


func _by_layer_desc(a: Dictionary, b: Dictionary) -> bool:
	return int(a["layer"]) > int(b["layer"])


func _open_surfaces() -> Dictionary:
	var main := _main()
	var out := {"screens": [], "pinned": "", "popups": [], "region_panel": false, "other": []}
	var cs: Node = current_scene
	if main == null:
		if cs != null and is_instance_valid(cs):
			out["other"].append(cs.scene_file_path.get_file().get_basename())
			var card = cs.get("_scale_card")
			if card != null and is_instance_valid(card) and (card as CanvasItem).is_visible_in_tree():
				out["popups"].append("scale_card")
		return out
	var top = main.get("top_bar")
	if top != null:
		var screens = top.get("screens")
		if screens is Dictionary:
			for k in screens:
				var s = screens[k]
				if s != null and is_instance_valid(s) and s.visible:
					out["screens"].append(str(k))
		if top.has_method("get_pinned_screen"):
			out["pinned"] = str(top.get_pinned_screen())
	var dm = main.get("dialog_manager")
	if dm != null and dm.get("_dialogs") is Dictionary:
		for k in dm._dialogs:
			var node = dm._dialogs[k].node
			if node != null and is_instance_valid(node) and node.visible:
				out["popups"].append(str(k) + ("" if dm._dialogs[k].modal else " (not modal)"))
	var rp = main.get("region_panel")
	out["region_panel"] = rp != null and is_instance_valid(rp) and rp.visible
	for key in ["diplomacy_wizard", "pause_menu", "mailbox_panel"]:
		var node = main.get(key)
		if node != null and is_instance_valid(node) and node is CanvasItem and (node as CanvasItem).visible:
			out["other"].append(key)
	return out


func _map_rows() -> Array:
	"""The map's drawn place names and the pieces' labels, with their SCREEN
	rects in logical px (the capture harness's X28 reading)."""
	var out: Array = []
	for n in _all_nodes(root):
		if not (n is Control) or not _shown(n):
			continue
		if n.has_method("drawn_label_rects") and not _inside_subviewport(n):
			var xf: Transform2D = (n as Control).get_global_transform()
			for row in n.drawn_label_rects():
				var r: Rect2 = row.get("rect", Rect2())
				var a: Vector2 = xf * r.position
				var b: Vector2 = xf * r.end
				var g := Rect2(a, b - a).abs()
				out.append({"text": str(row.get("text", "")), "kind": "place " + str(row.get("tier", "")),
						"rect": _r(g)})
		elif n is Label and _inside_subviewport(n) and str((n as Label).text).strip_edges() != "":
			var sr := _map_screen_rect(n as Control)
			if sr.is_empty():
				continue
			var view := root.get_visible_rect()
			var g2 := Rect2(sr[0], sr[1], sr[2], sr[3])
			if not view.intersects(g2):
				continue
			out.append({"text": str((n as Label).text).strip_edges(),
					"kind": str(n.get_meta("furniture_kind", "piece")), "rect": _r(g2)})
	return out


# ── controls ────────────────────────────────────────────────────────────────

func _controls(above_floor_only: bool) -> Array:
	var floor_layer := _live_floor() if above_floor_only else -1000000
	var out: Array = []
	for n in _all_nodes(root):
		if not (n is Control) or not _shown(n) or _inside_subviewport(n):
			continue
		var ctrl := n as Control
		var layer := _layer_of(ctrl)
		if layer < floor_layer:
			continue
		var vis := _visible_rect(ctrl)
		if vis.size.x < 2.0 or vis.size.y < 2.0:
			continue
		var s := _surface_of(ctrl)
		var base := {"surface": s["name"], "layer": layer, "rect": _r(vis),
				"tooltip": str(ctrl.tooltip_text).strip_edges().left(240), "_node": ctrl}
		if ctrl is BaseButton:
			var b := ctrl as BaseButton
			var text := (str(n.text) if ("text" in n) else "").strip_edges()
			if text == "":
				text = _own_text(ctrl).strip_edges()
			base["kind"] = "button"
			base["text"] = text.left(MAX_CONTROL_TEXT)
			base["disabled"] = b.disabled
			if b.toggle_mode:
				base["toggled"] = b.button_pressed
			out.append(base)
		elif ctrl.mouse_default_cursor_shape == Control.CURSOR_POINTING_HAND \
				and ctrl.mouse_filter != Control.MOUSE_FILTER_IGNORE and not (ctrl is RichTextLabel):
			base["kind"] = "chip"
			base["text"] = _own_text(ctrl).strip_edges().left(MAX_CONTROL_TEXT)
			base["disabled"] = false
			out.append(base)
		elif ctrl is Slider:
			# Dragged or clicked along its track (click_at): listed so the
			# player knows it is there.
			var sl := ctrl as Slider
			base["kind"] = "slider"
			base["text"] = ""
			base["value"] = sl.value
			base["range"] = [sl.min_value, sl.max_value]
			base["disabled"] = not sl.editable
			out.append(base)
		if ctrl is RichTextLabel:
			var rtl := ctrl as RichTextLabel
			for m in _url_re.search_all(rtl.text):
				var meta := m.get_string(1)
				var label := _tag_re.sub(_img_re.sub(m.get_string(2), "", true), "", true).strip_edges()
				if label == "":
					continue
				var link := base.duplicate()
				link["kind"] = "link"
				link["text"] = label.left(MAX_CONTROL_TEXT)
				link["meta_value"] = meta if meta != "" else m.get_string(2)
				link["disabled"] = false
				link["tooltip"] = ""
				out.append(link)
	return out


func _describe(controls: Array) -> Array:
	var out: Array = []
	for c in controls:
		var d := {}
		for k in c:
			if str(k).begins_with("_") or str(k) == "meta_value":
				continue
			d[k] = c[k]
		out.append(d)
	return out


func _centre(c: Dictionary) -> Vector2:
	var r: Array = c["rect"]
	return Vector2(float(r[0]) + float(r[2]) * 0.5, float(r[1]) + float(r[3]) * 0.5)


func _cover_at(at: Vector2, target: Control) -> String:
	"""The topmost visible input-taking Control at the point, by layer then
	tree order."""
	var best := ""
	var best_layer := -1000000
	for n in _all_nodes(root):
		if not (n is Control) or not _shown(n) or _inside_subviewport(n):
			continue
		var ctrl := n as Control
		if target != null and (ctrl == target or target.is_ancestor_of(ctrl)):
			continue
		if ctrl.mouse_filter == Control.MOUSE_FILTER_IGNORE:
			continue
		if not _visible_rect(ctrl).has_point(at):
			continue
		var layer := _layer_of(ctrl)
		if layer >= best_layer:
			best_layer = layer
			var label := _own_text(ctrl).strip_edges().left(40) if not (ctrl is BaseButton) \
					else str(ctrl.get("text")).left(40)
			best = "%s %s (%s, layer %d)" % [ctrl.name, ("'" + label + "'") if label != "" else "",
					ctrl.get_class(), layer]
	return best


func _live_floor() -> int:
	"""The highest layer a near-full-screen input-taking control stands on: a
	player cannot press what lies under it."""
	var view := root.get_visible_rect()
	var area := view.size.x * view.size.y
	var floor_layer := -1000000
	for n in _all_nodes(root):
		if not (n is Control) or not _shown(n) or _inside_subviewport(n):
			continue
		var ctrl := n as Control
		if ctrl.mouse_filter == Control.MOUSE_FILTER_IGNORE:
			continue
		var r := ctrl.get_global_rect().intersection(view)
		if r.size.x * r.size.y >= MODAL_COVER * area:
			floor_layer = maxi(floor_layer, _layer_of(ctrl))
	return floor_layer


func _own_text(ctrl: Control) -> String:
	for n in _all_nodes(ctrl):
		if n is Label and (n as Label).is_visible_in_tree():
			return str((n as Label).text)
		if n is RichTextLabel and (n as RichTextLabel).is_visible_in_tree():
			return (n as RichTextLabel).get_parsed_text()
	return ""


# ── tree helpers ────────────────────────────────────────────────────────────

func _all_nodes(from: Node) -> Array:
	var out: Array = []
	var stack: Array = [from]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		out.append(n)
		var kids := n.get_children()
		for i in range(kids.size() - 1, -1, -1):
			stack.append(kids[i])
	return out


func _inside_subviewport(n: Node) -> bool:
	var p: Node = n.get_parent()
	while p != null:
		if p is SubViewport:
			return true
		p = p.get_parent()
	return false


func _shown(n: Node) -> bool:
	if not (n is CanvasItem) or not (n as CanvasItem).is_visible_in_tree():
		return false
	var p: Node = n.get_parent()
	while p != null:
		if p is SubViewport:
			var holder: Node = p.get_parent()
			if holder is CanvasItem and not (holder as CanvasItem).is_visible_in_tree():
				return false
		if p is CanvasLayer and not (p as CanvasLayer).visible:
			return false
		p = p.get_parent()
	return true


func _layer_of(n: Node) -> int:
	var p: Node = n
	while p != null:
		if p is CanvasLayer:
			return (p as CanvasLayer).layer
		p = p.get_parent()
	return 0


func _surface_of(n: Node) -> Dictionary:
	"""The surface a node stands on: its CanvasLayer, or (on the scene's own
	canvas) the scene's child that holds it."""
	var p: Node = n
	var cs: Node = current_scene
	var last: Node = n
	while p != null:
		if p is CanvasLayer:
			return {"name": str(p.name), "layer": (p as CanvasLayer).layer}
		if p == cs or p == root:
			break
		last = p
		p = p.get_parent()
	return {"name": str(last.name), "layer": 0}


func _visible_rect(ctrl: Control) -> Rect2:
	"""The part of the control a player can see: its rect, clipped by every
	ancestor that clips its children (a scroll's window) and by the screen."""
	var r := ctrl.get_global_rect()
	var p: Node = ctrl.get_parent()
	while p != null and not (p is CanvasLayer) and not (p is Viewport):
		if p is Control and ((p as Control).clip_contents or p is ScrollContainer):
			r = r.intersection((p as Control).get_global_rect())
			if r.size.x <= 0.0 or r.size.y <= 0.0:
				return Rect2()
		p = p.get_parent()
	return r.intersection(root.get_visible_rect())


func _subviewport_of(n: Node) -> SubViewport:
	var p: Node = n.get_parent()
	while p != null:
		if p is SubViewport:
			return p
		p = p.get_parent()
	return null


func _subviewport_display(sv: SubViewport) -> Control:
	if sv.get_parent() is SubViewportContainer:
		return sv.get_parent()
	var shown: Control = _sv_display_cache.get(sv.get_instance_id(), null)
	if shown == null or not is_instance_valid(shown):
		shown = null
		var tex := sv.get_texture()
		for c in _all_nodes(root):
			if c is TextureRect and (c as TextureRect).texture == tex:
				shown = c
				break
		_sv_display_cache[sv.get_instance_id()] = shown
	return shown


func _map_screen_rect(n: Control) -> Array:
	var sv := _subviewport_of(n)
	if sv == null or sv.size.x <= 0 or sv.size.y <= 0:
		return []
	var shown := _subviewport_display(sv)
	if shown == null or not shown.is_visible_in_tree():
		return []
	var xf: Transform2D = n.get_global_transform_with_canvas()
	var a: Vector2 = xf * Vector2.ZERO
	var b: Vector2 = xf * n.size
	var r := Rect2(a, b - a).abs()
	var sr := shown.get_global_rect()
	var k := Vector2(sr.size.x / float(sv.size.x), sr.size.y / float(sv.size.y))
	return [sr.position.x + r.position.x * k.x, sr.position.y + r.position.y * k.y,
			r.size.x * k.x, r.size.y * k.y]


# ── text helpers ────────────────────────────────────────────────────────────

func _terminal_text() -> String:
	var main := _main()
	var od: RichTextLabel = main.get("output_display") if main != null else null
	return od.get_parsed_text() if od != null else ""


func _tail_lines(text: String, n: int) -> Array:
	var lines: Array = []
	for line in text.split("\n"):
		if line.strip_edges() != "":
			lines.append(line.strip_edges().left(600))
	return lines.slice(maxi(0, lines.size() - n))


func _new_lines(before: String, after: String) -> Array:
	var fresh := after.substr(before.length()) if after.begins_with(before) else after
	var lines: Array = []
	for line in fresh.split("\n"):
		if line.strip_edges() != "":
			lines.append(line.strip_edges().left(1200))
	return lines.slice(maxi(0, lines.size() - 80))


func _squash(t: String) -> String:
	return _ws_re.sub(t.to_lower(), " ", true).strip_edges()


func _r(r: Rect2) -> Array:
	return [roundf(r.position.x), roundf(r.position.y), roundf(r.size.x), roundf(r.size.y)]


func _err(rec: Dictionary, msg: String) -> void:
	rec["ok"] = false
	rec["error"] = msg


func _read_json(path: String):
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var text := f.get_as_text()
	f.close()
	return JSON.parse_string(text)


func _write_json(path: String, value) -> void:
	var tmp := path + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		push_error("[DD-B] cannot write " + path)
		return
	f.store_string(JSON.stringify(value, " "))
	f.close()
	DirAccess.rename_absolute(tmp, path)

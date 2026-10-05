extends SceneTree
# The driven client session — UI/UX C6's delegate evidence (economy gate,
# October 5, 2026; SCORE_FINISH_SPEC §6.8, EA-E8's sibling).
#
#   $env:MODEC_SPEC = "<absolute path to a spec JSON>"  {"out": "<abs>", "turns": 5}
#   $env:SOVEREIGN_PORT = "<port>"   # a backend listening there, saves sandboxed
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/mode_c_driven_session.gd
#
# Run by `tools/mode_c_driven_session.py`, which starts the backend on an
# unused port with its own save directory, and by the reading's client arm.
#
# The REAL `main.tscn` with the REAL APIClient against a live backend. Every
# key the client advertises is pushed into the viewport as an ENGINE event
# (`Viewport.push_input`) — never an operating-system keystroke, so no window
# is needed, no other program can receive it, and the player's own game is
# never touched. Each key is tried in both states the client lives in — the
# command line unfocused, and focused (the state the client re-grabs after
# nearly every action), where the advertised form is Alt+<key> — and the
# screen it names is checked open and then closed by Escape. Then N turns are
# played: an order typed into the command line each turn, and the turn ended
# in turn by typing "end turn", the bare E key, Alt+E while typing, and the
# End Turn button; every modal that appears is answered through its own first
# enabled button (never Replay, Load, Save, Quit or Main Menu).
#
# What this CANNOT see, stated in the result: a key the operating system eats
# before the engine (EA-E9's overlay), and whether the screens LOOK right —
# that is the client arm's frames and the user's eye.
#
# Safety rails (IQ-10's): UiSettings on an in-memory ConfigFile; the result
# JSON is written on every exit path, including the wall-clock limit.

const WALL_LIMIT_MS := 420000
const IDLE_LIMIT_MS := 60000
const TURN_LIMIT_MS := 90000

const SCREEN_KEYS := [
	[KEY_L, "event_log"], [KEY_T, "ledger"], [KEY_G, "generals"],
	[KEY_D, "diplomatic_ledger"], [KEY_R, "dispatch"], [KEY_N, "gazette"],
]
const ORDERS := [
	"Davout, fortify",
	"what can I do",
	"Ney, scout Swabia",
	"status",
	"who am I fighting",
	"Soult, drill",
]
const NEVER_PRESS := ["replay", "load", "save", "quit", "main menu", "new game",
	"return to the war room"]
const PREFER_PRESS := ["acknowledge", "continue", "close", "dismiss", "ok",
	"decline", "defy", "secure", "respect", "restrain", "proceed"]

var _main = null
var _spec: Dictionary = {}
var _out: Dictionary = {}
var _t0 := 0
var _done := false
var _checks: Array = []
var _modals: Array = []
var _turns: Array = []
var _notes: Array = []


func _init():
	UiSettings._cfg = ConfigFile.new()
	_t0 = Time.get_ticks_msec()
	process_frame.connect(_watchdog)
	_session.call_deferred()


func _watchdog():
	if not _done and Time.get_ticks_msec() - _t0 > WALL_LIMIT_MS:
		_out["error"] = "wall-clock limit hit"
		_finish()


# ── plumbing ────────────────────────────────────────────────────────────────

func _frames(n: int) -> void:
	for _i in range(n):
		await process_frame


func _api():
	return _main.get("api_client") if _main != null else null


func _api_idle() -> bool:
	var api = _api()
	if api == null:
		return true
	var busy = bool(api.get("_request_in_flight"))
	var queue = api.get("_request_queue")
	return not busy and (queue == null or queue.is_empty())


func _wait_idle(limit_ms: int = IDLE_LIMIT_MS) -> bool:
	var start := Time.get_ticks_msec()
	var calm := 0
	while Time.get_ticks_msec() - start < limit_ms:
		await process_frame
		if _api_idle():
			calm += 1
			if calm >= 6:
				return true
		else:
			calm = 0
	return false


func _terminal() -> String:
	var display = _main.get("output_display")
	return display.get_parsed_text() if display != null else ""


func _tail(text: String, chars: int = 600) -> String:
	return text.substr(max(0, text.length() - chars))


func _cmd():
	return _main.get("command_input")


func _key(keycode: int, alt: bool = false, unicode: int = 0) -> void:
	var down := InputEventKey.new()
	down.keycode = keycode
	down.physical_keycode = keycode
	down.pressed = true
	down.alt_pressed = alt
	down.unicode = unicode
	root.push_input(down)
	await process_frame
	var up := InputEventKey.new()
	up.keycode = keycode
	up.physical_keycode = keycode
	up.pressed = false
	up.alt_pressed = alt
	root.push_input(up)
	await _frames(3)


func _focus(on: bool) -> void:
	var cmd = _cmd()
	if cmd == null:
		return
	if on:
		cmd.grab_focus()
	else:
		cmd.release_focus()
		var owner = root.gui_get_focus_owner()
		if owner != null:
			owner.release_focus()
	await _frames(2)


func _screen() -> String:
	var bar = _main.get("top_bar")
	return str(bar.get_active_screen()) if bar != null else ""


func _modal_open() -> bool:
	var dm = _main.get("dialog_manager")
	return dm != null and dm.is_any_modal_open()


func _check(name: String, ok: bool, detail: String = "") -> void:
	_checks.append({"check": name, "ok": ok, "detail": detail})


# ── modals: answered through their own first enabled button ────────────────

func _visible_modals() -> Array:
	var out: Array = []
	var dm = _main.get("dialog_manager")
	if dm == null:
		return out
	var dialogs = dm.get("_dialogs")
	if not (dialogs is Dictionary):
		return out
	for name in dialogs:
		var entry = dialogs[name]
		if entry.get("modal", false) and entry.get("node") != null and entry["node"].visible:
			out.append([str(name), entry["node"]])
	return out


func _buttons(node: Node, acc: Array) -> void:
	for child in node.get_children():
		if child is BaseButton:
			var b: BaseButton = child
			if b.is_visible_in_tree() and not b.disabled:
				acc.append(b)
		_buttons(child, acc)


func _label_of(b: BaseButton) -> String:
	if b is Button:
		return str((b as Button).text).strip_edges()
	return ""


func _choose(buttons: Array):
	var allowed: Array = []
	for b in buttons:
		var label := _label_of(b).to_lower()
		if label == "":
			continue
		var banned := false
		for word in NEVER_PRESS:
			if label.find(word) != -1:
				banned = true
				break
		if not banned:
			allowed.append(b)
	for word in PREFER_PRESS:
		for b in allowed:
			if _label_of(b).to_lower().begins_with(word):
				return b
	return allowed[0] if not allowed.is_empty() else null


func _answer_modals(context: String) -> bool:
	"""Answer every open modal. False when one cannot be answered.

	A modal with no enabled button yet (the battle diorama plays its tableau
	before its Close appears) is given what a person gives it: a moment, then
	Escape — the diorama's own skip, a second Escape its close."""
	var escapes := 0
	for _round in range(32):
		var open := _visible_modals()
		if open.is_empty():
			return true
		var name: String = open[0][0]
		var node: Node = open[0][1]
		if name == "pause_menu":
			if node.has_method("close_menu"):
				node.call("close_menu")
			else:
				node.hide()
			await _frames(3)
			continue
		var buttons: Array = []
		_buttons(node, buttons)
		var pick = _choose(buttons)
		if pick == null:
			# a moment of real time for a control that appears late
			var waited := Time.get_ticks_msec()
			while pick == null and Time.get_ticks_msec() - waited < 1500:
				await _frames(5)
				buttons.clear()
				_buttons(node, buttons)
				pick = _choose(buttons)
		if pick == null and escapes < 4:
			escapes += 1
			await _focus(false)
			await _key(KEY_ESCAPE)
			_modals.append({"context": context, "dialog": name, "pressed": "Escape",
				"turn": int(_main.get("current_turn"))})
			await _frames(6)
			continue
		if pick == null:
			var labels: Array = []
			for b in buttons:
				labels.append(_label_of(b))
			_modals.append({"context": context, "dialog": name, "pressed": "",
				"blocked": true, "buttons": labels})
			return false
		_modals.append({"context": context, "dialog": name,
			"pressed": _label_of(pick), "turn": int(_main.get("current_turn"))})
		pick.emit_signal("pressed")
		await _frames(4)
		await _wait_idle()
	_modals.append({"context": context, "dialog": "?", "pressed": "",
		"blocked": true, "note": "32 rounds and still a modal open"})
	return false


# ── the session ─────────────────────────────────────────────────────────────

func _session() -> void:
	var path := OS.get_environment("MODEC_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_out["error"] = "MODEC_SPEC missing or not a JSON object"
		_finish()
		return
	_spec = parsed
	_out["backend"] = Utils.backend_url()
	var packed: PackedScene = load("res://scenes/main.tscn")
	if packed == null:
		_out["error"] = "main.tscn did not load"
		_finish()
		return
	_main = packed.instantiate()
	root.add_child(_main)

	# The connection test runs 0.5 s after _ready, then the topology fetch
	# bootstraps the map: wait for both.
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < IDLE_LIMIT_MS:
		await process_frame
		if bool(_main.get("_initial_map_bootstrapped")) and _api_idle():
			break
	await _wait_idle()
	var connected := _terminal().find("Communications established") != -1
	_check("the client connects to the backend", connected, _tail(_terminal(), 300))
	if not connected:
		_out["error"] = "no connection to " + Utils.backend_url()
		_finish()
		return
	await _answer_modals("boot")

	await _hotkey_census("turn 1")
	await _play_turns(int(_spec.get("turns", 5)))
	await _hotkey_census("after the turns")
	_finish()


func _hotkey_census(when: String) -> void:
	var clear: bool = await _answer_modals("before the keys (" + when + ")")
	if not clear:
		_check(when + ": a modal is answered before the keys", false)
		return
	var cmd = _cmd()
	# The six screen keys, both states.
	for pair in SCREEN_KEYS:
		var code: int = pair[0]
		var screen: String = pair[1]
		var letter := OS.get_keycode_string(code)
		await _focus(false)
		await _key(code)
		var opened := _screen() == screen
		await _key(KEY_ESCAPE)
		_check("%s: %s opens %s (command line unfocused)" % [when, letter, screen],
			opened, "active: " + _screen() if not opened else "")
		_check("%s: Escape closes %s" % [when, screen], _screen() == "", "active: " + _screen())
		if _screen() != "":
			var bar = _main.get("top_bar")
			bar.close_all_screens()
			await _frames(2)
		# typing: Alt+<key> opens it and the bare letter types
		await _focus(true)
		cmd.text = ""
		await _key(code, true)
		var alt_opened := _screen() == screen
		_check("%s: Alt+%s opens %s while typing" % [when, letter, screen],
			alt_opened, "active: " + _screen() if not alt_opened else "")
		var escapes := 0
		while _screen() != "" and escapes < 3:
			await _key(KEY_ESCAPE)
			escapes += 1
		_check("%s: Escape closes %s from the command line" % [when, screen],
			_screen() == "", "escapes: %d" % escapes)
		await _focus(true)
		cmd.text = ""
		await _key(code, false, letter.to_lower().unicode_at(0))
		var typed: String = cmd.text
		_check("%s: a bare %s while typing types the letter" % [when, letter],
			typed == letter.to_lower() and _screen() == "", "text: '%s', screen: '%s'" % [typed, _screen()])
		cmd.text = ""
		if _screen() != "":
			_main.get("top_bar").close_all_screens()
			await _frames(2)

	# The two ledgers' tabs: bare digits unfocused, Alt+digit while typing.
	for pair in [[KEY_T, "ledger", "strategic_ledger", 8], [KEY_D, "diplomatic_ledger", "diplomatic_ledger", 7]]:
		var screen_name: String = pair[1]
		var node = _main.get("top_bar").screens.get(screen_name)
		var tabs: int = pair[3]
		await _focus(false)
		await _key(pair[0])
		await _wait_idle()
		var bare_ok := true
		var bare_bad := ""
		for i in range(tabs):
			await _key(KEY_1 + i)
			if node == null or int(node.get("current_tab")) != i:
				bare_ok = false
				bare_bad += "%d→%s " % [i + 1, str(node.get("current_tab")) if node != null else "?"]
		_check("%s: keys 1–%d turn the %s's books" % [when, tabs, screen_name], bare_ok, bare_bad)
		await _focus(true)
		cmd.text = ""
		var alt_ok := true
		var alt_bad := ""
		for i in range(tabs - 1, -1, -1):
			await _key(KEY_1 + i, true)
			if node == null or int(node.get("current_tab")) != i:
				alt_ok = false
				alt_bad += "%d→%s " % [i + 1, str(node.get("current_tab")) if node != null else "?"]
		_check("%s: Alt+1–%d turn the %s's books while typing" % [when, tabs, screen_name],
			alt_ok and cmd.text == "", alt_bad + ("text: '%s'" % cmd.text if cmd.text != "" else ""))
		cmd.text = ""
		_main.get("top_bar").close_all_screens()
		await _frames(2)

	# F1 — the diplomacy wizard, both states; Escape closes it.
	var wizard = _main.get("diplomacy_wizard")
	for focused in [false, true]:
		await _focus(focused)
		await _key(KEY_F1)
		await _wait_idle()
		var shown: bool = wizard != null and wizard.visible
		_check("%s: F1 opens the diplomacy wizard (%s)" % [when, "typing" if focused else "unfocused"], shown)
		var escapes := 0
		while wizard != null and wizard.visible and escapes < 3:
			await _key(KEY_ESCAPE)
			escapes += 1
		_check("%s: Escape closes the wizard (%s)" % [when, "typing" if focused else "unfocused"],
			wizard == null or not wizard.visible, "escapes: %d" % escapes)

	# Tab / Alt+` — the terminal.
	var panel = _main.get("bottom_left_ui")
	await _focus(false)
	var before: bool = panel.visible
	await _key(KEY_TAB)
	var toggled: bool = panel.visible != before
	await _key(KEY_TAB)
	_check("%s: Tab folds and restores the terminal" % when, toggled and panel.visible == before)
	if panel.visible != before:
		_main.call("_restore_terminal")
		await _frames(2)
	await _focus(true)
	before = panel.visible
	await _key(KEY_QUOTELEFT, true)
	var alt_toggled: bool = panel.visible != before
	if panel.visible != before:
		_main.call("_restore_terminal")
		await _frames(2)
	_check("%s: Alt+` folds the terminal while typing" % when, alt_toggled)

	# The map keys: M, Home, +, -, both states.
	var map_area = _main.get("map_area")
	for focused in [false, true]:
		var label := "typing" if focused else "unfocused"
		await _focus(focused)
		var mode_before = map_area.get("_map_fill_mode")
		await _key(KEY_M, focused)
		var mode_after = map_area.get("_map_fill_mode")
		_check("%s: %sM changes the map mode (%s)" % [when, "Alt+" if focused else "", label],
			mode_after != mode_before, "%s → %s" % [mode_before, mode_after])
		var zoom_before = float(map_area.get("_zoom_level"))
		await _key(KEY_EQUAL, focused)
		await _frames(30)
		var zoom_in = float(map_area.get("_zoom_level"))
		await _key(KEY_MINUS, focused)
		await _frames(30)
		var zoom_out = float(map_area.get("_zoom_level"))
		_check("%s: %s+ and %s- zoom the map (%s)" % [when, "Alt+" if focused else "", "Alt+" if focused else "", label],
			zoom_in > zoom_before and zoom_out < zoom_in,
			"%.3f → %.3f → %.3f" % [zoom_before, zoom_in, zoom_out])
		await _key(KEY_HOME, focused)
		await _frames(10)
		_check("%s: %sHome answers (%s)" % [when, "Alt+" if focused else "", label], true,
			"the camera re-centres (no assertion on the position)")

	# Escape with nothing open — the pause menu, and Escape again closes it.
	await _focus(false)
	var pause = _main.get("pause_menu")
	await _key(KEY_ESCAPE)
	var paused: bool = pause != null and pause.visible
	await _key(KEY_ESCAPE)
	_check("%s: Escape opens the pause menu and Escape closes it" % when,
		paused and (pause == null or not pause.visible))
	if pause != null and pause.visible:
		pause.call("close_menu")
		await _frames(2)
	await _focus(true)


func _submit(text: String) -> void:
	var cmd = _cmd()
	cmd.grab_focus()
	cmd.text = text
	cmd.text_submitted.emit(text)
	await _frames(3)
	await _wait_idle()


func _play_turns(n: int) -> void:
	var ways := ["typed", "E", "Alt+E", "button", "typed"]
	for t in range(n):
		var turn_before := int(_main.get("current_turn"))
		var record := {"turn": turn_before, "order": "", "order_reply": "", "end_by": ways[t % ways.size()]}
		var start_clear: bool = await _answer_modals("turn %d start" % turn_before)
		if not start_clear:
			record["blocked"] = "a modal could not be answered at the turn's start"
			_turns.append(record)
			return
		var order: String = ORDERS[t % ORDERS.size()]
		record["order"] = order
		var before_len := _terminal().length()
		await _submit(order)
		await _answer_modals("after '%s'" % order)
		var after: String = _terminal()
		record["order_reply"] = _tail(after.substr(min(before_len, after.length())), 500)
		# End the turn, by this turn's road.
		var way: String = record["end_by"]
		var start := Time.get_ticks_msec()
		var confirms := 0
		var advanced := false
		var tries := 0
		while Time.get_ticks_msec() - start < TURN_LIMIT_MS and tries < 4:
			tries += 1
			await _answer_modals("before ending turn %d" % turn_before)
			match way:
				"typed":
					await _submit("end turn")
				"E":
					await _focus(false)
					await _key(KEY_E)
				"Alt+E":
					await _focus(true)
					await _key(KEY_E, true)
				"button":
					_main.get("end_turn_button").emit_signal("pressed")
					await _frames(3)
			await _wait_idle(TURN_LIMIT_MS)
			# the enemy phase's modals, the diorama, the morning's letters
			for _k in range(6):
				await _answer_modals("turn %d end" % turn_before)
				await _wait_idle()
			if int(_main.get("current_turn")) > turn_before:
				advanced = true
				break
			if bool(_main.get("_awaiting_end_turn_confirmation")):
				confirms += 1
				continue
		record["advanced"] = advanced
		record["lapse_confirms"] = confirms
		record["turn_after"] = int(_main.get("current_turn"))
		if not advanced:
			record["blocked"] = "the turn did not advance"
			record["terminal_tail"] = _tail(_terminal(), 900)
			_turns.append(record)
			return
		_turns.append(record)


func _finish() -> void:
	if _done:
		return
	_done = true
	var failed: Array = []
	for c in _checks:
		if not c["ok"]:
			failed.append(c["check"])
	var blocked := false
	for m in _modals:
		if m.get("blocked", false):
			blocked = true
	for r in _turns:
		if r.has("blocked"):
			blocked = true
	_out["checks"] = _checks
	_out["failed_checks"] = failed
	_out["modals"] = _modals
	_out["turns"] = _turns
	_out["turns_played"] = _turns.size()
	_out["blocked"] = blocked
	_out["cannot_see"] = [
		"a key the operating system eats before the engine (EA-E9's overlay)",
		"whether the screens look right (the client arm's frames, the user's eye)",
	]
	_out["seconds"] = int((Time.get_ticks_msec() - _t0) / 1000)
	var out := str(_spec.get("out", ""))
	if out != "":
		var f := FileAccess.open(out, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_out, " "))
			f.close()
	quit(0 if _out.get("error", "") == "" else 1)

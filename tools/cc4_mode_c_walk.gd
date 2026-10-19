extends SceneTree
# Row CC, CC-4 "Chained orders" — the Mode C walk (Pre-Deploy S13c part 4,
# October 19, 2026).
#
#   $env:SOVEREIGN_PORT = "8007"     # a backend listening there, saves sandboxed
#   $env:CC4_WALK_OUT  = "<abs dir>" # frames + walk.json land here
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/cc4_mode_c_walk.gd
#
# The REAL `main.tscn` with the REAL APIClient against a live sandboxed
# backend (never 8005 or 8006 — the player's ports). Every line is typed into
# the real command line and every click pushed into the viewport as an ENGINE
# event (`Viewport.push_input`) — never an operating-system input; the window
# is parked off the 5120-wide desktop. Two turns:
#
#   1 then_fortify — `Soult, march to Burgundy then fortify`: his arrow, its
#                    badge "· then fortify" (Soult is literal: he never answers
#                    the guns of his own accord, so the march is his alone)
#   2 march_card   — the arrow clicked: "Soult marches to Burgundy, then fortifies"
#   3 asked_first  — `Ney, fortify then attack Mack`: nothing goes out, the
#                    order that gives both offered beside the line
#   4 contingency  — `Davout, if Mack advances, fall back to Lorraine`: the
#                    anchor "holds Rhineland · if Mack comes"
#   5 anchor_card  — the anchor clicked: the watch in its headline
#   6 end_turn     — the turn ends: what the screen shows before any modal is answered
#   7 morning      — every modal answered: Davout's watch fired, he fell back
#   8 arrival      — the next turn's end: Soult arrives at Burgundy and fortifies
#
# `walk.json` records what each step read, the modals answered, the terminal.

const WALL_LIMIT_MS := 420000
const OUT_DEFAULT := "res://../../docs/audits/cc4_client"
const NEVER_PRESS := ["replay", "load", "save", "quit", "main menu", "new game",
	"return to the war room"]
const PREFER_PRESS := ["acknowledge", "continue", "close", "dismiss", "ok",
	"decline", "defy", "secure", "respect", "restrain", "proceed"]

var _main = null
var _out: Dictionary = {"steps": [], "modals": []}
var _dir := ""
var _t0 := 0
var _done := false


func _init():
	UiSettings._cfg = ConfigFile.new()
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


func _map():
	return _main.get("map_area")


func _card():
	return _main.get("order_card")


func _motion(at: Vector2) -> void:
	for _i in range(2):
		var ev := InputEventMouseMotion.new()
		ev.position = at
		ev.global_position = at
		root.push_input(ev, true)
	await _frames(2)


func _button(at: Vector2, pressed: bool) -> void:
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = pressed
	ev.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
	ev.position = at
	ev.global_position = at
	root.push_input(ev, true)
	await _frames(2)


func _key(keycode: int, unicode: int = 0) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = keycode
		ev.physical_keycode = keycode
		ev.unicode = unicode
		ev.pressed = pressed
		root.push_input(ev)
	await _frames(3)


func _terminal_tail(chars: int = 900) -> String:
	var display = _main.get("output_display")
	var text: String = display.get_parsed_text() if display != null else ""
	return text.substr(maxi(0, text.length() - chars))


func _shot(name: String, note: String) -> void:
	# The cursor parked off the map: no province card over the frame.
	var park := InputEventMouseMotion.new()
	park.position = Vector2(-40, -40)
	park.global_position = park.position
	root.push_input(park, true)
	await _frames(4)
	var img := root.get_texture().get_image()
	var path := _dir.path_join("CC4_%s_2026_10_19.jpg" % name)
	var err := img.save_jpg(path, 0.86)   # the audits' frames are JPEGs
	var rep: Dictionary = _map().call("order_report") if _map() != null else {}
	var card = _card()
	var layer: Dictionary = rep.get("layer", {})
	_out["steps"].append({
		"step": name, "note": note, "frame": path.get_file(), "saved": err == OK,
		"card_open": card != null and card.visible,
		"card_mode": str(card.call("mode")) if card != null else "",
		"card_title": str(card.get("title_label").text) if card != null and card.visible else "",
		"card_command": str(card.get("command_label").text) if card != null and card.visible else "",
		"arrows": layer.get("arrows", []),
		"actions": int(_main.get("actions_remaining")),
		"turn": int(_main.get("current_turn")),
	})


func _uncovered(at: Vector2) -> bool:
	await _motion(at)
	var map = _map()
	var over = root.gui_get_hovered_control()
	return over == map or (over != null and map.is_ancestor_of(over))


func _arrow_point(key: String) -> Vector2:
	"""A point on his arrow (its line or its badge), uncovered, no piece or
	chip under it."""
	var map = _map()
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
			var clear: bool = await _uncovered(at)
			if clear and (map.get("hovered_marshal") as Dictionary).is_empty() \
					and (map.get("hovered_fogged_force") as Dictionary).is_empty():
				return at
	return Vector2(-1, -1)


func _type(line: String) -> void:
	var input = _main.get("command_input")
	input.text = line
	input.caret_column = line.length()
	_main.call("_execute_command")
	await _settle()
	await _frames(6)


# ── the modals of the turn's end (the driven session's answerer) ────────────

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
	var escapes := 0
	for _round in range(32):
		var open := _visible_modals()
		if open.is_empty():
			return true
		var name: String = open[0][0]
		var node: Node = open[0][1]
		if name == "pause_menu":
			node.hide()
			await _frames(3)
			continue
		var buttons: Array = []
		_buttons(node, buttons)
		var pick = _choose(buttons)
		if pick == null:
			var waited := Time.get_ticks_msec()
			while pick == null and Time.get_ticks_msec() - waited < 1500:
				await _frames(5)
				buttons.clear()
				_buttons(node, buttons)
				pick = _choose(buttons)
		if pick == null and escapes < 4:
			escapes += 1
			_main.get("command_input").release_focus()
			await _key(KEY_ESCAPE)
			_out["modals"].append({"context": context, "dialog": name, "pressed": "Escape"})
			await _frames(6)
			continue
		if pick == null:
			_out["modals"].append({"context": context, "dialog": name, "blocked": true})
			return false
		_out["modals"].append({"context": context, "dialog": name, "pressed": _label_of(pick)})
		pick.emit_signal("pressed")
		await _frames(4)
		await _settle()
	return false


func _walk() -> void:
	var dir_env := OS.get_environment("CC4_WALK_OUT")
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
	while Time.get_ticks_msec() - start < 60000:
		await process_frame
		if bool(_main.get("_initial_map_bootstrapped")) and _main.get("command_input").editable:
			break
	await _settle()
	_out["backend"] = Utils.backend_url()
	_out["booted"] = bool(_main.get("_initial_map_bootstrapped"))
	var map = _map()
	map.call("fit_europe")
	map.call("_set_camera_zoom_level", 2.2)   # the theatre close: the arrows read
	await _frames(6)

	# 1 — the march carries its arrival verb.
	await _type("Soult, march to Burgundy then fortify")
	_out["then_fortify_tail"] = _terminal_tail(500)
	_main.call("_minimize_terminal")
	map.call("focus_on_region", "Lorraine")
	await _frames(6)
	await _shot("1_then_fortify", "Soult's march to Burgundy, its badge '· then fortify'")

	# 2 — his arrow clicked: the card's headline.
	var at: Vector2 = await _arrow_point("Soult")
	_out["soult_arrow_point"] = [at.x, at.y]
	if at.x >= 0.0:
		await _button(at, true)
		await _button(at, false)
		await _frames(4)
		await _shot("2_march_card", "the arrow clicked: 'Soult marches to Burgundy, then fortifies'")
		await _key(KEY_ESCAPE)

	# 3 — a contradiction asked first (while actions remain): nothing goes
	#     out, the order that gives both offered beside the line.
	_main.call("_restore_terminal")
	await _type("Ney, fortify then attack Mack")
	_out["asked_first_tail"] = _terminal_tail(700)
	_out["asked_first_offer"] = str(_main.get("_offered_command"))
	await _shot("3_asked_first", "nothing sent; 'Ney, attack Mack then fortify' offered beside the line")
	_main.get("command_input").text = ""

	# 4 — the standing contingency.
	await _type("Davout, if Mack advances, fall back to Lorraine")
	_out["contingency_tail"] = _terminal_tail(700)
	await _shot("4_contingency_reply", "the watch said: within reach already, at the turn's end")
	_main.call("_minimize_terminal")
	map.call("focus_on_region", "Rhineland")
	await _frames(6)
	await _shot("4_contingency", "Davout's anchor: 'holds Rhineland · if Mack comes'")

	# 5 — the anchor clicked: the watch in its headline.
	var anchor: Vector2 = await _arrow_point("Davout")
	_out["davout_anchor_point"] = [anchor.x, anchor.y]
	if anchor.x >= 0.0:
		await _button(anchor, true)
		await _button(anchor, false)
		await _frames(4)
		await _shot("5_anchor_card", "the anchor clicked: the watch in its headline")
		await _key(KEY_ESCAPE)

	# 6 + 7 — the turn's end: Davout's watch fires, he falls back.
	await _end_turn("turn1", "6_end_turn", "the turn ends: the screen before any modal is answered")
	_main.call("_restore_terminal")
	await _frames(6)
	map.call("focus_on_region", "Lorraine")
	await _frames(6)
	await _shot("7_morning", "Davout's watch fired: he fell back to Lorraine; Soult one march from Burgundy")

	# 8 — the next turn's end: Ney arrives and fortifies.
	await _end_turn("turn2", "", "")
	_main.call("_minimize_terminal")
	map.call("focus_on_region", "Burgundy")
	await _frames(6)
	await _shot("8_arrival", "Soult at Burgundy behind his works — the march's arrival verb done")
	_main.call("_restore_terminal")
	_finish()


func _terminal_full() -> String:
	var display = _main.get("output_display")
	return display.get_parsed_text() if display != null else ""


func _end_turn(tag: String, shot_name: String, shot_note: String) -> void:
	var turn_before := int(_main.get("current_turn"))
	_main.get("command_input").text = ""
	_main.get("end_turn_button").emit_signal("pressed")
	await _frames(3)
	await _settle(120000)
	await _frames(10)
	if shot_name != "":
		await _shot(shot_name, shot_note)
	for _k in range(8):
		var clear: bool = await _answer_modals("%s end" % tag)
		await _settle()
		if clear and int(_main.get("current_turn")) > turn_before:
			break
		if bool(_main.get("_awaiting_end_turn_confirmation")):
			_main.get("end_turn_button").emit_signal("pressed")
			await _settle(120000)
	_out[tag + "_after"] = int(_main.get("current_turn"))
	# the LAST "Strategic Order Updates" block the terminal printed (a trimmed
	# terminal makes any character offset unreliable)
	var text := _terminal_full()
	var at_block := text.rfind("--- Strategic Order Updates ---")
	var lines: Array = []
	if at_block >= 0:
		for line in text.substr(at_block).split(char(10)).slice(1, 12):
			if line.strip_edges() == "":
				break
			lines.append(line.strip_edges())
	_out[tag + "_report"] = lines


func _finish():
	if _done:
		return
	_done = true
	_out["ms"] = Time.get_ticks_msec() - _t0
	var path := _dir.path_join("walk.json") if _dir != "" else ""
	if path != "":
		var f := FileAccess.open(path, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_out, "  "))
			f.close()
	quit(1 if _out.has("error") else 0)

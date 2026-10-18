extends SceneTree
# Row CC, CC-5 "The war table" — the Mode C walk (Pre-Deploy S13c part 3,
# October 18, 2026).
#
#   $env:SOVEREIGN_PORT = "8007"     # a backend listening there, saves sandboxed
#   $env:CC5_WALK_OUT  = "<abs dir>" # frames + walk.json land here
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/cc5_mode_c_walk.gd
#
# The REAL `main.tscn` with the REAL APIClient against a live sandboxed
# backend (never 8005 or 8006 — the player's ports). Every gesture is pushed
# into the viewport as an ENGINE event (`Viewport.push_input`) at the screen
# point of the piece, the province or the arrow — never an operating-system
# input, so the player's own desktop is never touched; the window is parked
# off the 5120-wide desktop. One turn's four actions; a frame at each step:
#
#   1 group       — Ctrl-click two of our corps: a ring at each, the strip
#   2 group_card  — a province: ONE card, a line per corps, the sum vs the pool
#   3 group_sent  — Enter: the lines go one at a time; the account in the terminal
#   4 arrows      — a hold typed beside them: every standing order an arrow
#   5 arrow_card  — a click on a march's arrow: Cancel or Change
#   6 change      — Enter (Change): he is selected — his arrow bright, the rest dimmed
#   7 idle        — `.`: the next corps with nothing to do, the camera on him
#   8 anchor_card — the hold's anchor clicked: its Cancel dimmed, no action left
#
# `walk.json` records what each step read.

const WALL_LIMIT_MS := 300000
const OUT_DEFAULT := "res://../../docs/audits/cc5_client"

var _main = null
var _out: Dictionary = {"steps": []}
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


func _button(at: Vector2, pressed: bool, ctrl: bool = false) -> void:
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = pressed
	ev.ctrl_pressed = ctrl
	ev.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
	ev.position = at
	ev.global_position = at
	root.push_input(ev, true)
	await _frames(2)


func _click(at: Vector2, ctrl: bool = false) -> void:
	await _motion(at)
	await _button(at, true, ctrl)
	await _button(at, false, ctrl)


func _key(keycode: int, unicode: int = 0) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = keycode
		ev.physical_keycode = keycode
		ev.unicode = unicode
		ev.pressed = pressed
		root.push_input(ev)
	await _frames(3)


func _shot(name: String, note: String) -> void:
	# The cursor parked off the map: no province card over the frame.
	var park := InputEventMouseMotion.new()
	park.position = Vector2(-40, -40)
	park.global_position = park.position
	root.push_input(park, true)
	await _frames(4)
	var img := root.get_texture().get_image()
	var path := _dir.path_join("CC5_%s_2026_10_18.jpg" % name)
	var err := img.save_jpg(path, 0.86)   # the audits' frames are JPEGs
	var rep: Dictionary = _map().call("order_report") if _map() != null else {}
	var card = _card()
	var layer: Dictionary = rep.get("layer", {})
	_out["steps"].append({
		"step": name, "note": note, "frame": path.get_file(), "saved": err == OK,
		"selected": str(_main.get("_order_marshal")),
		"group": (_main.get("_order_group") as Array).duplicate(),
		"strip": str(_main.call("order_strip_text")),
		"card_open": card != null and card.visible,
		"card_mode": str(card.call("mode")) if card != null else "",
		"card_title": str(card.get("title_label").text) if card != null and card.visible else "",
		"card_terms": str(card.get("terms_label").get_parsed_text()) if card != null and card.visible else "",
		"arrows": layer.get("arrows", []),
		"rings": int(layer.get("rings", 0)),
		"actions": int(_main.get("actions_remaining")),
	})


func _terminal_tail(chars: int = 900) -> String:
	var display = _main.get("output_display")
	var text: String = display.get_parsed_text() if display != null else ""
	return text.substr(maxi(0, text.length() - chars))


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


func _walk() -> void:
	var dir_env := OS.get_environment("CC5_WALK_OUT")
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
	_main.call("_minimize_terminal")
	map.call("focus_on_region", "Lorraine")
	await _frames(6)

	# 1 — the group: Ctrl-click two corps of ours.
	var members := ["Soult", "Davout"]
	for key in members:
		await _click(map.call("screen_point_of_marshal", key), true)
		await _settle()
	await _shot("1_group", "Ctrl-click Soult and Davout: a ring at each, the strip")

	# 2 — a province both march to cleanly (no contact, no doubt): the card.
	var positions: Dictionary = map.call("_get_active_region_positions")
	var home: Vector2 = positions.get("Lorraine", Vector2.ZERO)
	var regions: Array = []
	for region in positions:
		if region in ["Lorraine", "Rhineland"]:
			continue
		regions.append([home.distance_to(positions[region]), str(region)])
	regions.sort()
	var card = _card()
	var dest := ""
	for row in regions.slice(0, 24):
		var p: Vector2 = map.call("screen_point_of_region", row[1])
		if p.x < 0.0:
			continue
		var open: bool = await _uncovered(p)
		if not open:
			continue
		await _click(p)
		await _settle()
		await _frames(4)
		var terms := str(card.get("terms_label").get_parsed_text()) if card.visible else ""
		var lines: Array = card.call("group_lines") if card.visible else []
		if lines.size() == 2 and not ("asks" in terms) and not ("may object" in terms) \
				and not ("arrives this turn" in terms):
			dest = str(row[1])
			break
		if card.visible:
			await _key(KEY_ESCAPE)   # the card's Esc: back to the group
	_out["dest"] = dest
	await _shot("2_group_card", "the click on %s: ONE card, a line per corps" % dest)

	# 3 — Enter: the lines go one at a time; the account.
	await _key(KEY_ENTER)
	for _i in range(4):
		await _settle()
		await _frames(6)
	_main.call("_restore_terminal")
	await _frames(6)
	_out["group_tail"] = _terminal_tail()
	await _shot("3_group_sent", "Enter: both march; the account in the terminal")

	# 4 — a hold typed beside them: the anchor stands with the marches.
	await _type("Napoleon, hold Lorraine")
	_out["hold_tail"] = _terminal_tail(400)
	_main.call("_minimize_terminal")
	map.call("focus_on_region", "Lorraine")
	await _frames(6)
	await _shot("4_arrows", "every standing order of ours an arrow — two marches and a hold")

	# 5 — the march's arrow clicked: the arrow card.
	var at: Vector2 = await _arrow_point("Soult")
	_out["arrow_point"] = [at.x, at.y]
	await _button(at, true)
	await _button(at, false)
	await _frames(4)
	await _shot("5_arrow_card", "a click on Soult's arrow: Cancel or Change")

	# 6 — Enter is Change: he is selected.
	await _key(KEY_ENTER)
	await _settle()
	await _frames(6)
	await _shot("6_change", "Enter (Change): Soult selected — his arrow bright, the rest dimmed")
	await _key(KEY_ESCAPE)

	# 7 — `.`: the next corps with nothing to do.
	_main.get("command_input").grab_focus()
	await _key(KEY_PERIOD, 46)
	await _settle()
	await _frames(6)
	await _shot("7_idle", "`.`: the next corps with nothing to do, the camera on him")
	await _key(KEY_ESCAPE)

	# 8 — the hold's anchor: its card (no action left — the Cancel dimmed).
	map.call("focus_on_region", "Lorraine")
	await _frames(6)
	var anchor: Vector2 = await _arrow_point("Napoleon")
	_out["anchor_point"] = [anchor.x, anchor.y]
	if anchor.x >= 0.0:
		await _button(anchor, true)
		await _button(anchor, false)
		await _frames(4)
		_out["anchor_cancel_disabled"] = bool((card.get("send_button") as Button).disabled)
		await _shot("8_anchor_card", "the anchor clicked: its card — no action left to cancel")
		await _key(KEY_ESCAPE)
	_main.call("_restore_terminal")
	_finish()


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

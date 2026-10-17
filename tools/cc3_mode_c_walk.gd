extends SceneTree
# Row CC, CC-3 "Select, click, Enter" (+ drag) — the Mode C walk (Pre-Deploy
# S13c part 2, October 17, 2026).
#
#   $env:SOVEREIGN_PORT = "8007"     # a backend listening there, saves sandboxed
#   $env:CC3_WALK_OUT  = "<abs dir>" # frames + walk.json land here
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/cc3_mode_c_walk.gd
#
# The REAL `main.tscn` with the REAL APIClient against a live sandboxed
# backend (never 8005 or 8006 — the player's ports). Every gesture is pushed
# into the viewport as an ENGINE event (`Viewport.push_input`) at the screen
# point of the piece or province — never an operating-system input, so the
# player's own desktop is never touched; the window is parked off the
# 5120-wide desktop. A frame is shot at each step:
#
#   1 select   — a click on a piece of ours: the ring, the strip, the tint
#   2 hover    — the cursor on a province: the quote's road as a ghost line
#   3 card     — the click: the confirm card on the exact quote
#   4 sent     — Enter: the order through the typed road, the reply in the terminal
#   5 dragging — a second corps' piece dragged across the map
#   6 dropped  — released on a province: the card for that province
#   7 attack   — with a selection, a click on an enemy we see: the attack card
#
# `walk.json` records what each step read: the selection, the card's command
# beside the quote's, what was sent and the backend's reply.

const WALL_LIMIT_MS := 240000
const OUT_DEFAULT := "res://../../docs/audits/cc3_client"

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


func _motion(at: Vector2, held: bool = false) -> void:
	for _i in range(2):
		var ev := InputEventMouseMotion.new()
		ev.position = at
		ev.global_position = at
		ev.button_mask = MOUSE_BUTTON_MASK_LEFT if held else 0
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


func _click(at: Vector2) -> void:
	await _motion(at)
	await _button(at, true)
	await _button(at, false)


func _key(keycode: int) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = keycode
		ev.physical_keycode = keycode
		ev.pressed = pressed
		root.push_input(ev)
	await _frames(3)


func _shot(name: String, note: String) -> void:
	await _frames(4)
	var img := root.get_texture().get_image()
	var path := _dir.path_join("CC3_%s_2026_10_17.jpg" % name)
	var err := img.save_jpg(path, 0.86)   # the audits' frames are JPEGs
	var rep: Dictionary = _map().call("order_report") if _map() != null else {}
	var card = _main.get("order_card")
	_out["steps"].append({
		"step": name, "note": note, "frame": path.get_file(), "saved": err == OK,
		"selected": str(_main.get("_order_marshal")),
		"strip": str(_main.call("order_strip_text")),
		"card_open": card != null and card.visible,
		"card_command": str(card.call("command")) if card != null and card.visible else "",
		"bands": (rep.get("bands", {}) as Dictionary).size(),
		"layer": rep.get("layer", {}),
	})


func _terminal_tail(chars: int = 700) -> String:
	var display = _main.get("output_display")
	var text: String = display.get_parsed_text() if display != null else ""
	return text.substr(maxi(0, text.length() - chars))


func _own_rows() -> Array:
	var gs: Dictionary = _main.get("_last_game_state")
	var rows: Array = []
	var marshals = gs.get("marshals", {})
	for key in marshals:
		rows.append([str(key), str((marshals[key] as Dictionary).get("location", ""))])
	rows.sort()
	return rows


func _candidates(reach: Dictionary, map, min_turns: int) -> Array:
	"""Provinces in reach, at least `min_turns` away (nearest first), with no
	piece on them, whose centre is on screen clear of the edges."""
	var rows = reach.get("reach", {})
	var region_marshals: Dictionary = map.get("region_marshals")
	var view: Rect2 = map.get_global_rect()
	var out: Array = []
	for region in rows:
		var t := int((rows[region] as Dictionary).get("turns", 0))
		if t < min_turns or region_marshals.has(region):
			continue
		var p: Vector2 = map.call("screen_point_of_region", region)
		if view.grow(-120.0).has_point(p):
			out.append([t, str(region)])
	out.sort()
	return out.map(func(r): return r[1])


func _rest_on(region: String, held: bool = false) -> Dictionary:
	"""The cursor on `region` long enough for its exact quote to come back."""
	var at: Vector2 = _map().call("screen_point_of_region", region)
	await _motion(at, held)
	await _frames(20)   # the 0.15 s rest before the exact quote is fetched
	await _settle()
	await _motion(at + Vector2(1, 0), held)
	return (_main.get("_order_quotes") as Dictionary).get("dest:" + region, {})


func _walk() -> void:
	var dir_env := OS.get_environment("CC3_WALK_OUT")
	_dir = dir_env if dir_env != "" else ProjectSettings.globalize_path(OUT_DEFAULT)
	DirAccess.make_dir_recursive_absolute(_dir)
	root.mode = Window.MODE_WINDOWED
	root.position = Vector2i(5200, 20)
	root.size = Vector2i(1920, 1080)
	await _frames(4)
	var packed: PackedScene = load("res://scenes/main.tscn")
	_main = packed.instantiate()
	root.add_child(_main)
	# The boot: /test, the topology, the map shown.
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
	map.call("_set_camera_zoom_level", 1.0)   # a regional view: the pieces read
	await _frames(6)
	_main.call("_minimize_terminal")
	await _frames(3)

	# 1 — select: a click on a piece of ours on an empty line. The Emperor
	# (a sovereign never objects), so the walk's Send is answered with the
	# order itself, not a modal the frame would show instead.
	var rows := _own_rows()
	var subject := "Napoleon"
	if not rows.any(func(r): return r[0] == subject) and not rows.is_empty():
		subject = rows[0][0]
	map.call("focus_on_region", str(_main.call("_marshal_entry", subject).get("location", "")))
	await _frames(6)
	var piece: Vector2 = map.call("screen_point_of_marshal", subject)
	await _click(piece)
	await _settle()
	_out["subject"] = subject
	await _shot("1_select", "a click on %s's piece on an empty line" % subject)

	# 2 — hover: a province two or three turns off — the ghost road; at rest
	# the exact quote comes back and the badge reads its terms. The first one
	# whose quote meets no contact and no doubt is walked to the Send.
	var reach: Dictionary = _main.get("_order_reach")
	var dest := ""
	var quote: Dictionary = {}
	for region in _candidates(reach, map, 2) + _candidates(reach, map, 1):
		quote = await _rest_on(region)
		if bool(quote.get("ok", false)) and str(quote.get("contact", "")) == "" \
				and str(quote.get("objection", "none")) == "none":
			dest = region
			break
	_out["dest"] = dest
	await _shot("2_hover", "the cursor on %s: the quote's road" % dest)

	# 3 — the click: the confirm card.
	var dest_pt: Vector2 = map.call("screen_point_of_region", dest)
	await _button(dest_pt, true)
	await _button(dest_pt, false)
	await _settle()
	var card = _main.get("order_card")
	_out["dest_quote"] = quote
	await _shot("3_card", "the click on %s: the card on the exact quote" % dest)

	# 4 — Enter: the order goes down the typed road.
	_out["sent_command"] = str(card.call("command"))
	await _key(KEY_ENTER)
	await _settle()
	await _frames(10)
	_main.call("_restore_terminal")
	await _frames(4)
	_out["reply_tail"] = _terminal_tail()
	_out["modal_after_send"] = bool(_main.call("_is_modal_dialog_open"))
	await _shot("4_sent", "Enter: '%s' sent; the reply in the terminal" % _out["sent_command"])
	await _settle()

	# 5 — drag a second corps of ours across the map.
	var second := ""
	for row in rows:
		if row[0] != subject:
			second = row[0]
			break
	_main.call("_minimize_terminal")
	map.call("focus_on_region", str(_main.call("_marshal_entry", second).get("location", "")))
	await _frames(6)
	var piece2: Vector2 = map.call("screen_point_of_marshal", second)
	await _motion(piece2)
	await _button(piece2, true)
	await _motion(piece2 + Vector2(12, 0), true)
	await _settle()
	var reach2: Dictionary = _main.get("_order_reach")
	var drops := _candidates(reach2, map, 1)
	var drop: String = drops[0] if not drops.is_empty() else ""
	_out["second"] = second
	_out["drop"] = drop
	var drop_pt: Vector2 = map.call("screen_point_of_region", drop)
	await _rest_on(drop, true)
	await _shot("5_dragging", "%s's piece dragged over %s" % [second, drop])

	# 6 — released there: the card for that province.
	await _button(drop_pt, false)
	await _settle()
	var quotes2: Dictionary = _main.get("_order_quotes")
	_out["drop_quote"] = quotes2.get("dest:" + drop, {})
	await _shot("6_dropped", "released on %s: the card" % drop)
	await _key(KEY_ESCAPE)   # the card's Esc: back to the selection

	# 7 — with the selection, a click on an enemy we see: the attack card.
	var gs: Dictionary = _main.get("_last_game_state")
	var enemy := ""
	var enemies = gs.get("enemies", {})
	var seen: Array = []
	for key in enemies:
		var row: Dictionary = enemies[key]
		var p: Vector2 = map.call("screen_point_of_marshal", str(key))
		seen.append([str(key), bool(row.get("at_war_with_player", false)), p.x, p.y])
		if enemy == "" and bool(row.get("at_war_with_player", false)) and p.x >= 0.0:
			enemy = str(key)
	_out["enemies_seen"] = seen
	_out["enemy"] = enemy
	if enemy != "":
		map.call("focus_on_map_point", map.call("_get_active_region_positions").get(
			str((enemies[enemy] as Dictionary).get("location", "")), Vector2.ZERO))
		await _frames(6)
		var foe_pt: Vector2 = map.call("screen_point_of_marshal", enemy)
		await _click(foe_pt)
		await _settle()
		var quotes3: Dictionary = _main.get("_order_quotes")
		_out["enemy_quote"] = quotes3.get("enemy:" + enemy, {})
		await _shot("7_attack", "with %s selected, a click on %s" % [second, enemy])
		await _key(KEY_ESCAPE)
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

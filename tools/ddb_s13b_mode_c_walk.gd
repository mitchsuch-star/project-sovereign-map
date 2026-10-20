extends SceneTree
# DD-B's client rows — the Mode C walk (Pre-Deploy S13b part 4, October 19,
# 2026; DDB-54 … 57).
#
#   $env:SOVEREIGN_PORT = "8007"      # a backend listening there, saves sandboxed
#   $env:DDB_WALK_OUT   = "<abs dir>" # frames + walk.json land here
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/ddb_s13b_mode_c_walk.gd
#
# The REAL `main.tscn` with the REAL APIClient against a live sandboxed
# backend (never 8005 or 8006 — the player's ports). Every line is typed into
# the real command line and every key and wheel notch pushed into the viewport
# as an ENGINE event (`Viewport.push_input`) — never an operating-system
# input; the window is parked off the 5120-wide desktop.
#
#   1 tall_reply     — `help`: the reference opens at its FIRST line, the
#                      window raised to its tallest (DDB-57)
#   2 wheel          — one notch down: three whole lines (DDB-57)
#   3 short_reply    — `how strong is Mack and where is Vienna?`: the next
#                      command puts the window back; two answers (DDB-45)
#   4 screen_esc     — the Strategic Ledger open, a draft on the line, Esc:
#                      the screen closes, the line keeps its draft (DDB-54)
#   5 ally_loss      — the enemy-phase dialog: Munich taken from Bavaria,
#                      France's ally, in the colour of a loss (DDB-56; the
#                      event STAGED in the shape `main._stamp_battle_standing`
#                      stamps — the dice decide whether turn 1 gives one)
#   6 caption_start  — the title screen, 0.3 s into a crossfade: the outgoing
#                      painting still on top, still captioned (DDB-55)
#   7 caption_mid    — past the midpoint: the new painting, its caption
#
# `walk.json` records what each step read.

const WALL_LIMIT_MS := 300000
const OUT_DEFAULT := "res://../../docs/audits/ddb_s13b_client"

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


func _key(keycode: int) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = keycode
		ev.physical_keycode = keycode
		ev.pressed = pressed
		root.push_input(ev)
	await _frames(3)


func _wheel(at: Vector2, down: bool) -> void:
	for pressed in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_WHEEL_DOWN if down else MOUSE_BUTTON_WHEEL_UP
		ev.pressed = pressed
		ev.factor = 1.0
		ev.position = at
		ev.global_position = at
		root.push_input(ev, true)
	await _frames(3)


func _type(line: String) -> void:
	var input = _main.get("command_input")
	input.text = line
	input.caret_column = line.length()
	_main.call("_execute_command")
	await _settle()
	await _frames(10)


func _shot(name: String, note: String, extra: Dictionary = {}) -> void:
	var park := InputEventMouseMotion.new()
	park.position = Vector2(-40, -40)
	park.global_position = park.position
	root.push_input(park, true)
	await _frames(4)
	var img := root.get_texture().get_image()
	var path := _dir.path_join("DDB_%s_2026_10_19.jpg" % name)
	var err := img.save_jpg(path, 0.86)
	var row := {"step": name, "note": note, "frame": path.get_file(), "saved": err == OK}
	row.merge(extra)
	_out["steps"].append(row)


func _walk() -> void:
	var dir_env := OS.get_environment("DDB_WALK_OUT")
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
	var scroll: ScrollContainer = _main.get("output_scroll")

	# 1 — the reference opens at its first line, the window raised.
	var height_before := float(_main.get("_terminal_height"))
	await _type("help")
	await _frames(10)
	var display = _main.get("output_display")
	await _shot("1_tall_reply", "`help`: the reference from its first line, the window raised", {
		"height_before": height_before,
		"height_raised": float(_main.get("_terminal_height")),
		"raised": _main.get("_reply_raised") == true,
		"scroll": int(scroll.scroll_vertical),
		"reply_top": int(_main.call("_reply_top_px")),
		"scroll_max": int(scroll.get_v_scroll_bar().max_value),
	})

	# 2 — a wheel notch: three whole lines.
	var before := int(scroll.scroll_vertical)
	await _wheel(scroll.get_global_rect().get_center(), true)
	await _frames(4)
	await _shot("2_wheel", "one notch down: three whole lines", {
		"moved": int(scroll.scroll_vertical) - before,
		"line_px": float(_main.call("_output_line_px")),
	})

	# 3 — the next command: the window back; two questions, two answers.
	await _type("how strong is Mack and where is Vienna?")
	var tail: String = display.get_parsed_text()
	await _shot("3_short_reply", "the window back; two answers on two lines", {
		"height": float(_main.get("_terminal_height")),
		"raised": _main.get("_reply_raised") == true,
		"tail": tail.substr(maxi(0, tail.length() - 400)),
	})

	# 4 — a screen open, a draft on the line, Esc.
	var top_bar = _main.get("top_bar")
	top_bar.call("toggle_screen", "ledger")
	await _settle()
	await _frames(10)
	var line: LineEdit = _main.get("command_input")
	line.grab_focus()
	line.text = "Ney, fortify"
	line.caret_column = line.text.length()
	await _frames(4)
	var open_before := bool(top_bar.call("is_screen_open"))
	await _key(KEY_ESCAPE)
	await _frames(6)
	await _shot("4_screen_esc", "Esc on the line: the ledger closes, the draft stays on the focused line", {
		"screen_open_before": open_before,
		"screen_open_after": bool(top_bar.call("is_screen_open")),
		"line_focused": line.has_focus(),
		"line_text": str(line.text),
	})
	line.text = ""

	# 5 — the enemy phase: an ally's province lost reads as a loss.
	var dialog = _main.get("enemy_phase_dialog")
	if dialog != null:
		var phase := {"total_actions": 1, "nations": {"Austria": {"action_count": 1, "actions": [{
			"nation": "Austria",
			"ai_action": {"marshal": "Mack", "action": "move", "target": "Munich"},
			"events": [{"type": "conquest", "region": "Munich", "captured_from": "Bavaria",
						"captured_from_alignment": "friend"}]}]}}}
		dialog.call("show_enemy_phase", phase, int(_main.get("current_turn")))
		await _frames(10)
		await _shot("5_ally_loss", "Munich taken from Bavaria, our ally — red, not the conquest green", {
			"staged": true})
		dialog.call("_on_continue_pressed")
		await _frames(6)

	# 6 + 7 — the title screen's caption at the crossfade.
	_main.queue_free()
	await _frames(4)
	var menu = (load("res://scenes/main_menu.tscn") as PackedScene).instantiate()
	root.add_child(menu)
	await _frames(30)
	var caption: Label = menu.get("_caption")
	var first := str(caption.text)
	menu.call("_advance_slide")
	await create_timer(0.3).timeout
	await _shot("6_caption_start", "0.3 s into the crossfade: the outgoing painting and its own caption", {
		"caption": str(caption.text), "first": first})
	var fade: float = float(menu.get("FADE_SECONDS"))
	await create_timer(fade * 0.5).timeout
	await _shot("7_caption_mid", "past the midpoint: the new painting's caption", {
		"caption": str(caption.text)})
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

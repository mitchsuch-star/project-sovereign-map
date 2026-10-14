# UXR-D4 "The Side Desk" — the driven proof (Pre-Deploy S12b, Slice 3,
# October 14, 2026).
#
# The done-when: a pinned ledger survives a command, a popup and an end turn
# beside a live map. A source pin cannot show that, so this harness boots the
# REAL `main.tscn`, whose REAL client talks to a sandboxed live backend, and
# plays the Side Desk as the player would:
#
#   1. opens the Strategic Ledger by the bar's own road and presses its Pin
#      chip: the panel stands in the right third, its overlay is hidden, the
#      map takes the mouse again, and a click on Paris selects the province
#      (a click on the docked panel selects nothing);
#   2. types "Ney, fortify": Ney objects (a popup, layer 108, above the
#      ledger); the answer is Insist; the ledger re-reads (the client's own
#      request count) and stays pinned, Ney's line changed;
#   3. ends the turn: the enemy phase (layer 118) stands above the visible
#      ledger; dismissed, the chain settles, the ledger is still pinned and
#      reads the new turn;
#   4. presses Esc: the ledger unpins and closes, the map stays live, the HUD
#      band is whole again.
#
# Run by `tests/test_uxr_d4_the_side_desk.py`, which starts the backend
# (`tools/uxr3_action_probe.py` `start_backend`: an unused port from 8006,
# never 8005, its own INK_IRON_SAVE_DIR, the mock parser) and then:
#
#   SOVEREIGN_PORT=<that port> UXR_D4_OUT=<result.json> \
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --position 5200,20 --path godot-client/project-sovereign \
#           --script <abs>/tools/uxr_d4_side_desk_harness.gd
#
# Rails: it refuses the player's 8005; UiSettings is an in-memory ConfigFile
# (`_persist` false), so nothing it does reaches the player's settings; the
# window is parked past the desktop; the result JSON is written on every exit
# path, a watchdog included.
extends SceneTree

const MAIN_SCENE := "res://scenes/main.tscn"
const BOOT_MS := 120000
const IDLE_MS := 60000
const WATCHDOG_S := 480.0
const SETTLE_FRAMES := 20

var _out := {"fatal": "", "backend": "", "steps": {}, "modals_answered": []}
var _main: Node = null
var _started := false
var _finished := false


func _init():
	UiSettings._cfg = ConfigFile.new()
	var settings_class: Variant = UiSettings
	settings_class.set("_persist", false)
	# no tutor card or first-run aside over the war room
	UiSettings._cfg.set_value("tutorial", "done", true)
	UiSettings._cfg.set_value("parser", "hint_seen", true)
	UiSettings._cfg.set_value("display", "scale_acknowledged", true)
	UiSettings._cfg.set_value("display", "ui_scale", 1.0)
	UiSettings._cfg.set_value("display", "ui_scale_auto", false)
	UiSettings._cfg.set_value("display", "hud_width", "full")
	process_frame.connect(_tick)


func _tick():
	if _started:
		return
	_started = true
	create_timer(WATCHDOG_S).timeout.connect(_on_watchdog)
	_run()


func _on_watchdog() -> void:
	_fail("watchdog: the run took longer than %d s" % int(WATCHDOG_S))


# ── the run ─────────────────────────────────────────────────────────────────

func _run() -> void:
	if Utils.backend_url().ends_with(":8005"):
		_fail("refused: SOVEREIGN_PORT points at the player's 8005")
		return
	_out["backend"] = Utils.backend_url()
	root.mode = Window.MODE_WINDOWED
	root.position = Vector2i(5200, 20)
	root.size = Vector2i(1920, 1080)
	await _frames(10)
	_main = (load(MAIN_SCENE) as PackedScene).instantiate()
	root.add_child(_main)
	current_scene = _main
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < BOOT_MS:
		await process_frame
		if bool(_main.get("_initial_map_bootstrapped")) and _api_idle():
			break
	if not bool(_main.get("_initial_map_bootstrapped")):
		_fail("the war room did not boot against " + Utils.backend_url())
		return
	await _settle()
	if not await _step_pin():
		return
	if not await _step_command():
		return
	if not await _step_end_turn():
		return
	await _step_esc()
	_finish()


func _step_pin() -> bool:
	var top = _main.get("top_bar")
	var map_area: Control = _main.get("map_area")
	top.toggle_screen("ledger")
	await _settle()
	var ledger: Node = top.screens["ledger"]
	var opened := {"visible": ledger.visible, "screen_open": top.is_screen_open(),
			"map_mouse_filter": int(map_area.mouse_filter)}
	var chip: Button = ledger.get_node_or_null("PanelContainer/VBoxContainer/HeaderRow/PinChip")
	if chip == null:
		_fail("the ledger's header has no Pin chip")
		return false
	var reads := _reads()
	chip.pressed.emit()
	await _settle()
	var view := root.get_visible_rect().size
	var panel: Control = ledger.get_node("PanelContainer")
	var grip_visible := false
	for c in ledger.get_children():
		if c is ResizeGrip and (c as Control).visible:
			grip_visible = true
	var band := Utils.hud_band(view)
	var rec := {
		"opened": opened,
		"pinned": top.get_pinned_screen(), "screen_open": top.is_screen_open(),
		"visible": ledger.visible, "chip_text": chip.text,
		"overlay_visible": (ledger.get_node("BackgroundOverlay") as Control).visible,
		"grip_visible": grip_visible,
		"panel": _rect(panel), "view": [view.x, view.y],
		"dock_width": Utils.dock_width(), "band": [band.x, band.y],
		"map_mouse_filter": int(map_area.mouse_filter), "panning": bool(map_area.get("panning_enabled")),
		"terminal": _rect(_main.get("bottom_left_ui")),
		"ledger_reads_on_pin": _reads() - reads,
	}
	var war = _main.get("war_status_panel")
	if war != null and war.visible:
		rec["war_hud"] = _rect(war.get_node("PanelContainer"))
	# A click on Paris, left of the dock, selects the province.
	var paris := _map_point("Paris")
	rec["paris_point"] = [paris.x, paris.y]
	await _click(paris)
	await _settle()
	rec["selected_after_map_click"] = str(map_area.get("selected_region"))
	var region_panel = _main.get("region_panel")
	rec["region_panel_after_map_click"] = region_panel != null and region_panel.visible
	if region_panel != null and region_panel.visible and region_panel.has_method("close_panel"):
		region_panel.close_panel()
		await _settle()
	# A click on the docked panel reaches no province.
	var before := str(map_area.get("selected_region"))
	var on_panel := panel.get_global_rect().get_center()
	await _click(on_panel)
	await _settle()
	rec["selected_after_panel_click"] = str(map_area.get("selected_region"))
	rec["selected_before_panel_click"] = before
	rec["region_panel_after_panel_click"] = region_panel != null and region_panel.visible
	rec["pinned_after_clicks"] = top.get_pinned_screen()
	_out["steps"]["pin"] = rec
	return true


func _step_command() -> bool:
	var top = _main.get("top_bar")
	var ledger: Node = top.screens["ledger"]
	var reads := _reads()
	var ney_before := _ledger_line(ledger, "Ney")
	var input: LineEdit = _main.get("command_input")
	input.text = "Ney, fortify"
	_main.call("_execute_command")
	await _settle()
	var objection = _main.get("objection_dialog")
	var rec := {"ney_before": ney_before}
	rec["objection_visible"] = objection != null and objection.visible
	rec["objection_layer"] = int(objection.layer) if objection != null else -1
	rec["ledger_visible_under_popup"] = ledger.visible
	rec["ledger_layer"] = int(ledger.layer)
	rec["pinned_under_popup"] = top.get_pinned_screen()
	if objection != null and objection.visible:
		objection.call("_on_insist_pressed")
		_out["modals_answered"].append("objection_dialog: insist")
		await _settle()
	await _answer_modals()
	rec["ledger_reads"] = _reads() - reads
	rec["pinned"] = top.get_pinned_screen()
	rec["visible"] = ledger.visible
	rec["ney_after"] = _ledger_line(ledger, "Ney")
	rec["terminal_tail"] = _terminal_tail()
	_out["steps"]["command"] = rec
	return true


func _step_end_turn() -> bool:
	var top = _main.get("top_bar")
	var ledger: Node = top.screens["ledger"]
	var reads := _reads()
	var cal_before := _calendar(ledger)
	var turn_before: String = top.turn_label.text
	_main.call("_execute_end_turn")
	await _frames(5)
	if bool(_main.get("_awaiting_end_turn_confirmation")):
		# The client's lapse gate (envoys unanswered): the second press sends.
		_main.call("_execute_end_turn")
	var enemy = _main.get("enemy_phase_dialog")
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < IDLE_MS:
		await process_frame
		if enemy != null and enemy.visible:
			break
	var rec := {"turn_before": turn_before, "calendar_before": cal_before}
	rec["enemy_phase_visible"] = enemy != null and enemy.visible
	rec["enemy_phase_layer"] = int(enemy.layer) if enemy != null else -1
	rec["ledger_visible_under_popup"] = ledger.visible
	rec["pinned_under_popup"] = top.get_pinned_screen()
	rec["ledger_panel_under_popup"] = _rect(ledger.get_node("PanelContainer"))
	await _settle()
	if enemy != null and enemy.visible:
		enemy.call("_on_continue_pressed")
		_out["modals_answered"].append("enemy_phase_dialog: continue")
	await _settle()
	await _answer_modals()
	await _settle()
	rec["turn_after"] = top.turn_label.text
	rec["calendar_after"] = _calendar(ledger)
	rec["ledger_reads"] = _reads() - reads
	rec["pinned"] = top.get_pinned_screen()
	rec["visible"] = ledger.visible
	rec["panel"] = _rect(ledger.get_node("PanelContainer"))
	rec["input_enabled"] = (_main.get("command_input") as LineEdit).editable
	_out["steps"]["end_turn"] = rec
	return true


func _step_esc() -> void:
	var top = _main.get("top_bar")
	var ledger: Node = top.screens["ledger"]
	var map_area: Control = _main.get("map_area")
	root.gui_release_focus()
	await _frames(2)
	await _key(KEY_ESCAPE)
	await _settle()
	var view := root.get_visible_rect().size
	var band := Utils.hud_band(view)
	var pause = _main.get("pause_menu")
	var rec := {
		"pinned": top.get_pinned_screen(), "visible": ledger.visible,
		"map_mouse_filter": int(map_area.mouse_filter), "panning": bool(map_area.get("panning_enabled")),
		"dock_width": Utils.dock_width(), "band": [band.x, band.y], "view": [view.x, view.y],
		"pause_open": pause != null and pause.visible,
		"chip_text": str((ledger.get_node("PanelContainer/VBoxContainer/HeaderRow/PinChip") as Button).text),
	}
	# The map is live: a click on Paris still selects it.
	var paris := _map_point("Paris")
	await _click(paris)
	await _settle()
	rec["selected_after_map_click"] = str(map_area.get("selected_region"))
	_out["steps"]["esc"] = rec


# ── helpers ─────────────────────────────────────────────────────────────────

func _answer_modals() -> void:
	"""Answer whatever modal the chain raises until none stands (the probe's
	rule: the road a player takes first)."""
	var dm = _main.get("dialog_manager")
	if dm == null:
		return
	for _i in range(12):
		await _settle()
		if not dm.is_any_modal_open():
			return
		var answered := false
		for key in dm._dialogs:
			var node = dm._dialogs[key].node
			if node == null or not node.visible or not dm._dialogs[key].modal:
				continue
			for method in ["_on_continue_pressed", "_on_insist_pressed", "_on_close_pressed",
					"_on_dismiss_pressed", "_on_ok_pressed", "close_popup"]:
				if node.has_method(method):
					node.call(method)
					_out["modals_answered"].append("%s: %s" % [key, method])
					answered = true
					break
			if not answered:
				node.hide()
				_out["modals_answered"].append("%s: hide" % key)
				answered = true
			break


func _api_idle() -> bool:
	var api = _main.get("api_client") if _main != null and is_instance_valid(_main) else null
	if api == null or not is_instance_valid(api):
		return true
	var busy = bool(api.get("_request_in_flight"))
	var queue = api.get("_request_queue")
	return not busy and (queue == null or queue.is_empty())


func _settle() -> void:
	var start := Time.get_ticks_msec()
	var calm := 0
	while Time.get_ticks_msec() - start < IDLE_MS:
		await process_frame
		if _api_idle():
			calm += 1
			if calm >= SETTLE_FRAMES:
				return
		else:
			calm = 0


func _frames(n: int) -> void:
	for _i in range(n):
		await process_frame


func _reads() -> int:
	var api = _main.get("api_client")
	var counts = api.get("sent_counts") if api != null else null
	return int((counts as Dictionary).get("/ledger", 0)) if counts is Dictionary else -1


func _rect(c) -> Array:
	if c == null or not (c is Control):
		return []
	var r := (c as Control).get_global_rect()
	return [r.position.x, r.position.y, r.size.x, r.size.y]


func _map_point(region: String) -> Vector2:
	"""A province's anchor on the screen (logical px, the window at scale 1)."""
	var map_area = _main.get("map_area")
	var positions: Dictionary = map_area.call("_get_active_region_positions")
	if not positions.has(region):
		return Vector2(-1, -1)
	var vp: float = float(map_area.call("_viewport_pixel_scale"))
	var xf: Transform2D = map_area.map_viewport.canvas_transform
	return (map_area as Control).global_position + (xf * Vector2(positions[region])) / vp


func _click(at: Vector2) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = at
	motion.global_position = at
	root.push_input(motion)
	await _frames(3)
	for pressed in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = pressed
		ev.position = at
		ev.global_position = at
		root.push_input(ev)
		await _frames(2)


func _key(keycode: int) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = keycode
		ev.physical_keycode = keycode
		ev.pressed = pressed
		root.push_input(ev)
		await _frames(2)


func _calendar(ledger: Node) -> String:
	var cd = ledger.get("cached_data")
	return str(cd.get("calendar_label", "")) if cd is Dictionary else ""


func _ledger_line(ledger: Node, name: String) -> String:
	var content: RichTextLabel = ledger.get("content_area")
	if content == null:
		return ""
	var text := content.get_parsed_text()
	var at := text.find("\n" + name + " ")
	if at < 0:
		return ""
	return text.substr(at + 1, 160).strip_edges()


func _terminal_tail() -> String:
	var out_display: RichTextLabel = _main.get("output_display")
	if out_display == null:
		return ""
	var text := out_display.get_parsed_text().strip_edges()
	return text.substr(maxi(0, text.length() - 400))


func _fail(msg: String) -> void:
	if _out["fatal"] == "":
		_out["fatal"] = msg
	_finish()


func _finish() -> void:
	if _finished:
		return
	_finished = true
	var path := OS.get_environment("UXR_D4_OUT")
	if path == "":
		path = "user://uxr_d4_side_desk.json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(_out, " "))
		f.close()
	quit(0 if _out["fatal"] == "" else 1)

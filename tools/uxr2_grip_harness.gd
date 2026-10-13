# UXR-2 Slice C — the grips, DRIVEN (Pre-Deploy S9, October 12, 2026).
#
# The layout law's done-when says the big screens "resize and remember". A
# source pin cannot show that, so this harness boots the REAL `main.tscn`
# headlessly (the CX-7 shape: an API stub swapped in before `_ready` can
# fetch, a `process_frame` tick with a hard frame cap) and, for each of the
# six top-bar screens, presses real mouse events onto its grip:
#
#   open → the grip sits on the panel's bottom-right corner
#   press + drag (+80, −60) + release → the panel is 160 wider and 120 lower
#     (it grows about its centre), the screen stayed open (the press never
#     reached the close-on-click overlay), the size is stored
#   close → reopen → the stored size returns
#   double-click → the authored size returns, the stored one is forgotten
#
# then, with a screen grown wide, raises the Interface Scale and checks the
# open panel was refit inside the new logical viewport (the clamp ran on open
# only before UXR-2), and runs Reset layout.
#
# `UiSettings` is an in-memory ConfigFile with `_persist = false` (set
# through a Variant), so no grip commit ever writes the player's file.
#
#   Godot --headless --path godot-client/project-sovereign \
#         --script ../../tools/uxr2_grip_harness.gd
#
# Writes one JSON object to $UXR2_OUT (default user://uxr2_grips.json). Read
# by `tests/test_uxr2_grips_driven.py`, which SKIPS without the engine.
extends SceneTree

const HARD_FRAME_LIMIT := 3000
const SCREENS := ["ledger", "generals", "dispatch", "event_log", "gazette", "diplomatic_ledger"]
const DRAG := Vector2(80.0, -60.0)


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "uxr2 stub"})

	func test_connection(cb = null): _answer("test_connection", cb)
	func get_map_topology(_cb = null): calls.append("get_map_topology")
	func get_ledger(cb = null): _answer("get_ledger", cb)
	func get_diplomatic_ledger(cb = null): _answer("get_diplomatic_ledger", cb)
	func get_marshal_overview(cb = null): _answer("get_marshal_overview", cb)
	func get_dispatch(cb = null): _answer("get_dispatch", cb)
	func get_gazette(cb = null): _answer("get_gazette", cb)
	func get_campaign_log(cb = null): _answer("get_campaign_log", cb)
	func get_mailbox(cb = null): _answer("get_mailbox", cb)
	func get_pending_envoy(cb = null): _answer("get_pending_envoy", cb)
	func send_command(_c, _cb = null): calls.append("send_command")
	func cancel_strategic_order(_m, _cb = null): calls.append("cancel_strategic_order")
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")


var _frames := 0
var _phase := "window"
var _wait := 0
var _main: Node = null
var _api: ApiStub = null
var _top_bar = null
var _i := 0
var _rec := {}
var _out := {"screens": {}}
var _fatal := ""


func _init():
	UiSettings._cfg = ConfigFile.new()
	var settings_class: Variant = UiSettings
	settings_class.set("_persist", false)
	# no tutor card or first-run aside over the screens' corners
	UiSettings._cfg.set_value("tutorial", "done", true)
	UiSettings._cfg.set_value("parser", "hint_seen", true)
	UiSettings._cfg.set_value("display", "scale_acknowledged", true)
	UiSettings._cfg.set_value("display", "ui_scale", _env_float("UXR2_SCALE", 1.0))
	UiSettings._cfg.set_value("display", "ui_scale_auto", false)
	# UXR-D3 (Pre-Deploy S9b): UXR2_MODE=band measures the HUD against the
	# band at UXR2_RES (e.g. 5120x1440) with UXR2_HUD (full / centred).
	UiSettings._cfg.set_value("display", "hud_width", OS.get_environment("UXR2_HUD") if OS.get_environment("UXR2_HUD") != "" else "full")
	process_frame.connect(_tick)


func _env_float(key: String, fallback: float) -> float:
	var v := OS.get_environment(key)
	return float(v) if v.is_valid_float() else fallback


func _band_mode() -> bool:
	return OS.get_environment("UXR2_MODE") == "band"


func _tick():
	_frames += 1
	if _frames > HARD_FRAME_LIMIT:
		_fatal = "frame limit hit in phase %s (screen %d)" % [_phase, _i]
		_finish()
		return
	if _wait > 0:
		_wait -= 1
		return
	call("_" + _phase)


func _window():
	# The project boots maximized; the IQ-10 capture's own rail (set on the
	# first tick — in `_init` the project's maximize lands after it): a
	# windowed 1600x900, parked past the desktop, never on the player's screen.
	root.mode = Window.MODE_WINDOWED
	root.position = Vector2i(5200, 20)
	var res := OS.get_environment("UXR2_RES").split("x")
	if res.size() == 2 and res[0].is_valid_int() and res[1].is_valid_int():
		root.size = Vector2i(int(res[0]), int(res[1]))
	else:
		root.size = Vector2i(1600, 900)
	_phase = "boot"
	_wait = 10


func _boot():
	var packed: PackedScene = load("res://scenes/main.tscn")
	if packed == null:
		_fatal = "main.tscn did not load"
		_finish()
		return
	_main = packed.instantiate()
	_api = ApiStub.new()
	_api.name = "APIClient"
	var real = _main.get_node_or_null("APIClient")
	if real != null:
		_main.remove_child(real)
		real.queue_free()
	_main.add_child(_api)
	root.add_child(_main)
	if "api_client" in _main:
		_main.set("api_client", _api)
	_phase = "settle"
	_wait = 40


func _settle():
	if "api_client" in _main:
		_main.set("api_client", _api)
	_top_bar = _main.get("top_bar")
	if _top_bar == null:
		_fatal = "the top bar never resolved"
		_finish()
		return
	# The screens open through the TOP BAR's client, which main.gd handed the
	# real APIClient in its `_ready` — swap the stub in there too, or every
	# open sends a real GET to the backend (the review's P2).
	_top_bar.set_api_client(_api)
	# Belt and braces: never run against the player's live backend.
	if Utils.backend_url().ends_with(":8005"):
		_fatal = "refusing to run against the live 8005 backend: set SOVEREIGN_PORT"
		_finish()
		return
	_out["viewport"] = [root.get_visible_rect().size.x, root.get_visible_rect().size.y]
	_out["terminal_grip"] = _main.get("resize_grip") != null
	_phase = "band_show" if _band_mode() else "open"


# ── per screen ────────────────────────────────────────────────────────────

func _screen() -> Node:
	return _top_bar.screens.get(SCREENS[_i])


func _panel() -> Control:
	var s := _screen()
	return s.get_node_or_null("PanelContainer") if s != null else null


func _grip() -> Control:
	var s := _screen()
	return s.get_node_or_null("ResizeGrip") if s != null else null


func _mouse(pos: Vector2, pressed: bool, double: bool = false) -> void:
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = pressed
	ev.double_click = double
	ev.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
	ev.position = pos
	ev.global_position = pos
	root.push_input(ev)


func _motion(pos: Vector2, rel: Vector2) -> void:
	var ev := InputEventMouseMotion.new()
	ev.button_mask = MOUSE_BUTTON_MASK_LEFT
	ev.position = pos
	ev.global_position = pos
	ev.relative = rel
	root.push_input(ev)


func _grip_center() -> Vector2:
	var g := _grip()
	return g.position + g.size * 0.5


func _open():
	_rec = {"name": SCREENS[_i]}
	if _screen() == null:
		_rec["error"] = "screen not registered"
		_next_screen()
		return
	_top_bar.toggle_screen(SCREENS[_i])
	_phase = "measure_open"
	_wait = 8


func _measure_open():
	var panel := _panel()
	var grip := _grip()
	_rec["open"] = _screen().visible
	_rec["grip"] = grip != null
	if panel == null or grip == null:
		_rec["error"] = "no panel or no grip"
		_next_screen()
		return
	_rec["grip_visible"] = grip.visible
	_rec["authored"] = [panel.size.x, panel.size.y]
	var corner := panel.get_global_rect().end
	_rec["grip_gap"] = (_grip_center() - corner).length()
	_mouse(_grip_center(), true)
	_phase = "drag"
	_wait = 2


func _drag():
	var start := _grip_center()
	_motion(start + DRAG * 0.5, DRAG * 0.5)
	_motion(start + DRAG, DRAG * 0.5)
	_phase = "release"
	_wait = 3


func _release():
	_mouse(_grip_center(), false)
	_phase = "measure_drag"
	_wait = 4


func _measure_drag():
	var panel := _panel()
	_rec["after_drag"] = [panel.size.x, panel.size.y]
	_rec["open_after_drag"] = _screen().visible
	var key: String = SCREENS[_i]
	_rec["stored"] = UiSettings.has_panel_size(key)
	var stored := UiSettings.get_panel_size(key, Vector2.ZERO)
	_rec["stored_size"] = [stored.x, stored.y]
	_rec["grip_gap_after"] = (_grip_center() - panel.get_global_rect().end).length()
	_top_bar.toggle_screen(key)
	_phase = "reopen"
	_wait = 4


func _reopen():
	_rec["closed"] = not _screen().visible
	# The reopened size must come from the STORE (UiSettings), as it does in
	# a new session — not from the meta the drag left on this same node.
	_panel().remove_meta("clamp_user_size")
	_top_bar.toggle_screen(SCREENS[_i])
	_phase = "measure_reopen"
	_wait = 8


func _measure_reopen():
	var panel := _panel()
	_rec["reopened"] = [panel.size.x, panel.size.y]
	# a double-click on the grip: the authored size, the stored one forgotten
	_mouse(_grip_center(), true, true)
	_phase = "dbl_release"
	_wait = 2


func _dbl_release():
	_mouse(_grip_center(), false)
	_phase = "measure_reset"
	_wait = 4


func _measure_reset():
	var panel := _panel()
	_rec["after_double_click"] = [panel.size.x, panel.size.y]
	_rec["stored_after_double_click"] = UiSettings.has_panel_size(SCREENS[_i])
	_rec["open_after_double_click"] = _screen().visible
	# a click that does not move stores nothing
	_mouse(_grip_center(), true)
	_phase = "click_release"
	_wait = 2


func _click_release():
	_mouse(_grip_center(), false)
	_phase = "measure_click"
	_wait = 3


func _measure_click():
	_rec["stored_after_click"] = UiSettings.has_panel_size(SCREENS[_i])
	_top_bar.toggle_screen(SCREENS[_i])
	_out["screens"][SCREENS[_i]] = _rec
	_next_screen()


func _next_screen():
	if _rec.has("name") and not _out["screens"].has(_rec["name"]):
		_out["screens"][_rec["name"]] = _rec
	_i += 1
	if _i < SCREENS.size():
		_phase = "open"
		_wait = 4
	else:
		_i = 0
		_phase = "ws_show"
		_wait = 4


# ── the war HUD (Slice D): an EDGE grip on its top-left corner ────────────

func _ws() -> Node:
	return _main.get("war_status_panel")


func _ws_panel() -> Control:
	var ws := _ws()
	return ws.get_node_or_null("PanelContainer") if ws != null else null


func _ws_grip() -> Control:
	var ws := _ws()
	return ws.get_node_or_null("ResizeGrip") if ws != null else null


func _ws_grip_center() -> Vector2:
	var g := _ws_grip()
	return g.position + g.size * 0.5


func _ws_show():
	var ws := _ws()
	if ws == null:
		_out["ws_error"] = "no war_status_panel"
		_phase = "scale_open"
		return
	ws.show()
	ws.call("_fit_panel_to_content")
	_phase = "ws_press"
	_wait = 8


func _ws_press():
	var panel := _ws_panel()
	var grip := _ws_grip()
	_out["ws_grip"] = grip != null
	if panel == null or grip == null:
		_phase = "scale_open"
		return
	_out["ws_before"] = [panel.size.x, panel.size.y]
	_out["ws_grip_gap"] = (_ws_grip_center() - panel.get_global_rect().position).length()
	_mouse(_ws_grip_center(), true)
	_phase = "ws_drag"
	_wait = 2


func _ws_drag():
	var start := _ws_grip_center()
	_motion(start + Vector2(-40.0, -10.0), Vector2(-40.0, -10.0))
	_motion(start + Vector2(-80.0, -20.0), Vector2(-40.0, -10.0))
	_phase = "ws_release"
	_wait = 3


func _ws_release():
	_mouse(_ws_grip_center(), false)
	_phase = "ws_measure"
	_wait = 6


func _ws_measure():
	var panel := _ws_panel()
	_out["ws_after_drag"] = [panel.size.x, panel.size.y]
	_out["ws_stored"] = UiSettings.has_panel_size("war_status")
	_ws().hide()
	_phase = "ws_reshow"
	_wait = 3


func _ws_reshow():
	_ws().show()
	_ws().call("_fit_panel_to_content")
	_phase = "ws_measure_reshow"
	_wait = 6


func _ws_measure_reshow():
	var panel := _ws_panel()
	_out["ws_after_reshow"] = [panel.size.x, panel.size.y]
	_mouse(_ws_grip_center(), true, true)
	_phase = "ws_dbl_release"
	_wait = 2


func _ws_dbl_release():
	_mouse(_ws_grip_center(), false)
	_phase = "ws_measure_dbl"
	_wait = 6


func _ws_measure_dbl():
	var panel := _ws_panel()
	_out["ws_after_dbl"] = [panel.size.x, panel.size.y]
	_out["ws_stored_after_dbl"] = UiSettings.has_panel_size("war_status")
	_ws().hide()
	_phase = "scale_open"
	_wait = 4


# ── the refit road and Reset layout ───────────────────────────────────────

func _scale_open():
	_top_bar.toggle_screen("ledger")
	_phase = "scale_grow"
	_wait = 8


func _scale_grow():
	# grow the ledger wide (stored), then raise the Interface Scale under it
	_mouse(_grip_center(), true)
	_phase = "scale_drag"
	_wait = 2


func _scale_drag():
	var start := _grip_center()
	_motion(start + Vector2(140.0, 0.0), Vector2(140.0, 0.0))
	_phase = "scale_release"
	_wait = 3


func _scale_release():
	_mouse(_grip_center(), false)
	_phase = "scale_apply"
	_wait = 4


func _scale_apply():
	_out["refit_before"] = [_panel().size.x, _panel().size.y]
	_main.call("_apply_ui_scale", 1.5, false)
	_phase = "scale_measure"
	_wait = 10


func _scale_measure():
	var view := root.get_visible_rect().size
	var r := _panel().get_global_rect()
	_out["refit_view"] = [view.x, view.y]
	_out["refit_rect"] = [r.position.x, r.position.y, r.end.x, r.end.y]
	_out["refit_inside"] = (r.position.x >= -0.5 and r.position.y >= -0.5
			and r.end.x <= view.x + 0.5 and r.end.y <= view.y + 0.5)
	_out["refit_grip_gap"] = (_grip_center() - r.end).length()
	_main.call("_apply_ui_scale", 1.0, false)
	_phase = "reset_layout"
	_wait = 10


func _reset_layout():
	_out["stored_before_reset"] = UiSettings.has_panel_size("ledger")
	UiSettings.reset_layout()
	_main.call("_on_layout_reset")
	_phase = "reset_measure"
	_wait = 10


func _reset_measure():
	var any := false
	for key in SCREENS:
		any = any or UiSettings.has_panel_size(key)
	_out["stored_after_reset"] = any
	_out["ledger_after_reset"] = [_panel().size.x, _panel().size.y]
	# Reset layout returns the scale to the DERIVATION too, so the authored
	# rect is clamped to the logical viewport that scale leaves.
	var view := root.get_visible_rect().size
	_out["reset_view"] = [view.x, view.y]
	_out["ledger_authored"] = _out["screens"]["ledger"].get("authored", [])
	_top_bar.toggle_screen("ledger")
	_phase = "text_open"
	_wait = 6


# ── UXR-D1 (Pre-Deploy S9b): the Text size slider, driven live ──────────────

func _text_slider() -> HSlider:
	var pm = _main.get("pause_menu")
	return (pm.find_child("TextSizeSlider", true, false) as HSlider) if pm != null else null


func _text_sizes() -> Dictionary:
	# A theme-sized node of each family on the live war room: the command
	# line (LineEdit 16), the output (RichTextLabel 16), the slider's own hint
	# rows in the pause menu (Caption 14), and the terminal's footprint.
	var out := {}
	var input = _main.get("command_input")
	if input is Control:
		out["line_edit"] = (input as Control).get_theme_font_size("font_size")
	var output = _main.get("output_display")
	if output is Control:
		out["rich"] = (output as Control).get_theme_font_size("normal_font_size")
	var slider := _text_slider()
	if slider != null:
		var row := slider.get_parent()
		var caption := row.get_child(0) as Label if row != null else null
		if caption != null:
			out["caption"] = caption.get_theme_font_size("font_size")
	var term = _main.get_node_or_null("BottomLeftUI")
	if term is Control:
		out["terminal"] = [(term as Control).size.x, (term as Control).size.y]
		# What floors the command window's width: each row's own minimum.
		var rows := {}
		for row_name in ["TitleRow", "StatusSection", "InputSection"]:
			var row := (term as Control).find_child(row_name, true, false) as Control
			if row != null:
				rows[row_name] = row.get_combined_minimum_size().x
		out["rows_min_width"] = rows
		# the footprint the window was ASKED for (its fraction or the grip's)
		out["requested"] = [float(_main.get("_terminal_width")), float(_main.get("_terminal_height"))]
	out["stored"] = UiSettings.get_text_size()
	return out


func _text_open():
	var pm = _main.get("pause_menu")
	if pm == null:
		_out["text_size"] = {"error": "no pause menu"}
		_finish()
		return
	pm.call("open_menu")
	pm.call("_on_settings")
	_phase = "text_drive"
	_wait = 10


func _text_drive():
	var slider := _text_slider()
	if slider == null:
		_out["text_size"] = {"error": "no TextSizeSlider in Settings"}
		_finish()
		return
	_out["text_size"] = {"before": _text_sizes(), "range": [slider.min_value, slider.max_value]}
	# A click on the slider (not a drag): applied AND persisted at once.
	slider.value = 1.5
	_phase = "text_measure"
	_wait = 10


func _text_measure():
	_out["text_size"]["at_150"] = _text_sizes()
	# Reset layout from the panel itself returns the text to 100 %.
	var panel = _text_slider()
	while panel != null and not (panel is SettingsPanel):
		panel = panel.get_parent()
	if panel != null:
		panel.call("_on_reset_layout")
	_phase = "text_reset_measure"
	_wait = 10


func _text_reset_measure():
	_out["text_size"]["after_reset"] = _text_sizes()
	var pm = _main.get("pause_menu")
	if pm != null:
		pm.call("close_menu")
	_finish()


# ── UXR-D3 (Pre-Deploy S9b): the HUD band, driven ──────────────────────────

func _rect_of(c) -> Array:
	if not (c is Control) or not (c as Control).is_visible_in_tree():
		return []
	var r: Rect2 = (c as Control).get_global_rect()
	return [r.position.x, r.position.y, r.end.x, r.end.y]


func _band_show():
	# the war HUD and the region panel on screen, as a campaign has them
	var ws := _ws()
	if ws != null:
		ws.show()
		ws.call("_fit_panel_to_content")
	var rp = _main.get("region_panel")
	if rp != null:
		rp.show()
		rp.call("_fit_width")
	_phase = "band_measure"
	_wait = 12


func _band_measure():
	var view := root.get_visible_rect().size
	var band := Utils.hud_band(view)
	_out["band"] = {"view": [view.x, view.y], "band": [band.x, band.y],
			"hud_width": UiSettings.get_hud_width()}
	var rects := {}
	rects["terminal"] = _rect_of(_main.get_node_or_null("BottomLeftUI"))
	rects["screen_buttons"] = _rect_of(_top_bar.get_node_or_null("BarContainer/BarBG/BarLayout/ScreenButtons"))
	rects["right_section"] = _rect_of(_top_bar.get_node_or_null("BarContainer/BarBG/BarLayout/RightSection"))
	rects["bar_strip"] = _rect_of(_top_bar.get_node_or_null("BarContainer"))
	rects["rail_slot"] = _rect_of(_top_bar.get("notification_area"))
	rects["war_hud"] = _rect_of(_ws_panel())
	var rp = _main.get("region_panel")
	rects["region_panel"] = _rect_of(rp.get_node_or_null("PanelContainer")) if rp != null else []
	rects["map_controls"] = _rect_of(_main.get("map_controls"))
	_out["band"]["rects"] = rects
	# the minimized window's restore button rides the band too
	_main.call("_minimize_terminal")
	_phase = "band_restore"
	_wait = 6


func _band_restore():
	_out["band"]["rects"]["restore_button"] = _rect_of(_main.get_node_or_null("RestoreButton"))
	_main.call("_restore_terminal")
	# ⌂ Fit Europe: zoom in three steps, then press the chip
	var map = _main.get("map_area")
	_out["band"]["zoom_fit"] = float(map.call("_get_initial_zoom_level"))
	for i in 3:
		map.call("zoom_step", true)
	_phase = "band_zoomed"
	_wait = 4


func _band_zoomed():
	# mid-ease (the zoom tween still running): ⌂ must still land on the fit
	var map = _main.get("map_area")
	_out["band"]["zoom_in"] = float(map.get("_zoom_level"))
	var fit := (_main.get("map_controls") as Node).find_child("FitEuropeButton", true, false) as Button
	_out["band"]["fit_button"] = fit != null and fit.focus_mode == Control.FOCUS_NONE
	if fit != null:
		fit.pressed.emit()
	_phase = "band_fit"
	_wait = 40


func _band_fit():
	var map = _main.get("map_area")
	_out["band"]["zoom_after_fit"] = float(map.get("_zoom_level"))
	_finish()


func _finish():
	_out["fatal"] = _fatal
	_out["frames"] = _frames
	var text := JSON.stringify(_out)
	var path := OS.get_environment("UXR2_OUT")
	if path == "":
		path = "user://uxr2_grips.json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(text)
		f.close()
	print("[uxr2] " + text)
	quit(0)

extends SceneTree
# =============================================================================
# Session UI-4 (November 12, 2026) — the levers past 7, DRIVEN (headless).
# Read by tests/test_ui_gilt4_levers.py. Runs the real scripts under Godot
# 4.4.1 headless and writes ONE JSON object to $UI_GILT4_OUT:
#
#   type   — the shipped Text size (115 %, the user's ruling) applied to the
#            project theme: the default 16 → 18, a Caption 14 → 16; an inline
#            glyph grows with the words, a meter does not;
#   band   — Utils.hud_band_full on a 32:9 view: Auto at the screen's edges
#            while the map fills the width (the user's "Screen edges"), the
#            16:9 zone while it shows the whole sheet and under "16:9"; the
#            room panels SIZE against is the zone either way;
#   chips  — a locked chip has no box and a lock before its name; a live
#            chip's rim is at full strength; the signed meter's halves;
#   clear  — the war list never stands on the command window: beside it when
#            there is room, risen above it when there is not.
# =============================================================================

var _out := {}
var _frames := 0
var _war = null
var _term: Control = null


func _init() -> void:
	UiSettings._cfg = ConfigFile.new()
	var settings_class: Variant = UiSettings
	settings_class.set("_persist", false)
	_probe_type()
	_probe_band()
	_probe_chips()
	_stage_clear()
	process_frame.connect(_tick)


func _tick() -> void:
	# The war list's @onready nodes fill when it enters the tree — a frame or
	# two after _init; then the clearing is read and the record written.
	_frames += 1
	if _frames < 4:
		return
	process_frame.disconnect(_tick)
	_probe_clear()
	var path := OS.get_environment("UI_GILT4_OUT")
	if path != "":
		var f := FileAccess.open(path, FileAccess.WRITE)
		f.store_string(JSON.stringify(_out))
		f.close()
	quit(0)


func _probe_type() -> void:
	var theme: Theme = ThemeDB.get_project_theme()
	var before := {"default": theme.default_font_size if theme != null else -1,
		"caption": theme.get_font_size("font_size", "Caption") if theme != null else -1}
	Utils.apply_text_size()
	_out["type"] = {
		"shipped": UiSettings.DEFAULT_TEXT_SIZE,
		"stored": UiSettings.get_text_size(),
		"before": before,
		"after": {"default": theme.default_font_size if theme != null else -1,
			"caption": theme.get_font_size("font_size", "Caption") if theme != null else -1},
		"factor": Utils.text_size_factor(),
		"glyph": Utils.bb_glyph("gold", 18),
		"flag_px": Utils.text_px(14),
		"meter": Utils.bb_meter(5.0, 10.0, 100, 8),
	}


func _probe_band() -> void:
	var wide := Vector2(3200, 900)
	var plain := Vector2(1600, 900)
	var res := {}
	for case in [["auto", "fill"], ["auto", "sheet"], ["16:9", "fill"], ["full", "fill"], ["centred", "fill"]]:
		UiSettings.set_hud_width(case[0])
		UiSettings.set_wide_map(case[1])
		var key: String = case[0] + "/" + case[1]
		res[key] = {
			"band": [Utils.hud_band_full(wide).x, Utils.hud_band_full(wide).y],
			"room": Utils.hud_size_room(wide),
			"plain": [Utils.hud_band_full(plain).x, Utils.hud_band_full(plain).y],
			"plain_room": Utils.hud_size_room(plain),
		}
	UiSettings.set_hud_width(UiSettings.DEFAULT_HUD_WIDTH)
	UiSettings.set_wide_map(UiSettings.DEFAULT_WIDE_MAP)
	res["widths"] = UiSettings.HUD_WIDTHS
	_out["band"] = res


func _probe_chips() -> void:
	_out["chips"] = {
		"locked": Utils.bb_chip_disabled("Cede Province", "", "No eligible province"),
		"live": Utils.bb_button_chip("vassal:loosen:Holland", "Loosen Rein", "7eb8da", "233043"),
		"signed_loss": Utils.bb_signed_meter(-35.0, 40.0, 160, 8),
		"signed_win": Utils.bb_signed_meter(15.0, 15.0, 160, 8),
		"signed_zero_cap": Utils.bb_signed_meter(3.0, 0.0, 160, 8),
	}


func _stage_clear() -> void:
	# The war list and a stand-in command window in one 800 x 450 SubViewport
	# (Interface Scale 2.0 on a 1600 x 900 screen) — the readers' frame.
	var vp := SubViewport.new()
	vp.size = Vector2i(800, 450)
	root.add_child(vp)
	var host := Control.new()
	host.size = Vector2(800, 450)
	vp.add_child(host)
	_war = load("res://scenes/war_status_panel.tscn").instantiate()
	vp.add_child(_war)
	_term = Control.new()
	_term.position = Vector2(12, 155)
	_term.size = Vector2(462, 283)
	host.add_child(_term)


func _probe_clear() -> void:
	var war = _war
	var term := _term
	war.avoid_control = term
	var pc: Control = war.panel_container
	var place := func(left: float, right: float, top: float, bottom: float) -> void:
		pc.anchor_left = 1.0
		pc.anchor_right = 1.0
		pc.anchor_top = 0.0
		pc.anchor_bottom = 0.0
		pc.offset_left = left
		pc.offset_right = right
		pc.offset_top = top
		pc.offset_bottom = bottom
	var res := {}
	# 1 — room beside: the list narrows to stand right of the window.
	place.call(-331.0, -12.0, 147.0, 249.0)
	war._clear_the_command_window(Vector2(800, 450))
	res["beside"] = [pc.offset_left, pc.offset_right, pc.offset_top, pc.offset_bottom]
	# 2 — no room beside (a wide window): the list rises above it.
	term.size = Vector2(700, 283)
	place.call(-331.0, -12.0, 147.0, 249.0)
	war._clear_the_command_window(Vector2(800, 450))
	res["above"] = [pc.offset_left, pc.offset_right, pc.offset_top, pc.offset_bottom]
	# 3 — apart already: untouched.
	term.size = Vector2(300, 100)
	term.position = Vector2(12, 340)
	place.call(-331.0, -12.0, 147.0, 249.0)
	war._clear_the_command_window(Vector2(800, 450))
	res["apart"] = [pc.offset_left, pc.offset_right, pc.offset_top, pc.offset_bottom]
	res["gap"] = war.AVOID_GAP
	_out["clear"] = res

extends SceneTree
# =============================================================================
# Session UI-2 (November 11, 2026) — the imperial desk's kit, DRIVEN (headless).
# =============================================================================
# Read by tests/test_ui_gilt2_imperial_desk.py. Runs the real scripts under
# Godot 4.4.1 headless and writes ONE JSON object to $UI_GILT2_OUT:
#
#   button  — scripts/gilt_button.gd: StyleBoxFlat's names survive a duplicate
#             (a tint written at run time), it is NOT a StyleBoxFlat, and the
#             theme's five Button states and the parchment steps are its faces;
#   rows    — map_renderer_base.name_rows: co-located names never touch (the
#             zig-zag; the column when two on one row would);
#   tables  — a page with a striped table and a portrait row whose cell holds
#             newlines keeps the card underlay's precondition: the label's
#             paragraphs are the newlines OUTSIDE tables (Utils.flatten_tables);
#   heads   — Utils.dress_heads turns the capital headings into the title face
#             and leaves their words; Utils.bb_meter / bb_relation_meter / the
#             chip draw the segments and the rim they promise;
#   band    — Utils.hud_band_full: Auto is the whole view on 16:9 and a 16:9
#             safe zone about the centre on 32:9; the derivation gives 1.60 at
#             5120 x 1440.
# =============================================================================

var _out := {}
var _frames := 0
var _label: RichTextLabel = null
var _page := ""


func _init() -> void:
	UiSettings._cfg = ConfigFile.new()
	var settings_class: Variant = UiSettings
	settings_class.set("_persist", false)
	_probe_button()
	_probe_rows()
	_probe_heads()
	_probe_band()
	_build_page()
	process_frame.connect(_tick)


func _probe_button() -> void:
	var b: StyleBox = load("res://scripts/gilt_button.gd").new()
	b.set("border_color", Color(0.8, 0.4, 0.4, 1.0))
	b.set("bg_color", Color(0.1, 0.2, 0.3, 1.0))
	b.content_margin_left = 12.0
	var copy: StyleBox = b.duplicate()
	var theme: Theme = load("res://ui/main_theme.tres")
	var faces := {}
	for state in ["normal", "hover", "pressed", "disabled"]:
		var box := theme.get_stylebox(state, "Button")
		faces[state] = {"scripted": box.get_script() != null and str(box.get_script().resource_path).ends_with("gilt_button.gd"),
			"dashed": bool(box.get("dashed")) if "dashed" in box else false}
	var parch := theme.get_stylebox("normal", "ParchmentButton")
	_out["button"] = {
		"is_flat": b is StyleBoxFlat,
		"has_border_color": "border_color" in b,
		"copy_border": copy.get("border_color").to_html(),
		"copy_bg": copy.get("bg_color").to_html(),
		"copy_margin": copy.content_margin_left,
		"faces": faces,
		"parchment_scripted": parch.get_script() != null,
		"steps": {
			"EndTurnButton": theme.get_font_size("font_size", "EndTurnButton"),
			"ParchmentButton": theme.get_font_size("font_size", "ParchmentButton"),
			"StatFigure": theme.get_font_size("font_size", "StatFigure"),
			"Figure": theme.get_font_size("font_size", "Figure"),
		},
	}


func _probe_rows() -> void:
	var renderer = load("res://scenes/map_renderer_base.gd")
	var cases := []
	# three pieces 38 px apart, names ~60 px: the zig-zag fits
	cases.append({"xs": [-38.0, 0.0, 38.0], "ws": [60.0, 64.0, 58.0]})
	# three long names: the column
	cases.append({"xs": [-38.0, 0.0, 38.0], "ws": [110.0, 96.0, 104.0]})
	# two names
	cases.append({"xs": [-19.0, 19.0], "ws": [70.0, 66.0]})
	var results := []
	for c in cases:
		var rows: Array = renderer.name_rows(c["xs"], c["ws"], 2.0)
		# the plates' rects: row r at height r, centred at the given x
		var overlap := false
		for i in range(rows.size()):
			for j in range(i + 1, rows.size()):
				if int(rows[i][0]) != int(rows[j][0]):
					continue
				var half := (float(c["ws"][i]) + float(c["ws"][j])) * 0.5
				if absf(float(rows[i][1]) - float(rows[j][1])) < half:
					overlap = true
		results.append({"rows": rows, "overlap": overlap})
	_out["rows"] = results


func _probe_heads() -> void:
	var src := "[color=#B8860B]═══ FORCES ═══[/color]\n[color=#B8860B]THE SEA[/color]\n[color=#B8860B]════════════[/color]\n"
	var dressed := Utils.dress_heads(src)
	_out["heads"] = {
		"dressed": dressed,
		"meter": Utils.bb_meter(3.0, 10.0, 100, 8, "aabbcc"),
		"relation": Utils.bb_relation_meter(-50, 100, 7),
		"chip": Utils.bb_button_chip("order:drill:Ney", "Drill now", "d9c08c", "233043"),
		"chip_off": Utils.bb_chip_disabled("Fall back"),
		"flatten": Utils.flatten_tables("a\n[table=2][cell]x\ny[/cell][cell]z[/cell][/table]\nb"),
	}


func _probe_band() -> void:
	UiSettings._cfg.set_value("display", "hud_width", "auto")
	var wide := Utils.hud_band_full(Vector2(3200, 900))
	var std := Utils.hud_band_full(Vector2(1600, 900))
	_out["band"] = {
		"auto_wide": [wide.x, wide.y],
		"auto_std": [std.x, std.y],
		"default_width": UiSettings.DEFAULT_HUD_WIDTH,
		"derived_5120": UiSettings.derive_ui_scale_for(5120, 1440, 96.0),
		"derived_1920": UiSettings.derive_ui_scale_for(1920, 1080, 96.0),
	}


func _build_page() -> void:
	var panel := Control.new()
	panel.size = Vector2(700, 600)
	root.add_child(panel)
	_label = RichTextLabel.new()
	_label.bbcode_enabled = true
	_label.fit_content = true
	_label.size = Vector2(660, 560)
	panel.add_child(_label)
	Utils.card_page(_label)
	var portrait := "[img width=40 height=50]res://assets/portraits/Ney.jpg[/img]"
	_page = "Head line\n"
	_page += Utils.card_open() + Utils.bb_portrait_row(portrait, "Ney\nInfantry · France\nStrength 24,000") + "\n"
	_page += "  after the row" + Utils.CARD_CLOSE + "\n"
	_page += Utils.bb_table(["Marshal", "Strength"], [["Ney", "24,000"], ["Davout", "30,000"]], [1]) + "\n"
	_page += "Tail line"
	_label.text = _page


func _tick() -> void:
	_frames += 1
	if _frames < 4:
		return
	var flat := Utils.flatten_tables(_page)
	_out["tables"] = {
		"paragraphs": _label.get_paragraph_count(),
		"raw_newlines": _page.count("\n"),
		"flat_newlines": flat.count("\n"),
		"parsed_has_words": _label.get_parsed_text().contains("Strength 24,000") and _label.get_parsed_text().contains("Davout"),
	}
	var f := FileAccess.open(OS.get_environment("UI_GILT2_OUT"), FileAccess.WRITE)
	f.store_string(JSON.stringify(_out))
	f.close()
	quit()

extends SceneTree
# =============================================================================
# Session UI-3 (November 12, 2026) — the folds, the hover and the fitted
# windows, DRIVEN (headless). Read by tests/test_ui_gilt3_folds_and_fill.py.
# Runs the real scripts under Godot 4.4.1 headless and writes ONE JSON object
# to $UI_GILT3_OUT:
#
#   hints  — Utils.bb_hint answers RichTextLabel.get_tooltip() over its words,
#            over the ⓘ a lead-in stands behind (a link round a hinted image)
#            and over a chip's words (a hint inside a link inside a one-cell
#            table); the tip is cleaned (brackets, quotes, newlines);
#   modes  — every helper's page branch returns the caller's old string byte
#            for byte; the folded branch carries the words in its hint or its
#            note, and an opened note shows the whole passage;
#   share  — Utils.clamp_centered_panel honours `clamp_reading_share` (the
#            share of the view, capped; the authored rect the floor; a grip's
#            size never raised).
# =============================================================================

var _out := {}
var _frames := 0
var _labels := {}


func _init() -> void:
	UiSettings._cfg = ConfigFile.new()
	var settings_class: Variant = UiSettings
	settings_class.set("_persist", false)
	_probe_modes()
	_build_hint_labels()
	_probe_share()
	_probe_map()
	process_frame.connect(_tick)


func _probe_map() -> void:
	# The very wide room's cover zoom and the whole-sheet view's gathering,
	# through the scripts' own pure functions.
	var renderer = load("res://scenes/map_renderer_base.gd")
	var layer = load("res://scenes/map_label_layer.gd")
	var sheet := Vector2(2560, 1600)
	var r := func(x: float, y: float, w: float, h: float) -> Rect2:
		return Rect2(x, y, w, h)
	var entries := [
		{"rect": r.call(0, 0, 60, 16), "nation": "France", "rank": 1000000000, "count": 1},   # 0 the Emperor
		{"rect": r.call(40, 0, 60, 16), "nation": "France", "rank": 50, "count": 1},          # 1 touches 0
		{"rect": r.call(300, 0, 60, 16), "nation": "France", "rank": 10, "count": 1},         # 2 alone
		{"rect": r.call(20, 4, 60, 16), "nation": "Austria", "rank": 80, "count": 1},         # 3 another nation
		{"rect": r.call(61, 10, 60, 16), "nation": "France", "rank": 5, "count": 4},          # 4 a stack, 1 px off 0
	]
	_out["map"] = {
		"fill_5120": renderer.fill_zoom_for(Vector2(5120, 1440), sheet),
		"fill_7680": renderer.fill_zoom_for(Vector2(7680, 2160), sheet),
		"fill_1920": renderer.fill_zoom_for(Vector2(1920, 1080), sheet),
		"wide_5120": renderer.is_wide_room(Vector2(5120, 1440)),
		"wide_3840x1200": renderer.is_wide_room(Vector2(3840, 1200)),
		"wide_3440": renderer.is_wide_room(Vector2(3440, 1440)),
		"wide_1920": renderer.is_wide_room(Vector2(1920, 1080)),
		"groups": layer.gather_groups(entries, 2.0),
		"format": layer.GATHER_FORMAT % ["Napoleon", 6],
	}


func _probe_modes() -> void:
	var lead := "[color=#a0a0a8]Every court of Europe — its temper toward France.[/color]\n\n"
	var res := {}
	UiSettings.set_explanations("page")
	res["page"] = {
		"folded": Utils.explanations_folded(),
		"lead_mark": Utils.lead_mark(lead, "probe.lead"),
		"lead": Utils.bb_lead(lead, "probe.lead"),
		"note": Utils.bb_note("probe.note", "First sentence.", " The rest of it.", "\n"),
		"link": Utils.note_link("probe.note"),
		"show": Utils.show_note("probe.note"),
	}
	UiSettings.set_explanations("folded")
	Utils.reset_notes()
	res["folded"] = {
		"folded": Utils.explanations_folded(),
		"lead_mark": Utils.lead_mark(lead, "probe.lead"),
		"lead": Utils.bb_lead(lead, "probe.lead"),
		"note": Utils.bb_note("probe.note", "First sentence.", " The rest of it.", "\n"),
		"show": Utils.show_note("probe.note"),
	}
	var opened := Utils.toggle_note("note:probe.note")
	res["opened"] = {
		"state": opened,
		"note": Utils.bb_note("probe.note", "First sentence.", " The rest of it.", "\n"),
		"show": Utils.show_note("probe.note"),
		"lead_open_after_toggle": Utils.toggle_note("probe.lead") and Utils.bb_lead(lead, "probe.lead") == lead,
	}
	Utils.reset_notes()
	res["clean"] = Utils.clean_tip("Loosen [b]Rein[/b] — \"loyalty\" stays [100]\nline two [img]res://x.png[/img]")
	res["hints"] = Utils.bb_hints("a [hint=one]x[/hint] b [hint=two words]y[/hint]")
	res["default"] = UiSettings.DEFAULT_EXPLANATIONS
	res["wide_default"] = UiSettings.DEFAULT_WIDE_MAP
	# the interim reading's fixes, through their pure functions: the one
	# sentence finder, and a card's pad reaching only into a blank paragraph
	var rec := "Sire, the field reads +0 and no road carries. Propose Peace comes nearest at -1 of 50."
	res["sentence"] = [Utils.first_sentence_end(rec), Utils.first_sentence_end("One sentence only."),
		Utils.first_sentence_end("St. Petersburg holds. Then more."),
		Utils.first_sentence_end("Sire, the words [hint=a. b]x[/hint] stand. More.")]
	var underlay = load("res://scripts/card_underlay.gd")
	var paras := PackedStringArray(["THE EMPEROR'S DESIGNS", "",
		"[bgcolor=#00000000][/bgcolor]  ", "  Road II — The Crowns of Italy", "[img width=8 height=8]res://x.png[/img]",
		"[lb]"])
	res["blank"] = [underlay.blank_paragraph(paras, -1), underlay.blank_paragraph(paras, 0),
		underlay.blank_paragraph(paras, 1), underlay.blank_paragraph(paras, 2), underlay.blank_paragraph(paras, 3),
		underlay.blank_paragraph(paras, 4), underlay.blank_paragraph(paras, 5), underlay.blank_paragraph(paras, 6)]
	_out["modes"] = res


func _build_hint_labels() -> void:
	var host := Control.new()
	host.size = Vector2(900, 400)
	root.add_child(host)
	UiSettings.set_explanations("folded")
	var cases := {
		"word": "Before " + Utils.bb_hint("[color=#d9c08c]HINTED[/color]", "the plain tip") + " after",
		"lead": "HEADING" + Utils.lead_mark("[color=#a0a0a8]The lead-in's \"own\" words [100].[/color]\n", "probe.lead2"),
		"chip": "Acts: " + Utils.bb_button_chip("vassal:loosen:Holland", "Loosen Rein", "d9c08c", "233043", "",
				"loyalty stays 100; tribute 75% to 50%"),
		"chip_off": "Acts: " + Utils.bb_chip_disabled("Invest", "", "unavailable: Loyalty is already full"),
	}
	var y := 0.0
	for key in cases:
		var label := RichTextLabel.new()
		label.bbcode_enabled = true
		label.fit_content = true
		label.position = Vector2(0, y)
		label.size = Vector2(880, 60)
		label.text = cases[key]
		host.add_child(label)
		_labels[key] = label
		y += 80.0


func _probe_share() -> void:
	# A headless root is 64 x 64: the panel stands in a 1600 x 900 SubViewport,
	# which is the viewport `clamp_centered_panel` measures.
	var vp := SubViewport.new()
	vp.size = Vector2i(1600, 900)
	root.add_child(vp)
	var host := Control.new()
	host.size = Vector2(1600, 900)
	vp.add_child(host)
	var panel := PanelContainer.new()
	panel.anchor_left = 0.5
	panel.anchor_right = 0.5
	panel.anchor_top = 0.5
	panel.anchor_bottom = 0.5
	panel.offset_left = -350.0
	panel.offset_right = 350.0
	panel.offset_top = -250.0
	panel.offset_bottom = 250.0
	host.add_child(panel)
	_labels["__share_panel"] = panel


func _scan(label: RichTextLabel) -> Array:
	var tips := {}
	var x := 1.0
	while x < label.size.x:
		var yy := 1.0
		while yy < maxf(label.size.y, 24.0):
			var t := label.get_tooltip(Vector2(x, yy))
			if t != "":
				tips[t] = true
			yy += 3.0
		x += 3.0
	return tips.keys()


func _tick() -> void:
	_frames += 1
	if _frames < 5:
		return
	var hints := {}
	for key in ["word", "lead", "chip", "chip_off"]:
		var label: RichTextLabel = _labels[key]
		hints[key] = {"tips": _scan(label), "parsed": label.get_parsed_text(), "text": label.text}
	_out["hints"] = hints
	var panel: Control = _labels["__share_panel"]
	var view := Vector2(panel.get_viewport().get_visible_rect().size)
	var res := {"view": [view.x, view.y]}
	Utils.clamp_centered_panel(panel)
	res["authored"] = [panel.offset_right - panel.offset_left, panel.offset_bottom - panel.offset_top]
	Utils.set_reading_share(panel, Vector2(0.55, 0.85), Vector2(900.0, 1000.0))
	Utils.clamp_centered_panel(panel)
	res["shared"] = [panel.offset_right - panel.offset_left, panel.offset_bottom - panel.offset_top]
	panel.set_meta("clamp_user_size", Vector2(600, 400))
	Utils.clamp_centered_panel(panel)
	res["gripped"] = [panel.offset_right - panel.offset_left, panel.offset_bottom - panel.offset_top]
	_out["share"] = res
	var f := FileAccess.open(OS.get_environment("UI_GILT3_OUT"), FileAccess.WRITE)
	f.store_string(JSON.stringify(_out))
	f.close()
	quit()

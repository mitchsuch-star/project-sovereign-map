extends SceneTree
# =============================================================================
# Session UI (November 11, 2026) — the chrome kit, DRIVEN (headless).
# =============================================================================
# Read by tests/test_ui_gilt_frame.py. Runs the real scripts under Godot 4.4.1
# headless and writes ONE JSON object to $UI_GILT_OUT:
#
#   frame   — scripts/gilt_frame.gd: StyleBoxFlat's property names survive a
#             duplicate (the tone a popup sets at run time), its thickness per
#             weight, that it is NOT a StyleBoxFlat (so a consumer must ask by
#             property), and that a framed scene loads with its own values;
#   theme   — the project theme carries the kit: the rule (zero minimum, so no
#             separator moves), the primary steps, the title face;
#   cards   — scripts/card_underlay.gd: the marks add NOTHING to a page's
#             parsed text, the page describes its own cards, a real page keeps
#             one paragraph per newline (the fail-safe's precondition), and the
#             underlay is a mouse-ignored child that changes no line height;
#   figures — Utils.bb_tabulate: the column is invisible spacers, the page's
#             parsed text is character-identical, a link line is left alone.
#
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs>/tools/ui_gilt_probe.gd
# =============================================================================

const FRAME_PATH := "res://scripts/gilt_frame.gd"
var _out := {}
var _frames := 0
var _labels := {}


func _init() -> void:
	UiSettings._cfg = ConfigFile.new()
	UiSettings._persist = false   # Session UI-5: the harness flag — writes stay in memory, and the scripted day keeps its one End Turn
	_probe_frame()
	_probe_theme()
	_build_pages()
	process_frame.connect(_tick)


func _probe_frame() -> void:
	var frame: StyleBox = load(FRAME_PATH).new()
	frame.set("bg_color", Color(0.1, 0.2, 0.3, 1.0))
	frame.set("border_color", Color(0.8, 0.4, 0.4, 1.0))
	frame.set("weight", 1)
	frame.set_content_margin_all(20.0)
	var copy: StyleBox = frame.duplicate()
	var thickness := []
	for w in [0, 1, 2]:
		frame.set("weight", w)
		thickness.append(frame.call("thickness"))
	frame.set("weight", 1)
	var scenes := {}
	for scene_name in ["objection_dialog", "strategic_ledger", "war_status_panel", "notification_bar", "main"]:
		var packed: PackedScene = load("res://scenes/%s.tscn" % scene_name)
		var node: Node = packed.instantiate()
		var panel: Control = null
		for path in ["PanelContainer", "RailPanel", "BottomLeftUI"]:
			if node.has_node(path):
				panel = node.get_node(path)
				break
		var box: StyleBox = panel.get_theme_stylebox("panel") if panel != null else null
		scenes[scene_name] = {
			"script": str(box.get_script().resource_path) if box != null and box.get_script() != null else "",
			"has_bg": box != null and "bg_color" in box,
			"has_border": box != null and "border_color" in box,
			"margin_left": box.get_margin(SIDE_LEFT) if box != null else -1.0,
			"weight": box.get("weight") if box != null else -1,
		}
		node.free()
	_out["frame"] = {
		"is_flat": frame is StyleBoxFlat,
		"has_border_color": "border_color" in frame,
		"copy_border": (copy.get("border_color") as Color).to_html(true),
		"copy_bg": (copy.get("bg_color") as Color).to_html(true),
		"copy_weight": copy.get("weight"),
		"copy_margin": copy.get_margin(SIDE_LEFT),
		"thickness": thickness,
		"minimum": [frame.get_minimum_size().x, frame.get_minimum_size().y],
		"scenes": scenes,
	}


func _probe_theme() -> void:
	var theme: Theme = ThemeDB.get_project_theme()
	var rule: StyleBox = theme.get_stylebox("separator", "HSeparator")
	var title: Font = theme.get_font("font", "ScreenTitle")
	var title_base := ""
	if title is FontVariation and (title as FontVariation).base_font != null:
		title_base = (title as FontVariation).base_font.resource_path
	var margins := {}
	for state in ["normal", "hover", "pressed", "disabled"]:
		var b: StyleBox = theme.get_stylebox(state, "Button")
		margins[state] = [b.get_margin(SIDE_LEFT), b.get_margin(SIDE_TOP),
				b.get_margin(SIDE_RIGHT), b.get_margin(SIDE_BOTTOM)]
	_out["theme"] = {
		"rule_script": str(rule.get_script().resource_path) if rule.get_script() != null else "",
		"rule_minimum": [rule.get_minimum_size().x, rule.get_minimum_size().y],
		"primary_size": theme.get_font_size("font_size", "PrimaryButton"),
		"primary_caption_size": theme.get_font_size("font_size", "PrimaryCaptionButton"),
		"primary_variation_of": str(theme.get_type_variation_base("PrimaryCaptionButton")),
		"title_base": title_base,
		"button_margins": margins,
	}


func _page() -> String:
	var open := Utils.card_open()
	var tone := Utils.card_open(Utils.COLOR_ERROR)
	var close := Utils.CARD_CLOSE
	return ("[color=#B8860B]═══ FORCES ═══[/color]\n[color=#a0a0a8]The muster of your corps.[/color]\n\n"
		+ open + "[color=#d9c08c]Ney[/color]  [color=#a0a0a8]Infantry[/color]\n"
		+ "  Status: [color=#a0a0a8]Idle[/color]  Location: Rhineland\n"
		+ "  Strength: 24,000  " + Utils.bb_button_chip("do:drill", "Drill now", "d9c08c", "22283a") + "\n"
		+ close + "\n"
		+ tone + "[color=#d06e6e]A PRISONER — Davout[/color]\n"
		+ "[img width=80 height=100]res://assets/portraits/Davout.jpg[/img]\n"
		+ Utils.bb_flag("France", 14) + "[b]France[/b] — [url=x]the court[/url]\n"
		+ close + "\n"
		+ "The end.")


const ECONOMY := ("  Treasury: 800g\n  Income:   +2590g\n  Trade:    +350g\n"
	+ "  [color=#e0c060]Blockade: -175g  (trade halved under enemy sail)[/color]\n"
	+ "  Upkeep:   -1512g\n    [color=#a0a0a8](paid for the men under arms)[/color]\n"
	+ "  Net:      [color=#8fbc8f]+1032g[/color]\n\n"
	+ "  Berry (major city): 150g\n  Artois (city): 110g\n  [url=x]Linked: 5g[/url]\n")


func _label(text: String) -> RichTextLabel:
	var label := RichTextLabel.new()
	label.bbcode_enabled = true
	label.fit_content = true
	label.size = Vector2(520, 10)
	label.custom_minimum_size = Vector2(520, 0)
	label.text = text
	root.add_child(label)
	return label


func _build_pages() -> void:
	var page := _page()
	var bare := page.replace(Utils.CARD_CLOSE, "")
	for tone_hex in [Utils.COLOR_GOLD, Utils.COLOR_ERROR]:
		bare = bare.replace(Utils.card_open(tone_hex), "")
	_labels["marked"] = _label(page)
	_labels["bare"] = _label(bare)
	var dressed := _label(page)
	Utils.card_page(dressed)
	_labels["dressed"] = dressed
	_labels["economy"] = _label(ECONOMY)
	_out["cards_in"] = []
	for card in load("res://scripts/card_underlay.gd").cards_in(page):
		_out["cards_in"].append([card[0], card[1], (card[2] as Color).to_html(false)])
	_out["page_newlines"] = page.count("\n")


func _tick() -> void:
	_frames += 1
	if _frames == 4:
		var econ: RichTextLabel = _labels["economy"]
		var before := econ.get_parsed_text()
		var tabulated := Utils.bb_tabulate(ECONOMY, econ)
		econ.text = tabulated
		_out["figures"] = {
			"parsed_before": before,
			"spacers": tabulated.count("[img color=#00000000"),
			"features": tabulated.count("[opentype_features=tnum,lnum]"),
			"link_line_untouched": tabulated.contains("  [url=x]Linked: 5g[/url]\n"),
			"single_line_runs_untouched": not Utils.bb_tabulate("  Alone: 5g\n", econ).contains("[img"),
		}
	if _frames == 8:
		var marked: RichTextLabel = _labels["marked"]
		var dressed: RichTextLabel = _labels["dressed"]
		var layer: Control = dressed.get_node_or_null("CardUnderlay")
		var box: StyleBox = dressed.get_theme_stylebox("normal")
		_out["cards"] = {
			"parsed_marked": marked.get_parsed_text(),
			"parsed_bare": (_labels["bare"] as RichTextLabel).get_parsed_text(),
			"parsed_dressed": dressed.get_parsed_text(),
			"paragraphs": marked.get_paragraph_count(),
			"underlay": layer != null,
			"underlay_ignores_mouse": layer != null and layer.mouse_filter == Control.MOUSE_FILTER_IGNORE,
			"underlay_behind": layer != null and layer.show_behind_parent,
			"underlay_minimum": [layer.get_combined_minimum_size().x, layer.get_combined_minimum_size().y] if layer != null else [-1, -1],
			"side_margins": [box.get_margin(SIDE_LEFT), box.get_margin(SIDE_RIGHT)],
			"vertical_margins": [box.get_margin(SIDE_TOP), box.get_margin(SIDE_BOTTOM)],
			"attach_is_idempotent": Utils.CARD_UNDERLAY.attach(dressed) == layer,
		}
		_out["figures"]["parsed_after"] = (_labels["economy"] as RichTextLabel).get_parsed_text()
		var path := OS.get_environment("UI_GILT_OUT")
		var f := FileAccess.open(path, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_out, " "))
			f.close()
		quit()
	if _frames > 600:
		quit(1)

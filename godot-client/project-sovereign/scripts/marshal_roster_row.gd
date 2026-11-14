extends Button
class_name MarshalRosterRow

# =============================================================================
# INK & IRON - One row of the Generals roster (Session UI-6, November 13, 2026)
# =============================================================================
# A real Button, one per marshal, in the roster column of the Generals screen
# (scripts/marshal_management.gd). Wide: a position number, a portrait, the
# name in the title face, a dim "location · strength" line, a status badge in
# the tone `MarshalState.status_of` names. Narrow (the Side Desk, a small
# window): the portrait alone, the name and the status its tooltip.
#
# The portrait ring takes the status tone; a gilt dot at the row's top right
# marks what asks for the Emperor (a prisoner, a petition, a grievance). The
# row judges nothing: the screen hands it the card, the view and the status.
# Pressing it emits `chosen(marshal_name)`; the screen owns the selection.
# =============================================================================

signal chosen(marshal_name: String)

const MarshalKit := preload("res://scripts/marshal_state.gd")

const PORTRAIT_W := 36
const PORTRAIT_H := 44
const ROW_H := 68
const ROW_H_NARROW := 64
const NARROW_W := 56
const DOT := 8

var marshal_name := ""


func setup(card: Dictionary, status: Dictionary, slot_index: int, narrow: bool,
		selected: bool, urgent: bool) -> void:
	marshal_name = str(card.get("name", ""))
	var shown: String = Utils.display_marshal_name(marshal_name)
	var tone := Color.html("#" + str(status.get("tone", Utils.COLOR_GOLD)))
	toggle_mode = true
	set_pressed_no_signal(selected)
	focus_mode = Control.FOCUS_ALL
	text = ""
	clip_contents = true
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	custom_minimum_size = Vector2(NARROW_W, ROW_H_NARROW) if narrow else Vector2(0, ROW_H)
	if narrow:
		tooltip_text = shown + " — " + str(status.get("detail", ""))
	else:
		tooltip_text = str(status.get("detail", ""))
	_apply_styles()
	pressed.connect(_on_pressed)

	var box := HBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# A Button lays out no children: the box spans it by its anchors. The offsets
	# are set outright — a preset applied while the row is still 0 px wide (before
	# the roster's VBox sizes it) left the box at its minimum, so the name, the
	# place and the badge were squeezed out of sight (the lead's W1 shoot).
	box.set_anchors_preset(Control.PRESET_FULL_RECT)
	box.offset_left = 6.0
	box.offset_top = 6.0
	box.offset_right = -6.0
	box.offset_bottom = -6.0
	box.add_theme_constant_override("separation", 8)
	if narrow:
		box.alignment = BoxContainer.ALIGNMENT_CENTER
	add_child(box)

	if not narrow and slot_index < 9:
		var num := Label.new()
		num.theme_type_variation = &"Caption"
		num.text = str(slot_index + 1)
		num.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
		num.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		num.mouse_filter = Control.MOUSE_FILTER_IGNORE
		box.add_child(num)

	box.add_child(_portrait(marshal_name, tone))

	if not narrow:
		var col := VBoxContainer.new()
		col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		col.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		col.add_theme_constant_override("separation", 0)
		col.mouse_filter = Control.MOUSE_FILTER_IGNORE
		box.add_child(col)

		var name_label := Label.new()
		# The title face at the theme's HudTitle step (no raw size — the
		# override-diet ratchet and the one-off size census). The lead's frame
		# reading: ScreenTitle cut "BERNADO..." and pushed the badge out of the row.
		name_label.theme_type_variation = &"HudTitle"
		name_label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
		name_label.text = shown
		name_label.clip_text = true
		name_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		col.add_child(name_label)

		var sub := Label.new()
		sub.theme_type_variation = &"Caption"
		sub.text = _sub_line(card)
		sub.clip_text = true
		sub.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		sub.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
		sub.mouse_filter = Control.MOUSE_FILTER_IGNORE
		# the place and strength, then the status badge, on ONE line (the lead's
		# frame reading: a third line overran the row and the badge was clipped)
		var line2 := HBoxContainer.new()
		line2.add_theme_constant_override("separation", 6)
		line2.mouse_filter = Control.MOUSE_FILTER_IGNORE
		sub.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		line2.add_child(sub)
		line2.add_child(_badge(status, tone))
		col.add_child(line2)

	if urgent:
		add_child(_dot())


func _on_pressed() -> void:
	chosen.emit(marshal_name)


func _sub_line(card: Dictionary) -> String:
	var where: String = Utils.humanize_entity_name(str(card.get("location", "")))
	# the interim readers (November 13): "Rhineland · 24,…" — the badge beside
	# the line left the figure no room; the roster states it in thousands (the
	# detail's strip carries the exact figure)
	var strength: int = int(card.get("strength", 0))
	var men: String = (str(int(round(float(strength) / 1000.0))) + "k") if strength >= 1000 else str(strength)
	if where == "":
		return men
	return where + " · " + men


func _portrait(key: String, tone: Color) -> Control:
	"""The likeness (or a monogram) in a ring of the status tone."""
	var ring := PanelContainer.new()
	ring.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ring.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0, 0, 0, 0.35)
	sb.border_color = Color(tone, 0.85)
	sb.set_border_width_all(2)
	sb.set_corner_radius_all(2)
	sb.set_content_margin_all(2)
	ring.add_theme_stylebox_override("panel", sb)
	var holder := Control.new()
	holder.custom_minimum_size = Vector2(PORTRAIT_W, PORTRAIT_H)
	holder.clip_contents = true
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ring.add_child(holder)
	var path: String = MarshalKit.portrait_path(key)
	if path != "":
		var pic := TextureRect.new()
		pic.texture = load(path)
		pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		pic.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.add_child(pic)
	else:
		var mono := Label.new()
		mono.theme_type_variation = &"StatFigure"
		mono.text = MarshalKit.monogram(key)
		mono.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		mono.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		mono.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		mono.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.add_child(mono)
	return ring


func _badge(status: Dictionary, tone: Color) -> Control:
	"""The status badge: its label (and glyph) on a wash of the status tone."""
	var panel := PanelContainer.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(tone, 0.34)
	sb.set_corner_radius_all(3)
	sb.content_margin_left = 6
	sb.content_margin_right = 6
	sb.content_margin_top = 1
	sb.content_margin_bottom = 1
	panel.add_theme_stylebox_override("panel", sb)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 4)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_child(row)
	var glyph_name := str(status.get("glyph", ""))
	if glyph_name != "":
		var g := TextureRect.new()
		g.texture = load(Utils.glyph(glyph_name))
		g.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		g.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		g.custom_minimum_size = Vector2(12, 12)
		g.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		g.modulate = tone
		g.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(g)
	var label := Label.new()
	label.theme_type_variation = &"Caption"
	label.text = str(status.get("label", ""))
	label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(label)
	return panel


func _dot() -> Control:
	"""The gilt dot at the row's top right: something asks for the Emperor."""
	var dot := Panel.new()
	dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sb := StyleBoxFlat.new()
	sb.bg_color = Utils.UI_GOLD_BRIGHT
	sb.set_corner_radius_all(DOT)
	dot.add_theme_stylebox_override("panel", sb)
	dot.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	dot.offset_left = -(DOT + 6)
	dot.offset_right = -6
	dot.offset_top = 6
	dot.offset_bottom = 6 + DOT
	return dot


func _apply_styles() -> void:
	var normal := _box(Color(0, 0, 0, 0.22), Color(Utils.UI_GOLD, 0.18), 1)
	var hover := _box(Utils.UI_PANEL_BG, Color(Utils.UI_GOLD, 0.5), 1)
	var held := _box(Utils.UI_ACTIVE_TAB_BG, Utils.UI_GOLD, 2)
	var focus := _box(Color(0, 0, 0, 0), Utils.UI_GOLD_BRIGHT, 2)
	add_theme_stylebox_override("normal", normal)
	add_theme_stylebox_override("hover", hover)
	add_theme_stylebox_override("pressed", held)
	add_theme_stylebox_override("hover_pressed", held)
	add_theme_stylebox_override("focus", focus)
	add_theme_stylebox_override("disabled", normal)


func _box(fill: Color, rim: Color, width: int) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.border_color = rim
	sb.set_border_width_all(width)
	sb.set_corner_radius_all(3)
	return sb

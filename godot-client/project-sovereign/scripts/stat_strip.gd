extends HBoxContainer

# =============================================================================
# INK & IRON — The Stat Strip (Session UI-2, November 11, 2026)
# =============================================================================
# A row of figure tiles a book stands above its page: a glyph, the figure in
# the title face (theme step `StatFigure`), and a caption under it — the
# Economy's Treasury / Net / Ceiling, the Forces' Authority, the Manpower's
# pools, the Balance of Europe's threat. The blind readers' first complaint
# was "walls of small text, no hierarchy among the figures"; the research's
# first take, "figures before prose". Real controls (not BBCode), so the big
# figures sit on the type ladder (no inline size) and the page's words below
# stay exactly the page's.
#
# set_tiles([{glyph, figure, caption, tone?, tip?, meter?, meter_max?}, …]);
# an empty list hides the strip.
# =============================================================================

const TILE_MIN_W := 120.0
const GLYPH_PX := 24


func _ready() -> void:
	name = "StatStrip"
	add_theme_constant_override("separation", 8)
	visible = false


func set_tiles(tiles: Array) -> void:
	for c in get_children():
		c.queue_free()
	visible = not tiles.is_empty()
	for t in tiles:
		if t is Dictionary:
			add_child(_tile(t))


func _tile(t: Dictionary) -> PanelContainer:
	var panel := PanelContainer.new()
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.custom_minimum_size = Vector2(TILE_MIN_W, 0)
	var well := StyleBoxFlat.new()
	well.bg_color = Color(0, 0, 0, 0.24)
	well.border_color = Color(Utils.UI_GOLD, 0.28)
	well.set_border_width_all(1)
	well.set_corner_radius_all(2)
	well.content_margin_left = 10
	well.content_margin_right = 10
	well.content_margin_top = 6
	well.content_margin_bottom = 6
	panel.add_theme_stylebox_override("panel", well)
	panel.tooltip_text = str(t.get("tip", ""))
	panel.mouse_filter = Control.MOUSE_FILTER_PASS if panel.tooltip_text != "" else Control.MOUSE_FILTER_IGNORE
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_child(row)
	var glyph_name := str(t.get("glyph", ""))
	if glyph_name != "":
		var g := TextureRect.new()
		g.texture = load(Utils.glyph(glyph_name))
		g.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		g.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		g.custom_minimum_size = Vector2(GLYPH_PX, GLYPH_PX)
		g.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		g.modulate = Color(Utils.UI_GOLD, 0.95)
		g.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(g)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 0)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(col)
	var fig := Label.new()
	fig.theme_type_variation = &"StatFigure"
	fig.text = str(t.get("figure", ""))
	var tone = t.get("tone", null)
	if tone is Color:
		fig.add_theme_color_override("font_color", tone)
	fig.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_child(fig)
	var cap := Label.new()
	cap.theme_type_variation = &"Caption"
	cap.text = str(t.get("caption", ""))
	cap.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
	cap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_child(cap)
	if t.has("meter"):
		var bar := _meter(float(t.get("meter", 0.0)), float(t.get("meter_max", 100.0)),
			t.get("marks", []), tone if tone is Color else Utils.UI_GOLD)
		col.add_child(bar)
	return panel


func _meter(value: float, maximum: float, marks: Array, tone: Color) -> Control:
	var m := Control.new()
	m.custom_minimum_size = Vector2(80, 6)
	m.mouse_filter = Control.MOUSE_FILTER_IGNORE
	m.draw.connect(func():
		var w := m.size.x
		var h := m.size.y
		m.draw_rect(Rect2(0, 0, w, h), Color(0, 0, 0, 0.45))
		m.draw_rect(Rect2(0, 0, w * clampf(value / maxf(maximum, 0.001), 0.0, 1.0), h), tone)
		for mark in marks:
			var x := w * clampf(float(mark) / maxf(maximum, 0.001), 0.0, 1.0)
			m.draw_rect(Rect2(x, -1, 1, h + 2), Color(Utils.UI_GOLD, 0.85))
		m.draw_rect(Rect2(0, 0, w, h), Color(Utils.UI_GOLD, 0.4), false, 1.0))
	return m

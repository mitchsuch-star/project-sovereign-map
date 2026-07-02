extends Control

# Map Slice 7.5 (DEF-11): zoom-LOD map labels — supersedes the Slice-7
# "no persistent labels" decision of record (user-blessed July 2, 2026).
#
# SCREEN-SPACE overlay (July 2 zoom-feedback fold): every _draw() re-projects
# the stored WORLD anchors through the map SubViewport's canvas transform.
# Two reasons this is not a world_layer child: (1) world-space text under
# camera zoom rasterized glyphs at tiny world font sizes and scaled them up
# blurry; (2) holding a constant screen size while the map grew read as
# "the names shrink when I zoom in". Here glyphs rasterize at the exact
# on-screen size (always crisp) and the size GROWS with zoom inside clamps.
#
# Two tiers, switched by camera zoom:
#   - nation labels (zoomed out): one name per nation at the radius-weighted
#     centroid of its owned provinces;
#   - province labels (zoomed in): the registry name at each province's
#     `label_anchor` (parsed since §4.1 but unread until this slice).
#
# Everything draws in ONE _draw() pass — no per-label nodes. Label data
# reflects region_controllers, i.e. exactly what the owner fill already
# tints — no fog information beyond the fill's is revealed.

const PROVINCE_LABEL_MIN_ZOOM: float = 1.1
# Screen font size = clampf(BASE * zoom, MIN, MAX) — labels grow as you zoom
# in (sub-map-rate via the caps) instead of visually shrinking against the
# growing map.
const NATION_FONT_BASE: float = 34.0
const NATION_FONT_MIN: float = 22.0
const NATION_FONT_MAX: float = 46.0
const PROVINCE_FONT_BASE: float = 13.0
const PROVINCE_FONT_MIN: float = 14.0
const PROVINCE_FONT_MAX: float = 34.0
const LABEL_TEXT_COLOR := Color(0.97, 0.94, 0.86, 0.95)
const LABEL_OUTLINE_COLOR := Color(0.09, 0.07, 0.05, 0.88)
const OFFSCREEN_CULL_MARGIN: float = 120.0

# The owning renderer (map_renderer_base.gd) — source of the SubViewport
# canvas transform used to project world anchors to screen.
var _renderer = null
# [{"text": String, "position": Vector2 (WORLD coords)}]
var _nation_labels: Array = []
var _province_labels: Array = []
var _zoom_level: float = 1.0


func setup(renderer) -> void:
	_renderer = renderer


func set_labels(nation_labels: Array, province_labels: Array) -> void:
	_nation_labels = nation_labels.duplicate(true)
	_province_labels = province_labels.duplicate(true)
	queue_redraw()


func set_zoom_level(zoom_level: float) -> void:
	if is_equal_approx(_zoom_level, zoom_level):
		return
	_zoom_level = zoom_level
	queue_redraw()


func clear_labels() -> void:
	_nation_labels.clear()
	_province_labels.clear()
	queue_redraw()


func _draw():
	var font: Font = ThemeDB.fallback_font
	if font == null or _renderer == null or _renderer.map_viewport == null:
		return
	var xform: Transform2D = _renderer.map_viewport.canvas_transform
	if _zoom_level >= PROVINCE_LABEL_MIN_ZOOM:
		_draw_label_tier(
			font, _province_labels, xform,
			clampf(PROVINCE_FONT_BASE * _zoom_level, PROVINCE_FONT_MIN, PROVINCE_FONT_MAX)
		)
	else:
		_draw_label_tier(
			font, _nation_labels, xform,
			clampf(NATION_FONT_BASE * _zoom_level, NATION_FONT_MIN, NATION_FONT_MAX)
		)


func _draw_label_tier(font: Font, labels: Array, xform: Transform2D, font_screen_px: float) -> void:
	var font_size: int = max(1, int(round(font_screen_px)))
	var outline_size: int = max(2, int(round(font_screen_px / 6.0)))
	var cull_rect := Rect2(Vector2.ZERO, size).grow(OFFSCREEN_CULL_MARGIN)
	for label in labels:
		var text: String = str(label.get("text", ""))
		if text == "":
			continue
		var center: Vector2 = xform * Vector2(label.get("position", Vector2.ZERO))
		if not cull_rect.has_point(center):
			continue
		var text_size: Vector2 = font.get_string_size(
			text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size
		)
		var draw_pos := center + Vector2(-text_size.x / 2.0, text_size.y / 4.0)
		draw_string_outline(
			font, draw_pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			font_size, outline_size, LABEL_OUTLINE_COLOR
		)
		draw_string(
			font, draw_pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			font_size, LABEL_TEXT_COLOR
		)

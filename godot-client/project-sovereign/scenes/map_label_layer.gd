extends Control

# Map Slice 7.5 (DEF-11): zoom-LOD map labels — supersedes the Slice-7
# "no persistent labels" decision of record (user-blessed July 2, 2026).
#
# Two tiers, switched by camera zoom:
#   - nation labels (zoomed out): one name per nation at the radius-weighted
#     centroid of its owned provinces, so the strategic view reads like a
#     political map without hovering;
#   - province labels (zoomed in): the registry name at each province's
#     `label_anchor` (parsed since §4.1 but unread until this slice).
#
# The layer lives in world space (a world_layer child), so positions ride the
# camera transform for free; font sizes counter-scale by 1/zoom to hold a
# constant on-screen size. Everything draws in ONE _draw() pass — no per-label
# nodes, mirroring map_tooltip_layer.gd's cheap draw_string pattern. Label
# data reflects region_controllers, i.e. exactly what the owner fill already
# tints — no fog information beyond the fill's is revealed.

const PROVINCE_LABEL_MIN_ZOOM: float = 1.1
const NATION_FONT_SCREEN_PX: float = 26.0
const PROVINCE_FONT_SCREEN_PX: float = 12.0
const LABEL_TEXT_COLOR := Color(0.97, 0.94, 0.86, 0.95)
const LABEL_OUTLINE_COLOR := Color(0.09, 0.07, 0.05, 0.88)
const LABEL_OUTLINE_SCREEN_PX: float = 4.0

# [{"text": String, "position": Vector2 (layer space)}]
var _nation_labels: Array = []
var _province_labels: Array = []
var _zoom_level: float = 1.0


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
	if font == null:
		return
	var zoom: float = maxf(_zoom_level, 0.001)
	if _zoom_level >= PROVINCE_LABEL_MIN_ZOOM:
		_draw_label_tier(font, _province_labels, PROVINCE_FONT_SCREEN_PX / zoom)
	else:
		_draw_label_tier(font, _nation_labels, NATION_FONT_SCREEN_PX / zoom)


func _draw_label_tier(font: Font, labels: Array, font_px: float) -> void:
	var font_size: int = max(1, int(round(font_px)))
	var outline_size: int = max(1, int(round(LABEL_OUTLINE_SCREEN_PX / maxf(_zoom_level, 0.001))))
	for label in labels:
		var text: String = str(label.get("text", ""))
		if text == "":
			continue
		var center: Vector2 = label.get("position", Vector2.ZERO)
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

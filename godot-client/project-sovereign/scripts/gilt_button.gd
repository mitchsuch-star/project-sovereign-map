@tool
extends StyleBox

# =============================================================================
# INK & IRON — The Gilt Button (Session UI-2, November 11, 2026)
# =============================================================================
# ONE drawn face for every button state the theme names. The readers of the
# November 11 baseline read the flat navy box as "a generic widget" and a
# DISABLED button as an enabled one; this face is a lit gradient (lighter at
# the head, darker at the foot), a 1 px gilt rim, a 1 px highlight under the
# head, a lift shadow — and per state: a warm gilt glow on hover, a sunk well
# when pressed, a flat desaturated face and a DASHED rim when disabled.
#
# It is geometry (like scripts/gilt_frame.gd), so it is crisp at every
# Interface Scale. THE CONTRACT (pinned by tests/test_ui_gilt2_imperial_desk.py):
#   * StyleBoxFlat's NAMES for the fill and the rim — `bg_color`, `border_color`
#     — and the inherited `content_margin_*`, so the theme's margins (12 / 6;
#     the pressed state's 7 / 5) stay where every button's size was measured,
#     and code that tints a button's box at run time keeps working. A consumer
#     asks `"border_color" in box`, never `box is StyleBoxFlat`.
#   * It draws INSIDE the content box's rect (the glow and the shadow outside
#     it, reported by `_get_draw_rect`): no button changes size.
#   * High contrast (UiSettings) drops the gradient for the flat `bg_color` and
#     draws the rim at full alpha.
#   * No `class_name`: the theme names it by path.
# =============================================================================

## The fill at the head (StyleBoxFlat's name: the colour a tint writes).
@export var bg_color := Color(0.13, 0.145, 0.225, 1.0):
	set(value):
		bg_color = value
		emit_changed()
## The fill at the foot (the gradient runs head → foot).
@export var bg_foot := Color(0.07, 0.08, 0.135, 1.0):
	set(value):
		bg_foot = value
		emit_changed()
## The rim (StyleBoxFlat's name).
@export var border_color := Color(0.85, 0.75, 0.55, 0.62):
	set(value):
		border_color = value
		emit_changed()
@export_range(1, 3) var rim_width := 1:
	set(value):
		rim_width = value
		emit_changed()
@export_range(0, 6) var corner := 2:
	set(value):
		corner = value
		emit_changed()
## The 1 px light under the head (alpha of white; 0 = none).
@export_range(0.0, 1.0) var highlight := 0.07:
	set(value):
		highlight = value
		emit_changed()
## The lift shadow under the button (alpha; 0 = none) and its size.
@export_range(0.0, 1.0) var shadow_alpha := 0.45:
	set(value):
		shadow_alpha = value
		emit_changed()
@export_range(0, 12) var shadow_size := 3:
	set(value):
		shadow_size = value
		emit_changed()
## A gilt glow round the button (hover): alpha of the rim's colour; 0 = none.
@export_range(0.0, 1.0) var glow := 0.0:
	set(value):
		glow = value
		emit_changed()
## A sunk well at the head (pressed): alpha of the inner shadow; 0 = none.
@export_range(0.0, 1.0) var inset := 0.0:
	set(value):
		inset = value
		emit_changed()
## A dashed rim (disabled): the face says it cannot act before the pointer asks.
@export var dashed := false:
	set(value):
		dashed = value
		emit_changed()

var _base := StyleBoxFlat.new()
var _rim := StyleBoxFlat.new()


func _high_contrast() -> bool:
	# The editor's @tool preview draws the authored face.
	if Engine.is_editor_hint():
		return false
	return UiSettings.get_high_contrast()


func _get_draw_rect(rect: Rect2) -> Rect2:
	var grow := maxf(float(shadow_size) + 1.0, 6.0 if glow > 0.0 else 0.0)
	return rect.grow(grow)


func _draw(to_canvas_item: RID, rect: Rect2) -> void:
	var hc := _high_contrast()
	var alpha := bg_color.a
	# 1 — the shadow (or the hover's glow) and the foot's fill, rounded.
	_base.bg_color = bg_color if hc else bg_foot
	_base.set_corner_radius_all(corner)
	_base.set_border_width_all(0)
	if glow > 0.0:
		_base.shadow_color = Color(border_color.r, border_color.g, border_color.b, glow * alpha)
		_base.shadow_size = 6
		_base.shadow_offset = Vector2.ZERO
	else:
		_base.shadow_color = Color(0, 0, 0, shadow_alpha * alpha)
		_base.shadow_size = shadow_size
		_base.shadow_offset = Vector2(0, 1)
	_base.draw(to_canvas_item, rect)
	var inner := rect.grow(-1.0)
	if inner.size.x <= 2.0 or inner.size.y <= 2.0:
		return
	# 2 — the gradient, head → foot (none under High contrast).
	if not hc:
		RenderingServer.canvas_item_add_polygon(to_canvas_item,
			PackedVector2Array([inner.position, Vector2(inner.end.x, inner.position.y),
				inner.end, Vector2(inner.position.x, inner.end.y)]),
			PackedColorArray([bg_color, bg_color, bg_foot, bg_foot]))
	# 3 — the light under the head, or the pressed well's shade.
	if highlight > 0.0 and inset <= 0.0:
		RenderingServer.canvas_item_add_rect(to_canvas_item,
			Rect2(inner.position + Vector2(1.0, 0.0), Vector2(inner.size.x - 2.0, 1.0)),
			Color(1, 1, 1, highlight * alpha))
	if inset > 0.0:
		var shade := Color(0, 0, 0, inset * alpha)
		var clear := Color(0, 0, 0, 0)
		var band := minf(4.0, inner.size.y * 0.5)
		RenderingServer.canvas_item_add_polygon(to_canvas_item,
			PackedVector2Array([inner.position, Vector2(inner.end.x, inner.position.y),
				Vector2(inner.end.x, inner.position.y + band), Vector2(inner.position.x, inner.position.y + band)]),
			PackedColorArray([shade, shade, clear, clear]))
	# 4 — the rim: solid, or dashed for a button that cannot act.
	var rim := Color(border_color.r, border_color.g, border_color.b, 1.0 if hc else border_color.a)
	if not dashed:
		_rim.draw_center = false
		_rim.border_color = rim
		_rim.set_border_width_all(rim_width)
		_rim.set_corner_radius_all(corner)
		_rim.draw(to_canvas_item, rect)
		return
	_dash(to_canvas_item, rect, rim)


func _dash(item: RID, rect: Rect2, colour: Color) -> void:
	"""A 4-on 3-off dashed rim, 1 px, inside the rect."""
	var a := rect.position + Vector2(0.5, 0.5)
	var b := rect.end - Vector2(0.5, 0.5)
	for edge in [[a, Vector2(b.x, a.y)], [Vector2(b.x, a.y), b], [b, Vector2(a.x, b.y)], [Vector2(a.x, b.y), a]]:
		var p0: Vector2 = edge[0]
		var p1: Vector2 = edge[1]
		var length := p0.distance_to(p1)
		if length <= 0.0:
			continue
		var dir := (p1 - p0) / length
		var t := 0.0
		while t < length:
			var seg_end := minf(t + 4.0, length)
			RenderingServer.canvas_item_add_line(item, p0 + dir * t, p0 + dir * seg_end, colour, 1.0)
			t += 7.0

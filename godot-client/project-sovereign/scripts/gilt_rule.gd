@tool
extends StyleBox

# =============================================================================
# INK & IRON — The Gilt Rule (Session UI, November 11, 2026)
# =============================================================================
# The game's one horizontal rule: a hairline that fades at both ends, a small
# lozenge at its centre. It is the theme's `HSeparator/styles/separator`, so
# every separator in every scene takes it with no scene edit.
#
# It changes NO layout: its minimum size is zero, so an HSeparator keeps the
# height its `separation` constant gives it (4 px), and the rule is drawn on
# the rect's centre line — the lozenge overdraws its rect by a pixel or two
# above and below, which nothing clips.
#
# Vector, like the frame (`gilt_frame.gd`): crisp at every Interface Scale.
# =============================================================================

@export var color := Color(0.85, 0.75, 0.55, 0.8):
	set(value):
		color = value
		emit_changed()
## The centre ornament. False gives the plain fading hairline.
@export var lozenge := true:
	set(value):
		lozenge = value
		emit_changed()
## The part of the rule's length, at each end, over which it fades to nothing.
@export_range(0.0, 0.5) var fade := 0.35:
	set(value):
		fade = value
		emit_changed()


func _get_minimum_size() -> Vector2:
	return Vector2.ZERO


func _draw(to_canvas_item: RID, rect: Rect2) -> void:
	if rect.size.x <= 2.0:
		return
	var y := floorf(rect.position.y + rect.size.y * 0.5)
	var x0 := rect.position.x
	var x1 := rect.end.x
	var cx := floorf((x0 + x1) * 0.5)
	var clear := Color(color.r, color.g, color.b, 0.0)
	var gap := 9.0 if lozenge else 0.0
	var run := maxf((x1 - x0) * 0.5 - gap, 0.0)
	var ramp := run * (fade * 2.0)
	# Each half: a faded ramp from the end, then the full-strength run to the
	# centre gap — two quads a side, the colour carried on the vertices.
	_span(to_canvas_item, x0, x0 + ramp, y, clear, color)
	_span(to_canvas_item, x0 + ramp, cx - gap, y, color, color)
	_span(to_canvas_item, cx + gap, x1 - ramp, y, color, color)
	_span(to_canvas_item, x1 - ramp, x1, y, color, clear)
	if lozenge:
		var s := 3.5
		var p := Vector2(cx, y + 0.5)
		RenderingServer.canvas_item_add_polygon(to_canvas_item,
			PackedVector2Array([p + Vector2(0, -s), p + Vector2(s, 0), p + Vector2(0, s), p + Vector2(-s, 0)]),
			PackedColorArray([color]))


func _span(ci: RID, from_x: float, to_x: float, y: float, from_c: Color, to_c: Color) -> void:
	if to_x - from_x <= 0.5:
		return
	RenderingServer.canvas_item_add_polygon(ci,
		PackedVector2Array([Vector2(from_x, y), Vector2(to_x, y), Vector2(to_x, y + 1.0), Vector2(from_x, y + 1.0)]),
		PackedColorArray([from_c, to_c, to_c, from_c]))

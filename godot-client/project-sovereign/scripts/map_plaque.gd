@tool
extends StyleBox

# =============================================================================
# INK & IRON — The Map's Plaques (Session UI-2, November 11, 2026)
# =============================================================================
# The markers that stand on the map — a province's garrison, a force the fog
# half-hides, a fleet's sail count, a marshal's name — were flat coloured
# rectangles and outlined words; the blind readers read them as crude and saw
# the names overprint. Each is now a plaque drawn in a palette that stands off
# the painted paper (the research's "icons pop out of the surrounding palette"):
#
#   GARRISON  a dark plate, the holder's colour as a left band, a gilt rim
#   FOG       a round token, a dashed rim in the holder's tint
#   SAIL      a navy roundel with a gilt rim
#   NAME      a dark nameplate with the nation's colour as its foot rule
#
# Geometry, crisp at every zoom; StyleBoxFlat's names for the fill and the rim
# (`bg_color`, `border_color`); no `class_name` — the renderer loads it by path.
# =============================================================================

enum Kind { GARRISON, FOG, SAIL, NAME }

@export_enum("garrison", "fog", "sail", "name") var kind: int = Kind.GARRISON:
	set(value):
		kind = value
		emit_changed()
@export var bg_color := Color(0.07, 0.08, 0.12, 0.92):
	set(value):
		bg_color = value
		emit_changed()
@export var border_color := Color(0.85, 0.75, 0.55, 0.85):
	set(value):
		border_color = value
		emit_changed()
## The holder's / the nation's colour: the garrison's band, the name's rule,
## the fog token's rim.
@export var band_color := Color(0.25, 0.41, 0.88, 1.0):
	set(value):
		band_color = value
		emit_changed()
## The band's width on a garrison plate (px, at the furniture's scale).
@export var band_width := 5.0:
	set(value):
		band_width = value
		emit_changed()

var _flat := StyleBoxFlat.new()


func _get_draw_rect(rect: Rect2) -> Rect2:
	return rect.grow(4.0)


func _draw(to_canvas_item: RID, rect: Rect2) -> void:
	match kind:
		Kind.GARRISON:
			_draw_garrison(to_canvas_item, rect)
		Kind.FOG:
			_draw_fog(to_canvas_item, rect)
		Kind.SAIL:
			_draw_sail(to_canvas_item, rect)
		_:
			_draw_name(to_canvas_item, rect)


func _draw_garrison(item: RID, rect: Rect2) -> void:
	_flat.bg_color = bg_color
	_flat.set_corner_radius_all(3)
	_flat.set_border_width_all(0)
	_flat.shadow_color = Color(0, 0, 0, 0.5 * bg_color.a)
	_flat.shadow_size = 3
	_flat.shadow_offset = Vector2(0, 1)
	_flat.draw(item, rect)
	# the holder's band, flush left, under the rim
	var band := Rect2(rect.position + Vector2(1, 1), Vector2(band_width, rect.size.y - 2))
	RenderingServer.canvas_item_add_rect(item, band, band_color)
	RenderingServer.canvas_item_add_rect(item,
		Rect2(Vector2(band.end.x, band.position.y), Vector2(1, band.size.y)),
		Color(border_color.r, border_color.g, border_color.b, border_color.a * 0.6))
	_flat.draw_center = false
	_flat.shadow_size = 0
	_flat.border_color = border_color
	_flat.set_border_width_all(1)
	_flat.draw(item, rect)
	_flat.draw_center = true


func _draw_fog(item: RID, rect: Rect2) -> void:
	var c := rect.get_center()
	var r := minf(rect.size.x, rect.size.y) * 0.5
	RenderingServer.canvas_item_add_circle(item, c + Vector2(0, 1), r + 1.0, Color(0, 0, 0, 0.35))
	RenderingServer.canvas_item_add_circle(item, c, r, bg_color)
	# a dashed rim: twelve arcs in the holder's tint — a force half-seen
	var segs := 12
	for i in range(segs):
		var a0 := TAU * float(i) / float(segs)
		var a1 := a0 + TAU / float(segs) * 0.55
		var pts := PackedVector2Array()
		for k in range(5):
			var a := lerpf(a0, a1, float(k) / 4.0)
			pts.append(c + Vector2(cos(a), sin(a)) * (r - 0.75))
		RenderingServer.canvas_item_add_polyline(item, pts, PackedColorArray([band_color]), 1.5, true)


func _draw_sail(item: RID, rect: Rect2) -> void:
	_flat.bg_color = bg_color
	var radius := int(minf(rect.size.y, rect.size.x) * 0.5)
	_flat.set_corner_radius_all(radius)
	_flat.border_color = border_color
	_flat.set_border_width_all(1)
	_flat.shadow_color = Color(0, 0, 0, 0.45 * bg_color.a)
	_flat.shadow_size = 2
	_flat.shadow_offset = Vector2(0, 1)
	_flat.draw(item, rect)


func _draw_name(item: RID, rect: Rect2) -> void:
	_flat.bg_color = bg_color
	_flat.set_corner_radius_all(2)
	_flat.set_border_width_all(0)
	_flat.shadow_color = Color(0, 0, 0, 0.35 * bg_color.a)
	_flat.shadow_size = 2
	_flat.shadow_offset = Vector2(0, 1)
	_flat.draw(item, rect)
	# the nation's colour as the plate's foot rule
	RenderingServer.canvas_item_add_rect(item,
		Rect2(Vector2(rect.position.x + 1, rect.end.y - 2), Vector2(rect.size.x - 2, 2)), band_color)

extends Control

# Row CC, CC-3 "Select, click, Enter" (Pre-Deploy S13c part 2, October 2026):
# the map's ORDER layer — what a selected corps would do, drawn over the map.
#
#   * the RING at the selected piece's feet;
#   * the GHOST ROAD — the quote's own road, from his feet through every
#     province of it to its end, a pip where he stands at each turn's end,
#     the head an arrow, and the badge ("3 turns · 2 AP") beside it.
#
# SCREEN space, like the label layer (`map_label_layer.gd`): WORLD anchors
# are re-projected through the map camera on every draw, so the line and the
# badge stay crisp and the same width at every zoom, and the layer redraws
# whenever the projection moves (a pan, a zoom, Home). It owns no rule — the
# road, the turns and the price are the backend's quote, handed in by the
# renderer (`map_renderer_base.gd`, `GET /march_reach`, `GET /march_quotes`).

const RING_COLOR := Color(1.0, 0.86, 0.42, 0.95)
const RING_SHADOW := Color(0.08, 0.06, 0.04, 0.75)
const GHOST_SHADOW := Color(0.08, 0.06, 0.04, 0.62)
const GHOST_COLORS := {
	"march": Color(1.0, 0.92, 0.66, 0.95),
	"march_attack": Color(0.98, 0.52, 0.36, 0.95),
	"attack": Color(0.98, 0.42, 0.32, 0.95),
	"support": Color(0.62, 0.86, 1.0, 0.95),
	"follow": Color(0.62, 0.86, 1.0, 0.95),
	"refused": Color(0.86, 0.36, 0.32, 0.9),
	"drag": Color(1.0, 0.92, 0.66, 0.75),
}
const GHOST_WIDTH := 3.5
const GHOST_DASH := 10.0
const BADGE_FONT_PX := 14
const BADGE_PAD := Vector2(7, 4)
const BADGE_BG := Color(0.09, 0.08, 0.07, 0.88)

# The owning renderer — source of the camera projection.
var _renderer = null
var _ring_world := Vector2.ZERO
var _ring_radius_world := 0.0
var _has_ring := false
# The ghost: WORLD points (his feet first), its kind, the badge, and which
# points are a turn's end (indexes into the points).
var _ghost_world: Array = []
var _ghost_kind := ""
var _ghost_label := ""
var _ghost_pips: Array = []
# A drag's free end, in this layer's LOCAL space (the cursor) — used when the
# cursor stands where no road is quoted.
var _ghost_cursor_local := Vector2.ZERO
var _ghost_to_cursor := false
var _drawn_xform := Transform2D()


func setup(renderer) -> void:
	_renderer = renderer


func set_ring(feet_world: Vector2, radius_world: float) -> void:
	_ring_world = feet_world
	_ring_radius_world = radius_world
	_has_ring = true
	queue_redraw()


func clear_ring() -> void:
	_has_ring = false
	queue_redraw()


func set_ghost(points_world: Array, kind: String, label: String, pips: Array = []) -> void:
	"""The road to draw: WORLD points from his feet to the road's end."""
	_ghost_world = points_world.duplicate()
	_ghost_kind = kind
	_ghost_label = label
	_ghost_pips = pips.duplicate()
	_ghost_to_cursor = false
	queue_redraw()


func set_ghost_to_cursor(from_world: Vector2, cursor_local: Vector2) -> void:
	"""A drag over ground no road is quoted to: a plain line to the cursor."""
	_ghost_world = [from_world]
	_ghost_kind = "drag"
	_ghost_label = ""
	_ghost_pips = []
	_ghost_cursor_local = cursor_local
	_ghost_to_cursor = true
	queue_redraw()


func clear_ghost() -> void:
	_ghost_world = []
	_ghost_kind = ""
	_ghost_label = ""
	_ghost_pips = []
	_ghost_to_cursor = false
	queue_redraw()


func screen_rect() -> Rect2:
	"""The ring and the ghost road's bounding box in this layer's LOCAL space
	(empty with neither) — the confirm card stands clear of it."""
	if _renderer == null or _renderer.map_viewport == null:
		return Rect2()
	var xform := _projection()
	var points: Array = []
	if _has_ring:
		points.append(xform * _ring_world)
	for p in _ghost_world:
		points.append(xform * (p as Vector2))
	if _ghost_to_cursor:
		points.append(_ghost_cursor_local)
	if points.is_empty():
		return Rect2()
	var box := Rect2(points[0], Vector2.ZERO)
	for p in points:
		box = box.expand(p)
	# The badge stands above the road's head, to either side.
	return box.grow_individual(140.0, 48.0, 140.0, 24.0)


func report() -> Dictionary:
	"""What the layer holds — read by the capture harness."""
	return {
		"ring": _has_ring,
		"ghost_points": _ghost_world.size() + (1 if _ghost_to_cursor else 0),
		"ghost_kind": _ghost_kind,
		"ghost_label": _ghost_label,
		"pips": _ghost_pips.size(),
	}


func _projection() -> Transform2D:
	# The label layer's projection: canvas_transform maps world -> PHYSICAL
	# viewport px (UI-2 Part 2), this layer draws in LOGICAL px.
	var xform: Transform2D = _renderer.map_viewport.canvas_transform
	var vp_scale: float = 1.0
	if _renderer.has_method("_viewport_pixel_scale"):
		vp_scale = _renderer._viewport_pixel_scale()
	if not is_equal_approx(vp_scale, 1.0):
		xform = xform.scaled(Vector2(1.0 / vp_scale, 1.0 / vp_scale))
	return xform


func _process(_delta: float) -> void:
	if _renderer == null or _renderer.map_viewport == null:
		return
	if not (_has_ring or not _ghost_world.is_empty()):
		return
	if _projection() != _drawn_xform:
		queue_redraw()


func _draw() -> void:
	if _renderer == null or _renderer.map_viewport == null:
		return
	var xform := _projection()
	_drawn_xform = xform
	var zoom: float = xform.get_scale().x
	if _has_ring:
		var c: Vector2 = xform * _ring_world
		var r: float = maxf(_ring_radius_world * zoom, 9.0)
		_draw_ellipse(c, r, r * 0.42, RING_SHADOW, 5.0)
		_draw_ellipse(c, r, r * 0.42, RING_COLOR, 2.5)
	if _ghost_world.is_empty():
		return
	var pts := PackedVector2Array()
	for p in _ghost_world:
		pts.append(xform * (p as Vector2))
	if _ghost_to_cursor:
		pts.append(_ghost_cursor_local)
	if pts.size() < 2:
		return
	var color: Color = GHOST_COLORS.get(_ghost_kind, GHOST_COLORS["march"])
	draw_polyline(pts, GHOST_SHADOW, GHOST_WIDTH + 3.0, true)
	for i in range(pts.size() - 1):
		draw_dashed_line(pts[i], pts[i + 1], color, GHOST_WIDTH, GHOST_DASH, true, true)
	for idx in _ghost_pips:
		var k := int(idx)
		if k > 0 and k < pts.size() - 1:
			draw_circle(pts[k], 5.0, GHOST_SHADOW)
			draw_circle(pts[k], 3.5, color)
	_draw_arrow_head(pts[pts.size() - 2], pts[pts.size() - 1], color)
	if _ghost_label != "":
		# On the side the road travels, so it never stands on the man who
		# marches (a road heading west carries its badge to the west).
		var westward: bool = pts[pts.size() - 1].x < pts[pts.size() - 2].x
		_draw_badge(pts[pts.size() - 1], _ghost_label, color, westward)


func _draw_ellipse(center: Vector2, rx: float, ry: float, color: Color, width: float) -> void:
	var pts := PackedVector2Array()
	var steps := 40
	for i in range(steps + 1):
		var a := TAU * float(i) / float(steps)
		pts.append(center + Vector2(cos(a) * rx, sin(a) * ry))
	draw_polyline(pts, color, width, true)


func _draw_arrow_head(from: Vector2, to: Vector2, color: Color) -> void:
	var dir := to - from
	if dir.length() < 0.5:
		return
	dir = dir.normalized()
	var side := Vector2(-dir.y, dir.x)
	var head_len := 11.0
	var tip := to
	var base := to - dir * head_len
	var head := PackedVector2Array([tip, base + side * head_len * 0.55, base - side * head_len * 0.55])
	draw_colored_polygon(PackedVector2Array([tip + dir * 1.5, base + side * head_len * 0.75 - dir, base - side * head_len * 0.75 - dir]), GHOST_SHADOW)
	draw_colored_polygon(head, color)


func _draw_badge(anchor: Vector2, text: String, accent: Color, westward: bool = false) -> void:
	var font: Font = ThemeDB.fallback_font
	if font == null:
		return
	var text_size := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, BADGE_FONT_PX)
	var box_size := text_size + BADGE_PAD * 2.0
	var at := anchor + Vector2(12, -text_size.y - 14)
	if westward:
		at.x = anchor.x - 12.0 - box_size.x
	var box := Rect2(at, box_size)
	# Keep the badge on the layer (a road ending at the screen's edge).
	var room := Rect2(Vector2.ZERO, size)
	if room.size.x > 0.0 and room.size.y > 0.0:
		box.position.x = clampf(box.position.x, 0.0, maxf(0.0, room.size.x - box.size.x))
		box.position.y = clampf(box.position.y, 0.0, maxf(0.0, room.size.y - box.size.y))
	draw_rect(box, BADGE_BG, true)
	draw_rect(box, accent, false, 1.5)
	var baseline := box.position + Vector2(BADGE_PAD.x, BADGE_PAD.y + font.get_ascent(BADGE_FONT_PX))
	draw_string(font, baseline, text, HORIZONTAL_ALIGNMENT_LEFT, -1, BADGE_FONT_PX, Color(0.98, 0.95, 0.88))

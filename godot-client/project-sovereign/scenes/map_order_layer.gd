extends Control

# Row CC, CC-3 "Select, click, Enter" (Pre-Deploy S13c part 2, October 2026):
# the map's ORDER layer — what a selected corps would do, drawn over the map.
#
#   * the RING at the selected piece's feet (one per corps of a CC-5 group);
#   * the GHOST ROAD — the quote's own road, from his feet through every
#     province of it to its end, a pip where he stands at each turn's end,
#     the head an arrow, and the badge ("3 turns · 2 AP") beside it.
#
# CC-5 "The war table" (Pre-Deploy S13c part 3, October 2026) adds a second
# pass beneath them: the ORDER ARROWS — every standing order of ours, a
# dashed line along the road it has still to walk (the backend's
# `tactical_state.order_road`) with its clock on a badge: a march or a
# pursuit ends in an arrowhead, a hold in an anchor, a support or a follow on
# the friend's feet. A click on one is the owner's (`arrow_at`).
#
# SCREEN space, like the label layer (`map_label_layer.gd`): WORLD anchors
# are re-projected through the map camera on every draw, so the line and the
# badge stay crisp and the same width at every zoom, and the layer redraws
# whenever the projection moves (a pan, a zoom, Home). It owns no rule — the
# road, the turns and the price are the backend's, handed in by the renderer
# (`map_renderer_base.gd`, `GET /march_reach`, `GET /march_quotes`, the board).

const RING_COLOR := Color(1.0, 0.86, 0.42, 0.95)
const RING_SHADOW := Color(0.08, 0.06, 0.04, 0.75)
const GHOST_SHADOW := Color(0.08, 0.06, 0.04, 0.62)
const GHOST_COLORS := {
	"march": Color(1.0, 0.92, 0.66, 0.95),
	"move": Color(1.0, 0.96, 0.80, 0.98),      # row PW: the plain move, he arrives now
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

# CC-5: the standing orders' arrows — quieter than the ghost (a lighter line,
# a smaller badge), so a selection's road always reads first.
const ARROW_COLORS := {
	"march": Color(0.96, 0.84, 0.52, 0.88),
	"pursue": Color(0.95, 0.52, 0.38, 0.88),
	"hold": Color(0.74, 0.82, 0.92, 0.92),
	"support": Color(0.60, 0.84, 1.0, 0.88),
	"follow": Color(0.60, 0.84, 1.0, 0.88),
	"halted": Color(1.0, 0.64, 0.24, 0.95),
}
const ARROW_WIDTH := 2.5
const ARROW_DASH := 7.0
const ARROW_HOVER_WIDTH := 4.0
const ARROW_BADGE_PX := 12
const ARROW_DIM := 0.32          # the arrows step back while a corps is selected
const ARROW_HIT_PX := 7.0        # a click within this of the line is the arrow's

# The owning renderer — source of the camera projection.
var _renderer = null
# The rings: [{"at": WORLD feet, "r": WORLD radius}] — one for a selection,
# one a member for a group.
var _rings: Array = []
# Row PW: the piece of ours under the cursor ({} for none) — {"at", "r"}.
var _hover_ring: Dictionary = {}
const HOVER_RING_COLOR := Color(1.0, 0.95, 0.78, 0.85)
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
# CC-5: [{"marshal", "kind", "points" (WORLD, his feet first), "anchor",
# "label", "halted"}] — every standing order of ours.
var _arrows: Array = []
var _arrow_focus := ""           # the selected corps: his arrow stays bright
var _arrow_dimmed := false
var _arrow_hover := ""


func setup(renderer) -> void:
	_renderer = renderer


func set_ring(feet_world: Vector2, radius_world: float) -> void:
	_rings = [{"at": feet_world, "r": radius_world}]
	queue_redraw()


func set_rings(rings: Array) -> void:
	"""CC-5: a ring at every member's feet — [{"at", "r"}] in WORLD space."""
	_rings = rings.duplicate()
	queue_redraw()


func clear_ring() -> void:
	_rings = []
	queue_redraw()


func set_hover_ring(feet_world: Vector2, radius_world: float) -> void:
	"""Row PW (the first playtest: "its hard to click genral pieces"): a quiet
	ring at the feet of the piece of ours under the cursor — the one a click
	would pick — so the eye sees the target before the hand commits."""
	var ring := {"at": feet_world, "r": radius_world}
	if _hover_ring == ring:
		return
	_hover_ring = ring
	queue_redraw()


func clear_hover_ring() -> void:
	if _hover_ring.is_empty():
		return
	_hover_ring = {}
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


func ghost_badge_rect() -> Rect2:
	"""Row PW: where the ghost road's tag stands, in this layer's LOCAL space
	(empty with no tag) — the hover box stands clear of it, so the order's
	price and consequence are never covered by a second box."""
	if _renderer == null or _renderer.map_viewport == null \
			or _ghost_label == "" or _ghost_world.is_empty():
		return Rect2()
	var xform := _projection()
	var pts := PackedVector2Array()
	for p in _ghost_world:
		pts.append(xform * (p as Vector2))
	if _ghost_to_cursor:
		pts.append(_ghost_cursor_local)
	if pts.size() < 2:
		return Rect2()
	var westward: bool = pts[pts.size() - 1].x < pts[pts.size() - 2].x
	return _badge_rect(pts[pts.size() - 1], _ghost_label, westward, BADGE_FONT_PX)


func clear_ghost() -> void:
	_ghost_world = []
	_ghost_kind = ""
	_ghost_label = ""
	_ghost_pips = []
	_ghost_to_cursor = false
	queue_redraw()


func set_arrows(arrows: Array) -> void:
	"""CC-5: every standing order of ours to draw (the renderer builds them
	from the board on every refresh)."""
	_arrows = arrows.duplicate(true)
	if _arrow_hover != "" and not _arrows.any(func(a): return str(a.get("marshal", "")) == _arrow_hover):
		_arrow_hover = ""
	queue_redraw()


func set_arrow_focus(marshal: String, dimmed: bool) -> void:
	"""While a corps (or a group) is selected the arrows step back — all but
	the selected man's own, which shows what a new order would replace."""
	_arrow_focus = marshal
	_arrow_dimmed = dimmed
	queue_redraw()


func set_arrow_hover(marshal: String) -> void:
	if marshal == _arrow_hover:
		return
	_arrow_hover = marshal
	queue_redraw()


func arrow_hovered() -> String:
	return _arrow_hover


func screen_rect() -> Rect2:
	"""The rings and the ghost road's bounding box in this layer's LOCAL
	space (empty with neither) — the confirm card stands clear of it."""
	if _renderer == null or _renderer.map_viewport == null:
		return Rect2()
	var xform := _projection()
	var points: Array = []
	for ring in _rings:
		points.append(xform * (ring["at"] as Vector2))
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


func arrow_rect(marshal: String) -> Rect2:
	"""CC-5: one arrow's box in LOCAL space, its badge included (empty when
	he has none) — the arrow card stands clear of it."""
	for geo in _arrow_geometry():
		if str(geo["marshal"]) != marshal:
			continue
		var pts: PackedVector2Array = geo["pts"]
		var box := Rect2(pts[0], Vector2.ZERO) if pts.size() > 0 else Rect2()
		for p in pts:
			box = box.expand(p)
		return box.merge(geo["badge"]).grow(12.0)
	return Rect2()


func arrow_at(local_point: Vector2) -> String:
	"""CC-5: the corps whose arrow is under `local_point` — its badge, its
	head or anchor, or within `ARROW_HIT_PX` of its line — "" for none. The
	topmost (last drawn) wins."""
	var geometry := _arrow_geometry()
	for i in range(geometry.size() - 1, -1, -1):
		var geo: Dictionary = geometry[i]
		if (geo["badge"] as Rect2).grow(2.0).has_point(local_point):
			return str(geo["marshal"])
		var pts: PackedVector2Array = geo["pts"]
		if pts.is_empty():
			continue
		if pts[pts.size() - 1].distance_to(local_point) <= 11.0:
			return str(geo["marshal"])
		for k in range(pts.size() - 1):
			var near := Geometry2D.get_closest_point_to_segment(local_point, pts[k], pts[k + 1])
			if near.distance_to(local_point) <= ARROW_HIT_PX:
				return str(geo["marshal"])
	return ""


func report() -> Dictionary:
	"""What the layer holds — read by the capture harness."""
	return {
		"ring": not _rings.is_empty(),
		"rings": _rings.size(),
		"ghost_points": _ghost_world.size() + (1 if _ghost_to_cursor else 0),
		"ghost_kind": _ghost_kind,
		"ghost_label": _ghost_label,
		"pips": _ghost_pips.size(),
		"arrows": arrows_report(),
		"arrow_hover": _arrow_hover,
		"arrows_dimmed": _arrow_dimmed,
		"dangers": _dangers.size(),      # row IC: the provinces marked as in danger
	}


func arrows_report() -> Array:
	var out: Array = []
	for a in _arrows:
		out.append({
			"marshal": str(a.get("marshal", "")),
			"kind": str(a.get("kind", "")),
			"points": (a.get("points", []) as Array).size(),
			"anchor": bool(a.get("anchor", false)),
			"label": str(a.get("label", "")),
			"halted": bool(a.get("halted", false)),
		})
	return out


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


# Row PW "Plain Words" (the first playtest: "it seemd liek things randfomly
# flipped back to enemy control"): the provinces that changed hands while the
# turn turned pulse on the map when the report is put away — what changed is
# seen where it changed. WORLD points; FLASH_SECONDS, then gone. With Reduce
# Motion on the rings stand still for the same time.
const FLASH_SECONDS := 3.5
const FLASH_COLOR := Color(1.0, 0.86, 0.42, 1.0)
var _flashes: Array = []
var _flash_from_msec := 0


func set_flashes(points_world: Array) -> void:
	_flashes = points_world.duplicate()
	_flash_from_msec = Time.get_ticks_msec()
	queue_redraw()


func flash_count() -> int:
	return _flashes.size()


# Row IC "the desk" (November 19, 2026): a province of ours that an enemy we
# can see could walk into next turn because nothing holds it (the backend's
# `desk.danger`, `threats.in_danger`). A standing mark, not a pulse: a red
# warning triangle with its "!" — a SHAPE as well as a colour — above the
# province's seat, for as long as the danger stands. WORLD points.
const DANGER_COLOR := Color(0.93, 0.36, 0.28, 0.98)
const DANGER_INK := Color(0.99, 0.95, 0.88, 1.0)
const DANGER_LIFT := 30.0        # px above the province's seat (clear of the pieces)
const DANGER_HALF := 11.0        # half the triangle's base
var _dangers: Array = []
var _danger_names: Array = []    # the province each mark stands for, in the points' order


func set_dangers(points_world: Array, names: Array = []) -> void:
	"""The provinces in danger, as WORLD points (the renderer resolves the
	names); [] clears every mark. `names` are the provinces' own, in the same
	order — lever L3 of the blind reading (reader 2: "Rhineland is named in
	the list, but the red triangle on the map has no name"): the mark wears
	the name the list and the card say."""
	if points_world == _dangers and names == _danger_names:
		return
	_dangers = points_world.duplicate()
	_danger_names = names.duplicate()
	queue_redraw()


func danger_count() -> int:
	return _dangers.size()


func danger_names() -> Array:
	"""The names the marks wear now (read by the driven tests)."""
	return _danger_names.duplicate()


func danger_mark_boxes() -> Array:
	"""Each mark's box for the map's names to dodge (seen in the real client:
	the "Rhineland" plate stood over the name HESSE): [{at: the WORLD point,
	rect: the triangle and its name plate in px FROM the projected point}] —
	a fixed size on screen, whatever the zoom (`map_label_layer.set_mark_boxes`)."""
	var out: Array = []
	var font: Font = ThemeDB.fallback_font
	for i in range(_dangers.size()):
		var label: String = str(_danger_names[i]) if i < _danger_names.size() else ""
		var plate := Vector2.ZERO
		if font != null and label != "":
			plate = font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, BADGE_FONT_PX) + BADGE_PAD * 2.0
			plate.x += 5.0
		var half_h: float = maxf(DANGER_HALF + 3.0, plate.y * 0.5)
		out.append({"at": _dangers[i], "rect": Rect2(-DANGER_HALF - 3.0, -DANGER_LIFT - half_h,
				DANGER_HALF * 2.0 + 6.0 + plate.x, half_h * 2.0)})
	return out


func _draw_dangers(xform: Transform2D) -> void:
	for i in range(_dangers.size()):
		var c: Vector2 = xform * (_dangers[i] as Vector2) + Vector2(0, -DANGER_LIFT)
		var tip := c + Vector2(0, -DANGER_HALF)
		var left := c + Vector2(-DANGER_HALF, DANGER_HALF * 0.8)
		var right := c + Vector2(DANGER_HALF, DANGER_HALF * 0.8)
		var grow := 3.0
		draw_colored_polygon(PackedVector2Array([tip + Vector2(0, -grow), left + Vector2(-grow, grow * 0.7),
			right + Vector2(grow, grow * 0.7)]), RING_SHADOW)
		draw_colored_polygon(PackedVector2Array([tip, left, right]), Utils.cv(DANGER_COLOR))
		# the "!" — a stem and a dot
		draw_line(c + Vector2(0, -5.0), c + Vector2(0, 2.5), DANGER_INK, 2.4, true)
		draw_circle(c + Vector2(0, 6.0), 1.5, DANGER_INK)
		# its province's name, on a small plate beside the mark (the badge's own face)
		var label: String = str(_danger_names[i]) if i < _danger_names.size() else ""
		if label != "":
			var font: Font = ThemeDB.fallback_font
			if font != null:
				var text_size := font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, BADGE_FONT_PX)
				var box := Rect2(c + Vector2(DANGER_HALF + 5.0, -text_size.y * 0.5 - BADGE_PAD.y),
						text_size + BADGE_PAD * 2.0)
				_draw_badge_in(box, label, Utils.cv(DANGER_COLOR), BADGE_FONT_PX, BADGE_BG, false)


func _draw_flashes(xform: Transform2D) -> void:
	if _flashes.is_empty():
		return
	var age: float = float(Time.get_ticks_msec() - _flash_from_msec) / 1000.0
	if age >= FLASH_SECONDS:
		return
	var still: bool = UiSettings.get_reduce_motion()
	var fade: float = clampf(1.0 - age / FLASH_SECONDS, 0.0, 1.0)
	var phase: float = 0.5 if still else fmod(age, 1.0)      # one pulse a second
	for p in _flashes:
		var c: Vector2 = xform * (p as Vector2)
		var r: float = 14.0 + 26.0 * phase
		var ring := Color(FLASH_COLOR, (0.95 if still else 1.0 - phase * 0.7) * fade)
		_draw_ellipse(c, r, r * 0.62, Color(RING_SHADOW, RING_SHADOW.a * fade), 6.0)
		_draw_ellipse(c, r, r * 0.62, ring, 3.0)


# Row PW part 3 (November 19, 2026): the trail a march leaves. A piece that
# walks is followed by a line in its nation's colour, drawn as he goes and
# kept a few seconds after he is set down — where he came from stays on the
# map after the motion is over (the enemy's moves most of all: several pieces
# walk at once, and the eye cannot follow them all). WORLD points.
const TRAIL_LINGER_S := 3.2
const TRAIL_WIDTH := 3.0
var _trails: Array = []          # {points, color, from_msec, march_s}


func add_trail(points_world: Array, color: Color, march_seconds: float) -> void:
	if points_world.size() < 2:
		return
	_trails.append({"points": points_world.duplicate(), "color": color,
		"from_msec": Time.get_ticks_msec(), "march_s": maxf(march_seconds, 0.05)})
	if _trails.size() > 48:
		_trails = _trails.slice(_trails.size() - 48)
	queue_redraw()


func trail_count() -> int:
	return _trails.size()


func clear_trails() -> void:
	_trails = []
	queue_redraw()


func _draw_trails(xform: Transform2D) -> void:
	var now := Time.get_ticks_msec()
	for t in _trails:
		var age: float = float(now - int(t["from_msec"])) / 1000.0
		var march_s: float = float(t["march_s"])
		if age >= march_s + TRAIL_LINGER_S:
			continue
		var pts := PackedVector2Array()
		for p in t["points"]:
			pts.append(xform * (p as Vector2))
		# how far the walker has come
		var shown := _trail_head(pts, clampf(age / march_s, 0.0, 1.0))
		if shown.size() < 2:
			continue
		var fade: float = 1.0 if age <= march_s else clampf(1.0 - (age - march_s) / TRAIL_LINGER_S, 0.0, 1.0)
		var tint: Color = (t["color"] as Color).lightened(0.35)
		draw_polyline(shown, Color(GHOST_SHADOW, GHOST_SHADOW.a * fade), TRAIL_WIDTH + 2.5, true)
		for i in range(shown.size() - 1):
			draw_dashed_line(shown[i], shown[i + 1], Color(tint, 0.95 * fade), TRAIL_WIDTH, 6.0, true, true)
		draw_circle(shown[0], 5.0, Color(GHOST_SHADOW, GHOST_SHADOW.a * fade))
		draw_circle(shown[0], 3.5, Color(tint, 0.95 * fade))
		if age > march_s:
			_draw_arrow_head(shown[shown.size() - 2], shown[shown.size() - 1], Color(tint, 0.95 * fade))


static func _trail_head(pts: PackedVector2Array, share: float) -> PackedVector2Array:
	"""The first `share` (0..1) of a road, by length."""
	var out := PackedVector2Array()
	if pts.size() < 2:
		return out
	var total := 0.0
	for i in range(pts.size() - 1):
		total += pts[i].distance_to(pts[i + 1])
	var want := total * share
	out.append(pts[0])
	for i in range(pts.size() - 1):
		var leg := pts[i].distance_to(pts[i + 1])
		if leg <= want:
			out.append(pts[i + 1])
			want -= leg
		else:
			if leg > 0.0 and want > 0.0:
				out.append(pts[i].lerp(pts[i + 1], want / leg))
			break
	return out


func _process(_delta: float) -> void:
	if _renderer == null or _renderer.map_viewport == null:
		return
	if not _flashes.is_empty():
		if float(Time.get_ticks_msec() - _flash_from_msec) / 1000.0 >= FLASH_SECONDS:
			_flashes = []
		queue_redraw()
	if not _trails.is_empty():
		var now := Time.get_ticks_msec()
		var kept: Array = []
		for t in _trails:
			if float(now - int(t["from_msec"])) / 1000.0 < float(t["march_s"]) + TRAIL_LINGER_S:
				kept.append(t)
		_trails = kept
		queue_redraw()
	if _rings.is_empty() and _ghost_world.is_empty() and _arrows.is_empty() \
			and _hover_ring.is_empty() and _dangers.is_empty():
		return
	if _projection() != _drawn_xform:
		queue_redraw()


func _draw() -> void:
	if _renderer == null or _renderer.map_viewport == null:
		return
	var xform := _projection()
	_drawn_xform = xform
	_draw_arrows()
	_draw_trails(xform)      # row PW part 3: where the marching pieces came from
	_draw_flashes(xform)     # row PW: the provinces that changed hands
	_draw_dangers(xform)     # row IC: the provinces an enemy in sight can walk into
	var zoom: float = xform.get_scale().x
	if not _hover_ring.is_empty():
		# Row PW: under the selection's ring, thinner — "a click picks him".
		var hc: Vector2 = xform * (_hover_ring["at"] as Vector2)
		var hr: float = maxf(float(_hover_ring["r"]) * zoom, 11.0)
		_draw_ellipse(hc, hr, hr * 0.42, RING_SHADOW, 4.0)
		_draw_ellipse(hc, hr, hr * 0.42, HOVER_RING_COLOR, 1.8)
	for ring in _rings:
		var c: Vector2 = xform * (ring["at"] as Vector2)
		var r: float = maxf(float(ring["r"]) * zoom, 9.0)
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
	var color: Color = Utils.cv(GHOST_COLORS.get(_ghost_kind, GHOST_COLORS["march"]))
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


# ── CC-5: the order arrows ─────────────────────────────────────────────────

func _arrow_geometry() -> Array:
	"""Every arrow projected to LOCAL space: its points, its badge's box and
	the side the badge stands on — ONE reading for the draw and the click."""
	var out: Array = []
	if _renderer == null or _renderer.map_viewport == null:
		return out
	var xform := _projection()
	var placed: Array = []
	for a in _arrows:
		var pts := PackedVector2Array()
		for p in a.get("points", []):
			pts.append(xform * (p as Vector2))
		if pts.is_empty():
			continue
		if pts.size() == 1:
			# An order with no road left (a hold where he stands, a pursuit
			# whose road is spent): its mark stands just below his feet, never
			# on his piece.
			pts[0] += Vector2(0, 21)
		var end: Vector2 = pts[pts.size() - 1]
		var westward: bool = pts.size() > 1 and end.x < pts[pts.size() - 2].x
		var label := str(a.get("label", ""))
		var badge := _badge_rect(end, label, westward, ARROW_BADGE_PX) if label != "" else Rect2(end, Vector2.ZERO)
		if badge.size != Vector2.ZERO:
			# Two orders bound for one province would print their badges on
			# one spot: a later badge steps down beneath those placed.
			var steps := 0
			while steps < 8 and _overlaps_any(badge, placed):
				badge.position.y += badge.size.y + 3.0
				steps += 1
			placed.append(badge)
		out.append({"marshal": str(a.get("marshal", "")), "pts": pts, "badge": badge,
			"westward": westward, "arrow": a})
	return out


static func _overlaps_any(box: Rect2, placed: Array) -> bool:
	for r in placed:
		if (r as Rect2).intersects(box):
			return true
	return false


func _draw_arrows() -> void:
	for geo in _arrow_geometry():
		var a: Dictionary = geo["arrow"]
		var pts: PackedVector2Array = geo["pts"]
		var kind := "halted" if bool(a.get("halted", false)) else str(a.get("kind", "march"))
		var color: Color = Utils.cv(ARROW_COLORS.get(kind, ARROW_COLORS["march"]))
		var marshal := str(geo["marshal"])
		if _arrow_dimmed and marshal != _arrow_focus:
			color.a *= ARROW_DIM
		var hovered := marshal == _arrow_hover
		var width := ARROW_HOVER_WIDTH if hovered else ARROW_WIDTH
		var shadow := Color(GHOST_SHADOW, GHOST_SHADOW.a * color.a)
		if pts.size() >= 2:
			draw_polyline(pts, shadow, width + 2.5, true)
			for i in range(pts.size() - 1):
				draw_dashed_line(pts[i], pts[i + 1], color, width, ARROW_DASH, true, true)
		var end: Vector2 = pts[pts.size() - 1]
		if bool(a.get("anchor", false)):
			_draw_anchor(end, color, shadow)
		elif pts.size() >= 2:
			_draw_arrow_head(pts[pts.size() - 2], end, color)
		var label := str(a.get("label", ""))
		if label != "":
			_draw_badge_in(geo["badge"], label, color, ARROW_BADGE_PX,
				Color(BADGE_BG, BADGE_BG.a * (1.0 if color.a > 0.5 else 0.5)), hovered)


func _draw_anchor(at: Vector2, color: Color, shadow: Color) -> void:
	"""A hold's mark: an anchor standing on the province it holds."""
	var top := at + Vector2(0, -15)
	var bottom := at + Vector2(0, -2)
	for pass_i in range(2):
		var c: Color = shadow if pass_i == 0 else color
		var w: float = 4.5 if pass_i == 0 else 2.2
		draw_arc(top + Vector2(0, -2.5), 2.6, 0.0, TAU, 14, c, w * 0.6, true)
		draw_line(top, bottom, c, w, true)
		draw_line(top + Vector2(-5, 3), top + Vector2(5, 3), c, w, true)
		draw_arc(bottom + Vector2(0, -6), 6.5, deg_to_rad(20), deg_to_rad(160), 12, c, w, true)


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
	draw_colored_polygon(PackedVector2Array([tip + dir * 1.5, base + side * head_len * 0.75 - dir, base - side * head_len * 0.75 - dir]), Color(GHOST_SHADOW, GHOST_SHADOW.a * color.a))
	draw_colored_polygon(head, color)


func _badge_rect(anchor: Vector2, text: String, westward: bool, font_px: int) -> Rect2:
	"""Where a badge for `anchor` stands — beside the road's head, on the
	side it travels, kept on the layer."""
	var font: Font = ThemeDB.fallback_font
	if font == null:
		return Rect2(anchor, Vector2.ZERO)
	# Row PW: a badge may run to several lines (the order's tag: its price and
	# clock, then what it does to the province) — as wide as its widest line.
	var text_size := Vector2.ZERO
	for line in text.split("\n"):
		var line_size := font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, font_px)
		text_size.x = maxf(text_size.x, line_size.x)
		text_size.y += line_size.y
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
	return box


func _draw_badge(anchor: Vector2, text: String, accent: Color, westward: bool = false) -> void:
	_draw_badge_in(_badge_rect(anchor, text, westward, BADGE_FONT_PX), text, accent, BADGE_FONT_PX, BADGE_BG, false)


func _draw_badge_in(box: Rect2, text: String, accent: Color, font_px: int, bg: Color, strong: bool) -> void:
	var font: Font = ThemeDB.fallback_font
	if font == null or box.size == Vector2.ZERO:
		return
	draw_rect(box, bg, true)
	draw_rect(box, accent, false, 2.0 if strong else 1.5)
	var baseline := box.position + Vector2(BADGE_PAD.x, BADGE_PAD.y + font.get_ascent(font_px))
	var ink := Color(0.98, 0.95, 0.88, clampf(accent.a + 0.1, 0.0, 1.0))
	var line_h: float = font.get_height(font_px)
	var lines := text.split("\n")
	for i in range(lines.size()):
		# the first line is the order; the lines under it (what it does) a shade quieter
		var line_ink := ink if i == 0 else Color(ink, ink.a * 0.86)
		draw_string(font, baseline + Vector2(0, line_h * float(i)), lines[i],
			HORIZONTAL_ALIGNMENT_LEFT, -1, font_px, line_ink)

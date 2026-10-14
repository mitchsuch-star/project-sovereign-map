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
#
# UXR-X28 (Pre-Deploy S12b): this layer also LAYS OUT the map's text
# furniture — the world-space Labels in the map's SubViewport that the
# renderer builds (the marshals' names and stacks, the fogged forces' names
# and "?" chips, the garrison chips, the sail counts). The two systems never
# saw each other: at the whole-map view (UXR-X4's floor grows the furniture)
# a garrison chip sat on a nation's name and Masséna's name under a "?". One
# priority order now holds (FURNITURE_PRIORITY): the place names keep their
# place; then the standees' names, each nudged off what was placed before it;
# then the chips, each nudged within one chip's width or hidden at that zoom
# (it returns as the zoom makes room). A chip never covers a name and a name
# never covers a chip; a chip that must move takes a place clear of the
# pieces too when its reach holds one. The layout runs once
# per settled zoom (and when the
# furniture or the labels change), never per frame; _draw() keeps a place
# name that the UI pushed off its laid-out place clear of the furniture too.

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
# UI cleanup (July 2 playtest feedback): province labels were drawing straight
# over marshal name stacks and over each other in dense areas (Low Countries).
# Province labels dodge the PIECES (the standees' footprints, pushed by the
# renderer in WORLD coords) by nudging up, and overlap between labels resolves
# greedily — first label in registry order wins, the loser is dropped for this
# zoom level (it returns as you zoom in). The text furniture no longer pushes
# a place name: it yields to it (UXR-X28, below).
const AVOID_RECT_PADDING: float = 2.0
# A label may be nudged at most this many font-heights before it is dropped.
const MAX_AVOID_NUDGE_FONT_HEIGHTS: float = 2.5

# UXR-X28: the furniture's layout order. The place names stand first (they
# are this layer's own tier, placed before any furniture); then the names a
# piece carries; then the chips, which yield.
const FURNITURE_PRIORITY := ["name", "stack", "fog_name", "fog_chip", "garrison", "sail"]
const FURNITURE_NAME_KINDS := ["name", "stack", "fog_name"]
# How far a name may move off its authored place: this share of its width
# sideways, these many of its heights up or down (up is preferred: a name
# floats above its piece). With no free place in that reach it hides at this
# zoom, as a chip does; the census records every hidden item.
const NAME_REACH_WIDTHS: float = 0.75
const NAME_REACH_HEIGHTS: float = 2.5
# A chip moves within one chip's width, or hides at this zoom.
const CHIP_REACH_WIDTHS: float = 1.0
# The clear gap the layout leaves between two laid-out rects (px).
const FURNITURE_GAP: float = 2.0
# Frames to wait after new furniture arrives, so every Label has taken its
# theme's minimum size before it is measured.
const FURNITURE_SETTLE_FRAMES: int = 2

# Period-cartographic label faces (Task 1, July 16, 2026). The map previously
# drew ALL labels with ThemeDB.fallback_font (a plain sans), ignoring the
# game's own serifs. Two DISTINCT faces give the antique-atlas hierarchy:
#   - nations: Marcellus SC — a Roman SMALL-CAPS serif, the classic country
#     tier ("Fʀᴀɴᴄᴇ"); nation display names are Title Case so the small-cap
#     two-height effect renders. Highly legible even at NATION_FONT_MIN (22px).
#   - provinces/cities: Spectral — a lighter serif drawn for screen legibility
#     at small sizes, distinct from both the nation tier and the EB-Garamond
#     UI default. Reads cleanly at PROVINCE_FONT_MIN (14px).
# Both are static regulars already on disk + OFL-credited (THIRD_PARTY_LICENSES).
const NATION_FONT_PATH := "res://assets/fonts/MarcellusSC-Regular.ttf"
const PROVINCE_FONT_PATH := "res://assets/fonts/Spectral-Regular.ttf"

# The owning renderer (map_renderer_base.gd) — source of the SubViewport
# canvas transform used to project world anchors to screen.
var _renderer = null
# Resolved label faces (loaded in setup(); each falls back to the ThemeDB
# fallback face so a missing asset degrades to the old look, never a crash).
var _nation_font: Font = null
var _province_font: Font = null
# [{"text": String, "position": Vector2 (WORLD coords)}]
var _nation_labels: Array = []
var _province_labels: Array = []
var _zoom_level: float = 1.0
# WORLD-coord rects of the pieces (the standees' footprints). Only the
# province tier dodges these — nation labels draw zoomed out where a piece
# is visually negligible.
var _avoid_world_rects: Array = []
# GLOBAL-space rects of UI panels (the command terminal) — see
# set_ui_avoid_rects(). Layout, not map data: clear_labels() leaves them.
var _ui_avoid_rects: Array = []
# S12b (UXR-X28): what the last _draw() placed — [{text, tier, rect}], the
# rect in this Control's local space — read by the capture harness.
var _drawn: Array = []
# UXR-X28: the furniture items (map_renderer_base.gd `_push_furniture`):
# [{kind, nodes: [Control], base: [Vector2]}], and the layout's state.
var _furniture: Array = []
var _furniture_version: int = 0
var _labels_version: int = 0
var _furniture_settle: int = 0
# The key of the last layout (tier, zoom, viewport scale, versions); _draw()
# trusts the layout only while the live key still matches it.
var _laid_out_key: Array = []
# Label index -> its laid-out rect's offset from its projected anchor.
var _laid_out_offsets: Dictionary = {}
# WORLD rects of the furniture the layout left visible, where it put them.
var _furniture_world_rects: Array = []
var _furniture_report: Dictionary = {"moved": 0, "hidden": [], "items": 0}
# The projection the last _draw() used. A camera moved in code (Home, a
# focus on a region) redraws this layer in the same frame, before the camera
# has written the viewport's new transform, and nothing redrew it after: the
# names stood where the old view had them until the next hover. _process
# redraws whenever the live projection is not the drawn one.
var _drawn_xform := Transform2D()


func setup(renderer) -> void:
	_renderer = renderer
	_nation_font = _load_label_font(NATION_FONT_PATH)
	_province_font = _load_label_font(PROVINCE_FONT_PATH)


func _load_label_font(path: String) -> Font:
	"""Load a label face, falling back to the ThemeDB fallback font so a
	missing/unimported asset degrades gracefully instead of crashing _draw()."""
	var f = load(path)
	if f is Font:
		return f
	push_warning("MapLabelLayer: could not load label font %s — using fallback" % path)
	return ThemeDB.fallback_font


func set_labels(nation_labels: Array, province_labels: Array) -> void:
	_nation_labels = nation_labels.duplicate(true)
	_province_labels = province_labels.duplicate(true)
	_labels_version += 1
	queue_redraw()


func set_avoid_rects(avoid_world_rects: Array) -> void:
	_avoid_world_rects = avoid_world_rects.duplicate()
	_labels_version += 1
	queue_redraw()


func set_furniture(items: Array) -> void:
	"""UXR-X28: the map's text furniture to lay out against the place names
	(each item's nodes start from their `base` positions on every layout)."""
	_furniture = items.duplicate()
	_furniture_version += 1
	_furniture_settle = FURNITURE_SETTLE_FRAMES
	queue_redraw()


func set_ui_avoid_rects(global_ui_rects: Array) -> void:
	"""GLOBAL-space rects of UI panels labels must not draw over.

	The map furniture rects above are WORLD-space; the command terminal is a
	screen-space panel on another CanvasLayer, so it was invisible to the
	dodge pass and 'FRANCE' / 'SPAIN' / 'PORTUGAL' rendered straight across
	the Imperial Command window's own text. Applies to BOTH tiers — the
	nation tier previously dodged nothing at all.
	"""
	_ui_avoid_rects = global_ui_rects.duplicate()
	queue_redraw()


func set_zoom_level(zoom_level: float) -> void:
	if is_equal_approx(_zoom_level, zoom_level):
		return
	_zoom_level = zoom_level
	queue_redraw()


func clear_labels() -> void:
	_nation_labels.clear()
	_province_labels.clear()
	_avoid_world_rects.clear()
	_labels_version += 1
	queue_redraw()


func drawn_label_rects() -> Array:
	return _drawn


func furniture_report() -> Dictionary:
	"""What the last furniture layout moved and hid, and whether _draw() is
	reading it at the live zoom (`fresh`)."""
	var out := _furniture_report.duplicate(true)
	out["fresh"] = _renderer != null and _renderer.map_viewport != null \
			and _laid_out_key == _layout_key(_projection())
	return out


# ── the projection and the tier ────────────────────────────────────────────

func _projection() -> Dictionary:
	# UI-2 Part 2: the map SubViewport renders at PHYSICAL resolution, so its
	# canvas_transform maps world -> physical viewport px and the camera zoom is
	# physical-px/world. This layer draws in the Control's LOGICAL space, so undo
	# the physical scale (÷ viewport-pixel-scale) on BOTH the projection transform
	# and the zoom that drives the LOD switch + font size. At scale 1.0 vp == 1.0
	# and this is a no-op (identical to pre-Part-2).
	var vp_scale: float = 1.0
	if _renderer.has_method("_viewport_pixel_scale"):
		vp_scale = _renderer._viewport_pixel_scale()
	var xform: Transform2D = _renderer.map_viewport.canvas_transform
	if not is_equal_approx(vp_scale, 1.0):
		xform = xform.scaled(Vector2(1.0 / vp_scale, 1.0 / vp_scale))
	return {"xform": xform, "zoom": _zoom_level / vp_scale, "vp": vp_scale}


func _tier(logical_zoom: float) -> Dictionary:
	# Per-tier serif faces (setup() guarantees non-null via fallback).
	if logical_zoom >= PROVINCE_LABEL_MIN_ZOOM:
		return {
			"tier": "province", "labels": _province_labels,
			"font": _province_font if _province_font != null else ThemeDB.fallback_font,
			"px": clampf(PROVINCE_FONT_BASE * logical_zoom, PROVINCE_FONT_MIN, PROVINCE_FONT_MAX),
		}
	return {
		"tier": "nation", "labels": _nation_labels,
		"font": _nation_font if _nation_font != null else ThemeDB.fallback_font,
		"px": clampf(NATION_FONT_BASE * logical_zoom, NATION_FONT_MIN, NATION_FONT_MAX),
	}


func _layout_key(proj: Dictionary) -> Array:
	var zoom: float = proj["zoom"]
	return [_tier(zoom)["tier"], zoom, proj["vp"], _labels_version, _furniture_version]


func _label_size(font: Font, text: String, font_screen_px: float) -> Vector2:
	var font_size: int = max(1, int(round(font_screen_px)))
	return font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size)


# ── the furniture layout (UXR-X28) ─────────────────────────────────────────

func _process(_delta: float) -> void:
	if _renderer == null or _renderer.map_viewport == null:
		return
	if _projection()["xform"] != _drawn_xform:
		queue_redraw()
	if _furniture_settle > 0:
		_furniture_settle -= 1
		return
	if _renderer.has_method("is_zoom_settled") and not _renderer.is_zoom_settled():
		return
	var proj := _projection()
	var key := _layout_key(proj)
	if key == _laid_out_key:
		return
	_lay_out(proj)
	_laid_out_key = key
	queue_redraw()


func _lay_out(proj: Dictionary) -> void:
	"""Place the names where they stand with nothing but the pieces and each
	other in their way (no UI, no cull: a pan never changes this), then lay
	the furniture out against them in FURNITURE_PRIORITY's order."""
	var xform: Transform2D = proj["xform"]
	var spec := _tier(proj["zoom"])
	var labels: Array = spec["labels"]
	var pieces: Array = _project_avoid_rects(xform)
	var avoid: Array = pieces if spec["tier"] == "province" else []
	var placed: Array = []
	_laid_out_offsets = {}
	for i in range(labels.size()):
		var text: String = str(labels[i].get("text", ""))
		if text == "":
			continue
		var anchor: Vector2 = xform * Vector2(labels[i].get("position", Vector2.ZERO))
		var text_size := _label_size(spec["font"], text, spec["px"])
		var nudged = _nudge_clear(Rect2(anchor - text_size / 2.0, text_size), avoid)
		if nudged == null:
			continue
		var rect: Rect2 = nudged
		if _hits_any(rect, placed):
			continue
		placed.append(rect)
		_laid_out_offsets[i] = rect.position - anchor
	_lay_out_furniture(xform, placed, pieces)


func _ordered_furniture() -> Array:
	# Stable: FURNITURE_PRIORITY first, then the renderer's own build order.
	var rows: Array = []
	for i in range(_furniture.size()):
		var item: Dictionary = _furniture[i]
		var rank: int = FURNITURE_PRIORITY.find(str(item.get("kind", "")))
		rows.append([rank if rank >= 0 else FURNITURE_PRIORITY.size(), i, item])
	rows.sort_custom(_by_rank_then_order)
	var out: Array = []
	for row in rows:
		out.append(row[2])
	return out


func _lay_out_furniture(xform: Transform2D, obstacles: Array, pieces: Array) -> void:
	# `obstacles` are hard (a place name, a laid-out name or chip: never
	# covered); `pieces` are soft, for the chips: a chip that must move
	# anyway prefers a place clear of the standees too (Masséna's "?" sat on
	# his piece), and covers one only when its reach holds no other. A chip
	# whose own place is clear never moves for a piece. The names do not
	# weigh the pieces: a name over its own stack reads as its own, and the
	# room a name gives up to dodge one cost a fogged name its place.
	var inv := xform.affine_inverse()
	var moved := 0
	var hidden: Array = []
	var count := 0
	_furniture_world_rects = []
	for item in _ordered_furniture():
		var nodes: Array = item.get("nodes", [])
		if not _item_alive(nodes):
			continue
		_reset_item(item)
		var world := _item_world_rect(nodes)
		if world.size.x <= 0.0 or world.size.y <= 0.0:
			continue
		count += 1
		var kind := str(item.get("kind", ""))
		var r := _project_rect(xform, world)
		var reach_x: float = r.size.x * (NAME_REACH_WIDTHS if kind in FURNITURE_NAME_KINDS else CHIP_REACH_WIDTHS)
		var reach_y: float = r.size.y * NAME_REACH_HEIGHTS if kind in FURNITURE_NAME_KINDS else reach_x
		var x_cost: float = 1.5 if kind in FURNITURE_NAME_KINDS else 1.0
		var off = _free_offset(r, obstacles, reach_x, reach_y, x_cost)
		if off != null and off != Vector2.ZERO and not (kind in FURNITURE_NAME_KINDS):
			var clear_of_pieces = _free_offset(r, obstacles + pieces, reach_x, reach_y, x_cost)
			if clear_of_pieces != null:
				off = clear_of_pieces
		if off == null:
			for n in nodes:
				(n as CanvasItem).visible = false
			hidden.append("%s:%s" % [kind, _item_text(nodes)])
			continue
		var d: Vector2 = off
		var dw: Vector2 = inv.basis_xform(d)
		if d != Vector2.ZERO:
			for n in nodes:
				(n as Control).position += dw
			moved += 1
		obstacles.append(Rect2(r.position + d, r.size))
		_furniture_world_rects.append(Rect2(world.position + dw, world.size))
	_furniture_report = {"moved": moved, "hidden": hidden, "items": count}


func _item_alive(nodes: Array) -> bool:
	if nodes.is_empty():
		return false
	for n in nodes:
		if n == null or not is_instance_valid(n) or (n as Node).is_queued_for_deletion() \
				or not (n as Node).is_inside_tree():
			return false
	return true


func _reset_item(item: Dictionary) -> void:
	var nodes: Array = item.get("nodes", [])
	var base: Array = item.get("base", [])
	for i in range(nodes.size()):
		var n: Control = nodes[i]
		if i < base.size():
			n.position = base[i]
		n.visible = true


func _item_world_rect(nodes: Array) -> Rect2:
	# The nodes' own rects in the SubViewport's canvas (= world coords: the
	# map root sits at the origin), each at least its combined minimum size —
	# a Label grows past the size it was given to fit its theme's line.
	var out := Rect2()
	var first := true
	for n in nodes:
		var c: Control = n
		var sz := Vector2(maxf(c.size.x, c.get_combined_minimum_size().x),
				maxf(c.size.y, c.get_combined_minimum_size().y))
		var r := Rect2(c.global_position, sz)
		out = r if first else out.merge(r)
		first = false
	return out


func _item_text(nodes: Array) -> String:
	for n in nodes:
		if n is Label:
			return (n as Label).text
		for c in (n as Node).get_children():
			if c is Label:
				return (c as Label).text
	return ""


func _project_rect(xform: Transform2D, world: Rect2) -> Rect2:
	var a: Vector2 = xform * world.position
	var b: Vector2 = xform * world.end
	return Rect2(a, b - a).abs()


func _free_offset(r: Rect2, obstacles: Array, reach_x: float, reach_y: float, x_cost: float):
	"""The smallest move (by x_cost * |dx| + |dy|, up before down) that takes
	r clear of every obstacle, within reach; null when there is none. The
	candidates are the moves that put an edge of r FURNITURE_GAP beyond an
	edge of an obstacle in its reach, alone and in pairs."""
	var zone := r.grow_individual(reach_x, reach_y, reach_x, reach_y)
	var near: Array = []
	for o in obstacles:
		if (o as Rect2).intersects(zone):
			near.append(o)
	if not _hits_any(r, near):
		return Vector2.ZERO
	var xs: Array = [0.0]
	var ys: Array = [0.0]
	for o in near:
		var orect: Rect2 = o
		for dx in [orect.position.x - r.end.x - FURNITURE_GAP, orect.end.x - r.position.x + FURNITURE_GAP]:
			if absf(dx) <= reach_x and not xs.has(dx):
				xs.append(dx)
		for dy in [orect.position.y - r.end.y - FURNITURE_GAP, orect.end.y - r.position.y + FURNITURE_GAP]:
			if absf(dy) <= reach_y and not ys.has(dy):
				ys.append(dy)
	var candidates: Array = []
	for dx in xs:
		for dy in ys:
			if dx == 0.0 and dy == 0.0:
				continue
			var cost: float = absf(dx) * x_cost + absf(dy) + (0.25 if dy > 0.0 else 0.0)
			candidates.append([cost, dy, dx])
	candidates.sort_custom(_by_cost_then_up)
	for c in candidates:
		var d := Vector2(c[2], c[1])
		if not _hits_any(Rect2(r.position + d, r.size), near):
			return d
	return null


static func _by_rank_then_order(a: Array, b: Array) -> bool:
	return a[0] < b[0] or (a[0] == b[0] and a[1] < b[1])


static func _by_cost_then_up(a: Array, b: Array) -> bool:
	# [cost, dy, dx]: the cheaper move; at a tie the higher, then the leftmost.
	if a[0] != b[0]:
		return a[0] < b[0]
	if a[1] != b[1]:
		return a[1] < b[1]
	return a[2] < b[2]


func _hits_any(rect: Rect2, rects: Array) -> bool:
	for other in rects:
		if rect.intersects(other):
			return true
	return false


# ── the draw ───────────────────────────────────────────────────────────────

func _draw():
	_drawn = []
	if _renderer == null or _renderer.map_viewport == null:
		return
	var proj := _projection()
	var spec := _tier(proj["zoom"])
	var font: Font = spec["font"]
	if font == null:
		return
	var xform: Transform2D = proj["xform"]
	_drawn_xform = xform
	var avoid: Array = _project_avoid_rects(xform) if spec["tier"] == "province" else []
	# The layout is trusted only at the zoom it was made for; while a zoom
	# eases the names draw as before it, and the furniture follows once the
	# zoom settles.
	var fresh: bool = _laid_out_key == _layout_key(proj)
	var guard: Array = []
	if fresh:
		for wr in _furniture_world_rects:
			guard.append(_project_rect(xform, wr).grow(AVOID_RECT_PADDING))
	_draw_label_tier(spec, xform, avoid, _local_ui_avoid_rects(), guard, fresh)


func _local_ui_avoid_rects() -> Array:
	"""UI panel rects converted from GLOBAL space into this Control's own."""
	if _ui_avoid_rects.is_empty():
		return []
	var out: Array = []
	var inv := get_global_transform().affine_inverse()
	for rect in _ui_avoid_rects:
		if not rect is Rect2:
			continue
		var top_left: Vector2 = inv * rect.position
		var bottom_right: Vector2 = inv * rect.end
		out.append(Rect2(top_left, bottom_right - top_left).abs().grow(AVOID_RECT_PADDING))
	return out


func _project_avoid_rects(xform: Transform2D) -> Array:
	var projected: Array = []
	for rect in _avoid_world_rects:
		if not rect is Rect2:
			continue
		projected.append(_project_rect(xform, rect).grow(AVOID_RECT_PADDING))
	return projected


func _draw_label_tier(spec: Dictionary, xform: Transform2D, avoid: Array, ui_rects: Array,
		guard: Array, fresh: bool) -> void:
	var font: Font = spec["font"]
	var labels: Array = spec["labels"]
	var font_screen_px: float = spec["px"]
	var font_size: int = max(1, int(round(font_screen_px)))
	var outline_size: int = max(2, int(round(font_screen_px / 6.0)))
	var cull_rect := Rect2(Vector2.ZERO, size).grow(OFFSCREEN_CULL_MARGIN)
	var placed_rects: Array = []
	for i in range(labels.size()):
		var text: String = str(labels[i].get("text", ""))
		if text == "":
			continue
		var center: Vector2 = xform * Vector2(labels[i].get("position", Vector2.ZERO))
		if not cull_rect.has_point(center):
			continue
		var text_size := _label_size(font, text, font_screen_px)
		var label_rect = null
		# A name at its laid-out place stands there: the furniture yielded
		# to it (UXR-X28). Only the UI or an earlier name moves it off.
		if fresh and _laid_out_offsets.has(i):
			var natural := Rect2(center + Vector2(_laid_out_offsets[i]), text_size)
			if not _hits_any(natural, ui_rects) and not _hits_any(natural, placed_rects):
				label_rect = natural
		if label_rect == null:
			# Off its laid-out place (the command window pushed it, or the
			# layout dropped it): it dodges the pieces and the UI by nudging
			# up, and the laid-out furniture too, which never moved for it;
			# dropped when the nudge would exceed the readable budget.
			var nudged = _nudge_clear(Rect2(center - text_size / 2.0, text_size),
					avoid + ui_rects + guard)
			if nudged == null:
				continue
			label_rect = nudged
			# Greedy label-vs-label overlap: first label placed wins, later
			# overlappers are dropped for this frame (they reappear as zoom
			# makes room). Registry order is stable, so no frame-to-frame pop.
			if _hits_any(label_rect, placed_rects):
				continue
		placed_rects.append(label_rect)
		_drawn.append({"text": text, "tier": spec["tier"], "rect": label_rect})
		var draw_pos := Vector2(
			label_rect.position.x,
			label_rect.get_center().y + text_size.y / 4.0
		)
		draw_string_outline(
			font, draw_pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			font_size, outline_size, LABEL_OUTLINE_COLOR
		)
		draw_string(
			font, draw_pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			font_size, LABEL_TEXT_COLOR
		)


func _nudge_clear(label_rect: Rect2, avoid_rects: Array):
	"""Return the label rect shifted up until it clears every avoid rect,
	or null when clearing it would exceed the nudge budget."""
	if avoid_rects.is_empty():
		return label_rect
	var rect := label_rect
	var max_nudge: float = rect.size.y * MAX_AVOID_NUDGE_FONT_HEIGHTS
	# Two passes: a nudge that clears one rect can land on another.
	for _pass in range(2):
		var collided := false
		for avoid_rect in avoid_rects:
			if rect.intersects(avoid_rect):
				collided = true
				rect.position.y = avoid_rect.position.y - rect.size.y - AVOID_RECT_PADDING
		if not collided:
			return rect
		if label_rect.position.y - rect.position.y > max_nudge:
			return null
	for avoid_rect in avoid_rects:
		if rect.intersects(avoid_rect):
			return null
	return rect

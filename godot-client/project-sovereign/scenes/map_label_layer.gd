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
# UI cleanup (July 2 playtest feedback): province labels were drawing straight
# over marshal name stacks and over each other in dense areas (Low Countries).
# Labels now dodge "occupied" rects (army markers + name stacks + garrison
# chips, pushed by the renderer in WORLD coords) by nudging up, and overlap
# between labels resolves greedily — first label in registry order wins, the
# loser is dropped for this zoom level (it returns as you zoom in).
const AVOID_RECT_PADDING: float = 2.0
# A label may be nudged at most this many font-heights before it is dropped.
const MAX_AVOID_NUDGE_FONT_HEIGHTS: float = 2.5

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
# WORLD-coord rects occupied by dynamic map furniture (marshal icons + name
# stacks + garrison chips). Only the province tier dodges these — nation
# labels draw zoomed out where the furniture is visually negligible.
var _avoid_world_rects: Array = []
# GLOBAL-space rects of UI panels (the command terminal) — see
# set_ui_avoid_rects(). Layout, not map data: clear_labels() leaves them.
var _ui_avoid_rects: Array = []
# Screen-projected avoid rects for the tier currently being drawn.
var _projected_avoid_rects: Array = []


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
	queue_redraw()


func set_avoid_rects(avoid_world_rects: Array) -> void:
	_avoid_world_rects = avoid_world_rects.duplicate()
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
	queue_redraw()


func _draw():
	if _renderer == null or _renderer.map_viewport == null:
		return
	# Per-tier serif faces (setup() guarantees non-null via fallback). Guard
	# once more in case _draw() ever fires before setup().
	var nation_font: Font = _nation_font if _nation_font != null else ThemeDB.fallback_font
	var province_font: Font = _province_font if _province_font != null else ThemeDB.fallback_font
	if nation_font == null or province_font == null:
		return
	# UI-2 Part 2: the map SubViewport now renders at PHYSICAL resolution, so its
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
	var logical_zoom: float = _zoom_level / vp_scale
	var ui_rects: Array = _local_ui_avoid_rects()
	if logical_zoom >= PROVINCE_LABEL_MIN_ZOOM:
		_projected_avoid_rects = _project_avoid_rects(xform) + ui_rects
		_draw_label_tier(
			province_font, _province_labels, xform,
			clampf(PROVINCE_FONT_BASE * logical_zoom, PROVINCE_FONT_MIN, PROVINCE_FONT_MAX)
		)
	else:
		_projected_avoid_rects = ui_rects
		_draw_label_tier(
			nation_font, _nation_labels, xform,
			clampf(NATION_FONT_BASE * logical_zoom, NATION_FONT_MIN, NATION_FONT_MAX)
		)


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
		var top_left: Vector2 = xform * rect.position
		var bottom_right: Vector2 = xform * rect.end
		projected.append(
			Rect2(top_left, bottom_right - top_left).abs().grow(AVOID_RECT_PADDING)
		)
	return projected


func _draw_label_tier(font: Font, labels: Array, xform: Transform2D, font_screen_px: float) -> void:
	var font_size: int = max(1, int(round(font_screen_px)))
	var outline_size: int = max(2, int(round(font_screen_px / 6.0)))
	var cull_rect := Rect2(Vector2.ZERO, size).grow(OFFSCREEN_CULL_MARGIN)
	var placed_rects: Array = []
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
		var label_rect := Rect2(center - text_size / 2.0, text_size)
		# Dodge map furniture (army markers / name stacks / garrison chips):
		# nudge the label upward until clear; drop it when the nudge would
		# exceed the readable budget.
		var nudged = _nudge_clear_of_avoid_rects(label_rect)
		if nudged == null:
			continue
		label_rect = nudged
		# Greedy label-vs-label overlap: first label placed wins, later
		# overlappers are dropped for this frame (they reappear as zoom
		# makes room). Registry order is stable, so no frame-to-frame pop.
		var overlaps := false
		for prev_rect in placed_rects:
			if label_rect.intersects(prev_rect):
				overlaps = true
				break
		if overlaps:
			continue
		placed_rects.append(label_rect)
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


func _nudge_clear_of_avoid_rects(label_rect: Rect2):
	"""Return the label rect shifted up until it clears every avoid rect,
	or null when clearing it would exceed the nudge budget."""
	if _projected_avoid_rects.is_empty():
		return label_rect
	var rect := label_rect
	var max_nudge: float = rect.size.y * MAX_AVOID_NUDGE_FONT_HEIGHTS
	# Two passes: a nudge that clears one rect can land on another.
	for _pass in range(2):
		var collided := false
		for avoid_rect in _projected_avoid_rects:
			if rect.intersects(avoid_rect):
				collided = true
				rect.position.y = avoid_rect.position.y - rect.size.y - AVOID_RECT_PADDING
		if not collided:
			return rect
		if label_rect.position.y - rect.position.y > max_nudge:
			return null
	for avoid_rect in _projected_avoid_rects:
		if rect.intersects(avoid_rect):
			return null
	return rect

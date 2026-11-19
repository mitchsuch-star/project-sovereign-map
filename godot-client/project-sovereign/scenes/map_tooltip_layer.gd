extends Control

var _visible_tooltip: bool = false
var _lines: Array = []
var _width: float = 0.0
var _panel_color: Color = Color(0.1, 0.1, 0.15, 0.95)
var _border_color: Color = Color.WHITE
var _mouse_position: Vector2 = Vector2.ZERO
# Row PW: a box on the map this one must not cover (the order's tag at the
# head of a ghost road) — LOCAL space; empty for none.
var _avoid: Rect2 = Rect2()


func show_tooltip(lines: Array, width: float, panel_color: Color, border_color: Color,
		mouse_position: Vector2, avoid: Rect2 = Rect2()):
	_visible_tooltip = true
	_lines = lines.duplicate(true)
	_width = width
	_panel_color = panel_color
	_border_color = border_color
	_mouse_position = mouse_position
	_avoid = avoid
	queue_redraw()


func clear_tooltip():
	if not _visible_tooltip and _lines.is_empty():
		return
	_visible_tooltip = false
	_lines.clear()
	queue_redraw()


# UXR-X4 (Pre-Deploy S9b): the hover tooltip's two tiers read at the theme's
# sizes — the body at Caption (14), the title at Lead (18), both times Text
# size — where they were raw 11 / 14 px draw_string text (the body under the
# caption floor, and seen by no census, since a draw call is not a node). The
# callers keep asking for 11 (the body) or 14 (a title); the box widens with
# the type, and a line's height is the font's own.
const BODY_DESIGN_PX := 11
const TITLE_DESIGN_PX := 14
const BODY_PX := 14
const TITLE_PX := 18


static func line_px(design_size: int) -> int:
	return Utils.text_px(TITLE_PX if design_size >= TITLE_DESIGN_PX else BODY_PX)


static func type_ratio() -> float:
	"""How much wider the box draws than the width its caller authored for
	the 11-px body."""
	return float(line_px(BODY_DESIGN_PX)) / float(BODY_DESIGN_PX)


func _line_height(design_size: int) -> float:
	var font = ThemeDB.fallback_font
	var px := line_px(design_size)
	return (font.get_height(px) if font != null else float(px) * 1.3) + 2.0


func _draw():
	if not _visible_tooltip or _lines.is_empty():
		return

	var tooltip_size = _measure_tooltip(_lines, _width)
	var tooltip_pos = _clamp_tooltip_pos(_mouse_position + Vector2(15, 15), tooltip_size)
	var font = ThemeDB.fallback_font
	var padding = 10.0
	var text_x = tooltip_pos.x + padding
	var text_y = tooltip_pos.y + padding

	draw_rect(Rect2(tooltip_pos, tooltip_size), _panel_color)
	draw_rect(Rect2(tooltip_pos, tooltip_size), _border_color, false, 2.0)

	for line in _lines:
		if line.get("spacer", false):
			text_y += float(line.get("height", 8.0))
			continue

		var design_size = int(line.get("size", BODY_DESIGN_PX))
		var line_height = _line_height(design_size)
		draw_string(
			font,
			Vector2(text_x, text_y + line_height - 4.0),
			str(line.get("text", "")),
			HORIZONTAL_ALIGNMENT_LEFT,
			-1,
			line_px(design_size),
			line.get("color", Color.WHITE)
		)
		text_y += line_height


func _measure_tooltip(lines: Array, width: float) -> Vector2:
	var padding = 10.0
	var height = padding * 2.0
	for line in lines:
		if line.get("spacer", false):
			height += float(line.get("height", 8.0))
		else:
			height += _line_height(int(line.get("size", BODY_DESIGN_PX)))
	return Vector2(width * type_ratio(), height)


func _clamp_tooltip_pos(pos: Vector2, tooltip_size: Vector2) -> Vector2:
	var view: Vector2 = get_viewport_rect().size
	var top_floor: float = Utils.TOP_BAR_HEIGHT + Utils.top_bar_growth() + 4.0 - global_position.y
	var left_floor: float = -global_position.x
	var placed := clamp_box(pos, tooltip_size, _mouse_position, view, top_floor, left_floor)
	if _avoid.size == Vector2.ZERO or not Rect2(placed, tooltip_size).intersects(_avoid):
		return placed
	return clear_of(placed, tooltip_size, _mouse_position, view, top_floor, left_floor, _avoid)


static func clear_of(placed: Vector2, box: Vector2, mouse: Vector2, view: Vector2,
		top_floor: float, left_floor: float, avoid: Rect2) -> Vector2:
	"""Row PW: the hover box's place when its usual one would cover `avoid`
	(the order's tag) — the cursor's other three corners in turn, each held on
	the screen; the first that leaves the tag whole wins, else the usual place
	(a view too small for both: the box is the older word)."""
	var gap := 15.0
	var corners := [
		Vector2(mouse.x - gap - box.x, mouse.y + gap),      # below, left
		Vector2(mouse.x + gap, mouse.y - gap - box.y),      # above, right
		Vector2(mouse.x - gap - box.x, mouse.y - gap - box.y),   # above, left
	]
	for corner in corners:
		var at: Vector2 = corner
		at.x = clampf(at.x, left_floor, maxf(left_floor, view.x - box.x))
		at.y = clampf(at.y, top_floor, maxf(top_floor, view.y - box.y - 4.0))
		if not Rect2(at, box).intersects(avoid):
			return at
	return placed


static func clamp_box(pos: Vector2, box: Vector2, mouse: Vector2, view: Vector2,
		top_floor: float, left_floor: float = 0.0) -> Vector2:
	"""Row PW (November 18, 2026 — the first playtest, at 5120x1440 and Interface
	Scale 1.8: a view 800 units tall): where the hover box stands. Below-right
	of the cursor; flipped above it where it would pass the bottom edge — and
	then, the half the old rule lacked, held WHOLE on the screen: never above
	`top_floor` (the top bar's strip covered a marshal's name and half his
	figures on any hover in the middle band of a short view) and never past
	the left edge. A box taller than the room stands at the floor and runs
	off the bottom, the lines a reader starts with kept."""
	if pos.x + box.x > view.x:
		pos.x = view.x - box.x
	if pos.y + box.y > view.y:
		pos.y = mouse.y - box.y - 5.0
	if pos.y < top_floor:
		# No room above the cursor either: as low as the screen lets it stand
		# (beside the cursor, which the x-shift above already cleared).
		pos.y = maxf(top_floor, view.y - box.y - 4.0)
	pos.x = maxf(pos.x, left_floor)
	return pos

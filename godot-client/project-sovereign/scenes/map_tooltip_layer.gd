extends Control

var _visible_tooltip: bool = false
var _lines: Array = []
var _width: float = 0.0
var _panel_color: Color = Color(0.1, 0.1, 0.15, 0.95)
var _border_color: Color = Color.WHITE
var _mouse_position: Vector2 = Vector2.ZERO


func show_tooltip(lines: Array, width: float, panel_color: Color, border_color: Color, mouse_position: Vector2):
	_visible_tooltip = true
	_lines = lines.duplicate(true)
	_width = width
	_panel_color = panel_color
	_border_color = border_color
	_mouse_position = mouse_position
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
	var viewport_size = get_viewport_rect().size
	if pos.x + tooltip_size.x > viewport_size.x:
		pos.x = viewport_size.x - tooltip_size.x
	if pos.y + tooltip_size.y > viewport_size.y:
		pos.y = _mouse_position.y - tooltip_size.y - 5.0
	return pos

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

		var font_size = int(line.get("size", 11))
		var line_height = _tooltip_line_height(font_size)
		draw_string(
			font,
			Vector2(text_x, text_y + line_height - 2.0),
			str(line.get("text", "")),
			HORIZONTAL_ALIGNMENT_LEFT,
			-1,
			font_size,
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
			height += _tooltip_line_height(int(line.get("size", 11)))
	return Vector2(width, height)


func _tooltip_line_height(font_size: int) -> float:
	return 20.0 if font_size >= 14 else 16.0


func _clamp_tooltip_pos(pos: Vector2, tooltip_size: Vector2) -> Vector2:
	var viewport_size = get_viewport_rect().size
	if pos.x + tooltip_size.x > viewport_size.x:
		pos.x = viewport_size.x - tooltip_size.x
	if pos.y + tooltip_size.y > viewport_size.y:
		pos.y = _mouse_position.y - tooltip_size.y - 5.0
	return pos

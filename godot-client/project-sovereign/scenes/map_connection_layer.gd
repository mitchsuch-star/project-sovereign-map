extends Control

# Slice 7.5 fold: connection lines (the Europe map's 12 hand-authored sea
# links) draw DASHED so they read as deliberate crossing routes on the chart
# — a solid light line blended into the sea art and looked like an artifact.
const DASH_LENGTH: float = 12.0

var _connections: Array = []
var _line_color: Color = Color(0.6, 0.6, 0.6)
var _line_width: float = 2.0


func set_connections(connections: Array, line_color: Color, line_width: float = 2.0):
	_connections = connections.duplicate(true)
	_line_color = line_color
	_line_width = line_width
	queue_redraw()


func clear_connections():
	_connections.clear()
	queue_redraw()


func _draw():
	for connection in _connections:
		var start_pos = connection.get("start", Vector2.ZERO)
		var end_pos = connection.get("end", Vector2.ZERO)
		draw_dashed_line(start_pos, end_pos, _line_color, _line_width, DASH_LENGTH, true, true)

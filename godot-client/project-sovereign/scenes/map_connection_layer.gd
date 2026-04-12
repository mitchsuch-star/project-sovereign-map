extends Control

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
		draw_line(start_pos, end_pos, _line_color, _line_width, true)

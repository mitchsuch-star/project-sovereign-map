extends Control

# Slice 7.5 fold: connection lines (the Europe map's 12 hand-authored sea
# links) draw DASHED so they read as deliberate crossing routes on the chart
# — a solid light line blended into the sea art and looked like an artifact.
#
# DEF-5 naval (NAVAL_SPEC §9, v1.0.4 legibility contract): each segment may
# carry its own verdict tint — normal = open/uncontested, crimson = shut to
# the player's movement, gold = window open — and blockaded dockyard
# provinces draw a small crimson anchor glyph (the watchtower-glyph idiom).
# The map is where movement decisions are made, so the answer lives here.
const DASH_LENGTH: float = 12.0

var _connections: Array = []
var _line_color: Color = Color(0.6, 0.6, 0.6)
var _line_width: float = 2.0
var _port_glyphs: Array = []
const GLYPH_COLOR := Color(0.85, 0.25, 0.25, 0.95)
const GLYPH_RADIUS: float = 7.0


func set_connections(connections: Array, line_color: Color, line_width: float = 2.0):
	_connections = connections.duplicate(true)
	_line_color = line_color
	_line_width = line_width
	queue_redraw()


func clear_connections():
	_connections.clear()
	queue_redraw()


func set_port_glyphs(glyph_positions: Array):
	# Positions in this layer's coordinate space (blockaded dockyards).
	_port_glyphs = glyph_positions.duplicate(true)
	queue_redraw()


func _draw():
	for connection in _connections:
		var start_pos = connection.get("start", Vector2.ZERO)
		var end_pos = connection.get("end", Vector2.ZERO)
		var seg_color: Color = connection.get("color", _line_color)
		var seg_width: float = connection.get("width", _line_width)
		draw_dashed_line(start_pos, end_pos, seg_color, seg_width, DASH_LENGTH, true, true)
	for glyph_pos in _port_glyphs:
		if not (glyph_pos is Vector2):
			continue
		# A small fouled anchor: ring + shank + stock — unmistakable at map
		# scale and colorblind-safe by shape.
		draw_arc(glyph_pos, GLYPH_RADIUS, 0.0, TAU, 16, GLYPH_COLOR, 2.0, true)
		draw_line(glyph_pos + Vector2(0, -GLYPH_RADIUS - 4), glyph_pos + Vector2(0, GLYPH_RADIUS - 2), GLYPH_COLOR, 2.0)
		draw_line(glyph_pos + Vector2(-4, -GLYPH_RADIUS - 2), glyph_pos + Vector2(4, -GLYPH_RADIUS - 2), GLYPH_COLOR, 2.0)

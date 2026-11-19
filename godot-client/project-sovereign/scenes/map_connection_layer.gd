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
var _line_color: Color = Utils.MAP_CONNECTION_GREY
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
		draw_anchor(self, glyph_pos, GLYPH_RADIUS, Utils.cv(GLYPH_COLOR))


static func draw_anchor(item: CanvasItem, at: Vector2, r: float, color: Color) -> void:
	"""A small anchor — a ring at the head, the stock across under it, the
	shank down, and the two arms curving up from its foot. Row PW part 3: the
	mark was a ring with a line through it, and three blind readers of three
	read it as a stopwatch. One drawing for the map and for the map's key."""
	var head := at + Vector2(0, -r - 2.0)
	item.draw_arc(head, 2.6, 0.0, TAU, 12, color, 1.8, true)                    # the ring
	item.draw_line(at + Vector2(-r * 0.6, -r + 2.5), at + Vector2(r * 0.6, -r + 2.5), color, 2.0)   # the stock
	item.draw_line(head + Vector2(0, 2.6), at + Vector2(0, r + 1.0), color, 2.0)                   # the shank
	item.draw_arc(at + Vector2(0, 1.0), r, deg_to_rad(12.0), deg_to_rad(168.0), 14, color, 2.0, true)  # the arms
	# the flukes: a short barb at each arm's tip
	var tip_r := at + Vector2(0, 1.0) + Vector2(cos(deg_to_rad(12.0)), sin(deg_to_rad(12.0))) * r
	var tip_l := at + Vector2(0, 1.0) + Vector2(cos(deg_to_rad(168.0)), sin(deg_to_rad(168.0))) * r
	item.draw_line(tip_r, tip_r + Vector2(-3.5, -1.0), color, 2.0)
	item.draw_line(tip_l, tip_l + Vector2(3.5, -1.0), color, 2.0)

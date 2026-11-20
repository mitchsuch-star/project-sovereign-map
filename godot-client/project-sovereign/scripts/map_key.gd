extends PanelContainer

# =============================================================================
# INK & IRON — The Map's Key (row PW part 3, November 19, 2026)
# =============================================================================
# The first player's readers, of the map: "the '?' markers, the numbers in
# circles with ships, the '12k' boxes … no key on the screen". Every mark the
# map draws is shown here as the map draws it — the same plaque, the same
# piece, the same colours — beside what it means in everyday words (golden
# rule 11). Opened from the map's own controls ("Key") and by K; it is a HUD
# panel, never a modal: the map stays in hand while it is read.
#
# Display only (golden rule 6): the key reads nothing of the game's state.
# No `class_name` — its owner loads it by path, as the plaques are loaded.
# =============================================================================

const MapPlaque = preload("res://scripts/map_plaque.gd")

const TITLE := "MAP KEY"
const CLOSE_HINT := "Esc or × closes"
const SAMPLE_SIZE := Vector2(64, 34)
const WORDS_WIDTH := 360.0
const COLUMN_WIDTH := 64.0 + 10.0 + WORDS_WIDTH + 22.0
# The sections each column holds, by how many columns the room seats.
const COLUMNS := {
	3: [["ARMIES"], ["THE SEA", "THE LAND"], ["ORDERS"]],
	2: [["ARMIES", "THE SEA"], ["THE LAND", "ORDERS"]],
	1: [["ARMIES", "THE SEA", "THE LAND", "ORDERS"]],
}

# [section, sample kind, the words]. The words say what the mark IS and what
# the player can DO about it; each claim is the renderer's own rule
# (`map_renderer_base.gd`: the plaques §2760–2884, the fleets §5143, the sea
# links' verdict tints §1876, the reach bands ORDER_BAND_COLORS; the order
# layer's arrows ARROW_COLORS).
const ENTRIES := [
	["ARMIES", "piece", "A corps. Its coat is its nation's colour; the figure is its arm — foot, horse or guns. Click one of yours to give it an order."],
	["ARMIES", "name", "Who commands it. \"· 2 more\" means other corps stand in the same province — click the name to pick one."],
	["ARMIES", "fog", "A force seen through the fog of war: someone is there, but you do not have a count. Hover it for a rough size; scout the province to know."],
	["ARMIES", "garrison", "A garrison holding the province, and its men (12k = 12,000). The stripe is the colour of the nation that holds it. \"?\" = strength unknown."],
	["THE SEA", "sail", "A fleet, and how many ships of the line it has. Hover it for what it is doing."],
	["THE SEA", "port", "A red anchor: a port under blockade."],
	["THE SEA", "sea", "A sea crossing. Grey: an army can cross. Red: an enemy fleet has closed it. Amber: only a landing can cross. Gold: open for a short time."],
	["THE LAND", "land", "A province's colour is the nation that holds it. A gold border marks a capital."],
	["THE LAND", "flash", "A province that has just changed hands."],
	["THE LAND", "danger", "A province of yours with nothing strong enough to hold it, and an enemy you can see one march away. March a corps in, or have a corps there leave a garrison."],
	["ORDERS", "reach", "With a corps selected, each province shows how long he needs to get there: this turn, 1 turn, 2–3 turns, 4 or more. Dark = he cannot reach it."],
	["ORDERS", "arrow", "A standing order: the road a corps is marching. Red: he is pursuing. Blue: he is supporting. Click the line to change or cancel it."],
	["ORDERS", "trail", "The road a corps has just walked — yours when you send it, the enemy's after you end the turn."],
	# Row IC, directives: the war goal's gold ring.
	["ORDERS", "goal", "A gold ring: the goal you set for a war — a place to take, or an enemy army to beat. Set it from a province's panel, or type “the war goal is Vienna”."],
]

var _columns_box: HBoxContainer = null
var _columns := 0


func _init() -> void:
	name = "MapKey"
	visible = false
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_theme_stylebox_override("panel", Utils.leather_frame(Utils.FRAME_HUD, 14.0))


func _ready() -> void:
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 6)
	add_child(column)
	var header := HBoxContainer.new()
	column.add_child(header)
	var title := Label.new()
	title.text = TITLE
	title.theme_type_variation = &"DialogTitle"
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	var hint := Label.new()
	hint.text = CLOSE_HINT
	hint.theme_type_variation = &"Caption"
	hint.modulate = Color(1, 1, 1, 0.7)
	hint.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	header.add_child(hint)
	var close := Button.new()
	close.name = "MapKeyClose"
	close.text = "×"
	close.tooltip_text = "Close the map key"
	close.focus_mode = Control.FOCUS_NONE
	close.pressed.connect(close_key)
	header.add_child(close)
	_columns_box = HBoxContainer.new()
	_columns_box.add_theme_constant_override("separation", 22)
	column.add_child(_columns_box)
	_build_columns(3)


func is_open() -> bool:
	return visible


func open_key() -> void:
	if not visible:
		visible = true
		AudioManager.play("panel_open")
	fit()


func close_key() -> void:
	if visible:
		visible = false
		AudioManager.play("panel_close")


func toggle() -> void:
	if visible:
		close_key()
	else:
		open_key()


func fit(room_width: float = 0.0) -> void:
	"""As many columns as the room seats (three, two, one), each a whole
	section or two; then the panel's own minimum size (the owner seats it)."""
	var room: float = room_width
	if room <= 0.0:
		room = get_viewport_rect().size.x if is_inside_tree() else COLUMN_WIDTH * 3.0
	var wanted := clampi(int(floor((room - 40.0) / COLUMN_WIDTH)), 1, 3)
	if wanted != _columns and _columns_box != null:
		_build_columns(wanted)
	reset_size()


func columns_shown() -> int:
	return _columns


func _build_columns(count: int) -> void:
	"""A section is read top to bottom in one column."""
	_columns = count
	for old in _columns_box.get_children():
		_columns_box.remove_child(old)
		old.queue_free()
	for sections in COLUMNS[count]:
		var col := VBoxContainer.new()
		col.add_theme_constant_override("separation", 8)
		_columns_box.add_child(col)
		var last_section := ""
		for entry in ENTRIES:
			if not (str(entry[0]) in sections):
				continue
			col.add_child(_row(str(entry[1]), str(entry[2]), str(entry[0]) if str(entry[0]) != last_section else ""))
			last_section = str(entry[0])


func _row(kind: String, words: String, section: String) -> Control:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 2)
	if section != "":
		var head := Label.new()
		head.text = section
		head.theme_type_variation = &"Caption"
		head.add_theme_color_override("font_color", Utils.cv(Color.html("#" + Utils.COLOR_GOLD)))
		box.add_child(head)
	var line := HBoxContainer.new()
	line.add_theme_constant_override("separation", 10)
	box.add_child(line)
	var sample := MapKeySample.new()
	sample.kind = kind
	sample.custom_minimum_size = SAMPLE_SIZE
	sample.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	line.add_child(sample)
	var text := Label.new()
	text.text = words
	text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text.custom_minimum_size = Vector2(WORDS_WIDTH, 0)
	line.add_child(text)
	return box


# ── the samples: each mark as the map draws it ──────────────────────────────

class MapKeySample extends Control:
	const Plaque = preload("res://scripts/map_plaque.gd")
	const ConnectionLayer = preload("res://scenes/map_connection_layer.gd")
	const SAMPLE_NATION := Color(0.25, 0.41, 0.88)      # a blue coat
	const SEA_SHUT := Color(0.85, 0.25, 0.25, 0.9)
	const SEA_LANDING := Color(0.88, 0.55, 0.18, 0.92)
	const SEA_WINDOW := Color(0.95, 0.78, 0.2, 0.95)
	const ARROW_MARCH := Color(0.96, 0.84, 0.52, 0.95)
	const ARROW_PURSUE := Color(0.95, 0.52, 0.38, 0.95)
	const ARROW_SUPPORT := Color(0.60, 0.84, 1.0, 0.95)
	const REACH := [Color(1.0, 0.98, 0.84), Color(1.0, 0.90, 0.52), Color(0.98, 0.74, 0.34), Color(0.90, 0.58, 0.28)]
	const FLASH := Color(1.0, 0.86, 0.42, 1.0)
	const SHADOW := Color(0.08, 0.06, 0.04, 0.75)
	const PORT_RED := Color(0.85, 0.25, 0.25, 0.95)
	const DANGER := Color(0.93, 0.36, 0.28, 0.98)       # row IC: `map_order_layer.DANGER_COLOR`
	const GOAL := Color(0.96, 0.80, 0.36, 1.0)          # row IC, directives: `map_order_layer.GOAL_COLOR`
	const GOAL_SHADE := Color(0.08, 0.06, 0.04, 0.78)   # … and `GOAL_SHADOW`
	var kind := ""

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		match kind:
			"piece":
				if WarTablePiece.pieces_available():
					var piece := WarTablePiece.new()
					add_child(piece)
					piece.setup("infantry", "r", SAMPLE_NATION, 40.0)
					piece.position = Vector2(custom_minimum_size.x / 2.0, custom_minimum_size.y - 1.0)
			"name":
				_plate("NEY", Plaque.Kind.NAME, Vector2(8, 8), Vector2(0, 0))
			"fog":
				_plate("?", Plaque.Kind.FOG, Vector2(20, 5), Vector2(24, 24))
			"garrison":
				_plate("12k", Plaque.Kind.GARRISON, Vector2(12, 7), Vector2(0, 0))
			"sail":
				_plate("45", Plaque.Kind.SAIL, Vector2(18, 4), Vector2(28, 26))

	func _plate(text: String, plaque_kind: int, at: Vector2, fixed: Vector2) -> void:
		var label := Label.new()
		label.text = text
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		label.theme_type_variation = &"Caption"
		label.add_theme_color_override("font_color", Color(0.96, 0.93, 0.86))
		var style = Plaque.new()
		style.kind = plaque_kind
		style.band_color = SAMPLE_NATION
		if plaque_kind == Plaque.Kind.GARRISON:
			style.content_margin_left = 11.0
			style.content_margin_right = 6.0
		elif plaque_kind == Plaque.Kind.NAME:
			style.content_margin_left = 6.0
			style.content_margin_right = 6.0
			style.content_margin_bottom = 3.0
		label.add_theme_stylebox_override("normal", style)
		label.position = at
		if fixed != Vector2.ZERO:
			label.custom_minimum_size = fixed
			label.size = fixed
		add_child(label)

	func _dashes(from: Vector2, to: Vector2, color: Color, width: float = 2.5) -> void:
		draw_line(from, to, Color(SHADOW, 0.5), width + 2.0, true)
		draw_dashed_line(from, to, color, width, 6.0, true, true)

	func _head(from: Vector2, to: Vector2, color: Color) -> void:
		var dir := (to - from).normalized()
		var side := Vector2(-dir.y, dir.x)
		draw_colored_polygon(PackedVector2Array([to, to - dir * 9.0 + side * 5.0, to - dir * 9.0 - side * 5.0]), color)

	func _draw() -> void:
		var w := size.x
		var h := size.y
		match kind:
			"port":
				# the map's own drawing (`map_connection_layer.draw_anchor`)
				ConnectionLayer.draw_anchor(self, Vector2(w / 2.0, h / 2.0 + 1.0), 7.0, PORT_RED)
			"sea":
				var rows := [Utils.MAP_CONNECTION_GREY, SEA_SHUT, SEA_LANDING, SEA_WINDOW]
				for i in range(rows.size()):
					var y := 5.0 + float(i) * 8.0
					_dashes(Vector2(6, y), Vector2(w - 6, y), rows[i], 2.0)
			"land":
				var tile := Rect2(Vector2(14, 5), Vector2(w - 28, h - 10))
				draw_rect(tile, Color(SAMPLE_NATION, 0.75))
				draw_rect(tile, Color.html("#" + Utils.COLOR_GOLD), false, 3.0)
			"flash":
				var c2 := Vector2(w / 2.0, h / 2.0)
				draw_arc(c2, 12.0, 0.0, TAU, 28, SHADOW, 6.0, true)
				draw_arc(c2, 12.0, 0.0, TAU, 28, FLASH, 3.0, true)
			"danger":
				# the order layer's own mark (`map_order_layer._draw_dangers`)
				var c4 := Vector2(w / 2.0, h / 2.0 + 2.0)
				var half := 11.0
				var tri := PackedVector2Array([c4 + Vector2(0, -half), c4 + Vector2(-half, half * 0.8),
					c4 + Vector2(half, half * 0.8)])
				draw_colored_polygon(PackedVector2Array([tri[0] + Vector2(0, -3), tri[1] + Vector2(-3, 2), tri[2] + Vector2(3, 2)]), SHADOW)
				draw_colored_polygon(tri, DANGER)
				draw_line(c4 + Vector2(0, -5.0), c4 + Vector2(0, 2.5), Color(0.99, 0.95, 0.88), 2.4, true)
				draw_circle(c4 + Vector2(0, 6.0), 1.5, Color(0.99, 0.95, 0.88))
			"goal":
				# the order layer's own ring (`map_order_layer._draw_goals`)
				var c5 := Vector2(w / 2.0, h / 2.0)
				var ring_pts := PackedVector2Array()
				for s in range(41):
					var ang := TAU * float(s) / 40.0
					ring_pts.append(c5 + Vector2(cos(ang) * 18.0, sin(ang) * 11.0))
				draw_polyline(ring_pts, GOAL_SHADE, 5.5, true)
				draw_polyline(ring_pts, GOAL, 2.8, true)
			"reach":
				var side_px := 12.0
				for i in range(REACH.size()):
					var at := Vector2(4.0 + float(i) * (side_px + 3.0), (h - side_px) / 2.0)
					draw_rect(Rect2(at, Vector2(side_px, side_px)), REACH[i])
					draw_rect(Rect2(at, Vector2(side_px, side_px)), Color(SHADOW, 0.8), false, 1.0)
			"arrow":
				var rows2 := [ARROW_MARCH, ARROW_PURSUE, ARROW_SUPPORT]
				for i in range(rows2.size()):
					var y2 := 7.0 + float(i) * 10.0
					_dashes(Vector2(6, y2), Vector2(w - 16, y2), rows2[i], 2.0)
					_head(Vector2(w - 16, y2), Vector2(w - 6, y2), rows2[i])
			"trail":
				var a := Vector2(8, h - 8)
				var b := Vector2(w / 2.0, 9)
				var c3 := Vector2(w - 10, h / 2.0)
				var tint := SAMPLE_NATION.lightened(0.35)
				_dashes(a, b, tint, 3.0)
				_dashes(b, c3, tint, 3.0)
				draw_circle(a, 3.5, tint)
				_head(b, c3, tint)

extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - The Stack Picker (row PW, November 18, 2026)
# =============================================================================
# The first playtest: "its hard to click genral pieces". Three or more corps
# in one province stand as overlapping pieces 20 px wide under ONE label
# ("Napoleon · 3 more"), and a click on that label only ever picked the first
# man. A click on a stack's label now opens this small list beside the cursor
# - each of OUR corps there by name with his men and what he is doing - and a
# click on a row selects him (the host's own `_select_marshal`).
#
# It closes on a pick, on Esc and on a click anywhere else. It judges no rule
# and sends nothing: one signal, `picked(roster_key)`. Loaded by path (no
# class_name: the parse harness's class cache stays as it is).
# =============================================================================

signal picked(marshal_key: String)

const ROW_HEIGHT := 40.0
const MIN_WIDTH := 260.0
const EDGE := 8.0

var _catch: Control = null
var _panel: PanelContainer = null
var _rows: VBoxContainer = null
var _title: Label = null
var _keys: Array = []
var _opened_frame := -1


func _init() -> void:
	name = "StackPicker"
	layer = 27          # above the province panel (26), under the modals (100+)
	visible = false


func _ready() -> void:
	# The click-away: a clear full-view control under the list.
	_catch = Control.new()
	_catch.name = "ClickAway"
	_catch.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_catch.mouse_filter = Control.MOUSE_FILTER_STOP
	_catch.gui_input.connect(_on_catch_input)
	add_child(_catch)
	_panel = PanelContainer.new()
	_panel.name = "List"
	_panel.add_theme_stylebox_override("panel",
			Utils.gilt_frame(Utils.UI_POPUP_BG, Utils.UI_GOLD, Utils.FRAME_HUD, 8.0))
	add_child(_panel)
	var body := VBoxContainer.new()
	body.add_theme_constant_override("separation", 4)
	_panel.add_child(body)
	_title = Label.new()
	_title.theme_type_variation = &"Caption"
	_title.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	body.add_child(_title)
	_rows = VBoxContainer.new()
	_rows.add_theme_constant_override("separation", 3)
	body.add_child(_rows)


func is_open() -> bool:
	return visible


func open_list(place: String, rows: Array, at: Vector2) -> void:
	"""`rows`: [{"key", "name", "men", "doing"}] - our corps in `place`, in the
	board's order. `at`: where the label was clicked (logical screen px)."""
	if _panel == null:
		return
	for child in _rows.get_children():
		child.queue_free()
	_keys = []
	_title.text = "Which corps at %s?" % place if place != "" else "Which corps?"
	for row in rows:
		if not (row is Dictionary):
			continue
		var key := str(row.get("key", ""))
		if key == "":
			continue
		_keys.append(key)
		var btn := Button.new()
		btn.name = "Pick_" + key
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.custom_minimum_size = Vector2(MIN_WIDTH, ROW_HEIGHT)
		btn.focus_mode = Control.FOCUS_NONE     # the command line keeps the keyboard
		var words := str(row.get("name", key)) + "  ·  " + Utils.format_number(int(row.get("men", 0))) + " men"
		var doing := str(row.get("doing", ""))
		if doing != "":
			words += "  ·  " + doing
		btn.text = words
		btn.pressed.connect(_on_row_pressed.bind(key))
		_rows.add_child(btn)
	if _keys.is_empty():
		close_list()
		return
	visible = true
	_opened_frame = Engine.get_process_frames()
	_place_beside.call_deferred(at)


func close_list() -> void:
	visible = false
	_keys = []


func _place_beside(at: Vector2) -> void:
	"""Beside the click, kept whole on the view."""
	if _panel == null or not visible:
		return
	_panel.reset_size()
	var view := get_viewport().get_visible_rect().size
	var want := _panel.get_combined_minimum_size()
	var pos := at + Vector2(14.0, -10.0)
	pos.x = clampf(pos.x, EDGE, maxf(EDGE, view.x - want.x - EDGE))
	pos.y = clampf(pos.y, EDGE, maxf(EDGE, view.y - want.y - EDGE))
	_panel.position = pos
	_panel.size = want


func _on_row_pressed(key: String) -> void:
	close_list()
	picked.emit(key)


func _on_catch_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and (event as InputEventMouseButton).pressed:
		# Never the press that opened it (it reaches the GUI pass in the same
		# frame, after the map's own `_input` raised the list).
		if Engine.get_process_frames() == _opened_frame:
			return
		close_list()
		get_viewport().set_input_as_handled()


func _unhandled_key_input(event: InputEvent) -> void:
	if visible and event is InputEventKey and (event as InputEventKey).pressed \
			and (event as InputEventKey).keycode == KEY_ESCAPE:
		close_list()
		get_viewport().set_input_as_handled()

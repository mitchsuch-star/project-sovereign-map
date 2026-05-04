extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - War Status Panel (N4a: Layer 1 HUD)
# =============================================================================
# Compact always-visible panel anchored bottom-right. Shows active wars,
# coalition grouping, and armistice cards with tug-of-war score meters.
# CanvasLayer 25. User-resizable via drag handles.
# Clicks emit card_clicked for main.gd to open the detail popup.
# =============================================================================

signal card_clicked(nation: String, status: String)
signal coalition_header_clicked()

@onready var panel_container = $PanelContainer
@onready var scroll_container = $PanelContainer/ScrollContainer
@onready var vbox = $PanelContainer/ScrollContainer/VBoxContainer
@onready var header_label = $PanelContainer/ScrollContainer/VBoxContainer/HeaderLabel

# Nation tints — single source is Utils.NATION_COLORS (§3.3).
const COLOR_GREEN = Color(0.29, 0.67, 0.29)
const COLOR_RED = Color(0.67, 0.27, 0.27)
const COLOR_WHITE = Color(0.75, 0.75, 0.78)
const COLOR_GOLD = Color(0.85, 0.7, 0.3)
const COLOR_DIMMED = Color(0.5, 0.5, 0.5)
const COLOR_BAR_BG = Color(0.15, 0.15, 0.2, 0.8)
const COLOR_BAR_CENTER = Color(0.35, 0.35, 0.4, 0.6)

# Resize constraints
const MIN_WIDTH = 150
const MAX_WIDTH = 500
const MIN_HEIGHT = 60
const MAX_HEIGHT_RATIO = 0.45  # Max 45% of screen height

# Drag state
var _dragging_edge: String = ""  # "left", "top", "topleft", ""
var _drag_start_mouse: Vector2 = Vector2.ZERO
var _drag_start_rect: Rect2 = Rect2()
const DRAG_MARGIN = 6  # Pixels from edge to trigger resize cursor


func _ready():
	hide()


func _input(event):
	if not visible:
		return
	if event is InputEventMouseButton:
		if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			var edge = _get_resize_edge(event.position)
			if edge != "":
				_dragging_edge = edge
				_drag_start_mouse = event.position
				_drag_start_rect = Rect2(
					Vector2(panel_container.offset_left, panel_container.offset_top),
					Vector2(panel_container.offset_right - panel_container.offset_left,
							panel_container.offset_bottom - panel_container.offset_top)
				)
				get_viewport().set_input_as_handled()
		elif not event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			if _dragging_edge != "":
				_dragging_edge = ""
				get_viewport().set_input_as_handled()
	elif event is InputEventMouseMotion:
		if _dragging_edge != "":
			_apply_resize(event.position)
			get_viewport().set_input_as_handled()


func _get_resize_edge(mouse_pos: Vector2) -> String:
	"""Check if mouse is near a resizable edge of the panel."""
	var screen_size = get_viewport().get_visible_rect().size
	# Panel anchored bottom-right: offsets are negative from bottom-right corner
	var panel_left = screen_size.x + panel_container.offset_left
	var panel_top = screen_size.y + panel_container.offset_top
	var panel_right = screen_size.x + panel_container.offset_right
	var panel_bottom = screen_size.y + panel_container.offset_bottom

	var near_left = abs(mouse_pos.x - panel_left) < DRAG_MARGIN
	var near_top = abs(mouse_pos.y - panel_top) < DRAG_MARGIN
	var in_x = mouse_pos.x >= panel_left - DRAG_MARGIN and mouse_pos.x <= panel_right
	var in_y = mouse_pos.y >= panel_top - DRAG_MARGIN and mouse_pos.y <= panel_bottom

	if near_left and near_top:
		return "topleft"
	if near_left and in_y:
		return "left"
	if near_top and in_x:
		return "top"
	return ""


func _apply_resize(mouse_pos: Vector2):
	"""Apply resize drag delta to panel offsets."""
	var delta = mouse_pos - _drag_start_mouse
	var screen_size = get_viewport().get_visible_rect().size
	var max_h = int(screen_size.y * MAX_HEIGHT_RATIO)

	if _dragging_edge == "left" or _dragging_edge == "topleft":
		var new_left = _drag_start_rect.position.x + delta.x
		var width = panel_container.offset_right - new_left
		width = clamp(width, MIN_WIDTH, MAX_WIDTH)
		panel_container.offset_left = panel_container.offset_right - width

	if _dragging_edge == "top" or _dragging_edge == "topleft":
		var new_top = _drag_start_rect.position.y + delta.y
		var height = panel_container.offset_bottom - new_top
		height = clamp(height, MIN_HEIGHT, max_h)
		panel_container.offset_top = panel_container.offset_bottom - height


func update_wars(data: Dictionary) -> void:
	"""Rebuild the entire panel from active_wars data."""
	# Clear existing cards (keep header)
	for child in vbox.get_children():
		if child != header_label:
			vbox.remove_child(child)
			child.queue_free()

	var wars = data.get("wars", [])
	if wars.is_empty():
		hide()
		return

	header_label.text = "ACTIVE WARS"

	var coalition_data = data.get("coalition", null)
	var has_coalition = coalition_data != null

	# ── Coalition group ──
	if has_coalition:
		var coalition_name = str(coalition_data.get("name", "Coalition"))
		_add_coalition_header(coalition_name)
		for w in wars:
			if w.get("in_coalition", false) and w.get("status", "") == "war":
				_add_war_entry(w, true)

	# ── Bilateral war cards (non-coalition) ──
	for w in wars:
		if w.get("status", "") == "war" and not w.get("in_coalition", false):
			_add_war_entry(w, false)

	# ── Armistice cards ──
	for w in wars:
		if w.get("status", "") == "armistice":
			_add_armistice_card(w)

	show()


func _add_coalition_header(coalition_name: String):
	var btn = Button.new()
	btn.text = " " + coalition_name.to_upper()
	btn.flat = true
	btn.custom_minimum_size = Vector2(0, 18)
	btn.add_theme_font_size_override("font_size", 10)
	btn.add_theme_color_override("font_color", COLOR_GOLD)
	btn.pressed.connect(func(): coalition_header_clicked.emit())
	vbox.add_child(btn)


func _add_war_entry(war_data: Dictionary, is_coalition_member: bool):
	"""Add a compact war entry: entire row is clickable."""
	var opponent = str(war_data.get("opponent", "?"))
	var score = int(float(war_data.get("war_score", 0)))
	var duration = int(float(war_data.get("duration", 0)))

	# Whole row is a flat Button for full clickability
	var row_btn = Button.new()
	row_btn.flat = true
	row_btn.custom_minimum_size = Vector2(0, 18)
	row_btn.pressed.connect(func(): card_clicked.emit(opponent, "war"))
	row_btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	row_btn.tooltip_text = _build_war_tooltip(war_data)

	# Inner HBox for layout — passes mouse through to the button
	var row = HBoxContainer.new()
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.add_theme_constant_override("separation", 4)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Nation name label
	var name_label = Label.new()
	var indent = "  " if is_coalition_member else ""
	name_label.text = indent + opponent
	name_label.custom_minimum_size = Vector2(60, 0)
	name_label.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	name_label.add_theme_font_size_override("font_size", 10)
	name_label.add_theme_color_override("font_color", _get_score_color(score))
	name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(name_label)

	# Tug-of-war bar
	var bar = _create_tug_of_war_bar(score, opponent, 80, 6)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(bar)

	# Turn counter
	var turn_label = Label.new()
	turn_label.text = "T:" + str(duration)
	turn_label.add_theme_font_size_override("font_size", 9)
	turn_label.add_theme_color_override("font_color", COLOR_DIMMED)
	turn_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(turn_label)

	row_btn.add_child(row)
	vbox.add_child(row_btn)


func _build_war_tooltip(war_data: Dictionary) -> String:
	var lines = []
	var tier = str(war_data.get("settlement_tier_display", ""))
	if tier:
		lines.append("Settlement: " + tier)
	var objective = war_data.get("objective", null)
	if objective != null and objective is Dictionary:
		var targets = objective.get("target_regions", [])
		var target_text = ", ".join(targets) if targets is Array and not targets.is_empty() else "target pending"
		lines.append("Objective: " + str(objective.get("type_display", "Objective")) + " - " + target_text)
		lines.append("Ticking: +" + str(int(float(objective.get("accumulated_ticking", 0)))))
	var enemy_objective = war_data.get("enemy_objective", null)
	if enemy_objective != null and enemy_objective is Dictionary:
		lines.append("Enemy: " + str(enemy_objective.get("type_display", "Objective")))
	# WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §16.2 — top-five
	# contribution share rows + overflow indicator. Rows come from
	# `build_active_wars` which already enforces the cap server-side.
	var contribution = war_data.get("contribution_share", [])
	if contribution is Array and contribution.size() > 0:
		lines.append("---")
		lines.append("Standing (top 5):")
		for row in contribution:
			if not row is Dictionary:
				continue
			var nation = str(row.get("nation", "?"))
			var standing = str(row.get("standing", "no_standing"))
			var material = float(row.get("material_share", 0.0)) * 100.0
			var leader_marker = "*" if row.get("is_leader", false) else " "
			lines.append("  " + leader_marker + " " + nation + " — " + standing + " (" + str(int(round(material))) + "%)")
		var overflow = int(war_data.get("contribution_overflow_count", 0))
		if overflow > 0:
			lines.append("  +" + str(overflow) + " more participant(s)")
	return "\n".join(lines)


func _add_armistice_card(war_data: Dictionary):
	var opponent = str(war_data.get("opponent", "?"))
	var remaining = int(float(war_data.get("armistice_remaining", 0)))

	var btn = Button.new()
	btn.text = opponent + "  " + str(remaining) + "t"
	btn.flat = true
	btn.custom_minimum_size = Vector2(0, 16)
	btn.add_theme_font_size_override("font_size", 9)
	btn.add_theme_color_override("font_color", COLOR_DIMMED)
	btn.pressed.connect(func(): card_clicked.emit(opponent, "armistice"))
	vbox.add_child(btn)


func _create_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int) -> Control:
	"""Create a two-tone tug-of-war bar. Blue=France (right), Red=enemy (left).
	Center = 0. Score > 0 means France winning (blue fills right of center).
	Score < 0 means enemy winning (red fills left of center).
	All children use MOUSE_FILTER_IGNORE so clicks pass to parent."""
	var container = Control.new()
	container.custom_minimum_size = Vector2(bar_width, bar_height)
	container.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Background
	var bg = ColorRect.new()
	bg.color = COLOR_BAR_BG
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	container.add_child(bg)

	# Center line (subtle)
	var center_line = ColorRect.new()
	center_line.color = COLOR_BAR_CENTER
	center_line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	center_line.position = Vector2(bar_width / 2 - 1, 0)
	center_line.size = Vector2(1, bar_height)
	container.add_child(center_line)

	# Score fill
	var normalized = clamp(score, -100, 100)
	var enemy_color = Utils.NATION_COLORS.get(opponent, Utils.COLOR_ENEMY_DEFAULT)
	var half_w = bar_width / 2.0

	if normalized > 0:
		# France winning — blue fills from center rightward
		var fill_width = int((normalized / 100.0) * half_w)
		if fill_width > 0:
			var fill = ColorRect.new()
			fill.color = Utils.NATION_COLORS["France"]
			fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
			fill.position = Vector2(int(half_w), 0)
			fill.size = Vector2(fill_width, bar_height)
			container.add_child(fill)
	elif normalized < 0:
		# Enemy winning — red fills from center leftward
		var fill_width = int((abs(normalized) / 100.0) * half_w)
		if fill_width > 0:
			var fill = ColorRect.new()
			fill.color = enemy_color
			fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
			fill.position = Vector2(int(half_w) - fill_width, 0)
			fill.size = Vector2(fill_width, bar_height)
			container.add_child(fill)

	# Score label (small, centered on bar)
	var score_label = Label.new()
	var score_sign = "+" if score > 0 else ""
	score_label.text = score_sign + str(score)
	score_label.add_theme_font_size_override("font_size", 8)
	score_label.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))
	score_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	score_label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	container.add_child(score_label)

	return container


func _get_score_color(score: int) -> Color:
	if score > 0:
		return COLOR_GREEN
	elif score < 0:
		return COLOR_RED
	return COLOR_WHITE

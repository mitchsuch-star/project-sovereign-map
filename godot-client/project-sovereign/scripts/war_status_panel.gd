extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - War Status Panel (N4a: Layer 1 HUD)
# =============================================================================
# Compact always-visible panel anchored bottom-right. Shows active wars,
# coalition grouping, and armistice cards with tug-of-war score meters.
# CanvasLayer 25. User-resizable via drag handles.
# Clicks emit card_clicked for main.gd to open the detail popup.
# =============================================================================

signal card_clicked(nation: String, status: String, war_instance_id: String)
signal coalition_header_clicked()

@onready var panel_container = $PanelContainer
@onready var scroll_container = $PanelContainer/ScrollContainer
@onready var vbox = $PanelContainer/ScrollContainer/VBoxContainer
@onready var header_label = $PanelContainer/ScrollContainer/VBoxContainer/HeaderLabel

# Nation tints — single source is Utils.NATION_COLORS (§3.3).
# UI-2 Part 2: the score triad + bar track are shared with war_detail_popup —
# they now alias the centralized Utils palette (single source for a re-skin).
const COLOR_GREEN = Utils.UI_SCORE_POSITIVE
const COLOR_RED = Utils.UI_SCORE_NEGATIVE
const COLOR_WHITE = Utils.UI_SCORE_NEUTRAL
const COLOR_GOLD = Color(0.85, 0.7, 0.3)
const COLOR_DIMMED = Color(0.5, 0.5, 0.5)
const COLOR_BAR_BG = Utils.UI_BAR_BG
const COLOR_BAR_CENTER = Color(0.35, 0.35, 0.4, 0.6)
# War-score bar frame (CC0 Kenney RPG track): 9px 3-slice caps; a cool-navy
# modulate tints the dark track to match the UI without lightening (modulate
# multiplies).
const BAR_FRAME_CAP = 9
const COLOR_BAR_FRAME_TINT = Color(0.72, 0.78, 1.0)

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
	_add_panel_grain()


func _add_panel_grain() -> void:
	# Subtle dark-leather grain behind the panel content for a richer, in-world
	# feel (existing CC0 leather asset, dark-navy-tinted + low alpha so it reads
	# as texture, not a brown wash). Behind the ScrollContainer; ignores mouse.
	var tex = load("res://assets/textures/fabric_leather_01_diff_1k.jpg")
	if tex == null:
		return
	var grain = TextureRect.new()
	grain.texture = tex
	grain.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	# CRITICAL: without EXPAND_IGNORE_SIZE the TextureRect reports the 1024x1024
	# texture as its minimum size, and PanelContainer (which sizes to its
	# children's min) balloons the whole panel to fill the screen.
	grain.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	grain.custom_minimum_size = Vector2.ZERO
	grain.modulate = Color(0.30, 0.32, 0.44, 0.32)
	grain.mouse_filter = Control.MOUSE_FILTER_IGNORE
	grain.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	panel_container.add_child(grain)
	panel_container.move_child(grain, 0)


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
	_fit_panel_to_content()


func _fit_panel_to_content() -> void:
	# Shrink-wrap the panel height to its content (up to MAX_HEIGHT_RATIO of the
	# screen, then the ScrollContainer scrolls). A fixed .tscn height left a big
	# dead gap below a single war entry. Anchored bottom-right, so we move the TOP
	# edge; width stays user-draggable. One frame lets the containers lay out.
	await get_tree().process_frame
	if not visible or not is_instance_valid(panel_container):
		return
	var content_h: float = vbox.get_combined_minimum_size().y
	var screen_size: Vector2 = get_viewport().get_visible_rect().size
	var max_h := float(int(screen_size.y * MAX_HEIGHT_RATIO))
	# +8 covers the panel stylebox content margins (2 top + 4 bottom) + slack.
	var target_h: float = clampf(content_h + 8.0, MIN_HEIGHT, max_h)
	panel_container.offset_top = panel_container.offset_bottom - target_h


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
	"""Add a two-line war entry: name + turn on top, a full-width tug-of-war bar
	below. Two lines guarantee the bar always gets the panel's full width — a
	long collapsed coalition name (e.g. "Britain + Austria + Russia") no longer
	crushes it to nothing. Entire card is clickable."""
	var opponent = str(war_data.get("opponent", "?"))
	var opponent_display = Utils.humanize_nation_keys_in_text(str(war_data.get("opponent_display", Utils.display_nation_name(opponent))))
	var score = int(float(war_data.get("war_score", 0)))
	var duration = int(float(war_data.get("duration", 0)))

	# Whole card is a flat Button for full clickability
	var row_btn = Button.new()
	row_btn.flat = true
	row_btn.custom_minimum_size = Vector2(0, 36)
	row_btn.pressed.connect(func(): card_clicked.emit(opponent, "war", str(war_data.get("war_instance_id", ""))))
	row_btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	row_btn.tooltip_text = _build_war_tooltip(war_data)

	# Inner VBox: [name row] over [bar]. Passes mouse through to the button.
	var col = VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.add_theme_constant_override("separation", 1)
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# ── Line 1: name (clips instead of pushing) + turn counter ──
	var name_row = HBoxContainer.new()
	name_row.add_theme_constant_override("separation", 4)
	name_row.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# UI-6: opponent heraldry ahead of the name (untinted colored art)
	var flag_path = Utils.nation_flag_path(opponent)
	if flag_path != "":
		var flag_rect = TextureRect.new()
		flag_rect.texture = load(flag_path)
		flag_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		flag_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		flag_rect.custom_minimum_size = Vector2(16, 11)
		flag_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		name_row.add_child(flag_rect)

	var name_label = Label.new()
	var indent = "  " if is_coalition_member else ""
	name_label.text = indent + opponent_display
	name_label.clip_text = true
	name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	name_label.add_theme_font_size_override("font_size", 10)
	name_label.add_theme_color_override("font_color", Color(0.85, 0.85, 0.88))
	name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	name_row.add_child(name_label)

	# Score number lives here (not on the bar) so it never fights the centre gem.
	var score_label = Label.new()
	score_label.text = ("+" if score > 0 else "") + str(score)
	score_label.add_theme_font_size_override("font_size", 10)
	score_label.add_theme_color_override("font_color", _get_score_color(score))
	score_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	name_row.add_child(score_label)

	var turn_label = Label.new()
	turn_label.text = "T:" + str(duration)
	turn_label.add_theme_font_size_override("font_size", 9)
	turn_label.add_theme_color_override("font_color", COLOR_DIMMED)
	turn_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	name_row.add_child(turn_label)
	col.add_child(name_row)

	# ── Line 2: full-width tug-of-war bar ──
	var bar = _create_tug_of_war_bar(score, opponent, 80, 16)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_child(bar)

	row_btn.add_child(col)
	vbox.add_child(row_btn)


func _build_war_tooltip(war_data: Dictionary) -> String:
	var lines = []
	if bool(war_data.get("is_multi_participant_war", false)):
		lines.append("Shared war: " + Utils.humanize_nation_keys_in_text(str(war_data.get("opponent_display", Utils.display_nation_name(str(war_data.get("opponent", "?")))))))
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
			var standing = str(row.get("standing_display", "Standing pending"))
			var material = float(row.get("material_share", 0.0)) * 100.0
			var leader_marker = "*" if row.get("is_leader", false) else " "
			lines.append("  " + leader_marker + " " + Utils.display_nation_name(nation) + " — " + standing + " (" + str(int(round(material))) + "%)")
		var overflow = int(war_data.get("contribution_overflow_count", 0))
		if overflow > 0:
			lines.append("  +" + str(overflow) + " more participant(s)")
	else:
		var status_display = str(war_data.get("standing_status_display", ""))
		if status_display != "":
			lines.append("---")
			lines.append("Standing: " + status_display)
	return "\n".join(lines)


func _add_armistice_card(war_data: Dictionary):
	var opponent = str(war_data.get("opponent", "?"))
	var opponent_display = Utils.display_nation_name(opponent)
	var remaining = int(float(war_data.get("armistice_remaining", 0)))

	var btn = Button.new()
	btn.text = opponent_display + "  " + str(remaining) + "t"
	btn.flat = true
	btn.custom_minimum_size = Vector2(0, 16)
	btn.add_theme_font_size_override("font_size", 9)
	btn.add_theme_color_override("font_color", COLOR_DIMMED)
	# UI-6: opponent heraldry on the truce row too
	Utils.apply_flag_icon(btn, opponent)
	# G4F-17: the HUD card whispers the expiry fork — tooltip names where
	# the truce is heading (peace vs collapse) without growing the card.
	var projected = str(war_data.get("armistice_projected_outcome", ""))
	if projected == "peace":
		btn.tooltip_text = "Armistice with %s — %d turns left, on course for peace." % [opponent_display, remaining]
	elif projected == "war":
		btn.tooltip_text = "Armistice with %s — %d turns left, on course to collapse back to war unless relations heal." % [opponent_display, remaining]
	btn.pressed.connect(func(): card_clicked.emit(opponent, "armistice", str(war_data.get("war_instance_id", ""))))
	vbox.add_child(btn)


func _create_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int) -> Control:
	"""Premium tug-of-war gauge: a gold-rimmed recessed track, a glossy fill
	tinted to the leader's nation (France blue right / enemy left), and a gold
	centre gem. The SCORE NUMBER is shown on the name line, not on the bar, so
	it never fights the gem. All children pass the mouse to the parent button."""
	return _build_tug_of_war_bar(score, opponent, bar_width, bar_height)


# Shared premium tug-of-war builder (HUD + detail popup use the same textures,
# assets/ui/bars/warbar_*.png — original gold-and-navy chrome). load() (not
# preload) so a missing texture degrades gracefully instead of a parse failure.
static func _build_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int) -> Control:
	var container = Control.new()
	container.custom_minimum_size = Vector2(bar_width, bar_height)
	container.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Gold-rimmed recessed track (horizontal 3-slice: rounded L/R caps).
	var track = NinePatchRect.new()
	track.texture = load("res://assets/ui/bars/warbar_track.png")
	track.patch_margin_left = 14
	track.patch_margin_right = 14
	track.mouse_filter = Control.MOUSE_FILTER_IGNORE
	track.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	container.add_child(track)

	# Glossy fill from centre, tinted to the leader's nation via modulate (the
	# fill texture is grayscale, so modulate keeps the gloss).
	var normalized = clamp(score, -100, 100)
	if normalized != 0:
		var fill = TextureRect.new()
		fill.texture = load("res://assets/ui/bars/warbar_fill.png")
		fill.stretch_mode = TextureRect.STRETCH_SCALE
		fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
		if normalized > 0:
			fill.modulate = Utils.NATION_COLORS["France"]
			_anchor_bar_child(fill, 0.5, 0.5 + (normalized / 100.0) * 0.5, 0.0, 0.0)
		else:
			fill.modulate = Utils.NATION_COLORS.get(opponent, Utils.COLOR_ENEMY_DEFAULT)
			_anchor_bar_child(fill, 0.5 - (abs(normalized) / 100.0) * 0.5, 0.5, 0.0, 0.0)
		fill.offset_top = 3.0
		fill.offset_bottom = -3.0
		container.add_child(fill)

	# Gold centre gem (the balanced-point marker; reads even at an even score).
	var gem = TextureRect.new()
	gem.texture = load("res://assets/ui/bars/warbar_gem.png")
	gem.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	gem.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var gem_size := float(bar_height) + 4.0
	gem.anchor_left = 0.5
	gem.anchor_right = 0.5
	gem.anchor_top = 0.5
	gem.anchor_bottom = 0.5
	gem.offset_left = -gem_size / 2.0
	gem.offset_right = gem_size / 2.0
	gem.offset_top = -gem_size / 2.0
	gem.offset_bottom = gem_size / 2.0
	container.add_child(gem)

	return container


static func _anchor_bar_child(node: Control, a_left: float, a_right: float, o_left: float, o_right: float) -> void:
	# Anchor a tug-of-war bar child horizontally to fractions of the container's
	# ACTUAL width (full height), so it resizes with a SIZE_EXPAND_FILL bar.
	node.anchor_left = a_left
	node.anchor_right = a_right
	node.anchor_top = 0.0
	node.anchor_bottom = 1.0
	node.offset_left = o_left
	node.offset_right = o_right
	node.offset_top = 0.0
	node.offset_bottom = 0.0


func _get_score_color(score: int) -> Color:
	if score > 0:
		return COLOR_GREEN
	elif score < 0:
		return COLOR_RED
	return COLOR_WHITE

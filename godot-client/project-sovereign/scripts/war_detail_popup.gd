extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - War Detail Popup (N4b: Layer 2)
# =============================================================================
# Lightweight popup showing war details, coalition overview, or armistice info.
# CanvasLayer 30. Opened from war_status_panel card clicks.
# Includes tug-of-war score meter for visual war score display.
# Emits negotiate_clicked / target_clicked for wizard handoff (Layer 3).
# =============================================================================

signal negotiate_clicked(nation: String)
signal target_clicked(nation: String)
signal war_ended(message: String)

@onready var background_overlay = $BackgroundOverlay
@onready var header_label = $PanelContainer/VBoxContainer/HeaderRow/HeaderLabel
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var score_bar_container = $PanelContainer/VBoxContainer/ScoreBarContainer
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var button_row = $PanelContainer/VBoxContainer/ButtonRow

var _current_nation: String = ""
var _current_mode: String = ""  # "war", "coalition", "armistice"

# Colors
const COLOR_GREEN = "#4a4"
const COLOR_RED = "#a44"
const COLOR_WHITE = "#c0c0c8"
const COLOR_GOLD = "#d9c08c"
const COLOR_AMBER = "#e0a040"
const COLOR_HEADER = "#B8860B"
const COLOR_DIMMED = "#808080"
const COLOR_INFO = "#a0a0a8"

# Bar colors
const COLOR_FRANCE = Color(0.255, 0.412, 0.882)
const COLOR_ENEMY_DEFAULT = Color(0.7, 0.2, 0.2)
const COLOR_BAR_BG = Color(0.15, 0.15, 0.2, 0.8)
const COLOR_BAR_CENTER = Color(0.4, 0.4, 0.45, 0.6)

const NATION_COLORS = {
	"France": Color(0.255, 0.412, 0.882),
	"Britain": Color(0.863, 0.078, 0.235),
	"Prussia": Color(0.2, 0.2, 0.2),
	"Austria": Color(1.0, 0.843, 0.0),
	"Saxony": Color(0.4, 0.6, 0.3),
}


func _ready():
	hide()
	close_button.pressed.connect(_close_popup)
	background_overlay.gui_input.connect(_on_overlay_input)


func _input(event):
	if visible and event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		_close_popup()
		get_viewport().set_input_as_handled()


func _close_popup():
	hide()


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		_close_popup()


func show_war(war_data: Dictionary, _coalition_data) -> void:
	"""Show bilateral war detail (N4b)."""
	_current_nation = str(war_data.get("opponent", ""))
	_current_mode = "war"
	header_label.text = "WAR WITH " + _current_nation.to_upper()
	_clear_score_bars()
	_add_tug_of_war_bar(
		int(float(war_data.get("war_score", 0))),
		_current_nation, 280, 16
	)
	_render_war_detail(war_data)
	_clear_buttons()
	_add_negotiate_button(_current_nation)
	show()


func show_coalition(coalition_data: Dictionary, wars: Array) -> void:
	"""Show coalition overview detail (N4b coalition variant)."""
	_current_nation = str(coalition_data.get("leader", ""))
	_current_mode = "coalition"
	header_label.text = str(coalition_data.get("name", "COALITION")).to_upper()
	_clear_score_bars()
	# Add a tug-of-war bar per coalition member
	for w in wars:
		if w.get("in_coalition", false):
			var opp = str(w.get("opponent", "?"))
			var score = int(float(w.get("war_score", 0)))
			_add_labeled_tug_of_war_bar(opp, score, 280, 12)
	_render_coalition_detail(coalition_data, wars)
	_clear_buttons()
	# Add Target buttons for non-leader coalition members
	for w in wars:
		if w.get("in_coalition", false) and not w.get("is_coalition_leader", false):
			_add_target_button(str(w.get("opponent", "")))
	show()


func show_armistice(war_data: Dictionary) -> void:
	"""Show armistice detail (N4b armistice variant)."""
	_current_nation = str(war_data.get("opponent", ""))
	_current_mode = "armistice"
	header_label.text = "ARMISTICE WITH " + _current_nation.to_upper()
	_clear_score_bars()
	_render_armistice_detail(war_data)
	_clear_buttons()
	_add_diplomatic_options_button(_current_nation)
	show()


func refresh_if_open(active_wars_data: Dictionary) -> void:
	"""Refresh data in-place if popup is open (N4d: don't close mid-read)."""
	if not visible:
		return

	var wars = active_wars_data.get("wars", [])
	var coalition_data = active_wars_data.get("coalition", null)

	if _current_mode == "coalition" and coalition_data != null:
		show_coalition(coalition_data, wars)
		return

	# Find the war data for current nation
	var found = false
	for w in wars:
		if str(w.get("opponent", "")) == _current_nation:
			found = true
			if _current_mode == "war" and str(w.get("status", "")) == "war":
				show_war(w, coalition_data)
			elif _current_mode == "armistice" and str(w.get("status", "")) == "armistice":
				show_armistice(w)
			elif str(w.get("status", "")) == "armistice":
				# War ended, now armistice
				show_armistice(w)
			break

	if not found:
		# War ended entirely — notify before closing (Fix 10)
		war_ended.emit("The war with " + _current_nation + " has ended.")
		_close_popup()


# ── SCORE BAR ──

func _clear_score_bars():
	for child in score_bar_container.get_children():
		child.queue_free()


func _add_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int):
	"""Add a large tug-of-war bar to the score bar container."""
	var bar = _create_tug_of_war_bar(score, opponent, bar_width, bar_height, 11)
	score_bar_container.add_child(bar)


func _add_labeled_tug_of_war_bar(opponent: String, score: int, bar_width: int, bar_height: int):
	"""Add a labeled tug-of-war bar (nation name + bar) for coalition view."""
	var row = HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)

	var lbl = Label.new()
	lbl.text = opponent
	lbl.custom_minimum_size = Vector2(60, 0)
	lbl.add_theme_font_size_override("font_size", 10)
	var score_color_val = Color(0.29, 0.67, 0.29) if score > 0 else (Color(0.67, 0.27, 0.27) if score < 0 else Color(0.75, 0.75, 0.78))
	lbl.add_theme_color_override("font_color", score_color_val)
	row.add_child(lbl)

	var bar = _create_tug_of_war_bar(score, opponent, bar_width, bar_height, 9)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(bar)

	score_bar_container.add_child(row)


func _create_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int, font_size: int) -> Control:
	"""Create a two-tone tug-of-war bar. Blue=France (right), Red=enemy (left).
	Center = 0. Score > 0 means France winning (blue fills right of center).
	Score < 0 means enemy winning (red fills left of center)."""
	var container = Control.new()
	container.custom_minimum_size = Vector2(bar_width, bar_height)

	# Background
	var bg = ColorRect.new()
	bg.color = COLOR_BAR_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	container.add_child(bg)

	# Center line
	var center_line = ColorRect.new()
	center_line.color = COLOR_BAR_CENTER
	center_line.position = Vector2(bar_width / 2 - 1, 0)
	center_line.size = Vector2(1, bar_height)
	container.add_child(center_line)

	# Score fill
	var normalized = clamp(score, -100, 100)
	var enemy_color = NATION_COLORS.get(opponent, COLOR_ENEMY_DEFAULT)
	var half_w = bar_width / 2.0

	if normalized > 0:
		var fill_width = int((normalized / 100.0) * half_w)
		if fill_width > 0:
			var fill = ColorRect.new()
			fill.color = COLOR_FRANCE
			fill.position = Vector2(int(half_w), 0)
			fill.size = Vector2(fill_width, bar_height)
			container.add_child(fill)
	elif normalized < 0:
		var fill_width = int((abs(normalized) / 100.0) * half_w)
		if fill_width > 0:
			var fill = ColorRect.new()
			fill.color = enemy_color
			fill.position = Vector2(int(half_w) - fill_width, 0)
			fill.size = Vector2(fill_width, bar_height)
			container.add_child(fill)

	# Score label
	var score_label = Label.new()
	var score_sign = "+" if score > 0 else ""
	score_label.text = score_sign + str(score)
	score_label.add_theme_font_size_override("font_size", font_size)
	score_label.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))
	score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	score_label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	container.add_child(score_label)

	# Side labels (France / Enemy)
	var france_lbl = Label.new()
	france_lbl.text = "FR"
	france_lbl.add_theme_font_size_override("font_size", max(7, font_size - 3))
	france_lbl.add_theme_color_override("font_color", Color(0.5, 0.6, 0.8, 0.6))
	france_lbl.position = Vector2(3, 0)
	france_lbl.size = Vector2(20, bar_height)
	france_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	container.add_child(france_lbl)

	var enemy_lbl = Label.new()
	# Abbreviate enemy name to 2 chars
	var abbr = opponent.left(2).to_upper() if opponent.length() >= 2 else opponent.to_upper()
	enemy_lbl.text = abbr
	enemy_lbl.add_theme_font_size_override("font_size", max(7, font_size - 3))
	enemy_lbl.add_theme_color_override("font_color", Color(0.8, 0.5, 0.5, 0.6))
	enemy_lbl.position = Vector2(bar_width - 22, 0)
	enemy_lbl.size = Vector2(20, bar_height)
	enemy_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	enemy_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	container.add_child(enemy_lbl)

	return container


# ── RENDERING ──

func _render_war_detail(w: Dictionary):
	var trend = str(w.get("trend", "stable"))
	var duration = int(float(w.get("duration", 0)))
	var started = int(float(w.get("started_turn", 0)))
	var we = w.get("war_exhaustion", null)
	var breakdown = w.get("breakdown", null)

	var bbcode = ""

	# Breakdown
	if breakdown != null and breakdown is Dictionary:
		bbcode += "[color=" + COLOR_HEADER + "]Score Breakdown[/color]\n"
		bbcode += "  Territory:  " + _signed(int(breakdown.get("territory", 0))) + "\n"
		bbcode += "  Battles:    " + _signed(int(breakdown.get("battles", 0))) + "\n"
		bbcode += "  Decisive:   " + _signed(int(breakdown.get("decisive", 0))) + "\n"
		bbcode += "  Capital:    " + _signed(int(breakdown.get("capital", 0))) + "\n\n"

	# Duration
	bbcode += "Duration: " + str(duration) + " turns (since Turn " + str(started) + ")\n"

	# War exhaustion
	if we != null:
		var we_int = int(float(we))
		var we_color = COLOR_WHITE
		if we_int >= 80:
			we_color = COLOR_RED
		elif we_int >= 40:
			we_color = COLOR_AMBER
		bbcode += "Enemy War Exhaustion: [color=" + we_color + "]" + str(we_int) + "[/color]\n"
	else:
		bbcode += "Enemy War Exhaustion: [color=" + COLOR_DIMMED + "]Unknown[/color]\n"

	# Recent battles
	var recent = w.get("recent_battles", [])
	if recent.size() > 0:
		bbcode += "\n[color=" + COLOR_HEADER + "]Recent Battles[/color]\n"
		for b in recent:
			var prefix = ""
			if b.get("decisive", false):
				prefix = "[color=" + COLOR_GOLD + "]* [/color]"
			var outcome = "Victory" if b.get("won", false) else "Defeat"
			var outcome_color = COLOR_GREEN if b.get("won", false) else COLOR_RED
			bbcode += "  " + prefix + "[color=" + outcome_color + "]" + outcome + "[/color] at " + str(b.get("location", "?")) + " (T:" + str(int(b.get("turn", 0))) + ")\n"

	content_label.text = bbcode


func _render_coalition_detail(coalition_data: Dictionary, wars: Array):
	var leader = str(coalition_data.get("leader", ""))
	var posture = str(coalition_data.get("posture", "defensive")).capitalize()

	var bbcode = ""
	bbcode += "Leader: [color=" + COLOR_GOLD + "]" + leader + "[/color]   Posture: " + posture + "\n\n"

	# Members (text summary — bars are in score_bar_container above)
	for w in wars:
		if not w.get("in_coalition", false):
			continue
		var opp_name = str(w.get("opponent", "?"))
		var we = w.get("war_exhaustion", null)
		var army = str(w.get("army_strength", "Unknown"))
		var line = opp_name
		if we != null:
			line += "  WE:" + str(int(float(we)))
		line += "  " + army
		if opp_name == leader:
			line = "[u]" + line + "[/u]"
		bbcode += "  " + line + "\n"

	# Coordination
	var coordination = coalition_data.get("coordination", [])
	if coordination.size() > 0:
		bbcode += "\n[color=" + COLOR_HEADER + "]Coordination[/color]\n"
		for c in coordination:
			var quality = str(c.get("quality", "?"))
			var q_color = COLOR_GREEN if quality == "Good" else (COLOR_AMBER if quality == "Strained" else COLOR_RED)
			bbcode += "  " + str(c.get("nation_a", "")) + "-" + str(c.get("nation_b", "")) + ": [color=" + q_color + "]" + quality + "[/color]\n"

	# Weak link
	var weak_link = coalition_data.get("weak_link", null)
	if weak_link != null:
		bbcode += "\n[color=" + COLOR_AMBER + "]Weak link: " + str(weak_link) + " (highest WE)[/color]\n"

	content_label.text = bbcode


func _render_armistice_detail(w: Dictionary):
	var remaining = int(float(w.get("armistice_remaining", 0)))
	var relation = int(float(w.get("relation", 0)))
	var rel_desc = str(w.get("relation_descriptor", "?"))
	var rel_trend = str(w.get("relation_trend", "stable"))

	var bbcode = ""
	bbcode += "Status: [color=" + COLOR_DIMMED + "]Armistice (" + str(remaining) + " turns remaining)[/color]\n"

	var rel_color = COLOR_GREEN if relation > 0 else (COLOR_RED if relation < 0 else COLOR_WHITE)
	var rel_sign = "+" if relation > 0 else ""
	bbcode += "Relations: [color=" + rel_color + "]" + rel_sign + str(relation) + " (" + rel_desc + ")[/color]\n"
	bbcode += "Trend: " + _trend_str(rel_trend) + "\n"

	content_label.text = bbcode


# ── BUTTONS ──

func _clear_buttons():
	for child in button_row.get_children():
		child.queue_free()


func _add_negotiate_button(nation: String):
	var btn = Button.new()
	btn.text = "Negotiate Peace"
	btn.custom_minimum_size = Vector2(160, 36)
	btn.add_theme_font_size_override("font_size", 13)
	btn.pressed.connect(func():
		hide()
		negotiate_clicked.emit(nation)
	)
	button_row.add_child(btn)


func _add_target_button(nation: String):
	var btn = Button.new()
	btn.text = "Target " + nation
	btn.custom_minimum_size = Vector2(130, 36)
	btn.add_theme_font_size_override("font_size", 12)
	btn.pressed.connect(func():
		hide()
		target_clicked.emit(nation)
	)
	button_row.add_child(btn)


func _add_diplomatic_options_button(nation: String):
	var btn = Button.new()
	btn.text = "Diplomatic Options"
	btn.custom_minimum_size = Vector2(160, 36)
	btn.add_theme_font_size_override("font_size", 13)
	btn.pressed.connect(func():
		hide()
		negotiate_clicked.emit(nation)
	)
	button_row.add_child(btn)


# ── HELPERS ──

func _trend_str(trend: String) -> String:
	match trend:
		"rising":
			return "[color=" + COLOR_GREEN + "]^[/color]"
		"falling":
			return "[color=" + COLOR_RED + "]v[/color]"
		_:
			return "[color=" + COLOR_WHITE + "]=[/color]"


func _signed(val: int) -> String:
	if val > 0:
		return "+" + str(val)
	return str(val)

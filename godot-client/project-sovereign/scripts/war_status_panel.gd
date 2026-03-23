extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - War Status Panel (N4a: Layer 1 HUD)
# =============================================================================
# Compact always-visible panel anchored bottom-right. Shows active wars,
# coalition grouping, and armistice cards. CanvasLayer 25.
# Clicks emit card_clicked for main.gd to open the detail popup.
# =============================================================================

signal card_clicked(nation: String, status: String)
signal coalition_header_clicked()

@onready var panel_container = $PanelContainer
@onready var scroll_container = $PanelContainer/ScrollContainer
@onready var vbox = $PanelContainer/ScrollContainer/VBoxContainer
@onready var header_label = $PanelContainer/ScrollContainer/VBoxContainer/HeaderLabel

# Nation colors (must match map.gd COLORS)
const NATION_COLORS = {
	"France": Color(0.255, 0.412, 0.882),
	"Britain": Color(0.863, 0.078, 0.235),
	"Prussia": Color(0.2, 0.2, 0.2),
	"Austria": Color(1.0, 0.843, 0.0),
	"Saxony": Color(0.4, 0.6, 0.3),
}

const COLOR_GREEN = Color(0.29, 0.67, 0.29)
const COLOR_RED = Color(0.67, 0.27, 0.27)
const COLOR_WHITE = Color(0.75, 0.75, 0.78)
const COLOR_GOLD = Color(0.85, 0.7, 0.3)
const COLOR_DIMMED = Color(0.5, 0.5, 0.5)


func _ready():
	hide()


func update_wars(data: Dictionary) -> void:
	"""Rebuild the entire panel from active_wars data."""
	# Clear existing cards (keep header)
	for child in vbox.get_children():
		if child != header_label:
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
				_add_coalition_member_row(w)

	# ── Bilateral war cards (non-coalition) ──
	for w in wars:
		if w.get("status", "") == "war" and not w.get("in_coalition", false):
			_add_war_card(w)

	# ── Armistice cards ──
	for w in wars:
		if w.get("status", "") == "armistice":
			_add_armistice_card(w)

	show()


func _add_coalition_header(coalition_name: String):
	var btn = Button.new()
	btn.text = "  " + coalition_name.to_upper()
	btn.flat = true
	btn.custom_minimum_size = Vector2(0, 24)
	btn.add_theme_font_size_override("font_size", 11)
	btn.add_theme_color_override("font_color", COLOR_GOLD)
	btn.pressed.connect(func(): coalition_header_clicked.emit())
	vbox.add_child(btn)


func _add_coalition_member_row(war_data: Dictionary):
	var opponent = str(war_data.get("opponent", "?"))
	var score = int(float(war_data.get("war_score", 0)))
	var trend = str(war_data.get("trend", "stable"))

	var trend_arrow = _get_trend_arrow(trend)
	var score_sign = "+" if score > 0 else ""
	var text = "  " + opponent + "  " + score_sign + str(score) + " " + trend_arrow

	var btn = Button.new()
	btn.text = text
	btn.flat = true
	btn.custom_minimum_size = Vector2(0, 22)
	btn.add_theme_font_size_override("font_size", 11)
	btn.add_theme_color_override("font_color", _get_score_color(score))
	btn.pressed.connect(func(): card_clicked.emit(opponent, "war"))
	vbox.add_child(btn)


func _add_war_card(war_data: Dictionary):
	var opponent = str(war_data.get("opponent", "?"))
	var score = int(float(war_data.get("war_score", 0)))
	var trend = str(war_data.get("trend", "stable"))
	var duration = int(float(war_data.get("duration", 0)))

	var trend_arrow = _get_trend_arrow(trend)
	var score_sign = "+" if score > 0 else ""
	var text = opponent + "  " + score_sign + str(score) + " " + trend_arrow + "  T:" + str(duration)

	var btn = Button.new()
	btn.text = text
	btn.flat = true
	btn.custom_minimum_size = Vector2(0, 26)
	btn.add_theme_font_size_override("font_size", 11)
	btn.add_theme_color_override("font_color", _get_score_color(score))
	btn.pressed.connect(func(): card_clicked.emit(opponent, "war"))
	vbox.add_child(btn)

	# Score bar
	var bar = _create_score_bar(score)
	vbox.add_child(bar)


func _add_armistice_card(war_data: Dictionary):
	var opponent = str(war_data.get("opponent", "?"))
	var remaining = int(float(war_data.get("armistice_remaining", 0)))

	var btn = Button.new()
	btn.text = opponent + "  " + str(remaining) + " turns"
	btn.flat = true
	btn.custom_minimum_size = Vector2(0, 22)
	btn.add_theme_font_size_override("font_size", 11)
	btn.add_theme_color_override("font_color", COLOR_DIMMED)
	btn.pressed.connect(func(): card_clicked.emit(opponent, "armistice"))
	vbox.add_child(btn)


func _create_score_bar(score: int) -> ColorRect:
	"""Create a simple score bar: green right of center = winning, red left = losing."""
	var bar = ColorRect.new()
	bar.custom_minimum_size = Vector2(0, 4)
	# Score ranges -100 to +100. Map to bar fill.
	var normalized = clamp(score, -100, 100)
	if normalized >= 0:
		bar.color = COLOR_GREEN.lerp(COLOR_WHITE, 0.5)
	else:
		bar.color = COLOR_RED.lerp(COLOR_WHITE, 0.5)
	return bar


func _get_trend_arrow(trend: String) -> String:
	match trend:
		"rising":
			return "^"
		"falling":
			return "v"
		_:
			return "-"


func _get_score_color(score: int) -> Color:
	if score > 0:
		return COLOR_GREEN
	elif score < 0:
		return COLOR_RED
	return COLOR_WHITE

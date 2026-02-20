extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Campaign Log Overlay (Phase 6.5)
# =============================================================================
# Fog-filtered event log grouped by turn. Toggle with L key or LOG button.
# Layer 102 (above pause menu 101). Click-to-close overlay.
# =============================================================================

signal closed

# UI References
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var turn_list = $PanelContainer/VBoxContainer/ScrollContainer/TurnList
@onready var empty_label = $PanelContainer/VBoxContainer/ScrollContainer/TurnList/EmptyLabel

# Category icons (BBCode-friendly)
const CATEGORY_ICONS = {
	"combat": "[color=#daa06d]X[/color]",
	"territory": "[color=#90d890]>[/color]",
	"economy": "[color=#d9c08c]$[/color]",
	"command": "[color=#c9b8e0]![/color]",
}

# Category colors for event text
const CATEGORY_COLORS = {
	"combat": "daa06d",
	"territory": "90d890",
	"economy": "d9c08c",
	"command": "c9b8e0",
}

# Track which turns are expanded
var expanded_turns: Dictionary = {}

# Store turn data for expand/collapse
var turn_data: Dictionary = {}

func _ready():
	close_button.pressed.connect(close_log)
	background_overlay.gui_input.connect(_on_overlay_input)
	hide()

func open_log(api_client):
	"""Fetch campaign log from backend and display it."""
	# Show overlay immediately with loading state
	empty_label.text = "Loading..."
	empty_label.visible = true
	show()
	api_client.get_campaign_log(_on_campaign_log_received)

func close_log():
	"""Hide the overlay and emit closed signal."""
	hide()
	closed.emit()

func _on_campaign_log_received(response):
	"""Build the turn-grouped event list from backend response."""
	# Clear previous entries — remove_child BEFORE queue_free to avoid
	# name collisions on re-open (queue_free doesn't remove immediately)
	var children_snapshot = turn_list.get_children()
	for child in children_snapshot:
		if child != empty_label:
			turn_list.remove_child(child)
			child.queue_free()

	if not response.get("success", false):
		empty_label.text = "Failed to load campaign log."
		empty_label.visible = true
		return

	var turns = response.get("turns", [])
	if turns.is_empty():
		empty_label.text = "No events recorded."
		empty_label.visible = true
		return

	empty_label.visible = false

	# Reset tracking
	expanded_turns.clear()
	turn_data.clear()

	# Build turn sections — most recent first (backend sends descending)
	var is_first = true
	for turn_block in turns:
		var turn_num = turn_block.get("turn", 0)
		var events = turn_block.get("events", [])
		var event_count = events.size()

		# Hide empty turns (0 visible events after fog filtering)
		if event_count == 0:
			continue

		turn_data[turn_num] = events

		# Turn header button — Turn 0 shows as "Setup"
		var header_btn = Button.new()
		var turn_label = "Turn 0 — Setup" if turn_num == 0 else "Turn %d" % turn_num
		header_btn.text = "%s  —  %d event%s" % [turn_label, event_count, "" if event_count == 1 else "s"]
		header_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		header_btn.add_theme_color_override("font_color", Color(0.85, 0.75, 0.55, 1))
		header_btn.add_theme_color_override("font_hover_color", Color(1, 0.95, 0.75, 1))
		header_btn.add_theme_font_size_override("font_size", 14)
		header_btn.pressed.connect(_toggle_turn.bind(turn_num))
		turn_list.add_child(header_btn)

		# Event container (VBox below header)
		var event_container = VBoxContainer.new()
		event_container.name = "TurnEvents_%d" % turn_num
		event_container.add_theme_constant_override("separation", 2)
		turn_list.add_child(event_container)

		# Populate events
		for evt in events:
			var label = RichTextLabel.new()
			label.bbcode_enabled = true
			label.fit_content = true
			label.scroll_active = false
			label.add_theme_font_size_override("normal_font_size", 12)

			var category = evt.get("category", "unknown")
			var icon = CATEGORY_ICONS.get(category, " ")
			var color = CATEGORY_COLORS.get(category, "a0a0a8")
			var display_text = evt.get("display", "Unknown event")

			label.text = "  %s [color=#%s]%s[/color]" % [icon, color, display_text]
			event_container.add_child(label)

		# Default: most recent turn expanded, all others collapsed
		if is_first:
			expanded_turns[turn_num] = true
			event_container.visible = true
			is_first = false
		else:
			expanded_turns[turn_num] = false
			event_container.visible = false

func _toggle_turn(turn_num: int):
	"""Toggle expand/collapse for a turn's events."""
	var container_name = "TurnEvents_%d" % turn_num
	var event_container = turn_list.get_node_or_null(container_name)
	if event_container:
		var is_expanded = expanded_turns.get(turn_num, false)
		expanded_turns[turn_num] = not is_expanded
		event_container.visible = not is_expanded

func _on_overlay_input(event):
	"""Click on dark overlay to close."""
	if event is InputEventMouseButton and event.pressed:
		close_log()

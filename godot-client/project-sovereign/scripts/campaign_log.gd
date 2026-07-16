extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Campaign Log Overlay
# =============================================================================
# Fog-filtered event log grouped by turn. Turn headers now carry a simple
# expand/collapse affordance so the current state reads at a glance.
# =============================================================================

signal closed

@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var turn_list = $PanelContainer/VBoxContainer/ScrollContainer/TurnList
@onready var empty_label = $PanelContainer/VBoxContainer/ScrollContainer/TurnList/EmptyLabel

const CATEGORY_ICONS = {
	"combat": "[color=#daa06d]X[/color]",
	"territory": "[color=#90d890]>[/color]",
	"economy": "[color=#d9c08c]$[/color]",
	"command": "[color=#c9b8e0]![/color]",
	"diplomacy": "[color=#b0a0d0]D[/color]",
}

const CATEGORY_COLORS = {
	"combat": "daa06d",
	"territory": "90d890",
	"economy": "d9c08c",
	"command": "c9b8e0",
	"diplomacy": "b0a0d0",
}

var expanded_turns: Dictionary = {}
var header_buttons: Dictionary = {}
var turn_data: Dictionary = {}


func _ready():
	close_button.pressed.connect(close_log)
	background_overlay.gui_input.connect(_on_overlay_input)
	hide()


func open_log(api_client):
	empty_label.text = "Loading..."
	empty_label.visible = true
	scroll_container.scroll_vertical = 0
	show()
	Utils.clamp_centered_panel($PanelContainer)
	api_client.get_campaign_log(_on_campaign_log_received)


func close_log():
	hide()
	closed.emit()


func _on_campaign_log_received(response):
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
	expanded_turns.clear()
	header_buttons.clear()
	turn_data.clear()

	var is_first = true
	for turn_block in turns:
		var turn_num = int(turn_block.get("turn", 0))
		var events = turn_block.get("events", [])
		var event_count = events.size()
		if event_count == 0:
			continue

		turn_data[turn_num] = events

		var header_btn = Button.new()
		header_btn.set_meta("turn_label", "Turn 0 - Setup" if turn_num == 0 else "Turn %d" % turn_num)
		header_btn.set_meta("event_count", event_count)
		header_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		header_btn.add_theme_color_override("font_color", Utils.UI_GOLD)
		header_btn.add_theme_color_override("font_hover_color", Color(1, 0.95, 0.75, 1))
		header_btn.add_theme_font_size_override("font_size", 14)
		header_btn.pressed.connect(_toggle_turn.bind(turn_num))
		turn_list.add_child(header_btn)
		header_buttons[turn_num] = header_btn

		var event_container = VBoxContainer.new()
		event_container.name = "TurnEvents_%d" % turn_num
		event_container.add_theme_constant_override("separation", 2)
		turn_list.add_child(event_container)

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

			label.text = "  %s [color=#%s]%s[/color]" % [icon, color, Utils.humanize_nation_keys_in_text(str(display_text))]
			event_container.add_child(label)

		if is_first:
			expanded_turns[turn_num] = true
			event_container.visible = true
			is_first = false
		else:
			expanded_turns[turn_num] = false
			event_container.visible = false
		_update_turn_header(turn_num)


func _toggle_turn(turn_num: int):
	var event_container = turn_list.get_node_or_null("TurnEvents_%d" % turn_num)
	if event_container:
		var is_expanded = expanded_turns.get(turn_num, false)
		expanded_turns[turn_num] = not is_expanded
		event_container.visible = not is_expanded
		_update_turn_header(turn_num)


func _update_turn_header(turn_num: int):
	var header_btn = header_buttons.get(turn_num)
	if header_btn == null:
		return
	var event_count = int(header_btn.get_meta("event_count"))
	var turn_label = str(header_btn.get_meta("turn_label"))
	var affordance = "v" if expanded_turns.get(turn_num, false) else ">"
	header_btn.text = "%s %s  -  %d event%s" % [
		affordance,
		turn_label,
		event_count,
		"" if event_count == 1 else "s",
	]


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		close_log()

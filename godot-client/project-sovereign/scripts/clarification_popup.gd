extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Clarification Popup (Grouchy/Literal)
# =============================================================================
# Displays when a literal marshal needs clarification on a vague order.
# Shows interpreted target and alternatives as buttons.
# NOT an objection — this is the marshal asking for specifics.
# =============================================================================

signal clarification_choice(marshal_name: String, chosen_target: String)
signal cancelled

# UI References
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var message_label = $PanelContainer/VBoxContainer/MessageLabel
@onready var button_container = $PanelContainer/VBoxContainer/ButtonContainer

# Color palette
const COLOR_GOLD = "d9c08c"
const COLOR_TEXT = "eeeeee"

# Current clarification data
var current_marshal: String = ""

func _ready():
	hide()

func show_clarification(data: Dictionary):
	"""Display clarification popup with target options."""
	current_marshal = data.get("marshal", "Marshal")

	# Title
	title_label.text = current_marshal.to_upper() + " ASKS:"

	# Message
	var message = data.get("message", "How shall I proceed, Sire?")
	message_label.text = '"%s"' % message

	# Clear existing buttons
	for child in button_container.get_children():
		child.queue_free()

	# Primary interpreted target button
	var interpreted = data.get("interpreted_target", "")
	if interpreted:
		var primary_btn = _create_button("Yes, " + interpreted, interpreted)
		button_container.add_child(primary_btn)

	# Alternative target buttons
	var alternatives = data.get("alternatives", [])
	for alt in alternatives:
		var alt_btn = _create_button("No, " + alt, alt)
		button_container.add_child(alt_btn)

	# Options from backend (if provided instead of alternatives)
	var options = data.get("options", [])
	for option in options:
		if option != interpreted and option not in alternatives:
			var opt_btn = _create_button(option.capitalize(), option)
			button_container.add_child(opt_btn)

	# Always add cancel button
	var cancel_btn = _create_button("Cancel Order", "")
	cancel_btn.add_theme_color_override("font_color", Color(0.8, 0.5, 0.5, 1))
	button_container.add_child(cancel_btn)

	show()

func _create_button(label: String, target_value: String) -> Button:
	"""Create a styled button for a clarification option."""
	var btn = Button.new()
	btn.custom_minimum_size = Vector2(0, 42)
	btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn.text = label

	btn.add_theme_color_override("font_color", Color(0.933, 0.933, 0.933, 1))
	btn.add_theme_color_override("font_pressed_color", Color(1, 1, 1, 1))
	btn.add_theme_color_override("font_hover_color", Color(1, 1, 1, 1))
	btn.add_theme_font_size_override("font_size", 14)

	btn.pressed.connect(_on_option_pressed.bind(target_value))
	return btn

func _on_option_pressed(target_value: String):
	"""Handle player selecting a clarification option."""
	hide()
	if target_value == "":
		cancelled.emit()
	else:
		clarification_choice.emit(current_marshal, target_value)

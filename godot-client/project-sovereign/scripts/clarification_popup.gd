extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Clarification Popup (Grouchy/Literal)
# =============================================================================
# Displays when a literal marshal needs clarification on a vague order.
# Shows interpreted target and alternatives as buttons.
# NOT an objection — this is the marshal asking for specifics.
# =============================================================================

signal clarification_choice(marshal_name: String, chosen_target: String, strategic_type: String)
# CR-2: options built by the backend carry a full reissue command — emit it
# verbatim so backend and popup resolve answers identically.
signal clarification_command(command: String)
signal cancelled

# UI References
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var message_label = $PanelContainer/VBoxContainer/MessageLabel
@onready var button_container = $PanelContainer/VBoxContainer/ButtonContainer

# Current clarification data
var current_marshal: String = ""
var current_strategic_type: String = ""

func _ready():
	hide()

func show_clarification(data: Dictionary):
	"""Display clarification popup with target options."""
	current_marshal = str(data.get("marshal", "Marshal"))
	# CR-2: .get() defaults do NOT apply to present-but-null keys — a null
	# strategic_type must not crash the typed String assignment
	var st = data.get("strategic_type", "PURSUE")
	current_strategic_type = str(st) if st != null else "PURSUE"

	# Title
	title_label.text = current_marshal.to_upper() + " ASKS:"

	# Message
	var message = data.get("message", "How shall I proceed, Sire?")
	message_label.text = '"%s"' % message

	# Clear existing buttons
	for child in button_container.get_children():
		child.queue_free()

	# Use structured options from backend if available, else fall back to interpreted/alternatives
	var options = data.get("options", [])
	if options.size() > 0:
		for option in options:
			var label = option.get("label", "Option")
			var opt_btn = _create_button(label, option)
			button_container.add_child(opt_btn)
	else:
		# Fallback: build buttons from interpreted_target + alternatives
		var interpreted = data.get("interpreted_target", "")
		if interpreted:
			var primary_btn = _create_button("Yes, " + interpreted, {"target": interpreted})
			button_container.add_child(primary_btn)

		var alternatives = data.get("alternatives", [])
		for alt in alternatives:
			var alt_btn = _create_button("No, " + alt, {"target": alt})
			button_container.add_child(alt_btn)

	# Always add cancel button
	var cancel_btn = _create_button("Cancel Order", {})
	cancel_btn.add_theme_color_override("font_color", Color(0.8, 0.5, 0.5, 1))
	button_container.add_child(cancel_btn)

	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)

func _create_button(label: String, option: Dictionary) -> Button:
	"""Create a styled button for a clarification option."""
	var btn = Button.new()
	btn.custom_minimum_size = Vector2(0, 42)
	btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn.text = label

	btn.add_theme_color_override("font_color", Color(0.933, 0.933, 0.933, 1))
	btn.add_theme_color_override("font_pressed_color", Color(1, 1, 1, 1))
	btn.add_theme_color_override("font_hover_color", Color(1, 1, 1, 1))
	btn.add_theme_font_size_override("font_size", 14)

	btn.pressed.connect(_on_option_pressed.bind(option))
	return btn

func _on_option_pressed(option: Dictionary):
	"""Handle player selecting a clarification option."""
	for btn in button_container.get_children():
		btn.disabled = true
	hide()
	var command = str(option.get("command", ""))
	var target = str(option.get("target", ""))
	var value = str(option.get("value", ""))
	if command != "":
		# CR-2: backend supplied the exact reissue command — send it verbatim
		clarification_command.emit(command)
	elif value == "cancel" or (target == "" and value == ""):
		# Backend cancel option or the popup's own Cancel Order button.
		# (Pre-CR-2 the backend cancel option leaked "cancel" as a TARGET
		# and reissued "<marshal> pursue cancel".)
		cancelled.emit()
	elif target != "":
		clarification_choice.emit(current_marshal, target, current_strategic_type)
	else:
		cancelled.emit()

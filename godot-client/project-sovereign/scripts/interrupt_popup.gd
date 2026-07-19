extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN - Strategic Interrupt Popup (R15 migrated)
# =============================================================================
# Displays when a marshal's strategic order hits an interrupt requiring
# player input: cannon fire, blocked path, contact, ally moving.
# Buttons are generated dynamically from the interrupt's options list.
# =============================================================================

signal choice_made(marshal_name: String, response_type: String, choice: String)

# UI References
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var message_label = $PanelContainer/VBoxContainer/MessageLabel
@onready var button_container = $PanelContainer/VBoxContainer/ButtonContainer

# Current interrupt data
var current_marshal: String = ""
var current_response_type: String = ""

# Human-readable labels for option IDs
const OPTION_LABELS = {
	"attack": "Attack!",
	"attack_anyway": "Commit the Attack",
	"go_around": "Go Around",
	"hold_position": "Hold Position",
	"cancel_order": "Cancel Order",
	"investigate": "March to the Guns",
	"continue_order": "Continue as Ordered",
	"attack_again": "Attack Again",
	"follow": "Follow Ally",
	"hold_current": "Hold Current Position",
	"cancel_support": "Cancel Support",
	"fight_to_the_last": "Fight to the Last",
	"attempt_breakout": "Attempt a Breakout",
}

func _ready():
	hide()

func show_interrupt(interrupt_data: Dictionary):
	"""Display interrupt popup with dynamic buttons."""
	current_marshal = interrupt_data.get("marshal", "Marshal")
	current_response_type = interrupt_data.get("interrupt_type", "unknown")

	# Title
	title_label.text = current_marshal.to_upper() + " REPORTS"

	# Message
	var message = interrupt_data.get("message", "Awaiting your orders, Sire.")
	message_label.text = '"%s"' % message

	# Clear existing buttons
	for child in button_container.get_children():
		child.queue_free()

	# Create buttons from options
	var options = interrupt_data.get("options", [])
	if options.is_empty():
		# Fallback: just a continue button
		options = ["continue_order"]

	for option_id in options:
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(0, 45)
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.text = OPTION_LABELS.get(option_id, option_id.replace("_", " ").capitalize())

		# Style to match existing dialogs
		btn.add_theme_color_override("font_color", Color(0.933, 0.933, 0.933, 1))
		btn.add_theme_color_override("font_pressed_color", Color(1, 1, 1, 1))
		btn.add_theme_color_override("font_hover_color", Color(1, 1, 1, 1))
		btn.add_theme_font_size_override("font_size", 14)

		# Bind the option_id to the callback
		btn.pressed.connect(_on_option_pressed.bind(option_id))
		button_container.add_child(btn)

	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)

func _on_option_pressed(option_id: String):
	"""Handle player selecting an interrupt response option."""
	close_popup()
	choice_made.emit(current_marshal, current_response_type, option_id)

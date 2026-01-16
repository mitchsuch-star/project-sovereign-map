extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Marshal Redemption Dialog
# =============================================================================
# Displays when a marshal's trust drops to critical levels (≤ 20)
# Player chooses: Grant Autonomy, Dismiss Marshal, or Demand Obedience
# =============================================================================

signal choice_made(choice: String)

# UI References
@onready var panel_container = $PanelContainer
@onready var marshal_name_label = $PanelContainer/VBoxContainer/MarshalNameLabel
@onready var message_label = $PanelContainer/VBoxContainer/MessageLabel
@onready var trust_label = $PanelContainer/VBoxContainer/StatsContainer/TrustLabel
@onready var autonomy_button = $PanelContainer/VBoxContainer/ButtonContainer/AutonomyButton
@onready var dismiss_button = $PanelContainer/VBoxContainer/ButtonContainer/DismissButton
@onready var demand_button = $PanelContainer/VBoxContainer/ButtonContainer/DemandButton

var current_marshal: String = ""

# Napoleonic color palette
const COLOR_GOLD = "d9c08c"
const COLOR_TEXT = "eee"
const COLOR_WARNING = "cd6b6b"
const COLOR_PANEL = "1a1a2e"

func _ready():
	# Connect button signals
	autonomy_button.pressed.connect(_on_autonomy_pressed)
	dismiss_button.pressed.connect(_on_dismiss_pressed)
	demand_button.pressed.connect(_on_demand_pressed)

	# Hide by default
	hide()

func show_redemption(redemption_data: Dictionary):
	"""Display redemption dialog with data from backend."""
	print("REDEMPTION DIALOG: show_redemption() called")
	print("  Data: ", redemption_data)

	current_marshal = redemption_data.get("marshal", "Marshal")

	# Set marshal name header
	marshal_name_label.text = "%s REQUESTS AUDIENCE" % current_marshal.to_upper()

	# Set message
	var message = redemption_data.get("message", "Our relationship has broken down, Sire. Something must change.")
	message_label.text = '"%s"' % message

	# Get trust value
	var trust = int(redemption_data.get("trust", 20))
	trust_label.text = "Trust: %d (Critical)" % trust

	# Set button text with descriptions
	var options = redemption_data.get("options", [])
	for opt in options:
		var opt_id = opt.get("id", "")
		var opt_text = opt.get("text", "")
		match opt_id:
			"grant_autonomy":
				autonomy_button.text = opt_text if opt_text else "Grant Autonomy (3 turns)"
			"dismiss":
				dismiss_button.text = opt_text if opt_text else "Dismiss Marshal"
			"demand_obedience":
				demand_button.text = opt_text if opt_text else "Demand Obedience"

	# Show the dialog
	print("REDEMPTION DIALOG: Showing dialog...")
	show()
	print("REDEMPTION DIALOG: visible = ", visible)

func _on_autonomy_pressed():
	"""Player grants marshal autonomy."""
	hide()
	choice_made.emit("grant_autonomy")

func _on_dismiss_pressed():
	"""Player dismisses the marshal."""
	hide()
	choice_made.emit("dismiss")

func _on_demand_pressed():
	"""Player demands obedience despite broken trust."""
	hide()
	choice_made.emit("demand_obedience")

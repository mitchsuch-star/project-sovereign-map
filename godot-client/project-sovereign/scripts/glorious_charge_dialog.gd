extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Glorious Charge Dialog
# =============================================================================
# Displays when a reckless cavalry marshal (Ney) reaches recklessness 3
# Player chooses: Execute Glorious Charge (2x damage) or Normal Attack
# =============================================================================

signal choice_made(choice: String)

# UI References
@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var marshal_label = $PanelContainer/VBoxContainer/MarshalLabel
@onready var recklessness_label = $PanelContainer/VBoxContainer/RecklessnessLabel
@onready var warning_label = $PanelContainer/VBoxContainer/WarningLabel
@onready var charge_button = $PanelContainer/VBoxContainer/ButtonContainer/ChargeButton
@onready var restrain_button = $PanelContainer/VBoxContainer/ButtonContainer/RestrainButton

var current_marshal: String = ""
var current_target: String = ""
var current_recklessness: int = 0

# Napoleonic color palette
const COLOR_GOLD = "d9c08c"
const COLOR_TEXT = "eee"
const COLOR_DANGER = "ff4444"
const COLOR_CAVALRY = "8b4513"  # Saddle brown for cavalry theme

func _ready():
	print("GloriousChargeDialog: _ready() STARTING")
	print("  panel_container: ", panel_container)
	print("  charge_button: ", charge_button)
	print("  restrain_button: ", restrain_button)

	# Connect button signals
	if charge_button:
		charge_button.pressed.connect(_on_charge_pressed)
		print("  ✓ ChargeButton connected")
	else:
		push_error("GloriousChargeDialog: ChargeButton is NULL!")

	if restrain_button:
		restrain_button.pressed.connect(_on_restrain_pressed)
		print("  ✓ RestrainButton connected")
	else:
		push_error("GloriousChargeDialog: RestrainButton is NULL!")

	# Hide by default
	hide()

	print("GloriousChargeDialog: _ready() COMPLETE - is_inside_tree: ", is_inside_tree())

func show_glorious_charge(data: Dictionary):
	"""Display Glorious Charge popup with data from backend."""
	print("GloriousChargeDialog.show_glorious_charge() ENTERED")
	print("  Received data: ", data)

	# Handle null values from JSON (get() default doesn't work if key exists with null)
	var marshal_val = data.get("marshal")
	var target_val = data.get("target")
	var reck_val = data.get("recklessness")

	current_marshal = marshal_val if marshal_val != null else "Marshal"
	current_target = target_val if target_val != null else "enemy"
	current_recklessness = int(reck_val) if reck_val != null else 3

	print("  Parsed: marshal=%s, target=%s, recklessness=%d" % [current_marshal, current_target, current_recklessness])

	# Set title with horse emoji
	title_label.text = "GLORIOUS CHARGE!"

	# Set marshal info
	marshal_label.text = "%s's blood is up!" % current_marshal

	# Set recklessness level with visual indicator (simple bars)
	var reck_bars = ""
	for i in range(current_recklessness):
		reck_bars += "|"
	for i in range(4 - current_recklessness):
		reck_bars += "."
	recklessness_label.text = "Recklessness: %s (%d/4)" % [reck_bars, current_recklessness]

	# Set warning
	warning_label.text = "Glorious Charge deals 2x damage but also TAKES 2x damage!\nTarget: %s" % current_target

	# Set button text
	charge_button.text = "CHARGE! (2x damage dealt AND taken)"
	restrain_button.text = "Restrain - Normal Attack"

	# Show the dialog
	print("  About to call show()")

	# Ensure all children are visible first
	if panel_container:
		panel_container.visible = true
		print("  Set panel_container.visible = true")

	# Get the background overlay and make it visible too
	var bg_overlay = get_node_or_null("BackgroundOverlay")
	if bg_overlay:
		bg_overlay.visible = true
		print("  Set BackgroundOverlay.visible = true")

	# Now show the CanvasLayer itself
	show()
	visible = true  # Force visibility

	print("  AFTER show() - visible property: ", visible)
	print("  is_inside_tree: ", is_inside_tree())
	print("  PanelContainer visible: ", panel_container.visible if panel_container else "NULL")
	print("  layer: ", layer)

func _on_charge_pressed():
	"""Player chooses to execute Glorious Charge."""
	print("GloriousChargeDialog: CHARGE pressed")
	hide()
	choice_made.emit("charge")

func _on_restrain_pressed():
	"""Player restrains the marshal - normal attack."""
	print("GloriousChargeDialog: RESTRAIN pressed")
	hide()
	choice_made.emit("restrain")

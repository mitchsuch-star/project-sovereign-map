extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Capture Choice Dialog (Phase 6.2.E)
# =============================================================================
# Displays when player captures an enemy region.
# Player chooses: Plunder (gold + destroy buildings) or Secure (higher stability)
# =============================================================================

signal choice_made(choice: String)

# UI References
@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var region_label = $PanelContainer/VBoxContainer/RegionLabel
@onready var description_label = $PanelContainer/VBoxContainer/DescriptionLabel
@onready var plunder_button = $PanelContainer/VBoxContainer/ButtonContainer/PlunderButton
@onready var secure_button = $PanelContainer/VBoxContainer/ButtonContainer/SecureButton

var current_region: String = ""
var current_capturer: String = ""

func _ready():
	# Connect button signals
	if plunder_button:
		plunder_button.pressed.connect(_on_plunder_pressed)
	else:
		push_error("CaptureChoiceDialog: PlunderButton is NULL!")

	if secure_button:
		secure_button.pressed.connect(_on_secure_pressed)
	else:
		push_error("CaptureChoiceDialog: SecureButton is NULL!")

	# Hide by default
	hide()

func show_capture_choice(data: Dictionary):
	"""Display capture choice popup with data from backend."""
	var region_val = data.get("region")
	var capturer_val = data.get("capturer")

	current_region = region_val if region_val != null else "Unknown"
	current_capturer = capturer_val if capturer_val != null else "Marshal"

	# Set title
	title_label.text = "REGION CAPTURED!"

	# Set region info
	region_label.text = "%s has taken %s" % [current_capturer, current_region]

	# Set description
	description_label.text = "How shall your forces treat the conquered territory?"

	# Set button text with consequences
	plunder_button.text = "PLUNDER (Loot gold, destroy buildings, stability 10)"
	secure_button.text = "SECURE (Preserve order, stability 25, buildings damaged)"

	# Ensure all children are visible first
	if panel_container:
		panel_container.visible = true

	var bg_overlay = get_node_or_null("BackgroundOverlay")
	if bg_overlay:
		bg_overlay.visible = true

	# Show the CanvasLayer
	show()
	visible = true

func _on_plunder_pressed():
	"""Player chooses to plunder the region."""
	hide()
	choice_made.emit("plunder")

func _on_secure_pressed():
	"""Player chooses to secure the region."""
	hide()
	choice_made.emit("secure")

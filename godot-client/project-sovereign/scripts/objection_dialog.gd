extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Marshal Objection Dialog
# =============================================================================
# Displays when a marshal objects to an order with severity ≥ 0.50
# Player chooses: Trust (accept alternative), Insist (override), or Compromise
# =============================================================================

signal choice_made(choice: String)

# UI References
@onready var panel_container = $PanelContainer
@onready var marshal_name_label = $PanelContainer/VBoxContainer/MarshalNameLabel
@onready var message_label = $PanelContainer/VBoxContainer/MessageLabel
@onready var personality_label = $PanelContainer/VBoxContainer/StatsContainer/PersonalityLabel
@onready var trust_label = $PanelContainer/VBoxContainer/StatsContainer/TrustLabel
@onready var vindication_label = $PanelContainer/VBoxContainer/StatsContainer/VindicationLabel
@onready var authority_label = $PanelContainer/VBoxContainer/StatsContainer/AuthorityLabel
@onready var trust_button = $PanelContainer/VBoxContainer/ButtonContainer/TrustButton
@onready var insist_button = $PanelContainer/VBoxContainer/ButtonContainer/InsistButton
@onready var compromise_button = $PanelContainer/VBoxContainer/ButtonContainer/CompromiseButton

var current_marshal: String = ""
var has_alternative: bool = false
var has_compromise: bool = false

# Napoleonic color palette
const COLOR_GOLD = "d9c08c"
const COLOR_TEXT = "eee"
const COLOR_BACKGROUND = "16213e"
const COLOR_PANEL = "1a1a2e"
const COLOR_TRUST = "2d5a27"    # Green
const COLOR_INSIST = "8b0000"   # Dark red
const COLOR_COMPROMISE = "4a4a4a"  # Gray

func _ready():
	# Connect button signals
	trust_button.pressed.connect(_on_trust_pressed)
	insist_button.pressed.connect(_on_insist_pressed)
	compromise_button.pressed.connect(_on_compromise_pressed)

	# Hide by default
	hide()

	# Apply styling
	_apply_styling()

func _apply_styling():
	"""Apply Napoleonic theme styling to the dialog."""
	# This would be better done in the .tscn file, but we can set some properties here
	# Background panel styling (requires theme override in .tscn)
	pass

func show_objection(objection_data: Dictionary):
	"""Display objection dialog with data from backend."""
	print("14. ObjectionDialog.show_objection() ENTERED")
	print("15. Received data: ", objection_data)

	current_marshal = objection_data.get("marshal", "Marshal")

	# Set marshal name header
	marshal_name_label.text = "%s OBJECTS" % current_marshal.to_upper()

	# Set objection message
	var message = objection_data.get("message", "I have concerns about this order, Sire.")
	message_label.text = '"%s"' % message

	# Get marshal stats (from game state if available, otherwise defaults)
	var personality = objection_data.get("personality", "unknown")
	if personality_label:
		personality_label.text = "Personality: %s" % personality.capitalize()

	var trust = int(objection_data.get("trust", 70))
	var trust_label_text = objection_data.get("trust_label", "Unknown")
	trust_label.text = "Trust: %d (%s)" % [trust, trust_label_text]

	var vindication = int(objection_data.get("vindication", 0))
	vindication_label.text = "Track record: %s" % _get_vindication_text(vindication)

	var authority = int(objection_data.get("authority", 100))
	authority_label.text = "Authority: %d" % authority

	# Check which options are available
	has_alternative = objection_data.has("suggested_alternative") and objection_data.suggested_alternative != null
	has_compromise = objection_data.has("compromise") and objection_data.compromise != null

	# Set button text
	if has_alternative:
		var alt = objection_data.suggested_alternative
		var alt_desc = _describe_order(alt)
		trust_button.text = "Trust %s (%s)" % [current_marshal, alt_desc]
	else:
		trust_button.text = "Trust %s's Judgment" % current_marshal

	insist_button.text = "Proceed as Ordered"

	if has_compromise:
		var comp = objection_data.compromise
		var comp_desc = _describe_order(comp)
		compromise_button.text = "Compromise (%s)" % comp_desc
		compromise_button.visible = true
	else:
		compromise_button.visible = false

	# Show the dialog
	print("16. About to call show()")
	show()
	print("17. AFTER show() - visible property: ", visible)
	print("18. is_inside_tree: ", is_inside_tree())
	print("19. PanelContainer visible: ", panel_container.visible if panel_container else "NULL")

func _describe_order(order: Dictionary) -> String:
	"""Create brief description of an order."""
	if not order:
		return "unknown"

	var action = order.get("action", "act")
	var target = order.get("target", "")

	if target:
		return "%s %s" % [action, target]
	else:
		return action

func _get_vindication_text(score: int) -> String:
	"""Convert vindication score to readable text."""
	if score >= 3:
		return "Often correct"
	elif score >= 1:
		return "Good instincts"
	elif score <= -3:
		return "Often wrong"
	elif score <= -1:
		return "Mixed results"
	return "Neutral"

func _on_trust_pressed():
	"""Player chooses to trust marshal's judgment."""
	hide()
	choice_made.emit("trust")

func _on_insist_pressed():
	"""Player insists on original order."""
	hide()
	choice_made.emit("insist")

func _on_compromise_pressed():
	"""Player seeks middle ground."""
	hide()
	choice_made.emit("compromise")

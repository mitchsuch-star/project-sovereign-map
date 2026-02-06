extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Marshal Objection Dialog
# =============================================================================
# V2a: Tone-based styling. Border color and header reflect trust tier:
#   respectful (DEVOTED) = gold, firm (TRUSTING) = orange,
#   challenging (WARY) = red, defiant (HOSTILE) = dark red
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

# V2a tone-based border colors
const TONE_COLORS = {
	"respectful": Color(0.851, 0.753, 0.549, 1),  # Gold
	"firm": Color(0.9, 0.6, 0.2, 1),               # Orange
	"challenging": Color(0.8, 0.2, 0.2, 1),         # Red
	"defiant": Color(0.55, 0.0, 0.0, 1),            # Dark red
}

# V2a tone-based header text
const TONE_HEADERS = {
	"respectful": "%s'S ADVICE",
	"firm": "%s'S CONCERN",
	"challenging": "%s OBJECTS",
	"defiant": "%s REFUSES",
}

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
	pass

func _apply_tone_styling(tone: String):
	"""V2a: Apply border color and header text based on marshal's tone."""
	# Header text
	var header_template = TONE_HEADERS.get(tone, "%s OBJECTS")
	marshal_name_label.text = header_template % current_marshal.to_upper()

	# Border color on panel StyleBox
	var border_color = TONE_COLORS.get(tone, TONE_COLORS["firm"])
	var style = panel_container.get_theme_stylebox("panel")
	if style and style is StyleBoxFlat:
		var new_style = style.duplicate()
		new_style.border_color = border_color
		panel_container.add_theme_stylebox_override("panel", new_style)

	# Header label color matches border
	marshal_name_label.add_theme_color_override("font_color", border_color)

func show_objection(objection_data: Dictionary):
	"""Display objection dialog with data from backend."""
	current_marshal = objection_data.get("marshal", "Marshal")

	# V2a: Apply tone-based styling (border color + header text)
	var tone = objection_data.get("tone", "firm")
	_apply_tone_styling(tone)

	# Set objection message
	var message = objection_data.get("message", "I have concerns about this order, Sire.")
	message_label.text = '"%s"' % message

	# Get marshal stats
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

	# V2a trust change values for button previews
	var trust_gain = int(objection_data.get("trust_gain", 3))
	var insist_penalty = int(objection_data.get("insist_penalty", -10))
	var compromise_gain = int(objection_data.get("compromise_gain", 3))

	# Strategic objections (Phase M) use options array
	# Tactical objections use suggested_alternative/compromise dicts
	var options = objection_data.get("options", [])
	var is_strategic = objection_data.get("is_strategic", false) or options.size() > 0

	if is_strategic and options.size() > 0:
		# Strategic objection - use options array (already has trust previews)
		_setup_strategic_buttons(options)
	else:
		# Tactical objection
		has_alternative = objection_data.has("suggested_alternative") and objection_data.suggested_alternative != null
		has_compromise = objection_data.has("compromise") and objection_data.compromise != null

		# Set button text with V2a trust change previews
		if has_alternative:
			var alt = objection_data.suggested_alternative
			var alt_desc = _describe_order(alt)
			trust_button.text = "Trust %s: %s (%+d trust)" % [current_marshal, alt_desc, trust_gain]
		else:
			trust_button.text = "Trust %s's Judgment (%+d trust)" % [current_marshal, trust_gain]

		insist_button.text = "Proceed as Ordered (%+d trust)" % insist_penalty

		if has_compromise:
			var comp = objection_data.compromise
			var comp_desc = _describe_order(comp)
			compromise_button.text = "Compromise: %s (%+d trust)" % [comp_desc, compromise_gain]
			compromise_button.visible = true
		else:
			compromise_button.visible = false

	# Show the dialog
	show()

func _describe_order(order: Dictionary) -> String:
	"""Create human-readable description of an order."""
	if not order:
		return "unknown"

	var action = order.get("action", "act")
	var target = order.get("target", "")

	# Handle specific action types with nice formatting
	match action:
		"attack":
			return "attack %s" % target if target else "attack"
		"defend":
			return "defend position"
		"move":
			return "move to %s" % target if target else "move"
		"fortify":
			return "fortify position"
		"drill":
			return "drill troops"
		"retreat":
			return "retreat"
		"stance_change":
			var stance = target.to_upper() if target else "new"
			return "adopt %s stance" % stance
		"aggressive_stance":
			return "adopt AGGRESSIVE stance"
		"defensive_stance":
			return "adopt DEFENSIVE stance"
		"neutral_stance":
			return "adopt NEUTRAL stance"
		"recruit":
			return "recruit troops"
		"unfortify":
			return "abandon fortifications"
		"wait", "hold":
			return "hold position"
		_:
			# Fallback for unknown actions
			if target:
				return "%s %s" % [action, target]
			return action

func _setup_strategic_buttons(options: Array):
	"""Configure buttons for strategic objection options."""
	# Find each option type
	var proceed_opt = null
	var preferred_opt = null
	var compromise_opt = null

	for opt in options:
		var opt_type = opt.get("type", "")
		if opt_type == "proceed":
			proceed_opt = opt
		elif opt_type == "preferred":
			preferred_opt = opt
		elif opt_type == "compromise":
			compromise_opt = opt

	# Set up Insist/Proceed button
	if proceed_opt:
		var text = proceed_opt.get("text", "Proceed as Ordered")
		var ap = proceed_opt.get("ap_cost", 2)
		var trust = proceed_opt.get("trust_change", -10)
		insist_button.text = "%s (%d AP, %+d trust)" % [text, ap, trust]
	else:
		insist_button.text = "Proceed as Ordered"

	# Set up Trust/Preferred button
	if preferred_opt:
		var text = preferred_opt.get("text", "Accept Alternative")
		var ap = preferred_opt.get("ap_cost", 1)
		var trust = preferred_opt.get("trust_change", 12)
		trust_button.text = "%s (%d AP, %+d trust)" % [text, ap, trust]
		has_alternative = true
	else:
		trust_button.text = "Trust %s's Judgment" % current_marshal
		has_alternative = false

	# Set up Compromise button
	if compromise_opt:
		var text = compromise_opt.get("text", "Compromise")
		var ap = compromise_opt.get("ap_cost", 2)
		var trust = compromise_opt.get("trust_change", 3)
		compromise_button.text = "%s (%d AP, %+d trust)" % [text, ap, trust]
		compromise_button.visible = true
		has_compromise = true
	else:
		compromise_button.visible = false
		has_compromise = false

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

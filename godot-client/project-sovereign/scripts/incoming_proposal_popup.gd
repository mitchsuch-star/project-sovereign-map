extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Incoming Proposal Popup (Session 8C)
# =============================================================================
# Displays when an AI nation sends a diplomatic proposal to the player.
# Three buttons: Accept / Counter / Reject
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var accept_btn = $PanelContainer/VBoxContainer/ButtonContainer/AcceptButton
@onready var counter_btn = $PanelContainer/VBoxContainer/ButtonContainer/CounterButton
@onready var reject_btn = $PanelContainer/VBoxContainer/ButtonContainer/RejectButton

# Display name mapping for proposal types
const PROPOSAL_TYPE_DISPLAY = {
	"PEACE_TREATY": "Peace Treaty",
	"ALLIANCE": "Alliance",
	"NON_AGGRESSION": "Non-Aggression Pact",
	"OPEN_BORDERS": "Open Borders",
	"TRADE_AGREEMENT": "Trade Agreement",
	"VASSALAGE": "Vassalage",
	"MILITARY_ACCESS": "Military Access",
	"DEFENSIVE_ALLIANCE": "Defensive Alliance",
}

var current_data: Dictionary = {}
var _default_border_color: Color
@onready var panel_style: StyleBoxFlat = $PanelContainer.get_theme_stylebox("panel")

func _ready():
	hide()
	accept_btn.pressed.connect(_on_accept)
	counter_btn.pressed.connect(_on_counter)
	reject_btn.pressed.connect(_on_reject)
	# Cache default border color for normal proposals
	_default_border_color = panel_style.border_color

func show_proposal(data: Dictionary):
	"""Display incoming proposal popup."""
	current_data = data
	var from_nation = data.get("from_nation", "Unknown")
	var diplomat_name = data.get("diplomat_name", "An envoy")
	var diplomat_personality = data.get("diplomat_personality", "")
	var proposal_type = data.get("proposal_type", "unknown")
	var clauses = data.get("clauses", [])
	var assessment = data.get("talleyrand_assessment", "")
	var accept_hint = data.get("acceptance_hint", "")
	var reject_hint = data.get("rejection_hint", "")
	var is_counter = data.get("is_counter_offer", false)

	var type_display = PROPOSAL_TYPE_DISPLAY.get(proposal_type, proposal_type.replace("_", " ").capitalize())
	var bbcode = ""

	if is_counter:
		# Counter-offer: distinct header + context
		bbcode += "[center][color=#7eb8da][b]COUNTER-OFFER[/b][/color][/center]\n"
		var pers_str = " (%s)" % diplomat_personality if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, pers_str, from_nation]
		bbcode += "[color=#a0a0a8]In response to your %s proposal, %s offers modified terms:[/color]\n\n" % [type_display, from_nation]
		bbcode += "[b]Revised Terms:[/b]\n"
		# Style: blue border for counter-offers
		panel_style.border_color = Color(0.494, 0.722, 0.855, 1.0)  # Steel blue
	else:
		# Normal AI proposal
		bbcode += "[b]DIPLOMATIC ENVOY[/b]\n"
		var pers_str = " (%s)" % diplomat_personality if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, pers_str, from_nation]
		bbcode += "[b]Proposes:[/b] %s\n" % type_display
		bbcode += "[b]Terms:[/b]\n"
		# Restore default gold border
		panel_style.border_color = _default_border_color

	for clause in clauses:
		bbcode += "  - %s\n" % str(clause)

	if assessment:
		bbcode += "\n[color=gray]%s[/color]\n" % assessment

	if accept_hint:
		bbcode += "\n[color=green]If accepted: %s[/color]" % accept_hint
	if reject_hint:
		bbcode += "\n[color=red]Key obstacle: %s[/color]" % reject_hint

	content_label.text = ""
	content_label.append_text(bbcode)

	# Enable buttons — hide Counter for counter-offers (no counter-counter)
	accept_btn.disabled = false
	counter_btn.visible = not is_counter
	counter_btn.disabled = is_counter
	reject_btn.disabled = false
	# Button labels adapt to context
	accept_btn.text = "Accept Terms" if is_counter else "Accept"
	reject_btn.text = "Reject Terms" if is_counter else "Reject"
	show()

func _on_accept():
	_disable_buttons()
	hide()
	choice_made.emit("accept", current_data)

func _on_counter():
	_disable_buttons()
	hide()
	choice_made.emit("counter", current_data)

func _on_reject():
	_disable_buttons()
	hide()
	choice_made.emit("reject", current_data)

func _disable_buttons():
	accept_btn.disabled = true
	counter_btn.disabled = true
	reject_btn.disabled = true

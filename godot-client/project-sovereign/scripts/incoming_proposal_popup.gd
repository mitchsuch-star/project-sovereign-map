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

var current_data: Dictionary = {}

func _ready():
	hide()
	accept_btn.pressed.connect(_on_accept)
	counter_btn.pressed.connect(_on_counter)
	reject_btn.pressed.connect(_on_reject)

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

	var bbcode = ""
	bbcode += "[b]DIPLOMATIC ENVOY[/b]\n"
	bbcode += "%s (%s) of %s\n\n" % [diplomat_name, diplomat_personality, from_nation]
	bbcode += "[b]Proposes:[/b] %s\n" % proposal_type.replace("_", " ").capitalize()
	bbcode += "[b]Terms:[/b]\n"

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
	var is_counter = data.get("is_counter_offer", false)
	counter_btn.visible = not is_counter
	counter_btn.disabled = is_counter
	reject_btn.disabled = false
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

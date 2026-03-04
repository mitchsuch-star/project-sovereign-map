extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Sabotage Discovery Popup (Session 8C)
# =============================================================================
# Displays when player discovers Talleyrand modified their proposal.
# Two buttons: Confront / Overlook
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var confront_btn = $PanelContainer/VBoxContainer/ButtonContainer/ConfrontButton
@onready var overlook_btn = $PanelContainer/VBoxContainer/ButtonContainer/OverlookButton

var current_data: Dictionary = {}

func _ready():
	hide()
	confront_btn.pressed.connect(_on_confront)
	overlook_btn.pressed.connect(_on_overlook)

func show_sabotage(data: Dictionary):
	"""Display sabotage discovery popup."""
	current_data = data
	var target = data.get("target_nation", "Unknown")
	var ordered = data.get("ordered_summary", "?")
	var delivered = data.get("delivered_summary", "?")
	var trust_penalty = data.get("trust_penalty_if_confronted", 10)
	var auth_bonus = data.get("authority_bonus_if_confronted", 5)
	var trust_bonus = data.get("trust_bonus_if_overlooked", 3)

	var bbcode = ""
	bbcode += "[b]TALLEYRAND'S DECEPTION DISCOVERED[/b]\n\n"
	bbcode += "[b]You ordered:[/b]  %s\n" % ordered
	bbcode += "[b]He delivered:[/b] %s\n\n" % delivered
	bbcode += "[b]How do you respond?[/b]\n\n"
	bbcode += "[color=yellow]Confront:[/color] Authority +%d, Trust -%d\n" % [auth_bonus, trust_penalty]
	bbcode += "[color=green]Overlook:[/color] Trust +%d" % trust_bonus

	content_label.text = ""
	content_label.append_text(bbcode)

	confront_btn.disabled = false
	overlook_btn.disabled = false
	show()

func _on_confront():
	_disable_buttons()
	hide()
	choice_made.emit("confront", current_data)

func _on_overlook():
	_disable_buttons()
	hide()
	choice_made.emit("overlook", current_data)

func _disable_buttons():
	confront_btn.disabled = true
	overlook_btn.disabled = true

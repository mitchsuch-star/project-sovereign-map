extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Alliance Paradox Popup (Deep Audit Session 8)
# =============================================================================
# Shown when an attack would violate an alliance. Player must choose:
# honor the defender (cancel attack) or break the alliance.
# CanvasLayer 100 (modal). Pattern follows coalition_declaration_popup.
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var honor_button = $PanelContainer/VBoxContainer/ButtonContainer/HonorButton
@onready var break_button = $PanelContainer/VBoxContainer/ButtonContainer/BreakButton

var _data: Dictionary = {}


func _ready():
	hide()
	honor_button.pressed.connect(_on_honor_pressed)
	break_button.pressed.connect(_on_break_pressed)


func show_paradox(data: Dictionary):
	"""Display alliance paradox popup."""
	_data = data
	var attacker = str(data.get("attacker", "?"))
	var defender = str(data.get("defender", "?"))
	var attacker_alliance = str(data.get("attacker_alliance", "?"))
	var defender_alliance = str(data.get("defender_alliance", "?"))
	var message = str(data.get("message", ""))

	var bbcode = ""
	bbcode += "[center][color=red][b]ALLIANCE PARADOX[/b][/color][/center]\n\n"
	if message:
		bbcode += message + "\n\n"
	else:
		bbcode += "Attacking %s would violate our %s.\n\n" % [defender, defender_alliance]
	bbcode += "[color=gray]Talleyrand: \"A delicate situation, Sire. We cannot attack an ally without consequences.\"[/color]"

	honor_button.text = "Honor " + defender
	break_button.text = "Break " + defender + " Alliance"

	content_label.text = ""
	content_label.append_text(bbcode)
	show()


func _on_honor_pressed():
	honor_button.disabled = true
	break_button.disabled = true
	hide()
	choice_made.emit("honor_defender", _data)


func _on_break_pressed():
	honor_button.disabled = true
	break_button.disabled = true
	hide()
	choice_made.emit("break_defender_alliance", _data)

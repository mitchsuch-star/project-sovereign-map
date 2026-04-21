extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN - Commitment Paradox Popup (Deep Audit Session 8, R15 migrated)
# =============================================================================
# Shown when an attack forces France to choose between competing alliances.
# The player must either honor the defender or break faith with them.
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
	"""Display commitment paradox popup."""
	_data = data
	var attacker = str(data.get("attacker", "?"))
	var defender = str(data.get("defender", "?"))
	var defender_alliance = str(data.get("defender_alliance", "?"))
	var message = str(data.get("message", ""))

	var bbcode = ""
	bbcode += "[center][color=red][b]COMMITMENT PARADOX[/b][/color][/center]\n\n"
	if message:
		bbcode += message + "\n\n"
	else:
		bbcode += "Attacking %s would violate our %s.\n\n" % [defender, defender_alliance]
	bbcode += Utils.bbcode_color(
		"Talleyrand: \"Europe watches how we honor one promise without disgracing another, Sire.\"",
		Utils.COLOR_INFO
	)

	honor_button.text = "Honor " + defender
	break_button.text = "Break " + defender + " Alliance"

	content_label.text = ""
	content_label.append_text(bbcode)
	show()


func _on_honor_pressed():
	close_popup()
	choice_made.emit("honor_defender", _data)


func _on_break_pressed():
	close_popup()
	choice_made.emit("break_defender_alliance", _data)

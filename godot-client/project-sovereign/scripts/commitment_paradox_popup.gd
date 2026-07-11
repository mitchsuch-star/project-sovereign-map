extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN - Commitment Paradox Popup (Deep Audit Session 8, R15 migrated)
# =============================================================================
# Shown when an attack forces France to choose between competing alliances.
# The player must either honor the defender or break faith with them.
# CanvasLayer 100 (modal). Standard registered-dialog popup pattern.
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var honor_button = $PanelContainer/VBoxContainer/ButtonContainer/HonorButton
@onready var break_button = $PanelContainer/VBoxContainer/ButtonContainer/BreakButton

var _data: Dictionary = {}
var _choice_locked: bool = false


func _ready():
	hide()
	honor_button.pressed.connect(_on_honor_pressed)
	break_button.pressed.connect(_on_break_pressed)


func show_paradox(data: Dictionary):
	"""Display commitment paradox popup."""
	_data = data
	_choice_locked = false
	honor_button.visible = true
	break_button.visible = true
	honor_button.disabled = false
	break_button.disabled = false
	var attacker = str(data.get("attacker", "?"))
	var defender = str(data.get("defender", "?"))
	var defender_alliance = str(data.get("defender_alliance", "?"))
	var message = str(data.get("message", ""))
	var attacker_display = Utils.display_nation_name(attacker)
	var defender_display = Utils.display_nation_name(defender)

	var bbcode = ""
	bbcode += "[center][color=red][b]COMMITMENT PARADOX[/b][/color][/center]\n\n"
	if message:
		bbcode += message + "\n\n"
	else:
		bbcode += "Attacking %s would violate our %s.\n\n" % [defender_display, Utils.display_diplo_state(str(defender_alliance)).to_lower()]
	bbcode += Utils.bbcode_color(
		"Talleyrand: \"Europe watches how we honor one promise without disgracing another, Sire.\"",
		Utils.COLOR_INFO
	)

	honor_button.text = "Honor " + defender_display
	break_button.text = "Side with " + attacker_display

	content_label.text = ""
	content_label.append_text(Utils.humanize_nation_keys_in_text(bbcode))
	show()


func _on_honor_pressed():
	if _choice_locked:
		close_popup()
		return
	_show_after_choice_aside("honor_defender")
	choice_made.emit("honor_defender", _data)


func _on_break_pressed():
	if _choice_locked:
		close_popup()
		return
	_show_after_choice_aside("break_defender_alliance")
	choice_made.emit("break_defender_alliance", _data)


func _show_after_choice_aside(choice: String):
	_choice_locked = true
	var attacker = str(_data.get("attacker", "?"))
	var defender = str(_data.get("defender", "?"))
	var spurned = attacker if choice == "honor_defender" else defender
	var diplomat_key = "attacker_diplomat" if choice == "honor_defender" else "defender_diplomat"
	var diplomat = str(_data.get(diplomat_key, ""))
	if diplomat == "":
		diplomat = "The Chancery of " + Utils.display_nation_name(spurned)

	var aside = "\n\n" + Utils.bbcode_color(
		diplomat + ": \"The wound is recorded. Europe will remember which oath France chose.\"",
		Utils.COLOR_ERROR
	)
	aside += "\n" + Utils.bbcode_color(
		"Talleyrand: \"Then let the record show a choice, not confusion.\"",
		Utils.COLOR_INFO
	)
	content_label.append_text(aside)
	honor_button.text = "Continue"
	break_button.visible = false

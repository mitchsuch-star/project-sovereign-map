extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Vassal Rebellion Imminent Popup (Session 8C)
# =============================================================================
# Displays when a vassal's loyalty drops critically low.
# Three buttons: Invest / Send Garrison / Accept Risk
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var invest_btn = $PanelContainer/VBoxContainer/ButtonContainer/InvestButton
@onready var garrison_btn = $PanelContainer/VBoxContainer/ButtonContainer/GarrisonButton
@onready var accept_btn = $PanelContainer/VBoxContainer/ButtonContainer/AcceptButton

var current_data: Dictionary = {}

func _ready():
	hide()
	invest_btn.pressed.connect(_on_invest)
	garrison_btn.pressed.connect(_on_garrison)
	accept_btn.pressed.connect(_on_accept)

func show_rebellion(data: Dictionary):
	"""Display vassal rebellion imminent popup."""
	current_data = data
	var nation = data.get("nation", "Unknown")
	var loyalty = data.get("loyalty", 0)
	var invest_cost = data.get("invest_cost_dp", 1)
	var garrison_cost = data.get("garrison_ap_cost", 2)
	var invest_effect = data.get("invest_effect", "Loyalty +15")
	var garrison_effect = data.get("garrison_effect", "Loyalty +10")
	var accept_effect = data.get("accept_effect", "Rebellion may occur")

	var bbcode = ""
	bbcode += "[b]REBELLION IMMINENT[/b]\n"
	bbcode += "[color=red]%s loyalty: %d/100[/color]\n\n" % [nation, loyalty]
	bbcode += "[b]Invest (%d DP)[/b] — %s\n" % [invest_cost, invest_effect]
	bbcode += "[b]Send Garrison (costs %d AP)[/b] — %s\n" % [garrison_cost, garrison_effect]
	bbcode += "[b]Accept the Risk[/b] — %s" % accept_effect

	content_label.text = ""
	content_label.append_text(bbcode)

	invest_btn.disabled = false
	garrison_btn.disabled = false
	accept_btn.disabled = false
	show()

func _on_invest():
	_disable_buttons()
	hide()
	choice_made.emit("invest", current_data)

func _on_garrison():
	_disable_buttons()
	hide()
	choice_made.emit("garrison", current_data)

func _on_accept():
	_disable_buttons()
	hide()
	choice_made.emit("accept", current_data)

func _disable_buttons():
	invest_btn.disabled = true
	garrison_btn.disabled = true
	accept_btn.disabled = true

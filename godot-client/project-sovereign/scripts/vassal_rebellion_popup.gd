extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Vassal Rebellion Imminent Popup (Session 8C)
# =============================================================================
# Displays when a vassal's loyalty drops critically low.
# Three buttons: Invest / Show the Flag / Accept Risk
# (IQ-7 review [21]: "Send Garrison" promised a corps; none moves. The
# choice id stays "garrison" -> garrison_vassal_rebellion.)
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
	AudioManager.play("bell_toll")  # grave news
	current_data = data
	var nation = data.get("nation", "Unknown")
	var loyalty = data.get("loyalty", 0)
	var invest_cost = data.get("invest_cost_dp", 1)
	var invest_effect = data.get("invest_effect", "Loyalty +15")
	var garrison_effect = data.get("garrison_effect", "%d AP → Loyalty +10 now. No corps moves." % int(data.get("garrison_ap_cost", 2)))
	var accept_effect = data.get("accept_effect", "Rebellion may occur")

	var bbcode = ""
	bbcode += "[b]REBELLION IMMINENT[/b]\n"
	bbcode += "[color=red]%s loyalty: %d/100[/color]\n\n" % [Utils.display_nation_name(str(nation)), loyalty]
	bbcode += "[b]Invest (%d DP)[/b] — %s\n" % [invest_cost, invest_effect]
	# IQ-7 review [21]: the option says what it does — no corps moves (the
	# backend's own copy, which already names the AP cost; the header used
	# to double it and the button used to promise a garrison).
	bbcode += "[b]Show the Flag[/b] — %s\n" % garrison_effect
	bbcode += "[b]Accept the Risk[/b] — %s" % accept_effect

	content_label.text = ""
	content_label.append_text(Utils.humanize_nation_keys_in_text(bbcode))

	invest_btn.disabled = false
	garrison_btn.disabled = false
	accept_btn.disabled = false
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)

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

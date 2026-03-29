extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN - Coalition Declaration Popup (Session 8C, R15 migrated)
# =============================================================================
# Dramatic reveal when a coalition forms against France.
# Single [Continue] button — informational only.
# =============================================================================

signal dismissed

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var continue_btn = $PanelContainer/VBoxContainer/ButtonContainer/ContinueButton

func _ready():
	hide()
	continue_btn.pressed.connect(_on_continue_pressed)

func show_coalition(data: Dictionary):
	"""Display coalition declaration popup."""
	var coalition_name = data.get("coalition_name", "A Coalition")
	var leader = data.get("leader", "Unknown")
	var posture = data.get("posture", "aggressive")
	var combined_str = data.get("combined_strength_display", "???")
	var threat = data.get("threat_level", 0)
	var members = data.get("members", [])

	var bbcode = ""
	bbcode += "[center][color=red][b]⚔ COALITION DECLARED ⚔[/b][/color][/center]\n\n"
	bbcode += "[b]%s[/b] has declared war on France.\n\n" % coalition_name
	bbcode += "[b]Leader:[/b] %s\n" % leader
	bbcode += "[b]Posture:[/b] %s\n" % posture.capitalize()
	bbcode += "[b]Combined Strength:[/b] %s\n\n" % combined_str
	bbcode += "[b]Members:[/b]\n"

	if members.size() == 0:
		bbcode += "  (No members yet)\n"
	else:
		for member in members:
			var nation = member.get("nation", "?")
			var strength = member.get("strength_display", "?")
			var we = int(float(member.get("war_exhaustion", 0)))
			bbcode += "  - %s: %s — War Exhaustion: %d/100\n" % [nation, strength, we]

	bbcode += "\n" + Utils.bbcode_color("Talleyrand: \"The courts of Europe have united against us, Sire.\"", Utils.COLOR_INFO)

	content_label.text = ""
	content_label.append_text(bbcode)
	show()

func _on_continue_pressed():
	close_popup()
	dismissed.emit()

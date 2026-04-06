extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN - Proposal Result Popup (Session 8, PL-5 Part A)
# =============================================================================
# Informational popup showing outcome of player-initiated diplomatic proposals.
# Single [Continue] button — same pattern as coalition_declaration_popup.gd.
# =============================================================================

signal dismissed

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var continue_btn = $PanelContainer/VBoxContainer/ButtonContainer/ContinueButton

func _ready():
	hide()
	continue_btn.pressed.connect(_on_continue_pressed)

func show_result(data: Dictionary):
	"""Display proposal result popup."""
	var target_nation = data.get("target_nation", "Unknown")
	var proposal_type = data.get("proposal_type", "Proposal")
	var outcome = data.get("outcome", "REJECT")
	var message = data.get("message", "")
	var feedback = data.get("feedback", "")

	var bbcode = ""

	if outcome == "ACCEPT":
		bbcode += "[center][color=#50c878][b]PROPOSAL ACCEPTED[/b][/color][/center]\n\n"
	else:
		bbcode += "[center][color=#e04040][b]PROPOSAL REJECTED[/b][/color][/center]\n\n"

	bbcode += "[b]Nation:[/b] %s\n" % target_nation
	bbcode += "[b]Proposal:[/b] %s\n\n" % proposal_type

	if message != "":
		bbcode += "%s\n\n" % message

	if feedback != "":
		bbcode += Utils.bbcode_color("Talleyrand: \"%s\"" % feedback, Utils.COLOR_INFO)

	content_label.text = ""
	content_label.append_text(bbcode)
	# Re-enable button (close_popup disables all buttons via PopupBase)
	continue_btn.disabled = false
	show()

func _on_continue_pressed():
	close_popup()
	dismissed.emit()

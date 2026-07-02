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

func _is_accept_result(data: Dictionary) -> bool:
	var raw_result = str(data.get("outcome", data.get("result", ""))).strip_edges().to_upper()
	if raw_result.find("REJECT") != -1 or raw_result.find("DECLIN") != -1:
		return false
	if raw_result.find("ACCEPT") != -1 or raw_result.find("APPROV") != -1 or raw_result.find("SUCCESS") != -1:
		return true

	var message = str(data.get("message", "")).to_lower()
	if message.find("reject") != -1 or message.find("declin") != -1 or message.find("empty-handed") != -1:
		return false
	if message.find("accept") != -1 or message.find("agreed") != -1:
		return true

	return false

func show_result(data: Dictionary):
	"""Display proposal result popup."""
	var target_nation = data.get("target_nation", "Unknown")
	var proposal_type = data.get("proposal_type", "Proposal")
	var message = data.get("message", "")
	var feedback = data.get("feedback", "")
	var decision_reason_display = data.get("decision_reason_display", "")
	var is_accept = _is_accept_result(data)

	var bbcode = ""

	if is_accept:
		bbcode += "[center][color=#50c878][b]PROPOSAL ACCEPTED[/b][/color][/center]\n\n"
	else:
		bbcode += "[center][color=#e04040][b]PROPOSAL REJECTED[/b][/color][/center]\n\n"

	bbcode += "[b]Nation:[/b] %s\n" % Utils.display_nation_name(str(target_nation))
	bbcode += "[b]Proposal:[/b] %s\n\n" % proposal_type

	if message != "":
		bbcode += "%s\n\n" % message

	if feedback != "":
		bbcode += Utils.bbcode_color("Talleyrand: \"%s\"" % feedback, Utils.COLOR_INFO)
	if decision_reason_display != "":
		bbcode += "\n" + Utils.bbcode_color(
			"Court rationale: %s." % decision_reason_display,
			Utils.COLOR_DIMMED,
		)

	content_label.text = ""
	content_label.append_text(Utils.humanize_nation_keys_in_text(bbcode))
	# Re-enable button (close_popup disables all buttons via PopupBase)
	continue_btn.disabled = false
	show()

func _on_continue_pressed():
	close_popup()
	dismissed.emit()

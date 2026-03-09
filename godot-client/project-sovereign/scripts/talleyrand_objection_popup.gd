extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Talleyrand Objection Popup (Session 8C)
# =============================================================================
# Displays when Talleyrand objects to a diplomatic proposal before sending.
# Three buttons: Proceed Anyway / Modify / Cancel
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var proceed_btn = $PanelContainer/VBoxContainer/ButtonContainer/ProceedButton
@onready var modify_btn = $PanelContainer/VBoxContainer/ButtonContainer/ModifyButton
@onready var cancel_btn = $PanelContainer/VBoxContainer/ButtonContainer/CancelButton

var current_data: Dictionary = {}

# Color map for concern levels
const LEVEL_COLORS = {
	"MILD": "e0c060",
	"MODERATE": "e09040",
	"STRONG": "e04040",
}

func _ready():
	hide()
	proceed_btn.pressed.connect(_on_proceed)
	modify_btn.pressed.connect(_on_modify)
	cancel_btn.pressed.connect(_on_cancel)

func show_objection(data: Dictionary):
	"""Display Talleyrand objection popup."""
	current_data = data
	var concern_level = data.get("concern_level", "MODERATE")
	var objection_text = data.get("objection_text", "Sire, I have concerns.")
	var defiance_risk = data.get("defiance_risk", "Medium")
	var proposal_summary = data.get("proposal_summary", "")

	var level_color = LEVEL_COLORS.get(concern_level, "e09040")

	var bbcode = ""
	bbcode += "[b]TALLEYRAND OBJECTS[/b]\n"
	bbcode += "[color=#%s]%s[/color]\n\n" % [level_color, concern_level]
	bbcode += "\"%s\"\n\n" % objection_text

	# Show proposal terms if enriched
	var terms = data.get("proposal_terms", [])
	if not terms.is_empty():
		bbcode += "[b]Proposed terms:[/b]\n"
		for t in terms:
			bbcode += "  [color=#e0c070]•[/color] %s\n" % str(t)
		bbcode += "\n"

	# Acceptance estimate with color coding
	var acceptance = data.get("acceptance_estimate", -1)
	var outcome = data.get("acceptance_outcome", "")
	if acceptance >= 0:
		var a_color = "#e04040"
		if acceptance >= 50:
			a_color = "#80c080"
		elif acceptance >= 30:
			a_color = "#e0e060"
		bbcode += "Acceptance estimate: [color=%s]~%d%%[/color] (%s)\n" % [a_color, acceptance, outcome]

	bbcode += "[b]Defiance Risk:[/b] %s\n" % defiance_risk
	bbcode += "[b]Regarding:[/b] %s" % proposal_summary

	content_label.text = ""
	content_label.append_text(bbcode)

	proceed_btn.disabled = false
	modify_btn.disabled = false
	cancel_btn.disabled = false
	show()

func _on_proceed():
	_disable_buttons()
	hide()
	choice_made.emit("proceed", current_data)

func _on_modify():
	_disable_buttons()
	hide()
	choice_made.emit("modify", current_data)

func _on_cancel():
	_disable_buttons()
	hide()
	choice_made.emit("cancel", current_data)

func _disable_buttons():
	proceed_btn.disabled = true
	modify_btn.disabled = true
	cancel_btn.disabled = true

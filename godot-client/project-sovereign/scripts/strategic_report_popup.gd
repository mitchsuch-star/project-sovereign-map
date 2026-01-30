extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Strategic Order Report Popup
# =============================================================================
# Displays after enemy phase to show what happened with marshals'
# multi-turn strategic orders (MOVE_TO, PURSUE, HOLD, SUPPORT).
# Shows progress, completions, failures, and blocked paths.
# =============================================================================

signal dismissed

# UI References
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var content_label = $PanelContainer/VBoxContainer/ContentScroll/ContentLabel
@onready var continue_button = $PanelContainer/VBoxContainer/ContinueButton

# Color palette (matching main.gd)
const COLOR_GOLD = "d9c08c"
const COLOR_TEXT = "eeeeee"
const COLOR_SUCCESS = "8fbc8f"
const COLOR_ERROR = "cd6b6b"
const COLOR_BATTLE = "daa06d"
const COLOR_INFO = "a0a0a8"
const COLOR_WARNING = "e0c060"

# Status icons (text-based, no image assets needed)
const STATUS_ICONS = {
	"continues": "->",
	"completed": "[OK]",
	"failed": "[X]",
	"breaks": "[X]",
	"awaiting_response": "[!]",
	"paused": "[||]",
	"error": "[?]",
}

func _ready():
	continue_button.pressed.connect(_on_continue_pressed)
	hide()

func show_reports(reports: Array, turn: int):
	"""Display strategic order reports from turn processing."""
	title_label.text = "STRATEGIC ORDERS - Turn %d" % turn

	var content = ""

	if reports.is_empty():
		content = "[color=#" + COLOR_INFO + "]No active strategic orders.[/color]"
	else:
		for report in reports:
			content += _format_report(report)
			content += "\n"

	content_label.text = content
	show()

func _format_report(report: Dictionary) -> String:
	"""Format a single strategic order report."""
	var result = ""
	var marshal = report.get("marshal", "Unknown")
	var command = report.get("command", "UNKNOWN")
	var status = report.get("order_status", "unknown")
	var message = report.get("message", "")

	# Status icon and color
	var icon = STATUS_ICONS.get(status, "[ ]")
	var color = _get_status_color(status)

	# Header line: icon + marshal + order type
	result += "[color=#" + color + "]" + icon + " " + marshal + "[/color]"
	result += " [color=#" + COLOR_INFO + "](" + command + ")[/color]\n"

	# Message line
	if message:
		result += "[color=#" + COLOR_TEXT + "]   " + message + "[/color]\n"

	# Progress details
	var regions_moved = report.get("regions_moved", [])
	if not regions_moved.is_empty():
		var path_str = " -> ".join(PackedStringArray(regions_moved))
		result += "[color=#" + COLOR_INFO + "]   Moved through: " + path_str + "[/color]\n"

	var destination = report.get("destination", "")
	var turns_remaining = report.get("turns_remaining", -1)
	if destination and turns_remaining >= 0:
		result += "[color=#" + COLOR_INFO + "]   Destination: " + destination
		if turns_remaining > 0:
			result += " (" + str(turns_remaining) + " turns remaining)"
		result += "[/color]\n"

	# Pursuit target info
	var target = report.get("target", "")
	var distance = report.get("distance", -1)
	if target and command == "PURSUE" and distance >= 0:
		result += "[color=#" + COLOR_INFO + "]   Target: " + target
		result += " (" + str(distance) + " regions away)"
		result += "[/color]\n"

	# Support ally info
	var ally = report.get("ally", "")
	if ally and command == "SUPPORT":
		result += "[color=#" + COLOR_INFO + "]   Supporting: " + ally + "[/color]\n"

	# Combat outcome
	var outcome = report.get("outcome", "")
	if outcome:
		var outcome_color = COLOR_SUCCESS if outcome == "victory" else COLOR_ERROR if outcome == "defeat" else COLOR_BATTLE
		result += "[color=#" + outcome_color + "]   Combat: " + outcome.capitalize() + "[/color]\n"

	# Requires input warning
	if report.get("requires_input", false):
		result += "[color=#" + COLOR_WARNING + "]   ** Awaiting your orders **[/color]\n"

	return result

func _get_status_color(status: String) -> String:
	"""Get color for order status."""
	match status:
		"continues":
			return COLOR_GOLD
		"completed":
			return COLOR_SUCCESS
		"failed", "breaks":
			return COLOR_ERROR
		"awaiting_response":
			return COLOR_WARNING
		"paused":
			return COLOR_INFO
		_:
			return COLOR_TEXT

func _on_continue_pressed():
	hide()
	dismissed.emit()

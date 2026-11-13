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

# Session UI-5: the status marks are inline glyphs, not ASCII. Each status maps
# to [kind, name]: "glyph" = a stat glyph (Utils.bb_glyph), "icon" = a Phosphor
# icon (Utils.bb_icon). The meanings are the old marks': ->, [-], [OK], [X],
# [!], [||], [?], [ ].
const STATUS_ICONS = {
	"continues": ["glyph", "march"],
	# LV-4 (row EP F2): the two statuses the tick actually sends had no
	# row, so every standing order rendered the "[ ]" fallback.
	"active": ["glyph", "march"],
	"consumed": ["icon", "minus"],
	"retired": ["icon", "minus"],
	"completed": ["glyph", "medal"],
	"failed": ["icon", "x"],
	"breaks": ["icon", "x"],
	"awaiting_response": ["icon", "warning"],
	"paused": ["icon", "hourglass"],
	"error": ["icon", "question"],
}
const STATUS_ICON_FALLBACK := ["icon", "clock"]
const STATUS_ICON_PX := 18


func _status_icon(status: String, hex: String) -> String:
	"""The inline mark for an order's status, tinted `hex`."""
	var spec: Array = STATUS_ICONS.get(status, STATUS_ICON_FALLBACK)
	if str(spec[0]) == "glyph":
		return Utils.bb_glyph(str(spec[1]), STATUS_ICON_PX, hex)
	return Utils.bb_icon(Utils.ICON_PHOSPHOR + str(spec[1]) + ".svg", STATUS_ICON_PX, hex)


func _ready():
	continue_button.set_meta("no_click_sfx", true)   # its handler plays the departure cue
	continue_button.pressed.connect(_on_continue_pressed)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS still delivers _gui_input.
	content_label.mouse_filter = Control.MOUSE_FILTER_PASS
	hide()

func show_reports(reports: Array, turn: int):
	"""Display strategic order reports from turn processing."""
	title_label.text = "STRATEGIC ORDERS - Turn %d" % turn

	var content = ""

	if reports.is_empty():
		content = "[color=#" + Utils.COLOR_INFO + "]No active strategic orders.[/color]"
	else:
		for report in reports:
			content += _format_report(report)
			content += "\n"

	content_label.text = content
	if not visible:
		AudioManager.play("page_turn")   # the report's leaf, turned
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can push the action row off-screen.
	# Runs AFTER show() so layout has settled.
	Utils.clamp_centered_panel($PanelContainer)

func _format_report(report: Dictionary) -> String:
	"""Format a single strategic order report."""
	var result = ""
	var marshal = Utils.display_marshal_name(str(report.get("marshal", "Unknown")))
	var command = str(report.get("command", "UNKNOWN"))
	# LV-4 (row EP F2): the order's printed name, which the backend stamps
	# on every row (`command_display`); the enum is the fallback only.
	var command_label = str(report.get("command_display", command))
	if command_label == "":
		command_label = command
	var status = report.get("order_status", "unknown")
	var message = report.get("message", "")

	# Status icon and color
	var color = _get_status_color(str(status))
	var icon = _status_icon(str(status), color)

	# Header line: icon + marshal + order type
	result += icon + "[color=#" + color + "] " + marshal + "[/color]"
	result += " [color=#" + Utils.COLOR_INFO + "](" + command_label + ")[/color]\n"

	# Message line
	if message:
		result += "[color=#" + Utils.COLOR_TEXT + "]   " + message + "[/color]\n"

	# Progress details
	var regions_moved = report.get("regions_moved", [])
	if not regions_moved.is_empty():
		var path_str = " → ".join(PackedStringArray(regions_moved))  # LV-19: one arrow
		result += "[color=#" + Utils.COLOR_INFO + "]   Moved through: " + path_str + "[/color]\n"

	var destination = report.get("destination", "")
	# LV-4 (row EP F2): a JSON float rendered raw read "2.0 turns remaining";
	# the count is an int and the noun agrees with it.
	var turns_remaining = int(report.get("turns_remaining", -1))
	if destination and turns_remaining >= 0:
		result += "[color=#" + Utils.COLOR_INFO + "]   Destination: " + Utils.display_marshal_name(str(destination))
		if turns_remaining > 0:
			result += " (" + Utils.plural(turns_remaining, "turn") + " remaining)"
		result += "[/color]\n"

	# Pursuit target info
	var target = report.get("target", "")
	var distance = report.get("distance", -1)
	if target and command == "PURSUE" and distance >= 0:
		result += "[color=#" + Utils.COLOR_INFO + "]   Target: " + target
		result += " (" + Utils.plural(int(distance), "region") + " away)"
		result += "[/color]\n"

	# Support ally info
	var ally = report.get("ally", "")
	if ally and command == "SUPPORT":
		result += "[color=#" + Utils.COLOR_INFO + "]   Supporting: " + ally + "[/color]\n"

	# Combat outcome and battle details
	var outcome = report.get("outcome", "")
	if outcome:
		var outcome_color = Utils.COLOR_SUCCESS if outcome == "victory" else Utils.COLOR_ERROR if outcome == "defeat" else Utils.COLOR_BATTLE
		result += "[color=#" + outcome_color + "]   Combat: " + outcome.capitalize() + "[/color]\n"

	var battle_msg = report.get("battle_message", "")
	if battle_msg:
		result += "[color=#" + Utils.COLOR_TEXT + "]   " + battle_msg + "[/color]\n"

	# Requires input warning
	if report.get("requires_input", false):
		result += "[color=#" + Utils.COLOR_WARNING + "]   ** Awaiting your orders **[/color]\n"

	return result

func _get_status_color(status: String) -> String:
	"""Get color for order status."""
	match status:
		"continues":
			return Utils.COLOR_GOLD
		"completed":
			return Utils.COLOR_SUCCESS
		"failed", "breaks":
			return Utils.COLOR_ERROR
		"awaiting_response":
			return Utils.COLOR_WARNING
		"paused":
			return Utils.COLOR_INFO
		_:
			return Utils.COLOR_TEXT

# July 18, 2026 viewport sweep: a keyboard escape hatch. main.gd's ESC ladder
# deliberately refuses to act while a modal is open, and dialog_manager
# registers this dialog as modal=true — so if a geometry, theme or font change
# ever pushes [Continue] off the bottom, there is literally no way out and the
# turn is lost. Routing through _on_continue_pressed keeps hide()+dismissed
# single-source, so the dismissal is identical to clicking the button.
func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("ui_accept") or event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_on_continue_pressed()

func _on_continue_pressed():
	if visible:
		AudioManager.play("back")
	hide()
	dismissed.emit()

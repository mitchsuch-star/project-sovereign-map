extends Control

# =============================================================================
# PROJECT SOVEREIGN - Notification Rail
# =============================================================================
# Persistent notice rail for informational events. Lives below the top bar so it
# no longer competes with Envoys/DP/threat controls, and expands downward from
# the rail instead of the viewport corner.
# =============================================================================

signal notification_dismissed(notification_id: String)
signal notification_review_requested(review_target: String)

const MAX_VISIBLE_ICONS := 6
const MAX_VISIBLE_COMMITMENTS_PER_TURN := 2
const DETAIL_PANEL_MIN_WIDTH := 280.0
const DETAIL_PANEL_MAX_WIDTH := 340.0
const DETAIL_PANEL_GAP := 6.0

const PRIORITY_COLORS = {
	2: Color(0.85, 0.25, 0.25, 1.0),
	1: Color(0.85, 0.6, 0.2, 1.0),
	0: Color(0.35, 0.55, 0.75, 1.0),
}

const PRIORITY_BORDER_COLORS = {
	2: Color(1.0, 0.4, 0.4, 1.0),
	1: Color(1.0, 0.75, 0.35, 1.0),
	0: Color(0.5, 0.7, 0.9, 1.0),
}

const TYPE_ICONS = {
	"coalition_declared": "WAR",
	"balance_of_europe_shifted": "BOE",
	"amends_offered": "AMD",
	"hard_reject_posture_triggered": "HRT",
	"hard_reject_posture_cleared": "HRC",
	"diplomatic_treaty_broken": "BRK",
	"commitment_paradox": "OAT",
	"commitment_paradox_resolved": "WND",
	"witness_strike_recorded": "EYE",
	"call_to_arms_refused_offensive": "PCT",
	"call_to_arms_refused_defensive": "ALY",
	"call_to_arms_honored_costly": "OAT",
	"bargain_fulfilled": "HON",
	"bargain_breached": "BRK",
	"bargain_voided": "LAP",
	"bargain_ratified": "BAG",
	"bargain_triggered": "ACT",
	"diplomatic_proposal": "ENV",
	"diplomatic_proposal_result": "RPT",
	"treaty_signed": "TRT",
	"treaty_broken": "BRK",
	"war_declared": "WAR",
	"vassal_rebellion": "RBL",
	"vassal_rebellion_imminent": "LOY",
	"dp_insufficient": "DP",
	"turn_limit_warning": "TMR",
	"defeat_imminent_warning": "DNG",
}

const ROUTE_ICON_TEXT = {
	"icon_balance_of_europe": "BOE",
	"icon_amends_offered": "AMD",
	"icon_hard_reject": "HRT",
	"icon_chancery_reopened": "HRC",
	"icon_treaty_broken": "BRK",
	"icon_treaty_dragged": "TRT",
	"icon_paradox": "OAT",
	"icon_paradox_resolved": "WND",
	"icon_witness_strike": "EYE",
	"icon_call_refused_offensive": "PCT",
	"icon_call_refused_defensive": "ALY",
	"icon_call_honored_costly": "OAT",
	"icon_bargain_honoured": "HON",
	"icon_bargain_broken": "BRK",
	"icon_bargain_lapsed": "LAP",
	"icon_bargain_sealed": "BAG",
	"icon_bargain_activated": "ACT",
}

const COMMITMENTS_EVENT_TYPES = {
	"balance_of_europe_shifted": true,
	"amends_offered": true,
	"hard_reject_posture_triggered": true,
	"hard_reject_posture_cleared": true,
	"diplomatic_treaty_broken": true,
	"commitment_paradox": true,
	"commitment_paradox_resolved": true,
	"witness_strike_recorded": true,
	"call_to_arms_refused_offensive": true,
	"call_to_arms_refused_defensive": true,
	"call_to_arms_honored_costly": true,
	"bargain_fulfilled": true,
	"bargain_breached": true,
	"bargain_voided": true,
	"bargain_ratified": true,
	"bargain_triggered": true,
}

@onready var rail_panel: PanelContainer = $RailPanel
@onready var icon_container: HBoxContainer = $RailPanel/RailLayout/IconContainer
@onready var overflow_label: Label = $RailPanel/RailLayout/OverflowLabel

var expanded_panel: PanelContainer = null
var current_notifications: Array = []
var api_client = null
var _suspended: bool = false


func _ready():
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	rail_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	icon_container.mouse_filter = Control.MOUSE_FILTER_IGNORE
	overflow_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_refresh_visibility()


func set_api_client(client):
	api_client = client


func set_suspended(suspended: bool):
	"""Hide the rail while a blocking modal owns focus."""
	_suspended = suspended
	if _suspended:
		_close_expanded_panel()
	_refresh_visibility()


func update_notifications(notifications: Array):
	current_notifications = notifications.duplicate()

	for child in icon_container.get_children():
		icon_container.remove_child(child)
		child.queue_free()

	_close_expanded_panel()

	var rail_notifications = _visible_notifications_for_rail(current_notifications)
	var visible_count = min(rail_notifications.size(), MAX_VISIBLE_ICONS)
	for i in range(visible_count):
		icon_container.add_child(_create_notification_icon(rail_notifications[i]))

	var hidden_count = max(current_notifications.size() - visible_count, 0)
	overflow_label.visible = hidden_count > 0
	overflow_label.text = "+%d" % hidden_count
	overflow_label.tooltip_text = "%d additional notices are queued behind the visible rail." % hidden_count

	_refresh_visibility()


func _refresh_visibility():
	visible = (not _suspended) and not current_notifications.is_empty()


func _create_notification_icon(notif: Dictionary) -> Button:
	var priority = int(notif.get("priority", 0))
	var color = PRIORITY_COLORS.get(priority, PRIORITY_COLORS[0])
	var border_color = PRIORITY_BORDER_COLORS.get(priority, PRIORITY_BORDER_COLORS[0])

	var btn = Button.new()
	btn.custom_minimum_size = Vector2(38, 28)
	btn.text = _icon_text_for(notif)
	btn.tooltip_text = str(notif.get("title", "Notification"))
	btn.mouse_filter = Control.MOUSE_FILTER_STOP
	btn.focus_mode = Control.FOCUS_NONE

	var style = StyleBoxFlat.new()
	style.bg_color = Color(color.r, color.g, color.b, 0.88)
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.border_color = border_color
	style.corner_radius_top_left = 4
	style.corner_radius_top_right = 4
	style.corner_radius_bottom_right = 4
	style.corner_radius_bottom_left = 4
	style.content_margin_left = 4.0
	style.content_margin_right = 4.0
	style.content_margin_top = 2.0
	style.content_margin_bottom = 2.0
	btn.add_theme_stylebox_override("normal", style)

	var hover_style = style.duplicate()
	hover_style.bg_color = Color(
		min(color.r + 0.12, 1.0),
		min(color.g + 0.12, 1.0),
		min(color.b + 0.12, 1.0),
		0.96
	)
	btn.add_theme_stylebox_override("hover", hover_style)

	var pressed_style = style.duplicate()
	pressed_style.bg_color = Color(color.r * 0.8, color.g * 0.8, color.b * 0.8, 0.96)
	btn.add_theme_stylebox_override("pressed", pressed_style)

	btn.add_theme_font_size_override("font_size", 10)
	btn.add_theme_color_override("font_color", Color(1, 1, 1, 1))
	btn.set_meta("notification_data", notif)
	btn.pressed.connect(_on_icon_pressed.bind(btn))
	return btn


func _icon_text_for(notif: Dictionary) -> String:
	var notif_type = str(notif.get("type", ""))
	if TYPE_ICONS.has(notif_type):
		return TYPE_ICONS[notif_type]
	var details = notif.get("details", {})
	if details is Dictionary:
		var icon_key = str(details.get("icon", ""))
		if ROUTE_ICON_TEXT.has(icon_key):
			return ROUTE_ICON_TEXT[icon_key]
	var priority = int(notif.get("priority", 0))
	if priority >= 2:
		return "ALT"
	if priority == 1:
		return "NEW"
	return "INF"


func _visible_notifications_for_rail(notifications: Array) -> Array:
	var visible: Array = []
	var commitments_by_turn := {}
	for notif in notifications:
		if _is_commitments_notice(notif):
			var turn_key = str(int(notif.get("turn_created", 0)))
			var count = int(commitments_by_turn.get(turn_key, 0))
			if count >= MAX_VISIBLE_COMMITMENTS_PER_TURN:
				continue
			commitments_by_turn[turn_key] = count + 1
		visible.append(notif)
		if visible.size() >= MAX_VISIBLE_ICONS:
			break
	return visible


func _is_commitments_notice(notif: Dictionary) -> bool:
	var notif_type = str(notif.get("type", ""))
	if COMMITMENTS_EVENT_TYPES.has(notif_type):
		return true
	var details = notif.get("details", {})
	if details is Dictionary:
		var event_type = str(details.get("event_type", ""))
		return COMMITMENTS_EVENT_TYPES.has(event_type)
	return false


func _on_icon_pressed(btn: Button):
	var notif = btn.get_meta("notification_data")
	if not notif:
		return

	if expanded_panel and expanded_panel.has_meta("notification_id") and expanded_panel.get_meta("notification_id") == notif.get("id", ""):
		_close_expanded_panel()
		return

	_close_expanded_panel()
	_show_expanded_panel(notif)


func _show_expanded_panel(notif: Dictionary):
	var priority = int(notif.get("priority", 0))
	var accent = PRIORITY_BORDER_COLORS.get(priority, PRIORITY_BORDER_COLORS[0])

	expanded_panel = PanelContainer.new()
	expanded_panel.set_meta("notification_id", notif.get("id", ""))
	expanded_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	expanded_panel.custom_minimum_size = Vector2(DETAIL_PANEL_MIN_WIDTH, 0)

	var panel_style = StyleBoxFlat.new()
	panel_style.bg_color = Color(0.04, 0.06, 0.1, 0.98)
	panel_style.border_width_left = 1
	panel_style.border_width_top = 1
	panel_style.border_width_right = 1
	panel_style.border_width_bottom = 1
	panel_style.border_color = accent
	panel_style.corner_radius_top_left = 6
	panel_style.corner_radius_top_right = 6
	panel_style.corner_radius_bottom_right = 6
	panel_style.corner_radius_bottom_left = 6
	panel_style.content_margin_left = 10.0
	panel_style.content_margin_top = 8.0
	panel_style.content_margin_right = 10.0
	panel_style.content_margin_bottom = 10.0
	expanded_panel.add_theme_stylebox_override("panel", panel_style)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 8)
	expanded_panel.add_child(vbox)

	var header = HBoxContainer.new()
	header.add_theme_constant_override("separation", 8)
	vbox.add_child(header)

	var title_label = Label.new()
	title_label.text = str(notif.get("title", "Notification"))
	title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title_label.add_theme_color_override("font_color", accent)
	title_label.add_theme_font_size_override("font_size", 12)
	header.add_child(title_label)

	var turn_created = int(notif.get("turn_created", 0))
	if turn_created > 0:
		var turn_label = Label.new()
		turn_label.text = "T%d" % turn_created
		turn_label.add_theme_color_override("font_color", Color(0.58, 0.58, 0.64, 1))
		turn_label.add_theme_font_size_override("font_size", 10)
		header.add_child(turn_label)

	var body = RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.scroll_active = false
	body.custom_minimum_size = Vector2(DETAIL_PANEL_MIN_WIDTH - 20.0, 0)
	body.text = _build_detail_text(notif)
	vbox.add_child(body)

	var button_row = HBoxContainer.new()
	button_row.alignment = BoxContainer.ALIGNMENT_END
	button_row.add_theme_constant_override("separation", 8)
	vbox.add_child(button_row)

	var details = notif.get("details", {})
	if details is Dictionary:
		var review_target = str(details.get("review_target", ""))
		var review_label = str(details.get("review_label", "Open Ledger"))
		if review_target != "":
			var review_btn = Button.new()
			review_btn.text = review_label
			review_btn.custom_minimum_size = Vector2(92, 28)
			review_btn.add_theme_font_size_override("font_size", 10)
			review_btn.pressed.connect(_on_review_pressed.bind(review_target))
			button_row.add_child(review_btn)

	var keep_btn = Button.new()
	keep_btn.text = "Keep"
	keep_btn.custom_minimum_size = Vector2(64, 28)
	keep_btn.add_theme_font_size_override("font_size", 10)
	keep_btn.pressed.connect(_close_expanded_panel)
	button_row.add_child(keep_btn)

	var dismiss_btn = Button.new()
	dismiss_btn.text = "Acknowledge"
	dismiss_btn.custom_minimum_size = Vector2(92, 28)
	dismiss_btn.add_theme_font_size_override("font_size", 10)
	dismiss_btn.pressed.connect(_on_dismiss_pressed.bind(str(notif.get("id", ""))))
	button_row.add_child(dismiss_btn)

	add_child(expanded_panel)
	_position_expanded_panel.call_deferred()


func _build_detail_text(notif: Dictionary) -> String:
	var text = ""
	var message = str(notif.get("message", "")).strip_edges()
	if message != "":
		text += "[color=#d7d7dc]%s[/color]\n" % message

	var notif_type = str(notif.get("type", ""))
	var details = notif.get("details", {})
	if details is Dictionary:
		match notif_type:
			"coalition_declared":
				text += "\n[color=#e0c060]Leader:[/color] %s\n" % str(details.get("leader", "Unknown"))
				text += "[color=#e0c060]Posture:[/color] %s\n" % str(details.get("posture", "Unknown")).capitalize()
				var combined_strength = int(details.get("combined_strength", 0))
				if combined_strength > 0:
					text += "[color=#e0c060]Combined Strength:[/color] %s\n" % _format_number(combined_strength)
				var members = details.get("members", [])
				if members is Array and not members.is_empty():
					text += "[color=#e0c060]Members:[/color] %s\n" % ", ".join(members)
			"diplomatic_proposal_result":
				text += "\n[color=#e0c060]Nation:[/color] %s\n" % str(details.get("target_nation", "Unknown"))
				text += "[color=#e0c060]Proposal:[/color] %s\n" % str(details.get("proposal_type", "Diplomatic Action"))
				text += "[color=#e0c060]Outcome:[/color] %s\n" % str(details.get("outcome", "Unknown")).capitalize()
				var feedback = str(details.get("feedback", "")).strip_edges()
				if feedback != "":
					text += "\n[color=#8faed6]Talleyrand:[/color] \"%s\"\n" % feedback
			"diplomatic_proposal":
				text += "\n[color=#8faed6]The diplomatic packet waits in Envoys for review.[/color]\n"

	return text.strip_edges()


func _format_number(value: int) -> String:
	var s = str(int(value))
	var result = ""
	var count = 0
	for i in range(s.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			result = "," + result
		result = s[i] + result
		count += 1
	return result


func _position_expanded_panel():
	if not expanded_panel:
		return
	var panel_width = expanded_panel.size.x
	if panel_width <= 0:
		panel_width = DETAIL_PANEL_MIN_WIDTH
	panel_width = clamp(panel_width, DETAIL_PANEL_MIN_WIDTH, DETAIL_PANEL_MAX_WIDTH)
	var local_x = max(0.0, rail_panel.size.x - panel_width)
	expanded_panel.position = Vector2(local_x, rail_panel.size.y + DETAIL_PANEL_GAP)


func _unhandled_input(event):
	if not expanded_panel or _suspended:
		return
	if event is InputEventMouseButton and event.pressed:
		var click_pos = event.position
		var panel_rect = Rect2(expanded_panel.global_position, expanded_panel.size)
		var rail_rect = Rect2(rail_panel.global_position, rail_panel.size)
		if not panel_rect.has_point(click_pos) and not rail_rect.has_point(click_pos):
			_close_expanded_panel()


func _close_expanded_panel():
	if expanded_panel:
		remove_child(expanded_panel)
		expanded_panel.queue_free()
		expanded_panel = null


func _on_dismiss_pressed(notification_id: String):
	_close_expanded_panel()
	current_notifications = current_notifications.filter(
		func(n): return str(n.get("id", "")) != notification_id
	)
	update_notifications(current_notifications)
	if api_client:
		api_client.dismiss_notification(notification_id, func(_response): pass)
	notification_dismissed.emit(notification_id)


func _on_review_pressed(review_target: String):
	_close_expanded_panel()
	notification_review_requested.emit(review_target)


func dismiss_all():
	_close_expanded_panel()
	current_notifications = []
	update_notifications([])
	if api_client:
		api_client.dismiss_all_notifications(func(_response): pass)

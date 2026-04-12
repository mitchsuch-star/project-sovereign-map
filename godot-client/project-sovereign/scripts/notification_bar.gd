extends Control

# =============================================================================
# PROJECT SOVEREIGN - Notification Bar (Phase 6.5)
# =============================================================================
# EU4-style persistent notification icons. Non-blocking, sits at top-right
# below LOG button. Each notification is a small colored icon that expands
# on click to show details. Dismiss with X button.
# =============================================================================

signal notification_dismissed(notification_id: String)

# Priority colors (match backend NotificationPriority enum values)
const PRIORITY_COLORS = {
	2: Color(0.85, 0.25, 0.25, 1.0),   # CRITICAL — red
	1: Color(0.85, 0.6, 0.2, 1.0),     # HIGH — orange
	0: Color(0.35, 0.55, 0.75, 1.0),   # NORMAL — blue
}

# Priority border colors (lighter variants for icon borders)
const PRIORITY_BORDER_COLORS = {
	2: Color(1.0, 0.4, 0.4, 1.0),
	1: Color(1.0, 0.75, 0.35, 1.0),
	0: Color(0.5, 0.7, 0.9, 1.0),
}

# Priority icons (text characters for icon buttons)
const PRIORITY_ICONS = {
	2: "!!",   # CRITICAL
	1: "!",    # HIGH
	0: "i",    # NORMAL
}
const DETAIL_PANEL_MIN_WIDTH := 240.0
const DETAIL_PANEL_MAX_WIDTH := 300.0
const DETAIL_PANEL_TOP_OFFSET := 42.0
const VIEWPORT_EDGE_MARGIN := 14.0

@onready var icon_container: HBoxContainer = $IconContainer
var expanded_panel: PanelContainer = null
var current_notifications: Array = []
var api_client = null


func _ready():
	# Start hidden — only show when notifications exist
	visible = false
	# Wrapper controls should not eat clicks outside the actual icon buttons.
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	icon_container.mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_api_client(client):
	"""Set the API client reference for dismiss calls."""
	api_client = client


func update_notifications(notifications: Array):
	"""Replace all notification icons with the provided list."""
	current_notifications = notifications

	# Clear existing icons
	for child in icon_container.get_children():
		icon_container.remove_child(child)
		child.queue_free()

	# Close expanded panel if open
	_close_expanded_panel()

	if notifications.is_empty():
		visible = false
		return

	visible = true

	# Create icon buttons sorted by priority (CRITICAL first)
	for notif in notifications:
		var btn = _create_notification_icon(notif)
		icon_container.add_child(btn)


func _create_notification_icon(notif: Dictionary) -> Button:
	"""Create a small colored icon button for a notification."""
	var priority = int(notif.get("priority", 0))
	var color = PRIORITY_COLORS.get(priority, PRIORITY_COLORS[0])
	var border_color = PRIORITY_BORDER_COLORS.get(priority, PRIORITY_BORDER_COLORS[0])
	var icon_text = PRIORITY_ICONS.get(priority, "i")

	var btn = Button.new()
	btn.custom_minimum_size = Vector2(28, 28)
	btn.text = icon_text
	btn.tooltip_text = str(notif.get("title", "Notification"))
	btn.mouse_filter = Control.MOUSE_FILTER_STOP

	# Style the button
	var style = StyleBoxFlat.new()
	style.bg_color = Color(color.r, color.g, color.b, 0.85)
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

	# Hover style (brighter)
	var hover_style = style.duplicate()
	hover_style.bg_color = Color(color.r * 1.2, color.g * 1.2, color.b * 1.2, 0.95)
	btn.add_theme_stylebox_override("hover", hover_style)

	# Pressed style
	var pressed_style = style.duplicate()
	pressed_style.bg_color = Color(color.r * 0.8, color.g * 0.8, color.b * 0.8, 0.95)
	btn.add_theme_stylebox_override("pressed", pressed_style)

	btn.add_theme_font_size_override("font_size", 11)
	btn.add_theme_color_override("font_color", Color(1, 1, 1, 1))

	# Store notification data on the button
	btn.set_meta("notification_data", notif)
	btn.pressed.connect(_on_icon_pressed.bind(btn))

	return btn


func _on_icon_pressed(btn: Button):
	"""Expand notification details when icon is clicked."""
	var notif = btn.get_meta("notification_data")
	if not notif:
		return

	# Toggle: if already showing this notification, close it
	if expanded_panel and expanded_panel.has_meta("notification_id") and expanded_panel.get_meta("notification_id") == notif.get("id", ""):
		_close_expanded_panel()
		return

	_close_expanded_panel()
	_show_expanded_panel(notif)


func _show_expanded_panel(notif: Dictionary):
	"""Show expanded notification details as a compact top-right drawer."""
	var priority = int(notif.get("priority", 0))
	var color = PRIORITY_COLORS.get(priority, PRIORITY_COLORS[0])
	var border_color = PRIORITY_BORDER_COLORS.get(priority, PRIORITY_BORDER_COLORS[0])

	expanded_panel = PanelContainer.new()
	expanded_panel.set_meta("notification_id", notif.get("id", ""))
	expanded_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	expanded_panel.custom_minimum_size = Vector2(DETAIL_PANEL_MIN_WIDTH, 0)

	# Style the panel
	var panel_style = StyleBoxFlat.new()
	panel_style.bg_color = Color(0.05, 0.07, 0.1, 0.97)
	panel_style.border_width_left = 1
	panel_style.border_width_top = 1
	panel_style.border_width_right = 1
	panel_style.border_width_bottom = 1
	panel_style.border_color = border_color
	panel_style.corner_radius_top_left = 6
	panel_style.corner_radius_top_right = 6
	panel_style.corner_radius_bottom_right = 6
	panel_style.corner_radius_bottom_left = 6
	panel_style.content_margin_left = 10.0
	panel_style.content_margin_top = 8.0
	panel_style.content_margin_right = 10.0
	panel_style.content_margin_bottom = 9.0
	expanded_panel.add_theme_stylebox_override("panel", panel_style)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 6)
	expanded_panel.add_child(vbox)

	# Header row: title + dismiss button
	var header = HBoxContainer.new()
	vbox.add_child(header)

	var title_label = Label.new()
	title_label.text = str(notif.get("title", "Notification"))
	title_label.add_theme_color_override("font_color", color)
	title_label.add_theme_font_size_override("font_size", 12)
	title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title_label)

	# Turn indicator (between title and dismiss button)
	var turn_created = notif.get("turn_created", 0)
	if turn_created > 0:
		var turn_label = Label.new()
		turn_label.text = "(Turn " + str(int(turn_created)) + ")"
		turn_label.add_theme_color_override("font_color", Color(0.58, 0.58, 0.64, 1))
		turn_label.add_theme_font_size_override("font_size", 10)
		header.add_child(turn_label)

	var dismiss_btn = Button.new()
	dismiss_btn.text = "Close"
	dismiss_btn.custom_minimum_size = Vector2(52, 24)
	dismiss_btn.add_theme_font_size_override("font_size", 10)
	dismiss_btn.add_theme_color_override("font_color", Color(0.7, 0.7, 0.75, 1))
	dismiss_btn.pressed.connect(_on_dismiss_pressed.bind(notif.get("id", "")))
	header.add_child(dismiss_btn)

	# Message body
	var message_label = Label.new()
	message_label.text = str(notif.get("message", ""))
	message_label.add_theme_color_override("font_color", Color(0.83, 0.83, 0.86, 1))
	message_label.add_theme_font_size_override("font_size", 11)
	message_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	message_label.custom_minimum_size = Vector2(DETAIL_PANEL_MIN_WIDTH - 20.0, 0)
	vbox.add_child(message_label)

	# Position panel below the notification bar, right-aligned so it doesn't overflow the screen
	add_child(expanded_panel)
	# Defer positioning so the panel's size is calculated first
	_position_expanded_panel.call_deferred()


func _position_expanded_panel():
	"""Anchor the drawer to the top-right of the viewport, not over Envoys."""
	if expanded_panel:
		var viewport_size = get_viewport_rect().size
		var panel_width = expanded_panel.size.x
		if panel_width <= 0:
			panel_width = DETAIL_PANEL_MIN_WIDTH
		panel_width = clamp(panel_width, DETAIL_PANEL_MIN_WIDTH, DETAIL_PANEL_MAX_WIDTH)
		var target_global_x = max(
			VIEWPORT_EDGE_MARGIN,
			viewport_size.x - panel_width - VIEWPORT_EDGE_MARGIN
		)
		var local_x = target_global_x - global_position.x
		expanded_panel.position = Vector2(local_x, DETAIL_PANEL_TOP_OFFSET)


func _unhandled_input(event):
	"""Clicking elsewhere closes the expanded drawer."""
	if not expanded_panel:
		return
	if event is InputEventMouseButton and event.pressed:
		var click_pos = event.position
		var panel_rect = Rect2(expanded_panel.global_position, expanded_panel.size)
		var bar_rect = Rect2(global_position, size)
		if not panel_rect.has_point(click_pos) and not bar_rect.has_point(click_pos):
			_close_expanded_panel()


func _close_expanded_panel():
	"""Close the expanded detail panel."""
	if expanded_panel:
		remove_child(expanded_panel)
		expanded_panel.queue_free()
		expanded_panel = null


func _on_dismiss_pressed(notification_id: String):
	"""Dismiss a notification — remove locally and tell backend."""
	_close_expanded_panel()

	# Remove from local list
	current_notifications = current_notifications.filter(
		func(n): return n.get("id", "") != notification_id
	)

	# Refresh icons
	update_notifications(current_notifications)

	# Tell backend
	if api_client:
		api_client.dismiss_notification(notification_id, func(_response): pass)

	notification_dismissed.emit(notification_id)


func dismiss_all():
	"""Dismiss all notifications."""
	_close_expanded_panel()
	current_notifications = []
	update_notifications([])
	if api_client:
		api_client.dismiss_all_notifications(func(_response): pass)

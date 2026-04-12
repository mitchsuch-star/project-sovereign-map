extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Top Bar Controller (Session A)
# =============================================================================
# Unified top bar framework. CanvasLayer 75 with buttons + notification area +
# turn counter. Manages information screens (layer 50) — one screen at a time.
# =============================================================================

signal screen_changed(screen_name: String)

# UI References — paths must match scene tree: BarContainer > BarBG > BarLayout > ...
@onready var event_log_btn: Button = $BarContainer/BarBG/BarLayout/ScreenButtons/EventLogBtn
@onready var ledger_btn: Button = $BarContainer/BarBG/BarLayout/ScreenButtons/LedgerBtn
@onready var generals_btn: Button = $BarContainer/BarBG/BarLayout/ScreenButtons/GeneralsBtn
@onready var diplo_ledger_btn: Button = $BarContainer/BarBG/BarLayout/ScreenButtons/DiploLedgerBtn
@onready var dispatch_btn: Button = $BarContainer/BarBG/BarLayout/ScreenButtons/DispatchBtn
@onready var notification_area: Control = $BarContainer/BarBG/BarLayout/RightSection/NotificationArea
@onready var turn_label: Label = $BarContainer/BarBG/BarLayout/RightSection/TurnLabel

# Diplomatic top bar fields (Session 8B)
@onready var dp_label: Label = $BarContainer/BarBG/BarLayout/RightSection/DPLabel
@onready var threat_label: Label = $BarContainer/BarBG/BarLayout/RightSection/ThreatLabel
@onready var talleyrand_label: Label = $BarContainer/BarBG/BarLayout/RightSection/TalleyrandLabel
@onready var mailbox_btn: Button = $BarContainer/BarBG/BarLayout/RightSection/MailboxButton

# State tracking
var active_screen: String = ""  # "" = none, "event_log", "ledger", "generals", "diplomatic_ledger", "dispatch"
var screens: Dictionary = {}    # maps screen name -> node reference
var api_client = null

# Threat pulse state (Session 8B)
var _threat_pulse_timer: Timer = null
var _threat_pulsing: bool = false

# Button -> screen name mapping
var button_map: Dictionary = {}

# Active button style
var _active_style: StyleBoxFlat = null
var _normal_style: StyleBoxFlat = null
var _mailbox_idle_style: StyleBoxFlat = null
var _mailbox_idle_hover_style: StyleBoxFlat = null
var _mailbox_alert_style: StyleBoxFlat = null
var _mailbox_alert_hover_style: StyleBoxFlat = null
var _mailbox_pressed_style: StyleBoxFlat = null

func _ready():
	# Build button styles
	_active_style = StyleBoxFlat.new()
	_active_style.bg_color = Color(0.25, 0.22, 0.15, 1.0)
	_active_style.border_width_bottom = 2
	_active_style.border_color = Color(0.85, 0.75, 0.55, 1.0)
	_active_style.content_margin_left = 8.0
	_active_style.content_margin_right = 8.0
	_active_style.content_margin_top = 4.0
	_active_style.content_margin_bottom = 4.0

	_normal_style = StyleBoxFlat.new()
	_normal_style.bg_color = Color(0.12, 0.14, 0.18, 1.0)
	_normal_style.content_margin_left = 8.0
	_normal_style.content_margin_right = 8.0
	_normal_style.content_margin_top = 4.0
	_normal_style.content_margin_bottom = 4.0

	_mailbox_idle_style = StyleBoxFlat.new()
	_mailbox_idle_style.bg_color = Color(0.1, 0.12, 0.16, 0.9)
	_mailbox_idle_style.border_width_left = 1
	_mailbox_idle_style.border_width_top = 1
	_mailbox_idle_style.border_width_right = 1
	_mailbox_idle_style.border_width_bottom = 1
	_mailbox_idle_style.border_color = Color(0.32, 0.35, 0.42, 0.9)
	_mailbox_idle_style.corner_radius_top_left = 4
	_mailbox_idle_style.corner_radius_top_right = 4
	_mailbox_idle_style.corner_radius_bottom_right = 4
	_mailbox_idle_style.corner_radius_bottom_left = 4
	_mailbox_idle_style.content_margin_left = 10.0
	_mailbox_idle_style.content_margin_right = 10.0
	_mailbox_idle_style.content_margin_top = 4.0
	_mailbox_idle_style.content_margin_bottom = 4.0

	_mailbox_idle_hover_style = _mailbox_idle_style.duplicate()
	_mailbox_idle_hover_style.bg_color = Color(0.16, 0.18, 0.23, 0.95)

	_mailbox_alert_style = _mailbox_idle_style.duplicate()
	_mailbox_alert_style.bg_color = Color(0.23, 0.18, 0.08, 0.95)
	_mailbox_alert_style.border_color = Color(0.85, 0.65, 0.2, 0.95)

	_mailbox_alert_hover_style = _mailbox_alert_style.duplicate()
	_mailbox_alert_hover_style.bg_color = Color(0.3, 0.22, 0.08, 1.0)

	_mailbox_pressed_style = _mailbox_idle_style.duplicate()
	_mailbox_pressed_style.bg_color = Color(0.08, 0.1, 0.14, 1.0)

	# Connect button signals
	event_log_btn.pressed.connect(_on_button_pressed.bind("event_log"))
	ledger_btn.pressed.connect(_on_button_pressed.bind("ledger"))
	generals_btn.pressed.connect(_on_button_pressed.bind("generals"))
	diplo_ledger_btn.pressed.connect(_on_button_pressed.bind("diplomatic_ledger"))
	dispatch_btn.pressed.connect(_on_button_pressed.bind("dispatch"))

	# Map buttons to screen names
	button_map = {
		"event_log": event_log_btn,
		"ledger": ledger_btn,
		"generals": generals_btn,
		"diplomatic_ledger": diplo_ledger_btn,
		"dispatch": dispatch_btn,
	}

	# Generals button — wired to Marshal Management screen (Phase 6.5)
	generals_btn.disabled = false

	# Apply normal style to all buttons
	for btn in button_map.values():
		btn.add_theme_stylebox_override("normal", _normal_style)

	# Initialize turn label
	turn_label.text = "Turn 1"

	# Initialize diplomatic fields (Session 8B)
	dp_label.text = "DP: 0/3"
	threat_label.text = ""
	threat_label.visible = false
	talleyrand_label.text = "Talleyrand: Idle"
	update_mailbox_count(0)
	mailbox_btn.add_theme_stylebox_override("pressed", _mailbox_pressed_style)

	# Notification wrappers should not block unrelated HUD clicks.
	notification_area.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Mailbox button click handler
	mailbox_btn.pressed.connect(_on_mailbox_pressed)

	# Threat pulse timer
	_threat_pulse_timer = Timer.new()
	_threat_pulse_timer.wait_time = 0.5
	_threat_pulse_timer.timeout.connect(_on_threat_pulse)
	add_child(_threat_pulse_timer)


func set_api_client(client):
	"""Set the API client reference for screens to use."""
	api_client = client


func register_screen(screen_name: String, node: Node):
	"""Register a screen node. Called during main.gd _ready() setup."""
	screens[screen_name] = node
	# Listen for screen's own close signal (X button, overlay click)
	if node.has_signal("closed"):
		node.closed.connect(_on_screen_closed.bind(screen_name))


func toggle_screen(screen_name: String):
	"""Toggle a screen: close if open, open if closed (closing current first)."""
	if active_screen == screen_name:
		# Toggle off — close the active screen
		_close_screen(screen_name)
	else:
		# Close current screen first (one at a time rule)
		if active_screen != "":
			_close_screen(active_screen)
		# Open the new screen
		_open_screen(screen_name)


func close_all_screens():
	"""Close whatever screen is open. Called on turn transitions."""
	if active_screen != "":
		_close_screen(active_screen)


func is_screen_open() -> bool:
	"""True when any top bar screen is visible."""
	return active_screen != ""


func get_active_screen() -> String:
	"""Return the name of the active screen, or empty string."""
	return active_screen


func update_turn(turn_number: int):
	"""Update the turn counter label."""
	turn_label.text = "Turn " + str(int(turn_number))


func _open_screen(screen_name: String):
	"""Open a screen by name."""
	if not screens.has(screen_name):
		return
	var node = screens[screen_name]
	if node == null:
		return

	active_screen = screen_name

	# Open the screen — each screen fetches its own data
	if node.has_method("open_log"):
		# Campaign log uses open_log(api_client)
		node.open_log(api_client)
	elif node.has_method("open"):
		node.open(api_client)
	else:
		node.show()

	_update_button_highlights()
	screen_changed.emit(active_screen)


func _close_screen(screen_name: String):
	"""Close a screen by name."""
	if not screens.has(screen_name):
		return
	var node = screens[screen_name]
	if node == null:
		return

	# Clear active BEFORE calling close method to prevent double screen_changed
	# emission (close_log/close_view emit 'closed' signal -> _on_screen_closed
	# checks active_screen == name, which will be false since we cleared it)
	active_screen = ""

	# Close the screen
	if node.has_method("close_log"):
		node.close_log()
	elif node.has_method("close_view"):
		node.close_view()
	else:
		node.hide()

	_update_button_highlights()
	screen_changed.emit(active_screen)


func _on_button_pressed(screen_name: String):
	"""Handle a top bar button click."""
	# Generals is a placeholder — guard against it
	if screen_name == "generals" and (not screens.has("generals") or screens["generals"] == null):
		return
	toggle_screen(screen_name)


func _on_screen_closed(screen_name: String):
	"""Handle a screen closing itself (X button, overlay click)."""
	if active_screen == screen_name:
		active_screen = ""
		_update_button_highlights()
		screen_changed.emit(active_screen)


func _update_button_highlights():
	"""Set the active button to highlighted style, all others to normal."""
	for sname in button_map:
		var btn = button_map[sname]
		if sname == active_screen:
			btn.add_theme_stylebox_override("normal", _active_style)
			btn.add_theme_color_override("font_color", Color(0.85, 0.75, 0.55, 1.0))
		else:
			btn.add_theme_stylebox_override("normal", _normal_style)
			btn.add_theme_color_override("font_color", Color(0.75, 0.72, 0.65, 1.0))


# =============================================================================
# DIPLOMATIC TOP BAR FIELDS (Session 8B)
# =============================================================================

signal envoy_clicked

func update_diplomatic_fields(data: Dictionary):
	"""Update all diplomatic top bar fields from /test poll data."""
	# DP counter
	var dp = int(data.get("diplomatic_points", 0))
	var dp_max = int(data.get("max_diplomatic_points", 3))
	dp_label.text = "DP: " + str(dp) + "/" + str(dp_max)

	# Threat indicator
	var threat = int(data.get("threat_level", 0))
	var brewing = data.get("coalition_brewing", false)
	if threat < 30:
		threat_label.visible = false
		_stop_threat_pulse()
	elif threat < 60:
		threat_label.visible = true
		threat_label.text = "[THREAT]"
		threat_label.add_theme_color_override("font_color", Color(0.85, 0.65, 0.2, 1.0))
		if brewing:
			_start_threat_pulse()
		else:
			_stop_threat_pulse()
	else:
		threat_label.visible = true
		threat_label.text = "[THREAT!]"
		threat_label.add_theme_color_override("font_color", Color(0.85, 0.25, 0.25, 1.0))
		if brewing:
			_start_threat_pulse()
		else:
			_stop_threat_pulse()

	# Talleyrand status
	var mission_summary = str(data.get("talleyrand_mission_summary", "Idle"))
	if mission_summary == "" or mission_summary == "null":
		mission_summary = "Idle"
	talleyrand_label.text = "Talleyrand: " + mission_summary

	update_mailbox_count(int(data.get("pending_envoy_count", 0)))


var _current_envoy_count: int = 0

func get_envoy_count() -> int:
	return _current_envoy_count

func update_mailbox_count(envoy_count: int):
	"""Refresh the envoys button copy and styling."""
	_current_envoy_count = envoy_count
	if envoy_count > 0:
		mailbox_btn.text = "Envoys (" + str(envoy_count) + ")"
		mailbox_btn.tooltip_text = str(envoy_count) + " pending envoy(s) await your reply."
		mailbox_btn.add_theme_stylebox_override("normal", _mailbox_alert_style)
		mailbox_btn.add_theme_stylebox_override("hover", _mailbox_alert_hover_style)
		mailbox_btn.add_theme_color_override("font_color", Color(0.85, 0.65, 0.2, 1.0))
	else:
		mailbox_btn.text = "Envoys"
		mailbox_btn.tooltip_text = "No pending envoys."
		mailbox_btn.add_theme_stylebox_override("normal", _mailbox_idle_style)
		mailbox_btn.add_theme_stylebox_override("hover", _mailbox_idle_hover_style)
		mailbox_btn.add_theme_color_override("font_color", Color(0.72, 0.72, 0.76, 1.0))


func _start_threat_pulse():
	"""Start the threat indicator pulsing."""
	if not _threat_pulsing:
		_threat_pulsing = true
		_threat_pulse_timer.start()


func _stop_threat_pulse():
	"""Stop the threat indicator pulsing."""
	if _threat_pulsing:
		_threat_pulsing = false
		_threat_pulse_timer.stop()
		threat_label.modulate = Color(1, 1, 1, 1)


func _on_threat_pulse():
	"""Toggle threat label visibility for pulse effect."""
	if threat_label.modulate.a > 0.5:
		threat_label.modulate = Color(1, 1, 1, 0.3)
	else:
		threat_label.modulate = Color(1, 1, 1, 1.0)


func _on_mailbox_pressed():
	"""Emit the mailbox click signal for main.gd to handle."""
	envoy_clicked.emit()

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
@onready var dispatch_btn: Button = $BarContainer/BarBG/BarLayout/ScreenButtons/DispatchBtn
@onready var notification_area: Control = $BarContainer/BarBG/BarLayout/RightSection/NotificationArea
@onready var turn_label: Label = $BarContainer/BarBG/BarLayout/RightSection/TurnLabel

# State tracking
var active_screen: String = ""  # "" = none, "event_log", "ledger", "generals", "dispatch"
var screens: Dictionary = {}    # maps screen name -> node reference
var api_client = null

# Button -> screen name mapping
var button_map: Dictionary = {}

# Active button style
var _active_style: StyleBoxFlat = null
var _normal_style: StyleBoxFlat = null

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

	# Connect button signals
	event_log_btn.pressed.connect(_on_button_pressed.bind("event_log"))
	ledger_btn.pressed.connect(_on_button_pressed.bind("ledger"))
	generals_btn.pressed.connect(_on_button_pressed.bind("generals"))
	dispatch_btn.pressed.connect(_on_button_pressed.bind("dispatch"))

	# Map buttons to screen names
	button_map = {
		"event_log": event_log_btn,
		"ledger": ledger_btn,
		"generals": generals_btn,
		"dispatch": dispatch_btn,
	}

	# Generals button — wired to Marshal Management screen (Phase 6.5)
	generals_btn.disabled = false

	# Apply normal style to all buttons
	for btn in button_map.values():
		btn.add_theme_stylebox_override("normal", _normal_style)

	# Initialize turn label
	turn_label.text = "Turn 1"


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

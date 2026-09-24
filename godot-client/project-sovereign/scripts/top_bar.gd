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
# HC-G: Le Moniteur — the Gazette's archive screen.
@onready var gazette_btn: Button = $BarContainer/BarBG/BarLayout/ScreenButtons/GazetteBtn
@onready var notification_area: Control = $NotificationArea
@onready var turn_label: Label = $BarContainer/BarBG/BarLayout/RightSection/TurnLabel

# Diplomatic top bar fields (Session 8B)
@onready var dp_label: Label = $BarContainer/BarBG/BarLayout/RightSection/DPLabel
@onready var threat_label: Label = $BarContainer/BarBG/BarLayout/RightSection/ThreatLabel
@onready var talleyrand_label: Label = $BarContainer/BarBG/BarLayout/RightSection/TalleyrandLabel
@onready var mailbox_btn: Button = $BarContainer/BarBG/BarLayout/RightSection/MailboxButton
# NUI "The Admiralty on the Map": the fleet's standing line, hidden on a
# world with no naval theatre; a click opens THE ADMIRALTY (ledger tab 7).
@onready var admiralty_btn: Button = $BarContainer/BarBG/BarLayout/RightSection/AdmiraltyBtn
# UI-6: the pause menu finally gets a clickable entry point (was ESC-only)
@onready var menu_btn: Button = $BarContainer/BarBG/BarLayout/RightSection/MenuBtn

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
const TALLEYRAND_SUMMARY_MAX_CHARS := 34
# IQ10-X1 (routed to "the next UI slice" — this one): at Interface Scale
# 2.0 the logical viewport is 800px wide and the bar's content grew past
# it — EventLogBtn measured at x=-26 (boot) and x=-65 with a mission
# standing, off the left edge, while MenuBtn sat at x=798. Below this
# width the bar goes COMPACT: nav buttons keep their tinted icon and
# drop their text (the tooltip still names the screen and both
# hotkeys), the Cabinet line hides (its full text lives on the Ledger),
# and the Admiralty chip shows the sail count alone.
const COMPACT_BELOW_PX := 1180.0
# PC15-18's hint table, hoisted so the compact bar can fall back on the
# bare letter for a button whose icon did not load (never a blank square).
const HOTKEY_HINTS := {
	"event_log": "L", "ledger": "T", "generals": "G",
	"diplomatic_ledger": "D", "dispatch": "R", "gazette": "N",
}
var _nav_full_text := {}
var _compact := false

func _ready():
	# Build button styles
	_active_style = StyleBoxFlat.new()
	_active_style.bg_color = Utils.UI_ACTIVE_TAB_BG
	_active_style.border_width_bottom = 2
	_active_style.border_color = Utils.UI_GOLD
	_active_style.content_margin_left = 8.0
	_active_style.content_margin_right = 8.0
	_active_style.content_margin_top = 4.0
	_active_style.content_margin_bottom = 4.0

	_normal_style = StyleBoxFlat.new()
	_normal_style.bg_color = Utils.UI_PANEL_BG
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
	gazette_btn.pressed.connect(_on_button_pressed.bind("gazette"))

	# Map buttons to screen names
	button_map = {
		"event_log": event_log_btn,
		"ledger": ledger_btn,
		"generals": generals_btn,
		"diplomatic_ledger": diplo_ledger_btn,
		"dispatch": dispatch_btn,
		"gazette": gazette_btn,
	}

	# Generals button — wired to Marshal Management screen (Phase 6.5)
	generals_btn.disabled = false

	# PC15-18: name the focus-safe hotkey form. The bare letter works only
	# while the command line is unfocused (typing must type); Alt+<key>
	# works even mid-sentence (main.gd _on_command_input_gui_input).
	for sname in HOTKEY_HINTS:
		var key: String = HOTKEY_HINTS[sname]
		# IQ10-X1: the tooltip names the SCREEN too, because in the compact
		# bar the button's own text is gone and the icon is all that shows.
		var screen_title: String = button_map[sname].text.split(" (")[0]
		button_map[sname].tooltip_text = (
			screen_title + " — " + key + ", or Alt+" + key + " while typing")

	# Apply normal style to all buttons
	for btn in button_map.values():
		btn.add_theme_stylebox_override("normal", _normal_style)

	# UI-3: a tinted leading icon per nav button (labels + hotkey hints kept).
	Utils.apply_button_icon(event_log_btn, Utils.ICON_PHOSPHOR + "list.svg")
	Utils.apply_button_icon(ledger_btn, Utils.ICON_PHOSPHOR + "map-trifold.svg")
	Utils.apply_button_icon(generals_btn, Utils.ICON_PHOSPHOR + "users-three.svg")
	Utils.apply_button_icon(diplo_ledger_btn, Utils.ICON_PHOSPHOR + "handshake.svg")
	Utils.apply_button_icon(dispatch_btn, Utils.ICON_PHOSPHOR + "scroll.svg")
	# (no newspaper glyph in the curated set — the open book reads as
	# the periodical's archive)
	Utils.apply_button_icon(gazette_btn, Utils.ICON_PHOSPHOR + "book-open.svg")

	# UI-6: nav hover/pressed match the flat bar look — without these the
	# theme's gold-bordered navy stylebox flashed in on hover (style-jump).
	var nav_hover_style: StyleBoxFlat = _normal_style.duplicate()
	nav_hover_style.bg_color = Utils.UI_ACTIVE_TAB_BG
	var nav_pressed_style: StyleBoxFlat = _normal_style.duplicate()
	nav_pressed_style.bg_color = Color(
		Utils.UI_PANEL_BG.r * 0.8, Utils.UI_PANEL_BG.g * 0.8,
		Utils.UI_PANEL_BG.b * 0.8, 1.0)
	for nav_btn in button_map.values():
		nav_btn.add_theme_stylebox_override("hover", nav_hover_style)
		nav_btn.add_theme_stylebox_override("pressed", nav_pressed_style)

	# UI-6: gear button → pause menu (Save/Load/Settings)
	Utils.apply_icon_only_button(menu_btn, Utils.ICON_PHOSPHOR + "gear.svg")
	menu_btn.pressed.connect(func(): menu_clicked.emit())

	# Initialize turn label
	turn_label.text = "Turn 1"

	# Initialize diplomatic fields (Session 8B)
	dp_label.text = "DP: 0/3"
	threat_label.text = ""
	threat_label.visible = false
	_set_talleyrand_summary("Idle")
	update_mailbox_count(0)
	mailbox_btn.add_theme_stylebox_override("pressed", _mailbox_pressed_style)

	# Notification wrappers should not block unrelated HUD clicks.
	notification_area.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Mailbox button click handler
	mailbox_btn.pressed.connect(_on_mailbox_pressed)

	# NUI: the Admiralty chip — styled like the mailbox button, hidden
	# until a naval world reports a fleet line, opens the ledger's book 7.
	if admiralty_btn:
		admiralty_btn.add_theme_stylebox_override("normal", _mailbox_idle_style)
		admiralty_btn.add_theme_stylebox_override("hover", _mailbox_idle_hover_style)
		admiralty_btn.add_theme_stylebox_override("pressed", _mailbox_pressed_style)
		admiralty_btn.pressed.connect(func(): admiralty_clicked.emit())
		admiralty_btn.visible = false

	# IQ10-X1: the bar fits itself to the logical viewport, now and on every
	# resize (an Interface Scale change resizes the logical viewport too).
	for sname in button_map:
		_nav_full_text[sname] = button_map[sname].text
	get_viewport().size_changed.connect(_fit_bar)
	call_deferred("_fit_bar")

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


func open_diplomatic_ledger_review(review_target: String, route_id: String = "", war_id: String = ""):
	"""Open the diplomatic ledger to a named review target."""
	var screen_name = "diplomatic_ledger"
	if not screens.has(screen_name):
		return
	if active_screen != "" and active_screen != screen_name:
		_close_screen(active_screen)
	var node = screens[screen_name]
	if node == null:
		return
	active_screen = screen_name
	if review_target == "ledger_commitments" and node.has_method("open_to_commitments"):
		node.open_to_commitments(api_client)
	elif review_target == "ledger_war_bargains" and node.has_method("open_to_war_bargains"):
		node.open_to_war_bargains(api_client)
	elif review_target == "ledger_settlements" and node.has_method("open_to_settlements"):
		node.open_to_settlements(api_client, route_id, war_id)
	elif review_target == "ledger_vassals" and node.has_method("open_to_vassals"):
		node.open_to_vassals(api_client)
	elif node.has_method("open"):
		node.open(api_client)
	else:
		node.show()
	_update_button_highlights()
	screen_changed.emit(active_screen)


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


func update_turn(turn_number: int, calendar_label: String = ""):
	"""Update the turn counter label.

	HC-0: an anchored campaign shows the dated turn beside the counter
	("Turn 5 — Late November 1805"); worlds without an anchor pass ""
	and keep the plain "Turn N" byte-identically."""
	if calendar_label != "":
		turn_label.text = "Turn " + str(int(turn_number)) + " — " + calendar_label
	else:
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
	# Null-safety: never toggle a screen that failed to register.
	if not screens.has(screen_name) or screens[screen_name] == null:
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
			btn.add_theme_color_override("font_color", Utils.UI_GOLD)
		else:
			btn.add_theme_stylebox_override("normal", _normal_style)
			btn.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)


# =============================================================================
# DIPLOMATIC TOP BAR FIELDS (Session 8B)
# =============================================================================

signal envoy_clicked
# NUI: the Admiralty chip (main.gd opens the ledger's own naval book)
signal admiralty_clicked
# UI-6: gear button — main.gd toggles the pause menu (mirrors ESC)
signal menu_clicked

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
		threat_label.add_theme_color_override("font_color", Utils.UI_WARNING)
		if brewing:
			_start_threat_pulse()
		else:
			_stop_threat_pulse()
	else:
		threat_label.visible = true
		threat_label.text = "[THREAT!]"
		threat_label.add_theme_color_override("font_color", Utils.UI_ALERT)
		if brewing:
			_start_threat_pulse()
		else:
			_stop_threat_pulse()

	# Talleyrand status
	var mission_summary = str(data.get("talleyrand_mission_summary", "Idle"))
	# IQ-4: the backend says "None" when no mission is live (three pins hold
	# that string), and the bar printed "Talleyrand: None" — read it as Idle.
	if mission_summary == "" or mission_summary == "null" or mission_summary == "None":
		mission_summary = "Idle"
	_set_talleyrand_summary(mission_summary)

	update_mailbox_count(int(data.get("pending_envoy_count", 0)))


var _current_envoy_count: int = 0

func get_envoy_count() -> int:
	return _current_envoy_count

func _set_talleyrand_summary(mission_summary: String):
	"""Keep the mission line compact without hiding the full text."""
	var clean_summary = mission_summary.strip_edges()
	# IQ-4: "None" is the backend's idle word — both entry points read it so.
	if clean_summary == "" or clean_summary == "None":
		clean_summary = "Idle"
	var full_text = "Talleyrand: " + Utils.humanize_nation_keys_in_text(clean_summary)
	talleyrand_label.tooltip_text = full_text
	if full_text.length() > TALLEYRAND_SUMMARY_MAX_CHARS:
		talleyrand_label.text = full_text.substr(0, TALLEYRAND_SUMMARY_MAX_CHARS - 3).rstrip(" ") + "..."
	else:
		talleyrand_label.text = full_text

func update_mailbox_count(envoy_count: int):
	"""Refresh the envoys button copy and styling."""
	_current_envoy_count = envoy_count
	if envoy_count > 0:
		mailbox_btn.text = "Envoys (" + str(envoy_count) + ")"
		mailbox_btn.tooltip_text = Utils.plural(envoy_count, "pending envoy") + (" awaits" if envoy_count == 1 else " await") + " your reply."
		mailbox_btn.add_theme_stylebox_override("normal", _mailbox_alert_style)
		mailbox_btn.add_theme_stylebox_override("hover", _mailbox_alert_hover_style)
		mailbox_btn.add_theme_color_override("font_color", Utils.UI_WARNING)
	else:
		mailbox_btn.text = "Envoys"
		mailbox_btn.tooltip_text = "No pending envoys."
		mailbox_btn.add_theme_stylebox_override("normal", _mailbox_idle_style)
		mailbox_btn.add_theme_stylebox_override("hover", _mailbox_idle_hover_style)
		mailbox_btn.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)


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


# =============================================================================
# NUI "The Admiralty on the Map" (September 23, 2026) — the Admiralty chip
# =============================================================================

var _admiralty_summary: Dictionary = {}


func update_admiralty(summary: Dictionary):
	"""The fleet's standing line from `naval_overlay.player_summary` — hidden
	on a world with no naval theatre; crimson-bordered under blockade, gold
	while a window stands open. The tooltip is the backend's one sentence."""
	if admiralty_btn == null:
		return
	_admiralty_summary = summary if summary is Dictionary else {}
	if not bool(_admiralty_summary.get("active", false)):
		admiralty_btn.visible = false
		return
	admiralty_btn.visible = true
	admiralty_btn.tooltip_text = Utils.humanize_nation_keys_in_text(
		str(_admiralty_summary.get("line", ""))) + "\nClick — THE ADMIRALTY (Ledger, book 7)"
	var blockaded := str(_admiralty_summary.get("blockaded_by", "")) != ""
	var window := int(_admiralty_summary.get("window_turns", 0)) > 0
	if blockaded:
		admiralty_btn.add_theme_stylebox_override("normal", _mailbox_alert_style)
		admiralty_btn.add_theme_stylebox_override("hover", _mailbox_alert_hover_style)
		admiralty_btn.add_theme_color_override("font_color", Utils.UI_ALERT)
	elif window:
		admiralty_btn.add_theme_stylebox_override("normal", _mailbox_alert_style)
		admiralty_btn.add_theme_stylebox_override("hover", _mailbox_alert_hover_style)
		admiralty_btn.add_theme_color_override("font_color", Utils.UI_GOLD)
	else:
		admiralty_btn.add_theme_stylebox_override("normal", _mailbox_idle_style)
		admiralty_btn.add_theme_stylebox_override("hover", _mailbox_idle_hover_style)
		admiralty_btn.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	_refresh_admiralty_text()


func _refresh_admiralty_text():
	if admiralty_btn == null or _admiralty_summary.is_empty():
		return
	var ships := int(_admiralty_summary.get("ships", 0))
	var blockaded := str(_admiralty_summary.get("blockaded_by", "")) != ""
	var window := int(_admiralty_summary.get("window_turns", 0)) > 0
	var text := "\u2693 " + str(ships)
	if not _compact:
		text += " sail"
		if blockaded:
			text += " \u00b7 BLOCKADED"
		elif window:
			text += " \u00b7 WINDOW"
	elif blockaded:
		text += "!"
	admiralty_btn.text = text


func open_ledger_to_tab(tab_index: int):
	"""Open the Strategic Ledger straight to one book (THE ADMIRALTY = 6)."""
	var screen_name := "ledger"
	if not screens.has(screen_name) or screens[screen_name] == null:
		return
	if active_screen == screen_name:
		var open_node = screens[screen_name]
		if open_node.has_method("_switch_tab"):
			open_node._switch_tab(tab_index)
		return
	if active_screen != "":
		_close_screen(active_screen)
	var node = screens[screen_name]
	active_screen = screen_name
	if node.has_method("open_to_tab"):
		node.open_to_tab(api_client, tab_index)
	elif node.has_method("open"):
		node.open(api_client)
	else:
		node.show()
	_update_button_highlights()
	screen_changed.emit(active_screen)


func is_compact() -> bool:
	return _compact


func _fit_bar():
	"""IQ10-X1: fit the bar to the LOGICAL viewport. Below COMPACT_BELOW_PX the
	nav buttons go icon-only (their tooltips carry the name and both hotkeys),
	the Cabinet line hides and the Admiralty chip keeps the count alone."""
	var width := get_viewport().get_visible_rect().size.x
	var compact := width < COMPACT_BELOW_PX
	if compact == _compact and not _nav_full_text.is_empty() and _fit_applied:
		return
	_compact = compact
	_fit_applied = true
	for sname in button_map:
		var btn: Button = button_map[sname]
		if compact:
			# Icon-only — or the hotkey letter where no icon loaded, so the
			# bar never shows a blank square (the capture harness has no
			# icon imports and showed six).
			btn.text = "" if btn.icon != null else str(HOTKEY_HINTS.get(sname, ""))
		else:
			btn.text = str(_nav_full_text.get(sname, btn.text))
	if talleyrand_label:
		talleyrand_label.visible = not compact
	_refresh_admiralty_text()


var _fit_applied := false

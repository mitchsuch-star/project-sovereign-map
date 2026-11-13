extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Top Bar Controller (Session A)
# =============================================================================
# Unified top bar framework. CanvasLayer 75 with buttons + notification area +
# turn counter. Manages information screens (layer 50) — one screen at a time.
# =============================================================================

signal screen_changed(screen_name: String)
# UXR-D1 (Pre-Deploy S9b): the strip's drawn height moved (Text size grew or
# shrank its line); main.gd refits the HUD that sits under it.
signal bar_height_changed
# UXR-D4 (Pre-Deploy S12b, the Side Desk): the pinned screen changed ("" when
# none), and the dock's width moved — main.gd re-fits the HUD beside it.
signal pin_changed(screen_name: String)
signal dock_changed

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
# UXR3-2 (Pre-Deploy S12 part 2): the Cabinet line is a bordered chip in the
# Admiralty chip's style — it was small plain text the eye passed over — and
# it opens the Diplomatic Ledger at Talleyrand's book.
@onready var talleyrand_label: Button = $BarContainer/BarBG/BarLayout/RightSection/TalleyrandLabel
@onready var mailbox_btn: Button = $BarContainer/BarBG/BarLayout/RightSection/MailboxButton
# NUI "The Admiralty on the Map": the fleet's standing line, hidden on a
# world with no naval theatre; a click opens THE ADMIRALTY (ledger tab 7).
@onready var admiralty_btn: Button = $BarContainer/BarBG/BarLayout/RightSection/AdmiraltyBtn
# UI-6: the pause menu finally gets a clickable entry point (was ESC-only)
@onready var menu_btn: Button = $BarContainer/BarBG/BarLayout/RightSection/MenuBtn

# State tracking
var active_screen: String = ""  # "" = none, "event_log", "ledger", "generals", "diplomatic_ledger", "dispatch"
var screens: Dictionary = {}    # maps screen name -> node reference
# UXR-D4 (Pre-Deploy S12b): the Side Desk. ONE screen may be pinned: it docks
# non-modal in the right third of the HUD band beside a live map. Pinning
# moves the open screen from `active_screen` to `pinned_screen`, so
# `is_screen_open()` is false while only a pinned screen stands (the map, the
# command line and the rail stay live). Opening any other screen unpins and
# closes it first: the one-screen rule holds. The pin is a session state,
# never saved.
var pinned_screen: String = ""
const PIN_TOOLTIP := "Keep this screen open beside the map — Esc or Unpin closes it"
# Session UI-4: the compact view leaves no room beside the map for a desk
const PIN_COMPACT_TOOLTIP := "No room beside the map at this Interface Scale — lower it to keep a screen beside the map"
var _pin_chips: Dictionary = {}  # screen name -> its header's Pin chip
var api_client = null

# Threat pulse state (Session 8B)
var _threat_pulse_timer: Timer = null
var _threat_pulsing: bool = false

# Button -> screen name mapping
var button_map: Dictionary = {}

# Active button style
var _active_style: StyleBoxFlat = null
var _normal_style: StyleBoxFlat = null
var _nav_strip: Dictionary = {}
var _mailbox_idle_style: StyleBoxFlat = null
var _mailbox_idle_hover_style: StyleBoxFlat = null
var _mailbox_alert_style: StyleBoxFlat = null
var _mailbox_alert_hover_style: StyleBoxFlat = null
var _mailbox_pressed_style: StyleBoxFlat = null
const TALLEYRAND_SUMMARY_MAX_CHARS := 34
# S14G-X118: the head of the backend's paused suffix ("paused — carrying a
# letter", `diplomacy.MISSION_PAUSED_SUFFIX`) - the face keeps this much of it.
const TALLEYRAND_PAUSED_MARK := " (paused"
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
# EA-E9 (SF-RR5, October 21, 2026): a second while-typing key where a common
# overlay takes the first — NVIDIA's and AMD's overlays both default to Alt+R
# (main.gd _SCREEN_HOTKEYS carries the binding).
const SECOND_HOTKEYS := {"dispatch": "B"}
var _nav_full_text := {}
# EA-E1: each nav button's glyph, shown only on the compact bar.
var _nav_icons := {}
var _compact := false

func _ready():
	# Session UI (November 11, 2026): the nav is the ONE tab strip
	# (`Utils.tab_styles`) at the bar's own 8 / 4 margins — a closed screen is
	# its words on the strip (the grey boxes are gone), the open one stands on
	# a gilt underline.
	_nav_strip = Utils.tab_styles(8.0, 4.0)
	_active_style = _nav_strip["active"]
	_normal_style = _nav_strip["normal"]

	_mailbox_idle_style = StyleBoxFlat.new()
	_mailbox_idle_style.bg_color = Color(0.075, 0.09, 0.14, 0.9)
	_mailbox_idle_style.border_width_left = 1
	_mailbox_idle_style.border_width_top = 1
	_mailbox_idle_style.border_width_right = 1
	_mailbox_idle_style.border_width_bottom = 1
	# Session UI: a gilt hairline (it was UI_ENVOY_IDLE_BORDER, a grey-blue).
	_mailbox_idle_style.border_color = Color(Utils.UI_GOLD, 0.42)
	_mailbox_idle_style.corner_radius_top_left = 2
	_mailbox_idle_style.corner_radius_top_right = 2
	_mailbox_idle_style.corner_radius_bottom_right = 2
	_mailbox_idle_style.corner_radius_bottom_left = 2
	_mailbox_idle_style.content_margin_left = 10.0
	_mailbox_idle_style.content_margin_right = 10.0
	_mailbox_idle_style.content_margin_top = 4.0
	_mailbox_idle_style.content_margin_bottom = 4.0

	_mailbox_idle_hover_style = _mailbox_idle_style.duplicate()
	_mailbox_idle_hover_style.bg_color = Utils.UI_ENVOY_IDLE_HOVER
	_mailbox_idle_hover_style.border_color = Utils.UI_GOLD_BRIGHT

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
		var tip := screen_title + " — " + key + ", or Alt+" + key + " while typing"
		if SECOND_HOTKEYS.has(sname):
			var second: String = SECOND_HOTKEYS[sname]
			tip += " (Alt+%s where a graphics overlay keeps Alt+%s)" % [second, key]
		button_map[sname].tooltip_text = tip

	# Apply normal style to all buttons
	for btn in button_map.values():
		btn.add_theme_stylebox_override("normal", _normal_style)

	# UI-3: a tinted glyph per nav button. EA-E1 (SF-RR5): it is the COMPACT
	# bar's face — `_fit_bar` shows it where the words go and takes it off the
	# full bar, which keeps its words and hotkeys (every frame since UI-3 shows
	# them so: the leading glyph never drew beside them, and there it would
	# push the compact threshold past 1,180).
	Utils.apply_button_icon(event_log_btn, Utils.ICON_PHOSPHOR + "list.svg")
	Utils.apply_button_icon(ledger_btn, Utils.ICON_PHOSPHOR + "map-trifold.svg")
	Utils.apply_button_icon(generals_btn, Utils.ICON_PHOSPHOR + "users-three.svg")
	Utils.apply_button_icon(diplo_ledger_btn, Utils.ICON_PHOSPHOR + "handshake.svg")
	Utils.apply_button_icon(dispatch_btn, Utils.ICON_PHOSPHOR + "scroll.svg")
	# (no newspaper glyph in the curated set — the open book reads as
	# the periodical's archive)
	Utils.apply_button_icon(gazette_btn, Utils.ICON_PHOSPHOR + "book-open.svg")
	for sname in button_map:
		_nav_icons[sname] = button_map[sname].icon

	# UI-6: nav hover/pressed match the flat bar look — without these the
	# theme's gold-bordered navy stylebox flashed in on hover (style-jump).
	var nav_hover_style: StyleBoxFlat = _nav_strip["hover"]
	var nav_pressed_style: StyleBoxFlat = _nav_strip["pressed"]
	for nav_btn in button_map.values():
		nav_btn.add_theme_stylebox_override("hover", nav_hover_style)
		nav_btn.add_theme_stylebox_override("pressed", nav_pressed_style)
		nav_btn.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		nav_btn.add_theme_color_override("font_hover_color", Utils.UI_GOLD_BRIGHT)

	# UI-6: gear button → pause menu (Save/Load/Settings)
	Utils.apply_icon_only_button(menu_btn, Utils.ICON_PHOSPHOR + "gear.svg")
	menu_btn.pressed.connect(func(): menu_clicked.emit())

	# Initialize turn label
	turn_label.text = "Turn 1"

	# Initialize diplomatic fields (Session 8B)
	dp_label.text = "0/3"
	# AU-1 (docs/AUTHORITY_CURRENCY_SPEC.md §5.6): the Authority chip beside DP —
	# code-built (the Pin chip's precedent, no .tscn edit).
	_build_authority_chip()
	# Session UI-2 (November 11, 2026): the resource groups, the court's
	# chips and the date — glyph + figure, each figure opening its book.
	_build_desk_groups()
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

	# UXR3-2: the Cabinet chip, styled as the Admiralty chip.
	if talleyrand_label:
		talleyrand_label.add_theme_stylebox_override("normal", _mailbox_idle_style)
		talleyrand_label.add_theme_stylebox_override("hover", _mailbox_idle_hover_style)
		talleyrand_label.add_theme_stylebox_override("pressed", _mailbox_pressed_style)
		talleyrand_label.pressed.connect(open_cabinet)

	# UXR-D3: two pads at the ends of the layout hold the clusters inside the
	# HUD band (0 wide at Full); the strip itself stays full-bleed.
	var layout := get_node_or_null("BarContainer/BarBG/BarLayout") as Control
	if layout != null:
		_band_pad_left = Control.new()
		_band_pad_left.name = "BandPadLeft"
		_band_pad_left.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layout.add_child(_band_pad_left)
		layout.move_child(_band_pad_left, 0)
		_band_pad_right = Control.new()
		_band_pad_right.name = "BandPadRight"
		_band_pad_right.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layout.add_child(_band_pad_right)
	# IQ10-X1: the bar fits itself to the logical viewport, now and on every
	# resize (an Interface Scale change resizes the logical viewport too).
	for sname in button_map:
		_nav_full_text[sname] = button_map[sname].text
	get_viewport().size_changed.connect(_fit_bar)
	call_deferred("_fit_bar")
	# UXR-2: the notice rail's slot is ANCHORED too (a viewport fraction).
	get_viewport().size_changed.connect(_fit_rail)
	call_deferred("_fit_rail")
	# UXR-D1: the strip's drawn height (its line grows with Text size) is the
	# one number the HUD under it clears.
	var bar := get_node_or_null("BarContainer") as Control
	if bar != null:
		bar.resized.connect(_on_bar_resized)

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
	# Session UI-2: a screen fades in when it opens (Reduce motion: at once).
	Utils.watch_motion(node)
	# Listen for screen's own close signal (X button, overlay click)
	if node.has_signal("closed"):
		node.closed.connect(_on_screen_closed.bind(screen_name))
	_attach_pin_chip(screen_name, node)


func toggle_screen(screen_name: String):
	"""Toggle a screen: close if open, open if closed (closing current first)."""
	if pinned_screen == screen_name:
		# Its key or its button closes a pinned screen, as it closes an open one.
		unpin()
		return
	if active_screen == screen_name:
		# Toggle off — close the active screen
		_close_screen(screen_name)
	else:
		# Close current screen first (one at a time rule)
		if active_screen != "":
			_close_screen(active_screen)
		# Open the new screen
		_open_screen(screen_name)


func open_cabinet() -> void:
	"""UXR3-2: the Cabinet chip — the Diplomatic Ledger at TALLEYRAND (book 4)."""
	cabinet_clicked.emit()
	open_diplomatic_ledger_review("ledger_talleyrand")


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
	# UXR-D4: a pinned Diplomatic Ledger turns to the review where it stands.
	var stays_pinned: bool = pinned_screen == screen_name
	_make_room_for(screen_name)
	if not stays_pinned:
		active_screen = screen_name
	if review_target == "ledger_commitments" and node.has_method("open_to_commitments"):
		node.open_to_commitments(api_client)
	elif review_target == "ledger_war_bargains" and node.has_method("open_to_war_bargains"):
		node.open_to_war_bargains(api_client)
	elif review_target == "ledger_settlements" and node.has_method("open_to_settlements"):
		node.open_to_settlements(api_client, route_id, war_id)
	elif review_target == "ledger_vassals" and node.has_method("open_to_vassals"):
		node.open_to_vassals(api_client)
	elif review_target == "ledger_congress" and node.has_method("open_to_congress"):
		node.open_to_congress(api_client)
	elif review_target == "ledger_talleyrand" and node.has_method("open_to_talleyrand"):
		node.open_to_talleyrand(api_client)
	elif review_target == "ledger_balance" and node.has_method("open_to_balance"):
		node.open_to_balance(api_client)
	elif node.has_method("open"):
		node.open(api_client)
	else:
		node.show()
	if stays_pinned:
		# Its open road re-centred the panel; it stays at the desk.
		_set_docked(node, true)
	_update_button_highlights()
	screen_changed.emit(active_screen)


func close_all_screens():
	"""Close whatever screen is open. Called on turn transitions, before a
	popup, a command and the mailbox — a pinned screen stays at the desk
	(UXR-D4); `close_everything` unpins it too."""
	if active_screen != "":
		_close_screen(active_screen)


func close_everything():
	"""UXR-D4: close the open screen AND unpin the pinned one — the pause
	menu, a load, a new campaign and the Fall, which leave the war room."""
	close_all_screens()
	unpin()


func refit_active_screen() -> void:
	"""UXR-2: the open screen re-fits the logical viewport (and keeps its
	grip on its corner) — called by `main._on_root_resized`. UXR-D4: a pinned
	screen re-docks (its width follows the band)."""
	if pinned_screen != "" and not can_pin():
		_unpin_to_book()
	for chip_screen in _pin_chips:
		_dress_pin_chip(chip_screen)
	if active_screen != "" and screens.get(active_screen) != null:
		Utils.refit_surface(screens[active_screen])
	if pinned_screen != "" and screens.get(pinned_screen) != null:
		_dock(screens[pinned_screen])


func is_screen_open() -> bool:
	"""True when any top bar screen is visible — the MODAL kind. A pinned
	screen alone is not one (UXR-D4): the map is live beside it."""
	return active_screen != ""


func is_pinned() -> bool:
	"""UXR-D4: a screen stands pinned at the Side Desk."""
	return pinned_screen != ""


func get_pinned_screen() -> String:
	return pinned_screen


func refresh_pinned() -> void:
	"""UXR-D4: re-read the pinned screen (main.gd calls it after every
	command response and once the end-turn chain settles). Its current tab,
	its scroll kept — each screen's own `refresh_pinned`."""
	if pinned_screen == "":
		return
	var node = screens.get(pinned_screen)
	if node != null and node.visible and node.has_method("refresh_pinned"):
		node.refresh_pinned()


func can_pin() -> bool:
	"""Session UI-4 (November 12, 2026): a desk needs room beside the map. In
	the compact view (Interface Scale 2.0 on a 900-px window: 800 x 450 logical)
	the docked screen took the whole width its content needs (the ledger's tab
	row, 737 px), covering the war room, the command window under it and the
	map's zoom row off the left edge — there a screen opens as a book."""
	return not Utils.compact_view()


func toggle_pin(screen_name: String) -> void:
	"""UXR-D4: the header's Pin chip. Pin the open screen to the desk; on a
	pinned screen the chip reads Unpin, which closes it."""
	if pinned_screen == screen_name:
		unpin()
	elif active_screen == screen_name and can_pin():
		_pin(screen_name)


func _unpin_to_book() -> void:
	"""Session UI-4: the view turned compact under a pinned screen (the player
	raised the Interface Scale) — it stays open, as a book, its place in the
	books kept; the desk's width returns to the HUD."""
	var screen_name := pinned_screen
	pinned_screen = ""
	var node = screens.get(screen_name)
	if node != null:
		_set_docked(node, false)
		active_screen = screen_name
	_update_button_highlights()
	screen_changed.emit(active_screen)
	pin_changed.emit("")


func unpin() -> void:
	"""UXR-D4: unpin the pinned screen and close it (its Unpin chip, Esc, a
	key or a button that toggles it, another screen opening, the pause menu,
	a load, a new campaign, the Fall)."""
	if pinned_screen == "":
		return
	var screen_name := pinned_screen
	pinned_screen = ""
	var node = screens.get(screen_name)
	if node != null:
		_set_docked(node, false)
		_close_node(node)
	_update_button_highlights()
	pin_changed.emit("")


func _pin(screen_name: String) -> void:
	var node = screens.get(screen_name)
	if node == null:
		return
	if pinned_screen != "" and pinned_screen != screen_name:
		unpin()
	if active_screen == screen_name:
		active_screen = ""
	pinned_screen = screen_name
	_set_docked(node, true)
	_update_button_highlights()
	# active_screen is "" now: main.gd gives the map back its mouse.
	screen_changed.emit(active_screen)
	pin_changed.emit(pinned_screen)


func _make_room_for(screen_name: String) -> void:
	"""UXR-D4: the one-screen rule — any OTHER screen opening unpins and
	closes the pinned one first."""
	if pinned_screen != "" and pinned_screen != screen_name:
		unpin()


func _attach_pin_chip(screen_name: String, node: Node) -> void:
	"""UXR-D4: a text chip "Pin" beside the header's close cross (Phosphor
	ships no push-pin; nothing is downloaded), styled as the family's chip."""
	var close_btn := node.get_node_or_null("PanelContainer/VBoxContainer/HeaderRow/CloseButton") as Control
	if close_btn == null:
		return
	var chip := Button.new()
	chip.name = "PinChip"
	chip.text = "Pin"
	chip.theme_type_variation = &"CaptionButton"
	chip.focus_mode = Control.FOCUS_NONE
	chip.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	chip.tooltip_text = PIN_TOOLTIP
	chip.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	chip.pressed.connect(toggle_pin.bind(screen_name))
	var row := close_btn.get_parent()
	row.add_child(chip)
	row.move_child(chip, close_btn.get_index())
	_pin_chips[screen_name] = chip
	_dress_pin_chip(screen_name)


func _dress_pin_chip(screen_name: String) -> void:
	"""Session UI-4: where a desk has no room (the compact view) the Pin chip
	is disabled and its hover says why; an Unpin chip always acts."""
	var chip := _pin_chips.get(screen_name) as Button
	if chip == null:
		return
	var locked := pinned_screen != screen_name and not can_pin()
	chip.disabled = locked
	chip.tooltip_text = PIN_COMPACT_TOOLTIP if locked else PIN_TOOLTIP


func _set_docked(node: Node, on: bool) -> void:
	"""Dock a screen at the Side Desk or return it to its centred self: its
	overlay hides and lets the mouse through, its grip hides, its chip reads
	Unpin; undocked, each comes back as it was."""
	node.set_meta("side_desk_docked", on)
	var overlay := node.get_node_or_null("BackgroundOverlay") as Control
	if overlay != null:
		if not overlay.has_meta("side_desk_filter"):
			overlay.set_meta("side_desk_filter", overlay.mouse_filter)
		overlay.visible = not on
		overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE if on \
				else int(overlay.get_meta("side_desk_filter"))
	for c in node.get_children():
		if c is ResizeGrip:
			(c as ResizeGrip).set_suppressed(on)
	for screen_name in screens:
		if screens[screen_name] == node and _pin_chips.has(screen_name):
			(_pin_chips[screen_name] as Button).text = "Unpin" if on else "Pin"
			_dress_pin_chip(screen_name)
	if on:
		_dock(node)
	else:
		_publish_dock(0.0)
		var panel := node.get_node_or_null("PanelContainer") as Control
		if panel != null and node.visible:
			Utils.clamp_centered_panel(panel)


func _dock(node: Node) -> void:
	var panel := node.get_node_or_null("PanelContainer") as Control
	if panel != null:
		_publish_dock(Utils.dock_right(panel))


func _publish_dock(width: float) -> void:
	if Utils.set_dock_width(width):
		dock_changed.emit()


func _exit_tree() -> void:
	# The dock's width is static: a war room torn down with a screen pinned
	# (a scene change) must not leave the next one's HUD beside no dock.
	Utils.set_dock_width(0.0)


func get_active_screen() -> String:
	"""Return the name of the active screen, or empty string."""
	return active_screen


func update_turn(turn_number: int, calendar_label: String = ""):
	"""Update the turn counter label.

	HC-0: an anchored campaign shows the dated turn beside the counter
	("Turn 5 — Late November 1805"); worlds without an anchor pass ""
	and keep the plain "Turn N" byte-identically."""
	# Session UI-2: the date stands in the title face; the turn's number
	# beside the hourglass (the tooltip names both). A world with no anchor
	# keeps its plain "Turn N".
	_calendar_label = calendar_label
	_turn_number = int(turn_number)
	_render_turn_text()
	if _turn_figure != null:
		_turn_figure.text = str(int(turn_number)) if calendar_label != "" else ""
		_turn_figure.get_parent().visible = calendar_label != ""
	var turn_tip := "Turn " + str(int(turn_number)) + ((" — " + calendar_label) if calendar_label != "" else "")
	turn_label.tooltip_text = turn_tip + "\nClick — the morning dispatch (press R, or Alt+R or Alt+B while you type)"
	_queue_fit_right()
	if _turn_figure != null:
		_turn_figure.get_parent().tooltip_text = turn_label.tooltip_text


func _open_screen(screen_name: String):
	"""Open a screen by name."""
	if not screens.has(screen_name):
		return
	var node = screens[screen_name]
	if node == null:
		return

	_make_room_for(screen_name)
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

	_close_node(node)

	_update_button_highlights()
	screen_changed.emit(active_screen)


func _close_node(node: Node) -> void:
	# Close the screen
	if node.has_method("close_log"):
		node.close_log()
	elif node.has_method("close_view"):
		node.close_view()
	else:
		node.hide()


func _on_button_pressed(screen_name: String):
	"""Handle a top bar button click."""
	# Null-safety: never toggle a screen that failed to register.
	if not screens.has(screen_name) or screens[screen_name] == null:
		return
	toggle_screen(screen_name)


func _on_screen_closed(screen_name: String):
	"""Handle a screen closing itself (X button, overlay click)."""
	if pinned_screen == screen_name:
		# UXR-D4: a pinned screen closed by its own cross leaves the desk.
		pinned_screen = ""
		var node = screens.get(screen_name)
		if node != null:
			_set_docked(node, false)
		_update_button_highlights()
		pin_changed.emit("")
		return
	if active_screen == screen_name:
		active_screen = ""
		_update_button_highlights()
		screen_changed.emit(active_screen)


func _update_button_highlights():
	"""Set the active button to highlighted style, all others to normal."""
	for sname in button_map:
		var btn = button_map[sname]
		if sname == active_screen or sname == pinned_screen:
			btn.add_theme_stylebox_override("normal", _active_style)
			btn.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
		else:
			btn.add_theme_stylebox_override("normal", _normal_style)
			# PC15-10 B1: amber while a marshal waits in the antechamber.
			if sname == "generals" and _audience_marshal != "":
				btn.add_theme_color_override("font_color", Utils.UI_WARNING)
			else:
				btn.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
		# RR5-X6 (SF-RR5): the compact bar's glyph carries the antechamber's
		# amber too — its words, and their "(1)", are gone there.
		var waiting: bool = (sname == "generals" and _audience_marshal != ""
				and sname != active_screen and sname != pinned_screen)
		btn.add_theme_color_override("icon_normal_color",
				Utils.UI_WARNING if waiting else Utils.UI_GOLD)


# =============================================================================
# DIPLOMATIC TOP BAR FIELDS (Session 8B)
# =============================================================================

signal envoy_clicked
# NUI: the Admiralty chip (main.gd opens the ledger's own naval book)
signal admiralty_clicked
# UXR3-2: the Cabinet chip was pressed (main may listen; the bar opens the
# ledger at Talleyrand's book itself).
signal cabinet_clicked
# UI-6: gear button — main.gd toggles the pause menu (mirrors ESC)
signal menu_clicked

# UXR3-F6's class (Pre-Deploy S12 part 2, part 5d): the alarm read
# "[THREAT]" / "[THREAT!]", a bracketed tag; it reads in the game's words —
# the Balance of Europe tab's own figure — its colour still the warning or
# the alert.
# S14G-M3 (Pre-Deploy S14h part 2, October 26, 2026): the HUD said "Threat" while
# every reply said "alarm" ("[Alarm] Europe's alarm rises +8") - the tooltip now
# joins the two nouns: the Threat IS Europe's alarm at France. A win adds to it
# (the muster says how much), and the morning's Threat line names what moved it.
# S14G-X77: the Balance of Europe tab in the book's key form (a bare letter TYPES into the line).
const THREAT_TOOLTIP := "Europe's alarm (the Threat) at France, out of 100 — a coalition brews at 60 and forms at 80. A battle won, a province taken, a war declared each add to it; the morning dispatch names what moved it. The Diplomatic Ledger's Balance of Europe tab (press D, then 3; Alt+D, then Alt+3 while you type) tells the sources."


static func _threat_words(threat: int) -> String:
	# Session UI-2: the figure beside the eye glyph; "of 100" and the bands
	# are the tooltip's (THREAT_TOOLTIP) and the gauge's.
	return "%d" % threat


func update_diplomatic_fields(data: Dictionary):
	"""Update all diplomatic top bar fields from /test poll data."""
	# DP counter
	var dp = int(data.get("diplomatic_points", 0))
	var dp_max = int(data.get("max_diplomatic_points", 3))
	dp_label.text = str(dp) + "/" + str(dp_max)
	dp_label.tooltip_text = DP_TOOLTIP % [dp, dp_max]

	# AU-1: the Authority chip, from the one key every base response carries.
	if data.has("authority"):
		update_authority_chip(data.get("authority"))

	# Threat indicator
	var threat = int(data.get("threat_level", 0))
	var brewing = data.get("coalition_brewing", false)
	_set_threat_gauge(threat)
	if threat < 30:
		threat_label.visible = false
		_stop_threat_pulse()
	elif threat < 60:
		threat_label.visible = true
		threat_label.text = _threat_words(threat)
		threat_label.tooltip_text = THREAT_TOOLTIP
		threat_label.add_theme_color_override("font_color", Utils.UI_WARNING)
		if brewing:
			_start_threat_pulse()
		else:
			_stop_threat_pulse()
	else:
		threat_label.visible = true
		threat_label.text = _threat_words(threat)
		threat_label.tooltip_text = THREAT_TOOLTIP
		threat_label.add_theme_color_override("font_color", Utils.UI_ALERT_TEXT)
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

	# S14G-6 (Pre-Deploy S14h part 1, October 26, 2026): the Cabinet's lock
	# rides the same payload - the Envoys badge's tooltip says whose letter
	# shuts it (`update_mailbox_count` reads it).
	if data.has("cabinet_locked"):
		_cabinet_locked = bool(data.get("cabinet_locked", false))
		var locked_by = data.get("cabinet_locked_by", [])
		_cabinet_locked_by = locked_by.duplicate() if locked_by is Array else []
		_cabinet_locked_until = int(data.get("cabinet_locked_until", 0))

	update_mailbox_count(int(data.get("pending_envoy_count", 0)))
	_queue_fit_right()


# ═══ Session UI-2 (November 11, 2026): the desk's groups ═══════════════════
# The right side reads in three clusters split by gilt hairlines: the
# RESOURCES (glyph + figure: the chest, DP, authority, the threat with its
# gauge), the COURT (the Admiralty, the Cabinet, the Envoys — rimmed chips
# with their glyphs) and the DATE (the title face; the turn beside its
# hourglass). Every figure opens its book on a click (the research's "click a
# figure → its ledger"). Node paths are kept: the glyphs and rules are code-built
# siblings; the clusters are the existing nodes re-ordered in their row.
const DP_TOOLTIP := "Diplomatic points: %d of %d — what an envoy, a treaty or a Congress spends; they refill each turn.\nClick — the Cabinet (Diplomacy · Talleyrand)"
const TREASURY_TOOLTIP := "The treasury: %s gold, %s next turn by the accounts (income against upkeep and every charge).\nClick — the Economy book (Ledger)"
const GLYPH_PX := 18
var treasury_label: Label = null
var _treasury_gold := 0
var _treasury_net := 0
var _has_treasury := false
var _turn_figure: Label = null
var _threat_gauge: Control = null
var _threat_value := 0


func _glyph(name: String, tint: Color = Utils.UI_GOLD) -> TextureRect:
	var g := TextureRect.new()
	g.name = "Glyph_" + name
	g.texture = load(Utils.glyph(name))
	g.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	g.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	g.custom_minimum_size = Vector2(GLYPH_PX, GLYPH_PX)
	g.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	g.modulate = tint
	g.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return g


func _cluster_rule() -> Control:
	"""A gilt hairline standing between two clusters."""
	var r := ColorRect.new()
	r.name = "ClusterRule"
	r.color = Color(Utils.UI_GOLD, 0.35)
	r.custom_minimum_size = Vector2(1, 20)
	r.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


func _group(name: String, glyph_name: String, figure: Control, opens: Callable) -> HBoxContainer:
	"""Glyph + figure as one hover target that opens its book."""
	var box := HBoxContainer.new()
	box.name = name
	box.add_theme_constant_override("separation", 4)
	box.mouse_filter = Control.MOUSE_FILTER_STOP
	_pointer_controls.append(box)   # the pointing hand once the bar is laid out
	box.add_child(_glyph(glyph_name))
	box.gui_input.connect(func(event):
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			opens.call())
	box.mouse_entered.connect(func(): box.modulate = Color(1.12, 1.08, 0.98))
	box.mouse_exited.connect(func(): box.modulate = Color(1, 1, 1))
	return box


func _build_desk_groups() -> void:
	var row := dp_label.get_parent() as HBoxContainer
	if row == null or treasury_label != null:
		return
	row.add_theme_constant_override("separation", 8)
	var open_economy := func(): open_ledger_to_tab(2)
	var open_cabinet_book := func(): open_cabinet()
	var open_forces := func(): open_ledger_to_tab(0)
	var open_balance := func(): open_diplomatic_ledger_review("ledger_balance")
	var open_dispatch := func(): _on_button_pressed("dispatch")
	# the figures: the body face's lining figures (theme step `Figure`)
	treasury_label = Label.new()
	treasury_label.name = "TreasuryLabel"
	treasury_label.theme_type_variation = &"Figure"
	treasury_label.text = "—"
	treasury_label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	for fig in [dp_label, authority_chip, threat_label]:
		if fig != null:
			fig.theme_type_variation = &"Figure"
	# RESOURCES: the chest, DP, authority, the threat
	var g_gold := _group("TreasuryGroup", "gold", treasury_label, open_economy)
	g_gold.add_child(treasury_label)
	row.add_child(g_gold)
	row.move_child(g_gold, dp_label.get_index())
	var g_dp := _group("DPGroup", "dp", dp_label, open_cabinet_book)
	row.add_child(g_dp)
	row.move_child(g_dp, dp_label.get_index())
	_wire_figure(dp_label, open_cabinet_book)
	if authority_chip != null:
		var g_auth := _group("AuthorityGroup", "authority", authority_chip, open_forces)
		row.add_child(g_auth)
		row.move_child(g_auth, authority_chip.get_index())
		_wire_figure(authority_chip, open_forces)
	var g_threat := _group("ThreatGroup", "threat", threat_label, open_balance)
	row.add_child(g_threat)
	row.move_child(g_threat, threat_label.get_index())
	_wire_figure(threat_label, open_balance)
	_threat_gauge = _make_threat_gauge()
	row.add_child(_threat_gauge)
	row.move_child(_threat_gauge, threat_label.get_index() + 1)
	# the threat's glyph and gauge follow its visibility (shown from 30)
	threat_label.visibility_changed.connect(func():
		g_threat.visible = threat_label.visible
		_threat_gauge.visible = threat_label.visible)
	g_threat.visible = threat_label.visible
	_threat_gauge.visible = threat_label.visible
	# COURT: the Admiralty, the Cabinet, the Envoys — after a rule
	var rule_a := _cluster_rule()
	row.add_child(rule_a)
	row.move_child(rule_a, _threat_gauge.get_index() + 1)
	if admiralty_btn != null and talleyrand_label != null:
		# the Admiralty leaves index 0, so the Cabinet's index drops by one
		row.move_child(admiralty_btn, talleyrand_label.get_index() - 1)
	if talleyrand_label != null:
		Utils.apply_button_icon(talleyrand_label, Utils.glyph("cabinet"))
	Utils.apply_button_icon(mailbox_btn, Utils.glyph("envoy"))
	# DATE: a rule, the hourglass and the turn, the date in the title face
	var rule_b := _cluster_rule()
	row.add_child(rule_b)
	row.move_child(rule_b, turn_label.get_index())
	var g_turn := _group("TurnGroup", "turn", null, open_dispatch)
	_turn_figure = Label.new()
	_turn_figure.name = "TurnFigure"
	_turn_figure.theme_type_variation = &"Figure"
	_turn_figure.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
	g_turn.add_child(_turn_figure)
	row.add_child(g_turn)
	row.move_child(g_turn, turn_label.get_index())
	turn_label.theme_type_variation = &"HudTitle"
	turn_label.remove_theme_color_override("font_color")
	_wire_figure(turn_label, open_dispatch)
	_refresh_treasury_text()
	_arm_pointers.call_deferred()


var _pointer_controls: Array = []


func _arm_pointers() -> void:
	"""Session UI-2: the figure groups take the pointing hand only once the
	bar has laid out. A cursor shape written during `_ready` makes the engine
	re-pick the control under the mouse while every child still stands at
	(0, 0): the gear (the row's last child) took a stale hover, then its
	tooltip, and that open tooltip ate the first Esc (DDB-54's driven pin)."""
	await get_tree().process_frame
	for c in _pointer_controls:
		if is_instance_valid(c):
			(c as Control).mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_pointer_controls.clear()


func _wire_figure(figure: Control, opens: Callable) -> void:
	figure.mouse_filter = Control.MOUSE_FILTER_STOP
	_pointer_controls.append(figure)   # the pointing hand once the bar is laid out
	figure.gui_input.connect(func(event):
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			opens.call())


func update_treasury(gold: int, net: int, has_net: bool = true) -> void:
	"""The chest's figure (main.gd::_update_gold_display — the status row's
	own numbers): the gold, and the turn's net beside it when it is known."""
	_treasury_gold = int(gold)
	_treasury_net = int(net)
	_has_treasury = bool(has_net)
	_refresh_treasury_text()
	_queue_fit_right()


func _refresh_treasury_text() -> void:
	if treasury_label == null:
		return
	var gold_words := Utils.format_number(_treasury_gold)
	if not _has_treasury:
		treasury_label.text = gold_words
		treasury_label.tooltip_text = TREASURY_TOOLTIP % [gold_words, "nothing yet"]
		return
	var sign := "+" if _treasury_net >= 0 else "\u2212"
	var net_words := sign + Utils.format_number(absi(_treasury_net))
	treasury_label.text = gold_words if _fit_step >= 2 else gold_words + "  " + net_words
	treasury_label.tooltip_text = TREASURY_TOOLTIP % [gold_words, net_words]
	treasury_label.get_parent().tooltip_text = treasury_label.tooltip_text


# The fit ladder: the right side sheds detail, one step at a time, until the
# bar fits its band — the gauge, the chest's net, the Cabinet chip (its full
# line is on the Ledger), the Admiralty's words, the Envoys' word, the title
# face and the turn's hourglass. Each step returns when the bar widens. The
# nav's words / glyphs (`_compact`) are decided first, by COMPACT_BELOW_PX.
var _fit_step := 0
var _fit_queued := false
# Session UI-4 (November 12, 2026): two last steps, the date's own — 7 drops its
# season word ("September 1805"), 8 keeps the turn alone ("Turn 20"); the whole
# date is always the hover. At the shipped 115 % on the compact 2.0 view (800
# logical px) six steps left the bar 2–28 px wider than the window, the Event
# Log's button off its left edge and the menu's gear off its right (IQ10-X1's
# own two, measured on the war room's real chips).
const _FIT_STEPS := 8
var _calendar_label := ""
var _turn_number := 0


func _queue_fit_right() -> void:
	if _fit_queued:
		return
	_fit_queued = true
	call_deferred("_fit_right_cluster")


func _fit_right_cluster() -> void:
	_fit_queued = false
	var layout := get_node_or_null("BarContainer/BarBG/BarLayout") as Control
	if layout == null or treasury_label == null:
		return
	var view_w := get_viewport().get_visible_rect().size.x
	for step in range(0, _FIT_STEPS + 1):
		_apply_fit_step(step)
		if layout.get_combined_minimum_size().x + 16.0 <= view_w:
			return


func _apply_fit_step(step: int) -> void:
	_fit_step = step
	if _threat_gauge != null:
		_threat_gauge.visible = threat_label.visible and step < 1
	_refresh_treasury_text()
	if talleyrand_label:
		talleyrand_label.visible = not _compact and step < 3
	_refresh_admiralty_text()
	mailbox_btn.custom_minimum_size.x = 0.0 if step >= 5 else 110.0
	update_mailbox_count(_current_envoy_count)
	if _turn_figure != null:
		_turn_figure.get_parent().visible = step < 6 and _turn_figure.text != ""
	turn_label.theme_type_variation = &"Caption" if step >= 6 else &"HudTitle"
	_render_turn_text()


func _render_turn_text() -> void:
	"""The turn's words at the bar's fit step: the whole date, then the month
	and year (step 7), then the turn alone (step 8); a world with no calendar
	keeps its plain "Turn N"."""
	if _calendar_label == "" or _fit_step >= 8:
		turn_label.text = "Turn " + str(_turn_number)
	elif _fit_step >= 7:
		var words := _calendar_label.split(" ", false)
		turn_label.text = " ".join(words.slice(1)) if words.size() >= 3 else _calendar_label
	else:
		turn_label.text = _calendar_label


func _make_threat_gauge() -> Control:
	"""A slim 0–100 gauge under the threat's figure: the coalition's brew (60)
	and its forming (80) marked."""
	var gauge := Control.new()
	gauge.name = "ThreatGauge"
	gauge.custom_minimum_size = Vector2(38, 6)
	gauge.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	gauge.mouse_filter = Control.MOUSE_FILTER_IGNORE
	gauge.draw.connect(func():
		var w := gauge.size.x
		var h := gauge.size.y
		gauge.draw_rect(Rect2(0, 0, w, h), Color(0, 0, 0, 0.45))
		var fill := clampf(float(_threat_value) / 100.0, 0.0, 1.0)
		var tone: Color = Utils.UI_ALERT if _threat_value >= 60 else Utils.UI_WARNING
		gauge.draw_rect(Rect2(0, 0, w * fill, h), tone)
		for mark in [0.6, 0.8]:
			gauge.draw_rect(Rect2(w * mark, -1, 1, h + 2), Color(Utils.UI_GOLD, 0.8))
		gauge.draw_rect(Rect2(0, 0, w, h), Color(Utils.UI_GOLD, 0.45), false, 1.0))
	return gauge


func _set_threat_gauge(threat: int) -> void:
	_threat_value = int(threat)
	if _threat_gauge != null:
		_threat_gauge.queue_redraw()


# ═══ AU-1 (docs/AUTHORITY_CURRENCY_SPEC.md §5.6): the Authority chip ═══
# One figure beside DP ("Authority 87"; "Auth 87" in the compact bar), fed by
# the one key `authority` of every base response — {value, label, grip,
# presence, moves[≤5]}, every number an int — and tinted by the lines the
# price is read against: bright gold at 85 and above (the Presence full),
# the DP label's gold from 71 (credit), amber under 71 (the calm and the
# Charges lost), red under 50. The tooltip names the last moves with their
# causes and the five lines; the grip and the Presence when they differ.
const AUTHORITY_LINES_TOOLTIP := "The lines: 85 the Presence (the aura full); 80 obedience; 70 the marshals' calm and the Charges of Empire; 60 a diplomatic point a turn; 30 the spiral."
var authority_chip: Label = null
var _authority_payload: Dictionary = {}


func _build_authority_chip() -> void:
	if dp_label == null or authority_chip != null:
		return
	var chip := Label.new()
	chip.name = "AuthorityChip"
	chip.theme_type_variation = &"Caption"
	# a Label ignores the mouse by default — no tooltip without this
	chip.mouse_filter = Control.MOUSE_FILTER_STOP
	chip.text = "—"
	chip.tooltip_text = AUTHORITY_LINES_TOOLTIP
	chip.add_theme_color_override("font_color", Utils.UI_GOLD)
	var row := dp_label.get_parent()
	row.add_child(chip)
	row.move_child(chip, dp_label.get_index() + 1)
	authority_chip = chip


func update_authority_chip(payload) -> void:
	"""The figure as the backend says it (`standing.payload`): {value, label,
	grip, presence, moves[≤5]}. Tint by line; the tooltip from the moves."""
	if authority_chip == null:
		_build_authority_chip()
	if authority_chip == null or not (payload is Dictionary) or payload.is_empty():
		return
	_authority_payload = payload
	var value := int(payload.get("value", 100))
	var colour: Color = Utils.UI_GOLD_BRIGHT
	if value < 50:
		colour = Utils.UI_ALERT_TEXT
	elif value < 71:
		colour = Utils.UI_WARNING
	elif value < 85:
		colour = Utils.UI_GOLD
	authority_chip.add_theme_color_override("font_color", colour)
	authority_chip.tooltip_text = _authority_tooltip(payload)
	_refresh_authority_text()


func _authority_tooltip(payload: Dictionary) -> String:
	var value := int(payload.get("value", 0))
	var label := str(payload.get("label", ""))
	var grip := int(payload.get("grip", value))
	var presence := int(payload.get("presence", -1))
	var lines: Array = ["Authority %d (%s)" % [value, label]]
	if grip != value:
		lines.append("The Empire's grip %d — the number the game acts on (a lost capital, a losing war)." % grip)
	if presence >= 0 and presence < 10:
		lines.append("The Presence at +%d%% on the field." % presence)
	var moves = payload.get("moves", [])
	if moves is Array and moves.size() > 0:
		lines.append("Last moves:")
		for m in moves:
			if m is Dictionary:
				var delta := int(m.get("delta", 0))
				var sign := "+" if delta > 0 else "−"
				var cause := Utils.humanize_nation_keys_in_text(str(m.get("cause", "")))
				lines.append("  T%d  %s (%s%d)" % [int(m.get("turn", 0)), cause, sign, abs(delta)])
	else:
		lines.append("No move yet this campaign.")
	lines.append(AUTHORITY_LINES_TOOLTIP)
	return "\n".join(lines)


func _refresh_authority_text() -> void:
	if authority_chip == null:
		return
	# Session UI-2: the figure beside the crown glyph, on both bars.
	if _authority_payload.is_empty():
		authority_chip.text = "—"
		return
	var value := int(_authority_payload.get("value", 0))
	authority_chip.text = "%d" % value


var _current_envoy_count: int = 0
# S14G-6: the Cabinet's lock as the last diplomatic payload said it (whether a
# letter that locks stands, whose, and to which turn) - the badge's tooltip.
var _cabinet_locked: bool = false
var _cabinet_locked_by: Array = []
var _cabinet_locked_until: int = 0

func get_envoy_count() -> int:
	return _current_envoy_count

func _set_talleyrand_summary(mission_summary: String):
	"""Keep the mission line compact without hiding the full text."""
	var clean_summary = mission_summary.strip_edges()
	# IQ-4: "None" is the backend's idle word — both entry points read it so.
	if clean_summary == "" or clean_summary == "None":
		clean_summary = "Idle"
	var full_text = "Talleyrand: " + Utils.humanize_nation_keys_in_text(clean_summary)
	# S14G-X118 (Pre-Deploy S14h part 2, October 26, 2026): the tooltip is the
	# backend's WHOLE summary string - suffix and all ("Improving Relations →
	# Prussia (paused — carrying a letter)", `main._get_talleyrand_mission_summary`),
	# the one source; the face is the short form of it (`_talleyrand_face`).
	talleyrand_label.tooltip_text = full_text + "\nClick — Talleyrand's book (Diplomacy)"
	talleyrand_label.text = _talleyrand_face(full_text)


func _talleyrand_face(full_text: String) -> String:
	"""S14G-X118: the bar's short form of Talleyrand's summary. The old cut at
	TALLEYRAND_SUMMARY_MAX_CHARS fell on the tail, so a mission paused under a
	letter lost the one thing that mattered at a glance - "Talleyrand: Improving
	Relations..." read as a courtship at work. The body is cut instead and the
	paused cue stays on the face ("Talleyrand: Improving... (paused)"); the
	tooltip holds the whole sentence."""
	if full_text.length() <= TALLEYRAND_SUMMARY_MAX_CHARS:
		return full_text
	var cut = full_text.find(TALLEYRAND_PAUSED_MARK)
	if cut > 0:
		var cue = TALLEYRAND_PAUSED_MARK + ")"
		var room = TALLEYRAND_SUMMARY_MAX_CHARS - cue.length() - 3
		var body = full_text.substr(0, cut)
		if body.length() > room:
			body = body.substr(0, room).rstrip(" ") + "..."
		return body + cue
	return full_text.substr(0, TALLEYRAND_SUMMARY_MAX_CHARS - 3).rstrip(" ") + "..."

var _audience_marshal := ""
var _generals_base_text := ""
var _generals_base_tooltip := ""

func update_audience_badge(audience) -> void:
	"""PC15-10 B1 "The Antechamber": a marshal waits to be heard — the
	Generals button says so (a count in its label, amber text, his name in
	its tooltip). Display only: his card's chip and the rail row open him."""
	var who := ""
	if audience is Dictionary:
		who = str(audience.get("marshal_display", audience.get("marshal", "")))
		if who == "<null>":
			who = ""
	if who == _audience_marshal:
		return
	if _generals_base_text == "":
		_generals_base_text = str(_nav_full_text.get("generals", generals_btn.text))
		_generals_base_tooltip = generals_btn.tooltip_text
	_audience_marshal = who
	if who != "":
		_nav_full_text["generals"] = _generals_base_text + " (1)"
		generals_btn.tooltip_text = (_generals_base_tooltip + "\n" + who
			+ " seeks an audience — open his card to hear him.").strip_edges()
	else:
		_nav_full_text["generals"] = _generals_base_text
		generals_btn.tooltip_text = _generals_base_tooltip
	if not _compact:
		generals_btn.text = str(_nav_full_text["generals"])
	_update_button_highlights()


func update_mailbox_count(envoy_count: int):
	"""Refresh the envoys button copy and styling."""
	_current_envoy_count = envoy_count
	if envoy_count > 0:
		mailbox_btn.text = str(envoy_count) if _fit_step >= 5 else "Envoys (" + str(envoy_count) + ")"
		mailbox_btn.tooltip_text = Utils.plural(envoy_count, "pending envoy") + (" awaits" if envoy_count == 1 else " await") + " your reply."
		# S14G-6 (Pre-Deploy S14h part 1, October 26, 2026): the badge says
		# the lock too - which court's letter shuts the Cabinet, in the one
		# sentence every surface uses (`Utils.cabinet_shut_line`). A lesser
		# court's routine letter shuts nothing and the badge says nothing of
		# the Cabinet for it (S14G-D3).
		if _cabinet_locked:
			mailbox_btn.tooltip_text += " " + Utils.cabinet_shut_lead(_cabinet_locked_by, true) + Utils.cabinet_shut_line(_cabinet_locked_until)
		mailbox_btn.add_theme_stylebox_override("normal", _mailbox_alert_style)
		mailbox_btn.add_theme_stylebox_override("hover", _mailbox_alert_hover_style)
		mailbox_btn.add_theme_color_override("font_color", Utils.UI_WARNING)
	else:
		mailbox_btn.text = "" if _fit_step >= 5 else "Envoys"
		mailbox_btn.tooltip_text = "No pending envoys."
		mailbox_btn.add_theme_stylebox_override("normal", _mailbox_idle_style)
		mailbox_btn.add_theme_stylebox_override("hover", _mailbox_idle_hover_style)
		mailbox_btn.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))


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
		# UXR3-F9 (Pre-Deploy S12 part 2): under blockade the border is
		# crimson, as the board's must_show and the chip's own words say
		# (it was the envoys' amber alert).
		admiralty_btn.add_theme_stylebox_override("normal", _blockade_style())
		admiralty_btn.add_theme_stylebox_override("hover", _blockade_style(true))
		admiralty_btn.add_theme_color_override("font_color", Utils.UI_ALERT)
	elif window:
		admiralty_btn.add_theme_stylebox_override("normal", _mailbox_alert_style)
		admiralty_btn.add_theme_stylebox_override("hover", _mailbox_alert_hover_style)
		admiralty_btn.add_theme_color_override("font_color", Utils.UI_GOLD)
	else:
		admiralty_btn.add_theme_stylebox_override("normal", _mailbox_idle_style)
		admiralty_btn.add_theme_stylebox_override("hover", _mailbox_idle_hover_style)
		admiralty_btn.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
	_refresh_admiralty_text()
	_queue_fit_right()


func _blockade_style(hover := false) -> StyleBoxFlat:
	var sb: StyleBoxFlat = _mailbox_alert_style.duplicate()
	sb.border_color = Utils.UI_ALERT
	sb.bg_color = Color(0.26, 0.09, 0.08, 1.0 if hover else 0.95)
	return sb


func _refresh_admiralty_text():
	if admiralty_btn == null or _admiralty_summary.is_empty():
		return
	var ships := int(_admiralty_summary.get("ships", 0))
	var blockaded := str(_admiralty_summary.get("blockaded_by", "")) != ""
	var window := int(_admiralty_summary.get("window_turns", 0)) > 0
	var text := "\u2693 " + str(ships)
	if not (_compact or _fit_step >= 4):
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
	if active_screen == screen_name or pinned_screen == screen_name:
		var open_node = screens[screen_name]
		if open_node.has_method("_switch_tab"):
			open_node._switch_tab(tab_index)
		return
	if active_screen != "":
		_close_screen(active_screen)
	_make_room_for(screen_name)
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


# UXR-2 (the layout law): the notice rail's slot — a fraction of the logical
# viewport between the authored 360 and a ceiling, under the bar, inset from
# the right edge. The authored .tscn offsets (-374 / 42 / -14 / 118) are the
# floor's own numbers; this writes them at run time.
const RAIL_WIDTH_FRACTION := 0.12
const RAIL_MIN_WIDTH := 360.0
const RAIL_MAX_WIDTH := 520.0
const RAIL_RIGHT_INSET := 14.0
const RAIL_GAP := 6.0
const RAIL_SLOT_HEIGHT := 76.0


func _on_bar_resized() -> void:
	var bar := get_node_or_null("BarContainer") as Control
	# A Text size change resizes the strip: re-decide compact first (its
	# threshold follows the text), then publish the height.
	_fit_bar()
	if bar != null and Utils.set_top_bar_drawn(bar.size.y):
		_fit_rail()
		bar_height_changed.emit()


func refit_hud_band() -> void:
	"""UXR-D3: Settings → HUD width changed — the clusters and the rail slot
	re-measure the band."""
	_fit_bar()
	_fit_rail()


func _fit_rail() -> void:
	if notification_area == null or not is_instance_valid(notification_area):
		return
	var view := get_viewport().get_visible_rect().size
	# UXR-D3: a fraction of the HUD band, inset from the band's right edge.
	var band := Utils.hud_band(view)
	var w := Utils.fraction_px(band.y - band.x, RAIL_WIDTH_FRACTION, RAIL_MIN_WIDTH, RAIL_MAX_WIDTH,
			2.0 * RAIL_RIGHT_INSET)
	notification_area.offset_right = -RAIL_RIGHT_INSET - (view.x - band.y)
	notification_area.offset_left = notification_area.offset_right - w
	notification_area.offset_top = Utils.TOP_BAR_HEIGHT + RAIL_GAP + Utils.top_bar_growth()
	notification_area.offset_bottom = notification_area.offset_top + RAIL_SLOT_HEIGHT


func _fit_bar():
	"""IQ10-X1: fit the bar to the LOGICAL viewport. Below COMPACT_BELOW_PX the
	nav buttons go icon-only (their tooltips carry the name and both hotkeys),
	the Cabinet line hides and the Admiralty chip keeps the count alone."""
	var view := get_viewport().get_visible_rect().size
	# UXR-D3: the clusters live in the HUD band (the pads are 0 at Full).
	# UXR-D4: the whole band — the strip runs above the Side Desk's dock.
	var band := Utils.hud_band_full(view)
	if _band_pad_left != null:
		_band_pad_left.custom_minimum_size.x = band.x
		_band_pad_right.custom_minimum_size.x = view.x - band.y
	var width := band.y - band.x
	# UXR-D1: the full-text bar's width grows with Text size (it overran a
	# 1920-px screen at 175 %), so the threshold grows with it.
	var compact := width < COMPACT_BELOW_PX * Utils.text_size_factor()
	if compact == _compact and not _nav_full_text.is_empty() and _fit_applied:
		return
	_compact = compact
	_fit_applied = true
	for sname in button_map:
		var btn: Button = button_map[sname]
		var glyph: Texture2D = _nav_icons.get(sname, null)
		if compact:
			# The glyph alone, at its own width (EA-E1) — or the hotkey letter
			# where no glyph loaded, so the bar never shows a blank square.
			btn.icon = glyph
			btn.text = "" if glyph != null else str(HOTKEY_HINTS.get(sname, ""))
		else:
			btn.icon = null
			btn.text = str(_nav_full_text.get(sname, btn.text))
	if talleyrand_label:
		talleyrand_label.visible = not compact
	_refresh_admiralty_text()
	_refresh_authority_text()
	_refresh_treasury_text()
	_queue_fit_right()


var _fit_applied := false
var _band_pad_left: Control = null
var _band_pad_right: Control = null

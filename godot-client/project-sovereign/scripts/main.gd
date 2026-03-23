extends Control

# =============================================================================
# PROJECT SOVEREIGN - Main UI Controller
# =============================================================================
# Handles command input, output display, and status updates
# Color scheme: Dark blue background, gold accents, cream text
# =============================================================================

# UI References - Header Status
@onready var turn_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/TurnDisplay/TurnValue
@onready var actions_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/ActionsDisplay/ActionsValue
@onready var admin_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/AdminDisplay/AdminValue
@onready var gold_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/GoldDisplay/GoldValue
@onready var inf_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/ManpowerDisplay/InfValue
@onready var cav_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/ManpowerDisplay/CavValue
@onready var art_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/ManpowerDisplay/ArtValue

# UI References - Main Interface
@onready var output_scroll = $BottomLeftUI/MainMargin/MainLayout/OutputScroll
@onready var output_display = $BottomLeftUI/MainMargin/MainLayout/OutputScroll/OutputDisplay
@onready var command_input = $BottomLeftUI/MainMargin/MainLayout/InputSection/CommandInput
@onready var send_button = $BottomLeftUI/MainMargin/MainLayout/InputSection/SendButton
@onready var diplomacy_button = $BottomLeftUI/MainMargin/MainLayout/InputSection/DiplomacyButton
@onready var end_turn_button = $BottomLeftUI/MainMargin/MainLayout/InputSection/EndTurnButton

# UI References - Minimize/Restore
@onready var bottom_left_ui = $BottomLeftUI
@onready var minimize_button = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/TitleRow/MinimizeButton
@onready var restore_button = $RestoreButton
# Top Bar (Session A)
var top_bar = null

# Map reference
@onready var map_area = $MapArea

# Objection Dialog
var objection_dialog = null

# Redemption Dialog
var redemption_dialog = null

# Enemy Phase Dialog
var enemy_phase_dialog = null
var pending_enemy_phase_response = null  # Store response to check game_over after dismissal

# Morning Dispatch — stored for display after all dialogs are dismissed
var pending_dispatch_data = null

# Glorious Charge Dialog (Phase 3 Cavalry Recklessness)
var glorious_charge_dialog = null

# Capture Choice Dialog (Phase 6.2.E Plunder/Secure)
var capture_choice_dialog = null

# Load Game Dialog (Phase 6: Save/Load)
var load_dialog = null

# Strategic Command Dialogs (Phase J)
var strategic_report_popup = null
var interrupt_popup = null
var clarification_popup = null
var pending_strategic_response = null  # Store response for post-report flow
var interrupt_queue: Array = []  # Queue of interrupts to show one at a time

# Session 8C Diplomatic Popups
var coalition_declaration_popup = null
var incoming_proposal_popup = null
var talleyrand_objection_popup = null
var sabotage_discovery_popup = null
var talleyrand_redemption_popup = null
var vassal_rebellion_popup = null
var proposal_confirm_popup = null

# Diplomacy Wizard (Diplomacy Button Session B)
var diplomacy_wizard = null

# War Status Panel (N4: HUD Layer 1 + Detail Layer 2)
var war_status_panel = null
var war_detail_popup = null
var _cached_wars: Array = []
var _cached_coalition_data = null
var _has_active_wars: bool = false

# Pause Menu (Phase 6.5)
var pause_menu = null

# Campaign Log (Phase 6.5)
var campaign_log = null

# Notification Bar (Phase 6.5)
var notification_bar = null

# API Client
var api_client = null

# Game state tracking
var actions_remaining = 4
var max_actions = 4
var admin_actions_remaining = 2
var max_admin_actions = 2
var current_turn = 1
var max_turns = 40
var gold = 1200
var infantry_pool = 80000
var cavalry_pool = 15000
var artillery_pool = 10000
var pending_redemption = false  # True when awaiting redemption choice

# Command history (up/down arrow navigation)
var command_history: Array = []
var history_index: int = -1  # -1 means "new command mode"
const MAX_HISTORY = 10

# Color palette (Napoleonic theme)
const COLOR_GOLD = "d9c08c"        # Gold for titles, important text
const COLOR_COMMAND = "7eb8da"     # Light blue for player commands
const COLOR_SUCCESS = "8fbc8f"     # Soft green for success
const COLOR_ERROR = "cd6b6b"       # Muted red for errors
const COLOR_BATTLE = "daa06d"      # Orange/amber for battle results
const COLOR_INFO = "a0a0a8"        # Gray for system info
const COLOR_MARSHAL = "c9b8e0"     # Lavender for marshal responses
const COLOR_CONQUEST = "90d890"    # Bright green for conquests
const COLOR_FEEDBACK = "b8a0d9"    # Soft purple/lavender for AI feedback
const COLOR_DISPATCH = "c9b878"    # Warm gold for field dispatches (MILD flavor)
const COLOR_BERTHIER = "B8860B"    # Dark goldenrod for Berthier dispatch headers
const COLOR_OBSERVATION = "DAA520"  # Goldenrod for Berthier closing notes

# Message history limit (prevents infinite growth)
const MAX_MESSAGES = 100
var message_count = 0

func _ready():
	# Create API client
	api_client = load("res://scripts/api_client.gd").new()
	add_child(api_client)

	# Load and setup Objection Dialog
	print("🔧 Loading ObjectionDialog scene...")
	var dialog_scene = load("res://scenes/objection_dialog.tscn")
	if dialog_scene == null:
		push_error("❌ FAILED to load objection_dialog.tscn!")
		print("❌ FAILED to load objection_dialog.tscn!")
	else:
		print("✓ Scene loaded, instantiating...")
		objection_dialog = dialog_scene.instantiate()
		if objection_dialog == null:
			push_error("❌ FAILED to instantiate ObjectionDialog!")
			print("❌ FAILED to instantiate ObjectionDialog!")
		else:
			print("✓ Dialog instantiated, adding to tree...")
			add_child(objection_dialog)
			objection_dialog.choice_made.connect(_on_objection_choice_made)
			print("✓ ObjectionDialog ready! Node: ", objection_dialog.name)
			print("  In tree: ", objection_dialog.is_inside_tree())
			print("  Visible: ", objection_dialog.visible)

	# Load and setup Redemption Dialog
	print("🔧 Loading RedemptionDialog scene...")
	var redemption_scene = load("res://scenes/redemption_dialog.tscn")
	if redemption_scene == null:
		push_error("❌ FAILED to load redemption_dialog.tscn!")
		print("❌ FAILED to load redemption_dialog.tscn!")
	else:
		print("✓ Redemption scene loaded, instantiating...")
		redemption_dialog = redemption_scene.instantiate()
		if redemption_dialog == null:
			push_error("❌ FAILED to instantiate RedemptionDialog!")
			print("❌ FAILED to instantiate RedemptionDialog!")
		else:
			print("✓ Redemption dialog instantiated, adding to tree...")
			add_child(redemption_dialog)
			redemption_dialog.choice_made.connect(_on_redemption_choice_made)
			print("✓ RedemptionDialog ready!")

	# Load and setup Enemy Phase Dialog
	print("🔧 Loading EnemyPhaseDialog scene...")
	var enemy_phase_scene = load("res://scenes/enemy_phase_dialog.tscn")
	if enemy_phase_scene == null:
		push_error("❌ FAILED to load enemy_phase_dialog.tscn!")
		print("❌ FAILED to load enemy_phase_dialog.tscn!")
	else:
		print("✓ Enemy phase scene loaded, instantiating...")
		enemy_phase_dialog = enemy_phase_scene.instantiate()
		if enemy_phase_dialog == null:
			push_error("❌ FAILED to instantiate EnemyPhaseDialog!")
			print("❌ FAILED to instantiate EnemyPhaseDialog!")
		else:
			print("✓ Enemy phase dialog instantiated, adding to tree...")
			add_child(enemy_phase_dialog)
			enemy_phase_dialog.dismissed.connect(_on_enemy_phase_dismissed)
			print("✓ EnemyPhaseDialog ready!")

	# Load and setup Glorious Charge Dialog (Phase 3 Cavalry Recklessness)
	print("🔧 Loading GloriousChargeDialog scene...")
	var glorious_charge_scene = load("res://scenes/glorious_charge_dialog.tscn")
	if glorious_charge_scene == null:
		push_error("❌ FAILED to load glorious_charge_dialog.tscn!")
		print("❌ FAILED to load glorious_charge_dialog.tscn!")
	else:
		print("✓ Glorious charge scene loaded, instantiating...")
		glorious_charge_dialog = glorious_charge_scene.instantiate()
		if glorious_charge_dialog == null:
			push_error("❌ FAILED to instantiate GloriousChargeDialog!")
			print("❌ FAILED to instantiate GloriousChargeDialog!")
		else:
			print("✓ Glorious charge dialog instantiated, adding to tree...")
			add_child(glorious_charge_dialog)
			glorious_charge_dialog.choice_made.connect(_on_glorious_charge_choice_made)
			print("✓ GloriousChargeDialog ready!")

	# Load and setup Capture Choice Dialog (Phase 6.2.E Plunder/Secure)
	var capture_choice_scene = load("res://scenes/capture_choice_dialog.tscn")
	if capture_choice_scene:
		capture_choice_dialog = capture_choice_scene.instantiate()
		add_child(capture_choice_dialog)
		capture_choice_dialog.choice_made.connect(_on_capture_choice_made)
		print("✓ CaptureChoiceDialog ready!")

	# Load and setup Load Game Dialog (Phase 6: Save/Load)
	var load_dialog_scene = load("res://scenes/load_dialog.tscn")
	if load_dialog_scene:
		load_dialog = load_dialog_scene.instantiate()
		add_child(load_dialog)
		load_dialog.save_selected.connect(_on_load_save_selected)
		load_dialog.load_cancelled.connect(_on_load_cancelled)
		print("LoadDialog ready!")

	# Load and setup Strategic Report Popup (Phase J)
	var strategic_report_scene = load("res://scenes/strategic_report_popup.tscn")
	if strategic_report_scene:
		strategic_report_popup = strategic_report_scene.instantiate()
		add_child(strategic_report_popup)
		strategic_report_popup.dismissed.connect(_on_strategic_report_dismissed)
		print("✓ StrategicReportPopup ready!")

	# Load and setup Interrupt Popup (Phase J)
	var interrupt_scene = load("res://scenes/interrupt_popup.tscn")
	if interrupt_scene:
		interrupt_popup = interrupt_scene.instantiate()
		add_child(interrupt_popup)
		interrupt_popup.choice_made.connect(_on_interrupt_choice_made)
		print("✓ InterruptPopup ready!")

	# Load and setup Clarification Popup (Phase J)
	var clarification_scene = load("res://scenes/clarification_popup.tscn")
	if clarification_scene:
		clarification_popup = clarification_scene.instantiate()
		add_child(clarification_popup)
		clarification_popup.clarification_choice.connect(_on_clarification_choice_made)
		clarification_popup.cancelled.connect(_on_clarification_cancelled)
		print("✓ ClarificationPopup ready!")

	# ── Session 8C Diplomatic Popups ──
	var coalition_decl_scene = load("res://scenes/coalition_declaration_popup.tscn")
	if coalition_decl_scene:
		coalition_declaration_popup = coalition_decl_scene.instantiate()
		add_child(coalition_declaration_popup)
		coalition_declaration_popup.dismissed.connect(_on_coalition_popup_dismissed)
		print("✓ CoalitionDeclarationPopup ready!")

	var incoming_prop_scene = load("res://scenes/incoming_proposal_popup.tscn")
	if incoming_prop_scene:
		incoming_proposal_popup = incoming_prop_scene.instantiate()
		add_child(incoming_proposal_popup)
		incoming_proposal_popup.choice_made.connect(_on_incoming_proposal_choice)
		print("✓ IncomingProposalPopup ready!")

	var proposal_confirm_scene = load("res://scenes/proposal_confirm_popup.tscn")
	if proposal_confirm_scene:
		proposal_confirm_popup = proposal_confirm_scene.instantiate()
		add_child(proposal_confirm_popup)
		proposal_confirm_popup.choice_made.connect(_on_proposal_confirm_choice)
		print("✓ ProposalConfirmPopup ready!")

	var talleyrand_obj_scene = load("res://scenes/talleyrand_objection_popup.tscn")
	if talleyrand_obj_scene:
		talleyrand_objection_popup = talleyrand_obj_scene.instantiate()
		add_child(talleyrand_objection_popup)
		talleyrand_objection_popup.choice_made.connect(_on_talleyrand_objection_choice)
		print("✓ TalleyrandObjectionPopup ready!")

	var sabotage_scene = load("res://scenes/sabotage_discovery_popup.tscn")
	if sabotage_scene:
		sabotage_discovery_popup = sabotage_scene.instantiate()
		add_child(sabotage_discovery_popup)
		sabotage_discovery_popup.choice_made.connect(_on_sabotage_discovery_choice)
		print("✓ SabotageDiscoveryPopup ready!")

	var redemption_scene_8c = load("res://scenes/talleyrand_redemption_popup.tscn")
	if redemption_scene_8c:
		talleyrand_redemption_popup = redemption_scene_8c.instantiate()
		add_child(talleyrand_redemption_popup)
		talleyrand_redemption_popup.choice_made.connect(_on_talleyrand_redemption_choice)
		print("✓ TalleyrandRedemptionPopup ready!")

	var vassal_rebel_scene = load("res://scenes/vassal_rebellion_popup.tscn")
	if vassal_rebel_scene:
		vassal_rebellion_popup = vassal_rebel_scene.instantiate()
		add_child(vassal_rebellion_popup)
		vassal_rebellion_popup.choice_made.connect(_on_vassal_rebellion_choice)
		print("✓ VassalRebellionPopup ready!")

	# ── Diplomacy Wizard (Session B) ──
	var diplomacy_wizard_scene = load("res://scenes/diplomacy_wizard.tscn")
	if diplomacy_wizard_scene:
		diplomacy_wizard = diplomacy_wizard_scene.instantiate()
		add_child(diplomacy_wizard)
		diplomacy_wizard.command_selected.connect(_on_wizard_command_selected)
		print("✓ DiplomacyWizard ready!")

	# ── War Status Panel (N4: HUD + Detail Popup) ──
	var war_panel_scene = load("res://scenes/war_status_panel.tscn")
	if war_panel_scene:
		war_status_panel = war_panel_scene.instantiate()
		add_child(war_status_panel)
		war_status_panel.card_clicked.connect(_on_war_card_clicked)
		war_status_panel.coalition_header_clicked.connect(_on_coalition_header_clicked)
		print("War StatusPanel ready!")

	var war_detail_scene = load("res://scenes/war_detail_popup.tscn")
	if war_detail_scene:
		war_detail_popup = war_detail_scene.instantiate()
		add_child(war_detail_popup)
		war_detail_popup.negotiate_clicked.connect(_on_war_negotiate_clicked)
		war_detail_popup.target_clicked.connect(_on_war_target_clicked)
		print("War DetailPopup ready!")

	# Load and setup Pause Menu (Phase 6.5)
	var pause_menu_scene = load("res://scenes/pause_menu.tscn")
	if pause_menu_scene:
		pause_menu = pause_menu_scene.instantiate()
		add_child(pause_menu)
		pause_menu.save_requested.connect(_on_pause_save_requested)
		pause_menu.load_requested.connect(_on_pause_load_requested)
		print("✓ PauseMenu ready!")

	# Load and setup Top Bar (Session A)
	var top_bar_scene = load("res://scenes/top_bar.tscn")
	if top_bar_scene:
		top_bar = top_bar_scene.instantiate()
		add_child(top_bar)
		top_bar.set_api_client(api_client)
		top_bar.screen_changed.connect(_on_screen_changed)
		top_bar.envoy_clicked.connect(_on_envoy_clicked)
		print("✓ TopBar ready!")

	# Load and setup Campaign Log (Phase 6.5)
	var campaign_log_scene = load("res://scenes/campaign_log.tscn")
	if campaign_log_scene:
		campaign_log = campaign_log_scene.instantiate()
		add_child(campaign_log)
		print("✓ CampaignLog ready!")

	# Register campaign log with top bar
	if top_bar and campaign_log:
		top_bar.register_screen("event_log", campaign_log)

	# Load and setup Dispatch View (Session A)
	var dispatch_view_scene = load("res://scenes/dispatch_view.tscn")
	if dispatch_view_scene:
		var dispatch_view = dispatch_view_scene.instantiate()
		add_child(dispatch_view)
		if top_bar:
			top_bar.register_screen("dispatch", dispatch_view)
		print("✓ DispatchView ready!")

	# Load and setup Strategic Ledger (Session B)
	var ledger_scene = load("res://scenes/strategic_ledger.tscn")
	if ledger_scene:
		var strategic_ledger = ledger_scene.instantiate()
		add_child(strategic_ledger)
		if top_bar:
			top_bar.register_screen("ledger", strategic_ledger)
		print("✓ StrategicLedger ready!")

	# Load and setup Marshal Management (Phase 6.5)
	var marshal_mgmt_scene = load("res://scenes/marshal_management.tscn")
	if marshal_mgmt_scene:
		var marshal_management = marshal_mgmt_scene.instantiate()
		add_child(marshal_management)
		if top_bar:
			top_bar.register_screen("generals", marshal_management)
		print("✓ MarshalManagement ready!")

	# Load and setup Diplomatic Ledger (Session 8B)
	var diplo_ledger_scene = load("res://scenes/diplomatic_ledger.tscn")
	if diplo_ledger_scene:
		var diplomatic_ledger = diplo_ledger_scene.instantiate()
		add_child(diplomatic_ledger)
		if top_bar:
			top_bar.register_screen("diplomatic_ledger", diplomatic_ledger)
		print("✓ DiplomaticLedger ready!")

	# Load and setup Notification Bar (Phase 6.5) — reparented into top bar
	var notification_bar_scene = load("res://scenes/notification_bar.tscn")
	if notification_bar_scene:
		notification_bar = notification_bar_scene.instantiate()
		if top_bar and top_bar.notification_area:
			top_bar.notification_area.add_child(notification_bar)
		else:
			add_child(notification_bar)
		notification_bar.set_api_client(api_client)
		print("✓ NotificationBar ready!")

	# Connect signals
	if not send_button.pressed.is_connected(_on_send_button_pressed):
		send_button.pressed.connect(_on_send_button_pressed)

	if not command_input.text_submitted.is_connected(_on_command_submitted):
		command_input.text_submitted.connect(_on_command_submitted)

	if not end_turn_button.pressed.is_connected(_on_end_turn_pressed):
		end_turn_button.pressed.connect(_on_end_turn_pressed)

	if not diplomacy_button.pressed.is_connected(_on_diplomacy_button_pressed):
		diplomacy_button.pressed.connect(_on_diplomacy_button_pressed)

	if not command_input.gui_input.is_connected(_on_command_input_gui_input):
		command_input.gui_input.connect(_on_command_input_gui_input)

	# Minimize/Restore terminal panel
	if not minimize_button.pressed.is_connected(_minimize_terminal):
		minimize_button.pressed.connect(_minimize_terminal)
	if not restore_button.pressed.is_connected(_restore_terminal):
		restore_button.pressed.connect(_restore_terminal)

	# Start disabled until connected
	set_input_enabled(false)

	# Welcome message
	_show_welcome()

	# Test connection after brief delay
	await get_tree().create_timer(0.5).timeout
	test_connection()

func _show_welcome():
	"""Display welcome message with proper formatting."""
	add_output("")
	add_output("[color=#" + COLOR_GOLD + "][b]═══════════════════════════════════════[/b][/color]")
	add_output("[color=#" + COLOR_GOLD + "][b]        IMPERIAL HEADQUARTERS[/b][/color]")
	add_output("[color=#" + COLOR_GOLD + "][b]═══════════════════════════════════════[/b][/color]")
	add_output("")
	add_output("[color=#" + COLOR_INFO + "]June 1815 — The Hundred Days Campaign[/color]")
	add_output("[color=#" + COLOR_INFO + "]You are Napoleon Bonaparte.[/color]")
	add_output("")

func test_connection():
	"""Test if backend is running."""
	add_output("[color=#" + COLOR_INFO + "]Establishing connection to headquarters...[/color]")
	api_client.test_connection(_on_connection_test)

func _on_connection_test(response):
	"""Handle connection test response."""
	if response.success:
		add_output("[color=#" + COLOR_SUCCESS + "]✓ Communications established![/color]")
		add_output("")

		# Update status from server
		if response.has("action_summary"):
			_update_status(response.action_summary)
		if response.has("gold"):
			gold = int(response.gold)
			_update_gold_display()
		if response.has("manpower_pools"):
			_apply_manpower(response.manpower_pools)

		# Update diplomatic top bar fields (Session 8B)
		_update_diplomatic_top_bar(response)

		# N4i: Initialize war status HUD on game start
		_process_active_wars(response)

		# Update map with initial state
		if response.has("game_state") and response.game_state.has("map_data"):
			print("MAIN: Connection test - map_data found, updating map")
			print("MAIN: map_data keys: ", response.game_state.map_data.keys())
			map_area.update_all_regions(response.game_state.map_data)
		else:
			print("⚠️  MAIN: Connection test - NO map_data in response!")
			if response.has("game_state"):
				print("     game_state keys: ", response.game_state.keys())

		# Show instructions
		add_output("[color=#" + COLOR_INFO + "]Your marshals await your orders, Sire.[/color]")
		add_output("")
		add_output("[color=#" + COLOR_INFO + "]Commands:[/color]")
		add_output("[color=#" + COLOR_INFO + "]  • \"Ney, attack Wellington\"[/color]")
		add_output("[color=#" + COLOR_INFO + "]  • \"scout Rhine\" or \"move to Belgium\"[/color]")
		add_output("[color=#" + COLOR_INFO + "]  • \"recruit\" or \"end turn\"[/color]")
		add_output("")
		_add_separator()
		
		set_input_enabled(true)
	else:
		add_output("[color=#" + COLOR_ERROR + "]✗ Cannot reach headquarters![/color]")
		add_output("[color=#" + COLOR_INFO + "]Start the Python server: python backend/main.py[/color]")
		add_output("")

func _on_send_button_pressed():
	"""Handle send button click."""
	_execute_command()

func _on_command_submitted(_text: String):
	"""Handle enter key in command input."""
	_execute_command()

func _on_command_input_gui_input(event):
	"""Handle special keys in command input."""
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_F1:
			_open_diplomacy_wizard()
			command_input.accept_event()
		elif event.keycode == KEY_UP:
			_history_previous()
			command_input.accept_event()  # Consume event, prevent camera movement
		elif event.keycode == KEY_DOWN:
			_history_next()
			command_input.accept_event()  # Consume event, prevent camera movement
		elif event.keycode == KEY_ESCAPE:
			command_input.release_focus()  # Unfocus to allow camera controls
			command_input.accept_event()

func _history_previous():
	"""Navigate to previous command in history (up arrow)."""
	if command_history.is_empty():
		return

	if history_index == -1:
		# Start from most recent
		history_index = command_history.size() - 1
	elif history_index > 0:
		# Go further back
		history_index -= 1
	# else: already at oldest, stay there

	command_input.text = command_history[history_index]
	command_input.caret_column = command_input.text.length()

func _history_next():
	"""Navigate to next command in history (down arrow)."""
	if history_index == -1:
		# Already in new command mode
		return

	if history_index < command_history.size() - 1:
		# Go forward in history
		history_index += 1
		command_input.text = command_history[history_index]
		command_input.caret_column = command_input.text.length()
	else:
		# At newest, return to new command mode (clear)
		history_index = -1
		command_input.text = ""

func _add_to_history(command: String):
	"""Add command to history if valid."""
	if command.is_empty():
		return

	# Don't add if same as last command
	if not command_history.is_empty() and command_history.back() == command:
		return

	command_history.append(command)

	# Trim to max size
	while command_history.size() > MAX_HISTORY:
		command_history.pop_front()

	# Reset to new command mode
	history_index = -1

func _on_end_turn_pressed():
	"""Handle End Turn button click."""
	_execute_end_turn()

func _unhandled_input(event):
	"""Handle hotkeys when command input is not focused."""
	if event is InputEventKey and event.pressed and not event.echo:
		# ═══ ESC KEY: Smart context-aware (Phase 6.5 + Session A) ═══
		# Priority: 1) release focus (gui_input), 2) close screen, 3) close pause, 4) open pause
		if event.keycode == KEY_ESCAPE:
			if top_bar and top_bar.is_screen_open():
				top_bar.close_all_screens()
				get_viewport().set_input_as_handled()
				return
			if pause_menu and pause_menu.visible:
				pause_menu.close_menu()
			elif not _is_modal_dialog_open():
				if pause_menu:
					pause_menu.open_menu()
			get_viewport().set_input_as_handled()
			return

		# Block all hotkeys while pause menu is open
		if pause_menu and pause_menu.visible:
			get_viewport().set_input_as_handled()
			return

		# ═══ F1: DIPLOMACY WIZARD — works even when input focused ═══
		if event.keycode == KEY_F1:
			if not _is_modal_dialog_open():
				_open_diplomacy_wizard()
			get_viewport().set_input_as_handled()
			return

		# ═══ SCREEN HOTKEYS (L, T, G, D, R) — work even when a screen is open ═══
		# Only blocked by modal dialogs or text input focus
		if event.keycode == KEY_L:
			if not _is_hotkey_blocked():
				if top_bar:
					top_bar.toggle_screen("event_log")
				get_viewport().set_input_as_handled()
			return
		if event.keycode == KEY_T:
			if not _is_hotkey_blocked():
				if top_bar:
					top_bar.toggle_screen("ledger")
				get_viewport().set_input_as_handled()
			return
		if event.keycode == KEY_G:
			if not _is_hotkey_blocked():
				if top_bar and top_bar.screens.has("generals") and top_bar.screens["generals"] != null:
					top_bar.toggle_screen("generals")
				get_viewport().set_input_as_handled()
			return
		if event.keycode == KEY_D:
			if not _is_hotkey_blocked():
				if top_bar:
					top_bar.toggle_screen("diplomatic_ledger")
				get_viewport().set_input_as_handled()
			return
		if event.keycode == KEY_R:
			if not _is_hotkey_blocked():
				if top_bar:
					top_bar.toggle_screen("dispatch")
				get_viewport().set_input_as_handled()
			return

		# ═══ MAP / GAME HOTKEYS — blocked when screen is open ═══
		if _is_screen_open():
			return

		# E key for End Turn (only when not typing in command input)
		if event.keycode == KEY_E:
			if not command_input.has_focus() and end_turn_button.visible and not end_turn_button.disabled:
				_execute_end_turn()
				get_viewport().set_input_as_handled()
		# Tab key to toggle terminal panel
		elif event.keycode == KEY_TAB:
			if not command_input.has_focus():
				_toggle_terminal()
				get_viewport().set_input_as_handled()

func _minimize_terminal():
	"""Collapse the terminal panel, show restore button."""
	bottom_left_ui.visible = false
	restore_button.visible = true

func _restore_terminal():
	"""Expand the terminal panel, hide restore button."""
	bottom_left_ui.visible = true
	restore_button.visible = false

func _toggle_terminal():
	"""Toggle terminal panel visibility."""
	if bottom_left_ui.visible:
		_minimize_terminal()
	else:
		_restore_terminal()

func _execute_end_turn():
	"""Execute end turn command."""
	# Add to history
	_add_to_history("end turn")

	# Display the command
	add_output("")
	add_output("[color=#" + COLOR_COMMAND + "]► end turn[/color]")

	# Disable input while processing
	set_input_enabled(false)

	# Send to backend
	api_client.send_command("end turn", _on_command_result)

func _execute_command():
	"""Execute the command in the input field."""
	var command = command_input.text.strip_edges()

	if command.is_empty():
		return

	# Add to history before clearing
	_add_to_history(command)

	# Display player command with prompt styling
	add_output("")
	add_output("[color=#" + COLOR_COMMAND + "]► " + command + "[/color]")

	# Clear input
	command_input.text = ""

	# ════════════════════════════════════════════════════════════
	# CHECK FOR REDEMPTION COMMAND: Handle redemption choices
	# ════════════════════════════════════════════════════════════
	var redemption_choices = ["grant_autonomy", "dismiss", "demand_obedience"]
	if command.to_lower() in redemption_choices:
		print("REDEMPTION COMMAND DETECTED: ", command)
		set_input_enabled(false)
		api_client.send_redemption_response(command.to_lower(), _on_redemption_response)
		return

	# Disable input while processing
	set_input_enabled(false)

	# Send to backend
	api_client.send_command(command, _on_command_result)

func _on_command_result(response):
	"""Handle command execution result."""
	# ═══════════════════════════════════════════════════════════
	# DEBUG TRACE: Exact step-by-step debugging
	# ═══════════════════════════════════════════════════════════
	print("\n" + "=".repeat(60))
	print("1. GOT RESPONSE: ", response)
	print("=".repeat(60))
	print("2. HAS 'state' key: ", response.has("state"))
	print("2b. HAS 'awaiting_player_choice' key: ", response.has("awaiting_player_choice"))
	if response.has("state"):
		print("3. STATE VALUE: ", response.state)
		print("3b. STATE == 'awaiting_player_choice': ", response.state == "awaiting_player_choice")
	print("3c. response.success: ", response.get("success", false))
	print("=".repeat(60) + "\n")

	# Check for marshal objection FIRST (before re-enabling input)
	# Tactical objections: state == "awaiting_player_choice"
	# Strategic objections (Phase M): pending_objection == true
	var is_tactical_objection = response.get("success", false) and response.has("state") and response.state == "awaiting_player_choice"
	var is_strategic_objection = response.get("success", false) and response.has("pending_objection") and response.pending_objection == true
	var is_objection = is_tactical_objection or is_strategic_objection
	print("4. IS_OBJECTION CHECK: tactical=", is_tactical_objection, " strategic=", is_strategic_objection, " => ", is_objection)

	if is_objection:
		print("5. OBJECTION DETECTED - About to show dialog")
		print("6. DIALOG NODE: ", objection_dialog)
		print("7. DIALOG IN TREE: ", objection_dialog.is_inside_tree() if objection_dialog else "NULL")
		print("8. DIALOG VISIBLE BEFORE: ", objection_dialog.visible if objection_dialog else "NULL")
		_show_objection_dialog(response)
		return  # Don't re-enable input or continue processing
	else:
		print("5. No objection - continuing normal flow")

	# Check for Glorious Charge popup (Phase 3 Cavalry Recklessness)
	# This happens when a reckless cavalry marshal at recklessness 3 tries to attack
	print("GLORIOUS_CHARGE CHECK:")
	print("  response.has('pending_glorious_charge'): ", response.has("pending_glorious_charge"))
	if response.has("pending_glorious_charge"):
		print("  response.pending_glorious_charge VALUE: ", response.pending_glorious_charge)

	if response.has("pending_glorious_charge") and response.pending_glorious_charge:
		print(">>> GLORIOUS CHARGE CONDITION MET - calling _show_glorious_charge_dialog()")
		print(">>> glorious_charge_dialog is: ", glorious_charge_dialog)
		print(">>> glorious_charge_dialog == null: ", glorious_charge_dialog == null)
		_show_glorious_charge_dialog(response)
		return  # Don't re-enable input until choice made

	# Priority 3: Coalition Declaration Popup (Session 8C)
	if response.has("coalition_popup") and response.coalition_popup != null:
		if coalition_declaration_popup:
			coalition_declaration_popup.show_coalition(response.coalition_popup)
			return  # Don't re-enable input until dismissed

	# Check for capture choice (Phase 6.2.E: Plunder or Secure)
	if response.has("pending_capture_choice") and response.pending_capture_choice:
		_show_capture_choice_dialog(response)
		return  # Don't re-enable input until choice made

	# Check for load dialog request (Phase 6: Save/Load)
	if response.has("show_load_dialog") and response.show_load_dialog:
		_show_load_dialog()
		# Don't return — still show the save list message in terminal

	# Priority 5: Diplomatic Objection Popup (Session 8C)
	if response.has("diplomatic_objection") and response.diplomatic_objection != null:
		if talleyrand_objection_popup:
			talleyrand_objection_popup.show_objection(response.diplomatic_objection)
			return

	# Priority 6: Incoming Proposal Popup (Session 8C)
	if response.has("incoming_proposal") and response.incoming_proposal != null:
		if incoming_proposal_popup:
			incoming_proposal_popup.show_proposal(response.incoming_proposal)
			return

	# Priority 6.5: Player-initiated Proposal Confirm Popup
	# Catches diplomatic_dialogue returned by the outgoing proposal flow.
	if response.has("diplomatic_dialogue") and response.diplomatic_dialogue != null:
		var dialogue = response.diplomatic_dialogue
		var dtype = dialogue.get("type", "")
		# BUGFIX (Bug 4A): "terms_guidance" is generated by the adjust_terms flow
		# in executor.py (8 instances). Without this, selecting "Adjust terms"
		# causes a dead-end where the popup never shows and input stays disabled.
		# See BUGFIX_PLAN_PROPOSAL_FLOW.md.
		if dtype in ["proposal_confirm", "proposal_execute", "proposal_options",
			"mission", "feasibility", "advisory",
			"force_declare_war_confirmation", "conflict_alert",
			"terms_guidance"]:
			if proposal_confirm_popup:
				proposal_confirm_popup.show_dialogue(dialogue)
				return

	# Check for clarification request (Grouchy/literal marshal)
	if response.has("state") and response.state == "awaiting_clarification":
		_show_clarification_popup(response)
		return  # Don't re-enable input until choice made

	# Check for strategic interrupt (blocked path, cannon fire, etc.)
	if response.has("pending_interrupt") and response.pending_interrupt:
		_show_interrupt_popup(response.pending_interrupt)
		return  # Don't re-enable input until choice made

	# Priority 8: Sabotage Discovery Popup (Session 8C)
	if response.has("diplomatic_sabotage") and response.diplomatic_sabotage != null:
		if sabotage_discovery_popup:
			sabotage_discovery_popup.show_sabotage(response.diplomatic_sabotage)
			return

	# Priority 9: Talleyrand Redemption Popup (Session 8C)
	if response.has("talleyrand_redemption") and response.talleyrand_redemption != null:
		if talleyrand_redemption_popup:
			talleyrand_redemption_popup.show_redemption(response.talleyrand_redemption)
			return

	# Priority 10: Vassal Rebellion Imminent Popup (Session 8C)
	if response.has("vassal_rebellion_imminent") and response.vassal_rebellion_imminent != null:
		if vassal_rebellion_popup:
			vassal_rebellion_popup.show_rebellion(response.vassal_rebellion_imminent)
			return

	# Check for redemption event (bombardment friendly fire, cavalry, etc.)
	# End-turn responses with enemy_phase defer redemption to post-enemy-phase flow
	if response.has("redemption_event") and not response.has("enemy_phase"):
		if response.success:
			if response.has("action_summary"):
				_update_status(response.action_summary)
			if response.has("game_state") and response.game_state.has("gold"):
				gold = int(response.game_state.gold)
				_update_gold_display()
			if response.has("game_state") and response.game_state.has("manpower_pools"):
				_apply_manpower(response.game_state.manpower_pools)
			if response.has("game_state") and response.game_state.has("map_data"):
				map_area.update_all_regions(response.game_state.map_data)
			if notification_bar and response.has("notifications"):
				notification_bar.update_notifications(response.notifications)
			_display_result(response)
		_show_redemption_dialog(response.redemption_event)
		return  # Don't re-enable input until redemption resolved

	# Re-enable input
	set_input_enabled(true)

	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)

		# Update diplomatic top bar fields (Session 8B)
		_update_diplomatic_top_bar(response)

		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)

		# Update map with latest state
		if response.has("game_state") and response.game_state.has("map_data"):
			print("MAIN: Command result - map_data found, updating map")
			print("MAIN: Received map_data with ", response.game_state.map_data.keys().size(), " regions")
			map_area.update_all_regions(response.game_state.map_data)
		else:
			print("⚠️  MAIN: Command result - NO map_data in response!")
			if response.has("game_state"):
				print("     game_state keys: ", response.game_state.keys())

		# Format and display result based on event type
		_display_result(response)

		# Tactical events absorbed into Morning Dispatch (no separate display)

		# Update notification bar with any pending notifications
		# (must be before enemy_phase dialog check — that returns early)
		if notification_bar and response.has("notifications"):
			notification_bar.update_notifications(response.notifications)

		# Check for enemy phase (from end_turn)
		# NOTE: No total_actions > 0 gate — dialog shows even with 0 enemy actions
		# (e.g. debug freeze_enemies). The dialog handles 0-action case with
		# "No enemy actions this turn." message.
		if response.has("enemy_phase"):
			print("ENEMY PHASE DETECTED - showing dialog")
			# Close screens before showing modal (avoid stale screen behind dialog)
			if top_bar:
				top_bar.close_all_screens()
			set_input_enabled(false)  # Disable input until dismissed
			var turn = current_turn
			if response.has("action_summary"):
				turn = int(response.action_summary.get("turn", current_turn))
			pending_enemy_phase_response = response  # Store for post-enemy-phase flow
			_show_enemy_phase_dialog(response.enemy_phase, turn)
			return  # Don't re-enable input until dialog dismissed

		# V2a: Show MILD dispatches when no enemy phase dialog
		_show_mild_dispatches(response)

		# Check for strategic reports (when no enemy phase dialog)
		if response.has("strategic_reports") and not response.strategic_reports.is_empty():
			set_input_enabled(false)
			pending_strategic_response = response
			_show_strategic_reports(response)
			return  # Don't re-enable input until reports dismissed

		# Check for game over
		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return  # Don't auto-focus input

		# Morning Dispatch — displayed last, right before player gets control
		_show_pending_dispatch()

	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")

	# N4i: Update war status HUD on every response
	_process_active_wars(response)

	add_output("")

	# Auto-focus input
	command_input.grab_focus()

func _display_result(response):
	"""Display result with appropriate formatting based on event type."""
	var message = response.message
	var events = response.get("events", [])
	var action_info = response.get("action_info", {})
	
	# Determine event type for coloring
	var event_type = ""
	if events.size() > 0:
		var event = events[0]
		event_type = event.get("type", "")
		if event.get("marshal_switched", false):
			# Split message at double newline
			var parts = message.split("\n\n", true, 1)
			if parts.size() == 2:
				 # Color explanation differently
				add_output("[color=#" + COLOR_INFO + "]" + parts[0] + "[/color]")
				add_output("")
				message = parts[1]  # Rest of message

	# Color based on event type
	match event_type:
		"battle":
			_display_battle_result(message, events[0], action_info)
		"bombardment":
			add_output("[color=#" + COLOR_BATTLE + "]" + message + "[/color]")
			_show_action_cost(action_info)
		"conquest":
			add_output("[color=#" + COLOR_CONQUEST + "]⚑ " + message + "[/color]")
			_show_action_cost(action_info)
		"move":
			add_output("[color=#" + COLOR_SUCCESS + "]→ " + message + "[/color]")
			_show_action_cost(action_info)
		"scout":
			add_output("[color=#" + COLOR_INFO + "]👁 " + message + "[/color]")
			_show_action_cost(action_info)
		"recruit":
			add_output("[color=#" + COLOR_SUCCESS + "]+ " + message + "[/color]")
			_show_action_cost(action_info)
		"defend":
			add_output("[color=#" + COLOR_SUCCESS + "]⛨ " + message + "[/color]")
			_show_action_cost(action_info)
		"turn_end":
			_display_turn_change(events[0])
			# Morning Dispatch — stored for display after all dialogs (enemy phase, strategic reports)
			if response.has("morning_dispatch"):
				pending_dispatch_data = response.morning_dispatch
		_:
			add_output("[color=#" + COLOR_SUCCESS + "]" + message + "[/color]")
			_show_action_cost(action_info)

	# Reinforcement inline-dramatic display (Session 66) — before Berthier report
	if response.has("reinforcement_messages"):
		_display_reinforcement_messages(response.reinforcement_messages)

	# Berthier's After-Action Report — shown after any combat event type
	if response.has("battle_report"):
		_display_berthier_report(response.battle_report)

	# First-time coordination tutorial (Session 66)
	if response.has("coordination_tutorial"):
		_display_coordination_tutorial(response.coordination_tutorial)

	# Berthier's Bombardment Report — shown after bombardment actions
	if response.has("bombardment_result"):
		_display_bombardment_report(response.bombardment_result)

	# Berthier's Bombardment Advisory — shown when artillery crumbles enemy forts
	var bombardment_advisory = response.get("bombardment_advisory", "")
	if bombardment_advisory != "" and bombardment_advisory != null:
		add_output("[color=#" + COLOR_DISPATCH + "]  Berthier: \"" + str(bombardment_advisory) + "\"[/color]")
	
	# Check for turn advancement
	if action_info.get("turn_advanced", false):
		_display_turn_advance(action_info)

	# Display AI feedback if present (LLM mode only)
	if response.has("feedback"):
		_display_feedback(response.feedback)

func _display_battle_result(message: String, event: Dictionary, action_info: Dictionary):
	"""Display battle results with dramatic formatting."""
	var outcome = event.get("outcome", "")
	var victor = event.get("victor", "")
	var enemy_destroyed = event.get("enemy_destroyed", false)
	var region_conquered = event.get("region_conquered", false)

	# Battle header - use battle_name if available
	var battle_name = event.get("battle_name", "BATTLE")
	add_output("[color=#" + COLOR_BATTLE + "]⚔ " + battle_name + " ⚔[/color]")
	
	# Main result
	add_output("[color=#" + COLOR_BATTLE + "]" + message + "[/color]")

	# Cavalry terrain flavor (Phase 6.1: separate colored line for cavalry effectiveness)
	var cav_terrain_msg = event.get("cavalry_terrain_message", "")
	if cav_terrain_msg != "" and cav_terrain_msg != null:
		add_output("[color=#" + COLOR_DISPATCH + "]   🐴 " + cav_terrain_msg + "[/color]")

	# Special notifications
	if enemy_destroyed:
		add_output("[color=#" + COLOR_CONQUEST + "]   ★ Enemy army destroyed! ★[/color]")
	
	if region_conquered:
		var region_name = event.get("region_name", "territory")
		add_output("[color=#" + COLOR_CONQUEST + "]   ⚑ " + region_name + " captured! ⚑[/color]")
	
	_show_action_cost(action_info)

func _display_berthier_report(report: Dictionary):
	"""Display Berthier's After-Action Report with modifier breakdown and observation."""
	var COLOR_BERTHIER = "B8860B"   # Dark goldenrod for header
	var COLOR_REPORT = "CCCCCC"     # Light gray for report lines
	var COLOR_OBSERVATION = "DAA520" # Goldenrod for Berthier's quote

	add_output("[color=#" + COLOR_BERTHIER + "]--- Berthier's Report ---[/color]")

	# Modifier breakdown
	var breakdown = report.get("modifier_breakdown", {})

	# Attacker modifiers
	var atk_mods = breakdown.get("attacker", [])
	var casualty = report.get("casualty_summary", {})
	var atk_name = str(casualty.get("attacker_name", "Attacker"))
	if atk_mods.size() > 0:
		var atk_parts: Array = []
		for m in atk_mods:
			var sign = "+" if m.get("type", "") == "bonus" else "-"
			atk_parts.append(str(m.get("label", "")) + " " + sign + str(int(m.get("value", 0))) + "%")
		add_output("[color=#" + COLOR_REPORT + "]  Attack: " + atk_name + " (" + ", ".join(PackedStringArray(atk_parts)) + ")[/color]")

	# Defender modifiers
	var def_mods = breakdown.get("defender", [])
	var def_name = str(casualty.get("defender_name", "Defender"))
	if def_mods.size() > 0:
		var def_parts: Array = []
		for m in def_mods:
			var sign = "+" if m.get("type", "") == "bonus" else "-"
			def_parts.append(str(m.get("label", "")) + " " + sign + str(int(m.get("value", 0))) + "%")
		add_output("[color=#" + COLOR_REPORT + "]  Defense: " + def_name + " (" + ", ".join(PackedStringArray(def_parts)) + ")[/color]")

	# Casualty summary
	var atk_cas = int(casualty.get("attacker_casualties", 0))
	var def_cas = int(casualty.get("defender_casualties", 0))
	var atk_orig = int(casualty.get("attacker_original", 0))
	var atk_rem = int(casualty.get("attacker_remaining", 0))
	var def_orig = int(casualty.get("defender_original", 0))
	var def_rem = int(casualty.get("defender_remaining", 0))

	# Format with thousands separators
	add_output("[color=#" + COLOR_REPORT + "]  Casualties: " + atk_name + " " + _format_number(atk_cas) + " | " + def_name + " " + _format_number(def_cas) + "[/color]")
	add_output("[color=#" + COLOR_REPORT + "]  Strength: " + atk_name + " " + _format_number(atk_orig) + " -> " + _format_number(atk_rem) + " | " + def_name + " " + _format_number(def_orig) + " -> " + _format_number(def_rem) + "[/color]")

	# Berthier's observation
	var observation = str(report.get("observation", ""))
	if observation != "":
		add_output("[color=#" + COLOR_OBSERVATION + "]  Berthier: \"" + observation + "\"[/color]")

	add_output("")

func _display_reinforcement_messages(messages: Array):
	"""Display reinforcement arrival/failure as gold-bordered inline-dramatic blocks."""
	var COLOR_REINF_BORDER = "d9c08c"   # Gold border
	var COLOR_REINF_ARRIVE = "90d890"   # Green for arrivals
	var COLOR_REINF_FAIL = "cd6b6b"     # Red for failures

	for msg in messages:
		var text = str(msg)
		var is_arrival = text.find("arrived") >= 0
		if is_arrival:
			add_output("[color=#" + COLOR_REINF_BORDER + "]┌─── REINFORCEMENT ───┐[/color]")
			add_output("[color=#" + COLOR_REINF_ARRIVE + "]  " + text + "[/color]")
			add_output("[color=#" + COLOR_REINF_BORDER + "]└─────────────────────┘[/color]")
		else:
			add_output("[color=#" + COLOR_REINF_BORDER + "]┌─── REINFORCEMENT ───┐[/color]")
			add_output("[color=#" + COLOR_REINF_FAIL + "]  " + text + "[/color]")
			add_output("[color=#" + COLOR_REINF_BORDER + "]└─────────────────────┘[/color]")

func _display_coordination_tutorial(tutorial: Dictionary):
	"""Display first-time coordination tutorial as gold-bordered inline-dramatic block."""
	var COLOR_TUTORIAL_BORDER = "d9c08c"  # Gold border
	var COLOR_TUTORIAL_TITLE = "B8860B"   # Dark goldenrod
	var COLOR_TUTORIAL_TEXT = "DAA520"     # Goldenrod
	var COLOR_TUTORIAL_TIP = "8fbc8f"     # Soft green for tips
	var COLOR_TUTORIAL_WARN = "cd6b6b"    # Muted red for warning

	var title = str(tutorial.get("title", "BERTHIER'S REPORT"))
	var message = str(tutorial.get("message", ""))
	var tip = str(tutorial.get("tip", ""))
	var warning = str(tutorial.get("warning", ""))

	add_output("")
	add_output("[color=#" + COLOR_TUTORIAL_BORDER + "]┌─────────────────────────────────────────────────┐[/color]")
	add_output("[color=#" + COLOR_TUTORIAL_TITLE + "]  " + title + "[/color]")
	add_output("[color=#" + COLOR_TUTORIAL_BORDER + "]  ─────────────────────────────────────────────── [/color]")
	if message != "":
		add_output("[color=#" + COLOR_TUTORIAL_TEXT + "]  " + message + "[/color]")
		add_output("")
	if tip != "":
		add_output("[color=#" + COLOR_TUTORIAL_TIP + "]  " + tip + "[/color]")
		add_output("")
	if warning != "":
		add_output("[color=#" + COLOR_TUTORIAL_WARN + "]  " + warning + "[/color]")
	add_output("[color=#" + COLOR_TUTORIAL_BORDER + "]└─────────────────────────────────────────────────┘[/color]")
	add_output("")

func _display_bombardment_report(result: Dictionary):
	"""Display Berthier's bombardment report with casualty summary and observation."""
	var COLOR_BERTHIER = "B8860B"   # Dark goldenrod for header
	var COLOR_CASUALTY = "a0a0a8"   # Info gray for stats
	var COLOR_ENEMY_CAS = "cd5c5c"  # Red for enemy casualties
	var COLOR_OWN_CAS = "8fbc8f"    # Muted green for own (low) casualties
	var COLOR_TERRAIN = "b0a890"    # Warm gray for terrain info
	var COLOR_FORT = "daa06d"       # Battle orange for fort degradation
	var COLOR_OBSERVATION = "DAA520" # Goldenrod for Berthier's quote
	var COLOR_FRIENDLY = "cd6b6b"   # Muted red for friendly fire
	var COLOR_REMAINING = "a0a0a8"  # Info gray for remaining count

	add_output("[color=#" + COLOR_BERTHIER + "]--- Bombardment Report ---[/color]")

	# Attacker (artillery) casualties
	var atk = result.get("attacker", {})
	var atk_name = str(atk.get("name", "Artillery"))
	var atk_cas = int(atk.get("casualties", 0))
	var atk_rem = int(atk.get("remaining", 0))

	# Defender casualties
	var defn = result.get("defender", {})
	var def_name = str(defn.get("name", "Enemy"))
	var def_cas = int(defn.get("casualties", 0))
	var def_rem = int(defn.get("remaining", 0))
	var def_morale = int(defn.get("morale", 100))

	# Terrain effectiveness
	var terrain_name = str(result.get("terrain", "plains")).replace("_", " ").capitalize()
	var terrain_mod = result.get("terrain_modifier", 1.0)
	# terrain_mod may be a float — display as percentage
	var terrain_pct = int(terrain_mod * 100)
	var terrain_label = ""
	if terrain_pct > 100:
		terrain_label = terrain_name + " (+" + str(terrain_pct - 100) + "% damage)"
	elif terrain_pct < 100:
		terrain_label = terrain_name + " (-" + str(100 - terrain_pct) + "% damage)"
	else:
		terrain_label = terrain_name + " (no modifier)"
	add_output("[color=#" + COLOR_TERRAIN + "]  Terrain: " + terrain_label + "[/color]")

	# Casualty summary — enemy in red, own in green
	add_output("[color=#" + COLOR_ENEMY_CAS + "]  Enemy casualties: " + def_name + " " + _format_number(def_cas) + " (remaining: " + _format_number(def_rem) + ", morale: " + str(def_morale) + "%)[/color]")
	add_output("[color=#" + COLOR_OWN_CAS + "]  Return fire: " + atk_name + " " + _format_number(atk_cas) + " (remaining: " + _format_number(atk_rem) + ")[/color]")

	# Fort degradation
	var fort_degraded = result.get("fort_degraded", false)
	if fort_degraded:
		var fort_old = int(result.get("fort_old", 0) * 100)
		var fort_new = int(result.get("fort_new", 0) * 100)
		if fort_new <= 0:
			add_output("[color=#" + COLOR_FORT + "]  Fortifications DESTROYED! (" + str(fort_old) + "% -> 0%)[/color]")
		else:
			add_output("[color=#" + COLOR_FORT + "]  Fort degraded: " + str(fort_old) + "% -> " + str(fort_new) + "%[/color]")

	# Collateral damage
	var collateral = result.get("collateral", [])
	if collateral is Array and collateral.size() > 0:
		add_output("[color=#" + COLOR_CASUALTY + "]  -- Collateral Damage --[/color]")
		for c in collateral:
			var c_name = str(c.get("name", "Unknown"))
			var c_nation = str(c.get("nation", ""))
			var c_cas = int(c.get("casualties", 0))
			var is_friendly = c.get("friendly_fire", false)
			if is_friendly:
				add_output("[color=#" + COLOR_FRIENDLY + "]  FRIENDLY FIRE: " + c_name + " (" + c_nation + ") — " + _format_number(c_cas) + " casualties[/color]")
			else:
				add_output("[color=#" + COLOR_ENEMY_CAS + "]  " + c_name + " (" + c_nation + ") — " + _format_number(c_cas) + " casualties[/color]")

	# Bombardments remaining
	var remaining = int(result.get("bombardments_remaining", 0))
	add_output("[color=#" + COLOR_REMAINING + "]  Bombardments remaining today: " + str(remaining) + "[/color]")

	# Berthier's observation
	var obs = str(result.get("berthier_observation", ""))
	if obs != "" and obs != "null":
		add_output("[color=#" + COLOR_OBSERVATION + "]  Berthier: \"" + obs + "\"[/color]")

	add_output("")

func _display_defiance_result(response: Dictionary):
	"""Display V2b defiance result — marshal defied a direct order."""
	var outcome = str(response.get("defiance_outcome", ""))
	var defiance_action = str(response.get("defiance_action", ""))
	var berthier_text = str(response.get("berthier_text", ""))
	var trust_change = int(response.get("trust_change", 0))
	var authority_change = int(response.get("authority_change", 0))
	var message = str(response.get("message", ""))

	# Defiance header — distinct from normal objection
	add_output("")
	add_output("[color=#" + COLOR_ERROR + "]┌─────── DEFIANCE ───────┐[/color]")

	# Main message (e.g. "Despite your insistence, Ney attacked instead!")
	if message != "":
		add_output("[color=#" + COLOR_MARSHAL + "]  " + message + "[/color]")

	# Outcome label with color coding
	var outcome_color = COLOR_INFO
	var outcome_label = ""
	match outcome:
		"right":
			outcome_color = COLOR_SUCCESS
			outcome_label = "VINDICATED — Marshal was right"
		"wrong":
			outcome_color = COLOR_ERROR
			outcome_label = "FAILURE — Marshal was wrong"
		"inconclusive":
			outcome_color = COLOR_INFO
			outcome_label = "INCONCLUSIVE — No clear result"
		"failed_roll":
			outcome_color = COLOR_DISPATCH
			outcome_label = "DISCIPLINE HELD — Marshal obeyed reluctantly"

	if outcome_label != "":
		add_output("[color=#" + outcome_color + "]  " + outcome_label + "[/color]")

	# Stat changes
	var stat_parts = []
	if trust_change != 0:
		var sign = "+" if trust_change > 0 else ""
		var tc_color = COLOR_SUCCESS if trust_change > 0 else COLOR_ERROR
		stat_parts.append("[color=#" + tc_color + "]Trust " + sign + str(trust_change) + "[/color]")
	if authority_change != 0:
		var sign = "+" if authority_change > 0 else ""
		var ac_color = COLOR_SUCCESS if authority_change > 0 else COLOR_ERROR
		stat_parts.append("[color=#" + ac_color + "]Authority " + sign + str(authority_change) + "[/color]")

	if stat_parts.size() > 0:
		add_output("  " + "  ".join(stat_parts))

	# Berthier's flavor text
	if berthier_text != "" and berthier_text != "null":
		add_output("[color=#" + COLOR_OBSERVATION + "]  Berthier: \"" + berthier_text + "\"[/color]")

	add_output("[color=#" + COLOR_ERROR + "]└────────────────────────┘[/color]")
	add_output("")

func _display_authority_event(authority_event: Dictionary):
	"""Display authority threshold event (e.g. 'Whispers of Weakness')."""
	var title = str(authority_event.get("title", "Authority Changed"))
	var message = str(authority_event.get("message", ""))
	var authority = int(authority_event.get("authority", 0))

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]┌─── AUTHORITY ───┐[/color]")
	add_output("[color=#" + COLOR_GOLD + "]  " + title + "[/color]")
	if message != "":
		add_output("[color=#" + COLOR_DISPATCH + "]  " + message + "[/color]")
	add_output("[color=#" + COLOR_INFO + "]  Authority: " + str(authority) + "[/color]")
	add_output("[color=#" + COLOR_GOLD + "]└─────────────────┘[/color]")
	add_output("")

func _display_turn_change(event: Dictionary):
	"""Display turn end notification with full financial summary.

	Backend sends: income, upkeep, spent, net, treasury in turn_end event.
	All values are int() wrapped by executor.py (Godot crashes on floats).
	"""
	# Close all information screens on turn transition (avoid stale data)
	if top_bar:
		top_bar.close_all_screens()

	var new_turn = int(event.get("new_turn", 0))
	var income = int(event.get("income", 0))
	var upkeep = int(event.get("upkeep", 0))
	var spent = int(event.get("spent", 0))
	var net = int(event.get("net", 0))
	var treasury = int(event.get("treasury", 0))

	var net_sign = "+" if net >= 0 else ""
	var spent_str = ""
	if spent > 0:
		spent_str = " | Spent: " + str(int(spent)) + "g"

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]         TURN " + str(int(new_turn)) + " BEGINS[/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_SUCCESS + "]Income: " + str(int(income)) + "g | Upkeep: " + str(int(upkeep)) + "g | Net: " + net_sign + str(int(net)) + "g" + spent_str + "[/color]")
	add_output("[color=#" + COLOR_GOLD + "]Treasury: " + _format_number(int(treasury)) + "g[/color]")

	# Bankruptcy warning
	var bankruptcy_turns = int(event.get("bankruptcy_turns", 0))
	if bankruptcy_turns > 0:
		if bankruptcy_turns >= 3:
			add_output("[color=#" + COLOR_ERROR + "]BANKRUPTCY: Troops are deserting! (" + str(bankruptcy_turns) + " turns in deficit)[/color]")
		elif bankruptcy_turns >= 2:
			add_output("[color=#" + COLOR_ERROR + "]WARNING: Treasury in deficit! Troops grow restless![/color]")
		else:
			add_output("[color=#" + COLOR_ERROR + "]WARNING: Treasury in deficit! Upkeep costs halved as mercy.[/color]")

	add_output("[color=#" + COLOR_SUCCESS + "]Actions refreshed: " + str(int(max_actions)) + "/" + str(int(max_actions)) + "[/color]")
	add_output("")

func _display_morning_dispatch(data: Dictionary):
	"""Display Berthier's Morning Dispatch — structured turn-start briefing (Phase 6.5).

	Renders SITUATION, MARSHAL STATUS, INTELLIGENCE, and Berthier's closing note
	as formatted terminal output. All data is fog-filtered by the backend.
	"""
	var turn_num = int(data.get("turn", 0))
	var situation = data.get("situation", {})
	var marshals_list = data.get("marshals", [])
	var intel_list = data.get("intelligence", [])
	var berthier_note = str(data.get("berthier_note", "Your orders, Sire."))

	# ═══ DISPATCH HEADER ═══
	add_output("[color=#" + COLOR_BERTHIER + "]════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_BERTHIER + "]  MORNING DISPATCH — Turn " + str(turn_num) + "[/color]")
	add_output("[color=#" + COLOR_INFO + "]  Chief of Staff Berthier reporting[/color]")
	add_output("[color=#" + COLOR_BERTHIER + "]════════════════════════════════════[/color]")
	add_output("")

	# ═══ SITUATION ═══
	add_output("[color=#" + COLOR_BERTHIER + "]SITUATION[/color]")
	var player_regions = int(situation.get("player_regions", 0))
	var enemy_regions = int(situation.get("enemy_regions", 0))
	var treasury = int(situation.get("treasury", 0))
	var treasury_delta = int(situation.get("treasury_delta", 0))
	var bankrupt = situation.get("bankrupt", false)
	var strength_pct = int(situation.get("strength_ratio_pct", 0))

	# Treasury line
	var delta_sign = "+" if treasury_delta >= 0 else ""
	var delta_color = COLOR_SUCCESS if treasury_delta >= 0 else COLOR_ERROR
	add_output("[color=#" + COLOR_INFO + "]  France holds " + str(player_regions) + " regions. Treasury: " + _format_number(treasury) + "g [/color][color=#" + delta_color + "](" + delta_sign + str(treasury_delta) + ")[/color]")

	# Enemy regions + estimated strength
	if bankrupt:
		add_output("[color=#" + COLOR_ERROR + "]  BANKRUPT — Treasury exhausted. Troops desert.[/color]")
	else:
		add_output("[color=#" + COLOR_INFO + "]  Enemy nations hold " + str(enemy_regions) + " regions. Estimated enemy strength: " + str(strength_pct) + "% of French forces.[/color]")

	# Authority (V2b)
	var authority = int(situation.get("authority", 100))
	var authority_label = str(situation.get("authority_label", "Normal"))
	var auth_color = COLOR_INFO
	if authority >= 80:
		auth_color = COLOR_SUCCESS
	elif authority < 50:
		auth_color = COLOR_ERROR
	add_output("[color=#" + COLOR_INFO + "]  Your authority: [/color][color=#" + auth_color + "]" + str(authority) + " (" + authority_label + ")[/color]")
	add_output("")

	# ═══ MARSHAL STATUS ═══
	if marshals_list.size() > 0:
		add_output("[color=#" + COLOR_BERTHIER + "]MARSHAL STATUS[/color]")
		for m in marshals_list:
			var m_name = str(m.get("name", "?"))
			var m_loc = str(m.get("location", "?"))
			var m_str = int(m.get("strength", 0))
			var m_status = str(m.get("status", "awaiting"))
			var m_note = str(m.get("status_note", ""))
			var m_trust = int(m.get("trust", 75))
			var m_trust_notable = m.get("trust_notable", false)
			var m_morale = int(m.get("morale", 100))
			var m_morale_warning = m.get("morale_warning", false)

			# Status icon
			var icon = ""
			match m_status:
				"awaiting":
					icon = "-"
				"drilling":
					icon = "*"
				"fortified":
					icon = "#"
				"retreating":
					icon = "<"
				"broken":
					icon = "!"
				"en_route":
					icon = ">"
				"idle_restless":
					icon = "-"
				"artillery":
					icon = "+"
				_:
					icon = "-"

			# Build the line
			var line = "  " + icon + " "
			line += m_name
			# Pad name to ~14 chars for alignment
			while line.length() < 18:
				line += " "
			line += m_loc
			while line.length() < 34:
				line += " "
			line += _format_number(m_str)
			while line.length() < 44:
				line += " "
			line += m_note

			# Append trust/morale warnings
			if m_trust_notable and m_trust < 55:
				line += " Trust:" + str(m_trust)
			if m_morale_warning:
				line += " Morale:" + str(m_morale) + "%"

			# Color based on status
			var line_color = COLOR_INFO
			if m_status == "broken":
				line_color = COLOR_ERROR
			elif m_status == "retreating":
				line_color = COLOR_ERROR
			elif m_status == "idle_restless":
				line_color = COLOR_BATTLE

			add_output("[color=#" + line_color + "]" + line + "[/color]")
		add_output("")

	# ═══ INTELLIGENCE ═══
	add_output("[color=#" + COLOR_BERTHIER + "]INTELLIGENCE[/color]")
	if intel_list.size() == 0:
		add_output("[color=#" + COLOR_INFO + "]  No enemy forces in observation range.[/color]")
	else:
		for intel in intel_list:
			var i_name = str(intel.get("name", "?"))
			var i_loc = str(intel.get("location", "?"))
			var i_strength = str(intel.get("strength_display", "?"))
			var i_vis = str(intel.get("visibility", "unknown"))
			var i_turn = int(intel.get("intel_turn", 0))

			var vis_label = ""
			var vis_color = COLOR_INFO
			match i_vis:
				"full":
					vis_label = "[confirmed]"
					vis_color = COLOR_SUCCESS
				"partial":
					vis_label = "[partial]"
					vis_color = COLOR_INFO
				"stale":
					vis_label = "[stale - T" + str(i_turn) + "]"
					vis_color = COLOR_BATTLE
				"last_known":
					vis_label = "[last known - T" + str(i_turn) + "]"
					vis_color = COLOR_ERROR
				_:
					vis_label = ""

			var intel_line = "  " + i_name
			while intel_line.length() < 18:
				intel_line += " "
			intel_line += i_loc
			while intel_line.length() < 34:
				intel_line += " "
			intel_line += i_strength

			add_output("[color=#" + COLOR_INFO + "]" + intel_line + " [/color][color=#" + vis_color + "]" + vis_label + "[/color]")
	add_output("")

	# ═══ TURN EVENTS ═══
	var turn_events = data.get("turn_events", [])
	if turn_events.size() > 0:
		add_output("[color=#" + COLOR_BERTHIER + "]TURN EVENTS[/color]")
		for evt in turn_events:
			var evt_msg = str(evt.get("message", ""))
			var evt_sev = str(evt.get("severity", "info"))
			var evt_color = COLOR_INFO
			if evt_sev == "warning":
				evt_color = COLOR_ERROR
			elif evt_sev == "good":
				evt_color = COLOR_SUCCESS
			add_output("[color=#" + evt_color + "]  " + evt_msg + "[/color]")
		add_output("")

	# ═══ BERTHIER'S NOTE ═══
	add_output("[color=#" + COLOR_OBSERVATION + "]  Berthier: \"" + berthier_note + "\"[/color]")
	add_output("[color=#" + COLOR_BERTHIER + "]════════════════════════════════════[/color]")
	add_output("")

func _show_pending_dispatch():
	"""Display pending morning dispatch if any, then clear it."""
	if pending_dispatch_data != null:
		_display_morning_dispatch(pending_dispatch_data)
		pending_dispatch_data = null

func _display_turn_advance(action_info: Dictionary):
	"""Display automatic turn advancement when actions run out."""
	# Close all information screens on turn transition (avoid stale data)
	if top_bar:
		top_bar.close_all_screens()

	var new_turn = int(action_info.get("new_turn", current_turn + 1))
	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]  Actions exhausted — Turn " + str(int(new_turn)) + " begins[/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")

func _show_game_over_screen(game_state: Dictionary):
	"""Display dramatic game over screen with final statistics."""
	# Disable input permanently
	set_input_enabled(false)

	# Add spacing for dramatic effect
	add_output("")
	add_output("")

	# Dramatic separator
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")

	# Victory or defeat title
	var victory_status = game_state.get("victory", "defeat")
	if victory_status == "victory":
		add_output("[center][color=#" + COLOR_GOLD + "][b][font_size=28]⚜ VICTOIRE! ⚜[/font_size][/b][/color][/center]")
		add_output("")
		add_output("[center][color=#" + COLOR_SUCCESS + "]The Empire Triumphant![/color][/center]")
		add_output("")
		add_output("[color=#" + COLOR_INFO + "]Europe bends the knee before the French Eagle.[/color]")
		add_output("[color=#" + COLOR_INFO + "]Your marshals have conquered all who opposed them.[/color]")
		add_output("[color=#" + COLOR_INFO + "]History will remember this as the height of Imperial glory![/color]")
	else:
		add_output("[center][color=#" + COLOR_ERROR + "][b][font_size=28]⚔ DÉFAITE ⚔[/font_size][/b][/color][/center]")
		add_output("")
		add_output("[center][color=#" + COLOR_ERROR + "]The Empire Has Fallen[/color][/center]")
		add_output("")
		add_output("[color=#" + COLOR_INFO + "]The enemies of France have prevailed.[/color]")
		add_output("[color=#" + COLOR_INFO + "]Your marshals fought bravely, but it was not enough.[/color]")
		add_output("[color=#" + COLOR_INFO + "]The eagles are furled. The Grande Armée is no more.[/color]")

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]─────────────────────────────────────[/color]")
	add_output("[color=#" + COLOR_GOLD + "]         FINAL STATISTICS[/color]")
	add_output("[color=#" + COLOR_GOLD + "]─────────────────────────────────────[/color]")

	# Display final statistics
	var final_turn = int(game_state.get("turn", current_turn))
	var regions_controlled = int(game_state.get("regions_controlled", 0))
	var total_regions = int(game_state.get("total_regions", 13))
	var final_gold = int(game_state.get("gold", gold))

	add_output("[color=#" + COLOR_INFO + "]Campaign Duration: " + str(final_turn) + " turns[/color]")
	add_output("[color=#" + COLOR_INFO + "]Regions Controlled: " + str(regions_controlled) + "/" + str(total_regions) + "[/color]")
	add_output("[color=#" + COLOR_INFO + "]Imperial Treasury: " + _format_number(final_gold) + " gold[/color]")

	# Marshal status if available
	if game_state.has("player_marshals"):
		var marshals = game_state.player_marshals
		add_output("")
		add_output("[color=#" + COLOR_MARSHAL + "]Marshal Status:[/color]")
		for marshal_name in marshals:
			var marshal = marshals[marshal_name]
			var strength = int(marshal.get("strength", 0))
			var location = marshal.get("location", "Unknown")
			if strength > 0:
				add_output("[color=#" + COLOR_INFO + "]  • " + marshal_name + ": " + _format_number(strength) + " troops at " + location + "[/color]")
			else:
				add_output("[color=#" + COLOR_ERROR + "]  • " + marshal_name + ": Destroyed[/color]")

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")

	# Closing message
	if victory_status == "victory":
		add_output("[center][color=#" + COLOR_GOLD + "]Vive l'Empereur![/color][/center]")
	else:
		add_output("[center][color=#" + COLOR_INFO + "]The game is over, but the legend endures...[/color][/center]")

	add_output("")

func _show_action_cost(action_info: Dictionary):
	"""Show action point usage."""
	var cost = int(action_info.get("cost", 0))
	var remaining = int(action_info.get("remaining", actions_remaining))
	
	if cost > 0:
		add_output("[color=#" + COLOR_INFO + "]   [" + str(int(remaining)) + "/" + str(int(max_actions)) + " actions remaining][/color]")

func _update_status(action_summary: Dictionary):
	"""Update header status displays.

	Backend sends action_summary with: actions_remaining, max_actions,
	admin_actions_remaining, max_admin_actions, turn, max_turns.
	All values are int() wrapped by world_state.py get_action_summary().
	"""
	if action_summary.has("actions_remaining"):
		actions_remaining = int(action_summary.actions_remaining)

	if action_summary.has("max_actions"):
		max_actions = int(action_summary.max_actions)

	if action_summary.has("admin_actions_remaining"):
		admin_actions_remaining = int(action_summary.admin_actions_remaining)

	if action_summary.has("max_admin_actions"):
		max_admin_actions = int(action_summary.max_admin_actions)

	if action_summary.has("turn"):
		current_turn = int(action_summary.turn)

	if action_summary.has("max_turns"):
		max_turns = int(action_summary.max_turns)

	# Update displays - force integer conversion in strings
	turn_value.text = str(int(current_turn)) + "/" + str(int(max_turns))

	# Color actions based on remaining
	if actions_remaining <= 1:
		actions_value.add_theme_color_override("font_color", Color(0.8, 0.4, 0.4))  # Red when low
	elif actions_remaining <= 2:
		actions_value.add_theme_color_override("font_color", Color(0.9, 0.7, 0.3))  # Yellow when medium
	else:
		actions_value.add_theme_color_override("font_color", Color(0.4, 0.8, 0.4))  # Green when good

	actions_value.text = str(int(actions_remaining)) + "/" + str(int(max_actions))

	# Admin AP display
	if admin_actions_remaining == 0:
		admin_value.add_theme_color_override("font_color", Color(0.5, 0.5, 0.55))  # Grey when spent
	else:
		admin_value.add_theme_color_override("font_color", Color(0.6, 0.7, 0.9))  # Blue when available
	admin_value.text = str(int(admin_actions_remaining)) + "/" + str(int(max_admin_actions))

	# Update top bar turn counter
	if top_bar:
		top_bar.update_turn(current_turn)


func _update_diplomatic_top_bar(response: Dictionary):
	"""Update diplomatic fields in top bar from /test or /command response."""
	if not top_bar:
		return
	if not top_bar.has_method("update_diplomatic_fields"):
		return
	var diplo_data = {}
	# Check game_state first (command responses), then top-level (connection test)
	if response.has("diplomatic_points"):
		diplo_data["diplomatic_points"] = response.get("diplomatic_points", 0)
		diplo_data["max_diplomatic_points"] = response.get("max_diplomatic_points", 3)
		diplo_data["threat_level"] = response.get("threat_level", 0)
		diplo_data["coalition_brewing"] = response.get("coalition_brewing", false)
		diplo_data["talleyrand_mission_summary"] = response.get("talleyrand_mission_summary", "Idle")
		diplo_data["pending_envoy_count"] = response.get("pending_envoy_count", 0)
	if not diplo_data.is_empty():
		top_bar.update_diplomatic_fields(diplo_data)


func _update_gold_display():
	"""Update treasury display with formatting."""
	gold_value.text = _format_number(gold)

func _apply_manpower(pools: Dictionary):
	"""Extract manpower values from a dict and update display."""
	if pools.has("infantry"):
		infantry_pool = int(pools.infantry)
	if pools.has("cavalry"):
		cavalry_pool = int(pools.cavalry)
	if pools.has("artillery"):
		artillery_pool = int(pools.artillery)
	_update_manpower_display()

func _update_manpower_display():
	"""Update manpower pool display with formatting."""
	inf_value.text = _format_number(infantry_pool)
	cav_value.text = _format_number(cavalry_pool)
	art_value.text = _format_number(artillery_pool)
	# Color shift when pools are low
	if cavalry_pool < 5000:
		cav_value.add_theme_color_override("font_color", Color(0.9, 0.3, 0.3))
	elif cavalry_pool < 10000:
		cav_value.add_theme_color_override("font_color", Color(0.9, 0.6, 0.4))
	else:
		cav_value.add_theme_color_override("font_color", Color(0.85, 0.75, 0.55))
	if infantry_pool < 20000:
		inf_value.add_theme_color_override("font_color", Color(0.9, 0.3, 0.3))
	elif infantry_pool < 40000:
		inf_value.add_theme_color_override("font_color", Color(0.9, 0.6, 0.4))
	else:
		inf_value.add_theme_color_override("font_color", Color(0.6, 0.8, 0.6))
	if artillery_pool < 3000:
		art_value.add_theme_color_override("font_color", Color(0.9, 0.3, 0.3))
	elif artillery_pool < 8000:
		art_value.add_theme_color_override("font_color", Color(0.9, 0.6, 0.4))
	else:
		art_value.add_theme_color_override("font_color", Color(0.75, 0.7, 0.85))

func _format_number(num) -> String:
	"""Format number with comma separators."""
	var s = str(int(num))
	var result = ""
	var count = 0
	for i in range(s.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			result = "," + result
		result = s[i] + result
		count += 1
	return result

func _add_separator():
	"""Add a visual separator line."""
	add_output("[color=#" + COLOR_INFO + "]─────────────────────────────────────[/color]")

func add_output(text: String):
	"""Add text to output display with message limit."""
	message_count += 1
	
	# Trim old messages if over limit
	if message_count > MAX_MESSAGES:
		_trim_old_messages()
	
	output_display.append_text(text + "\n")
	
	# Ensure scroll to bottom
	await get_tree().process_frame
	output_scroll.scroll_vertical = output_scroll.get_v_scroll_bar().max_value

func _display_feedback(feedback: Dictionary):
	"""Display AI feedback from LLM response (words, not numbers)."""
	if feedback.is_empty():
		return

	# Strategic feedback (eloquence/inspiration)
	if feedback.has("strategic") and feedback.strategic != "":
		add_output("[color=#" + COLOR_FEEDBACK + "][i]" + feedback.strategic + "[/i][/color]")

	# Ambiguity feedback (clarity)
	if feedback.has("ambiguity") and feedback.ambiguity != "":
		add_output("[color=#" + COLOR_FEEDBACK + "][i]" + feedback.ambiguity + "[/i][/color]")

func _trim_old_messages():
	"""Remove oldest messages to prevent infinite growth."""
	var current_text = output_display.get_parsed_text()
	var lines = current_text.split("\n")
	
	# Keep last 75% of messages
	var keep_from = int(lines.size() * 0.25)
	var new_lines = lines.slice(keep_from)
	
	output_display.clear()
	output_display.append_text("[color=#" + COLOR_INFO + "][...earlier messages trimmed...][/color]\n\n")
	for line in new_lines:
		output_display.append_text(line + "\n")
	
	message_count = new_lines.size()

func set_input_enabled(enabled: bool):
	"""Enable or disable command input and buttons."""
	command_input.editable = enabled
	send_button.disabled = not enabled
	end_turn_button.disabled = not enabled
	diplomacy_button.disabled = not enabled

	if enabled:
		command_input.grab_focus()

func _show_objection_dialog(response):
	"""Display objection dialog when marshal objects."""
	# Strategic objections (Phase M) nest data in response.objection
	# Tactical objections have data at top level
	var is_strategic = response.has("pending_objection") and response.pending_objection == true
	var objection = response.get("objection", {}) if is_strategic else response

	var marshal_name = objection.get("marshal", response.get("marshal", "Unknown"))

	add_output("")
	add_output("[color=#" + COLOR_MARSHAL + "]⚠ Marshal " + marshal_name + " raises concerns...[/color]")
	add_output("")

	# Prepare objection data for dialog
	# Handle both tactical (top-level) and strategic (nested in objection) formats
	var objection_data = {
		"marshal": marshal_name,
		"personality": objection.get("personality", response.get("personality", "unknown")),
		"message": objection.get("message", response.get("message", "I have concerns about this order, Sire.")),
		"trust": response.get("trust", 70),
		"trust_label": response.get("trust_label", "Unknown"),
		"vindication": response.get("vindication", 0),
		"authority": response.get("authority", 100),
		"suggested_alternative": objection.get("suggested_alternative", response.get("suggested_alternative")),
		"compromise": objection.get("compromise", response.get("compromise")),
		# Strategic objections have options array instead of suggested_alternative/compromise
		"options": objection.get("options", []),
		"is_strategic": is_strategic,
		# V2a fields: tone, concern_level, trust change previews
		"tone": objection.get("tone", response.get("tone", "firm")),
		"concern_level": objection.get("concern_level", response.get("concern_level", "MODERATE")),
		"trust_gain": objection.get("trust_gain", response.get("trust_gain", 3)),
		"insist_penalty": objection.get("insist_penalty", response.get("insist_penalty", -10)),
		"compromise_gain": objection.get("compromise_gain", response.get("compromise_gain", 3)),
	}

	if objection_dialog == null:
		push_error("objection_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Dialog not loaded![/color]")
		set_input_enabled(true)
		return

	objection_dialog.show_objection(objection_data)

func _on_objection_choice_made(choice: String):
	"""Handle player's choice in objection dialog."""
	# Disable input while processing
	set_input_enabled(false)

	# Display player choice
	var choice_text = ""
	match choice:
		"trust":
			choice_text = "You decide to trust your marshal's judgment."
		"insist":
			choice_text = "You insist the order be carried out as given."
		"compromise":
			choice_text = "You seek a middle ground with your marshal."

	add_output("[color=#" + COLOR_COMMAND + "]► " + choice_text + "[/color]")
	add_output("")

	# Send choice to backend
	api_client.send_objection_response(choice, _on_objection_response)

func _on_objection_response(response):
	"""Handle backend response after player makes objection choice."""
	print("\n" + "=".repeat(60))
	print("OBJECTION RESPONSE RECEIVED:")
	print("  success: ", response.get("success", false))
	print("  disobeyed: ", response.get("disobeyed", false))
	print("  defiance: ", response.get("defiance", false))
	print("  has redemption_event: ", response.has("redemption_event"))
	print("  state: ", response.get("state", "none"))
	print("=".repeat(60) + "\n")

	# ════════════════════════════════════════════════════════════
	# CHECK FOR DEFIANCE (V2b): Marshal defied a direct order
	# ════════════════════════════════════════════════════════════
	if response.get("defiance", false):
		_display_defiance_result(response)

		# Update status and state
		if response.has("action_summary"):
			_update_status(response.action_summary)
		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)

		# Battle report if defiant action caused combat
		if response.has("battle_report"):
			_display_berthier_report(response.battle_report)

		# Notifications
		if notification_bar and response.has("notifications"):
			notification_bar.update_notifications(response.notifications)

		# Authority threshold event
		if response.has("authority_event"):
			_display_authority_event(response.authority_event)

		# Check for redemption event triggered by defiance trust penalty
		if response.has("redemption_event"):
			_show_redemption_dialog(response.redemption_event)
			return

		set_input_enabled(true)
		command_input.grab_focus()
		return

	# ════════════════════════════════════════════════════════════
	# CHECK FOR DISOBEY (V1): Marshal refused to obey
	# ════════════════════════════════════════════════════════════
	if response.get("disobeyed", false):
		add_output("[color=#" + COLOR_ERROR + "]⚠ DISOBEDIENCE![/color]")
		add_output("[color=#" + COLOR_MARSHAL + "]" + response.message + "[/color]")
		add_output("")

		# Update status even on disobey
		if response.has("action_summary"):
			_update_status(response.action_summary)

		# Check for redemption event triggered by disobey
		if response.has("redemption_event"):
			print("🚨 REDEMPTION EVENT after disobey - showing dialog")
			_show_redemption_dialog(response.redemption_event)
			return  # Don't re-enable input until redemption resolved

		set_input_enabled(true)
		command_input.grab_focus()
		return

	# ════════════════════════════════════════════════════════════
	# CHECK FOR REDEMPTION EVENT: Trust at critical low
	# ════════════════════════════════════════════════════════════
	if response.has("redemption_event"):
		print("🚨 REDEMPTION EVENT detected - showing dialog")

		# First show the normal result
		if response.success:
			if response.has("action_summary"):
				_update_status(response.action_summary)
			if response.has("game_state") and response.game_state.has("gold"):
				gold = int(response.game_state.gold)
				_update_gold_display()
			if response.has("game_state") and response.game_state.has("manpower_pools"):
				_apply_manpower(response.game_state.manpower_pools)
			if response.has("game_state") and response.game_state.has("map_data"):
				map_area.update_all_regions(response.game_state.map_data)
			_display_result(response)

		# Then show redemption dialog
		_show_redemption_dialog(response.redemption_event)
		return  # Don't re-enable input until redemption resolved

	# Check for strategic interrupt (post-objection command hit blocked path)
	if response.has("pending_interrupt") and response.pending_interrupt:
		# Show the command result message first
		if response.has("message") and response.message:
			_display_result(response)
		_show_interrupt_popup(response.pending_interrupt)
		return  # Don't re-enable input until interrupt resolved

	# Re-enable input (normal flow)
	set_input_enabled(true)

	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)

		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)

		# Update map with latest state
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)

		# Display result
		_display_result(response)

		# Authority threshold event (V2b)
		if response.has("authority_event"):
			_display_authority_event(response.authority_event)

		# Notifications
		if notification_bar and response.has("notifications"):
			notification_bar.update_notifications(response.notifications)

		# Check for game over
		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")

	add_output("")
	command_input.grab_focus()


func _show_redemption_dialog(redemption_event: Dictionary):
	"""Display redemption popup dialog when trust hits critical low."""
	print("REDEMPTION DIALOG - showing popup for event: ", redemption_event)

	var marshal_name = redemption_event.get("marshal", "Marshal")

	# Show brief notification in log
	add_output("")
	add_output("[color=#" + COLOR_ERROR + "]⚠ " + marshal_name + " requests an urgent audience...[/color]")
	add_output("")

	# Check if dialog exists
	if redemption_dialog == null:
		print("❌ ERROR: redemption_dialog is NULL!")
		push_error("redemption_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Redemption dialog not loaded![/color]")
		# Fallback to text commands
		_show_redemption_text_fallback(redemption_event)
		return

	# Show the popup dialog
	redemption_dialog.show_redemption(redemption_event)
	pending_redemption = true


func _show_redemption_text_fallback(redemption_event: Dictionary):
	"""Fallback text display if dialog fails to load."""
	var options = redemption_event.get("options", [])

	add_output("[color=#" + COLOR_INFO + "]You must decide how to handle this:[/color]")
	for opt in options:
		add_output("[color=#" + COLOR_INFO + "]  • " + opt.get("id", "?") + ": " + opt.get("text", "Unknown") + "[/color]")

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]Type: 'grant_autonomy', 'dismiss', or 'demand_obedience'[/color]")
	add_output("")

	pending_redemption = true
	set_input_enabled(true)
	command_input.grab_focus()


func _on_redemption_choice_made(choice: String):
	"""Handle player's choice in redemption dialog."""
	print("REDEMPTION CHOICE MADE: ", choice)

	# Disable input while processing
	set_input_enabled(false)

	# Display player choice in log
	var choice_text = ""
	match choice:
		"grant_autonomy":
			choice_text = "You grant the marshal autonomy to act independently."
		"dismiss":
			choice_text = "You dismiss the marshal from command."
		"demand_obedience":
			choice_text = "You demand continued obedience despite the broken trust."

	add_output("[color=#" + COLOR_COMMAND + "]► " + choice_text + "[/color]")
	add_output("")

	# Send choice to backend
	api_client.send_redemption_response(choice, _on_redemption_response)


func _on_redemption_response(response):
	"""Handle backend response after player makes redemption choice."""
	print("\n" + "=".repeat(60))
	print("REDEMPTION RESPONSE RECEIVED:")
	print("  success: ", response.get("success", false))
	print("  choice: ", response.get("choice", "unknown"))
	print("  autonomous: ", response.get("autonomous", false))
	print("  dismissed: ", response.get("dismissed", false))
	print("=".repeat(60) + "\n")

	pending_redemption = false

	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)

		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)

		# Update map
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)

		# Display result based on choice
		var choice = response.get("choice", "")
		add_output("")

		if choice == "grant_autonomy":
			add_output("[color=#" + COLOR_SUCCESS + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_SUCCESS + "]   AUTONOMY GRANTED[/color]")
			add_output("[color=#" + COLOR_SUCCESS + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_MARSHAL + "]" + response.message + "[/color]")
			var turns = int(response.get("autonomy_turns", 3))
			add_output("[color=#" + COLOR_INFO + "]The marshal will act independently for " + str(turns) + " turns.[/color]")

		elif choice == "dismiss":
			add_output("[color=#" + COLOR_ERROR + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_ERROR + "]   MARSHAL DISMISSED[/color]")
			add_output("[color=#" + COLOR_ERROR + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_MARSHAL + "]" + response.message + "[/color]")

		elif choice == "demand_obedience":
			add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_GOLD + "]   OBEDIENCE DEMANDED[/color]")
			add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_MARSHAL + "]" + response.message + "[/color]")
			add_output("[color=#" + COLOR_INFO + "]Warning: High chance of future disobedience.[/color]")

		else:
			add_output("[color=#" + COLOR_SUCCESS + "]" + response.message + "[/color]")

		add_output("")
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")
		add_output("")

	set_input_enabled(true)
	command_input.grab_focus()


func _show_enemy_phase_dialog(enemy_phase: Dictionary, turn: int):
	"""Display enemy phase popup with full battle details."""
	print("Showing enemy phase dialog for turn ", turn)

	# Check if dialog exists
	if enemy_phase_dialog == null:
		print("ERROR: enemy_phase_dialog is NULL!")
		push_error("enemy_phase_dialog is NULL! Cannot show dialog.")
		# Fallback: just re-enable input
		set_input_enabled(true)
		return

	# Show the dialog
	enemy_phase_dialog.show_enemy_phase(enemy_phase, turn)


func _show_mild_dispatches(response):
	"""V2a: Show MILD concerns as 'Field Dispatches' in the turn log.
	Atmosphere text — feels like reading war dispatches, not game feedback.
	Key 'mild_concerns' must match exactly what main.py sends — verify with curl if dispatches stop appearing."""
	if not response.has("mild_concerns"):
		return
	var concerns = response.mild_concerns
	if concerns is Array and concerns.size() > 0:
		add_output("")
		add_output("[color=#" + COLOR_DISPATCH + "]━━ Field Dispatches ━━[/color]")
		for concern in concerns:
			var marshal_name = concern.get("marshal", "Unknown")
			var msg = concern.get("message", "")
			if msg != "":
				add_output("[color=#" + COLOR_DISPATCH + "]  " + msg + "[/color]")
		add_output("")


func _on_enemy_phase_dismissed():
	"""Handle enemy phase dialog dismissal."""
	# Enemy phase text removed from terminal — popup is sufficient,
	# campaign log has the full record.

	# Show MILD dispatches after enemy phase (V2a: atmosphere text)
	if pending_enemy_phase_response != null:
		_show_mild_dispatches(pending_enemy_phase_response)

	# Check for game over (Paris captured, all marshals destroyed, etc.)
	if pending_enemy_phase_response != null:
		var response = pending_enemy_phase_response

		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				pending_enemy_phase_response = null
				_show_game_over_screen(response.game_state)
				return  # Don't re-enable input

		# Check for strategic reports (show after enemy phase)
		if response.has("strategic_reports") and not response.strategic_reports.is_empty():
			# Keep pending_enemy_phase_response for post-report game over check
			pending_strategic_response = response
			_show_strategic_reports(response)
			return  # Don't re-enable input until reports dismissed

		# Check for deferred redemption (cavalry trust penalty from end-turn)
		if response.has("redemption_event"):
			pending_enemy_phase_response = null
			_show_pending_dispatch()
			_show_redemption_dialog(response.redemption_event)
			return  # Don't re-enable input until redemption resolved

		# N4i: Update war status HUD after enemy phase
		_process_active_wars(response)
		pending_enemy_phase_response = null

	# Morning Dispatch — displayed last, right before player gets control
	_show_pending_dispatch()

	set_input_enabled(true)
	command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# CAPTURE CHOICE DIALOG (Phase 6.2.E Plunder/Secure)
# ════════════════════════════════════════════════════════════════════════════

func _show_capture_choice_dialog(response):
	"""Display Plunder/Secure popup when player captures an enemy region."""
	var capture_data = response.get("capture_data", {})
	var region_name = capture_data.get("region", "Unknown") if capture_data is Dictionary else "Unknown"
	var capturer_name = capture_data.get("capturer", "Marshal") if capture_data is Dictionary else "Marshal"

	# Show the capture message in log first
	if response.has("message"):
		add_output("[color=#" + COLOR_CONQUEST + "]" + response.message + "[/color]")

	# Update status/map from the response
	if response.has("action_summary"):
		_update_status(response.action_summary)
	if response.has("game_state") and response.game_state.has("gold"):
		gold = int(response.game_state.gold)
		_update_gold_display()
	if response.has("game_state") and response.game_state.has("manpower_pools"):
		_apply_manpower(response.game_state.manpower_pools)
	if response.has("game_state") and response.game_state.has("map_data"):
		map_area.update_all_regions(response.game_state.map_data)

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]Your forces await orders: Plunder or Secure?[/color]")
	add_output("")

	if capture_choice_dialog == null:
		push_error("capture_choice_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Capture choice dialog not loaded![/color]")
		set_input_enabled(true)
		return

	capture_choice_dialog.show_capture_choice(capture_data)


func _on_capture_choice_made(choice: String):
	"""Handle player's plunder/secure choice."""
	set_input_enabled(false)

	var choice_text = ""
	if choice == "plunder":
		choice_text = "You order your troops to plunder the region!"
		add_output("[color=#" + COLOR_BATTLE + "]" + choice_text + "[/color]")
	else:
		choice_text = "You order your troops to secure the region."
		add_output("[color=#" + COLOR_SUCCESS + "]" + choice_text + "[/color]")
	add_output("")

	api_client.send_capture_choice_response(choice, _on_capture_choice_response)


func _on_capture_choice_response(response):
	"""Handle backend response after player makes plunder/secure choice."""
	set_input_enabled(true)

	if response.success:
		if response.has("action_summary"):
			_update_status(response.action_summary)
		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)

		add_output("[color=#" + COLOR_SUCCESS + "]" + response.message + "[/color]")

		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")

	add_output("")
	command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# LOAD GAME DIALOG (Phase 6: Save/Load)
# ════════════════════════════════════════════════════════════════════════════

func _show_load_dialog():
	"""Fetch saves from backend and show load dialog."""
	if load_dialog == null:
		add_output("[color=#" + COLOR_ERROR + "]Load dialog not available.[/color]")
		return
	api_client.list_saves(_on_saves_listed)

func _on_saves_listed(response):
	"""Handle saves list response from backend."""
	if response.success and response.has("saves"):
		load_dialog.show_saves(response.saves)
	else:
		add_output("[color=#" + COLOR_ERROR + "]Failed to list saves.[/color]")
		set_input_enabled(true)

func _on_load_save_selected(filename: String):
	"""Player selected a save to load."""
	set_input_enabled(false)
	add_output("[color=#" + COLOR_INFO + "]Loading save...[/color]")
	api_client.load_game(filename, _on_load_result)

func _on_load_result(response):
	"""Handle load result from backend."""
	set_input_enabled(true)
	if response.success:
		# Refresh entire display from new game state
		if response.has("game_state"):
			var gs = response.game_state
			if gs.has("map_data"):
				map_area.update_all_regions(gs.map_data)
			if gs.has("gold"):
				gold = int(gs.gold)
				_update_gold_display()
			if gs.has("manpower_pools"):
				_apply_manpower(gs.manpower_pools)
			if gs.has("turn"):
				current_turn = int(gs.turn)
				turn_value.text = str(current_turn)
			if gs.has("actions_remaining"):
				actions_remaining = int(gs.actions_remaining)
			if gs.has("max_actions"):
				max_actions = int(gs.max_actions)
			if gs.has("admin_actions_remaining"):
				admin_actions_remaining = int(gs.admin_actions_remaining)
			if gs.has("max_admin_actions"):
				max_admin_actions = int(gs.max_admin_actions)
			# Update actions display
			actions_value.text = "%d / %d" % [actions_remaining, max_actions]
			admin_value.text = "%d / %d" % [admin_actions_remaining, max_admin_actions]

		add_output("[color=#" + COLOR_SUCCESS + "]Game loaded successfully.[/color]")
		add_output("[color=#" + COLOR_INFO + "]" + response.get("message", "") + "[/color]")
	else:
		add_output("[color=#" + COLOR_ERROR + "]Load failed: " + response.get("message", "Unknown error") + "[/color]")
	add_output("")
	command_input.grab_focus()

func _on_load_cancelled():
	"""Player cancelled the load dialog."""
	set_input_enabled(true)
	command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# GLORIOUS CHARGE DIALOG (Phase 3 Cavalry Recklessness)
# ════════════════════════════════════════════════════════════════════════════

var pending_charge_marshal: String = ""
var pending_charge_target: String = ""

func _show_glorious_charge_dialog(response):
	"""Display Glorious Charge popup when reckless cavalry is at recklessness 3."""
	print("_show_glorious_charge_dialog() CALLED")
	print("  Response: ", response)

	# Store pending info for sending back to server
	# Handle null values (get() default doesn't work if key exists with null)
	var marshal_val = response.get("marshal")
	var target_val = response.get("target")
	var reck_val = response.get("recklessness")

	pending_charge_marshal = marshal_val if marshal_val != null else ""
	pending_charge_target = target_val if target_val != null else ""

	# Get recklessness - backend sends it in the response directly
	var recklessness = int(reck_val) if reck_val != null else 3

	print("  Parsed: marshal=%s, target=%s, recklessness=%d" % [pending_charge_marshal, pending_charge_target, recklessness])

	# Show notification in log
	add_output("")
	add_output("[color=#" + COLOR_BATTLE + "]🐴 " + pending_charge_marshal + "'s blood is up![/color]")
	add_output("[color=#" + COLOR_INFO + "]Recklessness at " + str(int(recklessness)) + "/4 - Glorious Charge available![/color]")
	add_output("")

	# Check if dialog exists
	if glorious_charge_dialog == null:
		print("❌ ERROR: glorious_charge_dialog is NULL!")
		push_error("glorious_charge_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Glorious Charge dialog not loaded![/color]")
		# Fallback to text
		_show_glorious_charge_text_fallback()
		return

	# Prepare data for dialog
	var charge_data = {
		"marshal": pending_charge_marshal,
		"target": pending_charge_target,
		"recklessness": recklessness
	}

	# Show the popup dialog
	glorious_charge_dialog.show_glorious_charge(charge_data)


func _show_glorious_charge_text_fallback():
	"""Fallback text display if dialog fails to load."""
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]         GLORIOUS CHARGE![/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")
	add_output("[color=#" + COLOR_ERROR + "]⚠ Glorious Charge deals 2x damage but also TAKES 2x damage![/color]")
	add_output("[color=#" + COLOR_INFO + "]Target: " + pending_charge_target + "[/color]")
	add_output("")
	add_output("[color=#" + COLOR_INFO + "]Type 'charge' to execute Glorious Charge[/color]")
	add_output("[color=#" + COLOR_INFO + "]Type 'restrain' for normal attack[/color]")
	add_output("")

	set_input_enabled(true)
	command_input.grab_focus()


func _on_glorious_charge_choice_made(choice: String):
	"""Handle player's choice in Glorious Charge dialog."""
	print("GLORIOUS CHARGE CHOICE MADE: ", choice)
	print("  Marshal: ", pending_charge_marshal)
	print("  Target: ", pending_charge_target)

	# Disable input while processing
	set_input_enabled(false)

	# Display player choice in log
	var choice_text = ""
	if choice == "charge":
		choice_text = pending_charge_marshal + " unleashes a GLORIOUS CHARGE!"
		add_output("[color=#" + COLOR_BATTLE + "]🐴⚔ " + choice_text + " ⚔🐴[/color]")
	else:
		choice_text = "You restrain " + pending_charge_marshal + " - normal attack."
		add_output("[color=#" + COLOR_COMMAND + "]► " + choice_text + "[/color]")

	add_output("")

	# Send choice to backend
	api_client.send_glorious_charge_response(choice, _on_glorious_charge_response)


func _on_glorious_charge_response(response):
	"""Handle backend response after player makes Glorious Charge choice."""
	print("\n" + "=".repeat(60))
	print("GLORIOUS CHARGE RESPONSE RECEIVED:")
	print("  success: ", response.get("success", false))
	print("  message: ", response.get("message", ""))
	print("=".repeat(60) + "\n")

	# Clear pending state
	pending_charge_marshal = ""
	pending_charge_target = ""

	# Re-enable input
	set_input_enabled(true)

	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)

		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)

		# Update map with latest state
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)

		# Display result
		_display_result(response)

		# Check for game over
		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")

	add_output("")
	command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# STRATEGIC COMMAND UI (Phase J)
# ════════════════════════════════════════════════════════════════════════════

func _show_strategic_reports(response):
	"""Show strategic order reports popup after enemy phase."""
	var reports = response.get("strategic_reports", [])
	if reports.is_empty():
		_on_strategic_report_dismissed()
		return

	if strategic_report_popup == null:
		push_error("strategic_report_popup is NULL!")
		_on_strategic_report_dismissed()
		return

	var turn = current_turn
	if response.has("action_summary"):
		turn = int(response.action_summary.get("turn", current_turn))

	# Log reports to output too
	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]--- Strategic Order Updates ---[/color]")
	for report in reports:
		var marshal_name = report.get("marshal", "")
		var msg = report.get("message", "")
		if msg:
			add_output("[color=#" + COLOR_INFO + "]" + marshal_name + ": " + msg + "[/color]")
		# Log sally battle details to output
		var battle_msg = report.get("battle_message", "")
		if battle_msg:
			add_output("[color=#" + COLOR_BATTLE + "]  " + battle_msg + "[/color]")
		var outcome = report.get("outcome", "")
		if outcome:
			var outcome_color = COLOR_SUCCESS if outcome == "victory" else COLOR_ERROR if outcome == "defeat" else COLOR_BATTLE
			add_output("[color=#" + outcome_color + "]  Result: " + outcome.capitalize() + "[/color]")
	add_output("")

	strategic_report_popup.show_reports(reports, turn)


func _on_strategic_report_dismissed():
	"""Handle strategic report popup dismissed."""
	print("Strategic report popup dismissed")

	# Check if any reports have interrupts that need input
	if pending_strategic_response != null:
		var response = pending_strategic_response
		var reports = response.get("strategic_reports", [])

		# Queue up any interrupts that require input
		interrupt_queue.clear()
		for report in reports:
			if report.get("requires_input", false):
				interrupt_queue.append(report)

		# Show first interrupt if any
		if not interrupt_queue.is_empty():
			var first_interrupt = interrupt_queue.pop_front()
			_show_interrupt_popup(first_interrupt)
			return  # Don't re-enable input yet

		# Check for game over
		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				pending_strategic_response = null
				_show_game_over_screen(response.game_state)
				return

		# Check for deferred redemption (cavalry trust penalty from end-turn)
		if response.has("redemption_event"):
			pending_strategic_response = null
			pending_enemy_phase_response = null
			_show_pending_dispatch()
			_show_redemption_dialog(response.redemption_event)
			return  # Don't re-enable input until redemption resolved

	pending_strategic_response = null
	pending_enemy_phase_response = null

	# Morning Dispatch — displayed last, right before player gets control
	_show_pending_dispatch()

	set_input_enabled(true)
	command_input.grab_focus()


func _show_interrupt_popup(interrupt_data: Dictionary):
	"""Show interrupt popup for a marshal needing a decision."""
	set_input_enabled(false)

	if interrupt_popup == null:
		push_error("interrupt_popup is NULL!")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Interrupt popup not loaded![/color]")
		_process_next_interrupt()
		return

	var marshal_name = interrupt_data.get("marshal", "Marshal")
	add_output("[color=#" + COLOR_BATTLE + "]" + marshal_name + " awaits your orders![/color]")

	interrupt_popup.show_interrupt(interrupt_data)


func _on_interrupt_choice_made(marshal_name: String, response_type: String, choice: String):
	"""Handle player choosing an interrupt response."""
	print("Interrupt choice: marshal=%s, type=%s, choice=%s" % [marshal_name, response_type, choice])
	set_input_enabled(false)

	add_output("[color=#" + COLOR_COMMAND + "]> " + marshal_name + ": " + choice.replace("_", " ") + "[/color]")

	# Send to backend
	api_client.send_strategic_response(marshal_name, response_type, choice, _on_interrupt_response)


func _on_interrupt_response(response):
	"""Handle backend response to interrupt choice."""
	if response.success:
		var msg = response.get("message", "Order acknowledged.")
		add_output("[color=#" + COLOR_SUCCESS + "]" + msg + "[/color]")

		# Update UI state
		if response.has("action_summary"):
			_update_status(response.action_summary)
		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.get("message", "Error processing response.") + "[/color]")

	# Check for redemption event from strategic interrupt trust penalty
	if response.has("redemption_event"):
		interrupt_queue.clear()  # Redemption takes priority
		pending_strategic_response = null
		pending_enemy_phase_response = null
		_show_pending_dispatch()
		_show_redemption_dialog(response.redemption_event)
		return  # Don't re-enable input until redemption resolved

	# Process next interrupt in queue
	_process_next_interrupt()


func _process_next_interrupt():
	"""Show next queued interrupt or re-enable input."""
	if not interrupt_queue.is_empty():
		var next_interrupt = interrupt_queue.pop_front()
		_show_interrupt_popup(next_interrupt)
	else:
		# Check for deferred redemption (cavalry trust penalty from end-turn)
		if pending_strategic_response and pending_strategic_response.has("redemption_event"):
			var event = pending_strategic_response.redemption_event
			pending_strategic_response = null
			pending_enemy_phase_response = null
			_show_pending_dispatch()
			_show_redemption_dialog(event)
			return  # Don't re-enable input until redemption resolved
		# All interrupts processed
		pending_strategic_response = null
		pending_enemy_phase_response = null
		set_input_enabled(true)
		command_input.grab_focus()


func _show_clarification_popup(response):
	"""Show clarification popup for literal marshals."""
	set_input_enabled(false)

	var data = response.get("clarification_data", response)

	if clarification_popup == null:
		push_error("clarification_popup is NULL!")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Clarification popup not loaded![/color]")
		set_input_enabled(true)
		return

	var marshal_name = data.get("marshal", "Marshal")
	add_output("[color=#" + COLOR_MARSHAL + "]" + marshal_name + " requests clarification...[/color]")

	clarification_popup.show_clarification(data)


func _on_clarification_choice_made(marshal_name: String, chosen_target: String, strategic_type: String):
	"""Handle player selecting a clarification target."""
	print("Clarification choice: marshal=%s, target=%s, type=%s" % [marshal_name, chosen_target, strategic_type])
	add_output("[color=#" + COLOR_COMMAND + "]> " + marshal_name + ", target " + chosen_target + "[/color]")

	# Reissue with correct strategic keyword for the command type
	var keyword_map = {
		"PURSUE": "pursue",
		"MOVE_TO": "march to",
		"SUPPORT": "support",
		"HOLD": "hold",
	}
	var keyword = keyword_map.get(strategic_type, "pursue")
	var clarified_command = marshal_name + " " + keyword + " " + chosen_target
	set_input_enabled(false)
	api_client.send_command(clarified_command, _on_command_result)


func _on_clarification_cancelled():
	"""Handle player cancelling a clarification."""
	add_output("[color=#" + COLOR_INFO + "]Order cancelled.[/color]")
	set_input_enabled(true)
	command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# SESSION 8C DIPLOMATIC POPUP HANDLERS
# ════════════════════════════════════════════════════════════════════════════

func _on_coalition_popup_dismissed():
	"""Handle coalition declaration popup dismissed."""
	add_output("[color=#e04040]The coalition has declared war on France.[/color]")
	set_input_enabled(true)
	command_input.grab_focus()

func _on_proposal_confirm_choice(action: String, data: Dictionary):
	"""Handle player response to outgoing proposal confirmation popup.
	CRITICAL: Use send_dialogue_response (direct action index), NOT send_command.
	Keyword routing in /command misroutes terms_guidance actions:
	'territory_no_ap' contains 'territory' → matches territory_yes → Belgium bug.
	See BUGFIX_PLAN_PROPOSAL_FLOW.md Bug 6."""
	# Send the raw action directly to dialogue endpoint via 1-based option index.
	# DO NOT construct natural language — keyword routing causes mismatches.
	var options = data.get("options", [])
	var choice_index = -1
	for i in range(options.size()):
		if options[i].get("action", "") == action:
			choice_index = i + 1  # 1-based
			break
	if choice_index > 0:
		add_output("[color=#d9c08c]Directing Talleyrand: %s[/color]" % action.replace("_", " "))
		set_input_enabled(false)
		api_client.send_dialogue_response(choice_index, _on_command_result)
	else:
		# Fallback for unknown actions — use old keyword path
		var target = data.get("target_nation", "Unknown")
		var _ACTION_KEYWORD_MAP = {
			"execute_proposal": "send",
			"modify_harsh": "harsh",
			"modify_generous": "generous",
			"expand_options": "adjust",
			"send_override": "proceed",
			"send_suggested": "trust",
			"start_mission": "begin",
			"dismiss": "dismiss",
			"reconsider": "reconsider",
			"elaborate": "elaborate",
			"expand_to_proposal": "elaborate",
			"review_counter": "review",
			"accept_with_conflict": "accept",
			"cancel_mission": "cancel",
			"force_declare_war": "proceed",
			"accept_ai_proposal": "accept",
			"reject_ai_proposal": "reject",
			"accept_counter_offer": "accept",
			"reject_counter_offer": "reject",
		}
		var keyword = _ACTION_KEYWORD_MAP.get(action, action)
		var command = "Talleyrand, %s the %s proposal" % [keyword, target]
		add_output("[color=#d9c08c]Directing Talleyrand: %s[/color]" % keyword)
		set_input_enabled(false)
		api_client.send_command(command, _on_command_result)

func _on_incoming_proposal_choice(choice: String, data: Dictionary):
	"""Handle player response to AI diplomatic proposal."""
	var from_nation = data.get("from_nation", "Unknown")
	var command = "Talleyrand, %s the %s proposal" % [choice, from_nation]
	add_output("[color=#d9c08c]Responding to %s's proposal: %s[/color]" % [from_nation, choice])
	set_input_enabled(false)
	api_client.send_command(command, _on_command_result)

func _on_talleyrand_objection_choice(choice: String, data: Dictionary):
	"""Handle player response to Talleyrand's diplomatic objection."""
	if choice == "proceed":
		add_output("[color=#d9c08c]Overriding Talleyrand's objection...[/color]")
		set_input_enabled(false)
		api_client.send_command("Talleyrand, proceed with the proposal", _on_command_result)
	elif choice == "modify":
		add_output("[color=#d9c08c]Reconsidering the proposal...[/color]")
		set_input_enabled(true)
		command_input.grab_focus()
	else:
		add_output("[color=#" + COLOR_INFO + "]Proposal cancelled.[/color]")
		set_input_enabled(false)
		api_client.send_command("Talleyrand, dismiss", _on_command_result)

func _on_sabotage_discovery_choice(choice: String, data: Dictionary):
	"""Handle player response to sabotage discovery."""
	var target = data.get("target_nation", "unknown")
	var command = "Talleyrand, I %s your actions regarding %s" % [choice, target]
	add_output("[color=#d9c08c]%s Talleyrand's sabotage...[/color]" % choice.capitalize())
	set_input_enabled(false)
	api_client.send_command(command, _on_command_result)

func _on_talleyrand_redemption_choice(choice: String, data: Dictionary):
	"""Handle player response to Talleyrand redemption event."""
	var command = "Talleyrand, %s" % choice
	add_output("[color=#d9c08c]Talleyrand redemption: %s[/color]" % choice)
	set_input_enabled(false)
	api_client.send_command(command, _on_command_result)

func _on_vassal_rebellion_choice(choice: String, data: Dictionary):
	"""Handle player response to vassal rebellion imminent."""
	var nation = data.get("nation", "unknown")
	var command = "Talleyrand, %s regarding %s rebellion" % [choice, nation]
	add_output("[color=#d9c08c]Vassal %s: %s[/color]" % [nation, choice])
	set_input_enabled(false)
	api_client.send_command(command, _on_command_result)


# ════════════════════════════════════════════════════════════════════════════
# PAUSE MENU (Phase 6.5)
# ════════════════════════════════════════════════════════════════════════════

func _is_modal_dialog_open() -> bool:
	"""True when a modal dialog requiring player choice is visible.
	These block EVERYTHING. Campaign log is NOT a modal — it's a screen."""
	if objection_dialog and objection_dialog.visible:
		return true
	if redemption_dialog and redemption_dialog.visible:
		return true
	if enemy_phase_dialog and enemy_phase_dialog.visible:
		return true
	if glorious_charge_dialog and glorious_charge_dialog.visible:
		return true
	if capture_choice_dialog and capture_choice_dialog.visible:
		return true
	if load_dialog and load_dialog.visible:
		return true
	if strategic_report_popup and strategic_report_popup.visible:
		return true
	if interrupt_popup and interrupt_popup.visible:
		return true
	if clarification_popup and clarification_popup.visible:
		return true
	# Session 8C diplomatic popups
	if coalition_declaration_popup and coalition_declaration_popup.visible:
		return true
	if incoming_proposal_popup and incoming_proposal_popup.visible:
		return true
	if talleyrand_objection_popup and talleyrand_objection_popup.visible:
		return true
	if sabotage_discovery_popup and sabotage_discovery_popup.visible:
		return true
	if talleyrand_redemption_popup and talleyrand_redemption_popup.visible:
		return true
	if vassal_rebellion_popup and vassal_rebellion_popup.visible:
		return true
	if proposal_confirm_popup and proposal_confirm_popup.visible:
		return true
	# Diplomacy Wizard (Session B)
	if diplomacy_wizard and diplomacy_wizard.visible:
		return true
	return false

func _is_screen_open() -> bool:
	"""True when a top bar screen is open. Blocks map, allows terminal."""
	return top_bar != null and top_bar.is_screen_open()

func _is_hotkey_blocked() -> bool:
	"""True when hotkeys should not fire (typing or modal open)."""
	return command_input.has_focus() or _is_modal_dialog_open()

func _on_screen_changed(screen_name: String):
	"""Handle top bar screen open/close — toggle map interaction."""
	if screen_name != "":
		# Screen opened — block map interaction
		map_area.mouse_filter = Control.MOUSE_FILTER_IGNORE
		map_area.panning_enabled = false
	else:
		# All screens closed — restore map interaction
		map_area.mouse_filter = Control.MOUSE_FILTER_STOP
		map_area.panning_enabled = true
	# N4i: Update war panel visibility when screens open/close
	_update_war_panel_visibility()


func _on_envoy_clicked():
	"""Handle envoy indicator click — type diplomatic report command."""
	command_input.text = "Talleyrand, report on the waiting envoy"
	command_input.grab_focus()
	command_input.caret_column = command_input.text.length()


# ════════════════════════════════════════════════════════════════════════════
# DIPLOMACY WIZARD (Session B)
# ════════════════════════════════════════════════════════════════════════════

func _on_diplomacy_button_pressed():
	"""Handle Diplomacy button click."""
	_open_diplomacy_wizard()


func _open_diplomacy_wizard():
	"""Open the diplomacy wizard (§9c, §9d)."""
	if _is_modal_dialog_open():
		return
	if not diplomacy_wizard:
		return
	# Close any open top bar screens first (§9d)
	if top_bar and top_bar.is_screen_open():
		top_bar.close_all_screens()
	diplomacy_wizard.open()


func _on_wizard_command_selected(command: String):
	"""Handle wizard action selection — execute constructed command (§2 Step 3)."""
	if command.is_empty():
		return

	# Add to history
	_add_to_history(command)

	# Display the command in terminal
	add_output("")
	add_output("[color=#" + COLOR_COMMAND + "]► " + command + "[/color]")

	# Disable input while processing
	set_input_enabled(false)

	# Send to backend via normal command flow
	api_client.send_command(command, _on_command_result)


# ════════════════════════════════════════════════════════════════════════════
# WAR STATUS PANEL (N4)
# ════════════════════════════════════════════════════════════════════════════

func _update_war_panel_visibility():
	"""N4i: Hide HUD when screens/modals open, show when wars exist."""
	var should_show = (
		not _is_screen_open()
		and not _is_modal_dialog_open()
		and _has_active_wars
	)
	if war_status_panel:
		war_status_panel.visible = should_show
	if not should_show and war_detail_popup:
		war_detail_popup.hide()


func _on_war_card_clicked(nation: String, status: String):
	"""N4h: Handle war card click — open detail popup."""
	if war_detail_popup == null:
		return
	if status == "armistice":
		var war_data = _find_war_data(nation)
		if war_data != null:
			war_detail_popup.show_armistice(war_data)
	else:
		var war_data = _find_war_data(nation)
		if war_data != null:
			war_detail_popup.show_war(war_data, _cached_coalition_data)


func _on_coalition_header_clicked():
	"""N4h: Handle coalition header click — open coalition detail."""
	if war_detail_popup == null or _cached_coalition_data == null:
		return
	war_detail_popup.show_coalition(_cached_coalition_data, _cached_wars)


func _on_war_negotiate_clicked(nation: String):
	"""N4h: Handle [Negotiate Peace] / [Diplomatic Options] — open wizard for nation."""
	if diplomacy_wizard:
		diplomacy_wizard.open_for_nation(nation)


func _on_war_target_clicked(nation: String):
	"""N4h: Handle [Target X] — open wizard for that nation."""
	if diplomacy_wizard:
		diplomacy_wizard.open_for_nation(nation)


func _find_war_data(nation: String):
	"""Find war data for a specific nation from cached active_wars."""
	for w in _cached_wars:
		if str(w.get("opponent", "")) == nation:
			return w
	return null


func _process_active_wars(response: Dictionary):
	"""N4i: Parse active_wars from response and update HUD + detail popup."""
	var active_wars_data = response.get("active_wars", null)
	if active_wars_data == null:
		return
	if not active_wars_data is Dictionary:
		return

	if war_status_panel:
		war_status_panel.update_wars(active_wars_data)

	_cached_wars = active_wars_data.get("wars", [])
	_cached_coalition_data = active_wars_data.get("coalition", null)
	_has_active_wars = not _cached_wars.is_empty()

	# Refresh detail popup if open (in-place update, don't close)
	if war_detail_popup and war_detail_popup.visible:
		war_detail_popup.refresh_if_open(active_wars_data)

	_update_war_panel_visibility()


func _on_pause_save_requested():
	"""Handle Save Game from pause menu."""
	add_output("[color=#" + COLOR_INFO + "]Saving game...[/color]")
	api_client.save_game("quicksave", _on_pause_save_result)

func _on_pause_save_result(response):
	"""Handle save result from pause menu."""
	if response.success:
		add_output("[color=#" + COLOR_SUCCESS + "]Game saved successfully.[/color]")
	else:
		add_output("[color=#" + COLOR_ERROR + "]Save failed: " + str(response.get("message", "Unknown error")) + "[/color]")
	add_output("")

func _on_pause_load_requested():
	"""Handle Load Game from pause menu."""
	_show_load_dialog()

extends Control

# =============================================================================
# PROJECT SOVEREIGN - Main UI Controller
# =============================================================================
# Handles command input, output display, and status updates
# Color scheme: Dark blue background, gold accents, cream text
# =============================================================================

# Set to true for verbose debug logging in editor
const DEBUG_VERBOSE := false
const PROPOSAL_CONFIRM_DIALOGUE_TYPES := [
	"proposal_confirm",
	"pushback_confirm",
	"proposal_execute",
	"proposal_options",
	"mission",
	"feasibility",
	"advisory",
	"force_declare_war_confirmation",
	"conflict_alert",
	"terms_guidance",
	"ultimatum_confirm",
	"ultimatum_demand_wizard",
	"war_purpose_selection",
	"settlement_confirm",
	"settlement_scope_replace_confirm",
	# G4F-8: the pair-substitute confirm chooser (leave the joint
	# settlement?) — joint draft kept until Proceed; Cancel restores REVIEW.
	"settlement_pair_substitute_confirm",
	# SC-5 reversal commit 2 (Slice G1): incoming AI settlement offers
	# reuse the proposal_confirm popup; the popup script branches on
	# dtype to render the incoming-offer arrival copy and Voice Bible
	# §16.1 incoming-offer voice.
	"incoming_settlement_offer",
	"ally_settlement_petition",
]
const SETTLEMENT_DIALOGUE_ACTIONS := [
	"confirm_settlement",
	"revise_settlement_terms",
	"back_out_settlement",
	# Re-front Slice 1 PROPOSE rail. `submit_settlement_for_review` round-trips
	# so the backend re-stages the REVIEW surface for the per-court ratification
	# gate. (GT-Slice-4: the settlement `adjust_terms` rail verb is retired with
	# the freeform editor — the guided per-court rows are the deep tier. The
	# bilateral terms-guidance flow still owns the backend `adjust_terms`
	# action id and resolves through the option-index path.)
	"submit_settlement_for_review",
	# Re-front UX follow-up: a blocked REVIEW offers "Return to terms" to
	# re-stage the conversational PROPOSE surface (round-trips, no params).
	"return_to_settlement_terms",
	# Re-front Slice 2 PROPOSE Tier-2 verbs: intent dials (whole-table from the
	# rail, focused from a per-court row), coverage edits, and court focus. They
	# round-trip with structured `scope` / `nation` params (sent as
	# `action_params`) so the backend re-drafts + re-scores per court live.
	"settlement_dial_harsher",
	"settlement_dial_generous",
	"settlement_cover_add",
	"settlement_cover_drop",
	"settlement_focus_court",
	# GT-Slice-1 guided demand-mutation verbs (Guided Terms §7 wiring
	# point 3). Round-trip with structured `nation` / `group` /
	# `clause_type` / `clause_index` / magnitude params as `action_params`;
	# the backend authors the fully-formed clause (direction fixed per
	# option) and re-scores the court live. The per-court row UI that
	# emits them lands in GT-Slice-3 — the ids are whitelisted now so the
	# transport contract is complete from the backend slice.
	"settlement_demand_add",
	"settlement_demand_remove",
	"settlement_demand_set_magnitude",
	# SC-5R-2 follow-up: the non-destructive Back Out on the PROPOSE
	# authoring surface. Pops the staged settlement_confirm while preserving
	# the scoped draft (back_out_settlement discards; this suspend does not).
	"suspend_settlement_editor",
	"open_war_detail",
	"re_author_with_concessions",
	"apply_concession_baseline_replacement",
	"keep_current_settlement_draft",
	# SC-29 / G2-Slice-7 pair-scoped peace substitute CTAs. The backend
	# dialogue handler re-runs `evaluate_pair_peace_substitute_eligibility`
	# at click time and either stages the underlying propose_armistice /
	# propose_peace proposal dialogue or returns a humanized refusal.
	"seek_bilateral_peace",
	"seek_armistice_instead",
	# SC-31 / G2-Slice-8 Author surrender terms (Talleyrand). Backend
	# handler revalidates surrender-preset visibility at click time and
	# stages a fresh settlement_confirm with surrender_preset=true on
	# success, or returns a humanized refusal without mutating the draft.
	"author_surrender_terms",
	"apply_surrender_preset_replacement",
	# SC-33 / G2-Slice-9 recurring-gold authoring path. Backend stages
	# a finite `gold_per_turn` draft and revalidates it at click time.
	"author_recurring_gold_terms",
	"apply_recurring_gold_preset_replacement",
	# Empty first-open settlement authoring controls for winning-side
	# gold demands.
	"author_gold_indemnity_terms",
	"author_gold_per_turn_terms",
	# G2-Slice-G2e same-war different-scope settlement chooser.
	"replace_current_scope_draft",
	"keep_current_scope_draft",
	# G4F-8 pair-substitute confirm chooser: Proceed runs the handoff with
	# terms carry-over; Cancel restores the prior REVIEW exactly.
	"confirm_pair_substitute",
	"keep_joint_settlement",
	# SC-5 reversal commit 2 (Slice G1) incoming-offer actions. Accept
	# stages settlement_confirm with the offered package preserved;
	# Reject removes the pending entry without mutation; Request
	# Revision opens the editor seeded from the offered terms so the
	# player can answer with a counter draft.
	"accept_settlement_offer",
	"reject_settlement_offer",
	"request_settlement_revision",
	"acknowledge_ally_settlement_petition",
	# Slice H (approved July 3, 2026) full-agency ally petition verbs.
	# Grant adds the petitioned clause to the mounted PROPOSE draft;
	# Decline / Proceed Regardless records the refusal; Honor adjusts
	# the draft so a pledged war-bargain claim survives ratification.
	"grant_ally_petition_clause",
	"decline_ally_petition",
	"honor_bargain_in_settlement",
]

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
@onready var open_envoys_button = $BottomLeftUI/MainMargin/MainLayout/InputSection/OpenEnvoysButton

# UI References - Minimize/Restore
@onready var bottom_left_ui = $BottomLeftUI
@onready var minimize_button = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/TitleRow/MinimizeButton
@onready var restore_button = $RestoreButton

# UI References - Terminal text scale (A− / A+), UI-2
@onready var scale_down_button = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/TitleRow/ScaleDownButton
@onready var scale_up_button = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/TitleRow/ScaleUpButton

# ── UI-2: Expandable command window + UI scale (DEF-13 fold) ──
# The terminal is anchored bottom-left; it grows UP and to the RIGHT from that
# fixed corner (offset_left / offset_bottom stay put; offset_right / offset_top
# carry the width / height). A corner grip drives the resize; A− / A+ drive a
# crisp per-terminal font scale. Both persist via UiSettings.
const GRIP_SIZE := 20.0
const TERMINAL_ANCHOR_LEFT := 10.0    # matches BottomLeftUI offset_left in main.tscn
const TERMINAL_ANCHOR_BOTTOM := -10.0  # matches BottomLeftUI offset_bottom in main.tscn
var _terminal_width := UiSettings.DEFAULT_TERMINAL_WIDTH
var _terminal_height := UiSettings.DEFAULT_TERMINAL_HEIGHT
var _terminal_scale := UiSettings.DEFAULT_TERMINAL_SCALE
var resize_grip: Panel = null
var _grip_dragging := false
# Auto-discovered [{node, key, base}] of every font override inside the terminal,
# captured from the .tscn at boot so the scale multiplies the authored sizes.
var _scalable_fonts: Array = []
# Top Bar (Session A)
var top_bar = null

# Map reference
@onready var map_area = $MapArea
var _pending_initial_map_data: Dictionary = {}
var _pending_initial_map_topology: Dictionary = {}
var _initial_map_bootstrapped: bool = false
var _initial_topology_failed: bool = false

# Dialog Manager (R16)
var dialog_manager = null

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
var reward_dialog = null  # ES-7 second pass (§0.6.8): the Marshal's Reward dialog
var marshal_petition_dialog = null  # Jealousy v3.2: the marshal-petition channel (layer 114)

# Load Game Dialog (Phase 6: Save/Load)
var load_dialog = null

# Strategic Command Dialogs (Phase J)
var strategic_report_popup = null
var interrupt_popup = null
var clarification_popup = null
# CR-2: true while the backend holds a pending command_clarification dialogue
var _clarification_backend_pending := false
var pending_strategic_response = null  # Store response for post-report flow
var interrupt_queue: Array = []  # Queue of interrupts to show one at a time

# Session 8C Diplomatic Popups
var incoming_proposal_popup = null
var talleyrand_objection_popup = null
var sabotage_discovery_popup = null
# PL-23: talleyrand_redemption_popup removed (trust system deleted)
var vassal_rebellion_popup = null
var proposal_confirm_popup = null
# GT-Slice-4: the SC-5R EDIT-mode settlement editor popup is retired. The
# guided per-court rows on the proposal_confirm PROPOSE surface are the deep
# authoring tier; settlement failures re-attach the dialogue + error_display
# (CH-5) and re-mount the proposal_confirm popup.

# Commitment Paradox Popup (Deep Audit Session 8)
var commitment_paradox_popup = null

# Diplomacy Wizard (Diplomacy Button Session B)
var diplomacy_wizard = null

# War Status Panel (N4: HUD Layer 1 + Detail Layer 2)
var war_status_panel = null
var war_detail_popup = null
var _cached_wars: Array = []
var _seen_war_ids: Dictionary = {}
var _cached_coalition_data = null
var _has_active_wars: bool = false
var _last_command_response: Dictionary = {}  # Cached for post-popup war panel refresh
var _dismissed_proposal_nation: String = ""  # PL-27: Suppress re-show after "Not Now"
var _pending_envoy_request_active: bool = false
var _current_envoy_count: int = 0  # Tracks pending envoy count for end-turn gate
var _awaiting_end_turn_confirmation: bool = false
var mailbox_panel = null  # Session 2 follow-up: browsable envoy inbox
var _pre_hud_response_routes: Array = []
var _post_hud_response_routes: Array = []

# Pause Menu (Phase 6.5)
var pause_menu = null

# Campaign Log (Phase 6.5)
var campaign_log = null
var dispatch_view = null

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

# Message history limit (prevents infinite growth)
const MAX_MESSAGES = 100
var message_count = 0

func _ready():
	# Create API client
	api_client = load("res://scripts/api_client.gd").new()
	add_child(api_client)

	# ── Dialog Manager (R16) — centralized dialog instantiation ──
	dialog_manager = DialogManager.new()
	add_child(dialog_manager)

	# Modal dialogs (layers 101-118, set in .tscn files)
	objection_dialog = dialog_manager.register("objection", "res://scenes/objection_dialog.tscn")
	if objection_dialog:
		objection_dialog.choice_made.connect(_on_objection_choice_made)

	redemption_dialog = dialog_manager.register("redemption", "res://scenes/redemption_dialog.tscn")
	if redemption_dialog:
		redemption_dialog.choice_made.connect(_on_redemption_choice_made)

	enemy_phase_dialog = dialog_manager.register("enemy_phase", "res://scenes/enemy_phase_dialog.tscn")
	if enemy_phase_dialog:
		enemy_phase_dialog.dismissed.connect(_on_enemy_phase_dismissed)

	glorious_charge_dialog = dialog_manager.register("glorious_charge", "res://scenes/glorious_charge_dialog.tscn")
	if glorious_charge_dialog:
		glorious_charge_dialog.choice_made.connect(_on_glorious_charge_choice_made)

	capture_choice_dialog = dialog_manager.register("capture_choice", "res://scenes/capture_choice_dialog.tscn")
	if capture_choice_dialog:
		capture_choice_dialog.choice_made.connect(_on_capture_choice_made)

	# ES-7 second pass (§0.6.8 item 6): the Marshal's Reward dialog (layer 109)
	reward_dialog = dialog_manager.register("reward_dialog", "res://scenes/reward_dialog.tscn")
	if reward_dialog:
		reward_dialog.reward_command.connect(_on_reward_command)

	# Jealousy v3.2 (spec §0.2-10): the marshal-petition channel (layer 114) —
	# jealousy confrontations, rivalry events, Fontainebleau, war-weary counsel.
	marshal_petition_dialog = dialog_manager.register("marshal_petition", "res://scenes/marshal_petition_dialog.tscn")
	if marshal_petition_dialog:
		marshal_petition_dialog.petition_choice.connect(_on_marshal_petition_choice)

	load_dialog = dialog_manager.register("load", "res://scenes/load_dialog.tscn")
	if load_dialog:
		load_dialog.save_selected.connect(_on_load_save_selected)
		load_dialog.load_cancelled.connect(_on_load_cancelled)

	strategic_report_popup = dialog_manager.register("strategic_report", "res://scenes/strategic_report_popup.tscn")
	if strategic_report_popup:
		strategic_report_popup.dismissed.connect(_on_strategic_report_dismissed)

	interrupt_popup = dialog_manager.register("interrupt", "res://scenes/interrupt_popup.tscn")
	if interrupt_popup:
		interrupt_popup.choice_made.connect(_on_interrupt_choice_made)

	clarification_popup = dialog_manager.register("clarification", "res://scenes/clarification_popup.tscn")
	if clarification_popup:
		clarification_popup.clarification_choice.connect(_on_clarification_choice_made)
		clarification_popup.clarification_command.connect(_on_clarification_command)
		clarification_popup.cancelled.connect(_on_clarification_cancelled)

	# Diplomatic popups
	incoming_proposal_popup = dialog_manager.register("incoming_proposal", "res://scenes/incoming_proposal_popup.tscn")
	if incoming_proposal_popup:
		incoming_proposal_popup.choice_made.connect(_on_incoming_proposal_choice)

	proposal_confirm_popup = dialog_manager.register("proposal_confirm", "res://scenes/proposal_confirm_popup.tscn")
	if proposal_confirm_popup:
		proposal_confirm_popup.choice_made.connect(_on_proposal_confirm_choice)

	talleyrand_objection_popup = dialog_manager.register("talleyrand_objection", "res://scenes/talleyrand_objection_popup.tscn")
	if talleyrand_objection_popup:
		talleyrand_objection_popup.choice_made.connect(_on_talleyrand_objection_choice)

	sabotage_discovery_popup = dialog_manager.register("sabotage_discovery", "res://scenes/sabotage_discovery_popup.tscn")
	if sabotage_discovery_popup:
		sabotage_discovery_popup.choice_made.connect(_on_sabotage_discovery_choice)

	# PL-23: talleyrand_redemption_popup registration removed

	vassal_rebellion_popup = dialog_manager.register("vassal_rebellion", "res://scenes/vassal_rebellion_popup.tscn")
	if vassal_rebellion_popup:
		vassal_rebellion_popup.choice_made.connect(_on_vassal_rebellion_choice)

	commitment_paradox_popup = dialog_manager.register("commitment_paradox", "res://scenes/commitment_paradox_popup.tscn")
	if commitment_paradox_popup:
		commitment_paradox_popup.choice_made.connect(_on_commitment_paradox_choice)

	_configure_response_routes()

	# Diplomacy wizard
	diplomacy_wizard = dialog_manager.register("diplomacy_wizard", "res://scenes/diplomacy_wizard.tscn")
	if diplomacy_wizard and diplomacy_wizard.has_signal("structured_command_selected"):
		diplomacy_wizard.structured_command_selected.connect(_on_wizard_structured_command_selected)
	if diplomacy_wizard:
		diplomacy_wizard.command_selected.connect(_on_wizard_command_selected)
		if diplomacy_wizard.has_signal("open_envoys_requested"):
			diplomacy_wizard.open_envoys_requested.connect(_on_wizard_open_envoys_requested)

	# War Status Panel (N4: HUD Layer 25 + Detail Layer 30) — not modal
	war_status_panel = dialog_manager.register("war_status_panel", "res://scenes/war_status_panel.tscn", false)
	if war_status_panel:
		war_status_panel.card_clicked.connect(_on_war_card_clicked)
		war_status_panel.coalition_header_clicked.connect(_on_coalition_header_clicked)

	war_detail_popup = dialog_manager.register("war_detail", "res://scenes/war_detail_popup.tscn")
	if war_detail_popup:
		war_detail_popup.negotiate_clicked.connect(_on_war_negotiate_clicked)
		war_detail_popup.target_clicked.connect(_on_war_target_clicked)
		if war_detail_popup.has_signal("settlement_clicked"):
			war_detail_popup.settlement_clicked.connect(_on_war_settlement_clicked)
		if war_detail_popup.has_signal("request_terms_clicked"):
			war_detail_popup.request_terms_clicked.connect(_on_war_request_terms_clicked)
		war_detail_popup.war_ended.connect(_on_war_ended_notification)

	# Mailbox panel (Session 2 follow-up: browsable inbox, layer 119)
	mailbox_panel = dialog_manager.register("mailbox_panel", "res://scenes/mailbox_panel.tscn")
	if mailbox_panel:
		mailbox_panel.item_selected.connect(_on_mailbox_item_selected)
		mailbox_panel.panel_closed.connect(_on_mailbox_panel_closed)

	# Pause menu (layer 120, always on top)
	pause_menu = dialog_manager.register("pause_menu", "res://scenes/pause_menu.tscn")
	if pause_menu:
		pause_menu.save_requested.connect(_on_pause_save_requested)
		pause_menu.load_requested.connect(_on_pause_load_requested)
		pause_menu.new_game_requested.connect(_on_pause_new_game_requested)

	# ── Top Bar + Screens (special setup, not managed by DialogManager) ──
	var top_bar_scene = load("res://scenes/top_bar.tscn")
	if top_bar_scene:
		top_bar = top_bar_scene.instantiate()
		add_child(top_bar)
		top_bar.set_api_client(api_client)
		top_bar.screen_changed.connect(_on_screen_changed)
		top_bar.envoy_clicked.connect(_on_envoy_clicked)

	# Screens registered with top bar
	var _screen_configs = [
		["event_log", "res://scenes/campaign_log.tscn"],
		["dispatch", "res://scenes/dispatch_view.tscn"],
		["ledger", "res://scenes/strategic_ledger.tscn"],
		["generals", "res://scenes/marshal_management.tscn"],
		["diplomatic_ledger", "res://scenes/diplomatic_ledger.tscn"],
	]
	for config in _screen_configs:
		var scene = load(config[1])
		if scene:
			var instance = scene.instantiate()
			add_child(instance)
			if top_bar:
				top_bar.register_screen(config[0], instance)
			# Keep campaign_log reference for direct access
			if config[0] == "event_log":
				campaign_log = instance
			elif config[0] == "dispatch":
				dispatch_view = instance
				if dispatch_view.has_signal("open_envoys_requested"):
					dispatch_view.open_envoys_requested.connect(_on_dispatch_open_envoys_requested)
			elif config[0] == "generals":
				# ES-7 second pass (§0.6.8): the card's [Reward…] link
				if instance.has_signal("reward_requested"):
					instance.reward_requested.connect(_on_reward_requested)
				# Marshal Recruitment (Jealousy v3.2): the Commission view
				if instance.has_signal("commission_requested"):
					instance.commission_requested.connect(_on_commission_requested)

	# Notification bar — reparented into top bar
	var notification_bar_scene = load("res://scenes/notification_bar.tscn")
	if notification_bar_scene:
		notification_bar = notification_bar_scene.instantiate()
		if top_bar and top_bar.notification_area:
			top_bar.notification_area.add_child(notification_bar)
		else:
			add_child(notification_bar)
		notification_bar.set_api_client(api_client)
		if notification_bar.has_signal("notification_review_requested"):
			notification_bar.notification_review_requested.connect(_on_notification_review_requested)

	# Connect signals
	if not send_button.pressed.is_connected(_on_send_button_pressed):
		send_button.pressed.connect(_on_send_button_pressed)

	if not command_input.text_submitted.is_connected(_on_command_submitted):
		command_input.text_submitted.connect(_on_command_submitted)

	if not end_turn_button.pressed.is_connected(_on_end_turn_pressed):
		end_turn_button.pressed.connect(_on_end_turn_pressed)

	if not diplomacy_button.pressed.is_connected(_on_diplomacy_button_pressed):
		diplomacy_button.pressed.connect(_on_diplomacy_button_pressed)

	if not open_envoys_button.pressed.is_connected(_on_open_envoys_button_pressed):
		open_envoys_button.pressed.connect(_on_open_envoys_button_pressed)

	if not command_input.gui_input.is_connected(_on_command_input_gui_input):
		command_input.gui_input.connect(_on_command_input_gui_input)

	# Minimize/Restore terminal panel
	if not minimize_button.pressed.is_connected(_minimize_terminal):
		minimize_button.pressed.connect(_minimize_terminal)
	if not restore_button.pressed.is_connected(_restore_terminal):
		restore_button.pressed.connect(_restore_terminal)

	# ── UI-2: expandable + scaling command window (DEF-13 fold) ──
	# Apply the saved global interface scale FIRST so the logical viewport is
	# settled before the terminal geometry is computed in logical coordinates.
	_apply_ui_scale(UiSettings.get_ui_scale(), false)
	_setup_scalable_terminal()
	# The pause-menu Settings slider drives the global scale through us (we own
	# the map compensation + persistence).
	if pause_menu and pause_menu.has_signal("ui_scale_changed"):
		pause_menu.ui_scale_changed.connect(_on_ui_scale_changed)
	if not resized.is_connected(_on_root_resized):
		resized.connect(_on_root_resized)

	# Start disabled until connected
	set_input_enabled(false)
	if map_area:
		# Keep the placeholder renderer hidden until `/map_topology` arrives so
		# startup does not flash an empty connection layer before the rebuild.
		map_area.visible = false

	# Welcome message
	_show_welcome()

	# Test connection after brief delay
	await get_tree().create_timer(0.5).timeout
	test_connection()

func _show_welcome():
	"""Display welcome message with proper formatting."""
	add_output("")
	add_output("[color=#" + Utils.COLOR_GOLD + "][b]═══════════════════════════════════════[/b][/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "][b]        IMPERIAL HEADQUARTERS[/b][/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "][b]═══════════════════════════════════════[/b][/color]")
	add_output("")
	add_output("[color=#" + Utils.COLOR_INFO + "]September 1805 — The War of the Third Coalition[/color]")
	add_output("[color=#" + Utils.COLOR_INFO + "]You are Napoleon Bonaparte.[/color]")
	add_output("")

func test_connection():
	"""Test if backend is running."""
	add_output("[color=#" + Utils.COLOR_INFO + "]Establishing connection to headquarters...[/color]")
	api_client.test_connection(_on_connection_test)

func _on_connection_test(response):
	"""Handle connection test response."""
	if response.success:
		add_output("[color=#" + Utils.COLOR_SUCCESS + "]✓ Communications established![/color]")
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

		# Fetch static map topology (adjacencies) from backend — §3.2 replaces
		# the hardcoded REGION_CONNECTIONS that used to live in map.gd.
		_initial_topology_failed = false
		api_client.get_map_topology(_on_map_topology_received)

		# Update map with initial state
		if response.has("game_state") and response.game_state.has("map_data"):
			if DEBUG_VERBOSE:
				print("MAIN: Connection test - map_data found, awaiting topology bootstrap")
			if _initial_map_bootstrapped:
				map_area.update_all_regions(response.game_state.map_data)
			else:
				_pending_initial_map_data = response.game_state.map_data.duplicate(true)
				_try_finalize_initial_map_bootstrap()
		elif DEBUG_VERBOSE:
			print("⚠️  MAIN: Connection test - NO map_data in response!")

		# Show instructions
		add_output("[color=#" + Utils.COLOR_INFO + "]Your marshals await your orders, Sire.[/color]")
		add_output("")
		add_output("[color=#" + Utils.COLOR_INFO + "]Commands:[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]  • \"Ney, attack Mack\"[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]  • \"scout Swabia\" or \"move to Flanders\"[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]  • \"recruit\" or \"end turn\"[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]  • Diplomacy: click [b][Diplomacy][/b] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]  • Generals: press [b]G[/b] to review your marshals — their loyalty, rewards (duchies & rentes), and grievances[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]  • Map: M cycles view (blended / political / terrain), +/- zoom, Home recenters[/color]")
		add_output("")
		_add_separator()
		
		set_input_enabled(true)
	else:
		add_output("[color=#" + Utils.COLOR_ERROR + "]✗ Cannot reach headquarters![/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]Start the Python server: python backend/main.py[/color]")
		add_output("")


func _on_map_topology_received(response):
	"""Backend /map_topology payload — hand off adjacency to the map renderer (§3.2)."""
	if not response or not response.get("success", false):
		if DEBUG_VERBOSE:
			print("⚠️  MAIN: /map_topology fetch failed: %s" % response)
		if not _initial_map_bootstrapped:
			_initial_topology_failed = true
			_try_finalize_initial_map_bootstrap()
		return
	if _initial_map_bootstrapped:
		if map_area and map_area.has_method("set_region_topology"):
			map_area.set_region_topology(response)
		return
	_pending_initial_map_topology = response.duplicate(true)
	_initial_topology_failed = false
	_try_finalize_initial_map_bootstrap()


func _try_finalize_initial_map_bootstrap() -> void:
	if _initial_map_bootstrapped or map_area == null:
		return
	if _pending_initial_map_topology.is_empty():
		if not _initial_topology_failed:
			return
	elif map_area.has_method("set_region_topology"):
		map_area.set_region_topology(_pending_initial_map_topology)
	if not _pending_initial_map_data.is_empty():
		map_area.update_all_regions(_pending_initial_map_data)
	_pending_initial_map_data.clear()
	_pending_initial_map_topology.clear()
	map_area.visible = true
	_initial_map_bootstrapped = true


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
			# Close diplomacy wizard first (Fix 11)
			if diplomacy_wizard and diplomacy_wizard.visible:
				diplomacy_wizard._close_wizard()
				get_viewport().set_input_as_handled()
				return
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
	if resize_grip:
		resize_grip.visible = false

func _restore_terminal():
	"""Expand the terminal panel, hide restore button."""
	bottom_left_ui.visible = true
	restore_button.visible = false
	if resize_grip:
		resize_grip.visible = true
		_reposition_after_layout()
	command_input.grab_focus()

# ═══════════════════════════════════════════════════════════════════════════
# UI-2: Expandable command window + terminal text scale (DEF-13 fold)
# ═══════════════════════════════════════════════════════════════════════════

func _setup_scalable_terminal() -> void:
	"""Wire the A− / A+ text scale + the corner resize grip and restore the
	saved footprint/scale. Called once from _ready() after the global UI scale
	has been applied."""
	_collect_scalable_fonts()

	if scale_down_button and not scale_down_button.pressed.is_connected(_on_scale_down_pressed):
		scale_down_button.pressed.connect(_on_scale_down_pressed)
	if scale_up_button and not scale_up_button.pressed.is_connected(_on_scale_up_pressed):
		scale_up_button.pressed.connect(_on_scale_up_pressed)

	_create_resize_grip()

	# Restore persisted preferences.
	_apply_terminal_scale(UiSettings.get_terminal_scale())
	_apply_terminal_size(UiSettings.get_terminal_width(), UiSettings.get_terminal_height())

func _collect_scalable_fonts() -> void:
	"""Snapshot every authored font-size override inside the terminal so the
	scale multiplies the .tscn base sizes (auto-adapts if the layout changes;
	no per-node enumeration to drift). Includes the out-of-panel RestoreButton."""
	_scalable_fonts.clear()
	_gather_fonts(bottom_left_ui)
	_gather_fonts(restore_button)

func _gather_fonts(node: Node) -> void:
	if node is Control:
		for key in ["font_size", "normal_font_size", "bold_font_size"]:
			if node.has_theme_font_size_override(key):
				_scalable_fonts.append({
					"node": node,
					"key": key,
					"base": node.get_theme_font_size(key),
				})
	for child in node.get_children():
		_gather_fonts(child)

func _apply_terminal_scale(scale: float) -> void:
	_terminal_scale = clampf(scale, UiSettings.MIN_TERMINAL_SCALE, UiSettings.MAX_TERMINAL_SCALE)
	for f in _scalable_fonts:
		var n = f.get("node")
		if is_instance_valid(n):
			n.add_theme_font_size_override(f.key, int(round(float(f.base) * _terminal_scale)))
	# Larger text may need a taller panel to keep the input row visible.
	_reposition_after_layout()

func _on_scale_down_pressed() -> void:
	_apply_terminal_scale(_terminal_scale - UiSettings.TERMINAL_SCALE_STEP)
	UiSettings.set_terminal_scale(_terminal_scale)

func _on_scale_up_pressed() -> void:
	_apply_terminal_scale(_terminal_scale + UiSettings.TERMINAL_SCALE_STEP)
	UiSettings.set_terminal_scale(_terminal_scale)

func _create_resize_grip() -> void:
	if resize_grip and is_instance_valid(resize_grip):
		return
	resize_grip = Panel.new()
	resize_grip.name = "TerminalResizeGrip"
	resize_grip.custom_minimum_size = Vector2(GRIP_SIZE, GRIP_SIZE)
	resize_grip.size = Vector2(GRIP_SIZE, GRIP_SIZE)
	resize_grip.mouse_filter = Control.MOUSE_FILTER_STOP
	resize_grip.mouse_default_cursor_shape = Control.CURSOR_BDIAGSIZE
	resize_grip.tooltip_text = "Drag to resize the command window · double-click to reset"
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.08, 0.1, 0.15, 0.92)
	sb.border_color = Color(0.85, 0.75, 0.55, 1)  # gold, matches the terminal accent
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(3)
	resize_grip.add_theme_stylebox_override("panel", sb)
	var glyph := Label.new()
	glyph.text = "⤢"
	glyph.mouse_filter = Control.MOUSE_FILTER_IGNORE
	glyph.set_anchors_preset(Control.PRESET_FULL_RECT)
	glyph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	glyph.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	glyph.add_theme_color_override("font_color", Color(0.85, 0.75, 0.55, 1))
	glyph.add_theme_font_size_override("font_size", 12)
	resize_grip.add_child(glyph)
	add_child(resize_grip)
	resize_grip.gui_input.connect(_on_grip_gui_input)
	_position_resize_grip()

func _apply_terminal_size(width: float, height: float) -> void:
	"""Set the DESIRED terminal footprint (the user's intent) and lay it out.
	The desired size is clamped only to the absolute min/max — never to the
	window — so a transient viewport shrink (a window resize or a raised global
	scale) can't permanently shrink it. The window fit happens in
	_relayout_terminal, for DISPLAY only, and is never written back over intent."""
	_terminal_width = clampf(width, UiSettings.MIN_TERMINAL_WIDTH, UiSettings.MAX_TERMINAL_WIDTH)
	_terminal_height = clampf(height, UiSettings.MIN_TERMINAL_HEIGHT, UiSettings.MAX_TERMINAL_HEIGHT)
	_relayout_terminal()

func _relayout_terminal() -> void:
	"""Fit the DESIRED size to the current viewport for display only. Anchored
	bottom-left: the fixed corner stays, width extends offset_right, height
	extends offset_top (negative = upward). Growing the window back restores the
	intended footprint because _terminal_width/height are left untouched here."""
	var disp_w = clampf(_terminal_width, UiSettings.MIN_TERMINAL_WIDTH,
			maxf(UiSettings.MIN_TERMINAL_WIDTH, size.x - TERMINAL_ANCHOR_LEFT * 2.0))
	var disp_h = clampf(_terminal_height, UiSettings.MIN_TERMINAL_HEIGHT,
			maxf(UiSettings.MIN_TERMINAL_HEIGHT, size.y - 20.0))
	bottom_left_ui.offset_left = TERMINAL_ANCHOR_LEFT
	bottom_left_ui.offset_bottom = TERMINAL_ANCHOR_BOTTOM
	bottom_left_ui.offset_right = TERMINAL_ANCHOR_LEFT + disp_w
	bottom_left_ui.offset_top = TERMINAL_ANCHOR_BOTTOM - disp_h
	_reposition_after_layout()

func _position_resize_grip() -> void:
	if resize_grip == null or not is_instance_valid(resize_grip):
		return
	if not bottom_left_ui.visible:
		return
	# Read the ACTUAL rendered rect: BottomLeftUI is a PanelContainer, so it
	# clamps up to its combined minimum size (header + output + input row), and
	# A+ text scale enlarges that min — the grip must follow the real top-right
	# corner, not the requested footprint, or it strands mid-panel.
	var rect: Rect2 = bottom_left_ui.get_global_rect()
	var corner := Vector2(rect.position.x + rect.size.x, rect.position.y)
	resize_grip.position = corner - resize_grip.size * 0.5

func _reposition_after_layout() -> void:
	# Font/scale changes can reflow container min-sizes a frame later.
	call_deferred("_position_resize_grip")

func _on_grip_gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			if event.double_click:
				_reset_terminal_size()
			else:
				_grip_dragging = true
		else:
			if _grip_dragging:
				_grip_dragging = false
				UiSettings.set_terminal_size(_terminal_width, _terminal_height)
	elif event is InputEventMouseMotion and _grip_dragging:
		_resize_terminal_from_mouse(get_global_mouse_position())

func _resize_terminal_from_mouse(mouse_pos: Vector2) -> void:
	# The panel's fixed corner is bottom-left; the grip drags the top-right one.
	var new_width = mouse_pos.x - TERMINAL_ANCHOR_LEFT
	var bottom_y = size.y + TERMINAL_ANCHOR_BOTTOM
	var new_height = bottom_y - mouse_pos.y
	_apply_terminal_size(new_width, new_height)

func _reset_terminal_size() -> void:
	_apply_terminal_size(UiSettings.DEFAULT_TERMINAL_WIDTH, UiSettings.DEFAULT_TERMINAL_HEIGHT)
	UiSettings.set_terminal_size(_terminal_width, _terminal_height)

func _on_root_resized() -> void:
	# Window / global-scale reflow: re-fit the UNCHANGED desired size to the new
	# viewport (display-only) and re-glue the grip. Must NOT go through
	# _apply_terminal_size, which would re-clamp the intent.
	_relayout_terminal()

func _apply_ui_scale(scale: float, persist: bool = true) -> void:
	"""Global interface scale via content_scale_factor (UI-2 / DEF-13 fold).
	The map SubViewport is recompensated to stay crisp."""
	var clamped = clampf(scale, UiSettings.MIN_UI_SCALE, UiSettings.MAX_UI_SCALE)
	var win = get_window()
	if win:
		win.content_scale_factor = clamped
	if map_area and map_area.has_method("refresh_viewport_scale"):
		map_area.refresh_viewport_scale()
	if persist:
		UiSettings.set_ui_scale(clamped)
	# Logical viewport size just changed — re-glue the terminal + grip.
	call_deferred("_on_root_resized")

func _on_ui_scale_changed(scale: float, persist: bool = true) -> void:
	# Applied live for preview on every slider step; persisted only when the drag
	# ends (or immediately for a click / keyboard change) so a drag doesn't spam
	# the config file to disk each step.
	_apply_ui_scale(scale, persist)

func _toggle_terminal():
	"""Toggle terminal panel visibility."""
	if bottom_left_ui.visible:
		_minimize_terminal()
	else:
		_restore_terminal()

func _execute_end_turn():
	"""Execute end turn command with client-side lapse confirmation gate."""
	if _awaiting_end_turn_confirmation:
		_awaiting_end_turn_confirmation = false
		_send_end_turn()
		return

	# Client-side confirmation gate — spec §5
	if _current_envoy_count > 0:
		_show_lapse_confirmation()
		return

	_awaiting_end_turn_confirmation = false
	_set_open_envoys_prompt_visible(false)
	_send_end_turn()

func _send_end_turn():
	"""Actually send end turn command to backend."""
	_set_open_envoys_prompt_visible(false)
	# Add to history
	_add_to_history("end turn")

	# Display the command
	add_output("")
	add_output("[color=#" + Utils.COLOR_COMMAND + "]► end turn[/color]")

	# Disable input while processing
	set_input_enabled(false)

	# Send to backend
	api_client.send_command("end turn", _on_command_result)

func _show_lapse_confirmation():
	"""Show confirmation before ending turn with pending envoys."""
	var msg = "You have %d unanswered envoy(s) that will lapse if you end the turn now." % _current_envoy_count
	add_output("")
	add_output("[color=#e0c060]⚠ %s[/color]" % msg)
	add_output("[color=#d9c08c]  Click [b]Open Envoys[/b] to review now, or press [b]End Turn[/b] again, [b]Enter[/b], or type [b]end turn[/b] again to confirm the lapse.[/color]")
	_awaiting_end_turn_confirmation = true
	_set_open_envoys_prompt_visible(true)
	end_turn_button.grab_focus()

func _execute_command():
	"""Execute the command in the input field."""
	var command = command_input.text.strip_edges()

	if command.is_empty():
		if _awaiting_end_turn_confirmation:
			_awaiting_end_turn_confirmation = false
			command_input.text = ""
			_send_end_turn()
		return

	_awaiting_end_turn_confirmation = false
	_set_open_envoys_prompt_visible(false)

	# Route typed "end turn" through the same confirmation gate as button/hotkey.
	if command.to_lower() == "end turn":
		command_input.text = ""
		_execute_end_turn()
		return

	# Add to history before clearing
	_add_to_history(command)

	# Display player command with prompt styling
	add_output("")
	add_output("[color=#" + Utils.COLOR_COMMAND + "]► " + command + "[/color]")

	# Clear input
	command_input.text = ""

	# ════════════════════════════════════════════════════════════
	# CHECK FOR REDEMPTION COMMAND: Handle redemption choices
	# ════════════════════════════════════════════════════════════
	var redemption_choices = ["grant_autonomy", "dismiss", "demand_obedience"]
	if command.to_lower() in redemption_choices:
		if DEBUG_VERBOSE:
			print("REDEMPTION COMMAND DETECTED: ", command)
		set_input_enabled(false)
		api_client.send_redemption_response(command.to_lower(), _on_redemption_response)
		return

	# Disable input while processing
	set_input_enabled(false)

	# Send to backend
	api_client.send_command(command, _on_command_result)

func _configure_response_routes():
	"""Centralize modal response ordering for _on_command_result()."""
	# Order in these arrays is the precedence contract.
	_pre_hud_response_routes = [
		{"id": "objection", "matches": "_response_has_objection_route", "show": "_route_objection_response"},
		{"id": "glorious_charge", "matches": "_response_has_glorious_charge_route", "show": "_route_glorious_charge_response"},
	]
	_post_hud_response_routes = [
		{"id": "commitment_paradox", "matches": "_response_has_commitment_paradox_route", "show": "_route_commitment_paradox_response"},
		{"id": "capture_choice", "matches": "_response_has_capture_choice_route", "show": "_route_capture_choice_response"},
		{"id": "marshal_petition", "matches": "_response_has_marshal_petition_route", "show": "_route_marshal_petition_response"},
		{"id": "diplomatic_objection", "matches": "_response_has_diplomatic_objection_route", "show": "_route_diplomatic_objection_response"},
		{"id": "incoming_proposal", "matches": "_response_has_incoming_proposal_route", "show": "_route_incoming_proposal_response"},
		{"id": "incoming_settlement_offer", "matches": "_response_has_incoming_settlement_offer_route", "show": "_route_incoming_settlement_offer_response"},
		{"id": "proposal_confirm", "matches": "_response_has_proposal_confirm_route", "show": "_route_proposal_confirm_response"},
		{"id": "clarification", "matches": "_response_has_clarification_route", "show": "_route_clarification_response"},
		{"id": "interrupt", "matches": "_response_has_interrupt_route", "show": "_route_interrupt_response"},
		{"id": "diplomatic_sabotage", "matches": "_response_has_sabotage_route", "show": "_route_sabotage_response"},
		{"id": "vassal_rebellion", "matches": "_response_has_vassal_rebellion_route", "show": "_route_vassal_rebellion_response"},
		{"id": "redemption_event", "matches": "_response_has_redemption_route", "show": "_route_redemption_response"},
	]

func _route_response_ui(response: Dictionary, routes: Array) -> bool:
	"""Run the first matching response route and keep the precedence policy data-driven."""
	for route in routes:
		var matches_method = str(route.get("matches", ""))
		if matches_method == "" or not call(matches_method, response):
			continue
		var show_method = str(route.get("show", ""))
		if show_method == "":
			continue
		if DEBUG_VERBOSE:
			print("RESPONSE ROUTE MATCHED: ", route.get("id", "unknown"))
		call(show_method, response)
		_process_active_wars(response)
		return true
	return false

func _response_has_objection_route(response: Dictionary) -> bool:
	var is_tactical_objection = response.get("success", false) and response.has("state") and response.state == "awaiting_player_choice"
	var is_strategic_objection = response.get("success", false) and response.has("pending_objection") and response.pending_objection == true
	if DEBUG_VERBOSE:
		print("4. IS_OBJECTION CHECK: tactical=", is_tactical_objection, " strategic=", is_strategic_objection, " => ", is_tactical_objection or is_strategic_objection)
	return is_tactical_objection or is_strategic_objection

func _route_objection_response(response: Dictionary):
	if DEBUG_VERBOSE:
		print("5. OBJECTION DETECTED - About to show dialog")
	_show_objection_dialog(response)

func _response_has_glorious_charge_route(response: Dictionary) -> bool:
	return response.has("pending_glorious_charge") and response.pending_glorious_charge

func _route_glorious_charge_response(response: Dictionary):
	if DEBUG_VERBOSE:
		print("GLORIOUS CHARGE CONDITION MET")
	_show_glorious_charge_dialog(response)

func _response_has_commitment_paradox_route(response: Dictionary) -> bool:
	return (
		response.has("commitment_paradox_popup")
		and response.commitment_paradox_popup != null
		and commitment_paradox_popup != null
	)

func _route_commitment_paradox_response(response: Dictionary):
	commitment_paradox_popup.show_paradox(response.commitment_paradox_popup)

func _response_has_capture_choice_route(response: Dictionary) -> bool:
	return response.has("pending_capture_choice") and response.pending_capture_choice

func _route_capture_choice_response(response: Dictionary):
	_show_capture_choice_dialog(response)

func _response_has_marshal_petition_route(response: Dictionary) -> bool:
	# Jealousy v3.2: the PopupQueue delivers the petition under
	# `marshal_petition`; ESP-2 also attaches it directly to the
	# declare-war command result.
	return (
		response.has("marshal_petition")
		and response.marshal_petition != null
		and marshal_petition_dialog != null
	)

func _route_marshal_petition_response(response: Dictionary):
	marshal_petition_dialog.show_petition(response.marshal_petition)

func _response_has_diplomatic_objection_route(response: Dictionary) -> bool:
	return (
		response.has("diplomatic_objection")
		and response.diplomatic_objection != null
		and talleyrand_objection_popup != null
	)

func _route_diplomatic_objection_response(response: Dictionary):
	talleyrand_objection_popup.show_objection(response.diplomatic_objection)

func _response_has_incoming_proposal_route(response: Dictionary) -> bool:
	if not response.has("incoming_proposal") or response.incoming_proposal == null or incoming_proposal_popup == null:
		return false
	var proposal_nation = response.incoming_proposal.get("from_nation", "")
	return proposal_nation != _dismissed_proposal_nation

func _route_incoming_proposal_response(response: Dictionary):
	incoming_proposal_popup.show_proposal(response.incoming_proposal)

func _response_has_incoming_settlement_offer_route(response: Dictionary) -> bool:
	# SC-5 reversal commit 2 (Slice G1): match either the dedicated
	# `incoming_settlement_offer` popup-queue key or a dialogue dict
	# whose type is `incoming_settlement_offer`. The proposal_confirm
	# route handles the popup body once we deliver it here.
	if response.has("incoming_settlement_offer") and response.incoming_settlement_offer != null:
		return proposal_confirm_popup != null
	var dialogue = response.get("diplomatic_dialogue", {})
	if typeof(dialogue) == TYPE_DICTIONARY and dialogue.get("type", dialogue.get("dialogue_type", "")) == "incoming_settlement_offer":
		return proposal_confirm_popup != null
	return false

func _route_incoming_settlement_offer_response(response: Dictionary):
	var dialogue = response.get("incoming_settlement_offer", {})
	if typeof(dialogue) != TYPE_DICTIONARY or dialogue.is_empty():
		dialogue = response.get("diplomatic_dialogue", {})
	if proposal_confirm_popup != null and dialogue is Dictionary and dialogue.size() > 0:
		set_input_enabled(false)
		proposal_confirm_popup.show_dialogue(dialogue)

func _response_has_proposal_confirm_route(response: Dictionary) -> bool:
	return response.has("diplomatic_dialogue") and response.diplomatic_dialogue != null and proposal_confirm_popup != null

func _route_proposal_confirm_response(response: Dictionary):
	var dialogue = response.diplomatic_dialogue
	var dtype = dialogue.get("type", "")
	if dtype not in PROPOSAL_CONFIRM_DIALOGUE_TYPES:
		push_warning("Unknown diplomatic_dialogue dtype: '%s' - showing as popup (add to PROPOSAL_CONFIRM_DIALOGUE_TYPES)" % dtype)
	# PF-1 (D3): a failed settlement action (blocked dial, coverage edit,
	# Submit, Ratify) re-attaches the unchanged dialogue so the popup
	# re-mounts. Carry the failure reason onto that re-mount — otherwise the
	# popup repaints identical state and the click reads as a silent no-op.
	if not bool(response.get("success", true)):
		var err_text = str(response.get("error_display", response.get("message", "")))
		if err_text != "":
			dialogue = dialogue.duplicate(true)
			dialogue["transient_error_display"] = err_text
	proposal_confirm_popup.show_dialogue(dialogue)

func _show_confirm_dialogue_from_response(response: Dictionary, missing_message: String):
	# SC-5 reversal commit 2 (Slice G1): the incoming-offer payload is
	# delivered via the dedicated `incoming_settlement_offer` response
	# key + popup route, not as a generic `diplomatic_dialogue`
	# fallback. This helper only inflates explicit
	# `diplomatic_dialogue` payloads.
	var dialogue = response.get("diplomatic_dialogue", {})
	if proposal_confirm_popup and dialogue is Dictionary and dialogue.size() > 0:
		set_input_enabled(false)
		proposal_confirm_popup.show_dialogue(dialogue)
	else:
		add_output("[color=#d9c08c]" + missing_message + "[/color]")

func _response_has_clarification_route(response: Dictionary) -> bool:
	return response.has("state") and response.state == "awaiting_clarification"

func _route_clarification_response(response: Dictionary):
	_show_clarification_popup(response)

func _response_has_interrupt_route(response: Dictionary) -> bool:
	return response.has("pending_interrupt") and response.pending_interrupt

func _route_interrupt_response(response: Dictionary):
	_show_interrupt_popup(response.pending_interrupt)

func _response_has_sabotage_route(response: Dictionary) -> bool:
	return (
		response.has("diplomatic_sabotage")
		and response.diplomatic_sabotage != null
		and sabotage_discovery_popup != null
	)

func _route_sabotage_response(response: Dictionary):
	sabotage_discovery_popup.show_sabotage(response.diplomatic_sabotage)

func _response_has_vassal_rebellion_route(response: Dictionary) -> bool:
	return (
		response.has("vassal_rebellion_imminent")
		and response.vassal_rebellion_imminent != null
		and vassal_rebellion_popup != null
	)

func _route_vassal_rebellion_response(response: Dictionary):
	vassal_rebellion_popup.show_rebellion(response.vassal_rebellion_imminent)

func _response_has_redemption_route(response: Dictionary) -> bool:
	return response.has("redemption_event") and response.redemption_event != null and not response.has("enemy_phase")

func _route_redemption_response(response: Dictionary):
	if response.success:
		_display_result(response)
	_show_redemption_dialog(response.redemption_event)

func _on_command_result(response):
	"""Handle command execution result."""
	# ═══════════════════════════════════════════════════════════
	# DEBUG TRACE: Exact step-by-step debugging
	# ═══════════════════════════════════════════════════════════
	if DEBUG_VERBOSE:
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

	# Cache response for post-popup war panel refresh (Fix 1)
	_last_command_response = response

	# GT-Slice-4: the settlement editor error-remount hooks are retired. A
	# failed settlement action re-attaches the dialogue + error_display
	# (CH-5), so the proposal_confirm route below re-mounts the PROPOSE /
	# REVIEW popup with the failure rendered (transient_error_display).
	if _route_response_ui(response, _pre_hud_response_routes):
		return  # Don't re-enable input or continue processing

	_sync_response_hud(response)
	if response.has("settlement_draft_notices") and response.settlement_draft_notices is Array:
		for notice in response.settlement_draft_notices:
			if notice is Dictionary:
				var notice_text = str(notice.get("message_display", "Settlement draft discarded at turn end."))
				add_output("[color=#" + Utils.COLOR_INFO + "]" + notice_text + "[/color]")

	# Priority 3: Coalition Declaration Popup (Session 8C)
	# Informational-only coalition declarations now route through the notice rail.

	# Check for capture choice (Phase 6.2.E: Plunder or Secure)
	# Check for load dialog request (Phase 6: Save/Load)
	if response.has("show_load_dialog") and response.show_load_dialog:
		_show_load_dialog()
		# Don't return - still show the save list message in terminal

	# Priority 6.25: Proposal Result Popup (PL-5A - proposal outcome)
	# Informational-only proposal results now route through the notice rail.

	if _route_response_ui(response, _post_hud_response_routes):
		return  # Don't re-enable input until choice made

	# Re-enable input
	set_input_enabled(true)

	# Settlement reopen signal: backend asks the UI to re-open the settlement
	# review (e.g. after a stale active_pair_changed / proposer_leader_changed,
	# after Revise Terms, or after accepting an incoming offer with no war_id).
	# Acted on regardless of success because the helper paths return success=False
	# but still hand back a reopen_target.
	if bool(response.get("must_reopen", false)):
		var reopen_target = response.get("reopen_target", {})
		if typeof(reopen_target) == TYPE_DICTIONARY:
			var rt_war_id = str(reopen_target.get("war_id", ""))
			var rt_nation = str(reopen_target.get("target_nation", reopen_target.get("nation", "")))
			if rt_war_id != "" and rt_nation != "":
				add_output("[color=#" + Utils.COLOR_INFO + "]Reopening settlement review for " + rt_nation + "…[/color]")
				_on_war_settlement_clicked(rt_war_id, rt_nation)
				return
		add_output("[color=#e04040]Settlement review needs to reopen, but the backend did not provide a valid target.[/color]")
		set_input_enabled(true)
		command_input.grab_focus()
		return

	if response.has("recovery_route") and response.recovery_route is Dictionary:
		# SC-29 / G2-Slice-7 pair-scoped substitute CTAs return a
		# recovery_route with surface=proposal_confirm together with a
		# fresh diplomatic_dialogue. _route_settlement_recovery_route
		# only knows war_detail and settlement_history; if we return
		# early for proposal_confirm the new proposal popup never opens
		# and the player is left with no clickable target. Restrict the
		# early-return to surfaces the helper actually handles, and let
		# proposal_confirm fall through to the normal diplomatic_dialogue
		# route below.
		var rr_surface = str(response.recovery_route.get("surface", response.recovery_route.get("target", "")))
		if rr_surface in ["war_detail", "settlement_history"]:
			_process_active_wars(response)
			_route_settlement_recovery_route(response.recovery_route)
			return

	if response.success:
		# Format and display result based on event type
		_display_result(response)

		# Display tactical events (supply attrition, occupation updates)
		if response.has("tactical_events"):
			var events = response.tactical_events
			if events is Array:
				for event in events:
					var msg = str(event.get("message", ""))
					if msg != "":
						add_output("[color=#" + Utils.COLOR_INFO + "]" + msg + "[/color]")

		# Check for enemy phase (from end_turn)
		# NOTE: No total_actions > 0 gate — dialog shows even with 0 enemy actions
		# (e.g. debug freeze_enemies). The dialog handles 0-action case with
		# "No enemy actions this turn." message.
		if response.has("enemy_phase"):
			if DEBUG_VERBOSE:
				print("ENEMY PHASE DETECTED - showing dialog")
			# Close screens before showing modal (avoid stale screen behind dialog)
			if top_bar:
				top_bar.close_all_screens()
			set_input_enabled(false)  # Disable input until dismissed
			# Use turn_ended (the turn enemy actually acted on) not action_summary.turn
			# (which is already incremented by advance_turn)
			var turn = current_turn
			if response.has("turn_ended") and response.turn_ended != null:
				turn = int(response.turn_ended)
			elif response.has("action_summary"):
				turn = int(response.action_summary.get("turn", current_turn))
			pending_enemy_phase_response = response  # Store for post-enemy-phase flow
			_show_enemy_phase_dialog(response.enemy_phase, turn)
			_update_war_panel_visibility()
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
		add_output("[color=#" + Utils.COLOR_ERROR + "]" + str(response.get("message", "An error occurred")) + "[/color]")

	# N4i: Update war status HUD on every response
	_process_active_wars(response)

	add_output("")

	# Auto-focus input
	command_input.grab_focus()

func _display_result(response):
	"""Display result with appropriate formatting based on event type."""
	var message = str(response.get("message", ""))
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
				add_output("[color=#" + Utils.COLOR_INFO + "]" + parts[0] + "[/color]")
				add_output("")
				message = parts[1]  # Rest of message

	# Color based on event type
	match event_type:
		"battle":
			_display_battle_result(message, events[0], action_info)
		"bombardment":
			add_output("[color=#" + Utils.COLOR_BATTLE + "]" + message + "[/color]")
			_show_action_cost(action_info)
		"conquest":
			add_output("[color=#" + Utils.COLOR_CONQUEST + "]⚑ " + message + "[/color]")
			_show_action_cost(action_info)
		"move":
			add_output("[color=#" + Utils.COLOR_SUCCESS + "]→ " + message + "[/color]")
			_show_action_cost(action_info)
		"scout":
			add_output("[color=#" + Utils.COLOR_INFO + "]👁 " + message + "[/color]")
			_show_action_cost(action_info)
		"recruit":
			add_output("[color=#" + Utils.COLOR_SUCCESS + "]+ " + message + "[/color]")
			_show_action_cost(action_info)
		"defend":
			add_output("[color=#" + Utils.COLOR_SUCCESS + "]⛨ " + message + "[/color]")
			_show_action_cost(action_info)
		"turn_end":
			_display_turn_change(events[0])
			# Morning Dispatch — stored for display after all dialogs (enemy phase, strategic reports)
			if response.has("morning_dispatch"):
				pending_dispatch_data = response.morning_dispatch
		_:
			add_output("[color=#" + Utils.COLOR_SUCCESS + "]" + message + "[/color]")
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
	# First-hour opener guidance (PL-26) reuses the same inline report surface.
	if response.has("opening_attack_guidance"):
		_display_coordination_tutorial(response.opening_attack_guidance)

	if response.has("bombardment_result"):
		_display_bombardment_report(response.bombardment_result)

	# Peace Deals BPH-D: immediate ratification outcome summary
	if response.has("peace_ratification_summary") and response.peace_ratification_summary is Dictionary:
		_display_peace_ratification_summary(response.peace_ratification_summary)

	# Common Peace: compact result feedback after the confirm popup resolves.
	if response.has("settlement_result_feedback") and response.settlement_result_feedback is Dictionary:
		_display_settlement_result_feedback(response.settlement_result_feedback)

	# Berthier's Bombardment Advisory - shown when artillery crumbles enemy forts
	var bombardment_advisory = response.get("bombardment_advisory", "")
	if bombardment_advisory != "" and bombardment_advisory != null:
		add_output("[color=#" + Utils.COLOR_DISPATCH + "]  Berthier: \"" + str(bombardment_advisory) + "\"[/color]")
	
	# Check for turn advancement
	if action_info.get("turn_advanced", false):
		_display_turn_advance(action_info)

	# Display AI feedback if present (LLM mode only)
	if response.has("feedback"):
		_display_feedback(response.feedback)

func _display_peace_ratification_summary(summary: Dictionary):
	var target = str(summary.get("target_nation", "Unknown"))
	var capital = str(summary.get("target_capital", target))
	var outcome = _peace_outcome_label(str(summary.get("war_outcome", "")))
	var duration = int(summary.get("war_duration_turns", 0))
	var score = int(summary.get("final_war_score", 0))
	var score_sign = "+" if score > 0 else ""

	add_output("")
	add_output("[color=#" + Utils.COLOR_GOLD + "]PEACE SETTLEMENT: Treaty of " + capital + "[/color]")
	add_output("[color=#" + Utils.COLOR_INFO + "]  Outcome: " + outcome + " after " + str(duration) + " turns. Final war score: " + score_sign + str(score) + "[/color]")

	var gained = _stringify_list(summary.get("territory_gained", []))
	var lost = _stringify_list(summary.get("territory_lost", []))
	if gained.size() > 0:
		add_output("[color=#" + Utils.COLOR_SUCCESS + "]  Gained: " + ", ".join(gained) + "[/color]")
	if lost.size() > 0:
		add_output("[color=#" + Utils.COLOR_ERROR + "]  Lost: " + ", ".join(lost) + "[/color]")

	var gold_received = int(summary.get("gold_received", 0))
	var gold_paid = int(summary.get("gold_paid", 0))
	if gold_received > 0 or gold_paid > 0:
		var gold_parts = PackedStringArray()
		if gold_received > 0:
			gold_parts.append("+" + str(gold_received) + " gold")
		if gold_paid > 0:
			gold_parts.append("-" + str(gold_paid) + " gold")
		add_output("[color=#" + Utils.COLOR_GOLD + "]  Treasury: " + ", ".join(gold_parts) + "[/color]")

	var casualties_france = int(summary.get("casualties_france", 0))
	var casualties_enemy = int(summary.get("casualties_enemy", 0))
	if casualties_france > 0 or casualties_enemy > 0:
		add_output("[color=#" + Utils.COLOR_INFO + "]  Casualties: France " + _format_number(casualties_france) + " / " + target + " " + _format_number(casualties_enemy) + "[/color]")

	var terms = _stringify_list(summary.get("terms_ratified", []))
	if terms.size() > 0:
		add_output("[color=#" + Utils.COLOR_INFO + "]  Terms: " + "; ".join(terms) + "[/color]")

	var aftermath = _stringify_list(summary.get("political_aftermath", []))
	if aftermath.size() > 0:
		add_output("[color=#" + Utils.COLOR_BATTLE + "]  Aftermath: " + "; ".join(aftermath) + "[/color]")

func _display_settlement_result_feedback(feedback: Dictionary):
	var title = str(feedback.get("title", "Settlement Ratified"))
	var message = str(feedback.get("message", ""))
	var war_label = str(feedback.get("war_label", ""))
	var resolved = int(feedback.get("resolved_pair_count", 0))
	add_output("[color=#" + Utils.COLOR_SUCCESS + "]" + title + "[/color]")
	if message != "":
		add_output("[color=#" + Utils.COLOR_INFO + "]  " + message + "[/color]")
	elif war_label != "":
		add_output("[color=#" + Utils.COLOR_INFO + "]  " + war_label + " updated.[/color]")
	if resolved > 0:
		add_output("[color=#" + Utils.COLOR_INFO + "]  Covered pairings: " + str(resolved) + "[/color]")
	var review_route = feedback.get("review_route", {})
	var route_id = str(feedback.get("route_id", ""))
	var war_id = str(feedback.get("war_id", ""))
	if typeof(review_route) == TYPE_DICTIONARY:
		route_id = str(review_route.get("route_id", route_id))
		war_id = str(review_route.get("war_id", war_id))
	if route_id != "" or war_id != "":
		add_output("[color=#" + Utils.COLOR_INFO + "]  Opening diplomatic ledger to settlement…[/color]")
		# Programmatic open of the ledger focused on this settlement so the
		# player does not have to manually press D after ratification.
		if top_bar and top_bar.has_method("open_diplomatic_ledger_review"):
			top_bar.open_diplomatic_ledger_review("ledger_settlements", route_id, war_id)

func _peace_outcome_label(outcome: String) -> String:
	match outcome:
		"french_victory":
			return "French victory"
		"enemy_victory":
			return "Enemy victory"
		"stalemate":
			return "Stalemate"
		"white_peace":
			return "White peace"
		_:
			return outcome.replace("_", " ").capitalize()

func _stringify_list(values) -> PackedStringArray:
	var result = PackedStringArray()
	if values is Array:
		for value in values:
			result.append(str(value))
	return result

func _display_battle_result(message: String, event: Dictionary, action_info: Dictionary):
	"""Display battle results with dramatic formatting."""
	var outcome = event.get("outcome", "")
	var victor = event.get("victor", "")
	var enemy_destroyed = event.get("enemy_destroyed", false)
	var region_conquered = event.get("region_conquered", false)

	# Battle header - use battle_name if available
	var battle_name = event.get("battle_name", "BATTLE")
	add_output("[color=#" + Utils.COLOR_BATTLE + "]⚔ " + battle_name + " ⚔[/color]")
	
	# Main result
	add_output("[color=#" + Utils.COLOR_BATTLE + "]" + message + "[/color]")

	# Cavalry terrain flavor (Phase 6.1: separate colored line for cavalry effectiveness)
	var cav_terrain_msg = event.get("cavalry_terrain_message", "")
	if cav_terrain_msg != "" and cav_terrain_msg != null:
		add_output("[color=#" + Utils.COLOR_DISPATCH + "]   🐴 " + cav_terrain_msg + "[/color]")

	# Special notifications
	if enemy_destroyed:
		add_output("[color=#" + Utils.COLOR_CONQUEST + "]   ★ Enemy army destroyed! ★[/color]")
	
	if region_conquered:
		var region_name = event.get("region_name", "territory")
		add_output("[color=#" + Utils.COLOR_CONQUEST + "]   ⚑ " + region_name + " captured! ⚑[/color]")
	
	_show_action_cost(action_info)

func _display_berthier_report(report: Dictionary):
	"""Display Berthier's After-Action Report with modifier breakdown and observation."""
	var COLOR_REPORT = "CCCCCC"     # Light gray for report lines

	add_output("[color=#" + Utils.COLOR_BERTHIER + "]--- Berthier's Report ---[/color]")

	# CR-5 rider (d) "words become the record": when this battle came from a
	# delegation the marshal INTERPRETED (not an order the player typed), quote
	# the player's verbatim words. Backend sets this only on delegation-inferred
	# battles against the delegation's own quarry (game_logic/combat.py).
	var deleg_attr = str(report.get("delegation_attribution", ""))
	if deleg_attr != "":
		add_output("[color=#" + Utils.COLOR_OBSERVATION + "]  " + deleg_attr + "[/color]")

	# ES-7 second pass (§0.6.8 item 4c): a decisive victory that raised the
	# winner's reward expectation says so in the after-action report.
	var exp_note = str(report.get("expectation_note", ""))
	if exp_note != "":
		add_output("[color=#" + Utils.COLOR_GOLD + "]  " + exp_note + "[/color]")

	# Jealousy v3.2 (spec §11): Berthier notes jealous conduct on the field.
	var jl_note = str(report.get("jealousy_note", ""))
	if jl_note != "":
		add_output("[color=#" + Utils.COLOR_OBSERVATION + "]  " + jl_note + "[/color]")

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
		add_output("[color=#" + Utils.COLOR_OBSERVATION + "]  Berthier: \"" + observation + "\"[/color]")

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
	var COLOR_CASUALTY = "a0a0a8"   # Info gray for stats
	var COLOR_ENEMY_CAS = "cd5c5c"  # Red for enemy casualties
	var COLOR_OWN_CAS = "8fbc8f"    # Muted green for own (low) casualties
	var COLOR_TERRAIN = "b0a890"    # Warm gray for terrain info
	var COLOR_FORT = "daa06d"       # Battle orange for fort degradation
	var COLOR_FRIENDLY = "cd6b6b"   # Muted red for friendly fire
	var COLOR_REMAINING = "a0a0a8"  # Info gray for remaining count

	add_output("[color=#" + Utils.COLOR_BERTHIER + "]--- Bombardment Report ---[/color]")

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
		var fort_old = int(result.get("fort_old", 0))
		var fort_new = int(result.get("fort_new", 0))
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
		add_output("[color=#" + Utils.COLOR_OBSERVATION + "]  Berthier: \"" + obs + "\"[/color]")

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
	add_output("[color=#" + Utils.COLOR_ERROR + "]┌─────── DEFIANCE ───────┐[/color]")

	# Main message (e.g. "Despite your insistence, Ney attacked instead!")
	if message != "":
		add_output("[color=#" + Utils.COLOR_MARSHAL + "]  " + message + "[/color]")

	# Outcome label with color coding
	var outcome_color = Utils.COLOR_INFO
	var outcome_label = ""
	match outcome:
		"right":
			outcome_color = Utils.COLOR_SUCCESS
			outcome_label = "VINDICATED — Marshal was right"
		"wrong":
			outcome_color = Utils.COLOR_ERROR
			outcome_label = "FAILURE — Marshal was wrong"
		"inconclusive":
			outcome_color = Utils.COLOR_INFO
			outcome_label = "INCONCLUSIVE — No clear result"
		"failed_roll":
			outcome_color = Utils.COLOR_DISPATCH
			outcome_label = "DISCIPLINE HELD — Marshal obeyed reluctantly"

	if outcome_label != "":
		add_output("[color=#" + outcome_color + "]  " + outcome_label + "[/color]")

	# Stat changes
	var stat_parts = []
	if trust_change != 0:
		var sign = "+" if trust_change > 0 else ""
		var tc_color = Utils.COLOR_SUCCESS if trust_change > 0 else Utils.COLOR_ERROR
		stat_parts.append("[color=#" + tc_color + "]Trust " + sign + str(trust_change) + "[/color]")
	if authority_change != 0:
		var sign = "+" if authority_change > 0 else ""
		var ac_color = Utils.COLOR_SUCCESS if authority_change > 0 else Utils.COLOR_ERROR
		stat_parts.append("[color=#" + ac_color + "]Authority " + sign + str(authority_change) + "[/color]")

	if stat_parts.size() > 0:
		add_output("  " + "  ".join(stat_parts))

	# Berthier's flavor text
	if berthier_text != "" and berthier_text != "null":
		add_output("[color=#" + Utils.COLOR_OBSERVATION + "]  Berthier: \"" + berthier_text + "\"[/color]")

	add_output("[color=#" + Utils.COLOR_ERROR + "]└────────────────────────┘[/color]")
	add_output("")

func _display_authority_event(authority_event: Dictionary):
	"""Display authority threshold event (e.g. 'Whispers of Weakness')."""
	var title = str(authority_event.get("title", "Authority Changed"))
	var message = str(authority_event.get("message", ""))
	var authority = int(authority_event.get("authority", 0))

	add_output("")
	add_output("[color=#" + Utils.COLOR_GOLD + "]┌─── AUTHORITY ───┐[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]  " + title + "[/color]")
	if message != "":
		add_output("[color=#" + Utils.COLOR_DISPATCH + "]  " + message + "[/color]")
	add_output("[color=#" + Utils.COLOR_INFO + "]  Authority: " + str(authority) + "[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]└─────────────────┘[/color]")
	add_output("")

func _display_turn_change(event: Dictionary):
	"""Display turn end notification with full financial summary.

	Backend sends: income, upkeep, spent, net, treasury in turn_end event.
	All values are int() wrapped by executor.py (Godot crashes on floats).
	"""
	# Close all information screens on turn transition (avoid stale data)
	if top_bar:
		top_bar.close_all_screens()

	# Clear deferred state — new turn starts fresh
	_dismissed_proposal_nation = ""

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
	# ES-2 (S6): occupation is a separate Net component — without it the
	# banner's Income/Upkeep lines would not visibly sum toward Net
	var occupation = int(event.get("occupation", 0))
	var occupation_str = ""
	if occupation > 0:
		occupation_str = " | Occupation: -" + str(int(occupation)) + "g"
	# ES-7 (S7): the estate redirect is a separate Net component too
	var dotation_skim = int(event.get("dotation_skim", 0))
	var dotation_str = ""
	if dotation_skim > 0:
		dotation_str = " | Dotations: -" + str(int(dotation_skim)) + "g"
	# ES-7 second pass (§0.6.8): the rente bill is a separate Net component
	var rente_cost = int(event.get("rente_cost", 0))
	var rente_str = ""
	if rente_cost > 0:
		rente_str = " | Rentes: -" + str(int(rente_cost)) + "g"

	add_output("")
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]         TURN " + str(int(new_turn)) + " BEGINS[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + Utils.COLOR_SUCCESS + "]Income: " + str(int(income)) + "g" + occupation_str + dotation_str + rente_str + " | Upkeep: " + str(int(upkeep)) + "g | Net: " + net_sign + str(int(net)) + "g" + spent_str + "[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]Treasury: " + _format_number(int(treasury)) + "g[/color]")

	# Bankruptcy warning
	var bankruptcy_turns = int(event.get("bankruptcy_turns", 0))
	if bankruptcy_turns > 0:
		if bankruptcy_turns >= 3:
			add_output("[color=#" + Utils.COLOR_ERROR + "]BANKRUPTCY: Troops are deserting! (" + str(bankruptcy_turns) + " turns in deficit)[/color]")
		elif bankruptcy_turns >= 2:
			add_output("[color=#" + Utils.COLOR_ERROR + "]WARNING: Treasury in deficit! Troops grow restless![/color]")
		else:
			add_output("[color=#" + Utils.COLOR_ERROR + "]WARNING: Treasury in deficit! Upkeep costs halved as mercy.[/color]")

	add_output("[color=#" + Utils.COLOR_SUCCESS + "]Actions refreshed: " + str(int(max_actions)) + "/" + str(int(max_actions)) + "[/color]")
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
	var peace_settlements = data.get("peace_settlements", [])
	var berthier_note = str(data.get("berthier_note", "Your orders, Sire."))

	# ═══ DISPATCH HEADER ═══
	add_output("[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]")
	add_output("[color=#" + Utils.COLOR_BERTHIER + "]  MORNING DISPATCH — Turn " + str(turn_num) + "[/color]")
	add_output("[color=#" + Utils.COLOR_INFO + "]  Chief of Staff Berthier reporting[/color]")
	add_output("[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]")
	add_output("")

	# ═══ W6-3 HEADLINE — the turn's top story, then up to 2 sub-beats ═══
	var headline = data.get("headline", {})
	if headline is Dictionary and headline.size() > 0:
		add_output("[color=#" + Utils.COLOR_WARNING + "]" + str(headline.get("text", "")) + "[/color]")
		var sub_beats = headline.get("sub_beats", [])
		if sub_beats is Array:
			for beat in sub_beats:
				add_output("[color=#" + Utils.COLOR_INFO + "]  • " + str(beat) + "[/color]")
		add_output("")

	# ═══ SITUATION ═══
	add_output("[color=#" + Utils.COLOR_BERTHIER + "]SITUATION[/color]")
	var player_regions = int(situation.get("player_regions", 0))
	var enemy_regions = int(situation.get("enemy_regions", 0))
	var treasury = int(situation.get("treasury", 0))
	var treasury_delta = int(situation.get("treasury_delta", 0))
	var bankrupt = situation.get("bankrupt", false)
	var strength_pct = int(situation.get("strength_ratio_pct", 0))

	# Treasury line
	var delta_sign = "+" if treasury_delta >= 0 else ""
	var delta_color = Utils.COLOR_SUCCESS if treasury_delta >= 0 else Utils.COLOR_ERROR
	add_output("[color=#" + Utils.COLOR_INFO + "]  France holds " + str(player_regions) + " regions. Treasury: " + _format_number(treasury) + "g [/color][color=#" + delta_color + "](" + delta_sign + str(treasury_delta) + ")[/color]")

	# Enemy regions + estimated strength
	if bankrupt:
		add_output("[color=#" + Utils.COLOR_ERROR + "]  BANKRUPT — Treasury exhausted. Troops desert.[/color]")
	else:
		add_output("[color=#" + Utils.COLOR_INFO + "]  Enemy nations hold " + str(enemy_regions) + " regions. Estimated enemy strength: " + str(strength_pct) + "% of French forces.[/color]")

	# Authority (V2b)
	var authority = int(situation.get("authority", 100))
	var authority_label = str(situation.get("authority_label", "Normal"))
	var auth_color = Utils.COLOR_INFO
	if authority >= 80:
		auth_color = Utils.COLOR_SUCCESS
	elif authority < 50:
		auth_color = Utils.COLOR_ERROR
	add_output("[color=#" + Utils.COLOR_INFO + "]  Your authority: [/color][color=#" + auth_color + "]" + str(authority) + " (" + authority_label + ")[/color]")
	add_output("")

	# ═══ MARSHAL STATUS ═══
	if marshals_list.size() > 0:
		add_output("[color=#" + Utils.COLOR_BERTHIER + "]MARSHAL STATUS[/color]")
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
			var line_color = Utils.COLOR_INFO
			if m_status == "broken":
				line_color = Utils.COLOR_ERROR
			elif m_status == "retreating":
				line_color = Utils.COLOR_ERROR
			elif m_status == "idle_restless":
				line_color = Utils.COLOR_BATTLE

			add_output("[color=#" + line_color + "]" + line + "[/color]")

			# W6-3 §5.2: danger flag line (fog-legal threat under the row)
			var m_danger = str(m.get("danger", ""))
			if m_danger != "":
				add_output("[color=#" + Utils.COLOR_WARNING + "]      ⚠ " + m_danger + "[/color]")
		add_output("")

	# ═══ INTELLIGENCE ═══
	add_output("[color=#" + Utils.COLOR_BERTHIER + "]INTELLIGENCE[/color]")
	if intel_list.size() == 0:
		add_output("[color=#" + Utils.COLOR_INFO + "]  No enemy forces in observation range.[/color]")
	else:
		for intel in intel_list:
			var i_name = str(intel.get("name", "?"))
			var i_loc = str(intel.get("location", "?"))
			var i_strength = str(intel.get("strength_display", "?"))
			var i_vis = str(intel.get("visibility", "unknown"))
			var i_turn = int(intel.get("intel_turn", 0))

			var vis_label = ""
			var vis_color = Utils.COLOR_INFO
			match i_vis:
				"full":
					vis_label = "[confirmed]"
					vis_color = Utils.COLOR_SUCCESS
				"partial":
					vis_label = "[partial]"
					vis_color = Utils.COLOR_INFO
				"stale":
					vis_label = "[stale - T" + str(i_turn) + "]"
					vis_color = Utils.COLOR_BATTLE
				"last_known":
					vis_label = "[last known - T" + str(i_turn) + "]"
					vis_color = Utils.COLOR_ERROR
				_:
					vis_label = ""

			var intel_line = "  " + i_name
			while intel_line.length() < 18:
				intel_line += " "
			intel_line += i_loc
			while intel_line.length() < 34:
				intel_line += " "
			intel_line += i_strength

			add_output("[color=#" + Utils.COLOR_INFO + "]" + intel_line + " [/color][color=#" + vis_color + "]" + vis_label + "[/color]")
	add_output("")

	# ═══ TURN EVENTS ═══
	var turn_events = data.get("turn_events", [])
	if turn_events.size() > 0:
		add_output("[color=#" + Utils.COLOR_BERTHIER + "]TURN EVENTS[/color]")
		for evt in turn_events:
			var evt_msg = str(evt.get("message", ""))
			var evt_sev = str(evt.get("severity", "info"))
			var evt_color = Utils.COLOR_INFO
			if evt_sev == "warning":
				evt_color = Utils.COLOR_ERROR
			elif evt_sev == "good":
				evt_color = Utils.COLOR_SUCCESS
			add_output("[color=#" + evt_color + "]  " + evt_msg + "[/color]")
		add_output("")

	# Peace Deals BPH-D: previous-turn ratification summaries
	if peace_settlements.size() > 0:
		add_output("[color=#" + Utils.COLOR_BERTHIER + "]PEACE SETTLEMENTS[/color]")
		for settlement in peace_settlements:
			# Renamed from `headline`: W6-1 added a dispatch-headline local at
			# the top of this function and GDScript forbids the shadow.
			var settlement_headline = str(settlement.get("headline", "Peace Settlement"))
			var detail = str(settlement.get("detail", ""))
			add_output("[color=#" + Utils.COLOR_GOLD + "]  " + settlement_headline + "[/color]")
			if detail != "":
				add_output("[color=#" + Utils.COLOR_INFO + "]    " + detail + "[/color]")
		add_output("")

	# LAPSED ENVOYS
	var lapsed_offers = data.get("lapsed_offers", [])
	if lapsed_offers.size() > 0:
		add_output("[color=#" + Utils.COLOR_BERTHIER + "]LAPSED ENVOYS[/color]")
		for lapse in lapsed_offers:
			var l_nation = str(lapse.get("nation", "?"))
			var l_ptype = str(lapse.get("proposal_type", "offer")).replace("_", " ").capitalize()
			add_output("[color=#" + Utils.COLOR_BATTLE + "]  " + l_nation + "'s " + l_ptype + " offer lapsed unanswered[/color]")
		add_output("")

	# ═══ ENVOYS AWAITING RESPONSE ═══
	var pending_envoys = data.get("pending_envoys", [])
	var pending_envoy_count = int(data.get("pending_envoy_count", pending_envoys.size()))
	if pending_envoys.size() > 0 and pending_envoy_count > 0:
		add_output("[color=#" + Utils.COLOR_BERTHIER + "]ENVOYS AWAITING RESPONSE[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]  Talleyrand: " + str(pending_envoy_count) + " envoy(s) await your reply this turn. Open [b]Envoys[/b] before ending the turn.[/color]")
		for i in range(min(pending_envoys.size(), 3)):
			var envoy = pending_envoys[i]
			var envoy_nation = str(envoy.get("nation", "?"))
			var envoy_type = str(envoy.get("proposal_type", "proposal")).capitalize()
			add_output("[color=#" + Utils.COLOR_INFO + "]    - " + envoy_nation + " — " + envoy_type + "[/color]")
		if pending_envoys.size() > 3:
			add_output("[color=#" + Utils.COLOR_INFO + "]    - ...and " + str(pending_envoys.size() - 3) + " more[/color]")
		add_output("[color=#" + Utils.COLOR_OBSERVATION + "]  Berthier: \"I have placed the diplomatic packet atop the morning dispatch, Sire.\"[/color]")
		add_output("")

	# ═══ TURN LIMIT WARNING ═══
	var turn_limit_warning = data.get("turn_limit_warning", null)
	if turn_limit_warning != null and turn_limit_warning is Dictionary:
		var tlw_msg = str(turn_limit_warning.get("message", ""))
		var tlw_sev = str(turn_limit_warning.get("severity", "warning"))
		if tlw_msg != "":
			var tlw_color = Utils.COLOR_ERROR if tlw_sev == "critical" else Utils.COLOR_BATTLE
			add_output("[color=#" + tlw_color + "]  " + tlw_msg + "[/color]")
			add_output("")

	# ═══ TALLEYRAND REPORT ═══
	# â•â•â• DEFEAT WARNING â•â•â•
	# Defeat warning
	var defeat_imminent_warning = data.get("defeat_imminent_warning", null)
	if defeat_imminent_warning != null and defeat_imminent_warning is Dictionary:
		var diw_msg = str(defeat_imminent_warning.get("message", ""))
		var diw_sev = str(defeat_imminent_warning.get("severity", "warning"))
		if diw_msg != "":
			add_output("[color=#" + Utils.COLOR_BERTHIER + "]DEFEAT WARNING[/color]")
			var diw_color = Utils.COLOR_ERROR if diw_sev == "critical" else Utils.COLOR_BATTLE
			add_output("[color=#" + diw_color + "]  " + diw_msg + "[/color]")
			add_output("")

	# â•â•â• TALLEYRAND REPORT â•â•â•
	# Talleyrand report
	var talleyrand_report = data.get("talleyrand_report", [])
	if talleyrand_report is Array and talleyrand_report.size() > 0:
		add_output("[color=#" + Utils.COLOR_BERTHIER + "]DIPLOMATIC STATUS[/color]")
		for tal_entry in talleyrand_report:
			var tal_msg = str(tal_entry.get("message", "")) if tal_entry is Dictionary else str(tal_entry)
			if tal_msg != "":
				add_output("[color=#" + Utils.COLOR_INFO + "]  " + tal_msg + "[/color]")
		add_output("")

	# ═══ COALITION STATUS ═══
	var coalition_status = data.get("coalition_status", null)
	if coalition_status != null and coalition_status is Dictionary:
		var threat_level = int(coalition_status.get("threat_level", 0))
		var tier = str(coalition_status.get("tier", ""))
		if threat_level > 0:
			add_output("[color=#" + Utils.COLOR_BERTHIER + "]COALITION THREAT[/color]")
			var tier_color = Utils.COLOR_ERROR if tier == "CRITICAL" or tier == "HIGH" else Utils.COLOR_BATTLE
			add_output("[color=#" + tier_color + "]  Threat: " + str(threat_level) + "/100 [" + tier + "][/color]")
			var brewing = coalition_status.get("brewing", null)
			if brewing != null and brewing is Dictionary:
				var brew_turns = int(brewing.get("turns_remaining", 0))
				add_output("[color=#" + Utils.COLOR_ERROR + "]  Coalition forming in " + str(brew_turns) + " turns![/color]")
			var active_coal = coalition_status.get("active_coalition", null)
			if active_coal != null and active_coal is Dictionary:
				var coal_name = str(active_coal.get("name", "Coalition"))
				var coal_leader = str(active_coal.get("leader", "?"))
				add_output("[color=#" + Utils.COLOR_ERROR + "]  ACTIVE: " + coal_name + " — Leader: " + coal_leader + "[/color]")
			add_output("")

	# ═══ BERTHIER'S NOTE ═══
	add_output("[color=#" + Utils.COLOR_OBSERVATION + "]  Berthier: \"" + berthier_note + "\"[/color]")
	add_output("[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]")
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
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]  Actions exhausted — Turn " + str(int(new_turn)) + " begins[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")

func _show_game_over_screen(game_state: Dictionary):
	"""Display dramatic game over screen with final statistics."""
	# Disable input permanently
	set_input_enabled(false)

	# Add spacing for dramatic effect
	add_output("")
	add_output("")

	# Dramatic separator
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")

	# Victory or defeat title
	var victory_status = game_state.get("victory", "defeat")
	if victory_status == "victory":
		add_output("[center][color=#" + Utils.COLOR_GOLD + "][b][font_size=28]⚜ VICTOIRE! ⚜[/font_size][/b][/color][/center]")
		add_output("")
		add_output("[center][color=#" + Utils.COLOR_SUCCESS + "]The Empire Triumphant![/color][/center]")
		add_output("")
		add_output("[color=#" + Utils.COLOR_INFO + "]Europe bends the knee before the French Eagle.[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]Your marshals have conquered all who opposed them.[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]History will remember this as the height of Imperial glory![/color]")
	else:
		add_output("[center][color=#" + Utils.COLOR_ERROR + "][b][font_size=28]⚔ DÉFAITE ⚔[/font_size][/b][/color][/center]")
		add_output("")
		add_output("[center][color=#" + Utils.COLOR_ERROR + "]The Empire Has Fallen[/color][/center]")
		add_output("")
		add_output("[color=#" + Utils.COLOR_INFO + "]The enemies of France have prevailed.[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]Your marshals fought bravely, but it was not enough.[/color]")
		add_output("[color=#" + Utils.COLOR_INFO + "]The eagles are furled. The Grande Armée is no more.[/color]")

	add_output("")
	add_output("[color=#" + Utils.COLOR_GOLD + "]─────────────────────────────────────[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]         FINAL STATISTICS[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]─────────────────────────────────────[/color]")

	# Display final statistics
	var final_turn = int(game_state.get("turn", current_turn))
	var regions_controlled = int(game_state.get("regions_controlled", 0))
	var total_regions = int(game_state.get("total_regions", 13))
	var final_gold = int(game_state.get("gold", gold))

	add_output("[color=#" + Utils.COLOR_INFO + "]Campaign Duration: " + str(final_turn) + " turns[/color]")
	add_output("[color=#" + Utils.COLOR_INFO + "]Regions Controlled: " + str(regions_controlled) + "/" + str(total_regions) + "[/color]")
	add_output("[color=#" + Utils.COLOR_INFO + "]Imperial Treasury: " + _format_number(final_gold) + " gold[/color]")

	# Marshal status if available
	if game_state.has("marshals"):
		var marshals = game_state.marshals
		add_output("")
		add_output("[color=#" + Utils.COLOR_MARSHAL + "]Marshal Status:[/color]")
		for marshal_name in marshals:
			var marshal = marshals[marshal_name]
			var strength = int(marshal.get("strength", 0))
			var location = marshal.get("location", "Unknown")
			if strength > 0:
				add_output("[color=#" + Utils.COLOR_INFO + "]  • " + marshal_name + ": " + _format_number(strength) + " troops at " + location + "[/color]")
			else:
				add_output("[color=#" + Utils.COLOR_ERROR + "]  • " + marshal_name + ": Destroyed[/color]")

	add_output("")
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")

	# Closing message
	if victory_status == "victory":
		add_output("[center][color=#" + Utils.COLOR_GOLD + "]Vive l'Empereur![/color][/center]")
	else:
		add_output("[center][color=#" + Utils.COLOR_INFO + "]The game is over, but the legend endures...[/color][/center]")

	add_output("")

func _show_action_cost(action_info: Dictionary):
	"""Show action point usage."""
	var cost = int(action_info.get("cost", 0))
	var remaining = int(action_info.get("remaining", actions_remaining))
	
	if cost > 0:
		add_output("[color=#" + Utils.COLOR_INFO + "]   [" + str(int(remaining)) + "/" + str(int(max_actions)) + " actions remaining][/color]")

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
	# EC-6a: max_turns == 0 is the backend's open-ended-sandbox sentinel
	# (Europe campaign) — show the bare turn number, never "N/0" or a
	# stale "61/60" countdown. Legacy worlds keep the N/limit clock.
	if int(max_turns) <= 0:
		turn_value.text = str(int(current_turn))
	else:
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
		_set_pending_envoy_count(int(diplo_data.get("pending_envoy_count", 0)))
		top_bar.update_diplomatic_fields(diplo_data)


func _set_pending_envoy_count(count: int):
	"""Sync cached envoy count and clear stale end-turn confirmation when needed."""
	var new_count = int(count)
	if new_count != _current_envoy_count or new_count <= 0:
		_awaiting_end_turn_confirmation = false
		_set_open_envoys_prompt_visible(false)
	_current_envoy_count = new_count


func _set_open_envoys_prompt_visible(is_visible: bool):
	open_envoys_button.visible = is_visible and _current_envoy_count > 0
	if open_envoys_button.visible:
		open_envoys_button.text = "Open Envoys (%d)" % _current_envoy_count


func _sync_response_hud(response: Dictionary):
	"""Apply HUD updates before popup early-returns short-circuit the handler."""
	if response.get("success", false):
		if response.has("action_summary"):
			_update_status(response.action_summary)
		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)
	_update_diplomatic_top_bar(response)
	if notification_bar and response.has("notifications"):
		notification_bar.update_notifications(response.notifications)


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
	add_output("[color=#" + Utils.COLOR_INFO + "]─────────────────────────────────────[/color]")

func add_output(text: String):
	"""Add text to output display with message limit."""
	text = Utils.humanize_nation_keys_in_text(text)
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
		add_output("[color=#" + Utils.COLOR_FEEDBACK + "][i]" + feedback.strategic + "[/i][/color]")

	# Ambiguity feedback (clarity)
	if feedback.has("ambiguity") and feedback.ambiguity != "":
		add_output("[color=#" + Utils.COLOR_FEEDBACK + "][i]" + feedback.ambiguity + "[/i][/color]")

func _trim_old_messages():
	"""Remove oldest messages to prevent infinite growth.
	Uses .text (preserves BBCode) instead of .get_parsed_text() (strips BBCode)."""
	var current_text = output_display.text
	var lines = current_text.split("\n")

	# Keep last 75% of messages
	var keep_from = int(lines.size() * 0.25)
	var new_lines = lines.slice(keep_from)

	output_display.clear()
	output_display.append_text("[color=#" + Utils.COLOR_INFO + "][...earlier messages trimmed...][/color]\n\n")
	output_display.append_text("\n".join(new_lines))

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
	add_output("[color=#" + Utils.COLOR_MARSHAL + "]⚠ Marshal " + marshal_name + " raises concerns...[/color]")
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
		add_output("[color=#" + Utils.COLOR_ERROR + "]ERROR: Dialog not loaded![/color]")
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

	add_output("[color=#" + Utils.COLOR_COMMAND + "]► " + choice_text + "[/color]")
	add_output("")

	# Send choice to backend
	api_client.send_objection_response(choice, _on_objection_response)

func _on_objection_response(response):
	"""Handle backend response after player makes objection choice."""
	if DEBUG_VERBOSE:
		print("OBJECTION RESPONSE: success=%s disobeyed=%s defiance=%s" % [
			response.get("success", false), response.get("disobeyed", false), response.get("defiance", false)])

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

		_update_diplomatic_top_bar(response)
		_update_war_panel_visibility()
		set_input_enabled(true)
		command_input.grab_focus()
		return

	# ════════════════════════════════════════════════════════════
	# CHECK FOR DISOBEY (V1): Marshal refused to obey
	# ════════════════════════════════════════════════════════════
	if response.get("disobeyed", false):
		add_output("[color=#" + Utils.COLOR_ERROR + "]⚠ DISOBEDIENCE![/color]")
		add_output("[color=#" + Utils.COLOR_MARSHAL + "]" + str(response.get("message", "The marshal refuses.")) + "[/color]")
		add_output("")

		# Update status even on disobey
		if response.has("action_summary"):
			_update_status(response.action_summary)

		# Check for redemption event triggered by disobey
		if response.has("redemption_event"):
			if DEBUG_VERBOSE:
				print("REDEMPTION EVENT after disobey - showing dialog")
			_show_redemption_dialog(response.redemption_event)
			return  # Don't re-enable input until redemption resolved

		_update_diplomatic_top_bar(response)
		_update_war_panel_visibility()
		set_input_enabled(true)
		command_input.grab_focus()
		return

	# ════════════════════════════════════════════════════════════
	# CHECK FOR REDEMPTION EVENT: Trust at critical low
	# ════════════════════════════════════════════════════════════
	if response.has("redemption_event"):
		if DEBUG_VERBOSE:
			print("REDEMPTION EVENT detected - showing dialog")

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
		if response.has("message") and response.get("message", ""):
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
		add_output("[color=#" + Utils.COLOR_ERROR + "]" + str(response.get("message", "An error occurred")) + "[/color]")

	_update_war_panel_visibility()
	add_output("")
	command_input.grab_focus()


func _show_redemption_dialog(redemption_event: Dictionary):
	"""Display redemption popup dialog when trust hits critical low."""
	print("REDEMPTION DIALOG - showing popup for event: ", redemption_event)

	var marshal_name = redemption_event.get("marshal", "Marshal")

	# Show brief notification in log
	add_output("")
	add_output("[color=#" + Utils.COLOR_ERROR + "]⚠ " + marshal_name + " requests an urgent audience...[/color]")
	add_output("")

	# Check if dialog exists
	if redemption_dialog == null:
		print("❌ ERROR: redemption_dialog is NULL!")
		push_error("redemption_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + Utils.COLOR_ERROR + "]ERROR: Redemption dialog not loaded![/color]")
		# Fallback to text commands
		_show_redemption_text_fallback(redemption_event)
		return

	# Show the popup dialog
	redemption_dialog.show_redemption(redemption_event)
	pending_redemption = true


func _show_redemption_text_fallback(redemption_event: Dictionary):
	"""Fallback text display if dialog fails to load."""
	var options = redemption_event.get("options", [])

	add_output("[color=#" + Utils.COLOR_INFO + "]You must decide how to handle this:[/color]")
	for opt in options:
		add_output("[color=#" + Utils.COLOR_INFO + "]  • " + opt.get("id", "?") + ": " + opt.get("text", "Unknown") + "[/color]")

	add_output("")
	add_output("[color=#" + Utils.COLOR_GOLD + "]Type: 'grant_autonomy', 'dismiss', or 'demand_obedience'[/color]")
	add_output("")

	pending_redemption = true
	set_input_enabled(true)
	command_input.grab_focus()


func _on_redemption_choice_made(choice: String):
	"""Handle player's choice in redemption dialog."""
	if DEBUG_VERBOSE:
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

	add_output("[color=#" + Utils.COLOR_COMMAND + "]► " + choice_text + "[/color]")
	add_output("")

	# Send choice to backend
	api_client.send_redemption_response(choice, _on_redemption_response)


func _on_redemption_response(response):
	"""Handle backend response after player makes redemption choice."""
	if DEBUG_VERBOSE:
		print("REDEMPTION RESPONSE: success=%s choice=%s" % [
			response.get("success", false), response.get("choice", "unknown")])

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

		var msg = str(response.get("message", ""))
		if choice == "grant_autonomy":
			add_output("[color=#" + Utils.COLOR_SUCCESS + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + Utils.COLOR_SUCCESS + "]   AUTONOMY GRANTED[/color]")
			add_output("[color=#" + Utils.COLOR_SUCCESS + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + Utils.COLOR_MARSHAL + "]" + msg + "[/color]")
			var turns = int(response.get("autonomy_turns", 3))
			add_output("[color=#" + Utils.COLOR_INFO + "]The marshal will act independently for " + str(turns) + " turns.[/color]")

		elif choice == "dismiss":
			add_output("[color=#" + Utils.COLOR_ERROR + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + Utils.COLOR_ERROR + "]   MARSHAL DISMISSED[/color]")
			add_output("[color=#" + Utils.COLOR_ERROR + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + Utils.COLOR_MARSHAL + "]" + msg + "[/color]")

		elif choice == "demand_obedience":
			add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + Utils.COLOR_GOLD + "]   OBEDIENCE DEMANDED[/color]")
			add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + Utils.COLOR_MARSHAL + "]" + msg + "[/color]")
			add_output("[color=#" + Utils.COLOR_INFO + "]Warning: High chance of future disobedience.[/color]")

		else:
			add_output("[color=#" + Utils.COLOR_SUCCESS + "]" + msg + "[/color]")

		add_output("")
	else:
		add_output("[color=#" + Utils.COLOR_ERROR + "]" + str(response.get("message", "An error occurred")) + "[/color]")
		add_output("")

	_update_diplomatic_top_bar(response)
	_update_war_panel_visibility()
	set_input_enabled(true)
	command_input.grab_focus()


func _show_enemy_phase_dialog(enemy_phase: Dictionary, turn: int):
	"""Display enemy phase popup with full battle details."""
	if DEBUG_VERBOSE:
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
		add_output("[color=#" + Utils.COLOR_DISPATCH + "]━━ Field Dispatches ━━[/color]")
		for concern in concerns:
			var marshal_name = concern.get("marshal", "Unknown")
			var msg = concern.get("message", "")
			if msg != "":
				add_output("[color=#" + Utils.COLOR_DISPATCH + "]  " + msg + "[/color]")
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
		add_output("[color=#" + Utils.COLOR_CONQUEST + "]" + str(response.get("message", "")) + "[/color]")

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
	if capture_data is Dictionary and str(capture_data.get("stage", "capture")) == "estate":
		# W6-8: the second, estate question
		add_output("[color=#" + Utils.COLOR_GOLD + "]An estate in your hands: Confiscate or Respect the title?[/color]")
	else:
		add_output("[color=#" + Utils.COLOR_GOLD + "]Your forces await orders: Plunder or Secure?[/color]")
	add_output("")

	if capture_choice_dialog == null:
		push_error("capture_choice_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + Utils.COLOR_ERROR + "]ERROR: Capture choice dialog not loaded![/color]")
		set_input_enabled(true)
		return

	capture_choice_dialog.show_capture_choice(capture_data)


func _on_capture_choice_made(choice: String):
	"""Handle player's capture-pipeline choice (plunder/secure or the W6-8
	estate stage's confiscate/respect)."""
	set_input_enabled(false)

	var choice_text = ""
	if choice == "plunder":
		choice_text = "You order your troops to plunder the region!"
		add_output("[color=#" + Utils.COLOR_BATTLE + "]" + choice_text + "[/color]")
	elif choice == "confiscate":
		choice_text = "You order the estate confiscated for the treasury!"
		add_output("[color=#" + Utils.COLOR_BATTLE + "]" + choice_text + "[/color]")
	elif choice == "respect":
		choice_text = "You order the marshal's title respected."
		add_output("[color=#" + Utils.COLOR_SUCCESS + "]" + choice_text + "[/color]")
	else:
		choice_text = "You order your troops to secure the region."
		add_output("[color=#" + Utils.COLOR_SUCCESS + "]" + choice_text + "[/color]")
	add_output("")

	# W6-0/W6-8: answer with the identity of the question we rendered so a
	# superseded popup can never resolve the wrong matter.
	var dialogue_id: int = -1
	if capture_choice_dialog != null:
		dialogue_id = capture_choice_dialog.current_dialogue_id
	api_client.send_capture_choice_response(choice, _on_capture_choice_response, dialogue_id)


func _on_capture_choice_response(response):
	"""Handle backend response after player makes plunder/secure choice."""
	set_input_enabled(true)

	# W6-8: the answer may mount a SECOND question (the estate stage), or a
	# stale/wrong-token answer re-attaches the current one — chain straight
	# into the same dialog (it prints the message and refreshes state).
	if _response_has_capture_choice_route(response):
		_show_capture_choice_dialog(response)
		return

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

		add_output("[color=#" + Utils.COLOR_SUCCESS + "]" + str(response.get("message", "")) + "[/color]")

		# Update diplomatic displays after capture choice (may change threat/territory)
		_update_diplomatic_top_bar(response)

		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return
	else:
		add_output("[color=#" + Utils.COLOR_ERROR + "]" + str(response.get("message", "An error occurred")) + "[/color]")

	_update_war_panel_visibility()
	add_output("")
	command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# LOAD GAME DIALOG (Phase 6: Save/Load)
# ════════════════════════════════════════════════════════════════════════════

func _show_load_dialog():
	"""Fetch saves from backend and show load dialog."""
	if load_dialog == null:
		add_output("[color=#" + Utils.COLOR_ERROR + "]Load dialog not available.[/color]")
		return
	api_client.list_saves(_on_saves_listed)

func _on_saves_listed(response):
	"""Handle saves list response from backend."""
	if response.success and response.has("saves"):
		load_dialog.show_saves(response.saves)
	else:
		add_output("[color=#" + Utils.COLOR_ERROR + "]Failed to list saves.[/color]")
		set_input_enabled(true)

func _on_load_save_selected(filename: String):
	"""Player selected a save to load."""
	set_input_enabled(false)
	add_output("[color=#" + Utils.COLOR_INFO + "]Loading save...[/color]")
	api_client.load_game(filename, _on_load_result)

func _reset_frontend_state_for_world_swap(clear_output: bool = true):
	"""Clear transient local UI state before hydrating a different campaign."""
	if top_bar:
		top_bar.close_all_screens()
	if dialog_manager:
		dialog_manager.hide_all()
	if notification_bar and notification_bar.has_method("update_notifications"):
		notification_bar.update_notifications([])

	pending_enemy_phase_response = null
	pending_dispatch_data = null
	pending_strategic_response = null
	pending_redemption = false
	pending_charge_marshal = ""
	pending_charge_target = ""
	interrupt_queue.clear()
	_last_command_response = {}
	_cached_wars = []
	_cached_coalition_data = null
	_has_active_wars = false
	_dismissed_proposal_nation = ""
	_pending_envoy_request_active = false
	_awaiting_end_turn_confirmation = false
	_set_pending_envoy_count(0)
	command_history.clear()
	history_index = -1
	command_input.text = ""

	if clear_output:
		output_display.clear()
		message_count = 0


func _apply_world_swap_response(response: Dictionary, success_text: String):
	"""Reuse one hydration path for load and new-game world swaps."""
	_reset_frontend_state_for_world_swap(true)
	_sync_response_hud(response)
	_process_active_wars(response)

	if success_text != "":
		add_output("[color=#" + Utils.COLOR_SUCCESS + "]" + success_text + "[/color]")
	var detail = str(response.get("message", "")).strip_edges()
	if detail != "":
		add_output("[color=#" + Utils.COLOR_INFO + "]" + detail + "[/color]")
	add_output("")
	set_input_enabled(true)
	command_input.grab_focus()


func _on_load_result(response):
	"""Handle load result from backend."""
	if response.success:
		_apply_world_swap_response(response, "Game loaded successfully.")
	else:
		set_input_enabled(true)
		add_output("[color=#" + Utils.COLOR_ERROR + "]Load failed: " + response.get("message", "Unknown error") + "[/color]")
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
	if DEBUG_VERBOSE:
		print("_show_glorious_charge_dialog() CALLED")

	# Store pending info for sending back to server
	# Handle null values (get() default doesn't work if key exists with null)
	var marshal_val = response.get("marshal")
	var target_val = response.get("target")
	var reck_val = response.get("recklessness")

	pending_charge_marshal = marshal_val if marshal_val != null else ""
	pending_charge_target = target_val if target_val != null else ""

	# Get recklessness - backend sends it in the response directly
	var recklessness = int(reck_val) if reck_val != null else 3

	if DEBUG_VERBOSE:
		print("  Parsed: marshal=%s, target=%s, recklessness=%d" % [pending_charge_marshal, pending_charge_target, recklessness])

	# Show notification in log
	add_output("")
	add_output("[color=#" + Utils.COLOR_BATTLE + "]🐴 " + pending_charge_marshal + "'s blood is up![/color]")
	add_output("[color=#" + Utils.COLOR_INFO + "]Recklessness at " + str(int(recklessness)) + "/4 - Glorious Charge available![/color]")
	add_output("")

	# Check if dialog exists
	if glorious_charge_dialog == null:
		print("❌ ERROR: glorious_charge_dialog is NULL!")
		push_error("glorious_charge_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + Utils.COLOR_ERROR + "]ERROR: Glorious Charge dialog not loaded![/color]")
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
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]         GLORIOUS CHARGE![/color]")
	add_output("[color=#" + Utils.COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")
	add_output("[color=#" + Utils.COLOR_ERROR + "]⚠ Glorious Charge deals 2x damage but also TAKES 2x damage![/color]")
	add_output("[color=#" + Utils.COLOR_INFO + "]Target: " + pending_charge_target + "[/color]")
	add_output("")
	add_output("[color=#" + Utils.COLOR_INFO + "]Type 'charge' to execute Glorious Charge[/color]")
	add_output("[color=#" + Utils.COLOR_INFO + "]Type 'restrain' for normal attack[/color]")
	add_output("")

	set_input_enabled(true)
	command_input.grab_focus()


func _on_glorious_charge_choice_made(choice: String):
	"""Handle player's choice in Glorious Charge dialog."""
	if DEBUG_VERBOSE:
		print("GLORIOUS CHARGE CHOICE: %s marshal=%s target=%s" % [choice, pending_charge_marshal, pending_charge_target])

	# Disable input while processing
	set_input_enabled(false)

	# Display player choice in log
	var choice_text = ""
	if choice == "charge":
		choice_text = pending_charge_marshal + " unleashes a GLORIOUS CHARGE!"
		add_output("[color=#" + Utils.COLOR_BATTLE + "]🐴⚔ " + choice_text + " ⚔🐴[/color]")
	else:
		choice_text = "You restrain " + pending_charge_marshal + " - normal attack."
		add_output("[color=#" + Utils.COLOR_COMMAND + "]► " + choice_text + "[/color]")

	add_output("")

	# Send choice to backend
	api_client.send_glorious_charge_response(choice, _on_glorious_charge_response)


func _on_glorious_charge_response(response):
	"""Handle backend response after player makes Glorious Charge choice."""
	if DEBUG_VERBOSE:
		print("GLORIOUS CHARGE RESPONSE: success=%s" % response.get("success", false))

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
		add_output("[color=#" + Utils.COLOR_ERROR + "]" + str(response.get("message", "An error occurred")) + "[/color]")

	_update_diplomatic_top_bar(response)
	_update_war_panel_visibility()
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
	add_output("[color=#" + Utils.COLOR_GOLD + "]--- Strategic Order Updates ---[/color]")
	for report in reports:
		var marshal_name = report.get("marshal", "")
		var msg = report.get("message", "")
		if msg:
			add_output("[color=#" + Utils.COLOR_INFO + "]" + marshal_name + ": " + msg + "[/color]")
		# Log sally battle details to output
		var battle_msg = report.get("battle_message", "")
		if battle_msg:
			add_output("[color=#" + Utils.COLOR_BATTLE + "]  " + battle_msg + "[/color]")
		var outcome = report.get("outcome", "")
		if outcome:
			var outcome_color = Utils.COLOR_SUCCESS if outcome == "victory" else Utils.COLOR_ERROR if outcome == "defeat" else Utils.COLOR_BATTLE
			add_output("[color=#" + outcome_color + "]  Result: " + outcome.capitalize() + "[/color]")
	add_output("")

	strategic_report_popup.show_reports(reports, turn)


func _on_strategic_report_dismissed():
	"""Handle strategic report popup dismissed."""
	if DEBUG_VERBOSE:
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
		add_output("[color=#" + Utils.COLOR_ERROR + "]ERROR: Interrupt popup not loaded![/color]")
		_process_next_interrupt()
		return

	var marshal_name = interrupt_data.get("marshal", "Marshal")
	add_output("[color=#" + Utils.COLOR_BATTLE + "]" + marshal_name + " awaits your orders![/color]")

	interrupt_popup.show_interrupt(interrupt_data)


func _on_interrupt_choice_made(marshal_name: String, response_type: String, choice: String):
	"""Handle player choosing an interrupt response."""
	if DEBUG_VERBOSE:
		print("Interrupt choice: marshal=%s, type=%s, choice=%s" % [marshal_name, response_type, choice])
	set_input_enabled(false)

	add_output("[color=#" + Utils.COLOR_COMMAND + "]> " + marshal_name + ": " + choice.replace("_", " ") + "[/color]")

	# Send to backend
	api_client.send_strategic_response(marshal_name, response_type, choice, _on_interrupt_response)


func _on_interrupt_response(response):
	"""Handle backend response to interrupt choice."""
	if response.success:
		# A muster "Attack Anyway" RESOLVES a battle — render it with the same
		# battle / After-Action formatting a direct attack gets, not a flat
		# one-liner (was: plain text, so the confirmed battle read as a shrug).
		var events = response.get("events", [])
		var is_battle = response.has("battle_report") or (
			events.size() > 0 and str(events[0].get("type", "")) in ["battle", "bombardment", "conquest"])
		if is_battle:
			_display_result(response)
		else:
			var msg = response.get("message", "Order acknowledged.")
			add_output("[color=#" + Utils.COLOR_SUCCESS + "]" + msg + "[/color]")

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
		add_output("[color=#" + Utils.COLOR_ERROR + "]" + response.get("message", "Error processing response.") + "[/color]")

	# Update diplomatic displays after interrupt resolution
	_update_diplomatic_top_bar(response)

	# Check for redemption event from strategic interrupt trust penalty
	if response.has("redemption_event"):
		interrupt_queue.clear()  # Redemption takes priority
		pending_strategic_response = null
		pending_enemy_phase_response = null
		_show_pending_dispatch()
		_show_redemption_dialog(response.redemption_event)
		return  # Don't re-enable input until redemption resolved

	# A muster-confirmed attack can resolve into a CAPTURE (plunder/secure),
	# a glorious charge, or another follow-on popup. Route them through the
	# shared table so the choice is surfaced instead of silently dropped —
	# dropping the capture choice used to block the NEXT command with
	# "you must decide how to handle the captured region first!". If a
	# follow-on popup takes the flow, stop here (it owns re-enabling input).
	if _route_response_ui(response, _post_hud_response_routes):
		return

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
		_update_war_panel_visibility()
		set_input_enabled(true)
		command_input.grab_focus()


func _show_clarification_popup(response):
	"""Show clarification popup for literal marshals."""
	set_input_enabled(false)

	# CR-2: whether the backend registered a pending dialogue for this
	# question (drives the cancel round-trip that clears it)
	_clarification_backend_pending = bool(response.get("clarification_registered", false))

	var data = response.get("clarification_data", response)

	if clarification_popup == null:
		push_error("clarification_popup is NULL!")
		add_output("[color=#" + Utils.COLOR_ERROR + "]ERROR: Clarification popup not loaded![/color]")
		set_input_enabled(true)
		return

	var marshal_name = data.get("marshal", "Marshal")
	add_output("[color=#" + Utils.COLOR_MARSHAL + "]" + marshal_name + " requests clarification...[/color]")

	clarification_popup.show_clarification(data)


func _on_clarification_choice_made(marshal_name: String, chosen_target: String, strategic_type: String):
	"""Handle player selecting a clarification target."""
	_clarification_backend_pending = false
	if DEBUG_VERBOSE:
		print("Clarification choice: marshal=%s, target=%s, type=%s" % [marshal_name, chosen_target, strategic_type])
	add_output("[color=#" + Utils.COLOR_COMMAND + "]> " + marshal_name + ", target " + chosen_target + "[/color]")

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


func _on_clarification_command(command: String):
	"""CR-2: reissue a clarification option's full command verbatim.
	The backend built the exact command ('Davout, support Ney'), so the
	popup and typed answers resolve through the same deterministic parse."""
	_clarification_backend_pending = false
	add_output("[color=#" + Utils.COLOR_COMMAND + "]> " + command + "[/color]")
	set_input_enabled(false)
	api_client.send_command(command, _on_command_result)


func _on_clarification_cancelled():
	"""Handle player cancelling a clarification."""
	add_output("[color=#" + Utils.COLOR_INFO + "]Order cancelled.[/color]")
	if _clarification_backend_pending:
		# CR-2: clear the backend's pending clarification question so it
		# cannot linger in the dialogue slot (it would block mailbox
		# activation until the next typed command consumed it)
		_clarification_backend_pending = false
		api_client.send_command("never mind", _on_command_result)
	else:
		set_input_enabled(true)
		command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# SESSION 8C DIPLOMATIC POPUP HANDLERS
# ════════════════════════════════════════════════════════════════════════════

func _on_proposal_confirm_choice(action: String, data: Dictionary):
	"""Handle player response to outgoing proposal confirmation popup.
	CRITICAL: Use send_dialogue_response (direct action index), NOT send_command.
	Keyword routing in /command misroutes terms_guidance actions:
	'territory_no_ap' contains 'territory' → matches territory_yes → Belgium bug.
	See BUGFIX_PLAN_PROPOSAL_FLOW.md Bug 6."""
	# GT-Slice-4: the client-side `adjust_terms` / `revise_settlement_terms`
	# editor mounts are retired with the freeform editor — the guided
	# per-court rows on the PROPOSE surface are the deep authoring tier, and
	# a blocked REVIEW routes back to shaping via `Return to terms`. The
	# bilateral terms-guidance `adjust_terms` still resolves through the
	# option-index path below.
	# Re-front Slice 2: a per-court row affordance (focused dial / holdout
	# Ease/Drop / coverage add) carries its own structured params (scope / nation)
	# and is NOT in options[], so the index path below cannot resolve it. The
	# popup emits the affordance dict as `data`; route it through the structured
	# `action_params` dialogue path. (Whole-table dials ride in options[] and
	# resolve via the index path with their server-side `scope: "table"`.)
	if action in SETTLEMENT_DIALOGUE_ACTIONS and (data.has("scope") or data.has("nation")):
		add_output("[color=#d9c08c]Directing Talleyrand: %s[/color]" % action.replace("_", " "))
		set_input_enabled(false)
		api_client.send_dialogue_response_with_params(action, data, _on_command_result, int(data.get("dialogue_id", -1)))
		return
	# Index-based pickers (war-purpose objectives; proposal_options) bind a
	# pure 1-based index as their action because every option shares the same
	# action string — the index is the ONLY signal of which row was clicked.
	# The backend resolves options[choice-1] directly. Was: the loop below
	# first-matched the shared action string and always sent index 1, so the
	# player's chosen war objective was silently dropped for conquest.
	if action.is_valid_int():
		add_output("[color=#d9c08c]Directing Talleyrand…[/color]")
		set_input_enabled(false)
		api_client.send_dialogue_response(int(action), _on_command_result, int(data.get("dialogue_id", -1)))
		return
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
		# W6-0 (BUG-CA-7): bind the answer to the dialogue this popup rendered.
		api_client.send_dialogue_response(choice_index, _on_command_result, int(data.get("dialogue_id", -1)))
	else:
		if action in SETTLEMENT_DIALOGUE_ACTIONS:
			add_output("[color=#e04040]Settlement popup action lost its dialogue option: %s[/color]" % action)
			set_input_enabled(false)
			if proposal_confirm_popup:
				proposal_confirm_popup.show_dialogue(data)
			return
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
	"""Handle player response to AI diplomatic proposal.
	PL-27: Uses typed dialogue response instead of synthesized command."""
	var from_nation = data.get("from_nation", "Unknown")
	if choice == "dismiss":
		# PL-27 Mailbox UX: Hide popup, keep proposal in backend for later
		_dismissed_proposal_nation = from_nation
		add_output("[color=#d9c08c]Setting aside %s's proposal. Click the envoy badge to revisit.[/color]" % from_nation)
		set_input_enabled(true)
		command_input.grab_focus()
		return
	add_output("[color=#d9c08c]Responding to %s's proposal: %s[/color]" % [from_nation, choice])
	set_input_enabled(false)
	# W6-0 (BUG-CA-7): answer the proposal this popup RENDERED, not whatever
	# is on top of the dialogue stack by the time the response arrives.
	api_client.send_dialogue_response(choice, _on_command_result, int(data.get("dialogue_id", -1)))

func _on_talleyrand_objection_choice(choice: String, data: Dictionary):
	"""Handle player response to Talleyrand's diplomatic objection.
	Session 6: Uses a typed objection endpoint instead of synthesized commands."""
	if choice == "proceed":
		add_output("[color=#d9c08c]Overriding Talleyrand's objection...[/color]")
	elif choice == "modify":
		add_output("[color=#d9c08c]Reviewing the proposal again...[/color]")
	else:
		add_output("[color=#" + Utils.COLOR_INFO + "]Proposal cancelled.[/color]")
	set_input_enabled(false)
	api_client.send_diplomatic_objection_response(choice, data, _on_command_result)

func _on_sabotage_discovery_choice(choice: String, data: Dictionary):
	"""Handle player response to sabotage discovery.
	Session 6: Uses typed dialogue response instead of synthesized command."""
	var action = {
		"confront": "confront_sabotage",
		"overlook": "overlook_sabotage",
	}.get(choice, choice)
	add_output("[color=#d9c08c]%s Talleyrand's sabotage...[/color]" % choice.capitalize())
	set_input_enabled(false)
	api_client.send_dialogue_response(action, _on_command_result)

# PL-23: _on_talleyrand_redemption_choice removed (trust system deleted)

func _on_vassal_rebellion_choice(choice: String, data: Dictionary):
	"""Handle player response to vassal rebellion imminent.
	Session 6: Uses typed dialogue response instead of synthesized command."""
	var action = {
		"invest": "invest_vassal_rebellion",
		"garrison": "garrison_vassal_rebellion",
		"accept": "accept_vassal_rebellion",
	}.get(choice, choice)
	var nation = data.get("nation", "unknown")
	add_output("[color=#d9c08c]Vassal %s: %s[/color]" % [nation, choice])
	set_input_enabled(false)
	api_client.send_dialogue_response(action, _on_command_result)

func _on_commitment_paradox_choice(choice: String, data: Dictionary):
	"""Handle player response to commitment paradox popup (Fix 15).
	Routes through dialogue response system (option index), not regular commands.
	Backend pending_diplomatic_dialogue has options[0]=honor_defender, options[1]=break."""
	var defender = str(data.get("defender", "unknown"))
	var attacker = str(data.get("attacker", "unknown"))
	set_input_enabled(false)
	if choice == "honor_defender":
		add_output("[color=#" + Utils.COLOR_GOLD + "]Honoring alliance with %s — declaring war on %s![/color]" % [defender, attacker])
		api_client.send_dialogue_response(1, _on_command_result)  # Option 1: honor_defender
	elif choice == "break_defender_alliance":
		add_output("[color=#" + Utils.COLOR_ERROR + "]Breaking alliance with %s — siding with %s.[/color]" % [defender, attacker])
		api_client.send_dialogue_response(2, _on_command_result)  # Option 2: break_defender_alliance


# ════════════════════════════════════════════════════════════════════════════
# PAUSE MENU (Phase 6.5)
# ════════════════════════════════════════════════════════════════════════════

func _is_modal_dialog_open() -> bool:
	"""True when a modal dialog requiring player choice is visible.
	These block EVERYTHING. Campaign log is NOT a modal — it's a screen.
	Delegates to DialogManager which tracks all registered modal dialogs."""
	if dialog_manager:
		return dialog_manager.is_any_modal_open()
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


func _on_open_envoys_button_pressed():
	_on_envoy_clicked()


func _on_wizard_open_envoys_requested():
	_on_envoy_clicked()


func _on_dispatch_open_envoys_requested():
	_on_envoy_clicked()


func _on_notification_review_requested(review_target: String, route_id: String = "", war_id: String = ""):
	if review_target == "diplomacy_wizard":
		_open_diplomacy_wizard()
		return
	if review_target == "ally_settlement_petition_popup":
		_on_envoy_clicked()
		return
	# WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11.6 — settlement events
	# either route to the live settlement review (war still active) or
	# fall back to the diplomatic ledger settlements section once the
	# war archives. Both targets land on the diplomatic ledger
	# CanvasLayer 50 surface for now; the settlement-review tab handle
	# is forwarded so the ledger can deep-link into recent settlements.
	if review_target == "settlement_review" or review_target == "ledger_settlements":
		if top_bar:
			if top_bar.has_method("open_diplomatic_ledger_review"):
				top_bar.open_diplomatic_ledger_review("ledger_settlements", route_id, war_id)
			else:
				top_bar.toggle_screen("diplomatic_ledger")
		return
	if review_target == "diplomatic_ledger" and top_bar:
		top_bar.toggle_screen("diplomatic_ledger")
		return
	if review_target.begins_with("ledger_") and top_bar:
		if top_bar.has_method("open_diplomatic_ledger_review"):
			top_bar.open_diplomatic_ledger_review(review_target, route_id, war_id)
		else:
			top_bar.toggle_screen("diplomatic_ledger")


func _on_envoy_clicked():
	"""Handle mailbox button click — Session 2 follow-up: open mailbox panel."""
	if _pending_envoy_request_active:
		return
	_awaiting_end_turn_confirmation = false
	_set_open_envoys_prompt_visible(false)
	_dismissed_proposal_nation = ""  # Clear so popup can show again
	_pending_envoy_request_active = true
	api_client.get_mailbox(_on_mailbox_list_result)

func _on_mailbox_list_result(response: Dictionary):
	"""Handle GET /mailbox response — show mailbox panel or direct-open single item."""
	_pending_envoy_request_active = false
	if not response.get("success", false):
		add_output("[color=#d9c08c]%s[/color]" % str(
			response.get("message", "Unable to reach the envoy at this time.")
		))
		return
	var count = int(response.get("count", 0))
	var items = response.get("items", [])
	if top_bar and top_bar.has_method("update_mailbox_count"):
		top_bar.update_mailbox_count(count)
	_set_pending_envoy_count(count)
	if count == 0:
		add_output("[color=#d9c08c]No pending envoys at this time.[/color]")
		return
	if count == 1:
		# Single item: reopen directly if already active, otherwise activate it.
		var item = items[0] if items.size() > 0 else {}
		var mailbox_id = int(item.get("mailbox_id", 0))
		var is_active = str(item.get("state", "")) == "ACTIVE"
		if is_active:
			api_client.get_pending_envoy(_on_pending_envoy_result)
		elif mailbox_id > 0:
			api_client.activate_mailbox_item(mailbox_id, _on_mailbox_activate_result)
		else:
			add_output("[color=#d9c08c]That diplomatic item could not be opened.[/color]")
		return
	# 2+ items: show the browsable mailbox panel
	if mailbox_panel:
		mailbox_panel.show_mailbox(response)

func _on_pending_envoy_result(response: Dictionary):
	"""Handle pending envoy recovery — reopen the active proposal popup."""
	_pending_envoy_request_active = false
	var envoy_ct = int(response.get("pending_envoy_count", 0))
	if top_bar and top_bar.has_method("update_mailbox_count"):
		top_bar.update_mailbox_count(envoy_ct)
	_set_pending_envoy_count(envoy_ct)
	if not response.get("success", false):
		add_output("[color=#d9c08c]%s[/color]" % str(
			response.get("message", "Unable to reach the envoy at this time.")
		))
		return
	if not response.get("has_pending", false):
		add_output("[color=#d9c08c]No pending envoys at this time.[/color]")
		return
	var dtype = response.get("dialogue_type", "")
	if dtype in ["incoming_proposal", "counter_offer", "counter_offer_response"]:
		var proposal_data = response.get("incoming_proposal", {})
		if incoming_proposal_popup and proposal_data.size() > 0:
			set_input_enabled(false)
			incoming_proposal_popup.show_proposal(proposal_data)
		else:
			add_output("[color=#d9c08c]An envoy is waiting but the proposal data could not be retrieved.[/color]")
	elif dtype == "incoming_settlement_offer":
		# SC-5 reversal commit 2 (Slice G1): open the incoming
		# settlement offer popup. The pending-envoy response returns
		# the popup payload under `incoming_settlement_offer`.
		var offer_data = response.get("incoming_settlement_offer", {})
		if proposal_confirm_popup and offer_data is Dictionary and offer_data.size() > 0:
			set_input_enabled(false)
			proposal_confirm_popup.show_dialogue(offer_data)
		else:
			add_output("[color=#d9c08c]A settlement offer is waiting but the popup data could not be retrieved.[/color]")
	elif dtype in ["conflict_alert", "settlement_confirm", "ally_settlement_petition"]:
		_show_confirm_dialogue_from_response(response, "A diplomatic alert is pending.")
	else:
		add_output("[color=#d9c08c]Pending diplomatic matter: %s[/color]" % dtype)

func _on_mailbox_item_selected(mailbox_id: int, is_active: bool, item_type: String):
	"""Handle click on a mailbox item row."""
	if is_active:
		# Active item: just reopen via /pending_envoy
		api_client.get_pending_envoy(_on_pending_envoy_result)
	else:
		# Queued item: activate it first via POST /mailbox/activate
		api_client.activate_mailbox_item(mailbox_id, _on_mailbox_activate_result)

func _on_mailbox_activate_result(response: Dictionary):
	"""Handle POST /mailbox/activate response — open the newly active item."""
	var act_ct = int(response.get("count", 0))
	if top_bar and top_bar.has_method("update_mailbox_count"):
		top_bar.update_mailbox_count(act_ct)
	_set_pending_envoy_count(act_ct)
	if not response.get("success", false):
		add_output("[color=#d9c08c]%s[/color]" % str(
			response.get("message", "Could not activate that item.")
		))
		return
	var dtype = str(response.get("dialogue_type", ""))
	if dtype in ["incoming_proposal", "counter_offer", "counter_offer_response"]:
		var proposal_data = response.get("incoming_proposal", {})
		if incoming_proposal_popup and proposal_data.size() > 0:
			set_input_enabled(false)
			incoming_proposal_popup.show_proposal(proposal_data)
		else:
			add_output("[color=#d9c08c]Item activated but popup data missing.[/color]")
	elif dtype == "incoming_settlement_offer":
		# SC-5 reversal commit 2 (Slice G1): open the incoming
		# settlement offer popup. The mailbox-activate response
		# returns the popup payload under `incoming_settlement_offer`.
		var offer_data = response.get("incoming_settlement_offer", {})
		if proposal_confirm_popup and offer_data is Dictionary and offer_data.size() > 0:
			set_input_enabled(false)
			proposal_confirm_popup.show_dialogue(offer_data)
		else:
			add_output("[color=#d9c08c]Item activated but settlement-offer popup data missing.[/color]")
	elif dtype in ["conflict_alert", "settlement_confirm", "ally_settlement_petition"]:
		_show_confirm_dialogue_from_response(response, "Item activated but alert data missing.")

func _on_mailbox_panel_closed():
	"""Mailbox panel closed without selecting an item."""
	pass


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
	add_output("[color=#" + Utils.COLOR_COMMAND + "]► " + command + "[/color]")

	# Disable input while processing
	set_input_enabled(false)

	# Send to backend via normal command flow
	api_client.send_command(command, _on_command_result)


# ═══════ ES-7 SECOND PASS (§0.6.8 item 6): THE MARSHAL'S REWARD ═══════

func _on_reward_requested(card: Dictionary):
	"""The Generals screen's [Reward…] link — open the portfolio dialog."""
	if reward_dialog:
		reward_dialog.show_reward(card)


func _on_commission_requested(candidate_name: String):
	"""Marshal Recruitment: a [Commission X] button — the typed command
	through the reward pipeline (history, echo, Generals refresh)."""
	if candidate_name.is_empty():
		return
	_on_reward_command("commission " + candidate_name)


func _on_reward_command(command: String):
	"""A reward-dialog button — same pipeline as a typed command, then
	refresh the Generals screen so the card shows the new estate/rente."""
	if command.is_empty():
		return
	_add_to_history(command)
	add_output("")
	add_output("[color=#" + Utils.COLOR_COMMAND + "]► " + command + "[/color]")
	set_input_enabled(false)
	api_client.send_command(command, _on_reward_command_result)


func _on_reward_command_result(response):
	_on_command_result(response)
	if top_bar and top_bar.screens.has("generals"):
		var generals_screen = top_bar.screens["generals"]
		if generals_screen and generals_screen.has_method("refresh_if_open"):
			generals_screen.refresh_if_open()


# ═══════ JEALOUSY v3.2: THE MARSHAL-PETITION CHANNEL (spec §0.2-10) ═══════

func _on_marshal_petition_choice(choice_id: String):
	"""A petition-dialog button — POST the answer to the one shared
	endpoint; the backend dispatches by petition kind."""
	if choice_id.is_empty():
		return
	set_input_enabled(false)
	api_client.send_marshal_petition_response(choice_id, _on_marshal_petition_result)


func _on_marshal_petition_result(response):
	_on_command_result(response)
	if top_bar and top_bar.screens.has("generals"):
		var generals_screen = top_bar.screens["generals"]
		if generals_screen and generals_screen.has_method("refresh_if_open"):
			generals_screen.refresh_if_open()


func _on_wizard_structured_command_selected(command: String, data: Dictionary):
	"""Handle wizard action selection that needs structured POST fields
	(e.g. `open_settlement` carrying `war_id` so the backend can scope the
	settlement to the correct war_instance instead of falling through to
	the legacy first-active-war fallback)."""
	if command.is_empty():
		return

	_add_to_history(command)

	add_output("")
	add_output("[color=#" + Utils.COLOR_COMMAND + "]► " + command + "[/color]")

	set_input_enabled(false)

	if api_client.has_method("send_structured_command"):
		api_client.send_structured_command(command, data, _on_command_result)
	else:
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
	if notification_bar and notification_bar.has_method("set_suspended"):
		notification_bar.set_suspended(_is_modal_dialog_open())


func _on_war_card_clicked(nation: String, status: String, war_instance_id: String = ""):
	"""N4h: Handle war card click — open detail popup."""
	if war_detail_popup == null:
		return
	if status == "armistice":
		var war_data = _find_war_data(nation, war_instance_id)
		if war_data != null:
			war_detail_popup.show_armistice(war_data)
	else:
		var war_data = _find_war_data(nation, war_instance_id)
		if war_data != null:
			war_detail_popup.show_war(war_data, _cached_coalition_data)


func _route_settlement_recovery_route(route: Dictionary):
	var surface = str(route.get("surface", route.get("target", "")))
	var war_id = str(route.get("war_id", ""))
	var target_nation = str(route.get("selected_target_nation", route.get("target_nation", route.get("nation", ""))))
	if surface == "war_detail":
		if war_detail_popup == null:
			add_output("[color=#e04040]War detail is not available.[/color]")
			set_input_enabled(true)
			command_input.grab_focus()
			return
		var war_data = _find_war_data(target_nation, war_id)
		if war_data != null:
			add_output("[color=#" + Utils.COLOR_INFO + "]Opening war detail for " + target_nation + ".[/color]")
			war_detail_popup.show_war(war_data, _cached_coalition_data)
		else:
			add_output("[color=#e04040]This war is no longer active from the current war panel.[/color]")
		set_input_enabled(true)
		command_input.grab_focus()
		return
	if surface == "settlement_history":
		var route_id = str(route.get("route_id", ""))
		if top_bar and top_bar.has_method("open_diplomatic_ledger_review"):
			top_bar.open_diplomatic_ledger_review("ledger_settlements", route_id, war_id)
		set_input_enabled(true)
		command_input.grab_focus()
		return
	add_output("[color=#e04040]No verified recovery route is available.[/color]")
	set_input_enabled(true)
	command_input.grab_focus()


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


func _on_war_settlement_clicked(war_id: String, nation: String):
	"""Open common-peace settlement from war detail / coalition detail.

	SC-5R-2: when the war is archived (already settled / cleaned up),
	the settlement surface is the Diplomatic Ledger Treaties tab, not
	the live war editor. Route to the ledger instead of POSTing a stale
	`propose_common_peace`, which would only return a humanized error.
	Active wars continue to open the live settlement review."""
	if _is_war_archived_in_cache(war_id):
		add_output("[color=#d9c08c]Opening settlement history for %s[/color]" % nation)
		_route_settlement_recovery_route({
			"surface": "settlement_history",
			"war_id": war_id,
		})
		return
	var command = "propose common peace with " + nation
	add_output("[color=#d9c08c]Opening settlement review for %s[/color]" % nation)
	set_input_enabled(false)
	if api_client.has_method("send_structured_command"):
		api_client.send_structured_command(command, {
			"action": "propose_common_peace",
			"target_nation": nation,
			"war_id": war_id,
		}, _on_command_result)
	else:
		api_client.send_command(command, _on_command_result)


func _on_war_request_terms_clicked(war_id: String, nation: String):
	"""SC-30 / Slice G1: ask the enemy war leader to name settlement terms.

	The answer arrives on the next AI phase — a granted request produces a
	real incoming settlement offer (the existing offer popup/mailbox), a
	refusal arrives as a voiced notification."""
	var command = "request terms from " + nation
	add_output("[color=#d9c08c]Requesting terms from %s[/color]" % Utils.display_nation_name(nation))
	set_input_enabled(false)
	if api_client.has_method("send_structured_command"):
		api_client.send_structured_command(command, {
			"action": "request_terms",
			"target_nation": nation,
			"war_id": war_id,
		}, _on_command_result)
	else:
		api_client.send_command(command, _on_command_result)


func _is_war_archived_in_cache(war_id: String) -> bool:
	"""SC-5R-2: return true when the cached war list shows the war as
	ended / archived. _cached_wars only carries active wars, so a war_id
	that does NOT appear in any active row AND that we have seen before
	is treated as archived. An unknown war_id is treated as active
	(conservative — the backend will still validate)."""
	if war_id == "":
		return false
	for w in _cached_wars:
		if str(w.get("war_instance_id", w.get("war_id", ""))) == war_id:
			return false
	# War isn't in cached active wars. Check if it was previously in a
	# notification / treaty rail; otherwise default to active so live
	# wars without a war_instance_id still reach the backend.
	return bool(_seen_war_ids.get(war_id, false))


func _on_war_ended_notification(message: String):
	"""Fix 10: Display feedback when war ends while detail popup is open."""
	add_output("[color=#" + Utils.COLOR_INFO + "]" + message + "[/color]")


func _find_war_data(nation: String, war_instance_id: String = ""):
	"""Find war data for a specific nation from cached active_wars."""
	if war_instance_id != "":
		for w in _cached_wars:
			if str(w.get("war_instance_id", "")) == war_instance_id and str(w.get("opponent", "")) == nation:
				return w
	for w in _cached_wars:
		if str(w.get("opponent", "")) == nation:
			return w
	return null


func _process_active_wars(response: Dictionary):
	"""N4i: Parse active_wars from response and update HUD + detail popup.
	ALWAYS refreshes panel visibility — even when response lacks active_wars.
	This ensures the panel re-appears after modal popups close."""
	var active_wars_data = response.get("active_wars", null)
	if active_wars_data != null and active_wars_data is Dictionary:
		if war_status_panel:
			war_status_panel.update_wars(active_wars_data)

		_cached_wars = active_wars_data.get("wars", [])
		for w in _cached_wars:
			var cached_war_id = str(w.get("war_instance_id", w.get("war_id", "")))
			if cached_war_id != "":
				_seen_war_ids[cached_war_id] = true
		_cached_coalition_data = active_wars_data.get("coalition", null)
		_has_active_wars = not _cached_wars.is_empty()

		# Refresh detail popup if open (in-place update, don't close)
		if war_detail_popup and war_detail_popup.visible:
			war_detail_popup.refresh_if_open(active_wars_data)

	# Always refresh visibility — critical for re-showing after popup dismiss
	_update_war_panel_visibility()


func _on_pause_save_requested():
	"""Handle Save Game from pause menu."""
	add_output("[color=#" + Utils.COLOR_INFO + "]Saving game...[/color]")
	api_client.save_game("quicksave", _on_pause_save_result)

func _on_pause_save_result(response):
	"""Handle save result from pause menu."""
	if response.success:
		add_output("[color=#" + Utils.COLOR_SUCCESS + "]Game saved successfully.[/color]")
	else:
		add_output("[color=#" + Utils.COLOR_ERROR + "]Save failed: " + str(response.get("message", "Unknown error")) + "[/color]")
	add_output("")

func _on_pause_load_requested():
	"""Handle Load Game from pause menu."""
	_show_load_dialog()

func _on_pause_new_game_requested():
	"""Handle New Campaign from pause menu."""
	add_output("[color=#" + Utils.COLOR_INFO + "]Starting a new campaign. Current autosave will be replaced.[/color]")
	set_input_enabled(false)
	api_client.new_game(_on_new_game_result)

func _on_new_game_result(response):
	"""Handle fresh-campaign hydration from backend."""
	if response.success:
		_apply_world_swap_response(response, "New campaign ready.")
	else:
		set_input_enabled(true)
		add_output("[color=#" + Utils.COLOR_ERROR + "]New campaign failed: " + str(response.get("message", "Unknown error")) + "[/color]")
		add_output("")
		command_input.grab_focus()

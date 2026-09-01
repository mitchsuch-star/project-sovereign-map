extends Control

# =============================================================================
# PROJECT SOVEREIGN - Notification Rail
# =============================================================================
# Persistent notice rail for informational events. Lives below the top bar so it
# no longer competes with Envoys/DP/threat controls, and expands downward from
# the rail instead of the viewport corner.
# =============================================================================

signal notification_dismissed(notification_id: String)
signal notification_review_requested(review_target: String, route_id: String, war_id: String)
# UX23-A: a row that can DO the thing it announces. The rail never sends a
# command itself — it names one, and main.gd puts it through the same typed
# pipeline a chip or the terminal would (latch, echo, history, refresh).
signal notification_action_requested(command: String)

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
	# UX23-A: the two reward rows fell through to the priority default ("INF"
	# / "NEW"), which names neither the marshal nor the matter — and the rail
	# is now the surface the reward is GRANTED from, so the player has to be
	# able to pick it out of six pills first.
	"dotation_expectation": "PAY",
	"dotation_erosion": "PAY",
	# Aug 30, 2026 visual pass — found ON SCREEN, not by a test. With the
	# review's own `buildings_damaged` join in place the live rail STILL
	# carried two anonymous "INF" pills: PT-J4's bench notice and HC-G's
	# Gazette. Same defect, same shape — a producer shipped without its
	# renderer join — and both are player-facing rows that named nothing.
	"commission_available": "MAR",
	"gazette_published": "GAZ",
	# Aug 30, 2026 review: the same fallthrough, one slice later. The [V-6]
	# damage-legibility work added the `buildings_damaged` producer so "the
	# damage announces itself" and never made the renderer join, so a wrecked
	# market or depot arrived as the anonymous priority pill "INF" — naming
	# neither the province nor the matter, in a rail the player scans by icon.
	"buildings_damaged": "DMG",
	# ── REV-V3 (Aug 31, 2026): the rail's unmapped tail ──────────────────
	# The Aug 30 review measured 33 of the backend's 57 notification types
	# with no renderer join, arriving as the anonymous priority pill "INF" /
	# "NEW" / "ALT" — naming neither the subject nor the matter, in a rail
	# the player scans by icon. Re-measuring with an AST census over every
	# `create_notification` producer found FOUR more the constant list could
	# not see (three shipped as bare string literals, one derived from
	# SETTLEMENT_ROUTES), and three of the filed 33 that no producer has ever
	# emitted — those stand in `notifications.RAIL_EXEMPT_TYPES` with their
	# reason instead.
	#
	# Both maps are keyed identically on purpose: a label without a glyph is
	# a half-join, which is the mistake `buildings_damaged` shipped with.
	# The label is a FALLBACK (the glyph blanks the button text), so it only
	# shows if an SVG fails to load — but it must still name the matter.

	# The marshal and his corps
	"strategic_order_complete": "ARR",
	"forced_retreat_order_voided": "RTR",
	"friendly_fire_trust": "FFR",
	"reckless_cavalry_action": "CAV",
	"counter_punch_earned": "CTR",
	"drill_cancelled": "DRL",
	"marshal_defied_order": "DFY",
	"marshal_commissioned": "CMS",
	"marshal_last_stand": "ENC",
	"vindication_expired": "VIN",

	# Men, money and land
	"manpower_depleted": "DRY",
	"manpower_replenished": "MEN",
	"bankruptcy_escalation": "BNK",
	"rente_defaulted": "RNT",
	"estate_lost": "EST",
	"estate_confiscated": "SZD",

	# The map of Europe
	"nation_formed": "PRC",
	"nation_eliminated": "END",

	# The coalition ladder, and what becomes of one
	"coalition_threat_tension": "TNS",
	"coalition_murmurs": "MUR",
	"coalition_brewing": "BRW",
	"coalition_member_peaced": "SEP",
	"coalition_dissolved": "DIS",
	"coalition_cooldown_ended": "CDN",
	"alliance_cascade_war": "CSC",

	# The satellites
	"vassal_courting_detected": "CRT",
	"defection_cascade": "CSD",

	# The chancery and the peace table
	"sabotage_discovered": "SAB",
	"diplo_auto_downgrade": "DWN",
	"incoming_settlement_offer": "OFR",
	"settlement_terms_request_result": "TRM",
	"ally_settlement_petition": "PET",
	"settlement_summary": "STL",
	"armistice_expired": "ARM",
}

# UI-6: real glyphs for the rail (phosphor white silhouettes on the priority-
# colored pill). Types absent here fall back to the legacy 3-letter code.
const TYPE_ICON_SVGS = {
	"coalition_declared": "sword",
	"balance_of_europe_shifted": "scales",
	"amends_offered": "handshake",
	"hard_reject_posture_triggered": "x-circle",
	"hard_reject_posture_cleared": "check-circle",
	"diplomatic_treaty_broken": "warning",
	"commitment_paradox": "warning-circle",
	"commitment_paradox_resolved": "check-circle",
	"witness_strike_recorded": "eye",
	"call_to_arms_refused_offensive": "flag-banner",
	"call_to_arms_refused_defensive": "flag-banner",
	"call_to_arms_honored_costly": "flag-banner",
	"bargain_fulfilled": "check-circle",
	"bargain_breached": "warning",
	"bargain_voided": "hourglass",
	"bargain_ratified": "scroll",
	"bargain_triggered": "bell",
	"diplomatic_proposal": "scroll",
	"diplomatic_proposal_result": "info",
	"treaty_signed": "check",
	"treaty_broken": "warning",
	"war_declared": "sword",
	"vassal_rebellion": "castle-turret",
	"vassal_rebellion_imminent": "warning",
	"dp_insufficient": "coins",
	"turn_limit_warning": "hourglass-high",
	"defeat_imminent_warning": "warning-circle",
	# UX23-A: a purse for the expectation, the medal he has not been given
	# for the neglect. The pill colour already carries the urgency (NORMAL vs
	# HIGH), so the glyphs carry the subject instead.
	"dotation_expectation": "coins",
	"dotation_erosion": "medal",
	# The glyphs for the rows the Aug 30 review and its visual pass caught: a
	# wrecked works, a bench of officers waiting to be commissioned, and the
	# newspaper. `buildings_damaged` had been given a LABEL and no glyph — a
	# half-join, caught by this round's own floor pin rather than on screen.
	"buildings_damaged": "house",
	"commission_available": "users-three",
	"gazette_published": "book-open",
	# ── REV-V3 (Aug 31, 2026) ────────────────────────────────────────────
	# Every glyph below exists under assets/ui/icons/phosphor (a name with no
	# SVG renders NOTHING, which is worse than the pill it replaced — pinned).
	# Glyphs are a FAMILY signal, not a unique id: this file already runs
	# `warning` six times and `check-circle` six times, and the tooltip is
	# what names the particular matter. So rows that mean the same KIND of
	# thing deliberately share one — `hourglass` is "a window closed",
	# `flag` is "a nation's standing changed", `warning-circle` is the
	# coalition alarm whose rung the pill COLOUR already carries.

	# The marshal and his corps
	"strategic_order_complete": "arrow-right",
	"forced_retreat_order_voided": "arrow-arc-left",
	"friendly_fire_trust": "warning",
	"reckless_cavalry_action": "horse",
	"counter_punch_earned": "shield-check",
	"drill_cancelled": "hourglass",
	"marshal_defied_order": "x-circle",
	"marshal_commissioned": "medal-military",
	# NOT sovereign-only, despite the Emperor's copy: the ordinary cornered
	# marshal raises the same row, and both ask the player to answer.
	"marshal_last_stand": "shield",
	"vindication_expired": "hourglass",

	# Men, money and land
	"manpower_depleted": "minus",
	"manpower_replenished": "plus",
	"bankruptcy_escalation": "bank",
	"rente_defaulted": "coins",
	"estate_lost": "house",
	"estate_confiscated": "house",

	# The map of Europe — a flag raised, a flag struck
	"nation_formed": "flag",
	"nation_eliminated": "flag",

	# The coalition ladder, and what becomes of one
	"coalition_threat_tension": "warning-circle",
	"coalition_murmurs": "warning-circle",
	"coalition_brewing": "warning-circle",
	"coalition_member_peaced": "handshake",
	"coalition_dissolved": "arrows-out",
	"coalition_cooldown_ended": "hourglass",
	"alliance_cascade_war": "sword",

	# The satellites
	"vassal_courting_detected": "eye",
	"defection_cascade": "castle-turret",

	# The chancery and the peace table
	"sabotage_discovered": "magnifying-glass",
	"diplo_auto_downgrade": "caret-down",
	"incoming_settlement_offer": "scroll",
	"settlement_terms_request_result": "x-circle",
	"ally_settlement_petition": "flag-banner",
	"settlement_summary": "check",
	"armistice_expired": "hourglass",
}

const ROUTE_ICON_SVGS = {
	"icon_balance_of_europe": "scales",
	"icon_amends_offered": "handshake",
	"icon_hard_reject": "x-circle",
	"icon_chancery_reopened": "check-circle",
	"icon_treaty_broken": "warning",
	"icon_treaty_dragged": "clock",
	"icon_paradox": "warning-circle",
	"icon_paradox_resolved": "check-circle",
	"icon_witness_strike": "eye",
	"icon_call_refused_offensive": "flag-banner",
	"icon_call_refused_defensive": "flag-banner",
	"icon_call_honored_costly": "flag-banner",
	"icon_bargain_honoured": "check-circle",
	"icon_bargain_broken": "warning",
	"icon_bargain_lapsed": "hourglass",
	"icon_bargain_sealed": "scroll",
	"icon_bargain_activated": "bell",
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
# Music & Sound Core: notification ids the bell has already rung for.
var _audio_seen_ids: Dictionary = {}
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
	# Music & Sound Core: ring the desk bell once per NEW notification id —
	# refreshes re-deliver the whole list every response, so dedupe by id.
	for notif in notifications:
		var nid := str(notif.get("id", ""))
		if nid != "" and not _audio_seen_ids.has(nid):
			_audio_seen_ids[nid] = true
			AudioManager.play("notification")
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
	btn.tooltip_text = Utils.humanize_nation_keys_in_text(str(notif.get("title", "Notification")))
	btn.mouse_filter = Control.MOUSE_FILTER_STOP
	btn.focus_mode = Control.FOCUS_NONE

	# UI-6: a real glyph when one is mapped — white phosphor silhouette on the
	# priority-colored pill; unmapped types keep the legacy 3-letter code.
	var icon_svg = _icon_svg_for(notif)
	if icon_svg != "":
		var icon_tex = load(Utils.ICON_PHOSPHOR + icon_svg + ".svg")
		if icon_tex != null:
			btn.text = ""
			btn.icon = icon_tex
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
			for icon_state in ["icon_normal_color", "icon_hover_color", "icon_pressed_color", "icon_focus_color"]:
				btn.add_theme_color_override(icon_state, Color(1, 1, 1, 1))

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


func _icon_svg_for(notif: Dictionary) -> String:
	"""Phosphor glyph name for a notification, '' when unmapped."""
	var notif_type = str(notif.get("type", ""))
	if TYPE_ICON_SVGS.has(notif_type):
		return TYPE_ICON_SVGS[notif_type]
	var details = notif.get("details", {})
	if details is Dictionary:
		var icon_key = str(details.get("icon", ""))
		if ROUTE_ICON_SVGS.has(icon_key):
			return ROUTE_ICON_SVGS[icon_key]
	return ""


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

	# Title must sit ABOVE the body in the type hierarchy: the body RichTextLabel
	# inherits the theme's 16px, so a 12px title read as a sub-caption of its
	# own paragraph. 17px keeps the heading a heading.
	var title_label = Label.new()
	title_label.text = Utils.humanize_nation_keys_in_text(str(notif.get("title", "Notification")))
	title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title_label.add_theme_color_override("font_color", accent)
	title_label.add_theme_font_size_override("font_size", 17)
	header.add_child(title_label)

	var turn_created = int(notif.get("turn_created", 0))
	if turn_created > 0:
		var turn_label = Label.new()
		turn_label.text = "T%d" % turn_created
		turn_label.add_theme_color_override("font_color", Color(0.58, 0.58, 0.64, 1))
		turn_label.add_theme_font_size_override("font_size", 12)
		header.add_child(turn_label)

	var body = RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.scroll_active = false
	body.custom_minimum_size = Vector2(DETAIL_PANEL_MIN_WIDTH - 20.0, 0)
	body.text = _build_detail_text(notif)
	vbox.add_child(body)

	var details = notif.get("details", {})

	# ── UX23-A: the primary action, on its own full-width row ──
	# (user: "no way to do it without menuing"). It sits ABOVE the button row
	# rather than as a fourth button in it, for two reasons.
	#
	# The layout one: `expanded_panel.custom_minimum_size` is a FLOOR of 280
	# and the panel has no maximum — `DETAIL_PANEL_MAX_WIDTH` is consumed only
	# by `_position_expanded_panel`, to compute an x offset. So a fourth button
	# beside the existing ~264px of [Reward…]/Keep/Acknowledge does not clip;
	# it makes the panel WIDER than the 340 the placement math assumes, and the
	# panel then hangs off the right edge it was meant to be flush with. (An
	# earlier draft of this comment claimed it would overflow; that was wrong,
	# and the real failure is the quieter one.)
	#
	# The design one: this is not a fourth peer. Full width, above the row,
	# reads as the thing to do — with reviewing, keeping and acknowledging
	# beneath it.
	#
	# Deliberately NOT gated on live AP. The producer cannot know the player's
	# admin actions — `_process_dotation_state` writes the notice BEFORE
	# `advance_turn` refills them, which is precisely the IGR-2 P1 that shipped
	# every AP-priced petition arm permanently disabled — and a button that
	# lies about being unavailable is worse than one whose refusal is honest
	# and free. The label states the price; the executor states the reason.
	if details is Dictionary:
		var action_command = str(details.get("action_command", ""))
		if action_command != "":
			var action_btn = Button.new()
			action_btn.text = str(details.get("action_label", "Act"))
			action_btn.tooltip_text = str(details.get("action_detail", ""))
			action_btn.custom_minimum_size = Vector2(0, 32)
			action_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			action_btn.clip_text = true
			# UX23-A review round: this carried an explicit 13px while the
			# project theme sets Button/font_size = 15, so the "primary" CTA
			# rendered SMALLER than the [Reward…]/[Keep]/[Acknowledge] row
			# beneath it — the type hierarchy inverted against the very intent
			# the comment above states. It takes the theme size now.
			action_btn.add_theme_color_override("font_color", Utils.UI_GOLD)
			action_btn.add_theme_color_override("font_hover_color", Utils.UI_GOLD_BRIGHT)
			action_btn.pressed.connect(_on_action_pressed.bind(action_command))
			vbox.add_child(action_btn)

	var button_row = HBoxContainer.new()
	button_row.alignment = BoxContainer.ALIGNMENT_END
	button_row.add_theme_constant_override("separation", 8)
	vbox.add_child(button_row)

	if details is Dictionary:
		var review_target = str(details.get("review_target", ""))
		var review_label = str(details.get("review_label", "Open Ledger"))
		if review_target != "":
			var review_btn = Button.new()
			review_btn.text = review_label
			review_btn.custom_minimum_size = Vector2(92, 28)
			review_btn.pressed.connect(_on_review_pressed.bind(
				review_target,
				str(details.get("route_id", "")),
				str(details.get("war_id", ""))
			))
			button_row.add_child(review_btn)

	var keep_btn = Button.new()
	keep_btn.text = "Keep"
	keep_btn.custom_minimum_size = Vector2(64, 28)
	keep_btn.pressed.connect(_close_expanded_panel)
	button_row.add_child(keep_btn)

	var dismiss_btn = Button.new()
	dismiss_btn.text = "Acknowledge"
	dismiss_btn.custom_minimum_size = Vector2(92, 28)
	dismiss_btn.pressed.connect(_on_dismiss_pressed.bind(str(notif.get("id", ""))))
	button_row.add_child(dismiss_btn)

	add_child(expanded_panel)
	_position_expanded_panel.call_deferred()


func _build_detail_text(notif: Dictionary) -> String:
	var text = ""
	var message = str(notif.get("message", "")).strip_edges()
	if message != "":
		text += "[color=#d7d7dc]%s[/color]\n" % Utils.humanize_nation_keys_in_text(message)

	var notif_type = str(notif.get("type", ""))
	var details = notif.get("details", {})
	if details is Dictionary:
		match notif_type:
			"coalition_declared":
				text += "\n[color=#e0c060]Leader:[/color] %s\n" % Utils.display_nation_name(str(details.get("leader", "Unknown")))
				text += "[color=#e0c060]Posture:[/color] %s\n" % str(details.get("posture", "Unknown")).capitalize()
				var combined_strength = int(details.get("combined_strength", 0))
				if combined_strength > 0:
					text += "[color=#e0c060]Combined Strength:[/color] %s\n" % Utils.format_number(combined_strength)
				var members = details.get("members", [])
				if members is Array and not members.is_empty():
					var member_names: Array = []
					for member in members:
						member_names.append(Utils.display_nation_name(str(member)))
					text += "[color=#e0c060]Members:[/color] %s\n" % ", ".join(member_names)
			"diplomatic_proposal_result":
				text += "\n[color=#e0c060]Nation:[/color] %s\n" % Utils.display_nation_name(str(details.get("target_nation", "Unknown")))
				text += "[color=#e0c060]Proposal:[/color] %s\n" % str(details.get("proposal_type", "Diplomatic Action"))
				text += "[color=#e0c060]Outcome:[/color] %s\n" % str(details.get("outcome", "Unknown")).capitalize()
				var feedback = str(details.get("feedback", "")).strip_edges()
				if feedback != "":
					text += "\n[color=#8faed6]Talleyrand:[/color] \"%s\"\n" % feedback
			"diplomatic_proposal":
				text += "\n[color=#8faed6]The diplomatic packet waits in Envoys for review.[/color]\n"

	return text.strip_edges()


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


func _on_action_pressed(command: String):
	"""UX23-A: the row settles what it announces. Close first — the terminal
	echoes the order and the response re-renders the rail, so leaving the
	panel open would show it over its own stale copy."""
	_close_expanded_panel()
	notification_action_requested.emit(command)


func _on_review_pressed(review_target: String, route_id: String = "", war_id: String = ""):
	_close_expanded_panel()
	notification_review_requested.emit(review_target, route_id, war_id)


func dismiss_all():
	_close_expanded_panel()
	current_notifications = []
	update_notifications([])
	if api_client:
		api_client.dismiss_all_notifications(func(_response): pass)

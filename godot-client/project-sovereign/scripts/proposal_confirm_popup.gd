extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Proposal Confirm Popup (Proposal Flow Bugfix)
# =============================================================================
# Displays when the player initiates a diplomatic proposal via the Diplomacy
# Button (F1). Shows Talleyrand's proposed terms with acceptance estimate,
# harshness, DP cost, and action buttons built from dialogue options.
# =============================================================================

signal choice_made(action: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var button_container = $PanelContainer/VBoxContainer/ButtonContainer
# GT-Slice-3 (Guided Terms §9) + UX-5: the per-court settlement table lives in
# its own RichTextLabel inside a ScrollContainer so the inline `Add demand`
# expansion scrolls instead of growing the popup unbounded (the full-1805
# court-count horizon). The footer label carries the post-table sections.
@onready var per_court_scroll = $PanelContainer/VBoxContainer/PerCourtScroll
@onready var per_court_table = $PanelContainer/VBoxContainer/PerCourtScroll/PerCourtTable
@onready var footer_label = $PanelContainer/VBoxContainer/FooterLabel

var current_data: Dictionary = {}
# GT-Slice-3 client-side expansion state for the guided per-court rows.
# Reset on every show_dialogue (each backend restage re-mounts fresh data;
# the §3.3 lead-group defaults re-apply).
var _add_demand_expanded: Dictionary = {}
var _trailing_group_expanded: Dictionary = {}
var _suggestion_options_expanded: Dictionary = {}

const COLOR_GOLD = "#d9c08c"
const COLOR_DIMMED = "#808080"
const COLOR_RED = "#e04040"
# GT-Slice-3: client-side magnitude step for the per-line gold controls
# (mirrors the backend SETTLEMENT_DIAL_GOLD_STEP; the server clamps and
# revalidates every value — this is presentation-side convenience only).
const DEMAND_GOLD_MAGNITUDE_STEP = 100

func _ready():
	hide()
	if per_court_table:
		per_court_table.meta_clicked.connect(_on_per_court_meta_clicked)

func _should_label_ask_later(dtype: String, action_str: String, original_label: String) -> bool:
	if dtype not in ["proposal_confirm", "proposal_execute", "proposal_options", "pushback_confirm"]:
		return false
	if action_str == "reconsider":
		return true
	if action_str == "dismiss" and original_label in ["Dismiss", "Not now", "Reconsider"]:
		return true
	return false

func show_dialogue(data: Dictionary):
	"""Display proposal confirmation popup with terms and options."""
	current_data = data
	var dtype = data.get("type", "proposal_confirm")
	var bbcode = ""
	match dtype:
		"mission":
			bbcode = _build_mission_content(data)
		"feasibility":
			bbcode = _build_feasibility_content(data)
		"advisory", "advisory_threat", "advisory_recommendation":
			bbcode = _build_advisory_content(data)
		"war_purpose_selection":
			bbcode = _build_war_purpose_content(data)
		"force_declare_war_confirmation":
			bbcode = _build_war_confirm_content(data)
		"conflict_alert":
			bbcode = _build_conflict_alert_content(data)
		"ultimatum_confirm", "ultimatum_demand_wizard":
			bbcode = _build_ultimatum_content(data)
		"settlement_confirm":
			bbcode = _build_settlement_content(data)
		"settlement_scope_replace_confirm":
			bbcode = _build_settlement_scope_replace_content(data)
		# SC-5 reversal commit 2 (Slice G1): incoming AI settlement
		# offers render with accepting-side framing — the player is
		# reading a draft authored by a foreign court, so the popup
		# uses the Voice Bible §16.1 incoming-offer arrival families.
		# SC-5R-2: the "open the offer" action is now labelled Review
		# Settlement Offer to match its behavior (staged review, not
		# immediate ratification).
		"incoming_settlement_offer":
			bbcode = _build_incoming_settlement_offer_content(data)
		"ally_settlement_petition":
			bbcode = _build_ally_settlement_petition_content(data)
		_:
			if data.has("war_context_snapshot"):
				bbcode = _build_peace_preview_content(data)
			else:
				bbcode = _build_content(data)
	content_label.text = ""
	content_label.append_text(bbcode)

	# GT-Slice-3 + UX-5: the settlement_confirm surface renders in three
	# regions — header (ContentLabel), the scrollable per-court table
	# (PerCourtScroll/PerCourtTable), and the post-table footer. Every other
	# dialogue type keeps the single-label layout.
	var is_settlement_table = (dtype == "settlement_confirm")
	_add_demand_expanded = {}
	_trailing_group_expanded = {}
	_suggestion_options_expanded = {}
	if per_court_scroll:
		per_court_scroll.visible = is_settlement_table
	if footer_label:
		footer_label.visible = is_settlement_table
	if is_settlement_table:
		# Gate-4 G4F-3: the treasury / narration / advisory / voice-beat
		# preamble renders in the HEADER (above the scroll), so the scroll
		# viewport holds only the court rows — at 2 courts the second
		# court and the Add demand affordances were below the fold and the
		# guided authoring surface read as missing.
		content_label.append_text(_build_settlement_table_preamble(data))
		_render_per_court_table()
		if footer_label:
			footer_label.text = ""
			footer_label.append_text(_build_settlement_footer(data))

	# Create buttons dynamically from dialogue options
	_clear_buttons()
	var options = data.get("options", [])
	var is_options_picker = (dtype == "proposal_options")
	var idx = 1
	for opt in options:
		var btn = Button.new()
		var original_label = str(opt.get("label", "???"))
		var original_tooltip = str(opt.get("description", ""))
		var available = bool(opt.get("available", true))
		var disabled_reason = str(opt.get("disabled_reason", original_tooltip))
		btn.text = original_label
		btn.tooltip_text = original_tooltip
		btn.custom_minimum_size = Vector2(160, 45)
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.add_theme_font_size_override("font_size", 14)
		btn.disabled = not available
		if not available:
			btn.tooltip_text = disabled_reason if disabled_reason != "" else "Unavailable"
			btn.add_theme_color_override("font_disabled_color", Color(COLOR_DIMMED))
		var action_str = opt.get("action", "dismiss")
		if _should_label_ask_later(dtype, action_str, original_label):
			btn.text = "Not Now"
			btn.tooltip_text = "Close this for now — offer lapses at end of turn."
		# For proposal_options, bind 1-based index so backend can parse as int
		if is_options_picker and action_str == "expand_options":
			action_str = str(idx)
		btn.pressed.connect(_on_option_selected.bind(action_str))
		button_container.add_child(btn)
		idx += 1

	# Re-front Slice 2: per-court row affordances (holdout Ease/Drop, focused
	# dials) and conversational coverage prompts are NOT in options[] — they ride
	# on the per-court table and the coverage suggestion list. Render them as
	# clickable buttons that carry their own structured params (scope / nation).
	if dtype == "settlement_confirm":
		_add_settlement_tier2_buttons(data)

	show()

func _add_settlement_tier2_buttons(data: Dictionary):
	# UX-2 (GT-Slice-3): REVIEW is a frozen staged-decision surface — no
	# dial / holdout / coverage affordances render there. The backend already
	# withholds them server-side (rows carry empty lists outside PROPOSE);
	# this client gate keeps the contract explicit at the render layer too.
	if str(data.get("dialogue_mode", "REVIEW")) != "PROPOSE":
		return
	var affordances: Array = []
	var per_court = data.get("per_court_acceptance", [])
	if per_court is Array:
		for row in per_court:
			if not (row is Dictionary):
				continue
			# Focused dials ("Press <court>" / "Ease <court>") ride on every
			# dialable row; holdout Ease/Drop ride on holdout rows.
			var dial_actions = row.get("dial_actions", [])
			if dial_actions is Array:
				for da in dial_actions:
					if da is Dictionary and str(da.get("action", "")) != "":
						affordances.append(da)
			var holdout_actions = row.get("holdout_actions", [])
			if holdout_actions is Array:
				for ha in holdout_actions:
					if ha is Dictionary and str(ha.get("action", "")) != "":
						affordances.append(ha)
	var coverage_suggestions = data.get("coverage_add_suggestions", [])
	if coverage_suggestions is Array:
		for cs in coverage_suggestions:
			if cs is Dictionary and str(cs.get("action", "")) != "":
				affordances.append(cs)
	for aff in affordances:
		var btn = Button.new()
		btn.text = str(aff.get("label", "???"))
		btn.tooltip_text = str(aff.get("description", ""))
		btn.custom_minimum_size = Vector2(160, 40)
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.add_theme_font_size_override("font_size", 13)
		btn.add_theme_color_override("font_color", Color("#80b0e0"))
		btn.pressed.connect(_on_settlement_tier2_affordance.bind(aff))
		button_container.add_child(btn)

func _build_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "Unknown")
	var proposal_display = data.get("proposal_type_display", "Proposal")

	var bbcode = ""
	bbcode += "[b]DIPLOMATIC PROPOSAL — %s[/b]\n\n" % target

	# BPH-A: Annotated terms grouped by direction
	var annotated = data.get("annotated_terms", [])
	if not annotated.is_empty():
		bbcode += _build_annotated_terms_section(annotated)
	else:
		# Legacy fallback: flat terms summary
		var terms = data.get("proposal_terms_summary", [])
		if not terms.is_empty():
			bbcode += "[b]Terms Talleyrand proposes:[/b]\n"
			for t in terms:
				bbcode += "  [color=#e0c070]•[/color] %s\n" % str(t)
			bbcode += "\n"

	# Harshness
	var harshness_label = data.get("harshness_label", "")
	if harshness_label:
		var h_color = "#80c080"  # green for Low
		if harshness_label == "Moderate":
			h_color = "#e0e060"
		elif harshness_label == "High":
			h_color = "#e09040"
		elif harshness_label == "Very High":
			h_color = "#e04040"
		bbcode += "Harshness: [color=%s]%s[/color]\n" % [h_color, harshness_label]

	# Acceptance estimate
	var acceptance = data.get("acceptance_estimate", -1)
	var outcome = data.get("acceptance_outcome", "")
	if acceptance >= 0:
		var a_color = "#e04040"  # red
		if acceptance >= 50:
			a_color = "#80c080"  # green
		elif acceptance >= 30:
			a_color = "#e0e060"  # yellow
		bbcode += "Acceptance estimate: [color=%s]~%d%%[/color] (%s)\n" % [a_color, acceptance, outcome]
		var hint = data.get("acceptance_hint", "")
		if hint:
			bbcode += "[color=#a0a0a0]%s[/color]\n" % hint

	# DP cost
	var dp_cost = data.get("dp_cost", -1)
	if dp_cost >= 0:
		bbcode += "DP cost: [color=#80a0d0]%d[/color]\n" % dp_cost

	var warnings = data.get("warnings", [])
	if not warnings.is_empty():
		bbcode += "\n[b]Political Context:[/b]\n"
		var shown = mini(warnings.size(), 2)
		for idx in range(shown):
			var warning = warnings[idx]
			var severity = str(warning.get("severity", "low"))
			var color = "#e0c070"
			if severity == "critical":
				color = "#e04040"
			elif severity == "high":
				color = "#e09040"
			elif severity == "medium":
				color = "#e0c060"
			bbcode += "  [color=%s]•[/color] %s\n" % [color, str(warning.get("text", ""))]
		if warnings.size() > shown:
			bbcode += "  [color=#a0a0a0]+%d more diplomatic concern%s[/color]\n" % [
				warnings.size() - shown,
				"" if (warnings.size() - shown) == 1 else "s",
			]

	# Talleyrand commentary
	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "\n[color=#c0b080][i]\"%s\"[/i][/color]\n" % ttext

	return bbcode


func _build_settlement_content(data: Dictionary) -> String:
	var war_label = str(data.get("war_label", data.get("war_id", "Settlement")))
	var scope = str(data.get("coverage_scope_display", data.get("war_scope_display", "Settlement review")))
	var review = data.get("review_sections", {})
	var sections = review.get("sections", {}) if review is Dictionary else {}
	var bbcode = ""

	# PF-1 (D3): a failed settlement action re-mounts this popup on its
	# unchanged dialogue with the failure reason attached by main.gd. Render
	# it as the first line so a blocked dial / Submit / Ratify never reads
	# as a silent no-op blink.
	var transient_error = _safe_str(data.get("transient_error_display"))
	if transient_error != "":
		bbcode += "[color=#e0a040]⚠ %s[/color]\n\n" % transient_error

	# SC-17: Humanize the malformed-payload guard. Players never need to
	# see raw structured key names; the voice-resolved talleyrand_text
	# below stays mounted while the player escapes via Back Out / war
	# detail.
	var missing = []
	for key in ["war_label", "review_sections", "covered_enemy_display_chips"]:
		if not data.has(key):
			missing.append(key)
	if missing.size() > 0 and str(data.get("type", data.get("dialogue_type", ""))) == "settlement_confirm":
		bbcode += "[color=#e04040]We could not prepare this settlement review. Reopen from war detail.[/color]\n\n"

	var awe = review.get("awe_tag_displays", data.get("awe_tag_displays", [])) if review is Dictionary else []
	if awe is Array and awe.size() > 0:
		bbcode += "[color=#e0c070][b]" + str(awe[0]) + "[/b][/color]\n"

	# SC-19: Settlement heading routes through the backend-resolved
	# settlement voice family (talleyrand_text). When ratification is
	# blocked the backend supplies blocked-banner copy that suppresses
	# "Will they accept?" framing; otherwise the live-review voice line
	# carries acceptance band + top blocker. Foreign-court / observer
	# settlements get their own chancery voice via the same field.
	var accepting_side = str(data.get("accepting_side", ""))
	var leaders = data.get("staged_leaders", {})
	var accepting_leader = "their leader"
	if leaders is Dictionary and accepting_side != "":
		accepting_leader = str(leaders.get(accepting_side, accepting_leader))
	var heading_voice = str(data.get("talleyrand_text", ""))
	var can_ratify_now = bool(data.get("can_ratify", true))
	if heading_voice != "":
		bbcode += "[b][color=#e0c070]%s[/color][/b]\n" % heading_voice
	elif can_ratify_now:
		bbcode += "[b][color=#e0c070]Settlement of %s — ready for ratification[/color][/b]\n" % war_label
	else:
		bbcode += "[b][color=#e04040]This settlement cannot be ratified now.[/color][/b]\n"
	bbcode += "[color=#a0a0a8]%s - %s[/color]\n" % [war_label, scope]

	# UX-2 (GT-Slice-3): REVIEW reads as a staged-decision surface, visually
	# distinct from the PROPOSE authoring surface — the terms are frozen, the
	# blockers are promoted to the top, and no authoring affordances render
	# anywhere below (the backend already withholds them server-side).
	var dialogue_mode = str(data.get("dialogue_mode", "REVIEW"))
	if dialogue_mode == "REVIEW":
		bbcode += "[color=#80a0d0][b]STAGED FOR REVIEW[/b] — the terms are frozen. Ratify, revise, or return to shaping.[/color]\n"
		if not can_ratify_now:
			var promoted_blocker = str(data.get("ratify_blocked_reason", ""))
			if promoted_blocker != "":
				bbcode += "[color=#e0a040]▸ Blocked: %s[/color]\n" % promoted_blocker
			var overall_review = data.get("overall_acceptance", {})
			if overall_review is Dictionary:
				var holdouts = overall_review.get("holdout_courts", [])
				if holdouts is Array and holdouts.size() > 0:
					bbcode += "[color=#e0a040]▸ Holding out: %s[/color]\n" % ", ".join(PackedStringArray(holdouts))

	var chips = data.get("covered_enemy_display_chips", data.get("covered_enemy_participants", []))
	if chips is Array and chips.size() > 0:
		bbcode += "[b]Covered enemies:[/b] " + ", ".join(PackedStringArray(chips)) + "\n"
	var uncovered = data.get("uncovered_enemy_display_chips", review.get("uncovered_enemy_display_chips", [])) if review is Dictionary else []
	if uncovered is Array and uncovered.size() > 0:
		bbcode += "[color=#e0a040][b]Still at war:[/b] " + ", ".join(PackedStringArray(uncovered)) + "[/color]\n"

	# The per-court table itself renders into the scrollable PerCourtTable
	# region (GT-Slice-3 / UX-5 — see _render_per_court_table); the post-table
	# sections render into the footer region (_build_settlement_footer).
	return bbcode


func _build_settlement_footer(data: Dictionary) -> String:
	var review = data.get("review_sections", {})
	var sections = review.get("sections", {}) if review is Dictionary else {}
	var bbcode = ""

	var ally_petitions = data.get("ally_petitions", [])
	if ally_petitions is Array and ally_petitions.size() > 0:
		bbcode += "[b]Allied petitions[/b]\n"
		for petition in ally_petitions:
			if not petition is Dictionary:
				continue
			var ally = str(petition.get("ally_nation", "An ally"))
			var ally_voice = str(petition.get("ally_voice", ""))
			if ally_voice != "":
				bbcode += "  [color=#e0c070]*[/color] [i]\"" + ally_voice + "\"[/i]\n"
			else:
				bbcode += "  [color=#e0c070]*[/color] " + ally + " petitions over settlement scope.\n"
		bbcode += "\n"

	var allies = sections.get("allies", {}) if sections is Dictionary else {}
	if allies is Dictionary:
		var rows = allies.get("rows", [])
		if rows is Array and rows.size() > 0:
			bbcode += "[b]Allies and Standing[/b]\n"
			for row in rows:
				if not row is Dictionary:
					continue
				var nation = str(row.get("nation", "?"))
				var standing = str(row.get("standing_display", row.get("standing", "Standing").replace("_", " ").capitalize()))
				var side_label = str(row.get("side_label", row.get("side", "")))
				var stamps = []
				if side_label != "":
					stamps.append(side_label)
				if bool(row.get("is_leader", false)):
					stamps.append("war leader")
				if bool(row.get("is_beneficiary", false)):
					stamps.append("rewarded")
				var stamp_text = ""
				if stamps.size() > 0:
					stamp_text = " [color=#808080](" + ", ".join(PackedStringArray(stamps)) + ")[/color]"
				bbcode += "  [color=#e0c070]*[/color] %s - %s%s\n" % [nation, standing, stamp_text]
			var overflow = int(allies.get("overflow_count", 0))
			if overflow > 0:
				bbcode += "  [color=#808080]+%d more participants in the ledger[/color]\n" % overflow
			bbcode += "\n"

	var acceptance = data.get("acceptance_display", sections.get("acceptance", {}))
	if acceptance is Dictionary and not acceptance.is_empty():
		var band = str(acceptance.get("band_display", acceptance.get("band", "Review").replace("_", " ").capitalize()))
		var band_code = str(acceptance.get("band", "")).to_lower()
		# Color decisions are made off the raw enum band code, never the
		# humanized `band` string — that way a future tweak to
		# ACCEPTANCE_BAND_DISPLAY wording does not silently swap the colour.
		var color = "#e04040"
		if band_code in ["accept", "acceptable"]:
			color = "#80c080"
		elif band_code == "near_acceptable":
			color = "#e0e060"
		bbcode += "[b]Acceptance[/b]\n"
		# SC-15b: structurally blocked acceptance must not show a
		# numeric `0 / 50` line that reads like a tunable score gap.
		# The backend payload sets total/threshold to null in this
		# case and supplies blocker_display + band_display="Blocked".
		if band_code == "blocked" or acceptance.get("total") == null or acceptance.get("threshold") == null:
			var blocker_display = str(acceptance.get("blocker_display", ""))
			bbcode += "  [color=%s]%s[/color]" % [color, band]
			if blocker_display != "":
				bbcode += " — " + blocker_display
			bbcode += "\n"
		else:
			# SC-20: render exactly one acceptance label per band. The
			# legacy " (phrase)" suffix that produced "Unlikely (Likely
			# to reject)" duplicates is gone; band_display is the single
			# player-facing label per band.
			var total = int(acceptance.get("total", 0))
			var threshold = int(acceptance.get("threshold", 50))
			bbcode += "  [color=%s]%d / %d - %s[/color]\n" % [color, total, threshold, band]
		var top_blocker = str(acceptance.get("top_blocker_display", ""))
		var top_value = str(acceptance.get("top_blocker_value_display", ""))
		# May 24, 2026 audit punch list Tier 3 P3 polish: when the
		# acceptance band reads "Acceptable" and the total comfortably
		# exceeds threshold (>= +10), suppress the "Top pressure" line
		# so the popup does not read as conflicting with its own verdict.
		# The line still renders when the score is close to threshold
		# (the player needs to know which component is the swing factor),
		# in non-accept bands, and on structurally blocked acceptance
		# (covered separately above).
		var suppress_top_pressure = false
		if band_code in ["accept", "acceptable"]:
			var current_total = int(acceptance.get("total", 0))
			var current_threshold = int(acceptance.get("threshold", 50))
			if current_total - current_threshold >= 10:
				suppress_top_pressure = true
		if top_blocker != "" and not suppress_top_pressure:
			bbcode += "  Top pressure: " + top_blocker
			if top_value != "":
				bbcode += " " + top_value
			bbcode += "\n"
		var ratify_blocked_reason = str(data.get("ratify_blocked_reason", ""))
		if ratify_blocked_reason != "":
			bbcode += "  [color=#e0a040]" + ratify_blocked_reason + "[/color]\n"
		# May 24, 2026 audit punch list Tier 2: render the
		# `terminal_recovery_copy` field after `ratify_blocked_reason`
		# so the chancery recovery line authored by the backend via
		# `settlement_no_alternative_route_chancery` actually reaches
		# the player. Backend emits empty string when ratification is
		# available or War Detail recovery is actionable; this render
		# is therefore a no-op outside the terminal-stale state.
		var terminal_recovery_copy = str(data.get("terminal_recovery_copy", ""))
		if terminal_recovery_copy != "":
			bbcode += "  [color=#a0a0a0][i]" + terminal_recovery_copy + "[/i][/color]\n"
		bbcode += "\n"

	var warnings = sections.get("warnings", {}) if sections is Dictionary else {}
	if warnings is Dictionary:
		var inline_warns = warnings.get("inline", [])
		if inline_warns is Array and inline_warns.size() > 0:
			bbcode += "[b]Warnings[/b]\n"
			for warning in inline_warns:
				if not warning is Dictionary:
					continue
				var severity = str(warning.get("severity", "WARNING"))
				var color = "#e04040" if severity == "HARD_STOP" else "#e0a040"
				var label = str(warning.get("code_display", warning.get("code", "Concern").replace("_", " ").capitalize()))
				var detail = str(warning.get("detail", ""))
				bbcode += "  [color=%s]*[/color] %s" % [color, label]
				if detail != "":
					bbcode += " - " + detail
				bbcode += "\n"
			var overflow_warns = warnings.get("overflow", [])
			if overflow_warns is Array and overflow_warns.size() > 0:
				bbcode += "  [color=#808080]+%d more warnings in the ledger[/color]\n" % overflow_warns.size()
			bbcode += "\n"

	var terms = sections.get("terms", {}) if sections is Dictionary else {}
	if terms is Dictionary:
		var term_rows = terms.get("rows", [])
		if term_rows is Array and term_rows.size() > 0:
			bbcode += "[b]Terms[/b]\n"
			for term in term_rows:
				if term is Dictionary:
					var label = str(term.get("display_label", term.get("type_display", "Settlement term")))
					var role = str(term.get("role_display", term.get("role", "")))
					if role != "":
						label = role + ": " + label
					bbcode += "  [color=#e0c070]*[/color] %s\n" % label
			var term_overflow = int(terms.get("overflow_count", 0))
			if term_overflow > 0:
				bbcode += "  [color=#808080]+%d more terms in the ledger[/color]\n" % term_overflow
			bbcode += "\n"

	# SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 Concession Baseline:
	# when `concession_baseline_visible=true` the dialogue carries a
	# deterministic draft + humanized reasoning. The popup renders a
	# first-frame primary-weighted note describing the suggested
	# Talleyrand concession; the actual "Generate concession baseline"
	# action button is rendered alongside the existing options by the
	# editor surface. Click-time revalidation re-POSTs the preview and
	# only applies the baseline when the predicate still holds.
	if bool(data.get("concession_baseline_visible", false)) and not bool(data.get("surrender_preset", false)):
		var baseline = data.get("concession_baseline", {})
		if baseline is Dictionary:
			var reasoning = str(baseline.get("reasoning", ""))
			if reasoning != "":
				bbcode += "[color=#80c080][b]Talleyrand's concession draft:[/b] %s[/color]\n" % reasoning
	# Surrender preset banner: a single banner covers both the editor-side
	# "Talleyrand is offering a surrender draft" affordance and the
	# staged-outcome "surrender draft applied at ratification" state.
	# May 24, 2026 audit punch list Tier 3 P2 collapsed the previous
	# double-banner cluster (reasoning banner + outcome banner) into one
	# labeled block so the popup does not advertise the same draft twice.
	var surrender_preset_staged = bool(data.get("surrender_preset", false))
	var surrender_preset_visible = bool(data.get("surrender_preset_visible", false))
	if surrender_preset_staged or surrender_preset_visible:
		var preset_reasoning = ""
		var preset_payload = data.get("surrender_preset_payload", {})
		if preset_payload is Dictionary:
			preset_reasoning = str(preset_payload.get("reasoning", ""))
		if surrender_preset_staged:
			var staged_line = "[color=#d09080][b]Surrender draft[/b] — dependency consequence applied at ratification."
			if preset_reasoning != "":
				staged_line += " " + preset_reasoning
			staged_line += "[/color]\n"
			bbcode += staged_line
		else:
			if preset_reasoning != "":
				bbcode += "[color=#d0a080][b]Talleyrand's surrender draft:[/b] %s[/color]\n" % preset_reasoning
	# White peace banner: when the dialogue is staged with
	# `white_peace=true` the popup labels the outcome explicitly.
	if bool(data.get("white_peace", false)):
		bbcode += "[color=#a0a0d0][b]White Peace[/b] — no terms will be exchanged.[/color]\n"
	# SETTLEMENT_UI_CLEANUP_SPEC v0.30 G2-Slice-9 SC-33: Recurring-gold
	# draft payloads expose the finite payer / recipient / amount /
	# duration before the player clicks the structured authoring action.
	if bool(data.get("recurring_gold_preset_visible", false)):
		var recurring_payload = data.get("recurring_gold_preset_payload", {})
		if recurring_payload is Dictionary:
			var recurring_reasoning = str(recurring_payload.get("reasoning", ""))
			if recurring_reasoning != "":
				bbcode += "[color=#80b8c0][b]Talleyrand's recurring-gold draft:[/b] %s[/color]\n" % recurring_reasoning

	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n" % ttext
	return bbcode

func _safe_str(v) -> String:
	# Coalesce JSON null -> "" so a null field never renders as Godot's literal
	# "<null>". `row.get(key, "")` returns the present-but-null value (the default
	# only applies to MISSING keys), and str(null) == "<null>", which leaked into
	# the per-court table on first paint (delta_display is null before any dial).
	return "" if v == null else str(v)

func _render_per_court_table():
	# GT-Slice-3 / UX-5: (re)paint the scrollable per-court table region from
	# current_data. Client-side expansion toggles re-enter here without a
	# round trip; backend mutations re-mount the whole popup instead. The
	# preamble (G4F-3) lives in the header label, so toggles never repaint it.
	if per_court_table == null:
		return
	per_court_table.text = ""
	per_court_table.append_text(_build_settlement_per_court_block(current_data))


func _build_settlement_table_preamble(data: Dictionary) -> String:
	# Gate-4 G4F-3: the table preamble — treasury line, table narration,
	# targeted-posture advisory, and one-shot authoring voice beats — renders
	# in the HEADER above PerCourtScroll so the scroll viewport spends its
	# whole height on court rows (at 2 courts the second court and the Add
	# demand affordances sat below the fold and read as missing).
	var per_court = data.get("per_court_acceptance", [])
	if not (per_court is Array) or per_court.size() == 0:
		return ""
	var dialogue_mode = str(data.get("dialogue_mode", "REVIEW"))
	var authoring_surface = (dialogue_mode == "PROPOSE")
	var bbcode = ""
	# G4F-7: the carry verdict LEADS the header — the one full-deal fact
	# (carries iff every court reaches the threshold), with per-court score
	# attribution. The per-court integers alone read as "high acceptance"
	# in the live smoke while both courts were holdouts.
	var overall_verdict = data.get("overall_acceptance", {})
	if overall_verdict is Dictionary:
		var verdict_line = _safe_str(overall_verdict.get("carry_verdict_display"))
		if verdict_line != "":
			var verdict_color = "#e05050"
			if bool(overall_verdict.get("carries", false)):
				verdict_color = "#80c080"
			bbcode += "[b][color=%s]%s[/color][/b]\n" % [verdict_color, verdict_line]
	# Guided Terms §3.4 (GT-A1): the shared-treasury allocation line, one pool
	# across every court's France-paid gold. PROPOSE-only payload.
	var treasury = data.get("treasury_line", {})
	if authoring_surface and treasury is Dictionary and treasury.size() > 0:
		bbcode += "[color=#d9c08c][b]Treasury[/b] %s gold: committed %s / reserve %s / remaining %s[/color]\n" % [
			Utils.format_number(int(treasury.get("treasury", 0))),
			Utils.format_number(int(treasury.get("committed", 0))),
			Utils.format_number(int(treasury.get("reserve", 0))),
			Utils.format_number(int(treasury.get("remaining", 0))),
		]
	var narration = _safe_str(data.get("multi_court_table_narration"))
	if narration != "":
		bbcode += "[i][color=#c0c0c8]%s[/color][/i]\n" % narration
	# Re-front Slice 2 / OQ#1: Talleyrand's voice-only targeted-posture advice
	# (PF-1/DC-2 + OQ-6: carries the binding-constraint + budget-bound
	# recommendation voice when the treasury binds).
	var advisory = _safe_str(data.get("targeted_posture_advisory"))
	if advisory != "":
		bbcode += "[i][color=#c0b080]\"%s\"[/color][/i]\n" % advisory
	# GT-Slice-V: one-shot authoring voice beats from the last mutation — the
	# DC-4 concede-court caution (Talleyrand) and the affected court's
	# named-diplomat reaction. Dropped by the next restage.
	var voice_beats = data.get("authoring_voice_beats", [])
	if voice_beats is Array:
		for beat in voice_beats:
			if not (beat is Dictionary):
				continue
			var beat_line = _safe_str(beat.get("line"))
			if beat_line == "":
				continue
			if str(beat.get("kind", "")) == "talleyrand_caution":
				bbcode += "[i][color=#e0c070]\"%s\"[/color][/i]\n" % beat_line
			else:
				bbcode += "[i][color=#c0c0c8]%s[/color][/i]\n" % beat_line
	return bbcode

func _build_settlement_per_court_block(data: Dictionary) -> String:
	# Re-front Slice 1: render the per-court acceptance table (PROPOSE + REVIEW).
	# GT-Slice-3 (Guided Terms §3.1-§3.3): on the PROPOSE authoring surface each
	# row additionally renders its current demand lines (per-line Remove +
	# magnitude controls), the inline `Add demand` expansion fed by
	# `demand_suggestions[]`, the §3.4 treasury line, and the REFRONT-9 focused
	# component breakdown. REVIEW renders the same table frozen (UX-2 — no
	# links, no authoring affordances).
	var per_court = data.get("per_court_acceptance", [])
	if not (per_court is Array) or per_court.size() == 0:
		return ""
	var dialogue_mode = str(data.get("dialogue_mode", "REVIEW"))
	var authoring_surface = (dialogue_mode == "PROPOSE")
	var bbcode = ""
	bbcode += "[b]The table[/b]\n"
	var focused_court = _safe_str(data.get("focused_court"))
	var court_index = -1
	for row in per_court:
		court_index += 1
		if not (row is Dictionary):
			continue
		var nation = str(row.get("nation", "?"))
		var band_display = _safe_str(row.get("band_display"))
		if band_display == "":
			band_display = _safe_str(row.get("band"))
		var direction = _safe_str(row.get("direction_summary"))
		var total = row.get("total", null)
		var total_text = ""
		if total != null:
			# G4F-7: threshold-honest framing — "44/50" makes the ratify bar
			# visible in the number itself instead of a bare integer.
			total_text = " (%d/%d)" % [int(total), int(row.get("threshold", 50))]
		var is_focused = (focused_court != "" and nation == focused_court)
		# REFRONT-9 (OQ-5/GT-A4): on PROPOSE the court name is the focus
		# trigger — clicking it round-trips presentation-only
		# `settlement_focus_court` and the focused row expands into the full
		# component breakdown below. Clicking again clears the focus.
		var name_cell = "[b]%s[/b]" % nation
		if authoring_surface:
			name_cell = "[url=focus:%d][b]%s[/b] %s[/url]" % [
				court_index, nation, "▾" if is_focused else "▸",
			]
		bbcode += "  [color=#e0c070]*[/color] %s - %s%s" % [name_cell, band_display, total_text]
		if direction != "":
			bbcode += " [color=#a0a0a8]%s[/color]" % direction
		bbcode += "\n"
		var blocker = _safe_str(row.get("top_blocker_display"))
		if blocker != "":
			bbcode += "      [color=#e0a040]Blocker: %s[/color]\n" % blocker
		# Re-front Slice 2 / §11.2: the live band delta after a dial (presentation
		# only — it never feeds the scored result). Null on first paint (no
		# previous band) — _safe_str coalesces so it never prints "<null>".
		var delta = _safe_str(row.get("delta_display"))
		if delta != "":
			bbcode += "      [color=#80b0e0]%s[/color]\n" % delta
		var voice = _safe_str(row.get("voice_line"))
		if voice != "":
			bbcode += "      [i]%s[/i]\n" % voice
			# Rendered as real clickable buttons by _add_settlement_tier2_buttons
			# (self-labeled, e.g. "Ease Britain") -- intentionally NOT echoed inline.
			# The old blue "Ease X | Drop X" body text was inert (looked clickable,
			# did nothing) and duplicated the working buttons; Gate-4 smoke finding.
		if is_focused:
			bbcode += _build_focused_component_breakdown(row)
		if authoring_surface:
			bbcode += _build_court_authoring_lines(row, court_index)
	var overall = data.get("overall_acceptance", {})
	if overall is Dictionary:
		var summary = str(overall.get("summary_display", ""))
		if summary != "":
			var carries = bool(overall.get("carries", false))
			var color = "#60c060" if carries else "#e0a040"
			bbcode += "[b][color=%s]%s[/color][/b]\n" % [color, summary]
	# Re-front UX follow-up: when the package does not carry yet, the PROPOSE
	# surface spells out the next step (ease until every court accepts, THEN
	# Submit) so the player does not submit into a blocked, no-Ratify REVIEW.
	# Backend emits this ONLY on PROPOSE-while-not-carrying.
	var carry_hint = _safe_str(data.get("propose_carry_hint"))
	if carry_hint != "":
		bbcode += "[color=#e0a040]▸ %s[/color]\n" % carry_hint
	bbcode += "\n"
	return bbcode


func _build_focused_component_breakdown(row: Dictionary) -> String:
	# REFRONT-9 (re-front spec §14 row, re-owned by Guided Terms GT-A4): the
	# focused court's expanded row renders the FULL component table — all ten
	# acceptance components incl. concession_credit — from the row's
	# `component_breakdown` (already computed by the score pass; the focus
	# trigger stays presentation-only).
	var breakdown = row.get("component_breakdown", [])
	if not (breakdown is Array) or breakdown.size() == 0:
		return ""
	var nation = str(row.get("nation", "?"))
	var bbcode = "      [b]Why %s stands here[/b]\n" % nation
	for entry in breakdown:
		if not (entry is Dictionary):
			continue
		var value = int(entry.get("value", 0))
		var color = "#80c080" if value > 0 else ("#e08060" if value < 0 else "#a0a0a8")
		bbcode += "        [color=%s]%s %s[/color]\n" % [
			color,
			_safe_str(entry.get("value_display")),
			_safe_str(entry.get("component_display")),
		]
	return bbcode


func _build_court_authoring_lines(row: Dictionary, court_index: int) -> String:
	# GT-Slice-3 (Guided Terms §3.1/§3.3): the per-court authoring block —
	# current demand/offer lines with per-line Remove + magnitude controls,
	# then the inline `Add demand` expansion. All affordances are [url] metas
	# resolved by _on_per_court_meta_clicked; direction is fixed per option
	# server-side, so no identity ever crosses this surface.
	var bbcode = ""
	var nation = str(row.get("nation", "?"))
	var current_demands = row.get("current_demands", [])
	if current_demands is Array:
		var line_index = -1
		for line in current_demands:
			line_index += 1
			if not (line is Dictionary):
				continue
			var tag = _safe_str(line.get("direction_tag"))
			var tag_color = "#e09040" if tag == "Demanded" else ("#80c0a0" if tag == "Conceded" else "#e0c070")
			var authored_suffix = ""
			if str(line.get("authored_by", "")) == "player":
				authored_suffix = " [color=#808080](yours)[/color]"
			bbcode += "      [color=%s]%s[/color] · %s%s" % [
				tag_color, tag, _safe_str(line.get("line_display")), authored_suffix,
			]
			var magnitude = line.get("magnitude", null)
			if magnitude is Dictionary:
				bbcode += "  [url=mag:%d:%d:amount:-][-][/url][url=mag:%d:%d:amount:+][+][/url]" % [
					court_index, line_index, court_index, line_index,
				]
				if magnitude.has("turns"):
					bbcode += " [color=#a0a0a8]turns[/color][url=mag:%d:%d:turns:-][-][/url][url=mag:%d:%d:turns:+][+][/url]" % [
						court_index, line_index, court_index, line_index,
					]
			if line.get("remove_action") != null:
				bbcode += "  [url=rm:%d:%d][color=#e08060]Remove[/color][/url]" % [
					court_index, line_index,
				]
			bbcode += "\n"
	# The `Add demand` affordance (§3.1): disabled with the humanized reason
	# (clause cap / hard stop / frozen) when the row cannot author.
	if not bool(row.get("can_author", false)):
		var disabled_reason = _safe_str(row.get("authoring_disabled_reason_display"))
		if disabled_reason != "":
			bbcode += "      [color=#808080]+ Add demand — %s[/color]\n" % disabled_reason
		return bbcode
	var suggestions = row.get("demand_suggestions", [])
	if not (suggestions is Array) or suggestions.size() == 0:
		return bbcode
	if not bool(_add_demand_expanded.get(nation, false)):
		bbcode += "      [url=addmenu:%d][color=#80b0e0]+ Add demand[/color][/url]\n" % court_index
		return bbcode
	bbcode += "      [url=addmenu:%d][color=#80b0e0]− Add demand[/color][/url]\n" % court_index
	# §3.3: the direction-led group leads and renders expanded; the trailing
	# group renders collapsed behind a toggle. The dead-band (lead_group
	# empty) keeps the §3.1 order with BOTH groups behind toggles.
	var lead_group = str(row.get("lead_group", ""))
	var groups: Array = []
	if lead_group == "offer":
		groups = [["offer", true], ["demand", false]]
	elif lead_group == "demand":
		groups = [["demand", true], ["offer", false]]
	else:
		groups = [["demand", false], ["offer", false]]
	for group_spec in groups:
		var group_name: String = group_spec[0]
		var pre_expanded: bool = group_spec[1]
		var entries: Array = []
		var sugg_index = -1
		for sugg in suggestions:
			sugg_index += 1
			if sugg is Dictionary and str(sugg.get("group", "")) == group_name:
				entries.append([sugg_index, sugg])
		if entries.size() == 0:
			continue
		var group_label = ("Demands of %s" % nation) if group_name == "demand" else ("Offers to %s" % nation)
		var group_key = "%s|%s" % [nation, group_name]
		var expanded = pre_expanded or bool(_trailing_group_expanded.get(group_key, false))
		if not expanded:
			bbcode += "        [url=group:%d:%s][color=#a0a0c0]▸ %s (%d)[/color][/url]\n" % [
				court_index, group_name, group_label, entries.size(),
			]
			continue
		bbcode += "        [color=#a0a0c0]%s[/color]\n" % group_label
		for entry in entries:
			bbcode += _build_suggestion_lines(entry[1], court_index, int(entry[0]))
	return bbcode


func _build_suggestion_lines(sugg: Dictionary, court_index: int, sugg_index: int) -> String:
	# One Talleyrand-suggested, fully-formed option (§3.1): the act link, the
	# OQ-1 dropdown toggle when several candidates are valid, and the
	# GT-Slice-V in-character reason line.
	var bbcode = "          [url=sugg:%d:%d][color=#80b0e0]%s[/color][/url]" % [
		court_index, sugg_index, _safe_str(sugg.get("label")),
	]
	var options: Array = []
	if sugg.get("region_options") is Array:
		options = sugg.get("region_options")
	elif sugg.get("vassal_options") is Array:
		options = sugg.get("vassal_options")
	if options.size() > 1:
		bbcode += " [url=suggopts:%d:%d]▾[/url]" % [court_index, sugg_index]
	if bool(sugg.get("supports_continental_system", false)):
		bbcode += " [url=suggcs:%d:%d][color=#80b0e0][+ Continental System][/color][/url]" % [
			court_index, sugg_index,
		]
	bbcode += "\n"
	var reason = _safe_str(sugg.get("reason_display"))
	if reason != "":
		bbcode += "            [i][color=#909098]— %s[/color][/i]\n" % reason
	var options_key = "%d|%d" % [court_index, sugg_index]
	if options.size() > 1 and bool(_suggestion_options_expanded.get(options_key, false)):
		var opt_index = -1
		for opt in options:
			opt_index += 1
			bbcode += "            [url=suggpick:%d:%d:%d][color=#9ec0e0]%s[/color][/url]\n" % [
				court_index, sugg_index, opt_index, str(opt),
			]
	return bbcode


func _on_per_court_meta_clicked(meta):
	# GT-Slice-3: dispatch the per-court table's inline affordances. Encoding
	# is `op:court_index[:...]` with all names resolved from current_data at
	# click time (indices, never embedded identities). Client-only toggles
	# repaint the table; everything else round-trips through main.gd's
	# structured `action_params` path (send_dialogue_response_with_params).
	var parts = str(meta).split(":")
	if parts.size() < 2:
		return
	var op = parts[0]
	var row = _per_court_row(int(parts[1]))
	if row.is_empty():
		return
	var nation = str(row.get("nation", ""))
	match op:
		"focus":
			# REFRONT-9: presentation-only focus round trip; clicking the
			# focused court again clears the focus.
			var target = "" if str(current_data.get("focused_court", "")) == nation else nation
			_emit_settlement_action("settlement_focus_court", {
				"nation": target,
				"war_id": str(current_data.get("war_id", "")),
				"draft_key": str(current_data.get("draft_key", "")),
			})
		"addmenu":
			_add_demand_expanded[nation] = not bool(_add_demand_expanded.get(nation, false))
			_render_per_court_table()
		"group":
			if parts.size() >= 3:
				var group_key = "%s|%s" % [nation, parts[2]]
				_trailing_group_expanded[group_key] = not bool(_trailing_group_expanded.get(group_key, false))
				_render_per_court_table()
		"suggopts":
			if parts.size() >= 3:
				var options_key = "%s|%s" % [parts[1], parts[2]]
				_suggestion_options_expanded[options_key] = not bool(_suggestion_options_expanded.get(options_key, false))
				_render_per_court_table()
		"sugg", "suggcs", "suggpick":
			if parts.size() >= 3:
				_fire_suggestion(row, int(parts[2]), op, parts)
		"rm":
			if parts.size() >= 3:
				_fire_line_action(row, int(parts[2]), "remove_action", {})
		"mag":
			if parts.size() >= 5:
				_fire_magnitude_step(row, int(parts[2]), parts[3], parts[4])


func _per_court_row(court_index: int) -> Dictionary:
	var per_court = current_data.get("per_court_acceptance", [])
	if per_court is Array and court_index >= 0 and court_index < per_court.size():
		var row = per_court[court_index]
		if row is Dictionary:
			return row
	return {}


func _fire_suggestion(row: Dictionary, sugg_index: int, op: String, parts: PackedStringArray):
	# Fire one suggestion verbatim: the payload IS the suggestion's
	# `action_params` (the exact shape the GT-Slice-1 add verb accepts) plus
	# the transport keys. `suggpick` overrides the pre-picked region/vassal
	# with the chosen dropdown candidate; `suggcs` adds the optional
	# Continental System clause field (§3.1 — an existing clause field, not a
	# new mechanic).
	var suggestions = row.get("demand_suggestions", [])
	if not (suggestions is Array) or sugg_index < 0 or sugg_index >= suggestions.size():
		return
	var sugg = suggestions[sugg_index]
	if not (sugg is Dictionary):
		return
	var params = sugg.get("action_params", {})
	var payload = params.duplicate(true) if params is Dictionary else {}
	payload["war_id"] = str(sugg.get("war_id", current_data.get("war_id", "")))
	payload["draft_key"] = str(sugg.get("draft_key", current_data.get("draft_key", "")))
	if op == "suggcs":
		payload["includes_continental_system"] = true
	elif op == "suggpick" and parts.size() >= 4:
		var options: Array = []
		var option_field = ""
		if sugg.get("region_options") is Array:
			options = sugg.get("region_options")
			option_field = "region"
		elif sugg.get("vassal_options") is Array:
			options = sugg.get("vassal_options")
			option_field = "vassal_nation"
		var opt_index = int(parts[3])
		if option_field == "" or opt_index < 0 or opt_index >= options.size():
			return
		payload[option_field] = str(options[opt_index])
	_emit_settlement_action(str(sugg.get("action", "settlement_demand_add")), payload)


func _fire_line_action(row: Dictionary, line_index: int, action_field: String, extra: Dictionary):
	# Fire a current-demand line's ready-made mutation payload (GT-Slice-2's
	# `remove_action` / `set_magnitude_action` — clause_index + expected_type,
	# the stale-click guard).
	var current_demands = row.get("current_demands", [])
	if not (current_demands is Array) or line_index < 0 or line_index >= current_demands.size():
		return
	var line = current_demands[line_index]
	if not (line is Dictionary):
		return
	var action_dict = line.get(action_field, null)
	if not (action_dict is Dictionary):
		return
	var params = action_dict.get("action_params", {})
	var payload = params.duplicate(true) if params is Dictionary else {}
	payload["war_id"] = str(action_dict.get("war_id", current_data.get("war_id", "")))
	payload["draft_key"] = str(action_dict.get("draft_key", current_data.get("draft_key", "")))
	# `nation` keys the structured action_params route in main.gd; the
	# backend verbs key on clause_index, so this is transport-only.
	payload["nation"] = str(row.get("nation", ""))
	for key in extra:
		payload[key] = extra[key]
	_emit_settlement_action(str(action_dict.get("action", "")), payload)


func _fire_magnitude_step(row: Dictionary, line_index: int, field: String, direction: String):
	# GT-Slice-3 magnitude controls: compute the stepped value client-side
	# against the GT-Slice-2 magnitude metadata bounds, then fire the
	# set-magnitude verb with an ABSOLUTE value (the server clamps and
	# revalidates; a no-op step is skipped without a round trip).
	var current_demands = row.get("current_demands", [])
	if not (current_demands is Array) or line_index < 0 or line_index >= current_demands.size():
		return
	var line = current_demands[line_index]
	if not (line is Dictionary):
		return
	var magnitude = line.get("magnitude", null)
	if not (magnitude is Dictionary):
		return
	var extra = {}
	if field == "amount":
		var step = DEMAND_GOLD_MAGNITUDE_STEP if direction == "+" else -DEMAND_GOLD_MAGNITUDE_STEP
		var amount_min = int(magnitude.get("amount_min", 1))
		var new_amount = max(amount_min, int(magnitude.get("amount", 0)) + step)
		if new_amount == int(magnitude.get("amount", 0)):
			return
		extra["amount"] = new_amount
	elif field == "turns":
		var turn_step = 1 if direction == "+" else -1
		var new_turns = clampi(
			int(magnitude.get("turns", 0)) + turn_step,
			int(magnitude.get("turns_min", 1)),
			int(magnitude.get("turns_max", 20)),
		)
		if new_turns == int(magnitude.get("turns", 0)):
			return
		extra["turns"] = new_turns
	else:
		return
	_fire_line_action(row, line_index, "set_magnitude_action", extra)


func _emit_settlement_action(action: String, payload: Dictionary):
	# Same contract as _on_settlement_tier2_affordance: hide, emit, and let
	# main.gd route the structured payload through
	# send_dialogue_response_with_params; the backend re-mounts the popup on
	# success AND on failure (the CH-5 re-attach + error_display invariant).
	if action == "":
		return
	_clear_buttons()
	hide()
	choice_made.emit(action, payload)


func _build_settlement_scope_replace_content(data: Dictionary) -> String:
	var war_label = str(data.get("war_label", data.get("war_id", "Settlement")))
	var current_scope = str(data.get("current_scope_display", "current scope"))
	var incoming_scope = str(data.get("incoming_scope_display", "new scope"))
	var bbcode = ""
	bbcode += "[b][color=#e0c070]Settlement scope already staged[/color][/b]\n"
	bbcode += "[color=#a0a0a8]%s[/color]\n\n" % war_label
	bbcode += "[b]Current draft:[/b] %s\n" % current_scope
	bbcode += "[b]New scope:[/b] %s\n\n" % incoming_scope
	var ttext = str(data.get("talleyrand_text", ""))
	if ttext != "":
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n" % ttext
	return bbcode

func _build_war_purpose_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "Unknown")
	var bbcode = "[b]WAR PURPOSE - %s[/b]\n\n" % target
	var message = str(data.get("message", "Choose your war purpose."))
	bbcode += message + "\n\n"

	var objectives = data.get("objectives", [])
	for obj in objectives:
		var available = bool(obj.get("available", true))
		var label = str(obj.get("label", obj.get("type", "Objective")))
		var label_color = COLOR_GOLD if available else COLOR_DIMMED
		bbcode += "[color=" + label_color + "][b]" + label + "[/b][/color]\n"
		var description = str(obj.get("description", ""))
		if description:
			bbcode += "  " + description + "\n"
		var rate = int(float(obj.get("ticking_rate", 0)))
		if rate > 0:
			bbcode += "  Ticking score: +" + str(rate) + "/turn\n"
		if not available:
			var reason = str(obj.get("reason", "Not available"))
			bbcode += "  [color=" + COLOR_RED + "]" + reason + "[/color]\n"
		bbcode += "\n"

	return bbcode

func _build_peace_preview_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "Unknown")
	var snapshot = data.get("war_context_snapshot", {})
	var bbcode = "[b]PEACE PREVIEW - %s[/b]\n\n" % target

	bbcode += "[b]War Summary[/b]\n"
	var war_score = int(snapshot.get("war_score", 0))
	var score_color = "#80c080"
	if war_score < 0:
		score_color = "#e04040"
	elif war_score == 0:
		score_color = "#80a0d0"
	var trend = str(snapshot.get("war_score_trend", "stagnant"))
	var trend_arrow = "->"
	if trend == "rising":
		trend_arrow = "^"
	elif trend == "falling":
		trend_arrow = "v"
	bbcode += "War score: [color=%s]%d %s[/color]" % [score_color, war_score, trend_arrow]

	var components = snapshot.get("war_score_components", {})
	if components is Dictionary:
		var parts = []
		for key in ["territory", "battle", "decisive_battle", "capital", "ticking"]:
			var val = int(components.get(key, 0))
			if val != 0:
				var label = str(key).replace("_", " ").capitalize()
				parts.append("%s %s%d" % [label, "+" if val > 0 else "", val])
		if not parts.is_empty():
			bbcode += " (%s)" % ", ".join(parts)
	bbcode += "\n"

	var tier_display = str(snapshot.get("settlement_tier_display", ""))
	if tier_display:
		bbcode += "Settlement: [color=#e0c070]%s[/color]\n" % tier_display
	var objective = snapshot.get("war_objective", {})
	if objective is Dictionary and not objective.is_empty():
		var objective_type = str(objective.get("type", "")).replace("_", " ").capitalize()
		var target_regions = objective.get("target_regions", [])
		var region_text = ", ".join(target_regions) if target_regions is Array and not target_regions.is_empty() else "objective target"
		var accumulated = int(objective.get("accumulated_ticking", 0))
		var active = bool(objective.get("ticking_active", false))
		var active_text = "active" if active else "inactive"
		bbcode += "Objective: %s - %s (%s)\n" % [objective_type, region_text, active_text]
		bbcode += "Ticking: +%d\n" % accumulated

	var duration = int(snapshot.get("war_duration_turns", 0))
	var won = int(snapshot.get("battles_won", 0))
	var lost = int(snapshot.get("battles_lost", 0))
	bbcode += "Duration: %d turns   Battles: %dW / %dL\n" % [duration, won, lost]

	var fc = int(snapshot.get("french_casualties_total", 0))
	var ec = int(snapshot.get("enemy_casualties_total", 0))
	if fc > 0 or ec > 0:
		bbcode += "Casualties: ours %s / theirs %s\n" % [Utils.format_number(fc), Utils.format_number(ec)]

	var held_by_us = snapshot.get("regions_held_by_france", [])
	if held_by_us is Array and not held_by_us.is_empty():
		bbcode += "[color=#80c080]We hold: %s[/color]\n" % ", ".join(held_by_us)
	var held_by_them = snapshot.get("regions_held_by_enemy", [])
	if held_by_them is Array and not held_by_them.is_empty():
		bbcode += "[color=#e04040]They hold: %s[/color]\n" % ", ".join(held_by_them)
	if snapshot.has("armistice_remaining_turns"):
		bbcode += "Armistice remaining: %d turns\n" % int(snapshot.get("armistice_remaining_turns", 0))

	bbcode += "\n[b]Proposed Terms[/b]\n"
	var annotated = snapshot.get("annotated_terms", data.get("annotated_terms", []))
	if annotated is Array and not annotated.is_empty():
		bbcode += _build_annotated_terms_section(annotated)
	else:
		var terms = data.get("proposal_terms_summary", [])
		for t in terms:
			bbcode += "  [color=#e0c070]*[/color] %s\n" % str(t)

	var harshness_label = str(snapshot.get("harshness_label", data.get("harshness_label", "")))
	if harshness_label:
		var h_color = "#80a0d0"
		if harshness_label == "generous":
			h_color = "#80c080"
		elif harshness_label == "harsh":
			h_color = "#e09040"
		elif harshness_label == "punitive":
			h_color = "#e04040"
		bbcode += "Assessment: [color=%s]%s[/color]\n" % [h_color, harshness_label.to_upper()]

	bbcode += "\n[b]Acceptance Estimate[/b]\n"
	var acceptance = snapshot.get("acceptance_preview", {})
	if acceptance is Dictionary:
		var score = int(acceptance.get("score", data.get("acceptance_estimate", 0)))
		var outcome = str(acceptance.get("outcome", data.get("acceptance_outcome", "REJECT")))
		var a_color = "#e04040"
		if outcome == "ACCEPT":
			a_color = "#80c080"
		elif outcome == "COUNTER" or outcome == "COUNTER_OFFER":
			a_color = "#e0e060"
		bbcode += "Score: [color=%s]%d - %s[/color]\n" % [a_color, score, outcome]
		var lp = str(acceptance.get("largest_positive", ""))
		var ln = str(acceptance.get("largest_negative", ""))
		if lp:
			bbcode += "[color=#80c080]Key advantage: %s[/color]\n" % lp
		if ln:
			bbcode += "[color=#e04040]Key obstacle: %s[/color]\n" % ln

	var warnings = data.get("warnings", [])
	var tier_warnings = snapshot.get("tier_mismatch_warnings", [])
	var fallout = snapshot.get("fallout_warnings", [])
	var conflicts = snapshot.get("commitment_conflicts", [])
	if not warnings.is_empty() or (tier_warnings is Array and not tier_warnings.is_empty()) or (fallout is Array and not fallout.is_empty()) or (conflicts is Array and not conflicts.is_empty()):
		bbcode += "\n[b]Political Consequences[/b]\n"
		var consequence_items = []
		for warning in warnings:
			var txt = warning.get("text", str(warning)) if warning is Dictionary else str(warning)
			var sev = str(warning.get("severity", "medium")).to_upper() if warning is Dictionary else "MEDIUM"
			var category = str(warning.get("category", "")) if warning is Dictionary else ""
			var priority = 1
			if sev == "CRITICAL" or category == "hard_reject":
				priority = 0
			elif sev == "LOW":
				priority = 4
			consequence_items.append({"priority": priority, "color": "#e04040" if priority == 0 else "#e0c070", "text": txt})
		for warning in tier_warnings:
			var txt = warning.get("display", warning.get("text", str(warning))) if warning is Dictionary else str(warning)
			consequence_items.append({"priority": 1, "color": "#e0c070", "text": txt})
		for warning in fallout:
			var txt = warning.get("display", str(warning)) if warning is Dictionary else str(warning)
			var sev = str(warning.get("severity", "INFO")).to_upper() if warning is Dictionary else "INFO"
			var warning_type = str(warning.get("warning_type", "")) if warning is Dictionary else ""
			var priority = 2 if warning_type == "separate_peace_ally" else 3
			var color = "#e04040" if sev == "SEVERE" else "#e0c070"
			consequence_items.append({"priority": priority, "color": color, "text": txt})
		for conflict in conflicts:
			var txt = conflict.get("display", str(conflict)) if conflict is Dictionary else str(conflict)
			var sev = str(conflict.get("severity", "INFO")).to_upper() if conflict is Dictionary else "INFO"
			var priority = 0 if sev == "HARD_STOP" else 4
			if sev == "WARNING":
				priority = 1
			var color = "#e04040" if sev in ["WARNING", "HARD_STOP"] else "#e0c070"
			consequence_items.append({"priority": priority, "color": color, "text": txt})
		consequence_items.sort_custom(func(a, b): return int(a.get("priority", 99)) < int(b.get("priority", 99)))
		var shown = 0
		for item in consequence_items:
			if shown >= 3:
				break
			bbcode += "  [color=%s]*[/color] %s\n" % [str(item.get("color", "#e0c070")), str(item.get("text", ""))]
			shown += 1
		var overflow = consequence_items.size() - shown
		if overflow > 0:
			bbcode += "  [color=#808080](%d more concern%s...)[/color]\n" % [overflow, "s" if overflow > 1 else ""]

	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "\n[color=#c0b080][i]\"%s\"[/i][/color]\n" % ttext
	return bbcode

func _build_ultimatum_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "Unknown")
	var bbcode = "[b][color=#e04040]ULTIMATUM — %s[/color][/b]\n\n" % target

	# Talleyrand text (wizard step instructions)
	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n\n" % ttext

	# Demands display
	var demands = data.get("demands_display", [])
	if not demands.is_empty():
		bbcode += "[b]Demands:[/b]\n"
		for d in demands:
			bbcode += "  [color=#e09040]\u2022[/color] %s\n" % str(d)
		bbcode += "\n"

	# Harshness — "Coercive" maps to red
	var harshness_label = data.get("harshness_label", "")
	if harshness_label:
		var h_color = "#e04040"
		if harshness_label == "Low":
			h_color = "#80c080"
		elif harshness_label == "Moderate":
			h_color = "#e0e060"
		elif harshness_label == "High":
			h_color = "#e09040"
		bbcode += "Harshness: [color=%s]%s[/color]\n" % [h_color, harshness_label]

	# Acceptance estimate
	var acceptance = data.get("acceptance_estimate", -1)
	var outcome = data.get("acceptance_outcome", "")
	if acceptance >= 0:
		var a_color = "#e04040"
		if acceptance >= 50:
			a_color = "#80c080"
		elif acceptance >= 30:
			a_color = "#e0e060"
		bbcode += "Acceptance estimate: [color=%s]~%d%%[/color] (%s)\n" % [a_color, acceptance, outcome]
		var hint = data.get("acceptance_hint", "")
		if hint:
			bbcode += "[color=#a0a0a0]%s[/color]\n" % hint

	# DP cost
	var dp_cost = data.get("dp_cost", -1)
	if dp_cost >= 0:
		bbcode += "DP cost: [color=#80a0d0]%d[/color]\n" % dp_cost

	# Splash damage preview
	var splash = data.get("splash_damage_preview", [])
	if not splash.is_empty():
		bbcode += "\n[b]Diplomatic Fallout:[/b]\n"
		for s in splash:
			var nation_name = s.get("nation", "?")
			var penalty = s.get("relation_penalty", 0)
			var treaty = str(s.get("treaty_with_target", "")).replace("_", " ").to_lower()
			bbcode += "  [color=#e09040]\u2022[/color] %s: %d relations (%s)\n" % [nation_name, penalty, treaty]

	# Threat preview
	var threat = data.get("threat_increase_preview", "")
	if threat:
		bbcode += "\n[color=#e09040]Threat: %s[/color]\n" % threat

	return bbcode

func _build_mission_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "Unknown")
	var bbcode = "[b]DIPLOMATIC MISSION — %s[/b]\n\n" % target
	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n\n" % ttext
	# Show mission options from context if available
	var context = data.get("context", {})
	var dp_cost = data.get("dp_cost", -1)
	if dp_cost >= 0:
		bbcode += "DP cost: [color=#80a0d0]%d/turn[/color]\n" % dp_cost
	return bbcode

func _build_feasibility_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "Unknown")
	var bbcode = "[b]FEASIBILITY ASSESSMENT — %s[/b]\n\n" % target
	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n\n" % ttext
	# Acceptance estimate
	var acceptance = data.get("acceptance_estimate", -1)
	var outcome = data.get("acceptance_outcome", "")
	if acceptance >= 0:
		var a_color = "#e04040"
		if acceptance >= 50:
			a_color = "#80c080"
		elif acceptance >= 30:
			a_color = "#e0e060"
		bbcode += "Estimated acceptance: [color=%s]~%d%%[/color] (%s)\n" % [a_color, acceptance, outcome]
		var hint = data.get("acceptance_hint", "")
		if hint:
			bbcode += "[color=#a0a0a0]%s[/color]\n" % hint
	return bbcode


func _build_incoming_settlement_offer_content(data: Dictionary) -> String:
	"""SC-5 reversal commit 2 (Slice G1): render an AI-authored
	settlement offer using accepting-side framing. The backend popup
	payload supplies `talleyrand_text` (Talleyrand framing) and
	`proposer_voice` (foreign chancery line) per Voice Bible §16.1
	incoming-offer families, plus a structured terms summary.
	"""
	var proposer = str(data.get("proposer_nation", "Unknown"))
	var war_label = str(data.get("war_label", data.get("war_id", "settlement")))
	var bbcode = ""
	bbcode += "[b]SETTLEMENT OFFER FROM %s[/b]\n\n" % proposer.to_upper()
	bbcode += "[color=#a0a0a8]%s[/color]\n\n" % war_label

	var proposer_voice = str(data.get("proposer_voice", ""))
	if proposer_voice != "":
		bbcode += "[color=#e0c070][i]\"%s\"[/i][/color]\n\n" % proposer_voice

	var terms = data.get("terms_summary", [])
	if terms is Array and terms.size() > 0:
		bbcode += "[b]Their proposed terms:[/b]\n"
		for t in terms:
			bbcode += "  [color=#e0c070]•[/color] %s\n" % str(t)
		bbcode += "\n"

	var covered = data.get("covered_enemy_participants", [])
	if covered is Array and covered.size() > 0:
		bbcode += "[b]Covered enemies:[/b] " + ", ".join(PackedStringArray(covered)) + "\n\n"

	var talleyrand = str(data.get("talleyrand_text", ""))
	if talleyrand != "":
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n" % talleyrand

	return bbcode


func _build_ally_settlement_petition_content(data: Dictionary) -> String:
	var ally = str(data.get("ally_nation", "Ally"))
	var war_label = str(data.get("war_label", data.get("war_id", "settlement")))
	var claim_war = str(data.get("claim_war_label", data.get("claim_war_id", "")))
	var claim_region = str(data.get("claim_region", "claim"))
	var target_enemy = str(data.get("target_enemy", "the enemy"))
	var bbcode = ""
	bbcode += "[b]ALLY SETTLEMENT PETITION - %s[/b]\n\n" % ally.to_upper()
	bbcode += "[color=#a0a0a8]%s[/color]\n" % war_label
	if claim_war != "":
		bbcode += "[color=#a0a0a8]Related claim: %s[/color]\n" % claim_war
	bbcode += "\n"

	var ally_voice = str(data.get("ally_voice", ""))
	if ally_voice != "":
		bbcode += "[color=#e0c070][i]\"%s\"[/i][/color]\n\n" % ally_voice

	bbcode += "[b]Claim at issue:[/b] %s" % claim_region
	if target_enemy != "":
		bbcode += " against " + target_enemy
	bbcode += "\n\n"

	var talleyrand = str(data.get("talleyrand_text", ""))
	if talleyrand != "":
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n" % talleyrand
	return bbcode


func _build_advisory_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "")
	var header = "TALLEYRAND'S ASSESSMENT"
	if target:
		header += " — %s" % target
	var bbcode = "[b]%s[/b]\n\n" % header
	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n" % ttext
	return bbcode

func _build_war_confirm_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "Unknown")
	var bbcode = "[b][color=#e04040]WAR DECLARATION — %s[/color][/b]\n\n" % target
	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "[color=#e09040]%s[/color]\n" % ttext
	var warnings = data.get("warnings", [])
	if not warnings.is_empty():
		bbcode += "\n[b]Political Context:[/b]\n"
		var shown = mini(warnings.size(), 2)
		for idx in range(shown):
			var warning = warnings[idx]
			var severity = str(warning.get("severity", "low"))
			var color = "#e0c070"
			if severity == "critical":
				color = "#e04040"
			elif severity == "high":
				color = "#e09040"
			elif severity == "medium":
				color = "#e0c060"
			bbcode += "  [color=%s]â€¢[/color] %s\n" % [color, str(warning.get("text", ""))]
		if warnings.size() > shown:
			bbcode += "  [color=#a0a0a0]+%d more diplomatic concern%s[/color]\n" % [
				warnings.size() - shown,
				"" if (warnings.size() - shown) == 1 else "s",
			]
	return bbcode

func _build_conflict_alert_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "Unknown")
	var bbcode = "[b][color=#e09040]ALLIANCE CONFLICT — %s[/color][/b]\n\n" % target
	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n" % ttext
	var warnings = data.get("warnings", [])
	if not warnings.is_empty():
		bbcode += "\n[b]Political Context:[/b]\n"
		var shown = mini(warnings.size(), 2)
		for idx in range(shown):
			var warning = warnings[idx]
			var severity = str(warning.get("severity", "low"))
			var color = "#e0c070"
			if severity == "critical":
				color = "#e04040"
			elif severity == "high":
				color = "#e09040"
			elif severity == "medium":
				color = "#e0c060"
			bbcode += "  [color=%s]â€¢[/color] %s\n" % [color, str(warning.get("text", ""))]
		if warnings.size() > shown:
			bbcode += "  [color=#a0a0a0]+%d more diplomatic concern%s[/color]\n" % [
				warnings.size() - shown,
				"" if (warnings.size() - shown) == 1 else "s",
			]
	return bbcode

func _build_annotated_terms_section(annotated: Array) -> String:
	var demands = []
	var concessions = []
	var mutual = []
	for term in annotated:
		var direction = str(term.get("term_direction", "mutual"))
		if direction == "demand":
			demands.append(term)
		elif direction == "concession":
			concessions.append(term)
		else:
			mutual.append(term)

	var bbcode = ""
	if not demands.is_empty():
		bbcode += "[b]France demands:[/b]\n"
		for t in demands:
			bbcode += "  [color=#e09040]•[/color] %s\n" % str(t.get("display_label", "?"))
	if not concessions.is_empty():
		bbcode += "[b]France concedes:[/b]\n"
		for t in concessions:
			bbcode += "  [color=#80c0a0]•[/color] %s\n" % str(t.get("display_label", "?"))
	if not mutual.is_empty():
		bbcode += "[b]Mutual:[/b]\n"
		for t in mutual:
			bbcode += "  [color=#e0c070]•[/color] %s\n" % str(t.get("display_label", "?"))
	if bbcode:
		bbcode += "\n"
	return bbcode


func _on_option_selected(action: String):
	_clear_buttons()
	hide()
	choice_made.emit(action, current_data)

func _on_settlement_tier2_affordance(affordance: Dictionary):
	# Re-front Slice 2: a per-row dial / coverage affordance carries its own
	# structured params (scope / nation / war_id / draft_key). Emit the affordance
	# dict as the choice data so main.gd routes it through the structured
	# `action_params` dialogue path instead of options[] index matching.
	_clear_buttons()
	hide()
	choice_made.emit(str(affordance.get("action", "")), affordance)

func _clear_buttons():
	for child in button_container.get_children():
		child.queue_free()

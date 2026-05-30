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

var current_data: Dictionary = {}

const COLOR_GOLD = "#d9c08c"
const COLOR_DIMMED = "#808080"
const COLOR_RED = "#e04040"

func _ready():
	hide()

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

	show()

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

	var chips = data.get("covered_enemy_display_chips", data.get("covered_enemy_participants", []))
	if chips is Array and chips.size() > 0:
		bbcode += "[b]Covered enemies:[/b] " + ", ".join(PackedStringArray(chips)) + "\n"
	var uncovered = data.get("uncovered_enemy_display_chips", review.get("uncovered_enemy_display_chips", [])) if review is Dictionary else []
	if uncovered is Array and uncovered.size() > 0:
		bbcode += "[color=#e0a040][b]Still at war:[/b] " + ", ".join(PackedStringArray(uncovered)) + "[/color]\n"
	bbcode += "\n"

	# Re-front Slice 1 §11.2/§11.4: the per-court table. Each covered court has
	# its own band, direction summary, and named-diplomat voice; holdouts carry
	# Ease/Drop affordances on their own row. Talleyrand narrates the table.
	bbcode += _build_settlement_per_court_block(data)

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

func _build_settlement_per_court_block(data: Dictionary) -> String:
	# Re-front Slice 1: render the per-court acceptance table (PROPOSE + REVIEW).
	var per_court = data.get("per_court_acceptance", [])
	if not (per_court is Array) or per_court.size() == 0:
		return ""
	var bbcode = ""
	var narration = str(data.get("multi_court_table_narration", ""))
	if narration != "":
		bbcode += "[i][color=#c0c0c8]%s[/color][/i]\n" % narration
	bbcode += "[b]The table[/b]\n"
	for row in per_court:
		if not (row is Dictionary):
			continue
		var nation = str(row.get("nation", "?"))
		var band_display = str(row.get("band_display", row.get("band", "")))
		var direction = str(row.get("direction_summary", ""))
		var total = row.get("total", null)
		var total_text = ""
		if total != null:
			total_text = " (%d)" % int(total)
		bbcode += "  [color=#e0c070]*[/color] [b]%s[/b] - %s%s" % [nation, band_display, total_text]
		if direction != "":
			bbcode += " [color=#a0a0a8]%s[/color]" % direction
		bbcode += "\n"
		var blocker = str(row.get("top_blocker_display", ""))
		if blocker != "" and blocker != "null":
			bbcode += "      [color=#e0a040]Blocker: %s[/color]\n" % blocker
		var voice = str(row.get("voice_line", ""))
		if voice != "":
			bbcode += "      [i]%s[/i]\n" % voice
		# Holdout rows expose Ease / Drop affordances (§11.4).
		var holdout_actions = row.get("holdout_actions", [])
		if holdout_actions is Array and holdout_actions.size() > 0:
			var labels = []
			for ha in holdout_actions:
				if ha is Dictionary:
					labels.append(str(ha.get("label", "")))
			if labels.size() > 0:
				bbcode += "      [color=#80b0e0]%s[/color]\n" % " | ".join(PackedStringArray(labels))
	var overall = data.get("overall_acceptance", {})
	if overall is Dictionary:
		var summary = str(overall.get("summary_display", ""))
		if summary != "":
			var carries = bool(overall.get("carries", false))
			var color = "#60c060" if carries else "#e0a040"
			bbcode += "[b][color=%s]%s[/color][/b]\n" % [color, summary]
	bbcode += "\n"
	return bbcode


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

func _clear_buttons():
	for child in button_container.get_children():
		child.queue_free()

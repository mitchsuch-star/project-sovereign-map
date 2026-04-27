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
		btn.text = original_label
		btn.tooltip_text = original_tooltip
		btn.custom_minimum_size = Vector2(160, 45)
		btn.add_theme_font_size_override("font_size", 14)
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

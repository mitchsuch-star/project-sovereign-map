extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Incoming Proposal Popup (Session 8C)
# =============================================================================
# Displays when an AI nation sends a diplomatic proposal to the player.
# Three buttons: Accept / Counter / Reject
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var accept_btn = $PanelContainer/VBoxContainer/ButtonContainer/AcceptButton
@onready var counter_btn = $PanelContainer/VBoxContainer/ButtonContainer/CounterButton
@onready var reject_btn = $PanelContainer/VBoxContainer/ButtonContainer/RejectButton
@onready var dismiss_btn = $PanelContainer/VBoxContainer/ButtonContainer/DismissButton

var current_data: Dictionary = {}
var _default_border_color: Color
@onready var panel_style: StyleBoxFlat = $PanelContainer.get_theme_stylebox("panel")

func _ready():
	hide()
	accept_btn.pressed.connect(_on_accept)
	counter_btn.pressed.connect(_on_counter)
	reject_btn.pressed.connect(_on_reject)
	dismiss_btn.pressed.connect(_on_dismiss)
	# Cache default border color for normal proposals
	_default_border_color = panel_style.border_color

func show_proposal(data: Dictionary):
	"""Display incoming proposal popup."""
	current_data = data
	var from_nation = data.get("from_nation", "Unknown")
	var from_display = Utils.display_nation_name(str(from_nation))
	var diplomat_name = data.get("diplomat_name", "An envoy")
	var diplomat_personality = data.get("diplomat_personality", "")
	var proposal_type = data.get("proposal_type", "unknown")
	var proposal_type_display = data.get("proposal_type_display", proposal_type)
	var clauses = data.get("clauses", [])
	var assessment = data.get("talleyrand_assessment", "")
	var accept_hint = data.get("acceptance_hint", "")
	var reject_hint = data.get("rejection_hint", "")
	var decision_reason = str(data.get("decision_reason", ""))
	var is_counter = data.get("is_counter_offer", false)
	# NA-5 §8: incoming AI ultimatum — its own register (never a counter)
	var is_ultimatum = data.get("is_ultimatum", false)
	var decision_reason_display = str(data.get("decision_reason_display", ""))
	# W6-10: the diplomat's own spoken line (voices the motive in-register)
	var diplomat_line = str(data.get("diplomat_line", ""))

	var type_display = str(proposal_type_display)
	var bbcode = ""

	if is_ultimatum:
		# Ultimatum: struck header, crimson border, demands not terms
		bbcode += "[center][color=#e04040][b]ULTIMATUM[/b][/color][/center]\n"
		var ult_pers_str = " (%s)" % str(diplomat_personality).capitalize() if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, ult_pers_str, from_display]
		bbcode += "[b]Demands:[/b]\n"
		panel_style.border_color = Color(0.878, 0.251, 0.251, 1.0)  # Crimson
	elif is_counter:
		# Counter-offer: distinct header + context
		bbcode += "[center][color=#7eb8da][b]COUNTER-OFFER[/b][/color][/center]\n"
		var pers_str = " (%s)" % str(diplomat_personality).capitalize() if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, pers_str, from_display]
		bbcode += "[color=#a0a0a8]In response to your %s proposal, %s offers modified terms:[/color]\n\n" % [type_display, from_display]
		bbcode += "[b]Revised Terms:[/b]\n"
		# Style: blue border for counter-offers
		panel_style.border_color = Color(0.494, 0.722, 0.855, 1.0)  # Steel blue
	else:
		# Normal AI proposal
		bbcode += "[b]DIPLOMATIC ENVOY[/b]\n"
		var pers_str = " (%s)" % str(diplomat_personality).capitalize() if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, pers_str, from_display]
		bbcode += "[b]Proposes:[/b] %s\n" % type_display
		bbcode += "[b]Terms:[/b]\n"
		# Restore default gold border
		panel_style.border_color = _default_border_color

	if data.has("war_context_snapshot"):
		bbcode += _build_peace_preview_section(data, clauses)
	else:
		for clause in clauses:
			bbcode += "  - %s\n" % str(clause)

	# W6-10: the envoy speaks the proposal and its motive in his own
	# register — when the line is present, it REPLACES the raw
	# "Court rationale" tag (the motive is voiced, not labeled).
	if diplomat_line != "":
		bbcode += "\n[color=#e0c060][i]%s[/i][/color]\n" % diplomat_line
	elif decision_reason_display:
		bbcode += "\n[color=#a0a0a8]Court rationale: %s.[/color]\n" % decision_reason_display

	if assessment:
		bbcode += "\n[color=gray]%s[/color]\n" % assessment

	if diplomat_line == "" and decision_reason != "" and decision_reason_display == "":
		bbcode += "\n[color=#9cb2c5]Court motive: %s[/color]\n" % decision_reason

	if accept_hint:
		bbcode += "\n[color=green]If accepted: %s[/color]" % accept_hint
	if reject_hint:
		bbcode += "\n[color=red]Key obstacle: %s[/color]" % reject_hint

	# Lapse warning
	if is_ultimatum:
		bbcode += "\n[color=#e0c060][i]This demand will lapse at end of turn.[/i][/color]"
	elif is_counter:
		bbcode += "\n[color=#e0c060][i]This response will lapse at end of turn.[/i][/color]"
	else:
		bbcode += "\n[color=#e0c060][i]This offer will lapse at end of turn.[/i][/color]"

	content_label.text = ""
	# Backend prose (clause strings, court rationale, hints) can embed raw
	# multi-word nation keys — humanize once at the render chokepoint.
	content_label.append_text(Utils.humanize_nation_keys_in_text(bbcode))

	# Enable buttons — hide Counter for counter-offers (no counter-counter)
	# and for ultimatums (an ultimatum is not a negotiation — NA-5 §8)
	accept_btn.disabled = false
	counter_btn.visible = not is_counter and not is_ultimatum
	counter_btn.disabled = is_counter or is_ultimatum
	reject_btn.disabled = false
	dismiss_btn.disabled = false
	dismiss_btn.text = "Not Now"
	# Button labels adapt to context
	if is_ultimatum:
		accept_btn.text = "Yield"
		reject_btn.text = "Defy"
	else:
		accept_btn.text = "Accept Terms" if is_counter else "Accept"
		reject_btn.text = "Reject Terms" if is_counter else "Reject"
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)

func _on_accept():
	_disable_buttons()
	hide()
	choice_made.emit("accept", current_data)

func _on_counter():
	_disable_buttons()
	hide()
	choice_made.emit("counter", current_data)

func _on_reject():
	_disable_buttons()
	hide()
	choice_made.emit("reject", current_data)

func _on_dismiss():
	_disable_buttons()
	hide()
	choice_made.emit("dismiss", current_data)

func _disable_buttons():
	accept_btn.disabled = true
	counter_btn.disabled = true
	reject_btn.disabled = true
	dismiss_btn.disabled = true

func _build_peace_preview_section(data: Dictionary, clauses: Array) -> String:
	var snapshot = data.get("war_context_snapshot", {})
	var bbcode = "\n[b]War Summary[/b]\n"
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

	var french_casualties = int(snapshot.get("french_casualties_total", 0))
	var enemy_casualties = int(snapshot.get("enemy_casualties_total", 0))
	if french_casualties > 0 or enemy_casualties > 0:
		bbcode += "Casualties: ours %s / theirs %s\n" % [str(french_casualties), str(enemy_casualties)]

	var held_by_us = snapshot.get("regions_held_by_france", [])
	if held_by_us is Array and not held_by_us.is_empty():
		bbcode += "[color=#80c080]We hold: %s[/color]\n" % ", ".join(held_by_us)
	var held_by_them = snapshot.get("regions_held_by_enemy", [])
	if held_by_them is Array and not held_by_them.is_empty():
		bbcode += "[color=#e04040]They hold: %s[/color]\n" % ", ".join(held_by_them)
	if snapshot.has("armistice_remaining_turns"):
		bbcode += "Armistice remaining: %d turns\n" % int(snapshot.get("armistice_remaining_turns", 0))

	# G4F-17: incoming armistice offers explain the truce mechanics too.
	var armistice_mechanics = snapshot.get("armistice_mechanics", {})
	if armistice_mechanics is Dictionary and not armistice_mechanics.is_empty():
		bbcode += "\n[b]Armistice Terms[/b]\n"
		for line in armistice_mechanics.get("display_lines", []):
			var line_color = "#a0a0d0"
			if str(line).begins_with("Relations stand"):
				line_color = "#80c080" if str(armistice_mechanics.get("projected_outcome", "")) == "peace" else "#e09040"
			bbcode += "  [color=%s]%s[/color]\n" % [line_color, str(line)]

	bbcode += "\n[b]Proposed Terms[/b]\n"
	var annotated = snapshot.get("annotated_terms", data.get("annotated_terms", []))
	if annotated is Array and not annotated.is_empty():
		bbcode += _build_annotated_terms_section(annotated)
	else:
		for clause in clauses:
			bbcode += "  - %s\n" % str(clause)

	var harshness_label = str(snapshot.get("harshness_label", data.get("harshness_label", "")))
	if harshness_label:
		var harshness_color = "#80a0d0"
		if harshness_label == "generous":
			harshness_color = "#80c080"
		elif harshness_label == "harsh":
			harshness_color = "#e09040"
		elif harshness_label == "punitive":
			harshness_color = "#e04040"
		bbcode += "Assessment: [color=%s]%s[/color]\n" % [harshness_color, harshness_label.to_upper()]

	var fallout = data.get("fallout_warnings", snapshot.get("fallout_warnings", []))
	var conflicts = data.get("commitment_conflicts", snapshot.get("commitment_conflicts", []))
	var tier_warnings = snapshot.get("tier_mismatch_warnings", [])
	if (tier_warnings is Array and not tier_warnings.is_empty()) or (fallout is Array and not fallout.is_empty()) or (conflicts is Array and not conflicts.is_empty()):
		bbcode += "\n[b]Political Consequences[/b]\n"
		var consequence_items = []
		for warning in tier_warnings:
			var warning_text = warning.get("display", warning.get("text", str(warning))) if warning is Dictionary else str(warning)
			consequence_items.append({"priority": 1, "color": "#e0c070", "text": warning_text})
		for warning in fallout:
			var warning_text = warning.get("display", str(warning)) if warning is Dictionary else str(warning)
			var severity = str(warning.get("severity", "INFO")).to_upper() if warning is Dictionary else "INFO"
			var warning_type = str(warning.get("warning_type", "")) if warning is Dictionary else ""
			var priority = 2 if warning_type == "separate_peace_ally" else 3
			var color = "#e04040" if severity == "SEVERE" else "#e0c070"
			consequence_items.append({"priority": priority, "color": color, "text": warning_text})
		for conflict in conflicts:
			var conflict_text = conflict.get("display", str(conflict)) if conflict is Dictionary else str(conflict)
			var conflict_severity = str(conflict.get("severity", "INFO")).to_upper() if conflict is Dictionary else "INFO"
			var conflict_priority = 0 if conflict_severity == "HARD_STOP" else 4
			if conflict_severity == "WARNING":
				conflict_priority = 1
			var conflict_color = "#e04040" if conflict_severity in ["WARNING", "HARD_STOP"] else "#e0c070"
			consequence_items.append({"priority": conflict_priority, "color": conflict_color, "text": conflict_text})
		consequence_items.sort_custom(func(a, b): return int(a.get("priority", 99)) < int(b.get("priority", 99)))
		var shown = 0
		for item in consequence_items:
			if shown >= 3:
				break
			bbcode += "  [color=%s]-[/color] %s\n" % [str(item.get("color", "#e0c070")), str(item.get("text", ""))]
			shown += 1
		var overflow = consequence_items.size() - shown
		if overflow > 0:
			bbcode += "  [color=#808080](%d more concern%s...)[/color]\n" % [overflow, "s" if overflow > 1 else ""]

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
		for term in demands:
			bbcode += "  [color=#e09040]-[/color] %s\n" % _term_label(term)
	if not concessions.is_empty():
		bbcode += "[b]France concedes:[/b]\n"
		for term in concessions:
			bbcode += "  [color=#80c0a0]-[/color] %s\n" % _term_label(term)
	if not mutual.is_empty():
		bbcode += "[b]Mutual:[/b]\n"
		for term in mutual:
			bbcode += "  [color=#e0c070]-[/color] %s\n" % _term_label(term)
	if bbcode:
		bbcode += "\n"
	return bbcode

func _term_label(term: Dictionary) -> String:
	return str(term.get("display_label", term.get("display", "?")))

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
		"force_declare_war_confirmation":
			bbcode = _build_war_confirm_content(data)
		"conflict_alert":
			bbcode = _build_conflict_alert_content(data)
		"ultimatum_confirm", "ultimatum_demand_wizard":
			bbcode = _build_ultimatum_content(data)
		_:
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

	# Terms summary
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

	# Talleyrand commentary
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
	return bbcode

func _build_conflict_alert_content(data: Dictionary) -> String:
	var target = data.get("target_nation", "Unknown")
	var bbcode = "[b][color=#e09040]ALLIANCE CONFLICT — %s[/color][/b]\n\n" % target
	var ttext = data.get("talleyrand_text", "")
	if ttext:
		bbcode += "[color=#c0b080][i]\"%s\"[/i][/color]\n" % ttext
	return bbcode

func _on_option_selected(action: String):
	_clear_buttons()
	hide()
	choice_made.emit(action, current_data)

func _clear_buttons():
	for child in button_container.get_children():
		child.queue_free()

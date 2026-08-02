extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Enemy Phase Dialog
# =============================================================================
# Displays enemy actions after player ends their turn.
# Shows full battle details: casualties, outcomes, conquests.
# Player must click Continue to proceed.
# =============================================================================

signal dismissed
# BD: a "⚔ View the field" link was clicked — main.gd opens the tableau
# over this dialog (layer 121 > 118); the dialog's input hold stands.
signal view_field_requested(payload: Dictionary)

# UI References
@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var content_label = $PanelContainer/VBoxContainer/ContentScroll/ContentLabel
@onready var continue_button = $PanelContainer/VBoxContainer/ContinueButton

# Color palette (matching main.gd). Nation header tints come from
# Utils.NATION_COLORS (single source, all 20 nations) — see _get_nation_color.
const COLOR_ERROR = "cd5c5c"

# BD: tableau payloads for this phase's battles, indexed by the meta link.
var _diorama_payloads: Array = []

func _ready():
	# Connect button signal
	continue_button.pressed.connect(_on_continue_pressed)
	# BD: battle lines carry [url=diorama:N] view-field links.
	content_label.meta_clicked.connect(_on_content_meta_clicked)

	# Hide by default
	hide()

func show_enemy_phase(enemy_phase: Dictionary, turn: int):
	"""Display enemy phase with full battle details."""

	# DEBUG: Print received enemy_phase structure
	print("[GODOT_ENEMY_PHASE] ═══════════════════════════════════════")
	print("[GODOT_ENEMY_PHASE] Received enemy_phase for turn ", turn)
	print("[GODOT_ENEMY_PHASE] Keys: ", enemy_phase.keys())
	print("[GODOT_ENEMY_PHASE] total_actions: ", enemy_phase.get("total_actions", "MISSING"))

	# Set title
	title_label.text = "ENEMY PHASE - Turn %d" % turn

	# Build content
	_diorama_payloads = []
	var content = ""

	var nations = enemy_phase.get("nations", {})
	var total_actions = enemy_phase.get("total_actions", 0)

	print("[GODOT_ENEMY_PHASE] nations count: ", nations.size())
	for n in nations:
		var nd = nations[n]
		print("[GODOT_ENEMY_PHASE]   ", n, ": ", nd.get("action_count", 0), " actions")
		var acts = nd.get("actions", [])
		for i in range(acts.size()):
			var act = acts[i]
			print("[GODOT_ENEMY_PHASE]     [", i, "] ai_action=", act.get("ai_action", {}))
			print("[GODOT_ENEMY_PHASE]     [", i, "] has events=", act.has("events"), " count=", act.get("events", []).size() if act.has("events") else 0)

	if enemy_phase.has("fog_hidden_summary"):
		# PL-4: Fog hid all enemy actions — show Berthier fog summary
		var fog_messages = enemy_phase.get("fog_hidden_summary", [])
		for msg in fog_messages:
			content += "[color=#" + Utils.COLOR_INFO + "]" + msg + "[/color]\n"
	elif total_actions == 0:
		content = "[color=#" + Utils.COLOR_INFO + "]No enemy actions this turn.[/color]"
	else:
		for nation in nations:
			var nation_data = nations[nation]
			var action_count = nation_data.get("action_count", 0)

			# Nation header with colored name
			var nation_color = _get_nation_color(nation)
			content += "[color=#" + nation_color + "][b]" + Utils.display_nation_name(nation).to_upper() + "[/b][/color]\n"
			content += "[color=#" + Utils.COLOR_INFO + "]" + "-".repeat(40) + "[/color]\n"

			# Process each action
			var actions = nation_data.get("actions", [])
			for action in actions:
				content += _format_action(action)

			content += "\n"

	# Set content
	content_label.text = content

	# Show the dialog
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can push the action row off-screen.
	# Runs AFTER show() so layout has settled.
	Utils.clamp_centered_panel($PanelContainer)

func _format_action(action: Dictionary) -> String:
	"""Format a single action with full details."""
	var result = ""

	# DEBUG: Print entire action to see what's coming through
	print("[ENEMY_PHASE_DEBUG] action keys: ", action.keys())
	if action.has("events"):
		print("[ENEMY_PHASE_DEBUG] events: ", action.get("events"))
	else:
		print("[ENEMY_PHASE_DEBUG] NO events key in action!")

	var ai_action = action.get("ai_action", {})
	var marshal_name = ai_action.get("marshal", "")
	var action_type = ai_action.get("action", "unknown")
	var target = ai_action.get("target", "")
	var nation = action.get("nation", "")

	# Basic action line — admin actions (build/repair/recruit) may not have a marshal
	var action_str = ""
	if marshal_name != "":
		action_str = marshal_name + " "
	elif nation != "":
		action_str = Utils.display_nation_name(nation) + " "

	# Detect bombardment (AI sends action="attack" but result has bombardment_result)
	var is_bombardment = action.has("bombardment_result")

	match action_type:
		"attack":
			if is_bombardment:
				action_str += "bombards " + target
			else:
				action_str += "attacks " + target
		"move":
			action_str += "moves to " + target
		"forced_march":
			# PT-D4: a 3+ hop chain collapsed server-side into one line —
			# origin (when scouted) → each stage → terminus, losses summed.
			var fm = action.get("forced_march", {})
			var fm_stages: Array = fm.get("stages", [])
			var fm_route = ""
			if fm.has("from"):
				fm_route = str(fm.get("from")) + " → "
			for fm_i in range(fm_stages.size()):
				if fm_i > 0:
					fm_route += " → "
				fm_route += str(fm_stages[fm_i])
			if fm_route == "":
				fm_route = target
			action_str += "drives a forced march — " + fm_route
			var fm_losses = int(fm.get("march_losses", 0))
			if fm_losses > 0:
				action_str += " (" + Utils.format_number(fm_losses) + " lost on the march)"
		"defend":
			action_str += "defends"
		"fortify":
			action_str += "fortifies position"
		"unfortify":
			action_str += "abandons fortified position"
		"drill":
			action_str += "drills troops"
		"stance_change":
			action_str += "changes stance to " + target
		"retreat":
			action_str += "retreats to " + target
		"wait":
			action_str += "holds position"
		"recruit":
			action_str += "recruits troops"
		"scout":
			action_str += "scouts " + target
		"build":
			var building_type = ai_action.get("building_type", "building").replace("_", " ")
			action_str += "builds " + building_type + " at " + target
		"repair":
			action_str += "repairs " + target
		_:
			action_str += action_type.replace("_", " ")
			if target:
				action_str += " " + target

	result += "[color=#" + Utils.COLOR_TEXT + "]- " + action_str + "[/color]\n"

	# Check for battle events
	var events = action.get("events", [])
	print("[ENEMY_PHASE_DEBUG] events count: ", events.size() if events else 0)
	for i in range(events.size()):
		var event = events[i]
		print("[ENEMY_PHASE_DEBUG] event[", i, "] type: ", event.get("type", "NO TYPE"))
		if event.get("type") == "battle":
			print("[ENEMY_PHASE_DEBUG] Calling _format_battle for battle event")
			# Pass the action line's own pair so the battle block does not
			# restate it: "- Mack attacks Ney" was immediately followed by
			# "Mack attacks Ney" under the battle name, every single turn.
			result += _format_battle(event, marshal_name, str(target))
		elif event.get("type") == "bombardment":
			print("[ENEMY_PHASE_DEBUG] Calling _format_bombardment for bombardment event")
			result += _format_bombardment(event)
		elif event.get("type") == "conquest":
			var region = event.get("region", "territory")
			var capture_choice = event.get("capture_choice", "")
			var choice_str = ""
			if capture_choice == "plunder":
				choice_str = " (plundered)"
			elif capture_choice == "secure":
				choice_str = " (secured)"
			result += "[color=#" + Utils.COLOR_CONQUEST + "]    Region captured: " + region + choice_str + "[/color]\n"

	# Berthier's After-Action Report (if battle occurred)
	if action.has("battle_report"):
		result += _format_berthier_report(action.battle_report)

	# Bombardment report (if bombardment occurred)
	if action.has("bombardment_result"):
		result += _format_bombardment_report(action.bombardment_result)

	# Session 66: Reinforcement messages (from coordinated battles)
	if action.has("reinforcement_messages"):
		var reinf_msgs = action.get("reinforcement_messages", [])
		for msg in reinf_msgs:
			var msg_text = str(msg)
			var reinf_color = Utils.COLOR_SUCCESS if msg_text.find("arrived") >= 0 else COLOR_ERROR
			result += "[color=#" + reinf_color + "]    " + msg_text + "[/color]\n"

	return result

func _format_battle(event: Dictionary, action_marshal: String = "", action_target: String = "") -> String:
	"""Format battle details.

	`action_marshal`/`action_target` are the pair the caller's action line
	already printed; when the battle is between exactly those two, the
	"X attacks Y" restatement is dropped as a duplicate.
	"""
	var result = ""

	var attacker = event.get("attacker", {})
	var defender = event.get("defender", {})
	var outcome = event.get("outcome", "unknown")
	var victor = event.get("victor", null)

	var attacker_name = attacker.get("name", "Unknown")
	var attacker_casualties = attacker.get("casualties", 0)
	var attacker_remaining = attacker.get("remaining", 0)
	var attacker_morale = attacker.get("morale", 0)

	var defender_name = defender.get("name", "Unknown")
	var defender_casualties = defender.get("casualties", 0)
	var defender_remaining = defender.get("remaining", 0)
	var defender_morale = defender.get("morale", 0)

	# Battle header - use battle_name if available, fallback to attacker vs defender
	var battle_title = event.get("battle_name", attacker_name + " vs " + defender_name)
	result += "[color=#" + Utils.COLOR_BATTLE + "]    " + battle_title + "[/color]\n"
	var already_stated = (
		action_marshal != "" and attacker_name == action_marshal
		and action_target != "" and defender_name == action_target
	)
	if not already_stated:
		result += "[color=#" + Utils.COLOR_INFO + "]    " + attacker_name + " attacks " + defender_name + "[/color]\n"

	# Casualties
	result += "[color=#" + Utils.COLOR_INFO + "]    " + attacker_name + ": "
	result += _format_number(attacker_casualties) + " casualties, "
	result += _format_number(attacker_remaining) + " remaining[/color]\n"

	result += "[color=#" + Utils.COLOR_INFO + "]    " + defender_name + ": "
	result += _format_number(defender_casualties) + " casualties, "
	result += _format_number(defender_remaining) + " remaining[/color]\n"

	# Outcome — colored by WHO WON: green only when the victor fought for
	# France. (The old check colored on "defender is a player marshal" against
	# a hardcoded legacy roster, so Soult/Murat/Lannes victories rendered red
	# and a player DEFEAT under Ney rendered green.)
	var outcome_text = _get_outcome_text(outcome)
	var outcome_color = Utils.COLOR_INFO
	if victor:
		outcome_color = Utils.COLOR_SUCCESS if _victor_is_player(event, str(victor)) else COLOR_ERROR

	result += "[color=#" + outcome_color + "]    Result: " + outcome_text
	if victor:
		result += " (" + victor + " victorious)"
	result += "[/color]\n"

	# Check for enemy destroyed
	if event.get("enemy_destroyed", false):
		result += "[color=#" + Utils.COLOR_CONQUEST + "]    ARMY DESTROYED![/color]\n"

	# Check for region conquered
	if event.get("region_conquered", false):
		var region = event.get("region_name", "territory")
		# IGR-X8: field-battle conquests now carry the decided choice like
		# the garrison/unopposed conquest events — same suffix vocabulary.
		var battle_capture_choice = str(event.get("capture_choice", ""))
		var battle_choice_str = ""
		if battle_capture_choice == "plunder":
			battle_choice_str = " (plundered)"
		elif battle_capture_choice == "secure":
			battle_choice_str = " (secured)"
		result += "[color=#" + Utils.COLOR_CONQUEST + "]    " + region + " CAPTURED!" + battle_choice_str + "[/color]\n"

	# Check for forced retreat
	if attacker.get("forced_retreat", false):
		result += "[color=#" + COLOR_ERROR + "]    " + attacker_name + " forced to retreat![/color]\n"
	if defender.get("forced_retreat", false):
		result += "[color=#" + COLOR_ERROR + "]    " + defender_name + " forced to retreat![/color]\n"

	# BD: the tableau link — every battle that carried a diorama payload is
	# one click from its field (the routine-raid case; the dramatic case
	# auto-plays after this dialog closes).
	var diorama = event.get("diorama")
	if diorama is Dictionary and not diorama.is_empty():
		_diorama_payloads.append(diorama)
		result += "[color=#" + Utils.COLOR_GOLD + "]    [url=diorama:" \
			+ str(_diorama_payloads.size() - 1) + "]⚔ View the field[/url][/color]\n"

	# Fort degradation
	if event.get("fortification_degraded", false):
		var fort_old = int(event.get("fortification_old", 0) * 100)
		var fort_new = int(event.get("fortification_new", 0) * 100)
		if fort_new <= 0:
			result += "[color=#" + Utils.COLOR_INFO + "]    Fortifications DESTROYED! (" + str(fort_old) + "% -> 0%)[/color]\n"
		else:
			result += "[color=#" + Utils.COLOR_INFO + "]    Fort degraded: " + str(fort_old) + "% -> " + str(fort_new) + "%[/color]\n"

	return result

func _format_berthier_report(report: Dictionary) -> String:
	"""Format Berthier's After-Action Report for enemy phase dialog."""
	var result = ""
	var COLOR_RPT = "AAAAAA"

	result += "[color=#" + Utils.COLOR_BERTHIER + "]    --- Berthier's Report ---[/color]\n"

	# Modifier lines
	var breakdown = report.get("modifier_breakdown", {})
	var casualty = report.get("casualty_summary", {})
	var atk_name = str(casualty.get("attacker_name", "Attacker"))
	var def_name = str(casualty.get("defender_name", "Defender"))

	var atk_mods = breakdown.get("attacker", [])
	if atk_mods.size() > 0:
		var parts: Array = []
		for m in atk_mods:
			var sign = "+" if m.get("type", "") == "bonus" else "-"
			parts.append(str(m.get("label", "")) + " " + sign + str(int(m.get("value", 0))) + "%")
		result += "[color=#" + COLOR_RPT + "]    Attack: " + atk_name + " (" + ", ".join(PackedStringArray(parts)) + ")[/color]\n"

	var def_mods = breakdown.get("defender", [])
	if def_mods.size() > 0:
		var parts: Array = []
		for m in def_mods:
			var sign = "+" if m.get("type", "") == "bonus" else "-"
			parts.append(str(m.get("label", "")) + " " + sign + str(int(m.get("value", 0))) + "%")
		result += "[color=#" + COLOR_RPT + "]    Defense: " + def_name + " (" + ", ".join(PackedStringArray(parts)) + ")[/color]\n"

	# Observation
	var observation = report.get("observation", "")
	if observation != "":
		result += "[color=#" + Utils.COLOR_OBSERVATION + "]    Berthier: \"" + observation + "\"[/color]\n"

	return result

func _format_bombardment(event: Dictionary) -> String:
	"""Format bombardment event details."""
	var result = ""
	var attacker_name = str(event.get("attacker", "Artillery"))
	var defender_name = str(event.get("defender", "Enemy"))
	var atk_location = str(event.get("attacker_location", ""))
	var def_location = str(event.get("defender_location", ""))
	var def_casualties = int(event.get("defender_casualties", 0))
	var atk_casualties = int(event.get("attacker_casualties", 0))

	result += "[color=#" + Utils.COLOR_BATTLE + "]    Bombardment of " + def_location + "[/color]\n"
	result += "[color=#" + Utils.COLOR_INFO + "]    " + attacker_name + " fires from " + atk_location + " on " + defender_name + "[/color]\n"
	result += "[color=#" + COLOR_ERROR + "]    " + defender_name + ": " + _format_number(def_casualties) + " casualties[/color]\n"
	result += "[color=#" + Utils.COLOR_INFO + "]    " + attacker_name + ": " + _format_number(atk_casualties) + " return fire[/color]\n"

	# Fort degradation
	if event.get("fort_degraded", false):
		var fort_old = int(event.get("fort_old", 0) * 100)
		var fort_new = int(event.get("fort_new", 0) * 100)
		if fort_new <= 0:
			result += "[color=#" + Utils.COLOR_BATTLE + "]    Fortifications DESTROYED![/color]\n"
		else:
			result += "[color=#" + Utils.COLOR_INFO + "]    Fort degraded: " + str(fort_old) + "% -> " + str(fort_new) + "%[/color]\n"

	return result

func _format_bombardment_report(bombard_result: Dictionary) -> String:
	"""Format bombardment result details for enemy phase dialog."""
	var result = ""
	var COLOR_RPT = "AAAAAA"

	result += "[color=#" + Utils.COLOR_BERTHIER + "]    --- Bombardment Report ---[/color]\n"

	var atk = bombard_result.get("attacker", {})
	var defn = bombard_result.get("defender", {})

	var atk_name = str(atk.get("name", "Artillery"))
	var def_name = str(defn.get("name", "Enemy"))
	var def_cas = int(defn.get("casualties", 0))
	var def_rem = int(defn.get("remaining", 0))
	var def_morale = int(defn.get("morale", 100))
	var atk_cas = int(atk.get("casualties", 0))
	var atk_rem = int(atk.get("remaining", 0))

	result += "[color=#" + COLOR_RPT + "]    " + def_name + ": " + _format_number(def_cas) + " casualties, " + _format_number(def_rem) + " remaining, morale " + str(def_morale) + "%[/color]\n"
	result += "[color=#" + COLOR_RPT + "]    " + atk_name + ": " + _format_number(atk_cas) + " return fire, " + _format_number(atk_rem) + " remaining[/color]\n"

	# Berthier observation
	var obs = str(bombard_result.get("berthier_observation", ""))
	if obs != "" and obs != "null":
		result += "[color=#" + Utils.COLOR_OBSERVATION + "]    Berthier: \"" + obs + "\"[/color]\n"

	return result

func _get_outcome_text(outcome: String) -> String:
	"""Convert outcome code to readable text."""
	match outcome:
		"attacker_victory":
			return "Decisive attacker victory"
		"defender_victory":
			return "Decisive defender victory"
		"attacker_tactical_victory":
			return "Attacker tactical victory"
		"defender_tactical_victory":
			return "Defender tactical victory"
		"stalemate":
			return "Bloody stalemate"
		_:
			return outcome.replace("_", " ").capitalize()

func _get_nation_color(nation: String) -> String:
	"""Nation header tint from the central 20-nation palette (Utils.NATION_COLORS,
	Slice 7.5) instead of a private 3-nation map. Palette entries are map fills,
	so near-black ones (Prussia) get a one-shot luminance lift to stay legible
	on the dark panel."""
	if not Utils.NATION_COLORS.has(nation):
		return Utils.COLOR_TEXT
	var c: Color = Utils.NATION_COLORS[nation]
	var lum := c.get_luminance()
	if lum < 0.45:
		c = c.lightened(clampf(0.55 - lum, 0.0, 0.6))
	return c.to_html(false)

func _victor_is_player(event: Dictionary, victor: String) -> bool:
	"""True when the battle's victor fought for France. Side nations ride the
	battle event (attacker_nation/defender_nation) — never a hardcoded roster,
	which broke for the 1805 marshals and Marshalate recruits."""
	var defender_dict = event.get("defender", {})
	var defender_name = str(defender_dict.get("name", "")) if defender_dict is Dictionary else ""
	var side_nation = ""
	if victor == defender_name:
		side_nation = str(event.get("defender_nation", ""))
	else:
		side_nation = str(event.get("attacker_nation", ""))
	return side_nation == "France"

func _format_number(num) -> String:
	"""Format number with comma separators (delegates to the Utils single source)."""
	return Utils.format_number(int(num))

# July 18, 2026 viewport sweep: a keyboard escape hatch. main.gd's ESC ladder
# deliberately refuses to act while a modal is open, and dialog_manager
# registers this dialog as modal=true — so if a geometry, theme or font change
# ever pushes [Continue] off the bottom, there is literally no way out and the
# turn is lost. Routing through _on_continue_pressed keeps hide()+dismissed
# single-source, so the dismissal is identical to clicking the button.
func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("ui_accept") or event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_on_continue_pressed()

func _on_content_meta_clicked(meta) -> void:
	"""BD: open the tableau for a battle line's view-field link."""
	var meta_str := str(meta)
	if not meta_str.begins_with("diorama:"):
		return
	var idx := int(meta_str.trim_prefix("diorama:"))
	if idx < 0 or idx >= _diorama_payloads.size():
		return
	view_field_requested.emit(_diorama_payloads[idx])


func _on_continue_pressed():
	"""Handle continue button press."""
	hide()
	dismissed.emit()

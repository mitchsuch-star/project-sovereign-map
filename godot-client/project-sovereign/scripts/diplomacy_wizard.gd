extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Diplomacy Wizard (Diplomacy Button Session B)
# =============================================================================
# Three-step guided wizard for diplomacy. CanvasLayer 100 (modal).
# Step 1: Nation selection (categorized). Step 2: Assessment + actions.
# Step 3: Handoff — emits command_selected with constructed command string.
# Own HTTPRequest to avoid ERR_BUSY conflicts with api_client (§9b).
# =============================================================================

signal command_selected(command: String)
signal open_envoys_requested

# UI References — paths match scene tree
@onready var background_overlay = $BackgroundOverlay
@onready var title_label = $PanelContainer/VBoxContainer/HeaderRow/TitleLabel
@onready var dp_label = $PanelContainer/VBoxContainer/HeaderRow/DPLabel
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var assessment_panel = $PanelContainer/VBoxContainer/AssessmentPanel
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_list = $PanelContainer/VBoxContainer/ScrollContainer/ContentList
@onready var back_button = $PanelContainer/VBoxContainer/ButtonRow/BackButton
@onready var cancel_button = $PanelContainer/VBoxContainer/ButtonRow/CancelButton

# Dedicated HTTP request (§9b — must not share api_client's HTTPRequest)
var _http: HTTPRequest
var _pending_request: String = ""  # "nations" or "preview"
var _request_id: int = 0  # Monotonic ID to discard stale responses
var _request_in_flight: bool = false  # Guard against double-open (Fix 8)

# State
var _current_step: int = 0  # 0=hidden, 1=nations, 2=actions, 3=peace_preview
var _selected_nation: String = ""
var _dp_available: int = 0
var _pending_peace_command: String = ""  # BPH-B: command held during preview
var _last_preview_data: Dictionary = {}  # BPH-B: cached Step 2 response for snapshot lookup

# BPH-B: Peace-class actions that trigger the preview panel
const PEACE_CLASS_ACTIONS = ["propose_armistice", "propose_peace"]

# Color palette
const COLOR_LIGHT_GREEN = "a0d0a0"
const COLOR_LIGHT_RED = "d9a0a0"
const COLOR_ORANGE = "d9a060"
const COLOR_YELLOW = "d9d080"

# Likelihood color mapping (§3a) — keys must match get_likelihood_descriptor() exactly
var _likelihood_colors: Dictionary = {
	"Almost Certain": Utils.COLOR_SUCCESS,
	"Favorable": COLOR_LIGHT_GREEN,
	"Uncertain — may counter": COLOR_YELLOW,
	"Doubtful — expect counter": COLOR_ORANGE,
	"Unlikely": COLOR_LIGHT_RED,
	"Hopeless": Utils.COLOR_ERROR,
}


func _ready():
	hide()
	close_button.pressed.connect(_close_wizard)
	cancel_button.pressed.connect(_close_wizard)
	back_button.pressed.connect(_go_back)
	background_overlay.gui_input.connect(_on_overlay_input)

	# Create dedicated HTTPRequest (§9b)
	_http = HTTPRequest.new()
	add_child(_http)
	_http.request_completed.connect(_on_http_completed)
	_http.timeout = 30.0


func open():
	"""Open wizard at Step 1 — fetch and show nation list."""
	# Guard against double-open while HTTP request is in flight (Fix 8)
	if _request_in_flight:
		return
	_current_step = 1
	_selected_nation = ""
	title_label.text = "DIPLOMACY"
	assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]\"Your Excellency, which nation requires our diplomatic attention?\"[/color]"
	back_button.visible = false
	dp_label.text = ""
	_clear_content_list()
	_add_loading_label()
	show()
	_fetch_nations()


func open_for_nation(nation: String):
	"""Open wizard directly at Step 2 for a specific nation (N4c).
	Called from war detail popup [Negotiate Peace] and coalition [Target X] buttons."""
	# Guard against double-open while HTTP request is in flight (Fix 8)
	if _request_in_flight:
		return
	_current_step = 2
	_selected_nation = nation
	back_button.visible = true
	title_label.text = "DIPLOMACY — " + nation
	assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]Loading assessment...[/color]"
	_clear_content_list()
	_add_loading_label()
	show()
	_fetch_preview(nation)


func _close_wizard():
	_current_step = 0
	_selected_nation = ""
	_pending_peace_command = ""
	_request_in_flight = false
	if _http:
		_http.cancel_request()
	hide()


func _go_back():
	"""Return to previous step."""
	if _current_step == 3:
		# BPH-B: Step 3 (peace preview) → Step 2 (actions)
		_current_step = 2
		_pending_peace_command = ""
		title_label.text = "DIPLOMACY — " + _selected_nation
		_render_preview(_last_preview_data)
		return
	if _current_step == 2:
		_current_step = 1
		_selected_nation = ""
		back_button.visible = false
		title_label.text = "DIPLOMACY"
		assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]\"Your Excellency, which nation requires our diplomatic attention?\"[/color]"
		_clear_content_list()
		_add_loading_label()
		_fetch_nations()


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		_close_wizard()


# =============================================================================
# HTTP REQUESTS
# =============================================================================

const API_URL = "http://127.0.0.1:8005"

func _fetch_nations():
	"""Fetch categorized nation list for Step 1."""
	_http.cancel_request()
	_request_id += 1
	_pending_request = "nations"
	_request_in_flight = true
	var error = _http.request(API_URL + "/diplomatic_preview")
	if error != OK:
		_request_in_flight = false
		_show_error("Failed to connect to headquarters.")


func _fetch_preview(nation: String):
	"""Fetch diplomatic preview for Step 2."""
	_http.cancel_request()
	_request_id += 1
	_pending_request = "preview"
	_request_in_flight = true
	var url = API_URL + "/diplomatic_preview?nation=" + nation.uri_encode()
	var error = _http.request(url)
	if error != OK:
		_request_in_flight = false
		_show_error("Failed to fetch diplomatic preview.")


func _on_http_completed(result, response_code, headers, body):
	_request_in_flight = false
	if not visible:
		return
	# Capture the request ID at response time to detect stale responses
	var response_id = _request_id
	# Discard stale responses (user navigated away before response arrived)
	if response_id != _request_id:
		return
	if response_code != 200:
		_show_error("Connection failed.")
		return

	var json = JSON.new()
	if json.parse(body.get_string_from_utf8()) != OK:
		_show_error("Failed to parse response.")
		return

	var data = json.data
	if not data.get("success", false):
		_show_error(str(data.get("message", data.get("error", "Unknown error"))))
		return

	if _pending_request == "nations":
		_render_nations(data)
	elif _pending_request == "preview":
		_render_preview(data)


func _show_error(msg: String):
	_current_step = 1  # Reset step so back button works (Fix 7)
	back_button.visible = false
	_clear_content_list()
	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	lbl.text = "[color=#" + Utils.COLOR_ERROR + "]" + msg + "[/color]"
	content_list.add_child(lbl)


# =============================================================================
# STEP 1: NATION LIST
# =============================================================================

func _render_nations(data: Dictionary):
	_clear_content_list()
	scroll_container.scroll_vertical = 0
	_dp_available = int(data.get("dp_available", 0))
	dp_label.text = "DP: " + str(_dp_available)
	var pending_envoy_count = int(data.get("pending_envoy_count", 0))

	# PL-30: Distinguish blocking dialogue from deferred proposal result.
	# Never close+add_output — that path crashes when the wizard is no longer
	# in the scene tree. Show an in-wizard message instead.
	var dialogue_pending = data.get("dialogue_pending", false)
	if dialogue_pending:
		_add_dialogue_gate_notice(pending_envoy_count)
		return

	var categories = data.get("categories", {})
	var has_any = false

	# At War (red header)
	var at_war = categories.get("at_war", [])
	if at_war.size() > 0:
		has_any = true
		_add_category_header("At War (" + str(at_war.size()) + ")", Utils.COLOR_ERROR)
		for n in at_war:
			_add_nation_button(n)

	# Treaties (blue header)
	var treaties = categories.get("treaties", [])
	if treaties.size() > 0:
		has_any = true
		_add_category_header("Treaties (" + str(treaties.size()) + ")", Utils.COLOR_BLUE)
		for n in treaties:
			_add_nation_button(n)

	# Vassals (gold header)
	var vassals = categories.get("vassals", [])
	if vassals.size() > 0:
		has_any = true
		_add_category_header("Vassals (" + str(vassals.size()) + ")", Utils.COLOR_GOLD)
		for n in vassals:
			_add_nation_button(n)

	# Neutral (gray header)
	var neutral = categories.get("neutral", [])
	if neutral.size() > 0:
		has_any = true
		_add_category_header("Neutral (" + str(neutral.size()) + ")", Utils.COLOR_GREY)
		for n in neutral:
			_add_nation_button(n)

	if not has_any:
		_show_error("No nations in diplomatic contact.")


func _add_category_header(text: String, color: String):
	var lbl = Label.new()
	lbl.text = text
	lbl.add_theme_color_override("font_color", Color("#" + color))
	lbl.add_theme_font_size_override("font_size", 13)
	content_list.add_child(lbl)


func _add_nation_button(nation_data: Dictionary):
	var btn = Button.new()
	var nation_name = str(nation_data.get("name", "?"))
	var state_display = str(nation_data.get("state_display", "?"))
	var text = nation_name + "  —  " + state_display

	# W1: Relation score and descriptor
	var relation = nation_data.get("relation")
	if relation != null:
		var rel_sign = "+" if int(relation) > 0 else ""
		var rel_desc = str(nation_data.get("relation_descriptor", ""))
		text += "  |  " + rel_sign + str(int(relation))
		if rel_desc:
			text += " (" + rel_desc + ")"

	# W2: Active mission indicator
	var has_mission = nation_data.get("has_active_mission", false)
	if has_mission:
		text += "  [MISSION]"

	btn.text = text
	btn.custom_minimum_size = Vector2(0, 36)
	btn.add_theme_font_size_override("font_size", 13)
	btn.pressed.connect(_on_nation_selected.bind(nation_name))
	content_list.add_child(btn)


func _on_nation_selected(nation: String):
	_selected_nation = nation
	_current_step = 2
	back_button.visible = true
	title_label.text = "DIPLOMACY — " + nation
	assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]Loading assessment...[/color]"
	_clear_content_list()
	_add_loading_label()
	_fetch_preview(nation)


# =============================================================================
# STEP 2: ASSESSMENT + ACTIONS
# =============================================================================

func _render_preview(data: Dictionary):
	_clear_content_list()
	scroll_container.scroll_vertical = 0
	_last_preview_data = data  # BPH-B: cache for snapshot lookup
	_dp_available = int(data.get("dp_available", 0))
	dp_label.text = "DP: " + str(_dp_available)
	var pending_envoy_count = int(data.get("pending_envoy_count", 0))

	# PL-30: Same fix as Step 1 — never close+add_output (null-instance crash).
	var dialogue_pending = data.get("dialogue_pending", false)
	if dialogue_pending:
		_add_dialogue_gate_notice(pending_envoy_count)
		return

	# Build assessment panel
	var state_display = str(data.get("current_state_display", "?"))
	var relation = int(data.get("relation", 0))
	var relation_desc = str(data.get("relation_descriptor", "?"))
	var assessment_text = str(data.get("assessment", ""))
	var recommendation = str(data.get("recommendation", ""))
	var is_vassal = data.get("is_vassal", false)

	var rel_sign = "+" if relation > 0 else ""
	var rel_color = Utils.COLOR_INFO
	if relation < -29:
		rel_color = Utils.COLOR_ERROR
	elif relation >= 30:
		rel_color = Utils.COLOR_SUCCESS

	var state_color = Utils.COLOR_INFO
	match str(data.get("current_state", "")):
		"WAR":
			state_color = Utils.COLOR_ERROR
		"ALLIANCE", "DEFENSIVE_ALLIANCE":
			state_color = Utils.COLOR_SUCCESS
		"OPEN_BORDERS", "NON_AGGRESSION":
			state_color = Utils.COLOR_BLUE

	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]TALLEYRAND'S ASSESSMENT — " + _selected_nation.to_upper() + "[/color]\n"
	bbcode += "Status: [color=#" + state_color + "]" + state_display + "[/color]"
	bbcode += "   Relation: [color=#" + rel_color + "]" + rel_sign + str(relation) + " (" + relation_desc + ")[/color]\n"

	# Vassal-specific fields
	if is_vassal:
		var loyalty = int(data.get("vassal_loyalty", 0))
		var autonomy = str(data.get("vassal_autonomy", "?"))
		var trend = str(data.get("vassal_loyalty_trend", "stable"))
		var tribute = int(data.get("vassal_tribute", 0))
		var trend_arrow = "→"
		if trend == "rising":
			trend_arrow = "↑"
		elif trend == "falling":
			trend_arrow = "↓"

		var loyalty_color = Utils.COLOR_SUCCESS
		if loyalty < 25:
			loyalty_color = Utils.COLOR_ERROR
		elif loyalty < 50:
			loyalty_color = Utils.COLOR_ORANGE

		bbcode += "Loyalty: [color=#" + loyalty_color + "]" + str(loyalty) + " " + trend_arrow + "[/color]"
		bbcode += "   Autonomy: " + autonomy
		bbcode += "   Tribute: " + str(tribute) + "g\n"

	if assessment_text:
		bbcode += "\n[color=#" + Utils.COLOR_INFO + "]\"" + assessment_text + "\"[/color]\n"
	if recommendation:
		bbcode += "[color=#" + Utils.COLOR_GOLD + "]Recommendation: " + recommendation + "[/color]\n"

	# W3: Acceptance preview — key factors
	var acceptance_preview = data.get("acceptance_preview")
	if acceptance_preview != null and acceptance_preview is Dictionary:
		var positives = acceptance_preview.get("positive", [])
		var negatives = acceptance_preview.get("negative", [])
		if positives.size() > 0 or negatives.size() > 0:
			bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]KEY FACTORS[/color]\n"
			for p in positives:
				var p_label = str(p.get("label", "?"))
				var p_val = int(p.get("value", 0))
				bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]+ " + p_label + " (+" + str(p_val) + ")[/color]\n"
			for neg in negatives:
				var neg_label = str(neg.get("label", "?"))
				var neg_val = int(neg.get("value", 0))
				bbcode += "  [color=#" + Utils.COLOR_ERROR + "]- " + neg_label + " (" + str(neg_val) + ")[/color]\n"

	# W4: Cooldown pre-check warning
	var actions_list = data.get("actions", [])
	for act in actions_list:
		var disabled_reason = str(act.get("disabled_reason", ""))
		if "cooldown" in disabled_reason.to_lower() or "Cooldown" in disabled_reason:
			bbcode += "\n[color=#" + Utils.COLOR_ORANGE + "]\"We must exercise patience, Sire. " + disabled_reason + " before we may approach them again.\"[/color]\n"
			break

	assessment_panel.text = bbcode

	# Build action buttons
	var actions = data.get("actions", [])
	if actions.size() == 0:
		var lbl = RichTextLabel.new()
		lbl.bbcode_enabled = true
		lbl.fit_content = true
		lbl.scroll_active = false
		lbl.text = "[color=#" + Utils.COLOR_GREY + "]No diplomatic actions available.[/color]"
		content_list.add_child(lbl)
		return

	for action in actions:
		_add_action_button(action)


func _add_action_button(action: Dictionary):
	var display_name = str(action.get("display_name", "?"))
	var dp_cost = int(action.get("dp_cost", 0))
	var gold_cost = int(action.get("gold_cost", 0))
	var available = action.get("available", false)
	var disabled_reason = str(action.get("disabled_reason", ""))
	var likelihood = str(action.get("likelihood", ""))
	var action_id = str(action.get("action", ""))

	# Build button text
	var text = display_name + " (" + str(dp_cost) + " DP"
	if gold_cost > 0:
		text += " + " + str(gold_cost) + "g"
	text += ")"

	# W5: Mission effect text
	var effect_text = str(action.get("effect_text", ""))
	if effect_text and effect_text != "" and effect_text != "null":
		text += "  —  " + effect_text
	elif likelihood and likelihood != "" and likelihood != "null":
		text += "  —  " + likelihood

	if not available and disabled_reason and disabled_reason != "" and disabled_reason != "null":
		text += "  [" + disabled_reason + "]"

	var btn = Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(0, 40)
	btn.add_theme_font_size_override("font_size", 12)
	btn.disabled = not available

	# Color the button text based on likelihood
	if likelihood in _likelihood_colors:
		var color_hex = _likelihood_colors[likelihood]
		btn.add_theme_color_override("font_color", Color("#" + color_hex))

	if available:
		btn.pressed.connect(_on_action_selected.bind(action_id))

	content_list.add_child(btn)


func _on_action_selected(action_id: String):
	"""Build command string and emit for main.gd to execute (§2 Step 3).
	BPH-B: Peace-class actions show a preview panel before emitting."""
	var command = _build_command(action_id, _selected_nation)
	if not command:
		_show_error("Unknown diplomatic action: " + action_id)
		return

	# BPH-B: Intercept peace-class actions for preview panel
	if action_id in PEACE_CLASS_ACTIONS:
		var snapshots = _last_preview_data.get("war_context_snapshots", {})
		var snapshot = snapshots.get(action_id, {}) if snapshots is Dictionary else {}
		if snapshot is Dictionary and snapshot.size() > 0:
			_pending_peace_command = command
			_render_peace_preview(snapshot, action_id)
			return

	_close_wizard()
	command_selected.emit(command)


func _build_command(action_id: String, nation: String) -> String:
	"""Map wizard action ID to the command string the backend expects."""
	match action_id:
		"propose_armistice":
			return "propose armistice with " + nation
		"propose_peace":
			return "propose peace with " + nation
		"propose_open_borders":
			return "propose open borders with " + nation
		"propose_non_aggression":
			return "propose non aggression with " + nation
		"propose_defensive_alliance":
			return "propose defensive alliance with " + nation
		"propose_alliance":
			return "propose alliance with " + nation
		"propose_vassal":
			return "propose vassalization to " + nation
		"declare_war":
			return "declare war on " + nation
		"break_treaty":
			return "break treaty with " + nation
		"downgrade":
			return "downgrade relations with " + nation
		"send_ultimatum":
			return "send ultimatum to " + nation
		"invest_vassal":
			return "invest in " + nation
		"increase_autonomy":
			return "increase autonomy " + nation
		"decrease_autonomy":
			return "decrease autonomy " + nation
		"release_vassal":
			return "release " + nation
		"mission_improve_relations":
			return "improve relations with " + nation
		"mission_court":
			return "court " + nation
		"mission_gather_intel":
			return "gather intel on " + nation
		"mission_reassure":
			return "reassure " + nation
		"mission_undermine":
			return "undermine " + nation
		"cancel_mission":
			return "Talleyrand, cancel mission with " + nation
	return ""


# =============================================================================
# STEP 3: PEACE PREVIEW PANEL (BPH-B)
# =============================================================================

func _render_peace_preview(snapshot: Dictionary, action_id: String):
	"""Render the peace preview panel — war summary, terms, acceptance (BPH-B §8.2)."""
	_current_step = 3
	back_button.visible = true
	_clear_content_list()
	scroll_container.scroll_vertical = 0

	var proposed = str(snapshot.get("proposed_state", "PEACE"))
	title_label.text = "PEACE PREVIEW — " + _selected_nation

	# ── Section 1: War Summary ──
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]WAR SUMMARY[/color]\n"

	var war_score = int(snapshot.get("war_score", 0))
	var score_color = Utils.COLOR_SUCCESS if war_score > 0 else (Utils.COLOR_ERROR if war_score < 0 else Utils.COLOR_INFO)
	var trend = str(snapshot.get("war_score_trend", "stagnant"))
	var trend_arrow = "→"
	if trend == "rising":
		trend_arrow = "↑"
	elif trend == "falling":
		trend_arrow = "↓"
	bbcode += "War Score: [color=#" + score_color + "]" + str(war_score) + " " + trend_arrow + "[/color]"

	var components = snapshot.get("war_score_components", {})
	if components is Dictionary and components.size() > 0:
		bbcode += "  ("
		var parts = []
		var terr = int(components.get("territory", 0))
		if terr != 0:
			parts.append("Territory " + ("+" if terr > 0 else "") + str(terr))
		var bat = int(components.get("battle", 0))
		if bat != 0:
			parts.append("Battles " + ("+" if bat > 0 else "") + str(bat))
		var dec = int(components.get("decisive_battle", 0))
		if dec != 0:
			parts.append("Decisive " + ("+" if dec > 0 else "") + str(dec))
		var cap = int(components.get("capital", 0))
		if cap != 0:
			parts.append("Capital " + ("+" if cap > 0 else "") + str(cap))
		bbcode += ", ".join(parts) + ")\n"
	else:
		bbcode += "\n"

	var duration = int(snapshot.get("war_duration_turns", 0))
	var won = int(snapshot.get("battles_won", 0))
	var lost = int(snapshot.get("battles_lost", 0))
	bbcode += "Duration: " + str(duration) + " turns   Battles: " + str(won) + "W / " + str(lost) + "L\n"

	var dv = int(snapshot.get("decisive_victories", 0))
	var dd = int(snapshot.get("decisive_defeats", 0))
	if dv > 0 or dd > 0:
		bbcode += "Decisive: " + str(dv) + " victories, " + str(dd) + " defeats\n"

	var fc = int(snapshot.get("french_casualties_total", 0))
	var ec = int(snapshot.get("enemy_casualties_total", 0))
	if fc > 0 or ec > 0:
		bbcode += "Casualties: Ours " + Utils.format_number(fc) + " / Theirs " + Utils.format_number(ec) + "\n"

	var held_by_us = snapshot.get("regions_held_by_france", [])
	var held_by_them = snapshot.get("regions_held_by_enemy", [])
	if held_by_us is Array and held_by_us.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_SUCCESS + "]We hold: " + ", ".join(held_by_us) + "[/color]\n"
	if held_by_them is Array and held_by_them.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_ERROR + "]They hold: " + ", ".join(held_by_them) + "[/color]\n"

	# Armistice-specific fields
	if snapshot.has("armistice_remaining_turns"):
		var remaining = int(snapshot.get("armistice_remaining_turns", 0))
		bbcode += "Armistice remaining: " + str(remaining) + " turns\n"

	assessment_panel.text = bbcode

	# ── Section 2: Terms Review ──
	var annotated_terms = snapshot.get("annotated_terms", [])
	if annotated_terms is Array and annotated_terms.size() > 0:
		var terms_lbl = RichTextLabel.new()
		terms_lbl.bbcode_enabled = true
		terms_lbl.fit_content = true
		terms_lbl.scroll_active = false

		var terms_bbcode = "[color=#" + Utils.COLOR_HEADER + "]PROPOSED TERMS[/color]\n"

		# Group by direction
		var demands = []
		var concessions = []
		var mutual = []
		for term in annotated_terms:
			if not term is Dictionary:
				continue
			var direction = str(term.get("term_direction", ""))
			match direction:
				"demand":
					demands.append(term)
				"concession":
					concessions.append(term)
				_:
					mutual.append(term)

		if demands.size() > 0:
			terms_bbcode += "[color=#" + Utils.COLOR_SUCCESS + "]France demands:[/color]\n"
			for t in demands:
				terms_bbcode += "  • " + str(t.get("display_label", "?")) + "\n"
		if concessions.size() > 0:
			terms_bbcode += "[color=#" + Utils.COLOR_ERROR + "]France concedes:[/color]\n"
			for t in concessions:
				terms_bbcode += "  • " + str(t.get("display_label", "?")) + "\n"
		if mutual.size() > 0:
			terms_bbcode += "[color=#" + Utils.COLOR_INFO + "]Mutual:[/color]\n"
			for t in mutual:
				terms_bbcode += "  • " + str(t.get("display_label", "?")) + "\n"

		# Harshness assessment
		var harshness_label = str(snapshot.get("harshness_label", ""))
		if harshness_label:
			var h_color = Utils.COLOR_INFO
			match harshness_label:
				"generous":
					h_color = Utils.COLOR_SUCCESS
				"balanced":
					h_color = Utils.COLOR_BLUE
				"harsh":
					h_color = COLOR_ORANGE
				"punitive":
					h_color = Utils.COLOR_ERROR
			terms_bbcode += "Assessment: [color=#" + h_color + "]" + harshness_label.to_upper() + "[/color]\n"

		terms_lbl.text = terms_bbcode
		content_list.add_child(terms_lbl)

	# ── Section 2b: Acceptance Preview ──
	var acceptance = snapshot.get("acceptance_preview", {})
	if acceptance is Dictionary and acceptance.size() > 0:
		var acc_lbl = RichTextLabel.new()
		acc_lbl.bbcode_enabled = true
		acc_lbl.fit_content = true
		acc_lbl.scroll_active = false

		var acc_score = int(acceptance.get("score", 0))
		var acc_outcome = str(acceptance.get("outcome", "?"))
		var outcome_color = Utils.COLOR_INFO
		match acc_outcome:
			"ACCEPT":
				outcome_color = Utils.COLOR_SUCCESS
			"COUNTER":
				outcome_color = COLOR_YELLOW
			"REJECT":
				outcome_color = Utils.COLOR_ERROR

		var acc_bbcode = "[color=#" + Utils.COLOR_HEADER + "]ACCEPTANCE ESTIMATE[/color]\n"
		acc_bbcode += "Score: [color=#" + outcome_color + "]" + str(acc_score) + " — " + acc_outcome + "[/color]\n"

		var lp = str(acceptance.get("largest_positive", ""))
		var ln = str(acceptance.get("largest_negative", ""))
		if lp:
			acc_bbcode += "[color=#" + Utils.COLOR_SUCCESS + "]Key advantage: " + lp + "[/color]\n"
		if ln:
			acc_bbcode += "[color=#" + Utils.COLOR_ERROR + "]Key obstacle: " + ln + "[/color]\n"

		acc_lbl.text = acc_bbcode
		content_list.add_child(acc_lbl)

	# ── Section 3: Political Consequences (placeholder for BPH-C) ──
	var fallout = snapshot.get("fallout_warnings", [])
	var conflicts = snapshot.get("commitment_conflicts", [])
	if (fallout is Array and fallout.size() > 0) or (conflicts is Array and conflicts.size() > 0):
		var pol_lbl = RichTextLabel.new()
		pol_lbl.bbcode_enabled = true
		pol_lbl.fit_content = true
		pol_lbl.scroll_active = false
		var pol_bbcode = "[color=#" + Utils.COLOR_HEADER + "]POLITICAL CONSEQUENCES[/color]\n"
		for w in fallout:
			pol_bbcode += "[color=#" + COLOR_ORANGE + "]⚠ " + str(w) + "[/color]\n"
		for c in conflicts:
			pol_bbcode += "[color=#" + Utils.COLOR_ERROR + "]⚠ " + str(c) + "[/color]\n"
		pol_lbl.text = pol_bbcode
		content_list.add_child(pol_lbl)

	# ── Confirm / Back buttons ──
	var spacer = Control.new()
	spacer.custom_minimum_size = Vector2(0, 8)
	content_list.add_child(spacer)

	var btn_row = HBoxContainer.new()
	btn_row.custom_minimum_size = Vector2(0, 44)

	var confirm_btn = Button.new()
	confirm_btn.text = "Send Proposal"
	confirm_btn.custom_minimum_size = Vector2(200, 40)
	confirm_btn.add_theme_font_size_override("font_size", 14)
	confirm_btn.add_theme_color_override("font_color", Color("#" + Utils.COLOR_SUCCESS))
	confirm_btn.pressed.connect(_on_peace_confirmed)
	btn_row.add_child(confirm_btn)

	var gap = Control.new()
	gap.custom_minimum_size = Vector2(16, 0)
	gap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn_row.add_child(gap)

	var back_btn = Button.new()
	back_btn.text = "Reconsider"
	back_btn.custom_minimum_size = Vector2(160, 40)
	back_btn.add_theme_font_size_override("font_size", 14)
	back_btn.pressed.connect(_go_back)
	btn_row.add_child(back_btn)

	content_list.add_child(btn_row)


func _on_peace_confirmed():
	"""BPH-B: Player confirmed the peace proposal after reviewing the preview."""
	if _pending_peace_command:
		var cmd = _pending_peace_command
		_pending_peace_command = ""
		_close_wizard()
		command_selected.emit(cmd)


# =============================================================================
# HELPERS
# =============================================================================

func _clear_content_list():
	for child in content_list.get_children():
		child.queue_free()


func _add_loading_label():
	var lbl = Label.new()
	lbl.text = "Loading..."
	lbl.add_theme_color_override("font_color", Color("#" + Utils.COLOR_INFO))
	lbl.add_theme_font_size_override("font_size", 12)
	content_list.add_child(lbl)


func _add_dialogue_gate_notice(pending_envoy_count: int):
	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	if pending_envoy_count > 0:
		lbl.text = "[color=#" + COLOR_ORANGE + "]An unanswered envoy awaits your reply. Reopen Envoys before starting a new diplomatic action.[/color]"
	else:
		lbl.text = "[color=#" + COLOR_ORANGE + "]Resolve the active diplomatic dialogue before starting a new action.[/color]"
	content_list.add_child(lbl)
	if pending_envoy_count > 0:
		_add_open_envoys_button(pending_envoy_count)


func _add_open_envoys_button(pending_envoy_count: int):
	var btn = Button.new()
	btn.text = "Open Envoys (%d)" % pending_envoy_count
	btn.custom_minimum_size = Vector2(0, 38)
	btn.add_theme_font_size_override("font_size", 12)
	btn.pressed.connect(_on_open_envoys_pressed)
	content_list.add_child(btn)


func _on_open_envoys_pressed():
	_close_wizard()
	open_envoys_requested.emit()

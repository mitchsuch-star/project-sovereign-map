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
signal structured_command_selected(command: String, data: Dictionary)
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
var _current_step: int = 0  # 0=hidden, 1=nations, 2=actions
var _selected_nation: String = ""
var _dp_available: int = 0

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
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport. Both
	# open paths clamp — the wizard is reachable from F1 and from the war
	# panel handoff, and only clamping one would leave the other overflowing.
	Utils.clamp_centered_panel($PanelContainer)
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
	title_label.text = "DIPLOMACY — " + Utils.display_nation_name(nation)
	assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]Loading assessment...[/color]"
	_clear_content_list()
	_add_loading_label()
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport. Both
	# open paths clamp — the wizard is reachable from F1 and from the war
	# panel handoff, and only clamping one would leave the other overflowing.
	Utils.clamp_centered_panel($PanelContainer)
	_fetch_preview(nation)


func _close_wizard():
	_current_step = 0
	_selected_nation = ""
	_request_in_flight = false
	if _http:
		_http.cancel_request()
	hide()


func _go_back():
	"""Return to previous step."""
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
	var text = Utils.display_nation_name(nation_name) + "  —  " + state_display

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
	# UI-6: period heraldry as the leading icon (untinted — colored art)
	Utils.apply_flag_icon(btn, nation_name)
	btn.pressed.connect(_on_nation_selected.bind(nation_name))
	content_list.add_child(btn)


func _on_nation_selected(nation: String):
	_selected_nation = nation
	_current_step = 2
	back_button.visible = true
	title_label.text = "DIPLOMACY — " + Utils.display_nation_name(nation)
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
	bbcode += Utils.bb_flag(_selected_nation, 16)
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]TALLEYRAND'S ASSESSMENT — " + Utils.display_nation_name(_selected_nation).to_upper() + "[/color]\n"
	bbcode += "Status: [color=#" + state_color + "]" + state_display + "[/color]"
	bbcode += "   Relation: [color=#" + rel_color + "]" + rel_sign + str(relation) + " (" + relation_desc + ")[/color]\n"

	# Vassal-specific fields
	if is_vassal:
		var loyalty = int(data.get("vassal_loyalty", 0))
		var autonomy = str(data.get("vassal_autonomy", "?"))
		var trend = str(data.get("vassal_loyalty_trend", "stable"))
		var tribute = int(data.get("vassal_tribute", 0))
		var trend_arrow = ""
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
	var disabled_reason = str(action.get("disabled_reason_display", action.get("error_display", action.get("disabled_reason", ""))))
	var likelihood = str(action.get("likelihood", ""))
	var action_id = str(action.get("action", ""))

	# Build button text
	var text = display_name
	var costs = []
	if dp_cost > 0:
		costs.append(str(dp_cost) + " DP")
	if gold_cost > 0:
		costs.append(str(gold_cost) + "g")
	if costs.size() > 0:
		text += " (" + " + ".join(PackedStringArray(costs)) + ")"

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
		btn.pressed.connect(_on_action_selected.bind(action_id, action))

	content_list.add_child(btn)

	# May 24, 2026 audit punch list Tier 2: multi-war ambiguity in-wizard
	# rescue. When the backend marks the action unavailable with
	# `error="multi_war_ambiguity"` and surfaces `available_wars`, render
	# a clickable per-war picker below the disabled action button so the
	# player can pick a specific `war_id` without leaving the wizard.
	# Each picker button reuses `_on_action_selected` with the original
	# `action_id` and a payload clone carrying the chosen `war_id`,
	# which `_structured_payload_for_action` then forwards to the backend.
	var error_code = str(action.get("error", ""))
	var available_wars = action.get("available_wars", [])
	if not available and error_code == "multi_war_ambiguity" and available_wars is Array and available_wars.size() > 0:
		var picker_label = RichTextLabel.new()
		picker_label.bbcode_enabled = true
		picker_label.fit_content = true
		picker_label.scroll_active = false
		picker_label.text = "  [color=#a0a0a0][i]Pick a war to settle:[/i][/color]"
		content_list.add_child(picker_label)
		for war_entry in available_wars:
			var war_str = str(war_entry)
			var war_btn = Button.new()
			war_btn.text = "    \u21B3 " + war_str
			war_btn.custom_minimum_size = Vector2(0, 30)
			war_btn.add_theme_font_size_override("font_size", 11)
			var picker_payload = action.duplicate(true)
			picker_payload["war_id"] = war_str
			war_btn.pressed.connect(_on_action_selected.bind(action_id, picker_payload))
			content_list.add_child(war_btn)

	# VS-3 (Vassal Depth, July 2026): positive-path province picker for the
	# land grant. Unlike the multi-war rescue above (an error-path picker),
	# this renders under an AVAILABLE action: one button per eligible
	# province, each stating its terms (income handoff + worth-scaled
	# loyalty + the vassal's tribute cut). Each pick clones the payload with
	# the chosen `region`, which _structured_payload_for_action forwards as
	# the structured POST field (CommandRequest.region).
	var eligible_regions = action.get("eligible_regions", [])
	if available and action_id == "grant_region_to_vassal" and eligible_regions is Array and eligible_regions.size() > 0:
		var grant_label = RichTextLabel.new()
		grant_label.bbcode_enabled = true
		grant_label.fit_content = true
		grant_label.scroll_active = false
		grant_label.text = "  [color=#a0a0a0][i]Pick a province to cede:[/i][/color]"
		content_list.add_child(grant_label)
		for region_entry in eligible_regions:
			if not (region_entry is Dictionary):
				continue
			var region_name = str(region_entry.get("region", ""))
			if region_name == "":
				continue
			var income = int(region_entry.get("income", 0))
			var loyalty_gain = int(region_entry.get("loyalty_gain", 0))
			var tribute_pct = int(region_entry.get("tribute_pct", 0))
			var region_btn = Button.new()
			region_btn.text = "    \u21B3 %s \u2014 income %dg, loyalty +%d, they remit %d%%" % [region_name, income, loyalty_gain, tribute_pct]
			region_btn.custom_minimum_size = Vector2(0, 30)
			region_btn.add_theme_font_size_override("font_size", 11)
			var region_payload = action.duplicate(true)
			region_payload["region"] = region_name
			region_btn.pressed.connect(_on_action_selected.bind(action_id, region_payload))
			content_list.add_child(region_btn)


func _on_action_selected(action_id: String, action_payload: Dictionary = {}):
	"""Build command string and emit for main.gd to execute (§2 Step 3).
	Peace-class proposal previews render in the canonical proposal confirmation popup.

	When the action carries structured backend metadata (e.g. `war_id` for
	`open_settlement` so the war-detail-popup-equivalent path can scope the
	settlement to the correct war_instance), emit the structured signal so
	main.gd can call `send_structured_command` instead of free-text parsing.
	"""
	var command = _build_command(action_id, _selected_nation)
	if not command:
		_show_error("Unknown diplomatic action: " + action_id)
		return

	var structured_data = _structured_payload_for_action(action_id, action_payload)

	_close_wizard()
	if structured_data.is_empty():
		command_selected.emit(command)
	else:
		structured_command_selected.emit(command, structured_data)
	return


func _structured_payload_for_action(action_id: String, action_payload: Dictionary) -> Dictionary:
	"""Return the structured POST fields the backend should receive alongside
	the free-text command. `open_settlement` and `propose_white_peace`
	(SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1) both consume this so the
	wizard preserves the wizard's selected `war_id`; other actions return
	an empty dict (which routes through the legacy free-text command path).
	Spec line 352: `propose_white_peace` is structured-only on the wizard
	surface — the typed `propose white peace with X` echo is display copy,
	not a parser dependency."""
	if action_id == "open_settlement":
		var war_id = str(action_payload.get("war_id", ""))
		var data = {
			"action": "propose_common_peace",
			"target_nation": _selected_nation,
		}
		if war_id != "":
			data["war_id"] = war_id
		return data
	if action_id == "propose_white_peace":
		var war_id = str(action_payload.get("war_id", ""))
		var data = {
			"action": "propose_white_peace",
			"target_nation": _selected_nation,
		}
		if war_id != "":
			data["war_id"] = war_id
		return data
	if action_id == "grant_region_to_vassal":
		# VS-3: the sub-picker's chosen province rides the structured
		# `region` field. Clicking the parent button without a pick sends
		# no region — the backend answers with the eligible list.
		var grant_region = str(action_payload.get("region", ""))
		var grant_data = {
			"action": "grant_region_to_vassal",
			"target_nation": _selected_nation,
		}
		if grant_region != "":
			grant_data["region"] = grant_region
		return grant_data
	return {}


func _build_command(action_id: String, nation: String) -> String:
	"""Map wizard action ID to the command string the backend expects."""
	match action_id:
		"propose_armistice":
			return "propose armistice with " + nation
		"propose_peace":
			return "propose peace with " + nation
		"open_settlement":
			return "propose common peace with " + nation
		"propose_white_peace":
			# SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1: labeled
			# white-peace echo. Structured payload routes the action;
			# the typed string is display copy only — the backend
			# parser does not auto-classify "white peace".
			return "propose white peace with " + nation
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
		"grant_region_to_vassal":
			# VS-3: display echo — the structured payload carries the region
			return "cede territory to " + nation
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

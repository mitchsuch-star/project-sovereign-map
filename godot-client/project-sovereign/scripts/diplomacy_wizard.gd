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

# State
var _current_step: int = 0  # 0=hidden, 1=nations, 2=actions
var _selected_nation: String = ""
var _dp_available: int = 0

# Color palette
const COLOR_GOLD = "d9c08c"
const COLOR_RED = "cd6b6b"
const COLOR_GREEN = "8fbc8f"
const COLOR_BLUE = "6495ed"
const COLOR_GREY = "808080"
const COLOR_INFO = "a0a0a8"
const COLOR_HEADER = "B8860B"
const COLOR_AMBER = "daa06d"
const COLOR_LIGHT_GREEN = "a0d0a0"
const COLOR_LIGHT_RED = "d9a0a0"
const COLOR_ORANGE = "d9a060"
const COLOR_YELLOW = "d9d080"

# Likelihood color mapping (§3a) — keys must match get_likelihood_descriptor() exactly
var _likelihood_colors: Dictionary = {
	"Almost Certain": COLOR_GREEN,
	"Favorable": COLOR_LIGHT_GREEN,
	"Uncertain — may counter": COLOR_YELLOW,
	"Doubtful — expect counter": COLOR_ORANGE,
	"Unlikely": COLOR_LIGHT_RED,
	"Hopeless": COLOR_RED,
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


func open():
	"""Open wizard at Step 1 — fetch and show nation list."""
	_current_step = 1
	_selected_nation = ""
	title_label.text = "DIPLOMACY"
	assessment_panel.text = "[color=#" + COLOR_INFO + "]\"Your Excellency, which nation requires our diplomatic attention?\"[/color]"
	back_button.visible = false
	_clear_content_list()
	_add_loading_label()
	show()
	_fetch_nations()


func _close_wizard():
	_current_step = 0
	_selected_nation = ""
	if _http:
		_http.cancel_request()
	hide()


func _go_back():
	"""Return to Step 1 from Step 2."""
	if _current_step == 2:
		_current_step = 1
		_selected_nation = ""
		back_button.visible = false
		title_label.text = "DIPLOMACY"
		assessment_panel.text = "[color=#" + COLOR_INFO + "]\"Your Excellency, which nation requires our diplomatic attention?\"[/color]"
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
	var error = _http.request(API_URL + "/diplomatic_preview")
	if error != OK:
		_show_error("Failed to connect to headquarters.")


func _fetch_preview(nation: String):
	"""Fetch diplomatic preview for Step 2."""
	_http.cancel_request()
	_request_id += 1
	_pending_request = "preview"
	var url = API_URL + "/diplomatic_preview?nation=" + nation.uri_encode()
	var error = _http.request(url)
	if error != OK:
		_show_error("Failed to fetch diplomatic preview.")


func _on_http_completed(result, response_code, headers, body):
	if not visible:
		return
	# Capture the request ID at response time to detect stale responses
	var response_id = _request_id
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

	# Discard stale responses (user navigated away before response arrived)
	if response_id != _request_id:
		return

	if _pending_request == "nations":
		_render_nations(data)
	elif _pending_request == "preview":
		_render_preview(data)


func _show_error(msg: String):
	_clear_content_list()
	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	lbl.text = "[color=#" + COLOR_RED + "]" + msg + "[/color]"
	content_list.add_child(lbl)


# =============================================================================
# STEP 1: NATION LIST
# =============================================================================

func _render_nations(data: Dictionary):
	_clear_content_list()
	scroll_container.scroll_vertical = 0
	_dp_available = int(data.get("dp_available", 0))
	dp_label.text = "DP: " + str(_dp_available)

	var dialogue_pending = data.get("dialogue_pending", false)
	if dialogue_pending:
		assessment_panel.text = "[color=#" + COLOR_AMBER + "]\"Talleyrand awaits your response to the current diplomatic matter.\"[/color]"
		_close_wizard()
		return

	var categories = data.get("categories", {})
	var has_any = false

	# At War (red header)
	var at_war = categories.get("at_war", [])
	if at_war.size() > 0:
		has_any = true
		_add_category_header("At War (" + str(at_war.size()) + ")", COLOR_RED)
		for n in at_war:
			_add_nation_button(n)

	# Treaties (blue header)
	var treaties = categories.get("treaties", [])
	if treaties.size() > 0:
		has_any = true
		_add_category_header("Treaties (" + str(treaties.size()) + ")", COLOR_BLUE)
		for n in treaties:
			_add_nation_button(n)

	# Vassals (gold header)
	var vassals = categories.get("vassals", [])
	if vassals.size() > 0:
		has_any = true
		_add_category_header("Vassals (" + str(vassals.size()) + ")", COLOR_GOLD)
		for n in vassals:
			_add_nation_button(n)

	# Neutral (gray header)
	var neutral = categories.get("neutral", [])
	if neutral.size() > 0:
		has_any = true
		_add_category_header("Neutral (" + str(neutral.size()) + ")", COLOR_GREY)
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
	btn.text = nation_name + "  —  " + state_display
	btn.custom_minimum_size = Vector2(0, 36)
	btn.add_theme_font_size_override("font_size", 13)
	btn.pressed.connect(_on_nation_selected.bind(nation_name))
	content_list.add_child(btn)


func _on_nation_selected(nation: String):
	_selected_nation = nation
	_current_step = 2
	back_button.visible = true
	title_label.text = "DIPLOMACY — " + nation
	assessment_panel.text = "[color=#" + COLOR_INFO + "]Loading assessment...[/color]"
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

	# Check if dialogue became pending since we fetched
	var dialogue_pending = data.get("dialogue_pending", false)
	if dialogue_pending:
		assessment_panel.text = "[color=#" + COLOR_AMBER + "]\"Talleyrand awaits your response to the current diplomatic matter.\"[/color]"
		_close_wizard()
		return

	# Build assessment panel
	var state_display = str(data.get("current_state_display", "?"))
	var relation = int(data.get("relation", 0))
	var relation_desc = str(data.get("relation_descriptor", "?"))
	var assessment_text = str(data.get("assessment", ""))
	var recommendation = str(data.get("recommendation", ""))
	var is_vassal = data.get("is_vassal", false)

	var rel_sign = "+" if relation > 0 else ""
	var rel_color = COLOR_INFO
	if relation < -29:
		rel_color = COLOR_RED
	elif relation >= 30:
		rel_color = COLOR_GREEN

	var state_color = COLOR_INFO
	match str(data.get("current_state", "")):
		"WAR":
			state_color = COLOR_RED
		"ALLIANCE", "DEFENSIVE_ALLIANCE":
			state_color = COLOR_GREEN
		"OPEN_BORDERS", "NON_AGGRESSION":
			state_color = COLOR_BLUE

	var bbcode = ""
	bbcode += "[color=#" + COLOR_HEADER + "]TALLEYRAND'S ASSESSMENT — " + _selected_nation.to_upper() + "[/color]\n"
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

		var loyalty_color = COLOR_GREEN
		if loyalty < 25:
			loyalty_color = COLOR_RED
		elif loyalty < 50:
			loyalty_color = COLOR_AMBER

		bbcode += "Loyalty: [color=#" + loyalty_color + "]" + str(loyalty) + " " + trend_arrow + "[/color]"
		bbcode += "   Autonomy: " + autonomy
		bbcode += "   Tribute: " + str(tribute) + "g\n"

	if assessment_text:
		bbcode += "\n[color=#" + COLOR_INFO + "]\"" + assessment_text + "\"[/color]\n"
	if recommendation:
		bbcode += "[color=#" + COLOR_GOLD + "]Recommendation: " + recommendation + "[/color]"

	assessment_panel.text = bbcode

	# Build action buttons
	var actions = data.get("actions", [])
	if actions.size() == 0:
		var lbl = RichTextLabel.new()
		lbl.bbcode_enabled = true
		lbl.fit_content = true
		lbl.scroll_active = false
		lbl.text = "[color=#" + COLOR_GREY + "]No diplomatic actions available.[/color]"
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

	if likelihood and likelihood != "" and likelihood != "null":
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
	"""Build command string and emit for main.gd to execute (§2 Step 3)."""
	var command = _build_command(action_id, _selected_nation)
	if command:
		_close_wizard()
		command_selected.emit(command)
	else:
		_show_error("Unknown diplomatic action: " + action_id)


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
	lbl.add_theme_color_override("font_color", Color("#" + COLOR_INFO))
	lbl.add_theme_font_size_override("font_size", 12)
	content_list.add_child(lbl)

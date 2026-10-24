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
# GE-3: "View the table" — main.gd opens the Diplomatic Ledger on its
# CONGRESS tab (top_bar.open_diplomatic_ledger_review("ledger_congress")).
signal open_congress_requested
# S14d (docs/TABLE_LESSON_SPEC.md §2 lines 1–2): a first-open line was drawn at
# the head of a view — main.gd acknowledges it through the api_client queue.
signal first_open_seen(screen: String)

# GE-3 (ENDGAME_PLAN §2.3): the summons is the typed verb the backend's own
# payload names (`congress.SUMMON_COMMAND`); main.gd sends it through the
# ordinary typed pipeline (history, terminal echo). It names no court, so it
# is NOT a `_build_command` arm (every arm there echoes a court — CN-4).
const CONGRESS_SUMMON_COMMAND := "summon the congress"

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
var _current_step: int = 0  # 0=hidden, 1=nations, 2=actions, 3=formables (NA-6d), 4=the Emperor's designs (VP-1)
var _selected_nation: String = ""
var _dp_available: int = 0

# Color palette
# SF7-X28 (Score Finish Step 7, the frames, Oct 5 2026): the Formable
# Nations step laid its two-line quote out like Talleyrand's assessment (an
# expanding region), so a blank band sat between the quote and the list.
# True = step 3 hugs its quote; false = the expanding layout.
const THE_FORMABLES_PROMPT_HUGS_ITS_QUOTE := true

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
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(assessment_panel)
	Utils.keep_whole_lines(scroll_container)
	hide()
	close_button.pressed.connect(_close_wizard)
	# UXR3-F5: the drawn cross every screen closes with.
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	close_button.tooltip_text = "Close (Esc)"
	# S14D-X10 (October 23, 2026): the header spells its currency — the
	# Cabinet's first-open line does too, once; the tooltip stands.
	dp_label.tooltip_text = "Diplomatic points (DP) — the Cabinet's currency: every act here is priced in them, and they return each turn."
	cancel_button.pressed.connect(_close_wizard)
	back_button.pressed.connect(_go_back)
	background_overlay.gui_input.connect(_on_overlay_input)
	# LV-15 (row EP F3): the list never scrolls sideways — a chip that is
	# wider than the panel WRAPS (see _add_action_button) instead of dragging
	# a horizontal scrollbar under the list with its gate reason clipped off.
	scroll_container.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	# DDB-7 (Pre-Deploy S13b): a list taller than its pane says so — "▼ more
	# below" under the list, on the Caption step and the info token, hidden
	# once the list is read to its end (conquest #22: the recommended mission
	# sat below the fold with no cue).
	_more_below = Label.new()
	_more_below.text = "▼ more below"
	_more_below.theme_type_variation = &"Caption"
	_more_below.add_theme_color_override("font_color", Color("#" + Utils.COLOR_INFO))
	_more_below.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_more_below.visible = false
	var list_box: Node = scroll_container.get_parent()
	list_box.add_child(_more_below)
	list_box.move_child(_more_below, scroll_container.get_index() + 1)
	var list_bar: VScrollBar = scroll_container.get_v_scroll_bar()
	list_bar.value_changed.connect(func(_v): _update_more_below())
	list_bar.changed.connect(_update_more_below)

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
	title_label.text = "THE CABINET"
	assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]\"Your Excellency, which nation requires our diplomatic attention?\"[/color]"
	_lay_out_prompt(1)
	back_button.visible = false
	dp_label.text = ""
	_clear_content_list()
	_add_loading_label()
	AudioManager.play("panel_open")
	AudioManager.start_loop("crowd")
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport. Both
	# open paths clamp — the wizard is reachable from F1 and from the war
	# panel handoff, and only clamping one would leave the other overflowing.
	# (Row EP F3: the clamp lives in ONE place, `refit`.)
	refit()
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
	title_label.text = "THE CABINET — " + Utils.display_nation_name(nation)
	assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]Loading assessment...[/color]"
	_lay_out_prompt(2)
	_clear_content_list()
	_add_loading_label()
	AudioManager.play("panel_open")
	AudioManager.start_loop("crowd")
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport. Both
	# open paths clamp — the wizard is reachable from F1 and from the war
	# panel handoff, and only clamping one would leave the other overflowing.
	# (Row EP F3: the clamp lives in ONE place, `refit`.)
	refit()
	_fetch_preview(nation)


func refit() -> void:
	"""Fit the panel to the CURRENT logical viewport — what `open` and
	`open_for_nation` do on their own road. Public so a surface rendered
	OFFLINE (the IQ-10 capture harness feeds `_render_nations` /
	`_render_preview` a captured payload instead of fetching it) fits the
	way the live wizard does, and so a later Interface Scale change can
	refit an open wizard without re-fetching."""
	Utils.clamp_centered_panel($PanelContainer)


func _lay_out_prompt(step: int) -> void:
	"""LV-20 (row EP F3): on step 1 the prompt is ONE line and the nation list
	sits directly under it. The scene authors the assessment panel as an
	expanding region (half the slack, for Talleyrand's step-2 assessment), so
	on step 1 it opened a blank gap the height of an assessment that had not
	been written. Step 1 pins it to a one-line floor; steps 2 and 3 expand."""
	if assessment_panel == null:
		return
	if step == 1:
		assessment_panel.size_flags_vertical = Control.SIZE_FILL
		assessment_panel.custom_minimum_size.y = 40.0
	elif step == 3 and THE_FORMABLES_PROMPT_HUGS_ITS_QUOTE:
		# SF7-X28: step 3's prompt is a fixed two-line quote, not an
		# assessment — expanding it opened a blank band above the list.
		assessment_panel.size_flags_vertical = Control.SIZE_FILL
		assessment_panel.custom_minimum_size.y = 56.0
	elif step == 4:
		# VP-1: the road page's prompt is a fixed quote too (step 3's rule).
		assessment_panel.size_flags_vertical = Control.SIZE_FILL
		assessment_panel.custom_minimum_size.y = 56.0
	else:
		assessment_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
		assessment_panel.custom_minimum_size.y = 56.0


# EA-E5 (SF-RR5, October 21, 2026): step 2's assessment keeps Talleyrand's
# counsel in view. Its share of the panel (half the chip list's) was 75 px at
# Interface Scale 2.0 — the heading and the status line, the counsel below its
# own fold. Its floor is its first ASSESSMENT_FLOOR_LINES lines (the heading,
# the status, the space, the counsel's opening two), never more than the text
# it holds; the chip list scrolls under its "more below".
const ASSESSMENT_FLOOR_LINES := 5


func _fit_assessment() -> void:
	await get_tree().process_frame
	if assessment_panel == null or not visible or _current_step != 2:
		return
	var lines: int = assessment_panel.get_line_count()
	var upto: float = float(assessment_panel.get_content_height())
	if lines > ASSESSMENT_FLOOR_LINES:
		upto = float(assessment_panel.get_line_offset(ASSESSMENT_FLOOR_LINES))
	var box: StyleBox = assessment_panel.get_theme_stylebox("normal")
	var top: float = box.get_margin(SIDE_TOP) if box else 0.0
	assessment_panel.custom_minimum_size.y = maxf(56.0, ceilf(upto + top + 6.0))
	refit()


func _close_wizard():
	if visible:
		AudioManager.play("panel_close")
	AudioManager.stop_loop("crowd")
	_current_step = 0
	_selected_nation = ""
	_request_in_flight = false
	if _http:
		_http.cancel_request()
	hide()


func _go_back():
	"""Return to previous step."""
	if _current_step == 2 or _current_step == 3 or _current_step == 4:
		_current_step = 1
		_selected_nation = ""
		back_button.visible = false
		title_label.text = "THE CABINET"
		assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]\"Your Excellency, which nation requires our diplomatic attention?\"[/color]"
		_lay_out_prompt(1)
		_clear_content_list()
		_add_loading_label()
		_fetch_nations()


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		_close_wizard()


# =============================================================================
# HTTP REQUESTS
# =============================================================================

var API_URL: String = Utils.backend_url()  # Golden Rule 7 single source

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


func _fetch_formables():
	"""Fetch the formable-world browser for Step 3 (NA-6d §11.6-8)."""
	_http.cancel_request()
	_request_id += 1
	_pending_request = "formables"
	_request_in_flight = true
	var error = _http.request(API_URL + "/formables")
	if error != OK:
		_request_in_flight = false
		_show_error("Failed to fetch the formable nations.")


func _fetch_designs():
	"""Fetch the road page for Step 4 (VP-1, the Emperor's Designs)."""
	_http.cancel_request()
	_request_id += 1
	_pending_request = "designs"
	_request_in_flight = true
	var error = _http.request(API_URL + "/imperial_designs")
	if error != OK:
		_request_in_flight = false
		_show_error("Failed to fetch the Emperor's designs.")


func _on_http_completed(result, response_code, headers, body):
	_request_in_flight = false
	if not visible:
		return
	# S14D-X33 (October 23, 2026): the "stale response" guard that stood here
	# compared `_request_id` with itself and never fired; `cancel_request()` on
	# the Back road is what discards a page the player has left.
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
	elif _pending_request == "formables":
		_render_formables(data)
	elif _pending_request == "designs":
		# A page the player has left (Back) is never drawn over the nation
		# list — this step check is the real guard (S14D-X33).
		if _current_step == 4:
			_render_designs(data)


func _show_error(msg: String):
	_current_step = 1  # Reset step so back button works (Fix 7)
	# S14D-X32 (October 23, 2026): the error view is step 1's — never stranded
	# under a page's title (THE EMPEROR'S DESIGNS) with no Back.
	title_label.text = "THE CABINET"
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

	_add_first_open_line(data)

	# GE-3 (ENDGAME_PLAN §2.3): "The Congress of Paris" — the ending's
	# summons, at the very top, with its honest-availability gate terms. The
	# backend sends the row only on a world whose ending is authored (the
	# tutorial and the bare flag world send null — no row).
	_last_nations_data = data
	_add_congress_row(data.get("congress"))
	# VP-1 (S14b part 2): the Emperor's Designs — the road page's door, right
	# under the Congress (the backend sends null where no designs are authored).
	_add_designs_row(data.get("designs"))

	# NA-6d §11.6-8: the Formables button — the assured, always-reachable
	# browser for the formable world. Top of the list, never hidden.
	_add_formables_button()

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
		_add_category_header("Neutral (" + str(neutral.size()) + ")", Utils.COLOR_INFO)
		for n in neutral:
			_add_nation_button(n)

	if not has_any:
		_show_error("No nations in diplomatic contact.")


func _add_category_header(text: String, color: String):
	var lbl = Label.new()
	lbl.text = text
	lbl.add_theme_color_override("font_color", Color("#" + color))
	lbl.theme_type_variation = &"Caption"
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
	btn.theme_type_variation = &"CaptionButton"
	# UI-6: period heraldry as the leading icon (untinted — colored art)
	Utils.apply_flag_icon(btn, nation_name)
	btn.pressed.connect(_on_nation_selected.bind(nation_name))
	content_list.add_child(btn)


func _on_nation_selected(nation: String):
	_selected_nation = nation
	_current_step = 2
	back_button.visible = true
	title_label.text = "THE CABINET — " + Utils.display_nation_name(nation)
	assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]Loading assessment...[/color]"
	_lay_out_prompt(2)
	_clear_content_list()
	_add_loading_label()
	_fetch_preview(nation)


# =============================================================================
# STEP 1: THE CONGRESS OF PARIS (GE-3 — ENDGAME_PLAN §2.3)
# =============================================================================
# A slice of the ONE payload (`congress.build_congress_payload`, carried on
# /diplomatic_preview's nation list as `congress`). Null-safe on every key:
# bool(null) / int(null) / `for x in null` are Godot runtime errors, and a
# present-but-null key survives `.get(key, default)`.

func _congress_tint(severity: String) -> String:
	match severity:
		"critical":
			return Utils.COLOR_ERROR
		"warning":
			return Utils.COLOR_BATTLE
		"paused":
			return Utils.COLOR_INFO
	return Utils.COLOR_GOLD


# UXR3-28 / 78 (Pre-Deploy S12 part 2): the Congress row is ONE line above
# the court list — its name and where it stands, with [Summon] and [View the
# table] beside it — and its terms fold behind "▸ the terms". Unfolded it
# filled the list's whole first screen: no court and no Formable Nations
# entry was in view on step 1, the step whose question is "which nation?".
var _congress_terms_open := false
var _last_nations_data: Dictionary = {}


func _toggle_congress_terms() -> void:
	_congress_terms_open = not _congress_terms_open
	if not _last_nations_data.is_empty():
		var keep: int = scroll_container.scroll_vertical
		_render_nations(_last_nations_data)
		scroll_container.scroll_vertical = keep


func _on_congress_meta(meta) -> void:
	if str(meta) == "congress:terms":
		_toggle_congress_terms()


func _add_congress_row(congress) -> void:
	if not (congress is Dictionary) or congress.is_empty():
		return
	var phase = congress.get("phase")
	var phase_s: String = phase if phase is String else ""
	var sitting: bool = congress.get("sitting") is bool and congress.get("sitting")
	var available: bool = congress.get("available") is bool and congress.get("available")
	var gate_terms = congress.get("gate_terms")
	if not (gate_terms is Array):
		gate_terms = []
	var shows_terms: bool = not sitting and phase_s != "concluded" and gate_terms.size() > 0

	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	# The nation list's own size (its buttons are 13) — the row sits above
	# them and must not shout over them.
	lbl.theme_type_variation = &"CaptionRich"
	var bbcode := "[color=#" + Utils.COLOR_GOLD + "][b]The Congress of Paris[/b][/color]"
	# Where it stands, in one clause: the clock line where it says something
	# the terms do not (the sitting's turn, the cooldown); at the gate, how
	# many of its terms are met.
	var line = congress.get("state_line")
	if phase_s != "gate" and line is String and line != "":
		var severity = congress.get("severity")
		bbcode += " [color=#" + _congress_tint(severity if severity is String else "") + "]— " + line.replace("[", "[lb]") + "[/color]"
	elif shows_terms:
		var met_n := 0
		for term in gate_terms:
			if term is Dictionary and term.get("met") is bool and term.get("met"):
				met_n += 1
		var met_color: String = Utils.COLOR_SUCCESS if met_n == gate_terms.size() else Utils.COLOR_INFO
		bbcode += " [color=#" + met_color + "]— " + str(met_n) + " of " + str(gate_terms.size()) + " terms met[/color]"
	if shows_terms:
		bbcode += "  [url=congress:terms]" + ("▾ hide the terms" if _congress_terms_open else "▸ the terms") + "[/url]"
		# Before a summons the terms the summons is refused on, ✓ met / • not;
		# while it sits the table holds the story ("View the table").
		if _congress_terms_open:
			for term in gate_terms:
				if not (term is Dictionary):
					continue
				var met: bool = term.get("met") is bool and term.get("met")
				var mark: String = "✓" if met else "•"
				var term_color: String = Utils.COLOR_SUCCESS if met else Utils.COLOR_INFO
				var text = term.get("text")
				bbcode += "\n    [color=#" + term_color + "]" + mark + " " + (str(text) if text != null else "") + "[/color]"
	lbl.text = bbcode
	lbl.meta_clicked.connect(_on_congress_meta)
	content_list.add_child(lbl)

	# The summons and the table, on one row. The summons is always present;
	# disabled with the backend's own reason (its tooltip, and beneath it
	# while the terms are open) when any term is unmet — the
	# _add_action_button idiom. Live, it is the primary action (UXR3-F5): gold
	# on the bar's alert chip.
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	var btn = Button.new()
	var cost = congress.get("cost_text")
	btn.text = "Summon the Congress of Paris"
	if cost is String and cost != "":
		btn.text += " (" + cost + ")"
	btn.custom_minimum_size = Vector2(0, 36)
	btn.theme_type_variation = &"CaptionButton"
	btn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn.disabled = not available
	if available:
		btn.add_theme_color_override("font_color", Color("#" + Utils.COLOR_GOLD))
		var primary := StyleBoxFlat.new()
		primary.bg_color = Color(0.23, 0.18, 0.08, 0.95)
		primary.border_color = Utils.UI_GOLD
		primary.set_border_width_all(2)
		primary.set_corner_radius_all(4)
		primary.content_margin_left = 10.0
		primary.content_margin_right = 10.0
		primary.content_margin_top = 4.0
		primary.content_margin_bottom = 4.0
		btn.add_theme_stylebox_override("normal", primary)
		btn.pressed.connect(_on_congress_summon_pressed)
	row.add_child(btn)
	# The table — every great power's answer, reason and price, on the
	# Diplomatic Ledger's CONGRESS tab.
	var view = Button.new()
	if sitting:
		view.text = "View the table — the courts' answers, the hold, the days"
	else:
		view.text = "View the table"
	view.custom_minimum_size = Vector2(0, 36)
	view.theme_type_variation = &"CaptionButton"
	view.add_theme_color_override("font_color", Color("#" + Utils.COLOR_GOLD))
	view.pressed.connect(_on_congress_table_pressed)
	row.add_child(view)
	content_list.add_child(row)
	var reason = congress.get("unavailable_reason")
	if not available and reason is String and reason != "":
		btn.tooltip_text = reason
		if _congress_terms_open or not shows_terms:
			var reason_label = Label.new()
			reason_label.text = "    " + reason
			reason_label.theme_type_variation = &"Caption"
			reason_label.add_theme_color_override("font_color", Utils.UI_REASON_GREY)
			reason_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			content_list.add_child(reason_label)


func _on_congress_summon_pressed():
	_close_wizard()
	command_selected.emit(CONGRESS_SUMMON_COMMAND)


func _on_congress_table_pressed():
	_close_wizard()
	open_congress_requested.emit()


# =============================================================================
# STEP 4: THE EMPEROR'S DESIGNS (VP-1, docs/VP1_DESIGNS_SPEC.md §6 — the road page)
# =============================================================================

func _add_designs_row(designs) -> void:
	if not (designs is Dictionary) or designs.is_empty():
		return
	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	lbl.theme_type_variation = &"CaptionRich"
	var line = designs.get("line")
	var bbcode := "[color=#" + Utils.COLOR_GOLD + "][b]The Emperor's Designs[/b][/color]"
	if line is String and line != "":
		bbcode += " [color=#" + Utils.COLOR_INFO + "]— " + line.replace("[", "[lb]") + "[/color]"
	lbl.text = bbcode
	content_list.add_child(lbl)
	var btn = Button.new()
	btn.text = "The Emperor's Designs — the roads of the Empire"
	btn.custom_minimum_size = Vector2(0, 36)
	btn.theme_type_variation = &"CaptionButton"
	btn.add_theme_color_override("font_color", Color("#" + Utils.COLOR_GOLD))
	btn.pressed.connect(_on_designs_pressed)
	content_list.add_child(btn)


func _on_designs_pressed():
	_current_step = 4
	_selected_nation = ""
	back_button.visible = true
	title_label.text = "THE CABINET — THE EMPEROR'S DESIGNS"
	assessment_panel.text = _designs_prompt()
	_lay_out_prompt(4)
	_clear_content_list()
	_add_loading_label()
	_fetch_designs()


func _bb(text) -> String:
	"""A backend string, safe inside BBCode."""
	return (str(text) if text != null else "").replace("[", "[lb]")


func _designs_prompt(proclaimed_title: String = "") -> String:
	"""The road page's prompt. S14D-X31 (October 23, 2026): once a road is
	proclaimed the prompt says so — the standing "One proclamation decides it"
	read wrong over a page whose decision was made."""
	if proclaimed_title != "":
		return ("[color=#" + Utils.COLOR_INFO + "]\"The Empire's road is proclaimed, Sire — "
			+ _bb(proclaimed_title) + ". It cannot be undone, and the other roads are forsworn.\"[/color]")
	return "[color=#" + Utils.COLOR_INFO + "]\"Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone.\"[/color]"


func _render_designs(data: Dictionary):
	"""The road page: every road with its gate, its teeth and its two
	designs (what each asks, the Cabinet row that does it, its reward), the
	courts each names as links, and the Proclaim button — disabled with the
	executor's own refusal (the payload's `disabled_reason`). The button
	sends the payload's own command; the backend quotes the price and that
	it cannot be undone before anything is spent."""
	_clear_content_list()
	scroll_container.scroll_vertical = 0
	var roads = data.get("roads")
	if not (data.get("armed") is bool and data.get("armed")) or not (roads is Array) or roads.size() == 0:
		var empty_lbl = RichTextLabel.new()
		empty_lbl.bbcode_enabled = true
		empty_lbl.fit_content = true
		empty_lbl.scroll_active = false
		empty_lbl.text = ("[color=#" + Utils.COLOR_INFO
			+ "]No designs of the Empire are authored in this campaign.[/color]")
		content_list.add_child(empty_lbl)
		return
	# S14D-X31: the prompt reads the proclaimed road, where there is one.
	var proclaimed_title := ""
	for road in roads:
		if road is Dictionary and road.get("proclaimed") is bool and road.get("proclaimed"):
			proclaimed_title = str(road.get("title", ""))
			break
	assessment_panel.text = _designs_prompt(proclaimed_title)
	# S14d: the road page's line at the head, above the headline (the Proclaim
	# strip stays above the fold at scale 2.0 — the frame pins it).
	_add_first_open_line(data)
	var head = RichTextLabel.new()
	head.bbcode_enabled = true
	head.fit_content = true
	head.scroll_active = false
	head.text = "[color=#" + Utils.COLOR_GOLD + "]" + _bb(data.get("headline")) + "[/color]"
	content_list.add_child(head)
	# The decision first: every road's Proclaim button in one strip under the
	# headline, above the fold at both scales (the details scroll beneath).
	var strip := HFlowContainer.new()
	strip.add_theme_constant_override("h_separation", 8)
	strip.add_theme_constant_override("v_separation", 6)
	for road in roads:
		if road is Dictionary:
			var btn = _proclaim_button(road)
			if btn != null:
				strip.add_child(btn)
	if strip.get_child_count() > 0:
		content_list.add_child(strip)
	else:
		strip.queue_free()
	# The proclaimed road leads; a forsworn road keeps its name and its line.
	for road in roads:
		if road is Dictionary and road.get("proclaimed") is bool and road.get("proclaimed"):
			_add_road_block(road)
	for road in roads:
		if road is Dictionary and not (road.get("proclaimed") is bool and road.get("proclaimed")):
			_add_road_block(road)
	# S14b part 3: the Acts of the Empire — the road's gold sink, decreed once.
	var acts = data.get("acts")
	if acts is Array and not (acts as Array).is_empty():
		_add_acts_block(acts)
	call_deferred("_update_more_below")


func _add_acts_block(acts: Array) -> void:
	"""THE ACTS OF THE EMPIRE (VP-1, the record §5): each Act's date, what it
	is, its price and its effects (the payload's — the decree applies the
	same), and its Decree button: the payload's own command when available,
	disabled with the executor's own refusal otherwise (`act_refusal`)."""
	var head = RichTextLabel.new()
	head.bbcode_enabled = true
	head.fit_content = true
	head.scroll_active = false
	# S14D-X44: the escape, as the rest of the file writes it (never a raw
	# newline inside a literal — it parsed by the LF attribute alone).
	head.text = ("\n[color=#" + Utils.COLOR_GOLD + "][b]THE ACTS OF THE EMPIRE[/b][/color] "
		+ "[color=#" + Utils.COLOR_INFO + "]— gold for the road, each decreed once[/color]")
	content_list.add_child(head)
	for row in acts:
		if not (row is Dictionary):
			continue
		var decreed := int(row.get("decreed_turn", -1))
		var forsworn: bool = row.get("forsworn") is bool and row.get("forsworn")
		var lbl = RichTextLabel.new()
		lbl.bbcode_enabled = true
		lbl.fit_content = true
		lbl.scroll_active = false
		lbl.theme_type_variation = &"CaptionRich"
		var name_color: String = Utils.COLOR_INFO if forsworn else Utils.COLOR_GOLD
		var bbcode := "[color=#" + name_color + "][b]" + _bb(row.get("title")) + "[/b][/color]"
		var date := str(row.get("date", ""))
		if date != "":
			bbcode += " [color=#" + Utils.COLOR_INFO + "](" + _bb(date) + ")[/color]"
		var numeral := str(row.get("road_numeral", ""))
		bbcode += " [color=#" + Utils.COLOR_INFO + "]· " + ("Road " + numeral if numeral != "" else "any road") + "[/color]"
		if not forsworn:
			var says := str(row.get("says", ""))
			if says != "":
				bbcode += "\n  " + _bb(says)
			bbcode += "\n  " + Utils.format_number(int(row.get("price", 0))) + " gold and " + str(int(row.get("admin_cost", 1))) + " administrative action, once"
			var effects := str(row.get("effects_line", ""))
			if effects != "":
				bbcode += " — " + _bb(effects)
			var relief := int(row.get("relief", 0))
			if relief > 0:
				bbcode += "; the Charges of Empire fall by " + Utils.format_number(relief) + "g a turn"
		if decreed >= 0:
			bbcode += "\n  [color=#" + Utils.COLOR_SUCCESS + "]✓ Decreed on turn " + str(decreed) + "[/color]"
		lbl.text = bbcode
		content_list.add_child(lbl)
		if decreed >= 0 or forsworn:
			continue
		var available: bool = row.get("available") is bool and row.get("available")
		var btn = Button.new()
		btn.text = "Decree " + str(row.get("title", ""))
		btn.custom_minimum_size = Vector2(0, 32)
		btn.theme_type_variation = &"CaptionButton"
		btn.disabled = not available
		if available:
			btn.add_theme_color_override("font_color", Color("#" + Utils.COLOR_GOLD))
			btn.pressed.connect(_on_proclaim_pressed.bind(str(row.get("command", ""))))
			btn.tooltip_text = "Decreed once — the gold is not refunded."
		else:
			var reason = row.get("disabled_reason")
			if reason is String and reason != "":
				btn.tooltip_text = reason
				var why = RichTextLabel.new()
				why.bbcode_enabled = true
				why.fit_content = true
				why.scroll_active = false
				why.theme_type_variation = &"CaptionRich"
				why.text = "  [color=#" + Utils.COLOR_INFO + "]" + _bb(reason) + "[/color]"
				content_list.add_child(btn)
				content_list.add_child(why)
				continue
		content_list.add_child(btn)


func _add_road_block(road: Dictionary) -> void:
	var proclaimed: bool = road.get("proclaimed") is bool and road.get("proclaimed")
	var forsworn: bool = road.get("forsworn") is bool and road.get("forsworn")
	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	lbl.theme_type_variation = &"CaptionRich"
	var name_color: String = Utils.COLOR_INFO if forsworn else Utils.COLOR_GOLD
	var bbcode := "\n[color=#" + name_color + "][b]Road " + _bb(road.get("numeral")) + " — " + _bb(road.get("title")) + "[/b][/color]"
	bbcode += " [color=#" + Utils.COLOR_INFO + "](" + _bb(road.get("proclamation")) + ")[/color]"
	if proclaimed:
		bbcode += "\n    [color=#" + Utils.COLOR_SUCCESS + "]✓ Proclaimed — the Empire's road.[/color]"
	elif forsworn:
		bbcode += "\n    [color=#" + Utils.COLOR_INFO + "]" + _bb(road.get("forsworn_line")) + "[/color]"
	else:
		var gate_ok: bool = road.get("gate_met") is bool and road.get("gate_met")
		var gate_mark: String = "✓" if gate_ok else "•"
		var gate_color: String = Utils.COLOR_SUCCESS if gate_ok else Utils.COLOR_INFO
		bbcode += "\n    [color=#" + gate_color + "]" + gate_mark + " " + _bb(road.get("gate_reason")) + "[/color]"
		var teeth = road.get("teeth_line")
		var cost_text := "Proclaiming takes " + str(int(road.get("dp_cost", 0))) + " diplomatic points and " + str(int(road.get("admin_cost", 0))) + " administrative action"
		if teeth is String and teeth != "":
			cost_text += "; " + teeth
		bbcode += "\n    [color=#" + Utils.COLOR_INFO + "]" + _bb(cost_text) + ".[/color]"
	var designs = road.get("designs")
	if not (designs is Array) or forsworn:
		designs = []
	for d in designs:
		if not (d is Dictionary):
			continue
		var status: String = str(d.get("status", ""))
		var mark: String = "✓" if status == "fulfilled" or status == "met" else ("✗" if status == "lapsed" else "•")
		var d_color: String = Utils.COLOR_SUCCESS if status == "fulfilled" else (Utils.COLOR_ERROR if status == "lapsed" else Utils.COLOR_HEADER)
		bbcode += "\n    [color=#" + d_color + "]" + mark + " " + _bb(d.get("title")) + "[/color] [color=#" + Utils.COLOR_INFO + "](" + _bb(d.get("role_display")) + ") — " + _bb(d.get("progress"))
		var hold_line = d.get("hold_line")
		if hold_line is String and hold_line != "":
			bbcode += "; " + _bb(hold_line)
		bbcode += "[/color]"
		if not forsworn:
			var hint = d.get("hint")
			if hint is String and hint != "":
				bbcode += "\n        [color=#" + Utils.COLOR_INFO + "]" + _bb(hint) + "[/color]"
			var control = d.get("control")
			if control is String and control != "":
				bbcode += "\n        [color=#" + Utils.COLOR_INFO + "]In the Cabinet: " + _bb(control) + "[/color]"
			var reward = d.get("reward_line")
			if reward is String and reward != "":
				bbcode += "\n        [color=#" + Utils.COLOR_GOLD + "]" + _bb(reward) + "[/color]"
	lbl.text = bbcode
	content_list.add_child(lbl)

	# The courts each design names — their own Cabinet pages, where the
	# controls the hints name live (never a typed line).
	if not forsworn:
		var links := HFlowContainer.new()
		links.add_theme_constant_override("h_separation", 6)
		links.add_theme_constant_override("v_separation", 4)
		var seen := {}
		for d in designs:
			if not (d is Dictionary):
				continue
			var dl = d.get("links")
			if not (dl is Array):
				continue
			for link in dl:
				if not (link is Dictionary):
					continue
				var court := str(link.get("court", ""))
				if court == "" or seen.has(court):
					continue
				seen[court] = true
				var lb = Button.new()
				lb.text = "↳ " + str(link.get("label", court))
				lb.custom_minimum_size = Vector2(0, 30)
				lb.theme_type_variation = &"CaptionButton"
				lb.add_theme_color_override("font_color", Color("#" + Utils.COLOR_GOLD))
				lb.tooltip_text = "Open " + str(link.get("label", court)) + "'s page in the Cabinet"
				lb.pressed.connect(_on_nation_selected.bind(court))
				links.add_child(lb)
		if links.get_child_count() > 0:
			content_list.add_child(links)
		else:
			links.queue_free()

	if proclaimed or forsworn:
		return
	# The road's refusal, where its button in the strip above is dimmed.
	var available: bool = road.get("available") is bool and road.get("available")
	var reason = road.get("disabled_reason")
	if not available and reason is String and reason != "":
		var reason_label = Label.new()
		reason_label.text = "    " + reason
		reason_label.theme_type_variation = &"Caption"
		reason_label.add_theme_color_override("font_color", Utils.UI_REASON_GREY)
		reason_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		content_list.add_child(reason_label)


func _proclaim_button(road: Dictionary):
	"""A road's Proclaim button — the primary act when available (UXR3-F5
	gold), disabled with the executor's own refusal (its tooltip; the reason
	also stands under the road's details). None for a road proclaimed or
	forsworn."""
	var proclaimed: bool = road.get("proclaimed") is bool and road.get("proclaimed")
	var forsworn: bool = road.get("forsworn") is bool and road.get("forsworn")
	if proclaimed or forsworn:
		return null
	var available: bool = road.get("available") is bool and road.get("available")
	var btn = Button.new()
	btn.text = "Proclaim Road " + str(road.get("numeral", "")) + " — " + str(road.get("proclamation", ""))
	btn.custom_minimum_size = Vector2(0, 36)
	btn.theme_type_variation = &"CaptionButton"
	btn.disabled = not available
	if available:
		btn.add_theme_color_override("font_color", Color("#" + Utils.COLOR_GOLD))
		var primary := StyleBoxFlat.new()
		primary.bg_color = Color(0.23, 0.18, 0.08, 0.95)
		primary.border_color = Utils.UI_GOLD
		primary.set_border_width_all(2)
		primary.set_corner_radius_all(4)
		primary.content_margin_left = 10.0
		primary.content_margin_right = 10.0
		primary.content_margin_top = 4.0
		primary.content_margin_bottom = 4.0
		btn.add_theme_stylebox_override("normal", primary)
		btn.pressed.connect(_on_proclaim_pressed.bind(str(road.get("command", ""))))
		btn.tooltip_text = "It cannot be undone — the other roads are forsworn."
	else:
		var reason = road.get("disabled_reason")
		if reason is String and reason != "":
			btn.tooltip_text = reason
	return btn


func _on_proclaim_pressed(command: String):
	"""The payload's own command (`imperial_designs.proclaim_command`). The
	wizard closes first — the confirm (the clarification popup) stands below
	its layer — and the backend quotes the price before anything is spent."""
	if command == "":
		return
	_close_wizard()
	command_selected.emit(command)


# =============================================================================
# STEP 3: FORMABLE NATIONS (NA-6d §11.6-8 — the Formables button)
# =============================================================================

func _add_formables_button():
	var btn = Button.new()
	btn.text = "Formable Nations — states that could yet exist"
	btn.custom_minimum_size = Vector2(0, 36)
	btn.theme_type_variation = &"CaptionButton"
	btn.add_theme_color_override("font_color", Color("#" + Utils.COLOR_GOLD))
	btn.pressed.connect(_on_formables_pressed)
	content_list.add_child(btn)


func _on_formables_pressed():
	_current_step = 3
	_selected_nation = ""
	back_button.visible = true
	title_label.text = "THE CABINET — FORMABLE NATIONS"
	assessment_panel.text = "[color=#" + Utils.COLOR_INFO + "]\"The map of Europe is not finished, Sire. These states could yet exist — each names what its existence would require.\"[/color]"
	_lay_out_prompt(3)
	_clear_content_list()
	_add_loading_label()
	_fetch_formables()


func _render_formables(data: Dictionary):
	"""One row per formable — §11.6-8: never hidden, never dead. An
	unavailable row states exactly what is missing; an available row
	deep-links into the settlement flow for the qualifying war."""
	_clear_content_list()
	scroll_container.scroll_vertical = 0
	var rows = data.get("formables", [])
	# An empty catalogue is a legitimate world (the SOVEREIGN_MAP=legacy
	# rollback authors none), not an error. `_show_error` resets to step 1
	# and hides Back, which stranded the player on a step-3 screen still
	# titled FORMABLE NATIONS with no way back — so say it in place and
	# leave the Back button working.
	if not (rows is Array) or rows.size() == 0:
		var empty_lbl = RichTextLabel.new()
		empty_lbl.bbcode_enabled = true
		empty_lbl.fit_content = true
		empty_lbl.scroll_active = false
		empty_lbl.text = ("[color=#" + Utils.COLOR_INFO
			+ "]No formable nations are authored in this campaign.[/color]")
		content_list.add_child(empty_lbl)
		return
	# S14d part 1, second landing (the class sweep, TABLE_LESSON_SPEC §0 Q3): the
	# page's first-open line at the head of a non-empty catalogue — an empty one
	# says so above and never latches.
	_add_first_open_line(data)
	for row in rows:
		if row is Dictionary:
			_add_formable_row(row)


func _add_formable_row(row: Dictionary):
	var display_name = str(row.get("display_name", "?"))
	var flag = str(row.get("flag", ""))
	var cls = str(row.get("cls", ""))
	var available = row.get("available", false)
	var progress = str(row.get("progress", ""))

	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false

	var name_color = Utils.COLOR_GOLD if available else Utils.COLOR_HEADER
	var kind = "client state at the settlement table" if cls == "C" else "forms by conquest"
	var bbcode = Utils.bb_flag(flag, 16)
	bbcode += "[color=#" + name_color + "][b]" + display_name + "[/b][/color]"
	bbcode += " [color=#" + Utils.COLOR_INFO + "]— " + kind + "[/color]"
	if progress != "":
		bbcode += " [color=#" + Utils.COLOR_INFO + "](" + progress + ")[/color]"
	# `.get(k, default)` returns the default only for a MISSING key — a
	# present-but-null `gate_terms` would come back null and `for term in
	# null` is a runtime error. Match the file's own defensive idiom.
	var gate_terms = row.get("gate_terms")
	if not (gate_terms is Array):
		gate_terms = []
	for term in gate_terms:
		if not (term is Dictionary):
			continue
		var met = term.get("met", false)
		var mark = "✓" if met else "•"
		var term_color = Utils.COLOR_SUCCESS if met else Utils.COLOR_INFO
		bbcode += "\n    [color=#" + term_color + "]" + mark + " " + str(term.get("text", "")) + "[/color]"
	lbl.text = bbcode
	content_list.add_child(lbl)

	# The honest deep link: an available carve lands on the defeated
	# court's action list, where Open Settlement authors the clause.
	var deep_link = row.get("deep_link")
	if available and deep_link is Dictionary:
		var court = str(deep_link.get("nation", ""))
		if court != "":
			var btn = Button.new()
			btn.text = "    ↳ Open negotiations — " + Utils.display_nation_name(court)
			btn.custom_minimum_size = Vector2(0, 32)
			btn.theme_type_variation = &"CaptionButton"
			btn.add_theme_color_override("font_color", Color("#" + Utils.COLOR_GOLD))
			# The row's `deep_link.war_id` is deliberately NOT threaded on.
			# An AVAILABLE open_settlement always carries its own war_id
			# (diplomacy.py forces `available: false` for both the
			# multi-war-ambiguity and no-common-war cases), so a carried
			# value could never reach the POST — it would be state that
			# only risks leaking. The genuine gap it was meant to close,
			# a deep link landing on the ambiguity picker where the
			# player can choose the war the carve does NOT qualify in,
			# is routed as DESIGN_REFINEMENT NAD-4.
			btn.pressed.connect(_on_nation_selected.bind(court))
			content_list.add_child(btn)


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

	# S14d: the Cabinet's line is drawn on its FIRST view (step 1) only — at
	# Interface Scale 2.0 a line above this page's assessment pushed its
	# action chips below the fold (the EA-E5 frame). A court's page opened by
	# a door meets the line on the next Cabinet open; nothing is lost, since
	# the acknowledgement fires only on a draw.

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
	# PC-R7 (i) — ruling J (S13e part 4): at war, the war is named by its stake.
	var war_title = str(data.get("war_title", ""))
	if war_title != "":
		bbcode += " [color=#" + state_color + "]— the " + Utils.humanize_nation_keys_in_text(war_title) + "[/color]"
	bbcode += "   Relation: [color=#" + rel_color + "]" + rel_sign + str(relation) + " (" + relation_desc + ")[/color]\n"
	# S14E-10: why the court is cold - the grievance it holds, by its kind,
	# with the price of Make Amends (the relation line gave the figure only).
	var grievance_line = data.get("grievance_line", "")
	if grievance_line is String and grievance_line != "":
		bbcode += "[color=#" + Utils.COLOR_ORANGE + "]" + Utils.humanize_nation_keys_in_text(grievance_line.replace("[", "[lb]")) + "[/color]\n"

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

	# S14E-5: the court's LIVE holdings — a rump reads "Hanover holds 1
	# province (Osnabruck); the rest are Prussia's." ('' for every other court).
	var holdings_line = data.get("holdings_line", "")
	if holdings_line is String and holdings_line != "":
		bbcode += "[color=#" + Utils.COLOR_ORANGE + "]" + Utils.humanize_nation_keys_in_text(holdings_line.replace("[", "[lb]")) + "[/color]\n"

	if assessment_text:
		bbcode += "\n[color=#" + Utils.COLOR_INFO + "]\"" + assessment_text + "\"[/color]\n"
	if recommendation:
		bbcode += "[color=#" + Utils.COLOR_GOLD + "]Recommendation: " + recommendation + "[/color]\n"
	# VP-1 (S14b part 2): Talleyrand's reading of this court on the Emperor's
	# road — the road page (F1 → The Emperor's Designs) holds the rest.
	var designs_line = data.get("designs_line", "")
	if designs_line is String and designs_line != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + Utils.humanize_nation_keys_in_text(designs_line.replace("[", "[lb]")) + "[/color]\n"
	# PC-R8 / PC-F12 (S13e part 1): the counsel's ranked roads — each with
	# its dry-run number, whether it carries and its price — under the line.
	var roads = data.get("counsel_roads_display", [])
	if roads is Array and roads.size() > 0:
		bbcode += "[color=#" + Utils.toned_hex("a0a0a0") + "]"
		for road in roads:
			bbcode += "  " + Utils.humanize_nation_keys_in_text(str(road)) + "\n"
		bbcode += "[/color]"

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
	call_deferred("_fit_assessment")

	# Build action buttons
	var actions = data.get("actions", [])
	if actions.size() == 0:
		var lbl = RichTextLabel.new()
		lbl.bbcode_enabled = true
		lbl.fit_content = true
		lbl.scroll_active = false
		lbl.text = "[color=#" + Utils.COLOR_INFO + "]No diplomatic actions available.[/color]"
		content_list.add_child(lbl)
		return

	# UXR3-28 (Pre-Deploy S12 part 2): when the court has a live design (an
	# instrument chip names its aim), the three D5 instruments lead — they
	# are what that court's design asks of us, and they sat below the fold
	# under the routine missions.
	var live_design := false
	for action in actions:
		if action is Dictionary and INSTRUMENT_ACTIONS.has(str(action.get("action", ""))) \
				and str(action.get("aim", "")) != "":
			live_design = true
			break
	# DDB-7: the counsel's recommended action and a running mission's
	# Cancel (`counsel_first`, ordered by the backend) stay on top; the
	# instruments follow them when a design is live.
	var counsel: Array = []
	var others: Array = []
	for action in actions:
		if action is Dictionary and bool(action.get("counsel_first", false)):
			counsel.append(action)
		else:
			others.append(action)
	if live_design:
		var lead: Array = []
		var rest: Array = []
		for action in others:
			if action is Dictionary and INSTRUMENT_ACTIONS.has(str(action.get("action", ""))):
				lead.append(action)
			else:
				rest.append(action)
		others = lead + rest
	actions = counsel + others
	for action in actions:
		_add_action_button(action)
	call_deferred("_update_more_below")


const INSTRUMENT_ACTIONS := ["sponsor_design", "buy_off_design", "guarantee_nation"]


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

	var has_reason = (not available and disabled_reason and disabled_reason != ""
		and disabled_reason != "null")

	var btn = Button.new()
	btn.text = text
	# PC-R2 / PC-F44 (S13e part 2): a truce's row carries the one wording
	# (what it keeps, where it heads, the cure priced) in its tooltip.
	var truce_display = str(action.get("truce_display", ""))
	if truce_display != "" and truce_display != "null":
		btn.tooltip_text = Utils.wrap_text(truce_display, 100)  # PC-X11
	btn.custom_minimum_size = Vector2(0, 40)
	btn.theme_type_variation = &"CaptionButton"
	btn.disabled = not available
	# LV-15 (row EP F3): the chip WRAPS instead of running off the panel (the
	# list's horizontal scroll is disabled in _ready), and a gate reason is
	# its own smaller line under the chip rather than a bracket clipped off
	# its end — "Sponsor Their Design (200g/turn) (1 DP + 200g) — Aim their
	# court at France — gold flows, the compa…" was the measured frame.
	btn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if has_reason:
		btn.tooltip_text = disabled_reason

	# Color the button text based on likelihood
	if likelihood in _likelihood_colors:
		var color_hex = _likelihood_colors[likelihood]
		btn.add_theme_color_override("font_color", Color("#" + color_hex))

	if available:
		btn.pressed.connect(_on_action_selected.bind(action_id, action))

	content_list.add_child(btn)
	if has_reason:
		var reason_label = Label.new()
		reason_label.text = "    " + disabled_reason
		reason_label.theme_type_variation = &"Caption"
		reason_label.add_theme_color_override("font_color", Utils.UI_REASON_GREY)
		reason_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		content_list.add_child(reason_label)

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
		picker_label.text = "  [color=#" + Utils.toned_hex("a0a0a0") + "][i]Pick a war to settle:[/i][/color]"
		content_list.add_child(picker_label)
		for war_entry in available_wars:
			var war_str = str(war_entry)
			var war_btn = Button.new()
			war_btn.text = "    \u21B3 " + war_str
			war_btn.custom_minimum_size = Vector2(0, 30)
			war_btn.theme_type_variation = &"CaptionButton"
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
		grant_label.text = "  [color=#" + Utils.toned_hex("a0a0a0") + "][i]Pick a province to cede:[/i][/color]"
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
			region_btn.theme_type_variation = &"CaptionButton"
			var region_payload = action.duplicate(true)
			region_payload["region"] = region_name
			region_btn.pressed.connect(_on_action_selected.bind(action_id, region_payload))
			content_list.add_child(region_btn)

	# PC-X45 (the user's rule: diplomacy is never typed): a row that needs a
	# parameter carries `choices` — one indented button per choice, each
	# sending the row's action with the choice's own fields (the bid's sum).
	var choices = action.get("choices", [])
	if available and choices is Array and choices.size() > 0:
		for choice in choices:
			if not (choice is Dictionary):
				continue
			var choice_btn = Button.new()
			choice_btn.text = "    ↳ " + str(choice.get("label", ""))
			choice_btn.custom_minimum_size = Vector2(0, 30)
			choice_btn.theme_type_variation = &"CaptionButton"
			var choice_payload = action.duplicate(true)
			var extra = choice.get("payload", {})
			if extra is Dictionary:
				for key in extra.keys():
					choice_payload[key] = extra[key]
			# PC-X48 / X50: a choice may name its own action (a skip-ahead
			# rung, an autonomy jump); the row's action otherwise.
			var choice_action = str(choice.get("action", action_id))
			choice_btn.pressed.connect(_on_action_selected.bind(choice_action, choice_payload))
			content_list.add_child(choice_btn)


func _on_action_selected(action_id: String, action_payload: Dictionary = {}):
	"""Build command string and emit for main.gd to execute (§2 Step 3).
	Peace-class proposal previews render in the canonical proposal confirmation popup.

	When the action carries structured backend metadata (e.g. `war_id` for
	`open_settlement` so the war-detail-popup-equivalent path can scope the
	settlement to the correct war_instance), emit the structured signal so
	main.gd can call `send_structured_command` instead of free-text parsing.
	"""
	var command = _build_command(action_id, _selected_nation, action_payload)
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
		# PC-R8 K item 6: the table road the counsel named opens with the
		# coverage it priced ("Open Settlement with Austria alone").
		var coverage = action_payload.get("counsel_coverage", [])
		if coverage is Array and coverage.size() > 0:
			data["counsel_coverage"] = coverage
		return data
	if action_id == "propose_white_peace":
		var war_id = str(action_payload.get("war_id", ""))
		var data = {
			"action": "propose_white_peace",
			"target_nation": _selected_nation,
		}
		if war_id != "":
			data["war_id"] = war_id
		# PC-R8 K item 6: the white peace the counsel priced with the court
		# alone opens with that coverage.
		var wp_coverage = action_payload.get("counsel_coverage", [])
		if wp_coverage is Array and wp_coverage.size() > 0:
			data["counsel_coverage"] = wp_coverage
		return data
	if action_id == "outbid_bond":
		# PC-R7 (ii) part 3: "Outbid <payer>'s Bond" opens the table with the
		# court alone and France's bid staged (the row's choice carries it).
		var bid_data = {
			"action": "propose_common_peace",
			"target_nation": _selected_nation,
		}
		var bid_war = str(action_payload.get("war_id", ""))
		if bid_war != "":
			bid_data["war_id"] = bid_war
		var bid_coverage = action_payload.get("counsel_coverage", [])
		if bid_coverage is Array and bid_coverage.size() > 0:
			bid_data["counsel_coverage"] = bid_coverage
		var bid_gold = int(float(action_payload.get("bond_bid", 0)))
		if bid_gold > 0:
			bid_data["bond_bid"] = bid_gold
		return bid_data
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


# CN-4: a structured action whose echo, TYPED, does something else. The echo
# is display copy (SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1: the white
# peace is structured-only on this surface), so main.gd does not park it on
# the up-arrow and says where it came from. Measured: re-sending "propose
# white peace with Austria" from the history proposed a Peace Treaty with
# terms. Every other structured echo re-types to its own action (pinned by
# driving each one — tests/test_cn4_the_chip_honesty_census.py).
const ECHO_IS_DISPLAY_ONLY = {
	"propose_white_peace": "sent from the diplomacy screen — typed, this line would propose a peace treaty with terms",
	# PC-R7 (ii) part 3: the bid rides the structured road (the court alone,
	# France's gold staged); typed, the line opens the whole table, no bid.
	"outbid_bond": "sent from the diplomacy screen — typed, this line would open the whole table without the bid",
}


func echo_note(action: String) -> String:
	"""The disclosure for a structured action's display-only echo, or ""."""
	return str(ECHO_IS_DISPLAY_ONLY.get(action, ""))


func _build_command(action_id: String, nation: String, action_payload: Dictionary = {}) -> String:
	"""Map wizard action ID to the command string the backend expects."""
	match action_id:
		# AI-6c (Stage F, §4.6b): the three D5 instrument verbs — typed
		# command echoes (the UI-6 chip idiom); the backend chip payload
		# carries the aim and the default amount so the echo names the
		# whole bargain.
		"sponsor_design":
			var aim = str(action_payload.get("aim", ""))
			var amount = int(float(action_payload.get("amount", 200)))
			if aim == "":
				return "sponsor " + nation + ", " + str(amount) + " gold"
			return "sponsor " + nation + " against " + aim + ", " + str(amount) + " gold"
		"buy_off_design":
			return "buy off " + nation
		"guarantee_nation":
			return "guarantee " + nation
		# PC-R7 (ii) part 3 (Chaumont): the bond — the ally bound against the
		# enemy chosen on the row; the paymaster's bond outbid at the table.
		"bind_to_war":
			var enemy = str(action_payload.get("enemy", ""))
			if enemy == "":
				return "bind " + nation + " to the war"
			return "bind " + nation + " to the war against " + enemy
		"outbid_bond":
			return "propose common peace with " + nation
		# DD-1 S8 Step 3 (October 12, 2026) — the verbs. The ask-back's row
		# carries the province (one chip per home province the ally holds);
		# the bid's echo names the default sum the backend chip quotes.
		"ask_return_province":
			var ask_region = str(action_payload.get("region", ""))
			return "ask " + nation + " to return " + ask_region
		"bid_for_allegiance":
			# PC-X45: the sum chosen on the row (its `choices`); the chip's own 100 by default
			var amount = int(float(action_payload.get("amount", 100)))
			return "bid for " + nation + ", " + str(amount) + " gold"
		# PC-X43 / X44 (diplomacy is never typed): the reparations and the
		# bargain's repudiation, each from its Cabinet row.
		"make_amends":
			return "make amends with " + nation
		"make_amends_grievance":
			return "make amends with " + nation + " for the abandoned alliance"
		"repudiate_bargain":
			return "repudiate the bargain with " + nation
		# PC-X46 / X47 / X50 (diplomacy is never typed): the Congress's
		# sweetener (its sum from the row's choices), the beaten court's
		# subjugation, and an autonomy jump of two levels.
		"recognition_sweetener":
			var amount = int(float(action_payload.get("amount", 1000)))
			return "offer " + nation + " " + str(amount) + " gold for recognition"
		"subjugate":
			return "vassalize " + nation
		"set_autonomy":
			var level = str(action_payload.get("level", "satellite"))
			return "set " + nation + " to " + level
		# PC-X42 (S14 part 2): the war's purpose and its articles — the
		# card's two steps open from this row (diplomacy is never typed).
		"set_war_purpose":
			return "set war purpose against " + nation
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
			# VS-3: the structured payload carries the region. CN-4: so does
			# the echo — the typed form reads a province ("cede Rhineland to
			# Holland"), and "cede territory to <N>" dropped the one the
			# player picked, so the up-arrow re-sent a different order (the
			# eligible list). With no pick, the bare form asks for the list,
			# which is what the structured road does too. (The bare form
			# comes first on purpose: FA-N81's drift pin reads each arm's
			# first echo as its canonical one. Keep the word the arms use
			# to hand back a string out of comments here — the census pins
			# find the echoes by it.)
			var cede_region = str(action_payload.get("region", ""))
			if cede_region == "":
				return "cede territory to " + nation
			return "cede " + cede_region + " to " + nation
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

var _more_below: Label = null


func _update_more_below() -> void:
	"""DDB-7: the cue shows while rows remain below the pane's fold."""
	if _more_below == null:
		return
	var bar: VScrollBar = scroll_container.get_v_scroll_bar()
	_more_below.visible = bar != null and (bar.max_value - bar.page) > bar.value + 1.0


func _add_first_open_line(data: Dictionary) -> void:
	"""S14d: the payload's `first_open` {screen, line} — one INFO row at the HEAD
	of the view (never the assessment panel: LV-20 pins it to one line), then
	the acknowledgement. Drawn = visible: the row is the first thing added."""
	var fo = data.get("first_open")
	if not (fo is Dictionary):
		return
	var line := str(fo.get("line", ""))
	var screen := str(fo.get("screen", ""))
	if line == "" or screen == "":
		return
	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	lbl.text = "[color=#" + Utils.COLOR_INFO + "]" + _bb(line) + "[/color]"
	content_list.add_child(lbl)
	first_open_seen.emit(screen)


func _clear_content_list():
	if _more_below != null:
		_more_below.visible = false
	for child in content_list.get_children():
		child.queue_free()


func _add_loading_label():
	var lbl = Label.new()
	lbl.text = "Loading..."
	lbl.add_theme_color_override("font_color", Color("#" + Utils.COLOR_INFO))
	lbl.theme_type_variation = &"Caption"
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
	btn.theme_type_variation = &"CaptionButton"
	btn.pressed.connect(_on_open_envoys_pressed)
	content_list.add_child(btn)


func _on_open_envoys_pressed():
	_close_wizard()
	open_envoys_requested.emit()

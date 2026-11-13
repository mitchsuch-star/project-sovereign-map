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

# Session UI-2: red WORDS on the dark ground take the lifted alert red.
var _alert_hex: String = Utils.UI_ALERT_TEXT.to_html(false)

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

# S14G-22: the Cabinet's default height as a share of the viewport (x = 0: the
# width keeps its authored 560) - about 60 % of a 5120x1440 screen's height,
# where the authored 520 left five lines of the court list (864 px at 1440).
# Session UI-2 (November 12, 2026): 0.6 -> 0.7 - the blind readers found the
# court list "crammed in a small scroll while the window has empty space".
# Session UI-3 (November 12, 2026): 0.7 -> 0.8 - the readers again saw the acts
# scroll under a band of dark screen (a viewport under 650 px keeps the
# authored rect: 0.8 x 650 = 520; the compact view's 450 is unchanged).
const CABINET_CEILING_SHARE := Vector2(0.0, 0.8)


func _ready():
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(assessment_panel)
	Utils.keep_whole_lines(scroll_container)
	# Session UI-4 (November 12, 2026): the Recommendation stands on a gold card
	# (the readers: "lift the recommendation into a highlighted card").
	Utils.card_page(assessment_panel)
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
	# S14G-22 (Pre-Deploy S14h part 2, October 26, 2026): the Cabinet was a bare
	# 560x520 window with no grip - on a 5120x1440 screen five lines of the
	# court list and a scroll for every court (DD-B diplomacy #5). It is
	# CLAMPED AND GRIPPED now, like the layer-50 screens (the player's size is
	# remembered under "cabinet"), and its DEFAULT height is a share of the
	# viewport (`CABINET_CEILING_SHARE`, read by the centred-panel clamp in utils.gd;
	# the authored rect stays the floor, a grip's double-click returns to it).
	$PanelContainer.set_meta("clamp_ceiling_fraction", CABINET_CEILING_SHARE)
	ResizeGrip.attach_centered($PanelContainer, "cabinet")
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

	# Session UI-3: the act notes fold into hovers; the switch re-draws the
	# current step from its cached payload (no re-fetch, scroll kept).
	Utils.on_explanations_changed(_on_explanations_changed)
	assessment_panel.meta_clicked.connect(_on_assessment_meta)

	# Create dedicated HTTPRequest (§9b)
	_http = HTTPRequest.new()
	add_child(_http)
	_http.request_completed.connect(_on_http_completed)
	_http.timeout = 30.0


var _last_preview_data: Dictionary = {}
# Session UI-3: the assessment's counsel note (one id for every court — a
# player who opens Talleyrand's counsel once reads it whole on every court).
const COUNSEL_NOTE := "cabinet.counsel"


func _on_assessment_meta(meta) -> void:
	"""The assessment's links: its counsel note opens and closes in place."""
	if not Utils.is_note_meta(meta):
		return
	Utils.toggle_note(meta)
	_on_explanations_changed()


func _on_explanations_changed() -> void:
	if not visible or _request_in_flight:
		return
	if _current_step == 2 and not _last_preview_data.is_empty():
		var keep: int = scroll_container.scroll_vertical
		_render_preview(_last_preview_data)
		Utils.restore_scroll(scroll_container, keep)


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
		# Session UI-2: the acts take the window's height - the assessment keeps
		# its counsel in view (_fit_assessment) and a smaller share of the slack
		# than the list ("use the full height": the blind reader of step 2).
		assessment_panel.size_flags_stretch_ratio = 0.3


# EA-E5 (SF-RR5, October 21, 2026): step 2's assessment keeps Talleyrand's
# counsel in view. Its share of the panel (half the chip list's) was 75 px at
# Interface Scale 2.0 — the heading and the status line, the counsel below its
# own fold. Its floor is its first ASSESSMENT_FLOOR_LINES lines (the heading,
# the status, the space, the counsel's opening two), never more than the text
# it holds; the chip list scrolls under its "more below".
const ASSESSMENT_FLOOR_LINES := 5
const ASSESSMENT_CAP_SHARE := 0.5   # Session UI-4: 0.4 -> 0.5 — the factors table stood cut by the acts   # Session UI-3: the whole counsel, at most 40 % of the panel
# In the compact view (Interface Scale 2.0, a 360-px panel) 40 % left the acts
# fewer than two whole rows (EA-E5's driven pin): the heading, the status and the
# counsel's opening still stand in 30 %.
const ASSESSMENT_CAP_SHARE_COMPACT := 0.3


func _fit_assessment() -> void:
	await get_tree().process_frame
	if assessment_panel == null or not visible or _current_step != 2:
		return
	# Session UI-3 (November 12, 2026): the floor cut Talleyrand's quote to ONE
	# line - on a 560-wide panel the status line wraps (its relation figure
	# drops to a second line), so the first five lines ended inside the
	# quote's first line. The counsel now stands WHOLE up to
	# ASSESSMENT_CAP_SHARE of the panel's height; the acts take the rest.
	var upto: float = float(assessment_panel.get_content_height())
	var box: StyleBox = assessment_panel.get_theme_stylebox("normal")
	var top: float = box.get_margin(SIDE_TOP) if box else 0.0
	var panel_h: float = $PanelContainer.offset_bottom - $PanelContainer.offset_top
	var share: float = ASSESSMENT_CAP_SHARE_COMPACT if Utils.compact_view() else ASSESSMENT_CAP_SHARE
	var cap: float = maxf(56.0, panel_h * share)
	assessment_panel.custom_minimum_size.y = clampf(ceilf(upto + top + 6.0), 56.0, cap)
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
	lbl.text = "[color=#" + _alert_hex + "]" + msg + "[/color]"
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
		# S14E-X91 / S14E-X92: the notice names the dialogue and the turn.
		# S14G-6: and whose letter shuts it (`cabinet_locked_by`), when a letter does.
		_add_dialogue_gate_notice(pending_envoy_count, int(data.get("cabinet_locked_until", 0)), str(data.get("dialogue_pending_name", "")), data.get("cabinet_locked_by", []), bool(data.get("cabinet_locked", pending_envoy_count > 0)))
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

	# S14G-22: "Your courts" - the courts with business waiting (a mission
	# running, a letter unanswered) in ONE place above the groups, so a court
	# that moves between At War / Treaties / Neutral as treaties change is
	# still one click away. Omitted when no court has any.
	_add_your_courts(data.get("your_courts", []))

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


func _add_your_courts(rows) -> void:
	"""S14G-22: the "Your courts" rows above the groups. `rows` is the
	backend's `your_courts` (null-safe: absent, null or empty draws nothing),
	each the same entry the groups carry plus `why` - the business waiting
	("letter awaiting your answer"; a running mission already rides the
	button's [MISSION] tag). The court keeps its place in its own group below:
	the groups stay complete, this is the shortcut."""
	if not (rows is Array) or rows.is_empty():
		return
	_add_category_header("Your courts (" + str(rows.size()) + ")", Utils.COLOR_GOLD)
	for row in rows:
		if not (row is Dictionary):
			continue
		var entry: Dictionary = row.duplicate()
		var why := str(entry.get("why", ""))
		if why != "":
			entry["state_display"] = str(entry.get("state_display", "?")) + " · " + why
		_add_nation_button(entry)


func _add_category_header(text: String, color: String):
	# Session UI-2: a group's heading is in the title face (its colour kept, the
	# red lifted to the alert red that reads on the dark ground).
	var hex: String = color
	if hex == Utils.COLOR_ERROR:
		hex = _alert_hex
	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	lbl.text = "[font=" + Utils.TITLE_FONT + "][color=#" + hex + "]" + text + "[/color][/font]"
	content_list.add_child(lbl)


# Session UI-2: a court's state, as a badge tone (WAR red, ALLIANCE green, the
# open treaties blue, a VASSAL gold, anything else quiet).
func _state_tone(nation_data: Dictionary) -> String:
	var state := str(nation_data.get("state", ""))
	var shown := str(nation_data.get("state_display", "")).to_lower()
	if state == "WAR" or shown.begins_with("at war"):
		return "8b2a2a"
	if state == "ALLIANCE" or state == "DEFENSIVE_ALLIANCE" or shown.find("alliance") >= 0:
		return "2f6b3a"
	if shown.begins_with("vassal") or state == "VASSAL":
		return "8a6d2a"
	if state == "OPEN_BORDERS" or state == "NON_AGGRESSION" or state == "PEACE" or shown.find("peace") >= 0 			or shown.find("non-aggression") >= 0 or shown.find("borders") >= 0 or shown.find("treaty") >= 0:
		return "3a4a6b"
	return Utils.COLOR_BADGE_QUIET


func _add_nation_button(nation_data: Dictionary):
	"""Session UI-2: a court is a ROW - the court's button (flag, name) on the
	left, and on the right its state as a badge and its relation as a meter
	with its figure. The row's words are the old button's: the name, the state
	(and the business waiting that rides it, on a line of its own under the
	row), the relation figure and its descriptor, [MISSION]."""
	var nation_name = str(nation_data.get("name", "?"))
	var state_display = str(nation_data.get("state_display", "?"))
	# S14G-22: "Your courts" rides the business waiting on the state, after " · ".
	var why := ""
	var cut: int = state_display.find(" · ")
	if cut >= 0:
		why = state_display.substr(cut + 3)
		state_display = state_display.substr(0, cut)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	var btn = Button.new()
	btn.text = Utils.display_nation_name(nation_name)
	btn.custom_minimum_size = Vector2(0, 44)
	btn.theme_type_variation = &"CaptionButton"
	btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn.clip_text = true
	# UI-6: period heraldry as the leading icon (untinted — colored art)
	Utils.apply_flag_icon(btn, nation_name)
	btn.pressed.connect(_on_nation_selected.bind(nation_name))
	row.add_child(btn)

	var figures := RichTextLabel.new()
	figures.bbcode_enabled = true
	figures.fit_content = true
	figures.scroll_active = false
	figures.autowrap_mode = TextServer.AUTOWRAP_OFF
	figures.mouse_filter = Control.MOUSE_FILTER_IGNORE
	figures.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	figures.theme_type_variation = &"CaptionRich"
	# Session UI-4: every row's figures take ONE column width, right-aligned, so
	# the state badges stand at the rows' right edge in a straight line (the
	# readers: "the At War badges float away from the rows"). A row whose
	# figures are wider (a MISSION badge beside the state) keeps its own width.
	figures.custom_minimum_size.x = float(Utils.text_px(230))
	var bbcode := "[right]" + Utils.bb_badge(state_display, _state_tone(nation_data))
	# W2: Active mission indicator
	if nation_data.get("has_active_mission", false):
		bbcode += " " + Utils.bb_badge("MISSION", "8a6d2a")
	# W1: Relation score and descriptor
	var relation = nation_data.get("relation")
	if relation != null:
		var rel: int = int(relation)
		var rel_sign = "+" if rel > 0 else ""
		var rel_desc = str(nation_data.get("relation_descriptor", ""))
		bbcode += "
" + Utils.bb_relation_meter(rel, 80, 7) + " " + rel_sign + str(rel)
		if rel_desc:
			bbcode += " (" + rel_desc + ")"
	bbcode += "[/right]"
	figures.text = bbcode
	row.add_child(figures)
	content_list.add_child(row)
	if why != "":
		var why_label := Label.new()
		why_label.text = "    " + why
		why_label.theme_type_variation = &"Caption"
		why_label.add_theme_color_override("font_color", Utils.UI_GOLD)
		why_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		content_list.add_child(why_label)


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
	else:
		# Session UI-2: the blind readers took the shut Summon for a live
		# button - it keeps the theme's dashed disabled face and is dimmed
		# further, and says why under it (the reason line, below).
		btn.modulate = Color(1, 1, 1, 0.6)
		btn.focus_mode = Control.FOCUS_NONE
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
			# AU-3b: the Act's second purse — the titles, paid in authority
			var titles_row = row.get("titles")
			if titles_row is Dictionary and not titles_row.is_empty():
				bbcode += "\n  or " + _bb(titles_row.get("name", "")) + ": " + str(int(titles_row.get("authority", 0))) + " authority and " + str(int(row.get("admin_cost", 1))) + " administrative action, once — the chest untouched"
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
				_add_titles_button(row)
				continue
		content_list.add_child(btn)
		_add_titles_button(row)


func _add_titles_button(row: Dictionary) -> void:
	"""AU-3b (AUTHORITY_CURRENCY_SPEC.md §5.3): the Act's second purse — "Grant
	the titles (N authority)" under the gold Decree, the payload's own command
	when open, disabled with the executor's own refusal otherwise
	(`act_refusal(..., currency="authority")`); nothing when the Act has none."""
	var titles = row.get("titles")
	if not (titles is Dictionary) or titles.is_empty():
		return
	var open: bool = titles.get("available") is bool and titles.get("available")
	var tbtn = Button.new()
	tbtn.text = "Grant the titles (" + str(int(titles.get("authority", 0))) + " authority)"
	tbtn.custom_minimum_size = Vector2(0, 32)
	tbtn.theme_type_variation = &"CaptionButton"
	tbtn.disabled = not open
	content_list.add_child(tbtn)
	if open:
		tbtn.add_theme_color_override("font_color", Color("#" + Utils.COLOR_GOLD))
		tbtn.pressed.connect(_on_proclaim_pressed.bind(str(titles.get("command", ""))))
		tbtn.tooltip_text = str(titles.get("line", ""))
		return
	var why_not := str(titles.get("disabled_reason", ""))
	if why_not != "":
		tbtn.tooltip_text = why_not
		var note = RichTextLabel.new()
		note.bbcode_enabled = true
		note.fit_content = true
		note.scroll_active = false
		note.theme_type_variation = &"CaptionRich"
		note.text = "  [color=#" + Utils.COLOR_INFO + "]" + _bb(why_not) + "[/color]"
		content_list.add_child(note)


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
	# DY-6 (DYNAMISM_SPEC.md §6): a crown names its throne — a marshal with
	# laurels or a prince of the Imperial house may be seated on it.
	var crown = str(row.get("crown", ""))
	if crown != "" and crown != "null":
		kind = "a crown (" + crown + ") at the settlement table"
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
		# S14E-X91 / S14E-X92: the notice names the dialogue and the turn.
		# S14G-6: and whose letter shuts it (`cabinet_locked_by`), when a letter does.
		_add_dialogue_gate_notice(pending_envoy_count, int(data.get("cabinet_locked_until", 0)), str(data.get("dialogue_pending_name", "")), data.get("cabinet_locked_by", []), bool(data.get("cabinet_locked", pending_envoy_count > 0)))
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
		rel_color = _alert_hex
	elif relation >= 30:
		rel_color = Utils.COLOR_SUCCESS

	var state_color = Utils.COLOR_INFO
	match str(data.get("current_state", "")):
		"WAR":
			state_color = _alert_hex
		"ALLIANCE", "DEFENSIVE_ALLIANCE":
			state_color = Utils.COLOR_SUCCESS
		"OPEN_BORDERS", "NON_AGGRESSION":
			state_color = Utils.COLOR_BLUE

	var bbcode = ""
	bbcode += Utils.bb_flag(_selected_nation, 20)
	# Session UI-2: the heading in the title face; the court's STATE a badge and
	# its RELATION a meter with its figure - the figures lead, the prose follows.
	bbcode += Utils.HEAD_OPEN + "TALLEYRAND'S ASSESSMENT — " + Utils.display_nation_name(_selected_nation).to_upper() + Utils.HEAD_CLOSE + "\n"
	var state_tone := "3a4a6b"
	match str(data.get("current_state", "")):
		"WAR":
			state_tone = "8b2a2a"
		"ALLIANCE", "DEFENSIVE_ALLIANCE":
			state_tone = "2f6b3a"
		"":
			state_tone = Utils.COLOR_BADGE_QUIET
	bbcode += "Status: " + Utils.bb_badge(state_display, state_tone)
	# PC-R7 (i) — ruling J (S13e part 4): at war, the war is named by its stake.
	var war_title = str(data.get("war_title", ""))
	if war_title != "":
		bbcode += " [color=#" + state_color + "]— the " + Utils.humanize_nation_keys_in_text(war_title) + "[/color]"
	bbcode += "   Relation: " + Utils.bb_relation_meter(relation, 90, 7) + " [color=#" + rel_color + "]" + rel_sign + str(relation) + " (" + relation_desc + ")[/color]\n"
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
			loyalty_color = _alert_hex
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
		# Session UI-4: the compact view gives the counsel the blank line's room —
		# at 115 % its opening line stood cut under the assessment's 30 % (EA-E5)
		bbcode += ("" if Utils.compact_view() else "\n") + "[color=#" + Utils.COLOR_INFO + "]\"" + assessment_text + "\"[/color]\n"
	# VP-1 (S14b part 2): Talleyrand's reading of this court on the Emperor's
	# road — the road page (F1 → The Emperor's Designs) holds the rest.
	var designs_part := ""
	var designs_line = data.get("designs_line", "")
	if designs_line is String and designs_line != "":
		designs_part = "[color=#" + Utils.COLOR_INFO + "]" + Utils.humanize_nation_keys_in_text(designs_line.replace("[", "[lb]")) + "[/color]\n"
	# PC-R8 / PC-F12 (S13e part 1): the counsel's ranked roads — each with
	# its dry-run number, whether it carries and its price — under the line.
	var roads_part := ""
	var roads = data.get("counsel_roads_display", [])
	if roads is Array and roads.size() > 0:
		roads_part = "[color=#" + Utils.toned_hex("a0a0a0") + "]"
		for road in roads:
			roads_part += "  " + Utils.humanize_nation_keys_in_text(str(road)) + "\n"
		roads_part += "[/color]"
	# Session UI-3 (the interim reading, F15): the counsel opens from the
	# Recommendation's first sentence (`cabinet.counsel`, one note for every
	# court) — the rest of it, the road reading and the ranked roads stand in
	# place on "▸ more"; the acts beside each road keep their price badges.
	# On the page (or opened) every line prints as it did, in the same order.
	var rec_cut: int = Utils.first_sentence_end(str(recommendation)) if recommendation else -1
	var counsel_held: bool = rec_cut >= 0 or designs_part != "" or roads_part != ""
	# Session UI-4: the counsel (the Recommendation, folded or whole, with the
	# road reading under it) is ONE gold card; the card closes on the counsel's
	# last line, never on the blank paragraph after it.
	var counsel_carded: bool = counsel_held or recommendation != ""
	if counsel_carded:
		bbcode += Utils.card_open(Utils.COLOR_GOLD)
	if Utils.show_note(COUNSEL_NOTE) or not counsel_held:
		if recommendation:
			bbcode += "[color=#" + Utils.COLOR_GOLD + "]Recommendation: " + recommendation + "[/color]\n"
		bbcode += designs_part + roads_part
		if Utils.explanations_folded() and counsel_held:
			bbcode += Utils.note_link(COUNSEL_NOTE) + "\n"
	elif recommendation:
		var opening: String = str(recommendation).substr(0, rec_cut) if rec_cut >= 0 else str(recommendation)
		bbcode += "[color=#" + Utils.COLOR_GOLD + "]Recommendation: " + opening + "[/color] " + Utils.note_link(COUNSEL_NOTE) + "\n"
	else:
		bbcode += Utils.note_link(COUNSEL_NOTE) + "\n"
	if counsel_carded:
		if bbcode.ends_with("\n[/color]"):
			bbcode = bbcode.substr(0, bbcode.length() - 9) + "[/color]" + Utils.CARD_CLOSE + "\n"
		elif bbcode.ends_with("\n"):
			bbcode = bbcode.substr(0, bbcode.length() - 1) + Utils.CARD_CLOSE + "\n"
		else:
			bbcode += Utils.CARD_CLOSE

	# W3: Acceptance preview — key factors
	var acceptance_preview = data.get("acceptance_preview")
	if acceptance_preview != null and acceptance_preview is Dictionary:
		var positives = acceptance_preview.get("positive", [])
		var negatives = acceptance_preview.get("negative", [])
		if positives.size() > 0 or negatives.size() > 0:
			bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]KEY FACTORS[/color]\n"
			# Session UI-4: the factors are a small two-column table (factor |
			# value), each figure in the tone of what it does to the court's
			# willingness (the readers: "the assessment text is dense ... move
			# the key factors into a small bar or table").
			var factor_rows: Array = []
			for p in positives:
				factor_rows.append([str(p.get("label", "?")),
					"[color=#" + Utils.COLOR_SUCCESS + "]+" + str(int(p.get("value", 0))) + "[/color]"])
			for neg in negatives:
				factor_rows.append([str(neg.get("label", "?")),
					"[color=#" + _alert_hex + "]" + str(int(neg.get("value", 0))) + "[/color]"])
			bbcode += Utils.bb_table(["Factor", "Value"], factor_rows, [1], [4, 1]) + "\n"

	# W4: Cooldown pre-check warning
	var actions_list = data.get("actions", [])
	for act in actions_list:
		var disabled_reason = str(act.get("disabled_reason", ""))
		if "cooldown" in disabled_reason.to_lower() or "Cooldown" in disabled_reason:
			bbcode += "\n[color=#" + Utils.COLOR_ORANGE + "]\"We must exercise patience, Sire. " + disabled_reason + " before we may approach them again.\"[/color]\n"
			break

	assessment_panel.text = bbcode
	_last_preview_data = data
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


# Session UI-2: the verdict a likelihood word carries, as a badge tone - the
# favourable words green, the middling gold, the doubtful rust, "Hopeless" red.
func _verdict_tone(likelihood: String) -> String:
	if likelihood.begins_with("Almost Certain") or likelihood.begins_with("Favorable"):
		return "2f6b3a"
	if likelihood.begins_with("Uncertain"):
		return "8a6d2a"
	if likelihood.begins_with("Doubtful") or likelihood.begins_with("Unlikely"):
		return "8a4f2a"
	if likelihood.begins_with("Hopeless"):
		return "8b2a2a"
	return Utils.COLOR_BADGE_QUIET


func _add_action_button(action: Dictionary):
	"""Session UI-2: an act is a ROW - the act's own words on the left (the
	button), its price (DP, gold) and the likelihood's verdict as badges on the
	right. The act's effect text is a note on a line of its own under the row
	(it was the button's long tail); a likelihood's rider ("a counter is
	likely") rides the same note."""
	var display_name = str(action.get("display_name", "?"))
	var dp_cost = int(action.get("dp_cost", 0))
	var gold_cost = int(action.get("gold_cost", 0))
	var available = action.get("available", false)
	var disabled_reason = str(action.get("disabled_reason_display", action.get("error_display", action.get("disabled_reason", ""))))
	var likelihood = str(action.get("likelihood", ""))
	var action_id = str(action.get("action", ""))

	# The button's text: the act, as named.
	var text = display_name

	# W5: Mission effect text
	var note := ""
	var verdict := ""
	var effect_text = str(action.get("effect_text", ""))
	if effect_text and effect_text != "" and effect_text != "null":
		note = effect_text
	elif likelihood and likelihood != "" and likelihood != "null":
		# the verdict is the likelihood's head; what follows it is the note
		var cut_at: int = likelihood.find(" — ")
		if cut_at >= 0:
			verdict = likelihood.substr(0, cut_at)
			note = likelihood.substr(cut_at + 3)
		else:
			verdict = likelihood
	if verdict == "" and likelihood and likelihood != "" and likelihood != "null":
		var head_at: int = likelihood.find(" — ")
		verdict = likelihood.substr(0, head_at) if head_at >= 0 else likelihood

	var has_reason = (not available and disabled_reason and disabled_reason != ""
		and disabled_reason != "null")

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	var btn = Button.new()
	btn.text = text
	# PC-R2 / PC-F44 (S13e part 2): a truce's row carries the one wording
	# (what it keeps, where it heads, the cure priced) in its tooltip.
	var truce_display = str(action.get("truce_display", ""))
	if truce_display != "" and truce_display != "null":
		# PC-F47 (S15 head): PC-X11's hard wrap at 100 characters is retired —
		# the tooltip wraps itself to the window now (`Utils.wrap_tooltips`),
		# and a fixed width re-wrapped raggedly in a narrow one.
		btn.tooltip_text = truce_display
	btn.custom_minimum_size = Vector2(0, 40)
	btn.theme_type_variation = &"CaptionButton"
	btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
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

	if available:
		btn.pressed.connect(_on_action_selected.bind(action_id, action))
	row.add_child(btn)

	# The right-hand cell: the price, then the verdict - badges, not prose.
	var badges := ""
	# Session UI-4: the ONE recommendation the game makes - Talleyrand's counsel
	# - is tagged beside its act (no primary face; a running mission's Cancel
	# also leads the list but is no recommendation).
	if bool(action.get("counsel_first", false)) and not action_id.begins_with("cancel"):
		badges += Utils.bb_badge("Talleyrand's counsel", "8a6d2a") + " "
	if dp_cost > 0:
		badges += Utils.bb_glyph("dp", 16, Utils.COLOR_GOLD) + " " + str(dp_cost) + " DP  "
	if gold_cost > 0:
		badges += Utils.bb_glyph("gold", 16, Utils.COLOR_GOLD) + " " + str(gold_cost) + "g  "
	if verdict != "":
		badges += Utils.bb_badge(verdict, _verdict_tone(verdict))
	if badges != "":
		var cell := RichTextLabel.new()
		cell.bbcode_enabled = true
		cell.fit_content = true
		cell.scroll_active = false
		cell.autowrap_mode = TextServer.AUTOWRAP_OFF
		cell.mouse_filter = Control.MOUSE_FILTER_IGNORE
		cell.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		cell.theme_type_variation = &"CaptionRich"
		cell.text = "[right]" + badges.strip_edges() + "[/right]"
		if not available:
			# a shut act's figures are dimmed with it - it never reads as live
			cell.modulate = Color(1, 1, 1, 0.6)
		row.add_child(cell)
	content_list.add_child(row)
	# Session UI-3 (November 12, 2026): "Fold, a switch restores" - the act's
	# effect note is the act Button's hover (its DP / gold figures and the verdict
	# badge stay on the face); On the page the line prints under it as before.
	if note != "" and note != "null":
		Utils.explain_tip(btn, note, btn.tooltip_text)
	if note != "" and note != "null" and not Utils.explanations_folded():
		var note_label = Label.new()
		note_label.text = "    " + note
		note_label.theme_type_variation = &"Caption"
		note_label.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
		note_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		content_list.add_child(note_label)
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
		# S14E-D7: the counsel's lever ("Open Settlement with Britain alone",
		# the payment that carries her) opens the table with that sum staged,
		# the way the bid is - the offer row opens at it, not at its default.
		var offer_gold = int(float(action_payload.get("gold_offer", 0)))
		if offer_gold > 0:
			data["gold_offer"] = offer_gold
			# S14E-X125: the echo's disclosure key. `action` is the shared
			# "propose_common_peace" here, so the lookup in ECHO_IS_DISPLAY_ONLY
			# needs its own: typed, this echo opens the whole table, no sum.
			data["echo_key"] = "open_settlement_offer"
		elif bool(action_payload.get("echo_display_only", false)):
			# S14E-X128: a row that opens one court of several (the lever's
			# row when the chest cannot fund its sum, a coverage the counsel
			# stamped) is display copy too: typed, the echo opens the whole
			# table. The backend flags the row; the key is registered below.
			data["echo_key"] = "open_settlement_alone"
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
			# S14E-X125: the echo's disclosure key (`action` is the shared
			# "propose_common_peace", which ECHO_IS_DISPLAY_ONLY never lists).
			"echo_key": "outbid_bond",
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
	# S14E-X125: keyed by `echo_key` (the payload's own, main.gd reads it before
	# the action): the lever row opens the court alone with the sum staged.
	"open_settlement_offer": "sent from the diplomacy screen — typed, this line would open the whole table without the sum staged",
	# S14E-X128: the court alone out of a larger table (no sum to stage, or
	# none the chest can fund); typed, the line opens the whole table.
	"open_settlement_alone": "sent from the diplomacy screen — typed, this line would open the whole table, not the court alone",
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


func _add_dialogue_gate_notice(pending_envoy_count: int, locked_until: int = 0, dialogue_name: String = "", locked_by: Array = [], letter_locks: bool = true):
	"""`locked_until` is the backend's `cabinet_locked_until` (S14E-X92: the
	answer-by turn of a standing call to arms, 0 = the lock lifts when the turn
	ends); `dialogue_name` is `dialogue_pending_name` (S14E-X91: the display
	name of the hard-stop / local-planning dialogue that gates the wizard).
	S14G-6: `locked_by` is `cabinet_locked_by` (the courts whose letters shut
	the Cabinet) and `letter_locks` the backend's `cabinet_locked` - a LETTER is
	what gates the wizard only when it says so: a lesser court's routine letter
	(S14G-D3) is pending mail and no part of the lock, so a hard-stop dialogue
	with such a letter waiting names the dialogue, not the envoy."""
	var lbl = RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	if pending_envoy_count > 0 and letter_locks:
		# S14E-18 (S14f part 2): the rule, in the sentence "Not Now" and the
		# Cabinet button use — the notice named the envoy, never the lock.
		# S14G-6: and WHOSE letter it is, when the backend names the court.
		var by_letters = Utils.cabinet_shut_letters(locked_by)
		var whose = (" (" + by_letters + ")") if by_letters != "" else ""
		lbl.text = "[color=#" + COLOR_ORANGE + "]An unanswered envoy awaits your reply" + whose + " — " + Utils.cabinet_shut_line(locked_until) + " Reopen Envoys to answer it.[/color]"
	elif dialogue_name != "":
		# S14E-X91: name the matter. Number-neutral on purpose -- several
		# display names are plural noun phrases ("the terms you are drafting").
		lbl.text = "[color=#" + COLOR_ORANGE + "]Resolve the active dialogue first — you have " + dialogue_name + " awaiting your answer.[/color]"
	else:
		lbl.text = "[color=#" + COLOR_ORANGE + "]Resolve the active dialogue first.[/color]"
	content_list.add_child(lbl)
	if pending_envoy_count > 0 and letter_locks:
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

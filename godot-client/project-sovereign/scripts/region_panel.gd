extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Region Action Panel (UI-6)
# =============================================================================
# The map's provinces finally answer a click. Non-modal side panel
# (CanvasLayer 26 — beside the war HUD's 25, below every screen/modal) that
# renders the clicked province from the map node's OWN fog-filtered data
# (region_full_data / region_visibility / region_marshals / region_garrisons
# — no extra fetch, no fog leak) plus context action chips:
#   - own province:      [Recruit Infantry] [Build Depot]
#   - foreign controller: [Negotiate with X] → the F1 wizard at that court
#   - own marshals here:  [Fortify]/[Unfortify] [Drill] [Scout] per marshal,
#                         and CF-6's [Hold (2 AP)] [Fall back] [Garrison (2 AP)]
#                         (lit where `order_refusals` has no reason, dimmed
#                         with it otherwise; priced from `order_prices`)
# Chips send the SAME typed commands a player would type — the executor owns
# every gate (AP, gold, objections); a refused chip reports like a typed
# refusal in the terminal. Display-only, Golden Rule 6 clean.
#
# UX pass July 16: docked TOP-LEFT under the top bar (the old center-left
# anchor grew downward into the expandable terminal and covered the command
# box). The content area lives in a ScrollContainer whose height is fitted
# each render and CLAMPED above the terminal's live top edge (avoid_control,
# set by main.gd) — the panel and the command box can no longer fight for the
# same corner. Overflow scrolls.
# =============================================================================

signal region_command(command: String)
signal negotiate_requested(nation: String)
# NUI: THE SEA block's chip opens THE ADMIRALTY (main.gd → ledger book 7)
signal admiralty_requested
signal closed
# CC-2 "March here": the panel wants the backend's quotes for this province
# (main.gd fetches GET /march_quotes and hands them back to set_march_quotes).
signal quotes_requested(region: String)
# Session UI-6 (November 13, 2026): a marshal's name in FORCES PRESENT selects
# him on the map (main.gd answers; meta "select:<Name>").
signal marshal_select_requested(marshal_name: String)

const _MarshalState = preload("res://scripts/marshal_state.gd")

@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/HeaderRow/TitleLabel
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll = $PanelContainer/VBoxContainer/Scroll
@onready var content_area = $PanelContainer/VBoxContainer/Scroll/ContentArea

const _CHIP_BG = "233043"
# The whole client plays France (1805 campaign); dispatch/ledger make the
# same assumption.
const _PLAYER_NATION = "France"
# Panel geometry: matches the .tscn top-left dock (12, 48 — under the 36px
# top bar) plus a breathing margin above the terminal / screen bottom.
const _PANEL_TOP := 48.0
const _PANEL_LEFT := 12.0     # matches PanelContainer offset_left in region_panel.tscn
const _CLAMP_MARGIN := 10.0
# Never fit smaller than this — if the player drags the terminal to a
# near-full-height footprint the panel keeps a usable window and (drawing on
# layer 26) overlaps rather than collapsing to nothing.
const _MIN_CONTENT_H := 120.0
# S14G-15 (Pre-Deploy S14h part 2, October 26, 2026): under this many px of
# room above the terminal the panel DOCKS BESIDE it instead of squeezing to
# the 120 floor. A raised reply window (or a terminal dragged tall) left
# 120 px of body with the march list below the fold, overlapping the window.
const _DOCK_BESIDE_BELOW_H := 260.0
# The strip kept clear at the viewport's bottom when docked beside the
# terminal: the map controls' row (32 px chips + their frame) stands to the
# terminal's right at the same edge (main.gd `_fit_map_controls`).
const _DOCK_BOTTOM_RESERVE := 56.0
# UXR-2 (the layout law): the panel's WIDTH is a fraction of the logical
# viewport between the authored 344 (Scroll 320 + the leather's 24) and a
# ceiling — it was a bare fixed 344 at every size (9% of the user's panel).
const _WIDTH_FRACTION := 0.25   # Session UI-4: 0.2 -> 0.25 (the chips on one row, at 115 % type)
const _MIN_WIDTH := 440.0     # Session UI-4: 400 -> 440
const _MAX_WIDTH := 600.0     # Session UI-4: 560 -> 600

# The Control whose top edge the panel must stay above (main.gd wires the
# terminal's BottomLeftUI here). Null = clamp to the viewport bottom only.
# Review fix (July 16): a property setter, because the terminal moves WITHOUT
# a viewport resize (grip drag / double-click reset / minimize / restore) —
# the panel must refit on the avoided control's OWN rect/visibility signals
# or its clamp goes stale and it covers the very command box it dodges.
var avoid_control: Control = null:
	set(value):
		if avoid_control != null and is_instance_valid(avoid_control):
			if avoid_control.item_rect_changed.is_connected(_on_avoid_control_changed):
				avoid_control.item_rect_changed.disconnect(_on_avoid_control_changed)
			if avoid_control.visibility_changed.is_connected(_on_avoid_control_changed):
				avoid_control.visibility_changed.disconnect(_on_avoid_control_changed)
		avoid_control = value
		if avoid_control != null:
			avoid_control.item_rect_changed.connect(_on_avoid_control_changed)
			avoid_control.visibility_changed.connect(_on_avoid_control_changed)


func _on_avoid_control_changed():
	if visible:
		_fit_height()


# Session UI-6 (the lead's wave-1 shoot, November 13, 2026): on a very wide
# screen the HUD stands in two full-height columns and the right one is the
# CONTEXT WING (main.gd draws its frame) — the notice rail, the war list and,
# under them, this panel at the column's full width. `avoid_above` is the war
# list's panel (main.gd wires it): the panel docks below it, and refits as it
# grows or goes. Everywhere else the panel stands as before.
const _WING_INSET := 8.0       # inside the wing's frame, as the war list stands (its EDGE_MARGIN)
const _WING_TOP_GAP := 88.0    # under the rail's slot when no war list stands (the list's own NARROW_TOP_GAP)
const _WING_BOTTOM := 10.0     # the column's foot, the command desk's own margin
var avoid_above: Control = null:
	set(value):
		if avoid_above != null and is_instance_valid(avoid_above):
			if avoid_above.item_rect_changed.is_connected(_on_avoid_above_changed):
				avoid_above.item_rect_changed.disconnect(_on_avoid_above_changed)
			if avoid_above.visibility_changed.is_connected(_on_avoid_above_changed):
				avoid_above.visibility_changed.disconnect(_on_avoid_above_changed)
		avoid_above = value
		if avoid_above != null:
			avoid_above.item_rect_changed.connect(_on_avoid_above_changed)
			avoid_above.visibility_changed.connect(_on_avoid_above_changed)


func _on_avoid_above_changed():
	if visible and _wing_band().y > _wing_band().x:
		_fit_height()


func _wing_band() -> Vector2:
	"""The right column's span while the HUD stands in its two columns, else
	(0, 0)."""
	var view := get_viewport().get_visible_rect().size
	if Utils.hud_columns(view).y <= 0.0:
		return Vector2.ZERO
	return Utils.hud_anchor_band(view)


func _wing_top() -> float:
	"""The panel's top in the wing: under the war list (with room left for a
	useful panel), else under the rail's slot — a long war list is stood over
	(this layer is above the list's) rather than squeezing the panel."""
	var top := Utils.TOP_BAR_HEIGHT + Utils.top_bar_growth() + _WING_TOP_GAP
	if avoid_above != null and is_instance_valid(avoid_above) and avoid_above.is_visible_in_tree():
		var below := avoid_above.get_global_rect().end.y + Utils.HUD_MARGIN
		var view_h := get_viewport().get_visible_rect().size.y
		if view_h - _WING_BOTTOM - below >= _DOCK_BESIDE_BELOW_H:
			top = maxf(top, below)
	return top


func _fit_width_in_wing(wing: Vector2) -> void:
	"""The panel at the wing's full width, under the war list."""
	var w := maxf(wing.y - wing.x - 2.0 * _WING_INSET, 240.0)
	scroll.custom_minimum_size.x = w - 24.0
	content_area.custom_minimum_size.x = w - 44.0
	panel_container.offset_left = wing.x + _WING_INSET
	panel_container.offset_right = panel_container.offset_left + w
	panel_container.offset_top = _wing_top()


func _fit_height_in_wing() -> void:
	"""The panel's height in the wing: its content, down to the column's foot
	(the command desk is in the other column — nothing to dodge here)."""
	var vp_bottom := get_viewport().get_visible_rect().size.y
	var top := _wing_top()
	panel_container.offset_top = top
	var header_h := 0.0
	var header = panel_container.get_node_or_null("VBoxContainer/HeaderRow")
	if header != null:
		header_h = header.size.y
	var available := maxf(vp_bottom - _WING_BOTTOM - _CLAMP_MARGIN - top - header_h - 24.0, _MIN_CONTENT_H)
	var content_h := float(content_area.get_content_height()) + 4.0
	scroll.custom_minimum_size.y = _window_on_whole_lines(content_h, available)
	panel_container.size = Vector2.ZERO


var _rest_tick := 0


func _rest_window_soon(_v: float = 0.0) -> void:
	"""BA2-X6: after the scroll has come to rest (the shared top snap runs two frames
	after its last move) the window is set again from where it rests, so that its
	foot falls between two lines at any offset, not only at the top."""
	_rest_tick += 1
	var tick := _rest_tick
	for _i in range(3):
		await get_tree().process_frame
		if not is_inside_tree() or tick != _rest_tick:
			return
	_rest_window()


func _rest_window() -> void:
	if not visible or scroll == null or content_area == null:
		return
	var before: float = scroll.custom_minimum_size.y
	_fit_height()
	if absf(scroll.custom_minimum_size.y - before) > Utils.WHOLE_LINE_EDGE:
		panel_container.size = Vector2.ZERO


func _window_on_whole_lines(content_h: float, available: float) -> float:
	"""The scroll window's height: the content's when it fits, else the room
	there is cut back to the last line that fits WHOLE. BA2-X6 (row BA, BA-2,
	November 15, 2026): a long province — its march, army and attack rows on a
	short screen — opened with its fold through the middle of a line (13 px of
	a row at 5120 × 1440, the frame census). The panel opens at its top, so
	the fold is set between two lines there. The same at any scroll offset `v`
	(`scroll.scroll_vertical`, which the rest sets on a line's top): the window
	is the span from `v` to the last line's foot that fits the room, so a panel
	scrolled to the middle or the end rests on whole lines too."""
	var v := float(scroll.scroll_vertical) if scroll != null else 0.0
	if content_h - v <= available:
		return _steady_window(clampf(content_h - v, 40.0, available))
	var frame: StyleBox = content_area.get_theme_stylebox("normal")
	var top: float = frame.get_margin(SIDE_TOP) if frame != null else 0.0
	var lines: int = content_area.get_line_count()
	var fits := 0.0
	for i in range(lines):
		var line_end: float = top + (float(content_area.get_line_offset(i + 1)) if i + 1 < lines
				else content_h)
		if line_end - v > available:
			break
		fits = line_end - v
	return _steady_window(clampf(fits if fits >= 40.0 else available, 40.0, available))


func _steady_window(h: float) -> float:
	"""A window within the rest's own tolerance of the one standing is left as it
	is: the window sets the bar's range, the range moves the rest - this is what
	keeps the two from chasing each other."""
	var now: float = scroll.custom_minimum_size.y if scroll != null else 0.0
	if now > 0.0 and absf(h - now) <= Utils.WHOLE_LINE_EDGE:
		return now
	return h

var _region: String = ""
# WO-V-D1 (Score Finish Step 7 slice 8): the Build rows fold behind one
# header that names their count — the section had grown from one chips row
# to a header plus up to seven terms rows and fell below the terminal-
# clamped fold. Folded by default; the choice holds for the session.
var _build_open := false
var _map_node = null
# CC-2 "March here": the quotes the backend gave for `_quotes_region` — the
# click orders rendered exactly as quoted, never re-derived here (the CN-3
# rule: the chip says what the quote says).
var _quotes: Dictionary = {}
var _quotes_region := ""
var _march_more := false
const _MARCH_SHOWN := 5
# Row BA, BA-2: the ATTACK rows' "Bring up" fold stands open.
var _bring_open := false
# Session UI-6: the marshals whose "+N orders" row stands open (name -> true).
var _orders_open: Dictionary = {}
# Session UI-6: at the compact view the panel is capped at this share of the
# HUD band (never under _COMPACT_MIN_WIDTH) - it stops covering a third of the map.
const _COMPACT_FRACTION := 0.30
const _COMPACT_MIN_WIDTH := 360.0
# The context verbs a marshal's row leads with when no enemy shares the
# province: the two most useful of these that stand lit, in this order.
const _CONTEXT_VERBS := ["fortify", "unfortify", "drill", "scout", "hold", "garrison", "retreat"]
const _CONTEXT_SHOWN := 2


func _ready():
	close_button.pressed.connect(close_panel)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	content_area.meta_clicked.connect(_on_meta_clicked)
	Utils.on_explanations_changed(_on_explanations_switched)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS keeps the action chips working.
	content_area.mouse_filter = Control.MOUSE_FILTER_PASS
	get_viewport().size_changed.connect(_on_viewport_resized)
	# BA2-X6: a scrolled panel rests with its top on a line's top (the shared rest) and
	# its window on a line's foot (`_rest_window`, run once the scroll has come to rest)
	Utils.keep_whole_lines(scroll)
	scroll.get_v_scroll_bar().value_changed.connect(_rest_window_soon)
	hide()


func _on_viewport_resized():
	if visible:
		_fit_width()
		_fit_height()


func _fit_width() -> void:
	"""UXR-2: the panel's width from the logical viewport (the Scroll and its
	content follow; the PanelContainer shrink-wraps them)."""
	if scroll == null or content_area == null or panel_container == null:
		return
	# Session UI-6: on a very wide screen the panel stands in the right wing.
	var wing := _wing_band()
	if wing.y > wing.x:
		_fit_width_in_wing(wing)
		return
	var view := get_viewport().get_visible_rect().size
	# UXR-D3: docked at the HUD band's left edge, a fraction of its width.
	var band := Utils.hud_band(view)
	var w := Utils.fraction_px(band.y - band.x, _WIDTH_FRACTION, _MIN_WIDTH, _MAX_WIDTH, 24.0)
	if Utils.compact_view():
		# Session UI-6: at the compact view (Interface Scale 2.0 on a 900-px
		# screen) the panel is capped at about 30 % of the HUD band - never under
		# 360 - so it stops covering a third of the map.
		w = minf(w, maxf((band.y - band.x) * _COMPACT_FRACTION, _COMPACT_MIN_WIDTH))
	scroll.custom_minimum_size.x = w - 24.0
	content_area.custom_minimum_size.x = w - 44.0
	panel_container.offset_left = band.x + _PANEL_LEFT
	panel_container.offset_right = panel_container.offset_left + w
	# UXR-D1: the dock clears the top bar's DRAWN strip (its line grows with
	# Text size); the authored 48 at 100 %.
	panel_container.offset_top = _PANEL_TOP + Utils.top_bar_growth()


func show_region(region_name: String, map_node) -> void:
	"""Open (or retarget) the panel for a clicked province."""
	AudioManager.play("select")
	if region_name == "" or map_node == null:
		return
	var retargeted = region_name != _region
	_region = region_name
	_map_node = map_node
	if retargeted:
		_quotes = {}
		_quotes_region = ""
		_march_more = false
		_bring_open = false
		_orders_open = {}
	_fit_width()
	_render()
	show()
	quotes_requested.emit(_region)   # CC-2: the March here rows follow
	if retargeted and scroll != null:
		# A fresh province starts at the top; refresh_if_open (same province,
		# post-chip re-render) keeps the player's scroll position.
		scroll.scroll_vertical = 0


func refresh_if_open() -> void:
	"""Re-render from the map node's current data after a chip command lands
	(the map itself refreshes from every response's game_state.map_data)."""
	if visible and _region != "" and _map_node != null:
		_quotes.erase("day")   # row BA, BA-3: the day's chips are stale once an order landed
		_render()
		quotes_requested.emit(_region)   # CC-2: an order landed — re-quote


func current_region() -> String:
	return _region


func set_march_quotes(region: String, payload) -> void:
	"""CC-2: the quotes for `region` arrived. Dropped when the player has
	moved to another province or shut the panel — a stale answer must never
	draw under the wrong title."""
	if not visible or region != _region or not (payload is Dictionary):
		return
	if not bool(payload.get("success", false)) or str(payload.get("region", "")) != region:
		return
	_quotes = payload
	_quotes_region = region
	_render()


func _on_explanations_switched() -> void:
	_render_keeping_scroll()


# Row IC, directives: the desk's war goals and the courts the player fights,
# handed in by main.gd on every reply (set_war_goal_context).
var _war_goals: Array = []
var _war_enemies: Array = []


func set_war_goal_context(goals: Array, enemies: Array) -> void:
	"""Row IC, directives: store the desk's goal rows and the courts we are at war
	with; an open panel redraws, the reader's scroll kept."""
	_war_goals = goals.duplicate()
	_war_enemies = enemies.duplicate()
	_render_keeping_scroll()


func _open_place_goal_here() -> Dictionary:
	"""The open goal of kind "place" that names this province, else {}."""
	for g in _war_goals:
		if g is Dictionary and str(g.get("kind", "")) == "place" \
				and str(g.get("status", "")) == "open" and str(g.get("target", "")) == _region:
			return g
	return {}


func _war_goal_row(controller: String) -> String:
	"""Row IC, directives: "Make this the war goal" on an enemy's province with no
	open place goal on it; "Your war goal" and "Clear the war goal" where one is
	named. Nothing for our own, a neutral's, or a court we are not fighting."""
	var goal := _open_place_goal_here()
	var folded := Utils.explanations_folded()
	if not goal.is_empty():
		var court := Utils.display_nation_name(str(goal.get("court", "")))
		var clear_tip := "The war with " + court + " will have no goal. Free."
		var clear_chip := Utils.bb_button_chip("goalclear:" + str(goal.get("court", "")), "Clear the war goal",
				Utils.COLOR_WARNING, _CHIP_BG, "", clear_tip if folded else "")
		var row := "[color=#" + Utils.COLOR_GOLD + "]Your war goal[/color]   " + clear_chip
		if not folded:
			row += "  [color=#" + Utils.COLOR_INFO + "]" + clear_tip + "[/color]"
		return row + "\n"
	if controller == _PLAYER_NATION or not (controller in _war_enemies):
		return ""
	var court_name := Utils.display_nation_name(controller)
	var make_tip := "Names " + _region + " as the goal of the war with " + court_name \
		+ ": the desk names it, the map rings it in gold, and the desk offers the march on it as one list. Free."
	var make_chip := Utils.bb_button_chip("goal:" + _region, "Make this the war goal",
			Utils.COLOR_GOLD, _CHIP_BG, "", make_tip if folded else "")
	var make_row := make_chip
	if not folded:
		make_row += "  [color=#" + Utils.COLOR_INFO + "]" + make_tip + "[/color]"
	return make_row + "\n"


func close_panel() -> void:
	if visible:
		AudioManager.play("back")
	hide()
	_region = ""
	closed.emit()


func _on_meta_clicked(meta):
	# Session UI-3: a note (the lead-in's ⓘ) opens in place — a local re-render.
	if Utils.is_note_meta(meta):
		Utils.toggle_note(meta)
		_render_keeping_scroll()
		return
	var meta_str = str(meta)
	if meta_str.begins_with("order:"):
		# "order:<verb>:<MarshalName>" → "<Name>, <verb>" (typed-command echo)
		var parts = meta_str.split(":")
		if parts.size() == 3 and str(parts[2]) != "":
			region_command.emit(str(parts[2]) + ", " + str(parts[1]))
	elif meta_str.begins_with("do:"):
		# The chip carries its full typed command — the same string a player
		# would type; the executor owns every gate.
		var command = meta_str.substr("do:".length())
		if command != "":
			region_command.emit(command)
	elif meta_str.begins_with("goalclear:"):
		# Row IC, directives: "clear the war goal against <court>" (free)
		var goal_court := meta_str.substr("goalclear:".length())
		if goal_court != "":
			region_command.emit("clear the war goal against " + goal_court)
	elif meta_str.begins_with("goal:"):
		# Row IC, directives: "the war goal is <province>" (free)
		var goal_region := meta_str.substr("goal:".length())
		if goal_region != "":
			region_command.emit("the war goal is " + goal_region)
	elif meta_str.begins_with("negotiate:"):
		var nation = meta_str.substr("negotiate:".length())
		if nation != "":
			negotiate_requested.emit(nation)
	elif meta_str == "admiralty":
		admiralty_requested.emit()
	elif meta_str == "toggle:build":
		_build_open = not _build_open
		_render()
	elif meta_str == "toggle:march_more":
		_march_more = not _march_more
		_render()
	elif meta_str == "toggle:bring":
		_bring_open = not _bring_open
		_render_keeping_scroll()
	elif meta_str.begins_with("toggle:orders:"):
		# Session UI-6: a marshal's "+N orders" row opens / shuts in place.
		var who := meta_str.substr("toggle:orders:".length())
		if who != "":
			if _orders_open.has(who):
				_orders_open.erase(who)
			else:
				_orders_open[who] = true
			_render_keeping_scroll()
	elif meta_str.begins_with("select:"):
		# Session UI-6: his name selects him on the map; sends no command.
		var picked := meta_str.substr("select:".length())
		if picked != "":
			marshal_select_requested.emit(picked)


func _render_keeping_scroll() -> void:
	"""Session UI-3: redraw from the map node's data, the reader's scroll kept."""
	if not visible or _region == "" or _map_node == null:
		return
	var sv: int = int(scroll.scroll_vertical)
	_render()
	Utils.restore_scroll(scroll, sv)


func _dim(label: String, why: String, sep: String = "  ") -> String:
	"""Session UI-3: a dimmed chip and the reason it cannot act. On the page the
	reason prints beside it, as it did; Folded it is the chip's hover."""
	if Utils.explanations_folded():
		return Utils.bb_chip_disabled(label, "", why)
	return Utils.bb_chip_disabled(label) + sep + "[color=#" + Utils.COLOR_INFO + "]" + why + "[/color]"


func _facts_row(income: int, stability: int, supply: int, has_garrison: bool, garrison: int, war_damage: int = 0) -> String:
	"""Session UI-4 (November 12, 2026): the province's four facts as ONE figure
	row — a glyph, the figure in the title face, a caption (the form of the
	dispatch's situation row). A fogged figure (-1) reads Unknown, as the page's
	line does. A figure binds to its glyph and caption (U+00A0) so the row wraps
	BETWEEN facts, never through one."""
	var nb := " "
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	var parts: Array = []
	var fig_income: String = "Unknown" if income < 0 else str(income) + "g"
	var fig_stab: String = "Unknown" if stability < 0 else str(stability) + "%"
	var fig_supply: String = "Unknown" if supply < 0 else Utils.format_number(supply)
	parts.append(Utils.bb_glyph("income", 18) + nb + Utils.HEAD_OPEN + fig_income + Utils.HEAD_CLOSE + nb + info + "income[/color]")
	parts.append(Utils.bb_glyph("stability", 18) + nb + Utils.HEAD_OPEN + fig_stab + Utils.HEAD_CLOSE + nb + info + "stability[/color]")
	parts.append(Utils.bb_glyph("supply", 18) + nb + Utils.HEAD_OPEN + fig_supply + Utils.HEAD_CLOSE + nb + info + "supply[/color]")
	if has_garrison:
		var fig_g: String = "Present" if garrison == -1 else Utils.format_number(garrison)
		var cap_g := "garrison (strength unknown)" if garrison == -1 else "garrison"
		parts.append(Utils.bb_glyph("garrison", 18) + nb + Utils.HEAD_OPEN + fig_g + Utils.HEAD_CLOSE + nb + info + cap_g.replace(" ", nb) + "[/color]")
	# Session UI-6 (November 13, 2026): war damage is a RED figure tile in the
	# row (it was a sentence under it); the sentence is the tile's hover.
	if war_damage > 0:
		var red := "[color=#" + Utils.COLOR_ERROR + "]"
		var tile := Utils.bb_glyph("war", 18, Utils.COLOR_ERROR) + nb + "[font=" + Utils.TITLE_FONT + "]" + red \
			+ str(war_damage) + "%[/color][/font]" + nb + red + "war" + nb + "damage[/color]"
		parts.append(Utils.bb_hint(tile, "War damage " + str(war_damage) + "% — suppressing this province's income"))
	return "   ".join(PackedStringArray(parts)) + "\n"


func _build_item(chip: String, terms_text: String) -> String:
	"""Session UI-4: one work of the Build fold. On the page its terms print
	beside it, a row each (as they did); Folded the chip stands alone — its terms
	are its hover — to join the fold's ONE row."""
	if Utils.explanations_folded():
		return chip
	if terms_text == "":
		return "    " + chip
	return "    " + chip + " [color=#" + Utils.COLOR_INFO + "]" + terms_text + "[/color]"


func _caption(text: String) -> String:
	"""Session UI-4: a group's small-caps caption over its ONE row of chips."""
	return "  [color=#" + Utils.COLOR_INFO + "]" + text + "[/color]"


func _chip_row(chips: Array) -> String:
	"""Session UI-4: a group's chips on ONE row, evenly spaced (the readers:
	"ragged small chips", "widen the spacing"). A chip's own spaces are bound, so
	a long row breaks only between chips."""
	return "    " + "   ".join(PackedStringArray(chips))


func _render() -> void:
	var data: Dictionary = _map_node.region_full_data.get(_region, {})
	var visibility = str(_map_node.region_visibility.get(_region, "unknown"))
	var controller_raw = data.get("controller", "Neutral")
	var controller = str(controller_raw) if controller_raw != null else "Neutral"

	title_label.text = _region
	var bbcode = ""

	# ── Controller + terrain ──
	bbcode += Utils.bb_flag(controller, 18)
	bbcode += " [color=#" + Utils.COLOR_GOLD + "][b]" + Utils.display_nation_name(controller) + "[/b][/color]"
	var region_type = str(data.get("region_type", ""))
	var terrain = str(data.get("terrain", ""))
	# Session UI-2: the province's kind and ground as two quiet badges.
	if region_type != "":
		bbcode += "  " + Utils.bb_badge(region_type.replace("_", " ").capitalize(), Utils.COLOR_BADGE_QUIET)
	if terrain != "":
		bbcode += " " + Utils.bb_badge(terrain.replace("_", " ").capitalize(), "5b6b4a")
	# Session UI-3 (November 12, 2026): where the folded lead-in's ⓘ goes — the
	# end of this first line (set below, once the lead-in's literal is read).
	var lead_at := bbcode.length()
	bbcode += "\n"
	# UXR3-79 (Pre-Deploy S15 head, October 25, 2026): the LAND'S NOTE — the
	# poor-country / stripped-by-war mark the doctrines' boards exist to show
	# (SR-7d DC-3a, DOCTRINES_SPEC RV-13) — rides directly under the controller
	# line, in the Lead step, above the ACTIONS block it used to sit beneath
	# (and under the help text, as the last row). Composed by the backend with
	# the fog applied (the stripped mark reads the econ fog; the poor mark is
	# geography and always shows), so it reads the same on an unscouted
	# province and on one in view. Absent = no mark.
	var dmark = data.get("doctrine_supply")
	if dmark is Dictionary and str(dmark.get("line", "")) != "":
		bbcode += "[color=#" + Utils.COLOR_WARNING + "]" + str(dmark.get("line", "")) + "[/color]\n"
	# UXR3-76 (Pre-Deploy S12 part 2): the ACTIONS block — the recruit,
	# build and repair chips this panel exists for — is spliced in HERE,
	# directly under the title line (and, since UXR3-79, the land's note),
	# once the rows are known (below); the province's figures, its forces
	# and its sea follow it.
	# Row IC, directives: the war goal's chip stands at the province's head.
	bbcode += _war_goal_row(controller)
	var actions_at := bbcode.length()
	# R159 (POSITION 7): each core screen names the mechanic it displays.
	# Session UI-3: the line stands behind an ⓘ ("Fold, a switch restores"); On
	# the page it prints exactly as it did.
	var lead_line := "[color=#" + Utils.COLOR_INFO + "]One province — who holds it, what it pays, what defends it. Click the map to choose another.[/color]\n"
	bbcode += Utils.bb_lead(lead_line, "region.lead")
	var lead_mark_text: String = Utils.lead_mark(lead_line, "region.lead")
	if lead_mark_text != "":
		bbcode = bbcode.substr(0, lead_at) + lead_mark_text + bbcode.substr(lead_at)
		actions_at += lead_mark_text.length()
	# S14E-15: a province on a formable's road the bloc has begun carries the
	# Formable Nations page's pointer ("Ireland needs Ulster too — …"), the
	# backend road builder's own sentence. Absent key = no road = no line.
	var road_note := str(data.get("road_note", ""))
	if road_note != "":
		bbcode += "[color=#" + Utils.COLOR_WARNING + "]" + Utils.humanize_nation_keys_in_text(road_note) + ".[/color]\n"

	# ── Fog-honest economy block ──
	var folded_facts := ""   # Session UI-6: Folded, the figures row (spliced in before ACTIONS)
	if visibility == "unknown" or visibility == "last_known":
		var intel_note = "No intelligence" if visibility == "unknown" else "Last known (outdated)"
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + intel_note + " — scout or advance to learn more.[/color]\n"
		# UXR3-F9 (Pre-Deploy S12 part 2): the three figures stand as Unknown.
		# SR-7d DC-3a (DOCTRINES_SPEC RV-13): the poor-country mark is geography
		# and shows on an unscouted province too; the stripped mark reads
		# "Stripped? unknown — scout it" (the backend applied the fog). UXR3-79
		# (S15 head): both read in the land's note under the controller line.
		bbcode += Utils.bb_glyph("income", 16) + " Income: [color=#" + Utils.COLOR_INFO + "]Unknown[/color]   " \
			+ Utils.bb_glyph("stability", 16) + " Stability: [color=#" \
			+ Utils.COLOR_INFO + "]Unknown[/color]   " + Utils.bb_glyph("supply", 16) + " Supply: [color=#" \
			+ Utils.COLOR_INFO + "]Unknown[/color]\n"
	else:
		# WO-V-D2 (Score Finish Step 7 slice 8): no hedge on our own soil — its
		# figures are exact by ownership (`world.region_econ_visible`), and
		# "Partial (reports only)" above them read as doubt about all four.
		if visibility == "partial" and controller != _PLAYER_NATION:
			bbcode += "[color=#" + Utils.COLOR_INFO + "]Intel: Partial (reports only)[/color]\n"
		elif visibility == "stale" and controller != _PLAYER_NATION:
			bbcode += "[color=#" + Utils.COLOR_ORANGE + "]Intel: Stale (outdated)[/color]\n"
		# Session UI-4 (November 12, 2026): the facts as the page prints them (the
		# old lines, byte for byte) are built into `facts_page`; Folded they stand
		# as ONE figure row instead (`_facts_row`) — the readers: "plain lines",
		# "small, plain text". The same four fields either way.
		var effective_income = int(data.get("effective_income", 0))
		var stability = int(data.get("stability", 100))
		var facts_page := ""
		# PC15-16: -1 is the fog sentinel on income/stability too (same
		# CA9-F5 idiom as Supply below) — PARTIAL provinces rendered a
		# fabricated "Income: 0g / Stability: 0%" as fact.
		facts_page += Utils.bb_glyph("income", 16) + " "
		if effective_income < 0:
			facts_page += "Income: [color=#" + Utils.COLOR_INFO + "]Unknown[/color]"
		else:
			facts_page += "Income: [color=#" + Utils.COLOR_GOLD + "]" + str(effective_income) + "g[/color]"
		facts_page += "   " + Utils.bb_glyph("stability", 16)
		if stability < 0:
			facts_page += " Stability: [color=#" + Utils.COLOR_INFO + "]Unknown[/color]"
		else:
			facts_page += " Stability: " + str(stability) + "%"
		# CA9-F5: -1 is the fog sentinel. `format_number(-1)` renders
		# "-1", so both readers of this key must branch — the garrison
		# sibling just below already does.
		var supply_cap := int(data.get("supply_capacity", 0))
		var supply_text := "Unknown" if supply_cap < 0 else Utils.format_number(supply_cap)
		facts_page += "   " + Utils.bb_glyph("supply", 16) + " Supply: " + supply_text + "\n"
		# SR-7d DC-3a (RV-13): the poor / stripped mark moved UP to the land's
		# note under the controller line (UXR3-79, S15 head).
		var garrison_info = _map_node.region_garrisons.get(_region, null)
		var g_strength := 0
		if garrison_info != null:
			g_strength = int(garrison_info.get("strength", 0))
			var g_text = "Present (unknown strength)" if g_strength == -1 else Utils.format_number(g_strength)
			facts_page += Utils.bb_glyph("garrison", 16) + " Garrison: " + g_text + "\n"
		if Utils.explanations_folded():
			# Session UI-6: Folded, the figures row LEADS - it is spliced in under
			# the controller line, before ACTIONS (war damage a red tile in it).
			folded_facts = _facts_row(effective_income, stability, supply_cap, garrison_info != null, g_strength, int(data.get("war_damage", 0)))
		else:
			bbcode += facts_page
		# S14E-D10 (the sweep): the Descent camp's count on the panel the marches
		# are ordered from, the map tooltip's twin (the backend stamps `camp_note`
		# only while the camp counts).
		var camp_count_line := str(data.get("camp_note", ""))
		if camp_count_line != "":
			bbcode += "[color=#" + Utils.COLOR_WARNING + "]" + camp_count_line + "[/color]\n"
		# ── Damage (in-game pass, WO slice 8 follow-up) ──
		# This panel carries the Repair chip and never said WHAT was in
		# ruins: it listed "Buildings: Market" whether that market was
		# working or a wreck, and showed war damage nowhere at all. The
		# map tooltip and the ledger's Territories tab had both marked it
		# for months, so the one surface you ACT from was the blind one
		# and the Repair chip appeared with no visible cause. Same
		# vocabulary as the ledger ("name (damaged)", COLOR_ERROR) so the
		# two surfaces cannot describe one ruin two ways.
		#
		# Fog-safe by construction: the filtered summary sentinels
		# `war_damage` to 0 and `buildings` to [] below FULL on foreign
		# soil, so neither line can render an enemy's ruin.
		var war_dmg := int(data.get("war_damage", 0))
		if war_dmg > 0:
			# Session UI-6: Folded, war damage is a red tile in the figures row
			# (its sentence the tile's hover); the page prints the line as it did.
			if not Utils.explanations_folded():
				bbcode += "War damage: [color=#" + Utils.COLOR_ERROR + "]" \
					+ str(war_dmg) + "%[/color]  [color=#" + Utils.COLOR_INFO \
					+ "]suppressing this province's income[/color]\n"
		var watchtower := str(data.get("watchtower", "none"))
		if watchtower == "damaged":
			bbcode += "Watchtower: [color=#" + Utils.COLOR_ERROR + "]damaged[/color]\n"
		elif watchtower == "under_construction":
			bbcode += "Watchtower: [color=#" + Utils.COLOR_INFO + "]building (" \
				+ str(int(data.get("watchtower_turns_remaining", 0))) + "t)[/color]\n"
		elif watchtower == "active":
			bbcode += "Watchtower: [color=#" + Utils.COLOR_SUCCESS + "]active[/color]\n"
		var buildings = data.get("buildings", [])
		if buildings is Array and buildings.size() > 0:
			var b_names = []
			for b in buildings:
				var bname := str(b.get("type", "?")).replace("_", " ").capitalize()
				if b is Dictionary and b.get("damaged", false):
					b_names.append("[color=#" + Utils.COLOR_ERROR + "]" + bname + " (damaged)[/color]")
				else:
					b_names.append(bname)
			bbcode += "Buildings: " + ", ".join(PackedStringArray(b_names)) + "\n"

	# ── Forces present ──
	var marshals = _map_node.region_marshals.get(_region, [])
	var enemy_names = []
	if marshals is Array:
		for em in marshals:
			# CN-4: an ENEMY, not every foreigner — the chip is an order, not
			# a declaration of war, and "Attack Deroy" beside a Bavarian ally
			# was refused every time ("they are our ally"). The backend marks
			# the courts France is at war with (`at_war_with_player`).
			if str(em.get("nation", "")) != _PLAYER_NATION \
					and bool(em.get("at_war_with_player", false)):
				enemy_names.append(str(em.get("name", "")))
	# Row PW (PW2-D1): the actions left are said once, right under the first rows
	# that carry a price — the forces' orders, else the march-here orders
	# (`_actions_left_words`).
	var ap_said := false
	if marshals is Array and marshals.size() > 0:
		bbcode += "\n" + Utils.HEAD_OPEN + "FORCES PRESENT" + Utils.HEAD_CLOSE + "\n"
		var forces_from := bbcode.length()
		for m in marshals:
			if Utils.explanations_folded():
				bbcode += _marshal_row_folded(m, enemy_names)   # Session UI-6: one row a marshal
			else:
				bbcode += _format_marshal_row(m, enemy_names)
		var ap_under_forces := _actions_left_words(bbcode.substr(forces_from))
		ap_said = ap_under_forces != ""
		bbcode += ap_under_forces

	# ── CC-2 "March here": the click orders, as the backend quoted them ──
	if _quotes_region == _region and not _quotes.is_empty():
		var march := _march_here_section()
		bbcode += march
		if not ap_said:
			bbcode += _actions_left_words(march)

	# ── THE SEA (NUI "The Admiralty on the Map", September 23, 2026) ──
	# A coastal province says what the water around it means: every sea
	# crossing that touches it with the Admiralty's OWN verdict sentence
	# (`crossing_line` — the same string the ledger's Crossings row shows),
	# the port's blockade, and the fleet stationed here. Read from the map
	# node's naval overlay — no fetch, no fog leak (fleet counts are public).
	var sea_overlay = _map_node.naval_overlay if (_map_node != null and "naval_overlay" in _map_node) else {}
	if sea_overlay is Dictionary and not sea_overlay.is_empty():
		var sea_rows := []
		var verdict_entries = sea_overlay.get("sea_link_verdicts", [])
		if verdict_entries is Array:
			for entry in verdict_entries:
				if not (entry is Dictionary):
					continue
				if str(entry.get("link_a", "")) != _region and str(entry.get("link_b", "")) != _region:
					continue
				var verdict := str(entry.get("verdict", ""))
				var vcolor: String = Utils.COLOR_TEXT
				if verdict == "shut":
					vcolor = Utils.COLOR_ERROR
				elif verdict == "landing":
					vcolor = Utils.COLOR_ORANGE
				elif verdict == "window" or verdict == "open" or verdict == "open_ratio":
					vcolor = Utils.COLOR_SUCCESS
				sea_rows.append("  [color=#" + vcolor + "]"
					+ Utils.humanize_nation_keys_in_text(str(entry.get("line", ""))) + "[/color]")
		var ports = sea_overlay.get("blockaded_ports", [])
		if ports is Array and _region in ports:
			sea_rows.append("  [color=#" + Utils.COLOR_ERROR
				+ "]This port is under blockade — its trade halved, its fleet pinned.[/color]")
		var fleets = sea_overlay.get("fleets", [])
		if fleets is Array:
			for f in fleets:
				if not (f is Dictionary) or str(f.get("station", "")) != _region:
					continue
				var admiral := str(f.get("admiral", ""))
				var f_color: String = Utils.COLOR_TEXT
				if bool(f.get("is_player", false)):
					f_color = Utils.COLOR_GOLD
				elif bool(f.get("at_war_with_player", false)):
					f_color = Utils.COLOR_ERROR
				# The backend's adjectival label ("the French fleet", "the Royal
				# Navy") — capitalised as the row's first word; the raw tag + "fleet"
				# only as a fallback for a payload without it.
				var f_label := str(f.get("label", ""))
				if f_label == "":
					f_label = "the " + Utils.display_nation_name(str(f.get("nation", ""))) + " fleet"
				f_label = f_label.substr(0, 1).to_upper() + f_label.substr(1)
				var row := "  [color=#" + f_color + "]" + Utils.humanize_nation_keys_in_text(f_label)
				if admiral != "":
					row += " (Adm. " + admiral + ")"
				row += " — " + Utils.format_number(int(f.get("ships", 0))) + " sail, readiness " \
					+ str(int(f.get("readiness", 0))) + ", " + str(f.get("posture", "guard")) + "[/color]"
				var blockaded_by := str(f.get("blockaded_by", ""))
				if blockaded_by != "":
					row += "  [color=#" + Utils.COLOR_ERROR + "]blockaded by " \
						+ Utils.display_nation_name(blockaded_by) + "[/color]"
				sea_rows.append(row)
		if sea_rows.size() > 0:
			bbcode += "\n" + Utils.HEAD_OPEN + "THE SEA" + Utils.HEAD_CLOSE + "  " \
				+ Utils.bb_button_chip("admiralty", "THE ADMIRALTY", Utils.COLOR_GOLD, _CHIP_BG) + "\n"
			for row in sea_rows:
				bbcode += row + "\n"

	# ── Context actions ──
	var action_rows = []
	var admiralty_captioned := false   # Session UI-4: Folded, the ADMIRALTY caption stands once
	var levy = _map_node.levy_status if _map_node != null else {}

	# ── The levy — CN-3 "The Chip Names the Man" (Sept 22, 2026) ──
	# The row renders where the backend QUOTED it: `recruit_here`, one quote
	# per arm, built from the executor's own selector, gates and pricer
	# (`economy_executor.recruit_quote`, drift-pinned against the real
	# `/command` on every province), and only on the player's own soil and
	# on friendly ground feeding a French corps — where it carries the
	# executor's refusal, because recruiting does not open on ally soil
	# (ruling D5). Measured before: of the 90 chips this row rendered, 69
	# refused and 14 of the 21 that acted raised an arm the label did not
	# name. A chip is now ENABLED only where its levy will be made, and it
	# states its terms — the man, the men, the gold, the pool it draws on;
	# otherwise it is dimmed beside the backend's own reason. Nothing is
	# re-derived here.
	var recruit_here = data.get("recruit_here", {})
	var folded_sub_chip := ""   # Session UI-4: Folded, the substitute chip joins the levy's row
	var recruit_row_at := -1
	if recruit_here is Dictionary and not recruit_here.is_empty():
		for recruit_row in _recruit_rows(recruit_here, levy):
			action_rows.append(recruit_row)
		recruit_row_at = action_rows.size() - 1   # the levy's last row (Folded: its chips)

	# IQ-10 "The Client Pass" (Sept 19, 2026): the substitute market is open
	# on ALLY and VASSAL soil — IQ1-3 opened the granary to the engine's own
	# `ALLY_SUPPLY_STATES` and the backend prices it there (measured on the
	# 1805 boot: Amsterdam, Holland's province with Bernadotte standing on
	# it, 3,193g a substitute batch; Milan 3,672g) — and every row used to
	# sit inside `controller == _PLAYER_NATION`. The ground that feeds us is
	# the ground the backend PRICED (it prices only where a French corps
	# stands, so this needs no second rule). CN-3: the levy no longer rides
	# this gate — it opened the recruit row on a SUBSTITUTE signal while the
	# executor gates recruiting on control, which is how Franconia and Milan
	# rendered six chips that could never act.
	var feeds_us := controller == _PLAYER_NATION \
		or int(data.get("substitute_price_here", 0)) > 0
	if feeds_us:
		# IQ-1 IQ1-3D rider 1: THE SUBSTITUTE MARKET, where the choice is made.
		# Until IQ1-2 the row's headline gold sink had zero mentions on any
		# unprompted surface; the help text closed that, and this closes the
		# rest. The chip is present-but-DIMMED with the reason when it is
		# gated — never absent — which is this project's honest-availability
		# idiom, and it renders on ALLY soil too because the granary is open
		# there (IQ1-3A).
		# CN-4: the chip renders the backend's quote (`substitute_here`,
		# `economy_executor.substitute_quote`, the executor's own gates in its
		# own order): it names the recipient the quote chose — the first
		# infantryman of ours standing here, the market sells muskets — and
		# states the men and the gold the executor will charge, or dims with
		# the executor's own reason. Measured before: it quoted the national
		# "per 10,000" where a field purchase delivers 3,000, it was gated on
		# a national room flag the executor does not read (Milan: enabled,
		# always refused), and at Franche-Comte it named Murat, a cavalryman.
		var sub_q = data.get("substitute_here", {})
		if sub_q is Dictionary and not sub_q.is_empty():
			if bool(sub_q.get("ok", false)):
				var _terms = str(sub_q.get("terms", "")) + " — no men off the rolls"
				var subs = levy.get("substitutes", null) if levy is Dictionary else null
				var _alarm = int(subs.get("alarm_premium_pct", 0)) if subs is Dictionary else 0
				if _alarm > 0:
					_terms += ", +" + str(_alarm) + "% while Europe is alarmed"
				var _room = int(sub_q.get("room", 0))
				if _room > 0:
					_terms += "  (" + Utils.format_number(_room) + " under the establishment)"
				# Session UI-4: Folded, the price rides the chip's face and the
				# terms its hover, and the chip joins the levy's ONE row.
				var _sub_face := "Buy Substitutes"
				var _sub_tip := ""
				if Utils.explanations_folded():
					_sub_face += " · " + Utils.format_number(int(sub_q.get("price", 0))) + "g"
					_sub_tip = _terms
				var _sub_chip := Utils.bb_button_chip("do:buy substitutes for " + str(sub_q.get("recipient", "")), \
						_sub_face, Utils.COLOR_GOLD, _CHIP_BG, "", _sub_tip)
				if Utils.explanations_folded():
					folded_sub_chip = _sub_chip
				else:
					action_rows.append("  Substitutes: " + _sub_chip \
						+ "  [color=#" + Utils.COLOR_SUCCESS + "]" + _terms + "[/color]")
			else:
				var _sub_dim := Utils.bb_chip_disabled("Buy Substitutes", "", str(sub_q.get("short", "")) if Utils.explanations_folded() else "")
				if Utils.explanations_folded():
					folded_sub_chip = _sub_dim
				else:
					action_rows.append("  Substitutes: " + _sub_dim \
						+ "  [color=#" + Utils.COLOR_INFO + "]" + str(sub_q.get("short", "")) + "[/color]")

	# Session UI-4: Folded, the substitute market's chip stands on the levy's ONE
	# row (or, with no levy quoted here, under a RECRUIT caption of its own).
	if folded_sub_chip != "":
		if recruit_row_at >= 0:
			action_rows[recruit_row_at] = str(action_rows[recruit_row_at]) + "   " + folded_sub_chip
		else:
			action_rows.append(_caption("RECRUIT"))
			action_rows.append(_chip_row([folded_sub_chip]))

	# Everything below is OWN soil: a building, a repair and a garrison are
	# the owner's to order, and the executors refuse them on a vassal's
	# province, so the panel does not offer them there.
	if controller == _PLAYER_NATION:
		# Build — every missing building while a slot is free (slot math from
		# the fog-filtered payload; towns/rural report 0 slots so the row
		# hides itself). Watchtowers ride their own field, slot-exempt.
		# WO slice 8 (WO-D4-A): each chip states its terms — cost on the
		# chip, delivered yield after it — every digit read from the
		# backend's `build_terms` payload (the executors' own numbers),
		# never hardcoded here. Absent terms (older payload) fall back to
		# the plain label row.
		var buildings = data.get("buildings", [])
		var used_slots = buildings.size() if buildings is Array else 0
		if data.get("building_under_construction") != null:
			used_slots += 1
		var max_slots = int(data.get("max_building_slots", 0))
		var terms = data.get("build_terms", {})
		if not (terms is Dictionary):
			terms = {}
		var build_rows = []
		var build_chips = ""
		# CRT-9 (CQ-21): every administrative chip below spends one of the
		# turn's administrative actions; with none left each is dimmed and
		# says so (the recruit and substitute chips already did — their
		# quotes run the executor's own gates).
		var admin_why := _admin_why()
		if max_slots > used_slots:
			for def in _BUILD_CHIP_DEFS:
				if not _region_has_building(data, str(def[0])):
					var b_key := str(def[0])
					var t = terms.get(b_key, {})
					if t is Dictionary and t.has("cost"):
						var b_label := str(def[1]) + " " + str(int(t.get("cost", 0))) + "g"
						if admin_why == "":
							# Session UI-4: Folded, the terms ride the chip as its hover.
							build_rows.append(_build_item(Utils.bb_button_chip("do:" + str(def[2]) % _region, b_label, Utils.COLOR_GOLD, _CHIP_BG, "", _build_terms_text(b_key, t) if Utils.explanations_folded() else ""),
								_build_terms_text(b_key, t)))
						else:
							build_rows.append(_build_item(_dim(b_label, admin_why, " "), ""))
					elif admin_why == "":
						build_chips += Utils.bb_button_chip("do:" + str(def[2]) % _region, str(def[1]), Utils.COLOR_GOLD, _CHIP_BG) + " "
					else:
						build_chips += Utils.bb_chip_disabled(str(def[1]), "", admin_why if Utils.explanations_folded() else "") + " "
		if str(data.get("watchtower", "none")) == "none":
			var wt = terms.get("watchtower", {})
			if wt is Dictionary and wt.has("cost"):
				var wt_label := "Watchtower " + str(int(wt.get("cost", 0))) + "g"
				if admin_why == "":
					build_rows.append(_build_item(Utils.bb_button_chip("do:build watchtower in " + _region, wt_label, Utils.COLOR_GOLD, _CHIP_BG, "", "eyes on every adjacent province" if Utils.explanations_folded() else ""),
						"eyes on every adjacent province"))
				else:
					build_rows.append(_build_item(_dim(wt_label, admin_why, " "), ""))
			elif admin_why == "":
				build_chips += Utils.bb_button_chip("do:build watchtower in " + _region, "Watchtower", Utils.COLOR_GOLD, _CHIP_BG) + " "
			else:
				build_chips += Utils.bb_chip_disabled("Watchtower", "", admin_why if Utils.explanations_folded() else "") + " "
		# SR-5b / NV-D9: the naval yard. The backend sends `naval_yard` only
		# where this province is a yard SITE (an anchorage, an admiralty,
		# not a yard already) and states the executor's own verdict in
		# `refusal` — so the chip builds when it is lit and says why when
		# it is dimmed, and the slot arithmetic above never has to guess.
		var yard = terms.get("naval_yard", {})
		if yard is Dictionary and yard.has("cost"):
			var yard_label := "Naval Yard " + Utils.format_number(int(yard.get("cost", 0))) + "g"
			var yard_why := str(yard.get("refusal", ""))
			if yard_why == "":
				yard_why = admin_why
			if yard_why == "":
				# S14G-X137 (Pre-Deploy S14h part 2, October 26, 2026): the chip
				# omitted its action - a raised yard is an ADMINISTRATIVE act.
				# The price is the backend's (`yard_ap_note` on the naval overlay,
				# `naval.ap_cost_note`, the action table's own number).
				var yard_ap := ""
				if _map_node != null and "naval_overlay" in _map_node and _map_node.naval_overlay is Dictionary:
					yard_ap = str(_map_node.naval_overlay.get("yard_ap_note", ""))
				var yard_terms := (yard_ap + " " if yard_ap != "" else "") + "keels laid and corps embarked here · " \
					+ str(int(yard.get("turns", 0))) + " turns · " \
					+ str(int(yard.get("raised", 0))) + " of " + str(int(yard.get("cap", 0))) + " yards raised"
				build_rows.append(_build_item(Utils.bb_button_chip("do:build naval yard in " + _region, yard_label, Utils.COLOR_GOLD, _CHIP_BG, "", yard_terms if Utils.explanations_folded() else ""),
					yard_terms))
			else:
				build_rows.append(_build_item(_dim(yard_label, yard_why, " "), ""))
		if build_rows.size() > 0:
			# The tier upkeep is one figure for every work here — said
			# once on the header, not repeated per row.
			var upkeep := int(terms.get("upkeep", 0))
			# WO-V-D1: one clickable header; the rows only when it is open.
			var works := str(build_rows.size()) + (" work" if build_rows.size() == 1 else " works")
			var build_head := "  [url=toggle:build]" + ("▾ Build" if _build_open else "▸ Build — " + works) + "[/url]"
			if upkeep > 0:
				if Utils.explanations_folded():
					# Session UI-6: a tag, "40g / turn each" - the sentence its hover.
					build_head += " " + Utils.bb_hint(Utils.bb_tag(str(upkeep) + "g / turn each", Utils.COLOR_BADGE_QUIET),
						"each finished work keeps " + str(upkeep) + "g a turn")
				else:
					build_head += " [color=#" + Utils.COLOR_INFO + "](each finished work keeps " + str(upkeep) + "g a turn)[/color]"
			if _build_open:
				build_head += ":"
			action_rows.append(build_head)
			if _build_open:
				# Session UI-4: Folded, the open works stand on ONE row of chips.
				if Utils.explanations_folded():
					action_rows.append(_chip_row(build_rows))
				else:
					for br in build_rows:
						action_rows.append(br)
		if build_chips != "":
			action_rows.append("  Build: " + build_chips
				+ ("" if (admin_why == "" or Utils.explanations_folded()) else "[color=#" + Utils.COLOR_INFO + "]" + admin_why + "[/color]"))

		# Repair — one chip per KIND of ruin, because they are different
		# orders with different effects and (before the in-game pass) war
		# damage had no chip at all: it is repairable for the same 150g,
		# it suppresses the province's income every turn it stands, and
		# the only way to reach it was knowing to type `repair <region>`.
		var needs_repair = str(data.get("watchtower", "")) == "damaged"
		if buildings is Array:
			for b in buildings:
				if b is Dictionary and b.get("damaged", false):
					needs_repair = true
		var rep = terms.get("repair", {})
		var rep_cost := ""
		if rep is Dictionary and rep.has("cost"):
			rep_cost = " " + str(int(rep.get("cost", 0))) + "g"
		# Session UI-4: Folded, the repairs stand on ONE row, each with its terms
		# as its hover (`repair_chips`); the page prints them as it did.
		var repair_chips := []
		if needs_repair and admin_why == "":
			var rw_chip := Utils.bb_button_chip("do:repair buildings in " + _region, "Repair works" + rep_cost, Utils.COLOR_WARNING, _CHIP_BG, "", "restore damaged works — and their upkeep" if Utils.explanations_folded() else "")
			if Utils.explanations_folded():
				repair_chips.append(rw_chip)
			else:
				action_rows.append("  " + rw_chip + "  [color=#" + Utils.COLOR_INFO + "]restore damaged works — and their upkeep[/color]")
		elif needs_repair:
			if Utils.explanations_folded():
				repair_chips.append(_dim("Repair works" + rep_cost, admin_why))
			else:
				action_rows.append("  " + _dim("Repair works" + rep_cost, admin_why))
		# Re-read: the display block's `war_dmg` is scoped to the fog
		# branch it was declared in (the same reason `buildings` is
		# re-declared above). This arm is inside the own-soil gate, so the
		# figure is never fogged.
		var own_war_dmg := int(data.get("war_damage", 0))
		if own_war_dmg > 0:
			var wd_terms := "reduces war damage"
			if rep is Dictionary and rep.has("war_damage_pct"):
				wd_terms = "−" + str(int(rep.get("war_damage_pct", 0))) + "% of " \
					+ str(own_war_dmg) + "% — restores income"
			if admin_why == "":
				var wd_chip := Utils.bb_button_chip("do:repair " + _region, "Repair war damage" + rep_cost, Utils.COLOR_WARNING, _CHIP_BG, "", wd_terms if Utils.explanations_folded() else "")
				if Utils.explanations_folded():
					repair_chips.append(wd_chip)
				else:
					action_rows.append("  " + wd_chip + "  [color=#" + Utils.COLOR_INFO + "]" + wd_terms + "[/color]")
			elif Utils.explanations_folded():
				repair_chips.append(_dim("Repair war damage" + rep_cost, admin_why))
			else:
				action_rows.append("  " + _dim("Repair war damage" + rep_cost, admin_why))
		if not repair_chips.is_empty():
			action_rows.append(_chip_row(repair_chips))

		# DEF-5 naval §9: the dockyard chip — only on player-controlled build
		# sites, price quoted from the backend's live constant (honest-chip
		# idiom; the executor still gates gold/AP/rate).
		var overlay = _map_node.naval_overlay if (_map_node != null and "naval_overlay" in _map_node) else {}
		if overlay is Dictionary:
			var yards = overlay.get("player_dockyards", [])
			if yards is Array and _region in yards:
				var ship_cost = int(overlay.get("ship_cost", 400))
				# NV-12 (recon gap 11): the chip is region-scoped in
				# appearance but NATION-scoped in effect — the keel lands in
				# the first yard, which may not be this one. Say where.
				var yard_note = "a keel in this yard"
				if yards.size() > 0 and str(yards[0]) != _region:
					yard_note = "the keel is laid at " + str(yards[0]) + " (the senior yard)"
				# CN-4: the Admiralty's own gate (`naval.build_ships_refusal`)
				# — the second keel of a turn (the yards at capacity) and a
				# short treasury were enabled chips the executor refused.
				var ship_why = str(overlay.get("ship_build_refusal", ""))
				if ship_why == "":
					ship_why = admin_why
				if ship_why == "":
					# S14G-X137 (Pre-Deploy S14h part 2, October 26, 2026): the keel
					# is an ADMINISTRATIVE act and the chip said no action - the
					# price leads the note, from the overlay (`ship_ap_note`,
					# `naval.ap_cost_note`: the action table's own number).
					var ship_ap := str(overlay.get("ship_ap_note", ""))
					var ship_terms: String = (ship_ap + " " if ship_ap != "" else "") + yard_note
					var ship_chip := Utils.bb_button_chip("do:build ships", "Lay down ships (" + str(ship_cost) + "g)", Utils.COLOR_GOLD, _CHIP_BG, "", ship_terms if Utils.explanations_folded() else "")
					if Utils.explanations_folded():
						# Session UI-4: the Admiralty's group, its caption over its chip.
						action_rows.append(_caption("ADMIRALTY"))
						action_rows.append(_chip_row([ship_chip]))
						admiralty_captioned = true
					else:
						action_rows.append("  " + ship_chip + "  [color=#" + Utils.COLOR_INFO + "]" + ship_terms + "[/color]")
				elif Utils.explanations_folded():
					action_rows.append(_caption("ADMIRALTY"))
					action_rows.append(_chip_row([_dim("Lay down ships (" + str(ship_cost) + "g)", ship_why)]))
					admiralty_captioned = true
				else:
					action_rows.append("  " + _dim("Lay down ships (" + str(ship_cost) + "g)", ship_why))
	elif controller != "Neutral" and controller != "" and visibility != "unknown":
		action_rows.append("  " + Utils.bb_button_chip("negotiate:" + controller, "Negotiate with " + Utils.display_nation_name(controller), Utils.COLOR_COMMAND, _CHIP_BG))

	# NV-6: THE LANDING. The expedition is the one naval verb that needs a
	# destination, and this panel is where a destination is chosen — so its
	# chip lives here, on ANY coastal province (ours, theirs, or a host's),
	# outside the owner branches above. Eligibility and the quoted odds are
	# both resolved server-side by the same functions the executor and the
	# resolver use, so a chip that appears is a chip that sails.
	var naval = _map_node.naval_overlay if (_map_node != null and "naval_overlay" in _map_node) else {}
	if naval is Dictionary:
		var landings = naval.get("expedition_landings", {})
		if landings is Dictionary and landings.has(_region):
			for corps in landings[_region]:
				if not (corps is Dictionary):
					continue
				var who = str(corps.get("marshal", ""))
				var odds = int(corps.get("odds", 0))
				# CRT-9: the state probe's verdict on this corps' landing.
				var land_why := str(corps.get("refusal", ""))
				if land_why != "":
					if Utils.explanations_folded() and not admiralty_captioned:
						action_rows.append(_caption("ADMIRALTY"))
						admiralty_captioned = true
					action_rows.append("  " + _dim("Land " + who + " here", land_why))
					continue
				# S14G-X86 (Pre-Deploy S14h part 2, October 26, 2026): the note
				# leads with the verb's price (`cost_note`, the action table's own
				# number - an expedition is a real commitment) and says WHY the
				# corps may embark where he stands (`from_reason`, the rule in
				# words) - both built once on the backend row, the Admiralty's
				# chips read the same fields.
				var land_cost := str(corps.get("cost_note", ""))
				var land_from := str(corps.get("from", ""))
				var land_from_why := str(corps.get("from_reason", ""))
				if land_from_why != "":
					land_from += " (" + Utils.humanize_nation_keys_in_text(land_from_why) + ")"
				if Utils.explanations_folded() and not admiralty_captioned:
					action_rows.append(_caption("ADMIRALTY"))
					admiralty_captioned = true
				if Utils.explanations_folded():
					# Session UI-6: Folded, the chip stands alone - the men, the odds,
					# what winning the throw gets him and the levers are ITS hover.
					var land_tip: String = (land_cost + " " if land_cost != "" else "") \
						+ Utils.format_number(int(corps.get("strength", 0))) + " men from " + land_from \
						+ " · " + str(odds) + " in 100 slip past"
					var land_prize_said := str(corps.get("prize", ""))
					if land_prize_said != "":
						land_tip += ". If it lands: " + Utils.humanize_nation_keys_in_text(land_prize_said)
					var land_levers := str(corps.get("levers", ""))
					if land_levers != "":
						land_tip += ". " + Utils.humanize_nation_keys_in_text(land_levers)
					action_rows.append("  " + Utils.bb_button_chip("do:land " + who + " in " + _region,
						"Land " + who + " here", Utils.COLOR_GOLD, _CHIP_BG, "", land_tip))
					continue
				action_rows.append("  " + Utils.bb_button_chip(
					"do:land " + who + " in " + _region,
					"Land " + who + " here", Utils.COLOR_GOLD, _CHIP_BG)
					+ "  [color=#" + Utils.COLOR_INFO + "]"
					+ (land_cost + " " if land_cost != "" else "")
					+ Utils.format_number(int(corps.get("strength", 0)))
					+ " men from " + land_from + " · "
					+ str(odds) + " in 100 slip past[/color]")
				# S14G-31: what winning the throw GETS him here - the confirm card's
				# own sentence (`naval.landing_prize_clause`, built on the row): the
				# carve's pointer, what waits ashore as far as the fog admits, the
				# raiding-party floor for a small corps. Absent = not an enemy's shore.
				var land_prize := str(corps.get("prize", ""))
				if land_prize != "":
					action_rows.append("      [color=#" + Utils.COLOR_INFO + "]If it lands: "
						+ Utils.humanize_nation_keys_in_text(land_prize) + ".[/color]")
				# SR-5b (AAR-D7): what would make it a better throw — the
				# resolver's own odds re-asked, one lever at a time.
				var levers := str(corps.get("levers", ""))
				if levers != "":
					action_rows.append("      [color=#" + Utils.COLOR_INFO + "]"
						+ Utils.humanize_nation_keys_in_text(levers) + "[/color]")
		else:
			# NV-12 (recon gap 3): a too-large, inland, or non-consenting
			# landing used to produce NO chip and NO message — absence was
			# the only signal. The withheld chip now states the executor's
			# own reason (honest availability: never dark and silent).
			var blocked = naval.get("expedition_blocked", {})
			if blocked is Dictionary and blocked.has(_region):
				if Utils.explanations_folded() and not admiralty_captioned:
					action_rows.append(_caption("ADMIRALTY"))
					admiralty_captioned = true
				action_rows.append("  " + _dim("No landing here", Utils.humanize_nation_keys_in_text(str(blocked[_region]))))

	# Session UI-6: Folded, the figures row leads (under the controller line,
	# before ACTIONS); the page has none here and splices ACTIONS as it did.
	if action_rows.size() > 0:
		var actions := Utils.HEAD_OPEN + "ACTIONS" + Utils.HEAD_CLOSE + "\n"
		for row in action_rows:
			actions += row + "\n"
		bbcode = bbcode.substr(0, actions_at) + actions + "\n" + bbcode.substr(actions_at)
	if folded_facts != "":
		bbcode = bbcode.substr(0, actions_at) + folded_facts + bbcode.substr(actions_at)
	# Row BA, BA-3 (K14): an open day that awaits our word is the most pressing
	# thing in its province — its block (heading, morning, chips) is the FIRST
	# section: under the province's own header lines (and, Folded, the figures
	# row) and above ACTIONS, not down among the ATTACK rows.
	if _quotes_region == _region and not _quotes.is_empty():
		# Row PW: ...and with it the order that makes the province OURS, when a
		# corps of ours stands on it (`_take_section`) — at the head, where the
		# eye lands, not down among the march rows.
		var day_text := _day_block() + _take_section()
		if day_text != "":
			var day_at: int = actions_at + folded_facts.length()
			bbcode = bbcode.substr(0, day_at) + day_text + bbcode.substr(day_at)

	content_area.text = bbcode
	# fit_content needs a layout pass before get_content_height() is real.
	call_deferred("_fit_height")


func _fit_height() -> void:
	# Size the scroll window to the content, capped so the panel bottom stays
	# above the terminal's live top edge (or the viewport bottom). Runs
	# deferred after every render and again on viewport resize.
	if not visible or scroll == null:
		return
	# Session UI-6: in the right wing the column's foot is the floor.
	if _wing_band().y > _wing_band().x:
		_fit_height_in_wing()
		return
	var vp_bottom := get_viewport().get_visible_rect().size.y
	var limit := vp_bottom
	if avoid_control != null and is_instance_valid(avoid_control) and avoid_control.visible \
			and _avoid_overlaps_panel():
		limit = minf(limit, avoid_control.get_global_rect().position.y)
	var header_h := 0.0
	var header = panel_container.get_node_or_null("VBoxContainer/HeaderRow")
	if header != null:
		header_h = header.size.y
	# Panel chrome: top offset + header + separations + PanelContainer margins.
	var available := limit - _PANEL_TOP - Utils.top_bar_growth() - _CLAMP_MARGIN - header_h - 24.0
	# S14G-15: too little room above the terminal -> dock at its right edge at
	# full height (down to the map controls' strip) instead of the 120 floor;
	# room again (the window lowered) -> back at the HUD band's left edge.
	var beside_left := _beside_terminal_left(available)
	_place_dock_left(beside_left if beside_left >= 0.0 else _home_left())
	if beside_left >= 0.0:
		available = vp_bottom - _DOCK_BOTTOM_RESERVE - _PANEL_TOP - Utils.top_bar_growth() \
				- _CLAMP_MARGIN - header_h - 24.0
	available = maxf(available, _MIN_CONTENT_H)
	var content_h := float(content_area.get_content_height()) + 4.0
	scroll.custom_minimum_size.y = _window_on_whole_lines(content_h, available)
	# The PanelContainer keeps yesterday's taller size unless reset — shrink it
	# back to its minimum so closing a long province and opening a short one
	# doesn't leave a stretched empty frame.
	panel_container.size = Vector2.ZERO


func _home_left() -> float:
	"""The panel's home dock: the HUD band's left edge plus the authored 12
	(the same number `_fit_width` writes)."""
	return Utils.hud_band(get_viewport().get_visible_rect().size).x + _PANEL_LEFT


func _beside_terminal_left(available: float) -> float:
	"""S14G-15: the left edge for the panel docked beside the terminal, or
	-1.0 when it should stay home. Beside only when the room above the
	terminal is under `_DOCK_BESIDE_BELOW_H` AND the terminal's right edge
	leaves the panel's whole width inside the HUD band (else the floor, as
	before: a panel pushed off the band is worse than a short one)."""
	if available >= _DOCK_BESIDE_BELOW_H:
		return -1.0
	if avoid_control == null or not is_instance_valid(avoid_control) or not avoid_control.visible:
		return -1.0
	if not _avoid_overlaps_panel():
		return -1.0   # Session UI-6: a column beside the panel (32:9) is nothing to dock around
	var left :=avoid_control.get_global_rect().end.x + Utils.HUD_MARGIN
	var width: float = scroll.custom_minimum_size.x + 24.0   # `scroll` is untyped: no `:=`
	var band := Utils.hud_band(get_viewport().get_visible_rect().size)
	if left + width > band.y:
		return -1.0
	return left


func _avoid_overlaps_panel() -> bool:
	"""Session UI-6: does the avoided control (the command desk) share any of
	the panel's HOME columns? The 32:9 layout stands the desk in a full-height
	column to the panel's left, where its top edge says nothing about how tall
	the panel may be - clamping to it collapsed the panel's height. Measured
	against the home dock (never the live offset), so docking beside the desk
	does not flip the answer."""
	if avoid_control == null or not is_instance_valid(avoid_control):
		return false
	var rect := avoid_control.get_global_rect()
	var panel_left := _home_left()
	var panel_right: float = panel_left + scroll.custom_minimum_size.x + 24.0   # `scroll` is untyped: no `:=` on its fields
	return rect.position.x < panel_right and rect.end.x > panel_left


func _place_dock_left(left: float) -> void:
	"""S14G-15: put the panel's left edge at `left`, its width unchanged
	(the Scroll's width plus the leather's 24 — what `_fit_width` wrote)."""
	panel_container.offset_left = left
	panel_container.offset_right = left + scroll.custom_minimum_size.x + 24.0


# Build chip catalog: backend BUILDING_TYPES key → chip label → the typed
# command (the executor's _extract_building_type keys off these words).
const _BUILD_CHIP_DEFS = [
	["supply_depot", "Depot", "build depot in %s"],
	["fortification", "Fort", "build fort in %s"],
	["training_ground", "Training Ground", "build training ground in %s"],
	["market", "Market", "build market in %s"],
	["stables", "Stables", "build stables in %s"],
]


const _RECRUIT_ARMS := ["infantry", "cavalry", "artillery"]

# CN-3 rider 1: the marshal row names the arm the payload already carries
# (`arm` rides the base marshal dict; an enemy's only at FULL visibility).
# The player could not see that Murat is the cavalryman and Lannes the
# infantryman standing in one province — the fact the recruit chips turn on.
const _ARM_WORD := {"infantry": " foot", "cavalry": " horse", "artillery": " guns", "emperor": " Guard"}


func _arm_word(m: Dictionary) -> String:
	return str(_ARM_WORD.get(str(m.get("arm", "")), ""))


func _recruit_rows(recruit_here: Dictionary, levy) -> Array:
	# CN-3: one chip per arm — enabled with its terms where the quote says
	# the levy will be made, dimmed with the quote's own reason where it will
	# not. When every arm is refused for ONE reason (ally soil, no
	# administrative action left, unrest) the reason is said once, beside
	# three dimmed chips, rather than three times.
	var rows := []
	var shorts := {}
	var any_ok := false
	for arm in _RECRUIT_ARMS:
		var q = recruit_here.get(arm, {})
		if q is Dictionary:
			if bool(q.get("ok", false)):
				any_ok = true
			else:
				shorts[str(q.get("short", ""))] = true
	# Session UI-4 (November 12, 2026): Folded, the levy is one caption (RECRUIT,
	# the ordinance's line under it) and ONE row of chips — each live arm carries
	# its price on its face ("Infantry · 598g") and its terms as its hover, each
	# refused arm its reason as its hover. On the page the rows below stand as
	# they did (the terms and reasons printed beside their chips).
	if Utils.explanations_folded():
		return _recruit_rows_folded(recruit_here, levy)
	if not any_ok and shorts.size() == 1:
		var chips := ""
		for arm in _RECRUIT_ARMS:
			chips += Utils.bb_chip_disabled(str(arm).capitalize(), "", str(shorts.keys()[0]) if Utils.explanations_folded() else "") + " "
		rows.append("  Recruit: " + chips + ("" if Utils.explanations_folded() else " [color=#" + Utils.COLOR_INFO + "]" \
			+ str(shorts.keys()[0]) + "[/color]"))
		return rows
	rows.append("  Recruit:" + _ordinance_note(levy))
	# Session UI-3 (the interim reading, F24): Folded, a refused arm's reason is
	# its chip's hover, so the refused chips stand together on ONE row after the
	# levies that can be made — one bare chip a line read as a ragged column.
	var refused_row := ""
	for arm in _RECRUIT_ARMS:
		var q = recruit_here.get(arm, {})
		if not (q is Dictionary):
			continue
		if bool(q.get("ok", false)):
			rows.append("    " + Utils.bb_button_chip("do:recruit " + str(arm) + " in " + _region, str(arm).capitalize(), Utils.COLOR_GOLD, _CHIP_BG) \
				+ "  [color=#" + Utils.COLOR_INFO + "]" + str(q.get("terms", "")) + "[/color]")
		elif Utils.explanations_folded():
			refused_row += ("" if refused_row == "" else " ") + _dim(str(arm).capitalize(), str(q.get("short", "")))
		else:
			rows.append("    " + _dim(str(arm).capitalize(), str(q.get("short", ""))))
	if refused_row != "":
		rows.append("    " + refused_row)
	return rows


func _recruit_rows_folded(recruit_here: Dictionary, levy) -> Array:
	"""Session UI-4: the levy Folded — see `_recruit_rows`. The chips are the
	LAST row returned (the substitute market's chip joins it, in `_render`)."""
	# Session UI-6 (November 13, 2026): the caption, the ordinance as a
	# "Levies ×1.45" tag (the whole sentence its hover) and the arm chips stand
	# on ONE line; when every arm is refused for the SAME reason, ONE lock chip
	# "Levies" carries it as its hover instead of three dim chips.
	var rows := []
	var chips := []
	var refused := []   # [arm word, reason] pairs
	var shorts := {}
	for arm in _RECRUIT_ARMS:
		var q = recruit_here.get(arm, {})
		if not (q is Dictionary):
			continue
		if bool(q.get("ok", false)):
			var face := str(arm).capitalize()
			if int(q.get("price", 0)) > 0:
				face += " · " + Utils.format_number(int(q.get("price", 0))) + "g"
			chips.append(Utils.bb_button_chip("do:recruit " + str(arm) + " in " + _region, face, Utils.COLOR_GOLD, _CHIP_BG, "", str(q.get("terms", ""))))
		else:
			refused.append([str(arm).capitalize(), str(q.get("short", ""))])
			shorts[str(q.get("short", ""))] = true
	var locked := []
	if chips.is_empty() and shorts.size() == 1 and refused.size() > 0:
		locked.append(Utils.bb_chip_disabled("Levies", "", str(shorts.keys()[0])))
	else:
		for r in refused:
			locked.append(_dim(str(r[0]), str(r[1])))
	var line := _caption("RECRUIT")
	var tag := _ordinance_tag(levy)
	if tag != "":
		line += "  " + tag
	line += "   " + "   ".join(PackedStringArray(chips + locked))
	rows.append(line)
	return rows


func _ordinance_tag(levy) -> String:
	"""Session UI-6: the ordinance as ONE tag - "Levies ×1.45" over the limit (the
	figure every chip's price already carries), "Levies open" under it - the
	page's whole sentence (`_ordinance_note`'s words) its hover. "" with no limit."""
	if not (levy is Dictionary) or int(levy.get("force_limit", 0)) <= 0:
		return ""
	var over := int(levy.get("over_by", 0))
	if over > 0:
		var sentence := Utils.format_number(over) + " over the ordinance"
		var face := "Levies over"
		var mult := int(levy.get("ordinance_mult_pct", 100))
		if mult > 100:
			var times: String = "%.2f" % (float(mult) / 100.0)
			sentence += " — every levy costs ×" + times
			face = "Levies ×" + times
		return Utils.bb_hint(Utils.bb_tag(face, Utils.COLOR_WARNING), sentence)
	return Utils.bb_hint(Utils.bb_tag("Levies open", Utils.COLOR_SUCCESS),
		Utils.format_number(int(levy.get("headroom", 0))) + " under the ordinance")


func _ordinance_note(levy) -> String:
	# "The Levy is Open" (econ spec review §6): say where the army stands
	# against the ordinance, right where the choice is made — the played
	# campaign spent ten turns +59,000 over the limit and read the warning as
	# a ban. CN-3 rider 4: over the limit the ordinance is a PRICE, not a bar
	# (every levy costs (1 + overage) more — the figure on each chip already
	# includes it), so the line says the multiplier instead of a warning with
	# no verb. The per-arm price moved onto the chips (rider 7: the old
	# "872g per 10,000 foot here" quoted men a field levy never delivers).
	if not (levy is Dictionary) or int(levy.get("force_limit", 0)) <= 0:
		return ""
	var over := int(levy.get("over_by", 0))
	if over > 0:
		var txt := Utils.format_number(over) + " over the ordinance"
		var mult := int(levy.get("ordinance_mult_pct", 100))
		if mult > 100:
			txt += " — every levy costs ×" + ("%.2f" % (float(mult) / 100.0))
		return "  [color=#" + Utils.COLOR_WARNING + "]" + txt + "[/color]"
	return "  [color=#" + Utils.COLOR_SUCCESS + "]" \
		+ Utils.format_number(int(levy.get("headroom", 0))) + " under the ordinance[/color]"


func _format_marshal_row(m: Dictionary, enemy_names: Array) -> String:
	var m_name = str(m.get("name", "?"))
	# CN-4: the printed name, never the roster key ("ArchdukeCharles" —
	# Golden Rule 7). The order chips keep the key (they address our own
	# marshals, whose keys are their names).
	var shown_name = Utils.humanize_entity_name(m_name)
	var m_nation = str(m.get("nation", ""))
	var m_strength = int(m.get("strength", 0))
	var row = "  "
	# S14E-X79: Berthier's muster for each Attack chip below, one line apiece.
	var muster_lines := []
	# Row BA, BA-2: under them, the order that brings each corps standing by.
	var bring_lines := []
	var bring_seen := {}
	var nation_color = Utils.COLOR_TEXT if m_nation == _PLAYER_NATION else Utils.COLOR_ERROR
	row += "[color=#" + nation_color + "]" + shown_name + "[/color]"
	if m_strength > 0:
		row += " [color=#" + Utils.COLOR_INFO + "](" + Utils.format_number(m_strength) + _arm_word(m) + ")[/color]"
	if m_nation == _PLAYER_NATION:
		# Order chips — mirror the Generals-card gating: nothing for a
		# broken/retreating marshal. The map summary carries tactical_state
		# (flat bools: fortified/retreating/broken/drilling) for PLAYER
		# marshals only, fog-safe.
		var tactical = m.get("tactical_state", {})
		if tactical is Dictionary and not tactical.is_empty():
			var retreating = bool(tactical.get("retreating", false))
			var broken = bool(tactical.get("broken", false))
			# Session UI-4 (November 12, 2026): Folded, his orders stand on ONE row
			# of chips UNDER his name and strength (each chip leads with two spaces,
			# so the row is indented four) — the readers: "ragged small chips".
			if Utils.explanations_folded():
				row += "\n  "
			# CF-6 (October 17, 2026): the dimmed list is shared by the CN-4
			# chips below and the three new ones after them, so one reason is
			# said once for every chip it stops.
			var dimmed_all := []
			if not retreating and not broken:
				# CN-4: Fortify likewise — offered only where the works would
				# begin (`tactical_state.fortify_refusal`, the executor's own
				# gates), else dimmed at the end of the row with the reason:
				# Ney and Davout beside Archduke Charles had enabled Fortify
				# chips that answered "cannot fortify while engaged".
				# CRT-9 (Oct 3, 2026): the orders his STATE or the turn's
				# actions refuse — `tactical_state.order_refusals`, the
				# backend's one probe (`state_probe.order_refusals`), the
				# executor's gates in the executor's order. A refused chip is
				# dimmed with the reason, said once for every chip it stops
				# (CQ-21: at zero actions every chip was offered and refused).
				var refusals = tactical.get("order_refusals", {})
				if not (refusals is Dictionary):
					refusals = {}
				var dimmed := []
				var fortified = bool(tactical.get("fortified", false))
				var fortify_why = str(refusals.get("fortify", tactical.get("fortify_refusal", "")))
				if fortified:
					var unfortify_why = str(refusals.get("unfortify", ""))
					if unfortify_why == "":
						row += "  " + Utils.bb_button_chip("order:unfortify:" + m_name, "Unfortify", Utils.COLOR_COMMAND, _CHIP_BG)
					else:
						dimmed.append(["Unfortify", unfortify_why])
				elif fortify_why == "":
					# S14G-X168 (Pre-Deploy S14h part 2, October 26, 2026): the chip sends '<Name>, fortify' and priced it
					# nowhere - a corps standing NEUTRAL goes defensive first and pays two. The figure is the payload's
					# `tactical_state.order_prices.fortify` (the executor's own, `insist_terms`), the way Hold is priced below.
					var fortify_label := "Fortify"
					var fortify_prices = tactical.get("order_prices", {})
					if fortify_prices is Dictionary and int(fortify_prices.get("fortify", 0)) > 0:
						fortify_label += " (" + Utils.plural(int(fortify_prices.get("fortify", 0)), "action") + ")"
					row += "  " + Utils.bb_button_chip("order:fortify:" + m_name, fortify_label, Utils.COLOR_COMMAND, _CHIP_BG)
				# CN-4: the Drill chip is offered only where the drill would
				# begin; otherwise it is dimmed at the end of the row beside
				# the executor's own reason (`tactical_state.drill_refusal`,
				# `tactical_executor.drill_refusal`). Measured before: at the
				# 1805 boot every French corps stood one province from Mack
				# and every Drill chip answered "cannot drill with enemy
				# forces nearby".
				var drill_why = str(refusals.get("drill", tactical.get("drill_refusal", "")))
				var drilling = bool(tactical.get("drilling", false))
				if not drilling and drill_why == "":
					row += "  " + Utils.bb_button_chip("order:drill:" + m_name, "Drill", Utils.COLOR_COMMAND, _CHIP_BG)
				var scout_why = str(refusals.get("scout", ""))
				if scout_why == "":
					row += "  " + Utils.bb_button_chip("order:scout:" + m_name, "Scout", Utils.COLOR_COMMAND, _CHIP_BG)
				else:
					dimmed.append(["Scout", scout_why])
				# Attack chips — only enemies the fog actually shows here
				# (enemy marshals ride region_marshals at FULL visibility
				# only), capped so a stacked province stays readable.
				var attack_why = str(refusals.get("attack", ""))
				for i in range(mini(enemy_names.size(), 2)):
					var enemy = str(enemy_names[i])
					if enemy != "":
						# CN-4: the printed name on the label AND in the
						# command, so the terminal echo and the up-arrow
						# history read what the player saw (the parser
						# resolves the printed form — pinned by driving it).
						var enemy_shown = Utils.humanize_entity_name(enemy)
						if attack_why == "":
							row += "  " + Utils.bb_button_chip("do:" + m_name + ", attack " + enemy_shown, "Attack " + enemy_shown, Utils.COLOR_ERROR_CHIP, _CHIP_BG)
							# S14E-X79: the chip sends at once -- the muster the
							# map attack card shows (who answers the guns, the
							# band) stands under it, from the same quote.
							var chip_muster := _here_attack_muster(m_name, enemy)
							if chip_muster != "":
								muster_lines.append("Attack " + enemy_shown + ": " + _muster_tail(chip_muster))
							var chip_alarm := _here_attack_muster(m_name, enemy, "alarm")   # S14G-X165: what a win here adds to Europe's alarm
							if chip_alarm != "":
								muster_lines.append("Attack " + enemy_shown + ": " + chip_alarm)
							bring_lines.append_array(_bring_lines(_here_attack_bring(m_name, enemy), bring_seen))
						else:
							dimmed.append(["Attack " + enemy_shown, attack_why])
				if not fortified and fortify_why != "":
					dimmed.append(["Fortify", fortify_why])
				if not drilling and drill_why != "":
					dimmed.append(["Drill", drill_why])
				dimmed_all = dimmed
			# CF-6 (October 17, 2026): Hold · Fall back · Garrison — the three
			# verbs a player gives every campaign that were typed-only. Each
			# is offered only where the probe (`tactical_state.order_refusals`)
			# has no reason for it and dimmed with the reason otherwise, priced
			# on the label from `tactical_state.order_prices` (the executor's
			# own figure — a literal marshal's hold is 1), and sends the
			# literal typed string through the chip road ("<Name>, hold" /
			# "<Name>, retreat" / "<Name>, garrison"). Rendered for a
			# recovering or broken corps too: the probe already carries his
			# state as the reason, and a corps recovering beside the enemy is
			# exactly the one whose Fall back matters.
			row += _state_order_chips(m_name, tactical, dimmed_all)
			row += _dimmed_chips(dimmed_all)
	for muster_line in muster_lines:
		row += "\n    [color=#" + Utils.COLOR_INFO + "]" + str(muster_line) + "[/color]"
	for bring_line in bring_lines:
		row += "\n" + str(bring_line)
	return row + "\n"


# Session UI-6: the arm's stat glyph for the FORCES PRESENT row's strength figure.
const _ARM_GLYPH := {"infantry": "foot", "cavalry": "horse", "artillery": "guns", "emperor": "command"}


func _marshal_row_folded(m: Dictionary, enemy_names: Array) -> String:
	"""Session UI-6 (November 13, 2026): ONE row per marshal, Folded - his name
	(ours: a link, meta "select:<Name>", that selects him on the map), his
	strength with the arm's glyph, a status badge (`MarshalState.status_of`, the
	one reading the Generals and the war room share), then the CONTEXT verbs -
	Attack <enemy> where an enemy shares the province, else the two most useful
	orders that stand lit - and a "+N orders" toggle (meta "toggle:orders:<Name>")
	that opens the rest in place. The muster lines the page prints under each
	Attack chip are that chip's hover. Every chip sends the command it always
	sent; the probe's reasons are the locked chips' hovers."""
	var m_name := str(m.get("name", "?"))
	var shown_name := Utils.humanize_entity_name(m_name)
	var mine := str(m.get("nation", "")) == _PLAYER_NATION
	var nb := " "
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	var row := "  "
	if mine:
		row += "[url=select:" + m_name + "][color=#" + Utils.COLOR_TEXT + "]" + shown_name + "[/color][/url]"
	else:
		row += "[color=#" + Utils.COLOR_ERROR + "]" + shown_name + "[/color]"
	var m_strength := int(m.get("strength", 0))
	if m_strength > 0:
		var fig := Utils.format_number(m_strength)
		var arm_glyph := str(_ARM_GLYPH.get(str(m.get("arm", "")), ""))
		var face := info + fig + "[/color]"
		if arm_glyph != "":
			face = Utils.bb_glyph(arm_glyph, 16, Utils.COLOR_INFO) + nb + face
		row += "  " + Utils.bb_hint(face, fig + _arm_word(m))
	var tactical = m.get("tactical_state", {})
	if not mine or not (tactical is Dictionary) or tactical.is_empty():
		return row + "\n"
	var view: Dictionary = _MarshalState.from_board(m, {})
	var status: Dictionary = _MarshalState.status_of(view)
	var tone := str(status.get("tone", Utils.COLOR_GOLD))
	var badge := Utils.bb_tag(str(status.get("label", "")), tone)
	var badge_glyph := str(status.get("glyph", ""))
	if badge_glyph != "":
		badge = Utils.bb_glyph(badge_glyph, 16, tone) + nb + badge
	row += "  " + Utils.bb_hint(badge, str(status.get("detail", "")))
	# ── the verbs ──
	var specs: Array = _MarshalState.order_specs(view)
	var refusals: Dictionary = view["refusals"]
	var grounded := bool(view.get("broken", false)) or bool(view.get("retreating", false))
	var attack_why := str(refusals.get("attack", ""))
	var context := []
	var attack_lit := false
	# Row BA, BA-2: the order that brings each corps standing by, one line of
	# chips under the verbs (each chip's reason its hover).
	var bring_lines := []
	var bring_seen := {}
	if not grounded:
		for i in range(mini(enemy_names.size(), 2)):
			var enemy := str(enemy_names[i])
			if enemy == "":
				continue
			var enemy_shown := Utils.humanize_entity_name(enemy)
			if attack_why == "":
				bring_lines.append_array(_bring_lines(_here_attack_bring(m_name, enemy), bring_seen))
				var tips := []
				var chip_muster := _here_attack_muster(m_name, enemy)
				if chip_muster != "":
					tips.append(_muster_tail(chip_muster))
				var chip_alarm := _here_attack_muster(m_name, enemy, "alarm")   # what a win here adds to Europe's alarm
				if chip_alarm != "":
					tips.append(chip_alarm)
				context.append(Utils.bb_button_chip("do:" + m_name + ", attack " + enemy_shown, "Attack " + enemy_shown, Utils.COLOR_ERROR_CHIP, _CHIP_BG, " · ".join(PackedStringArray(tips))))
				attack_lit = true
			else:
				context.append(Utils.bb_chip_disabled("Attack " + enemy_shown, "", attack_why))
	var shown_verbs := {}
	if not attack_lit:
		var lit_chips := 0
		for want in _CONTEXT_VERBS:
			if lit_chips >= _CONTEXT_SHOWN:
				break
			for spec in specs:
				if str(spec["verb"]) == str(want) and not bool(spec["locked"]):
					context.append(_order_chip(spec, m_name))
					shown_verbs[str(want)] = true
					lit_chips += 1
	var rest_lit := []
	var rest_locked := []
	for spec in specs:
		var verb := str(spec["verb"])
		if verb == "cancel" or shown_verbs.has(verb):
			continue
		if bool(spec["locked"]):
			rest_locked.append(_order_chip(spec, m_name))
		else:
			rest_lit.append(_order_chip(spec, m_name))
	var rest := rest_lit + rest_locked
	var orders_open := _orders_open.has(m_name)
	var verbs_line := context.duplicate()
	if not rest.is_empty():
		var toggle_words := "fewer orders" if orders_open else "+" + str(rest.size()) + " orders"
		var toggle_bb := info + toggle_words + "[/color]"
		if not orders_open:
			# The CN-4 census (the lead's engine run, November 13): the orders
			# folded behind "+N orders" showed no reason anywhere — a folded
			# reason is a hover, so the fold's own hover names each hidden
			# order, and why a locked one would be refused.
			var hidden := []
			for spec in specs:
				var hidden_verb := str(spec["verb"])
				if hidden_verb == "cancel" or shown_verbs.has(hidden_verb):
					continue
				var part := str(spec["label"])
				if bool(spec["locked"]) and str(spec.get("reason", "")) != "":
					part += " — " + str(spec.get("reason", ""))
				hidden.append(part)
			toggle_bb = Utils.bb_hint(toggle_bb, " · ".join(PackedStringArray(hidden)))
		verbs_line.append("[url=toggle:orders:" + m_name + "]" + toggle_bb + "[/url]")
	if not verbs_line.is_empty():
		row += "\n    " + "   ".join(PackedStringArray(verbs_line))
	if orders_open and not rest.is_empty():
		row += "\n    " + "   ".join(PackedStringArray(rest))
	for bring_line in bring_lines:
		row += "\n" + str(bring_line)
	return row + "\n"


func _order_chip(spec: Dictionary, m_name: String) -> String:
	"""Session UI-6: one of a marshal's order slots as a chip - priced on its
	face when it costs ("Hold (2 actions)"), locked (lock + dim words) with the
	probe's reason as its hover when the executor would refuse it."""
	var verb := str(spec["verb"])
	var label := str(spec["label"])
	var price := int(spec["price"])
	if price > 0:
		label += " (" + Utils.plural(price, "action") + ")"
	if bool(spec["locked"]):
		return Utils.bb_chip_disabled(label, "", str(spec["reason"]))
	return Utils.bb_button_chip("order:" + verb + ":" + m_name, label, Utils.COLOR_COMMAND, _CHIP_BG)


func _here_attack_muster(m_name: String, enemy: String, key: String = "muster") -> String:
	"""S14E-X79: Berthier's one-line muster for `<m_name>, attack <enemy>` when
	both stand in this province -- the quote the backend's `here` list carries
	(`order_quotes.march_quotes_for_region`), "" until the quotes for THIS
	province have arrived, or when that attack is refused or has no muster."""
	if _quotes_region != _region or _quotes.is_empty():
		return ""
	var rows = _quotes.get("attack", [])
	if not (rows is Array):
		return ""
	for row in rows:
		if not (row is Dictionary) or str(row.get("enemy", "")) != enemy:
			continue
		var here = row.get("here", [])
		if not (here is Array):
			return ""
		for q in here:
			if q is Dictionary and str(q.get("marshal", "")) == m_name and bool(q.get("ok", false)):
				return str(q.get(key, ""))   # S14G-X165: "alarm" too (the muster's alarm clause)
	return ""


# ── Row BA, BA-2 (November 14, 2026): the plan of battle at the attack row ──
# An attack quote carries `bring` (`order_quotes.bring_quotes`): for each corps
# of ours standing by that the muster says will NOT come, or may not, the order
# the game already has that would bring him — SUPPORT's own quote (its command,
# its price) with the muster's reason or his odds before and after. A chip
# sends that typed order down the chip road ("do:"), and the muster then reads
# him as ordered. No new order and no new number: the panel prints what it is
# given, and judges nothing.
const _BRING_LEAD := "Bring up"
const _BRING_SENTENCE := "the written order that brings him to these guns"


func _here_attack_bring(m_name: String, enemy: String) -> Array:
	"""The `bring` rows of `<m_name>, attack <enemy>` when both stand in this
	province — off the same `here` quote `_here_attack_muster` reads; [] until
	the quotes for THIS province have arrived."""
	if _quotes_region != _region or _quotes.is_empty():
		return []
	var rows = _quotes.get("attack", [])
	if not (rows is Array):
		return []
	for row in rows:
		if not (row is Dictionary) or str(row.get("enemy", "")) != enemy:
			continue
		var here = row.get("here", [])
		if not (here is Array):
			return []
		for q in here:
			if q is Dictionary and str(q.get("marshal", "")) == m_name and bool(q.get("ok", false)):
				var bring = q.get("bring", [])
				return bring if bring is Array else []
	return []


func _bring_order(b: Dictionary) -> String:
	"""The order in its own words: the quote's command after the man's name
	(`Soult, support Ney` -> `support Ney`)."""
	var command := str(b.get("command", ""))
	var cut := command.find(", ")
	return command.substr(cut + 2) if cut >= 0 else command


func _bring_label(b: Dictionary, priced: bool = true, with_order: bool = true) -> String:
	"""`Soult · support Ney · 1 AP` — the man, the order in its own words and,
	when it would be taken, its price; `Soult · 1 AP` where the line's lead-in
	has already said the order (`with_order` false)."""
	var label := str(b.get("shown", ""))
	if with_order:
		label += " · " + _bring_order(b)
	if priced:
		label += " · " + Utils.quote_price_tail(b)     # BA3-X5
	return label


func _bring_said(b: Dictionary) -> String:
	"""What the order changes, then what else the click does: the muster's
	reason he stays or his odds before and after (`why`), what the order's
	first step MEETS (`contact`: a corps we see on his road — he attacks at once
	if the numbers favour him, else asks), and the quote's own riders
	(`_quote_notes`: the order it replaces, whether he may object). For an
	order that would be refused, the quote's reason alone."""
	if not bool(b.get("ok", false)):
		return str(b.get("refusal", ""))
	var parts := []
	var why := str(b.get("why", ""))
	if why != "":
		parts.append(why)
	var contact := str(b.get("contact", ""))
	if contact != "" and contact != str(b.get("note", "")):
		parts.append(contact)
	var notes := _quote_notes(b)
	if notes != "":
		parts.append(notes)
	return " · ".join(PackedStringArray(parts))


func _bring_chip(b: Dictionary, tip: String, with_order: bool = true) -> String:
	"""One `bring` row as a chip: lit, it sends the row's own command; locked
	(the order would be refused) it keeps its words and its place."""
	if not bool(b.get("ok", false)):
		return Utils.bb_chip_disabled(_bring_label(b, false, with_order), "", tip)
	return Utils.bb_button_chip("do:" + str(b.get("command", "")), _bring_label(b, true, with_order),
		Utils.COLOR_GOLD, _CHIP_BG, "", tip)


func _bring_block(groups: Array) -> String:
	"""The plan under a row of attack chips. ONE corps that could lead: his
	`Bring up` line, as it stands in a marshal's own row. Several: one fold —
	`▸ Bring up — 9 orders`, what they are its hover (on the page: beside it) —
	and, open, a line per lead: `to support Davout:` then a chip per corps, the
	man and the price. Nine chips under five were a wall (the frames, November 15)."""
	var out := ""
	if groups.is_empty():
		return out
	if groups.size() == 1:
		for line in _bring_lines(groups[0][1], {}):
			out += str(line) + "\n"
		return out
	var total := 0
	for g in groups:
		for b in g[1]:
			if b is Dictionary and not bool(b.get("already", false)) and str(b.get("command", "")) != "":
				total += 1
	if total == 0:
		return out
	var head := ("▾ " + _BRING_LEAD) if _bring_open \
			else ("▸ " + _BRING_LEAD + " — " + Utils.plural(total, "order"))
	if Utils.explanations_folded():
		out += "  [url=toggle:bring]" + Utils.bb_hint(head, _BRING_SENTENCE) + "[/url]\n"
	else:
		out += "  [url=toggle:bring]" + head + "[/url]  [color=#" + Utils.COLOR_INFO + "](" \
			+ _BRING_SENTENCE + ")[/color]\n"
	if _bring_open:
		for g in groups:
			for line in _bring_lines(g[1], {}, "    ", "", false):
				out += str(line) + "\n"
	return out


func _bring_lines(rows: Array, seen: Dictionary, indent: String = "    ",
		lead_in: String = _BRING_LEAD, say_what: bool = true) -> Array:
	"""The `bring` rows as lines, each order once (`seen`, by its command: two
	Attack chips on one field share their rows). Folded: ONE line — the lead-in
	(its sentence the hover), then the chips, each chip's reason its hover. On
	the page: the lead-in and its sentence, then a line per chip with its reason
	beside it. `say_what` false: the sentence was said by the fold above."""
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	var folded := Utils.explanations_folded()
	var chips := []
	var out := []
	var kept := []
	var orders := {}
	for b in rows:
		if not (b is Dictionary) or bool(b.get("already", false)):
			continue
		var command := str(b.get("command", ""))
		if command == "" or seen.has(command):
			continue
		seen[command] = true
		kept.append(b)
		orders[_bring_order(b)] = true
	# The panel is narrow: where every row on the line is the SAME order (they
	# are, for one lead), the lead-in says it once — "Bring up to support Ney:"
	# — and each chip is the man and the price.
	var once: bool = orders.size() == 1
	if once:
		var to_order: String = "to " + str(orders.keys()[0])
		lead_in = (lead_in + " " + to_order) if lead_in != "" else to_order
	for b in kept:
		var said := _bring_said(b)
		if folded:
			chips.append(_bring_chip(b, said, not once))
		else:
			out.append(indent + "  " + _bring_chip(b, "", not once)
				+ ("  " + info + said + "[/color]" if said != "" else ""))
	if not chips.is_empty():
		var said_lead := info + lead_in + ":[/color]"
		if say_what:
			said_lead = Utils.bb_hint(said_lead, _BRING_SENTENCE)
		out.append(indent + said_lead + "   " + "   ".join(PackedStringArray(chips)))
	elif not out.is_empty():
		out.insert(0, indent + info + lead_in
			+ ((" — " + _BRING_SENTENCE) if say_what else "") + ":[/color]")
	return out


func _muster_tail(muster: String) -> String:
	"""S14E-X79: the muster line, short for a chip's tail -- 'Berthier adds: '
	dropped, and of the line's ' — '-joined clauses (who answers the guns /
	the figures / the band) the first and the last kept."""
	var line := muster.strip_edges()
	if line.begins_with("Berthier adds: "):
		line = line.substr("Berthier adds: ".length())
	var parts := line.split(" — ")
	if parts.size() > 2:
		# S14G-X61 (Pre-Deploy S14h part 2, October 26, 2026): the S14G-14 note
		# ("The band weighs a force of his you have not scouted — scout
		# Carniola. On the men in view alone ...") carries its own ' — ', so
		# "the last clause" was the NOTE's tail and the chip lost the TRUE band
		# ("Ney would answer the guns — scout Carniola. On the men in view
		# alone the odds read 'favorable' ..." and never 'unfavorable'). Keep the
		# clause that carries the band ("the balance of force looks X") up to its
		# sentence's end, and cut the note's sentences from the tail; with no
		# band clause (nothing weighed) the first and last clauses stand as before.
		for i in range(1, parts.size()):
			var clause := str(parts[i])
			if clause.find("balance of force looks") < 0:
				continue
			var stop := clause.find(". ")
			if stop >= 0:
				clause = clause.substr(0, stop + 1)
			return str(parts[0]) + " — " + clause
		return str(parts[0]) + " — " + str(parts[parts.size() - 1])
	return line


func _state_order_chips(m_name: String, tactical: Dictionary, dimmed: Array) -> String:
	"""CF-6: the Hold / Fall back / Garrison chips of one corps of ours —
	lit where `order_refusals` carries no reason for the verb, else added to
	`dimmed` with the reason. The label carries the price when it is not
	free ("Hold (2 actions)"); the free retreat has none."""
	var refusals = tactical.get("order_refusals", {})
	if not (refusals is Dictionary):
		refusals = {}
	var prices = tactical.get("order_prices", {})
	if not (prices is Dictionary):
		prices = {}
	var out := ""
	for spec in [["hold", "Hold"], ["retreat", "Fall back"], ["garrison", "Garrison"]]:
		var verb := str(spec[0])
		var label := str(spec[1])
		var ap := int(prices.get(verb, 0))
		if ap > 0:
			label += " (" + Utils.plural(ap, "action") + ")"
		var why := str(refusals.get(verb, ""))
		if why == "":
			out += "  " + Utils.bb_button_chip("order:" + verb + ":" + m_name, label, Utils.COLOR_COMMAND, _CHIP_BG)
		else:
			dimmed.append([label, why])
	return out


# Row PW, PW2-D1 (November 19, 2026): a price tag reads in actions — "Hold
# (2 actions)", never "(2 AP)": four blind readers of four could not say what
# AP stands for. Where the panel shows a price it also says, once, how many
# actions are left this turn (the map's `action_pools`, the top bar's own
# figure) — the number a price is read against.
func _actions_left_words(shown: String) -> String:
	# (a chip binds its spaces — U+00A0, UXR3-83 — so the tag is read with both)
	var flat := shown.replace("\u00a0", " ")
	if not (flat.contains(" action)") or flat.contains(" actions)")
			or flat.contains(" action ·") or flat.contains(" actions ·")):
		return ""
	if _map_node == null or not ("action_pools" in _map_node) or not (_map_node.action_pools is Dictionary) \
			or not (_map_node.action_pools as Dictionary).has("military"):
		return ""
	var left := int((_map_node.action_pools as Dictionary).get("military", 0))
	return "\n[color=#" + Utils.COLOR_INFO + "]You have " + Utils.plural(left, "action") + " left this turn[/color]\n"


func _march_here_section() -> String:
	"""CC-2 "March here": the backend's quotes as rows of chips — MARCH HERE
	(every corps of ours standing elsewhere), SUPPORT <ally> (one row per
	corps of ours standing here) and ATTACK <enemy> (one row per enemy corps
	we see here). A chip sends its quoted command through the same road as a
	typed one; a refused order is dimmed beside the quote's own reason."""
	var out := ""
	var march = _quotes.get("march", [])
	if march is Array and not march.is_empty():
		# Row PW: a corps within one move pays the move's price and arrives now;
		# further off it is the standing march (each row says which).
		out += _march_caption("SEND A CORPS HERE", "next door is a move, and he arrives now; further off he marches on each turn")
		out += _quote_rows(march)
	var support = _quotes.get("support", [])
	if support is Array:
		for row in support:
			if row is Dictionary:
				out += _march_caption("SUPPORT " + str(row.get("ally_shown", "")).to_upper(), "he follows, and marches to the guns")
				out += _quote_rows(row.get("quotes", []))
	# AO (October 17, 2026): the SUPPORT that stands — one row per corps of
	# ours standing here, each chip `<Marshal>, follow <ally>`.
	var follow = _quotes.get("follow", [])
	if follow is Array:
		for row in follow:
			if row is Dictionary:
				out += _march_caption("FOLLOW " + str(row.get("ally_shown", "")).to_upper(),
					"he marches where " + str(row.get("ally_shown", "")) + " marches, turn after turn, and to his guns")
				out += _quote_rows(row.get("quotes", []))
	# AO: the Staff's one order for the Emperor's column — a chip when the
	# army can march here as one, else dimmed beside the reason (the law not
	# in force, no Emperor in the field, authority below the gate, the pool).
	var army = _quotes.get("army", null)
	if army is Dictionary and not army.is_empty():
		out += _march_caption("THE ARMY", "one order, the Staff's price, every corps within the Emperor's reach")
		out += _quote_rows([army])
		out += _army_detour_rows(army)   # S14E-X135: which corps take a long or foreign road
		out += _army_rider_rows(army)   # S14G-11 / S14G-7 / S14G-2: and which cross guarded ground, march to a front, carry terms
	var attack = _quotes.get("attack", [])
	if attack is Array:
		for row in attack:
			if row is Dictionary:
				# Row BA, BA-4 (BA3-X5): an attack that is a WORD of an open day
				# is offered by the day's own chips above (`_day_block`, priced
				# in points) — not a second time here as an ordinary attack.
				var ordinary: Array = []
				for q in row.get("quotes", []):
					if not (q is Dictionary) or str((q as Dictionary).get("word", "")) == "":
						ordinary.append(q)
				if ordinary.is_empty():
					continue
				out += "\n" + Utils.HEAD_OPEN + "ATTACK " \
					+ str(row.get("enemy_shown", "")).to_upper() + Utils.HEAD_CLOSE + "\n"
				out += _quote_rows(ordinary)
	# Row IC, Session 2 (IC-7): "Look at it" — our corps that can scout this
	# province from where they stand (the backend's `look` rows).
	out += _look_rows(_quotes.get("look", []))
	return out


func _look_rows(rows) -> String:
	"""Row IC, Session 2 (IC-7): a chip per corps of ours that can look into
	this province — "Davout · 1 action" sends `Davout, scout <province>` down
	the same road as a typed order; one whose state refuses the scout is
	dimmed beside the game's own reason. "" when no corps is within reach."""
	if not (rows is Array) or (rows as Array).is_empty():
		return ""
	var chips := []
	var dimmed := []
	for r in rows:
		if not (r is Dictionary) or str(r.get("command", "")) == "":
			continue
		var ap := int(r.get("ap", 0))
		var label := str(r.get("shown", "")) + " · " + ("free" if ap <= 0 else Utils.plural(ap, "action"))
		if bool(r.get("ok", false)):
			chips.append(Utils.bb_button_chip("do:" + str(r.get("command", "")), label, Utils.COLOR_GOLD,
				_CHIP_BG, "", "He scouts it from " + str(r.get("from", "")) + "."))
		else:
			dimmed.append([str(r.get("shown", "")), str(r.get("refusal", ""))])
	if chips.is_empty() and dimmed.is_empty():
		return ""
	var out := _march_caption("LOOK AT IT", "a corps within reach scouts the province from where it stands")
	if not chips.is_empty():
		out += _chip_row(chips) + "\n"
	if not dimmed.is_empty():
		out += _dimmed_chips(dimmed) + "\n"
	return out


func _take_section() -> String:
	"""Row PW (the first playtest: "i had 3 people in colinia and no one could
	take it"): a corps of ours stands HERE and the province is not ours — the
	backend's `take` rows (`order_quotes.take_quote`): the order that takes it
	as a chip ("Take Carniola — Ney · 1 action", "Storm Vienna — Davout"), with
	the storm's reckoning under it, or the plain reason nothing would."""
	var take = _quotes.get("take", [])
	if not (take is Array) or take.is_empty():
		return ""
	var out := "\n" + Utils.HEAD_OPEN + "TAKE THIS PROVINCE" + Utils.HEAD_CLOSE + "\n"
	var said := {}
	for q in take:
		if not (q is Dictionary):
			continue
		var ground = q.get("ground", {})
		var line := str(ground.get("line", "")) if ground is Dictionary else ""
		var who := str(q.get("shown", ""))
		if bool(q.get("ok", false)) and str(q.get("command", "")) != "":
			var label := (str(ground.get("remedy_label", "Take it")) if ground is Dictionary else "Take it") \
				+ " — " + who + " · " + Utils.plural(int(q.get("ap", 1)), "action")
			var reckoning := str(q.get("muster", "")).strip_edges()
			var note := str(q.get("note", "")).strip_edges()
			var hover := " ".join(PackedStringArray([line, reckoning, note])).strip_edges()
			out += "  " + Utils.bb_button_chip("do:" + str(q.get("command", "")), label,
				Utils.COLOR_GOLD, _CHIP_BG, "", hover if Utils.explanations_folded() else "") + "\n"
			if not Utils.explanations_folded():
				for extra in [line, reckoning, note]:
					if str(extra) != "":
						out += "    [color=#" + Utils.COLOR_INFO + "]" + str(extra) + "[/color]\n"
			elif not said.has(line) and line != "":
				out += "    [color=#" + Utils.COLOR_INFO + "]" + line.substr(0, 1).to_upper() + line.substr(1) + ".[/color]\n"
				said[line] = true
		else:
			var why := str(q.get("refusal", "")).strip_edges()
			if why == "":
				why = line
			if why != "" and not said.has(why):
				out += "  [color=#" + Utils.COLOR_WARNING + "]" + why.substr(0, 1).to_upper() + why.substr(1) \
					+ ("" if why.ends_with(".") else ".") + "[/color]\n"
				said[why] = true
	return out


func _day_chip_tip(chip: Dictionary) -> String:
	"""A day's chip, hovered: why it is locked; what the word does and the rest of
	it (row BA, BA-5: the chip's `does` and `more`, the table's own words); whether
	the marshal may object. A chip from before BA-5 carries its odds alone."""
	var parts: Array = []
	if not bool(chip.get("ok", false)) and str(chip.get("why", "")) != "":
		parts.append(str(chip.get("why", "")))
	var does := str(chip.get("does", "")).strip_edges()
	if does != "":
		does = does.substr(0, 1).to_upper() + does.substr(1)
		parts.append(does if does.ends_with(".") else does + ".")
	if str(chip.get("more", "")) != "":
		parts.append(str(chip.get("more", "")))
	if str(chip.get("counsel", "none")) == "possible":
		parts.append("The marshal may object to this word.")
	if does == "" and str(chip.get("odds", "")) != "":
		parts.append("The odds read: " + str(chip.get("odds", "")) + ".")
	return " ".join(PackedStringArray(parts))


func _day_block() -> String:
	"""Row BA, BA-3: a day of battle open on this field and awaiting OUR word
	(the quotes' `day` block): the chips the table offers, above the ATTACK
	rows. An order chip carries `@day:` + its command, a word chip
	`@word:<word>:<enemy>` — main.gd routes both; the table's own panel is the
	same chips."""
	var day = _quotes.get("day", null)
	if not (day is Dictionary) or not bool(day.get("open", false)) \
			or str(day.get("awaits", "")) != "ours" or bool(day.get("pending", false)):
		return ""
	var chips = day.get("chips", [])
	if not (chips is Array) or (chips as Array).is_empty():
		return ""
	var title := "THE DAY AT " + str(day.get("field_shown", "")).to_upper() + " — " \
		+ Utils.plural(int(day.get("ours", 0)), "point").to_upper()   # BA3-X19: "1 POINT"
	var row := []
	# the server orders the words once for every surface: array order, never re-sorted
	for chip in chips:
		if not (chip is Dictionary):
			continue
		# a word that costs nothing shows no price
		var price := int(chip.get("price", 0))
		var label := str(chip.get("label", "")) if price <= 0 \
			else "%s · %d" % [str(chip.get("label", "")), price]
		var tip := _day_chip_tip(chip)
		var word := str(chip.get("word", ""))
		var command := ("@word:%s:%s" % [word, str(day.get("enemy", ""))]) if word != "" \
			else "@day:" + str(chip.get("command", ""))
		if bool(chip.get("ok", false)) and command != "@day:":
			row.append(Utils.bb_button_chip("do:" + command, label, Utils.COLOR_GOLD, _CHIP_BG, "", tip))
		else:
			row.append(Utils.bb_chip_disabled(label, "", tip))
	if row.is_empty():
		return ""
	var out := "\n" + Utils.HEAD_OPEN + title + Utils.HEAD_CLOSE + "\n"
	var morning := str(day.get("morning", ""))
	if morning != "":
		out += "  [color=#" + Utils.COLOR_INFO + "]" + morning + "[/color]\n"
	# Row BA, BA-5: Berthier's reading of his next word, as the table's head says it
	var reading = day.get("reading", null)
	if reading is Dictionary and str((reading as Dictionary).get("line", "")) != "":
		out += "  " + Utils.bb_hint("[color=#" + Utils.COLOR_WARNING + "]Berthier's reading: " \
			+ str(reading.get("line", "")) + ".[/color]", str(reading.get("hover", ""))) + "\n"
	return out + _chip_row(row) + "\n"


func _march_caption(title: String, sentence: String) -> String:
	"""Session UI-6: a march group's caption. On the page the sentence prints
	beside it (as it did); Folded the caption stands alone and the sentence is
	its hover."""
	if Utils.explanations_folded():
		return "\n" + Utils.bb_hint(Utils.HEAD_OPEN + title + Utils.HEAD_CLOSE, sentence) + "\n"
	return "\n" + Utils.HEAD_OPEN + title + Utils.HEAD_CLOSE + "  [color=#" + Utils.COLOR_INFO + "]" + sentence + "[/color]\n"


func _quote_rows(quotes) -> String:
	"""One chip per order the backend will take, nearest first (five, then
	"+N more…"); the refused ones grouped under their reason."""
	var out := ""
	if not (quotes is Array):
		return out
	var shown := 0
	var hidden := 0
	var dimmed := []
	var open_chips := []   # Session UI-4: Folded, the open orders' chips
	# Row BA, BA-2: each attack quote's `bring` rows — the order that brings a
	# corps standing by — under the row's chips (`_bring_block`).
	var bring_groups := []    # [the lead's printed name, his `bring` rows]
	for q in quotes:
		if not (q is Dictionary):
			continue
		if not bool(q.get("ok", false)):
			dimmed.append([str(q.get("shown", "")), str(q.get("refusal", ""))])
			continue
		if shown >= _MARCH_SHOWN and not _march_more:
			hidden += 1
			continue
		shown += 1
		var notes := _quote_notes(q)
		# Session UI-6: Folded, the Staff's per-corps lines (the long road, the
		# guarded ground, the front, the terms) ride the ARMY chip's hover.
		if Utils.explanations_folded() and str(q.get("kind", "")) == "army":
			var corps_said := _army_corps_tip(q)
			if corps_said != "":
				notes = notes + (" · " if notes != "" else "") + corps_said
		# Session UI-4 (November 12, 2026): Folded, the open orders stand on ONE
		# row of chips, what each would also do (`notes`) its hover; the page
		# prints a chip and its notes a line each, as it did.
		var quote_chip := Utils.bb_button_chip("do:" + str(q.get("command", "")), _quote_label(q),
			Utils.COLOR_GOLD, _CHIP_BG, "", notes if Utils.explanations_folded() else "")
		var bring = q.get("bring", [])
		if bring is Array and not bring.is_empty():
			bring_groups.append([str(q.get("shown", "")), bring])
		if Utils.explanations_folded():
			open_chips.append(quote_chip)
			continue
		out += "  " + quote_chip
		if notes != "":
			out += "  [color=#" + Utils.COLOR_INFO + "]" + notes + "[/color]"
		out += "\n"
	if not open_chips.is_empty():
		out += _chip_row(open_chips) + "\n"
	out += _bring_block(bring_groups)
	# The refused: all of them when nothing is open (the reason IS the
	# answer), otherwise behind "+N more…" so the open orders lead.
	if not dimmed.is_empty():
		if shown == 0 or _march_more:
			out += _dimmed_chips(dimmed) + "\n"
		else:
			hidden += dimmed.size()
	if hidden > 0:
		out += "  [url=toggle:march_more][color=#" + Utils.COLOR_INFO + "]+" + str(hidden) \
			+ " more…[/color][/url]\n"
	elif _march_more and (shown > _MARCH_SHOWN or (not dimmed.is_empty() and shown > 0)):
		out += "  [url=toggle:march_more][color=#" + Utils.COLOR_INFO + "]fewer[/color][/url]\n"
	return out


func _army_detour_rows(army: Dictionary) -> String:
	"""S14E-X135: one note-coloured line under the army row for each corps whose
	road would be asked about (`corps[].detour`, S14E-X88) -- the row's note
	counts them ("3 of 5 corps take a long or foreign road"), these say which."""
	var out := ""
	if Utils.explanations_folded():
		return out   # Session UI-6: Folded, these ride the army chip's hover (`_army_corps_tip`)
	var corps = army.get("corps", [])
	if not (corps is Array):
		return out
	for c in corps:
		if not (c is Dictionary):
			continue
		var detour := str(c.get("detour", ""))
		if detour == "":
			continue
		out += "    [color=#" + Utils.COLOR_INFO + "]" + str(c.get("shown", "")) + " — " + detour + "[/color]\n"
	return out


func _army_rider_rows(army: Dictionary) -> String:
	"""S14G-11 / S14G-7 / S14G-2: the army row's other riders, one note-coloured
	line per corps that carries one -- the guarded ground its road crosses
	(`corps[].guard`), the front it marches to (`corps[].front`) and the standing
	order's terms (`corps[].terms`), each the sentence the corps' own card prints."""
	var out := ""
	if Utils.explanations_folded():
		return out   # Session UI-6: Folded, these ride the army chip's hover (`_army_corps_tip`)
	var corps = army.get("corps", [])
	if not (corps is Array):
		return out
	for c in corps:
		if not (c is Dictionary):
			continue
		for rider in ["guard", "front", "terms"]:
			var said := str(c.get(rider, ""))
			if said != "":
				out += "    [color=#" + Utils.COLOR_INFO + "]" + str(c.get("shown", "")) + " — " + said + "[/color]\n"
	return out


func _army_corps_tip(army: Dictionary) -> String:
	"""Session UI-6: the per-corps lines (detour, guard, front, terms) the page
	prints under the army row, as ONE string for the ARMY chip's hover."""
	var said_all := []
	var corps = army.get("corps", [])
	if not (corps is Array):
		return ""
	for c in corps:
		if not (c is Dictionary):
			continue
		for rider in ["march_cost", "detour", "guard", "front", "terms"]:   # BA2-X21: the march's cost in men first
			var said := str(c.get(rider, ""))
			if said != "":
				said_all.append(str(c.get("shown", "")) + " — " + said)
	return " · ".join(PackedStringArray(said_all))


func _quote_label(q: Dictionary) -> String:
	"""`Soult · 2 actions · 3 turns` — the man, the price, the clock."""
	var label := str(q.get("shown", ""))
	if bool(q.get("already", false)):
		return label + " · already ordered"
	var kind := str(q.get("kind", ""))
	if kind == "attack":
		label += " · attack"
	elif kind == "march_attack":
		label += " · march & attack"
	elif kind == "army":
		# AO: `The army · 6 corps · 2 actions · longest 3 turns`
		var corps = q.get("corps", [])
		var n: int = corps.size() if corps is Array else 0
		label += " · " + Utils.plural(n, "corps") + " · " + Utils.plural(int(q.get("ap", 0)), "action")
		var longest := int(q.get("turns", 0))
		label += " · " + ("this turn" if longest == 0 else "longest " + Utils.plural(longest, "turn"))
		return label
	label += " · " + Utils.quote_price_tail(q)     # BA3-X5: a word of the day is priced in points
	if kind != "attack":
		var turns := int(q.get("turns", 0))
		if bool(q.get("halts", false)):
			label += " · halts at the approach"           # BA-4: the approach rule
		else:
			label += " · " + ("this turn" if turns == 0 else Utils.plural(turns, "turn"))
	return label


func _quote_notes(q: Dictionary) -> String:
	"""What the click would also do: the contact on the road, the standing
	order it REPLACES (the executor cancels the old one without a word), and
	whether he may object."""
	var notes := []
	var note := str(q.get("note", ""))
	if note != "":
		notes.append(note)
	var camp := str(q.get("camp", ""))   # S14E-13: what the march takes out of the Descent camp
	if camp != "":
		notes.append(camp)
	var departs := str(q.get("departs", ""))   # S14E-13's sweep: what the march costs the corps as it stands
	if departs != "":
		notes.append(departs)
	var march_cost := str(q.get("march_cost", ""))   # BA2-X21: the men the order's first march costs
	if march_cost != "":
		notes.append(march_cost)
	var detour := str(q.get("detour", ""))   # S14E-22: the detour round a road the diplomacy shuts
	if detour != "":
		notes.append(detour)
	var pay := str(q.get("pay", ""))   # S14E-X67: the campaign pay the destination draws
	if pay != "":
		notes.append(pay)
	var guard := str(q.get("guard", ""))   # S14G-11: the guarded ground the road crosses (the Ansbach trap's price)
	if guard != "":
		notes.append(guard)
	var front := str(q.get("front", ""))   # S14G-7: the front the destination is (an ally's province whose war a truce of ours leaves running)
	if front != "":
		notes.append(front)
	var terms_text := str(q.get("terms", ""))   # S14G-2 / S14G-3: what the standing order does once taken
	if terms_text != "":
		notes.append(terms_text)
	var replaces := str(q.get("replaces", ""))
	if replaces != "" and not bool(q.get("already", false)):
		notes.append("replaces " + replaces)
	# S14E-X79: an attack chip sends at once, so the map attack card's line --
	# Berthier's muster: who answers the guns, and the band they make -- rides
	# the row in short (`_muster_tail`).
	var muster := str(q.get("muster", ""))
	if muster != "" and str(q.get("kind", "")) == "attack":
		notes.append("Berthier: " + _muster_tail(muster))
	var alarm := str(q.get("alarm", ""))   # S14G-X165: what a win here adds to Europe's alarm
	if alarm != "" and str(q.get("kind", "")) == "attack":
		notes.append(alarm)
	if str(q.get("objection", "none")) == "possible":
		notes.append("he may object")
	return " · ".join(PackedStringArray(notes))


func _dimmed_chips(dimmed: Array) -> String:
	"""CRT-9: the refused chips, grouped by their reason — each reason said
	once after the chips it stops ("the one reason", CQ-21's done-when)."""
	var out := ""
	var reasons := []
	for entry in dimmed:
		if not (str(entry[1]) in reasons):
			reasons.append(str(entry[1]))
	for why in reasons:
		for entry in dimmed:
			if str(entry[1]) == why:
				out += "  " + Utils.bb_chip_disabled(str(entry[0]), "", str(why) if Utils.explanations_folded() else "")
		if not Utils.explanations_folded():
			out += " [color=#" + Utils.COLOR_INFO + "]" + why + "[/color]"
	return out


func _admin_why() -> String:
	"""CRT-9 (CQ-21): the reason an administrative chip (a build, a repair,
	a keel) is refused for the turn's actions — read off the payload's
	`action_pools` (the top bar's own figures), "" while one remains."""
	if _map_node == null or not ("action_pools" in _map_node):
		return ""
	var pools = _map_node.action_pools
	if not (pools is Dictionary) or not pools.has("admin"):
		return ""
	if int(pools.get("admin", 1)) <= 0:
		return "no administrative action left this turn"
	return ""


func _region_has_building(data: Dictionary, building_type: String) -> bool:
	var buildings = data.get("buildings", [])
	if not buildings is Array:
		return false
	for b in buildings:
		if b is Dictionary and str(b.get("type", "")) == building_type:
			return true
	var construction = data.get("building_under_construction", null)
	if construction is Dictionary and str(construction.get("type", "")) == building_type:
		return true
	return false


func _build_terms_text(building_key: String, t: Dictionary) -> String:
	# WO slice 8: the delivered terms after the chip — every digit from
	# the backend's build_terms payload (this province's own arithmetic,
	# stability and terrain included), never a constant kept here.
	match building_key:
		"supply_depot":
			return "+" + Utils.format_number(int(t.get("supply", 0))) + " supply · +" \
				+ str(int(t.get("income", 0))) + "g/turn"
		"fortification":
			return "+" + str(int(t.get("defense_pct", 0))) + "% to defenders here"
		"training_ground":
			return "recruits " + str(int(t.get("recruit_morale_base", 0))) + "→" \
				+ str(int(t.get("recruit_morale", 0))) + " morale · drill +" \
				+ str(int(t.get("drill_gain_base", 0))) + "→+" + str(int(t.get("drill_gain", 0)))
		"market":
			# EA-9 (the economy audit, Oct 5 2026): a market keeps itself.
			if int(t.get("upkeep", -1)) == 0:
				return "+" + str(int(t.get("income", 0))) + "g/turn · no upkeep"
			return "+" + str(int(t.get("income", 0))) + "g/turn"
		"stables":
			var cav := int(t.get("cavalry", 0))
			if cav <= 0:
				return "+0 cavalry/turn — the remount cap is already filled"
			return "+" + Utils.format_number(cav) + " cavalry/turn"
	return ""

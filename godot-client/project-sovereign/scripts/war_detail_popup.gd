extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - War Detail Popup (N4b: Layer 2)
# =============================================================================
# Lightweight popup showing war details, coalition overview, or armistice info.
# CanvasLayer 30. Opened from war_status_panel card clicks.
# Includes tug-of-war score meter for visual war score display.
# Emits negotiate_clicked / target_clicked for wizard handoff (Layer 3).
# =============================================================================

signal negotiate_clicked(nation: String)
signal target_clicked(nation: String)
signal settlement_clicked(war_id: String, target_nation: String)
# SC-30 / Slice G1: ask the enemy war leader to name settlement terms.
signal request_terms_clicked(war_id: String, target_nation: String)
signal war_ended(message: String)

@onready var background_overlay = $BackgroundOverlay
@onready var header_label = $PanelContainer/VBoxContainer/HeaderRow/HeaderLabel
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var score_bar_container = $PanelContainer/VBoxContainer/ScoreBarContainer
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var button_row = $PanelContainer/VBoxContainer/ButtonRow

var _current_nation: String = ""
var _current_war_id: String = ""
var _current_mode: String = ""  # "war", "coalition", "armistice"

# Colors
const COLOR_GREEN = "#4a4"
# S12 (UXR3-6): aa4444 read 3.15 : 1 on the popup's panel; the same hue, lighter.
const COLOR_RED = "#c36969"
const COLOR_WHITE = "#c0c0c8"
const COLOR_GOLD = "#d9c08c"
const COLOR_AMBER = "#e0a040"
const COLOR_HEADER = "#B8860B"
# UXR-D2: the dim greys through High contrast (getters, not consts).
var COLOR_DIMMED: String:
	get: return "#" + Utils.COLOR_INFO
var COLOR_INFO: String:
	get: return "#" + Utils.toned_hex("a0a0a8")

# Bar colors — nation tints come from Utils.NATION_COLORS (§3.3).
# UI-2 Part 2: the bar track is shared with war_status_panel via Utils.
const COLOR_BAR_BG = Utils.UI_BAR_BG
const COLOR_BAR_CENTER = Utils.UI_BAR_CENTER_DETAIL
# War-score bar frame (CC0 Kenney RPG track): 9px 3-slice caps + cool-navy tint.
const BAR_FRAME_CAP = 9
const COLOR_BAR_FRAME_TINT = Color(0.72, 0.78, 1.0)
# UXR-X6 (UXR-2, October 12, 2026): the bar's own text — the score and the two
# side tags — is the theme's Caption (14), never a computed size: the tags were
# `max(7, font_size - 3)` = 8 / 7 px and the score 11 / 9, under the readability
# floor on every monitor. A 14-px EB Garamond line is ~19 px tall, so both bars
# (the war's and each coalition member's) are 22 px — the track is a horizontal
# 3-slice and stretches — and a tag slot is wide enough for "WU" at 14.
const WAR_BAR_HEIGHT := 22
const WAR_BAR_TAG_W := 28.0
# UXR-X8: the track is a 3-slice whose rounded gold cap is 14 px wide; a tag
# 3 px in sat under the rim (invisible at 8 px, clipped at 14). Past the cap.
const WAR_BAR_TAG_INSET := 14.0
# UXR-2 (the layout law): ANCHORED beside the war-status panel — its width and
# height fractions of the logical viewport between the authored 330 x 440 and
# a ceiling, docked a gap left of the war HUD's LIVE left edge, centred in the
# band under the top bar, then fitted by `Utils.clamp_anchored_panel` (the
# centre clamp skips an edge-anchored panel, so this was a bare fixed rect
# whose header went under the top bar on a short logical viewport).
const WIDTH_FRACTION := 0.20
const HEIGHT_FRACTION := 0.55
const FIT_MIN_WIDTH := 330.0
const FIT_MAX_WIDTH := 600.0
const FIT_MIN_HEIGHT := 440.0
const FIT_MAX_HEIGHT := 720.0
const DOCK_GAP := 40.0
const AUTHORED_RIGHT := 240.0  # the .tscn's offset_right: beside the authored 192-px HUD
var dock_beside: Control = null


func refit() -> void:
	"""UXR-2: the popup's rect from the viewport — on every show and on the
	live-refit road (`DialogManager.refit_visible`)."""
	var panel: Control = $PanelContainer
	var view := get_viewport().get_visible_rect().size
	var right := AUTHORED_RIGHT
	if dock_beside != null and is_instance_valid(dock_beside) and dock_beside.is_visible_in_tree():
		right = view.x - dock_beside.get_global_rect().position.x + DOCK_GAP
	var w := Utils.fraction_px(view.x, WIDTH_FRACTION, FIT_MIN_WIDTH, FIT_MAX_WIDTH,
			right + Utils.HUD_MARGIN)
	var band_top := Utils.TOP_BAR_HEIGHT + Utils.HUD_MARGIN
	var h := Utils.fraction_px(view.y, HEIGHT_FRACTION, FIT_MIN_HEIGHT, FIT_MAX_HEIGHT,
			band_top + Utils.HUD_MARGIN)
	# The band [band_top, view.y - margin]'s centre, relative to the panel's
	# vertical anchor (0.5).
	var mid := (band_top - Utils.HUD_MARGIN) / 2.0
	panel.offset_right = -right
	panel.offset_left = -right - w
	panel.offset_top = mid - h / 2.0
	panel.offset_bottom = mid + h / 2.0
	Utils.clamp_anchored_panel(panel)
	# The button row is an HFlowContainer: its wrapped height is known only
	# after the containers sort at the new width, so the first pass can
	# under-measure the minimum and the panel grows past the band (measured at
	# 800x450: its header under the top bar). Fit once more after layout.
	_settle_fit.call_deferred()


func _settle_fit() -> void:
	await get_tree().process_frame
	if visible and is_instance_valid($PanelContainer):
		Utils.clamp_anchored_panel($PanelContainer)


func _ready():
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(content_label)
	hide()
	close_button.pressed.connect(_close_popup)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)


func _input(event):
	if visible and event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		_close_popup()
		get_viewport().set_input_as_handled()


func _close_popup():
	hide()


# UI-6: opponent heraldry in the popup header (untinted colored art).
var _header_flag: TextureRect = null

func _set_header_flag(nation: String) -> void:
	if _header_flag == null:
		_header_flag = TextureRect.new()
		_header_flag.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		_header_flag.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		_header_flag.custom_minimum_size = Vector2(24, 16)
		var header_row = header_label.get_parent()
		header_row.add_child(_header_flag)
		header_row.move_child(_header_flag, header_label.get_index())
	var path = Utils.nation_flag_path(nation)
	if path == "":
		_header_flag.visible = false
		return
	_header_flag.texture = load(path)
	_header_flag.visible = true


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		_close_popup()


func show_war(war_data: Dictionary, _coalition_data) -> void:
	"""Show bilateral war detail (N4b)."""
	AudioManager.play("cloth")
	_current_nation = str(war_data.get("opponent", ""))
	var opponent_display = Utils.humanize_nation_keys_in_text(str(war_data.get("opponent_display", Utils.display_nation_name(_current_nation))))
	_current_war_id = str(war_data.get("war_instance_id", ""))
	_current_mode = "war"
	# PC-R7 (i) — ruling J (S13e part 4): the popup is headed by the war's
	# STAKE ("WAR FOR BOHEMIA"); the roster rides the first line of the body.
	var war_title = str(war_data.get("war_title", ""))
	header_label.text = (war_title.to_upper() if war_title != "" else "WAR WITH " + opponent_display.to_upper())
	_set_header_flag(_current_nation)
	_clear_score_bars()
	_add_tug_of_war_bar(
		int(float(war_data.get("war_score", 0))),
		_current_nation, 280, WAR_BAR_HEIGHT
	)
	_render_war_detail(war_data)
	_clear_buttons()
	# PC-F41 (S13e part 4): every peace button names the court it addresses
	# — one Negotiate per court of a shared war (the leader first), never a
	# bare "Negotiate Peace" that opened the leader at 1 % of the war.
	var courts = war_data.get("opponents", [])
	if not (courts is Array) or courts.is_empty():
		courts = [_current_nation]
	for court in courts:
		_add_negotiate_button(str(court))
	if bool(war_data.get("settlement_available", false)):
		_add_settlement_button(_current_war_id, _current_nation, "Open Settlement")
	elif str(war_data.get("settlement_tier_display", "")) != "" and str(war_data.get("settlement_disabled_reason_display", "")) != "":
		# FA-D15 (slice 17, Phase 2): the Request Terms idiom — a settlement-tier
		# war whose review is unavailable renders the button DISABLED with the
		# reason in the tooltip, instead of vanishing.
		_add_disabled_settlement_button(str(war_data.get("settlement_disabled_reason_display", "")))
	# SC-30 / Slice G1: Request Terms — absent state never renders (the
	# no-false-affordance rule); disabled renders ONLY for deterministic
	# temporal reasons, with the pre-click clock in the tooltip (G4F-16).
	var rt_state = war_data.get("request_terms_state", {})
	if rt_state is Dictionary and str(rt_state.get("state", "absent")) != "absent":
		_add_request_terms_button(_current_war_id, _current_nation, rt_state)
	show()
	refit()


func show_coalition(coalition_data: Dictionary, wars: Array) -> void:
	"""Show coalition overview detail (N4b coalition variant)."""
	AudioManager.play("cloth")
	_current_nation = str(coalition_data.get("leader", ""))
	_current_mode = "coalition"
	header_label.text = str(coalition_data.get("name", "COALITION")).to_upper()
	_set_header_flag("")
	_clear_score_bars()
	# Add a tug-of-war bar per coalition member
	for w in _coalition_member_rows(wars):
		if w.get("in_coalition", false):
			var opp = str(w.get("opponent", "?"))
			var score = int(float(w.get("war_score", 0)))
			_add_labeled_tug_of_war_bar(opp, score, 280, WAR_BAR_HEIGHT)
	_render_coalition_detail(coalition_data, wars)
	_clear_buttons()
	var shared_war_id = _shared_coalition_war_id(wars)
	if shared_war_id != "":
		_add_settlement_button(shared_war_id, _current_nation, "Open Whole-War Settlement")
	else:
		_add_coalition_settlement_explainer()
	# Add Target buttons for non-leader coalition members
	for w in _coalition_member_rows(wars):
		if w.get("in_coalition", false) and not w.get("is_coalition_leader", false):
			_add_target_button(str(w.get("opponent", "")))
	show()
	refit()


func show_armistice(war_data: Dictionary) -> void:
	"""Show armistice detail (N4b armistice variant)."""
	AudioManager.play("cloth")
	_current_nation = str(war_data.get("opponent", ""))
	_current_mode = "armistice"
	# PC-R7 (i) (S13e part 4): the truce is a pause in a war that keeps its title.
	var truce_title = str(war_data.get("war_title", ""))
	header_label.text = ((truce_title.to_upper() + " — ARMISTICE WITH ") if truce_title != "" else "ARMISTICE WITH ") + Utils.display_nation_name(_current_nation).to_upper()
	_set_header_flag(_current_nation)
	_clear_score_bars()
	_render_armistice_detail(war_data)
	_clear_buttons()
	_add_diplomatic_options_button(_current_nation)
	show()
	refit()


func refresh_if_open(active_wars_data: Dictionary) -> void:
	"""Refresh data in-place if popup is open (N4d: don't close mid-read).

	When `_current_war_id` is known (war card opened with a specific
	war_instance_id), match BOTH nation and war_instance_id so that
	multiple wars vs the same nation across different war_instances
	cannot silently swap the popup's data."""
	if not visible:
		return

	var wars = active_wars_data.get("wars", [])
	var coalition_data = active_wars_data.get("coalition", null)

	if _current_mode == "coalition" and coalition_data != null:
		show_coalition(coalition_data, wars)
		return

	# Find the war data for current nation. Prefer a war_instance_id
	# match when one was captured at show_war(); fall back to nation-only
	# only if no war_instance_id was captured (legacy entry points).
	var found = false
	var matched: Variant = null
	if _current_war_id != "":
		for w in wars:
			if str(w.get("opponent", "")) == _current_nation and str(w.get("war_instance_id", "")) == _current_war_id:
				matched = w
				found = true
				break
	if not found:
		for w in wars:
			if str(w.get("opponent", "")) == _current_nation:
				matched = w
				found = true
				break
	if matched != null:
		if _current_mode == "war" and str(matched.get("status", "")) == "war":
			show_war(matched, coalition_data)
		elif _current_mode == "armistice" and str(matched.get("status", "")) == "armistice":
			show_armistice(matched)
		elif str(matched.get("status", "")) == "armistice":
			# War ended, now armistice
			show_armistice(matched)

	if not found:
		# War ended entirely — notify before closing (Fix 10)
		war_ended.emit("The war with " + Utils.display_nation_name(_current_nation) + " has ended.")
		_close_popup()


# ── SCORE BAR ──

func _clear_score_bars():
	for child in score_bar_container.get_children():
		score_bar_container.remove_child(child)
		child.queue_free()


func _add_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int):
	"""Add a large tug-of-war bar to the score bar container."""
	var bar = _create_tug_of_war_bar(score, opponent, bar_width, bar_height)
	score_bar_container.add_child(bar)


func _add_labeled_tug_of_war_bar(opponent: String, score: int, bar_width: int, bar_height: int):
	"""Add a labeled tug-of-war bar (nation name + bar) for coalition view."""
	var row = HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)

	var lbl = Label.new()
	lbl.text = Utils.display_nation_name(opponent)
	lbl.custom_minimum_size = Vector2(60, 0)
	lbl.theme_type_variation = &"Caption"
	var score_color_val = Utils.UI_SCORE_POSITIVE if score > 0 else (Utils.UI_SCORE_NEGATIVE if score < 0 else Utils.UI_SCORE_NEUTRAL)
	lbl.add_theme_color_override("font_color", score_color_val)
	row.add_child(lbl)

	var bar = _create_tug_of_war_bar(score, opponent, bar_width, bar_height)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(bar)

	score_bar_container.add_child(row)


# UXR3-F1: the score label's clearance from the 2-px centre tick.
const SCORE_TICK_CLEAR := 5.0


func _create_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int) -> Control:
	"""Create a two-tone tug-of-war bar. Blue=France (right), Red=enemy (left).
	Center = 0. Score > 0 means France winning (blue fills right of center).
	Score < 0 means enemy winning (red fills left of center)."""
	var container = Control.new()
	container.custom_minimum_size = Vector2(bar_width, bar_height)

	# Gold-rimmed recessed track (assets/ui/bars/warbar_track.png, 3-slice).
	# Matches the HUD bar. load() so a missing texture degrades gracefully.
	var track = NinePatchRect.new()
	track.texture = load("res://assets/ui/bars/warbar_track.png")
	track.patch_margin_left = 14
	track.patch_margin_right = 14
	track.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	container.add_child(track)

	var enemy_color: Color = Utils.NATION_COLORS.get(opponent, Utils.COLOR_ENEMY_DEFAULT)
	var france_color: Color = Utils.NATION_COLORS["France"]

	# Glossy fill from centre, tinted to the leader's nation via modulate.
	var normalized = clamp(score, -100, 100)
	if normalized != 0:
		var fill = TextureRect.new()
		fill.texture = load("res://assets/ui/bars/warbar_fill.png")
		fill.stretch_mode = TextureRect.STRETCH_SCALE
		# EXPAND_IGNORE_SIZE is load-bearing: without it the texture's natural
		# 72x22 px becomes the control's MINIMUM size, so any anchored span
		# smaller than that (short bars, high UI scale, low scores) overflows
		# past the centre and bulges out of the track.
		fill.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		var fraction: float = abs(normalized) / 100.0
		# Outer edge tucks inside the track's gold rim cap proportionally
		# (mirrors war_status_panel.BAR_RIM_INSET).
		var rim_inset: float = 5.0 * fraction
		if normalized > 0:
			fill.modulate = france_color
			_anchor_bar_child(fill, 0.5, 0.5 + fraction * 0.5, 0.0, -rim_inset)
		else:
			fill.modulate = enemy_color
			_anchor_bar_child(fill, 0.5 - fraction * 0.5, 0.5, rim_inset, 0.0)
		fill.offset_top = 3.0
		fill.offset_bottom = -3.0
		container.add_child(fill)

	# Slim gold centre tick — the balance point. The HUD bar marks it with the
	# gem; here the score label owns the centre, so a 2px tick keeps the
	# fill direction readable without fighting the text.
	var tick = ColorRect.new()
	tick.name = "CentreTick"
	tick.color = Color(0.85, 0.7, 0.3, 0.75)
	_anchor_bar_child(tick, 0.5, 0.5, -1.0, 1.0)
	tick.offset_top = 2.0
	tick.offset_bottom = -2.0
	tick.add_to_group("bar_ticks")
	container.add_child(tick)

	# Score label. Slice 7.5 review fold: dark outline keeps the score
	# readable over light nation fills (e.g. PapalStates white) at high scores.
	# UXR3-F1 (Pre-Deploy S12 part 2): the label stands on the LEADER's side
	# of the tick, never across it — centred, the tick drew over the minus of
	# a losing score and −60 read "60" beside a red fill. A true minus sign.
	var score_label = Label.new()
	score_label.name = "ScoreLabel"
	var score_sign = "+" if score > 0 else ("\u2212" if score < 0 else "")
	score_label.text = score_sign + str(absi(score))
	score_label.theme_type_variation = &"Caption"
	score_label.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))
	score_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	score_label.add_theme_constant_override("outline_size", 3)
	score_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	if score < 0:
		score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		_anchor_bar_child(score_label, 0.0, 0.5, WAR_BAR_TAG_INSET + WAR_BAR_TAG_W, -SCORE_TICK_CLEAR)
	else:
		score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		_anchor_bar_child(score_label, 0.5, 1.0, SCORE_TICK_CLEAR, -(WAR_BAR_TAG_INSET + WAR_BAR_TAG_W))
	container.add_child(score_label)

	# Side labels (Enemy on LEFT, France on RIGHT — matches fill direction)
	var enemy_lbl = Label.new()
	var abbr = opponent.left(2).to_upper() if opponent.length() >= 2 else opponent.to_upper()
	enemy_lbl.text = abbr
	enemy_lbl.theme_type_variation = &"Caption"
	# S12 (UXR3-5, 6): the side tags at 60 % alpha read 2.45 : 1; full alpha (4.19).
	enemy_lbl.add_theme_color_override("font_color", Color(0.8, 0.5, 0.5, 1.0))
	# Pinned to the LEFT edge (enemy side) so it tracks the stretched width.
	_anchor_bar_child(enemy_lbl, 0.0, 0.0, WAR_BAR_TAG_INSET, WAR_BAR_TAG_INSET + WAR_BAR_TAG_W)
	enemy_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	container.add_child(enemy_lbl)

	var france_lbl = Label.new()
	france_lbl.text = "FR"
	france_lbl.theme_type_variation = &"Caption"
	france_lbl.add_theme_color_override("font_color", Color(0.5, 0.6, 0.8, 1.0))
	# Pinned to the RIGHT edge (France side), right-aligned.
	_anchor_bar_child(france_lbl, 1.0, 1.0, -WAR_BAR_TAG_INSET - WAR_BAR_TAG_W, -WAR_BAR_TAG_INSET)
	france_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	france_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	container.add_child(france_lbl)

	return container


static func _anchor_bar_child(node: Control, a_left: float, a_right: float, o_left: float, o_right: float) -> void:
	# Anchor a tug-of-war bar child horizontally to fractions of the container's
	# ACTUAL width (full height), so it resizes with a SIZE_EXPAND_FILL bar.
	node.anchor_left = a_left
	node.anchor_right = a_right
	node.anchor_top = 0.0
	node.anchor_bottom = 1.0
	node.offset_left = o_left
	node.offset_right = o_right
	node.offset_top = 0.0
	node.offset_bottom = 0.0


# ── RENDERING ──

func _render_war_detail(w: Dictionary):
	var trend = str(w.get("trend", "stable"))
	var duration = int(float(w.get("duration", 0)))
	var started = int(float(w.get("started_turn", 0)))
	var we = w.get("war_exhaustion", null)
	var breakdown = w.get("breakdown", null)

	var bbcode = ""

	# R159 (POSITION 7): each core screen names the mechanic it displays.
	bbcode += "[color=#" + Utils.COLOR_INFO + "]The ledger of one war — its score, its fronts, and the price of peace. Negotiate ends it.[/color]\n\n"
	# PC-R7 (i): the stake named, then who (the header carries the title).
	var title_line = str(w.get("war_title_line", ""))
	if title_line != "":
		bbcode += Utils.humanize_nation_keys_in_text(title_line) + "\n"
		var roster = str(w.get("war_roster_display", w.get("opponent_display", "")))
		if roster != "":
			bbcode += "With: " + Utils.humanize_nation_keys_in_text(roster) + "\n"
		bbcode += "\n"

	# Breakdown
	if breakdown != null and breakdown is Dictionary:
		bbcode += "[color=" + COLOR_HEADER + "]Score Breakdown[/color]"
		# PC-F84 (S13e part 3): the trend, drawn — it was computed on every
		# row and printed by no surface.
		bbcode += "   trend " + _trend_str(trend) + " " + trend + "\n"
		# PC-R6 (ruling G, S13e part 3): each component's FILL against its
		# cap — "Battles +15/15 — full" — read off the backend's
		# `breakdown_fill` (one source); the old fixed rows are the fallback
		# for an older payload. Blockade and Captive still render only when
		# nonzero (most wars are land wars; the row earns its place).
		var fill = w.get("breakdown_fill", null)
		if fill is Array and not fill.is_empty():
			for f in fill:
				if not (f is Dictionary):
					continue
				var key = str(f.get("key", ""))
				var value = int(float(f.get("value", 0)))
				if (key == "blockade" or key == "captive") and value == 0:
					continue
				var label = str(f.get("label", key.capitalize()))
				var line = "  " + (label + ":").rpad(12) + _signed(value) + "/" + str(int(float(f.get("cap", 0))))
				if bool(f.get("full", false)):
					line += "  [color=" + COLOR_GOLD + "]— full[/color]"
				bbcode += line + "\n"
			bbcode += "\n"
		else:
			bbcode += "  Territory:  " + _signed(int(breakdown.get("territory", 0))) + "\n"
			bbcode += "  Battles:    " + _signed(int(breakdown.get("battles", 0))) + "\n"
			bbcode += "  Decisive:   " + _signed(int(breakdown.get("decisive", 0))) + "\n"
			bbcode += "  Capital:    " + _signed(int(breakdown.get("capital", 0))) + "\n"
			# PT-J2: the war's memory — provinces taken this war (even if
			# retaken) and the blood differential. Shown = applied.
			bbcode += "  Campaign:   " + _signed(int(breakdown.get("campaign", 0))) + "\n"
			bbcode += "  Blood:      " + _signed(int(breakdown.get("blood", 0))) + "\n"
			# HC-1: the silver blockade — rendered only when nonzero (most
			# wars are land wars; the row earns its place by having a value).
			var _blockade = int(breakdown.get("blockade", 0))
			if _blockade != 0:
				bbcode += "  Blockade:   " + _signed(_blockade) + "\n"
			# NP-4: the Captive Eagle — a sovereign in an enemy cell weighs on
			# the score. Render-when-nonzero, the blockade row's idiom.
			var _captive = int(breakdown.get("captive", 0))
			if _captive != 0:
				bbcode += "  Captive:    " + _signed(_captive) + "\n"
			bbcode += "  Ticking:    " + _signed(int(breakdown.get("ticking", 0))) + "\n\n"

	var tier_display = str(w.get("settlement_tier_display", ""))
	if tier_display:
		# IQ-2 (Sept 14, 2026): the tier rendered in gold — a prize — on a war
		# France was losing to one province. When the backend says the table
		# is the enemy's, it says whose, in this popup's loss colour.
		if str(w.get("settlement_tier_side", "")) == "theirs":
			bbcode += "Settlement Tier (theirs to impose): [color=" + COLOR_RED + "]" + tier_display + "[/color]\n"
		else:
			bbcode += "Settlement Tier: [color=" + COLOR_GOLD + "]" + tier_display + "[/color]\n"
	# PC-F33 (S13e part 4): a white peace confirms every holding — say so
	# beside the tier.
	var held_line = str(w.get("held_line", ""))
	if held_line != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + Utils.humanize_nation_keys_in_text(held_line) + "[/color]\n"
	# PC-F3 (Oct 15, 2026): the tier above is the peace table's, not the
	# score bar's — say the table's number, each court against 50, and
	# (mid-turn) that this turn's fighting counts from next turn.
	var peace_table = w.get("peace_table", null)
	if peace_table is Dictionary:
		for ln in peace_table.get("lines", []):
			bbcode += "[color=#" + Utils.COLOR_INFO + "]" + str(ln) + "[/color]\n"

	# PF-2 (D4/UX-1): make the Back Out "Settlement draft kept" promise
	# visible where the player reopens — the badge appears iff a same-turn
	# scoped draft would actually restore.
	if bool(w.get("settlement_draft_kept", false)):
		bbcode += "[color=" + COLOR_GOLD + "]▸ Draft kept — Open Settlement resumes your terms.[/color]\n"

	var objective = w.get("objective", null)
	if objective != null and objective is Dictionary:
		var obj_type = str(objective.get("type_display", "Objective"))
		# LV-8 (row EP F1): one sentence, not the 28-name homeland list.
		var target_text = Utils.objective_targets_text(objective, "target pending")
		var accumulated = int(float(objective.get("accumulated_ticking", 0)))
		var rate = int(float(objective.get("ticking_rate", 0)))
		var active = "active" if bool(objective.get("ticking_active", false)) else "not ticking"
		bbcode += "Objective: [color=" + COLOR_GOLD + "]" + obj_type + "[/color] - " + target_text
		# FA-D2 (slice 17, Phase 2): a coalition row's objective names the court it targets.
		var against = str(objective.get("against", ""))
		if against != "" and bool(w.get("is_multi_participant_war", false)):
			bbcode += " (against " + Utils.display_nation_name(against) + ")"
		bbcode += " (" + active + ", +" + str(accumulated)
		# FA-S17-19 (Phase 4): a rate printed beside "not ticking" read as a
		# contradiction — "(not ticking, +0, +1/turn)" on the boot board,
		# where a defence objective ticks only for homeland LOST. State the
		# rate when it is running; state what WOULD start it when it is not.
		if rate > 0 and bool(objective.get("ticking_active", false)):
			bbcode += ", +" + str(rate) + "/turn"
		bbcode += ")"
		if rate > 0 and not bool(objective.get("ticking_active", false)):
			bbcode += " — +" + str(rate) + "/turn once it begins"
		bbcode += "\n"

	# FA-D4 (slice 17, Phase 2): the verb that sets a war purpose had no UI home.
	var objective_hint = str(w.get("objective_hint", ""))
	if objective_hint != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + objective_hint + "[/color]\n"
	var enemy_objective = w.get("enemy_objective", null)
	if enemy_objective != null and enemy_objective is Dictionary:
		bbcode += "Enemy Objective: " + str(enemy_objective.get("type_display", "Objective")) + "\n"

	# FA-D10 (slice 17, Phase 2): who is carrying the coalition war — the rows
	# the HUD tooltip alone used to show, from the ONE shared formatter.
	for ln in Utils.standing_lines(w):
		bbcode += ln + "\n"

	# Duration
	bbcode += "Duration: " + str(duration) + " turns (since Turn " + str(started) + ")\n"

	# AI-6c (§4.6): a war's reason is shown wherever the war appears —
	# the Stage D stamp (an AI-declared war names the design it fights
	# for; blank rows render nothing).
	var stated_reason = str(w.get("stated_reason", ""))
	if stated_reason != "":
		bbcode += "Casus belli: " + stated_reason + "\n"

	# War exhaustion
	if we != null:
		var we_int = int(float(we))
		var we_color = COLOR_WHITE
		if we_int >= 80:
			we_color = COLOR_RED
		elif we_int >= 40:
			we_color = COLOR_AMBER
		bbcode += "Enemy War Exhaustion: [color=" + we_color + "]" + str(we_int) + "[/color]\n"
		# PC-R5 / PC-F42 (S13e part 3): what the clock is made of — the
		# backend writes the sentence (`exhaustion_terms.lines`); diplomacy
		# carries no fog, so the figure above is never "Unknown" now.
		var ex_terms = w.get("exhaustion_terms", null)
		if ex_terms is Dictionary:
			for ln in ex_terms.get("lines", []):
				bbcode += "[color=#" + Utils.COLOR_INFO + "]" + Utils.humanize_nation_keys_in_text(str(ln)) + "[/color]\n"
	else:
		# FA-70 (slice 17): this `else` belongs to `if we != null` — NV-12
		# inserted the fleet block between the two, so a fleetless court with
		# known exhaustion printed BOTH a figure and "Unknown", and a fogged
		# fleet-holder (Britain, the boot's only war row) printed neither.
		bbcode += "Enemy War Exhaustion: [color=" + COLOR_DIMMED + "]Unknown[/color]\n"

	# NV-12 (recon gap 8): the per-belligerent fleet line — built by
	# war_status.py since NV-0 (counts/postures are ruled PUBLIC) and
	# consumed by NOTHING until now. Standalone: no else (FA-70).
	var naval_line = str(w.get("naval_line", ""))
	if naval_line != "":
		bbcode += "Their fleet: " + Utils.humanize_nation_keys_in_text(naval_line) + "\n"

	# Recent battles
	var recent = w.get("recent_battles", [])
	if recent.size() > 0:
		bbcode += "\n[color=" + COLOR_HEADER + "]Recent Battles[/color]\n"
		for b in recent:
			var prefix = ""
			if b.get("decisive", false):
				prefix = "[color=" + COLOR_GOLD + "]* [/color]"
			var outcome = "Victory" if b.get("won", false) else "Defeat"
			var outcome_color = COLOR_GREEN if b.get("won", false) else COLOR_RED
			bbcode += "  " + prefix + "[color=" + outcome_color + "]" + outcome + "[/color] at " + str(b.get("location", "?")) + " (T:" + str(int(b.get("turn", 0))) + ")\n"


	# PC-R3 (S13e part 2): the tier the court's next letter would dictate,
	# and the peace the Emperor refused (both from the backend's reading).
	var next_letter = w.get("next_letter", null)
	if next_letter is Dictionary and str(next_letter.get("display", "")) != "":
		bbcode += "\n[color=" + COLOR_AMBER + "]" + str(next_letter.get("display", "")) + "[/color]\n"
	var refused_peace = str(w.get("refused_peace", ""))
	if refused_peace != "" and refused_peace != "null":
		bbcode += "[color=" + COLOR_AMBER + "]" + refused_peace + "[/color]\n"
	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)


func _render_coalition_detail(coalition_data: Dictionary, wars: Array):
	var leader = str(coalition_data.get("leader", ""))
	var posture = str(coalition_data.get("posture", "defensive")).capitalize()

	var bbcode = ""
	bbcode += "Leader: [color=" + COLOR_GOLD + "]" + Utils.display_nation_name(leader) + "[/color]   Posture: " + posture + "\n\n"

	# Members (text summary — bars are in score_bar_container above)
	for w in _coalition_member_rows(wars):
		if not w.get("in_coalition", false):
			continue
		var opp_name = str(w.get("opponent", "?"))
		var we = w.get("war_exhaustion", null)
		var army = str(w.get("army_strength", "Unknown"))
		var line = Utils.display_nation_name(opp_name)
		if we != null:
			line += "  WE:" + str(int(float(we)))
		line += "  " + army
		if opp_name == leader:
			# UXR3-13 (Pre-Deploy S12): an underline read as a link and the row
			# is no control; the leader is marked in words.
			line = "[b]" + line + "[/b]  [color=" + COLOR_GOLD + "]— leads the coalition[/color]"
		bbcode += "  " + line + "\n"

	# Coordination
	var coordination = coalition_data.get("coordination", [])
	if coordination.size() > 0:
		bbcode += "\n[color=" + COLOR_HEADER + "]Coordination[/color]\n"
		for c in coordination:
			var quality = str(c.get("quality", "?"))
			var q_color = COLOR_GREEN if quality == "Good" else (COLOR_AMBER if quality == "Strained" else COLOR_RED)
			bbcode += "  " + Utils.display_nation_name(str(c.get("nation_a", ""))) + "-" + Utils.display_nation_name(str(c.get("nation_b", ""))) + ": [color=" + q_color + "]" + quality + "[/color]\n"

	# Weak link
	var weak_link = coalition_data.get("weak_link", null)
	if weak_link != null:
		bbcode += "\n[color=" + COLOR_AMBER + "]Weak link: " + Utils.display_nation_name(str(weak_link)) + " (highest WE)[/color]\n"

	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)


func _render_armistice_detail(w: Dictionary):
	var remaining = int(float(w.get("armistice_remaining", 0)))
	var relation = int(float(w.get("relation", 0)))
	var rel_desc = str(w.get("relation_descriptor", "?"))
	var rel_trend = str(w.get("relation_trend", "stable"))

	var bbcode = ""
	bbcode += "Status: [color=" + COLOR_DIMMED + "]Armistice (" + str(remaining) + " turns remaining)[/color]\n"

	var rel_color = COLOR_GREEN if relation > 0 else (COLOR_RED if relation < 0 else COLOR_WHITE)
	var rel_sign = "+" if relation > 0 else ""
	bbcode += "Relations: [color=" + rel_color + "]" + rel_sign + str(relation) + " (" + rel_desc + ")[/color]\n"
	bbcode += "Trend: " + _trend_str(rel_trend) + "\n"

	# PC-R2 / PC-F44 (S13e part 2): the ONE wording from the backend
	# (`diplomacy.truce_words` — what the truce keeps, where it heads, the
	# hope terms, the sureties, the cure priced) — the client composed its
	# own "On course to collapse" sentence before.
	var exit_kind = str(w.get("armistice_exit", w.get("armistice_projected_outcome", "")))
	var line_color = COLOR_GREEN if (exit_kind == "peace" or exit_kind == "dictated") else COLOR_AMBER
	var truce_lines = w.get("armistice_lines", [])
	if truce_lines is Array and not truce_lines.is_empty():
		for line in truce_lines:
			bbcode += "[color=" + line_color + "]" + str(line) + "[/color]\n"
	else:
		# G4F-17: the fork alone (a save from before the words)
		var projected = str(w.get("armistice_projected_outcome", ""))
		if projected != "":
			var threshold = int(float(w.get("armistice_auto_peace_threshold", -60)))
			if projected == "peace":
				bbcode += "[color=" + COLOR_GREEN + "]On course for peace: relations have healed past " + str(threshold) + ".[/color]\n"
			else:
				bbcode += "[color=" + COLOR_AMBER + "]On course to collapse: unless relations heal to " + str(threshold) + " or better, the war resumes at expiry.[/color]\n"

	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)


# ── BUTTONS ──

func _clear_buttons():
	for child in button_row.get_children():
		button_row.remove_child(child)
		child.queue_free()


func _add_negotiate_button(nation: String):
	var btn = Button.new()
	# PC-F41: the button names the court it addresses.
	btn.text = "Negotiate with " + Utils.display_nation_name(nation)
	btn.tooltip_text = "Open bilateral peace options with " + Utils.display_nation_name(nation) + " only."
	btn.custom_minimum_size = Vector2(160, 36)
	btn.theme_type_variation = &"CaptionButton"
	btn.pressed.connect(func():
		hide()
		negotiate_clicked.emit(nation)
	)
	button_row.add_child(btn)


func _add_settlement_button(war_id: String, nation: String, label: String):
	var btn = Button.new()
	btn.text = label
	btn.tooltip_text = "Open a war-wide settlement review."
	btn.custom_minimum_size = Vector2(190, 36)
	btn.theme_type_variation = &"CaptionButton"
	btn.pressed.connect(func():
		hide()
		settlement_clicked.emit(war_id, nation)
	)
	button_row.add_child(btn)


func _add_disabled_settlement_button(reason: String):
	var btn = Button.new()
	btn.text = "Open Settlement"
	btn.custom_minimum_size = Vector2(190, 36)
	btn.theme_type_variation = &"CaptionButton"
	btn.disabled = true
	btn.tooltip_text = reason
	button_row.add_child(btn)


func _add_request_terms_button(war_id: String, nation: String, rt_state: Dictionary):
	var btn = Button.new()
	btn.text = "Request Terms"
	btn.custom_minimum_size = Vector2(150, 36)
	btn.theme_type_variation = &"CaptionButton"
	if str(rt_state.get("state", "")) == "available":
		btn.tooltip_text = "Ask the enemy war leader to name settlement terms."
		btn.pressed.connect(func():
			hide()
			request_terms_clicked.emit(war_id, nation)
		)
	else:
		btn.disabled = true
		btn.tooltip_text = str(rt_state.get("reason_display", "Unavailable now."))
	button_row.add_child(btn)


func _add_target_button(nation: String):
	var btn = Button.new()
	btn.text = "Target " + Utils.display_nation_name(nation)
	btn.tooltip_text = "Open diplomatic options for this coalition member; this is not a settlement action."
	btn.custom_minimum_size = Vector2(130, 36)
	btn.theme_type_variation = &"CaptionButton"
	btn.pressed.connect(func():
		hide()
		target_clicked.emit(nation)
	)
	button_row.add_child(btn)


func _add_coalition_settlement_explainer():
	var lbl = Label.new()
	lbl.text = "Coalition spans multiple wars; settle each separately."
	lbl.tooltip_text = "Open an individual war detail to prepare a settlement for that war."
	lbl.custom_minimum_size = Vector2(250, 36)
	lbl.theme_type_variation = &"Caption"
	lbl.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	button_row.add_child(lbl)


func _add_diplomatic_options_button(nation: String):
	var btn = Button.new()
	btn.text = "Diplomatic Options"
	btn.custom_minimum_size = Vector2(160, 36)
	btn.theme_type_variation = &"CaptionButton"
	btn.pressed.connect(func():
		hide()
		negotiate_clicked.emit(nation)
	)
	button_row.add_child(btn)


func _coalition_member_rows(wars: Array) -> Array:
	# FA-N75 (slice 11): CA8-D2 folds the three bilateral fronts of one
	# coalition war into a single HUD row, and every block on this card
	# iterates that list — so the card showed ONE strength bar, ONE member
	# line and ZERO Target buttons for a three-power coalition. The backend
	# now carries the folded pair rows on the collapsed row; unfold them
	# here. A row without them is its own member, so a bilateral war and the
	# legacy world are unchanged.
	var out: Array = []
	for w in wars:
		var folded = w.get("coalition_member_rows", null)
		if folded != null and folded is Array and folded.size() > 0:
			for row in folded:
				out.append(row)
		else:
			out.append(w)
	return out


func _shared_coalition_war_id(wars: Array) -> String:
	var shared := ""
	for w in wars:
		if not w.get("in_coalition", false) or str(w.get("status", "")) != "war":
			continue
		var wid = str(w.get("war_instance_id", ""))
		if wid == "":
			return ""
		if shared == "":
			shared = wid
		elif shared != wid:
			return ""
	return shared


# ── HELPERS ──

func _trend_str(trend: String) -> String:
	match trend:
		"rising":
			return "[color=" + COLOR_GREEN + "]^[/color]"
		"falling":
			return "[color=" + COLOR_RED + "]v[/color]"
		_:
			return "[color=" + COLOR_WHITE + "]=[/color]"


func _signed(val: int) -> String:
	if val > 0:
		return "+" + str(val)
	return str(val)

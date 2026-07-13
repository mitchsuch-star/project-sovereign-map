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
const COLOR_RED = "#a44"
const COLOR_WHITE = "#c0c0c8"
const COLOR_GOLD = "#d9c08c"
const COLOR_AMBER = "#e0a040"
const COLOR_HEADER = "#B8860B"
const COLOR_DIMMED = "#808080"
const COLOR_INFO = "#a0a0a8"

# Bar colors — nation tints come from Utils.NATION_COLORS (§3.3).
# UI-2 Part 2: the bar track is shared with war_status_panel via Utils.
const COLOR_BAR_BG = Utils.UI_BAR_BG
const COLOR_BAR_CENTER = Color(0.4, 0.4, 0.45, 0.6)
# War-score bar frame (CC0 Kenney RPG track): 9px 3-slice caps + cool-navy tint.
const BAR_FRAME_CAP = 9
const COLOR_BAR_FRAME_TINT = Color(0.72, 0.78, 1.0)


func _ready():
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


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		_close_popup()


func show_war(war_data: Dictionary, _coalition_data) -> void:
	"""Show bilateral war detail (N4b)."""
	_current_nation = str(war_data.get("opponent", ""))
	var opponent_display = Utils.humanize_nation_keys_in_text(str(war_data.get("opponent_display", Utils.display_nation_name(_current_nation))))
	_current_war_id = str(war_data.get("war_instance_id", ""))
	_current_mode = "war"
	header_label.text = "WAR WITH " + opponent_display.to_upper()
	_clear_score_bars()
	_add_tug_of_war_bar(
		int(float(war_data.get("war_score", 0))),
		_current_nation, 280, 16
	)
	_render_war_detail(war_data)
	_clear_buttons()
	_add_negotiate_button(_current_nation)
	if bool(war_data.get("settlement_available", false)):
		_add_settlement_button(_current_war_id, _current_nation, "Open Settlement")
	# SC-30 / Slice G1: Request Terms — absent state never renders (the
	# no-false-affordance rule); disabled renders ONLY for deterministic
	# temporal reasons, with the pre-click clock in the tooltip (G4F-16).
	var rt_state = war_data.get("request_terms_state", {})
	if rt_state is Dictionary and str(rt_state.get("state", "absent")) != "absent":
		_add_request_terms_button(_current_war_id, _current_nation, rt_state)
	show()


func show_coalition(coalition_data: Dictionary, wars: Array) -> void:
	"""Show coalition overview detail (N4b coalition variant)."""
	_current_nation = str(coalition_data.get("leader", ""))
	_current_mode = "coalition"
	header_label.text = str(coalition_data.get("name", "COALITION")).to_upper()
	_clear_score_bars()
	# Add a tug-of-war bar per coalition member
	for w in wars:
		if w.get("in_coalition", false):
			var opp = str(w.get("opponent", "?"))
			var score = int(float(w.get("war_score", 0)))
			_add_labeled_tug_of_war_bar(opp, score, 280, 12)
	_render_coalition_detail(coalition_data, wars)
	_clear_buttons()
	var shared_war_id = _shared_coalition_war_id(wars)
	if shared_war_id != "":
		_add_settlement_button(shared_war_id, _current_nation, "Open Whole-War Settlement")
	else:
		_add_coalition_settlement_explainer()
	# Add Target buttons for non-leader coalition members
	for w in wars:
		if w.get("in_coalition", false) and not w.get("is_coalition_leader", false):
			_add_target_button(str(w.get("opponent", "")))
	show()


func show_armistice(war_data: Dictionary) -> void:
	"""Show armistice detail (N4b armistice variant)."""
	_current_nation = str(war_data.get("opponent", ""))
	_current_mode = "armistice"
	header_label.text = "ARMISTICE WITH " + Utils.display_nation_name(_current_nation).to_upper()
	_clear_score_bars()
	_render_armistice_detail(war_data)
	_clear_buttons()
	_add_diplomatic_options_button(_current_nation)
	show()


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
	var bar = _create_tug_of_war_bar(score, opponent, bar_width, bar_height, 11)
	score_bar_container.add_child(bar)


func _add_labeled_tug_of_war_bar(opponent: String, score: int, bar_width: int, bar_height: int):
	"""Add a labeled tug-of-war bar (nation name + bar) for coalition view."""
	var row = HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)

	var lbl = Label.new()
	lbl.text = Utils.display_nation_name(opponent)
	lbl.custom_minimum_size = Vector2(60, 0)
	lbl.add_theme_font_size_override("font_size", 10)
	var score_color_val = Utils.UI_SCORE_POSITIVE if score > 0 else (Utils.UI_SCORE_NEGATIVE if score < 0 else Utils.UI_SCORE_NEUTRAL)
	lbl.add_theme_color_override("font_color", score_color_val)
	row.add_child(lbl)

	var bar = _create_tug_of_war_bar(score, opponent, bar_width, bar_height, 9)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(bar)

	score_bar_container.add_child(row)


func _create_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int, font_size: int) -> Control:
	"""Create a two-tone tug-of-war bar. Blue=France (right), Red=enemy (left).
	Center = 0. Score > 0 means France winning (blue fills right of center).
	Score < 0 means enemy winning (red fills left of center)."""
	var container = Control.new()
	container.custom_minimum_size = Vector2(bar_width, bar_height)

	# Background — a recessed bar FRAME (CC0 Kenney RPG track, assets/ui/bars/
	# bar_frame.png), cool-navy tinted, so the tug-of-war sits in a real bar track
	# with rounded ends instead of a flat rectangle. load() (not preload) so a
	# missing texture degrades to an empty NinePatch rather than a parse failure.
	var bg = NinePatchRect.new()
	bg.texture = load("res://assets/ui/bars/bar_frame.png")
	bg.patch_margin_left = BAR_FRAME_CAP
	bg.patch_margin_right = BAR_FRAME_CAP
	bg.modulate = COLOR_BAR_FRAME_TINT
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	container.add_child(bg)

	# Center line. Anchored to the container's TRUE horizontal center so it tracks
	# the actual (stretched) width — coalition rows add this bar with
	# SIZE_EXPAND_FILL, so a fixed bar_width/2 coordinate bunched the whole
	# tug-of-war into the left `bar_width` px of a wider bar (UI bar-fill fix).
	var center_line = ColorRect.new()
	center_line.color = COLOR_BAR_CENTER
	_anchor_bar_child(center_line, 0.5, 0.5, -1.0, 0.0)
	container.add_child(center_line)

	# Score fill — anchored fractions of the ACTUAL width, measured from center.
	var normalized = clamp(score, -100, 100)
	var enemy_color = Utils.NATION_COLORS.get(opponent, Utils.COLOR_ENEMY_DEFAULT)

	if normalized > 0:
		var fill = ColorRect.new()
		fill.color = Utils.NATION_COLORS["France"]
		_anchor_bar_child(fill, 0.5, 0.5 + (normalized / 100.0) * 0.5, 0.0, 0.0)
		container.add_child(fill)
	elif normalized < 0:
		var fill = ColorRect.new()
		fill.color = enemy_color
		_anchor_bar_child(fill, 0.5 - (abs(normalized) / 100.0) * 0.5, 0.5, 0.0, 0.0)
		container.add_child(fill)

	# Score label. Slice 7.5 review fold: dark outline keeps the score
	# readable over light nation fills (e.g. PapalStates white) at high scores.
	var score_label = Label.new()
	var score_sign = "+" if score > 0 else ""
	score_label.text = score_sign + str(score)
	score_label.add_theme_font_size_override("font_size", font_size)
	score_label.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))
	score_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	score_label.add_theme_constant_override("outline_size", 3)
	score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	score_label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	container.add_child(score_label)

	# Side labels (Enemy on LEFT, France on RIGHT — matches fill direction)
	var enemy_lbl = Label.new()
	var abbr = opponent.left(2).to_upper() if opponent.length() >= 2 else opponent.to_upper()
	enemy_lbl.text = abbr
	enemy_lbl.add_theme_font_size_override("font_size", max(7, font_size - 3))
	enemy_lbl.add_theme_color_override("font_color", Color(0.8, 0.5, 0.5, 0.6))
	# Pinned to the LEFT edge (enemy side) so it tracks the stretched width.
	_anchor_bar_child(enemy_lbl, 0.0, 0.0, 3.0, 23.0)
	enemy_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	container.add_child(enemy_lbl)

	var france_lbl = Label.new()
	france_lbl.text = "FR"
	france_lbl.add_theme_font_size_override("font_size", max(7, font_size - 3))
	france_lbl.add_theme_color_override("font_color", Color(0.5, 0.6, 0.8, 0.6))
	# Pinned to the RIGHT edge (France side), right-aligned.
	_anchor_bar_child(france_lbl, 1.0, 1.0, -23.0, -3.0)
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

	# Breakdown
	if breakdown != null and breakdown is Dictionary:
		bbcode += "[color=" + COLOR_HEADER + "]Score Breakdown[/color]\n"
		bbcode += "  Territory:  " + _signed(int(breakdown.get("territory", 0))) + "\n"
		bbcode += "  Battles:    " + _signed(int(breakdown.get("battles", 0))) + "\n"
		bbcode += "  Decisive:   " + _signed(int(breakdown.get("decisive", 0))) + "\n"
		bbcode += "  Capital:    " + _signed(int(breakdown.get("capital", 0))) + "\n"
		bbcode += "  Ticking:    " + _signed(int(breakdown.get("ticking", 0))) + "\n\n"

	var tier_display = str(w.get("settlement_tier_display", ""))
	if tier_display:
		bbcode += "Settlement Tier: [color=" + COLOR_GOLD + "]" + tier_display + "[/color]\n"

	# PF-2 (D4/UX-1): make the Back Out "Settlement draft kept" promise
	# visible where the player reopens — the badge appears iff a same-turn
	# scoped draft would actually restore.
	if bool(w.get("settlement_draft_kept", false)):
		bbcode += "[color=" + COLOR_GOLD + "]▸ Draft kept — Open Settlement resumes your terms.[/color]\n"

	var objective = w.get("objective", null)
	if objective != null and objective is Dictionary:
		var obj_type = str(objective.get("type_display", "Objective"))
		var targets = objective.get("target_regions", [])
		var target_text = ", ".join(targets) if targets is Array and not targets.is_empty() else "target pending"
		var accumulated = int(float(objective.get("accumulated_ticking", 0)))
		var rate = int(float(objective.get("ticking_rate", 0)))
		var active = "active" if bool(objective.get("ticking_active", false)) else "not ticking"
		bbcode += "Objective: [color=" + COLOR_GOLD + "]" + obj_type + "[/color] - " + target_text
		bbcode += " (" + active + ", +" + str(accumulated)
		if rate > 0:
			bbcode += ", +" + str(rate) + "/turn"
		bbcode += ")\n"

	var enemy_objective = w.get("enemy_objective", null)
	if enemy_objective != null and enemy_objective is Dictionary:
		bbcode += "Enemy Objective: " + str(enemy_objective.get("type_display", "Objective")) + "\n"

	# Duration
	bbcode += "Duration: " + str(duration) + " turns (since Turn " + str(started) + ")\n"

	# War exhaustion
	if we != null:
		var we_int = int(float(we))
		var we_color = COLOR_WHITE
		if we_int >= 80:
			we_color = COLOR_RED
		elif we_int >= 40:
			we_color = COLOR_AMBER
		bbcode += "Enemy War Exhaustion: [color=" + we_color + "]" + str(we_int) + "[/color]\n"
	else:
		bbcode += "Enemy War Exhaustion: [color=" + COLOR_DIMMED + "]Unknown[/color]\n"

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

	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)


func _render_coalition_detail(coalition_data: Dictionary, wars: Array):
	var leader = str(coalition_data.get("leader", ""))
	var posture = str(coalition_data.get("posture", "defensive")).capitalize()

	var bbcode = ""
	bbcode += "Leader: [color=" + COLOR_GOLD + "]" + Utils.display_nation_name(leader) + "[/color]   Posture: " + posture + "\n\n"

	# Members (text summary — bars are in score_bar_container above)
	for w in wars:
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
			line = "[u]" + line + "[/u]"
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

	# G4F-17: project the expiry fork — where this truce is heading and why.
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
	btn.text = "Negotiate Peace"
	btn.tooltip_text = "Open bilateral peace options for this court only."
	btn.custom_minimum_size = Vector2(160, 36)
	btn.add_theme_font_size_override("font_size", 13)
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
	btn.add_theme_font_size_override("font_size", 13)
	btn.pressed.connect(func():
		hide()
		settlement_clicked.emit(war_id, nation)
	)
	button_row.add_child(btn)


func _add_request_terms_button(war_id: String, nation: String, rt_state: Dictionary):
	var btn = Button.new()
	btn.text = "Request Terms"
	btn.custom_minimum_size = Vector2(150, 36)
	btn.add_theme_font_size_override("font_size", 13)
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
	btn.add_theme_font_size_override("font_size", 12)
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
	lbl.add_theme_font_size_override("font_size", 11)
	lbl.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	button_row.add_child(lbl)


func _add_diplomatic_options_button(nation: String):
	var btn = Button.new()
	btn.text = "Diplomatic Options"
	btn.custom_minimum_size = Vector2(160, 36)
	btn.add_theme_font_size_override("font_size", 13)
	btn.pressed.connect(func():
		hide()
		negotiate_clicked.emit(nation)
	)
	button_row.add_child(btn)


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

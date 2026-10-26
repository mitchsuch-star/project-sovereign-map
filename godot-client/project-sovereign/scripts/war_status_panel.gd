extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - War Status Panel (N4a: Layer 1 HUD)
# =============================================================================
# Compact always-visible panel anchored bottom-right. Shows active wars,
# coalition grouping, and armistice cards with tug-of-war score meters.
# CanvasLayer 25. Its width is a viewport fraction; a grip on its top-left
# corner resizes it and the size is remembered (UXR-2, the layout law).
# Clicks emit card_clicked for main.gd to open the detail popup.
# =============================================================================

signal card_clicked(nation: String, status: String, war_instance_id: String)
signal coalition_header_clicked()

@onready var panel_container = $PanelContainer
@onready var scroll_container = $PanelContainer/ScrollContainer
@onready var vbox = $PanelContainer/ScrollContainer/VBoxContainer
@onready var header_label = $PanelContainer/ScrollContainer/VBoxContainer/HeaderLabel

# Nation tints — single source is Utils.NATION_COLORS (§3.3).
# UI-2 Part 2: the score triad + bar track are shared with war_detail_popup —
# they now alias the centralized Utils palette (single source for a re-skin).
const COLOR_GREEN = Utils.UI_SCORE_POSITIVE
const COLOR_RED = Utils.UI_SCORE_NEGATIVE
const COLOR_WHITE = Utils.UI_SCORE_NEUTRAL
const COLOR_GOLD = Color(0.85, 0.7, 0.3)
# 808080 is a palette step (S12, R4): its token. Every use is a caption,
# which keeps 808080 at >= 3 : 1 on the HUD (the R3 rule's one allowance).
var COLOR_DIMMED: Color:
	get: return Color(Utils.COLOR_DIMMED)
const COLOR_BAR_BG = Utils.UI_BAR_BG
const COLOR_BAR_CENTER = Utils.UI_BAR_CENTER_HUD
# War-score bar frame (CC0 Kenney RPG track): 9px 3-slice caps; a cool-navy
# modulate tints the dark track to match the UI without lightening (modulate
# multiplies).
const BAR_FRAME_CAP = 9
const COLOR_BAR_FRAME_TINT = Color(0.72, 0.78, 1.0)
# Max pixels the fill's OUTER edge tucks inside the track's gold rim cap at
# |score| 100 (applied proportionally so mid-range scores stay honest).
const BAR_RIM_INSET = 5.0

# Resize constraints
const MIN_WIDTH = 150
const MIN_HEIGHT = 60
const MAX_HEIGHT_RATIO = 0.45  # Max 45% of screen height
# UXR-2 (the layout law): ANCHORED bottom-right — its width a fraction of the
# logical viewport between the authored 192 and a ceiling, until the player
# drags its grip (the size remembered as "war_status"). The hidden 6-px edge
# band it replaces had no cursor, ate clicks on the cards' edges, could stick
# mid-drag, and was forgotten on every restart.
const EDGE_MARGIN := 8.0
const WIDTH_FRACTION := 0.12
const DEFAULT_MIN_WIDTH := 192.0
const DEFAULT_MAX_WIDTH := 440.0


func _ready():
	hide()
	_add_panel_grain()
	# UXR-2 (the layout law): the panel re-fits when the window or the
	# Interface Scale changes the logical viewport under it — it fit only on
	# `update_wars`, so a scale step left its height cap stale.
	get_viewport().size_changed.connect(_on_viewport_size_changed)
	var grip = ResizeGrip.attach_edge(panel_container, "war_status", ResizeGrip.Corner.TOP_LEFT)
	grip.resize_requested.connect(_apply_geometry)
	grip.resize_committed.connect(func(_s): _fit_panel_to_content())
	grip.reset_requested.connect(_fit_panel_to_content)


func _on_viewport_size_changed() -> void:
	if visible:
		_fit_panel_to_content()


func _add_panel_grain() -> void:
	# Subtle dark-leather grain behind the panel content for a richer, in-world
	# feel (existing CC0 leather asset, dark-navy-tinted + low alpha so it reads
	# as texture, not a brown wash). Behind the ScrollContainer; ignores mouse.
	var tex = load("res://assets/textures/fabric_leather_01_diff_1k.jpg")
	if tex == null:
		return
	var grain = TextureRect.new()
	grain.texture = tex
	grain.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	# CRITICAL: without EXPAND_IGNORE_SIZE the TextureRect reports the 1024x1024
	# texture as its minimum size, and PanelContainer (which sizes to its
	# children's min) balloons the whole panel to fill the screen.
	grain.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	grain.custom_minimum_size = Vector2.ZERO
	grain.modulate = Color(0.30, 0.32, 0.44, 0.32)
	grain.mouse_filter = Control.MOUSE_FILTER_IGNORE
	grain.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	panel_container.add_child(grain)
	panel_container.move_child(grain, 0)


func update_wars(data: Dictionary) -> void:
	"""Rebuild the entire panel from active_wars data."""
	# Clear existing cards (keep header)
	for child in vbox.get_children():
		if child != header_label:
			vbox.remove_child(child)
			child.queue_free()

	var wars = data.get("wars", [])
	var foreign_wars = data.get("foreign_wars", [])
	# AI-6c (§4.6b): Europe's own wars keep the panel alive even when
	# France herself is at peace — that is exactly when they matter.
	if wars.is_empty() and foreign_wars.is_empty():
		hide()
		return

	header_label.text = "ACTIVE WARS"
	# R159 (POSITION 7): the HUD names its mechanic on hover.
	header_label.tooltip_text = "Your active wars and Europe's own — click a card for the full ledger of one war."

	var coalition_data = data.get("coalition", null)
	var has_coalition = coalition_data != null

	# ── Coalition group ──
	if has_coalition:
		var coalition_name = str(coalition_data.get("name", "Coalition"))
		_add_coalition_header(coalition_name)
		for w in wars:
			if w.get("in_coalition", false) and w.get("status", "") == "war":
				_add_war_entry(w, true)

	# ── Bilateral war cards (non-coalition) ──
	for w in wars:
		if w.get("status", "") == "war" and not w.get("in_coalition", false):
			_add_war_entry(w, false)

	# ── Armistice cards ──
	for w in wars:
		if w.get("status", "") == "armistice":
			_add_armistice_card(w)

	# ── Foreign wars (AI-6c §4.6b): the wars France is NOT in — court
	# knowledge across Europe, compact and dim; the tooltip carries the
	# cause and the bleed ("let them bleed while France rearms").
	if not foreign_wars.is_empty():
		_add_foreign_wars_header()
		for fw in foreign_wars:
			_add_foreign_war_row(fw)

	show()
	_fit_panel_to_content()


func _fit_panel_to_content() -> void:
	# Shrink-wrap the panel height to its content (up to MAX_HEIGHT_RATIO of the
	# screen, then the ScrollContainer scrolls). A fixed .tscn height left a big
	# dead gap below a single war entry. Anchored bottom-right, so the TOP and
	# LEFT edges move. One frame lets the containers lay out.
	await get_tree().process_frame
	if not visible or not is_instance_valid(panel_container):
		return
	_apply_geometry()


func _apply_geometry(drag: Vector2 = Vector2.ZERO) -> void:
	"""UXR-2: the panel's rect. Width: the grip's live drag, else the stored
	size, else a viewport fraction. Height: shrink-wrapped to the cards under
	MAX_HEIGHT_RATIO of the screen — a stored height is a CAP on that, so a
	short war list never leaves a tall empty panel."""
	if not is_instance_valid(panel_container):
		return
	var view: Vector2 = get_viewport().get_visible_rect().size
	var max_h := float(int(view.y * MAX_HEIGHT_RATIO))
	var stored := UiSettings.get_panel_size("war_status", Vector2.ZERO)
	# UXR-D3: the HUD band's right edge, and a fraction of its width.
	var band := Utils.hud_band(view)
	var room := band.y - band.x
	var w: float
	if drag != Vector2.ZERO:
		w = drag.x
	elif stored != Vector2.ZERO:
		w = stored.x
	else:
		w = Utils.fraction_px(room, WIDTH_FRACTION, DEFAULT_MIN_WIDTH, DEFAULT_MAX_WIDTH)
		# UXR-D4 (Pre-Deploy S12b): never narrower than its longest war line
		# needs whole — the Side Desk's dock narrows the band, and at the
		# floor "Britain + Austria + Russia" was cut to "Rus".
		w = maxf(w, _content_need_width())
	w = clampf(w, MIN_WIDTH, maxf(room - 2.0 * EDGE_MARGIN, MIN_WIDTH))
	var h: float
	if drag != Vector2.ZERO:
		h = clampf(drag.y, MIN_HEIGHT, maxf(max_h, MIN_HEIGHT))
	else:
		var cap := max_h
		if stored != Vector2.ZERO:
			cap = minf(cap, stored.y)
		# +18 covers the panel stylebox content margins (12 top + 4 bottom) +
		# slack. The top margin is the grip's: its hatch sits in the corner's
		# padding, never on the header (UXR3-F4, Pre-Deploy S12 part 2).
		h = clampf(vbox.get_combined_minimum_size().y + 18.0, MIN_HEIGHT, maxf(cap, MIN_HEIGHT))
	var right_inset := EDGE_MARGIN + (view.x - band.y)
	panel_container.offset_right = -right_inset
	panel_container.offset_bottom = -EDGE_MARGIN
	panel_container.offset_left = -right_inset - w
	panel_container.offset_top = -EDGE_MARGIN - h


func _content_need_width() -> float:
	"""The width the panel needs for every war line whole: its own combined
	minimum (every fixed part of every row) plus the most any clipping name
	label's text runs past the minimum it reports."""
	var extra := 0.0
	var stack: Array = [vbox]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		for c in n.get_children():
			stack.append(c)
		if n is Label and (n as Label).clip_text and (n as Label).visible:
			var label := n as Label
			var font: Font = label.get_theme_font("font")
			if font == null:
				continue
			var tw: float = font.get_string_size(label.text, HORIZONTAL_ALIGNMENT_LEFT, -1,
					label.get_theme_font_size("font_size")).x
			extra = maxf(extra, tw - label.get_combined_minimum_size().x)
	return panel_container.get_combined_minimum_size().x + extra + 2.0


func _add_coalition_header(coalition_name: String):
	var btn = Button.new()
	btn.text = " " + coalition_name.to_upper() + "  ▸"
	btn.custom_minimum_size = Vector2(0, 18)
	btn.theme_type_variation = &"CaptionButton"
	btn.add_theme_color_override("font_color", COLOR_GOLD)
	btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn.tooltip_text = "Open the coalition's detail"
	_give_row_chrome(btn)
	btn.pressed.connect(func(): coalition_header_clicked.emit())
	vbox.add_child(btn)


func _give_row_chrome(btn: Button) -> void:
	"""UXR3-14 (Pre-Deploy S12): the header and the war rows open the detail,
	so they are drawn as controls — a faint card with a hairline border at
	rest, a gold fill on hover and press, and the pointing hand — never as a
	plain heading and a status bar."""
	btn.flat = false
	btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var rest := StyleBoxFlat.new()
	rest.bg_color = Color(Utils.UI_GOLD, 0.05)
	rest.border_color = Color(Utils.UI_GOLD, 0.28)
	rest.set_border_width_all(1)
	rest.set_corner_radius_all(3)
	rest.set_content_margin_all(2)
	var hover := rest.duplicate() as StyleBoxFlat
	hover.bg_color = Color(Utils.UI_GOLD, 0.16)
	hover.border_color = Color(Utils.UI_GOLD, 0.7)
	var pressed := hover.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(Utils.UI_GOLD, 0.24)
	btn.add_theme_stylebox_override("normal", rest)
	btn.add_theme_stylebox_override("hover", hover)
	btn.add_theme_stylebox_override("pressed", pressed)
	btn.add_theme_stylebox_override("focus", StyleBoxEmpty.new())


func _add_war_entry(war_data: Dictionary, is_coalition_member: bool):
	"""Add a two-line war entry: name + turn on top, a full-width tug-of-war bar
	below. Two lines guarantee the bar always gets the panel's full width — a
	long collapsed coalition name (e.g. "Britain + Austria + Russia") no longer
	crushes it to nothing. Entire card is clickable."""
	var opponent = str(war_data.get("opponent", "?"))
	var opponent_display = Utils.humanize_nation_keys_in_text(str(war_data.get("opponent_display", Utils.display_nation_name(opponent))))
	var score = int(float(war_data.get("war_score", 0)))
	var duration = int(float(war_data.get("duration", 0)))

	# Whole card is a flat Button for full clickability
	var row_btn = Button.new()
	row_btn.custom_minimum_size = Vector2(0, 36)
	row_btn.pressed.connect(func(): card_clicked.emit(opponent, "war", str(war_data.get("war_instance_id", ""))))
	_give_row_chrome(row_btn)
	row_btn.tooltip_text = _build_war_tooltip(war_data)

	# Inner VBox: [name row] over [bar]. Passes mouse through to the button.
	var col = VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.add_theme_constant_override("separation", 1)
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# ── Line 1: name (clips instead of pushing) + turn counter ──
	var name_row = HBoxContainer.new()
	name_row.add_theme_constant_override("separation", 4)
	name_row.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# UI-6: opponent heraldry ahead of the name (untinted colored art)
	var flag_path = Utils.nation_flag_path(opponent)
	if flag_path != "":
		var flag_rect = TextureRect.new()
		flag_rect.texture = load(flag_path)
		flag_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		flag_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		flag_rect.custom_minimum_size = Vector2(16, 11)
		flag_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		name_row.add_child(flag_rect)

	var name_label = Label.new()
	var indent = "  " if is_coalition_member else ""
	# PC-R7 (i) — ruling J (S13e part 4): the card is titled by the war's
	# STAKE ("War for Bohemia"), never the leader pair; who stays on the
	# tooltip's first line. An older payload keeps the roster.
	var war_title = str(war_data.get("war_title", ""))
	name_label.text = indent + (war_title if war_title != "" else opponent_display)
	name_label.clip_text = true
	name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	name_label.theme_type_variation = &"Caption"
	name_label.add_theme_color_override("font_color", Color(0.85, 0.85, 0.88))
	name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	name_row.add_child(name_label)

	# Score number lives here (not on the bar) so it never fights the centre gem.
	var score_label = Label.new()
	# PC-F84 (S13e part 3): the trend's glyph beside the score ("+77 ↑").
	var glyph = str(war_data.get("trend_glyph", ""))
	score_label.text = ("+" if score > 0 else "") + str(score) + ("" if glyph == "" else " " + glyph)
	score_label.theme_type_variation = &"Caption"
	score_label.add_theme_color_override("font_color", _get_score_color(score))
	score_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	name_row.add_child(score_label)

	var turn_label = Label.new()
	turn_label.text = "T:" + str(duration)
	turn_label.theme_type_variation = &"Caption"
	turn_label.add_theme_color_override("font_color", COLOR_DIMMED)
	turn_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	name_row.add_child(turn_label)
	col.add_child(name_row)

	# ── Line 2: full-width tug-of-war bar ──
	var bar = _create_tug_of_war_bar(score, opponent, 80, 16)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_child(bar)

	row_btn.add_child(col)
	vbox.add_child(row_btn)


func _build_war_tooltip(war_data: Dictionary) -> String:
	var lines = []
	# PC-R7 (i): the title's own line leads — the stake named, then who.
	var title_line = str(war_data.get("war_title_line", ""))
	if title_line != "":
		lines.append(Utils.humanize_nation_keys_in_text(title_line))
	if bool(war_data.get("is_multi_participant_war", false)):
		lines.append("Shared war: " + Utils.humanize_nation_keys_in_text(str(war_data.get("opponent_display", Utils.display_nation_name(str(war_data.get("opponent", "?")))))))
	elif str(war_data.get("war_title", "")) != "":
		lines.append("With: " + Utils.humanize_nation_keys_in_text(str(war_data.get("opponent_display", Utils.display_nation_name(str(war_data.get("opponent", "?")))))))
	var tier = str(war_data.get("settlement_tier_display", ""))
	if tier:
		# IQ-2 (Sept 14, 2026): the tier read as OURS to claim — "Settlement:
		# Harsh Peace" — on a war France was losing to one province. When the
		# backend says the table is the enemy's, say whose. (A tooltip is
		# plain text; the war-detail popup carries the colour.)
		if str(war_data.get("settlement_tier_side", "")) == "theirs":
			lines.append("Settlement (theirs to impose): " + tier)
		else:
			lines.append("Settlement: " + tier)
	# PC-F33 (S13e part 4): a white peace confirms every holding — say so.
	var held_line = str(war_data.get("held_line", ""))
	if held_line != "":
		lines.append(Utils.humanize_nation_keys_in_text(held_line))
	# PC-F3 (Oct 15, 2026): what the peace math reads — the table's own
	# number, each court against 50, and (mid-turn) that this turn's
	# fighting counts from next turn. The backend writes the sentences.
	var peace_table = war_data.get("peace_table", null)
	if peace_table is Dictionary:
		for ln in peace_table.get("lines", []):
			lines.append(Utils.humanize_nation_keys_in_text(str(ln)))
	# PC-R6 (S13e part 3): the components that are FULL, named ("Full:
	# Battles 15/15 — another victory adds nothing there").
	for ln in war_data.get("breakdown_fill_lines", []):
		lines.append(str(ln))
	# PC-R5 / F42: the clock's components, one line (the popup carries the rest).
	var ex_line = str(war_data.get("exhaustion_line", ""))
	if ex_line != "":
		lines.append(Utils.humanize_nation_keys_in_text(ex_line))
	var objective = war_data.get("objective", null)
	if objective != null and objective is Dictionary:
		# LV-8 (row EP F1): one sentence, not the 28-name homeland list.
		var target_text = Utils.objective_targets_text(objective, "target pending")
		lines.append("Objective: " + str(objective.get("type_display", "Objective")) + " - " + target_text)
		lines.append("Ticking: +" + str(int(float(objective.get("accumulated_ticking", 0)))))
	var enemy_objective = war_data.get("enemy_objective", null)
	if enemy_objective != null and enemy_objective is Dictionary:
		lines.append("Enemy: " + str(enemy_objective.get("type_display", "Objective")))
	# WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §16.2 — top-five
	# contribution share rows + overflow indicator. Rows come from
	# `build_active_wars` which already enforces the cap server-side.
	# FA-D10 (slice 17, Phase 2): ONE formatter for both surfaces (Utils).
	var standing_rows = Utils.standing_lines(war_data)
	if standing_rows.size() > 0:
		lines.append("---")
		for ln in standing_rows:
			lines.append(ln)
	return "\n".join(lines)


func _add_armistice_card(war_data: Dictionary):
	var opponent = str(war_data.get("opponent", "?"))
	var opponent_display = Utils.display_nation_name(opponent)
	var remaining = int(float(war_data.get("armistice_remaining", 0)))

	var btn = Button.new()
	# PC-R7 (i) (S13e part 4): a truce is a pause in a war that keeps its
	# title — "War for Bohemia — Austria, truce 4t".
	var truce_title = str(war_data.get("war_title", ""))
	if truce_title != "":
		btn.text = truce_title + " — " + opponent_display + ", truce " + str(remaining) + "t"
	else:
		btn.text = opponent_display + "  " + str(remaining) + "t"
	btn.flat = true
	btn.custom_minimum_size = Vector2(0, 16)
	btn.theme_type_variation = &"CaptionButton"
	btn.add_theme_color_override("font_color", COLOR_DIMMED)
	# UI-6: opponent heraldry on the truce row too
	Utils.apply_flag_icon(btn, opponent)
	# G4F-17: the HUD card whispers the expiry fork — tooltip names where
	# the truce is heading (peace vs collapse) without growing the card.
	# PC-R2 / PC-F44 (S13e part 2): the tooltip reads the one wording — what
	# the truce keeps, where it heads, the cure priced.
	var keeps = str(war_data.get("armistice_keeps_line", ""))
	var heading = str(war_data.get("armistice_heading_line", ""))
	var cure = str(war_data.get("armistice_cure_line", ""))
	var projected = str(war_data.get("armistice_projected_outcome", ""))
	if keeps != "" or heading != "":
		# PC-X11: one part a line. PC-F47 (S15 head): the hard wrap at 100
		# characters is retired — the tooltip wraps itself to the window now
		# (`Utils.wrap_tooltips`), and a fixed width re-wrapped raggedly in a
		# narrow one.
		var tip = "Armistice with %s — %d turns left.\n%s\n%s" % [opponent_display, remaining, keeps, heading]
		if cure != "":
			tip += "\n" + cure
		btn.tooltip_text = tip.strip_edges()
	elif projected == "peace":
		btn.tooltip_text = "Armistice with %s — %d turns left, on course for peace." % [opponent_display, remaining]
	elif projected == "war":
		btn.tooltip_text = "Armistice with %s — %d turns left, on course to collapse back to war unless relations heal." % [opponent_display, remaining]
	btn.pressed.connect(func(): card_clicked.emit(opponent, "armistice", str(war_data.get("war_instance_id", ""))))
	vbox.add_child(btn)


func _add_foreign_wars_header():
	var lbl = Label.new()
	lbl.text = " FOREIGN WARS"
	lbl.theme_type_variation = &"Caption"
	lbl.add_theme_color_override("font_color", COLOR_DIMMED)
	vbox.add_child(lbl)


func _add_foreign_war_row(fw: Dictionary):
	"""AI-6c (§4.6b): one third-party war, unclickable (the ledger and the
	war room own its depth) — hover carries duration, cause and the two
	leaders' exhaustion where French intelligence can see it."""
	var att = str(fw.get("attackers_display", "?"))
	var def_side = str(fw.get("defenders_display", "?"))
	var btn = Button.new()
	# PC-X25 (S13e part 4): a foreign war is titled by its stake too; who
	# fights it rides the tooltip's first line.
	var fw_title = str(fw.get("war_title", ""))
	btn.text = fw_title if fw_title != "" else att + " vs " + def_side
	btn.flat = true
	btn.custom_minimum_size = Vector2(0, 16)
	btn.theme_type_variation = &"CaptionButton"
	btn.add_theme_color_override("font_color", COLOR_DIMMED)
	var lines: Array = []
	lines.append("%s vs %s — turn %d of their war." % [
		att, def_side, int(float(fw.get("duration", 0)))])
	var fw_line = str(fw.get("war_title_line", ""))
	if fw_line != "":
		lines.append(Utils.humanize_nation_keys_in_text(fw_line))
	var reason = str(fw.get("stated_reason", ""))
	if reason != "":
		lines.append("Cause: " + reason + ".")
	var att_we = fw.get("attacker_exhaustion")
	var def_we = fw.get("defender_exhaustion")
	if att_we != null or def_we != null:
		var att_s = "?" if att_we == null else str(int(float(att_we)))
		var def_s = "?" if def_we == null else str(int(float(def_we)))
		lines.append("Exhaustion — %s: %s · %s: %s" % [att, att_s, def_side, def_s])
	btn.tooltip_text = "\n".join(lines)
	vbox.add_child(btn)


func _create_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int) -> Control:
	"""Premium tug-of-war gauge: a gold-rimmed recessed track, a glossy fill
	tinted to the leader's nation (France blue right / enemy left), and a gold
	centre gem. The SCORE NUMBER is shown on the name line, not on the bar, so
	it never fights the gem. All children pass the mouse to the parent button."""
	return _build_tug_of_war_bar(score, opponent, bar_width, bar_height)


# Shared premium tug-of-war builder (HUD + detail popup use the same textures,
# assets/ui/bars/warbar_*.png — original gold-and-navy chrome). load() (not
# preload) so a missing texture degrades gracefully instead of a parse failure.
static func _build_tug_of_war_bar(score: int, opponent: String, bar_width: int, bar_height: int) -> Control:
	var container = Control.new()
	container.custom_minimum_size = Vector2(bar_width, bar_height)
	container.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Gold-rimmed recessed track (horizontal 3-slice: rounded L/R caps).
	var track = NinePatchRect.new()
	track.texture = load("res://assets/ui/bars/warbar_track.png")
	track.patch_margin_left = 14
	track.patch_margin_right = 14
	track.mouse_filter = Control.MOUSE_FILTER_IGNORE
	track.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	container.add_child(track)

	# Glossy fill from centre, tinted to the leader's nation via modulate (the
	# fill texture is grayscale, so modulate keeps the gloss).
	var normalized = clamp(score, -100, 100)
	if normalized != 0:
		var fill = TextureRect.new()
		fill.texture = load("res://assets/ui/bars/warbar_fill.png")
		fill.stretch_mode = TextureRect.STRETCH_SCALE
		# EXPAND_IGNORE_SIZE is load-bearing: without it the texture's natural
		# 72x22 px becomes the control's MINIMUM size, so any anchored span
		# smaller than that (short bars, high UI scale, low scores) overflows
		# past the centre gem and bulges out of the track.
		fill.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var fraction: float = abs(normalized) / 100.0
		var rim_inset: float = BAR_RIM_INSET * fraction
		if normalized > 0:
			fill.modulate = Utils.NATION_COLORS["France"]
			_anchor_bar_child(fill, 0.5, 0.5 + fraction * 0.5, 0.0, -rim_inset)
		else:
			fill.modulate = Utils.NATION_COLORS.get(opponent, Utils.COLOR_ENEMY_DEFAULT)
			_anchor_bar_child(fill, 0.5 - fraction * 0.5, 0.5, rim_inset, 0.0)
		fill.offset_top = 3.0
		fill.offset_bottom = -3.0
		container.add_child(fill)

	# Gold centre gem (the balanced-point marker; reads even at an even score).
	var gem = TextureRect.new()
	gem.texture = load("res://assets/ui/bars/warbar_gem.png")
	gem.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	# Same min-size trap as the fill: the 26x26 texture must not clamp the
	# 20x20 anchored rect or the gem drifts right/down off the true centre.
	gem.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	gem.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var gem_size := float(bar_height) + 4.0
	gem.anchor_left = 0.5
	gem.anchor_right = 0.5
	gem.anchor_top = 0.5
	gem.anchor_bottom = 0.5
	gem.offset_left = -gem_size / 2.0
	gem.offset_right = gem_size / 2.0
	gem.offset_top = -gem_size / 2.0
	gem.offset_bottom = gem_size / 2.0
	container.add_child(gem)

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


func _get_score_color(score: int) -> Color:
	if score > 0:
		return COLOR_GREEN
	elif score < 0:
		return Utils.UI_SCORE_NEGATIVE_TEXT   # the score is text (S12)
	return COLOR_WHITE

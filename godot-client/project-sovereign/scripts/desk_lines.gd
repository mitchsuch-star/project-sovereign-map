extends VBoxContainer

# =============================================================================
# INK & IRON - The desk's three lines (row IC, November 19, 2026)
# =============================================================================
# THE PEACE, THE WAR, TO DECIDE - from the backend's one `desk` key
# (`backend/game_logic/today.py`): what the campaign is for, what each war is
# fought for, and the matters that want a word now.
#
#   full   the card at the map's top-left corner (the desk and the 32:9 column):
#          the two lines, then up to `shown` rows of TO DECIDE, each one sentence
#          and ONE door; "+n more" opens the rest. A small fold control puts the
#          card away to one line and brings it back.
#   line   the slim bar (the compact view), and the folded card: one line - how
#          many matters, and the first of them; its door is that row's.
#
# The control judges nothing and sends nothing: every press is the signal
# `door_pressed(door, row_id)` and the host (main.gd) opens the place. A row is
# a Button, so the keyboard reaches it (Tab / the arrows, Enter or Space); the
# small x beside it sets the row aside for the turn - on this client only (a
# saved key would close Take back). Text first: a matter that bites when the
# turn ends wears a mark as well as a colour.
# =============================================================================

signal door_pressed(door: Dictionary, row_id: String)
signal resized_by_content()
signal focus_released()   # the last row was set aside from the keyboard: the host takes the focus back

const BITES := 1          # the backend's tier for "bites when the turn ends"
const MARK_BITES := "!"   # a shape beside the colour (never colour alone)
const FOLD_FACE := "–"
const UNFOLD_FACE := "+"
const FOLD_TIP := "Put this card away (it stays one line)"
const UNFOLD_TIP := "Open the card: the peace, the war, and what wants your word"
# Lever L2 of the blind reading (all three readers: "the ! in front of a matter
# is not explained"): one line under the rows says what the mark means.
const LEGEND := "    ! can cost you when the turn ends"

var _mode := "full"
var _foldable := false
var _folded := false
var _desk: Dictionary = {}
var _turn := -1
var _aside := {}          # row id -> true, for `_turn` only
var _expanded := false
var _signature := ""

var _top: HBoxContainer = null
var _peace: Button = null
var _fold: Button = null
var _war: Button = null
var _own: Button = null        # row IC, Session 3: "ON THEIR OWN — 1 of 2 · …"
var _head: Button = null
var _rows_box: VBoxContainer = null
var _more: Button = null
var _legend: Label = null
var _line_row: HBoxContainer = null
var _line: Button = null
var _unfold: Button = null
var _row_buttons: Array = []   # [Button], the rows on show, in order


func _init() -> void:
	name = "DeskLines"
	add_theme_constant_override("separation", 1)
	visible = false
	_top = HBoxContainer.new()
	_top.name = "TopRow"
	_top.add_theme_constant_override("separation", 2)
	add_child(_top)
	_peace = _make_line("PeaceLine")
	_top.add_child(_peace)
	_fold = _make_corner("Fold", FOLD_FACE, FOLD_TIP)
	_fold.pressed.connect(_on_fold_pressed)
	_top.add_child(_fold)
	_war = _make_line("WarLine")
	add_child(_war)
	_own = _make_line("OwnLine")
	_own.focus_mode = Control.FOCUS_NONE
	_own.visible = false
	add_child(_own)
	_head = _make_line("DecideHead")
	_head.focus_mode = Control.FOCUS_NONE
	_head.pressed.connect(_on_more_pressed)
	add_child(_head)
	_rows_box = VBoxContainer.new()
	_rows_box.name = "DecideRows"
	_rows_box.add_theme_constant_override("separation", 0)
	add_child(_rows_box)
	_legend = Label.new()
	_legend.name = "Legend"
	_legend.text = LEGEND
	_legend.theme_type_variation = &"Caption"
	_legend.add_theme_color_override("font_color", Color(Color.html("#" + Utils.COLOR_WARNING), 0.85))
	_legend.visible = false
	add_child(_legend)
	_more = _make_line("MoreRows")
	_more.pressed.connect(_on_more_pressed)
	add_child(_more)
	_line_row = HBoxContainer.new()
	_line_row.name = "LineRow"
	_line_row.add_theme_constant_override("separation", 2)
	add_child(_line_row)
	_line = _make_line("OneLine")
	_line.autowrap_mode = TextServer.AUTOWRAP_OFF
	_line.clip_text = true
	_line.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_line.pressed.connect(_on_one_line_pressed)
	_line_row.add_child(_line)
	_unfold = _make_corner("Unfold", UNFOLD_FACE, UNFOLD_TIP)
	_unfold.pressed.connect(_on_fold_pressed)
	_line_row.add_child(_unfold)
	_peace.pressed.connect(_on_line_pressed.bind("peace"))
	_war.pressed.connect(_on_line_pressed.bind("war"))


# ---------------------------------------------------------------- the API

func set_mode(mode: String) -> void:
	"""The desk's form: "line" on the slim bar, else "full"."""
	var want := "line" if mode == "line" else "full"
	if want == _mode:
		return
	_mode = want
	_rebuild()


func set_foldable(foldable: bool) -> void:
	"""The card may be put away to one line (never the slim bar's line: it is
	one line already)."""
	if foldable == _foldable:
		return
	_foldable = foldable
	if not foldable:
		_folded = false
	_rebuild()


func is_folded() -> bool:
	return _folded


func set_desk(desk, turn: int) -> void:
	"""The backend's `desk` payload for `turn` (null or {} hides the lines). A
	new turn lets every set-aside row back; a payload that changes nothing on
	show rebuilds nothing (no hover or focus lost to a refresh)."""
	var d: Dictionary = desk if desk is Dictionary else {}
	if turn != _turn:
		_turn = turn
		_aside.clear()
		_expanded = false
	var sig := JSON.stringify(d) + "|" + str(_turn)
	if sig == _signature:
		return
	_signature = sig
	_desk = d
	_rebuild()


func set_aside(row_id: String) -> void:
	"""Set one row aside for this turn (this client only)."""
	if row_id == "":
		return
	_aside[row_id] = true
	_rebuild()


func rows() -> Array:
	"""The TO DECIDE rows still standing (those set aside left out), in order."""
	var out: Array = []
	var all = _desk.get("decide", [])
	if not (all is Array):
		return out
	for r in all:
		if r is Dictionary and not _aside.has(str(r.get("id", ""))):
			out.append(r)
	return out


func shown_ids() -> Array:
	"""The ids of the rows on show now, in order (read by the driven tests)."""
	var out: Array = []
	for b in _row_buttons:
		if is_instance_valid(b) and b.visible:
			out.append(str(b.get_meta("row_id", "")))
	return out


func texts() -> Dictionary:
	"""What the lines say now (read by the driven tests)."""
	var shown: Array = []
	for b in _row_buttons:
		if is_instance_valid(b) and b.visible:
			shown.append(str(b.text))
	var one := _one_line()
	return {"peace": _peace.text if (not one and _peace.visible) else "", "war": _war.text if _war.visible else "",
			"head": _head.text if _head.visible else "", "rows": shown,
			"more": _more.text if _more.visible else "", "line": _line.text if one else "",
			"legend": _legend.text if _legend.visible else "",
			"mode": _mode, "folded": _folded,
			"own": _own.text if _own.visible else ""}


func first_row_button() -> Button:
	for b in _row_buttons:
		if is_instance_valid(b) and b.visible:
			return b
	return null


# ---------------------------------------------------------------- building

func _make_line(node_name: String) -> Button:
	var b := Button.new()
	b.name = node_name
	b.flat = true
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	b.theme_type_variation = &"CaptionButton"
	b.focus_mode = Control.FOCUS_ALL
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
	b.add_theme_color_override("font_hover_color", Utils.UI_GOLD_BRIGHT)
	b.add_theme_color_override("font_focus_color", Utils.UI_GOLD_BRIGHT)
	return b


func _make_corner(node_name: String, face: String, tip: String) -> Button:
	var b := Button.new()
	b.name = node_name
	b.flat = true
	b.text = face
	b.tooltip_text = tip
	b.focus_mode = Control.FOCUS_NONE
	b.theme_type_variation = &"CaptionButton"
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	b.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
	b.add_theme_color_override("font_hover_color", Utils.UI_GOLD_BRIGHT)
	return b


func _has_door(part) -> bool:
	if not (part is Dictionary):
		return false
	var door = (part as Dictionary).get("door", {})
	return door is Dictionary and not (door as Dictionary).is_empty()


func _door_face(b: Button, has_door: bool) -> void:
	"""A line with no door is a sentence, not a button: no hand, no stop for Tab."""
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND if has_door else Control.CURSOR_ARROW
	b.focus_mode = Control.FOCUS_ALL if has_door else Control.FOCUS_NONE


func _tone_color(tone: String) -> Color:
	match tone:
		"bad":
			return Color.html("#" + Utils.COLOR_ERROR)
		"good":
			return Color.html("#" + Utils.COLOR_SUCCESS)
	return Utils.toned(Utils.UI_TEXT_DIM)


func _one_line() -> bool:
	return _mode == "line" or _folded


func _rebuild() -> void:
	for b in _row_buttons:
		if is_instance_valid(b):
			var holder: Node = (b as Button).get_parent()
			if holder != null and holder.get_parent() == _rows_box:
				_rows_box.remove_child(holder)
				holder.queue_free()
	_row_buttons.clear()
	var peace = _desk.get("peace", {})
	var war = _desk.get("war", {})
	var peace_text := str(peace.get("text", "")) if peace is Dictionary else ""
	var war_text := str(war.get("text", "")) if war is Dictionary else ""
	var standing := rows()
	if _desk.is_empty() or (peace_text == "" and war_text == "" and standing.is_empty()):
		visible = false
		_legend.visible = false
		resized_by_content.emit()
		return
	visible = true
	var one_line := _one_line()
	_top.visible = not one_line
	_peace.visible = peace_text != ""
	_fold.visible = _foldable
	_war.visible = not one_line and war_text != ""
	_head.visible = not one_line and not standing.is_empty()
	_rows_box.visible = not one_line and not standing.is_empty()
	_line_row.visible = one_line
	_unfold.visible = _foldable and _folded
	if one_line:
		_more.visible = false
		_legend.visible = false
		_own.visible = false    # the review, IC3-V: the one-line desk carries no own line
		_fill_one_line(peace_text, war_text, standing)
		resized_by_content.emit()
		return
	_peace.text = "THE PEACE — " + peace_text
	_peace.tooltip_text = str(peace.get("hint", "")) if peace is Dictionary else ""
	_peace.add_theme_color_override("font_color", _tone_color(str(peace.get("tone", "")) if peace is Dictionary else ""))
	_door_face(_peace, _has_door(peace))
	_war.text = "THE WAR — " + war_text
	_war.tooltip_text = str(war.get("hint", "")) if war is Dictionary else ""
	_door_face(_war, _has_door(war))
	_fill_own()
	var limit := int(_desk.get("shown", 3))
	var show_n := standing.size() if _expanded else mini(limit, standing.size())
	_head.text = "TO DECIDE — %s · press one to go to it" % Utils.plural(standing.size(), "matter")
	_head.tooltip_text = "What wants your word now, the most pressing first. Press a row to go to it."
	_head.add_theme_color_override("font_color", Utils.UI_GOLD)
	var any_bites := false
	for i in show_n:
		_rows_box.add_child(_make_row(i, standing[i]))
		if int((standing[i] as Dictionary).get("tier", 0)) == BITES:
			any_bites = true
	_legend.visible = any_bites
	var hidden: int = standing.size() - show_n + int(_desk.get("more", 0))
	_more.visible = hidden > 0 or (_expanded and standing.size() > limit)
	if hidden > 0:
		_more.text = "    + %d more" % hidden
		_more.tooltip_text = "Show every matter"
	else:
		_more.text = "    show fewer"
		_more.tooltip_text = "Show the first %d only" % limit
	resized_by_content.emit()


func _fill_own() -> void:
	"""Row IC, Session 3 (§4): "ON THEIR OWN — 1 of 2 · tonight: Ney attacks
	Mack at Swabia" while a man is on his own; every man's night on the hover."""
	var own = _desk.get("own", {})
	var tonight = own.get("tonight", []) if own is Dictionary else []
	if not (own is Dictionary) or int(own.get("n", 0)) <= 0 or not (tonight is Array):
		_own.visible = false
		return
	var first := ""
	var army_note := ""
	var all := PackedStringArray()
	for r in tonight:
		if r is Dictionary:
			all.append(str(r.get("line", "")))
			if first == "":
				first = str(r.get("line", "")).trim_prefix("Tonight: ")
				# Row IC, Session 3b: an army's commander is counted ONCE — the
				# line says how many follow him (each man's night is on the hover).
				var behind := int(r.get("followers", 0))
				if str(r.get("army", "")) != "":
					army_note = ("the " + str(r.get("army", "")) + ", "
						+ ("nobody following yet" if behind == 0 else (
							"1 man following" if behind == 1 else (str(behind) + " men following"))) + " · ")
	_own.text = "ON THEIR OWN — %d of the %d you may have · %stonight: %s" % [int(own.get("n", 0)), int(own.get("of", 1)), army_note, first]
	# (round 2 of the blind reading: "1 of 1" never said how to raise it)
	_own.tooltip_text = "\n".join(all) + "\n\nThe laws raise the count: the Grand Quartier Général," + " then the Emperor's Aides-de-Camp, one more each."
	_own.visible = not _one_line()


func _make_row(index: int, row: Dictionary) -> Control:
	var holder := HBoxContainer.new()
	holder.name = "Row%d" % (index + 1)
	holder.add_theme_constant_override("separation", 2)
	var b := Button.new()
	b.name = "Matter"
	b.flat = true
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	b.focus_mode = Control.FOCUS_ALL
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var bites := int(row.get("tier", 0)) == BITES
	b.text = "%d. %s%s" % [index + 1, (MARK_BITES + " ") if bites else "", str(row.get("text", ""))]
	var more := str(row.get("more", ""))
	# Row IC, Session 4 (IC-13): a letter-following man's own line rides the
	# hover, after the row's own words (the row's one line stays as it was)
	var voiced := VoiceLine.plain_text(str(row.get("speaker", "")), str(row.get("says", "")))
	if voiced != "":
		more = (more + "\n" if more != "" else "") + voiced
	b.tooltip_text = (more + "\n" if more != "" else "") + "Press to go to it."
	var ink := Color.html("#" + Utils.COLOR_WARNING) if bites else Utils.toned(Utils.UI_TEXT_DIM)
	b.add_theme_color_override("font_color", ink)
	b.add_theme_color_override("font_hover_color", Utils.UI_GOLD_BRIGHT)
	b.add_theme_color_override("font_focus_color", Utils.UI_GOLD_BRIGHT)
	b.set_meta("row_id", str(row.get("id", "")))
	b.set_meta("door", row.get("door", {}))
	b.pressed.connect(_on_row_pressed.bind(b))
	b.gui_input.connect(_on_row_gui_input.bind(b))
	holder.add_child(b)
	# Row IC, Session 3 (§4): a row with more than one door (the jealous man's:
	# [Give him an order] [Set him on his own]) shows each as a small button.
	var doors = row.get("doors", [])
	if doors is Array:
		for d in doors:
			if not (d is Dictionary) or str(d.get("label", "")) == "":
				continue
			var extra := _make_corner("Door_" + str(d.get("label", "")).replace(" ", "_"),
				str(d.get("label", "")), str(d.get("label", "")))
			extra.pressed.connect(func(): door_pressed.emit(d.get("door", {}), str(row.get("id", ""))))
			holder.add_child(extra)
	var x := _make_corner("SetAside", "×", "Set this aside for the turn (Delete on the row)")
	x.pressed.connect(set_aside.bind(str(row.get("id", ""))))
	holder.add_child(x)
	_row_buttons.append(b)
	return holder


func _fill_one_line(peace_text: String, war_text: String, standing: Array) -> void:
	if standing.is_empty():
		# no matter stands: the aim — or, on a board with no Congress, the war
		var which := "peace" if peace_text != "" else "war"
		_line.text = ("THE PEACE — " + peace_text) if which == "peace" else ("THE WAR — " + war_text)
		_line.tooltip_text = peace_text if which == "peace" else war_text
		_line.set_meta("row", {})
		_line.set_meta("which", which)
		_line.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
		return
	var first: Dictionary = standing[0]
	_line.text = "TO DECIDE (%d) — %s" % [standing.size(), str(first.get("text", ""))]
	var tip := PackedStringArray()
	for i in standing.size():
		tip.append("%d. %s" % [i + 1, str((standing[i] as Dictionary).get("text", ""))])
		var said := VoiceLine.plain_text(str((standing[i] as Dictionary).get("speaker", "")),
				str((standing[i] as Dictionary).get("says", "")))
		if said != "":
			tip.append("    " + said)
	_line.tooltip_text = "\n".join(tip)
	_line.set_meta("row", first)
	var bites := int(first.get("tier", 0)) == BITES
	_line.add_theme_color_override("font_color",
			Color.html("#" + Utils.COLOR_WARNING) if bites else Utils.toned(Utils.UI_TEXT_DIM))


# ---------------------------------------------------------------- the presses

func _on_line_pressed(which: String) -> void:
	var part = _desk.get(which, {})
	if part is Dictionary and part.get("door", {}) is Dictionary and not (part.get("door", {}) as Dictionary).is_empty():
		door_pressed.emit(part.get("door", {}), which)


func _on_row_pressed(b: Button) -> void:
	var door = b.get_meta("door", {})
	if door is Dictionary and not (door as Dictionary).is_empty():
		door_pressed.emit(door, str(b.get_meta("row_id", "")))


func _on_row_gui_input(event: InputEvent, b: Button) -> void:
	var key := event as InputEventKey
	if key != null and key.pressed and not key.echo and key.keycode == KEY_DELETE:
		accept_event()
		# The row goes and the keyboard must not go with it (the review: the
		# focus fell to nothing): the row that takes its place holds it, or
		# the last one, or - with none left - the host takes it back.
		var at: int = _row_buttons.find(b)
		set_aside(str(b.get_meta("row_id", "")))
		var next: Button = null
		for i in range(_row_buttons.size()):
			if is_instance_valid(_row_buttons[i]) and (next == null or i <= at):
				next = _row_buttons[i]
		if next != null and next.is_visible_in_tree():
			next.grab_focus()
		else:
			focus_released.emit()


func _on_one_line_pressed() -> void:
	var row = _line.get_meta("row", {})
	if row is Dictionary and (row as Dictionary).get("door", {}) is Dictionary \
			and not ((row as Dictionary).get("door", {}) as Dictionary).is_empty():
		door_pressed.emit((row as Dictionary).get("door", {}), str((row as Dictionary).get("id", "")))
	else:
		_on_line_pressed(str(_line.get_meta("which", "peace")))


func _on_more_pressed() -> void:
	_expanded = not _expanded
	_rebuild()


func _on_fold_pressed() -> void:
	_folded = not _folded
	_rebuild()

extends Control
class_name MarshalChipRow

# =============================================================================
# INK & IRON - The marshal row (Session UI-6, November 13, 2026)
# =============================================================================
# The command desk's row of our marshals in the field: who has nothing to do
# shows BEFORE End Turn asks (the plan's decision 9), and each marshal is one
# click from the map. Three forms, set by the host (main.gd) with the desk's:
#
#   "row"   the desk: one line - the idle first, in gilt; each chip his likeness
#           (his monogram where none is shipped), his name and his state's glyph
#           in its tone; a "+N" chip for those that do not fit (the Generals).
#   "grid"  the 32:9 desk's column: two columns of larger likenesses, at most
#           GRID_ROWS rows, then "+N".
#   "idle"  the slim bar (the compact view): one "● N idle" chip - the next idle
#           marshal, as `.` is - hidden while no one is idle.
#
# The row judges nothing: the host hands it rows of {key, view, status} read by
# the shared kit (scripts/marshal_state.gd), and every click is a signal the
# host routes (select him, open his card, the Generals, the next idle). No chip
# takes the keyboard: the command line keeps it. The chips are laid out by hand
# to the width the desk gives, so the row's minimum width never depends on how
# many marshals there are and the row can never widen the window.
# =============================================================================

signal marshal_pressed(key: String)
signal marshal_double_pressed(key: String)
signal more_pressed()
signal idle_pressed()
# Row IC, directives: a named army's chip - the host selects that army's corps.
signal army_pressed(name: String)

const MarshalKit := preload("res://scripts/marshal_state.gd")

const MODES := ["row", "grid", "idle"]
const ROW_H := 30.0          # a row chip: a 22-px likeness beside his name
# Session UI-6 (the lead's wave-1 shoot): the 32:9 column's likenesses were too
# small for it — a grid chip is a 40 x 50 portrait (the Generals' roster's
# own) and his name at the body's size.
const GRID_H := 58.0         # a grid chip: the 50-px likeness in its 1-px ring, a little air
const PORTRAIT_ROW := 22.0
const PORTRAIT_GRID := Vector2(40.0, 50.0)
const GLYPH_PX := 16.0       # the smallest stat glyph that renders
const DOT_PX := 8.0
const GAP := 4.0
const PAD := 6.0
const GRID_ROWS := 6
const GRID_COLUMNS := 2
const ARMY_H := 30.0         # Row IC, directives: an army chip (a button with its name and corps)

var _mode := "row"
var _rows: Array = []        # [{key, view, status}], the idle first
var _selected := ""
var _signature := ""
var _chips: Array = []       # [Button], in _rows order
var _more: Button = null
var _idle_chip: Button = null
var _hush := ""              # a double-click's key: its release must not select him again
var _laying_out := false
var _armies: Array = []      # Row IC, directives: [{name, members, members_shown, in_field}]
var _army_signature := ""
var _selected_army := ""
var _army_chips: Array = []  # [Button], in _armies order


func _init() -> void:
	name = "MarshalRow"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	clip_contents = true
	visible = false


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED or what == NOTIFICATION_THEME_CHANGED:
		_layout()
	elif what == NOTIFICATION_ENTER_TREE:
		_layout.call_deferred()


# ---------------------------------------------------------------- the API

func set_mode(mode: String) -> void:
	"""The desk's form: "row", "grid" or "idle" (anything else reads "row")."""
	var want: String = mode if mode in MODES else "row"
	if want == _mode:
		return
	_mode = want
	_rebuild()


func get_mode() -> String:
	return _mode


func set_rows(rows: Array) -> void:
	"""The marshals in the field, as [{key, view, status}] (MarshalState's view
	and status), in the board's order; the idle stand first. A board that
	changed nothing the row shows rebuilds nothing (no hover lost to a refresh)."""
	var sorted := _idle_first(rows)
	var sig := _signature_of(sorted)
	if sig == _signature:
		return
	_signature = sig
	_rows = sorted
	_rebuild()


func set_selected(key: String) -> void:
	"""The marshal the map has selected ("" for none) wears the bright rim."""
	if key == _selected:
		return
	_selected = key
	for chip in _chips:
		if is_instance_valid(chip):
			_dress(chip)


func set_armies(rows: Array) -> void:
	"""Row IC, directives: the named armies, as [{name, members, members_shown,
	in_field}]; an empty Array when there are none. A reply that changes nothing
	rebuilds nothing."""
	var clean: Array = []
	for r in rows:
		if r is Dictionary and str(r.get("name", "")) != "":
			clean.append(r)
	var sig := _army_signature_of(clean)
	if sig == _army_signature:
		return
	_army_signature = sig
	_armies = clean
	_rebuild()


func set_selected_army(army_name: String) -> void:
	"""The army the map's selected group is exactly ("" for none) wears the bright rim."""
	if army_name == _selected_army:
		return
	_selected_army = army_name
	for chip in _army_chips:
		if is_instance_valid(chip):
			_dress_army(chip)


func shown_armies() -> Array:
	"""The names whose army chips stand visible now (read by the harness)."""
	var out: Array = []
	for chip in _army_chips:
		if is_instance_valid(chip) and chip.visible:
			out.append(str(chip.get_meta("army", "")))
	return out


func idle_count() -> int:
	var n := 0
	for r in _rows:
		if bool(_status_of(r).get("idle", false)):
			n += 1
	return n


func shown_keys() -> Array:
	"""The keys whose chips stand on the row now, in order (read by the harness)."""
	var out: Array = []
	for chip in _chips:
		if is_instance_valid(chip) and chip.visible:
			out.append(str(chip.get_meta("key", "")))
	return out


# ---------------------------------------------------------------- building

func _rebuild() -> void:
	for chip in _chips:
		_drop(chip)
	_chips.clear()
	for achip in _army_chips:
		_drop(achip)
	_army_chips.clear()
	_drop(_more)
	_more = null
	_drop(_idle_chip)
	_idle_chip = null
	if _mode == "idle":
		var n := idle_count()
		if n > 0:
			_idle_chip = _make_idle_chip(n)
			add_child(_idle_chip)
	else:
		var grid := _mode == "grid"
		for a in _armies:
			var achip := _make_army_chip(a)
			add_child(achip)
			_army_chips.append(achip)
		for r in _rows:
			var chip := _make_chip(r, grid)
			add_child(chip)
			_chips.append(chip)
		if not _rows.is_empty():
			_more = _make_more_chip()
			add_child(_more)
	_layout()


func _drop(node) -> void:
	if node != null and is_instance_valid(node):
		if node.get_parent() == self:
			remove_child(node)
		node.queue_free()


func _make_chip(row: Dictionary, grid: bool) -> Button:
	var key := str(row.get("key", ""))
	var st := _status_of(row)
	var chip := Button.new()
	chip.name = "Chip_" + key
	chip.text = ""
	chip.focus_mode = Control.FOCUS_NONE
	chip.mouse_filter = Control.MOUSE_FILTER_STOP
	chip.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	chip.clip_contents = true
	chip.set_meta("key", key)
	chip.set_meta("idle", bool(st.get("idle", false)))
	chip.tooltip_text = _tip(key, _view_of(row), st)
	var box := HBoxContainer.new()
	box.name = "Box"
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_theme_constant_override("separation", 4)
	box.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	box.offset_left = PAD
	box.offset_right = -PAD
	chip.add_child(box)
	box.add_child(_likeness(key, PORTRAIT_GRID if grid else Vector2(PORTRAIT_ROW, PORTRAIT_ROW), st))
	var name_label := Label.new()
	name_label.name = "Name"
	name_label.text = Utils.display_marshal_name(key)
	if not grid:
		name_label.theme_type_variation = &"Caption"   # the grid's names stand at the body's size
	name_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	name_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if grid:
		name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		name_label.clip_text = true
		name_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	box.add_child(name_label)
	box.add_child(_state_mark(st))
	chip.pressed.connect(_on_chip_pressed.bind(key))
	chip.gui_input.connect(_on_chip_gui_input.bind(key))
	_dress(chip)
	return chip


func _likeness(key: String, px: Vector2, st: Dictionary) -> Control:
	"""His likeness (or his monogram) in a ring of his state's tone, `px` its
	size (square on the row, a portrait's 4:5 in the grid)."""
	var ring := PanelContainer.new()
	ring.name = "Likeness"
	ring.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ring.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(Utils.UI_INK_NAVY, 0.85)
	sb.border_color = Color(_tone(st), 0.9)
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(2)
	sb.set_content_margin_all(1)
	ring.add_theme_stylebox_override("panel", sb)
	var holder := Control.new()
	holder.custom_minimum_size = px
	holder.clip_contents = true
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ring.add_child(holder)
	var path: String = MarshalKit.portrait_path(key)
	var tex = load(path) if path != "" else null
	if tex is Texture2D:
		var pic := TextureRect.new()
		pic.texture = tex
		pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		pic.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.add_child(pic)
	else:
		var mono := Label.new()
		mono.text = MarshalKit.monogram(key)
		mono.theme_type_variation = &"Caption"
		mono.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		mono.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		mono.add_theme_color_override("font_color", Utils.UI_GOLD)
		mono.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		mono.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.add_child(mono)
	return ring


func _state_mark(st: Dictionary) -> Control:
	"""His state: its glyph in its tone - or, for the idle, the gilt dot."""
	var glyph_name := str(st.get("glyph", ""))
	if glyph_name == "":
		var dot := Panel.new()
		dot.name = "IdleDot"
		dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
		dot.custom_minimum_size = Vector2(DOT_PX, DOT_PX)
		dot.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var sb := StyleBoxFlat.new()
		sb.bg_color = Utils.UI_GOLD_BRIGHT
		sb.set_corner_radius_all(int(DOT_PX))
		dot.add_theme_stylebox_override("panel", sb)
		return dot
	var g := TextureRect.new()
	g.name = "StateGlyph"
	g.texture = load(Utils.glyph(glyph_name))
	g.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	g.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	g.custom_minimum_size = Vector2(GLYPH_PX, GLYPH_PX)
	g.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	g.modulate = _tone(st)
	g.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return g


func _make_army_chip(a: Dictionary) -> Button:
	"""Row IC, directives: one army's chip - its name and its corps in the field."""
	var army_name := str(a.get("name", ""))
	var in_field := int(a.get("in_field", 0))
	var b := Button.new()
	b.name = "Army_" + army_name
	b.focus_mode = Control.FOCUS_NONE
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	b.theme_type_variation = &"CaptionButton"
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.clip_contents = true
	# "· 2 corps" (the directives' blind reading 1: "Army of Italy · 2" read as a
	# heading, not a chip, to one reader of three)
	b.text = "%s · %d corps" % [army_name, in_field]
	b.set_meta("army", army_name)
	if in_field <= 0:
		b.disabled = true
		b.modulate = Color(1, 1, 1, 0.5)
		b.tooltip_text = "No corps of the %s is in the field." % army_name
	else:
		var names := PackedStringArray()
		for m in a.get("members_shown", []):
			names.append(str(m))
		var who := ""
		if names.size() == 1:
			who = names[0]
		elif names.size() > 1:
			who = ", ".join(names.slice(0, names.size() - 1)) + " and " + names[names.size() - 1]
		b.tooltip_text = ("The %s: %s. Press to select its corps — then click a province to send them,"
			+ " or use the card's Hold, Fortify or Drill.") % [army_name, who]
		# Row IC, Session 3b: an army with a TASK says so on its chip — its
		# commander is on his own and the rest follow him.
		var task = a.get("task", {})
		if task is Dictionary and str((task as Dictionary).get("line", "")) != "":
			b.text += " · on its own"
			var followers = (task as Dictionary).get("followers", [])
			var n: int = (followers as Array).size() if followers is Array else 0
			var men := "nobody follows him yet" if n == 0 else (
				"1 man follows him" if n == 1 else (str(n) + " men follow him"))
			b.tooltip_text = ("The %s is on its own: %s. %s commands, on his own; %s. "
				+ "Press to select its corps.") % [army_name,
				str((task as Dictionary).get("words", "")), str((task as Dictionary).get("lead_shown", "")), men]
		var named := str(a.get("commander", ""))
		if named != "" and not (task is Dictionary and str((task as Dictionary).get("line", "")) != ""):
			b.tooltip_text += " " + Utils.humanize_entity_name(named) + " is named to command it."
	b.pressed.connect(_on_army_pressed.bind(army_name))
	_dress_army(b)
	return b


func _dress_army(b: Button) -> void:
	var picked := str(b.get_meta("army", "")) == _selected_army and _selected_army != ""
	var rim := Color(Utils.UI_GOLD, 0.6)
	var fill := Color(Utils.UI_PANEL_BG, 0.82)
	var ink: Color = Utils.UI_GOLD
	var width := 1
	if picked:
		rim = Utils.UI_GOLD_BRIGHT
		fill = Utils.UI_ACTIVE_TAB_BG
		ink = Utils.UI_GOLD_BRIGHT
		width = 2
	b.add_theme_stylebox_override("normal", _box(fill, rim, width))
	b.add_theme_stylebox_override("disabled", _box(fill, rim, width))
	b.add_theme_stylebox_override("hover", _box(Color(Utils.UI_GOLD, 0.24), Utils.UI_GOLD_BRIGHT, width))
	b.add_theme_stylebox_override("pressed", _box(Utils.UI_ACTIVE_TAB_BG, Utils.UI_GOLD_BRIGHT, 2))
	b.add_theme_stylebox_override("hover_pressed", _box(Utils.UI_ACTIVE_TAB_BG, Utils.UI_GOLD_BRIGHT, 2))
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	for c in ["font_color", "font_hover_color", "font_pressed_color", "font_disabled_color"]:
		b.add_theme_color_override(c, ink)


func _on_army_pressed(army_name: String) -> void:
	army_pressed.emit(army_name)


func _make_more_chip() -> Button:
	var b := Button.new()
	b.name = "MoreChip"
	b.focus_mode = Control.FOCUS_NONE
	b.theme_type_variation = &"CaptionButton"
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.visible = false
	b.pressed.connect(func(): more_pressed.emit())
	return b


func _make_idle_chip(n: int) -> Button:
	var b := Button.new()
	b.name = "IdleChip"
	b.focus_mode = Control.FOCUS_NONE
	b.theme_type_variation = &"CaptionButton"
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.text = "● %d idle" % n
	b.tooltip_text = (Utils.plural(n, "marshal") + " with nothing to do - click for the next of them"
		+ " (the . key on an empty line)")
	b.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	b.add_theme_color_override("font_hover_color", Utils.UI_GOLD_BRIGHT)
	b.pressed.connect(func(): idle_pressed.emit())
	return b


func _dress(chip: Button) -> void:
	"""A chip's face: gilt for the idle, the bright rim for the selected."""
	var key := str(chip.get_meta("key", ""))
	var idle := bool(chip.get_meta("idle", false))
	var rim := Color(Utils.UI_GOLD, 0.28)
	var fill := Color(Utils.UI_PANEL_BG, 0.82)
	var ink: Color = Utils.toned(Utils.UI_TEXT_DIM)
	var width := 1
	if idle:
		rim = Color(Utils.UI_GOLD, 0.9)
		fill = Color(Utils.UI_GOLD, 0.16)
		ink = Utils.UI_GOLD_BRIGHT
	if key != "" and key == _selected:
		rim = Utils.UI_GOLD_BRIGHT
		fill = Utils.UI_ACTIVE_TAB_BG
		ink = Utils.UI_GOLD_BRIGHT
		width = 2
	chip.add_theme_stylebox_override("normal", _box(fill, rim, width))
	chip.add_theme_stylebox_override("disabled", _box(fill, rim, width))
	chip.add_theme_stylebox_override("hover", _box(Color(Utils.UI_GOLD, 0.24), Utils.UI_GOLD_BRIGHT, width))
	chip.add_theme_stylebox_override("pressed", _box(Utils.UI_ACTIVE_TAB_BG, Utils.UI_GOLD_BRIGHT, 2))
	chip.add_theme_stylebox_override("hover_pressed", _box(Utils.UI_ACTIVE_TAB_BG, Utils.UI_GOLD_BRIGHT, 2))
	chip.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	var label := chip.get_node_or_null("Box/Name") as Label
	if label != null:
		label.add_theme_color_override("font_color", ink)


static func _box(fill: Color, rim: Color, width: int) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.border_color = rim
	sb.set_border_width_all(width)
	sb.set_corner_radius_all(3)
	return sb


# ---------------------------------------------------------------- the layout

func _layout() -> void:
	if _laying_out:
		return
	_laying_out = true
	match _mode:
		"idle":
			_layout_idle()
		"grid":
			_layout_grid()
		_:
			_layout_row()
	_laying_out = false


func _layout_row() -> void:
	"""One line: the chips that fit the width, then "+N" for the rest."""
	visible = not _chips.is_empty() or not _army_chips.is_empty()
	if not visible:
		custom_minimum_size = Vector2.ZERO
		return
	var room := size.x
	# Row IC, directives: the armies stand first and are never pushed into "+N"
	# (one that cannot fit the width is hidden; the row never widens).
	var ax := 0.0
	for achip in _army_chips:
		var aw := ceilf(achip.get_combined_minimum_size().x)
		achip.visible = ax + aw <= room or ax == 0.0
		if achip.visible:
			achip.position = Vector2(ax, 0.0)
			achip.size = Vector2(aw if ax > 0.0 else minf(aw, maxf(room, 0.0)), ROW_H)
			ax += aw + GAP
	room = maxf(room - ax, 0.0)
	var widths: Array = []
	var total := 0.0
	for chip in _chips:
		var w := _chip_width(chip)
		widths.append(w)
		total += w + GAP
	total -= GAP
	var shown := _chips.size()
	if total > room:
		var more_w := _more_width(_chips.size())
		shown = 0
		var used := 0.0
		while shown < _chips.size() and used + float(widths[shown]) + GAP + more_w <= room:
			used += float(widths[shown]) + GAP
			shown += 1
	custom_minimum_size = Vector2(_more_width(_chips.size()), ROW_H)
	var x := ax
	for i in _chips.size():
		var chip: Button = _chips[i]
		chip.visible = i < shown
		if i < shown:
			chip.position = Vector2(x, 0.0)
			chip.size = Vector2(float(widths[i]), ROW_H)
			x += float(widths[i]) + GAP
	_place_more(_chips.size() - shown, Rect2(x, 0.0, _more_width(_chips.size() - shown), ROW_H))


func _layout_grid() -> void:
	"""Two columns of likenesses, at most GRID_ROWS rows; past that the last
	cell is "+N"."""
	visible = not _chips.is_empty() or not _army_chips.is_empty()
	if not visible:
		custom_minimum_size = Vector2.ZERO
		return
	# Row IC, directives: army chips stand at the top as full-width rows; the
	# marshal grid below gives up as many rows as they take, so the column's
	# room is kept.
	var top := 0.0
	for achip in _army_chips:
		achip.visible = true
		achip.position = Vector2(0.0, top)
		achip.size = Vector2(maxf(size.x, 0.0), ARMY_H)
		top += ARMY_H + GAP
	var taken := ceili(top / (GRID_H + GAP))
	var cap := maxi(GRID_ROWS - taken, 1) * GRID_COLUMNS
	var n := _chips.size()
	var shown := n if n <= cap else cap - 1
	var cells := shown + (1 if shown < n else 0)
	var rows := ceili(float(cells) / float(GRID_COLUMNS))
	var grid_h := 0.0
	if rows > 0:
		grid_h = float(rows) * GRID_H + float(rows - 1) * GAP
	elif top > 0.0:
		top -= GAP
	custom_minimum_size = Vector2(0.0, top + grid_h)
	var cw := floorf((size.x - GAP * float(GRID_COLUMNS - 1)) / float(GRID_COLUMNS))
	for i in n:
		var chip: Button = _chips[i]
		chip.visible = i < shown
		if i < shown:
			chip.position = _cell(i, cw) + Vector2(0.0, top)
			chip.size = Vector2(cw, GRID_H)
	_place_more(n - shown, Rect2(_cell(shown, cw) + Vector2(0.0, top), Vector2(cw, GRID_H)))


func _layout_idle() -> void:
	visible = _idle_chip != null
	if _idle_chip == null:
		custom_minimum_size = Vector2.ZERO
		return
	var s := _idle_chip.get_combined_minimum_size()
	custom_minimum_size = s
	_idle_chip.position = Vector2.ZERO
	_idle_chip.size = Vector2(maxf(s.x, size.x), maxf(s.y, size.y))


func _cell(i: int, cw: float) -> Vector2:
	var col := i % GRID_COLUMNS
	var row := floori(float(i) / float(GRID_COLUMNS))
	return Vector2(float(col) * (cw + GAP), float(row) * (GRID_H + GAP))


func _place_more(hidden: int, rect: Rect2) -> void:
	if _more == null or not is_instance_valid(_more):
		return
	_more.visible = hidden > 0
	if hidden <= 0:
		return
	_more.text = "+%d" % hidden
	# S14G-X78: never a bare key in brackets (a bare letter types into the line)
	_more.tooltip_text = (Utils.plural(hidden, "marshal")
		+ " more - every marshal in the Generals (press G, or Alt+G while you type)")
	_more.position = rect.position
	_more.size = rect.size


func _chip_width(chip: Button) -> float:
	var box := chip.get_node_or_null("Box") as Control
	if box == null:
		return 80.0
	return ceilf(box.get_combined_minimum_size().x + 2.0 * PAD)


func _more_width(hidden: int) -> float:
	if _more == null or not is_instance_valid(_more):
		return 0.0
	_more.text = "+%d" % maxi(hidden, 1)
	return ceilf(_more.get_combined_minimum_size().x)


# ---------------------------------------------------------------- the clicks

func _on_chip_gui_input(event: InputEvent, key: String) -> void:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed or mb.button_index != MOUSE_BUTTON_LEFT:
		return
	if mb.double_click:
		_hush = key
		marshal_double_pressed.emit(key)
	else:
		_hush = ""


func _on_chip_pressed(key: String) -> void:
	if _hush == key:
		_hush = ""
		return
	marshal_pressed.emit(key)


# ---------------------------------------------------------------- reading a row

func _tip(key: String, view: Dictionary, st: Dictionary) -> String:
	var lines := PackedStringArray()
	lines.append(Utils.display_marshal_name(key) + " — " + str(st.get("detail", "")))
	var where := Utils.humanize_entity_name(str(view.get("location", "")))
	var men := int(view.get("strength", 0))
	var place := PackedStringArray()
	if where != "":
		place.append(where)
	if men > 0:
		place.append(Utils.format_number(men) + " men")
	if not place.is_empty():
		lines.append(" · ".join(place))
	lines.append("Click: select him on the map · double-click: his card in the Generals")
	return "\n".join(lines)


static func _status_of(row) -> Dictionary:
	if not (row is Dictionary):
		return {}
	var st = row.get("status", {})
	if st is Dictionary:
		return st
	return {}


static func _view_of(row) -> Dictionary:
	if not (row is Dictionary):
		return {}
	var v = row.get("view", {})
	if v is Dictionary:
		return v
	return {}


static func _tone(st: Dictionary) -> Color:
	var hex := str(st.get("tone", Utils.COLOR_GOLD))
	if not Color.html_is_valid(hex):
		hex = Utils.COLOR_GOLD
	return Color.html("#" + hex)


static func _idle_first(rows: Array) -> Array:
	var idle: Array = []
	var busy: Array = []
	for r in rows:
		if not (r is Dictionary) or str(r.get("key", "")) == "":
			continue
		if bool(_status_of(r).get("idle", false)):
			idle.append(r)
		else:
			busy.append(r)
	return idle + busy


static func _signature_of(rows: Array) -> String:
	var parts := PackedStringArray()
	for r in rows:
		var st := _status_of(r)
		var view := _view_of(r)
		parts.append(str(r.get("key", "")) + ":" + str(st.get("key", "")) + ":"
			+ str(st.get("detail", "")) + ":" + str(int(view.get("strength", 0))))
	return ";".join(parts)


static func _army_signature_of(rows: Array) -> String:
	var parts := PackedStringArray()
	for r in rows:
		var shown := PackedStringArray()
		for m in r.get("members_shown", []):
			shown.append(str(m))
		# (Session 3b) its task and its named commander are on the chip too
		var task = r.get("task", {})
		var task_key := ""
		if task is Dictionary:
			task_key = str((task as Dictionary).get("line", "")) + "/" + str((task as Dictionary).get("lead", "")) \
				+ "/" + str((task as Dictionary).get("followers", []))
		parts.append(str(r.get("name", "")) + ":" + str(int(r.get("in_field", 0))) + ":" + ",".join(shown)
			+ ":" + task_key + ":" + str(r.get("commander", "")))
	return ";".join(parts)

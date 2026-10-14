extends Panel
class_name ResizeGrip

# =============================================================================
# PROJECT SOVEREIGN — the one resize grip (UXR-2 "the layout law", Pre-Deploy S9)
# =============================================================================
# "Only some boxes are adjustable": until UXR-2 the command window was the one
# surface with a grip (main.gd, UI-2 Part 1). This is that grip, shared.
#
# A surface is ANCHORED (a viewport fraction with min/max) or CLAMPED-AND-
# GRIPPED: an authored rect `Utils.clamp_centered_panel` shrinks and a grip
# resizes, the size remembered in `ui_settings.cfg`. Three ways to host one:
#
#   ResizeGrip.make(corner, tooltip)
#       Visuals only (HOST mode). The host wires `gui_input` and places it —
#       the command window keeps its own fixed-corner geometry in main.gd.
#   ResizeGrip.attach_centered(panel, name)
#       A centre-anchored clamped panel (the six top-bar screens). The grip
#       sits on the panel's bottom-right corner; the panel grows about its
#       centre. The player's size rides the panel as the `clamp_user_size`
#       meta, which `clamp_centered_panel` reads in place of the authored
#       rect — so the clamp still fits it to any viewport, display-only.
#   ResizeGrip.attach_edge(panel, name, corner)
#       An edge-anchored HUD panel (the war-status panel). The opposite
#       corner is fixed at press; the host applies `resize_requested`.
#
# A press never reaches the screen's close-on-click overlay: the grip is the
# panel's LAST sibling (drawn above the overlay), stops the mouse and accepts
# every left-button event. A click that does not move is not a resize, and a
# double-click returns the authored size and forgets the stored one.
#
# Display-only (Golden Rule 6): nothing here touches game state.
# =============================================================================

signal resize_requested(new_size: Vector2)
signal resize_committed(new_size: Vector2)
signal reset_requested

const GRIP_SIZE := 24.0
const GROUP := "resize_grips"
const USER_SIZE_META := "clamp_user_size"
# A press-and-release within this many logical px is a click, not a drag.
const MOVE_THRESHOLD := 2.0
# UXR3-74: every grip says what it does, the command window's too.
const TOOLTIP := "Drag to resize · double-click to restore"

enum Corner { TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT }
enum Mode { HOST, CENTERED, EDGE }

var corner: int = Corner.BOTTOM_RIGHT
var store_name := ""
var _mode: int = Mode.HOST
var _target: Control = null
var _dragging := false
var _moved := false
var _press_at := Vector2.ZERO
var _grab_offset := Vector2.ZERO
var _fixed_corner := Vector2.ZERO


static func make(grip_corner: int, tooltip: String) -> Panel:
	"""The grip's look, with no behaviour (UXR3-74, Pre-Deploy S12 part 2):
	a borderless corner hatch, three diagonal gold strokes, which says
	"drag" where the boxed four-arrow tile it replaces said "expand" and read
	as a button. The 24-px hit square stays centred on the panel's corner;
	the strokes are drawn in its INNER quadrant only, inside the panel's
	padding, so the grip never sits on content (UXR3-F4)."""
	var grip := ResizeGrip.new()
	grip.corner = grip_corner
	grip.custom_minimum_size = Vector2(GRIP_SIZE, GRIP_SIZE)
	grip.size = Vector2(GRIP_SIZE, GRIP_SIZE)
	grip.mouse_filter = Control.MOUSE_FILTER_STOP
	grip.mouse_default_cursor_shape = (Control.CURSOR_BDIAGSIZE
			if grip_corner in [Corner.TOP_RIGHT, Corner.BOTTOM_LEFT]
			else Control.CURSOR_FDIAGSIZE)
	grip.tooltip_text = tooltip
	grip.add_theme_stylebox_override("panel", StyleBoxEmpty.new())
	return grip


# The hatch: three 1-px strokes across the corner, 2.5 / 6 / 9.5 px from it,
# inset 2.5 px from the panel's two edges, clear of a rounded border (so all
# of it lies in the 12-px inner quadrant), UI_GOLD at 0.7 alpha.
const HATCH_STEPS: Array[float] = [2.5, 6.0, 9.5]
const HATCH_INSET := 2.5
const HATCH_WIDTH := 1.0
const HATCH_ALPHA := 0.7


func _draw() -> void:
	# The panel's corner is the grip's centre; `inward` points into the panel.
	var c := size * 0.5
	var inward := Vector2(
			1.0 if corner in [Corner.TOP_LEFT, Corner.BOTTOM_LEFT] else -1.0,
			1.0 if corner in [Corner.TOP_LEFT, Corner.TOP_RIGHT] else -1.0)
	var col := Color(Utils.UI_GOLD, HATCH_ALPHA)
	for k in HATCH_STEPS:
		var a := c + inward * Vector2(HATCH_INSET, HATCH_INSET + k)
		var b := c + inward * Vector2(HATCH_INSET + k, HATCH_INSET)
		draw_line(a, b, col, HATCH_WIDTH, true)


static func attach_centered(panel: Control, panel_name: String) -> Panel:
	"""A grip on a centre-anchored clamped panel's bottom-right corner. Call
	once from the screen's `_ready`; the screen's own open path keeps its
	`Utils.clamp_centered_panel($PanelContainer)`, which reads the size."""
	var grip: ResizeGrip = make(Corner.BOTTOM_RIGHT,
			TOOLTIP)
	grip._bind(panel, panel_name, Mode.CENTERED)
	grip.load_stored_size()
	return grip


static func attach_edge(panel: Control, panel_name: String, grip_corner: int) -> Panel:
	"""A grip on an edge-anchored panel's `grip_corner`. The host listens to
	`resize_requested` / `resize_committed` / `reset_requested` and lays the
	panel out itself (its own anchors decide which corner stays put)."""
	var grip: ResizeGrip = make(grip_corner,
			TOOLTIP)
	grip._bind(panel, panel_name, Mode.EDGE)
	return grip


func _bind(panel: Control, panel_name: String, mode: int) -> void:
	_target = panel
	store_name = panel_name
	_mode = mode
	name = "ResizeGrip"
	add_to_group(GROUP)
	# The panel's LAST sibling: drawn above the screen's overlay and the panel.
	panel.get_parent().add_child.call_deferred(self)
	gui_input.connect(_on_input)
	panel.item_rect_changed.connect(_queue_reposition)
	panel.visibility_changed.connect(_queue_reposition)
	var host := panel.get_parent()
	if host is CanvasLayer:
		host.visibility_changed.connect(_on_host_visibility_changed)


func load_stored_size() -> void:
	"""The remembered size becomes the panel's clamp intent (or none)."""
	if _mode != Mode.CENTERED or _target == null:
		return
	if UiSettings.has_panel_size(store_name):
		_target.set_meta(USER_SIZE_META, UiSettings.get_panel_size(store_name, Vector2.ZERO))
	elif _target.has_meta(USER_SIZE_META):
		_target.remove_meta(USER_SIZE_META)


func _on_host_visibility_changed() -> void:
	# Re-read the store on every open (it fires inside show(), before the
	# open path's clamp), so a Reset layout made while the screen was shut
	# is honoured; a grip hidden mid-drag ends the drag.
	var host := _target.get_parent() if _target != null else null
	if host is CanvasLayer and host.visible:
		load_stored_size()
	elif _dragging:
		_finish_drag()
	_queue_reposition()


func _queue_reposition() -> void:
	reposition.call_deferred()


func reposition() -> void:
	if _target == null or not is_instance_valid(_target):
		return
	visible = _target.is_visible_in_tree()
	if not visible:
		return
	position = _corner_point(_target.get_global_rect(), corner) - size * 0.5


static func _corner_point(r: Rect2, c: int) -> Vector2:
	match c:
		Corner.TOP_LEFT:
			return r.position
		Corner.TOP_RIGHT:
			return Vector2(r.end.x, r.position.y)
		Corner.BOTTOM_LEFT:
			return Vector2(r.position.x, r.end.y)
	return r.end


static func _opposite(c: int) -> int:
	return 3 - c


func _on_input(event: InputEvent) -> void:
	if _mode == Mode.HOST or _target == null:
		return
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		accept_event()
		if event.pressed:
			if event.double_click:
				_dragging = false
				reset_to_authored()
				return
			var r := _target.get_global_rect()
			_dragging = true
			_moved = false
			# The event's own canvas position (its CanvasLayer's space, the
			# space get_global_rect() answers in) — never the OS cursor.
			_press_at = event.global_position
			_grab_offset = _corner_point(r, corner) - _press_at  # no jump on grab
			_fixed_corner = _corner_point(r, _opposite(corner))
		elif _dragging:
			_finish_drag()
	elif event is InputEventMouseMotion and _dragging:
		accept_event()
		var m: Vector2 = event.global_position
		if not _moved and m.distance_to(_press_at) > MOVE_THRESHOLD:
			_moved = true
		if _moved:
			_drag_to(m + _grab_offset)


func _limit(want: Vector2) -> Vector2:
	var lo: Vector2 = UiSettings.panel_min(store_name)
	var hi: Vector2 = UiSettings.panel_max(store_name)
	var floor_size := _target.get_combined_minimum_size()
	return Vector2(
		clampf(want.x, maxf(lo.x, floor_size.x), hi.x),
		clampf(want.y, maxf(lo.y, floor_size.y), hi.y))


func _drag_to(p: Vector2) -> void:
	var want: Vector2
	if _mode == Mode.CENTERED:
		# grow_*=2 keeps the centre, so the corner tracks the cursor exactly.
		want = 2.0 * (p - _target.get_global_rect().get_center()).abs()
	else:
		want = (p - _fixed_corner).abs()
	want = _limit(want)
	if _mode == Mode.CENTERED:
		_target.set_meta(USER_SIZE_META, want)
		Utils.clamp_centered_panel(_target)
	resize_requested.emit(want)


func _finish_drag() -> void:
	_dragging = false
	if not _moved:
		return  # a click is not a resize
	_moved = false
	# Store the size the player SAW: viewport-capped, minimum-floored.
	var shown := _target.size
	if _mode == Mode.CENTERED:
		_target.set_meta(USER_SIZE_META, shown)
	UiSettings.set_panel_size(store_name, shown)
	resize_committed.emit(shown)


func reset_to_authored() -> void:
	"""Double-click, and Reset layout (`call_group(GROUP, ...)`): the stored
	size is forgotten and the authored rect returns."""
	if _mode == Mode.HOST:
		return
	UiSettings.clear_panel_size(store_name)
	if _mode == Mode.CENTERED and _target != null and is_instance_valid(_target):
		if _target.has_meta(USER_SIZE_META):
			_target.remove_meta(USER_SIZE_META)
		if _target.is_visible_in_tree():
			Utils.clamp_centered_panel(_target)
	reset_requested.emit()
	_queue_reposition()

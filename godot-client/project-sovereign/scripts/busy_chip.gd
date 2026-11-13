extends PanelContainer
class_name BusyChip

# =============================================================================
# Session UI-5 (November 12, 2026) — the courier rides: a visible busy state.
# =============================================================================
# While an order, the enemy phase, a save or a load is out at the backend, the
# command line is disabled and the quill scribbles — but nothing on screen said
# so (the UX survey's gap 4). This framed chip stands above the command line
# with a quill that moves and one plain line: "Berthier reads the order…",
# "The courts of Europe move…", "Saving…", "Loading…".
#
# It shows for at least MIN_SHOW_S, so a fast answer does not flicker, and its
# glyph is still under Settings → Reduce motion. main.gd places it (`attach`)
# and drives it from `set_input_enabled`, the one seam every response passes.
# Display only: it reads nothing of the game.
# =============================================================================

const MIN_SHOW_S := 0.25
const WORDS := {
	"order": "Berthier reads the order…",
	"enemy": "The courts of Europe move…",
	"save": "Saving…",
	"load": "Loading…",
	"wait": "A moment, Sire…",
}

var _glyph: TextureRect
var _label: Label
var _shown_ms := 0
var _token := 0
var _bob: Tween
var _kind := ""


func _init() -> void:
	name = "BusyChip"
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_theme_stylebox_override("panel", Utils.gilt_frame(Utils.UI_POPUP_BG, Utils.UI_GOLD, Utils.FRAME_HAIRLINE, 8.0))
	var row := HBoxContainer.new()
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", 8)
	add_child(row)
	_glyph = TextureRect.new()
	_glyph.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_glyph.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_glyph.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_glyph.custom_minimum_size = Vector2(18, 18)
	_glyph.modulate = Utils.UI_GOLD
	var path := Utils.glyph("command")
	if ResourceLoader.exists(path):
		_glyph.texture = load(path)
	row.add_child(_glyph)
	_label = Label.new()
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label.add_theme_color_override("font_color", Utils.UI_GOLD)
	row.add_child(_label)


func kind() -> String:
	return _kind if visible else ""


func show_busy(kind_name: String = "order") -> void:
	_token += 1
	_kind = kind_name
	_label.text = str(WORDS.get(kind_name, WORDS["wait"]))
	if not visible:
		_shown_ms = Time.get_ticks_msec()
	visible = true
	_start_bob()


func hide_busy() -> void:
	if not visible:
		return
	_token += 1
	var held := (Time.get_ticks_msec() - _shown_ms) / 1000.0
	if held >= MIN_SHOW_S or not is_inside_tree():
		_finish(_token)
	else:
		var t := get_tree().create_timer(MIN_SHOW_S - held)
		t.timeout.connect(_finish.bind(_token))


func _finish(token: int) -> void:
	if token != _token:
		return
	visible = false
	_kind = ""
	if _bob != null and _bob.is_valid():
		_bob.kill()
	_glyph.rotation = 0.0


func _start_bob() -> void:
	if UiSettings.get_reduce_motion() or not is_inside_tree():
		return
	if _bob != null and _bob.is_valid():
		return
	_glyph.pivot_offset = _glyph.custom_minimum_size * 0.5
	_bob = create_tween().set_loops()
	_bob.tween_property(_glyph, "rotation", deg_to_rad(-14.0), 0.32).set_trans(Tween.TRANS_SINE)
	_bob.tween_property(_glyph, "rotation", deg_to_rad(10.0), 0.32).set_trans(Tween.TRANS_SINE)

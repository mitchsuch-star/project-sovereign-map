extends CanvasLayer
class_name ToastLayer

# =============================================================================
# Session UI-5 (November 12, 2026) — toasts: the client's own acts, said once.
# =============================================================================
# "Saved · September 1805", "Autosaved", "Loaded", "Map view: Political",
# "Help & Keys — F10", a rebound key. Game events never come here — they stay
# on the notice rail and in the log (the plan's decision 15).
# A gilt chip at the top centre, under the top bar; 2.5 s; three at most
# (a fourth pushes the oldest out); a repeat of the showing text refreshes it
# instead of stacking. Lazy, like AudioManager: the first `ToastLayer.say()`
# installs one layer under the root; a scene change keeps it.
# Layer 121 — above every dialog (101–119) and the mailbox (119), so a F5 under
# a letter still says it saved.
# =============================================================================

const LAYER := 121
const HOLD_S := 2.5
const FADE_S := 0.35
const MAX_TOASTS := 3
const TOP_MARGIN := 64.0

static var _layer_node: ToastLayer = null

var _column: VBoxContainer


static func say(text: String, glyph_name: String = "") -> void:
	"""Show one toast. Null-safe in a bare SceneTree (the parse harness)."""
	var inst := _inst()
	if inst == null:
		return
	# The layer enters the tree on a deferred add; a toast said before that
	# waits one deferred call behind it (its timers need the tree).
	if inst.is_inside_tree():
		inst._push(text, glyph_name)
	else:
		inst._push.call_deferred(text, glyph_name)


static func clear() -> void:
	var inst := _inst()
	if inst != null and inst._column != null:
		for child in inst._column.get_children():
			child.queue_free()


static func _inst() -> ToastLayer:
	if _layer_node != null and is_instance_valid(_layer_node):
		return _layer_node
	var ml := Engine.get_main_loop()
	if ml == null or not (ml is SceneTree):
		return null
	var root := (ml as SceneTree).root
	if root == null:
		return null
	_layer_node = ToastLayer.new()
	_layer_node.name = "ToastLayer"
	root.add_child.call_deferred(_layer_node)
	return _layer_node


func _init() -> void:
	layer = LAYER
	_column = VBoxContainer.new()
	_column.name = "Toasts"
	_column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_column.add_theme_constant_override("separation", 6)
	_column.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_column.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_column.position.y = TOP_MARGIN
	add_child(_column)


func _push(text: String, glyph_name: String) -> void:
	if text.strip_edges() == "":
		return
	for child in _column.get_children():
		if child.has_meta("toast_text") and str(child.get_meta("toast_text")) == text:
			_refresh(child)
			return
	while _column.get_child_count() >= MAX_TOASTS:
		var oldest := _column.get_child(0)
		_column.remove_child(oldest)
		oldest.queue_free()
	var chip := PanelContainer.new()
	chip.set_meta("toast_text", text)
	chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	chip.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	chip.add_theme_stylebox_override("panel", Utils.gilt_frame(Utils.UI_POPUP_BG, Utils.UI_GOLD, Utils.FRAME_HAIRLINE, 10.0))
	var row := HBoxContainer.new()
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", 8)
	chip.add_child(row)
	if glyph_name != "" and ResourceLoader.exists(Utils.glyph(glyph_name)):
		var icon := TextureRect.new()
		icon.texture = load(Utils.glyph(glyph_name))
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icon.custom_minimum_size = Vector2(18, 18)
		icon.modulate = Utils.UI_GOLD
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(icon)
	var label := Label.new()
	label.text = text
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override("font_color", Utils.UI_GOLD)
	row.add_child(label)
	_column.add_child(chip)
	_recentre()
	_refresh(chip)


func _refresh(chip: Control) -> void:
	chip.modulate.a = 1.0
	var token := int(chip.get_meta("toast_token", 0)) + 1
	chip.set_meta("toast_token", token)
	var t := get_tree().create_timer(HOLD_S)
	t.timeout.connect(_fade_due.bind(chip.get_instance_id(), token))


func _fade_due(chip_id: int, token: int) -> void:
	var chip = instance_from_id(chip_id)
	if not is_instance_valid(chip) or int(chip.get_meta("toast_token", 0)) != token:
		return
	if UiSettings.get_reduce_motion():
		_retire(chip_id, token)
		return
	var tw := (chip as Control).create_tween()
	tw.tween_property(chip, "modulate:a", 0.0, FADE_S)
	tw.tween_callback(_retire.bind(chip_id, token))


func _retire(chip_id: int, token: int) -> void:
	var chip = instance_from_id(chip_id)
	if is_instance_valid(chip) and int(chip.get_meta("toast_token", 0)) == token:
		chip.queue_free()
		_recentre.call_deferred()


func _recentre() -> void:
	if _column == null:
		return
	var view := get_viewport().get_visible_rect().size if get_viewport() != null else Vector2(1600, 900)
	_column.reset_size()
	_column.position = Vector2((view.x - _column.size.x) * 0.5, TOP_MARGIN)

extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN — The Battle Diorama (row BD)
# =============================================================================
# A framed carved-wood tableau of the battle just fought: two lines of the
# map's own oak figures on green baize inside a gilt frame, the loser's flank
# toppling in a cascade, standards falling (and — on a decisive field — taken
# across the centre line), an odometer counting the dead, and Berthier's
# verdict delivered last, like a gavel.
#
# Art direction is the eval memo §8 (docs/audits/BATTLE_DIORAMA_EVAL_2026_07_17.md):
# a Kriegsspiel tray, not a UI panel. One warm key light from upper-right
# (the direction baked into the sprites), long shadows, colour kept rare —
# wood everywhere, faction hue only on standards/coats the generator painted,
# red ONLY in the casualty tally.
#
# The player's line is ALWAYS the near (left) side, whoever attacked — a
# defeat reads as YOUR line breaking, not a mirrored enemy triumph (§7 Q6).
#
# CanvasLayer 121: above the enemy-phase dialog (118) so "⚔ View the field"
# opens over it; the pause menu cannot stack above it because a modal
# diorama blocks the ESC ladder while visible (same rule as every modal).
#
# Display-only (Golden Rule 6). Fed one self-contained payload
# (backend/game_logic/battle_diorama.py); never reads game state.
# =============================================================================

signal dismissed

# ── Geometry (design px; Utils.clamp_centered_panel shrinks on small screens)
const TRAY_W := 1000.0
const TRAY_H := 660.0
const STAGE_MARGIN_X := 26.0
const STAGE_TOP := 52.0
const STAGE_H := 380.0
const SHELF_H := 66.0
const FIGURE_PX := 58.0
const SHELF_FIGURE_PX := 44.0

# PT-D2: the backend's absence family (battle_diorama.py ABSENT_STATUSES)
# — statuses the shelf renders, never the line.
const ABSENT_STATUSES := ["failed_arrive", "refused", "out_of_reach"]

# ── Palette (colour rarity per the brief: wood, brass, baize; red = casualties)
const WOOD_BG := Color(0.165, 0.118, 0.078, 1.0)        # walnut tray
const WOOD_EDGE := Color(0.24, 0.175, 0.115, 1.0)
const BAIZE := Color(0.129, 0.208, 0.153, 1.0)          # green felt
const BAIZE_EDGE := Color(0.086, 0.145, 0.104, 1.0)
const BRASS := Color(0.72, 0.60, 0.36, 1.0)
const BRASS_DARK := Color(0.42, 0.33, 0.17, 1.0)
const ENGRAVE := Color(0.18, 0.13, 0.06, 1.0)           # cut into brass
const CRIMSON := Color(0.72, 0.20, 0.18, 1.0)
const BONE_HEX := "c9c2b2"
const GOLD_HEX := "d9c08c"

const FONT_ENGRAVED := "res://assets/fonts/Cinzel[wght].ttf"
const FONT_VOICE := "res://assets/fonts/IMFeENit28P.ttf"       # period italic
const FILIGREE := "res://assets/ui/ornaments/corner_floral_01.svg"
const WAX_SEAL := "res://assets/ui/ornaments/wax_seal.png"
const LAUREL := "res://assets/ui/ornaments/laurel_golden.svg"
const AUDIO_CANNON := "res://assets/audio/battle/cannon_thud.ogg"
const AUDIO_DRUM := "res://assets/audio/battle/drum_sting.wav"

# Figures per corps by arm — a line of foot, a squadron, a battery.
# NV-7 adds "ship": a squadron is three sail on the table, the same count
# the batteries get — a line of battle reads as a line, not a crowd.
const FIGURES_BY_ARM := {"infantry": 5, "cavalry": 4, "artillery": 3, "ship": 3}

# NV-7 — the sea. A fleet action plays on the same tray, on chart-blue
# instead of green felt: the tableau is still a war table, and the one
# thing it must say at a glance is "this is not a field".
const CHART_SEA := Color(0.098, 0.153, 0.216, 1.0)
const CHART_SEA_EDGE := Color(0.063, 0.098, 0.145, 1.0)

# ── State
var _data: Dictionary = {}
var _final := false            # sequence has settled (or was opened settled)
var _seq: Tween = null         # master cinematic tween
var _blocks_left: Array = []   # per-corps dicts (see _make_block)
var _blocks_right: Array = []
var _audio: AudioStreamPlayer = null

# Chrome nodes (built once in _ready)
var _root: Control = null
var _scrim: ColorRect = null
var _tray: PanelContainer = null
var _tray_inner: Control = null
var _stage: Control = null
var _stage_canvas: Control = null
var _vignette: TextureRect = null
var _lamp: TextureRect = null
var _clash_label: Label = null
var _banner: Label = null
var _sub_banner: Label = null
var _odo_left: Label = null
var _odo_right: Label = null
var _odo_left_cap: Label = null
var _odo_right_cap: Label = null
var _left_holder: Node2D = null
var _right_holder: Node2D = null
var _shelf_left: Control = null
var _shelf_right: Control = null
var _verdict: RichTextLabel = null
var _nameplate: PanelContainer = null
var _plate_name: Label = null
var _plate_sub: Label = null
var _seal: TextureRect = null
var _laurel_l: TextureRect = null
var _laurel_r: TextureRect = null
var _btn_close: Button = null
var _btn_replay: Button = null
var _skip_hint: Label = null

var _font_engraved: FontVariation = null
var _font_voice: Font = null


func _ready() -> void:
	hide()
	_build_chrome()


# ─────────────────────────────────────────────────────────────────────────────
# Public entry
# ─────────────────────────────────────────────────────────────────────────────

func show_diorama(data: Dictionary, cinematic := true) -> void:
	"""Open the tableau. cinematic=false renders the settled final frame
	instantly (repeat viewings must never drag — eval §7 Q1)."""
	# A prior cinematic's master tween holds live references to the shared
	# chrome (odometer labels) — kill it FIRST or a re-open mid-sequence
	# keeps ticking the old battle's numbers over the new frame.
	_kill_sequence()
	_data = data
	show()
	_populate(not cinematic)
	Utils.clamp_centered_panel(_tray)
	if cinematic:
		_play_cinematic()
	else:
		_enter_final(false)


# ─────────────────────────────────────────────────────────────────────────────
# Chrome — built once
# ─────────────────────────────────────────────────────────────────────────────

func _build_chrome() -> void:
	_font_engraved = FontVariation.new()
	_font_engraved.base_font = load(FONT_ENGRAVED)
	# 2003265652 == the OpenType 'wght' axis tag (same value main_theme.tres
	# uses for its Cinzel heading variation).
	_font_engraved.variation_opentype = {2003265652: 600}
	if ResourceLoader.exists(FONT_VOICE):
		_font_voice = load(FONT_VOICE)

	_root = Control.new()
	_root.name = "Root"
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_STOP
	_root.gui_input.connect(_on_root_input)
	add_child(_root)

	_scrim = ColorRect.new()
	_scrim.color = Color(0.0, 0.0, 0.0, 0.62)
	_scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(_scrim)

	_tray = PanelContainer.new()
	_tray.name = "Tray"
	_tray.set_anchors_preset(Control.PRESET_CENTER)
	_tray.offset_left = -TRAY_W / 2.0
	_tray.offset_top = -TRAY_H / 2.0
	_tray.offset_right = TRAY_W / 2.0
	_tray.offset_bottom = TRAY_H / 2.0
	_tray.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_tray.grow_vertical = Control.GROW_DIRECTION_BOTH
	var tray_style := StyleBoxFlat.new()
	tray_style.bg_color = WOOD_BG
	tray_style.border_color = Utils.UI_GOLD
	tray_style.set_border_width_all(3)
	tray_style.set_corner_radius_all(10)
	tray_style.set_content_margin_all(0.0)
	_tray.add_theme_stylebox_override("panel", tray_style)
	_root.add_child(_tray)

	_tray_inner = Control.new()
	_tray_inner.name = "TrayInner"
	_tray_inner.custom_minimum_size = Vector2(TRAY_W, TRAY_H)
	_tray_inner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tray.add_child(_tray_inner)

	_build_stage()
	_build_shelves()
	_build_verdict_and_plate()
	_build_buttons()
	_build_filigree()

	_audio = AudioStreamPlayer.new()
	_audio.name = "Audio"
	_audio.bus = "Master"
	add_child(_audio)


func _build_stage() -> void:
	_stage = Control.new()
	_stage.name = "Stage"
	_stage.position = Vector2(STAGE_MARGIN_X, STAGE_TOP)
	_stage.size = Vector2(TRAY_W - STAGE_MARGIN_X * 2.0, STAGE_H)
	_stage.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tray_inner.add_child(_stage)

	_stage_canvas = Control.new()
	_stage_canvas.name = "Baize"
	_stage_canvas.set_anchors_preset(Control.PRESET_FULL_RECT)
	_stage_canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_stage_canvas.draw.connect(_draw_stage)
	_stage.add_child(_stage_canvas)

	# Warm lamp pool — upper-right, the direction the sprites' relief is lit
	# from (any other angle reads double-lit; eval §8).
	_lamp = TextureRect.new()
	_lamp.name = "Lamp"
	_lamp.texture = _radial_texture(
		Color(1.0, 0.9, 0.66, 0.55), Color(1.0, 0.9, 0.66, 0.0))
	_lamp.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lamp.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var add_mat := CanvasItemMaterial.new()
	add_mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_lamp.material = add_mat
	_lamp.modulate.a = 0.16
	_stage.add_child(_lamp)

	# Figure holders — Node2D space over the baize. Right holder added after
	# left so an advancing enemy standard draws over the centre line.
	_left_holder = Node2D.new()
	_left_holder.name = "SideLeft"
	_stage.add_child(_left_holder)
	_right_holder = Node2D.new()
	_right_holder.name = "SideRight"
	_stage.add_child(_right_holder)

	# Vignette ABOVE the figures: the frame edges fall into shadow.
	_vignette = TextureRect.new()
	_vignette.name = "Vignette"
	_vignette.texture = _radial_texture(
		Color(0.0, 0.0, 0.0, 0.0), Color(0.0, 0.0, 0.0, 0.5))
	_vignette.set_anchors_preset(Control.PRESET_FULL_RECT)
	_vignette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_stage.add_child(_vignette)

	_clash_label = Label.new()
	_clash_label.text = "⚔"
	_clash_label.add_theme_font_size_override("font_size", 26)
	_clash_label.add_theme_color_override(
		"font_color", Color(Utils.UI_GOLD, 0.55))
	_clash_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_stage.add_child(_clash_label)

	# Odometers — the ONLY red on the table.
	_odo_left_cap = _mk_label(_stage, "", 12, Color(BONE_HEX))
	_odo_left = _mk_label(_stage, "0", 24, CRIMSON, _font_engraved)
	_odo_right_cap = _mk_label(_stage, "", 12, Color(BONE_HEX))
	_odo_right_cap.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_odo_right = _mk_label(_stage, "0", 24, CRIMSON, _font_engraved)
	_odo_right.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	# The outcome banner — engraved capitals, register-toned, arrives LAST.
	_banner = _mk_label(_stage, "", 30, Utils.UI_GOLD, _font_engraved)
	_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_banner.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
	_banner.add_theme_constant_override("outline_size", 6)
	_sub_banner = _mk_label(_stage, "", 14, Color(BONE_HEX))
	_sub_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER


func _build_shelves() -> void:
	# The reserve shelf: OFF the baize, sunk into the tray wood — the
	# negative space where a corps should have stood (eval §8).
	for side in ["left", "right"]:
		var shelf := PanelContainer.new()
		shelf.name = "Shelf" + side.capitalize()
		var st := StyleBoxFlat.new()
		st.bg_color = Color(0.10, 0.072, 0.05, 1.0)
		st.border_color = Color(0.0, 0.0, 0.0, 0.55)
		st.set_border_width_all(1)
		st.set_corner_radius_all(6)
		st.content_margin_left = 10.0
		st.content_margin_right = 10.0
		st.content_margin_top = 4.0
		st.content_margin_bottom = 4.0
		shelf.add_theme_stylebox_override("panel", st)
		shelf.position = Vector2(
			STAGE_MARGIN_X if side == "left"
			else TRAY_W / 2.0 + 14.0,
			STAGE_TOP + STAGE_H + 8.0)
		shelf.size = Vector2(TRAY_W / 2.0 - STAGE_MARGIN_X - 14.0, SHELF_H)
		shelf.visible = false
		shelf.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_tray_inner.add_child(shelf)
		if side == "left":
			_shelf_left = shelf
		else:
			_shelf_right = shelf


func _build_verdict_and_plate() -> void:
	_verdict = RichTextLabel.new()
	_verdict.name = "Verdict"
	_verdict.bbcode_enabled = true
	_verdict.fit_content = true
	_verdict.scroll_active = false
	_verdict.position = Vector2(TRAY_W * 0.14, STAGE_TOP + STAGE_H + SHELF_H + 16.0)
	_verdict.size = Vector2(TRAY_W * 0.72, 58.0)
	_verdict.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if _font_voice != null:
		_verdict.add_theme_font_override("normal_font", _font_voice)
		_verdict.add_theme_font_override("italics_font", _font_voice)
	_verdict.add_theme_font_size_override("normal_font_size", 17)
	_verdict.add_theme_font_size_override("italics_font_size", 17)
	_tray_inner.add_child(_verdict)

	# The engraved brass nameplate, wax-sealed — the diorama is an OBJECT.
	_nameplate = PanelContainer.new()
	_nameplate.name = "Nameplate"
	var brass := StyleBoxFlat.new()
	brass.bg_color = BRASS
	brass.border_color = BRASS_DARK
	brass.set_border_width_all(2)
	brass.set_corner_radius_all(4)
	brass.content_margin_left = 26.0
	brass.content_margin_right = 26.0
	brass.content_margin_top = 5.0
	brass.content_margin_bottom = 5.0
	_nameplate.add_theme_stylebox_override("panel", brass)
	_nameplate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tray_inner.add_child(_nameplate)

	var plate_box := VBoxContainer.new()
	plate_box.add_theme_constant_override("separation", 0)
	_nameplate.add_child(plate_box)
	_plate_name = Label.new()
	_plate_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_plate_name.add_theme_font_override("font", _font_engraved)
	_plate_name.add_theme_font_size_override("font_size", 19)
	_plate_name.add_theme_color_override("font_color", ENGRAVE)
	plate_box.add_child(_plate_name)
	_plate_sub = Label.new()
	_plate_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_plate_sub.add_theme_font_size_override("font_size", 11)
	_plate_sub.add_theme_color_override("font_color", Color(0.30, 0.23, 0.11, 1.0))
	plate_box.add_child(_plate_sub)

	if ResourceLoader.exists(WAX_SEAL):
		_seal = TextureRect.new()
		_seal.texture = load(WAX_SEAL)
		_seal.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		_seal.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		_seal.size = Vector2(44, 44)
		_seal.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_tray_inner.add_child(_seal)

	# Laurels flank the plate on a triumph only.
	for flip in [false, true]:
		if not ResourceLoader.exists(LAUREL):
			break
		var laurel := TextureRect.new()
		laurel.texture = load(LAUREL)
		laurel.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		laurel.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		laurel.size = Vector2(34, 34)
		laurel.flip_h = flip
		laurel.modulate = Color(Utils.UI_GOLD, 0.85)
		laurel.visible = false
		laurel.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_tray_inner.add_child(laurel)
		if flip:
			_laurel_r = laurel
		else:
			_laurel_l = laurel


func _build_buttons() -> void:
	_btn_close = Button.new()
	_btn_close.text = "Close"
	_btn_close.custom_minimum_size = Vector2(110, 34)
	_btn_close.pressed.connect(_on_close_pressed)
	_tray_inner.add_child(_btn_close)
	_btn_close.position = Vector2(TRAY_W - 136.0, TRAY_H - 46.0)

	_btn_replay = Button.new()
	_btn_replay.text = "Replay"
	_btn_replay.custom_minimum_size = Vector2(110, 34)
	_btn_replay.pressed.connect(_on_replay_pressed)
	_tray_inner.add_child(_btn_replay)
	_btn_replay.position = Vector2(TRAY_W - 256.0, TRAY_H - 46.0)

	_skip_hint = _mk_label(_tray_inner, "click anywhere to skip ▸", 12,
			Color(Utils.COLOR_DIMMED))
	_skip_hint.position = Vector2(22.0, TRAY_H - 40.0)


func _build_filigree() -> void:
	# Gold filigree corners — the U3 pattern (crisp StyleBoxFlat border +
	# ornament, never a muddy full-texture frame).
	if not ResourceLoader.exists(FILIGREE):
		return
	var tex: Texture2D = load(FILIGREE)
	for corner in range(4):
		var fil := TextureRect.new()
		fil.texture = tex
		fil.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		fil.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		fil.size = Vector2(30, 30)
		fil.modulate = Color(Utils.UI_GOLD, 0.4)
		fil.flip_h = corner in [1, 3]
		fil.flip_v = corner in [2, 3]
		fil.position = Vector2(
			8.0 if corner in [0, 2] else TRAY_W - 38.0,
			8.0 if corner in [0, 1] else TRAY_H - 38.0)
		fil.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_tray_inner.add_child(fil)


func _mk_label(parent: Node, text: String, fsize: int, color: Color,
		font: Font = null) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", fsize)
	l.add_theme_color_override("font_color", color)
	if font != null:
		l.add_theme_font_override("font", font)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(l)
	return l


func _radial_texture(inner: Color, outer: Color) -> GradientTexture2D:
	var grad := Gradient.new()
	grad.colors = PackedColorArray([inner, outer])
	grad.offsets = PackedFloat32Array([0.35, 1.0])
	var tex := GradientTexture2D.new()
	tex.gradient = grad
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = 256
	tex.height = 256
	return tex


func _draw_stage() -> void:
	var r := Rect2(Vector2.ZERO, _stage_canvas.size)
	# Baize with a darker felt border band — chart-blue for a sea action.
	var naval := _is_naval()
	_stage_canvas.draw_rect(r, CHART_SEA_EDGE if naval else BAIZE_EDGE)
	_stage_canvas.draw_rect(r.grow(-5.0), CHART_SEA if naval else BAIZE)
	if naval:
		# A few ruled swell lines: an admiralty chart, not an ocean.
		var rows := int(_stage_canvas.size.y / 34.0)
		for i in range(1, rows):
			var y := 5.0 + i * 34.0
			_stage_canvas.draw_line(
				Vector2(9.0, y), Vector2(_stage_canvas.size.x - 9.0, y),
				Color(0.28, 0.42, 0.55, 0.13), 1.0)
	# The brass tray lip at the stage's foot.
	_stage_canvas.draw_rect(
		Rect2(0.0, _stage_canvas.size.y - 4.0, _stage_canvas.size.x, 4.0),
		Color(BRASS.r, BRASS.g, BRASS.b, 0.35))
	# The clash line — dashed, restrained.
	var cx := _stage_canvas.size.x / 2.0
	_stage_canvas.draw_dashed_line(
		Vector2(cx, 26.0), Vector2(cx, _stage_canvas.size.y - 14.0),
		Color(Utils.UI_GOLD, 0.32), 1.5, 9.0)


# ─────────────────────────────────────────────────────────────────────────────
# Population — data → table
# ─────────────────────────────────────────────────────────────────────────────

func _clear_table() -> void:
	for holder in [_left_holder, _right_holder]:
		if holder == null:
			continue
		for child in holder.get_children():
			child.queue_free()
	for shelf in [_shelf_left, _shelf_right]:
		if shelf == null:
			continue
		shelf.visible = false
		for child in shelf.get_children():
			child.queue_free()
	for node in _transients:
		if is_instance_valid(node):
			node.queue_free()
	_transients = []
	_blocks_left = []
	_blocks_right = []


func _side_payloads() -> Array:
	"""[left_side, right_side] — the player's line is ALWAYS the near/left
	side; an observed third-party battle keeps attacker left."""
	var atk: Dictionary = _data.get("attacker", {})
	var deff: Dictionary = _data.get("defender", {})
	if str(_data.get("player_side", "")) == "defender":
		return [deff, atk]
	return [atk, deff]


func _populate(final_frame: bool) -> void:
	_final = final_frame
	_clear_table()

	var sides := _side_payloads()
	var left: Dictionary = sides[0]
	var right: Dictionary = sides[1]
	var register := str(_data.get("register", "observer"))

	# Stage dressing.
	var sw := _stage.size.x
	var sh := _stage.size.y
	_clash_label.position = Vector2(sw / 2.0 - 14.0, sh * 0.42)
	_vignette.modulate = Color(1, 1, 1, 1) if register != "defeat" \
		else Color(1.25, 0.82, 0.82, 1.0)

	# Odometers.
	var left_name := Utils.display_nation_name(str(left.get("nation", "")))
	var right_name := Utils.display_nation_name(str(right.get("nation", "")))
	# NV-7: a fleet action is counted in hulls, not men — say which.
	var loss_word := " SAIL LOST" if _is_naval() else " LOSSES"
	_odo_left_cap.text = left_name.to_upper() + loss_word
	_odo_right_cap.text = right_name.to_upper() + loss_word
	_odo_left_cap.position = Vector2(14.0, 8.0)
	_odo_left.position = Vector2(14.0, 22.0)
	_odo_right_cap.size = Vector2(220.0, 16.0)
	_odo_right_cap.position = Vector2(sw - 234.0, 8.0)
	_odo_right.size = Vector2(220.0, 30.0)
	_odo_right.position = Vector2(sw - 234.0, 22.0)
	_odo_left.text = "0"
	_odo_right.text = "0"

	# Banner (hidden until the topple settles).
	_banner.size = Vector2(sw, 40.0)
	_banner.position = Vector2(0.0, 12.0)
	_banner.text = _banner_text(register)
	_banner.add_theme_color_override("font_color", _banner_color(register))
	_banner.visible = false
	_sub_banner.size = Vector2(sw, 20.0)
	_sub_banner.position = Vector2(0.0, 48.0)
	_sub_banner.text = _sub_banner_text(register)
	_sub_banner.visible = false

	# Corps blocks.
	_blocks_left = _build_side(left, true)
	_blocks_right = _build_side(right, false)

	# Reserve shelves.
	_populate_shelf(_shelf_left, left, true)
	_populate_shelf(_shelf_right, right, false)

	# Verdict + nameplate.
	_verdict.text = ""
	_nameplate_layout()
	_laurel_layout(register)

	_btn_replay.disabled = false
	_btn_close.disabled = false
	_btn_replay.visible = final_frame
	_btn_close.visible = final_frame
	_skip_hint.visible = not final_frame


func _build_side(side: Dictionary, is_left: bool) -> Array:
	var blocks: Array = []
	var contingents: Array = side.get("contingents", [])
	var fought: Array = []
	for c in contingents:
		# PT-D2: the whole absence family stays off the line — an unknown
		# status must never default to a fighting block.
		if not (str(c.get("status", "")) in ABSENT_STATUSES):
			fought.append(c)

	var sw := _stage.size.x
	var base_y := _stage.size.y - 58.0
	var holder := _left_holder if is_left else _right_holder

	for i in range(fought.size()):
		var c: Dictionary = fought[i]
		var depth_x := 128.0 + 118.0 * i
		var x := sw / 2.0 - depth_x if is_left else sw / 2.0 + depth_x
		var pos := Vector2(x, base_y - 66.0 * i)
		var block_scale := 1.0 - 0.12 * i
		blocks.append(_make_block(holder, c, pos, block_scale, is_left, i))

	# The honest tail: corps the cap could not seat.
	var reserve := int(side.get("reserve_count", 0))
	if reserve > 0:
		var tail := _mk_label(_stage, "+%d corps in reserve" % reserve, 11,
				Color(Utils.COLOR_DIMMED))
		tail.position = Vector2(
			14.0 if is_left else sw - 150.0,
			base_y - 66.0 * fought.size() - 8.0)
		_transients.append(tail)
	return blocks


# Labels created per-populate outside the holders — cleared with the table.
var _transients: Array = []


func _make_block(holder: Node2D, c: Dictionary, pos: Vector2,
		block_scale: float, is_left: bool, depth: int) -> Dictionary:
	"""One corps: a rank of figures, its standard, the locket, the labels.
	Returns the block record the sequence animates."""
	var block := Node2D.new()
	block.position = pos
	block.scale = Vector2(block_scale, block_scale)
	block.z_index = 20 - depth
	holder.add_child(block)

	var facing := "r" if is_left else "l"
	var arm := str(c.get("arm", "infantry"))
	var nation := str(c.get("nation", ""))
	var color_key := str(c.get("origin_nation", nation))
	var nation_color: Color = Utils.NATION_COLORS.get(
		color_key, Color(0.6, 0.6, 0.6))

	var committed := maxi(int(c.get("committed", 0)), 1)
	var casualties := int(c.get("casualties", 0))
	var status := str(c.get("status", "engaged"))
	var count: int = FIGURES_BY_ARM.get(arm, 5)
	var frac := clampf(float(casualties) / float(committed), 0.0, 1.0)
	var fallen := clampi(int(round(frac * count)), 0, count)
	if status == "routed":
		fallen = maxi(fallen, count - 1)
	elif status == "destroyed":
		fallen = count

	# Figures: rear rank first (draws behind), then the front rank.
	var figures: Array = []
	# NV-7: a hull fills most of its 256px frame where a soldier fills a
	# third of his, so the land spread packed a squadron into one blob.
	# Ships get room to read as a LINE of battle, which is the whole point
	# of the formation they are in. NV-8b: and they sail LARGER — three
	# small ships on a wide sea read sparse; a liner has presence.
	var fig_px := FIGURE_PX * 1.3 if arm == "ship" else FIGURE_PX
	var spread := 66.0 if arm == "ship" else 30.0
	var rear := count - mini(count, 3)
	for j in range(rear):
		var f := DioramaFigure.new()
		f.setup(arm, facing, nation_color, fig_px * 0.94)
		f.position = Vector2((j - (rear - 1) / 2.0) * spread + 6.0, -22.0)
		block.add_child(f)
		figures.append(f)
	for j in range(mini(count, 3)):
		var f := DioramaFigure.new()
		f.setup(arm, facing, nation_color, fig_px)
		f.position = Vector2((j - (mini(count, 3) - 1) / 2.0) * spread, 0.0)
		block.add_child(f)
		figures.append(f)

	# Which figures fall: the CLASH-side flank first — the line breaks from
	# where it met the enemy.
	if is_left:
		figures.sort_custom(func(a, b): return a.position.x > b.position.x)
	else:
		figures.sort_custom(func(a, b): return a.position.x < b.position.x)
	var falling: Array = figures.slice(0, fallen)
	var standing: Array = figures.slice(fallen, figures.size())

	# The corps standard — planted mid-rank, clash side. NOT at sea (NV-8b):
	# on the naval tableau the land poles floated in open water, and a rear
	# squadron's standard drew OVER the front block's locket (the live pass
	# caught Russia's colours covering Nelson's face). Every ship already
	# carries her own faction ensign at the spanker peak — the sea needs no
	# second flag.
	var standard: Node2D = null
	if not _is_naval():
		standard = _make_standard(nation_color, color_key, is_left)
		standard.position = Vector2(38.0 if is_left else -38.0, 0.0)
		block.add_child(standard)

	# Locket + labels above the block (Control children of the Node2D).
	# Left side: locket outboard-left, text flows right toward the line.
	# Right side mirrored: text right-aligned, locket outboard-right.
	var locket := PortraitLocket.new()
	locket.setup(str(c.get("name", "")), 38.0, bool(c.get("crowned", false)))
	locket.position = Vector2(-86.0 if is_left else 48.0, -158.0)
	block.add_child(locket)

	var text_align := HORIZONTAL_ALIGNMENT_LEFT if is_left \
		else HORIZONTAL_ALIGNMENT_RIGHT
	var text_x := -42.0 if is_left else -186.0
	var text_w := 150.0 if is_left else 226.0

	var lead_mark := " ◆" if bool(c.get("lead", false)) else ""
	var name_l := _mk_label(block, str(c.get("name", "")) + lead_mark, 14,
			Color(GOLD_HEX))
	name_l.position = Vector2(text_x, -156.0)
	name_l.size = Vector2(text_w, 18.0)
	name_l.horizontal_alignment = text_align

	var remaining := int(c.get("remaining", 0))
	# NV-7: a squadron is counted in sail, and 45 → 38 needs the unit said
	# out loud or it reads as a rout of thirty-eight men.
	var unit := " sail" if str(c.get("arm", "")) == "ship" else ""
	var strength_l := _mk_label(
		block, "%s → %s%s" % [Utils.format_number(committed),
		Utils.format_number(remaining), unit], 11, Color(BONE_HEX))
	strength_l.position = Vector2(text_x, -138.0)
	strength_l.size = Vector2(text_w, 14.0)
	strength_l.horizontal_alignment = text_align

	var status_l: Label = null
	if status in ["routed", "destroyed"]:
		# NV-8b: the sea has its own words — a squadron STRIKES her
		# colours; a squadron lost is SUNK. "ROUTED" is a land verb.
		var status_word := status.to_upper()
		if _is_naval():
			status_word = "STRUCK" if status == "routed" else "SUNK"
		status_l = _mk_label(block, status_word, 11, CRIMSON)
		status_l.visible = false
	elif status == "reinforced":
		status_l = _mk_label(block, "marched to the guns", 10,
				Color(0.55, 0.65, 0.5))
	if status_l != null:
		status_l.position = Vector2(text_x, -124.0)
		status_l.size = Vector2(text_w, 14.0)
		status_l.horizontal_alignment = text_align

	return {
		"node": block, "data": c, "figures": figures,
		"falling": falling, "standing": standing,
		"standard": standard, "locket": locket, "status_label": status_l,
		"is_left": is_left, "status": status, "depth": depth,
	}


func _make_standard(nation_color: Color, flag_key: String,
		is_left: bool) -> Node2D:
	"""A corps standard: a real pole with the nation's own colours flying —
	the one saturated element on a wood figure, which is exactly why it is
	the thing that falls."""
	var std := Node2D.new()
	std.name = "Standard"
	std.z_index = 3

	var pole := Line2D.new()
	pole.points = PackedVector2Array([Vector2(0, 0), Vector2(0, -86)])
	pole.width = 2.4
	pole.default_color = Color(0.32, 0.24, 0.14, 1.0)
	std.add_child(pole)
	# Finial.
	var finial := Line2D.new()
	finial.points = PackedVector2Array([Vector2(0, -86), Vector2(0, -92)])
	finial.width = 4.0
	finial.default_color = BRASS
	std.add_child(finial)

	var flag_path := Utils.nation_flag_path(flag_key)
	if flag_path != "":
		var spr := Sprite2D.new()
		spr.texture = load(flag_path)
		spr.centered = false
		var tex_size: Vector2 = spr.texture.get_size()
		var flag_w := 30.0
		var s := flag_w / maxf(tex_size.x, 1.0)
		spr.scale = Vector2(s, s)
		# The flag flies toward the clash line on both sides.
		spr.position = Vector2(1.0 if is_left else -1.0 - flag_w, -86.0)
		std.add_child(spr)
	else:
		var pennant := Polygon2D.new()
		var dir := 1.0 if is_left else -1.0
		pennant.polygon = PackedVector2Array([
			Vector2(1.0 * dir, -86.0), Vector2(30.0 * dir, -80.0),
			Vector2(1.0 * dir, -70.0)])
		pennant.color = WarTablePiece.legible_tint(nation_color)
		std.add_child(pennant)
	return std


func _populate_shelf(shelf: Control, side: Dictionary, is_left: bool) -> void:
	var absent: Array = []
	for c in side.get("contingents", []):
		# PT-D2: refused / failed_arrive / out_of_reach all shelve; the
		# absence_reason caption carries which it was.
		if str(c.get("status", "")) in ABSENT_STATUSES:
			absent.append(c)
	if absent.is_empty():
		return
	shelf.visible = true

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	shelf.add_child(row)

	for c in absent.slice(0, 2):
		var cell := Control.new()
		cell.custom_minimum_size = Vector2(46.0, SHELF_H - 10.0)
		cell.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(cell)
		var f := DioramaFigure.new()
		f.setup(str(c.get("arm", "infantry")), "r" if is_left else "l",
				Utils.NATION_COLORS.get(str(c.get("nation", "")),
				Color(0.6, 0.6, 0.6)), SHELF_FIGURE_PX)
		f.position = Vector2(23.0, SHELF_H - 16.0)
		f.grey_out()
		cell.add_child(f)

		var text_box := VBoxContainer.new()
		text_box.add_theme_constant_override("separation", 0)
		text_box.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(text_box)
		var head := Label.new()
		head.text = "%s — %s" % [str(c.get("name", "")),
				str(c.get("absence_reason", "did not march"))]
		head.add_theme_font_size_override("font_size", 12)
		head.add_theme_color_override("font_color",
				Color(0.62, 0.62, 0.66, 1.0))
		text_box.add_child(head)
		var grudge := str(c.get("grudge", ""))
		if grudge != "":
			var g := Label.new()
			g.text = grudge
			if _font_voice != null:
				g.add_theme_font_override("font", _font_voice)
			g.add_theme_font_size_override("font_size", 12)
			g.add_theme_color_override("font_color",
					Color(0.66, 0.42, 0.40, 1.0))
			text_box.add_child(g)


func _nameplate_layout() -> void:
	_plate_name.text = str(_data.get("battle_name", "")).to_upper()
	# NV-7: a fleet action has no province to engrave — it is named for its
	# waters, exactly as the log names it.
	var place := str(_data.get("waters", "")) if _is_naval() \
		else str(_data.get("region", ""))
	_plate_sub.text = "%s · TURN %d" % [
		place.to_upper(), int(_data.get("turn", 0))]
	# Measure after text set.
	_nameplate.reset_size()
	await get_tree().process_frame
	var plate_size := _nameplate.size
	_nameplate.position = Vector2(
		(TRAY_W - plate_size.x) / 2.0, TRAY_H - plate_size.y - 12.0)
	if _seal != null:
		_seal.position = _nameplate.position + Vector2(
			plate_size.x - 12.0, plate_size.y - 30.0)


func _laurel_layout(register: String) -> void:
	var is_triumph := register == "triumph"
	for laurel in [_laurel_l, _laurel_r]:
		if laurel != null:
			laurel.visible = is_triumph
	if is_triumph and _laurel_l != null:
		await get_tree().process_frame
		var y := TRAY_H - 46.0
		_laurel_l.position = Vector2(_nameplate.position.x - 44.0, y)
		# Right laurel clears the wax seal (which overhangs the plate's
		# right edge by design — a seal ON the document).
		_laurel_r.position = Vector2(
			_nameplate.position.x + _nameplate.size.x + 44.0, y)


# ─────────────────────────────────────────────────────────────────────────────
# Copy — the register owns the words
# ─────────────────────────────────────────────────────────────────────────────

func _decisive() -> bool:
	return str(_data.get("outcome", "")) in [
		"attacker_victory", "defender_victory", "mutual_destruction"]


func _is_naval() -> bool:
	"""NV-7 — a §4.4 fleet action rather than a land battle. Set by the
	backend builder; everything it changes here is presentation."""
	return bool(_data.get("naval", false))


func _banner_text(register: String) -> String:
	var outcome := str(_data.get("outcome", ""))
	if _is_naval():
		# NV-7: the sea has its own vocabulary. Nothing is "carried" and no
		# field is held — a fleet action is decided by who is left in
		# possession of the water.
		match register:
			"triumph":
				return "THE SEA IS OURS" if _decisive() else "THE ENEMY DRAWS OFF"
			"defeat":
				return "THE FLEET IS BROKEN" if _decisive() else "WE BEAR AWAY"
			"grim":
				return "AN ACTION WITHOUT ISSUE"
			_:
				var victor := _victor_nation()
				if victor != "" and _decisive():
					return "%s HOLDS THE SEA" % \
						Utils.display_nation_name(victor).to_upper()
				return "AN INDECISIVE ACTION"
	match register:
		"triumph":
			if _data.get("great_battle", false):
				return "A FIELD OF LEGEND IS WON"
			return "A DECISIVE VICTORY" if _decisive() else "THE FIELD IS OURS"
		"defeat":
			if str(_data.get("player_side", "")) == "defender":
				return "THE LINE IS BROKEN" if _decisive() else "THE FIELD IS LOST"
			return "THE ASSAULT FAILS"
		"grim":
			return "MUTUAL RUIN" if outcome == "mutual_destruction" \
				else "A BLOODY STALEMATE"
		_:
			var victor_nation := _victor_nation()
			if victor_nation != "" and _decisive():
				return "%s CARRIES THE FIELD" % \
					Utils.display_nation_name(victor_nation).to_upper()
			return "AN INDECISIVE ACTION"


func _victor_nation() -> String:
	var victor := str(_data.get("victor", ""))
	if victor == "" or victor == "<null>":
		return ""
	var outcome := str(_data.get("outcome", ""))
	if outcome.begins_with("attacker"):
		return str(_data.get("attacker_nation", ""))
	if outcome.begins_with("defender"):
		return str(_data.get("defender_nation", ""))
	return ""


func _banner_color(register: String) -> Color:
	match register:
		"triumph":
			return Utils.UI_GOLD
		"defeat":
			return CRIMSON
		"grim":
			return Color(BONE_HEX)
		_:
			return Color(0.83, 0.79, 0.68, 1.0)


func _sub_banner_text(register: String) -> String:
	if not bool(_data.get("region_conquered", false)):
		return ""
	var region := str(_data.get("region", ""))
	var victor_nation := _victor_nation()
	match register:
		"triumph":
			return "%s falls to %s." % [region,
				Utils.display_nation_name(victor_nation)]
		"defeat":
			return "%s is lost." % region
		_:
			return "%s changes hands." % region


# ─────────────────────────────────────────────────────────────────────────────
# The cinematic
# ─────────────────────────────────────────────────────────────────────────────

func _play_cinematic() -> void:
	_final = false
	_kill_sequence()

	# Reveal: the tray settles into view under one cannon thud.
	_tray.modulate.a = 0.0
	_play_sound(AUDIO_CANNON, -8.0)
	_seq = create_tween()
	_seq.tween_property(_tray, "modulate:a", 1.0, 0.24)

	# Figures placed on the table.
	var t := 0.30
	var all_blocks := _blocks_left + _blocks_right
	for b in all_blocks:
		for f in b["figures"]:
			f.pop_in(t)
			t += 0.035
	for b in all_blocks:
		b["locket"].modulate.a = 0.0
		_seq.parallel().tween_property(b["locket"], "modulate:a", 1.0, 0.3) \
			.set_delay(t)

	# The lines close.
	var lean_at := t + 0.25
	for b in all_blocks:
		for f in b["standing"]:
			f.lean_in(7.0, lean_at)
		for f in b["falling"]:
			f.lean_in(7.0, lean_at)

	# The topple cascade + the odometers, bound together: the count and the
	# collapse are the same event.
	var topple_start := lean_at + 0.45
	var topple_span := 1.5
	_schedule_topples(topple_start, topple_span)
	_animate_odometers(topple_start, topple_span + 0.4)

	# Standards fall; on a decisive field the beaten lead's eagle is TAKEN.
	var standards_at := topple_start + topple_span * 0.55
	_schedule_standards(standards_at)

	# The gavel: banner, then Berthier.
	var banner_at := topple_start + topple_span + 0.55
	_seq.parallel().tween_callback(_show_banner).set_delay(banner_at)
	_seq.parallel().tween_callback(_type_verdict).set_delay(banner_at + 0.45)
	_seq.parallel().tween_callback(func(): _enter_final(true)) \
		.set_delay(banner_at + 0.6)


func _schedule_topples(start: float, span: float) -> void:
	for blocks in [_blocks_left, _blocks_right]:
		for b in blocks:
			var falling: Array = b["falling"]
			if falling.is_empty():
				# The victor's line takes the shock and holds.
				for f in b["standing"]:
					f.recoil(start + 0.15 * b["depth"])
				continue
			var per := span / maxf(float(falling.size()), 1.0)
			for j in range(falling.size()):
				var f: DioramaFigure = falling[j]
				f.topple(start + 0.12 * b["depth"] + per * j * 0.62)
			# The broken corps' face goes grey as its line falls.
			if b["status"] in ["routed", "destroyed"]:
				_seq.parallel().tween_callback(
					func(): b["locket"].set_dead(true)) \
					.set_delay(start + span * 0.5)
				if b["status_label"] != null:
					_seq.parallel().tween_callback(
						func(): b["status_label"].visible = true) \
						.set_delay(start + span * 0.6)


func _schedule_standards(at: float) -> void:
	var register := str(_data.get("register", "observer"))
	var decisive := _decisive()
	var drum_queued := false

	for blocks in [_blocks_left, _blocks_right]:
		for b in blocks:
			if b["status"] not in ["routed", "destroyed"]:
				continue
			var std: Node2D = b["standard"]
			if std == null:
				continue  # NV-8b: no standards at sea
			var fall_dir := -1.0 if b["is_left"] else 1.0
			_seq.parallel().tween_property(
				std, "rotation", deg_to_rad(64.0) * fall_dir, 0.5) \
				.set_delay(at).set_trans(Tween.TRANS_BOUNCE) \
				.set_ease(Tween.EASE_OUT)
			_seq.parallel().tween_property(std, "modulate:a", 0.85, 0.5) \
				.set_delay(at)

			# The eagle taken: the beaten LEAD's standard crosses the line.
			if decisive and bool(b["data"].get("lead", false)):
				var across := 300.0 if b["is_left"] else -300.0
				_seq.parallel().tween_property(
					std, "position:x", std.position.x + across, 0.8) \
					.set_delay(at + 0.55) \
					.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
				if not drum_queued and register in ["triumph", "defeat"]:
					drum_queued = true
					_seq.parallel().tween_callback(
						func(): _play_sound(AUDIO_DRUM, -6.0)) \
						.set_delay(at + 0.55)

	# The alarm register (§7 Q6): on a defeat the victor's lead standard
	# advances ONTO your half of the baize.
	if register == "defeat":
		var enemy_blocks := _blocks_right \
			if str(_data.get("player_side", "")) != "" else []
		for b in enemy_blocks:
			if bool(b["data"].get("lead", false)) \
					and b["status"] not in ["routed", "destroyed"]:
				var std2: Node2D = b["standard"]
				if std2 == null:
					break  # NV-8b: no advancing standard at sea
				_seq.parallel().tween_property(
					std2, "position:x", std2.position.x - 60.0, 0.9) \
					.set_delay(at + 0.4) \
					.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
				if not drum_queued:
					drum_queued = true
					_seq.parallel().tween_callback(
						func(): _play_sound(AUDIO_DRUM, -6.0)) \
						.set_delay(at + 0.5)
				break


func _animate_odometers(start: float, span: float) -> void:
	var sides := _side_payloads()
	var left_total := int(sides[0].get("casualties_total", 0))
	var right_total := int(sides[1].get("casualties_total", 0))
	_seq.parallel().tween_method(
		func(v: float): _odo_left.text = Utils.format_number(int(v)),
		0.0, float(left_total), span).set_delay(start) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_seq.parallel().tween_method(
		func(v: float): _odo_right.text = Utils.format_number(int(v)),
		0.0, float(right_total), span).set_delay(start) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


func _show_banner() -> void:
	_banner.visible = true
	_banner.scale = Vector2(1.12, 1.12)
	_banner.pivot_offset = _banner.size / 2.0
	_banner.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(_banner, "modulate:a", 1.0, 0.3)
	tw.parallel().tween_property(_banner, "scale", Vector2.ONE, 0.35) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	if _sub_banner.text != "":
		_sub_banner.visible = true
		_sub_banner.modulate.a = 0.0
		tw.parallel().tween_property(_sub_banner, "modulate:a", 1.0, 0.4) \
			.set_delay(0.25)


func _verdict_bbcode() -> String:
	var text := ""
	var observation := str(_data.get("observation", ""))
	if observation != "":
		# NV-7: Berthier is the Emperor's chief of staff and has no
		# business reporting a fleet action — the sea answers to the
		# Admiralty.
		var speaker := "The Admiralty" if _is_naval() else "Berthier"
		text += "[center][i]%s[/i][/center]" % Utils.bbcode_color(
			"%s: “%s”" % [speaker, observation], Utils.COLOR_OBSERVATION)
	var voice := str(_data.get("enemy_voice", ""))
	if voice != "":
		if text != "":
			text += "\n"
		text += "[center][i]%s[/i][/center]" % Utils.bbcode_color(
			voice, Utils.COLOR_DIMMED)
	return text


func _type_verdict() -> void:
	var bb := _verdict_bbcode()
	if bb == "":
		return
	_verdict.text = bb
	_verdict.visible_characters = 0
	var total := _verdict.get_total_character_count()
	var tw := create_tween()
	tw.tween_method(
		func(v: float): _verdict.visible_characters = int(v),
		0.0, float(total), clampf(total / 34.0, 0.8, 2.6))


func _enter_final(from_cinematic: bool) -> void:
	_final = true
	_skip_hint.visible = false
	_btn_close.visible = true
	_btn_replay.visible = true
	if not from_cinematic:
		# The settled frame, instantly: everything at end state.
		_apply_final_frame_instant()


func _apply_final_frame_instant() -> void:
	var sides := _side_payloads()
	for pair in [[_blocks_left, sides[0]], [_blocks_right, sides[1]]]:
		var blocks: Array = pair[0]
		for b in blocks:
			for f in b["falling"]:
				f.topple(0.0, true)
			if b["status"] in ["routed", "destroyed"]:
				b["locket"].set_dead(false)
				if b["status_label"] != null:
					b["status_label"].visible = true
				var std: Node2D = b["standard"]
				if std != null:  # NV-8b: no standards at sea
					std.rotation = deg_to_rad(64.0) * (-1.0 if b["is_left"] else 1.0)
					std.modulate.a = 0.85
					if _decisive() and bool(b["data"].get("lead", false)):
						std.position.x += 300.0 if b["is_left"] else -300.0
	_odo_left.text = Utils.format_number(int(sides[0].get("casualties_total", 0)))
	_odo_right.text = Utils.format_number(int(sides[1].get("casualties_total", 0)))
	_banner.visible = true
	_banner.modulate.a = 1.0
	_banner.scale = Vector2.ONE
	if _sub_banner.text != "":
		_sub_banner.visible = true
		_sub_banner.modulate.a = 1.0
	_verdict.text = _verdict_bbcode()
	_verdict.visible_characters = -1


func _skip_to_final() -> void:
	"""Any click during the cinematic: kill the tweens, rebuild the settled
	frame deterministically — no tween bookkeeping, no half states."""
	_kill_sequence()
	_populate(true)
	_enter_final(false)


func _kill_sequence() -> void:
	if _seq != null and _seq.is_valid():
		_seq.kill()
	_seq = null


func _play_sound(path: String, volume_db: float) -> void:
	if _audio == null or not UiSettings.get_battle_sfx():
		return
	if not ResourceLoader.exists(path):
		return
	_audio.stream = load(path)
	_audio.volume_db = volume_db
	_audio.play()


# ─────────────────────────────────────────────────────────────────────────────
# Input
# ─────────────────────────────────────────────────────────────────────────────

func _on_root_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		if not _final:
			_root.accept_event()
			_skip_to_final()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("ui_cancel") \
			or event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		if _final:
			_on_close_pressed()
		else:
			_skip_to_final()


func _on_replay_pressed() -> void:
	_populate(false)
	_play_cinematic()


func _on_close_pressed() -> void:
	_kill_sequence()
	hide()
	dismissed.emit()

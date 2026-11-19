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
signal word_given(command: String)   # row BA, BA-3: a day's chip pressed

# ── Geometry (design px; Utils.clamp_centered_panel shrinks on small screens)
const TRAY_W := 1000.0
# Session UI-2: 684 (was 660) - the strength band takes a 42-px row under the
# stage, the shelves move below it, and the verdict keeps its room.
const TRAY_H := 744.0   # Session UI-6: 744 (was 684) - the stage grew 60 px so the armies fill the field
# Session UI-2: THE STRENGTH BAND - each side's strength before -> after as a
# drawn bar with its figures, in the row under the stage (the band that stood
# empty wood on a field without a shelf).
const BAND_H := 36.0
const BAND_GAP := 6.0
const STAGE_MARGIN_X := 26.0
const STAGE_TOP := 52.0
const STAGE_H := 440.0
const SHELF_H := 66.0
# UXR-X9: the verdict's room — never less than one line, and ending this far
# above the nameplate's top.
const VERDICT_ROOM_MIN := 30.0
const VERDICT_PLATE_GAP := 6.0
const FIGURE_PX := 80.0   # Session UI-6: 80 (was 58) - the readers: "the sprites are small, enlarge the armies"
# IQ-5 review (B): the `faith` caption sits UNDER a corps' figures, outboard
# (away from the clash line), wrapped in this block-local width. Measured
# headless on the real tableau (both columns, depths 1-2, reinforced and
# co-located): nothing else is drawn there. Y is below the feet (y = 0) and
# clear of a fallen figure's ink (+22 still grazed one by 1px).
# UXR3-F2: 230 wide, so the faith sentence wraps in two lines — at three it
# ran into the forward rank's "marched to the guns".
const FAITH_CAPTION_W := 230.0
const FAITH_CAPTION_Y := 30.0
const FAITH_CAPTION_INBOARD := 20.0
# UXR-X5 (UXR-2, October 12, 2026): the TEXT leaves the depth scale. A block's
# art (figures, standard, locket) recedes by 1 − 0.12·depth; its words are
# read at the theme's sizes at every depth (name 16, the rest Caption 14 —
# 10–14 design px × 0.88 had read 8.8 px on a 1080 panel). Only the text's
# ANCHORS follow the depth. Two lines fit above the feet between ranks
# (name, strength — who); the status joins the faith caption UNDER the feet
# (what became of them), one 14-px line apart.
const TEXT_PITCH := 18.0
const FATE_PITCH := 18.0
# BA1-X4: the pitches above are the 115 % line (a Caption line is 25 px tall there);
# at a larger Text size the stack's pitch grows with the line, never below today's
const LINE_H_SHIPPED := 25.0
const CLASH_PUSH_MAX_EXTRA := 10.0     # guard for a future cap above 1.3 (held at 130 % the extra never exceeds +3; unreachable today)
# A fate caption is cut back to stay on the baize, never narrower than this.
const BAIZE_PAD := 14.0
const FATE_MIN_W := 96.0
# Every rank's words draw above every rank's standard (a standard rides its
# block +3): at four ranks the next rank's colours stood over a name.
const TEXT_Z := 10
const SHELF_FIGURE_PX := 44.0
# UXR3-F2: a standard's pole, and the shortest a narrowed line cuts it to.
const STANDARD_POLE := 86.0
const STANDARD_POLE_MIN := 36.0

# PT-D2: the backend's absence family (battle_diorama.py ABSENT_STATUSES)
# — statuses the shelf renders, never the line.
const ABSENT_STATUSES := ["failed_arrive", "refused", "out_of_reach"]
# SF7-X23: the line's steps shrink to fit the contingents on the baize.
const THE_LINE_FITS_THE_BAIZE := true
# SF7-X29: the reserve tail states its dead and right-aligns by its width
# (the payload's `reserve_casualties`; the text reads it whenever present).
const THE_RESERVE_NAMES_ITS_DEAD := true

# ── Palette (colour rarity per the brief: wood, brass, baize; red = casualties)
const WOOD_BG := Color(0.165, 0.118, 0.078, 1.0)        # walnut tray
const WOOD_EDGE := Color(0.24, 0.175, 0.115, 1.0)
const BAIZE := Utils.UI_DIORAMA_BAIZE          # green felt
const BAIZE_EDGE := Color(0.086, 0.145, 0.104, 1.0)
const BRASS := Color(0.72, 0.60, 0.36, 1.0)
const BRASS_DARK := Color(0.42, 0.33, 0.17, 1.0)
const ENGRAVE := Color(0.18, 0.13, 0.06, 1.0)           # cut into brass
# UXR3-75 (Pre-Deploy S12 part 2): the plate's sub-line, brass engraved on the
# walnut (4.6 : 1 on WOOD_BG); the name is BRASS itself (6.0 : 1).
const PLATE_SUB := Color(0.62, 0.52, 0.33, 1.0)
# S12 (UXR3-50, 51): b8332e read 2.93 : 1 on the tableau's dark field; the
# same crimson hue, lighter (d7635e, 4.82 : 1). CRIMSON is text only.
const CRIMSON := Color(0.843, 0.388, 0.369, 1.0)
const BONE_HEX := "c9c2b2"
const GOLD_HEX := "d9c08c"

const FONT_ENGRAVED := "res://assets/fonts/Cinzel[wght].ttf"
const FONT_VOICE := "res://assets/fonts/IMFeENit28P.ttf"       # period italic
const FILIGREE := "res://assets/ui/ornaments/corner_floral_01.svg"
const WAX_SEAL := "res://assets/ui/ornaments/wax_seal.png"
const LAUREL := "res://assets/ui/ornaments/laurel_golden.svg"
const LAUREL_PX := 34.0         # a laurel's side (BA1-X8: they flank the triumph's banner)
const LAUREL_GAP := 16.0        # ...this far from its words

# Figures per corps by arm — a line of foot, a squadron, a battery.
# NV-7 adds "ship": a squadron is three sail on the table, the same count
# the batteries get — a line of battle reads as a line, not a crowd.
const FIGURES_BY_ARM := {"infantry": 5, "cavalry": 4, "artillery": 3, "ship": 3}

# NV-7 — the sea. A fleet action plays on the same tray, on chart-blue
# instead of green felt: the tableau is still a war table, and the one
# thing it must say at a glance is "this is not a field".
const CHART_SEA := Color(0.098, 0.153, 0.216, 1.0)
const CHART_SEA_EDGE := Color(0.063, 0.098, 0.145, 1.0)
# Row BA, BA-6 (the user's "does not look ai genned … get assets if needed"):
# the felt is a photographed baize (ambientCG Fabric034, CC0, on the table's own
# green) tiled under a land battle, whose province's survey is laid on it (the
# acts' Ground class; tools/ba6_terrain_plates.py). A fleet action keeps its
# chart-blue table (no period chart passed the licence policy).
const FELT_TILE := "res://assets/textures/battle/felt_baize.jpg"

# ── State
var _data: Dictionary = {}
var _final := false            # sequence has settled (or was opened settled)
var _seq: Tween = null         # master cinematic tween
var _blocks_left: Array = []   # per-corps dicts (see _make_block)
var _blocks_right: Array = []
# Row BA (BA-1): the battle in acts — the plinths, the dice and the sequencer
# that plays the payload's script (scripts/battle_acts.gd). Made per showing.
var _acts: BattleActs = null
# UX23-R6: cues this diorama started, silenced on close.
var _own_cues_started: Array = []
var _music_ducked := false

# Chrome nodes (built once in _ready)
var _root: Control = null
var _scrim: ColorRect = null
var _tray: PanelContainer = null
var _tray_inner: Control = null
var _stage: Control = null
var _stage_canvas: Control = null
var _felt_tex: Texture2D = null        # BA-6: the photographed baize
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
var _band: Control = null           # the strength band (Session UI-2)
var _band_names: Array = []         # [left Label, right Label]
var _band_figs: Array = []          # [left Label, right Label]
var _band_bars: Array = []          # [left Control, right Control]
var _band_rows: Array = []          # [{before, lost, tone}, ...] left, right
var _band_progress := 1.0
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
	# Row PW (the first playtest: "some sound lingers on after"): the field's
	# noise and the ducked music end with the table, by whatever road it shut —
	# `_on_close_pressed` was their one stop, and a world swap's `hide_all` (or
	# any bare `hide()`) left the battle murmuring under the map.
	visibility_changed.connect(_on_table_visibility_changed)


func _on_table_visibility_changed() -> void:
	if visible:
		return
	for tag in ["battle_bed", "sea", "creak", "scribble_verdict"]:
		AudioManager.stop_loop(tag)
	if _music_ducked:
		_music_ducked = false
		AudioManager.duck_music(false)


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
	# Music & Sound Core: the tableau takes the stage — music ducks under it,
	# the field (or the sea) murmurs beneath the baize.
	if not _music_ducked:
		_music_ducked = true
		AudioManager.duck_music(true)
	if UiSettings.get_battle_sfx():
		if _is_naval():
			AudioManager.stop_loop("battle_bed")
			AudioManager.start_loop("sea")
			AudioManager.start_loop("creak")
			_cue("ship_bell")
		else:
			AudioManager.start_loop("battle_bed")
	# Row BA: Settings → Battle scenes → "Final frame only" opens the field as
	# it ended (Replay still plays it).
	if cinematic and BattleActs.opens_settled():
		cinematic = false
	_fit_tableau_type()
	_refit_chrome_type()
	_populate(not cinematic)
	_fit_tray_to_viewport()
	if cinematic:
		_play_cinematic()
	else:
		_enter_final(false)



# ─────────────────────────────────────────────────────────────────────────────
# Fit (IQ-10 "The Client Pass", Sept 19, 2026)
# ─────────────────────────────────────────────────────────────────────────────

const FIT_MARGIN_X := 24.0
const FIT_MARGIN_Y := 88.0          # the 36px top bar plus breathing room
# False restores `Utils.clamp_centered_panel(_tray)`, under which the tableau
# rendered 1000px wide inside an 800px logical viewport at Interface Scale 2.0
# and put Replay and Close at y=658, off a 450-high screen.
const THE_TABLEAU_FITS_THE_SCREEN := true


func _fit_tray_to_viewport() -> void:
	"""Shrink the WHOLE tableau to the live logical viewport, uniformly.

	The tray is authored in design pixels (TRAY_W x TRAY_H) and its children
	are placed absolutely, so the clamp helper's approach — rewrite the centre
	offsets, then relax descendant height minimums — cannot apply here: the
	inner's own `custom_minimum_size` is a hard floor on the width, and
	reflowing the shelves would break the composition. Scaling about the
	tray's centre keeps every relation intact and is a no-op (scale 1.0)
	wherever the tableau already fits, which is every window at Interface
	Scale 1.0 on a 1280x720 screen or larger."""
	if _tray == null:
		return
	if not THE_TABLEAU_FITS_THE_SCREEN:
		Utils.clamp_centered_panel(_tray)
		return
	var viewport := _tray.get_viewport()
	if viewport == null:
		return
	var view: Vector2 = viewport.get_visible_rect().size
	var fit := 1.0
	if TRAY_W > 0.0 and tray_h() > 0.0:
		fit = minf(1.0, minf((view.x - FIT_MARGIN_X) / TRAY_W,
				(view.y - FIT_MARGIN_Y) / tray_h()))
	fit = clampf(fit, 0.35, 1.0)
	_tray.pivot_offset = Vector2(TRAY_W / 2.0, tray_h() / 2.0)
	_tray.scale = Vector2(fit, fit)


# Row BA, the levers past 5: a table whose day panel stands asks the tray for more
# room at its foot (the acts' DAY_ROOM, design px). The stage, the band and the
# shelves keep their places; everything anchored to the foot moves down with it.
var _day_room := 0.0


func tray_h() -> float:
	"""The tray's design height now: TRAY_H, and the day panel's room while one stands."""
	return TRAY_H + _day_room


func set_day_room(px: float) -> void:
	"""Idempotent: the tray grows by `px` (0 puts it back to TRAY_H), the foot's
	controls follow it down, and the tray is fitted to the screen again."""
	_day_room = maxf(px, 0.0)
	if _tray == null:
		return
	_tray.offset_top = -tray_h() / 2.0
	_tray.offset_bottom = tray_h() / 2.0
	if _tray_inner != null:
		_tray_inner.custom_minimum_size = Vector2(TRAY_W, tray_h())
	_tray.reset_size()
	_place_the_foot()
	if _nameplate != null and _nameplate.size.y > 0.0:
		_nameplate.position.y = tray_h() - _nameplate.size.y - 12.0
		if _seal != null:
			_seal.position.y = _nameplate.position.y + _nameplate.size.y / 2.0 - 22.0
	_fit_tray_to_viewport()


func _place_the_foot() -> void:
	if _btn_close != null:
		_btn_close.position.y = tray_h() - 46.0
	if _btn_replay != null:
		_btn_replay.position.y = tray_h() - 46.0
	if _skip_hint != null:
		_skip_hint.position.y = tray_h() - 40.0


func refit() -> void:
	"""UXR-2: the live-refit road's hook (`Utils.refit_surface`) — the
	tableau re-scales to the new logical viewport, as it does on open."""
	_fit_tray_to_viewport()

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
	# Session UI-2 (November 11, 2026): the one window frame over the wood —
	# the last surface still in the thick tan rounded border; the frame's own
	# re-entrant corners retire the four floral ones.
	_tray.add_theme_stylebox_override("panel",
		Utils.gilt_frame(WOOD_BG, Utils.UI_GOLD, Utils.FRAME_WINDOW, 0.0))
	# BA1-X5 (row BA, BA-1): "click anywhere to skip" was true only of the dark
	# margin round the tableau. A PanelContainer stops the mouse by default, so
	# a click ON the tableau — where the hint is printed — never reached
	# `_on_root_input`. The frame passes it up; the buttons still take theirs.
	_tray.mouse_filter = Control.MOUSE_FILTER_PASS
	_root.add_child(_tray)

	_tray_inner = Control.new()
	_tray_inner.name = "TrayInner"
	_tray_inner.custom_minimum_size = Vector2(TRAY_W, TRAY_H)
	_tray_inner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tray.add_child(_tray_inner)

	_build_stage()
	_build_strength_band()
	_build_shelves()
	_build_verdict_and_plate()
	_build_buttons()



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
	# BA-6: the felt tile repeats across the baize; the plates scale smoothly
	_stage_canvas.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	_stage_canvas.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
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
	_clash_label.theme_type_variation = &"TableauClash"
	# S12 (UXR3-50, 51): at 55 % alpha the ⚔ read 2.77 : 1 on the field; full
	# alpha (5.44 : 1).
	_clash_label.add_theme_color_override("font_color", Utils.UI_GOLD)
	_clash_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_stage.add_child(_clash_label)

	# Odometers — the ONLY red on the table.
	_odo_left_cap = _mk_label(_stage, "", &"Caption", Color(BONE_HEX))
	_odo_left = _mk_label(_stage, "0", &"TableauOdometer", CRIMSON, _font_engraved)
	_odo_right_cap = _mk_label(_stage, "", &"Caption", Color(BONE_HEX))
	_odo_right_cap.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_odo_right = _mk_label(_stage, "0", &"TableauOdometer", CRIMSON, _font_engraved)
	_odo_right.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	# The outcome banner — engraved capitals, register-toned, arrives LAST.
	_banner = _mk_label(_stage, "", &"TableauBanner", Utils.UI_GOLD, _font_engraved)
	_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_banner.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
	_banner.add_theme_constant_override("outline_size", 6)
	_sub_banner = _mk_label(_stage, "", &"", Color(BONE_HEX))
	_sub_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	# C2: the labels made once, here - show_diorama re-applies the held type to them
	_chrome_labels = [_odo_left_cap, _odo_left, _odo_right_cap, _odo_right, _banner, _sub_banner]


func _build_strength_band() -> void:
	"""Session UI-2: the band under the stage - per side, the nation's name and
	its strength before -> after (the figures in lining numerals), over a bar
	drawn from the outer edge inward: what stands, then what was lost (the
	table's one red), the track's full width the larger side's muster so the
	two bars compare."""
	_band = Control.new()
	_band.name = "StrengthBand"
	_band.position = Vector2(STAGE_MARGIN_X, STAGE_TOP + STAGE_H + 8.0)
	_band.size = Vector2(TRAY_W - STAGE_MARGIN_X * 2.0, BAND_H)
	_band.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_band.visible = false
	_tray_inner.add_child(_band)
	var half_w: float = _band.size.x / 2.0 - 14.0
	for i in range(2):
		var is_left := i == 0
		var x: float = 0.0 if is_left else _band.size.x - half_w
		var nm := Label.new()
		nm.theme_type_variation = &"Caption"
		nm.add_theme_color_override("font_color", BRASS)
		nm.add_theme_font_override("font", _font_engraved)
		nm.position = Vector2(x, 0.0)
		nm.size = Vector2(half_w, 18.0)
		nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT if is_left \
			else HORIZONTAL_ALIGNMENT_RIGHT
		nm.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_band.add_child(nm)
		var fg := Label.new()
		fg.theme_type_variation = &"Figure"
		fg.add_theme_color_override("font_color", Color(BONE_HEX))
		fg.position = Vector2(x, -2.0)
		fg.size = Vector2(half_w, 20.0)
		fg.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT if is_left \
			else HORIZONTAL_ALIGNMENT_LEFT
		fg.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_band.add_child(fg)
		var bar := Control.new()
		bar.position = Vector2(x, 24.0)
		bar.size = Vector2(half_w, 8.0)
		bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
		bar.draw.connect(_draw_band_bar.bind(bar, i))
		_band.add_child(bar)
		_band_names.append(nm)
		_band_figs.append(fg)
		_band_bars.append(bar)


func _draw_band_bar(bar: Control, i: int) -> void:
	if i >= _band_rows.size():
		return
	var row: Dictionary = _band_rows[i]
	var w: float = bar.size.x
	var h: float = bar.size.y
	var peak: float = maxf(float(row.get("peak", 1)), 1.0)
	# BA5-X15: a corps still unseen is not in the figure; the peak stays the full muster
	var before: float = float(row.get("before", 0)) - float(row.get("unseen", 0))
	var lost: float = float(row.get("lost", 0)) * _band_progress
	var w_before: float = w * clampf(before / peak, 0.0, 1.0)
	var w_after: float = w * clampf((before - lost) / peak, 0.0, 1.0)
	bar.draw_rect(Rect2(0.0, 0.0, w, h), Color(0.0, 0.0, 0.0, 0.42))
	var tone: Color = row.get("tone", Utils.UI_GOLD)
	if i == 1:
		bar.draw_rect(Rect2(w - w_after, 0.0, w_after, h), tone)
		bar.draw_rect(Rect2(w - w_before, 0.0, w_before - w_after, h), Color(CRIMSON, 0.62))
	else:
		bar.draw_rect(Rect2(0.0, 0.0, w_after, h), tone)
		bar.draw_rect(Rect2(w_after, 0.0, w_before - w_after, h), Color(CRIMSON, 0.62))
	bar.draw_rect(Rect2(0.0, 0.0, w, h), Color(Utils.UI_GOLD, 0.35), false, 1.0)


func _band_fig_text(i: int) -> String:
	var row: Dictionary = _band_rows[i]
	var before: int = int(roundf(float(row.get("before", 0)) - float(row.get("unseen", 0))))
	var after: int = int(roundf(float(before) - float(row.get("lost", 0)) * _band_progress))
	return "%s → %s%s" % [Utils.format_number(before), Utils.format_number(after),
		str(row.get("unit", ""))]


func set_band_unseen(i: int, men: float) -> void:
	"""BA5-X15: the men of a side's corps still unseen on the table; the band
	counts only the corps made out (the acts set it, and tween it back to 0)."""
	if i < 0 or i >= _band_rows.size():
		return
	(_band_rows[i] as Dictionary)["unseen"] = men
	if _band != null and _band_rows.size() >= 2:
		_band_figs[i].text = _band_fig_text(i)
		_band_bars[i].queue_redraw()


func _set_band_progress(p: float) -> void:
	_band_progress = p
	if _band == null or _band_rows.size() < 2:
		return
	for i in range(2):
		_band_figs[i].text = _band_fig_text(i)
		_band_bars[i].queue_redraw()


func _populate_band(left: Dictionary, right: Dictionary, final_frame: bool) -> void:
	"""The band's rows from the payload's own figures: `committed_total` (the
	fought corps' muster) and `casualties_total`; no new maths - after is
	before less the dead the odometer counts."""
	_band_rows = []
	var unit := " sail" if _is_naval() else ""
	var peak := 1
	for side in [left, right]:
		var before := int(side.get("committed_total", 0))
		if before <= 0:
			for c in side.get("contingents", []):
				if not (str(c.get("status", "")) in ABSENT_STATUSES):
					before += int(c.get("committed", 0))
		var lost := clampi(int(side.get("casualties_total", 0)), 0, maxi(before, 0))
		var tone: Color = Utils.NATION_COLORS.get(str(side.get("nation", "")),
				Utils.UI_NEUTRAL_FIGURE)
		_band_rows.append({"before": before, "lost": lost, "tone": tone, "unit": unit, "unseen": 0})
		peak = maxi(peak, before)
	for row in _band_rows:
		row["peak"] = peak
	var has_band: bool = int(_band_rows[0]["before"]) > 0 or int(_band_rows[1]["before"]) > 0
	_band.visible = has_band
	if not has_band:
		return
	var sides := [left, right]
	for i in range(2):
		_band_names[i].text = Utils.display_nation_name(
			str(sides[i].get("nation", ""))).to_upper()
	_set_band_progress(1.0 if final_frame else 0.0)


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
			STAGE_TOP + STAGE_H + 8.0 + BAND_H + BAND_GAP)
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
	# UXR-X9 (Pre-Deploy S12 part 2, part 5e): the verdict was a fit_content
	# label on a free-positioned parent, so the worst case (the longest
	# observation, the Emperor's prefix and an enemy voice: about four lines)
	# grew into the nameplate. It is a bounded room that ends above the plate
	# (`_fit_verdict_room`, once the plate is placed); text that needs more
	# scrolls inside it and rests on whole lines; the wheel reaches it (PASS)
	# and a click still falls through to the tableau's skip.
	_verdict.fit_content = false
	_verdict.scroll_active = true
	_verdict.position = Vector2(TRAY_W * 0.14, STAGE_TOP + STAGE_H + SHELF_H + 16.0)
	_verdict.size = Vector2(TRAY_W * 0.72, VERDICT_ROOM_MIN)
	_verdict.mouse_filter = Control.MOUSE_FILTER_PASS
	if _font_voice != null:
		_verdict.add_theme_font_override("normal_font", _font_voice)
		_verdict.add_theme_font_override("italics_font", _font_voice)
	_verdict.theme_type_variation = &"BodyLargeRich"
	_tray_inner.add_child(_verdict)
	Utils.keep_whole_lines(_verdict)

	# The nameplate, wax-sealed — the diorama is an OBJECT. UXR3-75 (Pre-
	# Deploy S12 part 2): a flat ENGRAVED label, the battle's name cut into
	# the walnut, with no fill, no border and no hover. The gold-filled brass
	# plate it was stood in the button row beside Replay and Close and read as
	# the main button. Same words, same place: the margins keep its size.
	_nameplate = PanelContainer.new()
	_nameplate.name = "Nameplate"
	var engraved := StyleBoxEmpty.new()
	engraved.content_margin_left = 26.0
	engraved.content_margin_right = 26.0
	engraved.content_margin_top = 5.0
	engraved.content_margin_bottom = 5.0
	_nameplate.add_theme_stylebox_override("panel", engraved)
	_nameplate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tray_inner.add_child(_nameplate)

	var plate_box := VBoxContainer.new()
	plate_box.add_theme_constant_override("separation", 0)
	_nameplate.add_child(plate_box)
	_plate_name = Label.new()
	_plate_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_plate_name.add_theme_font_override("font", _font_engraved)
	_plate_name.theme_type_variation = &"TableauPlate"
	_plate_name.add_theme_color_override("font_color", BRASS)
	# The cut: a one-pixel shadow below and right, as a letter cut into wood.
	_plate_name.add_theme_color_override("font_shadow_color", ENGRAVE)
	_plate_name.add_theme_constant_override("shadow_offset_x", 1)
	_plate_name.add_theme_constant_override("shadow_offset_y", 1)
	plate_box.add_child(_plate_name)
	_plate_sub = Label.new()
	_plate_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_plate_sub.theme_type_variation = &"Caption"
	_plate_sub.add_theme_color_override("font_color", PLATE_SUB)
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
	_btn_close.theme_type_variation = &"PrimaryButton"   # Session UI-6: Close is the primary act
	_btn_close.custom_minimum_size = Vector2(110, 34)
	_btn_close.pressed.connect(_on_close_pressed)
	_tray_inner.add_child(_btn_close)
	# UXR3-F2 (S12 part 2): the buttons stood clear of the corner filigree
	# (TRAY_W - 38 .. TRAY_W - 8); Session UI-2 retired it for the gilt frame,
	# whose cut corner lies inside its band. Close's right edge is TRAY_W - 44.
	_btn_close.position = Vector2(TRAY_W - 154.0, tray_h() - 46.0)

	_btn_replay = Button.new()
	_btn_replay.text = "Replay"
	_btn_replay.add_theme_stylebox_override("normal", _replay_face(false))   # UI-6: a gilt-rimmed face
	_btn_replay.add_theme_stylebox_override("hover", _replay_face(true))
	_btn_replay.add_theme_color_override("font_color", Utils.UI_GOLD)
	_btn_replay.add_theme_color_override("font_hover_color", Utils.UI_GOLD)
	_btn_replay.custom_minimum_size = Vector2(110, 34)
	_btn_replay.pressed.connect(_on_replay_pressed)
	_tray_inner.add_child(_btn_replay)
	_btn_replay.position = Vector2(TRAY_W - 274.0, tray_h() - 46.0)

	_skip_hint = _mk_label(_tray_inner, "click anywhere to skip ▸", &"Caption",
			Color(Utils.COLOR_DIMMED))
	_skip_hint.theme = null      # C3: stands beside Close and Replay, which render at the full size
	_skip_hint.position = Vector2(22.0, tray_h() - 40.0)


func _replay_face(hover: bool) -> StyleBox:
	"""Session UI-6: Replay is the secondary button - a dark face with a gilt rim
	(the primary Close beside it is gilt-filled)."""
	var st := StyleBoxFlat.new()
	st.bg_color = Utils.UI_REPLAY_FACE_HOVER if hover else Utils.UI_REPLAY_FACE
	st.border_color = Utils.UI_GOLD
	st.set_border_width_all(2 if hover else 1)
	st.set_corner_radius_all(3)
	st.content_margin_left = 12.0
	st.content_margin_right = 12.0
	st.content_margin_top = 6.0
	st.content_margin_bottom = 6.0
	return st


func _line_extra() -> float:
	"""BA1-X4: how much taller a Caption line is than the shipped 115 % line (0 at 100 % and
	115 %, so those stay pixel for pixel what they were): what every fixed pitch of
	the tableau's stacked lines is lengthened by at Text size 130 % and up."""
	_fit_tableau_type()
	var probe := Label.new()
	probe.theme_type_variation = &"Caption"
	probe.text = "Mg"
	probe.theme = _tableau_theme        # the type the baize's own lines are read in
	add_child(probe)
	var h: float = probe.get_minimum_size().y
	probe.queue_free()
	return maxf(h - LINE_H_SHIPPED, 0.0)


# BA1-X4: the baize is a fixed 948 x 440 surface and its small type is a fixed step
# beyond TABLEAU_TEXT_CAP (as its display type is at every size): Text size scales the
# tableau's lines up to a 130 % step, where the walk holds every claim, and the
# stage keeps that step above it - the plate's verdict, the day's panel, the band
# and the buttons below the baize keep the player's whole size.
const TABLEAU_TEXT_CAP := 1.3
const TABLEAU_TEXT_STEPS := {"Caption": 14, "Label": 16, "Lead": 18, "BodyLarge": 17}


var _tableau_theme: Theme = null
var _chrome_labels: Array = []      # C2: the persistent chrome labels _mk_label built once


func _refit_chrome_type() -> void:
	"""C2: a Text size change in Settings between two showings re-holds (or releases)
	the persistent chrome labels' type; a fixed display variation never carries it."""
	for l in _chrome_labels:
		if l != null and is_instance_valid(l):
			var fixed := String((l as Label).theme_type_variation) in Utils.TEXT_SIZE_FIXED_STEPS
			(l as Label).theme = null if fixed else _tableau_theme
var _tableau_theme_for := -1.0


func _fit_tableau_type() -> void:
	"""BA1-X4: the ladder's steps the baize's lines read in, held at the cap (a Theme the
	tableau's own labels carry: they stand under Node2D blocks, which pass no theme down).
	Nothing is held at or under the cap: 100 % and 115 % are the project theme."""
	var factor: float = Utils.text_size_factor()
	if is_equal_approx(factor, _tableau_theme_for):
		return
	_tableau_theme_for = factor
	_tableau_theme = null
	if factor <= TABLEAU_TEXT_CAP + 0.001:
		return
	var held := Theme.new()
	for step in TABLEAU_TEXT_STEPS:
		held.set_font_size(&"font_size", StringName(step),
				Utils.text_px(int(TABLEAU_TEXT_STEPS[step]), TABLEAU_TEXT_CAP))
	_tableau_theme = held


func dice_room_h() -> float:
	"""BA1-X4: the room the dice tray's die and three lines need: the shipped 106 at the sizes
	it has always served (100 %, 115 %), and above that the die, the three Caption lines
	and their gaps - so the luck line is not the one left off. The crossed swords stand
	below it (`_populate`)."""
	var extra := _line_extra()
	if extra <= 0.0:
		return 106.0
	# the swords may be pushed down only so far: at Text size 175 % the lead's name
	# (taller too) stands at their foot, so that size keeps the first two lines
	# (guard for a future cap above 1.3: the type is held at 130 %, so this branch is not
	# reached today - kept so a higher TABLEAU_TEXT_CAP cannot push the swords into the lead's name)
	if extra > CLASH_PUSH_MAX_EXTRA:
		return 106.0
	return maxf(106.0, 30.0 + 5.0 + 3.0 * (LINE_H_SHIPPED + extra + 1.0))


func _mk_label(parent: Node, text: String, variation: StringName, color: Color,
		font: Font = null) -> Label:
	"""UXR-X5 (UXR-2, October 12, 2026): a tableau label takes a THEME size —
	`&"Caption"` (14) for the small lines, `&""` for the body (16) — never a
	design-px number. The tray is a scaled surface; its type is not, and a
	number passed here was how the 10/11/12-px lines escaped the floor's
	census (it read only literal overrides). The four engraved display
	sizes (odometer 24, banner 30) are set by their callers."""
	_fit_tableau_type()
	var l := Label.new()
	# C1: the held theme sets a font_size for base type Label, which would override a fixed
	# display variation (banner 30, odometer 24 ...): those labels carry no held theme.
	l.theme = null if String(variation) in Utils.TEXT_SIZE_FIXED_STEPS else _tableau_theme
	l.text = text
	if variation != &"":
		l.theme_type_variation = variation
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
	if _felt_tex == null and ResourceLoader.exists(FELT_TILE):
		_felt_tex = load(FELT_TILE)
	if _felt_tex != null and not naval:
		# BA-6: the felt's own nap, tiled (the table's green, a photograph's grain)
		_stage_canvas.draw_texture_rect(_felt_tex, r.grow(-5.0), true)
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
	if _line_extra() > 0.0:                # BA1-X4: the swords stand below the dice tray's room
		_clash_label.position.y = maxf(_clash_label.position.y, 74.0 + dice_room_h() + 4.0)
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
	var cap_extra := _line_extra()          # BA1-X4: the count stands under its caption's own height
	_odo_left.position = Vector2(14.0, 22.0 + cap_extra)
	_odo_right_cap.size = Vector2(220.0, 16.0)
	_odo_right_cap.position = Vector2(sw - 234.0, 8.0)
	_odo_right.size = Vector2(220.0, 30.0)
	_odo_right.position = Vector2(sw - 234.0, 22.0 + cap_extra)
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

	# The strength band, and the verdict's top under whatever the shelves hold.
	_populate_band(left, right, final_frame)
	var shelf_up: bool = (_shelf_left != null and _shelf_left.visible) \
		or (_shelf_right != null and _shelf_right.visible)
	_verdict.position.y = STAGE_TOP + STAGE_H + 8.0 + BAND_H + BAND_GAP \
		+ (SHELF_H + 8.0 if shelf_up else 0.0)

	# Verdict + nameplate.
	_verdict.text = ""
	_nameplate_layout()
	_laurel_layout(register)

	_btn_replay.disabled = false
	_btn_close.disabled = false
	_btn_replay.visible = final_frame
	_btn_close.visible = final_frame
	_skip_hint.visible = not final_frame

	# Row BA (BA-1): the Blend look and the acts — a plinth under every corps,
	# the dice tray, and either the settled frame or the acts' opening places.
	_acts = BattleActs.new(self)
	_acts.dress(final_frame)


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

	# SF7-X23 (Score Finish Step 7, the frames, Oct 4 2026): the steps were
	# fixed at 118px outward and 66px up, so the cap's FOURTH contingent sat
	# at x ≈ −8 on the ~950px baize and its locket climbed into the
	# odometer — measured live: Lannes drawn outside the tableau's frame at
	# the Second Battle of Swabia. The steps now shrink to fit the count:
	# the outermost locket (≈100px outboard and ≈158px above the feet, both
	# scaled with the block) stays on the baize and under the odometers.
	var step_x := 118.0
	var step_y := 66.0
	var n := fought.size()
	if THE_LINE_FITS_THE_BAIZE and n > 1:
		var last_scale := 1.0 - 0.12 * (n - 1)
		step_x = minf(step_x, maxf(40.0,
				(sw / 2.0 - 128.0 - 100.0 * last_scale - 16.0) / float(n - 1)))
		step_y = minf(step_y, maxf(30.0,
				(base_y - 60.0 - 158.0 * last_scale) / float(n - 1)))
	for i in range(n):
		var c: Dictionary = fought[i]
		var depth_x := 128.0 + step_x * i
		var x := sw / 2.0 - depth_x if is_left else sw / 2.0 + depth_x
		var pos := Vector2(x, base_y - step_y * i)
		var block_scale := 1.0 - 0.12 * i
		# UXR3-F2 (Pre-Deploy S12 part 2): at three and four ranks the steps
		# narrow and a deeper rank's 86-px standard flew beside the NEXT
		# rank's name and strength lines (Austria's colours by Kutuzov,
		# Russia's by Archduke Charles). Its pole is cut so the flag flies
		# below the forward rank's strength line, among its own men. Part
		# 5d: at two ranks too — Davout's colours flew over Ney's portrait
		# on the closing re-read's `diorama_aadj` frame.
		var pole := STANDARD_POLE
		if n >= 2 and i > 0:
			var fwd_scale := 1.0 - 0.12 * (i - 1)
			var clear_top := 156.0 * fwd_scale - (TEXT_PITCH + 19.0) - 4.0 - step_y - _line_extra()
			# the art is scaled by block_scale; the pole is drawn in art units
			pole = clampf(clear_top / maxf(block_scale, 0.01), STANDARD_POLE_MIN, STANDARD_POLE)
		blocks.append(_make_block(holder, c, pos, block_scale, is_left, i, pole))

	# The honest tail: corps the cap could not seat.
	var reserve := int(side.get("reserve_count", 0))
	if reserve > 0:
		# NV-9: "corps" is a land word — a sea overflow is squadrons.
		var reserve_word := "squadrons astern" if _is_naval() else "corps in reserve"
		var tail_text := "+%d %s" % [reserve, reserve_word]
		# SF7-X29: what the unseated corps lost rides the tail, so the
		# figures on the baize and the odometer over them add up.
		var reserve_dead := int(side.get("reserve_casualties", 0))
		if reserve_dead > 0:
			tail_text += " — %s lost" % Utils.format_number(reserve_dead)
		var tail := _mk_label(_stage, tail_text, &"Caption",
				Color(Utils.COLOR_DIMMED))
		# The right-hand tail is right-aligned to the stage by its own width
		# (the longer SF7-X29 line would run off a fixed `sw - 150`).
		var right_x := sw - 150.0
		if THE_RESERVE_NAMES_ITS_DEAD:
			right_x = minf(right_x, sw - tail.get_minimum_size().x - 14.0)
		# UXR-X5: the tail sits in the baize's OUTBOARD BOTTOM corner, over
		# the reserve shelf. It used to follow the steps one rank beyond
		# the last (`base_y - step_y * n - 8`), which at four ranks is the
		# depth-2 rank's name row — at the floor's 14 px the line ran
		# across that name. The corner holds nothing at any count.
		tail.position = Vector2(
			14.0 if is_left else right_x,
			_stage.size.y - BAIZE_PAD - tail.get_minimum_size().y)
		_transients.append(tail)
	return blocks


# Labels created per-populate outside the holders — cleared with the table.
var _transients: Array = []


func _make_block(holder: Node2D, c: Dictionary, pos: Vector2,
		block_scale: float, is_left: bool, depth: int,
		pole: float = STANDARD_POLE) -> Dictionary:
	"""One corps: a rank of figures, its standard, the locket, the labels.
	Returns the block record the sequence animates."""
	var block := Node2D.new()
	block.position = pos
	block.z_index = 20 - depth
	holder.add_child(block)
	# UXR-X5: the block itself is unscaled; its ART recedes with depth. The
	# labels are the block's own children, so they read at the theme's size
	# at every depth — and never through a 1/scale counter-scale, whose float
	# product lands a hair under 1.0 and reads a 14-px caption as 13.99999.
	var art := Node2D.new()
	art.name = "Art"
	art.scale = Vector2(block_scale, block_scale)
	block.add_child(art)

	var facing := "r" if is_left else "l"
	var arm := str(c.get("arm", "infantry"))
	var nation := str(c.get("nation", ""))
	var color_key := str(c.get("origin_nation", nation))
	var nation_color: Color = Utils.NATION_COLORS.get(
		color_key, Utils.UI_NEUTRAL_FIGURE)

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
	var spread := 84.0 if arm == "ship" else 42.0
	var rear := count - mini(count, 3)
	for j in range(rear):
		var f := DioramaFigure.new()
		f.setup(arm, facing, nation_color, fig_px * 0.94)
		f.position = Vector2((j - (rear - 1) / 2.0) * spread + 6.0, -22.0)
		art.add_child(f)
		figures.append(f)
	for j in range(mini(count, 3)):
		var f := DioramaFigure.new()
		f.setup(arm, facing, nation_color, fig_px)
		f.position = Vector2((j - (mini(count, 3) - 1) / 2.0) * spread, 0.0)
		art.add_child(f)
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
		standard = _make_standard(nation_color, color_key, is_left, pole)
		standard.position = Vector2(38.0 if is_left else -38.0, 0.0)
		art.add_child(standard)

	# Locket + labels above the block (Control children of the Node2D).
	# Left side: locket outboard-left, text flows right toward the line.
	# Right side mirrored: text right-aligned, locket outboard-right.
	var locket := PortraitLocket.new()
	locket.setup(str(c.get("name", "")), 38.0, bool(c.get("crowned", false)),
			bool(c.get("sovereign", false)))
	locket.position = Vector2(-86.0 if is_left else 48.0, -158.0)
	art.add_child(locket)

	var text_align := HORIZONTAL_ALIGNMENT_LEFT if is_left \
		else HORIZONTAL_ALIGNMENT_RIGHT
	# UXR-X5: the text's ALIGNED edge follows the art (the left column's text
	# starts at −42·b, the right column's ends at 40·b — where the depth-0
	# layout put them, receding with the block); its size does not.
	var text_w := 150.0 if is_left else 226.0
	var text_x := -42.0 * block_scale if is_left else 40.0 * block_scale - text_w
	var text_y := -156.0 * block_scale

	var lead_mark := " ◆" if bool(c.get("lead", false)) else ""
	# LV-2 (row EP F2): the printed name; the locket keeps the raw key
	# (its portrait is looked up by it).
	var name_l := _mk_label(block, Utils.display_marshal_name(str(c.get("name", ""))) + lead_mark, &"",
			Color(GOLD_HEX))
	name_l.position = Vector2(text_x, text_y)
	name_l.size = Vector2(text_w, 22.0)
	name_l.horizontal_alignment = text_align
	name_l.z_index = TEXT_Z
	_outline_over_colours(name_l)

	var remaining := int(c.get("remaining", 0))
	# NV-7: a squadron is counted in sail, and 45 → 38 needs the unit said
	# out loud or it reads as a rout of thirty-eight men.
	var unit := " sail" if str(c.get("arm", "")) == "ship" else ""
	# LV-11 (row EP F2): the lead's locked figure, then the advance's toll
	# when the backend stamped one — the next diorama opens him at the
	# number this one closed on.
	var after_advance := ""
	if c.has("after_advance") and int(c.get("advance_losses", 0)) > 0:
		after_advance = " → %s after the advance" % Utils.format_number(int(c.get("after_advance", 0)))
	var strength_l := _mk_label(
		block, "%s → %s%s%s" % [Utils.format_number(committed),
		Utils.format_number(remaining), unit, after_advance], &"Caption", Color(BONE_HEX))
	var line_extra := _line_extra()         # BA1-X4
	strength_l.position = Vector2(text_x, text_y + TEXT_PITCH + line_extra)
	strength_l.size = Vector2(text_w, 19.0 + line_extra)
	strength_l.horizontal_alignment = text_align
	strength_l.z_index = TEXT_Z
	_outline_over_colours(strength_l)

	# UXR-X5: the FATE line — under the feet, outboard, where the faith
	# caption already sat (IQ-5 review B): a third row above the feet at
	# the floor's size lands on the next rank's locket, two do not.
	var fate_y := FAITH_CAPTION_Y * block_scale
	var status_l: Label = null
	if status in ["routed", "destroyed"]:
		# NV-8b: the sea has its own words — a squadron STRIKES her
		# colours; a squadron lost is SUNK. "ROUTED" is a land verb.
		var status_word := status.to_upper()
		if _is_naval():
			status_word = "STRUCK" if status == "routed" else "SUNK"
		status_l = _mk_label(block, status_word, &"Caption", CRIMSON)
		status_l.visible = false
	elif status == "reinforced":
		status_l = _mk_label(block, "marched to the guns", &"Caption",
				Color(0.55, 0.65, 0.5))
	if status_l != null:
		status_l.size = Vector2(FAITH_CAPTION_W, 19.0)
		if is_left:
			status_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			status_l.position = Vector2(FAITH_CAPTION_INBOARD * block_scale - FAITH_CAPTION_W,
					fate_y)
		else:
			status_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
			status_l.position = Vector2(-FAITH_CAPTION_INBOARD * block_scale, fate_y)
		_keep_fate_on_baize(status_l, pos, is_left)
		status_l.z_index = TEXT_Z
		fate_y += FATE_PITCH + line_extra

	# IQ-5 / PR-X3 (R11): a man whose faith in you is spent brought less
	# than his whole weight to this field. The optional `faith` caption says
	# so, in the voice and colour of the shelf's `grudge` caption. The
	# `committed` figure above is deliberately left as it is — the caption
	# explains it, it does not restate it. Absent key → nothing drawn.
	#
	# IQ-5 review (B): sited UNDER the corps' figures, outboard, wrapped. It
	# used to be a fourth row of the text stack, and the stack has room for
	# three: the lead block stands 66px lower and 118px toward the clash, so
	# a reinforcer's fourth row landed on the LEAD's locket and name (measured
	# headless on the real tableau: 38x7 and 36x5 px) and, because `size` was
	# set before `autowrap_mode`, it never wrapped at all — one ~420px line
	# into the opposing half. Below the feet and away from the clash line,
	# the caption meets nothing at depth 1 or 2 on either side (the sweep's
	# y=+22 still grazed a fallen figure by 1px; +30 is clear). Autowrap is
	# set FIRST and the width is a minimum, so the label wraps inside it.
	var faith_v = c.get("faith", null)
	var faith := str(faith_v) if faith_v is String else ""
	if faith != "":
		var faith_l := _mk_label(block, faith, &"Caption",
				Color(0.90, 0.68, 0.64, 1.0), _font_voice)
		faith_l.theme_type_variation = &"BodyLarge"   # Session UI-6: the italic caption at the body step
		faith_l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		faith_l.custom_minimum_size = Vector2(FAITH_CAPTION_W, 0.0)
		faith_l.size = Vector2(FAITH_CAPTION_W, 14.0)
		if is_left:
			faith_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			faith_l.position = Vector2(FAITH_CAPTION_INBOARD * block_scale - FAITH_CAPTION_W,
					fate_y)
		else:
			faith_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
			faith_l.position = Vector2(-FAITH_CAPTION_INBOARD * block_scale, fate_y)
		_keep_fate_on_baize(faith_l, pos, is_left)
		faith_l.z_index = TEXT_Z

	return {
		"node": block, "data": c, "figures": figures,
		"falling": falling, "standing": standing,
		"standard": standard, "locket": locket, "status_label": status_l,
		"is_left": is_left, "status": status, "depth": depth,
	}


func _outline_over_colours(l: Label) -> void:
	"""UXR-X7: at four ranks the steps narrow and the next rank's colours
	stand behind a name or a strength line; the text draws above them
	(TEXT_Z) and a thin dark rim keeps bone-on-white legible. On the bare
	baize the rim is all but invisible."""
	l.add_theme_color_override("font_outline_color", Color(0.0, 0.0, 0.0, 0.85))
	l.add_theme_constant_override("outline_size", 3)


func _keep_fate_on_baize(l: Label, block_pos: Vector2, is_left: bool) -> void:
	"""UXR-X5: an outer contingent's fate caption (status, faith) must not
	hang off the baize — at four contingents the outermost block stands
	~80 px from the stage edge and a 150-px caption box reached past it.
	The caption's INBOARD edge (where its aligned text sits) stays; its
	outboard edge is cut back to the baize margin, so the text wraps
	narrower instead of sliding inboard onto the next rank's figures."""
	var w := l.size.x
	if is_left:
		var inboard := l.position.x + w
		var outboard := maxf(l.position.x, BAIZE_PAD - block_pos.x)
		w = maxf(inboard - outboard, FATE_MIN_W)
		l.custom_minimum_size.x = minf(l.custom_minimum_size.x, w)
		l.size.x = w
		l.position.x = inboard - w
	else:
		var outboard_r := minf(l.position.x + w,
				_stage.size.x - BAIZE_PAD - block_pos.x)
		w = maxf(outboard_r - l.position.x, FATE_MIN_W)
		l.custom_minimum_size.x = minf(l.custom_minimum_size.x, w)
		l.size.x = w


func _make_standard(nation_color: Color, flag_key: String,
		is_left: bool, pole_h: float = STANDARD_POLE) -> Node2D:
	"""A corps standard: a real pole with the nation's own colours flying —
	the one saturated element on a wood figure, which is exactly why it is
	the thing that falls."""
	var std := Node2D.new()
	std.name = "Standard"
	std.z_index = 3

	var pole := Line2D.new()
	pole.points = PackedVector2Array([Vector2(0, 0), Vector2(0, -pole_h)])
	pole.width = 2.4
	pole.default_color = Color(0.32, 0.24, 0.14, 1.0)
	std.add_child(pole)
	# Finial.
	var finial := Line2D.new()
	finial.points = PackedVector2Array([Vector2(0, -pole_h), Vector2(0, -pole_h - 6.0)])
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
		spr.position = Vector2(1.0 if is_left else -1.0 - flag_w, -pole_h)
		std.add_child(spr)
	else:
		var pennant := Polygon2D.new()
		var dir := 1.0 if is_left else -1.0
		pennant.polygon = PackedVector2Array([
			Vector2(1.0 * dir, -pole_h), Vector2(30.0 * dir, -pole_h + 6.0),
			Vector2(1.0 * dir, -pole_h + 16.0)])
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
				Utils.UI_NEUTRAL_FIGURE), SHELF_FIGURE_PX)
		f.position = Vector2(23.0, SHELF_H - 16.0)
		f.grey_out()
		cell.add_child(f)

		var text_box := VBoxContainer.new()
		text_box.add_theme_constant_override("separation", 0)
		text_box.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(text_box)
		var head := Label.new()
		head.text = "%s — %s" % [Utils.display_marshal_name(str(c.get("name", ""))),
				str(c.get("absence_reason", "did not march"))]
		head.theme_type_variation = &"Caption"
		head.add_theme_color_override("font_color",
				Utils.UI_ABSENT_FIGURE)
		text_box.add_child(head)
		var grudge := str(c.get("grudge", ""))
		if grudge != "":
			var g := Label.new()
			g.text = grudge
			if _font_voice != null:
				g.add_theme_font_override("font", _font_voice)
			g.theme_type_variation = &"BodyLarge"   # UI-6: the italic caption at the body step
			g.add_theme_color_override("font_color",
					Color(0.90, 0.68, 0.64, 1.0))
			text_box.add_child(g)
		# IQ-5 review (B): no `faith` caption here. The shelf holds only the
		# ABSENT statuses, and the backend attaches `faith` only to a man
		# who stood on the field (`status not in ABSENT_STATUSES`) — a man
		# who never came brought none of his weight. The arm that read it
		# here was unreachable, and its comment ("drawn wherever the
		# contingent is, the line or the shelf") was false.


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
		(TRAY_W - plate_size.x) / 2.0, tray_h() - plate_size.y - 12.0)
	_fit_verdict_room()
	if _seal != null:
		# Session UI-2: the seal stands LEFT of the plate, clear of Replay / Close
		# (at the plate's right it met Replay whenever the plate ran wide).
		_seal.position = _nameplate.position + Vector2(-56.0, plate_size.y / 2.0 - 22.0)


func _fit_verdict_room() -> void:
	"""UXR-X9: the verdict's room ends VERDICT_PLATE_GAP above the plate."""
	if _verdict == null or _nameplate == null:
		return
	var room: float = _nameplate.position.y - VERDICT_PLATE_GAP - _verdict.position.y
	_verdict.size = Vector2(_verdict.size.x, maxf(room, VERDICT_ROOM_MIN))


func _laurel_layout(register: String) -> void:
	var is_triumph := register == "triumph"
	for laurel in [_laurel_l, _laurel_r]:
		if laurel != null:
			laurel.visible = is_triumph
	if is_triumph and _laurel_l != null:
		await get_tree().process_frame
		# BA1-X8 (closed in row BA, BA-5, November 17, 2026): the laurels flank
		# the BANNER that announces the triumph, on the baize. They flanked the
		# plate — but Session UI-2 had since stood the wax seal at the plate's
		# left (the left laurel lay on it) and Replay comes up at its right (the
		# right laurel lay under the button); no place on that row clears the
		# seal and two buttons at every plate width. The banner's row has the
		# two loss counters at its ends and nothing between them but its words.
		var words: float = _banner.get_minimum_size().x
		var mid: float = _stage.position.x + _stage.size.x / 2.0
		var y: float = _stage.position.y + _banner.position.y \
			+ (_banner.size.y - LAUREL_PX) / 2.0
		# (row BA, BA-5, the second reading: the line under the headline names the
		# moment a line broke, and runs wider than a short headline with its laurels)
		# the laurels end where that line begins
		if _sub_banner.text != "":
			y = minf(y, _stage.position.y + _sub_banner.position.y - LAUREL_PX)
		_laurel_l.position = Vector2(mid - words / 2.0 - LAUREL_GAP - LAUREL_PX, y)
		_laurel_r.position = Vector2(mid + words / 2.0 + LAUREL_GAP, y)


# ─────────────────────────────────────────────────────────────────────────────
# Copy — the register owns the words
# ─────────────────────────────────────────────────────────────────────────────

func _decisive() -> bool:
	# NV-9: a fleet action ALWAYS carries a victor, so the land grammar
	# ("attacker_victory" == decisive) made every sea action decisive —
	# the indecisive banner was dead code, and a squadron that merely had
	# the better of it read "THE SEA IS OURS" while the Admiralty said the
	# enemy drew off in order, on the same screen. §4.4 computes the real
	# answer (ratio >= 1.5) and the payload carries it.
	if _is_naval():
		return bool(_data.get("decisive", false))
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
	# S14G-X10 (Pre-Deploy S14h part 1, October 26, 2026): a liberation is
	# not a fall - the province went back to its home nation, and the payload
	# carries the backend's own sentence (`liberation_line`, built with
	# `liberated_to` from the battle event): "Munich, Bavaria's capital,
	# retaken — handed back to Bavaria." in every register.
	var liberation := str(_data.get("liberation_line", ""))
	if str(_data.get("liberated_to", "")) != "" and liberation != "" and liberation != "<null>":
		return liberation
	var victor_nation := _victor_nation()
	match register:
		"triumph":
			return "%s falls to %s." % [region,
				Utils.display_nation_name(victor_nation)]
		"defeat":
			return "%s is lost." % region
		_:
			return "%s changes hands." % region


func _play_arm_flavor() -> void:
	"""Cinematic flavor by arms on the field: a musket volley for the foot,
	hooves for the horse — scheduled just behind the cannon reveal, and
	skipped entirely when battle sounds are off or the tableau is naval."""
	if not UiSettings.get_battle_sfx() or _is_naval():
		return
	var has_infantry := false
	var has_cavalry := false
	for side in _side_payloads():
		for c in (side as Dictionary).get("contingents", []):
			match str(c.get("arm", "")):
				"infantry":
					has_infantry = true
				"cavalry":
					has_cavalry = true
	if has_infantry:
		get_tree().create_timer(0.9).timeout.connect(func():
			if is_instance_valid(self) and visible:
				_cue("musket_volley"))
	if has_cavalry:
		get_tree().create_timer(1.6).timeout.connect(func():
			if is_instance_valid(self) and visible:
				_cue("cavalry")
				get_tree().create_timer(1.2).timeout.connect(func():
					if is_instance_valid(self) and visible:
						_cue("whinny")))


# ─────────────────────────────────────────────────────────────────────────────
# The cinematic
# ─────────────────────────────────────────────────────────────────────────────

func _play_cinematic() -> void:
	_final = false
	_kill_sequence()

	# Row BA (BA-1): a land battle that carries a script plays in acts; a
	# fleet action, or a payload from before the acts, plays the sequence below.
	if _acts != null and _acts.plays():
		_acts.play()
		return

	# Reveal: the tray settles into view under one cannon thud.
	_tray.modulate.a = 0.0
	_cue("cannon")
	_play_arm_flavor()
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
						func(): _cue("drum_sting")) \
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
						func(): _cue("drum_sting")) \
						.set_delay(at + 0.5)
				break


func _animate_odometers(start: float, span: float) -> void:
	var sides := _side_payloads()
	var left_total := int(sides[0].get("casualties_total", 0))
	var right_total := int(sides[1].get("casualties_total", 0))
	_seq.parallel().tween_method(
		func(v: float): _set_band_progress(v),
		0.0, 1.0, span).set_delay(start) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
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
			voice, "e0d8c4")  # Session UI-5 interim fix (Nov 13): >= 4.5:1 on the tray, not the faint grey
	return text


func _type_verdict() -> void:
	var bb := _verdict_bbcode()
	if bb == "":
		return
	_verdict.text = bb
	_verdict.visible_characters = 0
	var total := _verdict.get_total_character_count()
	if UiSettings.get_battle_sfx():
		AudioManager.start_loop("scribble_verdict")  # the verdict is written, not spoken (UI-5: its own tag — the shared one let the close cut the command line's quill)
		match str(_data.get("register", "")):
			"triumph":
				_cue("fanfare")
			"defeat":
				_cue("bell_toll")
	var tw := create_tween()
	tw.tween_method(
		func(v: float): _verdict.visible_characters = int(v),
		0.0, float(total), clampf(total / 34.0, 0.8, 2.6))
	tw.finished.connect(func(): AudioManager.stop_loop("scribble_verdict"))


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
	_set_band_progress(1.0)
	_banner.visible = true
	_banner.modulate.a = 1.0
	_banner.scale = Vector2.ONE
	if _sub_banner.text != "":
		_sub_banner.visible = true
		_sub_banner.modulate.a = 1.0
	_verdict.text = _verdict_bbcode()
	_verdict.visible_characters = -1
	# Row BA: the plinths' pips, a beaten corps driven back, the dice at rest.
	if _acts != null:
		_acts.settle()


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


func _cue(cue: String) -> void:
	"""Play one diorama cue through the shared AudioManager.

	UX23-R6. This used to be `_play_sound(path, db)` driving a private
	`AudioStreamPlayer` — a second audio implementation that bypassed the
	`CUES` registry, the throttle, the one-shot budget and `max_s`. Both files
	were ALREADY registered cues (`cannon`, `drum_sting`) with byte-identical
	trims, so routing changes no audible level.

	The toggle guard stays HERE, and that is the whole point: the routed row
	claimed "the next diorama sound will forget the toggle guard" and had it
	exactly backwards — the guard is inherited by anything added to this
	function, while `AudioManager._play_cue` has never read
	`UiSettings.get_battle_sfx()` at all. Routing the calls naively, as the row
	instructed, would have silently disabled the "Battle sounds" setting."""
	if not UiSettings.get_battle_sfx():
		return
	var p := AudioManager.play(cue)
	# The PLAYER, not the cue name (review round): claiming a name made the
	# close a global kill that would have silenced another surface's play of
	# the same sound. Deduped, because `_play_cinematic` runs again on Replay
	# and an un-deduped list asks the manager to stop one player twice.
	if p != null and not _own_cues_started.has(p):
		_own_cues_started.append(p)


func keep_battle_speed(speed: String) -> void:
	"""Row BA, BA-5: the table's own ×1 / ×2 switch was pressed. The acts' helper
	is display-only and writes no setting; the tableau does, in the same key
	Settings → Interface → Battle speed writes."""
	UiSettings.set_battle_speed(speed)


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
	# S14E-21: Esc is "close", always, in ONE press. It used to share an arm
	# with Enter/Space — skip while the cinematic plays, close once settled —
	# so a player who pressed Esc to leave needed two presses, and the second
	# (or, after the close, the command line's silent release and the one
	# after) opened the pause menu by accident. Space / Enter / a click still
	# skip first, then close.
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_on_close_pressed()
		return
	if event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		if _final:
			_on_close_pressed()
		else:
			_skip_to_final()


func _on_replay_pressed() -> void:
	_populate(false)
	_play_cinematic()


func _exit_tree() -> void:
	# BA6-X3: a table that leaves the tree without its Close (freed by its owner, the
	# walk's teardown) must not leave the verdict's quill scratching over the next table
	AudioManager.stop_loop("scribble_verdict")


func _on_close_pressed() -> void:
	set_day_room(0.0)
	_kill_sequence()
	AudioManager.stop_loop("battle_bed")
	AudioManager.stop_loop("sea")
	AudioManager.stop_loop("creak")
	AudioManager.stop_loop("scribble_verdict")
	# UX23-R1/R6: the one-shots too — they are children of the AudioManager
	# singleton, so closing the tableau never used to silence its own guns.
	for p in _own_cues_started:
		AudioManager.stop_player(p)
	_own_cues_started.clear()
	if _music_ducked:
		_music_ducked = false
		AudioManager.duck_music(false)
	hide()
	dismissed.emit()

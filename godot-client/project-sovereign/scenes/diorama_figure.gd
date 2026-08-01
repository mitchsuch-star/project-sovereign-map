extends Node2D
class_name DioramaFigure

# =============================================================================
# PROJECT SOVEREIGN — Battle Diorama figure (row BD)
# =============================================================================
# One carved-wood figure on the tableau's baize — the SAME four-layer sprites
# and texture cache as the map's WarTablePiece (one identity, two surfaces),
# with the one thing a tableau figure needs that a map standee never does:
# it can FALL.
#
# The topple verb is the eval's fixed one (§4-6): rotate ~78° about the feet
# AND desaturate+darken AND cast a fresh long shadow — while the turned base
# disc and its baked ground shadow STAY PUT. Opacity-ghosting is deliberately
# not available: a fallen soldier is wood on the table, not an erasure.
#
# Display-only (Golden Rule 6): fed once from the diorama payload, never
# reads or writes game state.
# =============================================================================

const TILT_LAYERS := ["coat", "body"]      # what falls
const GROUND_LAYERS := ["shadow", "base"]  # what stays

# The fall: ~78 degrees, darkened toward bare timber, a long cast shadow.
const TOPPLE_DEG := 78.0
const TOPPLE_TINT := Color(0.52, 0.47, 0.44, 1.0)
const GREY_TINT := Color(0.62, 0.62, 0.66, 0.9)   # the no-show shelf wash
const LONG_SHADOW_STRETCH := 2.3

var arm: String = "infantry"
var facing: String = "r"
var toppled := false

var _tilt: Node2D = null            # rotates about the ground origin
var _tilt_sprites := {}             # layer -> Sprite2D (falls)
var _ground_sprites := {}           # layer -> Sprite2D (stays)
var _base_shadow_scale := Vector2.ONE
var _tween: Tween = null


func setup(arm_key: String, facing_key: String, nation_color: Color,
		frame_px: float) -> void:
	arm = arm_key if arm_key in WarTablePiece.VALID_ARMS else "infantry"
	facing = facing_key if facing_key in ["r", "l"] else "r"

	var s := frame_px / WarTablePiece.SPRITE_FRAME
	scale = Vector2(s, s)
	var offset := Vector2(-WarTablePiece.SPRITE_FRAME / 2.0,
			-WarTablePiece.SPRITE_GROUND_Y)

	_tilt = Node2D.new()
	_tilt.name = "Tilt"

	for layer in WarTablePiece.LAYER_ORDER:
		var spr := Sprite2D.new()
		spr.name = layer.capitalize()
		spr.centered = false
		spr.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		spr.texture = WarTablePiece.layer_texture(arm, layer, facing)
		spr.position = offset
		if layer in TILT_LAYERS:
			_tilt.add_child(spr)
			_tilt_sprites[layer] = spr
		else:
			add_child(spr)
			_ground_sprites[layer] = spr

	add_child(_tilt)  # after ground layers -> the man draws over his base

	var coat: Sprite2D = _tilt_sprites.get("coat")
	if coat != null:
		coat.modulate = WarTablePiece.legible_tint(nation_color)


func pop_in(delay: float, duration := 0.18) -> void:
	# The figures are PLACED on the table at reveal — a quick settle, not a
	# fade (they are objects, not apparitions).
	modulate.a = 0.0
	var from_scale := scale
	scale = from_scale * 0.86
	var tw := create_tween()
	tw.tween_interval(delay)
	tw.tween_property(self, "modulate:a", 1.0, duration * 0.6)
	tw.parallel().tween_property(self, "scale", from_scale, duration) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func lean_in(px: float, delay: float) -> void:
	# The lines close: a small resolute step toward the clash.
	var dir := 1.0 if facing == "r" else -1.0
	var tw := create_tween()
	tw.tween_interval(delay)
	tw.tween_property(self, "position:x", position.x + dir * px, 0.3) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


func topple(delay: float, instant := false) -> void:
	"""The fall. Rotation direction is BACKWARD — away from the enemy the
	figure faces — so a breaking line visibly gives ground."""
	if toppled or _tilt == null:
		return
	toppled = true
	var dir := -1.0 if facing == "r" else 1.0
	var target_rot := deg_to_rad(TOPPLE_DEG) * dir

	var shadow: Sprite2D = _ground_sprites.get("shadow")
	var long_shadow := Vector2(_base_shadow_scale.x * LONG_SHADOW_STRETCH,
			_base_shadow_scale.y)

	if instant:
		_tilt.rotation = target_rot
		_tilt.modulate = TOPPLE_TINT
		if shadow != null:
			shadow.scale = long_shadow
			shadow.modulate.a = 0.85
		return

	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = create_tween()
	_tween.tween_interval(delay)
	# The fall itself: fast, slightly past, settle — wood hitting felt.
	_tween.tween_property(_tilt, "rotation", target_rot, 0.34) \
		.set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
	_tween.parallel().tween_property(_tilt, "modulate", TOPPLE_TINT, 0.34)
	if shadow != null:
		_tween.parallel().tween_property(shadow, "scale", long_shadow, 0.34) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		_tween.parallel().tween_property(shadow, "modulate:a", 0.85, 0.34)


func grey_out() -> void:
	# The no-show wash: present, unbloodied, absent — never rotated (he did
	# not fall; he did not come).
	modulate = GREY_TINT


func recoil(delay: float) -> void:
	# The victor's line takes the shock and holds — a two-frame shudder.
	var dir := -1.0 if facing == "r" else 1.0
	var tw := create_tween()
	tw.tween_interval(delay)
	tw.tween_property(self, "position:x", position.x + dir * 3.0, 0.09)
	tw.tween_property(self, "position:x", position.x, 0.16) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

extends Control
class_name PortraitLocket

# =============================================================================
# PROJECT SOVEREIGN — Portrait locket (Battle Diorama, row BD)
# =============================================================================
# A marshal's face in an oval brass locket, sepia-washed and vignetted so a
# photo-lithograph sits IN the carved-wood tray instead of floating over it —
# the eval's §8 treatment ("untreated raw JPGs are the biggest material
# clash"). Name-keyed off the same assets/portraits/<name> files the Generals
# cards use, with the same gold-monogram fallback so no corps is faceless.
#
# States:
#   set_dead(true)  — the corps broke: the glass desaturates and darkens.
#   crowned         — the standing glory-#1 wears his star on the rim
#                     (a laurel he ALREADY wore — never minted by this battle).
# =============================================================================

const PORTRAIT_DIR := "res://assets/portraits/"
const RING_COLOR := Color(0.72, 0.60, 0.36, 1.0)       # aged brass
const RING_SHINE := Color(0.95, 0.88, 0.66, 0.9)       # top-left catchlight
const RING_DARK := Color(0.28, 0.21, 0.10, 1.0)        # bezel shadow
const BACKING := Color(0.13, 0.10, 0.07, 1.0)          # leather backing

# One sepia-duotone + ellipse-mask + vignette shader, shared by every locket.
const _SHADER_CODE := """
shader_type canvas_item;
uniform float dead : hint_range(0.0, 1.0) = 0.0;
void fragment() {
	vec2 c = (UV - vec2(0.5)) * 2.0;
	float r = length(c);
	vec4 tex = texture(TEXTURE, UV);
	float g = dot(tex.rgb, vec3(0.299, 0.587, 0.114));
	vec3 sepia = vec3(0.90, 0.76, 0.55) * g + vec3(0.10, 0.065, 0.03);
	vec3 deadened = mix(sepia, vec3(g * 0.45 + 0.05), 0.85);
	vec3 col = mix(sepia, deadened, dead);
	float vig = mix(0.72, 1.0, smoothstep(1.0, 0.45, r));
	col *= vig;
	float edge = 1.0 - smoothstep(0.90, 1.0, r);
	COLOR = vec4(col, tex.a * edge);
}
"""

static var _shader: Shader = null
static var _portrait_paths := {}   # name -> path or "" (probe once)

var marshal_name := ""
var crowned := false
var _dead := 0.0
var _portrait: TextureRect = null
var _material: ShaderMaterial = null


static func _portrait_path(name_key: String) -> String:
	if _portrait_paths.has(name_key):
		return _portrait_paths[name_key]
	var found := ""
	for ext in ["jpg", "png"]:
		var p: String = PORTRAIT_DIR + name_key + "." + str(ext)
		if ResourceLoader.exists(p):
			found = p
			break
	_portrait_paths[name_key] = found
	return found


func setup(name_key: String, diameter: float, is_crowned: bool) -> void:
	marshal_name = name_key
	crowned = is_crowned
	custom_minimum_size = Vector2(diameter, diameter)
	size = Vector2(diameter, diameter)
	pivot_offset = size / 2.0

	var path := _portrait_path(name_key)
	if path != "":
		if _shader == null:
			_shader = Shader.new()
			_shader.code = _SHADER_CODE
		_material = ShaderMaterial.new()
		_material.shader = _shader
		_material.set_shader_parameter("dead", 0.0)
		_portrait = TextureRect.new()
		_portrait.texture = load(path)
		_portrait.material = _material
		_portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		_portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		var inset := diameter * 0.10
		_portrait.position = Vector2(inset, inset)
		_portrait.size = Vector2(diameter - inset * 2.0, diameter - inset * 2.0)
		_portrait.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(_portrait)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	queue_redraw()


func set_dead(animated := true) -> void:
	"""The corps broke — the face in the glass goes grey."""
	if _material == null:
		_dead = 1.0
		queue_redraw()
		return
	if animated:
		var tw := create_tween()
		tw.tween_method(_apply_dead, _dead, 1.0, 0.5)
	else:
		_apply_dead(1.0)


func _apply_dead(v: float) -> void:
	_dead = v
	if _material != null:
		_material.set_shader_parameter("dead", v)
	queue_redraw()


func _draw() -> void:
	var c := size / 2.0
	var radius := minf(size.x, size.y) / 2.0

	# Leather backing disc (also the monogram ground when no portrait).
	draw_circle(c, radius - 1.0, BACKING)

	if _portrait == null:
		# Gold monogram fallback — the Generals-card discipline: no face is
		# never a blank face.
		var letter := marshal_name.substr(0, 1).to_upper()
		var font: Font = get_theme_default_font()
		var fsize := int(radius * 1.1)
		var ls := font.get_string_size(letter, HORIZONTAL_ALIGNMENT_CENTER,
				-1, fsize)
		var col := RING_COLOR if _dead < 0.5 else Color(0.45, 0.45, 0.48, 1.0)
		draw_string(font, Vector2(c.x - ls.x / 2.0,
				c.y + ls.y * 0.34), letter,
				HORIZONTAL_ALIGNMENT_CENTER, -1, fsize, col)

	# Brass bezel: dark seat, brass ring, catchlight arc (upper-left, matching
	# the sprites' baked key from upper-right — the shine reads as the rim
	# turning away from the lamp).
	var ring := RING_COLOR if _dead < 0.5 else RING_COLOR.darkened(0.35)
	draw_arc(c, radius - 1.0, 0.0, TAU, 48, RING_DARK, 3.0, true)
	draw_arc(c, radius - 2.2, 0.0, TAU, 48, ring, 2.2, true)
	if _dead < 0.5:
		draw_arc(c, radius - 2.2, PI * 0.75, PI * 1.35, 20, RING_SHINE, 1.4, true)

	# The standing star — worn INTO the rim, not floated above it.
	if crowned:
		var star_pos := Vector2(c.x, c.y - radius + 1.0)
		var font: Font = get_theme_default_font()
		var s := "★"
		var ss := font.get_string_size(s, HORIZONTAL_ALIGNMENT_CENTER, -1, 13)
		draw_string(font, Vector2(star_pos.x - ss.x / 2.0, star_pos.y + 4.0),
				s, HORIZONTAL_ALIGNMENT_CENTER, -1, 13,
				Color(0.98, 0.86, 0.35, 1.0))

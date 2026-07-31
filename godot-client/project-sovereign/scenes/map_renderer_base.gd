extends Control

signal region_hovered(region_name)
signal region_clicked(region_name)
# UX pass July 16: dismiss affordances — right-click anywhere or left-click on
# open water both read as "put the panel away" in every map game.
signal map_dismiss_requested

const MapConnectionLayer = preload("res://scenes/map_connection_layer.gd")
const MapTooltipLayer = preload("res://scenes/map_tooltip_layer.gd")
const MapLabelLayer = preload("res://scenes/map_label_layer.gd")

const REGION_RADIUS: float = 30.0
const REGION_DIAMETER: float = REGION_RADIUS * 2.0
const REGION_LABEL_WIDTH: float = 120.0
const REGION_LABEL_HEIGHT: float = 20.0
const MARSHAL_ICON_SIZE := Vector2(16, 16)
const MARSHAL_ICON_SPACING: float = 8.0
const MARSHAL_ICON_Y_OFFSET: float = -50.0
# UI-5 War-Table Pieces: on-map draw size of a carved-wood standee (the full
# 256px source frame maps to this height; the visible figure is ~55% of it), the
# horizontal spread for co-located marshals, and the province->province move
# tween. Tunable — flagged for visual sign-off like the U2/U3 gates. Shrunk from
# 84 -> 64 so standees in neighbouring provinces stop overlapping (July 13 feedback).
const WAR_PIECE_FRAME_PX: float = 64.0
# IGR-G2: 30px spacing against a ~35px visible figure (64 * 0.55) meant
# co-located pieces overlapped at EVERY zoom — geometry, not zoom. 38 gives
# each figure daylight while a 5-stack still reads as one massed province.
const WAR_PIECE_SLOT_SPACING: float = 38.0
# UI-6 (U5 residual): 3+ co-located standees split into two ranks — the rear
# rank steps back by this many map px (pieces_layer y-sorts, so rear draws
# behind) instead of stretching one overlapping x-line across the province.
const WAR_PIECE_RANK_DEPTH: float = 16.0
const WAR_PIECE_MOVE_DURATION: float = 0.45
const GARRISON_SIZE := Vector2(26, 18)
const GARRISON_Y_OFFSET: float = 38.0
# UI cleanup (July 2 playtest feedback): force name labels draw straight on
# the terrain art — without an outline the white text vanished on light
# provinces and read as part of the colliding province labels.
const FORCE_NAME_OUTLINE_COLOR := Color(0.09, 0.07, 0.05, 0.9)
const FORCE_NAME_OUTLINE_SIZE: int = 4
const DEFAULT_CAPITAL_REGIONS := ["Paris", "Berlin", "Vienna", "London", "Madrid"]
const DEFAULT_MAP_PADDING: float = 140.0
const MAP_BACKGROUND_COLOR := Color(0.12, 0.13, 0.14, 1.0)
# Slice 7.5 (DEF-9): with commissioned art the out-of-map margin reads as the
# map sheet itself — parchment sampled from the art's edge (rgb 153,125,90) —
# instead of a black void band. The legacy circle map keeps the dark canvas.
const BITMAP_LETTERBOX_COLOR := Color(0.6, 0.49, 0.353, 1.0)
# Slice 7.5 (DEF-9): Camera2D hardware limits are deliberately disabled (set
# to the engine's wide-open defaults). When the visible extent exceeded the
# map, Godot's limit clamps (left->right, bottom->top; last write wins)
# pinned the view to limit_right/limit_top and dumped the entire letterbox
# deficit on one side as a single void band — fighting (and beating)
# _clamp_camera_position()'s centered letterboxing.
const CAMERA_LIMIT_DISABLED: int = 10000000
const NO_PROVINCE_COLOR := Color8(0, 0, 0, 255)
# §4.4: unwired provinces are painted over with a flat grey tint so authors can
# see map coverage without exposing outlined-but-unimplemented territory as
# playable. `UNWIRED_GREY_BLEND` is the lerp factor toward `UNWIRED_GREY_COLOR`:
# 0.0 = underlying visual unchanged, 1.0 = fully flat grey. Kept high enough to
# clearly read as "not yet in play" without erasing the underlying shape.
const UNWIRED_GREY_COLOR := Color(0.32, 0.32, 0.34, 1.0)
const UNWIRED_GREY_BLEND: float = 0.7
const UNWIRED_TOOLTIP_SUFFIX := "(not yet in play)"
# §4.4 tooltip palette: warm sepia so "unwired" is visually unmistakable next to
# the cold blue-grey fogged-region tooltip (panel `(0.08, 0.08, 0.12, 0.95)`,
# border `(0.4, 0.4, 0.5)`). The panel reads as an old-paper map margin —
# "drawn but not yet in play" — instead of another shade of intel darkness.
const UNWIRED_TOOLTIP_PANEL := Color(0.14, 0.11, 0.08, 0.95)
const UNWIRED_TOOLTIP_BORDER := Color(0.55, 0.42, 0.28, 0.9)
const UNWIRED_TOOLTIP_TITLE_COLOR := Color(0.82, 0.72, 0.55)
const UNWIRED_TOOLTIP_SUFFIX_COLOR := Color(0.72, 0.58, 0.38)
# Map Slice 6: province ownership fills. In bitmap mode every province is
# tinted by its owner's Utils.NATION_COLORS color through the lookup mask on a
# dedicated shader layer. OWNER_FILL_STRENGTH is the tint alpha over the
# terrain art (0.0 = invisible, 1.0 = flat political map). An ownership change
# costs ONE <=128-entry palette uniform upload (G4: re-tint in <= one frame) —
# never a per-pixel CPU pass; the per-pixel §4.4 grey-overlay pattern is
# load-time-only and must not be mirrored here.
const OWNER_FILL_STRENGTH: float = 0.55
const OWNER_FILL_MAX_PROVINCES: int = 128
# Slice 7.5 (DEF-12 cheap tier): three intensities on the SAME fill_strength
# uniform — "blended" (shipped default), "political" (near-flat ownership),
# "terrain" (art-forward, fills faint). Cycled with the M key; one uniform
# write per switch, the same G4 budget shape as the palette upload. A real
# multi-overlay map-mode system (supply/diplomatic overlays, fog decoupled
# from the owner palette) stays owned by the DEF-12 future spec.
const MAP_FILL_MODE_ORDER: Array = ["blended", "political", "terrain"]
const MAP_FILL_MODE_STRENGTHS := {
	"blended": OWNER_FILL_STRENGTH,
	"political": 0.85,
	"terrain": 0.15,
}
# Slice 7.5 (DEF-10): fog previously lerped owner rgb by the FULL fog alpha —
# "unknown" (0.75) destroyed 75% of the national hue and collapsed the mostly
# fogged turn-1 map to uniform grey-brown (measured mean pairwise deltaE 11.7
# across the 20-nation roster). The HUE lerp is scaled down so fogged-but-
# known ownership stays readable, while the alpha wash (maxf) keeps fog
# clearly visible. Measured at 0.6: turn-1 mean pairwise deltaE 26.5.
const FOG_HUE_LERP_SCALE: float = 0.6
# The palette match loop runs per on-screen fragment every frame; the sea
# early-out (sentinel [0,0,0] covers most of the image) bounds it and also
# guarantees a zeroed palette slot can never paint open water.
# Slice 7.5 (DEF-10) border pass: fragments whose lookup key differs from the
# right/down neighbor darken into a 1px province border — the art's painted
# borders are washed by the owner fill, and without edges the re-authored
# palette still smears at province granularity. Land-land edges only (sea
# neighbors are skipped) so coastlines keep the painted art. Two extra texture
# taps + key compares per land fragment; no palette rescans, no CPU.
const OWNER_FILL_SHADER := """
shader_type canvas_item;

uniform int province_count = 0;
uniform vec4 lookup_colors[128];
uniform vec4 owner_colors[128];
uniform float fill_strength = 0.55;
uniform float border_strength = 0.5;

void fragment() {
	vec4 key = texture(TEXTURE, UV);
	if (key.r + key.g + key.b < 0.002) {
		COLOR = vec4(0.0);
	} else {
		vec4 result = vec4(0.0);
		for (int i = 0; i < province_count; i++) {
			if (all(lessThan(abs(key.rgb - lookup_colors[i].rgb), vec3(0.002)))) {
				result = vec4(owner_colors[i].rgb, owner_colors[i].a * fill_strength);
				break;
			}
		}
		vec3 right = texture(TEXTURE, UV + vec2(TEXTURE_PIXEL_SIZE.x, 0.0)).rgb;
		vec3 down = texture(TEXTURE, UV + vec2(0.0, TEXTURE_PIXEL_SIZE.y)).rgb;
		bool right_differs = (right.r + right.g + right.b >= 0.002) && any(greaterThanEqual(abs(key.rgb - right), vec3(0.002)));
		bool down_differs = (down.r + down.g + down.b >= 0.002) && any(greaterThanEqual(abs(key.rgb - down), vec3(0.002)));
		if (right_differs || down_differs) {
			result = vec4(mix(result.rgb, vec3(0.13, 0.1, 0.07), 0.7), max(result.a, border_strength));
		}
		COLOR = result;
	}
}
"""
# UX pass July 16: hover/selection highlight moved onto the GPU. The old path
# allocated a full map-canvas RGBA image and CPU-stamped a CIRCLE on every
# hover change; this shader reads the SAME lookup mask the owner fill uses and
# lights the TRUE province silhouette — soft fill + rim at the real border —
# for the cost of a uniform write per hover change. `selected_key` keeps the
# clicked province lit while the Region Action Panel is open; `selected_boost`
# is tweened 1→0 on click for a brief confirmation pulse. Sentinel vec3(-10)
# can never match a texture key in [0,1]. Legacy circle-fixture maps (no
# lookup image) keep the old CPU circle path.
const HIGHLIGHT_SHADER := """
shader_type canvas_item;

uniform vec3 hover_key = vec3(-10.0);
uniform vec3 selected_key = vec3(-10.0);
uniform float selected_boost = 0.0;

const vec4 HOVER_FILL = vec4(1.0, 0.94, 0.78, 0.10);
const vec4 HOVER_RIM = vec4(1.0, 0.90, 0.62, 0.85);
const vec4 SELECT_FILL = vec4(1.0, 0.87, 0.55, 0.16);
const vec4 SELECT_RIM = vec4(1.0, 0.82, 0.40, 0.95);

bool key_match(vec3 a, vec3 b) {
	return all(lessThan(abs(a - b), vec3(0.002)));
}

void fragment() {
	vec3 key = texture(TEXTURE, UV).rgb;
	vec4 result = vec4(0.0);
	if (key.r + key.g + key.b >= 0.002) {
		bool sel = key_match(key, selected_key);
		bool hov = key_match(key, hover_key);
		if (sel || hov) {
			vec2 px = TEXTURE_PIXEL_SIZE * 2.0;
			bool rim = !key_match(texture(TEXTURE, UV + vec2(px.x, 0.0)).rgb, key)
				|| !key_match(texture(TEXTURE, UV - vec2(px.x, 0.0)).rgb, key)
				|| !key_match(texture(TEXTURE, UV + vec2(0.0, px.y)).rgb, key)
				|| !key_match(texture(TEXTURE, UV - vec2(0.0, px.y)).rgb, key);
			if (sel) {
				result = rim ? SELECT_RIM : SELECT_FILL;
				result.a = min(1.0, result.a + selected_boost * 0.30);
			} else {
				result = rim ? HOVER_RIM : HOVER_FILL;
			}
		}
	}
	COLOR = result;
}
"""
const HIGHLIGHT_KEY_NONE := Vector3(-10.0, -10.0, -10.0)

static var _bitmap_load_error_latch := {}
const FOG_OVERLAYS = {
	"full": Color(0, 0, 0, 0),
	"partial": Color(0.15, 0.15, 0.2, 0.3),
	"stale": Color(0.1, 0.1, 0.15, 0.5),
	"last_known": Color(0.05, 0.05, 0.1, 0.65),
	"unknown": Color(0.02, 0.02, 0.05, 0.75),
}

var region_controllers := {}
var region_marshals := {}
var region_visibility := {}
var region_fogged_forces := {}
var region_garrisons := {}
var region_full_data := {}

var mouse_position: Vector2 = Vector2.ZERO
var hovered_marshal := {}
var hovered_fogged_force := {}
var hovered_region: String = ""
var pan_keys_pressed := {
	"left": false,
	"right": false,
	"up": false,
	"down": false,
}

var _zoom_level: float = 1.0
var min_zoom: float = 0.5
# Slice 7.5 fold (user zoom feedback): capped at the art's useful limit —
# the 2560x1600 sheet carries no information past ~2.5x; the old 4.0 was
# pure upscaled pixel soup.
var max_zoom: float = 2.5
var is_panning: bool = false
var pan_start_pos: Vector2 = Vector2.ZERO
var zoom_tween: Tween = null
var panning_enabled: bool = true

const PAN_SPEED_KEYS: float = 300.0
const ZOOM_SPEED: float = 0.1
const ZOOM_DURATION: float = 0.2

var viewport_background: ColorRect
var map_viewport: SubViewport
# UI-2 Part 2: the SubViewport is displayed through this TextureRect (not a
# stretch-drawing SubViewportContainer) so it can render at PHYSICAL resolution
# and stay crisp under a global content_scale_factor > 1.0.
var map_display: TextureRect
var map_root: Node2D
var map_camera: Camera2D
var world_layer: Control
var connection_layer
var region_layer: Control
var force_layer: Control
var garrison_layer: Control
var tooltip_layer
var visual_map_layer: TextureRect
var highlight_map_layer: TextureRect
var owner_fill_layer: TextureRect

var region_nodes := {}
var marshal_hitboxes: Array = []
var fogged_force_hitboxes: Array = []
# UI-5 War-Table Pieces: a PERSISTENT, y-sorted layer of tin-flat standees at
# marshal anchors. Unlike the force_layer icons (torn down every refresh — see
# _rebuild_dynamic_nodes), pieces keep per-marshal node identity across updates
# so they can tween province->province and flip facing by travel heading. Only
# populated in bitmap-art mode (the legacy circle fixture keeps its square icons).
var pieces_layer: Node2D = null
var _war_pieces := {}          # marshal name -> WarTablePiece
var _war_piece_anchors := {}   # marshal name -> Vector2 (last layer anchor)
var _war_piece_regions := {}   # marshal name -> String (last region — a REAL
                               # move (region change) tweens + flips facing; a
                               # pure slot re-center from a neighbor arriving/
                               # leaving snaps, so idle marshals don't slide.
var province_definition := {}
var province_shapes := {}
var province_color_lookup := {}
var province_lookup_image: Image = null
var visual_map_texture = null
var highlight_map_texture = null
# UX pass July 16: shader-highlight state. _highlight_material is non-null only
# in bitmap mode (lookup mask present); selected_region survives layer rebuilds
# so the lit province re-applies after a topology refresh.
var selected_region: String = ""
var _highlight_material: ShaderMaterial = null
var _select_pulse_tween: Tween = null
# True iff _load_map_images() delivered artist bitmaps (vs the circle
# fallback). The owner-fill layer only exists in bitmap mode — the legacy
# circle map keeps its per-region Panel fills as the ownership display.
var _bitmap_mode := false
# Fixed province ordering shared by the lookup_colors and owner_colors shader
# palettes — index alignment between the two arrays is the load-bearing
# invariant of the owner-fill pass.
var _owner_fill_province_order: Array = []
var map_origin: Vector2 = Vector2.ZERO
var map_canvas_size: Vector2 = Vector2.ZERO
var world_bounds: Rect2 = Rect2(Vector2.ZERO, Vector2.ONE)
# Slice 7.5 (DEF-11): the zoom-LOD label layer; null outside bitmap mode.
var map_label_layer = null
# GLOBAL-space rects of overlaying UI panels (the command terminal) that map
# labels must dodge. Cached here because the owner pushes them on every
# layout pass, which can precede the label layer's creation.
var _ui_avoid_global_rects: Array = []
# WORLD-coord rects occupied by marshal icons, name stacks, and garrison
# chips this rebuild — pushed to the label layer so province labels dodge
# the map furniture instead of drawing through it.
var _label_avoid_world_rects: Array = []
# Slice 7.5 (DEF-12 cheap tier): the active fill mode key.
var _map_fill_mode: String = "blended"


func _get_region_positions() -> Dictionary:
	return {}


func _get_region_connections() -> Dictionary:
	return {}


func _get_colors() -> Dictionary:
	return {}


func _get_capital_regions() -> Array:
	return DEFAULT_CAPITAL_REGIONS.duplicate()


func _get_map_asset_definition_path() -> String:
	return ""


func _get_map_visual_bitmap_path() -> String:
	# Subclasses override to return the artist-delivered "pretty map" bitmap.
	# Empty string means: fall back to generated circle visuals.
	return ""


func _get_map_lookup_bitmap_path() -> String:
	# Subclasses override to return the artist-delivered province color-map
	# (the hidden image used for pixel-perfect hit detection).
	# Empty string means: fall back to generated circle color-map.
	return ""


func _get_active_region_positions() -> Dictionary:
	if not province_shapes.is_empty():
		var positions := {}
		for region_name in province_shapes:
			positions[region_name] = province_shapes[region_name].get("center", Vector2.ZERO)
		return positions
	return _get_region_positions()


func _ready():
	resized.connect(_on_map_area_resized)
	_initialize_map()
	_initialize_map_assets()
	_create_scene_layers()
	_build_static_map_visuals()
	call_deferred("_finalize_view_setup")


func _initialize_map():
	region_controllers = {}
	region_marshals = {}
	region_visibility = {}
	region_fogged_forces = {}
	region_garrisons = {}
	region_full_data = {}


func _initialize_map_assets():
	province_definition = _load_province_definition()
	_build_province_shapes()
	_build_map_textures()
	world_bounds = _compute_world_bounds()


func _finalize_view_setup():
	_on_map_area_resized()
	_set_camera_zoom_level(_get_initial_zoom_level())
	_center_view_on_map()
	queue_redraw()


func _compute_world_bounds() -> Rect2:
	if map_canvas_size != Vector2.ZERO:
		return Rect2(map_origin, map_canvas_size)

	var positions = _get_active_region_positions()
	if positions.is_empty():
		return Rect2(Vector2.ZERO, Vector2.ONE)

	var padding = max(DEFAULT_MAP_PADDING, REGION_LABEL_WIDTH)
	var min_x = INF
	var max_x = -INF
	var min_y = INF
	var max_y = -INF

	for pos in positions.values():
		min_x = min(min_x, pos.x - padding)
		max_x = max(max_x, pos.x + padding)
		min_y = min(min_y, pos.y - padding)
		max_y = max(max_y, pos.y + padding)

	return Rect2(
		Vector2(min_x, min_y),
		Vector2(max(1.0, max_x - min_x), max(1.0, max_y - min_y))
	)


func _load_province_definition() -> Dictionary:
	var definition_path = _get_map_asset_definition_path()
	if definition_path == "":
		return {}

	if not FileAccess.file_exists(definition_path):
		push_warning("Map province definition missing: %s" % definition_path)
		return {}

	var file = FileAccess.open(definition_path, FileAccess.READ)
	if file == null:
		push_warning("Could not open province definition: %s" % definition_path)
		return {}

	var parsed = JSON.parse_string(file.get_as_text())
	if not (parsed is Dictionary):
		push_warning("Province definition is not a dictionary: %s" % definition_path)
		return {}

	return parsed


func _build_province_shapes():
	province_shapes.clear()
	province_color_lookup.clear()
	map_origin = Vector2.ZERO
	map_canvas_size = Vector2.ZERO
	province_lookup_image = null
	visual_map_texture = null
	highlight_map_texture = null
	_bitmap_mode = false
	_owner_fill_province_order = []

	var positions = _get_region_positions()
	if positions.is_empty():
		return

	var regions = province_definition.get("regions", {})
	var padding = float(province_definition.get("padding", DEFAULT_MAP_PADDING))
	var min_x = INF
	var max_x = -INF
	var min_y = INF
	var max_y = -INF

	for region_name in positions:
		var center: Vector2 = positions[region_name]
		var region_data: Dictionary = regions.get(region_name, {})
		if region_data.has("anchor"):
			center = _vector_from_array(region_data.get("anchor", []), center)
		var radius = float(region_data.get("radius", REGION_RADIUS * 1.8))
		var lookup_color = _color_from_rgb_array(region_data.get("lookup_color", []), _fallback_lookup_color(region_name))
		var visual_tint = _color_from_rgb_array(region_data.get("visual_tint", []), lookup_color.lightened(0.45))
		var province_id = str(region_data.get("province_id", region_name.to_lower()))
		var unit_anchor = _vector_from_array(region_data.get("unit_anchor", []), center)
		var label_anchor = _vector_from_array(region_data.get("label_anchor", []), center)
		var garrison_anchor = _vector_from_array(region_data.get("garrison_anchor", []), center)
		var building_anchor = _vector_from_array(region_data.get("building_anchor", []), center)
		var wired = bool(region_data.get("wired", true))
		var interactive = bool(region_data.get("interactive", true))

		province_shapes[region_name] = {
			"center": center,
			"radius": radius,
			"lookup_color": lookup_color,
			"visual_tint": visual_tint,
			"province_id": province_id,
			"unit_anchor": unit_anchor,
			"label_anchor": label_anchor,
			"garrison_anchor": garrison_anchor,
			"building_anchor": building_anchor,
			"wired": wired,
			"interactive": interactive,
		}
		province_color_lookup[_color_to_key(lookup_color)] = region_name

		min_x = min(min_x, center.x - radius)
		max_x = max(max_x, center.x + radius)
		min_y = min(min_y, center.y - radius)
		max_y = max(max_y, center.y + radius)

	map_origin = Vector2(min_x - padding, min_y - padding)
	map_canvas_size = Vector2(
		max(1.0, (max_x - min_x) + padding * 2.0),
		max(1.0, (max_y - min_y) + padding * 2.0)
	)


func _build_map_textures():
	if province_shapes.is_empty() or map_canvas_size == Vector2.ZERO:
		return

	# §4.2: prefer artist-delivered bitmaps when the subclass declares them.
	# Fall back to generated circles so the 19-region placeholder scene
	# (which has no bitmap) keeps working unchanged.
	if _load_map_images():
		return

	var image_width = max(1, int(ceil(map_canvas_size.x)))
	var image_height = max(1, int(ceil(map_canvas_size.y)))
	var visual_image = Image.create(image_width, image_height, false, Image.FORMAT_RGBA8)
	visual_image.fill(MAP_BACKGROUND_COLOR)
	var color_map = Image.create(image_width, image_height, false, Image.FORMAT_RGBA8)
	color_map.fill(NO_PROVINCE_COLOR)

	for region_name in province_shapes:
		var shape: Dictionary = province_shapes[region_name]
		var center: Vector2 = shape["center"] - map_origin
		var radius = float(shape["radius"])
		_draw_circle_on_image(visual_image, center + Vector2(8.0, 10.0), radius + 2.0, Color(0.0, 0.0, 0.0, 0.18))
		_draw_circle_on_image(visual_image, center, radius, shape["visual_tint"])
		_draw_circle_outline_on_image(visual_image, center, radius, Color(0.2, 0.18, 0.16, 0.9), 3)
		_draw_circle_on_image(color_map, center, radius, shape["lookup_color"])

	province_lookup_image = color_map
	_apply_unwired_grey_overlay(visual_image, color_map)
	visual_map_texture = ImageTexture.create_from_image(visual_image)
	_clear_highlight_texture()


func _load_map_images() -> bool:
	# Attempts to load artist-delivered visual + lookup bitmaps declared by the
	# subclass via _get_map_visual_bitmap_path() / _get_map_lookup_bitmap_path().
	#
	# Returns true iff both bitmaps loaded successfully and their dimensions
	# match. On success: sets visual_map_texture + province_lookup_image,
	# overrides map_origin to Vector2.ZERO and map_canvas_size to the bitmap
	# dimensions (so authored anchors are interpreted in bitmap-pixel coords),
	# and clears any stale highlight texture.
	#
	# Returns false on any failure — caller falls back to circle generation.
	# Deeper asset validation (color-map vs registry coverage, artifact pixels,
	# etc.) is §4.3's job; this routine only checks that the files exist, load,
	# and agree on size.
	var visual_path = _get_map_visual_bitmap_path()
	var lookup_path = _get_map_lookup_bitmap_path()
	if visual_path == "" or lookup_path == "":
		return false

	var visual_image = _load_bitmap_texture_image(visual_path, "visual")
	if visual_image == null:
		return false

	var lookup_image = _load_bitmap_texture_image(lookup_path, "lookup")
	if lookup_image == null:
		return false

	if visual_image.get_size() != lookup_image.get_size():
		_report_bitmap_load_error_once(
			"Map visual/lookup bitmap size mismatch: visual=%s lookup=%s" %
			[visual_image.get_size(), lookup_image.get_size()]
		)
		return false

	if not _validate_lookup_bitmap_image(lookup_image, lookup_path):
		return false

	# Bitmap mode convention: the bitmap's (0, 0) is the map origin in world
	# coords, and anchors in the province registry are authored in bitmap-pixel
	# coords. _build_province_shapes() already populated province_color_lookup
	# from the registry, so hit detection via province_lookup_image.get_pixel()
	# + province_color_lookup keeps working unchanged.
	map_origin = Vector2.ZERO
	map_canvas_size = Vector2(visual_image.get_size())
	province_lookup_image = lookup_image
	_bitmap_mode = true
	_apply_unwired_grey_overlay(visual_image, lookup_image)
	# Slice 7.5 fold: mipmaps let the linear filter minify without shimmer at
	# low zoom (one-time load cost; the lookup image stays mip-less/NEAREST).
	visual_image.generate_mipmaps()
	visual_map_texture = ImageTexture.create_from_image(visual_image)
	_clear_highlight_texture()
	return true


func _load_bitmap_texture_image(resource_path: String, label: String) -> Image:
	if not ResourceLoader.exists(resource_path):
		_report_bitmap_load_error_once("Map %s bitmap resource missing: %s" % [label, resource_path])
		return null

	var resource = ResourceLoader.load(resource_path)
	if resource == null:
		_report_bitmap_load_error_once("Failed to load map %s bitmap resource: %s" % [label, resource_path])
		return null

	var texture := resource as Texture2D
	if texture == null:
		_report_bitmap_load_error_once("Map %s bitmap is not a Texture2D: %s" % [label, resource_path])
		return null

	var image := texture.get_image()
	if image == null or image.get_width() <= 0 or image.get_height() <= 0:
		_report_bitmap_load_error_once("Map %s bitmap returned no image data: %s" % [label, resource_path])
		return null

	return image


func _validate_lookup_bitmap_image(lookup_image: Image, lookup_path: String) -> bool:
	var no_province_key = _color_to_key(NO_PROVINCE_COLOR)
	var seen_region_keys := {}

	for y in range(lookup_image.get_height()):
		for x in range(lookup_image.get_width()):
			var pixel_key = _color_to_key(lookup_image.get_pixel(x, y))
			if pixel_key == no_province_key:
				continue
			if not province_color_lookup.has(pixel_key):
				_report_bitmap_load_error_once(
					"Map lookup bitmap has unmapped province color %s at (%d, %d): %s" %
					[pixel_key, x, y, lookup_path]
				)
				return false
			seen_region_keys[pixel_key] = true

	for pixel_key in province_color_lookup.keys():
		if not seen_region_keys.has(pixel_key):
			_report_bitmap_load_error_once(
				"Map lookup bitmap is missing province color %s (%s): %s" %
				[pixel_key, province_color_lookup[pixel_key], lookup_path]
			)
			return false

	return true


func _report_bitmap_load_error_once(message: String) -> void:
	if _bitmap_load_error_latch.has(message):
		return
	_bitmap_load_error_latch[message] = true
	push_error(message)


func _vector_from_array(values, fallback: Vector2) -> Vector2:
	if values is Array and values.size() >= 2:
		return Vector2(float(values[0]), float(values[1]))
	return fallback


func _color_from_rgb_array(values, fallback: Color) -> Color:
	if values is Array and values.size() >= 3:
		return Color8(int(values[0]), int(values[1]), int(values[2]), 255)
	return fallback


func _fallback_lookup_color(region_name: String) -> Color:
	var hash_value = abs(region_name.hash())
	return Color8(
		55 + (hash_value % 180),
		55 + (int(hash_value / 3) % 180),
		55 + (int(hash_value / 7) % 180),
		255
	)


func _color_to_key(color: Color) -> String:
	return "%s,%s,%s" % [
		int(round(color.r * 255.0)),
		int(round(color.g * 255.0)),
		int(round(color.b * 255.0)),
	]


func _is_region_wired(region_name: String) -> bool:
	# §4.4: unwired provinces render in grey tint, hover shows "(not yet in
	# play)", and clicks are suppressed. Regions not in province_shapes
	# (legacy paths without registry data) default to wired so existing
	# behavior is preserved.
	if not province_shapes.has(region_name):
		return true
	return bool(province_shapes[region_name].get("wired", true))


func _unwired_lookup_keys() -> Dictionary:
	# Returns a set (dict-as-set) of lookup-color keys belonging to unwired
	# provinces, used to stamp the grey overlay onto the visual image in one
	# pass.
	var keys := {}
	for color_key in province_color_lookup.keys():
		var region_name = province_color_lookup[color_key]
		if not _is_region_wired(region_name):
			keys[color_key] = true
	return keys


func _apply_unwired_grey_overlay(visual_image: Image, lookup_image: Image) -> void:
	# §4.4: blend UNWIRED_GREY_COLOR over every visual pixel whose lookup color
	# belongs to an unwired province. Runs after either the bitmap loader or
	# the circle fallback has populated visual_image, so the tint applies
	# uniformly regardless of source. No-op when every province is wired.
	if visual_image == null or lookup_image == null:
		return
	var unwired_keys := _unwired_lookup_keys()
	if unwired_keys.is_empty():
		return
	if visual_image.get_size() != lookup_image.get_size():
		return
	var width = lookup_image.get_width()
	var height = lookup_image.get_height()
	for y in range(height):
		for x in range(width):
			var pixel_key = _color_to_key(lookup_image.get_pixel(x, y))
			if not unwired_keys.has(pixel_key):
				continue
			var base = visual_image.get_pixel(x, y)
			var tinted = base.lerp(UNWIRED_GREY_COLOR, UNWIRED_GREY_BLEND)
			tinted.a = base.a
			visual_image.set_pixel(x, y, tinted)


func _draw_circle_on_image(image: Image, center: Vector2, radius: float, color: Color):
	var start_x = max(0, int(floor(center.x - radius)))
	var end_x = min(image.get_width() - 1, int(ceil(center.x + radius)))
	var start_y = max(0, int(floor(center.y - radius)))
	var end_y = min(image.get_height() - 1, int(ceil(center.y + radius)))
	var radius_sq = radius * radius

	for y in range(start_y, end_y + 1):
		for x in range(start_x, end_x + 1):
			var delta = Vector2(float(x) + 0.5, float(y) + 0.5) - center
			if delta.length_squared() <= radius_sq:
				image.set_pixel(x, y, color)


func _draw_circle_outline_on_image(image: Image, center: Vector2, radius: float, color: Color, width: int = 2):
	var outer_radius = radius
	var inner_radius = max(radius - float(width), 0.0)
	var outer_sq = outer_radius * outer_radius
	var inner_sq = inner_radius * inner_radius
	var start_x = max(0, int(floor(center.x - outer_radius)))
	var end_x = min(image.get_width() - 1, int(ceil(center.x + outer_radius)))
	var start_y = max(0, int(floor(center.y - outer_radius)))
	var end_y = min(image.get_height() - 1, int(ceil(center.y + outer_radius)))

	for y in range(start_y, end_y + 1):
		for x in range(start_x, end_x + 1):
			var delta = Vector2(float(x) + 0.5, float(y) + 0.5) - center
			var dist_sq = delta.length_squared()
			if dist_sq <= outer_sq and dist_sq >= inner_sq:
				image.set_pixel(x, y, color)


func _clear_highlight_texture():
	if _highlight_material != null:
		_highlight_material.set_shader_parameter("hover_key", HIGHLIGHT_KEY_NONE)
		return
	highlight_map_texture = null
	if highlight_map_layer != null:
		highlight_map_layer.texture = null


func _lookup_key_for(region_name: String) -> Vector3:
	# The shader's match key for a province: its lookup-mask color as a vec3.
	# Unknown/empty names return the sentinel that matches nothing.
	if region_name == "" or not province_shapes.has(region_name):
		return HIGHLIGHT_KEY_NONE
	var lookup = province_shapes[region_name].get("lookup_color", null)
	if lookup == null:
		return HIGHLIGHT_KEY_NONE
	return Vector3(lookup.r, lookup.g, lookup.b)


func set_selected_region(region_name: String):
	# UX pass July 16: the clicked province stays lit while the Region Action
	# Panel is open (cleared with ""). Bitmap-shader maps only — the legacy
	# circle fixture keeps hover-only feedback. A fresh selection fires a brief
	# brightness pulse so the click visibly "took".
	selected_region = region_name if province_shapes.has(region_name) else ""
	if _highlight_material == null:
		return
	_highlight_material.set_shader_parameter("selected_key", _lookup_key_for(selected_region))
	if _select_pulse_tween != null and _select_pulse_tween.is_valid():
		_select_pulse_tween.kill()
	_select_pulse_tween = null
	if selected_region == "":
		_highlight_material.set_shader_parameter("selected_boost", 0.0)
		return
	_highlight_material.set_shader_parameter("selected_boost", 1.0)
	_select_pulse_tween = create_tween()
	_select_pulse_tween.tween_method(
		func(v): _highlight_material.set_shader_parameter("selected_boost", v),
		1.0, 0.0, 0.45
	).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)


func _refresh_highlight_texture():
	if highlight_map_layer == null:
		return
	# Shader path: one uniform write, no per-pixel CPU work (G4 budget shape).
	if _highlight_material != null:
		_highlight_material.set_shader_parameter("hover_key", _lookup_key_for(hovered_region))
		return
	if hovered_region == "" or not province_shapes.has(hovered_region) or map_canvas_size == Vector2.ZERO:
		_clear_highlight_texture()
		return

	var image_width = max(1, int(ceil(map_canvas_size.x)))
	var image_height = max(1, int(ceil(map_canvas_size.y)))
	var highlight_image = Image.create(image_width, image_height, false, Image.FORMAT_RGBA8)
	highlight_image.fill(Color(0, 0, 0, 0))
	var shape: Dictionary = province_shapes[hovered_region]
	var center: Vector2 = shape["center"] - map_origin
	var radius = float(shape["radius"]) + 5.0
	_draw_circle_on_image(highlight_image, center, radius, Color(1.0, 0.94, 0.78, 0.12))
	_draw_circle_outline_on_image(highlight_image, center, radius, Color(1.0, 0.9, 0.62, 0.85), 4)
	highlight_map_texture = ImageTexture.create_from_image(highlight_image)
	highlight_map_layer.texture = highlight_map_texture


func _create_scene_layers():
	viewport_background = ColorRect.new()
	viewport_background.name = "ViewportBackground"
	viewport_background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewport_background.set_anchors_preset(Control.PRESET_FULL_RECT)
	viewport_background.color = MAP_BACKGROUND_COLOR
	if _bitmap_mode:
		viewport_background.color = BITMAP_LETTERBOX_COLOR
	add_child(viewport_background)

	# UI-2 Part 2 — native-resolution map under content_scale_factor.
	# The SubViewport is hosted directly (no stretch-drawing SubViewportContainer)
	# and sized to PHYSICAL pixels (logical size * content_scale_factor) by
	# _refresh_map_viewport_resolution(). A dedicated TextureRect scales its
	# texture (STRETCH_SCALE) into the logical full-rect — 1 render texel : 1
	# physical pixel = crisp at any UI scale. The old container stretch-drew a
	# logical-sized render target which the global content scale then magnified
	# (soft at scale > 1.0). Input is handled by this Control's own _input(), so
	# dropping the container's input routing is intentional.
	map_viewport = SubViewport.new()
	map_viewport.name = "MapViewport"
	map_viewport.disable_3d = true
	map_viewport.handle_input_locally = false
	map_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	map_viewport.transparent_bg = true
	add_child(map_viewport)

	map_display = TextureRect.new()
	map_display.name = "MapDisplay"
	map_display.mouse_filter = Control.MOUSE_FILTER_IGNORE
	map_display.set_anchors_preset(Control.PRESET_FULL_RECT)
	map_display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	map_display.stretch_mode = TextureRect.STRETCH_SCALE
	map_display.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	map_display.texture = map_viewport.get_texture()
	add_child(map_display)

	_refresh_map_viewport_resolution()

	map_root = Node2D.new()
	map_root.name = "MapRoot"
	map_viewport.add_child(map_root)

	map_camera = Camera2D.new()
	map_camera.name = "MapCamera"
	map_camera.enabled = true
	map_camera.anchor_mode = Camera2D.ANCHOR_MODE_DRAG_CENTER
	map_root.add_child(map_camera)

	world_layer = Control.new()
	world_layer.name = "WorldLayer"
	world_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	world_layer.show_behind_parent = true
	world_layer.position = world_bounds.position
	world_layer.size = world_bounds.size
	map_root.add_child(world_layer)

	visual_map_layer = TextureRect.new()
	visual_map_layer.name = "VisualMapLayer"
	visual_map_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	visual_map_layer.position = map_origin - world_bounds.position
	visual_map_layer.size = map_canvas_size
	visual_map_layer.stretch_mode = TextureRect.STRETCH_SCALE
	# Slice 7.5 fold: the commissioned art scales smoothly (mipmapped linear
	# — NEAREST was blocky zoomed in and shimmered minified). The legacy
	# circle canvas keeps hard NEAREST edges. The owner-fill layer must stay
	# NEAREST regardless: filtering would blend province lookup keys at
	# borders and break the shader's exact palette match.
	visual_map_layer.texture_filter = (
		CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS if _bitmap_mode
		else CanvasItem.TEXTURE_FILTER_NEAREST
	)
	visual_map_layer.z_index = -2
	visual_map_layer.texture = visual_map_texture
	world_layer.add_child(visual_map_layer)

	_create_owner_fill_layer()

	highlight_map_layer = TextureRect.new()
	highlight_map_layer.name = "ProvinceHighlightLayer"
	highlight_map_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	highlight_map_layer.position = map_origin - world_bounds.position
	highlight_map_layer.size = map_canvas_size
	highlight_map_layer.stretch_mode = TextureRect.STRETCH_SCALE
	highlight_map_layer.z_index = -1
	_highlight_material = null
	if _bitmap_mode and province_lookup_image != null:
		# Shader path: the layer displays the lookup mask itself and the shader
		# lights matching fragments. NEAREST is mandatory — filtering would
		# blend lookup keys at borders and break the exact palette match (same
		# rule as the owner-fill layer).
		highlight_map_layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		highlight_map_layer.texture = ImageTexture.create_from_image(province_lookup_image)
		var highlight_shader = Shader.new()
		highlight_shader.code = HIGHLIGHT_SHADER
		_highlight_material = ShaderMaterial.new()
		_highlight_material.shader = highlight_shader
		_highlight_material.set_shader_parameter("hover_key", _lookup_key_for(hovered_region))
		_highlight_material.set_shader_parameter("selected_key", _lookup_key_for(selected_region))
		_highlight_material.set_shader_parameter("selected_boost", 0.0)
		highlight_map_layer.material = _highlight_material
	else:
		highlight_map_layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		highlight_map_layer.texture = highlight_map_texture
	world_layer.add_child(highlight_map_layer)

	connection_layer = MapConnectionLayer.new()
	connection_layer.name = "ConnectionLayer"
	connection_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	connection_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	connection_layer.z_index = 0
	world_layer.add_child(connection_layer)

	region_layer = Control.new()
	region_layer.name = "RegionLayer"
	region_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	region_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	region_layer.z_index = 1
	world_layer.add_child(region_layer)

	# UI-5: war-table pieces — tin-flat standees at marshal anchors. A Node2D
	# (not a Control) so it can y-sort its children by depth and each piece can
	# tween. z_index 2 = above the province art/region fills, and — added BEFORE
	# force_layer (same z) — it draws UNDER the marshal name labels so text stays
	# readable over the pieces. Bitmap-art maps only (the war-table fantasy is on
	# the commissioned map); the legacy circle fixture keeps its square icons.
	pieces_layer = null
	if _bitmap_mode and WarTablePiece.pieces_available():
		pieces_layer = Node2D.new()
		pieces_layer.name = "WarTablePieceLayer"
		pieces_layer.y_sort_enabled = true
		pieces_layer.z_index = 2
		world_layer.add_child(pieces_layer)

	force_layer = Control.new()
	force_layer.name = "ForceLayer"
	force_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	force_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	force_layer.z_index = 2
	world_layer.add_child(force_layer)

	garrison_layer = Control.new()
	garrison_layer.name = "GarrisonLayer"
	garrison_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	garrison_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	garrison_layer.z_index = 3
	world_layer.add_child(garrison_layer)

	# Slice 7.5 (DEF-11, screen-space fold): zoom-LOD name labels — a SCREEN-
	# SPACE overlay (sibling of the tooltip layer) that re-projects world
	# anchors through the camera transform each draw. NOT a world_layer child:
	# world-space text rasterized glyphs at tiny world font sizes and the
	# camera scaled them up blurry, and constant-screen-size labels read as
	# "shrinking" while the map grew. Bitmap-art maps only — the legacy circle
	# map draws its own per-region labels in _build_region_nodes.
	map_label_layer = null
	if _bitmap_mode:
		map_label_layer = MapLabelLayer.new()
		map_label_layer.name = "MapLabelLayer"
		map_label_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
		map_label_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
		map_label_layer.z_index = 50
		map_label_layer.setup(self)
		add_child(map_label_layer)
		# Re-apply any UI rects pushed before the layer existed.
		if not _ui_avoid_global_rects.is_empty():
			map_label_layer.set_ui_avoid_rects(_ui_avoid_global_rects)

	tooltip_layer = MapTooltipLayer.new()
	tooltip_layer.name = "TooltipLayer"
	tooltip_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tooltip_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	tooltip_layer.z_index = 100
	add_child(tooltip_layer)


func _create_owner_fill_layer():
	# Map Slice 6: political ownership fills. Same z_index as the visual layer
	# but a later sibling, so it draws above the terrain art and below the
	# hover highlight (z -1). Skipped entirely on the circle-fallback path.
	owner_fill_layer = null
	if not _bitmap_mode or province_lookup_image == null:
		return
	if province_shapes.size() > OWNER_FILL_MAX_PROVINCES:
		push_error(
			"Owner-fill palette holds %d provinces; registry has %d — the overflow will never tint" %
			[OWNER_FILL_MAX_PROVINCES, province_shapes.size()]
		)

	owner_fill_layer = TextureRect.new()
	owner_fill_layer.name = "OwnerFillLayer"
	owner_fill_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	owner_fill_layer.position = map_origin - world_bounds.position
	owner_fill_layer.size = map_canvas_size
	owner_fill_layer.stretch_mode = TextureRect.STRETCH_SCALE
	owner_fill_layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	owner_fill_layer.z_index = -2
	owner_fill_layer.texture = ImageTexture.create_from_image(province_lookup_image)

	var shader = Shader.new()
	shader.code = OWNER_FILL_SHADER
	var fill_material = ShaderMaterial.new()
	fill_material.shader = shader

	# Both palette arrays MUST iterate _owner_fill_province_order so slot i's
	# lookup color and owner color describe the same province. Arrays are
	# always uploaded at exactly OWNER_FILL_MAX_PROVINCES entries — a short
	# upload would leave zeroed tail slots.
	_owner_fill_province_order = []
	var lookups := PackedColorArray()
	lookups.resize(OWNER_FILL_MAX_PROVINCES)
	for region_name in province_shapes:
		if _owner_fill_province_order.size() >= OWNER_FILL_MAX_PROVINCES:
			break
		_owner_fill_province_order.append(region_name)
	for i in range(_owner_fill_province_order.size()):
		lookups[i] = province_shapes[_owner_fill_province_order[i]]["lookup_color"]
	fill_material.set_shader_parameter("lookup_colors", lookups)
	fill_material.set_shader_parameter("province_count", _owner_fill_province_order.size())
	fill_material.set_shader_parameter("fill_strength", OWNER_FILL_STRENGTH)
	owner_fill_layer.material = fill_material
	world_layer.add_child(owner_fill_layer)

	_refresh_owner_fill_palette()


func _refresh_owner_fill_palette():
	# G4 hot path: an ownership change costs one <=128-entry uniform upload.
	# Called on every update_all_regions/update_region, including the legacy
	# circle map where no owner layer exists — must no-op there.
	if owner_fill_layer == null:
		return
	var owners := PackedColorArray()
	owners.resize(OWNER_FILL_MAX_PROVINCES)
	for i in range(_owner_fill_province_order.size()):
		var region_name: String = _owner_fill_province_order[i]
		var owner_color := Color(0, 0, 0, 0)
		if region_controllers.has(region_name) and _is_region_wired(region_name):
			var controller = str(region_controllers[region_name])
			owner_color = Utils.NATION_COLORS.get(controller, Utils.COLOR_ENEMY_DEFAULT)
		# Map Slice 7: province-level fog rides the same palette entry (legacy
		# parity with the circle map's FogOverlay panels). rgb lerps toward the
		# fog color by its alpha (scaled by FOG_HUE_LERP_SCALE since Slice 7.5
		# so the national hue survives the wash — DEF-10); alpha takes the max
		# so unknown-but-unowned provinces still get a dark wash over the raw
		# art. Pure per-province color math ahead of the SAME single uniform
		# upload — the G4 re-tint budget (no per-pixel work) is preserved.
		var visibility := str(region_visibility.get(region_name, "full"))
		var fog: Color = FOG_OVERLAYS.get(visibility, FOG_OVERLAYS["full"])
		if fog.a > 0.0:
			var hue_wash: float = fog.a * FOG_HUE_LERP_SCALE
			owner_color = Color(
				lerpf(owner_color.r, fog.r, hue_wash),
				lerpf(owner_color.g, fog.g, hue_wash),
				lerpf(owner_color.b, fog.b, hue_wash),
				maxf(owner_color.a, fog.a)
			)
		owners[i] = owner_color
	owner_fill_layer.material.set_shader_parameter("owner_colors", owners)


func cycle_map_fill_mode() -> String:
	# Slice 7.5 (DEF-12 cheap tier): M key cycles blended -> political ->
	# terrain. Returns the new mode key so callers can surface it.
	var idx: int = MAP_FILL_MODE_ORDER.find(_map_fill_mode)
	_map_fill_mode = MAP_FILL_MODE_ORDER[(idx + 1) % MAP_FILL_MODE_ORDER.size()]
	_apply_map_fill_mode()
	return _map_fill_mode


func _apply_map_fill_mode():
	# One fill_strength uniform write — the same G4 budget shape as the
	# palette upload; no-ops on the legacy circle map (no owner layer).
	if owner_fill_layer == null:
		return
	owner_fill_layer.material.set_shader_parameter(
		"fill_strength", MAP_FILL_MODE_STRENGTHS[_map_fill_mode]
	)


func _refresh_map_labels():
	# Slice 7.5 (DEF-11): rebuild both label tiers from the same ownership
	# state the owner fill renders (region_controllers) — labels can never
	# reveal more than the fill already tints. Province tier reads the
	# registry's label_anchor; nation tier sits at the radius^2-weighted
	# centroid of owned provinces, SNAPPED back onto an owned province when
	# the raw centroid falls outside every owned blob (multi-blob nations
	# like Naples+Sicily otherwise print their name in open sea).
	# Per-province work only; no per-pixel cost.
	if map_label_layer == null:
		return
	var province_labels: Array = []
	var nation_accum := {}
	for region_name in province_shapes:
		var shape: Dictionary = province_shapes[region_name]
		if not bool(shape.get("wired", true)):
			continue
		# WORLD coords — the screen-space layer projects them through the
		# camera transform at draw time.
		var label_pos: Vector2 = shape.get("label_anchor", shape.get("center", Vector2.ZERO))
		province_labels.append({"text": region_name, "position": label_pos})
		if not region_controllers.has(region_name):
			continue
		var controller := str(region_controllers[region_name])
		if controller == "" or controller == "Neutral":
			continue
		var radius := float(shape.get("radius", REGION_RADIUS))
		var weight := radius * radius
		if not nation_accum.has(controller):
			nation_accum[controller] = [Vector2.ZERO, 0.0, []]
		nation_accum[controller][0] += label_pos * weight
		nation_accum[controller][1] += weight
		nation_accum[controller][2].append({
			"label_pos": label_pos,
			"center": shape.get("center", label_pos),
			"radius": radius,
		})
	var nation_labels: Array = []
	for nation in nation_accum:
		var weight_sum: float = nation_accum[nation][1]
		if weight_sum <= 0.0:
			continue
		var centroid: Vector2 = nation_accum[nation][0] / weight_sum
		nation_labels.append({
			"text": Utils.display_nation_name(str(nation)),
			"position": _snap_label_to_owned_land(centroid, nation_accum[nation][2]),
		})
	map_label_layer.set_labels(nation_labels, province_labels)


func _snap_label_to_owned_land(centroid: Vector2, provinces: Array) -> Vector2:
	# Multi-blob nations (Naples + Sicily, Piedmont + Sardinia) can average
	# their provinces to a point in open water. Province circles overlap when
	# tiling a landmass, so a centroid inside ANY owned circle is on (or hugging)
	# the nation's own soil and keeps its nice central placement; a centroid
	# outside every circle is at sea and snaps to the hand-authored label
	# anchor of the nearest owned blob instead.
	var best_pos: Vector2 = centroid
	var best_gap: float = INF
	for prov in provinces:
		var gap: float = centroid.distance_to(prov["center"]) - float(prov["radius"])
		if gap <= 0.0:
			return centroid
		if gap < best_gap:
			best_gap = gap
			best_pos = prov["label_pos"]
	return best_pos


func _build_static_map_visuals():
	connection_layer.clear_connections()
	_clear_children(region_layer)
	region_nodes.clear()
	_build_connection_nodes()
	_build_region_nodes()
	_refresh_all_region_visuals()
	_refresh_map_labels()


func _world_to_layer_position(world_position: Vector2) -> Vector2:
	return world_position - world_bounds.position


func _build_connection_nodes():
	var positions = _get_active_region_positions()
	var connections = _get_region_connections()
	var colors = _get_colors()
	var drawn_connections := {}
	var segments: Array = []

	for region_name in connections:
		var start_pos = positions.get(region_name, null)
		if start_pos == null:
			continue
		for adjacent in connections[region_name]:
			var end_pos = positions.get(adjacent, null)
			if end_pos == null:
				continue
			var connection_key = [region_name, adjacent]
			connection_key.sort()
			var key_text = str(connection_key)
			if key_text in drawn_connections:
				continue

			segments.append({
				"start": _world_to_layer_position(start_pos),
				"end": _world_to_layer_position(end_pos),
			})
			drawn_connections[key_text] = true

	connection_layer.set_connections(segments, colors.get("connection", Color(0.6, 0.6, 0.6)), 2.0)


func _build_region_nodes():
	var positions = _get_active_region_positions()
	for region_name in positions:
		var pos: Vector2 = positions[region_name]
		var layer_pos = _world_to_layer_position(pos)

		var root = Control.new()
		root.name = "%sRegionRoot" % region_name
		root.mouse_filter = Control.MOUSE_FILTER_IGNORE
		root.position = layer_pos - Vector2(REGION_RADIUS, REGION_RADIUS)
		root.size = Vector2(REGION_DIAMETER, REGION_DIAMETER)
		region_layer.add_child(root)

		var fill = Panel.new()
		fill.name = "Fill"
		fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
		fill.position = Vector2.ZERO
		fill.size = root.size
		root.add_child(fill)

		var overlay = Panel.new()
		overlay.name = "FogOverlay"
		overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
		overlay.position = Vector2.ZERO
		overlay.size = root.size
		root.add_child(overlay)

		var label = Label.new()
		label.name = "%sLabel" % region_name
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		label.position = layer_pos + Vector2(-REGION_LABEL_WIDTH / 2.0, -5.0)
		label.size = Vector2(REGION_LABEL_WIDTH, REGION_LABEL_HEIGHT)
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		label.add_theme_font_size_override("font_size", 14)
		label.text = region_name
		region_layer.add_child(label)

		region_nodes[region_name] = {
			"fill": fill,
			"overlay": overlay,
			"label": label,
		}


func _refresh_all_region_visuals():
	for region_name in _get_active_region_positions():
		_refresh_region_visual(region_name)


func _refresh_region_visual(region_name: String):
	if not region_nodes.has(region_name):
		return

	var colors = _get_colors()
	var controller = region_controllers.get(region_name, "Neutral")
	var visibility = region_visibility.get(region_name, "full")
	var fill_color = colors.get(controller, Color(1.0, 0.0, 1.0))
	var fog_color = FOG_OVERLAYS.get(visibility, FOG_OVERLAYS["full"])
	var border_color = Color.BLACK

	if region_name in _get_capital_regions():
		border_color = Color(0.85, 0.75, 0.3)
	elif visibility == "unknown" or visibility == "last_known":
		border_color = Color(0.25, 0.25, 0.3)

	var label_color = Color.WHITE if controller != "Neutral" else Color.BLACK
	if visibility == "unknown" or visibility == "last_known":
		label_color = Color(0.5, 0.5, 0.55)
	elif visibility == "stale":
		label_color = Color(0.7, 0.7, 0.75)

	var nodes: Dictionary = region_nodes[region_name]
	var border_width = 2.0
	if region_name in _get_capital_regions():
		border_width = 3.0
	nodes["fill"].add_theme_stylebox_override(
		"panel",
		_make_box_style(fill_color, border_color, border_width, int(REGION_RADIUS))
	)
	nodes["overlay"].add_theme_stylebox_override(
		"panel",
		_make_box_style(fog_color, Color(0, 0, 0, 0), 0.0, int(REGION_RADIUS))
	)
	nodes["label"].add_theme_color_override("font_color", label_color)


func _rebuild_dynamic_nodes():
	_clear_children(force_layer)
	_clear_children(garrison_layer)
	marshal_hitboxes.clear()
	fogged_force_hitboxes.clear()
	_label_avoid_world_rects.clear()
	var positions = _get_active_region_positions()

	for region_name in positions:
		var region_pos: Vector2 = positions[region_name]
		var regular_count = 0

		if region_marshals.has(region_name):
			var marshals = region_marshals[region_name]
			regular_count = marshals.size()
			_create_marshal_nodes(region_pos, marshals)

		if region_fogged_forces.has(region_name):
			_create_fogged_force_nodes(region_pos, region_fogged_forces[region_name], regular_count)

		if region_garrisons.has(region_name):
			var controller = region_controllers.get(region_name, "Neutral")
			var visibility = region_visibility.get(region_name, "full")
			_create_garrison_node(region_pos, region_garrisons[region_name], controller, visibility)

	if map_label_layer != null:
		map_label_layer.set_avoid_rects(_label_avoid_world_rects)
	_refresh_hover_state()


func set_ui_avoid_rects(global_rects: Array) -> void:
	"""Screen-space UI panels the map labels must not draw over (main.gd
	pushes the command terminal's rect on every layout pass)."""
	_ui_avoid_global_rects = global_rects.duplicate()
	if map_label_layer != null:
		map_label_layer.set_ui_avoid_rects(_ui_avoid_global_rects)


func _marshal_slot_offset(i: int, count: int) -> float:
	# x component of the shared slot math (legacy callers).
	return _marshal_slot_offset_2d(i, count).x


func _marshal_slot_offset_2d(i: int, count: int) -> Vector2:
	# Symmetric spread for co-located marshals — shared by the standee layer,
	# the name labels, and the hover hitboxes so a name rests over its own
	# piece (the label is rebuilt at the destination each refresh; during a
	# march the piece tweens up to it over WAR_PIECE_MOVE_DURATION).
	# UI-6 (U5 residual): 1-2 pieces keep the flat x-line; 3+ split into two
	# ranks (even indexes front, odd indexes a rank back) so a massed
	# province stops drawing as one overlapping smear.
	# IGR-G2: 5+ split into THREE ranks (i % ranks round-robin, generalizing
	# the two-rank math — the 3-4 piece shape is numerically unchanged) so a
	# Grande-Armee stack grows back instead of stretching one long x-line.
	if count <= 2:
		return Vector2((float(i) - float(count - 1) / 2.0) * WAR_PIECE_SLOT_SPACING, 0.0)
	var ranks := 2 if count <= 4 else 3
	var rank := i % ranks
	var idx := int(i / float(ranks))
	# Pieces in this rank: indexes {rank, rank+ranks, ...} below count.
	var rank_count := int(ceil(float(count - rank) / float(ranks)))
	var x := (float(idx) - float(rank_count - 1) / 2.0) * WAR_PIECE_SLOT_SPACING
	var y := -float(rank) * WAR_PIECE_RANK_DEPTH
	return Vector2(x, y)


func _create_marshal_nodes(region_pos: Vector2, marshals: Array):
	var font = ThemeDB.fallback_font
	var pieces_active := pieces_layer != null
	var colors = _get_colors()
	# Legacy square-icon horizontal layout (only used when pieces are inactive).
	var total_width = marshals.size() * MARSHAL_ICON_SIZE.x + max(0, marshals.size() - 1) * MARSHAL_ICON_SPACING
	var start_x = -total_width / 2.0

	# IGR-G2: above 3 co-located pieces the per-marshal name pile (a 13px
	# stagger of 40-60px-wide names over 38px slots) is unreadable at every
	# zoom — draw ONE stack label ("Ney +4") instead. Hover hitboxes stay
	# per-marshal, so the tooltip still identifies each piece.
	var use_stack_label := pieces_active and marshals.size() > 3

	for i in range(marshals.size()):
		var marshal: Dictionary = marshals[i]
		var marshal_name = str(marshal.get("name", "?"))
		var nation = str(marshal.get("nation", "Neutral"))
		var name_width = font.get_string_size(marshal_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x + 4.0

		# label_anchor_world = top-left of the name label (WORLD coords);
		# hitbox_rect = the hover target (WORLD coords).
		var label_anchor_world: Vector2
		var hitbox_rect: Rect2

		if pieces_active:
			# The standee IS the marshal's map presence (drawn by
			# _update_war_table_pieces, spread by the same slot math). Skip the
			# colored square; float the name above the standee and size the hover
			# box to its footprint.
			var slot := _marshal_slot_offset_2d(i, marshals.size())
			var name_y := -(WAR_PIECE_FRAME_PX * 0.6 + 8.0 + i * 13.0)
			label_anchor_world = region_pos + Vector2(slot.x - name_width / 2.0, name_y)
			var box_w := maxf(WAR_PIECE_SLOT_SPACING, 34.0)
			var box_h := WAR_PIECE_FRAME_PX * 0.62
			hitbox_rect = Rect2(
				region_pos + Vector2(slot.x - box_w / 2.0, slot.y - box_h),
				Vector2(box_w, box_h)
			)
		else:
			var icon_pos = region_pos + Vector2(start_x + i * (MARSHAL_ICON_SIZE.x + MARSHAL_ICON_SPACING), MARSHAL_ICON_Y_OFFSET)
			var icon_panel = Panel.new()
			icon_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
			icon_panel.position = _world_to_layer_position(icon_pos)
			icon_panel.size = MARSHAL_ICON_SIZE
			icon_panel.add_theme_stylebox_override("panel", _make_box_style(colors.get(nation, Color(1.0, 0.0, 1.0)), Color.BLACK, 2.0, 2))
			force_layer.add_child(icon_panel)
			label_anchor_world = icon_pos + Vector2(MARSHAL_ICON_SIZE.x / 2.0 - name_width / 2.0, -15.0 - i * 14.0)
			hitbox_rect = Rect2(icon_pos, MARSHAL_ICON_SIZE)

		if not use_stack_label:
			var name_label = Label.new()
			name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
			name_label.position = _world_to_layer_position(label_anchor_world)
			name_label.size = Vector2(name_width, 14.0)
			name_label.text = marshal_name
			name_label.add_theme_font_size_override("font_size", 11)
			name_label.add_theme_color_override("font_color", Color.WHITE)
			name_label.add_theme_color_override("font_outline_color", FORCE_NAME_OUTLINE_COLOR)
			name_label.add_theme_constant_override("outline_size", FORCE_NAME_OUTLINE_SIZE)
			force_layer.add_child(name_label)
			_label_avoid_world_rects.append(Rect2(label_anchor_world, Vector2(name_width, 14.0)))

		marshal_hitboxes.append({
			"rect": hitbox_rect,
			"marshal": marshal,
		})
		_label_avoid_world_rects.append(hitbox_rect)

	if use_stack_label:
		# One aggregate label over the whole stack, centered on the slot
		# spread (slots are symmetric about region_pos.x) and lifted clear
		# of the rearmost rank's figures.
		var lead_name = str(marshals[0].get("name", "?"))
		var stack_text := "%s +%d" % [lead_name, marshals.size() - 1]
		var stack_width = font.get_string_size(stack_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x + 4.0
		var rear_ranks := 1 if marshals.size() <= 4 else 2
		var stack_y := -(WAR_PIECE_FRAME_PX * 0.6 + 8.0
				+ float(rear_ranks) * WAR_PIECE_RANK_DEPTH)
		var stack_anchor := region_pos + Vector2(-stack_width / 2.0, stack_y)
		var stack_label = Label.new()
		stack_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		stack_label.position = _world_to_layer_position(stack_anchor)
		stack_label.size = Vector2(stack_width, 14.0)
		stack_label.text = stack_text
		stack_label.add_theme_font_size_override("font_size", 11)
		stack_label.add_theme_color_override("font_color", Color.WHITE)
		stack_label.add_theme_color_override("font_outline_color", FORCE_NAME_OUTLINE_COLOR)
		stack_label.add_theme_constant_override("outline_size", FORCE_NAME_OUTLINE_SIZE)
		force_layer.add_child(stack_label)
		_label_avoid_world_rects.append(Rect2(stack_anchor, Vector2(stack_width, 14.0)))


func _marshal_arm(marshal: Dictionary) -> String:
	# One marshal is a single unit type (models/marshal.py: cavalry/artillery are
	# mutually-exclusive bools, else infantry). That IS the dominant arm.
	# The backend ships a display-only top-level "arm" for EVERY visible marshal
	# (own + FULL-visibility enemy); read it first so enemy corps key correctly.
	# tactical_state.cavalry/artillery is the player-only fallback for older
	# payloads (it is absent on enemy marshals — hence the top-level field).
	var top := str(marshal.get("arm", ""))
	if top == "cavalry" or top == "artillery" or top == "infantry":
		return top
	var ts: Dictionary = marshal.get("tactical_state", {})
	if bool(ts.get("cavalry", false)):
		return "cavalry"
	if bool(ts.get("artillery", false)):
		return "artillery"
	return "infantry"


func _update_war_table_pieces() -> void:
	# Diff the live marshal set against the persistent standee layer: retire gone
	# marshals, tween movers (facing by travel heading), spawn newcomers. Runs
	# after _rebuild_dynamic_nodes so region_marshals is current.
	if pieces_layer == null:
		return
	var colors = _get_colors()
	var positions = _get_active_region_positions()

	# Desired state: marshal name -> {anchor (layer coords), arm, nation}.
	var desired := {}
	for region_name in region_marshals:
		if not positions.has(region_name):
			continue
		var region_pos: Vector2 = positions[region_name]
		var marshals: Array = region_marshals[region_name]
		var count := marshals.size()
		for i in range(count):
			var marshal: Dictionary = marshals[i]
			var mname := str(marshal.get("name", ""))
			if mname == "":
				continue
			var world_anchor := region_pos + _marshal_slot_offset_2d(i, count)
			desired[mname] = {
				"anchor": _world_to_layer_position(world_anchor),
				"region": region_name,
				"arm": _marshal_arm(marshal),
				"nation": str(marshal.get("nation", "Neutral")),
			}

	# Retire pieces whose marshal is gone (killed / captured / fogged out).
	for mname in _war_pieces.keys():
		if not desired.has(mname):
			var gone: Node = _war_pieces[mname]
			if is_instance_valid(gone):
				gone.queue_free()
			_war_pieces.erase(mname)
			_war_piece_anchors.erase(mname)
			_war_piece_regions.erase(mname)

	# Create or update the live pieces.
	for mname in desired:
		var spec: Dictionary = desired[mname]
		var anchor: Vector2 = spec["anchor"]
		var region: String = spec["region"]
		var arm: String = spec["arm"]
		var nation_color: Color = colors.get(spec["nation"], Utils.COLOR_ENEMY_DEFAULT)

		var piece = _war_pieces.get(mname, null)
		if piece != null and is_instance_valid(piece):
			piece.set_arm(arm)
			piece.set_faction(nation_color)
			var prev_region: String = str(_war_piece_regions.get(mname, region))
			var prev: Vector2 = _war_piece_anchors.get(mname, anchor)
			if region != prev_region:
				# A REAL march — tween along the path + face the travel heading.
				if anchor.x > prev.x + 0.5:
					piece.set_facing("r")
				elif anchor.x < prev.x - 0.5:
					piece.set_facing("l")
				piece.move_to(anchor, WAR_PIECE_MOVE_DURATION)
			elif prev.distance_to(anchor) > 0.5:
				# Same region, slot re-centered because a neighbor arrived/left —
				# snap in place (no slide, no facing flip) so idle pieces are still.
				piece.position = anchor
			_war_piece_anchors[mname] = anchor
			_war_piece_regions[mname] = region
			continue

		var new_piece = WarTablePiece.new()
		pieces_layer.add_child(new_piece)
		new_piece.setup(arm, "r", nation_color, WAR_PIECE_FRAME_PX)
		new_piece.position = anchor
		_war_pieces[mname] = new_piece
		_war_piece_anchors[mname] = anchor
		_war_piece_regions[mname] = region


func _create_fogged_force_nodes(region_pos: Vector2, fogged_forces: Array, regular_marshal_offset: int):
	var font = ThemeDB.fallback_font
	var total_icons = regular_marshal_offset + fogged_forces.size()
	var total_width = total_icons * MARSHAL_ICON_SIZE.x + max(0, total_icons - 1) * MARSHAL_ICON_SPACING
	var start_x = -total_width / 2.0
	var colors = _get_colors()

	for i in range(fogged_forces.size()):
		var force: Dictionary = fogged_forces[i]
		var force_name = str(force.get("name", "?"))
		var force_nation = str(force.get("nation", "Unknown"))
		var fog_level = str(force.get("fog_level", "partial"))
		var slot = regular_marshal_offset + i
		var icon_pos = region_pos + Vector2(start_x + slot * (MARSHAL_ICON_SIZE.x + MARSHAL_ICON_SPACING), MARSHAL_ICON_Y_OFFSET)
		var layer_icon_pos = _world_to_layer_position(icon_pos)
		var nation_color = colors.get(force_nation, Color(0.5, 0.5, 0.5))
		var fill_color = nation_color.darkened(0.5 if fog_level == "partial" else 0.7)
		fill_color.a = 0.7 if fog_level == "partial" else 0.5

		var icon_panel = Panel.new()
		icon_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
		icon_panel.position = layer_icon_pos
		icon_panel.size = MARSHAL_ICON_SIZE
		icon_panel.add_theme_stylebox_override("panel", _make_box_style(fill_color, Color(0.4, 0.4, 0.45, 0.6), 1.5, 2))
		force_layer.add_child(icon_panel)

		var icon_label = Label.new()
		icon_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		icon_label.position = layer_icon_pos
		icon_label.size = MARSHAL_ICON_SIZE
		icon_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		icon_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		icon_label.text = "?"
		icon_label.add_theme_font_size_override("font_size", 12)
		icon_label.add_theme_color_override("font_color", Color(1.0, 1.0, 1.0, 0.8))
		force_layer.add_child(icon_label)

		var name_width = font.get_string_size(force_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x + 4.0
		var name_offset := Vector2(MARSHAL_ICON_SIZE.x / 2.0 - name_width / 2.0, -15.0 - slot * 14.0)
		var name_label = Label.new()
		name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		name_label.position = layer_icon_pos + name_offset
		name_label.size = Vector2(name_width, 14.0)
		name_label.text = force_name
		name_label.add_theme_font_size_override("font_size", 11)
		name_label.add_theme_color_override(
			"font_color",
			Color(0.7, 0.7, 0.75, 0.7) if fog_level == "partial" else Color(0.5, 0.5, 0.55, 0.5)
		)
		name_label.add_theme_color_override("font_outline_color", FORCE_NAME_OUTLINE_COLOR)
		name_label.add_theme_constant_override("outline_size", FORCE_NAME_OUTLINE_SIZE)
		force_layer.add_child(name_label)

		fogged_force_hitboxes.append({
			"rect": Rect2(icon_pos, MARSHAL_ICON_SIZE),
			"force": force,
		})
		_label_avoid_world_rects.append(Rect2(icon_pos, MARSHAL_ICON_SIZE))
		_label_avoid_world_rects.append(Rect2(icon_pos + name_offset, Vector2(name_width, 14.0)))


func _create_garrison_node(region_pos: Vector2, garrison_data: Dictionary, controller: String, visibility: String):
	var strength = garrison_data.get("strength", 0)
	var colors = _get_colors()
	var nation_color = colors.get(controller, Color(0.5, 0.5, 0.5))
	var fill_color = nation_color
	# Slice 7.5 review fold: light nation fills (PapalStates white, Bavaria
	# pale blue) need dark text/border — white-on-near-white was illegible.
	var text_color: Color = Utils.contrast_text_color(nation_color)
	var border_color = Color(0.9, 0.9, 0.9) if text_color == Color.WHITE else Color(0.25, 0.22, 0.18)
	var label_text = "?"
	if strength >= 1000:
		label_text = "%sk" % int(strength / 1000)
	elif strength > -1:
		label_text = str(int(strength))

	if visibility == "stale":
		fill_color = Color(nation_color.r * 0.5, nation_color.g * 0.5, nation_color.b * 0.5, 0.6)
		text_color = Color(0.7, 0.7, 0.7)
		border_color = Color(0.5, 0.5, 0.5)
	elif visibility == "partial":
		fill_color = Color(nation_color.r * 0.7, nation_color.g * 0.7, nation_color.b * 0.7, 0.8)
		text_color = Color(0.85, 0.85, 0.85)
		border_color = Color(0.7, 0.7, 0.7)

	var label_font_size = 10
	var font = ThemeDB.fallback_font
	var panel_width = GARRISON_SIZE.x
	if font != null:
		panel_width = max(GARRISON_SIZE.x, font.get_string_size(label_text, HORIZONTAL_ALIGNMENT_CENTER, -1, label_font_size).x + 10.0)
	var panel_size = Vector2(panel_width, GARRISON_SIZE.y)

	var panel = Panel.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var panel_world_pos := region_pos + Vector2(-panel_size.x / 2.0, GARRISON_Y_OFFSET - panel_size.y / 2.0)
	panel.position = _world_to_layer_position(panel_world_pos)
	panel.size = panel_size
	panel.add_theme_stylebox_override("panel", _make_box_style(fill_color, border_color, 1.5, 3))
	garrison_layer.add_child(panel)
	_label_avoid_world_rects.append(Rect2(panel_world_pos, panel_size))

	var label = Label.new()
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.position = Vector2.ZERO
	label.size = panel.size
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.text = label_text
	label.add_theme_font_size_override("font_size", label_font_size)
	label.add_theme_color_override("font_color", text_color)
	panel.add_child(label)


func _make_box_style(fill_color: Color, border_color: Color, border_width: float, corner_radius: int) -> StyleBoxFlat:
	var style = StyleBoxFlat.new()
	style.bg_color = fill_color
	style.border_color = border_color
	style.border_width_left = int(round(border_width))
	style.border_width_top = int(round(border_width))
	style.border_width_right = int(round(border_width))
	style.border_width_bottom = int(round(border_width))
	style.corner_radius_top_left = corner_radius
	style.corner_radius_top_right = corner_radius
	style.corner_radius_bottom_left = corner_radius
	style.corner_radius_bottom_right = corner_radius
	return style


func _clear_children(node: Node):
	for child in node.get_children():
		child.queue_free()


func _on_map_area_resized():
	_refresh_map_viewport_resolution()
	_update_zoom_floor()
	_update_camera_limits()
	queue_redraw()


func _target_content_scale() -> float:
	# The global UI scale (get_window().content_scale_factor). The SubViewport is
	# a separate viewport that the content scale does NOT apply to, so we bake it
	# into the render resolution ourselves (UI-2 Part 2).
	var win := get_window()
	if win == null:
		return 1.0
	return maxf(win.content_scale_factor, 0.01)


func _viewport_pixel_scale() -> float:
	# Ratio of SubViewport RENDER pixels to the Control's LOGICAL pixels — equals
	# _target_content_scale() once _refresh_map_viewport_resolution() has run.
	# Used to convert logical pointer/pan deltas into the camera's viewport-pixel
	# space (the camera's canvas_transform maps world -> physical viewport px).
	if map_viewport == null or size.x <= 0.0:
		return 1.0
	return maxf(float(map_viewport.size.x) / size.x, 0.01)


func _refresh_map_viewport_resolution() -> void:
	# UI-2 Part 2: render the map at PHYSICAL resolution so it stays crisp under a
	# global content_scale_factor > 1.0. `size` is the Control's LOGICAL rect;
	# multiply by the content scale to get physical pixels. The TextureRect then
	# scales this back into the logical full-rect at 1 texel : 1 physical pixel.
	if map_viewport == null:
		return
	var scale := _target_content_scale()
	var target := Vector2i(
		max(1, int(round(size.x * scale))),
		max(1, int(round(size.y * scale)))
	)
	if map_viewport.size != target:
		map_viewport.size = target


func refresh_viewport_scale() -> void:
	# UI-2 Part 2 hook: after the global content_scale_factor changes, resize the
	# SubViewport to the new PHYSICAL resolution (keeping the map crisp — the
	# TextureRect scales it back into the logical full-rect) and recompute the
	# camera fit metrics. On-screen COVERAGE is unchanged; only render resolution
	# tracks the scale now.
	_refresh_map_viewport_resolution()
	_update_zoom_floor()
	_update_camera_limits()
	queue_redraw()


func _get_camera_viewport_size() -> Vector2:
	if map_viewport != null and map_viewport.size.x > 0 and map_viewport.size.y > 0:
		return Vector2(map_viewport.size)
	return Vector2(max(size.x, 1.0), max(size.y, 1.0))


func _get_fit_zoom_level() -> float:
	# Contain-fit: the zoom at which the whole map is exactly visible on the
	# longer-fitting axis. Anything below it can only add out-of-map margin.
	var viewport_size = _get_camera_viewport_size()
	var width_ratio = viewport_size.x / max(world_bounds.size.x, 1.0)
	var height_ratio = viewport_size.y / max(world_bounds.size.y, 1.0)
	var fit_ratio = min(width_ratio, height_ratio)
	return fit_ratio


func _update_zoom_floor():
	# Slice 7.5 (DEF-9): min_zoom is the contain-fit ratio, recomputed on every
	# viewport resize — the map can never be zoomed out past the whole-map
	# view. The old hard 0.5 floor sat far below fit on any modern monitor and
	# let the view sink into void.
	min_zoom = clampf(_get_fit_zoom_level(), 0.05, max_zoom)
	if _zoom_level < min_zoom:
		_set_camera_zoom_level(min_zoom)


func _get_initial_zoom_level() -> float:
	# Slice 7.5 (DEF-9): boot at exact contain-fit (the whole theater visible,
	# any letterbox symmetric and parchment-toned). The old /1.18 overscan
	# deliberately zoomed past fit and guaranteed void at boot on every aspect.
	return clamp(_get_fit_zoom_level(), min_zoom, max_zoom)


func _sync_camera_zoom():
	if map_camera == null:
		return
	map_camera.zoom = Vector2(_zoom_level, _zoom_level)


func _get_camera_half_extents() -> Vector2:
	return _get_camera_viewport_size() / max(_zoom_level, 0.001) / 2.0


func _clamp_camera_position(target: Vector2) -> Vector2:
	var clamped = target
	var half_extents = _get_camera_half_extents()
	var bounds_end = world_bounds.position + world_bounds.size

	if world_bounds.size.x <= half_extents.x * 2.0:
		clamped.x = world_bounds.position.x + world_bounds.size.x / 2.0
	else:
		clamped.x = clamp(target.x, world_bounds.position.x + half_extents.x, bounds_end.x - half_extents.x)

	if world_bounds.size.y <= half_extents.y * 2.0:
		clamped.y = world_bounds.position.y + world_bounds.size.y / 2.0
	else:
		clamped.y = clamp(target.y, world_bounds.position.y + half_extents.y, bounds_end.y - half_extents.y)

	return clamped


func _set_camera_position(target: Vector2):
	if map_camera == null:
		return
	map_camera.position = _clamp_camera_position(target)
	if map_label_layer != null:
		map_label_layer.queue_redraw()
	_refresh_hover_state()
	queue_redraw()


func _set_camera_zoom_level(value: float):
	_zoom_level = clamp(value, min_zoom, max_zoom)
	_sync_camera_zoom()
	if map_camera != null:
		map_camera.position = _clamp_camera_position(map_camera.position)
	if map_label_layer != null:
		map_label_layer.set_zoom_level(_zoom_level)
	_refresh_hover_state()
	queue_redraw()


func _update_camera_limits():
	# Slice 7.5 (DEF-9): hardware limits stay wide open —
	# _clamp_camera_position() is the single clamping authority (it centers
	# each axis whenever the map is smaller than the view; see
	# CAMERA_LIMIT_DISABLED for why the old map-rect limits produced the
	# one-sided void band). The call still re-clamps after resizes.
	if map_camera == null:
		return
	map_camera.limit_left = -CAMERA_LIMIT_DISABLED
	map_camera.limit_top = -CAMERA_LIMIT_DISABLED
	map_camera.limit_right = CAMERA_LIMIT_DISABLED
	map_camera.limit_bottom = CAMERA_LIMIT_DISABLED
	_set_camera_position(map_camera.position)


func _center_view_on_map():
	if map_canvas_size != Vector2.ZERO:
		var asset_center = map_origin + map_canvas_size / 2.0
		focus_on_map_point(asset_center)
		return

	var positions = _get_active_region_positions()
	if positions.is_empty():
		return

	var min_x = INF
	var max_x = -INF
	var min_y = INF
	var max_y = -INF

	for pos in positions.values():
		min_x = min(min_x, pos.x)
		max_x = max(max_x, pos.x)
		min_y = min(min_y, pos.y)
		max_y = max(max_y, pos.y)

	var map_center = Vector2((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)
	focus_on_map_point(map_center)


func focus_on_map_point(map_point: Vector2):
	_set_camera_position(map_point)


func focus_on_region(region_name: String):
	var positions = _get_active_region_positions()
	if positions.has(region_name):
		focus_on_map_point(positions[region_name])


func _process(delta: float):
	var focused = get_viewport().gui_get_focus_owner()
	var text_focused = focused is LineEdit or focused is TextEdit

	if not text_focused and panning_enabled:
		var pan_input = Vector2.ZERO
		if pan_keys_pressed["left"]:
			pan_input.x += 1
		if pan_keys_pressed["right"]:
			pan_input.x -= 1
		if pan_keys_pressed["up"]:
			pan_input.y += 1
		if pan_keys_pressed["down"]:
			pan_input.y -= 1
		if pan_input != Vector2.ZERO:
			var world_delta = Vector2(-pan_input.x, -pan_input.y) * PAN_SPEED_KEYS * delta * _viewport_pixel_scale() / _zoom_level
			_set_camera_position(map_camera.position + world_delta)
	elif pan_keys_pressed["left"] or pan_keys_pressed["right"] or pan_keys_pressed["up"] or pan_keys_pressed["down"]:
		_clear_pan_key_state()


func _input(event):
	if event is InputEventKey:
		_handle_pan_key_event(event)
		return

	if not _should_handle_map_pointer_event(event):
		if event is InputEventMouseMotion:
			_clear_hover_state()
			queue_redraw()
		return

	if event is InputEventMouseMotion:
		mouse_position = event.position
		if is_panning:
			var drag_delta = event.position - pan_start_pos
			pan_start_pos = event.position
			_set_camera_position(map_camera.position - drag_delta * _viewport_pixel_scale() / _zoom_level)
		else:
			_refresh_hover_state()
			queue_redraw()
		return

	if event is InputEventMouseButton and event.pressed:
		if event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_MIDDLE]:
			get_viewport().gui_release_focus()
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_zoom_at_point(event.position, 1.0 + ZOOM_SPEED)
			return
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_zoom_at_point(event.position, 1.0 - ZOOM_SPEED)
			return
		elif event.button_index == MOUSE_BUTTON_MIDDLE:
			is_panning = true
			pan_start_pos = event.position
			return
		elif event.button_index == MOUSE_BUTTON_LEFT:
			# Review fix: while middle-button panning, _should_handle bypasses
			# the hovered-control guard — a click mid-pan could select/dismiss
			# through the panel or terminal under the drifting cursor.
			if is_panning:
				return
			var clicked_region = _lookup_region_from_color_map(_screen_to_map_position(event.position))
			if clicked_region == "":
				clicked_region = hovered_region
			if clicked_region != "":
				# §4.4: clicks on unwired provinces are no-ops — the region is
				# outlined for coverage preview but has no gameplay data.
				if not _is_region_wired(clicked_region):
					return
				region_clicked.emit(clicked_region)
			else:
				# UX pass July 16: clicking open water reads as "click away" —
				# let the owner dismiss whatever the last province click opened.
				map_dismiss_requested.emit()
			return
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			# UX pass July 16: right-click = dismiss, the map-game convention.
			if is_panning:
				return
			map_dismiss_requested.emit()
			return

	if event is InputEventMouseButton and not event.pressed and event.button_index == MOUSE_BUTTON_MIDDLE:
		is_panning = false


func _handle_pan_key_event(event: InputEventKey):
	if event.echo:
		return
	var focused = get_viewport().gui_get_focus_owner()
	var text_focused = focused is LineEdit or focused is TextEdit
	if text_focused or not panning_enabled:
		if not event.pressed:
			_clear_pan_key_state()
		return

	match event.keycode:
		KEY_LEFT:
			pan_keys_pressed["left"] = event.pressed
		KEY_RIGHT:
			pan_keys_pressed["right"] = event.pressed
		KEY_UP:
			pan_keys_pressed["up"] = event.pressed
		KEY_DOWN:
			pan_keys_pressed["down"] = event.pressed


func _clear_pan_key_state():
	pan_keys_pressed["left"] = false
	pan_keys_pressed["right"] = false
	pan_keys_pressed["up"] = false
	pan_keys_pressed["down"] = false


func _clear_hover_state():
	hovered_marshal = {}
	hovered_fogged_force = {}
	_set_hovered_region("")


func _should_handle_map_pointer_event(event) -> bool:
	if not panning_enabled:
		return false
	if not (event is InputEventMouseMotion or event is InputEventMouseButton):
		return false
	if is_panning:
		return true
	var rect = get_global_rect()
	if not rect.has_point(event.position):
		return false
	var hovered_control = get_viewport().gui_get_hovered_control()
	if hovered_control != null and hovered_control != self and not is_ancestor_of(hovered_control):
		return false
	return true


func _draw():
	if hovered_marshal.size() > 0:
		_draw_marshal_tooltip()
	elif hovered_fogged_force.size() > 0:
		_draw_fogged_force_tooltip()
	elif hovered_region != "" and not _is_region_wired(hovered_region):
		# §4.4: unwired provinces never populate region_full_data, so the
		# standard region tooltip cannot render. Show a dedicated placeholder
		# tooltip so authors can still identify the province by name.
		_draw_unwired_region_tooltip()
	elif hovered_region != "" and region_full_data.has(hovered_region):
		_draw_region_tooltip()
	elif tooltip_layer != null:
		tooltip_layer.clear_tooltip()


func _screen_to_map_position(screen_position: Vector2) -> Vector2:
	if map_viewport == null:
		return screen_position
	var local_pos = screen_position - global_position
	# local_pos is in the Control's LOGICAL pixels; the camera's canvas_transform
	# maps world -> the SubViewport's (physical) pixel space, so scale up first
	# (UI-2 Part 2 — the SubViewport renders at physical resolution).
	return map_viewport.canvas_transform.affine_inverse() * (local_pos * _viewport_pixel_scale())


func _get_map_mouse_position() -> Vector2:
	return _screen_to_map_position(mouse_position)


func _set_hovered_region(region_name: String):
	if hovered_region == region_name:
		return
	hovered_region = region_name
	# UX pass July 16: a wired province is clickable — say so with the cursor.
	mouse_default_cursor_shape = (
		Control.CURSOR_POINTING_HAND
		if hovered_region != "" and _is_region_wired(hovered_region)
		else Control.CURSOR_ARROW
	)
	_refresh_highlight_texture()
	region_hovered.emit(hovered_region)


func _lookup_region_from_color_map(map_position: Vector2) -> String:
	if province_lookup_image == null:
		return ""

	var local_position = map_position - map_origin
	var pixel_x = int(floor(local_position.x))
	var pixel_y = int(floor(local_position.y))
	if pixel_x < 0 or pixel_y < 0:
		return ""
	if pixel_x >= province_lookup_image.get_width() or pixel_y >= province_lookup_image.get_height():
		return ""

	var pixel = province_lookup_image.get_pixel(pixel_x, pixel_y)
	var region_name = province_color_lookup.get(_color_to_key(pixel), "")
	if region_name == "":
		return ""
	if province_shapes.has(region_name) and not bool(province_shapes[region_name].get("interactive", true)):
		return ""
	return region_name


func _refresh_hover_state():
	hovered_marshal = {}
	hovered_fogged_force = {}

	var map_mouse = _get_map_mouse_position()
	var positions = _get_active_region_positions()

	for hitbox in marshal_hitboxes:
		if hitbox["rect"].has_point(map_mouse):
			hovered_marshal = hitbox["marshal"]
			_set_hovered_region("")
			return

	for hitbox in fogged_force_hitboxes:
		if hitbox["rect"].has_point(map_mouse):
			hovered_fogged_force = hitbox["force"]
			_set_hovered_region("")
			return

	var color_map_region = _lookup_region_from_color_map(map_mouse)
	if color_map_region != "":
		_set_hovered_region(color_map_region)
		return

	for region_name in positions:
		if province_shapes.has(region_name) and not bool(province_shapes[region_name].get("interactive", true)):
			continue
		if map_mouse.distance_to(positions[region_name]) <= REGION_RADIUS:
			_set_hovered_region(region_name)
			return

	_set_hovered_region("")


func _unhandled_input(event):
	var focused = get_viewport().gui_get_focus_owner()
	var text_focused = focused is LineEdit or focused is TextEdit
	if text_focused or not panning_enabled:
		return

	if event is InputEventKey and event.pressed and not event.echo:
		var screen_center = global_position + size / 2.0
		match event.physical_keycode:
			KEY_EQUAL, KEY_KP_ADD:
				_zoom_at_point(screen_center, 1.0 + ZOOM_SPEED)
			KEY_MINUS, KEY_KP_SUBTRACT:
				_zoom_at_point(screen_center, 1.0 - ZOOM_SPEED)
			KEY_HOME:
				_center_view_on_map()
			KEY_M:
				cycle_map_fill_mode()
func _zoom_at_point(point: Vector2, zoom_factor: float):
	var new_zoom = clamp(_zoom_level * zoom_factor, min_zoom, max_zoom)
	if is_equal_approx(new_zoom, _zoom_level):
		return

	var map_point_before = _screen_to_map_position(point)
	var local_point = point - global_position
	var viewport_center = size / 2.0
	# The logical cursor offset is scaled into the camera's physical viewport-px
	# space before dividing by the (world -> physical px) zoom (UI-2 Part 2).
	var target_position = map_point_before - (local_point - viewport_center) * _viewport_pixel_scale() / new_zoom
	target_position = _clamp_camera_position(target_position)

	if zoom_tween:
		zoom_tween.kill()

	zoom_tween = create_tween()
	zoom_tween.set_parallel(true)
	zoom_tween.tween_method(Callable(self, "_set_camera_zoom_level"), _zoom_level, new_zoom, ZOOM_DURATION).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	zoom_tween.tween_method(Callable(self, "_set_camera_position"), map_camera.position, target_position, ZOOM_DURATION).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	zoom_tween.finished.connect(func():
		_set_camera_zoom_level(new_zoom)
		_set_camera_position(target_position)
	)


func _clamp_tooltip_pos(pos: Vector2, tooltip_size: Vector2) -> Vector2:
	var viewport_size = get_viewport_rect().size
	if pos.x + tooltip_size.x > viewport_size.x:
		pos.x = viewport_size.x - tooltip_size.x
	if pos.y + tooltip_size.y > viewport_size.y:
		pos.y = mouse_position.y - tooltip_size.y - 5.0
	return pos


func _draw_tooltip_lines(lines: Array, width: float, panel_color: Color, border_color: Color):
	if tooltip_layer != null:
		tooltip_layer.show_tooltip(lines, width, panel_color, border_color, mouse_position)


func _measure_tooltip(lines: Array, width: float) -> Vector2:
	var padding = 10.0
	var height = padding * 2.0
	for line in lines:
		if line.get("spacer", false):
			height += float(line.get("height", 8.0))
		else:
			height += _tooltip_line_height(int(line.get("size", 11)))
	return Vector2(width, height)


func _tooltip_line_height(font_size: int) -> float:
	return 20.0 if font_size >= 14 else 16.0


func _push_tooltip_line(lines: Array, text: String, color: Color, size: int = 11):
	lines.append({
		"text": text,
		"color": color,
		"size": size,
	})


func _push_tooltip_spacer(lines: Array, height: float = 8.0):
	lines.append({
		"spacer": true,
		"height": height,
	})


func _draw_marshal_tooltip():
	var marshal = hovered_marshal
	var lines: Array = []

	_push_tooltip_line(lines, str(marshal.get("name", "Unknown")), Color.WHITE, 14)
	_push_tooltip_line(lines, Utils.display_nation_name(str(marshal.get("nation", "Neutral"))), Color(0.7, 0.7, 0.7))
	_push_tooltip_spacer(lines, 8.0)

	_push_tooltip_line(lines, "Troops: " + _format_number(marshal.get("strength", 0)), Color.WHITE)
	_push_tooltip_line(lines, "Morale: %s%%" % int(marshal.get("morale", 0)), Color.WHITE)
	_push_tooltip_line(lines, "Movement: Range %s" % int(marshal.get("movement_range", 1)), Color.WHITE)

	var skills = marshal.get("skills", {})
	if skills.size() > 0:
		_push_tooltip_spacer(lines, 8.0)
		_push_tooltip_line(
			lines,
			"Skills: Shock %s | Def %s | Tac %s" % [
				int(skills.get("shock", 0)),
				int(skills.get("defense", 0)),
				int(skills.get("tactical", 0)),
			],
			Color(0.6, 0.8, 0.6)
		)

	var personality = str(marshal.get("personality", ""))
	if personality != "":
		_push_tooltip_spacer(lines, 8.0)
		_push_tooltip_line(lines, "Type: " + personality.capitalize(), Color(0.85, 0.85, 0.5))

		var trust = int(marshal.get("trust", 0))
		var trust_color = Color(0.5, 0.85, 0.5)
		if trust < 40:
			trust_color = Color(0.85, 0.5, 0.5)
		elif trust < 60:
			trust_color = Color(0.85, 0.75, 0.5)
		_push_tooltip_line(
			lines,
			"Trust: %s (%s)" % [trust, str(marshal.get("trust_label", ""))],
			trust_color
		)

		var vindication = int(marshal.get("vindication", 0))
		var vindication_text = "Track record: Neutral"
		if vindication >= 3:
			vindication_text = "Track record: Often right +%s" % vindication
		elif vindication >= 1:
			vindication_text = "Track record: Good +%s" % vindication
		elif vindication <= -3:
			vindication_text = "Track record: Often wrong %s" % vindication
		elif vindication <= -1:
			vindication_text = "Track record: Mixed %s" % vindication
		if marshal.get("has_pending_vindication", false):
			vindication_text += " [Pending]"
		_push_tooltip_line(lines, vindication_text, Color(0.7, 0.7, 0.9))

	var tactical_state = marshal.get("tactical_state", {})
	if tactical_state.size() > 0:
		_push_tooltip_spacer(lines, 8.0)
		var stance = str(tactical_state.get("stance", "neutral"))
		var stance_text = "Stance: NEUTRAL"
		var stance_color = Color(0.7, 0.7, 0.7)
		if stance == "aggressive":
			stance_text = "Stance: AGGRESSIVE (+15% atk, -10% def)"
			stance_color = Color(0.9, 0.4, 0.3)
		elif stance == "defensive":
			stance_text = "Stance: DEFENSIVE (-10% atk, +15% def)"
			stance_color = Color(0.4, 0.6, 0.9)
		_push_tooltip_line(lines, stance_text, stance_color)

		if tactical_state.get("square_formation", false):
			_push_tooltip_line(lines, "SQUARE (+5% def, cav -40%, arty +50%)", Color(0.9, 0.8, 0.3))

		var cavalry = tactical_state.get("cavalry", false)
		var artillery = tactical_state.get("artillery", false)
		if cavalry:
			_push_tooltip_line(lines, "CAVALRY: Can attack 2 tiles away", Color(0.9, 0.6, 0.3))
		elif artillery:
			_push_tooltip_line(lines, "ARTILLERY: Cannot attack after moving", Color(0.8, 0.6, 0.4))
		else:
			_push_tooltip_line(lines, "INFANTRY", Color(0.5, 0.7, 0.9))

		if tactical_state.get("drilling", false) or tactical_state.get("drilling_locked", false):
			var drill_text = "DRILLING - Will lock next turn"
			var drill_color = Color(0.9, 0.7, 0.3)
			if tactical_state.get("drilling_locked", false):
				drill_text = "DRILLING (Locked) - Ready turn %s" % int(tactical_state.get("drill_complete_turn", -1))
				drill_color = Color(0.9, 0.5, 0.3)
			elif tactical_state.get("drill_completes_this_turn", false):
				# MC-1 Drillmaster of Boulogne: completes tonight, never locks
				drill_text = "DRILLING - Completes this turn (remains at your orders)"
			_push_tooltip_line(lines, drill_text, drill_color)

		var shock_bonus = float(tactical_state.get("shock_bonus", 0))
		if shock_bonus > 0:
			_push_tooltip_line(lines, "SHOCK READY: +%s%% attack bonus" % int(shock_bonus * 10), Color(0.3, 0.9, 0.3))

		# MC-1c Iron Resolve: coiled stacks — render the backend's derived
		# numbers (Q3 pattern: shown = applied, no hardcoded table here)
		var iron_stacks = int(tactical_state.get("iron_resolve_stacks", 0))
		if iron_stacks > 0:
			var iron_pct = int(tactical_state.get("iron_resolve_bonus_pct", 0))
			var iron_max = int(tactical_state.get("iron_resolve_max_stacks", 3))
			_push_tooltip_line(
				lines,
				"IRON RESOLVE: %s/%s stacks (+%s%% next attack)" % [iron_stacks, iron_max, iron_pct],
				Color(0.9, 0.8, 0.3)
			)

		if tactical_state.get("fortified", false):
			var fort_text = "FORTIFIED: +%s%%" % int(tactical_state.get("defense_bonus", 0))
			var fort_color = Color(0.5, 0.7, 0.9)
			var fortify_state = tactical_state.get("fortify_state", null)
			if fortify_state is Dictionary:
				match str(fortify_state.get("direction", "none")):
					"growing":
						fort_text += " [building]"
						fort_color = Color(0.3, 0.8, 0.3)
					"decaying":
						fort_text += " [decaying]"
						fort_color = Color(0.9, 0.6, 0.3)
					"stable":
						fort_text += " [max]"
					"at_floor":
						var floor = int(fortify_state.get("floor", 0))
						if floor > 0:
							fort_text += " [floor %s%%]" % floor
						else:
							fort_text += " [collapsed]"
						fort_color = Color(0.7, 0.7, 0.5)
					"cavalry_limit":
						fort_text += " [cavalry limit]"
						fort_color = Color(0.9, 0.5, 0.3)
			_push_tooltip_line(lines, fort_text, fort_color)

		if tactical_state.get("retreating", false):
			var recovery = int(tactical_state.get("retreat_recovery", 0))
			# MC gate Q3: the penalty is command-aware — render the backend's
			# derived value, never a hardcoded table (fallback for old payloads)
			var penalty = str(tactical_state.get("retreat_penalty", ""))
			if penalty == "":
				var retreat_penalties = {0: "-45%", 1: "-30%", 2: "-15%", 3: "0%"}
				penalty = str(retreat_penalties.get(recovery, "?"))
			_push_tooltip_line(
				lines,
				"RETREATING: %s effectiveness (stage %s/3)" % [penalty, recovery],
				Color(0.9, 0.5, 0.5)
			)

		if tactical_state.get("broken", false):
			# MC gate Q3: recovery speed is command-aware — use the backend's
			# derived turns_left (fallback for old payloads)
			var turns_left = int(tactical_state.get("broken_turns_left",
				max(0, 4 - int(tactical_state.get("broken_recovery", 0)))))
			_push_tooltip_line(lines, "BROKEN: Recruit only (%s turns to recover)" % turns_left, Color(0.8, 0.2, 0.2))

		var turns_defensive = int(tactical_state.get("turns_in_defensive_stance", 0))
		if turns_defensive > 0:
			var restless = "RESTLESS: %s/3 turns defensive" % turns_defensive
			if turns_defensive >= 3:
				restless += " (objecting)"
			_push_tooltip_line(lines, restless, Color(0.9, 0.7, 0.4))

		if tactical_state.get("counter_punch_available", false):
			_push_tooltip_line(lines, "COUNTER-PUNCH READY: Free attack after defense", Color(0.4, 0.9, 0.6))

		var in_hold = tactical_state.get("holding_position", false)
		var in_strategic = tactical_state.get("in_strategic_mode", false)
		var strategic_type = str(tactical_state.get("strategic_command_type", ""))
		var strategic_target = str(tactical_state.get("strategic_target", ""))
		if in_hold or (in_strategic and strategic_type == "HOLD"):
			var hold_text = "HOLDING POSITION"
			if in_hold:
				hold_text += " (Immovable): +15% defense"
			if strategic_target != "":
				hold_text += " at " + strategic_target
			elif str(tactical_state.get("hold_region", "")) != "":
				hold_text += " at " + str(tactical_state.get("hold_region", ""))
			_push_tooltip_line(lines, hold_text, Color(0.6, 0.6, 0.9))

		if in_strategic and strategic_type != "":
			var order_text = strategic_type
			if strategic_target != "":
				order_text += " -> " + strategic_target
			_push_tooltip_line(lines, order_text, Color(0.85, 0.75, 0.55))

		if artillery:
			var remaining = max(0, 2 - int(tactical_state.get("bombardments_this_turn", 0)))
			var ammo_color = Color(0.4, 0.8, 0.4)
			if remaining == 0:
				ammo_color = Color(0.8, 0.3, 0.3)
			elif remaining == 1:
				ammo_color = Color(0.9, 0.7, 0.3)
			_push_tooltip_line(lines, "Bombardments: %s/2 remaining" % remaining, ammo_color)

	var relationships = marshal.get("relationships", {})
	if relationships.size() > 0:
		_push_tooltip_spacer(lines, 8.0)
		_push_tooltip_line(lines, "Relationships:", Color(0.8, 0.8, 0.8))
		for rel_name in relationships:
			var rel_data = relationships[rel_name]
			var rel_value = int(rel_data.get("value", 0))
			var rel_label = str(rel_data.get("label", "Professional"))
			var rel_color = Color(0.8, 0.8, 0.8)
			match rel_value:
				-2:
					rel_color = Color(0.9, 0.3, 0.3)
				-1:
					rel_color = Color(0.9, 0.6, 0.3)
				1:
					rel_color = Color(0.4, 0.9, 0.4)
				2:
					rel_color = Color(1.0, 0.84, 0.0)
			_push_tooltip_line(lines, "  %s: %s (%s)" % [rel_name, rel_label, rel_value], rel_color)

	_draw_tooltip_lines(lines, 260.0, Color(0.1, 0.1, 0.15, 0.95), Color.WHITE)


func _draw_fogged_force_tooltip():
	var force = hovered_fogged_force
	var lines: Array = []
	var fog_level = str(force.get("fog_level", "partial"))
	var intel_text = "Intel: Recent reports"
	var intel_color = Color(0.6, 0.75, 0.6)
	if fog_level == "stale":
		intel_text = "Intel: Stale (outdated)"
		intel_color = Color(0.8, 0.6, 0.4)

	_push_tooltip_line(lines, str(force.get("name", "Unknown")), Color(0.85, 0.85, 0.9), 14)
	# Display name in the text; the raw key stays in the color lookup.
	_push_tooltip_line(lines, Utils.display_nation_name(str(force.get("nation", "Unknown"))), _get_colors().get(str(force.get("nation", "Unknown")), Color(0.7, 0.7, 0.7)).lightened(0.2))
	_push_tooltip_spacer(lines, 8.0)
	_push_tooltip_line(lines, "Estimated: " + str(force.get("strength_band", "unknown forces")), Color(0.8, 0.75, 0.5))
	_push_tooltip_line(lines, intel_text, intel_color)

	_draw_tooltip_lines(lines, 220.0, Color(0.12, 0.1, 0.18, 0.95), Color(0.6, 0.6, 0.7, 0.8))


func _draw_unwired_region_tooltip():
	# §4.4: named but unimplemented province. Panel uses the dedicated warm
	# sepia palette (UNWIRED_TOOLTIP_*) so authors can never mistake an unwired
	# province for a fogged one — the fogged tooltip uses a cold blue-grey
	# panel. The suffix line also sits in its own warmer accent color so the
	# "(not yet in play)" state reads at a glance without relying on panel
	# deltas alone.
	var lines: Array = []
	_push_tooltip_line(lines, hovered_region, UNWIRED_TOOLTIP_TITLE_COLOR, 14)
	_push_tooltip_line(lines, UNWIRED_TOOLTIP_SUFFIX, UNWIRED_TOOLTIP_SUFFIX_COLOR)
	_draw_tooltip_lines(lines, 220.0, UNWIRED_TOOLTIP_PANEL, UNWIRED_TOOLTIP_BORDER)


func _draw_region_tooltip():
	var data: Dictionary = region_full_data[hovered_region]
	var visibility = str(region_visibility.get(hovered_region, "full"))
	var controller = data.get("controller", "Neutral")
	if controller == null:
		controller = "Neutral"
	var region_type = str(data.get("region_type", "town"))
	var terrain = str(data.get("terrain", "plains"))
	var lines: Array = []

	_push_tooltip_line(lines, hovered_region, Color.WHITE if visibility == "full" else Color(0.7, 0.7, 0.75), 14)
	# Display name in the text; the raw key stays in the color lookup.
	_push_tooltip_line(lines, Utils.display_nation_name(str(controller)), _get_colors().get(str(controller), Color(0.7, 0.7, 0.7)))
	_push_tooltip_spacer(lines, 8.0)

	if visibility == "unknown" or visibility == "last_known":
		_push_tooltip_line(lines, terrain.replace("_", " ").capitalize(), Color(0.5, 0.5, 0.55))
		_push_tooltip_line(lines, "No intelligence" if visibility == "unknown" else "Last known (outdated)", Color(0.6, 0.4, 0.4))
		_draw_tooltip_lines(lines, 240.0, Color(0.08, 0.08, 0.12, 0.95), Color(0.4, 0.4, 0.5))
		return

	_push_tooltip_line(lines, "%s | %s" % [region_type.replace("_", " ").capitalize(), terrain.replace("_", " ").capitalize()], Color(0.7, 0.7, 0.7))
	if visibility == "partial":
		_push_tooltip_line(lines, "Intel: Partial (reports only)", Color(0.6, 0.75, 0.6))
	elif visibility == "stale":
		_push_tooltip_line(lines, "Intel: Stale (outdated)", Color(0.8, 0.6, 0.4))

	var income_value = int(data.get("income_value", 0))
	var effective_income = int(data.get("effective_income", 0))
	var income_text = "Income: %s" % effective_income
	if effective_income != income_value:
		income_text += " (base %s)" % income_value
	_push_tooltip_line(lines, income_text, Color(0.9, 0.85, 0.4))

	var stability = int(data.get("stability", 100))
	var stability_label = str(data.get("stability_label", "Stable"))
	var stability_color = Color(0.5, 0.85, 0.5)
	if stability <= 25:
		stability_color = Color(0.85, 0.3, 0.3)
	elif stability <= 50:
		stability_color = Color(0.85, 0.5, 0.3)
	elif stability <= 75:
		stability_color = Color(0.85, 0.75, 0.4)
	_push_tooltip_line(lines, "Stability: %s%% (%s)" % [stability, stability_label], stability_color)

	_push_tooltip_line(lines, "Supply: " + _format_number(data.get("supply_capacity", 0)), Color(0.6, 0.8, 0.7))

	var garrison_info = region_garrisons.get(hovered_region, null)
	if garrison_info != null:
		var g_text = "Garrison: "
		var g_strength = int(garrison_info.get("strength", 0))
		if g_strength == -1:
			g_text += "Present (unknown strength)"
		else:
			g_text += _format_number(g_strength)
		if garrison_info.get("detachment", false):
			g_text += " [Detachment]"
		_push_tooltip_line(lines, g_text, Color(0.8, 0.6, 0.4))

	var war_damage = int(data.get("war_damage", 0))
	if war_damage > 0:
		_push_tooltip_line(lines, "War Damage: %s%%" % war_damage, Color(0.85, 0.4, 0.4))

	var watchtower_status = str(data.get("watchtower", "none"))
	if watchtower_status != "none":
		var watchtower_text = "Watchtower: "
		var watchtower_color = Color(0.6, 0.8, 0.9)
		if watchtower_status == "active":
			watchtower_text += "ACTIVE [observes adjacent]"
			watchtower_color = Color(0.5, 0.85, 0.5)
		elif watchtower_status == "under_construction":
			watchtower_text += "Under Construction (%s turns)" % int(data.get("watchtower_turns_remaining", 0))
			watchtower_color = Color(0.85, 0.75, 0.4)
		elif watchtower_status == "damaged":
			watchtower_text += "DAMAGED"
			watchtower_color = Color(0.85, 0.5, 0.3)
		_push_tooltip_line(lines, watchtower_text, watchtower_color)

	var buildings = data.get("buildings", [])
	var construction = data.get("building_under_construction", null)
	var max_slots = int(data.get("max_building_slots", 0))
	if max_slots > 0:
		_push_tooltip_spacer(lines, 8.0)
		var used_slots = buildings.size()
		if construction != null:
			used_slots += 1
		_push_tooltip_line(lines, "Buildings (%s/%s):" % [used_slots, max_slots], Color(0.7, 0.8, 0.9))
		for building in buildings:
			var building_text = "  " + str(building.get("type", "unknown")).replace("_", " ").capitalize()
			var building_color = Color(0.6, 0.8, 0.6)
			if building.get("damaged", false):
				building_text += " [DAMAGED]"
				building_color = Color(0.85, 0.5, 0.3)
			_push_tooltip_line(lines, building_text, building_color)
		if construction != null:
			_push_tooltip_line(
				lines,
				"  %s (%s turns)" % [
					str(construction.get("type", "unknown")).replace("_", " ").capitalize(),
					int(construction.get("turns_remaining", 0)),
				],
				Color(0.85, 0.75, 0.4)
			)

	var friendly_marshals: Array = []
	for marshal in data.get("marshals", []):
		if marshal.get("relationships", {}).size() > 0:
			friendly_marshals.append(marshal)

	if friendly_marshals.size() >= 2:
		_push_tooltip_spacer(lines, 8.0)
		_push_tooltip_line(lines, "COORDINATION READINESS:", Color(0.85, 0.75, 0.55))

		var has_infantry = false
		var has_cavalry = false
		var has_artillery = false
		for marshal in friendly_marshals:
			var tactical_state = marshal.get("tactical_state", {})
			if tactical_state.get("cavalry", false):
				has_cavalry = true
			elif tactical_state.get("artillery", false):
				has_artillery = true
			else:
				has_infantry = true

		var unit_types: Array = []
		if has_infantry:
			unit_types.append("Inf")
		if has_cavalry:
			unit_types.append("Cav")
		if has_artillery:
			unit_types.append("Art")
		var unit_count = unit_types.size()
		var combined_arms_color = Color(0.7, 0.7, 0.7)
		if unit_count >= 2:
			combined_arms_color = Color(0.5, 0.85, 0.5)
		_push_tooltip_line(
			lines,
			"  Combined Arms: %s/3 (%s)" % [unit_count, ", ".join(PackedStringArray(unit_types))],
			combined_arms_color
		)

		for i in range(friendly_marshals.size()):
			for j in range(i + 1, friendly_marshals.size()):
				var marshal_a = friendly_marshals[i]
				var marshal_b = friendly_marshals[j]
				var name_a = str(marshal_a.get("name", ""))
				var name_b = str(marshal_b.get("name", ""))
				var rel_to_b = marshal_a.get("relationships", {}).get(name_b, {})
				var rel_label = str(rel_to_b.get("label", "Professional"))
				var rel_value = int(rel_to_b.get("value", 0))
				var rel_color = Color(0.8, 0.8, 0.8)
				match rel_value:
					-2:
						rel_color = Color(0.9, 0.3, 0.3)
					-1:
						rel_color = Color(0.9, 0.6, 0.3)
					1:
						rel_color = Color(0.4, 0.9, 0.4)
					2:
						rel_color = Color(1.0, 0.84, 0.0)

				var co_turns = int(marshal_a.get("co_location_turns", {}).get(name_b, 0))
				var pair_text = "  %s<>%s: %s" % [name_a, name_b, rel_label]
				if co_turns >= 2:
					pair_text += " [Dedicated]"
				else:
					pair_text += " (%s turns)" % co_turns
				_push_tooltip_line(lines, pair_text, rel_color)

	var panel_color = Color(0.1, 0.1, 0.15, 0.95)
	var border_color = Color.WHITE
	if visibility == "stale":
		panel_color = Color(0.1, 0.09, 0.14, 0.95)
		border_color = Color(0.7, 0.7, 0.75)
	elif visibility == "partial":
		border_color = Color(0.85, 0.85, 0.9)

	_draw_tooltip_lines(lines, 300.0 if friendly_marshals.size() >= 2 else 270.0, panel_color, border_color)


func _format_number(num) -> String:
	var num_str = str(int(num))
	var result = ""
	var count = 0

	for i in range(num_str.length() - 1, -1, -1):
		if count == 3:
			result = "," + result
			count = 0
		result = num_str[i] + result
		count += 1

	return result


func update_region(region_name: String, controller: String, marshal_data = null):
	if not _get_active_region_positions().has(region_name):
		return
	if province_shapes.has(region_name) and not bool(province_shapes[region_name].get("wired", true)):
		return

	region_controllers[region_name] = controller
	if marshal_data == null:
		region_marshals.erase(region_name)
	elif marshal_data is Array:
		if marshal_data.is_empty():
			region_marshals.erase(region_name)
		else:
			region_marshals[region_name] = marshal_data
	elif marshal_data is Dictionary:
		region_marshals[region_name] = [marshal_data]
	elif marshal_data is String and marshal_data != "":
		region_marshals[region_name] = [{"name": marshal_data}]
	else:
		region_marshals.erase(region_name)

	_refresh_region_visual(region_name)
	_refresh_owner_fill_palette()
	_refresh_map_labels()
	_rebuild_dynamic_nodes()
	_update_war_table_pieces()
	queue_redraw()


func update_all_regions(map_data: Dictionary):
	var wired_data := {}
	for region_name in map_data:
		if province_shapes.has(region_name) and not bool(province_shapes[region_name].get("wired", true)):
			region_controllers.erase(region_name)
			region_visibility.erase(region_name)
			region_marshals.erase(region_name)
			region_fogged_forces.erase(region_name)
			region_garrisons.erase(region_name)
			continue
		wired_data[region_name] = map_data[region_name]

	region_full_data = wired_data

	for region_name in wired_data:
		var data: Dictionary = wired_data[region_name]
		var controller = data.get("controller", "Neutral")
		if controller == null:
			controller = "Neutral"
		region_controllers[region_name] = controller

		var visibility = data.get("visibility_status", "full")
		if visibility == null:
			visibility = "full"
		region_visibility[region_name] = visibility

		var marshals = data.get("marshals", [])
		if marshals.is_empty():
			region_marshals.erase(region_name)
		else:
			region_marshals[region_name] = marshals

		var fogged_forces = data.get("fogged_forces", [])
		if fogged_forces.is_empty():
			region_fogged_forces.erase(region_name)
		else:
			region_fogged_forces[region_name] = fogged_forces

		var garrison_strength = int(data.get("garrison_strength", 0))
		if garrison_strength != 0:
			region_garrisons[region_name] = {
				"strength": garrison_strength,
				"detachment": data.get("garrison_detachment", false),
				"band": data.get("garrison_strength_band", ""),
			}
		else:
			region_garrisons.erase(region_name)

	_refresh_all_region_visuals()
	_refresh_owner_fill_palette()
	_refresh_map_labels()
	_rebuild_dynamic_nodes()
	_update_war_table_pieces()
	queue_redraw()

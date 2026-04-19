extends Control

signal region_hovered(region_name)
signal region_clicked(region_name)

const MapConnectionLayer = preload("res://scenes/map_connection_layer.gd")
const MapTooltipLayer = preload("res://scenes/map_tooltip_layer.gd")

const REGION_RADIUS: float = 30.0
const REGION_DIAMETER: float = REGION_RADIUS * 2.0
const REGION_LABEL_WIDTH: float = 120.0
const REGION_LABEL_HEIGHT: float = 20.0
const MARSHAL_ICON_SIZE := Vector2(16, 16)
const MARSHAL_ICON_SPACING: float = 8.0
const MARSHAL_ICON_Y_OFFSET: float = -50.0
const GARRISON_SIZE := Vector2(26, 18)
const GARRISON_Y_OFFSET: float = 38.0
const DEFAULT_CAPITAL_REGIONS := ["Paris", "Berlin", "Vienna", "London", "Madrid"]
const DEFAULT_MAP_PADDING: float = 140.0
const MAP_BACKGROUND_COLOR := Color(0.12, 0.13, 0.14, 1.0)
const INITIAL_CAMERA_OVERSCAN: float = 1.18
const NO_PROVINCE_COLOR := Color8(0, 0, 0, 255)
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
var max_zoom: float = 4.0
var is_panning: bool = false
var pan_start_pos: Vector2 = Vector2.ZERO
var zoom_tween: Tween = null
var panning_enabled: bool = true

const PAN_SPEED_KEYS: float = 300.0
const ZOOM_SPEED: float = 0.1
const ZOOM_DURATION: float = 0.2

var map_viewport_container: SubViewportContainer
var viewport_background: ColorRect
var map_viewport: SubViewport
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

var region_nodes := {}
var marshal_hitboxes: Array = []
var fogged_force_hitboxes: Array = []
var province_definition := {}
var province_shapes := {}
var province_color_lookup := {}
var province_lookup_image: Image = null
var visual_map_texture = null
var highlight_map_texture = null
var map_origin: Vector2 = Vector2.ZERO
var map_canvas_size: Vector2 = Vector2.ZERO
var world_bounds: Rect2 = Rect2(Vector2.ZERO, Vector2.ONE)
var _debug_label: Label = null


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
	_create_debug_label()


func _create_debug_label():
	_debug_label = Label.new()
	_debug_label.name = "DebugLabel"
	_debug_label.position = Vector2(10, 40)
	_debug_label.size = Vector2(600, 160)
	_debug_label.add_theme_font_size_override("font_size", 11)
	_debug_label.add_theme_color_override("font_color", Color.YELLOW)
	_debug_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_debug_label.z_index = 200
	add_child(_debug_label)


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
	visual_map_texture = ImageTexture.create_from_image(visual_image)
	_clear_highlight_texture()


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
	highlight_map_texture = null
	if highlight_map_layer != null:
		highlight_map_layer.texture = null


func _refresh_highlight_texture():
	if highlight_map_layer == null:
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
	add_child(viewport_background)

	map_viewport_container = SubViewportContainer.new()
	map_viewport_container.name = "MapViewportContainer"
	map_viewport_container.mouse_filter = Control.MOUSE_FILTER_IGNORE
	map_viewport_container.stretch = true
	map_viewport_container.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(map_viewport_container)

	map_viewport = SubViewport.new()
	map_viewport.name = "MapViewport"
	map_viewport.disable_3d = true
	map_viewport.handle_input_locally = false
	map_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	map_viewport.transparent_bg = true
	map_viewport_container.add_child(map_viewport)

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
	visual_map_layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	visual_map_layer.z_index = -2
	visual_map_layer.texture = visual_map_texture
	world_layer.add_child(visual_map_layer)

	highlight_map_layer = TextureRect.new()
	highlight_map_layer.name = "ProvinceHighlightLayer"
	highlight_map_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	highlight_map_layer.position = map_origin - world_bounds.position
	highlight_map_layer.size = map_canvas_size
	highlight_map_layer.stretch_mode = TextureRect.STRETCH_SCALE
	highlight_map_layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	highlight_map_layer.z_index = -1
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

	tooltip_layer = MapTooltipLayer.new()
	tooltip_layer.name = "TooltipLayer"
	tooltip_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tooltip_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	tooltip_layer.z_index = 100
	add_child(tooltip_layer)


func _build_static_map_visuals():
	connection_layer.clear_connections()
	_clear_children(region_layer)
	region_nodes.clear()
	_build_connection_nodes()
	_build_region_nodes()
	_refresh_all_region_visuals()


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

	_refresh_hover_state()


func _create_marshal_nodes(region_pos: Vector2, marshals: Array):
	var font = ThemeDB.fallback_font
	var total_width = marshals.size() * MARSHAL_ICON_SIZE.x + max(0, marshals.size() - 1) * MARSHAL_ICON_SPACING
	var start_x = -total_width / 2.0
	var colors = _get_colors()

	for i in range(marshals.size()):
		var marshal: Dictionary = marshals[i]
		var marshal_name = str(marshal.get("name", "?"))
		var nation = str(marshal.get("nation", "Neutral"))
		var icon_pos = region_pos + Vector2(start_x + i * (MARSHAL_ICON_SIZE.x + MARSHAL_ICON_SPACING), MARSHAL_ICON_Y_OFFSET)
		var layer_icon_pos = _world_to_layer_position(icon_pos)
		var icon_panel = Panel.new()
		icon_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
		icon_panel.position = layer_icon_pos
		icon_panel.size = MARSHAL_ICON_SIZE
		icon_panel.add_theme_stylebox_override("panel", _make_box_style(colors.get(nation, Color(1.0, 0.0, 1.0)), Color.BLACK, 2.0, 2))
		force_layer.add_child(icon_panel)

		var name_width = font.get_string_size(marshal_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x + 4.0
		var name_label = Label.new()
		name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		name_label.position = layer_icon_pos + Vector2(MARSHAL_ICON_SIZE.x / 2.0 - name_width / 2.0, -15.0 - i * 14.0)
		name_label.size = Vector2(name_width, 14.0)
		name_label.text = marshal_name
		name_label.add_theme_font_size_override("font_size", 11)
		name_label.add_theme_color_override("font_color", Color.WHITE)
		force_layer.add_child(name_label)

		marshal_hitboxes.append({
			"rect": Rect2(icon_pos, MARSHAL_ICON_SIZE),
			"marshal": marshal,
		})


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
		var name_label = Label.new()
		name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		name_label.position = layer_icon_pos + Vector2(MARSHAL_ICON_SIZE.x / 2.0 - name_width / 2.0, -15.0 - slot * 14.0)
		name_label.size = Vector2(name_width, 14.0)
		name_label.text = force_name
		name_label.add_theme_font_size_override("font_size", 11)
		name_label.add_theme_color_override(
			"font_color",
			Color(0.7, 0.7, 0.75, 0.7) if fog_level == "partial" else Color(0.5, 0.5, 0.55, 0.5)
		)
		force_layer.add_child(name_label)

		fogged_force_hitboxes.append({
			"rect": Rect2(icon_pos, MARSHAL_ICON_SIZE),
			"force": force,
		})


func _create_garrison_node(region_pos: Vector2, garrison_data: Dictionary, controller: String, visibility: String):
	var strength = garrison_data.get("strength", 0)
	var colors = _get_colors()
	var nation_color = colors.get(controller, Color(0.5, 0.5, 0.5))
	var fill_color = nation_color
	var text_color = Color.WHITE
	var border_color = Color(0.9, 0.9, 0.9)
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
	panel.position = _world_to_layer_position(region_pos + Vector2(-panel_size.x / 2.0, GARRISON_Y_OFFSET - panel_size.y / 2.0))
	panel.size = panel_size
	panel.add_theme_stylebox_override("panel", _make_box_style(fill_color, border_color, 1.5, 3))
	garrison_layer.add_child(panel)

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
	if map_viewport != null:
		var viewport_size = Vector2i(
			max(1, int(round(size.x))),
			max(1, int(round(size.y)))
		)
		map_viewport.size = viewport_size
	_update_camera_limits()
	queue_redraw()


func _get_camera_viewport_size() -> Vector2:
	if map_viewport != null and map_viewport.size.x > 0 and map_viewport.size.y > 0:
		return Vector2(map_viewport.size)
	return Vector2(max(size.x, 1.0), max(size.y, 1.0))


func _get_initial_zoom_level() -> float:
	var viewport_size = _get_camera_viewport_size()
	var width_ratio = viewport_size.x / max(world_bounds.size.x, 1.0)
	var height_ratio = viewport_size.y / max(world_bounds.size.y, 1.0)
	var fit_ratio = min(width_ratio, height_ratio)
	return clamp(fit_ratio / INITIAL_CAMERA_OVERSCAN, min_zoom, max_zoom)


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
	_refresh_hover_state()
	queue_redraw()


func _set_camera_zoom_level(value: float):
	_zoom_level = clamp(value, min_zoom, max_zoom)
	_sync_camera_zoom()
	if map_camera != null:
		map_camera.position = _clamp_camera_position(map_camera.position)
	_refresh_hover_state()
	queue_redraw()


func _update_camera_limits():
	if map_camera == null:
		return
	map_camera.limit_left = int(floor(world_bounds.position.x))
	map_camera.limit_top = int(floor(world_bounds.position.y))
	map_camera.limit_right = int(ceil(world_bounds.position.x + world_bounds.size.x))
	map_camera.limit_bottom = int(ceil(world_bounds.position.y + world_bounds.size.y))
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
			var world_delta = Vector2(-pan_input.x, -pan_input.y) * PAN_SPEED_KEYS * delta / _zoom_level
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
			_set_camera_position(map_camera.position - drag_delta / _zoom_level)
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
			var clicked_region = _lookup_region_from_color_map(_screen_to_map_position(event.position))
			if clicked_region == "":
				clicked_region = hovered_region
			if clicked_region != "":
				region_clicked.emit(clicked_region)
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
	_update_debug_label()
	if hovered_marshal.size() > 0:
		_draw_marshal_tooltip()
	elif hovered_fogged_force.size() > 0:
		_draw_fogged_force_tooltip()
	elif hovered_region != "" and region_full_data.has(hovered_region):
		_draw_region_tooltip()
	elif tooltip_layer != null:
		tooltip_layer.clear_tooltip()


func _update_debug_label():
	if _debug_label == null:
		return
	var map_mouse = _get_map_mouse_position()
	var xform = map_viewport.canvas_transform if map_viewport else Transform2D.IDENTITY
	var manual = map_camera.position + (mouse_position - global_position - size / 2.0) / _zoom_level if map_camera else mouse_position
	_debug_label.text = "Screen: %s | World(xform): %s | World(manual): %s\nCam: %s | Zoom: %.3f | GPos: %s\nSize: %s | VP: %s | Hover: %s\nXform: %s" % [
		mouse_position, map_mouse, manual,
		map_camera.position if map_camera else "null", _zoom_level, global_position,
		size, Vector2(map_viewport.size) if map_viewport else "null", hovered_region,
		xform,
	]


func _screen_to_map_position(screen_position: Vector2) -> Vector2:
	if map_viewport == null:
		return screen_position
	var local_pos = screen_position - global_position
	return map_viewport.canvas_transform.affine_inverse() * local_pos


func _get_map_mouse_position() -> Vector2:
	return _screen_to_map_position(mouse_position)


func _set_hovered_region(region_name: String):
	if hovered_region == region_name:
		return
	hovered_region = region_name
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
func _zoom_at_point(point: Vector2, zoom_factor: float):
	var new_zoom = clamp(_zoom_level * zoom_factor, min_zoom, max_zoom)
	if is_equal_approx(new_zoom, _zoom_level):
		return

	var map_point_before = _screen_to_map_position(point)
	var local_point = point - global_position
	var viewport_center = size / 2.0
	var target_position = map_point_before - (local_point - viewport_center) / new_zoom
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
	_push_tooltip_line(lines, str(marshal.get("nation", "Neutral")), Color(0.7, 0.7, 0.7))
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
			_push_tooltip_line(lines, drill_text, drill_color)

		var shock_bonus = float(tactical_state.get("shock_bonus", 0))
		if shock_bonus > 0:
			_push_tooltip_line(lines, "SHOCK READY: +%s%% attack bonus" % int(shock_bonus * 10), Color(0.3, 0.9, 0.3))

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
			var retreat_penalties = {0: "-45%", 1: "-30%", 2: "-15%", 3: "0%"}
			_push_tooltip_line(
				lines,
				"RETREATING: %s effectiveness (stage %s/3)" % [retreat_penalties.get(recovery, "?"), recovery],
				Color(0.9, 0.5, 0.5)
			)

		if tactical_state.get("broken", false):
			var turns_left = max(0, 4 - int(tactical_state.get("broken_recovery", 0)))
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
	_push_tooltip_line(lines, str(force.get("nation", "Unknown")), _get_colors().get(str(force.get("nation", "Unknown")), Color(0.7, 0.7, 0.7)).lightened(0.2))
	_push_tooltip_spacer(lines, 8.0)
	_push_tooltip_line(lines, "Estimated: " + str(force.get("strength_band", "unknown forces")), Color(0.8, 0.75, 0.5))
	_push_tooltip_line(lines, intel_text, intel_color)

	_draw_tooltip_lines(lines, 220.0, Color(0.12, 0.1, 0.18, 0.95), Color(0.6, 0.6, 0.7, 0.8))


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
	_push_tooltip_line(lines, str(controller), _get_colors().get(str(controller), Color(0.7, 0.7, 0.7)))
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
	_rebuild_dynamic_nodes()
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
	_rebuild_dynamic_nodes()
	queue_redraw()

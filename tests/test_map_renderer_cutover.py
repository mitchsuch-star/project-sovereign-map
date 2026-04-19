"""Source-level guardrails for the Session 8 renderer cutover slice."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map.gd"
BASE_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map_renderer_base.gd"
TOOLTIP_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map_tooltip_layer.gd"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _func_body(source: str, signature: str) -> str:
    return source.split(signature, 1)[1].split("\nfunc ", 1)[0]


def test_map_script_extends_renderer_base():
    source = _read(MAP_GD)
    assert 'extends "res://scenes/map_renderer_base.gd"' in source


def test_renderer_base_declares_scene_layers():
    source = _read(BASE_GD)
    for node_name in [
        'world_layer.name = "WorldLayer"',
        'visual_map_layer.name = "VisualMapLayer"',
        'highlight_map_layer.name = "ProvinceHighlightLayer"',
        'connection_layer.name = "ConnectionLayer"',
        'region_layer.name = "RegionLayer"',
        'force_layer.name = "ForceLayer"',
        'garrison_layer.name = "GarrisonLayer"',
        'tooltip_layer.name = "TooltipLayer"',
    ]:
        assert node_name in source, f"Missing renderer layer declaration: {node_name}"
    assert "world_layer.show_behind_parent = true" in source
    assert 'const MapConnectionLayer = preload("res://scenes/map_connection_layer.gd")' in source
    assert 'const MapTooltipLayer = preload("res://scenes/map_tooltip_layer.gd")' in source
    assert "connection_layer = MapConnectionLayer.new()" in source
    assert "tooltip_layer = MapTooltipLayer.new()" in source
    assert "connection_layer = Node2D.new()" not in source


def test_renderer_base_isolates_map_world_in_subviewport_camera():
    source = _read(BASE_GD)
    for snippet in [
        "viewport_background = ColorRect.new()",
        'viewport_background.name = "ViewportBackground"',
        "viewport_background.color = MAP_BACKGROUND_COLOR",
        "map_viewport_container = SubViewportContainer.new()",
        'map_viewport_container.name = "MapViewportContainer"',
        "map_viewport_container.stretch = true",
        "map_viewport = SubViewport.new()",
        'map_viewport.name = "MapViewport"',
        "map_root = Node2D.new()",
        'map_root.name = "MapRoot"',
        "map_camera = Camera2D.new()",
        'map_camera.name = "MapCamera"',
        "map_camera.enabled = true",
        "map_root.add_child(map_camera)",
        "map_root.add_child(world_layer)",
    ]:
        assert snippet in source, f"Missing viewport/camera cutover snippet: {snippet}"


def test_camera_cutover_replaces_manual_world_transform():
    source = _read(BASE_GD)
    assert "var pan_offset: Vector2" not in source
    assert "var is_zooming: bool" not in source
    assert "world_layer.position = pan_offset" not in source
    assert "world_layer.scale = Vector2(zoom_level, zoom_level)" not in source
    assert "const MAP_BACKGROUND_COLOR := Color(0.12, 0.13, 0.14, 1.0)" in source
    assert "const INITIAL_CAMERA_OVERSCAN: float = 1.18" in source
    assert "var max_zoom: float = 4.0" in source
    assert "map_camera.zoom = Vector2(_zoom_level, _zoom_level)" in source
    assert "map_camera.position = _clamp_camera_position(target)" in source
    assert "func focus_on_region(region_name: String):" in source


def test_renderer_base_loads_placeholder_province_definition_and_textures():
    source = _read(BASE_GD)
    assert "func _get_map_asset_definition_path() -> String:" in source
    assert "func _get_active_region_positions() -> Dictionary:" in source
    assert 'positions[region_name] = province_shapes[region_name].get("center", Vector2.ZERO)' in source
    assert "province_definition = _load_province_definition()" in source
    assert "var parsed = JSON.parse_string(file.get_as_text())" in source
    assert "FileAccess.file_exists(definition_path)" in source
    assert "province_lookup_image = color_map" in source
    assert "visual_map_texture = ImageTexture.create_from_image(visual_image)" in source
    assert "highlight_map_texture = ImageTexture.create_from_image(highlight_image)" in source
    assert "var positions = _get_active_region_positions()" in source
    assert "for region_name in _get_active_region_positions():" in source
    assert "if not _get_active_region_positions().has(region_name):" in source


def test_renderer_base_preserves_update_all_regions_contract():
    source = _read(BASE_GD)
    assert "func update_all_regions(map_data: Dictionary):" in source
    # §4.1 introduced a wired/interactive gate: region_full_data now holds the
    # wired subset of map_data so unwired provinces can still render but never
    # populate gameplay state.
    assert "region_full_data = wired_data" in source
    assert "_refresh_all_region_visuals()" in source
    assert "_rebuild_dynamic_nodes()" in source
    update_body = _func_body(source, "func update_all_regions(map_data: Dictionary):")
    assert "queue_redraw()" in update_body
    assert "wired" in update_body, "update_all_regions must gate on the wired flag"


def test_update_all_regions_erases_unwired_regions_from_all_gameplay_dicts():
    source = _read(BASE_GD)
    update_body = _func_body(source, "func update_all_regions(map_data: Dictionary):")
    assert "var wired_data := {}" in update_body
    assert 'if province_shapes.has(region_name) and not bool(province_shapes[region_name].get("wired", true)):' in update_body
    for snippet in [
        "region_controllers.erase(region_name)",
        "region_visibility.erase(region_name)",
        "region_marshals.erase(region_name)",
        "region_fogged_forces.erase(region_name)",
        "region_garrisons.erase(region_name)",
    ]:
        assert snippet in update_body, f"Missing unwired erase in update_all_regions: {snippet}"
    assert "continue" in update_body
    assert "wired_data[region_name] = map_data[region_name]" in update_body
    assert "region_full_data = wired_data" in update_body


def test_update_region_short_circuits_before_writing_unwired_regions():
    source = _read(BASE_GD)
    update_body = _func_body(
        source,
        "func update_region(region_name: String, controller: String, marshal_data = null):",
    )
    wired_guard = 'if province_shapes.has(region_name) and not bool(province_shapes[region_name].get("wired", true)):'
    assert wired_guard in update_body
    guard_index = update_body.index(wired_guard)
    return_index = update_body.index("return", guard_index)
    controller_write_index = update_body.index("region_controllers[region_name] = controller")
    assert return_index < controller_write_index


def test_update_region_accepts_legacy_and_new_payload_shapes():
    source = _read(BASE_GD)
    assert "func update_region(region_name: String, controller: String, marshal_data = null):" in source
    assert "marshal_data is Array" in source
    assert "marshal_data is Dictionary" in source
    assert 'marshal_data is String and marshal_data != ""' in source


def test_garrison_badge_sizes_to_text():
    source = _read(BASE_GD)
    assert "font.get_string_size(label_text" in source
    assert "panel_width = max(GARRISON_SIZE.x" in source
    assert "label.position = Vector2.ZERO" in source
    assert "panel.add_child(label)" in source


def test_tooltip_drawing_delegates_to_overlay_layer():
    source = _read(BASE_GD)
    overlay = _read(TOOLTIP_GD)
    assert "tooltip_layer.show_tooltip(lines, width, panel_color, border_color, mouse_position)" in source
    assert "tooltip_layer.clear_tooltip()" in source
    assert "func show_tooltip(" in overlay
    assert "func clear_tooltip()" in overlay


def test_renderer_base_declares_bitmap_loader_hooks():
    """§4.2: the base exposes subclass hooks for artist-delivered bitmap paths.

    Both hooks default to "" so the placeholder scene keeps falling back to
    generated circle geometry without any subclass opt-out work.
    """
    source = _read(BASE_GD)
    assert "func _get_map_visual_bitmap_path() -> String:" in source
    assert "func _get_map_lookup_bitmap_path() -> String:" in source
    visual_hook_body = _func_body(source, "func _get_map_visual_bitmap_path() -> String:")
    lookup_hook_body = _func_body(source, "func _get_map_lookup_bitmap_path() -> String:")
    assert 'return ""' in visual_hook_body
    assert 'return ""' in lookup_hook_body


def test_renderer_base_declares_load_map_images():
    """§4.2: base has a bitmap loader that guards file-exists + load + size match."""
    source = _read(BASE_GD)
    assert "func _load_map_images() -> bool:" in source
    body = _func_body(source, "func _load_map_images() -> bool:")
    # Empty path → skip (no subclass bitmap opt-in).
    assert 'if visual_path == "" or lookup_path == "":' in body
    # Imported res:// textures are loaded through the resource pipeline, not
    # Image.load(), so exported builds keep working.
    assert 'var visual_image = _load_bitmap_texture_image(visual_path, "visual")' in body
    assert 'var lookup_image = _load_bitmap_texture_image(lookup_path, "lookup")' in body
    # Visual and lookup bitmaps must agree on size — §4.3 will deepen this
    # into a full asset validator; §4.2 just guards the obvious mismatch.
    assert "visual_image.get_size() != lookup_image.get_size()" in body
    assert "_validate_lookup_bitmap_image(lookup_image, lookup_path)" in body
    # On success the loader wires the visual texture + lookup image and
    # aligns the canvas to the bitmap dimensions.
    assert "province_lookup_image = lookup_image" in body
    assert "visual_map_texture = ImageTexture.create_from_image(visual_image)" in body
    assert "map_origin = Vector2.ZERO" in body
    assert "map_canvas_size = Vector2(visual_image.get_size())" in body
    # Explicit success/failure return values — the caller branches on this.
    assert "return true" in body
    assert "return false" in body


def test_renderer_base_loads_bitmap_resources_via_texture_pipeline():
    source = _read(BASE_GD)
    body = _func_body(source, "func _load_bitmap_texture_image(resource_path: String, label: String) -> Image:")
    assert "ResourceLoader.exists(resource_path)" in body
    assert "var resource = ResourceLoader.load(resource_path)" in body
    assert "var texture := resource as Texture2D" in body
    assert "var image := texture.get_image()" in body
    assert "FileAccess.file_exists" not in body
    assert "Image.new()" not in body


def test_renderer_base_validates_lookup_colors_and_latches_failures():
    source = _read(BASE_GD)
    assert "static var _bitmap_load_error_latch := {}" in source
    validate_body = _func_body(
        source,
        "func _validate_lookup_bitmap_image(lookup_image: Image, lookup_path: String) -> bool:",
    )
    assert "var no_province_key = _color_to_key(NO_PROVINCE_COLOR)" in validate_body
    assert "province_color_lookup.has(pixel_key)" in validate_body
    assert "seen_region_keys[pixel_key] = true" in validate_body
    assert "Map lookup bitmap has unmapped province color" in validate_body
    assert "Map lookup bitmap is missing province color" in validate_body
    error_body = _func_body(source, "func _report_bitmap_load_error_once(message: String) -> void:")
    assert "_bitmap_load_error_latch.has(message)" in error_body
    assert "_bitmap_load_error_latch[message] = true" in error_body
    assert "push_error(message)" in error_body


def test_build_map_textures_tries_bitmap_loader_before_circle_fallback():
    """§4.2: bitmap mode must win over generated circles when both paths are set.

    The loader must be invoked FROM WITHIN _build_map_textures BEFORE the
    circle-generation block so that a successful bitmap load short-circuits
    the fallback instead of being overwritten.
    """
    source = _read(BASE_GD)
    body = _func_body(source, "func _build_map_textures():")
    loader_index = body.index("_load_map_images()")
    # Circle generation is identified by the per-shape draw calls that only
    # appear inside the fallback path.
    circle_fill_index = body.index("_draw_circle_on_image(visual_image")
    assert loader_index < circle_fill_index, (
        "_load_map_images() must run before circle generation so a successful "
        "bitmap load short-circuits the fallback."
    )
    # The early-return on successful bitmap load is what enforces the skip.
    assert "if _load_map_images():" in body
    assert_return_after_loader = body[body.index("if _load_map_images():"):]
    assert "return" in assert_return_after_loader.split("\n")[1]


def test_hover_and_click_lookup_use_color_map_sampling_before_fallback():
    source = _read(BASE_GD)
    assert "func _lookup_region_from_color_map(map_position: Vector2) -> String:" in source
    assert "var pixel = province_lookup_image.get_pixel(pixel_x, pixel_y)" in source
    assert "return map_viewport.canvas_transform.affine_inverse() * local_pos" in source
    assert "var target_position = map_point_before - (local_point - viewport_center) / new_zoom" in source
    assert "var color_map_region = _lookup_region_from_color_map(map_mouse)" in source
    assert "_set_hovered_region(color_map_region)" in source
    assert "var clicked_region = _lookup_region_from_color_map(_screen_to_map_position(event.position))" in source
    assert "region_clicked.emit(clicked_region)" in source


def test_hover_distance_fallback_skips_noninteractive_regions():
    source = _read(BASE_GD)
    hover_body = _func_body(source, "func _refresh_hover_state():")
    interactive_guard = 'if province_shapes.has(region_name) and not bool(province_shapes[region_name].get("interactive", true)):'
    assert interactive_guard in hover_body
    guard_index = hover_body.index(interactive_guard)
    continue_index = hover_body.index("continue", guard_index)
    distance_index = hover_body.index("map_mouse.distance_to(positions[region_name]) <= REGION_RADIUS")
    assert continue_index < distance_index


def test_camera_cutover_has_keyboard_pan_and_zoom_fallbacks():
    source = _read(BASE_GD)
    assert 'if pan_keys_pressed["left"]:' in source
    assert 'if pan_keys_pressed["right"]:' in source
    assert 'if pan_keys_pressed["up"]:' in source
    assert 'if pan_keys_pressed["down"]:' in source
    assert "get_viewport().gui_release_focus()" in source
    assert "func _input(event):" in source
    assert "func _handle_pan_key_event(event: InputEventKey):" in source
    assert "func _clear_pan_key_state():" in source
    assert "func _clear_hover_state():" in source
    assert "func _should_handle_map_pointer_event(event) -> bool:" in source
    assert "func _unhandled_input(event):" in source
    assert "KEY_EQUAL, KEY_KP_ADD:" in source
    assert "KEY_MINUS, KEY_KP_SUBTRACT:" in source
    assert "KEY_HOME:" in source
    assert 'pan_keys_pressed["left"] = event.pressed' in source
    assert 'pan_keys_pressed["right"] = event.pressed' in source
    assert 'pan_keys_pressed["up"] = event.pressed' in source
    assert 'pan_keys_pressed["down"] = event.pressed' in source


def test_camera_cutover_sets_initial_zoom_and_reverses_wheel_mapping():
    source = _read(BASE_GD)
    assert "_set_camera_zoom_level(_get_initial_zoom_level())" in source
    assert "func _get_initial_zoom_level() -> float:" in source
    assert "var fit_ratio = min(width_ratio, height_ratio)" in source
    assert "return clamp(fit_ratio / INITIAL_CAMERA_OVERSCAN, min_zoom, max_zoom)" in source
    assert "_zoom_at_point(event.position, 1.0 - ZOOM_SPEED)" in source
    assert "_zoom_at_point(event.position, 1.0 + ZOOM_SPEED)" in source

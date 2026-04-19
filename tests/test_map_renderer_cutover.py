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


def test_renderer_declares_unwired_grey_overlay_constants():
    """§4.4: the renderer pins a single grey-tint color and blend factor so
    unwired regions look uniform across the bitmap and circle-fallback paths.
    The tooltip palette constants pin the warm-sepia treatment that keeps the
    unwired tooltip visually unmistakable next to the cold blue-grey fogged
    tooltip (audit 2026-04-19).
    """
    source = _read(BASE_GD)
    assert "const UNWIRED_GREY_COLOR := Color(0.32, 0.32, 0.34, 1.0)" in source
    assert "const UNWIRED_GREY_BLEND: float = 0.7" in source
    assert 'const UNWIRED_TOOLTIP_SUFFIX := "(not yet in play)"' in source
    # Warm-sepia tooltip palette — must differ meaningfully from the fogged
    # tooltip's cold blue-grey panel/border so the two states are instantly
    # distinguishable.
    assert "const UNWIRED_TOOLTIP_PANEL := Color(0.14, 0.11, 0.08, 0.95)" in source
    assert "const UNWIRED_TOOLTIP_BORDER := Color(0.55, 0.42, 0.28, 0.9)" in source
    assert "const UNWIRED_TOOLTIP_TITLE_COLOR := Color(0.82, 0.72, 0.55)" in source
    assert "const UNWIRED_TOOLTIP_SUFFIX_COLOR := Color(0.72, 0.58, 0.38)" in source


def test_unwired_tooltip_palette_distinct_from_fogged():
    """§4.4: the unwired panel/border must not collapse back to the cold
    blue-grey fogged palette. This test compares the declared channels so a
    future edit can't silently drift them to near-identical values (the
    pre-audit panels only differed by 0.02 on one channel).
    """
    import re

    source = _read(BASE_GD)

    def _find_color(const_name: str) -> tuple[float, ...]:
        # Match `const <name> := Color(r, g, b[, a])` with decimal channels.
        pattern = (
            rf"const\s+{re.escape(const_name)}\s*:=\s*Color\("
            r"([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)(?:,\s*([0-9.]+))?\)"
        )
        match = re.search(pattern, source)
        assert match is not None, f"missing or malformed constant: {const_name}"
        parts = [p for p in match.groups() if p is not None]
        return tuple(float(v) for v in parts)

    unwired_panel = _find_color("UNWIRED_TOOLTIP_PANEL")
    unwired_border = _find_color("UNWIRED_TOOLTIP_BORDER")

    # Warm-sepia panel: red channel must dominate over blue (cold-panel would
    # have blue >= red). Keep this constraint tight enough to prevent drift.
    assert unwired_panel[0] > unwired_panel[2] + 0.03, (
        f"unwired panel must read warm (R > B by > 0.03), got {unwired_panel}"
    )
    assert unwired_border[0] > unwired_border[2] + 0.2, (
        f"unwired border must read warm (R > B by > 0.2), got {unwired_border}"
    )


def test_renderer_exposes_is_region_wired_helper():
    source = _read(BASE_GD)
    assert "func _is_region_wired(region_name: String) -> bool:" in source
    body = _func_body(source, "func _is_region_wired(region_name: String) -> bool:")
    # Regions missing from province_shapes default to wired so legacy call
    # sites (no registry loaded) keep their existing behavior.
    assert "if not province_shapes.has(region_name):" in body
    assert "return true" in body
    assert 'return bool(province_shapes[region_name].get("wired", true))' in body


def test_renderer_defines_unwired_overlay_function():
    """§4.4: the overlay helper is declared and stamps grey over any lookup
    pixel belonging to an unwired province. The early-return on empty set
    keeps the placeholder (all-wired) path zero-cost.
    """
    source = _read(BASE_GD)
    assert (
        "func _apply_unwired_grey_overlay(visual_image: Image, lookup_image: Image) -> void:"
        in source
    )
    body = _func_body(
        source,
        "func _apply_unwired_grey_overlay(visual_image: Image, lookup_image: Image) -> void:",
    )
    assert "if visual_image == null or lookup_image == null:" in body
    assert "var unwired_keys := _unwired_lookup_keys()" in body
    assert "if unwired_keys.is_empty():" in body
    assert "if visual_image.get_size() != lookup_image.get_size():" in body
    assert "lookup_image.get_pixel(x, y)" in body
    assert "base.lerp(UNWIRED_GREY_COLOR, UNWIRED_GREY_BLEND)" in body
    assert "visual_image.set_pixel(x, y, tinted)" in body


def test_renderer_defines_unwired_lookup_keys_helper():
    source = _read(BASE_GD)
    assert "func _unwired_lookup_keys() -> Dictionary:" in source
    body = _func_body(source, "func _unwired_lookup_keys() -> Dictionary:")
    assert "for color_key in province_color_lookup.keys():" in body
    assert "var region_name = province_color_lookup[color_key]" in body
    assert "if not _is_region_wired(region_name):" in body
    assert "keys[color_key] = true" in body


def test_build_map_textures_applies_unwired_overlay_in_circle_fallback():
    """§4.4: after the circle fallback populates visual_image, the grey
    overlay must run BEFORE the texture is created so unwired pixels are
    tinted in the final texture.
    """
    source = _read(BASE_GD)
    body = _func_body(source, "func _build_map_textures():")
    overlay_index = body.index("_apply_unwired_grey_overlay(visual_image, color_map)")
    texture_index = body.index("visual_map_texture = ImageTexture.create_from_image(visual_image)")
    assert overlay_index < texture_index, (
        "grey overlay must run before texture creation in circle fallback"
    )


def test_load_map_images_applies_unwired_overlay_before_texture():
    """§4.4: the bitmap path must also pass visual_image through the overlay
    BEFORE converting it to a texture so unwired regions of commissioned art
    render grey.
    """
    source = _read(BASE_GD)
    body = _func_body(source, "func _load_map_images() -> bool:")
    overlay_index = body.index("_apply_unwired_grey_overlay(visual_image, lookup_image)")
    texture_index = body.index("visual_map_texture = ImageTexture.create_from_image(visual_image)")
    assert overlay_index < texture_index, (
        "grey overlay must run before texture creation in bitmap path"
    )
    # The overlay must sit AFTER province_lookup_image is assigned so
    # _unwired_lookup_keys() has the registry-backed keys populated.
    lookup_assign_index = body.index("province_lookup_image = lookup_image")
    assert lookup_assign_index < overlay_index


def test_click_handler_gates_emit_on_wired_flag():
    """§4.4: clicking an unwired province must NOT emit region_clicked.

    The guard lives inside the MOUSE_BUTTON_LEFT branch, AFTER resolving the
    clicked_region (via color-map lookup or hover fallback) but BEFORE the
    region_clicked.emit() call.
    """
    source = _read(BASE_GD)
    # Extract the button-press block so we can reason about order within it.
    left_click_anchor = "elif event.button_index == MOUSE_BUTTON_LEFT:"
    assert left_click_anchor in source
    post_left = source.split(left_click_anchor, 1)[1]
    # Stop at the next elif/else at the same indent, which in this file is the
    # button-release branch.
    click_block = post_left.split("if event is InputEventMouseButton and not event.pressed", 1)[0]
    guard = "if not _is_region_wired(clicked_region):"
    emit = "region_clicked.emit(clicked_region)"
    assert guard in click_block, "click handler must gate on _is_region_wired()"
    assert emit in click_block
    assert click_block.index(guard) < click_block.index(emit), (
        "wired guard must precede region_clicked.emit"
    )


def test_draw_routes_unwired_regions_to_placeholder_tooltip():
    """§4.4: _draw() must check the wired flag BEFORE region_full_data.has(),
    because update_all_regions() deliberately excludes unwired regions from
    region_full_data — the standard tooltip would render nothing otherwise.
    """
    source = _read(BASE_GD)
    body = _func_body(source, "func _draw():")
    unwired_branch = 'elif hovered_region != "" and not _is_region_wired(hovered_region):'
    wired_branch = 'elif hovered_region != "" and region_full_data.has(hovered_region):'
    assert unwired_branch in body
    assert wired_branch in body
    assert body.index(unwired_branch) < body.index(wired_branch), (
        "unwired branch must be evaluated before the wired-region branch"
    )
    assert "_draw_unwired_region_tooltip()" in body


def test_unwired_region_tooltip_renders_name_and_suffix():
    source = _read(BASE_GD)
    assert "func _draw_unwired_region_tooltip():" in source
    body = _func_body(source, "func _draw_unwired_region_tooltip():")
    assert "_push_tooltip_line(lines, hovered_region" in body
    assert "_push_tooltip_line(lines, UNWIRED_TOOLTIP_SUFFIX" in body
    assert "_draw_tooltip_lines(lines" in body
    # The tooltip must route through the named warm-sepia palette constants,
    # not open-coded colors — the latter is how the panel drifted back toward
    # the fogged-tooltip palette before the 2026-04-19 audit fix.
    assert "UNWIRED_TOOLTIP_TITLE_COLOR" in body
    assert "UNWIRED_TOOLTIP_SUFFIX_COLOR" in body
    assert "UNWIRED_TOOLTIP_PANEL" in body
    assert "UNWIRED_TOOLTIP_BORDER" in body


def test_lookup_region_from_color_map_still_returns_unwired_regions():
    """§4.4: the color-map hit-test must keep returning unwired region names
    so hover can identify them. Only `interactive` gates the lookup; `wired`
    is enforced at the click/tooltip layer, not here.
    """
    source = _read(BASE_GD)
    body = _func_body(source, "func _lookup_region_from_color_map(map_position: Vector2) -> String:")
    # The existing interactive gate stays — unwired provinces with
    # interactive=true (the §4.4 default) still produce hover hits.
    assert (
        'if province_shapes.has(region_name) and not bool(province_shapes[region_name].get("interactive", true)):'
        in body
    )
    # Must NOT short-circuit on wired here; unwired provinces need to hover.
    assert "_is_region_wired" not in body
    assert '"wired"' not in body

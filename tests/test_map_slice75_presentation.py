"""Map Slice 7.5 — presentation pass (DEF-9 / DEF-10 / DEF-11 / DEF-12 toggle).

First wide-window playtest feedback (July 2, 2026), root-caused and fixed:

- DEF-9  camera/void: Camera2D hardware limits fought (and beat) the script's
  centered letterbox clamp, pinning the map top-right with the whole fit
  deficit as one black band; INITIAL_CAMERA_OVERSCAN 1.18 + hard min_zoom 0.5
  guaranteed out-of-map void at boot; the yellow debug overlay shipped to
  players. Fixes: fit-floored min_zoom, contain-fit boot zoom, wide-open
  hardware limits, parchment letterbox, debug overlay deleted.
- DEF-10 owner-color legibility: the 20-nation palette re-authored as a SET
  (measured on the shipped art: min pairwise blended deltaE 4.5 -> 14.4);
  fog hue lerp scaled (FOG_HUE_LERP_SCALE) so the turn-1 map keeps national
  hues; COLOR_ENEMY_DEFAULT moved to artificial magenta; an in-shader
  province border pass survives the fill.
- DEF-11 labels: zoom-LOD map labels (nation names zoomed out at weighted
  centroids, province names zoomed in at the registry label_anchor) —
  supersedes the Slice-7 "no persistent labels" decision of record
  (user-blessed July 2, 2026).
- DEF-12 cheap tier: M cycles blended/political/terrain on the single
  fill_strength uniform (the full map-mode system stays future-spec-owned).

Style mirrors the sibling renderer suites: source-level pins on the .gd files
plus Python perceptual mirrors of the exact shader blend.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_SCENES_DIR = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes"
BASE_GD = GODOT_SCENES_DIR / "map_renderer_base.gd"
LABEL_GD = GODOT_SCENES_DIR / "map_label_layer.gd"
UTILS_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scripts" / "utils.gd"

# Land-terrain mean of europe_visual.png under the europe_lookup.png land mask
# (measured July 2, 2026; re-derive with the palette measurement script if the
# art redelivers). The perceptual floors below blend against this constant so
# the test runs without decoding the PNGs.
LAND_TERRAIN_MEAN = (0.708, 0.616, 0.453)
FOG_UNKNOWN_RGB = (0.02, 0.02, 0.05)
FOG_UNKNOWN_ALPHA = 0.75

# Floors (measured mins: blended 13.7 incl. Neutral / fog-unknown 8.2 /
# fallback 40.6 — asserted with headroom so art-driven drift, not noise,
# trips them).
BLENDED_DELTA_E_FLOOR = 12.0
FOG_DELTA_E_FLOOR = 7.0
FALLBACK_DELTA_E_FLOOR = 30.0


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _func_body(source: str, signature: str) -> str:
    return source.split(signature, 1)[1].split("\nfunc ", 1)[0]


def _parse_nation_colors() -> dict[str, tuple[float, float, float]]:
    source = _read(UTILS_GD)
    block = source.split("const NATION_COLORS = {", 1)[1].split("\n}", 1)[0]
    colors = {}
    for name, r, g, b in re.findall(
        r'"([A-Za-z]+)":\s*Color\(([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)\)', block
    ):
        colors[name] = (float(r), float(g), float(b))
    # Review fold: the regex only matches 3-arg Color entries. A 4-arg alpha
    # edit would silently drop that nation from every floor test below —
    # 'Neutral' especially has no other backstop (it is not a
    # starting_controller). Keep entries 3-arg, or extend the regex.
    assert len(colors) >= 21, (
        f"parsed only {len(colors)} NATION_COLORS entries — a non-3-arg "
        f"Color entry silently escaped the perceptual floor gates"
    )
    return colors


def _parse_enemy_default() -> tuple[float, float, float]:
    match = re.search(
        r"const COLOR_ENEMY_DEFAULT = Color\(([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)\)",
        _read(UTILS_GD),
    )
    assert match
    return (float(match.group(1)), float(match.group(2)), float(match.group(3)))


def _parse_fill_strength() -> float:
    match = re.search(
        r"const OWNER_FILL_STRENGTH: float = ([0-9.]+)", _read(BASE_GD)
    )
    assert match
    return float(match.group(1))


def _parse_fog_hue_scale() -> float:
    match = re.search(
        r"const FOG_HUE_LERP_SCALE: float = ([0-9.]+)", _read(BASE_GD)
    )
    assert match
    return float(match.group(1))


def _srgb_to_lab(rgb):
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def _delta_e(a, b) -> float:
    la, lb = _srgb_to_lab(a), _srgb_to_lab(b)
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(la, lb)))


def _mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def _blend_over_terrain(owner, fill):
    """Mirror of the shader output over the art: (1-fill)*terrain + fill*owner."""
    return _mix(LAND_TERRAIN_MEAN, owner, fill)


# ═══════════════════════════════════════════════════════════════════════════
# DEF-9 — camera void + debug overlay
# ═══════════════════════════════════════════════════════════════════════════


def test_camera_hardware_limits_disabled():
    """The old map-rect hardware limits fought _clamp_camera_position()'s
    centering (Godot's limit clamps run left->right / bottom->top, last write
    wins) and pinned the view top-right — the whole letterbox deficit landed
    as ONE void band on the left. The script clamp is the single authority."""
    source = _read(BASE_GD)
    assert "const CAMERA_LIMIT_DISABLED: int = 10000000" in source
    body = _func_body(source, "func _update_camera_limits():")
    assert "map_camera.limit_left = -CAMERA_LIMIT_DISABLED" in body
    assert "map_camera.limit_top = -CAMERA_LIMIT_DISABLED" in body
    assert "map_camera.limit_right = CAMERA_LIMIT_DISABLED" in body
    assert "map_camera.limit_bottom = CAMERA_LIMIT_DISABLED" in body
    assert "int(floor(world_bounds.position.x))" not in body, (
        "map-rect hardware limits must not return — they override the "
        "centered letterbox"
    )
    # The script clamp still centers each axis when the map is smaller than
    # the view — that behavior is what the hardware limits were breaking.
    clamp_body = _func_body(source, "func _clamp_camera_position(target: Vector2) -> Vector2:")
    assert "world_bounds.position.x + world_bounds.size.x / 2.0" in clamp_body
    assert "world_bounds.position.y + world_bounds.size.y / 2.0" in clamp_body


def test_zoom_floor_is_contain_fit():
    """min_zoom floors at the contain-fit ratio (recomputed per resize) — the
    view can never be zoomed out past the whole-map view into void."""
    source = _read(BASE_GD)
    assert "func _get_fit_zoom_level() -> float:" in source
    floor_body = _func_body(source, "func _update_zoom_floor():")
    assert "min_zoom = clampf(_get_fit_zoom_level(), 0.05, max_zoom)" in floor_body
    assert "_set_camera_zoom_level(min_zoom)" in floor_body
    resized_body = _func_body(source, "func _on_map_area_resized():")
    assert "_update_zoom_floor()" in resized_body
    assert resized_body.index("_update_zoom_floor()") < resized_body.index(
        "_update_camera_limits()"
    ), "the floor must be re-established before the camera re-clamps"


def test_initial_zoom_is_contain_fit_without_overscan():
    source = _read(BASE_GD)
    assert "INITIAL_CAMERA_OVERSCAN" not in source, (
        "the 1.18 overscan guaranteed out-of-map void at boot on every aspect"
    )
    body = _func_body(source, "func _get_initial_zoom_level() -> float:")
    assert "return clamp(_get_fit_zoom_level(), min_zoom, max_zoom)" in body


def test_debug_overlay_removed():
    """The always-on yellow coordinate overlay was dev scaffolding visible to
    every player — it must not return without a debug-build gate."""
    source = _read(BASE_GD)
    for token in ["_create_debug_label", "_update_debug_label", "DebugLabel", "_debug_label"]:
        assert token not in source, f"player-visible debug overlay resurfaced: {token}"


def test_letterbox_background_is_parchment_in_bitmap_mode():
    """Residual contain-fit letterbox must read as the map sheet (parchment
    sampled from the art edge), not a void; the legacy circle map keeps the
    dark canvas."""
    source = _read(BASE_GD)
    assert "const BITMAP_LETTERBOX_COLOR := Color(0.6, 0.49, 0.353, 1.0)" in source
    body = _func_body(source, "func _create_scene_layers():")
    base_idx = body.index("viewport_background.color = MAP_BACKGROUND_COLOR")
    bitmap_idx = body.index("viewport_background.color = BITMAP_LETTERBOX_COLOR")
    assert base_idx < bitmap_idx, "legacy default first, bitmap override second"
    guard_idx = body.index("if _bitmap_mode:")
    assert base_idx < guard_idx < bitmap_idx


# ═══════════════════════════════════════════════════════════════════════════
# DEF-10 — palette legibility, fog hue retention, borders, fallback
# ═══════════════════════════════════════════════════════════════════════════


def test_shader_border_pass_present_and_sea_safe():
    """Fragments whose lookup key differs from the right/down neighbor darken
    into a province border; sea neighbors are skipped so coastlines keep the
    painted art; the palette result line is untouched (owner-fill pins)."""
    source = _read(BASE_GD)
    shader = source.split('const OWNER_FILL_SHADER := """', 1)[1].split('"""', 1)[0]
    assert "uniform float border_strength" in shader
    assert "TEXTURE_PIXEL_SIZE.x" in shader and "TEXTURE_PIXEL_SIZE.y" in shader
    assert "right.r + right.g + right.b >= 0.002" in shader, "sea neighbor guard (right)"
    assert "down.r + down.g + down.b >= 0.002" in shader, "sea neighbor guard (down)"
    assert "result = vec4(owner_colors[i].rgb, owner_colors[i].a * fill_strength);" in shader
    # The border test is key comparison only — no second palette loop.
    assert shader.count("for (int i") == 1, "border pass must not rescan the palette"


def test_fog_hue_scale_is_a_retention_fraction():
    scale = _parse_fog_hue_scale()
    assert 0.0 < scale < 1.0


def test_palette_pairwise_floor_over_terrain():
    """The re-authored NATION_COLORS must stay pairwise distinguishable under
    the exact shader blend over the measured terrain mean. This is the DEF-10
    completion gate — any palette edit that re-clusters two nations fails
    here before a playtest has to catch it."""
    colors = _parse_nation_colors()
    fill = _parse_fill_strength()
    blended = {n: _blend_over_terrain(c, fill) for n, c in colors.items()}
    names = sorted(blended)
    worst = None
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = _delta_e(blended[a], blended[b])
            if worst is None or d < worst[0]:
                worst = (d, a, b)
    assert worst[0] >= BLENDED_DELTA_E_FLOOR, (
        f"nation colors {worst[1]} and {worst[2]} blend to deltaE "
        f"{worst[0]:.1f} over the terrain art (floor {BLENDED_DELTA_E_FLOOR}) "
        f"— re-author one of them (verify with the Slice 7.5 measurement "
        f"method before pinning)"
    )


def test_palette_pairwise_floor_under_unknown_fog():
    """Turn-1 reality: most provinces sit under fog. With the hue-retention
    scale the roster must stay distinguishable under the 'unknown' wash —
    this was the dominant cause of the original 'colors are confusing'."""
    colors = _parse_nation_colors()
    fill = _parse_fill_strength()
    scale = _parse_fog_hue_scale()
    fogged = {}
    for n, c in colors.items():
        washed = _mix(c, FOG_UNKNOWN_RGB, FOG_UNKNOWN_ALPHA * scale)
        fogged[n] = _blend_over_terrain(washed, fill)
    names = sorted(fogged)
    worst = None
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = _delta_e(fogged[a], fogged[b])
            if worst is None or d < worst[0]:
                worst = (d, a, b)
    assert worst[0] >= FOG_DELTA_E_FLOOR, (
        f"under unknown fog, {worst[1]} and {worst[2]} collapse to deltaE "
        f"{worst[0]:.1f} (floor {FOG_DELTA_E_FLOOR})"
    )


def test_chip_text_contrast_over_light_palette_entries():
    """Review fold: white chip text was illegible on the re-authored
    near-white PapalStates (and marginal on pale Bavaria / gold Austria).
    Every consumer drawing text over a raw NATION_COLORS fill must resolve
    its text color through Utils.contrast_text_color()."""
    utils_source = _read(UTILS_GD)
    assert "static func contrast_text_color(background: Color) -> Color:" in utils_source
    assert "background.get_luminance() > 0.62" in utils_source
    base_source = _read(BASE_GD)
    garrison_body = _func_body(
        base_source,
        "func _create_garrison_node(region_pos: Vector2, garrison_data: Dictionary, controller: String, visibility: String):",
    )
    assert "Utils.contrast_text_color(nation_color)" in garrison_body
    assert "var text_color = Color.WHITE" not in garrison_body
    # Python mirror of the luminance rule (Rec.709 coefficients, matching
    # Godot's Color.get_luminance) over the live palette: light entries take
    # dark text, saturated darks keep white.
    colors = _parse_nation_colors()

    def luminance(rgb):
        return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

    # Exemplars track the live palette (EU4-convention re-author, July 16,
    # 2026): Austria white / Bavaria pale blue / Hanover pale yellow / Spain
    # gold are the light entries; PapalStates moved to the dark (cardinal
    # purple) side.
    for light in ["Austria", "Bavaria", "Hanover", "Spain"]:
        assert luminance(colors[light]) > 0.62, (
            f"{light} expected on the dark-text side of the contrast rule"
        )
    for dark in ["France", "Britain", "Prussia", "Russia", "PapalStates"]:
        assert luminance(colors[dark]) <= 0.62, (
            f"{dark} expected to keep white chip text"
        )


def test_enemy_default_fallback_is_artificial_and_distant():
    """An unmapped controller must be a VISIBLE bug (magenta), not camouflage
    — the old muted red sat blended deltaE ~4 from Switzerland."""
    fallback = _parse_enemy_default()
    r, g, b = fallback
    assert r >= 0.8 and b >= 0.8 and g <= 0.15, (
        f"COLOR_ENEMY_DEFAULT {fallback} must stay obviously-artificial magenta"
    )
    colors = _parse_nation_colors()
    fill = _parse_fill_strength()
    fallback_blend = _blend_over_terrain(fallback, fill)
    for name, c in colors.items():
        d = _delta_e(fallback_blend, _blend_over_terrain(c, fill))
        assert d >= FALLBACK_DELTA_E_FLOOR, (
            f"fallback magenta is only deltaE {d:.1f} from {name} — an "
            f"unmapped controller would impersonate it"
        )


def test_art_layer_filters_smoothly_but_lookup_stays_exact():
    """July 2 zoom-feedback fold: the commissioned art upscales with a
    mipmapped linear filter (NEAREST was blocky zoomed in, shimmered
    minified); the legacy circle canvas keeps NEAREST. The owner-fill layer
    must stay NEAREST — filtering would blend province lookup keys at
    borders and break the shader's exact palette match."""
    source = _read(BASE_GD)
    body = _func_body(source, "func _create_scene_layers():")
    visual_idx = body.index("visual_map_layer.texture_filter = (")
    assert "CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS if _bitmap_mode" in body[visual_idx:]
    owner_body = _func_body(source, "func _create_owner_fill_layer():")
    assert "owner_fill_layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST" in owner_body
    loader_body = _func_body(source, "func _load_map_images() -> bool:")
    assert "visual_image.generate_mipmaps()" in loader_body
    # Zoom is capped at the art's useful limit — past ~2.5x the 2560x1600
    # sheet is pure upscaled pixels.
    assert "var max_zoom: float = 2.5" in source


def test_sea_link_lines_are_dashed_dark_ink():
    """July 2 user report: the sea-link lines blended into the sea art and
    read as artifacts. They now draw dashed in dark map-ink so they read as
    deliberate crossing routes on the chart."""
    connection_gd = GODOT_SCENES_DIR / "map_connection_layer.gd"
    source = _read(connection_gd)
    assert "draw_dashed_line(" in source, "sea links must draw dashed"
    assert "draw_line(start_pos, end_pos" not in source, "solid line must not return"
    dash = float(re.search(r"const DASH_LENGTH: float = ([0-9.]+)", source).group(1))
    assert dash > 0
    utils_source = _read(UTILS_GD)
    match = re.search(
        r"const COLOR_CONNECTION = Color\(([0-9.]+),\s*([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)\)",
        utils_source,
    )
    assert match, "COLOR_CONNECTION must carry an explicit alpha"
    r, g, b, a = (float(match.group(i)) for i in range(1, 5))
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    assert luminance < 0.35, (
        f"COLOR_CONNECTION luminance {luminance:.2f} — must stay dark ink, "
        f"the light grey vanished against the sea art"
    )
    assert 0.5 <= a <= 1.0
    # The Europe map must still resolve the line color through the single
    # source (also pinned by test_map_slice7_cutover's _get_colors check).
    map_gd = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map.gd"
    assert "Utils.COLOR_CONNECTION" in _read(map_gd)


# ═══════════════════════════════════════════════════════════════════════════
# DEF-11 — zoom-LOD map labels
# ═══════════════════════════════════════════════════════════════════════════


def test_label_layer_script_draws_two_lod_tiers():
    source = _read(LABEL_GD)
    assert "const PROVINCE_LABEL_MIN_ZOOM" in source
    assert "func set_labels(" in source
    assert "func set_zoom_level(" in source
    draw_body = _func_body(source, "func _draw():")
    # UI-2 Part 2: the tier switch keys off `logical_zoom` (= _zoom_level /
    # viewport-pixel-scale) so the LOD stays consistent on-screen once the map
    # SubViewport renders at physical resolution.
    assert "logical_zoom >= PROVINCE_LABEL_MIN_ZOOM" in draw_body
    assert "_province_labels" in draw_body and "_nation_labels" in draw_body
    tier_body = _func_body(
        source,
        "func _draw_label_tier(font: Font, labels: Array, xform: Transform2D, font_screen_px: float) -> void:",
    )
    assert "draw_string_outline(" in tier_body, "labels need an outline to read on the art"
    assert "draw_string(" in tier_body


def test_labels_are_screen_space_and_grow_with_zoom():
    """July 2 zoom-feedback fold: world-space labels rasterized blurry under
    camera zoom and read as 'shrinking' while the map grew. The layer is a
    screen-space overlay projecting WORLD anchors through the SubViewport
    canvas transform, with font sizes that GROW with zoom inside clamps."""
    source = _read(LABEL_GD)
    assert "_renderer.map_viewport.canvas_transform" in source
    draw_body = _func_body(source, "func _draw():")
    # UI-2 Part 2: font size grows with `logical_zoom` (scale-corrected zoom) so
    # labels stay the right on-screen size under content_scale_factor > 1.0.
    assert "clampf(PROVINCE_FONT_BASE * logical_zoom, PROVINCE_FONT_MIN, PROVINCE_FONT_MAX)" in draw_body
    assert "clampf(NATION_FONT_BASE * logical_zoom, NATION_FONT_MIN, NATION_FONT_MAX)" in draw_body
    # Growth clamps must be a real range (min < max) so labels neither
    # vanish nor explode.
    for tier in ["NATION", "PROVINCE"]:
        base = float(re.search(rf"const {tier}_FONT_BASE: float = ([0-9.]+)", source).group(1))
        lo = float(re.search(rf"const {tier}_FONT_MIN: float = ([0-9.]+)", source).group(1))
        hi = float(re.search(rf"const {tier}_FONT_MAX: float = ([0-9.]+)", source).group(1))
        assert 0 < lo < hi and base > 0
    tier_body = _func_body(
        source,
        "func _draw_label_tier(font: Font, labels: Array, xform: Transform2D, font_screen_px: float) -> void:",
    )
    assert "xform * Vector2(label.get(" in tier_body, "anchors project world -> screen each draw"
    assert "cull_rect" in tier_body, "offscreen labels must be culled"
    # Camera pans must re-project labels (zoom changes already redraw via
    # set_zoom_level).
    base_source = _read(BASE_GD)
    pos_body = _func_body(base_source, "func _set_camera_position(target: Vector2):")
    assert "map_label_layer.queue_redraw()" in pos_body
    # Label data is stored in WORLD coords — layer-space conversion would
    # double-offset under the projection.
    refresh_body = _func_body(base_source, "func _refresh_map_labels():")
    assert "_world_to_layer_position" not in refresh_body


def test_base_creates_label_layer_bitmap_gated():
    """Bitmap-art maps only: the legacy circle map draws its own per-region
    labels in _build_region_nodes — a second layer would double-draw them."""
    source = _read(BASE_GD)
    assert 'const MapLabelLayer = preload("res://scenes/map_label_layer.gd")' in source
    body = _func_body(source, "func _create_scene_layers():")
    reset_idx = body.index("map_label_layer = null")
    guard_idx = body.index("if _bitmap_mode:", reset_idx)
    create_idx = body.index("map_label_layer = MapLabelLayer.new()")
    assert reset_idx < guard_idx < create_idx
    assert "map_label_layer.setup(self)" in body, "the layer projects via the renderer's viewport"
    assert "map_label_layer.z_index = 50" in body, "labels sit under the tooltip layer (z 100)"
    assert "world_layer.add_child(map_label_layer)" not in body, (
        "screen-space overlay — never a world_layer (camera-scaled) child"
    )


def test_label_refresh_rides_the_update_paths():
    """Label data rebuilds exactly where the owner fill refreshes — labels
    reflect region_controllers (what the fill tints) and the registry's
    label_anchor (parsed since §4.1, unread until this slice)."""
    source = _read(BASE_GD)
    refresh_body = _func_body(source, "func _refresh_map_labels():")
    assert '"label_anchor"' in refresh_body
    assert "region_controllers" in refresh_body
    assert "Utils.display_nation_name" in refresh_body
    # G4 discipline: per-province work only, never per-pixel.
    for forbidden in ["get_pixel", "set_pixel", "for y in range", "for x in range"]:
        assert forbidden not in refresh_body
    # Null-guard first: the legacy circle map has no label layer.
    lines = [line.strip() for line in refresh_body.splitlines() if line.strip()]
    guard_idx = next(i for i, l in enumerate(lines) if l == "if map_label_layer == null:")
    assert lines[guard_idx + 1] == "return"
    for signature in [
        "func update_all_regions(map_data: Dictionary):",
        "func update_region(region_name: String, controller: String, marshal_data = null):",
        "func _build_static_map_visuals():",
    ]:
        assert "_refresh_map_labels()" in _func_body(source, signature), (
            f"{signature} must rebuild map labels"
        )


def test_zoom_changes_propagate_to_the_label_layer():
    source = _read(BASE_GD)
    body = _func_body(source, "func _set_camera_zoom_level(value: float):")
    assert "map_label_layer.set_zoom_level(_zoom_level)" in body


def test_nation_centroid_is_radius_weighted():
    """The nation tier sits at the radius^2-weighted centroid of owned
    provinces so big provinces anchor the name (naive for multi-blob nations
    — the accepted first pass per the DEF-11 row)."""
    source = _read(BASE_GD)
    body = _func_body(source, "func _refresh_map_labels():")
    assert "radius * radius" in body
    assert "label_pos * weight" in body
    # Python mirror of the weighting rule.
    provinces = [((0.0, 0.0), 10.0), ((100.0, 0.0), 20.0)]
    weight_total = sum(r * r for _, r in provinces)
    cx = sum(p[0] * r * r for p, r in provinces) / weight_total
    assert cx == 80.0, "the larger province must dominate the centroid"


def test_display_nation_names_cover_the_multiword_keys():
    source = _read(UTILS_GD)
    block = source.split("const NATION_DISPLAY_NAMES = {", 1)[1].split("\n}", 1)[0]
    for key, display in [
        ("Ottoman", "Ottoman Empire"),
        ("PapalStates", "Papal States"),
        ("KingdomOfItaly", "Kingdom of Italy"),
    ]:
        assert f'"{key}": "{display}"' in block, (
            f"raw internal key {key!r} would leak onto the map (R7)"
        )
    assert "static func display_nation_name(nation: String) -> String:" in source


# ═══════════════════════════════════════════════════════════════════════════
# DEF-12 cheap tier — fill-mode toggle
# ═══════════════════════════════════════════════════════════════════════════


def test_fill_mode_cycle_rides_the_single_uniform():
    source = _read(BASE_GD)
    assert 'const MAP_FILL_MODE_ORDER: Array = ["blended", "political", "terrain"]' in source
    strengths_block = source.split("const MAP_FILL_MODE_STRENGTHS := {", 1)[1].split("\n}", 1)[0]
    assert '"blended": OWNER_FILL_STRENGTH' in strengths_block
    political = float(re.search(r'"political": ([0-9.]+)', strengths_block).group(1))
    terrain = float(re.search(r'"terrain": ([0-9.]+)', strengths_block).group(1))
    fill = _parse_fill_strength()
    assert terrain < fill < political <= 1.0, (
        "modes must order terrain < blended < political"
    )
    apply_body = _func_body(source, "func _apply_map_fill_mode():")
    lines = [line.strip() for line in apply_body.splitlines() if line.strip()]
    guard_idx = lines.index("if owner_fill_layer == null:")
    assert lines[guard_idx + 1] == "return", "legacy circle map must no-op"
    assert apply_body.count("set_shader_parameter(") == 1, (
        "a mode switch is ONE uniform write — the G4 budget shape"
    )
    cycle_body = _func_body(source, "func cycle_map_fill_mode() -> String:")
    assert "_apply_map_fill_mode()" in cycle_body
    # Hotkey wiring.
    unhandled_body = _func_body(source, "func _unhandled_input(event):")
    assert "KEY_M:" in unhandled_body
    assert "cycle_map_fill_mode()" in unhandled_body

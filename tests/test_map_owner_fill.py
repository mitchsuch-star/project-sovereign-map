"""Map Slice 6 — province ownership fills (owner-tint via lookup mask).

The owner-fill pass runs inside Godot, so these tests follow the two
established renderer-suite styles:

- source-level guardrails (mirroring `test_map_renderer_cutover.py`): the
  shader/palette machinery must exist in `map_renderer_base.gd` with the
  exact contracts the slice pins — most importantly the G4 completion gate:
  an ownership change is ONE <=128-entry shader-palette uniform upload,
  never a per-pixel CPU pass;
- Python behavioral mirrors (mirroring `test_map_unwired_overlay.py`): the
  lookup color -> region -> owner color mapping is recomputed in Python
  against the real `europe.json` + `utils.gd` data so CI catches drift
  (a starting controller without a nation color, lookup colors that the
  shader epsilon could confuse, a palette rule regression).

The parse-harness coverage/staleness checks for the two scenes-dir scripts
also live here: `test_godot_parse_harness.py`'s staleness guard resolves its
list against `scripts/` only, so the scenes-dir renderer scripts own their
mirror checks locally (MAP_CRITICAL_SCRIPTS in `tools/godot_parse_check.gd`).
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_SCENES_DIR = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes"
BASE_GD = GODOT_SCENES_DIR / "map_renderer_base.gd"
EUROPE_GD = GODOT_SCENES_DIR / "europe_map.gd"
EUROPE_SMOKE_GD = GODOT_SCENES_DIR / "europe_map_smoke.gd"
UTILS_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scripts" / "utils.gd"
EUROPE_JSON = (
    REPO_ROOT
    / "godot-client"
    / "project-sovereign"
    / "assets"
    / "maps"
    / "europe.json"
)
HARNESS_PATH = REPO_ROOT / "tools" / "godot_parse_check.gd"
REPORT_PATH = REPO_ROOT / "tools" / "godot_parse_report.json"

MAP_CRITICAL_SCRIPTS = [
    "map_renderer_base.gd",
    "europe_map.gd",
    "europe_map_smoke.gd",
    "map.gd",
    "map_label_layer.gd",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _func_body(source: str, signature: str) -> str:
    return source.split(signature, 1)[1].split("\nfunc ", 1)[0]


def _load_europe_registry() -> dict:
    return json.loads(EUROPE_JSON.read_text(encoding="utf-8"))


def _parse_nation_colors() -> dict[str, tuple[float, float, float]]:
    """Extract Utils.NATION_COLORS entries (name -> rgb floats) from source."""
    source = _read(UTILS_GD)
    block = source.split("const NATION_COLORS = {", 1)[1].split("\n}", 1)[0]
    colors = {}
    for name, r, g, b in re.findall(
        r'"([A-Za-z]+)":\s*Color\(([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)\)', block
    ):
        colors[name] = (float(r), float(g), float(b))
    # Slice 7.5 review fold: 3-arg-only regex — a 4-arg alpha edit would
    # silently drop an entry from every mirror below. Keep entries 3-arg.
    assert len(colors) >= 21, (
        f"parsed only {len(colors)} NATION_COLORS entries — a non-3-arg "
        f"Color entry silently escaped the palette mirrors"
    )
    return colors


def _parse_enemy_default_color() -> tuple[float, float, float]:
    source = _read(UTILS_GD)
    match = re.search(
        r"const COLOR_ENEMY_DEFAULT = Color\(([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)\)",
        source,
    )
    assert match, "utils.gd must define COLOR_ENEMY_DEFAULT"
    return (float(match.group(1)), float(match.group(2)), float(match.group(3)))


def _parse_shader_epsilon() -> float:
    """The per-channel match tolerance the fragment shader compares against."""
    source = _read(BASE_GD)
    shader = _shader_block(source)
    match = re.search(r"vec3\(([0-9.]+)\)\)\)\)", shader)
    assert match, "owner-fill shader must compare against a vec3 epsilon"
    return float(match.group(1))


def _parse_max_provinces() -> int:
    source = _read(BASE_GD)
    match = re.search(r"const OWNER_FILL_MAX_PROVINCES: int = (\d+)", source)
    assert match, "map_renderer_base.gd must define OWNER_FILL_MAX_PROVINCES"
    return int(match.group(1))


def _shader_block(source: str) -> str:
    return source.split('const OWNER_FILL_SHADER := """', 1)[1].split('"""', 1)[0]


def _shader_channels_match(
    a: tuple[int, int, int], b: tuple[int, int, int], epsilon: float
) -> bool:
    """Python mirror of the shader's all(lessThan(abs(a - b), vec3(eps)))."""
    return all(abs(ca / 255.0 - cb / 255.0) < epsilon for ca, cb in zip(a, b))


def _build_palette_mirror(
    order: list[str],
    controllers: dict[str, str],
    wired: dict[str, bool],
    nation_colors: dict[str, tuple[float, float, float]],
    enemy_default: tuple[float, float, float],
) -> list[tuple[float, float, float, float]]:
    """Python mirror of `_refresh_owner_fill_palette`'s per-slot OWNER rules.

    - province absent from region_controllers -> transparent (no fill)
    - unwired province -> transparent (the §4.4 grey overlay owns its look)
    - known controller -> Utils.NATION_COLORS entry, opaque
    - unknown controller -> Utils.COLOR_ENEMY_DEFAULT, opaque

    The Slice-7 fog wash composites AFTER these rules (visibility "full" is a
    no-op, so every scenario here is fog-neutral); its mirror lives in
    tests/test_map_slice7_cutover.py.
    """
    palette = []
    for region_name in order:
        if region_name not in controllers or not wired.get(region_name, True):
            palette.append((0.0, 0.0, 0.0, 0.0))
            continue
        rgb = nation_colors.get(controllers[region_name], enemy_default)
        palette.append((rgb[0], rgb[1], rgb[2], 1.0))
    return palette


# ═══════════════════════════════════════════════════════════════════════════
# Source-level guardrails — map_renderer_base.gd
# ═══════════════════════════════════════════════════════════════════════════


def test_owner_fill_constants_and_shader_uniforms_present():
    source = _read(BASE_GD)
    assert "const OWNER_FILL_STRENGTH: float =" in source
    assert "const OWNER_FILL_MAX_PROVINCES: int = 128" in source
    shader = _shader_block(source)
    assert "shader_type canvas_item;" in shader
    for uniform in [
        "uniform int province_count",
        "uniform vec4 lookup_colors[128];",
        "uniform vec4 owner_colors[128];",
        "uniform float fill_strength",
    ]:
        assert uniform in shader, f"Missing owner-fill shader uniform: {uniform}"
    assert "result = vec4(owner_colors[i].rgb, owner_colors[i].a * fill_strength);" in shader


def test_owner_fill_shader_has_sea_early_out_before_palette_loop():
    """Sea ([0,0,0]) covers most of the bitmap; the early-out both bounds the
    per-fragment loop and guarantees a zeroed palette slot can never paint
    open water."""
    shader = _shader_block(_read(BASE_GD))
    sea_idx = shader.index("if (key.r + key.g + key.b < 0.002)")
    loop_idx = shader.index("for (int i = 0; i < province_count; i++)")
    assert sea_idx < loop_idx, "sea early-out must run before the palette loop"
    assert "COLOR = vec4(0.0);" in shader[:loop_idx]


def test_owner_fill_layer_created_after_visual_below_highlight():
    source = _read(BASE_GD)
    scene_body = _func_body(source, "func _create_scene_layers():")
    visual_idx = scene_body.index("world_layer.add_child(visual_map_layer)")
    owner_idx = scene_body.index("_create_owner_fill_layer()")
    highlight_idx = scene_body.index("highlight_map_layer = TextureRect.new()")
    assert visual_idx < owner_idx < highlight_idx, (
        "OwnerFillLayer must be added after the visual layer and before the "
        "highlight layer is created (same z_index=-2, later sibling draws "
        "above the art; highlight at -1 stays on top)"
    )
    layer_body = _func_body(source, "func _create_owner_fill_layer():")
    assert 'owner_fill_layer.name = "OwnerFillLayer"' in layer_body
    assert "owner_fill_layer.z_index = -2" in layer_body
    assert "owner_fill_layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST" in layer_body
    assert "owner_fill_layer.texture = ImageTexture.create_from_image(province_lookup_image)" in layer_body
    assert "shader.code = OWNER_FILL_SHADER" in layer_body


def test_owner_fill_layer_gated_on_bitmap_mode():
    """The legacy circle map keeps its per-region Panel fills — the owner
    layer must only exist when artist bitmaps loaded."""
    source = _read(BASE_GD)
    layer_body = _func_body(source, "func _create_owner_fill_layer():")
    guard_idx = layer_body.index("if not _bitmap_mode or province_lookup_image == null:")
    assert "return" in layer_body[guard_idx:].splitlines()[1], (
        "bitmap-mode guard must return before building the layer"
    )
    # The flag flips true only in the bitmap loader's success path...
    loader_body = _func_body(source, "func _load_map_images() -> bool:")
    assert "_bitmap_mode = true" in loader_body
    # ...and resets with the rest of the shape state for re-entrancy.
    shapes_body = _func_body(source, "func _build_province_shapes():")
    assert "_bitmap_mode = false" in shapes_body
    assert "_owner_fill_province_order = []" in shapes_body


def test_owner_fill_preserves_bitmap_loader_call_shape():
    """`_build_map_textures` must keep the pinned `if _load_map_images():` +
    immediate return shape (the flag is set INSIDE the loader, not by
    restructuring the caller)."""
    source = _read(BASE_GD)
    textures_body = _func_body(source, "func _build_map_textures():")
    load_idx = textures_body.index("if _load_map_images():")
    following = textures_body[load_idx:].splitlines()[1]
    assert "return" in following
    assert "_bitmap_mode = _load_map_images()" not in source


def test_palette_builders_share_the_province_order():
    """Index alignment between lookup_colors[i] and owner_colors[i] is the
    load-bearing invariant: both palettes must iterate
    _owner_fill_province_order."""
    source = _read(BASE_GD)
    layer_body = _func_body(source, "func _create_owner_fill_layer():")
    assert "_owner_fill_province_order.append(region_name)" in layer_body
    assert 'lookups[i] = province_shapes[_owner_fill_province_order[i]]["lookup_color"]' in layer_body
    refresh_body = _func_body(source, "func _refresh_owner_fill_palette():")
    assert "for i in range(_owner_fill_province_order.size()):" in refresh_body


def test_palette_arrays_upload_exactly_max_entries():
    """A short uniform-array upload leaves zeroed tail slots — both palettes
    must resize to OWNER_FILL_MAX_PROVINCES, and an over-capacity registry
    must be reported loudly."""
    source = _read(BASE_GD)
    layer_body = _func_body(source, "func _create_owner_fill_layer():")
    assert "lookups.resize(OWNER_FILL_MAX_PROVINCES)" in layer_body
    assert "if province_shapes.size() > OWNER_FILL_MAX_PROVINCES:" in layer_body
    assert "push_error(" in layer_body
    refresh_body = _func_body(source, "func _refresh_owner_fill_palette():")
    assert "owners.resize(OWNER_FILL_MAX_PROVINCES)" in refresh_body


def test_refresh_palette_is_g4_safe_no_per_pixel_work():
    """The G4 completion gate: an ownership change re-tints in <= one frame.
    The refresh path is a <=128-entry uniform upload — any per-pixel image
    work here is the explicitly forbidden path."""
    source = _read(BASE_GD)
    refresh_body = _func_body(source, "func _refresh_owner_fill_palette():")
    assert 'set_shader_parameter("owner_colors", owners)' in refresh_body
    for forbidden in ["get_pixel", "set_pixel", "for y in range", "for x in range"]:
        assert forbidden not in refresh_body, (
            f"_refresh_owner_fill_palette must never do per-pixel work "
            f"(found {forbidden!r}) — G4 requires a palette-uniform-only re-tint"
        )


def test_refresh_palette_no_ops_without_owner_layer():
    """The refresh hook runs on every legacy-game update_all_regions call in
    circle mode (no owner layer) — the early return is a hard contract."""
    source = _read(BASE_GD)
    refresh_body = _func_body(source, "func _refresh_owner_fill_palette():")
    lines = [line.strip() for line in refresh_body.splitlines() if line.strip()]
    guard_idx = lines.index("if owner_fill_layer == null:")
    assert lines[guard_idx + 1] == "return"


def test_update_paths_refresh_the_owner_palette():
    source = _read(BASE_GD)
    for signature in [
        "func update_all_regions(map_data: Dictionary):",
        "func update_region(region_name: String, controller: String, marshal_data = null):",
    ]:
        body = _func_body(source, signature)
        assert "_refresh_owner_fill_palette()" in body, (
            f"{signature} must refresh the owner palette after controllers change"
        )


def test_palette_reads_centralized_nation_colors():
    """Nation colors resolve through Utils.NATION_COLORS (§3.3 single source
    of truth) with the shared unknown-nation fallback; no fill without a
    known controller on a wired province."""
    source = _read(BASE_GD)
    refresh_body = _func_body(source, "func _refresh_owner_fill_palette():")
    assert "Utils.NATION_COLORS.get(controller, Utils.COLOR_ENEMY_DEFAULT)" in refresh_body
    assert "if region_controllers.has(region_name) and _is_region_wired(region_name):" in refresh_body
    assert "Color(0, 0, 0, 0)" in refresh_body


# ═══════════════════════════════════════════════════════════════════════════
# Source-level guardrails — europe_map.gd (shared Europe renderer) +
# europe_map_smoke.gd (the smoke-only subclass; Slice 7 split)
# ═══════════════════════════════════════════════════════════════════════════


def test_europe_map_rekeys_registry_by_historical_name():
    """The registry keys regions by Region_NNN ids; backend map_data is keyed
    by historical name (create_europe_regions() does the same re-key
    server-side). The shared Europe renderer must re-key at load so ownership
    data and hit-testing share one key scheme."""
    source = _read(EUROPE_GD)
    body = _func_body(source, "func _load_province_definition() -> Dictionary:")
    assert 'var region_name := str(row.get("name", region_id))' in body
    assert "renamed[region_name] = row" in body
    assert 'definition["regions"] = renamed' in body


def test_europe_map_seeds_ownership_through_update_all_regions():
    """The 1805 snapshot must flow through the SAME update_all_regions()
    entry point the live game uses — not by poking renderer state."""
    source = _read(EUROPE_SMOKE_GD)
    ready_body = _func_body(source, "func _ready():")
    assert "_seed_registry_ownership()" in ready_body
    seed_body = _func_body(source, "func _seed_registry_ownership():")
    assert '"controller": str(row.get("starting_controller", "Neutral")),' in seed_body
    assert "update_all_regions(_seeded_map_data)" in seed_body
    assert "region_controllers[" not in seed_body, (
        "seeding must go through update_all_regions, not direct state writes"
    )


def test_europe_map_click_cycle_keeps_tooltip_and_fill_in_sync():
    """The smoke G4 demo mutates the retained seed dict and re-sends the whole
    snapshot, so region_full_data (tooltip) and region_controllers (fill)
    can never diverge."""
    source = _read(EUROPE_SMOKE_GD)
    cycle_body = _func_body(source, "func _cycle_smoke_owner(region_name: String):")
    assert '_seeded_map_data[region_name]["controller"] = next_owner' in cycle_body
    assert "update_all_regions(_seeded_map_data)" in cycle_body


def test_europe_map_owner_cycle_uses_names_only():
    """No nation-color literals outside utils.gd — the cycle list carries
    names; colors always resolve through Utils.NATION_COLORS."""
    source = _read(EUROPE_SMOKE_GD)
    cycle_line = next(
        line for line in source.splitlines() if "const SMOKE_OWNER_CYCLE" in line
    )
    assert "Color(" not in cycle_line
    cycle_names = re.findall(r'"([A-Za-z]+)"', cycle_line)
    assert len(cycle_names) >= 2, "cycle needs at least two nations to demo a re-tint"
    nation_colors = _parse_nation_colors()
    for name in cycle_names:
        assert name in nation_colors, (
            f"SMOKE_OWNER_CYCLE entry {name!r} has no Utils.NATION_COLORS color"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Behavioral mirrors — lookup color -> region -> owner color
# ═══════════════════════════════════════════════════════════════════════════


def test_every_starting_controller_resolves_to_a_nation_color():
    registry = _load_europe_registry()
    nation_colors = _parse_nation_colors()
    missing = {
        row["starting_controller"]
        for row in registry["regions"].values()
        if row.get("starting_controller") not in nation_colors
    }
    assert not missing, (
        f"europe.json starting controllers without Utils.NATION_COLORS "
        f"entries (would fall back to COLOR_ENEMY_DEFAULT): {sorted(missing)}"
    )


def test_registry_fits_the_palette_capacity():
    registry = _load_europe_registry()
    max_provinces = _parse_max_provinces()
    assert len(registry["regions"]) <= max_provinces, (
        f"europe.json has {len(registry['regions'])} provinces but the "
        f"owner-fill palette holds {max_provinces} — the overflow would "
        f"silently never tint"
    )


def test_shader_epsilon_is_below_the_8bit_quantization_step():
    """Lookup colors are 8-bit; sampled texels are exact v/255 floats. The
    epsilon must accept exact matches (float error ~1e-7) and reject the
    nearest distinct 8-bit value (distance 1/255 ~ 0.0039)."""
    epsilon = _parse_shader_epsilon()
    assert 0.0 < epsilon < 1.0 / 255.0


def test_lookup_colors_are_unconfusable_under_the_shader_match():
    """No two provinces — and no province vs the sea sentinel — may sit
    within the shader's per-channel epsilon of each other, or fills would
    bleed across borders (or into open water)."""
    registry = _load_europe_registry()
    epsilon = _parse_shader_epsilon()
    sea = tuple(registry["no_province_color"])
    entries = [
        (name, tuple(row["lookup_color"]))
        for name, row in registry["regions"].items()
    ]
    seen: dict[tuple[int, int, int], str] = {}
    for name, color in entries:
        assert color not in seen, (
            f"{name} and {seen[color]} share lookup color {color}"
        )
        seen[color] = name
        assert not _shader_channels_match(color, sea, epsilon), (
            f"{name} lookup color {color} is within shader epsilon of the "
            f"sea sentinel {sea}"
        )
    colors = list(seen)
    for i, a in enumerate(colors):
        for b in colors[i + 1 :]:
            assert not _shader_channels_match(a, b, epsilon), (
                f"lookup colors {a} and {b} are within shader epsilon of "
                f"each other — the palette match cannot distinguish them"
            )


def test_palette_mirror_applies_the_fill_rules():
    nation_colors = _parse_nation_colors()
    enemy_default = _parse_enemy_default_color()
    order = ["Picardy", "Ghostland", "Ruritania", "Unownedia"]
    controllers = {
        "Picardy": "France",
        "Ruritania": "Zenda",  # unknown nation -> enemy-default fallback
        "Ghostland": "Austria",  # unwired -> transparent even with a controller
    }
    wired = {"Picardy": True, "Ghostland": False, "Ruritania": True, "Unownedia": True}
    palette = _build_palette_mirror(order, controllers, wired, nation_colors, enemy_default)

    france = nation_colors["France"]
    assert palette[0] == (france[0], france[1], france[2], 1.0)
    assert palette[1] == (0.0, 0.0, 0.0, 0.0), "unwired province must not tint"
    assert palette[2] == (enemy_default[0], enemy_default[1], enemy_default[2], 1.0)
    assert palette[3] == (0.0, 0.0, 0.0, 0.0), "no controller data -> no fill"


def test_full_1805_snapshot_resolves_every_palette_slot():
    """End-to-end mirror over the real registry: seeding every province's
    starting_controller produces an opaque, NATION_COLORS-backed palette
    slot for all 126 provinces (all wired today)."""
    registry = _load_europe_registry()
    nation_colors = _parse_nation_colors()
    enemy_default = _parse_enemy_default_color()
    order = [row["name"] for row in registry["regions"].values()]
    controllers = {
        row["name"]: row["starting_controller"]
        for row in registry["regions"].values()
    }
    wired = {row["name"]: bool(row.get("wired", True)) for row in registry["regions"].values()}
    palette = _build_palette_mirror(order, controllers, wired, nation_colors, enemy_default)
    assert len(palette) == len(registry["regions"])
    for slot, region_name in zip(palette, order):
        assert slot[3] == 1.0, f"{region_name} seeded but produced no fill"
        assert slot[:3] != enemy_default, (
            f"{region_name} fell back to COLOR_ENEMY_DEFAULT — its "
            f"starting_controller is missing a NATION_COLORS entry"
        )


def test_owner_fill_strength_is_a_tunable_fraction():
    """The tint alpha must be a real blend (not invisible, not a flat
    political map). The exact value is a manual-smoke tunable — do NOT pin it."""
    source = _read(BASE_GD)
    match = re.search(r"const OWNER_FILL_STRENGTH: float = ([0-9.]+)", source)
    assert match
    strength = float(match.group(1))
    assert 0.0 < strength < 1.0


# ═══════════════════════════════════════════════════════════════════════════
# Parse-harness coverage for the scenes-dir renderer scripts
# ═══════════════════════════════════════════════════════════════════════════


def test_parse_harness_covers_the_map_renderer_scripts():
    harness_text = _read(HARNESS_PATH)
    assert "const MAP_CRITICAL_SCRIPTS" in harness_text
    for script in MAP_CRITICAL_SCRIPTS:
        assert f'"res://scenes/{script}"' in harness_text, (
            f"tools/godot_parse_check.gd MAP_CRITICAL_SCRIPTS missing {script}"
        )
    with REPORT_PATH.open(encoding="utf-8") as f:
        report = json.load(f)
    covered = {
        entry.get("path", "").rsplit("/", 1)[-1]: entry
        for entry in report.get("scripts", [])
    }
    for script in MAP_CRITICAL_SCRIPTS:
        assert script in covered, f"parse report missing {script}; regenerate"
        assert covered[script].get("parse_ok") is True
        assert covered[script].get("load_ok") is True


def test_parse_report_is_not_stale_relative_to_map_renderer_scripts():
    """Scenes-dir mirror of test_godot_parse_harness.py's staleness guard
    (which resolves its own list against scripts/ only). Same 24h working-
    tree tolerance; regenerate via
    `Godot_v4.4.1-stable_win64.exe --headless --quit
     --path godot-client/project-sovereign
     --script ../../tools/godot_parse_check.gd`."""
    with REPORT_PATH.open(encoding="utf-8") as f:
        report = json.load(f)
    report_ts = report.get("timestamp", "")
    assert report_ts, "parse report missing timestamp"
    report_dt = datetime.datetime.fromisoformat(report_ts.replace("Z", "+00:00"))
    tolerance = datetime.timedelta(hours=24)
    for script in MAP_CRITICAL_SCRIPTS:
        path = GODOT_SCENES_DIR / script
        if not path.exists():
            continue
        mtime = datetime.datetime.fromtimestamp(
            path.stat().st_mtime, tz=datetime.timezone.utc
        )
        assert report_dt + tolerance >= mtime, (
            f"Godot parse report is stale relative to {path}; regenerate the "
            f"harness report"
        )

"""Source-level guardrails for the Session 8 renderer cutover slice."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map.gd"
BASE_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map_renderer_base.gd"
TOOLTIP_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map_tooltip_layer.gd"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_map_script_extends_renderer_base():
    source = _read(MAP_GD)
    assert 'extends "res://scenes/map_renderer_base.gd"' in source


def test_renderer_base_declares_scene_layers():
    source = _read(BASE_GD)
    for node_name in [
        'world_layer.name = "WorldLayer"',
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


def test_renderer_base_preserves_update_all_regions_contract():
    source = _read(BASE_GD)
    assert "func update_all_regions(map_data: Dictionary):" in source
    assert "region_full_data = map_data" in source
    assert "_refresh_all_region_visuals()" in source
    assert "_rebuild_dynamic_nodes()" in source
    update_body = source.split("func update_all_regions(map_data: Dictionary):", 1)[1]
    assert "queue_redraw()" in update_body


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

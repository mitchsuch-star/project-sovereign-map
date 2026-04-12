"""Source-level guardrails for the Session 8 renderer cutover slice."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map.gd"
BASE_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map_renderer_base.gd"


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
    ]:
        assert node_name in source, f"Missing renderer layer declaration: {node_name}"


def test_renderer_base_preserves_update_all_regions_contract():
    source = _read(BASE_GD)
    assert "func update_all_regions(map_data: Dictionary):" in source
    assert "region_full_data = map_data" in source
    assert "_refresh_all_region_visuals()" in source
    assert "_rebuild_dynamic_nodes()" in source

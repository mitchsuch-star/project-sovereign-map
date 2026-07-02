"""
Map Slice 7 — Godot game cutover + the default-boot flip to europe_1805.json.

Guards the two flips from docs/MAP_IMPLEMENTATION_PLAN.md §Slice 7 (landed as
ONE commit per the standing decision):

Backend — the default-boot flip:
    * An unconfigured backend (no SOVEREIGN_* env) boots the authored 1805
      scenario: 126 provinces, the 21-marshal opening, the seeded coalition war.
    * SOVEREIGN_SCENARIO=none is the explicit opt-out sentinel (bare
      flag-resolved world) — the suite-wide conftest default.
    * SOVEREIGN_MAP=legacy still bypasses the scenario entirely (the G1
      rollback drill stays a pure flag flip).
    * SOVEREIGN_SMOKE_START suppresses the DEFAULT scenario (presets seed
      their own wars); combining it with an EXPLICIT scenario fails loudly.

Godot — the game cutover (source-level pins in the renderer-suite style):
    * main.tscn's MapArea is scripted by map.gd, which is now the Europe game
      map (extends europe_map.gd; registry positions; no 19-region tables) —
      the successor of test_map_consistency.py's retired placeholder guards.
    * Connection lines are the registry's hand-authored sea links only,
      translated Region_NNN -> historical name (the re-keyed rows' `adjacent`
      id-lists are never drawn).
    * Province-level fog rides the owner-fill palette (legacy FogOverlay
      parity) without breaking the G4 single-uniform-upload re-tint.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as main_module

client = TestClient(main_module.app)

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_DIR = REPO_ROOT / "godot-client" / "project-sovereign"
MAIN_TSCN = GODOT_DIR / "scenes" / "main.tscn"
MAP_GD = GODOT_DIR / "scenes" / "map.gd"
EUROPE_GD = GODOT_DIR / "scenes" / "europe_map.gd"
EUROPE_SMOKE_GD = GODOT_DIR / "scenes" / "europe_map_smoke.gd"
EUROPE_SMOKE_TSCN = GODOT_DIR / "scenes" / "europe_map_smoke.tscn"
BASE_GD = GODOT_DIR / "scenes" / "map_renderer_base.gd"
MAIN_SCRIPT_GD = GODOT_DIR / "scripts" / "main.gd"
EUROPE_JSON = GODOT_DIR / "assets" / "maps" / "europe.json"
REPORT_PATH = REPO_ROOT / "tools" / "godot_parse_report.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _func_body(source: str, signature: str) -> str:
    return source.split(signature, 1)[1].split("\nfunc ", 1)[0]


@pytest.fixture(autouse=True)
def _isolated_save_dir(tmp_path, monkeypatch):
    """Keep /new_game autosaves out of the real saves/ directory."""
    import backend.save_manager as save_manager
    monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")


@pytest.fixture
def restore_bootstrap(monkeypatch):
    """Restore the suite's bare-world module state after bootstrap tests."""
    yield
    monkeypatch.setenv("SOVEREIGN_SCENARIO", "none")
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    monkeypatch.delenv("SOVEREIGN_SMOKE_START", raising=False)
    main_module._reset_world_state()


def _write_scenario(tmp_path, payload, name="scenario.json"):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


# ════════════════════════════════════════════════════════════════════
# THE DEFAULT-BOOT FLIP — an unconfigured backend boots the 1805 opening
# ════════════════════════════════════════════════════════════════════


def test_default_scenario_path_is_absolute_and_committed():
    path = main_module._DEFAULT_SCENARIO_PATH
    assert path.is_absolute()
    assert path.name == "europe_1805.json"
    assert path.exists(), "the shipped default scenario must exist in the repo"


def test_default_boot_is_the_1805_scenario(monkeypatch, restore_bootstrap):
    monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    world = main_module._reset_world_state()
    assert world.sovereign_map == "europe"
    assert len(world.regions) == 126
    assert world.current_turn == 1
    # The authored opening, not the bare army-less world:
    assert world.get_marshal("Ney") is not None
    assert world.get_marshal("Mack") is not None
    assert world.get_diplomatic_state("France", "Britain") == "WAR"
    assert world.get_diplomatic_state("France", "Austria") == "WAR"


def test_new_game_endpoint_boots_the_1805_default(monkeypatch, restore_bootstrap):
    monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    response = client.post("/new_game")
    assert response.status_code == 200
    assert response.json()["success"] is True
    world = main_module.world
    assert len(world.regions) == 126
    assert world.get_marshal("Ney") is not None
    assert world.get_diplomatic_state("France", "Britain") == "WAR"


def test_none_sentinel_opts_out_to_the_bare_flag_world(monkeypatch, restore_bootstrap):
    monkeypatch.setenv("SOVEREIGN_SCENARIO", "none")
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    world = main_module._reset_world_state()
    assert world.sovereign_map == "europe"
    assert len(world.regions) == 126
    assert not world.marshals, "the sentinel boots the army-less bare Europe world"


def test_legacy_rollback_flag_bypasses_the_scenario_default(monkeypatch, restore_bootstrap):
    """(G1) The rollback drill survives the flip: legacy map, legacy armies,
    no scenario load, no code change."""
    monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
    monkeypatch.setenv("SOVEREIGN_MAP", "legacy")
    assert main_module._resolve_scenario_path() == ""
    world = main_module._reset_world_state()
    assert world.sovereign_map == "legacy"
    assert len(world.regions) == 19
    assert world.get_nation_capital("Britain") == "Netherlands"
    assert world.get_marshal("Ney") is not None  # legacy roster, not 1805's


def test_explicit_scenario_path_still_wins(tmp_path, monkeypatch, restore_bootstrap):
    path = _write_scenario(
        tmp_path, {"sovereign_map": "europe", "player_nation": "France", "current_turn": 4}
    )
    monkeypatch.setenv("SOVEREIGN_SCENARIO", path)
    world = main_module._reset_world_state()
    assert world.current_turn == 4
    assert not world.marshals


def test_smoke_preset_alone_suppresses_the_scenario_default(monkeypatch, restore_bootstrap):
    """Presets seed wars in the WorldState constructor; the default scenario
    must yield to them rather than silently create the never-combine pair."""
    monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
    monkeypatch.setenv("SOVEREIGN_SMOKE_START", "settlement_multilateral")
    assert main_module._resolve_scenario_path() == ""
    world = main_module._reset_world_state()
    assert not world.get_marshal("Mack"), "no 1805 scenario under a smoke preset"


def test_explicit_scenario_plus_smoke_preset_fails_loudly(
    tmp_path, monkeypatch, restore_bootstrap
):
    path = _write_scenario(
        tmp_path, {"sovereign_map": "europe", "player_nation": "France"}
    )
    monkeypatch.setenv("SOVEREIGN_SCENARIO", path)
    monkeypatch.setenv("SOVEREIGN_SMOKE_START", "settlement_multilateral")
    with pytest.raises(ValueError, match="never combine"):
        main_module._reset_world_state()


# ════════════════════════════════════════════════════════════════════
# THE GODOT CUTOVER — main.tscn renders the Europe map through map.gd
# ════════════════════════════════════════════════════════════════════


def test_main_tscn_map_area_is_scripted_by_map_gd():
    tscn = _read(MAIN_TSCN)
    ext = re.search(
        r'\[ext_resource type="Script"[^\]]*path="res://scenes/map\.gd" id="([^"]+)"\]',
        tscn,
    )
    assert ext, "main.tscn must load res://scenes/map.gd as a script resource"
    node = re.search(
        r'\[node name="MapArea"[^\]]*\](.*?)(?=\n\[node |\Z)', tscn, re.DOTALL
    )
    assert node, "main.tscn must declare the MapArea node"
    assert f'script = ExtResource("{ext.group(1)}")' in node.group(1), (
        "MapArea must be scripted by map.gd (the Europe game map)"
    )


def test_map_gd_is_the_europe_game_map():
    """Successor of test_map_consistency.py's retired placeholder guards: the
    game map carries NO hardcoded region tables — positions come from the
    registry anchors (europe_map.gd), adjacency from backend /map_topology,
    and drawn connections from the registry sea links."""
    source = _read(MAP_GD)
    assert 'extends "res://scenes/europe_map.gd"' in source
    assert "REGION_POSITIONS" not in source
    assert "session8_placeholder_provinces" not in source
    assert "REGION_CONNECTIONS" not in source
    assert "Vector2(" not in source, (
        "map.gd needs no coordinates — registry anchors own positions"
    )
    topo_body = _func_body(source, "func set_region_topology(topology: Dictionary) -> void:")
    assert 'topology.get("regions", {})' in topo_body
    colors_body = _func_body(source, "func _get_colors() -> Dictionary:")
    assert "Utils.NATION_COLORS.duplicate()" in colors_body
    assert "Utils.COLOR_CONNECTION" in colors_body


def test_europe_map_translates_sea_links_for_connections():
    """Drawn connections are the registry's hand-authored sea links only,
    translated through the id->name map retained at re-key. The re-keyed
    rows' `adjacent` id-lists are never fed to connection drawing."""
    source = _read(EUROPE_GD)
    load_body = _func_body(source, "func _load_province_definition() -> Dictionary:")
    assert "_region_id_to_name[str(region_id)] = region_name" in load_body
    conn_body = _func_body(source, "func _get_region_connections() -> Dictionary:")
    assert 'province_definition.get("sea_links", [])' in conn_body
    assert '"Region_%03d" % int(pair[0])' in conn_body
    assert "_region_id_to_name" in conn_body
    assert '"adjacent"' not in conn_body, (
        "the re-keyed adjacent id-lists must never drive connection drawing"
    )


def test_sea_links_all_translate_to_known_provinces():
    """Behavioral mirror of the sea-link translation over the real registry."""
    registry = json.loads(_read(EUROPE_JSON))
    id_to_name = {rid: row["name"] for rid, row in registry["regions"].items()}
    sea_links = registry.get("sea_links", [])
    assert sea_links, "the registry's hand-authored sea links must exist"
    for pair in sea_links:
        a = id_to_name.get("Region_%03d" % int(pair[0]))
        b = id_to_name.get("Region_%03d" % int(pair[1]))
        assert a and b and a != b, f"untranslatable sea link {pair}"
    # DEF-6's cross-Channel link is the flagship case:
    named = {
        frozenset((id_to_name["Region_%03d" % int(p[0])], id_to_name["Region_%03d" % int(p[1])]))
        for p in sea_links
    }
    assert frozenset(("London", "Flanders")) in named


def test_smoke_scene_runs_the_smoke_subclass():
    """The smoke-only seed + owner-cycle demo moved to europe_map_smoke.gd;
    the shared renderer (europe_map.gd) must stay demo-free for the game."""
    tscn = _read(EUROPE_SMOKE_TSCN)
    assert 'path="res://scenes/europe_map_smoke.gd"' in tscn
    smoke = _read(EUROPE_SMOKE_GD)
    assert 'extends "res://scenes/europe_map.gd"' in smoke
    assert "SMOKE_OWNER_CYCLE" in smoke
    shared = _read(EUROPE_GD)
    for smoke_only in ["SMOKE_OWNER_CYCLE", "_seed_registry_ownership", "func _ready("]:
        assert smoke_only not in shared, (
            f"smoke-only member {smoke_only!r} leaked into the shared renderer"
        )


def test_help_text_examples_use_1805_names():
    source = _read(MAIN_SCRIPT_GD)
    assert "Wellington" not in source, "Wellington left the scenario (Moore replaced him)"
    assert '\\"scout Swabia\\"' in source
    assert '\\"Ney, attack Mack\\"' in source


# ════════════════════════════════════════════════════════════════════
# FOG WASH — province-level fog rides the owner-fill palette (G4-safe)
# ════════════════════════════════════════════════════════════════════


def _parse_fog_overlays() -> dict[str, tuple[float, float, float, float]]:
    source = _read(BASE_GD)
    block = source.split("const FOG_OVERLAYS = {", 1)[1].split("\n}", 1)[0]
    overlays = {}
    for name, args in re.findall(r'"(\w+)":\s*Color\(([^)]+)\)', block):
        parts = [float(p.strip()) for p in args.split(",")]
        overlays[name] = tuple(parts)
    return overlays


def _parse_fog_hue_scale() -> float:
    """Slice 7.5 (DEF-10): the rgb lerp is scaled below the raw fog alpha so
    the national hue survives the wash (the full-alpha lerp collapsed the
    turn-1 palette to grey-brown)."""
    source = _read(BASE_GD)
    match = re.search(r"const FOG_HUE_LERP_SCALE: float = ([0-9.]+)", source)
    assert match, "map_renderer_base.gd must define FOG_HUE_LERP_SCALE (Slice 7.5)"
    return float(match.group(1))


def _fog_composite(
    owner: tuple[float, float, float, float],
    fog: tuple[float, float, float, float],
    hue_scale: float,
) -> tuple[float, float, float, float]:
    """Python mirror of the palette fog wash in `_refresh_owner_fill_palette`:
    rgb lerps toward the fog color by its alpha scaled by FOG_HUE_LERP_SCALE
    (Slice 7.5 — hue retention); alpha takes the max so unknown-but-unowned
    provinces still wash."""
    if fog[3] <= 0.0:
        return owner
    wash = fog[3] * hue_scale
    return (
        owner[0] + (fog[0] - owner[0]) * wash,
        owner[1] + (fog[1] - owner[1]) * wash,
        owner[2] + (fog[2] - owner[2]) * wash,
        max(owner[3], fog[3]),
    )


def test_fog_wash_rides_the_owner_palette_upload():
    """The wash is per-province color math ahead of the SAME single uniform
    upload — the G4 no-per-pixel re-tint contract is untouched."""
    source = _read(BASE_GD)
    body = _func_body(source, "func _refresh_owner_fill_palette():")
    assert 'region_visibility.get(region_name, "full")' in body
    assert "FOG_OVERLAYS.get(visibility" in body
    assert body.count("lerpf(") == 3, "rgb channels lerp toward the fog color"
    assert "fog.a * FOG_HUE_LERP_SCALE" in body, (
        "the hue lerp must be scaled below the raw fog alpha (Slice 7.5 DEF-10)"
    )
    assert "maxf(owner_color.a, fog.a)" in body
    assert "if fog.a > 0.0:" in body, 'visibility "full" (alpha 0) must be a no-op'
    assert body.count('set_shader_parameter("owner_colors"') == 1, (
        "the fog wash must not add a second uniform upload"
    )
    scale = _parse_fog_hue_scale()
    assert 0.0 < scale < 1.0, "hue retention must weaken, not remove or invert, the wash"


def test_fog_overlays_carry_the_legacy_visibility_tiers():
    overlays = _parse_fog_overlays()
    assert set(overlays) == {"full", "partial", "stale", "last_known", "unknown"}
    assert overlays["full"][3] == 0.0, "full visibility must never tint"
    # Fog deepens as knowledge decays — the wash inherits the legacy ordering.
    assert (
        overlays["partial"][3]
        < overlays["stale"][3]
        < overlays["last_known"][3]
        < overlays["unknown"][3]
    )


def test_fog_wash_mirror_rules():
    overlays = _parse_fog_overlays()
    scale = _parse_fog_hue_scale()
    france = (0.2, 0.4, 0.8, 1.0)

    # Full visibility: palette entry unchanged (the pre-Slice-7 contract).
    assert _fog_composite(france, overlays["full"], scale) == france

    # Owned but unknown: still opaque, every channel pulled toward the fog —
    # but never all the way (Slice 7.5 hue retention: the owner hue survives).
    washed = _fog_composite(france, overlays["unknown"], scale)
    assert washed[3] == 1.0
    for owner_c, fog_c, washed_c in zip(france[:3], overlays["unknown"][:3], washed[:3]):
        assert min(owner_c, fog_c) <= washed_c <= max(owner_c, fog_c)
        assert washed_c != owner_c
        # Hue retention: the wash may not close more than `scale` of the gap.
        assert abs(washed_c - owner_c) <= abs(fog_c - owner_c) * scale + 1e-9

    # Unowned (transparent slot) but unknown: the dark wash still lands so
    # unscouted provinces read as fogged over the raw art.
    unowned = (0.0, 0.0, 0.0, 0.0)
    washed = _fog_composite(unowned, overlays["unknown"], scale)
    assert washed[3] == overlays["unknown"][3] > 0.0


def test_parse_report_covers_scene_instantiation():
    """The Slice-7 harness section instantiates main.tscn (verifying MapArea's
    script) and the smoke scene headless; the committed report carries the
    evidence."""
    report = json.loads(_read(REPORT_PATH))
    scenes = {entry["path"]: entry for entry in report.get("scenes", [])}
    for scene in ["res://scenes/main.tscn", "res://scenes/europe_map_smoke.tscn"]:
        assert scene in scenes, f"parse report missing {scene}; regenerate the harness"
        assert scenes[scene]["load_ok"] is True
        assert scenes[scene]["instantiate_ok"] is True
    assert scenes["res://scenes/main.tscn"]["map_area_script"] == "res://scenes/map.gd"

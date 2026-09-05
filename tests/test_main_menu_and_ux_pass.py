"""Main Menu pass (Road to EA position 6) + the Aug-8 UX fixes.

Pins, in one file, the three deliverables of the August 8, 2026 session:

1. THE MAIN MENU — the project boots into `scenes/main_menu.tscn` (painting
   slideshow, Cinzel title, campaign column), hands its action to main.gd via
   the `MenuBoot` statics, and ships the promoted Settings surface
   (`settings_panel.tscn`) embedded by BOTH the menu and the pause menu.
   Includes the shipping identity (name "Ink & Iron", generated icon.png) and
   the in-client API key: `/config/llm` (GET status, POST BYOK swap).

2. REWARD DISCOVERABILITY — every Generals card renders a real Reward CHIP
   (enabled via the existing `reward:` meta, or DISABLED with its stated gate
   reason — the UI-6 honest-availability idiom). The ES-7 reactive gate itself
   is unchanged (feedback memory: fix discoverability, never the gate).

3. THEMATIC CLICKS — the global button click is the CC0 wooden-tap trio and
   row/province select is the leather tap (user: the Interface-pack blips read
   as "laser"); the old files remain as pool variants.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_ROOT = REPO_ROOT / "godot-client" / "project-sovereign"
SCRIPTS = GODOT_ROOT / "scripts"
SCENES = GODOT_ROOT / "scenes"
PAINTINGS = GODOT_ROOT / "assets" / "ui" / "paintings"
AUDIO_UI = GODOT_ROOT / "assets" / "audio" / "ui"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# 1a. Project identity: name, icon, main scene
# ═══════════════════════════════════════════════════════════════════════════


class TestProjectIdentity:
    def test_project_boots_into_the_main_menu(self):
        text = _read(GODOT_ROOT / "project.godot")
        assert 'run/main_scene="res://scenes/main_menu.tscn"' in text, (
            "position 6: the Main Menu must be the project's main scene"
        )

    def test_shipping_name_is_ink_and_iron(self):
        text = _read(GODOT_ROOT / "project.godot")
        assert 'config/name="Ink & Iron"' in text

    def test_icon_is_the_generated_png(self):
        text = _read(GODOT_ROOT / "project.godot")
        assert 'config/icon="res://icon.png"' in text
        icon = GODOT_ROOT / "icon.png"
        assert icon.exists()
        assert icon.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        # ORIGINAL procedural art — the generator ships with the repo.
        assert (REPO_ROOT / "tools" / "gen_app_icon.py").exists()

    def test_boot_splash_is_navy_not_default_logo(self):
        text = _read(GODOT_ROOT / "project.godot")
        assert "boot_splash/show_image=false" in text
        assert "boot_splash/bg_color" in text


# ═══════════════════════════════════════════════════════════════════════════
# 1b. The menu scene: slideshow, hand-off, honest availability
# ═══════════════════════════════════════════════════════════════════════════


class TestMainMenuScene:
    def test_scene_and_script_exist_with_slide_layers(self):
        scene = _read(SCENES / "main_menu.tscn")
        assert 'name="SlideA" type="TextureRect"' in scene
        assert 'name="SlideB" type="TextureRect"' in scene
        assert 'name="StatusHttp" type="HTTPRequest"' in scene
        # KEEP_ASPECT_COVERED so every canvas cover-crops, never stretches
        assert "stretch_mode = 6" in scene

    def test_every_shipped_painting_is_in_the_slide_list(self):
        gd = _read(SCRIPTS / "main_menu.gd")
        jpgs = sorted(p.name for p in PAINTINGS.glob("*.jpg"))
        assert len(jpgs) == 6, f"expected the 6 sourced paintings, found {jpgs}"
        for name in jpgs:
            assert name in gd, f"painting {name} missing from SLIDES"

    def test_paintings_are_valid_jpegs_and_credited(self):
        licenses = _read(REPO_ROOT / "THIRD_PARTY_LICENSES.md")
        assert "## Main-Menu Battle Paintings" in licenses
        for p in PAINTINGS.glob("*.jpg"):
            head = p.read_bytes()[:3]
            assert head == b"\xff\xd8\xff", f"{p.name} is not a JPEG"
            assert p.name in licenses, f"{p.name} has no license record"

    def test_slide_captions_name_the_artists(self):
        gd = _read(SCRIPTS / "main_menu.gd")
        for artist in ("Gérard", "Gros", "Meissonier", "Vernet", "Turner", "David"):
            assert artist in gd, f"caption missing artist {artist}"

    def test_menu_hand_off_rides_menu_boot_statics(self):
        gd = _read(SCRIPTS / "main_menu.gd")
        boot = _read(SCRIPTS / "menu_boot.gd")
        assert "MenuBoot.pending_action" in gd
        assert 'change_scene_to_file(GAME_SCENE)' in gd
        assert 'GAME_SCENE := "res://scenes/main.tscn"' in gd
        # Golden Rule 4 in the statics: read, use, THEN clear.
        assert "static func take_action()" in boot
        assert 'pending_action = ""' in boot

    def test_menu_uses_child_timers_never_scene_tree_timers(self):
        """A SceneTreeTimer outlives the scene: a pending 13s slide tick would
        fire on the FREED menu after every campaign start (console error).
        Child Timer nodes die with the scene — pin the class of bug out."""
        gd = _read(SCRIPTS / "main_menu.gd")
        assert "get_tree().create_timer" not in gd
        assert "Timer.new()" in gd

    def test_menu_buttons_are_honest_about_the_backend(self):
        """FA-29 (slice 13) re-pointed this pin CONSCIOUSLY, in both
        directions.

        It asserted the literal `-m backend.main` in `main_menu.gd`, which
        is exactly the string that had to LEAVE that file: it is a Python
        command, and the zip a tester unpacks has no Python, no venv and no
        `backend/`. The row's own filed fix says "keep the dev string so
        this line holds" AND "main_menu.gd reads the helper" — two sentences
        that cannot both be true.

        So the pin now asserts what it was ever for: the menu polls, states
        a reason, disables what it cannot do, and the reason it states
        BRANCHES on which build is running.
        """
        gd = _read(SCRIPTS / "main_menu.gd")
        utils = _read(SCRIPTS / "utils.gd")
        assert "/test" in gd
        assert "Utils.launch_hint()" in gd
        assert "disabled = not" in gd
        assert "-m backend.main" in utils, "the editor arm still names it"
        assert "launch.bat" in utils, "and the template arm names the zip's"
        assert 'has_feature("editor")' in utils, (
            "one string for both builds is how this shipped a dead "
            "instruction in the first place — it must branch")

    def test_begin_confirms_before_replacing_a_campaign(self):
        gd = _read(SCRIPTS / "main_menu.gd")
        assert "_confirm_box" in gd
        assert "autosave" in gd.lower()

    def test_menu_music_is_the_title_theme_rotation(self):
        am = _read(SCRIPTS / "audio_manager.gd")
        assert '"menu": ["music/theme_eroica_i.ogg"]' in am
        assert "static func set_menu_mood" in am
        assert "static func stop_all_loops" in am
        gd = _read(SCRIPTS / "main_menu.gd")
        # deferred like main.gd's AudioManager.boot — the lazy audio instance
        # cannot add_child to a root busy instantiating this very scene
        assert "AudioManager.set_menu_mood.call_deferred()" in gd


# ═══════════════════════════════════════════════════════════════════════════
# 1c. main.gd consumes the hand-off through the EXISTING world-swap flows
# ═══════════════════════════════════════════════════════════════════════════


class TestMainGdHandOff:
    def test_connection_test_consumes_menu_boot_exactly_once(self):
        main = _read(SCRIPTS / "main.gd")
        assert "_consume_menu_boot_action()" in main
        assert "func _consume_menu_boot_action" in main
        # new_game reuses the pause flow — ONE world-swap machinery
        assert '"new_game":\n\t\t\t_on_pause_new_game_requested()' in main

    def test_continue_gates_on_payload_shape_not_success(self):
        """/saves returns a bare {"saves": [...]} with NO success field —
        both save-list handlers must gate on shape."""
        main = _read(SCRIPTS / "main.gd")
        assert "func _on_continue_saves_listed" in main
        continue_body = main.split("func _on_continue_saves_listed", 1)[1].split("\nfunc ")[0]
        assert "if response.success" not in continue_body
        assert 'response.get("saves"' in continue_body
        listed_body = main.split("func _on_saves_listed", 1)[1].split("\nfunc ")[0]
        assert "if response.success" not in listed_body
        assert 'response.get("saves"' in listed_body

    def test_pause_menu_gains_the_main_menu_exit(self):
        main = _read(SCRIPTS / "main.gd")
        assert "main_menu_requested.connect(_on_pause_main_menu_requested)" in main
        assert "func _on_pause_main_menu_requested" in main
        assert "MenuBoot.came_from_game = true" in main
        scene = _read(SCENES / "pause_menu.tscn")
        assert 'name="MainMenuButton"' in scene

    def test_stored_key_is_pushed_at_campaign_start(self):
        main = _read(SCRIPTS / "main.gd")
        assert "func _push_stored_llm_key" in main
        assert "_push_stored_llm_key()" in main
        api = _read(SCRIPTS / "api_client.gd")
        assert '"/config/llm"' in api


# ═══════════════════════════════════════════════════════════════════════════
# 1d. The shared Settings surface (promoted from the pause menu)
# ═══════════════════════════════════════════════════════════════════════════


class TestSharedSettingsPanel:
    def test_panel_scene_exists_and_owns_the_four_sections(self):
        assert (SCENES / "settings_panel.tscn").exists()
        panel = _read(SCRIPTS / "settings_panel.gd")
        for marker in ("INTERFACE", "SOUND", "THE PARSER (AI)", "CREDITS"):
            assert marker in panel, f"settings panel missing section {marker}"
        # the four bus sliders + battle toggle + the scale contract
        assert '["Master", "Music", "SFX", "UI"]' in panel
        assert "get_battle_sfx" in panel
        assert "signal ui_scale_changed" in panel

    def test_pause_menu_embeds_the_shared_panel_and_builds_nothing_itself(self):
        pause = _read(SCRIPTS / "pause_menu.gd")
        assert 'settings_panel.tscn' in pause
        # the promoted builders must NOT survive as a second copy
        assert "_add_volume_sliders" not in pause
        assert "_add_asset_credits" not in pause
        assert "UiScaleSlider" not in _read(SCENES / "pause_menu.tscn")

    def test_menu_embeds_the_same_panel(self):
        gd = _read(SCRIPTS / "main_menu.gd")
        assert 'settings_panel.tscn' in gd

    def test_api_key_is_stored_locally_via_ui_settings(self):
        ui = _read(SCRIPTS / "ui_settings.gd")
        assert "static func get_api_key" in ui
        assert "static func set_api_key" in ui
        panel = _read(SCRIPTS / "settings_panel.gd")
        assert "UiSettings.set_api_key" in panel
        assert "/config/llm" in panel
        assert "secret = true" in panel  # never render the key


# ═══════════════════════════════════════════════════════════════════════════
# 1e. Backend /config/llm — the BYOK seam
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def llm_config_client():
    """TestClient + guaranteed restore of the module-global parser's client
    (the endpoint swaps parser.llm; other tests share that parser)."""
    import backend.main as main_module

    client = TestClient(main_module.app)
    original_llm = main_module.parser.llm
    try:
        yield client, main_module
    finally:
        main_module.parser.llm = original_llm


class TestLLMConfigEndpoint:
    def test_get_reports_effective_parser_config(self, llm_config_client):
        client, main_module = llm_config_client
        resp = client.get("/config/llm")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["provider"] == main_module.parser.llm.provider_name
        assert data["key_source"] == main_module.parser.llm.key_source
        assert isinstance(data["live"], bool)

    def test_post_key_swaps_parser_to_byok_anthropic(self, llm_config_client):
        client, main_module = llm_config_client
        resp = client.post("/config/llm", json={"api_key": "sk-ant-test-menu-key"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["provider"] == "anthropic"
        assert data["key_source"] == "byok"
        assert data["live"] is True
        # the swap reached the ONE production LLM seam (parser.llm)
        assert main_module.parser.llm._byok_key == "sk-ant-test-menu-key"

    def test_post_empty_key_reverts_to_env_configuration(self, llm_config_client):
        client, main_module = llm_config_client
        client.post("/config/llm", json={"api_key": "sk-ant-test-menu-key"})
        resp = client.post("/config/llm", json={"api_key": ""})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["key_source"] != "byok"
        assert main_module.parser.llm._byok_key is None

    def test_whitespace_key_counts_as_empty(self, llm_config_client):
        client, main_module = llm_config_client
        resp = client.post("/config/llm", json={"api_key": "   "})
        assert resp.status_code == 200
        assert resp.json()["key_source"] != "byok"

    def test_key_is_never_echoed_back(self, llm_config_client):
        client, _ = llm_config_client
        resp = client.post("/config/llm", json={"api_key": "sk-ant-super-secret"})
        assert "sk-ant-super-secret" not in resp.text


# ═══════════════════════════════════════════════════════════════════════════
# 2. Reward discoverability: the chip is ALWAYS there, honestly gated
# ═══════════════════════════════════════════════════════════════════════════


class TestRewardChip:
    def test_utils_ships_the_disabled_chip_partner(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert "static func bb_chip_disabled" in utils
        body = utils.split("static func bb_chip_disabled", 1)[1].split("\n\n\nstatic func", 1)[0]
        assert "[url=" not in body, "a disabled chip must not be clickable"

    def test_generals_card_renders_an_enabled_reward_chip_when_eligible(self):
        mm = _read(SCRIPTS / "marshal_management.gd")
        assert '_button_chip("reward:' in mm, "eligible marshals get a REAL chip, not a bare text link"

    def test_generals_card_states_the_gate_reason_when_locked(self):
        mm = _read(SCRIPTS / "marshal_management.gd")
        # three honest-availability arms: prisoner / met / no expectation yet
        assert mm.count("bb_chip_disabled(") >= 3
        assert "held prisoner" in mm
        assert "expectation is met" in mm
        assert "victories raise his expectation" in mm

    def test_the_es7_reactive_gate_is_unchanged(self):
        """Feedback memory: fix discoverability, NEVER the gate — the enabled
        chip still requires an actual shortfall or standing rente."""
        mm = _read(SCRIPTS / "marshal_management.gd")
        assert "elif shortfall > 0 or pension > 0:" in mm


# ═══════════════════════════════════════════════════════════════════════════
# 3. Thematic clicks
# ═══════════════════════════════════════════════════════════════════════════


class TestThematicClicks:
    def test_click_cue_is_the_wooden_tap_trio(self):
        am = _read(SCRIPTS / "audio_manager.gd")
        m = re.search(r'"click": \{"files": \[(.*?)\]', am)
        assert m, "click cue missing"
        assert "wood_tap_1.ogg" in m.group(1)
        assert "wood_tap_2.ogg" in m.group(1)
        assert "wood_tap_3.ogg" in m.group(1)
        assert "click_primary" not in m.group(1), "the laser blip must be off the button cue"

    def test_select_cue_is_the_leather_tap(self):
        am = _read(SCRIPTS / "audio_manager.gd")
        m = re.search(r'"select": \{"files": \[(.*?)\]', am)
        assert m
        assert "leather_tap_1.ogg" in m.group(1)

    def test_the_new_cue_files_exist_and_the_pool_variants_survive(self):
        for name in ("wood_tap_1.ogg", "wood_tap_2.ogg", "wood_tap_3.ogg",
                     "leather_tap_1.ogg", "leather_tap_2.ogg"):
            assert (AUDIO_UI / name).exists(), f"missing cue file {name}"
        # the old files stay on disk as documented pool variants
        assert (AUDIO_UI / "click_primary.ogg").exists()
        assert (AUDIO_UI / "select_item.ogg").exists()

    def test_spec_cue_table_carries_the_swap(self):
        spec = _read(REPO_ROOT / "docs" / "MUSIC_SOUND_SPEC.md")
        assert "wood_tap_1/2/3.ogg" in spec
        assert "leather_tap_1/2.ogg" in spec


# ═══════════════════════════════════════════════════════════════════════════
# Harness coverage: every new script/scene is compile-gated
# ═══════════════════════════════════════════════════════════════════════════


class TestHarnessCoverage:
    def test_new_scripts_ride_the_parse_harness(self):
        harness = _read(REPO_ROOT / "tools" / "godot_parse_check.gd")
        for script in ("main_menu.gd", "settings_panel.gd", "menu_boot.gd"):
            assert script in harness
        for scene in ("main_menu.tscn", "settings_panel.tscn"):
            assert scene in harness

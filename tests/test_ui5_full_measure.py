"""Session UI-5 (November 12, 2026) — the full measure: sound, UX and UI.

The user's word: "do full upgrade of sounds, ux and ui leave nothing unturned
look online if needed, be thorough and dont leave anything open". The plan's
decisions are pinned here (docs/MUSIC_SOUND_SPEC.md §6, docs/UI_VISUAL_
FOUNDATION_SPEC.md §13, docs/SYSTEMS_REFERENCE.md §216). Source pins launch
nothing; `TestDriven` runs tools/ui5_probe.gd headless (the engine lane).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CLIENT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = CLIENT / "scripts"
AUDIO = CLIENT / "assets" / "audio"
ILLUS = CLIENT / "assets" / "ui" / "illustrations"
RECORD = REPO / "docs" / "audits" / "audio_loudness_2026_11_12.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _script(name: str) -> str:
    return _read(SCRIPTS / name)


def _block(src: str, name: str) -> str:
    start = src.index(f"const {name} := {{")
    return src[start:src.index("\n}\n", start)]


def _func(src: str, header: str) -> str:
    start = src.index(header)
    rest = src[start + len(header):]
    m = re.search(r"\n(?:static )?func ", rest)
    return src[start:start + len(header) + (m.start() if m else len(rest))]


def _registry_files() -> dict:
    src = _script("audio_manager.gd")
    out: dict[str, str] = {}
    for m in re.finditer(r'^\t"([a-z_0-9]+)": \{(.+)\},?\s*$', _block(src, "CUES"), re.M):
        for rel in re.findall(r'"([a-z_0-9]+/[^"]+)"', m.group(2)):
            out[rel] = "cue:" + m.group(1)
    for tag, rel in re.findall(r'^\t"([a-z_0-9]+)": \{"file": "([^"]+)"', _block(src, "LOOPS"), re.M):
        out[rel] = "loop:" + tag
    for rel in re.findall(r'"(music/[^"]+)"', _block(src, "MUSIC")):
        out[rel] = "music"
    for name in ("MUSIC_ONESHOTS", "ANTHEMS"):
        for _key, rel in re.findall(r'"([A-Za-z_]+)": "(music/[^"]+)"', _block(src, name)):
            out[rel] = name.lower()
    return out


# ══════════════════════════════════════════════════════════════════════════
# A1 — the engine
# ══════════════════════════════════════════════════════════════════════════

class TestTheBuses:
    def test_five_buses_and_ceremony_under_effects(self):
        src = _script("audio_manager.gd")
        body = _func(src, "func _ensure_buses() -> void:")
        assert 'for bus_name in ["Music", "SFX", "UI", "Ambience", "Ceremony"]:' in body
        assert 'AudioServer.set_bus_send(idx, "SFX" if bus_name == "Ceremony" else "Master")' in body

    def test_the_music_dips_under_a_ceremony(self):
        body = _func(_script("audio_manager.gd"), "func _ensure_buses() -> void:")
        assert "AudioEffectCompressor.new()" in body and 'duck.sidechain = &"Ceremony"' in body

    def test_the_master_never_clips(self):
        body = _func(_script("audio_manager.gd"), "func _ensure_buses() -> void:")
        assert "AudioEffectHardLimiter.new()" in body and "limiter.ceiling_db = -1.0" in body

    def test_every_bed_rides_the_ambience_bus(self):
        loops = _block(_script("audio_manager.gd"), "LOOPS")
        for tag, bus in re.findall(r'^\t"([a-z_0-9]+)": \{"file": "[^"]+", "bus": "(\w+)"', loops, re.M):
            assert bus == ("UI" if tag.startswith("scribble") else "Ambience"), (tag, bus)

    def test_ambience_has_its_own_slider(self):
        panel = _script("settings_panel.gd")
        assert '["Master", "Music", "SFX", "UI"]' in panel, "the pinned literal stands"
        assert '"Ambience"' in panel

    def test_the_window_in_the_background(self):
        src = _script("audio_manager.gd")
        body = _func(src, "func _notification(what: int) -> void:")
        assert "NOTIFICATION_APPLICATION_FOCUS_OUT" in body and "NOTIFICATION_APPLICATION_FOCUS_IN" in body
        assert "BACKGROUND_QUIET_DB" in body


class TestVariationAndVoices:
    def test_the_click_varies_and_is_capped(self):
        cues = _block(_script("audio_manager.gd"), "CUES")
        click = next(ln for ln in cues.split("\n") if '"click": {' in ln)
        assert '"pitch": 0.04' in click and '"max_voices": 3' in click

    def test_no_music_like_cue_varies(self):
        cues = _block(_script("audio_manager.gd"), "CUES")
        for name in ("reveille", "mail_call", "first_call", "to_the_color", "fanfare",
                     "bells_peal", "bugle_to_arms", "bugle_charge", "bugle_retreat"):
            row = next(ln for ln in cues.split("\n") if f'"{name}": {{' in ln)
            assert '"pitch"' not in row, name

    def test_a_voice_cap_skips_before_the_stamp(self):
        body = _func(_script("audio_manager.gd"), "func _play_cue(cue: String, max_seconds: float) -> AudioStreamPlayer:")
        assert body.index("max_voices") < body.index("_last_played_ms[cue] =")
        assert body.count("_last_played_ms[cue] =") == 1


class TestTheDefectsFixed:
    def test_the_verdict_has_its_own_quill(self):
        diorama = _script("battle_diorama.gd")
        assert 'start_loop("scribble_verdict")' in diorama
        assert 'stop_loop("scribble")' not in diorama and 'start_loop("scribble")' not in diorama

    def test_the_study_restarts_after_a_swap(self):
        body = _func(_script("main.gd"), "func _reset_frontend_state_for_world_swap(")
        loops = body.index("AudioManager.stop_all_loops()")
        cues = body.index("AudioManager.stop_all_cues()")
        assert "AudioManager.start_ambience()" in body[max(loops, cues):]

    def test_the_fall_stops_the_quill(self):
        body = _func(_script("main.gd"), "func set_input_enabled(")
        # The stop's own guard names `_campaign_over` (`if enabled or _campaign_over`);
        # what must follow the stop is the COERCION that closes the line after the Fall.
        assert body.index("AudioManager.stop_scribble()") < body.index("if enabled and _campaign_over")


# ══════════════════════════════════════════════════════════════════════════
# A2 — the music program
# ══════════════════════════════════════════════════════════════════════════

class TestTheMusic:
    def test_the_war_no_longer_plays_american_fife_tunes(self):
        music = _block(_script("audio_manager.gd"), "MUSIC")
        war = re.search(r'"war": \[(.*?)\]', music, re.S).group(1)
        for gone in ("fife_drum_brandywine", "fife_drum_field_medley", "fife_drum_warlike_medley"):
            assert gone not in war, gone
        assert "drums_rage_of_cornwallis" in war, "the drum-only feature stays"
        for kept in ("fife_drum_brandywine.ogg", "fife_drum_field_medley.ogg", "fife_drum_warlike_medley.ogg"):
            assert (AUDIO / "music" / kept).exists(), "the files stay on disk (one line restores them)"

    def test_crisis_and_court(self):
        music = _block(_script("audio_manager.gd"), "MUSIC")
        assert '"crisis": [' in music and '"court": [' in music
        assert "const CRISIS_SCORE := -30" in _script("audio_manager.gd")

    def test_the_menu_row_is_unchanged(self):
        assert '"menu": ["music/theme_eroica_i.ogg"]' in _block(_script("audio_manager.gd"), "MUSIC")

    def test_rests_between_pieces(self):
        src = _script("audio_manager.gd")
        body = _func(src, "func _on_music_finished() -> void:")
        assert "UiSettings.get_music_rests()" in body and "_rest_timer.start(" in body

    def test_every_piece_has_its_words(self):
        src = _script("audio_manager.gd")
        meta = _block(src, "MUSIC_META")
        for rel, role in _registry_files().items():
            if role in ("music", "music_oneshots", "anthems"):
                assert f'"{rel}"' in meta, rel

    def test_the_anthem_rule_in_one_place(self):
        body = _func(_script("audio_manager.gd"), "static func announce_war(opponent: String, france_attacker: bool) -> void:")
        assert 'if france_attacker or not inst._has_anthem(opponent):' in body
        assert 'inst._play_music_once("marseillaise")' in body

    def test_only_period_true_anthems(self):
        anthems = _block(_script("audio_manager.gd"), "ANTHEMS")
        assert '"Russia"' not in anthems, "the Navy Band's Russian anthem is the Soviet melody"
        assert '"Austria": "music/anthem_austria_kaiserhymne.ogg"' in anthems

    def test_the_campaign_end_plays_the_reserved_pieces(self):
        end = _script("campaign_end.gd")
        assert 'play_music_once("triumph")' in end and 'play_music_once("lament")' in end

    def test_the_court_scene_is_requested_and_released(self):
        for name in ("diplomacy_wizard.gd", "proposal_confirm_popup.gd"):
            src = _script(name)
            assert 'AudioManager.request_scene_music("court")' in src, name
            assert 'AudioManager.release_scene_music("court")' in src, name


# ══════════════════════════════════════════════════════════════════════════
# A4 — coverage
# ══════════════════════════════════════════════════════════════════════════

class TestCoverage:
    def test_no_surface_is_silent(self):
        out = subprocess.run([sys.executable, str(REPO / "tools" / "ui5_sound_census.py"), "--check"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert out.returncode == 0, out.stdout[-2000:]
        assert "silent: 0" in out.stdout

    def test_a_notice_priority_is_heard(self):
        bar = _script("notification_bar.gd")
        assert "AudioManager.hint_notification_priority(" in bar
        assert bar.count('AudioManager.play("notification")') == 1
        src = _script("audio_manager.gd")
        assert '"notification_critical": {' in src and '"notification_high": {' in src

    def test_decisions_do_not_stack_the_click(self):
        for name in ("incoming_proposal_popup.gd", "objection_dialog.gd", "marshal_petition_dialog.gd",
                     "glorious_charge_dialog.gd", "redemption_dialog.gd", "proposal_confirm_popup.gd"):
            assert 'set_meta("no_click_sfx", true)' in _script(name), name

    def test_hover_dropdown_and_link_hooks(self):
        body = _func(_script("audio_manager.gd"), "func _hook_button(node: Node) -> void:")
        assert "mouse_entered.connect(_on_any_button_hovered" in body
        assert "item_selected.connect(_on_option_item_selected" in body
        assert "meta_clicked.connect(_on_any_meta_clicked" in body

    def test_orders_are_heard_as_they_are_carried_out(self):
        src = _script("audio_manager.gd")
        results = _block(src, "RESULT_CUES")
        for verb in ("move", "attack", "fortify", "drill", "recruit", "build", "scout", "retreat"):
            assert f'"{verb}": ' in results, verb


# ══════════════════════════════════════════════════════════════════════════
# A6 — loudness
# ══════════════════════════════════════════════════════════════════════════

class TestLoudness:
    def test_every_registry_file_was_measured(self):
        record = json.loads(_read(RECORD))
        assert record["missing"] == []
        for rel in _registry_files():
            assert rel in record["files"], rel

    def test_the_trims_are_the_records(self):
        record = json.loads(_read(RECORD))
        src = _script("audio_manager.gd")
        for name, key in (("FILE_TRIM_DB", "file_trim_db"), ("MUSIC_TRIM_DB", "music_trim_db")):
            block = _block(src, name)
            got = {k: float(v) for k, v in re.findall(r'^\t"([^"]+)": (-?[0-9.]+),$', block, re.M)}
            assert got == {k: float(v) for k, v in record[key].items()}, name

    def test_the_rotation_sits_within_one_lu(self):
        record = json.loads(_read(RECORD))
        after = [record["files"][rel]["lufs"] + trim for rel, trim in record["music_trim_db"].items()
                 if any(r.startswith("music:") for r in record["files"][rel]["roles"])]
        # a piece too quiet to lift without clipping its peak may sit lower — never louder
        assert max(after) - record["music_target"] <= 1.0
        assert sum(1 for a in after if abs(a - record["music_target"]) <= 1.0) >= len(after) - 2

    def test_every_loop_seam_passes(self):
        record = json.loads(_read(RECORD))
        for rel, row in record["files"].items():
            if "seam" in row:
                assert row["seam"]["ok"], (rel, row["seam"])


# ══════════════════════════════════════════════════════════════════════════
# Settings — every new key with its default (the plan's decisions 1–4, 9, 13, 14)
# ══════════════════════════════════════════════════════════════════════════

class TestTheDefaults:
    def test_the_sound_switches(self):
        ui = _script("ui_settings.gd")
        assert 'get_value("audio", "hover_sfx", true)' in ui
        assert 'get_value("audio", "typing_sfx", true)' in ui
        assert 'get_value("audio", "music_rests", true)' in ui
        assert 'const DEFAULT_BACKGROUND_AUDIO := "quiet"' in ui
        assert '"Ambience": 0.7,' in ui

    def test_the_display_and_order_switches(self):
        ui = _script("ui_settings.gd")
        # ON for a player; a driven harness (settings in memory) keeps its scripted day
        assert 'get_value("orders", "idle_warning", not harness_active())' in ui
        assert 'const DEFAULT_COLOUR_VISION := "standard"' in ui
        assert 'const DEFAULT_TOOLTIP_DELAY := "short"' in ui
        assert 'get_value("display", "edge_scroll", false)' in ui

    def test_the_tabs_stay_five(self):
        assert 'const _TAB_NAMES := ["DISPLAY", "SOUND", "ORDERS", "CONTROLS", "CREDITS"]' in _script("settings_panel.gd")


class TestTheTooltipDelay:
    def test_the_engine_floor_and_the_held_reveal(self):
        assert "timers/tooltip_delay_sec=0.05" in _read(CLIENT / "project.godot")
        utils = _script("utils.gd")
        assert "const TOOLTIP_ENGINE_FLOOR_S := 0.05" in utils
        assert "_hold_tooltip(node)" in _func(utils, "static func _wrap_tooltip_popup(node: Node) -> void:")


class TestColourVision:
    def test_the_tokens_retone_at_the_sinks(self):
        utils = _script("utils.gd")
        assert 'static var COLOR_SUCCESS := "8fbc8f"' in utils
        assert 'static var COLOR_ERROR := "d06e6e"' in utils
        assert "apply_colour_vision()" in _func(utils, "static func apply_contrast(tree: SceneTree = null) -> void:")
        assert 'const COLOR_ERROR_CHIP = "d68686"' in utils, "a pinned contrast const stays"


class TestTheKeys:
    def test_the_actions_and_their_defaults(self):
        keys = _script("keys.gd")
        for action, key in (("event_log", "KEY_L"), ("ledger", "KEY_T"), ("end_turn", "KEY_E"),
                            ("help", "KEY_F10"), ("hide_hud", "KEY_H"), ("quicksave", "KEY_F5"),
                            ("quickload", "KEY_F9")):
            assert f'["{action}", ' in keys and key in keys, action

    def test_a_rebinding_is_read_at_the_handlers_door(self):
        main = _script("main.gd")
        # The two hotkey doors — the line's gui_input and _unhandled_input (whose Alt+key
        # path runs after the canonical read); `_input`'s type-through carries typed
        # characters to a draft, never a hotkey, so it reads no binding.
        assert main.count("Keys.canonical(event)") == 2
        assert "func _on_command_input_gui_input(event):" in main and "func _unhandled_input(event):" in main
        assert "const _SCREEN_HOTKEYS := {" in main, "the literal table stands"
        assert "Keys.canonical(event)" in _read(CLIENT / "scenes" / "map_renderer_base.gd")


# ══════════════════════════════════════════════════════════════════════════
# B — the pictures
# ══════════════════════════════════════════════════════════════════════════

class TestThePictures:
    def test_every_authored_letter_has_its_picture(self):
        scenario = json.loads(_read(CLIENT / "assets" / "maps" / "europe_1805.json"))
        ids = [m["id"] for m in scenario["moments"]["deck"]]
        ids += [a["id"] for a in scenario["moments"]["affairs"]["deck"]]
        catalogue = _block(_script("illustrations.gd"), "LETTER_BY_TEMPLATE")
        for template in ids:
            assert f'"{template}": ' in catalogue, template

    def test_every_work_is_on_disk_in_both_forms(self):
        works = _block(_script("illustrations.gd"), "WORKS")
        keys = re.findall(r'^\t"([a-z_]+)": \{', works, re.M)
        assert keys
        for key in keys:
            for form in ("banner", "plate"):
                assert (ILLUS / f"{key}_{form}.jpg").exists(), (key, form)

    def test_the_paintings_folder_is_untouched(self):
        assert len(list((CLIENT / "assets" / "ui" / "paintings").glob("*.jpg"))) == 6


# ══════════════════════════════════════════════════════════════════════════
# The licences — every new file is on the ledger
# ══════════════════════════════════════════════════════════════════════════

class TestTheReadingsFixes:
    """What the interim reading, the engine lane and the final shoot caught (UI spec §13), pinned at the cause."""

    def test_no_value_or_collapses_to_a_bool(self):
        """GDScript's `or` answers a bool, never an operand: `str(x or y)` printed "true" under every locked
        vassal chip. No client script wraps an `or` of payload reads in a conversion."""
        rx = re.compile(r"\b(str|int|float)\([^()]*\.get\([^()]*\)[^()]* or ")
        hits = []
        for folder in (SCRIPTS, CLIENT / "scenes"):
            for path in sorted(folder.glob("*.gd")):
                for n, line in enumerate(_read(path).splitlines(), 1):
                    if rx.search(line) and not line.lstrip().startswith("#"):
                        hits.append(f"{path.name}:{n}")
        assert hits == [], hits

    def test_a_folded_locked_chip_says_why_in_its_hover(self):
        """UI-4's rule under the user's "Fold, a switch restores": no visible caption per locked chip."""
        parts = _func(_script("diplomatic_ledger.gd"), "func _vassal_action_parts(")
        assert 'return [Utils.bb_chip_disabled(label, "", gated), ""]' in parts
        assert "_recruit_refusal_line" not in _script("region_panel.gd")

    def test_a_banner_gives_up_its_height_first(self):
        illus = _script("illustrations.gd")
        assert "follow_width: bool = false" in illus and "static func fit_banner_to_card(" in illus
        assert "const BAR_BAND := 44.0" in illus and "const BANNER_FLOOR := 72.0" in illus
        for name in ("objection_dialog", "capture_choice_dialog", "commitment_paradox_popup", "glorious_charge_dialog",
                     "interrupt_popup", "marshal_petition_dialog", "sabotage_discovery_popup", "vassal_rebellion_popup"):
            src = _script(name + ".gd")
            assert "Illustrations.fit_banner_to_card($PanelContainer, view.y)" in src, name
            assert re.search(r"Illustrations\.make_banner\(surface, .*, true\)$", src, re.M), name
        # a letter's picture takes only what its words leave (the armistice's cost above the fold, PC-F46)
        assert "maxf(body_h, 140.0)" in _func(_script("incoming_proposal_popup.gd"), "func _fit_letter_banner(")

    def test_each_surface_its_own_picture_and_a_strip_a_wide_scene(self):
        surfaces = _block(_script("illustrations.gd"), "SURFACES")
        for surface, key in (("cabinet", "congress"), ("objection", "council"), ("petition", "court"),
                             ("correspondence", "treaty")):
            assert f'"{surface}": "{key}"' in surfaces, surface
        for name in ("diplomacy_wizard.gd", "proposal_confirm_popup.gd"):
            assert "const BANNER_MIN_VIEW_HEIGHT := 880.0" in _script(name), name

    def test_the_compact_window_folds_until_the_player_is_at_the_line(self):
        main = _script("main.gd")
        body = _func(main, "func _ui5_compact_collapsed(")
        assert "_ui5_compact_engaged and command_input.has_focus()" in body
        assert "command_input.gui_input.connect(_ui5_line_gui_input)" in main
        relayout = main[main.index("var collapsed := _ui5_compact_collapsed()"):]
        assert "(gold_value.get_parent() as Control).visible = not collapsed" in relayout[:1600]

    def test_the_war_detail_leads_with_the_peace_table(self):
        body = _func(_script("war_detail_popup.gd"), "func _render_war_detail(")
        assert "bbcode = tier_bb + bbcode + prose" in body


class TestTheLedger:
    def test_every_audio_and_picture_file_is_credited(self):
        """Every file is named on the ledger or in the sound spec's inventory
        (§1 and §1a name the August files one by one; the ledger names every
        UI-5 file with its source, uploader and licence)."""
        ledger = _read(REPO / "THIRD_PARTY_LICENSES.md")
        spec = _read(REPO / "docs" / "MUSIC_SOUND_SPEC.md")
        missing = []
        for folder in (AUDIO, ILLUS):
            for path in folder.rglob("*"):
                if path.suffix.lower() in (".ogg", ".mp3", ".wav", ".jpg"):
                    if path.name not in ledger and path.name not in spec:
                        missing.append(str(path.relative_to(CLIENT)))
        assert not missing, missing

    # Every audio file Session UI-5 added (assets/ is git-ignored and force-added,
    # so this list is the commit's own record of what it ships).
    UI5_AUDIO = (
        "ambient/birds_loop.ogg", "ambient/clock_loop.ogg", "ambient/crowd_cheer.ogg",
        "ambient/distant_drums.ogg", "ambient/fire_loop.ogg", "ambient/rain_loop.ogg",
        "ambient/winter_wind_loop.ogg", "battle/boots_halt.ogg", "battle/drum_cadence.ogg",
        "battle/hammer.ogg", "battle/horse_trot.ogg", "battle/saw.ogg", "battle/spade_dig.ogg",
        "music/anthem_austria_kaiserhymne.ogg", "music/anthem_britain_god_save.ogg",
        "music/anthem_denmark_kong_christian.ogg", "music/anthem_holland_wilhelmus.ogg",
        "music/anthem_spain_marcha_real.ogg", "music/anthem_warsaw_dabrowski.ogg",
        "music/bugle_assembly.mp3", "music/bugle_fix_bayonets.mp3", "music/bugle_tattoo.mp3",
        "music/court_beethoven_op18_6_ii.ogg", "music/court_figaro_overture.ogg",
        "music/court_haydn_lark_i.ogg", "music/court_mozart40_iii.ogg", "music/court_mozart_quartet.ogg",
        "music/crisis_mozart40_i.ogg", "music/crisis_mozart40_iv.ogg",
        "music/peace_magic_flute_overture.ogg", "music/peace_mozart_k421_ii.ogg",
        "music/peace_mozart_k465_ii.ogg", "music/war_beethoven5_i.ogg", "music/war_egmont.ogg",
        "music/war_eroica_iii.ogg", "ui/door_knock.ogg", "ui/gavel.ogg", "ui/hover_tick.ogg",
        "ui/hover_tick_2.ogg", "ui/paper_slide.ogg", "ui/quill_scribble_long_seamless.ogg",
        "ui/quill_scribble_loop_seamless.ogg", "ui/quill_strokes.ogg",
        # the seven re-made loops (their wraps stepped 8-30 dB or clicked)
        "ambient/crowd_murmur_seamless.ogg", "ambient/fire_loop_seamless.ogg",
        "ambient/rain_loop_seamless.ogg", "ambient/winter_wind_loop_seamless.ogg",
        "ambient/ship_creak_1_seamless.ogg", "battle/army_march_loop_short_seamless.ogg",
        "battle/battlefield_ambience_seamless.ogg",
    )

    def test_every_ui5_file_names_its_source_on_the_ledger(self):
        """Each file Session UI-5 added stands, on disk and by name, in the
        ledger's Session UI-5 sections (the audio, the music and the pictures)."""
        ledger = _read(REPO / "THIRD_PARTY_LICENSES.md")
        section = ledger[ledger.index("### Session UI-5"):]
        audio = CLIENT / "assets" / "audio"
        for rel in self.UI5_AUDIO:
            assert (audio / rel).exists(), rel
            assert (audio / (rel + ".import")).exists(), rel + " (no .import: run Godot's --import)"
            assert rel.split("/")[-1] in section, rel
        pictures = CLIENT / "assets" / "ui" / "illustrations"
        works = re.findall(r'^\t"([a-z_]+)": \{"title"', _read(CLIENT / "scripts" / "illustrations.gd"), re.M)
        assert len(works) >= 30
        for key in works:
            for form in ("banner", "plate"):
                assert (pictures / f"{key}_{form}.jpg").exists(), (key, form)
        illus = ledger[ledger.index("## Illustrations"):]
        for key in works:
            assert f"{key}_banner.jpg" in illus or f"`{key}`" in illus, key

    def test_every_audio_file_on_disk_has_a_record(self):
        """No sound ships unrecorded: each file under assets/audio is named in
        the ledger or in the per-file inventory the ledger points to
        (docs/MUSIC_SOUND_SPEC.md, the August pass's files)."""
        ledger = _read(REPO / "THIRD_PARTY_LICENSES.md")
        spec = _read(REPO / "docs" / "MUSIC_SOUND_SPEC.md")
        for f in sorted((CLIENT / "assets" / "audio").rglob("*")):
            if f.is_dir() or f.suffix in (".import", ".zip", ".txt", ".md"):
                continue
            assert f.name in ledger or f.name in spec, f.relative_to(CLIENT)


# ══════════════════════════════════════════════════════════════════════════
# Driven — the headless probe (the engine lane)
# ══════════════════════════════════════════════════════════════════════════

GODOT = os.environ.get("IQ10_GODOT", r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe")


class TestDriven:
    def test_the_probe(self):
        if not Path(GODOT).exists():
            pytest.skip("no Godot binary on this machine (a skip is not a pass)")
        proc = subprocess.run([GODOT, "--headless", "--path", str(CLIENT), "--script",
                               str(REPO / "tools" / "ui5_probe.gd")],
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=240, stdin=subprocess.DEVNULL)
        out = proc.stdout + proc.stderr
        assert "[UI5] PASS" in out, out[-4000:]
        assert "SCRIPT ERROR" not in out, out[-4000:]

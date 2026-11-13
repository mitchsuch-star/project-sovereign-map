"""Session UI (November 11, 2026) — "The Gilt Frame, the War Table and the Dressed Page".

The user's word: "MAKE THE UI AND UX LOOK BETTER — LOOK ONLINE IF NEEDED"; at
the plan's head they ruled the content re-layout into the same session and a
dark leather desk around the map. Record: docs/UI_VISUAL_FOUNDATION_SPEC.md §9;
rules docs/SYSTEMS_REFERENCE.md §212.

What these pins hold:

* THE CHROME KIT — one window frame (scripts/gilt_frame.gd, a scripted StyleBox
  that keeps StyleBoxFlat's property names), one rule (scripts/gilt_rule.gd),
  one tab strip (Utils.tab_styles), the primary button steps and the title face
  in the theme. Every window, popup and HUD panel scene wears the frame with its
  OWN fill, tone and margins.
* SAME BOXES — the frame changes no layout: content margins, the Button
  margins, the separator's height (the rule's minimum is zero) are what they
  were.
* THE WAR ROOM — the desk (one switch restores July), the command window in
  its frame, End Turn the gilt primary exactly when the day is spent (DDB-R4's
  cue, invisible since it landed: it added gold to words already gold).
* THE DRESSED PAGE — cards and the figure column add NOTHING to a page's
  words: the marks are no-op tags, the column is invisible spacers; the driven
  probe compares parsed text character for character.

The driven half runs tools/ui_gilt_probe.gd headless and SKIPS when the engine
is absent — a skip is not a pass.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
THEME = PROJECT / "ui" / "main_theme.tres"
PROBE = REPO / "tools" / "ui_gilt_probe.gd"

FRAME_REF = 'path="res://scripts/gilt_frame.gd"'
# Every window, popup and HUD panel scene: the 32 that each carried their own
# navy-and-tan StyleBoxFlat, the notice rail, the command window (main) and the
# region panel (which wore the theme's bare leather).
FRAMED_SCENES = {
    "campaign_end", "campaign_log", "capture_choice_dialog", "clarification_popup",
    "commitment_paradox_popup", "diplomacy_wizard", "diplomatic_ledger", "dispatch_view",
    "enemy_phase_dialog", "gazette_view", "glorious_charge_dialog", "incoming_proposal_popup",
    "interrupt_popup", "load_dialog", "mailbox_panel", "marshal_management",
    "marshal_petition_dialog", "objection_dialog", "order_confirm_card", "pause_menu",
    "proclamation_popup", "proposal_confirm_popup", "redemption_dialog", "reward_dialog",
    "sabotage_discovery_popup", "strategic_ledger", "strategic_report_popup",
    "talleyrand_objection_popup", "tutorial_overlay", "vassal_rebellion_popup",
    "war_detail_popup", "war_status_panel", "notification_bar", "main", "region_panel",
}
# The flat boxes that stay flat, each a strip or a band, not a window.
FLAT_BY_DESIGN = {
    ("top_bar", "StyleBoxFlat_bar_bg"),     # the war room's strip
    ("main", "StyleBoxFlat_header"),        # the command window's header band
}


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    m = re.search(rf"(?ms)^(?:static )?func {re.escape(name)}\(.*?(?=^(?:static )?func |\Z)", src)
    assert m, name
    return m.group(0)


def _sub_resources(text: str) -> dict:
    return {m.group(2): (m.group(1), m.group(3)) for m in re.finditer(
        r'(?ms)^\[sub_resource type="(\w+)" id="([^"]+)"\]\n(.*?)(?=^\[|\Z)', text)}


def _panel_boxes(text: str) -> list:
    return re.findall(r'(?m)^theme_override_styles/panel = SubResource\("([^"]+)"\)', text)


# ═══════════════════════════════════════════════════════════════════════════
# The chrome kit
# ═══════════════════════════════════════════════════════════════════════════


class TestTheFrame:
    def test_the_frame_is_a_scripted_stylebox_with_flats_names(self):
        src = _read(SCRIPTS / "gilt_frame.gd")
        assert src.startswith("@tool\nextends StyleBox"), "the frame draws in the editor too"
        assert "class_name" not in src.split("\n# ===", 1)[0], "no class_name: no class-cache pass"
        for prop in ("bg_color", "border_color", "weight", "shadow"):
            assert re.search(rf"(?m)^@export(?:_\w+\([^)]*\))? var {prop}\b", src), prop
        assert "func _draw(to_canvas_item: RID, rect: Rect2) -> void:" in src
        assert "func thickness() -> float:" in src

    def test_the_rule_moves_no_separator(self):
        src = _read(SCRIPTS / "gilt_rule.gd")
        assert src.startswith("@tool\nextends StyleBox")
        assert "return Vector2.ZERO" in _func(src, "_get_minimum_size")

    def test_every_window_scene_wears_the_frame(self):
        framed = {p.stem for p in SCENES.glob("*.tscn") if FRAME_REF in _read(p)}
        assert framed == FRAMED_SCENES

    def test_each_frame_keeps_its_scenes_fill_tone_and_margins(self):
        for name in sorted(FRAMED_SCENES):
            text = _read(SCENES / f"{name}.tscn")
            ext_id = re.search(r'\[ext_resource type="Script" path="res://scripts/gilt_frame.gd" id="([^"]+)"\]',
                               text).group(1)
            subs = _sub_resources(text)
            frames = {sid: body for sid, (kind, body) in subs.items()
                      if kind == "StyleBox" and f'script = ExtResource("{ext_id}")' in body}
            assert frames, name
            for sid, body in frames.items():
                assert body.startswith(f'script = ExtResource("{ext_id}")'), (name, "script first")
                for key in ("bg_color", "border_color", "content_margin_left", "content_margin_top",
                            "content_margin_right", "content_margin_bottom"):
                    assert re.search(rf"(?m)^{key} = ", body), (name, sid, key)
                assert "border_width_" not in body and "corner_radius_" not in body, (name, sid)
                assert sid in _panel_boxes(text), (name, sid, "wired as the panel")

    def test_no_window_wears_a_flat_box(self):
        for path in sorted(SCENES.glob("*.tscn")):
            text = _read(path)
            subs = _sub_resources(text)
            for sid in _panel_boxes(text):
                kind = subs[sid][0]
                if kind == "StyleBoxFlat":
                    assert (path.stem, sid) in FLAT_BY_DESIGN, (path.stem, sid)

    def test_the_scenes_tones_are_kept(self):
        """A frame's tone is its surface's meaning: the enemy phase's crimson,
        the charge's orange, the rebellion's red, the paradox's amber."""
        tones = {
            "enemy_phase_dialog": "Color(0.804, 0.361, 0.361, 1)",
            "glorious_charge_dialog": "Color(0.85, 0.5, 0.2, 1)",
            "vassal_rebellion_popup": "Color(0.9, 0.3, 0.2, 1)",
            "commitment_paradox_popup": "Color(0.85, 0.7, 0.3, 1)",
            "sabotage_discovery_popup": "Color(0.9, 0.6, 0.2, 1)",
            "redemption_dialog": "Color(0.8, 0.42, 0.42, 1)",
        }
        for scene, tone in tones.items():
            assert f"border_color = {tone}" in _read(SCENES / f"{scene}.tscn"), scene

    def test_the_hud_pieces_take_the_lighter_weights(self):
        assert "weight = 1" in _read(SCENES / "war_detail_popup.tscn")
        assert "weight = 1" in _read(SCENES / "tutorial_overlay.tscn")
        assert "weight = 2" in _read(SCENES / "war_status_panel.tscn")
        assert "weight = 2" in _read(SCENES / "notification_bar.tscn")

    def test_the_consumers_ask_by_property_not_by_class(self):
        """Three places read a panel's box as a StyleBoxFlat; a scripted box
        would have silently stopped the tints (and the harness's reading)."""
        objection = _func(_read(SCRIPTS / "objection_dialog.gd"), "_apply_tone_styling")
        code = "\n".join(ln for ln in objection.splitlines() if not ln.strip().startswith("#"))
        assert 'if style and "border_color" in style:' in code and "is StyleBoxFlat" not in code
        proposal = _read(SCRIPTS / "incoming_proposal_popup.gd")
        assert "@onready var panel_style = $PanelContainer.get_theme_stylebox(\"panel\")" in proposal
        assert "var panel_style: StyleBoxFlat" not in proposal
        harness = _func(_read(REPO / "tools" / "iq10_surface_screenshot.gd"), "_draws")
        assert '"bg_color" in sb and "border_color" in sb' in harness

    def test_code_built_panels_use_the_one_frame(self):
        assert "Utils.gilt_frame(" in _func(_read(SCRIPTS / "popup_base.gd"), "_apply_standard_theme")
        assert "Utils.gilt_frame(" in _func(_read(SCRIPTS / "campaign_end.gd"), "_apply_style")
        assert "Utils.gilt_frame(" in _read(SCRIPTS / "scale_card.gd")
        assert _read(SCRIPTS / "notification_bar.gd").count("Utils.gilt_frame(") == 2
        assert "Utils.leather_frame(" in _func(_read(SCRIPTS / "main.gd"), "_build_map_controls")


class TestTheTheme:
    def test_the_button_states_keep_their_margins(self):
        """Same boxes: every state's horizontal margins are 12 + 12 and its
        vertical ones sum to 12 (pressed sinks a pixel: 7 + 5)."""
        text = _read(THEME)
        subs = _sub_resources(text)
        for state in ("normal", "hover", "pressed", "disabled", "focus"):
            sid = re.search(rf'(?m)^Button/styles/{state} = SubResource\("([^"]+)"\)', text).group(1)
            body = subs[sid][1]
            m = {s: float(re.search(rf"(?m)^content_margin_{s} = ([0-9.]+)", body).group(1))
                 for s in ("left", "top", "right", "bottom")}
            assert m["left"] == 12.0 and m["right"] == 12.0, (state, m)
            assert m["top"] + m["bottom"] == 12.0, (state, m)

    def test_the_focus_ring_is_a_ring(self):
        text = _read(THEME)
        sid = re.search(r'(?m)^Button/styles/focus = SubResource\("([^"]+)"\)', text).group(1)
        body = _sub_resources(text)[sid][1]
        assert "draw_center = false" in body and "expand_margin_left = 2.0" in body

    def test_the_primary_steps(self):
        text = _read(THEME)
        for name, size in (("PrimaryButton", 16), ("PrimaryCaptionButton", 14)):
            assert f'{name}/base_type = &"Button"' in text
            assert f"{name}/font_sizes/font_size = {size}" in text
            assert f'{name}/styles/normal = SubResource("StyleBoxFlat_primary")' in text
            assert f"{name}/colors/font_color = Color(0.07, 0.085, 0.14, 1)" in text

    def test_the_titles_take_the_title_face(self):
        text = _read(THEME)
        for step in ("ScreenTitle", "DialogTitle", "DialogTitleLarge", "HudTitle"):
            assert f'{step}/fonts/font = SubResource("FontVariation_title")' in text, step
        body = _sub_resources(text)["FontVariation_title"][1]
        assert 'base_font = ExtResource("1_6tukj")' in body and "spacing_glyph = 2" in body
        assert 'path="res://assets/fonts/Cinzel[wght].ttf" id="1_6tukj"' in text

    def test_the_rule_scrollbars_field_menu_and_slider(self):
        text = _read(THEME)
        assert 'HSeparator/styles/separator = SubResource("StyleBox_rule")' in text
        assert '[ext_resource type="Script" path="res://scripts/gilt_rule.gd" id="5_rule"]' in text
        for bar in ("VScrollBar", "HScrollBar"):
            for item in ("grabber", "grabber_highlight", "grabber_pressed", "scroll"):
                assert f"{bar}/styles/{item} = SubResource(" in text, (bar, item)
        assert 'LineEdit/styles/normal = SubResource("StyleBoxFlat_field")' in text
        assert 'PopupMenu/styles/panel = SubResource("StyleBoxFlat_menu")' in text
        assert 'HSlider/styles/slider = SubResource("StyleBoxFlat_slider")' in text

    def test_the_command_lines_field_keeps_its_size(self):
        """The engine default's 4 px a side: the command line is the size it was."""
        body = _sub_resources(_read(THEME))["StyleBoxFlat_field"][1]
        for side in ("left", "top", "right", "bottom"):
            assert f"content_margin_{side} = 4.0" in body


class TestTheTabStrip:
    def test_one_strip_three_users(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert "static func tab_styles(" in utils and "static func dress_tab(" in utils
        for name, margins in (("strategic_ledger.gd", "6.0, 3.0"), ("diplomatic_ledger.gd", "6.0, 3.0"),
                              ("top_bar.gd", "8.0, 4.0")):
            assert f"Utils.tab_styles({margins})" in _read(SCRIPTS / name), name

    def test_the_open_book_rule_is_kept(self):
        for name in ("strategic_ledger.gd", "diplomatic_ledger.gd"):
            body = _func(_read(SCRIPTS / name), "_update_tab_highlights")
            assert "Utils.mark_active_tab(tab_buttons[i], i == current_tab, _active_tab_style)" in body
            assert "Utils.tint_tab(tab_buttons[i], i == current_tab)" in body


# ═══════════════════════════════════════════════════════════════════════════
# The war room
# ═══════════════════════════════════════════════════════════════════════════


class TestTheDesk:
    def test_the_desk_is_one_switch_and_bitmap_only(self):
        src = _read(SCENES / "map_renderer_base.gd")
        assert "const DESK_SURFACE := true" in src
        body = _func(src, "_create_scene_layers")
        pinned = body.index("viewport_background.color = BITMAP_LETTERBOX_COLOR")
        desk = body.index("desk_surface = _make_desk_surface() if (_bitmap_mode and DESK_SURFACE) else null")
        assert desk > pinned, "the desk lies over the pinned parchment, never before its assignment"
        assert body.index("world_layer.add_child(sheet_shadow)") < body.index("world_layer.add_child(visual_map_layer)")
        assert body.index("world_layer.add_child(sheet_neatline)") > body.index("world_layer.add_child(visual_map_layer)")

    def test_nothing_on_the_desk_takes_the_mouse(self):
        src = _read(SCENES / "map_renderer_base.gd")
        for fn in ("_make_desk_surface", "_make_sheet_shadow", "_make_sheet_neatline"):
            body = _func(src, fn)
            assert body.count("MOUSE_FILTER_IGNORE") >= 1, fn
        assert "rule.mouse_filter = Control.MOUSE_FILTER_IGNORE" in _func(src, "_make_sheet_neatline")

    def test_the_desk_is_the_tracked_leather(self):
        src = _read(SCENES / "map_renderer_base.gd")
        assert "uniform sampler2D leather : source_color" in src
        assert 'const UI_LEATHER := "res://assets/textures/fabric_leather_01_diff_1k.jpg"' in _read(SCRIPTS / "utils.gd")
        assert "load(Utils.UI_LEATHER)" in _func(src, "_make_desk_surface")


class TestTheCommandWindow:
    def test_the_window_wears_the_frame_over_its_leather(self):
        text = _read(SCENES / "main.tscn")
        body = _sub_resources(text)["GiltFrame_command"][1]
        assert 'texture = ExtResource("10_leather")' in body and "weight = 1" in body
        assert 'theme_override_styles/panel = SubResource("GiltFrame_command")' in text

    def test_the_header_is_one_band_and_the_paths_are_kept(self):
        """The header lost its box in a box; every node the script reads is
        where it was (tests/test_ui2c_global_text_size.py holds the paths)."""
        text = _read(SCENES / "main.tscn")
        assert 'theme_override_styles/panel = SubResource("StyleBoxFlat_header")' in text
        assert 'theme_type_variation = &"HudTitle"\ntext = "IMPERIAL COMMAND"' in text
        main = _read(SCRIPTS / "main.gd")
        assert "Utils.apply_stepper_button(scale_up_button)" in main
        assert "Utils.apply_stepper_button(scale_down_button)" in main
        assert 'Utils.apply_icon_only_button(minimize_button, Utils.ICON_PHOSPHOR + "caret-down.svg")' in main

    def test_the_header_keeps_its_side_inset(self):
        """At Interface Scale 2.0 the Table lesson's card covers the window's
        top right; a narrower inset let the status row reflow under it."""
        body = _sub_resources(_read(SCENES / "main.tscn"))["StyleBoxFlat_header"][1]
        assert "content_margin_left = 12.0" in body and "content_margin_right = 12.0" in body

    def test_a_spent_day_makes_end_turn_the_primary(self):
        body = _func(_read(SCRIPTS / "main.gd"), "_note_the_end_of_the_day")
        # Session UI-2: End Turn wears its own seal-rimmed step every day.
        assert '&"PrimaryCaptionButton" if spent else &"EndTurnButton"' in body
        assert 'end_turn_button.remove_theme_color_override("font_color")' in body
        assert 'add_theme_color_override("font_color"' not in body, "an override would beat the step's words"
        text = _read(SCENES / "main.tscn")
        block = text[text.index('[node name="EndTurnButton"'):].split("[node", 2)[1]
        assert 'theme_type_variation = &"EndTurnButton"' in block


# ═══════════════════════════════════════════════════════════════════════════
# The dressed page
# ═══════════════════════════════════════════════════════════════════════════


class TestTheDressedPage:
    def test_the_marks_are_empty_tags(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert 'const CARD_CLOSE := "[bgcolor=#00000000][/bgcolor]"' in utils
        assert 'return "[fgcolor=#" + tone + "00][/fgcolor]"' in _func(utils, "card_open")

    def test_the_three_books_take_the_underlay(self):
        for name in ("strategic_ledger.gd", "diplomatic_ledger.gd", "marshal_management.gd"):
            assert "Utils.card_page(content_area)" in _func(_read(SCRIPTS / name), "_ready"), name

    def test_every_card_that_opens_closes(self):
        """A builder's opens and closes pair up (an open card would leave the
        underlay drawing nothing for it — the fail-safe — but the pairing is
        the contract)."""
        for name, fn in (("strategic_ledger.gd", "_render_forces"), ("strategic_ledger.gd", "_render_territories"),
                         ("strategic_ledger.gd", "_render_manpower"), ("strategic_ledger.gd", "_render_intel"),
                         ("diplomatic_ledger.gd", "_render_nations"), ("diplomatic_ledger.gd", "_format_vassal_card")):
            body = _func(_read(SCRIPTS / name), fn)
            assert body.count("Utils.card_open(") == body.count("Utils.CARD_CLOSE"), (name, fn)
        treaties = _func(_read(SCRIPTS / "diplomatic_ledger.gd"), "_render_treaties")
        assert treaties.count("Utils.card_open(") == 1 and treaties.count("Utils.CARD_CLOSE") == 2  # two exits
        generals = _read(SCRIPTS / "marshal_management.gd")
        card = _func(generals, "_render_card")
        assert card.count("Utils.CARD_CLOSE") == 1 and "if not opened:" in card
        assert _func(generals, "_render_all_cards").count(", true)") == 2   # the Emperor, the urgent

    def test_the_figure_column_rides_the_economy_book(self):
        body = _func(_read(SCRIPTS / "strategic_ledger.gd"), "_render_economy")
        # Session UI-4 (November 12, 2026): the blind readers asked for "a
        # two-column table with right-aligned figures and color-coded signs" —
        # the books are tables now (label | signed figure | note, a subtotal
        # under each block, Net last), so the figure column is the table's own
        # right-aligned column, not bb_tabulate's spacer; the page's one seam
        # still dresses its headings as it sets the text.
        assert "_econ_table(" in body and "ECON_COLS" in _read(SCRIPTS / "strategic_ledger.gd")
        assert "content_area.text = Utils.dress_heads(bbcode)" in body
        assert "Utils.bb_tabulate(" not in body


# ═══════════════════════════════════════════════════════════════════════════
# Driven: the real scripts, headless
# ═══════════════════════════════════════════════════════════════════════════

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe",
    "godot",
    "godot4",
]


def _engine():
    for candidate in _CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate or "/" in candidate:
            if pathlib.Path(candidate).is_file():
                return candidate
            continue
        found = shutil.which(candidate)
        if found:
            return found
    return None


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, and a skip is not a pass")
    out = tmp_path_factory.mktemp("ui_gilt") / "probe.json"
    env = dict(os.environ, UI_GILT_OUT=str(out))
    env.pop("PYTHONIOENCODING", None)
    proc = subprocess.run(
        [engine, "--headless", "--path", str(PROJECT), "--script", str(PROBE)],
        capture_output=True, text=True, timeout=300, env=env, cwd=str(PROJECT),
        stdin=subprocess.DEVNULL, encoding="utf-8", errors="replace",
    )
    if not out.is_file():
        pytest.fail(f"the probe wrote no result (exit {proc.returncode})\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    return json.loads(out.read_text(encoding="utf-8"))


class TestDriven:
    def test_the_frame_keeps_flats_names_through_a_duplicate(self, probe):
        f = probe["frame"]
        assert f["is_flat"] is False and f["has_border_color"] is True
        assert f["copy_border"] == "cc6666ff" and f["copy_bg"] == "1a334dff"
        assert f["copy_weight"] == 1 and f["copy_margin"] == 20.0

    def test_the_frame_fits_inside_the_tightest_margin(self, probe):
        assert probe["frame"]["thickness"] == [7.0, 5.0, 2.0]
        assert max(probe["frame"]["thickness"]) < 12.0     # the tightest window margin

    def test_the_framed_scenes_load_with_their_own_values(self, probe):
        for name, rec in probe["frame"]["scenes"].items():
            assert rec["script"] == "res://scripts/gilt_frame.gd", name
            assert rec["has_bg"] and rec["has_border"], name
        assert probe["frame"]["scenes"]["strategic_ledger"]["margin_left"] == 20.0
        assert probe["frame"]["scenes"]["war_status_panel"]["weight"] == 2
        assert probe["frame"]["scenes"]["main"]["weight"] == 1

    def test_the_theme_carries_the_kit(self, probe):
        t = probe["theme"]
        assert t["rule_script"] == "res://scripts/gilt_rule.gd" and t["rule_minimum"] == [0.0, 0.0]
        assert t["primary_size"] == 16 and t["primary_caption_size"] == 14
        assert t["primary_variation_of"] == "Button"
        assert t["title_base"] == "res://assets/fonts/Cinzel[wght].ttf"
        for state, m in t["button_margins"].items():
            assert m[0] == 12.0 and m[2] == 12.0 and m[1] + m[3] == 12.0, (state, m)

    def test_the_marks_add_nothing_to_the_words(self, probe):
        c = probe["cards"]
        assert c["parsed_marked"] == c["parsed_bare"] == c["parsed_dressed"]

    def test_the_page_describes_its_own_cards(self, probe):
        assert probe["cards_in"] == [[3, 5, "d9c08c"], [7, 9, "d06e6e"]]

    def test_a_real_page_keeps_one_paragraph_per_newline(self, probe):
        """The underlay's fail-safe: it draws only where this holds — chips,
        flags, portraits and links included."""
        assert probe["cards"]["paragraphs"] == probe["page_newlines"] + 1

    def test_the_underlay_is_a_quiet_child(self, probe):
        c = probe["cards"]
        assert c["underlay"] and c["underlay_ignores_mouse"] and c["underlay_behind"]
        assert c["underlay_minimum"] == [0.0, 0.0]
        assert c["side_margins"] == [12.0, 12.0]
        assert c["vertical_margins"] == [0.0, 0.0], "no line moves down: the whole-line rules read the top margin"
        assert c["attach_is_idempotent"] is True

    def test_the_figure_column_is_invisible(self, probe):
        f = probe["figures"]
        assert f["parsed_after"] == f["parsed_before"]
        assert f["spacers"] == 8 and f["features"] == 8      # six books' lines and two regions
        assert f["link_line_untouched"] is True
        assert f["single_line_runs_untouched"] is True

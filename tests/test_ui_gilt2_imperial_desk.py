"""Session UI-2 (November 11, 2026) — "The Imperial Desk": the second visual pass.

The user's word: raise the client from the last pass's own 7/10 to 9/10 — every
surface, nothing assumed, assets found (licence-checked) or coded. Rules in
docs/SYSTEMS_REFERENCE.md §213; the record docs/UI_VISUAL_FOUNDATION_SPEC.md §10.

The source half pins the kit's contracts (the button face, the steps, the
glyphs and the eagle tracked with their licences, the top bar's routes, the
map's plaques, the books' kit, the letters' fit, Reduce motion, the Auto HUD
band, the 32:9 derivation). The driven half runs tools/ui_gilt2_probe.gd
headless and SKIPS when the engine is missing — a skip is not a pass.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
THEME = PROJECT / "ui" / "main_theme.tres"
GLYPHS = PROJECT / "assets" / "ui" / "icons" / "glyphs"
EAGLE = PROJECT / "assets" / "ui" / "ornaments" / "eagle_empire.svg"
PROBE = REPO / "tools" / "ui_gilt2_probe.gd"

GLYPH_NAMES = {
    "gold", "income", "dp", "authority", "threat", "turn", "actions", "admin", "foot", "horse", "guns",
    "strength", "morale", "trust", "stability", "supply", "garrison", "tactical", "shock", "defense",
    "logistics", "administration", "command", "fleet", "sail", "envoy", "letter", "glory", "cabinet",
    "war", "intel", "build", "march", "medal", "drum", "europe",
}


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    at = src.index(f"func {name}(")
    ends = [i for i in (src.find("\nfunc ", at + 10), src.find("\nstatic func ", at + 10)) if i != -1]
    return src[at:min(ends) if ends else len(src)]


def _tracked(path: pathlib.Path) -> bool:
    rel = path.relative_to(REPO).as_posix()
    out = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=str(REPO),
                         capture_output=True, text=True)
    return out.returncode == 0


class TestTheButtonFace:
    def test_the_face_is_a_scripted_stylebox_with_flats_names(self):
        src = _read(SCRIPTS / "gilt_button.gd")
        assert src.startswith("@tool\nextends StyleBox")
        assert not re.search(r"(?m)^class_name ", src)   # its header comment names the rule
        for prop in ("bg_color", "bg_foot", "border_color", "highlight", "glow", "inset", "dashed"):
            assert f"var {prop}" in src, prop
        assert "UiSettings.get_high_contrast()" in src      # High contrast drops the gradient

    def test_every_button_state_wears_it_and_disabled_is_dashed(self):
        text = _read(THEME)
        assert '[ext_resource type="Script" path="res://scripts/gilt_button.gd" id="6_button"]' in text
        for state in ("normal", "hover", "pressed", "disabled"):
            sid = re.search(rf'(?m)^Button/styles/{state} = SubResource\("([^"]+)"\)', text).group(1)
            block = re.search(rf'\[sub_resource type="StyleBox" id="{sid}"\]\n(.*?)\n\n', text, re.S).group(1)
            assert block.startswith('script = ExtResource("6_button")'), state
        sid = re.search(r'(?m)^Button/styles/disabled = SubResource\("([^"]+)"\)', text).group(1)
        assert "dashed = true" in re.search(rf'id="{sid}"\]\n(.*?)\n\n', text, re.S).group(1)

    def test_the_new_steps(self):
        text = _read(THEME)
        for step, size in (("EndTurnButton", 14), ("ParchmentButton", 16), ("StatFigure", 24), ("Figure", 16)):
            assert f"{step}/font_sizes/font_size = {size}" in text, step
        assert 'ParchmentButton/styles/normal = SubResource("StyleBox_parchment")' in text
        assert 'EndTurnButton/styles/normal = SubResource("StyleBox_end_turn")' in text
        fig = re.search(r'id="FontVariation_figures"\]\n(.*?)\n\n', text, re.S).group(1)
        assert "1819178349: 1" in fig and "1953396077: 1" in fig        # lnum, tnum

    def test_end_turn_is_always_its_own_step(self):
        main = _read(SCRIPTS / "main.gd")
        body = _func(main, "_note_the_end_of_the_day")
        assert '&"PrimaryCaptionButton" if spent else &"EndTurnButton"' in body
        assert 'theme_type_variation = &"EndTurnButton"' in _read(SCENES / "main.tscn")


class TestTheGlyphsAndTheEagle:
    def test_every_glyph_is_shipped_tracked_and_mipmapped(self):
        names = {p.stem for p in GLYPHS.glob("*.svg")}
        assert names == GLYPH_NAMES
        for name in GLYPH_NAMES:
            svg = GLYPHS / f"{name}.svg"
            imp = GLYPHS / f"{name}.svg.import"
            assert _tracked(svg) and _tracked(imp), name
            assert "mipmaps/generate=true" in _read(imp), name
            assert 'fill="#fff"' in _read(svg), name      # white: tinted by modulate

    def test_each_glyph_names_its_author_and_the_licence(self):
        manifest = _read(GLYPHS / "GLYPHS.txt")
        lic = _read(REPO / "THIRD_PARTY_LICENSES.md")
        assert "CC BY 3.0" in manifest
        for name in GLYPH_NAMES:
            assert re.search(rf"(?m)^{name}\.svg\t\S+\t\S+$", manifest), name
        assert "assets/ui/icons/glyphs/" in lic

    def test_the_eagle_is_public_domain_and_recorded(self):
        assert _tracked(EAGLE) and _tracked(EAGLE.with_name("eagle_empire.svg.import"))
        lic = _read(REPO / "THIRD_PARTY_LICENSES.md")
        assert "eagle_empire.svg" in lic and "PD-self" in lic and "PD-Art" in lic
        assert "fill:#ffffff" in _read(EAGLE)      # the detail white, tinted gilt


class TestTheTopBar:
    def test_every_figure_opens_its_book(self):
        bar = _read(SCRIPTS / "top_bar.gd")
        groups = _func(bar, "_build_desk_groups")
        for route in ("open_ledger_to_tab(2)", "open_cabinet()", "open_ledger_to_tab(0)",
                      'open_diplomatic_ledger_review("ledger_balance")', '_on_button_pressed("dispatch")'):
            assert route in groups, route
        assert "func open_to_balance(api_client):" in _read(SCRIPTS / "diplomatic_ledger.gd")
        assert "top_bar.update_treasury(" in _func(_read(SCRIPTS / "main.gd"), "_update_gold_display")

    def test_the_bar_sheds_detail_rather_than_overflow(self):
        bar = _read(SCRIPTS / "top_bar.gd")
        # Session UI-4: two more steps, the date's own (its season word, then the turn alone)
        assert "const _FIT_STEPS := 8" in bar
        fit = _func(bar, "_fit_right_cluster")
        assert "layout.get_combined_minimum_size().x + 16.0 <= view_w" in fit
        assert "offset_bottom = 36.0" in _read(SCENES / "top_bar.tscn")        # the bar stays 36 px


class TestTheMapsMarkers:
    def test_the_plaques(self):
        plaque = _read(SCRIPTS / "map_plaque.gd")
        assert "enum Kind { GARRISON, FOG, SAIL, NAME }" in plaque
        r = _read(SCENES / "map_renderer_base.gd")
        assert "MapPlaque.Kind.GARRISON" in _func(r, "_create_garrison_node")
        assert "MapPlaque.Kind.FOG" in _func(r, "_create_fogged_force_nodes")
        assert "MapPlaque.Kind.SAIL" in _func(r, "_update_fleet_pieces")
        assert "_nameplate(" in _func(r, "_create_marshal_nodes")
        assert "name_rows(xs, ws" in _func(r, "_create_marshal_nodes")


class TestTheBooks:
    def test_the_kit(self):
        u = _read(SCRIPTS / "utils.gd")
        for fn in ("flatten_tables", "dress_heads", "bb_table", "bb_relation_meter", "bb_portrait_row",
                   "bb_meter", "bb_badge", "bb_glyph", "motion_open", "watch_motion"):
            assert f"static func {fn}(" in u, fn
        assert 'const TITLE_FONT := "res://ui/title_face.tres"' in u      # no brackets in a [font=] path
        assert "Utils.flatten_tables(_label.text)" in _read(SCRIPTS / "card_underlay.gd")

    def test_the_chip_is_a_rimmed_cell(self):
        u = _read(SCRIPTS / "utils.gd")
        assert 'const CHIP_OPEN_HEAD := "[table=1,baseline][cell border=#"' in u
        assert "CHIP_OPEN_HEAD + text_hex + CHIP_RIM_ALPHA" in _func(u, "bb_button_chip")

    def test_the_pages_wear_it(self):
        assert "func _set_strip() -> void:" in _read(SCRIPTS / "strategic_ledger.gd")
        assert "Utils.bb_portrait_row(portrait, sheet, card_tone)" in _read(SCRIPTS / "marshal_management.gd")
        dl = _read(SCRIPTS / "diplomatic_ledger.gd")
        assert "Utils.bb_relation_meter(relation, 100, 7)" in dl and "Utils.bb_badge(" in dl
        assert "MASTHEAD_FONT" in _read(SCRIPTS / "gazette_view.gd")


class TestTheLettersAndThePopups:
    def test_every_letter_fits_what_it_holds(self):
        src = _read(SCRIPTS / "incoming_proposal_popup.gd")
        for fn in ("show_proposal", "refit"):
            body = _func(src, fn)
            assert body.index("Utils.clamp_centered_panel($PanelContainer)") < body.index("_fit_to_letter()"), fn
        dress = _func(src, "_dress_letter")
        assert 'b.theme_type_variation = &"ParchmentButton"' in dress
        assert 'add_theme_color_override("default_color", Color.html(Utils.INK_BODY))' in dress

    def test_the_ceremonies(self):
        assert "func _show_settings_page(on: bool) -> void:" in _read(SCRIPTS / "pause_menu.gd")
        assert "func _build_filigree" not in _read(SCRIPTS / "battle_diorama.gd")
        assert "Utils.gilt_frame(WOOD_BG" in _read(SCRIPTS / "battle_diorama.gd")
        ce = _read(SCRIPTS / "campaign_end.gd")
        assert "func _ensure_crest() -> void:" in ce and "func _fit_card() -> void:" in ce
        assert "load(Utils.EAGLE)" in _read(SCRIPTS / "main_menu.gd")


class TestMotionAndTheBand:
    def test_reduce_motion(self):
        s = _read(SCRIPTS / "ui_settings.gd")
        assert "static func get_reduce_motion() -> bool:" in s
        assert '"ReduceMotionToggle"' in _read(SCRIPTS / "settings_panel.gd")
        assert 'UiSettings._cfg.set_value("display", "reduce_motion", true)' in _read(
            REPO / "tools" / "iq10_surface_screenshot.gd")
        assert "Utils.watch_motion(instance)" in _read(SCRIPTS / "dialog_manager.gd")
        assert "Utils.watch_motion(node)" in _read(SCRIPTS / "top_bar.gd")

    def test_auto_is_the_default_and_both_twins_derive_1_60(self):
        s = _read(SCRIPTS / "ui_settings.gd")
        assert 'const HUD_WIDTHS := ["auto", "full", "16:9", "centred"]' in s
        assert 'const DEFAULT_HUD_WIDTH := "auto"' in s and "const ULTRA_WIDE_BONUS := 0.65" in s   # Session UI-4: 0.45 -> 0.65
        sys.path.insert(0, str(REPO / "tools"))
        from uxr0_readability_report import derive_ui_scale
        # Session UI-4: the 32:9 term 0.45 -> 0.65 — the user's panel derives 1.80
        assert derive_ui_scale(5120, 1440) == pytest.approx(1.8)
        assert derive_ui_scale(1920, 1080) == pytest.approx(1.0)


# ═══════════════════════════════════════════════════════════════════════════
# DRIVEN — tools/ui_gilt2_probe.gd, headless
# ═══════════════════════════════════════════════════════════════════════════

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe",
    "godot", "godot4",
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
    out = tmp_path_factory.mktemp("ui_gilt2") / "probe.json"
    env = dict(os.environ, UI_GILT2_OUT=str(out))
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
    def test_the_face_keeps_flats_names_through_a_duplicate(self, probe):
        b = probe["button"]
        assert b["is_flat"] is False and b["has_border_color"] is True
        assert b["copy_border"] == "cc6666ff" and b["copy_bg"] == "1a334dff" and b["copy_margin"] == 12.0
        assert all(f["scripted"] for f in b["faces"].values())
        assert b["faces"]["disabled"]["dashed"] is True and b["faces"]["normal"]["dashed"] is False
        assert b["parchment_scripted"] is True
        assert b["steps"] == {"EndTurnButton": 14, "ParchmentButton": 16, "StatFigure": 24, "Figure": 16}

    def test_co_located_names_never_touch(self, probe):
        zig, column, pair = probe["rows"]
        assert not zig["overlap"] and not column["overlap"] and not pair["overlap"]
        assert sorted(int(r[0]) for r in zig["rows"]) == [0, 0, 1]          # the zig-zag
        assert sorted(int(r[0]) for r in column["rows"]) == [0, 1, 2]       # the column
        assert len({float(r[1]) for r in column["rows"]}) == 1              # one centre

    def test_a_table_is_one_paragraph_of_its_page(self, probe):
        t = probe["tables"]
        assert t["raw_newlines"] > t["flat_newlines"]                       # the cell holds lines
        assert t["paragraphs"] == t["flat_newlines"] + 1                    # the underlay's precondition
        assert t["parsed_has_words"] is True

    def test_the_heads_meters_and_chips(self, probe):
        h = probe["heads"]
        assert "res://ui/title_face.tres" in h["dressed"] and "FORCES" in h["dressed"]
        assert "═══ FORCES" not in h["dressed"] and "THE SEA" in h["dressed"]
        assert "swatch.png" in h["dressed"]                                  # the bare rule a hairline
        assert h["meter"].count("[img") == 2 and "width=30 " in h["meter"]
        assert h["relation"].count("[img") == 4                              # track, hostile, nought, track
        # Session UI-4: a live chip's rim at full strength (b0 → ff) — beside a
        # locked chip, which has no rim at all
        assert h["chip"].startswith("[table=1,baseline][cell border=#d9c08cff bg=#233043][url=order:drill:Ney]")
        # Session UI-4: a locked chip has no rim and no ground (the cell kept,
        # transparent, so a row never jumps) and a lock before its name
        assert h["chip_off"].startswith("[table=1,baseline][cell border=#00000000 bg=#00000000]")
        assert "lock-simple.svg" in h["chip_off"]
        assert h["flatten"] == "a\n[table=2][cell]x y[/cell][cell]z[/cell][/table]\nb"

    def test_the_band_and_the_derivation(self, probe):
        b = probe["band"]
        assert b["default_width"] == "auto"
        assert b["auto_std"] == [0.0, 1600.0]
        # Session UI-4, the user's "Screen edges": Auto on a 32:9 view stands at
        # the edges while the map fills the width (the default since UI-3);
        # the 16:9 zone is "16:9"'s, and Auto's with the whole sheet
        assert b["auto_wide"] == [0.0, 3200.0]
        # Session UI-4: the 32:9 term 0.65 — the user's panel derives 1.80
        assert b["derived_5120"] == pytest.approx(1.8) and b["derived_1920"] == pytest.approx(1.0)


class TestWhatTheInstrumentsCaught:
    """The after-build shoot's instruments caught four things the build had
    put in (November 12, 2026); each is fixed at its cause and pinned here."""

    def test_the_objections_even_grid_never_adds_a_row(self):
        """At Interface Scale 2.0 the grid pushed a long answer onto a row of
        its own and the dialog stood over the top bar's strip (the frames'
        clamp-band pin): the answers go even only when every one fits half.

        Session UI-4 (November 12, 2026): the readers asked for the answers
        "aligned in a grid" — the grid is ALWAYS even now (an `AnswerGrid` of
        two columns), a long answer wrapping inside its half instead of taking
        a row of its own; so the natural-width fallback is retired."""
        src = _read(SCRIPTS / "objection_dialog.gd")
        dress = _func(src, "_dress_answers")
        assert 'grid.name = "AnswerGrid"' in dress and "grid.columns = 2" in dress
        assert "btn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART" in dress
        assert "custom_minimum_size.x = 0.0" in _func(src, "_even_the_answers")

    def test_a_red_figure_reads_on_the_dark_ground(self):
        """The figures took the `Figure` step (16 px, body type): the alert red
        read 4.36 : 1 on the bar and 4.24 on a page; its text tone reads 4.5+."""
        sys.path.insert(0, str(REPO / "tools"))
        import uxr2b_contrast_report as CR  # noqa: E402
        utils = _read(SCRIPTS / "utils.gd")
        assert "const UI_ALERT_TEXT := Color(0.871, 0.341, 0.341, 1.0)" in utils
        for bg in ("0b0e18", "0c0f19", "0e121c", "1d171c"):
            assert CR.ratio((0.871, 0.341, 0.341), CR._hex(bg)) >= CR.BODY_FLOOR, bg
        tb = _read(SCRIPTS / "top_bar.gd")
        assert 'threat_label.add_theme_color_override("font_color", Utils.UI_ALERT_TEXT)' in tb
        assert "if value < 50:\n\t\tcolour = Utils.UI_ALERT_TEXT" in tb
        assert "else Utils.UI_ALERT_TEXT}" in _read(SCRIPTS / "strategic_ledger.gd")

    def test_a_chip_is_measured_on_its_own_ground(self):
        """The contrast census read a chip's ink against its own [bgcolor];
        the rimmed chip is a one-cell table, and the harness reads that too
        (the Correspondence's gold chips read 1.06 : 1 against the paper
        without it). The dimmed cell keeps the exempt pill's ground."""
        harness = _read(REPO / "tools" / "iq10_surface_screenshot.gd")
        assert "var _cell_chip_re := RegEx.create_from_string(" in harness
        assert 'var rest := _cell_chip_re.sub(_chip_re.sub(src, "", true), "", true)' in harness
        sys.path.insert(0, str(REPO / "tools"))
        import uxr2b_contrast_report as CR  # noqa: E402
        utils = _read(SCRIPTS / "utils.gd")
        # Session UI-4: the locked chip has no ground (a transparent cell, a
        # lock before its name) — the exempt pair follows it.
        assert 'const CHIP_DIM_BG := "00000000"' in utils
        assert CR.DISABLED_CHIP == ("00000000", "6f7480ff")

    def test_the_new_greys_are_named_tokens(self):
        """The consistency census's R4: no one-off grey in a surface's own files."""
        utils = _read(SCRIPTS / "utils.gd")
        for token in ("UI_PLAQUE_DIM_INK", "UI_PLAQUE_FADED_RIM", "UI_PLAQUE_FADE_TO", "COLOR_BADGE_QUIET"):
            assert f"const {token} :=" in utils, token
        renderer = _read(SCENES / "map_renderer_base.gd")
        assert "const PLAQUE_DIM_INK := Utils.UI_PLAQUE_DIM_INK" in renderer
        assert "Color(0.62, 0.62, 0.64, 0.55)" not in renderer and "Color(0.5, 0.5, 0.5)" not in renderer
        assert '"6b6f80"' not in _read(SCRIPTS / "region_panel.gd")


class TestTheHeaderFolds:
    """Plan 1d / the 2.0 layout: under 600 logical px of height the command
    window's header folds into one band (the blind readers: at Interface Scale
    2.0 the window covered the map); the scene's node paths stay the scene's."""

    def test_the_fold_moves_two_controls_and_hides_the_name(self):
        main = _read(SCRIPTS / "main.gd")
        assert "const HEADER_FOLD_BELOW := 600.0" in main
        body = _func(main, "_fold_header")
        assert "var fold := size.y < HEADER_FOLD_BELOW" in body
        assert "size_box.reparent(status, false)" in body and "minimize_button.reparent(status, false)" in body
        assert "size_box.reparent(title_row, false)" in body and "minimize_button.reparent(title_row, false)" in body
        assert "title_row.visible = not fold" in body
        # it runs on every relayout, beside the log's floor
        relayout = _func(main, "_relayout_terminal")
        assert relayout.index("_log_floor()") < relayout.index("_fold_header()")
        scene = _read(SCENES / "main.tscn")
        assert 'parent="BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/TitleRow"' in scene


class TestTheFiguresPointOnlyOnceLaidOut:
    """DDB-54's driven pin caught it: a cursor shape written during the top
    bar's _ready re-picked the hover while every child stood at (0, 0); the
    gear took a stale hover and its tooltip ate the first Esc."""

    def test_the_pointing_hand_is_armed_a_frame_later(self):
        tb = _read(SCRIPTS / "top_bar.gd")
        for name in ("_group", "_wire_figure"):
            body = _func(tb, name)
            assert "_pointer_controls.append(" in body, name
            assert "mouse_default_cursor_shape" not in body, name
        arm = _func(tb, "_arm_pointers")
        assert "await get_tree().process_frame" in arm
        assert "mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND" in arm
        assert "_arm_pointers.call_deferred()" in _func(tb, "_build_desk_groups")


class TestTheCompactViewAndTheInCellTag:
    """The frames' pins at Interface Scale 2.0 (800 x 450 logical) and the A3
    frames caught them: the builders' arms rows, figure strips and spacing
    pushed answers, terms and a door below the fold; a badge (a one-cell
    table) inside a table cell printed one letter a line."""

    def test_the_compact_view_is_one_rule(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert "const COMPACT_BELOW := 600.0" in utils
        body = _func(utils, "compact_view")
        assert "get_visible_rect().size.y < COMPACT_BELOW" in body
        for name in ("capture_choice_dialog.gd", "commitment_paradox_popup.gd", "interrupt_popup.gd",
                     "marshal_petition_dialog.gd", "proclamation_popup.gd", "redemption_dialog.gd",
                     "reward_dialog.gd", "sabotage_discovery_popup.gd", "vassal_rebellion_popup.gd"):
            assert "row.visible = row.get_child_count() > 0 and not Utils.compact_view()" in _read(SCRIPTS / name), name
        tut = _read(SCRIPTS / "tutorial_overlay.gd")
        assert "var compact := Utils.compact_view()" in tut
        assert '_paragraphs(str(step["body"]), "\\n" if compact else "\\n\\n"))' in tut

    def test_a_badge_inside_a_cell_is_an_inline_tag(self):
        utils = _read(SCRIPTS / "utils.gd")
        tag = _func(utils, "bb_tag")
        assert "[bgcolor=#" in tag and "[table" not in tag
        sheet = _func(_read(SCRIPTS / "marshal_management.gd"), "_render_card")
        assert "Utils.bb_tag(unit_type, arm_tone)" in sheet
        ledger = _read(SCRIPTS / "strategic_ledger.gd")
        # Session UI-5 interim fix (Nov 13): still an inline tag, now inside the cell's
        # hover (the compact "OK · cap 60k"; the full sentence rides the hint).
        assert "var supply_cell = Utils.bb_hint(Utils.bb_tag(supply_status, supply_tone)" in ledger
        assert "Utils.bb_tag(vis_label, vis_tone)])" in ledger

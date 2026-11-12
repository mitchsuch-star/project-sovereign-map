"""Session UI-3 (November 12, 2026) — past 7: the folds, the filled ultrawide, the
settlement's one scroll, the windows that fit.

The user's ruling at the session's head: "Fold, a switch restores." Explanations
leave the face of the pages — a page's lead-in behind an ⓘ, what a control does
as its hover (its figures kept on the face), long counsel opened from its first
sentence — and Settings → INTERFACE → Explanations: On the page prints every word
exactly as before. Levers 2–4 the user delegated ("DO BEST THING FOR GAME"): the
map fills a very wide screen's width (⌂ toggles the whole sheet), the settlement
table is one scroll with each court's acts in its card, reading windows fit their
content, the books take the room, crowded name plates gather at the whole-sheet
view. Rules in docs/SYSTEMS_REFERENCE.md §214; the record
docs/UI_VISUAL_FOUNDATION_SPEC.md §11.

The source half pins the kit and where it is used. The driven half runs
tools/ui_gilt3_probe.gd headless and SKIPS when the engine is missing — a skip is
not a pass.
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
TOOLS = REPO / "tools"
PROBE = TOOLS / "ui_gilt3_probe.gd"


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    at = src.index(f"func {name}(")
    ends = [i for i in (src.find("\nfunc ", at + 10), src.find("\nstatic func ", at + 10)) if i != -1]
    return src[at:min(ends) if ends else len(src)]


# ═══════════════════════════════════════════════════════════════════════════
# The switch and the kit
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSwitch:
    SRC = _read(SCRIPTS / "ui_settings.gd")

    def test_explanations_fold_by_default_and_the_page_restores(self):
        assert 'const EXPLANATIONS := ["folded", "page"]' in self.SRC
        assert 'const DEFAULT_EXPLANATIONS := "folded"' in self.SRC
        assert '_config().get_value("display", "explanations", DEFAULT_EXPLANATIONS)' in self.SRC

    def test_the_wide_map_fills_by_default_and_reset_layout_restores_it(self):
        assert 'const WIDE_MAPS := ["fill", "sheet"]' in self.SRC
        assert 'const DEFAULT_WIDE_MAP := "fill"' in self.SRC
        assert "set_wide_map(DEFAULT_WIDE_MAP)" in _func(self.SRC, "reset_layout")

    def test_settings_carries_both_choices(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        assert '_explanations.name = "ExplanationsOption"' in src
        assert '_wide_map.name = "WideMapOption"' in src
        body = _func(src, "_on_explanations_selected")
        assert "UiSettings.set_explanations(mode)" in body
        assert "Utils.notify_explanations_changed()" in body
        assert "wide_map_changed.emit(mode)" in _func(src, "_on_wide_map_selected")
        assert "wide_map_changed.emit(UiSettings.get_wide_map())" in _func(src, "_on_reset_layout")

    def test_a_settings_hint_becomes_its_controls_hover_and_the_keys_stay(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        body = _func(src, "_add_hint")
        assert "_hints_fold" in body and "prev is BaseButton or prev is HBoxContainer" in body
        assert "mark.tooltip_text = text" in body
        controls = _func(src, "_build_controls_section")
        assert controls.index("_hints_fold = false") < controls.index("_add_hint(")
        assert controls.rindex("_add_hint(") < controls.index("_hints_fold = true")

    def test_the_host_relays_the_wide_map(self):
        assert "signal wide_map_changed(mode)" in _read(SCRIPTS / "pause_menu.gd")
        main = _read(SCRIPTS / "main.gd")
        assert "pause_menu.wide_map_changed.connect(_on_wide_map_changed)" in main
        assert "map_area.apply_boot_view()" in _func(main, "_on_wide_map_changed")


class TestTheKit:
    SRC = _read(SCRIPTS / "utils.gd")

    def test_the_fold_helpers_exist(self):
        for name in ("explanations_folded", "clean_tip", "bb_hint", "bb_hints", "bb_info_glyph",
                     "is_note_meta", "note_is_open", "toggle_note", "reset_notes", "show_note",
                     "note_link", "bb_note", "lead_mark", "bb_lead", "explain_tip",
                     "on_explanations_changed", "notify_explanations_changed", "restore_label_scroll",
                     "set_reading_share", "fit_reading_window"):
            assert f"static func {name}(" in self.SRC, name

    def test_a_hint_is_written_by_one_road(self):
        """Every `[hint=` in the client is Utils.bb_hint's: the tip is cleaned
        there (a bracket ends the tag, an apostrophe opens a quoted value)."""
        for path in sorted(SCRIPTS.glob("*.gd")) + sorted(SCENES.glob("*.gd")):
            text = _read(path)
            if path.name == "utils.gd":
                assert text.count('"[hint="') == 1, path.name
                continue
            assert "[hint=" not in text, path.name

    def test_a_chip_carries_its_hover_inside_its_link(self):
        body = _func(self.SRC, "bb_button_chip")
        assert 'icon_path := "", tip := ""' in body
        assert body.index("inner = bb_hint(inner, tip)") < body.index('"][url=" + url_meta + "]"')
        assert 'tip := ""' in _func(self.SRC, "bb_chip_disabled")

    def test_the_reading_share_is_capped_and_never_raises_a_grip(self):
        body = _func(self.SRC, "clamp_centered_panel")
        assert 'panel.has_meta("clamp_reading_share") and not panel.has_meta("clamp_user_size")' in body
        assert "minf(r_share.x * view.x, r_max.x)" in body
        # the Cabinet's fraction is untouched (pinned by S14G-22)
        assert 'panel.has_meta("clamp_ceiling_fraction") and not panel.has_meta("clamp_user_size")' in body

    def test_the_info_glyph_is_shipped_and_mipmapped(self):
        assert 'const INFO_GLYPH := ICON_PHOSPHOR + "info.svg"' in self.SRC
        imp = _read(PROJECT / "assets" / "ui" / "icons" / "phosphor" / "info.svg.import")
        assert "mipmaps/generate=true" in imp


# ═══════════════════════════════════════════════════════════════════════════
# Where the folds stand (the readers' surfaces and the class)
# ═══════════════════════════════════════════════════════════════════════════

FOLDED = {
    "diplomatic_ledger.gd": ("Utils.lead_mark(", "Utils.show_note(", "Utils.on_explanations_changed("),
    "region_panel.gd": ("Utils.lead_mark(", "Utils.bb_lead(", "Utils.on_explanations_changed("),
    "war_detail_popup.gd": ("Utils.bb_lead(", "Utils.note_link(", "Utils.on_explanations_changed("),
    "dispatch_view.gd": ("Utils.lead_mark(", "Utils.bb_lead(", "Utils.set_reading_share(", "Utils.fit_reading_window("),
    "gazette_view.gd": ("Utils.lead_mark(", "Utils.bb_lead(", "Utils.set_reading_share(", "Utils.fit_reading_window("),
    "strategic_ledger.gd": ("Utils.lead_mark(", "Utils.bb_lead(", "Utils.BOOK_SHARE"),
    "marshal_management.gd": ("Utils.lead_mark(", "Utils.bb_lead(", "Utils.BOOK_SHARE"),
    "incoming_proposal_popup.gd": ("Utils.explain_tip(", "Utils.bb_note(", "Utils.on_explanations_changed("),
    "diplomacy_wizard.gd": ("Utils.explain_tip(", "Utils.on_explanations_changed("),
    "mailbox_panel.gd": ("Utils.set_reading_share(", "Utils.on_explanations_changed("),
}


@pytest.mark.parametrize("script", sorted(FOLDED))
def test_each_folded_surface_uses_the_kit(script):
    src = _read(SCRIPTS / script)
    for needle in FOLDED[script]:
        assert needle in src, f"{script}: {needle}"


@pytest.mark.parametrize("script", ["diplomatic_ledger.gd", "region_panel.gd", "war_detail_popup.gd",
                                    "dispatch_view.gd", "strategic_ledger.gd", "marshal_management.gd",
                                    "incoming_proposal_popup.gd"])
def test_a_note_click_is_routed_before_anything_else_reads_the_meta(script):
    src = _read(SCRIPTS / script)
    assert "Utils.is_note_meta(" in src and "Utils.toggle_note(" in src, script


def test_the_lead_ins_stay_in_their_functions():
    """R159's lines (each screen names its mechanic) keep their words in the
    source — the ⓘ carries them folded, the page prints them."""
    assert "Every court of Europe" in _read(SCRIPTS / "diplomatic_ledger.gd")
    assert "the price of peace" in _read(SCRIPTS / "war_detail_popup.gd")
    assert "One province — who holds it" in _read(SCRIPTS / "region_panel.gd")
    assert "before you spend a single order" in _read(SCRIPTS / "dispatch_view.gd")
    assert "The capital's press" in _read(SCRIPTS / "gazette_view.gd")
    assert "only glory answers envy" in _read(SCRIPTS / "marshal_management.gd")


def test_the_petition_carries_its_figures_from_the_priced_terms():
    src = _read(REPO / "backend" / "game_logic" / "vassal.py")
    assert 'terms["grant_figures"]' in src and 'terms["refuse_figures"]' in src


class TestTheInterimReadingsFixes:
    """What the interim blind reading named, fixed at its cause before the final
    reading (`SYSTEMS_REFERENCE.md` §214, "The interim reading and its fixes")."""

    def test_one_sentence_finder_serves_the_settlement_and_the_cabinet(self):
        u = _read(SCRIPTS / "utils.gd")
        assert "static func first_sentence_end(text: String) -> int:" in u
        popup = _read(SCRIPTS / "proposal_confirm_popup.gd")
        body = popup.split("func _first_sentence_end(", 1)[1].split("\nfunc ", 1)[0]
        assert "return Utils.first_sentence_end(text)" in body

    def test_the_cabinet_counsel_opens_from_its_first_sentence(self):
        wiz = _read(SCRIPTS / "diplomacy_wizard.gd")
        assert 'const COUNSEL_NOTE := "cabinet.counsel"' in wiz
        assert "assessment_panel.meta_clicked.connect(_on_assessment_meta)" in wiz
        render = wiz.split("func _render_preview(", 1)[1].split("\nfunc ", 1)[0]
        assert "Utils.first_sentence_end(str(recommendation))" in render
        # On the page (or opened) the old lines print in their old order
        assert render.index('"]Recommendation: " + recommendation + "[/color]\\n"') \
            < render.index("bbcode += designs_part + roads_part")
        assert 'data.get("counsel_roads_display"' in render

    def test_a_cards_pad_reaches_only_into_a_blank_paragraph(self):
        u = _read(SCRIPTS / "card_underlay.gd")
        assert "static func blank_paragraph(paragraphs: PackedStringArray, i: int) -> bool:" in u
        assert "PAD_TOP if blank_paragraph(paragraphs, first - 1) else 0.0" in u
        assert "PAD_BOTTOM if blank_paragraph(paragraphs, last + 1) else 0.0" in u

    def test_the_settlement_tail_folds_its_how_to(self):
        popup = _read(SCRIPTS / "proposal_confirm_popup.gd")
        assert '_fold_first_sentence("settle.carry", carry_hint)' in popup

    def test_the_refused_levies_stand_on_one_row_folded(self):
        rp = _read(SCRIPTS / "region_panel.gd")
        body = rp.split("func _recruit_rows(", 1)[1].split("\nfunc ", 1)[0]
        assert "elif Utils.explanations_folded():" in body and 'rows.append("    " + refused_row)' in body
        # On the page each refused arm keeps its own row and its reason
        assert 'rows.append("    " + _dim(str(arm).capitalize(), str(q.get("short", ""))))' in body


# ═══════════════════════════════════════════════════════════════════════════
# The very wide screen and the gathering
# ═══════════════════════════════════════════════════════════════════════════

class TestTheWideMap:
    SRC = _read(SCENES / "map_renderer_base.gd")

    def test_the_contain_fit_keeps_its_meaning(self):
        assert "return clamp(_get_fit_zoom_level(), min_zoom, max_zoom)" in _func(self.SRC, "_get_initial_zoom_level")
        body = _func(self.SRC, "fit_europe")
        assert body.index("_set_camera_zoom_level(_get_initial_zoom_level())") < body.index("_center_view_on_map()")

    def test_a_very_wide_room_opens_filled_and_home_toggles(self):
        assert "if _fills_width():\n\t\t_apply_fill_view()" in _func(self.SRC, "_finalize_view_setup")
        home = _func(self.SRC, "home_view")
        assert "if _fills_width() and not _is_fill_view():" in home and "fit_europe()" in home
        assert 'UiSettings.get_wide_map() != "fill"' in _func(self.SRC, "_fills_width")
        assert "max_zoom = maxf(2.5, _get_fill_zoom_level() * 1.25)" in _func(self.SRC, "_update_zoom_floor")

    def test_the_boot_view_follows_the_room_until_the_player_moves(self):
        for fn in ("_on_map_area_resized", "refresh_viewport_scale"):
            assert "_rederive_boot_view()" in _func(self.SRC, fn), fn
        for fn in ("_zoom_at_point", "focus_on_map_point", "_handle_pan_key_event"):
            assert "_player_moved_view()" in _func(self.SRC, fn), fn

    def test_the_dock_keeps_a_filled_view_filled(self):
        body = _func(self.SRC, "set_right_inset")
        assert "var was_fill := _is_fill_view()" in body and "_apply_fill_view()" in body

    def test_the_chip_says_which_view_comes_next(self):
        main = _read(SCRIPTS / "main.gd")
        assert "map_area.home_view()" in _func(main, "_on_fit_europe")
        assert "map_area.home_tip()" in _func(main, "_refresh_map_controls")

    def test_names_gather_only_at_the_whole_sheet(self):
        assert "is_at_min_zoom()" in _func(self.SRC, "gathers_names")
        layer = _read(SCENES / "map_label_layer.gd")
        assert 'const GATHER_FORMAT := "%s · %d more"' in layer
        assert '"gathered": gathered' in layer
        # IGR-G2's co-located stack keeps its own form
        assert 'var stack_text := "%s +%d" % [lead_name, group_size - 1]' in self.SRC


class TestTheHarness:
    def test_the_capture_runner_shoots_the_defaults_and_tags_the_old_views(self):
        runner = _read(TOOLS / "iq10_run_captures.py")
        assert 'ap.add_argument("--explanations", default="folded", choices=["folded", "page"]' in runner
        assert 'ap.add_argument("--wide-map", default="fill", choices=["fill", "sheet"]' in runner
        assert 'text_tag += "_" + explanations.upper()' in runner

    def test_the_harness_seeds_both_and_records_hints_and_the_raw_hash(self):
        harness = _read(TOOLS / "iq10_surface_screenshot.gd")
        assert 'get_script_constant_map().has("EXPLANATIONS")' in harness
        assert 'utils_notes.call("reset_notes")' in harness
        assert 'entry["text_md5"] = raw.md5_text()' in harness
        assert 'entry["hints"] = hints' in harness


# ═══════════════════════════════════════════════════════════════════════════
# DRIVEN — tools/ui_gilt3_probe.gd, headless
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
    out = tmp_path_factory.mktemp("ui_gilt3") / "probe.json"
    env = dict(os.environ, UI_GILT3_OUT=str(out))
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
    def test_on_the_page_every_helper_returns_the_old_string(self, probe):
        page = probe["modes"]["page"]
        lead = "[color=#a0a0a8]Every court of Europe — its temper toward France.[/color]\n\n"
        assert page["folded"] is False
        assert page["lead_mark"] == "" and page["lead"] == lead
        assert page["note"] == "First sentence. The rest of it.\n"
        assert page["link"] == "" and page["show"] is True

    def test_folded_the_words_ride_in_the_hint_or_the_note(self, probe):
        folded, opened = probe["modes"]["folded"], probe["modes"]["opened"]
        assert folded["folded"] is True and folded["lead"] == "" and folded["show"] is False
        assert "[hint=Every court of Europe — its temper toward France.]" in folded["lead_mark"]
        assert "[url=note:probe.lead]" in folded["lead_mark"]
        assert folded["note"].startswith("First sentence. [url=note:probe.note]") and folded["note"].endswith("\n")
        assert opened["state"] is True and opened["show"] is True
        assert opened["note"].startswith("First sentence. The rest of it. [url=note:probe.note]")
        assert opened["lead_open_after_toggle"] is True

    def test_the_interim_fixes_hold_in_the_engine(self, probe):
        """The sentence finder and the card pad rule, run by the engine."""
        assert probe["modes"]["sentence"] == [45, -1, 21, -1]
        assert probe["modes"]["blank"] == [True, False, True, True, False, False, False, True]

    def test_a_tip_is_cleaned_for_the_tag(self, probe):
        assert probe["modes"]["clean"] == "Loosen Rein — loyalty stays (100) line two"
        assert probe["modes"]["hints"] == ["one", "two words"]
        assert probe["modes"]["default"] == "folded" and probe["modes"]["wide_default"] == "fill"

    @pytest.mark.parametrize("case,tip", [
        ("word", "the plain tip"),
        ("lead", "The lead-in’s own words (100)."),
        ("chip", "loyalty stays 100; tribute 75% to 50%"),
        ("chip_off", "unavailable: Loyalty is already full"),
    ])
    def test_the_hover_answers_over_its_words(self, probe, case, tip):
        """RichTextLabel.get_tooltip() answers the tip over the hinted words,
        the ⓘ (a link round a hinted image) and a chip (a hint inside a link
        inside a one-cell table) — and no raw tag prints (the straight
        apostrophe once broke the tag: measured)."""
        got = probe["hints"][case]
        assert tip in got["tips"], got
        assert "[hint=" not in got["parsed"]

    def test_the_reading_share_takes_the_view_and_spares_the_grip(self, probe):
        share = probe["share"]
        assert share["view"] == [1600.0, 900.0]
        assert share["authored"] == [700.0, 500.0]
        assert share["shared"] == [880.0, 765.0]      # 0.55 x 1600 under the 900 cap; 0.85 x 900
        assert share["gripped"] == [600.0, 400.0]

    def test_the_very_wide_room_fills_and_the_ordinary_one_does_not(self, probe):
        m = probe["map"]
        assert m["fill_5120"] == pytest.approx(2.0) and m["fill_7680"] == pytest.approx(3.0)
        assert m["wide_5120"] is True and m["wide_3840x1200"] is True
        assert m["wide_3440"] is False and m["wide_1920"] is False

    def test_crowded_plates_gather_under_their_lead_by_nation(self, probe):
        m = probe["map"]
        assert m["groups"] == [{"count": 6, "lead": 0, "members": [1, 4]}]
        assert m["format"] == "Napoleon · 6 more"

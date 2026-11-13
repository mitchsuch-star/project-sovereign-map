"""Session UI-4 (November 12, 2026) — the levers past 7.

Session UI-3's three blind readers held the client at 7 and named why: small body
type and text-heavy bodies, four screens at 6 (the Balance of Europe, the province
panel, the war detail, the settlement table), the 32:9 HUD clustered in the middle of
the filled map, the command window's prose cut at Interface Scale 2.0, and disabled
controls that read like live ones. The user's rulings at the session's head: "115%"
(the shipped Text size) and "Screen edges" (the 32:9 HUD); the rest delegated. Rules
in docs/SYSTEMS_REFERENCE.md §215; the record docs/UI_VISUAL_FOUNDATION_SPEC.md §12.

The source half pins the kit and where it is used. The driven half runs
tools/ui_gilt4_probe.gd headless and SKIPS when the engine is missing — a skip is
not a pass.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"
PROBE = TOOLS / "ui_gilt4_probe.gd"


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    at = src.index(f"func {name}(")
    ends = [i for i in (src.find("\nfunc ", at + 10), src.find("\nstatic func ", at + 10),
                        src.find("\nconst ", at + 10), src.find("\nvar ", at + 10)) if i != -1]
    return src[at:min(ends) if ends else len(src)]


# ═══════════════════════════════════════════════════════════════════════════
# The user's two rulings
# ═══════════════════════════════════════════════════════════════════════════
class TestTheType:
    def test_the_game_ships_at_115_and_100_stays_a_choice(self):
        src = _read(SCRIPTS / "ui_settings.gd")
        assert "const DEFAULT_TEXT_SIZE := 1.15" in src
        assert "const MIN_TEXT_SIZE := 1.0" in src

    def test_an_inline_icon_grows_with_the_words_and_a_meter_does_not(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert "var px := text_px(size)" in _func(utils, "bb_icon")
        assert "var h := text_px(height)" in _func(utils, "bb_flag")
        assert "text_px(" not in _func(utils, "bb_meter")

    def test_the_harness_shoots_each_checkout_at_its_own_default(self):
        """A BEFORE copy (1.0) and this tree (1.15) are each shot as they
        ship, untagged; a size given on the command line tags the frame, and
        the readability report keys a reading apart only off its own default."""
        harness = _read(TOOLS / "iq10_surface_screenshot.gd")
        assert 'var default_text := float(consts.get("DEFAULT_TEXT_SIZE", 1.0))' in harness
        assert '_current["text_size_default"] = default_text' in harness
        runner = _read(TOOLS / "iq10_run_captures.py")
        assert 'ap.add_argument("--text-size", type=float, default=None,' in runner
        assert 'text_tag = "" if text_size is None else "_T%.2f" % text_size' in runner
        report = _read(TOOLS / "uxr0_readability_report.py")
        assert 'text_default = float(res.get("text_size_default", 1.0) or 1.0)' in report
        assert "if abs(text_size - text_default) > 1e-9:" in report


class TestTheEdges:
    def test_auto_stands_at_the_edges_while_the_map_fills(self):
        settings = _read(SCRIPTS / "ui_settings.gd")
        assert 'const HUD_WIDTHS := ["auto", "full", "16:9", "centred"]' in settings
        full = _func(_read(SCRIPTS / "utils.gd"), "hud_band_full")
        assert 'width == "16:9"' in full
        assert '(width == "auto" and UiSettings.get_wide_map() == "sheet")' in full

    def test_panels_size_against_the_zone_and_anchor_to_the_band(self):
        utils = _read(SCRIPTS / "utils.gd")
        room = _func(utils, "hud_size_room")
        assert "var band := hud_band(view)" in room
        assert "room = minf(room, floorf(view.y * 16.0 / 9.0))" in room
        assert "bw = minf(bw, floorf(view.y * 16.0 / 9.0))" in _func(utils, "dock_rect")
        main = _read(SCRIPTS / "main.gd")
        assert main.count("UiSettings.default_terminal_size(_hud_size_room())") == 3
        assert "_hud_room().x - TERMINAL_ANCHOR_LEFT * 2.0" in _func(main, "_relayout_terminal")
        tutor = _read(SCRIPTS / "tutorial_overlay.gd")
        assert "Utils.hud_size_room(view) * CARD_WIDTH_FRACTION" in _func(tutor, "_fit_card_width")

    def test_the_wide_map_switch_moves_the_band(self):
        main = _read(SCRIPTS / "main.gd")
        assert "_refit_hud_band()" in _func(main, "_on_wide_map_changed")
        panel = _read(SCRIPTS / "settings_panel.gd")
        # short names; the row's hint names what each choice does
        assert '"16:9": "16:9 band"' in panel and '"auto": "Auto (the default)"' in panel
        assert "16:9 keeps them in that band; Centred gathers them into the middle" in panel

    def test_the_runner_names_a_16_9_frame_without_a_colon(self):
        runner = _read(TOOLS / "iq10_run_captures.py")
        assert 'choices=["auto", "full", "16:9", "centred"]' in runner
        assert 'text_tag += "_HUD_" + hud_width.upper().replace(":", "X")' in runner


# ═══════════════════════════════════════════════════════════════════════════
# The locked chip, the command window, the boot map
# ═══════════════════════════════════════════════════════════════════════════
class TestTheLockedChip:
    def test_a_locked_chip_has_no_box_and_a_lock(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert 'const CHIP_DIM_BG := "00000000"' in utils
        assert 'const CHIP_DIM_RIM := "00000000"' in utils
        assert 'const CHIP_RIM_ALPHA := "ff"' in utils
        body = _func(utils, "bb_chip_disabled")
        assert "bb_icon(LOCK_GLYPH, 16, CHIP_DIM_INK)" in body
        assert 'label.replace(" ", "\\u00A0")' in body
        assert "[url=" not in body
        assert (PROJECT / "assets" / "ui" / "icons" / "phosphor" / "lock-simple.svg").is_file()

    def test_the_lock_is_imported_with_mipmaps(self):
        imp = PROJECT / "assets" / "ui" / "icons" / "phosphor" / "lock-simple.svg.import"
        assert imp.is_file()
        assert "mipmaps/generate=true" in _read(imp)

    def test_the_contrast_census_exempts_the_locked_pair(self):
        sys.path.insert(0, str(TOOLS))
        import uxr2b_contrast_report as CR  # noqa: E402
        assert CR.DISABLED_CHIP == ("00000000", "6f7480ff")

    def test_a_disabled_button_keeps_its_ink_and_loses_its_face(self):
        theme = _read(PROJECT / "ui" / "main_theme.tres")
        block = theme.split('[sub_resource type="StyleBox" id="StyleBoxFlat_joxlk"]', 1)[1].split("[sub_resource", 1)[0]
        assert "bg_color = Color(0.075, 0.08, 0.115, 0)" in block
        assert "dashed = true" in block
        assert "Button/colors/font_disabled_color = Color(0.55, 0.55, 0.58, 1)" in theme


class TestTheCommandWindow:
    def test_the_war_list_never_stands_on_the_window(self):
        war = _read(SCRIPTS / "war_status_panel.gd")
        assert "_clear_the_command_window(view)" in _func(war, "_apply_geometry")
        body = _func(war, "_clear_the_command_window")
        assert "avoid_control.get_global_rect().grow(AVOID_GAP)" in body
        # whole war lines beside the window; in the compact view (800 x 450) the
        # list narrows to its floor and its names clip rather than stand on it
        assert ("var floor_w: float = float(MIN_WIDTH) if Utils.compact_view() "
                "else maxf(float(MIN_WIDTH), _content_need_width())") in body
        main = _read(SCRIPTS / "main.gd")
        assert "war_status_panel.avoid_control = bottom_left_ui" in main
        assert 'war_status_panel.call_deferred("_fit_panel_to_content")' in _func(main, "_relayout_terminal")

    def test_the_boot_help_folds_to_two_lines_and_every_command_is_a_click_away(self):
        main = _read(SCRIPTS / "main.gd")
        body = _func(main, "_print_boot_help")
        assert "func _print_boot_help(full: bool = false) -> void:" in main
        folded = body.index("var folded := Utils.explanations_folded()")
        assert body.index('[url=" + BOOT_HELP_META + "]') > folded
        # On the page (and on the click) every line prints as before
        assert body.index("Commands:") > folded
        assert "The war table: every standing order is an arrow" in body
        meta = _func(main, "_on_output_meta_clicked")
        assert "if meta_str == BOOT_HELP_META:\n\t\t_print_boot_help(true)" in meta

    def test_the_war_detail_starts_below_the_notice_rail(self):
        """Shot over the t20 war room the popup stood under the rail's Imperial
        Box, its close button hidden: it starts below the rail when the rail
        stands over its columns, and the clamp honours that floor."""
        war = _read(SCRIPTS / "war_detail_popup.gd")
        refit = _func(war, "refit")
        assert "band_top = maxf(band_top, rail.end.y + Utils.HUD_MARGIN)" in refit
        assert 'panel.set_meta("clamp_band_top", band_top)' in refit
        utils = _read(SCRIPTS / "utils.gd")
        assert 'if panel.has_meta("clamp_band_top"):' in _func(utils, "clamp_anchored_panel")
        main = _read(SCRIPTS / "main.gd")
        assert "war_detail_popup.avoid_rail = notification_bar.rail_panel" in main

    def test_the_rail_stands_aside_for_a_covering_screen(self):
        """The sibling: the books (62 % wide since UI-3, layer 50) reach under
        the rail's corner at 1600 x 900 — the rail stands aside for a covering
        screen as the war HUD does; a pinned screen is not a covering one."""
        main = _read(SCRIPTS / "main.gd")
        # Session UI-5: and while the HUD is hidden (H) the rail stands aside too.
        assert ("notification_bar.set_suspended(_is_modal_dialog_open() or _is_screen_open() or _hud_hidden)"
                in _func(main, "_update_war_panel_visibility"))

    def test_the_folded_help_stands_whole_at_2_0(self):
        main = _read(SCRIPTS / "main.gd")
        body = _func(main, "_print_boot_help")
        assert "or click one of your marshals on the map.[/color]" in body
        # Berthier's question stands in the full list, every word
        assert "\\\"what can I do\\\" (Berthier names the orders the board takes today)" in body

    def test_crowded_plates_gather_a_hair_apart(self):
        layer = _read(SCENES / "map_label_layer.gd")
        assert "const GATHER_GAP_PX := 6.0" in layer


# ═══════════════════════════════════════════════════════════════════════════
# The measure correction — three frames shot as the game shows them
# ═══════════════════════════════════════════════════════════════════════════
class TestTheInterimReadingsFixes:
    """What the three interim readers named, fixed before the final reading."""

    def test_the_rest_stops_on_a_tables_rows(self):
        utils = _read(SCRIPTS / "utils.gd")
        body = _func(utils, "_rtl_lines")
        assert "if b - a > row_px * WHOLE_LINE_BLOCK_ROWS:" in body
        assert "var step := _table_row_step(b - a, row_px, sep)" in body
        assert "const TABLE_ROW_PAD := 6.0" in utils
        # the step is the one the block divides into whole rows — bb_table's
        # padded row or a bare [table]'s — else the block stays one box (HEAD's rule)
        step = _func(utils, "_table_row_step")
        assert "for step in [row_px + TABLE_ROW_PAD + sep, row_px + sep]:" in step
        assert "absf(n - roundf(n)) <= WHOLE_LINE_ROW_FIT" in step and "const WHOLE_LINE_ROW_FIT := 0.12" in utils

    def test_the_portrait_cell_is_not_ruled(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert 'return "[table=2][cell padding=2,2,2,2]" + portrait.strip_edges()' in _func(utils, "bb_portrait_row")

    def test_the_windows_the_readers_found_short(self):
        enemy = _read(SCRIPTS / "enemy_phase_dialog.gd")
        assert "Utils.fit_reading_window($PanelContainer, $PanelContainer/VBoxContainer/ContentScroll, content_label)" in enemy
        assert "const ASSESSMENT_CAP_SHARE := 0.5" in _read(SCRIPTS / "diplomacy_wizard.gd")
        assert _read(SCRIPTS / "mailbox_panel.gd").count("Vector2(0.62, 0.94)") == 2
        assert "const LOG_FLOOR_SHORT := 80.0" in _read(SCRIPTS / "main.gd")

    def test_the_war_details_noughts_stand_on_one_line(self):
        war = _read(SCRIPTS / "war_detail_popup.gd")
        assert 'at_nought.append(label + " 0/" + str(cap))' in war
        assert 'At nought: " + ", ".join(at_nought)' in war

    def test_the_economys_repeats_fold_behind_its_info(self):
        ledger = _read(SCRIPTS / "strategic_ledger.gd")
        assert 'Utils.bb_lead(_ceiling_line(econ, treasury), "sl.economy.lead")' in ledger

    def test_the_menu_column_stands_between_the_title_and_the_footer(self):
        menu = _read(SCRIPTS / "main_menu.gd")
        fit = _func(menu, "_fit_menu_column")
        # the title is planned against the TIGHTEST column, its rows stepping
        # aside from the top (the eagle, then the overline) before the block does
        assert 'const TITLE_STEPS := [[], ["Eagle"], ["Eagle", "OverTitle"]]' in menu
        assert "var limit: float = footer_top - 12.0 - col_h4 - 12.0" in fit
        assert "if h * rest + _title_height(block, step) + TITLE_INK_FOOT <= limit:" in fit
        # measured AT REST — never at the entrance's sliding position
        assert "_title_tween == null or not _title_tween.is_running()" in fit
        assert "total += maxf(row.size.y, row.get_combined_minimum_size().y)" in _func(menu, "_title_height")
        assert "tw.finished.connect(func(): _fit_menu_column.call_deferred())" in menu
        # the compact view's button faces step in (the label's line sets the height)
        assert "var pad: float = 5.0 if compact else 10.0" in fit
        # the painting's credit stands beside the chip, wrapping, growing up
        build = _func(menu, "_build_footer")
        assert "_caption.anchor_left = 0.62" in build and "_caption.grow_vertical = Control.GROW_DIRECTION_BEGIN" in build
        assert "_caption.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART" in build
        assert "footer_top = h * _footer.anchor_top - _footer.get_combined_minimum_size().y" in fit
        assert 'var footer_top: float = h - 24.0' in fit
        assert '_footer.add_child(version)' in menu and '_footer.add_child(_status_chip)' in menu

    def test_settings_joins_its_thin_sections(self):
        panel = _read(SCRIPTS / "settings_panel.gd")
        assert 'const _JOIN_PREVIOUS := ["INTERFACE", "SPOKEN ORDERS"]' in panel
        assert 'const _TAB_NAMES := ["DISPLAY", "SOUND", "ORDERS", "CONTROLS", "CREDITS"]' in panel

    def test_the_ultrawide_derives_a_step_larger(self):
        assert "const ULTRA_WIDE_BONUS := 0.65" in _read(SCRIPTS / "ui_settings.gd")
        assert "ULTRA_WIDE_BONUS = 0.65" in _read(TOOLS / "uxr0_readability_report.py")


class TestTheLastFits:
    """The interim run's fit flags, fixed before the final measure."""

    def test_the_rail_holds_what_its_slot_holds(self):
        bar = _read(SCRIPTS / "notification_bar.gd")
        body = _func(bar, "_render_rail")
        assert "while room > 0.0 and visible_count > 1 and rail_panel.get_combined_minimum_size().x > room + 0.5:" in body
        assert "resized.connect(_on_rail_resized)" in _func(bar, "_ready")
        # the "+N" list reads what the rail SHOWS, so a trimmed icon is listed there
        assert 'shown[str(b.get_meta("notification_data").get("id", ""))] = true' in _func(bar, "_on_overflow_pressed")

    def test_a_scrolled_row_stands_where_it_is_seen(self):
        # the instrument's correction, declared in the record (spec §12)
        body = _func(_read(TOOLS / "iq10_surface_screenshot.gd"), "_under_modal")
        assert "var seen := r.intersection(scroll.get_global_rect())" in body
        assert "rows.append([layer, centre, str(root.get_path_to(c)), str(words)])" in body


class TestTheFinalShootsFixes:
    """What the first final shoot caught at Interface Scale 2.0 (800 x 450 logical), fixed before the record."""

    def test_the_stat_strip_wraps(self):
        strip = _read(SCRIPTS / "stat_strip.gd")
        assert strip.startswith("extends HFlowContainer")
        assert 'add_theme_constant_override("h_separation", 8)' in strip
        # the ledger's typed handle takes any container
        assert "var _strip: Container = null" in _read(SCRIPTS / "strategic_ledger.gd")

    def test_the_letters_answers_wrap(self):
        scene = _read(SCENES / "incoming_proposal_popup.tscn")
        assert '[node name="ButtonContainer" type="HFlowContainer" parent="PanelContainer/VBoxContainer"]' in scene

    def test_the_scale_cards_middle_scrolls_and_the_buttons_stand(self):
        card = _read(SCRIPTS / "scale_card.gd")
        assert "_middle_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED" in card
        for kid in ("_middle.add_child(lead)", "_middle.add_child(sample)", "_middle.add_child(row)",
                    "_middle.add_child(_derived_label)"):
            assert kid in card, kid
        assert "vbox.add_child(buttons)" in card
        fit = _func(card, "_fit_to_view")
        assert 'set_meta("clamp_ceiling_override", Vector2(0.0, need))' in fit
        assert "Utils.clamp_centered_panel(self)" in fit

    def test_a_long_path_note_opens_from_its_first_sentence(self):
        popup = _read(SCRIPTS / "proposal_confirm_popup.gd")
        assert "Utils.first_sentence_end(note_text) if Utils.explanations_folded() else -1" in popup
        assert "note.tooltip_text = note_text" in popup

    def test_the_tutor_body_rests_on_whole_lines(self):
        body = _func(_read(SCRIPTS / "tutorial_overlay.gd"), "_fit_card_height")
        assert "Utils.keep_whole_lines(_body)" in body

    def test_a_desk_needs_room_beside_the_map(self):
        top = _read(SCRIPTS / "top_bar.gd")
        assert "return not Utils.compact_view()" in _func(top, "can_pin")
        assert "elif active_screen == screen_name and can_pin():" in _func(top, "toggle_pin")
        refit = _func(top, "refit_active_screen")
        assert refit.index("_unpin_to_book()") < refit.index("_dock(screens[pinned_screen])")
        assert "chip.disabled = locked" in _func(top, "_dress_pin_chip")

    def test_the_end_card_has_a_compact_form(self):
        end = _read(SCRIPTS / "campaign_end.gd")
        assert "return Utils.compact_view()" in _func(end, "_compact_card")
        render = _func(end, "_render")
        assert "if _compact_card():\n\t\t\t_strip.visible = false" in render
        assert "crest.visible = not _compact_card()" in render
        # the strip aside, the record prints the figures in place
        assert "var tiled: bool = not totals.is_empty() and not _compact_card()" in _func(end, "_record_block")

    def test_the_bar_sheds_the_dates_words_last(self):
        bar = _read(SCRIPTS / "top_bar.gd")
        assert "const _FIT_STEPS := 8" in bar
        turn = _func(bar, "_render_turn_text")
        assert 'if _calendar_label == "" or _fit_step >= 8:' in turn
        assert 'turn_label.text = " ".join(words.slice(1)) if words.size() >= 3 else _calendar_label' in turn
        assert "_render_turn_text()" in _func(bar, "_apply_fit_step")
        assert "_render_turn_text()" in _func(bar, "update_turn")

    def test_on_the_page_settings_shows_every_section(self):
        panel = _read(SCRIPTS / "settings_panel.gd")
        show = _func(panel, "_show_tab")
        assert "var paged := Utils.explanations_folded()" in show
        assert "_tab_row.visible = paged" in show
        assert "(_pages[i] as Control).visible = (i == index) or not paged" in show
        assert "_show_tab(_remembered_tab)" in _func(panel, "_on_explanations_selected")

    def test_the_books_figures_carry_the_thousands_mark(self):
        ledger = _read(SCRIPTS / "strategic_ledger.gd")
        assert 'return ("+" if n >= 0 else "-") + _format_number(absi(n)) + "g"' in ledger
        assert 'income_prefix.strip_edges().trim_suffix("+").strip_edges().trim_suffix(":")' in ledger


class TestTheHooksRound:
    """What the hook's full run caught after the final measure (the engine lane's
    frame and driven pins at 115 %), fixed at its cause before the commit."""

    def test_the_objection_has_a_compact_form(self):
        dlg = _read(SCRIPTS / "objection_dialog.gd")
        fit = _func(dlg, "_fit_compact")
        assert "grid.columns = 3 if compact else 2" in fit
        assert 'column.add_theme_constant_override("separation", 4)' in fit
        assert "_fit_compact()" in _func(dlg, "show_objection") and "_fit_compact()" in _func(dlg, "refit")
        assert '("\\n" if Utils.compact_view() else "\\n\\n") + stake_line' in dlg

    def test_the_capture_choice_wraps_its_answers_in_the_compact_view(self):
        dlg = _read(SCRIPTS / "capture_choice_dialog.gd")
        fit = _func(dlg, "_fit_compact")
        assert "btn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART if compact else TextServer.AUTOWRAP_OFF" in fit

    def test_the_proclamation_reads_whole(self):
        card = _read(SCRIPTS / "proclamation_popup.gd")
        fit = _func(card, "_fit_card")
        assert 'scroll.set_meta("relax_last", true)' in fit
        assert 'panel.set_meta("clamp_ceiling_override", Vector2(0.0, view.y))' in fit
        assert "flags.visible = not Utils.compact_view() and new_flag.texture != null" in fit

    def test_the_cabinets_counsel_takes_the_blank_lines_room_in_the_compact_view(self):
        wiz = _read(SCRIPTS / "diplomacy_wizard.gd")
        assert '("" if Utils.compact_view() else "\\n") + "[color=#" + Utils.COLOR_INFO + "]\\"" + assessment_text' in wiz

    def test_the_tutor_cards_acts_lead_in_the_compact_view(self):
        render = _func(_read(SCRIPTS / "tutorial_overlay.gd"), "_render")
        assert "var acts_at := lines.size()" in render
        assert "lines.insert(acts_at, door)" in render and "lines.insert(acts_at, skip)" in render

    def test_the_settlement_rows_stand_alone_in_the_compact_view(self):
        popup = _read(SCRIPTS / "proposal_confirm_popup.gd")
        assert "if Utils.compact_view():\n\t\treturn false" in _func(popup, "_court_is_open")
        assert "btn.custom_minimum_size = Vector2(160, 40 if Utils.compact_view() else 45)" in popup

    def test_the_war_details_purpose_stays_one_sentence(self):
        war = _read(SCRIPTS / "war_detail_popup.gd")
        assert "var obj_summary = obj_lead + target_text + \" \" + Utils.bb_meter(held_n, held_of, 90, 8)" in war


class TestTablesSpanTheirPages:
    def test_a_table_takes_a_floor_per_column(self):
        """A BBCode table shrinks to its words (the economy's books stood 130 px
        on a 990-px page): `width_px` sets a transparent floor in each head cell,
        the column's share less its words."""
        utils = _read(SCRIPTS / "utils.gd")
        table = _func(utils, "bb_table")
        assert "width_px: float = 0.0" in table
        assert "var pad := bb_col_floor(float(floors[c]) - _head_words_px(head_txt))" in table
        assert "head_txt = (pad + head_txt) if c in right_cols else (head_txt + pad)" in table
        assert "[img width=%d height=1 color=#00000000]" in _func(utils, "bb_col_floor")

    def test_the_readers_tables_span(self):
        ledger = _read(SCRIPTS / "strategic_ledger.gd")
        assert ledger.count("_table_px())") >= 7
        assert "float(_balance_width()) - 16.0)" in _read(SCRIPTS / "diplomatic_ledger.gd")
        # the Dispatch's marshal table stands at its natural width (its State
        # tags are wider than any share: a floored table overran the window);
        # its ⚠ rides the State cell — the fifth column was clipped at 2.0
        assert 'Utils.bb_table(["Marshal", "Location", "Men", "State"], m_rows, [2], [3, 3, 2, 4])' \
            in _read(SCRIPTS / "dispatch_view.gd")
        assert "[3, 4, 3, 1]," in _read(SCRIPTS / "war_detail_popup.gd")

    def test_the_gauge_labels_stand_under_their_ticks(self):
        dl = _read(SCRIPTS / "diplomatic_ledger.gd")
        body = _func(dl, "_gauge_scale_table")
        assert "[table=" not in body
        assert "font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x" in body


class TestTheStagings:
    def test_three_surfaces_are_shot_in_context(self):
        runner = _read(TOOLS / "iq10_run_captures.py")
        for shot in ('"id": "region_paris_war_room"', '"id": "war_detail_t20_war_room"',
                     '"id": "main_menu_answering"'):
            assert shot in runner, shot
        assert '{"call": "_on_map_region_clicked", "args": ["Paris"], "then_wait": 30}' in runner
        assert '{"set_path": "_backend_up", "value": True}' in runner
        recorder = _read(TOOLS / "iq10_capture_payloads.py")
        assert 'record("war_room_t20", {"test": test, "topology": get(c, "/map_topology"),' in recorder

    def test_the_rating_set_maps_them_and_keeps_the_old_road(self):
        rating = _read(TOOLS / "ui_rating" / "make_rating_set.py")
        assert '"F24": "IQ10_REGION_PARIS_WAR_ROOM"' in rating
        assert '"F25": "IQ10_WAR_DETAIL_T20_WAR_ROOM"' in rating
        assert '"F27": "IQ10_MAIN_MENU_ANSWERING"' in rating
        assert '"--old-stagings" in sys.argv[5:]' in rating


# ═══════════════════════════════════════════════════════════════════════════
# DRIVEN — tools/ui_gilt4_probe.gd, headless
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
    out = tmp_path_factory.mktemp("ui_gilt4") / "probe.json"
    env = dict(os.environ, UI_GILT4_OUT=str(out))
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
    def test_the_theme_takes_the_shipped_115(self, probe):
        t = probe["type"]
        assert t["shipped"] == pytest.approx(1.15) and t["stored"] == pytest.approx(1.15)
        assert (t["before"]["default"], t["before"]["caption"]) == (16, 14)
        assert (t["after"]["default"], t["after"]["caption"]) == (18, 16)
        assert "width=21 height=21" in t["glyph"]          # an 18-px glyph at 115 %
        assert t["flag_px"] == 16
        assert "width=50 height=8" in t["meter"]           # a meter keeps its geometry

    def test_auto_stands_at_the_edges_while_the_map_fills(self, probe):
        b = probe["band"]
        assert b["auto/fill"]["band"] == [0.0, 3200.0]
        assert b["auto/sheet"]["band"] == [800.0, 2400.0]
        assert b["16:9/fill"]["band"] == [800.0, 2400.0]
        assert b["full/fill"]["band"] == [0.0, 3200.0]
        assert b["centred/fill"]["band"] == [320.0, 2880.0]
        for key in ("auto/fill", "auto/sheet", "16:9/fill", "full/fill"):
            assert b[key]["room"] == 1600.0, key          # the panels keep the zone's size
            assert b[key]["plain"] == [0.0, 1600.0], key  # an ordinary screen: Full, as ever
            assert b[key]["plain_room"] == 1600.0, key

    def test_a_locked_chip_reads_locked(self, probe):
        c = probe["chips"]
        assert "lock-simple.svg" in c["locked"]
        assert "[cell border=#00000000 bg=#00000000]" in c["locked"]
        assert "[url=" not in c["locked"]
        assert "[cell border=#7eb8daff bg=#233043][url=vassal:loosen:Holland]" in c["live"]

    def test_the_signed_meter_fills_from_nought(self, probe):
        c = probe["chips"]
        # half 80: territory -35 of 40 fills 70 of the losing half
        assert "width=10 height=8 color=#" + "232838" in c["signed_loss"]
        assert "width=70 height=8" in c["signed_loss"]
        assert "width=80 height=8" in c["signed_win"]
        assert "width=80 height=8" in c["signed_zero_cap"]   # a cap of 0 reads as 1

    def test_the_war_list_clears_the_window(self, probe):
        c = probe["clear"]
        assert c["gap"] == 8.0
        assert c["beside"] == [-318.0, -12.0, 147.0, 249.0]
        assert c["above"] == [-331.0, -12.0, 45.0, 147.0]
        assert c["apart"] == [-331.0, -12.0, 147.0, 249.0]

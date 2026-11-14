"""Session UI-6 (November 13, 2026) - the campaign end, the main menu, the mailbox
(frames F26, F27, F29).

The UI-5 readers held these at 8 / 8-9 / 7-8: "the verdict is a long run of plain
text - make it a pull-quote / one verdict plaque", "the buttons are small"; "the
Seed field is small and odd", "the build string is dim", "the status bar is wide",
"the disabled rows look similar to the active ones", "the sibling buttons need more
finish"; "the terms are repetitive - a chip row", "a repeated Terms label", "make
the Accept button larger".

Source pins only (no engine).  The verdict's words move whole into the plaque; the
page branch of the mailbox keeps its "Terms" caption and hint line.
"""
from __future__ import annotations

import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


def _src(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    at = src.index(f"func {name}(")
    end = src.find("\nfunc ", at + 10)
    return src[at:end if end >= 0 else len(src)]


# -- F26: the campaign end ---------------------------------------------------

def test_the_verdict_stands_in_one_plaque():
    end = _src("campaign_end.gd")
    build = _func(end, "_ensure_plaque")
    assert 'name = "VerdictPlaque"' in build
    assert 'theme_type_variation = &"DisplayTitleLarge"' in build   # the tier, large, in the title face
    assert "_plaque_lines.bbcode_enabled = true" in build
    fill = _func(end, "_fill_plaque")
    assert "Utils.gilt_frame(box_bg, tone, Utils.FRAME_HAIRLINE, 18.0)" in fill
    # every word of the verdict: its tier, its lines, its closing
    assert 'verdict.get("lines", [])' in fill and 'verdict.get("closing", "")' in fill
    assert 'verdict.get("title", "")' in fill
    assert '"[center]"' in fill


def test_the_verdict_leaves_the_reading_only_where_the_plaque_stands():
    end = _src("campaign_end.gd")
    render = _func(end, "_render")
    assert "var plaqued: bool = _plaque_wanted(verdict)" in render
    assert 'var verdict_block := "" if plaqued else _verdict_block(verdict, style)' in render
    # the compact card (Interface Scale 2.0) keeps the verdict in the reading
    assert "and not _compact_card()" in _func(end, "_plaque_wanted")
    # over the reading on the Verdict's own card, under it on the others
    place = _func(end, "_place_plaque")
    assert 'at if _register == "verdict" else at + 1' in place


def test_the_end_card_buttons_are_bolder():
    arm = _func(_src("campaign_end.gd"), "_arm_buttons")
    assert 'primary_btn.theme_type_variation = &"PrimaryButton"' in arm
    assert "primary_btn.custom_minimum_size = Vector2(btn_w, btn_h)" in arm
    assert "secondary_btn.custom_minimum_size = Vector2(btn_w, btn_h)" in arm
    assert "40.0 if _compact_card() else 58.0" in arm


def test_the_plaque_is_built_before_the_card_renders():
    show = _func(_src("campaign_end.gd"), "show_ending")
    assert show.index("_ensure_plaque()") < show.index("_render(style)")


# -- F27: the main menu ------------------------------------------------------

def test_the_seed_is_one_options_row():
    menu = _src("main_menu.gd")
    assert 'seed_row.name = "SeedOptionsRow"' in menu
    assert "var seed_row := PanelContainer.new()" in menu
    assert "seed_row.custom_minimum_size = Vector2(520, 0)" in menu   # the buttons' width
    assert "_seed_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL" in menu
    assert "Vector2(240, 34)" not in menu
    # it is still the one box Begin reads
    assert "_seed_edit.text.strip_edges()" in menu


def test_the_build_line_reads():
    menu = _src("main_menu.gd")
    footer = _func(menu, "_build_footer")
    assert 'version.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)' in footer
    assert "Utils.UI_VERSION_LINE" not in footer
    assert 'version.add_theme_constant_override("outline_size", 3)' in footer
    assert "_footer.add_child(version)" in footer and "_footer.add_child(_status_chip)" in footer


def test_the_status_chip_is_no_wider_than_its_words():
    menu = _src("main_menu.gd")
    size = _func(menu, "_size_status_chip")
    assert "Control.SIZE_SHRINK_BEGIN" in size and "TextServer.AUTOWRAP_OFF" in size
    # the long launch hint still wraps in the footer's width
    assert "TextServer.AUTOWRAP_WORD_SMART if long_words" in size
    state = _func(menu, "_apply_backend_state")
    assert "_size_status_chip(false)" in state and "_size_status_chip(true)" in state


def test_a_waiting_row_reads_unavailable():
    menu = _src("main_menu.gd")
    make = _func(menu, "_make_button")
    assert 'add_theme_color_override("font_disabled_color", Utils.UI_DISABLED_TEXT)' in make
    assert "Color(Utils.UI_GOLD, 0.3), 1, 0.0, 0.0, true)" in make   # no face, a dashed rim
    face = _func(menu, "_button_face")
    assert 'f.set("dashed", dashed)' in face
    assert 'f.set("shadow_alpha", 0.0)' in face
    # the reason stays the hover
    assert 'b.tooltip_text = "" if _backend_up else WAITING_TIP' in _func(menu, "_apply_backend_state")


def test_the_live_rows_are_the_drawn_gilt_button():
    menu = _src("main_menu.gd")
    assert 'const GILT_BUTTON := preload("res://scripts/gilt_button.gd")' in menu
    make = _func(menu, "_make_button")
    assert "0.35, 0.0, false)" in make      # hover: the warm glow
    assert "0.0, 0.5, false)" in make       # pressed: the sunk well
    # the compact fit steps ANY face's margins, not only a StyleBoxFlat's
    assert "var sb: StyleBox = mb.get_theme_stylebox(st)" in _func(menu, "_fit_menu_column")
    # the live/waiting button language is still named by variation
    assert '&"TitleScreenButtonProminent" if prominent else &"TitleScreenButton"' in make


# -- F29: the mailbox --------------------------------------------------------

def test_the_terms_are_a_chip_row_without_a_repeated_label_when_folded():
    mail = _src("mailbox_panel.gd")
    terms = _func(mail, "_terms_line_label")
    assert "var folded: bool = Utils.explanations_folded()" in terms
    assert "if not folded:" in terms
    assert 'caption.text = "Terms"' in terms        # On the page keeps it
    assert "_terms_chip(text, text.length() > TERMS_CHIP_SHORT, folded)" in terms
    # the hover still carries every term
    assert '"Terms: " + " · ".join(' in terms


def test_a_term_chip_leads_with_its_glyph():
    mail = _src("mailbox_panel.gd")
    chip = _func(mail, "_terms_chip")
    assert "with_glyph := false" in chip
    # the lead's frame fixes (Nov 13): a long term's chip face is its lead words,
    # so the glyph is read off the WHOLE term (`glyph_text`) when it is given
    assert "Utils.glyph(_term_glyph(glyph_text if glyph_text != \"\" else text))" in chip
    assert "const TERM_GLYPHS := [" in mail
    # every glyph named is one of the shipped stat glyphs
    import re
    named = set(re.findall(r'\], "([a-z]+)"\]', mail[mail.index("const TERM_GLYPHS"):]))
    shipped = {"actions", "admin", "administration", "authority", "build", "cabinet", "command",
               "defense", "dp", "drum", "envoy", "europe", "fleet", "foot", "garrison", "glory",
               "gold", "guns", "horse", "income", "intel", "letter", "logistics", "march", "medal",
               "morale", "sail", "shock", "stability", "strength", "supply", "tactical", "threat",
               "trust", "turn", "war"}
    assert named and named <= shipped, named - shipped
    assert 'return "letter"' in _func(mail, "_term_glyph")


def test_accept_is_the_larger_gilt_answer_and_decline_a_plain_button():
    row = _func(_src("mailbox_panel.gd"), "_build_action_row")
    assert 'accept_btn.theme_type_variation = &"PrimaryButton"' in row
    assert "accept_btn.custom_minimum_size = Vector2(168, 46)" in row
    assert "decline_btn.custom_minimum_size = Vector2(120, 46)" in row
    assert "decline_btn.theme_type_variation" not in row


def test_the_reply_hint_is_a_hover_folded_and_a_caption_on_the_page():
    row = _func(_src("mailbox_panel.gd"), "_build_action_row")
    folded = row[:row.index("var hint = Label.new()")]
    assert "if Utils.explanations_folded():" in folded
    assert 'row.tooltip_text = "or click the letter to reply in full"' in folded
    assert "return row" in folded
    # On the page the caption is printed as before
    assert 'hint.text = "or click the letter to reply in full"' in row

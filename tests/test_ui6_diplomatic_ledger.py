"""Session UI-6: the Diplomatic Ledger's Nations, Vassals and Balance tabs (frames F11-F13).

Pure source pins (no engine): the figures-first layouts are gated on the Explanations switch (Folded), and
On the page the old strings stand. Driven reading is the lead's shoot."""
from pathlib import Path
import re

SCRIPT = Path(__file__).resolve().parent.parent / "godot-client" / "project-sovereign" / "scripts" / "diplomatic_ledger.gd"
SRC = SCRIPT.read_text(encoding="utf-8")


def _func(name: str) -> str:
    start = SRC.index(f"func {name}(")
    nxt = re.search(r"^func |^const |^var ", SRC[start + 5:], re.M)
    return SRC[start: start + 5 + nxt.start()] if nxt else SRC[start:]


class TestNations:
    def test_folded_courts_stand_in_pairs_page_keeps_the_table(self):
        body = _func("_render_nations")
        assert "if Utils.explanations_folded():\n\t\t\tbbcode += _court_grid(facts)" in body
        # Row FR, Session FR-2's review (FR2-2): the 820-px rule moved into a helper
        # that also records the width it read, so the page reflows on a resize.
        assert "bbcode += _facts_table(facts, _nations_table_is_wide())" in body
        wide = _func("_nations_table_is_wide")
        assert "return int(content_area.size.x) >= 820" in wide
        assert "_width_used = w if w > 280 else 640" in wide

    def test_the_grid_is_four_columns_two_facts_a_row_at_any_width(self):
        grid = _func("_court_grid")
        assert '"[table=4]"' in grid
        assert "i += 2" in grid
        assert "expand=1" in grid
        assert "820" not in grid
        # UI6-X48 (the final shoot's reading): a fact longer than a cell holds prints
        # under the grid as one full-width line — a sentence in a cell grew the grid
        # past the card's hairline (Godot lays the padding on top of the growth)
        assert "const GRID_FACT_MAX_CHARS := 44" in SRC
        assert "Utils.bb_plain(str(fact[1])).length() > GRID_FACT_MAX_CHARS" in grid
        assert 'out += " " + _caption_of(str(r[0])) + "  " + str(r[1]) + "\\n"' in grid

    def test_the_label_is_a_caption_without_its_colon(self):
        assert '": [/color]"' in _func("_caption_of")

    def test_every_fact_row_still_authored(self):
        body = _func("_render_nations")
        for label in ("Diplomat: ", "Doctrine: ", "Authority: ", "Regions: ", "Army: ", "Treaties: "):
            assert f'"{label}"' in body, label


class TestVassals:
    def test_locked_pin_line_is_kept_verbatim(self):
        assert 'return [Utils.bb_chip_disabled(label, "", gated), ""]' in _func("_vassal_action_parts")

    def test_a_locked_reason_is_never_a_printed_caption_folded(self):
        parts = _func("_vassal_action_parts")
        folded_branch = parts[parts.index("if Utils.explanations_folded():\n\t\t# Folded, a locked chip"):]
        assert folded_branch.index("return [Utils.bb_chip_disabled(label") < folded_branch.index("COLOR_INFO")

    def test_chip_face_is_title_face_folded_only(self):
        parts = _func("_vassal_action_parts")
        assert 'label = "[font=" + Utils.TITLE_FONT + "]" + plain_label + "[/font]"' in parts
        assert "var gated: String = plain_label" in parts
        assert 'face += " · " + cost_text' in parts

    def test_the_card_leads_with_a_strip_folded(self):
        card = _func("_format_vassal_card")
        assert "var folded_card: bool = Utils.explanations_folded()" in card
        assert "bbcode += _vassal_strip(strip)" in card
        # the interim readers (Nov 13): four tiles on one line clipped the garrison —
        # a narrower meter, and the tribute's note is its tile's hover
        assert 'Utils.bb_meter(loyalty, 100, 120, 14, loyalty_color)' in card
        assert 'tribute_tile = Utils.bb_hint(tribute_tile, "Tribute " + tribute_tip)' in card
        # On the page the old meter line and the facts rows stand
        assert 'bbcode += "  Loyalty [color=#"' in card
        assert 'facts.append([_fact_label("gold", "Tribute: "), tribute_cell])' in card
        assert 'facts.append([_fact_label("garrison", "")' in card

    def test_one_lock_chip_when_every_action_shares_a_reason(self):
        card = _func("_format_vassal_card")
        assert "_vassal_shared_lock_reason(actions) if folded_card" in card
        assert 'Utils.bb_chip_disabled("All instruments locked", "", shared_reason)' in card
        shared = _func("_vassal_shared_lock_reason")
        assert "return \"\"" in shared and "available" in shared

    def test_the_strip_is_one_line_to_four_tiles(self):
        body = _func("_vassal_strip")
        assert "tiles.size() if tiles.size() <= 4" in body and "ceil(tiles.size() / 2.0)" in body


class TestBalance:
    def test_folded_roads_share_one_table_page_keeps_the_cards(self):
        block = _func("_designs_block")
        assert "var one_table: bool = Utils.explanations_folded()" in block
        assert "out += _designs_one_table(roads)" in block
        assert 'Utils.bb_table(["Design", "Progress", "Hold", "Status"]' in block

    def test_one_header_row_and_a_band_row_per_road(self):
        table = _func("_designs_one_table")
        assert table.count('"Design", "Progress", "Hold", "Status"') == 1
        assert "Road %s" in table
        assert "Utils.TITLE_FONT" in table
        assert "bb_col_floor" in table          # the header spans the page
        assert "_balance_width()" in table

    def test_meters_fill_in_stronger_tokens_and_are_wide(self):
        table = _func("_designs_one_table")
        for token in ("COLOR_WARNING", "COLOR_CONQUEST", "COLOR_ERROR_CHIP"):
            assert f"Utils.{token}" in table
        assert "Utils.bb_meter(held, maxi(required, 1), meter_w, 12, tone)" in table
        assert "clampi(int(progress_px) - 80, 110, 420)" in table

    def test_folded_words_ride_hovers(self):
        table = _func("_designs_one_table")
        assert 'Utils.bb_hint(meter_cell, str(d.get("progress", "")))' in table


class TestRules:
    def test_no_value_or_collapses_to_a_bool(self):
        rx = re.compile(r"\b(str|int|float)\([^()]*\.get\([^()]*\)[^()]* or ")
        assert not [l for l in SRC.splitlines() if rx.search(l) and not l.lstrip().startswith("#")]

    def test_no_font_size_tags_and_no_new_hex_colours(self):
        assert "[font_size" not in SRC
        added = re.findall(r'"#?[0-9a-fA-F]{6}"', _func("_designs_one_table") + _func("_vassal_strip") + _func("_court_grid"))
        assert added == []


class TestTheTabIsDrawnToItsSettledWidth:
    """The lead's frame reading (Session UI-6, November 13): a tab drawn before
    the window's first layout measured its tables against the 640-px fallback
    (the nation cards' facts stood at ~70 % of the card, Austria's Exposure ran
    past it). The width used is remembered and the open tab redrawn once the
    page settles at another; the facts grid spans the card's inner width."""

    def test_the_resize_redraws_the_open_tab(self):
        src = _src() if "_src" in globals() else (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign" / "scripts" / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert "content_area.resized.connect(_on_content_resized)" in src
        assert "_width_used = out" in src
        assert 'call_deferred("_rerender_keeping_scroll")' in src
        assert "var span_w: float = float(_balance_width())\n" in src


class TestTheTextStopsShortOfTheCardsHairline:
    """The lead's dry-run reading of F11 (Session UI-6): Austria's open card —
    its Weariness and Exposure values long — grew its grid to the label's full
    width, past the card's right hairline (the theme gives a RichTextLabel no
    margin; a card is drawn 2 px inside the label's edge; Godot grows a table's
    long-text columns until the table fills the width it has). The page keeps
    a right text margin, so no text or table reaches the border."""

    def test_the_page_keeps_a_right_margin(self):
        src = SRC
        assert "const PAGE_RIGHT_MARGIN := 16.0" in src
        assert "page_box.content_margin_right = PAGE_RIGHT_MARGIN" in src
        assert 'content_area.add_theme_stylebox_override("normal", page_box)' in src

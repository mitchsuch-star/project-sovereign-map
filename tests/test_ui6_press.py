"""Session UI-6 - the press: the Morning Dispatch, the Correspondence and Le Moniteur.

Source-level pins (no engine): the figure tiles lead the Dispatch Folded, the beats
stand in the brighter ink, the courier's banner is cropped by hand, the sealed letter
has its own gilt action, empty Correspondence sections are one quiet line, the offing
is a compact row, and The War is a column of headlines with result badges - every one
gated on Explanations: Folded, the page branch left as it was.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


def _read(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def _func(src: str, name: str) -> str:
    m = re.search(r"^(?:static )?func " + re.escape(name) + r"\(.*?(?=^(?:static )?func |\Z)", src, re.S | re.M)
    assert m, name
    return m.group(0)


class TestDispatchTiles:
    def test_the_tiles_lead_before_the_beats_and_only_folded(self):
        body = _func(_read("dispatch_view.gd"), "_on_dispatch_received")
        i_tiles = body.index("_headline_tiles(situation")
        assert body.rfind("if Utils.explanations_folded():", 0, i_tiles) > 0
        assert i_tiles < body.index("W6-3 HEADLINE") < body.index('sub_beats')

    def test_the_old_figure_line_stays_on_the_page(self):
        body = _func(_read("dispatch_view.gd"), "_on_dispatch_received")
        i = body.index("_situation_figures(situation")
        assert "if not Utils.explanations_folded():" in body[i - 80:i]

    def test_the_tiles_hold_the_four_figures(self):
        tiles = _func(_read("dispatch_view.gd"), "_headline_tiles")
        for field in ("player_regions", "treasury", "treasury_delta", "authority", "strength_ratio_pct"):
            assert '"' + field + '"' in tiles
        assert "Utils.bb_table(heads" in tiles and "Utils.CARD_CLOSE" in tiles

    def test_the_beats_are_brighter_only_folded(self):
        body = _func(_read("dispatch_view.gd"), "_on_dispatch_received")
        assert "Utils.COLOR_TEXT if Utils.explanations_folded() else Utils.COLOR_INFO" in body

    def test_the_courier_banner_is_cropped_to_its_subject(self):
        src = _read("dispatch_view.gd")
        assert 'if key == "dispatch":' in src and "_focus_banner(_banner, w, BANNER_FOCUS_Y)" in src
        fn = _func(src, "_focus_banner")
        assert "AtlasTexture.new()" in fn and "clampf(focus_y, 0.0, 1.0)" in fn


class TestCorrespondence:
    def test_the_sealed_letter_has_its_own_gilt_action(self):
        src = _read("dispatch_view.gd")
        fn = _func(src, "_corr_primary_action")
        assert '"corr:read:" + str(mailbox_id)' in fn
        assert "Utils.TITLE_FONT" in fn and "Utils.UI_INK_NAVY" in fn and "_on_corr_meta" in fn
        # the whole face sits inside the navy ink - the glyph and the pad too (the contrast
        # instrument read the pad before the colour as the link's default ink on the gilt)
        assert '"[color=#" + ink + "]" + Utils.bb_glyph("letter", 20, ink)' in fn
        assert 'action.add_theme_color_override("default_color", Utils.UI_INK_NAVY)' in fn
        assert "_corr_primary_action(int(row.get" in src
        # the old chip is the page's, untouched
        body = _func(src, "_corr_body_bbcode")
        assert "not Utils.explanations_folded()" in body and '"Read the letter ▸"' in body

    def test_empty_sections_are_one_quiet_line_folded(self):
        render = _func(_read("dispatch_view.gd"), "_render_correspondence")
        for key in ("desk", "offing", "answered"):
            assert 'empty.get("%s"' % key in render
        assert 'ANSWERED (0)' in render and "Nothing has yet been answered." in render
        assert render.count("and folded") >= 3

    def test_the_offing_is_a_compact_row_folded(self):
        src = _read("dispatch_view.gd")
        assert "_add_offing_row(str(line))" in _func(src, "_render_correspondence")
        row = _func(src, "_add_offing_row")
        assert 'rfind(" — ")' in row and "COLOR_GOLD" in row


class TestMoniteur:
    def test_the_war_is_headlines_folded_and_the_page_is_unchanged(self):
        sec = _func(_read("gazette_view.gd"), "_section")
        assert 'title == "THE WAR" and Utils.explanations_folded()' in sec
        assert "_war_rows(rows)" in sec
        # the page's loop is still there, below the folded return
        assert sec.index("_war_rows(rows)") < sec.index("for i in range(rows.size()):")

    def test_a_battle_is_a_headline_with_a_result_badge_and_a_casualty_pair(self):
        blk = _func(_read("gazette_view.gd"), "_battle_block")
        assert "Utils.HEAD_OPEN + place + Utils.HEAD_CLOSE" in blk
        for badge in ("COLOR_SUCCESS", "COLOR_WARNING", "COLOR_ERROR"):
            assert "Utils.bb_badge(" in blk and badge in blk
        assert "casualties" in blk and "[i]" in blk
        assert '_nation_of(atk_tag) == "France"' in blk

    def test_the_disabled_later_issue_is_legible_with_its_reason_as_a_hover(self):
        row = _func(_read("gazette_view.gd"), "_update_page_row")
        assert "font_disabled_color" in row and "Utils.COLOR_INFO" in row
        assert "This is the newest issue." in row and "tooltip_text" in row


class TestBattleLinePattern:
    """The pattern gazette_view reads the campaign log's battle line with, run
    against the line `campaign_log` writes (backend/campaign_log.py)."""
    PATTERN = r"^(?:(.+?): )?(.+?) attacked (.+?)(?: at ([^—]+?))? — (.+?) \(([\d,]+) / ([\d,]+) casualties\)(.*)$"

    def test_the_named_battle_with_a_quote(self):
        line = ('Battle of Tyrol: Archduke John (Austria) attacked Bernadotte (France) — '
                'Archduke John tactical victory (234 / 2,519 casualties) — Archduke John: "The moment."')
        m = re.match(self.PATTERN, line)
        assert m and m.group(1) == "Battle of Tyrol"
        assert m.group(2) == "Archduke John (Austria)" and m.group(3) == "Bernadotte (France)"
        assert m.group(5) == "Archduke John tactical victory"
        assert (m.group(6), m.group(7)) == ("234", "2,519")
        assert m.group(8).strip().startswith("— Archduke John:")

    def test_the_stalemate_and_the_unnamed_battle(self):
        m = re.match(self.PATTERN, "Second Battle of Tyrol: Deroy (Bavaria) attacked Archduke John (Austria) — stalemate (1,960 / 1,312 casualties)")
        assert m and m.group(5) == "stalemate" and m.group(8) == ""
        m = re.match(self.PATTERN, "Ney (France) attacked Wellington (Britain) at Flanders — Wellington holds the field (10 / 20 casualties)")
        assert m and m.group(1) is None and m.group(4) == "Flanders"

    def test_a_capture_is_not_a_battle(self):
        assert re.match(self.PATTERN, "Bohemia captured by Austria (secure)") is None

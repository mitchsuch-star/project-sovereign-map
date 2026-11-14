"""Session UI-6 (November 13, 2026) - the Strategic Ledger's four books
(frames F05 Forces, F06 Economy, F07 Territories, F08 Manpower, scored 7-8).

The readers' single changes, built Folded (Explanations: Folded) only:

- Forces: the idle Cabinet sentence and the Authority line (the tiles say it)
  stand behind the book's note; the ORDER badge is toned by state (idle gold,
  an order in the command tone);
- Economy: ONE income-versus-charges bar under the tiles with the net at its
  end (drawn only where the printed rows reach the payload's Net), a band
  between the two tables, the tables spanning out to the tiles' edge;
- Territories: exceptions first in each group, the healthy run folded behind
  "N more at 100 %", a column empty on every row hidden;
- Manpower: the arms are ONE table, a recruit button per arm (a locked arm is a
  dim chip whose reason is the hover).

On the page every book prints as it did. GDScript is invisible to pytest, so
these are source pins.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "godot-client" / "project-sovereign" / "scripts" / "strategic_ledger.gd"


def _src() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _func(name: str) -> str:
    src = _src()
    m = re.search(r"^func " + re.escape(name) + r"\(", src, re.M)
    assert m, name
    nxt = re.search(r"^func |^static func ", src[m.end():], re.M)
    return src[m.start(): m.end() + (nxt.start() if nxt else len(src))]


class TestForces:
    def test_idle_cabinet_and_authority_stand_behind_the_note(self):
        body = _func("_render_forces")
        assert 'Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]THE CABINET' in body
        assert 'Utils.bb_lead("Authority: [color=#"' in body

    def test_order_badge_is_toned_by_state(self):
        body = _func("_render_forces")
        assert "tag_tone = Utils.COLOR_GOLD" in body
        assert "tag_tone = Utils.COLOR_COMMAND" in body
        assert "Utils.bb_tag(status.replace" in body


class TestEconomy:
    def test_balance_bar_folded_only_and_reconciled(self):
        body = _func("_render_economy")
        assert "if folded_books:" in body
        assert "_econ_balance_bar(inc + chg, net, reconciles)" in body
        bar = _func("_econ_balance_bar")
        assert "if not reconciles:" in bar
        assert "Utils.bb_meter(money_in" in bar and "Utils.bb_meter(money_out" in bar
        assert "Utils.COLOR_SUCCESS" in bar and "Utils.COLOR_ERROR" in bar
        assert "_econ_signed(net)" in bar

    def test_band_sits_between_income_and_charges(self):
        body = _func("_render_economy")
        assert body.index('"INCOME"') < body.index("_econ_band()") < body.index('"CHARGES"')

    def test_tables_reach_the_tiles_edge_folded_only(self):
        px = _func("_table_px")
        assert "Utils.explanations_folded()" in px and "size.x - 48.0" in px


class TestTerritories:
    def test_exceptions_first_and_healthy_run_folded(self):
        body = _func("_render_territories")
        assert '"exception": is_exception' in body
        assert "more at 100 %" in body
        assert "terr:more:" in body
        assert body.index('if bool(r["exception"]):') < body.index("for r in healthy:")
        # the lead's frame reading: the healthy rows fill the page first — only
        # the rest past _TERR_SHOWN folds (a group with nothing amiss was one fold)
        assert "var room: int = maxi(_TERR_SHOWN - shown, 3)" in body
        assert "str(rest.size()) + \" more at 100 %" in body
        assert "const _TERR_SHOWN := 10" in _src()

    def test_empty_column_hidden(self):
        body = _func("_render_territories")
        assert "any_buildings" in body and "heads.slice(0, 6)" in body

    def test_more_fold_is_routed(self):
        meta = _func("_on_meta_clicked")
        assert 'meta_str.begins_with("terr:more:")' in meta
        assert "_terr_more" in _src()

    def test_page_branch_still_lists_every_row(self):
        body = _func("_render_territories")
        assert "if not folded_rows:" in body


class TestManpower:
    def test_one_table_one_button_per_arm(self):
        body = _func("_render_manpower")
        assert "Utils.explanations_folded()" in body and "_manpower_table(mp)" in body
        table = _func("_manpower_table")
        assert "Utils.bb_table([" in table and '"Pool bar"' in table
        assert 'Utils.bb_button_chip("do:recruit " + pool_type' in table
        assert "Utils.bb_chip_disabled(" in table

    def test_page_cards_untouched(self):
        body = _func("_render_manpower")
        assert '"  Pool: [color=#"' in body and '"  Recruit: "' in body
        assert 'pool.get("regen_terms", [])' in body and 'pool.get("price_terms", [])' in body

    def test_recruit_chip_travels_the_typed_road(self):
        # the Admiralty's `do:` meta emits the typed command through main.gd
        meta = _func("_on_meta_clicked")
        assert 'meta_str.begins_with("do:")' in meta and "naval_command.emit(command)" in meta


class TestTheEconomyNotesAreHovers:
    """The interim blind reading (Session UI-6, November 13): folded, the Note
    column stood empty but for one line — a line's note is its label's hover,
    both tables Line | Gold; On the page the Note column stands as before."""

    def test_folded_the_note_is_the_labels_hover(self):
        body = _func("_econ_table")
        assert "if note_col >= 0:" in body
        assert "label = Utils.bb_hint(label, note_words)" in body
        assert 'Utils.bb_table(["Line", "Gold"], folded_cells, [1], [ECON_COLS[0], ECON_COLS[1]], _table_px())' in body
        # the page branch keeps its Note column
        assert 'Utils.bb_table(["Line", "Gold", "Note"], cells, [1], ECON_COLS, _table_px())' in body

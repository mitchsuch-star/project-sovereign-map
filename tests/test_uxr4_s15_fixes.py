"""UXR-4 at Pre-Deploy S15's head (October 25, 2026) — the decided fixes of the
re-homed marks, built as `docs/BUG_FIXES.md` decided them and re-shot at
1920x1080 and 5120x1440 for the user's yes/no at their monitor:

  UXR3-24 / UXR3-80  the Generals fold OUR DOCTRINE to its one title line behind
                     "▸ the doctrine" (open only on the doctrine's own board);
                     the Emperor's Presence states the figure AS APPLIED where he
                     stands ("+10% here at Bohemia") and its star dims with it
  UXR3-29            the Nations book leads with the courts' cards; "How Europe
                     Reads France" and the Exposure block close the book
  UXR3-79            the land's note (poor country / stripped by war) rides
                     directly under the controller line, above the ACTIONS block
  UXR3-81            the Vassals book lists a court with a granted petition
                     first, its Bond line leading its card

The pins are engine-free: the `.gd` source is the subject, and the frame record
(`docs/audits/uxr4_s15/index.json` — the harness's `seen_text`, whole lines
inside the window) says what each re-shot frame shows.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
AUDIT = REPO / "docs" / "audits" / "uxr4_s15"
RESOLUTIONS = ("1920x1080", "5120x1440")


def _src(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    """The body of one GDScript func (to the next top-level func)."""
    m = re.search(rf"(?ms)^(?:static )?func {re.escape(name)}\(.*?(?=^(?:static )?func |^const |\Z)", src)
    assert m, name
    return m.group(0)


def _order(src: str, *needles: str) -> bool:
    """True when every needle is in `src`, in the order given."""
    at = -1
    for n in needles:
        i = src.find(n, at + 1)
        if i < 0:
            return False
        at = i
    return True


_INDEX = json.loads((AUDIT / "index.json").read_text(encoding="utf-8"))


def _frame(fid: str, res: str) -> dict:
    for f in _INDEX["frames"]:
        if f["id"] == fid and f["resolution"] == res:
            return f
    raise AssertionError(f"no frame {fid} at {res}")


def _seen(fid: str, res: str) -> str:
    """The whole lines a player sees in the frame's content label (the longest
    label of the record — the screen's scroll body)."""
    rec = _frame(fid, res)["seen_text"]
    return max((e["seen"] for e in rec), key=len)


def _at(text: str, needle: str) -> int:
    i = text.find(needle)
    assert i >= 0, f"{needle!r} is not in the frame's seen text"
    return i


def test_the_frame_set_is_whole():
    """Every surface the row names is on the record at both sizes, with its
    before frame (where the S12b set has one) and its jpeg on disk."""
    wanted = {
        "generals_t20", "generals_np_field", "generals_boot", "generals_doctrine",
        "diplo_laws_rival_nations", "diplo_doctrine_nations", "diplo_petition_granted_vassals",
        "region_doctrine_posen", "region_doctrine_tyrol",
    }
    for fid in wanted:
        for res in RESOLUTIONS:
            f = _frame(fid, res)
            assert (REPO / f["after"]).is_file(), f["after"]
            assert f["errors"] == [], (fid, res, f["errors"])
            if f["before"] is not None:
                assert (REPO / f["before"]).is_file(), f["before"]
    assert _INDEX["script_errors"] == 0


class TestUXR3_24:
    """The Generals: OUR DOCTRINE folds; the Emperor's Presence is stated as
    applied where he stands and the star dims with it."""

    SRC = _src("marshal_management.gd")

    def test_a_the_doctrine_is_one_title_line_behind_a_toggle(self):
        body = _func(self.SRC, "_render_doctrine")
        assert "[url=doctrine:toggle]" in body
        assert '"▾ hide the doctrine" if _doctrine_open else "▸ the doctrine"' in body
        # The fold returns BEFORE the says / strength / flaw lines are written.
        assert _order(body, "if not _doctrine_open:", "return bbcode", "d_says", "Strength — ", "Flaw — ")

    def test_b_the_players_toggle_is_a_plain_var_that_outlives_the_screen(self):
        assert re.search(r"(?m)^var _doctrine_open := false$", self.SRC)
        # The session's own state: close_view() leaves it where the player put it.
        assert "_doctrine_open" not in _func(self.SRC, "close_view")
        meta = _func(self.SRC, "_on_meta_clicked")
        assert _order(meta, 'meta_str == "doctrine:toggle"', "_doctrine_open = not _doctrine_open",
                      "_render_current_view()", "Utils.restore_scroll(scroll_container, held_scroll)")

    def test_c_only_the_doctrine_board_opens_it(self):
        """The `generals_doctrine` shot presses the toggle through the screen's
        own meta road; no other Generals board carries the step."""
        spec = importlib.util.spec_from_file_location("_uxr4_runner", REPO / "tools" / "iq10_run_captures.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        press = {"call": "_on_meta_clicked", "args": ["doctrine:toggle"], "then_wait": 4}
        by_id = {s["id"]: s for s in runner.SHOTS}
        assert by_id["generals_doctrine"]["steps"] == [press]
        for sid, shot in by_id.items():
            if sid.startswith("generals_") and sid != "generals_doctrine":
                assert press not in (shot.get("steps") or []), sid

    def test_d_the_presence_is_the_figure_as_applied_where_he_stands(self):
        line = _func(self.SRC, "_presence_applied_line")
        # Read from the backend's own sentence (NPC-D1) — never recomputed.
        assert "Today it stands at" in line and r"\\+(\\d+)%" in line
        assert '" here at " + held_at' in line and 'm.get("location", "")' in line
        assert '+ str(applied_pct) + "%" + here' in line
        # The star is gold at the full figure and lerps toward the grey ink as it falls.
        assert "lerp(" in line and "1.0 - lit" in line and "★" in line
        ability = _func(self.SRC, "_ability_line")
        assert _order(ability, 'bool(m.get("sovereign", false))', "_presence_applied_line(m, ab_name, ab_effect)")
        # a marshal's plain ability line is untouched
        assert "COLOR_GOLD + \"]\" + ab_name" in ability

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_e_t20_leads_with_the_roster_not_the_doctrine(self, res):
        seen = _seen("generals_t20", res)
        assert "▸ the doctrine" in seen
        assert "Flaw — Living off the land" not in seen        # the block is folded
        assert _at(seen, "OUR DOCTRINE") < _at(seen, "THE LAURELS OF THE ARMY") < _at(seen, "[1] Ney")

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_f_np_field_states_the_presence_as_applied(self, res):
        seen = _seen("generals_np_field", res)
        assert "+10% here at Bohemia" in seen
        assert _at(seen, "THE EMPEROR") < _at(seen, "The Presence  +10% here at Bohemia") < _at(seen, "Strength:")
        assert "Flaw — Living off the land" not in seen

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_g_the_doctrine_board_opens_it_above_the_emperor(self, res):
        seen = _seen("generals_doctrine", res)
        assert "▾ hide the doctrine" in seen
        assert _at(seen, "OUR DOCTRINE") < _at(seen, "Strength — The corps system") \
            < _at(seen, "Flaw — Living off the land") < _at(seen, "THE EMPEROR")

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_h_a_captive_leads_and_the_doctrine_stays_one_line(self, res):
        """UXR3-24's part-2 order stands: what asks for attention leads (a
        captured marshal, in his header), then the one-line doctrine, then the
        Emperor — whose card opens on his state, the captive's included."""
        prisoner = _seen("generals_prisoner", res)
        assert _at(prisoner, "A PRISONER — Ney: PRISONER of the Kingdom of Italy since T1.") < _at(prisoner, "[1] Ney")
        assert "Flaw — Living off the land" not in prisoner
        captive = _seen("generals_np_captive", res)
        assert "▸ the doctrine" in captive and "Flaw — Living off the land" not in captive
        assert _at(captive, "OUR DOCTRINE") < _at(captive, "THE EMPEROR") < _at(captive, "A captive — PRISONER of Austria")

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_i_the_star_dims_with_the_figure(self, res):
        """The backend's own NPC-D1 sentence ("Today it stands at +4% — his
        star dims", "+0% — his star is out") drives the figure the line states.
        The two check frames carry a payload edit and say so in their staging."""
        dim, out = _frame("generals_np_field_dim", res), _frame("generals_np_field_out", res)
        assert "payload edit" in dim["staging"] and "payload edit" in out["staging"]
        assert "The Presence  +4% here at Bohemia" in _seen("generals_np_field_dim", res)
        assert "The Presence  +0% here at Bohemia" in _seen("generals_np_field_out", res)


class TestUXR3_80:
    """The boot board: one cause with UXR3-24 — the Emperor's card leads the
    first screenful, the doctrine one line above it."""

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_a_the_boot_generals_open_on_the_emperor(self, res):
        seen = _seen("generals_boot", res)
        assert "▸ the doctrine" in seen
        assert "Flaw — Living off the land" not in seen and "Strength — The corps system" not in seen
        assert _at(seen, "OUR DOCTRINE") < _at(seen, "THE EMPEROR") < _at(seen, "Napoleon")
        # the Presence reads as applied on the card that leads
        assert _at(seen, "THE EMPEROR") < _at(seen, "+10% here at Lorraine") < _at(seen, "Strength:")
        # nothing sits between the doctrine's title line and the Emperor's header but the gap
        gap = seen[_at(seen, "OUR DOCTRINE"):_at(seen, "THE EMPEROR")]
        assert len(gap.splitlines()) <= 3, gap

    def test_b_the_cause_is_the_one_fold(self):
        """UXR3-80 is UXR3-24's cause: the same `_render_doctrine` fold serves both."""
        all_cards = _func(_src("marshal_management.gd"), "_render_all_cards")
        assert _order(all_cards, "bbcode += _render_doctrine()", "]THE EMPEROR[/color]", "_render_glory_ladder()")


class TestUXR3_29:
    """The Nations book leads with the courts' cards."""

    SRC = _src("diplomatic_ledger.gd")

    def test_a_the_france_blocks_close_the_book(self):
        body = _func(self.SRC, "_render_nations")
        assert _order(body, "var france_blocks := \"\"", "How Europe Reads France",
                      "The Emperor's Own Exposure", "for n in nations:", "bbcode += france_blocks",
                      "content_area.text = bbcode")
        # neither block is written to the page head any more
        head = body[:body.index("for n in nations:")]
        assert "bbcode += \"[color=#\" + Utils.COLOR_GOLD + \"][b]How Europe Reads France" not in head
        assert "bbcode += \"[color=#\" + Utils.COLOR_GOLD + \"][b]The Emperor's Own Exposure" not in head

    def test_b_an_empty_court_list_still_shows_the_blocks(self):
        body = _func(self.SRC, "_render_nations")
        empty = body[body.index("if nations.size() == 0:"):body.index("for n in nations:")]
        assert "bbcode += \"\\n\" + france_blocks" in empty and "return" in empty

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_c_britains_laws_and_every_visible_doctrine_lead(self, res):
        seen = _seen("diplo_laws_rival_nations", res)
        assert _at(seen, "NATION OVERVIEW") < _at(seen, "Britain") < _at(seen, "Laws: the Orders in Council") \
            < _at(seen, "Doctrine: The Line Holds")
        assert "How Europe Reads France" not in seen and "The Emperor's Own Exposure" not in seen
        seen = _seen("diplo_doctrine_nations", res)
        assert _at(seen, "Britain") < _at(seen, "Doctrine: The Line Holds") < _at(seen, "Russia [Coalition Member]") \
            < _at(seen, "Doctrine: Stubborn; flaw: Slow to concentrate")
        assert "How Europe Reads France" not in seen


class TestUXR3_79:
    """The land's note rides under the controller line, above ACTIONS."""

    SRC = _src("region_panel.gd")

    def test_a_the_note_is_taken_once_before_the_actions_splice(self):
        body = _func(self.SRC, "_render")
        assert body.count('data.get("doctrine_supply")') == 1
        assert _order(body, "# ── Controller + terrain ──", 'var dmark = data.get("doctrine_supply")',
                      "var actions_at := bbcode.length()", "One province — who holds it",
                      "# ── Fog-honest economy block ──")
        assert "bbcode = bbcode.substr(0, actions_at) + actions" in body

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_b_posen_reads_the_poor_mark_under_the_controller(self, res):
        seen = _seen("region_doctrine_posen", res)
        assert _at(seen, "Prussia") < _at(seen, "Poor country — a French army here draws 80%") \
            < _at(seen, "One province — who holds it") < _at(seen, "Supply:")

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_c_tyrol_reads_the_stripped_mark_above_the_actions(self, res):
        seen = _seen("region_doctrine_tyrol", res)
        assert _at(seen, "Austria") < _at(seen, "Stripped by war (35%)") < _at(seen, "ACTIONS") \
            < _at(seen, "One province — who holds it") < _at(seen, "War damage: 35%")


class TestUXR3_81:
    """The Vassals book lists a court with a granted petition first, its Bond
    line leading its card."""

    SRC = _src("diplomatic_ledger.gd")

    def test_a_a_granted_court_is_listed_first(self):
        body = _func(self.SRC, "_render_vassals")
        assert _order(body, "granted_rows", "other_rows", "_vassal_petition_granted(v)",
                      "for v in granted_rows + other_rows:", "_format_vassal_card(v,")
        granted = _func(self.SRC, "_vassal_petition_granted")
        # the grant's two marks: the bond it earned and the tribute it remitted
        assert 'v.get("relation_modifier", 0)) > 0' in granted and 'v.get("remission_left", 0)) > 0' in granted

    def test_b_the_bond_line_leads_the_card(self):
        card = _func(self.SRC, "_format_vassal_card")
        assert _order(card, "var bond_led: bool", "Bond: [color=#", "# ── Loyalty bar + trend forecast ──")
        # the later Bond line is kept for a court the grant has not reached
        assert 'if v.has("bond") and not bond_led:' in card and 'v.has("bond")' in card

    @pytest.mark.parametrize("res", RESOLUTIONS)
    def test_c_the_granted_court_and_its_bond_are_the_first_screenful(self, res):
        seen = _seen("diplo_petition_granted_vassals", res)
        assert _at(seen, "CLIENT STATES") < _at(seen, "Switzerland") < _at(seen, "Bond: +1/turn") \
            < _at(seen, "Loyalty 100/100") < _at(seen, "Holland")
        # the bond's own words, and not the "no bond yet" of the ungranted cards, lead
        assert "a bond worth one honoured petition" in seen
        assert _at(seen, "Bond: +1/turn") < (seen.find("no bond yet") if "no bond yet" in seen else 10 ** 9)

"""Row IC "Independent Command", the desk (November 19, 2026) — IC-3: what was hidden.

Three things the game already knew and no screen said: that a first-time player has a guided lesson two rows
below "Begin"; that a marshal acted WITHOUT ORDERS this turn (the reply has always carried
`independent_command_report`; it was a terse block in the log and no client script read it); and that a
jealous man may attack on his own tonight, or a literal man resents being left out (both are TO DECIDE rows
now — pinned in `tests/test_ic1_the_desk.py`). Styling, focus and words only: nothing is renamed, moved or
shut, and no rule changes.
"""

from __future__ import annotations

import pathlib
import re

from backend.game_logic import while_you_waited as WYW

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


def _src(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _func(source: str, name: str) -> str:
    match = re.search(rf"^(?:static )?func {re.escape(name)}\(.*?(?=^\S|\Z)", source, re.S | re.M)
    assert match, f"no func {name}"
    return match.group(0)


REPORT = [
    {"marshal": "Ney", "action": "attack", "target": "Mack", "turns_remaining": 2,
     "performance": {"battles_won": 1, "battles_lost": 0, "regions_captured": 0},
     "result": {"message": "x"}},
    {"marshal": "Davout", "action": "wait", "target": None, "turns_remaining": 1,
     "performance": {"battles_won": 0, "battles_lost": 0, "regions_captured": 0}},
    {"marshal": "Murat", "action": "move", "target": "Bavaria", "turns_remaining": 0, "autonomy_ended": True,
     "end_result": {"tier": "success", "message": "Murat performed well independently. Trust +25."}},
]


# ═════════════════════════════════════════════════════════════════════════════
# 1. A marshal who acted without orders is said, in plain words
# ═════════════════════════════════════════════════════════════════════════════

class TestAManActingWithoutOrdersIsReported:
    def test_one_plain_line_each(self):
        rows = WYW._own_way(REPORT)
        assert [r["marshal"] for r in rows] == ["Ney", "Davout", "Murat"]
        # the morning after: said in the past tense (the review)
        assert rows[0]["line"] == "Ney acted without orders: he attacked Mack. He acts on his own for 2 more turns."
        assert rows[1]["line"] == ("Davout acted without orders: he held his position. He acts on his own for "
                                   "1 more turn.")
        assert rows[2]["line"] == ("Murat acted without orders: he marched to Bavaria. He is under your orders "
                                   "again. Murat performed well independently. Trust +25.")
        assert rows[2]["ended"] is True and rows[0]["ended"] is False
        for row in rows:
            assert "_" not in row["line"], row["line"]              # no internal verb in the words
            assert isinstance(row["turns_left"], int)

    def test_an_enemy_he_went_for_is_named_only_where_the_player_knows_him(self):
        """The review (IC-R3): the man chose his quarry with the AI's eyes. An enemy the player
        cannot see and did not fight is "an enemy corps" — in the report AND in the log's block."""
        import contextlib
        import io as _io
        import json
        from backend.models.intel import RegionIntel
        from backend.models.world_state import WorldState
        scenario = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
        with contextlib.redirect_stdout(_io.StringIO()):
            world = WorldState.from_dict(json.loads(json.dumps(
                WorldState.from_scenario(str(scenario)).to_dict(), default=str)))
        mack = world.marshals["Mack"]
        intel = world.intel.get(mack.location)
        if intel is None:
            intel = world.intel[mack.location] = RegionIntel(mack.location)
        entry = {"marshal": "Ney", "action": "attack", "target": "Mack", "turns_remaining": 2,
                 "result": {"success": False, "message": "No enemy there."}}
        intel.visibility = "unknown"
        assert WYW.own_way_target(world, entry) == "an enemy corps"
        assert WYW._own_way([entry], world)[0]["line"] == (
            "Ney acted without orders: he attacked an enemy corps. He acts on his own for 2 more turns.")
        intel.visibility = "partial"                                    # he stands in sight now
        assert WYW.own_way_target(world, entry) == "Mack"
        intel.visibility = "unknown"
        fought = dict(entry, result={"battle_won": True})               # a battle was fought with him
        assert WYW.own_way_target(world, fought) == "Mack"
        # a province, one of our own men and a name the roster does not hold are said as they are
        assert WYW.own_way_target(world, {"target": "Bavaria"}) == "Bavaria"
        assert WYW.own_way_target(world, {"target": "Davout"}) == "Davout"
        assert WYW.own_way_target(world, {"target": None}) == ""
        # … and the log's older block reads the same rule (the sibling)
        block = (REPO / "backend" / "commands" / "meta_executor.py").read_text(encoding="utf-8")
        report = block[block.index("═══ INDEPENDENT COMMAND REPORT ═══"):block.index("# FINANCIAL SUMMARY")]
        assert "own_way_target(world, entry) or target" in report
        assert 'action_str += f" {target}"' not in report

    def test_a_verb_with_no_place_does_not_dangle(self):
        rows = WYW._own_way([{"marshal": "Ney", "action": "retreat", "target": None, "turns_remaining": 1}])
        assert rows[0]["line"] == "Ney acted without orders: he fell back. He acts on his own for 1 more turn."

    def test_nothing_to_say_is_nothing_said(self):
        assert WYW._own_way(None) == [] and WYW._own_way([]) == []
        assert WYW._own_way([{"action": "attack"}, "x", None]) == []

    def test_the_turn_s_summary_carries_it_and_is_no_longer_quiet(self):
        class _Board:
            player_nation = "France"
            regions: dict = {}
            current_turn = 3

            def get_visible_enemies(self, nation):
                return []

            def get_player_marshals(self):
                return []
        before = {"turn": 2, "regions": {}, "garrisons": {}, "corps": {}, "places": {}, "wars": []}
        told = WYW.digest(_Board(), before, None, None, own_way=REPORT)
        assert [r["marshal"] for r in told["own_way"]] == ["Ney", "Davout", "Murat"]
        assert told["quiet"] is False
        quiet = WYW.digest(_Board(), before, None, None)
        assert "own_way" not in quiet and quiet["quiet"] is True

    def test_the_turn_hands_its_report_to_the_summary(self):
        attach = (REPO / "backend" / "game_logic" / "while_you_waited.py").read_text(encoding="utf-8")
        body = attach[attach.index("def attach("):attach.index("def snapshot(")]
        assert 'own_way=result.get("independent_command_report")' in body

    def test_the_seam_down_is_the_summary_as_it_was(self, monkeypatch):
        monkeypatch.setattr(WYW, "a_man_acting_without_orders_is_reported", lambda: False)

        class _Board:
            player_nation = "France"
            regions: dict = {}
            current_turn = 3

            def get_visible_enemies(self, nation):
                return []

            def get_player_marshals(self):
                return []
        before = {"turn": 2, "regions": {}, "garrisons": {}, "corps": {}, "places": {}, "wars": []}
        told = WYW.digest(_Board(), before, None, None, own_way=REPORT)
        assert "own_way" not in told and told["quiet"] is True

    def test_the_report_after_end_turn_shows_it(self):
        block = _func(_src("enemy_phase_dialog.gd"), "_wyw_block")
        assert 'var own_way = d.get("own_way", [])' in block
        assert "[b]Acting without orders[/b]" in block
        assert block.index("Acting without orders") < block.index("Now next to you")


# ═════════════════════════════════════════════════════════════════════════════
# 2. The first time at the menu
# ═════════════════════════════════════════════════════════════════════════════

class TestTheFirstTimeAtTheMenu:
    MENU = _src("main_menu.gd")

    def test_no_row_is_renamed_moved_or_shut(self):
        build = _func(self.MENU, "_build_menu_column")
        rows = re.findall(r'_add_menu_button\("(\w+)", "([^"]+)"', build)
        assert rows == [
            ("return", "Return to the War Room"),
            ("begin", "Begin the 1805 Campaign"),
            ("tutorial", "The School of War — a guided campaign"),
            ("tutorial_table", "The School of War — The Table (a guided peace)"),
            ("continue", "Continue"),
            ("load", "Load a Campaign…"),
            ("settings", "Settings"),
            ("quit", "Quit to Desktop"),
        ]
        steer = _func(self.MENU, "_ic_steer_a_first_timer")
        # (the one `move_child` is the LINE's own — put just above the column in the draw
        # order, under the settings view: the review found it drawn over an open panel)
        cleaned = steer.replace("_ic_first_line.text = IC_FIRST_TIME_LINE", "").replace(
            "move_child(_ic_first_line, _menu_column.get_index() + 1)", "")
        for forbidden in (".text =", ".disabled =", "move_child", "remove_child", ".visible = false"):
            assert forbidden not in cleaned, forbidden
        assert "move_child(_ic_first_line, _menu_column.get_index() + 1)" in steer

    def test_a_first_time_machine_is_one_with_no_save_and_no_finished_lesson(self):
        first = _func(self.MENU, "_ic_first_time")
        assert "_ic_saves_known and _saves.is_empty() and not MenuBoot.came_from_game" in first
        assert "not UiSettings.get_tutorial_done()" in first
        # known only once the list of saves has come back
        assert "_ic_saves_known = true" in self.MENU.split('elif mode == "saves":')[1][:400]

    def test_the_school_s_row_is_lit_and_takes_the_keyboard_once(self):
        steer = _func(self.MENU, "_ic_steer_a_first_timer")
        assert "if _ic_steered or not _backend_up or not _ic_first_time():" in steer
        assert 'school.theme_type_variation = &"TitleScreenButtonProminent"' in steer
        assert "school.grab_focus()" in steer
        assert "_ic_steered = true" in steer
        # … but never from a box the player is typing in (the campaign seed) — the review
        assert "if not (holder is LineEdit):\n\t\tschool.grab_focus()" in steer

    def test_one_row_is_lit_while_the_steer_stands(self):
        """Lever L1 of the blind reading (all three readers: "TWO lit rows — not clear which one
        is the default"): "Begin" wears the plain face every other row wears. It is not shut."""
        steer = _func(self.MENU, "_ic_steer_a_first_timer")
        assert 'var begin: Button = _buttons.get("begin", null)' in steer
        assert 'begin.theme_type_variation = &"TitleScreenButton"' in steer
        assert "begin.disabled" not in steer and "begin.visible" not in steer
        assert "_fit_menu_column.call_deferred()" in steer        # the rows' heights follow their faces
        fit = _func(self.MENU, "_fit_menu_column")
        assert 'mb.theme_type_variation == &"TitleScreenButtonProminent"' in fit

    def test_the_line_says_what_it_is_and_that_it_can_be_left(self):
        line = re.search(r'const IC_FIRST_TIME_LINE := "([^"]+)"', self.MENU).group(1)
        assert line == ("New here? Start with the School of War — a short guided campaign you can leave at "
                        "any time.")
        # the review: "twelve short turns" was false (the Danube lesson gates on turn 14). No
        # count of turns is promised at all.
        assert not any(ch.isdigit() for ch in line) and "twelve" not in line

    def test_the_line_stands_beside_the_row_and_costs_the_column_no_height(self):
        """In the column it made the menu taller, and on a short window the title stepped aside
        for it (seen at 5120x1377, scale 1.8)."""
        steer = _func(self.MENU, "_ic_steer_a_first_timer")
        assert "add_child(_ic_first_line)" in steer
        assert "_menu_column.add_child(_ic_first_line)" not in steer
        seat = _func(self.MENU, "_ic_seat_first_line")
        assert "row.end.x + 16.0" in seat
        assert "school.tooltip_text = \"\" if _ic_first_line.visible else IC_FIRST_TIME_LINE" in seat   # no room: the hover

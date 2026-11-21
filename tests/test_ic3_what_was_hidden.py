"""Row IC "Independent Command", the desk (November 19, 2026) — IC-3: what was hidden.

Three things the game already knew and no screen said: that a first-time player has a guided lesson two rows
below "Begin"; that a marshal acted WITHOUT ORDERS this turn (the reply has always carried
`independent_command_report`; it was a terse block in the log and no client script read it); and that a
jealous man may attack on his own tonight, or a literal man resents being left out (both are TO DECIDE rows
now — pinned in `tests/test_ic1_the_desk.py`). Styling, focus and words only: nothing is renamed, moved or
shut, and no rule changes.

Row IC, Session 2b (November 20, 2026): the second of the three is re-seated. The engine that moved a marshal
"without orders" (the trust crisis's "Grant Autonomy") is removed, with its report; the man out of the player's
hands is now the one on his TASK TO PROVE HIMSELF, and the first class below pins that what HE does is said in
plain words. (The jealous strike's words are "without waiting for orders" now: "on his own" is kept for the man
the Emperor sets on his own.)
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


def _board():
    """The shipped 1805 board, Ney moved to Franconia (beside Austrian Bohemia)."""
    import contextlib
    import io as _io
    from backend.models.world_state import WorldState
    scenario = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
    with contextlib.redirect_stdout(_io.StringIO()):
        world = WorldState.from_scenario(str(scenario))
        world.marshals["Ney"].location = "Franconia"
        world._build_marshal_index()
        world.calculate_visibility()
    return world


def _quietly(fn, *args, **kwargs):
    import contextlib
    import io as _io
    with contextlib.redirect_stdout(_io.StringIO()):
        return fn(*args, **kwargs)


# ═════════════════════════════════════════════════════════════════════════════
# 1. A marshal who is out of your hands is said, in plain words
# ═════════════════════════════════════════════════════════════════════════════
#
# IC-3 found that a marshal ACTED WITHOUT ORDERS and no screen said so: the
# trust crisis's "Grant Autonomy" handed him to the enemy's decision logic for
# three turns, and the reply's `independent_command_report` was read by no
# client script (`while_you_waited._own_way` then said it in one plain line).
#
# Row IC, Session 2b (November 20, 2026) removed that engine, its report and
# `_own_way` with it. The man who is out of the player's hands now is the one
# on his TASK TO PROVE HIMSELF — and the promise this class pinned is kept
# for him: what he does is said, in plain words, where the player reads the
# turn (the standing orders' rows, the turn's events, the summary).

class TestAManOnHisTaskIsReported:
    def test_one_plain_line_each(self):
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.game_logic import trial
        world = _board()
        ney = world.marshals["Ney"]
        given = _quietly(trial.give, world, ney)
        executor = CommandExecutor()
        rows = _quietly(StrategicOrderProcessor(executor).process_strategic_orders,
                        world, {"world": world, "executor": executor})
        took = next(r for r in rows if r.get("marshal") == "Ney")
        assert took["message"] == "Ney marches on Bohemia, as he proposed. Bohemia is ours."
        ney.battles_won += 1                                   # ... he won a battle on each turn
        _quietly(trial.tick, world)
        ney.battles_won += 1
        _quietly(trial.tick, world)
        ney.battles_won += 1
        pressed = _quietly(trial.tick, world)                  # his last turn ended on a victory
        assert pressed[0]["message"].startswith(
            "Ney is on a roll — last turn he won a battle and lost none. He presses on with his "
            "task one more turn")
        over = _quietly(trial.tick, world)                     # a turn with no victory: it ends
        # (the review, IC2B-X19: Bohemia stood open — he walked in — and the
        # morning says so; the old pin here was an `or` whose first arm could
        # never match)
        assert over[0]["message"].startswith(
            "Ney has proved himself. In 4 turns he won 3 battles and took 1 place that nobody "
            "defended. His trust in you rises by ")
        assert over[0]["message"].endswith(" He is under your orders again.")
        for line in (given["message"], took["message"], pressed[0]["message"], over[0]["message"],
                     trial.status_words(world.marshals["Davout"]) or "x"):
            assert "_" not in line, line                       # no internal word in the words
            for hidden in ("trial", "HOLD", "opening_take", "autonom", "independent"):
                assert hidden not in line, (hidden, line)

    def test_an_enemy_he_goes_for_is_named_only_where_the_player_knows_him(self):
        """The review (IC-R3) found the old report naming a quarry the man
        had chosen "with the AI's eyes". The task is proposed from what
        FRANCE sees: an enemy corps the player cannot see is named nowhere —
        not in the proposal, not in the order's line."""
        from backend.game_logic import trial
        from backend.models.intel import RegionIntel
        world = _board()
        ney = world.marshals["Ney"]
        charles = world.marshals["ArchdukeCharles"]
        charles.location = "Bohemia"                           # a corps stands on his target
        charles.strength = 9000
        world._build_marshal_index()
        intel = world.intel.get("Bohemia")
        if intel is None:
            intel = world.intel["Bohemia"] = RegionIntel("Bohemia")
        intel.visibility = "unknown"                           # ... and France cannot see it
        unseen = _quietly(trial.proposal, world, ney)
        assert "Charles" not in unseen["words"] and "Charles" not in unseen["line"]
        assert unseen["foe"] == ""
        intel.visibility = "full"                              # he stands in sight now
        seen = _quietly(trial.proposal, world, ney)
        assert seen["place"] == "Bohemia" and seen["foe"] == "ArchdukeCharles"   # (the roster's key)
        assert "where Archduke Charles stands" in seen["words"]

    def test_a_hold_with_nothing_beside_it_does_not_dangle(self):
        from backend.game_logic import trial
        world = _board()
        read = trial.proposal(None, world.marshals["Davout"])  # no board to read: no friend, no place to take
        assert read["line"] == "Davout, hold Alsace." or read["line"].startswith("Davout, hold ")
        assert read["line"].endswith(".") and "  " not in read["line"] and "None" not in read["line"]
        assert read["words"].endswith(".") and "None" not in read["words"]

    def test_nothing_to_say_is_nothing_said(self):
        from backend.game_logic import trial
        world = _board()
        kept = [{"marshal": "Davout", "message": "kept"}]
        assert _quietly(trial.close_of_turn, world, kept) == kept
        assert _quietly(trial.tick, world) == []
        assert trial.morning_events(world) == []
        assert trial.status_words(world.marshals["Ney"]) == ""
        assert trial.payload(world.marshals["Ney"]) is None

    def test_the_turn_s_summary_carries_it_and_is_no_longer_quiet(self):
        """The province he took on his task is in the summary of the turn —
        which is then no quiet turn."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.game_logic import trial
        world = _board()
        ney = world.marshals["Ney"]
        before = WYW.before(world)
        quiet = WYW.digest(world, before, None, None)
        assert quiet["quiet"] is True and quiet["gained"] == []
        _quietly(trial.give, world, ney)
        executor = CommandExecutor()
        _quietly(StrategicOrderProcessor(executor).process_strategic_orders,
                 world, {"world": world, "executor": executor})
        told = WYW.digest(world, before, None, None)
        assert [row["region"] for row in told["gained"]] == ["Bohemia"]
        assert told["quiet"] is False
        assert "own_way" not in told

    def test_the_turn_hands_the_morning_its_lines(self):
        manager = (REPO / "backend" / "game_logic" / "turn_manager.py").read_text(encoding="utf-8")
        # (row IC, Session 3: the trial's lines and the nights on his own, told once)
        assert "tactical_events.extend(_their_mornings(self.world))" in manager
        assert "list(_trial.morning_events(world)) + list(_own.morning_events(world))" in manager
        assert "_trial.close_of_turn(self.world, strategic_reports)" in manager
        attach = (REPO / "backend" / "game_logic" / "while_you_waited.py").read_text(encoding="utf-8")
        body = attach[attach.index("def attach("):attach.index("def snapshot(")]
        assert "own_way" not in body and "independent_command_report" not in body

    def test_the_old_report_and_its_seam_are_gone(self):
        import inspect
        for gone in ("_own_way", "own_way_target", "a_man_acting_without_orders_is_reported"):
            assert not hasattr(WYW, gone), gone
        assert "own_way" not in inspect.signature(WYW.digest).parameters
        block = (REPO / "backend" / "commands" / "meta_executor.py").read_text(encoding="utf-8")
        assert "INDEPENDENT COMMAND REPORT" not in block
        assert "independent_command_report" not in block

    def test_the_report_after_end_turn_shows_it(self):
        """The client: the old "Acting without orders" block is gone from the
        turn's report, and the task's lines print with the turn's events and
        the standing orders' rows (each once — `tests/test_autonomy.py`)."""
        block = _func(_src("enemy_phase_dialog.gd"), "_wyw_block")
        assert "own_way" not in block and "Acting without orders" not in block
        main = _src("main.gd")
        assert "independent_command_report" not in main
        events = main[main.index("# Display tactical events (supply attrition, occupation updates)"):]
        assert 'var msg = str(event.get("message", ""))' in events[:600]
        rows = _func(main, "_show_strategic_reports")
        assert 'var msg = report.get("message", "")' in rows


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

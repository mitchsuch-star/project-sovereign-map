"""FA slice 16 (part a) — "THE NAVAL FIGURE NAMES WHOSE IT IS".

Five rows, one rule: **a naval figure names whose it is, and a naval refusal
states every gate it already knows it will hit.** FA-58, FA-59, FA-45,
FA-51, FA-64.

The through-line the reproduction pass found: the naval surface reported the
smaller of two true causes, or the larger of two true figures, and in both
directions it flattered the wrong actor. FA-45 credited a fall to the keel
when the blockade had done all of it. FA-59 credited France with losses two
allies took. FA-58 credited the enemy's blockade with HEALING the fleet it
had beaten. FA-51 and FA-64 each stated the smaller of two refusals the game
already knew.

Reproduction of record: `docs/audits/fa_build_2026_09_04/repro/
REPRO_L_slice16_at_head.md`, group `FA-45, FA-51, FA-58, FA-59, FA-64`.
Landing record: the boxed SLICE 16 (part a) block in `docs/BUG_FIXES.md`.
"""

import contextlib
import io
import os
import pathlib
import re

import pytest

from backend.commands.naval_executor import (NavalExecutor,
                                             _blockade_rot_clause,
                                             _detachment_echo,
                                             _green_crew_clause)
from backend.game_logic import naval
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" /
               "maps" / "europe_1805.json")


@pytest.fixture
def world():
    os.environ.setdefault(
        "INK_IRON_SAVE_DIR",
        str(pathlib.Path(os.environ.get("TEMP", "/tmp")) / "fa_s16a_saves"))
    pathlib.Path(os.environ["INK_IRON_SAVE_DIR"]).mkdir(parents=True,
                                                        exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════
# FA-58 — the blockade floor is a floor on the ROT, not on the fleet
# ═══════════════════════════════════════════════════════════════════════════

class TestTheBlockadeDoesNotHealTheFleetItBeat:

    @pytest.mark.parametrize("start", [1, 20, 40, 45, 49, 50])
    def test_a_fleet_at_or_below_the_floor_is_not_lifted(self, world, start):
        rec = naval.get_fleet(world, "France")
        assert "France" in naval.blockaded_nations(world)
        rec["readiness"] = start
        _quiet(naval._readiness_tick, world)
        assert rec["readiness"] == start, (
            "the enemy's blockade healed the fleet it had just beaten")

    @pytest.mark.parametrize("start,expected", [(52, 50), (55, 50), (70, 65)])
    def test_the_rot_still_bites_above_the_floor(self, world, start, expected):
        rec = naval.get_fleet(world, "France")
        rec["readiness"] = start
        _quiet(naval._readiness_tick, world)
        assert rec["readiness"] == expected

    def test_the_two_roads_that_reach_it(self, world):
        """Not hypothetical. A failed Grand Diversion sets readiness below
        the floor, and a small blockaded navy folds itself under it with one
        green keel — measured, Holland at 12 sail goes 50 -> 49."""
        holland = naval.get_fleet(world, "Holland")
        assert "Holland" in naval.blockaded_nations(world)
        holland["readiness"] = 50
        holland["ships"] = 12
        outcome = naval.lay_down_ship(world, "Holland")
        assert outcome["readiness"] == 49
        _quiet(naval._readiness_tick, world)
        assert holland["readiness"] == 49, "one keel, healed by the blockade"

    def test_the_diversion_road(self, world):
        rec = naval.get_fleet(world, "France")
        rec["readiness"] = 50
        assert naval.diversion_failure_readiness(rec) < 50
        rec["readiness"] = naval.diversion_failure_readiness(rec)
        beaten = rec["readiness"]
        _quiet(naval._readiness_tick, world)
        assert rec["readiness"] == beaten


# ═══════════════════════════════════════════════════════════════════════════
# FA-59 — a figure names whose it is
# ═══════════════════════════════════════════════════════════════════════════

ACTION = {"losses": {"France": {"France": 25, "Spain": 17, "Holland": 7},
                     "Britain": {"Britain": 4, "Russia": 1}},
          "loser": "France", "winner": "Britain", "decisive": True}


class TestTheLossFigureNamesWhoseItIs:

    def test_the_own_figure_is_not_the_pooled_one(self):
        assert naval.own_ships_lost(ACTION, "France") == 25
        assert naval.own_ships_lost(ACTION, "Spain") == 17
        assert naval.own_ships_lost(ACTION, "Britain") == 4

    def test_the_helper_is_nation_parameterised_not_loser_keyed(self):
        """Two of the three call sites ask about the DIVERTING or the
        MARCHING court, which is not necessarily the loser — a loser-keyed
        field would leave both reading the wrong side."""
        assert naval.own_ships_lost(ACTION, "Russia") == 1
        assert naval.allied_ships_lost(ACTION, "Britain") == {"Russia": 1}

    def test_the_allies_are_named_not_absorbed(self):
        assert naval.losses_sentence(ACTION, "France") == (
            "France loses 25 sail; Spain 17 and Holland 7 beside her")

    def test_a_lone_fleet_says_only_its_own(self):
        solo = {"losses": {"France": {"France": 9}, "Britain": {"Britain": 2}}}
        assert naval.losses_sentence(solo, "France") == "France loses 9 sail"

    def test_an_unknown_court_reads_zero_not_a_crash(self):
        assert naval.own_ships_lost(ACTION, "Sweden") == 0
        assert naval.allied_ships_lost(ACTION, "Sweden") == {}
        assert naval.losses_sentence({}, "France") == "France loses 0 sail"

    def test_the_dispatch_beat_carries_the_own_figure(self, world):
        """The beat said "49 sail lost" while France held 45."""
        import inspect
        src = inspect.getsource(naval._log_fleet_action)
        assert "own_ships_lost(result, result[\"loser\"])" in src
        assert "sum(result[\"losses\"]" not in src

    def test_the_diversion_message_reads_the_shared_source(self):
        import inspect
        src = inspect.getsource(naval.resolve_diversion)
        assert "own_ships_lost(action, nation)" in src
        assert "losses_sentence(action, nation)" in src

    def test_the_expedition_intercept_reads_it_too(self):
        src = (REPO / "backend" / "commands" / "naval_executor.py").read_text(
            encoding="utf-8")
        assert "naval.losses_sentence(action, marshal.nation)" in src
        assert "sum(action['losses']" not in src

    def test_the_diorama_is_deliberately_left_alone(self):
        """⚠ The FOURTH consumer is by design. `naval_diorama._side` sums the
        whole side because the tableau disaggregates per squadron beside it
        (the NV-9 comment says so), and two pins assert that sum. A
        "make it the own figure everywhere" sweep would red both and reverse
        a landed design decision."""
        src = (REPO / "backend" / "game_logic" / "naval_diorama.py").read_text(
            encoding="utf-8")
        assert "own_ships_lost" not in src


# ═══════════════════════════════════════════════════════════════════════════
# FA-45 — the keel receipt names the real cause
# ═══════════════════════════════════════════════════════════════════════════

class TestTheKeelReceiptNamesTheRealCause:

    def test_both_return_arms_carry_readiness_before(self, world):
        """⚠ The 0-ship arm IS reachable: `check_build_fleet` returns None
        for a fleet annihilated at Trafalgar, so the next keel takes it, and
        a caller reading the key off the other arm alone would KeyError."""
        rec = naval.get_fleet(world, "France")
        rec["ships"] = 45
        rec["readiness"] = 70
        assert "readiness_before" in naval.lay_down_ship(world, "France")
        rec["ships"] = 0
        assert "readiness_before" in naval.lay_down_ship(world, "France")

    def test_a_keel_that_cost_nothing_says_so(self):
        clause = _green_crew_clause({"readiness_before": 58, "readiness": 58})
        assert "cost her nothing" in clause
        assert "down" not in clause

    def test_a_keel_that_cost_something_quotes_the_real_delta(self):
        clause = _green_crew_clause({"readiness_before": 70, "readiness": 69})
        assert "down 1" in clause

    def test_a_fleet_rebuilt_from_nothing_says_so(self):
        clause = _green_crew_clause({"readiness_before": 0, "readiness": 40})
        assert "rebuilt from nothing" in clause

    def test_the_blockade_is_named_with_its_number(self, world):
        clause = _blockade_rot_clause(world, "France")
        assert "Britain" in clause
        assert str(naval.READINESS_TICK) in clause

    def test_an_unblockaded_navy_hears_nothing_about_a_blockade(self, world):
        assert _blockade_rot_clause(world, "Britain") == ""

    def test_the_receipt_itself_names_the_blockade(self, world):
        """The clause helper is not enough — the RECEIPT has to interpolate
        it. Measured before: four keels in a row printed a falling readiness
        and the word "blockade" appeared on none of them."""
        rec = naval.get_fleet(world, "France")
        rec["ships"], rec["readiness"], rec["built_this_turn"] = 45, 70, 0
        world.nation_gold["France"] = 9999
        out = _quiet(NavalExecutor(None)._execute_build_fleet,
                     {"action": "build_fleet"}, {"world": world})
        assert "blockade" in out["message"]
        assert str(naval.READINESS_TICK) in out["message"]

    def test_the_receipt_does_not_dump_the_trade_paragraph(self, world):
        """⚠ The filed fix said to reuse `blockade_forecast_sentence`. It
        returns a three-clause paragraph about Continental-System trade
        closure and never states the per-turn number — a shipbuilding
        receipt needs one clause and a figure the player can act on."""
        clause = _blockade_rot_clause(world, "France")
        assert "trade" not in clause.lower()
        assert len(clause) < 140

    def test_four_consecutive_keels_stop_blaming_the_crews(self, world):
        """The measured sequence: fold −1, −1, 0, 0 while readiness falls
        69/63/58/53. From the third keel the message was blaming green crews
        for a fall the keel had not caused at all."""
        rec = naval.get_fleet(world, "France")
        rec["ships"], rec["readiness"] = 45, 70
        ex = NavalExecutor(None)
        blamed = []
        for _ in range(4):
            rec["built_this_turn"] = 0
            world.nation_gold["France"] = 9999
            out = _quiet(ex._execute_build_fleet, {"action": "build_fleet"},
                         {"world": world})
            blamed.append("cost her nothing" in out["message"])
            _quiet(naval._readiness_tick, world)
        assert blamed == [False, False, True, True], blamed


# ═══════════════════════════════════════════════════════════════════════════
# FA-51 — the lift is the first word, and the figure typed is read
# ═══════════════════════════════════════════════════════════════════════════

class TestTheExpeditionStatesTheGateItWillHit:

    @staticmethod
    def _soult(world, location, strength=30000):
        m = world.get_marshal("Soult")
        m.location = location
        m.strength = strength
        return m

    def test_an_over_lift_corps_hears_about_the_lift_first(self, world):
        """It used to be sent to a yard and told AT the yard that the
        transports carry 15,000 — the road offered led to a wall."""
        self._soult(world, "Lorraine")
        out = _quiet(NavalExecutor(None)._execute_naval_expedition,
                     {"action": "naval_expedition", "target": "Munster",
                      "marshal": "Soult"}, {"world": world})
        assert out["success"] is False
        assert "transports lift" in out["message"]
        assert "must stand at one of our yards" not in out["message"]

    def test_a_corps_within_the_lift_still_hears_about_the_yard(self, world):
        self._soult(world, "Lorraine", strength=9000)
        out = _quiet(NavalExecutor(None)._execute_naval_expedition,
                     {"action": "naval_expedition", "target": "Munster",
                      "marshal": "Soult"}, {"world": world})
        assert out["success"] is False
        assert "must stand at one of our yards" in out["message"]

    def test_the_inland_abroad_arm_is_NOT_outranked(self, world):
        """⚠ The filed fix said only "evaluate the lift before the embark
        position". Hoisting it blind puts it above the inland-abroad arm
        too, so a 30,000-man corps standing inland on FOREIGN soil is told
        about the lift and never about the coast — the identical defect
        mirrored. The lift goes above the YARD arm only."""
        import inspect
        src = inspect.getsource(NavalExecutor._execute_naval_expedition)
        i_lift = src.index("_over_lift = ")
        i_yard = src.index("must stand at one of our yards")
        i_inland = src.index("stands inland at")
        assert i_lift < i_yard, "the lift must outrank the yard"
        assert i_lift < i_inland, (
            "the lift is sited above the inland arm too — the behavioural "
            "pin below is what makes that safe; read them together")

    def test_a_big_corps_inland_abroad_hears_about_the_coast(self, world):
        """The behavioural half of the pin above."""
        m = self._soult(world, "Swabia")
        assert world.regions["Swabia"].controller != m.nation
        out = _quiet(NavalExecutor(None)._execute_naval_expedition,
                     {"action": "naval_expedition", "target": "Munster",
                      "marshal": "Soult"}, {"world": world})
        assert out["success"] is False
        # He is over the lift AND inland abroad. The lift is the property of
        # the corps and holds wherever he stands, so it is the honest first
        # word — but the coast clause must still be reachable for a corps
        # that is only inland.
        assert "transports lift" in out["message"]
        m.strength = 9000
        out = _quiet(NavalExecutor(None)._execute_naval_expedition,
                     {"action": "naval_expedition", "target": "Munster",
                      "marshal": "Soult"}, {"world": world})
        assert "the boats" in out["message"] and "coast" in out["message"]

    def test_the_typed_figure_is_echoed(self, world):
        self._soult(world, "Lorraine")
        out = _quiet(NavalExecutor(None)._execute_naval_expedition,
                     {"action": "naval_expedition", "target": "Munster",
                      "marshal": "Soult",
                      "raw_input": "land Soult in Munster with 12,000 men"},
                     {"world": world})
        assert "You asked for 12,000" in out["message"]

    def test_the_echo_lives_in_the_executor_not_the_shared_refusal(self, world):
        """⚠ `naval.over_lift_refusal` is pinned BYTE-FOR-BYTE by
        `test_wo_slice6_the_admiralty_speaks_plainly.py` and has a second
        caller — `expedition_blocked_reasons`, the region panel — which has
        no raw command text to read."""
        import inspect
        assert "You asked for" not in inspect.getsource(naval.over_lift_refusal)
        m = world.get_marshal("Soult")
        m.location, m.strength = "Brittany", 30000
        assert "You asked for" not in naval.over_lift_refusal(world, m)

    def test_no_figure_typed_means_no_echo(self):
        assert _detachment_echo({"raw_input": "land Soult in Munster"}) == ""
        assert _detachment_echo({}) == ""

    def test_the_echo_reads_either_raw_key(self):
        for key in ("raw_input", "original_command"):
            assert "8,000" in _detachment_echo(
                {key: "land Ney in Ulster with 8,000 troops"})


# ═══════════════════════════════════════════════════════════════════════════
# FA-64 — the typed confirm states the camp warning the chip states
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDiversionConfirmWarnsAboutTheEmptyCamp:

    @staticmethod
    def _confirm(world):
        return _quiet(NavalExecutor(None)._execute_naval_diversion,
                      {"action": "naval_diversion",
                       "raw_command": "order the grand diversion"},
                      {"world": world})["message"]

    def test_the_unstaged_camp_is_named(self, world):
        assert naval.camp_staged(world, "France") is False
        assert "No army is staged to use the open water" in self._confirm(world)

    def test_a_staged_camp_says_nothing(self, world):
        rec = naval.get_fleet(world, "France")
        provinces = rec.get("camp_provinces") or []
        assert provinces, "the 1805 France fleet authors camp provinces"
        world.get_marshal("Soult").location = provinces[0]
        rec["camp_turns"] = 99
        assert naval.camp_staged(world, "France") is True
        assert "No army is staged" not in self._confirm(world)

    def test_the_forecast_sentence_is_not_said_twice(self, world):
        """⚠ The filed fix — append the chip's whole note builder — is now a
        REGRESSION: since FA-31 (slice 14 part 2b) that note ENDS with the
        same forecast sentence the confirm already carries, so it would
        state the 45% figure twice and the forecast twice."""
        message = self._confirm(world)
        assert message.count("times in 100") == 1
        clause = naval.window_forecast_clause(world, "France")
        if clause:
            assert message.count(clause) == 1

    def test_the_confirm_keeps_its_subject(self, world):
        """A source census one file over reads the 900 characters BEFORE the
        message literal and asserts the `marshal` key sits inside them."""
        out = _quiet(NavalExecutor(None)._execute_naval_diversion,
                     {"action": "naval_diversion",
                      "raw_command": "order the grand diversion"},
                     {"world": world})
        assert out["marshal"] == "The Admiralty"

    @staticmethod
    def _diversion_chip(world):
        report = _quiet(naval.build_admiralty_report, world) or {}
        for chip in report.get("chips") or []:
            if chip.get("label") == "The Grand Diversion":
                return chip
        return {}

    def test_the_chip_still_carries_its_own_clause(self, world):
        note = self._diversion_chip(world).get("note", "")
        assert "no army is staged to use the open water" in note

    def test_the_chip_and_the_confirm_now_agree(self, world):
        """The whole point of the row: two surfaces for one order, and only
        one of them warned. They need not read alike — the chip is a
        fragment and the confirm is a sentence — but neither may be silent
        about a gate the other names."""
        note = self._diversion_chip(world).get("note", "").lower()
        message = self._confirm(world).lower()
        assert ("no army is staged" in note) == ("no army is staged" in message)


# ═══════════════════════════════════════════════════════════════════════════
# The rule, asserted once
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRuleIsSingleSourced:

    def test_no_text_site_sums_a_side_dict_any_more(self):
        """The census that would have caught FA-59 in the first place —
        scoped to CODE lines, and with the diorama's deliberate whole-side
        sum exempted by name."""
        offenders = []
        for name in ("backend/game_logic/naval.py",
                     "backend/commands/naval_executor.py"):
            src = (REPO / name).read_text(encoding="utf-8")
            code = "\n".join(ln for ln in src.split("\n")
                             if not ln.lstrip().startswith("#"))
            for match in re.finditer(r"sum\((?:action|result)\[.losses.\]"
                                     r"\.get\([^)]*\)\.values\(\)\)", code):
                offenders.append(f"{name}: {match.group(0)}")
        assert not offenders, offenders

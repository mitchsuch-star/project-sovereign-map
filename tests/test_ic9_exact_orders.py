"""Row IC, Session 2 — IC-9, EXACT ORDERS and THE TASK TO PROVE HIMSELF
(November 20, 2026).

The design is `docs/INDEPENDENT_COMMAND_SPEC.md` version 6, §7 (exact orders),
§6.11 (autonomy you grant) and §12 (the rulings on edge cases); the rules
`docs/SYSTEMS_REFERENCE.md` §231.

"Bold and careful men act on their own. A literal man gets it to the letter."
A standing order carries a short list of IF-THENS (`StrategicOrder.if_thens`;
`backend/commands/if_thens.py` is the grammar, the rules and the triggers):
three for a marshal who follows orders to the letter, one — on a hold — for
anyone else. Eight ifs, five thens, each line used once, read after the enemy
has moved, from the turn after it is written, on what his own nation can see.

It replaces CC-4 / D8's single `contingency`, whose own pins are
`tests/test_cc4_chained_orders.py` (re-seated on the list).
"""
from __future__ import annotations

import contextlib
import io
import json
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import if_thens as IT
from backend.commands import parse_preview as PP
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.commands.strategic import StrategicOrderProcessor
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def world1805():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    """A fresh copy of the 1805 board: Soult (literal) and the Emperor at
    Lorraine, Ney (bold) and Davout (careful) at Rhineland, Mack's 52,000 at
    Swabia — next to both, seen in part."""
    with _quiet():
        return WorldState.from_dict(world1805.to_dict())


def _names(world):
    friends = [m.name for m in world.get_player_marshals()]
    enemies = [m.name for m in world.marshals.values() if m.nation != world.player_nation]
    return friends, enemies, list(world.regions)


def _read(world, text):
    return IT.read(text, *_names(world))


def _line(world, text):
    """The one if-then of an "<addr>, if …" line."""
    got = _read(world, text)
    assert got is not None and len(got["lines"]) == 1 and not got["unread"], (text, got)
    return got["lines"][0]


def _give(world, name, kind="HOLD", target=None, lines=(), written=None):
    """A standing order with if-thens, as if given the turn before (so its
    lines are live and he was given no order by hand today)."""
    marshal = world.marshals[name]
    turn = int(world.current_turn)
    target = target or marshal.location
    order = StrategicOrder(
        command_type=kind, target=target, target_type="region",
        started_turn=turn - 1, issued_turn=turn - 1,
        original_command=f"{name}, {kind.lower()} {target}",
        if_thens=[{**dict(line), "used": False,
                   "written": (turn - 1 if written is None else written)} for line in lines])
    marshal.strategic_order = order
    if kind == "HOLD" and marshal.personality == "literal":
        marshal.holding_position = True
        marshal.hold_region = target
    return order


def _tick(world):
    with _quiet():
        return StrategicOrderProcessor(CommandExecutor()).process_strategic_orders(
            world, {"world": world})


def _rows(reports, name):
    return [r for r in reports if r.get("marshal") == name]


# ═══════════════════════════ the grammar ════════════════════════════════════

class TestTheGrammar:

    @pytest.mark.parametrize("text, want", [
        ("Soult, hold Lorraine. If attacked, dig in.",
         ("attacked", None, None, None, "dig_in", None, False)),
        ("Soult, hold Lorraine. If you are attacked, dig in.",
         ("attacked", None, None, None, "dig_in", None, False)),
        ("Soult, hold Lorraine. If Mack attacks you, fall back on Champagne.",
         ("attacked", "Mack", None, None, "fall_back", "Champagne", False)),
        ("Soult, hold Lorraine. If outnumbered, fall back on Champagne.",
         ("outnumbered", None, None, None, "fall_back", "Champagne", False)),
        ("Soult, hold Lorraine. If you are being surrounded, march to Champagne.",
         ("surrounded", None, None, None, "march", "Champagne", False)),
        ("Soult, hold Lorraine. If an enemy comes within reach, attack.",
         ("enemy_near", None, None, None, "attack", None, False)),
        ("Soult, hold Lorraine. If Mack comes within reach, attack whatever the odds.",
         ("enemy_near", "Mack", None, None, "attack", None, True)),
        ("Soult, hold. If Ney is attacked next to you, join his battle.",
         ("friend_attacked", None, "Ney", None, "join", None, False)),
        ("Davout, hold Franconia. If Munich falls, march to Munich.",
         ("place_falls", None, None, "Munich", "march", "Munich", False)),
        ("Soult, hold Lorraine. If Ney arrives, attack.",
         ("friend_arrives", None, "Ney", None, "attack", None, False)),
    ])
    def test_the_eight_ifs_and_the_five_thens_are_read(self, world, text, want):
        got = _read(world, text)
        assert got is not None and not got["unread"], (text, got)
        line = got["lines"][0]
        assert (line["if"], line["who"], line["friend"], line["place"], line["then"], line["to"],
                line["any_odds"]) == want, (text, line)

    def test_when_should_and_in_case_read_as_if(self, world):
        for text in ("Ney, when Mack advances, fall back to Lorraine",
                     "Ney, should Mack advance, fall back to Lorraine",
                     "Ney, in case Mack advances, fall back to Lorraine"):
            line = _line(world, text)
            assert (line["if"], line["who"], line["then"], line["to"]) == (
                "enemy_near", "Mack", "fall_back", "Lorraine"), text
        # "once" and "as soon as" are no if-words: the clause guard's, as before
        assert _read(world, "Ney, once Mack advances, fall back to Lorraine") is None
        assert _read(world, "Ney, as soon as Mack advances, fall back to Lorraine") is None

    def test_a_line_of_only_if_thens_is_a_hold_where_he_stands(self, world):
        got = _read(world, "Ney, if Mack advances fall back to Lorraine")
        assert got["order"] == "hold" and got["implicit_hold"] is True
        assert got["address"] == "Ney" and got["addressee"] == "Ney"

    def test_the_orders_own_words_are_kept_whole(self, world):
        got = _read(world, "Soult, hold Lorraine until Ney arrives. If attacked, dig in.")
        assert got["order"] == "hold Lorraine until Ney arrives" and len(got["lines"]) == 1
        got = _read(world, "Soult, march to Rhineland; if attacked, dig in")
        assert got["order"] == "march to Rhineland" and got["lines"][0]["then"] == "dig_in"

    def test_what_it_does_not_take_is_named_or_left_to_the_old_readers(self, world):
        # an if-segment beside a line it DID take: named, with why
        got = _read(world, "Soult, hold Lorraine. If attacked, dig in. If the moon is full, dance.")
        assert len(got["lines"]) == 1 and got["order"] == "hold Lorraine"
        assert got["unread"][0][0] == "If the moon is full, dance"
        # an answer of the five that does not fit its condition: named, with why
        got = _read(world, "Soult, hold Lorraine. If outnumbered, attack.")
        assert got["lines"] == [] and "not outnumbered" in got["unread"][0][1]
        got = _read(world, "Soult, hold Lorraine. If Ney is attacked, fall back on Narnia.")
        assert "no province on the map" in got["unread"][0][1]
        # ... and the shapes that are not exact orders at all stay the old readers'
        for text in ("Ney, attack Mack if he is not fortified",     # a condition ON an order
                     "Ney, retreat if outnumbered",                 # IC-V1's own line
                     "Ney, hold Lorraine, if you can",              # a trailing clause
                     "Ney, if Mack advances fall back to Narnia",   # one bad line, no order
                     "Ney, if Zorglub advances, fall back to Lorraine",
                     "In case Mack comes, fall back",               # nobody addressed
                     # no answer of the five anywhere: the relay's, as it always was
                     "Soult, hold Lorraine. If the moon is full, dance.",
                     "Massena, attack John; if he retreats, pursue him into Vienna",
                     "Ney, if the odds are bad, don't bother; otherwise, attack",
                     "Davout, when Ney arrives, hold Lorraine",     # CR-7-5's hand-off
                     "Ney, attack Mack. Then fortify. If attacked, dig in."):   # two orders
            assert _read(world, text) is None, text

    def test_every_phrase_it_writes_it_reads_back(self, world):
        """`describe` and `restate` write only what `read` takes: the line as
        understood always reads back to the same if-thens."""
        friends, enemies, places = _names(world)
        samples = []
        for if_, slot in (("enemy_near", {}), ("enemy_near", {"who": "Mack"}),
                          ("attacked", {}), ("attacked", {"who": "ArchdukeCharles"}),
                          ("outnumbered", {}), ("surrounded", {}),
                          ("friend_attacked", {"friend": "Ney"}),
                          ("place_falls", {"place": "East Prussia"}),
                          ("friend_arrives", {"friend": "Davout"})):
            for then, extra in (("attack", {}), ("attack", {"any_odds": True}),
                                ("fall_back", {"to": "Champagne"}), ("march", {"to": "Ile-de-France"}),
                                ("join", {}), ("dig_in", {})):
                if then not in IT.TW.THENS_FOR[if_]:
                    continue
                samples.append(IT.make_line(if_, then=then, **slot, **extra))
        assert len(samples) >= 30
        for line in samples:
            text = IT.restate("Soult", "hold Lorraine", [line])
            again = IT.read(text, friends, enemies, places)
            assert again is not None and not again["unread"], text
            assert IT.same_watch(again["lines"], [line]), (text, again["lines"])

    def test_names_are_shown_as_the_game_prints_them(self, world):
        line = _line(world, "Ney, if Archduke Charles attacks you, fall back to Lorraine")
        assert line["who"] == "ArchdukeCharles"
        assert IT.describe(line) == "if Archduke Charles attacks him, fall back to Lorraine"


# ═══════════════════════════ the rules ══════════════════════════════════════

class TestTheRules:

    @staticmethod
    def _three(world):
        got = _read(world, "Soult, hold Lorraine. If attacked, dig in. If outnumbered, "
                           "fall back on Champagne. If Ney arrives, attack.")
        assert len(got["lines"]) == 3
        return got["lines"]

    def test_three_for_a_literal_man_one_for_anyone_else(self, world):
        lines = self._three(world)
        kept, refused = IT.settle(world, world.marshals["Soult"], "HOLD", lines)
        assert len(kept) == 3 and not refused
        kept, refused = IT.settle(world, world.marshals["Ney"], "HOLD", lines)
        assert len(kept) == 1 and len(refused) == 2
        assert "carry one if-then" in refused[0][1]

    def test_a_fourth_line_is_refused(self, world):
        lines = self._three(world) + [IT.make_line("surrounded", then="dig_in")]
        kept, refused = IT.settle(world, world.marshals["Soult"], "HOLD", lines)
        assert len(kept) == 3 and "three if-thens at most" in refused[0][1]

    def test_a_literal_man_carries_them_on_any_standing_order_others_on_a_hold(self, world):
        line = [IT.make_line("attacked", then="dig_in")]
        soult, ney = world.marshals["Soult"], world.marshals["Ney"]
        for kind in ("HOLD", "MOVE_TO", "PURSUE", "SUPPORT"):
            assert IT.settle(world, soult, kind, line)[0], kind
        assert IT.settle(world, ney, "HOLD", line)[0]
        for kind in ("MOVE_TO", "PURSUE", "SUPPORT", None):
            kept, refused = IT.settle(world, ney, kind, line)
            assert not kept and "rides a hold" in refused[0][1], kind
        # an order that is no standing order carries none, for anyone
        assert not IT.settle(world, soult, None, line)[0]

    def test_at_most_one_attack_line(self, world):
        lines = [IT.make_line("enemy_near", then="attack"),
                 IT.make_line("friend_arrives", friend="Ney", then="attack", any_odds=True)]
        kept, refused = IT.settle(world, world.marshals["Soult"], "HOLD", lines)
        assert len(kept) == 1 and refused[0][1] == "at most one line of an order may attack"

    def test_a_line_that_repeats_or_contradicts_is_refused(self, world):
        soult = world.marshals["Soult"]
        a = IT.make_line("attacked", then="dig_in")
        kept, refused = IT.settle(world, soult, "HOLD", [a, dict(a)])
        assert len(kept) == 1 and refused[0][1] == "it repeats line 1"
        b = IT.make_line("attacked", then="fall_back", to="Champagne")
        kept, refused = IT.settle(world, soult, "HOLD", [a, b])
        assert len(kept) == 1 and refused[0][1] == "it contradicts line 1"

    def test_a_place_already_fallen_and_a_friend_gone_are_refused(self, world):
        soult = world.marshals["Soult"]
        world.regions["Rhineland"].controller = "Austria"
        kept, refused = IT.settle(world, soult, "HOLD",
                                  [IT.make_line("place_falls", place="Rhineland", then="dig_in")])
        assert not kept and refused[0][1] == "Rhineland has already fallen"
        kept, refused = IT.settle(world, soult, "HOLD",
                                  [IT.make_line("attacked", then="fall_back", to="Rhineland")])
        assert not kept and "in the enemy's hands" in refused[0][1]
        world.marshals["Ney"].strength = 0
        kept, refused = IT.settle(world, soult, "HOLD",
                                  [IT.make_line("friend_arrives", friend="Ney", then="dig_in")])
        assert not kept and refused[0][1] == "Ney is no longer in the field"

    def test_settle_changes_nothing_it_was_handed(self, world):
        lines = self._three(world)
        before = json.dumps(lines, sort_keys=True)
        IT.settle(world, world.marshals["Ney"], "HOLD", lines)
        assert json.dumps(lines, sort_keys=True) == before


# ═══════════════════════════ the triggers ═══════════════════════════════════

class TestTheTriggers:
    """Each IF, on the board his own nation SEES. Soult stands at Lorraine;
    Mack's 52,000 stand at Swabia, next to him, seen in part ("large force":
    France knows him at the middle of that band)."""

    def _happened(self, world, line, name="Soult"):
        return IT.happened(world, world.marshals[name], line)

    def test_an_enemy_within_reach(self, world):
        hit = self._happened(world, IT.make_line("enemy_near", then="dig_in"))
        assert hit and hit["enemy"].name == "Mack" and hit["where"] == "Swabia"
        assert hit["came"] == "Mack comes within reach at Swabia"

    def test_only_the_named_enemy_fires_a_named_line(self, world):
        assert self._happened(world, IT.make_line("enemy_near", who="Mack", then="dig_in"))
        assert self._happened(world, IT.make_line("enemy_near", who="Kutuzov", then="dig_in")) is None

    def test_never_on_a_province_he_cannot_see(self, world):
        from backend.models.intel import UNKNOWN
        world.get_region_intel("Swabia").visibility = UNKNOWN
        assert self._happened(world, IT.make_line("enemy_near", then="dig_in")) is None
        assert self._happened(world, IT.make_line("outnumbered", then="dig_in")) is None

    def test_a_force_under_a_fifth_trips_nothing_but_a_named_marshal_does(self, world):
        mack = world.marshals["Mack"]
        mack.strength = 3000            # "screening force": known at 2,499 — under 30,000 / 5
        world.calculate_visibility()
        assert IT.known_strength(world, mack) < world.marshals["Soult"].strength // IT.FLOOR_DIVISOR
        assert self._happened(world, IT.make_line("enemy_near", then="dig_in")) is None
        assert self._happened(world, IT.make_line("enemy_near", who="Mack", then="dig_in"))

    def test_horse_reaches_two_provinces(self, world):
        murat, soult = world.marshals["Murat"], world.marshals["Soult"]
        assert murat.cavalry and not soult.cavalry
        beside = set(world.get_region(soult.location).adjacent_regions)
        two_out = [r for r in IT.reach(world, murat)
                   if r != murat.location
                   and r not in world.get_region(murat.location).adjacent_regions]
        assert two_out, "a horseman's reach runs two provinces out"
        assert set(IT.reach(world, soult)) <= beside | {soult.location}

    def test_he_is_attacked(self, world):
        line = IT.make_line("attacked", then="dig_in")
        assert self._happened(world, line) is None
        world.record_battle("Lorraine", "Mack", "Soult", "defender_victory")
        hit = self._happened(world, line)
        assert hit and hit["enemy"].name == "Mack" and hit["came"] == "Mack attacked him at Lorraine"
        # a named attacker: only he fires it
        assert self._happened(world, IT.make_line("attacked", who="Kutuzov", then="dig_in")) is None
        assert self._happened(world, IT.make_line("attacked", who="Mack", then="dig_in"))

    def test_a_battle_he_began_is_not_being_attacked(self, world):
        world.record_battle("Swabia", "Soult", "Mack", "attacker_victory")
        assert self._happened(world, IT.make_line("attacked", then="dig_in")) is None

    def test_he_is_outnumbered_as_france_knows_it(self, world):
        line = IT.make_line("outnumbered", then="dig_in")
        assert self._happened(world, line), "30,000 against the 'large force' at Swabia"
        world.marshals["Mack"].strength = 9000        # known at about 10,000
        world.calculate_visibility()
        assert self._happened(world, line) is None

    def test_he_is_being_surrounded(self, world):
        line = IT.make_line("surrounded", then="dig_in")
        soult = world.marshals["Soult"]
        assert self._happened(world, line) is None, "Mack alone is one side"
        john = world.marshals["ArchdukeJohn"]
        john.location = "Rhineland"                   # a second side ...
        for name in ("Ney", "Davout", "Lannes", "Murat", "Napoleon"):
            world.marshals[name].location = "Paris"   # ... and no friend next to him
        world._build_marshal_index()
        world.calculate_visibility()
        hit = self._happened(world, line)
        assert hit and "Rhineland" in hit["came"] and "Swabia" in hit["came"], hit
        # a friend next to him: he is not surrounded
        world.marshals["Ney"].location = "Franche-Comte"
        world._build_marshal_index()
        assert soult.location == "Lorraine" and self._happened(world, line) is None

    def test_a_named_friend_is_attacked_next_to_him(self, world):
        line = IT.make_line("friend_attacked", friend="Ney", then="attack")
        assert self._happened(world, line) is None
        world.record_battle("Rhineland", "Mack", "Ney", "defender_victory")
        hit = self._happened(world, line)
        assert hit and hit["enemy"].name == "Mack" and hit["where"] == "Rhineland"
        # ... but not a battle far from him
        world.battles_this_turn.clear()
        world.record_battle("Paris", "Mack", "Ney", "defender_victory")
        assert self._happened(world, line) is None

    def test_a_named_place_falls(self, world):
        line = IT.make_line("place_falls", place="Rhineland", then="dig_in")
        assert self._happened(world, line) is None
        world.regions["Rhineland"].controller = "Austria"
        assert self._happened(world, line)["came"] == "Rhineland has fallen"

    def test_a_named_friend_arrives(self, world):
        line = IT.make_line("friend_arrives", friend="Massena", then="dig_in")
        assert self._happened(world, line) is None, "Massena stands at Milan"
        world.marshals["Massena"].location = "Rhineland"
        assert self._happened(world, line)["came"] == "Massena has arrived at Rhineland"

    def test_an_attack_line_strikes_only_when_he_is_not_outnumbered(self, world):
        soult = world.marshals["Soult"]
        event = self._happened(world, IT.make_line("enemy_near", then="attack"))
        assert IT.attack_target(world, soult, IT.make_line("enemy_near", then="attack"), event) is None
        bold = IT.make_line("enemy_near", then="attack", any_odds=True)
        assert IT.attack_target(world, soult, bold, event).name == "Mack"

    def test_the_readings_write_nothing_and_cast_no_die(self, world):
        order = _give(world, "Soult", lines=[IT.make_line("attacked", then="dig_in"),
                                              IT.make_line("outnumbered", then="fall_back", to="Champagne")])
        before = json.dumps(world.to_dict(), sort_keys=True, default=str)
        state = random.getstate()
        for _ in range(3):
            IT.ready(world, world.marshals["Soult"], order)
            IT.describe_all(order)
            IT.left_words(order)
        assert random.getstate() == state
        assert json.dumps(world.to_dict(), sort_keys=True, default=str) == before


# ═══════════════════════════ the firing ═════════════════════════════════════

class TestTheFiring:

    def test_dig_in_fires_free_and_the_order_stands_with_what_is_left(self, world):
        soult = world.marshals["Soult"]
        order = _give(world, "Soult", lines=[
            IT.make_line("attacked", then="dig_in"),
            IT.make_line("friend_arrives", friend="Massena", then="attack")])
        world.record_battle("Lorraine", "Mack", "Soult", "defender_victory")
        actions = int(world.actions_remaining)
        rows = _rows(_tick(world), "Soult")
        fired = [r for r in rows if r.get("action") == "contingency_fired"]
        assert fired and fired[0]["then"] == "dig_in", rows
        assert "Mack attacked him at Lorraine — Soult digs in at Lorraine, as you ordered." in fired[0]["message"]
        assert "(1 of 2 left)" in fired[0]["message"]
        assert soult.fortified and soult.strategic_order is order
        assert [line["used"] for line in order.if_thens] == [True, False]
        assert int(world.actions_remaining) == actions, "an if-then costs nothing when it fires"

    def test_a_line_is_used_once(self, world):
        order = _give(world, "Soult", lines=[IT.make_line("attacked", then="dig_in"),
                                              IT.make_line("friend_arrives", friend="Massena",
                                                           then="attack")])
        world.record_battle("Lorraine", "Mack", "Soult", "defender_victory")
        _tick(world)
        world.marshals["Soult"].fortified = False
        rows = _rows(_tick(world), "Soult")          # the condition is true again
        assert not [r for r in rows if r.get("action") == "contingency_fired"], rows
        assert world.marshals["Soult"].fortified is False and order.if_thens[0]["used"] is True

    def test_two_lines_true_only_the_first_fires(self, world):
        order = _give(world, "Soult", lines=[
            IT.make_line("outnumbered", then="dig_in"),
            IT.make_line("enemy_near", who="Mack", then="fall_back", to="Champagne")])
        rows = _rows(_tick(world), "Soult")
        assert [r["then"] for r in rows if r.get("action") == "contingency_fired"] == ["dig_in"]
        assert world.marshals["Soult"].location == "Lorraine"
        assert [line["used"] for line in order.if_thens] == [True, False]

    def test_a_fall_back_carries_the_rest_and_holds_on_arrival(self, world):
        soult = world.marshals["Soult"]
        _give(world, "Soult", lines=[
            IT.make_line("outnumbered", then="fall_back", to="Orleanais"),
            IT.make_line("attacked", then="dig_in")])
        rows = _rows(_tick(world), "Soult")
        fired = next(r for r in rows if r.get("action") == "contingency_fired")
        assert "falls back to Orleanais, as you ordered" in fired["message"]
        assert soult.location == "Orleanais", "the fresh march is walked this very tick"
        # arrived: the march has become the hold of that ground, with the line left
        order = soult.strategic_order
        assert order is not None and order.command_type == "HOLD" and order.target == "Orleanais"
        assert [(l["if"], l["then"], l["used"]) for l in order.if_thens] == [("attacked", "dig_in", False)]

    def test_the_last_line_ends_the_order_as_the_single_contingency_did(self, world):
        soult = world.marshals["Soult"]
        _give(world, "Soult", lines=[IT.make_line("outnumbered", then="fall_back", to="Orleanais")])
        _tick(world)
        assert soult.location == "Orleanais" and soult.strategic_order is None

    def test_a_march_line_marches(self, world):
        soult = world.marshals["Soult"]
        _give(world, "Soult", lines=[IT.make_line("outnumbered", then="march", to="Orleanais")])
        rows = _rows(_tick(world), "Soult")
        assert any("marches to Orleanais, as you ordered" in (r.get("message") or "") for r in rows)
        assert soult.location == "Orleanais"

    def test_an_attack_line_whatever_the_odds_fights(self, world):
        random.seed(1805)
        mack = world.marshals["Mack"]
        before = int(mack.strength)
        _give(world, "Soult", lines=[
            IT.make_line("enemy_near", then="attack", any_odds=True),
            IT.make_line("attacked", then="dig_in")])
        rows = _rows(_tick(world), "Soult")
        fired = next(r for r in rows if r.get("action") == "contingency_fired")
        assert fired["then"] == "attack" and fired["target"] == "Mack"
        assert int(mack.strength) < before

    def test_nothing_fires_on_the_turn_a_line_is_written(self, world):
        order = _give(world, "Soult", lines=[IT.make_line("outnumbered", then="dig_in")],
                      written=int(world.current_turn))
        rows = _rows(_tick(world), "Soult")
        assert not [r for r in rows if r.get("action") == "contingency_fired"]
        assert order.if_thens[0]["used"] is False and not world.marshals["Soult"].fortified
        assert IT.is_live(order.if_thens[0], int(world.current_turn)) is False
        assert IT.is_live(order.if_thens[0], int(world.current_turn) + 1) is True

    def test_one_thing_a_turn_his_lines_sleep_on_a_day_he_was_ordered_by_hand(self, world):
        soult = world.marshals["Soult"]
        order = _give(world, "Soult", lines=[IT.make_line("outnumbered", then="dig_in")])
        soult.last_ordered_turn = int(world.current_turn)
        rows = _rows(_tick(world), "Soult")
        assert not [r for r in rows if r.get("action") == "contingency_fired"]
        assert order.if_thens[0]["used"] is False
        soult.last_ordered_turn = int(world.current_turn) - 1
        rows = _rows(_tick(world), "Soult")
        assert [r for r in rows if r.get("action") == "contingency_fired"]

    def test_the_executor_marks_an_order_given_by_hand(self, world):
        soult = world.marshals["Soult"]
        parser = CommandParser(use_real_llm=False)
        with _quiet():
            CommandExecutor().execute(
                parser.parse("Soult, defend", {"world": world}, world=world), {"world": world})
        assert soult.last_ordered_turn == int(world.current_turn)
        # "stay put" is no order that reaches him; a strategic execution is the game's own
        ney = world.marshals["Ney"]
        with _quiet():
            CommandExecutor().execute(
                parser.parse("Ney, wait", {"world": world}, world=world), {"world": world})
            CommandExecutor().execute({"command": {"marshal": "Ney", "action": "defend",
                                                   "_strategic_execution": True}}, {"world": world})
        assert ney.last_ordered_turn is None

    def test_two_mens_lines_are_carried_out_by_rank(self, world):
        """§12: "Two literal men's lines fire together: carried out by rank" —
        Soult stands above Davout in the order of precedence; the pass's own
        order is alphabetical (Davout first)."""
        from backend.game_logic import precedence
        court = [m.name for m in precedence.order_of_precedence(world, world.player_nation)]
        assert court.index("Soult") < court.index("Davout")
        _give(world, "Soult", lines=[IT.make_line("outnumbered", then="dig_in")])
        _give(world, "Davout", lines=[IT.make_line("enemy_near", who="Mack", then="dig_in")])
        fired = [r["marshal"] for r in _tick(world) if r.get("action") == "contingency_fired"]
        assert fired == ["Soult", "Davout"]

    def test_the_lines_are_read_on_one_board(self, world):
        """One man's act cannot make another's line true: both readings are
        taken before either is carried out."""
        _give(world, "Soult", lines=[IT.make_line("outnumbered", then="fall_back", to="Orleanais")])
        # Davout's line would come true only AFTER Soult has left Lorraine
        _give(world, "Davout", lines=[IT.make_line("friend_arrives", friend="Soult", then="dig_in")])
        davout = world.marshals["Davout"]
        davout.location = "Ile-de-France"        # next to Orleanais, not to Lorraine
        world._build_marshal_index()
        assert "Ile-de-France" in world.get_region("Orleanais").adjacent_regions
        assert "Ile-de-France" not in world.get_region("Lorraine").adjacent_regions
        line = davout.strategic_order.if_thens[0]
        assert IT.happened(world, davout, line) is None, "Soult is two marches off"
        fired = [r["marshal"] for r in _tick(world) if r.get("action") == "contingency_fired"]
        assert fired == ["Soult"]
        assert world.marshals["Soult"].location == "Orleanais"
        assert line["used"] is False and not davout.fortified
        # ... it is true NOW (Soult stands next to him) and fires on the next pass
        assert IT.happened(world, davout, line)["came"] == "Soult has arrived at Orleanais"

    def test_a_line_that_can_no_longer_be_carried_out_is_struck(self, world):
        order = _give(world, "Soult", lines=[
            IT.make_line("friend_arrives", friend="Massena", then="attack"),
            IT.make_line("attacked", then="dig_in")])
        world.marshals["Massena"].strength = 0
        rows = _rows(_tick(world), "Soult")
        struck = next(r for r in rows if r.get("action") == "if_then_struck")
        assert "Soult's orders are broken" in struck["message"]
        assert "Massena is no longer in the field" in struck["message"]
        assert order.if_thens[0]["used"] is True and order.if_thens[0]["struck"]
        assert order.if_thens[1]["used"] is False and world.marshals["Soult"].strategic_order is order
        # said once: the next pass does not say it again
        again = _rows(_tick(world), "Soult")
        assert not [r for r in again if r.get("action") == "if_then_struck"]

    def test_a_literal_mans_march_may_carry_them_and_digging_in_holds_the_ground(self, world):
        soult = world.marshals["Soult"]
        order = _give(world, "Soult", kind="MOVE_TO", target="Champagne",
                      lines=[IT.make_line("attacked", then="dig_in"),
                             IT.make_line("friend_arrives", friend="Massena", then="attack")])
        order.path = ["Orleanais", "Champagne"]
        world.record_battle("Lorraine", "Mack", "Soult", "defender_victory")
        _tick(world)
        assert soult.location == "Lorraine" and soult.fortified
        held = soult.strategic_order
        assert held.command_type == "HOLD" and held.target == "Lorraine"
        assert [l["used"] for l in held.if_thens] == [True, False]


# ═══════════════════════════ join his battle ════════════════════════════════

class TestJoinHisBattle:
    """The friend must be the one ATTACKED; Soult (literal, on his post at
    Lorraine) stands next to Ney at Rhineland."""

    @staticmethod
    def _results(world, attacked=True):
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        random.seed(7)
        with _quiet():
            rows = CommandExecutor()._combat._calculate_reinforcements(
                ney, mack, "Rhineland", ney.nation, world, attacked=attacked)
        return {r["marshal"]: r for r in rows}

    def test_without_the_line_a_man_on_his_post_does_not_march(self, world):
        _give(world, "Soult", lines=[IT.make_line("attacked", then="dig_in")])
        assert "Soult" not in self._results(world), "Rule 8: a hold keeps him on his post"

    def test_with_the_line_he_rolls_by_his_written_order_and_the_line_is_used(self, world):
        order = _give(world, "Soult", lines=[
            IT.make_line("friend_attacked", friend="Ney", then="join"),
            IT.make_line("attacked", then="dig_in")])
        row = self._results(world)["Soult"]
        assert row["joined_by_line"] is True and row["has_explicit_order"] is True
        assert row["order_type"] == "IF_THEN" and row["reason"] != "literal_personality"
        assert order.if_thens[0]["used"] is True and order.if_thens[1]["used"] is False

    def test_it_answers_only_when_the_friend_is_the_one_attacked(self, world):
        order = _give(world, "Soult", lines=[IT.make_line("friend_attacked", friend="Ney", then="join")])
        assert "Soult" not in self._results(world, attacked=False)
        assert order.if_thens[0]["used"] is False

    def test_another_friends_battle_is_not_his_line(self, world):
        _give(world, "Soult", lines=[IT.make_line("friend_attacked", friend="Davout", then="join")])
        assert "Soult" not in self._results(world)

    def test_the_strategic_pass_never_fires_a_join_line(self, world):
        order = _give(world, "Soult", lines=[IT.make_line("friend_attacked", friend="Ney", then="join")])
        world.record_battle("Rhineland", "Mack", "Ney", "defender_victory")
        assert IT.ready(world, world.marshals["Soult"], order) is None


# ═══════════════════════════ saves ══════════════════════════════════════════

class TestTheSave:

    def test_the_list_survives_a_save(self, world):
        order = _give(world, "Soult", lines=[IT.make_line("attacked", then="dig_in"),
                                              IT.make_line("outnumbered", then="fall_back",
                                                           to="Champagne")])
        order.if_thens[0]["used"] = True
        again = StrategicOrder.from_dict(json.loads(json.dumps(order.to_dict())))
        assert again.to_dict() == order.to_dict()
        with _quiet():
            loaded = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        assert loaded.marshals["Soult"].strategic_order.if_thens == order.if_thens

    def test_an_old_saves_contingency_loads_as_its_one_line(self, world):
        order = _give(world, "Ney", lines=[])
        saved = order.to_dict()
        saved.pop("if_thens")
        saved["contingency"] = {"who": "Mack", "then": "fall_back", "to": "Lorraine",
                                "clause": "Ney, if Mack advances fall back to Lorraine"}
        loaded = StrategicOrder.from_dict(saved)
        assert len(loaded.if_thens) == 1
        line = loaded.if_thens[0]
        assert (line["if"], line["who"], line["then"], line["to"], line["used"]) == (
            "enemy_near", "Mack", "fall_back", "Lorraine", False)
        assert IT.is_live(line, int(world.current_turn)), "it was written before the save"
        assert "contingency" not in loaded.to_dict()

    def test_the_two_marshal_fields_survive_a_save(self, world):
        soult = world.marshals["Soult"]
        soult.last_ordered_turn, soult.stay_put_turn = 4, 5
        with _quiet():
            loaded = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        assert (loaded.marshals["Soult"].last_ordered_turn,
                loaded.marshals["Soult"].stay_put_turn) == (4, 5)
        assert loaded.marshals["Ney"].last_ordered_turn is None


# ═══════════════════════════ the surfaces ═══════════════════════════════════

class TestWhatThePlayerIsTold:

    def test_the_ledger_and_the_arrow_say_each_line_and_how_many_are_left(self, world):
        from backend.commands.strategic import standing_order_road
        from backend.game_logic.ledger import build_strategic_ledger
        order = _give(world, "Soult", lines=[IT.make_line("attacked", then="dig_in"),
                                              IT.make_line("outnumbered", then="fall_back",
                                                           to="Champagne")])
        forces = next(r for r in build_strategic_ledger(world)["forces"]
                      if r.get("name") == "Soult" or r.get("marshal") == "Soult")
        assert forces["strategic_order"].endswith(
            "if he is attacked, dig in; if he is outnumbered, fall back to Champagne (2 of 2 left)")
        road = standing_order_road(world, world.marshals["Soult"])
        assert road["watch"] == "if he is attacked, dig in; if he is outnumbered, fall back to Champagne"
        assert road["watch_left"] == "2 of 2 left" and road["watch_who"] == "the enemy"
        # the map's badge says the first line's OWN if, and how many more wait
        assert road["watch_short"] == "if he is attacked · +1 more"
        order.if_thens[0]["used"] = True
        road = standing_order_road(world, world.marshals["Soult"])
        assert road["watch"] == "if he is outnumbered, fall back to Champagne"
        assert road["watch_left"] == "1 of 2 left"
        assert road["watch_short"] == "if he is outnumbered"

    def test_the_maps_badge_says_each_if_in_its_own_words(self, world):
        """Found in the real client: the badge said "if the enemy comes" of
        every first line ("if Rhineland comes" of a place that falls)."""
        order = _give(world, "Soult")
        for line, said in (
                (IT.make_line("enemy_near", who="Mack", then="attack"), "if Mack comes"),
                (IT.make_line("enemy_near", then="attack"), "if the enemy comes"),
                (IT.make_line("attacked", then="dig_in"), "if he is attacked"),
                (IT.make_line("outnumbered", then="dig_in"), "if he is outnumbered"),
                (IT.make_line("surrounded", then="dig_in"), "if he is being surrounded"),
                (IT.make_line("friend_attacked", friend="Ney", then="join"), "if Ney is attacked"),
                (IT.make_line("place_falls", place="Rhineland", then="dig_in"), "if Rhineland falls"),
                (IT.make_line("friend_arrives", friend="Ney", then="attack"), "if Ney arrives")):
            order.if_thens = [dict(line)]
            assert IT.badge_words(order) == said, line
        order.if_thens = []
        assert IT.badge_words(order) == ""
        client = (REPO / "godot-client" / "project-sovereign" / "scenes"
                  / "map_renderer_base.gd").read_text(encoding="utf-8")
        assert '((" · " + watch_short) if watch_short != ""' in client

    def test_the_desk_offers_to_renew_used_lines_and_flags_broken_orders(self, world):
        from backend.game_logic import today
        order = _give(world, "Soult", lines=[IT.make_line("attacked", then="dig_in")])
        assert not [r for r in today.decide(world) if r["id"].startswith("orders_")]
        order.if_thens[0]["used"] = True
        row = next(r for r in today.decide(world) if r["id"] == "orders_used:Soult")
        assert row["text"] == "Soult has used his if-thens and stands — renew them (1 action)."
        assert row["door"] == {"kind": "marshal", "marshal": "Soult",
                               "line": "Soult, hold Lorraine. If he is attacked, dig in."}
        order.if_thens[0]["struck"] = "Ney is no longer in the field"
        row = next(r for r in today.decide(world) if r["id"] == "orders_broken:Soult")
        assert row["tier"] == today.TIER_BITES and "orders are broken" in row["text"]

    def test_the_renewing_sentence_is_one_the_line_reads(self, world):
        from backend.game_logic import today
        order = _give(world, "Soult", lines=[IT.make_line("attacked", then="dig_in"),
                                              IT.make_line("outnumbered", then="fall_back",
                                                           to="Champagne")])
        for line in order.if_thens:
            line["used"] = True
        row = next(r for r in today.decide(world) if r["id"] == "orders_used:Soult")
        again = _read(world, row["door"]["line"])
        assert again is not None and not again["unread"]
        assert IT.same_watch(again["lines"], order.if_thens)

    def test_a_live_exact_order_is_work_for_a_literal_man(self, world):
        """§7: a hold that still carries an if-then is no man left out; a
        plain hold (and one whose lines are used) still is."""
        from backend.game_logic import jealousy
        soult = world.marshals["Soult"]
        world.marshals["Ney"].moved_this_turn = True        # somebody else marches
        _give(world, "Soult", lines=[])
        with _quiet():
            jealousy.update_literal_hold_counters(world)
        assert soult.consecutive_hold_turns == 1
        order = _give(world, "Soult", lines=[IT.make_line("attacked", then="dig_in")])
        with _quiet():
            jealousy.update_literal_hold_counters(world)
        assert soult.consecutive_hold_turns == 0
        order.if_thens[0]["used"] = True
        with _quiet():
            jealousy.update_literal_hold_counters(world)
        assert soult.consecutive_hold_turns == 1


# ═══════════════════════════ the typed road ═════════════════════════════════

@pytest.fixture(scope="module")
def road():
    mp = pytest.MonkeyPatch()
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    prior = (M.world, M.game_state.get("world"), M.parser)
    with _quiet():
        M._reset_world_state()
    snap = json.dumps(M.world.to_dict(), default=str)
    try:
        with TestClient(M.app) as client:
            yield client, snap
    finally:
        M.world, M.parser = prior[0], prior[2]
        M.game_state["world"] = prior[1]
        PP.invalidate()
        mp.undo()


def _board(snap):
    with _quiet():
        board = WorldState.from_dict(json.loads(snap))
        M._set_active_world(board)
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    return board


def _post(client, line):
    random.seed(1805)
    with _quiet():
        return client.post("/command", json={"command": line}).json()


class TestTheTypedExactOrder:

    def test_a_literal_mans_three_lines_cost_one_action(self, road):
        client, snap = road
        board = _board(snap)
        actions = int(board.actions_remaining)
        reply = _post(client, "Soult, hold Lorraine. If attacked, dig in. If outnumbered, "
                              "fall back on Champagne. If Ney arrives, attack.")
        assert reply.get("success"), reply.get("message")
        order = board.marshals["Soult"].strategic_order
        assert order.command_type == "HOLD" and order.target == "Lorraine"
        assert [(l["if"], l["then"]) for l in order.if_thens] == [
            ("attacked", "dig_in"), ("outnumbered", "fall_back"), ("friend_arrives", "attack")]
        assert all(l["written"] == int(board.current_turn) and not l["used"] for l in order.if_thens)
        assert int(board.actions_remaining) == actions - 1
        assert ("Soult's exact orders — (1) if he is attacked, dig in; (2) if he is outnumbered, "
                "fall back to Champagne; (3) if Ney arrives, attack.") in reply["message"]
        assert "from next turn on, each line once" in reply["message"]

    def test_another_mans_one_line_rides_his_hold_at_its_usual_price(self, road):
        client, snap = road
        board = _board(snap)
        actions = int(board.actions_remaining)
        reply = _post(client, "Ney, hold Rhineland. If attacked, dig in.")
        assert reply.get("success"), reply.get("message")
        assert int(board.actions_remaining) == actions - 2
        assert len(board.marshals["Ney"].strategic_order.if_thens) == 1

    def test_a_second_line_for_another_man_is_refused_free_with_the_line_as_understood(self, road):
        client, snap = road
        board = _board(snap)
        actions = int(board.actions_remaining)
        reply = _post(client, "Ney, hold Rhineland. If attacked, dig in. If outnumbered, "
                              "fall back on Lorraine.")
        assert reply.get("success") is False and int(board.actions_remaining) == actions
        assert board.marshals["Ney"].strategic_order is None
        assert "Ney's orders carry one if-then" in reply["message"]
        assert reply["understood"] == "Ney, hold Rhineland. If he is attacked, dig in."
        assert reply["not_taken"][0]["clause"] == "If outnumbered, fall back on Lorraine"
        # ... and what was understood is an order the line takes whole
        again = _post(client, reply["understood"])
        assert again.get("success"), again.get("message")
        assert len(board.marshals["Ney"].strategic_order.if_thens) == 1

    def test_an_order_that_carries_no_if_thens_refuses_them_all(self, road):
        client, snap = road
        board = _board(snap)
        mack = int(board.marshals["Mack"].strength)
        reply = _post(client, "Ney, attack Mack. If outnumbered, fall back on Lorraine.")
        assert reply.get("success") is False, reply.get("message")
        assert int(board.marshals["Mack"].strength) == mack, "the attack did not go out without it"
        assert reply["understood"] == "Ney, attack Mack"

    def test_a_fall_back_to_where_he_holds_is_refused_free(self, road):
        client, snap = road
        board = _board(snap)
        actions = int(board.actions_remaining)
        reply = _post(client, "Soult, hold Lorraine. If attacked, fall back on Lorraine.")
        assert reply.get("success") is False and "already stands at Lorraine" in reply["message"]
        assert int(board.actions_remaining) == actions

    def test_a_typed_exact_order_is_never_an_interrupts_answer(self, road):
        client, snap = road
        board = _board(snap)
        assert M._line_is_a_contingency("Ney, if attacked, attack", board) is True
        assert M._line_is_a_contingency("Soult, hold Lorraine. If attacked, dig in.", board) is True
        assert M._line_is_a_contingency("Ney, attack anyway", board) is False

    def test_the_same_order_twice_is_the_no_op_and_a_changed_line_is_not(self, road):
        client, snap = road
        board = _board(snap)
        _post(client, "Soult, hold Lorraine. If attacked, dig in.")
        same = _post(client, "Soult, hold Lorraine. If attacked, dig in.")
        assert "already carrying out" in (same.get("message") or "")
        other = _post(client, "Soult, hold Lorraine. If attacked, fall back on Champagne.")
        assert "already carrying out" not in (other.get("message") or ""), other.get("message")
        assert board.marshals["Soult"].strategic_order.if_thens[0]["then"] == "fall_back"


# ═══════════════════════════ the review's rows ══════════════════════════════

class TestTheReviewsRows:
    """The one review before the commit (three readers on a frozen copy):
    its rows on exact orders, each a behaviour pinned here."""

    def test_joining_is_his_one_thing_that_turn(self, world):
        """S1: he joined his friend's battle by his line — and "if
        outnumbered" then marched him off at the same end of turn."""
        order = _give(world, "Soult", lines=[
            IT.make_line("friend_attacked", friend="Ney", then="join"),
            IT.make_line("outnumbered", then="dig_in")])
        soult = world.marshals["Soult"]
        random.seed(7)
        with _quiet():
            CommandExecutor().execute(
                {"command": {"marshal": "Mack", "action": "attack", "target": "Ney"}},
                {"world": world})
        assert soult.location == "Rhineland", "he marched to the guns by his written line"
        assert [line["used"] for line in order.if_thens] == [True, False]
        assert soult.last_ordered_turn == int(world.current_turn)
        rows = _rows(_tick(world), "Soult")
        assert not [r for r in rows if r.get("action") == "contingency_fired"]
        assert order.if_thens[1]["used"] is False

    def test_only_an_order_carried_out_is_an_order_given_by_hand(self, world):
        """S2: a pension, a recruit, a garrison that merely NAMES him is no
        order to him; nor is one he has only been asked about."""
        from backend.ai.validation import ADMINISTRATIVE_ACTIONS, NON_ORDER_ACTIONS
        soult = world.marshals["Soult"]
        done = {"success": True}
        for action in sorted(ADMINISTRATIVE_ACTIONS | NON_ORDER_ACTIONS | {"wait"}):
            IT.ordered_by_hand(world, "Soult", action, {"action": action}, done)
            assert soult.last_ordered_turn is None, action
        for asked in ({"success": True, "state": "awaiting_player_choice"},
                      {"success": True, "state": "awaiting_clarification"},
                      {"success": True, "requires_input": True},
                      {"success": True, "pending_glorious_charge": True},
                      {"success": False}):
            IT.ordered_by_hand(world, "Soult", "attack", {"action": "attack"}, asked)
            assert soult.last_ordered_turn is None, asked
        for flag in ("_strategic_execution", "_jealousy_autonomous", "_autonomous_execution"):
            IT.ordered_by_hand(world, "Soult", "attack", {"action": "attack", flag: True}, done)
            assert soult.last_ordered_turn is None, flag
        # an enemy's marshal is never marked
        IT.ordered_by_hand(world, "Mack", "attack", {"action": "attack"}, done)
        assert world.marshals["Mack"].last_ordered_turn is None
        IT.ordered_by_hand(world, "Soult", "attack", {"action": "attack"}, done)
        assert soult.last_ordered_turn == int(world.current_turn)

    def test_a_named_commander_must_be_one_we_are_at_war_with(self, world):
        """S5: a line naming an ally's or a neutral's commander would never
        fire, and would sit using up a line."""
        soult = world.marshals["Soult"]
        deroy = world.marshals["Deroy"]
        assert not world.is_at_war(soult.nation, deroy.nation)
        got = _read(world, "Soult, hold Lorraine. If Deroy comes within reach, "
                           "fall back to Champagne.")
        kept, refused = IT.settle(world, soult, "HOLD", got["lines"])
        assert kept == [] and [why for _line, why in refused] == [
            "we are not at war with Deroy's court"]
        got = _read(world, "Soult, hold Lorraine. If Mack comes within reach, "
                           "fall back to Champagne.")
        kept, refused = IT.settle(world, soult, "HOLD", got["lines"])
        assert len(kept) == 1 and refused == []

    @pytest.mark.parametrize("verb", [None, "drill", "fortify"])
    def test_a_march_keeps_its_lines_whatever_it_ends_in(self, world, verb):
        """S4: a march's if-thens went with it, in silence, unless it ended
        in "then hold" — he holds where he arrives, with the lines unused."""
        soult = world.marshals["Soult"]
        order = _give(world, "Soult", kind="MOVE_TO", target="Orleanais",
                      lines=[IT.make_line("attacked", then="dig_in")])
        order.path = ["Orleanais"]
        if verb:
            order.arrival_verb = verb
        row = _rows(_tick(world), "Soult")[-1]
        held = soult.strategic_order
        assert soult.location == "Orleanais"
        assert held is not None and held.command_type == "HOLD" and held.target == "Orleanais"
        assert [(line["if"], line["then"], line["used"]) for line in held.if_thens] == [
            ("attacked", "dig_in", False)]
        assert "He holds Orleanais with the rest of his exact orders (1 of 1 left)." in (
            row.get("message") or "")

    def test_a_march_with_no_lines_ends_as_it_always_did(self, world):
        soult = world.marshals["Soult"]
        order = _give(world, "Soult", kind="MOVE_TO", target="Orleanais")
        order.path = ["Orleanais"]
        row = _rows(_tick(world), "Soult")[-1]
        assert soult.location == "Orleanais" and soult.strategic_order is None
        assert "exact orders" not in (row.get("message") or "")

    def test_a_province_is_said_by_the_name_the_game_prints(self):
        """L6: every name in a line's phrase goes through the one shower."""
        line = IT.make_line("place_falls", place="Upper_Austria", then="march", to="Lower_Austria")
        assert IT.describe(line) == "if Upper Austria falls, march to Lower Austria"
        back = IT.make_line("outnumbered", then="fall_back", to="Lower_Austria")
        assert IT.describe(back, shown=str.upper) == "if he is outnumbered, fall back to LOWER_AUSTRIA"


class TestTheReviewsRowsOnTheRoad:

    def test_an_order_carried_out_after_his_objection_is_given_by_hand_too(self, road):
        """S3: the executor's close marked an order; the order carried out
        AFTER an objection never passed it."""
        client, snap = road
        board = _board(snap)
        first = _post(client, "Ney, fortify")
        assert first.get("pending_objection"), first.get("message")
        ney = board.marshals["Ney"]
        assert ney.last_ordered_turn is None, "asked about, not yet ordered"
        with _quiet():
            answer = client.post("/respond_to_objection", json={"choice": "insist"}).json()
        assert answer.get("success"), answer.get("message")
        assert ney.last_ordered_turn == int(board.current_turn)

    def test_a_march_that_arrives_at_once_keeps_its_lines(self, road):
        """S4 on the first step: "march to Orleanais then drill. If attacked,
        dig in." — he drills, and holds Orleanais with the line."""
        client, snap = road
        board = _board(snap)
        reply = _post(client, "Soult, march to Orleanais then drill. If attacked, dig in.")
        assert reply.get("success"), reply.get("message")
        soult = board.marshals["Soult"]
        held = soult.strategic_order
        assert soult.location == "Orleanais" and soult.drilling
        assert held is not None and held.command_type == "HOLD" and held.target == "Orleanais"
        assert [(line["if"], line["then"], line["used"]) for line in held.if_thens] == [
            ("attacked", "dig_in", False)]

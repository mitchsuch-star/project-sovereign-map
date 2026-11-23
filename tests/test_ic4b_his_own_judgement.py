"""Row IC, Session 4b (IC4-D3) — HIS OWN JUDGEMENT, AND HE MOVES AT TURN START.

The user's ruling (November 22, 2026), verbatim: "orders shlould beguiding ai
that has its own actions and does its own thing you get it"; his correction
opening Session 4b (November 23): "thats not true either its just these are
autonomous armies napoleons orders guiode them, they still work under ai with
goals set that impact their decision tree!!"; and, in Session 4b's Plan Mode,
his choice "He moves at turn start" ("each turn opens with his move, before you
give any orders, like a general already in the field").

`backend/game_logic/own_judgement.py`: each turn he weighs every act open to
him — your aim's step, the chances beside him, finding the enemy, his ways of
waiting — and does the one that weighs most. These tests pin how the GOAL
weighs (a pull, never a fence), how his NATURE weighs, the guards (no marching
out and back, the fog, no capital unnamed), the reasons said for a stay, and
"no task" (`free`).
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import own_judgement as J
from backend.game_logic import own_order as O
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def world1805():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


def _fresh(world1805) -> WorldState:
    with _quiet():
        return WorldState.from_dict(world1805.to_dict())


def _give(world, name, task, target="", **kw):
    marshal = world.marshals[name]
    spec, why = O.spec_from(world, marshal, task, target, **kw)
    assert spec is not None, why
    with _quiet():
        result = O.give(world, marshal, spec, line=f"{name}, {task} {target} on your own.",
                        own_proposal=True)
    assert result["success"], result
    O.own(marshal)["given"] = int(world.current_turn) - 1        # his first turn is past
    O.own(marshal)["late"] = False
    return marshal


def _raid(world1805, strength=4000):
    """The board of the first strict pin: Mack gone east, an Austrian raid in
    French Lorraine beside Ney at Rhineland."""
    world = _fresh(world1805)
    world.marshals["Mack"].location = "Vienna"
    john = world.marshals["ArchdukeJohn"]
    john.location, john.strength = "Lorraine", strength
    world.refresh_marshal_indexes()
    return world


def _odds(monkeypatch, ratio: float, who: str = "ArchdukeJohn"):
    """The battle forecast France reads of `who`, fixed (every other forecast
    is the game's own)."""
    real = O.odds_against

    def fake(world, marshal, enemy):
        if getattr(enemy, "name", "") == who:
            return {"ratio": ratio, "tenths": O._tenths(ratio), "exact": True, "joining": [],
                    "theirs": "", "weight": 0, "theirs_low": 1, "theirs_high": 1}
        return real(world, marshal, enemy)
    monkeypatch.setattr(O, "odds_against", fake)


# ═══════════════════════ the goal is a PULL, never a fence ═══════════════════

class TestTheGoalPulls:

    def test_a_crushing_chance_beside_his_road_wins_the_turn(self, world1805):
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        reading = O.read(world, ney)
        assert reading["kind"] == "chance" and reading["act"] == "strike"
        assert reading["target"] == "ArchdukeJohn" and "beside his road to Bohemia" in reading["line"]
        goal = [w for w in reading["weighed"] if w["kind"] == "goal"]
        assert goal and goal[0]["weight"] == J.WEIGHTS["goal_march"], reading["weighed"]

    def test_a_chance_at_his_bare_figure_does_not_pull_him_off_his_road(self, world1805, monkeypatch):
        """A bare chance — at his own figure, on nobody's soil, threatening no
        friend — weighs less than the step on your road (55 − 12 < 60)."""
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        need = O.needed(ney, 0, O._record_view(ney), reaching=True)
        _odds(monkeypatch, float(need["needed"]) / 10.0)          # margin 0
        monkeypatch.setattr(J, "_soil", lambda *a, **k: "")
        monkeypatch.setattr(J, "_threatened", lambda *a, **k: "")
        reading = O.read(world, ney)
        assert reading["kind"] == "goal" and reading["act"] == "march", reading["weighed"]

    def test_the_same_chance_on_our_soil_beside_a_friend_wins(self, world1805, monkeypatch):
        """... and the same enemy standing on French soil, beside a friend,
        is worth the detour to a bold man (55 + 15 + 10 − 12 > 60)."""
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        need = O.needed(ney, 0, O._record_view(ney), reaching=True)
        _odds(monkeypatch, float(need["needed"]) / 10.0)
        monkeypatch.setattr(J, "_threatened", lambda *a, **k: "Davout")
        reading = O.read(world, ney)
        assert reading["kind"] == "chance" and "a threat to Davout" in reading["line"], reading["weighed"]

    def test_your_aim_in_reach_beats_any_chance(self, world1805):
        world = _raid(world1805)
        world.marshals["Mack"].location = "Swabia"
        world.refresh_marshal_indexes()
        ney = _give(world, "Ney", "take", "Swabia")
        reading = O.read(world, ney)
        assert reading["kind"] == "goal" and reading["target"] in ("Mack", "Swabia"), reading["weighed"]

    def test_after_the_strike_he_turns_back_to_your_aim(self, world1805):
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        world.marshals["ArchdukeJohn"].strength = 0                 # the raid beaten off
        world.refresh_marshal_indexes()
        rec = O.record(ney)
        rec["acts"] = [["strike", "Lorraine", int(world.current_turn) - 1, "Rhineland", "ArchdukeJohn"]]
        ney.own_record = rec
        reading = O.read(world, ney)
        assert reading["kind"] == "goal" and "on the road to Bohemia" in reading["line"], reading

    def test_the_weights_live_in_one_table(self, world1805, monkeypatch):
        """Take the bold man's taste for a chance out of the table and the raid
        no longer wins the turn — the table, and nothing else, weighs."""
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        monkeypatch.setitem(J.WEIGHTS, "chance", {"bold": 0, "careful": 0})
        reading = O.read(world, ney)
        assert reading["kind"] == "goal", reading["weighed"]


# ═══════════════════════ his nature weighs ═══════════════════════════════════

class TestHisNatureWeighs:

    def test_a_careful_man_leaves_your_road_only_at_good_odds(self, world1805, monkeypatch):
        world = _raid(world1805)
        davout = world.marshals["Davout"]
        davout.location = "Rhineland"
        world.refresh_marshal_indexes()
        _give(world, "Davout", "take", "Bohemia")
        need = O.needed(davout, 0, O._record_view(davout))
        _odds(monkeypatch, (float(need["needed"]) + 2.0) / 10.0)   # two tenths above his figure
        assert O.read(world, davout)["kind"] == "goal"
        _odds(monkeypatch, (float(need["needed"]) + 15.0) / 10.0)  # far above it
        assert O.read(world, davout)["kind"] == "chance"

    def test_a_bold_man_takes_the_same_modest_chance(self, world1805, monkeypatch):
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        need = O.needed(ney, 0, O._record_view(ney), reaching=True)
        _odds(monkeypatch, (float(need["needed"]) + 2.0) / 10.0)
        assert O.read(world, ney)["kind"] == "chance"


# ═══════════════════════ under a hold he keeps the ground you named ══════════

class TestUnderAHold:

    def test_he_strikes_beside_the_ground_he_holds(self, world1805):
        world = _raid(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        reading = O.read(world, ney)
        assert reading["kind"] == "chance" and "next to the ground he holds" in reading["line"]

    def test_he_never_goes_hunting_off_his_ground(self, world1805, monkeypatch):
        from backend.commands import if_thens
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        monkeypatch.setattr(if_thens, "seen_enemies", lambda *a, **k: [])
        monkeypatch.setattr(O, "_foes_at", lambda *a, **k: [])
        reading = O.read(world, ney)
        assert reading["kind"] == "wait", reading
        assert not any(w["kind"] == "seek" for w in reading["weighed"])

    def test_every_stay_names_the_reason_his_judgement_chose_it(self, world1805, monkeypatch):
        from backend.commands import if_thens
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        ney.fortified = True
        monkeypatch.setattr(if_thens, "seen_enemies", lambda *a, **k: [])
        monkeypatch.setattr(O, "_foes_at", lambda *a, **k: [])
        monkeypatch.setattr(O, "_waiting_options", lambda *a, **k: [])
        reading = O.read(world, ney)
        assert reading["act"] == "stay" and reading["why"]
        assert "nothing to do" not in reading["line"]
        assert "as you asked" in reading["line"] and "worth leaving it for" in reading["line"]


# ═══════════════════════ the guards ══════════════════════════════════════════

class TestTheGuards:

    def test_a_move_that_only_retraces_his_last_step_weighs_less(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        ctx = {"came_from": "Lorraine"}
        go_back = J._opt("seek", {"act": "march", "place": "Lorraine", "target": "Mack",
                                  "do": [{"action": "move", "target": "Lorraine"}]}, 50, "seek")
        stay = J._opt("wait", {"act": "stay", "place": ney.location, "target": ""}, 40, "stay")
        chosen, _ranked, _changed = J._settle([go_back, stay], {"acts": []}, ctx)
        assert chosen["act"] == "stay", "50 − the turn-back's 20 is below 40"

    def test_no_act_at_the_same_place_a_third_turn_running(self, world1805):
        look = J._opt("wait", {"act": "look", "place": "Swabia", "target": "Swabia"}, 40, "look")
        dig = J._opt("wait", {"act": "dig_in", "place": "Rhineland", "target": "Rhineland"}, 30, "dig")
        rec = {"acts": [["look", "Swabia", 1], ["look", "Swabia", 2]]}
        chosen, _ranked, changed = J._settle([look, dig], rec, {"came_from": ""})
        assert chosen["act"] == "dig_in" and changed

    def test_he_never_strikes_what_france_cannot_see(self, world1805, monkeypatch):
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        real = O._visible
        monkeypatch.setattr(O, "_visible", lambda w, place: False if place == "Lorraine" else real(w, place))
        reading = O.read(world, ney)
        assert reading["target"] != "ArchdukeJohn" and reading["kind"] == "goal", reading["weighed"]

    def test_no_enemy_capital_unless_you_named_it(self, world1805, monkeypatch):
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        monkeypatch.setattr(J, "_capitals", lambda w: {"Lorraine"})
        reading = O.read(world, ney)
        assert reading["target"] != "ArchdukeJohn", reading["weighed"]

    def test_the_reading_is_pure(self, world1805):
        import json
        import random
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        before = json.dumps(world.to_dict(), sort_keys=True, default=str)
        random.seed(9)
        expected = random.random()
        random.seed(9)
        O.read(world, ney)
        O.read(world, ney, preview=True)
        assert random.random() == expected
        assert json.dumps(world.to_dict(), sort_keys=True, default=str) == before


# ═══════════════════════ no task: he makes war as he sees fit ════════════════

class TestNoTask:

    def test_a_free_man_strikes_what_he_can_beat_beside_him(self, world1805):
        world = _raid(world1805)
        ney = _give(world, "Ney", "free")
        reading = O.read(world, ney)
        assert reading["kind"] == "chance" and reading["target"] == "ArchdukeJohn"
        assert "beside his road" not in reading["line"], "no task: no road"

    def test_with_nothing_in_reach_he_heads_for_your_war_goal(self, world1805):
        """The Austrians drawn off east: nothing within his reach, so a man with
        no task heads for the war goal you named."""
        world = _fresh(world1805)
        for name in ("Mack", "ArchdukeJohn"):
            world.marshals[name].location = "Vienna"
        world.refresh_marshal_indexes()
        ney = _give(world, "Ney", "free")
        world.war_goals = {"Austria": {"kind": "place", "target": "Bohemia", "turn": 1}}
        reading = O.read(world, ney)
        assert reading["kind"] == "seek" and reading["target"] == "Bohemia", reading["weighed"]
        assert "toward your war goal" in reading["line"]

    def test_free_costs_two_actions_and_rides_a_hold(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        spec, why = O.spec_from(world, ney, "free", "")
        assert spec is not None and O.price_of(ney, spec) == 2
        assert O.ORDER_TYPE["free"] == "HOLD" and "free" not in O.TASK_OF_ORDER.values()
        assert O.TASK_OF_ORDER["HOLD"] == "hold"

    def test_at_peace_there_is_no_war_to_make(self, world1805, monkeypatch):
        world = _fresh(world1805)
        monkeypatch.setattr(O, "_at_war", lambda w: False)
        why = O.why_not(world, world.marshals["Ney"], "free")
        assert why == "there is no war to make — give him a hold or a support"

    def test_a_literal_man_and_the_guns_are_never_offered_it(self, world1805):
        from backend.commands import state_probe as SP
        world = _fresh(world1805)
        assert SP.button_offered(world.marshals["Soult"])["own_free"] is False
        assert SP.button_offered(world.marshals["Ney"])["own_free"] is True
        assert SP.button_offered(world.marshals["Davout"])["own_free"] is True

    def test_the_typed_line_and_its_words(self):
        from backend.ai.own_words import free_task, set_aside_marks
        for line in ("Ney, act on your own", "Ney, as you see fit", "Ney, make war as you see fit",
                     "Ney, on your own", "Ney, use your judgement"):
            rest, marks = set_aside_marks(line)
            assert marks, line
            assert free_task(rest, ["Ney"]) == ("Ney", 0), line
        rest, _marks = set_aside_marks("Ney, act boldly on your own")
        assert free_task(rest, ["Ney"]) == ("Ney", 1)
        rest, _marks = set_aside_marks("Ney, take Swabia on your own")
        assert free_task(rest, ["Ney"]) is None, "a task is not 'no task'"


# ═══════════════════════ beaten, he rallies and carries on ═══════════════════

class TestBeaten:

    def test_he_keeps_his_task_and_rallies_first(self, world1805):
        from backend.commands.executor import CommandExecutor
        world = _fresh(world1805)
        ney = _give(world, "Ney", "take", "Swabia")
        with _quiet():
            CommandExecutor()._combat._apply_forced_retreat_or_break(
                ney, world.marshals["Mack"], world, skip_fate=True)
        assert O.on_his_own(ney) and O.own(ney)["task"] == "take"
        ney.retreat_recovery = 1                       # as the turn's advance leaves it
        reading = O.read(world, ney)
        assert reading["act"] == "recover" and "rallying" in reading["line"]

    def test_a_square_he_breaks_leaves_his_task(self, world1805):
        """The sibling sweep (golden rule 10): breaking square to act was one of
        the five other places that wiped every order."""
        from backend.commands.executor import CommandExecutor
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        ney.square_formation = True
        with _quiet():
            CommandExecutor()._tactical._auto_break_square(ney, "attack")
        assert not ney.square_formation and O.on_his_own(ney)

    def test_a_breakout_leaves_his_task(self, world1805):
        from backend.commands.executor import CommandExecutor
        world = _fresh(world1805)
        ney = _give(world, "Ney", "take", "Swabia")
        with _quiet():
            CommandExecutor()._combat.apply_successful_breakout(ney, world.marshals["Mack"], world)
        assert O.on_his_own(ney)


# ═══════════════════════ he moves at turn start ══════════════════════════════

class TestHeMovesAtTurnStart:

    def test_the_morning_tells_what_he_did_in_the_past(self, world1805):
        ney = _fresh(world1805).marshals["Ney"]
        line = ("Ney strikes Archduke John at Lorraine — the odds are our 60 to their 10, and he goes in "
                "when they are our 5 to their 10 or better; beside his road to Bohemia, on our soil")
        told = O.told(line, ney)
        assert told == ("Ney struck Archduke John at Lorraine — the odds were our 60 to their 10; beside "
                        "his road to Bohemia, on our soil")
        assert O.told("Ney marches from Rhineland to Swabia, on the road to Bohemia — 2 more marches "
                      "to go", ney).startswith("Ney marched from Rhineland to Swabia")

    def test_the_card_says_what_he_did_this_turn_never_what_he_will_do(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        info = O.payload(world, ney)
        assert "tonight" not in info and "ahead" not in info
        assert info["this_turn"] == ""
        rec = O.record(ney)
        rec["acts"] = [["dig_in", "Rhineland", int(world.current_turn), "Rhineland", "Rhineland"]]
        rec["said"] = "Ney dug in at Rhineland"
        ney.own_record = rec
        assert O.payload(world, ney)["this_turn"] == "Ney dug in at Rhineland"

    def test_asked_what_he_will_do_he_says_an_intention(self, world1805):
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        said = O.answer(world, ney, "night")["says"]
        assert said.startswith("At the start of next turn I mean to ") and said.endswith(
            ", if nothing changes first."), said


class TestThePlayOutsFindings:
    """Session 4b's play-out (three campaigns of ten turns, before the measure)."""

    def test_a_weak_corps_does_not_rest_a_third_turn_running(self):
        """"Never the same thing a third turn running" covers every act — a
        half-strength corps rested five turns running, though rest restores no
        men in this game."""
        rest = J._opt("wait", {"act": "stay", "place": "Munich", "target": ""}, 35, "stay")
        look = J._opt("wait", {"act": "look", "place": "Tyrol", "target": "Tyrol"}, 25, "look")
        rec = {"acts": [["stay", "Munich", 5], ["stay", "Munich", 6]]}
        chosen, _ranked, changed = J._settle([rest, look], rec, {"came_from": "", "on_post": False})
        assert chosen["act"] == "look" and changed

    def test_keeping_the_ground_you_named_is_your_order_not_his_habit(self):
        keep = J._opt("wait", {"act": "stay", "place": "Rhineland", "target": ""}, 20, "stay")
        look = J._opt("wait", {"act": "look", "place": "Swabia", "target": "Swabia"}, 15, "look")
        rec = {"acts": [["stay", "Rhineland", 5], ["stay", "Rhineland", 6]]}
        chosen, _ranked, _changed = J._settle([keep, look], rec, {"came_from": "", "on_post": True})
        assert chosen["act"] == "stay"

    def test_bernadottes_late_start_says_what_it_was(self):
        src = (Path(__file__).resolve().parents[1] / "backend" / "game_logic"
               / "own_order.py").read_text(encoding="utf-8")
        assert "made ready for his task" not in src
        assert "started a turn late, as is his way" in src


class TestTheMeasuresFindings:
    """Session 4b's measure (round 0, before any weight changed): two defects,
    fixed before the weights were touched."""

    def test_engaged_he_attacks_only_the_enemy_beside_him(self, world1805):
        """"Cannot attack elsewhere while engaged with enemy forces": an enemy
        standing in his own province closes every other attack."""
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        mack = world.marshals["Mack"]
        mack.location = ney.location
        world.refresh_marshal_indexes()
        assert O._engaged_by(world, ney) == [mack]
        need = O.needed(ney, 0, O._record_view(ney), reaching=True)
        hit, why = O._attack_choice(world, ney, "Lorraine", need, {})
        assert hit is None and "must be dealt with first" in why
        reading = O.read(world, ney)
        dest = J._moves_to(reading)
        assert reading.get("place") in ("", ney.location) or (
            dest and world.get_region(dest).controller == ney.nation), reading["weighed"]

    def test_a_charge_is_barred_by_any_corps_between(self, world1805):
        """"Cannot charge through X — Y blocks the path": the executor checks
        every province between — the reach read "any one clear"."""
        world = _fresh(world1805)
        murat = world.marshals["Murat"]
        here = str(murat.location)
        two = [p for p in world.regions if (world.get_distance(here, p) or 0) == 2]
        far = next(p for p in two if len([q for q in O._near(world, here)
                                          if p in O._near(world, q)]) >= 2)
        between = [q for q in O._near(world, here) if far in O._near(world, q)]
        real = O._foes_at
        blocker = world.marshals["ArchdukeJohn"]
        O_foes = {between[0]: [blocker]}

        def fake(w, m, place):
            return O_foes.get(place, []) if place in between else real(w, m, place)
        import pytest as _pt
        mp = _pt.MonkeyPatch()
        try:
            mp.setattr(O, "_foes_at", fake)
            mp.setattr(O, "strike_crossing_verdict", lambda *a: None, raising=False)
            murat.movement_range = 2
            assert not O._in_strike_reach(world, murat, far), (far, between)
        finally:
            mp.undo()

    def test_a_man_drawn_into_a_later_battle_says_so(self, world1805):
        """"Lannes marched from Swabia to Franconia" while he stood at Munich in
        Ney's battle: his line now says the roll drew him on."""
        world = _fresh(world1805)
        lannes, ney = world.marshals["Lannes"], world.marshals["Ney"]
        rows = [{"marshal": "Lannes", "message": "Lannes marched from Swabia to Franconia.",
                 "reason": "", "act": "march", "place": "Franconia"}]
        lannes.reinforced_this_turn = True
        rec = O.record(lannes)
        rec["said"] = "Lannes marched from Swabia to Franconia"
        lannes.own_record = rec
        O._drawn_in_after_his_move(world, rows, {"Lannes"}, ney, {"place": "Munich"})
        assert rows[0]["message"].endswith("then the usual roll drew him into Ney's battle at Munich.")
        assert rows[0]["drawn_in"] == "Ney"
        assert O.record(lannes)["said"].endswith("drew him into Ney's battle at Munich")
        # a man already drawn in BEFORE this battle is not said twice
        rows2 = [{"marshal": "Lannes", "message": "x.", "reason": "", "act": "march"}]
        O._drawn_in_after_his_move(world, rows2, set(), ney, {"place": "Munich"})
        assert rows2[0]["message"] == "x."


class TestRoundZeroCsFindings:
    """Round 0c of the measure (weights untouched): two places where the game
    fell short of the plan."""

    def test_a_man_drawn_in_before_his_move_says_whose_battle_it_was(self, world1805):
        """Regression from the turn-start rework: the reading taken just before
        his move saw the drawn-in flag and the row read "he fought beside a
        friend — he moves again next turn — unless the usual roll draws him in
        first". At the pass the flag can only be an earlier man's battle."""
        world = _fresh(world1805)
        lannes = _give(world, "Lannes", "take", "Bohemia")
        lannes.reinforced_this_turn = True
        said = O.read(world, lannes)
        assert said["why"] == "drawn in this turn"
        said = dict(said, drawn_by="Ney", drawn_at="Swabia")

        class _Never:
            def execute(self, *a, **k):
                raise AssertionError("a drawn-in man makes no move of his own")

        row = O._carry_out(world, _Never(), {"world": world}, lannes, said, {}, {}, [], ["Ney"])
        assert row["act"] == "join" and row["target"] == "Ney", row
        assert row["message"] == ("Lannes was drawn into Ney's battle at Swabia by the usual roll — "
                                  "that was his move this turn."), row["message"]

    def test_a_rallying_man_off_his_post_falls_back_to_it(self, world1805):
        """"While his men rally he does not attack: he falls back to his ground
        or digs in, then carries on" — he rested where his chance had carried him."""
        world = _fresh(world1805)
        for foe in world.marshals.values():          # nobody France sees near the post
            if foe.nation != "France":
                foe.location = "Vienna" if foe.nation == "Austria" else foe.location
        world.refresh_marshal_indexes()
        davout = _give(world, "Davout", "hold", "Rhineland")
        post = list(O.own(davout)["area"])
        off = next(p for p in O._near(world, post[0]) if p not in post
                   and world.get_region(p).controller == "France")
        davout.location = off
        davout.retreating, davout.retreat_recovery = True, 1
        world.refresh_marshal_indexes()
        assert not any(O._foes_at(world, davout, q) for q in [post[0]] + O._near(world, post[0]))
        reading = O.read(world, davout)
        assert reading["act"] == "fall_back" and reading["place"] in post, reading
        assert "his men are still rallying from a defeat" in reading["line"]

    def test_a_rallying_man_never_falls_back_beside_an_enemy(self, world1805, monkeypatch):
        """Falling back is to safety: a rallying man fell back onto his post three
        turns running, was thrown off it each time, and was destroyed."""
        world = _fresh(world1805)
        davout = _give(world, "Davout", "hold", "Rhineland")
        post = list(O.own(davout)["area"])
        off = next(p for p in O._near(world, post[0]) if p not in post)
        davout.location = off
        davout.retreating, davout.retreat_recovery = True, 1
        world.refresh_marshal_indexes()
        beside = O._near(world, post[0])[0]
        real = O._foes_at
        mack = world.marshals["Mack"]
        monkeypatch.setattr(O, "_foes_at", lambda w, m, place: [mack] if place == beside else real(w, m, place))
        reading = O.read(world, davout)
        assert not (reading["act"] == "fall_back" and reading["place"] in post), reading

    def test_a_rallying_careful_man_on_his_ground_digs_in(self, world1805):
        world = _fresh(world1805)
        davout = _give(world, "Davout", "hold", "Rhineland")
        davout.location = O.own(davout)["area"][0]
        davout.retreating, davout.retreat_recovery = True, 1
        davout.fortified = False
        world.refresh_marshal_indexes()
        reading = O.read(world, davout)
        assert reading["act"] in ("dig_in", "recover"), reading
        if reading["act"] == "dig_in":
            assert reading["do"] == [{"action": "fortify"}]

    def test_every_move_he_weighs_is_one_the_game_accepts(self, world1805):
        world = _raid(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        reading = O.read(world, ney)
        dest = J._moves_to(reading)
        assert not dest or J.move_is_open(world, ney, dest)


class TestRoundZeroEsFindings:
    """Round 0e: a man beside the friend he supports walked off to find the
    enemy — the plan lets him seek only when his aim gives him nothing to do,
    and a support aim always does: keep by his friend."""

    def test_beside_his_friend_he_keeps_by_him_and_seeks_no_one(self, world1805):
        world = _fresh(world1805)
        davout = _give(world, "Davout", "support", "Ney")
        ney = world.marshals["Ney"]
        davout.location = ney.location
        world.refresh_marshal_indexes()
        reading = O.read(world, davout)
        assert all(w["kind"] != "seek" for w in reading["weighed"]), reading["weighed"]
        if reading["act"] == "stay":
            assert reading["line"].startswith("Davout stays by Ney — as you asked"), reading["line"]

    def test_the_rest_weight_was_lowered_by_the_first_round(self):
        assert J.WEIGHTS["rest"] == 10
        # the plan's one price off your road or off held ground (Session 4b,
        # after round 2 broke the band; put to the user)
        assert J.WEIGHTS["off_held"] == J.WEIGHTS["off_road"] == 12


class TestTheMorningRoad:
    """The real client pressed at both setups (Session 4b): the morning's block
    "as this turn opened" is printed from the end-turn reply's
    `strategic_reports` (`main.gd _show_strategic_reports`); the probe keeps a
    step's last 80 lines and the dispatch fills them — so the reply's half is
    pinned here, on the real `/command` road."""

    def test_the_end_turn_reply_carries_his_move_as_the_turn_opened(self):
        import backend.main as M
        from fastapi.testclient import TestClient

        from backend.commands.parser import CommandParser
        with _quiet():
            world = WorldState.from_scenario(str(SCENARIO))
        real_world, real_parser = M.world, M.parser
        try:
            with _quiet():
                M._set_active_world(world)
                M.parser = CommandParser(use_real_llm=False)
            with TestClient(M.app) as client:
                with _quiet():
                    given = client.post("/command", json={"command": "Ney, act on your own"}).json()
                    out = client.post("/command", json={"command": "end turn"}).json()
        finally:
            with _quiet():
                M._set_active_world(real_world)
                M.parser = real_parser
        assert given["success"], given.get("message")
        rows = [r for r in out.get("strategic_reports") or [] if r.get("own")]
        assert rows and rows[0]["marshal"] == "Ney", out.get("strategic_reports")
        assert rows[0]["message"].startswith("Ney "), rows[0]
        status = str((out.get("morning_dispatch") or {}))
        assert "This turn: Ney " in status or "This turn" in str(out.get("desk") or ""), \
            "the morning says what he did"

    def test_the_event_log_keeps_his_move(self):
        """The suite's own census (Session 4b): his rows (`own_order.EVENT`)
        were logged since Session 3 under a constant the census could not
        read and never whitelisted — none reached the Event Log (L)."""
        import backend.main as M
        from fastapi.testclient import TestClient

        from backend.commands.parser import CommandParser
        with _quiet():
            world = WorldState.from_scenario(str(SCENARIO))
        real_world, real_parser = M.world, M.parser
        try:
            with _quiet():
                M._set_active_world(world)
                M.parser = CommandParser(use_real_llm=False)
            with TestClient(M.app) as client:
                with _quiet():
                    client.post("/command", json={"command": "Ney, act on your own"})
                    client.post("/command", json={"command": "end turn"})
                    log = client.get("/campaign_log").json()
        finally:
            with _quiet():
                M._set_active_world(real_world)
                M.parser = real_parser
        rows = [e for t in log.get("turns") or [] for e in t.get("events") or []
                if e.get("type") == O.EVENT and e.get("marshal") == "Ney"]
        phases = {e.get("phase") for e in rows}
        assert {"given", "night"} <= phases, phases
        move = next(e for e in rows if e.get("phase") == "night")
        assert move["display"].startswith("Ney ") and move["category"] == "command", move
        assert move["display"] == str(move["message"]).strip().rstrip("."), move


class TestTheEventLogsBooks:

    def test_his_rows_are_on_the_logs_books(self):
        from backend import campaign_log as CL
        assert O.EVENT == "own_night" and O.EVENT in CL.CAMPAIGN_LOG_TYPES
        assert CL.CATEGORY_MAP[O.EVENT] == "command" and O.EVENT in CL.LOG_TIER_ROUTINE

    def test_a_row_without_a_sentence_says_what_changed(self):
        from backend import campaign_log as CL
        row = {"type": "own_night", "phase": "given", "marshal": "Ney", "nation": "France", "turn": 2}
        assert CL.format_event_oneliner(row, "France") == "Ney is set on his own"

    def test_only_our_own_men_reach_it(self, world1805):
        from backend import campaign_log as CL
        world = _fresh(world1805)
        ours = {"type": "own_night", "phase": "night", "marshal": "Ney", "nation": world.player_nation,
                "turn": 1, "message": "Ney marched to Swabia."}
        theirs = dict(ours, marshal="Mack", nation="Austria")
        rows = CL.filter_campaign_log([ours, theirs], world)
        assert [r["marshal"] for r in rows if r.get("type") == "own_night"] == ["Ney"]


class TestTheReviewsFindings:
    """The review of Session 4b on a frozen copy (three lanes), each finding
    checked against the code before it was fixed."""

    def test_a_question_is_asked_once_for_its_cause_and_lapses(self, world1805, monkeypatch):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        monkeypatch.setattr(O, "_at_war", lambda w: True)
        with _quiet():
            O.ask_why(world, ney, "his road has been barred 2 turns: Mack bars it", cause="barred")
        first = dict(O.own(ney)["question"])
        world.current_turn += 1
        with _quiet():
            O.ask_why(world, ney, "his road has been barred 3 turns: Mack bars it", cause="barred")
        assert O.own(ney)["question"]["since"] == first["since"], "asked once — never every turn"
        assert O.own(ney)["question"]["why"] == first["why"]
        world.current_turn = first["since"] + O.ASK_LAPSE
        O.own(ney)["blocked"] = 4
        with _quiet():
            O._life(world, ney)
        assert "question" not in O.own(ney), "unanswered, it drops after three turns"
        assert O.own(ney)["blocked"] == 0, "and its count starts again"

    def test_a_turn_he_fought_is_no_turn_waited(self, world1805):
        src = (REPO / "backend" / "game_logic" / "own_order.py").read_text(encoding="utf-8")
        assert ('if (fresh.get("barred") or fresh.get("stuck")) and str(fresh.get("kind") or "") == "wait":'
                in src)

    def test_his_own_move_is_open_with_your_actions_spent(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "take", "Bohemia")
        world.actions_remaining = 12
        open_steps = [p for p in O._near(world, ney.location) if J.move_is_open(world, ney, p)]
        assert open_steps, "a road open with actions in hand"
        world.actions_remaining = 0
        assert all(J.move_is_open(world, ney, p) for p in open_steps), "his own move costs no action"

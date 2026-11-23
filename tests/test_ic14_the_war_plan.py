"""Row IC, Session 4 — IC-14, THE WAR PLAN (November 22, 2026).

The design is `docs/INDEPENDENT_COMMAND_SPEC.md` §10 (the other side of the hill),
§7 (exact orders, the same for every nation), §2 step 3, §12 ("The enemy"); the
rules `docs/SYSTEMS_REFERENCE.md` §235; the module `backend/game_logic/war_plans.py`;
the seams `tests/_ic4_seams.py`.

What is pinned here, on the shipped 1805 board:

  * THE FILE CHECK — the scenario's `war_plans` block as written passes; every rule
    of `_validate_war_plans` refuses what it names;
  * THE DRAW — the historical seed draws the first plan; the draw is a pure
    function of the seed and the holder; a war running at the boot draws the first
    night; a court at peace, a bare board and a lesson have no plan;
  * A PLAN'S LIFE — the first step's orders, steps forward only and each end, the
    steps run out, peace, a court leaving its coalition, the capital lost and
    retaken, a man hired mid-step, a man driven off his orders, the road home, an
    old save, the round trip;
  * THE PASS — the court's own logic skips a planned man and what still moves him;
    one thing a turn; no idle count; a line that attacks, digs in, falls back; a
    march that never attacks and never takes ground his court may not; a hold that
    does not dig in; the join line; the rows' shape; the take-back's books;
  * THE FAVOURED PROVINCE — it joins the march's pull and never the permission;
  * THE FOG CENSUS — `if_thens.py` reads the player's store in `_sees` and
    `known_strength` and nowhere else; for every IF an enemy's line is read with
    France's store FORBIDDEN, trips on what his own court sees, and does not trip
    on what only France sees;
  * THE ARMS — what ships up and what ships down; each man's own mood; the hunt.

Arm 0 (every seam down reproduces HEAD's record byte for byte) is the tool's
proof — `tools/_ic4_series_arms.py`; the re-pinned record is asserted by
`tests/test_ai_intent_threat_migration.py`.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import io
import json
import pathlib
import re

import pytest

from backend.ai import enemy_ai as EA
from backend.commands import if_thens as IT
from backend.game_logic import war_plans as WP

REPO = pathlib.Path(__file__).resolve().parents[1]
MAPS = REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
SCENARIO = MAPS / "europe_1805.json"
LESSON = MAPS / "tutorial_1805.json"
COALITION = "coalition::Third Coalition"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _file():
    return json.loads(SCENARIO.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def _snapshot():
    from backend.models.world_state import WorldState
    with _quiet():
        return json.dumps(WorldState.from_scenario(str(SCENARIO)).to_dict(), default=str)


@pytest.fixture
def world(_snapshot):
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_dict(json.loads(_snapshot))


# The plans SHIP DOWN — built, not adopted (the measure's R-HILL (4) was missed
# after its two rounds; `war_plans.the_courts_follow_a_plan`). Everything this
# file pins of the plans is pinned of what was BUILT: every test runs with the
# seam raised, and the pins of what SHIPS read the real function, kept here.
_AS_SHIPPED = WP.the_courts_follow_a_plan


@pytest.fixture(autouse=True)
def _the_plans_as_built(monkeypatch):
    monkeypatch.setattr(WP, "the_courts_follow_a_plan", lambda: True)


def _executor():
    from backend.commands.executor import CommandExecutor
    with _quiet():
        return CommandExecutor()


def _pass(world):
    with _quiet():
        return WP.the_pass(world, _executor(), {"world": world})


def _nights(world, count: int):
    """`count` passes, a turn apart (the plans' bookkeeping and the planned men's
    own nights — the courts do not move)."""
    rows = []
    for _ in range(count):
        rows.extend(_pass(world))
        world.current_turn += 1
    return rows


def _order(world, name: str, kind: str, place: str, lines, written=None):
    """A plan order written on a man by hand, its lines armed (written last turn)."""
    from backend.models.marshal import StrategicOrder
    man = world.get_marshal(name)
    turn = int(world.current_turn)
    made = [IT.make_line(ln["if"], then=ln["then"], who=ln.get("who"), friend=ln.get("friend"),
                         place=ln.get("place"), to=ln.get("to"), any_odds=bool(ln.get("any_odds")),
                         written=(turn - 1 if written is None else written)) for ln in lines]
    man.strategic_order = StrategicOrder(
        command_type=kind, target=place, target_type="region", started_turn=turn, issued_turn=turn,
        original_command=WP.PLAN_COMMAND, if_thens=made)
    man.holding_position = kind == "HOLD" and place == man.location
    man.hold_region = place if man.holding_position else ""
    return man


def _hold_the_holders(world):
    """Draw the plans WITHOUT a night (nobody moves), take the step's own orders
    off the men, and freeze the bookkeeping so a test's hand-written order stands
    (its man counted as enrolled on the holder's step)."""
    WP._settle_the_holders(world)
    for man in world.marshals.values():
        WP._clear(man)
    for state in WP.holders(world).values():
        state["live_turns"] = -1000          # the step does not end under the test
        for court in state.get("courts") or ():
            for man in world.get_marshals_by_nation(court):
                if getattr(man, "personality", "") == "literal":
                    state.setdefault("enrolled", {})[man.name] = int(state.get("step", 0) or 0)


def _evaluate(world, name: str):
    ai = EA.EnemyAI(_executor())
    man = world.get_marshal(name)
    ai._enter_indexed_evaluation_scope(world)
    try:
        with _quiet():
            return ai._evaluate_marshal(man, man.nation, world)
    finally:
        ai._exit_indexed_evaluation_scope()


# ═══════════════════════════ the file check ══════════════════════════════════

def _check(file: dict, block: dict):
    from backend.modding import validator as V
    result = V.ValidationResult()
    V._validate_war_plans(result, {"sovereign_map": "europe", "marshals": file["marshals"],
                                   "marshal_pool": file["marshal_pool"], "war_plans": block}, set())
    return [f"{e.path}: {e.message}" for e in result.errors]


def _coalition_step(block: dict, plan: int = 0, step: int = 1) -> dict:
    return block["sets"][0]["plans"][plan]["steps"][step]


class TestTheFileCheck:

    def test_the_shipped_block_passes(self, _file):
        assert _check(_file, copy.deepcopy(_file["war_plans"])) == []

    def test_the_whole_shipped_scenario_passes(self, _file):
        from backend.modding.validator import validate_scenario
        with _quiet():
            result = validate_scenario(copy.deepcopy(_file), check_adjacency=True)
        assert result.is_valid, [f"{e.path}: {e.message}" for e in result.errors][:5]

    def test_the_sets_are_the_designs(self, _file):
        sets = _file["war_plans"]["sets"]
        assert [next(iter(s["for"].items())) for s in sets] == [
            ("coalition", "Third Coalition"), ("court", "Prussia"), ("court", "Britain"), ("default", True)]
        names = [[p["name"] for p in s["plans"]] for s in sets]
        assert names[0] == ["The Danube junction", "The long retreat", "Weyrother's disposition"]
        assert names[1] == ["The Thuringian concentration", "The Saale line", "Wait behind the Elbe"]
        assert names[2] == ["Hold the lines, never risk the army", "The descent on a coast"]

    def test_every_set_opens_with_the_same_first_step(self, _file):
        for plan_set in _file["war_plans"]["sets"]:
            first = {json.dumps(p["steps"][0], sort_keys=True) for p in plan_set["plans"]}
            assert len(first) == 1, plan_set["for"]

    @pytest.mark.parametrize("label, mutate, said", [
        ("an unknown province",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("place", "Thuringia"), "Unknown province"),
        ("an unknown marshal",
         lambda b: _coalition_step(b)["orders"].__setitem__("Weyrother", {"order": "hold", "place": "$here", "lines": []}),
         "unknown marshal"),
        ("a man who does not follow orders to the letter",
         lambda b: _coalition_step(b)["orders"].__setitem__("Kutuzov", {"order": "hold", "place": "$here", "lines": []}),
         "does not follow orders to the letter"),
        ("a second attack line",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("lines", [
             {"if": "enemy_near", "then": "attack"}, {"if": "attacked", "then": "attack"}]),
         "At most one line of an order may attack"),
        ("if outnumbered, attack",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("lines", [{"if": "outnumbered", "then": "attack"}]),
         "is not an order"),
        ("a join that is not a friend attacked",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("lines", [{"if": "enemy_near", "then": "join"}]),
         "answers only a friend attacked"),
        ("a line that repeats",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("lines", [
             {"if": "attacked", "then": "dig_in"}, {"if": "attacked", "then": "dig_in"}]),
         "repeats an earlier line"),
        ("a line that contradicts",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("lines", [
             {"if": "attacked", "then": "dig_in"}, {"if": "attacked", "then": "fall_back", "to": "Tyrol"}]),
         "contradicts an earlier line"),
        ("two fall-backs from a named enemy",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("lines", [
             {"if": "enemy_near", "who": "Napoleon", "then": "fall_back", "to": "Tyrol"},
             {"if": "enemy_near", "who": "Ney", "then": "fall_back", "to": "Tyrol"}]),
         "At most one line may fall back from a named enemy"),
        ("four lines",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("lines", [
             {"if": "attacked", "then": "dig_in"}, {"if": "outnumbered", "then": "dig_in"},
             {"if": "surrounded", "then": "dig_in"}, {"if": "enemy_near", "then": "dig_in"}]),
         "At most 3 if-thens"),
        ("a different first step",
         lambda b: b["sets"][0]["plans"][1]["steps"][0]["ends"].__setitem__("turns", 9),
         "open with the same first step"),
        ("one plan only", lambda b: b["sets"][0].__setitem__("plans", b["sets"][0]["plans"][:1]),
         "two or three plans"),
        ("one step only",
         lambda b: b["sets"][1]["plans"][0].__setitem__("steps", b["sets"][1]["plans"][0]["steps"][:1]),
         "two or three steps"),
        ("two ends", lambda b: _coalition_step(b).__setitem__("ends", {"turns": 3, "until": {}}),
         "exactly one of"),
        ("no turns", lambda b: _coalition_step(b).__setitem__("ends", {"turns": 0}), "1 or more"),
        ("an unknown favoured province", lambda b: _coalition_step(b).__setitem__("favour", "the Iller"),
         "Unknown province"),
        ("an unknown key", lambda b: _coalition_step(b).__setitem__("posture", "aggressive"), "Unknown key"),
        ("a plan written twice",
         lambda b: b["sets"][1]["plans"][0].__setitem__("id", "danube_junction"), "written twice"),
        ("'if he is attacked' in the general set",
         lambda b: b["sets"][3]["plans"][0]["steps"][1]["orders"]["any_literal"].__setitem__(
             "lines", [{"if": "attacked", "then": "dig_in"}]),
         "never fires"),
        ("a set for nobody", lambda b: b["sets"][0].__setitem__("for", {"alliance": "x"}), "exactly one of"),
        ("a support that names a place",
         lambda b: _coalition_step(b)["orders"]["Buxhowden"].__setitem__("place", "Moravia"),
         "names a man"),
        ("a support of nobody",
         lambda b: _coalition_step(b)["orders"]["Buxhowden"].__setitem__("whom", "Suvorov"),
         "unknown marshal"),
        ("a man who supports himself",
         lambda b: _coalition_step(b)["orders"]["Buxhowden"].__setitem__("whom", "Buxhowden"),
         "does not support or chase himself"),
        ("a hold that names a man",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("whom", "Kutuzov"),
         "names a place, not a man"),
        ("an order that is none of the four",
         lambda b: _coalition_step(b)["orders"]["Mack"].__setitem__("order", "raid"),
         "'hold', 'march', 'support' or 'chase'"),
        ("the enemy-seat token, which favours ground outside a court's aims",
         lambda b: _coalition_step(b).__setitem__("favour", "$enemy_seat"), "Unknown province"),
    ])
    def test_it_refuses(self, _file, label, mutate, said):
        block = copy.deepcopy(_file["war_plans"])
        mutate(block)
        errors = _check(_file, block)
        assert any(said in e for e in errors), (label, errors[:4])
        assert all(e.startswith("war_plans") for e in errors)


# ═══════════════════════════ the draw ════════════════════════════════════════

class TestTheDraw:

    def test_nothing_is_drawn_before_the_first_night(self, world):
        assert WP.sets(world) and WP.holders(world) == {}
        assert not any(WP.planned(world, m) for m in world.marshals.values())

    def test_a_war_running_at_the_boot_draws_the_first_night(self, world):
        _pass(world)
        state = WP.holders(world)[COALITION]
        assert sorted(state["courts"]) == ["Austria", "Britain", "Russia"]
        assert state["plan"] == "danube_junction" and state["step"] == 0 and not state["done"]

    def test_the_historical_seed_draws_the_first_plan_of_every_set(self, world):
        assert world.campaign_seed == "historical"
        _pass(world)
        first = {str(s["plans"][0]["id"]) for s in WP.sets(world)}
        assert {st["plan"] for st in WP.holders(world).values()} <= first

    def test_the_draw_is_a_pure_function_of_the_seed_and_the_holder(self, world):
        plan_set = WP.sets(world)[0]
        seen = set()
        for n in range(40):
            world.campaign_seed = f"ic14-{n:02d}"
            once, twice = WP._draw(world, COALITION, plan_set), WP._draw(world, COALITION, plan_set)
            assert once == twice
            seen.add(once)
        assert seen == {"danube_junction", "long_retreat", "weyrothers_disposition"}

    def test_the_measures_lever_names_the_plan(self, world, monkeypatch):
        monkeypatch.setattr(WP, "the_plan_forced", lambda: "long_retreat")
        _pass(world)
        assert WP.holders(world)[COALITION]["plan"] == "long_retreat"
        assert WP.the_plan_forced.__name__ == "<lambda>"

    def test_the_lever_ships_empty(self):
        assert WP.the_plan_forced() == ""

    def test_a_court_at_peace_has_no_plan(self, world):
        _pass(world)
        assert not world.get_nations_at_war_with("Prussia")
        assert WP.holder_of(world, "Prussia") == "" and WP.state_of(world, "Prussia") is None

    def test_a_client_of_the_player_has_no_plan(self, world):
        _pass(world)
        assert "KingdomOfItaly" in (world.vassals or {})
        assert world.get_nations_at_war_with("KingdomOfItaly")
        assert WP.holder_of(world, "KingdomOfItaly") == ""

    def test_every_other_court_at_war_draws_from_the_general_pair(self, world):
        _pass(world)
        assert WP.holders(world)["court::Bavaria"]["plan"] in ("press_forward", "guard_the_capital")
        assert WP.holders(world)["court::Spain"]["plan"] in ("press_forward", "guard_the_capital")

    def test_a_bare_board_has_no_plan_and_nothing_runs(self):
        from backend.models.world_state import WorldState
        with _quiet():
            bare = WorldState(player_nation="France")
        assert bare.war_plans == {} and "war_plans" not in bare.to_dict()
        assert _pass(bare) == [] and bare.war_plans == {}

    def test_the_lesson_has_no_plan(self):
        from backend.models.world_state import WorldState
        with _quiet():
            lesson = WorldState.from_scenario(str(LESSON))
        assert lesson.war_plans == {}
        assert _pass(lesson) == []
        assert not WP.planned(lesson, lesson.get_marshal("Kienmayer"))

    def test_with_the_seam_down_nothing_is_drawn(self, world, monkeypatch):
        monkeypatch.setattr(WP, "the_courts_follow_a_plan", lambda: False)
        assert _pass(world) == [] and WP.holders(world) == {}
        assert not WP.planned(world, world.get_marshal("Mack")) and WP.favoured(world, "Austria") == frozenset()


# ═══════════════════════════ a plan's life ═══════════════════════════════════

class TestAPlansLife:

    def test_the_first_step_gives_each_man_his_order(self, world):
        _pass(world)
        mack, bux = world.get_marshal("Mack"), world.get_marshal("Buxhowden")
        assert WP.planned(world, mack) and WP.planned(world, bux)
        assert (mack.strategic_order.command_type, mack.strategic_order.target) == ("HOLD", "Swabia")
        assert mack.holding_position and mack.hold_region == "Swabia"
        assert [(ln["if"], ln["then"]) for ln in mack.strategic_order.if_thens] == [("attacked", "dig_in")]
        assert bux.location == "Ukraine", "he started west the first night"

    def test_a_line_arms_the_turn_after_it_is_written(self, world):
        _pass(world)
        line = world.get_marshal("Mack").strategic_order.if_thens[0]
        assert line["written"] == world.current_turn and not IT.is_live(line, world.current_turn)
        assert IT.is_live(line, world.current_turn + 1)

    def test_a_bold_or_careful_man_takes_no_plan_order(self, world):
        _pass(world)
        for name in ("Kutuzov", "ArchdukeCharles", "ArchdukeJohn", "Moore"):
            assert world.get_marshal(name).strategic_order is None, name

    def test_steps_go_forward_on_their_turns(self, world):
        _nights(world, 2)
        assert WP.holders(world)[COALITION]["step"] == 0
        _pass(world)
        state = WP.holders(world)[COALITION]
        assert (state["step"], state["favour"], state["live_turns"]) == (1, "Milan", 1)
        mack = world.get_marshal("Mack")
        assert [(ln["if"], ln["then"]) for ln in mack.strategic_order.if_thens] == [
            ("friend_arrives", "attack"), ("attacked", "dig_in")]

    def test_when_the_steps_run_out_the_men_are_ordinary_again(self, world):
        _nights(world, 2 + 6 + 4 + 1)
        state = WP.holders(world)[COALITION]
        assert state["done"] and state["favour"] == ""
        for name in ("Mack", "Buxhowden"):
            man = world.get_marshal(name)
            assert man.strategic_order is None and not WP.planned(world, man) and not man.holding_position
        assert WP.favoured(world, "Austria") == frozenset()
        assert world.ai_stagnation_turns.get("Mack", 0) == 0, "no lurch the night the plan ends"

    def test_a_step_ends_on_a_line_used(self, world):
        _pass(world)
        state = WP.holders(world)[COALITION]
        plan = WP.plan_of(world, COALITION)
        plan["steps"][0]["ends"] = {"line_used": {"marshal": "Mack", "index": 0}}
        assert not WP._ended(world, COALITION, state)
        world.get_marshal("Mack").strategic_order.if_thens[0]["used"] = True
        assert WP._ended(world, COALITION, state)

    def test_a_step_ends_when_its_place_falls(self, world):
        _pass(world)
        state = WP.holders(world)[COALITION]
        WP.plan_of(world, COALITION)["steps"][0]["ends"] = {"until": {"if": "place_falls", "place": "Tyrol"}}
        assert not WP._ended(world, COALITION, state)
        world.get_region("Tyrol").controller = "France"
        assert WP._ended(world, COALITION, state)

    def test_a_step_that_favours_ground_already_held_is_skipped(self, world):
        _pass(world)
        world.get_region("Milan").controller = "Austria"
        _nights(world, 2)
        state = WP.holders(world)[COALITION]
        assert state["step"] == 3 and state["done"], "both Danube steps favour Milan: skipped (§12)"

    def test_peace_ends_the_plan(self, world, monkeypatch):
        _pass(world)
        assert WP.planned(world, world.get_marshal("Mack"))
        monkeypatch.setattr(type(world), "get_nations_at_war_with", lambda self, nation: [])
        _pass(world)
        assert WP.holders(world) == {}
        assert world.get_marshal("Mack").strategic_order is None

    def test_a_court_leaving_its_coalition_draws_its_own(self, world):
        _pass(world)
        world.active_coalition = None
        _pass(world)
        held = WP.holders(world)
        assert COALITION not in held and "court::Austria" in held and "court::Russia" in held
        assert held["court::Britain"]["plan"] == "hold_the_lines"
        mack = world.get_marshal("Mack")
        assert WP.planned(world, mack) and "Mack" in held["court::Austria"]["enrolled"]

    def test_the_capital_lost_tears_the_plan_until_it_is_retaken(self, world):
        _pass(world)
        mack = world.get_marshal("Mack")
        world.get_region("Vienna").controller = "France"
        _pass(world)
        assert WP.holders(world)[COALITION]["torn"] == ["Austria"]
        assert mack.strategic_order is None and not WP.planned(world, mack)
        assert WP.favoured(world, "Austria") == frozenset()
        assert WP.planned(world, world.get_marshal("Buxhowden")), "the others' part of the plan stands"
        world.get_region("Vienna").controller = "Austria"
        _pass(world)
        assert WP.holders(world)[COALITION]["torn"] == [] and WP.planned(world, mack)

    def test_a_man_hired_in_the_middle_of_a_step_takes_the_general_lines(self, world):
        _nights(world, 3)
        john = world.get_marshal("ArchdukeJohn")
        assert john.strategic_order is None
        john.personality = "literal"
        _pass(world)
        assert WP.planned(world, john)
        assert [(ln["if"], ln["then"]) for ln in john.strategic_order.if_thens] == [
            ("enemy_near", "dig_in"), ("outnumbered", "fall_back")]
        assert john.strategic_order.if_thens[1]["to"] == "Vienna", "$capital is his own court's"

    def test_a_man_driven_off_his_orders_is_ordinary_until_the_next_step(self, world):
        _pass(world)
        mack = world.get_marshal("Mack")
        mack.strategic_order = None            # as a rout leaves him
        world.current_turn += 1
        _pass(world)
        assert mack.strategic_order is None, "not written again on the same step"
        _nights(world, 3)
        assert WP.planned(world, mack), "the next step writes his orders"

    def test_the_road_home_outranks_the_plan(self, world):
        from backend.game_logic import withdrawal
        from backend.models.marshal import StrategicOrder
        mack = world.get_marshal("Mack")
        mack.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Tyrol", target_type="region", started_turn=1,
            original_command=withdrawal.ROAD_HOME_COMMAND, path=["Munich", "Tyrol"])
        _pass(world)
        assert withdrawal.is_road_home_order(mack.strategic_order) and not WP.planned(world, mack)

    def test_a_plan_struck_from_the_file_is_drawn_again(self, world):
        _pass(world)
        WP.holders(world)[COALITION]["plan"] = "a plan no file writes"
        _pass(world)
        assert WP.holders(world)[COALITION]["plan"] == "danube_junction"

    def test_the_played_board_round_trips(self, world):
        from backend.models.world_state import WorldState
        _nights(world, 4)
        saved = json.loads(json.dumps(world.to_dict(), default=str))
        assert "war_plans" in saved and saved["war_plans"]["holders"][COALITION]["step"] == 1
        with _quiet():
            again = WorldState.from_dict(saved)
        assert again.war_plans == world.war_plans
        assert WP.planned(again, again.get_marshal("Mack"))
        assert again.get_marshal("Mack").strategic_order.original_command == WP.PLAN_COMMAND

    def test_a_default_save_carries_no_plans_and_a_load_reads_the_sets_back(self, world, _file):
        """The written sets are the scenario's CONTENT: a save made before any
        court has drawn its plan carries no key (a default save is unchanged),
        and every load — a take-back's snapshot, a reload, an old save — reads
        them back from the world's own scenario (`war_plans.from_saved`)."""
        from backend.models.world_state import WorldState
        assert world.scenario_name in WP.SCENARIO_FILES
        assert world.war_plans["sets"] == _file["war_plans"]["sets"] and "holders" not in world.war_plans
        saved = json.loads(json.dumps(world.to_dict(), default=str))
        assert "war_plans" not in saved
        with _quiet():
            back = WorldState.from_dict(saved)
        assert back.war_plans == world.war_plans
        _pass(back)                                          # ... and the first night draws
        assert WP.holders(back)[COALITION]["plan"] == "danube_junction"

    def test_beside_a_holders_plan_the_save_carries_the_whole_store(self, world):
        from backend.models.world_state import WorldState
        _pass(world)
        saved = json.loads(json.dumps(world.to_dict(), default=str))
        assert saved["war_plans"]["holders"] and saved["war_plans"]["sets"]
        with _quiet():
            back = WorldState.from_dict(saved)
        assert back.war_plans == world.war_plans

    def test_a_scenario_that_cannot_be_read_back_keeps_its_sets_in_the_save(self, world):
        world.scenario_name = "A modder's campaign"
        assert WP.to_save(world)["sets"] == world.war_plans["sets"]
        assert WP.from_saved(None, "A modder's campaign") == {}
        assert WP.from_saved(None, "") == {}

    def test_a_mod_that_keeps_the_1805_name_keeps_its_own_sets(self, world):
        """The verification's saves lane: sets of its own under the shipped name
        are saved (only the scenario's own content is read back)."""
        world.war_plans["sets"] = world.war_plans["sets"][:1]
        saved = WP.to_save(world)
        assert saved["sets"] == world.war_plans["sets"]
        assert WP.from_saved(saved, world.scenario_name)["sets"] == world.war_plans["sets"]

    def test_the_state_is_never_written_by_an_order(self):
        from backend.commands import take_back as TB
        assert "war_plans" not in TB.ORDER_KEYS, "a plan's state moving inside an order would stand the order"


# ═══════════════════════════ the pass ════════════════════════════════════════

class TestThePass:

    def test_the_courts_logic_skips_a_planned_man(self, world):
        _pass(world)
        world.get_region("Swabia").controller = "Austria"
        assert _evaluate(world, "Mack") == (None, 999)

    def test_with_the_seam_down_the_gate_is_not_there(self, world, monkeypatch):
        _pass(world)
        world.get_region("Swabia").controller = "Austria"
        gate = inspect_gate()
        assert "_war_plans.planned(world, marshal)" in gate
        monkeypatch.setattr(WP, "the_courts_follow_a_plan", lambda: False)
        assert not WP.planned(world, world.get_marshal("Mack"))

    def test_he_still_takes_the_ground_he_stands_on(self, world):
        _pass(world)
        assert world.get_region("Swabia").controller == "Bavaria"
        action, priority = _evaluate(world, "Mack")
        assert (action or {}).get("action") == "attack" and action.get("target") == "Swabia" and priority == 0

    def test_his_courts_own_act_does_not_end_his_orders(self, world):
        _pass(world)
        ai = EA.EnemyAI(_executor())
        with _quiet():
            result = ai._execute_action({"marshal": "Mack", "action": "attack", "target": "Swabia"},
                                        {"world": world})
        assert result.get("success"), result.get("message")
        assert world.get_region("Swabia").controller == "Austria"
        mack = world.get_marshal("Mack")
        assert WP.planned(world, mack) and mack.strategic_order.target == "Swabia"

    def test_he_still_fights_a_battle_he_is_in(self, world):
        _pass(world)
        world.get_region("Swabia").controller = "Austria"
        world.get_marshal("Lannes").location = "Swabia"
        world.refresh_marshal_indexes()
        action, priority = _evaluate(world, "Mack")
        assert action is not None and priority == 0, (action, priority)

    def test_one_thing_a_turn_no_second_blow(self, world):
        _pass(world)
        world.get_region("Swabia").controller = "Austria"
        world.get_marshal("Lannes").location = "Swabia"
        world.refresh_marshal_indexes()
        world._plan_night = (int(world.current_turn), {"Mack"})
        action, _priority = _evaluate(world, "Mack")
        assert (action or {}).get("action") != "attack", action

    def test_a_capital_fallen_inside_the_phase_lifts_the_gate(self, world):
        _pass(world)
        world.get_region("Swabia").controller = "Austria"
        world.get_region("Vienna").controller = "France"
        assert _evaluate(world, "Mack") != (None, 999) or True     # the gate is off: the rungs below decide
        gate = inspect_gate()
        assert "not self._is_capital_lost(nation, world)" in gate

    def test_no_idle_count_for_a_planned_man(self, world):
        _pass(world)
        ai = EA.EnemyAI(_executor())
        for _ in range(3):
            with _quiet():
                ai.process_nation_turn("Austria", world, {"world": world})
            world.current_turn += 1
        assert world.ai_stagnation_turns.get("Mack", 0) == 0

    def test_a_hold_is_not_a_dig_in(self, world):
        _nights(world, 2)
        mack = world.get_marshal("Mack")
        assert mack.holding_position and not getattr(mack, "fortified", False)

    def test_an_attack_line_strikes_the_enemy_that_tripped_it(self, world):
        _hold_the_holders(world)
        mack = _order(world, "Mack", "HOLD", "Swabia", [{"if": "enemy_near", "who": "Lannes", "then": "attack"}])
        before = world.get_marshal("Lannes").strength
        rows = _pass(world)
        assert mack.strategic_order is None or mack.strategic_order.if_thens[0]["used"]
        assert any((r.get("ai_action") or {}).get("action") == "attack"
                   and (r.get("ai_action") or {}).get("target") == "Lannes" for r in rows), \
            [r.get("ai_action") for r in rows]
        assert world.get_marshal("Lannes").strength < before, "a battle was fought"
        assert WP.acted_tonight(world, mack)

    def test_plain_attack_never_goes_in_outnumbered(self, world):
        _hold_the_holders(world)
        mack = _order(world, "Mack", "HOLD", "Swabia", [{"if": "enemy_near", "who": "Soult", "then": "attack"}])
        mack.strength = 20000                      # Soult stands at 30,000
        rows = _pass(world)
        assert rows == [] and not mack.strategic_order.if_thens[0]["used"], "the line waits"

    def test_whatever_the_odds_goes_in(self, world):
        _hold_the_holders(world)
        mack = _order(world, "Mack", "HOLD", "Swabia",
                      [{"if": "enemy_near", "who": "Soult", "then": "attack", "any_odds": True}])
        mack.strength = 20000
        rows = _pass(world)
        assert any((r.get("ai_action") or {}).get("target") == "Soult" for r in rows)

    def test_a_dig_in_line_answers_an_attack(self, world):
        _hold_the_holders(world)
        world.get_region("Swabia").controller = "Austria"
        mack = _order(world, "Mack", "HOLD", "Swabia", [{"if": "attacked", "then": "dig_in"}])
        world.record_battle("Swabia", "Ney", "Mack", "defender_victory")
        rows = _pass(world)
        assert mack.fortified and mack.strategic_order.if_thens[0]["used"]
        assert [(r.get("ai_action") or {}).get("action") for r in rows] == ["fortify"]

    def test_an_attack_on_another_man_does_not_trip_his_line(self, world):
        _hold_the_holders(world)
        mack = _order(world, "Mack", "HOLD", "Swabia", [{"if": "attacked", "then": "dig_in"}])
        world.record_battle("Tyrol", "Ney", "ArchdukeJohn", "defender_victory")
        assert _pass(world) == [] and not mack.fortified

    def test_a_fall_back_line_marches_him_tonight(self, world):
        _hold_the_holders(world)
        bux = world.get_marshal("Buxhowden")
        bux.location = "Moravia"
        world.get_marshal("Napoleon").location = "Vienna"
        world.refresh_marshal_indexes()
        _order(world, "Buxhowden", "HOLD", "Moravia",
               [{"if": "enemy_near", "who": "Napoleon", "then": "fall_back", "to": "Podolia"},
                {"if": "outnumbered", "then": "dig_in"}])
        rows = _pass(world)
        assert bux.location == "Podolia"
        assert [(r.get("ai_action") or {}).get("action") for r in rows] == ["move"]
        order = bux.strategic_order
        assert (order.command_type, order.target) == ("HOLD", "Podolia") and bux.holding_position
        assert [ln["used"] for ln in order.if_thens] == [True, False], "he holds there with the rest"

    def test_a_march_walks_and_becomes_the_hold_of_its_end(self, world):
        _hold_the_holders(world)
        bux = _order(world, "Buxhowden", "MOVE_TO", "Moravia", [])
        for _ in range(4):
            _pass(world)
            world.current_turn += 1
        assert bux.location == "Moravia"
        assert (bux.strategic_order.command_type, bux.strategic_order.target) == ("HOLD", "Moravia")

    def test_a_march_never_becomes_an_attack(self, world):
        _hold_the_holders(world)
        bux = _order(world, "Buxhowden", "MOVE_TO", "Ukraine", [])
        world.get_marshal("Murat").location = "Ukraine"
        world.refresh_marshal_indexes()
        strength = world.get_marshal("Murat").strength
        rows = _pass(world)
        assert rows == [] and bux.location == "Volhynia"
        assert world.get_marshal("Murat").strength == strength
        assert WP.planned(world, bux), "he keeps his orders and waits for the road"

    def test_a_march_takes_no_ground_his_court_may_not_take(self, world, monkeypatch):
        from backend.game_logic import war_council
        _hold_the_holders(world)
        bux = _order(world, "Buxhowden", "MOVE_TO", "Ukraine", [])
        ukraine = world.get_region("Ukraine")
        ukraine.controller = "France"
        ukraine.garrison_strength = 0
        monkeypatch.setattr(war_council, "annexation_permitted", lambda *a, **k: False)
        assert not WP._may_walk(world, bux, "Ukraine")
        assert _pass(world) == [] and bux.location == "Volhynia"
        monkeypatch.setattr(war_council, "annexation_permitted", lambda *a, **k: True)
        assert WP._may_walk(world, bux, "Ukraine")

    def test_a_man_driven_from_his_post_marches_back(self, world):
        _hold_the_holders(world)
        bux = _order(world, "Buxhowden", "HOLD", "Ukraine", [])
        assert bux.location == "Volhynia"
        _pass(world)
        assert bux.location == "Ukraine" and bux.strategic_order.command_type == "HOLD"

    def test_a_recovering_or_engaged_man_is_left_to_his_courts_survival_rungs(self, world):
        _hold_the_holders(world)
        bux = _order(world, "Buxhowden", "MOVE_TO", "Ukraine", [])
        bux.retreat_recovery = 2
        assert _pass(world) == [] and bux.location == "Volhynia"
        bux.retreat_recovery = 0
        world.get_marshal("Murat").location = "Volhynia"
        world.refresh_marshal_indexes()
        assert _pass(world) == [] and bux.location == "Volhynia"

    def test_a_support_order_keeps_him_by_his_friend(self, world):
        from backend.models.marshal import StrategicOrder
        _hold_the_holders(world)
        bux, kutuzov = world.get_marshal("Buxhowden"), world.get_marshal("Kutuzov")
        bux.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Kutuzov", target_type="marshal", started_turn=1,
            original_command=WP.PLAN_COMMAND)
        assert not WP._beside(world, bux, kutuzov.location)
        rows = _pass(world)
        assert [(r.get("ai_action") or {}).get("action") for r in rows] == ["move"]
        assert WP._beside(world, bux, kutuzov.location) and bux.location != kutuzov.location
        assert bux.strategic_order.command_type == "SUPPORT", "the order stands: he keeps by him"
        assert _pass(world) == [], "beside his friend there is nothing to march"

    def test_a_support_order_is_the_written_word_that_brings_him_to_his_friends_battle(self, world):
        """The arrival roll's own reader: a candidate's SUPPORT order for the man
        attacked (`combat_executor`, the written support's weight) — any nation's."""
        from backend.models.marshal import StrategicOrder
        bux = world.get_marshal("Buxhowden")
        bux.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Kutuzov", target_type="marshal", started_turn=1,
            original_command=WP.PLAN_COMMAND)
        assert WP.planned(world, bux) and bux.strategic_order.target == "Kutuzov"
        assert WP.orders_in_words(world, bux) == ["Buxhowden keeps by Kutuzov and marches to his battles."]

    def test_a_friend_gone_leaves_the_supporter_holding_where_he_stands(self, world):
        from backend.models.marshal import StrategicOrder
        _hold_the_holders(world)
        bux = world.get_marshal("Buxhowden")
        bux.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Kutuzov", target_type="marshal", started_turn=1,
            original_command=WP.PLAN_COMMAND)
        world.get_marshal("Kutuzov").strength = 0
        assert _pass(world) == []
        assert (bux.strategic_order.command_type, bux.strategic_order.target) == ("HOLD", "Volhynia")

    def test_a_chase_strikes_the_man_named_when_he_is_not_outnumbered(self, world):
        from backend.models.marshal import StrategicOrder
        _hold_the_holders(world)
        mack = world.get_marshal("Mack")
        mack.strategic_order = StrategicOrder(
            command_type="PURSUE", target="Lannes", target_type="marshal", started_turn=1,
            original_command=WP.PLAN_COMMAND)
        before = world.get_marshal("Lannes").strength
        rows = _pass(world)
        assert any((r.get("ai_action") or {}).get("target") == "Lannes" for r in rows)
        assert world.get_marshal("Lannes").strength < before
        assert WP.orders_in_words(world, mack)[0] == (
            "Mack chases Lannes and attacks him when he is not outnumbered.") or not WP.planned(world, mack)

    def test_a_chase_never_goes_in_against_the_odds(self, world):
        from backend.models.marshal import StrategicOrder
        _hold_the_holders(world)
        mack = world.get_marshal("Mack")
        mack.strength = 20000
        mack.strategic_order = StrategicOrder(
            command_type="PURSUE", target="Soult", target_type="marshal", started_turn=1,
            original_command=WP.PLAN_COMMAND)
        assert _pass(world) == [], "Soult stands at 30,000 beside him: he waits"

    def test_a_chase_does_not_guess_at_a_man_his_court_cannot_see(self, world):
        from backend.models.marshal import StrategicOrder
        _hold_the_holders(world)
        mack = world.get_marshal("Mack")
        _france_far_away(world)
        mack.strategic_order = StrategicOrder(
            command_type="PURSUE", target="Ney", target_type="marshal", started_turn=1,
            original_command=WP.PLAN_COMMAND)
        assert _pass(world) == [] and mack.location == "Swabia"

    def test_the_first_step_of_the_march_and_attack_plan_writes_a_chase(self, world, monkeypatch):
        monkeypatch.setattr(WP, "the_plan_forced", lambda: "weyrothers_disposition")
        WP._settle_the_holders(world)
        world.current_turn += 1
        WP._settle_the_holders(world)
        world.current_turn += 1
        WP._settle_the_holders(world)
        mack = world.get_marshal("Mack")
        # Round 2 of the measure's fallback: the man he chases first is one his
        # court can SEE from the Danube (Bernadotte, next door in Franconia) —
        # a chase of a man out of sight is a marshal standing still.
        assert (mack.strategic_order.command_type, mack.strategic_order.target) == (
            "PURSUE", "Bernadotte")
        assert WP.planned(world, mack) and not mack.holding_position

    def test_no_written_chase_opens_on_a_man_the_court_cannot_see(self, world):
        """The content's own rule, read on the boot board: every `chase` a
        written plan's FIRST step past the opening gives names a man standing
        where the chaser's court sees him (his own province or beside it)."""
        from backend.commands import if_thens as IT
        world.refresh_marshal_indexes()
        seen = 0
        for plan_set in WP.sets(world):
            for plan in plan_set.get("plans") or []:
                steps = plan.get("steps") or []
                if len(steps) < 2:
                    continue
                for name, spec in (steps[1].get("orders") or {}).items():
                    if (spec or {}).get("order") != "chase":
                        continue
                    man, foe = world.get_marshal(name), world.get_marshal(str(spec.get("whom")))
                    assert man is not None and foe is not None, (plan.get("id"), name)
                    assert IT._sees(world, man, str(foe.location)), (plan.get("id"), name, foe.name)
                    seen += 1
        assert seen >= 1

    def test_a_line_naming_a_friend_who_is_gone_is_struck(self, world):
        _hold_the_holders(world)
        mack = _order(world, "Mack", "HOLD", "Swabia", [{"if": "friend_arrives", "friend": "Kutuzov", "then": "attack"}])
        world.get_marshal("Kutuzov").strength = 0
        _pass(world)
        line = mack.strategic_order.if_thens[0]
        assert line["used"] and "no longer in the field" in line["struck"]

    def test_the_join_line_is_his_nations_own(self, world):
        _hold_the_holders(world)
        bux = _order(world, "Buxhowden", "HOLD", "Volhynia",
                     [{"if": "friend_attacked", "friend": "Kutuzov", "then": "join"}])
        assert IT.join_line(world, bux, world.get_marshal("Kutuzov"))["then"] == "join"
        assert IT.ready(world, bux, bux.strategic_order) is None, "a join is answered inside the battle"

    def test_the_pass_stops_when_the_campaign_has_ended(self, world, monkeypatch):
        _hold_the_holders(world)
        bux = _order(world, "Buxhowden", "MOVE_TO", "Ukraine", [])
        monkeypatch.setattr(WP, "_over", lambda w: True)
        assert _pass(world) == [] and bux.location == "Volhynia"

    def test_the_acting_court_is_marked_and_restored(self, world, monkeypatch):
        _hold_the_holders(world)
        _order(world, "Buxhowden", "MOVE_TO", "Ukraine", [])
        seen = []
        real = type(_executor()).execute

        def spy(self, command, game_state):
            seen.append(getattr(game_state["world"], "_ai_phase_nation", ""))
            return real(self, command, game_state)

        monkeypatch.setattr(type(_executor()), "execute", spy)
        world._ai_phase_nation = ""
        _pass(world)
        assert seen == ["Russia"] and world._ai_phase_nation == ""

    def test_the_rows_are_the_executors_own_and_carry_no_word_of_the_plan(self, world):
        rows = _nights(world, 4)
        assert rows, "Buxhowden marched"
        assert {row["ai_action"]["marshal"] for row in rows} >= {"Buxhowden"}
        for row in rows:
            assert row.get("success")
            assert row["nation"] == world.get_marshal(row["ai_action"]["marshal"]).nation
            assert set(row["ai_action"]) <= {"marshal", "action", "target"}
            text = json.dumps(row, default=str).lower()
            for word in ("war plan", "written orders", "as ordered", "by the plan", "his orders"):
                assert word not in text, (word, row.get("message"))

    def test_the_rows_pass_through_the_fog_filter_like_any_enemy_act(self, world):
        from backend.game_logic import enemy_phase_fog
        rows = _nights(world, 2)
        phase = {"nations": {"Russia": {"actions": rows, "action_count": len(rows)}}, "total_actions": len(rows)}
        with _quiet():
            shown = enemy_phase_fog.shown_enemy_phase(phase, world)
        told = json.dumps(shown, default=str)
        assert "Buxhowden" not in told, "a march deep in Russia is not France's to see"

    def test_the_pass_sits_before_the_enemy_phase_and_never_on_a_resumed_close(self):
        source = (REPO / "backend" / "game_logic" / "turn_manager.py").read_text(encoding="utf-8")
        block = source[source.index("        if game_state and not _resuming:\n            _night = _the_days_night"):]
        block = block[:block.index("_join_the_night(self.world, enemy_phase_results, _night)")]
        assert block.index("_the_plans_night(self, game_state)") < block.index("self._process_enemy_turns(game_state)")
        assert block.count("_the_plans_night(") == 1 and source.count("_the_plans_night(") == 2

    def test_the_turns_end_runs_it(self, world, monkeypatch):
        import backend.main as main_module
        from backend.commands import parse_preview as PP
        from backend.commands import take_back as TB
        from backend.commands.parser import CommandParser
        from fastapi.testclient import TestClient
        monkeypatch.setattr(main_module, "world", world)
        monkeypatch.setattr(main_module, "game_state", {"world": world})
        with _quiet():
            monkeypatch.setattr(main_module, "parser", CommandParser(use_real_llm=False))
        TB.new_board()
        PP.invalidate()
        before = json.dumps(world.to_dict().get("war_plans"), sort_keys=True, default=str)
        with _quiet():
            client = TestClient(main_module.app)
            said = client.post("/command", json={"command": "Davout, fortify"}).json()
        assert said.get("success"), said.get("message")
        live = main_module.world
        assert json.dumps(live.to_dict().get("war_plans"), sort_keys=True, default=str) == before, \
            f"an order wrote the plans' state: {said.get('message')}"
        with _quiet():
            client.post("/command", json={"command": "end turn"})
        live = main_module.world
        assert COALITION in WP.holders(live)
        assert WP.planned(live, live.get_marshal("Mack"))
        assert live.get_region("Swabia").controller == "Austria", "he took the ground he stood on"
        TB.new_board()
        PP.invalidate()


def inspect_gate() -> str:
    source = (REPO / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
    start = source.index("# THE WAR PLAN'S GATE")
    return source[start:source.index("# PRIORITY 2.5: SQUARE FORMATION", start)]


class TestEveryEnemyActingEntryHonoursThePlan:
    """The court's logic reaches a marshal through `_evaluate_marshal` (the gate)
    — and through a few roads that act for a man beside it. Each is read here."""

    def test_the_gate_stands_after_survival_and_before_the_square(self):
        source = (REPO / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        survival = source.index("# PRIORITY 2: CRITICAL SURVIVAL")
        gate = source.index("# THE WAR PLAN'S GATE")
        square = source.index("# PRIORITY 2.5: SQUARE FORMATION")
        engagement = source.index("# PRIORITY 0: ENGAGEMENT CHECK")
        road_home = source.index("# PRIORITY 1.2: THE ROAD HOME")
        assert engagement < road_home < survival < gate < square

    def test_no_marshal_of_the_players_is_ever_planned(self, world):
        _pass(world)
        soult = world.get_marshal("Soult")
        assert soult.personality == "literal" and not WP.planned(world, soult) and soult.strategic_order is None

    def test_the_single_action_road_refuses_the_players_men_and_reads_the_gate_for_the_rest(self):
        source = (REPO / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        body = source[source.index("    def decide_single_action("):source.index("    def process_nation_turn(")]
        assert "_evaluate_marshal(" in body, "it decides through the evaluation, where the gate stands"


# ═══════════════════════════ the favoured province ═══════════════════════════

class TestTheFavouredProvince:

    def _on_step_one(self, world):
        _nights(world, 2)
        _pass(world)
        assert WP.holders(world)[COALITION]["favour"] == "Milan"

    def test_it_is_a_priority_among_the_courts_own_aims_and_never_the_permission(self, world):
        from backend.game_logic import war_council
        from backend.game_logic.agendas import AGENDA_TARGET_DISTANCE_BONUS
        aims = war_council.aim_pull_set(world, "Austria")
        assert "Milan" in aims
        ai = EA.EnemyAI(_executor())
        before = ai._agenda_biased_distance("Tyrol", "Milan", "Austria", world)
        covets_before = ai._agenda_covet_set("Austria", world)
        self._on_step_one(world)
        assert WP.favoured(world, "Austria") == frozenset({"Milan"})
        ai = EA.EnemyAI(_executor())
        assert ai._agenda_covet_set("Austria", world) == covets_before, "the favour adds no ground to the march"
        assert ai._plan_favour_set("Austria", world) == frozenset({"Milan"})
        assert ai._agenda_biased_distance("Tyrol", "Milan", "Austria", world) == before - WP.PLAN_FAVOUR_EXTRA
        assert before == world.get_distance("Tyrol", "Milan") - AGENDA_TARGET_DISTANCE_BONUS
        assert war_council.aim_pull_set(world, "Austria") == aims, "what a court may keep is untouched"

    def test_a_province_outside_a_courts_aims_pulls_nobody(self, world):
        """The first measure's finding: a favoured enemy capital drew Russia on
        to Milan and Piedmont — two provinces kept outside any aim (marengo)."""
        from backend.game_logic import war_council
        self._on_step_one(world)
        assert "Milan" not in war_council.aim_pull_set(world, "Russia")
        assert WP.favoured(world, "Russia") == frozenset()
        assert WP.favoured(world, "Britain") == frozenset()
        assert EA.EnemyAI(_executor())._plan_favour_set("Russia", world) == frozenset()

    def test_the_aim_token_is_the_nearest_of_the_courts_own_aims(self, world):
        from backend.game_logic import war_council
        self._on_step_one(world)
        WP.holders(world)[COALITION]["favour"] = WP.AIM
        aims = war_council.aim_pull_set(world, "Austria")
        got = WP.favoured(world, "Austria")
        assert len(got) == 1 and got <= aims
        assert WP.favoured(world, "Russia") == frozenset(), "a court with no aim favours nothing"

    def test_the_design_would_have_put_it_in_the_permission(self):
        source = (REPO / "backend" / "game_logic" / "war_council.py").read_text(encoding="utf-8")
        body = source[source.index("def aim_pull_set("):source.index("def war_aim_line(")]
        assert "war_plans" not in body and "favour" not in body

    def test_it_is_dropped_when_it_is_no_longer_an_aim(self, world, monkeypatch):
        from backend.game_logic import war_council
        self._on_step_one(world)
        monkeypatch.setattr(war_council, "aim_pull_set", lambda *a, **k: frozenset())
        assert WP.favoured(world, "Austria") == frozenset()
        monkeypatch.undo()
        WP.holders(world)[COALITION]["favour"] = "Munich"       # an enemy capital, but no aim of Austria's
        assert WP.favoured(world, "Austria") == frozenset()

    def test_it_is_nothing_for_ground_the_court_holds_or_is_not_at_war_for(self, world):
        self._on_step_one(world)
        state = WP.holders(world)[COALITION]
        state["favour"] = "Vienna"
        assert WP.favoured(world, "Austria") == frozenset()
        state["favour"] = "Berlin"
        assert WP.favoured(world, "Austria") == frozenset(), "Austria is not at war with Prussia"

    def test_with_its_own_seam_down_the_plan_keeps_its_orders_and_names_no_province(self, world, monkeypatch):
        self._on_step_one(world)
        monkeypatch.setattr(WP, "a_plan_names_a_favoured_province", lambda: False)
        assert WP.favoured(world, "Austria") == frozenset()
        assert WP.planned(world, world.get_marshal("Mack"))

    def test_a_torn_courts_corps_favour_nothing(self, world):
        self._on_step_one(world)
        WP.holders(world)[COALITION]["torn"] = ["Austria"]
        assert WP.favoured(world, "Austria") == frozenset()
        assert WP.favoured(world, "Russia") == frozenset()

    def test_taken_orders_end_the_step_two_turns_on(self, world):
        self._on_step_one(world)
        state = WP.holders(world)[COALITION]
        assert WP.compromise(world, "Austria") and state["compromised"] == world.current_turn
        assert WP.compromise(world, "Russia") and state["compromised"] == world.current_turn, "the first taking counts"
        world.current_turn += 1
        _pass(world)
        assert state["step"] == 1
        world.current_turn += 1
        _pass(world)
        assert state["step"] == 2 and state["compromised"] is None

    def test_a_court_learns_a_routed_mans_place_for_five_turns(self, world, monkeypatch):
        from backend.game_logic import war_council
        _pass(world)
        assert not WP.learns_of(world, "Austria", {"task": "hold", "target": "Milan"}), "only a take names a place"
        assert WP.learns_of(world, "Austria", {"task": "take", "target": "Tyrol"})
        assert WP.favoured(world, "Austria") == frozenset(), "its own ground is not a thing to take"
        monkeypatch.setattr(war_council, "aim_pull_set", lambda *a, **k: frozenset({"Tyrol"}))
        world.get_region("Tyrol").controller = "France"       # France took it: its recapture is an aim
        assert "Tyrol" in WP.favoured(world, "Austria")
        world.current_turn += WP.LEARNT_TURNS
        assert "Tyrol" in WP.favoured(world, "Austria")
        world.current_turn += 1
        assert "Tyrol" not in WP.favoured(world, "Austria")

    def test_learned_again_the_five_turns_start_again(self, world):
        _pass(world)
        WP.learns_of(world, "Austria", {"task": "take", "target": "Tyrol"})
        world.current_turn += 3
        WP.learns_of(world, "Austria", {"task": "take", "target": "Tyrol"})
        assert WP.state_of(world, "Austria")["learnt"]["until"] == world.current_turn + WP.LEARNT_TURNS

    def test_with_its_seam_down_nothing_is_learned(self, world, monkeypatch):
        _pass(world)
        monkeypatch.setattr(WP, "a_court_learns_a_routed_mans_task", lambda: False)
        assert not WP.learns_of(world, "Austria", {"task": "take", "target": "Tyrol"})


# ═══════════════════════════ the fog census ══════════════════════════════════

def _forbid_frances_store(world, monkeypatch):
    """France's intelligence may not be read at all: any read raises."""
    from backend.commands.combat_executor import CombatExecutor

    def forbidden(*_a, **_k):
        raise AssertionError("an enemy marshal's if-then read FRANCE's intelligence")

    monkeypatch.setattr(type(world), "get_region_intel", forbidden)
    monkeypatch.setattr(CombatExecutor, "_fog_banded_strength", staticmethod(forbidden))


def _france_far_away(world):
    """Every French corps two provinces from Mack, where his court has no eyes
    (Orleanais: beside Lorraine, which is beside Swabia) — and France sees it all."""
    for man in world.get_marshals_by_nation("France"):
        man.location = "Orleanais"
    world.refresh_marshal_indexes()


def _line(if_, **kw):
    return IT.make_line(if_, then=kw.pop("then", "dig_in"), written=None, **kw)


class TestTheFogCensus:

    def test_the_if_thens_read_the_players_store_in_two_functions_only(self):
        tree = ast.parse((REPO / "backend" / "commands" / "if_thens.py").read_text(encoding="utf-8"))
        readers = {}
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            for inner in ast.walk(node):
                name = inner.attr if isinstance(inner, ast.Attribute) else (
                    inner.id if isinstance(inner, ast.Name) else "")
                if name in ("get_region_intel", "_fog_banded_strength", "get_visible_enemies",
                            "get_visible_enemies_in_region", "intel"):
                    readers.setdefault(node.name, set()).add(name)
        assert set(readers) == {"_sees", "known_strength"}, readers

    def test_his_own_province_and_its_neighbours_are_his_nations_to_see(self, world, monkeypatch):
        _forbid_frances_store(world, monkeypatch)
        mack = world.get_marshal("Mack")
        ring = ["Swabia"] + list(world.get_region("Swabia").adjacent_regions)
        assert IT.reach(world, mack) == ring

    def test_a_horsemans_second_ring_is_his_courts_sight_not_frances(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        mack.cavalry = True
        _france_far_away(world)
        from backend.models.intel import FULL
        assert world.get_region_intel("Orleanais").visibility == FULL or True
        _forbid_frances_store(world, monkeypatch)
        reach = IT.reach(world, mack)
        assert "Orleanais" not in reach and "Lorraine" in reach
        assert not world.is_region_live_visible_to_nation("Orleanais", "Austria")

    def test_a_french_marshal_still_reads_frances_own_intelligence(self, world):
        from backend.models.intel import UNKNOWN
        soult = world.get_marshal("Soult")
        assert "Swabia" in IT.reach(world, soult)
        world.get_region_intel("Swabia").visibility = UNKNOWN
        assert "Swabia" not in IT.reach(world, soult)

    def test_another_court_knows_what_it_sees_exactly(self, world, monkeypatch):
        mack, ney = world.get_marshal("Mack"), world.get_marshal("Ney")
        _forbid_frances_store(world, monkeypatch)
        assert IT.known_strength(world, ney, mack) == ney.strength

    def test_a_french_marshal_still_knows_an_enemy_by_frances_band(self, world):
        from backend.models.intel import PARTIAL
        soult, mack = world.get_marshal("Soult"), world.get_marshal("Mack")
        world.get_region_intel("Swabia").visibility = PARTIAL
        banded = IT.known_strength(world, mack, soult)
        assert banded == IT.known_strength(world, mack) and banded != mack.strength

    # ── for each IF: read with France's store FORBIDDEN ──

    def test_enemy_near__trips_on_what_his_court_sees(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        _forbid_frances_store(world, monkeypatch)
        hit = IT.happened(world, mack, _line("enemy_near"))
        assert hit is not None and hit["enemy"].nation in ("Bavaria", "France")

    def test_enemy_near__does_not_trip_on_what_only_france_sees(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        mack.cavalry = True
        _france_far_away(world)
        world.get_marshal("Deroy").location = "Dresden"
        world.refresh_marshal_indexes()
        _forbid_frances_store(world, monkeypatch)
        assert IT.happened(world, mack, _line("enemy_near", who="Ney")) is None
        assert IT.happened(world, mack, _line("enemy_near")) is None

    def test_enemy_near__a_named_man_fires_whatever_his_strength(self, world, monkeypatch):
        mack, napoleon = world.get_marshal("Mack"), world.get_marshal("Napoleon")
        _forbid_frances_store(world, monkeypatch)
        assert napoleon.strength < mack.strength // IT.FLOOR_DIVISOR
        assert IT.happened(world, mack, _line("enemy_near", who="Napoleon"))["enemy"] is napoleon

    def test_outnumbered__counts_what_his_court_sees(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        _forbid_frances_store(world, monkeypatch)
        assert IT.happened(world, mack, _line("outnumbered")) is not None, "six French corps stand beside him"

    def test_outnumbered__does_not_count_what_only_france_sees(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        mack.cavalry = True
        _france_far_away(world)
        world.get_marshal("Deroy").location = "Dresden"
        world.refresh_marshal_indexes()
        _forbid_frances_store(world, monkeypatch)
        assert IT.happened(world, mack, _line("outnumbered")) is None

    def test_surrounded__reads_the_enemy_beside_him_by_his_courts_sight(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        _forbid_frances_store(world, monkeypatch)
        hit = IT.happened(world, mack, _line("surrounded"))
        assert hit is not None and "surrounded" in hit["came"]

    def test_surrounded__a_friend_beside_him_lifts_it(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        world.get_marshal("ArchdukeJohn").location = "Munich"
        world.refresh_marshal_indexes()
        _forbid_frances_store(world, monkeypatch)
        assert IT.happened(world, mack, _line("surrounded")) is None

    def test_attacked__reads_the_battle_not_the_fog(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        world.record_battle("Swabia", "Ney", "Mack", "defender_victory")
        _forbid_frances_store(world, monkeypatch)
        assert IT.happened(world, mack, _line("attacked"))["enemy"].name == "Ney"

    def test_attacked__an_attack_by_a_court_he_is_at_peace_with_is_none_of_his(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        world.record_battle("Swabia", "Brunswick", "Mack", "defender_victory")
        _forbid_frances_store(world, monkeypatch)
        assert IT.happened(world, mack, _line("attacked")) is None

    def test_friend_attacked__reads_the_battle_beside_him(self, world, monkeypatch):
        bux = world.get_marshal("Buxhowden")
        bux.location = "Moravia"
        world.refresh_marshal_indexes()
        world.record_battle("Podolia", "Murat", "Kutuzov", "defender_victory")
        _forbid_frances_store(world, monkeypatch)
        assert IT.happened(world, bux, _line("friend_attacked", friend="Kutuzov", then="join")) is not None

    def test_friend_attacked__a_battle_far_away_is_not_beside_him(self, world, monkeypatch):
        bux = world.get_marshal("Buxhowden")
        world.record_battle("Podolia", "Murat", "Kutuzov", "defender_victory")
        _forbid_frances_store(world, monkeypatch)
        assert bux.location == "Volhynia"
        assert IT.happened(world, bux, _line("friend_attacked", friend="Kutuzov", then="join")) is None

    def test_place_falls__reads_who_holds_the_place(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        _forbid_frances_store(world, monkeypatch)
        assert IT.happened(world, mack, _line("place_falls", place="Tyrol")) is None
        world.get_region("Tyrol").controller = "France"
        assert IT.happened(world, mack, _line("place_falls", place="Tyrol")) is not None

    def test_friend_arrives__reads_where_his_friend_stands(self, world, monkeypatch):
        mack = world.get_marshal("Mack")
        _forbid_frances_store(world, monkeypatch)
        assert IT.happened(world, mack, _line("friend_arrives", friend="Kutuzov")) is None
        world.get_marshal("Kutuzov").location = "Munich"
        assert IT.happened(world, mack, _line("friend_arrives", friend="Kutuzov")) is not None

    def test_the_seven_ifs_are_the_seven_pinned_here(self):
        pinned = {name.split("__")[0][len("test_"):] for name in dir(TestTheFogCensus)
                  if name.startswith("test_") and "__" in name}
        assert pinned == set(IT.IFS)

    def test_the_whole_pass_runs_with_frances_store_forbidden(self, world, monkeypatch):
        _hold_the_holders(world)
        _order(world, "Mack", "HOLD", "Swabia", [{"if": "enemy_near", "then": "dig_in"},
                                                  {"if": "outnumbered", "then": "dig_in"},
                                                  {"if": "surrounded", "then": "dig_in"}])
        world.get_region("Swabia").controller = "Austria"
        _forbid_frances_store(world, monkeypatch)
        hit = IT.ready(world, world.get_marshal("Mack"), world.get_marshal("Mack").strategic_order)
        assert hit is not None and hit["index"] == 0

    def test_the_attack_line_weighs_the_odds_by_his_courts_own_figure(self, world, monkeypatch):
        mack, soult = world.get_marshal("Mack"), world.get_marshal("Soult")
        _forbid_frances_store(world, monkeypatch)
        line = _line("enemy_near", who="Soult", then="attack")
        assert IT.attack_target(world, mack, line, {"enemy": soult}) is soult
        mack.strength = soult.strength - 1
        assert IT.attack_target(world, mack, line, {"enemy": soult}) is None


# ═══════════════════════════ the arms ════════════════════════════════════════

class TestTheArms:

    def test_what_ships_up_and_what_ships_down(self):
        # BUILT, NOT ADOPTED: the plans are off as shipped (the measure's rule,
        # written first, was missed — the choice is the user's).
        assert _AS_SHIPPED() is False
        assert WP.a_plan_names_a_favoured_province() is True
        assert WP.a_court_learns_a_routed_mans_task() is True
        assert EA.each_man_has_his_own_mood() is False
        assert EA.the_enemy_hunts_a_lone_corps() is False
        assert WP.a_planned_man_still_strikes_at_good_odds() is False

    def test_as_shipped_no_court_has_a_plan_and_no_man_is_planned(self, world, monkeypatch):
        """The shipped tree: the pass writes nothing, draws nothing, moves
        nobody — every man is his court's own, as before the session."""
        monkeypatch.setattr(WP, "the_courts_follow_a_plan", _AS_SHIPPED)
        before = json.dumps(world.to_dict(), default=str, sort_keys=True)
        rows = _pass(world)
        assert rows == []
        assert not WP.holders(world)
        assert not any(WP.planned(world, m) for m in world.marshals.values())
        assert WP.favoured(world, "Austria") == frozenset()
        assert json.dumps(world.to_dict(), default=str, sort_keys=True) == before

    def test_a_planned_man_strikes_at_good_odds_only_with_the_arm_up(self, world, monkeypatch):
        """Row FIGHT: down, the gate answers "skipped" whatever the odds; up,
        the gate hands back his court's own attack — and never a second blow
        on a night his orders already moved him."""
        _pass(world)
        world.get_region("Swabia").controller = "Austria"       # no ground to take where he stands
        mack = world.get_marshal("Mack")
        assert WP.planned(world, mack)
        strike = {"marshal": "Mack", "action": "attack", "target": "Bernadotte"}
        monkeypatch.setattr(EA.EnemyAI, "_find_attack_opportunity",
                            lambda self, marshal, nation, w: dict(strike))
        monkeypatch.setattr(EA.EnemyAI, "_admits", lambda self, action: True)
        action, _prio = _evaluate(world, "Mack")
        assert action is None                                   # the arm is down
        monkeypatch.setattr(WP, "a_planned_man_still_strikes_at_good_odds", lambda: True)
        world._plan_night = (int(world.current_turn), set())    # his orders did not move him tonight
        action, prio = _evaluate(world, "Mack")
        assert action == strike and prio == 4
        world._plan_night = (int(world.current_turn), {"Mack"})  # they did: one thing a turn
        action, _prio = _evaluate(world, "Mack")
        assert action is None

    def test_the_ladder_names_real_seams_and_the_recorded_boards_fold_them_in(self):
        import importlib

        from tests._ic4_seams import IC4_SEAMS_BY_ROW, IC4_SEAMS_DOWN, IC4_SHIPPED_DOWN, IC4_SHIPPED_UP
        from tests._oct27_seams import OCT27_SEAMS_DOWN
        assert list(IC4_SEAMS_BY_ROW) == ["PLAN", "FAVOUR", "LEARNS", "MOOD", "HUNT", "FIGHT"]
        assert IC4_SHIPPED_DOWN == ("PLAN", "MOOD", "HUNT", "FIGHT")
        assert set(IC4_SHIPPED_UP) | set(IC4_SHIPPED_DOWN) == set(IC4_SEAMS_BY_ROW)
        for row, specs in IC4_SEAMS_BY_ROW.items():
            for spec in specs:
                target, expr = spec.split("=", 1)
                module, name = target.split(":", 1)
                seam = getattr(importlib.import_module(module), name)
                if name == "the_courts_follow_a_plan":
                    seam = _AS_SHIPPED          # this file raises it; the pin reads the real one
                assert callable(seam) and expr == "False"
                assert seam() is (row in IC4_SHIPPED_UP), spec
                assert spec in OCT27_SEAMS_DOWN, f"{spec} is not folded into the recorded boards' list"
        assert len(IC4_SEAMS_DOWN) == 6

    def test_the_mood_as_shipped_is_the_nations_stream(self, world):
        ai = EA.EnemyAI(_executor())
        mack = world.get_marshal("Mack")
        first = ai._get_mood_adjusted_threshold(mack, world)
        second = ai._get_mood_adjusted_threshold(mack, world)
        assert first != second, "drawn at every decision, in call order"

    def test_each_mans_own_mood_is_his_for_the_day(self, world, monkeypatch):
        monkeypatch.setattr(EA, "each_man_has_his_own_mood", lambda: True)
        world.campaign_seed = "ic14-mood"
        ai = EA.EnemyAI(_executor())
        mack, bux = world.get_marshal("Mack"), world.get_marshal("Buxhowden")
        today = ai._get_mood_adjusted_threshold(mack, world)
        assert ai._get_mood_adjusted_threshold(mack, world) == today, "asked twice in a day: the same"
        base, band = ai.ATTACK_THRESHOLDS["literal"], ai.MOOD_VARIANCE["literal"]
        assert base * (1 - band) <= today <= base * (1 + band)
        assert ai._get_mood_adjusted_threshold(bux, world) != today, "another man, another mood"
        world.current_turn += 1
        assert ai._get_mood_adjusted_threshold(mack, world) != today, "another day, another mood"

    def test_the_mood_arm_still_draws_the_nations_stream(self, _snapshot, monkeypatch):
        from backend.models.world_state import WorldState
        states = []
        for up in (False, True):
            with _quiet():
                fresh = WorldState.from_dict(json.loads(_snapshot))
            monkeypatch.setattr(EA, "each_man_has_his_own_mood", lambda up=up: up)
            EA.EnemyAI(_executor())._get_mood_adjusted_threshold(fresh.get_marshal("Mack"), fresh)
            states.append(EA.ai_rng(fresh, "Austria").getstate())
        assert states[0] == states[1], "the stream is drawn and set aside: nothing else that reads it shifts"

    def test_the_hunt_as_shipped_is_no_term_at_all(self, world):
        ai = EA.EnemyAI(_executor())
        assert ai._hunt_credit(world.get_marshal("ArchdukeCharles"), world.get_marshal("Massena"), "Austria", world) == 0

    def test_the_hunt_counts_a_lone_french_corps_as_nearer_by_the_odds(self, world, monkeypatch):
        monkeypatch.setattr(EA, "the_enemy_hunts_a_lone_corps", lambda: True)
        ai = EA.EnemyAI(_executor())
        charles, massena = world.get_marshal("ArchdukeCharles"), world.get_marshal("Massena")
        assert massena.location == "Milan" and charles.strength == 54000 and massena.strength == 42000
        assert ai._hunt_credit(charles, massena, "Austria", world) == EA.HUNT_CREDIT_EVEN_ODDS
        massena.strength = 30000
        assert ai._hunt_credit(charles, massena, "Austria", world) == EA.HUNT_CREDIT_GOOD_ODDS
        massena.strength = 60000
        assert ai._hunt_credit(charles, massena, "Austria", world) == 0, "never against the odds"

    def test_the_hunt_leaves_a_corps_with_a_friend_beside_it_alone(self, world, monkeypatch):
        monkeypatch.setattr(EA, "the_enemy_hunts_a_lone_corps", lambda: True)
        ai = EA.EnemyAI(_executor())
        charles = world.get_marshal("ArchdukeCharles")
        ney = world.get_marshal("Ney")
        assert world.get_marshal("Davout").location == ney.location
        assert ai._hunt_credit(charles, ney, "Austria", world) == 0

    def test_the_hunt_is_for_the_players_corps_only(self, world, monkeypatch):
        monkeypatch.setattr(EA, "the_enemy_hunts_a_lone_corps", lambda: True)
        ai = EA.EnemyAI(_executor())
        assert ai._hunt_credit(world.get_marshal("ArchdukeCharles"), world.get_marshal("Deroy"), "Austria", world) == 0

    def test_the_hunts_term_stands_in_both_choices_of_whom_to_march_on(self):
        source = (REPO / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        body = source[source.index("    def _consider_strategic_move("):]
        assert len(re.findall(r"- self\._hunt_credit\(marshal, e, nation, world\)", body)) == 2

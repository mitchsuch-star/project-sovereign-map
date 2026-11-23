"""Row IC, Session 3 — IC-10, A MARSHAL ON HIS OWN (November 21, 2026).

The design is `docs/INDEPENDENT_COMMAND_SPEC.md` (§6, §8.6, §12, §13); the rules
`docs/SYSTEMS_REFERENCE.md` §233; the module `backend/game_logic/own_order.py`.

The user's direction for the session, verbatim: "make sure when you give
genmrals autonomy they really do stuff and iunteract withe achother and even
help their friends your strategoic suggestions are just guidance for ai" — and
for the typing: "make this engaging make the typing really fun".

What is pinned here:
  * who can be set on his own, the count and its laws, the price and the
    free stand-down (with the refund the turn it was given);
  * the typed road — "on your own", the how-bold words, the changes, the
    questions answered free in his own voice — and the read-back that says it
    all BEFORE anything is spent;
  * the ONE pure reading (no write, no die) and "Tonight is true" (R-TRUE):
    what the screen said, or he stays put and says why;
  * one thing a turn; the exemptions (no jealous strike, no cannon-fire
    redirect); R-FRIENDS at the reinforcement seam; R-TOGETHER's "never two
    attacks on one enemy";
  * the life table, the saves, the laws' data, the desk.
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
from backend.commands import parse_preview as PP
from backend.commands.parser import CommandParser
from backend.game_logic import own_order as O
from backend.game_logic import reforms as R
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


def _fresh(world1805) -> WorldState:
    with _quiet():
        return WorldState.from_dict(world1805.to_dict())


@pytest.fixture(scope="module")
def road():
    """The shipped 1805 board behind the real app and the mock parser (the
    pattern of `tests/test_ic8_the_line.py`)."""
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


def _board(snap, tweak=None) -> WorldState:
    with _quiet():
        world = WorldState.from_dict(json.loads(snap))
        if tweak is not None:
            tweak(world)
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    return world


def _post(client, line, **body):
    random.seed(1805)
    with _quiet():
        return client.post("/command", json={"command": line, "typed": True, **body}).json()


def _preview(client, line):
    PP.invalidate()
    with _quiet():
        return client.get("/parse_preview", params={"line": line}).json()


def _roles(reading, role):
    return [str(p.get("text") or "") for p in (reading.get("parts") or []) if p.get("role") == role]


def _give(world, name, task, target, **kw):
    marshal = world.marshals[name]
    spec, why = O.spec_from(world, marshal, task, target, **kw)
    assert spec is not None, why
    with _quiet():
        result = O.give(world, marshal, spec, line=f"{name}, {task} {target} on your own.",
                        own_proposal=True)
    assert result["success"], result
    return marshal


# ═══════════════════════ who, the count, the laws (§6.2, §6.4) ═══════════════

class TestWhoCanBeSet:

    def test_a_bold_or_careful_man_at_trust_30_can(self, world1805):
        world = _fresh(world1805)
        for name in ("Ney", "Davout", "Murat", "Lannes", "Massena"):
            assert O.why_not(world, world.marshals[name], "hold") == "", name

    def test_a_literal_man_the_emperor_and_a_low_trust_man_cannot(self, world1805):
        world = _fresh(world1805)
        assert "to the letter" in O.why_not(world, world.marshals["Soult"], "hold")
        assert "commands himself" in O.why_not(world, world.marshals["Napoleon"], "hold")
        ney = world.marshals["Ney"]
        ney.trust.set(29)
        assert "needs 30" in O.why_not(world, ney, "hold")

    def test_a_man_on_his_task_to_prove_himself_cannot(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        ney.trial = {"turns_left": 2}
        assert "prove himself" in O.why_not(world, ney, "hold")

    def test_guns_hold_or_support_only(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        ney.artillery = True
        assert "guns" in O.why_not(world, ney, "take")
        assert O.why_not(world, ney, "hold") == ""


class TestTheCount:

    def test_one_at_the_start(self, world1805):
        world = _fresh(world1805)
        assert O.allowed(world) == 1
        assert O.count_words(world) == "On their own: 0 of the 1 you may have"

    def test_the_staff_raises_it_and_the_aides_need_the_staff(self, world1805):
        world = _fresh(world1805)
        aides = R.find_law(world, "France", "aides_de_camp")
        staff = R.find_law(world, "France", "grand_quartier_general")
        assert aides is not None and staff is not None
        aides["enacted_turn"] = 1
        assert O.allowed(world) == 1, "the Aides count only while the Staff stands"
        assert "needs" in R.law_refusal(world, "France", "aides_de_camp") or \
            R.requires_law_refusal(world, "France", aides)
        staff["enacted_turn"] = 1
        assert O.allowed(world) == 3
        aides.pop("enacted_turn")
        assert O.allowed(world) == 2

    def test_the_aides_cannot_be_enacted_before_the_staff(self, world1805):
        world = _fresh(world1805)
        assert R.law_refusal(world, "France", "aides_de_camp").endswith("in force first.")

    def test_the_count_full_refuses_a_second_man(self, world1805):
        world = _fresh(world1805)
        _give(world, "Ney", "hold", "Rhineland")
        why = O.why_not(world, world.marshals["Davout"], "hold")
        assert "count is full" in why and "exact order" in why
        assert O.why_not(world, world.marshals["Ney"], "take", replacing=True) == ""

    def test_a_lapsed_law_ends_the_lowest_ranked_order_and_costs_no_trust(self, world1805):
        world = _fresh(world1805)
        R.find_law(world, "France", "grand_quartier_general")["enacted_turn"] = 1
        _give(world, "Ney", "hold", "Rhineland")
        _give(world, "Davout", "hold", "Rhineland")
        trust = {n: int(world.marshals[n].trust.value) for n in ("Ney", "Davout")}
        R.find_law(world, "France", "grand_quartier_general").pop("enacted_turn")
        rows = []
        O._the_count_holds(world, rows)
        assert len(rows) == 1 and O.count(world) == 1
        assert {n: int(world.marshals[n].trust.value) for n in ("Ney", "Davout")} == trust


# ═══════════════════════ the typed road (§8.2, §8.6) ═════════════════════════

class TestGivingIt:

    def test_on_your_own_gives_a_take_for_two_actions(self, road):
        client, snap = road
        world = _board(snap)
        before = int(world.actions_remaining)
        out = _post(client, "Ney, take Swabia on your own")
        assert out["success"], out
        assert int(M.world.actions_remaining) == before - 2
        ney = M.world.marshals["Ney"]
        assert O.on_his_own(ney) and O.own(ney)["task"] == "take" and O.own(ney)["target"] == "Swabia"
        assert "starts tomorrow night" in out["message"] and "On their own: 1 of the 1 you may have" in out["message"]

    def test_a_support_costs_one_action(self, road):
        client, snap = road
        world = _board(snap)
        before = int(world.actions_remaining)
        out = _post(client, "Lannes, support Ney on your own")
        assert out["success"], out
        assert int(M.world.actions_remaining) == before - 1

    def test_a_how_bold_word_on_a_standing_task_sets_him_on_his_own(self, road):
        client, snap = road
        _board(snap)
        out = _post(client, "Davout, hold Rhineland carefully")
        assert out["success"], out
        davout = M.world.marshals["Davout"]
        assert O.on_his_own(davout) and int(O.own(davout)["risk"]) == -1

    def test_stand_down_the_same_turn_gives_every_action_back(self, road):
        client, snap = road
        world = _board(snap)
        before = int(world.actions_remaining)
        assert _post(client, "Ney, take Swabia on your own")["success"]
        assert _post(client, "Ney, more risk")["success"]
        assert int(M.world.actions_remaining) == before - 3
        out = _post(client, "Ney, stand down")
        assert out["success"], out
        assert int(M.world.actions_remaining) == before
        assert not O.on_his_own(M.world.marshals["Ney"])

    def test_the_cancel_button_stands_him_down_free(self, road):
        client, snap = road
        world = _board(snap)
        assert _post(client, "Ney, hold Rhineland on your own")["success"]
        left = int(M.world.actions_remaining)
        with _quiet():
            out = client.post("/cancel_order", json={"marshal": "Ney"}).json()
        assert out.get("success"), out
        assert int(M.world.actions_remaining) == left + 2
        assert world is not None

    def test_recalled_mid_task_he_loses_three_trust(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        O.own(ney)["given"] = int(world.current_turn) - 2
        O.own(ney)["acted"] = int(world.current_turn) - 1
        trust = int(ney.trust.value)
        out = O.stand_down(world, ney)
        assert out["success"] and int(ney.trust.value) == trust - O.STAND_DOWN_TRUST
        assert "loses 3 trust" in out["message"]

    def test_a_literal_man_is_told_why_and_offered_the_exact_order(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Soult, hold Lorraine on your own")
        assert reading["kind"] == "refusal" and "to the letter" in reading["refusal"]
        assert reading["candidates"] == [{"label": "Give it as an exact order",
                                          "line": "Soult, hold Lorraine"}]
        out = _post(client, "Soult, hold Lorraine on your own")
        assert not out.get("success")

    def test_carry_on_answers_his_ask_free(self, road):
        client, snap = road
        _board(snap)
        assert _post(client, "Ney, hold Rhineland on your own")["success"]
        ney = M.world.marshals["Ney"]
        O.ask_why(M.world, ney, "his road has been barred")
        left = int(M.world.actions_remaining)
        out = _post(client, "Ney, carry on")
        assert out["success"], out
        assert O.own(ney)["state"] == "work" and int(M.world.actions_remaining) == left


class TestTheReadBack:

    def test_it_says_the_count_his_odds_tomorrow_night_and_his_answer(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Ney, take Swabia on your own")
        assert reading["kind"] == "order" and reading["ok"] and reading["ap"] == 2
        taken = _roles(reading, "taken")
        assert "on his own — once given, 1 of the 1 you may have (laws raise it)" in taken
        assert any(t.startswith("he attacks only when the odds are our ") for t in taken)
        (night,) = [t for t in _roles(reading, "tonight") if t.startswith("His first night (tomorrow)")]
        assert "Ney" in night
        assert _roles(reading, "answer"), reading

    def test_boldly_moves_his_figure_one_step_and_his_answer_changes(self, road):
        client, snap = road
        _board(snap)
        plain = _preview(client, "Davout, hold Rhineland on your own")
        bold = _preview(client, "Davout, hold Rhineland on your own, boldly")
        careful = _preview(client, "Davout, hold Rhineland on your own, carefully")
        assert "our 10 to their 10 or better" in " ".join(_roles(plain, "taken"))
        assert "our 9 to their 10 or better (his own 10, one step bolder from you)" in " ".join(_roles(bold, "taken"))
        assert "our 11 to their 10 or better (his own 10, one step more careful from you)" in " ".join(
            _roles(careful, "taken"))
        assert _roles(bold, "answer") != _roles(careful, "answer")

    def test_the_chips_write_bolder_and_more_careful_into_the_sentence(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Murat, chase Mack on your own")
        lines = [c["line"] for c in reading.get("candidates") or []]
        assert "Murat, chase Mack on your own, boldly." in lines
        assert "Murat, chase Mack on your own, carefully." in lines

    def test_nothing_is_spent_by_reading(self, road):
        client, snap = road
        world = _board(snap)
        before = json.dumps(world.to_dict(), sort_keys=True, default=str)
        _preview(client, "Ney, take Swabia on your own, boldly")
        _preview(client, "Ney, what will you do?")
        assert json.dumps(M.world.to_dict(), sort_keys=True, default=str) == before


class TestTheQuestions:

    @pytest.mark.parametrize("line", ["Ney, what will you do?", "Davout, what do you see?",
                                      "Ney, can you take Swabia?", "Ney, why did you stay put?"])
    def test_asked_free_and_answered_in_his_voice(self, road, line):
        client, snap = road
        world = _board(snap)
        before = json.dumps(world.to_dict(), sort_keys=True, default=str)
        reading = _preview(client, line)
        assert reading["kind"] == "question" and reading["parts"][0]["text"].startswith("A question for ")
        out = _post(client, line)
        shown = line.split(",")[0]
        assert out["success"] and str(out.get("message") or "").startswith(f'{shown}: "'), out
        assert int(M.world.actions_remaining) == int(world.actions_remaining)
        after = json.loads(json.dumps(M.world.to_dict(), sort_keys=True, default=str))
        mine = json.loads(before)
        for key in ("marshals", "regions", "actions_remaining"):
            assert after[key] == mine[key], key

    def test_a_man_not_on_his_own_says_what_he_would_do(self, road):
        client, snap = road
        _board(snap)
        out = _post(client, "Ney, what will you do?")
        assert out["message"].startswith('Ney: "Set me on my own, Sire, and I would '), out


# ═══════════════════════ the reading, the pass (§6.5, D6–D8) ═════════════════

def _five_on_their_own(world, monkeypatch):
    monkeypatch.setattr(O, "COUNT_AT_START", 5)
    for name in ("Ney", "Davout", "Murat", "Massena", "Lannes"):
        marshal = world.marshals[name]
        prop = O.proposal(world, marshal)
        _give(world, name, prop["task"], prop["target"])
    for name in ("Ney", "Davout", "Murat", "Massena", "Lannes"):
        O.own(world.marshals[name])["given"] = int(world.current_turn) - 1
        O.own(world.marshals[name])["late"] = False


class TestThePureReading:

    def test_the_night_writes_nothing_and_draws_no_die(self, world1805, monkeypatch):
        world = _fresh(world1805)
        _five_on_their_own(world, monkeypatch)
        before = json.dumps(world.to_dict(), sort_keys=True, default=str)
        random.seed(42)
        expected = random.random()
        random.seed(42)
        with _quiet():
            rows = O.tonight(world)
            for man in O.men(world):
                O.answer(world, man, "night")
                O.answer(world, man, "sight")
                O.proposal(world, man)
        assert random.random() == expected, "the reading drew from the global random stream"
        assert json.dumps(world.to_dict(), sort_keys=True, default=str) == before
        assert len(rows) == 5

    def test_rank_order_and_one_attack_per_enemy(self, world1805, monkeypatch):
        world = _fresh(world1805)
        _five_on_their_own(world, monkeypatch)
        with _quiet():
            rows = O.tonight(world)
        seats = O._seats(world)
        assert [r["marshal"] for r in rows] == sorted(
            [r["marshal"] for r in rows], key=lambda n: (seats.get(n, 99), n))
        attacked = [r["target"] for r in rows if r["act"] in ("attack", "strike")]
        assert len(attacked) == len(set(attacked)), rows


class TestTonightIsTrue:
    """R-TRUE: every act a man on his own made was what "Tonight" said — or he
    stayed put and said why (a join whose lead fought is its own act)."""

    def test_six_nights_on_the_1805_board(self, road, monkeypatch):
        client, snap = road
        world = _board(snap)
        _five_on_their_own(world, monkeypatch)
        mismatches, acts = [], 0
        for night in range(6):
            with _quiet():
                said = {r["marshal"]: r for r in O.tonight(M.world)}
            out = _post(client, "end turn")
            for row in out.get("strategic_reports") or []:
                if not row.get("own"):
                    continue
                plan = said.get(row["marshal"])
                if plan is None:
                    continue
                acts += 1
                if row["act"] == "stay" or (row["act"] == "join" and plan["act"] in ("join", "move_up")):
                    continue
                if row.get("said") and row["said"] != plan["line"]:
                    mismatches.append((night, row["marshal"], plan["line"], row["message"]))
        assert acts >= 20
        assert not mismatches, mismatches


class TestOneThingATurn:

    def test_his_if_thens_sleep_on_a_night_he_acted(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        assert not O.acted_tonight(ney, world)
        O.own(ney)["acted"] = int(world.current_turn)
        assert O.acted_tonight(ney, world)

    def test_the_given_night_he_makes_ready(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        with _quiet():
            (reading,) = O.tonight(world)
        assert reading["act"] == "start" and "makes ready — a task starts the night after it is given" in reading["line"] and reading["ahead"]


class TestTheExemptions:

    def test_no_jealous_strike_and_no_cannon_fire_redirect(self, world1805):
        from backend.commands.strategic import aggressive_interrupt_applies
        from backend.game_logic import jealousy as J
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        assert J.on_his_task(ney)
        assert not aggressive_interrupt_applies(world, ney)

    def test_the_strategic_pass_never_walks_his_order(self, world1805):
        import inspect

        from backend.commands import strategic as S
        source = inspect.getsource(S.StrategicOrderProcessor.process_strategic_orders)
        assert 'if getattr(order, "own", None) is not None:' in source


class TestRFriends:
    """R-FRIENDS: every man on his own answers a friend's battle next to him —
    dug in or on his hold's post — never a man he hates."""

    def _set(self, world, name, place):
        world.marshals[name].location = place

    @pytest.mark.parametrize("name", ["Ney", "Davout", "Massena"])
    def test_every_nature_answers_dug_in_on_his_post(self, world1805, name):
        from backend.commands.executor import CommandExecutor
        world = _fresh(world1805)
        man = _give(world, name, "hold", world.marshals[name].location)
        man.fortified = True
        friend = world.marshals["Soult"]
        region = world.get_region(man.location)
        friend.location = [n for n in region.adjacent_regions if n != man.location][0]
        combat = CommandExecutor()._combat
        assert combat._is_reinforcement_eligible(
            man, friend, friend.location, "France", world,
            written_join=O.answers_the_guns(man))
        ok, why = combat._muster_reason(man, friend, friend.location, "France", world)
        assert why not in ("fortified_static", "holding_position"), why

    def test_never_a_man_he_hates(self, world1805):
        from backend.commands.executor import CommandExecutor
        world = _fresh(world1805)
        man = _give(world, "Ney", "hold", world.marshals["Ney"].location)
        friend = world.marshals["Soult"]
        friend.location = [n for n in world.get_region(man.location).adjacent_regions
                           if n != man.location][0]
        man.relationships["Soult"] = -2
        combat = CommandExecutor()._combat
        assert not combat._is_reinforcement_eligible(
            man, friend, friend.location, "France", world,
            written_join=O.answers_the_guns(man))


# ═══════════════════════ the life table (§6.8) ═══════════════════════════════

class TestTheLifeTable:

    def test_an_unanswered_ask_ends_the_order_after_three_turns_no_trust_lost(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        O.ask_why(world, ney, "his road has been barred")
        # (the review, IC3-V: the ask stands three of YOUR turns — raised at
        # night T, seen on T+1, T+2 and T+3, ended at the close of T+3)
        O.own(ney)["asks"]["since"] = int(world.current_turn) - 2
        assert O._life(world, ney) is None and O.on_his_own(ney)
        O.own(ney)["asks"]["since"] = int(world.current_turn) - 3
        trust = int(ney.trust.value)
        row = O._life(world, ney)
        assert row is not None and not O.on_his_own(ney) and int(ney.trust.value) == trust

    def test_his_trust_under_30_makes_him_ask(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        ney.trust.set(25)
        O._life(world, ney)
        assert O.own(ney)["state"] == "asks" and "25" in O.own(ney)["asks"]["why"]

    def test_a_pursuit_ends_when_the_quarry_is_gone(self, world1805):
        world = _fresh(world1805)
        murat = _give(world, "Murat", "pursue", "Mack")
        world.marshals["Mack"].strength = 0
        row = O._life(world, murat)
        assert row is not None and not O.on_his_own(murat) and "done" in row["message"]

    def test_a_take_done_becomes_a_hold(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "take", "Swabia")
        ney.location = "Swabia"
        world.marshals["Mack"].location = "Bohemia"
        world.get_region("Swabia").controller = "France"
        O._life(world, ney)
        assert O.own(ney)["task"] == "hold" and ney.strategic_order.command_type == "HOLD"

    def test_his_record_reads_a_win_then_quiet_nights(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        O._life(world, ney)
        ney.battles_won += 1
        O._life(world, ney)
        assert O.record(ney)["last"] == "won" and O.record(ney)["quiet"] == 0
        O._life(world, ney)
        assert O.record(ney)["quiet"] == 1


# ═══════════════════════ saves, data, the desk ═══════════════════════════════

class TestSaves:

    def test_the_order_and_his_record_round_trip(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "take", "Swabia")
        ney.own_record = {"acts": [["look", "Swabia", 1]], "quiet": 2, "last": "won"}
        with _quiet():
            back = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        again = back.marshals["Ney"]
        assert O.own(again) == O.own(ney)
        assert again.own_record["quiet"] == 2 and again.own_odds == 6

    def test_a_man_with_no_task_saves_no_key(self, world1805):
        world = _fresh(world1805)
        row = world.marshals["Soult"].to_dict()
        assert "own_record" not in row and "own_odds" not in row
        from backend.models.marshal import StrategicOrder
        order = StrategicOrder(command_type="HOLD", target="Lorraine", target_type="region",
                               started_turn=1, original_command="")
        assert "own" not in order.to_dict()


class TestTheData:

    def test_the_six_men_carry_their_authored_odds(self, world1805):
        want = {"Murat": 5, "Ney": 6, "Lannes": 7, "Massena": 8, "Davout": 10, "Bernadotte": 14}
        assert {n: O.his_odds(world1805.marshals[n]) for n in want} == want
        assert O.his_odds(world1805.marshals["Soult"]) == 10      # literal: by nature's fall-back

    def test_the_validator_clamps_the_odds_and_checks_requires_law(self):
        from backend.modding.validator import validate_scenario
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        data["marshals"]["Ney"]["own_odds"] = 25
        data["reforms"]["France"][-1]["requires_law"] = "no_such_law"
        result = validate_scenario(data, check_adjacency=False)
        said = " ".join(e.message for e in result.errors)
        assert "own_odds must be an integer from 3 to 20" in said
        assert "requires_law 'no_such_law' is not a law of France's deck" in said

    def test_the_staff_carries_the_count(self, world1805):
        staff = R.find_law(world1805, "France", "grand_quartier_general")
        assert {"type": "on_their_own", "value": 1} in staff["effects"]
        assert "on_their_own" in R.WIRED_EFFECT_TYPES


class TestTheDesk:

    def test_the_desk_says_the_count_and_each_night(self, world1805):
        from backend.game_logic import today
        world = _fresh(world1805)
        built = today.desk(world)
        assert "own" not in built, "an unused feature changes no payload"
        _give(world, "Ney", "hold", "Rhineland")
        built = today.desk(world)
        assert built["own"]["n"] == 1 and built["own"]["tonight"][0]["line"].startswith("Tonight: Ney")

    def test_a_man_who_asks_comes_first(self, world1805):
        from backend.game_logic import today
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        O.ask_why(world, ney, "his road has been barred")
        rows = today.decide(world)
        own_rows = [r for r in rows if r["id"] == "own_asks:Ney"]
        assert own_rows and own_rows[0]["tier"] == today.TIER_BITES

    def test_the_jealous_row_offers_to_set_him_on_his_own(self, world1805):
        from backend.game_logic import today
        world = _fresh(world1805)
        world.marshals["Ney"].jealousy_autonomous_warned = True
        (row,) = [r for r in today.decide(world) if r["id"] == "strike:Ney"]
        labels = [d["label"] for d in row["doors"]]
        assert labels == ["Give him an order", "Set him on his own"]
        line = row["doors"][1]["door"]["line"]
        assert row["doors"][1]["door"]["kind"] == "line" and line.endswith("on your own.")


# ═══════════════════════ the head of the session: three small finds ══════════

CLIENT = REPO / "godot-client" / "project-sovereign"


class TestTheHeadsThreeFinds:
    """IC3-H1, H2, H3 (`docs/BUG_FIXES.md` §"Row IC, Session 3")."""

    def test_h1_a_slow_list_opens_where_its_reading_card_stood(self):
        card = (CLIENT / "scripts" / "order_confirm_card.gd").read_text(encoding="utf-8")
        assert "var _dir_anchor := Vector2(-1.0, -1.0)" in card
        assert 'var was_reading := visible and _mode == "directive" and bool(_dir.get("reading", false))' in card
        assert "elif bool(_dir.get(\"reading\", false)):\n\t\t\t_dir_anchor = pick" in card
        assert card.count("_dir_anchor = Vector2(-1.0, -1.0)") >= 3     # cleared on every other opening and close

    def test_h2_the_stopwatch_starts_before_the_hand_over(self):
        harness = (REPO / "tools" / "readback_harness.gd").read_text(encoding="utf-8")
        for typed in ('"Ney, attack Mack"', '"Nye, attack Mack"'):
            at = harness.index(f"_input.text = {typed}")
            stamp = harness.index("_typed_at = Time.get_ticks_msec()", at)
            hand = harness.index('_main.call("_on_command_text_changed", _input.text)', at)
            assert stamp < hand, typed

    def test_h3_the_trust_tile_says_it_is_trust(self):
        page = (CLIENT / "scripts" / "marshal_management.gd").read_text(encoding="utf-8")
        assert '"caption": "Trust: " + str(m.get("trust_label", "Neutral")).to_lower()' in page


class TestThePetitionsButton:
    """§6.9: "Give him a front" writes his own proposal on the line — or says
    plainly why he cannot be set."""

    def test_give_him_a_front_writes_his_proposal(self, world1805):
        from backend.game_logic import jealousy as J
        world = _fresh(world1805)
        out = J._apply_shadow_choice(world, "detach", {"marshal": "Ney"})
        assert out["success"] and out["write_line"].endswith("on your own.")
        assert "press Enter to set him on his own" in out["message"]

    def test_one_who_cannot_be_set_hears_why(self, world1805):
        from backend.game_logic import jealousy as J
        world = _fresh(world1805)
        world.marshals["Ney"].trust.set(25)
        out = J._apply_shadow_choice(world, "detach", {"marshal": "Ney"})
        assert "write_line" not in out and "cannot be set on his own now" in out["message"]


class TestTheReviewsRowsOnTheLine:
    """The one review's rows on the typed road (`BUG_FIXES.md` §"Row IC, Session 3")."""

    def test_an_exact_hold_of_two_provinces_keeps_its_words(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Soult, hold Lorraine and Champagne")
        assert "on his own" not in " ".join(_roles(reading, "head"))
        assert reading.get("kind") != "order" or "Champagne" in json.dumps(reading)

    def test_a_polite_can_you_hold_stays_an_order(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Ney, can you hold the line?")
        assert not str(reading["parts"][0]["text"]).startswith("A question for Ney")

    def test_on_your_own_ground_is_a_place_not_a_mark(self, world1805):
        from backend.ai.own_words import set_aside_marks
        assert set_aside_marks("Ney, hold Alsace on your own ground")[1] == []
        assert set_aside_marks("Ney, hold Alsace on your own")[1] == ["on your own"]

    def test_withdraw_keeps_meaning_a_retreat(self, world1805):
        from backend.ai.own_words import read_line
        assert read_line("Ney, withdraw", ["Ney"], ["Rhineland"], ["Ney"]) is None
        assert read_line("Ney, stand down", ["Ney"], ["Rhineland"], ["Ney"])["own"]["kind"] == "stand_down"

    def test_a_typed_cancel_stands_him_down_free_at_no_actions(self, road):
        client, snap = road
        _board(snap)
        assert _post(client, "Ney, hold Rhineland on your own")["success"]
        M.world.actions_remaining = 0
        out = _post(client, "Ney, cancel")
        assert out["success"], out
        assert not O.on_his_own(M.world.marshals["Ney"])

    def test_the_free_words_put_no_if_then_to_sleep(self, road):
        client, snap = road
        _board(snap)
        assert _post(client, "Ney, hold Rhineland on your own")["success"]
        ney = M.world.marshals["Ney"]
        ney.last_ordered_turn = -1
        O.ask_why(M.world, ney, "his road has been barred")
        assert _post(client, "Ney, carry on")["success"]
        assert int(ney.last_ordered_turn if ney.last_ordered_turn is not None else -1) != int(M.world.current_turn)


class TestTheReviewsRowsOnTheNight:
    """The review's rows on the night pass and the life table (`BUG_FIXES.md`
    §"Row IC, Session 3", IC3-V)."""

    def test_a_hand_order_leaves_his_task_standing(self, road):
        client, snap = road
        _board(snap)
        assert _post(client, "Ney, hold Rhineland on your own")["success"]
        ney = M.world.marshals["Ney"]
        O.own(ney)["given"] = int(M.world.current_turn) - 1
        out = _post(client, "Ney, fortify")
        assert out.get("success"), out
        assert O.on_his_own(ney), "today's order is an ordinary order — his task stands (§6.3)"

    def test_the_night_after_a_hand_order_he_stays_and_says_why(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        O.own(ney)["given"] = int(world.current_turn) - 1
        ney.last_ordered_turn = int(world.current_turn)
        reading = O.read(world, ney)
        assert reading["act"] == "stay" and "your order today" in reading["line"]

    def test_a_night_already_done_is_not_done_twice(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        O.own(ney)["given"] = int(world.current_turn) - 1
        O.own(ney)["acted"] = int(world.current_turn)
        assert O.read(world, ney)["act"] == "stay"

    def test_a_friends_battle_today_was_his_one_thing(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        O.own(ney)["given"] = int(world.current_turn) - 1
        ney.reinforced_this_turn = True
        reading = O.read(world, ney)
        assert reading["act"] == "stay" and "fought beside a friend today" in reading["line"]

    def test_a_new_order_counts_his_battles_from_now(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        ney.battles_won = 5
        ney.own_record = {"tick_won": 0, "tick_lost": 0}
        _give(world, "Ney", "hold", "Rhineland")
        assert O.record(ney)["tick_won"] == 5
        O._life(world, ney)
        assert O.record(ney).get("last") != "won" and not O.record(ney).get("held")

    def test_a_change_keeps_where_he_stands_and_starts_tonight(self, world1805):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        spec = O.own(ney)
        spec.update(given=int(world.current_turn) - 2, state="work", acted=int(world.current_turn) - 1)
        new, why = O.spec_from(world, ney, "hold", "Rhineland", risk=1)
        assert new is not None, why
        with _quiet():
            out = O.give(world, ney, new, line="Ney, more risk")
        assert out["success"] and "He turns to it tonight" in out["message"]
        assert O.own(ney)["state"] == "work" and O.own(ney)["acted"] == int(world.current_turn) - 1

    def test_a_march_into_an_empty_place_is_no_attack_to_join(self):
        taken = O._taken_by({"act": "take", "marshal": "Ney", "place": "Swabia", "target": "Swabia",
                             "do": [{"action": "move", "target": "Swabia"}]}, None)
        assert "Swabia" not in taken and taken.get("~Swabia") == "Ney"

    def test_a_quarry_destroyed_out_of_sight_is_not_known_destroyed(self, world1805):
        world = _fresh(world1805)
        murat = _give(world, "Murat", "pursue", "Mack")
        O.own(murat)["unseen"] = 1
        world.marshals["Mack"].strength = 0
        row = O._life(world, murat)
        assert O.on_his_own(murat) and row is None
        assert int(O.own(murat)["unseen"]) == 2

    def test_a_target_beyond_his_odds_asks_after_three_nights(self):
        import inspect
        src = inspect.getsource(O._carry_out)
        assert "WAITS_ASKS_AFTER" in src and 'fresh.get("stuck")' in src
        assert O.WAITS_ASKS_AFTER == 3 and O.BARRED_ASKS_AFTER == 2


class TestWhatThePressingAndTheClientReviewFound:
    """IC3-C1 … C6 (pressed in the real client) and IC3-V22, V23 (the review's
    client lane) — `BUG_FIXES.md` §"Row IC, Session 3"."""

    def test_c1_his_card_reads_his_task_off_the_board_and_the_overview(self):
        state = (CLIENT / "scripts" / "marshal_state.gd").read_text(encoding="utf-8")
        assert state.count('"own": _dict_of(') >= 2, "from_board and from_overview both carry it"
        assert 'return _badge("own", "On his own"' in state

    def test_c4_end_turn_prints_every_tonight_as_you_press(self):
        main = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8")
        at = main.index("func _send_end_turn")
        body = main[at:main.index("\nfunc ", at + 10)]
        assert "for own_row in _own_tonight_rows():" in body
        assert body.index("for own_row in _own_tonight_rows():") < body.index("set_input_enabled(false)")

    def test_c6_the_morning_tells_the_night_once(self, world1805):
        world = _fresh(world1805)
        world.log_event({"type": O.EVENT, "phase": "night", "act": "march", "marshal": "Ney",
                         "nation": "France", "message": "Ney marched."})
        world.log_event({"type": O.EVENT, "phase": "done", "marshal": "Ney", "nation": "France",
                         "message": "Ney has taken Swabia and holds it now."})
        said = [e["message"] for e in O.morning_events(world)]
        assert said == ["Ney has taken Swabia and holds it now."], said
        assert O.morning_events(world) == [], "each told once"

    def test_v22_the_updates_head_stands_with_nobody_on_his_own(self):
        main = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8")
        assert "var heads_said := false" in main
        assert "var heads_said := own_rows.is_empty()" not in main

    def test_v23_the_one_line_desk_carries_no_own_line(self):
        desk = (CLIENT / "scripts" / "desk_lines.gd").read_text(encoding="utf-8")
        at = desk.index("if one_line:")
        assert "_own.visible = false" in desk[at:desk.index("_fill_one_line(", at)]


class TestWhatTheSecondReadingSaidOfTheOlderScreens:
    """The second blind reading's still-unclear list (`docs/audits/ic_client/
    session3/README.md`): "Stand here" against "Stay put" is fixed here; the
    other three are IC3-N1, Session H's head (`BUG_FIXES.md`)."""

    def test_stand_here_and_stay_put_each_name_the_other(self):
        table = (CLIENT / "scripts" / "simple_orders.gd").read_text(encoding="utf-8")
        stand = table[table.index('{"id": "stand"'):table.index('{"id": "stay_put"')]
        stay = table[table.index('{"id": "stay_put"'):table.index('{"id": "posture"')]
        assert "Stay put does nothing at all" in stand
        assert "Stand here makes him defend where he is" in stay

    @pytest.mark.xfail(strict=True, reason="IC3-N1 — owned by Session H's head (BUG_FIXES.md §Row IC, Session 3)")
    def test_n1_actions_the_writing_chips_and_titled_provinces_are_said_plainly(self):
        scripts = CLIENT / "scripts"
        outside_codex = " ".join(p.read_text(encoding="utf-8") for p in scripts.glob("*.gd")
                                 if p.name != "codex_terms.gd")
        assert "an order spends them" in outside_codex, "the actions counter's hover says what an action is"
        assert "into your sentence" in (scripts / "main.gd").read_text(encoding="utf-8"), \
            "a chip that writes into the line says so on hover"
        ledger = (scripts / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        at = ledger.index("titled provinces")
        assert "a titled province is" in ledger[:at + 400].lower(), "the word is said before it is used"


class TestTheReviewsLastThreeRows:
    """IC3-V10, V17, V20 — each with a test of its own."""

    def test_v10_a_march_refused_half_way_was_his_night(self, world1805, monkeypatch):
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        O.own(ney)["given"] = int(world.current_turn) - 1
        said = {"marshal": "Ney", "act": "march", "place": "Swabia", "target": "Swabia",
                "line": "Ney marches on Swabia", "visible": True,
                "do": [{"action": "move", "target": "Baden"}, {"action": "move", "target": "Swabia"}]}
        monkeypatch.setattr(O, "_read_in_turn", lambda *a, **k: dict(said))

        class Half:
            calls = 0

            def execute(self, payload, game_state):
                Half.calls += 1
                return {"success": Half.calls == 1, "message": "the road is closed"}
        row = O._carry_out(world, Half(), {"world": world}, ney, dict(said), {}, {}, [], [])
        assert row["act"] == "stay" and "could not carry out" in row["message"]
        assert O.acted_tonight(ney, world), "he went part of the way: his if-thens sleep"

    def test_v17_a_risk_change_at_its_limit_is_refused_before_enter(self, road):
        client, snap = road
        _board(snap)
        assert _post(client, "Ney, hold Rhineland boldly on your own")["success"]
        reading = _preview(client, "Ney, more risk")
        assert reading.get("ok") is not True
        assert "one step is the most you can move him" in json.dumps(reading)

    def test_v20_why_to_a_man_not_on_his_own(self, world1805):
        world = _fresh(world1805)
        says = O.answer(world, world.marshals["Ney"], "why")["says"]
        assert says == "I carried out your orders, Sire."


# ═══════════════ his ruling of November 22, 2026 — owed by Session 4b ════════

class TestWhatSession4bOwesHisRuling:
    """The user, November 22, 2026, at the end of row IC Session 4, verbatim:
    "tihis is for one sgiven autonomous right i mean yeah they are autonomous
    your word sguide them it should be like napoleonic warfare buit no orders
    and they dont just sit there during war" — and, correcting the first
    wording (which kept his choices inside the task): "if they dont do their
    own thing its really no different then guys you move very turn in essance"
    · "orders shlould beguiding ai that has its own actions and does its own
    thing you get it". A man GIVEN autonomy is his own commander: the task
    guides his choice and never fences it; he takes the initiative and never
    sits idle while France is at war (`BUG_FIXES.md` IC4-D3, the spec's D40;
    row IC Session 4b, `docs/NEXT_SESSION_PROMPT.md`). Each pin is a STRICT
    expected failure on what the game does today: it turns red the day the
    ruling is built, and the builder makes it a plain test."""

    @pytest.mark.xfail(strict=True, raises=AssertionError,
                       reason="IC4-D3: today his task fences his choice — he marches past a beatable enemy beside him")
    def test_he_takes_the_initiative_beside_his_road(self, world1805):
        """Ney (bold) is told to take Bohemia; an Austrian raid of 4,000 stands in
        French Lorraine beside him, off his road, and France sees it. A commander
        with initiative strikes it, then turns back to his task; today he marches
        from Rhineland to Swabia past it."""
        from backend.commands import if_thens
        world = _fresh(world1805)
        world.marshals["Mack"].location = "Vienna"           # the road to Bohemia is open
        john = world.marshals["ArchdukeJohn"]
        john.location, john.strength = "Lorraine", 4000
        world.refresh_marshal_indexes()
        ney = _give(world, "Ney", "take", "Bohemia")
        O.own(ney)["given"] = int(world.current_turn) - 1    # his first night is past
        seen = [(enemy.name, where) for enemy, where in if_thens.seen_enemies(world, ney)]
        assert ("ArchdukeJohn", "Lorraine") in seen, seen
        reading = O.read(world, ney, O.own(ney), preview=True)
        assert any(step.get("action") == "attack" and step.get("target") in ("ArchdukeJohn", "Lorraine")
                   for step in reading.get("do") or []), reading.get("line")

    @pytest.mark.xfail(strict=True, raises=AssertionError,
                       reason="IC4-D3: today a finished chase ends his order and he waits")
    def test_a_finished_chase_in_a_war_leaves_him_on_his_own(self, world1805):
        world = _fresh(world1805)
        murat = _give(world, "Murat", "pursue", "Mack")
        assert world.is_at_war("France", "Austria")
        world.marshals["Mack"].strength = 0
        O._life(world, murat)
        assert O.on_his_own(murat), "the chase is done; in a war he goes on by his nature"

    @pytest.mark.xfail(strict=True, raises=AssertionError,
                       reason="IC4-D3: today four quiet nights make him ask for work and wait")
    def test_a_quiet_front_in_a_war_sends_him_to_find_work(self, world1805, monkeypatch):
        from backend.commands import if_thens
        world = _fresh(world1805)
        ney = _give(world, "Ney", "hold", "Rhineland")
        rec = O.record(ney)
        rec["idle_run"] = O.QUIET_FRONT_ASKS
        ney.own_record = rec
        monkeypatch.setattr(if_thens, "seen_enemies", lambda *a, **k: [])
        O._life(world, ney)
        assert O.on_his_own(ney)
        assert O.own(ney).get("state") != "asks", "a quiet front in a war: he goes to find the enemy"

    @pytest.mark.xfail(strict=True, raises=AssertionError,
                       reason="IC4-D3: today a forced retreat wipes his task (combat_executor)")
    def test_a_beaten_man_on_his_own_keeps_his_task(self, world1805):
        from backend.commands.executor import CommandExecutor
        world = _fresh(world1805)
        ney = _give(world, "Ney", "take", "Swabia")
        with _quiet():
            CommandExecutor()._combat._apply_forced_retreat_or_break(
                ney, world.marshals["Mack"], world, skip_fate=True)
        assert O.on_his_own(ney), "beaten, he falls back, rallies and carries on with his task"

    @pytest.mark.xfail(strict=True, raises=AssertionError,
                       reason="IC4-D3: today a man is set on his own only with one of four tasks")
    def test_he_can_be_set_on_his_own_with_no_task(self, road):
        client, snap = road
        world = _board(snap)
        _post(client, "Ney, act on your own")
        assert O.on_his_own(world.marshals["Ney"]), "no task: he makes war as he sees fit"

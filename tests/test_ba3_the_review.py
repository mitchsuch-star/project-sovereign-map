"""Row BA, session BA-3 — THE REVIEW (November 16, 2026).

Six readers, each in its own lane, on a frozen copy of the finished change;
every finding reproduced before a line was changed
(`docs/BATTLE_DIORAMA_SPEC.md` §15.18; the rows are `docs/BUG_FIXES.md` §BA3,
BA3-X6 on). One pin a row:

* a plain test for a row FIXED in the review — each was red before its fix;
* a strict xfail for a row FILED (owner: row BA's session BA-4). It turns red
  the day the row lands and is then made a plain test with it. Each filed pin
  fails on ONE assertion — the defect — and raises a `RuntimeError` when the
  board no longer reaches that assertion, so a board that drifted cannot pass
  for the defect.

The client's rows (BA3-X17, BA3-X18, BA3-X19, BA3-X22) are pinned where the
client is driven — the live walk's steps, in `tests/test_ba3_the_days_panel.py`.
"""

import contextlib
import copy
import io
from types import SimpleNamespace

import pytest

import backend.main as M
import tests.test_ba3_the_rounds as T
from backend.ai.enemy_ai import EnemyAI, ai_rng
from backend.commands.executor import CommandExecutor
from backend.game_logic import battle_day as BD
from backend.game_logic import battle_script as BS
from backend.game_logic import campaign_variance as cv
from backend.models.world_state import WorldState
from tests.test_ba3_the_rounds import (  # noqa: F401  (`table` is the fixture)
    FIELD, HOME, ROLLED, _awaits_us, _mk, _quiet, _seat, table)


def _ours(day):
    return [t for t in day["told"] if t["who"] == "ours"]


def _word_beats(tableau):
    """The `word` beats of a tableau's script — the day's own line, as the
    table tells the clash."""
    return [beat.get("text") for act in ((tableau or {}).get("script") or {}).get("acts") or []
            for beat in act.get("beats") or [] if beat.get("kind") == "word"]


# ════════════════════════════════════════════════════════
# BA3-X6 — the parked word: what parked it, and what its answer ran
# ════════════════════════════════════════════════════════

class TestAnAnswerIsToldAsWhatHeDid:
    """An objection's answer runs the order as given (insist, by my word),
    the marshal's alternative (trust) or the middle ground (compromise). The
    day bills the word the chip quoted and TELLS what he then did. Before the
    review a compromise that only changed his stance was told "Ney presses
    the attack.", an alternative that fought a battle "Ney digs in.", and an
    alternative that left the field closed the day with no line and no
    banner."""

    def _objected(self, table, line, timid=False):
        _, day = table.open_a_day(_awaits_us)
        world = table.world
        if timid:
            world.marshals["Ney"].personality = "cautious"
            world.marshals["Ney"].strength = 20000
            world.marshals["Mack"].strength = 70000
        asked = table.order(line)
        assert asked.get("state") == "awaiting_player_choice", asked.get("message")
        return day, world.pending_objection

    def test_the_middle_ground_that_puts_him_on_the_defensive_is_digging_in(self, table):
        day, objection = self._objected(table, "Ney, attack Mack", timid=True)
        middle = objection["compromise"]
        assert middle["action"] == "stance_change" and middle["target_stance"] == "defensive", middle
        answered = table.answer("compromise")
        assert answered["success"], answered.get("message")
        said = answered["battle_day"]
        assert _ours(said)[-1]["kind"] == "dig_in" and _ours(said)[-1]["line"] == "Ney digs in."
        assert not any(t["line"] == "Ney presses the attack." for t in said["told"]), "he did not press"
        assert said["ours"] == day["ours"] - 1, "an order ran: the word is paid for"
        assert answered["action_info"]["cost"] == 0 and table.world.actions_remaining == 3

    def test_his_alternative_fought_is_told_as_the_clash_it_was(self, table):
        day, objection = self._objected(table, "Ney, defend")
        assert objection["suggested_alternative"]["action"] == "attack", objection["suggested_alternative"]
        answered = table.answer("trust")
        assert answered["success"], answered.get("message")
        said = answered["battle_day"]
        assert _ours(said)[-1]["kind"] == "press" and _ours(said)[-1]["line"] == "Ney presses the attack."
        assert not any(t["who"] == "ours" and t["kind"] == "dig_in" for t in said["told"]), "he did not dig in"
        # ...and the clash's own script says the same word.
        assert _word_beats(answered.get("battle_diorama")) == ["Ney presses the attack."]
        assert answered["action_info"]["cost"] == 0 and table.world.actions_remaining == 3

    def test_his_alternative_to_leave_the_field_closes_the_day_as_a_fall_back(self, table):
        day, objection = self._objected(table, "Ney, attack Mack", timid=True)
        assert objection["suggested_alternative"]["action"] == "retreat", objection["suggested_alternative"]
        answered = table.answer("trust")
        assert answered["success"], answered.get("message")
        said = answered["battle_day"]
        assert said["open"] is False and said["ended"] == "fell_back", said
        assert said["banner"] == "Ney falls back" and _how(said)["line"] == "Ney falls back."
        assert said["ours"] == day["ours"], "he left the field: no point is taken"
        assert table.world.battle_days == {}

    def test_a_middle_ground_that_is_no_word_of_the_day_is_his_own_way(self, table):
        day, objection = self._objected(table, "Ney, defend")
        middle = objection["compromise"]
        assert middle["action"] == "stance_change" and middle["target_stance"] == "aggressive", middle
        answered = table.answer("compromise")
        said = answered["battle_day"]
        assert _ours(said)[-1]["kind"] == "own_way" and _ours(said)[-1]["line"] == "Ney goes his own way."
        assert not any(t["who"] == "ours" and t["kind"] == "dig_in" for t in said["told"])

    def test_the_word_that_runs_is_read_from_the_answer(self, table):
        """`the_word_that_runs` is PURE and keeps the price the chip quoted."""
        self._objected(table, "Ney, defend")
        world = table.world
        parked = BD.pending_word(world, marshal="Ney", by="objection")
        assert parked["kind"] == "dig_in" and parked["price"] == 1
        assert BD.what_the_answer_runs(world, "insist") is None
        assert BD.what_the_answer_runs(world, "word") is None
        assert BD.the_word_that_runs(world, parked, None) == parked
        fought = BD.the_word_that_runs(world, parked, BD.what_the_answer_runs(world, "trust"))
        assert (fought["kind"], fought["price"], fought["key"]) == ("press", 1, "Mack")
        assert BD.the_word_that_runs(world, parked, {"action": "retreat"})["kind"] == "break_off"
        assert BD.the_word_that_runs(world, parked, {"action": "wait"})["kind"] == "own_way"
        assert BD.the_word_that_runs(world, parked, {"action": "attack", "target": "Nobody"})["kind"] == "own_way"

    def test_on_the_strategic_road_the_middle_ground_is_the_word_itself(self):
        """A SUPPORT order's compromise is the same order with a term to it (a
        timed SUPPORT): the corps is still ordered up. Trusting him is his own
        way — the order is not issued."""
        world = SimpleNamespace(pending_objection=None, pending_strategic_objection={
            "marshal_name": "Soult", "strategic_type": "SUPPORT", "target": "Ney"})
        assert BD.what_the_answer_runs(world, "compromise") is None
        assert BD.what_the_answer_runs(world, "insist") is None
        assert BD.what_the_answer_runs(world, "word") is None
        assert BD.what_the_answer_runs(world, "trust") == {"action": "own_way"}
        parked = {"key": "Mack", "kind": "bring_up", "price": 1, "who": "ours", "marshal": "Soult"}
        world.battle_days = {"days": {}}
        world.get_marshal = lambda name: None
        assert BD.the_word_that_runs(world, parked, None)["kind"] == "bring_up"

    def test_a_sovereigns_alternative_attack_is_no_guard(self, table):
        """The Guard is the word that asks two points — never an objection's
        side door to its two morale numbers at one."""
        self._objected(table, "Ney, defend")
        world = table.world
        world.marshals["Ney"].personality = "sovereign"      # `is_sovereign` reads the temper
        assert world.marshals["Ney"].is_sovereign and BD.the_guard_goes_in()
        parked = BD.pending_word(world, marshal="Ney", by="objection")
        fought = BD.the_word_that_runs(world, parked, {"action": "attack", "target": "Mack"})
        assert fought["kind"] == "press"


class TestAnOrderThatIsNoWordDoesNotRideTheParkedWord:
    """The muster's "Commit the Attack?" parks the lead's press. His `defend`
    is then an ordinary order; he objects to it; and the answer ran on the
    PARKED word's lend — no action — while the muster's question still stood,
    so no point was taken either: a free order."""

    def _parked_by_the_question(self, table):
        _, day = table.open_a_day(_awaits_us, his_personality="cautious")
        world = table.world
        world.marshals["Ney"].strength = 14000
        world.marshals["Mack"].strength = 70000
        table.order("Ney, attack Mack")
        asking = world.marshals["Ney"].pending_interrupt
        assert asking and asking["interrupt_type"] == "muster_confirm"
        return day, world

    def test_it_costs_its_action(self, table):
        day, world = self._parked_by_the_question(table)
        assert world.battle_days["days"]["Mack"]["pending"]["by"] == "question"
        objected = table.order("Ney, defend")
        assert objected.get("state") == "awaiting_player_choice", objected.get("message")
        pool = world.actions_remaining
        answered = table.answer("insist")
        assert answered["success"], answered.get("message")
        assert world.actions_remaining == pool - 1 and answered["action_info"]["cost"] == 1
        store = world.battle_days["days"]["Mack"]
        assert store["ours"] == day["ours"], "no point: it was no word of the day"
        assert store["pending"]["kind"] == "press", "the parked press still waits for its own answer"

    def test_a_word_an_objection_parked_is_answered_only_by_that_objection(self, table):
        table.open_a_day(_awaits_us)
        world = table.world
        asked = table.order("Ney, defend")
        assert asked.get("state") == "awaiting_player_choice", asked.get("message")
        parked = world.battle_days["days"]["Mack"]["pending"]
        assert parked["by"] == "objection" and parked["order"][0] == "defend", parked
        assert BD.pending_word(world, marshal="Ney", by="objection")["kind"] == "dig_in"
        assert BD.pending_word(world, marshal="Ney", by="question") is None
        assert BD.pending_word(world, marshal="Ney")["kind"] == "dig_in", "unasked, as before"
        # Another order's objection in its place is not this word's.
        world.pending_objection["original_order"] = {"action": "attack", "target": "Davout"}
        assert BD.pending_word(world, marshal="Ney", by="objection") is None

    def test_a_parked_word_of_an_older_save_reads_as_before(self):
        """A day saved before the review holds no `by`: either road answers it."""
        world = SimpleNamespace(battle_days={"days": {"Mack": {
            "enemy": "Mack", "side": "attack", "pending": {"kind": "press", "price": 1, "marshal": "Ney"}}}},
            pending_objection=None, pending_strategic_objection=None)
        for by in (None, "objection", "question"):
            assert BD.pending_word(world, marshal="Ney", by=by)["kind"] == "press"


# ════════════════════════════════════════════════════════
# BA3-X7 — a day that is over awaits no word
# ════════════════════════════════════════════════════════

class TestTheGateNamesOnlyLivingDays:

    def test_a_day_its_lead_marched_away_from_awaits_no_word(self, table):
        """Every response lists the days that await our word, and the end-turn
        gate reads the list: "The day at … still hangs — Ney holds 2 points."
        It still named a day whose lead had marched off the field."""
        table.open_a_day(_awaits_us)
        world = table.world
        assert [d["enemy"] for d in table.order("status")["pending_battle_days"]] == ["Mack"]
        for there in world.get_region(HOME).adjacent_regions:
            if there != FIELD and table.order(f"Ney, move to {there}").get("success") \
                    and world.marshals["Ney"].location != HOME:
                break
        else:
            raise AssertionError("no road off the field for the lead")
        assert BD.awaiting(world) == []
        assert table.order("status")["pending_battle_days"] == []


class TestTheServerNamesTheLivingDays:
    """BA3-X18's server half. The client keeps each day's last block and its
    chips (in the log's old lines too) and had no way to learn that a day
    ended unseen — night at the turn's end carries no block; a lead marched
    off the field. Every response now names the days still open and alive
    (`open_battle_days`, by enemy); the client lets go of the rest — shown in
    the real client by the live walk's step `r12_old_chip`."""

    def test_every_response_names_the_days_still_open(self, table):
        assert table.order("status")["open_battle_days"] == []
        table.open_a_day(_awaits_us)
        assert table.order("status")["open_battle_days"] == ["Mack"]
        # A day that waits on a question awaits no word of ours — and is open.
        asked = table.order("Ney, defend")
        assert asked.get("state") == "awaiting_player_choice", asked.get("message")
        assert asked["pending_battle_days"] == [] and asked["open_battle_days"] == ["Mack"]
        table.answer("insist")
        ended = table.order("end turn")
        assert ended["success"], ended.get("message")
        assert ended["open_battle_days"] == [], "night fell: the client lets the day go"

    def test_a_loaded_save_names_its_open_day(self, table):
        table.open_a_day(_awaits_us)
        saved = _quiet(table.tc.post, "/save", json={"save_name": "ba3_review_day"}).json()
        assert saved["success"], saved.get("message")
        loaded = _quiet(table.tc.post, "/load", json={"filename": "ba3_review_day.json"}).json()
        assert loaded["success"] and loaded["open_battle_days"] == ["Mack"]

    def test_a_day_its_lead_left_is_not_among_them(self, table):
        table.open_a_day(_awaits_us)
        world = table.world
        world.marshals["Ney"].location = next(
            n for n in world.get_region(HOME).adjacent_regions if n != FIELD)
        assert BD.living(world) == [] and table.order("status")["open_battle_days"] == []

    def test_off_the_served_road_there_is_none(self):
        assert BD.living(WorldState()) == []


# ════════════════════════════════════════════════════════
# BA3-X8, BA3-X9 — who drew off, and where to
# ════════════════════════════════════════════════════════

class TestOurLeadFallsBackUnderHisOwnBanner:

    def test_left_to_it_and_beaten_on_points_he_falls_back(self, table):
        """`_speak`'s draw-off closed the day as "drew_off" whoever spoke: our
        own lead, left to it, left the field under "MACK DRAWS OFF"."""
        table.open_a_day(_awaits_us)
        world = table.world
        store = world.battle_days["days"]["Mack"]
        # A day HE opened, lost on points, our lead with nothing left to strike with.
        store.update(side="defence", ours=0, theirs=1)
        store["read"]["ahead"] = "theirs"
        body = table.word("leave_it")
        assert body["success"], body.get("message")
        said = body["battle_day"]
        assert said["open"] is False and said["ended"] == "fell_back", said
        assert said["banner"] == "Ney falls back"
        assert _how(said)["line"].startswith("Ney falls back toward ")
        assert world.marshals["Ney"].location != HOME and world.battle_days == {}


class TestWhereHeWentIsToldOnlyWhenWeSeeIt:
    """The fog law for the enemy in a battle we fought (`SYSTEMS_REFERENCE`
    §219.2, case 2): never where to. His road off the field is named when the
    game's one sighting rule shows him standing there — the server's own
    draw-off, with our lead on the field, is pinned so in
    `tests/test_ba3_the_rounds.py`
    (`test_through_the_server_he_draws_off_and_the_day_is_over`)."""

    def test_a_refuge_we_cannot_see_is_not_named(self, table, monkeypatch):
        """A clash won without the lead entering the field (the guns' word):
        he draws off two provinces from our nearest corps. The line said "Mack
        draws off toward Vienna." — an unseen corps placed on the map."""
        monkeypatch.setattr(T, "HOME", "Franconia")
        monkeypatch.setattr(T, "FIELD", "Bohemia")
        world = table.world
        _seat(world, ours=62000, his=40000)
        world.calculate_visibility()
        world.battle_days = {"days": {"Mack": {
            "enemy": "Mack", "lead": "Ney", "field": "Bohemia",
            "our_ground": "Franconia", "his_ground": "Bohemia", "side": "attack",
            "ours": 2, "theirs": 2, "ours_of": 2, "theirs_of": 2, "awaits": "theirs",
            "silences": 0, "words": 1, "turn": int(world.current_turn), "offered": False,
            "read": {"ahead": "ours", "our_loss": 1000, "his_loss": 4000}}}}
        replies = _quiet(BD.his_answer, world, M.game_state, M.executor, only="Mack")
        mack = world.marshals["Mack"]
        if replies.get("Mack", {}).get("kind") != "draw_off":
            raise AssertionError(f"he did not draw off on this board: {replies}")
        refuge = BD._place(world, mack.location)
        assert mack.location != "Bohemia" and refuge
        assert all(m.name != "Mack" for m in world.get_visible_enemies("France")), "the board must hide him"
        assert replies["Mack"]["line"] == "Mack draws off."
        closing = (BD._CLOSED.get(world) or {}).get("Mack") or {}
        assert closing.get("ended") == "drew_off" and closing.get("banner") == "Mack draws off"
        assert not any(refuge in str(t.get("line")) for t in closing.get("told") or []), closing.get("told")


# ════════════════════════════════════════════════════════
# BA3-X10 — his second assault is told as one
# ════════════════════════════════════════════════════════

class TestHisSecondAssaultIsToldAsOne:

    def test_on_a_day_he_opened_his_strike_comes_on_again(self, table):
        """His opening clash was never counted: under "Ney strikes back." the
        day told "Mack strikes back." too. The table's own word beat and the
        day's told line now say the same thing."""
        world = table.world
        body = None
        for _ in range(40):
            _seat(world, ours=50000, his=50000, his_personality="aggressive", our_personality="cautious")
            world.calculate_visibility()
            world.clear_turn_battles()
            _quiet(EnemyAI(M.executor)._execute_action,
                   {"marshal": "Mack", "action": "attack", "target": "Ney"}, M.game_state)
            if BD.day_against(world, "Mack") is None:
                continue
            body = table.order("Ney, attack Mack")
            if ((body.get("battle_day") or {}).get("reply") or {}).get("kind") == "strike":
                break
        else:
            raise AssertionError("no day he opened in which he then struck again")
        day = body["battle_day"]
        told = [(t["who"], t["line"]) for t in day["told"]]
        assert ("ours", "Ney strikes back.") in told
        assert ("theirs", "Mack comes on again.") in told and ("theirs", "Mack strikes back.") not in told
        assert day["reply"]["line"] == "Mack comes on again."
        assert _word_beats(day["reply"].get("diorama")) == ["Mack comes on again."]

    def test_on_a_day_we_opened_his_first_strike_strikes_back(self, table):
        want = lambda d: _awaits_us(d) and (d.get("reply") or {}).get("kind") == "strike"   # noqa: E731
        _, day = table.open_a_day(want, his=70000, his_personality="aggressive")
        assert day["reply"]["line"] == "Mack strikes back."
        assert _word_beats(day["reply"].get("diorama")) == ["Mack strikes back."]


# ════════════════════════════════════════════════════════
# BA3-X11 — two days, one lead: the first that can take the word
# ════════════════════════════════════════════════════════

class TestAWordBindsToTheDayThatCanTakeIt:

    def test_the_second_days_lit_chip_is_a_word_of_the_second_day(self, table):
        """`classify_word` returned on the FIRST day whose lead matched: with
        that day's purse spent, the second day's lit "digs in" (1 point) ran
        as an ordinary order and took an action."""
        table.open_a_day(_awaits_us)
        world = table.world
        world.marshals["Kienmayer"] = _mk("Kienmayer", "Frankfurt", 60000, nation="Austria",
                                          personality="literal")
        assert "Frankfurt" in world.get_region(HOME).adjacent_regions, "the board changed"
        world.update_intel_from_battle("Frankfurt", int(world.current_turn))
        first = world.battle_days["days"]["Mack"]
        second = copy.deepcopy(first)
        second.update(enemy="Kienmayer", his_ground="Frankfurt", ours=2, theirs=1, awaits="ours")
        world.battle_days["days"]["Kienmayer"] = second
        first["ours"] = 0                               # the first day's purse is spent
        chips = {d["enemy"]: next(c for c in d["chips"] if c["kind"] == "dig_in") for d in table.days()["days"]}
        assert chips["Mack"]["ok"] is False and chips["Kienmayer"]["ok"] is True
        assert chips["Kienmayer"]["command"] == "Ney, defend" and chips["Kienmayer"]["price"] == 1
        word = BD.classify_word(world, {"command": {"marshal": "Ney", "action": "defend"}})
        assert word and (word["key"], word["kind"]) == ("Kienmayer", "dig_in")
        pool = world.actions_remaining
        body = table.order("Ney, defend")
        if world.pending_objection:
            body = table.answer("insist")
        assert body["success"], body.get("message")
        assert world.actions_remaining == pool, "a word of the second day: no action"
        assert {k: d["ours"] for k, d in BD.open_days(world).items()} == {"Mack": 0, "Kienmayer": 1}


# ════════════════════════════════════════════════════════
# BA3-X12 — a day won on points is not a day carried
# ════════════════════════════════════════════════════════

class TestADayWonOnPointsIsNotCarried:
    """`victor` is set on a battle won ON POINTS — the very outcome a great
    battle's day hangs on. The named moment said "The day is won by Soult's
    arrival at the last hour." over "THE DAY HANGS"."""

    SEEDS = ("a", "b", "c", "d", "e", "f")

    def _moments(self, monkeypatch, kind, result, muster):
        monkeypatch.setattr(cv, "campaign_is_served", lambda world: True)
        texts = set()
        for seed in self.SEEDS:
            world = SimpleNamespace(campaign_seed=seed + "-seedy-09", current_turn=3)
            script = BS._Script({"Ney", "Mack", "Soult"}, world, ("Ney", "Mack", "Lorraine", 3))
            BS._named_moments(script, SimpleNamespace(name="Ney"), SimpleNamespace(name="Mack"),
                              result, muster, {})
            texts |= {beat["text"] for beat in script.acts["crisis"] if beat["kind"] == kind}
        assert len(texts) == 2, f"both variants are told across the seeds: {texts}"
        return texts

    @pytest.mark.parametrize("outcome, carried", [
        ("attacker_tactical_victory", False), ("attacker_victory", True)])
    def test_the_late_arrival(self, monkeypatch, outcome, carried):
        texts = self._moments(
            monkeypatch, "moment_late_arrival",
            {"outcome": outcome, "victor": "Ney", "attacker_roll": {}},
            {"attacker": [{"marshal": "Soult", "arrived": True, "score": 12, "threshold": 10}],
             "defender": []})
        says_won = {("carries the day" in t or "The day is won" in t) for t in texts}
        assert says_won == {carried}, texts
        if not carried:
            assert all("on points" in t for t in texts), texts

    @pytest.mark.parametrize("outcome, carried", [
        ("attacker_tactical_victory", False), ("attacker_victory", True)])
    def test_the_two_on_the_dice(self, monkeypatch, outcome, carried):
        texts = self._moments(
            monkeypatch, "moment_two",
            {"outcome": outcome, "victor": "Ney", "attacker_roll": {"is_critical_failure": True}},
            {"attacker": [], "defender": []})
        assert any("carries the day" in t for t in texts) is carried, texts
        if not carried:
            assert not any("wins all the same" in t for t in texts), texts


# ════════════════════════════════════════════════════════
# FILED for BA-4 — each moves a measured world-line, or is a rule to gate.
# LANDED there (row BA, BA-4, November 16, 2026): each pin below was a strict
# xfail and is a plain test now; the rule, its seam and its seam-down twin are
# in tests/test_ba4_the_roads_and_the_fog.py.
# ════════════════════════════════════════════════════════

def _how(block):
    """How a closed day ended, as its table tells it: the last line told that
    is not the day's tally. (Row BA, BA-4: under the line that says HOW it
    ended the closing table now tells what the day came to — "Two clashes:
    13,540 of ours for 16,474 of the enemy's." — as the last line told.)"""
    return next(t for t in reversed(block["told"]) if t.get("kind") != "tally")


def _served(extra=()):
    world = WorldState()
    world.campaign_seed = ROLLED
    cv.serve_campaign(world)
    ney, mack = _seat(world, extra=extra)
    return world, ney, mack


def _a_day(ney, mack, **over):
    day = {"enemy": mack.name, "lead": ney.name, "field": mack.location,
           "our_ground": ney.location, "his_ground": mack.location,
           "side": "attack", "ours": 2, "theirs": 0, "awaits": "ours", "silences": 0, "words": 0,
           "turn": 1, "offered": True, "read": {"ahead": "even", "our_loss": 0, "his_loss": 0}}
    day.update(over)
    return day


class TestFiledForTheRoadsAndTheFog:

    def test_a_day_that_died_before_night_bars_no_strike(self):
        """`night_falls` bars the pair for EVERY day open when the night
        began — also one that is already over because its lead marched off the
        field. Walking away buys a phase in which that corps cannot be struck."""
        world, ney, mack = _served()
        world.battle_days = {"days": {"Mack": _a_day(ney, mack)}}
        away = next(n for n in world.get_region(ney.location).adjacent_regions if n != mack.location)
        ney.location = away                              # the lead has left the field
        if BD._alive(world, world.battle_days["days"]["Mack"]):
            raise RuntimeError("the board no longer kills the day")
        with contextlib.redirect_stdout(io.StringIO()):
            BD.night_falls(world, {"world": world}, CommandExecutor())
        if BD.open_days(world):
            raise RuntimeError("the dead day was not closed at night")
        assert BD.bars(world) == set()

    def test_his_word_leaves_the_phases_stream_where_it_was(self, table):
        """His word is run through the AI's one executor door, which scores
        every order it runs with a draw from the court's own stream for the
        turn (`ai_rng`) — the PHASE's stream, which no save carries. A save
        and a load after a word of his replay his phase from another draw."""
        table.open_a_day(_awaits_us)
        world = table.world
        stream = ai_rng(world, "Austria")
        before = stream.getstate()
        body = table.word("stand")                       # we stand: he answers with a word of his own
        said = (body.get("battle_day") or {}).get("told") or []
        if not any(t["who"] == "theirs" and t["kind"] not in ("stand", "") for t in said[-2:]):
            raise RuntimeError(f"he gave no word that runs an order on this board: {said}")
        assert ai_rng(world, "Austria") is stream and stream.getstate() == before

    def test_a_lead_holds_one_day_at_a_time(self):
        """Two corps of his may each fight one lead of ours to a hanging great
        battle in one phase, and each opens a day: two purses, two turns, one
        lead — whose `digs in` is one order and can answer only one of them."""
        world, ney, mack = _served()
        beside = next(n for n in world.get_region(ney.location).adjacent_regions if n != mack.location)
        world.marshals["Kienmayer"] = _mk("Kienmayer", beside, 60000, nation="Austria", personality="literal")
        for foe in ("Mack", "Kienmayer"):
            BD.after_the_battle(SimpleNamespace(
                world=world, marshal=world.marshals[foe], enemy_marshal=ney,
                battle_result={"outcome": "stalemate", "attacker": {}, "defender": {}},
                total_engaged_strength=120000, battle_region_name=ney.location,
                conquered=False, enemy_destroyed=False))
        leads = [day["lead"] for day in BD.open_days(world).values()]
        if not leads:
            raise RuntimeError("no day opened on this board")
        assert leads == ["Ney"]

    def test_two_different_stance_orders_draw_their_own_moods(self, monkeypatch):
        """The mood's stream is keyed on the marshal, the action and the
        order's `target`; a stance order carries its stance in `target_stance`
        and no target, so "aggressive" and "defensive" share one draw."""
        made = []
        real = cv._PrivateStream

        class Recording(real):
            def __init__(self, seed):
                made.append(str(seed))
                super().__init__(seed)

        monkeypatch.setattr(cv, "_PrivateStream", Recording)
        keys = {}
        for stance in ("aggressive", "defensive"):
            world = WorldState()
            world.campaign_seed = ROLLED
            cv.serve_campaign(world)
            del made[:]
            with contextlib.redirect_stdout(io.StringIO()):
                CommandExecutor().execute({"command": {
                    "action": "stance_change", "type": "specific", "marshal": "Davout",
                    "target": None, "target_stance": stance}}, {"world": world})
            keys[stance] = [name for name in made if "|mood|" in name]
        if not all(keys.values()):
            raise RuntimeError(f"a stance order drew no mood on this board: {keys}")
        assert keys["aggressive"] != keys["defensive"]

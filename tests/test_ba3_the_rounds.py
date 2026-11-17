"""Row BA, session BA-3 — "the day's points": a great battle fought in turns.

The user's frame (November 15, 2026; `docs/BATTLE_DIORAMA_SPEC.md` §15.14):
"what if battles just have x amount of points in them and how you and enemy
use them is at discretion?" — the points from **the commander**, the enemy to
spend his on **all that you can**, and "small battles show the screen current
state it just doesnt need all mechanics".

What this file pins, by behaviour, through the game server (the only place a
day exists — `campaign_variance.campaign_is_served`):

* a small battle is one clash and carries nothing new;
* a great battle (80,000 men, the game's own bar) that does not decide the
  day opens one: the purses come from the two commanders, the side that did
  not open speaks first;
* a word is an order the game already has and costs points, never an action;
* the enemy spends his by the rule his AI already follows;
* silence is standing; two silences in a row, both purses empty or a side
  leaving the field is night;
* the Guard and NP-D1's two morale numbers; "Leave it to him";
* night at the turn's end and a defended day offered at dawn;
* the same save gives the same day; the store is saved only when it holds
  something; a world nobody serves has no day at all.
"""

import contextlib
import io
import random
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.game_logic import battle_day as BD
from backend.game_logic import campaign_variance as cv
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

ROLLED = "iron-eagle-07"
HOME, FIELD = "Rhineland", "Lorraine"


# ════════════════════════════════════════════════════════
# The board
# ════════════════════════════════════════════════════════

def _mk(name, location, strength, nation="France", personality="aggressive", command=6):
    marshal = Marshal(name=name, location=location, strength=int(strength),
                      personality=personality, nation=nation, movement_range=1,
                      tactical_skill=7, spawn_location=location)
    marshal.skills["command"] = int(command)
    return marshal


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _seat(world, *, ours=60000, his=60000, his_personality="literal", our_personality="aggressive",
          our_command=6, his_command=6, extra=()):
    """Ney beside Mack, at war, in sight; the turn's pool full; no day open.

    The served campaign's board is bare Europe (Rhineland beside Lorraine);
    a `WorldState()` of the suite's own is the legacy fixture map, where the
    pair is Belgium and Waterloo. The marshals carry their own ground."""
    home, field = (HOME, FIELD)
    if field not in world.get_region(home).adjacent_regions:
        home, field = "Belgium", "Waterloo"
    assert field in world.get_region(home).adjacent_regions, "the suite's boards changed"
    ney = _mk("Ney", home, ours, personality=our_personality, command=our_command)
    mack = _mk("Mack", field, his, nation="Austria", personality=his_personality, command=his_command)
    world.marshals = {m.name: m for m in (ney, mack) + tuple(extra)}
    world.diplomatic_states[world._make_diplo_key("Austria", "France")] = "WAR"
    for province in (home, field):
        world.update_intel_from_battle(province, int(world.current_turn))
    world.battle_days = {}
    world.actions_remaining = 4
    return ney, mack


class Table:
    """The game server with a campaign on it."""

    def __init__(self, client):
        self.tc = client

    @property
    def world(self):
        return M.world

    def boot(self, seed=ROLLED):
        booted = _quiet(self.tc.post, "/new_game", json={"seed": seed}).json()
        assert booted["success"], booted.get("message")
        return M.world

    def order(self, line):
        return _quiet(self.tc.post, "/command", json={"command": line}).json()

    def word(self, what, enemy="Mack"):
        return _quiet(self.tc.post, "/battle_day/word", json={"enemy": enemy, "word": what}).json()

    def answer(self, choice):
        return _quiet(self.tc.post, "/respond_to_objection", json={"choice": choice}).json()

    def days(self):
        return _quiet(self.tc.get, "/battle_day").json()

    def open_a_day(self, want=None, tries=40, **seat):
        """Fight the opening until the day hangs (and reads as `want` asks).
        The battle's dice are the campaign's (WS-11) and move with the count
        of battles fought, so each try is another battle of the same board."""
        for _ in range(tries):
            _seat(self.world, **seat)
            self.world.clear_turn_battles()
            body = self.order("Ney, attack Mack")
            day = body.get("battle_day")
            if day and (want is None or want(day)):
                return body, day
        raise AssertionError("no day of battle opened as asked")


def _how(block):
    """How a closed day ended, as its table tells it: the last line told that
    is not the day's tally. (Row BA, BA-4: under the line that says HOW it
    ended the closing table now tells what the day came to — "Two clashes:
    13,540 of ours for 16,474 of the enemy's." — as the last line told. Row
    BA, BA-5: and under the tally whom the toll favoured and what kind of day
    it was (kind "shape"); a clash's own line is kind "clash"; and, since the
    second reading, what follows a day no clash decided (kind "after").)"""
    return next(t for t in reversed(block["told"])
                if t.get("kind") not in ("tally", "shape", "clash", "after"))


def _awaits_us(day):
    return bool(day.get("open")) and day.get("awaits") == "ours"


def _chip(day, kind=None, word=None):
    for chip in day.get("chips") or []:
        if (kind is None or chip["kind"] == kind) and (word is None or chip["word"] == word):
            return chip
    return None


def _every_pool(body):
    """Every `actions_remaining` a response carries, wherever it sits (the
    client's counter reads `action_summary`'s)."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "actions_remaining" and isinstance(value, (int, float)):
                    found.append(int(value))
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(body)
    return found


def _tableaux_with_a_day(body):
    """Every tableau of a response that carries a day's block."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get("day"), dict) and "awaits" in node["day"]:
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(body)
    return found


@pytest.fixture
def table():
    before = M.world
    try:
        with TestClient(M.app) as client:
            seat = Table(client)
            seat.boot()
            yield seat
    finally:
        M._set_active_world(before)


# ════════════════════════════════════════════════════════
# 1. The others stay simple
# ════════════════════════════════════════════════════════

class TestASmallBattleIsOneClash:
    """The user's "small battles show the screen current state it just doesnt
    need all mechanics"."""

    def test_a_small_battle_opens_no_day_and_costs_its_action(self, table):
        # (row BA, BA-4: the key bar is 50,000 men since its measure — a small
        # battle is one under it; this board stood at 60,000 when the bar was 80,000)
        _seat(table.world, ours=20000, his=20000)
        body = table.order("Ney, attack Mack")
        assert body["success"], body.get("message")
        assert "battle_day" not in body
        assert "day" not in (body.get("battle_diorama") or {"day": 1}), "the tableau is today's"
        assert body["action_info"]["cost"] == 1
        assert table.world.battle_days == {}

    def test_a_great_battle_that_decides_the_day_opens_none(self, table):
        _seat(table.world, ours=110000, his=15000)
        body = table.order("Ney, attack Mack")
        assert body["success"], body.get("message")
        assert (body.get("battle_diorama") or {}).get("great_battle") is True
        assert "battle_day" not in body and table.world.battle_days == {}

    def test_nothing_is_written_to_an_ordinary_save(self, table):
        _seat(table.world, ours=20000, his=20000)        # under the key bar (50,000 since BA-4)
        table.order("Ney, attack Mack")
        assert "battle_days" not in table.world.to_dict()


# ════════════════════════════════════════════════════════
# 2. A great battle that hangs opens a day
# ════════════════════════════════════════════════════════

class TestAGreatBattleOpensADay:

    def test_the_day_its_purses_and_whose_word_it_is(self, table):
        body, day = table.open_a_day(_awaits_us)
        assert (body.get("battle_diorama") or {}).get("great_battle") is True
        assert day["enemy"] == "Mack" and day["lead"] == "Ney" and day["side"] == "attack"
        # The field is where the last clash was fought: his ground, or ours
        # when he has struck back.
        assert day["field"] in (FIELD, HOME)
        # The opening attack cost its action, as it always did.
        assert body["action_info"]["cost"] == 1 and table.world.actions_remaining == 3
        # The side that did not open speaks first: he has spoken (or stood).
        # (Row BA, BA-5: the opening's own line stands before his word.)
        words = [t for t in day["told"] if t["kind"] != "clash"]
        assert words and words[0]["who"] == "theirs"
        assert day["told"][0]["kind"] == "clash" and day["told"][0]["line"].startswith("The opening: ")
        assert day["ours"] == 2, "Ney's two points are untouched by the opening"
        assert 0 <= day["theirs"] <= 2
        assert body["battle_diorama"]["day"]["enemy"] == "Mack", "the tableau carries the day"

    def test_the_points_come_from_the_commander(self, table):
        _, day = table.open_a_day(_awaits_us, our_command=9, his_command=5)
        assert day["ours"] == 3, "command 8 or more: three points"
        assert (day["ours_of"], day["theirs_of"]) == (3, 2), "what each purse held when the day opened"
        assert day["theirs"] <= day["theirs_of"]
        _, day = table.open_a_day(_awaits_us, our_command=7)
        assert day["ours"] == 2

    def test_the_bar_is_the_games_own(self):
        """BA-3's bar was the game's GREAT battle (80,000). Row BA's BA-4
        moved it by its measure (`BATTLE_DIORAMA_SPEC.md` §15.20 M6): a key
        battle is a pitched battle of 50,000 — never above the great bar,
        which keeps its name and its news."""
        world = WorldState()
        assert world.GREAT_BATTLE_THRESHOLD == 80000
        assert BD.key_bar(world) == BD.KEY_BATTLE_MEN == 50000 <= world.GREAT_BATTLE_THRESHOLD
        low, high = _mk("A", HOME, 1, command=7), _mk("B", HOME, 1, command=8)
        assert Marshal.RALLY_FAST_COMMAND == 8
        assert (BD.points_for(low), BD.points_for(high)) == (2, 3)

    def test_the_chips_are_the_orders_the_game_already_has(self, table):
        _, day = table.open_a_day(_awaits_us)
        press, dig = _chip(day, "press"), _chip(day, "dig_in")
        assert press["command"] == "Ney, attack Mack" and press["price"] == 1 and press["ok"]
        assert dig["command"] == "Ney, defend" and dig["price"] == 1
        assert _chip(day, word="stand")["price"] == 0
        assert _chip(day, word="leave_it")["label"] == "Leave it to Ney"
        assert _chip(day, word="break_off")["label"] == "Break off"
        for chip in day["chips"]:
            assert bool(chip["command"]) != bool(chip["word"]), chip
            assert chip["counsel"] in ("none", "possible")
            assert chip["shown"] == "Ney" and chip["marshal"] == "Ney"

    def test_one_order_for_every_surface(self, table):
        """The lead's own words first, the Guard next, the others by kind, the
        exits last and "Leave it to him" last of all — on the table, the
        province panel and the log alike (`battle_day._chip_rank`)."""
        emperor = _mk("Napoleon", HOME, 30000, personality="sovereign", command=10)
        davout = _mk("Davout", HOME, 20000, personality="cautious")
        _, day = table.open_a_day(_awaits_us, extra=(emperor, davout))
        kinds = [(c["kind"], c["word"]) for c in day["chips"]]
        assert kinds[0] == ("press", "") and kinds[1] == ("guard", ""), kinds
        assert kinds[-1] == ("stand", "leave_it"), kinds
        spends = [i for i, (kind, word) in enumerate(kinds) if not word and kind not in ("stand", "break_off")]
        exits = [i for i in range(len(kinds)) if i not in spends]
        assert max(spends) < min(exits), kinds
        assert [k for k, _ in kinds].index("dig_in") < [k for k, _ in kinds].index("lead"), kinds

    def test_an_open_day_is_not_a_field_won(self, table):
        _, day = table.open_a_day(_awaits_us)
        assert day["banner"] == "The day hangs"
        assert table.word("break_off")["battle_day"]["banner"] == "The attack is broken off"

    def test_the_attack_card_says_a_battle_will_be_great(self, table):
        _seat(table.world)
        quote = _quiet(table.tc.get, "/march_quotes", params={"marshal": "Ney", "enemy": "Mack"}).json()
        told = quote["quote"]["day"]
        assert quote["success"] and {k: told[k] for k in ("great", "points", "bar")} == {
            "great": True, "points": 2, "bar": 50000}
        assert "pitched" not in told, "120,000 men: the game's GREAT battle"
        # The lesson of Ulm, before the order: is a road open behind him?
        assert told["his_road"] in (True, False)
        # (row BA, BA-4: 60,000 men is a key battle now — a pitched one — and
        # 40,000 is the small battle the card says nothing of)
        _seat(table.world, ours=30000, his=30000)
        quote = _quiet(table.tc.get, "/march_quotes", params={"marshal": "Ney", "enemy": "Mack"}).json()
        assert quote["quote"]["day"]["pitched"] is True and quote["quote"]["day"]["great"] is True
        _seat(table.world, ours=20000, his=20000)
        quote = _quiet(table.tc.get, "/march_quotes", params={"marshal": "Ney", "enemy": "Mack"}).json()
        assert "day" not in quote["quote"]


# ════════════════════════════════════════════════════════
# 3. A word costs points, never an action
# ════════════════════════════════════════════════════════

class TestAWordIsFreeOfActions:

    def test_the_lead_presses_for_a_point(self, table):
        _, day = table.open_a_day(_awaits_us)
        left = table.world.actions_remaining
        before = {n: int(m.strength) for n, m in table.world.marshals.items()}
        body = table.order("Ney, attack Mack")
        assert body["success"], body.get("message")
        assert body["action_info"]["cost"] == 0 and body["action_info"]["remaining"] == left
        assert table.world.actions_remaining == left, "nothing after the opening costs an action"
        after = {n: int(m.strength) for n, m in table.world.marshals.items()}
        assert after["Ney"] < before["Ney"] and after["Mack"] < before["Mack"], "a clash was fought"
        said = body["battle_day"]
        assert said["ours"] == day["ours"] - 1
        assert any(t["who"] == "ours" and t["kind"] == "press" for t in said["told"])
        assert body["battle_diorama"]["day"]["enemy"] == "Mack"

    def test_a_word_is_free_with_the_pool_empty(self, table):
        """What the lend is FOR (the review, BA3-X20: with the lend at nothing
        every test stayed green): the turn's actions all spent, the lead
        still presses for a point."""
        _, day = table.open_a_day(_awaits_us)
        table.world.actions_remaining = 0
        body = table.order("Ney, attack Mack")
        assert body["success"], body.get("message")
        assert table.world.actions_remaining == 0 and set(_every_pool(body)) == {0}
        said = body["battle_day"]
        assert any(t["who"] == "ours" and t["kind"] == "press" for t in said["told"])
        assert said["ours"] == day["ours"] - 1

    def test_he_answers_our_spent_word(self, table):
        """Turns alternate (the review, BA3-X20: a day that went on awaiting
        us after our own spent word left every test green)."""
        for _ in range(12):
            table.open_a_day(_awaits_us)
            said = table.order("Ney, attack Mack")["battle_day"]
            if said["ended"] != "decided":
                break
        else:
            raise AssertionError("every press decided the day")
        spoke = [t["who"] for t in said["told"]]
        ours_at = max(at for at, who in enumerate(spoke) if who == "ours")
        assert spoke[ours_at + 1:], f"nothing was said after our word: {said['told']}"
        # (Row BA, BA-5: a clash's own line is told after the word that fought it.)
        assert set(spoke[ours_at + 1:]) <= {"theirs", "end", "clash"}

    def test_the_counter_a_word_answers_with_is_the_pool(self, table):
        """Every `actions_remaining` the word's answer carries is the pool as
        it stands — never the pool with the word's lend on it."""
        _, day = table.open_a_day(_awaits_us)
        left = table.world.actions_remaining
        pressed = table.order(_chip(day, "press")["command"])
        assert pressed["success"], pressed.get("message")
        assert _every_pool(pressed) and set(_every_pool(pressed)) == {left}

    def test_every_response_names_the_days_that_await_our_word(self, table):
        """The end-turn gate's list (`pending_battle_days`, beside the last
        stands): ending the turn settles such a day by our silence."""
        body, day = table.open_a_day(_awaits_us)
        listed = body["pending_battle_days"]
        assert [(d["enemy"], d["lead_shown"], d["enemy_shown"], d["ours"], d["side"]) for d in listed] == [
            ("Mack", "Ney", "Mack", day["ours"], "attack")]
        assert listed[0]["field_shown"] == day["field_shown"]
        # a question out holds the turn by itself: the day is not listed twice over
        asked = table.order("Ney, defend")
        assert asked["battle_day"]["pending"] is True and asked["pending_battle_days"] == []
        table.answer("cancel")
        assert BD.awaiting(table.world) and BD.awaiting(table.world)[0]["enemy"] == "Mack"
        ended = table.word("break_off")
        assert ended["battle_day"]["open"] is False and ended["pending_battle_days"] == []
        assert BD.awaiting(WorldState()) == [], "a world nobody serves has no day to await"

    def test_a_refused_order_takes_no_point(self, table):
        _, day = table.open_a_day(_awaits_us)
        table.world.marshals["Ney"].fortified = True        # a fortified corps cannot attack
        body = table.order("Ney, attack Mack")
        assert not body["success"]
        assert table.world.battle_days["days"]["Mack"]["ours"] == day["ours"]
        assert table.world.actions_remaining == 3

    def test_with_the_purse_empty_the_chip_is_dim_and_an_order_is_an_order_again(self, table):
        want = lambda d: _awaits_us(d) and d["theirs"] >= 1          # noqa: E731
        _, day = table.open_a_day(want, his_command=9, his_personality="cautious",
                                  ours=62000, his=60000)
        table.world.battle_days["days"]["Mack"]["ours"] = 0
        live = table.days()["days"][0]
        press = _chip(live, "press")
        assert press["ok"] is False and press["why"] == "The day's points are spent."
        left = table.world.actions_remaining
        body = table.order("Ney, attack Mack")
        assert body["success"], body.get("message")
        assert body["action_info"]["cost"] == 1 and table.world.actions_remaining == left - 1

    def test_when_the_day_is_over_an_attack_costs_its_action_again(self, table):
        table.open_a_day(_awaits_us)
        closed = table.word("break_off")
        assert closed["success"] and closed["battle_day"]["open"] is False
        left = table.world.actions_remaining
        body = table.order("Ney, attack Mack")
        assert body["action_info"]["cost"] == 1 and table.world.actions_remaining == left - 1


# ════════════════════════════════════════════════════════
# 4. His answer — "all that you can", by the rule his AI already follows
# ════════════════════════════════════════════════════════

class _Fixed:
    """A stream that answers what it is told (the mood exactly at its base)."""

    def __init__(self, value=1.0):
        self.value = value

    def uniform(self, low, high):
        return self.value


def _pair(ours=60000, his=60000, personality="literal"):
    world = WorldState()
    _seat(world, ours=ours, his=his, his_personality=personality)
    return world, world.marshals["Ney"], world.marshals["Mack"]


class TestHisAnswerIsHisAIsOwnRule:

    def _word(self, world, marshal, foe, **kw):
        base = dict(purse=2, opened=False, behind=False, rng=_Fixed(1.0))
        base.update(kw)
        with contextlib.redirect_stdout(io.StringIO()):
            return EnemyAI(CommandExecutor()).the_days_word(marshal, foe, world, **base)

    @pytest.mark.parametrize("personality,his,kind", [
        ("aggressive", 43000, "strike"),      # 0.72 against a bar of 0.7
        ("aggressive", 41000, "dig_in"),      # 0.68: short of it
        ("literal", 61000, "strike"),         # 1.02 against 1.0
        ("literal", 59000, "dig_in"),
        ("cautious", 79000, "strike"),        # 1.32 against 1.3
        ("cautious", 77000, "dig_in"),
    ])
    def test_he_strikes_when_his_odds_meet_his_tempers_bar(self, personality, his, kind):
        world, ney, mack = _pair(his=his, personality=personality)
        assert EnemyAI.ATTACK_THRESHOLDS[personality] in (0.7, 1.0, 1.3)
        assert self._word(world, mack, ney)["kind"] == kind

    def test_his_mood_moves_the_bar_by_his_tempers_own_spread(self):
        world, ney, mack = _pair(his=57000, personality="literal")       # 0.95
        assert self._word(world, mack, ney, rng=_Fixed(1.0))["kind"] == "dig_in"
        low = 1.0 - EnemyAI.MOOD_VARIANCE["literal"]
        assert self._word(world, mack, ney, rng=_Fixed(low))["kind"] == "strike"

    def test_a_strike_asks_a_point(self):
        world, ney, mack = _pair(his=70000)
        assert self._word(world, mack, ney, purse=1)["kind"] == "strike"
        assert self._word(world, mack, ney, purse=0)["kind"] == "stand"

    def test_beaten_on_points_he_draws_off_when_a_road_is_open(self, monkeypatch):
        world, ney, mack = _pair(his=40000, personality="cautious")
        monkeypatch.setattr(EnemyAI, "_find_retreat_destination", lambda self, m, n, w, **k: "Franche-Comte")
        got = self._word(world, mack, ney, behind=True)
        assert got["kind"] == "draw_off" and got["to"] == "Franche-Comte"
        assert got["action"]["action"] == "retreat"

    def test_with_no_road_he_stands_and_digs_in(self, monkeypatch):
        """Mack, surrounded, stands and is taken."""
        world, ney, mack = _pair(his=40000, personality="cautious")
        monkeypatch.setattr(EnemyAI, "_find_retreat_destination", lambda self, m, n, w, **k: None)
        assert self._word(world, mack, ney, behind=True)["kind"] == "dig_in"
        assert self._word(world, mack, ney, behind=True, purse=0)["kind"] == "stand"

    def test_a_flight_into_the_country_he_is_at_war_with_is_no_road(self):
        """Mack at Ulm. Every province beside him is France's and empty: his
        AI's own finder would send him there in desperation, and in a day of
        battle that is no road — he is surrounded, and he stands."""
        world, ney, mack = _pair(his=40000, personality="cautious")
        for name in world.get_region(mack.location).adjacent_regions:
            world.get_region(name).controller = "France"
        ai = EnemyAI(CommandExecutor())
        with contextlib.redirect_stdout(io.StringIO()):
            desperate = ai._find_retreat_destination(mack, "Austria", world)
            to_the_rear = ai._find_retreat_destination(mack, "Austria", world, desperate=False)
        assert desperate is not None and to_the_rear is None
        assert self._word(world, mack, ney, behind=True)["kind"] == "dig_in"
        assert BD._his_road(world, mack) is False

    def test_a_road_to_his_own_soil_is_a_road(self):
        world, ney, mack = _pair(his=40000, personality="cautious")
        rear = next(n for n in world.get_region(mack.location).adjacent_regions if n != ney.location)
        for name in world.get_region(mack.location).adjacent_regions:
            world.get_region(name).controller = "France"
        world.get_region(rear).controller = "Austria"
        got = self._word(world, mack, ney, behind=True)
        assert got["kind"] == "draw_off" and got["to"] == rear
        assert BD._his_road(world, mack) is True

    def test_ahead_or_level_he_does_not_leave_his_ground(self, monkeypatch):
        world, ney, mack = _pair(his=40000, personality="cautious")
        monkeypatch.setattr(EnemyAI, "_find_retreat_destination", lambda self, m, n, w, **k: "Franche-Comte")
        assert self._word(world, mack, ney, behind=False)["kind"] == "dig_in"

    def test_the_day_he_opened_he_breaks_off(self):
        world, ney, mack = _pair(his=40000)
        assert self._word(world, mack, ney, opened=True)["kind"] == "break_off"

    def test_a_corps_beside_him_that_lifts_him_over_his_bar_is_brought_up_first(self):
        world, ney, mack = _pair(his=45000)
        beside = next(r for r in world.get_region(mack.location).adjacent_regions
                      if r != ney.location)
        world.marshals["Hohenlohe"] = _mk("Hohenlohe", beside, 30000, nation="Austria")
        got = self._word(world, mack, ney)
        assert got["kind"] == "bring_up" and got["who"] == "Hohenlohe"
        assert got["action"] == {"marshal": "Hohenlohe", "action": "move", "target": mack.location}
        world.marshals["Hohenlohe"].strength = 5000         # would not lift him: he is not called
        assert self._word(world, mack, ney)["kind"] == "dig_in"

    def test_his_purse_shut_he_stands(self, table, monkeypatch):
        monkeypatch.setattr(BD, "the_enemy_spends_his", lambda: False)
        _, day = table.open_a_day(_awaits_us, his=70000)
        assert day["theirs"] == 2, "he spent nothing"
        assert [t["kind"] for t in day["told"] if t["who"] == "theirs"] == ["stand"]

    def test_through_the_server_he_strikes_back_and_pays_a_point(self, table):
        want = lambda d: _awaits_us(d) and (d.get("reply") or {}).get("kind") == "strike"   # noqa: E731
        body, day = table.open_a_day(want, his=70000, his_personality="aggressive")
        assert day["theirs"] == 1 and isinstance(day["reply"].get("diorama"), dict)
        assert day["reply"]["diorama"]["day"]["enemy"] == "Mack", "his clash's tableau carries the day"
        # Our own tableau, with his clash to follow it, offers nothing yet:
        # the live chips ride HIS tableau (and the top-level block).
        ours_then = body["battle_diorama"]["day"]
        assert ours_then["follows"] is True and ours_then["chips"] == []
        assert day["chips"] and day["reply"]["diorama"]["day"]["chips"]
        assert "follows" not in day and "follows" not in day["reply"]["diorama"]["day"]
        assert "diorama" not in (body["battle_diorama"]["day"].get("reply") or {}), "never a tableau in a tableau"

    def _his_rear(self, world, holder):
        """Every province beside the field held by `holder` but the one we
        came from (ours)."""
        rear = [n for n in world.get_region(FIELD).adjacent_regions if n != HOME]
        for name in rear:
            world.get_region(name).controller = holder
        return rear

    def test_through_the_server_he_draws_off_and_the_day_is_over(self, table):
        """The Archduke slips away — when a road lies open to his own soil."""
        for _ in range(40):
            _seat(table.world, ours=85000, his=45000, his_personality="cautious")
            rear = self._his_rear(table.world, "Austria")
            table.world.clear_turn_battles()
            day = table.order("Ney, attack Mack").get("battle_day")
            if day and day.get("ended") == "drew_off":
                break
        else:
            raise AssertionError("he never drew off")
        assert day["open"] is False and day["ahead"] == "ours"
        assert _how(day)["line"].startswith("Mack draws off toward ")
        assert day["banner"] == "Mack draws off"
        assert table.world.battle_days == {}
        assert table.world.marshals["Mack"].location in rear

    def test_through_the_server_surrounded_he_stands_and_can_be_taken(self, table):
        """Mack at Ulm: beaten on points with nothing but France behind him he
        does not leave — the day stays open, and the word is ours."""
        for _ in range(40):
            _seat(table.world, ours=85000, his=45000, his_personality="cautious")
            self._his_rear(table.world, "France")
            table.world.clear_turn_battles()
            day = table.order("Ney, attack Mack").get("battle_day")
            if day and day.get("ahead") == "ours":
                break
        else:
            raise AssertionError("no morning won on points")
        assert day["open"] is True and day["awaits"] == "ours", day.get("told")
        assert day["his_road"] is False
        assert table.world.marshals["Mack"].location in (FIELD, HOME) and _chip(day, "press")["ok"]


# ════════════════════════════════════════════════════════
# 5. Silence, night, leaving the field
# ════════════════════════════════════════════════════════

class TestSilenceIsStanding:

    def test_two_silences_in_a_row_and_night_falls(self, table):
        table.open_a_day(_awaits_us)
        table.world.battle_days["days"]["Mack"]["theirs"] = 0       # he has nothing left to say
        body = table.word("stand")
        assert body["success"] and body["battle_day"]["open"] is False
        assert body["battle_day"]["ended"] == "night" and body["battle_day"]["banner"] == "Night falls"
        assert _how(body["battle_day"])["line"] == BD.NIGHT
        # BA-4: then what the day came to; BA-5: then whom the toll favoured and its shape,
        # and (the second reading) what follows a day no clash decided
        assert [t["kind"] for t in body["battle_day"]["told"][-3:]] == ["tally", "shape", "after"]
        assert table.world.battle_days == {} and table.world.actions_remaining == 3

    def test_a_priced_word_breaks_the_silence(self, table):
        """Two silences IN A ROW: a priced word between them starts the count
        again. (The review, BA3-X20: the first cut asserted inside a branch
        its board never took — the count could stop being reset and nothing
        went red.) One silence already stands and he has nothing left to say:
        our press is priced, so his stand after it is the FIRST silence again
        and the day goes on."""
        for _ in range(12):
            table.open_a_day(_awaits_us)
            store = table.world.battle_days["days"]["Mack"]
            store["silences"], store["theirs"] = 1, 0
            day = table.order("Ney, attack Mack")["battle_day"]
            if day["ended"] != "decided":
                break
        else:
            raise AssertionError("every press decided the day")
        assert day["open"] is True and day["awaits"] == "ours", day
        # (Row BA, BA-5: the press's own clash is told between the two.)
        assert [t["kind"] for t in day["told"] if t["kind"] != "clash"][-2:] == ["press", "stand"]
        assert table.world.battle_days["days"]["Mack"]["silences"] == 1

    def test_both_purses_empty_and_night_falls(self, table):
        table.open_a_day(_awaits_us)
        store = table.world.battle_days["days"]["Mack"]
        store["ours"], store["theirs"] = 1, 0
        body = table.order("Ney, attack Mack")
        said = body["battle_day"]
        assert said["open"] is False and said["ended"] in ("night", "decided")
        if said["ended"] == "night":
            assert (said["ours"], said["theirs"]) == (0, 0)

    def test_we_break_off_a_day_we_opened(self, table):
        table.open_a_day(_awaits_us)
        body = table.word("break_off")
        assert body["success"] and body["battle_day"]["ended"] == "broke_off"
        assert body["action_info"]["cost"] == 0 and table.world.battle_days == {}

    def test_a_word_with_no_day_is_refused(self, table):
        _seat(table.world)
        assert table.word("stand")["success"] is False
        table.open_a_day(_awaits_us)
        assert table.word("charge the moon")["success"] is False
        assert "Mack" in table.world.battle_days["days"], "a refusal closes nothing"


# ════════════════════════════════════════════════════════
# 6. The marshal's counsel and his answer
# ════════════════════════════════════════════════════════

class TestTheObjectionRoadStands:
    """An aggressive lead ordered to dig in objects, as he always has; the
    question is answered on the day's account."""

    def test_the_chip_says_he_may_object(self, table):
        _, day = table.open_a_day(_awaits_us)
        assert _chip(day, "dig_in")["counsel"] == "possible"
        assert _chip(day, "press")["counsel"] == "none"

    def test_the_word_is_parked_then_paid_for_in_points(self, table):
        _, day = table.open_a_day(_awaits_us)
        asked = table.order("Ney, defend")
        assert asked.get("state") == "awaiting_player_choice", asked.get("message")
        parked = asked["battle_day"]
        assert parked["pending"] is True and parked["chips"] == [] and parked["ours"] == day["ours"]
        assert table.world.actions_remaining == 3
        assert set(_every_pool(asked)) == {3}, "the question's counter is the pool, not the lend"
        answered = table.answer("insist")
        assert answered["success"], answered.get("message")
        assert answered["action_info"]["cost"] == 0 and table.world.actions_remaining == 3
        assert set(_every_pool(answered)) == {3}
        said = answered["battle_day"]
        assert said["pending"] is False and said["ours"] == day["ours"] - 1
        assert any(t["who"] == "ours" and t["kind"] == "dig_in" for t in said["told"])


# ════════════════════════════════════════════════════════
# 7. The Guard (NP-D1)
# ════════════════════════════════════════════════════════

def _emperor():
    return _mk("Napoleon", HOME, 30000, personality="sovereign", command=10)


class TestTheGuard:

    def test_the_two_numbers_are_the_users(self):
        assert (BD.GUARD_SHOCK, BD.GUARD_RECOIL) == (10, 10)
        assert BD.PRICES["guard"] == 2

    def test_the_guard_is_the_sovereign_leading_and_asks_two_points(self, table):
        _, day = table.open_a_day(_awaits_us, extra=(_emperor(),))
        guard = _chip(day, "guard")
        assert guard["label"] == "The Guard" and guard["price"] == 2
        assert guard["command"] == "Napoleon, attack Mack"
        body = table.order("Napoleon, attack Mack")
        assert body["success"], body.get("message")
        assert body["action_info"]["cost"] == 0 and table.world.actions_remaining == 3
        told = body["battle_day"]["told"]
        assert any(t["kind"] == "guard" and t["line"] == "The Guard goes in." for t in told)

    def test_two_points_or_the_chip_is_dim(self, table):
        _, day = table.open_a_day(_awaits_us, extra=(_emperor(),))
        table.world.battle_days["days"]["Mack"]["ours"] = 1
        guard = _chip(table.days()["days"][0], "guard")
        assert guard["ok"] is False and guard["why"] == "That asks 2 points; 1 is left."

    def test_with_the_seam_down_the_sovereign_is_another_corps(self, table, monkeypatch):
        monkeypatch.setattr(BD, "the_guard_goes_in", lambda: False)
        _, day = table.open_a_day(_awaits_us, extra=(_emperor(),))
        assert _chip(day, "guard") is None
        assert any(c["kind"] == "lead" and c["marshal"] == "Napoleon" and c["price"] == 1
                   for c in day["chips"])

    def _ctx(self, outcome="stalemate", forced=False):
        foe = _mk("Mack", FIELD, 50000, nation="Austria")
        nap, ney = _emperor(), _mk("Ney", HOME, 40000)
        gone = _mk("Lannes", HOME, 0)
        for corps in (foe, nap, ney, gone):
            corps.morale = 80
        ctx = SimpleNamespace(
            marshal=nap, enemy_marshal=foe, atk_participants=[nap, ney, gone],
            battle_result={"outcome": outcome, "attacker": {"forced_retreat": forced}})
        return ctx, foe, nap, ney, gone

    def test_as_it_goes_in_his_lead_loses_heart_once(self):
        ctx, foe, *_ = self._ctx()
        word = {"key": "Mack", "kind": "guard", "who": "ours", "price": 2}
        token = BD._WORD.set(word)
        try:
            BD.guard_shock(ctx)
            BD.guard_shock(ctx)
        finally:
            BD._WORD.reset(token)
        assert foe.morale == 70

    def test_no_shock_for_any_other_attack(self, monkeypatch):
        ctx, foe, *_ = self._ctx()
        BD.guard_shock(ctx)                                          # no word at all
        for word in ({"key": "Mack", "kind": "press", "who": "ours"},
                     {"key": "Mack", "kind": "strike", "who": "theirs"}):
            token = BD._WORD.set(word)
            try:
                BD.guard_shock(ctx)
            finally:
                BD._WORD.reset(token)
        assert foe.morale == 80
        monkeypatch.setattr(BD, "the_guards_numbers_bite", lambda: False)
        token = BD._WORD.set({"key": "Mack", "kind": "guard", "who": "ours"})
        try:
            BD.guard_shock(ctx)
        finally:
            BD._WORD.reset(token)
        assert foe.morale == 80

    def test_an_enemy_sovereigns_guard_is_the_same_guard(self):
        """Golden Rule 5: an authored enemy sovereign inherits the kit — his
        renewed assault is the Guard, with the same two numbers, on his side."""
        ctx, foe, nap, ney, gone = self._ctx("defender_victory")
        word = {"key": "Mack", "kind": "guard", "who": "theirs"}
        token = BD._WORD.set(word)
        try:
            BD.guard_shock(ctx)
        finally:
            BD._WORD.reset(token)
        assert foe.morale == 70, "the lead his Guard falls on loses heart"
        assert BD._guard_recoil(ctx, word) is True
        assert (nap.morale, ney.morale) == (70, 70), "thrown back, his own side's corps lose heart"

    def test_a_sovereign_strikes_only_as_the_guard(self):
        """His strike asks the Guard's two points: with one left he does not
        strike — as the player's own chip is dim with one point."""
        world, ney, mack = _pair(his=70000)                    # the odds are his
        ai = EnemyAI(CommandExecutor())
        base = dict(opened=False, behind=False, rng=_Fixed(1.0))
        with contextlib.redirect_stdout(io.StringIO()):
            assert ai.the_days_word(mack, ney, world, purse=1, strike_price=2, **base)["kind"] != "strike"
            assert ai.the_days_word(mack, ney, world, purse=2, strike_price=2, **base)["kind"] == "strike"
            assert ai.the_days_word(mack, ney, world, purse=1, **base)["kind"] == "strike"

    def test_the_emperor_left_to_it_with_one_point_does_not_go_in(self, table):
        for _ in range(40):
            _seat(table.world, extra=(_emperor(),))
            table.world.clear_turn_battles()
            body = table.order("Napoleon, attack Mack")
            day = body.get("battle_day")
            if day and _awaits_us(day) and day["lead"] == "Napoleon":
                break
        else:
            raise AssertionError("no day opened under the Emperor")
        assert day["ours"] == 3, "command 10: three points"
        table.world.battle_days["days"]["Mack"]["ours"] = 1
        said = table.word("leave_it")["battle_day"]
        ours = [t["kind"] for t in said["told"] if t["who"] == "ours"]
        assert "guard" not in ours and "press" not in ours, ours

    @pytest.mark.parametrize("outcome,forced,thrown", [
        ("defender_victory", False, True), ("defender_tactical_victory", False, True),
        ("stalemate", True, True), ("stalemate", False, False),
        ("attacker_tactical_victory", False, False), ("attacker_victory", False, False),
    ])
    def test_thrown_back_every_corps_of_ours_that_fought_loses_heart(self, outcome, forced, thrown):
        ctx, foe, nap, ney, gone = self._ctx(outcome, forced)
        word = {"key": "Mack", "kind": "guard", "who": "ours"}
        assert BD._guard_recoil(ctx, word) is thrown
        expect = 70 if thrown else 80
        assert (nap.morale, ney.morale) == (expect, expect)
        assert gone.morale == 80 and foe.morale == 80, "a corps no longer under arms, and his, are untouched"


# ════════════════════════════════════════════════════════
# 8. "Leave it to him"
# ════════════════════════════════════════════════════════

class TestLeaveItToHim:

    def test_what_his_own_clash_left_to_ask_rides_the_answer(self, table, monkeypatch):
        """A town taken by the lead's own strike asks "plunder or secure": the
        question must reach the player with this answer, not block his next
        order unseen (`say` carries the clash's result; the endpoint copies the
        combat allowlist the interrupt roads use)."""
        table.open_a_day(_awaits_us)
        real = BD.leave_it

        def with_a_capture(world, key, game_state, executor, keep=False):
            said = real(world, key, game_state, executor, keep=keep)
            for row in said:
                if row.get("who") == "ours" and isinstance(row.get("_result"), dict) and row.get("diorama"):
                    row["_result"]["pending_capture_choice"] = True
                    row["_result"]["capture_data"] = {"region": "Lorraine"}
            return said

        monkeypatch.setattr(BD, "leave_it", with_a_capture)
        body = table.word("leave_it")
        if any(t["who"] == "ours" and t["kind"] in ("press", "guard") for t in body["battle_day"]["told"]):
            assert body.get("pending_capture_choice") is True
            assert body.get("capture_data") == {"region": "Lorraine"}
        assert "_carry" not in body and "_result" not in str(body.get("battle_day"))

    def test_the_lead_spends_what_is_left_and_the_day_ends(self, table):
        _, day = table.open_a_day(_awaits_us)
        body = table.word("leave_it")
        assert body["success"], body.get("message")
        said = body["battle_day"]
        assert said["open"] is False and said["ended"] in ("night", "decided", "drew_off", "broke_off")
        assert table.world.battle_days == {}
        assert table.world.actions_remaining == 3, "his own account, not the Emperor's"
        assert table.world.pending_objection is None, "he raises no objection against himself"
        assert body["action_info"]["cost"] == 0

    def test_with_the_seam_down_there_is_no_such_word(self, table, monkeypatch):
        monkeypatch.setattr(BD, "a_marshal_may_be_left_to_it", lambda: False)
        _, day = table.open_a_day(_awaits_us)
        assert _chip(day, word="leave_it") is None
        assert table.word("leave_it")["success"] is False


# ════════════════════════════════════════════════════════
# 9. Night at the turn's end; a defended day at dawn
# ════════════════════════════════════════════════════════

class TestNightAndDawn:

    def test_the_turns_end_closes_every_open_day(self, table):
        table.open_a_day(_awaits_us)
        ended = table.order("end turn")
        assert ended["success"], ended.get("message")
        assert table.world.battle_days == {}, "night fell; the bar was lifted at dawn"

    def test_night_is_told_on_his_last_clash(self, table):
        """He strikes in the night and the field stays undecided: his clash's
        tableau — the one the enemy phase's telling carries, and the client
        raises — reads "Night falls". It carried the day as it stood after the
        clash: still open, with no word to give."""
        night = []
        for _ in range(6):
            table.open_a_day(_awaits_us, his=66000, his_personality="aggressive")
            body = table.order("end turn")
            tables = _tableaux_with_a_day(body.get("enemy_phase") or {})
            for tableau in tables:
                assert tableau["day"]["open"] is False and tableau["day"]["chips"] == [], tableau["day"]
            assert body["pending_battle_days"] == []
            night = [t["day"] for t in tables if t["day"]["ended"] == "night"]
            if night:
                break
        assert night, "no night fell after a strike of his in six days"
        for day in night:
            assert day["banner"] == "Night falls" and _how(day)["line"] == BD.NIGHT

    def test_the_end_is_written_on_the_last_clash_only_when_no_clash_decided_it(self):
        world = WorldState()
        cv.serve_campaign(world)
        ney, mack = _seat(world)
        world.battle_days = {"days": {"Mack": {
            "enemy": "Mack", "lead": "Ney", "field": mack.location,
            "our_ground": ney.location, "his_ground": mack.location,
            "side": "attack", "ours": 2, "theirs": 1, "awaits": "theirs", "silences": 1, "words": 1,
            "turn": 1, "offered": True, "read": {"ahead": "even", "our_loss": 0, "his_loss": 0}}}}
        stale = {"open": True, "enemy": "Mack", "awaits": "ours", "chips": []}
        first = {"battle_diorama": {"day": dict(stale)}}
        last = {"battle_diorama": {"day": dict(stale)}, "events": [{"diorama": {"day": dict(stale)}}, "a line"]}
        no_table = {"message": "Mack digs in."}
        BD._close(world, "Mack", "night", BD.NIGHT)
        BD._the_end_on_the_last(world, "Mack", [first, last, no_table])
        for tableau in (last["battle_diorama"], last["events"][0]["diorama"]):
            assert tableau["day"]["open"] is False and tableau["day"]["banner"] == "Night falls"
            assert _how(tableau["day"])["line"] == BD.NIGHT and "reply" not in tableau["day"]
        assert first["battle_diorama"]["day"] == stale, "only his LAST clash tells the end"
        # dawn: the closing block stands; the earlier clash's stale block goes
        phase = {"nations": {"Austria": {"actions": [first, last, no_table]}}}
        BD.dawn_on_the_tableaux(world, phase)
        assert "day" not in first["battle_diorama"]
        assert last["battle_diorama"]["day"]["banner"] == "Night falls"
        # a day a clash DECIDED keeps that clash's own block
        BD._CLOSED.setdefault(world, {})["Kienmayer"] = {"open": False, "ended": "decided", "enemy": "Kienmayer"}
        untouched = {"battle_diorama": {"day": dict(stale, enemy="Kienmayer")}}
        BD._the_end_on_the_last(world, "Kienmayer", [untouched])
        assert untouched["battle_diorama"]["day"]["open"] is True

    def test_night_bars_a_second_strike_for_the_phase_that_follows(self):
        world = WorldState()
        cv.serve_campaign(world)
        ney, mack = _seat(world)
        world.battle_days = {"days": {"Mack": {
            "enemy": "Mack", "lead": "Ney", "field": mack.location,
            "our_ground": ney.location, "his_ground": mack.location,
            "side": "attack", "ours": 2, "theirs": 0, "awaits": "ours", "silences": 0, "words": 0,
            "turn": 1, "offered": True, "read": {"ahead": "even", "our_loss": 0, "his_loss": 0}}}}
        with contextlib.redirect_stdout(io.StringIO()):
            said = BD.night_falls(world, {"world": world}, CommandExecutor())
        assert said == [] and BD.open_days(world) == {}
        assert BD.bars(world) == {("Mack", "Ney")}
        assert world.to_dict()["battle_days"] == {"days": {}, "barred": {"Mack": "Ney"}}
        BD.at_dawn(world)
        assert world.battle_days == {} and BD.bars(world) == set()

    def test_the_ai_reads_the_bar_into_its_own_pair_brake(self):
        import inspect
        src = inspect.getsource(EnemyAI)
        assert "self._attacked_targets_this_turn |= _battle_day.bars(world)" in src

    def test_a_great_battle_he_opens_against_us_awaits_us_at_dawn(self, table):
        for _ in range(30):
            _seat(table.world, ours=55000, his=70000, his_personality="aggressive")
            body = table.order("end turn")
            if table.world.battle_days.get("days"):
                break
        day = table.world.battle_days["days"]["Mack"]
        assert day["side"] == "defence" and day["lead"] == "Ney"
        assert day["awaits"] == "ours", "the side that did not open speaks first"
        assert day["offered"] is True
        notes = [n for n in body.get("notifications") or [] if n.get("type") == "battle_day_awaits"]
        assert len(notes) == 1 and notes[0]["title"].startswith("The day at ")
        live = table.days()["days"][0]
        assert _chip(live, "break_off")["label"] == "Fall back"
        assert _chip(live, "break_off")["command"] == "Ney, retreat"
        # On a day he opened the lead's own attack is his riposte.
        assert _chip(live, "press")["label"] == "Ney strikes back"
        assert _chip(live, word="break_off") is None, "a day we did not open is not ours to break off"
        # We answer first: the lead strikes back for a point, free of actions.
        left = table.world.actions_remaining
        struck = table.order("Ney, attack Mack")
        assert struck["success"], struck.get("message")
        assert struck["action_info"]["cost"] == 0 and table.world.actions_remaining == left
        assert any(t["who"] == "ours" and t["line"] == "Ney strikes back."
                   for t in struck["battle_day"]["told"]), struck["battle_day"]["told"]

    def test_the_table_that_rises_at_dawn_carries_the_days_chips(self, table):
        """The enemy phase's telling carries the battle's tableau, and the
        client raises it by itself when the list is left: at dawn that tableau
        reads the day as it stands — the chips `GET /battle_day` gives. Found
        in the real client: it rose with both purses and no word to give."""
        body = {}
        for _ in range(30):
            _seat(table.world, ours=55000, his=70000, his_personality="aggressive")
            body = table.order("end turn")
            if table.world.battle_days.get("days"):
                break
        live = table.days()["days"][0]
        want = [(c["kind"], c["label"], c["ok"]) for c in live["chips"]]
        assert want, "the day offers its words at dawn"
        tables = _tableaux_with_a_day(body.get("enemy_phase") or {})
        assert len(tables) >= 2, "the action's tableau and its event's"
        for tableau in tables:
            day = tableau["day"]
            assert day["open"] is True and day["awaits"] == "ours" and day["side"] == "defence"
            assert [(c["kind"], c["label"], c["ok"]) for c in day["chips"]] == want
        # quoting the chips at dawn left the new turn's pool as it found it
        assert body["action_summary"]["actions_remaining"] == table.world.actions_remaining
        assert table.world.actions_remaining == body["action_summary"]["max_actions"]

    def test_a_day_that_did_not_live_to_the_dawn_leaves_no_block_on_its_clash(self):
        world = WorldState()
        cv.serve_campaign(world)
        ney, mack = _seat(world)
        world.battle_days = {"days": {"Mack": {
            "enemy": "Mack", "lead": "Ney", "field": ney.location,
            "our_ground": ney.location, "his_ground": mack.location,
            "side": "defence", "ours": 2, "theirs": 2, "awaits": "ours", "silences": 0, "words": 0,
            "turn": 1, "offered": True, "read": {"ahead": "even", "our_loss": 0, "his_loss": 0}}}}
        stale = {"open": True, "enemy": "Mack", "awaits": "ours", "chips": []}
        gone = {"open": True, "enemy": "Kienmayer", "awaits": "ours", "chips": []}
        plain = {"kind": "battle"}
        phase = {"nations": {"Austria": {"actions": [
            {"battle_diorama": {"day": dict(stale)}, "events": [{"diorama": {"day": dict(stale)}}]},
            {"battle_diorama": {"day": dict(gone)}, "events": [{"diorama": plain}, "a line"]},
            "not an action"]}}}
        before = world.actions_remaining
        BD.dawn_on_the_tableaux(world, phase)
        first, second = phase["nations"]["Austria"]["actions"][:2]
        for tableau in (first["battle_diorama"], first["events"][0]["diorama"]):
            assert tableau["day"]["open"] is True and _chip(tableau["day"], "break_off")["label"] == "Fall back"
        assert first["battle_diorama"]["day"] is not first["events"][0]["diorama"]["day"]
        assert "day" not in second["battle_diorama"], "a day that is over is told as the battle it was"
        assert plain == {"kind": "battle"} and world.actions_remaining == before
        # off the served road nothing is touched
        bare = WorldState()
        untouched = {"nations": {"Austria": {"actions": [{"battle_diorama": {"day": dict(stale)}}]}}}
        BD.dawn_on_the_tableaux(bare, untouched)
        assert untouched["nations"]["Austria"]["actions"][0]["battle_diorama"]["day"] == stale
        BD.dawn_on_the_tableaux(world, None)

    def test_on_a_defended_day_we_may_fall_back_before_he_presses(self, table):
        for _ in range(30):
            _seat(table.world, ours=55000, his=70000, his_personality="aggressive")
            table.order("end turn")
            if table.world.battle_days.get("days"):
                break
        assert table.world.battle_days["days"]["Mack"]["side"] == "defence"
        was = table.world.marshals["Ney"].location
        left = table.world.actions_remaining
        body = table.order("Ney, retreat")
        assert body["success"], body.get("message")
        said = body["battle_day"]
        assert said["open"] is False and said["ended"] == "fell_back"
        assert _how(said)["line"] == "Ney falls back." and said["banner"] == "Ney falls back"
        assert table.world.marshals["Ney"].location != was
        assert table.world.battle_days == {} and table.world.actions_remaining == left

    def test_the_days_own_enemy_is_no_hidden_threat(self, table):
        """The enemy of an open day fought its lead this morning and the day's
        block names him: with the fog closed over his province "Fall back" is
        still lit, and taken. The fog-honest rule itself is not loosened — with
        no day against him the same hidden corps leaves the retreat dim
        (`state_probe._in_visible_danger`; found by the staged scene, whose
        chip read "not in danger — no retreat needed" under a day he opened)."""
        from backend.commands.state_probe import order_state_refusal
        from backend.models.intel import UNKNOWN
        for _ in range(30):
            _seat(table.world, ours=55000, his=70000, his_personality="aggressive")
            table.order("end turn")
            if table.world.battle_days.get("days"):
                break
        world = table.world
        assert world.battle_days["days"]["Mack"]["side"] == "defence"
        world.get_region_intel(world.marshals["Mack"].location).visibility = UNKNOWN
        assert "Mack" not in {m.name for m in world.get_visible_enemies("France")}
        fall = _chip(table.days()["days"][0], "break_off")
        assert fall["label"] == "Fall back" and fall["ok"] is True and fall["why"] == "", fall
        held = world.battle_days["days"].pop("Mack")
        assert order_state_refusal(world, world.marshals["Ney"], "retreat") == \
            "not in danger — no retreat needed", "a hidden corps that is no day's enemy is still a hidden threat"
        world.battle_days["days"]["Mack"] = held
        body = table.order("Ney, retreat")
        assert body["success"], body.get("message")
        assert body["battle_day"]["ended"] == "fell_back"


# ════════════════════════════════════════════════════════
# 10. The same save, the same day
# ════════════════════════════════════════════════════════

class TestTheSameSaveGivesTheSameDay:

    def _reading(self, body, world):
        day = body["battle_day"]
        return (day["open"], day["ours"], day["theirs"], day["ended"],
                [(t["who"], t["kind"]) for t in day["told"]],
                {n: (int(m.strength), int(m.morale), m.location) for n, m in sorted(world.marshals.items())})

    # A board on which his answer to our press hinges on his MOOD (his odds
    # sit on his temper's bar), and ambient streams that — were the mood drawn
    # from them — split it both ways. The review (BA3-X20): on the first cut's
    # board his answer did not turn on his mood, so with the temper's seam
    # held down the pin still held.
    HINGE = dict(his=62000, his_personality="literal")
    AMBIENTS = (1, 2, 3, 5, 77777)

    def _again_from_the_save(self, table, monkeypatch=None):
        table.open_a_day(_awaits_us, **self.HINGE)
        saved = _quiet(table.tc.post, "/save", json={"save_name": "ba3_the_day"}).json()
        assert saved["success"], saved.get("message")
        if monkeypatch is not None:
            monkeypatch.setattr(cv, "the_temper_is_seeded", lambda: False)
        seen = []
        for ambient in self.AMBIENTS:
            loaded = _quiet(table.tc.post, "/load", json={"filename": "ba3_the_day.json"}).json()
            assert loaded["success"], loaded.get("message")
            assert "Mack" in M.world.battle_days["days"], "the open day is in the save"
            random.seed(ambient)
            seen.append(self._reading(table.order("Ney, attack Mack"), M.world))
        return seen

    def test_a_word_given_again_from_the_save_meets_the_same_answer(self, table):
        seen = self._again_from_the_save(table)
        assert all(reading == seen[0] for reading in seen), seen

    def test_the_same_save_pin_can_fail(self, table, monkeypatch):
        """Held down, the same reloads under the same ambient streams meet
        MORE than one answer: the pin above is not blind."""
        seen = self._again_from_the_save(table, monkeypatch)
        assert any(reading != seen[0] for reading in seen), "the board no longer hinges on his mood"

    def test_his_mood_is_the_days_own_stream(self, monkeypatch):
        made = []
        real = cv._PrivateStream

        class Recording(real):
            def __init__(self, seed):
                made.append(str(seed))
                super().__init__(seed)

        monkeypatch.setattr(cv, "_PrivateStream", Recording)
        world = WorldState()
        world.campaign_seed = ROLLED
        cv.serve_campaign(world)
        day = {"enemy": "Mack", "lead": "Ney", "words": 2, "silences": 1}
        assert BD._day_rng(world, day, "theirs") is not None
        assert made[-1] == f"{ROLLED}|temper|{int(world.current_turn)}|day|Mack|Ney|theirs|2|1"


# ════════════════════════════════════════════════════════
# 11. Where it exists, and its switches
# ════════════════════════════════════════════════════════

def _fought_on(world):
    executor = CommandExecutor()
    with contextlib.redirect_stdout(io.StringIO()):
        return executor._execute_attack(world.marshals["Ney"], "Mack", world, {"world": world})


class TestOnlyACampaignTheServerHolds:

    def test_a_world_nobody_serves_has_no_day(self):
        """The measuring harnesses and the suite's own boards keep the game
        they pin: a great battle that hangs is one clash."""
        hung = 0
        for ambient in range(1, 25):
            world = WorldState()
            _seat(world)
            random.seed(ambient)
            result = _fought_on(world)
            tableau = result.get("battle_diorama") or {}
            if tableau.get("outcome") in BD.HANGING:
                hung += 1
            assert "day" not in tableau and world.battle_days == {}
        assert hung, "the board never hung: the pin proves nothing"

    def test_served_the_same_battle_opens_one(self):
        for ambient in range(1, 25):
            world = WorldState()
            world.campaign_seed = ROLLED
            cv.serve_campaign(world)
            _seat(world)
            random.seed(ambient)
            if "day" in (_fought_on(world).get("battle_diorama") or {}):
                assert "Mack" in world.battle_days["days"]
                return
        raise AssertionError("no day opened on a served board")

    def test_the_seam_down_is_the_game_before(self, table, monkeypatch):
        monkeypatch.setattr(BD, "the_day_has_points", lambda: False)
        for _ in range(6):
            _seat(table.world)
            table.world.clear_turn_battles()
            body = table.order("Ney, attack Mack")
            assert "battle_day" not in body and table.world.battle_days == {}
            assert body["action_info"]["cost"] == 1

    @pytest.mark.parametrize("seam", [
        "the_day_has_points", "the_enemy_spends_his", "the_guard_goes_in",
        "the_guards_numbers_bite", "a_marshal_may_be_left_to_it"])
    def test_every_switch_is_a_function_read_through_the_module(self, seam):
        assert callable(getattr(BD, seam)) and getattr(BD, seam)() is True

    def test_the_numbers_are_functions_too(self):
        assert (BD.points_low(), BD.points_high()) == (BD.POINTS, BD.POINTS_HIGH_COMMAND) == (2, 3)

    def test_the_prices(self):
        """Ruling 5: one point — press, another corps, a battery, a corps
        brought up, digging in; two — the Guard; nothing — to stand, to leave."""
        assert BD.PRICES == {
            "press": 1, "lead": 1, "cannonade": 1, "bring_up": 1, "dig_in": 1,
            "guard": 2, "stand": 0, "break_off": 0, "strike": 1, "draw_off": 0}


class TestTheStoreIsSavedOnlyWhenItHoldsSomething:

    def test_empty_it_is_not_in_a_save_and_an_old_save_reads_none(self):
        world = WorldState()
        data = world.to_dict()
        assert world.battle_days == {} and "battle_days" not in data
        assert WorldState.from_dict(data).battle_days == {}

    def test_an_open_day_goes_round_a_save(self):
        world = WorldState()
        world.battle_days = {"days": {"Mack": {"enemy": "Mack", "lead": "Ney", "ours": 1, "theirs": 2,
                                               "told": [{"who": "ours", "kind": "press", "line": "x"}]}}}
        data = world.to_dict()
        assert data["battle_days"] == world.battle_days
        data["battle_days"]["days"]["Mack"]["ours"] = 9
        assert world.battle_days["days"]["Mack"]["ours"] == 1, "the save is a copy"
        back = WorldState.from_dict(world.to_dict())
        assert back.battle_days == world.battle_days and back.battle_days is not world.battle_days

    def test_a_malformed_key_reads_none(self):
        data = WorldState().to_dict()
        data["battle_days"] = ["not", "a", "store"]
        assert WorldState.from_dict(data).battle_days == {}


# ════════════════════════════════════════════════════════
# 12. The wire
# ════════════════════════════════════════════════════════

class TestTheWire:

    def test_the_open_days_are_listed_live(self, table):
        assert table.days() == {"success": True, "days": []}
        table.open_a_day(_awaits_us)
        listed = table.days()["days"]
        assert [d["enemy"] for d in listed] == ["Mack"] and listed[0]["chips"]

    def test_the_province_panels_one_get_carries_the_day(self, table):
        table.open_a_day(_awaits_us)
        field = table.world.battle_days["days"]["Mack"]["field"]
        quoted = _quiet(table.tc.get, "/march_quotes", params={"region": field}).json()
        assert quoted["day"]["enemy"] == "Mack" and "reply_diorama" not in quoted["day"]
        other = _quiet(table.tc.get, "/march_quotes", params={"region": HOME}).json()
        assert "day" not in other or field == HOME

    def test_a_word_costs_no_action_on_the_wire(self, table):
        table.open_a_day(_awaits_us)
        body = table.word("stand")
        assert body["action_info"] == {"cost": 0, "remaining": 3, "turn_advanced": False, "new_turn": None}

    def test_a_day_whose_corps_has_gone_is_dropped(self, table):
        table.open_a_day(_awaits_us)
        table.world.marshals["Mack"].location = HOME + "-elsewhere"
        assert table.days()["days"] == [] and table.world.battle_days == {}

    def test_the_script_is_told_the_word_this_clash_is(self, table):
        """`battle_script_facts` carries `day_word` for a later clash of a day
        and for no other battle."""
        from backend.commands import combat_executor as CE
        seen = []
        real = CE.battle_script_facts

        def spy(ctx):
            facts = real(ctx)
            seen.append(facts.get("day_word"))
            return facts

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(CE, "battle_script_facts", spy)
            table.open_a_day(_awaits_us)
            assert seen[0] is None, "an opening clash is no word"
            del seen[:]
            table.order("Ney, attack Mack")
        assert seen and seen[0] == {"who": "ours", "kind": "press", "line": "Ney presses the attack."}


# ════════════════════════════════════════════════════════
# 13. The gate's measurement is on record
# ════════════════════════════════════════════════════════

class TestTheGatesMeasurementIsOnRecord:
    """`BATTLE_DIORAMA_SPEC.md` §15.14's table, counted again from the rows
    the probes printed (`docs/audits/ba3/hinge_probe_2026_11_15.json`)."""

    def _record(self):
        import json
        from pathlib import Path
        path = Path(__file__).resolve().parents[1] / "docs" / "audits" / "ba3" / "hinge_probe_2026_11_15.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_one_battle_in_four_is_great_and_seven_great_days_hang(self):
        record = self._record()
        rows = [r for seed in ("austerlitz", "marengo") for r in record["probes"]["hinge_probe3"][seed]]
        attacks = [r for r in rows if r["side"] == "attacker"]
        hung = [r for r in rows if r["hung"]]
        great = [r for r in rows if r["great"]]
        assert (len(rows), len(attacks), len(rows) - len(attacks)) == (47, 12, 35)
        assert (len(hung), sum(1 for r in hung if r["side"] == "attacker")) == (27, 6)
        assert len(great) == 11 and sum(1 for r in great if r["hung"]) == 7
        assert sum(1 for r in great if r["hung"] and r["side"] == "attacker") == 4
        assert sum(1 for r in rows if r["capital"]) == 31, "the meaning of `key` that was set aside"
        assert record["headline"]["great_hung"] == 7 and record["headline"]["battles"] == 47


class TestAQuoteSaysAWordsPrice:
    """BA3-X5 (FIXED by row BA's session BA-4, November 16, 2026). While a day was open the
    day's own chips — the table, the head of the province's panel, the log —
    price a word in points. The surfaces that quote the SAME order outside
    them (the attack card, the plan's "Bring up" rows, the relay's note, the
    province's ordinary attack row, the readback) still say "1 action", and
    the order then takes a point and no action. Found by the suite: CRT-11's
    relay pin read the pool after "Soult, support Ney" on a day that hung."""

    def test_the_card_forecasts_no_new_day_while_one_is_open(self, table):
        """Fixed in BA-3: the forecast ("A great battle — Ney commands the
        day: 2 points") is for a battle that would OPEN a day."""
        from backend.commands import order_quotes as Q
        world = table.world
        ney, mack = _seat(world, ours=62000, his=60000)
        before = Q.attack_quote(world, ney, mack)
        assert before.get("day", {}).get("great") is True, "a great battle is forecast before the order"
        table.open_a_day(_awaits_us, ours=62000, his=60000)
        world = table.world
        during = Q.attack_quote(world, world.marshals["Ney"], world.marshals["Mack"])
        assert "day" not in during

    def test_the_attack_quote_prices_a_word_in_points(self, table):
        """FIXED November 16, 2026 (row BA's session BA-4): one source for a
        word's price on every surface — `tests/test_ba4_the_roads_and_the_fog.py`."""
        from backend.commands import order_quotes as Q
        table.open_a_day(_awaits_us)
        world = table.world
        quote = Q.attack_quote(world, world.marshals["Ney"], world.marshals["Mack"])
        left = world.actions_remaining
        sent = table.order(quote["command"])
        assert sent["success"] and table.world.actions_remaining == left, "the order is a word: no action"
        assert quote["ap"] == 0, "and its quote says so"


class TestTheRecordsSayWhatLanded:
    """BA2-X19's sibling for this session: `STATUS.md` ▶ NEXT UP is read
    first, every session, and its head must not name a landed session as the
    one to come (it still ended "next BA-3 the rounds" at the stop)."""

    def test_the_head_of_status_names_the_day_as_landed(self):
        from tests._ledgers import doc_text
        head = next(line for line in doc_text("STATUS.md").splitlines()
                    if line.startswith("> **▶ NEXT ="))
        assert "next BA-3 the rounds" not in head
        assert "ROW BA, BA-3 ✅ LANDED November 16, 2026" in head

    def test_the_ledger_holds_the_sessions_rows(self):
        import re
        from tests._ledgers import doc_text
        rows = re.findall(r"^\| \*\*(BA3-X\d+)\*\* \| P\d \| (✅ FIXED|OPEN) ",
                          doc_text("BUG_FIXES.md"), flags=re.M)
        fixed = "✅ FIXED"
        # Every row is closed since row BA's session BA-4 (November 16, 2026):
        # X2, X5 and the four its review filed for BA-4 (X13 to X16) landed there.
        assert rows == [(f"BA3-X{n}", fixed) for n in range(1, 23)]

    def test_the_sweep_of_record_reads_the_gate(self):
        """The eight-seed sweep (`BATTLE_DIORAMA_SPEC.md` §15.16): every new
        seam down reproduces 26 / 27 / 28, and the commanded arms as they run
        — silent on a day — read 28 / 27 / 27."""
        import json
        from pathlib import Path
        sweep = json.loads((Path(__file__).resolve().parents[1] / "tools"
                            / "_ba3_sweep_2026_11_15.json").read_text(encoding="utf-8"))

        def band(arm):
            return [sweep["arms"][arm][seed]["provinces"] for seed in ("CMD-H", "CMD-A", "CMD-M")]

        assert band("0") == [26, 27, 28] and band("S") == [28, 27, 27]
        assert all(23 <= n <= 28 for n in band("S"))


class TestADayOpenedByAnotherRoad:
    """The command road and the objection's answer settle a day at once. An
    attack that reaches the executor past them (an interrupt's answer, a
    charge) opens a day that awaits HIM with nothing said: the table's own
    read — `GET /battle_day` — lets him answer (`battle_day.caught_up`)."""

    def _opened_past_the_door(self, table):
        for _ in range(40):
            _seat(table.world)
            table.world.clear_turn_battles()
            with contextlib.redirect_stdout(io.StringIO()):
                M.executor._execute_attack(
                    table.world.marshals["Ney"], "Mack", table.world, M.game_state)
            if table.world.battle_days.get("days"):
                return table.world.battle_days["days"]["Mack"]
        raise AssertionError("no day opened")

    def test_it_awaits_him_until_the_table_asks(self, table):
        day = self._opened_past_the_door(table)
        # (Row BA, BA-5: the opening's own line is told; no word has been.)
        assert day["awaits"] == "theirs"
        assert [t["kind"] for t in day.get("told") or []] == ["clash"]
        listed = table.days()["days"]
        assert [d["enemy"] for d in listed] == ["Mack"]
        assert listed[0]["open"] is False or listed[0]["awaits"] == "ours"
        assert any(t["who"] in ("theirs", "end") for t in listed[0]["told"]), "he has spoken"

    def test_the_province_panels_read_does_not_answer_for_him(self, table):
        day = self._opened_past_the_door(table)
        field = day["field"]
        _quiet(table.tc.get, "/march_quotes", params={"region": field})
        assert table.world.battle_days["days"]["Mack"]["awaits"] == "theirs"


class TestTheTablesReadHoldsTheLock:
    """The chips are quoted with the word's lend on the pool, stamped and put
    back (`battle_day.lending`). A read that crossed a command could leave the
    lend there for good — WS-6's class — so the read takes the state lock a
    POST takes, and the pool is as it was when it returns."""

    def test_the_read_is_a_locked_read(self):
        assert "/battle_day" in M._LOCKED_READS and "/march_quotes" in M._LOCKED_READS

    def test_the_offer_leaves_the_pool_as_it_found_it(self, table):
        table.open_a_day(_awaits_us)
        left = table.world.actions_remaining
        for _ in range(3):
            assert table.days()["days"][0]["chips"]
            field = table.world.battle_days["days"]["Mack"]["field"]
            _quiet(table.tc.get, "/march_quotes", params={"region": field})
        assert table.world.actions_remaining == left
        assert cv.lent_now() == 0

    def test_a_read_that_lets_him_answer_moves_the_epoch(self, table):
        for _ in range(40):
            _seat(table.world)
            table.world.clear_turn_battles()
            with contextlib.redirect_stdout(io.StringIO()):
                M.executor._execute_attack(
                    table.world.marshals["Ney"], "Mack", table.world, M.game_state)
            if table.world.battle_days.get("days"):
                break
        assert BD.awaits_him(table.world)
        before = M._STATE_EPOCH if hasattr(M, "_STATE_EPOCH") else None
        table.days()
        assert not BD.awaits_him(table.world)
        if before is not None:
            assert M._STATE_EPOCH != before
        quiet = M._STATE_EPOCH if hasattr(M, "_STATE_EPOCH") else None
        table.days()                                  # nothing owed: a plain read
        if quiet is not None:
            assert M._STATE_EPOCH == quiet


class TestAWordBehindTheMarshalsOwnQuestion:
    """A press at bad odds raises the muster's "Commit the Attack?" — a
    question of the marshal's own, answered on another road
    (`/strategic_response`). The day must not end for being asked, and the
    answer is the word: paid in points, never an action."""

    def _asked(self, table):
        _, day = table.open_a_day(_awaits_us, his_personality="cautious")
        table.world.marshals["Ney"].strength = 14000
        table.world.marshals["Mack"].strength = 70000
        body = table.order("Ney, attack Mack")
        asking = table.world.marshals["Ney"].pending_interrupt
        assert asking and asking["interrupt_type"] == "muster_confirm", body.get("message")
        return day, body, asking

    def _answer(self, table, asking, choice):
        return _quiet(table.tc.post, "/strategic_response", json={
            "marshal_name": asking["marshal"], "response_type": asking["interrupt_type"],
            "choice": choice}).json()

    def test_the_day_waits_for_the_answer(self, table):
        day, body, _ = self._asked(table)
        parked = body["battle_day"]
        assert parked["open"] is True and parked["pending"] is True and parked["chips"] == []
        assert parked["ours"] == day["ours"] and table.world.actions_remaining == 3
        assert "Mack" in table.world.battle_days["days"], "a question does not end the day"
        # Found in the real client, whose counter is `action_summary`: the
        # executor wrote it with the word's lend still on the pool (6 of 4).
        assert set(_every_pool(body)) == {3}, _every_pool(body)

    def test_commit_the_attack_is_the_word_and_costs_a_point(self, table):
        day, _, asking = self._asked(table)
        answered = self._answer(table, asking, "attack_anyway")
        assert answered["success"], answered.get("message")
        assert answered["action_info"]["cost"] == 0 and table.world.actions_remaining == 3
        assert set(_every_pool(answered)) == {3}, _every_pool(answered)   # it read 5 of 4
        said = answered["battle_day"]
        assert said["ours"] == day["ours"] - 1 and said["pending"] is False
        assert any(t["who"] == "ours" and t["kind"] == "press" for t in said["told"])
        assert isinstance(answered.get("battle_diorama"), dict), "the clash is shown"

    def test_cancel_the_order_and_nothing_is_paid(self, table):
        day, _, asking = self._asked(table)
        answered = self._answer(table, asking, "cancel_order")
        assert table.world.actions_remaining == 3
        live = table.days()["days"][0]
        assert live["ours"] == day["ours"] and live["pending"] is False and live["chips"]
        assert answered.get("success") is not None


class TestAParkedWordIsTiedToItsOwnQuestion:

    def _world(self, **kw):
        world = SimpleNamespace(pending_objection=None, pending_strategic_objection=None,
                                get_marshal=lambda name: SimpleNamespace(pending_interrupt=None))
        for key, value in kw.items():
            setattr(world, key, value)
        return world

    def test_the_questioner_is_read_on_both_roads(self):
        assert BD.questioner(self._world()) is None
        assert BD.questioner(self._world(pending_objection={"marshal": "Ney"})) == "Ney"
        assert BD.questioner(self._world(
            pending_strategic_objection={"marshal_name": "Davout"})) == "Davout"

    def test_another_marshals_objection_parks_nothing(self):
        word = {"marshal": "Ney", "kind": "press", "price": 1}
        assert BD._asked(self._world(pending_objection={"marshal": "Ney"}), word, {}) is True
        assert BD._asked(self._world(pending_objection={"marshal": "Davout"}), word, {}) is False
        assert BD._asked(self._world(
            pending_strategic_objection={"marshal_name": "Ney"}), word, {}) is True
        asking = self._world(get_marshal=lambda name: SimpleNamespace(
            pending_interrupt={"interrupt_type": "muster_confirm"}))
        assert BD._asked(asking, word, {}) is True
        assert BD._asked(self._world(), {"kind": "press"}, {}) is False

    def test_an_unrelated_objection_on_the_board_takes_no_point(self, table):
        _, day = table.open_a_day(_awaits_us)
        table.world.pending_objection = {"marshal": "Davout", "original_order": {"action": "attack"}}
        before = table.world.battle_days["days"]["Mack"]["ours"]
        table.order("Ney, attack Mack")
        store = table.world.battle_days.get("days", {}).get("Mack")
        if store is not None:
            assert not store.get("pending"), "the word is not parked behind Davout's question"
            assert store["ours"] in (before, before - 1)
        table.world.pending_objection = None


class TestWhatTheFieldShowsOfHim:
    """His temper (the plinth already wears it) and whether a road is open
    behind him — never his odds, his bar or his mood."""

    def test_the_block_names_his_temper_and_his_road(self, table):
        _, day = table.open_a_day(_awaits_us, his_personality="cautious")
        assert day["his_temper"] == "Cautious"
        assert day["his_road"] in (True, False)
        for leak in ("ratio", "bar", "odds_his", "threshold", "mood"):
            assert leak not in day

    def test_no_road_is_named_on_a_day_he_opened(self, table):
        for _ in range(30):
            _seat(table.world, ours=55000, his=70000, his_personality="aggressive")
            table.order("end turn")
            if table.world.battle_days.get("days"):
                break
        live = table.days()["days"][0]
        assert live["side"] == "defence" and live["his_road"] is None
        assert live["his_temper"] == "Aggressive"

    def test_his_road_is_read_without_a_draw(self, table, monkeypatch):
        """The read is on every block: it must move no stream."""
        from backend.ai import enemy_ai
        table.open_a_day(_awaits_us)
        drew = []
        monkeypatch.setattr(enemy_ai, "ai_rng", lambda *a, **k: drew.append(a) or random)
        state = random.getstate()
        assert table.days()["days"][0]["his_road"] in (True, False)
        assert drew == [] and random.getstate() == state

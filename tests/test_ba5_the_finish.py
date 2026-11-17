"""Row BA, session BA-5 — "the finish": BA-4's open readings ruled, and the
day of battle made to tell itself.

The user's word (November 16, 2026, after BA-4's commit and push): "AFTER
COMMITTING PUSHING MAKE THESE RULLINGS AND MAKE SURE THIS FEATURE ROCKS DONT
FEAR DEEPR ESERWARCH ETC" — planned in Plan Mode and approved, with four ticks
at its gate (`docs/BATTLE_DIORAMA_SPEC.md` §15.22).

What this file pins, by behaviour, through the game server:

* the six defects of what had landed, each by a test that failed before its
  fix (two blind readers of the table's frames found them; each was confirmed
  in the code before a line changed);
* the telling: what each word does, Berthier's reading of him, the day so far,
  what told, the close and its shape;
* the reserve that pursues a beaten enemy, behind its seam;
* the extras ticked at the gate.
"""

import contextlib
import io
import random
import re
from types import SimpleNamespace

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.game_logic import battle_day as BD
from backend.game_logic import battle_telling as T
from tests.test_ba3_the_rounds import (  # noqa: F401  (the fixture rides the import)
    Table,
    _awaits_us,
    _chip,
    _Fixed,
    _mk,
    _pair,
    _seat,
    table,
)
from tests.test_pc_rulings import _kill_hope, _truce, vienna_held  # noqa: F401  (a fixture)


def _figures(line):
    """Every figure a told line carries, as integers ("6,805 of ours" -> 6805)."""
    return [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", str(line or ""))]


def _toll_of(tableau):
    """(ours, his) — the losses the table's own counters show for the clash on
    it, by the side the player stands on."""
    sides = [tableau.get("attacker") or {}, tableau.get("defender") or {}]
    ours = next(s for s in sides if s.get("nation") == "France")
    his = next(s for s in sides if s.get("nation") != "France")
    return int(ours.get("casualties_total", 0)), int(his.get("casualties_total", 0))


def _struck_back(day):
    return _awaits_us(day) and (day.get("reply") or {}).get("kind") == "strike"


# ════════════════════════════════════════════════════════
# A. The defects
# ════════════════════════════════════════════════════════

class TestD1OurOwnClashsTableDoesNotTellHisAnswer:
    """D1 — `battle_day.settle` wrote onto OUR clash's tableau the day as it
    stood AFTER his answering clash: the line under the title told his clash's
    result ("The last clash: drawn — 4,001 …") over our clash's own counters,
    his purse already read a point short and his word was already told — all
    before the player pressed "His answer"."""

    def _a_clash_followed_by_his(self, table):
        return table.open_a_day(_struck_back, his=70000, his_personality="aggressive")

    def test_his_purse_is_whole_on_the_table_of_our_clash(self, table):
        body, day = self._a_clash_followed_by_his(table)
        ours_then = body["battle_diorama"]["day"]
        assert day["theirs"] == day["theirs_of"] - 1, "he struck: a point spent"
        assert ours_then["theirs"] == ours_then["theirs_of"], (
            "our clash's table reads the day as it stood when our clash ended — he had not spoken")

    def test_no_word_of_his_is_told_on_the_table_of_our_clash(self, table):
        body, day = self._a_clash_followed_by_his(table)
        ours_then = body["battle_diorama"]["day"]
        assert any(t["who"] == "theirs" for t in day["told"]), "the live day tells his word"
        assert not any(t["who"] == "theirs" for t in ours_then["told"]), (
            "his answer is not told on the table that comes before it")

    def test_the_line_under_the_title_is_about_the_clash_on_the_table(self, table):
        body, day = self._a_clash_followed_by_his(table)
        ours_then = body["battle_diorama"]["day"]
        his_then = day["reply"]["diorama"]["day"]
        ours, his = _toll_of(body["battle_diorama"])
        assert ours in _figures(ours_then["morning"]) and his in _figures(ours_then["morning"]), (
            "the figures under the title are the clash's own")
        assert ours_then["morning"] != his_then["morning"], "two clashes, two readings"

    def test_his_own_table_carries_the_day_as_it_stands(self, table):
        body, day = self._a_clash_followed_by_his(table)
        his_then = day["reply"]["diorama"]["day"]
        assert his_then["theirs"] == day["theirs"] and his_then["chips"], (
            "the live chips ride his tableau, as before")
        assert body["battle_diorama"]["day"]["follows"] is True

    def test_seam_down_our_table_carries_the_day_after_his_answer(self, table, monkeypatch):
        monkeypatch.setattr(BD, "our_table_reads_the_day_as_our_clash_left_it", lambda: False)
        body, day = self._a_clash_followed_by_his(table)
        assert body["battle_diorama"]["day"]["theirs"] == day["theirs"], "as BA-3 had it"


# ════════════════════════════════════════════════════════
# B. The table tells the day
# ════════════════════════════════════════════════════════

def _ctx(*, atk=40000, dfd=40000, outcome="attacker_tactical_victory", natural=7,
         atk_mods=(), dfd_mods=(), atk_parts=(), dfd_parts=()):
    """A finished clash as `battle_telling.what_told` reads it."""
    lead, foe = SimpleNamespace(name="Ney"), SimpleNamespace(name="Mack")
    pre = {"Ney": atk, "Mack": dfd}
    pre.update({p.name: p.strength for p in tuple(atk_parts) + tuple(dfd_parts)})
    return SimpleNamespace(
        marshal=lead, enemy_marshal=foe, atk_participants=list(atk_parts),
        def_participants=list(dfd_parts), _bd_pre_strengths=pre,
        pre_battle_attacker_strength=atk, pre_battle_defender_strength=dfd,
        conquered=False, enemy_destroyed=False,
        battle_result={"outcome": outcome, "attacker_roll": {"natural": natural},
                       "modifier_snapshot": {"attacker": list(atk_mods), "defender": list(dfd_mods)},
                       "attacker": {}, "defender": {}})


def _row(label, value, kind="bonus"):
    return {"label": label, "value": value, "type": kind}


class TestWhatTold:
    """One fixed rule, in order: numbers at 5 to 4, a named advantage of 10
    points, the dice at 3 from seven — else "an even fight". No figure."""

    def test_numbers_at_five_to_four_tell_first(self):
        ctx = _ctx(atk=50000, dfd=40000, dfd_mods=[_row("Fortified position", 16)])
        assert T.what_told(ctx, True, "ours") == "our weight of numbers told"
        assert T.what_told(ctx, False, "theirs") == "his weight of numbers told"

    def test_a_corps_that_fought_beside_the_lead_counts_with_him(self):
        davout = SimpleNamespace(name="Davout", strength=20000)
        ctx = _ctx(atk=30000, dfd=40000, atk_parts=[davout])
        assert T.what_told(ctx, True, "ours") == "our weight of numbers told"

    def test_short_of_it_the_largest_named_advantage_tells(self):
        ctx = _ctx(dfd_mods=[_row("Defensive stance", 15), _row("Fortified position", 16)])
        assert T.what_told(ctx, True, "theirs") == "his works told"
        assert T.what_told(ctx, False, "ours") == "our works told"

    def test_the_ground_is_nobodys(self):
        ctx = _ctx(dfd_mods=[_row("Terrain (hills)", 20)])
        assert T.what_told(ctx, True, "theirs") == "the ground told for him"
        assert T.what_told(ctx, False, "ours") == "the ground told for us"

    def test_the_losers_own_weakness_tells_against_him(self):
        ctx = _ctx(atk_mods=[_row("Exhaustion", 12, "penalty")])
        assert T.what_told(ctx, True, "theirs") == "our exhaustion told against us"
        assert T.what_told(ctx, False, "ours") == "his exhaustion told against him"

    def test_a_dug_in_line_shows_in_the_result(self):
        """The word's own effect: we dug in, he struck, and the line held."""
        ctx = _ctx(dfd_mods=[_row("Defensive stance", 15)])
        assert T.what_told(ctx, False, "ours") == "our dug-in line told"

    def test_his_squares_are_his_on_the_attackers_own_row(self):
        """The attacker's list names the DEFENDER's squares against the horse:
        "Our squares told against us" was said of his (the staged table)."""
        ctx = _ctx(atk_mods=[_row("Square formation (vs cavalry)", 40, "penalty")])
        assert T.what_told(ctx, True, "theirs") == "his squares told"
        assert T.what_told(ctx, False, "ours") == "our squares told"

    def test_his_guns_on_overwatch_are_his(self):
        ctx = _ctx(atk_mods=[_row("Artillery overwatch", 15, "penalty")])
        assert T.what_told(ctx, True, "theirs") == "his guns told"
        assert T.what_told(ctx, False, "ours") == "our guns told"

    def test_guns_on_a_square_are_the_gunners(self):
        ctx = _ctx(atk_mods=[_row("Square formation (vs artillery)", 50)])
        assert T.what_told(ctx, True, "ours") == "our guns told on his squares"
        assert T.what_told(ctx, False, "theirs") == "his guns told on our squares"

    def test_a_temper_is_named(self):
        ctx = _ctx(atk_mods=[_row("Personality (aggressive)", 15)])
        assert T.what_told(ctx, True, "ours") == "our aggressive temper told"
        ctx = _ctx(dfd_mods=[_row("Personality (aggressive)", 10, "penalty")])
        assert T.what_told(ctx, True, "ours") == "his aggressive temper told against him"

    def test_no_label_falls_to_a_bare_word(self):
        ctx = _ctx(dfd_mods=[_row("Outnumbered (cautious)", 10)])
        assert T.what_told(ctx, True, "theirs") == "his caution when outnumbered told"
        ctx = _ctx(dfd_mods=[_row("Immovable (literal hold)", 15)])
        assert T.what_told(ctx, True, "theirs") == "his immovable hold told"
        ctx = _ctx(atk_mods=[_row("Cavalry terrain (plains)", 20)])
        assert T.what_told(ctx, True, "ours") == "the ground told for our horse"
        ctx = _ctx(atk_mods=[_row("Cavalry terrain (forest)", 30, "penalty")])
        assert T.what_told(ctx, True, "theirs") == "the ground told against our horse"

    def test_under_ten_points_no_advantage_is_named(self):
        ctx = _ctx(dfd_mods=[_row("Square formation", 5)])
        assert T.what_told(ctx, True, "theirs") == "an even fight"

    @pytest.mark.parametrize("natural,attacker_is_ours,better,want", [
        (10, True, "ours", "the dice told for us"),         # our high throw
        (10, False, "theirs", "the dice told for him"),     # his high throw
        (4, True, "theirs", "the dice told for him"),       # our low throw served him
        (4, False, "ours", "the dice told for us"),
        (9, True, "ours", "an even fight"),                 # two from seven: no
        (10, True, "theirs", "an even fight"),              # a high throw, and still the worse of it
    ])
    def test_the_dice_tell_at_three_from_seven(self, natural, attacker_is_ours, better, want):
        assert T.what_told(_ctx(natural=natural), attacker_is_ours, better) == want

    def test_a_level_clash_is_an_even_fight(self):
        assert T.what_told(_ctx(atk=90000, dfd=30000), True, "even") == "an even fight"

    def test_it_never_carries_a_figure(self):
        for better in ("ours", "theirs"):
            for attacker_is_ours in (True, False):
                said = T.what_told(
                    _ctx(atk=50000, natural=11, dfd_mods=[_row("Fortified position", 16)]),
                    attacker_is_ours, better)
                assert not re.search(r"\d", said), said


class TestTheDaySoFarAndEachClash:
    """Figures with their scope: under the title the day's own toll, and one
    line a clash in the day's telling."""

    def test_the_line_under_the_title_is_the_days_toll(self, table):
        body, day = table.open_a_day(_awaits_us)
        toll = table.world.battle_days["days"]["Mack"]["toll"]
        assert day["morning"].startswith("The day so far: ")
        assert _figures(day["morning"]) == [toll["ours"], toll["his"]]
        assert day["morning"].endswith(("the better of the toll is ours.", "Mack has the better of the toll.",
                                        "the toll stands even."))

    def test_the_better_of_it_is_read_at_five_to_four(self):
        assert T.better_of(4000, 5000) == "ours" and T.better_of(5000, 4000) == "theirs"
        assert T.better_of(4000, 4999) == "even" and T.better_of(0, 0) == "even"
        day = {"clashes": 2, "toll": {"ours": 9000, "his": 4000}}
        assert T.day_so_far(day, "Mack") == (
            "The day so far: 9,000 of ours for 4,000 of his — Mack has the better of the toll.")
        assert T.day_so_far({"toll": {"ours": 1, "his": 2}}, "Mack") == "", "a day that kept no count"
        day["open"] = False
        assert T.day_so_far(day, "Mack") == (
            "The day: 9,000 of ours for 4,000 of his — Mack had the better of the toll.")
        even = {"clashes": 1, "toll": {"ours": 4000, "his": 4100}}
        assert T.day_so_far(even, "Mack").endswith("— the toll stands even."), (
            "the second reading: \"it stands even\" was read against a card's odds — the line names the TOLL")

    def test_the_opening_is_told_first_with_its_own_toll(self, table):
        body, day = table.open_a_day(_awaits_us)
        first = day["told"][0]
        assert first["kind"] == "clash" and first["who"] == "clash"
        assert first["line"].startswith("The opening: ")
        assert first["line"].split(": ", 1)[1].startswith(
            ("we won on points", "we lost on points", "drawn"))

    def test_a_clash_is_told_after_the_word_that_fought_it(self, table):
        for _ in range(12):
            table.open_a_day(_awaits_us)
            said = table.order("Ney, attack Mack")["battle_day"]
            if said["ended"] != "decided":
                break
        else:
            raise AssertionError("every press decided the day")
        kinds = [t["kind"] for t in said["told"]]
        at = max(i for i, k in enumerate(kinds) if k == "press")
        assert kinds[at + 1] == "clash", kinds
        assert said["told"][at + 1]["line"].startswith("Ney's attack: ")

    def test_his_clash_names_him_and_carries_its_own_toll(self, table):
        body, day = table.open_a_day(_struck_back, his=70000, his_personality="aggressive")
        clashes = [t["line"] for t in day["told"] if t["kind"] == "clash"]
        assert clashes[-1].startswith("Mack's attack: ")
        ours, his = _toll_of(day["reply"]["diorama"])
        assert _figures(clashes[-1]) == [ours, his], "the clash's own toll, as its table counts it"

    def test_seam_down_the_table_reads_as_before(self, table, monkeypatch):
        monkeypatch.setattr(T, "the_day_tells_its_clashes", lambda: False)
        body, day = table.open_a_day(_awaits_us)
        assert day["morning"].startswith("The last clash: ")
        assert not any(t["kind"] == "clash" for t in day["told"])
        assert "clash_line" not in table.world.battle_days["days"]["Mack"]


class TestBerthiersReading:
    """Three states, each true as things stand. The reading IS the rule he
    follows, read at the two ends of his mood, and it is shown only as far as
    the player can see."""

    def _ai(self):
        return EnemyAI(CommandExecutor())

    def _reading(self, world, mack, ney, **kw):
        base = dict(purse=2, opened=False, behind=False)
        base.update(kw)
        with contextlib.redirect_stdout(io.StringIO()):
            return self._ai().the_days_reading(mack, ney, world, **base)

    @pytest.mark.parametrize("personality,his,want", [
        ("literal", 70000, "will"),         # 1.17 over a bar of 0.92 to 1.08
        ("literal", 61000, "may"),          # 1.02: his mood decides
        ("literal", 50000, "will_not"),     # 0.83: short of his boldest mood
        ("aggressive", 50000, "will"),      # 0.83 over 0.595 to 0.805
        ("aggressive", 42000, "may"),
        ("cautious", 80000, "may"),         # 1.33 inside 1.17 to 1.43
        ("cautious", 60000, "will_not"),
    ])
    def test_the_three_states(self, personality, his, want):
        world, ney, mack = _pair(his=his, personality=personality)
        assert self._reading(world, mack, ney)["strike"] == want

    @pytest.mark.parametrize("personality,his", [
        ("literal", 70000), ("literal", 61000), ("literal", 50000),
        ("aggressive", 50000), ("aggressive", 42000), ("cautious", 80000), ("cautious", 60000),
    ])
    def test_the_reading_cannot_part_from_the_rule(self, personality, his):
        """For every roll on a grid across his mood, his word is the shared
        decision; "will" is never contradicted by a word that is no strike,
        "will not" never by a strike."""
        world, ney, mack = _pair(his=his, personality=personality)
        got = self._reading(world, mack, ney)
        spread = got["spread"]
        words = []
        for step in range(41):
            value = (1.0 - spread) + (2.0 * spread) * step / 40.0
            with contextlib.redirect_stdout(io.StringIO()):
                words.append(self._ai().the_days_word(
                    mack, ney, world, purse=2, opened=False, behind=False,
                    rng=_Fixed(value))["kind"])
        assert words[0] == got["low"]["kind"] and words[-1] == got["high"]["kind"]
        if got["strike"] == "will":
            assert set(words) == {"strike"}
        elif got["strike"] == "will_not":
            assert "strike" not in words
        else:
            assert "strike" in words and set(words) != {"strike"}
        # the decision falls from a strike as the bar rises, and never back
        first_other = next((i for i, k in enumerate(words) if k != "strike"), len(words))
        assert "strike" not in words[first_other:]

    def test_his_one_roll_is_still_the_first_thing_drawn(self, monkeypatch):
        """The split moved no draw: the mood is rolled after his temper is
        read and before anything of the field is."""
        world, ney, mack = _pair()
        order = []

        class Recording:
            def uniform(self, low, high):
                order.append("roll")
                return 1.0

        real = EnemyAI._muster_price

        def priced(self, *args, **kwargs):
            order.append("field")
            return real(self, *args, **kwargs)

        monkeypatch.setattr(EnemyAI, "_muster_price", priced)
        with contextlib.redirect_stdout(io.StringIO()):
            self._ai().the_days_word(mack, ney, world, purse=2, opened=False, behind=False,
                                     rng=Recording())
        assert order == ["roll", "field"]

    def test_the_reading_rolls_nothing_and_writes_nothing(self, table):
        body, day = table.open_a_day(_awaits_us)
        world = table.world
        stored = world.battle_days["days"]["Mack"]
        before, state = world.to_dict(), random.getstate()
        got = T.reading_of(world, stored)
        assert got and got["strike"] in ("will", "may", "will_not")
        assert world.to_dict() == before and random.getstate() == state

    def test_the_table_carries_it_only_where_a_word_is_ours_to_give(self, table):
        body, day = table.open_a_day(_awaits_us)
        assert day["reading"]["line"] in ("he will strike", "he may strike", "he will not strike")
        assert not re.search(r"\d", day["reading"]["line"] + day["reading"]["hover"])
        closed = table.word("break_off")["battle_day"]
        assert "reading" not in closed

    def test_a_purse_he_has_spent_is_read_from_the_table(self, table):
        body, day = table.open_a_day(_awaits_us, his=90000)
        stored = table.world.battle_days["days"]["Mack"]
        stored["theirs"] = 0
        assert T.reading_of(table.world, stored)["strike"] == "will_not"

    def test_a_corps_out_of_sight_beside_him_changes_nothing(self, table):
        """The fog law: no wording may turn on a corps the player cannot see."""
        body, day = table.open_a_day(_awaits_us, his=50000)
        world = table.world
        stored = world.battle_days["days"]["Mack"]
        alone = T.reading_of(world, stored)
        mack = world.marshals["Mack"]
        beside = next(r for r in world.get_region(mack.location).adjacent_regions
                      if r != world.marshals["Ney"].location)
        world.marshals["Hohenlohe"] = _mk("Hohenlohe", beside, 60000, nation="Austria")
        assert T.reading_of(world, stored) == alone

    def test_under_less_than_full_sight_a_certain_word_needs_the_bands(self, table):
        from backend.models.intel import FULL, PARTIAL, STALE
        body, day = table.open_a_day(_awaits_us, his=90000)
        world = table.world
        stored = world.battle_days["days"]["Mack"]
        mack, ney = world.marshals["Mack"], world.marshals["Ney"]
        stored["theirs"] = 2
        sight = world.intel[mack.location]
        # 33,000 on 30,000 is over a literal man's wariest bar (1.08): in
        # plain sight Berthier says so...
        ney.strength, mack.strength = 30000, 33000
        sight.visibility = FULL
        assert T.reading_of(world, stored)["strike"] == "will"
        # ...but in less than plain sight he is "a substantial force" (15,000
        # to 39,999): the band cannot prove it, and the word is "may".
        sight.visibility = PARTIAL
        assert T.reading_of(world, stored)["strike"] == "may"
        # Three to one is certain from the band alone ("a massive force", 70,000+).
        mack.strength = 90000
        assert T.reading_of(world, stored)["strike"] == "will"
        # Out of sight altogether, nothing is certain but an empty purse.
        sight.visibility = STALE
        assert T.reading_of(world, stored)["strike"] == "may"
        stored["theirs"] = 0
        assert T.reading_of(world, stored)["strike"] == "will_not"

    def test_seam_down_the_table_shows_his_temper_and_road_only(self, table, monkeypatch):
        monkeypatch.setattr(T, "the_table_reads_him", lambda: False)
        body, day = table.open_a_day(_awaits_us)
        assert "reading" not in day and day["his_temper"]


class TestAWordSaysWhatItDoes:
    """The chip's label keeps its words; what the word does rides beside it."""

    def test_a_press_carries_the_attack_cards_odds_and_the_men(self, table):
        body, day = table.open_a_day(_awaits_us)
        press = _chip(day, kind="press")
        assert press["label"] == "Ney presses", "the label is not rewritten"
        assert press["does"].startswith("odds: " + press["odds"] + " — ")
        assert _figures(press["does"])[-1] == table.world.marshals["Mack"].strength
        assert press["more"] == "A clash that decides ends the day at once.", (
            "and nothing of a reserve: the rule is parked, and no surface promises it")

    def test_with_the_reserve_armed_the_hover_says_what_a_point_kept_is_worth(self, table, monkeypatch):
        monkeypatch.setattr(BD, "the_reserve_pursues", lambda: True)
        body, day = table.open_a_day(_awaits_us)
        press = _chip(day, kind="press")
        assert f"pursues: {BD.reserve_pursuit():,} more of his fall" in press["more"]

    def test_dig_in_stand_and_the_exits_say_theirs(self, table):
        body, day = table.open_a_day(_awaits_us)
        assert _chip(day, kind="dig_in")["does"] == (
            f"defensive stance: +{T.dug_in_pct(table.world.marshals['Ney'])}% if he strikes")
        assert _chip(day, word="break_off")["does"] == "the day ends; he keeps the field"
        assert _chip(day, word="stand")["does"] in ("he speaks next", "night falls, undecided")
        assert "day ends" in _chip(day, word="break_off")["more"]

    def test_a_stand_after_his_silence_says_night_falls(self, table):
        table.open_a_day(_awaits_us)
        stored = table.world.battle_days["days"]["Mack"]
        stored["silences"] = 1
        assert _chip(BD.block(table.world, stored), word="stand")["does"] == "night falls, undecided"
        stored["silences"] = 0
        assert _chip(BD.block(table.world, stored), word="stand")["does"] == "he speaks next"

    def test_left_to_it_the_marshal_says_what_he_would_do(self, table):
        body, day = table.open_a_day(_awaits_us)
        leave = _chip(day, word="leave_it")
        assert leave["label"] == "Leave it to Ney"
        assert re.fullmatch(r"he (would|may) [a-z ]+", leave["does"]), leave["does"]

    def test_what_he_would_do_is_the_rule_he_then_follows(self, table):
        """Where the chip says "he would", leaving it to him does exactly that
        as his first word."""
        for _ in range(8):
            body, day = table.open_a_day(_awaits_us)
            leave = _chip(day, word="leave_it")
            if leave["does"].startswith("he would "):
                break
        else:
            pytest.skip("no day whose lead was certain of his word")
        told_before = len(day["told"])
        after = table.word("leave_it")["battle_day"]
        ours = [t for t in after["told"] if t["who"] == "ours"]
        want = {"press": ("press",), "strike back": ("press",), "dig in": ("dig_in",),
                "stand": ("stand",), "break off": ("break_off",), "fall back": ("break_off",)}
        would = leave["does"][len("he would "):]
        assert ours, f"he said nothing: {after['told'][told_before:]}"
        assert ours[0]["kind"] in want.get(would, (ours[0]["kind"],)), (would, ours)

    def test_the_guard_names_its_first_number(self, table):
        emperor = _mk("Napoleon", "Rhineland", 30000, personality="sovereign", command=10)
        _, day = table.open_a_day(_awaits_us, extra=(emperor,))
        guard = _chip(day, kind="guard")
        assert guard["label"] == "The Guard"
        assert guard["does"].endswith("his morale −10")
        assert "loses 10" in guard["more"]

    def test_seam_down_a_chip_is_as_it_was(self, table, monkeypatch):
        monkeypatch.setattr(T, "a_word_says_what_it_does", lambda: False)
        body, day = table.open_a_day(_awaits_us)
        assert all("does" not in chip and "more" not in chip for chip in day["chips"])


_SHAPES = [
    ({"clashes": 3, "decided_for": "ours", "said": [["ours", "press"], ["ours", "guard"]]},
     "decided", "The Guard decided it."),
    ({"clashes": 3, "decided_for": "theirs", "said": [["ours", "guard"]]},
     "decided", "The Guard went in and was thrown back."),
    ({"clashes": 3, "decided_for": "theirs", "said": [["theirs", "guard"]]},
     "decided", "Mack's Guard decided it."),
    ({"clashes": 3, "decided_for": "ours", "said": [["ours", "bring_up"], ["ours", "press"]]},
     "decided", "A corps brought up in the day turned it."),
    ({"clashes": 3, "decided_for": "ours", "said": [["ours", "cannonade"], ["ours", "press"]]},
     "decided", "The guns prepared it and the column carried it."),
    ({"clashes": 2, "decided_for": "ours", "said": [["ours", "press"]]},
     "decided", "One blow after the opening decided it."),
    ({"clashes": 4, "decided_for": "ours",
      "said": [["ours", "press"], ["theirs", "strike"], ["ours", "press"]]},
     "decided", "It was fought out to a decision."),
    ({"clashes": 2, "said": [["theirs", "dig_in"], ["ours", "press"]]},
     "broke_off", "The attack was given up before a dug-in line."),
    ({"clashes": 2, "said": [["ours", "press"]]}, "broke_off", "The attack was given up."),
    ({"clashes": 2, "said": [["theirs", "strike"]]}, "he_broke_off", "Mack gave up his attack."),
    ({"clashes": 2, "said": []}, "drew_off", "Mack left the field in good order."),
    ({"clashes": 2, "said": []}, "fell_back", "Ney left the field in good order."),
    ({"clashes": 2, "said": [], "ours": 1, "toll": {"ours": 4000, "his": 9000}},
     "night", "Our reserve was never spent."),
    ({"clashes": 2, "said": [], "theirs": 2, "toll": {"ours": 9000, "his": 4000}},
     "night", "Mack's reserve was never spent."),
    ({"clashes": 2, "said": [], "toll": {"ours": 5000, "his": 5100}},
     "night", "Neither side could claim the field."),
    ({"clashes": 2, "said": [], "ours": 0, "toll": {"ours": 4000, "his": 9000}},
     "night", "It was fought to a standstill."),
]


class TestTheCloseNamesWhatTold:
    """BA-4's line stands whole; the close goes on after it. And D5: a night
    on an undecided field says whom its toll favoured."""

    def test_a_night_says_whom_the_toll_favoured(self, table):
        table.open_a_day(_awaits_us)
        stored = table.world.battle_days["days"]["Mack"]
        stored["theirs"] = 0
        stored["toll"] = {"ours": 17320, "his": 11965}
        closing = table.word("stand")["battle_day"]
        assert closing["ended"] == "night"
        assert [t["kind"] for t in closing["told"]][-3:] == ["tally", "shape", "after"]
        assert closing["told"][-1]["line"] == "Neither army is driven off; the fight may be renewed tomorrow."
        shape = closing["told"][-2]["line"]
        assert shape.startswith("Mack had the better of the toll. ")
        assert closing["close"].endswith(shape)
        assert closing["close"].startswith("Night fell on the field at Lorraine: ")

    @pytest.mark.parametrize("day,how,want", _SHAPES)
    def test_the_shape_of_a_day_is_read_from_its_words_and_its_end(self, day, how, want):
        assert T.shape_of(day, how, "Mack", "Ney") == want

    def test_a_day_a_clash_decided_says_what_told(self):
        day = {"clashes": 3, "decided_for": "ours", "decided_by": "our weight of numbers told",
               "said": [["ours", "press"], ["ours", "press"]]}
        assert T.close_more(day, "decided", "Mack", "Ney") == [
            "Our weight of numbers told.", "It was fought out to a decision."]
        day["decided_by"] = "an even fight"
        assert T.close_more(day, "decided", "Mack", "Ney") == ["It was fought out to a decision."]

    def test_a_day_that_kept_no_count_adds_nothing(self):
        assert T.close_more({"said": [["ours", "press"]]}, "night", "Mack", "Ney") == []

    def test_through_the_server_a_decided_day_is_told_whole(self, table):
        for _ in range(60):
            table.open_a_day(_awaits_us, ours=90000, his=52000)
            said = table.order("Ney, attack Mack").get("battle_day") or {}
            if said.get("ended") == "decided":
                break
        else:
            raise AssertionError("no press decided a day")
        rows = [e for e in table.world.event_log if e.get("type") == "battle_day_closed"]
        line = rows[-1]["line"]
        assert line.startswith("The day at Lorraine was decided at the ")
        assert " of the enemy's. " in line, "the close goes on after BA-4's line"
        assert line == said["close"]

    def test_seam_down_the_close_is_ba4s(self, table, monkeypatch):
        monkeypatch.setattr(T, "the_close_names_what_told", lambda: False)
        table.open_a_day(_awaits_us)
        closing = table.word("break_off")["battle_day"]
        assert closing["close"].endswith(" of the enemy's.")
        assert not any(t["kind"] == "shape" for t in closing["told"])


# ════════════════════════════════════════════════════════
# C. The reserve pursues a beaten enemy
# ════════════════════════════════════════════════════════

@contextlib.contextmanager
def _a_word(**word):
    token = BD._WORD.set(dict(word))
    try:
        yield BD._WORD.get()
    finally:
        BD._WORD.reset(token)


def _lead(strength=40000, ability=""):
    return SimpleNamespace(name="Mack", strength=strength, ability={"name": ability} if ability else {})


class TestTheFirstDaysLineStandsOnItsFirstTable:
    """The first day of a campaign says what a day is, once (BA-4) — but a
    day is fought inside one turn, and a first-open line stays on every
    payload of the turn it was first shown: the two-line lecture stood on
    EVERY table of the first day (seen in the real client, on the table after
    the first word) and took the room of the exits' own words. Once the
    client says it has drawn the line, it stays on that table only."""

    @staticmethod
    def _ack(table):
        shown = table.tc.post("/first_open", json={"screen": "battle_day"}).json()
        assert shown["success"]

    @staticmethod
    def _a_day_that_comes_back_after_a_stand(table, before_the_stand=None):
        for _ in range(40):
            table.open_a_day(_awaits_us)
            if before_the_stand is not None:
                before_the_stand()
            block = table.word("stand").get("battle_day") or {}
            if block.get("open") and block.get("awaits") == "ours":
                return block
        raise AssertionError("no day came back to us after a stand")

    def test_the_first_table_carries_it_and_a_re_read_keeps_it(self, table):
        _body, day = table.open_a_day(_awaits_us)
        assert day["first_open"]["screen"] == "battle_day"
        self._ack(table)
        assert "first_open" in table.days()["days"][0], "the same table, read again on the turn it was shown"
        assert table.world.battle_days["days"]["Mack"]["first_shown_at"] == BD._as_it_stands(
            table.world.battle_days["days"]["Mack"])

    def test_once_it_is_drawn_the_days_next_table_does_not_say_it_again(self, table):
        block = self._a_day_that_comes_back_after_a_stand(table, before_the_stand=lambda: self._ack(table))
        assert any(t["who"] == "ours" for t in block["told"]), "our stand is told"
        assert "first_open" not in block, "the next table of the day"
        assert "first_open" not in table.days()["days"][0]

    def test_a_line_nobody_has_drawn_rides_the_next_table_too(self, table):
        """A first table with no room for it — or a first word given from the
        province's panel, with no table up — leaves the line to the table
        that follows (the road the old save's board walks in the client)."""
        block = self._a_day_that_comes_back_after_a_stand(table)
        assert "battle_day" not in table.world.first_opens
        assert block["first_open"]["screen"] == "battle_day"

    def test_another_day_of_the_same_turn_does_not_say_it(self, table):
        table.open_a_day(_awaits_us)
        self._ack(table)
        world = table.world
        kept = dict(world.battle_days["days"]["Mack"])
        other = dict(kept, enemy="Kienmayer", first_shown_at=None)
        other.pop("first_shown_at")
        assert BD._says_its_first_line(world, kept) is True
        assert BD._says_its_first_line(world, other) is False, "a day that was not on the table that showed it"

    def test_seam_down_every_table_of_the_turn_says_it(self, table, monkeypatch):
        monkeypatch.setattr(BD, "the_first_days_line_stands_on_its_first_table", lambda: False)
        block = self._a_day_that_comes_back_after_a_stand(table, before_the_stand=lambda: self._ack(table))
        assert block["first_open"]["screen"] == "battle_day", "as BA-4 had it"
        assert "first_shown_at" not in table.world.battle_days["days"]["Mack"], "and the day keeps no mark"


class TestTheCardCountsHimAsTheTableDoes:
    """A figure that did not agree, seen on the staged table of a defended
    day: the card read "38,210 on large force" beside his corps counted to the
    man. The map's sighting of his province was a band; the day's own table
    counts him at every clash, and the card now says that figure — with no
    odds word, which only an exact sighting of the whole field gives."""

    @staticmethod
    def _a_band(world, monkeypatch):
        """The map's own sighting of him: a band (as of a province seen in part)."""
        from backend.commands.combat_executor import CombatExecutor
        monkeypatch.setattr(CombatExecutor, "_fog_banded_strength",
                            staticmethod(lambda marshal, world: "large force"))

    def test_the_day_counts_him_at_its_opening_clash(self, table):
        body, day = table.open_a_day(_awaits_us)
        stored = table.world.battle_days["days"]["Mack"]
        assert stored["his_men"] == table.world.marshals["Mack"].strength

    def test_on_a_band_the_card_says_the_tables_own_figure(self, table, monkeypatch):
        body, day = table.open_a_day(_awaits_us)
        counted = table.world.battle_days["days"]["Mack"]["his_men"]
        self._a_band(table.world, monkeypatch)
        press = _chip(table.days()["days"][0], kind="press")
        assert press["does"].endswith(f" on {counted:,}"), press["does"]
        assert "large force" not in press["does"] and "odds" not in press["does"], (
            "the figure the table shows, and no odds word on a band")
        assert press["odds"] == ""

    def test_a_corps_that_joins_him_unseen_is_not_read_back(self, table, monkeypatch):
        body, day = table.open_a_day(_awaits_us)
        counted = table.world.battle_days["days"]["Mack"]["his_men"]
        self._a_band(table.world, monkeypatch)
        table.world.marshals["Mack"].strength += 9000        # out of our sight
        press = _chip(table.days()["days"][0], kind="press")
        assert press["does"].endswith(f" on {counted:,}"), "the count is the table's, not the truth"

    def test_an_exact_sighting_is_the_quotes_own(self, table):
        body, day = table.open_a_day(_awaits_us)
        press = _chip(day, kind="press")
        assert press["does"].startswith("odds: "), "the muster's word, on an exact sighting"

    def test_seam_down_nothing_is_counted(self, table, monkeypatch):
        monkeypatch.setattr(T, "a_word_says_what_it_does", lambda: False)
        table.open_a_day(_awaits_us)
        assert "his_men" not in table.world.battle_days["days"]["Mack"], "the record is BA-4's, key for key"


class TestTheReserveIsParked:
    """The user's tick at the plan gate — "Build it; the rule picks" — and the
    rule picked none: at every value of its ladder the reserve failed the
    rule written for it before its data (of the men it took, about nine in
    ten were ours). By the plan's own words it is NOT built: the rule stands
    behind its seam, DOWN in the game, and nothing a player reads promises
    it (`BATTLE_DIORAMA_SPEC.md` §15.23)."""

    def test_it_is_down_in_the_game(self):
        assert BD.the_reserve_pursues() is False
        assert "PARKED" in BD.the_reserve_pursues.__doc__

    def test_a_deciding_press_with_a_point_in_hand_pays_nothing(self, table):
        for _ in range(80):
            table.open_a_day(_awaits_us, ours=90000, his=52000)
            table.world.battle_days["days"]["Mack"]["theirs"] = 0
            body = table.order("Ney, attack Mack")
            said = body.get("battle_day") or {}
            if said.get("ended") == "decided":
                break
        else:
            raise AssertionError("no press decided a day")
        beats = [b for act in body["battle_diorama"]["script"]["acts"] for b in act["beats"]]
        assert not [b for b in beats if b.get("reserve")]
        assert "reserve pursued" not in said["close"]
        assert "The reserve pursues" not in body["message"]

    def test_no_surface_promises_it(self, table):
        import pathlib
        body, day = table.open_a_day(_awaits_us)
        for chip in day["chips"]:
            assert "pursue" not in (chip.get("more") or "").lower(), chip["label"]
            assert "pursue" not in (chip.get("does") or "").lower(), chip["label"]
        terms = (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
                 / "scripts" / "codex_terms.gd").read_text(encoding="utf-8")
        assert '["The reserve"' not in terms and "see The reserve" not in terms
        assert "unspent reserve pursues" not in terms

    def test_the_measured_record_says_why(self):
        import json
        import pathlib
        path = pathlib.Path(BD.__file__).resolve().parents[2] / "tools" / "_ba5_reserve_rule_2026_11_17.json"
        assert path.is_file(), "the reserve's rule is not on record"
        rule = json.loads(path.read_text(encoding="utf-8"))
        assert rule["pick"] is None and sorted(rule["values"]) == ["2000", "3000", "5000"]
        for value, cell in rule["values"].items():
            assert cell["passes"] is False, value
            assert cell["clauses"]["iii_neither_side_takes_three_quarters"] is False, value
            assert cell["men_from_us"] > 3 * cell["men_from_him"], (value, "nine in ten were ours")
            assert cell["clauses"]["iv_band_in"] is True, value


class TestTheReservePursuesABeatenEnemy:
    """THE MEASURED ARM (the seam up; the rule is parked in the game — the
    class above). When a clash decides a day, the victor's unspent points,
    less the loser's, each cost the beaten lead men more — either side, after
    an ability's own pursuit, never below 1,000 men, halved against the Old
    Fox; nothing when a side breaks off or draws off, or at night."""

    @pytest.fixture(autouse=True)
    def _armed(self, monkeypatch):
        monkeypatch.setattr(BD, "the_reserve_pursues", lambda: True)

    def test_the_number_is_one_of_the_ladders_three(self):
        assert BD.reserve_pursuit() == BD.RESERVE_PURSUIT and BD.RESERVE_PURSUIT in (2000, 3000, 5000)

    def test_a_point_held_over_the_loser_costs_him_the_figure(self):
        with _a_word(reserve={"attacker": 2, "defender": 1}):
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead()) == (BD.reserve_pursuit(), 1)
        with _a_word(reserve={"attacker": 2, "defender": 0}):
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead()) == (2 * BD.reserve_pursuit(), 2)

    def test_a_point_the_loser_kept_covers_him(self):
        with _a_word(reserve={"attacker": 1, "defender": 1}):
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead()) == (0, 0)
        with _a_word(reserve={"attacker": 1, "defender": 2}):
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead()) == (0, 0)

    def test_a_defender_who_throws_the_attack_back_pursues_with_his(self):
        with _a_word(reserve={"attacker": 0, "defender": 2}):
            assert BD.reserve_pursuit_men(attacker_wins=False, loser=_lead()) == (2 * BD.reserve_pursuit(), 2)
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead()) == (0, 0)

    def test_the_old_fox_halves_it_and_no_corps_is_pursued_under_a_thousand(self):
        with _a_word(reserve={"attacker": 2, "defender": 0}):
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead(ability="The Old Fox")) == (
                BD.reserve_pursuit(), 2)
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead(strength=1000)) == (0, 0)
            men, points = BD.reserve_pursuit_men(attacker_wins=True, loser=_lead(strength=2500))
            assert (men, points) == (1500, 2), "never below a thousand men"

    def test_no_word_of_a_day_no_reserve(self):
        assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead()) == (0, 0)
        with _a_word(kind="press"):
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead()) == (0, 0)

    def test_seam_down_a_point_kept_is_worth_nothing(self, monkeypatch):
        monkeypatch.setattr(BD, "the_reserve_pursues", lambda: False)
        with _a_word(reserve={"attacker": 2, "defender": 0}):
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=_lead()) == (0, 0)

    def test_the_count_is_taken_with_the_word_paid_for(self, table):
        table.open_a_day(_awaits_us)
        world = table.world
        stored = world.battle_days["days"]["Mack"]
        stored["ours"], stored["theirs"] = 2, 1
        # (the session's review) the count is the WORD's battle's: ours falls on the day's
        # enemy, his on the day's lead (`battle_day.a_words_battle_is_its_own_clash`)
        ours = SimpleNamespace(world=world, enemy_marshal=world.marshals["Mack"])
        his = SimpleNamespace(world=world, enemy_marshal=world.marshals["Ney"])
        with _a_word(key="Mack", who="ours", price=1, kind="press") as word:
            BD.count_the_reserve(ours)
            assert word["reserve"] == {"attacker": 1, "defender": 1}
        with _a_word(key="Mack", who="ours", price=2, kind="guard") as word:
            BD.count_the_reserve(ours)
            assert word["reserve"] == {"attacker": 0, "defender": 1}
        with _a_word(key="Mack", who="theirs", price=1, kind="strike") as word:
            BD.count_the_reserve(his)
            assert word["reserve"] == {"attacker": 0, "defender": 2}

    def _a_press_that_decides(self, table, his_purse):
        for _ in range(80):
            table.open_a_day(_awaits_us, ours=90000, his=52000)
            stored = table.world.battle_days["days"]["Mack"]
            stored["theirs"] = his_purse
            mack_before = None
            body = table.order("Ney, attack Mack")
            said = body.get("battle_day") or {}
            if said.get("ended") == "decided" and table.world.marshals["Mack"].strength > 1000:
                return body, said, mack_before
        raise AssertionError("no press decided a day")

    def test_through_the_server_a_point_in_hand_pursues_the_beaten_lead(self, table):
        body, said, _ = self._a_press_that_decides(table, his_purse=0)
        beats = [b for act in body["battle_diorama"]["script"]["acts"] for b in act["beats"]]
        pursued = [b for b in beats if b.get("reserve")]
        assert len(pursued) == 1, [b.get("kind") for b in beats]
        assert pursued[0]["damage"] == BD.reserve_pursuit(), "Ney pressed for one of two: one point over Mack's none"
        assert "reserve pursues" in pursued[0]["text"]
        assert "one point in hand more than Mack kept" in pursued[0]["text"], (
            "(the session's review) the points held OVER his, not \"the point he kept\"")
        assert f"Our reserve pursued: {BD.reserve_pursuit():,} more of his fell." in said["close"]

    def test_through_the_server_the_days_toll_counts_the_pursuit(self, table):
        body, said, _ = self._a_press_that_decides(table, his_purse=0)
        rows = [e for e in table.world.event_log if e.get("type") == "battle_day_closed"]
        ours, his = _toll_of(body["battle_diorama"])
        assert rows[-1]["his_loss"] >= his, "the clash's toll, pursuit and all, is in the day's"

    def test_through_the_server_a_reserve_he_kept_covers_him(self, table):
        body, said, _ = self._a_press_that_decides(table, his_purse=2)
        beats = [b for act in body["battle_diorama"]["script"]["acts"] for b in act["beats"]]
        assert not [b for b in beats if b.get("reserve")]
        assert "reserve pursued" not in said["close"]

    def test_seam_down_through_the_server_nothing_is_paid(self, table, monkeypatch):
        monkeypatch.setattr(BD, "the_reserve_pursues", lambda: False)
        body, said, _ = self._a_press_that_decides(table, his_purse=0)
        beats = [b for act in body["battle_diorama"]["script"]["acts"] for b in act["beats"]]
        assert not [b for b in beats if b.get("reserve")]
        assert "reserve pursued" not in said["close"]

    def test_an_ordinary_battle_pays_none(self, table):
        """A battle that is no word of an open day reads no reserve at all."""
        world = table.world
        _seat(world, ours=30000, his=9000)
        world.clear_turn_battles()
        body = table.order("Ney, attack Mack")
        assert "battle_day" not in body or not (body.get("battle_day") or {}).get("open")
        beats = [b for act in ((body.get("battle_diorama") or {}).get("script") or {}).get("acts", [])
                 for b in act.get("beats", [])]
        assert not [b for b in beats if b.get("reserve")]


# ════════════════════════════════════════════════════════
# Ruling 1 — a truce names the ground its peace would title
# ════════════════════════════════════════════════════════

class TestATruceNamesTheGroundItWouldTitle:
    """The AI-France harness's annexation line read 2 on one seed. The first
    was the player's own signature: Britain's truce ran out into a signed
    peace and the status quo titled Carniola to Britain (SR-1a — the player's
    peaces keep what each side holds), under a card that said only "what each
    side holds is titled by the signature". SF7-X7 made a PEACE name the
    ground; a truce that ends in one did not."""

    def _a_truce_heading_for_a_dictated_peace(self, world):
        from backend.game_logic import diplomacy as D
        _truce(world, proposer="Austria", target="France",
               sweeteners=[{"type": "gold_per_turn", "value": 80}])
        _kill_hope(world)
        world.nation_relations[world._make_diplo_key("Austria", "France")] = -80
        return D.truce_words(world, "France", "Austria")

    def test_the_heading_names_the_provinces(self, vienna_held):
        words = self._a_truce_heading_for_a_dictated_peace(vienna_held)
        assert words["exit"] == "dictated"
        head = words["heading_line"]
        assert head.startswith("At expiry: a dictated peace on the held line"), "its own words stay"
        assert "titled by the signature and the sureties become its terms. As things stand: " in head
        named = head.split("As things stand: ", 1)[1]
        for province in ("Bohemia", "Tyrol", "Vienna"):
            assert province in named
        assert "Status quo:" not in head, "one label, not two"

    def test_it_is_the_ratifiers_own_forecast(self, vienna_held):
        from backend.game_logic.game_end import status_quo_forecast_lines
        words = self._a_truce_heading_for_a_dictated_peace(vienna_held)
        forecast = status_quo_forecast_lines(vienna_held, "France", "Austria", "France")
        for sentence in forecast["lines"] + forecast["warnings"]:
            assert sentence.replace("Status quo: ", "", 1) in words["heading_line"]

    def test_a_truce_heading_back_to_war_names_nothing(self, vienna_held):
        from backend.game_logic import diplomacy as D
        _truce(vienna_held)
        words = D.truce_words(vienna_held, "France", "Austria")
        if words["exit"] == "war":
            assert "As things stand" not in words["heading_line"]

    def test_seam_down_the_heading_is_as_it_was(self, vienna_held, monkeypatch):
        from backend.game_logic import diplomacy as D
        monkeypatch.setattr(D, "a_truce_names_the_ground_it_would_title", lambda: False)
        words = self._a_truce_heading_for_a_dictated_peace(vienna_held)
        assert words["heading_line"].endswith("the sureties become its terms.")


# ════════════════════════════════════════════════════════
# D. The extras ticked at the gate
# ════════════════════════════════════════════════════════

_VERDICT_WORDS = ("won", "lost", "won on points", "lost on points", "drawn")


def _a_led_battle(outcome, *, attacker_is_ours=True, turn=7):
    """One finished pitched battle, kept through the record's own writer.
    Returns the marshal who led it for us."""
    ctx = _ctx(outcome=outcome)
    ctx.battle_name = "Battle of Swabia"
    ctx.battle_region_name = "Swabia"
    ctx.battle_result["attacker"] = {"casualties": 4000}
    ctx.battle_result["defender"] = {"casualties": 9000}
    world = SimpleNamespace(current_turn=turn)
    ours = _mk("Ney", "Swabia", 30000)
    his = _mk("Mack", "Swabia", 30000, nation="Austria")
    BD._keep_his_battle(world, ctx, ours, his, attacker_is_ours, outcome in BD.HANGING)
    return ours


class TestAMarshalsDays:
    """The user's tick at the plan gate — "A marshal's days". A pitched battle
    our marshal LED is kept on his own record when it is over: its name, its
    turn, how it went for him, what told and, for a great battle fought in
    turns, what kind of day it was. The last six stand; his card on the
    Generals screen reads them and no rule of the game does."""

    def _an_ordinary_battle(self, table, ours=30000, his=9000):
        world = table.world
        _seat(world, ours=ours, his=his)
        world.clear_turn_battles()
        return table.order("Ney, attack Mack")

    def test_a_battle_he_led_is_on_his_record(self, table):
        body = self._an_ordinary_battle(table)
        ney = table.world.marshals["Ney"]
        assert len(ney.days) == 1
        day = ney.days[-1]
        assert day["name"] == BD.the_battle_of(body["battle_diorama"]["battle_name"])
        assert day["turn"] == table.world.current_turn and day["against"] == "Mack"
        assert day["verdict"] in _VERDICT_WORDS
        assert day["shape"] == "" and "clashes" not in day, "a battle told at once is no day of turns"
        assert (day["our_loss"], day["his_loss"]) == _toll_of(body["battle_diorama"])

    def test_the_enemys_lead_keeps_none(self, table):
        self._an_ordinary_battle(table)
        assert table.world.marshals["Mack"].days == []

    @pytest.mark.parametrize("outcome, ours_attack, verdict", [
        ("attacker_victory", True, "won"), ("defender_victory", True, "lost"),
        ("attacker_victory", False, "lost"), ("defender_victory", False, "won"),
        ("attacker_tactical_victory", True, "won on points"),
        ("defender_tactical_victory", True, "lost on points"),
        ("attacker_tactical_victory", False, "lost on points"),
        ("defender_tactical_victory", False, "won on points"),
        ("stalemate", True, "drawn"), ("mutual_destruction", True, "drawn")])
    def test_how_it_went_for_him_from_either_side_of_the_field(self, outcome, ours_attack, verdict):
        lead = _a_led_battle(outcome, attacker_is_ours=ours_attack)
        [day] = lead.days
        assert day["verdict"] == verdict
        assert (day["our_loss"], day["his_loss"]) == ((4000, 9000) if ours_attack else (9000, 4000))
        assert day["name"] == "Battle of Swabia" and day["place"] == "Swabia" and day["turn"] == 7

    def test_what_told_is_the_tables_own_word(self):
        ctx = _ctx(atk=60000, dfd=30000, outcome="attacker_victory")
        ctx.battle_name, ctx.battle_region_name = "Battle of Swabia", "Swabia"
        ours, his = _mk("Ney", "Swabia", 60000), _mk("Mack", "Swabia", 30000, nation="Austria")
        BD._keep_his_battle(SimpleNamespace(current_turn=3), ctx, ours, his, True, False)
        assert ours.days[-1]["told"] == "our weight of numbers told" == T.what_told(ctx, True, "ours")
        even = _a_led_battle("stalemate")
        assert even.days[-1]["told"] == "", "an even fight says nothing of what told"

    def test_an_open_day_is_kept_when_it_closes_and_once(self, table):
        table.open_a_day(_awaits_us)
        ney = table.world.marshals["Ney"]
        assert ney.days == [], "the opening clash of a day is not yet a day on his record"
        closing = table.word("break_off")["battle_day"]
        assert closing["open"] is False
        [day] = ney.days
        told = [e for e in table.world.event_log if e.get("type") == "battle_day_closed"][-1]
        assert day["clashes"] == told["clashes"] >= 1, "the day's own count (his answer is a clash of it)"
        assert (day["our_loss"], day["his_loss"]) == (told["our_loss"], told["his_loss"]), "the day's toll"
        assert day["against"] == "Mack" and day["place"] == "Lorraine"
        assert day["shape"].startswith("The attack was given up")
        assert day["verdict"] in ("won on points", "lost on points", "drawn"), "no clash decided it"
        assert day["name"] and " — the " not in day["name"], "the BATTLE's name, not a clash's"
        assert day["told"] == ""

    def test_a_day_a_clash_decided_keeps_whom_for_and_what_told(self, table):
        for _ in range(80):
            table.open_a_day(_awaits_us, ours=90000, his=52000)
            said = table.order("Ney, attack Mack").get("battle_day") or {}
            if said.get("ended") == "decided":
                break
        else:
            raise AssertionError("no press decided a day")
        [day] = table.world.marshals["Ney"].days
        assert day["verdict"] in ("won", "lost") and day["clashes"] == 2
        assert day["shape"] and day["shape"] in said["close"], "the close's own shape"
        if day["told"]:
            assert f"{day['told'][:1].upper()}{day['told'][1:]}." in said["close"]

    def test_the_last_six_stand(self):
        lead = _mk("Ney", "Swabia", 30000)
        for n in range(9):
            lead.keep_day({"name": f"Battle {n}", "turn": n})
        assert [d["name"] for d in lead.days] == [f"Battle {n}" for n in range(3, 9)]
        assert type(lead).DAYS_KEPT == 6

    def test_a_save_holds_them_only_while_he_has_one(self):
        from backend.models.marshal import Marshal
        fresh = _mk("Ney", "Swabia", 30000)
        assert "days" not in fresh.to_dict(), "a marshal with none saves as he always did"
        assert Marshal.from_dict(fresh.to_dict()).days == []
        led = _a_led_battle("attacker_victory")
        saved = led.to_dict()
        assert saved["days"] == led.days and saved["days"] is not led.days
        assert Marshal.from_dict(saved).days == led.days
        assert "days" in Marshal.KEPT_ONLY_WHEN_HELD_FIELDS

    def test_the_field_censuses_still_see_a_day_that_is_not_saved(self, monkeypatch):
        """The exemption is narrow: EMPTY, the field is owed no key; holding a
        day, it is owed one — both censuses report it if `to_dict` drops it."""
        from backend.models.marshal import Marshal
        from tests.test_serialization_enforcement import get_instance_attributes
        from tests.test_serialization_played_world_census import _misses
        fresh, led = _mk("Ney", "Swabia", 30000), _a_led_battle("attacker_victory")
        assert "days" not in get_instance_attributes(fresh) and "days" not in _misses(fresh)
        assert "days" in get_instance_attributes(led) and "days" not in _misses(led)
        whole = Marshal.to_dict

        def amputated(self):
            data = whole(self)
            data.pop("days", None)
            return data

        monkeypatch.setattr(Marshal, "to_dict", amputated)
        assert "days" in _misses(led), "a day held and not saved is a defect the census reports"

    def test_the_world_carries_them_through_a_save(self, table):
        from backend.models.world_state import WorldState
        self._an_ordinary_battle(table)
        world = table.world
        again = WorldState.from_dict(world.to_dict())
        assert again.marshals["Ney"].days == world.marshals["Ney"].days != []
        assert "days" not in world.to_dict()["marshals"]["Mack"]

    def test_his_card_tells_them_newest_first(self, table):
        from backend.game_logic.marshal_overview import build_marshal_overview
        self._an_ordinary_battle(table)
        world = table.world
        ney = world.marshals["Ney"]
        ney.keep_day({"name": "The Great Battle of Bavaria", "turn": int(world.current_turn),
                      "place": "Bavaria", "against": "ArchdukeCharles", "verdict": "lost on points",
                      "told": "his works told", "shape": "The attack was given up before a dug-in line.",
                      "our_loss": 9100, "his_loss": 4200, "clashes": 2})
        card = next(c for c in build_marshal_overview(world) if c["name"] == "Ney")
        rows = card["days"]
        assert [r["name"] for r in rows][0] == "The Great Battle of Bavaria", "newest first"
        assert len(rows) == 2
        top = rows[0]
        assert top["verdict"] == "lost on points" and top["tone"] == "bad"
        assert top["rest"] == (" against Archduke Charles: 9,100 of ours for 4,200 of his. "
                               "His works told. The attack was given up before a dug-in line.")
        assert top["line"] == f"{top['when']}: The Great Battle of Bavaria — lost on points{top['rest']}"
        assert top["when"] and top["turn"] == int(world.current_turn)
        assert all(isinstance(r["turn"], int) for r in rows), "Golden Rule 2"
        assert rows[1]["rest"].startswith(" against Mack: ")

    def test_a_card_with_none_carries_no_such_key(self, table):
        from backend.game_logic.marshal_overview import build_marshal_overview
        world = table.world
        _seat(world)
        card = next(c for c in build_marshal_overview(world) if c["name"] == "Ney")
        assert "days" not in card

    def test_seam_down_nothing_is_kept(self, table, monkeypatch):
        monkeypatch.setattr(BD, "a_marshal_keeps_his_days", lambda: False)
        self._an_ordinary_battle(table)
        assert table.world.marshals["Ney"].days == []
        table.open_a_day(_awaits_us)
        table.word("break_off")
        assert table.world.marshals["Ney"].days == []

    def test_a_campaign_that_is_not_served_keeps_none(self, table, monkeypatch):
        """The record is written where a day of battle is — on a served
        campaign (`battle_day._on`): the suite's own worlds and a campaign
        from before the battle's dice carry none."""
        monkeypatch.setattr(BD, "_on", lambda world: False)
        self._an_ordinary_battle(table)
        assert table.world.marshals["Ney"].days == []

    def test_no_rule_of_the_game_reads_the_record(self):
        """`days` is read by the marshal's own model (its writer and its save)
        and by his card's builder. Nothing else in the backend names it."""
        import ast
        import pathlib
        root = pathlib.Path(BD.__file__).resolve().parents[1]
        readers = set()
        for path in root.rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                named = (isinstance(node, ast.Attribute) and node.attr == "days") or (
                    isinstance(node, ast.Call) and getattr(node.func, "id", "") == "getattr"
                    and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant)
                    and node.args[1].value == "days")
                if named:
                    readers.add(path.relative_to(root).as_posix())
        assert readers == {"models/marshal.py", "game_logic/marshal_overview.py"}, readers

    def test_the_generals_screen_prints_them(self):
        import pathlib
        src = (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
               / "scripts" / "marshal_management.gd").read_text(encoding="utf-8")
        assert 'func _days_lines(m: Dictionary) -> String:' in src
        assert '_caption("His days")' in src
        assert src.count("bbcode += _days_lines(m)") == 2, "the page's card and the master-detail body"
        for key in ('d.get("when", "")', 'd.get("name", "")', 'd.get("verdict", "")', 'd.get("rest", "")'):
            assert key in src, key


class TestAGreatBattlesNewsNamesItsCommanders:
    """The user's tick at the plan gate — "Name the commanders". The up side
    is pinned where BA-4's news is (`tests/test_ba4_the_roads_and_the_fog.py`);
    here its sentences, and the seam's down twin."""

    def test_the_sentences(self):
        from backend.game_logic import battle_news
        line = battle_news.line_of
        men = ("Hohenlohe", "Archduke John")
        assert line("Lithuania", "Prussia", "Austria", ("held", "Prussia"), great=True, commanders=men) == (
            "News from Lithuania: a great battle — Hohenlohe of Prussia held the field against "
            "Archduke John of Austria.")
        assert line("Lithuania", "Prussia", "Austria", ("held", "Austria"), great=True, commanders=men) == (
            "News from Lithuania: a great battle — Archduke John of Austria held the field against "
            "Hohenlohe of Prussia.")
        assert line("Lithuania", "Prussia", "Austria", ("better", "Prussia"), great=True,
                    commanders=men).endswith("Hohenlohe of Prussia had the better of the day against "
                                             "Archduke John of Austria.")
        assert line("Lithuania", "Prussia", "Austria", ("drawn", ""), great=True, commanders=men).endswith(
            "Hohenlohe of Prussia and Archduke John of Austria fought the day to a draw.")
        assert line("Lithuania", "Prussia", "Austria", ("ruin", ""), great=True, commanders=men).endswith(
            "the armies of Hohenlohe of Prussia and Archduke John of Austria were both ruined on it.")

    def test_an_ordinary_battle_of_an_ally_stays_crowns_only(self):
        from backend.game_logic import battle_news
        said = battle_news.line_of("Lithuania", "Prussia", "Austria", ("held", "Prussia"), great=False,
                                   ally="Prussia", commanders=("Hohenlohe", "Archduke John"))
        assert said == "News from Lithuania: our ally Prussia has fought Austria — Prussia held the field."

    def test_one_name_missing_names_neither(self):
        from backend.game_logic import battle_news
        said = battle_news.line_of("Lithuania", "Prussia", "Austria", ("held", "Austria"), great=True,
                                   commanders=("Hohenlohe", ""))
        assert said == ("News from Lithuania: Prussia and Austria have fought a great battle — "
                        "Austria held the field.")

    def test_a_great_assault_names_the_man_who_led_it(self):
        from backend.game_logic import battle_news
        said = battle_news.assault_line("Vienna", "Prussia", "Austria", True, great=True, commander="Hohenlohe")
        assert said.startswith("News from Vienna: Hohenlohe of Prussia has thrown a great assault on the works of Austria")
        plain = battle_news.assault_line("Vienna", "Prussia", "Austria", True, great=True)
        assert plain.startswith("News from Vienna: Prussia has thrown a great assault on the works of Austria")

    def test_seam_down_a_great_battles_news_is_crowns_only(self, monkeypatch):
        from backend.game_logic import battle_news
        from tests.test_ba4_the_roads_and_the_fog import _lithuania, _news
        monkeypatch.setattr(battle_news, "a_great_battle_names_its_commanders", lambda: False)
        world, _reply, _before = _lithuania()
        [news] = _news(world)
        assert news["line"].startswith("News from Lithuania: Prussia and Austria have fought a great battle — ")
        assert "Hohenlohe" not in news["line"] and "commanders" not in news


class TestTheSpeedOfTheActs:
    """The user's tick at the plan gate — "Speed for the acts". A switch in
    Close's room while something plays; the engine's clock is the acts' only
    then, and only at twice the speed. (The walk of record presses it with a
    real click: claims BA5-s1 … s4, each watched failing in the switch-off
    table.)"""

    @staticmethod
    def _gd(name):
        import pathlib
        return (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
                / "scripts" / name).read_text(encoding="utf-8")

    def test_the_setting(self):
        settings = self._gd("ui_settings.gd")
        assert 'const BATTLE_SPEEDS := ["x1", "x2"]' in settings
        assert 'const DEFAULT_BATTLE_SPEED := "x1"' in settings
        assert 'const BATTLE_SPEED_FACTORS := {"x1": 1.0, "x2": 2.0}' in settings
        assert '_config().get_value("display", "battle_speed", DEFAULT_BATTLE_SPEED)' in settings
        panel = self._gd("settings_panel.gd")
        assert '_battle_speed.name = "BattleSpeedOption"' in panel
        assert "UiSettings.set_battle_speed(" in panel
        assert "_battle_speed.select(maxi(UiSettings.BATTLE_SPEEDS.find(UiSettings.get_battle_speed()), 0))" in panel

    def test_the_helper_writes_no_setting_and_the_tableau_does(self):
        acts, host = self._gd("battle_acts.gd"), self._gd("battle_diorama.gd")
        assert "UiSettings.set_" not in acts, "Golden Rule 6: the acts are display only"
        assert "host.keep_battle_speed(next)" in acts
        assert "func keep_battle_speed(speed: String) -> void:" in host
        assert "UiSettings.set_battle_speed(speed)" in host
        assert host.count("_acts.") == 5, "the host's five hooks, and no sixth"

    def test_the_clock_is_taken_only_past_its_own_pace_and_given_back(self):
        acts = self._gd("battle_acts.gd")
        clock = acts.split("static func _run_the_clock(factor: float, keeper: int) -> void:", 1)[1]
        clock = clock.split("\nfunc ", 1)[0]
        assert "if is_equal_approx(factor, 1.0):" in clock
        assert "if _clock_held and _clock_keeper == keeper:" in clock, "only the switch that holds it gives it back"
        assert "Engine.time_scale = _clock_base\n" in clock
        assert "_clock_base = Engine.time_scale" in clock, "what the clock read before is what it reads after"
        assert "Engine.time_scale = _clock_base * factor" in clock
        assert acts.count("Engine.time_scale = ") == 2, "one take, one give back, in one function"
        switch = acts.split("class SpeedSwitch:", 1)[1].split("\n# ──", 1)[0]
        assert "NOTIFICATION_VISIBILITY_CHANGED" in switch and "NOTIFICATION_EXIT_TREE" in switch

    def test_the_switch_is_not_a_click_on_the_table(self):
        acts = self._gd("battle_acts.gd")
        build = acts.split("func _build_the_speed() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "sw.focus_mode = Control.FOCUS_NONE" in build, "Space and Enter stay the table's"
        assert "MOUSE_FILTER" not in build, "a Button stops the click: it never reaches the table's skip"
        assert "host._transients.append(sw)" in build, "freed when the next table is laid"
        assert "hint.visibility_changed.connect(sw.follow)" in build


class TestTheGroundOnTheTable:
    """The user's tick at the plan gate — "The ground on the table". A
    tableau's payload carries the terrain of the province it was fought in and
    the table draws it on the felt, under the men and every label, on the
    defender's half. (The walk of record reads the drawn node: claim BA5-g.)"""

    @staticmethod
    def _gd(name):
        import pathlib
        return (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
                / "scripts" / name).read_text(encoding="utf-8")

    def _a_battle(self, table):
        world = table.world
        _seat(world, ours=30000, his=9000)
        world.clear_turn_battles()
        return table.order("Ney, attack Mack")["battle_diorama"]

    def test_a_field_battles_table_carries_its_provinces_terrain(self, table):
        from backend.models.region import VALID_TERRAINS
        tableau = self._a_battle(table)
        region = table.world.get_region(tableau["region"])
        assert tableau["ground"] == region.terrain and tableau["ground"] in VALID_TERRAINS

    def test_it_is_the_terrain_the_province_has(self, table):
        world = table.world
        _seat(world)
        world.get_region("Lorraine").terrain = "forest"
        world.clear_turn_battles()
        assert table.order("Ney, attack Mack")["battle_diorama"]["ground"] == "forest"

    def test_seam_down_the_felt_is_bare(self, table, monkeypatch):
        from backend.game_logic import battle_diorama
        monkeypatch.setattr(battle_diorama, "the_table_shows_its_ground", lambda: False)
        assert "ground" not in self._a_battle(table)

    def test_the_three_tableaux_take_it_from_one_function(self):
        import inspect
        from backend.game_logic import battle_diorama, siege_diorama
        assert "payload.update(ground_key(world, battle_region))" in inspect.getsource(
            battle_diorama.build_battle_diorama)
        for build in (siege_diorama.build_assault_diorama, siege_diorama.build_bombardment_diorama):
            assert "**_bd.ground_key(world, region_name)," in inspect.getsource(build), build.__name__
        world = SimpleNamespace(get_region=lambda name: SimpleNamespace(terrain="hills") if name == "Tyrol" else None)
        assert battle_diorama.ground_key(world, "Tyrol") == {"ground": "hills"}
        assert battle_diorama.ground_key(world, "the Channel") == {}, "a fleet action's waters are no province"

    def test_the_client_draws_every_terrain_the_game_has(self):
        from backend.models.region import VALID_TERRAINS
        acts = self._gd("battle_acts.gd")
        kinds = re.search(r'const KINDS := \[([^\]]*)\]', acts.split("class Ground:", 1)[1]).group(1)
        assert {k.strip().strip('"') for k in kinds.split(",")} == set(VALID_TERRAINS)
        draw = acts.split("class Ground:", 1)[1].split("func _draw() -> void:", 1)[1].split("\n\t#", 1)[0]
        for terrain in VALID_TERRAINS:
            assert f'"{terrain}":' in draw, terrain

    def test_it_lies_under_the_men_and_on_the_defenders_half(self):
        acts = self._gd("battle_acts.gd")
        build = acts.split("func _build_the_ground() -> void:", 1)[1].split("\nclass ", 1)[0]
        assert 'var kind := str(host._data.get("ground", ""))' in build
        assert "if not Ground.KINDS.has(kind):\n\t\treturn" in build, "a payload without one draws nothing"
        assert "g.dir = 1.0 if _attacker_left() else -1.0" in build
        assert "host._stage.move_child(g, 1)" in build, "over the felt, under the lamp, the men and every label"
        assert "host._transients.append(g)" in build, "freed when the next table is laid"
        dress = acts.split("func dress(final_frame: bool) -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert dress.index("if host._is_naval():") < dress.index("_build_the_ground()"), "no ground at sea"

    def test_a_field_looks_the_same_every_time_it_is_fought_on(self):
        acts = self._gd("battle_acts.gd")
        ground = acts.split("class Ground:", 1)[1].split("\n# ──", 1)[0]
        assert 'rng.seed = (kind + "|" + seed_text).hash()' in ground
        assert "randomize()" not in ground and "randf()" in ground
        assert ground.count("var rng := _rng()") == 6, "one seeded stream a terrain"


class TestTheClientsOwnDefects:
    """D2, D3, D4 and D6 lived in the client: each is pressed or read in the
    real client by the walk of record and the live walk (their claims and
    steps are named below); these pin the lines the fixes stand on."""

    @staticmethod
    def _gd(name):
        import pathlib
        return (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
                / "scripts" / name).read_text(encoding="utf-8").replace("\r\n", "\n")

    def test_a_cards_second_line_reads_above_the_contrast_floor(self):
        """BA5-X9: what a word does was written in the info grey on the card's
        own ground — 4.21 to 1, under the game's 4.5 floor (the contrast
        instrument on the frozen pass's captures: 35 rows, all this line)."""
        acts, utils = self._gd("battle_acts.gd"), self._gd("utils.gd")

        def const(src, name):
            return re.search(rf'{name}\s*(?::\s*String)?\s*:?=\s*(?:toned_hex\()?"([0-9a-fA-F]{{6}})"', src).group(1)

        def lum(hexed):
            parts = [int(hexed[i:i + 2], 16) / 255 for i in (0, 2, 4)]
            lin = [p / 12.92 if p <= 0.03928 else ((p + 0.055) / 1.055) ** 2.4 for p in parts]
            return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

        def ratio(ink, ground):
            hi, lo = sorted((lum(ink), lum(ground)), reverse=True)
            return (hi + 0.05) / (lo + 0.05)

        ground = const(acts, "const DAY_CARD_BG")
        assert ratio(const(acts, "const DAY_CAPTION_INK"), ground) >= 4.5
        assert ratio(const(utils, "const COLOR_GOLD"), ground) >= 4.5, "the word itself, on the same ground"
        assert ratio(const(utils, "COLOR_INFO"), ground) < 4.5, "the ink it was written in"
        card = acts.split("func _day_card_bb(i: int, chip: Dictionary) -> String:", 1)[1].split("\nfunc ", 1)[0]
        assert "var sub := DAY_CAPTION_INK if lit else Utils.CHIP_DIM_INK" in card

    def test_d2_the_days_latest_clash_is_the_table(self):
        """The closing table of a day showed the men and the dice of the clash
        that was on screen when the word was given, not the day's last."""
        main = self._gd("main.gd")
        assert "const DAY_SHOWS_ITS_LATEST_CLASH := true" in main
        latest = main.split("func _the_days_latest_table(enemy: String, fallback):", 1)[1].split("\nfunc ", 1)[0]
        assert "_day_tables.get(enemy, null) if DAY_SHOWS_ITS_LATEST_CLASH else null" in latest
        assert main.count("_the_days_latest_table(") == 3, "its definition, the word's stash, the refresh"
        # a day's tableau that is RAISED is the day's latest, whatever road brought it
        # (the live walk: his clash after a word that raised the muster's question was
        # shown and never remembered, and the day closed on our own clash before it)
        raises = main.split("func _the_day_raises(data) -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "last_battle_diorama = data" in raises, "\"View the field\" opens the day's latest clash"
        assert "_day_tables[key] = data" in raises, "and a word with no clash closes on it"
        assert main.count("_the_day_raises(") == 4, "its definition and the three places a day's table is raised"
        for site in ("func _show_pending_diorama", "func _day_raise_over_list", "func _on_battle_diorama_dismissed"):
            body = main.split(site, 1)[1].split("\nfunc ", 1)[0]
            assert body.index("_the_day_raises(") < body.index("battle_diorama.show_diorama("), site

    def test_d3_the_verdict_stands_whole_in_its_room(self):
        acts = self._gd("battle_acts.gd")
        fit = acts.split("func _fit_the_verdict() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "v.visible_characters = -1" in fit, "measured whole: what the quill has not written is not laid out"
        assert "v.visible_characters = shown" in fit
        assert "var tries: Array = [[VERDICT_STEP, _verdict_source], [VERDICT_STEP_SMALL, _verdict_source]]" in fit, (
            "as it is, then a step smaller, before a word is folded away")
        assert "Utils.bb_hint(_with_more(kept), every_word)" in fit, "what is folded is in the hover, whole"
        assert fit.index("for step in [VERDICT_STEP, VERDICT_STEP_SMALL]:") < fit.index("for candidate in tries:")
        # (the house rule, UXR-2/S12: a size is a ladder step of its label, never a BBCode size)
        assert "[font_size" not in fit and "v.theme_type_variation = pick[0]" in fit
        assert 'const VERDICT_STEP := &"BodyLargeRich"' in acts and 'const VERDICT_STEP_SMALL := &"CaptionRich"' in acts
        back = acts.split("func _put_the_chrome_back() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "host._verdict.theme_type_variation = VERDICT_STEP" in back, "every table laid starts from its own step"
        lift = acts.split("func _lift_the_verdict() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "if _shelf_up():" in lift and "host._verdict.position.y -= VERDICT_LIFT" in lift
        assert "const VERDICT_LIFT := 4.0" in acts
        dress = acts.split("func dress(final_frame: bool) -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert dress.index("_build_the_day()") < dress.index("_lift_the_verdict()"), (
            "the day's panel reads the verdict's own top first")
        settle = acts.split("\nfunc settle() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "_verdict_refits = 2" in settle and "process_frame.connect(_refit_the_verdict, CONNECT_ONE_SHOT)" in settle, (
            "the plate is measured a frame late: a settled table fits its verdict again")
        assert "_fit_the_verdict()                 # BA5-D3" in acts, "and a beat's line as it is shown"

    def test_d4_an_exact_strength_is_printed_once(self):
        card = self._gd("order_confirm_card.gd")
        assert 'if low == high and label == band_text + " men":' in card

    def test_d6_the_throw_is_read_when_the_dice_have_landed(self):
        acts = self._gd("battle_acts.gd")
        tray = acts.split("class DiceTray:", 1)[1]
        assert "signal landed" in tray and "landed.emit()" in tray.split("func settle() -> void:", 1)[1].split("\n\tfunc ", 1)[0]
        roll = tray.split("func roll() -> void:", 1)[1].split("\n\tfunc ", 1)[0]
        assert "(row as CanvasItem).visible = false" in roll, "nothing of the throw is told while it tumbles"
        assert "_dice.landed.connect(_read_the_throw.bind(host._verdict.text), CONNECT_ONE_SHOT)" in acts
        assert "host._verdict.visible_characters = 0" in acts, "the throw's sentence waits with them"


class TestTheDaysSoundsAndHelp:
    """The user's tick — "Sounds for the day": the day's own beats in cues the
    game already has, through the tableau's own cue road (the "Battle sounds"
    setting). And Help & Keys says what the table now shows."""

    @staticmethod
    def _gd(name):
        import pathlib
        return (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
                / "scripts" / name).read_text(encoding="utf-8").replace("\r\n", "\n")

    def test_every_cue_of_the_day_is_one_the_game_has(self):
        acts, audio = self._gd("battle_acts.gd"), self._gd("audio_manager.gd")
        named = set()
        for const in ("DAY_WORD_CUES", "DAY_HIS_CUES", "DAY_END_CUES"):
            body = acts.split(f"const {const} := {{", 1)[1].split("}", 1)[0]
            named |= set(re.findall(r':\s*"([a-z_]+)"', body))
        assert {"bugle_to_arms", "drum_cadence", "spade", "cannon_distant", "bugle_retreat"} <= named
        for cue in named:
            assert f'"{cue}":' in audio, f"the cue {cue!r} is not registered"

    def test_they_go_by_the_tableaus_own_cue_road(self):
        acts = self._gd("battle_acts.gd")
        sound = acts.split("func _sound_the_day() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "host._cue(" in sound and "AudioManager.play(" not in sound, "the Battle sounds setting is the host's guard"
        assert "_day_sounded[enemy] = mark" in sound and "== mark:" in sound, "a table shown again says nothing twice"
        press = acts.split("func _on_day_chip(meta) -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "host._cue(str(DAY_WORD_CUES.get(" in press

    def test_help_says_the_readings_three_states_and_the_reserves_own_figure(self):
        terms = self._gd("codex_terms.gd")
        reading = next(line for line in terms.split("\n") if line.lstrip().startswith('["Berthier\'s reading"'))
        for state in T.READ_LINES.values():
            assert state in reading, state
        assert '["The reserve"' not in terms, "the reserve is parked: Help promises none"
        points = next(line for line in terms.split("\n") if line.lstrip().startswith('["The day\'s points"'))
        assert "digits 1 to 9" in points and "A lead holds one day at a time" in points
        news = next(line for line in terms.split("\n") if line.lstrip().startswith('["News of a battle"'))
        assert "two commanders by name" in news and "never a figure" in news


class TestOneDayALeadIsReadAsTheBattleBegan:
    """BA5-X1 — found by pressing ruling 9's card in the real client. A lead
    whose day was open, sent against another corps, won that clash on points
    and advanced: by the time "one day a lead" was read he stood off his first
    day's ground, that day read dead, and the second battle opened a day of
    its own under a card that had promised it would not. The rule is read as
    he stood when the battle BEGAN; his advance then ends the first day at
    once, and the battle's own message says he marched from it."""

    def _ney_advances_from_a_second_great_clash(self, table):
        """Ney's day against Mack open; Kienmayer on ground beside Ney's own
        (not the day's field); Ney fights him to a hanging great battle that
        carries him forward."""
        from tests.test_ba4_the_review import _a_second_corps
        from tests.test_ba4_the_roads_and_the_fog import _muster_answered
        for _ in range(60):
            table.open_a_day(_awaits_us)
            world = table.world
            ney = world.marshals["Ney"]
            home = ney.location
            # 25,000 against Ney's 70,000: a great battle (95,000 engaged) he wins
            # on points, which carries him forward (measured: eleven tries of twelve)
            kienmayer = _a_second_corps(world, men=25000)
            ney.strength, ney.morale = 70000, 80
            world.actions_remaining = 4
            body = _muster_answered(table, table.order("Ney, attack Kienmayer"))
            payload = body.get("battle_diorama") or {}
            if (payload.get("great_battle") and payload.get("outcome") in BD.HANGING
                    and table.world.marshals["Ney"].location != home):
                return body, payload, kienmayer
        raise AssertionError("no hanging great second battle carried Ney forward on sixty dice")

    def test_the_second_battle_opens_no_day_though_he_advanced(self, table):
        body, payload, kienmayer = self._ney_advances_from_a_second_great_clash(table)
        assert "day" not in payload, "a single clash, as its card said"
        words = [beat["text"] for act in payload["script"]["acts"] for beat in act["beats"]
                 if beat["kind"] == "word"]
        # (the session's review) the same response ends the first day: "is still open" stood
        # on the table of the battle that ended it
        assert words == ["Ney has marched from his day against Mack, which ends where it stands — "
                         "this clash opens none of its own."]
        assert kienmayer.name not in BD.open_days(table.world)

    def test_the_first_day_ends_at_once_and_the_battle_says_so(self, table):
        body, _payload, _kienmayer = self._ney_advances_from_a_second_great_clash(table)
        world = table.world
        assert BD.open_days(world) == {}, "he has left its ground: the day is over now, not at the next read"
        closed = [e for e in world.event_log if e.get("type") == "battle_day_closed"][-1]
        assert closed["how"] == "over" and closed["enemy"] == "Mack"
        assert closed["line"].startswith("Ney marched from the field at Lorraine after ")
        assert body["message"].endswith(closed["line"]), "told with the battle that ended it"

    def test_his_record_keeps_both(self, table):
        self._ney_advances_from_a_second_great_clash(table)
        days = table.world.marshals["Ney"].days
        assert [d["against"] for d in days] == ["Kienmayer", "Mack"]
        assert "clashes" not in days[0] and days[1]["clashes"] >= 1

    def test_the_card_says_what_winning_it_does(self, table):
        from backend.commands import order_quotes
        from tests.test_ba4_the_review import _a_second_corps
        table.open_a_day(_awaits_us, ours=30000, his=30000)
        world = table.world
        quote = order_quotes.attack_quote(world, world.marshals["Ney"], _a_second_corps(world))
        assert quote["note"].endswith("with no day of its own. Should he win it and advance, "
                                      "that day ends where it stands.")

    def test_a_day_whose_lead_stayed_is_untouched(self, table):
        """The enemy strikes a lead who holds a day: he does not move, the
        day stands and nothing is said of leaving it."""
        table.open_a_day(_awaits_us)
        world = table.world
        ney = world.marshals["Ney"]
        ctx = SimpleNamespace(world=world, marshal=ney, enemy_marshal=world.marshals["Mack"])
        BD.note_the_day_he_holds(ctx)
        assert ctx._bd_day_held == "Mack"
        assert BD.his_first_day_ends(ctx) == "" and "Mack" in BD.open_days(world)

    def test_seam_down_the_second_battle_opens_a_day_of_its_own(self, table, monkeypatch):
        """BA-4's reading, kept behind the seam: the defect as it was."""
        monkeypatch.setattr(BD, "a_lead_holds_his_day_as_the_battle_began", lambda: False)
        body, payload, kienmayer = self._ney_advances_from_a_second_great_clash(table)
        assert (payload.get("day") or {}).get("enemy") == kienmayer.name
        assert not body["message"].rstrip().endswith("of the enemy's.")


class TestAVerdictNamesWhatTold:
    """The readers' first failed check — "the verdict names a cause". A day's
    clashes said what told; a battle decided at once, and the clash that
    decided a day, did not: their tables showed a headline and Berthier's
    line. Now the table of any battle our marshal LED says under its own
    headline what told in it (`verdict_told`) — on any road, never a figure —
    and the clash that decides a day names itself."""

    @staticmethod
    def _fight(world, attacker="Ney", target="Mack", seed=3):
        executor = CommandExecutor()
        random.seed(seed)
        with contextlib.redirect_stdout(io.StringIO()):
            return executor._execute_attack(world.marshals[attacker], target, world,
                                            {"world": world, "executor": executor})

    @staticmethod
    def _gd(name):
        import pathlib
        return (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
                / "scripts" / name).read_text(encoding="utf-8").replace("\r\n", "\n")

    def test_the_line_in_its_two_forms(self):
        assert T.verdict_line("our weight of numbers told") == "Our weight of numbers told."
        assert T.verdict_line("the ground told for him") == "The ground told for him."
        assert T.verdict_line("") == "An even fight."
        assert T.verdict_line("his works told", "third") == "Decided at the third clash: his works told."
        assert T.verdict_line("an even fight", "second") == "Decided at the second clash, in an even fight."

    def test_a_battle_no_server_holds_names_what_told(self):
        world, ney, mack = _pair(ours=60000, his=20000)
        tableau = self._fight(world)["battle_diorama"]
        assert "day" not in tableau, "a world nobody serves has no day"
        assert tableau["verdict_told"] in ("Our weight of numbers told.",
                                           "Decided when Mack's line broke: our weight of numbers told.")
        assert not re.search(r"\d", tableau["verdict_told"]), "never a figure"

    def test_a_battle_lost_names_what_told_for_him(self):
        world, ney, mack = _pair(ours=20000, his=60000)
        assert self._fight(world)["battle_diorama"]["verdict_told"] in (
            "His weight of numbers told.", "Decided when Ney's line broke: his weight of numbers told.")

    def test_it_is_ours_to_read_when_we_defend(self):
        world, ney, mack = _pair(ours=60000, his=20000)
        tableau = self._fight(world, attacker="Mack", target="Ney")["battle_diorama"]
        assert tableau["verdict_told"] in ("Our weight of numbers told.",
                                           "Decided when Mack's line broke: our weight of numbers told.")

    def test_it_is_the_rules_own_word_for_the_side_that_did_better(self, monkeypatch):
        said = []
        real = T.what_told

        def heard(ctx, attacker_is_ours, better):
            said.append((bool(attacker_is_ours), better, real(ctx, attacker_is_ours, better)))
            return said[-1][2]

        monkeypatch.setattr(T, "what_told", heard)
        world, ney, mack = _pair(ours=60000, his=20000)
        tableau = self._fight(world)["battle_diorama"]
        ours_attack = [row for row in said if row[0]]
        assert ours_attack and ours_attack[-1][1] == "ours"
        assert tableau["verdict_told"] == T.verdict_line(ours_attack[-1][2])

    def test_a_battle_between_other_crowns_names_nothing(self):
        ctx = SimpleNamespace(world=SimpleNamespace(player_nation="France"),
                              marshal=SimpleNamespace(name="Mack", nation="Austria"),
                              enemy_marshal=SimpleNamespace(name="Kutuzov", nation="Russia"))
        assert BD.the_verdicts_line(ctx) == "", "the fog law: a battle we led no side of tells us no cause"

    def test_a_days_own_table_says_it_in_its_lines(self, table):
        body, day = table.open_a_day()
        assert "verdict_told" not in body["battle_diorama"], "a day's lines say what told, clash by clash"
        assert any(t.get("kind") == "clash" for t in day["told"])
        assert BD.the_verdicts_line(None, day) == ""

    def test_the_clash_that_decides_a_day_names_itself(self, table):
        for _ in range(80):
            table.open_a_day(_awaits_us, ours=90000, his=52000)
            body = table.order("Ney, attack Mack")
            said = body.get("battle_day") or {}
            if said.get("ended") == "decided":
                break
        else:
            raise AssertionError("no press decided a day")
        tableau = body["battle_diorama"]
        line = tableau["verdict_told"]
        nth = re.search(r"decided at the (\w+) clash", said["close"]).group(1)
        assert line.startswith(f"Decided at the {nth} clash"), line
        assert said["verdict_told"] == line and not re.search(r"\d", line)
        assert tableau["day"]["banner"] == "", "the deciding clash keeps its own headline: the line stands under it"

    def test_seam_down_the_headline_stands_alone(self, table, monkeypatch):
        monkeypatch.setattr(T, "a_verdict_names_what_told", lambda: False)
        world, ney, mack = _pair(ours=60000, his=20000)
        assert "verdict_told" not in self._fight(world)["battle_diorama"]
        for _ in range(80):
            table.open_a_day(_awaits_us, ours=90000, his=52000)
            body = table.order("Ney, attack Mack")
            if (body.get("battle_day") or {}).get("ended") == "decided":
                break
        else:
            raise AssertionError("no press decided a day")
        assert "verdict_told" not in body["battle_diorama"] and "verdict_told" not in body["battle_day"]

    def test_the_table_writes_it_under_its_headline(self):
        acts = self._gd("battle_acts.gd")
        dress = acts.split("func _dress_the_kind() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert 'host._data.get("verdict_told", "")' in dress
        assert 'host._sub_banner.text = told if host._sub_banner.text == "" else host._sub_banner.text + " " + told' in dress, (
            "after the host's own line where the province changed hands")
        assert dress.index('"sub_banner"') < dress.index('"verdict_told"'), "a payload's own sub-banner stands first"

    def test_the_dice_name_who_threw_them(self):
        acts = self._gd("battle_acts.gd")
        tray = acts.split("class DiceTray:", 1)[1].split("func settle() -> void:", 1)[0]
        assert 'Utils.display_marshal_name(str(roll.get("actor", "")))' in tray
        assert '"%s throws %d" % [thrower, natural]' in tray and '"thrown %d" % natural' in tray, (
            "a payload that names no thrower reads as before")

    def test_help_says_how_it_is_chosen(self):
        terms = self._gd("codex_terms.gd")
        entry = next(line for line in terms.split("\n") if line.lstrip().startswith('["What told"'))
        for words in ("5 to 4", "10 points or more", "3 or more from seven", "an even fight",
                      "the clash that decides a day is named", "the attacker's throw"):
            assert words in entry, words
        names = [m for m in re.findall(r'^\t\["([^"]+)",', terms.split("const ORDER_GRAMMAR", 1)[0], flags=re.M)]
        assert names[-2:] == ["War score", "What told"], "the terms stay A to Z"


class TestARoutWonOnPointsHasLeftTheField:
    """Berthier's line on the deciding table: "THE FIELD IS OURS … ROUTED …
    Decided at the second clash" stood over "A costly day for Mack: the losses
    ran two to one in Napoleon's favour, and Mack is still in the field."
    SF7-X32's family — a two-to-one exchange won on points, an enemy who still
    stands — was spoken of an enemy the same clash had driven off."""

    @staticmethod
    def _battle(routed):
        return {
            "outcome": "attacker_tactical_victory",
            "attacker": {"name": "Napoleon", "casualties": 1379},
            "defender": {"name": "Mack", "casualties": 29557, "forced_retreat": bool(routed)},
            "attacker_nation": "France", "defender_nation": "Austria",
            "attacker_original_strength": 94205, "defender_original_strength": 30557,
            "modifier_snapshot": {"attacker": [], "defender": []},
        }

    @staticmethod
    def _bank(name):
        from backend.game_logic import battle_report as BR
        return {line.format(marshal="Napoleon", enemy="Mack") for line in BR._OBSERVATIONS[name]}

    def _line(self, routed):
        from backend.game_logic import battle_report as BR
        BR.reset_observation_rotation()
        return BR._pick_observation(self._battle(routed), "France")

    def test_an_enemy_driven_off_is_not_still_in_the_field(self):
        line = self._line(routed=True)
        assert line in self._bank("won_the_exchange_and_the_field"), line
        assert "still in the field" not in line and "decided nothing" not in line and "not yet" not in line
        assert "decisive" not in line.lower(), "SF7-X32 stands: a tactical result is not called decisive"

    def test_an_enemy_who_stands_is_spoken_of_as_before(self):
        assert self._line(routed=False) in self._bank("won_the_exchange")

    def test_the_new_lines_say_we_of_no_one(self):
        for line in self._bank("won_the_exchange_and_the_field"):
            assert " we " not in f" {line.lower()} " and "ours" not in line.lower(), line

    def test_seam_down_it_is_sf7s_family(self, monkeypatch):
        from backend.game_logic import battle_report as BR
        monkeypatch.setattr(BR, "a_rout_won_on_points_has_left_the_field", lambda: False)
        assert self._line(routed=True) in self._bank("won_the_exchange")


class TestTheExitsSayWhatTheyDoBesideTheButtons:
    """At the shipped Text size no staged day's exits said what they do: on a
    row of their own they do, and that row was the first thing the table gave
    up. Level with the buttons the row now keeps what it can — in a fixed
    order (leave it to the marshal, leave the field, stand), as far as it fits
    left of Replay; the rest ride their hovers as before."""

    @staticmethod
    def _gd(name):
        import pathlib
        return (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
                / "scripts" / name).read_text(encoding="utf-8").replace("\r\n", "\n")

    def test_the_order_is_fixed_and_the_fit_is_measured(self):
        acts = self._gd("battle_acts.gd")
        assert 'const DAY_TAG_ORDER := ["leave_it", "break_off", "stand"]' in acts
        build = acts.split("func _build_the_day() -> void:", 1)[1].split("\nfunc ", 1)[0]
        fit = build.split("if not exit_cards and can_tag:", 1)[1].split("if first_box != null:", 1)[0]
        assert "for kept in range(DAY_TAG_ORDER.size(), 0, -1):" in fit
        assert "if e_box.get_content_width() <= DAY_CHIPS_W:" in fit, "the row fits left of Replay, or the tag goes"
        assert build.index("_day_tags_kept = 0") < build.index("for _step in range(14):"), (
            "the ladder itself is measured with every tag or none")

    def test_an_exits_turn_is_read_from_its_word_and_kind(self):
        acts = self._gd("battle_acts.gd")
        rank = acts.split("func _day_exit_rank(chip: Dictionary) -> int:", 1)[1].split("\nfunc ", 1)[0]
        assert 'if str(chip.get("word", "")) == "leave_it":' in rank and "return 0" in rank
        assert 'DAY_TAG_ORDER.find(str(chip.get("kind", "")))' in rank
        tagged = acts.split("func _day_exit_tagged(chip: Dictionary) -> bool:", 1)[1].split("\nfunc ", 1)[0]
        assert "if _day_exit_tags:" in tagged and "rank < _day_tags_kept" in tagged
        text = acts.split("func _day_exits_text() -> String:", 1)[1].split("\nfunc ", 1)[0]
        assert "_day_chip_bb(int(i), chip, false, _day_exit_tagged(chip))" in text

    def test_the_staged_scenes_say_the_first_days_line_once(self):
        """Every staged world is a fresh campaign: every day scene carried the
        first day's two-line lecture, which a campaign says once."""
        from tools import ba1_stage_battles as stage
        assert stage.FIRST_DAY_SCENES == ("day_opens", "day_crowded", "day_guns")
        assert set(stage.FIRST_DAY_SCENES) <= set(stage.SCENES)
        import inspect
        fight = inspect.getsource(stage.fight)
        assert 'first_open.seen(world)["battle_day"] = ' in fight and "if name not in FIRST_DAY_SCENES:" in fight

    def test_a_scene_that_is_not_the_first_day_carries_no_such_line(self):
        from tools import ba1_stage_battles as stage

        def staged(name):
            for ambient in range(stage.SEEDS_TRIED):
                with contextlib.redirect_stdout(io.StringIO()):
                    payload, reason, _result = stage.fight(name, ambient)
                if payload is not None and reason:
                    return payload
            raise AssertionError(f"{name} did not stage")

        dice = random.getstate()
        try:
            first, later = staged("day_guns"), staged("day_defence")
        finally:
            random.setstate(dice)
        assert first["day"].get("first_open"), "a campaign's first day says its own line"
        assert not later["day"].get("first_open"), "a day that is not the first does not say it again"


class TestTheStagedDimChipIsATableTheGameShows:
    """The scene behind the frame "a chip is dim" zeroed the purse by hand and
    laid the live day over the OPENING's table though he had struck since: the
    counters and the dice of one clash over a told line of another — a table
    the game no longer shows (BA5-D1), and the frame the first reading's
    critic named for figures that do not agree. The chips ride the table of
    the day's latest clash."""

    @staticmethod
    def _staged():
        from tools import ba1_stage_battles as stage
        dice = random.getstate()
        try:
            for ambient in range(stage.SEEDS_TRIED):
                with contextlib.redirect_stdout(io.StringIO()):
                    payload, reason, _result = stage.fight("day_dim_chip", ambient)
                if payload is not None and reason:
                    return payload
        finally:
            random.setstate(dice)
        raise AssertionError("day_dim_chip did not stage")

    def test_the_counters_the_dice_and_the_told_line_are_one_clashs(self):
        payload = self._staged()
        day = payload["day"]
        assert day["open"] and day["awaits"] == "ours" and day["ours"] == 0
        last = [t["line"] for t in day["told"] if t.get("kind") == "clash"][-1]
        ours, his = _toll_of(payload)
        assert ours in _figures(last) and his in _figures(last), (
            "the table's counters are the clash the last told line is about", ours, his, last)
        thrower = next(b for act in payload["script"]["acts"] for b in act["beats"]
                       if b.get("kind") == "dice")["actor"]
        attacker = payload["attacker"]["contingents"][0]["name"] if payload["attacker"].get("contingents") else thrower
        assert thrower == attacker, "the dice on the table are that clash's attacker's"

    def test_the_priced_words_are_dim_with_their_reason_and_the_free_ones_lit(self):
        day = self._staged()["day"]
        priced = [c for c in day["chips"] if int(c.get("price", 0)) > 0]
        free = [c for c in day["chips"] if int(c.get("price", 0)) == 0]
        assert priced and all(not c["ok"] and c["why"] == "The day's points are spent." for c in priced)
        assert free and all(c["ok"] for c in free)


# ════════════════════════════════════════════════════════
# The second reading
# ════════════════════════════════════════════════════════

class TestTheSecondReading:
    """The blind reading was taken again on the finished table — two fresh
    readers, the same briefs, the frames re-shot — and missed the bar written
    before the work (agency 5 and decision clarity 5, against 7). What both
    asked for first is built here, and no number of the game moves: the price
    AND the consequence on every control, the day's stakes beside the words
    they govern, one vocabulary for the odds and the toll, the decisive moment
    by name, and what a day that ends undecided comes to."""

    @staticmethod
    def _gd(name):
        import pathlib
        return (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
                / "scripts" / name).read_text(encoding="utf-8").replace("\r\n", "\n")

    @staticmethod
    def _func(source, name):
        return source.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]

    # ── the server's words ──

    def test_the_verdict_names_the_moment_a_line_broke(self):
        assert T.verdict_line("our weight of numbers told", broke="Mack") == (
            "Decided when Mack's line broke: our weight of numbers told.")
        assert T.verdict_line("an even fight", broke="Mack") == "Decided when Mack's line broke, in an even fight."
        assert T.verdict_line("his works told", "third", "Ney") == (
            "Decided at the third clash, when Ney's line broke: his works told.")
        assert T.verdict_line("an even fight", "second", "Ney") == (
            "Decided at the second clash, when Ney's line broke, in an even fight.")

    def test_whose_line_broke_is_read_from_the_battles_own_result(self):
        def ctx(attacker=False, defender=False):
            return SimpleNamespace(
                battle_result={"attacker": {"forced_retreat": attacker},
                               "defender": {"forced_retreat": defender}},
                marshal=SimpleNamespace(name="Ney"), enemy_marshal=SimpleNamespace(name="Mack"))
        assert BD._whose_line_broke(ctx(defender=True)) == "Mack"
        assert BD._whose_line_broke(ctx(attacker=True)) == "Ney"
        assert BD._whose_line_broke(ctx()) == "", "neither line broke: no moment is named"
        assert BD._whose_line_broke(ctx(True, True)) == "", "both broke: neither is the moment"

    def test_a_battle_that_drove_a_lead_off_names_him_under_its_headline(self, monkeypatch):
        """Through the executor: the line is the rule's own word for what told,
        after the moment the battle's own result gives."""
        heard = []
        real = BD._whose_line_broke

        def listen(ctx):
            heard.append(real(ctx))
            return heard[-1]

        monkeypatch.setattr(BD, "_whose_line_broke", listen)
        world, ney, mack = _pair(ours=60000, his=20000)
        tableau = TestAVerdictNamesWhatTold._fight(world)["battle_diorama"]
        assert heard, "the verdict's line asked whose line broke"
        want = (f"Decided when {heard[-1]}'s line broke: our weight of numbers told." if heard[-1]
                else "Our weight of numbers told.")
        assert tableau["verdict_told"] == want

    def test_seam_down_no_moment_and_no_cause_is_said(self, monkeypatch):
        monkeypatch.setattr(T, "a_verdict_names_what_told", lambda: False)
        world, ney, mack = _pair(ours=60000, his=20000)
        assert "verdict_told" not in TestAVerdictNamesWhatTold._fight(world)["battle_diorama"]

    def test_an_assaults_verdict_names_what_told_at_the_wall(self):
        # (the session's review) "the walls told" only where works stood behind them
        assert T.assault_told(True, True, 30000, 12000, fortified=True) == "The walls told for the garrison."
        assert T.assault_told(True, False, 30000, 12000, fortified=True) == "Our walls told."
        assert T.assault_told(False, True, 30000, 12000) == "Our weight of numbers told."
        assert T.assault_told(False, False, 30000, 12000) == "His weight of numbers told."
        assert T.assault_told(False, True, 14000, 12000) == "", "under 5 to 4 a wall carried names no cause"

    def test_an_assaults_table_carries_it_only_for_the_court_that_fought(self):
        import inspect

        from backend.game_logic import siege_diorama as SD
        source = inspect.getsource(SD.build_assault_diorama)
        gate = source.split("if player_side is not None:", 1)[1].split("if siege is not None:", 1)[0]
        assert "_telling.a_verdict_names_what_told()" in gate, "behind the verdict's own seam"
        assert "_telling.assault_told(" in gate and 'held, player_side == "attacker",' in gate
        assert 'payload["verdict_told"] = told' in gate

    def test_to_dig_in_says_its_number_and_the_number_is_the_models(self):
        from backend.models.marshal import Stance
        world, ney, mack = _pair()
        for lead, want in ((mack, 15), (ney, 9)):
            lead.stance = Stance.NEUTRAL
            neutral = lead.get_defense_modifier(consume=False)
            assert T.does_dig_in(lead) == f"defensive stance: +{want}% if he strikes", lead.name
            assert lead.stance == Stance.NEUTRAL, "the reading puts his stance back"
            lead.stance = Stance.DEFENSIVE
            dug_in = lead.get_defense_modifier(consume=False)
            assert round((dug_in / neutral - 1.0) * 100) == want, (
                "the card's figure is the model's own (`Marshal.get_defense_modifier`): an aggressive "
                "temper makes the stance worth less", lead.name)
            assert T.does_dig_in(lead) == "field works: firmer still if he strikes", (
                "a lead already in the stance throws up works: they grow by the turn and carry no one figure")
        ney.stance = Stance.AGGRESSIVE
        assert T.does_dig_in(ney).startswith("defensive stance: +") and ney.stance == Stance.AGGRESSIVE

    def test_every_exit_says_that_the_day_ends(self, table):
        body, day = table.open_a_day(_awaits_us)
        assert _chip(day, word="break_off")["does"] == "the day ends; he keeps the field"
        assert T.DOES["fall_back"] == "the day ends; he takes the field"
        assert T.DOES["stand_night"] == "night falls, undecided"
        for chip in day["chips"]:
            assert chip.get("does"), ("every word of a day says what it does", chip.get("label"))

    def test_a_card_whose_figure_is_the_days_count_says_whose_figure_it_is(self):
        counted = {"force": {"ours": 38210, "theirs_low": 47175, "theirs_high": 47175, "odds": ""}}
        assert T.does_attack("press", counted) == "by the day's count — 38,210 on 47,175"
        sighted = {"force": {"ours": 35195, "theirs_low": 49704, "theirs_high": 49704, "odds": "unfavorable"}}
        assert T.does_attack("press", sighted) == "odds: unfavorable — 35,195 on 49,704"
        banded = {"force": {"ours": 35195, "theirs_low": 40000, "theirs_high": 60000,
                            "theirs_label": "a large force", "odds": ""}}
        assert T.does_attack("press", banded) == "35,195 on a large force", "a band is no count: it stands as it was"

    def test_a_day_no_clash_decided_says_what_follows(self, table):
        assert T.what_follows("night") == "Neither army is driven off; the fight may be renewed tomorrow."
        assert T.what_follows("broke_off") == T.what_follows("he_broke_off") == "Neither army is driven off."
        for how in ("decided", "drew_off", "fell_back", "over", ""):
            assert T.what_follows(how) == "", (how, "a day that moved a corps says no such thing")
        table.open_a_day(_awaits_us)
        closing = table.word("break_off")["battle_day"]
        assert closing["told"][-1] == {"who": "end", "kind": "after", "line": "Neither army is driven off."}
        assert "Neither army" not in closing["close"], "the campaign log's line is BA-4's and BA-5's, as it was"

    def test_what_follows_is_true_of_the_rule(self, table):
        """A day broken off moves nobody: both leads stand where they stood."""
        table.open_a_day(_awaits_us)
        before = {name: m.location for name, m in table.world.marshals.items()}
        table.word("break_off")
        assert {name: m.location for name, m in table.world.marshals.items()} == before

    def test_seam_down_nothing_follows(self, table, monkeypatch):
        monkeypatch.setattr(T, "the_close_names_what_told", lambda: False)
        table.open_a_day(_awaits_us)
        closing = table.word("break_off")["battle_day"]
        assert not any(t["kind"] == "after" for t in closing["told"])

    # ── the client's table ──

    def test_the_stakes_head_the_panel_in_words_and_the_band_names_the_battle(self):
        acts = self._gd("battle_acts.gd")
        head = self._func(acts, "_day_head")
        assert '"%d of %d points[/color] " % [ours, slots_ours]' in head, "the purse in words, beside its pips"
        assert '"%d of %d[/color]" % [theirs, slots_his]' in head
        assert "The day's points" not in head, "the prefix gave its room to the words"
        build = self._func(acts, "_build_the_day")
        assert "var y: float = head_h                     # the head is the panel's first row" in build
        assert "head.position" not in build, "the head stands where it is made: the panel's own top"
        assert "name_label.position = Vector2(0.0, DAY_HEAD_Y - top)" in build, "the band above the baize is the name's"
        name = self._func(acts, "_day_name")
        assert 'host._data.get("battle_name", "")' in name and '"%s  ·  TURN %d"' in name

    def test_the_rule_stands_on_a_table_that_offers_its_words(self):
        acts = self._gd("battle_acts.gd")
        rule = acts.split('const DAY_RULE := "', 1)[1].split('"', 1)[0]
        for words in ("A word costs points", "A line that breaks decides the day",
                      "two silences running, or no point left, and night falls: nothing decided"):
            assert words in rule, words
        build = self._func(acts, "_build_the_day")
        assert "var rule_row: bool = rule_box != null and not first_row" in build, (
            "the first day's own line says the rule in full: one of the two stands")
        assert "if rule_box.get_content_width() > DAY_W - 8.0:" in build, "one whole line or not on the table"
        assert build.index("elif rule_row:") < build.index("elif told_row:") < build.index("elif first_row:") \
            < build.index("elif exit_cards:") < build.index("elif cards:"), (
            "the ladder: the rule, the told line and the first day's line give way before a word loses "
            "what it does")

    def test_an_exit_is_a_card_with_its_price_and_what_it_does(self):
        acts = self._gd("battle_acts.gd")
        card = self._func(acts, "_day_exit_card_bb")
        assert 'var paid := "free" if price <= 0 else' in card
        assert 'var caption := (paid + (" · " + does if does != "" else "")) if (lit or why == "") else why' in card
        assert "DAY_EXIT_RIM" in card and "DAY_EXIT_CARD_BG" in card and "DAY_EXIT_INK" in card, (
            "quieter than a word that costs points")
        text = self._func(acts, "_day_exits_text")
        assert "if _day_exit_tags:" in text and "_day_exit_card_bb(int(i), chip)" in text
        build = self._func(acts, "_build_the_day")
        assert "if exit_cards and e_box.get_content_width() > DAY_CHIPS_W:" in build, (
            "cards that do not fit left of Replay give way to the one-line chips")
        assert "e_top_abs = DAY_BOTTOM - DAY_EXIT_FLOOR - e_h" in build, "beside the buttons, down to the tray's floor"
        assert "COLOR_CHIP_BG_GREEN" not in acts.split("# The payload's `day` block", 1)[1].split("func _the_day()", 1)[0], (
            "\"Leave it to him\" is no go-ahead: its green ground is gone")

    def test_an_exit_cards_inks_read_above_the_contrast_floor(self):
        acts = self._gd("battle_acts.gd")

        def hexed(name):
            return acts.split(f'const {name} := "', 1)[1].split('"', 1)[0]

        def lum(h):
            def lin(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
            return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

        ground = lum(hexed("DAY_EXIT_CARD_BG"))
        for ink in ("DAY_EXIT_INK", "DAY_CAPTION_INK"):
            ratio = (lum(hexed(ink)) + 0.05) / (ground + 0.05)
            assert ratio >= 4.5, (ink, round(ratio, 2))

    def test_a_group_is_labelled_for_what_it_does_and_priced_in_points(self):
        acts = self._gd("battle_acts.gd")
        label = acts.split("const DAY_GROUP_LABEL := {", 1)[1].split("}", 1)[0]
        assert '"lead": "Another leads the attack"' in label
        assert '"bring_up": "Bring up"' in label
        assert '"cannonade": "The guns, no clash"' in label
        groups = self._func(acts, "_day_groups_text")
        assert '(" · %d %s" % [price, "point" if price == 1 else "points"]) if price > 0 else ""' in groups
        assert "if idx.size() == 1:" not in groups, "a kind of one word is labelled as a kind of five is"
        assert '(label + paid).replace(" ", "\\u00A0") + ":[/color]\\u00A0"' in groups, (
            "a label never breaks inside itself, nor from its first chip (it broke mid-phrase on Ulm's table)")

    def test_the_dice_say_what_was_added_and_stand_on_a_plate(self):
        acts = self._gd("battle_acts.gd")
        tray = acts.split("class DiceTray:", 1)[1]
        assert '_sum_text = ("%+d = %d" % [modified - natural, modified]) if modified != natural' in tray, (
            "\"= 10\" stood beside dice that show eight pips")
        assert '"the blow lands at %d%% of its weight · an average throw: %d%%"' in tray
        assert "draw_rect(_plate, PLATE)" in tray and "_plate_on = false" in tray and "_plate_on = true" in tray, (
            "the plate is read with the lines: not while the dice tumble")
        luck = self._func(acts, "_luck_line")
        assert "the day's fortune in strength:" in luck, "said for what it is: not the luck of the throw"

    def test_the_counters_on_a_days_table_say_their_scope(self):
        acts = self._gd("battle_acts.gd")
        scope = self._func(acts, "_scope_the_counters")
        assert 'const DAY_CLASH_SCOPE := " LOST THIS CLASH"' in acts and 'const DAY_LOSSES := " LOSSES"' in acts
        assert "if not plain.ends_with(DAY_LOSSES):" in scope, "a fleet action's caption counts sail: it is left alone"
        assert "cap.text = plain.substr(0, plain.length() - DAY_LOSSES.length()) + DAY_CLASH_SCOPE" in scope
        assert "if need > DAY_SCOPE_ROOM:" in scope and "cap.text = plain" in scope, (
            "a caption that would near the headline keeps its own words")
        assert "elif cap == host._odo_right_cap and need > cap.size.x:" in scope \
            and "cap.position.x = right_edge - need" in scope, (
            "the right-hand caption keeps its right edge: at Text size 130 % the words outgrow its box")

    def test_the_line_under_the_headline_stands_clear_of_the_reserves_dead(self):
        """At Text size 130 % the second reading's longer lines reached the
        reserve's dead on an order of battle (the walk at that size)."""
        acts = self._gd("battle_acts.gd")
        fit = self._func(acts, "_fit_the_line_under_the_headline")
        assert "for dead in _reserve_dead:" in fit and 'sub.theme_type_variation = &"Caption"' in fit, (
            "a THEME size, never a number")
        assert "if _sub_fits(sub, half):" in fit
        assert "return sub.get_minimum_size().x / 2.0 + SUB_CLEAR <= half" in self._func(acts, "_sub_fits")
        dress = self._func(acts, "dress")
        assert dress.index("_build_the_day()") < dress.index("_fit_the_line_under_the_headline()"), (
            "after every word of the line is written: the day's own line is the last")
        assert 'host._sub_banner.theme_type_variation = &""' in self._func(acts, "_put_the_chrome_back"), (
            "the next table laid has the line's own size back")
        build = self._func(acts, "_build_the_day")
        assert "_scope_the_counters()" in build

    def test_the_panel_takes_its_lift_before_a_word_loses_what_it_does(self):
        """Ulm's table was five pixels short of its exits' cards: the panel takes
        eight of the fifteen under the bars — after its own lines have given
        way, before a word gives up what it does."""
        acts = self._gd("battle_acts.gd")
        assert "const DAY_LIFT := 8.0" in acts
        build = self._func(acts, "_build_the_day")
        assert "top = (top_free if give_shelves else top_with) - (DAY_LIFT if lifted else 0.0)" in build
        assert build.index("elif first_row:") < build.index("elif not lifted:") < build.index("elif exit_cards:")
        assert "_day_lifted = lifted" in build and "_day_exits_wide = true" in build, "the walk reads both"

    def test_the_guns_toll_is_counted_as_the_battery_fires(self):
        """"3,152 fall before the assault" stood under two counters at 0, and a
        cannonade's own table was read mid-count."""
        acts = self._gd("battle_acts.gd")
        play = self._func(acts, "play")
        assert 'if _kind() == "bombardment":' in play and "span = 1.2" in play, (
            "a cannonade's own count runs as its battery fires")
        assert play.index("host._animate_odometers(fight_from, span + 0.4)") \
            < play.index("_count_the_guns(fight_from, span + 0.4)"), (
            "the guns' writers are added AFTER the host's: each frame theirs is the last word")
        guns = self._func(acts, "_count_the_guns")
        assert 'if str(row["act"]) != "cannonade" or str(beat.get("kind", "")) != "battery":' in guns
        assert 'var target_left: bool = (str(beat.get("side", "")) == "attacker") != _attacker_left()' in guns
        assert "var to: int = mini(counted + int(item[1]), total)" in guns, "never more than the side lost in all"
        assert "_band_never_above.bind(caps)" in guns and "_band_at.bind(i," in guns, (
            "the band's two figures follow the counters")
        cap = self._func(acts, "_band_never_above")
        assert 'if cut >= 0 and fig.text.substr(cut + 3).to_int() > int(caps[i]):' in cap
        assert "odo.text = Utils.format_number(maxi(int(v), never_under))" in self._func(acts, "_odo_at")

    def test_a_corps_line_runs_on_the_bands_curve(self):
        acts = self._gd("battle_acts.gd")
        run = self._func(acts, "_run_strengths")
        assert ".set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)" in run, (
            "mid-count a corps' line and the band beside it read two figures")

    def test_the_last_hours_roll_is_said_in_plain_words(self):
        import inspect

        from backend.game_logic import battle_script
        source = inspect.getsource(battle_script)
        assert "against a bar of {b}" not in source, "no line of the script says the roll in the old words"
        assert source.count("(his march: {s}, where {b} was needed)") == 3

    def test_the_march_says_what_it_cost(self):
        acts = self._gd("battle_acts.gd")
        toll = self._func(acts, "_advance_toll_under_the_feet")
        assert 'toll += "\\n(%s lost on the march)" % Utils.format_number(kept - marched)' in toll
        assert "if kept > marched and marched > 0:" in toll

    def test_the_marchs_cost_keeps_the_baize_on_the_leads_final_station(self):
        """The walk at Text size 120 % caught it: the toll is written while the
        order of battle is laid, the wedge is taken back to the file after
        that, and the second line ran off the baize under a lead at its foot.
        The room is read again where every corps stands on its final station."""
        acts = self._gd("battle_acts.gd")
        dress = self._func(acts, "dress")
        assert dress.index("_unrelay(relaid)") < dress.index("_plan_rest()") \
            < dress.index("_the_tolls_keep_the_baize()") < dress.index("_keep_the_end()")
        keep = self._func(acts, "_the_tolls_keep_the_baize")
        assert 'var station_y: float = maxf((b["node"] as Node2D).position.y, _rest_pos(b).y)' in keep
        assert "if station_y + toll.position.y + toll.size.y <= host._stage.size.y:" in keep
        assert 'toll.text = _toll_on_one_line(b, toll.text.get_slice("\\n", 0), _rest_pos(b).x,' in keep, (
            "the first line stays, the words every surface has had — with what the march cost on it "
            "where the baize has the room (the session's review)")


# ════════════════════════════════════════════════════════
# The session's review
# ════════════════════════════════════════════════════════

class TestTheSessionsReview:
    """The session's one review: six readers on a frozen copy, every finding
    reproduced and put to skeptics before a line changed
    (`BATTLE_DIORAMA_SPEC.md` §15.24). One test or more for each fix: run on
    the frozen copy the readers read, every test of the review's fixes fails
    but one, which pins the law the fog's fix keeps (a certain word said from
    the bounds of sight is never contradicted) and held there too. The
    re-review of the fixes (five lanes, two skeptics a finding) added four
    more, each failing on the tree it was found on."""

    @staticmethod
    def _gd(name):
        import pathlib
        return (pathlib.Path(BD.__file__).resolve().parents[2] / "godot-client" / "project-sovereign"
                / "scripts" / name).read_text(encoding="utf-8").replace("\r\n", "\n")

    @staticmethod
    def _func(source, name):
        return source.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]

    # ── the telling ──

    def test_a_ruin_is_decided_for_neither(self):
        ctx = SimpleNamespace(battle_result={"outcome": "mutual_destruction",
                                             "attacker": {"forced_retreat": False},
                                             "defender": {"forced_retreat": False}},
                              enemy_destroyed=True, conquered=False)
        assert T.decided_for(ctx, True) == "" and T.decided_for(ctx, False) == "", (
            "both armies ruined: the day was told as decided for the side that attacked")

    def test_never_spent_is_said_only_of_a_reserve_never_spent(self):
        day = {"clashes": 3, "ours": 1, "ours_of": 3, "theirs": 0, "theirs_of": 3, "said": [],
               "toll": {"ours": 4000, "his": 9000}}
        assert T.shape_of(day, "night", "Mack", "Ney") == "Night fell with part of our reserve unspent."
        day.update(ours=3)
        assert T.shape_of(day, "night", "Mack", "Ney") == "Our reserve was never spent."
        day.update(toll={"ours": 9000, "his": 4000}, ours=0, theirs=2)
        assert T.shape_of(day, "night", "Mack", "Ney") == "Night fell with part of Mack's reserve unspent."
        old = {"clashes": 2, "ours": 1, "said": [], "toll": {"ours": 4000, "his": 9000}}
        assert T.shape_of(old, "night", "Mack", "Ney") == "Our reserve was never spent.", (
            "a day kept from before BA-4 has no purse of the morning: it reads as it did")

    def test_what_told_at_a_wall_reads_the_works_and_the_odds_fought_on(self):
        a = T.assault_told
        assert a(True, True, 30000, 12000, fortified=True) == "The walls told for the garrison."
        assert a(True, False, 30000, 12000, fortified=True) == "Our walls told."
        assert a(True, True, 30000, 12000) == "", "a wall that held with no works and no numbers names no cause"
        assert a(True, True, 12000, 16000) == "The garrison's weight of numbers told."
        assert a(True, False, 12000, 16000) == "Our weight of numbers told."
        assert a(False, True, 30000, 12000) == "Our weight of numbers told."
        assert a(False, False, 30000, 12000) == "His weight of numbers told."
        assert a(False, True, 30000, 12000, fortified=True) == "", "works stood: numbers were not all of it"
        assert a(False, True, 14000, 12000) == "", "under 5 to 4 a wall carried names no cause"

    def test_numbers_at_a_wall_are_men_whose_edge_the_fight_kept(self):
        """(The re-review) the fight's figures carry the ground and the
        stormers' modifiers: an edge there that the men did not have is no
        weight of numbers, nor an edge in men the ground took away."""
        a = T.assault_told
        assert a(True, True, 6000, 7500, men=(6000, 6000)) == "", (
            "equal men on a mountain: the ground's quarter is not the garrison's numbers")
        assert a(False, True, 15000, 15000, men=(15000, 12000)) == "", (
            "five men to four, and the ground evened it: the wall fell with no weight of numbers")
        assert a(True, True, 12000, 20000, men=(12000, 16000)) == "The garrison's weight of numbers told."
        assert a(False, False, 40000, 15000, men=(30000, 12000)) == "His weight of numbers told."

    def test_the_wall_is_judged_on_the_strengths_the_fight_used(self):
        import inspect

        from backend.commands import combat_executor as CE
        from backend.game_logic import siege_diorama as SD
        tableau = inspect.getsource(CE.CombatExecutor._resolve_garrison_combat).split("_tableau = dict(", 1)[1]
        tableau = tableau.split("\n\n", 1)[0]
        assert "attacker_effective=int(attacker_effective)" in tableau
        assert "garrison_effective=int(garrison_effective)" in tableau
        gate = inspect.getsource(SD.build_assault_diorama).split("if player_side is not None:", 1)[1]
        gate = gate.split("if siege is not None:", 1)[0]
        assert '_i(facts.get("attacker_effective")) or atk_before' in gate
        assert '_i(facts.get("garrison_effective")) or gar_before' in gate
        assert 'bool(facts.get("fortified")), men=(atk_before, gar_before)' in gate

    def test_a_ruin_names_no_word_that_decided_it(self):
        """(The re-review) decided for neither, the shape said the Guard was
        thrown back when the Guard was the last word."""
        for said in ([["ours", "guard"]], [["theirs", "guard"]], [["ours", "press"]], []):
            day = {"clashes": 3, "decided_for": "", "said": said}
            assert T.shape_of(day, "decided", "Mack", "Ney") == "Neither army kept the field.", said

    # ── the fog ──

    @staticmethod
    def _fit_for_it(marshal):
        marshal.retreat_recovery, marshal.wounded_until_turn = 0, 0
        marshal.fortified, marshal.drilling, marshal.drilling_locked = False, False, False

    def test_full_sight_reads_only_what_full_sight_shows(self, table):
        from backend.models.intel import FULL
        table.open_a_day(_awaits_us, his=90000)
        world = table.world
        stored = world.battle_days["days"]["Mack"]
        mack, ney = world.marshals["Mack"], world.marshals["Ney"]
        stored["theirs"] = 2
        ney.strength, mack.strength = 30000, 90000
        self._fit_for_it(mack)
        world.intel[mack.location].visibility = FULL
        assert T.reading_of(world, stored)["strike"] == "will"
        # what full sight does not show (a retreat's recovery, a wound) turns the rule: the
        # word is "may" — "will not" over a field he plainly outnumbers three to one told the
        # player what he cannot see
        mack.retreat_recovery = 3
        assert T.reading_of(world, stored)["strike"] == "may"
        mack.retreat_recovery = 0
        mack.wounded_until_turn = int(world.current_turn) + 2
        assert T.reading_of(world, stored)["strike"] == "may"
        mack.wounded_until_turn = 0
        # his works full sight DOES show: the rule and the sight agree
        mack.fortified = True
        assert T.reading_of(world, stored)["strike"] == "will_not"

    def test_left_to_it_is_read_as_far_as_the_player_sees(self, table):
        from backend.models.intel import FULL, PARTIAL, STALE
        table.open_a_day(_awaits_us)
        world = table.world
        stored = world.battle_days["days"]["Mack"]
        mack = world.marshals["Mack"]
        sight = world.intel[mack.location]

        def said_at(*strengths):
            out = set()
            for s in strengths:
                mack.strength = s
                out.add(T.would_of(world, stored))
            return out

        sight.visibility = STALE
        unseen = said_at(20000, 90000)
        assert len(unseen) == 1, ("out of sight his strength turns no word", unseen)
        world.marshals["Hohenlohe"] = _mk("Hohenlohe", mack.location, 60000, nation="Austria")
        assert said_at(90000) == unseen, "a corps out of sight beside him turns no word"
        del world.marshals["Hohenlohe"]
        sight.visibility = PARTIAL
        banded = said_at(41000, 69000)
        assert len(banded) == 1, ("inside one band the word cannot bisect him", banded)
        sight.visibility = FULL
        assert T.would_of(world, stored).startswith(("he would ", "he may ")), "in plain sight, the rule"

    def test_a_certain_word_below_full_sight_holds_for_every_roll(self, table):
        """"He would X" said from the bounds of sight is never contradicted:
        here a lead with no point left, whatever the enemy's true field."""
        from backend.models.intel import STALE
        table.open_a_day(_awaits_us)
        world = table.world
        stored = world.battle_days["days"]["Mack"]
        stored["ours"] = 0
        world.intel[world.marshals["Mack"].location].visibility = STALE
        said = T.would_of(world, stored)
        assert said.startswith("he would "), said
        word = said[len("he would "):]
        kinds = {k for k, v in T._WOULD.items() if v == word} | (
            {"strike"} if word in ("press", "strike back") else set())
        terms = T._our_terms(world, stored)
        ai = EnemyAI(CommandExecutor())
        with contextlib.redirect_stdout(io.StringIO()):
            for his in (5000, 60000, 400000):
                world.marshals["Mack"].strength = his
                for value in (0.8, 0.9, 1.0, 1.1, 1.2):
                    got = ai.the_days_word(terms["marshal"], terms["foe"], world, purse=terms["purse"],
                                           opened=terms["opened"], behind=terms["behind"],
                                           strike_price=terms["strike_price"], rng=_Fixed(value))
                    assert got["kind"] in kinds, (said, his, value, got)

    # ── to dig in ──

    def test_to_dig_in_reads_the_drill_the_order_ends(self):
        from backend.models.marshal import Stance
        world, ney, mack = _pair()
        mack.stance, mack.drilling, mack.drilling_locked = Stance.NEUTRAL, True, False
        now = mack.get_defense_modifier(consume=False)
        mack.stance, mack.drilling = Stance.DEFENSIVE, False
        after = mack.get_defense_modifier(consume=False)
        mack.stance, mack.drilling = Stance.NEUTRAL, True
        assert T.dug_in_pct(mack) == round((after / now - 1.0) * 100) > 15, (
            "the order ends a drill not yet locked: its figure reads that too")
        assert mack.drilling is True and mack.stance == Stance.NEUTRAL, "the reading puts both back"

    def test_a_dig_in_the_table_refuses_says_no_figure(self, table, monkeypatch):
        from backend.commands import state_probe
        table.open_a_day(_awaits_us)
        world = table.world
        monkeypatch.setattr(state_probe, "order_state_refusal",
                            lambda w, marshal, verb: "no actions left" if verb == "defend" else "")
        chip = _chip(BD.block(world, world.battle_days["days"]["Mack"]), kind="dig_in")
        assert not chip["ok"] and chip["does"] == T.DOES["dig_in"], chip

    # ── the day ──

    def test_an_attack_that_is_no_word_of_the_day_is_told_at_once(self, table):
        for _ in range(40):
            table.open_a_day(_awaits_us, ours=90000, his=90000)
            stored = table.world.battle_days["days"]["Mack"]
            stored["ours"] = 0                   # no point: the attack is an ordinary order
            clashes, told = int(stored.get("clashes", 0)), len(stored.get("told") or [])
            table.order("Ney, attack Mack")
            day = BD.day_against(table.world, "Mack")
            if day is None or int(day.get("clashes", 0)) == clashes:
                continue                         # decided, or no clash: another battle
            assert "clash_line" not in day, "no word would come to tell it"
            new = (day.get("told") or [])[told:]
            assert any(t.get("who") == "clash" and t.get("kind") == "clash" for t in new), new
            return
        raise AssertionError("no undecided clash of the day by an ordinary order")

    def test_a_words_battle_is_its_own_clash(self, table, monkeypatch):
        table.open_a_day(_awaits_us)
        world = table.world
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        other = _mk("Kienmayer", mack.location, 30000, nation="Austria")
        world.marshals["Kienmayer"] = other
        other.morale = mack.morale = 80
        monkeypatch.setattr(BD, "the_reserve_pursues", lambda: True)
        with _a_word(key="Mack", who="ours", price=2, kind="guard") as word:
            astray = SimpleNamespace(world=world, marshal=ney, enemy_marshal=other)
            assert BD._word_for(astray) is None
            BD.guard_shock(astray)
            BD.count_the_reserve(astray)
            assert other.morale == 80 and "reserve" not in word, "his own way fell on another corps"
            on_it = SimpleNamespace(world=world, marshal=ney, enemy_marshal=mack)
            assert BD._word_for(on_it) is word
            BD.guard_shock(on_it)
            assert mack.morale == 80 - BD.GUARD_SHOCK
        monkeypatch.setattr(BD, "a_words_battle_is_its_own_clash", lambda: False)
        with _a_word(key="Mack", who="ours", price=1, kind="press") as word:
            assert BD._word_for(SimpleNamespace(world=world, enemy_marshal=other)) is word, (
                "seam down: every battle fought while a word runs is the word's")

    def test_the_words_line_rides_only_its_own_clash(self, table, monkeypatch):
        """(The re-review) the tableau's head beat ("Ney presses the attack.")
        was told on a battle against another corps."""
        table.open_a_day(_awaits_us)
        world = table.world
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        other = _mk("Kienmayer", mack.location, 30000, nation="Austria")
        world.marshals["Kienmayer"] = other
        with _a_word(key="Mack", who="ours", price=1, kind="press"):
            assert BD.word_line(SimpleNamespace(world=world, marshal=ney, enemy_marshal=other)) is None
            line = BD.word_line(SimpleNamespace(world=world, marshal=ney, enemy_marshal=mack))
            assert line and line["who"] == "ours" and line["kind"] == "press", line
        monkeypatch.setattr(BD, "a_words_battle_is_its_own_clash", lambda: False)
        with _a_word(key="Mack", who="ours", price=1, kind="press"):
            assert BD.word_line(SimpleNamespace(world=world, marshal=ney, enemy_marshal=other)), (
                "seam down: the line as BA-3 told it")

    def test_his_word_is_his_battle_against_our_lead(self, table):
        table.open_a_day(_awaits_us)
        world = table.world
        with _a_word(key="Mack", who="theirs", price=1, kind="strike") as word:
            assert BD._word_for(SimpleNamespace(world=world, enemy_marshal=world.marshals["Ney"])) is word
            assert BD._word_for(SimpleNamespace(world=world, enemy_marshal=world.marshals["Mack"])) is None

    def test_his_days_are_newest_first_by_turn(self):
        from backend.game_logic import marshal_overview as MO
        world, ney, mack = _pair()
        # a battle of turn 7 kept at once, then the day he opened on turn 5 kept when it closed
        ney.days = [{"turn": 7, "name": "A battle at Lorraine", "verdict": "won"},
                    {"turn": 5, "name": "The day at Lorraine", "verdict": "drawn", "clashes": 3}]
        rows = MO._build_days(ney, world)["days"]
        assert [r["turn"] for r in rows] == [7, 5], "the order of keeping is not the order of the days"

    # ── the script ──

    def test_a_rout_is_one_this_battle_made(self, monkeypatch):
        from backend.game_logic import battle_script as SC
        world, ney, mack = _pair()
        ney.retreated_this_turn = True
        here = ney.location
        assert SC._fate_of(world, "Ney", False, {}, here, {"Ney"})[0] == "", (
            "thrown back earlier in the turn and holding its ground now: no line breaks here")
        assert SC._fate_of(world, "Ney", False, {}, here, set())[0] == "routed", "driven off by this battle"
        assert SC._fate_of(world, "Ney", False, {}, "Elsewhere", {"Ney"})[0] == "routed", (
            "no longer where the battle was fought: this battle moved him")
        monkeypatch.setattr(SC, "a_rout_is_one_this_battle_made", lambda: False)
        assert SC._fate_of(world, "Ney", False, {}, here, {"Ney"})[0] == "routed", "seam down: the flag alone"

    def test_the_battle_notes_who_had_retreated_at_its_muster(self):
        import inspect

        from backend.commands import combat_executor as CE
        facts = CE.battle_script_facts(SimpleNamespace(_bd_pre_retreated=["Ney"]))
        assert facts["retreated_before"] == ["Ney"]
        source = inspect.getsource(CE)
        assert "ctx._bd_pre_retreated = sorted(" in source
        assert source.index("ctx._bd_pre_strengths = snapshot_pre_battle_strengths(") \
            < source.index("ctx._bd_pre_retreated = sorted(")

    # ── the client ──

    def test_a_closing_table_keeps_how_the_day_ended(self):
        acts = self._gd("battle_acts.gd")
        kept = self._func(acts, "_day_told_kept")
        assert 'if str((lines[i] as Dictionary).get("who", "")) == "end":' in kept
        assert kept.index("for i in range(first_end, n):") < kept.index("var j := first_end - 1"), (
            "the close first, from the line that says how it ended; then the words, newest first")
        assert "for i in _day_told_kept(lines, keep):" in self._func(acts, "_day_told")
        build = self._func(acts, "_build_the_day")
        assert 'if not (i in kept_idx) and str((lines[i] as Dictionary).get("who", "")) == "end":' in build, (
            "a line of the close the table had no row for rides the head's hover")

    def test_the_walks_closing_table_check_reads_the_rows_not_the_hover(self):
        """(The re-review) the claim that the line saying how the day ended is
        ON the table read the labels' sources, where the head's hover rides:
        a line on the hover alone passed it."""
        import inspect

        from tools import ba1_acts_walk as W
        source = inspect.getsource(W)
        block = source.split("(BA5-o, the session's review)", 1)[1].split("if lines:", 1)[0]
        assert 'on_table = " ".join(ln["text"] for ln in lines)' in block
        assert "if ends[0] not in on_table:" in block and "if ends[0] not in said:" not in block

    def test_a_locked_card_keeps_what_it_would_do_in_its_hover(self):
        """...and its reason too: a dim chip carries its reason as its hover
        wherever else it stands (the walk's oldest claim on a dim chip — the
        first form of this fix left the reason off a locked card's hover, and
        the walk caught it on the staged table whose words are spent,
        `day_dim_chip`)."""
        acts = self._gd("battle_acts.gd")
        want = 'var tip := _day_chip_tip(chip, false, not lit and why != "")'
        assert want in self._func(acts, "_day_card_bb") and want in self._func(acts, "_day_exit_card_bb")
        tip = self._func(acts, "_day_chip_tip")
        assert 'if not bool(chip.get("ok", false)) and str(chip.get("why", "")) != "":' in tip
        assert "with_why" not in tip

    def test_the_line_under_the_headline_fits_the_baize(self):
        acts = self._gd("battle_acts.gd")
        fit = self._func(acts, "_fit_the_line_under_the_headline")
        assert fit.index('sub.theme_type_variation = &"Caption"') < fit.index("var short := _told_short(_sub_told)") \
            < fit.index("sub.text = _sub_host\n"), (
            "the Caption size, then what told said short, then the host's line alone")
        assert "_hint_the_line(_sub_told)" in fit, "what told is never lost: it rides the line's hover whole"
        # (the walk of record, at the shipped size) the province's own line too wide even alone, what
        # told or none: its first clause stands, the whole line and what told on the hover
        assert fit.index("sub.text = _sub_host\n") < fit.index('var dash := _sub_host.find(" — ")')
        assert 'sub.text = _sub_host.substr(0, dash) + "."' in fit
        assert '_hint_the_line((_sub_host + " " + _sub_told).strip_edges())' in fit
        assert "Control.MOUSE_FILTER_PASS" in self._func(acts, "_hint_the_line")
        back = self._func(acts, "_put_the_chrome_back")
        assert 'host._sub_banner.tooltip_text = ""' in back and "Control.MOUSE_FILTER_IGNORE" in back
        assert 'if not told.begins_with("Decided") or cut < 0:' in self._func(acts, "_told_short")

    def test_the_marchs_cost_rides_one_line_at_the_baizes_foot(self):
        acts = self._gd("battle_acts.gd")
        one = self._func(acts, "_toll_on_one_line")
        assert 'var one: String = first + " (−%s)" % Utils.format_number(cost)' in one
        assert "if x0 < host.BAIZE_PAD or x0 + w > host._stage.size.x - host.BAIZE_PAD:" in one, (
            "the toll alone only where even one line would leave the baize sideways")
        assert "_toll_on_one_line(" in self._func(acts, "_the_tolls_keep_the_baize")
        assert "_toll_on_one_line(" in self._func(acts, "_advance_toll_under_the_feet")


class TestTheLiveWalkOfRecord:
    """Five boards pressed in the REAL client against a sandboxed server
    (`tools/ba4_mode_c_walk.py --export docs/audits/ba5_mode_c_2026_11_17`;
    `BATTLE_DIORAMA_SPEC.md` §15.23): BA-4's three on the finished client, and
    the session's two — `finish` (the table that tells itself) and `oneday`
    (ruling 9's card, pressed). The record is part of the session's commit: a
    missing board is a failure, never a skip."""

    STEPS = {"day": 13, "roads": 6, "oldsave": 6, "finish": 11, "oneday": 5}

    @staticmethod
    def _run(board):
        import json
        import pathlib
        path = (pathlib.Path(BD.__file__).resolve().parents[2] / "docs" / "audits"
                / "ba5_mode_c_2026_11_17" / board / "run.json")
        assert path.is_file(), f"the live walk of the {board} board is not on record"
        return json.loads(path.read_text(encoding="utf-8"))

    def _step(self, board, step):
        found = [r for r in (self._run(board).get("walk") or {}).get("results", []) if r.get("step") == step]
        assert len(found) == 1, f"step {step} is not on the {board} board's record"
        return found[0]

    @pytest.mark.parametrize("board", sorted(STEPS))
    def test_every_step_of_the_board_held(self, board):
        run = self._run(board)
        walk = run.get("walk") or {}
        assert run.get("engine_exit") == 0 and run.get("script_errors") == []
        assert walk.get("errors") == []
        assert len(walk["results"]) == self.STEPS[board], [r["step"] for r in walk["results"]]
        assert [(r["step"], r["saw"]) for r in walk["results"] if not r.get("ok")] == []

    @pytest.mark.parametrize("board, step, said", [
        ("finish", "ba5_speed", "the engine's clock 1.0 -> 2.0 -> 1.0"),
        ("finish", "ba5_day_opens", "the clock at rest 1.0"),
        ("finish", "ba5_reading", "the server's reading: 'he "),
        ("finish", "ba5_cards", "the server's `does` for the press: 'odds:"),
        ("finish", "ba5_word_sounds", "sounding before it=false"),
        # each of these FAILED in the real client before its fix
        ("finish", "ba5_d2_view_the_field", "the client's own store of it"),
        ("finish", "ba5_d2_the_close", "heard=true"),
        ("finish", "ba5_panel_reading", "Berthier's reading on it=true"),
        ("finish", "ba5_his_days", "His days"),
        ("oneday", "one_day_card", "Should he win it and advance, that day ends where it stands."),
        ("oneday", "one_day_pressed", "this clash opens none of its own"),
        ("oneday", "one_day_pressed", "a day's block on this table=false"),
        ("oneday", "one_day_pressed", "the log says he marched from the first field=true (he advanced=true)"),
        ("oneday", "one_day_first_is_over", "a day's block on it=false"),
        ("oldsave", "old_day_closes", "tally lines told: 0"),
        # BA5-X8: the first day's line on the table that showed it, and not on the day's next
        ("day", "first_day_line", "acknowledged to the server=true"),
        ("day", "first_line_once", "the first day's line on this table=''"),
        # ...and on the table that follows a first word given from the province's panel (the
        # road that showed the rule's first form wrong)
        ("oldsave", "old_day_pressed", "the first row: 'The day hangs, Sire."),
    ])
    def test_the_steps_the_session_owes(self, board, step, said):
        row = self._step(board, step)
        assert row.get("ok") is True and said in row.get("saw", ""), row.get("saw")

    def test_the_table_after_the_first_word_says_what_its_exits_do(self):
        saw = self._step("day", "first_line_once")["saw"]
        exits = saw.split("the exits:", 1)[1]
        assert "free · he speaks next" in exits and "free · the day ends; he keeps the field" in exits, saw

    def test_the_closing_table_is_the_days_latest_clash(self):
        """BA5-D2, as the client showed it: three readings of one table agree."""
        import re
        row = self._step("finish", "ba5_d2_view_the_field")
        sigs = re.findall(r"The Great Battle of [A-Za-z ]+\|\d+\|\d+\|\d+", row["saw"])
        assert len(sigs) == 3 and len(set(sigs)) == 1, row["saw"]
        close = self._step("finish", "ba5_d2_the_close")
        assert close["saw"].count(sigs[0]) == 2, "the closing table and the day's latest clash"

    def test_ruling_nines_road_is_the_one_that_held_the_defect(self):
        saw = self._step("oneday", "one_day_pressed")["saw"]
        assert "(attacker_tactical_victory)" in saw, "he won the second clash on points — and advanced"


class TestTheMeasureOfRecord:
    """The ONE measure (`tools/_ba5_measure.py`; `BATTLE_DIORAMA_SPEC.md` §15.22
    the rule, §15.23 the readings), read off the records the chain wrote on the
    FINAL tree — the reserve parked, so the tree as shipped is arm `ALL`."""

    STAMP = "2026_11_17"
    COMMANDED = ("CMD-H", "CMD-A", "CMD-M")

    @classmethod
    def _load(cls, name):
        import json
        import pathlib
        path = pathlib.Path(BD.__file__).resolve().parents[2] / "tools" / name
        assert path.is_file(), f"{name} is not on record"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_the_ladder_is_the_hold_list(self):
        """Every seam of the session's OFF list is a seam of the measure's
        ladder, and no other; a ladder value arms the parked reserve."""
        from tests._ba5_seams import BA5_PARKED, BA5_SEAMS_DOWN
        from tools import _ba5_measure as M5
        ladder = {f"{spec}=False" for specs in M5.LADDER.values() for spec in specs}
        assert ladder == set(BA5_SEAMS_DOWN)
        assert set(M5.held("0")) == set(BA5_SEAMS_DOWN) and M5.held("ALL") == []
        assert M5.held("R2000") == [f"{BA5_PARKED[0]}=True",
                                    "backend.game_logic.battle_day:reserve_pursuit=2000"]
        assert M5.held("OWNWAY") == [f"{BA5_PARKED[0]}=False"], "the tree as shipped is this arm"
        assert M5.held("ONEDAY") == ["backend.game_logic.battle_day:a_words_battle_is_its_own_clash=False",
                                     f"{BA5_PARKED[0]}=False"], "the review's rung comes after ONEDAY"

    @pytest.mark.parametrize("arm", ["0", "TELL", "ALL"])
    def test_the_probe_is_the_commit_before_on_every_key(self, arm):
        probe = self._load(f"_ba5_probe_{self.STAMP}.json")
        for seed in ("jena", "marengo"):
            cell = probe["arms"][arm][seed]
            assert cell["vs_head"] == {"identical": True} and cell["keys"] == {}, (arm, seed)
            assert cell["keys_a_turn"] == 212 and cell["crashes"] == cell["head_crashes"]

    @pytest.mark.parametrize("arm", ["0", "TELL", "ONEDAY", "ALL", "R2000", "R3000", "R5000"])
    def test_the_band_is_unmoved_on_every_arm(self, arm):
        from tools import _ba5_measure as M5
        cells = self._load(f"_ba5_band_{self.STAMP}.json")["arms"][arm]
        assert all(cells[n]["ok"] for n in self.COMMANDED)
        assert [cells[n]["provinces"] for n in self.COMMANDED] == [28, 28, 27]
        assert cells["seams_held"] == M5.held(arm), "the record was run on the tree as it stands"

    @pytest.mark.parametrize("arm", ["0", "oneday", "all"])
    def test_the_days_sweep_is_the_commit_befores_cell_for_cell(self, arm):
        """Every seam down, the telling and BA5-X1 up, and the tree as shipped:
        BA-3's eight seeds by its nine ways of playing a day, 72 cells of 72."""
        from tools import _ba5_measure as M5
        sweep = self._load(f"_ba5_sweep_{arm}_{self.STAMP}.json")
        assert sweep["held"] == M5.held(arm.upper()), (
            "(the review) the record was run on the tree as it stands: its seams are the ladder's")
        assert sweep["cells_moved_vs_commit_before"] == []
        assert len(sweep["seeds"]) == 8 and len(sweep["arms"]) == 9
        assert all(sweep["arms"][a][n]["ok"] for a in sweep["arms"] for n in sweep["seeds"])

    @pytest.mark.parametrize("value", ["r2000", "r3000", "r5000"])
    def test_a_reserve_sweep_is_whole(self, value):
        """A stopped chain once wrote this record with every cell flagged
        failed over true data: the record of record is a clean run's."""
        from tools import _ba5_measure as M5
        sweep = self._load(f"_ba5_sweep_{value}_{self.STAMP}.json")
        assert sweep["held"] == M5.held(value.upper()), "the reserve armed at its ladder value, as run"
        assert len(sweep["seeds"]) == 8 and len(sweep["arms"]) == 7
        cells = [sweep["arms"][a][n] for a in sweep["arms"] for n in sweep["seeds"]]
        assert all(c["ok"] and c["turn"] == 40 for c in cells)

    def test_off_the_served_road_the_gate_reads_as_ba4s_final_tree(self):
        """The ambient ten seeds and the AI-France harness at `ALL`: entry for
        entry BA-4's final tree — the session moved no world-line."""
        sig5 = self._load(f"_dy_signature_ba5_all_{self.STAMP}.json")
        sig4 = self._load("_dy_signature_ba4_x14_2026_11_16.json")
        assert {k: v for k, v in sig5.items() if k != "_note"} == {k: v for k, v in sig4.items() if k != "_note"}
        assert sig5["story_class_count"] == 10
        assert self._load(f"_ba5_all_census_{self.STAMP}.json") == self._load("_ba4_x14_census_2026_11_16.json")
        assert (self._load(f"_ba5_chain_d_{self.STAMP}.json")["arms"]["ALL"]
                == self._load("_ba4_chain_d_2026_11_16.json")["arms"]["X14"])


class TestTheSecondReadingsOpenRows:
    """Three finds of the blind readings that are older than this session's
    own work — BA5-X15 and BA5-X16 of the second, BA5-X17 of the third: each
    is filed (`BUG_FIXES.md` §BA5) and heads Session H. A strict xfail — the
    day one is fixed its pin fails until it is made a plain test."""

    @staticmethod
    def _read(relative):
        import json
        import pathlib
        root = pathlib.Path(BD.__file__).resolve().parents[2]
        return json.loads((root / relative).read_text(encoding="utf-8"))

    @pytest.mark.xfail(strict=True, reason="BA5-X15: the band counts a corps still unseen — Session H's head")
    def test_the_band_does_not_count_a_corps_still_unseen(self):
        record = self._read("docs/audits/ba1_client/walk_record.json")
        payload = self._read("docs/audits/ba1_client/payloads/enemy_comes.json")
        res = next(r for r in record["results"] if r.get("id") == "enemy_comes")
        frame = next(f for f in res["frames"] if f.get("tag") == "coming_up")
        unseen = [b for act in payload["script"]["acts"] for b in act["beats"]
                  if b.get("kind") == "arrive" and b.get("concealed")]
        assert unseen, "the scene stages a corps that comes up unseen"
        side = unseen[0]["side"]
        corps = next(c for c in payload[side]["contingents"] if c["name"] == unseen[0]["actor"])
        made_out = int(payload[side]["committed_total"]) - int(corps["committed"])
        assert any(str(fig).startswith(f"{made_out:,} ") for fig in frame["band"]), (
            "while he is still unseen the band reads his whole muster", frame["band"])

    @pytest.mark.xfail(strict=True, reason="BA5-X16: a narrow defeat is said of a heavy toll — Session H's head")
    def test_a_narrow_defeat_is_not_said_of_a_heavy_toll(self):
        payload = self._read("docs/audits/ba1_client/payloads/defeat_defending.json")
        ours = next(c for side in ("attacker", "defender") for c in payload[side]["contingents"]
                    if c.get("name") == "Bernadotte")
        assert int(ours["casualties"]) * 5 >= int(ours["committed"]), "the staged defeat costs him a fifth of his corps"
        said = str(payload.get("observation") or "")
        assert not any(words in said for words in ("margin was slim", "narrow defeat", "was close")), said

    @pytest.mark.xfail(strict=True, reason="BA5-X17: a card's men of ours are the muster's weight — Session H's head")
    def test_a_cards_men_are_men_on_the_field(self):
        payload = self._read("docs/audits/ba1_client/payloads/day_ulm.json")
        ours = next(side for side in (payload["attacker"], payload["defender"]) if side.get("nation") == "France")
        on_the_field = int(ours["committed_total"]) - int(ours["casualties_total"])
        press = next(c for c in payload["day"]["chips"] if c.get("kind") == "press")
        said = _figures(press["does"])[0]
        assert said <= on_the_field, ("the card says more men are ours than stand on the field", said, on_the_field)


# ════════════════════════════════════════════════════════
# The seams
# ════════════════════════════════════════════════════════

class TestTheSeams:
    """Every switch of the session is a zero-argument function that returns
    True, registered where a recorded board's replay will find it."""

    def test_each_seam_is_a_function_that_returns_true(self):
        import importlib
        from tests._ba5_seams import BA5_PARKED, BA5_SEAMS_BY_ROW
        for row, specs in BA5_SEAMS_BY_ROW.items():
            for spec in specs:
                target, expr = spec.split("=", 1)
                module, name = target.split(":", 1)
                assert module.startswith("backend.") and expr == "False", spec
                fn = getattr(importlib.import_module(module), name)
                parked = target in BA5_PARKED
                assert callable(fn) and fn() is (not parked), (row, spec)
        assert BA5_PARKED == ["backend.game_logic.battle_day:the_reserve_pursues"]

    def test_they_are_folded_into_the_standing_list(self):
        from tests._ba5_seams import BA5_SEAMS_DOWN
        from tests._oct27_seams import OCT27_SEAMS_DOWN
        assert BA5_SEAMS_DOWN and set(BA5_SEAMS_DOWN) <= set(OCT27_SEAMS_DOWN)

    def test_every_seam_of_the_new_module_is_registered(self):
        import inspect
        from tests._ba5_seams import BA5_SEAMS_DOWN
        registered = {spec.split("=", 1)[0] for spec in BA5_SEAMS_DOWN}
        for name, fn in inspect.getmembers(T, inspect.isfunction):
            if fn.__module__ != T.__name__ or name.startswith("_"):
                continue
            params = inspect.signature(fn).parameters
            if not params and fn.__annotations__.get("return") in (bool, "bool"):
                assert f"{T.__name__}:{name}" in registered, name

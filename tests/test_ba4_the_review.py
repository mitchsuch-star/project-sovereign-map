"""Row BA, session BA-4 — the session's one review (November 16, 2026;
`docs/BATTLE_DIORAMA_SPEC.md` §15.21).

Six readers of a frozen copy rebuilt from a bundle outside the repository,
one lane each: the roads and the quotes, the combat rules and the guns, the
day of battle, the fog and the news, the client, the pins and the records.
No crash, no corruption and no save defect was found. One finding a player
meets (an ally's assault abroad was told to nobody) and a dozen lesser ones;
every one was reproduced on the live tree before a line was changed.

A class a finding. Where a fix sits behind a seam of the session, a twin
holds the seam down and shows the game before it.
"""

import random
import re
from pathlib import Path

import pytest

from backend.commands import combat_executor, order_quotes
from backend.commands import strategic as road_law
from backend.game_logic import battle_day as BD
from backend.game_logic import battle_news, intel_surfaces
from backend.models import world_state as world_state_module
from backend.models.intel import FULL, UNKNOWN
from backend.models.marshal import StrategicOrder
from tests.test_ba3_the_rounds import _awaits_us, _mk, _seat, table  # noqa: F401  (`table`: the served campaign)
from tests.test_ba4_the_roads_and_the_fog import _gd, _gd_func, _news, _support
from tools import ba1_stage_battles as STAGE

REPO = Path(__file__).resolve().parents[1]


# ════════════════════════════════════════════════════════════════════════
# Lane 4 (P2) — every road a field is lit on tells its dark side
# ════════════════════════════════════════════════════════════════════════

def _abroad(*, ally=True):
    """The 1805 board with Prussia at war with Austria — and, by default, in
    alliance with France, who is at war with Austria too."""
    world, executor = STAGE._board()
    STAGE._war(world, "Prussia", "Austria")
    if ally:
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "ALLIANCE"
    return world, executor


def _assault(*, men=30000, ally=True, garrison=None):
    """Hohenlohe, from Bohemia, storms Vienna — no French corps near."""
    world, executor = _abroad(ally=ally)
    if garrison is not None:
        STAGE._garrison(world, "Vienna", garrison)
    hohenlohe = world.marshals["Hohenlohe"]
    hohenlohe.location, hohenlohe.strength = "Bohemia", int(men)
    random.seed(1)
    with STAGE._quiet():
        reply = executor._execute_attack(hohenlohe, "Vienna", world,
                                         {"world": world, "executor": executor})
    assert reply.get("success"), reply.get("message")
    return world


def _guns(*, ally=True, by="Hohenlohe", on="ArchdukeJohn", men=(20000, 20000)):
    """A battery in Silesia opens on a corps in Lithuania — Russia's soil."""
    world, executor = _abroad(ally=ally)
    battery, target = world.marshals[by], world.marshals[on]
    battery.location, target.location = "Silesia", "Lithuania"
    battery.strength, target.strength = men
    battery.artillery = True
    random.seed(1)
    with STAGE._quiet():
        reply = executor._combat._execute_bombardment(
            battery, target, world, {"world": world, "executor": executor})
    assert reply.get("success"), reply.get("message")
    return world


def _shown(world):
    from backend.campaign_log import filter_campaign_log
    return [e.get("type") for e in filter_campaign_log(world.event_log, world)]


class TestEveryRoadTellsItsDarkSide:
    """The news of a battle abroad was written on the main attack's road
    alone. An ally's assault on a garrison in a war the player shares lit no
    field (the rule) and wrote no news — and its own row needs sight of the
    province: the player was told nothing, where before the session he saw
    every figure of it. The same for his guns, a cavalry charge, and an
    attack whose guns destroyed the defender."""

    def test_the_sentences(self):
        said = battle_news.assault_line
        assert said("Vienna", "Prussia", "Austria", False, great=False, ally="Prussia") == (
            "News from Vienna: our ally Prussia has assaulted the works of Austria — the walls held.")
        assert said("Vienna", "Prussia", "Austria", True, great=False, ally="Prussia").endswith(
            " — the place has fallen.")
        assert said("Berlin", "Austria", "Prussia", True, great=False, ally="Prussia") == (
            "News from Berlin: Austria has assaulted the works of our ally Prussia — the place has fallen.")
        assert said("Vienna", "Prussia", "Austria", False, great=True) == (
            "News from Vienna: Prussia has thrown a great assault on the works of Austria — the walls held.")
        guns = battle_news.cannonade_line
        assert guns("Lithuania", "Prussia", "Austria", ally="Prussia") == (
            "News from Lithuania: the guns of our ally Prussia have opened on Austria.")
        assert guns("Lithuania", "Austria", "Prussia", ally="Prussia") == (
            "News from Lithuania: the guns of Austria have opened on our ally Prussia.")

    def test_an_allys_assault_in_a_shared_war_is_news(self):
        world = _assault()
        assert world.get_region_intel("Vienna").visibility != FULL, "it lit no field of ours"
        [news] = _news(world)
        assert news["kind"] == "assault" and news["ally"] == "Prussia" and news["great"] is False
        assert news["line"] == ("News from Vienna: our ally Prussia has assaulted the works of "
                                "Austria — the walls held.")
        assert not any(ch.isdigit() for ch in news["line"]), "no figure"
        assert "Hohenlohe" not in news["line"], "no commander"
        shown = _shown(world)
        assert "foreign_battle" in shown and "garrison_assault" not in shown
        queued = [e for e in world.pending_dispatch_events if e.get("type") == "battle_news"]
        assert [e["template_vars"]["line"] for e in queued] == [news["line"]]

    def test_the_place_that_falls_is_told_fallen(self):
        world = _assault(garrison=6000)
        [news] = _news(world)
        assert news["verdict"] == "fell" and news["crown"] == "Prussia"
        assert news["line"].endswith(" — the place has fallen.")

    def test_a_great_assault_abroad_is_news_whoever_made_it(self):
        world = _assault(men=60000, ally=False)
        [news] = _news(world)
        assert news["great"] is True and news["ally"] == ""
        assert news["line"].startswith(
            "News from Vienna: Prussia has thrown a great assault on the works of Austria — ")
        from backend.game_logic import gazette
        assert gazette._special_reason(world, [news]) == "a great battle abroad"

    def test_a_garrison_that_yields_without_an_assault_is_no_battle(self):
        """The last few thousand of a garrison give way and the corps marches
        in unopposed: a capture, which the map shows — there was no assault
        to tell."""
        world = _assault(garrison=4000)
        assert world.get_region("Vienna").controller == "Prussia" and not _news(world)

    def test_a_small_assault_between_other_crowns_is_none(self):
        world = _assault(men=30000, ally=False)
        assert not _news(world)
        assert not [e for e in world.pending_dispatch_events if e.get("type") == "battle_news"]

    def test_our_own_assault_lights_its_field_and_writes_none(self):
        world, executor = STAGE._board()
        STAGE._place(world, Ney="Bohemia")
        random.seed(1)
        with STAGE._quiet():
            reply = executor._execute_attack(world.marshals["Ney"], "Vienna", world,
                                             {"world": world, "executor": executor})
        assert reply.get("success"), reply.get("message")
        assert world.get_region_intel("Vienna").visibility == FULL and not _news(world)
        assert "garrison_assault" in _shown(world)

    def test_the_seam_down_lights_every_wall_and_tells_no_news(self, monkeypatch):
        monkeypatch.setattr(intel_surfaces, "a_battle_lights_its_field_only_for_those_who_fought",
                            lambda: False)
        world = _assault()
        assert world.get_region_intel("Vienna").visibility == FULL and not _news(world)
        assert "garrison_assault" in _shown(world), "the game before the session"

    def test_an_allys_guns_in_a_shared_war_are_news(self):
        world = _guns()
        [news] = _news(world)
        assert news["kind"] == "cannonade" and news["great"] is False
        assert news["line"] == "News from Lithuania: the guns of our ally Prussia have opened on Austria."
        assert "bombardment" not in _shown(world) and "foreign_battle" in _shown(world)

    def test_guns_turned_on_an_ally_are_news_too(self):
        world = _guns(by="ArchdukeJohn", on="Hohenlohe")
        [news] = _news(world)
        assert news["line"] == "News from Lithuania: the guns of Austria have opened on our ally Prussia."

    def test_a_cannonade_between_other_crowns_is_none_however_many_stand_under_it(self):
        world = _guns(ally=False, men=(70000, 70000))
        assert not _news(world), "a cannonade is no battle: there is no great one"

    def test_an_allys_charge_is_a_battle_like_another(self):
        world, executor = _abroad()
        hohenlohe, john = world.marshals["Hohenlohe"], world.marshals["ArchdukeJohn"]
        hohenlohe.location, john.location = "Silesia", "Lithuania"
        hohenlohe.strength, john.strength = 20000, 20000
        hohenlohe.cavalry, hohenlohe.personality = True, "aggressive"
        hohenlohe.recklessness = 1                  # one victory behind him arms the charge
        random.seed(1)
        with STAGE._quiet():
            reply = executor.execute(
                {"command": {"action": "charge", "marshal": "Hohenlohe", "target": "ArchdukeJohn"}},
                {"world": world, "executor": executor})
        if not reply.get("success"):
            raise RuntimeError(f"the charge did not stage: {reply.get('message')}")
        [news] = _news(world)
        assert "kind" not in news and news["ally"] == "Prussia" and news["road"] == "charge"
        assert news["line"].startswith("News from Lithuania: our ally Prussia has fought Austria — ")

    def test_every_road_that_asks_before_it_lights_tells_the_rest(self):
        """The sibling sweep, pinned: five sites ask the rule; each tells its
        dark side through `battle_news`."""
        for module, sites in ((combat_executor, 4), (world_state_module, 1)):
            source = Path(module.__file__).read_text(encoding="utf-8")
            found = [m.start() for m in re.finditer(r"_surf\.battle_lights_field\(", source)]
            assert len(found) == sites, (module.__name__, len(found))
            for at in found:
                assert "_news.of_" in source[at: at + 2400], (module.__name__, source[at: at + 80])


# ════════════════════════════════════════════════════════════════════════
# Lane 2 — the muster's last hour
# ════════════════════════════════════════════════════════════════════════

class TestTheMustersLastHour:
    def test_a_corps_that_brings_nothing_is_not_said_to_come_at_the_last_hour(self):
        """Murat, nursing a grievance against Ney, brings NOTHING to Ney's
        battle (the row says so) — and the row then carried his last-hour
        odds, and the screen "a corps brings three-quarters of its weight —
        counted in the figures above". None of his weight is in them."""
        world, executor = STAGE._board()
        combat = executor._combat
        ney, mack, murat = (world.marshals[n] for n in ("Ney", "Mack", "Murat"))
        murat.jealous_of = "Ney"
        STAGE._support(world, "Murat", "Ney")           # under a written order he marches all the same
        with STAGE._quiet():
            preview = combat._build_muster_preview(ney, mack, world, {"world": world})
        row = next(r for r in preview["rows"] if r["marshal"] == "Murat")
        assert row["will_join"] and "will bring NOTHING to the fighting" in row["withholds"]
        assert combat._pair_contribution_scale(ney, murat) == 0
        if not combat._last_hour_chance(ney, murat, world, mack.location) > 0:
            raise RuntimeError("on this board Murat can no longer come up at the last hour")
        assert "last_hour_odds" not in row
        for other in preview["rows"]:
            if other is not row:
                other.pop("last_hour_odds", None)
        assert combat_executor.LAST_HOUR_MUSTER_LINE not in combat._format_muster_lines(preview)

    def test_a_muster_of_corps_all_sure_to_come_still_states_its_least(self, monkeypatch):
        """Davout alone can answer, and every roll brings him — five in
        seventeen at the last hour. Nobody's ARRIVAL is in doubt, so the
        muster stated no least: yet he may bring three quarters."""
        cls = combat_executor.CombatExecutor
        real_base, real_bar = cls._arrival_deterministic, cls._arrival_threshold
        monkeypatch.setattr(cls, "_arrival_deterministic", lambda self, m, lead, world: (
            69 if m.name == "Davout" else real_base(self, m, lead, world)))
        monkeypatch.setattr(cls, "_arrival_threshold", lambda self, m, lead, region, world, **kw: (
            60 if m.name == "Davout" else real_bar(self, m, lead, region, world, **kw)))
        world, executor = STAGE._board()
        combat = executor._combat
        for name in ("Soult", "Lannes", "Murat", "Napoleon", "Bernadotte", "Massena"):
            world.marshals[name].location = "Paris"
        ney, mack, davout = (world.marshals[n] for n in ("Ney", "Mack", "Davout"))
        with STAGE._quiet():
            preview = combat._build_muster_preview(ney, mack, world, {"world": world})
        joining = [world.marshals[r["marshal"]] for r in preview["rows"]
                   if r["will_join"] and not r.get("cannot_arrive")]
        assert joining == [davout], [m.name for m in joining]
        certain, uncertain = combat._arrival_roster(ney, joining, world, mack.location)
        assert certain == [davout] and not uncertain
        enemy_joining, _ = combat._defender_muster(mack, world, term=False)
        enemy_team = combat._reachable_joiners(mack, enemy_joining, world, mack.location, active=True)
        with combat._priced_coordination(ney, [davout], mack, enemy_team, world, mack.location):
            whole = combat._committed_reinforcement_strength(ney, [davout], world)
        lead, mine = int(ney.strength), preview["attacker"]
        assert mine["floor_strength"] == pytest.approx(lead + 0.75 * whole, abs=1)
        assert mine["floor_strength"] < mine["committed_strength"] < lead + whole + 1
        assert mine["bad_day_strength"] == mine["floor_strength"], "five rolls in seventeen: a bad day is the least"
        header = combat._format_muster_lines(preview)
        assert f"; certain {mine['floor_strength']:,}" in header
        assert ", and a bad day (1 in 10) is no better" in header

    def test_the_seam_down_states_none(self, monkeypatch):
        monkeypatch.setattr(combat_executor, "the_last_hour_brings_three_quarters", lambda: False)
        world, executor = STAGE._board()
        for name in ("Soult", "Lannes", "Murat", "Napoleon", "Bernadotte", "Massena"):
            world.marshals[name].location = "Paris"
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        assert executor._combat._spread_of_the_certain(
            ney, [world.marshals["Davout"]], mack, [], world, mack.location) is None


# ════════════════════════════════════════════════════════════════════════
# Lane 1 — the approach rule: a foe the player cannot see; a timed order
# ════════════════════════════════════════════════════════════════════════

def _a_support_order():
    return StrategicOrder(command_type="SUPPORT", target="Ney", target_type="marshal",
                          started_turn=1, original_command="Murat, support Ney")


class TestTheApproachRuleReadsTheSameFieldAsItsQuote:
    """The quote names a corps on the road only where the player SEES him
    (`visible_foe_on_road`); the order halted at the approach for any corps
    there. Where Mack stood unseen the card said nothing, the order then
    halted — and its reply named the province of a corps no surface showed.
    The approach rule is the player's reading of his friend's field: it
    applies where he sees the corps. Unseen, the march meets him as it always
    did (the question is the discovery)."""

    @staticmethod
    def _unseen():
        world, executor = STAGE._board()
        world.get_region_intel("Swabia").visibility = UNKNOWN
        assert not world.get_visible_enemies_in_region("Swabia", "France")
        return world, executor

    def test_the_predicate_asks_whether_he_is_seen(self):
        order = _a_support_order()
        world, _executor = STAGE._board()
        ney = world.marshals["Ney"]
        assert road_law.support_stands_at_approach(order, ney, "Swabia", world) is True
        world, _executor = self._unseen()
        assert road_law.support_stands_at_approach(order, world.marshals["Ney"], "Swabia", world) is False

    def test_the_quote_and_the_order_agree_where_he_is_unseen(self, monkeypatch):
        world, executor = self._unseen()
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        quote = order_quotes.support_quote(world, murat, ney)
        assert not quote.get("halts") and not quote.get("contact")
        reply = _support(world, executor, "Murat", "Ney")
        assert "at the approach" not in str(reply.get("message"))
        # ... and it is the game before the approach rule, word for word
        monkeypatch.setattr(road_law, "a_support_order_halts_before_the_friends_foe", lambda: False)
        before_world, before_executor = self._unseen()
        before = _support(before_world, before_executor, "Murat", "Ney")
        assert reply.get("message") == before.get("message")
        assert bool(reply.get("requires_input")) == bool(before.get("requires_input"))

    def test_the_friends_own_field_still_halts_him_seen_or_not(self):
        """DDB-20's arm is untouched: the step that IS the friend's own
        contested province."""
        order = _a_support_order()
        world, _executor = self._unseen()
        ney = world.marshals["Ney"]
        assert road_law.support_stands_at_approach(order, ney, ney.location, world) is True


class TestATimedSupportOrdersClockRunsFromTheApproach:
    """"Murat, support Ney for 2 turns", halted beside Mack: the clock of a
    timed support order starts when he reaches his friend — and at the
    approach he never does. The order held him for as long as Ney sat still.
    Standing at the approach is the support: the clock starts there."""

    @staticmethod
    def _timed(world, executor):
        parsed = {"command": {"raw_input": "Murat, support Ney for 2 turns", "marshal": "Murat",
                              "action": "support", "target": "Ney"},
                  "is_strategic": True, "strategic_type": "SUPPORT",
                  "strategic_condition": {"max_turns": 2}}
        random.seed(11)
        with STAGE._quiet():
            return executor.execute(parsed, {"world": world})

    def test_the_first_stand_starts_the_clock(self):
        world, executor = STAGE._board()
        reply = self._timed(world, executor)
        order = world.marshals["Murat"].strategic_order
        assert reply["success"] and "at the approach to Swabia" in reply["message"]
        assert order is not None and order.condition.max_turns == 2
        assert order.arrived_turn == world.current_turn
        turn = int(world.current_turn)
        assert road_law.count_order_turns(order, turn) == 0, "the turn he took station gave no support"
        assert road_law.count_order_turns(order, turn + 2) == 2, "two turns at the approach are the term"

    def test_the_tick_starts_it_too(self):
        """An order that was already standing when its road met the corps."""
        world, executor = STAGE._board()
        self._timed(world, executor)
        murat = world.marshals["Murat"]
        murat.strategic_order.arrived_turn = None
        from backend.commands.strategic import StrategicOrderProcessor
        with STAGE._quiet():
            report = StrategicOrderProcessor(executor)._execute_support(murat, world, {"world": world})
        assert "at the approach to Swabia" in report["message"]
        assert murat.strategic_order.arrived_turn == world.current_turn

    def test_the_seam_down_leaves_the_clock_where_it_was(self, monkeypatch):
        """DDB-20's own arm with the approach rule down: no clock is started
        at the approach (the game before the session)."""
        monkeypatch.setattr(road_law, "a_support_order_halts_before_the_friends_foe", lambda: False)
        world, executor = STAGE._board()
        field = world.marshals["Ney"].location
        world.marshals["Mack"].location = field                    # the friend's own contested field
        world.marshals["Murat"].location = "Lorraine"              # one step from it
        assert field in world.get_region("Lorraine").adjacent_regions
        world.get_region_intel(field).visibility = FULL
        reply = self._timed(world, executor)
        order = world.marshals["Murat"].strategic_order
        if order is None or "at the approach" not in str(reply.get("message")):
            raise RuntimeError(f"DDB-20's arm did not stage: {reply.get('message')}")
        assert order.arrived_turn is None


# ════════════════════════════════════════════════════════════════════════
# Lane 3 — the day's door and the card's forecast
# ════════════════════════════════════════════════════════════════════════

def _a_second_corps(world, men=30000):
    """Kienmayer beside Ney's own province, at war, in sight."""
    ney = world.marshals["Ney"]
    taken = {m.location for m in world.marshals.values()}
    ground = next(r for r in world.get_region(ney.location).adjacent_regions if r not in taken)
    world.get_region(ground).controller = ney.nation    # our own soil: a corps of ours may take the field
    kienmayer = _mk("Kienmayer", ground, men, nation="Austria", personality="literal")
    world.marshals[kienmayer.name] = kienmayer
    world.update_intel_from_battle(ground, int(world.current_turn))
    return kienmayer


class TestTheCardPromisesNoDayTheRuleWillNotOpen:
    """One day a lead (the user's ruling): while Ney's day against Mack is
    open, a second pitched battle of his opens none. The attack card on
    another corps still said "A pitched battle — Ney commands the day: 2
    points." It says what will happen instead."""

    def test_no_forecast_while_his_day_is_open(self, table):
        table.open_a_day(_awaits_us, ours=30000, his=30000)
        world = table.world
        ney, kienmayer = world.marshals["Ney"], _a_second_corps(world)
        quote = order_quotes.attack_quote(world, ney, kienmayer)
        assert quote["ok"], quote.get("refusal")
        assert "day" not in quote
        assert quote["note"] == ("Ney's day against Mack is still open — a battle here would be "
                                 "a single clash, with no day of its own.")

    def test_with_no_day_open_the_same_card_forecasts_one(self, table):
        _seat(table.world, ours=30000, his=30000)
        world = table.world
        quote = order_quotes.attack_quote(world, world.marshals["Ney"], _a_second_corps(world))
        assert quote["day"]["pitched"] is True and not quote.get("note")

    def test_the_seam_down_forecasts_a_second_day(self, table, monkeypatch):
        table.open_a_day(_awaits_us, ours=30000, his=30000)
        monkeypatch.setattr(BD, "a_lead_holds_one_day", lambda: False)
        world = table.world
        quote = order_quotes.attack_quote(world, world.marshals["Ney"], _a_second_corps(world))
        assert quote["day"]["pitched"] is True


class TestTheLeadsRetreatEndsHisDayOnEitherSide:
    """Lane 3's second finding, reproduced and NOT upheld. "Fall back" is
    offered on a day we defend; on a day we opened the table offers "Break
    off", and a typed "Ney, retreat" is taken as the day's word all the same.
    The reviewer read that as a march to the rear at no action. Played on the
    frozen copy and on the tree: a retreat costs no action anywhere in the
    game (the order's own price is nothing; its cost is the men lost on the
    road and the corps' recovery), so the door gives nothing away — and taken
    as the word it closes the day at once and says what happened. Tried the
    other way, as an ordinary order, the day stood open with its lead gone
    until night and closed as "ended where it stood". The door stays."""

    def test_a_retreat_costs_no_action_day_or_no_day(self, table):
        table.open_a_day(_awaits_us, ours=40000, his=40000)
        world = table.world
        before = int(world.actions_remaining)
        body = table.order("Ney, retreat")
        if not body.get("success"):
            raise RuntimeError(f"the retreat did not stage: {body.get('message')}")
        assert body["action_info"]["cost"] == 0 and int(world.actions_remaining) == before
        table.boot()
        _seat(table.world, ours=40000, his=40000)             # the same corps, no day open
        before = int(table.world.actions_remaining)
        body = table.order("Ney, retreat")
        if not body.get("success"):
            raise RuntimeError(f"the plain retreat did not stage: {body.get('message')}")
        assert body["action_info"]["cost"] == 0 and int(table.world.actions_remaining) == before

    def test_on_a_day_we_opened_it_closes_the_day_at_once_and_says_so(self, table):
        _body, day = table.open_a_day(_awaits_us, ours=40000, his=40000)
        assert day["side"] == "attack"
        assert not [c for c in day["chips"] if str(c.get("command", "")).endswith(", retreat")], \
            "the table of a day we opened offers Break off, not Fall back"
        world = table.world
        parsed = {"command": {"marshal": "Ney", "action": "retreat", "target": None}}
        hit = BD.classify_word(world, parsed)
        assert hit is not None and hit["kind"] == "break_off" and hit["price"] == 0
        body = table.order("Ney, retreat")
        block = body["battle_day"]
        assert block["open"] is False and block["ended"] == "fell_back"
        assert block["close"].startswith("Ney fell back from ") and " of ours for " in block["close"]
        assert not BD.open_days(world), "no day stands open with its lead gone"

    def test_on_a_day_we_defend_it_is_the_tables_own_word(self):
        world = _awaited_defence()
        parsed = {"command": {"marshal": "Ney", "action": "retreat", "target": None}}
        hit = BD.classify_word(world, parsed)
        assert hit is not None and hit["kind"] == "break_off" and hit["side"] == "defence"


def _awaited_defence():
    """A day he opened on our lead, awaiting our word — the store's own shape
    (`tests.test_ba3_the_review._a_day`), on a served board."""
    from tests.test_ba3_the_review import _a_day, _served
    world, ney, mack = _served()
    world.battle_days = {"days": {"Mack": _a_day(ney, mack, side="defence", field=ney.location)}}
    if not BD._alive(world, world.battle_days["days"]["Mack"]):
        raise RuntimeError("the defended day did not stage alive")
    return world


# ════════════════════════════════════════════════════════════════════════
# Lane 5 — the client's words
# ════════════════════════════════════════════════════════════════════════

class TestTheClientsWords:
    def test_the_help_names_the_second_battle_by_the_bar_that_opens_a_day(self):
        """The bar is 50,000 men; the help still said "a second great
        battle" (80,000) for a rule that begins at a pitched one."""
        source = _gd("codex_terms.gd")
        assert "a second great battle he fights" not in source
        assert ("A lead holds one day at a time: a second pitched battle he fights while it is open "
                "is a single clash.") in source

    def test_a_free_order_is_free_on_the_chip_as_on_the_card(self):
        """Davout's counter-punch is an attack at no action: the card and the
        badge on the map said "free", the province's chip "0 AP"."""
        tail = _gd_func(_gd("utils.gd"), "quote_price_tail")
        assert 'if ap <= 0 and bool(q.get("ok", true)):\n\t\treturn "free"' in tail
        assert 'return str(ap) + " AP"' in tail
        card = _gd("order_confirm_card.gd")
        assert 'return "free" if ap <= 0 else Utils.plural(ap, "action")' in card


# ════════════════════════════════════════════════════════════════════════
# Lane 6 — the key bar's rule is a function that can be wrong
# ════════════════════════════════════════════════════════════════════════

def _cell(days_by_run, provinces=27):
    """A bar's cell as the measure builds it: sixteen runs, each with the
    driver's `day` rows."""
    from tools import _ba4_measure as measure
    seeds = list(measure.BAND_ARMS) + ["jena", "wagram", "lodi", "eylau", "friedland"]
    cell = {"S": {}, "L": {}}
    runs = [(mode, name) for mode in ("S", "L") for name in seeds]
    for (mode, name), days in zip(runs, days_by_run):
        cell[mode][name] = {"ok": True, "provinces": provinces, "days": days}
    return cell, seeds


def _day(turn, lead="Ney", enemy="Mack", priced=4):
    return {"turn": turn, "lead": lead, "enemy": enemy, "priced": priced}


class TestTheKeyBarsRuleIsComputedAsWritten:
    """The pin on the pick read the rule's own verdicts back from the record
    — a wrong inequality in `fun_rule` would have written itself there. The
    rule, clause by clause, on days made by hand (§15.19: rich — two days in
    three offer four or more priced words; varied — at most one in five
    repeats a pairing within two turns; rested — at most eight days a
    campaign, four turns running in at most one campaign of sixteen;
    balanced — the silent band inside 23 to 28)."""

    def _rule(self, days_by_run, provinces=27):
        from tools import _ba4_measure as measure
        cell, seeds = _cell(days_by_run, provinces)
        return measure.fun_rule(cell, seeds)

    def test_rich_is_two_days_in_three(self):
        spread = lambda rich, thin: [[_day(1 + 3 * i, enemy=f"E{i}", priced=4) for i in range(rich)]  # noqa: E731
                                     + [_day(40 + 3 * i, enemy=f"T{i}", priced=3) for i in range(thin)]] + [[]] * 15
        assert self._rule(spread(2, 1))["rich"] is True
        assert self._rule(spread(3, 2))["rich"] is False, "three in five is under two in three"
        assert self._rule(spread(2, 1))["rich_share"] == pytest.approx(0.667, abs=1e-3)

    def test_varied_is_one_repeat_in_five(self):
        runs = lambda gap: [[_day(1), _day(1 + gap)] + [_day(10 + 5 * i, enemy=f"E{i}") for i in range(3)]] + [[]] * 15  # noqa: E731
        assert self._rule(runs(2))["repeat_share"] == pytest.approx(0.2) and self._rule(runs(2))["varied"] is True
        assert self._rule(runs(3))["repeat_share"] == 0.0, "three turns apart is no repeat"
        tight = [[_day(1), _day(2), _day(3)] + [_day(20, enemy="E")]] + [[]] * 15
        assert self._rule(tight)["varied"] is False, "two repeats in four"

    def test_rested_is_eight_a_campaign_and_one_run_of_four(self):
        even = [[_day(1 + 4 * i, enemy=f"E{i}") for i in range(8)] for _ in range(16)]
        assert self._rule(even)["rested"] is True and self._rule(even)["days_per_campaign"] == 8.0
        over = [list(run) for run in even]
        over[0].append(_day(39, enemy="X"))
        assert self._rule(over)["rested"] is False, "129 days in sixteen campaigns"
        running = lambda n: [[_day(t, enemy=f"E{t}") for t in (1, 2, 3, 4)] for _ in range(n)] + [[]] * (16 - n)  # noqa: E731
        assert self._rule(running(1))["rested"] is True and self._rule(running(2))["rested"] is False

    def test_the_band_is_the_silent_arms_three_seeds(self):
        one = [[_day(1)]] + [[]] * 15
        assert self._rule(one, provinces=28)["band_in"] is True
        assert self._rule(one, provinces=22)["band_in"] is False

    def test_no_day_at_all_passes_nothing(self):
        rule = self._rule([[]] * 16)
        assert rule["days"] == 0 and rule["rich"] is False and rule["varied"] is False

    def test_a_failed_run_is_not_a_quiet_campaign(self):
        from tools import _ba4_measure as measure
        cell, seeds = _cell([[_day(1)]] * 16)
        cell["L"]["jena"]["ok"] = False
        assert measure.fun_rule(cell, seeds)["runs"] == 15

    def test_the_record_is_the_rule_read_again_on_all_four_bars(self):
        import json
        from tools import _ba4_measure as measure
        record = json.loads((REPO / "tools" / "_ba4_kbar_2026_11_16.json").read_text(encoding="utf-8"))
        for bar, cell in record["bars"].items():
            assert cell["rule"]["runs"] == 16, f"{bar}: a run failed and the bar was read short"
            assert measure.fun_rule(cell, record["seeds"]) == cell["rule"], bar


# ════════════════════════════════════════════════════════════════════════
# Lane 3's note — a day that dies at dawn is told in the morning too
# ════════════════════════════════════════════════════════════════════════

class TestADayThatDiesAtDawnIsToldInTheMorning:
    """Every day's close is told: on its table, in the log, and in the
    morning for a day the night closed. A day that did not live to the dawn —
    its lead gone by morning — is closed AT dawn, after the night's lines had
    already been handed to the morning: it was logged and told nowhere."""

    @staticmethod
    def _dead_at_dawn():
        from tests.test_ba3_the_review import _a_day, _served
        world, ney, mack = _served()
        world.battle_days = {"days": {"Mack": _a_day(
            ney, mack, side="defence", field=ney.location, clashes=2,
            toll={"ours": 4100, "his": 5300}, opened_at=ney.location)}}
        away = next(n for n in world.get_region(ney.location).adjacent_regions if n != mack.location)
        ney.location = away                               # the lead has left the field
        if BD._alive(world, world.battle_days["days"]["Mack"]):
            raise RuntimeError("the board no longer kills the day")
        world._last_tactical_events = []
        return world

    def test_the_mornings_turn_events_carry_its_close(self):
        import types
        from backend.game_logic import turn_manager
        world = self._dead_at_dawn()
        turn_manager._the_days_dawn(types.SimpleNamespace(world=world, executor=None), {"world": world})
        assert not BD.open_days(world)
        logged = [e["line"] for e in world.event_log if e.get("type") == "battle_day_closed"]
        told = [e["message"] for e in world._last_tactical_events if e.get("type") == "battle_day_closed"]
        assert len(logged) == 1 and told == logged
        assert "after two clashes" in told[0] and "4,100 of ours for 5,300 of the enemy's" in told[0]

    def test_a_day_the_night_closed_is_still_told_once(self):
        import types
        from backend.game_logic import turn_manager
        world = self._dead_at_dawn()
        BD._NIGHT.setdefault(world, []).append("Night fell on the field at Elsewhere.")
        turn_manager._the_days_dawn(types.SimpleNamespace(world=world, executor=None), {"world": world})
        told = [e["message"] for e in world._last_tactical_events if e.get("type") == "battle_day_closed"]
        assert told[0] == "Night fell on the field at Elsewhere." and len(told) == 2
        assert not BD._NIGHT.get(world), "the morning took them all"

    def test_with_the_close_untold_the_morning_says_nothing(self, monkeypatch):
        import types
        from backend.game_logic import turn_manager
        monkeypatch.setattr(BD, "a_days_close_is_told", lambda: False)
        world = self._dead_at_dawn()
        turn_manager._the_days_dawn(types.SimpleNamespace(world=world, executor=None), {"world": world})
        assert not [e for e in world._last_tactical_events if e.get("type") == "battle_day_closed"]


# ════════════════════════════════════════════════════════════════════════
# The ledger
# ════════════════════════════════════════════════════════════════════════

class TestTheReviewsRowsAreOnTheLedger:
    def test_eleven_rows_of_the_session_all_fixed(self):
        from tests._ledgers import doc_text
        rows = dict(re.findall(r"^\| \*\*(BA4-X\d+)\*\* \| P\d \| (✅ FIXED|OPEN) ",
                               doc_text("BUG_FIXES.md"), flags=re.M))
        assert sorted(rows, key=lambda name: int(name.split("X")[1])) == [f"BA4-X{n}" for n in range(1, 12)]
        assert set(rows.values()) == {"✅ FIXED"}, "two found in the real client, nine by the review"

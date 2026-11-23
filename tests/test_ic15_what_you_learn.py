"""Row IC, Session 4 — IC-15, WHAT YOU LEARN: the server's store (November 22, 2026).

The design is `docs/INDEPENDENT_COMMAND_SPEC.md` §10.2 (what France can learn),
§10.3 (what the enemy learns of you); the module `backend/game_logic/learned.py`.

WHERE THIS STANDS, said plainly. Written in Session 4, when the plans shipped
OFF: this file pins the SERVER'S STORE and its three writers (the spy's
completion, a rout, a routed French man's task) with the plans' seam raised,
and the store INERT with the seam down. The rest of IC-15 (natures on every
screen, the store on the enemy's card and the war's page, the spy's wording
and price) landed in Session 4b; the plans were fixed and SWITCHED ON
November 23, 2026 at the user's word ("Switch them on" — IC4-D1 closed;
`war_plans.the_courts_follow_a_plan`).

What is pinned:

  * WITH THE PLANS DOWN — the spy learns nothing more than it did, a rout
    takes no orders, a routed French man gives nothing away, nothing is saved;
  * THE STORE (the plans raised) — the spy's report: each letter-following
    marshal's orders in plain words and the province the court's corps favour,
    with the turn it was learned; nothing is shown that was not learned; an
    ally's plan is never read;
  * CAPTURED ORDERS — the nearest letter-following marshal's orders, the court
    with no such man gives its favoured province, the court's step then ends
    within two turns;
  * §10.3 — a routed French man on his own gives his task away, for five turns;
  * AGE — "learned N turns ago", never "changed"; the save.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import learned as L
from backend.game_logic import war_plans as WP
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
_AS_SHIPPED = WP.the_courts_follow_a_plan


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _snapshot():
    with _quiet():
        return json.dumps(WorldState.from_scenario(str(SCENARIO)).to_dict(), default=str)


@pytest.fixture
def world(_snapshot):
    with _quiet():
        return WorldState.from_dict(json.loads(_snapshot))


@pytest.fixture
def plans_up(monkeypatch):
    monkeypatch.setattr(WP, "the_courts_follow_a_plan", lambda: True)


def _executor():
    from backend.commands.executor import CommandExecutor
    with _quiet():
        return CommandExecutor()


def _night(world):
    """One plans' pass: the holders drawn, the letter-following men enrolled."""
    with _quiet():
        return WP.the_pass(world, _executor(), {"world": world})


# ═══════════════════════════ as shipped ══════════════════════════════════════

class TestWithThePlansDownNothingIsLearned:

    def test_the_plans_ship_on(self):
        # November 23, 2026 — the user's "Switch them on" (IC4-D1 closed).
        assert _AS_SHIPPED() is True

    def test_the_spy_a_rout_and_a_routed_task_write_nothing(self, world, monkeypatch):
        monkeypatch.setattr(WP, "the_courts_follow_a_plan", lambda: False)
        _night(world)
        before = json.dumps(world.to_dict(), default=str, sort_keys=True)
        assert L.from_spy(world, "Austria") == {"marshals": [], "favour": None}
        mack, ney = world.marshals["Mack"], world.marshals["Ney"]
        assert L.from_rout(world, mack, ney) is None
        assert L.a_rout(world, mack, ney) is None
        assert L.a_rout(world, ney, mack) is None
        assert L.payload(world) == {}
        assert json.dumps(world.to_dict(), default=str, sort_keys=True) == before
        assert "learned" not in world.to_dict() and "war_plans" not in world.to_dict() \
            or not (world.to_dict().get("war_plans") or {}).get("holders")

    def test_the_spys_words_add_nothing_when_nothing_was_learned(self, world, monkeypatch):
        monkeypatch.setattr(WP, "the_courts_follow_a_plan", lambda: False)
        assert L.spy_words(world, "Austria", L.from_spy(world, "Austria")) == ""


# ═══════════════════════════ the spy ═════════════════════════════════════════

class TestTheSpysReport:

    def test_it_learns_each_letter_following_mans_orders_and_the_favour(self, world, plans_up):
        _night(world)
        report = L.from_spy(world, "Austria")
        assert report["marshals"] == ["Mack"]
        row = L.of_marshal(world, "Mack")
        assert row["how"] == L.SPY and row["court"] == "Austria"
        assert row["turn"] == int(world.current_turn)
        assert row["orders"] and "Swabia" in " ".join(row["orders"])
        assert L.of_court(world, "Austria")["how"] == L.SPY
        words = L.spy_words(world, "Austria", report)
        assert "Mack" in words

    def test_nothing_is_shown_that_was_not_learned(self, world, plans_up):
        _night(world)
        assert L.payload(world) == {}
        L.from_spy(world, "Austria")
        shown = L.payload(world)
        assert set(shown.get("marshals") or {}) == {"Mack"}
        assert "Buxhowden" not in json.dumps(shown), "Russia was not spied on"
        assert set(shown.get("courts") or {}) <= {"Austria"}

    def test_a_court_at_peace_and_an_ally_give_nothing(self, world, plans_up):
        _night(world)
        assert L.from_spy(world, "Prussia") == {"marshals": [], "favour": None}
        report = L.from_spy(world, "Bavaria")
        # Bavaria is France's ally: since November 23, 2026 she draws no plan at
        # all (a plan is drawn only against France, `war_plans._muster`); the
        # store is for courts France fights — `tidy` puts away what is not of
        # an enemy court
        assert WP.holder_of(world, "Bavaria") == ""
        L.tidy(world)
        assert not (L.payload(world).get("marshals") or {}).get("Deroy"), report

    def test_what_is_known_carries_its_age_and_never_says_changed(self, world, plans_up):
        _night(world)
        L.from_spy(world, "Austria")
        row = L.of_marshal(world, "Mack")
        assert "this turn" in L.age_words(world, row) or "now" in L.age_words(world, row)
        world.current_turn += 2
        aged = L.age_words(world, row)
        assert "2 turns ago" in aged and "changed" not in aged.lower()
        shown = L.payload(world)["marshals"]["Mack"]
        assert shown["learned"] == aged and shown["how"] == L.how_words(row)

    def test_the_store_is_saved_only_when_it_holds_something(self, world, plans_up):
        assert "learned" not in world.to_dict()
        _night(world)
        L.from_spy(world, "Austria")
        data = json.loads(json.dumps(world.to_dict(), default=str))
        assert data["learned"]["marshals"]["Mack"]["how"] == L.SPY
        with _quiet():
            back = WorldState.from_dict(data)
        assert L.of_marshal(back, "Mack") == L.of_marshal(world, "Mack")


# ═══════════════════════════ captured orders ═════════════════════════════════

class TestCapturedOrders:

    def test_a_rout_takes_the_nearest_letter_following_mans_orders(self, world, plans_up):
        _night(world)
        mack, ney = world.marshals["Mack"], world.marshals["Ney"]
        taken = L.a_rout(world, mack, ney)
        assert taken and taken["court"] == "Austria" and taken["marshal"] == "Mack"
        assert taken["orders"] and L.of_marshal(world, "Mack")["how"] == L.CAPTURED
        told = L.taken_words(world, taken)
        assert "Mack" in told and taken["orders"][0] in told

    def test_routing_another_corps_of_the_court_takes_his_orders_too(self, world, plans_up):
        _night(world)
        charles, ney = world.marshals["ArchdukeCharles"], world.marshals["Ney"]
        taken = L.a_rout(world, charles, ney)
        assert taken and taken["marshal"] == "Mack", "the court's nearest such man"

    def test_a_court_with_no_such_man_gives_its_favoured_province(self, world, plans_up):
        _night(world)
        moore, ney = world.marshals["Moore"], world.marshals["Ney"]
        taken = L.a_rout(world, moore, ney)
        assert taken is not None and taken["marshal"] is None
        assert taken["favour"] is not None      # "" is knowledge too: no province favoured
        assert L.of_court(world, "Britain")["how"] == L.CAPTURED
        assert "Among the baggage" in L.taken_words(world, taken)

    def test_orders_once_taken_end_the_courts_step_within_two_turns(self, world, plans_up):
        _night(world)
        state = WP.state_of(world, "Austria")
        step = int(state["step"])
        L.a_rout(world, world.marshals["Mack"], world.marshals["Ney"])
        assert state["compromised"] == int(world.current_turn)
        world.current_turn += WP.COMPROMISED_TURNS
        WP._settle_the_holders(world)
        assert int(WP.state_of(world, "Austria")["step"]) > step or WP.state_of(world, "Austria")["done"]

    def test_a_french_corps_routed_by_a_court_at_peace_or_an_ally_takes_nothing(self, world, plans_up):
        _night(world)
        deroy, ney = world.marshals["Deroy"], world.marshals["Ney"]
        assert L.a_rout(world, deroy, ney) is None      # Bavaria is not at war with France


# ═══════════════════════════ what the enemy learns of you ════════════════════

class TestTheCourtLearnsARoutedMansTask:

    def test_a_routed_man_on_his_own_gives_his_task_away_for_five_turns(self, world, plans_up):
        _night(world)
        state = WP.state_of(world, "Austria")
        assert WP.learns_of(world, "Austria", {"task": "take", "target": "Swabia"})
        assert state["learnt"]["place"] == "Swabia"
        assert int(state["learnt"]["until"]) == int(world.current_turn) + WP.LEARNT_TURNS
        world.current_turn += WP.LEARNT_TURNS + 1
        WP._settle_the_holders(world)
        assert "learnt" not in WP.state_of(world, "Austria")

    def test_its_own_seam_takes_it_down(self, world, plans_up, monkeypatch):
        _night(world)
        monkeypatch.setattr(WP, "a_court_learns_a_routed_mans_task", lambda: False)
        assert not WP.learns_of(world, "Austria", {"task": "take", "target": "Swabia"})
        assert "learnt" not in WP.state_of(world, "Austria")

    def test_a_task_that_names_no_place_to_take_gives_nothing(self, world, plans_up):
        _night(world)
        assert not WP.learns_of(world, "Austria", {"task": "hold", "target": "Rhineland"})


# ═══════════════════════════ what Session 4b owed, built ═════════════════════
# Golden rule 9: these were Session 4's strict pins for row IC4-D2
# (`docs/BUG_FIXES.md` §"Row IC, Session 4"); Session 4b built them, so they
# are plain tests now.

class TestWhatSession4bOwed:

    def test_every_marshal_in_the_summary_carries_his_nature(self, world):
        summary = world.get_filtered_game_state_summary() if hasattr(
            world, "get_filtered_game_state_summary") else {}
        rows = list((summary.get("marshals") or {}).values()) if isinstance(
            summary.get("marshals"), dict) else list(summary.get("marshals") or [])
        assert rows and all(row.get("nature") in ("Bold", "Careful", "To the letter")
                            for row in rows if row.get("name") != "Napoleon")

    def test_captured_orders_reach_the_battles_telling(self):
        source = (REPO / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert "taken_words(" in source

    def test_what_was_learned_reaches_a_screen(self):
        main = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert "learned.payload(" in main or "_learned.payload(" in main


# ═══════════════════════════ Session 4b: told, shown ═════════════════════════

class TestTheBattleNamesNoEnemyOrder:
    """IC4b-33 (the second review, after the plans were switched on): the
    battle's own sentences named an enemy's standing order — "Mack's HOLD order
    at Swabia is broken!", "His HOLD order is cancelled." — and an enemy's
    letter-following man carries his court's written plan, which France knows
    only by the spy. The order is still broken or cancelled; the sentence is
    the player's own man's."""

    def test_a_planned_enemy_beaten_back_is_not_told_by_his_order(self, world, plans_up):
        from backend.commands.combat_executor import CombatExecutor
        _night(world)
        mack, ney = world.marshals["Mack"], world.marshals["Ney"]
        assert WP.planned(world, mack)
        ex = CombatExecutor(_executor())
        with _quiet():
            said = ex._apply_forced_retreat_or_break(mack, ney, world, skip_fate=True)
        assert "order" not in said.lower(), said
        assert mack.strategic_order is None, "the order is still broken"

    def test_the_players_man_beaten_back_is_still_told_his_order_is_lost(self, world):
        from backend.commands.combat_executor import CombatExecutor
        from backend.models.marshal import StrategicOrder
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        ney.strategic_order = StrategicOrder(command_type="MOVE_TO", target="Swabia", target_type="region",
                                             started_turn=1, original_command="Ney, march to Swabia")
        ex = CombatExecutor(_executor())
        with _quiet():
            said = ex._apply_forced_retreat_or_break(ney, mack, world, skip_fate=True)
        assert "order is cancelled" in said or "order is void" in said, said

    def test_an_enemy_square_names_no_order_of_his(self):
        source = (REPO / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        body = source[source.index('strategic_cancel_msg = ""'):source.index("square_discipline_note = (")]
        assert 'if marshal.nation == getattr(world, "player_nation", "France"):' in body


class TestTheBaggageIsToldOnce:

    def test_a_rout_tells_the_baggage_once_and_clears_it(self, world, plans_up):
        from backend.commands.combat_executor import CombatExecutor
        _night(world)
        mack, ney = world.marshals["Mack"], world.marshals["Ney"]
        ex = CombatExecutor(_executor())
        with _quiet():
            ex._apply_forced_retreat_or_break(mack, ney, world)
        told = ex._tell_orders_taken(world)
        assert told.startswith("Among the baggage") and "Mack" in told
        assert world._orders_taken is None
        assert ex._tell_orders_taken(world) == "", "read, used, then cleared (golden rule 4)"

    def test_a_re_entry_tells_nothing(self, world, plans_up):
        from backend.commands.combat_executor import CombatExecutor
        _night(world)
        mack, ney = world.marshals["Mack"], world.marshals["Ney"]
        ex = CombatExecutor(_executor())
        world._orders_taken = None
        with _quiet():
            ex._apply_forced_retreat_or_break(mack, ney, world, skip_fate=True)
        assert ex._tell_orders_taken(world) == ""


class TestWhatWasLearnedRidesTheReply:

    def test_the_envelope_carries_it_only_once_something_was_learned(self, world, plans_up):
        from backend import main as M
        _night(world)
        assert M._learned_for_wire(world) == {}
        L.from_spy(world, "Austria")
        shown = M._learned_for_wire(world)
        assert shown["marshals"]["Mack"]["learned"] == "learned this turn"
        assert isinstance(shown["marshals"]["Mack"]["turn"], int)

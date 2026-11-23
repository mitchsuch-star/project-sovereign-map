"""Row IC, Session 4 — IC-15, WHAT YOU LEARN: the server's store (November 22, 2026).

The design is `docs/INDEPENDENT_COMMAND_SPEC.md` §10.2 (what France can learn),
§10.3 (what the enemy learns of you); the module `backend/game_logic/learned.py`.

WHERE THIS STANDS, said plainly. IC-15 is NOT finished in this session: it
reads the enemy's war plans, and the plans ship OFF (built, not adopted — the
measure's rule written before the data was missed; `war_plans.the_courts_follow_a_plan`).
What is in the tree is the SERVER'S STORE and its three writers (the spy's
completion, a rout, a routed French man's task), pinned here with the plans'
seam raised — and pinned INERT as shipped. The rest of IC-15 (every marshal's
nature shown on every screen, the store on the enemy's card and the war's
page, the spy's wording and price) is Session 4b's, with the decision on the
plans.

What is pinned:

  * AS SHIPPED — the plans off: the spy learns nothing more than it did, a rout
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

class TestAsShippedNothingIsLearned:

    def test_the_plans_ship_off(self):
        assert _AS_SHIPPED() is False

    def test_the_spy_a_rout_and_a_routed_task_write_nothing(self, world):
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

    def test_the_spys_words_add_nothing_when_nothing_was_learned(self, world):
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
        # Bavaria is France's ally: her plan is hers; the store is for courts
        # France fights — `tidy` puts away what is not of an enemy court
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


# ═══════════════════════════ what is NOT built yet (Session 4b) ══════════════
# Golden rule 9: an owed piece carries its pin. Each test below is STRICT — the
# day Session 4b builds it the xfail turns red and is taken off
# (`docs/BUG_FIXES.md` §"Row IC, Session 4", row IC4-D2).

class TestWhatSession4bOwes:

    @pytest.mark.xfail(strict=True, reason="IC4-D2 (Session 4b): every row that names a marshal "
                                           "carries his nature — Bold · Careful · To the letter")
    def test_every_marshal_in_the_summary_carries_his_nature(self, world):
        summary = world.get_filtered_game_state_summary() if hasattr(
            world, "get_filtered_game_state_summary") else {}
        rows = list((summary.get("marshals") or {}).values()) if isinstance(
            summary.get("marshals"), dict) else list(summary.get("marshals") or [])
        assert rows and all(row.get("nature") in ("Bold", "Careful", "To the letter")
                            for row in rows if row.get("name") != "Napoleon")

    @pytest.mark.xfail(strict=True, reason="IC4-D2 (Session 4b): captured orders are told in the "
                                           "battle's result (`world._orders_taken` is written by "
                                           "the rout and read by nobody yet)")
    def test_captured_orders_reach_the_battles_telling(self):
        source = (REPO / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert "taken_words(" in source

    @pytest.mark.xfail(strict=True, reason="IC4-D2 (Session 4b): what France has learned is shown "
                                           "with its age on the enemy marshal's card and the war's page")
    def test_what_was_learned_reaches_a_screen(self):
        main = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert "learned.payload(" in main or "_learned.payload(" in main

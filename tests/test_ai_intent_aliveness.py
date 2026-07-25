"""AI-2c — great-power statecraft (Stage C).

docs/AI_INTENT_SPEC.md §3.4 — the aliveness contract: the majors must be
recognisable political actors, not nineteen postures aimed at France.
This file is the contract's tracking test: the in-character pins and the
homogeneity guard (§5 pin 10's peacetime half — the wartime half rides
AI-V in Stage G).

Boot-neutrality (§3.4 "must not perturb the 1805 boot"): statecraft
biases ask ORDER, coercion ANSWERS and the AI-AI counter arm; its
weight_mod is authored 0 for every 1805 court, asserted here beside the
untouched boot intents.
"""

from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy
from backend.game_logic.ai_diplomacy import _hegemony_ask_candidates
from backend.game_logic.intent import get_nation_intent
from backend.game_logic.statecraft import (
    COERCION_FOLDS_DELTA,
    COERCION_HARDENS_DELTA,
    COERCION_HONOUR_DELTA,
    COERCION_SUBSIDY_WALL,
    coercion_acceptance_delta,
    haggles,
    hostile_army_on_home_soil,
    order_asks_by_statecraft,
    statecraft_weight_mod,
)
from backend.models.world_state import WorldState
from backend.nation_config import NATION_STATECRAFT

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


class TestHomogeneityGuard:
    """§3.4: 'Europe could still feel like a spreadsheet because every
    power plays identically. This contract exists to make that outcome
    a FAILING test.'"""

    def test_the_four_majors_are_pairwise_distinct(self, world):
        majors = ("Austria", "Prussia", "Russia", "Britain")
        signatures = {
            nation: (tuple(world.get_statecraft(nation)["reaches_first"]),
                     world.get_statecraft(nation)["coercion"])
            for nation in majors
        }
        # No two majors share BOTH the instrument preference and the
        # coercion answer — the facade §3.4 forbids.
        seen = set()
        for nation, signature in signatures.items():
            assert signature not in seen, (
                f"{nation} duplicates another major's statecraft: "
                f"{signature}")
            seen.add(signature)

    def test_default_profile_is_neutral(self, world):
        profile = world.get_statecraft("Hesse")
        assert profile["reaches_first"] == ()
        assert profile["coercion"] == "neutral"
        assert profile["weight_mod"] == 0
        assert profile["haggles"] is False

    def test_secondaries_are_light_profiles(self):
        """§3.4: texture, not protagonists — a preferred rung and a
        coercion reaction, no more."""
        for nation in ("Sweden", "Ottoman", "Denmark", "Sardinia",
                       "Naples", "Spain"):
            authored = NATION_STATECRAFT[nation]
            assert set(authored.keys()) <= {"reaches_first", "coercion"}, (
                f"{nation}'s profile is over-characterised: "
                f"{sorted(authored.keys())}")


class TestBootNeutrality:
    """§3.4 'It must not perturb the 1805 boot (§5 pin 1).'"""

    def test_every_authored_weight_mod_is_zero(self, world):
        for nation in NATION_STATECRAFT:
            assert statecraft_weight_mod(world, nation) == 0

    def test_boot_intents_unmoved_by_statecraft(self, world):
        # The Stage B measured pins hold with the statecraft wire live.
        view = get_nation_intent("Prussia", world)
        assert (view.weight, view.price) == (59, "align")
        assert get_nation_intent("Austria", world).price == "fight"


class TestCoercionAnswers:
    def test_austria_hardens(self, world):
        assert (coercion_acceptance_delta(world, "Austria")
                == COERCION_HARDENS_DELTA)

    def test_prussia_folds(self, world):
        assert (coercion_acceptance_delta(world, "Prussia")
                == COERCION_FOLDS_DELTA)

    def test_russia_escalates_on_honour(self, world):
        assert (coercion_acceptance_delta(world, "Russia")
                == COERCION_HONOUR_DELTA)

    def test_neutral_court_reads_zero(self, world):
        assert coercion_acceptance_delta(world, "Hesse") == 0

    def test_britain_subsidy_wall_is_derived_not_hardcoded(self, world):
        """Pin 10 (narrowed): the wall stands while no hostile army is
        on British home soil — and DROPS when one is. London is
        land-reachable; a never-folds Britain is forbidden."""
        assert not hostile_army_on_home_soil(world, "Britain")
        assert (coercion_acceptance_delta(world, "Britain")
                == COERCION_SUBSIDY_WALL)
        home = list(world.nation_starting_regions["Britain"])
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France")
        marshal.location = home[0]
        assert world.is_at_war("Britain", "France")
        assert hostile_army_on_home_soil(world, "Britain")
        assert coercion_acceptance_delta(world, "Britain") == 0

    def test_captured_marshal_does_not_hold_the_wall_down(self, world):
        """A PRISONER paraded at the captor's capital is not a hostile
        army (review fix: the guard read a nonexistent `captured` attr —
        the Marshal field is `captured_by`)."""
        home = list(world.nation_starting_regions["Britain"])
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France")
        marshal.location = home[0]
        marshal.captured_by = "Britain"
        assert not hostile_army_on_home_soil(world, "Britain")

    def test_peacetime_army_is_not_hostile(self, world):
        # Prussia is at peace with Britain — a Prussian corps on British
        # soil is a curiosity, not coercion leverage.
        home = list(world.nation_starting_regions["Britain"])
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "Prussia")
        marshal.location = home[0]
        assert not hostile_army_on_home_soil(world, "Britain")


class TestAskOrdering:
    def test_prussia_reaches_for_gold_first(self, world):
        """The hesitant opportunist leads with the gift, not the pact."""
        candidates = _hegemony_ask_candidates("Prussia", "PEACE", 10, world)
        assert candidates, "P3 candidate list unexpectedly empty"
        gold_family = ("friendly_gift", "open_borders")
        pact_family = ("non_aggression", "defensive_alliance", "alliance")
        first_gold = min((candidates.index(c) for c in candidates
                          if c in gold_family), default=99)
        first_pact = min((candidates.index(c) for c in candidates
                          if c in pact_family), default=99)
        assert first_gold < first_pact

    def test_austria_reaches_for_the_bloc_first(self, world):
        candidates = order_asks_by_statecraft(
            "Austria", ["friendly_gift", "open_borders", "non_aggression"],
            world)
        assert candidates[0] == "non_aggression"

    def test_reorder_is_a_partition_never_a_mutation(self, world):
        original = ["non_aggression", "friendly_gift", "open_borders"]
        reordered = order_asks_by_statecraft("Prussia", list(original),
                                             world)
        assert sorted(reordered) == sorted(original)

    def test_design_advancing_ask_outranks_style(self, world):
        """The NA-2 front-move runs AFTER the statecraft reorder — the
        design outranks the style. Denmark's guard_neutrality design IS
        the non-aggression pact, and it leads despite Denmark's
        ask-first (open_borders) statecraft."""
        candidates = _hegemony_ask_candidates("Denmark", "PEACE", 10, world)
        assert candidates and candidates[0] == "non_aggression"

    def test_neutral_court_order_unchanged(self, world):
        original = ["non_aggression", "friendly_gift", "open_borders"]
        assert order_asks_by_statecraft("Hesse", list(original),
                                        world) == original


class TestHaggleArm:
    """The AI-2c court-to-court counter — who haggles is character."""

    def _resolve(self, world, target, monkeypatch, *, asked, band_score):
        scores = {asked: band_score}

        def fake_acceptance(proposal, evaluator, other, w):
            # The recipient balks in the band on the asked type; every
            # other (incl. the downgraded type, both sides) signs.
            if (proposal["type"] == asked and evaluator == target):
                return band_score
            return 60

        monkeypatch.setattr(ai_diplomacy, "_ai_ai_acceptance",
                            fake_acceptance)
        return ai_diplomacy._resolve_ai_ai_proposal(
            {"type": asked, "proposer": "Prussia", "target": target},
            world)

    def test_haggler_counters_one_rung_down(self, world, monkeypatch):
        event = self._resolve(world, "Austria", monkeypatch,
                              asked="defensive_alliance", band_score=40)
        assert event is not None
        assert event.get("countered") is True
        assert event.get("asked_type") == "defensive_alliance"

    def test_non_haggler_walks_away(self, world, monkeypatch):
        event = self._resolve(world, "Russia", monkeypatch,
                              asked="defensive_alliance", band_score=40)
        # Russia does not bargain — the near-miss is a refusal, recorded.
        assert event is not None
        assert event.get("type") == "ai_ai_proposal_refused"

    def test_below_the_band_no_haggle(self, world, monkeypatch):
        event = self._resolve(world, "Austria", monkeypatch,
                              asked="defensive_alliance", band_score=20)
        assert event is not None
        assert event.get("type") == "ai_ai_proposal_refused"

    def test_never_counters_below_open_borders(self, world, monkeypatch):
        event = self._resolve(world, "Austria", monkeypatch,
                              asked="open_borders", band_score=40)
        assert event is not None
        assert event.get("type") == "ai_ai_proposal_refused"

    def test_haggles_gate_reads_the_table(self, world):
        assert haggles(world, "Austria")
        assert haggles(world, "Prussia")
        assert haggles(world, "Britain")
        assert not haggles(world, "Russia")
        assert not haggles(world, "Hesse")

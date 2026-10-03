"""SF-LB-1 "Europe's own quarrels" (Score Finish Step 3, October 2, 2026).

Measured at the boot before a line was written: Prussia's `hanoverian_prize`
stood at `align` (59) over Hanover and the design ask fired only at ask/buy,
so an acquire design NEVER asked, never collected the two refusals AI-3's
ladder wants, and never opened a war — AI-3r's "0 council wars on every
seed with the predicate written". Four levers, each byte-identical down:

- `ai_diplomacy.A_DESIGN_IS_ASKED_BEFORE_IT_IS_FOUGHT`: the design ask at
  every rung below coerce;
- `intent.A_REFUSAL_HARDENS_THE_ASKER`: each refused ask on the record adds
  +6 to the asker's weight, capped at +12 (both boards);
- `agendas.AN_ALLY_IS_NOT_COVETED`: an acquire design against an ally's
  bloc sleeps while the alliance stands (IQ6-D1: Austria's deck advances
  to the authored follow-on, The Eastern Question);
- `agendas.A_CONTAIN_DESIGN_SLEEPS_IN_THE_ARMED_PEACE`: a contain design
  sleeps while the Armed Peace holds and its court is at peace with the
  hegemon (`gulf_and_straits` wakes without a volte-face).
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import agendas as AG
from backend.game_logic import ai_diplomacy as AD
from backend.game_logic import coalition as CO
from backend.game_logic import emergent_designs as ED
from backend.game_logic import intent as IN
from backend.game_logic.agendas import get_active_agenda
from backend.game_logic.intent import get_nation_intent
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


def _boot():
    return WorldState.from_scenario(str(SCENARIO))


def _fresh(world):
    world.invalidate_active_nations_cache()
    world._intent_cache = None
    world._agenda_cache = None


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


class TestTheAskAtEveryRungBelowCoerce:
    def test_prussia_at_align_asks_hanover(self):
        world = _boot()
        view = get_nation_intent("Prussia", world)
        # SF-LB-2 "The Defenceless Prize" (October 3, 2026): an armyless Hanover reads as a prize the moment the campaign boots, so Prussia's boot weight carries intent.WEIGHT_HOLDER_OUTMATCHED (59 -> 69, align -> bandwagon) — re-seated consciously, SCORE_FINISH_SPEC.md §6.4. The ask fires
        # at every rung in DESIGN_ASK_RUNGS — bandwagon included.
        assert view.against == "Hanover" and view.price == "bandwagon"
        assert view.price in AD.DESIGN_ASK_RUNGS
        proposal = _quiet(AD._evaluate_ai_ai_proposal, "Prussia", "Hanover", world)
        assert proposal == {"type": "design_ask", "proposer": "Prussia", "target": "Hanover"}

    def test_lever_down_align_never_asks(self, monkeypatch):
        monkeypatch.setattr(AD, "A_DESIGN_IS_ASKED_BEFORE_IT_IS_FOUGHT", False)
        world = _boot()
        proposal = _quiet(AD._evaluate_ai_ai_proposal, "Prussia", "Hanover", world)
        assert not proposal or proposal.get("type") != "design_ask"

    def test_a_court_at_coerce_does_not_ask(self, monkeypatch):
        world = _boot()
        monkeypatch.setattr(IN, "WEIGHT_BASE_BY_TYPE", dict(IN.WEIGHT_BASE_BY_TYPE, acquire_regions=75))
        _fresh(world)
        view = get_nation_intent("Prussia", world)
        assert view.price in ("coerce", "fight")
        proposal = _quiet(AD._evaluate_ai_ai_proposal, "Prussia", "Hanover", world)
        assert not proposal or proposal.get("type") != "design_ask"


class TestARefusalHardensTheAsker:
    def _refuse_twice(self, world):
        from backend.game_logic.ai_diplomacy import record_diplomatic_refusal
        world.current_turn = 10
        assert record_diplomatic_refusal(world, "Prussia", "Hanover", "design_ask")
        world.current_turn = 17        # past the 6-turn dedupe window
        assert record_diplomatic_refusal(world, "Prussia", "Hanover", "design_ask")
        _fresh(world)

    def test_two_refusals_add_twelve(self):
        world = _boot()
        before = get_nation_intent("Prussia", world).weight
        self._refuse_twice(world)
        after = get_nation_intent("Prussia", world).weight
        assert after - before == 12, (before, after)

    def test_the_cap_holds_at_three(self):
        from backend.game_logic.ai_diplomacy import record_diplomatic_refusal
        world = _boot()
        before = get_nation_intent("Prussia", world).weight
        for turn in (5, 12, 19):
            world.current_turn = turn
            record_diplomatic_refusal(world, "Prussia", "Hanover", "design_ask")
        world.current_turn = 20
        _fresh(world)
        assert get_nation_intent("Prussia", world).weight - before == IN.WEIGHT_REFUSED_ASK_CAP

    def test_the_memory_window_forgets(self):
        world = _boot()
        before = get_nation_intent("Prussia", world).weight
        self._refuse_twice(world)
        world.current_turn = 40          # both refusals older than 12 turns
        _fresh(world)
        assert get_nation_intent("Prussia", world).weight == before

    def test_lever_down_the_record_feeds_the_ladder_alone(self, monkeypatch):
        monkeypatch.setattr(IN, "A_REFUSAL_HARDENS_THE_ASKER", False)
        world = _boot()
        before = get_nation_intent("Prussia", world).weight
        self._refuse_twice(world)
        assert get_nation_intent("Prussia", world).weight == before

    def test_gr5_a_refused_ask_of_france_hardens_its_asker_too(self):
        from backend.game_logic.ai_diplomacy import record_diplomatic_refusal
        world = _boot()
        # Sardinia covets Piedmont (France's); at war with France? at the boot
        # it is at coerce — the term still reads
        before = get_nation_intent("Sardinia", world).weight
        world.current_turn = 10
        record_diplomatic_refusal(world, "Sardinia", "France", "design_purchase")
        _fresh(world)
        assert get_nation_intent("Sardinia", world).weight == min(100, before + IN.WEIGHT_REFUSED_ASK)


def _ally(world, a, b):
    world.diplomatic_states[world._make_diplo_key(a, b)] = "ALLIANCE"
    _fresh(world)


class TestAnAllyIsNotCoveted:
    def test_a_reversed_austria_turns_to_the_eastern_question(self):
        world = _boot()
        assert get_active_agenda("Austria", world).id == "redeem_italy"
        _ally(world, "Austria", "France")
        assert get_active_agenda("Austria", world).id == "the_eastern_question"
        view = get_nation_intent("Austria", world)
        assert view.against == "Ottoman"

    def test_the_design_wakes_when_the_alliance_ends(self):
        world = _boot()
        _ally(world, "Austria", "France")
        assert get_active_agenda("Austria", world).id == "the_eastern_question"
        world.diplomatic_states[world._make_diplo_key("Austria", "France")] = "PEACE"
        _fresh(world)
        assert get_active_agenda("Austria", world).id == "redeem_italy"

    def test_lever_down_the_ally_is_coveted(self, monkeypatch):
        monkeypatch.setattr(AG, "AN_ALLY_IS_NOT_COVETED", False)
        world = _boot()
        _ally(world, "Austria", "France")
        assert get_active_agenda("Austria", world).id == "redeem_italy"

    def test_the_boot_is_unchanged(self):
        world = _boot()
        assert get_active_agenda("Austria", world).id == "redeem_italy"
        assert [e["id"] for e in world.agendas["Austria"]] == \
            ["redeem_italy", "primacy_germany", "the_eastern_question"]

    def test_the_volte_face_beat_names_the_live_design(self):
        world = _boot()
        # a beaten, courted Austria: the predicate's clauses staged by hand
        world.current_turn = 20
        _ally(world, "Austria", "France")
        world.nation_relations[world._make_diplo_key("Austria", "France")] = 60
        import backend.game_logic.emergent_designs as _ed
        for name in ("_war_with_ended_recently", "_latest_war_end_turn"):
            pass
        orig_clauses = _ed.volte_face_failing_clauses
        _ed.volte_face_failing_clauses = lambda w, p, h, exhaustive=False: []
        try:
            event = _quiet(ED.maybe_fire_volte_face, world, "Austria", "France")
        finally:
            _ed.volte_face_failing_clauses = orig_clauses
        assert event and event["next_design"] == "the_eastern_question"
        assert "The Eastern Question" in event["message"]


class TestAContainDesignSleepsInTheArmedPeace:
    def _armed_peace_world(self):
        world = _boot()
        france = world.player_nation
        world.current_turn = 20
        world.active_coalition = None
        world.coalition_brewing = None
        world.coalition_cooldown = 0
        for nation in world.get_active_nations():
            if nation == france:
                continue
            key = world._make_diplo_key(france, nation)
            if world.diplomatic_states.get(key) == "WAR":
                world.diplomatic_states[key] = "PEACE"
        _fresh(world)
        return world

    def test_russia_turns_to_the_gulf_and_the_straits(self):
        world = self._armed_peace_world()
        assert CO.armed_peace_reading(world)["holds"]
        assert get_active_agenda("Russia", world).id == "gulf_and_straits"
        assert get_active_agenda("Sweden", world) is None   # Sweden's deck is the one contain design: it sleeps
        view = get_nation_intent("Russia", world)
        assert view.against in ("Sweden", "Ottoman")

    def test_a_league_wakes_the_contain_design(self):
        world = self._armed_peace_world()
        world.coalition_brewing = {"target_nation": "France", "turns_remaining": 2,
                                   "qualifying_nations": ["Russia"]}
        _fresh(world)
        assert not CO.armed_peace_reading(world)["holds"]
        assert get_active_agenda("Russia", world).id == "arbiter_of_europe"

    def test_a_court_at_war_with_the_hegemon_keeps_it(self):
        world = self._armed_peace_world()
        world.diplomatic_states[world._make_diplo_key("Russia", "France")] = "WAR"
        _fresh(world)
        assert get_active_agenda("Russia", world).id == "arbiter_of_europe"

    def test_the_boot_is_unchanged(self):
        world = _boot()
        assert world.active_coalition is not None
        assert get_active_agenda("Russia", world).id == "arbiter_of_europe"

    def test_lever_down_the_contain_design_holds_the_deck(self, monkeypatch):
        monkeypatch.setattr(AG, "A_CONTAIN_DESIGN_SLEEPS_IN_THE_ARMED_PEACE", False)
        world = self._armed_peace_world()
        assert get_active_agenda("Russia", world).id == "arbiter_of_europe"


class TestTheScenario:
    def test_the_eastern_question_validates_and_names_ottoman_soil(self):
        import json
        from backend.modding.validator import validate_scenario
        result = _quiet(validate_scenario, json.load(open(SCENARIO, encoding="utf-8")))
        assert result.is_valid, result.errors
        world = _boot()
        for r in ("Albania", "Rumelia"):
            assert world.get_region(r).controller == "Ottoman"

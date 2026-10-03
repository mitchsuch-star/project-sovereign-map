"""SF-LB-2 "The Defenceless Prize" — SCORE_FINISH_SPEC.md §6.4 (RULED
October 3, 2026), the head of Step 4.

The ruling: an AI-vs-AI acquire design whose holder cannot defend the prize
opens its crisis at `coerce`, and the asker's weight reads the holder's
weakness; the `fight` bar (85) stays where AI-3r put it for everything else.

Pins carried here:
- ONE outmatched predicate (`war_council.holder_outmatched`) read by the
  weight term AND the opening — never two copies (an AST census over the
  backend).
- The predicate on an armyless holder (yes), a 2:1 holder (yes), a 1.5:1
  holder (no), a guaranteed holder (lifted out), an asker with no free
  strength (no).
- Lever-down byte-identity for every lever: the weight without the term,
  the opening without the coerce road, the ask arm stopping at bandwagon,
  the fight road ignoring the restraints.
- The crisis opens at coerce ONLY under the test and ONLY with the
  restraints clear; a crisis opened at coerce survives the next poll; the
  player's guarantee of the holder passes it `deterred`.
- The addendum (AI_WAR_DECISION_SPEC.md §8): a court the restraints forbid
  never fore-warns on the fight road either.
- The ask at coerce while the ladder is unclimbed — a court asks before it
  demands.
- The surfaces: the Intent row names the clause; Talleyrand's war room
  names it with the guarantee as the counter, DP-gated honestly; the
  wizard's guarantee chip names whose reach the pledge lifts the court
  out of.
- The driven 40-turn board on three seeds (the probe runner IS the
  harness): the war is produced on every seed, at coerce, by Prussia on
  Hanover; the variance clause is recorded as MEASURED NOT MET (an xfail
  that must flip the day it is).
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy as AD
from backend.game_logic import diplomacy as DP
from backend.game_logic import diplomatic_advisory as ADV
from backend.game_logic import intent as IN
from backend.game_logic import war_council as WC
from backend.game_logic.ai_diplomacy import record_diplomatic_refusal
from backend.game_logic.diplomacy import declare_war
from backend.game_logic.instruments import pledge_guarantee
from backend.game_logic.intent import (
    WEIGHT_HOLDER_OUTMATCHED,
    build_intent_payload,
    get_nation_intent,
    rung_index,
)
from backend.game_logic.war_council import (
    HOLDER_OUTMATCHED_FRACTION,
    coveters_of_prize,
    crisis_rung_holds,
    defenceless_prize,
    defenceless_prize_line,
    holder_outmatched,
    process_war_council,
)
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")
PROBE = REPO_ROOT / "tools" / "_sf_lb1_fight_bar_probe.py"
BACKEND = REPO_ROOT / "backend"


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _fresh(world):
    world.invalidate_bloc_members_cache()
    world._intent_cache = None
    world._exposure_cache = None


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def _climb_ladder(world, coveter="Prussia", holder="Hanover"):
    """Two refused design asks on the serialized record (pin 8). The
    recorder dedupes a repeated TYPE inside REFUSAL_DEDUPE_TURNS, so the
    second refusal is the purchase variant (both count for the ladder and
    for the weight's +6 each)."""
    assert record_diplomatic_refusal(world, coveter, holder, "design_ask")
    world.current_turn = int(world.current_turn) + 1
    assert record_diplomatic_refusal(world, coveter, holder, "design_purchase")
    world.nation_gold[coveter] = max(int(world.nation_gold.get(coveter, 0)), 2000)
    _fresh(world)


def _poll_next_turn(world):
    world.current_turn = int(world.current_turn) + 1
    _fresh(world)
    return _quiet(process_war_council, world)


# ════════════════════════════════════════════════════════════════════════
# ONE predicate
# ════════════════════════════════════════════════════════════════════════

class TestOnePredicate:
    def test_the_fraction_is_read_in_one_place(self):
        hits = []
        for path in BACKEND.rglob("*.py"):
            src = path.read_text(encoding="utf-8")
            if "HOLDER_OUTMATCHED_FRACTION" in src:
                tree = ast.parse(src)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name) and node.id == "HOLDER_OUTMATCHED_FRACTION":
                        hits.append(path.name)
        # one definition + one read, both in war_council.py
        assert sorted(hits) == ["war_council.py", "war_council.py"], hits

    def test_both_readers_call_the_predicate(self):
        intent_src = (BACKEND / "game_logic" / "intent.py").read_text(encoding="utf-8")
        council_src = (BACKEND / "game_logic" / "war_council.py").read_text(encoding="utf-8")
        assert "holder_outmatched(world, nation, against)" in intent_src
        assert "holder_outmatched(world, coveter, view.against)" in council_src
        # the weight term never re-derives the ratio
        assert "get_free_strength" not in intent_src.split("A_HOLDER_WITHOUT_AN_ARMY_IS_A_PRIZE:")[-1].split("seeded_jitter")[0]

    def test_armyless_holder_counts(self, world1805):
        assert WC._standing_strength(world1805, "Hanover") == 0
        assert holder_outmatched(world1805, "Prussia", "Hanover")

    def test_half_is_the_edge(self, world, monkeypatch):
        """The blessed number is HALF (§6.4-1), pinned as a literal — a pin
        that read the constant back would pass at any fraction (the sweep
        found that form inert at 0.34)."""
        assert HOLDER_OUTMATCHED_FRACTION == 0.5
        free = 40000
        monkeypatch.setattr(WC, "get_free_strength", lambda w, n: free)
        strengths = {"Hanover": 20000}
        monkeypatch.setattr(WC, "_standing_strength",
                            lambda w, n: strengths.get(n, 0))
        assert holder_outmatched(world, "Prussia", "Hanover")        # exactly half
        strengths["Hanover"] = 13600                                    # a third: still a prize
        assert holder_outmatched(world, "Prussia", "Hanover")
        strengths["Hanover"] = int(free / 1.5)                          # 1.5 : 1
        assert not holder_outmatched(world, "Prussia", "Hanover")
        strengths["Hanover"] = 20001
        assert not holder_outmatched(world, "Prussia", "Hanover")     # one man over

    def test_a_guarantor_lifts_the_holder_out(self, world):
        assert holder_outmatched(world, "Prussia", "Hanover")
        pledge_guarantee(world, guarantor="France", protected="Hanover")
        _fresh(world)
        assert not holder_outmatched(world, "Prussia", "Hanover")

    def test_the_coveters_own_pledge_lifts_nothing(self, world):
        pledge_guarantee(world, guarantor="Prussia", protected="Hanover")
        _fresh(world)
        assert holder_outmatched(world, "Prussia", "Hanover")

    def test_an_asker_with_no_free_strength_threatens_nobody(self, world, monkeypatch):
        monkeypatch.setattr(WC, "get_free_strength", lambda w, n: 0)
        assert not holder_outmatched(world, "Prussia", "Hanover")

    def test_self_and_empty(self, world1805):
        assert not holder_outmatched(world1805, "Prussia", "Prussia")
        assert not holder_outmatched(world1805, "", "Hanover")


# ════════════════════════════════════════════════════════════════════════
# Clause 1 — the weight term
# ════════════════════════════════════════════════════════════════════════

class TestTheWeightTerm:
    def test_boot_prussia_carries_the_term(self, world1805):
        view = get_nation_intent("Prussia", world1805)
        assert (view.weight, view.price) == (59 + WEIGHT_HOLDER_OUTMATCHED, "bandwagon")

    def test_lever_down_the_boot_weight_returns(self, world, monkeypatch):
        monkeypatch.setattr(IN, "A_HOLDER_WITHOUT_AN_ARMY_IS_A_PRIZE", False)
        _fresh(world)
        view = get_nation_intent("Prussia", world)
        assert (view.weight, view.price) == (59, "align")

    def test_no_other_boot_court_moves(self, world1805):
        for nation, weight, price in (("Austria", 85, "fight"), ("Britain", 84, "fight"),
                                      ("Russia", 89, "fight"), ("Sardinia", 79, "coerce"),
                                      ("Sweden", 89, "fight")):
            view = get_nation_intent(nation, world1805)
            assert (view.weight, view.price) == (weight, price), nation

    def test_gr5_a_defenceless_player_hardens_its_coveter_too(self, world):
        """The player-targeted case keeps NA-5's road: the TERM reads on
        both boards (a France of 1,000 men holding Hanover is a prize),
        the OPENING stays AI-vs-AI."""
        world.regions["Hanover"].controller = "France"
        for m in world.marshals.values():
            if m.nation == "France":
                m.strength = 125
        world.invalidate_active_nations_cache()
        _fresh(world)
        view = get_nation_intent("Prussia", world)
        assert view.against == "France"
        assert holder_outmatched(world, "Prussia", "France")
        assert defenceless_prize(world, "Prussia", view) is None   # the opening never
        assert not crisis_rung_holds(world, "Prussia", view) or view.price == "fight"


# ════════════════════════════════════════════════════════════════════════
# Clause 2 — the opening at coerce
# ════════════════════════════════════════════════════════════════════════

class TestTheOpeningAtCoerce:
    def test_the_rung_holds_at_coerce_only_for_a_prize(self, world):
        _climb_ladder(world)
        view = get_nation_intent("Prussia", world)
        assert view.price == "coerce"
        assert crisis_rung_holds(world, "Prussia", view)
        pledge_guarantee(world, guarantor="France", protected="Hanover")
        _fresh(world)
        view = get_nation_intent("Prussia", world)
        assert rung_index(view.price) < rung_index("fight")
        assert not crisis_rung_holds(world, "Prussia", view)

    def test_the_crisis_opens_at_coerce(self, world):
        _climb_ladder(world)
        events = _poll_next_turn(world)
        record = world.war_intents.get("Prussia")
        assert record and record["target"] == "Hanover"
        assert record["opened_at_price"] == "coerce"
        assert any(e["type"] == "crisis_brewing" for e in events)

    def test_lever_down_no_crisis_opens_at_coerce(self, world, monkeypatch):
        monkeypatch.setattr(WC, "THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE", False)
        _climb_ladder(world)
        assert get_nation_intent("Prussia", world).price == "coerce"
        _poll_next_turn(world)
        assert "Prussia" not in world.war_intents

    def test_the_coerce_road_needs_the_restraints_clear(self, world):
        _climb_ladder(world)
        world.nation_gold["Prussia"] = WC.AI_WAR_TREASURY_FLOOR - 1
        _fresh(world)
        assert WC._restraint_block_reason(world, "Prussia", "Hanover") == "penniless"
        _poll_next_turn(world)
        assert "Prussia" not in world.war_intents
        world.nation_gold["Prussia"] = 2000
        _poll_next_turn(world)
        assert world.war_intents["Prussia"]["opened_at_price"] == "coerce"

    def test_a_climbed_ladder_at_bandwagon_opens_nothing(self, world):
        """The rung is coerce, not bandwagon: two refusals of OTHER asks
        climb the ladder without the +6 design hardening, so Prussia stands
        at bandwagon (69) with the ladder climbed, the restraints clear and
        the chest full — and no crisis opens."""
        assert record_diplomatic_refusal(world, "Prussia", "Hanover", "defensive_alliance")
        world.current_turn = int(world.current_turn) + 1
        assert record_diplomatic_refusal(world, "Prussia", "Hanover", "non_aggression")
        world.nation_gold["Prussia"] = 2000
        _fresh(world)
        view = get_nation_intent("Prussia", world)
        assert view.price == "bandwagon", view
        assert WC._ladder_climbed(world, "Prussia", "Hanover")
        assert WC._restraint_block_reason(world, "Prussia", "Hanover") is None
        assert not crisis_rung_holds(world, "Prussia", view)
        _poll_next_turn(world)
        assert "Prussia" not in world.war_intents

    def test_the_coerce_road_needs_the_ladder(self, world):
        record_diplomatic_refusal(world, "Prussia", "Hanover", "design_ask")
        world.nation_gold["Prussia"] = 2000
        _fresh(world)
        assert get_nation_intent("Prussia", world).price == "coerce"
        assert not WC._ladder_climbed(world, "Prussia", "Hanover")
        _poll_next_turn(world)
        assert "Prussia" not in world.war_intents

    def test_a_coerce_crisis_survives_the_next_poll(self, world):
        _climb_ladder(world)
        _poll_next_turn(world)
        assert "Prussia" in world.war_intents
        events = _poll_next_turn(world)
        assert "Prussia" in world.war_intents
        assert not any(e["type"] == "crisis_passed" for e in events)
        assert any(e["type"] == "coercive_demand" for e in events)

    def test_the_players_guarantee_passes_it_deterred(self, world):
        _climb_ladder(world)
        _poll_next_turn(world)
        assert "Prussia" in world.war_intents
        pledge_guarantee(world, guarantor="France", protected="Hanover")
        events = _poll_next_turn(world)
        passed = [e for e in events if e["type"] == "crisis_passed"]
        assert passed and passed[0]["cause"] == "deterred"
        assert "Prussia" not in world.war_intents

    def test_the_whole_road_declares(self, world):
        """coerce opening -> fore-warning -> the coercive demand -> the
        declaration, by AI-3's own clock; Hanover a minor (D2)."""
        _climb_ladder(world)
        _poll_next_turn(world)
        _poll_next_turn(world)   # the coercive demand
        events = _poll_next_turn(world)
        assert world.is_at_war("Prussia", "Hanover")
        assert any(e.get("type") == "war_declaration" for e in events) or \
            any("declar" in str(e.get("type")) for e in events)
        war = next(w for w in world.war_instances.values()
                   if w.get("ai_initiated") and "Prussia" in (w.get("attackers") or []))
        assert war["design_id"] == "hanoverian_prize"


# ════════════════════════════════════════════════════════════════════════
# The addendum — the fight road reads the restraints at the opening
# ════════════════════════════════════════════════════════════════════════

class TestTheFightRoadReadsTheRestraints:
    def _at_fight_and_busy(self, world):
        _climb_ladder(world)
        world.nation_relations[world._make_diplo_key("Prussia", "Hanover")] = -45
        declare_war(world, "Prussia", "Denmark")   # busy
        _fresh(world)
        view = get_nation_intent("Prussia", world)
        assert view.price == "fight", view
        assert WC._restraint_block_reason(world, "Prussia", "Hanover") == "busy"

    def test_a_busy_court_never_fore_warns(self, world):
        self._at_fight_and_busy(world)
        _poll_next_turn(world)
        assert "Prussia" not in world.war_intents

    def test_lever_down_ai3s_fight_road_opens_regardless(self, world, monkeypatch):
        monkeypatch.setattr(WC, "A_CRISIS_OPENS_ONLY_WHERE_IT_CAN_DECLARE", False)
        self._at_fight_and_busy(world)
        _poll_next_turn(world)
        assert world.war_intents["Prussia"]["opened_at_price"] == "fight"

    def test_a_restraint_that_appears_later_still_cools_on_screen(self, world):
        _climb_ladder(world)
        _poll_next_turn(world)
        assert "Prussia" in world.war_intents
        declare_war(world, "Prussia", "Denmark")
        _fresh(world)
        for _ in range(WC.CRISIS_SOFT_STALL_TURNS + 3):
            events = _poll_next_turn(world)
            passed = [e for e in events if e["type"] == "crisis_passed"]
            if passed:
                assert passed[0]["cause"] == "starved"   # busy -> the moment passed
                break
        else:
            pytest.fail("a crisis blocked after its opening must cool on screen")


# ════════════════════════════════════════════════════════════════════════
# A court asks before it demands
# ════════════════════════════════════════════════════════════════════════

class TestTheAskAtCoerce:
    def _prussia_at_coerce_unclimbed(self, world):
        record_diplomatic_refusal(world, "Prussia", "Hanover", "design_ask")
        world.current_turn = int(world.current_turn) + AD.REFUSAL_DEDUPE_TURNS + 1
        _fresh(world)
        view = get_nation_intent("Prussia", world)
        assert view.price == "coerce"
        assert not WC._ladder_climbed(world, "Prussia", "Hanover")

    def test_the_ask_fires_at_coerce_while_the_ladder_is_unclimbed(self, world):
        self._prussia_at_coerce_unclimbed(world)
        proposal = _quiet(AD._evaluate_ai_ai_proposal, "Prussia", "Hanover", world)
        assert proposal == {"type": "design_ask", "proposer": "Prussia", "target": "Hanover"}

    def test_once_climbed_the_court_demands_instead(self, world):
        """Staged OUTSIDE the refusal-dedupe window, so the ladder clause
        is the only thing stopping the ask (inside the window the dedupe
        would stop it anyway — the sweep found that form inert)."""
        self._prussia_at_coerce_unclimbed(world)   # the ask sits 7 turns back
        assert record_diplomatic_refusal(world, "Prussia", "Hanover", "design_purchase")
        _fresh(world)
        assert WC._ladder_climbed(world, "Prussia", "Hanover")
        assert get_nation_intent("Prussia", world).price == "coerce"
        recent = [e for e in AD.get_refused_asks(world, "Prussia", "Hanover")
                  if e.get("type") == "design_ask"
                  and int(world.current_turn) - int(e.get("turn", 0)) < AD.REFUSAL_DEDUPE_TURNS]
        assert not recent, "the fixture must sit outside the dedupe window"
        proposal = _quiet(AD._evaluate_ai_ai_proposal, "Prussia", "Hanover", world)
        assert not (proposal and proposal.get("type") == "design_ask"), proposal

    def test_lever_down_the_ask_stops_at_bandwagon(self, world, monkeypatch):
        monkeypatch.setattr(AD, "A_COURT_ASKS_BEFORE_IT_DEMANDS", False)
        self._prussia_at_coerce_unclimbed(world)
        proposal = _quiet(AD._evaluate_ai_ai_proposal, "Prussia", "Hanover", world)
        assert not (proposal and proposal.get("type") == "design_ask")


# ════════════════════════════════════════════════════════════════════════
# The surfaces
# ════════════════════════════════════════════════════════════════════════

class TestTheSurfaces:
    def test_the_intent_row_names_the_clause(self, world1805):
        payload = build_intent_payload("Prussia", world1805)
        assert payload["defenceless_prize"] == "Hanover"
        line = defenceless_prize_line(world1805, "Prussia", "Hanover")
        assert line == ("Hanover cannot defend itself — Prussia's design opens "
                        "at an ultimatum, not at war")
        assert payload["summary"].endswith(line)
        assert payload["defenceless_prize_line"] == line

    def test_the_row_is_silent_where_no_prize_stands(self, world1805):
        payload = build_intent_payload("Austria", world1805)
        assert payload["defenceless_prize"] is None
        assert "cannot defend itself" not in payload["summary"]

    def test_only_an_acquire_design_is_a_prize(self, world1805):
        """A deny or contain design on an outmatched holder opens nothing
        at coerce — staged on the view itself, since no 1805 deny/contain
        design aims at a court the player guard does not already exclude."""
        from backend.game_logic.intent import IntentView
        assert holder_outmatched(world1805, "Prussia", "Hanover")
        for want_type in ("deny_regions", "contain_hegemon", "paymaster"):
            view = IntentView(nation="Prussia", want_id="x", want_title="x",
                              want_type=want_type, against="Hanover",
                              weight=80, price="coerce")
            assert defenceless_prize(world1805, "Prussia", view) is None, want_type
            assert not crisis_rung_holds(world1805, "Prussia", view), want_type
        acquire = IntentView(nation="Prussia", want_id="x", want_title="x",
                             want_type="acquire_regions", against="Hanover",
                             weight=80, price="coerce")
        assert defenceless_prize(world1805, "Prussia", acquire) == "Hanover"
        assert crisis_rung_holds(world1805, "Prussia", acquire)

    def test_lever_down_the_row_is_silent(self, world, monkeypatch):
        monkeypatch.setattr(WC, "THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE", False)
        _fresh(world)
        payload = build_intent_payload("Prussia", world)
        assert payload["defenceless_prize"] is None
        assert "cannot defend itself" not in payload["summary"]

    def test_the_war_room_names_the_counter(self, world):
        _climb_ladder(world)
        world.diplomatic_points = 3
        assessment = _quiet(ADV._assess_situation, world)
        rows = assessment["context"]["defenceless_prizes"]
        assert rows and rows[0]["nation"] == "Prussia" and rows[0]["holder"] == "Hanover"
        text = assessment["talleyrand_text"]
        assert "Hanover cannot defend itself" in text
        assert "A guarantee of Hanover (1 DP — 3 in hand) puts our army in their scale." in text

    def test_the_war_room_is_honest_about_the_dp(self, world):
        _climb_ladder(world)
        world.diplomatic_points = 0
        text = _quiet(ADV._assess_situation, world)["talleyrand_text"]
        assert "needs 1 DP, none in hand" in text

    def test_the_war_room_knows_a_standing_pledge(self, world):
        _climb_ladder(world)
        _poll_next_turn(world)
        pledge_guarantee(world, guarantor="France", protected="Hanover")
        _fresh(world)
        text = _quiet(ADV._assess_situation, world)["talleyrand_text"]
        # the pledge lifts Hanover out of the reading — the clause is gone
        assert "Hanover cannot defend itself" not in text

    def test_the_war_room_waits_for_the_climb(self, world1805):
        """At bandwagon the clause is read but the counsel waits: the
        design has not reached the rung that opens."""
        assert get_nation_intent("Prussia", world1805).price == "bandwagon"
        rows = _quiet(ADV._assess_situation, world1805)["context"]["defenceless_prizes"]
        assert rows == []

    def test_the_guarantee_chip_names_the_reach(self, world1805):
        chips = DP._instrument_actions(world1805, "France", "Hanover")
        chip = next(c for c in chips if c["action"] == "guarantee_nation")
        assert chip["prize_coveters"] == ["Prussia"]
        assert chip["effect_text"].startswith(
            "Hanover cannot defend itself — our army in their scale lifts them "
            "out of Prussia's reach.")
        other = next(c for c in DP._instrument_actions(world1805, "France", "Austria")
                     if c["action"] == "guarantee_nation")
        assert other["prize_coveters"] == []
        assert "cannot defend itself" not in other["effect_text"]

    def test_coveters_of_prize_is_lever_gated(self, world, monkeypatch):
        assert coveters_of_prize(world, "Hanover") == ["Prussia"]
        monkeypatch.setattr(WC, "THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE", False)
        assert coveters_of_prize(world, "Hanover") == []


# ════════════════════════════════════════════════════════════════════════
# A province outranks a friendly namesake (found driving the war)
# ════════════════════════════════════════════════════════════════════════

class TestAProvinceOutranksAFriendlyNamesake:
    """Prussia's marshal Brunswick and Hanover's province Brunswick share a
    name; the undefended-capture rung's `attack Brunswick` was refused as
    an attack on a friend, so the council's war was declared and never
    fought (twelve turns of "No valid actions remaining"). Both boards."""

    def _at_war_at_berlin(self, world):
        from backend.commands.executor import CommandExecutor
        declare_war(world, "Prussia", "Hanover")
        hohenlohe = world.marshals["Hohenlohe"]
        hohenlohe.location = "Berlin"
        world.invalidate_active_nations_cache()
        assert world.regions["Brunswick"].controller == "Hanover"
        assert world.marshals["Brunswick"].nation == "Prussia"
        assert "Brunswick" in world.regions["Berlin"].adjacent_regions
        return CommandExecutor()

    def _attack(self, executor, world, target):
        cmd = {"command": {"type": "specific", "marshal": "Hohenlohe",
                           "action": "attack", "target": target,
                           "_autonomous_execution": True}}
        return _quiet(executor.execute, cmd, {"world": world, "executor": executor})

    def test_the_province_is_taken(self, world):
        from backend.commands import combat_executor as CE
        assert CE.A_PROVINCE_OUTRANKS_A_FRIENDLY_NAMESAKE
        executor = self._at_war_at_berlin(world)
        result = self._attack(executor, world, "Brunswick")
        assert result.get("success"), result.get("message")
        assert world.regions["Brunswick"].controller == "Prussia"

    def test_lever_down_the_friend_is_refused(self, world, monkeypatch):
        from backend.commands import combat_executor as CE
        monkeypatch.setattr(CE, "A_PROVINCE_OUTRANKS_A_FRIENDLY_NAMESAKE", False)
        executor = self._at_war_at_berlin(world)
        result = self._attack(executor, world, "Brunswick")
        assert result.get("success") is False
        assert "Cannot attack friendly marshal Brunswick" in result.get("message", "")
        assert world.regions["Brunswick"].controller == "Hanover"

    def test_a_friend_who_is_no_province_is_still_refused(self, world):
        executor = self._at_war_at_berlin(world)
        assert "Hohenlohe" not in world.regions
        world.marshals["Brunswick"].location = "Berlin"
        cmd = {"command": {"type": "specific", "marshal": "Brunswick",
                           "action": "attack", "target": "Hohenlohe",
                           "_autonomous_execution": True}}
        result = _quiet(executor.execute, cmd, {"world": world, "executor": executor})
        assert result.get("success") is False
        assert "Cannot attack friendly marshal Hohenlohe" in result.get("message", "")

    def test_the_enemy_marshal_still_comes_first(self, world):
        """WO-13's order stands: an ENEMY marshal named like a province is
        the target; the namesake arm runs only after no enemy answered."""
        src = (BACKEND / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        enemy_first = src.index("enemy_by_name, enemy_error = self._executor._fuzzy_match_enemy(target, world, marshal.nation)")
        namesake = src.index("A_PROVINCE_OUTRANKS_A_FRIENDLY_NAMESAKE and friendly_match")
        assert enemy_first < namesake


# ════════════════════════════════════════════════════════════════════════
# The exit's own fix — a full label keeps its last sighting (narration C4)
# ════════════════════════════════════════════════════════════════════════

class TestAFullLabelKeepsItsLastSighting:
    """The exit's one ✓→✗ (narration C4, CMD-H turn 30): Archduke Charles
    last seen at Franconia on turn 10 — a province in FULL view, empty of
    him since — and the sighting module, skipping every frozen snapshot in
    a full-view province, handed the row an OLDER Tyrol sighting (turn 8)
    while the store's reader said Franconia. The most recent knowledge
    wins; its label is last_known."""

    def _stage(self, world):
        from backend.models.intel import FULL, LAST_KNOWN
        world.current_turn = 30
        name = "ArchdukeCharles"
        charles = world.marshals[name]
        charles.location = "Carniola"
        for loc in ("Franconia", "Tyrol"):
            world.intel[loc].known_marshals = [
                {"name": name, "nation": "Austria", "strength": 25000}]
        world.intel["Franconia"].visibility = FULL
        world.intel["Franconia"].last_updated_turn = 10
        world.intel["Tyrol"].visibility = LAST_KNOWN
        world.intel["Tyrol"].last_updated_turn = 8
        world.intel["Carniola"].visibility = "unknown"
        assert world.get_last_known_location(name)[0] == "Franconia"
        return name

    def test_the_latest_sighting_wins(self, world):
        from backend.game_logic import intel_surfaces as IS
        name = self._stage(world)
        rows = {r["roster_name"]: r for r in IS.enemy_sightings(world, "France")}
        assert rows[name]["location"] == "Franconia"
        assert rows[name]["visibility"] == "last_known"
        assert rows[name]["intel_turn"] == 10
        assert rows[name]["source"] == "snapshot"

    def test_the_live_read_still_outranks_the_snapshot(self, world):
        from backend.game_logic import intel_surfaces as IS
        from backend.models.intel import FULL
        name = self._stage(world)
        world.marshals[name].location = "Franconia"   # he stands there, in full view
        world.intel["Franconia"].visibility = FULL
        rows = {r["roster_name"]: r for r in IS.enemy_sightings(world, "France")}
        assert rows[name]["source"] == "live"
        assert rows[name]["location"] == "Franconia"

    def test_a_man_in_plain_sight_keeps_no_stale_row(self, world):
        """The live read is the whole truth for a man standing in a
        full-view province today: an empty corps there gets no row from an
        older full-view snapshot elsewhere (SR-6a's own pin, kept)."""
        from backend.game_logic import intel_surfaces as IS
        from backend.models.intel import FULL
        name = self._stage(world)
        world.marshals[name].location = "Munich"
        world.marshals[name].strength = 0
        world.intel["Munich"].visibility = FULL
        world.intel["Munich"].known_marshals = []
        rows = {r["roster_name"]: r for r in IS.enemy_sightings(world, "France")}
        assert name not in rows

    def test_a_phantom_label_rides_no_row(self, world):
        """A full-view snapshot naming a man on no roster (SR-6a's ledger
        pin: Uxbridge at Waterloo) is yesterday's label, not a sighting."""
        from backend.game_logic import intel_surfaces as IS
        from backend.models.intel import FULL
        self._stage(world)
        world.intel["Franconia"].known_marshals.append(
            {"name": "Uxbridge", "nation": "Austria", "strength": 18000})
        world.intel["Franconia"].visibility = FULL
        rows = {r["roster_name"]: r for r in IS.enemy_sightings(world, "France")}
        assert "Uxbridge" not in rows
        assert rows["ArchdukeCharles"]["location"] == "Franconia"

    def test_lever_down_the_older_tyrol_row_returns(self, world, monkeypatch):
        from backend.game_logic import intel_surfaces as IS
        monkeypatch.setattr(IS, "A_FULL_LABEL_KEEPS_ITS_LAST_SIGHTING", False)
        name = self._stage(world)
        rows = {r["roster_name"]: r for r in IS.enemy_sightings(world, "France")}
        assert rows[name]["location"] == "Tyrol"


# ════════════════════════════════════════════════════════════════════════
# The driven board (the probe runner is the harness)
# ════════════════════════════════════════════════════════════════════════

DRIVEN_SEEDS = ("historical", "austerlitz", "eylau")


def _run_probe(seed: str, out_dir: Path) -> dict:
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(REPO_ROOT), LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "SOVEREIGN_SEED"):
        env.pop(key, None)
    out = out_dir / f"{seed}.json"
    proc = subprocess.run([sys.executable, str(PROBE), "--seed", seed, "--out", str(out)],
                          cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
                          timeout=1800)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(out.read_text(encoding="utf-8"))


class TestTheDrivenBoard:
    @pytest.fixture(scope="class")
    def records(self, tmp_path_factory):
        out_dir = tmp_path_factory.mktemp("sf_lb2_probe")
        with ThreadPoolExecutor(max_workers=3) as pool:
            return dict(zip(DRIVEN_SEEDS, pool.map(lambda s: _run_probe(s, out_dir), DRIVEN_SEEDS)))

    def test_the_war_is_produced_on_every_seed(self, records):
        """Living balance C1 (>= 1 AI-vs-AI war in 40 turns on >= 3 of 7
        seeds): measured 7 of 7 on October 3, 2026; three driven here."""
        for seed, rec in records.items():
            wars = rec["wars_declared"]
            assert wars, f"{seed}: no council war in 40 turns"
            assert any(w["attackers"] == ["Prussia"] and w["defenders"] == ["Hanover"]
                       for w in wars), (seed, wars)

    def test_the_crisis_opened_at_coerce(self, records):
        for seed, rec in records.items():
            prussia = [c for c in rec["crises_opened"] if c["coveter"] == "Prussia"]
            assert prussia and prussia[0]["opened_at_price"] == "coerce", (seed, prussia)
            assert prussia[0]["target"] == "Hanover"

    def test_only_a_prize_opens(self, records):
        """The addendum: no fight-road theatre — every crisis the board
        opens is one its court could declare (Sardinia's free strength of 0
        and Russia's war with France fore-warn nothing)."""
        for seed, rec in records.items():
            coveters = {c["coveter"] for c in rec["crises_opened"]}
            assert coveters == {"Prussia"}, (seed, rec["crises_opened"])

    def test_the_restraints_held_at_the_opening(self, records):
        for seed, rec in records.items():
            opened = next(c for c in rec["crises_opened"] if c["coveter"] == "Prussia")
            row = next(r for r in rec["rows"]
                       if r.get("nation") == "Prussia" and r.get("against") == "Hanover"
                       and r["turn"] == opened["opened_turn"])
            assert row["outmatched"] and row["ladder"], (seed, row)

    @pytest.mark.xfail(
        strict=True,
        reason=("SF-LB-2 §6.4's variance clause — the crisis turn spans >= 3 turns across "
                "the seeds — is MEASURED NOT MET (October 3, 2026): the opening waits on "
                "Prussia's chest clearing AI_WAR_TREASURY_FLOOR at the council's "
                "pre-income siting, which the unseeded economy reaches on turn 9 (10 on "
                "marengo) on every seed. Not tuned, by the ruling's own instruction; put "
                "to the user. This xfail flips the day the clause is met."),
    )
    def test_the_crisis_turn_varies_across_seeds(self, records):
        turns = {next(c for c in rec["crises_opened"] if c["coveter"] == "Prussia")["opened_turn"]
                 for rec in records.values()}
        assert len(turns) >= 3, turns

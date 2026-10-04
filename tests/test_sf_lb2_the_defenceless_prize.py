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
  Hanover; the variance clause — MEASURED NOT MET twice (SF-LB-2, SF-LB-2b)
  — is MET by SF-LB-2c "The patient ask" (§6 row 15): the strict xfails
  flipped on the shipped tree.
- SF-LB-2c's own pins (`TestThePatientAsk`): the seeded dwell before a
  court's FIRST design ask, historical = 0, the anchor serialized.
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
        """RE-SEATED by SF-LB-2b "The Chest the Council Can Spend" (October
        3, 2026): the OPENING reads the chest the court will have when the
        turn ends (`ledger.chest_forecast`), so `penniless` at the opening
        now means the PROJECTED chest under the floor — the live chest is
        staged so that chest + this turn's Net = floor - 1 (the SF-LB-2 pin
        had staged the live chest alone at floor - 1, which the forecast
        read carries over by design — see TestTheChestTheCouncilCanSpend)."""
        from backend.game_logic.ledger import chest_forecast
        _climb_ladder(world)
        net = int(chest_forecast(world, "Prussia")["net"])
        world.nation_gold["Prussia"] = WC.AI_WAR_TREASURY_FLOOR - 1 - net
        _fresh(world)
        assert WC._restraint_block_reason(world, "Prussia", "Hanover") == "penniless"
        assert WC._restraint_block_reason(world, "Prussia", "Hanover", forecast=True) == "penniless"
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
PROBE_RECORD_DIR = REPO_ROOT / "docs" / "audits" / "probes" / "sf_lb2"


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

    def test_the_crisis_turn_varies_across_seeds(self, records):
        """SF-LB-2 §6.4's variance clause — the crisis turn spans >= 3 turns
        across the seeds. MEASURED NOT MET twice (SF-LB-2 {9, 10}; SF-LB-2b
        {5, 9}: the ladder was climbed on the same turns everywhere because
        the court-to-court design ask fired the first turn the court stood
        at its rung). MET by SF-LB-2c "The patient ask" (§6 row 15, October
        3, 2026): the first ask waits a seeded dwell of 0..4 turns, and the
        driven seeds open on historical 5 / austerlitz 7 / eylau 13. Was a
        strict xfail; it flipped on the shipped tree."""
        turns = {min(c["opened_turn"] for c in rec["crises_opened"] if c["coveter"] == "Prussia")
                 for rec in records.values()}
        assert len(turns) >= 3, turns

    def test_the_opening_no_longer_waits_on_the_spent_purse(self, records):
        """SF-LB-2b's own clause on the driven seeds: the FIRST opening is the
        turn after the first after-turn snapshot on which the court is READY
        — the ladder climbed AND the rung at `coerce` or above (the two
        gates the opening reads besides the restraints) — so the purse never
        delays it (on the historical seed turn 5, where the SF-LB-2 tree
        waited to turn 9 on the pre-income chest). Re-stated by SF-LB-2c
        (October 3, 2026): the SF-LB-2b form read `opened <= first_ladder +
        2`, which held only while the design ask fired on the same turn as
        the ladder's other refusal; with the seeded dwell the ask's own
        refusal is what lifts the weight to `coerce` (austerlitz: ladder on
        turn 4, refusal on 5, coerce on 6, open on 7), so the clause is now
        read against READY, the purse-free condition it always meant. A
        measurement on each seed, not a schedule."""
        for seed, rec in records.items():
            opened = min(c["opened_turn"] for c in rec["crises_opened"] if c["coveter"] == "Prussia")
            first_ready = min(r["turn"] for r in rec["rows"]
                              if r.get("nation") == "Prussia" and r.get("against") == "Hanover"
                              and r["ladder"] and r.get("price") in ("coerce", "fight"))
            assert opened <= first_ready + 1, (seed, opened, first_ready)

    def test_the_seven_seed_record_spans_three_turns(self):
        """THE STANDING RULE (the user, October 3, 2026): a seeded game — a
        council war whose turn is the same on every seed is a defect. Every
        coveter→target pair that opens on >= 3 seeds spans >= 3 distinct
        FIRST-opening turns. Was a strict xfail (SF-LB-2b's record: turn 5 on
        six seeds, 9 on eylau); flipped by SF-LB-2c "The patient ask" —
        Prussia->Hanover now opens historical 5 / austerlitz 7 / friedland 7 /
        jena 5 / ulm 8 / marengo 5 / eylau 13. The record is the probe's own output
        (`tools/_sf_lb1_fight_bar_probe.py --seed <s> --out
        docs/audits/probes/sf_lb2/shipped_<s>.json`), re-run and overwritten
        by the slice that moves it."""
        openings = _first_openings_in_record()
        assert "Prussia->Hanover" in openings
        for pair, by_seed in openings.items():
            if len(by_seed) >= 3:
                assert len(set(by_seed.values())) >= 3, (pair, by_seed)

    def test_the_record_is_seven_seeds_and_marengo_cooled_and_reopened(self):
        """The record's shape, pinned so a re-run that loses it is noticed:
        seven seeds; on marengo the first crisis (turn 5) cooled when the
        seeded weight dipped below coerce and a second opened on turn 10 —
        the one place on the record where the seed moves the campaign's
        story, and why the WAR's turn spans three values while the opening
        spans two."""
        paths = sorted(PROBE_RECORD_DIR.glob("shipped_*.json"))
        assert len(paths) == 7, [p.name for p in paths]
        marengo = json.loads((PROBE_RECORD_DIR / "shipped_marengo.json").read_text(encoding="utf-8"))
        prussian = [c["opened_turn"] for c in marengo["crises_opened"] if c["coveter"] == "Prussia"]
        assert len(prussian) >= 2 and prussian[0] < prussian[1], prussian
        war_turns = set()
        for path in paths:
            rec = json.loads(path.read_text(encoding="utf-8"))
            for war in rec["wars_declared"]:
                if war["attackers"] == ["Prussia"] and war["defenders"] == ["Hanover"]:
                    war_turns.add(int(war["started_turn"]))
        assert len(war_turns) >= 3, war_turns


def _first_openings_in_record() -> dict:
    openings: dict = {}
    for path in sorted(PROBE_RECORD_DIR.glob("shipped_*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        for crisis in rec["crises_opened"]:
            key = f"{crisis['coveter']}->{crisis['target']}"
            prior = openings.setdefault(key, {}).get(rec["seed"])
            turn = int(crisis["opened_turn"])
            openings[key][rec["seed"]] = turn if prior is None else min(prior, turn)
    return openings

# ════════════════════════════════════════════════════════════════════════
# SF-LB-2b "The Chest the Council Can Spend" (SCORE_FINISH_SPEC.md §6 row 14,
# RULED + BUILT October 3, 2026; rules SYSTEMS_REFERENCE.md §85.8)
# ════════════════════════════════════════════════════════════════════════

def _open_crisis_fixture(world, coveter="Prussia", holder="Hanover"):
    """A fore-warned Prussian crisis on the record, two turns old, with the
    ladder climbed — the declaration gate's own geometry."""
    world.current_turn = 10  # the record's turn stamps must be positive
    _climb_ladder(world, coveter, holder)
    turn = int(world.current_turn)
    world.war_intents = {coveter: {
        "coveter": coveter, "target": holder, "design_id": "hanoverian_prize",
        "want_title": "The Hanoverian Prize", "opened_turn": turn - 3,
        "foregrounded": True, "foregrounded_turn": turn - 3,
        "coerce_recorded_turn": turn - 2, "treaty_broken_turn": None,
        "opened_at_price": "coerce",
    }}
    _fresh(world)


class TestTheChestTheCouncilCanSpend:
    def test_the_lever_down_is_the_live_read(self, world, monkeypatch):
        """Lever down = SF-LB-2 byte for byte: `forecast=True` is inert."""
        monkeypatch.setattr(WC, "THE_COUNCIL_SPENDS_THE_TURNS_INCOME", False)
        world.nation_gold["Prussia"] = 120
        _fresh(world)
        assert WC._restraint_block_reason(world, "Prussia", "Hanover") == "penniless"
        assert WC._restraint_block_reason(world, "Prussia", "Hanover", forecast=True) == "penniless"

    def test_the_opening_reads_the_chest_the_court_can_spend(self, world):
        """A court whose live chest is under the floor and whose income
        carries it over OPENS (the forecast read is None); the live read
        still says penniless — the two reads differ only at the chest."""
        from backend.game_logic.ledger import chest_forecast
        world.nation_gold["Prussia"] = 120
        _fresh(world)
        forecast = chest_forecast(world, "Prussia")
        assert forecast["chest"] == 120
        assert forecast["projected"] == 120 + forecast["net"]
        assert forecast["net"] >= WC.AI_WAR_TREASURY_FLOOR - 120, forecast
        assert WC._restraint_block_reason(world, "Prussia", "Hanover") == "penniless"
        assert WC._restraint_block_reason(world, "Prussia", "Hanover", forecast=True) is None

    def test_an_income_that_does_not_carry_it_is_still_penniless(self, world, monkeypatch):
        """The forecast is a projection, not a waiver: a court whose chest
        plus this turn's Net stays under the floor reads penniless on the
        opening too."""
        import backend.game_logic.ledger as LG
        world.nation_gold["Prussia"] = 120
        _fresh(world)
        real = LG.chest_forecast

        def starved(w, nation):
            out = real(w, nation)
            return {"chest": out["chest"], "net": 100, "projected": out["chest"] + 100}
        monkeypatch.setattr(LG, "chest_forecast", starved)
        assert WC._restraint_block_reason(world, "Prussia", "Hanover", forecast=True) == "penniless"

    def test_the_forecast_is_the_ledgers_own_net(self, world):
        """ONE seam: the projection is the chest plus the Net the LAWS tab
        and the end-turn banner quote (`ledger._build_economy` with no
        applied record) — for the player's chest too."""
        from backend.game_logic.ledger import _build_economy, chest_forecast
        for nation, chest in (("Prussia", int(world.nation_gold["Prussia"])),
                              (world.player_nation, int(world.gold))):
            out = chest_forecast(world, nation)
            assert out["chest"] == chest
            assert out["net"] == int(_build_economy(world, nation)["net"])
            assert out["projected"] == out["chest"] + out["net"]

    def test_the_lapse_forecast_reads_the_same_seam(self, world, monkeypatch):
        """`reforms.lapse_forecast` and the council read ONE projection —
        move the seam and both move. Staged: the player's first authored
        law is marked in force (no law is in force on the boot world — a
        saving France buys the Staff on turn 7)."""
        import backend.game_logic.ledger as LG
        from backend.game_logic import reforms as RF
        player = world.player_nation
        row = RF.deck(world, player)[0]
        row["enacted_turn"] = 1
        assert RF.laws_in_force(world, player)
        monkeypatch.setattr(LG, "chest_forecast",
                            lambda w, n: {"chest": 10, "net": -5000, "projected": -4990})
        doomed = RF.lapse_forecast(world, player)
        assert doomed is not None and doomed["shortfall"] == 4990, doomed
        assert "10" in doomed["line"] and "-5,000" in doomed["line"], doomed["line"]

    def test_no_second_copy_of_the_projection(self):
        """An AST census: `war_council.py` never calls `_build_economy`
        (its chest read comes to the one seam), and `reforms.lapse_forecast`
        — the projection's other reader — calls `chest_forecast` and never
        `_build_economy`. (`reforms.ai_purse_refusal` reads the forecast NET
        alone, a different question from "where does the chest stand when
        the turn ends"; it is not a projection and is not counted.)"""
        def _calls(node, name):
            return [n for n in ast.walk(node) if isinstance(n, ast.Call)
                    and getattr(n.func, "id", getattr(n.func, "attr", "")) == name]
        wc = ast.parse((BACKEND / "game_logic" / "war_council.py").read_text(encoding="utf-8"))
        assert not _calls(wc, "_build_economy")
        assert _calls(wc, "chest_forecast"), "war_council never reads chest_forecast"
        rf = ast.parse((BACKEND / "game_logic" / "reforms.py").read_text(encoding="utf-8"))
        lapse = next(n for n in ast.walk(rf) if isinstance(n, ast.FunctionDef)
                     and n.name == "lapse_forecast")
        assert not _calls(lapse, "_build_economy"), "lapse_forecast grew its own projection"
        assert _calls(lapse, "chest_forecast")

    def test_the_opening_calls_the_forecast_read_and_the_declaration_does_not(self):
        """The call-site census: inside `process_war_council`, exactly one
        `_restraint_block_reason(...)` call passes `forecast=True` (step 3,
        the opening) and the declaration's call (step 1) passes nothing."""
        src = (BACKEND / "game_logic" / "war_council.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == "process_war_council")
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                 and getattr(n.func, "id", "") == "_restraint_block_reason"]
        assert len(calls) == 2, [c.lineno for c in calls]
        forecast_flags = [any(k.arg == "forecast" and getattr(k.value, "value", None) is True
                              for k in c.keywords) for c in calls]
        assert sorted(forecast_flags) == [False, True], forecast_flags

    def test_the_declaration_still_refuses_a_live_chest_under_the_floor(self, world):
        """Step 1 keeps the live chest: a fore-warned crisis whose court holds
        120 gold with an income that would clear the floor is NOT declared —
        the soft block names `penniless`; with the chest filled the same
        poll declares."""
        _open_crisis_fixture(world)
        world.nation_gold["Prussia"] = 120
        _fresh(world)
        assert WC._restraint_block_reason(world, "Prussia", "Hanover", forecast=True) is None
        before = set(world.get_nations_at_war_with("Prussia"))
        _quiet(process_war_council, world)
        record = world.war_intents.get("Prussia")
        assert record is not None and record.get("last_soft_block") == "penniless", record
        assert set(world.get_nations_at_war_with("Prussia")) == before
        world.nation_gold["Prussia"] = 2000
        _fresh(world)
        _quiet(process_war_council, world)
        assert "Prussia" not in world.war_intents
        assert "Hanover" in world.get_nations_at_war_with("Prussia")

    def test_the_opening_opens_on_the_forecast(self, world):
        """Step 3 end to end: the ladder climbed, the live chest at 120, the
        income carrying it over — the crisis OPENS at coerce this poll (the
        SF-LB-2 tree read penniless here)."""
        _climb_ladder(world)
        world.nation_gold["Prussia"] = 120
        _fresh(world)
        view = get_nation_intent("Prussia", world)
        assert view.against == "Hanover" and crisis_rung_holds(world, "Prussia", view)
        _quiet(process_war_council, world)
        record = world.war_intents.get("Prussia")
        assert record is not None and record["target"] == "Hanover", world.war_intents
        assert record["opened_at_price"] == "coerce"

    def test_lever_down_the_opening_waits_on_the_live_chest(self, world, monkeypatch):
        monkeypatch.setattr(WC, "THE_COUNCIL_SPENDS_THE_TURNS_INCOME", False)
        _climb_ladder(world)
        world.nation_gold["Prussia"] = 120
        _fresh(world)
        _quiet(process_war_council, world)
        assert "Prussia" not in world.war_intents

    def test_every_court_reads_the_same_seam(self, world):
        """GR5: the forecast arm is not Prussia's. Six courts pacified toward
        France for the test, each with 50 gold live: every one reads
        `penniless` live, and the OPENING's read is None exactly where the
        court's own forecast Net carries 50 over the floor (measured at boot:
        Russia 1,515 / Britain 3,647 / Spain 1,717 / Sweden 1,004 / the
        Ottoman 1,808 carry it; Austria's 405 does not — 455 against 500, so
        Vienna reads penniless on BOTH arms). Both verdicts are asserted
        against the seam's own figure, never a list."""
        from backend.game_logic.diplomacy import set_diplomatic_state
        from backend.game_logic.ledger import chest_forecast
        courts = ("Austria", "Russia", "Britain", "Spain", "Sweden", "Ottoman")
        for court in courts:
            for enemy in list(world.get_nations_at_war_with(court)):
                set_diplomatic_state(world, enemy, court, "PEACE")
            world.nation_gold[court] = 50
        _fresh(world)
        verdicts = {}
        for court in courts:
            projected = int(chest_forecast(world, court)["projected"])
            assert WC._restraint_block_reason(world, court, "Hanover") == "penniless", court
            fc = WC._restraint_block_reason(world, court, "Hanover", forecast=True)
            expected = None if projected >= WC.AI_WAR_TREASURY_FLOOR else "penniless"
            assert fc == expected, (court, projected, fc)
            verdicts[court] = fc
        # both arms are reachable on this board — a pin that only ever saw
        # None (or only ever penniless) would be inert about the floor.
        assert None in verdicts.values() and "penniless" in verdicts.values(), verdicts


# ════════════════════════════════════════════════════════════════════════
# SF-LB-2c "The Patient Ask" (SCORE_FINISH_SPEC.md §6 row 15, RULED
# October 3, 2026 under the user's delegation; rules SYSTEMS_REFERENCE.md
# §85.9) — a seeded dwell of 0..4 turns before a court's FIRST
# court-to-court design ask of a holder; the historical seed collapses it
# to 0, so BASELINE_SERIES and every historical pin are byte-identical.
# ════════════════════════════════════════════════════════════════════════

def _design_ask(world, asker="Prussia", holder="Hanover"):
    _fresh(world)
    prop = AD._evaluate_ai_ai_proposal(asker, holder, world)
    return bool(prop and prop.get("type") == "design_ask"
                and prop.get("proposer") == asker and prop.get("target") == holder)


class TestThePatientAsk:
    def test_the_court_stands_at_its_ask_rung_at_the_boot(self, world):
        """The fixture's own geometry, pinned so the arms below are not
        vacuous: Prussia stands at a design-ask rung over Hanover at the
        boot, so trigger 0a would ask this very turn."""
        view = get_nation_intent("Prussia", world)
        assert view.against == "Hanover"
        assert view.price in AD.DESIGN_ASK_RUNGS

    def test_the_historical_seed_never_waits_and_writes_nothing(self, world):
        assert world.campaign_seed == "historical"
        assert AD.design_ask_patience(world, "Prussia", "Hanover") == 0
        assert _design_ask(world)
        assert world.design_ask_first_stood == {}

    def test_the_dwell_is_the_seeds_own_term(self, world):
        """The namespace is the ruling's, read through the raw helper — so a
        renamed key (which would silently re-draw every seed) is red."""
        from backend.game_logic.campaign_variance import seeded_int
        for seed in ("austerlitz", "friedland", "jena", "ulm", "marengo", "eylau"):
            world.campaign_seed = seed
            assert AD.design_ask_patience(world, "Prussia", "Hanover") == seeded_int(
                seed, "design_ask_patience::Prussia::Hanover", 0, 4), seed
        # the measured draws the record rests on (eylau waits the most)
        world.campaign_seed = "eylau"
        assert AD.design_ask_patience(world, "Prussia", "Hanover") == 4
        world.campaign_seed = "jena"
        assert AD.design_ask_patience(world, "Prussia", "Hanover") == 0

    def test_the_first_ask_waits_out_the_dwell(self, world):
        world.campaign_seed = "eylau"          # patience 4 for this pair
        start = int(world.current_turn)
        for offset in range(4):
            world.current_turn = start + offset
            assert not _design_ask(world), offset
        assert world.design_ask_first_stood == {"Prussia>Hanover": start}
        world.current_turn = start + 4
        assert _design_ask(world)
        # the anchor is the FIRST stand, never re-written
        assert world.design_ask_first_stood == {"Prussia>Hanover": start}

    def test_a_pair_already_asked_never_waits_again(self, world):
        world.campaign_seed = "eylau"
        assert record_diplomatic_refusal(world, "Prussia", "Hanover", "design_ask")
        assert not AD.design_ask_patience_holds(world, "Prussia", "Hanover")
        assert world.design_ask_first_stood == {}

    def test_a_zero_dwell_seed_writes_nothing(self, world):
        world.campaign_seed = "jena"
        assert _design_ask(world)
        assert world.design_ask_first_stood == {}

    def test_the_lever_down_is_byte_for_byte(self, world, monkeypatch):
        monkeypatch.setattr(AD, "A_COURT_IS_PATIENT_BEFORE_IT_ASKS", False)
        world.campaign_seed = "eylau"
        assert AD.design_ask_patience(world, "Prussia", "Hanover") == 0
        assert _design_ask(world)
        assert world.design_ask_first_stood == {}

    def test_the_wait_does_not_shadow_the_pairs_other_triggers(self, world):
        """Like the dedupe window, the dwell skips the ASK, not the pair:
        trigger 4 (a poor court and a rich one at peace → open borders)
        still answers while Prussia waits."""
        world.campaign_seed = "eylau"
        world.nation_gold["Prussia"] = 100
        world.nation_gold["Hanover"] = 1000
        _fresh(world)
        assert world.get_diplomatic_state("Prussia", "Hanover") == "PEACE"
        prop = AD._evaluate_ai_ai_proposal("Prussia", "Hanover", world)
        assert prop and prop["type"] == "open_borders", prop
        assert world.design_ask_first_stood == {"Prussia>Hanover": int(world.current_turn)}

    def test_the_anchor_survives_a_save(self, world):
        world.campaign_seed = "eylau"
        assert not _design_ask(world)
        anchor = dict(world.design_ask_first_stood)
        assert anchor
        loaded = WorldState.from_dict(world.to_dict())
        assert loaded.design_ask_first_stood == anchor
        assert loaded.campaign_seed == "eylau"

    def test_the_player_targeted_purchase_is_untouched(self):
        """AI-vs-AI only by construction: the patience is read in trigger 0a
        and nowhere on the player road (`_generate_intent_ask`)."""
        src = (BACKEND / "game_logic" / "ai_diplomacy.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        callers = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for sub in ast.walk(node):
                    if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                            and sub.func.id == "design_ask_patience_holds"):
                        callers.add(node.name)
        assert callers == {"_evaluate_ai_ai_proposal"}, callers

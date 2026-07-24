"""AI-2 — intent-driven peacetime pursuit (Stage C).

docs/AI_INTENT_SPEC.md §4.2 / §4.2b / §4.2c: the rungs fire on what the
nation is trying to achieve — the design purchase, sell-neutrality, the
alignment ask, the widened bandwagon, and the AI-AI design/alignment
triggers — within the §4.2c delivery budget. Pin 18: deckless courts
fall through to the legacy rungs byte-identically.
"""

from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy
from backend.game_logic.ai_diplomacy import (
    INTENT_ASK_BUDGET_PER_TURN,
    _evaluate_ai_ai_proposal,
    _generate_intent_ask,
    _is_on_cooldown,
    _process_ai_sponsorships,
    _resolve_ai_ai_proposal,
    build_ai_proposal_dialogue,
    process_diplomatic_phase,
)
from backend.game_logic.instruments import pledge_guarantee
from backend.game_logic.intent import IntentView, get_nation_intent
from backend.models.world_state import WorldState

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_dict(
        WorldState.from_scenario(str(SCENARIO_PATH)).to_dict())


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _make_war(world, a, b):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = int(world.current_turn)
    world.invalidate_bloc_members_cache()


def _set_relation(world, a, b, value):
    world.nation_relations[world._make_diplo_key(a, b)] = int(value)
    world.invalidate_bloc_members_cache()


def _fake_view(nation, *, against, price, weight=50,
               want_id="test_design"):
    return IntentView(nation=nation, want_id=want_id,
                      want_title="Test Design",
                      want_type="acquire_regions", against=against,
                      weight=weight, price=price)


# ═══════════════════════════════════════════════════════════════════════
# Arm 1 — the design purchase
# ═══════════════════════════════════════════════════════════════════════


class TestDesignPurchase:
    def _prussia_wants_french_hanover(self, world):
        """France holds Hanover; Prussia's design obstacle becomes
        France at the `buy` rung (warm relation + a third-party
        guarantee's deterrent pull the weight under the align floor)."""
        for region_name in ("Hanover",):
            world.regions[region_name].controller = "France"
        _set_relation(world, "France", "Prussia", 40)
        pledge_guarantee(world, guarantor="Denmark", protected="France")
        view = get_nation_intent("Prussia", world)
        assert view.against == "France"
        assert view.price == "buy", view
        return view

    def test_buy_rung_offers_gold_for_the_province(self, world):
        self._prussia_wants_french_hanover(world)
        proposal = process_diplomatic_phase("Prussia", world)
        assert proposal is not None
        assert proposal["proposal_type"] == "design_purchase"
        assert proposal["intent_ask"] is True
        terms = proposal["terms"]
        demands = [d for d in terms["demands"]
                   if d["type"] == "territory_cede"]
        assert demands and demands[0]["regions"] == ["Hanover"]
        gold = [s for s in terms["sweeteners"] if s["type"] == "gold_lump"]
        assert gold and gold[0]["value"] > 0

    def test_the_courier_delivers_it_as_a_named_envoy(self, world):
        """Beat 1 (§4.6a): the ask arrives as somebody talking — the
        named envoy in the Voice Bible register, not a dispatch line."""
        self._prussia_wants_french_hanover(world)
        proposal = process_diplomatic_phase("Prussia", world)
        dialogue = build_ai_proposal_dialogue(proposal, world)
        assert dialogue["type"] == "incoming_proposal"
        payload = dialogue["popup_payload"]
        assert payload["diplomat_name"] == "Hardenberg"
        assert payload.get("diplomat_line")

    def test_accepting_cedes_the_province_and_pays(self, world):
        self._prussia_wants_french_hanover(world)
        proposal = process_diplomatic_phase("Prussia", world)
        dialogue = build_ai_proposal_dialogue(proposal, world)
        world.dialogue_manager.push(dialogue)
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        offered = [s for s in proposal["terms"]["sweeteners"]
                   if s["type"] == "gold_lump"][0]["value"]
        france_gold = int(world.nation_gold.get("France", 0))
        result = executor._diplomatic._handle_accept_ai_proposal(
            dialogue, world)
        assert result["success"], result["message"]
        assert world.regions["Hanover"].controller == "Prussia"
        assert world.nation_gold["France"] == france_gold + offered
        # §3.1a (a): the design satisfies the moment the province moves —
        # descent for free, no latch anywhere.
        after = get_nation_intent("Prussia", world)
        assert after.price != "buy"

    def test_ask_rung_sends_the_polite_request(self, world, monkeypatch):
        self._prussia_wants_french_hanover(world)
        monkeypatch.setattr(
            "backend.game_logic.intent.get_nation_intent",
            lambda nation, w: _fake_view(nation, against="France",
                                         price="ask", weight=30,
                                         want_id="hanoverian_prize"))
        proposal = _generate_intent_ask("Prussia", world, "PEACE", 10, 1.0)
        assert proposal is not None
        assert proposal["proposal_type"] == "design_purchase"
        assert not proposal["terms"]["sweeteners"]  # no gold at `ask`


# ═══════════════════════════════════════════════════════════════════════
# Arm 2 — sell-neutrality (AI-2d's Stage C half)
# ═══════════════════════════════════════════════════════════════════════


class TestSellNeutrality:
    def _prussia_at_war_france_looming(self, world):
        _make_war(world, "Prussia", "Austria")
        _set_relation(world, "France", "Prussia", -15)
        world.nation_gold["Prussia"] = 2000

    def test_belligerent_offers_to_buy_frances_neutrality(self, world):
        self._prussia_at_war_france_looming(world)
        proposal = process_diplomatic_phase("Prussia", world)
        assert proposal is not None
        assert proposal["proposal_type"] == "sell_neutrality"
        assert proposal["intent_ask"] is True
        terms = proposal["terms"]
        assert terms["compact"] == "sell_neutrality"
        assert terms["compact_aim"] == "Austria"
        gold = [s for s in terms["sweeteners"] if s["type"] == "gold_lump"]
        assert gold and gold[0]["value"] >= 250

    def test_accepting_mints_the_compact_and_binds_france(self, world):
        self._prussia_at_war_france_looming(world)
        proposal = process_diplomatic_phase("Prussia", world)
        dialogue = build_ai_proposal_dialogue(proposal, world)
        world.dialogue_manager.push(dialogue)
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        result = executor._diplomatic._handle_accept_ai_proposal(
            dialogue, world)
        assert result["success"], result["message"]
        compacts = [r for r in world.directed_sponsorships
                    if r["kind"] == "neutrality"]
        assert len(compacts) == 1
        assert compacts[0]["payer"] == "Prussia"
        assert compacts[0]["recipient"] == "France"
        # The §3.3 bond: France entering the war against the payer is
        # reneging — the strongest mark in the game.
        from backend.game_logic.instruments import (
            has_renege_grievance,
            process_instruments,
        )
        _make_war(world, "France", "Prussia")
        events = process_instruments(world)
        assert any(e["type"] == "sponsorship_reneged"
                   and e["breaker"] == "France" for e in events)
        assert has_renege_grievance(world, "Prussia", "France")

    def test_no_offer_when_france_is_in_the_war(self, world):
        _make_war(world, "Prussia", "Austria")
        _make_war(world, "Prussia", "France")
        world.nation_gold["Prussia"] = 2000
        proposal = process_diplomatic_phase("Prussia", world)
        assert (proposal is None
                or proposal.get("proposal_type") != "sell_neutrality")

    def test_no_offer_when_france_is_no_threat(self, world):
        _make_war(world, "Prussia", "Austria")
        _set_relation(world, "France", "Prussia", 30)
        world.nation_gold["Prussia"] = 2000
        # Keep the mirror off Prussia: France's corps are nowhere near.
        from backend.game_logic import intent as intent_module
        assert intent_module  # (the mirror read is live; relation governs)
        proposal = process_diplomatic_phase("Prussia", world)
        assert (proposal is None
                or proposal.get("proposal_type") != "sell_neutrality")


# ═══════════════════════════════════════════════════════════════════════
# Arm 3 — the alignment ask
# ═══════════════════════════════════════════════════════════════════════


class TestAlignmentAsk:
    def test_court_at_align_courts_the_obstacles_enemy(self, world):
        # Prussia (align, against Hanover) approaches France once France
        # reads hostile to Hanover.
        _set_relation(world, "France", "Hanover", -20)
        view = get_nation_intent("Prussia", world)
        assert view.price == "align" and view.against == "Hanover"
        proposal = process_diplomatic_phase("Prussia", world)
        assert proposal is not None
        assert proposal["intent_ask"] is True
        assert proposal["proposal_type"] in (
            "open_borders", "non_aggression", "defensive_alliance")

    def test_quiet_when_france_is_warm_to_the_obstacle(self, world):
        _set_relation(world, "France", "Hanover", 20)
        proposal = _generate_intent_ask("Prussia", world, "PEACE", -10, 1.0)
        assert proposal is None


# ═══════════════════════════════════════════════════════════════════════
# §4.2c — the delivery budget
# ═══════════════════════════════════════════════════════════════════════


class TestDeliveryBudget:
    def _run_phase(self, world, monkeypatch, proposals_by_nation):
        from backend.game_logic.turn_manager import TurnManager
        delivered = []
        monkeypatch.setattr(
            "backend.game_logic.turn_manager.deliver_ai_proposal"
            if False else
            "backend.game_logic.ai_diplomacy.deliver_ai_proposal",
            lambda proposal, w: delivered.append(proposal) or {})
        monkeypatch.setattr(
            "backend.game_logic.ai_diplomacy.process_diplomatic_phase",
            lambda nation, w: proposals_by_nation.get(nation))
        tm = TurnManager(world)
        tm._process_ai_diplomatic_phase()
        return delivered

    def test_intent_budget_caps_at_two(self, world, monkeypatch):
        nations = list(world.enemy_nations)[:4]
        proposals = {
            n: {"source": n, "proposal_type": "design_purchase",
                "intent_ask": True, "decision_reason": "agenda_pursuit",
                "terms": {}}
            for n in nations
        }
        delivered = self._run_phase(world, monkeypatch, proposals)
        assert len(delivered) == INTENT_ASK_BUDGET_PER_TURN

    def test_intent_asks_never_starve_on_the_bandwagon_cap(self, world,
                                                           monkeypatch):
        """The §4.2b marquee case: two courting belligerents survive a
        bandwagon flood in the same turn."""
        nations = list(world.enemy_nations)[:6]
        proposals = {}
        for index, nation in enumerate(nations):
            if index < 3:
                proposals[nation] = {
                    "source": nation, "proposal_type": "open_borders",
                    "decision_reason": "hegemony_pressure", "terms": {}}
            else:
                proposals[nation] = {
                    "source": nation, "proposal_type": "sell_neutrality",
                    "intent_ask": True,
                    "decision_reason": "agenda_pursuit", "terms": {}}
        delivered = self._run_phase(world, monkeypatch, proposals)
        bandwagon = [p for p in delivered if not p.get("intent_ask")]
        intent = [p for p in delivered if p.get("intent_ask")]
        assert len(bandwagon) == 2  # MAX_BANDWAGON_PER_TURN unchanged
        assert len(intent) == INTENT_ASK_BUDGET_PER_TURN


class TestOpportunismValve:
    def test_deep_opportunism_bypasses_the_nation_cooldown(
            self, world, monkeypatch):
        cooldowns = ai_diplomacy._get_cooldowns(world)
        cooldowns["Prussia|nation"] = 3
        ai_diplomacy._set_cooldowns(world, cooldowns)
        monkeypatch.setattr(
            "backend.game_logic.intent.get_nation_intent",
            lambda nation, w: _fake_view(nation, against="Austria",
                                         price="buy"))
        _make_war(world, "Austria", "Russia")
        _make_war(world, "Austria", "Britain")
        assert not _is_on_cooldown("Prussia", "design_purchase", world, 0)

    def test_single_war_does_not_open_the_valve(self, world, monkeypatch):
        cooldowns = ai_diplomacy._get_cooldowns(world)
        cooldowns["Prussia|nation"] = 3
        ai_diplomacy._set_cooldowns(world, cooldowns)
        monkeypatch.setattr(
            "backend.game_logic.intent.get_nation_intent",
            lambda nation, w: _fake_view(nation, against="Hanover",
                                         price="buy"))
        assert _is_on_cooldown("Prussia", "design_purchase", world, 0)

    def test_type_cooldown_still_governs(self, world, monkeypatch):
        cooldowns = ai_diplomacy._get_cooldowns(world)
        cooldowns["Prussia|design_purchase"] = 6
        ai_diplomacy._set_cooldowns(world, cooldowns)
        monkeypatch.setattr(
            "backend.game_logic.intent.get_nation_intent",
            lambda nation, w: _fake_view(nation, against="Austria",
                                         price="buy"))
        _make_war(world, "Austria", "Russia")
        _make_war(world, "Austria", "Britain")
        assert _is_on_cooldown("Prussia", "design_purchase", world, 0)


# ═══════════════════════════════════════════════════════════════════════
# The AI-AI intent triggers
# ═══════════════════════════════════════════════════════════════════════


class TestAiAiIntentTriggers:
    def test_design_ask_fires_and_is_refused_on_record(self, world,
                                                       monkeypatch):
        views = {
            "Prussia": _fake_view("Prussia", against="Hanover",
                                  price="buy",
                                  want_id="hanoverian_prize"),
        }
        monkeypatch.setattr(
            "backend.game_logic.intent.get_nation_intent",
            lambda nation, w: views.get(nation,
                                        _fake_view(nation, against=None,
                                                   price="indifferent",
                                                   want_id=None)))
        proposal = _evaluate_ai_ai_proposal("Prussia", "Hanover", world)
        assert proposal == {"type": "design_ask", "proposer": "Prussia",
                            "target": "Hanover"}
        event = _resolve_ai_ai_proposal(proposal, world)
        assert event is not None
        assert event["type"] == "ai_ai_proposal_refused"
        assert event["refused_by"] == "Hanover"
        from backend.game_logic.ai_diplomacy import get_refused_asks
        assert get_refused_asks(world, "Prussia", "Hanover")
        # The dedupe window keeps the every-turn re-poll quiet.
        assert _resolve_ai_ai_proposal(proposal, world) is None

    def test_alignment_ask_courts_the_obstacles_enemy(self, world,
                                                      monkeypatch):
        views = {
            "Prussia": _fake_view("Prussia", against="Hanover",
                                  price="align",
                                  want_id="hanoverian_prize"),
        }
        monkeypatch.setattr(
            "backend.game_logic.intent.get_nation_intent",
            lambda nation, w: views.get(nation,
                                        _fake_view(nation, against=None,
                                                   price="indifferent",
                                                   want_id=None)))
        _set_relation(world, "Sweden", "Hanover", -20)
        proposal = _evaluate_ai_ai_proposal("Prussia", "Sweden", world)
        assert proposal == {"type": "defensive_alliance",
                            "proposer": "Prussia", "target": "Sweden"}

    def test_no_alignment_when_target_is_warm_to_obstacle(self, world,
                                                          monkeypatch):
        views = {
            "Prussia": _fake_view("Prussia", against="Hanover",
                                  price="align",
                                  want_id="hanoverian_prize"),
        }
        monkeypatch.setattr(
            "backend.game_logic.intent.get_nation_intent",
            lambda nation, w: views.get(nation,
                                        _fake_view(nation, against=None,
                                                   price="indifferent",
                                                   want_id=None)))
        _set_relation(world, "Sweden", "Hanover", 20)
        # Neutralize legacy trigger 5 (the pre-existing preemptive
        # alliance under high France-threat) so only trigger 0b is
        # under test: neither court hostile to France.
        _set_relation(world, "France", "Prussia", 10)
        _set_relation(world, "France", "Sweden", 10)
        proposal = _evaluate_ai_ai_proposal("Prussia", "Sweden", world)
        assert proposal is None or proposal.get("type") != (
            "defensive_alliance")


# ═══════════════════════════════════════════════════════════════════════
# The sponsor branch (AI-side)
# ═══════════════════════════════════════════════════════════════════════


class TestAiSponsorships:
    def test_a_sponsor_first_court_funds_a_shared_grievance(self, world):
        events = _process_ai_sponsorships(world)
        assert len(events) == 1
        event = events[0]
        assert event["type"] == "sponsorship_granted"
        payer = event["payer"]
        assert "sponsor" in world.get_statecraft(payer)["reaches_first"]
        assert event["aim"] == "France"
        assert event["amount"] > 0
        record = world.directed_sponsorships[0]
        assert record["payer"] == payer
        recipient_view = get_nation_intent(event["recipient"], world)
        assert recipient_view.against == "France"

    def test_one_new_patronage_per_turn(self, world):
        first = _process_ai_sponsorships(world)
        second = _process_ai_sponsorships(world)
        # A second call (same turn) may add at most one more, and never
        # duplicates an existing payer→recipient pair.
        assert len(first) == 1 and len(second) <= 1
        pairs = {(r["payer"], r["recipient"])
                 for r in world.directed_sponsorships}
        assert len(pairs) == len(world.directed_sponsorships)

    def test_poor_courts_do_not_sponsor(self, world):
        for nation in list(world.nation_gold):
            world.nation_gold[nation] = 100
        assert _process_ai_sponsorships(world) == []


# ═══════════════════════════════════════════════════════════════════════
# Pin 18 — deckless neutrality
# ═══════════════════════════════════════════════════════════════════════


class TestDecklessNeutral:
    def test_bare_world_intent_rung_is_silent(self):
        bare = WorldState(player_nation="France")
        for nation in list(bare.enemy_nations)[:5]:
            assert _generate_intent_ask(nation, bare, "PEACE", 0, 1.0) is None

    def test_bare_world_ai_ai_triggers_unchanged(self):
        bare = WorldState(player_nation="France")
        nations = list(bare.enemy_nations)
        # No wars, no threat, neutral relations → the legacy triggers
        # return None exactly as before AI-2.
        proposal = _evaluate_ai_ai_proposal(nations[0], nations[1], bare)
        assert proposal is None

    def test_bare_world_sponsorships_noop(self):
        bare = WorldState(player_nation="France")
        for nation in bare.enemy_nations:
            bare.nation_gold[nation] = 99999
        assert _process_ai_sponsorships(bare) == []

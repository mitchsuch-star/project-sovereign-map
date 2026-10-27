"""The October 27, 2026 enemy-AI sweep — the pins of batches 1–3.

Seven read-only audits over the enemy diplomacy AI (the coalition, the
intent ladder, the AI-to-AI paths, the proposal rungs, the courts' answers,
the other instruments) and the enemy military AI, each claim reproduced on
the 1805 boot before it was fixed. One class per seam; the row ids are the
sweep's (`docs/BUG_FIXES.md` §OCT27).
"""
import importlib.util
import json
from pathlib import Path

import pytest

from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(json.loads(json.dumps(world1805.to_dict(), default=str)))


def _dispatch_lines(world, dtype):
    return [e for e in (getattr(world, "pending_dispatch_events", None) or [])
            if e.get("type") == dtype]


# ════════════════════════════════════════════════════════════════════════
# Batch 1 — the coalition
# ════════════════════════════════════════════════════════════════════════


class TestCoalitionBatch:
    def test_c4_the_pivot_names_the_greater_danger(self, world):
        from backend.game_logic.coalition import _dissolution_reason_display
        assert _dissolution_reason_display("the_greater_danger", player="France") == \
            "Europe turns on France, the greater danger"
        assert _dissolution_reason_display("low_threat").startswith("Europe's alarm has fallen below")
        assert _dissolution_reason_display("some_new_reason") == "Some new reason"

    def test_c2_the_exhaustion_mark_rearms_after_a_full_band(self, world):
        from backend.game_logic.coalition import add_war_exhaustion_from_battle
        world.pending_dispatch_events = []
        world.war_exhaustion = {"Prussia": 0}
        world.we_dispatched_thresholds = {"Prussia": 20}      # told at 20 once, then the war ended
        add_war_exhaustion_from_battle("Prussia", 25000, world)   # +20 → 20 again
        assert [e["template_vars"]["threshold"]
                for e in _dispatch_lines(world, "diplomatic_we_threshold")] == [20]
        # the hysteresis: hovering under the mark re-crosses it silently
        world.pending_dispatch_events = []
        world.war_exhaustion = {"Austria": 15}
        world.we_dispatched_thresholds = {"Austria": 20}
        add_war_exhaustion_from_battle("Austria", 10000, world)   # 15 → 25
        assert _dispatch_lines(world, "diplomatic_we_threshold") == []

    def test_c1_a_lowered_gate_lowers_the_cancel_floor(self, world, monkeypatch):
        from backend.game_logic import coalition
        world.active_coalition = None
        world.coalition_cooldown = 0
        monkeypatch.setattr(coalition, "brewing_gate", lambda w, target=None: 40)
        monkeypatch.setattr(coalition, "get_qualifying_nations", lambda w, target=None: ["Austria"])
        world.threat_level = 35      # under the stock floor of 40, over the lowered gate's 20
        world.coalition_brewing = {"turns_remaining": 3, "started_turn": int(world.current_turn)}
        coalition.process_coalition_turn(world)
        assert world.coalition_brewing is not None, "the brew survives a tick of decay under a lowered gate"
        world.threat_level = 19
        coalition.process_coalition_turn(world)
        assert world.coalition_brewing is None, "the momentum rule still cancels under the lowered floor"

    def test_c3_the_successor_is_scored_against_the_leagues_own_target(self, world, monkeypatch):
        from backend.game_logic import coalition
        seen = {}

        def spy(members, w, target=None):
            seen["target"] = target
            return sorted(members)[0]
        monkeypatch.setattr(coalition, "select_coalition_leader", spy)
        world.active_coalition = {
            "name": "The League of the North", "target_nation": "Austria",
            "leader": "Prussia", "members": ["Prussia", "Sweden", "Denmark"],
            "formed_turn": 1, "strategic_posture": "contain",
        }
        coalition.remove_coalition_member("Prussia", world)
        assert seen.get("target") == "Austria"

    def test_c5_the_pivot_retires_the_eclipse_brew_card(self, world, monkeypatch):
        from backend.game_logic import coalition
        from backend.notifications import COALITION_BREWING
        world.active_coalition = None
        world.coalition_cooldown = 0
        world.coalition_brewing = {"target_nation": "Austria", "turns_remaining": 3}
        from backend.notifications import NotificationPriority, create_notification
        world.notifications.add(create_notification(
            COALITION_BREWING, NotificationPriority.CRITICAL,
            "Coalition Brewing Against Austria", "3 turns", int(world.current_turn)))
        monkeypatch.setattr(coalition, "brewing_gate", lambda w, target=None: 60)
        monkeypatch.setattr(coalition, "get_qualifying_nations", lambda w, target=None: ["Austria"])
        world.threat_level = 70        # France can coalesce → the pivot cancels the eclipse brew
        coalition.process_coalition_turn(world)
        titles = [n.get("title") for n in world.notifications.to_list()]
        assert "Coalition Brewing Against Austria" not in titles


# ════════════════════════════════════════════════════════════════════════
# Batch 1 — the AI-to-AI paths
# ════════════════════════════════════════════════════════════════════════


class TestAiAiBatch:
    def test_a1_the_return_tick_never_moves_the_players_province(self, world):
        from backend.game_logic.ai_diplomacy import process_province_returns
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(world, "France", "Spain", "ALLIANCE", "test")
        world.nation_relations[world._make_diplo_key("France", "Spain")] = 80
        world.regions["Morocco"].controller = "France"
        world.invalidate_active_nations_cache()
        events = process_province_returns(world)
        assert all(e.get("to") != "France" and e.get("from") != "France" for e in events)
        assert world.regions["Morocco"].controller == "France"

    def test_a2_a_closed_auction_rests_before_it_reopens(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as mod
        from backend.game_logic.intent import IntentView

        def crest(nation, w):
            if nation == "Denmark":
                return IntentView(nation=nation, want_id="d", want_title="T",
                                  want_type="acquire_regions", against="Austria",
                                  weight=66, price="bandwagon")
            return IntentView(nation=nation, want_id=None, want_title=None,
                              want_type=None, against=None, weight=0, price="indifferent")
        monkeypatch.setattr("backend.game_logic.intent.get_nation_intent", crest)
        world.allegiance_auctions = {}
        mod._announce_allegiance_close(world, "Denmark", "lapsed", None)
        assert world.ai_proposal_cooldowns["Denmark|allegiance_auction"] == mod.ALLEGIANCE_AUCTION_COOLDOWN_TURNS
        mod.process_allegiance_auctions(world)
        assert "Denmark" not in world.allegiance_auctions, "the court rests after a close"
        world.ai_proposal_cooldowns.pop("Denmark|allegiance_auction", None)
        mod.process_allegiance_auctions(world)
        assert "Denmark" in world.allegiance_auctions, "and is in play again when the rest is over"

    def test_a2_an_already_allied_winner_is_no_flip(self, world):
        from backend.game_logic import ai_diplomacy as mod
        world.pending_dispatch_events = []
        mod._announce_allegiance_close(world, "Denmark", "already_allied", "Britain")
        lines = [e["template_vars"]["line"] for e in _dispatch_lines(world, "allegiance_settled")]
        assert lines and "stays with Britain, whose pact she already holds" in lines[0]

    def test_a3_a_fallen_courts_auction_closes_its_notice(self, world):
        from backend.game_logic import ai_diplomacy as mod
        from backend.notifications import DIPLOMATIC_PROPOSAL, NotificationPriority, create_notification
        title = mod._allegiance_notice_title(world, "Atlantis")
        world.notifications.add(create_notification(
            DIPLOMATIC_PROPOSAL, NotificationPriority.HIGH, title, "in play", int(world.current_turn),
            details={"auction_court": "Atlantis"}))
        world.allegiance_auctions = {"Atlantis": {"opened_turn": 1, "resolves_turn": 4}}
        events = mod.process_allegiance_auctions(world)
        assert any(e.get("outcome") == "fallen" and e.get("nation") == "Atlantis" for e in events)
        assert "Atlantis" not in world.allegiance_auctions
        assert title not in [n.get("title") for n in world.notifications.to_list()]

    def test_a5_the_gold_bridge_prices_the_line_not_the_increment(self, world):
        from backend.game_logic.ai_diplomacy import _gold_bridge_counter, committed_gold_lump
        terms = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                 "sweeteners": [{"type": "gold_lump", "value": 1800}], "demands": [], "clauses": []}
        assert committed_gold_lump(terms) == 1800
        counter = _gold_bridge_counter(terms, world, accept_threshold=50,
                                       payer_nation="France", payer_gold=2000)
        if counter is not None:
            assert committed_gold_lump(counter) <= 2000
        assert _gold_bridge_counter(terms, world, accept_threshold=50,
                                    payer_nation="France", payer_gold=1850) is None

    def test_j1_a_balking_proposer_records_no_refusal(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as mod
        monkeypatch.setattr(mod, "_ai_ai_acceptance", lambda *a, **k: 10)
        out = mod._resolve_ai_ai_proposal(
            {"type": "non_aggression", "proposer": "Austria", "target": "Prussia"}, world)
        assert out is None
        assert mod.get_refused_asks(world, "Austria", "Prussia") == []

    def test_t6_a_recipients_refusal_rests_the_ordered_pair(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as mod
        monkeypatch.setattr(
            mod, "_ai_ai_acceptance",
            lambda scored, evaluator, other, w, **k: 60 if evaluator == "Austria" else 10)
        out = mod._resolve_ai_ai_proposal(
            {"type": "non_aggression", "proposer": "Austria", "target": "Prussia"}, world)
        assert out and out.get("type") == "ai_ai_proposal_refused"
        assert mod.get_refused_asks(world, "Austria", "Prussia")
        assert world.ai_proposal_cooldowns.get("Austria>Prussia|non_aggression", 0) == mod.TYPE_REJECTION_COOLDOWN
        assert mod._is_on_cooldown("Austria", "non_aggression", world, 0, recipient="Prussia")

    def test_a4_the_alignment_ask_yields_inside_the_dedupe_window(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as mod
        from backend.game_logic.intent import IntentView

        def aligned(nation, w):
            if nation == "Prussia":
                return IntentView(nation=nation, want_id="d", want_title="T",
                                  want_type="acquire_regions", against="Austria",
                                  weight=60, price="align")
            return IntentView(nation=nation, want_id=None, want_title=None,
                              want_type=None, against=None, weight=0, price="indifferent")
        monkeypatch.setattr("backend.game_logic.intent.get_nation_intent", aligned)
        world.threat_level = 0        # trigger 5 (both threatened by France) stays silent
        assert not world.is_at_war("Prussia", "France")
        # a target cold toward Austria, warm enough toward Prussia, no pact yet
        target = None
        for court in ("Saxony", "Hesse", "Denmark", "Sweden", "Hanover"):
            if court not in world.get_active_nations():
                continue
            world.nation_relations[world._make_diplo_key(court, "Austria")] = -20
            world.nation_relations[world._make_diplo_key("Prussia", court)] = 10
            if world.get_diplomatic_state("Prussia", court) in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
                continue
            first = mod._evaluate_ai_ai_proposal("Prussia", court, world)
            if first and first.get("type") == "defensive_alliance" and first.get("proposer") == "Prussia":
                target = court
                break
        assert target, "no court on the board took the alignment ask"
        mod.record_diplomatic_refusal(world, "Prussia", target, "defensive_alliance")
        second = mod._evaluate_ai_ai_proposal("Prussia", target, world)
        assert not (second and second.get("type") == "defensive_alliance"
                    and second.get("proposer") == "Prussia")


# ════════════════════════════════════════════════════════════════════════
# Batch 2 — the intent ladder and the guarantees
# ════════════════════════════════════════════════════════════════════════


class TestIntentLadderBatch:
    def test_d1_an_ally_is_never_the_obstacle(self, world):
        from backend.game_logic.agendas import get_agenda_covets, region_coveted
        from backend.game_logic.diplomacy import set_diplomatic_state
        from backend.game_logic.intent import get_nation_intent
        deck = [e for e in (world.agendas.get("Russia") or []) if e.get("id") == "gulf_and_straits"]
        assert deck, "the 1805 deck carries Russia's gulf_and_straits"
        world.agendas["Russia"] = deck
        set_diplomatic_state(world, "Russia", "Sweden", "ALLIANCE", "test")
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        assert not region_coveted(world, "Russia", "Finland")
        assert region_coveted(world, "Russia", "Rumelia")
        view = get_nation_intent("Russia", world)
        assert view.against != "Sweden"
        assert "Finland" not in get_agenda_covets("Russia", world)

    def test_d2_a_dead_or_client_guarantor_answers_for_nobody(self, world):
        from backend.game_logic.instruments import live_guarantees_of
        world.diplomatic_guarantees = [
            {"guarantor": "Atlantis", "protected": "Hanover", "turn": 1},
            {"guarantor": "Saxony", "protected": "Hanover", "turn": 1},
            {"guarantor": "Russia", "protected": "Hanover", "turn": 1},
        ]
        world.vassals = dict(world.vassals or {})
        world.vassals["Saxony"] = {"lord": "Prussia", "loyalty": 50}
        live = live_guarantees_of(world, "Hanover")
        assert [g["guarantor"] for g in live] == ["Russia"]

    def test_d2_the_council_never_marches_a_dead_guarantor(self, world):
        from backend.game_logic.war_council import _honour_guarantees
        world.diplomatic_guarantees = [{"guarantor": "Atlantis", "protected": "Hanover", "turn": 1}]
        events = []
        _honour_guarantees(world, "Prussia", "Hanover", "w1", events)
        assert events == []

    def test_d4_overtaken_is_not_satisfied(self, world):
        wd = _load("war_decision_pins", REPO / "tests" / "test_ai_intent_war_decision.py")
        from backend.game_logic.war_council import _CRISIS_CAUSE_COPY, _CRISIS_CAUSE_SHORT, process_war_council
        assert "overtaken" in _CRISIS_CAUSE_COPY and "overtaken" in _CRISIS_CAUSE_SHORT
        assert _CRISIS_CAUSE_COPY["overtaken"] != _CRISIS_CAUSE_COPY["satisfied"]
        wd._arm_prussia_crisis(world)
        process_war_council(world)
        assert "Prussia" in world.war_intents
        # France takes Hanover: the obstacle changes, the want is NOT won
        world.regions["Hanover"].controller = "France"
        world.invalidate_active_nations_cache()
        events = wd._poll_next_turn(world)
        passed = [e for e in events if e["type"] == "crisis_passed"]
        assert passed and passed[0]["cause"] == "overtaken", passed

    def test_d5_the_stall_counts_consecutive_refusals_only(self, world, monkeypatch):
        wd = _load("war_decision_pins", REPO / "tests" / "test_ai_intent_war_decision.py")
        from backend.game_logic import war_council
        wd._arm_prussia_crisis(world)
        war_council.process_war_council(world)
        assert "Prussia" in world.war_intents
        real = war_council.can_declare_war
        state = {"refuse": True}

        def gate(w, a, t, *args, **kwargs):
            if a == "Prussia" and state["refuse"]:
                return {"ok": False, "reason": "side_conflict", "message": "x"}
            return real(w, a, t, *args, **kwargs)
        monkeypatch.setattr(war_council, "can_declare_war", gate)
        for _ in range(war_council.CRISIS_HARD_STALL_TURNS - 1):   # three refused polls
            wd._poll_next_turn(world)
        assert "Prussia" in world.war_intents
        state["refuse"] = False
        wd._poll_next_turn(world)        # one clean poll clears the run
        assert "stall_turns" not in world.war_intents.get("Prussia", {"stall_turns": 0}) \
            or int(world.war_intents["Prussia"].get("stall_turns", 0)) == 0

    def test_d6_a_refusal_flushes_the_intent_cache(self, world):
        from backend.game_logic.ai_diplomacy import record_diplomatic_refusal
        from backend.game_logic.intent import get_nation_intent
        get_nation_intent("Prussia", world)
        assert getattr(world, "_intent_cache", None) is not None
        assert record_diplomatic_refusal(world, "Prussia", "Hanover", "design_ask")
        assert getattr(world, "_intent_cache", None) is None

    def test_d8_the_frontier_cache_flushes_with_its_siblings(self, world):
        from backend.game_logic.war_council import get_intent_frontier
        get_intent_frontier(world, "Prussia")
        assert getattr(world, "_intent_frontier_cache", None) is not None
        world.invalidate_bloc_members_cache()
        assert getattr(world, "_intent_frontier_cache", None) is None


# ════════════════════════════════════════════════════════════════════════
# Batch 2 — the player's roads
# ════════════════════════════════════════════════════════════════════════


class TestPlayersRoadsBatch:
    def test_send_override_asks_the_table_first(self, world):
        from backend.commands.executor import CommandExecutor
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {"France": DiplomaticRepresentative("Talleyrand", "France", "schemer", skill=10)}
        world.diplomatic_points = 10
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"
        world.nation_relations[key] = -30          # an alliance needs 40
        world.dialogue_manager.replace({
            "type": "proposal_confirm", "target_nation": "Prussia",
            "options": [{"label": "Send my terms", "action": "send_override",
                         "terms": {"proposal_type": "alliance"}}],
            "context": {"original_proposal": {"proposal_type": "alliance"},
                        "suggested_terms": {"proposal_type": "alliance"}},
        })
        result = CommandExecutor().handle_diplomatic_dialogue_response("send", {"world": world})
        assert result["success"] is False
        assert result.get("clause") == "relation_floor"
        assert world.diplomatic_points == 10, "refused free"
        assert getattr(world, "proposal_in_transit", None) is None

    def test_the_ratifier_reads_a_demands_direction_by_either_spelling(self, world):
        from backend.game_logic.treaty import treaty_clauses_of
        clauses = treaty_clauses_of({
            "type": "peace", "sweeteners": [],
            "demands": [{"type": "territory_cede", "from": "France", "to": "Prussia",
                         "regions": ["Belgium"]}],
        }, "France", "Prussia")
        assert clauses and clauses[0]["from"] == "France" and clauses[0]["to"] == "Prussia"
        clauses = treaty_clauses_of({
            "type": "peace", "sweeteners": [],
            "demands": [{"type": "territory_cede", "from_nation": "France", "to_nation": "Prussia",
                         "regions": ["Belgium"]}],
        }, "France", "Prussia")
        assert clauses[0]["from"] == "France" and clauses[0]["to"] == "Prussia"


# ════════════════════════════════════════════════════════════════════════
# Batch 2b — the proposal rungs and the other instruments
# ════════════════════════════════════════════════════════════════════════


class TestProposalRungsBatch:
    def test_t1_a_refused_pact_never_claims_the_turns_slot(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as mod
        key = world._make_diplo_key("France", "Denmark")
        world.diplomatic_states[key] = "PEACE"
        world.nation_relations[key] = -30
        assert mod.treaty_offer_refusal(world, "Denmark", "non_aggression", "France")
        monkeypatch.setattr(mod, "_count_nations_at_war_with_france", lambda w: 3)
        proposal = mod.process_diplomatic_phase("Denmark", world)
        assert proposal is None or proposal.get("proposal_type") != "opportunistic"

    def test_t3_the_readiness_letter_is_p1s_own_choice(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as mod
        monkeypatch.setattr(mod, "get_war_score_for", lambda w, a, b: -55)
        monkeypatch.setattr(mod, "effective_peace_threshold", lambda n, o, w: -40)
        monkeypatch.setattr(mod, "_hope_alive", lambda w, c, o: False)
        assert mod.court_own_readiness(world, "Austria", "France")["letter"] == "peace"
        monkeypatch.setattr(mod, "_hope_alive", lambda w, c, o: True)
        assert mod.court_own_readiness(world, "Austria", "France")["letter"] == "truce"
        monkeypatch.setattr(mod, "get_war_score_for", lambda w, a, b: -75)
        assert mod.court_own_readiness(world, "Austria", "France")["letter"] == "peace"

    def test_t4_a_refusal_never_shortens_a_standing_cooldown(self, world):
        from backend.game_logic.ai_diplomacy import apply_rejection_cooldowns
        world.ai_proposal_cooldowns = {"Prussia|offer_vassalage": 12}
        apply_rejection_cooldowns("Prussia", "offer_vassalage", world)
        assert world.ai_proposal_cooldowns["Prussia|offer_vassalage"] == 12

    def test_t4_the_governor_reads_prior_turns_and_only_the_courts_own_asks(self, world):
        from backend.game_logic.ai_diplomacy import apply_rejection_cooldowns, prior_refusals_of
        world.current_turn = 20
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"
        world.diplomatic_refusals = {"Prussia>France": [{"type": "open_borders", "turn": 20}]}
        assert prior_refusals_of(world, "Prussia", "France", "open_borders") == 0, "this turn's is not prior"
        world.diplomatic_refusals = {"Prussia>France": [{"type": "open_borders", "turn": 12}]}
        apply_rejection_cooldowns("Prussia", "open_borders", world, escalate=False)
        assert world.ai_proposal_cooldowns["Prussia|open_borders"] == 6, "the AI-refuses-France callers do not escalate"

    def test_t7_the_merge_keeps_the_letters_and_the_sureties(self):
        from backend.game_logic.settlement_helpers import _merge_instance_data
        survivor = {"war_id": "a", "attackers": ["Prussia"], "defenders": ["Hanover"],
                    "offer_history": [{"tier": 1}]}
        absorbed = {"war_id": "b", "attackers": ["Prussia"], "defenders": ["Denmark"],
                    "offer_history": [{"tier": 2}], "truce_sureties": {"Prussia|Hanover": ["Brunswick"]}}
        _merge_instance_data(survivor, absorbed)
        assert survivor["offer_history"] == [{"tier": 1}, {"tier": 2}]
        assert survivor["truce_sureties"] == {"Prussia|Hanover": ["Brunswick"]}

    def test_t5_the_letter_names_the_formed_court(self, world):
        from backend.game_logic.ai_diplomacy import _build_proposal_terms, _make_proposal, build_ai_proposal_dialogue
        from backend.game_logic.formations import formed_display_name
        shown = formed_display_name(world, "PapalStates")
        terms = _build_proposal_terms("PapalStates", "open_borders", 0, world)
        dialogue = build_ai_proposal_dialogue(_make_proposal("PapalStates", "open_borders", 3, terms, world), world)
        assert "from the Papal States:" in dialogue["talleyrand_text"]
        assert all("PapalStates" not in str(o.get("description")) for o in dialogue["options"])
        assert shown == "Papal States"


class TestOtherInstrumentsBatch:
    def test_i3_the_bonds_exhaustion_depth_keeps_both_exits_reachable(self):
        from backend.game_logic.ai_diplomacy import BREAK_RANKS_EXHAUSTION
        from backend.game_logic.bond import depth_for_strength
        from backend.game_logic.coalition import WAR_EXHAUSTION_MAX
        from backend.game_logic.settlement_third_party import PAIR_EXIT_WE_FLOOR
        # `points` are the bond's loyalty points (10 exhaustion a point): the
        # 200g tier reads 6 points, the 300g 9, the 400g 12. The P1 line
        # (`we > 80 + depth`) stays under the cap; the pair-exit floor is
        # capped at its own site (`settlement_third_party`).
        for points in (6, 9, 12, 100):
            d = depth_for_strength(points)["exhaustion"]
            assert BREAK_RANKS_EXHAUSTION + d <= WAR_EXHAUSTION_MAX - 1
        assert PAIR_EXIT_WE_FLOOR < WAR_EXHAUSTION_MAX
        assert depth_for_strength(6)["exhaustion"] == 60      # the 200g tier is untouched
        assert depth_for_strength(9)["exhaustion"] == 90      # the 300g tier is untouched
        assert depth_for_strength(12)["exhaustion"] == 119    # the 400g tier, one short of the cap
        from backend.game_logic.settlement_third_party import bonded_exit_floor
        world = WorldState.from_scenario(str(SCENARIO_PATH))
        assert bonded_exit_floor(world, "Austria", "Russia", PAIR_EXIT_WE_FLOOR) == PAIR_EXIT_WE_FLOOR  # no bond: the stock floor
        world.directed_sponsorships = [{"kind": "bond", "payer": "Britain", "recipient": "Austria",
                                        "aim": "France", "amount_per_turn": 400, "turns_remaining": 10,
                                        "started_turn": 1, "expiry_turn": 11}]
        assert bonded_exit_floor(world, "Austria", "France", PAIR_EXIT_WE_FLOOR) <= WAR_EXHAUSTION_MAX  # never past the cap

    def test_i2_a_war_france_has_joined_is_frances_to_end(self, world):
        from backend.game_logic.diplomacy import declare_war
        from backend.game_logic.settlement_third_party import attempt_third_party_settlement
        declare_war(world, "Prussia", "Hanover")
        war_id, war = next(((wid, w) for wid, w in world.war_instances.items()
                            if w.get("ended_turn") is None
                            and {"Prussia", "Hanover"} <= set(w.get("active_participants") or [])), (None, None))
        assert war_id
        war["active_participants"] = list(war.get("active_participants") or []) + ["France"]
        assert attempt_third_party_settlement(world, war_id, war, force=True, broker="France") is None

    def test_i1_the_third_party_peace_announces_what_was_applied(self, world):
        from backend.game_logic.diplomacy import declare_war
        from backend.game_logic.settlement_third_party import (
            THIRD_PARTY_MIN_WAR_TURNS,
            attempt_third_party_settlement,
        )
        declare_war(world, "Prussia", "Hanover")
        war_id, war = next(((wid, w) for wid, w in world.war_instances.items()
                            if w.get("ended_turn") is None
                            and {"Prussia", "Hanover"} <= set(w.get("active_participants") or [])), (None, None))
        war["created_turn"] = int(world.current_turn) - THIRD_PARTY_MIN_WAR_TURNS - 1
        world.war_exhaustion["Hanover"] = 120
        key = world._make_diplo_key("Hanover", "Prussia")
        world.war_scores[key] = -60 if key.startswith("Hanover") else 60
        world.nation_gold["Hanover"] = 120
        event = attempt_third_party_settlement(world, war_id, war, force=True)
        assert event is not None
        gold = [t for t in event["terms"] if t.get("type") == "gold_indemnity"]
        if gold:
            assert int(gold[0].get("amount", 0)) <= 120
            assert "120" in event["message"] or "pays" not in event["message"]
        assert "4,800" not in event["message"]

    def test_i4_a_relenting_court_is_unwarned(self, world, monkeypatch):
        from backend.game_logic import congress
        c = congress._store(world)
        c["warned"] = ["Prussia"]
        c["warned_turn"] = {"Prussia": 1}
        c["answers"] = {"Prussia": {"stance": congress.REFUSES, "by": "formula", "refusing_since": 1}}
        monkeypatch.setattr(congress, "great_powers", lambda w: ["Prussia"])
        monkeypatch.setattr(congress, "answer",
                            lambda w, court, overrides=None: {"stance": congress.RECOGNIZES, "by": "formula"})
        congress._take_answers(world)
        assert "Prussia" not in (c.get("warned") or [])
        assert "Prussia" not in (c.get("warned_turn") or {})

    def test_i5_the_broken_bargain_names_the_court(self, world):
        from backend.game_logic.instruments import _emit_broken_bargain_beat
        _emit_broken_bargain_beat(world, breaker="KingdomOfItaly", victim="France",
                                  event={"type": "bargain_reneged", "turn": 3})
        titles = [n.get("title") for n in world.notifications.to_list()]
        assert "A bargain broken by Kingdom of Italy" in titles


# ════════════════════════════════════════════════════════════════════════
# Batch 3 — the enemy military AI
# ════════════════════════════════════════════════════════════════════════


def _ai():
    from backend.ai.enemy_ai import EnemyAI
    from backend.commands.executor import CommandExecutor
    return EnemyAI(CommandExecutor())


class TestEnemyGeneralsBatch:
    def test_e1_a_liberation_never_breaks_a_truce(self, world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        ai = _ai()
        mack = world.marshals["Mack"]
        mack.location = "Swabia"
        world.regions["Munich"].controller = "France"
        world.invalidate_active_nations_cache()
        for m in list(world.marshals.values()):
            if m.location == "Munich":
                m.location = "Paris"
        world._build_marshal_index()
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives = {key: {"Austria": {
            "type": "liberation", "target_regions": ["Munich"],
            "target_nation": "France", "concluded_turn": None}}}
        assert world.is_at_war("Austria", "France")
        at_war = ai._find_liberation_target(mack, "Austria", world)
        assert at_war and at_war["action"] == "attack" and at_war["target"] == "Munich"
        set_diplomatic_state(world, "Austria", "France", "ARMISTICE", "test")
        assert ai._find_liberation_target(mack, "Austria", world) is None

    def test_e2_a_fortified_corps_never_unfortifies_for_barred_water(self, world, monkeypatch):
        ai = _ai()
        from backend.game_logic import naval
        monkeypatch.setattr(naval, "crossing_allowed", lambda w, n, o, d: False)
        moore = next(m for m in world.marshals.values() if m.nation == "Britain")
        moore.location = "London"
        moore.fortified = True
        for m in list(world.marshals.values()):
            if m.location == "Normandy":
                m.location = "Paris"
        world._build_marshal_index()
        assert world.is_at_war("Britain", "France")
        assert ai._check_fortification_opportunity(moore, "Britain", world) is None
        assert "Moore" not in ai._pending_intents and moore.name not in ai._pending_intents

    def test_e5_a_league_fellow_is_never_engaged(self, world):
        ai = _ai()
        from backend.game_logic.diplomacy import set_diplomatic_state
        world.active_coalition = {"name": "The Third Coalition", "target_nation": "France",
                                  "leader": "Britain", "members": ["Britain", "Prussia", "Austria"],
                                  "formed_turn": 1}
        set_diplomatic_state(world, "Britain", "Prussia", "WAR", "test")
        brit = next(m for m in world.marshals.values() if m.nation == "Britain")
        prus = next(m for m in world.marshals.values() if m.nation == "Prussia")
        prus.location = brit.location
        world._build_marshal_index()
        assert ai._engageable_enemies(brit, [prus], "Britain", world) == []

    def test_e7_a_fortified_corps_waits_out_its_recovery(self, world):
        ai = _ai()
        mack = world.marshals["Mack"]
        mack.fortified = True
        mack.retreat_recovery = 2
        action = ai._get_recovery_action(mack, world, "Austria")
        assert action == {"marshal": "Mack", "action": "wait"}

    def test_e10_artillery_still_setting_up_takes_no_walk_in(self, world):
        ai = _ai()
        mack = world.marshals["Mack"]
        mack.artillery = True
        mack.moved_this_turn = True
        assert ai._find_undefended_capture(mack, "Austria", world) is None

    def test_e12_the_survival_action_reads_the_defend_predicate(self, world):
        from backend.models.marshal import Stance
        ai = _ai()
        mack = world.marshals["Mack"]
        mack.location = "Vienna"
        mack.fortified = True
        mack.stance = Stance.DEFENSIVE
        mack.starting_strength = 100000
        mack.strength = 10000
        for m in list(world.marshals.values()):
            if m.nation != "Austria" and m.location in (world.regions["Vienna"].adjacent_regions or []):
                m.location = "Paris"
        world._build_marshal_index()
        action = ai._get_survival_action(mack, "Austria", world)
        assert action and action["action"] in ("wait", "retreat", "unfortify")
        assert action["action"] != "defend"

    def test_e6_reckless_cavalry_takes_an_empty_province(self, world):
        from backend.commands.executor import CommandExecutor
        murat = world.marshals["Murat"]
        murat.is_cavalry = True
        murat.personality = "aggressive"
        murat.recklessness = 3
        assert murat.is_reckless_cavalry
        world.regions["Munich"].controller = "Austria"
        world.regions["Munich"].garrison_strength = 0      # an EMPTY province, not an assault
        world.invalidate_active_nations_cache()
        for m in list(world.marshals.values()):
            if m.location == "Munich":
                m.location = "Vienna"
        world._build_marshal_index()
        world.actions_remaining = 4
        result = CommandExecutor().execute(
            {"command": {"action": "attack", "marshal": "Murat", "target": "Munich"}},
            {"world": world})
        assert result.get("success"), result.get("message")
        # taken - and, Munich being Bavaria's capital and Bavaria France's
        # ally, handed back at once (S14G-D1's liberation): never Austria's.
        assert world.regions["Munich"].controller in ("France", "Bavaria")

    def test_e4_the_ai_never_orders_more_than_its_budget(self, world, monkeypatch):
        """The loop's own gate: an order costing 2 is skipped at 1 action left
        (read through the paid-action predicate and `get_action_cost`)."""
        ai = _ai()
        assert ai._action_costs_point("garrison")
        assert world.get_action_cost("garrison") == 2
        assert ai._order_affordable(world, "garrison", 1) is False     # "Need 2, have 1"
        assert ai._order_affordable(world, "garrison", 2) is True
        assert ai._order_affordable(world, "wait", 0) is True           # a free order always

    def test_e15_the_stagnation_breaker_never_walks_away_from_its_target(self, world, monkeypatch):
        """OCT27-51: the breaker marches a corps TOWARD its nearest enemy; a
        corps already beside him (no nearer step) repositions along the front
        or not at all. Deroy at Munich with the Austrians in Tyrol: Franconia
        and Milan keep Tyrol one march off, Swabia and Franche-Comte are two.
        Killed by: the random walk back (the seam held down reaches a
        two-march province on some draw)."""
        import random
        from backend.ai.enemy_ai import EnemyAI
        ai = _ai()
        deroy = world.marshals["Deroy"]
        deroy.location = "Munich"
        deroy.fortified = False
        world.marshals["ArchdukeCharles"].location = "Tyrol"
        world.marshals["Mack"].location = "Vienna"
        world._build_marshal_index()
        assert world.is_at_war("Bavaria", "Austria")
        assert ai._stagnation_fallback_dests(
            world, "Munich", "Tyrol", ["Franconia", "Swabia", "Franche-Comte", "Milan"]) == ["Franconia", "Milan"]

        def moves(fresh):
            out = set()
            for seed in range(24):
                random.seed(seed)
                action = fresh()._get_stagnation_action(deroy, "Bavaria", world, 2, "literal")
                if action and action.get("action") == "move":
                    out.add(action["target"])
            return out

        live = moves(_ai)
        assert live and all(world.get_distance(dest, "Tyrol") <= 1 for dest in live), live
        with monkeypatch.context() as held:
            held.setattr(EnemyAI, "_stagnation_fallback_dests", lambda self, w, o, t, d: list(d))
            down = moves(_ai)
        assert any(world.get_distance(dest, "Tyrol") > 1 for dest in down), down
        # nothing lateral: the breaker falls through to its wait, never a walk
        monkeypatch.setattr(EnemyAI, "_stagnation_fallback_dests", lambda self, w, o, t, d: [])
        assert _ai()._get_stagnation_action(deroy, "Bavaria", world, 2, "literal") == {
            "marshal": "Deroy", "action": "wait"}

    def test_e15b_the_cautious_advances_fallback_keeps_contact_too(self, world, monkeypatch):
        """OCT27-51's sibling (Rule 10): the cautious advance's stagnation
        fallback (P7, an unthreatened cautious corps with no nearer step)
        took the FIRST safe neighbour in adjacency order, which may lead
        away. Deroy at Munich, the Austrians' nearest corps in Carniola two
        marches off: Franconia keeps Carniola two off, Swabia is three; with
        Swabia listed first the old pick walks away.
        Killed by: the first-pick walk back (the seam held down)."""
        from backend.ai.enemy_ai import EnemyAI
        deroy = world.marshals["Deroy"]
        deroy.location = "Munich"
        deroy.fortified = False
        deroy.artillery = False
        world.marshals["ArchdukeCharles"].location = "Carniola"
        world.marshals["ArchdukeJohn"].location = "Galicia"
        world.marshals["Mack"].location = "Galicia"
        for m in list(world.marshals.values()):
            if m.location == "Munich" and m.name != "Deroy":
                m.location = "Paris"
        world.regions["Munich"].adjacent_regions = ["Swabia", "Franconia", "Tyrol", "Franche-Comte", "Milan"]
        world._build_marshal_index()
        world.ai_stagnation_turns["Deroy"] = 2
        monkeypatch.setattr(EnemyAI, "_get_effective_personality", lambda self, m, w: "cautious")
        monkeypatch.setattr(EnemyAI, "_march_plan", lambda self, w, n, m, t: [lambda region: 9])
        assert world.get_distance("Franconia", "Carniola") == world.get_distance("Munich", "Carniola") == 2
        assert world.get_distance("Swabia", "Carniola") == 3
        action = _ai()._consider_strategic_move(deroy, "Bavaria", world)
        assert action == {"marshal": "Deroy", "action": "move", "target": "Franconia"}, action
        with monkeypatch.context() as held:
            held.setattr(EnemyAI, "_stagnation_fallback_dests", lambda self, w, o, t, d: list(d))
            down = _ai()._consider_strategic_move(deroy, "Bavaria", world)
        assert down == {"marshal": "Deroy", "action": "move", "target": "Swabia"}, down


# ════════════════════════════════════════════════════════════════════════
# S14i — the sweep's rulings, OCT27-D1 … D13 (the user, October 27, 2026:
# "Take OCT27-D1 … D13 as recommended under the standing delegation; S14i
# builds them before S15."). One class per row; each holds its seam down to
# show the pin kills the build.
# ════════════════════════════════════════════════════════════════════════

def _league(world, target, members, leader=None):
    world.active_coalition = {"name": "The League", "target_nation": target,
                              "leader": leader or members[0], "members": list(members),
                              "formed_turn": int(world.current_turn)}


def _state(world, a, b, state):
    import contextlib
    import io
    from backend.game_logic.diplomacy import set_diplomatic_state
    with contextlib.redirect_stdout(io.StringIO()):
        set_diplomatic_state(world, a, b, state, "test")


class TestOCT27D1:
    """The league frays to the edge, never over it by clockwork."""

    def test_friction_stops_at_the_last_uncounted_relation(self, world, monkeypatch):
        from backend.game_logic import coalition as CO
        from backend.game_logic.diplomacy import (AUTO_DOWNGRADE_GAP, STATE_RELATION_THRESHOLDS,
                                                  check_auto_downgrade)
        _league(world, "France", ["Austria", "Russia"])
        assert world.get_diplomatic_state("Austria", "Russia") == "ALLIANCE"
        floor = STATE_RELATION_THRESHOLDS["ALLIANCE"] - AUTO_DOWNGRADE_GAP + 1
        key = world._make_diplo_key("Austria", "Russia")
        world.nation_relations[key] = floor + 1
        CO.apply_coalition_friction(world)
        assert world.nation_relations[key] == floor
        CO.apply_coalition_friction(world)
        assert world.nation_relations[key] == floor          # the edge, not over it
        world.turns_below_threshold = {}
        check_auto_downgrade(world)
        assert world.turns_below_threshold.get(key, 0) == 0  # the run never starts
        world.nation_relations[key] = floor - 7              # a real wound
        CO.apply_coalition_friction(world)
        assert world.nation_relations[key] == floor - 7      # friction adds nothing
        monkeypatch.setattr(CO, "coalition_friction_floor", lambda *a, **k: None)
        world.nation_relations[key] = floor + 1
        CO.apply_coalition_friction(world)
        assert world.nation_relations[key] == floor - 1      # down: the clockwork


class TestOCT27D2:
    """The same statecraft for every league."""

    def test_the_league_target_and_the_loyalty_read(self, world, monkeypatch):
        from backend.game_logic import coalition as CO
        from backend.game_logic.ai_diplomacy import court_own_readiness, p2_league_gate
        assert CO.league_target(world) == "France"           # no league: the player
        _league(world, "Austria", ["Prussia", "Denmark"])
        _state(world, "Prussia", "Austria", "WAR")
        assert CO.league_target(world) == "Austria"
        ready = court_own_readiness(world, "Prussia", "Austria")
        assert ready["in_league"] and ready["loyal"], ready
        assert not court_own_readiness(world, "Prussia", "France")["in_league"]
        _state(world, "Prussia", "France", "WAR")
        # the eclipse league gates the war it was formed for, not France's
        assert not p2_league_gate(world, "Prussia", war_score=0,
                                  diplo_key=world._make_diplo_key("Prussia", "France"))
        assert p2_league_gate(world, "Prussia", war_score=0,
                              diplo_key=world._make_diplo_key("Prussia", "Austria"))
        monkeypatch.setattr(CO, "league_target", lambda w: w.player_nation)
        assert p2_league_gate(world, "Prussia", war_score=0,
                              diplo_key=world._make_diplo_key("Prussia", "France"))

    def test_an_eclipse_league_dissolves_without_a_cooldown_on_france(self, world):
        from backend.game_logic import coalition as CO
        _league(world, "Austria", ["Prussia", "Denmark"])
        world.coalition_cooldown = 0
        CO.dissolve_coalition(world, "low_threat")
        assert world.coalition_cooldown == 0
        _league(world, "France", ["Austria", "Russia"])
        CO.dissolve_coalition(world, "low_threat")
        assert world.coalition_cooldown == CO.COALITION_COOLDOWN_TURNS

    def test_the_member_holds_the_table_until_spent(self, world, monkeypatch):
        from backend.game_logic import settlement_third_party as STP
        _league(world, "Austria", ["Prussia", "Denmark"])
        _state(world, "Prussia", "Austria", "WAR")
        assert STP.eclipse_league_holds(world, "Prussia", "Austria", -20)
        assert not STP.eclipse_league_holds(world, "Prussia", "Austria", -60)  # spent: breaks ranks
        assert not STP.eclipse_league_holds(world, "Austria", "Prussia", -20)  # the target sues freely
        world.war_exhaustion["Prussia"] = 90
        assert not STP.eclipse_league_holds(world, "Prussia", "Austria", -20)  # exhausted: breaks ranks
        _league(world, "France", ["Prussia", "Denmark"])
        world.war_exhaustion["Prussia"] = 0
        assert not STP.eclipse_league_holds(world, "Prussia", "Austria", -20)  # France's league: not this war

    def test_the_bond_against_the_leagues_target_binds_her(self, world, monkeypatch):
        from backend.game_logic import coalition as CO
        from backend.game_logic.ai_diplomacy import break_ranks_lines
        _league(world, "Austria", ["Prussia", "Denmark"])
        _state(world, "Prussia", "Austria", "WAR")
        _state(world, "Denmark", "Austria", "WAR")
        world.directed_sponsorships = [{"kind": "bond", "payer": "Denmark", "recipient": "Prussia",
                                        "aim": "Austria", "amount_per_turn": 400,
                                        "turns_remaining": 10, "started_turn": 1,
                                        "expiry_turn": 11}]
        deep = break_ranks_lines(world, "Prussia")
        assert deep["bond"] == "Denmark" and deep["exhaustion"] > 80, deep
        monkeypatch.setattr(CO, "league_target", lambda w: w.player_nation)
        assert break_ranks_lines(world, "Prussia")["exhaustion"] == 80   # down: France's bond only


class TestOCT27D3:
    """The shelter rungs read the court's own hegemon."""

    def test_the_menace_is_the_largest_slot_among_the_disliked(self, world):
        from backend.game_logic.ai_diplomacy import menace_for
        assert menace_for(world, "Austria") == int(world.threat_level)   # 1805: France leads
        world.threat_by_target["Austria"] = int(world.threat_level) + 20
        world.nation_relations[world._make_diplo_key("Denmark", "Austria")] = -15
        assert menace_for(world, "Denmark") == int(world.threat_level) + 20
        world.nation_relations[world._make_diplo_key("Denmark", "Austria")] = 10
        assert menace_for(world, "Denmark") == int(world.threat_level)   # warm to Austria: France's

    def test_two_courts_cold_to_austria_find_each_other(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as AD
        world.threat_by_target["Austria"] = 75
        for court in ("Denmark", "Sweden"):
            world.nation_relations[world._make_diplo_key(court, "Austria")] = -20
            _state(world, court, "Austria", "PEACE")
        world.nation_relations[world._make_diplo_key("Denmark", "Sweden")] = 5
        assert AD.eclipse_menace_shared(world, "Denmark", "Sweden") == "Austria"
        _state(world, "Denmark", "Austria", "NON_AGGRESSION")
        assert AD.eclipse_menace_shared(world, "Denmark", "Sweden") is None   # a pact with her
        monkeypatch.setattr(AD, "eclipse_menace_shared", lambda *a, **k: None)
        assert AD.eclipse_menace_shared(world, "Denmark", "Sweden") is None


class TestOCT27D4:
    """Two courts both cold to the hegemon find each other."""

    def test_the_shared_menace_term(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as AD
        world.threat_level = 70
        for court in ("Denmark", "Sweden"):
            world.nation_relations[world._make_diplo_key(court, "France")] = -10
        assert AD.shared_menace_bonus(world, "Denmark", "Sweden", "defensive_alliance") == 25
        assert AD.shared_menace_bonus(world, "Denmark", "Sweden", "non_aggression") == 25
        assert AD.shared_menace_bonus(world, "Denmark", "Sweden", "alliance") == 0
        # neighbours only: Portugal is as cold to France and shares no border
        world.nation_relations[world._make_diplo_key("Portugal", "France")] = -10
        assert "Portugal" not in world.get_neighbouring_nations("Denmark")
        assert AD.shared_menace_bonus(world, "Denmark", "Portugal", "defensive_alliance") == 0
        world.threat_level = 50
        assert AD.shared_menace_bonus(world, "Denmark", "Sweden", "defensive_alliance") == 10
        world.nation_relations[world._make_diplo_key("Sweden", "France")] = 5
        assert AD.shared_menace_bonus(world, "Denmark", "Sweden", "defensive_alliance") == 0
        world.nation_relations[world._make_diplo_key("Sweden", "France")] = -10
        live = AD._ai_ai_acceptance({"type": "defensive_alliance"}, "Denmark", "Sweden", world)
        monkeypatch.setattr(AD, "shared_menace_bonus", lambda *a, **k: 0)
        down = AD._ai_ai_acceptance({"type": "defensive_alliance"}, "Denmark", "Sweden", world)
        assert live - down == 10


class TestOCT27D5:
    """No second purse for one aim, no round trip, a rivalry that rests."""

    def test_the_sponsorship_dedupe_reads_bonds_and_round_trips(self, world):
        from backend.game_logic.instruments import sponsorship_redundant
        world.directed_sponsorships = [{"kind": "bond", "payer": "Britain", "recipient": "Russia",
                                        "aim": "France", "amount_per_turn": 500}]
        assert sponsorship_redundant(world, "Britain", "Russia", "France")
        assert not sponsorship_redundant(world, "Britain", "Russia", "Prussia")
        assert sponsorship_redundant(world, "Russia", "Britain", "France")    # the round trip
        world.directed_sponsorships = [{"kind": "sponsorship", "payer": "Britain",
                                        "recipient": "Austria", "aim": "Prussia",
                                        "amount_per_turn": 300}]
        assert sponsorship_redundant(world, "Britain", "Austria", "France")   # the old read
        world.directed_sponsorships = [{"kind": "sponsorship", "payer": "Britain",
                                        "recipient": "Austria", "aim": "Prussia",
                                        "amount_per_turn": 0}]                # a licence
        assert not sponsorship_redundant(world, "Britain", "Austria", "France")

    def test_the_rivalry_rests_after_each_step(self, world):
        from backend.game_logic import ai_diplomacy as AD
        assert AD.rivalry_step_allowed(world, "Spain", "Portugal")
        AD.note_rivalry_step(world, "Spain", "Portugal")
        assert not AD.rivalry_step_allowed(world, "Portugal", "Spain")
        key = f"ai_ai|{world._make_diplo_key('Spain', 'Portugal')}"
        assert world.ai_proposal_cooldowns[key] == AD.RIVALRY_STEP_COOLDOWN == 5


class TestOCT27D6:
    """The reserve priced for the war, no brand for the lawless, an honest deterrent."""

    def test_the_target_and_its_guarantors_leave_the_reserve(self, world):
        from backend.game_logic.instruments import pledge_guarantee
        from backend.game_logic.war_council import exposure_against, get_exposure_view
        assert get_exposure_view(world, "Prussia")["worst_threat"] == "Russia"
        pledge_guarantee(world, guarantor="Russia", protected="Hanover")
        world.invalidate_bloc_members_cache()
        priced = exposure_against(world, "Prussia", "Hanover")
        assert priced["worst_threat"] == "Bavaria" and priced["reserve"] < get_exposure_view(
            world, "Prussia")["reserve"]
        assert exposure_against(world, "Prussia", "Russia")["worst_threat"] == "Bavaria"

    def test_a_guarantor_that_cannot_join_is_voided_never_branded(self, world, monkeypatch):
        from backend.game_logic import instruments as IN
        IN.pledge_guarantee(world, guarantor="Russia", protected="Hanover")
        _state(world, "Prussia", "Hanover", "WAR")
        world.armistice_cooldowns = {world._make_diplo_key("Russia", "Prussia"): 4}
        assert IN.guarantee_join_refusal(world, "Russia", "Prussia") == "armistice_cooldown"
        events = IN.honour_guarantees(world, "Prussia", "Hanover")
        assert [e["reason"] for e in events] == ["cannot_join"], events
        assert not any(g.get("guarantor") == "Russia" for g in world.diplomatic_guarantees)
        world.current_turn += 5
        tick = IN.process_instruments(world)
        assert not any(e.get("type") == "guarantee_abandoned" for e in tick), tick
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner(events[0])
        assert "cannot lawfully march on Prussia for Hanover" in line, line

    def test_deterred_is_credited_only_when_the_pledge_moved_the_rung(self, world):
        from types import SimpleNamespace
        from backend.game_logic.instruments import pledge_guarantee
        from backend.game_logic.war_council import guarantee_deterred
        pledge_guarantee(world, guarantor="Russia", protected="Hanover")
        assert guarantee_deterred(world, "Prussia", SimpleNamespace(weight=80), "Hanover")
        assert not guarantee_deterred(world, "Prussia", SimpleNamespace(weight=50), "Hanover")


class TestOCT27D7:
    """One honouring, on every road."""

    def test_the_tick_honours_a_war_from_another_road_before_any_brand(self, world, monkeypatch):
        from backend.game_logic import instruments as IN
        IN.pledge_guarantee(world, guarantor="Russia", protected="Hanover")
        _state(world, "Prussia", "Hanover", "WAR")    # a war the council never declared
        world.war_start_turns[world._make_diplo_key("Prussia", "Hanover")] = int(world.current_turn)
        assert not world.is_at_war("Russia", "Prussia")
        IN.process_instruments(world)
        assert world.is_at_war("Russia", "Prussia")   # honoured at the first tick
        honoured = [e for e in world.event_log if e.get("type") == "guarantee_honored"]
        assert honoured and honoured[-1]["guarantor"] == "Russia"

    def test_the_road_is_held_down_by_its_seam(self, world, monkeypatch):
        from backend.game_logic import instruments as IN
        monkeypatch.setattr(IN, "honour_on_road", lambda *a, **k: [])
        IN.pledge_guarantee(world, guarantor="Russia", protected="Hanover")
        _state(world, "Prussia", "Hanover", "WAR")
        world.war_start_turns[world._make_diplo_key("Prussia", "Hanover")] = int(world.current_turn)
        IN.process_instruments(world)
        assert not world.is_at_war("Russia", "Prussia")   # down: no road to join

    def test_the_league_join_road_calls_the_honouring(self):
        import inspect
        from backend.game_logic import coalition as CO
        from backend.commands import combat_executor as CE
        assert inspect.getsource(CO).count("honour_on_road(") >= 2
        assert inspect.getsource(CE).count("honour_on_road(") >= 2


class TestOCT27D8:
    """The Ansbach latch on a serialized map; a satisfied revanche refreshes."""

    def test_the_latch_reads_the_map_when_the_log_is_full(self, world, monkeypatch):
        from backend.game_logic import agendas as AG
        size = int(world.MAX_EVENT_LOG_SIZE)
        world.current_turn = 30
        world.event_log = [{"type": "filler", "turn": 29} for _ in range(size)]
        assert not AG.violation_on_cooldown(world, "France", "Prussia")   # never closed blind
        AG._note_violation(world, "France", "Prussia")
        assert AG.violation_on_cooldown(world, "France", "Prussia")
        world.current_turn = 30 + AG.AGENDA_VIOLATION_COOLDOWN
        assert not AG.violation_on_cooldown(world, "France", "Prussia")
        world.current_turn = 31
        reloaded = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        assert reloaded.agenda_violation_turns == {"France>Prussia": 30}
        assert AG.violation_on_cooldown(reloaded, "France", "Prussia")
        # a write prunes the map to the window
        world.current_turn = 30 + AG.AGENDA_VIOLATION_COOLDOWN + 1
        AG._note_violation(world, "France", "Bavaria")
        assert set(world.agenda_violation_turns) == {"France>Bavaria"}
        # a save from before the map keeps the rolled-log guard for its first window
        world.agenda_violation_map_since = int(world.current_turn)
        world.event_log = [{"type": "filler", "turn": int(world.current_turn)} for _ in range(size)]
        assert AG.violation_on_cooldown(world, "France", "Britain")
        world.current_turn += AG.AGENDA_VIOLATION_COOLDOWN
        world.event_log = [{"type": "filler", "turn": int(world.current_turn)} for _ in range(size)]
        assert not AG.violation_on_cooldown(world, "France", "Britain")   # the map covers it now
        old = WorldState.from_dict({k: v for k, v in json.loads(json.dumps(
            world.to_dict(), default=str)).items() if not k.startswith("agenda_violation")})
        assert old.agenda_violation_map_since == int(old.current_turn)   # a pre-map save
        # down: the full log fails closed for a pair that never violated
        monkeypatch.setattr(AG, "violation_latch_reads_the_map", lambda: False)
        world.agenda_violation_map_since = None
        assert AG.violation_on_cooldown(world, "France", "Britain")

    def test_a_satisfied_revanche_is_sworn_again(self, world, monkeypatch):
        from backend.game_logic import emergent_designs as ED
        world.agendas.setdefault("Prussia", []).insert(0, {
            "id": "revanche_prussia", "type": "acquire_regions", "title": "Revanche",
            "blurb": "", "regions": ["Silesia"], "emergent": True, "author": "Austria",
            "promoted_turn": 1})
        for name in ("Berlin", "Brandenburg"):
            world.regions[name].controller = "France"
        world.invalidate_active_nations_cache()
        events = [e for e in ED.process_emergent_designs(world) if e["nation"] == "Prussia"]
        assert len(events) == 1 and events[0].get("renewed"), events
        assert "swears revanche again" in events[0]["message"]
        entry = ED._emergent_entry(world, "Prussia")
        assert entry["regions"] == ["Silesia", "Berlin", "Brandenburg"]
        assert entry["author"] == "France" and entry["renewed_turn"] == int(world.current_turn)
        assert [e for e in world.agendas["Prussia"] if e.get("emergent")] == [entry]
        # an unsatisfied revanche is not re-sworn
        assert not [e for e in ED.process_emergent_designs(world) if e["nation"] == "Prussia"]

    def test_down_one_revanche_ever(self, world, monkeypatch):
        from backend.game_logic import emergent_designs as ED
        monkeypatch.setattr(ED, "emergent_design_refreshes", lambda *a, **k: False)
        world.agendas.setdefault("Prussia", []).insert(0, {
            "id": "revanche_prussia", "type": "acquire_regions", "regions": ["Silesia"],
            "emergent": True, "author": "Austria", "promoted_turn": 1})
        for name in ("Berlin", "Brandenburg"):
            world.regions[name].controller = "France"
        world.invalidate_active_nations_cache()
        assert not [e for e in ED.process_emergent_designs(world) if e["nation"] == "Prussia"]


def _letters(world):
    dm = world.dialogue_manager
    return [d for d in [dm.peek(), *dm.iter_queue()] if d]


def _swabia_french(world):
    world.regions["Swabia"].controller = "France"
    world.invalidate_active_nations_cache()


class TestOCT27D9:
    """An ally's ask for its home province reaches France as a letter."""

    def test_the_producer_writes_the_letter(self, world):
        from backend.game_logic import ai_diplomacy as AD
        _swabia_french(world)
        AD.process_province_returns(world)
        letters = [d for d in _letters(world) if AD.is_province_return_ask(d)]
        assert letters, "no province letter delivered"
        letter = letters[0]
        labels = [o["label"] for o in letter["options"] if not o.get("hidden")]
        assert labels == ["Return the province", "Keep the province"]
        assert "Swabia" in letter["talleyrand_text"] and "relations fall 5" in letter["talleyrand_text"]
        assert world.regions["Swabia"].controller == "France"        # nothing moved
        assert AD._get_cooldowns(world)["Bavaria|province_return_ask"] == AD.PROVINCE_RETURN_ASK_COOLDOWN
        before = len(letters)
        AD.process_province_returns(world)                           # the cooldown holds
        again = [d for d in _letters(world) if AD.is_province_return_ask(d)]
        assert len(again) == before

    def test_keep_costs_five_and_goes_on_the_record(self, world):
        from backend.game_logic import ai_diplomacy as AD
        _swabia_french(world)
        key = world._make_diplo_key("Bavaria", "France")
        before = int(world.nation_relations.get(key, 0))
        out = AD.answer_province_return(world, "Bavaria", "Swabia", give=False)
        assert out["verdict"] == "refused" and world.regions["Swabia"].controller == "France"
        assert int(world.nation_relations[key]) == max(-100, before - 5)
        assert [e["type"] for e in AD.get_refused_asks(world, "Bavaria", "France")] == ["province_return_ask"]
        kept = [e for e in world.event_log if e.get("type") == "province_returned"]
        assert kept[-1]["kept"] and kept[-1]["outcome"] == "refused"
        from backend.campaign_log import format_event_oneliner
        assert "keeps Swabia" in format_event_oneliner(kept[-1], "France")

    def test_return_hands_it_back_and_a_stale_ask_is_withdrawn(self, world):
        from backend.game_logic import ai_diplomacy as AD
        _swabia_french(world)
        out = AD.answer_province_return(world, "Bavaria", "Swabia", give=True)
        assert out["verdict"] == "granted" and world.regions["Swabia"].controller == "Bavaria"
        again = AD.answer_province_return(world, "Bavaria", "Swabia", give=True)
        assert again["verdict"] == "withdrawn"                       # it no longer stands

    def test_the_popup_reads_return_and_keep(self, world):
        """The client's register (a source census — the parse harness compiles
        it): Return / Keep with Keep's price on its tooltip, and S14I-3 — the
        Reject tooltip cleared before every letter's captions."""
        from backend.game_logic import ai_diplomacy as AD
        _swabia_french(world)
        AD.process_province_returns(world)
        letter = next(d for d in _letters(world) if AD.is_province_return_ask(d))
        payload = letter["popup_payload"]
        assert payload["is_province_letter"] is True
        assert "relations fall 5" in payload["keep_line"]
        gd = (REPO / "godot-client" / "project-sovereign" / "scripts"
              / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        assert 'accept_btn.text = "Return"' in gd and 'reject_btn.text = "Keep"' in gd
        reset = gd.index('reject_btn.tooltip_text = ""')
        captions = gd.index("if is_ultimatum:", reset)   # the caption chain the reset heads
        assert captions - reset < 80 < gd.index('reject_btn.text = "Keep"') - reset

    def test_down_the_court_asks_nothing(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as AD
        monkeypatch.setattr(AD, "province_letter_to_player", lambda *a, **k: None)
        _swabia_french(world)
        AD.process_province_returns(world)
        assert not [d for d in _letters(world) if AD.is_province_return_ask(d)]
        assert world.regions["Swabia"].controller == "France"


class TestOCT27D10:
    """The courts' answers, measured against what the player is shown."""

    def _young_war(self, world, age=2):
        _state(world, "France", "Prussia", "WAR")
        world.war_start_turns[world._make_diplo_key("France", "Prussia")] = int(world.current_turn) - age

    def test_the_arrival_forecast_counts_the_sting_and_the_weariness(self, world):
        from backend.game_logic import diplomacy as D
        self._young_war(world, age=2)
        proposal = {"type": "peace", "proposer_nation": "France", "target_nation": "Prussia",
                    "sweeteners": [], "demands": [{"type": "gold_lump", "value": 100}], "clauses": []}
        result = D.calculate_acceptance(proposal, world)
        assert result["components"]["war_age_penalty"] < 0
        gain = (D.war_age_acceptance_mod(3, extracts_value=True)
                - D.war_age_acceptance_mod(2, extracts_value=True)
                + D.war_weariness_acceptance_mod(3) - D.war_weariness_acceptance_mod(2))
        line = D.arrival_drift_line(world, proposal, result)
        assert line == (f"By his arrival Prussia will be about +{gain} readier — the young "
                        f"war's sting fades and its weariness grows.")
        white = dict(proposal, demands=[])
        assert D.arrival_drift_line(world, white, D.calculate_acceptance(white, world)) == ""

    def test_the_war_is_credited_in_one_place_its_total_measured(self, world, monkeypatch):
        """The fold (D10(ii)): the weight, R8 and R3 read from ONE function;
        the total is the settlement table's own felt credit (DDB-X5's pin,
        `tests/test_ddb_s13b_the_rulings.py::TestDDBX5`, holds 54 / 56 at 50)."""
        from backend.game_logic import diplomacy as D
        credit = D.bilateral_war_credit(60, "peace")
        assert credit == {"weighted": 60 * D.bilateral_war_score_weight(), "battlefield": 10,
                          "pressure": 9, "total": 60 * D.bilateral_war_score_weight() + 19}
        assert D.bilateral_war_credit(60, "peace", military_supremacy=10)["battlefield"] == 0
        assert D.bilateral_war_credit(60, "alliance")["battlefield"] == 0
        assert D.bilateral_war_credit(15, "peace")["battlefield"] == 0
        self._young_war(world, age=12)
        monkeypatch.setattr(D, "acceptance_reads_the_field", lambda *a, **k: False)
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 60 if key.startswith("France") else -60
        proposal = {"type": "peace", "proposer_nation": "France", "target_nation": "Prussia",
                    "sweeteners": [], "demands": [], "clauses": []}
        parts = D.calculate_acceptance(proposal, world)["components"]
        assert (parts["war_score_modifier"], parts["battlefield_diplomacy"],
                parts["military_pressure"]) == (round(credit["weighted"], 1), 10, 9)
        calls = []
        real = D.bilateral_war_credit
        monkeypatch.setattr(D, "bilateral_war_credit",
                            lambda *a, **k: calls.append(a) or real(*a, **k))
        D.calculate_acceptance(proposal, world)
        assert len(calls) == 2          # the weight's read and R3/R8's, one function

    def test_the_personality_term_ramps(self):
        from backend.game_logic.diplomacy import personality_term
        assert personality_term(10, -10, "peace", -3) == 10
        assert personality_term(10, -10, "peace", -7.5) == 0
        assert personality_term(10, -10, "peace", -12) == -10
        assert personality_term(10, -10, "peace", -40) == -10
        assert personality_term(10, -10, "vassalage", 0) == -10
        assert personality_term(-5, 5, "peace", -20) == -5            # the hawk unchanged
        steps = [personality_term(10, -10, "peace", -x / 2) for x in range(0, 40)]
        assert steps == sorted(steps, reverse=True)                   # monotone

    def test_a_held_province_is_priced_at_the_status_quo_rate(self, world):
        from backend.game_logic.diplomacy import analyze_territory_demands, held_cession_rate
        _swabia_french(world)
        demands = [{"type": "territory_cede", "regions": ["Swabia"]}]
        held = analyze_territory_demands(demands, "Bavaria", world, proposer="France")["held_costs"]
        weight = max(0.5, world.regions["Swabia"].income_value / 100)
        assert held == [("Swabia", -5 * weight * held_cession_rate())]
        assert held_cession_rate() == 0.5
        assert analyze_territory_demands(demands, "Bavaria", world)["held_costs"] == []

    def test_a_turned_back_envoy_brings_his_points_home(self, world, monkeypatch):
        import contextlib
        import io
        from backend.game_logic import diplomacy as D
        _state(world, "France", "Prussia", "NON_AGGRESSION")
        world.diplomatic_points = 1
        world.proposal_in_transit = {
            "target": "Prussia", "turns_remaining": 0, "turn_sent": int(world.current_turn) - 1,
            "dp_cost": 2,
            "proposal": {"type": "open_borders", "proposer_nation": "France", "target_nation": "Prussia",
                         "sweeteners": [], "demands": [], "clauses": []},
            "diplomatic_state_at_send": "NON_AGGRESSION", "acceptance_snapshot": 60}
        with contextlib.redirect_stdout(io.StringIO()):
            events = world._process_proposal_in_transit()
        returned = next(e for e in events if e.get("type") == "diplomatic_proposal_returned")
        assert returned["message"].endswith("His 2 DP come back with him; nothing is cooled.")
        assert world.diplomatic_points == 3
        assert "Prussia" not in world.player_proposal_cooldowns
        monkeypatch.setattr(D, "situation_changed_is_free", lambda: False)
        world.diplomatic_points = 1
        world.proposal_in_transit = dict(returned and {
            "target": "Prussia", "turns_remaining": 0, "turn_sent": int(world.current_turn) - 1,
            "dp_cost": 2,
            "proposal": {"type": "open_borders", "proposer_nation": "France", "target_nation": "Prussia",
                         "sweeteners": [], "demands": [], "clauses": []},
            "diplomatic_state_at_send": "NON_AGGRESSION", "acceptance_snapshot": 60})
        with contextlib.redirect_stdout(io.StringIO()):
            world._process_proposal_in_transit()
        assert world.diplomatic_points == 1 and world.player_proposal_cooldowns.get("Prussia") == 4

    def test_the_slide_clock_walks_the_forced_step(self, world, monkeypatch):
        from backend.game_logic import diplomacy as D
        key = world._make_diplo_key("France", "Spain")
        assert world.get_diplomatic_state("France", "Spain") == "ALLIANCE"
        world.nation_relations[key] = 50
        free = None
        monkeypatch.setattr(D, "forced_alliance_step", lambda *a, **k: 0)
        free = D.slide_clock(world, "Spain")
        monkeypatch.undo()
        world.alliance_origins = {key: "forced"}
        forced = D.slide_clock(world, "Spain")
        assert forced["rate"] == free["rate"] + 10
        assert forced["lapse_in"] is not None
        assert free["lapse_in"] is None or forced["lapse_in"] < free["lapse_in"]


class TestOCT27D11:
    """The proposal rungs' prices: a hawk pays the least."""

    def test_what_a_court_pays_scales_by_the_inverse(self, world, monkeypatch):
        from backend.game_logic import ai_diplomacy as AD
        assert AD.sweetener_multiplier(1.5) == pytest.approx(1 / 1.5)
        assert AD.sweetener_multiplier(0.75) == pytest.approx(1 / 0.75)
        world.nation_gold["Prussia"] = 1000
        _state(world, "France", "Prussia", "WAR")
        monkeypatch.setattr(world, "calculate_turn_income", lambda n: {"income": 10000})

        def gift(mult):
            terms = AD._build_proposal_terms("Prussia", "armistice_losing", -40, world, gold_mult=mult)
            return sum(int(s.get("value", 0) or 0) for s in terms["sweeteners"]
                       if s.get("type") == "gold_per_turn")
        assert gift(0.75) > gift(1.0) > gift(1.5)                    # the dove pays the most

    def test_the_compact_aims_at_the_courts_own_target(self, world, monkeypatch):
        from types import SimpleNamespace
        from backend.game_logic import ai_diplomacy as AD
        from backend.game_logic import intent as IT
        monkeypatch.setattr(IT, "get_nation_intent", lambda n, w: SimpleNamespace(against="Sweden"))
        assert AD.compact_aim_for(world, "Russia", ["Austria", "Sweden"]) == "Sweden"
        assert AD.compact_aim_for(world, "Russia", ["Austria", "Turkey"]) == "Austria"
        assert AD.compact_aim_for(world, "Russia", []) == ""


class TestOCT27D12:
    """The vassal roads."""

    def test_a_client_follows_its_lords_ally_to_peace(self):
        from backend.game_logic.vassal import client_follows_lord_footing
        assert client_follows_lord_footing("ALLIANCE") == "PEACE"
        assert client_follows_lord_footing("DEFENSIVE_ALLIANCE") == "PEACE"
        assert client_follows_lord_footing("ARMISTICE") == "ARMISTICE"
        assert client_follows_lord_footing("PEACE") == "PEACE"

    def test_a_war_of_frances_client_waits_for_france(self, world):
        from backend.game_logic import settlement_third_party as TP
        war = {"active_participants": ["Switzerland", "Sweden"],
               "side_by_nation": {"Switzerland": "defenders", "Sweden": "attackers"}}
        assert TP.client_war_waits_for_france(world, war, "France")
        assert not TP.client_war_waits_for_france(world, war, "France", broker="France")
        assert TP.attempt_third_party_settlement(world, "w", war) is None
        free = {"active_participants": ["Prussia", "Sweden"], "side_by_nation": {}}
        assert not TP.client_war_waits_for_france(world, free, "France")

    def test_the_bought_client_marches_against_its_old_lord(self, world, monkeypatch):
        from backend.game_logic import vassal as VA
        from backend.game_logic import diplomacy as D
        assert world.is_at_war("Russia", "France")
        world.vassals["Switzerland"]["loyalty"] = 5
        world.nation_gold["Russia"] = 5000
        monkeypatch.setattr(VA.random, "random", lambda: 0.0)
        monkeypatch.setattr(D, "check_vassalage_power_cap", lambda *a, **k: {"allowed": True})
        events = VA.attempt_vassal_bribe(world, "Russia")
        landed = [e for e in events if e.get("type") == "vassal_defected"]
        assert landed and landed[0]["outcome"] == "transfer", events
        assert world.vassals["Switzerland"]["lord"] == "Russia"
        assert world.get_diplomatic_state("Switzerland", "France") == "WAR"
        assert landed[0]["message"].endswith("Switzerland marches under Russia's eagle against France.")
        logged = [e for e in world.event_log if e.get("type") == "vassal_defected"]
        assert logged[-1]["marches"] is True

    def test_down_the_bought_client_stands_at_peace(self, world, monkeypatch):
        from backend.game_logic import vassal as VA
        from backend.game_logic import diplomacy as D
        monkeypatch.setattr(VA, "bribed_client_marches", lambda: False)
        world.vassals["Switzerland"]["loyalty"] = 5
        world.nation_gold["Russia"] = 5000
        monkeypatch.setattr(VA.random, "random", lambda: 0.0)
        monkeypatch.setattr(D, "check_vassalage_power_cap", lambda *a, **k: {"allowed": True})
        VA.attempt_vassal_bribe(world, "Russia")
        assert world.vassals["Switzerland"]["lord"] == "Russia"
        assert world.get_diplomatic_state("Switzerland", "France") != "WAR"

    def test_the_offered_crown_assimilates_the_marshals(self, world, monkeypatch):
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        from backend.game_logic import diplomacy as D
        monkeypatch.setattr(D, "check_vassalage_power_cap", lambda *a, **k: {"allowed": True})
        bavarians = [m for m in world.marshals.values() if m.nation == "Bavaria"]
        assert bavarians, "the 1805 boot has a Bavarian marshal"
        dialogue = {"type": "incoming_proposal", "target_nation": "Bavaria",
                    "context": {"source_nation": "Bavaria", "proposal_type": "offer_vassalage",
                                "proposal": {"type": "offer_vassalage", "proposer_nation": "Bavaria",
                                             "target_nation": "France"}}}
        world.dialogue_manager.replace(dialogue)
        result = DiplomaticExecutor(None)._handle_accept_ai_proposal(dialogue, world)
        assert result["success"], result
        assert world.vassals["Bavaria"]["lord"] == "France"
        assert all(m.nation == "France" and m.original_nation == "Bavaria" for m in bavarians)


class TestOCT27D13:
    """The enemy generals' remaining class."""

    def test_a_refused_order_cools_itself(self, world, monkeypatch):
        from backend.ai import enemy_ai as EA
        ai = _ai()
        ai._current_world = world
        assert EA.failed_order_key("attack", "Vienna") == "attack|Vienna"
        assert EA.failed_order_key("fortify", None) == "fortify"
        ai._record_failed_action("Ney", "attack", target="Vienna")
        assert world.ai_failed_action_cooldowns["Ney"] == {"attack|Vienna": 2}
        assert ai._is_action_on_cooldown("Ney", "attack", "Vienna")
        assert not ai._is_action_on_cooldown("Ney", "attack", "Munich")
        world.ai_failed_action_cooldowns["Ney"]["attack"] = 2      # a save from before
        assert ai._is_action_on_cooldown("Ney", "attack", "Munich")
        monkeypatch.setattr(EA, "cooldown_by_target", lambda: False)
        assert EA.failed_order_key("attack", "Vienna") == "attack"

    def test_a_refused_pick_is_asked_again_without_it(self, world, monkeypatch):
        from backend.ai import enemy_ai as EA
        ai = _ai()
        ai._current_world = world
        ai._marshals_done_this_turn = set()
        mack = world.marshals["Mack"]

        def fake_eval(marshal, nation, w):
            if marshal is not mack:
                return None, 999
            if ai._admits({"action": "attack", "target": "Munich"}):
                return {"marshal": marshal.name, "action": "attack", "target": "Munich"}, 4
            return {"marshal": marshal.name, "action": "fortify"}, 5
        monkeypatch.setattr(ai, "_evaluate_marshal", fake_eval)
        failed = {(mack.name, "attack", "Munich")}
        picked, action, _ = ai._select_next_marshal_action([mack], "Austria", world, {mack.name: 0}, failed)
        assert picked is mack and action["action"] == "fortify"
        monkeypatch.setattr(EA, "reevaluates_blocked_rung", lambda: False)
        picked, action, _ = ai._select_next_marshal_action([mack], "Austria", world, {mack.name: 0}, failed)
        assert picked is None

    def test_the_front_is_an_enemys_ground(self, world, monkeypatch):
        from types import SimpleNamespace
        from backend.ai import enemy_ai as EA
        from backend.game_logic import intent as IT
        ai = _ai()
        monkeypatch.setattr(IT, "get_nation_intent",
                            lambda n, w: SimpleNamespace(against="Hanover", price="ask"))
        assert ai._front_nations(world, "Prussia") == frozenset(
            n for n in world.get_active_nations() if n != "Prussia" and world.is_at_war("Prussia", n))
        assert not ai._is_front(world, "Prussia", "Hanover", legacy=True)
        monkeypatch.setattr(IT, "get_nation_intent",
                            lambda n, w: SimpleNamespace(against="Hanover", price="fight"))
        assert ai._is_front(world, "Prussia", "Hanover", legacy=False)
        monkeypatch.setattr(EA, "front_means_hostile", lambda: False)
        assert ai._is_front(world, "Prussia", "Saxony", legacy=True)

    def test_the_generals_draw_from_their_own_stream(self, world, monkeypatch):
        import random
        from backend.ai import enemy_ai as EA
        state = random.getstate()
        first = [EA.ai_rng(world, "Austria").random() for _ in range(3)]
        assert random.getstate() == state                           # the shared stream untouched
        other = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        assert [EA.ai_rng(other, "Austria").random() for _ in range(3)] == first
        assert EA.ai_rng(world, "Russia").random() != first[0]
        world.current_turn += 1
        assert EA.ai_rng(world, "Austria").random() != first[0]     # a new turn, a new stream
        assert EA.ai_rng(None, "Austria") is random
        # the seed reaches the stream through the variance layer's gate: a seed
        # with variance off draws as historical (IQ-7's control)
        from backend.game_logic import campaign_variance as CV
        world.current_turn -= 1
        world._ai_rng_cache = None
        world.campaign_seed = "ulm"
        assert EA.ai_rng(world, "Austria").random() != first[0]
        world._ai_rng_cache = None
        monkeypatch.setattr(CV, "is_historical", lambda seed: True)
        assert EA.ai_rng(world, "Austria").random() == first[0]

    def test_a_crashed_march_keeps_what_it_did_and_the_admin_phase_runs(self, world, monkeypatch):
        from backend.ai.enemy_ai import EnemyAI
        from backend.game_logic import turn_manager as TM
        tm = TM.TurnManager(world)
        ai = _ai()

        def crash(nation, w, gs):
            ai._partial_results.append({"action": "move", "message": "marched"})
            raise RuntimeError("mid-march")
        monkeypatch.setattr(ai, "process_nation_turn", crash)
        monkeypatch.setattr(ai, "execute_admin_phase", lambda *a, **k: [{"action": "recruit"}])
        results, admin = tm._run_ai_phases(ai, "Austria", {"world": world})
        assert [r["action"] for r in results] == ["move", "error", "recruit"]
        assert admin == [{"action": "recruit"}]
        monkeypatch.setattr(TM, "separate_ai_phases", lambda: False)
        results, admin = tm._run_ai_phases(ai, "Austria", {"world": world})
        assert [r["action"] for r in results] == ["error"] and admin == []
        assert EnemyAI  # the class the turn manager drives

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

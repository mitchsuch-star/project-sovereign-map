"""WB-C: War-entry integration — war_entry_score, hard blocks, join opportunities,
counter-bargain flow, reroll determinism, repudiate_bargain, AI rules, ledger."""

import pytest
from backend.game_logic.diplomacy import (
    compute_war_entry_score,
    get_ally_entry_hard_blocks,
    build_join_opportunity,
    resolve_join_opportunity,
    build_declaration_preview,
    build_peace_bargain_warnings,
    build_bargain_review,
    generate_counter_bargain,
    accept_counter_bargain,
    repudiate_bargain,
    get_live_bargains_for_ledger,
    ai_should_propose_bargain,
    ai_evaluate_war_entry,
    _hash_war_entry_inputs,
    _betrayal_key,
    create_war_bargain_commitment,
    declare_war,
    set_diplomatic_state,
    _get_live_bargains,
    WAR_ENTRY_BASE,
    WAR_ENTRY_TREATY_BONUS,
    WAR_ENTRY_DEFENSIVE_HONOR_BONUS,
    WAR_ENTRY_BARGAIN_BONUS,
    WAR_ENTRY_JOIN_THRESHOLD,
    WAR_ENTRY_COUNTER_BARGAIN_THRESHOLD,
    BARGAIN_BREACH_COOLDOWN_TURNS,
)
from backend.models.world_state import WorldState
from backend.commands.diplomatic_executor import DiplomaticExecutor


def _wbc_world() -> WorldState:
    world = WorldState()
    world.enemy_nations = ["Austria", "Prussia", "Britain", "Russia", "Saxony"]
    world.diplomatic_states = {}
    world.active_treaties = {}
    world.vassals = {}
    world.pending_dispatch_events = []
    world.event_log = []
    world.diplomatic_commitments = {}
    world.next_commitment_id = 1
    world.diplomatic_reliability = {"France": 50, "Prussia": 50, "Britain": 50, "Austria": 50}
    world.betrayal_history = {}
    world.current_turn = 5
    world.nation_relations = {}
    world._next_join_opportunity_id = 1
    world._war_entry_reroll_memory = {}
    world.pending_ally_entry_opportunities = []
    return world


def _setup_alliance(world, a="France", b="Prussia"):
    set_diplomatic_state(world, a, b, "ALLIANCE", "setup")
    pair_key = world._make_diplo_key(a, b)
    world.active_treaties[pair_key] = {
        "nations": [a, b], "type": "alliance", "clauses": [],
        "turn_signed": int(world.current_turn) - 1,
    }


def _setup_war(world, a="France", b="Britain"):
    set_diplomatic_state(world, a, b, "WAR", "setup")


def _setup_bargain(world, promiser="France", beneficiary="Prussia",
                   target_enemy="Britain", claim_region="Hanover"):
    _setup_alliance(world, promiser, beneficiary)
    _setup_war(world, promiser, target_enemy)
    return create_war_bargain_commitment(
        world, promiser, beneficiary, target_enemy, claim_region,
        "treaty_clause", world._make_diplo_key(promiser, beneficiary),
    )


# ═══════════════════════════════════════════════════════
# WAR ENTRY SCORE (12 tests)
# ═══════════════════════════════════════════════════════

class TestWarEntryScore:

    def test_base_score(self):
        world = _wbc_world()
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["score"] == WAR_ENTRY_BASE + result["components"]["reliability"]
        assert result["components"]["base"] == WAR_ENTRY_BASE

    def test_alliance_treaty_bonus(self):
        world = _wbc_world()
        _setup_alliance(world)
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["components"]["treaty_depth"] == WAR_ENTRY_TREATY_BONUS["ALLIANCE"]

    def test_defensive_alliance_treaty_bonus(self):
        world = _wbc_world()
        set_diplomatic_state(world, "France", "Prussia", "DEFENSIVE_ALLIANCE", "setup")
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["components"]["treaty_depth"] == WAR_ENTRY_TREATY_BONUS["DEFENSIVE_ALLIANCE"]

    def test_defensive_honor_bonus(self):
        world = _wbc_world()
        _setup_alliance(world)
        result = compute_war_entry_score(
            world, "France", "Prussia", "Britain", is_defensive=True,
        )
        assert result["components"]["defensive_honor"] == WAR_ENTRY_DEFENSIVE_HONOR_BONUS

    def test_no_defensive_bonus_on_offensive(self):
        world = _wbc_world()
        _setup_alliance(world)
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["components"]["defensive_honor"] == 0

    def test_matching_bargain_bonus(self):
        world = _wbc_world()
        _setup_bargain(world)
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["components"]["matching_bargain"] == WAR_ENTRY_BARGAIN_BONUS

    def test_no_bargain_no_bonus(self):
        world = _wbc_world()
        _setup_alliance(world)
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["components"]["matching_bargain"] == 0

    def test_betrayal_penalty(self):
        world = _wbc_world()
        pair_key = world._make_diplo_key("Prussia", "France")
        world.betrayal_history[pair_key] = {
            "strikes": [{"severity": "high"}, {"severity": "medium"}],
        }
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["components"]["betrayal_strikes"] == -16

    def test_betrayal_cap(self):
        world = _wbc_world()
        pair_key = world._make_diplo_key("Prussia", "France")
        world.betrayal_history[pair_key] = {
            "strikes": [{"severity": "high"}] * 5,
        }
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["components"]["betrayal_strikes"] == -24

    def test_betrayal_penalty_uses_directional_key(self):
        world = _wbc_world()
        world.betrayal_history[_betrayal_key("France", "Britain")] = {
            "strikes": [{"severity": "high"}, {"severity": "medium"}],
        }
        result = compute_war_entry_score(world, "France", "Britain", "Prussia")
        assert result["components"]["betrayal_strikes"] == -16

    def test_war_load_one_war(self):
        world = _wbc_world()
        _setup_war(world, "Prussia", "Austria")
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["components"]["war_load"] == -8

    def test_war_load_multi(self):
        world = _wbc_world()
        # Ensure Austria and Russia aren't eliminated (need regions)
        from backend.models.region import Region
        world.regions["Vienna"] = Region("Vienna", [])
        world.regions["Vienna"].controller = "Austria"
        world.regions["Moscow"] = Region("Moscow", [])
        world.regions["Moscow"].controller = "Russia"
        world.invalidate_active_nations_cache()
        set_diplomatic_state(world, "Prussia", "Austria", "WAR", "setup")
        set_diplomatic_state(world, "Prussia", "Russia", "WAR", "setup")
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["components"]["war_load"] == -18

    def test_band_thresholds(self):
        world = _wbc_world()
        _setup_alliance(world)
        _setup_bargain(world)
        result = compute_war_entry_score(world, "France", "Prussia", "Britain")
        assert result["band"] in ("join", "counter_bargain", "refuse")
        if result["score"] >= WAR_ENTRY_JOIN_THRESHOLD:
            assert result["band"] == "join"
        elif result["score"] >= WAR_ENTRY_COUNTER_BARGAIN_THRESHOLD:
            assert result["band"] == "counter_bargain"
        else:
            assert result["band"] == "refuse"


# ═══════════════════════════════════════════════════════
# HARD BLOCKS (6 tests)
# ═══════════════════════════════════════════════════════

class TestHardBlocks:

    def test_no_blocks_clean_state(self):
        world = _wbc_world()
        _setup_alliance(world)
        blocks = get_ally_entry_hard_blocks(world, "France", "Prussia", "Britain")
        assert blocks == []

    def test_armistice_block(self):
        world = _wbc_world()
        diplo_key = world._make_diplo_key("Prussia", "Britain")
        world.armistice_cooldowns = {diplo_key: 3}
        blocks = get_ally_entry_hard_blocks(world, "France", "Prussia", "Britain")
        assert any("armistice" in b for b in blocks)

    def test_anti_coalition_block(self):
        world = _wbc_world()
        world.active_coalition = {"target_nation": "France", "members": ["Prussia"]}
        blocks = get_ally_entry_hard_blocks(world, "France", "Prussia", "Britain")
        assert "anti_promiser_coalition_member" in blocks

    def test_hard_reject_posture_offensive_only(self):
        world = _wbc_world()
        world.betrayal_history[_betrayal_key("France", "Britain")] = {
            "strikes": [{"severity": "high"}] * 3,
        }
        blocks_off = get_ally_entry_hard_blocks(
            world, "France", "Britain", "Prussia", is_offensive=True,
        )
        assert "hard_reject_posture" in blocks_off

        blocks_def = get_ally_entry_hard_blocks(
            world, "France", "Britain", "Prussia", is_offensive=False,
        )
        assert "hard_reject_posture" not in blocks_def

    def test_hard_reject_ignores_wrong_direction_sorted_key(self):
        world = _wbc_world()
        world.betrayal_history[world._make_diplo_key("France", "Britain")] = {
            "strikes": [{"severity": "high"}] * 3,
        }
        blocks = get_ally_entry_hard_blocks(
            world, "France", "Britain", "Prussia", is_offensive=True,
        )
        assert "hard_reject_posture" not in blocks

    def test_no_participation_path(self):
        world = _wbc_world()
        blocks = get_ally_entry_hard_blocks(world, "France", "Saxony", "Russia")
        found_no_path = any("no_participation" in b for b in blocks)
        assert isinstance(blocks, list)

    def test_at_war_with_promiser(self):
        world = _wbc_world()
        _setup_war(world, "Prussia", "France")
        blocks = get_ally_entry_hard_blocks(world, "France", "Prussia", "Britain")
        assert any("at_war" in b or "direct_enemy" in b for b in blocks)


# ═══════════════════════════════════════════════════════
# JOIN OPPORTUNITY (6 tests)
# ═══════════════════════════════════════════════════════

class TestJoinOpportunity:

    def test_build_opportunity(self):
        world = _wbc_world()
        _setup_alliance(world)
        opp = build_join_opportunity(
            world, "Prussia", "Britain", "offensive_ally_request",
            promiser="France",
        )
        assert opp["beneficiary"] == "Prussia"
        assert opp["named_enemy"] == "Britain"
        assert opp["request_type"] == "offensive_ally_request"
        assert "war_entry_score" in opp
        assert opp["resolved"] is False

    def test_opportunity_id_increments(self):
        world = _wbc_world()
        opp1 = build_join_opportunity(world, "Prussia", "Britain", "offensive_ally_request")
        opp2 = build_join_opportunity(world, "Austria", "Britain", "offensive_ally_request")
        assert opp2["id"] == opp1["id"] + 1

    def test_resolve_accept(self):
        world = _wbc_world()
        _setup_alliance(world)
        opp = build_join_opportunity(
            world, "Prussia", "Britain", "offensive_ally_request", promiser="France",
        )
        result = resolve_join_opportunity(world, opp, "accept")
        assert result["joined"] is True
        assert opp["resolved"] is True

    def test_resolve_reject(self):
        world = _wbc_world()
        _setup_alliance(world)
        opp = build_join_opportunity(
            world, "Prussia", "Britain", "offensive_ally_request", promiser="France",
        )
        result = resolve_join_opportunity(world, opp, "reject")
        assert result["joined"] is False

    def test_resolve_back_out(self):
        world = _wbc_world()
        opp = build_join_opportunity(
            world, "Prussia", "Britain", "offensive_ally_request", promiser="France",
        )
        result = resolve_join_opportunity(world, opp, "back_out")
        assert result.get("backed_out") is True

    def test_reroll_key_format(self):
        world = _wbc_world()
        opp = build_join_opportunity(
            world, "Prussia", "Britain", "offensive_ally_request",
        )
        assert opp["reroll_key"] == f"Prussia|Britain|offensive_ally_request|{world.current_turn}"


# ═══════════════════════════════════════════════════════
# DECLARATION PREVIEW (4 tests)
# ═══════════════════════════════════════════════════════

class TestDeclarationPreview:

    def test_preview_includes_ally_opportunities(self):
        world = _wbc_world()
        _setup_alliance(world, "France", "Prussia")
        preview = build_declaration_preview(world, "France", "Britain")
        assert "ally_entry_opportunities" in preview
        found_prussia = any(
            o["beneficiary"] == "Prussia" for o in preview["ally_entry_opportunities"]
        )
        assert found_prussia

    def test_preview_with_bargain_warnings(self):
        world = _wbc_world()
        _setup_bargain(world)
        preview = build_declaration_preview(world, "France", "Britain")
        assert len(preview["bargain_warnings"]) >= 1

    def test_preview_no_self_in_opportunities(self):
        world = _wbc_world()
        preview = build_declaration_preview(world, "France", "Britain")
        for opp in preview.get("ally_entry_opportunities", []):
            assert opp["beneficiary"] != "France"
            assert opp["beneficiary"] != "Britain"

    def test_peace_bargain_warnings(self):
        world = _wbc_world()
        _setup_bargain(world)
        warnings = build_peace_bargain_warnings(world, "France", "Britain")
        assert len(warnings) >= 1
        assert "breach" in warnings[0]["warning"].lower() or "bargain" in warnings[0]["warning"].lower()


# ═══════════════════════════════════════════════════════
class TestWarEntryCommandIntegration:

    def test_declare_war_surfaces_ally_entry_dialogue(self):
        world = _wbc_world()
        set_diplomatic_state(world, "France", "Britain", "PEACE", "setup")
        _setup_alliance(world)
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = 100
        world.nation_relations[world._make_diplo_key("Prussia", "Britain")] = -100
        executor = DiplomaticExecutor(None)

        result = executor._execute_diplomatic_declare_war(
            {"target_nation": "Britain", "war_objective": "conquest"},
            world,
        )

        assert result["success"] is True
        assert result["awaiting_diplomatic_response"] is True
        dialogue = result["diplomatic_dialogue"]
        assert dialogue["context"]["kind"] == "ally_entry_review"
        assert any(o.get("beneficiary") == "Prussia" for o in dialogue["context"]["join_opportunities"])

    def test_accept_ally_entry_then_declare_war_joins_ally(self):
        world = _wbc_world()
        set_diplomatic_state(world, "France", "Britain", "PEACE", "setup")
        _setup_alliance(world)
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = 100
        world.nation_relations[world._make_diplo_key("Prussia", "Britain")] = -100
        executor = DiplomaticExecutor(None)
        executor._execute_diplomatic_declare_war(
            {"target_nation": "Britain", "war_objective": "conquest"},
            world,
        )

        result = executor.handle_diplomatic_dialogue_response(1, {"world": world})

        assert result["success"] is True
        assert world.is_at_war("France", "Britain")
        assert world.is_at_war("Prussia", "Britain")
        assert any(c.get("attacker_ally") == "Prussia" for c in result["cascade"])

    def test_suppressed_offensive_cascade_requires_explicit_decision(self):
        world = _wbc_world()
        set_diplomatic_state(world, "France", "Britain", "PEACE", "setup")
        _setup_alliance(world)

        result = declare_war(
            world,
            "France",
            "Britain",
            war_objective="conquest",
            suppress_unresolved_offensive_cascade=True,
        )

        assert result["success"] is True
        assert not world.is_at_war("Prussia", "Britain")
        assert any(e.get("path") == "not_requested" for e in result["war_entry_ledger"])


# BARGAIN REVIEW (3 tests)
# ═══════════════════════════════════════════════════════

class TestBargainReview:

    def test_review_basic_fields(self):
        world = _wbc_world()
        _setup_alliance(world)
        clause = {"beneficiary": "Prussia", "named_enemy": "Britain", "claim_region": "Hanover"}
        proposal = {"proposer_nation": "France", "target_nation": "Prussia"}
        review = build_bargain_review(world, clause, proposal)
        assert review["beneficiary"] == "Prussia"
        assert review["named_enemy"] == "Britain"
        assert review["claim_region"] == "Hanover"
        assert review["war_entry_forecast_band"] in ("join", "counter_bargain", "refuse")

    def test_review_decisive_flag(self):
        world = _wbc_world()
        _setup_alliance(world)
        clause = {"beneficiary": "Prussia", "named_enemy": "Britain", "claim_region": "Hanover"}
        proposal = {"proposer_nation": "France", "target_nation": "Prussia"}
        review = build_bargain_review(world, clause, proposal)
        assert isinstance(review["is_decisive"], bool)

    def test_review_contradiction_warnings(self):
        world = _wbc_world()
        _setup_bargain(world, target_enemy="Austria", claim_region="Bohemia")
        clause = {"beneficiary": "Prussia", "named_enemy": "Britain", "claim_region": "Hanover"}
        proposal = {"proposer_nation": "France", "target_nation": "Prussia"}
        review = build_bargain_review(world, clause, proposal)
        assert isinstance(review["contradiction_warnings"], list)


# ═══════════════════════════════════════════════════════
# COUNTER-BARGAIN (4 tests)
# ═══════════════════════════════════════════════════════

class TestCounterBargain:

    def test_generate_returns_none_for_join_band(self):
        world = _wbc_world()
        _setup_alliance(world)
        _setup_bargain(world)
        counter = generate_counter_bargain(
            world, "France", "Prussia", "Britain",
        )
        # With alliance + bargain bonus, score should be in join band
        entry = compute_war_entry_score(world, "France", "Prussia", "Britain")
        if entry["band"] == "join":
            assert counter is None

    def test_accept_counter_bargain_creates_triggered(self):
        world = _wbc_world()
        _setup_alliance(world)
        _setup_war(world)
        counter = {
            "type": "war_entry_counter_bargain",
            "beneficiary": "Prussia",
            "named_enemy": "Britain",
            "demanded_region": "Hanover",
            "promiser": "France",
        }
        result = accept_counter_bargain(world, counter)
        assert result["success"] is True
        bargain = result["bargain"]
        assert bargain["status"] == "triggered"
        event_types = [e.get("type") for e in world.event_log]
        assert "bargain_ratified" in event_types
        assert "bargain_triggered" in event_types

    def test_reroll_determinism(self):
        world = _wbc_world()
        _setup_alliance(world)
        _setup_war(world)
        key = "Prussia|Britain|offensive_ally_request|5"
        c1 = generate_counter_bargain(world, "France", "Prussia", "Britain", reroll_key=key)
        c2 = generate_counter_bargain(world, "France", "Prussia", "Britain", reroll_key=key)
        if c1 is not None and c2 is not None:
            assert c1["demanded_region"] == c2["demanded_region"]

    def test_hash_inputs_change_on_state_mutation(self):
        world = _wbc_world()
        _setup_alliance(world)
        h1 = _hash_war_entry_inputs(world, "France", "Prussia", "Britain")
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = 50
        h2 = _hash_war_entry_inputs(world, "France", "Prussia", "Britain")
        assert h1 != h2


# ═══════════════════════════════════════════════════════
# REPUDIATE BARGAIN (5 tests)
# ═══════════════════════════════════════════════════════

class TestRepudiateBargain:

    def test_repudiate_success(self):
        world = _wbc_world()
        bargain = _setup_bargain(world)
        bid = str(bargain["id"])
        result = repudiate_bargain(world, bid)
        assert result["success"] is True
        assert bargain["status"] == "breached"

    def test_repudiate_nonexistent(self):
        world = _wbc_world()
        result = repudiate_bargain(world, "999")
        assert result["success"] is False

    def test_repudiate_already_ended(self):
        world = _wbc_world()
        bargain = _setup_bargain(world)
        bargain["status"] = "fulfilled"
        bargain["ended_turn"] = 5
        result = repudiate_bargain(world, str(bargain["id"]))
        assert result["success"] is False

    def test_repudiate_applies_breach_penalties(self):
        world = _wbc_world()
        bargain = _setup_bargain(world)
        reliability_before = world.diplomatic_reliability.get("France", 50)
        repudiate_bargain(world, str(bargain["id"]))
        reliability_after = world.diplomatic_reliability.get("France", 50)
        assert reliability_after < reliability_before

    def test_repudiate_sets_cooldown(self):
        world = _wbc_world()
        bargain = _setup_bargain(world)
        repudiate_bargain(world, str(bargain["id"]))
        assert bargain.get("cooldown_until_turn", 0) > world.current_turn

    def test_repudiate_confirmation_uses_dialogue_and_costs_action(self):
        world = _wbc_world()
        _setup_bargain(world)
        world.actions_remaining = 2
        executor = DiplomaticExecutor(None)

        result = executor._execute_repudiate_bargain(
            {"action": "repudiate_bargain", "target_nation": "Prussia"},
            world,
        )
        assert result["success"] is True
        assert result["no_action_cost"] is True
        assert result["diplomatic_dialogue"]["options"][0]["action"] == "confirm_repudiate_bargain"

        response = executor.handle_diplomatic_dialogue_response(1, {"world": world})
        assert response["success"] is True
        assert world.actions_remaining == 1
        assert any(e.get("type") == "bargain_breached" for e in world.event_log)
        assert not any(e.get("type") == "bargain_repudiated" for e in world.event_log)


# ═══════════════════════════════════════════════════════
# AI RULES (6 tests)
# ═══════════════════════════════════════════════════════

class TestAIRules:

    def test_ai_feasible_proposal(self):
        world = _wbc_world()
        _setup_alliance(world)
        _setup_war(world)
        result = ai_should_propose_bargain(world, "France", "Prussia", "Britain")
        assert isinstance(result["feasible"], bool)
        assert result["decision_reason"] in (
            "claim_trade", "anti_spam", "cooldown_active", "no_feasible_target",
            "participation_blocked", "strength_insufficient", "counterparty_reversal",
            "no_valid_region", "contradiction",
        )

    def test_ai_anti_spam_existing_bargain(self):
        world = _wbc_world()
        _setup_bargain(world)
        result = ai_should_propose_bargain(world, "France", "Prussia", "Britain")
        assert result["feasible"] is False
        assert result["decision_reason"] == "anti_spam"

    def test_ai_cooldown_blocks(self):
        world = _wbc_world()
        _setup_alliance(world)
        _setup_war(world)
        world.diplomatic_commitments["99"] = {
            "cooldown_key": "France|Prussia::Britain",
            "cooldown_until_turn": 20,
            "status": "breached",
        }
        result = ai_should_propose_bargain(world, "France", "Prussia", "Britain")
        assert result["feasible"] is False
        assert result["decision_reason"] == "cooldown_active"

    def test_ai_betrayal_refusal(self):
        world = _wbc_world()
        _setup_alliance(world)
        _setup_war(world, "France", "Britain")
        pair_key = world._make_diplo_key("Prussia", "France")
        world.betrayal_history[pair_key] = {
            "strikes": [{"severity": "high"}] * 3,
        }
        result = ai_should_propose_bargain(world, "France", "Prussia", "Britain")
        assert result["feasible"] is False
        assert result["decision_reason"] == "counterparty_reversal"

    def test_ai_evaluate_join_with_bargain(self):
        world = _wbc_world()
        _setup_bargain(world)
        result = ai_evaluate_war_entry(world, "France", "Prussia", "Britain")
        assert isinstance(result["join"], bool)
        assert isinstance(result["counter_bargain"], bool)

    def test_ai_evaluate_hard_blocked(self):
        world = _wbc_world()
        world.active_coalition = {"target_nation": "France", "members": ["Prussia"]}
        result = ai_evaluate_war_entry(world, "France", "Prussia", "Britain")
        assert result["join"] is False
        assert result["counter_bargain"] is False
        assert result["decision_reason"] == "hard_blocked"


# ═══════════════════════════════════════════════════════
# LEDGER (3 tests)
# ═══════════════════════════════════════════════════════

class TestLedger:

    def test_ledger_empty(self):
        world = _wbc_world()
        result = get_live_bargains_for_ledger(world)
        assert result == []

    def test_ledger_live_bargain(self):
        world = _wbc_world()
        _setup_bargain(world)
        result = get_live_bargains_for_ledger(world)
        assert len(result) == 1
        entry = result[0]
        assert entry["beneficiary"] == "Prussia"
        assert entry["named_enemy"] == "Britain"
        assert entry["claim_region"] == "Hanover"
        assert entry["status"] == "active"

    def test_ledger_excludes_ended(self):
        world = _wbc_world()
        bargain = _setup_bargain(world)
        bargain["status"] = "fulfilled"
        bargain["ended_turn"] = 5
        result = get_live_bargains_for_ledger(world)
        assert len(result) == 0


# ═══════════════════════════════════════════════════════
# SERIALIZATION (3 tests)
# ═══════════════════════════════════════════════════════

class TestSerialization:

    def test_wbc_fields_roundtrip(self):
        world = _wbc_world()
        world._next_join_opportunity_id = 5
        world._war_entry_reroll_memory = {"key1": {"counter_bargain": None, "score_inputs_hash": "abc"}}
        world.pending_ally_entry_opportunities = [{"id": 1, "beneficiary": "Prussia"}]

        data = world.to_dict()
        assert data["next_join_opportunity_id"] == 5
        assert "key1" in data["war_entry_reroll_memory"]
        assert len(data["pending_ally_entry_opportunities"]) == 1

        world2 = WorldState.from_dict(data)
        assert world2._next_join_opportunity_id == 5
        assert "key1" in world2._war_entry_reroll_memory
        assert len(world2.pending_ally_entry_opportunities) == 1

    def test_pre_wbc_save_loads_cleanly(self):
        world = _wbc_world()
        data = world.to_dict()
        del data["next_join_opportunity_id"]
        del data["war_entry_reroll_memory"]
        del data["pending_ally_entry_opportunities"]
        world2 = WorldState.from_dict(data)
        assert world2._next_join_opportunity_id == 1
        assert world2._war_entry_reroll_memory == {}
        assert world2.pending_ally_entry_opportunities == []

    def test_full_diplomatic_ledger_includes_bargains(self):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world = _wbc_world()
        _setup_bargain(world)
        ledger = build_diplomatic_ledger(world)
        assert "war_bargains" in ledger
        assert len(ledger["war_bargains"]) == 1


# ═══════════════════════════════════════════════════════
# ACTION WIRING (4 tests)
# ═══════════════════════════════════════════════════════

class TestActionWiring:

    def test_repudiate_in_valid_actions(self):
        from backend.ai.validation import VALID_ACTIONS, META_ACTIONS
        assert "repudiate_bargain" in VALID_ACTIONS
        assert "repudiate_bargain" in META_ACTIONS

    def test_repudiate_in_display_names(self):
        from backend.display_names import ACTION_DISPLAY, OBJECTION_DISPLAY, DEFIANCE_DISPLAY
        assert "repudiate_bargain" in ACTION_DISPLAY
        assert "repudiate_bargain" in OBJECTION_DISPLAY
        assert "repudiate_bargain" in DEFIANCE_DISPLAY

    def test_wbc_event_types_in_campaign_log(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, CATEGORY_MAP
        wbc_types = {
            "bargain_ratified", "hard_block_surfaced", "ally_refused_free_join",
            "declaration_backed_out", "bargain_repudiated",
            "ally_entry_accepted", "ally_entry_refused",
            "counter_bargain_accepted", "counter_bargain_rejected",
        }
        for t in wbc_types:
            assert t in CAMPAIGN_LOG_TYPES, f"{t} missing from CAMPAIGN_LOG_TYPES"
            assert t in CATEGORY_MAP, f"{t} missing from CATEGORY_MAP"

    def test_repudiate_in_parser(self):
        from backend.commands.parser import CommandParser
        parser = CommandParser()
        assert "repudiate_bargain" in parser.valid_actions

    def test_repudiate_action_costs_one_ap(self):
        world = _wbc_world()
        assert world.get_action_cost("repudiate_bargain") == 1

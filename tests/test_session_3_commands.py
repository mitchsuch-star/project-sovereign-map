"""
Tests for Phase 8 Session 3: Talleyrand Commands + Conversational Dialogue Foundation.

Coverage:
- Parser routing (diplomatic vs military)
- Nation name extraction
- Specificity classification
- Dialogue generation
- Dialogue blocking
- Proposal execution flow
- Acceptance integration
- Treaty ratification
- Per-turn treaty clauses
- Treaty breaking
- Feasibility requests
- Missions (start, effects, pause, resume, cancel)
- Player proposal cooldowns
- Talleyrand in-transit blocking
- /respond_to_diplomatic_dialogue endpoint
- Dispatch events
- Serialization round-trip
- No regression on existing commands
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.ai.llm_client import LLMClient


@pytest.fixture
def world():
    """Create a fresh WorldState for testing."""
    w = WorldState(player_nation="France")
    return w


@pytest.fixture
def game_state(world):
    """Create a game state dict."""
    return {"world": world}


@pytest.fixture
def executor():
    """Create a command executor."""
    return CommandExecutor()


@pytest.fixture
def llm():
    """Create a mock LLM client."""
    return LLMClient(use_real_api=False)


# ═══════════════════════════════════════════════════════
# PARSER ROUTING TESTS
# ═══════════════════════════════════════════════════════

class TestParserRouting:
    def test_talleyrand_propose_peace_routes_to_diplomatic(self, llm):
        result = llm.parse_command("Talleyrand, propose peace with Prussia")
        assert result.get("diplomatic_data") is not None
        assert result["diplomatic_data"]["action"] == "diplomatic_proposal"
        assert result["diplomatic_data"]["target_nation"] == "Prussia"
        assert result["diplomatic_data"]["proposal_type"] == "peace"

    def test_ney_attack_routes_to_military(self, llm):
        result = llm.parse_command("Ney, attack Belgium")
        assert result.get("diplomatic_data") is None
        assert result["action"] == "attack"
        assert result["marshal"] == "Ney"

    def test_talleyrand_attack_returns_diplomat_error(self, llm):
        result = llm.parse_command("Talleyrand, attack Belgium")
        assert result.get("diplomatic_data") is not None
        assert result["diplomatic_data"]["action"] == "diplomatic_error"
        assert "diplomat" in result["diplomatic_data"]["message"].lower()

    def test_talleyrand_propose_alliance(self, llm):
        result = llm.parse_command("Talleyrand, propose alliance with Austria")
        data = result.get("diplomatic_data")
        assert data is not None
        assert data["proposal_type"] == "alliance"
        assert data["target_nation"] == "Austria"

    def test_talleyrand_demand_vassalage(self, llm):
        result = llm.parse_command("Talleyrand, demand vassalage from Saxony")
        data = result.get("diplomatic_data")
        assert data is not None
        assert data["tone"] == "demand"
        assert data["target_nation"] == "Saxony"

    def test_talleyrand_feasibility_question(self, llm):
        result = llm.parse_command("Talleyrand, what would it take to get peace with Prussia?")
        data = result.get("diplomatic_data")
        assert data is not None
        assert data["action"] == "diplomatic_feasibility"
        assert data["is_question"] is True

    def test_talleyrand_improve_relations_mission(self, llm):
        result = llm.parse_command("Talleyrand, improve relations with Austria")
        data = result.get("diplomatic_data")
        assert data is not None
        assert data["action"] == "diplomatic_mission"
        assert data["mission_type"] == "IMPROVE_RELATIONS"

    def test_talleyrand_cancel_mission(self, llm):
        result = llm.parse_command("Talleyrand, cancel mission")
        data = result.get("diplomatic_data")
        assert data is not None
        assert data["mission_type"] == "CANCEL"


# ═══════════════════════════════════════════════════════
# NATION NAME EXTRACTION
# ═══════════════════════════════════════════════════════

class TestNationExtraction:
    def test_england_maps_to_britain(self, llm):
        result = llm.parse_command("Talleyrand, deal with England")
        data = result.get("diplomatic_data")
        assert data["target_nation"] == "Britain"

    def test_uk_maps_to_britain(self, llm):
        result = llm.parse_command("Talleyrand, propose peace with the UK")
        data = result.get("diplomatic_data")
        assert data["target_nation"] == "Britain"

    def test_austrian_maps_to_austria(self, llm):
        result = llm.parse_command("Talleyrand, deal with the Austrian court")
        data = result.get("diplomatic_data")
        assert data["target_nation"] == "Austria"

    def test_unknown_nation_detected_at_executor(self, executor, game_state):
        """Unknown nations are detected at executor level, not parser."""
        parsed = {
            "success": True,
            "command": {
                "action": "diplomatic_proposal",
                "diplomatic_data": {
                    "action": "diplomatic_proposal",
                    "target_nation": "Atlantis",
                    "proposal_type": "peace",
                    "has_diplomatic_keywords": True,
                    "raw_text": "Talleyrand, propose peace with Atlantis",
                    "clauses": [],
                    "is_question": False,
                    "tone": "propose",
                },
            },
        }
        result = executor.execute(parsed, game_state)
        assert not result["success"]
        assert "not aware" in result["message"].lower() or "atlantis" in result["message"].lower()


# ═══════════════════════════════════════════════════════
# SPECIFICITY CLASSIFICATION
# ═══════════════════════════════════════════════════════

class TestSpecificityClassification:
    def test_vague_command(self):
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        w = WorldState(player_nation="France")
        parsed = {
            "target_nation": "Prussia",
            "proposal_type": None,
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "raw_text": "deal with Prussia",
        }
        assert classify_diplomatic_intent(parsed, w) == "proposal_options"

    def test_medium_command(self):
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        w = WorldState(player_nation="France")
        parsed = {
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "raw_text": "propose peace with Prussia",
        }
        assert classify_diplomatic_intent(parsed, w) == "proposal_confirm"

    def test_specific_command(self):
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        w = WorldState(player_nation="France")
        parsed = {
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [{"type": "open_borders"}],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "raw_text": "propose peace with Prussia: open borders",
        }
        assert classify_diplomatic_intent(parsed, w) == "proposal_execute"

    def test_feasibility_question(self):
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        w = WorldState(player_nation="France")
        parsed = {
            "target_nation": "Prussia",
            "proposal_type": None,
            "clauses": [],
            "is_question": True,
            "has_diplomatic_keywords": True,
            "raw_text": "what would it take to get peace with Prussia?",
        }
        assert classify_diplomatic_intent(parsed, w) == "feasibility"

    def test_advisory_question(self):
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        w = WorldState(player_nation="France")
        parsed = {
            "target_nation": "Austria",
            "proposal_type": None,
            "clauses": [],
            "is_question": True,
            "has_diplomatic_keywords": True,
            "raw_text": "what about Austria?",
        }
        assert classify_diplomatic_intent(parsed, w) == "advisory"

    def test_mission_classification(self):
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        w = WorldState(player_nation="France")
        parsed = {
            "target_nation": "Austria",
            "proposal_type": None,
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": "IMPROVE_RELATIONS",
            "raw_text": "improve relations with Austria",
        }
        assert classify_diplomatic_intent(parsed, w) == "mission"


# ═══════════════════════════════════════════════════════
# DIALOGUE GENERATION
# ═══════════════════════════════════════════════════════

class TestDialogueGeneration:
    def test_vague_war_generates_options(self, world):
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        dialogue = generate_dialogue("proposal_options", {
            "target_nation": "Prussia",
            "proposal_type": None,
            "raw_text": "deal with Prussia",
        }, world)
        assert dialogue["type"] == "proposal_options"
        assert len(dialogue["options"]) >= 2
        assert dialogue["target_nation"] == "Prussia"
        assert dialogue["turn_created"] == world.current_turn

    def test_medium_peace_generates_confirm(self, world):
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        dialogue = generate_dialogue("proposal_confirm", {
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "raw_text": "propose peace with Prussia",
        }, world)
        assert dialogue["type"] == "proposal_confirm"
        assert len(dialogue["options"]) >= 2

    def test_specific_generates_fast_track(self, world):
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        dialogue = generate_dialogue("proposal_execute", {
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "raw_text": "propose peace with Prussia",
        }, world)
        assert dialogue["type"] == "proposal_execute"
        # Should have Send + Reconsider
        actions = [o["action"] for o in dialogue["options"]]
        assert "send" in actions or "execute_proposal" in actions

    def test_feasibility_generates_assessment(self, world):
        from backend.game_logic.diplomatic_dialogue import generate_feasibility_dialogue
        dialogue = generate_feasibility_dialogue({
            "target_nation": "Prussia",
            "proposal_type": "peace",
        }, world)
        assert dialogue["type"] == "feasibility"
        assert "assessment" in dialogue["talleyrand_text"].lower() or "score" in dialogue["talleyrand_text"].lower() or "sire" in dialogue["talleyrand_text"].lower()

    def test_mission_generates_confirmation(self, world):
        from backend.game_logic.diplomatic_dialogue import generate_mission_dialogue
        dialogue = generate_mission_dialogue({
            "target_nation": "Austria",
            "mission_type": "IMPROVE_RELATIONS",
        }, world)
        assert dialogue["type"] == "mission"
        actions = [o["action"] for o in dialogue["options"]]
        assert "start_mission" in actions


# ═══════════════════════════════════════════════════════
# DIALOGUE BLOCKING
# ═══════════════════════════════════════════════════════

class TestDialogueBlocking:
    def test_hard_stop_dialogue_blocks_commands(self, executor, world, game_state):
        """PL-27: Only hard-stop dialogues block commands."""
        world.dialogue_manager.replace({
            "type": "alliance_paradox",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [{"label": "Honor", "action": "honor"}, {"label": "Break", "action": "side"}],
            "context": {},
            "turn_created": 1,
            "blocking": True,
        })
        parsed = {
            "success": True,
            "command": {"action": "attack", "marshal": "Ney", "target": "Belgium"},
        }
        result = executor.execute(parsed, game_state)
        assert not result["success"]
        assert "requires your attention" in result["message"].lower() or "talleyrand" in result["message"].lower() or "awaits" in result["message"].lower()

    def test_soft_stop_dialogue_allows_commands(self, executor, world, game_state):
        """PL-27: Soft-stop dialogues do not block commands."""
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [{"label": "Accept", "action": "accept_ai_proposal"}],
            "context": {},
            "turn_created": 1,
            "blocking": True,
        })
        parsed = {
            "success": True,
            "command": {"action": "status"},
        }
        result = executor.execute(parsed, game_state)
        # Soft-stop does not block — command proceeds normally
        assert result.get("awaiting_diplomatic_response") is not True

    def test_non_blocking_dialogue_auto_dismisses_on_end_turn(self, world):
        world.dialogue_manager.replace({
            "type": "proposal_options",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        # Simulate advance_turn where current_turn > turn_created
        world.current_turn = 2
        # The auto-dismiss happens in advance_turn
        if (world.pending_diplomatic_dialogue
                and not world.pending_diplomatic_dialogue.get("blocking")
                and world.pending_diplomatic_dialogue.get("turn_created", 0) < world.current_turn):
            world.dialogue_manager.pop()
        assert world.pending_diplomatic_dialogue is None

    def test_hard_stop_dialogue_prevents_end_turn(self, executor, world, game_state):
        """Only hard-stop dialogues (alliance_paradox, force_declare_war) block end-turn."""
        world.dialogue_manager.replace({
            "type": "alliance_paradox",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [],
            "context": {},
            "turn_created": 1,
            "blocking": True,
        })
        parsed = {
            "success": True,
            "command": {"action": "end_turn"},
        }
        result = executor.execute(parsed, game_state)
        assert not result["success"]


# ═══════════════════════════════════════════════════════
# PROPOSAL EXECUTION FLOW
# ═══════════════════════════════════════════════════════

class TestProposalExecution:
    def test_proposal_deducts_dp_and_sets_transit(self, executor, world, game_state):
        """Player picks execute_proposal → DP deducted, Talleyrand IN_TRANSIT."""
        world.diplomatic_points = 4
        world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "options": [{
                "label": "Send",
                "action": "execute_proposal",
                "terms": {
                    "proposal_type": "peace",
                    "target_nation": "Prussia",
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                },
            }],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"]
        assert world.talleyrand_state == "IN_TRANSIT"
        assert world.proposal_in_transit is not None
        assert world.proposal_in_transit["target"] == "Prussia"
        assert world.diplomatic_points < 4  # DP deducted
        assert world.pending_diplomatic_dialogue is None

    def test_proposal_resolves_next_turn(self, world):
        """Proposal in transit resolves when turn advances."""
        world.diplomatic_points = 4
        world.proposal_in_transit = {
            "target": "Saxony",
            "proposal": {
                "type": "open_borders",
                "proposer_nation": "France",
                "target_nation": "Saxony",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": 1,
        }
        world.talleyrand_state = "IN_TRANSIT"
        world.current_turn = 2  # Next turn

        events = world._process_proposal_in_transit()
        assert len(events) > 0
        assert world.proposal_in_transit is None
        assert world.talleyrand_state != "IN_TRANSIT"


# ═══════════════════════════════════════════════════════
# ACCEPTANCE INTEGRATION
# ═══════════════════════════════════════════════════════

class TestAcceptanceIntegration:
    def test_acceptance_formula_runs_on_resolve(self, world):
        """When proposal resolves, acceptance formula determines outcome."""
        # Set up a favorable scenario: Saxony has open borders, relation 40
        world.proposal_in_transit = {
            "target": "Saxony",
            "proposal": {
                "type": "non_aggression",
                "proposer_nation": "France",
                "target_nation": "Saxony",
                "sweeteners": [{"type": "gold_lump", "value": 500}],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": 1,
        }
        world.talleyrand_state = "IN_TRANSIT"
        world.current_turn = 2

        events = world._process_proposal_in_transit()
        assert len(events) > 0
        # Outcome should be in the event
        assert any("outcome" in e or "message" in e for e in events)

    def test_rejection_sets_cooldown(self, world):
        """REJECT sets cooldown."""
        # Set up hostile scenario: Prussia at war, bad relation
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "vassalage",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [{"type": "gold_per_turn", "value": 500}],
                "clauses": [],
            },
            "turn_sent": 1,
        }
        world.talleyrand_state = "IN_TRANSIT"
        world.current_turn = 2

        world._process_proposal_in_transit()
        # Should have cooldowns set
        cooldowns = world.player_proposal_cooldowns
        assert len(cooldowns) > 0


# ═══════════════════════════════════════════════════════
# TREATY RATIFICATION
# ═══════════════════════════════════════════════════════

class TestTreatyRatification:
    def test_treaty_signed_changes_diplomatic_state(self, world):
        """Treaty ratification changes the diplomatic state."""
        # Direct ratification test
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        event = world._ratify_treaty(proposal)
        assert event is not None
        # Should transition from WAR to PEACE
        state = world.get_diplomatic_state("France", "Prussia")
        assert state == "PEACE"

    def test_treaty_gold_lump_transfers(self, world):
        """Gold lump sum clause transfers gold immediately."""
        france_gold_before = world.nation_gold.get("France", 0)
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [{"type": "gold_lump", "value": 200}],
            "demands": [],
            "clauses": [],
        }
        world._ratify_treaty(proposal)
        france_gold_after = world.nation_gold.get("France", 0)
        assert france_gold_after == france_gold_before - 200

    def test_treaty_stored_in_active_treaties(self, world):
        """Treaty is stored in active_treaties."""
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        world._ratify_treaty(proposal)
        key = world._make_diplo_key("France", "Prussia")
        assert key in world.active_treaties


# ═══════════════════════════════════════════════════════
# PER-TURN TREATY CLAUSES
# ═══════════════════════════════════════════════════════

class TestTreatyClauses:
    def test_gold_per_turn_deducted(self, world):
        """Gold/turn clause applies during advance_turn."""
        key = world._make_diplo_key("France", "Prussia")
        world.active_treaties[key] = {
            "nations": ["France", "Prussia"],
            "type": "peace",
            "clauses": [
                {"type": "gold_per_turn", "from": "France", "to": "Prussia", "amount": 100},
            ],
            "turn_signed": 1,
            "harshness": 0.1,
        }
        france_before = world.nation_gold.get("France", 0)
        prussia_before = world.nation_gold.get("Prussia", 0)
        world._process_treaty_clauses()
        assert world.nation_gold["France"] == france_before - 100
        assert world.nation_gold["Prussia"] == prussia_before + 100

    def test_three_turn_accumulation(self, world):
        """Verify 3-turn gold/turn accumulation."""
        key = world._make_diplo_key("France", "Prussia")
        world.active_treaties[key] = {
            "nations": ["France", "Prussia"],
            "type": "peace",
            "clauses": [
                {"type": "gold_per_turn", "from": "France", "to": "Prussia", "amount": 50},
            ],
            "turn_signed": 1,
            "harshness": 0.05,
        }
        france_before = world.nation_gold.get("France", 0)
        for _ in range(3):
            world._process_treaty_clauses()
        assert world.nation_gold["France"] == france_before - 150


# ═══════════════════════════════════════════════════════
# TREATY BREAKING
# ═══════════════════════════════════════════════════════

class TestTreatyBreaking:
    def test_break_treaty_costs_dp(self, world):
        from backend.game_logic.diplomacy import break_treaty
        key = world._make_diplo_key("France", "Saxony")
        world.active_treaties[key] = {
            "nations": ["France", "Saxony"],
            "type": "open_borders",
            "clauses": [],
            "turn_signed": 1,
            "harshness": 0.0,
        }
        world.diplomatic_points = 4
        result = break_treaty(key, "France", world)
        assert result["success"]
        assert world.diplomatic_points == 3

    def test_break_treaty_relation_penalty(self, world):
        from backend.game_logic.diplomacy import break_treaty
        key = world._make_diplo_key("France", "Saxony")
        world.active_treaties[key] = {
            "nations": ["France", "Saxony"],
            "type": "open_borders",
            "clauses": [],
            "turn_signed": 1,
            "harshness": 0.0,
        }
        world.diplomatic_points = 4
        rel_before = world.nation_relations.get(key, 0)
        break_treaty(key, "France", world)
        rel_after = world.nation_relations.get(key, 0)
        assert rel_after < rel_before

    def test_break_treaty_insufficient_dp(self, world):
        from backend.game_logic.diplomacy import break_treaty
        key = world._make_diplo_key("France", "Saxony")
        world.active_treaties[key] = {"nations": ["France", "Saxony"], "type": "open_borders",
                                       "clauses": [], "turn_signed": 1, "harshness": 0.0}
        world.diplomatic_points = 0
        result = break_treaty(key, "France", world)
        assert not result["success"]


# ═══════════════════════════════════════════════════════
# FEASIBILITY
# ═══════════════════════════════════════════════════════

class TestFeasibility:
    def test_feasibility_returns_assessment(self, executor, world, game_state):
        parsed = {
            "success": True,
            "command": {
                "action": "diplomatic_feasibility",
                "diplomatic_data": {
                    "action": "diplomatic_feasibility",
                    "target_nation": "Prussia",
                    "proposal_type": "peace",
                    "has_diplomatic_keywords": True,
                    "is_question": True,
                    "raw_text": "what would it take to get peace with Prussia?",
                    "clauses": [],
                    "tone": "propose",
                },
            },
        }
        result = executor.execute(parsed, game_state)
        assert result["success"]
        assert "sire" in result["message"].lower() or "assessment" in result["message"].lower() or "score" in result["message"].lower()

    def test_feasibility_costs_zero_dp(self, executor, world, game_state):
        world.diplomatic_points = 4
        parsed = {
            "success": True,
            "command": {
                "action": "diplomatic_feasibility",
                "diplomatic_data": {
                    "action": "diplomatic_feasibility",
                    "target_nation": "Prussia",
                    "proposal_type": "peace",
                    "has_diplomatic_keywords": True,
                    "is_question": True,
                    "raw_text": "what would it take?",
                    "clauses": [],
                    "tone": "propose",
                },
            },
        }
        executor.execute(parsed, game_state)
        assert world.diplomatic_points == 4  # No DP spent


# ═══════════════════════════════════════════════════════
# MISSIONS
# ═══════════════════════════════════════════════════════

class TestMissions:
    def test_mission_start(self, executor, world, game_state):
        """Start a mission via dialogue response."""
        world.dialogue_manager.replace({
            "type": "mission",
            "target_nation": "Austria",
            "options": [{
                "label": "Begin mission",
                "action": "start_mission",
                "terms": {"mission_type": "IMPROVE_RELATIONS", "target_nation": "Austria"},
            }],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"]
        assert world.active_diplomatic_mission is not None
        assert world.active_diplomatic_mission["type"] == "IMPROVE_RELATIONS"
        assert world.talleyrand_state == "ON_MISSION"

    def test_mission_effects_improve_relations(self, world):
        """IMPROVE_RELATIONS mission improves relation each turn."""
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 0,
            "paused": False,
            "paused_turns": 0,
        }
        world.talleyrand_state = "ON_MISSION"
        key = world._make_diplo_key("France", "Austria")
        rel_before = world.nation_relations.get(key, 0)

        from backend.game_logic.diplomacy import _process_mission_effects
        _process_mission_effects(world)

        rel_after = world.nation_relations.get(key, 0)
        # Talleyrand skill 10 → 5 * 1.5 = 7.5 → 8
        assert rel_after == rel_before + 8

    def test_mission_skill_bonus(self, world):
        """Talleyrand skill 10 gives 1.5x multiplier."""
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 0,
            "paused": False,
            "paused_turns": 0,
        }
        key = world._make_diplo_key("France", "Austria")
        rel_before = world.nation_relations.get(key, 0)

        from backend.game_logic.diplomacy import _process_mission_effects
        _process_mission_effects(world)

        expected = int(round(5 * 1.5))  # 8
        assert world.nation_relations[key] == rel_before + expected

    def test_mission_dp_deduction(self, world):
        """Mission costs DP each turn."""
        world.diplomatic_points = 4
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 0,
            "paused": False,
            "paused_turns": 0,
        }
        from backend.game_logic.diplomacy import _process_mission_dp
        _process_mission_dp(world)
        assert world.diplomatic_points == 3
        assert world.active_diplomatic_mission["turns_active"] == 1

    def test_mission_paused_insufficient_dp(self, world):
        """Mission pauses when DP insufficient."""
        world.diplomatic_points = 0
        world.active_diplomatic_mission = {
            "type": "COURT_NATION",
            "target": "Austria",
            "turns_active": 0,
            "paused": False,
            "paused_turns": 0,
        }
        from backend.game_logic.diplomacy import _process_mission_dp
        events = _process_mission_dp(world)
        assert world.active_diplomatic_mission["paused"] is True
        assert len(events) > 0

    def test_mission_auto_cancel_after_3_paused_turns(self, world):
        """Mission auto-cancels after 3 consecutive paused turns."""
        world.diplomatic_points = 0
        world.active_diplomatic_mission = {
            "type": "COURT_NATION",
            "target": "Austria",
            "turns_active": 2,
            "paused": True,
            "paused_turns": 2,
        }
        world.talleyrand_state = "ON_MISSION"
        from backend.game_logic.diplomacy import _process_mission_dp
        _process_mission_dp(world)  # paused_turns becomes 3
        assert world.active_diplomatic_mission is None
        assert world.talleyrand_state == "IDLE"

    def test_mission_pause_on_proposal(self, executor, world, game_state):
        """Sending proposal while on mission pauses the mission."""
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 2,
            "paused": False,
            "paused_turns": 0,
        }
        world.talleyrand_state = "ON_MISSION"
        world.diplomatic_points = 4
        world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "options": [{
                "label": "Send",
                "action": "execute_proposal",
                "terms": {
                    "proposal_type": "peace",
                    "target_nation": "Prussia",
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                },
            }],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        executor.handle_diplomatic_dialogue_response(1, game_state)
        assert world.active_diplomatic_mission["paused"] is True
        assert world.talleyrand_state == "IN_TRANSIT"


# ═══════════════════════════════════════════════════════
# COOLDOWNS
# ═══════════════════════════════════════════════════════

class TestCooldowns:
    def test_cooldown_blocks_proposal(self, executor, world, game_state):
        world.player_proposal_cooldowns = {"Prussia": 3}
        parsed = {
            "success": True,
            "command": {
                "action": "diplomatic_proposal",
                "diplomatic_data": {
                    "action": "diplomatic_proposal",
                    "target_nation": "Prussia",
                    "proposal_type": "peace",
                    "has_diplomatic_keywords": True,
                    "is_question": False,
                    "raw_text": "propose peace with Prussia",
                    "clauses": [],
                    "tone": "propose",
                },
            },
        }
        result = executor.execute(parsed, game_state)
        assert not result["success"]
        assert "patience" in result["message"].lower()

    def test_cooldown_decrements(self, world):
        world.player_proposal_cooldowns = {"Prussia": 3, "Prussia_peace": 5}
        world._cooldown_manager.decrement_all()
        assert world.player_proposal_cooldowns["Prussia"] == 2
        assert world.player_proposal_cooldowns["Prussia_peace"] == 4

    def test_cooldown_expires(self, world):
        world.player_proposal_cooldowns = {"Prussia": 1}
        world._cooldown_manager.decrement_all()
        assert "Prussia" not in world.player_proposal_cooldowns


# ═══════════════════════════════════════════════════════
# TALLEYRAND IN-TRANSIT BLOCKING
# ═══════════════════════════════════════════════════════

class TestInTransitBlocking:
    def test_in_transit_blocks_proposals(self, executor, world, game_state):
        world.talleyrand_state = "IN_TRANSIT"
        parsed = {
            "success": True,
            "command": {
                "action": "diplomatic_proposal",
                "diplomatic_data": {
                    "action": "diplomatic_proposal",
                    "target_nation": "Austria",
                    "proposal_type": "peace",
                    "has_diplomatic_keywords": True,
                    "is_question": False,
                    "raw_text": "propose peace with Austria",
                    "clauses": [],
                    "tone": "propose",
                },
            },
        }
        result = executor.execute(parsed, game_state)
        assert not result["success"]
        assert "en route" in result["message"].lower() or "transit" in result["message"].lower()

    def test_in_transit_allows_feasibility(self, executor, world, game_state):
        """Feasibility checks work even while in transit."""
        world.talleyrand_state = "IN_TRANSIT"
        parsed = {
            "success": True,
            "command": {
                "action": "diplomatic_feasibility",
                "diplomatic_data": {
                    "action": "diplomatic_feasibility",
                    "target_nation": "Austria",
                    "proposal_type": "peace",
                    "has_diplomatic_keywords": True,
                    "is_question": True,
                    "raw_text": "what would it take?",
                    "clauses": [],
                    "tone": "propose",
                },
            },
        }
        result = executor.execute(parsed, game_state)
        assert result["success"]


# ═══════════════════════════════════════════════════════
# ENDPOINT TESTS
# ═══════════════════════════════════════════════════════

class TestEndpoint:
    def test_dialogue_response_by_index(self, executor, world, game_state):
        world.dialogue_manager.replace({
            "type": "proposal_options",
            "target_nation": "Prussia",
            "options": [
                {"label": "Option A", "action": "dismiss", "description": ""},
                {"label": "Option B", "action": "dismiss", "description": ""},
            ],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"]
        assert world.pending_diplomatic_dialogue is None

    def test_dialogue_response_invalid_index(self, executor, world, game_state):
        world.dialogue_manager.replace({
            "type": "proposal_options",
            "target_nation": "Prussia",
            "options": [{"label": "A", "action": "dismiss", "description": ""}],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        result = executor.handle_diplomatic_dialogue_response(5, game_state)
        assert not result["success"]

    def test_no_pending_dialogue(self, executor, world, game_state):
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert not result["success"]
        assert "no diplomatic" in result["message"].lower()

    def test_keyword_matching(self, executor, world, game_state):
        world.dialogue_manager.replace({
            "type": "proposal_options",
            "target_nation": "Prussia",
            "options": [
                {"label": "Send proposal", "action": "execute_proposal", "description": "",
                 "terms": {"proposal_type": "peace", "target_nation": "Prussia",
                           "sweeteners": [], "demands": [], "clauses": []}},
                {"label": "Dismiss", "action": "dismiss", "description": ""},
            ],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        world.diplomatic_points = 4
        result = executor.handle_diplomatic_dialogue_response("dismiss", game_state)
        assert result["success"]
        assert "very well" in result["message"].lower()


# ═══════════════════════════════════════════════════════
# SERIALIZATION
# ═══════════════════════════════════════════════════════

class TestSerialization:
    def test_pending_diplomatic_dialogue_roundtrip(self):
        world = WorldState(player_nation="France")
        world.dialogue_manager.replace({
            "type": "proposal_options",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [{"label": "A", "action": "dismiss"}],
            "context": {"war_score": 10},
            "turn_created": 1,
            "blocking": False,
        })
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.pending_diplomatic_dialogue is not None
        assert restored.pending_diplomatic_dialogue["target_nation"] == "Prussia"

    def test_active_mission_roundtrip(self):
        world = WorldState(player_nation="France")
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 3,
            "paused": False,
            "paused_turns": 0,
        }
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.active_diplomatic_mission is not None
        assert restored.active_diplomatic_mission["type"] == "IMPROVE_RELATIONS"

    def test_talleyrand_state_roundtrip(self):
        world = WorldState(player_nation="France")
        world.talleyrand_state = "ON_MISSION"
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.talleyrand_state == "ON_MISSION"

    def test_proposal_in_transit_roundtrip(self):
        world = WorldState(player_nation="France")
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {"type": "peace"},
            "turn_sent": 1,
        }
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.proposal_in_transit is not None
        assert restored.proposal_in_transit["target"] == "Prussia"

    def test_cooldowns_roundtrip(self):
        world = WorldState(player_nation="France")
        world.player_proposal_cooldowns = {"Prussia": 3, "Prussia_peace": 5}
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.player_proposal_cooldowns["Prussia"] == 3

    def test_active_treaties_roundtrip(self):
        world = WorldState(player_nation="France")
        key = world._make_diplo_key("France", "Saxony")
        world.active_treaties[key] = {
            "nations": ["France", "Saxony"],
            "type": "peace",
            "clauses": [],
            "turn_signed": 1,
            "harshness": 0.1,
        }
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert key in restored.active_treaties

    def test_backward_compat_no_session3_fields(self):
        """Old saves without Session 3 fields should load with defaults."""
        world = WorldState(player_nation="France")
        data = world.to_dict()
        # Remove Session 3 fields
        del data["pending_diplomatic_dialogue"]
        del data["active_diplomatic_mission"]
        del data["talleyrand_state"]
        del data["proposal_in_transit"]
        del data["player_proposal_cooldowns"]
        del data["active_treaties"]
        restored = WorldState.from_dict(data)
        assert restored.pending_diplomatic_dialogue is None
        assert restored.active_diplomatic_mission is None
        assert restored.talleyrand_state == "IDLE"
        assert restored.proposal_in_transit is None
        assert restored.player_proposal_cooldowns == {}
        assert restored.active_treaties == {}


# ═══════════════════════════════════════════════════════
# NO REGRESSION
# ═══════════════════════════════════════════════════════

class TestNoRegression:
    def test_ney_move_still_works(self, executor, game_state):
        parsed = {
            "success": True,
            "command": {"action": "move", "marshal": "Ney", "target": "Belgium"},
        }
        result = executor.execute(parsed, game_state)
        # Should at least not crash — may fail for game-state reasons but not parser/executor errors
        assert "message" in result

    def test_davout_attack_still_works(self, executor, game_state):
        parsed = {
            "success": True,
            "command": {"action": "attack", "marshal": "Davout", "target": "Rhineland"},
        }
        result = executor.execute(parsed, game_state)
        assert "message" in result

    def test_end_turn_still_works(self, executor, game_state):
        parsed = {
            "success": True,
            "command": {"action": "end_turn"},
        }
        result = executor.execute(parsed, game_state)
        assert result.get("success") is True

    def test_help_still_works(self, executor, game_state):
        parsed = {
            "success": True,
            "command": {"action": "help"},
        }
        result = executor.execute(parsed, game_state)
        assert result.get("success") is True

    def test_economy_still_works(self, executor, game_state):
        parsed = {
            "success": True,
            "command": {"action": "economy"},
        }
        result = executor.execute(parsed, game_state)
        assert result.get("success") is True


# ═══════════════════════════════════════════════════════
# GAME BUCKET TESTS
# ═══════════════════════════════════════════════════════

class TestGameBucket:
    def test_war_winning_comfortably(self, world):
        from backend.game_logic.diplomatic_dialogue import get_game_bucket
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 40
        bucket = get_game_bucket("Prussia", world)
        assert bucket == "winning_comfortably"

    def test_war_stalemate(self, world):
        from backend.game_logic.diplomatic_dialogue import get_game_bucket
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 0
        bucket = get_game_bucket("Prussia", world)
        assert bucket == "stalemate"

    def test_peace_friendly(self, world):
        from backend.game_logic.diplomatic_dialogue import get_game_bucket
        key = world._make_diplo_key("France", "Saxony")
        world.nation_relations[key] = 40
        bucket = get_game_bucket("Saxony", world)
        assert bucket == "friendly"

    def test_peace_hostile(self, world):
        from backend.game_logic.diplomatic_dialogue import get_game_bucket
        key = world._make_diplo_key("France", "Austria")
        world.nation_relations[key] = -30
        bucket = get_game_bucket("Austria", world)
        assert bucket == "hostile"


# ═══════════════════════════════════════════════════════
# TEMPLATE TESTS
# ═══════════════════════════════════════════════════════

class TestTemplates:
    def test_template_slot_resolution(self, world):
        from backend.game_logic.diplomatic_templates import resolve_template_text
        text = "Relations with {target_nation}: {relation}. War score: {war_score}."
        resolved = resolve_template_text(text, world, "Prussia")
        assert "Prussia" in resolved
        assert "{target_nation}" not in resolved

    def test_suggested_terms_peace(self, world):
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        terms = generate_suggested_terms("Prussia", "peace", world)
        assert terms["type"] == "peace"
        assert terms["proposer_nation"] == "France"
        assert terms["target_nation"] == "Prussia"

    def test_suggested_terms_vassalage(self, world):
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        terms = generate_suggested_terms("Saxony", "vassalage", world)
        assert terms["type"] == "vassalage"
        assert len(terms["demands"]) > 0

    def test_treaty_harshness_calculation(self):
        from backend.game_logic.diplomatic_templates import calculate_treaty_harshness
        treaty = {"clauses": [
            {"type": "gold_per_turn", "amount": 200},
            {"type": "territory_cede", "regions": ["Saxony", "Bavaria"]},
        ]}
        harshness = calculate_treaty_harshness(treaty)
        assert 0.0 < harshness <= 1.0

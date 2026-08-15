"""
Phase 4 Batch 1: Parser & LLM Robustness + War Declaration + Ultimatums
Tests for R10, R21, R93, LLM prompt guidance, and parser collision prevention.
"""

import pytest
from backend.ai.llm_client import LLMClient
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ═══════ FIXTURES ═══════

@pytest.fixture
def client():
    return LLMClient(use_real_api=False)


@pytest.fixture
def world():
    return WorldState()


@pytest.fixture
def executor():
    return CommandExecutor()


@pytest.fixture
def game_state(world):
    return {"world": world}


# ═══════ 1A: WAR DECLARATION COMMAND (R10) ═══════

class TestWarDeclaration:
    """R10: Player can declare war via command."""

    def test_declare_war_parses(self, client):
        result = client.parse_command("declare war on Prussia")
        assert result["action"] == "diplomatic_declare_war"

    def test_declare_war_against_parses(self, client):
        result = client.parse_command("declare war against Austria")
        assert result["action"] == "diplomatic_declare_war"

    def test_go_to_war_parses(self, client):
        result = client.parse_command("go to war with Britain")
        assert result["action"] == "diplomatic_declare_war"

    def test_open_hostilities_parses(self, client):
        result = client.parse_command("open hostilities with Prussia")
        assert result["action"] == "diplomatic_declare_war"

    def test_declare_war_extracts_nation(self, client):
        result = client.parse_command("declare war on Prussia")
        diplo_data = result.get("diplomatic_data", {})
        assert diplo_data.get("target_nation") == "Prussia"

    def test_declare_war_executor_success(self, executor, world, game_state):
        """War declaration via executor succeeds and costs 1 DP."""
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "PEACE"
        initial_dp = world.diplomatic_points
        command = {
            "action": "diplomatic_declare_war",
            "diplomatic_data": {
                "action": "diplomatic_declare_war",
                "target_nation": "Austria",
                "war_objective": "conquest",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert result.get("success"), result.get("message")
        assert world.diplomatic_points == initial_dp - 1

    def test_declare_war_already_at_war(self, executor, world, game_state):
        """Cannot declare war if already at war."""
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        command = {
            "action": "diplomatic_declare_war",
            "diplomatic_data": {
                "action": "diplomatic_declare_war",
                "target_nation": "Prussia",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert not result.get("success")
        assert "already at war" in result.get("message", "").lower()

    def test_declare_war_insufficient_dp(self, executor, world, game_state):
        """Cannot declare war with 0 DP."""
        world.diplomatic_points = 0
        command = {
            "action": "diplomatic_declare_war",
            "diplomatic_data": {
                "action": "diplomatic_declare_war",
                "target_nation": "Austria",
                "war_objective": "conquest",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert not result.get("success")
        # PC15-D1(c): the refusal is now the visible-receipt copy
        # ("the declaration cannot be sent … the chancery holds 0").
        msg = result.get("message", "").lower()
        assert "cannot be sent" in msg
        assert "diplomatic point" in msg

    def test_declare_war_high_threat_objection(self, executor, world, game_state):
        """Talleyrand objects when threat > 50."""
        world.threat_level = 60
        command = {
            "action": "diplomatic_declare_war",
            "diplomatic_data": {
                "action": "diplomatic_declare_war",
                "target_nation": "Austria",
                "war_objective": "conquest",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        # Should succeed but include objection popup
        assert result.get("success")
        assert world.diplomatic_objection_popup is not None
        assert world.diplomatic_objection_popup["concern_level"] == "STRONG"

    def test_declare_war_trust_reactions(self, executor, world, game_state):
        """R23: Aggressive marshals gain trust, cautious lose trust."""
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        initial_ney_trust = ney.trust.value
        initial_davout_trust = davout.trust.value

        diplomatic_data = {
            "action": "diplomatic_declare_war",
            "target_nation": "Austria",
            "war_objective": "conquest",
        }
        executor._execute_diplomatic_declare_war(diplomatic_data, world)
        # Ney is aggressive -> +3
        assert ney.trust.value == initial_ney_trust + 3
        # Davout is cautious -> -3
        assert davout.trust.value == initial_davout_trust - 3

    def test_declare_war_casus_belli_halves_penalties(self, world):
        """Casus belli from ultimatum rejection halves war penalties."""
        from backend.game_logic.diplomacy import declare_war
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "PEACE"
        initial_relation = world.nation_relations.get(world._make_diplo_key("France", "Austria"), 0)

        # Normal war: -30
        result = declare_war(world, "France", "Austria", casus_belli=False)
        assert result["success"]
        normal_delta = world.nation_relations.get(world._make_diplo_key("France", "Austria"), 0) - initial_relation

        # Reset
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "PEACE"
        world.modify_nation_relation("France", "Austria", -normal_delta)  # undo

        # With casus belli: -15 (halved)
        result2 = declare_war(world, "France", "Austria", casus_belli=True)
        assert result2["success"]
        cb_delta = world.nation_relations.get(world._make_diplo_key("France", "Austria"), 0) - initial_relation
        assert abs(cb_delta) < abs(normal_delta)

    def test_declare_war_no_target_asks(self, executor, world, game_state):
        """War declaration without target nation asks the player."""
        command = {
            "action": "diplomatic_declare_war",
            "diplomatic_data": {
                "action": "diplomatic_declare_war",
                "target_nation": None,
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert not result.get("success")
        assert "which nation" in result.get("message", "").lower()


# ═══════ 1B: ULTIMATUM COMMAND (R21) ═══════

class TestUltimatum:
    """R21: Player can issue ultimatums."""

    def test_ultimatum_parses(self, client):
        result = client.parse_command("ultimatum to Britain")
        assert result["action"] == "diplomatic_ultimatum"

    def test_issue_ultimatum_parses(self, client):
        result = client.parse_command("issue ultimatum to Prussia")
        assert result["action"] == "diplomatic_ultimatum"

    def test_final_offer_parses(self, client):
        result = client.parse_command("final offer to Austria")
        assert result["action"] == "diplomatic_ultimatum"

    def test_demand_surrender_parses(self, client):
        """'demand surrender' contains 'demand' but also context for ultimatum."""
        result = client.parse_command("Talleyrand, demand surrender from Prussia")
        # "demand surrender" matches the "demand" keyword which routes to proposal w/ tone=demand
        # But if in the future we add "demand surrender" as ultimatum keyword, change this test
        assert result["action"] in ("diplomatic_proposal", "diplomatic_ultimatum")

    def test_demand_without_ultimatum_is_proposal(self, client):
        """R21: 'demand' alone -> diplomatic_proposal with tone=demand, not ultimatum."""
        result = client.parse_command("Talleyrand, demand peace from Prussia")
        assert result["action"] == "diplomatic_proposal"

    def test_ultimatum_pushes_dialogue(self, executor, world, game_state):
        """PL-14: Ultimatum pushes dialogue (DP deferred to delivery)."""
        initial_dp = world.diplomatic_points
        diplomatic_data = {
            "action": "diplomatic_ultimatum",
            "target_nation": "Austria",
        }
        result = executor._execute_diplomatic_ultimatum(diplomatic_data, world)
        assert result.get("success"), result.get("message")
        assert result.get("awaiting_diplomatic_response") is True
        # DP not deducted yet
        assert world.diplomatic_points == initial_dp

    def test_ultimatum_insufficient_dp(self, executor, world, game_state):
        """Cannot issue ultimatum with < 2 DP."""
        world.diplomatic_points = 1
        command = {
            "action": "diplomatic_ultimatum",
            "diplomatic_data": {
                "action": "diplomatic_ultimatum",
                "target_nation": "Austria",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert not result.get("success")

    def test_ultimatum_dialogue_has_acceptance(self, executor, world, game_state):
        """PL-14: Ultimatum dialogue has acceptance estimate."""
        diplomatic_data = {
            "action": "diplomatic_ultimatum",
            "target_nation": "Austria",
        }
        result = executor._execute_diplomatic_ultimatum(diplomatic_data, world)
        dialogue = world.pending_diplomatic_dialogue
        assert "acceptance_estimate" in dialogue
        assert "dp_cost" in dialogue
        assert dialogue["harshness_label"] == "Coercive"

    def test_ultimatum_dialogue_has_terms(self, executor, world, game_state):
        """PL-14: Ultimatum dialogue contains demands (no sweeteners)."""
        diplomatic_data = {
            "action": "diplomatic_ultimatum",
            "target_nation": "Austria",
        }
        executor._execute_diplomatic_ultimatum(diplomatic_data, world)
        dialogue = world.pending_diplomatic_dialogue
        terms = dialogue.get("terms", {})
        assert len(terms.get("demands", [])) > 0
        assert terms.get("sweeteners", []) == []
        assert terms.get("type") == "ultimatum_demand"

    def test_ultimatum_no_target_asks(self, executor, world, game_state):
        """Ultimatum without target nation asks."""
        command = {
            "action": "diplomatic_ultimatum",
            "diplomatic_data": {
                "action": "diplomatic_ultimatum",
                "target_nation": None,
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert not result.get("success")
        assert "which nation" in result.get("message", "").lower()

    def test_ultimatum_at_war_fails(self, executor, world, game_state):
        """Cannot issue ultimatum to nation already at war."""
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        diplomatic_data = {
            "action": "diplomatic_ultimatum",
            "target_nation": "Prussia",
        }
        result = executor._execute_diplomatic_ultimatum(diplomatic_data, world)
        assert not result.get("success")
        assert "peace proposal" in result.get("message", "").lower() or "already at war" in result.get("message", "").lower()

    def test_ultimatum_dialogue_options(self, executor, world, game_state):
        """PL-15: Dialogue has [Customize] [Use Suggested] [Reconsider] options."""
        diplomatic_data = {
            "action": "diplomatic_ultimatum",
            "target_nation": "Austria",
        }
        executor._execute_diplomatic_ultimatum(diplomatic_data, world)
        dialogue = world.pending_diplomatic_dialogue
        actions = [o["action"] for o in dialogue.get("options", [])]
        assert "execute_ultimatum" in actions
        assert "ultimatum_customize" in actions
        assert "reconsider" in actions


# ═══════ 1C: LLM PROMPT DIPLOMATIC GUIDANCE ═══════

class TestLLMPromptGuidance:
    """LLM prompt builder includes diplomatic section."""

    def test_prompt_contains_diplomatic_section(self):
        from backend.ai.prompt_builder import build_parse_prompt
        game_state = {
            "marshals": {"Ney": {"location": "Paris", "strength": 50000}},
            "enemies": {},
            "map_data": {"Paris": {}},
        }
        prompt = build_parse_prompt("declare war on Prussia", game_state)
        assert "Diplomatic Commands" in prompt
        assert "diplomatic_declare_war" in prompt
        assert "diplomatic_ultimatum" in prompt

    def test_prompt_disambiguates_military_vs_diplomatic(self):
        from backend.ai.prompt_builder import build_parse_prompt
        game_state = {
            "marshals": {"Ney": {"location": "Paris", "strength": 50000}},
            "enemies": {},
            "map_data": {"Paris": {}},
        }
        prompt = build_parse_prompt("declare war on Prussia", game_state)
        assert "MILITARY" in prompt  # Military vs diplomatic distinction
        assert "NOT diplomatic" in prompt


# ═══════ 1D: DYNAMIC KNOWN_NATIONS (R93) ═══════

class TestDynamicKnownNations:
    """R93: Known nations includes vassals."""

    def test_base_nations(self):
        from backend.game_logic.diplomatic_dialogue import get_known_nations
        nations = get_known_nations()
        assert "Britain" in nations
        assert "Prussia" in nations
        assert "Austria" in nations
        assert "Saxony" in nations

    def test_includes_vassals(self, world):
        from backend.game_logic.diplomatic_dialogue import get_known_nations
        world.vassals["Bavaria"] = {"name": "Bavaria", "loyalty": 50}
        nations = get_known_nations(world)
        assert "Bavaria" in nations

    def test_executor_accepts_vassal_nation(self, executor, world, game_state):
        """Executor doesn't reject vassal names as unknown nations (R93)."""
        world.vassals["Bavaria"] = {"name": "Bavaria", "loyalty": 50}
        command = {
            "action": "diplomatic_proposal",
            "diplomatic_data": {
                "action": "diplomatic_proposal",
                "target_nation": "Bavaria",
                "proposal_type": "alliance",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        # Should not get "not aware of a nation" error
        msg = result.get("message", "")
        assert "not aware of a nation" not in msg


# ═══════ 1E: PARSER COLLISION TESTS ═══════

class TestParserCollisions:
    """Ensure diplomatic and military commands don't cross-contaminate."""

    def test_declare_war_is_diplomatic(self, client):
        result = client.parse_command("declare war on Prussia")
        assert result["action"] == "diplomatic_declare_war"

    def test_ney_attack_prussians_is_military(self, client):
        """'Ney, attack the Prussians' must be military, NOT diplomatic."""
        result = client.parse_command("Ney, attack the Prussians")
        assert result["action"] == "attack"
        assert result.get("marshal") == "Ney" or "Ney" in result.get("marshals", [])

    def test_how_is_war_going_not_diplomatic(self, client):
        """'how is the war going' must NOT route to diplomatic (bare 'war' safe)."""
        result = client.parse_command("how is the war going")
        assert result["action"] != "diplomatic_declare_war"

    def test_ultimatum_to_britain(self, client):
        result = client.parse_command("ultimatum to Britain")
        assert result["action"] == "diplomatic_ultimatum"

    def test_break_treaty_is_diplomatic(self, client):
        result = client.parse_command("break treaty with Austria")
        assert result["action"] == "diplomatic_break"

    def test_break_through_enemy_lines_is_military(self, client):
        """'break through enemy lines' must NOT be misread as treaty break."""
        result = client.parse_command("break through enemy lines")
        # Should NOT be diplomatic_break
        assert result["action"] != "diplomatic_break"

    def test_march_to_war_is_military(self, client):
        """'march to war' must be move, not diplomatic."""
        result = client.parse_command("march to war")
        assert result["action"] in ("move", "unknown")
        assert result["action"] != "diplomatic_declare_war"

    def test_talleyrand_attack_is_error(self, client):
        """Military command to Talleyrand should give diplomatic_error."""
        result = client.parse_command("Talleyrand, attack Prussia")
        assert result["action"] == "diplomatic_error"

    def test_demand_peace_is_proposal_not_ultimatum(self, client):
        """'demand peace' is proposal with tone=demand, not ultimatum."""
        result = client.parse_command("Talleyrand, demand peace from Prussia")
        assert result["action"] == "diplomatic_proposal"
        diplo_data = result.get("diplomatic_data", {})
        assert diplo_data.get("tone") == "demand"

    def test_war_on_with_space_prevents_warden(self, client):
        """'war on ' keyword has trailing space to prevent matching 'warden'."""
        result = client.parse_command("the warden watches")
        assert result["action"] != "diplomatic_declare_war"

    def test_war_against_with_space_prevents_warning(self, client):
        """'war against ' keyword has trailing space for safety."""
        result = client.parse_command("warning about the front")
        assert result["action"] != "diplomatic_declare_war"

    def test_go_to_war_with_nation(self, client):
        result = client.parse_command("go to war with Austria")
        assert result["action"] == "diplomatic_declare_war"

    def test_declare_hostilities(self, client):
        result = client.parse_command("declare hostilities against Britain")
        assert result["action"] == "diplomatic_declare_war"

    def test_give_ultimatum(self, client):
        result = client.parse_command("give ultimatum to Prussia")
        assert result["action"] == "diplomatic_ultimatum"

    def test_submit_or_face_war(self, client):
        result = client.parse_command("submit or face war, Austria")
        assert result["action"] == "diplomatic_ultimatum"

    def test_insist_is_proposal_demand_not_ultimatum(self, client):
        """'insist' alone is proposal with demand tone, not ultimatum."""
        result = client.parse_command("Talleyrand, insist on alliance with Austria")
        assert result["action"] == "diplomatic_proposal"

    def test_require_is_proposal_demand_not_ultimatum(self, client):
        """'require' alone is proposal with demand tone, not ultimatum."""
        result = client.parse_command("Talleyrand, require peace from Prussia")
        assert result["action"] == "diplomatic_proposal"


# ═══════ SERIALIZATION ═══════

class TestPhase4Serialization:
    """New fields must serialize correctly."""

    def test_casus_belli_serializes(self, world):
        world.casus_belli["France|Austria"] = True
        data = world.to_dict()
        assert data["casus_belli"] == {"France|Austria": True}
        restored = WorldState.from_dict(data)
        assert restored.casus_belli == {"France|Austria": True}

    def test_diplomatic_history_serializes(self, world):
        world.diplomatic_history = [{"turn": 1, "type": "war", "target": "Prussia"}]
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert len(restored.diplomatic_history) == 1
        assert restored.diplomatic_history[0]["type"] == "war"

    def test_diplomatic_reliability_serializes(self, world):
        world.diplomatic_reliability["Austria"] = 15
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.diplomatic_reliability["Austria"] == 15

    def test_commitment_paradox_popup_serializes(self, world):
        world.commitment_paradox_popup = {"type": "test"}
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.commitment_paradox_popup == {"type": "test"}

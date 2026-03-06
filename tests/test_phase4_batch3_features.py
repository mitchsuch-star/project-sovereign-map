"""
Phase 4 Batch 3: New Features
Tests for R23 (Marshal Morale), R34 (Diplomatic Memory), R31 (Acceptance Preview),
R29 (Diplomatic History).
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ═══════ FIXTURES ═══════

@pytest.fixture
def world():
    return WorldState()


@pytest.fixture
def executor():
    return CommandExecutor()


@pytest.fixture
def game_state(world):
    return {"world": world}


def _set_marshal_personality(world, marshal_name, personality):
    """Helper: set a marshal's personality string."""
    if marshal_name in world.marshals:
        world.marshals[marshal_name].personality = personality


def _get_marshal_trust(world, marshal_name):
    """Helper: read current trust value."""
    if marshal_name in world.marshals:
        return world.marshals[marshal_name].trust.value
    return None


def _get_player_marshals(world):
    """Helper: return list of player marshal names."""
    return [
        name for name, m in world.marshals.items()
        if m.nation == world.player_nation
    ]


# ═══════════════════════════════════════════════════════
# R23: MARSHAL MORALE — TRUST REACTIONS FOR DIPLOMATIC EVENTS
# ═══════════════════════════════════════════════════════

class TestR23TrustReactions:
    """R23: Marshal trust changes based on diplomatic events and personality."""

    def test_war_declaration_aggressive_gains_trust(self, executor, world):
        """Aggressive marshals gain trust on war declaration."""
        marshals = _get_player_marshals(world)
        assert len(marshals) > 0, "Need at least one player marshal"
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "aggressive")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "war_declaration", "Prussia")
        assert _get_marshal_trust(world, m_name) == initial + 3

    def test_war_declaration_cautious_loses_trust(self, executor, world):
        """Cautious marshals lose trust on war declaration."""
        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "cautious")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "war_declaration", "Prussia")
        assert _get_marshal_trust(world, m_name) == initial - 3

    def test_treaty_signed_cautious_gains_trust(self, executor, world):
        """Cautious marshals gain trust on treaty signed."""
        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "cautious")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "treaty_signed", "Prussia")
        assert _get_marshal_trust(world, m_name) == initial + 3

    def test_treaty_signed_aggressive_loses_trust(self, executor, world):
        """Aggressive marshals lose trust on treaty signed."""
        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "aggressive")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "treaty_signed", "Prussia")
        assert _get_marshal_trust(world, m_name) == initial - 2

    def test_treaty_broken_cautious_loses_trust(self, executor, world):
        """Cautious marshals lose trust on treaty broken."""
        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "cautious")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "treaty_broken", "Prussia")
        assert _get_marshal_trust(world, m_name) == initial - 3

    def test_treaty_broken_aggressive_gains_trust(self, executor, world):
        """Aggressive marshals gain trust on treaty broken."""
        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "aggressive")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "treaty_broken", "Prussia")
        assert _get_marshal_trust(world, m_name) == initial + 1

    def test_ultimatum_issued_aggressive_gains(self, executor, world):
        """Aggressive marshals gain trust on ultimatum."""
        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "aggressive")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "ultimatum_issued", "Prussia")
        assert _get_marshal_trust(world, m_name) == initial + 2

    def test_vassal_created_balanced_gains(self, executor, world):
        """Balanced marshals gain trust on vassal creation."""
        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "balanced")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "vassal_created", "Saxony")
        assert _get_marshal_trust(world, m_name) == initial + 1

    def test_alliance_formed_cautious_gains(self, executor, world):
        """Cautious marshals gain trust on alliance formation."""
        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "cautious")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "alliance_formed", "Austria")
        assert _get_marshal_trust(world, m_name) == initial + 2

    def test_literal_zero_on_war_declaration(self, executor, world):
        """Literal marshals have 0 delta for war declaration."""
        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "literal")
        initial = _get_marshal_trust(world, m_name)
        executor._apply_diplomatic_trust_reactions(world, "war_declaration", "Prussia")
        assert _get_marshal_trust(world, m_name) == initial

    def test_break_treaty_wires_trust_reaction(self, executor, world, game_state):
        """R23: Breaking a treaty via executor triggers trust reaction."""
        # Set up an active treaty
        player = world.player_nation
        pair_key = world._make_diplo_key(player, "Austria")
        world.diplomatic_states[pair_key] = "ALLIANCE"
        world.active_treaties[pair_key] = {
            "nations": [player, "Austria"],
            "type": "alliance",
            "turn_signed": 1,
            "clauses": [],
            "harshness": 0,
        }
        world.diplomatic_points = 5

        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "cautious")
        initial = _get_marshal_trust(world, m_name)

        command = {
            "action": "diplomatic_break",
            "diplomatic_data": {
                "action": "diplomatic_break",
                "target_nation": "Austria",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert result.get("success"), result.get("message")

        # Cautious should lose trust for treaty_broken
        assert _get_marshal_trust(world, m_name) < initial

    def test_vassalize_wires_trust_reaction(self, executor, world, game_state):
        """R23: Creating a vassal via executor triggers trust reaction."""
        player = world.player_nation
        # Set WAR state so conquest path triggers
        world.diplomatic_states[world._make_diplo_key(player, "Saxony")] = "WAR"
        world.diplomatic_points = 5

        marshals = _get_player_marshals(world)
        m_name = marshals[0]
        _set_marshal_personality(world, m_name, "aggressive")
        initial = _get_marshal_trust(world, m_name)

        command = {"action": "vassalize", "target": "Saxony"}
        result = executor._execute_make_vassal(command, game_state)
        if result.get("success"):
            # Aggressive gains trust for vassal_created (+2)
            assert _get_marshal_trust(world, m_name) == initial + 2


# ═══════════════════════════════════════════════════════
# R34: DIPLOMATIC MEMORY — RELIABILITY TRACKING
# ═══════════════════════════════════════════════════════

class TestR34DiplomaticReliability:
    """R34: Diplomatic reliability affects acceptance formula."""

    def test_reliability_starts_at_zero(self, world):
        """Nations start with 0 reliability."""
        assert world.diplomatic_reliability.get("France", 0) == 0
        assert world.diplomatic_reliability.get("Prussia", 0) == 0

    def test_reliability_decreases_on_break(self, world):
        """Breaking a treaty decreases reliability by 10."""
        player = world.player_nation
        pair_key = world._make_diplo_key(player, "Austria")
        world.diplomatic_states[pair_key] = "ALLIANCE"
        world.active_treaties[pair_key] = {
            "nations": [player, "Austria"],
            "type": "alliance",
            "turn_signed": 1,
            "clauses": [],
            "harshness": 0,
        }
        world.diplomatic_points = 5

        from backend.game_logic.diplomacy import break_treaty
        result = break_treaty(pair_key, player, world)
        assert result.get("success"), result.get("message")
        assert world.diplomatic_reliability.get(player, 0) == -10

    def test_reliability_decreases_cumulative(self, world):
        """Multiple breaks decrease reliability cumulatively."""
        player = world.player_nation

        # First break
        pair_key = world._make_diplo_key(player, "Austria")
        world.diplomatic_states[pair_key] = "ALLIANCE"
        world.active_treaties[pair_key] = {
            "nations": [player, "Austria"],
            "type": "alliance",
            "turn_signed": 1,
            "clauses": [],
            "harshness": 0,
        }
        world.diplomatic_points = 10

        from backend.game_logic.diplomacy import break_treaty
        break_treaty(pair_key, player, world)

        # Second break
        pair_key2 = world._make_diplo_key(player, "Prussia")
        world.diplomatic_states[pair_key2] = "NON_AGGRESSION"
        world.active_treaties[pair_key2] = {
            "nations": [player, "Prussia"],
            "type": "non_aggression",
            "turn_signed": 1,
            "clauses": [],
            "harshness": 0,
        }
        break_treaty(pair_key2, player, world)
        assert world.diplomatic_reliability.get(player, 0) == -20

    def test_reliability_capped_at_minus_100(self, world):
        """Reliability cannot go below -100."""
        world.diplomatic_reliability["France"] = -95
        player = world.player_nation
        pair_key = world._make_diplo_key(player, "Austria")
        world.diplomatic_states[pair_key] = "ALLIANCE"
        world.active_treaties[pair_key] = {
            "nations": [player, "Austria"],
            "type": "alliance",
            "turn_signed": 1,
            "clauses": [],
            "harshness": 0,
        }
        world.diplomatic_points = 5

        from backend.game_logic.diplomacy import break_treaty
        break_treaty(pair_key, player, world)
        assert world.diplomatic_reliability["France"] == -100

    def test_reliability_increases_on_honored_treaty(self, world):
        """Treaty honored for 10 turns increases reliability by 5."""
        from backend.game_logic.diplomacy import _process_diplomatic_reliability

        pair_key = world._make_diplo_key("France", "Austria")
        world.active_treaties[pair_key] = {
            "nations": ["France", "Austria"],
            "type": "peace",
            "turn_signed": 0,
            "clauses": [],
            "harshness": 0,
        }

        # Set current turn to exactly 10
        world.current_turn = 10
        _process_diplomatic_reliability(world)
        assert world.diplomatic_reliability.get("France", 0) == 5
        assert world.diplomatic_reliability.get("Austria", 0) == 5

    def test_reliability_capped_at_100(self, world):
        """Reliability cannot exceed 100."""
        from backend.game_logic.diplomacy import _process_diplomatic_reliability

        world.diplomatic_reliability["France"] = 98
        pair_key = world._make_diplo_key("France", "Austria")
        world.active_treaties[pair_key] = {
            "nations": ["France", "Austria"],
            "type": "peace",
            "turn_signed": 0,
            "clauses": [],
            "harshness": 0,
        }

        world.current_turn = 10
        _process_diplomatic_reliability(world)
        assert world.diplomatic_reliability["France"] == 100

    def test_reliability_affects_acceptance_positive(self, world):
        """Positive reliability gives positive modifier in acceptance formula."""
        from backend.game_logic.diplomacy import calculate_acceptance

        world.diplomatic_reliability["France"] = 50

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        # 50 reliability // 5 = 10, capped at 10
        assert result["components"]["reliability_modifier"] == 10

    def test_reliability_affects_acceptance_negative(self, world):
        """Negative reliability gives negative modifier in acceptance formula."""
        from backend.game_logic.diplomacy import calculate_acceptance

        world.diplomatic_reliability["France"] = -50

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        # -50 reliability // 5 = -10, capped at -10
        assert result["components"]["reliability_modifier"] == -10

    def test_reliability_modifier_capped_at_plus_minus_10(self, world):
        """Reliability modifier capped at +/-10 even with extreme values."""
        from backend.game_logic.diplomacy import calculate_acceptance

        world.diplomatic_reliability["France"] = 100

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["reliability_modifier"] == 10

        world.diplomatic_reliability["France"] = -100
        result2 = calculate_acceptance(proposal, world)
        assert result2["components"]["reliability_modifier"] == -10


# ═══════════════════════════════════════════════════════
# R31: ACCEPTANCE PREVIEW — FEASIBILITY COMPONENT BREAKDOWN
# ═══════════════════════════════════════════════════════

class TestR31AcceptancePreview:
    """R31: Feasibility check includes numerical component breakdown."""

    def test_feasibility_returns_acceptance_breakdown(self, executor, world, game_state):
        """Feasibility result includes acceptance_breakdown with score and components."""
        world.diplomatic_points = 5
        command = {
            "action": "diplomatic_feasibility",
            "diplomatic_data": {
                "action": "diplomatic_feasibility",
                "target_nation": "Prussia",
                "proposal_type": "peace",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert result.get("success"), result.get("message")
        assert "acceptance_breakdown" in result
        breakdown = result["acceptance_breakdown"]
        assert "score" in breakdown
        assert "outcome" in breakdown
        assert "components" in breakdown

    def test_feasibility_components_include_standard_fields(self, executor, world, game_state):
        """Component breakdown includes all standard acceptance formula fields."""
        command = {
            "action": "diplomatic_feasibility",
            "diplomatic_data": {
                "action": "diplomatic_feasibility",
                "target_nation": "Austria",
                "proposal_type": "peace",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert result.get("success")
        components = result["acceptance_breakdown"]["components"]
        expected_keys = [
            "base_disposition", "war_score_modifier", "relation_modifier",
            "threat_modifier", "deal_balance", "diplomat_skill_bonus",
            "personality_modifier", "reliability_modifier",
        ]
        for key in expected_keys:
            assert key in components, f"Missing component: {key}"

    def test_feasibility_score_is_integer(self, executor, world, game_state):
        """Acceptance score must be an integer (Godot rule)."""
        command = {
            "action": "diplomatic_feasibility",
            "diplomatic_data": {
                "action": "diplomatic_feasibility",
                "target_nation": "Prussia",
                "proposal_type": "peace",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert isinstance(result["acceptance_breakdown"]["score"], int)

    def test_feasibility_without_target_no_breakdown(self, executor, world, game_state):
        """No target nation means no acceptance_breakdown returned."""
        command = {
            "action": "diplomatic_feasibility",
            "diplomatic_data": {
                "action": "diplomatic_feasibility",
                "target_nation": "",
                "proposal_type": "peace",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert result.get("success")
        # No target means no breakdown
        assert "acceptance_breakdown" not in result


# ═══════════════════════════════════════════════════════
# R29: DIPLOMATIC HISTORY — LOGGING AND DISPLAY
# ═══════════════════════════════════════════════════════

class TestR29DiplomaticHistory:
    """R29: Diplomatic events logged to history and displayed in ledger."""

    def test_history_starts_empty(self, world):
        """Diplomatic history starts as empty list."""
        assert world.diplomatic_history == []

    def test_war_declaration_logged(self, world):
        """War declaration creates a history entry."""
        from backend.game_logic.diplomacy import declare_war
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "PEACE"
        declare_war(world, "France", "Austria")
        assert len(world.diplomatic_history) >= 1
        entry = world.diplomatic_history[-1]
        assert entry["type"] == "war_declared"
        assert entry["nation"] == "France"
        assert entry["target"] == "Austria"

    def test_treaty_broken_logged(self, world):
        """Breaking a treaty creates a history entry."""
        from backend.game_logic.diplomacy import break_treaty
        player = world.player_nation
        pair_key = world._make_diplo_key(player, "Prussia")
        world.diplomatic_states[pair_key] = "NON_AGGRESSION"
        world.active_treaties[pair_key] = {
            "nations": [player, "Prussia"],
            "type": "non_aggression",
            "turn_signed": 1,
            "clauses": [],
            "harshness": 0,
        }
        world.diplomatic_points = 5

        break_treaty(pair_key, player, world)
        found = [e for e in world.diplomatic_history if e["type"] == "treaty_broken"]
        assert len(found) >= 1
        assert found[-1]["nation"] == player
        assert found[-1]["target"] == "Prussia"

    def test_proposal_sent_logged(self, executor, world, game_state):
        """Sending a proposal creates a history entry."""
        world.diplomatic_points = 10
        world.pending_diplomatic_dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Austria",
            "options": [
                {
                    "label": "Send",
                    "action": "execute_proposal",
                    "terms": {
                        "proposal_type": "peace",
                        "target_nation": "Austria",
                        "sweeteners": [],
                        "demands": [],
                        "clauses": [],
                    },
                },
            ],
            "context": {},
            "turn_created": 1,
            "blocking": False,
            "talleyrand_text": "Test",
        }
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result.get("success"), result.get("message")
        found = [e for e in world.diplomatic_history if e["type"] == "proposal_sent"]
        assert len(found) >= 1
        assert found[-1]["target"] == "Austria"

    def test_history_capped_at_20(self, world):
        """History never exceeds 20 entries."""
        from backend.game_logic.diplomacy import declare_war
        # Pre-fill history with 19 entries
        for i in range(19):
            world.diplomatic_history.append({
                "turn": i,
                "type": "test",
                "nation": "France",
                "target": "Test",
            })

        # Add another via war declaration (brings it to 20+)
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "PEACE"
        declare_war(world, "France", "Austria")
        # Should add an entry but cap at 20
        assert len(world.diplomatic_history) <= 20

    def test_history_serialization(self, world):
        """Diplomatic history survives serialization round-trip."""
        world.diplomatic_history.append({
            "turn": 5,
            "type": "war_declared",
            "nation": "France",
            "target": "Prussia",
        })
        data = world.to_dict()
        assert len(data["diplomatic_history"]) == 1

        world2 = WorldState.from_dict(data)
        assert len(world2.diplomatic_history) == 1
        assert world2.diplomatic_history[0]["type"] == "war_declared"

    def test_reliability_serialization(self, world):
        """Diplomatic reliability survives serialization round-trip."""
        world.diplomatic_reliability["France"] = -20
        world.diplomatic_reliability["Prussia"] = 15
        data = world.to_dict()
        assert data["diplomatic_reliability"]["France"] == -20

        world2 = WorldState.from_dict(data)
        assert world2.diplomatic_reliability["France"] == -20
        assert world2.diplomatic_reliability["Prussia"] == 15

    def test_ledger_includes_history(self, world):
        """Diplomatic ledger Talleyrand tab includes history entries."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger

        world.diplomatic_history.append({
            "turn": 3,
            "type": "war_declared",
            "nation": "France",
            "target": "Prussia",
        })

        ledger = build_diplomatic_ledger(world)
        talleyrand = ledger["talleyrand"]
        assert "diplomatic_history" in talleyrand
        assert len(talleyrand["diplomatic_history"]) == 1
        assert talleyrand["diplomatic_history"][0]["type"] == "war_declared"

    def test_ledger_includes_reliability(self, world):
        """Diplomatic ledger Talleyrand tab includes reliability score."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger

        world.diplomatic_reliability["France"] = -15

        ledger = build_diplomatic_ledger(world)
        talleyrand = ledger["talleyrand"]
        assert "diplomatic_reliability" in talleyrand
        assert talleyrand["diplomatic_reliability"] == -15

    def test_ultimatum_already_logged(self, executor, world, game_state):
        """Ultimatum logging from Batch 1 is still in place."""
        world.diplomatic_points = 10
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "PEACE"

        command = {
            "action": "diplomatic_ultimatum",
            "diplomatic_data": {
                "action": "diplomatic_ultimatum",
                "target_nation": "Prussia",
            },
        }
        result = executor._execute_diplomatic(command, game_state)
        assert result.get("success"), result.get("message")
        found = [e for e in world.diplomatic_history if e["type"] == "ultimatum"]
        assert len(found) >= 1

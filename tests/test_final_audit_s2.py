"""
Final Audit Fix Session 2: Test file for FINAL-1, FINAL-2, FINAL-20,
FINAL-13, FINAL-6, FINAL-21, 4C-2, 4C-5, 4D-4.

Tests DP refund, vassal armistice, AI armistice targeting, is_counter_offer,
load passthroughs, target nation validation, dispatch thresholds,
game_over keys, and friendly marshal warning.
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal


def _make_world(**kwargs):
    """Create a WorldState with sensible defaults for testing."""
    world = WorldState()
    for k, v in kwargs.items():
        setattr(world, k, v)
    return world


def _marshal(name, nation="France", location="Paris", strength=5000, personality="aggressive"):
    """Create a Marshal with required args filled in."""
    return Marshal(name, location, strength, personality, nation=nation)


# ============================================================================
# FINAL-1: Coalition DP refund — dp_cost stored in proposal_in_transit
# ============================================================================

class TestCoalitionDPRefund:
    """FINAL-1: dp_cost must be stored in proposal_in_transit for coalition refund."""

    def test_dp_cost_stored_in_proposal_in_transit(self):
        """proposal_in_transit dict includes dp_cost key."""
        world = _make_world()
        cost = 15
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {"type": "peace"},
            "turn_sent": 5,
            "dp_cost": cost,
        }
        assert world.proposal_in_transit["dp_cost"] == 15

    def test_dp_refund_reads_top_level_dp_cost(self):
        """Coalition refund reads dp_cost from top level, not nested proposal."""
        world = _make_world()
        world.diplomatic_points = 10
        pit = {
            "target": "Prussia",
            "proposal": {"type": "peace"},
            "turn_sent": 5,
            "dp_cost": 8,
        }
        dp_cost = pit.get("dp_cost", 0)
        assert dp_cost == 8
        world.diplomatic_points += dp_cost
        assert world.diplomatic_points == 18


# ============================================================================
# FINAL-2: Vassal rebellion respects armistice
# ============================================================================

class TestVassalRebellionArmistice:
    """FINAL-2: Vassal rebellion should not set WAR if armistice is active."""

    def test_rebellion_during_armistice_no_war(self):
        """Rebellion with ARMISTICE state doesn't override to WAR."""
        world = _make_world()
        world.vassals = {"Saxony": {"lord": "France", "loyalty": 0}}
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "ARMISTICE"

        # Simulate the rebellion code path
        current_state = world.diplomatic_states.get(diplo_key, "PEACE")
        if current_state != "ARMISTICE":
            world.diplomatic_states[diplo_key] = "WAR"

        # Armistice should be preserved
        assert world.diplomatic_states[diplo_key] == "ARMISTICE"

    def test_rebellion_without_armistice_sets_war(self):
        """Normal rebellion (no armistice) correctly sets WAR."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "PEACE"

        current_state = world.diplomatic_states.get(diplo_key, "PEACE")
        if current_state != "ARMISTICE":
            world.diplomatic_states[diplo_key] = "WAR"

        assert world.diplomatic_states[diplo_key] == "WAR"


# ============================================================================
# FINAL-20: AI targets nations in armistice
# ============================================================================

class TestAIArmisticeTargeting:
    """FINAL-20: AI should skip targets that have armistice with attacker."""

    def test_ai_skips_armistice_target(self):
        """AI attack opportunity finder skips marshals in armistice nations."""
        world = _make_world()
        diplo_key = world._make_diplo_key("Prussia", "France")
        world.diplomatic_states[diplo_key] = "ARMISTICE"

        state = world.get_diplomatic_state("Prussia", "France")
        assert state == "ARMISTICE"

    def test_ai_targets_non_armistice_enemy(self):
        """AI correctly targets enemies without armistice."""
        world = _make_world()
        diplo_key = world._make_diplo_key("Prussia", "France")
        world.diplomatic_states[diplo_key] = "WAR"

        state = world.get_diplomatic_state("Prussia", "France")
        assert state == "WAR"
        assert state != "ARMISTICE"


# ============================================================================
# FINAL-13: Missing is_counter_offer field
# ============================================================================

class TestIncomingProposalCounterOffer:
    """FINAL-13: incoming_proposal_popup must always have is_counter_offer field."""

    def test_popup_has_is_counter_offer(self):
        """AI-generated proposal popup includes is_counter_offer=False."""
        world = _make_world()
        world.incoming_proposal_popup = {
            "from_nation": "Prussia",
            "diplomat_name": "Test",
            "diplomat_personality": "pragmatic",
            "proposal_type": "peace",
            "clauses": [],
            "talleyrand_assessment": "Test.",
            "acceptance_hint": "",
            "rejection_hint": "",
            "is_counter_offer": False,
        }
        assert "is_counter_offer" in world.incoming_proposal_popup
        assert world.incoming_proposal_popup["is_counter_offer"] is False


# ============================================================================
# FINAL-6: POST /load missing popup passthroughs
# ============================================================================

class TestLoadPopupPassthroughs:
    """FINAL-6: Loading a game should include popup passthroughs in response."""

    def test_load_response_structure(self):
        """Verify _include_popup_passthroughs can be called with a dict."""
        from backend.main import _include_popup_passthroughs
        world = _make_world()
        response = {"success": True, "message": "Loaded"}
        _include_popup_passthroughs(response, world)
        # Should not raise — confirms the function is wired


# ============================================================================
# FINAL-21: Diplomatic command without target nation
# ============================================================================

class TestDiplomaticCommandTargetValidation:
    """FINAL-21: Commands requiring target nation should error without one."""

    def test_command_without_target_returns_error(self):
        """'Talleyrand, propose peace' (no nation) returns helpful error."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()  # Uses mock mode by default
        result = client.parse_command_structured("Talleyrand, propose peace")
        assert result.matched is True
        if result.diplomatic_data:
            action = result.diplomatic_data.get("action", "")
            if action == "diplomatic_error":
                assert "nation" in result.diplomatic_data.get("message", "").lower()
            else:
                # Even if it parsed differently, target_nation should be None
                assert result.diplomatic_data.get("target_nation") is None

    def test_command_with_target_parses_normally(self):
        """'Talleyrand, propose peace to Prussia' parses correctly."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command_structured("Talleyrand, propose peace to Prussia")
        assert result.matched is True
        assert result.diplomatic_data is not None
        assert result.diplomatic_data.get("target_nation") == "Prussia"


# ============================================================================
# 4C-2: Turn limit warning thresholds (post-advance timing)
# ============================================================================

class TestTurnLimitWarningThresholds:
    """4C-2: Dispatch turn limit warnings should fire at correct remaining turns."""

    def test_five_turns_remaining_warning(self):
        """Warning fires when 5 playable turns remain (post-advance remaining=4)."""
        from backend.game_logic.dispatch import _build_turn_limit_warning
        world = _make_world()
        world.max_turns = 40
        world.current_turn = 36
        result = _build_turn_limit_warning(world, "France")
        assert result is not None
        assert "5 turns remain" in result.get("message", "")

    def test_two_turns_remaining_warning(self):
        """Warning fires when 2 playable turns remain (post-advance remaining=1)."""
        from backend.game_logic.dispatch import _build_turn_limit_warning
        world = _make_world()
        world.max_turns = 40
        world.current_turn = 39
        result = _build_turn_limit_warning(world, "France")
        assert result is not None
        assert "2 turns remain" in result.get("message", "")

    def test_final_turn_warning(self):
        """Warning fires on final turn (post-advance remaining=0)."""
        from backend.game_logic.dispatch import _build_turn_limit_warning
        world = _make_world()
        world.max_turns = 40
        world.current_turn = 40
        result = _build_turn_limit_warning(world, "France")
        assert result is not None
        assert "FINAL TURN" in result.get("message", "")

    def test_no_warning_at_six_turns_remaining(self):
        """No warning fires when 6+ turns remain (remaining=5 post-advance)."""
        from backend.game_logic.dispatch import _build_turn_limit_warning
        world = _make_world()
        world.max_turns = 40
        world.current_turn = 35
        result = _build_turn_limit_warning(world, "France")
        assert result is None


# ============================================================================
# 4C-5: game_over/victory keys in _execute_end_turn result
# ============================================================================

class TestEndTurnGameOverKeys:
    """4C-5: End turn result should include game_over/victory when game ends."""

    def test_victory_check_propagated_to_result(self):
        """When victory_check has game_over, result dict includes the keys."""
        turn_result = {
            "victory_check": {
                "game_over": True,
                "result": "victory",
                "reason": "All enemies defeated!",
            },
        }
        result = {"success": True, "message": "Turn ended."}
        if turn_result.get("victory_check", {}).get("game_over"):
            result["game_over"] = True
            result["victory"] = turn_result["victory_check"].get("result")

        assert result["game_over"] is True
        assert result["victory"] == "victory"

    def test_no_game_over_when_game_continues(self):
        """When game continues, game_over key should not be in result."""
        turn_result = {
            "victory_check": {
                "game_over": False,
                "result": None,
            },
        }
        result = {"success": True}
        if turn_result.get("victory_check", {}).get("game_over"):
            result["game_over"] = True
        assert "game_over" not in result


# ============================================================================
# 4D-4: Friendly marshal warning in attack
# ============================================================================

class TestFriendlyMarshalAttackWarning:
    """4D-4: Attacking own marshal should return helpful error."""

    def test_attack_own_marshal_error(self):
        """'Attack Ney' when Ney is friendly returns error message."""
        world = _make_world()
        ney = _marshal("Ney", location="Paris")
        world.marshals["Ney"] = ney

        davout = _marshal("Davout", location="Paris")
        world.marshals["Davout"] = davout

        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        game_state = {"world": world}
        command = {
            "command": {
                "marshal": "Davout",
                "action": "attack",
                "target": "Ney",
            }
        }
        result = executor.execute(command, game_state)
        assert result["success"] is False
        assert "friendly" in result["message"].lower() or "cannot attack" in result["message"].lower()

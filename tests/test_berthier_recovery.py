"""
Tests for Berthier Parse Recovery.

Replaces generic "Unknown action" errors with in-character Berthier
clarification. Tests cover:
1. Mock template responses (content, variation, context-awareness)
2. Prompt builder output (system + user prompt structure)
3. Integration with parser + main.py wiring
"""

import pytest
from backend.ai.llm_client import LLMClient
from backend.ai.prompt_builder import build_berthier_recovery_prompt
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState


# =============================================================================
# HELPERS
# =============================================================================

def _make_game_state():
    """Build a minimal LLM-compatible game_state dict."""
    return {
        "turn": 1,
        "gold": 500,
        "marshals": {
            "Ney": {"location": "Belgium", "strength": 72000, "morale": 85},
            "Davout": {"location": "Paris", "strength": 65000, "morale": 90},
        },
        "enemies": {
            "Wellington": {"location": "Waterloo", "strength": 65000, "nation": "British"},
        },
        "map_data": {
            "Belgium": {"controller": "France", "marshals": [{"name": "Ney", "personality": "aggressive"}]},
            "Paris": {"controller": "France", "marshals": [{"name": "Davout", "personality": "cautious"}]},
            "Waterloo": {"controller": "Britain", "marshals": []},
        },
    }


# =============================================================================
# MOCK TEMPLATE TESTS
# =============================================================================

class TestBerthierMockResponse:
    """Tests for _berthier_mock_response template generation."""

    def setup_method(self):
        self.client = LLMClient(use_real_api=False)
        self.game_state = _make_game_state()

    def test_returns_nonempty_string(self):
        """Recovery always returns a non-empty string."""
        result = self.client.generate_berthier_recovery("xyzzy", self.game_state)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_berthier_reference(self):
        """Every mock response mentions Berthier."""
        for _ in range(10):
            result = self.client.generate_berthier_recovery("xyzzy", self.game_state)
            assert "Berthier" in result

    def test_mentions_recognized_marshal(self):
        """When partial parse has a marshal, response mentions them."""
        partial = {"recognized_marshal": "Ney"}
        for _ in range(10):
            result = self.client.generate_berthier_recovery(
                "Ney do a dance", self.game_state, partial
            )
            assert "Ney" in result

    def test_mentions_recognized_target(self):
        """When partial parse has a target, response mentions it."""
        partial = {"recognized_target": "Wellington"}
        for _ in range(10):
            result = self.client.generate_berthier_recovery(
                "smite Wellington", self.game_state, partial
            )
            assert "Wellington" in result

    def test_general_help_when_nothing_recognized(self):
        """When nothing is recognized, response still contains helpful content."""
        result = self.client.generate_berthier_recovery(
            "dance with the moon", self.game_state, {}
        )
        assert "Berthier" in result
        # Should mention at least one real marshal name or valid action
        has_marshal = any(m in result for m in ["Ney", "Davout"])
        has_action = any(a in result for a in ["attack", "move", "defend", "scout"])
        assert has_marshal or has_action

    def test_mentions_valid_actions(self):
        """Mock responses include valid action suggestions."""
        # Run several times to get different templates
        found_action = False
        for _ in range(15):
            result = self.client.generate_berthier_recovery("xyzzy", self.game_state)
            if any(a in result.lower() for a in ["attack", "move", "defend", "scout", "fortify"]):
                found_action = True
                break
        assert found_action, "Expected at least one response to mention a valid action"

    def test_templates_vary(self):
        """Multiple calls should produce at least 2 different responses."""
        results = set()
        for _ in range(20):
            result = self.client.generate_berthier_recovery("xyzzy", self.game_state)
            results.add(result)
        assert len(results) >= 2, f"Expected variation, got {len(results)} unique responses"

    def test_handles_empty_game_state(self):
        """Recovery works even with minimal/empty game state."""
        result = self.client.generate_berthier_recovery("xyzzy", {})
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Berthier" in result


# =============================================================================
# PROMPT BUILDER TESTS
# =============================================================================

class TestBerthierPromptBuilder:
    """Tests for build_berthier_recovery_prompt."""

    def setup_method(self):
        self.game_state = _make_game_state()

    def test_system_prompt_mentions_berthier(self):
        """System prompt establishes Berthier character."""
        system, _ = build_berthier_recovery_prompt("xyzzy", self.game_state)
        assert "Berthier" in system

    def test_user_prompt_includes_raw_command(self):
        """User prompt contains the original failed command."""
        _, user = build_berthier_recovery_prompt("dance with the moon", self.game_state)
        assert "dance with the moon" in user

    def test_user_prompt_includes_partial_parse(self):
        """User prompt reflects partial parse info."""
        partial = {"recognized_marshal": "Ney", "recognized_target": "Wellington"}
        _, user = build_berthier_recovery_prompt("Ney smite Wellington", self.game_state, partial)
        assert "Ney" in user
        assert "Wellington" in user

    def test_user_prompt_includes_valid_actions(self):
        """User prompt lists valid actions for LLM context."""
        _, user = build_berthier_recovery_prompt("xyzzy", self.game_state)
        assert "attack" in user
        assert "move" in user

    def test_returns_tuple_of_two_strings(self):
        """Return value is (system_prompt, user_prompt) tuple."""
        result = build_berthier_recovery_prompt("xyzzy", self.game_state)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)


# =============================================================================
# INTEGRATION TESTS (parser → main.py wiring)
# =============================================================================

class TestBerthierIntegration:
    """Integration tests verifying end-to-end Berthier recovery flow."""

    def setup_method(self):
        self.parser = CommandParser(use_real_llm=False)
        self.world = WorldState(player_nation="France")

    def _get_llm_game_state(self):
        """Build LLM game state from world (mirrors main.py helper)."""
        marshals = {}
        for m in self.world.get_player_marshals():
            if m.strength > 0:
                marshals[m.name] = {
                    "location": m.location,
                    "strength": int(m.strength),
                    "morale": int(m.morale),
                }
        enemies = {}
        for m in self.world.get_enemy_marshals():
            if m.strength > 0:
                enemies[m.name] = {
                    "location": m.location,
                    "strength": int(m.strength),
                    "nation": m.nation,
                }
        map_data = {}
        for region_name, region in self.world.regions.items():
            marshals_here = self.world.get_marshals_in_region(region_name)
            map_data[region_name] = {
                "controller": region.controller or "Neutral",
                "marshals": [
                    {"name": m.name, "personality": getattr(m, 'personality', 'unknown')}
                    for m in marshals_here if m.strength > 0
                ]
            }
        return {
            "turn": int(self.world.current_turn),
            "gold": int(self.world.gold),
            "marshals": marshals,
            "enemies": enemies,
            "map_data": map_data,
        }

    def test_gibberish_gets_berthier_not_unknown_action(self):
        """Gibberish command triggers Berthier recovery, not 'Unknown action'."""
        llm_gs = self._get_llm_game_state()
        parsed = self.parser.parse("dance with the moon", llm_gs, world=self.world)

        # Parser should fail with "Unknown action"
        assert not parsed["success"]
        assert parsed["error"].startswith("Unknown action")

        # Now simulate what main.py does: detect and call recovery
        if not parsed.get("success") and (parsed.get("error") or "").startswith("Unknown action"):
            berthier_msg = self.parser.llm.generate_berthier_recovery(
                raw_command="dance with the moon",
                game_state=llm_gs,
                partial_parse={
                    "recognized_marshal": parsed.get("partial_marshal"),
                    "recognized_target": parsed.get("partial_target"),
                },
            )
            assert "Berthier" in berthier_msg
            assert "Unknown action" not in berthier_msg

    def test_valid_command_bypasses_berthier(self):
        """Normal valid commands are unaffected by the recovery path."""
        llm_gs = self._get_llm_game_state()
        parsed = self.parser.parse("Ney, attack Wellington", llm_gs, world=self.world)

        assert parsed["success"]
        # Berthier check should not fire
        should_fire = not parsed.get("success") and (parsed.get("error") or "").startswith("Unknown action")
        assert not should_fire

    def test_marshal_typo_still_gets_fuzzy_match(self):
        """Marshal typo gets fuzzy-matched, NOT Berthier recovery.

        CR-0 update: punctuation stripping means "Naey," now fuzzy
        AUTO-corrects to Ney (parse succeeds) instead of stopping at a
        suggest-level error. Either outcome honors the contract under
        test — a marshal typo must never fall through to Berthier."""
        llm_gs = self._get_llm_game_state()
        parsed = self.parser.parse("Naey, attack Wellington", llm_gs, world=self.world)

        if parsed["success"]:
            # Auto-corrected — the typo resolved to the real marshal
            assert parsed["command"]["marshal"] == "Ney"
        else:
            # Suggest-level — must be a typo suggestion, not Unknown action
            is_berthier_trigger = (parsed.get("error") or "").startswith("Unknown action")
            assert not is_berthier_trigger, (
                f"Marshal typo should NOT trigger Berthier; got error: {parsed.get('error')}"
            )

    def test_response_dict_has_correct_format(self):
        """Berthier response dict matches the shape main.py returns."""
        llm_gs = self._get_llm_game_state()
        berthier_msg = self.parser.llm.generate_berthier_recovery(
            raw_command="xyzzy",
            game_state=llm_gs,
            partial_parse={},
        )

        # Build response dict as main.py does
        response = {
            "success": False,
            "message": berthier_msg,
            "events": [],
            "action_info": {
                "cost": 0,
                "remaining": int(self.world.actions_remaining),
                "turn_advanced": False,
                "new_turn": None,
            },
            "action_summary": self.world.get_action_summary(),
            "game_state": self.world.get_game_state_summary(),
        }

        assert response["success"] is False
        assert isinstance(response["message"], str)
        assert "Berthier" in response["message"]
        assert isinstance(response["action_summary"], dict)
        assert isinstance(response["game_state"], dict)
        assert response["action_info"]["cost"] == 0

    def test_partial_marshal_forwarded_to_recovery(self):
        """When parser recognises a marshal but not the action, partial info is forwarded."""
        llm_gs = self._get_llm_game_state()
        # "Ney" is recognized but "xyzzy" is not a valid action
        parsed = self.parser.parse("Ney xyzzy", llm_gs, world=self.world)

        # Should fail with Unknown action since "xyzzy" is not valid
        if not parsed.get("success") and (parsed.get("error") or "").startswith("Unknown action"):
            assert parsed.get("partial_marshal") == "Ney"
            berthier_msg = self.parser.llm.generate_berthier_recovery(
                raw_command="Ney xyzzy",
                game_state=llm_gs,
                partial_parse={
                    "recognized_marshal": parsed.get("partial_marshal"),
                    "recognized_target": parsed.get("partial_target"),
                },
            )
            assert "Ney" in berthier_msg

    def test_marshal_none_executor_error_gets_berthier(self):
        """Commands that parse with valid action but marshal=None get Berthier,
        not the raw 'Marshal None not found' error."""
        from backend.commands.executor import CommandExecutor

        executor = CommandExecutor()
        gs = {"world": self.world, "debug_mode": True}
        llm_gs = self._get_llm_game_state()

        # "scout" parses successfully (action=scout) but marshal=None
        parsed = self.parser.parse("scout", llm_gs, world=self.world)
        assert parsed["success"]
        assert parsed["command"]["marshal"] is None

        result = executor.execute(parsed, gs)
        # Executor returns the marshal-None error
        assert not result.get("success")
        assert "Marshal 'None' not found" in (result.get("message") or "")

        # Simulate main.py's second Berthier check
        berthier_msg = self.parser.llm.generate_berthier_recovery(
            raw_command="scout",
            game_state=llm_gs,
            partial_parse={
                "recognized_marshal": None,
                "recognized_target": parsed.get("command", {}).get("target"),
                "raw_input": "scout",
            },
        )
        assert "Berthier" in berthier_msg
        assert "Marshal 'None'" not in berthier_msg

    def test_move_no_marshal_gets_berthier(self):
        """'move to Belgium' with no marshal triggers Berthier recovery."""
        from backend.commands.executor import CommandExecutor

        executor = CommandExecutor()
        gs = {"world": self.world, "debug_mode": True}
        llm_gs = self._get_llm_game_state()

        parsed = self.parser.parse("move to Belgium", llm_gs, world=self.world)
        if parsed["success"] and parsed["command"]["marshal"] is None:
            result = executor.execute(parsed, gs)
            is_marshal_none = "Marshal 'None' not found" in (result.get("message") or "")
            assert is_marshal_none, "Expected marshal-None error from executor"

            berthier_msg = self.parser.llm.generate_berthier_recovery(
                raw_command="move to Belgium",
                game_state=llm_gs,
                partial_parse={
                    "recognized_marshal": None,
                    "recognized_target": parsed["command"].get("target"),
                },
            )
            assert "Berthier" in berthier_msg

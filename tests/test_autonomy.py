"""
Autonomy System Test Suite for Project Sovereign

Tests Phase 2.5: Grant Autonomy → Enemy AI Connection

Tests cover:
- Grant Autonomy field initialization
- Autonomous marshal AI action execution
- Nation-aligned targeting (only attacks enemies)
- Command blocking for autonomous marshals
- Autonomy countdown and ending
- Performance evaluation (4 tiers)
- Independent Command Report generation

Run with: pytest tests/test_autonomy.py -v
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, Stance
from backend.commands.executor import CommandExecutor
from backend.commands.disobedience import DisobedienceSystem
from backend.game_logic.turn_manager import TurnManager
from backend.ai.enemy_ai import EnemyAI


class TestGrantAutonomy:
    """Test Grant Autonomy handler sets all fields correctly."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.disobedience = DisobedienceSystem()
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_grant_autonomy_sets_all_fields(self):
        """Grant Autonomy should set autonomous, turns, reason, and reset tracking."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(20)  # At redemption threshold
        ney.redemption_pending = True

        redemption_event = {
            "marshal": "Ney",
            "type": "redemption"
        }

        result = self.disobedience.handle_redemption_response(
            redemption_event, "grant_autonomy", self.game_state
        )

        assert result["success"] == True
        assert result["choice"] == "grant_autonomy"
        assert ney.autonomous == True
        assert ney.autonomy_turns == 3
        assert ney.autonomy_reason == "redemption"
        assert ney.autonomous_battles_won == 0
        assert ney.autonomous_battles_lost == 0
        assert ney.autonomous_regions_captured == 0
        print("Grant Autonomy: All fields set correctly")

    def test_grant_autonomy_clears_redemption_pending(self):
        """Grant Autonomy should clear redemption_pending flag."""
        ney = self.world.get_marshal("Ney")
        ney.redemption_pending = True

        redemption_event = {"marshal": "Ney", "type": "redemption"}
        self.disobedience.handle_redemption_response(
            redemption_event, "grant_autonomy", self.game_state
        )

        assert ney.redemption_pending == False
        print("Grant Autonomy: redemption_pending cleared")


class TestAutonomousAIAction:
    """Test autonomous marshals use Enemy AI for decisions."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_decide_single_action_returns_result(self):
        """decide_single_action should return action result dict."""
        ney = self.world.get_marshal("Ney")

        result = self.ai.decide_single_action(
            marshal=ney,
            nation="France",
            world=self.world,
            game_state=self.game_state
        )

        assert result is not None
        assert "marshal" in result
        assert "action" in result
        assert "result" in result
        print(f"AI decided: {result['action']} for {result['marshal']}")

    def test_autonomous_marshal_only_targets_enemies(self):
        """Autonomous French marshal should only target enemies of France."""
        ney = self.world.get_marshal("Ney")
        davout = self.world.get_marshal("Davout")
        wellington = self.world.get_marshal("Wellington")

        # Set up scenario where Ney could attack either
        ney.location = "Belgium"
        davout.location = "Belgium"  # Same location - friendly
        wellington.location = "Waterloo"  # Adjacent - enemy

        result = self.ai.decide_single_action(
            marshal=ney,
            nation="France",
            world=self.world,
            game_state=self.game_state
        )

        # If attacking, should target Wellington, not Davout
        if result and result.get("action") == "attack":
            assert result.get("target") != "Davout", "Should not attack own nation"
            print(f"Correctly targeted enemy: {result.get('target')}")
        else:
            print(f"Action was {result.get('action')}, not attack - OK")


class TestCommandBlocking:
    """Test player cannot command autonomous marshals."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_cannot_command_autonomous_marshal(self):
        """Player should not be able to issue orders to autonomous marshal."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 2
        ney.autonomy_reason = "redemption"

        command = {
            "command": {
                "type": "specific",
                "marshal": "Ney",
                "action": "attack",
                "target": "Wellington"
            }
        }

        result = self.executor.execute(command, self.game_state)

        assert result["success"] == False
        assert result["autonomous"] == True
        assert "acting independently" in result["message"]
        assert "performance" in result
        print(f"Command blocked: {result['message']}")

    def test_command_block_shows_performance(self):
        """Command block message should show performance stats."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 1
        ney.autonomous_battles_won = 2
        ney.autonomous_battles_lost = 1
        ney.autonomous_regions_captured = 1

        command = {
            "command": {
                "type": "specific",
                "marshal": "Ney",
                "action": "move",
                "target": "Paris"
            }
        }

        result = self.executor.execute(command, self.game_state)

        assert "2 battles won" in result["message"]
        assert "1 battle lost" in result["message"]
        assert "1 region captured" in result["message"]
        print(f"Performance shown: {result['message']}")

    def test_can_command_non_autonomous_marshal(self):
        """Player should be able to command non-autonomous marshals."""
        davout = self.world.get_marshal("Davout")
        davout.autonomous = False

        # Simple move command
        command = {
            "command": {
                "type": "specific",
                "marshal": "Davout",
                "action": "wait"
            }
        }

        result = self.executor.execute(command, self.game_state)

        # Should not be blocked by autonomy
        assert result.get("autonomous") != True
        print("Non-autonomous marshal can receive orders")


class TestAutonomyCountdown:
    """Test autonomy countdown and ending."""

    def setup_method(self):
        self.world = WorldState()
        self.turn_manager = TurnManager(self.world)
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_autonomy_decrements_each_turn(self):
        """Autonomy turns should decrement each turn."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 3
        ney.autonomy_reason = "redemption"

        # Process autonomous marshals (called during end_turn)
        self.turn_manager._process_autonomous_marshals(self.game_state)

        assert ney.autonomy_turns == 2
        print(f"Autonomy decremented: {ney.autonomy_turns} turns remaining")

    def test_autonomy_ends_after_3_turns(self):
        """Autonomy should end when turns hit 0."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 1  # Last turn
        ney.autonomy_reason = "redemption"

        self.turn_manager._process_autonomous_marshals(self.game_state)

        assert ney.autonomous == False
        assert ney.autonomy_turns == 0
        assert ney.autonomy_reason == ""
        print("Autonomy ended correctly after countdown")


class TestPerformanceEvaluation:
    """Test 4-tier performance evaluation when autonomy ends.

    All gains are RELATIVE (not flat) to prevent exploit:
    - Spectacular: +40 trust, +10 authority
    - Success: +25 trust
    - Neutral: +15 trust
    - Failure: +5 trust
    """

    def setup_method(self):
        self.world = WorldState()
        self.turn_manager = TurnManager(self.world)

    def test_spectacular_success_trust_plus_40_authority_10(self):
        """2+ battles won OR 1+ region = spectacular success (+40 trust)."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 0
        ney.autonomous_battles_won = 2
        ney.autonomous_regions_captured = 0
        ney.trust.set(20)
        self.world.authority = 50

        result = self.turn_manager._end_autonomy(ney)

        assert result["tier"] == "spectacular"
        assert ney.trust.value == 60  # 20 + 40 (relative, not flat 70)
        assert self.world.authority == 60  # +10
        print(f"Spectacular: {result['message']}")

    def test_spectacular_region_capture(self):
        """1+ region captured = spectacular (+40 trust)."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 0
        ney.autonomous_battles_won = 0
        ney.autonomous_regions_captured = 1
        ney.trust.set(20)
        self.world.authority = 50

        result = self.turn_manager._end_autonomy(ney)

        assert result["tier"] == "spectacular"
        assert ney.trust.value == 60  # 20 + 40
        print(f"Spectacular (region): {result['message']}")

    def test_success_trust_plus_25(self):
        """Positive score without spectacular = success (+25 trust)."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 0
        ney.autonomous_battles_won = 1  # +2 score
        ney.autonomous_battles_lost = 0
        ney.autonomous_regions_captured = 0
        ney.trust.set(20)

        result = self.turn_manager._end_autonomy(ney)

        assert result["tier"] == "success"
        assert ney.trust.value == 45  # 20 + 25
        print(f"Success: {result['message']}")

    def test_neutral_trust_plus_15(self):
        """Zero score = neutral."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 0
        ney.autonomous_battles_won = 0
        ney.autonomous_battles_lost = 0
        ney.autonomous_regions_captured = 0
        ney.trust.set(20)

        result = self.turn_manager._end_autonomy(ney)

        assert result["tier"] == "neutral"
        assert ney.trust.value == 35  # 20 + 15
        print(f"Neutral: {result['message']}")

    def test_failure_trust_plus_5(self):
        """Negative score = failure."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 0
        ney.autonomous_battles_won = 0
        ney.autonomous_battles_lost = 2  # -4 score
        ney.autonomous_regions_captured = 0
        ney.trust.set(20)

        result = self.turn_manager._end_autonomy(ney)

        assert result["tier"] == "failure"
        assert ney.trust.value == 25  # 20 + 5
        print(f"Failure: {result['message']}")

    def test_tracking_fields_reset_after_evaluation(self):
        """Performance tracking should reset after evaluation."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 0
        ney.autonomous_battles_won = 5
        ney.autonomous_battles_lost = 3
        ney.autonomous_regions_captured = 2
        ney.autonomy_reason = "redemption"

        self.turn_manager._end_autonomy(ney)

        assert ney.autonomous_battles_won == 0
        assert ney.autonomous_battles_lost == 0
        assert ney.autonomous_regions_captured == 0
        assert ney.autonomy_reason == ""
        print("Tracking fields reset correctly")

    def test_autonomy_end_actually_updates_trust(self):
        """Verify trust.modify() is called and trust value changes."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 0
        ney.autonomous_battles_won = 2  # Spectacular
        ney.autonomous_battles_lost = 0
        ney.autonomous_regions_captured = 0
        ney.trust.set(20)  # Start at redemption floor

        old_trust = ney.trust.value
        result = self.turn_manager._end_autonomy(ney)
        new_trust = ney.trust.value

        # Trust MUST have changed
        assert new_trust > old_trust, f"Trust should increase: {old_trust} -> {new_trust}"
        assert new_trust == 60, f"Spectacular should give 20+40=60, got {new_trust}"
        assert ney.autonomous == False
        assert result["old_trust"] == 20
        assert result["new_trust"] == 60
        print(f"Trust updated correctly: {old_trust} -> {new_trust}")


class TestIndependentCommandReport:
    """Test Independent Command Report generation."""

    def setup_method(self):
        self.world = WorldState()
        self.turn_manager = TurnManager(self.world)
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_no_popup_when_no_autonomous_marshals(self):
        """Should not show popup if no autonomous marshals."""
        # Ensure no marshals are autonomous
        for marshal in self.world.marshals.values():
            marshal.autonomous = False

        result = self.turn_manager._process_autonomous_marshals(self.game_state)

        assert result["show_independent_command_report"] == False
        assert result["independent_command_report"] == []
        print("No popup when no autonomous marshals")

    def test_popup_when_autonomous_marshals_exist(self):
        """Should show popup with report when autonomous marshals exist."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 2
        ney.autonomy_reason = "redemption"

        result = self.turn_manager._process_autonomous_marshals(self.game_state)

        assert result["show_independent_command_report"] == True
        assert len(result["independent_command_report"]) > 0
        report = result["independent_command_report"][0]
        assert report["marshal"] == "Ney"
        assert "action" in report
        assert "turns_remaining" in report
        print(f"Popup shown with report: {report['action']}")

    def test_report_contains_performance_data(self):
        """Report should include performance tracking."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 2
        ney.autonomous_battles_won = 1

        result = self.turn_manager._process_autonomous_marshals(self.game_state)
        report = result["independent_command_report"][0]

        assert "performance" in report
        assert "battles_won" in report["performance"]
        print(f"Performance in report: {report['performance']}")


class TestEndTurnIntegration:
    """Test autonomy integration with end_turn flow."""

    def setup_method(self):
        self.world = WorldState()
        self.turn_manager = TurnManager(self.world)
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_end_turn_includes_independent_command_report(self):
        """end_turn should include independent_command_report in result."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 2
        ney.autonomy_reason = "redemption"

        result = self.turn_manager.end_turn(self.game_state)

        assert "show_independent_command_report" in result
        assert "independent_command_report" in result
        print("end_turn includes autonomous report")

    def test_end_turn_processes_autonomy_after_advance(self):
        """Autonomy should be processed AFTER turn advances."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 2

        old_turn = self.world.current_turn
        result = self.turn_manager.end_turn(self.game_state)

        # Turn should have advanced
        assert result["next_turn"] == old_turn + 1
        # Autonomy should have been processed
        assert ney.autonomy_turns == 1
        print(f"Turn advanced to {result['next_turn']}, autonomy processed")


class TestExecutorPassesReport:
    """Test that executor passes Independent Command Report to frontend."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_executor_end_turn_includes_report(self):
        """Executor's end_turn should include independent_command_report."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 2
        ney.autonomy_reason = "redemption"

        command = {"command": {"type": "end_turn", "action": "end_turn"}}
        result = self.executor.execute(command, self.game_state)

        assert result["success"] == True
        assert "show_independent_command_report" in result
        assert result["show_independent_command_report"] == True
        assert "independent_command_report" in result
        assert len(result["independent_command_report"]) > 0
        print(f"Executor passed report: {result['independent_command_report']}")

    def test_executor_end_turn_report_in_message(self):
        """Executor's message should contain Independent Command Report."""
        ney = self.world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 2
        ney.autonomy_reason = "redemption"

        command = {"command": {"type": "end_turn", "action": "end_turn"}}
        result = self.executor.execute(command, self.game_state)

        assert "INDEPENDENT COMMAND REPORT" in result["message"]
        assert "Ney" in result["message"]
        print(f"Message includes report:\n{result['message']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

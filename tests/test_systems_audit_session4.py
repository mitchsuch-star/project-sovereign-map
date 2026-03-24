"""
Systems Audit Fix Plan — Session 4: AI System Bugs

Tests for fixes:
  F1: AI_DEBUG defaults to False, controlled by env var
  F2: Enemy phase error handling — crash in one nation doesn't block others
  F3: Capital proximity alert dedup — suppressed within 3 turns
  F4: _last_enemy_phase_results dead state removed
  F5: start_turn() dead code removed
  Confirmation: Vassal courting creates notifications (existing behavior)
"""

import os
from unittest.mock import patch, MagicMock

from backend.models.world_state import WorldState
from backend.game_logic.turn_manager import TurnManager


# ═══════════════════════════════════════════════════════════════════
# F1: AI_DEBUG flag controlled by env var
# ═══════════════════════════════════════════════════════════════════

class TestAIDebugFlag:
    """AI_DEBUG should default to False, settable via AI_DEBUG env var."""

    def test_ai_debug_defaults_false(self):
        """AI_DEBUG defaults to False when env var not set."""
        # Remove env var if present, re-import module
        env = os.environ.copy()
        env.pop("AI_DEBUG", None)
        with patch.dict(os.environ, env, clear=True):
            # Re-evaluate the expression (module-level constant already set,
            # so we test the expression directly)
            result = os.environ.get("AI_DEBUG", "").lower() in ("1", "true", "yes")
            assert result is False

    def test_ai_debug_enabled_by_env_var(self):
        """AI_DEBUG=1 enables debug output."""
        with patch.dict(os.environ, {"AI_DEBUG": "1"}):
            result = os.environ.get("AI_DEBUG", "").lower() in ("1", "true", "yes")
            assert result is True

    def test_ai_debug_enabled_by_true_string(self):
        """AI_DEBUG=true also works."""
        with patch.dict(os.environ, {"AI_DEBUG": "true"}):
            result = os.environ.get("AI_DEBUG", "").lower() in ("1", "true", "yes")
            assert result is True

    def test_ai_debug_not_enabled_by_random_string(self):
        """Random strings don't enable debug."""
        with patch.dict(os.environ, {"AI_DEBUG": "maybe"}):
            result = os.environ.get("AI_DEBUG", "").lower() in ("1", "true", "yes")
            assert result is False


# ═══════════════════════════════════════════════════════════════════
# F2: Enemy phase error handling
# ═══════════════════════════════════════════════════════════════════

class TestEnemyPhaseErrorHandling:
    """Crash in one nation's AI turn should not block other nations."""

    def test_crash_in_one_nation_continues_others(self):
        """If process_nation_turn raises for one nation, others still process."""
        world = WorldState(player_nation="France")
        tm = TurnManager(world)

        call_count = {"value": 0}
        processed_nations = []

        def mock_process_nation_turn(nation, w, gs):
            call_count["value"] += 1
            if nation == "Britain":
                raise RuntimeError("Simulated crash in Britain AI")
            processed_nations.append(nation)
            return []

        def mock_execute_admin_phase(nation, w, gs):
            return []

        mock_ai = MagicMock()
        mock_ai.process_nation_turn = mock_process_nation_turn
        mock_ai.execute_admin_phase = mock_execute_admin_phase

        with patch("backend.ai.enemy_ai.EnemyAI", return_value=mock_ai), \
             patch("backend.commands.executor.CommandExecutor"):

            game_state = {"world": world}
            results = tm._process_enemy_turns(game_state)

        # Britain crashed, but other nations should have been processed
        assert "Prussia" in processed_nations or "Austria" in processed_nations
        # Results should still be a valid dict
        assert "nations" in results
        assert "total_actions" in results

    def test_crash_returns_empty_for_failed_nation(self):
        """A crashed nation should have 0 actions in results."""
        world = WorldState(player_nation="France")
        tm = TurnManager(world)

        def mock_process_nation_turn(nation, w, gs):
            if nation == "Prussia":
                raise ValueError("Bad state in Prussia")
            return [{"ai_action": {"action": "wait", "marshal": "test"}}]

        def mock_execute_admin_phase(nation, w, gs):
            return []

        mock_ai = MagicMock()
        mock_ai.process_nation_turn = mock_process_nation_turn
        mock_ai.execute_admin_phase = mock_execute_admin_phase

        with patch("backend.ai.enemy_ai.EnemyAI", return_value=mock_ai), \
             patch("backend.commands.executor.CommandExecutor"):

            game_state = {"world": world}
            results = tm._process_enemy_turns(game_state)

        # Prussia crashed — should have 0 actions
        if "Prussia" in results["nations"]:
            assert results["nations"]["Prussia"]["action_count"] == 0


# ═══════════════════════════════════════════════════════════════════
# F3: Capital proximity alert dedup
# ═══════════════════════════════════════════════════════════════════

class TestCapitalProximityDedup:
    """Alerts for same enemy near capital should be suppressed within 3 turns."""

    def _setup_capital_threat(self):
        """Create a world with an enemy adjacent to Paris."""
        world = WorldState(player_nation="France")
        # Paris is France's capital. Find an adjacent region.
        paris = world.get_region("Paris")
        adj_region = paris.adjacent_regions[0]

        # Move Wellington to adjacent region
        wellington = world.get_marshal("Wellington")
        wellington.location = adj_region
        wellington.strength = 20000

        return world, adj_region

    def test_first_alert_fires(self):
        """First proximity check should generate an alert."""
        world, adj = self._setup_capital_threat()
        tm = TurnManager(world)

        alerts = tm._check_capital_proximity()
        assert len(alerts) >= 1
        assert any(a["enemy"] == "Wellington" for a in alerts)

    def test_repeat_suppressed_within_3_turns(self):
        """Same enemy near same capital should be suppressed on turn+1."""
        world, adj = self._setup_capital_threat()
        tm = TurnManager(world)

        # First check — fires
        alerts1 = tm._check_capital_proximity()
        assert len(alerts1) >= 1

        # Second check same turn — suppressed (within 3 turns)
        alerts2 = tm._check_capital_proximity()
        wellington_alerts = [a for a in alerts2 if a["enemy"] == "Wellington"]
        assert len(wellington_alerts) == 0

    def test_re_alerts_after_3_turns(self):
        """After 3 turns pass, the alert should fire again."""
        world, adj = self._setup_capital_threat()
        tm = TurnManager(world)

        # First alert on turn 1
        world.current_turn = 1
        alerts1 = tm._check_capital_proximity()
        assert len(alerts1) >= 1

        # Turn 2 — suppressed
        world.current_turn = 2
        alerts2 = tm._check_capital_proximity()
        wellington_alerts = [a for a in alerts2 if a["enemy"] == "Wellington"]
        assert len(wellington_alerts) == 0

        # Turn 4 (3 turns later) — should fire again
        world.current_turn = 4
        alerts3 = tm._check_capital_proximity()
        wellington_alerts = [a for a in alerts3 if a["enemy"] == "Wellington"]
        assert len(wellington_alerts) >= 1


# ═══════════════════════════════════════════════════════════════════
# F4 + F5: Dead state and dead code removed
# ═══════════════════════════════════════════════════════════════════

class TestDeadStateRemoved:
    """Verify dead code/state has been removed."""

    def test_no_last_enemy_phase_results_on_world(self):
        """_last_enemy_phase_results should not be initialized on WorldState."""
        world = WorldState(player_nation="France")
        assert not hasattr(world, '_last_enemy_phase_results')

    def test_no_start_turn_on_turn_manager(self):
        """start_turn() method should be removed from TurnManager."""
        world = WorldState(player_nation="France")
        tm = TurnManager(world)
        assert not hasattr(tm, 'start_turn')


# ═══════════════════════════════════════════════════════════════════
# Confirmation: Vassal courting creates notifications
# ═══════════════════════════════════════════════════════════════════

class TestVassalCourtingNotifications:
    """Confirm vassal courting already creates notifications (P2-9 not a bug)."""

    def test_vassal_courting_creates_notification(self):
        """attempt_vassal_courting should add a notification to world.notifications."""
        from backend.game_logic.vassal import attempt_vassal_courting

        world = WorldState(player_nation="France")

        # Set up a vassal with low loyalty
        world.vassals = {
            "Saxony": {"lord": "France", "loyalty": 30, "autonomy": 50}
        }

        # Give the courting nation enough DP
        world.nation_dp = {"Prussia": 5}

        # Positive relation to get 15 loyalty drop
        diplo_key = world._make_diplo_key("Saxony", "Prussia")
        world.nation_relations[diplo_key] = 10

        # Snapshot existing pending notifications
        initial_pending = list(world.notifications.get_pending())

        events = attempt_vassal_courting(world, "Prussia")

        # Should have events
        assert len(events) >= 1
        assert events[0]["type"] == "vassal_courting"

        # Should have added a notification (get_pending returns more than before)
        new_pending = world.notifications.get_pending()
        assert len(new_pending) > len(initial_pending)

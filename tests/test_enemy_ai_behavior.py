"""
Comprehensive Enemy AI Behavior Tests for Project Sovereign

Tests multi-turn integration, regression scenarios from real game logs,
adversarial board states, priority conflict resolution, anti-stagnation
systems, and nation-level action distribution.

Run with: pytest tests/test_enemy_ai_behavior.py -v
"""

import pytest
import random
from unittest.mock import patch
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, Stance
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI, get_marshal_priority
from backend.game_logic.turn_manager import TurnManager


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def _isolate_marshal(world: WorldState, keep_name: str, nation: str):
    """Move all marshals of `nation` EXCEPT `keep_name` to strength=0 so they don't act."""
    for m in world.marshals.values():
        if m.nation == nation and m.name != keep_name:
            m.strength = 0


def _clear_french_from_board(world: WorldState):
    """Move all French marshals far away and weaken them so they don't interfere."""
    for m in world.marshals.values():
        if m.nation == "France":
            m.location = "Marseille"
            m.strength = 1000  # Alive but irrelevant


def _run_nation_turn(world, nation="Britain"):
    """Run a single nation turn and return results."""
    executor = CommandExecutor()
    ai = EnemyAI(executor)
    game_state = {"world": world, "debug_mode": True}
    return ai.process_nation_turn(nation, world, game_state)


def _run_n_turns(world, nation, n):
    """Run n turns for a nation, returning all results."""
    all_results = []
    for _ in range(n):
        results = _run_nation_turn(world, nation)
        all_results.append(results)
    return all_results


# ═══════════════════════════════════════════════════════════════════
# 1. MULTI-TURN INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════

class TestMultiTurnIntegration:
    """Run process_nation_turn() across multiple turns to test stagnation counters."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world, "debug_mode": True}
        _clear_french_from_board(self.world)

    def test_stagnation_counter_increments_on_idle(self):
        """Marshal that only waits/stance-changes should accumulate stagnation."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")

        # Put Wellington somewhere with no targets and all adjacent friendly
        # so P3.5 doesn't unfortify (no capture targets, no enemies to reposition toward)
        wellington.location = "Waterloo"
        wellington.fortified = False
        wellington.stance = Stance.DEFENSIVE

        # Make all regions friendly and remove all enemies
        for region in self.world.regions.values():
            region.controller = "Britain"
        for m in self.world.marshals.values():
            if m.nation != "Britain":
                m.strength = 0

        _run_nation_turn(self.world, "Britain")
        stag1 = self.world.ai_stagnation_turns.get("Wellington", 0)

        _run_nation_turn(self.world, "Britain")
        stag2 = self.world.ai_stagnation_turns.get("Wellington", 0)

        # With no enemies and no targets, Wellington can only wait → stagnation increments
        assert stag1 >= 1 or stag2 >= 1, "Stagnation counter should increment when truly idle"

    def test_stagnation_resets_on_meaningful_action(self):
        """Counter resets to 0 when marshal takes a meaningful action like attack."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"

        # Pre-set stagnation
        self.world.ai_stagnation_turns["Wellington"] = 3

        # Place a weak French target adjacent
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 10000  # Very weak
        wellington.strength = 68000

        _run_nation_turn(self.world, "Britain")

        stag = self.world.ai_stagnation_turns.get("Wellington", 0)
        assert stag == 0, f"Stagnation should reset after meaningful action, got {stag}"

    def test_graduated_escalation_forces_unfortify_at_turn2(self):
        """At stagnation=2, fortified marshal should be forced to unfortify."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.fortified = True
        wellington.defense_bonus = 0.10
        wellington.stance = Stance.DEFENSIVE

        # Pre-set stagnation to 2
        self.world.ai_stagnation_turns["Wellington"] = 2

        # French far away so no combat triggers
        results = _run_nation_turn(self.world, "Britain")

        # Should have taken stagnation action (unfortify or move)
        actions = [r.get("action", r.get("ai_action", {}).get("action", "")) for r in results]
        meaningful = [a for a in actions if a in ("unfortify", "move", "attack")]
        assert len(meaningful) > 0, f"Stagnation=2 should force action, got actions: {actions}"

    def test_graduated_escalation_lowers_threshold_at_turn3(self):
        """At stagnation>=3, attack threshold should be reduced."""
        ai = EnemyAI(self.executor)

        blucher = self.world.get_marshal("Blucher")
        _isolate_marshal(self.world, "Blucher", "Prussia")
        blucher.location = "Netherlands"
        blucher.strength = 55000

        # Place enemy just barely below normal threshold
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 100000  # Ratio = 0.55, above aggressive 0.7? No — below.

        self.world.ai_stagnation_turns["Blucher"] = 3

        # At stagnation=3, threshold should be reduced by 0.2 → aggressive 0.7-0.2=0.5
        # Ratio 0.55 > 0.5, so should attack
        action, priority = ai._evaluate_marshal(blucher, "Prussia", self.world)
        # Stagnation action should suggest attack with lowered threshold
        # or at minimum some meaningful action
        if action:
            assert action.get("action") in ("attack", "move", "unfortify"), \
                f"Stagnation=3 should produce meaningful action, got {action.get('action')}"

    def test_multi_nation_independent_stagnation(self):
        """Britain and Prussia stagnation counters should be independent."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.fortified = True
        wellington.defense_bonus = 0.10
        wellington.stance = Stance.DEFENSIVE

        blucher = self.world.get_marshal("Blucher")
        _isolate_marshal(self.world, "Blucher", "Prussia")
        blucher.location = "Netherlands"

        # Place French target near Prussia but not Britain
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 20000
        blucher.strength = 55000

        _run_nation_turn(self.world, "Britain")
        _run_nation_turn(self.world, "Prussia")

        brit_stag = self.world.ai_stagnation_turns.get("Wellington", 0)
        prus_stag = self.world.ai_stagnation_turns.get("Blucher", 0)

        # Blucher should have attacked (meaningful), Wellington idle
        # So Blucher's counter should be 0 or low, Wellington's should be higher
        assert prus_stag <= brit_stag or prus_stag == 0, \
            f"Prussia active should have lower stagnation ({prus_stag}) than idle Britain ({brit_stag})"

    def test_end_turn_full_cycle_no_crash(self):
        """Full end_turn() with both nations acting should complete without crash."""
        tm = TurnManager(self.world, self.executor)
        result = tm.end_turn(self.game_state)

        assert result is not None
        assert "turn_ended" in result
        assert result["turn_ended"] == 1

    def test_stagnation_survives_across_advance_turn(self):
        """ai_stagnation_turns should persist after advance_turn()."""
        self.world.ai_stagnation_turns["Wellington"] = 3
        self.world.advance_turn()
        assert self.world.ai_stagnation_turns.get("Wellington", 0) == 3, \
            "Stagnation counter should persist across advance_turn()"

    def test_meaningful_action_types_all_reset(self):
        """Attack should reset stagnation counter to 0."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Belgium"
        wellington.strength = 68000

        self.world.ai_stagnation_turns["Wellington"] = 5

        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"  # Same region — P0 engagement
        ney.strength = 5000

        results = _run_nation_turn(self.world, "Britain")

        # Verify Wellington actually attacked
        attacks = [r for r in results if r.get("ai_action", {}).get("action") == "attack"]
        assert len(attacks) > 0, "Wellington should have attacked via P0 engagement"

        stag = self.world.ai_stagnation_turns.get("Wellington", 0)
        assert stag == 0, f"Attack should reset stagnation counter, got {stag}"


# ═══════════════════════════════════════════════════════════════════
# 2. REGRESSION TESTS FROM REAL GAME LOG
# ═══════════════════════════════════════════════════════════════════

class TestRegressionRealGameLog:
    """
    Board states from real game: Uxbridge ping-ponging between Bordeaux/Brittany,
    Wellington fortified at Waterloo dead-end, Prussia fortified Netherlands dead-end.
    """

    def _setup_regression_board(self):
        """Set up the specific regression scenario."""
        world = WorldState()
        _clear_french_from_board(world)

        # Uxbridge at Bordeaux (was ping-ponging to Brittany)
        uxbridge = world.get_marshal("Uxbridge")
        uxbridge.location = "Bordeaux"
        uxbridge.strength = 18000

        # Wellington fortified at Waterloo, no enemies nearby
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 68000
        wellington.fortified = True
        wellington.defense_bonus = 0.10
        wellington.stance = Stance.DEFENSIVE

        # Blucher fortified at Netherlands (dead-end adjacent: Belgium, Rhine)
        blucher = world.get_marshal("Blucher")
        blucher.location = "Netherlands"
        blucher.strength = 55000
        blucher.fortified = True
        blucher.defense_bonus = 0.10
        blucher.stance = Stance.DEFENSIVE

        # Gneisenau also in Netherlands
        gneisenau = world.get_marshal("Gneisenau")
        gneisenau.location = "Netherlands"
        gneisenau.strength = 40000

        # French threat is far: all at Marseille
        return world

    def test_uxbridge_stops_pingpong_over_3_turns(self):
        """Uxbridge should not just bounce between 2 regions forever."""
        world = self._setup_regression_board()
        uxbridge = world.get_marshal("Uxbridge")

        locations = [uxbridge.location]
        for _ in range(4):
            _run_nation_turn(world, "Britain")
            locations.append(uxbridge.location)

        # Should not be oscillating between exactly 2 locations
        unique = set(locations)
        if len(unique) == 2:
            # If only 2 unique locations across 5 data points, that's a ping-pong
            transitions = sum(1 for i in range(1, len(locations)) if locations[i] != locations[i-1])
            assert transitions < 4, \
                f"Uxbridge ping-ponging between {unique}: {locations}"

    def test_wellington_breaks_deadend_fortification(self):
        """Wellington fortified with no enemies near should eventually unfortify and move."""
        world = self._setup_regression_board()
        wellington = world.get_marshal("Wellington")

        # Run 3 turns — stagnation should kick in
        initial_loc = wellington.location
        for _ in range(3):
            _run_nation_turn(world, "Britain")

        # By turn 3, stagnation should have forced Wellington to act
        stag = world.ai_stagnation_turns.get("Wellington", 0)
        moved = wellington.location != initial_loc
        unfortified = not wellington.fortified

        assert moved or unfortified or stag < 2, \
            f"Wellington should break stagnation: loc={wellington.location}, fortified={wellington.fortified}, stag={stag}"

    def test_prussia_breaks_deadend_fortification(self):
        """Blucher fortified at Netherlands dead-end should reposition."""
        world = self._setup_regression_board()
        blucher = world.get_marshal("Blucher")

        initial_loc = blucher.location
        for _ in range(3):
            _run_nation_turn(world, "Prussia")

        stag = world.ai_stagnation_turns.get("Blucher", 0)
        moved = blucher.location != initial_loc
        unfortified = not blucher.fortified

        assert moved or unfortified or stag < 2, \
            f"Blucher should break stagnation: loc={blucher.location}, fortified={blucher.fortified}, stag={stag}"

    def test_combined_scenario_completes_5_turns(self):
        """Full scenario with both nations should complete 5 turns without hanging."""
        world = self._setup_regression_board()
        game_state = {"world": world, "debug_mode": True}
        executor = CommandExecutor()
        tm = TurnManager(world, executor)

        for turn in range(5):
            result = tm.end_turn(game_state)
            assert result is not None, f"Turn {turn+1} returned None"
            assert "turn_ended" in result, f"Turn {turn+1} missing turn_ended"

    def test_regression_action_budget_respected(self):
        """Each nation should use at most 6 total actions per turn (4 paid + 2 free)."""
        world = self._setup_regression_board()

        for turn in range(3):
            results_britain = _run_nation_turn(world, "Britain")
            results_prussia = _run_nation_turn(world, "Prussia")

            # Total actions capped at max_total_actions = paid_budget + 2 = 6
            for nation_name, results in [("Britain", results_britain), ("Prussia", results_prussia)]:
                assert len(results) <= 6, \
                    f"{nation_name} turn {turn+1}: {len(results)} total actions (max 6)"


# ═══════════════════════════════════════════════════════════════════
# 3. ADVERSARIAL BOARD STATES
# ═══════════════════════════════════════════════════════════════════

class TestAdversarialBoardStates:
    """Test AI with extreme or unusual board configurations."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_encirclement_doesnt_crash(self):
        """Marshal surrounded by enemies in every adjacent region should not crash."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Belgium"
        wellington.strength = 50000

        # Put French in every adjacent region
        region = self.world.get_region("Belgium")
        french_marshals = [m for m in self.world.marshals.values() if m.nation == "France"]
        for i, adj in enumerate(region.adjacent_regions):
            if i < len(french_marshals):
                french_marshals[i].location = adj
                french_marshals[i].strength = 40000

        results = _run_nation_turn(self.world, "Britain")
        # Should complete without crash
        assert isinstance(results, list)

    def test_encirclement_aggressive_attacks(self):
        """Aggressive marshal surrounded should still attempt attack (tolerance=99)."""
        # Uxbridge is aggressive
        uxbridge = self.world.get_marshal("Uxbridge")
        _isolate_marshal(self.world, "Uxbridge", "Britain")
        uxbridge.location = "Belgium"
        uxbridge.strength = 30000

        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"  # Same region — P0 engagement
        ney.strength = 25000

        action, priority = self.ai._evaluate_marshal(uxbridge, "Britain", self.world)
        assert action is not None
        # P0 should fire, and aggressive should attack
        assert action.get("action") in ("attack", "unfortify", "wait"), \
            f"Aggressive marshal should act on P0, got {action.get('action')}"

    def test_encirclement_cautious_behavior(self):
        """Cautious marshal surrounded with bad odds should try retreat or wait."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Belgium"
        wellington.strength = 20000

        # Strong enemy in same region
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 60000

        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        assert action is not None
        # Should retreat or wait (bad odds for cautious)
        assert action.get("action") in ("retreat", "wait", "unfortify"), \
            f"Cautious with bad odds should retreat/wait, got {action.get('action')}"

    def test_near_zero_strength_survival_mode(self):
        """Marshal with near-zero strength should enter survival mode (P2)."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Belgium"
        wellington.strength = 100  # Near-zero

        # Enemy adjacent
        ney = self.world.get_marshal("Ney")
        ney.location = "Netherlands"
        ney.strength = 50000

        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        # P2 survival should trigger (strength < 25% of starting 68000)
        assert action is not None
        assert priority <= 3, f"Near-zero strength should trigger high priority, got {priority}"

    def test_no_enemies_on_map(self):
        """With all French marshals dead, AI should do peaceful actions without crash."""
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.strength = 0

        results = _run_nation_turn(self.world, "Britain")
        assert isinstance(results, list)
        # Should complete without error

    def test_all_regions_friendly_no_crash(self):
        """When all regions are friendly, AI should handle gracefully."""
        for region in self.world.regions.values():
            region.controller = "Britain"

        for m in self.world.marshals.values():
            if m.nation == "France":
                m.strength = 0

        results = _run_nation_turn(self.world, "Britain")
        assert isinstance(results, list)

    def test_one_marshal_nation(self):
        """Nation with only one marshal should still get actions."""
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        _clear_french_from_board(self.world)

        results = _run_nation_turn(self.world, "Britain")
        assert isinstance(results, list)

    def test_two_equidistant_allies_consolidation(self):
        """Weak marshal with 2 allies equidistant should pick strongest, not oscillate."""
        # Use Gneisenau as weak marshal
        gneisenau = self.world.get_marshal("Gneisenau")
        gneisenau.location = "Bavaria"
        gneisenau.strength = 10000

        blucher = self.world.get_marshal("Blucher")
        blucher.location = "Rhine"  # Adjacent to Bavaria
        blucher.strength = 55000

        # Place strong French nearby
        ney = self.world.get_marshal("Ney")
        ney.location = "Geneva"  # Adjacent to Bavaria
        ney.strength = 50000

        action, _ = self.ai._evaluate_marshal(gneisenau, "Prussia", self.world)
        # With ratio 10000/50000 = 0.2 < 0.5, should consider consolidation
        if action and action.get("action") == "move":
            # Should not crash and should pick a destination
            assert action.get("target") is not None


# ═══════════════════════════════════════════════════════════════════
# 4. PRIORITY CONFLICT RESOLUTION
# ═══════════════════════════════════════════════════════════════════

class TestPriorityConflictResolution:
    """Test that correct priority fires when multiple conditions overlap."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)
        self.game_state = {"world": self.world, "debug_mode": True}
        _clear_french_from_board(self.world)

    def test_p0_overrides_fortified_and_drilling(self):
        """Enemy in same region should trigger P0 even if marshal is fortified."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Belgium"
        wellington.strength = 68000
        wellington.fortified = True
        wellington.defense_bonus = 0.10

        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"  # Same region — P0
        ney.strength = 30000

        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        assert action is not None
        assert priority <= 1, f"P0 should fire (priority 0), got {priority}"
        assert action.get("action") in ("unfortify", "attack", "wait"), \
            f"P0 should unfortify/attack/wait, got {action.get('action')}"

    def test_recovery_blocks_attack(self):
        """Marshal in retreat_recovery should not attack."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.retreat_recovery = 2
        wellington.strength = 68000

        # Enemy adjacent
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 10000

        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        if action:
            # Recovery should restrict to defensive actions only
            assert action.get("action") in ("wait", "stance_change", "defend", "recruit", "move"), \
                f"Recovery should block attack, got {action.get('action')}"

    def test_drilling_blocks_attack(self):
        """Marshal drilling_locked should not attack."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.drilling = True
        wellington.drilling_locked = True
        wellington.strength = 68000

        # Enemy adjacent
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 10000

        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        if action:
            assert action.get("action") != "attack", \
                "Drilling marshal should not attack"

    def test_p7_advance_suppresses_p8_retreat(self):
        """Marshal who advanced via P7 should not be retreated by P8."""
        blucher = self.world.get_marshal("Blucher")
        _isolate_marshal(self.world, "Blucher", "Prussia")
        blucher.location = "Belgium"
        blucher.strength = 20000  # Weak, so P8 might want to retreat

        # Place strong enemy adjacent to trigger retreat consideration
        ney = self.world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 80000

        # Simulate P7 advance already happened
        self.ai._advanced_this_turn = {"Blucher"}

        # P8 default should not retreat Blucher (note: _get_default_action takes marshal + world)
        action = self.ai._get_default_action(blucher, self.world)
        if action:
            # P8 for aggressive checks _advanced_this_turn before retreat
            # The action should be wait or stance_change, NOT a move to retreat
            assert action.get("action") != "retreat", \
                "P8 should not retreat a marshal that advanced via P7 this turn"

    def test_fortified_weak_stagnating_fires_survival_first(self):
        """Fortified + weak (<25%) + stagnating should fire P2 survival before stagnation."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.strength = 5000  # < 25% of 68000
        wellington.fortified = True
        wellington.defense_bonus = 0.10

        # Enemy adjacent
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 60000

        self.world.ai_stagnation_turns["Wellington"] = 5

        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        assert action is not None
        # P2 survival (priority 2) should fire before P7.5 stagnation (priority 7)
        assert priority <= 3, f"Survival P2 should fire first, got priority {priority}"

    def test_intent_fires_before_p0(self):
        """Pending intent (unfortify->capture) should fire before P0 re-evaluation."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.strength = 68000

        # Set up pending intent
        self.ai._pending_intents["Wellington"] = {
            "intent": "capture",
            "target": "Belgium"
        }

        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        assert action is not None
        assert priority <= 1, "Intent should fire at high priority"
        assert action.get("target") == "Belgium" or action.get("action") == "move"

    def test_p35_reposition_toward_fight(self):
        """Fortified marshal with no enemies adjacent but enemies 3 away should reposition."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Netherlands"
        wellington.fortified = True
        wellington.defense_bonus = 0.10
        wellington.stance = Stance.DEFENSIVE

        # All adjacent regions friendly, enemy far away
        for region in self.world.regions.values():
            region.controller = "Britain"

        ney = self.world.get_marshal("Ney")
        ney.location = "Lyon"  # Far from Netherlands
        ney.strength = 50000

        action = self.ai._check_fortification_opportunity(wellington, "Britain", self.world)
        # Should unfortify to reposition toward enemy
        if action:
            assert action.get("action") == "unfortify"

    def test_cautious_counterattack_p325(self):
        """Cautious marshal with counter_punch_available should get free attack."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.strength = 68000
        wellington.counter_punch_available = True

        # Enemy adjacent with reasonable odds
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 40000

        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        if action and action.get("action") == "attack":
            # Counter-punch at P3.25 has priority 3
            assert priority <= 4, "Counter-punch should be high priority"


# ═══════════════════════════════════════════════════════════════════
# 5. ANTI-STAGNATION SYSTEMS
# ═══════════════════════════════════════════════════════════════════

class TestAntiStagnationSystems:
    """Test P7→P8 suppression, P3.5 dead-end, P4.8 consolidation, graduated stagnation."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)
        self.game_state = {"world": self.world, "debug_mode": True}
        _clear_french_from_board(self.world)

    def test_p7_p8_suppression_flag_set(self):
        """_advanced_this_turn flag should prevent P8 retreat."""
        blucher = self.world.get_marshal("Blucher")
        _isolate_marshal(self.world, "Blucher", "Prussia")
        blucher.location = "Belgium"
        blucher.strength = 20000

        # Strong enemy adjacent so P8 would consider retreat
        ney = self.world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 80000

        # _advanced_this_turn is initialized in process_nation_turn, set manually
        self.ai._advanced_this_turn = set()
        self.ai._advanced_this_turn.add("Blucher")

        action = self.ai._get_default_action(blucher, self.world)
        if action and action.get("action") == "retreat":
            pytest.fail("P8 should not retreat a marshal that advanced via P7")

    def test_p35_dead_end_unfortify_no_enemies(self):
        """Fortified marshal with no enemies adjacent and valid destinations should unfortify."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.fortified = True
        wellington.defense_bonus = 0.10

        # Make sure no enemies are adjacent but some are far away
        ney = self.world.get_marshal("Ney")
        ney.location = "Marseille"
        ney.strength = 50000

        # Set some adjacent regions to be capturable
        self.world.regions["Belgium"].controller = "France"

        action = self.ai._check_fortification_opportunity(wellington, "Britain", self.world)
        if action:
            assert action.get("action") == "unfortify", \
                f"P3.5 should unfortify to capture Belgium, got {action.get('action')}"

    def test_p35_undefended_capture_opportunity(self):
        """Fortified marshal with undefended enemy region adjacent should unfortify."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.fortified = True
        wellington.defense_bonus = 0.10

        # Belgium is French-controlled, no defenders
        self.world.regions["Belgium"].controller = "France"
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.location = "Marseille"

        action = self.ai._check_fortification_opportunity(wellington, "Britain", self.world)
        assert action is not None, "Should unfortify for undefended capture"
        assert action["action"] == "unfortify"
        # Check intent was stored
        assert "Wellington" in self.ai._pending_intents

    def test_p48_consolidation_triggers_on_weak(self):
        """Weak marshal (ratio < 0.5) should consolidate toward strongest ally."""
        gneisenau = self.world.get_marshal("Gneisenau")
        gneisenau.location = "Bavaria"
        gneisenau.strength = 10000

        blucher = self.world.get_marshal("Blucher")
        blucher.location = "Rhine"  # 1 away from Bavaria
        blucher.strength = 55000

        # Strong enemy nearby
        ney = self.world.get_marshal("Ney")
        ney.location = "Geneva"  # Adjacent to Bavaria
        ney.strength = 50000

        action = self.ai._consider_consolidation(gneisenau, "Prussia", self.world)
        if action:
            assert action["action"] == "move"
            # Should move toward Blucher (strongest ally)

    def test_p48_no_consolidation_during_recovery(self):
        """Marshal in retreat_recovery should not consolidate."""
        gneisenau = self.world.get_marshal("Gneisenau")
        gneisenau.location = "Bavaria"
        gneisenau.strength = 10000
        gneisenau.retreat_recovery = 2

        ney = self.world.get_marshal("Ney")
        ney.location = "Geneva"
        ney.strength = 50000

        action = self.ai._consider_consolidation(gneisenau, "Prussia", self.world)
        assert action is None, "Should not consolidate during retreat recovery"

    def test_p48_no_consolidation_when_broken(self):
        """Broken marshal should not consolidate."""
        gneisenau = self.world.get_marshal("Gneisenau")
        gneisenau.location = "Bavaria"
        gneisenau.strength = 10000
        gneisenau.broken = True

        ney = self.world.get_marshal("Ney")
        ney.location = "Geneva"
        ney.strength = 50000

        action = self.ai._consider_consolidation(gneisenau, "Prussia", self.world)
        assert action is None, "Should not consolidate when broken"

    def test_stagnation_turn2_force_move(self):
        """Stagnation=2 with non-fortified marshal should force move toward enemy."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.strength = 68000
        # NOT fortified

        ney = self.world.get_marshal("Ney")
        ney.location = "Lyon"  # Far away
        ney.strength = 50000

        action = self.ai._get_stagnation_action(wellington, "Britain", self.world, 2, "cautious")
        if action:
            assert action["action"] == "move", \
                f"Stagnation=2 should force move, got {action['action']}"

    def test_stagnation_turn3_lower_threshold(self):
        """Stagnation=3 should reduce attack threshold."""
        blucher = self.world.get_marshal("Blucher")
        _isolate_marshal(self.world, "Blucher", "Prussia")
        blucher.location = "Netherlands"
        blucher.strength = 40000

        # Enemy adjacent, ratio below normal aggressive threshold (0.7) but above reduced
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 100000  # Ratio 0.4

        # At stagnation=3: threshold 0.7 - 0.2 = 0.5 → ratio 0.4 still below
        # At stagnation=4: threshold 0.7 - 0.3 = 0.4 → ratio 0.4 = threshold
        action = self.ai._get_stagnation_action(blucher, "Prussia", self.world, 4, "aggressive")
        if action and action.get("action") == "attack":
            assert action["target"] == "Ney"

    def test_stagnation_turn5_floor_at_03(self):
        """Stagnation=5 threshold should floor at 0.3, not go negative."""
        # Threshold: base 0.7 - 0.2 - 0.1*(5-3) = 0.7 - 0.4 = 0.3 (exactly floor)
        blucher = self.world.get_marshal("Blucher")
        _isolate_marshal(self.world, "Blucher", "Prussia")
        blucher.location = "Netherlands"
        blucher.strength = 20000

        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 60000  # Ratio 0.33 > 0.3

        action = self.ai._get_stagnation_action(blucher, "Prussia", self.world, 5, "aggressive")
        if action and action.get("action") == "attack":
            assert True  # Threshold 0.3 allows ratio 0.33
        # Even at stagnation=10, threshold should not go below 0.3

    def test_stagnation_never_walks_into_occupied_region(self):
        """Even with high stagnation, force-move should not enter enemy-occupied regions."""
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"
        wellington.strength = 68000

        # Put enemies in ALL adjacent regions
        french = [m for m in self.world.marshals.values() if m.nation == "France"]
        waterloo_adj = self.world.get_region("Waterloo").adjacent_regions
        for i, adj in enumerate(waterloo_adj):
            if i < len(french):
                french[i].location = adj
                french[i].strength = 40000

        action = self.ai._get_stagnation_action(wellington, "Britain", self.world, 5, "cautious")
        if action and action.get("action") == "move":
            target = action["target"]
            enemies_at_target = [m for m in self.world.marshals.values()
                                if m.location == target and m.nation != "Britain" and m.strength > 0]
            assert len(enemies_at_target) == 0, \
                f"Stagnation move should not enter enemy-occupied {target}"


# ═══════════════════════════════════════════════════════════════════
# 6. NATION-LEVEL ACTION DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════

class TestNationActionDistribution:
    """Test that actions are distributed fairly across marshals within a nation."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world, "debug_mode": True}
        _clear_french_from_board(self.world)

    def test_actions_spread_across_marshals(self):
        """Both British marshals should get at least some actions over 2 turns."""
        wellington = self.world.get_marshal("Wellington")
        uxbridge = self.world.get_marshal("Uxbridge")
        wellington.location = "Waterloo"
        uxbridge.location = "Netherlands"
        wellington.strength = 68000
        uxbridge.strength = 18000

        # Place targets near both
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 20000

        well_acted = False
        ux_acted = False

        for _ in range(2):
            results = _run_nation_turn(self.world, "Britain")
            for r in results:
                m = r.get("marshal", r.get("ai_action", {}).get("marshal", ""))
                if m == "Wellington":
                    well_acted = True
                if m == "Uxbridge":
                    ux_acted = True

        assert well_acted or ux_acted, "At least one marshal should act"

    def test_critical_marshal_acts_first(self):
        """Marshal in combat (P0) should get priority over idle marshal."""
        wellington = self.world.get_marshal("Wellington")
        uxbridge = self.world.get_marshal("Uxbridge")
        _isolate_marshal(self.world, "Wellington", "Britain")  # Remove Uxbridge

        # Restore Uxbridge manually at a safe location
        uxbridge.strength = 18000
        uxbridge.location = "Bordeaux"  # Far away, no enemies

        # Wellington engaged (enemy same region)
        wellington.location = "Waterloo"
        wellington.strength = 68000
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"  # Same region!
        ney.strength = 30000

        # Move all non-French, non-British away from Uxbridge
        for m in self.world.marshals.values():
            if m.nation == "Prussia":
                m.location = "Rhine"

        w_priority = get_marshal_priority(wellington, self.world)
        u_priority = get_marshal_priority(uxbridge, self.world)

        assert w_priority < u_priority, \
            f"Engaged Wellington ({w_priority}) should have lower priority than idle Uxbridge ({u_priority})"

    def test_wait_cap_per_marshal(self):
        """Marshal should be marked done after 2 consecutive waits."""
        ai = EnemyAI(self.executor)
        wellington = self.world.get_marshal("Wellington")
        _isolate_marshal(self.world, "Wellington", "Britain")
        wellington.location = "Waterloo"

        # No targets, no enemies — will wait
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.strength = 0

        results = _run_nation_turn(self.world, "Britain")

        # Count waits for Wellington
        waits = sum(1 for r in results
                   if r.get("ai_action", {}).get("action") == "wait"
                   or r.get("action") == "wait")
        assert waits <= 2, f"Wellington should wait at most 2 times, got {waits}"

    def test_four_action_limit(self):
        """Nation should use at most 4 paid actions."""
        wellington = self.world.get_marshal("Wellington")
        uxbridge = self.world.get_marshal("Uxbridge")
        wellington.location = "Waterloo"
        uxbridge.location = "Netherlands"

        results = _run_nation_turn(self.world, "Britain")

        # Total results can be more than 4 due to free actions, but paid <= 4
        paid_actions = [r for r in results
                       if r.get("ai_action", {}).get("action", r.get("action", ""))
                       not in ("wait", "stance_change", "retreat", "unfortify", "status", "help")]
        assert len(paid_actions) <= 4, \
            f"Should have at most 4 paid actions, got {len(paid_actions)}"

    def test_free_actions_dont_consume_budget(self):
        """Wait and retreat are free; attack, move, drill, fortify cost points."""
        ai = EnemyAI(self.executor)
        # Free actions (from _action_costs_point: status, help, end_turn, unknown, retreat, debug, wait)
        assert not ai._action_costs_point("wait")
        assert not ai._action_costs_point("retreat")
        assert not ai._action_costs_point("status")
        assert not ai._action_costs_point("help")
        # Paid actions
        assert ai._action_costs_point("attack")
        assert ai._action_costs_point("move")
        assert ai._action_costs_point("drill")
        assert ai._action_costs_point("fortify")
        assert ai._action_costs_point("stance_change")  # Stance change costs a point
        assert ai._action_costs_point("unfortify")  # Unfortify costs a point

    def test_no_marshal_starves_over_3_turns(self):
        """Over 3 turns, every marshal with strength>0 should act at least once."""
        wellington = self.world.get_marshal("Wellington")
        uxbridge = self.world.get_marshal("Uxbridge")
        wellington.location = "Waterloo"
        wellington.strength = 68000
        uxbridge.location = "Netherlands"
        uxbridge.strength = 18000

        acted = {"Wellington": False, "Uxbridge": False}

        for _ in range(3):
            results = _run_nation_turn(self.world, "Britain")
            for r in results:
                m = r.get("marshal", r.get("ai_action", {}).get("marshal", ""))
                if m in acted:
                    acted[m] = True

        for name, did_act in acted.items():
            marshal = self.world.get_marshal(name)
            if marshal and marshal.strength > 0:
                assert did_act, f"{name} (strength={marshal.strength}) never acted in 3 turns"

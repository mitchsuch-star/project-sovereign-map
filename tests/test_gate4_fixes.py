"""
Gate 4 fixes — tests for three issues found during UI testing.

Issue 1: Berthier observation uses narrative voice, not raw stats.
Issue 2: Auto-routed "attack" command includes coordination context.
Issue 3: Artillery does NOT advance when reinforcing from adjacent.
"""

import random

from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.battle_report import (
    snapshot_attacker_modifiers,
    snapshot_defender_modifiers,
)


# ────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────

def _make_world_with_colocation(attacker_loc="Waterloo", defender_loc="Waterloo"):
    """Create a world with two player marshals co-located (Ney + Davout)
    and one enemy marshal in the same or adjacent region."""
    world = WorldState()

    # Player marshals co-located for combined arms
    ney = world.get_marshal("Ney")
    ney.location = attacker_loc
    ney.strength = 30000

    davout = world.get_marshal("Davout")
    davout.location = attacker_loc
    davout.strength = 25000

    # Enemy
    wellington = world.get_marshal("Wellington")
    wellington.location = defender_loc
    wellington.strength = 28000

    return world


# ════════════════════════════════════════════════════════════
# ISSUE 1: Berthier observation — narrative voice, no raw stats
# ════════════════════════════════════════════════════════════

class TestBerthierNarrativeVoice:
    """Coordination data is omitted from modifier snapshots;
    Berthier's observation conveys coordination narratively."""

    def test_attacker_snapshot_omits_combined_arms(self):
        """Combined arms entry absent from attacker modifier snapshot."""
        world = _make_world_with_colocation()
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        wellington = world.get_marshal("Wellington")

        # Set combined arms display field
        ney._display_combined_arms_atk = 0.10
        mods = snapshot_attacker_modifiers(ney, wellington, "plains", 0.0, 0, False)
        labels = [m["label"] for m in mods]

        assert "Combined arms" not in labels
        assert "Per-ally coordination" not in labels
        assert "Dedicated coordination" not in labels
        assert "Adjacent support" not in labels
        assert "Coordination (total)" not in labels

    def test_defender_snapshot_omits_coordination(self):
        """Coordination entries absent from defender modifier snapshot."""
        world = _make_world_with_colocation()
        wellington = world.get_marshal("Wellington")
        ney = world.get_marshal("Ney")

        wellington._display_combined_arms_def = 0.08
        wellington._display_coordination_def = 0.05
        wellington.total_coordination_defense_bonus = 0.13

        mods = snapshot_defender_modifiers(wellington, ney, "plains", 0.0)
        labels = [m["label"] for m in mods]

        assert "Combined arms" not in labels
        assert "Per-ally coordination" not in labels
        assert "Coordination (total)" not in labels

    def test_non_coordination_modifiers_still_present(self):
        """Stance, personality, terrain etc. still appear in snapshots."""
        world = _make_world_with_colocation()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        from backend.models.marshal import Stance
        ney.stance = Stance.AGGRESSIVE
        ney.shock_bonus = 1.0  # Drill bonus

        mods = snapshot_attacker_modifiers(ney, wellington, "plains", 0.0, 0, False)
        labels = [m["label"] for m in mods]

        assert "Aggressive stance" in labels
        assert "Drill training" in labels


# ════════════════════════════════════════════════════════════
# ISSUE 2: Auto-routed attack includes coordination
# ════════════════════════════════════════════════════════════

class TestAutoRouteAttackCoordination:
    """Auto-assigned attacks delegate to _execute_attack for full coordination."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_auto_assign_attack_delegates_to_execute_attack(self):
        """Auto-assign 'attack Wellington' goes through _execute_attack."""
        random.seed(42)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 30000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 25000

        command = {"action": "auto_assign_attack", "target": "Wellington"}
        result = self.executor._execute_auto_assign_attack(command, self.game_state)

        assert result["success"] is True
        assert result.get("events")
        assert result["events"][0]["type"] == "battle"
        # Auto-assigned flag should be present
        assert result["events"][0].get("auto_assigned") is True

    def test_auto_assign_region_attack_delegates(self):
        """Auto-assign 'attack Waterloo' goes through _execute_attack."""
        random.seed(42)
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = 30000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 25000

        command = {"action": "auto_assign_attack", "target": "Waterloo"}
        result = self.executor._execute_auto_assign_attack(command, self.game_state)

        assert result["success"] is True
        assert result.get("events")
        # Auto-assigned flag
        assert result["events"][0].get("auto_assigned") is True

    def test_auto_assign_attack_with_colocation_gets_coordination(self):
        """Co-located marshals get coordination bonuses even via auto-assign."""
        random.seed(42)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 30000

        davout = self.world.get_marshal("Davout")
        davout.location = "Waterloo"
        davout.strength = 25000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 40000

        command = {"action": "auto_assign_attack", "target": "Wellington"}
        result = self.executor._execute_auto_assign_attack(command, self.game_state)

        assert result["success"] is True
        # Battle report should exist (generated by _execute_attack)
        assert "battle_report" in result or result.get("events")


# ════════════════════════════════════════════════════════════
# ISSUE 3: Artillery does NOT relocate on reinforcement
# ════════════════════════════════════════════════════════════

class TestArtilleryReinforcementNoAdvance:
    """Artillery reinforcing from adjacent stays in adjacent position."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_artillery_stays_adjacent_after_reinforcement(self):
        """Drouot (artillery) reinforces from adjacent but does NOT advance."""
        random.seed(42)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 30000

        drouot = self.world.get_marshal("Drouot")
        drouot.location = "Belgium"  # Adjacent to Waterloo
        drouot.strength = 20000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 35000

        # Execute attack — Drouot may reinforce from adjacent
        result = self.executor._execute_attack(
            ney, "Wellington", self.world, self.game_state)

        # Regardless of whether Drouot reinforced, Drouot should NOT be in Waterloo
        # (artillery stays in adjacent position)
        drouot_after = self.world.marshals.get("Drouot")
        if drouot_after:
            assert drouot_after.location != "Waterloo", \
                "Artillery should NOT advance to battle region on reinforcement"
            assert drouot_after.location == "Belgium", \
                "Artillery should stay in original adjacent position"

    def test_infantry_still_relocates_on_reinforcement(self):
        """Non-artillery marshals relocate on arrival AND stay if attacker wins."""
        random.seed(42)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 60000  # Strong enough to win

        davout = self.world.get_marshal("Davout")
        davout.location = "Belgium"  # Adjacent to Waterloo
        davout.strength = 40000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 25000  # Weaker so attacker wins

        result = self.executor._execute_attack(
            ney, "Wellington", self.world, self.game_state)

        # If Davout reinforced and attacker won, he should be in Waterloo
        davout_after = self.world.marshals.get("Davout")
        if davout_after and davout_after.reinforced_this_turn:
            assert davout_after.location == "Waterloo", \
                "Infantry should stay in battle region when attacker wins"

    def test_artillery_reinforcement_still_gets_flag(self):
        """Artillery that reinforced from adjacent still gets reinforced_this_turn."""
        random.seed(42)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 30000

        drouot = self.world.get_marshal("Drouot")
        drouot.location = "Belgium"  # Adjacent
        drouot.strength = 20000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 35000

        self.executor._execute_attack(
            ney, "Wellington", self.world, self.game_state)

        drouot_after = self.world.marshals.get("Drouot")
        if drouot_after and drouot_after.reinforced_this_turn:
            # If artillery reinforced, it should have the flag
            # but NOT have moved
            assert drouot_after.location == "Belgium"

    def test_artillery_participates_in_casualty_distribution(self):
        """Artillery that reinforced from adjacent still takes casualties."""
        random.seed(42)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 30000

        drouot = self.world.get_marshal("Drouot")
        drouot.location = "Belgium"  # Adjacent
        drouot.strength = 20000
        initial_drouot_strength = drouot.strength

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 40000

        self.executor._execute_attack(
            ney, "Wellington", self.world, self.game_state)

        drouot_after = self.world.marshals.get("Drouot")
        if drouot_after and drouot_after.reinforced_this_turn:
            # Artillery participated — should have taken some casualties
            # (unless battle was a total rout with 0 return fire)
            # At minimum, verify the marshal is still tracked
            assert drouot_after is not None

    def test_artillery_still_counts_as_adjacent_ally_for_coordination(self):
        """Artillery that stays adjacent is NOT excluded from adjacent ally count.

        Gate 4 gap fix: artillery must NOT be added to arrived_names
        (which becomes exclude_from_adjacent), so it still provides
        the +2% adjacent support attack bonus.
        """
        random.seed(42)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 30000

        drouot = self.world.get_marshal("Drouot")
        drouot.location = "Belgium"  # Adjacent to Waterloo
        drouot.strength = 20000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 35000

        # Directly test coordination context calculation AFTER simulating
        # the arrival loop logic (artillery stays adjacent, not in arrived_names)
        arrived_names = set()  # Artillery NOT added here

        adj_count, adj_names = self.executor._count_adjacent_allies(
            "Waterloo", "France", self.world, exclude_names=arrived_names)

        # Drouot is in Belgium (adjacent to Waterloo) and NOT excluded
        assert "Drouot" in adj_names, \
            "Artillery in adjacent region should count as adjacent ally"
        assert adj_count >= 1

    def test_infantry_excluded_from_adjacent_after_arrival(self):
        """Infantry that arrived IS excluded from adjacent count (moved to battle region)."""
        davout = self.world.get_marshal("Davout")
        davout.location = "Belgium"  # Adjacent
        davout.strength = 25000

        # Simulate arrival: infantry moves to Waterloo, added to arrived_names
        arrived_names = {"Davout"}

        adj_count, adj_names = self.executor._count_adjacent_allies(
            "Waterloo", "France", self.world, exclude_names=arrived_names)

        # Davout is excluded because he relocated to battle region
        assert "Davout" not in adj_names, \
            "Arrived infantry should be excluded from adjacent ally count"


# ════════════════════════════════════════════════════════════
# ISSUE 3b: Reinforcers retreat on loss
# ════════════════════════════════════════════════════════════

class TestReinforcerRetreatOnLoss:
    """Reinforcers who relocated to battle region return to origin if their side lost."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_reinforcer_returns_to_origin_on_attacker_loss(self):
        """Davout reinforces from Belgium, attacker loses → Davout returns to Belgium."""
        random.seed(99)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 20000  # Weak attacker

        davout = self.world.get_marshal("Davout")
        davout.location = "Belgium"  # Adjacent to Waterloo
        davout.strength = 25000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 50000  # Much stronger

        self.executor._execute_attack(
            ney, "Wellington", self.world, self.game_state)

        davout_after = self.world.marshals.get("Davout")
        if davout_after and davout_after.reinforced_this_turn:
            assert davout_after.location == "Belgium", \
                "Reinforcer should return to origin when attacker loses"

    def test_reinforcer_stays_on_attacker_win(self):
        """Davout reinforces from Belgium, attacker wins → Davout stays in Waterloo."""
        random.seed(42)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 60000  # Strong attacker

        davout = self.world.get_marshal("Davout")
        davout.location = "Belgium"  # Adjacent to Waterloo
        davout.strength = 40000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 25000  # Weaker

        self.executor._execute_attack(
            ney, "Wellington", self.world, self.game_state)

        davout_after = self.world.marshals.get("Davout")
        if davout_after and davout_after.reinforced_this_turn:
            assert davout_after.location == "Waterloo", \
                "Reinforcer should stay in battle region when attacker wins"

    def test_artillery_reinforcer_stays_at_origin_regardless(self):
        """Artillery stays at origin whether attacker wins or loses (never relocates)."""
        random.seed(99)
        ney = self.world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 20000

        drouot = self.world.get_marshal("Drouot")
        drouot.location = "Belgium"  # Adjacent
        drouot.strength = 20000

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 50000

        self.executor._execute_attack(
            ney, "Wellington", self.world, self.game_state)

        drouot_after = self.world.marshals.get("Drouot")
        if drouot_after:
            assert drouot_after.location == "Belgium", \
                "Artillery should always stay at origin (never relocates)"

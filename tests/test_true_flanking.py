"""
Test True Flanking System (Phase 2.5)

Tests position-based flanking that requires attacks from DIFFERENT adjacent regions.
True flanking = coordination bonus for attacking from multiple directions.
Spam attacks from the same direction do NOT get flanking bonus.

Flanking Bonus Scale:
- 0: All attacks from same direction (no coordination)
- +1: 2 unique attack directions (classic flank)
- +2: 3 unique attack directions (triple pincer)
- +3: 4+ unique attack directions (complete encirclement)
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.game_logic.combat import CombatResolver


class TestFlankingBasics:
    """Test basic attack tracking and flanking calculation."""

    def test_no_attacks_no_flanking(self):
        """Verify no flanking bonus when no attacks recorded."""
        world = WorldState()

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 0
        assert result["num_origins"] == 0
        assert result["message"] is None

    def test_single_attack_no_flanking(self):
        """Verify single attack gets no flanking bonus."""
        world = WorldState()

        # Record one attack
        world.record_attack("Ney", "Belgium", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 0
        assert result["num_origins"] == 1
        assert "Belgium" in result["unique_origins"]
        assert result["message"] is None

    def test_record_attack_returns_attack_info(self):
        """Verify record_attack returns proper attack record."""
        world = WorldState()

        record = world.record_attack("Ney", "Belgium", "Waterloo")

        assert record["attacker"] == "Ney"
        assert record["origin"] == "Belgium"
        assert record["timestamp"] == 1

    def test_multiple_records_increment_timestamp(self):
        """Verify timestamps increment properly."""
        world = WorldState()

        r1 = world.record_attack("Ney", "Belgium", "Waterloo")
        r2 = world.record_attack("Davout", "Rhine", "Waterloo")
        r3 = world.record_attack("Grouchy", "Paris", "Waterloo")

        assert r1["timestamp"] == 1
        assert r2["timestamp"] == 2
        assert r3["timestamp"] == 3


class TestTwoAttackersSameOrigin:
    """Test: 2 attackers from same origin = NO flanking bonus."""

    def test_two_attacks_same_origin_no_bonus(self):
        """2 attackers from same region get NO flanking bonus."""
        world = WorldState()

        # Both attack from Belgium
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Belgium", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 0
        assert result["num_origins"] == 1  # Only 1 unique origin
        assert result["message"] is None

    def test_three_attacks_same_origin_no_bonus(self):
        """3 attackers from same region get NO flanking bonus."""
        world = WorldState()

        # All attack from Belgium - spam attacks don't help
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Belgium", "Waterloo")
        world.record_attack("Grouchy", "Belgium", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 0
        assert result["num_origins"] == 1
        assert result["message"] is None


class TestTwoAttackersDifferentOrigins:
    """Test: 2 attackers from different origins = +1 flanking bonus."""

    def test_two_attacks_different_origins_plus_one(self):
        """2 attackers from different regions get +1 flanking bonus."""
        world = WorldState()

        # Classic flanking: attack from two sides
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 1
        assert result["num_origins"] == 2
        assert "Belgium" in result["unique_origins"]
        assert "Rhine" in result["unique_origins"]
        assert result["message"] == "Flanking maneuver!"

    def test_two_origins_with_multiple_attackers_each(self):
        """Multiple attackers from 2 different origins still = +1."""
        world = WorldState()

        # 2 from Belgium, 2 from Rhine
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Marshal1", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")
        world.record_attack("Marshal2", "Rhine", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 1  # Still only 2 unique directions
        assert result["num_origins"] == 2


class TestThreeAttackersThreeOrigins:
    """Test: 3 attackers from 3 different origins = +2 flanking bonus."""

    def test_three_attacks_three_origins_plus_two(self):
        """3 attackers from 3 different regions get +2 flanking bonus."""
        world = WorldState()

        # Triple pincer
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")
        world.record_attack("Grouchy", "Paris", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 2
        assert result["num_origins"] == 3
        assert result["message"] == "Triple pincer attack!"


class TestThreeAttackersTwoOrigins:
    """Test: 3 attackers from 2 origins (one shared) = +1 flanking bonus."""

    def test_three_attacks_two_origins_plus_one(self):
        """3 attackers but only 2 unique origins = +1 flanking bonus."""
        world = WorldState()

        # Two from Belgium, one from Rhine
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Belgium", "Waterloo")
        world.record_attack("Grouchy", "Rhine", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 1  # Only 2 unique directions
        assert result["num_origins"] == 2


class TestFourPlusOrigins:
    """Test: 4+ unique origins = +3 flanking bonus (complete encirclement)."""

    def test_four_origins_plus_three(self):
        """4 attackers from 4 different regions get +3 flanking bonus."""
        world = WorldState()

        # Complete encirclement
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")
        world.record_attack("Grouchy", "Paris", "Waterloo")
        world.record_attack("Murat", "Lyon", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 3
        assert result["num_origins"] == 4
        assert result["message"] == "Complete encirclement!"

    def test_five_origins_still_plus_three(self):
        """5+ origins still capped at +3 flanking bonus."""
        world = WorldState()

        # More than 4 origins
        world.record_attack("M1", "Belgium", "Waterloo")
        world.record_attack("M2", "Rhine", "Waterloo")
        world.record_attack("M3", "Paris", "Waterloo")
        world.record_attack("M4", "Lyon", "Waterloo")
        world.record_attack("M5", "Brittany", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        assert result["bonus"] == 3  # Capped at +3
        assert result["num_origins"] == 5


class TestFlankingMessages:
    """Test flanking messages show correct information."""

    def test_flanking_message_two_origins(self):
        """Message shows both attacking directions for +1 flanking."""
        world = WorldState()

        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")

        # Get message for Davout (second attacker)
        message = world.get_flanking_message("Davout", "Rhine", "Waterloo")

        assert message is not None
        assert "Davout" in message
        assert "Rhine" in message
        assert "Belgium" in message  # First attacker's origin
        assert "+1" in message

    def test_flanking_message_triple_pincer(self):
        """Message shows encirclement for +2 flanking."""
        world = WorldState()

        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")
        world.record_attack("Grouchy", "Paris", "Waterloo")

        message = world.get_flanking_message("Grouchy", "Paris", "Waterloo")

        assert message is not None
        assert "Grouchy" in message
        assert "Paris" in message
        assert "+2" in message
        assert "encirclement" in message.lower()

    def test_flanking_message_complete_encirclement(self):
        """Message shows complete encirclement for +3 flanking."""
        world = WorldState()

        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")
        world.record_attack("Grouchy", "Paris", "Waterloo")
        world.record_attack("Murat", "Lyon", "Waterloo")

        message = world.get_flanking_message("Murat", "Lyon", "Waterloo")

        assert message is not None
        assert "Murat" in message
        assert "+3" in message

    def test_no_flanking_message_same_origin(self):
        """No message when all attacks from same direction."""
        world = WorldState()

        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Belgium", "Waterloo")

        message = world.get_flanking_message("Davout", "Belgium", "Waterloo")

        assert message is None


class TestTurnResetClearsTracking:
    """Test that attack tracking resets properly between turns."""

    def test_reset_clears_attacks(self):
        """reset_attack_tracking clears all recorded attacks."""
        world = WorldState()

        # Record some attacks
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")

        assert len(world.attacks_this_turn) > 0

        # Reset
        world.reset_attack_tracking()

        assert len(world.attacks_this_turn) == 0
        assert world._action_counter == 0

    def test_reset_clears_flanking_bonus(self):
        """After reset, flanking bonus returns to 0."""
        world = WorldState()

        # Build up flanking bonus
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")

        result_before = world.calculate_flanking_bonus("Waterloo")
        assert result_before["bonus"] == 1

        # Reset turn
        world.reset_attack_tracking()

        result_after = world.calculate_flanking_bonus("Waterloo")
        assert result_after["bonus"] == 0

    def test_end_turn_resets_attack_tracking(self):
        """End turn command resets attack tracking."""
        world = WorldState()

        # Record attacks
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")

        # End turn (force_end_turn is the actual method name)
        world.force_end_turn()

        # Tracking should be cleared
        assert len(world.attacks_this_turn) == 0
        result = world.calculate_flanking_bonus("Waterloo")
        assert result["bonus"] == 0

    def test_auto_advance_resets_attack_tracking(self):
        """Using all actions auto-advances and resets tracking."""
        world = WorldState()

        # Record attacks
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")

        # Use all actions
        world.actions_remaining = 1
        world.use_action("attack")  # Last action triggers auto-advance

        # Tracking should be cleared
        assert len(world.attacks_this_turn) == 0


class TestFlankingAppliedToCombat:
    """Test that flanking bonus is properly applied to combat dice rolls."""

    def test_combat_resolver_accepts_flanking_bonus(self):
        """CombatResolver.resolve_battle accepts flanking_bonus parameter."""
        attacker = Marshal("Ney", "Belgium", 50000, "aggressive",
                          skills={"tactical": 7, "shock": 9, "defense": 4,
                                 "logistics": 5, "administration": 4, "command": 8})
        defender = Marshal("Wellington", "Waterloo", 50000, "cautious",
                          skills={"tactical": 8, "shock": 6, "defense": 9,
                                 "logistics": 7, "administration": 7, "command": 8})

        combat = CombatResolver()

        # Should not raise any errors
        result = combat.resolve_battle(attacker, defender, flanking_bonus=2)

        assert "attacker" in result
        assert "defender" in result
        assert "flanking_bonus" in result
        assert result["flanking_bonus"] == 2

    def test_flanking_bonus_increases_modified_roll(self):
        """Flanking bonus should increase attacker's modified roll."""
        attacker = Marshal("Ney", "Belgium", 50000, "aggressive",
                          skills={"tactical": 7, "shock": 9, "defense": 4,
                                 "logistics": 5, "administration": 4, "command": 8})

        combat = CombatResolver()

        # Roll dice multiple times to verify bonus is applied
        # Since dice are random, we compare with and without bonus
        rolls_without = []
        rolls_with = []

        for _ in range(20):
            r_without = combat.roll_combat_dice(attacker, flanking_bonus=0)
            r_with = combat.roll_combat_dice(attacker, flanking_bonus=3)
            rolls_without.append(r_without["modified"])
            rolls_with.append(r_with["modified"])

        # Average with bonus should be higher (statistically)
        avg_without = sum(rolls_without) / len(rolls_without)
        avg_with = sum(rolls_with) / len(rolls_with)

        # With +3 bonus, average should be noticeably higher
        assert avg_with > avg_without

    def test_flanking_message_in_combat_result(self):
        """Combat result includes flanking_message when provided."""
        attacker = Marshal("Ney", "Belgium", 50000, "aggressive")
        defender = Marshal("Wellington", "Waterloo", 50000, "cautious")

        combat = CombatResolver()

        result = combat.resolve_battle(
            attacker, defender,
            flanking_bonus=2,
            flanking_message="Triple pincer attack!"
        )

        assert result["flanking_message"] == "Triple pincer attack!"


class TestFlankingDifferentTargets:
    """Test that flanking tracks targets separately."""

    def test_attacks_on_different_targets_tracked_separately(self):
        """Attacks on different regions don't affect each other's flanking."""
        world = WorldState()

        # Attack Waterloo from Belgium
        world.record_attack("Ney", "Belgium", "Waterloo")

        # Attack Vienna from Bavaria (different target)
        world.record_attack("Davout", "Bavaria", "Vienna")

        # Each target should have only 1 attack origin
        waterloo_result = world.calculate_flanking_bonus("Waterloo")
        vienna_result = world.calculate_flanking_bonus("Vienna")

        assert waterloo_result["bonus"] == 0  # Only 1 origin
        assert vienna_result["bonus"] == 0  # Only 1 origin

        assert waterloo_result["num_origins"] == 1
        assert vienna_result["num_origins"] == 1

    def test_flanking_bonus_specific_to_target(self):
        """Flanking bonus is calculated per-target."""
        world = WorldState()

        # Build flanking on Waterloo
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")

        # Vienna has no attacks
        waterloo_result = world.calculate_flanking_bonus("Waterloo")
        vienna_result = world.calculate_flanking_bonus("Vienna")

        assert waterloo_result["bonus"] == 1
        assert vienna_result["bonus"] == 0


class TestFlankingEdgeCases:
    """Test edge cases for flanking system."""

    def test_same_attacker_different_origins_counts_as_two(self):
        """
        If same marshal somehow attacks from different origins
        (edge case), both origins count.
        """
        world = WorldState()

        # Same attacker, but from different origins (unrealistic but tests logic)
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Ney", "Rhine", "Waterloo")

        result = world.calculate_flanking_bonus("Waterloo")

        # Both origins should count for flanking
        assert result["num_origins"] == 2
        assert result["bonus"] == 1

    def test_empty_region_name_handled(self):
        """Empty target region name doesn't crash."""
        world = WorldState()

        result = world.calculate_flanking_bonus("")

        assert result["bonus"] == 0

    def test_nonexistent_target_no_bonus(self):
        """Nonexistent target region returns no flanking bonus."""
        world = WorldState()

        result = world.calculate_flanking_bonus("NonexistentRegion")

        assert result["bonus"] == 0


class TestFlankingIntegrationWithWorldState:
    """Integration tests with full WorldState context."""

    def test_attacks_persist_within_turn(self):
        """Attack records persist throughout a turn."""
        world = WorldState()

        # Initial turn
        start_turn = world.current_turn

        world.record_attack("Ney", "Belgium", "Waterloo")

        # Do some other stuff (simulate other actions)
        world.actions_remaining = 3  # Plenty of actions left

        world.record_attack("Davout", "Rhine", "Waterloo")

        # Should still be same turn
        assert world.current_turn == start_turn

        # Flanking should be tracked
        result = world.calculate_flanking_bonus("Waterloo")
        assert result["bonus"] == 1

    def test_new_turn_fresh_tracking(self):
        """Each new turn starts with fresh attack tracking."""
        world = WorldState()

        # Turn 1 attacks
        world.record_attack("Ney", "Belgium", "Waterloo")
        world.record_attack("Davout", "Rhine", "Waterloo")

        result_turn1 = world.calculate_flanking_bonus("Waterloo")
        assert result_turn1["bonus"] == 1

        # End turn 1 (force_end_turn is the actual method name)
        world.force_end_turn()

        # Turn 2 - fresh start
        result_turn2 = world.calculate_flanking_bonus("Waterloo")
        assert result_turn2["bonus"] == 0

        # New attacks in turn 2
        world.record_attack("Grouchy", "Paris", "Waterloo")

        result_turn2_after = world.calculate_flanking_bonus("Waterloo")
        assert result_turn2_after["num_origins"] == 1


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v"])

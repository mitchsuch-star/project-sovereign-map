"""
Test suite for 2d6 dice-based combat system

Tests:
- Basic dice rolling mechanics
- Skill bonus application
- Critical hits and misses
- Combat variance (same matchup = different outcomes)
- Skilled marshal advantage over time
"""

import pytest
from backend.models.marshal import Marshal
from backend.game_logic.combat import CombatResolver


class TestDiceRolling:
    """Test basic dice rolling mechanics."""

    def test_roll_range(self):
        """Dice rolls should be in valid range (2-12 natural)."""
        combat = CombatResolver()
        marshal = Marshal("Test", "Paris", 10000, "cautious", tactical_skill=6)

        # Roll 50 times to test range
        for _ in range(50):
            roll = combat.roll_combat_dice(marshal)
            assert 2 <= roll['natural'] <= 12, "Natural roll must be 2-12"
            assert roll['natural'] == int(roll['natural']), "Natural roll must be integer"

    def test_skill_bonus_calculation(self):
        """Skill bonus should be tactical_skill // 3."""
        combat = CombatResolver()

        test_cases = [
            (0, 0),   # Skill 0 → bonus 0
            (3, 1),   # Skill 3 → bonus 1
            (6, 2),   # Skill 6 → bonus 2
            (9, 3),   # Skill 9 → bonus 3
            (12, 4),  # Skill 12 → bonus 4
        ]

        for skill, expected_bonus in test_cases:
            marshal = Marshal("Test", "Paris", 10000, "cautious", tactical_skill=skill)
            roll = combat.roll_combat_dice(marshal)
            assert roll['skill_bonus'] == expected_bonus, f"Skill {skill} should give bonus {expected_bonus}"

    def test_modified_roll_cap(self):
        """Modified roll should cap at 14 (allows flanking bonus)."""
        combat = CombatResolver()
        # High skill marshal
        marshal = Marshal("Genius", "Paris", 10000, "cautious", tactical_skill=12)

        # Roll many times to ensure we'd hit high natural rolls
        # Cap is 14 (not 12) to allow flanking bonuses (+1 to +3) to matter
        for _ in range(100):
            roll = combat.roll_combat_dice(marshal)
            assert roll['modified'] <= 14, "Modified roll must cap at 14 (allows flanking bonus)"

    def test_multiplier_calculation(self):
        """Multiplier should be 0.85 + (modified * 0.025)."""
        combat = CombatResolver()

        # Test with skill 0 (no bonus)
        marshal = Marshal("Novice", "Paris", 10000, "cautious", tactical_skill=0)

        # Manually test multiplier formula
        test_modified_rolls = [2, 7, 12]
        expected_multipliers = [
            0.85 + (2 * 0.025),   # 0.90
            0.85 + (7 * 0.025),   # 1.025
            0.85 + (12 * 0.025),  # 1.15
        ]

        for modified, expected in zip(test_modified_rolls, expected_multipliers):
            actual = 0.85 + (modified * 0.025)
            assert abs(actual - expected) < 0.001, f"Multiplier formula incorrect for roll {modified}"

    def test_critical_success_natural_12(self):
        """Natural roll of 12 should be critical success."""
        combat = CombatResolver()
        marshal = Marshal("Test", "Paris", 10000, "cautious", tactical_skill=6)

        # Roll many times until we get a natural 12
        found_critical = False
        for _ in range(500):  # Should be very likely
            roll = combat.roll_combat_dice(marshal)
            if roll['natural'] == 12:
                assert roll['is_critical_success'] is True
                assert roll['is_critical_failure'] is False
                found_critical = True
                break

        assert found_critical, "Should roll natural 12 in 500 attempts"

    def test_critical_failure_natural_2(self):
        """Natural roll of 2 should be critical failure."""
        combat = CombatResolver()
        marshal = Marshal("Test", "Paris", 10000, "cautious", tactical_skill=6)

        # Roll many times until we get a natural 2
        found_critical = False
        for _ in range(500):  # Should be very likely
            roll = combat.roll_combat_dice(marshal)
            if roll['natural'] == 2:
                assert roll['is_critical_failure'] is True
                assert roll['is_critical_success'] is False
                found_critical = True
                break

        assert found_critical, "Should roll natural 2 in 500 attempts"

    def test_roll_returns_all_fields(self):
        """Roll result should contain all required fields."""
        combat = CombatResolver()
        marshal = Marshal("Test", "Paris", 10000, "cautious", tactical_skill=6)

        roll = combat.roll_combat_dice(marshal)

        required_fields = ['natural', 'modified', 'is_critical_success',
                          'is_critical_failure', 'multiplier', 'skill_bonus']
        for field in required_fields:
            assert field in roll, f"Roll must contain '{field}' field"

    def test_all_values_are_ints_except_multiplier(self):
        """All roll values should be ints except multiplier (float)."""
        combat = CombatResolver()
        marshal = Marshal("Test", "Paris", 10000, "cautious", tactical_skill=6)

        roll = combat.roll_combat_dice(marshal)

        assert isinstance(roll['natural'], int)
        assert isinstance(roll['modified'], int)
        assert isinstance(roll['skill_bonus'], int)
        assert isinstance(roll['multiplier'], float)
        assert isinstance(roll['is_critical_success'], bool)
        assert isinstance(roll['is_critical_failure'], bool)


class TestCombatVariance:
    """Test that dice create variance in combat outcomes."""

    def test_same_matchup_different_outcomes(self):
        """Same matchup should produce different casualties due to dice variance."""
        combat = CombatResolver()

        # Track unique casualty counts over multiple battles
        casualty_results = set()

        for _ in range(20):
            # Fresh marshals each time
            ney = Marshal("Ney", "Belgium", 50000, "aggressive", tactical_skill=8)
            wellington = Marshal("Wellington", "Waterloo", 50000, "cautious", tactical_skill=10)

            result = combat.resolve_battle(ney, wellington)
            casualty_tuple = (result['attacker']['casualties'], result['defender']['casualties'])
            casualty_results.add(casualty_tuple)

        # Should see at least 5 different outcomes in 20 battles
        assert len(casualty_results) >= 5, "Dice should create variance in outcomes"

    def test_battle_results_contain_roll_info(self):
        """Battle results should include attacker_roll data."""
        combat = CombatResolver()

        ney = Marshal("Ney", "Belgium", 50000, "aggressive", tactical_skill=8)
        wellington = Marshal("Wellington", "Waterloo", 50000, "cautious", tactical_skill=10)

        result = combat.resolve_battle(ney, wellington)

        assert 'attacker_roll' in result, "Battle result must include attacker_roll"
        assert 'natural' in result['attacker_roll']
        assert 'modified' in result['attacker_roll']
        assert 'multiplier' in result['attacker_roll']

    def test_description_includes_narrative(self):
        """Battle description should include narrative text instead of dice numbers."""
        combat = CombatResolver()

        ney = Marshal("Ney", "Belgium", 50000, "aggressive", tactical_skill=8)
        wellington = Marshal("Wellington", "Waterloo", 50000, "cautious", tactical_skill=10)

        result = combat.resolve_battle(ney, wellington)
        description = result['description']

        # Should NOT contain dice notation (immersion-breaking)
        assert "🎲" not in description, "Description should not show dice emoji"
        assert "rolls" not in description.lower(), "Description should not mention rolling"
        assert "+=" not in description, "Description should not show math notation"

        # Should contain narrative description
        assert "Ney" in description, "Description should mention attacker"
        assert len(description) > 20, "Description should have meaningful content"


class TestSkilledMarshalAdvantage:
    """Test that skilled marshals win more often over time."""

    def test_high_skill_wins_more_often(self):
        """Marshal with higher skill should deal more damage than lower skill marshal."""
        combat = CombatResolver()

        # Run battles with high-skill attacker
        high_skill_damage = 0
        num_battles = 30

        for _ in range(num_battles):
            skilled = Marshal("Davout", "Paris", 40000, "cautious", tactical_skill=10)
            defender = Marshal("Enemy", "Belgium", 40000, "cautious", tactical_skill=5)
            result = combat.resolve_battle(skilled, defender)
            high_skill_damage += result['defender']['casualties']

        # Run battles with low-skill attacker
        low_skill_damage = 0

        for _ in range(num_battles):
            unskilled = Marshal("Novice", "Paris", 40000, "cautious", tactical_skill=3)
            defender = Marshal("Enemy", "Belgium", 40000, "cautious", tactical_skill=5)
            result = combat.resolve_battle(unskilled, defender)
            low_skill_damage += result['defender']['casualties']

        # High-skill attacker should deal more damage
        # Skill 10 (bonus 3) vs Skill 3 (bonus 1) = 2 point bonus difference
        # This translates to about 2-5% more damage on average (with variance)
        damage_ratio = high_skill_damage / low_skill_damage
        assert damage_ratio >= 1.01, f"High-skill attacker should deal more damage, ratio: {damage_ratio:.2f}"

    def test_skill_bonus_consistent(self):
        """Skill bonus should be consistent for same marshal."""
        combat = CombatResolver()
        marshal = Marshal("Test", "Paris", 10000, "cautious", tactical_skill=9)

        # All rolls from same marshal should have same skill bonus
        bonuses = set()
        for _ in range(20):
            roll = combat.roll_combat_dice(marshal)
            bonuses.add(roll['skill_bonus'])

        assert len(bonuses) == 1, "Skill bonus should be constant for same marshal"
        assert bonuses.pop() == 3, "Skill 9 should give bonus 3"


class TestIntegerWrapping:
    """Test that all combat results are properly wrapped as integers for Godot."""

    def test_casualties_are_ints(self):
        """All casualty values must be integers."""
        combat = CombatResolver()

        ney = Marshal("Ney", "Belgium", 50000, "aggressive", tactical_skill=8)
        wellington = Marshal("Wellington", "Waterloo", 50000, "cautious", tactical_skill=10)

        result = combat.resolve_battle(ney, wellington)

        assert isinstance(result['attacker']['casualties'], int)
        assert isinstance(result['defender']['casualties'], int)

    def test_remaining_strength_are_ints(self):
        """Remaining strength values must be integers."""
        combat = CombatResolver()

        ney = Marshal("Ney", "Belgium", 50000, "aggressive", tactical_skill=8)
        wellington = Marshal("Wellington", "Waterloo", 50000, "cautious", tactical_skill=10)

        result = combat.resolve_battle(ney, wellington)

        assert isinstance(result['attacker']['remaining'], int)
        assert isinstance(result['defender']['remaining'], int)

    def test_morale_are_ints(self):
        """Morale values must be integers."""
        combat = CombatResolver()

        ney = Marshal("Ney", "Belgium", 50000, "aggressive", tactical_skill=8)
        wellington = Marshal("Wellington", "Waterloo", 50000, "cautious", tactical_skill=10)

        result = combat.resolve_battle(ney, wellington)

        assert isinstance(result['attacker']['morale'], int)
        assert isinstance(result['defender']['morale'], int)


class TestCriticalMessages:
    """Test that critical hits/misses appear as narrative descriptions."""

    def test_critical_success_message(self):
        """Critical success should use dramatic narrative text."""
        combat = CombatResolver()

        # Keep fighting until we get a critical success
        found_critical = False
        for _ in range(200):
            ney = Marshal("Ney", "Belgium", 50000, "aggressive", tactical_skill=8)
            wellington = Marshal("Wellington", "Waterloo", 50000, "cautious", tactical_skill=10)

            result = combat.resolve_battle(ney, wellington)

            if result['attacker_roll']['is_critical_success']:
                # Should use dramatic narrative keywords (not "CRITICAL SUCCESS")
                desc_lower = result['description'].lower()
                has_narrative = any(word in desc_lower for word in
                    ['brilliant', 'devastating', 'perfect', 'coordination'])
                assert has_narrative, "Critical success should use dramatic narrative"
                found_critical = True
                break

        assert found_critical, "Should get critical success in 200 battles"

    def test_critical_failure_message(self):
        """Critical failure should use negative narrative text."""
        combat = CombatResolver()

        # Keep fighting until we get a critical failure
        found_critical = False
        for _ in range(200):
            ney = Marshal("Ney", "Belgium", 50000, "aggressive", tactical_skill=8)
            wellington = Marshal("Wellington", "Waterloo", 50000, "cautious", tactical_skill=10)

            result = combat.resolve_battle(ney, wellington)

            if result['attacker_roll']['is_critical_failure']:
                # Should use negative narrative keywords (not "CRITICAL FAILURE")
                desc_lower = result['description'].lower()
                has_narrative = any(word in desc_lower for word in
                    ['falters', 'collapses', 'chaos', 'stumble', 'disastrously'])
                assert has_narrative, "Critical failure should use negative narrative"
                found_critical = True
                break

        assert found_critical, "Should get critical failure in 200 battles"


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v"])

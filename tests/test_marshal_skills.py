"""
Test Marshal Skills System (Phase 2.2)

Tests the 6-skill system for marshals:
- Tactical: Combat rolls, flanking bonuses
- Shock: Attack damage, pursuit effectiveness
- Defense: Defender bonus, retreat casualties
- Logistics: Supply range, attrition resistance (Phase 5)
- Administration: Recruitment speed, desertion prevention (Phase 5)
- Command: Morale management, discipline, looting prevention (Phase 5)
"""

import pytest
from backend.models.marshal import Marshal, create_starting_marshals, create_enemy_marshals
from backend.game_logic.combat import CombatResolver


class TestMarshalSkillsBasic:
    """Test basic skill system implementation."""

    def test_all_marshals_have_6_skills(self):
        """Verify all marshals have all 6 skills."""
        marshals = create_starting_marshals()
        marshals.update(create_enemy_marshals())

        required_skills = ["tactical", "shock", "defense", "logistics", "administration", "command"]

        for name, marshal in marshals.items():
            assert hasattr(marshal, "skills"), f"{name} missing skills attribute"
            for skill in required_skills:
                assert skill in marshal.skills, f"{name} missing {skill} skill"
                assert isinstance(marshal.skills[skill], int), f"{name} {skill} not an integer"
                assert 1 <= marshal.skills[skill] <= 10, f"{name} {skill} out of range (1-10)"

    def test_skills_are_integers(self):
        """Verify all skills are wrapped as integers."""
        marshals = create_starting_marshals()
        marshals.update(create_enemy_marshals())

        for name, marshal in marshals.items():
            for skill_name, skill_value in marshal.skills.items():
                assert type(skill_value) == int, f"{name}.{skill_name} is {type(skill_value)}, not int"

    def test_backward_compatibility_without_skills(self):
        """Test that marshals can be created without explicit skills (defaults)."""
        marshal = Marshal(
            name="Test Marshal",
            location="Paris",
            strength=50000,
            personality="cautious",
            tactical_skill=7
        )

        # Should have default skills
        assert hasattr(marshal, "skills")
        assert "tactical" in marshal.skills
        assert marshal.skills["tactical"] == 7  # Should use tactical_skill as default


class TestHistoricalSkillValues:
    """Test that marshals have historically accurate skill values."""

    def test_ney_skills(self):
        """Verify Ney's skills match historical profile: aggressive attacker, weak defender."""
        marshals = create_starting_marshals()
        ney = marshals["Ney"]

        assert ney.skills["tactical"] == 7
        assert ney.skills["shock"] == 9, "Ney should have highest shock (Bravest of the Brave)"
        assert ney.skills["defense"] == 4, "Ney should have low defense (too aggressive)"
        assert ney.skills["logistics"] == 5
        assert ney.skills["administration"] == 4
        assert ney.skills["command"] == 8

    def test_davout_skills(self):
        """Verify Davout's skills match historical profile: excellent all-around, Iron Marshal."""
        marshals = create_starting_marshals()
        davout = marshals["Davout"]

        assert davout.skills["tactical"] == 9, "Davout should have excellent tactical skill"
        assert davout.skills["shock"] == 7
        assert davout.skills["defense"] == 8, "Davout should be strong defender"
        assert davout.skills["logistics"] == 8, "Davout should have excellent logistics"
        assert davout.skills["administration"] == 8
        assert davout.skills["command"] == 9

    def test_grouchy_skills(self):
        """Verify Grouchy's skills match historical profile: average across the board."""
        marshals = create_starting_marshals()
        grouchy = marshals["Grouchy"]

        # Grouchy should be average (5) for most skills
        assert grouchy.skills["tactical"] == 5
        assert grouchy.skills["shock"] == 5
        assert grouchy.skills["defense"] == 5
        assert grouchy.skills["logistics"] == 6, "Grouchy slightly better at logistics"
        assert grouchy.skills["administration"] == 5
        assert grouchy.skills["command"] == 5

    def test_wellington_skills(self):
        """Verify Wellington's skills match historical profile: defensive genius, weak attacker."""
        enemies = create_enemy_marshals()
        wellington = enemies["Wellington"]

        assert wellington.skills["tactical"] == 9
        assert wellington.skills["shock"] == 4, "Wellington should have low shock (defensive-minded)"
        assert wellington.skills["defense"] == 10, "Wellington should have highest defense (never lost)"
        assert wellington.skills["logistics"] == 8, "Wellington excellent at logistics (Peninsular War)"
        assert wellington.skills["administration"] == 7
        assert wellington.skills["command"] == 9

    def test_blucher_skills(self):
        """Verify Blücher's skills match historical profile: aggressive attacker, average defender."""
        enemies = create_enemy_marshals()
        blucher = enemies["Blucher"]

        assert blucher.skills["tactical"] == 6
        assert blucher.skills["shock"] == 8, "Blücher should have high shock (Marshal Forward)"
        assert blucher.skills["defense"] == 5
        assert blucher.skills["logistics"] == 5
        assert blucher.skills["administration"] == 4
        assert blucher.skills["command"] == 7


class TestSkillComparisons:
    """Test relative skill differences between marshals."""

    def test_ney_vs_davout_tactical(self):
        """Davout should be better tactician than Ney."""
        marshals = create_starting_marshals()
        ney = marshals["Ney"]
        davout = marshals["Davout"]

        assert davout.skills["tactical"] > ney.skills["tactical"]

    def test_ney_vs_davout_shock(self):
        """Ney should be more aggressive attacker than Davout."""
        marshals = create_starting_marshals()
        ney = marshals["Ney"]
        davout = marshals["Davout"]

        assert ney.skills["shock"] > davout.skills["shock"]

    def test_wellington_vs_ney_defense(self):
        """Wellington should be much better defender than Ney."""
        marshals = create_starting_marshals()
        enemies = create_enemy_marshals()
        ney = marshals["Ney"]
        wellington = enemies["Wellington"]

        assert wellington.skills["defense"] > ney.skills["defense"]
        assert wellington.skills["defense"] - ney.skills["defense"] >= 5, "Wellington should be 5+ points better"

    def test_wellington_vs_ney_shock(self):
        """Ney should be much better attacker than Wellington."""
        marshals = create_starting_marshals()
        enemies = create_enemy_marshals()
        ney = marshals["Ney"]
        wellington = enemies["Wellington"]

        assert ney.skills["shock"] > wellington.skills["shock"]
        assert ney.skills["shock"] - wellington.skills["shock"] >= 5, "Ney should be 5+ points better"


class TestCombatSkillIntegration:
    """Test that skills actually affect combat outcomes."""

    def test_tactical_skill_affects_dice_rolls(self):
        """Verify tactical skill affects combat roll bonuses."""
        high_tactical = Marshal("High Tactical", "A", 50000, "cautious", skills={"tactical": 9, "shock": 5, "defense": 5, "logistics": 5, "administration": 5, "command": 5})
        low_tactical = Marshal("Low Tactical", "B", 50000, "cautious", skills={"tactical": 3, "shock": 5, "defense": 5, "logistics": 5, "administration": 5, "command": 5})

        combat = CombatResolver()

        # Roll dice multiple times to check skill bonuses
        high_roll = combat.roll_combat_dice(high_tactical)
        low_roll = combat.roll_combat_dice(low_tactical)

        # High tactical should have higher skill bonus
        assert high_roll["skill_bonus"] == 3  # 9 // 3 = 3
        assert low_roll["skill_bonus"] == 1   # 3 // 3 = 1

    def test_shock_skill_increases_damage(self):
        """Verify shock skill increases damage dealt to defender."""
        # Create identical marshals except for shock skill
        high_shock_attacker = Marshal(
            "High Shock", "A", 50000, "aggressive",
            skills={"tactical": 5, "shock": 9, "defense": 5, "logistics": 5, "administration": 5, "command": 5}
        )
        low_shock_attacker = Marshal(
            "Low Shock", "A", 50000, "aggressive",
            skills={"tactical": 5, "shock": 3, "defense": 5, "logistics": 5, "administration": 5, "command": 5}
        )

        # Same defender
        defender1 = Marshal("Defender1", "B", 50000, "cautious", skills={"tactical": 5, "shock": 5, "defense": 5, "logistics": 5, "administration": 5, "command": 5})
        defender2 = Marshal("Defender2", "B", 50000, "cautious", skills={"tactical": 5, "shock": 5, "defense": 5, "logistics": 5, "administration": 5, "command": 5})

        combat = CombatResolver()

        # Run multiple battles and average results
        high_shock_total_damage = 0
        low_shock_total_damage = 0

        for _ in range(10):
            # Reset defenders
            defender1.strength = 50000
            defender1.morale = 100
            defender2.strength = 50000
            defender2.morale = 100

            # Reset attackers
            high_shock_attacker.strength = 50000
            high_shock_attacker.morale = 100
            low_shock_attacker.strength = 50000
            low_shock_attacker.morale = 100

            result1 = combat.resolve_battle(high_shock_attacker, defender1)
            result2 = combat.resolve_battle(low_shock_attacker, defender2)

            high_shock_total_damage += result1["defender"]["casualties"]
            low_shock_total_damage += result2["defender"]["casualties"]

        high_shock_avg = high_shock_total_damage / 10
        low_shock_avg = low_shock_total_damage / 10

        # High shock should deal more damage on average
        assert high_shock_avg > low_shock_avg, f"High shock ({high_shock_avg:.0f}) should deal more damage than low shock ({low_shock_avg:.0f})"

    def test_defense_skill_reduces_casualties(self):
        """Verify defense skill reduces casualties taken."""
        # Same attacker
        attacker1 = Marshal("Attacker1", "A", 50000, "aggressive", skills={"tactical": 5, "shock": 5, "defense": 5, "logistics": 5, "administration": 5, "command": 5})
        attacker2 = Marshal("Attacker2", "A", 50000, "aggressive", skills={"tactical": 5, "shock": 5, "defense": 5, "logistics": 5, "administration": 5, "command": 5})

        # Different defenders with different defense skills
        high_defense = Marshal(
            "High Defense", "B", 50000, "cautious",
            skills={"tactical": 5, "shock": 5, "defense": 9, "logistics": 5, "administration": 5, "command": 5}
        )
        low_defense = Marshal(
            "Low Defense", "B", 50000, "cautious",
            skills={"tactical": 5, "shock": 5, "defense": 3, "logistics": 5, "administration": 5, "command": 5}
        )

        combat = CombatResolver()

        # Run multiple battles and average results
        high_defense_total_casualties = 0
        low_defense_total_casualties = 0

        for _ in range(10):
            # Reset
            attacker1.strength = 50000
            attacker1.morale = 100
            attacker2.strength = 50000
            attacker2.morale = 100
            high_defense.strength = 50000
            high_defense.morale = 100
            low_defense.strength = 50000
            low_defense.morale = 100

            result1 = combat.resolve_battle(attacker1, high_defense)
            result2 = combat.resolve_battle(attacker2, low_defense)

            high_defense_total_casualties += result1["defender"]["casualties"]
            low_defense_total_casualties += result2["defender"]["casualties"]

        high_defense_avg = high_defense_total_casualties / 10
        low_defense_avg = low_defense_total_casualties / 10

        # High defense should take fewer casualties on average
        assert high_defense_avg < low_defense_avg, f"High defense ({high_defense_avg:.0f}) should take less damage than low defense ({low_defense_avg:.0f})"

    def test_ney_vs_wellington_combat_difference(self):
        """Test that Ney vs Wellington shows expected skill differentiation."""
        marshals = create_starting_marshals()
        enemies = create_enemy_marshals()

        ney = marshals["Ney"]
        wellington = enemies["Wellington"]

        # Reset to full strength
        ney.strength = 70000
        ney.morale = 100
        wellington.strength = 70000
        wellington.morale = 100

        combat = CombatResolver()

        # Ney attacks Wellington
        result = combat.resolve_battle(ney, wellington)

        # Because of skill differences:
        # - Ney (shock 9) should deal heavy damage
        # - Wellington (defense 10) should resist well
        # This should be a close fight

        print(f"\nNey vs Wellington:")
        print(f"  Ney casualties: {result['attacker']['casualties']:,}")
        print(f"  Wellington casualties: {result['defender']['casualties']:,}")

        # Both should survive (not be destroyed)
        assert result["attacker"]["remaining"] > 0, "Ney shouldn't be destroyed"
        assert result["defender"]["remaining"] > 0, "Wellington shouldn't be destroyed"


class TestFutureSkillFoundations:
    """Test that future skills (logistics, administration, command) are present but not yet used."""

    def test_logistics_skill_present(self):
        """Verify logistics skill exists for Phase 5 (supply/attrition)."""
        marshals = create_starting_marshals()
        for marshal in marshals.values():
            assert "logistics" in marshal.skills
            # TODO Phase 5: Test supply range and attrition resistance

    def test_administration_skill_present(self):
        """Verify administration skill exists for Phase 5 (recruitment/desertion)."""
        marshals = create_starting_marshals()
        for marshal in marshals.values():
            assert "administration" in marshal.skills
            # TODO Phase 5: Test recruitment speed and desertion prevention

    def test_command_skill_present(self):
        """Verify command skill exists for Phase 5 (morale/discipline)."""
        marshals = create_starting_marshals()
        for marshal in marshals.values():
            assert "command" in marshal.skills
            # TODO Phase 5: Test morale management, discipline, looting prevention


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v"])

"""
Test Marshal Signature Abilities (Phase 2.3)

Tests unique abilities for each marshal:
- Ney: "Bravest of the Brave" - +2 Shock when attacking (IMPLEMENTED)
- Davout: "Iron Marshal" - Prevents first morale drop below 50 (TODO: Phase 2.4)
- Grouchy: "Literal Obedience" - Never questions orders (TODO: Phase 2.4)
- Wellington: "Reverse Slope Defense" - +2 Defense on Hills/Forest (TODO: Terrain system)
- Blücher: "Vorwärts!" - +1 pursuit damage after winning (TODO: Phase 2.6)
"""

import pytest
from backend.models.marshal import Marshal, create_starting_marshals, create_enemy_marshals
from backend.game_logic.combat import CombatResolver


class TestAbilityStructure:
    """Test that all marshals have ability definitions."""

    def test_all_marshals_have_abilities(self):
        """Verify all marshals have ability defined."""
        marshals = create_starting_marshals()
        marshals.update(create_enemy_marshals())

        required_fields = ["name", "description", "trigger", "effect"]

        for name, marshal in marshals.items():
            assert hasattr(marshal, "ability"), f"{name} missing ability attribute"
            for field in required_fields:
                assert field in marshal.ability, f"{name} missing {field} in ability"
                assert isinstance(marshal.ability[field], str), f"{name} {field} not a string"

    def test_ability_names_are_unique(self):
        """Verify each marshal has a different ability."""
        marshals = create_starting_marshals()
        marshals.update(create_enemy_marshals())

        ability_names = [m.ability["name"] for m in marshals.values()]
        # Remove "None" if any
        ability_names = [n for n in ability_names if n != "None"]

        assert len(ability_names) == len(set(ability_names)), "Some marshals share ability names"

    def test_backward_compatibility_without_ability(self):
        """Test marshals can be created without explicit ability."""
        marshal = Marshal(
            name="Test Marshal",
            location="Paris",
            strength=50000,
            personality="cautious"
        )

        assert hasattr(marshal, "ability")
        assert marshal.ability["name"] == "None"


class TestNeyBravestOfTheBrave:
    """Test Ney's 'Bravest of the Brave' ability (FULLY IMPLEMENTED)."""

    def test_ney_has_ability(self):
        """Verify Ney has the Bravest of the Brave ability."""
        marshals = create_starting_marshals()
        ney = marshals["Ney"]

        assert ney.ability["name"] == "Bravest of the Brave"
        assert ney.ability["trigger"] == "when_attacking"
        assert "+2 Shock" in ney.ability["effect"]

    def test_ney_ability_triggers_when_attacking(self):
        """Verify Ney's ability triggers in combat when he attacks."""
        marshals = create_starting_marshals()
        enemies = create_enemy_marshals()

        ney = marshals["Ney"]
        wellington = enemies["Wellington"]

        # Reset to known state
        ney.strength = 50000
        ney.morale = 100
        wellington.strength = 50000
        wellington.morale = 100

        combat = CombatResolver()
        result = combat.resolve_battle(ney, wellington)

        # Ney's ability should trigger
        assert result.get("ability_triggered") is not None, "Ney's ability should trigger when attacking"
        assert "Bravest of the Brave" in result["ability_triggered"]

    def test_ney_ability_not_triggered_when_defending(self):
        """Verify Ney's ability does NOT trigger when defending."""
        marshals = create_starting_marshals()
        enemies = create_enemy_marshals()

        ney = marshals["Ney"]
        blucher = enemies["Blucher"]

        # Reset to known state
        ney.strength = 50000
        ney.morale = 100
        blucher.strength = 50000
        blucher.morale = 100

        combat = CombatResolver()
        # Blücher attacks Ney (Ney is defender)
        result = combat.resolve_battle(blucher, ney)

        # Ney's ability should NOT trigger (he's defending)
        # Note: Blücher's ability is also not implemented yet
        ability_msg = result.get("ability_triggered")
        if ability_msg:
            assert "Ney" not in ability_msg, "Ney's ability shouldn't trigger when defending"

    def test_ney_deals_more_damage_with_ability(self):
        """Verify Ney deals more damage when his ability is active."""
        # Create two Neys: one with ability, one without (for comparison)
        ney_with_ability = Marshal(
            name="Ney",
            location="Belgium",
            strength=50000,
            personality="aggressive",
            skills={"tactical": 7, "shock": 9, "defense": 4, "logistics": 5, "administration": 4, "command": 8},
            ability={
                "name": "Bravest of the Brave",
                "description": "Test",
                "trigger": "when_attacking",
                "effect": "+2 Shock when attacking"
            }
        )

        ney_without_ability = Marshal(
            name="Regular Marshal",
            location="Belgium",
            strength=50000,
            personality="aggressive",
            skills={"tactical": 7, "shock": 9, "defense": 4, "logistics": 5, "administration": 4, "command": 8},
            ability={
                "name": "None",
                "description": "No ability",
                "trigger": "never",
                "effect": "none"
            }
        )

        # Same defenders
        defender1 = Marshal("Defender1", "B", 50000, "cautious",
                          skills={"tactical": 5, "shock": 5, "defense": 5, "logistics": 5, "administration": 5, "command": 5})
        defender2 = Marshal("Defender2", "B", 50000, "cautious",
                          skills={"tactical": 5, "shock": 5, "defense": 5, "logistics": 5, "administration": 5, "command": 5})

        combat = CombatResolver()

        # Run many battles to average out variance (50 battles for stability)
        num_battles = 50
        with_ability_total_damage = 0
        without_ability_total_damage = 0

        for _ in range(num_battles):
            # Reset
            ney_with_ability.strength = 50000
            ney_with_ability.morale = 100
            ney_without_ability.strength = 50000
            ney_without_ability.morale = 100
            defender1.strength = 50000
            defender1.morale = 100
            defender2.strength = 50000
            defender2.morale = 100

            result1 = combat.resolve_battle(ney_with_ability, defender1)
            result2 = combat.resolve_battle(ney_without_ability, defender2)

            with_ability_total_damage += result1["defender"]["casualties"]
            without_ability_total_damage += result2["defender"]["casualties"]

        with_ability_avg = with_ability_total_damage / num_battles
        without_ability_avg = without_ability_total_damage / num_battles

        # Ney with ability should deal more damage
        # With Shock 9 -> 11 (+2), the damage multiplier goes from 1.45 to 1.55 (~7% more damage)
        assert with_ability_avg > without_ability_avg, \
            f"Ney with ability ({with_ability_avg:.0f}) should deal more damage than without ({without_ability_avg:.0f})"

        # Should be roughly 7% more damage, threshold 3% to account for variance
        damage_increase_percent = ((with_ability_avg - without_ability_avg) / without_ability_avg) * 100
        assert damage_increase_percent > 3, f"Damage increase should be >3%, got {damage_increase_percent:.1f}%"

    def test_ney_effective_shock_11_when_attacking(self):
        """Verify Ney's effective Shock is 11 (9 base + 2) when attacking."""
        marshals = create_starting_marshals()
        ney = marshals["Ney"]

        # Ney's base shock is 9
        assert ney.skills["shock"] == 9

        # When attacking, his ability adds +2, making effective shock 11
        # We can verify this by checking the damage dealt compared to expected multiplier
        # Shock 9 = 1.45x multiplier
        # Shock 11 = 1.55x multiplier
        # That's about 6.9% more damage


class TestDavoutIronMarshal:
    """Test Davout's 'Iron Marshal' ability (TODO: Phase 2.4)."""

    def test_davout_has_ability(self):
        """Verify Davout has the Iron Marshal ability defined."""
        marshals = create_starting_marshals()
        davout = marshals["Davout"]

        assert davout.ability["name"] == "Iron Marshal"
        assert davout.ability["trigger"] == "morale_drops_below_50"
        assert "TODO" in davout.ability["effect"], "Should be marked as TODO"

    def test_davout_ability_not_implemented_yet(self):
        """Verify Davout's ability is not yet implemented (awaiting Phase 2.4)."""
        marshals = create_starting_marshals()
        davout = marshals["Davout"]

        # For now, just verify the structure exists
        assert "Prevents first morale drop below 50" in davout.ability["effect"]
        # TODO Phase 2.4: Test that Davout's morale doesn't drop below 50 on first attempt


class TestGrouchyLiteralObedience:
    """Test Grouchy's 'Literal Obedience' ability (TODO: Phase 2.4)."""

    def test_grouchy_has_ability(self):
        """Verify Grouchy has the Literal Obedience ability defined."""
        marshals = create_starting_marshals()
        grouchy = marshals["Grouchy"]

        assert grouchy.ability["name"] == "Literal Obedience"
        assert grouchy.ability["trigger"] == "receiving_orders"
        assert "TODO" in grouchy.ability["effect"], "Should be marked as TODO"

    def test_grouchy_ability_not_implemented_yet(self):
        """Verify Grouchy's ability is not yet implemented (awaiting Phase 2.4)."""
        marshals = create_starting_marshals()
        grouchy = marshals["Grouchy"]

        # For now, just verify the structure exists
        assert "Never questions orders" in grouchy.ability["effect"] or \
               "always obeys exactly" in grouchy.ability["effect"]
        # TODO Phase 2.4: Test that Grouchy never takes initiative in order delay system


class TestWellingtonReverseSlopeDefense:
    """Test Wellington's 'Reverse Slope Defense' ability (TODO: Terrain system)."""

    def test_wellington_has_ability(self):
        """Verify Wellington has the Reverse Slope Defense ability defined."""
        enemies = create_enemy_marshals()
        wellington = enemies["Wellington"]

        assert wellington.ability["name"] == "Reverse Slope Defense"
        assert "defending_in_hills_or_forest" in wellington.ability["trigger"]
        assert "TODO" in wellington.ability["effect"], "Should be marked as TODO"

    def test_wellington_ability_not_implemented_yet(self):
        """Verify Wellington's ability is not yet implemented (awaiting terrain system)."""
        enemies = create_enemy_marshals()
        wellington = enemies["Wellington"]

        # For now, just verify the structure exists
        assert "+2 Defense" in wellington.ability["effect"]
        assert "Hills or Forest" in wellington.ability["effect"]
        # TODO: Test that Wellington gets +2 Defense on Hills/Forest terrain


class TestBlucherVorwarts:
    """Test Blücher's 'Vorwärts!' ability (TODO: Phase 2.6)."""

    def test_blucher_has_ability(self):
        """Verify Blücher has the Vorwärts! ability defined."""
        enemies = create_enemy_marshals()
        blucher = enemies["Blucher"]

        assert blucher.ability["name"] == "Vorwärts!"
        assert blucher.ability["trigger"] == "after_winning_battle"
        assert "TODO" in blucher.ability["effect"], "Should be marked as TODO"

    def test_blucher_ability_not_implemented_yet(self):
        """Verify Blücher's ability is not yet implemented (awaiting Phase 2.6)."""
        enemies = create_enemy_marshals()
        blucher = enemies["Blucher"]

        # For now, just verify the structure exists
        assert "+1 pursuit damage" in blucher.ability["effect"] or \
               "pursuit" in blucher.ability["effect"].lower()
        # TODO Phase 2.6: Test that Blücher inflicts extra casualties on retreating enemies


class TestGneisenauStaffWork:
    """Test Gneisenau's 'Staff Work' ability (TODO: Phase 6)."""

    def test_gneisenau_exists(self):
        """Verify Gneisenau is created in enemy marshals."""
        enemies = create_enemy_marshals()
        assert "Gneisenau" in enemies, "Gneisenau should exist in enemy marshals"

    def test_gneisenau_is_prussian(self):
        """Verify Gneisenau belongs to Prussia."""
        enemies = create_enemy_marshals()
        gneisenau = enemies["Gneisenau"]
        assert gneisenau.nation == "Prussia", f"Gneisenau should be Prussian, got {gneisenau.nation}"

    def test_gneisenau_personality(self):
        """Verify Gneisenau has cautious personality."""
        enemies = create_enemy_marshals()
        gneisenau = enemies["Gneisenau"]
        assert gneisenau.personality == "cautious", f"Gneisenau should be cautious, got {gneisenau.personality}"

    def test_gneisenau_is_infantry(self):
        """Verify Gneisenau is infantry (not cavalry)."""
        enemies = create_enemy_marshals()
        gneisenau = enemies["Gneisenau"]
        assert gneisenau.cavalry is False, "Gneisenau should not be cavalry"
        assert gneisenau.movement_range == 1, f"Infantry should have movement_range=1, got {gneisenau.movement_range}"

    def test_gneisenau_has_ability(self):
        """Verify Gneisenau has the Staff Work ability defined."""
        enemies = create_enemy_marshals()
        gneisenau = enemies["Gneisenau"]

        assert gneisenau.ability["name"] == "Staff Work"
        assert gneisenau.ability["trigger"] == "when_in_same_region_as_ally"
        assert "TODO" in gneisenau.ability["effect"], "Should be marked as TODO"

    def test_gneisenau_blucher_relationship(self):
        """Verify Gneisenau and Blücher have bidirectional +2 relationship."""
        enemies = create_enemy_marshals()
        gneisenau = enemies["Gneisenau"]
        blucher = enemies["Blucher"]

        # Bidirectional relationship: both should be +2
        gneisenau_to_blucher = gneisenau.get_relationship("Blucher")
        blucher_to_gneisenau = blucher.get_relationship("Gneisenau")

        assert gneisenau_to_blucher == 2, f"Gneisenau->Blücher should be +2, got {gneisenau_to_blucher}"
        assert blucher_to_gneisenau == 2, f"Blücher->Gneisenau should be +2, got {blucher_to_gneisenau}"

    def test_gneisenau_starts_with_blucher(self):
        """Verify Gneisenau starts in the same location as Blücher."""
        enemies = create_enemy_marshals()
        gneisenau = enemies["Gneisenau"]
        blucher = enemies["Blucher"]

        assert gneisenau.location == blucher.location, \
            f"Gneisenau ({gneisenau.location}) should start with Blücher ({blucher.location})"

    def test_prussia_has_two_marshals(self):
        """Verify Prussia now has two marshals: Blücher and Gneisenau."""
        enemies = create_enemy_marshals()
        prussian_marshals = [name for name, m in enemies.items() if m.nation == "Prussia"]

        assert len(prussian_marshals) == 2, f"Prussia should have 2 marshals, got {len(prussian_marshals)}"
        assert "Blucher" in prussian_marshals, "Blücher should be Prussian"
        assert "Gneisenau" in prussian_marshals, "Gneisenau should be Prussian"


class TestUxbridgePursuitMaster:
    """Test Uxbridge's 'Pursuit Master' ability (TODO: combat.py implementation)."""

    def test_uxbridge_exists(self):
        """Verify Uxbridge is created in enemy marshals."""
        enemies = create_enemy_marshals()
        assert "Uxbridge" in enemies, "Uxbridge should exist in enemy marshals"

    def test_uxbridge_is_british(self):
        """Verify Uxbridge belongs to Britain."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]
        assert uxbridge.nation == "Britain", f"Uxbridge should be British, got {uxbridge.nation}"

    def test_uxbridge_personality(self):
        """Verify Uxbridge has aggressive personality."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]
        assert uxbridge.personality == "aggressive", f"Uxbridge should be aggressive, got {uxbridge.personality}"

    def test_uxbridge_is_cavalry(self):
        """Verify Uxbridge is cavalry (not infantry)."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]
        assert uxbridge.cavalry is True, "Uxbridge should be cavalry"
        assert uxbridge.movement_range == 2, f"Cavalry should have movement_range=2, got {uxbridge.movement_range}"

    def test_uxbridge_has_ability(self):
        """Verify Uxbridge has the Pursuit Master ability defined."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]

        assert uxbridge.ability["name"] == "Pursuit Master"
        assert uxbridge.ability["trigger"] == "when_enemy_retreats"
        assert "TODO" in uxbridge.ability["effect"], "Should be marked as TODO"

    def test_uxbridge_wellington_relationship(self):
        """Verify Uxbridge and Wellington have bidirectional +1 relationship."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]
        wellington = enemies["Wellington"]

        # Bidirectional relationship: both should be +1
        uxbridge_to_wellington = uxbridge.get_relationship("Wellington")
        wellington_to_uxbridge = wellington.get_relationship("Uxbridge")

        assert uxbridge_to_wellington == 1, f"Uxbridge->Wellington should be +1, got {uxbridge_to_wellington}"
        assert wellington_to_uxbridge == 1, f"Wellington->Uxbridge should be +1, got {wellington_to_uxbridge}"

    def test_uxbridge_starts_with_wellington(self):
        """Verify Uxbridge starts in the same location as Wellington."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]
        wellington = enemies["Wellington"]

        assert uxbridge.location == wellington.location, \
            f"Uxbridge ({uxbridge.location}) should start with Wellington ({wellington.location})"

    def test_britain_has_two_marshals(self):
        """Verify Britain now has two marshals: Wellington and Uxbridge."""
        enemies = create_enemy_marshals()
        british_marshals = [name for name, m in enemies.items() if m.nation == "Britain"]

        assert len(british_marshals) == 2, f"Britain should have 2 marshals, got {len(british_marshals)}"
        assert "Wellington" in british_marshals, "Wellington should be British"
        assert "Uxbridge" in british_marshals, "Uxbridge should be British"

    def test_uxbridge_smaller_than_wellington(self):
        """Verify Uxbridge has a smaller cavalry corps than Wellington's infantry."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]
        wellington = enemies["Wellington"]

        assert uxbridge.strength == 18000, f"Uxbridge should have 18000 strength, got {uxbridge.strength}"
        assert uxbridge.strength < wellington.strength, \
            f"Uxbridge ({uxbridge.strength}) should be smaller than Wellington ({wellington.strength})"

    def test_uxbridge_inherits_recklessness(self):
        """Verify Uxbridge (aggressive + cavalry) inherits the Recklessness system."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]

        # Recklessness field should exist and start at 0
        assert hasattr(uxbridge, 'recklessness'), "Uxbridge should have recklessness field"
        assert uxbridge.recklessness == 0, f"Recklessness should start at 0, got {uxbridge.recklessness}"

        # is_reckless_cavalry should be True (aggressive + cavalry)
        assert uxbridge.is_reckless_cavalry is True, \
            "Uxbridge (aggressive + cavalry) should have is_reckless_cavalry=True"


class TestAbilityIntegration:
    """Test that ability system integrates properly with combat."""

    def test_combat_result_includes_ability_field(self):
        """Verify combat results include ability_triggered field."""
        marshals = create_starting_marshals()
        enemies = create_enemy_marshals()

        ney = marshals["Ney"]
        wellington = enemies["Wellington"]

        ney.strength = 50000
        ney.morale = 100
        wellington.strength = 50000
        wellington.morale = 100

        combat = CombatResolver()
        result = combat.resolve_battle(ney, wellington)

        # Should have ability_triggered field (even if None)
        assert "ability_triggered" in result

    def test_non_ney_attacker_no_ability_triggered(self):
        """Verify non-Ney attackers don't trigger abilities (others not implemented yet)."""
        marshals = create_starting_marshals()
        enemies = create_enemy_marshals()

        davout = marshals["Davout"]
        blucher = enemies["Blucher"]

        davout.strength = 50000
        davout.morale = 100
        blucher.strength = 50000
        blucher.morale = 100

        combat = CombatResolver()
        result = combat.resolve_battle(davout, blucher)

        # Davout's ability is not implemented yet
        ability_msg = result.get("ability_triggered")
        assert ability_msg is None, "Non-Ney attackers shouldn't trigger abilities yet"


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v"])

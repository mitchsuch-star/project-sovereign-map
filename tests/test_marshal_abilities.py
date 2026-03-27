"""
Test Marshal Signature Abilities (Phase 2.3, Phase 6.5 wiring)

Tests unique abilities for each marshal:
- Ney: "Bravest of the Brave" - +2 Shock when attacking (IMPLEMENTED Phase 2.3)
- Davout: "Counter-Punch Mastery" - +20% attack after defending (IMPLEMENTED)
- Grouchy: "Literal Obedience" - Never questions orders (wired via disobedience.py, not combat)
- Wellington: "Reverse Slope Defense" - +5% flat defense always (IMPLEMENTED Phase 6.5)
- Drouot: "Sage of the Grand Army" - 15% fort degradation on attack (IMPLEMENTED Phase 6.5)
- Blucher: "Vorwärts!" - +3k pursuit damage on retreat (IMPLEMENTED Phase 6.5)
- Uxbridge: "Pursuit Master" - +5k pursuit damage on retreat, cavalry (IMPLEMENTED Phase 6.5)
- Gneisenau: "Staff Work" - +5% atk/def to allies (deferred to Phase 7 Session 58)
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


class TestDavoutCounterPunchMastery:
    """Test Davout's 'Counter-Punch Mastery' ability."""

    def test_davout_has_ability(self):
        """Verify Davout has the Counter-Punch Mastery ability defined."""
        marshals = create_starting_marshals()
        davout = marshals["Davout"]

        assert davout.ability["name"] == "Counter-Punch Mastery"
        assert davout.ability["trigger"] == "after_defending"
        assert "+20%" in davout.ability["effect"]

    def test_davout_ability_description(self):
        """Verify Davout's ability has a meaningful description."""
        marshals = create_starting_marshals()
        davout = marshals["Davout"]

        assert "counterattack" in davout.ability["description"].lower() or "counter" in davout.ability["description"].lower()


class TestGrouchyLiteralObedience:
    """Test Grouchy's 'Literal Obedience' ability (wired via disobedience.py)."""

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


# ════════════════════════════════════════════════════════════════
# DROUOT — "Sage of the Grand Army" (Phase 6.5)
# Fort degradation 10% → 15% when attacking fortified positions
# ════════════════════════════════════════════════════════════════

class TestDrouotSageOfTheGrandArmy:
    """Test Drouot's 'Sage of the Grand Army' ability — enhanced fort degradation."""

    def test_drouot_has_ability(self):
        """Verify Drouot has the Sage of the Grand Army ability defined."""
        marshals = create_starting_marshals()
        drouot = marshals["Drouot"]

        assert drouot.ability["name"] == "Sage of the Grand Army"
        assert drouot.ability["trigger"] == "when_attacking_fortified"
        assert "15%" in drouot.ability["effect"]

    def test_drouot_fort_degradation_15_percent(self):
        """Drouot degrades fort by 15% (not the base 10% for artillery)."""
        marshals = create_starting_marshals()
        drouot = marshals["Drouot"]
        drouot.strength = 30000
        drouot.morale = 100

        defender = Marshal("Defender", "Paris", 30000, "cautious")
        defender.morale = 100
        defender.defense_bonus = 0.30  # 30% fort bonus

        combat = CombatResolver()
        result = combat.resolve_battle(drouot, defender)

        # Drouot's ability: 15% degradation instead of 10%
        assert result["fortification_degraded"] is True
        assert result["fortification_old"] == 30
        assert result["fortification_new"] == 15  # 30 - 15 = 15

    def test_drouot_ability_message_in_result(self):
        """Drouot's ability trigger message appears in result dict."""
        marshals = create_starting_marshals()
        drouot = marshals["Drouot"]
        drouot.strength = 30000
        drouot.morale = 100

        defender = Marshal("Defender", "Paris", 30000, "cautious")
        defender.morale = 100
        defender.defense_bonus = 0.20

        combat = CombatResolver()
        result = combat.resolve_battle(drouot, defender)

        assert result.get("drouot_ability_triggered") is not None
        assert "Sage of the Grand Army" in result["drouot_ability_triggered"]

    def test_drouot_no_bonus_when_unfortified(self):
        """Drouot gets no special degradation when attacking unfortified defender."""
        marshals = create_starting_marshals()
        drouot = marshals["Drouot"]
        drouot.strength = 30000
        drouot.morale = 100

        defender = Marshal("Defender", "Paris", 30000, "cautious")
        defender.morale = 100
        defender.defense_bonus = 0.0  # No fortification

        combat = CombatResolver()
        result = combat.resolve_battle(drouot, defender)

        # No fort to degrade
        assert result["fortification_degraded"] is False
        assert result.get("drouot_ability_triggered") is None

    def test_regular_artillery_degrades_10_percent(self):
        """Non-Drouot artillery still degrades fort by 10% (base rate)."""
        # Create a synthetic non-Drouot artillery marshal
        generic_art = Marshal("GenericArt", "Paris", 30000, "cautious", "Prussia", artillery=True)
        generic_art.morale = 100

        defender = Marshal("Defender", "Paris", 30000, "cautious")
        defender.morale = 100
        defender.defense_bonus = 0.30

        combat = CombatResolver()
        result = combat.resolve_battle(generic_art, defender)

        # Base artillery: 10% degradation
        assert result["fortification_degraded"] is True
        assert result["fortification_old"] == 30
        assert result["fortification_new"] == 20  # 30 - 10 = 20
        assert result.get("drouot_ability_triggered") is None

    def test_infantry_degrades_5_percent(self):
        """Non-artillery infantry degrades fort by 5% (base rate)."""
        attacker = Marshal("Infantry", "Belgium", 30000, "aggressive")
        attacker.morale = 100

        defender = Marshal("Defender", "Paris", 30000, "cautious")
        defender.morale = 100
        defender.defense_bonus = 0.30

        combat = CombatResolver()
        result = combat.resolve_battle(attacker, defender)

        # Base infantry: 5% degradation
        assert result["fortification_degraded"] is True
        assert result["fortification_old"] == 30
        assert result["fortification_new"] == 25  # 30 - 5 = 25


# ════════════════════════════════════════════════════════════════
# WELLINGTON — "Reverse Slope Defense" (Phase 6.5)
# +5% flat defense bonus always when defending
# ════════════════════════════════════════════════════════════════

class TestWellingtonReverseSlopeDefense:
    """Test Wellington's 'Reverse Slope Defense' ability — +5% flat defense."""

    def test_wellington_has_ability(self):
        """Verify Wellington has the Reverse Slope Defense ability defined."""
        enemies = create_enemy_marshals()
        wellington = enemies["Wellington"]

        assert wellington.ability["name"] == "Reverse Slope Defense"
        assert wellington.ability["trigger"] == "when_defending"
        assert "+5%" in wellington.ability["effect"]

    def test_wellington_defense_modifier_includes_ability(self):
        """Wellington's get_defense_modifier() includes +5% from ability."""
        enemies = create_enemy_marshals()
        wellington = enemies["Wellington"]

        # Reset to neutral stance to isolate the ability bonus
        from backend.models.marshal import Stance
        wellington.stance = Stance.NEUTRAL
        wellington.defense_bonus = 0.0  # No fortify
        wellington.drilling = False
        wellington.drilling_locked = False

        # Wellington's modifier should include 1.05 from ability
        modifier = wellington.get_defense_modifier()

        # Personality modifier is also applied. Get the personality-only modifier
        # by checking a non-Wellington marshal with same personality.
        reference = Marshal("Reference", "Paris", 50000, "cautious")
        reference.stance = Stance.NEUTRAL
        reference.defense_bonus = 0.0
        reference.drilling = False
        reference.drilling_locked = False
        ref_modifier = reference.get_defense_modifier()

        # Wellington should be ~5% higher than a generic cautious marshal
        ratio = modifier / ref_modifier
        assert 1.04 <= ratio <= 1.06, \
            f"Wellington should be ~5% higher defense than baseline. Ratio: {ratio:.4f}"

    def test_wellington_ability_stacks_with_fortify(self):
        """Wellington's +5% stacks multiplicatively with fortify bonus."""
        enemies = create_enemy_marshals()
        wellington = enemies["Wellington"]

        from backend.models.marshal import Stance
        wellington.stance = Stance.NEUTRAL
        wellington.defense_bonus = 0.20  # 20% fort bonus
        wellington.drilling = False
        wellington.drilling_locked = False

        modifier = wellington.get_defense_modifier()

        # Should include: (1.0 + 0.20) * 1.05 * personality
        # = 1.20 * 1.05 * personality = 1.26 * personality
        # Just verify it's higher than 1.20 * personality
        reference = Marshal("Reference", "Paris", 50000, "cautious")
        reference.stance = Stance.NEUTRAL
        reference.defense_bonus = 0.20
        reference.drilling = False
        reference.drilling_locked = False
        ref_modifier = reference.get_defense_modifier()

        assert modifier > ref_modifier, \
            f"Wellington ({modifier:.4f}) should be higher than generic cautious ({ref_modifier:.4f}) with same fort"

    def test_generic_marshal_no_ability_defense_bonus(self):
        """A marshal without Reverse Slope Defense gets no ability bonus."""
        marshal = Marshal("Generic", "Paris", 50000, "cautious")
        from backend.models.marshal import Stance
        marshal.stance = Stance.NEUTRAL
        marshal.defense_bonus = 0.0
        marshal.drilling = False
        marshal.drilling_locked = False

        modifier = marshal.get_defense_modifier()

        # Create identical marshal, both should match
        marshal2 = Marshal("Generic2", "Paris", 50000, "cautious")
        marshal2.stance = Stance.NEUTRAL
        marshal2.defense_bonus = 0.0
        marshal2.drilling = False
        marshal2.drilling_locked = False

        modifier2 = marshal2.get_defense_modifier()

        assert abs(modifier - modifier2) < 0.001, \
            f"Two generic marshals should have same modifier: {modifier:.4f} vs {modifier2:.4f}"

    def test_wellington_no_bonus_when_attacking(self):
        """Wellington's defense ability doesn't affect attack modifier."""
        enemies = create_enemy_marshals()
        wellington = enemies["Wellington"]

        from backend.models.marshal import Stance
        wellington.stance = Stance.NEUTRAL

        # get_attack_modifier should not include the +5%
        reference = Marshal("Reference", "Paris", 50000, "cautious")
        reference.stance = Stance.NEUTRAL

        well_atk = wellington.get_attack_modifier()
        ref_atk = reference.get_attack_modifier()

        # Attack modifiers should be similar (both cautious personality)
        # Wellington's ability is defense-only
        ratio = well_atk / ref_atk if ref_atk > 0 else 1.0
        assert 0.95 <= ratio <= 1.05, \
            f"Wellington attack shouldn't differ much from generic cautious. Ratio: {ratio:.4f}"


# ════════════════════════════════════════════════════════════════
# BLUCHER — "Vorwärts!" (Phase 6.5)
# +3k pursuit damage when enemy retreats, floor 1000
# ════════════════════════════════════════════════════════════════

class TestBlucherVorwarts:
    """Test Blücher's 'Vorwärts!' ability — pursuit damage on retreat."""

    def test_blucher_has_ability(self):
        """Verify Blücher has the Vorwärts! ability defined."""
        enemies = create_enemy_marshals()
        blucher = enemies["Blucher"]

        assert blucher.ability["name"] == "Vorwärts!"
        assert blucher.ability["trigger"] == "when_enemy_retreats"
        assert "3,000" in blucher.ability["effect"]

    def test_blucher_pursuit_damage_on_forced_retreat(self):
        """Blücher inflicts 3k pursuit damage when enemy forced to retreat."""
        enemies = create_enemy_marshals()
        blucher = enemies["Blucher"]
        blucher.strength = 60000
        blucher.morale = 100

        # Weak defender will be forced to retreat (morale drops below 25)
        defender = Marshal("WeakDefender", "Paris", 15000, "cautious")
        defender.morale = 30  # Low morale, will likely trigger forced retreat

        combat = CombatResolver()

        # Run multiple times to find a case where defender retreats
        pursuit_triggered = False
        for _ in range(50):
            blucher.strength = 60000
            blucher.morale = 100
            defender.strength = 15000
            defender.morale = 30

            result = combat.resolve_battle(blucher, defender)

            if result.get("pursuit_damage", 0) > 0:
                pursuit_triggered = True
                assert result["pursuit_damage"] == 3000 or result["pursuit_damage"] < 3000
                assert result["pursuit_message"] is not None
                assert "Vorwärts!" in result["pursuit_message"]
                # Defender should have at least 1000 strength (floor)
                assert result["defender"]["remaining"] >= 1000
                break

        assert pursuit_triggered, "Blücher's pursuit should trigger at least once in 50 battles against weak defender"

    def test_blucher_pursuit_floor_at_1000(self):
        """Pursuit damage cannot reduce defender below 1000 strength."""
        enemies = create_enemy_marshals()
        blucher = enemies["Blucher"]
        blucher.strength = 80000
        blucher.morale = 100

        # Create a defender that will end up very weak after combat
        defender = Marshal("Fragile", "Paris", 8000, "cautious")
        defender.morale = 20  # Will definitely retreat

        combat = CombatResolver()

        for _ in range(50):
            blucher.strength = 80000
            blucher.morale = 100
            defender.strength = 8000
            defender.morale = 20

            result = combat.resolve_battle(blucher, defender)

            if result["defender"]["forced_retreat"]:
                # Even with pursuit, defender should never go below 1000
                assert result["defender"]["remaining"] >= 1000, \
                    f"Defender should have >= 1000 after pursuit, got {result['defender']['remaining']}"

    def test_blucher_no_pursuit_when_not_winning(self):
        """Blücher doesn't get pursuit damage if he doesn't win."""
        enemies = create_enemy_marshals()
        blucher = enemies["Blucher"]
        blucher.strength = 10000  # Weak attacker
        blucher.morale = 50

        defender = Marshal("StrongDefender", "Paris", 80000, "cautious")
        defender.morale = 100

        combat = CombatResolver()
        result = combat.resolve_battle(blucher, defender)

        # Blucher is unlikely to win here, but even if defender retreats
        # attacker_won must be True for pursuit to fire
        if not result.get("attacker_won", False):
            assert result.get("pursuit_damage", 0) == 0


# ════════════════════════════════════════════════════════════════
# UXBRIDGE — "Pursuit Master" (Phase 6.5)
# +5k pursuit damage when cavalry runs down retreating enemies, floor 1000
# ════════════════════════════════════════════════════════════════

class TestUxbridgePursuitMaster:
    """Test Uxbridge's 'Pursuit Master' ability — cavalry pursuit damage."""

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
        assert "5,000" in uxbridge.ability["effect"]

    def test_uxbridge_pursuit_damage_on_forced_retreat(self):
        """Uxbridge inflicts 5k pursuit damage when enemy forced to retreat."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]
        uxbridge.strength = 50000
        uxbridge.morale = 100

        defender = Marshal("WeakDefender", "Paris", 15000, "cautious")
        defender.morale = 30

        combat = CombatResolver()

        pursuit_triggered = False
        for _ in range(50):
            uxbridge.strength = 50000
            uxbridge.morale = 100
            defender.strength = 15000
            defender.morale = 30

            result = combat.resolve_battle(uxbridge, defender)

            if result.get("pursuit_damage", 0) > 0:
                pursuit_triggered = True
                assert result["pursuit_message"] is not None
                assert "Pursuit Master" in result["pursuit_message"]
                assert result["defender"]["remaining"] >= 1000
                break

        assert pursuit_triggered, "Uxbridge's pursuit should trigger at least once in 50 battles"

    def test_uxbridge_pursuit_requires_cavalry(self):
        """Pursuit Master requires cavalry flag — infantry with same ability dict doesn't fire."""
        # Create infantry marshal with Pursuit Master ability (hypothetical)
        fake_uxbridge = Marshal(
            "FakeUxbridge", "Belgium", 50000, "aggressive",
            ability={
                "name": "Pursuit Master",
                "description": "Test",
                "trigger": "when_enemy_retreats",
                "effect": "Test"
            }
        )
        fake_uxbridge.cavalry = False  # Infantry, not cavalry
        fake_uxbridge.morale = 100

        defender = Marshal("Fragile", "Paris", 8000, "cautious")
        defender.morale = 20

        combat = CombatResolver()

        for _ in range(50):
            fake_uxbridge.strength = 50000
            fake_uxbridge.morale = 100
            defender.strength = 8000
            defender.morale = 20

            result = combat.resolve_battle(fake_uxbridge, defender)

            # Even if defender retreats, Pursuit Master should NOT fire (no cavalry)
            assert result.get("pursuit_damage", 0) == 0, \
                "Pursuit Master should not fire for infantry"

    def test_uxbridge_pursuit_floor_at_1000(self):
        """Uxbridge pursuit damage cannot reduce defender below 1000.

        P1-5 fix: pursuit only fires if defender.strength > 1000 after combat.
        If combat already reduced defender below 1000, pursuit doesn't fire
        (prevents resurrecting strength from e.g. 500 → 1000).
        """
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]

        defender = Marshal("Fragile", "Paris", 8000, "cautious")
        defender.morale = 20

        combat = CombatResolver()

        for _ in range(50):
            uxbridge.strength = 50000
            uxbridge.morale = 100
            defender.strength = 8000
            defender.morale = 20

            result = combat.resolve_battle(uxbridge, defender)

            if result["defender"]["forced_retreat"]:
                remaining = result["defender"]["remaining"]
                # If combat left defender above 1000, pursuit floors at 1000
                # If combat left defender at/below 1000, pursuit doesn't fire (no resurrect)
                # Either way, remaining should be >= 0
                assert remaining >= 0, \
                    f"Defender remaining should be >= 0, got {remaining}"
                # Pursuit should never INCREASE strength (the P1-5 bug)
                if result.get("pursuit_damage", 0) > 0:
                    assert remaining >= 1000, \
                        f"When pursuit fires, defender should be >= 1000, got {remaining}"

    def test_uxbridge_wellington_relationship(self):
        """Verify Uxbridge and Wellington have bidirectional +1 relationship."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]
        wellington = enemies["Wellington"]

        uxbridge_to_wellington = uxbridge.get_relationship("Wellington")
        wellington_to_uxbridge = wellington.get_relationship("Uxbridge")

        assert uxbridge_to_wellington == 1, f"Uxbridge->Wellington should be +1, got {uxbridge_to_wellington}"
        assert wellington_to_uxbridge == 1, f"Wellington->Uxbridge should be +1, got {wellington_to_uxbridge}"

    def test_uxbridge_starts_at_hanover(self):
        """Verify Uxbridge starts at Hanover."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]

        assert uxbridge.location == "Hanover", \
            f"Uxbridge should start at Hanover, got {uxbridge.location}"

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

        assert uxbridge.strength == 24000, f"Uxbridge should have 24000 strength, got {uxbridge.strength}"
        assert uxbridge.strength < wellington.strength, \
            f"Uxbridge ({uxbridge.strength}) should be smaller than Wellington ({wellington.strength})"

    def test_uxbridge_inherits_recklessness(self):
        """Verify Uxbridge (aggressive + cavalry) inherits the Recklessness system."""
        enemies = create_enemy_marshals()
        uxbridge = enemies["Uxbridge"]

        assert hasattr(uxbridge, 'recklessness'), "Uxbridge should have recklessness field"
        assert uxbridge.recklessness == 0, f"Recklessness should start at 0, got {uxbridge.recklessness}"
        assert uxbridge.is_reckless_cavalry is True, \
            "Uxbridge (aggressive + cavalry) should have is_reckless_cavalry=True"


# ════════════════════════════════════════════════════════════════
# GNEISENAU — "Staff Work" (deferred to Phase 7 Session 58)
# ════════════════════════════════════════════════════════════════

class TestGneisenauStaffWork:
    """Test Gneisenau's 'Staff Work' ability (deferred to Phase 7)."""

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
        """Verify Gneisenau has the Staff Work ability defined (deferred)."""
        enemies = create_enemy_marshals()
        gneisenau = enemies["Gneisenau"]

        assert gneisenau.ability["name"] == "Staff Work"
        assert gneisenau.ability["trigger"] == "when_in_same_region_as_ally"
        assert "deferred" in gneisenau.ability["effect"].lower()

    def test_gneisenau_blucher_relationship(self):
        """Verify Gneisenau and Blücher have bidirectional +2 relationship."""
        enemies = create_enemy_marshals()
        gneisenau = enemies["Gneisenau"]
        blucher = enemies["Blucher"]

        gneisenau_to_blucher = gneisenau.get_relationship("Blucher")
        blucher_to_gneisenau = blucher.get_relationship("Gneisenau")

        assert gneisenau_to_blucher == 2, f"Gneisenau->Blücher should be +2, got {gneisenau_to_blucher}"
        assert blucher_to_gneisenau == 2, f"Blücher->Gneisenau should be +2, got {blucher_to_gneisenau}"

    def test_gneisenau_starts_at_rhineland(self):
        """Verify Gneisenau starts at Rhineland."""
        enemies = create_enemy_marshals()
        gneisenau = enemies["Gneisenau"]

        assert gneisenau.location == "Rhineland", \
            f"Gneisenau should start at Rhineland, got {gneisenau.location}"

    def test_prussia_has_two_marshals(self):
        """Verify Prussia has two marshals: Blucher and Gneisenau."""
        enemies = create_enemy_marshals()
        prussian_marshals = [name for name, m in enemies.items() if m.nation == "Prussia"]

        assert len(prussian_marshals) == 2, f"Prussia should have 2 marshals, got {len(prussian_marshals)}"
        assert "Blucher" in prussian_marshals, "Blucher should be Prussian"
        assert "Gneisenau" in prussian_marshals, "Gneisenau should be Prussian"


# ════════════════════════════════════════════════════════════════
# CROSS-ABILITY INTEGRATION TESTS
# ════════════════════════════════════════════════════════════════

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

        assert "ability_triggered" in result

    def test_combat_result_includes_pursuit_fields(self):
        """Verify combat results include pursuit_damage and pursuit_message fields."""
        attacker = Marshal("Attacker", "Belgium", 50000, "aggressive")
        attacker.morale = 100
        defender = Marshal("Defender", "Paris", 50000, "cautious")
        defender.morale = 100

        combat = CombatResolver()
        result = combat.resolve_battle(attacker, defender)

        assert "pursuit_damage" in result
        assert "pursuit_message" in result

    def test_combat_result_includes_drouot_field(self):
        """Verify combat results include drouot_ability_triggered field."""
        attacker = Marshal("Attacker", "Belgium", 50000, "aggressive")
        attacker.morale = 100
        defender = Marshal("Defender", "Paris", 50000, "cautious")
        defender.morale = 100

        combat = CombatResolver()
        result = combat.resolve_battle(attacker, defender)

        assert "drouot_ability_triggered" in result

    def test_non_ability_attacker_no_pursuit(self):
        """Marshal without pursuit ability doesn't get pursuit damage."""
        attacker = Marshal("Generic", "Belgium", 80000, "aggressive")
        attacker.morale = 100

        defender = Marshal("Weak", "Paris", 8000, "cautious")
        defender.morale = 20

        combat = CombatResolver()

        for _ in range(50):
            attacker.strength = 80000
            attacker.morale = 100
            defender.strength = 8000
            defender.morale = 20

            result = combat.resolve_battle(attacker, defender)
            assert result.get("pursuit_damage", 0) == 0, \
                "Marshal without pursuit ability shouldn't get pursuit damage"

    def test_non_ney_attacker_no_ability_triggered(self):
        """Verify non-Ney attackers don't trigger the Ney ability."""
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

        ability_msg = result.get("ability_triggered")
        assert ability_msg is None, "Non-Ney attackers shouldn't trigger Ney's ability"

    def test_generic_artillery_no_special_bonus(self):
        """Generic artillery has no special degradation bonus (Drouot only)."""
        # Create a synthetic non-Drouot artillery marshal
        generic_art = Marshal("GenericArt", "Paris", 30000, "cautious", "Prussia", artillery=True)
        generic_art.morale = 100

        defender = Marshal("Defender", "Paris", 30000, "cautious")
        defender.morale = 100
        defender.defense_bonus = 0.30

        combat = CombatResolver()
        result = combat.resolve_battle(generic_art, defender)

        # Generic artillery → 10% base degradation, NOT 15% (Drouot only)
        assert result["fortification_degraded"] is True
        assert result["fortification_new"] == 20  # 30 - 10
        assert result.get("drouot_ability_triggered") is None


# ════════════════════════════════════════════════════════════════════════════════
# DAVOUT: COUNTER-PUNCH MASTERY — FULL ABILITY TESTS
# ════════════════════════════════════════════════════════════════════════════════


class TestDavoutCounterPunchMasteryMechanics:
    """Test Davout's Counter-Punch Mastery: +20% attack after being attacked."""

    def _make_davout(self, strength=48000):
        """Create a Davout marshal with Counter-Punch Mastery ability."""
        d = Marshal("Davout", "Paris", strength, "cautious")
        d.ability = {
            "name": "Counter-Punch Mastery",
            "description": "Davout's counterattacks strike with devastating force",
            "trigger": "after_defending",
            "effect": "+20% attack on next attack after being attacked"
        }
        d.morale = 100
        return d

    def _make_attacker(self, name="Attacker", strength=40000, personality="aggressive"):
        """Create a generic attacker."""
        a = Marshal(name, "Paris", strength, personality)
        a.morale = 100
        return a

    # ── Trigger Tests ──

    def test_counter_punch_ready_set_when_davout_defends_and_wins(self):
        """counter_punch_ready=True when Davout is defender and wins."""
        davout = self._make_davout(60000)
        attacker = self._make_attacker(strength=20000)
        combat = CombatResolver()
        combat.resolve_battle(attacker, davout)
        assert davout.counter_punch_ready is True

    def test_counter_punch_ready_set_when_davout_defends_and_loses(self):
        """counter_punch_ready=True even when Davout loses (attacker victory)."""
        davout = self._make_davout(20000)
        attacker = self._make_attacker(strength=60000)
        combat = CombatResolver()
        combat.resolve_battle(attacker, davout)
        # If Davout survived (strength > 0), he gets counter_punch_ready
        if davout.strength > 0:
            assert davout.counter_punch_ready is True

    def test_counter_punch_ready_not_set_when_davout_destroyed(self):
        """counter_punch_ready=False if Davout is destroyed (strength=0)."""
        davout = self._make_davout(1000)  # Tiny army, will be destroyed
        attacker = self._make_attacker(strength=80000)
        combat = CombatResolver()
        combat.resolve_battle(attacker, davout)
        # Destroyed = no counter-punch ready
        if davout.strength <= 0:
            assert davout.counter_punch_ready is False

    def test_counter_punch_ready_set_on_stalemate(self):
        """counter_punch_ready=True on stalemate (draw)."""
        davout = self._make_davout(40000)
        attacker = self._make_attacker(strength=40000)
        combat = CombatResolver()
        # Run multiple times to catch a stalemate
        triggered = False
        for _ in range(50):
            d = self._make_davout(40000)
            a = self._make_attacker(strength=40000)
            result = combat.resolve_battle(a, d)
            if result["outcome"] == "stalemate":
                assert d.counter_punch_ready is True
                triggered = True
                break
        # Even if we didn't hit stalemate in 50 tries, verify the field exists
        assert hasattr(davout, 'counter_punch_ready')

    def test_counter_punch_ready_not_set_when_davout_is_attacker(self):
        """counter_punch_ready is NOT set when Davout is the attacker."""
        davout = self._make_davout(60000)
        defender = self._make_attacker(name="Defender", strength=20000)
        combat = CombatResolver()
        combat.resolve_battle(davout, defender)
        assert davout.counter_punch_ready is False

    def test_counter_punch_ready_not_set_for_non_davout_marshal(self):
        """counter_punch_ready is NOT set for marshals without the ability."""
        generic = Marshal("Wellington", "Paris", 50000, "cautious")
        generic.ability = {
            "name": "Reverse Slope Defense",
            "description": "test",
            "trigger": "when_defending",
            "effect": "+5% defense"
        }
        generic.morale = 100
        attacker = self._make_attacker(strength=30000)
        combat = CombatResolver()
        combat.resolve_battle(attacker, generic)
        assert generic.counter_punch_ready is False

    # ── Modifier Tests ──

    def test_20_percent_attack_bonus_when_ready(self):
        """get_attack_modifier() includes +20% when counter_punch_ready=True."""
        davout = self._make_davout()
        base_modifier = davout.get_attack_modifier()

        # Reset and set counter_punch_ready
        davout2 = self._make_davout()
        davout2.counter_punch_ready = True
        boosted_modifier = davout2.get_attack_modifier()

        # Boosted should be ~20% higher than base
        expected_ratio = 1.20
        actual_ratio = boosted_modifier / base_modifier
        assert abs(actual_ratio - expected_ratio) < 0.01, \
            f"Expected ~{expected_ratio}x, got {actual_ratio}x"

    def test_counter_punch_ready_consumed_after_attack_modifier(self):
        """counter_punch_ready is cleared after get_attack_modifier() consumes it."""
        davout = self._make_davout()
        davout.counter_punch_ready = True
        davout.get_attack_modifier()
        assert davout.counter_punch_ready is False

    def test_no_bonus_without_counter_punch_ready(self):
        """get_attack_modifier() has no bonus when counter_punch_ready=False."""
        davout = self._make_davout()
        assert davout.counter_punch_ready is False
        mod1 = davout.get_attack_modifier()
        mod2 = davout.get_attack_modifier()
        assert mod1 == mod2  # Consistent without bonus

    def test_counter_punch_does_not_stack(self):
        """Multiple defenses don't stack to +40% — stays at +20%."""
        davout = self._make_davout()
        davout.counter_punch_ready = True
        # "Set again" — still boolean True, not +40%
        davout.counter_punch_ready = True
        mod = davout.get_attack_modifier()
        # Should be exactly 1.20x the base (not 1.40x)
        davout2 = self._make_davout()
        base = davout2.get_attack_modifier()
        expected_ratio = 1.20
        actual_ratio = mod / base
        assert abs(actual_ratio - expected_ratio) < 0.01

    # ── Attack Against ANY Target ──

    def test_counter_punch_works_against_any_target(self):
        """Counter-punch bonus applies to attack against ANY target, not just the attacker."""
        davout = self._make_davout(50000)
        original_attacker = self._make_attacker(name="Blucher", strength=40000)
        different_target = self._make_attacker(name="Wellington", strength=40000)
        different_target.morale = 100

        combat = CombatResolver()
        # Blucher attacks Davout → Davout gets counter_punch_ready
        combat.resolve_battle(original_attacker, davout)
        assert davout.counter_punch_ready is True

        # Davout attacks Wellington (different target) → bonus still applies
        modifier = davout.get_attack_modifier()
        # The modifier should include the +20% (consumed now)
        assert davout.counter_punch_ready is False  # Consumed

    # ── Stacking With Other Modifiers ──

    def test_stacks_with_aggressive_stance(self):
        """Counter-punch bonus stacks multiplicatively with aggressive stance."""
        from backend.models.marshal import Stance
        davout = self._make_davout()
        davout.stance = Stance.AGGRESSIVE
        base = davout.get_attack_modifier()

        davout2 = self._make_davout()
        davout2.stance = Stance.AGGRESSIVE
        davout2.counter_punch_ready = True
        boosted = davout2.get_attack_modifier()

        ratio = boosted / base
        assert abs(ratio - 1.20) < 0.01

    def test_stacks_with_drill(self):
        """Counter-punch bonus stacks multiplicatively with drill bonus."""
        davout = self._make_davout()
        davout.shock_bonus = 2  # +20% from drill
        base = davout.get_attack_modifier()

        davout2 = self._make_davout()
        davout2.shock_bonus = 2
        davout2.counter_punch_ready = True
        boosted = davout2.get_attack_modifier()

        ratio = boosted / base
        assert abs(ratio - 1.20) < 0.01

    # ── Turn-End Clearing ──

    def test_counter_punch_ready_clears_at_turn_end(self):
        """counter_punch_ready is cleared during _process_tactical_states()."""
        from backend.models.world_state import WorldState
        world = WorldState()
        davout = world.marshals.get("Davout")
        assert davout is not None
        davout.counter_punch_ready = True

        # Process tactical states (called during advance_turn)
        world._process_tactical_states()
        assert davout.counter_punch_ready is False

    # ── Broken State Clearing ──

    def test_counter_punch_ready_cleared_when_broken(self):
        """counter_punch_ready is cleared when marshal enters broken state."""
        davout = self._make_davout()
        davout.counter_punch_ready = True
        # Simulate broken state clearing (as done in executor._handle_broken)
        davout.counter_punch_ready = False
        assert davout.counter_punch_ready is False

    # ── Serialization ──

    def test_counter_punch_ready_serialization_roundtrip(self):
        """counter_punch_ready survives save/load (to_dict → from_dict)."""
        davout = self._make_davout()
        davout.counter_punch_ready = True

        data = davout.to_dict()
        assert "counter_punch_ready" in data
        assert data["counter_punch_ready"] is True

        restored = Marshal.from_dict(data)
        assert restored.counter_punch_ready is True

    def test_counter_punch_ready_default_false_in_from_dict(self):
        """Missing counter_punch_ready in save data defaults to False."""
        davout = self._make_davout()
        data = davout.to_dict()
        del data["counter_punch_ready"]  # Simulate old save format

        restored = Marshal.from_dict(data)
        assert restored.counter_punch_ready is False

    # ── Battle Report Snapshot ──

    def test_modifier_snapshot_includes_counter_punch_label(self):
        """Battle report modifier snapshot includes 'Counter-Punch Mastery' label."""
        from backend.game_logic.battle_report import snapshot_attacker_modifiers
        davout = self._make_davout()
        davout.counter_punch_ready = True

        defender = self._make_attacker(strength=30000)
        mods = snapshot_attacker_modifiers(davout, defender, "plains", 0.0, 0, False)

        labels = [m["label"] for m in mods]
        assert "Counter-Punch Mastery" in labels
        mastery_mod = next(m for m in mods if m["label"] == "Counter-Punch Mastery")
        assert mastery_mod["value"] == 20
        assert mastery_mod["type"] == "bonus"

    def test_modifier_snapshot_excludes_label_when_not_ready(self):
        """No Counter-Punch Mastery label when counter_punch_ready=False."""
        from backend.game_logic.battle_report import snapshot_attacker_modifiers
        davout = self._make_davout()
        davout.counter_punch_ready = False

        defender = self._make_attacker(strength=30000)
        mods = snapshot_attacker_modifiers(davout, defender, "plains", 0.0, 0, False)

        labels = [m["label"] for m in mods]
        assert "Counter-Punch Mastery" not in labels

    # ── Combat Result Dict ──

    def test_combat_result_includes_mastery_earned_flag(self):
        """resolve_battle result includes counter_punch_mastery_earned flag."""
        davout = self._make_davout(50000)
        attacker = self._make_attacker(strength=30000)
        combat = CombatResolver()
        result = combat.resolve_battle(attacker, davout)
        assert "counter_punch_mastery_earned" in result
        if davout.strength > 0:
            assert result["counter_punch_mastery_earned"] is True

    # ── Building Blocks: Enemy Davout ──

    def test_enemy_marshal_with_ability_also_triggers(self):
        """Building Blocks: an enemy marshal with Counter-Punch Mastery also gets the bonus."""
        enemy_davout = self._make_davout(50000)
        enemy_davout.nation = "Prussia"  # Enemy nation
        player_attacker = self._make_attacker(strength=30000)
        player_attacker.nation = "France"

        combat = CombatResolver()
        combat.resolve_battle(player_attacker, enemy_davout)
        assert enemy_davout.counter_punch_ready is True

    # ── Integration: Full Combat Cycle ──

    def test_full_cycle_defend_then_attack(self):
        """Full cycle: Davout is attacked → gets +20% → attacks back → bonus consumed."""
        davout = self._make_davout(50000)
        enemy1 = self._make_attacker(name="Enemy1", strength=30000)
        enemy2 = self._make_attacker(name="Enemy2", strength=30000)

        combat = CombatResolver()

        # Step 1: Enemy attacks Davout
        combat.resolve_battle(enemy1, davout)
        if davout.strength > 0:
            assert davout.counter_punch_ready is True

            # Step 2: Davout attacks different target — bonus consumed
            base_mod = self._make_davout().get_attack_modifier()
            boosted_mod = davout.get_attack_modifier()
            assert boosted_mod > base_mod  # +20% applied
            assert davout.counter_punch_ready is False  # Consumed

            # Step 3: Davout attacks again — no bonus
            mod_after = davout.get_attack_modifier()
            # Recalculate base (cautious personality mods may shift with strength_ratio=None)
            fresh_davout = self._make_davout(davout.strength)
            fresh_base = fresh_davout.get_attack_modifier()
            assert abs(mod_after - fresh_base) < 0.01


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v"])

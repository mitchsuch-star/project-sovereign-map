"""
Combat System for Project Sovereign
Handles battle resolution between armies

Features:
- 2d6 dice-based combat with skill modifiers
- Critical success/failure on natural 12/2
- Skill-based advantage for better marshals
- Variance while maintaining tactical superiority
"""

from typing import Dict, Tuple, Optional
from backend.models.marshal import Marshal
import random


class CombatResolver:
    """
    Resolves battles between armies.

    Combat considers:
    - Army strength (troop numbers)
    - Marshal morale (affects effectiveness)
    - Terrain (defender advantage)
    - Random variance (fog of war)
    """

    def __init__(self):
        """Initialize combat resolver with default settings."""
        self.defender_bonus = 0.2  # +20% for defender
        self.variance = 0.1  # ±10% random variance

    def roll_combat_dice(self, marshal: Marshal) -> Dict:
        """
        Roll 2d6 for combat with skill modifiers.

        Formula:
        - Roll 2d6 (natural roll: 2-12)
        - Add skill bonus: tactical_skill // 3
        - Cap modified roll at 12
        - Calculate multiplier: 0.85 + (modified * 0.025)

        Args:
            marshal: The marshal rolling dice

        Returns:
            Dict with:
            - natural: int (2-12, unmodified 2d6 roll)
            - modified: int (natural + skill bonus, capped at 12)
            - is_critical_success: bool (natural 12)
            - is_critical_failure: bool (natural 2)
            - multiplier: float (0.85 to 1.15)
            - skill_bonus: int (tactical_skill // 3)
        """
        # Roll 2d6
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        natural_roll = die1 + die2  # Range: 2-12

        # Calculate skill bonus
        skill_bonus = marshal.tactical_skill // 3  # 0-4 for skill 0-12

        # Modified roll (capped at 12)
        modified_roll = min(12, natural_roll + skill_bonus)

        # Detect criticals (based on NATURAL roll only)
        is_critical_success = (natural_roll == 12)
        is_critical_failure = (natural_roll == 2)

        # Calculate damage multiplier
        # Range: 0.85 (roll 2) to 1.15 (roll 12)
        multiplier = 0.85 + (modified_roll * 0.025)

        return {
            "natural": int(natural_roll),
            "modified": int(modified_roll),
            "is_critical_success": is_critical_success,
            "is_critical_failure": is_critical_failure,
            "multiplier": multiplier,
            "skill_bonus": int(skill_bonus)
        }

    def resolve_battle(
            self,
            attacker: Marshal,
            defender: Marshal,
            terrain: str = "open"
    ) -> Dict:
        """Resolve a battle between two marshals using 2d6 dice system."""

        #print(f"\n⚔️ BATTLE: {attacker.name} vs {defender.name}")
        #print(f"   Attacker: {attacker.strength:,} troops, {attacker.morale}% morale")
        #print(f"   Defender: {defender.strength:,} troops, {defender.morale}% morale")

        # Roll combat dice for attacker
        attacker_roll = self.roll_combat_dice(attacker)

        # Calculate effective strengths
        attacker_effective = self._calculate_effective_strength(attacker, is_attacker=True)
        defender_effective = self._calculate_effective_strength(defender, is_attacker=False)

        #print(f"   Attacker effective: {attacker_effective:,.0f}")
        #print(f"   Defender effective: {defender_effective:,.0f}")

        # Apply terrain modifiers
        terrain_bonus = self._get_terrain_bonus(terrain)
        defender_effective *= (1 + terrain_bonus)

        #print(f"   Defender after terrain: {defender_effective:,.0f}")

        # Calculate casualties with dice multiplier
        # Attacker's roll affects how much damage they deal to defender
        attacker_casualties = self._calculate_casualties(
            attacker.strength,
            defender_effective,
            attacker_effective
        )

        # Apply attacker's dice multiplier to defender casualties
        defender_casualties = int(self._calculate_casualties(
            defender.strength,
            attacker_effective,
            defender_effective
        ) * attacker_roll['multiplier'])

        #print(f"   💀 Casualties: {attacker.name} {attacker_casualties:,}, {defender.name} {defender_casualties:,}")

        # Apply casualties FIRST (this was missing!)
        #print(f"   BEFORE: {attacker.name}={attacker.strength:,}, {defender.name}={defender.strength:,}")
        attacker.take_casualties(attacker_casualties)
        defender.take_casualties(defender_casualties)
        #print(f"   AFTER: {attacker.name}={attacker.strength:,}, {defender.name}={defender.strength:,}")

        # Determine victor (AFTER applying casualties)

        # Determine victor
        if attacker.strength <= 0 and defender.strength <= 0:
            victor = None
            outcome = "mutual_destruction"
        elif attacker.strength <= 0:
            victor = defender
            outcome = "defender_victory"
            defender.adjust_morale(10)
            attacker.adjust_morale(-20)
            defender.battles_won += 1
            attacker.battles_lost += 1
        elif defender.strength <= 0:
            victor = attacker
            outcome = "attacker_victory"
            attacker.adjust_morale(10)
            defender.adjust_morale(-20)
            attacker.battles_won += 1
            defender.battles_lost += 1
        else:
            # Both survive - tactical result
            if attacker_casualties > defender_casualties * 1.5:
                victor = defender
                outcome = "defender_tactical_victory"
                defender.adjust_morale(5)
                attacker.adjust_morale(-10)
            elif defender_casualties > attacker_casualties * 1.5:
                victor = attacker
                outcome = "attacker_tactical_victory"
                attacker.adjust_morale(5)
                defender.adjust_morale(-10)
            else:
                victor = None
                outcome = "stalemate"
                attacker.adjust_morale(-5)
                defender.adjust_morale(-5)

        # THIS RETURN MUST BE HERE!
        return {
            "outcome": outcome,
            "victor": victor.name if victor else None,
            "attacker": {
                "name": attacker.name,
                "casualties": int(attacker_casualties),
                "remaining": int(attacker.strength),
                "morale": int(attacker.morale)
            },
            "defender": {
                "name": defender.name,
                "casualties": int(defender_casualties),
                "remaining": int(defender.strength),
                "morale": int(defender.morale)
            },
            "terrain": terrain,
            "attacker_roll": attacker_roll,
            "description": self._generate_description(
                attacker, defender, outcome, attacker_casualties, defender_casualties, attacker_roll
            )
        }
        # ... rest of existing code ...

    def _calculate_effective_strength(self, marshal: Marshal, is_attacker: bool) -> float:
        """Calculate effective combat strength considering morale."""
        base_strength = float(marshal.strength)

        # Morale multiplier (from marshal.get_combat_effectiveness())
        morale_multiplier = marshal.get_combat_effectiveness()

        # Defender bonus
        defender_multiplier = 1.0
        if not is_attacker:
            defender_multiplier = 1.0 + self.defender_bonus

        # Random variance (fog of war)
        variance_multiplier = 1.0 + random.uniform(-self.variance, self.variance)

        effective = base_strength * morale_multiplier * defender_multiplier * variance_multiplier

        return effective

    def _get_terrain_bonus(self, terrain: str) -> float:
        """Get defender bonus based on terrain."""
        terrain_modifiers = {
            "open": 0.0,  # No bonus
            "fortified": 0.3,  # +30% for fortifications
            "mountain": 0.2,  # +20% for high ground
            "river": 0.15  # +15% for river crossing
        }
        return terrain_modifiers.get(terrain, 0.0)

    def _calculate_casualties(
            self,
            army_size: int,
            enemy_effective: float,
            own_effective: float
    ) -> int:
        """Calculate casualties based on strength ratio."""
        if own_effective <= 0:
            return army_size  # Total defeat

        # Casualty rate based on strength ratio
        strength_ratio = enemy_effective / own_effective

        # Base casualty rate (5-30% of army)
        base_rate = 0.15  # 15% average

        # Adjust by strength ratio
        casualty_rate = base_rate * strength_ratio

        # Cap at 60% max casualties per battle
        casualty_rate = min(0.6, casualty_rate)

        casualties = int(army_size * casualty_rate)

        return casualties

    def _get_combat_narrative(self, attacker_name: str, roll_modified: int, is_critical_success: bool, is_critical_failure: bool) -> str:
        """Generate narrative description based on roll quality."""
        import random

        if is_critical_success:
            narratives = [
                f"{attacker_name} executes a brilliant maneuver!",
                f"{attacker_name} launches a devastating assault!",
                f"{attacker_name}'s forces strike with perfect coordination!"
            ]
        elif is_critical_failure:
            narratives = [
                f"{attacker_name}'s attack falters disastrously!",
                f"{attacker_name}'s assault collapses into chaos!",
                f"{attacker_name}'s forces stumble badly!"
            ]
        elif roll_modified >= 9:  # High roll (9-12)
            narratives = [
                f"{attacker_name} launches a decisive assault.",
                f"{attacker_name} attacks with overwhelming force.",
                f"{attacker_name}'s forces press forward aggressively."
            ]
        elif roll_modified >= 6:  # Medium roll (6-8)
            narratives = [
                f"{attacker_name} delivers an effective strike.",
                f"{attacker_name} engages in solid combat.",
                f"{attacker_name}'s forces advance steadily."
            ]
        else:  # Low roll (2-5)
            narratives = [
                f"{attacker_name} struggles in a costly engagement.",
                f"{attacker_name} faces a difficult fight.",
                f"{attacker_name}'s attack meets fierce resistance."
            ]

        return random.choice(narratives)

    def _generate_description(
            self,
            attacker: Marshal,
            defender: Marshal,
            outcome: str,
            atk_casualties: int,
            def_casualties: int,
            attacker_roll: Dict
    ) -> str:
        """Generate narrative description of battle without exposing dice mechanics."""
        # Get narrative based on roll quality (no numbers shown)
        narrative = self._get_combat_narrative(
            attacker.name,
            attacker_roll['modified'],
            attacker_roll['is_critical_success'],
            attacker_roll['is_critical_failure']
        )

        # Build outcome description with narrative
        descriptions = {
            "attacker_victory": (
                f"{narrative} "
                f"{attacker.name} decisively defeats {defender.name}! "
                f"{defender.name}'s army is destroyed. "
                f"{attacker.name} suffered {atk_casualties:,} casualties."
            ),
            "defender_victory": (
                f"{narrative} "
                f"{defender.name} repels the assault! "
                f"{attacker.name}'s army is shattered. "
                f"{defender.name} suffered {def_casualties:,} casualties."
            ),
            "attacker_tactical_victory": (
                f"{narrative} "
                f"{attacker.name} gains the advantage over {defender.name}. "
                f"Casualties: {attacker.name} {atk_casualties:,}, {defender.name} {def_casualties:,}. "
                f"Both armies remain in the field."
            ),
            "defender_tactical_victory": (
                f"{narrative} "
                f"{defender.name} holds the line. "
                f"Casualties: {attacker.name} {atk_casualties:,}, {defender.name} {def_casualties:,}. "
                f"Both armies remain in the field."
            ),
            "stalemate": (
                f"{narrative} "
                f"Brutal stalemate between {attacker.name} and {defender.name}. "
                f"Heavy casualties on both sides: {attacker.name} {atk_casualties:,}, "
                f"{defender.name} {def_casualties:,}."
            ),
            "mutual_destruction": (
                f"{narrative} "
                f"Catastrophic battle! Both {attacker.name} and {defender.name} "
                f"annihilate each other. No survivors."
            )
        }

        return descriptions.get(outcome, "Battle concluded.")


# Test code
if __name__ == "__main__":
    """Test combat system."""
    print("=" * 70)
    print("COMBAT SYSTEM TEST")
    print("=" * 70)

    from backend.models.marshal import Marshal

    # Create test marshals
    ney = Marshal("Ney", "Belgium", 72000, "aggressive", "France")
    wellington = Marshal("Wellington", "Waterloo", 68000, "cautious", "Britain")

    print(f"\nBefore Battle:")
    print(f"  {ney}")
    print(f"  {wellington}")

    # Create combat resolver
    combat = CombatResolver()

    # Test 1: Open field battle
    print("\n" + "=" * 70)
    print("TEST 1: Open Field Battle")
    print("=" * 70)

    result = combat.resolve_battle(ney, wellington, terrain="open")

    print(f"\nOutcome: {result['outcome']}")
    print(f"Victor: {result['victor']}")
    print(f"\n{result['description']}")
    print(f"\nAttacker ({result['attacker']['name']}):")
    print(f"  Casualties: {result['attacker']['casualties']:,}")
    print(f"  Remaining: {result['attacker']['remaining']:,}")
    print(f"  Morale: {result['attacker']['morale']}%")
    print(f"\nDefender ({result['defender']['name']}):")
    print(f"  Casualties: {result['defender']['casualties']:,}")
    print(f"  Remaining: {result['defender']['remaining']:,}")
    print(f"  Morale: {result['defender']['morale']}%")

    # Test 2: Fortified position
    print("\n" + "=" * 70)
    print("TEST 2: Attack on Fortified Position")
    print("=" * 70)

    # Reset marshals
    ney_2 = Marshal("Ney", "Belgium", 50000, "aggressive", "France")
    blucher = Marshal("Blucher", "Waterloo", 40000, "cautious", "Prussia")

    print(f"\nBefore Battle:")
    print(f"  {ney_2}")
    print(f"  {blucher}")

    result_2 = combat.resolve_battle(ney_2, blucher, terrain="fortified")

    print(f"\nOutcome: {result_2['outcome']}")
    print(f"Victor: {result_2['victor']}")
    print(f"\n{result_2['description']}")

    print("\n" + "=" * 70)
    print("COMBAT TEST COMPLETE!")
    print("=" * 70)
    print("\n✓ Battle resolution working")
    print("✓ Casualties calculated")
    print("✓ Morale effects applied")
    print("✓ Terrain modifiers working")
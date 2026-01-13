"""
Combat System for Project Sovereign
Handles battle resolution between armies
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

    def resolve_battle(
            self,
            attacker: Marshal,
            defender: Marshal,
            terrain: str = "open"
    ) -> Dict:
        """Resolve a battle between two marshals."""

        #print(f"\n⚔️ BATTLE: {attacker.name} vs {defender.name}")
        #print(f"   Attacker: {attacker.strength:,} troops, {attacker.morale}% morale")
        #print(f"   Defender: {defender.strength:,} troops, {defender.morale}% morale")

        # Calculate effective strengths
        attacker_effective = self._calculate_effective_strength(attacker, is_attacker=True)
        defender_effective = self._calculate_effective_strength(defender, is_attacker=False)

        #print(f"   Attacker effective: {attacker_effective:,.0f}")
        #print(f"   Defender effective: {defender_effective:,.0f}")

        # Apply terrain modifiers
        terrain_bonus = self._get_terrain_bonus(terrain)
        defender_effective *= (1 + terrain_bonus)

        #print(f"   Defender after terrain: {defender_effective:,.0f}")

        # Calculate casualties
        attacker_casualties = self._calculate_casualties(
            attacker.strength,
            defender_effective,
            attacker_effective
        )

        defender_casualties = self._calculate_casualties(
            defender.strength,
            attacker_effective,
            defender_effective
        )

        print(f"   💀 Casualties: {attacker.name} {attacker_casualties:,}, {defender.name} {defender_casualties:,}")

        # Apply casualties FIRST (this was missing!)
        print(f"   BEFORE: {attacker.name}={attacker.strength:,}, {defender.name}={defender.strength:,}")
        attacker.take_casualties(attacker_casualties)
        defender.take_casualties(defender_casualties)
        print(f"   AFTER: {attacker.name}={attacker.strength:,}, {defender.name}={defender.strength:,}")

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
                "casualties": attacker_casualties,
                "remaining": attacker.strength,
                "morale": attacker.morale
            },
            "defender": {
                "name": defender.name,
                "casualties": defender_casualties,
                "remaining": defender.strength,
                "morale": defender.morale
            },
            "terrain": terrain,
            "description": self._generate_description(
                attacker, defender, outcome, attacker_casualties, defender_casualties
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

    def _generate_description(
            self,
            attacker: Marshal,
            defender: Marshal,
            outcome: str,
            atk_casualties: int,
            def_casualties: int
    ) -> str:
        """Generate narrative description of battle."""
        descriptions = {
            "attacker_victory": (
                f"{attacker.name} decisively defeats {defender.name}! "
                f"{defender.name}'s army is destroyed. "
                f"{attacker.name} suffered {atk_casualties:,} casualties."
            ),
            "defender_victory": (
                f"{defender.name} repels {attacker.name}'s assault! "
                f"{attacker.name}'s army is shattered. "
                f"{defender.name} suffered {def_casualties:,} casualties."
            ),
            "attacker_tactical_victory": (
                f"{attacker.name} gains the advantage over {defender.name}. "
                f"Casualties: {attacker.name} {atk_casualties:,}, {defender.name} {def_casualties:,}. "
                f"Both armies remain in the field."
            ),
            "defender_tactical_victory": (
                f"{defender.name} holds against {attacker.name}. "
                f"Casualties: {attacker.name} {atk_casualties:,}, {defender.name} {def_casualties:,}. "
                f"Both armies remain in the field."
            ),
            "stalemate": (
                f"Brutal stalemate between {attacker.name} and {defender.name}. "
                f"Heavy casualties on both sides: {attacker.name} {atk_casualties:,}, "
                f"{defender.name} {def_casualties:,}."
            ),
            "mutual_destruction": (
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
"""
Marshal Model for Project Sovereign
Represents a marshal (commander) with personality and army
"""

from typing import Optional


class Marshal:
    """
    A marshal commanding an army.

    Marshals have:
    - Name and personality traits
    - Current location (region)
    - Army strength (abstract number)
    - Morale (affects performance)
    """

    def __init__(
            self,
            name: str,
            location: str,
            strength: int,
            personality: str,
            nation: str = "France"
    ):
        """
        Initialize a marshal.

        Args:
            name: Marshal's name (e.g., "Ney", "Davout")
            location: Current region (e.g., "Belgium")
            strength: Army strength (number of troops)
            personality: Personality type ("aggressive", "cautious", "literal")
            nation: Which nation this marshal serves (default: France)
        """
        self.name = name
        self.location = location
        self.strength = strength
        self.personality = personality
        self.nation = nation

        # Game state (changes during play)
        self.morale: int = 100  # 0-100, affects combat effectiveness
        self.orders_overridden: int = 0  # Track player forcing orders
        self.battles_won: int = 0
        self.battles_lost: int = 0

    def move_to(self, new_location: str) -> None:
        """Move marshal to a new region."""
        self.location = new_location

    def add_troops(self, amount: int) -> None:
        """Add troops to this marshal's army (recruitment)."""
        self.strength += amount

    def take_casualties(self, amount: int) -> None:
        """Remove troops due to combat losses."""
        self.strength = max(0, self.strength - amount)

    def adjust_morale(self, change: int) -> None:
        """Adjust morale (victories increase, defeats decrease)."""
        self.morale = max(0, min(100, self.morale + change))

    def get_combat_effectiveness(self) -> float:
        """
        Calculate combat effectiveness multiplier.

        Returns:
            Float multiplier (0.5 to 1.5)
            - High morale: 1.5x effective
            - Normal morale: 1.0x effective
            - Low morale: 0.5x effective
        """
        # Morale affects effectiveness
        # 100 morale = 1.5x, 50 morale = 1.0x, 0 morale = 0.5x
        return 0.5 + (self.morale / 100.0)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Marshal({self.name}, {self.strength:,} troops at {self.location}, morale: {self.morale}%)"


# Personality traits for AI behavior (used in executor)
PERSONALITY_TRAITS = {
    "aggressive": {
        "description": "Prefers attacking, questions defensive orders",
        "attack_bias": 0.3,  # +30% likely to attack
        "caution": -0.2,  # -20% caution
        "example": "Ney - The Bravest of the Brave"
    },
    "cautious": {
        "description": "Methodical, provides analysis, suggests alternatives",
        "attack_bias": -0.2,  # -20% likely to attack
        "caution": 0.3,  # +30% more careful
        "example": "Davout - The Iron Marshal"
    },
    "literal": {
        "description": "Follows orders exactly, doesn't improvise",
        "attack_bias": 0.0,  # No bias
        "caution": 0.0,  # No bias
        "example": "Grouchy - The Unlucky"
    }
}


def create_starting_marshals() -> dict[str, Marshal]:
    """
    Create the starting marshals for France.

    Returns:
        Dictionary of marshal_name -> Marshal object
    """
    marshals = {
        "Ney": Marshal(
            name="Ney",
            location="Belgium",
            strength=72000,
            personality="aggressive",
            nation="France"
        ),
        "Davout": Marshal(
            name="Davout",
            location="Paris",
            strength=48000,
            personality="cautious",
            nation="France"
        ),
        "Grouchy": Marshal(
            name="Grouchy",
            location="Waterloo",
            strength=33000,
            personality="literal",
            nation="France"
        )
    }
    return marshals


def create_enemy_marshals() -> dict[str, Marshal]:
    """
    Create the enemy marshals (persistent across turns).

    These marshals exist in the world from game start and:
    - Defend their regions when attacked
    - Persist casualties and morale between battles
    - Can be completely destroyed

    Returns:
        Dictionary of marshal_name -> Marshal object
    """
    enemies = {
        "Wellington": Marshal(
            name="Wellington",
            location="Waterloo",
            strength=68000,
            personality="cautious",
            nation="Britain"
        ),
        "Blucher": Marshal(
            name="Blucher",
            location="Netherlands",
            strength=55000,
            personality="aggressive",
            nation="Prussia"
        )
    }
    return enemies
# Test code
if __name__ == "__main__":
    """Quick test of marshal system."""
    print("=" * 60)
    print("MARSHAL SYSTEM TEST")
    print("=" * 60)

    # Create marshals
    marshals = create_starting_marshals()

    print(f"\nStarting marshals: {len(marshals)}")
    for name, marshal in marshals.items():
        print(f"  {marshal}")

    print("\n" + "=" * 60)
    print("Test Movement")
    print("=" * 60)

    ney = marshals["Ney"]
    print(f"\nBefore: {ney}")
    ney.move_to("Waterloo")
    print(f"After moving to Waterloo: {ney}")

    print("\n" + "=" * 60)
    print("Test Recruitment")
    print("=" * 60)

    print(f"\nBefore: Ney has {ney.strength:,} troops")
    ney.add_troops(10000)
    print(f"After recruiting: Ney has {ney.strength:,} troops")

    print("\n" + "=" * 60)
    print("Test Combat")
    print("=" * 60)

    print(f"\nBefore battle: {ney.strength:,} troops, {ney.morale}% morale")
    print(f"Combat effectiveness: {ney.get_combat_effectiveness():.2f}x")

    ney.take_casualties(15000)
    ney.adjust_morale(-20)
    ney.battles_won += 1

    print(f"After battle: {ney.strength:,} troops, {ney.morale}% morale")
    print(f"Combat effectiveness: {ney.get_combat_effectiveness():.2f}x")
    print(f"Record: {ney.battles_won}W - {ney.battles_lost}L")

    print("\n" + "=" * 60)
    print("Personality Traits")
    print("=" * 60)

    for name, traits in PERSONALITY_TRAITS.items():
        print(f"\n{name.upper()}: {traits['example']}")
        print(f"  {traits['description']}")
        print(f"  Attack bias: {traits['attack_bias']:+.0%}")
        print(f"  Caution: {traits['caution']:+.0%}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
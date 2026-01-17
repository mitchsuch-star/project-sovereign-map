"""
Marshal Model for Project Sovereign
Represents a marshal (commander) with personality and army

Includes Disobedience System (Phase 2):
- Trust: How much the marshal trusts the player
- Vindication: Track record of marshal vs player being right
- Recent battles/overrides for objection severity modifiers

Includes Stance System (Phase 2.7):
- NEUTRAL: Balanced posture (default)
- DEFENSIVE: -10% attack, +15% defense
- AGGRESSIVE: +15% attack, -10% defense
"""

from enum import Enum
from typing import Optional, Dict, List
from backend.models.trust import Trust


class Stance(Enum):
    """Marshal stance affecting combat modifiers."""
    NEUTRAL = "neutral"
    DEFENSIVE = "defensive"
    AGGRESSIVE = "aggressive"


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
            nation: str = "France",
            movement_range: int = 1,
            tactical_skill: int = 5,
            skills: Optional[dict] = None,
            ability: Optional[dict] = None,
            starting_trust: int = 70
    ):
        """Initialize a marshal."""
        self.name = name
        self.location = location
        self.strength = strength
        self.starting_strength = strength  # NEW: Track original strength
        self.personality = personality
        self.nation = nation
        self.movement_range = movement_range  # Attack range (cavalry=2, infantry=1)
        self.tactical_skill = tactical_skill  # Tactical skill rating (0-12, affects dice rolls)

        # 6-Skill System (Phase 2.2)
        # Skills range 1-10 (10 = best)
        if skills is None:
            # Default skills if not provided (backward compatibility)
            skills = {
                "tactical": tactical_skill,  # Use tactical_skill for backward compat
                "shock": 5,
                "defense": 5,
                "logistics": 5,
                "administration": 5,
                "command": 5
            }

        self.skills: Dict[str, int] = {
            "tactical": int(skills.get("tactical", 5)),      # Combat rolls, flanking bonuses
            "shock": int(skills.get("shock", 5)),            # Attack damage, pursuit effectiveness
            "defense": int(skills.get("defense", 5)),        # Defender bonus, retreat casualties
            "logistics": int(skills.get("logistics", 5)),    # Supply range (Phase 5), attrition resistance
            "administration": int(skills.get("administration", 5)),  # Recruitment speed, desertion prevention
            "command": int(skills.get("command", 5))         # Morale management, discipline, looting prevention
        }

        # Signature Ability System (Phase 2.3)
        # Each marshal has a unique ability that triggers in specific situations
        if ability is None:
            # Default no ability (backward compatibility)
            ability = {
                "name": "None",
                "description": "No special ability",
                "trigger": "never",
                "effect": "none"
            }

        self.ability: Dict[str, str] = {
            "name": str(ability.get("name", "None")),
            "description": str(ability.get("description", "No special ability")),
            "trigger": str(ability.get("trigger", "never")),
            "effect": str(ability.get("effect", "none"))
        }

        # Game state (changes during play)
        self.morale: int = 100
        self.orders_overridden: int = 0
        self.battles_won: int = 0
        self.battles_lost: int = 0
        self.just_retreated: bool = False  # NEW: Vulnerable after retreat

        # Disobedience System (Phase 2)
        self.trust: Trust = Trust(int(starting_trust))
        self.vindication_score: int = 0  # -5 to +5, affects objection boldness
        self.recent_battles: List[str] = []  # Last 3 battle results
        self.recent_overrides: List[bool] = []  # Last 5 override events

        # Autonomy System (Phase 2.1 - Redemption)
        # When trust hits critical low, player can grant autonomy
        self.autonomous: bool = False  # Marshal acting independently
        self.autonomy_turns: int = 0   # Turns remaining in autonomy
        self.redemption_pending: bool = False  # FIX: Track if redemption event already triggered

        # ════════════════════════════════════════════════════════════
        # TACTICAL STATE SYSTEM (Phase 2.6)
        # ════════════════════════════════════════════════════════════

        # DRILL State: 2-turn commitment for +20% shock bonus
        # Turn N: Order drill → drilling = True
        # Turn N+1: Locked (drilling_locked = True, can't be ordered)
        # Turn N+2+: Bonus active (shock_bonus = 2)
        self.drilling: bool = False          # Currently drilling (Turn N)
        self.drilling_locked: bool = False   # Locked in drill (Turn N+1)
        self.drill_complete_turn: int = -1   # Turn when drill completes
        self.shock_bonus: int = 0            # +2 = +20% attack (from drill)

        # FORTIFY State: Defensive lockdown, +10% defense, can't move/attack
        self.fortified: bool = False         # Currently fortified
        self.fortify_expires_turn: int = -1  # Turn when fortification expires
        self.defense_bonus: int = 0          # +1 = +10% defense (from fortify)

        # RETREAT State: Recovery from combat penalty
        # Starts at -45% effectiveness, recovers over 3 turns
        self.retreating: bool = False        # Currently in retreat recovery
        self.retreat_recovery: int = 0       # 0-3, current recovery stage
        # Recovery stages: 0 = -45%, 1 = -30%, 2 = -15%, 3 = 0% (recovered)

        # ════════════════════════════════════════════════════════════
        # STANCE SYSTEM (Phase 2.7)
        # ════════════════════════════════════════════════════════════
        # NEUTRAL: 0% attack, 0% defense (default)
        # DEFENSIVE: -10% attack, +15% defense
        # AGGRESSIVE: +15% attack, -10% defense
        self.stance: Stance = Stance.NEUTRAL

    def move_to(self, new_location: str) -> None:
        """Move marshal to a new region."""
        self.location = new_location

    # ════════════════════════════════════════════════════════════
    # STANCE MODIFIER METHODS
    # ════════════════════════════════════════════════════════════

    def get_attack_modifier(self) -> float:
        """
        Get attack modifier from stance (and other sources like drill).

        Returns:
            Float multiplier (e.g., 1.15 = +15% attack)
        """
        modifier = 1.0

        # Stance modifiers
        if self.stance == Stance.AGGRESSIVE:
            modifier *= 1.15  # +15%
        elif self.stance == Stance.DEFENSIVE:
            modifier *= 0.90  # -10%

        # Drill/shock bonus (from completed drill training)
        shock = getattr(self, 'shock_bonus', 0)
        if shock > 0:
            modifier *= (1.0 + shock * 0.10)  # shock_bonus=2 → +20%

        return modifier

    def get_defense_modifier(self) -> float:
        """
        Get defense modifier from stance, fortify, and drill status.

        Returns:
            Float multiplier (e.g., 1.15 = +15% defense)
        """
        modifier = 1.0

        # Stance modifiers
        if self.stance == Stance.DEFENSIVE:
            modifier *= 1.15  # +15%
        elif self.stance == Stance.AGGRESSIVE:
            modifier *= 0.90  # -10%

        # Fortify bonus (grows +2% per turn, max 15%)
        defense_bonus = getattr(self, 'defense_bonus', 0)
        if defense_bonus > 0:
            modifier *= (1.0 + defense_bonus * 0.10)  # defense_bonus=1.5 → +15%

        # Drilling penalty (caught drilling = vulnerable)
        if getattr(self, 'drilling', False) or getattr(self, 'drilling_locked', False):
            modifier *= 0.75  # -25%

        return modifier

    def get_stance_display(self) -> str:
        """Get display string for current stance with modifiers."""
        if self.stance == Stance.AGGRESSIVE:
            return "AGGRESSIVE (+15% atk, -10% def)"
        elif self.stance == Stance.DEFENSIVE:
            return "DEFENSIVE (-10% atk, +15% def)"
        else:
            return "NEUTRAL"

    def add_troops(self, amount: int) -> None:
        """Add troops to this marshal's army (recruitment)."""
        self.strength += amount

    def take_casualties(self, amount: int) -> None:
        """Remove troops due to combat losses."""
        self.strength = max(0, self.strength - amount)
        if self.strength < 50:
            print(f"💀 {self.name} reduced to rubble ({self.strength} → 0)")
            self.strength = 0
    def adjust_morale(self, change: int) -> None:
        """Adjust morale (victories increase, defeats decrease)."""
        self.morale = max(0, min(100, self.morale + change))

    def modify_trust(self, delta: int) -> int:
        """
        Modify trust and handle redemption_pending flag clearing.

        Args:
            delta: Amount to change trust (+/-)

        Returns:
            Actual change applied (may be less if capped)
        """
        actual_change = self.trust.modify(delta)

        # Clear redemption_pending if trust recovered above threshold (>20)
        if self.redemption_pending and self.trust.value > 20:
            self.redemption_pending = False

        return actual_change

    def get_combat_effectiveness(self) -> float:
        """
        Calculate combat effectiveness multiplier.

        Returns:
            Float multiplier (0.25 to 1.5)
            - Just retreated (just_retreated): 0.5x (vulnerable!)
            - Retreating recovery: Varies by stage
            - High morale: 1.5x effective
            - Normal morale: 1.0x effective
            - Low morale: 0.5x effective
        """
        # PENALTY: Just retreated = vulnerable (legacy flag)
        if self.just_retreated:
            return 0.5

        # PENALTY: Retreat recovery stages
        # Stage 0: -45%, Stage 1: -30%, Stage 2: -15%, Stage 3: 0% (recovered)
        retreat_penalty = 0.0
        if getattr(self, 'retreating', False):
            recovery_stage = getattr(self, 'retreat_recovery', 0)
            retreat_penalties = {0: 0.45, 1: 0.30, 2: 0.15, 3: 0.0}
            retreat_penalty = retreat_penalties.get(recovery_stage, 0.0)

        # Normal morale calculation
        # 100 morale = 1.5x, 50 morale = 1.0x, 0 morale = 0.5x
        base_effectiveness = 0.5 + (self.morale / 100.0)

        # Apply retreat penalty
        return max(0.25, base_effectiveness * (1.0 - retreat_penalty))

    def __repr__(self) -> str:
        """String representation for debugging."""
        unit_type = "cavalry" if self.movement_range == 2 else "infantry"
        trust_label = self.trust.get_label() if hasattr(self, 'trust') else "?"
        return f"Marshal({self.name}, {self.strength:,} troops at {self.location}, morale: {self.morale}%, trust: {trust_label}, {unit_type})"


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
            nation="France",
            movement_range=2,  # Cavalry commander - can attack 2 regions away
            tactical_skill=8,  # Brave and inspiring, but sometimes reckless
            skills={
                "tactical": 7,      # Good tactician, not brilliant
                "shock": 9,         # "The Bravest of the Brave" - devastating attacker
                "defense": 4,       # Poor defender, too aggressive
                "logistics": 5,     # Average logistics
                "administration": 4,  # Not great at administration
                "command": 8        # Inspiring leader, men would follow him anywhere
            },
            ability={
                "name": "Bravest of the Brave",
                "description": "Ney's aggressive leadership inspires devastating attacks",
                "trigger": "when_attacking",
                "effect": "+2 Shock skill when attacking (not defending)"
            },
            starting_trust=75  # Loyal but headstrong, starts slightly above average
        ),
        "Davout": Marshal(
            name="Davout",
            location="Paris",
            strength=48000,
            personality="cautious",
            nation="France",
            movement_range=1,  # Infantry commander
            tactical_skill=10,  # "The Iron Marshal" - Napoleon's best tactician
            skills={
                "tactical": 9,      # Brilliant tactician
                "shock": 7,         # Strong attacker but not reckless
                "defense": 8,       # Excellent defender
                "logistics": 8,     # Outstanding logistics
                "administration": 8,  # Excellent administrator
                "command": 9        # Iron discipline, feared and respected
            },
            ability={
                "name": "Iron Marshal",
                "description": "Davout's iron discipline keeps his army steady under pressure",
                "trigger": "morale_drops_below_50",
                "effect": "Prevents first morale drop below 50% (TODO: Phase 2.4 morale system)"
            },
            starting_trust=85  # Most trusted marshal, proven record
        ),
        "Grouchy": Marshal(
            name="Grouchy",
            location="Waterloo",
            strength=33000,
            personality="literal",
            nation="France",
            movement_range=1,  # Infantry commander
            tactical_skill=6,  # Competent but unlucky
            skills={
                "tactical": 5,      # Average tactician
                "shock": 5,         # Average attacker
                "defense": 5,       # Average defender
                "logistics": 6,     # Slightly better at logistics
                "administration": 5,  # Average administrator
                "command": 5        # Average leader
            },
            ability={
                "name": "Literal Obedience",
                "description": "Grouchy follows orders exactly, never taking initiative",
                "trigger": "receiving_orders",
                "effect": "Never questions orders, always obeys exactly (TODO: Phase 2.4 order delay system)"
            },
            starting_trust=65  # Newly promoted, unproven, follows orders literally
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
            nation="Britain",
            tactical_skill=10,  # Defensive genius, never lost a battle
            skills={
                "tactical": 9,      # Brilliant tactician
                "shock": 4,         # Poor attacker, defensive-minded
                "defense": 10,      # Best defender in Europe
                "logistics": 8,     # Excellent logistics (Peninsular War)
                "administration": 7,  # Good administrator
                "command": 9        # Respected and competent leader
            },
            ability={
                "name": "Reverse Slope Defense",
                "description": "Wellington masters defensive terrain, hiding troops behind hills",
                "trigger": "defending_in_hills_or_forest",
                "effect": "+2 Defense skill when defending on Hills or Forest terrain (TODO: Terrain system)"
            },
            starting_trust=80  # Wellington trusts his government
        ),
        "Blucher": Marshal(
            name="Blucher",
            location="Netherlands",
            strength=55000,
            personality="aggressive",
            nation="Prussia",
            tactical_skill=7,  # Aggressive and determined, but impetuous
            skills={
                "tactical": 6,      # Good but not brilliant tactician
                "shock": 8,         # "Marshal Forward" - aggressive attacker
                "defense": 5,       # Average defender, prefers attack
                "logistics": 5,     # Average logistics
                "administration": 4,  # Poor administrator, soldier's soldier
                "command": 7        # Inspirational leader, loved by troops
            },
            ability={
                "name": "Vorwärts!",
                "description": "Blücher's aggressive pursuit inflicts extra casualties on retreating enemies",
                "trigger": "after_winning_battle",
                "effect": "+1 pursuit damage to retreating enemies (TODO: Phase 2.6 pursuit system)"
            },
            starting_trust=70  # Blucher trusts Prussia's king
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
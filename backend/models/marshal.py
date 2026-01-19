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
            starting_trust: int = 70,
            cavalry: bool = False,
            spawn_location: str = None  # Capital/respawn location when broken
    ):
        """Initialize a marshal."""
        self.name = name
        self.location = location
        self.strength = strength
        self.starting_strength = strength  # NEW: Track original strength
        self.personality = personality
        self.nation = nation
        # Spawn location: where marshal respawns when army is broken
        # For France: Paris (capital)
        # For enemies: their starting region (TODO: use actual capitals in future)
        self.spawn_location = spawn_location if spawn_location else location
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

        # BROKEN State: Army shattered from surrounded forced retreat
        # When surrounded and forced to retreat, army is "broken":
        # - Teleports to capital with 3-10% of original strength
        # - Takes 4 turns to recover (longer than normal retreat)
        # - Can ONLY use recruit action during recovery
        self.broken: bool = False            # Army is broken (shattered)
        self.broken_recovery: int = 0        # 0-4, current recovery stage
        # Recovery stages: 0-3 = broken (recruit only), 4 = recovered

        # ════════════════════════════════════════════════════════════
        # STANCE SYSTEM (Phase 2.7)
        # ════════════════════════════════════════════════════════════
        # NEUTRAL: 0% attack, 0% defense (default)
        # DEFENSIVE: -10% attack, +15% defense
        # AGGRESSIVE: +15% attack, -10% defense
        self.stance: Stance = Stance.NEUTRAL

        # ════════════════════════════════════════════════════════════
        # PERSONALITY ABILITY STATE (Phase 2.8)
        # ════════════════════════════════════════════════════════════
        # Unit type tag for cavalry-specific abilities
        self.cavalry: bool = cavalry  # True for cavalry commanders (Ney), False for infantry

        # CAVALRY DEFENSIVE LIMITS - Horses can't hold defensive positions
        # After 3 turns in defensive stance → auto-switch to aggressive (-3 trust)
        # After 3 turns fortified → auto-unfortify (-3 trust)
        # Tracked separately so both can trigger (-6 total if both)
        self.turns_in_defensive_stance: int = 0  # Resets when leaving defensive stance
        self.turns_fortified: int = 0            # Resets when unfortifying
        self.turns_defensive: int = 0            # Legacy - kept for compatibility

        # DAVOUT (Cautious) - Counter-Punch tracking
        # Set True after successfully defending against attack
        # Clears at turn END if not used, or after first attack
        self.counter_punch_available: bool = False

        # GROUCHY (Literal) - Immovable tracking
        # Set True when given hold/defend order
        # Provides +15% defense while holding position
        # Breaks (resets to False) if Grouchy moves or attacks
        self.holding_position: bool = False
        self.hold_region: str = ""  # Region where Grouchy is holding

    def move_to(self, new_location: str) -> None:
        """
        Move marshal to a new region.

        Also handles ability state resets:
        - Cavalry: Resets defensive tracking (moving breaks defensive posture)
        - Grouchy: Clears holding_position (moving breaks Immovable)
        """
        old_location = self.location
        self.location = new_location

        # Only reset if actually moving to a different region
        if old_location != new_location:
            # CAVALRY: Moving resets defensive counters
            if getattr(self, 'cavalry', False):
                self.turns_in_defensive_stance = 0
                self.turns_fortified = 0
            self.turns_defensive = 0  # Legacy compatibility

            # GROUCHY: Moving breaks Immovable
            if self.holding_position:
                self.holding_position = False
                self.hold_region = ""

    # ════════════════════════════════════════════════════════════
    # STANCE MODIFIER METHODS
    # ════════════════════════════════════════════════════════════

    def get_attack_modifier(self, strength_ratio: float = None) -> float:
        """
        Get attack modifier from stance, personality, and other sources.

        Args:
            strength_ratio: Our strength / enemy strength (for bad odds check)

        Returns:
            Float multiplier (e.g., 1.15 = +15% attack)
        """
        from backend.models.personality_modifiers import get_attack_modifier_for_personality

        modifier = 1.0

        # Stance modifiers (base)
        if self.stance == Stance.AGGRESSIVE:
            modifier *= 1.15  # +15%
        elif self.stance == Stance.DEFENSIVE:
            modifier *= 0.90  # -10%

        # Drill/shock bonus (from completed drill training)
        shock = getattr(self, 'shock_bonus', 0)
        has_drill_bonus = shock > 0
        if has_drill_bonus:
            modifier *= (1.0 + shock * 0.10)  # shock_bonus=2 → +20%

        # Personality-specific attack modifiers
        personality_mod = get_attack_modifier_for_personality(
            self.personality,
            self.stance.value,
            has_drill_bonus,
            strength_ratio
        )
        modifier *= personality_mod

        return modifier

    def get_defense_modifier(self, is_outnumbered: bool = False) -> float:
        """
        Get defense modifier from stance, personality, fortify, and drill status.

        Args:
            is_outnumbered: Whether marshal is outnumbered (for Davout bonus)

        Returns:
            Float multiplier (e.g., 1.15 = +15% defense)
        """
        from backend.models.personality_modifiers import get_defense_modifier_for_personality

        modifier = 1.0

        # Stance modifiers (base)
        if self.stance == Stance.DEFENSIVE:
            modifier *= 1.15  # +15%
        elif self.stance == Stance.AGGRESSIVE:
            modifier *= 0.90  # -10%

        # Fortify bonus (grows per turn, max varies by personality)
        # defense_bonus is stored as decimal (0.16 = 16%), applied directly as multiplier
        fortify_bonus = getattr(self, 'defense_bonus', 0)
        if fortify_bonus > 0:
            modifier *= (1.0 + fortify_bonus)  # 0.16 → 1.16x (16% reduction)

        # Drilling penalty (caught drilling = vulnerable)
        if getattr(self, 'drilling', False) or getattr(self, 'drilling_locked', False):
            modifier *= 0.75  # -25%

        # Personality-specific defense modifiers
        is_holding = getattr(self, 'holding_position', False)
        personality_mod = get_defense_modifier_for_personality(
            self.personality,
            self.stance.value,
            is_outnumbered,
            is_holding
        )
        modifier *= personality_mod

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
        unit_type = "cavalry" if getattr(self, 'cavalry', False) else "infantry"
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
            starting_trust=75,  # Loyal but headstrong, starts slightly above average
            cavalry=True,  # Cavalry commander - enables Fighting Retreat and 2-tile attacks
            spawn_location="Paris"  # French capital - respawn location when broken
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
            starting_trust=85,  # Most trusted marshal, proven record
            spawn_location="Paris"  # French capital - respawn location when broken
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
            starting_trust=65,  # Newly promoted, unproven, follows orders literally
            spawn_location="Paris"  # French capital - respawn location when broken
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
    # NOTE: Enemy spawn_location is currently their starting region.
    # TODO: In future, enemies should spawn at their nation's capital:
    # - Wellington → London (Britain capital)
    # - Blucher → Berlin (Prussia capital)
    # For now, they respawn at their starting positions.
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
            starting_trust=80,  # Wellington trusts his government
            spawn_location="Waterloo"  # TODO: Change to London (Britain capital) when map expanded
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
            starting_trust=70,  # Blucher trusts Prussia's king
            spawn_location="Netherlands"  # TODO: Change to Berlin (Prussia capital) when map expanded
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
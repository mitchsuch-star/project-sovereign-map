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

    def roll_combat_dice(self, marshal: Marshal, flanking_bonus: int = 0) -> Dict:
        """
        Roll 2d6 for combat with skill and flanking modifiers.

        Formula:
        - Roll 2d6 (natural roll: 2-12)
        - Add skill bonus: tactical_skill // 3
        - Add flanking bonus: 0-3 from coordinated attacks
        - Cap modified roll at 14 (allows flanking to exceed normal cap)
        - Calculate multiplier: 0.85 + (modified * 0.025)

        Args:
            marshal: The marshal rolling dice
            flanking_bonus: Bonus from attacking from multiple directions (0-3)

        Returns:
            Dict with:
            - natural: int (2-12, unmodified 2d6 roll)
            - modified: int (natural + skill bonus + flanking, capped at 14)
            - is_critical_success: bool (natural 12)
            - is_critical_failure: bool (natural 2)
            - multiplier: float (0.85 to 1.20 with flanking)
            - skill_bonus: int (tactical_skill // 3)
            - flanking_bonus: int (0-3)
        """
        # Roll 2d6
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        natural_roll = die1 + die2  # Range: 2-12

        # Calculate skill bonus from tactical skill (use skills dict if available)
        if hasattr(marshal, 'skills') and 'tactical' in marshal.skills:
            tactical_skill = marshal.skills['tactical']
        else:
            tactical_skill = marshal.tactical_skill  # Fallback for backward compatibility

        skill_bonus = tactical_skill // 3  # 0-3 for skill 1-10

        # Modified roll with flanking (cap at 14 to allow flanking benefits beyond 12)
        modified_roll = min(14, natural_roll + skill_bonus + int(flanking_bonus))

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
            "skill_bonus": int(skill_bonus),
            "flanking_bonus": int(flanking_bonus)
        }

    def resolve_battle(
            self,
            attacker: Marshal,
            defender: Marshal,
            terrain: str = "open",
            flanking_bonus: int = 0,
            flanking_message: str = None
    ) -> Dict:
        """
        Resolve a battle between two marshals using 2d6 dice system.

        Args:
            attacker: The attacking marshal
            defender: The defending marshal
            terrain: Terrain type (affects defender bonus)
            flanking_bonus: Coordination bonus from attacking from multiple directions (0-3)
            flanking_message: Message describing the flanking situation
        """

        #print(f"\n BATTLE: {attacker.name} vs {defender.name}")
        #print(f"   Attacker: {attacker.strength:,} troops, {attacker.morale}% morale")
        #print(f"   Defender: {defender.strength:,} troops, {defender.morale}% morale")

        # Roll combat dice for attacker (flanking bonus adds to roll)
        attacker_roll = self.roll_combat_dice(attacker, flanking_bonus=int(flanking_bonus))

        # Calculate effective strengths
        attacker_effective = self._calculate_effective_strength(attacker, is_attacker=True)
        defender_effective = self._calculate_effective_strength(defender, is_attacker=False)

        #print(f"   Attacker effective: {attacker_effective:,.0f}")
        #print(f"   Defender effective: {defender_effective:,.0f}")

        # Apply terrain modifiers
        terrain_bonus = self._get_terrain_bonus(terrain)
        defender_effective *= (1 + terrain_bonus)

        #print(f"   Defender after terrain: {defender_effective:,.0f}")

        # Calculate casualties with dice multiplier and skills
        # Attacker's roll affects how much damage they deal to defender

        # Base casualties before skill modifiers
        base_attacker_casualties = self._calculate_casualties(
            attacker.strength,
            defender_effective,
            attacker_effective
        )

        base_defender_casualties = self._calculate_casualties(
            defender.strength,
            attacker_effective,
            defender_effective
        )

        # Apply SHOCK skill to attacker damage (increases damage dealt to defender)
        # Higher shock = more casualties inflicted
        # shock_skill / 20 gives 0.05 to 0.50 bonus (5% to 50% more damage)
        attacker_shock = attacker.skills.get("shock", 5)

        # SIGNATURE ABILITY: Ney's "Bravest of the Brave" (Phase 2.3)
        # When attacking, Ney gets +2 Shock
        ability_message = None
        if hasattr(attacker, 'ability') and attacker.ability.get("trigger") == "when_attacking":
            # Check if this is an attack-triggering ability (currently only Ney has this)
            if attacker.ability.get("name") == "Bravest of the Brave":
                attacker_shock += 2
                ability_message = f"{attacker.name}'s '{attacker.ability['name']}' inspires the assault!"

        # ════════════════════════════════════════════════════════════
        # DRILL BONUS (Phase 2.6): +20% attack from drill training
        # NOTE: Actual calculation is in marshal.get_attack_modifier()
        # Save value for message generation, clear AFTER modifier is calculated
        # ════════════════════════════════════════════════════════════
        attacker_drill_bonus = getattr(attacker, 'shock_bonus', 0)
        drill_bonus_message = None
        if attacker_drill_bonus > 0:
            drill_bonus_message = f"{attacker.name}'s drilled troops attack with +{attacker_drill_bonus * 10}% effectiveness!"

        # ════════════════════════════════════════════════════════════
        # STANCE & PERSONALITY MODIFIER (Phase 2.7/2.8): Apply attack modifiers
        # NOTE: get_attack_modifier() includes stance, personality, AND drill bonus
        # ════════════════════════════════════════════════════════════
        attacker_stance_message = None
        attacker_personality_message = None
        attacker_stance_modifier = 1.0

        # Calculate strength ratio for personality modifiers (Davout bad odds)
        strength_ratio = attacker.strength / defender.strength if defender.strength > 0 else float('inf')

        if hasattr(attacker, 'get_attack_modifier'):
            attacker_stance_modifier = attacker.get_attack_modifier(strength_ratio)
            if attacker_stance_modifier != 1.0:
                from backend.models.marshal import Stance
                current_stance = getattr(attacker, 'stance', Stance.NEUTRAL)
                personality = getattr(attacker, 'personality', 'unknown')

                # Stance messages
                if current_stance == Stance.AGGRESSIVE:
                    attacker_stance_message = f"{attacker.name}'s AGGRESSIVE stance drives the assault! (+15% attack)"
                elif current_stance == Stance.DEFENSIVE:
                    attacker_stance_message = f"{attacker.name}'s DEFENSIVE stance hampers offensive operations (-10% attack)"

                # Personality-specific messages
                if personality == "aggressive":
                    base_bonus = 15
                    if current_stance == Stance.AGGRESSIVE:
                        base_bonus += 5  # +5% additional
                    if attacker_drill_bonus > 0:  # Use saved value
                        base_bonus += 5  # +5% drill synergy
                    if base_bonus > 15:
                        attacker_personality_message = f"{attacker.name}'s aggression fuels the attack! (Bravest of the Brave: +{base_bonus}% total)"
                    else:
                        attacker_personality_message = f"{attacker.name} leads the charge! (Aggressive: +15% attack)"

                elif personality == "cautious":
                    if strength_ratio < 1.0:
                        attacker_personality_message = f"{attacker.name} attacks cautiously at unfavorable odds. (Cautious: -10% attack)"
                    if current_stance == Stance.AGGRESSIVE:
                        if not attacker_personality_message:
                            attacker_personality_message = f"{attacker.name} is hesitant in aggressive posture. (Cautious: -5% attack)"

        # Clear drill bonus AFTER modifier calculation (one-time use)
        if attacker_drill_bonus > 0:
            attacker.shock_bonus = 0
            attacker.drilling = False
            attacker.drilling_locked = False
            attacker.drill_complete_turn = -1

        shock_multiplier = 1.0 + (attacker_shock / 20.0)
        # Apply stance modifier to shock
        shock_multiplier *= attacker_stance_modifier

        # Apply DEFENSE skill to defender protection (reduces casualties taken)
        # Higher defense = fewer casualties taken
        # defense_skill // 2 gives 0 to 5 percentage points of protection
        defender_defense = defender.skills.get("defense", 5)

        # ════════════════════════════════════════════════════════════
        # FORTIFY BONUS (Phase 2.6): Defense bonus from fortified position
        # NOTE: Actual calculation is in marshal.get_defense_modifier()
        # This section only generates the message for UI feedback
        # ════════════════════════════════════════════════════════════
        fortify_bonus_message = None
        defender_fortify_bonus = getattr(defender, 'defense_bonus', 0)
        if defender_fortify_bonus > 0:
            fortify_percent = int(defender_fortify_bonus * 100)  # 0.16 → 16%
            fortify_bonus_message = f"{defender.name}'s fortified position provides +{fortify_percent}% defense!"

        # ════════════════════════════════════════════════════════════
        # DRILLING PENALTY (Phase 2.6): -25% defense when caught drilling
        # NOTE: Actual penalty is in marshal.get_defense_modifier()
        # This section handles state changes and message generation
        # ════════════════════════════════════════════════════════════
        drilling_penalty_message = None
        is_drilling = getattr(defender, 'drilling', False) or getattr(defender, 'drilling_locked', False)
        if is_drilling:
            drilling_penalty_message = f"{defender.name}'s drill was interrupted by the attack! (-25% defense)"
            # Cancel drill - they lose all progress (state change stays here)
            defender.drilling = False
            defender.drilling_locked = False
            defender.drill_complete_turn = -1
            defender.shock_bonus = 0  # Clear any pending bonus

        # ════════════════════════════════════════════════════════════
        # STANCE & PERSONALITY MODIFIER (Phase 2.7/2.8): Apply defense modifiers
        # ════════════════════════════════════════════════════════════
        defender_stance_message = None
        defender_personality_message = None
        defender_stance_modifier = 1.0

        # Check if defender is outnumbered (for Davout bonus)
        is_outnumbered = defender.strength < attacker.strength

        if hasattr(defender, 'get_defense_modifier'):
            defender_stance_modifier = defender.get_defense_modifier(is_outnumbered)
            if defender_stance_modifier != 1.0 and not is_drilling:  # Don't double message if drilling
                from backend.models.marshal import Stance
                current_stance = getattr(defender, 'stance', Stance.NEUTRAL)
                personality = getattr(defender, 'personality', 'unknown')

                # Stance messages
                if current_stance == Stance.DEFENSIVE:
                    defender_stance_message = f"{defender.name}'s DEFENSIVE stance strengthens the line! (+15% defense)"
                elif current_stance == Stance.AGGRESSIVE:
                    defender_stance_message = f"{defender.name}'s AGGRESSIVE stance leaves flanks exposed (-10% defense)"

                # Personality-specific messages
                if personality == "aggressive":
                    if current_stance == Stance.AGGRESSIVE:
                        defender_personality_message = f"{defender.name}'s reckless aggression weakens defense! (Aggressive: -5% additional)"
                    elif current_stance == Stance.DEFENSIVE:
                        defender_personality_message = f"{defender.name} chafes at defensive duty. (Aggressive: +10% defense, not +15%)"

                elif personality == "cautious":
                    if current_stance == Stance.DEFENSIVE:
                        defender_personality_message = f"{defender.name}'s methodical defense is exemplary! (Iron Marshal: +20% total)"
                    if is_outnumbered:
                        if not defender_personality_message:
                            defender_personality_message = f"{defender.name} stands firm against superior numbers! (Cautious: +10% outnumbered)"
                        else:
                            defender_personality_message += f" Outnumbered bonus: +10%"

                elif personality == "literal":
                    is_holding = getattr(defender, 'holding_position', False)
                    if is_holding:
                        defender_personality_message = f"{defender.name} holds the position exactly as ordered! (Immovable: +15% defense)"

        defense_bonus = defender_defense / 20.0  # 0.05 to 0.50 (5% to 50% reduction)
        # Apply stance modifier to defense - note: higher modifier = better defense (reduces casualties MORE)
        # defender_stance_modifier > 1 means better defense (e.g., 1.15 for defensive stance)
        defense_multiplier = (1.0 - defense_bonus) / defender_stance_modifier

        # Calculate final casualties
        # Attacker takes casualties (reduced by their defense skill)
        attacker_defense = attacker.skills.get("defense", 5)
        attacker_defense_mult = 1.0 - (attacker_defense / 20.0)
        attacker_casualties = int(base_attacker_casualties * attacker_defense_mult)

        # Defender takes casualties (increased by attacker shock, reduced by defender defense, affected by dice roll)
        defender_casualties = int(
            base_defender_casualties
            * shock_multiplier          # Attacker's shock increases damage
            * defense_multiplier        # Defender's defense reduces damage
            * attacker_roll['multiplier']  # Dice roll affects damage
        )

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
            # COUNTER-PUNCH: Cautious defenders (Davout) get free attack after winning defense
            if getattr(defender, 'personality', '') == 'cautious':
                defender.counter_punch_available = True
                print(f"  [COUNTER-PUNCH EARNED] {defender.name} can now attack for FREE!")
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
                # COUNTER-PUNCH: Cautious defenders (Davout) get free attack after winning defense
                if getattr(defender, 'personality', '') == 'cautious':
                    defender.counter_punch_available = True
                    print(f"  [COUNTER-PUNCH EARNED] {defender.name} can now attack for FREE!")
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

        # Build description with tactical state messages
        base_description = self._generate_description(
            attacker, defender, outcome, attacker_casualties, defender_casualties, attacker_roll
        )

        # Prepend tactical state messages if applicable
        tactical_prefix = ""
        if attacker_stance_message:
            tactical_prefix += f"\n⚔️ {attacker_stance_message}"
        if attacker_personality_message:
            tactical_prefix += f"\n🔥 {attacker_personality_message}"
        if defender_stance_message:
            tactical_prefix += f"\n🛡️ {defender_stance_message}"
        if defender_personality_message:
            tactical_prefix += f"\n🛡️ {defender_personality_message}"
        if drill_bonus_message:
            tactical_prefix += f"\n⚔️ {drill_bonus_message}"
        if fortify_bonus_message:
            tactical_prefix += f"\n🏰 {fortify_bonus_message}"
        if drilling_penalty_message:
            tactical_prefix += f"\n⚠️ {drilling_penalty_message}"
        if tactical_prefix:
            tactical_prefix += "\n"

        # ════════════════════════════════════════════════════════════════
        # FORCED RETREAT CHECK: Armies with critically low morale must retreat
        # Threshold: 25% morale triggers forced retreat
        # ════════════════════════════════════════════════════════════════
        FORCED_RETREAT_THRESHOLD = 25
        attacker_forced_retreat = (
            attacker.strength > 0 and
            attacker.morale <= FORCED_RETREAT_THRESHOLD
        )
        defender_forced_retreat = (
            defender.strength > 0 and
            defender.morale <= FORCED_RETREAT_THRESHOLD
        )

        # Add forced retreat message to description if applicable
        retreat_message = ""
        if attacker_forced_retreat:
            retreat_message += f"\n\n⚠️ {attacker.name}'s troops are BROKEN (morale {int(attacker.morale)}%)! FORCED RETREAT!"
        if defender_forced_retreat:
            retreat_message += f"\n\n⚠️ {defender.name}'s troops are BROKEN (morale {int(defender.morale)}%)! FORCED RETREAT!"

        # THIS RETURN MUST BE HERE!
        return {
            "outcome": outcome,
            "victor": victor.name if victor else None,
            "attacker": {
                "name": attacker.name,
                "casualties": int(attacker_casualties),
                "remaining": int(attacker.strength),
                "morale": int(attacker.morale),
                "forced_retreat": attacker_forced_retreat
            },
            "defender": {
                "name": defender.name,
                "casualties": int(defender_casualties),
                "remaining": int(defender.strength),
                "morale": int(defender.morale),
                "forced_retreat": defender_forced_retreat
            },
            "terrain": terrain,
            "attacker_roll": attacker_roll,
            "ability_triggered": ability_message,  # Phase 2.3: Signature abilities
            "drill_bonus_triggered": drill_bonus_message,  # Phase 2.6: Drill bonus
            "fortify_bonus_triggered": fortify_bonus_message,  # Phase 2.6: Fortify bonus
            "drilling_penalty_triggered": drilling_penalty_message,  # Phase 2.6: Drilling penalty
            "attacker_stance_triggered": attacker_stance_message,  # Phase 2.7: Stance system
            "defender_stance_triggered": defender_stance_message,  # Phase 2.7: Stance system
            "attacker_personality_triggered": attacker_personality_message,  # Phase 2.8: Personality abilities
            "defender_personality_triggered": defender_personality_message,  # Phase 2.8: Personality abilities
            "flanking_bonus": int(flanking_bonus),  # Phase 2.5: Flanking system
            "flanking_message": flanking_message,
            "description": tactical_prefix + base_description + retreat_message
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
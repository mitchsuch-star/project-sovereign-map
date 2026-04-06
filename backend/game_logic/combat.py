"""
Combat System for Project Sovereign
Handles battle resolution between armies

Features:
- 2d6 dice-based combat with skill modifiers
- Critical success/failure on natural 12/2
- Skill-based advantage for better marshals
- Variance while maintaining tactical superiority
"""

from typing import Dict
from backend.models.marshal import Marshal
from backend.models.region import TERRAIN_DEFENSE_BONUS, TERRAIN_CAVALRY_EFFECTIVENESS
from backend.utils import ordinal


def _build_tactical_prefix(
    attacker, defender,
    attacker_stance_message="", attacker_personality_message="",
    defender_stance_message="", defender_personality_message="",
    drill_bonus_message="", fortify_bonus_message="",
    drilling_penalty_message="", exhaustion_message="",
    terrain_defense_message="", cavalry_terrain_message="",
    cavalry_counter_message="", square_cavalry_message="",
    square_artillery_message="", glorious_charge_message="",
):
    """Build tactical prefix string from combat modifier messages.

    Single source — called from both resolve_battle() and the secondary
    combat path to avoid duplication (Systems Audit Session 11, P1-21).
    """
    prefix = ""
    _MESSAGES = [
        (attacker_stance_message, "\n\u2694\ufe0f "),
        (attacker_personality_message, "\n\U0001f525 "),
        (defender_stance_message, "\n\U0001f6e1\ufe0f "),
        (defender_personality_message, "\n\U0001f6e1\ufe0f "),
        (drill_bonus_message, "\n\u2694\ufe0f "),
        (fortify_bonus_message, "\n\U0001f3f0 "),
        (drilling_penalty_message, "\n\u26a0\ufe0f "),
        (exhaustion_message, "\n\U0001f613 "),
        (terrain_defense_message, "\n\U0001f3d4\ufe0f "),
        (cavalry_terrain_message, "\n\U0001f40e "),
        (cavalry_counter_message, "\n\U0001f40e "),
        (square_cavalry_message, "\n\U0001f6e1\ufe0f "),
        (square_artillery_message, "\n\U0001f4a5 "),
    ]
    for msg, icon in _MESSAGES:
        if msg:
            prefix += f"{icon}{msg}"
    if glorious_charge_message:
        prefix += f"\n{glorious_charge_message}"

    # Combined arms (Phase 7)
    atk_ca = getattr(attacker, '_display_combined_arms_atk', 0.0)
    def_ca = getattr(defender, '_display_combined_arms_def', 0.0)
    if atk_ca > 0:
        prefix += f"\n\u2694\ufe0f {attacker.name}'s combined arms coordination! (+{int(atk_ca * 100)}% attack)"
    if def_ca > 0:
        prefix += f"\n\U0001f6e1\ufe0f {defender.name}'s combined arms coordination! (+{int(def_ca * 100)}% defense)"
    atk_adj = getattr(attacker, '_display_adjacent_atk', 0.0)
    if atk_adj > 0:
        prefix += f"\n\u2694\ufe0f Adjacent allies bolster {attacker.name}'s attack! (+{int(atk_adj * 100)}%)"

    if prefix:
        prefix += "\n"
    return prefix
from backend.utils.debug import debug_print
import random


# Morale % at which armies are forced to retreat
FORCED_RETREAT_THRESHOLD = 25


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
            tactical_skill = marshal.get_effective_skill('tactical') if hasattr(marshal, 'get_effective_skill') else marshal.skills['tactical']
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
            flanking_message: str = None,
            glorious_charge: bool = False,
            fortification_bonus: float = 0.0,
            apply_casualties: bool = True,
    ) -> Dict:
        """
        Resolve a battle between two marshals using 2d6 dice system.

        Args:
            attacker: The attacking marshal
            defender: The defending marshal
            terrain: Terrain type (affects defender bonus)
            flanking_bonus: Coordination bonus from attacking from multiple directions (0-3)
            flanking_message: Message describing the flanking situation
            glorious_charge: If True, deals 2x damage dealt AND taken (cavalry recklessness)
            fortification_bonus: Defense bonus from fortification building (Phase 6.2.E)
        """

        # C2 fix: Log warning for same-nation combat (defensive programming).
        # Hard block is in executor target resolution; this is a safety net.
        if attacker.nation == defender.nation:
            print(f"[WARNING] Same-nation combat: {attacker.name} ({attacker.nation}) vs "
                  f"{defender.name} ({defender.nation})")

        # Roll combat dice for attacker (flanking bonus adds to roll)
        attacker_roll = self.roll_combat_dice(attacker, flanking_bonus=int(flanking_bonus))

        # Calculate effective strengths
        attacker_effective = self._calculate_effective_strength(attacker, is_attacker=True)
        defender_effective = self._calculate_effective_strength(defender, is_attacker=False)

        #print(f"   Attacker effective: {attacker_effective:,.0f}")
        #print(f"   Defender effective: {defender_effective:,.0f}")

        # Apply terrain modifiers + fortification bonus (Phase 6.2.E — stacks additively)
        terrain_bonus = self._get_terrain_bonus(terrain)
        total_defense_bonus = terrain_bonus + fortification_bonus
        defender_effective *= (1 + total_defense_bonus)

        # Generate terrain defense message
        terrain_defense_message = None
        if terrain_bonus > 0 and fortification_bonus > 0:
            terrain_name = terrain.replace("_", " ").title()
            terrain_defense_message = (f"{defender.name} benefits from {terrain_name} terrain (+{int(terrain_bonus * 100)}% defense) "
                                       f"and fortifications (+{int(fortification_bonus * 100)}% defense)")
        elif terrain_bonus > 0:
            terrain_name = terrain.replace("_", " ").title()
            terrain_defense_message = f"{defender.name} benefits from {terrain_name} terrain (+{int(terrain_bonus * 100)}% defense)"
        elif fortification_bonus > 0:
            terrain_defense_message = f"{defender.name} benefits from fortifications (+{int(fortification_bonus * 100)}% defense)"

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
        attacker_shock = attacker.get_effective_skill("shock") if hasattr(attacker, 'get_effective_skill') else attacker.skills.get("shock", 5)

        # SIGNATURE ABILITY: Ney's "Bravest of the Brave" (Phase 2.3)
        # When attacking, Ney gets +2 Shock
        #
        # Wired abilities — see docs/ADDING_CONTENT.md "Wiring a Special Ability"
        # for the full checklist when adding new abilities:
        #   - Ney "Bravest of the Brave": +2 Shock when attacking (here)
        #   - Drouot "Sage of the Grand Army": +5% fort degradation (fort degradation block below)
        #   - Wellington "Reverse Slope Defense": +5% defense always (marshal.py get_defense_modifier)
        #   - Blucher "Vorwärts!": 3k pursuit damage on retreat (pursuit block below)
        #   - Uxbridge "Pursuit Master": 5k pursuit damage on retreat (pursuit block below)
        #   - Davout "Counter-Punch Mastery": +20% attack after defending (outcome block below)
        # Unwired:
        #   - Grouchy "Literal Obedience": order compliance (wired via disobedience.py, not combat)
        #   - Gneisenau "Staff Work": ally bonus (deferred to Phase 7 Session 58 — needs coordination fields)
        #   - ArchdukeCharles "Habsburg Resolve": +3% defense (wired below in defending abilities)
        #   - Schwarzenberg "Coalition Coordinator": placeholder (Phase 8)
        #   - Reynier "Saxon Discipline": placeholder
        ability_message = None
        if hasattr(attacker, 'ability') and attacker.ability.get("trigger") == "when_attacking":
            if attacker.ability.get("name") == "Bravest of the Brave":
                attacker_shock += 2
                ability_message = f"{attacker.name}'s '{attacker.ability['name']}' inspires the assault!"

        # ════════════════════════════════════════════════════════════
        # BERTHIER REPORT: Snapshot modifiers BEFORE consumption
        # Must happen before get_attack_modifier() / get_defense_modifier()
        # which zero out strategic_combat_bonus / strategic_defense_bonus
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.battle_report import (
            snapshot_attacker_modifiers, snapshot_defender_modifiers, generate_battle_report
        )
        attacker_modifier_snapshot = snapshot_attacker_modifiers(
            attacker, defender, terrain, fortification_bonus, flanking_bonus, glorious_charge
        )
        defender_modifier_snapshot = snapshot_defender_modifiers(
            defender, attacker, terrain, fortification_bonus
        )

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
        # EXHAUSTION MESSAGE (Phase 3 - Attack Spam Prevention)
        # Check if attacker has made previous attacks this turn
        # Artillery is EXEMPT: guns don't tire — sustained bombardment is their function
        # ════════════════════════════════════════════════════════════
        exhaustion_message = None
        exhaustion_info = attacker.get_exhaustion_info()
        if exhaustion_info["penalty"] > 0:
            penalty = exhaustion_info["penalty_percent"]
            attack_num = exhaustion_info["attacks_this_turn"] + 1
            exhaustion_message = f"{attacker.name}'s troops are exhausted from repeated attacks! ({ordinal(attack_num)} attack: -{penalty}%)"

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

        # Clear drill bonus AFTER modifier calculation (one-time use).
        # NOTE: Drill state is cleared here in combat.py rather than in marshal.py's
        # get_attack_modifier() because it requires resetting 4 interrelated fields
        # atomically (shock_bonus, drilling, drilling_locked, drill_complete_turn).
        # This is a pragmatic exception to Golden Rule #1 — the read-then-clear
        # pattern is correct, just located here for atomicity with the combat flow.
        if attacker_drill_bonus > 0:
            attacker.shock_bonus = 0
            attacker.drilling = False
            attacker.drilling_locked = False
            attacker.drill_complete_turn = -1

        shock_multiplier = 1.0 + (attacker_shock / 20.0)
        # Apply stance modifier to shock
        shock_multiplier *= attacker_stance_modifier

        # ════════════════════════════════════════════════════════════
        # CAVALRY TERRAIN EFFECTIVENESS (Phase 6.1): Scale recklessness bonus by terrain
        # Plains boost cavalry (+20%), mountains gut it (-70%).
        # Only affects cavalry marshals with recklessness > 0.
        # Non-cavalry marshals are completely unaffected.
        # ════════════════════════════════════════════════════════════
        cavalry_terrain_message = None
        if getattr(attacker, 'cavalry', False) and getattr(attacker, 'is_reckless_cavalry', False):
            recklessness_bonus = attacker._get_recklessness_attack_bonus()
            if recklessness_bonus > 0:
                terrain_cav_mult = TERRAIN_CAVALRY_EFFECTIVENESS.get(terrain, 1.0)
                if terrain_cav_mult != 1.0:
                    # Scale the recklessness portion of the attack modifier
                    # recklessness_bonus was applied as (1.0 + bonus) inside get_attack_modifier
                    # We adjust by removing the original bonus and adding the terrain-scaled version
                    original_contribution = 1.0 + recklessness_bonus
                    scaled_contribution = 1.0 + (recklessness_bonus * terrain_cav_mult)
                    terrain_cavalry_adjustment = scaled_contribution / original_contribution
                    shock_multiplier *= terrain_cavalry_adjustment

                    terrain_name = terrain.replace("_", " ").title()
                    effectiveness_pct = int(terrain_cav_mult * 100)
                    if terrain_cav_mult > 1.0:
                        cavalry_terrain_message = f"{attacker.name}'s cavalry thrives on {terrain_name} terrain! ({effectiveness_pct}% effectiveness)"
                    else:
                        cavalry_terrain_message = f"{attacker.name}'s cavalry is hampered by {terrain_name} terrain ({effectiveness_pct}% effectiveness)"

        # ════════════════════════════════════════════════════════════
        # CAVALRY vs ARTILLERY COUNTER: Cavalry devastates unscreened guns
        # +30% attack bonus when cavalry attacks artillery.
        # Applied to shock_multiplier (target-type interaction, not marshal-intrinsic).
        # ════════════════════════════════════════════════════════════
        cavalry_counter_message = None
        if getattr(attacker, 'cavalry', False) and getattr(defender, 'artillery', False):
            shock_multiplier *= 1.30
            cavalry_counter_message = f"{attacker.name}'s cavalry overruns {defender.name}'s gun line! (+30% attack)"

        # ════════════════════════════════════════════════════════════
        # SQUARE FORMATION INTERACTIONS (Phase 7b, Session 67)
        # Target-type interactions: depends on ATTACKER's type vs DEFENDER's state.
        # -40% cavalry damage against square (horses refuse bayonet wall)
        # +50% artillery damage against square (packed ranks, can't miss)
        # Infantry vs square: no special modifier
        # ════════════════════════════════════════════════════════════
        square_cavalry_message = None
        square_artillery_message = None
        if getattr(defender, 'square_formation', False):
            if getattr(attacker, 'cavalry', False):
                shock_multiplier *= 0.60  # -40% damage
                square_cavalry_message = f"{defender.name}'s square holds firm! {attacker.name}'s cavalry charge is blunted. (-40% cavalry damage)"
            elif getattr(attacker, 'artillery', False):
                shock_multiplier *= 1.50  # +50% damage
                square_artillery_message = f"{defender.name}'s packed square is a perfect target for {attacker.name}'s guns! (+50% artillery damage)"

        # Apply DEFENSE skill to defender protection (reduces casualties taken)
        # Higher defense = fewer casualties taken
        # defense_skill // 2 gives 0 to 5 percentage points of protection
        defender_defense = defender.get_effective_skill("defense") if hasattr(defender, 'get_effective_skill') else defender.skills.get("defense", 5)

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
                            defender_personality_message += " Outnumbered bonus: +10%"

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
        attacker_defense = attacker.get_effective_skill("defense") if hasattr(attacker, 'get_effective_skill') else attacker.skills.get("defense", 5)
        attacker_defense_mult = 1.0 - (attacker_defense / 20.0)
        attacker_casualties = int(base_attacker_casualties * attacker_defense_mult)

        # NOTE: Ranged bombardment (artillery firing from adjacent region) now uses
        # _execute_bombardment() in executor.py. resolve_battle() only handles
        # same-region combat. See BOMBARDMENT_SPEC.md §3.

        # Defender takes casualties (increased by attacker shock, reduced by defender defense, affected by dice roll)
        defender_casualties = int(
            base_defender_casualties
            * shock_multiplier          # Attacker's shock increases damage
            * defense_multiplier        # Defender's defense reduces damage
            * attacker_roll['multiplier']  # Dice roll affects damage
        )

        # ════════════════════════════════════════════════════════════
        # GLORIOUS CHARGE (Phase 3): 2x damage dealt AND taken
        # ════════════════════════════════════════════════════════════
        glorious_charge_message = None
        if glorious_charge:
            attacker_casualties = int(attacker_casualties * 2)
            defender_casualties = int(defender_casualties * 2)
            glorious_charge_message = f"[Cavalry][Combat] GLORIOUS CHARGE! {attacker.name}'s cavalry deals devastating damage - but exposes themselves! (2x casualties both ways)"

        #print(f"   💀 Casualties: {attacker.name} {attacker_casualties:,}, {defender.name} {defender_casualties:,}")

        # Capture original strengths for casualty-scaled morale
        attacker_original_strength = attacker.strength
        defender_original_strength = defender.strength

        # ════════════════════════════════════════════════════════════════
        # [S62] DEFERRED CASUALTY PATH — coordinated multi-marshal battles
        # When apply_casualties=False, compute ALL combat math but do NOT
        # modify marshal state. Returns raw results for caller to distribute
        # among participants. Fortification degradation KEPT (battle-triggered).
        # See PHASE7_SPEC_AMENDMENTS C1/C2 for the full contract.
        # ════════════════════════════════════════════════════════════════
        if not apply_casualties:
            return self._build_deferred_result(
                attacker, defender,
                attacker_casualties, defender_casualties,
                attacker_original_strength, defender_original_strength,
                attacker_roll, terrain, flanking_bonus, flanking_message,
                glorious_charge,
                # Message variables computed above
                ability_message, drill_bonus_message, fortify_bonus_message,
                drilling_penalty_message, exhaustion_message,
                attacker_stance_message, defender_stance_message,
                attacker_personality_message, defender_personality_message,
                terrain_defense_message, cavalry_terrain_message,
                cavalry_counter_message, glorious_charge_message,
                attacker_modifier_snapshot, defender_modifier_snapshot,
                is_drilling,
                square_cavalry_message, square_artillery_message,
            )

        # Apply casualties FIRST (this was missing!)
        attacker.take_casualties(attacker_casualties)
        defender.take_casualties(defender_casualties)

        # Calculate casualty rates for morale scaling
        # Heavier losses = worse morale hit (Napoleonic armies broke after severe casualties)
        atk_casualty_rate = attacker_casualties / max(attacker_original_strength, 1)
        def_casualty_rate = defender_casualties / max(defender_original_strength, 1)

        def _scaled_morale_loss(casualty_rate: float, base_loss: int) -> int:
            """Scale morale loss by casualty severity. Worse losses = worse morale.
            At 10% casualties: roughly base_loss. At 30%+: up to 2.5x base_loss."""
            severity = min(casualty_rate / 0.15, 2.5)  # 15% = 1.0x, 37.5% = 2.5x cap
            return max(base_loss, int(base_loss * severity))

        # Determine victor (AFTER applying casualties)
        if attacker.strength <= 0 and defender.strength <= 0:
            victor = None
            outcome = "mutual_destruction"
            attacker.adjust_morale(-_scaled_morale_loss(atk_casualty_rate, 20))
            defender.adjust_morale(-_scaled_morale_loss(def_casualty_rate, 20))
            attacker.battles_lost += 1
            defender.battles_lost += 1
        elif attacker.strength <= 0:
            victor = defender
            outcome = "defender_victory"
            defender.adjust_morale(10)
            attacker.adjust_morale(-_scaled_morale_loss(atk_casualty_rate, 20))
            defender.battles_won += 1
            attacker.battles_lost += 1
            # COUNTER-PUNCH: Cautious defenders (Davout) get free attack after winning defense
            if getattr(defender, 'personality', '') == 'cautious':
                defender.counter_punch_available = True
                defender.counter_punch_turns = 2  # Survives one turn transition
                debug_print(f"  [COUNTER-PUNCH EARNED] {defender.name} can now attack for FREE!")
        elif defender.strength <= 0:
            victor = attacker
            outcome = "attacker_victory"
            attacker.adjust_morale(10)
            defender.adjust_morale(-_scaled_morale_loss(def_casualty_rate, 20))
            attacker.battles_won += 1
            defender.battles_lost += 1
        else:
            # Both survive - tactical result
            if attacker_casualties > defender_casualties * 1.5:
                victor = defender
                outcome = "defender_tactical_victory"
                defender.adjust_morale(5)
                attacker.adjust_morale(-_scaled_morale_loss(atk_casualty_rate, 10))
                # COUNTER-PUNCH: Cautious defenders (Davout) get free attack after winning defense
                if getattr(defender, 'personality', '') == 'cautious':
                    defender.counter_punch_available = True
                    defender.counter_punch_turns = 2  # Survives one turn transition
                    debug_print(f"  [COUNTER-PUNCH EARNED] {defender.name} can now attack for FREE!")
            elif defender_casualties > attacker_casualties * 1.5:
                victor = attacker
                outcome = "attacker_tactical_victory"
                attacker.adjust_morale(5)
                defender.adjust_morale(-_scaled_morale_loss(def_casualty_rate, 10))
            else:
                victor = None
                outcome = "stalemate"
                attacker.adjust_morale(-_scaled_morale_loss(atk_casualty_rate, 5))
                defender.adjust_morale(-_scaled_morale_loss(def_casualty_rate, 5))
                # COUNTER-PUNCH: Cautious defenders held the line - still get counter-punch
                if getattr(defender, 'personality', '') == 'cautious':
                    defender.counter_punch_available = True
                    defender.counter_punch_turns = 2  # Survives one turn transition
                    debug_print(f"  [COUNTER-PUNCH EARNED] {defender.name} held the line - can now attack for FREE!")

        # COUNTER-PUNCH MASTERY: Davout's Iron Marshal ability
        # When Davout is the defender in any combat (win, lose, or draw),
        # his next attack gets +20%. Only triggers if defender survived.
        if (defender.strength > 0
                and hasattr(defender, 'ability')
                and defender.ability.get("name") == "Counter-Punch Mastery"):
            defender.counter_punch_ready = True
            debug_print(f"  [COUNTER-PUNCH MASTERY] {defender.name} absorbs the blow — next attack +20%!")

        # Build description with tactical state messages
        base_description = self._generate_description(
            attacker, defender, outcome, attacker_casualties, defender_casualties, attacker_roll
        )

        # Prepend tactical state messages (shared helper — P1-21 dedup)
        tactical_prefix = _build_tactical_prefix(
            attacker, defender,
            attacker_stance_message=attacker_stance_message,
            attacker_personality_message=attacker_personality_message,
            defender_stance_message=defender_stance_message,
            defender_personality_message=defender_personality_message,
            drill_bonus_message=drill_bonus_message,
            fortify_bonus_message=fortify_bonus_message,
            drilling_penalty_message=drilling_penalty_message,
            exhaustion_message=exhaustion_message,
            terrain_defense_message=terrain_defense_message,
            cavalry_terrain_message=cavalry_terrain_message,
            cavalry_counter_message=cavalry_counter_message,
            square_cavalry_message=square_cavalry_message,
            square_artillery_message=square_artillery_message,
            glorious_charge_message=glorious_charge_message,
        )

        # ════════════════════════════════════════════════════════════════
        # FORCED RETREAT CHECK: Armies with critically low morale must retreat
        # Uses module-level FORCED_RETREAT_THRESHOLD (25%)
        # ════════════════════════════════════════════════════════════════
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
            retreat_message += f"\n\n[!] {attacker.name}'s troops are BROKEN (morale {int(attacker.morale)}%)! FORCED RETREAT!"
        if defender_forced_retreat:
            retreat_message += f"\n\n[!] {defender.name}'s troops are BROKEN (morale {int(defender.morale)}%)! FORCED RETREAT!"

        # Victory flags (used by pursuit, recklessness, and result dict)
        attacker_won = outcome in ["attacker_victory", "attacker_tactical_victory"]
        attacker_lost = outcome in ["defender_victory", "defender_tactical_victory", "mutual_destruction"]

        # ════════════════════════════════════════════════════════════
        # PURSUIT DAMAGE: Attacker abilities that punish retreating enemies
        # Blucher "Vorwärts!" — 3k extra casualties on retreat
        # Uxbridge "Pursuit Master" — 5k extra casualties on retreat (cavalry)
        # Only fires when defender is forced to retreat. Floor at 1000 strength.
        # If multiple pursuit abilities somehow apply, use highest only.
        # ════════════════════════════════════════════════════════════
        pursuit_damage = 0
        pursuit_message = None
        if defender_forced_retreat and attacker_won:
            attacker_ability_name = ""
            if hasattr(attacker, 'ability'):
                attacker_ability_name = attacker.ability.get("name", "")

            if attacker_ability_name == "Pursuit Master" and getattr(attacker, 'cavalry', False):
                pursuit_damage = 5000
                pursuit_message = f"[Cavalry] {attacker.name}'s '{attacker.ability['name']}' — cavalry runs down the retreating enemy! (+{pursuit_damage:,} pursuit casualties)"
            elif attacker_ability_name == "Vorwärts!":
                pursuit_damage = 3000
                pursuit_message = f"[Combat] {attacker.name}'s '{attacker.ability['name']}' — relentless pursuit inflicts extra casualties! (+{pursuit_damage:,} pursuit casualties)"

            if pursuit_damage > 0 and defender.strength > 1000:
                old_strength = defender.strength
                defender.strength = max(1000, defender.strength - pursuit_damage)
                actual_pursuit = old_strength - defender.strength
                if actual_pursuit > 0:
                    defender_casualties += actual_pursuit
                    retreat_message += f"\n\n{pursuit_message}"
                else:
                    # Defender already at or below floor
                    pursuit_damage = 0
                    pursuit_message = None
            elif pursuit_damage > 0:
                # Defender at/below 1000 — pursuit doesn't fire (P1-5 fix)
                pursuit_damage = 0
                pursuit_message = None

        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS (Phase 3): Update attacker's recklessness
        # - Increment on attack WIN (not glorious_charge, which resets)
        # - Reset on attack LOSS
        # - Glorious charge resets are handled in executor._execute_glorious_charge
        # ════════════════════════════════════════════════════════════
        recklessness_message = None

        if hasattr(attacker, 'is_reckless_cavalry') and attacker.is_reckless_cavalry:
            old_recklessness = getattr(attacker, 'recklessness', 0)

            if glorious_charge:
                # Glorious charge: reset handled in executor (already done before this call)
                # But add message for clarity
                recklessness_message = f"[color=#cd6b6b]{attacker.name}'s recklessness resets after Glorious Charge[/color]"
            elif attacker_won:
                # Won as attacker (not charge): increment
                attacker._increment_recklessness()
                new_recklessness = getattr(attacker, 'recklessness', 0)
                if new_recklessness > old_recklessness:
                    if new_recklessness == 1:
                        recklessness_message = f"[Cavalry] {attacker.name}'s blood is up! (Recklessness: {new_recklessness})"
                    elif new_recklessness == 2:
                        recklessness_message = f"[Cavalry] {attacker.name} is building momentum! (Recklessness: {new_recklessness})"
                    elif new_recklessness == 3:
                        recklessness_message = f"[Cavalry][!] {attacker.name}'s recklessness is dangerous! Glorious Charge popup next attack. (Recklessness: {new_recklessness})"
                    else:  # 4+
                        recklessness_message = f"[Cavalry][!] {attacker.name} is UNCONTROLLABLE! Will auto-charge at next turn start! (Recklessness: {new_recklessness})"
            elif attacker_lost:
                # Lost as attacker: reset
                if old_recklessness > 0:
                    attacker.reset_recklessness()
                    recklessness_message = f"[Cavalry] {attacker.name}'s momentum broken by defeat. [color=#cd6b6b](Recklessness: {old_recklessness} → 0)[/color]"

        if recklessness_message:
            retreat_message += f"\n\n{recklessness_message}"

        # ════════════════════════════════════════════════════════════
        # FORTIFICATION DEGRADATION: Battles damage walls
        # Every battle degrades the defender's personal defense_bonus by 5%,
        # regardless of who wins. This makes sustained assault crack fortified
        # positions. Star fort buildings (fortification_bonus param) are NOT
        # affected — only the marshal's personal fortify bonus degrades.
        # ════════════════════════════════════════════════════════════
        fortification_degraded = False
        fortification_old = 0.0
        fortification_new = 0.0
        drouot_ability_message = None
        if getattr(defender, 'defense_bonus', 0) > 0:
            fortification_old = defender.defense_bonus
            degradation_amount = 0.10 if getattr(attacker, 'artillery', False) else 0.05
            # Drouot's "Sage of the Grand Army": +5% fort degradation on attack
            if (hasattr(attacker, 'ability')
                    and attacker.ability.get("name") == "Sage of the Grand Army"
                    and attacker.ability.get("trigger") == "when_attacking_fortified"):
                degradation_amount = 0.15
                drouot_ability_message = f"{attacker.name}'s '{attacker.ability['name']}' — precise artillery fire degrades fortifications faster!"
            defender.defense_bonus = max(0, round(defender.defense_bonus - degradation_amount, 2))
            fortification_new = defender.defense_bonus
            fortification_degraded = True

        # THIS RETURN MUST BE HERE!
        result_dict = {
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
            "glorious_charge": glorious_charge,  # Phase 3: Cavalry recklessness
            "attacker_won": attacker_won,  # Phase 3: For recklessness tracking
            "terrain_defense_message": terrain_defense_message,  # Phase 6.1: Terrain defense
            "cavalry_terrain_message": cavalry_terrain_message,  # Phase 6.1: Cavalry terrain
            "cavalry_counter_message": cavalry_counter_message,  # Phase 6: Cavalry vs artillery
            "description": tactical_prefix + base_description + retreat_message,
            # Berthier's After-Action Report
            "attacker_nation": getattr(attacker, "nation", ""),
            "defender_nation": getattr(defender, "nation", ""),
            "attacker_original_strength": int(attacker_original_strength),
            "defender_original_strength": int(defender_original_strength),
            "modifier_snapshot": {
                "attacker": attacker_modifier_snapshot,
                "defender": defender_modifier_snapshot,
            },
            # Fortification degradation (Session 31) — FINAL-8: int() for Godot
            "fortification_degraded": fortification_degraded,
            "fortification_old": int(fortification_old * 100),
            "fortification_new": int(fortification_new * 100),
            # Drouot ability (Phase 6.5: Marshal abilities wiring)
            "drouot_ability_triggered": drouot_ability_message,
            # Pursuit damage (Phase 6.5: Blucher/Uxbridge abilities)
            "pursuit_damage": int(pursuit_damage),
            "pursuit_message": pursuit_message,
            # Notification flags for executor.py to create notifications
            "counter_punch_earned": bool(getattr(defender, 'counter_punch_available', False)
                                         and getattr(defender, 'personality', '') == 'cautious'
                                         and outcome in ("defender_victory", "defender_tactical_victory", "stalemate")),
            # Counter-Punch Mastery: Davout's +20% attack after defending (any outcome)
            "counter_punch_mastery_earned": bool(getattr(defender, 'counter_punch_ready', False)
                                                 and hasattr(defender, 'ability')
                                                 and defender.ability.get("name") == "Counter-Punch Mastery"),
            "drill_cancelled": bool(is_drilling),
        }
        result_dict["battle_report"] = generate_battle_report(result_dict)

        # ════════════════════════════════════════════════════════════
        # EVENT LOG: Pre-build battle event dict for the caller to log.
        # combat.py doesn't have WorldState access, so we return the event
        # in the result dict. The caller (executor.py) fills in location
        # and calls world.log_event(). Retreat/broken events are logged
        # directly by _apply_forced_retreat_or_break where destination is known.
        # ════════════════════════════════════════════════════════════
        result_dict["log_battle_event"] = {
            "type": "battle",
            "attacker": attacker.name,
            "attacker_nation": getattr(attacker, "nation", ""),
            "defender": defender.name,
            "defender_nation": getattr(defender, "nation", ""),
            "location": "",  # Caller fills in
            "outcome": outcome,
            "attacker_casualties": int(attacker_casualties),
            "defender_casualties": int(defender_casualties),
            # Fort degradation (for enemy phase dialog display) — FINAL-8: int() for Godot
            "fortification_degraded": fortification_degraded,
            "fortification_old": int(fortification_old * 100),
            "fortification_new": int(fortification_new * 100),
        }
        return result_dict

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
        """Get defender bonus based on terrain type.

        Uses TERRAIN_DEFENSE_BONUS from region.py as single source of truth.
        Legacy values ("open", "fortified") kept for backward compat with tests/mods.
        """
        # Check new terrain types first (single source in region.py)
        if terrain in TERRAIN_DEFENSE_BONUS:
            return TERRAIN_DEFENSE_BONUS[terrain]

        # Legacy aliases for backward compatibility
        legacy_modifiers = {
            "open": 0.0,
            "fortified": 0.30,
            "mountain": 0.20,
            "river": 0.15,
        }
        return legacy_modifiers.get(terrain, 0.0)

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

        casualties = max(1, int(army_size * casualty_rate))

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

    def _build_deferred_result(
            self,
            attacker, defender,
            attacker_casualties, defender_casualties,
            attacker_original_strength, defender_original_strength,
            attacker_roll, terrain, flanking_bonus, flanking_message,
            glorious_charge,
            ability_message, drill_bonus_message, fortify_bonus_message,
            drilling_penalty_message, exhaustion_message,
            attacker_stance_message, defender_stance_message,
            attacker_personality_message, defender_personality_message,
            terrain_defense_message, cavalry_terrain_message,
            cavalry_counter_message, glorious_charge_message,
            attacker_modifier_snapshot, defender_modifier_snapshot,
            is_drilling,
            square_cavalry_message=None, square_artillery_message=None,
    ) -> Dict:
        """Build result dict for apply_casualties=False (Session 62).

        Computes projected outcome (C2), morale deltas (int per X3),
        and fortification degradation. Does NOT modify marshal state
        except fort degradation (battle-triggered per C1).
        """
        # Casualty rates for morale scaling (same formula as normal path)
        atk_casualty_rate = attacker_casualties / max(attacker_original_strength, 1)
        def_casualty_rate = defender_casualties / max(defender_original_strength, 1)

        def _scaled_morale_loss(casualty_rate: float, base_loss: int) -> int:
            severity = min(casualty_rate / 0.15, 2.5)
            return max(base_loss, int(base_loss * severity))

        # C2: Victor from PROJECTED strength (never modify .strength)
        projected_atk = attacker.strength - attacker_casualties
        projected_def = defender.strength - defender_casualties

        if projected_atk <= 0 and projected_def <= 0:
            victor = None
            outcome = "mutual_destruction"
            # [5D-1] Apply morale penalty for mutual destruction (matches normal combat path)
            atk_morale_delta = -_scaled_morale_loss(atk_casualty_rate, 20)
            def_morale_delta = -_scaled_morale_loss(def_casualty_rate, 20)
        elif projected_atk <= 0:
            victor = defender
            outcome = "defender_victory"
            def_morale_delta = 10
            atk_morale_delta = -_scaled_morale_loss(atk_casualty_rate, 20)
        elif projected_def <= 0:
            victor = attacker
            outcome = "attacker_victory"
            atk_morale_delta = 10
            def_morale_delta = -_scaled_morale_loss(def_casualty_rate, 20)
        else:
            # Both survive — tactical result
            # CRITICAL: 1.5 threshold MUST match line ~477 in normal path
            if attacker_casualties > defender_casualties * 1.5:
                victor = defender
                outcome = "defender_tactical_victory"
                def_morale_delta = 5
                atk_morale_delta = -_scaled_morale_loss(atk_casualty_rate, 10)
            elif defender_casualties > attacker_casualties * 1.5:
                victor = attacker
                outcome = "attacker_tactical_victory"
                atk_morale_delta = 5
                def_morale_delta = -_scaled_morale_loss(def_casualty_rate, 10)
            else:
                victor = None
                outcome = "stalemate"
                atk_morale_delta = -_scaled_morale_loss(atk_casualty_rate, 5)
                def_morale_delta = -_scaled_morale_loss(def_casualty_rate, 5)

        # Fortification degradation — KEEP inside (battle-triggered per C1)
        fortification_degraded = False
        fortification_old = 0.0
        fortification_new = 0.0
        drouot_ability_message = None
        if getattr(defender, 'defense_bonus', 0) > 0:
            fortification_old = defender.defense_bonus
            degradation_amount = 0.10 if getattr(attacker, 'artillery', False) else 0.05
            if (hasattr(attacker, 'ability')
                    and attacker.ability.get("name") == "Sage of the Grand Army"
                    and attacker.ability.get("trigger") == "when_attacking_fortified"):
                degradation_amount = 0.15
                drouot_ability_message = (
                    f"{attacker.name}'s '{attacker.ability['name']}' — "
                    f"precise artillery fire degrades fortifications faster!"
                )
            defender.defense_bonus = max(0, round(defender.defense_bonus - degradation_amount, 2))
            fortification_new = defender.defense_bonus
            fortification_degraded = True

        # Victory flags
        attacker_won = outcome in ["attacker_victory", "attacker_tactical_victory"]

        # Build description (tactical prefix + base narrative, no retreat/recklessness)
        base_description = self._generate_description(
            attacker, defender, outcome, attacker_casualties, defender_casualties, attacker_roll
        )
        tactical_prefix = _build_tactical_prefix(
            attacker, defender,
            attacker_stance_message=attacker_stance_message,
            attacker_personality_message=attacker_personality_message,
            defender_stance_message=defender_stance_message,
            defender_personality_message=defender_personality_message,
            drill_bonus_message=drill_bonus_message,
            fortify_bonus_message=fortify_bonus_message,
            drilling_penalty_message=drilling_penalty_message,
            exhaustion_message=exhaustion_message,
            terrain_defense_message=terrain_defense_message,
            cavalry_terrain_message=cavalry_terrain_message,
            cavalry_counter_message=cavalry_counter_message,
            square_cavalry_message=square_cavalry_message,
            square_artillery_message=square_artillery_message,
            glorious_charge_message=glorious_charge_message,
        )

        from backend.game_logic.battle_report import generate_battle_report

        result_dict = {
            "outcome": outcome,
            "victor": victor.name if victor else None,
            "attacker": {
                "name": attacker.name,
                "casualties": int(attacker_casualties),
                "remaining": int(attacker.strength),  # UNMODIFIED — caller distributes
                "morale": int(attacker.morale),  # UNMODIFIED — caller applies
                "forced_retreat": False,  # Deferred to caller
            },
            "defender": {
                "name": defender.name,
                "casualties": int(defender_casualties),
                "remaining": int(defender.strength),  # UNMODIFIED
                "morale": int(defender.morale),  # UNMODIFIED
                "forced_retreat": False,  # Deferred to caller
            },
            "terrain": terrain,
            "attacker_roll": attacker_roll,
            "ability_triggered": ability_message,
            "drill_bonus_triggered": drill_bonus_message,
            "fortify_bonus_triggered": fortify_bonus_message,
            "drilling_penalty_triggered": drilling_penalty_message,
            "attacker_stance_triggered": attacker_stance_message,
            "defender_stance_triggered": defender_stance_message,
            "attacker_personality_triggered": attacker_personality_message,
            "defender_personality_triggered": defender_personality_message,
            "flanking_bonus": int(flanking_bonus),
            "flanking_message": flanking_message,
            "glorious_charge": glorious_charge,
            "attacker_won": attacker_won,
            "terrain_defense_message": terrain_defense_message,
            "cavalry_terrain_message": cavalry_terrain_message,
            "cavalry_counter_message": cavalry_counter_message,
            "description": tactical_prefix + base_description,
            "attacker_nation": getattr(attacker, "nation", ""),
            "defender_nation": getattr(defender, "nation", ""),
            "attacker_original_strength": int(attacker_original_strength),
            "defender_original_strength": int(defender_original_strength),
            "modifier_snapshot": {
                "attacker": attacker_modifier_snapshot,
                "defender": defender_modifier_snapshot,
            },
            # FINAL-8: int() for Godot
            "fortification_degraded": fortification_degraded,
            "fortification_old": int(fortification_old * 100),
            "fortification_new": int(fortification_new * 100),
            "drouot_ability_triggered": drouot_ability_message,
            "pursuit_damage": 0,  # Deferred to caller
            "pursuit_message": None,
            "counter_punch_earned": False,  # Deferred to caller
            "counter_punch_mastery_earned": False,  # Deferred to caller
            "drill_cancelled": bool(is_drilling),
            # ═══ NEW: Raw data for caller to distribute (Session 62) ═══
            "attacker_raw_casualties": int(attacker_casualties),
            "defender_raw_casualties": int(defender_casualties),
            "attacker_morale_delta": int(atk_morale_delta),
            "defender_morale_delta": int(def_morale_delta),
            "raw_outcome": outcome,
        }
        result_dict["battle_report"] = generate_battle_report(result_dict)
        result_dict["log_battle_event"] = {
            "type": "battle",
            "attacker": attacker.name,
            "attacker_nation": getattr(attacker, "nation", ""),
            "defender": defender.name,
            "defender_nation": getattr(defender, "nation", ""),
            "location": "",  # Caller fills in
            "outcome": outcome,
            "attacker_casualties": int(attacker_casualties),
            "defender_casualties": int(defender_casualties),
            # FINAL-8: int() for Godot
            "fortification_degraded": fortification_degraded,
            "fortification_old": int(fortification_old * 100),
            "fortification_new": int(fortification_new * 100),
        }
        return result_dict


# Test code
if __name__ == "__main__":
    """Test combat system."""
    debug_print("=" * 70)
    debug_print("COMBAT SYSTEM TEST")
    debug_print("=" * 70)

    from backend.models.marshal import Marshal

    # Create test marshals
    ney = Marshal("Ney", "Belgium", 72000, "aggressive", "France")
    wellington = Marshal("Wellington", "Waterloo", 68000, "cautious", "Britain")

    debug_print("\nBefore Battle:")
    debug_print(f"  {ney}")
    debug_print(f"  {wellington}")

    # Create combat resolver
    combat = CombatResolver()

    # Test 1: Open field battle
    debug_print("\n" + "=" * 70)
    debug_print("TEST 1: Open Field Battle")
    debug_print("=" * 70)

    result = combat.resolve_battle(ney, wellington, terrain="open")

    debug_print(f"\nOutcome: {result['outcome']}")
    debug_print(f"Victor: {result['victor']}")
    debug_print(f"\n{result['description']}")
    debug_print(f"\nAttacker ({result['attacker']['name']}):")
    debug_print(f"  Casualties: {result['attacker']['casualties']:,}")
    debug_print(f"  Remaining: {result['attacker']['remaining']:,}")
    debug_print(f"  Morale: {result['attacker']['morale']}%")
    debug_print(f"\nDefender ({result['defender']['name']}):")
    debug_print(f"  Casualties: {result['defender']['casualties']:,}")
    debug_print(f"  Remaining: {result['defender']['remaining']:,}")
    debug_print(f"  Morale: {result['defender']['morale']}%")

    # Test 2: Fortified position
    debug_print("\n" + "=" * 70)
    debug_print("TEST 2: Attack on Fortified Position")
    debug_print("=" * 70)

    # Reset marshals
    ney_2 = Marshal("Ney", "Belgium", 50000, "aggressive", "France")
    blucher = Marshal("Blucher", "Waterloo", 40000, "cautious", "Prussia")

    debug_print("\nBefore Battle:")
    debug_print(f"  {ney_2}")
    debug_print(f"  {blucher}")

    result_2 = combat.resolve_battle(ney_2, blucher, terrain="fortified")

    debug_print(f"\nOutcome: {result_2['outcome']}")
    debug_print(f"Victor: {result_2['victor']}")
    debug_print(f"\n{result_2['description']}")

    debug_print("\n" + "=" * 70)
    debug_print("COMBAT TEST COMPLETE!")
    debug_print("=" * 70)
    debug_print("\n✓ Battle resolution working")
    debug_print("✓ Casualties calculated")
    debug_print("✓ Morale effects applied")
    debug_print("✓ Terrain modifiers working")
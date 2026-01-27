"""
Personality Combat Modifiers for Project Sovereign (Phase 2.8)

Defines combat bonuses and penalties for each marshal personality type.
These modifiers are applied on top of stance/drill/fortify bonuses.

═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Dict, Any

# ════════════════════════════════════════════════════════════════════════════════
# NEY (Aggressive) - Attack-focused, poor on defense
# ════════════════════════════════════════════════════════════════════════════════
NEY_MODIFIERS = {
    # Base attack bonus (always applies)
    "base_attack_bonus": 0.15,  # +15% attack

    # Stance-specific bonuses
    "aggressive_stance_attack_bonus": 0.05,  # +5% additional when aggressive (total +20%)
    "aggressive_stance_defense_penalty": 0.05,  # -5% additional defense in aggressive (total -15%)
    "defensive_stance_defense_penalty": 0.05,  # -5% off defensive bonus (gets +10% not +15%)

    # Drill synergy
    "drill_shock_bonus": 0.05,  # +5% additional after drill (total +25% with drill's +20%)

    # Fortify limitations
    "max_fortify_bonus": 0.10,  # Capped at 10% (not 15%)

    # Trust modifiers (applied in disobedience system)
    "attack_order_trust_bonus": 1,  # +2 total (instead of +1)
    "successful_attack_trust_bonus": 2,  # +3 total
    "defending_trust_penalty_per_turn": -1,  # -1 per turn after 3 turns (handled by restlessness)
}

# ════════════════════════════════════════════════════════════════════════════════
# DAVOUT (Cautious) - Defense-focused, methodical
# ════════════════════════════════════════════════════════════════════════════════
DAVOUT_MODIFIERS = {
    # Stance-specific bonuses
    "defensive_stance_defense_bonus": 0.05,  # +5% additional when defensive (total +20%)
    "aggressive_stance_attack_penalty": 0.05,  # -5% attack when aggressive (hesitant)

    # Bad odds penalty
    "bad_odds_attack_penalty": 0.10,  # -10% attack when outnumbered (<1:1 ratio)
    "bad_odds_threshold": 1.0,  # Strength ratio below which penalty applies

    # Outnumbered defense bonus
    "outnumbered_defense_bonus": 0.10,  # +10% defense when outnumbered

    # Fortify improvements
    "fortify_rate_bonus": 0.01,  # +1% per turn (total +3% instead of +2%)
    "max_fortify_bonus": 0.20,  # 20% max (not 15%)
    "instant_fortify_bonus": 0.05,  # +5% on first fortify

    # Scout range bonus
    "scout_range_bonus": 1,  # +1 region

    # Trust modifiers
    "fortify_defend_trust_bonus": 1,  # +2 total
    "successful_defense_trust_bonus": 2,  # +3 total
    "bad_odds_attack_trust_penalty": -1,  # -1 for attacking at bad odds
}

# ════════════════════════════════════════════════════════════════════════════════
# GROUCHY (Literal) - Precision Execution
#
# PHASE 5.2 IMPLEMENTATION: See docs/PHASE_5_2_IMPLEMENTATION_PLAN.md
# This file will be expanded with:
#   - explicit_order_attack_bonus: 0.10 (+10% attack on explicit orders)
#   - explicit_order_defense_bonus: 0.10 (+10% defense on explicit orders)
#   - strategic_completion_bonus: 0.20 (+20% next action after completing strategic)
#   - strategic_action_cost: 1 (1 action instead of 2 for strategic commands)
#   - strategic_morale_immunity: True (no morale loss during strategic execution)
#   - explicit_order_trust_bonus: 2 (+2 trust for explicit orders)
#   - strategic_completion_trust_bonus: 5 (+5 trust on strategic completion)
# ════════════════════════════════════════════════════════════════════════════════
GROUCHY_MODIFIERS = {
    # Immovable ability - +15% defense when holding position
    "hold_position_defense_bonus": 0.15,

    # TODO [Phase 5.2]: Add Precision Execution bonuses
    # See docs/PHASE_5_2_IMPLEMENTATION_PLAN.md Section 3 for full specification
}

# ════════════════════════════════════════════════════════════════════════════════
# SOULT (Balanced) - TODO: Not implemented yet
# ════════════════════════════════════════════════════════════════════════════════
# TODO: Soult marshal and abilities
# - Weaker stances: +10%/-15% instead of +15%/-10%
# - Base +5% all actions
# - Adjacent ally +10%
# - Allies adjacent to Soult get +5%
# - Retreat recovery -1 turn

# ════════════════════════════════════════════════════════════════════════════════
# LANNES (Loyal) - TODO: Not implemented yet
# ════════════════════════════════════════════════════════════════════════════════
# TODO: Lannes marshal and abilities
# - Desperate defense: +20% below 50% strength, +25% below 25%
# - Absolute Obedience: Always obeys on INSIST
# - Inspiring Presence: Adjacent marshals -0.15 severity
# - Napoleon proximity: +15%/+20% (requires Napoleon unit)


def get_personality_modifiers(personality: str) -> Dict[str, Any]:
    """
    Get combat modifiers for a personality type.

    Args:
        personality: Personality string (aggressive, cautious, literal, etc.)

    Returns:
        Dict of modifier constants for that personality
    """
    modifiers = {
        "aggressive": NEY_MODIFIERS,
        "cautious": DAVOUT_MODIFIERS,
        "literal": GROUCHY_MODIFIERS,
    }
    return modifiers.get(personality.lower(), {})


def get_attack_modifier_for_personality(
    personality: str,
    stance: str,
    has_drill_bonus: bool = False,
    strength_ratio: float = None
) -> float:
    """
    Calculate personality-specific attack modifier.

    Args:
        personality: Marshal's personality
        stance: Current stance (neutral, defensive, aggressive)
        has_drill_bonus: Whether drill bonus is active
        strength_ratio: Our strength / enemy strength (for bad odds check)

    Returns:
        Float multiplier (e.g., 1.15 = +15%)
    """
    modifier = 1.0
    mods = get_personality_modifiers(personality)

    if personality.lower() == "aggressive":
        # Ney: +15% base attack
        modifier *= (1.0 + mods.get("base_attack_bonus", 0))

        # +5% additional in aggressive stance
        if stance == "aggressive":
            modifier *= (1.0 + mods.get("aggressive_stance_attack_bonus", 0))

        # +5% additional with drill bonus
        if has_drill_bonus:
            modifier *= (1.0 + mods.get("drill_shock_bonus", 0))

    elif personality.lower() == "cautious":
        # Davout: -5% attack when aggressive (hesitant)
        if stance == "aggressive":
            modifier *= (1.0 - mods.get("aggressive_stance_attack_penalty", 0))

        # -10% attack at bad odds
        if strength_ratio is not None and strength_ratio < mods.get("bad_odds_threshold", 1.0):
            modifier *= (1.0 - mods.get("bad_odds_attack_penalty", 0))

    return modifier


def get_defense_modifier_for_personality(
    personality: str,
    stance: str,
    is_outnumbered: bool = False,
    is_holding: bool = False
) -> float:
    """
    Calculate personality-specific defense modifier.

    Args:
        personality: Marshal's personality
        stance: Current stance (neutral, defensive, aggressive)
        is_outnumbered: Whether marshal is outnumbered
        is_holding: Whether marshal is in hold position (Grouchy)

    Returns:
        Float multiplier (e.g., 1.15 = +15%)
    """
    modifier = 1.0
    mods = get_personality_modifiers(personality)

    if personality.lower() == "aggressive":
        # Ney: -5% additional defense in aggressive stance (total -15% with base -10%)
        if stance == "aggressive":
            modifier *= (1.0 - mods.get("aggressive_stance_defense_penalty", 0))

        # Ney: -5% off defensive stance bonus (gets +10% not +15%)
        # This is handled by returning a negative modifier that offsets the stance bonus
        if stance == "defensive":
            modifier *= (1.0 - mods.get("defensive_stance_defense_penalty", 0))

    elif personality.lower() == "cautious":
        # Davout: +5% additional defense in defensive stance (total +20%)
        if stance == "defensive":
            modifier *= (1.0 + mods.get("defensive_stance_defense_bonus", 0))

        # Davout: +10% defense when outnumbered
        if is_outnumbered:
            modifier *= (1.0 + mods.get("outnumbered_defense_bonus", 0))

    elif personality.lower() == "literal":
        # Grouchy: +15% defense when holding position (Immovable)
        if is_holding:
            modifier *= (1.0 + mods.get("hold_position_defense_bonus", 0))

    return modifier


def get_max_fortify_bonus(personality: str) -> float:
    """
    Get maximum fortification bonus for a personality.

    Args:
        personality: Marshal's personality

    Returns:
        Max fortify bonus as decimal (e.g., 0.15 = 15%)
    """
    mods = get_personality_modifiers(personality)

    if personality.lower() == "aggressive":
        return mods.get("max_fortify_bonus", 0.10)  # Ney: capped at 10%
    elif personality.lower() == "cautious":
        return mods.get("max_fortify_bonus", 0.20)  # Davout: up to 20%

    return 0.15  # Default: 15%


def get_fortify_rate(personality: str) -> float:
    """
    Get fortification rate per turn for a personality.

    Args:
        personality: Marshal's personality

    Returns:
        Fortify rate as decimal per turn (e.g., 0.02 = +2%)
    """
    base_rate = 0.02  # Default: +2% per turn

    if personality.lower() == "cautious":
        mods = get_personality_modifiers(personality)
        return base_rate + mods.get("fortify_rate_bonus", 0)  # Davout: +3% per turn

    return base_rate


def get_instant_fortify_bonus(personality: str) -> float:
    """
    Get instant fortify bonus on first fortify.

    Args:
        personality: Marshal's personality

    Returns:
        Instant bonus as decimal (e.g., 0.05 = +5%)
    """
    if personality.lower() == "cautious":
        mods = get_personality_modifiers(personality)
        return mods.get("instant_fortify_bonus", 0)  # Davout: +5% instant

    return 0.0  # Others: no instant bonus


def get_scout_range_bonus(personality: str) -> int:
    """
    Get scout range bonus for a personality.

    Args:
        personality: Marshal's personality

    Returns:
        Additional scout range in regions
    """
    if personality.lower() == "cautious":
        mods = get_personality_modifiers(personality)
        return mods.get("scout_range_bonus", 0)  # Davout: +1 region

    return 0


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("PERSONALITY MODIFIERS TEST")
    print("=" * 60)

    print("\n--- NEY (Aggressive) ---")
    print(f"Attack (neutral): {get_attack_modifier_for_personality('aggressive', 'neutral'):.2f}x")
    print(f"Attack (aggressive): {get_attack_modifier_for_personality('aggressive', 'aggressive'):.2f}x")
    print(f"Attack (aggressive + drill): {get_attack_modifier_for_personality('aggressive', 'aggressive', True):.2f}x")
    print(f"Defense (aggressive): {get_defense_modifier_for_personality('aggressive', 'aggressive'):.2f}x")
    print(f"Defense (defensive): {get_defense_modifier_for_personality('aggressive', 'defensive'):.2f}x")
    print(f"Max fortify: {get_max_fortify_bonus('aggressive'):.0%}")

    print("\n--- DAVOUT (Cautious) ---")
    print(f"Attack (neutral): {get_attack_modifier_for_personality('cautious', 'neutral'):.2f}x")
    print(f"Attack (aggressive): {get_attack_modifier_for_personality('cautious', 'aggressive'):.2f}x")
    print(f"Attack (bad odds): {get_attack_modifier_for_personality('cautious', 'neutral', False, 0.8):.2f}x")
    print(f"Defense (defensive): {get_defense_modifier_for_personality('cautious', 'defensive'):.2f}x")
    print(f"Defense (outnumbered): {get_defense_modifier_for_personality('cautious', 'neutral', True):.2f}x")
    print(f"Max fortify: {get_max_fortify_bonus('cautious'):.0%}")
    print(f"Fortify rate: {get_fortify_rate('cautious'):.0%}/turn")
    print(f"Instant fortify: {get_instant_fortify_bonus('cautious'):.0%}")
    print(f"Scout range bonus: +{get_scout_range_bonus('cautious')}")

    print("\n--- GROUCHY (Literal) ---")
    print(f"Defense (neutral): {get_defense_modifier_for_personality('literal', 'neutral'):.2f}x")
    print(f"Defense (holding): {get_defense_modifier_for_personality('literal', 'neutral', False, True):.2f}x")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

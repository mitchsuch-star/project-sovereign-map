"""
Personality System for Project Sovereign (Phase 2 - Disobedience)

Defines marshal personalities and their objection triggers.
Each personality type has specific situations that trigger objections.
"""

from enum import Enum
from typing import Dict, Optional


class Personality(Enum):
    """Marshal personality types affecting objection behavior."""
    AGGRESSIVE = "aggressive"
    CAUTIOUS = "cautious"
    LITERAL = "literal"
    BALANCED = "balanced"
    LOYAL = "loyal"


# Personality descriptions for UI/narrative
PERSONALITY_DESCRIPTIONS = {
    Personality.AGGRESSIVE: {
        'name': 'Aggressive',
        'summary': 'Bold and attack-minded',
        'description': 'Prefers bold attacks and dislikes defensive orders. '
                      'Will object to waiting, defending, or retreat commands.',
        'strengths': ['Devastating attacks', 'High morale in offense', 'Pursuit bonuses'],
        'weaknesses': ['Poor at defense', 'May refuse cautious orders', 'Reckless'],
        'examples': ['Ney', 'Blucher', 'Murat'],
    },
    Personality.CAUTIOUS: {
        'name': 'Cautious',
        'summary': 'Methodical and analytical',
        'description': 'Prefers calculated actions and dislikes risky attacks. '
                      'Will object to attacking when outnumbered or without intelligence.',
        'strengths': ['Solid defense', 'Good logistics', 'Preserves army'],
        'weaknesses': ['May refuse aggressive orders', 'Slow to exploit openings'],
        'examples': ['Davout', 'Wellington', 'Kutuzov'],
    },
    Personality.LITERAL: {
        'name': 'Literal',
        'summary': 'Follows orders exactly',
        'description': 'Interprets orders literally and struggles with ambiguity. '
                      'Will ask for clarification but rarely disobeys.',
        'strengths': ['Reliable execution', 'No surprises'],
        'weaknesses': ['No initiative', 'May fail if orders become obsolete'],
        'examples': ['Grouchy'],
    },
    Personality.BALANCED: {
        'name': 'Balanced',
        'summary': 'Adaptable and reasonable',
        'description': 'Adapts to situations and objects only to truly dangerous orders. '
                      'Will object to suicidal orders or exposing the capital.',
        'strengths': ['Flexible', 'Good judgment', 'Moderate in all areas'],
        'weaknesses': ['No exceptional strengths'],
        'examples': ['Soult', 'Bernadotte'],
    },
    Personality.LOYAL: {
        'name': 'Loyal',
        'summary': 'Devoted to the Emperor',
        'description': 'Deeply loyal and trusts the Emperor\'s judgment. '
                      'Will follow dangerous orders with minimal objection.',
        'strengths': ['High obedience', 'Rarely objects', 'Morale bonus'],
        'weaknesses': ['May follow bad orders to ruin'],
        'examples': ['Lannes', 'Duroc'],
    },
}


# Personality trigger severities
# Maps (personality, situation) -> base severity for objection
# Severity 0.0-0.19 = no objection
# Severity 0.20-0.49 = mild objection (auto-resolve)
# Severity 0.50-0.95 = major objection (player choice required)

PERSONALITY_TRIGGERS: Dict[Personality, Dict[str, float]] = {
    Personality.AGGRESSIVE: {
        'defend': 0.60,              # Hates defensive orders
        'wait': 0.50,                # Hates waiting around (fixed from 0.55)
        'wait_with_enemy_nearby': 0.65,  # Really hates waiting when enemy is close
        'retreat': 0.70,             # Strongly objects to retreat
        'hold_position': 0.60,       # Major objection to holding (same as defend)
        'fortify': 0.55,             # "You want me to dig trenches like a coward?!"
        'drill_enemy_nearby': 0.45,  # Mild objection: "We should attack, not drill!"
        # STANCE TRIGGERS (Phase 2.7)
        'defensive_stance': 0.55,    # Objects to defensive posture
        'neutral_stance_from_aggressive': 0.35,  # Mild objection to backing off
    },

    Personality.CAUTIOUS: {
        'certain_death': 0.80,                # 5:1+ odds - very strong objection
        'attack_outnumbered_3to1': 0.70,      # Very bad odds - strong objection
        'attack_outnumbered_2to1': 0.60,      # Bad odds objection (fixed from 0.70)
        'attack_outnumbered_1_5to1': 0.50,    # Moderate objection to risky attacks
        'attack_without_intel': 0.55,         # TODO Phase 3: Requires fog of war system to detect unknown enemy strength
        'attack_fortified': 0.60,             # Objects to attacking fortifications
        'forced_march': 0.45,                 # Mild objection to exhausting troops
        # STANCE TRIGGERS (Phase 2.7)
        'aggressive_stance': 0.40,   # Objects to aggressive posture (fixed from 0.50)
        'aggressive_stance_outnumbered': 0.60,  # Strongly objects when outnumbered (fixed from 0.65)
    },

    Personality.LITERAL: {
        'ambiguous_order': 0.50,              # TODO Phase 3: Implement in analyze_order_situation() - LLM will detect unclear commands
        'contradictory_orders': 0.60,         # TODO Phase 3: Requires order history tracking to detect conflicting orders
        'change_of_plans': 0.35,              # TODO Phase 3: Requires order history to detect frequent changes
    },

    Personality.BALANCED: {
        'certain_death': 0.70,                # 5:1+ odds - strong objection
        'expose_capital': 0.55,               # Objects to leaving capital undefended
        'suicidal_order': 0.65,               # TODO Phase 3: Currently uses 3:1+ ratio. Expand to other suicidal scenarios
        'attack_outnumbered_3to1': 0.60,      # Objects to very bad odds
        'abandon_allies': 0.50,               # TODO Phase 3: Requires ally tracking system - detect when order leaves ally exposed
    },

    Personality.LOYAL: {
        'suicidal_order': 0.40,               # TODO Phase 3: Same as balanced - expand suicidal definition
        'certain_death': 0.55,                # Even loyal marshals object to impossible odds (5:1+)
        'betray_emperor': 0.95,               # TODO Phase 3 (1805): Political intrigue system - detect orders harming Napoleon's interests
        'expose_capital': 0.35,               # Mild concern but trusts Emperor
    },
}


def get_personality(personality_str: str) -> Personality:
    """
    Convert personality string to Personality enum.

    Args:
        personality_str: String like "aggressive", "cautious", etc.

    Returns:
        Personality enum value
    """
    try:
        return Personality(personality_str.lower())
    except ValueError:
        # Default to balanced if unknown
        return Personality.BALANCED


def get_base_severity(personality: Personality, situation: str) -> Optional[float]:
    """
    Get base objection severity for a personality and situation.

    Args:
        personality: Personality enum
        situation: Situation key string

    Returns:
        Base severity (0.0-1.0) or None if no trigger
    """
    triggers = PERSONALITY_TRIGGERS.get(personality, {})
    return triggers.get(situation)


def analyze_order_situation(order: Dict, marshal, game_state) -> Optional[str]:
    """
    Analyze an order to determine the situation type.

    This function examines the order and game context to identify
    which personality trigger (if any) applies.

    Currently implemented:
    - defend, wait, wait_with_enemy_nearby, hold_position, retreat, fortify
    - attack_outnumbered_2to1, attack_outnumbered_1_5to1, attack_outnumbered_3to1
    - attack_fortified, forced_march, expose_capital

    TODO Phase 3 - Not yet implemented:
    - ambiguous_order: Requires LLM to detect unclear commands
    - contradictory_orders: Requires order history tracking
    - change_of_plans: Requires order history tracking
    - attack_without_intel: Requires fog of war system
    - suicidal_order (expanded): Currently only checks ratios
    - abandon_allies: Requires ally position tracking
    - betray_emperor: Requires political intrigue system (1805)

    Args:
        order: Order dict with 'action', 'target', etc.
        marshal: Marshal receiving the order
        game_state: Current game state

    Returns:
        Situation string or None if no triggering situation
    """
    action = order.get('action', '').lower()
    target = order.get('target')

    # Check for defend/wait/hold situations (aggressive triggers)
    if action == 'defend':
        return 'defend'

    # Hold = "hold the line" - similar to defend but milder objection
    # This is distinct from wait - hold is an alias for defend mechanics
    if action == 'hold':
        # Check if enemy is nearby - more urgent "hold the line" situation
        if _enemy_nearby(marshal, game_state):
            return 'hold_position'  # Mild objection even with enemy nearby
        return 'hold_position'

    # Wait = pass turn, do nothing (free action)
    if action == 'wait':
        # Check if enemy is nearby - aggressive marshals HATE waiting with enemy close
        if _enemy_nearby(marshal, game_state):
            return 'wait_with_enemy_nearby'
        return 'wait'

    # Check for attack situations (cautious triggers)
    if action == 'attack':
        strength_ratio = _get_strength_ratio(marshal, target, game_state)
        if strength_ratio is not None:
            if strength_ratio <= 0.20:  # 5:1+ outnumbered - certain death
                return 'certain_death'
            if strength_ratio <= 0.33:  # 3:1 outnumbered
                return 'attack_outnumbered_3to1'
            if strength_ratio <= 0.5:   # 2:1 outnumbered
                return 'attack_outnumbered_2to1'
            if strength_ratio <= 0.67:  # 1.5:1 outnumbered
                return 'attack_outnumbered_1_5to1'

        # Check if attacking fortified position
        if _is_fortified(target, game_state):
            return 'attack_fortified'

    # Check for retreat
    if action == 'retreat':
        return 'retreat'

    # Check for fortify (aggressive trigger)
    if action == 'fortify':
        return 'fortify'

    # Check for drill with enemy nearby (aggressive trigger)
    if action == 'drill':
        if _enemy_nearby(marshal, game_state):
            return 'drill_enemy_nearby'

    # Check for capital exposure (balanced trigger)
    if action == 'move' and _exposes_capital(marshal, target, game_state):
        return 'expose_capital'

    # Check for forced march
    if action == 'forced_march':
        return 'forced_march'

    # ════════════════════════════════════════════════════════════
    # STANCE CHANGE TRIGGERS (Phase 2.7)
    # ════════════════════════════════════════════════════════════
    if action == 'stance_change':
        target_stance = order.get('target_stance', '').lower()
        current_stance = getattr(marshal, 'stance', None)
        current_stance_str = current_stance.value if current_stance else 'neutral'

        # Aggressive marshal ordered to defensive stance
        if target_stance in ('defensive', 'defense', 'defend'):
            return 'defensive_stance'

        # Aggressive marshal ordered from aggressive back to neutral
        if target_stance == 'neutral' and current_stance_str == 'aggressive':
            return 'neutral_stance_from_aggressive'

        # Cautious marshal ordered to aggressive stance
        if target_stance in ('aggressive', 'attack', 'offense'):
            # Check if outnumbered
            strength_ratio = _get_enemy_strength_ratio(marshal, game_state)
            if strength_ratio is not None and strength_ratio < 0.67:
                return 'aggressive_stance_outnumbered'
            return 'aggressive_stance'

    return None


def _enemy_nearby(marshal, game_state) -> bool:
    """Check if an enemy is in an adjacent region."""
    if game_state is None:
        return False

    world = getattr(game_state, 'world', game_state)
    if not hasattr(world, 'regions') or not hasattr(world, 'marshals'):
        return False

    current_region = world.regions.get(marshal.location)
    if not current_region:
        return False

    for adj_name in current_region.adjacent_regions:  # FIX: was .adjacent (wrong attribute)
        for m in world.marshals.values():
            if m.location == adj_name and m.nation != marshal.nation:
                return True
    return False


def _get_strength_ratio(marshal, target, game_state) -> Optional[float]:
    """Get strength ratio (attacker/defender)."""
    if game_state is None or target is None:
        return None

    world = getattr(game_state, 'world', game_state)
    if not hasattr(world, 'marshals'):
        return None

    # Find enemy in target region
    enemy = None
    for m in world.marshals.values():
        if m.name == target or m.location == target:
            if m.nation != marshal.nation:
                enemy = m
                break

    if enemy is None:
        return None

    if enemy.strength == 0:
        return float('inf')

    return marshal.strength / enemy.strength


def _is_fortified(target, game_state) -> bool:
    """Check if target region is fortified."""
    if game_state is None:
        return False

    world = getattr(game_state, 'world', game_state)
    if not hasattr(world, 'regions'):
        return False

    region = world.regions.get(target)
    if region and hasattr(region, 'fortified'):
        return region.fortified
    return False


def _exposes_capital(marshal, target, game_state) -> bool:
    """Check if moving to target exposes the capital."""
    if game_state is None:
        return False

    world = getattr(game_state, 'world', game_state)

    # Check if marshal is currently defending capital
    capital = "Paris"  # France's capital
    if marshal.location != capital:
        return False

    # Check if any other friendly marshal is at capital
    for m in world.marshals.values():
        if m.name != marshal.name and m.location == capital and m.nation == marshal.nation:
            return False  # Another friendly is defending

    # Moving away from capital with no other defender
    return True


def _get_enemy_strength_ratio(marshal, game_state) -> Optional[float]:
    """
    Get strength ratio against nearest enemy.

    Returns marshal.strength / nearest_enemy.strength
    Returns None if no enemy nearby.
    """
    if game_state is None:
        return None

    world = getattr(game_state, 'world', game_state)
    if not hasattr(world, 'marshals') or not hasattr(world, 'regions'):
        return None

    # Find nearest enemy
    nearest_enemy = None
    min_distance = float('inf')

    for m in world.marshals.values():
        if m.nation != marshal.nation and m.strength > 0:
            dist = world.get_distance(marshal.location, m.location) if hasattr(world, 'get_distance') else 999
            if dist < min_distance:
                min_distance = dist
                nearest_enemy = m

    if nearest_enemy is None or nearest_enemy.strength == 0:
        return None

    return marshal.strength / nearest_enemy.strength


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("PERSONALITY SYSTEM TEST")
    print("=" * 60)

    for personality in Personality:
        desc = PERSONALITY_DESCRIPTIONS.get(personality, {})
        print(f"\n{personality.value.upper()}: {desc.get('summary', '')}")
        print(f"  {desc.get('description', '')}")

        triggers = PERSONALITY_TRIGGERS.get(personality, {})
        if triggers:
            print("  Triggers:")
            for situation, severity in triggers.items():
                level = "MAJOR" if severity >= 0.50 else "mild"
                print(f"    - {situation}: {severity:.0%} ({level})")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

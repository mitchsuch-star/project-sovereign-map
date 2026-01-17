"""
Severity Calculator for Project Sovereign (Phase 2 - Disobedience)

Calculates objection severity based on:
- Base severity from personality triggers
- Trust level modifier
- Vindication score modifier
- Recent performance modifier
- Recent override history
- Authority modifier

Final severity determines objection type:
- < 0.20: No objection
- 0.20-0.49: Mild objection (auto-resolve with grumbling)
- 0.50-0.95: Major objection (player choice required)
"""

import random
from typing import Dict, Optional, Tuple
from backend.models.personality import (
    Personality, get_personality, get_base_severity, analyze_order_situation
)


def calculate_objection_severity(
    marshal,
    order: Dict,
    game_state,
    include_variance: bool = True
) -> float:
    """
    Calculate objection severity for a given order.

    Formula:
    1. Get base severity from personality trigger
    2. Apply multiplicative modifiers:
       - Trust modifier (low trust = higher severity)
       - Vindication modifier (proven right = higher severity)
       - Performance modifier (winning streak = lower severity)
       - Override modifier (frequently overridden = higher severity)
       - Authority modifier (low authority = higher severity)
    3. Apply tiered variance based on severity level
    4. Cap at 0.95

    Args:
        marshal: Marshal receiving the order
        order: Order dict with action, target, etc.
        game_state: Current game state
        include_variance: Whether to add random variance (for testing)

    Returns:
        Severity value (0.0 to 0.95)
    """
    # Step 1: Get base severity from personality trigger
    personality = get_personality(marshal.personality)
    situation = analyze_order_situation(order, marshal, game_state)

    if situation is None:
        return 0.0  # No triggering situation

    base_severity = get_base_severity(personality, situation)
    if base_severity is None:
        return 0.0  # Personality doesn't trigger on this situation

    severity = base_severity

    # Step 2: Apply multiplicative modifiers

    # 2a: Trust modifier (inverse - low trust = high modifier)
    trust_modifier = get_trust_modifier(marshal)
    severity *= trust_modifier

    # 2b: Vindication modifier (been proven right = more bold)
    vindication_modifier = get_vindication_modifier(marshal)
    severity *= vindication_modifier

    # 2c: Performance modifier (winning = less objection)
    performance_modifier = get_performance_modifier(marshal)
    severity *= performance_modifier

    # 2d: Override modifier (frequently overridden = more objection)
    override_modifier = get_override_modifier(marshal)
    severity *= override_modifier

    # 2e: Authority modifier (from game state)
    authority_modifier = get_authority_modifier(game_state)
    severity *= authority_modifier

    # Step 3: Apply tiered variance
    if include_variance:
        severity = apply_variance(severity)

    # Step 4: Cap at 0.95
    severity = min(0.95, max(0.0, severity))

    return severity


def get_trust_modifier(marshal) -> float:
    """
    Get severity modifier based on marshal trust.

    Low trust = marshal more likely to object (higher severity)
    High trust = marshal trusts player judgment (lower severity)

    4-tier steep curve per design spec:
    Trust 80+: 0.7x (very trusting, much less likely to object)
    Trust 40-79: 1.0x (neutral baseline)
    Trust 20-39: 1.3x (distrustful, more likely to object)
    Trust <20: 1.6x (very distrustful, much more likely to object)
    """
    # Get trust value
    if hasattr(marshal, 'trust'):
        trust_value = marshal.trust.value if hasattr(marshal.trust, 'value') else int(marshal.trust)
    else:
        trust_value = 70  # Default

    if trust_value >= 80:
        return 0.7
    elif trust_value >= 40:
        return 1.0
    elif trust_value >= 20:
        return 1.3
    else:
        return 1.6


def get_vindication_modifier(marshal) -> float:
    """
    Get severity modifier based on vindication score.

    Positive vindication = marshal proven right before = more bold in objecting
    Negative vindication = marshal proven wrong = less bold

    Simplified 3-tier system per design spec:
    Vindication ≤-2: 0.85x (been proven wrong, less bold)
    Vindication -1 to +2: 1.0x (neutral)
    Vindication ≥+3: 1.15x (been proven right, bolder)
    """
    vindication = getattr(marshal, 'vindication_score', 0)

    if vindication <= -2:
        return 0.85
    elif vindication <= 2:
        return 1.0
    else:
        return 1.15


def get_performance_modifier(marshal) -> float:
    """
    Get severity modifier based on recent battle performance.

    Winning streak = marshal confident in current approach
    Losing streak = marshal may question orders

    Uses recent_battles list: ['victory', 'victory', 'defeat']
    """
    recent = getattr(marshal, 'recent_battles', [])
    if not recent:
        return 1.0

    # Count victories and defeats in last 3 battles
    recent_3 = recent[-3:]
    victories = recent_3.count('victory')
    defeats = recent_3.count('defeat')

    if victories >= 2:
        return 0.85  # Winning, less objection
    elif defeats >= 2:
        return 1.15  # Losing, more questioning
    else:
        return 1.0


def get_override_modifier(marshal) -> float:
    """
    Get severity modifier based on recent overrides.

    Frequently overridden = marshal resentful, objects more
    Rarely overridden = marshal respected, objects less

    Uses recent_overrides list of booleans
    """
    recent = getattr(marshal, 'recent_overrides', [])
    if not recent:
        return 1.0

    # Count overrides in last 5 decisions
    recent_5 = recent[-5:]
    override_count = sum(1 for x in recent_5 if x)

    if override_count >= 4:
        return 1.3  # Frequently overridden, resentful
    elif override_count >= 2:
        return 1.1  # Sometimes overridden
    else:
        return 1.0  # Rarely overridden


def get_authority_modifier(game_state) -> float:
    """
    Get severity modifier from Napoleon's authority level.

    Low authority = marshals object more boldly.
    """
    if game_state is None:
        return 1.0

    # Try to get authority tracker from game state
    if hasattr(game_state, 'authority_tracker'):
        return game_state.authority_tracker.get_severity_modifier()
    elif hasattr(game_state, 'world') and hasattr(game_state.world, 'authority_tracker'):
        return game_state.world.authority_tracker.get_severity_modifier()

    return 1.0


def apply_variance(severity: float) -> float:
    """
    Apply tiered random variance to severity.

    Low severity (0.20-0.35): ±3% variance (predictable)
    Medium severity (0.35-0.60): ±8% variance (moderate)
    High severity (0.60+): ±12% variance (unpredictable)

    This makes objection outcomes somewhat unpredictable while
    keeping the general trend based on modifiers.
    """
    if severity < 0.20:
        # Below objection threshold, no variance needed
        return severity
    elif severity < 0.35:
        variance_range = 0.03
    elif severity < 0.60:
        variance_range = 0.08
    else:
        variance_range = 0.12

    variance = random.uniform(-variance_range, variance_range)
    return severity + variance


def get_severity_label(severity: float) -> str:
    """
    Get human-readable label for severity level.

    Args:
        severity: Severity value (0.0 to 1.0)

    Returns:
        Label string
    """
    if severity < 0.20:
        return "Compliant"
    elif severity < 0.35:
        return "Mild Concern"
    elif severity < 0.50:
        return "Objecting"
    elif severity < 0.70:
        return "Strongly Objecting"
    elif severity < 0.85:
        return "Refusing"
    else:
        return "Outright Defiance"


def get_severity_breakdown(marshal, order: Dict, game_state) -> Dict:
    """
    Get detailed breakdown of severity calculation.

    Useful for debugging and UI display.

    Returns:
        Dict with all modifiers and calculations
    """
    personality = get_personality(marshal.personality)
    situation = analyze_order_situation(order, marshal, game_state)

    base_severity = 0.0 if situation is None else (get_base_severity(personality, situation) or 0.0)

    modifiers = {
        'trust': get_trust_modifier(marshal),
        'vindication': get_vindication_modifier(marshal),
        'performance': get_performance_modifier(marshal),
        'override': get_override_modifier(marshal),
        'authority': get_authority_modifier(game_state),
    }

    # Calculate without variance
    final = base_severity
    for mod in modifiers.values():
        final *= mod
    final = min(0.95, max(0.0, final))

    return {
        'personality': personality.value,
        'situation': situation,
        'base_severity': base_severity,
        'modifiers': modifiers,
        'final_severity': final,
        'label': get_severity_label(final),
        'will_object': final >= 0.20,
        'is_major': final >= 0.50,
    }


# Test code
if __name__ == "__main__":
    from backend.models.marshal import create_starting_marshals
    from backend.models.trust import Trust

    print("=" * 60)
    print("SEVERITY CALCULATOR TEST")
    print("=" * 60)

    marshals = create_starting_marshals()
    ney = marshals["Ney"]

    # Add trust and other attributes for testing
    ney.trust = Trust(70)
    ney.vindication_score = 0
    ney.recent_battles = []
    ney.recent_overrides = []

    # Test defend order (Ney should object)
    defend_order = {'action': 'defend', 'target': 'Belgium'}

    print(f"\nTesting: {ney.name} ({ney.personality}) receives defend order")
    breakdown = get_severity_breakdown(ney, defend_order, None)

    print(f"Situation: {breakdown['situation']}")
    print(f"Base severity: {breakdown['base_severity']:.2f}")
    print("Modifiers:")
    for name, value in breakdown['modifiers'].items():
        print(f"  {name}: {value:.2f}")
    print(f"Final severity: {breakdown['final_severity']:.2f}")
    print(f"Label: {breakdown['label']}")
    print(f"Will object: {breakdown['will_object']}")
    print(f"Is major objection: {breakdown['is_major']}")

    # Test attack order (Ney should be happy)
    print("\n" + "-" * 40)
    attack_order = {'action': 'attack', 'target': 'Wellington'}

    print(f"\nTesting: {ney.name} ({ney.personality}) receives attack order")
    breakdown = get_severity_breakdown(ney, attack_order, None)

    print(f"Situation: {breakdown['situation']}")
    print(f"Base severity: {breakdown['base_severity']:.2f}")
    print(f"Will object: {breakdown['will_object']}")

    # Test Davout with attack order when outnumbered
    print("\n" + "-" * 40)
    davout = marshals["Davout"]
    davout.trust = Trust(70)
    davout.vindication_score = 0
    davout.recent_battles = []
    davout.recent_overrides = []

    # Create mock game state with enemy
    class MockGameState:
        class World:
            marshals = {
                "Wellington": type('Marshal', (), {
                    'name': 'Wellington',
                    'location': 'Waterloo',
                    'nation': 'Britain',
                    'strength': 100000  # Much larger force
                })()
            }
            regions = {}
        world = World()

    davout.strength = 48000  # Outnumbered ~2:1

    print(f"\nTesting: {davout.name} ({davout.personality}) ordered to attack superior force")
    breakdown = get_severity_breakdown(davout, {'action': 'attack', 'target': 'Wellington'}, MockGameState())

    print(f"Situation: {breakdown['situation']}")
    print(f"Base severity: {breakdown['base_severity']:.2f}")
    print(f"Final severity: {breakdown['final_severity']:.2f}")
    print(f"Label: {breakdown['label']}")
    print(f"Will object: {breakdown['will_object']}")
    print(f"Is major objection: {breakdown['is_major']}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

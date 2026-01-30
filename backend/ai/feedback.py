"""
Immersive feedback generation for command scoring.

Converts numeric scores (ambiguity, strategic_score) into narrative
phrases that teach players the system without breaking immersion.

CRITICAL: Never expose raw numbers to players!

NOTE: This module currently handles TACTICAL commands only.
NOTE: Phase 5.2 strategic feedback not yet differentiated from tactical. Future improvement:
- Add get_strategic_order_feedback() for multi-turn commands
- Consider different thresholds for strategic vs tactical
- Handle feedback timing (start of order? completion? each turn?)
"""

from typing import Dict


def get_strategic_feedback(score: int, marshal_name: str) -> str:
    """
    Convert strategic score to immersive phrase.

    Args:
        score: Strategic score from LLM (0-100)
        marshal_name: Name of the marshal for personalized message

    Returns:
        Immersive feedback string (empty for low scores)

    Thresholds:
    - 76-100: "Your words stirred {marshal_name}'s heart!"
    - 51-75: "{marshal_name} was inspired by your words."
    - 26-50: "A sound order."
    - 0-25: "" (empty string, no comment)
    """
    # Null check
    if score is None:
        score = 0

    if score >= 76:
        return f"Your words stirred {marshal_name}'s heart!"
    if score >= 51:
        return f"{marshal_name} was inspired by your words."
    if score >= 26:
        return "A sound order."
    return ""


def get_ambiguity_feedback(score: int, marshal_name: str, personality: str) -> str:
    """
    Convert ambiguity score to immersive phrase.

    Args:
        score: Ambiguity score from LLM (0-100, higher = more ambiguous)
        marshal_name: Name of the marshal for personalized message
        personality: Marshal's personality type (aggressive, cautious, literal, etc.)

    Returns:
        Immersive feedback string describing how clearly the order was understood

    Thresholds:
    - 0-20: "Your orders were crystal clear."
    - 21-40: "Your intent was understood."
    - 41-60: Personality-specific message
    - 61-75: "{marshal_name} wasn't entirely certain of your intent."
    - 76-100: "Your orders were unclear."

    Personality messages for 41-60 range:
    - aggressive: "{marshal_name} interpreted this as a call to arms."
    - cautious: "{marshal_name} took a measured interpretation."
    - literal: "{marshal_name} followed your exact words."
    - default: "{marshal_name} interpreted your meaning."
    """
    # Null checks
    if score is None:
        score = 0
    if personality is None:
        personality = "balanced"

    if score <= 20:
        return "Your orders were crystal clear."
    if score <= 40:
        return "Your intent was understood."
    if score <= 60:
        # Personality-specific interpretation message
        if personality == "aggressive":
            return f"{marshal_name} interpreted this as a call to arms."
        if personality == "cautious":
            return f"{marshal_name} took a measured interpretation."
        if personality == "literal":
            return f"{marshal_name} followed your exact words."
        # Default for balanced, loyal, or unknown personalities
        return f"{marshal_name} interpreted your meaning."
    if score <= 75:
        return f"{marshal_name} wasn't entirely certain of your intent."
    return "Your orders were unclear."


def get_bonuses_for_score(score: int) -> Dict[str, int]:
    """
    Return bonus dict for a strategic score.

    Args:
        score: Strategic score from LLM (0-100)

    Returns:
        Dict with keys: morale, trust, combat
        - 76-100: {"morale": 15, "trust": 3, "combat": 10}
        - 51-75: {"morale": 10, "trust": 2, "combat": 5}
        - 26-50: {"morale": 5, "trust": 1, "combat": 0}
        - 0-25: {"morale": 0, "trust": 0, "combat": 0}
    """
    # Null check
    if score is None:
        score = 0

    if score >= 76:
        return {"morale": 15, "trust": 3, "combat": 10}
    if score >= 51:
        return {"morale": 10, "trust": 2, "combat": 5}
    if score >= 26:
        return {"morale": 5, "trust": 1, "combat": 0}
    return {"morale": 0, "trust": 0, "combat": 0}


def apply_strategic_bonuses(marshal, strategic_score: int, is_combat_action: bool = False) -> Dict[str, int]:
    """
    Apply morale and trust bonuses to marshal. Optionally set combat bonus.

    Args:
        marshal: Marshal object to modify
        strategic_score: Score from LLM (0-100)
        is_combat_action: If True, also set strategic_combat_bonus

    Returns:
        The bonuses dict that was applied

    NOTE: Only call for PLAYER actions, not enemy AI.
    Enemy AI doesn't use LLM scoring and shouldn't receive these bonuses.

    NOTE: Phase 5.2 strategic feedback not yet differentiated from tactical. Future improvement:
    When command_type == "strategic", use different bonus logic:
    - apply_strategic_order_bonuses(marshal, score, standing_order, condition)
    - Handle multi-turn persistence differently
    """
    bonuses = get_bonuses_for_score(strategic_score)

    # Apply morale bonus (cap at 100)
    if bonuses["morale"] > 0:
        marshal.morale = min(100, marshal.morale + bonuses["morale"])

    # Apply trust bonus (Trust class handles capping)
    if bonuses["trust"] > 0:
        marshal.trust.modify(bonuses["trust"])

    # Set combat bonus only for combat actions (attack, charge)
    # This will be consumed in get_attack_modifier()
    if is_combat_action and bonuses["combat"] > 0:
        marshal.strategic_combat_bonus = bonuses["combat"]

    return bonuses

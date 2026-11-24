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


def a_courts_bonus_rides_its_own_act() -> bool:
    """WS-R4 (row FR, Session FR-2 — the weak-spot readers' find 4): a court's
    attack is judged BEFORE it runs (`EnemyAI._judge_the_attack_first`), so the
    combat bonus its judgement earns is spent by the very attack it judged —
    what this module's own words promise ("consumed in get_attack_modifier()")
    and what the turn-end expiry's comment always assumed. Before, the court
    scored the attack AFTER it had run and the bonus waited for that marshal's
    next attack, however many turns later. With it, the turn-end expiry
    (GRD-33's rule: never banked for a battle turns later) covers every
    holder, so an attack refused before its blow banks nothing overnight.
    One line to reverse: return False."""
    return True


def set_combat_bonus(marshal, strategic_score: int) -> int:
    """WS-R4: the combat half of the score's bonuses, set before the attack it
    rewards (its morale and trust follow the act, `apply_strategic_bonuses`
    with `is_combat_action=False`). Returns the bonus set (0 for none)."""
    combat = int(get_bonuses_for_score(strategic_score)["combat"])
    if combat > 0:
        marshal.strategic_combat_bonus = combat
    return combat


def apply_strategic_bonuses(marshal, strategic_score: int, is_combat_action: bool = False) -> Dict[str, int]:
    """
    Apply morale and trust bonuses to marshal. Optionally set combat bonus.

    Args:
        marshal: Marshal object to modify
        strategic_score: the score (0-100)
        is_combat_action: If True, also set strategic_combat_bonus

    Returns:
        The bonuses dict that was applied

    Since WS-12 (row IC, Session 2: no number a model wrote reaches a marshal)
    the courts are this function's only callers, scored by the AI's own formula
    (`enemy_ai.calculate_ai_strategic_score`). Since WS-R4 (row FR, Session
    FR-2) a court's combat bonus is set BEFORE the attack it rewards
    (`set_combat_bonus`) and this function follows a successful act with its
    morale and trust only; with the seam down the old order returns.
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

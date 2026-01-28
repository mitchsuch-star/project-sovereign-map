"""
Validation layer for LLM parse results.
Ensures LLM can't hallucinate invalid marshals, actions, or targets.

This layer sits between LLM response and command execution to:
1. Clamp scores to valid ranges
2. Reject invalid marshals/actions
3. Clear invalid targets (let executor handle)
4. Block unimplemented features with friendly messages
"""

from typing import List, Set
from .schemas import ParseResult


# =============================================================================
# VALID GAME ENTITIES
# =============================================================================

# Actions that require marshal + validation
VALID_ACTIONS: Set[str] = {
    "attack",
    "defend",
    "hold",       # Alias for defend, executor handles
    "wait",       # Free action, pass turn
    "move",
    "scout",
    "retreat",
    "drill",
    "fortify",
    "unfortify",
    "stance_change",
    "recruit",
    "charge",     # Cavalry recklessness
    "restrain",   # Restrain reckless cavalry
}

# Meta actions that bypass validation entirely
META_ACTIONS: Set[str] = {
    "help",
    "end_turn",
    "debug",
    "status",
    "unknown",  # Failed parse, let executor handle error message
}

# Valid stances for stance_change action
VALID_STANCES: Set[str] = {
    "aggressive",
    "defensive",
    "neutral",
}


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_parse_result(
    result: ParseResult,
    valid_marshals: List[str],
    valid_regions: List[str],
    valid_targets: List[str],  # regions + enemy marshals
) -> ParseResult:
    """
    Validate and sanitize LLM parse result.

    Validation rules:
    - Meta actions (help, debug, etc.) → bypass validation
    - Invalid marshals → matched=False + suggestion
    - Multi-marshal commands → "coming soon"
    - Strategic commands → "coming soon"
    - Invalid actions → matched=False + suggestion
    - Invalid target_stance → matched=False + suggestion
    - Invalid targets → cleared silently (executor picks)
    - Scores → clamped 0-100

    Args:
        result: ParseResult from LLM
        valid_marshals: List of marshal names in game
        valid_regions: List of region names in game
        valid_targets: Combined list of regions + enemy marshals

    Returns:
        Validated/corrected ParseResult (mutated in place)
    """
    # Meta actions bypass validation
    if result.action in META_ACTIONS:
        return result

    # Clamp scores to valid range
    result.ambiguity = max(0, min(100, result.ambiguity))
    result.strategic_score = max(0, min(100, result.strategic_score))

    # Convert valid lists to sets for O(1) lookup
    marshal_set = set(valid_marshals)
    target_set = set(valid_targets)

    # Validate marshals exist
    if result.marshals:
        invalid_marshals = [m for m in result.marshals if m not in marshal_set]
        if invalid_marshals:
            result.matched = False
            available = ", ".join(valid_marshals[:3])
            if len(valid_marshals) > 3:
                available += "..."
            result.suggestion = f"Unknown marshal: {invalid_marshals[0]}. Available: {available}"
            return result

    # Multi-marshal commands: not yet implemented
    if result.marshals and len(result.marshals) > 1:
        result.matched = False
        result.suggestion = "Multi-marshal commands coming in a future update!"
        return result

    # Phase 5.2: Strategic commands now supported — pass through for executor handling
    # Note: command_type="strategic", condition, and standing_order are all valid now

    # Validate action is known
    if result.action and result.action not in VALID_ACTIONS:
        result.matched = False
        result.suggestion = f"Unknown action: {result.action}. Try: attack, move, defend, scout, fortify, drill"
        return result

    # Validate stance for stance_change action
    if result.action == "stance_change":
        if result.target_stance and result.target_stance not in VALID_STANCES:
            result.matched = False
            result.suggestion = f"Unknown stance: {result.target_stance}. Use: aggressive, defensive, or neutral"
            return result

    # Clear invalid targets silently (let executor/personality pick)
    if result.target and result.target not in target_set:
        result.target = None

    return result


def get_ambiguity_behavior(ambiguity: int) -> str:
    """
    Determine how to handle command based on ambiguity score.

    Thresholds:
    - 0-20: Clear command, execute as parsed
    - 21-75: Ambiguous, let marshal personality interpret
    - 76-100: Too vague, ask player for clarification

    Args:
        ambiguity: Score from 0-100

    Returns:
        One of: 'clear', 'personality', 'unparseable'
    """
    if ambiguity <= 20:
        return "clear"
    elif ambiguity <= 75:
        return "personality"
    else:
        return "unparseable"


def should_skip_validation(result: ParseResult) -> bool:
    """
    Check if this result should bypass validation entirely.

    Returns True for:
    - Meta actions (help, debug, end_turn, status)
    - Debug command type
    - Already failed parse (matched=False)
    """
    if result.action in META_ACTIONS:
        return True
    if result.type == "debug":
        return True
    if result.command_type == "debug":
        return True
    return False

"""
Defiance System for Project Sovereign (V2b Session 1)

Post-insist event: after player sees MODERATE/STRONG/EXTREME objection and insists,
the marshal may defy the order and act on their own judgment.

Three core functions:
- calculate_defiance_chance(): probability of defiance (0.0-0.40)
- get_defiant_action(): what the marshal does instead (fallback table)
- defiance_succeeded(): was the marshal RIGHT? (True/False/None)

Plus Berthier flavor text templates for all four outcome categories.
"""

import random
from typing import Optional

from backend.commands.objection_v2 import ConcernLevel

# ══════════════════════════════════════════════════════════════════════
# PT-C1 — the surcharge for obeying resentfully, named.
#
# It was an anonymous `-3` applied inside `apply_defiance_outcome`, on
# top of the `insist_penalty` the button quoted. Nothing disclosed it:
# the failed-roll result never writes `"defiance": True`, and
# `main.gd:3198` gates the only `trust_change` render in the entire
# client on exactly that key — so the branch that would have shown the
# number is unreachable on the path that charges it.
#
# It is not an edge case. `calculate_defiance_chance` is 0.05 at
# MODERATE, so the failed roll — the branch carrying this surcharge —
# is what happens 95% of the time.
#
# Measured consequence: Bernadotte at trust 17 lands on 2 at the quoted
# -15 and on 0 at the real -18, and 0 is what fires the redemption event
# that PT-B1 then destroyed. Which is why the spec says fix them
# together — the second bug hid the first.
# ══════════════════════════════════════════════════════════════════════
RELUCTANT_OBEDIENCE_PENALTY = -3


def calculate_defiance_chance(marshal, concern_level, world) -> float:
    """Calculate probability of marshal defying a direct order.

    Fires on MODERATE/STRONG/EXTREME concerns after player insists.
    Returns 0.0-0.40 (hard-capped).

    Args:
        marshal: The marshal who might defy
        concern_level: ConcernLevel enum value
        world: WorldState for authority/turn data

    Returns:
        Float probability (0.0 to 0.40)
    """
    if concern_level < ConcernLevel.MODERATE:
        return 0.0

    # Cooldown check
    if world.current_turn < marshal.defiance_cooldown_until:
        return 0.0

    # Literal personality never defies (Grouchy bypass)
    if getattr(marshal, 'personality', '') == 'literal':
        return 0.0

    # Base chances
    if concern_level == ConcernLevel.MODERATE:
        base = 0.05  # 5%
    elif concern_level == ConcernLevel.STRONG:
        base = 0.15  # 15%
    else:  # EXTREME
        base = 0.35  # 35%

    # MC-1: Bernadotte's "Eyes on a Crown" — +10pp after insisted objections
    # (5/15/35 -> 15/25/40-capped; the 0.40 hard cap below still holds).
    if (hasattr(marshal, 'ability')
            and marshal.ability.get("name") == "Eyes on a Crown"):
        base += 0.10

    # Vindication modifier: +10% per stack
    vindication_score = getattr(marshal, 'vindication_score', 0)
    vindication_mod = vindication_score * 0.10

    # Authority modifier (simpler tiers than AuthorityTracker methods)
    # Uses world.authority_tracker.authority (int, 0-100)
    # SEPARATE from get_obedience_modifier/get_severity_modifier — two systems, two purposes.
    authority = world.authority_tracker.authority
    if authority >= 80:
        authority_mod = -0.10  # Strong leader suppresses defiance
    elif authority < 50:
        authority_mod = +0.10  # Weak leader emboldens defiance
    else:
        authority_mod = 0.0

    # Trust tier modifier (narrower thresholds than V2a's TrustTier enum)
    trust = marshal.trust.value
    if trust <= 20:
        trust_mod = +0.15
    elif trust >= 80:
        trust_mod = -0.10
    else:
        trust_mod = 0.0

    # Variance band: prevents memorized thresholds
    variance = random.uniform(-0.08, 0.08)

    # Hard cap at 40%
    final = base + vindication_mod + authority_mod + trust_mod + variance
    return min(0.40, max(0.0, final))


def get_defiant_action(marshal, original_action: str) -> Optional[str]:
    """Get the action a marshal would take when defying orders.

    Uses the fallback table from V2b spec. Aggressive marshals attack,
    cautious marshals fortify, literal marshals never defy.

    Args:
        marshal: The defiant marshal
        original_action: The action the player ordered (lowercase)

    Returns:
        Action string ("attack", "fortify", "wait") or None if marshal can't defy
    """
    personality = getattr(marshal, 'personality', '')

    if personality == 'literal':
        return None  # Literal never defies

    if personality == 'aggressive':
        # Aggressive defiance: attack when ordered to do something defensive/passive
        # Map per fallback table — aggressive wouldn't object to attack
        if original_action in ("defend", "fortify", "hold", "wait", "retreat",
                               "SUPPORT", "MOVE_TO"):
            # Artillery routes to bombardment instead of melee attack
            if getattr(marshal, 'artillery', False):
                return "bombardment"
            return "attack"
        return None  # Wouldn't object to attack

    if personality == 'cautious':
        # Cautious defiance: fortify when ordered to attack or advance
        if original_action in ("attack", "SUPPORT", "MOVE_TO"):
            return "fortify"
        return None  # Wouldn't object to defend/fortify/hold

    # Unknown personality — no defiance
    return None


def defiance_succeeded(marshal, defiance_action: str, battle_result, pre_battle_strength: int):
    """Determine if a marshal's defiant action proved correct.

    Returns:
        True  -- marshal was RIGHT (won cleanly, held position, survived retreat)
        False -- marshal was WRONG (lost, pyrrhic victory, broken)
        None  -- INCONCLUSIVE (sulked/waited, no testable outcome)

    Used to determine vindication/authority/trust changes via 4-row outcome table.
    """
    if defiance_action == "wait":
        return None  # Sulk/wait-fallback = inconclusive

    if defiance_action == "attack":
        if battle_result is None:
            return None  # No battle happened (e.g., no enemy found)
        won = battle_result.get("attacker_won", False)
        casualties = battle_result.get("attacker", {}).get("casualties", 0)
        casualty_pct = casualties / pre_battle_strength if pre_battle_strength > 0 else 1.0
        return won and casualty_pct < 0.50  # Won AND not pyrrhic

    if defiance_action == "bombardment":
        if battle_result is None:
            return None  # No bombardment happened
        # Bombardment has no "won" flag — evaluate by damage inflicted.
        # RIGHT if defender took significant casualties (10%+ of attacker strength)
        # and attacker took light casualties (< 20% of own strength).
        defender_casualties = battle_result.get("defender", {}).get("casualties", 0)
        attacker_casualties = battle_result.get("attacker", {}).get("casualties", 0)
        dealt_significant = defender_casualties > (pre_battle_strength * 0.10)
        took_light = attacker_casualties < (pre_battle_strength * 0.20)
        return dealt_significant and took_light

    if defiance_action in ("defend", "fortify"):
        # Deferred evaluation: fortify/defend can't be assessed immediately.
        # Register a defensive vindication entry and return INCONCLUSIVE.
        # The vindication tracker will resolve when the enemy attacks (or not).
        return None

    if defiance_action == "retreat":
        return marshal.strength > 0  # Survived

    return None  # Unknown action = inconclusive


# ════════════════════════════════════════════════════════════════════════════
# BERTHIER FLAVOR TEXT (8 templates — 2 per outcome category)
# ════════════════════════════════════════════════════════════════════════════

BERTHIER_DEFIANCE_RIGHT = [
    "Despite your express command, {marshal} {action}... and proved the wiser for it.",
    "Your orders went unheeded by {marshal}. The outcome suggests they knew something you did not.",
]

BERTHIER_DEFIANCE_WRONG = [
    "{marshal} defied your authority and {action}. The results speak for themselves — poorly.",
    "Acting against your express command, {marshal} {action}. It did not go well.",
]

BERTHIER_DEFIANCE_INCONCLUSIVE = [
    "{marshal} defied your order... and then stood idle. The army watched in bewildered silence.",
    "{marshal} refused to act on your command, yet offered no alternative. A wasted day.",
]

BERTHIER_DEFIANCE_FAILED_ROLL = [
    "{marshal}'s hand trembled on the hilt, but discipline held... barely.",
    "For a moment, {marshal} hesitated — then obeyed. The tension in the air was palpable.",
]


def get_berthier_defiance_text(outcome_type: str, marshal_name: str, action_desc: str = "") -> str:
    """Get Berthier flavor text for a defiance outcome.

    Args:
        outcome_type: "right", "wrong", "inconclusive", or "failed_roll"
        marshal_name: Name of the marshal
        action_desc: Human-readable description of the defiant action

    Returns:
        Formatted Berthier text string
    """
    templates = {
        "right": BERTHIER_DEFIANCE_RIGHT,
        "wrong": BERTHIER_DEFIANCE_WRONG,
        "inconclusive": BERTHIER_DEFIANCE_INCONCLUSIVE,
        "failed_roll": BERTHIER_DEFIANCE_FAILED_ROLL,
    }

    template_list = templates.get(outcome_type, BERTHIER_DEFIANCE_INCONCLUSIVE)
    template = random.choice(template_list)
    return template.replace("{marshal}", marshal_name).replace("{action}", action_desc)


# ════════════════════════════════════════════════════════════════════════════
# DEFIANCE OUTCOME TABLE — apply consequences after defiance resolves
# ════════════════════════════════════════════════════════════════════════════

def describe_reluctant_obedience_cost(total_trust_change: int) -> str:
    """PT-C1: one sentence, one source, for the cost the button did not quote.

    Reads the TOTAL applied change rather than re-deriving it, so the
    sentence cannot drift from the charge — and names the surcharge
    separately, because the base penalty is the one the player already
    accepted on the button.
    """
    total = int(total_trust_change)
    surcharge = RELUCTANT_OBEDIENCE_PENALTY
    base = total - surcharge
    return (f"(Trust {total:+d} in all — {base:+d} for the order pressed "
            f"home, {surcharge:+d} more for the manner of his obedience.)")


def apply_defiance_outcome(marshal, outcome, world):
    """Apply the 4-row defiance outcome table.

    Args:
        marshal: The defiant marshal
        outcome: True (right), False (wrong), None (inconclusive), or "failed_roll"
        world: WorldState

    Returns:
        Dict with trust_change, vindication_change, authority_change, cooldown, berthier_text
    """
    result = {
        "trust_change": 0,
        "vindication_change": 0,
        "authority_change": 0,
        "cooldown_turns": 0,
        "berthier_text": "",
        "outcome_type": "",
    }

    if outcome == "failed_roll":
        # Roll fails, marshal obeys reluctantly
        result["trust_change"] = RELUCTANT_OBEDIENCE_PENALTY
        result["authority_change"] = 0
        result["cooldown_turns"] = 1
        result["outcome_type"] = "failed_roll"

        # Apply
        marshal.modify_trust(RELUCTANT_OBEDIENCE_PENALTY)
        old_v = marshal.vindication_score
        marshal.vindication_score = 0  # Reset
        result["vindication_change"] = marshal.vindication_score - old_v
        marshal.defiance_cooldown_until = world.current_turn + 1
        result["berthier_text"] = get_berthier_defiance_text("failed_roll", marshal.name)
        return result

    if outcome is True:
        # Marshal RIGHT — defiance succeeded, proved correct
        result["trust_change"] = +2
        result["vindication_change"] = +1
        result["authority_change"] = -5
        result["cooldown_turns"] = 3
        result["outcome_type"] = "right"

        marshal.modify_trust(+2)
        old_v = marshal.vindication_score
        marshal.vindication_score = max(-5, min(5, old_v + 1))
        result["vindication_change"] = marshal.vindication_score - old_v
        world.authority_tracker.modify_authority(-5)
        marshal.defiance_cooldown_until = world.current_turn + 3
        # 6C-2: Reset vindication decay timer
        world.vindication_tracker.last_change_turn[marshal.name] = world.current_turn

    elif outcome is False:
        # Marshal WRONG — defiance succeeded, proved incorrect
        result["trust_change"] = -5
        result["authority_change"] = +3
        result["cooldown_turns"] = 3
        result["outcome_type"] = "wrong"

        marshal.modify_trust(-5)
        old_v = marshal.vindication_score
        marshal.vindication_score = 0  # Reset
        result["vindication_change"] = marshal.vindication_score - old_v
        world.authority_tracker.modify_authority(+3)
        marshal.defiance_cooldown_until = world.current_turn + 3
        # 6C-2: Reset vindication decay timer
        world.vindication_tracker.last_change_turn[marshal.name] = world.current_turn

    else:  # None — INCONCLUSIVE (sulk)
        result["trust_change"] = 0
        result["vindication_change"] = 0
        result["authority_change"] = 0
        result["cooldown_turns"] = 3
        result["outcome_type"] = "inconclusive"

        marshal.defiance_cooldown_until = world.current_turn + 3

    outcome_type = result["outcome_type"]
    result["berthier_text"] = get_berthier_defiance_text(outcome_type, marshal.name)
    return result

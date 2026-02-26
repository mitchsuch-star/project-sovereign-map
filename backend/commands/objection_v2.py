"""
V2 Objection System for Project Sovereign

This module implements the V2a Objection Refactor as specified in:
- docs/OBJECTION_V2_REFACTOR_PLAN.md
- docs/V2A_IMPLEMENTATION_ADDENDUM.md

Key changes from V1:
- Deterministic ConcernLevel enum replaces severity floats
- Trust is consequence of player choices, not trigger modifier
- MILD concerns are flavor text (no popup), MODERATE+ are popups
- Per-marshal objection cap (max 1 popup per marshal per turn)
- Authority is inert in V2a (no mechanical effect until V2b)

Unit 1: Core Data Structures
- ConcernLevel enum
- TrustTier enum
- CONSEQUENCE_TABLE (tone, insist_penalty per tier)
- Trust gain/penalty calculations
- Mood variance (15-20% chance of ±1 level shift)
"""

from enum import IntEnum
from typing import Dict, Optional
import random


# ════════════════════════════════════════════════════════════════════════════
# CORE ENUMS
# ════════════════════════════════════════════════════════════════════════════


class ConcernLevel(IntEnum):
    """
    Deterministic concern levels replacing V1's severity floats.

    NONE: No concern - order executes without comment
    MILD: Minor concern - flavor text in turn log, order executes
    MODERATE: Significant concern - popup with choices
    STRONG: Major concern - popup with choices, higher trust gain if listened to
    EXTREME: Critical concern - popup, highest trust gain if listened to
    """
    NONE = 0
    MILD = 1
    MODERATE = 2
    STRONG = 3
    EXTREME = 4


class TrustTier(IntEnum):
    """
    Trust tier boundaries for consequence scaling.

    HOSTILE: Trust < 30 - Marshal deeply distrusts player
    WARY: Trust 30-49 - Marshal is skeptical
    TRUSTING: Trust 50-79 - Normal working relationship
    DEVOTED: Trust 80+ - Marshal has deep faith in player
    """
    HOSTILE = 0
    WARY = 1
    TRUSTING = 2
    DEVOTED = 3


# ════════════════════════════════════════════════════════════════════════════
# CONSEQUENCE TABLES
# ════════════════════════════════════════════════════════════════════════════


# Tone and insist penalty by trust tier
# Higher trust = more respectful objections, lower penalty for insisting
CONSEQUENCE_TABLE: Dict[TrustTier, Dict] = {
    TrustTier.HOSTILE: {
        "tone": "defiant",
        "insist_penalty": -15,
    },
    TrustTier.WARY: {
        "tone": "challenging",
        "insist_penalty": -12,
    },
    TrustTier.TRUSTING: {
        "tone": "firm",
        "insist_penalty": -10,
    },
    TrustTier.DEVOTED: {
        "tone": "respectful",
        "insist_penalty": -5,
    },
}


# Base trust gain when player trusts marshal's objection
# Higher concern level = marshal was more worried = more trust gained
TRUST_GAIN_BASE: Dict[ConcernLevel, int] = {
    ConcernLevel.MODERATE: 3,
    ConcernLevel.STRONG: 5,
    ConcernLevel.EXTREME: 8,
    # MILD and NONE have no popup, no choice, no trust gain
}


# Trust tier multiplier for trust gain (rubber-band effect)
# Low trust = bigger gains for listening (recovery rewarded)
# High trust = smaller gains (diminishing returns)
TRUST_TIER_MULTIPLIER: Dict[TrustTier, float] = {
    TrustTier.HOSTILE: 1.5,   # Rebuilding rewarded
    TrustTier.WARY: 1.2,      # Recovery encouraged
    TrustTier.TRUSTING: 1.0,  # Baseline
    TrustTier.DEVOTED: 0.7,   # Diminishing returns
}


# Flat compromise gain (not scaled by tier)
COMPROMISE_TRUST_GAIN = 3


# Backward compatibility: map ConcernLevel to legacy severity float
# Used only for gradual migration, will be removed in V2b
CONCERN_TO_SEVERITY: Dict[ConcernLevel, float] = {
    ConcernLevel.NONE: 0.0,
    ConcernLevel.MILD: 0.35,
    ConcernLevel.MODERATE: 0.55,
    ConcernLevel.STRONG: 0.72,
    ConcernLevel.EXTREME: 0.88,
}


# ════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════


def get_trust_tier(trust: int) -> TrustTier:
    """
    Get trust tier from trust value.

    Uses consistent >= operators:
    - Trust >= 80: DEVOTED
    - Trust >= 50: TRUSTING
    - Trust >= 30: WARY
    - Trust < 30: HOSTILE

    Args:
        trust: Trust value (0-100)

    Returns:
        TrustTier enum value
    """
    if trust >= 80:
        return TrustTier.DEVOTED
    if trust >= 50:
        return TrustTier.TRUSTING
    if trust >= 30:
        return TrustTier.WARY
    return TrustTier.HOSTILE


def calculate_trust_gain(concern: ConcernLevel, tier: TrustTier) -> int:
    """
    Calculate trust gain when player trusts marshal's objection.

    Formula: int(base × multiplier)

    | | HOSTILE (1.5x) | WARY (1.2x) | TRUSTING (1.0x) | DEVOTED (0.7x) |
    |---|---|---|---|---|
    | MODERATE (+3) | +5 | +4 | +3 | +2 |
    | STRONG (+5) | +8 | +6 | +5 | +4 |
    | EXTREME (+8) | +12 | +10 | +8 | +6 |

    Args:
        concern: ConcernLevel that triggered the objection
        tier: Marshal's current TrustTier

    Returns:
        Trust gain amount (always positive integer)
    """
    base = TRUST_GAIN_BASE.get(concern, 0)
    if base == 0:
        return 0
    multiplier = TRUST_TIER_MULTIPLIER.get(tier, 1.0)
    return int(base * multiplier)


def get_insist_penalty(tier: TrustTier) -> int:
    """
    Get trust penalty when player insists over marshal's objection.

    | Trust Tier | Penalty |
    |------------|---------|
    | HOSTILE | -15 |
    | WARY | -12 |
    | TRUSTING | -10 |
    | DEVOTED | -5 |

    Args:
        tier: Marshal's current TrustTier

    Returns:
        Trust penalty (negative integer)
    """
    return CONSEQUENCE_TABLE[tier]["insist_penalty"]


def get_objection_tone(tier: TrustTier) -> str:
    """
    Get objection tone based on trust tier.

    | Trust Tier | Tone |
    |------------|------|
    | HOSTILE | "defiant" |
    | WARY | "challenging" |
    | TRUSTING | "firm" |
    | DEVOTED | "respectful" |

    Args:
        tier: Marshal's current TrustTier

    Returns:
        Tone string for message generation
    """
    return CONSEQUENCE_TABLE[tier]["tone"]


def get_consequences(tier: TrustTier) -> Dict:
    """
    Get full consequence dict for a trust tier.

    Args:
        tier: Marshal's current TrustTier

    Returns:
        Dict with 'tone' and 'insist_penalty' keys
    """
    return CONSEQUENCE_TABLE[tier].copy()


# ════════════════════════════════════════════════════════════════════════════
# MOOD VARIANCE
# ════════════════════════════════════════════════════════════════════════════


def apply_mood_variance(concern: ConcernLevel) -> ConcernLevel:
    """
    Apply small random variance at ConcernLevel boundaries.

    ~15-20% chance of shifting ±1 level.
    Represents day-to-day mood of a human commander.

    Rules:
    - NONE never promotes to MILD randomly (no fake concerns)
    - Variance never drops below MILD (if base was MILD+, stays at least MILD)
    - 75% of the time, trigger is exactly as evaluated
    - 10% chance to go UP one level (cap at EXTREME)
    - 15% chance to go DOWN one level (floor at MILD)

    This is the ONLY source of randomness in V2a triggers.
    Tests should mock random.random() for deterministic results.

    Args:
        concern: Base ConcernLevel from evaluation

    Returns:
        Possibly shifted ConcernLevel
    """
    if concern == ConcernLevel.NONE:
        return concern  # Never promote NONE to MILD randomly

    roll = random.random()

    if roll < 0.10:
        # 10% chance to go UP one level (cap at EXTREME)
        new_val = min(concern.value + 1, ConcernLevel.EXTREME.value)
        return ConcernLevel(new_val)
    elif roll < 0.25:
        # 15% chance to go DOWN one level (floor at MILD, never to NONE)
        new_val = max(concern.value - 1, ConcernLevel.MILD.value)
        return ConcernLevel(new_val)

    return concern  # 75% stays at evaluated level


# ════════════════════════════════════════════════════════════════════════════
# RESPONSE HANDLING
# ════════════════════════════════════════════════════════════════════════════


def handle_objection_response(
    response_type: str,
    concern: ConcernLevel,
    tier: TrustTier
) -> int:
    """
    Calculate trust change based on player's response to objection.

    Args:
        response_type: "trust", "compromise", or "insist"
        concern: ConcernLevel that triggered the objection
        tier: Marshal's current TrustTier

    Returns:
        Trust change (positive for trust/compromise, negative for insist)
    """
    if response_type == "trust":
        return calculate_trust_gain(concern, tier)
    elif response_type == "compromise":
        return COMPROMISE_TRUST_GAIN  # Flat +3
    elif response_type == "insist":
        return get_insist_penalty(tier)
    else:
        return 0  # Unknown response type


# ════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY HELPERS
# ════════════════════════════════════════════════════════════════════════════


def concern_to_legacy_severity(concern: ConcernLevel) -> float:
    """
    Convert ConcernLevel to legacy severity float for backward compat.

    Used only for gradual migration. Will be removed in V2b.

    Args:
        concern: ConcernLevel enum value

    Returns:
        Severity float (0.0-0.88)
    """
    return CONCERN_TO_SEVERITY.get(concern, 0.0)


def is_popup_concern(concern: ConcernLevel) -> bool:
    """
    Check if concern level triggers a popup.

    MODERATE, STRONG, EXTREME → popup
    NONE, MILD → no popup

    Args:
        concern: ConcernLevel enum value

    Returns:
        True if popup should be shown
    """
    return concern >= ConcernLevel.MODERATE


def is_blocking_concern(concern: ConcernLevel) -> bool:
    """
    Check if concern level blocks order execution (pending objection).

    Same as is_popup_concern() - MODERATE+ blocks execution
    until player responds.

    Args:
        concern: ConcernLevel enum value

    Returns:
        True if order should be blocked pending player response
    """
    return concern >= ConcernLevel.MODERATE


# ════════════════════════════════════════════════════════════════════════════
# UNIT 2: TRIGGER EVALUATION FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════


def _get_world(game_state) -> Optional:
    """Extract world from game_state (handles different structures)."""
    if game_state is None:
        return None

    # Handle dict game_state (e.g., {"world": WorldState})
    if isinstance(game_state, dict):
        return game_state.get('world')

    # Handle object game_state with .world attribute
    if hasattr(game_state, 'world'):
        return game_state.world

    # Assume game_state IS the world
    return game_state


def get_visible_enemies_near(region_name: str, nation: str, world) -> list:
    """
    Get visible enemies in and adjacent to a region, respecting fog of war.

    Currently returns actual (omniscient) data — same as direct world access.
    In V2b, this will be swapped to fog-filtered data using
    world.get_visible_enemies_in_region() for each checked region.

    This is the single point of change for V2b fog integration in the
    objection system. All 12 helper functions above should eventually
    delegate enemy lookups through this helper.

    Args:
        region_name: Region to check (center of search)
        nation: The perspective nation (enemies are those with different nation)
        world: WorldState for context

    Returns:
        List of enemy marshal objects (currently omniscient, V2b: fog-filtered)
    """
    if not world or not hasattr(world, 'marshals'):
        return []

    region = world.regions.get(region_name) if hasattr(world, 'regions') else None
    if not region:
        return []

    # Check current region + adjacent regions
    check_regions = [region_name] + list(region.adjacent_regions)

    enemies = []
    seen_names = set()
    for rn in check_regions:
        for m in world.marshals.values():
            if (m.nation != nation and m.strength > 0
                    and m.location == rn and m.name not in seen_names):
                enemies.append(m)
                seen_names.add(m.name)

    return enemies


def _check_enemy_adjacent(marshal, game_state) -> bool:
    """
    Check if any enemy is adjacent to the marshal.

    TODO (V2b): Fog-aware. Currently reads world.marshals directly (omniscient).
    In V2b, should use get_visible_enemies_near() to only see enemies at
    PARTIAL+ visibility. Cautious marshals can't worry about unseen enemies.

    Args:
        marshal: The marshal to check
        game_state: Current game state

    Returns:
        True if at least one enemy is adjacent
    """
    world = _get_world(game_state)
    if not world:
        return False

    marshal_nation = getattr(marshal, 'nation', 'France')
    marshal_location = marshal.location

    # Get adjacent regions
    region = world.regions.get(marshal_location) if hasattr(world, 'regions') else None
    if not region:
        return False

    adjacent_regions = region.adjacent_regions

    # Check for enemies in adjacent regions
    if hasattr(world, 'marshals'):
        for enemy in world.marshals.values():
            if enemy.nation != marshal_nation and enemy.strength > 0:
                if enemy.location in adjacent_regions:
                    return True

    return False


def _check_enemy_in_region(marshal, game_state) -> bool:
    """
    Check if any enemy is in the same region as the marshal.

    TODO (V2b): Fog-aware. Marshal's own region is always FULL (Step 0),
    so enemies in same region are always visible. No change needed for V2b.

    Args:
        marshal: The marshal to check
        game_state: Current game state

    Returns:
        True if at least one enemy is in same region
    """
    world = _get_world(game_state)
    if not world:
        return False

    marshal_nation = getattr(marshal, 'nation', 'France')

    if hasattr(world, 'marshals'):
        for enemy in world.marshals.values():
            if enemy.nation != marshal_nation and enemy.strength > 0:
                if enemy.location == marshal.location:
                    return True

    return False


def _get_friendly_to_enemy_ratio(marshal, game_state) -> float:
    """
    Get ratio of friendly strength to nearby enemy strength.

    Higher ratio = we outnumber them.
    Used for aggressive personality "why are we defending when we outnumber them?"

    TODO (V2b): Fog-aware. Should only count enemies at PARTIAL+ visibility.
    At PARTIAL, use strength band midpoint instead of exact strength.
    At UNKNOWN, enemy contributes 0 to ratio (not seen).

    Args:
        marshal: The marshal to check
        game_state: Current game state

    Returns:
        Ratio (friendly/enemy). Returns 0.0 if no enemies, 999.0 if only friendlies.
    """
    world = _get_world(game_state)
    if not world:
        return 1.0

    marshal_nation = getattr(marshal, 'nation', 'France')
    marshal_location = marshal.location

    # Get adjacent regions
    region = world.regions.get(marshal_location) if hasattr(world, 'regions') else None
    if not region:
        return 1.0

    adjacent_and_here = list(region.adjacent_regions) + [marshal_location]

    # Sum enemy strength in adjacent regions + current region
    enemy_strength = 0
    if hasattr(world, 'marshals'):
        for enemy in world.marshals.values():
            if enemy.nation != marshal_nation and enemy.strength > 0:
                if enemy.location in adjacent_and_here:
                    enemy_strength += enemy.strength

    if enemy_strength == 0:
        return 999.0  # No enemies nearby

    return marshal.strength / enemy_strength


def _get_enemy_to_friendly_ratio(marshal, game_state) -> float:
    """
    Get ratio of enemy strength to friendly strength.

    Higher ratio = we are outnumbered.
    Used for cautious personality attack risk assessment.

    TODO (V2b): Fog-aware. Delegates to _get_friendly_to_enemy_ratio(),
    so fog filtering there automatically propagates here.

    Args:
        marshal: The marshal to check
        game_state: Current game state

    Returns:
        Ratio (enemy/friendly). Returns 0.0 if no enemies nearby.
    """
    ratio = _get_friendly_to_enemy_ratio(marshal, game_state)
    if ratio == 0.0:
        return 999.0  # No friendlies (shouldn't happen)
    if ratio == 999.0:
        return 0.0  # No enemies nearby
    return 1.0 / ratio


def _is_outnumbered_2to1(marshal, game_state) -> bool:
    """
    Check if marshal is outnumbered 2:1 or worse.

    Used for aggressive retreat exception: aggressive marshal accepts retreat
    if actually outnumbered 2:1+ AND morale is low.

    TODO (V2b): Fog-aware. Delegates to _get_enemy_to_friendly_ratio(),
    so fog filtering there automatically propagates here.

    Args:
        marshal: The marshal to check
        game_state: Current game state

    Returns:
        True if enemy strength >= 2x friendly strength
    """
    ratio = _get_enemy_to_friendly_ratio(marshal, game_state)
    return ratio >= 2.0


def _is_actually_threatened(marshal, game_state) -> bool:
    """
    Check if marshal faces a genuine threat (enemy in region or adjacent).

    TODO (V2b): Fog-aware. Delegates to _check_enemy_in_region() and
    _check_enemy_adjacent(), so fog filtering there propagates here.

    Args:
        marshal: The marshal to check
        game_state: Current game state

    Returns:
        True if enemy is in same region OR adjacent
    """
    return _check_enemy_in_region(marshal, game_state) or _check_enemy_adjacent(marshal, game_state)


def _path_crosses_enemy(marshal, target, game_state) -> bool:
    """
    Check if path to target crosses through enemy-occupied territory.

    Used for cautious MOVE objection: "marching through enemy territory is risky"

    TODO (V2b): Fog-aware. Should only detect enemies at PARTIAL+ visibility
    along the path. Walking into fogged enemies is a surprise, not a known risk.

    Args:
        marshal: The marshal moving
        target: Target region name
        game_state: Current game state

    Returns:
        True if path crosses enemy-occupied regions
    """
    world = _get_world(game_state)
    if not world:
        return False

    # Get path from world's pathfinding
    if hasattr(world, 'find_path'):
        path = world.find_path(marshal.location, target)
        if not path or len(path) < 2:
            return False

        marshal_nation = getattr(marshal, 'nation', 'France')

        # Check intermediate regions (not start, not destination)
        for region_name in path[1:-1]:
            if hasattr(world, 'marshals'):
                for enemy in world.marshals.values():
                    if enemy.nation != marshal_nation and enemy.strength > 0:
                        if enemy.location == region_name:
                            return True

    return False


def _check_attack_target_fortified(marshal, order: Dict, game_state) -> bool:
    """
    Check if attack target is fortified.

    TODO (V2b): Fog-aware. Fortification status only visible at FULL.
    At PARTIAL/STALE, marshal doesn't know if target is fortified.
    Should return False for non-FULL visibility targets.

    Args:
        marshal: The attacking marshal
        order: Order dict with 'target' key
        game_state: Current game state

    Returns:
        True if target marshal is fortified
    """
    world = _get_world(game_state)
    if not world:
        return False

    target_name = order.get('target')
    if not target_name or not hasattr(world, 'marshals'):
        return False

    target_marshal = world.marshals.get(target_name)
    if target_marshal:
        return getattr(target_marshal, 'fortified', False)

    return False


def _get_attack_odds_ratio(marshal, order: Dict, game_state) -> float:
    """
    Get strength ratio for attack target.

    Returns enemy_strength / marshal_strength.
    Higher = more dangerous for attacker.

    TODO (V2b): Fog-aware. At FULL, use exact strength (current behavior).
    At PARTIAL, use strength band midpoint estimate. At STALE/UNKNOWN,
    return 1.0 (unknown odds — can't assess danger).

    Args:
        marshal: The attacking marshal
        order: Order dict with 'target' key
        game_state: Current game state

    Returns:
        Ratio of target strength to attacker strength
    """
    world = _get_world(game_state)
    if not world:
        return 1.0

    target_name = order.get('target')
    if not target_name or not hasattr(world, 'marshals'):
        return 1.0

    target_marshal = world.marshals.get(target_name)
    if not target_marshal:
        return 1.0

    if marshal.strength <= 0:
        return 999.0  # Infinite danger

    return target_marshal.strength / marshal.strength


# ════════════════════════════════════════════════════════════════════════════
# TACTICAL TRIGGER EVALUATORS
# ════════════════════════════════════════════════════════════════════════════


def evaluate_aggressive(marshal, action: str, order: Dict, game_state) -> ConcernLevel:
    """
    Evaluate aggressive personality concern for given action.

    Triggers:
    - defend/fortify/hold/wait with enemy adjacent: MODERATE to EXTREME based on ratio
    - defend/fortify/hold/wait without enemy: MILD (why defend nothing?)
    - retreat when not actually threatened: STRONG
    - retreat when not outnumbered 2:1: MILD
    - drill with enemy adjacent: MODERATE

    Args:
        marshal: The marshal receiving the order
        action: The action being ordered
        order: Full order dict
        game_state: Current game state

    Returns:
        ConcernLevel for this situation
    """
    # Defensive actions (defend, fortify, hold, wait)
    if action in ("defend", "fortify", "hold", "wait"):
        enemy_adjacent = _check_enemy_adjacent(marshal, game_state)
        enemy_here = _check_enemy_in_region(marshal, game_state)

        if not enemy_adjacent and not enemy_here:
            return ConcernLevel.MILD  # "Why are we defending nothing?"

        # Enemy is nearby - how much do we outnumber them?
        ratio = _get_friendly_to_enemy_ratio(marshal, game_state)

        if ratio >= 3.0:
            return ConcernLevel.EXTREME  # "We outnumber them 3:1! Attack!"
        if ratio >= 2.0:
            return ConcernLevel.STRONG  # "We have clear advantage, let me attack!"
        return ConcernLevel.MODERATE  # "Enemy is right there, I want to attack"

    # Retreat action
    if action == "retreat":
        if not _is_actually_threatened(marshal, game_state):
            return ConcernLevel.STRONG  # "Retreat from what? There's no enemy!"

        # Check morale for retreat acceptance
        morale = getattr(marshal, 'morale', 100)
        if _is_outnumbered_2to1(marshal, game_state) and morale <= 40:
            return ConcernLevel.NONE  # Aggressive accepts retreat in dire situation

        if not _is_outnumbered_2to1(marshal, game_state):
            return ConcernLevel.MILD  # "We're not even outnumbered..."

        # Outnumbered 2:1+ but morale still high — aggressive wants to fight
        return ConcernLevel.MILD

    # Artillery: Wasted fire — bombarding already-broken target (§7.1)
    if action == "attack" and getattr(marshal, 'artillery', False):
        world = _get_world(game_state)
        target_name = order.get('target')
        if world and target_name:
            target_marshal = world.get_marshal(target_name) if hasattr(world, 'get_marshal') else None
            if target_marshal and getattr(target_marshal, 'defense_bonus', 0) == 0 and target_marshal.strength < 8000:
                return ConcernLevel.MILD  # "The target is already broken — save my powder"

    # Drill with enemy nearby
    if action == "drill":
        if _check_enemy_adjacent(marshal, game_state):
            return ConcernLevel.MODERATE  # "There's an enemy right there!"
        return ConcernLevel.NONE

    # Square formation — aggressive marshals want to charge, not stand still
    if action == "form_square":
        return ConcernLevel.MODERATE  # "Square?! Let me CHARGE them!"

    # Defensive stance change — aggressive marshals dislike ANY defensive posture,
    # matching the unconditional MILD on the "defend" action above.
    # V2b: escalate to MODERATE/STRONG when weak enemy is adjacent (beatable odds).
    if action == "stance_change":
        # BUG FIX: order.get('target', '') returns None when key exists with value None
        # (parser.py:297 explicitly sets "target": None). Must use `or ''` pattern.
        target_stance = (order.get('target') or '').lower()
        if target_stance in ('defensive', 'defense', 'defend'):
            return ConcernLevel.MILD  # "We should be attacking, not cowering!"
        return ConcernLevel.NONE

    return ConcernLevel.NONE


def evaluate_cautious(marshal, action: str, order: Dict, game_state) -> ConcernLevel:
    """
    Evaluate cautious personality concern for given action.

    Triggers:
    - attack with bad odds: MILD to EXTREME based on ratio
    - attack fortified position: +1 level
    - move through enemy territory: MODERATE
    - aggressive stance with enemy near: MILD

    Args:
        marshal: The marshal receiving the order
        action: The action being ordered
        order: Full order dict
        game_state: Current game state

    Returns:
        ConcernLevel for this situation
    """
    # Attack action
    if action == "attack":
        # Artillery: Ordered into melee — STRONG objection (§7.1)
        if getattr(marshal, 'artillery', False):
            world = _get_world(game_state)
            target_name = order.get('target')
            if world and target_name:
                target_marshal = world.get_marshal(target_name) if hasattr(world, 'get_marshal') else None
                if target_marshal and target_marshal.location == marshal.location:
                    return ConcernLevel.STRONG  # "You would send my gunners into the bayonet line?"

            # Artillery: Last-shot advisory — MILD when last bombardment and multiple targets (§7.1)
            if getattr(marshal, 'bombardments_this_turn', 0) == 1:
                if world:
                    region = world.get_region(marshal.location) if hasattr(world, 'get_region') else None
                    if region:
                        adjacent_targets = []
                        for adj_name in region.adjacent_regions:
                            for m in world.get_enemies_in_region(adj_name, marshal.nation):
                                if m.strength > 0 and not getattr(m, 'broken', False) and not getattr(m, 'retreating', False):
                                    adjacent_targets.append(m)
                        if len(adjacent_targets) > 1:
                            return ConcernLevel.MILD  # "One salvo remains — let me place it where it counts"

            # Artillery: Wasted fire — target already broken and weak (§7.1)
            if world and target_name:
                target_marshal = world.get_marshal(target_name) if hasattr(world, 'get_marshal') else None
                if target_marshal and getattr(target_marshal, 'defense_bonus', 0) == 0 and target_marshal.strength < 8000:
                    return ConcernLevel.MILD  # "The target is already broken — save my powder"

            return ConcernLevel.NONE  # Cautious artillery doesn't object to bombardment itself

        ratio = _get_attack_odds_ratio(marshal, order, game_state)

        # Base concern from odds
        if ratio >= 5.0:
            concern = ConcernLevel.EXTREME  # Suicide mission
        elif ratio >= 3.0:
            concern = ConcernLevel.STRONG  # Very risky
        elif ratio >= 2.0:
            concern = ConcernLevel.MODERATE  # Notably risky
        elif ratio >= 1.5:
            concern = ConcernLevel.MILD  # Slightly risky
        else:
            concern = ConcernLevel.NONE  # Acceptable odds

        # Bump up if target is fortified
        if _check_attack_target_fortified(marshal, order, game_state):
            if concern == ConcernLevel.NONE:
                concern = ConcernLevel.MILD
            elif concern < ConcernLevel.EXTREME:
                concern = ConcernLevel(concern.value + 1)

        return concern

    # Move action - check path danger
    if action == "move":
        # Artillery: Reckless repositioning — moving while bombardment streak active (§7.1)
        if getattr(marshal, 'artillery', False) and getattr(marshal, 'bombardment_streak', 0) >= 2:
            world = _get_world(game_state)
            if world:
                # Check if any adjacent target still has fortifications worth bombarding
                region = world.regions.get(marshal.location) if hasattr(world, 'regions') else None
                if region:
                    for adj_name in region.adjacent_regions:
                        for m in world.marshals.values():
                            if m.nation != getattr(marshal, 'nation', 'France') and m.location == adj_name:
                                if getattr(m, 'defense_bonus', 0) > 0:
                                    return ConcernLevel.MODERATE  # "One more barrage and their walls crumble!"

        target = order.get('target')
        if target and _path_crosses_enemy(marshal, target, game_state):
            return ConcernLevel.MODERATE  # "That route goes through enemy territory"
        return ConcernLevel.NONE

    # Artillery: Ordered to cease fire — defend/fortify while adjacent fort still standing (§7.1)
    if action in ("defend", "fortify") and getattr(marshal, 'artillery', False):
        streak = getattr(marshal, 'bombardment_streak', 0)
        if streak >= 1:
            world = _get_world(game_state)
            if world:
                region = world.get_region(marshal.location) if hasattr(world, 'get_region') else None
                if region:
                    for adj_name in region.adjacent_regions:
                        for m in world.get_enemies_in_region(adj_name, marshal.nation):
                            if getattr(m, 'defense_bonus', 0) > 0.05:
                                return ConcernLevel.MODERATE  # "Their walls still stand — give me one more day!"

    # Square formation — cautious marshal notices tactical problems
    if action == "form_square":
        # Already fortified — square would abandon earthworks for less protection
        if getattr(marshal, 'fortified', False):
            return ConcernLevel.MILD  # "We've built earthworks — square is worse!"
        # Enemy artillery adjacent but no cavalry — square invites shells
        has_cavalry = False
        has_artillery = False
        world = _get_world(game_state)
        if world:
            region = world.get_region(marshal.location) if hasattr(world, 'get_region') else None
            if region:
                for adj_name in region.adjacent_regions:
                    for m in world.get_enemies_in_region(adj_name, marshal.nation):
                        if getattr(m, 'cavalry', False) and m.strength > 0:
                            has_cavalry = True
                        if getattr(m, 'artillery', False) and m.strength > 0:
                            has_artillery = True
                # Also check same region
                for m in world.get_enemies_in_region(marshal.location, marshal.nation):
                    if getattr(m, 'cavalry', False) and m.strength > 0:
                        has_cavalry = True
                    if getattr(m, 'artillery', False) and m.strength > 0:
                        has_artillery = True
        if has_artillery and not has_cavalry:
            return ConcernLevel.MILD  # "Their guns will punish us — I see no cavalry"
        return ConcernLevel.NONE

    # Aggressive stance change
    if action == "stance_change":
        # BUG FIX: order.get('target', '') returns None when key exists with value None
        # (parser.py:297 explicitly sets "target": None). Must use `or ''` pattern.
        target_stance = (order.get('target') or '').lower()
        if target_stance == 'aggressive' and _check_enemy_adjacent(marshal, game_state):
            return ConcernLevel.MILD  # "Going aggressive with enemy nearby is risky"
        return ConcernLevel.NONE

    return ConcernLevel.NONE


def evaluate_literal(marshal, action: str, order: Dict, game_state) -> ConcernLevel:
    """
    Evaluate literal personality concern for given action.

    Literal personality (Grouchy) NEVER objects - uses clarification system instead.
    Always returns NONE.

    Args:
        marshal: The marshal receiving the order
        action: The action being ordered
        order: Full order dict
        game_state: Current game state

    Returns:
        Always ConcernLevel.NONE
    """
    return ConcernLevel.NONE


# Personality evaluator dispatch table
PERSONALITY_EVALUATORS = {
    "aggressive": evaluate_aggressive,
    "cautious": evaluate_cautious,
    "literal": evaluate_literal,
}


def evaluate_situation(marshal, action: str, order: Dict, game_state) -> ConcernLevel:
    """
    Main dispatcher: evaluate concern level for any marshal/action combination.

    Routes to personality-specific evaluator. Unknown personalities return NONE.

    Args:
        marshal: The marshal receiving the order
        action: The action being ordered (lowercase)
        order: Full order dict with action, target, etc.
        game_state: Current game state

    Returns:
        ConcernLevel for this situation
    """
    # Universal trigger: form_square with both cavalry AND artillery nearby
    if action == "form_square":
        world = _get_world(game_state)
        if world:
            has_cavalry = False
            has_artillery = False
            region = world.get_region(marshal.location) if hasattr(world, 'get_region') else None
            if region:
                for adj_name in list(region.adjacent_regions) + [marshal.location]:
                    for m in world.get_enemies_in_region(adj_name, marshal.nation):
                        if getattr(m, 'cavalry', False) and m.strength > 0:
                            has_cavalry = True
                        if getattr(m, 'artillery', False) and m.strength > 0:
                            has_artillery = True
            if has_cavalry and has_artillery:
                return ConcernLevel.MILD  # "Both cavalry and guns threaten us"

    personality = getattr(marshal, 'personality', 'balanced').lower()
    evaluator = PERSONALITY_EVALUATORS.get(personality)

    if evaluator is None:
        # Unknown personality (balanced, loyal, etc.) = no objection in V2a
        return ConcernLevel.NONE

    return evaluator(marshal, action, order, game_state)


# ════════════════════════════════════════════════════════════════════════════
# UNIT 3: STRATEGIC TRIGGER EVALUATORS
# ════════════════════════════════════════════════════════════════════════════


def _check_enemies_adjacent_to_region(region_name: str, marshal_nation: str, world) -> bool:
    """
    Check if any enemies are adjacent to a specific region.

    TODO (V2b): Fog-aware. Should only count enemies at PARTIAL+ visibility
    in adjacent regions. Use get_visible_enemies_near() instead of
    direct world.get_enemies_in_region() calls.

    Args:
        region_name: Name of the region to check
        marshal_nation: Nation of the marshal (to identify enemies)
        world: WorldState for context

    Returns:
        True if at least one enemy is in an adjacent region
    """
    if not world:
        return False

    region = world.get_region(region_name) if hasattr(world, 'get_region') else None
    if not region:
        return False

    for adj_name in region.adjacent_regions:
        if hasattr(world, 'get_enemies_in_region'):
            enemies = world.get_enemies_in_region(adj_name, marshal_nation)
            if enemies:
                return True

    return False


def _get_pursue_target_ratio(marshal, target_name: str, world) -> float:
    """
    Get strength ratio for PURSUE target.

    Returns target_strength / marshal_strength.
    Higher = more dangerous for pursuer.

    TODO (V2b): Fog-aware. At FULL, use exact strength. At PARTIAL, use
    band midpoint. At STALE/UNKNOWN, return 1.0 (unknown).

    Args:
        marshal: The pursuing marshal
        target_name: Name of target marshal
        world: WorldState for context

    Returns:
        Ratio of target strength to pursuer strength
    """
    if not world or not target_name:
        return 1.0

    target_marshal = world.get_marshal(target_name) if hasattr(world, 'get_marshal') else None
    if not target_marshal or target_marshal.strength <= 0:
        return 0.0  # No valid target

    if marshal.strength <= 0:
        return 999.0  # Infinite danger

    return target_marshal.strength / marshal.strength


def _path_has_enemies(path: list, marshal_nation: str, world) -> tuple:
    """
    Check if path crosses any enemy-occupied regions.

    TODO (V2b): Fog-aware. Should only detect enemies at PARTIAL+ visibility
    along the path. Fogged enemies are unknown — marshal can't object about them.

    Args:
        path: List of region names
        marshal_nation: Nation of the marshal
        world: WorldState for context

    Returns:
        (has_enemies, enemy_regions) - bool and list of enemy region names
    """
    if not world or not path:
        return False, []

    enemy_regions = []
    for region_name in path:
        if hasattr(world, 'get_enemies_in_region'):
            enemies = world.get_enemies_in_region(region_name, marshal_nation)
            if enemies:
                enemy_regions.append(region_name)

    return len(enemy_regions) > 0, enemy_regions


def evaluate_strategic_aggressive(
    marshal,
    order_type: str,
    target: str,
    path: list,
    game_state
) -> ConcernLevel:
    """
    Evaluate aggressive personality concerns for strategic commands.

    Triggers:
    - HOLD with no enemies adjacent to target region: MODERATE to EXTREME
      based on how much marshal outnumbers nearby enemies

    Args:
        marshal: The marshal receiving the order
        order_type: "HOLD", "PURSUE", "MOVE_TO", "SUPPORT"
        target: Target region name or marshal name
        path: List of regions to traverse (may be empty)
        game_state: Game state dict {"world": WorldState}

    Returns:
        ConcernLevel for this situation
    """
    world = _get_world(game_state)
    if not world:
        return ConcernLevel.NONE

    marshal_nation = getattr(marshal, 'nation', 'France')

    if order_type == "HOLD":
        hold_region = target or marshal.location
        enemies_adjacent = _check_enemies_adjacent_to_region(hold_region, marshal_nation, world)

        if not enemies_adjacent:
            # No enemies nearby - aggressive marshal objects to passive orders
            # Check if we have overwhelming force somewhere
            # For now, simple: no enemies = MODERATE (wants to attack somewhere)
            return ConcernLevel.MODERATE

        # Enemies ARE adjacent - check our advantage
        # Get ratio of our strength to nearby enemies
        ratio = _get_friendly_to_enemy_ratio(marshal, game_state)

        if ratio >= 3.0:
            return ConcernLevel.EXTREME  # "We outnumber them 3:1! Let me attack!"
        if ratio >= 2.0:
            return ConcernLevel.STRONG  # "Clear advantage, let me attack!"

        # Enemies adjacent but we're not overwhelmingly stronger - HOLD is acceptable
        return ConcernLevel.NONE

    # §6: Aggressive objects to defensive SUPPORT (target fortified/cautious/retreating/broken)
    if order_type == "SUPPORT":
        target_marshal = world.marshals.get(target) if target else None
        if target_marshal:
            target_is_defensive = (
                getattr(target_marshal, 'fortified', False)
                or target_marshal.personality == "cautious"
                or getattr(target_marshal, 'retreated_this_turn', False)
                or getattr(target_marshal, 'broken', False)
            )
            if target_is_defensive:
                return ConcernLevel.MODERATE
        return ConcernLevel.NONE

    return ConcernLevel.NONE


def evaluate_strategic_cautious(
    marshal,
    order_type: str,
    target: str,
    path: list,
    game_state
) -> ConcernLevel:
    """
    Evaluate cautious personality concerns for strategic commands.

    Triggers:
    - PURSUE with target strength >= 1.2x marshal strength: MILD to EXTREME
    - MOVE_TO/HOLD/SUPPORT with path through enemy territory: MODERATE

    Args:
        marshal: The marshal receiving the order
        order_type: "HOLD", "PURSUE", "MOVE_TO", "SUPPORT"
        target: Target region name or marshal name
        path: List of regions to traverse
        game_state: Game state dict {"world": WorldState}

    Returns:
        ConcernLevel for this situation
    """
    world = _get_world(game_state)
    if not world:
        return ConcernLevel.NONE

    marshal_nation = getattr(marshal, 'nation', 'France')

    # PURSUE - check target strength ratio
    if order_type == "PURSUE":
        ratio = _get_pursue_target_ratio(marshal, target, world)

        if ratio >= 5.0:
            return ConcernLevel.EXTREME  # Suicide mission
        if ratio >= 3.0:
            return ConcernLevel.STRONG  # Very risky
        if ratio >= 2.0:
            return ConcernLevel.MODERATE  # Notably risky
        if ratio >= 1.5:
            return ConcernLevel.MILD  # Slightly risky (V2: no popup)
        if ratio >= 1.2:
            return ConcernLevel.MILD  # Old threshold was 1.2, now MILD

        return ConcernLevel.NONE

    # MOVE_TO - check path danger
    if order_type == "MOVE_TO":
        has_enemies, _ = _path_has_enemies(path, marshal_nation, world)
        if has_enemies:
            return ConcernLevel.MODERATE  # Dangerous path
        return ConcernLevel.NONE

    # HOLD - check if distant and path is dangerous
    if order_type == "HOLD":
        # Only if marshal must travel (not already at target)
        if target and marshal.location != target and path:
            has_enemies, _ = _path_has_enemies(path, marshal_nation, world)
            if has_enemies:
                return ConcernLevel.MODERATE  # Dangerous path to hold position
        return ConcernLevel.NONE

    # SUPPORT - check reckless ally and path danger
    if order_type == "SUPPORT":
        # §6: Cautious objects to supporting reckless ally (aggressive + recklessness >= 2)
        target_marshal = world.marshals.get(target) if target else None
        if target_marshal:
            is_reckless = (
                target_marshal.personality == "aggressive"
                and getattr(target_marshal, 'recklessness', 0) >= 2
            )
            if is_reckless:
                return ConcernLevel.MODERATE
        if path:
            has_enemies, _ = _path_has_enemies(path, marshal_nation, world)
            if has_enemies:
                return ConcernLevel.MODERATE  # Dangerous path to ally
        return ConcernLevel.NONE

    return ConcernLevel.NONE


def evaluate_strategic_literal(
    marshal,
    order_type: str,
    target: str,
    path: list,
    game_state
) -> ConcernLevel:
    """
    Evaluate literal personality concerns for strategic commands.

    Literal personality (Grouchy) NEVER objects to strategic commands.
    Uses clarification system instead for ambiguous orders.

    Always returns NONE.
    """
    return ConcernLevel.NONE


# Strategic personality evaluator dispatch table
STRATEGIC_EVALUATORS = {
    "aggressive": evaluate_strategic_aggressive,
    "cautious": evaluate_strategic_cautious,
    "literal": evaluate_strategic_literal,
}


def _evaluate_relationship_support(marshal, target: str, game_state) -> ConcernLevel:
    """V2b: Relationship-based SUPPORT objection.

    Fires at order issuance when marshal is ordered to SUPPORT a hostile/rival target.
    Relationship check takes priority over personality if higher.

    | Personality | Target Relationship | ConcernLevel |
    |---|---|---|
    | Aggressive | Hostile (-2) | STRONG |
    | Cautious | Hostile (-2) | MODERATE |
    | Literal | Hostile (-2) | NONE |
    | Any | Rival (-1) | MILD |

    Args:
        marshal: The marshal receiving the SUPPORT order
        target: Target marshal name
        game_state: Game state dict

    Returns:
        ConcernLevel based on relationship (NONE if no relationship concern)
    """
    if not target:
        return ConcernLevel.NONE

    personality = getattr(marshal, 'personality', 'balanced').lower()
    if personality == 'literal':
        return ConcernLevel.NONE  # Literal follows orders regardless

    # Get relationship toward target
    rel = marshal.get_relationship(target) if hasattr(marshal, 'get_relationship') else 0

    if rel == -2:  # Hostile
        if personality == 'aggressive':
            return ConcernLevel.STRONG
        elif personality == 'cautious':
            return ConcernLevel.MODERATE
        # Other personalities with hostile: MODERATE as default
        return ConcernLevel.MODERATE
    elif rel == -1:  # Rival
        return ConcernLevel.MILD

    return ConcernLevel.NONE


# V2b: Relationship-based SUPPORT objection message templates
RELATIONSHIP_SUPPORT_MESSAGES = {
    ConcernLevel.STRONG: "You ask me to bleed for {target}? That man would see me destroyed!",
    ConcernLevel.MODERATE: "Supporting {target}... I have reservations, but I will comply.",
    ConcernLevel.MILD: "{target}... I have my doubts about that one.",
}


def evaluate_strategic_situation(
    marshal,
    order_type: str,
    target: str,
    path: list,
    game_state
) -> ConcernLevel:
    """
    Main dispatcher: evaluate concern level for strategic commands.

    Routes to personality-specific evaluator. Unknown personalities return NONE.
    V2b: Relationship-based SUPPORT check runs first, takes priority if higher.

    Args:
        marshal: The marshal receiving the order
        order_type: "HOLD", "PURSUE", "MOVE_TO", "SUPPORT"
        target: Target region name or marshal name
        path: List of regions to traverse
        game_state: Game state dict {"world": WorldState}

    Returns:
        ConcernLevel for this situation
    """
    # V2b: Relationship-based SUPPORT objection (fires before personality)
    relationship_concern = ConcernLevel.NONE
    if order_type == "SUPPORT":
        relationship_concern = _evaluate_relationship_support(marshal, target, game_state)

    personality = getattr(marshal, 'personality', 'balanced').lower()
    evaluator = STRATEGIC_EVALUATORS.get(personality)

    personality_concern = ConcernLevel.NONE
    if evaluator is not None:
        personality_concern = evaluator(marshal, order_type, target, path, game_state)

    # Relationship concern takes priority if higher
    return max(relationship_concern, personality_concern)


# ════════════════════════════════════════════════════════════════════════════
# TEST SUPPORT
# ════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    print("=" * 60)
    print("V2 OBJECTION SYSTEM - UNIT 1 VERIFICATION")
    print("=" * 60)

    # Test trust tiers
    print("\n--- Trust Tier Boundaries ---")
    test_cases = [0, 29, 30, 49, 50, 79, 80, 100]
    for trust in test_cases:
        tier = get_trust_tier(trust)
        print(f"Trust {trust:3d} → {tier.name}")

    # Test trust gain matrix
    print("\n--- Trust Gain Matrix ---")
    print(f"{'':12} | HOSTILE | WARY | TRUSTING | DEVOTED")
    for concern in [ConcernLevel.MODERATE, ConcernLevel.STRONG, ConcernLevel.EXTREME]:
        gains = [
            calculate_trust_gain(concern, TrustTier.HOSTILE),
            calculate_trust_gain(concern, TrustTier.WARY),
            calculate_trust_gain(concern, TrustTier.TRUSTING),
            calculate_trust_gain(concern, TrustTier.DEVOTED),
        ]
        print(f"{concern.name:12} | {gains[0]:7d} | {gains[1]:4d} | {gains[2]:8d} | {gains[3]:7d}")

    # Test insist penalties
    print("\n--- Insist Penalties ---")
    for tier in TrustTier:
        penalty = get_insist_penalty(tier)
        tone = get_objection_tone(tier)
        print(f"{tier.name:12} → penalty: {penalty:3d}, tone: {tone}")

    # Test mood variance distribution (sample 1000)
    print("\n--- Mood Variance Distribution (1000 samples) ---")
    from collections import Counter

    for base_level in [ConcernLevel.NONE, ConcernLevel.MILD, ConcernLevel.MODERATE, ConcernLevel.STRONG]:
        results = Counter()
        for _ in range(1000):
            result = apply_mood_variance(base_level)
            results[result.name] += 1

        print(f"\n{base_level.name}:")
        for name, count in sorted(results.items(), key=lambda x: ConcernLevel[x[0]].value):
            pct = count / 10
            print(f"  {name}: {pct:.1f}%")

    # Test response handling
    print("\n--- Response Handling ---")
    tier = TrustTier.WARY
    for concern in [ConcernLevel.MODERATE, ConcernLevel.STRONG, ConcernLevel.EXTREME]:
        trust_gain = handle_objection_response("trust", concern, tier)
        insist_pen = handle_objection_response("insist", concern, tier)
        compromise = handle_objection_response("compromise", concern, tier)
        print(f"{concern.name} at {tier.name}: trust=+{trust_gain}, insist={insist_pen}, compromise=+{compromise}")

    print("\n" + "=" * 60)
    print("UNIT 1 VERIFICATION COMPLETE")
    print("=" * 60)

"""
Disobedience System for Project Sovereign (Phase 2)

The CORE INNOVATION: Marshals negotiate orders rather than randomly disobeying.

When a marshal objects to an order:
1. Calculate objection severity based on personality, trust, situation
2. If mild (< 0.50): Auto-resolve with grumbling
3. If major (>= 0.50): Present player with choices:
   - Trust: Follow marshal's suggestion
   - Insist: Force original order (trust penalty)
   - Compromise: Find middle ground

This is Phase 2 (Mock Mode) - NO LLM API calls. All logic is deterministic.
"""

from typing import Dict, Optional, List, Tuple
import random
from backend.commands.severity import calculate_objection_severity
from backend.models.personality import Personality, get_personality


# Maximum objection popups per turn (cascade breaker — do NOT remove).
# V2a uses per-marshal cap only (world.objection_popups_this_turn).
# This constant is referenced by DisobedienceSystem.evaluate_order() (V1 code path).
# V2b rename: was MAX_MAJOR_OBJECTIONS_PER_TURN. MILD concerns (no popup) uncapped.
MAX_OBJECTION_POPUPS_PER_TURN = 2

# Backward-compat alias — legacy code and tests may reference old name
MAX_MAJOR_OBJECTIONS_PER_TURN = MAX_OBJECTION_POPUPS_PER_TURN


# ════════════════════════════════════════════════════════════════════════════
# VALID ACTIONS SYSTEM
# ════════════════════════════════════════════════════════════════════════════
# Extensible system for determining what actions a marshal can take.
# Currently: attack, defend, move
# FUTURE: scout, feint, abilities, etc.
# ════════════════════════════════════════════════════════════════════════════


def get_enemies_in_range(marshal, game_state) -> List:
    """Get all enemy marshals within this marshal's attack range."""
    if game_state is None:
        return []

    enemies = []
    movement_range = getattr(marshal, 'movement_range', 2)

    for enemy in game_state.get_enemy_marshals():
        if enemy.strength <= 0:
            continue
        distance = game_state.get_distance(marshal.location, enemy.location)
        if distance <= movement_range:
            enemies.append(enemy)

    # Sort by distance (closest first)
    enemies.sort(key=lambda e: game_state.get_distance(marshal.location, e.location))
    return enemies


def get_adjacent_regions(marshal_location: str, game_state) -> List[str]:
    """Get all adjacent regions the marshal can move to."""
    if game_state is None:
        return []

    region = game_state.regions.get(marshal_location)
    if region:
        return list(region.adjacent_regions)
    return []


def is_valid_move(marshal, target_region_name: str, game_state) -> Tuple[bool, str]:
    """
    Validate if a move to target region is legal.

    Checks:
    1. Engagement rule: If enemies in current region, can only move to friendly territory
    2. Destination enemy check: Cannot move into region with enemy marshals

    Returns:
        (is_valid, reason) - True if valid, False with explanation if not
    """
    if game_state is None:
        return False, "No game state"

    # Get world state (handle different game_state structures)
    world = getattr(game_state, 'world', game_state) if game_state else None
    if not world or not hasattr(world, 'get_marshals_in_region'):
        return True, "Cannot validate (no world)"  # Assume valid if can't check

    marshal_nation = getattr(marshal, 'nation', 'France')

    # ════════════════════════════════════════════════════════════
    # CHECK 1: ENGAGEMENT RULE
    # If enemy in current region, can only move to friendly territory
    # ════════════════════════════════════════════════════════════
    marshals_here = world.get_marshals_in_region(marshal.location)
    enemies_here = [m for m in marshals_here if m.nation != marshal_nation and m.strength > 0
                    and world.is_at_war(marshal_nation, m.nation)]

    if enemies_here:
        # Engaged with enemy - check if destination is friendly
        target_region = world.get_region(target_region_name)
        if target_region and target_region.controller != marshal_nation:
            return False, "Engaged with enemy - can only retreat to friendly territory"

    # ════════════════════════════════════════════════════════════
    # CHECK 2: DESTINATION ENEMY CHECK
    # Cannot MOVE into region with enemy marshals (must use ATTACK)
    # ════════════════════════════════════════════════════════════
    marshals_at_dest = world.get_marshals_in_region(target_region_name)
    enemies_at_dest = [m for m in marshals_at_dest if m.nation != marshal_nation and m.strength > 0
                       and world.is_at_war(marshal_nation, m.nation)]

    if enemies_at_dest:
        return False, f"Enemy forces at {target_region_name} - must use ATTACK"

    return True, "Valid move"


def get_valid_move_targets(marshal, game_state) -> List[str]:
    """
    Get list of adjacent regions the marshal can legally move to.

    Filters out invalid moves based on:
    - Engagement rules (can't advance if engaged with enemy)
    - Enemy presence at destination (can't move into enemy-occupied region)
    """
    adjacent = get_adjacent_regions(marshal.location, game_state)
    valid_targets = []

    for region_name in adjacent:
        is_valid, reason = is_valid_move(marshal, region_name, game_state)
        if is_valid:
            valid_targets.append(region_name)

    return valid_targets


def can_drill(marshal, game_state) -> bool:
    """
    Check if marshal can legally drill.

    Drill is blocked if:
    - Already drilling or drilling_locked
    - Fortified
    - Retreating
    - In aggressive stance (executor blocks drill in aggressive stance)
    - Enemy in same region (can't train with enemy attacking!)
    """
    if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
        return False
    if getattr(marshal, 'fortified', False):
        return False
    if getattr(marshal, 'retreating', False):
        return False

    # ⚠️3 fix: Aggressive stance blocks drill (mirrors executor pre-validation)
    from backend.models.marshal import Stance
    if getattr(marshal, 'stance', Stance.NEUTRAL) == Stance.AGGRESSIVE:
        return False

    # Check for enemies in same region
    if game_state is None:
        return True  # Assume valid if can't check

    world = getattr(game_state, 'world', game_state) if game_state else None
    if not world or not hasattr(world, 'get_marshals_in_region'):
        return True

    marshal_nation = getattr(marshal, 'nation', 'France')
    marshals_here = world.get_marshals_in_region(marshal.location)
    enemies_here = [m for m in marshals_here if m.nation != marshal_nation and m.strength > 0
                    and world.is_at_war(marshal_nation, m.nation)]

    return len(enemies_here) == 0


def can_change_stance(marshal, target_stance: str) -> bool:
    """
    Check if marshal can change to target stance.

    Blocked if:
    - Already in that stance
    - Drilling or drilling_locked
    - Retreating
    """
    from backend.models.marshal import Stance

    if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
        return False
    if getattr(marshal, 'retreating', False):
        return False

    current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

    stance_map = {
        'aggressive': Stance.AGGRESSIVE,
        'defensive': Stance.DEFENSIVE,
        'neutral': Stance.NEUTRAL,
    }

    target = stance_map.get(target_stance.lower())
    if target is None:
        return False

    return current_stance != target


def can_fortify(marshal, game_state) -> bool:
    """
    Check if marshal can legally fortify.

    Blocked if:
    - Already fortified
    - Drilling or drilling_locked
    - Retreating
    - In aggressive stance (executor blocks fortify in aggressive stance)
    """
    if getattr(marshal, 'fortified', False):
        return False
    if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
        return False
    if getattr(marshal, 'retreating', False):
        return False

    from backend.models.marshal import Stance
    if getattr(marshal, 'stance', Stance.NEUTRAL) == Stance.AGGRESSIVE:
        return False

    return True


def _can_execute_suggestion(marshal, action_dict, game_state) -> bool:
    """
    Master Rule #1: Validate whether a suggested alternative action is actually
    executable by the marshal. Used to filter fallback chains so we never suggest
    actions that would fail executor pre-validation.

    Args:
        marshal: The marshal who would execute
        action_dict: Dict with 'action', 'target', etc.
        game_state: Current game state

    Returns:
        True if the action would pass basic pre-validation
    """
    action = action_dict.get('action', '').lower()
    target = action_dict.get('target', '')

    # Attack: needs a valid target enemy
    if action == 'attack':
        if not target:
            return False
        world = getattr(game_state, 'world', game_state) if game_state else None
        if not world or not hasattr(world, 'marshals'):
            return False
        enemy = world.marshals.get(target)
        if not enemy or enemy.strength <= 0:
            return False
        if getattr(marshal, 'fortified', False):
            return False
        return True

    # Move: needs valid destination, not fortified
    if action == 'move':
        if not target:
            return False
        if getattr(marshal, 'fortified', False):
            return False
        return True

    # Defend: always valid
    if action == 'defend':
        return True

    # Drill: delegate to can_drill
    if action == 'drill':
        return can_drill(marshal, game_state)

    # Fortify: delegate to can_fortify
    if action == 'fortify':
        return can_fortify(marshal, game_state)

    # Stance change: delegate to can_change_stance
    if action == 'stance_change':
        target_stance = action_dict.get('target_stance') or target or ''
        if not target_stance:
            return False
        return can_change_stance(marshal, target_stance)

    # Retreat: needs danger
    if action == 'retreat':
        if getattr(marshal, 'retreating', False):
            return False
        world = getattr(game_state, 'world', game_state) if game_state else None
        if world:
            capital = getattr(world, 'player_capital', None)
            if capital and marshal.location == capital:
                return False
            if hasattr(world, 'is_in_danger'):
                return world.is_in_danger(marshal.name)
        return False

    # Recruit: generally always valid
    if action == 'recruit':
        return True

    # Form square: needs infantry (not cavalry/artillery), not already in square
    if action == 'form_square':
        if getattr(marshal, 'square_formation', False):
            return False
        if getattr(marshal, 'cavalry', False):
            return False
        if getattr(marshal, 'artillery', False):
            return False
        return True

    # Default: assume valid for unknown actions
    return True


def get_enemies_in_region(marshal, game_state) -> List:
    """Get enemy marshals in the same region as marshal."""
    if game_state is None:
        return []

    world = getattr(game_state, 'world', game_state) if game_state else None
    if not world or not hasattr(world, 'get_marshals_in_region'):
        return []

    marshal_nation = getattr(marshal, 'nation', 'France')
    marshals_here = world.get_marshals_in_region(marshal.location)
    return [m for m in marshals_here if m.nation != marshal_nation and m.strength > 0
            and world.is_at_war(marshal_nation, m.nation)]


def get_valid_actions(marshal, game_state) -> List[Dict]:
    """
    Return all actions this marshal can currently take.

    Always includes (based on state):
    - defend (current location)
    - attack (each enemy in range) - blocked if fortified
    - move (each adjacent region) - blocked if fortified
    - drill (if not already drilling/fortified/retreating)
    - fortify (if not already fortified/drilling/retreating)
    - unfortify (if fortified)
    - retreat (if not already retreating, always valid)

    FUTURE EXTENSIBILITY:
    - scout: Move toward enemy but don't engage
    - feint: Threaten attack, hold position
    - abilities: Marshal-specific special actions
    """
    valid = []

    # Check current tactical state
    is_drilling = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)
    is_fortified = getattr(marshal, 'fortified', False)
    is_retreating = getattr(marshal, 'retreating', False)

    # Defend is always valid
    valid.append({
        "action": "defend",
        "target": marshal.location,
        "description": f"Defend at {marshal.location}"
    })

    # Attack targets in range (blocked if fortified)
    if not is_fortified:
        enemies_in_range = get_enemies_in_range(marshal, game_state)
        for enemy in enemies_in_range:
            valid.append({
                "action": "attack",
                "target": enemy.name,
                "description": f"Attack {enemy.name}"
            })

    # Move destinations (blocked if fortified, validated against game rules)
    if not is_fortified:
        valid_move_targets = get_valid_move_targets(marshal, game_state)
        for region in valid_move_targets:
            valid.append({
                "action": "move",
                "target": region,
                "description": f"Move to {region}"
            })

    # ════════════════════════════════════════════════════════════
    # TACTICAL STATE ACTIONS (Phase 2.6)
    # ════════════════════════════════════════════════════════════

    # Drill: Available if not already drilling/fortified/retreating
    if not is_drilling and not is_fortified and not is_retreating:
        valid.append({
            "action": "drill",
            "target": marshal.location,
            "description": f"Drill troops at {marshal.location} (2-turn commitment, +20% attack)"
        })

    # Fortify: Available if not already fortified/drilling/retreating
    if not is_fortified and not is_drilling and not is_retreating:
        valid.append({
            "action": "fortify",
            "target": marshal.location,
            "description": f"Fortify position at {marshal.location} (+10% defense, cannot move/attack)"
        })

    # Unfortify: Only available if currently fortified
    if is_fortified:
        valid.append({
            "action": "unfortify",
            "target": marshal.location,
            "description": f"Abandon fortified position at {marshal.location}"
        })

    # Retreat: Always available (free action) unless already retreating or at capital
    world = getattr(game_state, 'world', game_state) if game_state else None
    capital = getattr(world, 'player_capital', None) if world else None
    if not is_retreating and (not capital or marshal.location != capital):
        valid.append({
            "action": "retreat",
            "target": "toward_capital",
            "description": "Retreat toward Paris (free, -45% effectiveness, recovers over 3 turns)"
        })

    # ════════════════════════════════════════════════════════════
    # STANCE CHANGES (Phase 2.7)
    # ════════════════════════════════════════════════════════════
    from backend.models.marshal import Stance
    current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

    # Can always change to a different stance (unless drilling/retreating)
    if not is_drilling and not is_retreating:
        if current_stance != Stance.NEUTRAL:
            valid.append({
                "action": "stance_change",
                "target": "neutral",
                "description": "Return to NEUTRAL stance (FREE, balanced posture)"
            })
        if current_stance != Stance.DEFENSIVE:
            cost = "1 action" if current_stance == Stance.NEUTRAL else "2 actions"
            valid.append({
                "action": "stance_change",
                "target": "defensive",
                "description": f"Adopt DEFENSIVE stance ({cost}, -10% atk, +15% def)"
            })
        if current_stance != Stance.AGGRESSIVE:
            cost = "1 action" if current_stance == Stance.NEUTRAL else "2 actions"
            valid.append({
                "action": "stance_change",
                "target": "aggressive",
                "description": f"Adopt AGGRESSIVE stance ({cost}, +15% atk, -10% def)"
            })

    # ════════════════════════════════════════════════════════════
    # FUTURE: Ability hooks
    # ════════════════════════════════════════════════════════════
    # for ability in getattr(marshal, 'abilities', []):
    #     if ability.can_use(marshal, game_state):
    #         valid.append({
    #             "action": ability.name,
    #             "target": ability.get_target(marshal, game_state),
    #             "description": ability.description
    #         })

    return valid


def find_action_in_valid(action: str, target: str, valid_actions: List[Dict]) -> Optional[Dict]:
    """Check if a specific action+target exists in valid actions."""
    for v in valid_actions:
        if v["action"] == action and v["target"] == target:
            return v
    return None


# ════════════════════════════════════════════════════════════════════════════
# COMPROMISE RULES
# ════════════════════════════════════════════════════════════════════════════
# TODO (see ROADMAP.md): Post-testing, evaluate if scout/feint are needed for meaningful
# compromise options. Only add if mechanically distinct from attack/defend/move.
#
# Current approach: If no real middle ground exists, compromise = original order
# executed with acknowledgment (small trust bonus for hearing marshal out).
# ════════════════════════════════════════════════════════════════════════════

COMPROMISE_RULES = {
    # Attack vs Defend - compromise is move (approach but don't engage yet)
    ('attack', 'defend'): 'move',
    ('defend', 'attack'): 'move',

    # Move conflicts - defend as safe option
    ('move', 'defend'): 'defend',
    ('defend', 'move'): 'move',

    # Attack vs Move - move is the middle ground
    ('attack', 'move'): 'move',
    ('move', 'attack'): 'defend',  # Hold ground — neither advance nor attack

    # ════════════════════════════════════════════════════════════
    # TACTICAL ACTION COMPROMISES (Phase 2.6)
    # ════════════════════════════════════════════════════════════

    # Fortify conflicts (aggressive marshals hate digging in)
    ('fortify', 'attack'): 'defend',  # Hold position but stay mobile
    ('fortify', 'move'): 'defend',    # Stay and hold, but don't dig in
    ('fortify', 'drill'): 'drill',    # Drill is active preparation - compromise toward marshal
    ('attack', 'fortify'): 'defend',  # If cautious wants fortify, settle for defend

    # Drill conflicts
    ('drill', 'attack'): 'defend',    # Hold position, prepare
    ('drill', 'move'): 'defend',      # Stay put, hold ground
    ('drill', 'defend'): 'defend',    # Defend is already similar
    ('attack', 'drill'): 'defend',    # Middle ground

    # Retreat conflicts (when marshal wants to retreat but player doesn't)
    ('retreat', 'defend'): 'defend',  # Hold but don't retreat
    ('retreat', 'attack'): 'defend',  # Middle ground - neither attack nor flee
    ('defend', 'retreat'): 'fortify',  # Dig in — acknowledge fear without retreating
    ('attack', 'retreat'): 'defend',  # If player orders attack, marshal wants retreat - hold

    # ════════════════════════════════════════════════════════════
    # STANCE CHANGE COMPROMISES (Phase 2.7)
    # Keys use consistent naming: 'defensive_stance', 'aggressive_stance', 'neutral_stance'
    # ════════════════════════════════════════════════════════════

    # Aggressive marshal ordered to defensive stance - compromise is neutral
    ('defensive_stance', 'aggressive_stance'): 'neutral_stance',
    ('defensive_stance', 'attack'): 'neutral_stance',  # Player wants defensive, marshal wants attack

    # Cautious marshal ordered to aggressive stance - compromise is neutral
    ('aggressive_stance', 'defensive_stance'): 'neutral_stance',
    ('aggressive_stance', 'defend'): 'neutral_stance',  # Player wants aggressive, marshal wants defend
}


# Objection message templates (Phase 2 mock mode)
OBJECTION_TEMPLATES = {
    'aggressive': {
        'defend': [
            "{name} slams his fist on the table. \"Defend? While the enemy sits idle? Give me the order to attack, Sire!\"",
            "\"{name} looks incredulous. \"You wish me to cower behind walls when glory awaits? I am no garrison commander!\"",
            "\"Defense is for the timid,\" {name} declares. \"Let me show them what French cavalry can do!\"",
        ],
        'wait': [
            "\"Wait?\" {name} paces restlessly. \"The enemy won't wait for us! We must strike while iron is hot!\"",
            "{name} grits his teeth. \"Every hour we wait, they grow stronger. Let me attack now!\"",
        ],
        'retreat': [
            "{name}'s face goes red. \"Retreat? I have never retreated in my life! Give me one more chance!\"",
            "\"The Bravest of the Brave does not retreat,\" {name} says coldly. \"Find another to flee.\"",
        ],
        'fortify': [
            "{name} stares at you in disbelief. \"Dig trenches? You want me to dig trenches like a coward?!\"",
            "\"I did not earn my marshal's baton by cowering behind earthworks,\" {name} says coldly.",
            "\"Fortifications are for those who fear battle,\" {name} declares. \"Let me attack instead!\"",
        ],
        # STANCE TRIGGERS (Phase 2.7)
        'defensive_stance': [
            "{name}'s eyes widen. \"A defensive posture? You want me to adopt the stance of a coward?!\"",
            "\"Sire, a defensive stance is for those who have already lost,\" {name} declares hotly.",
            "{name} grips his sword hilt. \"I am a warrior, not a turtle! Let me fight as one!\"",
        ],
        'neutral_stance_from_aggressive': [
            "{name} frowns. \"Stand down from aggressive posture? But Sire, the enemy is right there!\"",
            "\"You ask me to cool my blood when victory is within grasp?\" {name} protests.",
        ],
    },
    'cautious': {
        'attack_outnumbered': [
            "{name} studies the maps carefully. \"Sire, the enemy outnumbers us significantly. May I suggest we wait for reinforcements?\"",
            "\"The odds are not in our favor,\" {name} reports. \"A direct assault would be costly. Perhaps a flanking maneuver instead?\"",
        ],
        'attack_fortified': [
            "{name} shakes his head. \"Those walls have withstood sieges before. We need artillery support first.\"",
            "\"A frontal assault on fortifications?\" {name} frowns. \"That is not how I win battles, Sire.\"",
        ],
        # STANCE TRIGGERS (Phase 2.7)
        'aggressive_stance': [
            "{name} raises an eyebrow. \"Aggressive posture? That exposes us unnecessarily, Sire.\"",
            "\"A defensive stance would be more prudent,\" {name} suggests. \"We should not invite attack.\"",
        ],
        'aggressive_stance_outnumbered': [
            "{name} looks alarmed. \"Aggressive stance while outnumbered? Sire, that is... unwise.\"",
            "\"We are outnumbered, and you want me to be MORE aggressive?\" {name} asks incredulously.",
            "{name} shakes his head firmly. \"This is reckless. We should fortify, not expose ourselves.\"",
        ],
        # ARTILLERY TRIGGERS (Phase 6.5 — BOMBARDMENT_SPEC.md §7.5)
        'reckless_repositioning': [
            "{name} places a steadying hand on the nearest cannon. \"Sire, we have the range. Their fortifications are cracking. To move now abandons our advantage.\"",
            "{name} shakes his head firmly. \"The walls show fractures from our fire. One -- perhaps two -- more barrages and they will have no cover at all.\"",
        ],
        'ordered_into_melee': [
            "{name} pales visibly. \"Sire... these men serve the guns. In a bayonet fight, we are butchers sent to do a swordsman's work. I beg you, reconsider.\"",
            "{name} looks at his gunners, then back at you. \"If you order it, we go. But know that we lose the guns and the men who know how to fire them.\"",
        ],
        'ordered_to_cease_fire': [
            "{name} grips his telescope tightly. \"Sire, the fortifications crack more with each salvo. Silence my guns now and all that fire was for nothing.\"",
            "{name} gestures to the distant smoke. \"We have their measure, Sire. The walls will not survive another day of this. Why stop when we are so close?\"",
        ],
        'wasted_fire': [
            "{name} lowers his telescope. \"The position is already shattered, Sire. Sending more shells into rubble serves no purpose. Let the infantry advance.\"",
            "{name} gestures toward the distant target. \"Look -- they have no walls left, and barely enough men to hold a picket line. Save my powder for a worthy target.\"",
        ],
        'last_shot_advisory': [
            "{name} calculates carefully. \"One salvo remains today, Sire. Might I suggest the fortified position? My guns will have the greatest effect there.\"",
            "{name} studies the field. \"A single shot left for the day. Let me place it where it counts -- the enemy walls will crack if we strike true.\"",
        ],
    },
    'literal': {
        # TODO Phase 3 (see ROADMAP.md): 'ambiguous' situation detection not yet implemented in personality.py analyze_order_situation().
        # Currently this template is never used. Need LLM to detect unclear commands.
        'ambiguous': [
            "{name} looks confused. \"Sire, which enemy do you mean? There are several possibilities.\"",
            "\"Your orders are... unclear,\" {name} says hesitantly. \"Should I await clarification?\"",
        ],
        # TODO Phase 3 (see ROADMAP.md): 'contradictory' requires order history tracking to detect conflicting orders
        'contradictory': [
            "{name} frowns at the dispatch. \"But Sire, this contradicts what you ordered before...\"",
            "\"I... do not understand,\" {name} says slowly. \"First you said one thing, now another?\"",
        ],
        # TODO Phase 3 (see ROADMAP.md): 'change_of_plans' requires order history to detect frequent changes
        'change_of_plans': [
            "{name} hesitates. \"Another change of orders, Sire? The men grow confused.\"",
            "\"We have already begun the previous maneuver,\" {name} reports. \"Changing now will cause disorder.\"",
        ],
    },
    'balanced': {
        'expose_capital': [
            "{name} points to Paris on the map. \"If I leave, the capital will be undefended. Is that wise?\"",
            "\"Sire, consider: who will defend Paris if I march away?\" {name} asks reasonably.",
        ],
        'suicidal': [
            "{name} meets your eyes. \"I will follow this order if you insist, but you should know - we will not return.\"",
            "\"This order means death for my men,\" {name} says quietly. \"I ask you to reconsider.\"",
        ],
        # TODO Phase 3 (see ROADMAP.md): 'abandon_allies' requires ally tracking system
        'abandon_allies': [
            "{name} looks troubled. \"If we leave now, our allies will be surrounded. Is that your intention?\"",
            "\"Sire, Marshal {ally} depends on our support,\" {name} warns. \"Abandoning them now could be catastrophic.\"",
        ],
    },
    # TODO Phase 3 (see ROADMAP.md): LOYAL personality templates for 'betray_emperor' (political intrigue system)
    'loyal': {
        'betray_emperor': [
            "{name}'s face hardens. \"This order would harm the Emperor's cause. I cannot comply.\"",
            "\"I have sworn my life to Napoleon,\" {name} says firmly. \"What you ask is treason.\"",
        ],
    },
}


class DisobedienceSystem:
    """
    Main system for handling marshal objections.

    Usage:
        system = DisobedienceSystem()
        objection = system.evaluate_order(marshal, order, game_state)
        if objection and objection['type'] == 'major_objection':
            # Present choice to player
            result = system.handle_response(objection, player_choice, game_state)
    """

    def __init__(self):
        """Initialize disobedience system."""
        self.major_objections_this_turn: int = 0

    def reset_turn(self) -> None:
        """Reset turn-based counters."""
        self.major_objections_this_turn = 0

    def evaluate_order(
        self,
        marshal,
        order: Dict,
        game_state
    ) -> Optional[Dict]:
        """
        Evaluate an order for potential objection.

        Args:
            marshal: Marshal receiving the order
            order: Order dict with 'action', 'target', etc.
            game_state: Current game state

        Returns:
            None - No objection, execute normally
            dict with type='mild_objection' - Auto-resolve with message
            dict with type='major_objection' - Awaiting player choice
        """
        # Calculate severity
        severity = calculate_objection_severity(marshal, order, game_state)

        if severity < 0.20:
            # No objection - marshal complies
            return None

        elif severity < 0.50:
            # Mild objection - auto-resolve with grumbling
            return self._create_mild_objection(marshal, order, severity)

        else:
            # Major objection - requires player choice
            # Check if we've hit the cap
            if self.major_objections_this_turn >= MAX_MAJOR_OBJECTIONS_PER_TURN:
                # Downgrade to mild to prevent decision fatigue
                return self._create_mild_objection(marshal, order, severity)

            self.major_objections_this_turn += 1
            return self._create_major_objection(marshal, order, severity, game_state)

    def _create_mild_objection(
        self,
        marshal,
        order: Dict,
        severity: float
    ) -> Dict:
        """
        Create a mild objection (auto-resolves).

        Marshal grumbles but complies.
        """
        message = self._generate_objection_message(marshal, order, is_mild=True)

        return {
            'type': 'mild_objection',
            'marshal': marshal.name,
            'personality': marshal.personality,  # Phase 2.8: Added for UI display
            'severity': severity,
            'order': order,
            'message': message,
            'resolution': 'complies_grudgingly',
        }

    def _create_major_objection(
        self,
        marshal,
        order: Dict,
        severity: float,
        game_state
    ) -> Dict:
        """
        Create a major objection requiring player choice.
        """
        alternative = self._generate_alternative(marshal, order, game_state)
        message = self._generate_objection_message(marshal, order, alternative=alternative)
        compromise = self._find_compromise(marshal, order, alternative, game_state)

        # Calculate trust changes for display
        # Note: Actual changes happen in handle_response(), these are estimates
        trust_value = marshal.trust.value if hasattr(marshal, 'trust') else 70
        trust_gain_trust = 12   # Trust gained when trusting marshal
        trust_loss_insist = -10  # Trust lost when insisting (or -15 if disobeys)
        trust_gain_compromise = 3  # Trust gained for finding middle ground

        # Get marshal's alternative action description
        alt_desc = self._describe_order(alternative) if alternative else "take an alternative approach"
        orig_desc = self._describe_order(order)

        options = [
            {
                'id': 'trust',
                'header': "TRUST MARSHAL'S JUDGMENT",
                'text': f"Accept {marshal.name}'s alternative",
                'description': f"{marshal.name} will {alt_desc} instead",
                'effect': f'Trust +{trust_gain_trust}',
                'trust_change': trust_gain_trust,
                'result': alternative,
            },
            {
                'id': 'insist',
                'header': "INSIST ON ORDER",
                'text': "Force execution of original order",
                'description': f"Command {marshal.name} to {orig_desc} as ordered",
                'effect': f'Trust {trust_loss_insist} (may disobey at low trust)',
                'trust_change': trust_loss_insist,
                'may_disobey': trust_value < 40,  # Marshal may refuse at low trust
                'result': order,
            },
        ]

        # Add compromise option if available
        if compromise:
            comp_desc = self._describe_order(compromise)
            options.append({
                'id': 'compromise',
                'header': "COMPROMISE",
                'text': "Find middle ground",
                'description': f"Meet halfway: {marshal.name} will {comp_desc}",
                'effect': f'Trust +{trust_gain_compromise}',
                'trust_change': trust_gain_compromise,
                'result': compromise,
            })

        return {
            'type': 'major_objection',
            'marshal': marshal.name,
            'personality': marshal.personality,  # Phase 2.8: Added for UI display
            'severity': severity,
            'original_order': order,
            'suggested_alternative': alternative,
            'compromise': compromise,
            'message': message,
            'options': options,
            'awaiting_choice': True,
        }

    def _generate_alternative(self, marshal, order: Dict, game_state) -> Optional[Dict]:
        """
        Generate marshal's suggested alternative based on personality.

        Master Rule #1: Every candidate is validated via _can_execute_suggestion()
        before being returned. Returns None if no valid alternative exists
        (caller must demote to MILD per Master Rule #2).

        # TODO (V2b Session 2): Switch to fog-filtered helpers.
        # Currently uses omniscient get_enemies_in_range/_get_strength_ratio_for_alternative.
        # V2 triggers already use fog-aware helpers — this creates a perception mismatch.
        """
        # ════════════════════════════════════════════════════════════
        # RETREAT STATE: Force RECRUIT as alternative (no nonsense suggestions)
        # Marshals recovering from retreat should focus on rebuilding
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'retreating', False):
            return {
                'action': 'recruit',
                'target': marshal.location,
                'retreat_recovery': True
            }

        action = order.get('action', '').lower()
        personality = get_personality(marshal.personality)

        # Get valid actions for validation
        enemies = get_enemies_in_range(marshal, game_state)
        attack_target = enemies[0].name if enemies else None
        move_target = self._get_move_toward_enemy(marshal, game_state)

        # Helper: build candidate and validate
        def _attack(target):
            return {'action': 'attack', 'target': target}

        def _move(target):
            return {'action': 'move', 'target': target}

        def _defend():
            return {'action': 'defend', 'target': marshal.location}

        def _drill():
            return {'action': 'drill', 'target': marshal.location}

        def _fortify():
            return {'action': 'fortify', 'target': marshal.location}

        def _stance(stance):
            return {'action': 'stance_change', 'target': stance, 'target_stance': stance}

        def _retreat():
            return {'action': 'retreat', 'target': 'toward_paris'}

        def _first_valid(candidates):
            """Master Rule #1: return first executable candidate, or None."""
            for c in candidates:
                if c is not None and _can_execute_suggestion(marshal, c, game_state):
                    return c
            return None

        # ════════════════════════════════════════════════════════════
        # AGGRESSIVE: Wants action - attack if possible, else move toward enemy
        # ════════════════════════════════════════════════════════════
        if personality == Personality.AGGRESSIVE:
            # All defensive/passive actions use the same aggressive fallback chain
            if action in ('defend', 'fortify', 'hold', 'wait', 'form_square', 'drill',
                          'retreat', 'stance_change'):
                candidates = [
                    _attack(attack_target) if attack_target else None,
                    _move(move_target) if move_target else None,
                    _drill() if action != 'drill' else None,  # Don't suggest what was ordered
                    _stance('aggressive'),
                ]
                result = _first_valid(candidates)
                if result:
                    return result
                # Fallback exhausted — return None (caller demotes to MILD)
                return None

        # ════════════════════════════════════════════════════════════
        # CAUTIOUS: Context-aware alternatives based on odds
        # ════════════════════════════════════════════════════════════
        elif personality == Personality.CAUTIOUS:
            if action == 'attack':
                # Check odds to provide context-aware alternative
                strength_ratio = self._get_strength_ratio_for_alternative(marshal, order.get('target'), game_state)

                if strength_ratio is not None:
                    if strength_ratio <= 0.33:  # 3:1+ outnumbered
                        candidates = [_retreat(), _fortify(), _defend()]
                    elif strength_ratio <= 0.5:  # 2:1 outnumbered
                        candidates = [_fortify(), _stance('defensive'), _defend()]
                    else:  # 1.5:1 — mild concern area
                        candidates = [_stance('defensive'), _fortify(), _defend()]
                else:
                    candidates = [_stance('defensive'), _fortify(), _defend()]

                result = _first_valid(candidates)
                if result:
                    return result
                return None

            # Move through enemy territory — cautious wants safety
            if action == 'move':
                candidates = [_fortify(), _stance('defensive'), _defend()]
                result = _first_valid(candidates)
                if result:
                    return result
                return None

            # Defend/fortify with artillery streak — wants to keep bombarding
            if action in ('defend', 'fortify'):
                candidates = [
                    _attack(attack_target) if attack_target else None,
                    _move(move_target) if move_target else None,
                    _stance('defensive'),
                ]
                result = _first_valid(candidates)
                if result:
                    return result
                return None

        # ════════════════════════════════════════════════════════════
        # BALANCED/LITERAL/LOYAL: Context-dependent
        # No V2 evaluator — no current marshals use this personality.
        # Build when balanced/loyal marshals ship (1805 expansion).
        # ════════════════════════════════════════════════════════════
        elif personality in (Personality.BALANCED, Personality.LITERAL, Personality.LOYAL):
            if action == 'attack':
                return _first_valid([_defend()])
            elif action == 'defend':
                return _first_valid([
                    _attack(attack_target) if attack_target else None,
                    _move(move_target) if move_target else None,
                ])

        # ════════════════════════════════════════════════════════════
        # DEFAULT FALLBACK: Opposite action with validation
        # ════════════════════════════════════════════════════════════
        if action == 'attack':
            return _first_valid([_defend()])
        elif action == 'defend':
            return _first_valid([
                _attack(attack_target) if attack_target else None,
                _move(move_target) if move_target else None,
            ])
        elif action == 'move':
            return _first_valid([_fortify(), _defend()])
        else:
            return _first_valid([_defend()])

    def _find_compromise(
        self,
        marshal,
        original: Dict,
        alternative: Optional[Dict],
        game_state
    ) -> Optional[Dict]:
        """
        Find valid compromise between original order and alternative.

        Master Rule #1: All candidates validated via _can_execute_suggestion().
        Returns None if no distinct compromise exists (caller demotes to MILD).

        The compromise must differ from BOTH the original action AND the preferred
        alternative. If it matches either, it's not a real compromise.

        # TODO (V2b Session 2): Switch to fog-filtered helpers.
        # Currently uses omniscient get_enemies_in_range/_get_strength_ratio_for_alternative.
        # V2 triggers already use fog-aware helpers — this creates a perception mismatch.
        """
        orig_action = original.get('action', '').lower()
        alt_action = (alternative.get('action', '') if alternative else '').lower()
        personality = get_personality(marshal.personality)

        # Get context
        move_target = self._get_move_toward_enemy(marshal, game_state)
        enemies_in_range = get_enemies_in_range(marshal, game_state)

        # Helper: candidates that differ from both original and preferred
        def _first_valid_distinct(candidates):
            """Return first executable candidate that differs from original and preferred."""
            for c in candidates:
                if c is None:
                    continue
                if not _can_execute_suggestion(marshal, c, game_state):
                    continue
                c_action = c.get('action', '').lower()
                c_target = (c.get('target_stance') or c.get('target', '')).lower()
                # Must differ from original
                if c_action == orig_action:
                    # Same action type — check if target also matches
                    orig_target = (original.get('target_stance') or original.get('target', '')).lower()
                    if c_target == orig_target:
                        continue
                # Must differ from preferred alternative
                if alternative and c_action == alt_action:
                    alt_target = (alternative.get('target_stance') or alternative.get('target', '')).lower()
                    if c_target == alt_target:
                        continue
                return c
            return None

        # Shorthand builders
        def _defend():
            return {'action': 'defend', 'target': marshal.location}

        def _drill():
            return {'action': 'drill', 'target': marshal.location}

        def _fortify():
            return {'action': 'fortify', 'target': marshal.location}

        def _stance(s):
            return {'action': 'stance_change', 'target': s, 'target_stance': s}

        def _move_enemy():
            return {'action': 'move', 'target': move_target} if move_target else None

        def _attack_nearest():
            return {'action': 'attack', 'target': enemies_in_range[0].name} if enemies_in_range else None

        # ════════════════════════════════════════════════════════════
        # AGGRESSIVE MARSHAL: Compromise leans toward action-readiness
        # ════════════════════════════════════════════════════════════
        if personality == Personality.AGGRESSIVE:
            candidates = [
                _stance('aggressive'),
                _drill() if orig_action != 'drill' else None,
                _move_enemy(),
                _defend(),
            ]
            return _first_valid_distinct(candidates)

        # ════════════════════════════════════════════════════════════
        # CAUTIOUS MARSHAL: Compromise leans toward defensive readiness
        # ════════════════════════════════════════════════════════════
        elif personality == Personality.CAUTIOUS:
            candidates = [
                _stance('defensive'),
                _fortify(),
                _defend(),
            ]
            return _first_valid_distinct(candidates)

        # ════════════════════════════════════════════════════════════
        # OTHER PERSONALITIES / FALLBACK: Use COMPROMISE_RULES table
        # Gaps in table are fine — caught by Master Rule #2 if no valid
        # distinct compromise exists.
        # ════════════════════════════════════════════════════════════
        compromise_action = COMPROMISE_RULES.get((orig_action, alt_action))
        if not compromise_action:
            compromise_action = COMPROMISE_RULES.get((alt_action, orig_action))

        if compromise_action:
            if compromise_action == 'defend':
                c = _defend()
            elif compromise_action == 'move':
                c = _move_enemy()
                if not c:
                    c = _defend()
            elif compromise_action == 'attack':
                c = _attack_nearest()
                if not c:
                    c = _move_enemy()
                if not c:
                    c = _defend()
            elif compromise_action == 'drill':
                c = _drill()
                if not _can_execute_suggestion(marshal, c, game_state):
                    c = _defend()
            elif compromise_action == 'neutral_stance':
                c = _stance('neutral')
                if not _can_execute_suggestion(marshal, c, game_state):
                    c = _defend()
            elif compromise_action == 'fortify':
                c = _fortify()
                if not _can_execute_suggestion(marshal, c, game_state):
                    c = _defend()
            else:
                c = {'action': compromise_action, 'target': marshal.location}

            # Validate the compromise is distinct from both original and preferred
            if c and _can_execute_suggestion(marshal, c, game_state):
                c_action = c.get('action', '').lower()
                c_target = (c.get('target_stance') or c.get('target', '')).lower()
                orig_target = (original.get('target_stance') or original.get('target', '')).lower()
                is_same_as_original = (c_action == orig_action and c_target == orig_target)
                is_same_as_alt = False
                if alternative:
                    alt_target = (alternative.get('target_stance') or alternative.get('target', '')).lower()
                    is_same_as_alt = (c_action == alt_action and c_target == alt_target)
                if not is_same_as_original and not is_same_as_alt:
                    return c

        # No valid distinct compromise found
        return None

    def _get_move_toward_enemy(self, marshal, game_state) -> Optional[str]:
        """
        Find adjacent region that moves toward nearest enemy.

        Validates the move against game rules:
        - Cannot move into enemy-occupied region (must attack)
        - If engaged, can only retreat to friendly territory
        """
        if game_state is None:
            return None

        result = game_state.find_nearest_enemy(marshal.location)
        if not result:
            return None

        enemy, _ = result
        current_region = game_state.regions.get(marshal.location)
        if not current_region:
            return None

        current_dist = game_state.get_distance(marshal.location, enemy.location)

        # Find valid moves that reduce distance to enemy
        best_target = None
        best_distance = current_dist

        for adj_name in current_region.adjacent_regions:
            # Validate this move is legal
            valid, reason = is_valid_move(marshal, adj_name, game_state)
            if not valid:
                continue

            adj_dist = game_state.get_distance(adj_name, enemy.location)
            if adj_dist < best_distance:
                best_target = adj_name
                best_distance = adj_dist

        return best_target

    def _get_strength_ratio_for_alternative(self, marshal, target, game_state) -> Optional[float]:
        """
        Get strength ratio for context-aware alternative generation.

        Returns marshal.strength / enemy.strength
        Returns None if cannot determine.
        """
        if game_state is None or target is None:
            return None

        world = getattr(game_state, 'world', game_state)
        if not hasattr(world, 'marshals'):
            return None

        # Find enemy by name or location
        enemy = None
        for m in world.marshals.values():
            if m.name == target or m.location == target:
                if m.nation != marshal.nation and world.is_at_war(marshal.nation, m.nation):
                    enemy = m
                    break

        if enemy is None or enemy.strength == 0:
            return None

        return marshal.strength / enemy.strength

    def _generate_objection_message(
        self,
        marshal,
        order: Dict,
        alternative: Dict = None,
        is_mild: bool = False
    ) -> str:
        """
        Generate objection message based on personality and situation.

        Phase 2: Uses templates. Phase 3+ will use LLM.
        """
        action = order.get('action', '').lower()
        personality = marshal.personality.lower()

        # Find appropriate template
        templates = OBJECTION_TEMPLATES.get(personality, {})

        # Match action to template category
        template_list = None

        if personality == 'aggressive':
            if action in ('defend', 'hold'):
                template_list = templates.get('defend', [])
            elif action == 'wait':
                template_list = templates.get('wait', [])
            elif action == 'retreat':
                template_list = templates.get('retreat', [])
            elif action == 'fortify':
                template_list = templates.get('fortify', [])
            # STANCE TRIGGERS (Phase 2.7)
            elif action == 'stance_change':
                target_stance = order.get('target_stance', '').lower()
                if target_stance in ('defensive', 'defense'):
                    template_list = templates.get('defensive_stance', [])
                elif target_stance == 'neutral':
                    template_list = templates.get('neutral_stance_from_aggressive', [])

        elif personality == 'cautious':
            if action == 'attack':
                template_list = templates.get('attack_outnumbered', [])
            # STANCE TRIGGERS (Phase 2.7)
            elif action == 'stance_change':
                target_stance = order.get('target_stance', '').lower()
                if target_stance in ('aggressive', 'attack', 'offense'):
                    template_list = templates.get('aggressive_stance', [])
                    # Check if outnumbered for more specific template
                    if template_list and 'outnumbered' in str(order.get('situation', '')):
                        template_list = templates.get('aggressive_stance_outnumbered', []) or template_list

        elif personality == 'literal':
            template_list = templates.get('ambiguous', [])

        elif personality == 'balanced':
            template_list = templates.get('expose_capital', []) or templates.get('suicidal', [])

        elif personality == 'loyal':
            # LOYAL marshals rarely object, but when they do it's for good reason
            template_list = templates.get('betray_emperor', [])

        # Select template
        if template_list:
            template = random.choice(template_list)  # FIX: Removed duplicate import (already at top)
            message = template.format(name=marshal.name)
        else:
            # Generic fallback
            if is_mild:
                message = f"{marshal.name} expresses mild concern but prepares to follow orders."
            else:
                message = f"{marshal.name} objects to this order and suggests an alternative."

        return message

    def _describe_order(self, order: Dict) -> str:
        """Generate human-readable order description."""
        action = order.get('action', 'unknown')
        target = order.get('target', '')

        descriptions = {
            'attack': f"attack {target}",
            'defend': f"defend at {target}",
            'move': f"move to {target}",
            'hold': f"hold position at {target}",
            'wait': "wait for further orders",
            'retreat': "retreat from current position",
            'probe': f"probe enemy at {target}",
            'scout': f"scout toward {target}",
            'patrol': "patrol the area",
            'fortify': "fortify current position",
            'drill': "conduct drill training",
            'unfortify': "abandon fortifications and prepare to move",
            'advance': f"advance toward {target}",
            'clarify': "await clearer orders",
            # STANCE CHANGES (Phase 2.7) - consistent naming
            'stance_change': f"adopt {target.upper()} stance" if target else "change stance",
            'neutral_stance': "return to NEUTRAL stance",
            'defensive_stance': "adopt DEFENSIVE stance",
            'aggressive_stance': "adopt AGGRESSIVE stance",
        }

        return descriptions.get(action, f"{action} {target}")

    def handle_response(
        self,
        objection: Dict,
        choice: str,
        game_state,
        vindication_tracker=None
    ) -> Dict:
        """
        Process player's response to a major objection.

        Args:
            objection: The major objection dict
            choice: 'trust', 'insist', or 'compromise'
            game_state: Current game state
            vindication_tracker: VindicationTracker instance

        Returns:
            Result dict with final order to execute
        """
        marshal_name = objection['marshal']

        # Get marshal
        marshal = None
        if hasattr(game_state, 'world'):
            marshal = game_state.world.get_marshal(marshal_name)
        elif hasattr(game_state, 'get_marshal'):
            marshal = game_state.get_marshal(marshal_name)

        # Get authority tracker
        authority = None
        if hasattr(game_state, 'authority_tracker'):
            authority = game_state.authority_tracker
        elif hasattr(game_state, 'world') and hasattr(game_state.world, 'authority_tracker'):
            authority = game_state.world.authority_tracker

        # Record response in authority tracker (V2b: enriched with current_turn)
        authority_event = None
        if authority:
            current_turn = getattr(game_state, 'current_turn', 0)
            authority_event = authority.record_response(choice, current_turn)

        # Track trust change for redemption check
        trust_change = 0
        disobeyed = False

        # Determine final order based on choice
        if choice == 'trust':
            final_order = objection['suggested_alternative']
            message = f"You defer to {marshal_name}'s judgment."

            # V2 scaled trust gain from objection dict (concern_level × trust_tier)
            if marshal and hasattr(marshal, 'trust'):
                trust_change = objection.get('trust_gain', 3)
                marshal.modify_trust(trust_change)

        elif choice == 'insist':
            # ════════════════════════════════════════════════════════════
            # V2a: Insist always succeeds. Compliance chance is hidden.
            # V2b: Restore defiance roll for STRONG/EXTREME concerns only.
            # See OBJECTION_V2.md §8 (V2b Preview) for defiance mechanic design.
            # calculate_obedience_chance() is preserved for V2b reuse.
            # ════════════════════════════════════════════════════════════
            final_order = objection['original_order']
            message = f"You insist on the original order. {marshal_name} complies reluctantly."

            if marshal and hasattr(marshal, 'trust'):
                # V2 scaled insist penalty from objection dict
                trust_change = objection.get('insist_penalty', -10)
                marshal.modify_trust(trust_change)

            # Record override (whether successful or not)
            if marshal and hasattr(marshal, 'recent_overrides'):
                marshal.recent_overrides.append(True)
                if len(marshal.recent_overrides) > 5:
                    marshal.recent_overrides.pop(0)

        elif choice == 'compromise' and objection.get('compromise'):
            final_order = objection['compromise']
            message = f"You find middle ground with {marshal_name}."

            # V2: Compromise is flat +3 regardless of tier
            if marshal and hasattr(marshal, 'trust'):
                trust_change = objection.get('compromise_gain', 3)
                marshal.modify_trust(trust_change)

        else:
            # Invalid choice, default to insist
            final_order = objection['original_order']
            message = "Order proceeds as given."

        # Record for vindication tracking
        if vindication_tracker:
            vindication_tracker.record_choice(
                marshal_name,
                choice,
                objection['original_order'],
                objection['suggested_alternative']
            )

        # ════════════════════════════════════════════════════════════
        # BUG FIX: Check for redemption event at trust ≤ 20
        # FIX: Only trigger once per marshal (check redemption_pending + cooldown)
        # ════════════════════════════════════════════════════════════
        if marshal and hasattr(marshal, 'trust'):
            print(f"  [TRUST CHECK] {marshal_name} at {marshal.trust.value}, "
                  f"pending={getattr(marshal, 'redemption_pending', False)}")

        world = getattr(game_state, 'world', game_state) if game_state else None
        redemption_event = self.check_redemption_threshold(marshal, world) if marshal else None

        result = {
            'type': 'objection_resolved',
            'marshal': marshal_name,
            'choice': choice,
            'final_order': final_order,
            'message': message,
            'awaiting_choice': False,
            'disobeyed': disobeyed,
            'trust_change': trust_change,
        }

        # Add redemption event if triggered
        if redemption_event:
            result['redemption_event'] = redemption_event
            result['state'] = 'awaiting_redemption_choice'

        # V2b: Pass authority event through to caller
        if authority_event:
            result['authority_event'] = authority_event

        return result

    def _get_available_redemption_options(self, marshal, world) -> List[Dict]:
        """
        Determine which redemption options are available based on game state.

        Rules:
        - Grant Autonomy: Always available
        - Administrative Role: Available if ≥2 field marshals AND no existing admin
        - Dismiss: Available if ≥2 field marshals

        Last Marshal Protection: If only 1 field marshal remains, ONLY show Autonomy.

        Args:
            marshal: The marshal triggering redemption
            world: WorldState for checking marshal counts

        Returns:
            List of available option dicts
        """
        options = []

        # Get counts using world_state helpers
        field_marshals = world.get_field_marshals()
        admin_marshals = world.get_admin_marshals()

        field_count = len(field_marshals)
        admin_count = len(admin_marshals)

        print(f"  [REDEMPTION OPTIONS] Field marshals: {field_count}, Admin marshals: {admin_count}")

        # ════════════════════════════════════════════════════════════
        # GRANT AUTONOMY - Always available
        # ════════════════════════════════════════════════════════════
        options.append({
            'id': 'grant_autonomy',
            'text': f"Grant {marshal.name} Autonomy",
            'description': f"{marshal.name} will act independently for 3 turns. Cannot receive orders during this time. Trust restored based on performance.",
            'effect': 'autonomous_3_turns_trust_based_on_performance',
        })

        # ════════════════════════════════════════════════════════════
        # LAST MARSHAL PROTECTION - If only 1 field marshal, stop here
        # ════════════════════════════════════════════════════════════
        if field_count < 2:
            print("  [REDEMPTION OPTIONS] Last marshal protection: only autonomy available")
            return options

        # ════════════════════════════════════════════════════════════
        # ADMINISTRATIVE ROLE - Available if ≥2 field AND no existing admin
        # ════════════════════════════════════════════════════════════
        if admin_count == 0:
            options.append({
                'id': 'administrative_role',
                'text': f"Transfer {marshal.name} to Staff",
                'description': f"{marshal.name} joins the administrative staff. Troops frozen for future restoration. You gain +1 action per turn.",
                'effect': 'admin_role_plus_one_action',
            })
            print("  [REDEMPTION OPTIONS] Administrative role available (no existing admin)")
        else:
            print("  [REDEMPTION OPTIONS] Administrative role NOT available (already have admin)")

        # ════════════════════════════════════════════════════════════
        # DISMISS - Available if ≥2 field marshals
        # ════════════════════════════════════════════════════════════
        options.append({
            'id': 'dismiss',
            'text': f"Dismiss {marshal.name}",
            'description': f"Relieve {marshal.name} of command permanently. Troops transfer to nearby ally (≤3 regions) or disband. +10 authority.",
            'effect': 'remove_marshal_transfer_troops_authority_bonus',
        })
        print("  [REDEMPTION OPTIONS] Dismiss available (>=2 field marshals)")

        return options

    def _create_redemption_event(self, marshal, world=None) -> Dict:
        """
        Create a redemption event when trust falls to critical levels.

        Player must choose how to handle the broken relationship:
        - Grant Autonomy: Marshal acts independently for 3 turns
        - Administrative Role: Marshal sidelined, +1 action/turn (if available)
        - Dismiss: Remove marshal permanently, +10 authority (if available)

        Args:
            marshal: The marshal whose trust is critical
            world: WorldState for determining available options
        """
        # Get available options based on game state
        if world:
            options = self._get_available_redemption_options(marshal, world)
        else:
            # Fallback if no world provided - only autonomy
            options = [{
                'id': 'grant_autonomy',
                'text': f"Grant {marshal.name} Autonomy",
                'description': f"{marshal.name} will act independently for 3 turns.",
                'effect': 'autonomous_3_turns_trust_based_on_performance',
            }]

        return {
            'type': 'redemption_event',
            'marshal': marshal.name,
            'trust': int(marshal.trust.value),
            'message': f"{marshal.name}'s trust in you has broken completely. The relationship must be addressed.",
            'options': options,
        }

    def check_redemption_threshold(self, marshal, world) -> Optional[Dict]:
        """Check if marshal's trust crossed the redemption threshold (<=20).

        Centralizes the redemption gate used at multiple points in executor.py.
        Returns redemption event dict if threshold crossed, None otherwise.
        """
        if not (marshal and hasattr(marshal, 'trust')):
            return None
        if marshal.trust.value > 20:
            return None
        if getattr(marshal, 'redemption_pending', False):
            return None
        if getattr(marshal, 'autonomous', False):
            return None
        if getattr(marshal, 'administrative', False):
            return None
        if getattr(marshal, 'nation', '') != getattr(world, 'player_nation', 'France'):
            return None
        # Cooldown: skip if recently resolved
        cooldown = getattr(marshal, 'redemption_cooldown_until', 0)
        if getattr(world, 'current_turn', 0) < cooldown:
            return None

        marshal.redemption_pending = True
        return self._create_redemption_event(marshal, world)

    def handle_redemption_response(
        self,
        redemption_event: Dict,
        choice: str,
        game_state
    ) -> Dict:
        """
        Handle player's response to a redemption event.

        Args:
            redemption_event: The redemption event dict
            choice: 'grant_autonomy', 'administrative_role', or 'dismiss'
            game_state: Current game state

        Returns:
            Result dict with outcome
        """
        marshal_name = redemption_event['marshal']

        # Get marshal and world
        # Handle multiple ways game_state can be passed:
        # 1. Dict with 'world' key
        # 2. Object with 'world' attribute
        # 3. WorldState directly
        if isinstance(game_state, dict):
            world = game_state.get('world')
        elif hasattr(game_state, 'world'):
            world = game_state.world
        elif hasattr(game_state, 'marshals'):
            # game_state IS a WorldState
            world = game_state
        else:
            world = None

        if not world:
            return {'success': False, 'message': 'No world state'}

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return {'success': False, 'message': f'Marshal {marshal_name} not found'}

        # FIX: Clear redemption_pending flag now that we're resolving it
        marshal.redemption_pending = False
        # 5-turn cooldown to prevent rapid re-trigger
        marshal.redemption_cooldown_until = getattr(world, 'current_turn', 0) + 5

        # ════════════════════════════════════════════════════════════════════════════
        # GRANT AUTONOMY - Marshal acts independently for 3 turns
        # ════════════════════════════════════════════════════════════════════════════
        if choice == 'grant_autonomy':
            marshal.autonomous = True
            marshal.autonomy_turns = 3
            marshal.autonomy_reason = "redemption"

            # Reset performance tracking
            marshal.autonomous_battles_won = 0
            marshal.autonomous_battles_lost = 0
            marshal.autonomous_regions_captured = 0

            print(f"  [REDEMPTION] {marshal_name} granted autonomy for 3 turns")

            return {
                'success': True,
                'type': 'redemption_resolved',
                'choice': 'grant_autonomy',
                'marshal': marshal_name,
                'message': f"{marshal_name} has been granted autonomy. They will act independently for 3 turns, using their own judgment in battle.",
                'autonomous': True,
                'autonomy_turns': 3,
                'autonomy_reason': 'redemption',
            }

        # ════════════════════════════════════════════════════════════════════════════
        # ADMINISTRATIVE ROLE - Marshal sidelined, troops frozen, +1 action/turn
        # ════════════════════════════════════════════════════════════════════════════
        elif choice == 'administrative_role':
            # Store data for future restoration (Phase 4)
            marshal.administrative = True
            marshal.administrative_strength = marshal.strength
            marshal.administrative_location = marshal.location

            # Clear field presence (troops frozen, not transferred)
            marshal.strength = 0
            marshal.location = None
            marshal.clear_iron_resolve()  # MC-1c: leaving the field

            # Grant bonus action
            world.bonus_actions = getattr(world, 'bonus_actions', 0) + 1
            new_max_actions = world.calculate_max_actions()

            print(f"  [REDEMPTION] {marshal_name} transferred to administrative role")
            print(f"    Troops frozen: {marshal.administrative_strength:,}")
            print(f"    New max actions: {new_max_actions}")

            return {
                'success': True,
                'type': 'redemption_resolved',
                'choice': 'administrative_role',
                'marshal': marshal_name,
                'message': f"{marshal_name} has been transferred to administrative duties. Their {marshal.administrative_strength:,} troops await future assignment. You now have {int(new_max_actions)} actions per turn.",
                'administrative': True,
                'troops_frozen': int(marshal.administrative_strength),
                'new_max_actions': int(new_max_actions),
            }

        # ════════════════════════════════════════════════════════════════════════════
        # DISMISS - Remove marshal permanently, transfer troops if ally nearby, +10 authority
        # ════════════════════════════════════════════════════════════════════════════
        elif choice == 'dismiss':
            troop_count = marshal.strength
            marshal_location = marshal.location

            # Find nearest friendly marshal within 3 regions
            result = world.find_nearest_marshal_within_range(
                from_location=marshal_location,
                nation=marshal.nation,
                max_distance=3,
                exclude_marshal=marshal_name
            )

            if result:
                nearest, distance = result
                nearest.add_troops(troop_count)
                transfer_message = f"{troop_count:,} troops transferred to {nearest.name} ({distance} region{'s' if distance != 1 else ''} away)."
                print(f"  [REDEMPTION] Troops transferred to {nearest.name}")
            else:
                transfer_message = f"{troop_count:,} troops dispersed - no nearby commanders within 3 regions."
                print("  [REDEMPTION] Troops dispersed (no ally within 3 regions)")

            # Remove marshal from world
            if marshal_name in world.marshals:
                del world.marshals[marshal_name]

            # Grant authority bonus for difficult command decision
            authority_bonus = 10
            if hasattr(world, 'authority_tracker'):
                world.authority_tracker.authority = min(100, world.authority_tracker.authority + authority_bonus)
                print(f"  [REDEMPTION] Authority +{authority_bonus} (now {world.authority_tracker.authority})")

            return {
                'success': True,
                'type': 'redemption_resolved',
                'choice': 'dismiss',
                'marshal': marshal_name,
                'message': f"{marshal_name} has been relieved of command. {transfer_message} Your decisive action inspires confidence. (+{authority_bonus} Authority)",
                'dismissed': True,
                'authority_bonus': int(authority_bonus),
            }

        # ════════════════════════════════════════════════════════════════════════════
        # INVALID CHOICE
        # ════════════════════════════════════════════════════════════════════════════
        return {
            'success': False,
            'message': f'Invalid choice: {choice}. Valid options: grant_autonomy, administrative_role, dismiss',
        }

    def get_major_objections_remaining(self) -> int:
        """Get number of major objections remaining this turn."""
        return max(0, MAX_MAJOR_OBJECTIONS_PER_TURN - self.major_objections_this_turn)


# ════════════════════════════════════════════════════════════════════════════
# STRATEGIC OBJECTION SYSTEM (Phase M)
# ════════════════════════════════════════════════════════════════════════════
# Marshals can object to strategic commands at issuance based on personality.
# This is separate from tactical objection - strategic objections fire BEFORE
# the order is created, while tactical objections fire during execution.
# ════════════════════════════════════════════════════════════════════════════


def check_strategic_objection(
    marshal,
    strategic_type: str,
    target: str,
    path: List[str],
    world,
    game_state=None,
    include_variance: bool = True
) -> Optional[Dict]:
    """
    Check if a marshal objects to a strategic command at issuance.

    Uses probability system (same as tactical objections):
    1. Check if conditions are met for potential objection
    2. Calculate severity using trust, authority, vindication modifiers
    3. Roll against severity - only object if roll >= 0.50 threshold

    Trigger conditions:
    - Ney (aggressive): HOLD with no enemies adjacent to target region
    - Davout (cautious): PURSUE with target strength >= 1.2x marshal strength
    - Davout (cautious): MOVE_TO with path crossing enemy-occupied region
    - Grouchy (literal): NEVER objects (uses clarification popup instead)

    Bypass conditions:
    - Marshal is in retreat_recovery (compliant)
    - Order already has objection_resolved=True

    Args:
        marshal: Marshal receiving the order
        strategic_type: "HOLD", "PURSUE", "MOVE_TO", "SUPPORT"
        target: Target region or marshal name
        path: Calculated path for movement orders
        world: WorldState for context
        game_state: Game state for authority modifier (optional)
        include_variance: Whether to add random variance (for testing)

    Returns:
        None if no objection, or dict with:
        - should_object: True
        - reason: Human-readable explanation
        - message: Dramatic objection message
        - preferred_action: Dict with marshal's preferred alternative
        - compromise_action: Dict with middle-ground option (or None)
        - options: List of choice options for UI
        - severity: Calculated severity value
    """
    from backend.commands.severity import calculate_strategic_severity

    if not marshal or not world:
        return None

    personality = getattr(marshal, 'personality', 'balanced').lower()

    # Debug trace removed for production (was: strategic objection check)

    # ═══════════════════════════════════════════════════════════
    # BYPASS: Grouchy (literal) never objects to strategic commands
    # ═══════════════════════════════════════════════════════════
    if personality == 'literal':
        return None

    # ═══════════════════════════════════════════════════════════
    # BYPASS: Marshal in retreat recovery is compliant
    # ═══════════════════════════════════════════════════════════
    if getattr(marshal, 'retreat_recovery', 0) > 0:
        return None

    # Get game_state for severity calculation
    if game_state is None:
        game_state = {"world": world}

    # ═══════════════════════════════════════════════════════════
    # NEY (AGGRESSIVE) - Objects to HOLD with no enemies adjacent
    # Base severity: 0.72 (strong objection - aggressive hates passive orders)
    # At trust 70: 0.72 × 1.0 = 0.72 → ~80% objection chance
    # At trust 85: 0.72 × 0.7 = 0.50 → ~50% objection chance
    # At trust 15: 0.72 × 1.6 = 1.15 → capped at 0.95 → guaranteed
    # ═══════════════════════════════════════════════════════════
    if personality == 'aggressive' and strategic_type == "HOLD":
        # Check for enemies adjacent to target (or current location if no target)
        hold_region = target or marshal.location
        region = world.get_region(hold_region)

        enemies_adjacent = False
        if region:
            for adj_name in region.adjacent_regions:
                enemies = world.get_enemies_in_region(adj_name, marshal.nation)
                if enemies:
                    enemies_adjacent = True
                    break

        if enemies_adjacent:
            # Enemies adjacent — aggressive wants to attack, not hold
            severity = calculate_strategic_severity(
                marshal, strategic_type, 0.82, game_state, include_variance
            )
            if severity < 0.50:
                return None

            preferred = _get_aggressive_preferred(marshal, world)
            compromise = {"action": "hold", "max_turns": 3}  # Timed HOLD

            return {
                "should_object": True,
                "type": "strategic",
                "reason": "ney_hold_enemies_adjacent",
                "message": f'"{marshal.name} slams his fist on the map. "Hold? The enemy is RIGHT THERE! Let me attack, Sire!""',
                "marshal": marshal.name,
                "personality": personality,
                "severity": severity,
                "options": _build_strategic_options(
                    marshal,
                    preferred,
                    compromise,
                    "Proceed with Hold",
                    "Accept: Timed Hold (3 turns)",
                    strategic_type
                )
            }
        else:
            # No enemies adjacent — bored with nothing to do
            severity = calculate_strategic_severity(
                marshal, strategic_type, 0.72, game_state, include_variance
            )

            if severity < 0.50:
                return None

            preferred = _get_aggressive_preferred(marshal, world)
            compromise = {"action": "hold", "max_turns": 3}  # Timed HOLD

            return {
                "should_object": True,
                "type": "strategic",
                "reason": "ney_hold_no_enemies",
                "message": f'"{marshal.name} scoffs. "Hold position? While there\'s glory to be won? You want me to guard nothing, Sire?""',
                "marshal": marshal.name,
                "personality": personality,
                "severity": severity,
                "options": _build_strategic_options(
                    marshal,
                    preferred,
                    compromise,
                    "Proceed with Hold",
                    "Accept: Timed Hold (3 turns)",
                    strategic_type
                )
            }

    # ═══════════════════════════════════════════════════════════
    # DAVOUT (CAUTIOUS) - Objects to PURSUE with bad odds
    # Base severity: 0.68 (cautious hates risky chases)
    # At trust 70: 0.68 × 1.0 = 0.68 → ~75% objection chance
    # At trust 85: 0.68 × 0.7 = 0.48 → ~45% objection chance
    #
    # FOG OF WAR (Session 36): Respects visibility levels:
    # - FULL: Object on exact odds (ratio >= 1.2)
    # - PARTIAL: Object on strength band comparison (band-level only)
    # - STALE/LAST_KNOWN/UNKNOWN: Cannot object on odds. May object
    #   on staleness instead ("Three-day-old intelligence, Sire.")
    # ═══════════════════════════════════════════════════════════
    if personality == 'cautious' and strategic_type == "PURSUE":
        from backend.models.intel import FULL as FULL_VIS, PARTIAL as PARTIAL_VIS, STALE as STALE_VIS
        from backend.models.intel import get_strength_band

        target_marshal = world.get_marshal(target) if target else None

        # Determine target visibility from intel store
        target_visibility = None
        target_intel_age = 0
        if hasattr(world, 'get_last_known_location') and target:
            last_known = world.get_last_known_location(target)
            if last_known:
                _region, last_turn, vis = last_known
                target_visibility = vis
                target_intel_age = world.current_turn - last_turn

        if target_marshal and target_marshal.strength > 0:
            if target_visibility == FULL_VIS:
                # FULL visibility: object on exact odds as before
                ratio = target_marshal.strength / max(marshal.strength, 1)

                if ratio >= 1.2:
                    severity = calculate_strategic_severity(
                        marshal, strategic_type, 0.68, game_state, include_variance
                    )
                    if severity < 0.50:
                        return None

                    preferred = {"action": "fortify", "target": marshal.location}
                    compromise = {"action": "pursue", "auto_cancel_below_ratio": 0.8}

                    return {
                        "should_object": True,
                        "type": "strategic",
                        "reason": "davout_pursue_bad_odds",
                        "message": f'"{marshal.name} studies the reports. "Pursue {target}? Their forces outnumber us. This is reckless, Sire.""',
                        "marshal": marshal.name,
                        "personality": personality,
                        "severity": severity,
                        "options": _build_strategic_options(
                            marshal,
                            preferred,
                            compromise,
                            "Proceed with Pursue",
                            "Accept: Cautious PURSUE (auto-cancel if odds drop)",
                            strategic_type
                        )
                    }

            elif target_visibility == PARTIAL_VIS:
                # PARTIAL visibility: compare strength bands only
                target_band = get_strength_band(target_marshal.strength)
                our_band = get_strength_band(marshal.strength)
                # Object if target band suggests they're stronger
                # Band ordering: no forces < screening < small < substantial < large < massive
                band_order = ["no forces", "screening force", "small force",
                              "substantial force", "large force", "massive force"]
                target_idx = band_order.index(target_band) if target_band in band_order else 0
                our_idx = band_order.index(our_band) if our_band in band_order else 0

                if target_idx > our_idx:
                    severity = calculate_strategic_severity(
                        marshal, strategic_type, 0.60, game_state, include_variance
                    )
                    if severity < 0.50:
                        return None

                    preferred = {"action": "fortify", "target": marshal.location}
                    compromise = {"action": "pursue", "auto_cancel_below_ratio": 0.8}

                    return {
                        "should_object": True,
                        "type": "strategic",
                        "reason": "davout_pursue_bad_odds",
                        "message": f'"{marshal.name} studies the reports. "Reports suggest {target} commands a {target_band}. We are a {our_band}. This pursuit is unwise, Sire.""',
                        "marshal": marshal.name,
                        "personality": personality,
                        "severity": severity,
                        "options": _build_strategic_options(
                            marshal,
                            preferred,
                            compromise,
                            "Proceed with Pursue",
                            "Accept: Cautious PURSUE (auto-cancel if odds drop)",
                            strategic_type
                        )
                    }

            elif target_visibility in (STALE_VIS, "last_known", "unknown") or target_visibility is None:
                # STALE/LAST_KNOWN/UNKNOWN: Cannot object on odds.
                # May object on staleness if intel is old (3+ turns)
                if target_intel_age >= 3:
                    severity = calculate_strategic_severity(
                        marshal, strategic_type, 0.55, game_state, include_variance
                    )
                    if severity < 0.50:
                        return None

                    # Resolve marshal name to their last known location for scouting
                    scout_region = None
                    if target:
                        target_marshal_obj = world.get_marshal(target) if world else None
                        if target_marshal_obj:
                            scout_region = target_marshal_obj.location
                    preferred = {"action": "scout", "target": scout_region or marshal.location}
                    compromise = {"action": "pursue", "auto_cancel_below_ratio": 0.8}

                    return {
                        "should_object": True,
                        "type": "strategic",
                        "reason": "davout_pursue_stale_intel",
                        "message": f'"{marshal.name} frowns at the dispatch. "{target_intel_age}-day-old intelligence, Sire. We know nothing of {target}\'s current strength or position.""',
                        "marshal": marshal.name,
                        "personality": personality,
                        "severity": severity,
                        "options": _build_strategic_options(
                            marshal,
                            preferred,
                            compromise,
                            "Proceed with Pursue",
                            "Accept: Cautious PURSUE (scout first if possible)",
                            strategic_type
                        )
                    }

    # ═══════════════════════════════════════════════════════════
    # DAVOUT (CAUTIOUS) - Objects to MOVE_TO through danger
    # Base severity: 0.65 (cautious dislikes marching into danger)
    # At trust 70: 0.65 × 1.0 = 0.65 → ~70% objection chance
    # At trust 85: 0.65 × 0.7 = 0.46 → ~40% objection chance
    # ═══════════════════════════════════════════════════════════
    if personality == 'cautious' and strategic_type == "MOVE_TO":
        # Check if path crosses any enemy-occupied region
        enemy_regions = []
        for region_name in path:
            enemies = world.get_enemies_in_region(region_name, marshal.nation)
            if enemies:
                enemy_regions.append(region_name)

        if enemy_regions:
            # Calculate severity with probability modifiers
            severity = calculate_strategic_severity(
                marshal, strategic_type, 0.65, game_state, include_variance
            )

            # Only object if severity >= 0.50
            if severity < 0.50:
                return None

            preferred = {"action": "fortify", "target": marshal.location}

            # Check if safe path exists
            enemy_occupied = set()
            for rn in world.regions:
                if world.get_enemies_in_region(rn, marshal.nation):
                    enemy_occupied.add(rn)

            dest = path[-1] if path else target
            safe_path = world.find_path(marshal.location, dest, avoid_regions=enemy_occupied)

            compromise = None
            if safe_path and len(safe_path) <= len(path) * 2:
                compromise = {"action": "move_to", "safe_path": True}

            return {
                "should_object": True,
                "type": "strategic",
                "reason": "davout_move_dangerous_path",
                "message": f'"{marshal.name} traces the route. "That path passes through {enemy_regions[0]}. We would be walking into danger, Sire.""',
                "marshal": marshal.name,
                "personality": personality,
                "severity": severity,
                "options": _build_strategic_options(
                    marshal,
                    preferred,
                    compromise,
                    "Proceed through danger",
                    "Accept: Safe route" if compromise else None,
                    strategic_type
                )
            }

    # ═══════════════════════════════════════════════════════════
    # DAVOUT (CAUTIOUS) - Objects to distant HOLD through danger
    # Same logic as MOVE_TO: cautious marshals dislike marching into danger
    # Only triggers if marshal must travel to reach HOLD position
    # Base severity: 0.65 (same as MOVE_TO dangerous path)
    # ═══════════════════════════════════════════════════════════
    if personality == 'cautious' and strategic_type == "HOLD":
        # Only check if marshal isn't already at the target
        # (If already there, no dangerous path to traverse)
        if target and marshal.location != target and path:
            # Check if path crosses any enemy-occupied region
            enemy_regions = []
            for region_name in path:
                enemies = world.get_enemies_in_region(region_name, marshal.nation)
                if enemies:
                    enemy_regions.append(region_name)

            if enemy_regions:
                # Calculate severity with probability modifiers
                severity = calculate_strategic_severity(
                    marshal, strategic_type, 0.65, game_state, include_variance
                )

                # Only object if severity >= 0.50
                if severity < 0.50:
                    return None

                preferred = {"action": "fortify", "target": marshal.location}

                # Check if safe path exists
                enemy_occupied = set()
                for rn in world.regions:
                    if world.get_enemies_in_region(rn, marshal.nation):
                        enemy_occupied.add(rn)

                dest = path[-1] if path else target
                safe_path = world.find_path(marshal.location, dest, avoid_regions=enemy_occupied)

                compromise = None
                if safe_path and len(safe_path) <= len(path) * 2:
                    compromise = {"action": "hold", "safe_path": True}

                return {
                    "should_object": True,
                    "type": "strategic",
                    "reason": "davout_hold_dangerous_path",
                    "message": f'"{marshal.name} studies the map. "To hold {target}, we must march through {enemy_regions[0]}. A dangerous gambit, Sire.""',
                    "marshal": marshal.name,
                    "personality": personality,
                    "severity": severity,
                    "options": _build_strategic_options(
                        marshal,
                        preferred,
                        compromise,
                        "Proceed through danger",
                        "Accept: Safe route to position" if compromise else None,
                        strategic_type
                    )
                }

    # ═══════════════════════════════════════════════════════════
    # DAVOUT (CAUTIOUS) - Objects to SUPPORT through danger
    # Same logic as MOVE_TO/HOLD: cautious marshals dislike marching into danger
    # Base severity: 0.65 (same as other dangerous path objections)
    # ═══════════════════════════════════════════════════════════
    if personality == 'cautious' and strategic_type == "SUPPORT":
        # Only check if path exists (marshal isn't already with the ally)
        if path:
            # Check if path crosses any enemy-occupied region
            enemy_regions = []
            for region_name in path:
                enemies = world.get_enemies_in_region(region_name, marshal.nation)
                if enemies:
                    enemy_regions.append(region_name)

            if enemy_regions:
                # Calculate severity with probability modifiers
                severity = calculate_strategic_severity(
                    marshal, strategic_type, 0.65, game_state, include_variance
                )

                # Only object if severity >= 0.50
                if severity < 0.50:
                    return None

                preferred = {"action": "fortify", "target": marshal.location}

                # Check if safe path exists
                enemy_occupied = set()
                for rn in world.regions:
                    if world.get_enemies_in_region(rn, marshal.nation):
                        enemy_occupied.add(rn)

                dest = path[-1] if path else target
                safe_path = world.find_path(marshal.location, dest, avoid_regions=enemy_occupied)

                compromise = None
                if safe_path and len(safe_path) <= len(path) * 2:
                    compromise = {"action": "support", "safe_path": True}

                return {
                    "should_object": True,
                    "type": "strategic",
                    "reason": "davout_support_dangerous_path",
                    "message": f'"{marshal.name} examines the route. "To reach {target}, we must pass through {enemy_regions[0]}. That path invites disaster, Sire.""',
                    "marshal": marshal.name,
                    "personality": personality,
                    "severity": severity,
                    "options": _build_strategic_options(
                        marshal,
                        preferred,
                        compromise,
                        "Proceed through danger",
                        "Accept: Safe route to ally" if compromise else None,
                        strategic_type
                    )
                }

    return None


def _get_aggressive_preferred(marshal, world) -> Optional[Dict]:
    """
    Find preferred aggressive action for Ney-type marshals.

    Fallback chain:
    1. Attack adjacent enemy (if one exists)
    2. PURSUE nearest enemy (if within 3 regions)
    3. Aggressive stance (if not already aggressive)
    4. Drill (if not already drilling/has shock bonus)
    5. None (chain exhausted)
    """
    from backend.models.marshal import Stance

    # 1. Attack adjacent enemy
    region = world.get_region(marshal.location)
    if region:
        for adj_name in region.adjacent_regions:
            enemies = world.get_enemies_in_region(adj_name, marshal.nation)
            if enemies:
                return {"action": "attack", "target": enemies[0].name}

    # 2. PURSUE nearest enemy within 3 regions
    nearest_enemy = None
    nearest_dist = float('inf')
    for m in world.marshals.values():
        if m.nation != marshal.nation and m.strength > 0 and world.is_at_war(marshal.nation, m.nation):
            dist = world.get_distance(marshal.location, m.location)
            if dist <= 3 and dist < nearest_dist:
                nearest_enemy = m
                nearest_dist = dist

    if nearest_enemy:
        return {"action": "pursue", "target": nearest_enemy.name, "strategic_type": "PURSUE"}

    # 3. Aggressive stance
    current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
    if current_stance != Stance.AGGRESSIVE:
        return {"action": "stance_change", "target": "aggressive", "target_stance": "aggressive"}

    # 4. Drill
    is_drilling = getattr(marshal, 'drilling', False)
    has_shock = getattr(marshal, 'shock_bonus', 0) > 0
    if not is_drilling and not has_shock:
        return {"action": "drill", "target": marshal.location}

    # Chain exhausted
    return None


def _build_strategic_options(
    marshal,
    preferred: Optional[Dict],
    compromise: Optional[Dict],
    proceed_text: str,
    compromise_text: Optional[str],
    strategic_type: str,
    concern=None,
) -> List[Dict]:
    """Build options list for strategic objection popup.

    ══════════════════════════════════════════════════════════════════
    PT-C2 — the buttons quote what the engine will do.

    These three numbers used to be authored constants (-10 / +12 / +3)
    while the response handler applied the TIER-SCALED values off the
    same objection dict (`strategic_executor.py:2106-2108` reads
    `insist_penalty` and `trust_gain`; the options were never consulted).
    For a WARY marshal at STRONG concern the button read "Proceed -10"
    and charged -12, and read "Trust +12" and paid +6. -10 is correct
    only at TRUSTING; +12 only at HOSTILE+EXTREME.

    They are now derived from the marshal through `objection_v2`'s own
    functions — the same ones the handler resolves against — so the
    surface calls the executor's predicate instead of keeping a second
    opinion. `concern` is optional because the eight V1 call sites do
    not carry one; MODERATE is the floor at which a strategic objection
    can be raised at all, so it is the honest default rather than a
    guess.
    ══════════════════════════════════════════════════════════════════
    """
    from backend.commands.objection_v2 import (
        COMPROMISE_TRUST_GAIN,
        ConcernLevel,
        calculate_trust_gain,
        get_insist_penalty,
        get_trust_tier,
    )

    trust_tier = get_trust_tier(marshal.trust.value)
    insist_penalty = get_insist_penalty(trust_tier)
    trust_gain = calculate_trust_gain(concern or ConcernLevel.MODERATE,
                                      trust_tier)
    # `strategic_executor.py:1424` — a literal marshal's strategic order is
    # priced at 1, and the button said 2 for everyone.
    proceed_ap = 1 if getattr(marshal, "personality", "") == "literal" else 2

    options = []

    # Proceed option (always available)
    options.append({
        "type": "proceed",
        "text": proceed_text,
        "description": f"Override {marshal.name}'s objection and execute the order.",
        "trust_change": insist_penalty,
        "ap_cost": proceed_ap,
    })

    # Preferred option (if available)
    if preferred:
        action = preferred.get("action", "")
        target = preferred.get("target", "")

        if action == "attack":
            desc = f"{marshal.name} attacks {target}"
        elif action == "pursue":
            desc = f"{marshal.name} pursues {target}"
        elif action == "stance_change":
            desc = f"{marshal.name} adopts {target} stance"
        elif action == "drill":
            desc = f"{marshal.name} drills troops"
        elif action == "fortify":
            desc = f"{marshal.name} fortifies position"
        else:
            desc = f"{marshal.name} takes alternative action"

        options.append({
            "type": "preferred",
            "text": f"Trust: {desc}",
            "description": f"Accept {marshal.name}'s judgment.",
            "trust_change": trust_gain,
            "ap_cost": 1,
            "action": preferred.get("action"),
            "target": preferred.get("target"),
            "strategic_type": preferred.get("strategic_type"),
        })

    # Compromise option (if available)
    if compromise and compromise_text:
        options.append({
            "type": "compromise",
            "text": compromise_text,
            "description": f"Find middle ground with {marshal.name}.",
            # The one number that was already honest — it is flat.
            "trust_change": COMPROMISE_TRUST_GAIN,
            "ap_cost": 2,
            "compromise": compromise,
        })

    return options


# Test code
if __name__ == "__main__":
    from backend.models.marshal import create_starting_marshals
    from backend.models.trust import Trust
    from backend.models.authority import AuthorityTracker

    print("=" * 60)
    print("DISOBEDIENCE SYSTEM TEST")
    print("=" * 60)

    # Create mock game state
    class MockWorld:
        def __init__(self):
            self.marshals = create_starting_marshals()
            self.regions = {}
            self.authority_tracker = AuthorityTracker()

            # Add trust to marshals
            for m in self.marshals.values():
                m.trust = Trust(70)
                m.vindication_score = 0
                m.recent_battles = []
                m.recent_overrides = []

        def get_marshal(self, name):
            return self.marshals.get(name)

    class MockGameState:
        def __init__(self):
            self.world = MockWorld()
            self.authority_tracker = self.world.authority_tracker

    game_state = MockGameState()
    system = DisobedienceSystem()

    ney = game_state.world.get_marshal('Ney')
    davout = game_state.world.get_marshal('Davout')

    # Test 1: Ney with defend order (should object)
    print("\n" + "-" * 40)
    print("TEST 1: Ney receives defend order")
    defend_order = {'action': 'defend', 'target': 'Belgium'}
    objection = system.evaluate_order(ney, defend_order, game_state)

    if objection:
        print(f"Objection type: {objection['type']}")
        print(f"Severity: {objection['severity']:.2f}")
        print(f"Message: {objection['message']}")

        if objection['type'] == 'major_objection':
            print("Options:")
            for opt in objection['options']:
                print(f"  - {opt['id']}: {opt['text']}")

            # Player chooses to trust
            result = system.handle_response(objection, 'trust', game_state)
            print(f"\nResult: {result['message']}")
            print(f"Final order: {result['final_order']}")
    else:
        print("No objection")

    # Test 2: Ney with attack order (should not object)
    print("\n" + "-" * 40)
    print("TEST 2: Ney receives attack order")
    attack_order = {'action': 'attack', 'target': 'Wellington'}
    objection = system.evaluate_order(ney, attack_order, game_state)

    if objection:
        print(f"Objection type: {objection['type']}")
    else:
        print("No objection - Ney is happy to attack!")

    # Test 3: Davout with attack order (may object if outnumbered)
    print("\n" + "-" * 40)
    print("TEST 3: Davout receives attack order")
    attack_order = {'action': 'attack', 'target': 'Wellington'}
    objection = system.evaluate_order(davout, attack_order, game_state)

    if objection:
        print(f"Objection type: {objection['type']}")
        print(f"Severity: {objection['severity']:.2f}")
    else:
        print("No objection")

    # Test 4: Multiple objections (cap test)
    print("\n" + "-" * 40)
    print("TEST 4: Multiple major objections")
    system.reset_turn()

    for i in range(5):
        objection = system.evaluate_order(ney, defend_order, game_state)
        print(f"Order {i+1}: {objection['type'] if objection else 'no objection'}")
        print(f"  Major objections remaining: {system.get_major_objections_remaining()}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
